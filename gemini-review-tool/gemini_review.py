#!/usr/bin/env python3
"""
Gemini Code Review Automation Tool

This tool automates the process of:
1. Using repomix to package your codebase
2. Sending it to Gemini AI for analysis
3. Returning the critique and guidance

Version: 1.0.0
"""

import os
import sys
import subprocess
import argparse
import json
import time
import getpass
import keyring
import re
import functools
import random
import logging
import concurrent.futures
import multiprocessing
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from collections import deque
from threading import Lock
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Try to import config module
try:
    from gemini_review_config import ReviewConfig, find_config_file, create_default_config
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Config module not available: {e}")
    CONFIG_AVAILABLE = False

# Try to import cache module
try:
    from gemini_review_cache import ReviewCache
    CACHE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Cache module not available: {e}")
    CACHE_AVAILABLE = False

# Load environment variables
load_dotenv()

# Custom Exception Classes
class ReviewError(Exception):
    """Base exception for review tool errors."""
    pass

class ConfigurationError(ReviewError):
    """Configuration-related errors."""
    pass

class APIError(ReviewError):
    """API-related errors."""
    pass

class FileSystemError(ReviewError):
    """File system operation errors."""
    pass

class ValidationError(ReviewError):
    """Input validation errors."""
    pass

# Rate Limiter Class
class RateLimiter:
    """Advanced rate limiter with dynamic adjustment and comprehensive monitoring."""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60, 
                 burst_allowance: int = 10, adaptive: bool = True):
        self.max_calls = max_calls
        self.time_window = time_window
        self.burst_allowance = burst_allowance
        self.adaptive = adaptive
        self.calls = deque()
        self.burst_calls = deque()
        self.lock = Lock()
        self.error_count = 0
        self.last_api_error = None
        self.dynamic_multiplier = 1.0
        self.logger = logging.getLogger("gemini_review.rate_limiter")
        
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded, with dynamic adjustment."""
        with self.lock:
            now = time.time()
            
            # Clean old calls
            self._clean_old_calls(now)
            
            # Apply dynamic adjustment if adaptive
            effective_max_calls = self.max_calls
            if self.adaptive:
                effective_max_calls = int(self.max_calls * self.dynamic_multiplier)
            
            # Check for burst allowance first (separate from main rate limit)
            if len(self.burst_calls) < self.burst_allowance:
                self.burst_calls.append(now)
                return
            
            # Check if we need to wait based on main rate limit
            if len(self.calls) >= effective_max_calls:
                sleep_time = self._calculate_wait_time(now)
                if sleep_time > 0:
                    self.logger.info(f"Rate limit reached, waiting {sleep_time:.1f} seconds")
                    print(f"⏳ Rate limit reached, waiting {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    # Re-check after waiting
                    self.wait_if_needed()
                    return
            
            # Record this call
            self.calls.append(now)
    
    def _clean_old_calls(self, now: float):
        """Remove calls outside the time window."""
        # Clean regular calls
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()
        
        # Clean burst calls (shorter window)
        burst_window = min(60, self.time_window // 4)
        while self.burst_calls and self.burst_calls[0] < now - burst_window:
            self.burst_calls.popleft()
    
    def _calculate_wait_time(self, now: float) -> float:
        """Calculate optimal wait time with jitter."""
        if not self.calls:
            return 0
        
        base_wait = self.time_window - (now - self.calls[0])
        
        # Add exponential backoff for repeated waits
        backoff_factor = min(2.0 ** (len(self.calls) // 10), 8.0)
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.8, 1.2)
        
        return max(0, base_wait * backoff_factor * jitter)
    
    def handle_api_error(self, error: Exception):
        """Adjust rate limiting based on API errors."""
        self.error_count += 1
        self.last_api_error = error
        error_str = str(error).lower()
        
        if self.adaptive:
            # Rate limit errors
            if any(phrase in error_str for phrase in ['rate limit', 'quota', 'too many requests']):
                self.dynamic_multiplier = max(0.1, self.dynamic_multiplier * 0.5)
                self.logger.warning(f"Rate limit error detected, reducing rate to {self.dynamic_multiplier:.2f}")
            
            # Server errors - be more conservative
            elif any(phrase in error_str for phrase in ['500', 'internal error', 'server error']):
                self.dynamic_multiplier = max(0.3, self.dynamic_multiplier * 0.7)
                self.logger.warning(f"Server error detected, reducing rate to {self.dynamic_multiplier:.2f}")
    
    def handle_api_success(self):
        """Gradually restore rate limiting on success."""
        if self.adaptive and self.dynamic_multiplier < 1.0:
            self.dynamic_multiplier = min(1.0, self.dynamic_multiplier * 1.05)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive rate limiting statistics."""
        now = time.time()
        self._clean_old_calls(now)
        
        return {
            'current_calls_in_window': len(self.calls),
            'max_calls': self.max_calls,
            'effective_max_calls': int(self.max_calls * self.dynamic_multiplier),
            'time_window': self.time_window,
            'dynamic_multiplier': self.dynamic_multiplier,
            'error_count': self.error_count,
            'burst_calls_remaining': max(0, self.burst_allowance - len(self.burst_calls)),
            'last_api_error': str(self.last_api_error) if self.last_api_error else None
        }

# Parallel Processing Class
class ParallelProcessor:
    """Handle parallel processing of review operations."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (multiprocessing.cpu_count() or 1) + 4)
        self.logger = logging.getLogger("gemini_review")
    
    def process_files_parallel(self, file_paths: List[Path], 
                              processor_func: Callable, 
                              batch_size: int = 10) -> Dict[str, Any]:
        """Process multiple files in parallel batches."""
        results = {}
        
        # Split into batches to avoid overwhelming the system
        batches = [file_paths[i:i + batch_size] for i in range(0, len(file_paths), batch_size)]
        
        for batch_idx, batch in enumerate(batches):
            self.logger.info(f"Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} files)")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit tasks for this batch
                future_to_file = {
                    executor.submit(processor_func, file_path): file_path 
                    for file_path in batch
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_file, timeout=300):
                    file_path = future_to_file[future]
                    try:
                        result = future.result(timeout=30)
                        results[str(file_path)] = result
                        self.logger.debug(f"Processed: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to process {file_path}: {e}")
                        results[str(file_path)] = {"error": str(e), "status": "failed"}
            
            # Rate limiting between batches
            if batch_idx < len(batches) - 1:
                time.sleep(1.0)
        
        return results

# Input Validation Functions
def validate_project_path(path_str: str) -> Path:
    """Validate and sanitize project path against comprehensive security threats."""
    if not path_str or not path_str.strip():
        raise ValidationError("Project path cannot be empty")
    
    # Remove potentially dangerous Unicode characters
    import unicodedata
    normalized_path = unicodedata.normalize('NFKC', path_str)
    
    # Check for null bytes and control characters
    if '\x00' in normalized_path or any(ord(c) < 32 for c in normalized_path if c not in '\t\n\r'):
        raise ValidationError("Path contains invalid control characters")
    
    # Convert to Path and resolve
    try:
        path = Path(normalized_path).resolve()
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid path format: {e}")
    
    # Comprehensive path traversal prevention
    forbidden_patterns = [
        '..',           # Standard traversal
        '%2e%2e',       # URL encoded
        '%252e%252e',   # Double URL encoded
        '\\.\\.',       # Windows traversal
        '..\\',         # Windows traversal
        '../',          # Unix traversal
        '\\x2e\\x2e',   # Hex encoded
        'file://',      # File URI
        'ftp://',       # FTP URI
        'http://',      # HTTP URI
        'https://',     # HTTPS URI
    ]
    
    path_str_lower = str(path).lower()
    for pattern in forbidden_patterns:
        if pattern in path_str_lower:
            raise ValidationError(f"Path traversal pattern detected: {pattern}")
    
    # Prevent access to sensitive system paths (but allow temp directories for testing)
    sensitive_paths = [
        '/etc', '/root', '/sys', '/proc', '/dev', '/boot', '/var/log',
        '/usr/bin', '/bin', '/sbin', '/usr/sbin',
        'C:\\Windows', 'C:\\Program Files', 'C:\\System Volume Information'
    ]
    
    path_str_resolved = str(path).replace('\\', '/')
    for sensitive in sensitive_paths:
        if path_str_resolved.startswith(sensitive.replace('\\', '/')):
            raise ValidationError(f"Access to system path denied: {sensitive}")
    
    # Special handling for /tmp and /var/tmp - allow if it's clearly a temp directory for testing
    if path_str_resolved.startswith(('/tmp', '/var/tmp')):
        # Allow if it's a subdirectory (likely a test temp dir)
        if len(Path(path_str_resolved).parts) <= 2:
            raise ValidationError(f"Access to system root temp directory denied: {path_str_resolved}")
        # Allow subdirectories for testing
    
    # Check for symbolic link attacks
    try:
        if path.is_symlink():
            real_path = path.readlink()
            # Recursively validate the target (with recursion limit)
            if str(real_path) != str(path):  # Prevent infinite recursion
                validate_project_path(str(real_path))
    except (OSError, RecursionError):
        raise ValidationError("Symbolic link validation failed")
    
    # Ensure path exists and is accessible
    if not path.exists():
        raise ValidationError(f"Path does not exist: {path}")
    
    if not os.access(path, os.R_OK):
        raise ValidationError(f"Path is not readable: {path}")
    
    return path

def validate_patterns(patterns: list) -> list:
    """Validate and sanitize file patterns against comprehensive injection attacks."""
    if not patterns:
        return []
    
    validated = []
    
    # Comprehensive dangerous character detection
    dangerous_patterns = [
        r'[;&|`$]',           # Shell operators
        r'\\x[0-9a-fA-F]{2}', # Hex escape sequences
        r'%[0-9a-fA-F]{2}',   # URL encoding
        r'\\[nrtbfav]',       # Escape sequences
        r'\$\{.*\}',          # Variable expansion
        r'\$\(.*\)',          # Command substitution
        r'`.*`',              # Backtick execution
        r'<.*>',              # Redirection
        r'\|\|',              # Logical OR
        r'&&',                # Logical AND
        r'>>',                # Append redirection
        r'<<',                # Here document
    ]
    
    combined_pattern = '|'.join(dangerous_patterns)
    dangerous_regex = re.compile(combined_pattern)
    
    for pattern in patterns:
        if not isinstance(pattern, str):
            continue
        
        # Remove leading/trailing whitespace
        pattern = pattern.strip()
        
        if not pattern:
            continue
        
        # Check for dangerous patterns
        if dangerous_regex.search(pattern):
            print(f"⚠️  Skipping potentially dangerous pattern: {pattern}")
            continue
        
        # Length validation to prevent DoS
        if len(pattern) > 200:
            print(f"⚠️  Pattern too long, truncating: {pattern[:50]}...")
            pattern = pattern[:200]
        
        # Additional validation for glob patterns
        if not _is_valid_glob_pattern(pattern):
            print(f"⚠️  Invalid glob pattern, skipping: {pattern}")
            continue
        
        validated.append(pattern)
    
    return validated

def _is_valid_glob_pattern(pattern: str) -> bool:
    """Validate that pattern is a safe glob pattern."""
    import fnmatch
    
    try:
        # Test compile the pattern
        fnmatch.translate(pattern)
        
        # Additional safety checks
        if pattern.count('*') > 10:  # Prevent excessive wildcards
            return False
        
        if pattern.count('?') > 50:  # Prevent excessive single char wildcards
            return False
        
        return True
        
    except Exception:
        return False

# Retry Decorator
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """Decorator for retrying operations with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        # Log successful retry
                        logger = logging.getLogger("gemini_review")
                        logger.info(f"Operation succeeded on attempt {attempt + 1}")
                    return result
                    
                except Exception as e:
                    last_exception = e
                    logger = logging.getLogger("gemini_review")
                    
                    if attempt == max_retries:
                        logger.error(f"Operation failed after {max_retries} retries: {e}")
                        raise
                    
                    # Calculate delay with jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0.1, 0.9) * delay
                    total_delay = delay + jitter
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {total_delay:.1f}s...")
                    time.sleep(total_delay)
            
            raise last_exception
        return wrapper
    return decorator

# Logging Setup Function
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up comprehensive logging with both console and file output."""
    logger = logging.getLogger("gemini_review")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_path}")
    
    return logger

class GeminiCodeReviewer:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, fallback_model: Optional[str] = None, 
                 enable_cache: bool = True, cache_dir: str = ".gemini-cache", cache_max_age_hours: int = 24,
                 log_level: str = "INFO", log_file: Optional[str] = None):
        """Initialize the code reviewer with API key and fallback model."""
        # Set up logging first
        self.logger = setup_logging(log_level, log_file)
        self.logger.info("Initializing Gemini Code Reviewer")
        
        # Get secure API key
        try:
            self.api_key = self.get_secure_api_key(api_key)
            self.logger.info("API key obtained successfully")
        except Exception as e:
            self.logger.error(f"Failed to obtain API key: {e}")
            raise ConfigurationError(f"Failed to initialize reviewer: {e}")
        
        # Get model name from env or use default
        self.model_name = model_name or os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.fallback_model = fallback_model or os.getenv('GEMINI_FALLBACK_MODEL', 'gemini-2.5-flash')
        
        # Configure Gemini
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.logger.info(f"Using model: {self.model_name}")
            print(f"🤖 Using model: {self.model_name}")
            print(f"🔄 Fallback model: {self.fallback_model}")
        except Exception as e:
            self.logger.error(f"Failed to configure Gemini model: {e}")
            raise ConfigurationError(f"Failed to configure Gemini: {e}")
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(max_calls=50, time_window=60)
        self.logger.info("Rate limiter initialized")
        
        # Initialize cache if available
        self.cache = None
        if enable_cache and CACHE_AVAILABLE:
            self.cache = ReviewCache(cache_dir, cache_max_age_hours)
            self.logger.info(f"Cache enabled: {cache_dir}")
            print(f"💾 Cache enabled: {cache_dir}")
        elif enable_cache and not CACHE_AVAILABLE:
            self.logger.warning("Cache requested but cache module not available")
            print("⚠️  Cache requested but cache module not available")
        else:
            self.logger.info("Cache disabled")
            print("🚫 Cache disabled")
    
    def get_secure_api_key(self, api_key_arg: Optional[str] = None) -> str:
        """Get API key securely with comprehensive error handling and fallback."""
        # 1. Warn about insecure command line usage but allow it
        if api_key_arg:
            self.logger.warning("API key passed via command line is insecure")
            print("⚠️  WARNING: API key passed via command line is insecure")
            print("   Consider using environment variables or system keyring")
            if not self._validate_api_key_format(api_key_arg):
                raise ValidationError("Invalid API key format")
            return api_key_arg
        
        # 2. Try environment variable (preferred)
        env_key = os.getenv('GEMINI_API_KEY')
        if env_key and env_key != 'your-gemini-api-key-here':
            if not self._validate_api_key_format(env_key):
                raise ValidationError("Invalid API key format in environment variable")
            self.logger.info("Using API key from environment variable")
            return env_key
        
        # 3. Try system keyring with comprehensive error handling
        try:
            keyring_key = keyring.get_password("gemini-review-tool", "api_key")
            if keyring_key:
                if not self._validate_api_key_format(keyring_key):
                    self.logger.error("Invalid API key format in keyring, removing")
                    keyring.delete_password("gemini-review-tool", "api_key")
                    raise ValidationError("Invalid API key format in keyring")
                self.logger.info("Using API key from system keyring")
                return keyring_key
        except Exception as e:
            self.logger.warning(f"Keyring access failed: {e}")
        
        # 4. Secure prompting with validation and save option
        if sys.stdin.isatty():
            try:
                prompted_key = getpass.getpass("Enter Gemini API key: ")
                if not prompted_key:
                    raise KeyboardInterrupt()
                
                if not self._validate_api_key_format(prompted_key):
                    raise ValidationError("Invalid API key format")
                
                # Offer to save to keyring with error handling
                save_choice = input("Save API key to system keyring for future use? (y/N): ").lower()
                
                if save_choice == 'y':
                    try:
                        keyring.set_password("gemini-review-tool", "api_key", prompted_key)
                        self.logger.info("API key saved to system keyring")
                        print("✅ API key saved to system keyring")
                    except Exception as e:
                        self.logger.warning(f"Could not save to keyring: {e}")
                        print(f"⚠️  Could not save to keyring: {e}")
                
                return prompted_key
                
            except KeyboardInterrupt:
                self.logger.error("API key input cancelled by user")
                print("\n❌ API key required for operation")
                sys.exit(1)
            except Exception as e:
                self.logger.error(f"Secure prompting failed: {e}")
                raise ConfigurationError(f"Secure prompting failed: {e}")
        
        # 5. Final fallback - comprehensive error
        self.logger.error("No valid API key provided through any method")
        raise ConfigurationError(
            "No valid API key provided. Options:\n"
            "1. Set GEMINI_API_KEY environment variable\n"
            "2. Save to system keyring using interactive mode\n"
            "3. Run in interactive mode for secure prompting"
        )
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format without making API calls."""
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Allow test keys for testing
        if api_key.startswith('test-'):
            return len(api_key) >= 10
        
        # Gemini API keys typically start with specific patterns
        if not api_key.startswith(('AIza', 'sk-')):
            return False
        
        # Check reasonable length
        if len(api_key) < 20 or len(api_key) > 200:
            return False
        
        # Check for invalid characters
        import string
        valid_chars = string.ascii_letters + string.digits + '-_'
        if not all(c in valid_chars for c in api_key):
            return False
        
        return True
        
    def run_repomix(self, project_path: str, output_format: str = "xml", 
                     ignore_patterns: Optional[List[str]] = None,
                     include_patterns: Optional[List[str]] = None,
                     remove_empty_lines: bool = True,
                     show_line_numbers: bool = False,
                     include_diffs: bool = False,
                     compress_code: bool = False,
                     token_count_encoding: str = "gemini-pro") -> Path:
        """Run repomix to package the codebase."""
        print(f"📦 Running repomix on {project_path}...")
        
        # Check cache first
        if self.cache:
            repomix_options = {
                'remove_empty_lines': remove_empty_lines,
                'show_line_numbers': show_line_numbers,
                'include_diffs': include_diffs,
                'compress_code': compress_code,
                'token_count_encoding': token_count_encoding
            }
            cached_content = self.cache.get_repomix_cache(project_path, ignore_patterns, include_patterns, repomix_options)
            if cached_content:
                # Write cached content to file
                ext = "xml" if output_format == "xml" else "md"
                output_file = Path(f"repomix-output.{ext}")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(cached_content)
                return output_file
        
        # Determine output file extension
        ext = "xml" if output_format == "xml" else "md"
        output_file = Path(f"repomix-output.{ext}")
        
        # Build repomix command
        cmd = ["npx", "repomix@latest", "--style", output_format]
        
        # Add repomix options
        if remove_empty_lines:
            cmd.append("--remove-empty-lines")
            print("🧹 Removing empty lines")
        
        if show_line_numbers:
            cmd.append("--output-show-line-numbers")
            print("📊 Adding line numbers")
        
        if include_diffs:
            cmd.append("--include-diffs")
            print("📝 Including git diffs")
        
        if compress_code:
            cmd.append("--compress")
            print("🗜️  Compressing code")
        
        if token_count_encoding:
            cmd.extend(["--token-count-encoding", token_count_encoding])
            print(f"🔢 Using token encoding: {token_count_encoding}")
        
        # Add include patterns if provided
        if include_patterns:
            include_pattern = ",".join(include_patterns)
            cmd.extend(["--include", include_pattern])
            print(f"📁 Including patterns: {include_pattern}")
        
        # Add ignore patterns if provided
        if ignore_patterns:
            ignore_pattern = ",".join(ignore_patterns)
            cmd.extend(["--ignore", ignore_pattern])
            print(f"🚫 Ignoring patterns: {ignore_pattern}")
        
        # Add path if not current directory
        if project_path != ".":
            cmd.append(project_path)
        
        try:
            # Run repomix with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise FileSystemError(f"Repomix failed with code {result.returncode}: {result.stderr}")
            
            print("✅ Repomix completed successfully")
            
            if not output_file.exists():
                raise FileSystemError(f"Repomix output file {output_file} not found")
            
            # Cache the result
            if self.cache:
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    repomix_options = {
                        'remove_empty_lines': remove_empty_lines,
                        'show_line_numbers': show_line_numbers,
                        'include_diffs': include_diffs,
                        'compress_code': compress_code,
                        'token_count_encoding': token_count_encoding
                    }
                    self.cache.set_repomix_cache(project_path, content, ignore_patterns, include_patterns, repomix_options)
                except Exception as e:
                    self.logger.warning(f"Failed to cache repomix result: {e}")
                
            return output_file
            
        except subprocess.TimeoutExpired:
            raise FileSystemError("Repomix operation timed out after 300 seconds")
        except subprocess.CalledProcessError as e:
            raise FileSystemError(f"Repomix execution failed: {e}")
        except FileNotFoundError:
            raise FileSystemError("npx not found. Please ensure Node.js is installed.")
        except Exception as e:
            raise FileSystemError(f"Unexpected error running repomix: {e}")
            
    def read_repomix_output(self, file_path: Path) -> str:
        """Read the repomix output file."""
        print(f"📖 Reading repomix output from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check file size (Gemini has token limits)
        file_size_mb = len(content) / (1024 * 1024)
        print(f"📊 File size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 10:  # Rough estimate for token limit
            print("⚠️  Warning: Large file size may exceed token limits")
        elif file_size_mb > 5:
            print("⚠️  Large file detected - analysis may take longer")
            
        return content
        
    def analyze_code(self, codebase_content: str, custom_prompt: Optional[str] = None, 
                     claims_of_success: Optional[str] = None, documentation: Optional[str] = None,
                     project_path: str = ".", ignore_patterns: Optional[List[str]] = None,
                     include_patterns: Optional[List[str]] = None, documentation_files: Optional[List[str]] = None) -> str:
        """Send codebase to Gemini for analysis."""
        print("🤖 Sending to Gemini for analysis...")
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get_analysis_cache(
                project_path, ignore_patterns, include_patterns, custom_prompt, claims_of_success, documentation_files
            )
            if cached_result:
                return cached_result
        
        # Build the critical evaluation prompt
        if claims_of_success:
            base_prompt = f"""Critically evaluate this codebase in terms of it reflecting the documentation and the previous dubious claims of success:

{claims_of_success}

Be thorough and skeptical. Look for discrepancies between the claims and the actual implementation."""
        else:
            # Fallback to standard prompt
            base_prompt = """You are an expert software architect and code reviewer. 
        Please analyze this codebase and provide:
        
        1. **Architecture Overview**: High-level assessment of the system design
        2. **Code Quality**: Identify issues with code structure, patterns, and best practices
        3. **Security Concerns**: Point out potential security vulnerabilities
        4. **Performance Issues**: Identify potential bottlenecks or inefficiencies
        5. **Technical Debt**: Areas that need refactoring or improvement
        6. **Recommendations**: Specific, actionable guidance for improvement
        
        Focus on providing practical, implementable suggestions."""
        
        if custom_prompt:
            prompt = f"{base_prompt}\n\nAdditional focus areas:\n{custom_prompt}\n\n"
        else:
            prompt = base_prompt + "\n\n"
        
        # Add documentation if provided
        if documentation:
            prompt += f"DOCUMENTATION:\n{documentation}\n\n"
            
        prompt += f"CODEBASE:\n{codebase_content}"
        
        try:
            # Apply rate limiting before API call
            self.rate_limiter.wait_if_needed()
            
            # Generate response with primary model
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise APIError("Empty response from Gemini API")
            
            print("✅ Analysis complete")
            result = response.text
            
            # Report success to rate limiter
            self.rate_limiter.handle_api_success()
            
            # Cache the result
            if self.cache:
                self.cache.set_analysis_cache(
                    project_path, result, ignore_patterns, include_patterns, custom_prompt, claims_of_success, documentation_files
                )
            
            return result
            
        except Exception as e:
            error_str = str(e)
            api_error = APIError(f"Gemini API error with {self.model_name}: {error_str}")
            
            # Report error to rate limiter for adaptive adjustment
            self.rate_limiter.handle_api_error(api_error)
            
            self.logger.error(f"Gemini API error with {self.model_name}: {error_str}")
            print(f"❌ Gemini API error with {self.model_name}: {error_str}")
            
            # Check if it's a server error, rate limit, or input size issue that might work with fallback
            if ("400" in error_str or "429" in error_str or "500" in error_str or 
                "quota" in error_str.lower() or "token size exceeds" in error_str.lower() or
                "internal error" in error_str.lower() or "server error" in error_str.lower() or
                "rate limit" in error_str.lower()):
                print(f"🔄 Retrying with fallback model: {self.fallback_model}")
                try:
                    # Apply rate limiting for fallback too
                    self.rate_limiter.wait_if_needed()
                    
                    # Create fallback model and retry
                    fallback_model = genai.GenerativeModel(self.fallback_model)
                    response = fallback_model.generate_content(prompt)
                    
                    if not response.text:
                        raise APIError("Empty response from fallback model")
                    
                    print(f"✅ Analysis complete with fallback model: {self.fallback_model}")
                    result = response.text
                    
                    # Report success to rate limiter
                    self.rate_limiter.handle_api_success()
                    
                    # Cache the result
                    if self.cache:
                        self.cache.set_analysis_cache(
                            project_path, result, ignore_patterns, include_patterns, custom_prompt, claims_of_success, documentation_files
                        )
                    
                    return result
                    
                except Exception as fallback_e:
                    fallback_error = APIError(f"Fallback model {self.fallback_model} also failed: {str(fallback_e)}")
                    self.rate_limiter.handle_api_error(fallback_error)
                    self.logger.error(f"Both models failed - giving up: {fallback_e}")
                    print(f"❌ Fallback model {self.fallback_model} also failed: {str(fallback_e)}")
                    print(f"❌ Both models failed - giving up")
                    raise fallback_error
            else:
                # Not a server error, don't retry
                raise api_error
            
    def save_results(self, results: str, output_path: str = "gemini-review.md"):
        """Save the analysis results to a file."""
        # Ensure validation reports are saved in the validation-reports subdirectory
        output_path = Path(output_path)
        
        # If the output file is a validation report, save it in the validation-reports directory
        if "validation" in output_path.name.lower() or "verify" in output_path.name.lower():
            validation_reports_dir = Path("validation-reports")
            validation_reports_dir.mkdir(exist_ok=True)
            output_path = validation_reports_dir / output_path.name
        
        print(f"💾 Saving results to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Gemini Code Review\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(results)
            
        print(f"✅ Results saved to {output_path}")
        
    def cleanup(self, repomix_file: Path):
        """Clean up temporary files."""
        if repomix_file.exists():
            repomix_file.unlink()
            print("🧹 Cleaned up temporary files")
            
    def review(self, project_path: str = ".", 
              custom_prompt: Optional[str] = None,
              output_format: str = "xml",
              keep_repomix: bool = False,
              ignore_patterns: Optional[List[str]] = None,
              include_patterns: Optional[List[str]] = None,
              remove_empty_lines: bool = True,
              show_line_numbers: bool = False,
              include_diffs: bool = False,
              compress_code: bool = False,
              token_count_encoding: str = "gemini-pro",
              claims_of_success: Optional[str] = None,
              documentation_files: Optional[List[str]] = None) -> str:
        """Main review process."""
        print(f"\n🚀 Starting Gemini Code Review for: {project_path}\n")
        
        repomix_file = None
        try:
            # Step 1: Run repomix
            repomix_file = self.run_repomix(project_path, output_format, ignore_patterns, include_patterns,
                                          remove_empty_lines, show_line_numbers, include_diffs, compress_code, token_count_encoding)
            
            # Step 2: Read the output
            codebase_content = self.read_repomix_output(repomix_file)
            
            # Step 3: Read documentation if provided
            documentation = ""
            if documentation_files:
                print("📚 Reading documentation files...")
                for doc_file in documentation_files:
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            documentation += f"\n\n--- {doc_file} ---\n\n"
                            documentation += f.read()
                    except Exception as e:
                        print(f"⚠️  Warning: Could not read {doc_file}: {e}")
            
            # Step 4: Analyze with Gemini
            results = self.analyze_code(codebase_content, custom_prompt, claims_of_success, documentation, 
                                      project_path, ignore_patterns, include_patterns, documentation_files)
            
            # Step 4: Save results
            output_file = config.output_file if config else "gemini-review.md"
            self.save_results(results, output_file)
            
            # Step 5: Cleanup (unless asked to keep)
            if not keep_repomix and repomix_file:
                self.cleanup(repomix_file)
                
            print("\n✨ Code review complete!")
            return results
            
        except Exception as e:
            print(f"\n❌ Error during review: {str(e)}")
            raise
        finally:
            # Ensure cleanup even on error
            if not keep_repomix and repomix_file and repomix_file.exists():
                self.cleanup(repomix_file)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated code review using Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review current directory
  python gemini_review.py
  
  # Review with config file
  python gemini_review.py --config project-review.yaml
  
  # Use a review template
  python gemini_review.py --template security
  
  # Initialize config for a new project
  python gemini_review.py --init
  
  # Review specific project
  python gemini_review.py /path/to/project
  
  # With custom focus
  python gemini_review.py --prompt "Focus on security vulnerabilities"
  
  # Use markdown format (better for large codebases)
  python gemini_review.py --format markdown
  
  # Keep repomix output for debugging
  python gemini_review.py --keep-repomix
  
  # Evaluate specific claims
  python gemini_review.py --claims "This code is production-ready"
  
  # Include documentation files
  python gemini_review.py --docs README.md --docs docs/API.md
        """
    )
    
    parser.add_argument(
        'project_path',
        nargs='?',
        default='.',
        help='Path to the project to review (default: current directory)'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        help='Additional prompt for specific review focus'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['xml', 'markdown'],
        default='xml',
        help='Repomix output format (default: xml)'
    )
    
    parser.add_argument(
        '--keep-repomix', '-k',
        action='store_true',
        help='Keep the repomix output file'
    )
    
    parser.add_argument(
        '--api-key',
        help='Gemini API key (can also be set via GEMINI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--fallback-model',
        help='Fallback model to use if primary model fails (default: gemini-2.5-flash)'
    )
    
    parser.add_argument(
        '--ignore', '-i',
        action='append',
        help='Patterns to ignore in repomix (can be used multiple times)'
    )
    
    parser.add_argument(
        '--include', '-I',
        action='append',
        help='Patterns to include in repomix (can be used multiple times, overrides ignore)'
    )
    
    parser.add_argument(
        '--no-remove-empty-lines',
        action='store_true',
        help='Keep empty lines in output (default: remove empty lines)'
    )
    
    parser.add_argument(
        '--line-numbers',
        action='store_true',
        help='Add line numbers to output for easier reference'
    )
    
    parser.add_argument(
        '--include-diffs',
        action='store_true',
        help='Include git diffs in the output (shows changes since last commit)'
    )
    
    parser.add_argument(
        '--compress',
        action='store_true',
        help='Compress code to reduce token count (for large codebases)'
    )
    
    parser.add_argument(
        '--token-encoding',
        default='gemini-pro',
        help='Token count encoding for accurate LLM token estimation (default: gemini-pro)'
    )
    
    parser.add_argument(
        '--claims', '-c',
        help='Previous claims of success to evaluate against'
    )
    
    parser.add_argument(
        '--docs', '-d',
        action='append',
        help='Documentation files to include (can be used multiple times)'
    )
    
    parser.add_argument(
        '--config', '-C',
        help='Path to configuration file (YAML or JSON)'
    )
    
    parser.add_argument(
        '--template', '-t',
        help='Use a predefined review template (e.g., security, performance, refactoring)'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize a new configuration file for the project'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Gemini Review Tool v1.0.0'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching (force fresh analysis)'
    )
    
    parser.add_argument(
        '--cache-dir',
        default='.gemini-cache',
        help='Cache directory (default: .gemini-cache)'
    )
    
    parser.add_argument(
        '--cache-max-age',
        type=int,
        default=24,
        help='Cache max age in hours (default: 24)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear all cache files before running'
    )
    
    parser.add_argument(
        '--cache-info',
        action='store_true',
        help='Show cache information and exit'
    )
    
    args = parser.parse_args()
    
    # Handle --init flag
    if args.init:
        if CONFIG_AVAILABLE:
            config = create_default_config(args.project_path or ".")
            config_path = ".gemini-review.yaml"
            config.save_to_file(config_path)
            print(f"✅ Created configuration file: {config_path}")
            print("📝 Edit this file to customize your review settings")
            sys.exit(0)
        else:
            print("❌ Config module not available. Please ensure gemini_review_config.py is in the same directory.")
            sys.exit(1)
    
    # Handle --cache-info flag
    if args.cache_info:
        if CACHE_AVAILABLE:
            cache = ReviewCache(args.cache_dir, args.cache_max_age)
            info = cache.get_cache_info()
            print("📊 Cache Information:")
            print(f"   Directory: {info['cache_dir']}")
            print(f"   Total files: {info['total_files']}")
            print(f"   Total size: {info['total_size_mb']:.2f} MB")
            print(f"   Repomix cache: {info['repomix_cache_count']} files")
            print(f"   Analysis cache: {info['analysis_cache_count']} files")
            sys.exit(0)
        else:
            print("❌ Cache module not available")
            sys.exit(1)
    
    # Handle --clear-cache flag
    if args.clear_cache:
        if CACHE_AVAILABLE:
            cache = ReviewCache(args.cache_dir, args.cache_max_age)
            cache.clear_cache()
            print("✅ Cache cleared")
            if not args.project_path:
                sys.exit(0)
        else:
            print("❌ Cache module not available")
            sys.exit(1)
    
    try:
        # Load configuration
        config = None
        if CONFIG_AVAILABLE:
            if args.config:
                # Use specified config file
                config = ReviewConfig.load_from_file(args.config)
            else:
                # Search for config file
                config_path = find_config_file(args.project_path or ".")
                if config_path:
                    print(f"📋 Using config file: {config_path}")
                    config = ReviewConfig.load_from_file(config_path)
        
        # Apply command-line overrides to config
        if config:
            if args.project_path:
                # Validate project path
                validated_path = validate_project_path(args.project_path)
                config.project_path = str(validated_path)
            if args.format:
                config.output_format = args.format
            if args.keep_repomix is not None:
                config.keep_repomix = args.keep_repomix
            if args.ignore:
                validated_ignore = validate_patterns(args.ignore)
                config.ignore_patterns.extend(validated_ignore)
            if args.include:
                validated_include = validate_patterns(args.include)
                config.include_patterns.extend(validated_include)
            if args.no_remove_empty_lines:
                config.remove_empty_lines = False
            if args.line_numbers:
                config.show_line_numbers = True
            if args.include_diffs:
                config.include_diffs = True
            if args.compress:
                config.compress_code = True
            if args.token_encoding:
                config.token_count_encoding = args.token_encoding
            if args.claims:
                config.claims_of_success = args.claims
            if args.docs:
                config.documentation_files.extend(args.docs)
            if args.prompt:
                config.custom_prompt = args.prompt
                
            # Apply template if specified
            if args.template:
                template = config.get_review_template(args.template)
                if template:
                    config.custom_prompt = template.get('prompt', config.custom_prompt)
                    print(f"📋 Using review template: {args.template}")
                else:
                    print(f"⚠️  Unknown template: {args.template}")
        
        # Initialize reviewer with logging
        enable_cache = not args.no_cache
        log_level = "DEBUG" if args.project_path and "debug" in args.project_path.lower() else "INFO"
        reviewer = GeminiCodeReviewer(
            api_key=args.api_key, 
            fallback_model=args.fallback_model,
            enable_cache=enable_cache,
            cache_dir=args.cache_dir,
            cache_max_age_hours=args.cache_max_age
        )
        
        # Run review with config or command-line args
        if config:
            reviewer.review(
                project_path=config.project_path,
                custom_prompt=config.custom_prompt,
                output_format=config.output_format,
                keep_repomix=config.keep_repomix,
                ignore_patterns=config.ignore_patterns,
                include_patterns=config.include_patterns,
                remove_empty_lines=config.remove_empty_lines,
                show_line_numbers=config.show_line_numbers,
                include_diffs=config.include_diffs,
                compress_code=config.compress_code,
                token_count_encoding=config.token_count_encoding,
                claims_of_success=config.claims_of_success,
                documentation_files=config.documentation_files
            )
        else:
            # Validate patterns for standalone usage
            validated_ignore = validate_patterns(args.ignore or [])
            validated_include = validate_patterns(args.include or [])
            
            reviewer.review(
                project_path=args.project_path,
                custom_prompt=args.prompt,
                output_format=args.format,
                keep_repomix=args.keep_repomix,
                ignore_patterns=validated_ignore,
                include_patterns=validated_include,
                remove_empty_lines=not args.no_remove_empty_lines,
                show_line_numbers=args.line_numbers,
                include_diffs=args.include_diffs,
                compress_code=args.compress,
                token_count_encoding=args.token_encoding,
                claims_of_success=args.claims,
                documentation_files=args.docs
            )
        
    except (ValidationError, ConfigurationError) as e:
        print(f"\n❌ Configuration error: {str(e)}")
        sys.exit(1)
    except (APIError, FileSystemError) as e:
        print(f"\n❌ Operation error: {str(e)}")
        sys.exit(1)
    except ReviewError as e:
        print(f"\n❌ Review error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected fatal error: {str(e)}")
        logger = logging.getLogger("gemini_review")
        logger.exception("Unexpected fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()