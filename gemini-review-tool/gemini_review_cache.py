#!/usr/bin/env python3
"""
Caching system for Gemini Code Review Tool

Caches repomix outputs and analysis results to avoid redundant processing.
"""

import hashlib
import json
import os
import pickle
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import lru_cache


class ReviewCache:
    """Simple file-based cache for review results."""
    
    def __init__(self, cache_dir: str = ".gemini-cache", max_age_hours: int = 24):
        """Initialize cache with directory and max age."""
        self.cache_dir = Path(cache_dir)
        self.max_age = timedelta(hours=max_age_hours)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
        
    @lru_cache(maxsize=1000)
    def _get_file_hash_optimized(self, file_path: str, file_size: int, mod_time: float) -> str:
        """Cache file hashes based on size and modification time."""
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            return ""
        
        # For large files, use sampling instead of full read
        if file_size > 10 * 1024 * 1024:  # 10MB threshold
            return self._compute_sampled_hash(path_obj)
        
        # For smaller files, compute full hash
        try:
            hash_sha256 = hashlib.sha256()
            with open(path_obj, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, IOError):
            return ""

    def _compute_sampled_hash(self, file_path: Path) -> str:
        """Compute hash using file sampling for large files."""
        hash_sha256 = hashlib.sha256()
        file_size = file_path.stat().st_size
        
        # Sample beginning, middle, and end
        sample_size = 4096
        sample_positions = [0, file_size // 2, max(0, file_size - sample_size)]
        
        try:
            with open(file_path, "rb") as f:
                for pos in sample_positions:
                    f.seek(pos)
                    chunk = f.read(sample_size)
                    hash_sha256.update(chunk)
            
            # Include file metadata for uniqueness
            hash_sha256.update(str(file_size).encode())
            hash_sha256.update(str(file_path.stat().st_mtime).encode())
            
            return hash_sha256.hexdigest()
        except (OSError, IOError):
            return ""
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate SHA256 hash of file content with optimization."""
        try:
            stat = file_path.stat()
            return self._get_file_hash_optimized(str(file_path), stat.st_size, stat.st_mtime)
        except (OSError, IOError):
            return ""
    
    def _get_directory_hash(self, directory: Path, ignore_patterns: Optional[list] = None) -> str:
        """Generate hash of directory contents, respecting ignore patterns."""
        hash_sha256 = hashlib.sha256()
        ignore_patterns = ignore_patterns or []
        
        def should_ignore(path: Path) -> bool:
            for pattern in ignore_patterns:
                if path.match(pattern):
                    return True
            return False
        
        # Collect all files and their hashes
        file_hashes = []
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file() and not should_ignore(file_path):
                try:
                    file_hash = self._get_file_hash(file_path)
                    file_hashes.append(f"{file_path.relative_to(directory)}:{file_hash}")
                except (OSError, IOError):
                    # Skip files we can't read
                    continue
        
        # Create combined hash
        combined_content = "\n".join(file_hashes).encode('utf-8')
        hash_sha256.update(combined_content)
        return hash_sha256.hexdigest()
    
    def _get_cache_key(self, project_path: str, ignore_patterns: Optional[list] = None, 
                      include_patterns: Optional[list] = None, custom_prompt: Optional[str] = None, 
                      claims: Optional[str] = None, documentation_files: Optional[list] = None,
                      repomix_options: Optional[dict] = None) -> str:
        """Generate cache key based on project path and parameters."""
        project_path = Path(project_path).resolve()
        
        # Get project hash
        if project_path.is_file():
            project_hash = self._get_file_hash(project_path)
        else:
            project_hash = self._get_directory_hash(project_path, ignore_patterns)
        
        # Create parameter hash
        params = {
            'ignore_patterns': sorted(ignore_patterns or []),
            'include_patterns': sorted(include_patterns or []),
            'custom_prompt': custom_prompt,
            'claims': claims,
            'documentation_files': sorted(documentation_files or []),
            'repomix_options': repomix_options or {}
        }
        params_hash = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
        
        return f"{project_hash}_{params_hash}"
    
    def _get_cache_path(self, cache_key: str, cache_type: str) -> Path:
        """Get cache file path for given key and type."""
        return self.cache_dir / f"{cache_key}_{cache_type}.cache"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file is still valid (not expired)."""
        if not cache_path.exists():
            return False
        
        # Check file age
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age < self.max_age
    
    def get_repomix_cache(self, project_path: str, ignore_patterns: Optional[list] = None, 
                         include_patterns: Optional[list] = None, repomix_options: Optional[dict] = None) -> Optional[str]:
        """Get cached repomix output if available and valid."""
        cache_key = self._get_cache_key(project_path, ignore_patterns, include_patterns, repomix_options=repomix_options)
        cache_path = self._get_cache_path(cache_key, "repomix")
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.cache_hits += 1
                    print(f"📋 Using cached repomix output (age: {datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)})")
                    return cached_data['content']
            except (pickle.PickleError, EOFError, KeyError):
                # Cache file corrupted, remove it
                cache_path.unlink(missing_ok=True)
        
        self.cache_misses += 1
        return None
    
    def set_repomix_cache(self, project_path: str, content: str, ignore_patterns: Optional[list] = None,
                         include_patterns: Optional[list] = None, repomix_options: Optional[dict] = None):
        """Cache repomix output."""
        cache_key = self._get_cache_key(project_path, ignore_patterns, include_patterns, repomix_options=repomix_options)
        cache_path = self._get_cache_path(cache_key, "repomix")
        
        try:
            cached_data = {
                'content': content,
                'timestamp': datetime.now(),
                'project_path': str(project_path),
                'ignore_patterns': ignore_patterns,
                'include_patterns': include_patterns,
                'repomix_options': repomix_options
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            print(f"💾 Cached repomix output")
        except (OSError, IOError) as e:
            print(f"⚠️  Failed to cache repomix output: {e}")
    
    def get_analysis_cache(self, project_path: str, ignore_patterns: Optional[list] = None,
                         include_patterns: Optional[list] = None, custom_prompt: Optional[str] = None, 
                         claims: Optional[str] = None, documentation_files: Optional[list] = None) -> Optional[str]:
        """Get cached analysis result if available and valid."""
        cache_key = self._get_cache_key(project_path, ignore_patterns, include_patterns, custom_prompt, claims, documentation_files)
        cache_path = self._get_cache_path(cache_key, "analysis")
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.cache_hits += 1
                    print(f"📋 Using cached analysis result (age: {datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)})")
                    return cached_data['content']
            except (pickle.PickleError, EOFError, KeyError):
                # Cache file corrupted, remove it
                cache_path.unlink(missing_ok=True)
        
        self.cache_misses += 1
        return None
    
    def set_analysis_cache(self, project_path: str, content: str, ignore_patterns: Optional[list] = None,
                          include_patterns: Optional[list] = None, custom_prompt: Optional[str] = None, 
                          claims: Optional[str] = None, documentation_files: Optional[list] = None):
        """Cache analysis result."""
        cache_key = self._get_cache_key(project_path, ignore_patterns, include_patterns, custom_prompt, claims, documentation_files)
        cache_path = self._get_cache_path(cache_key, "analysis")
        
        try:
            cached_data = {
                'content': content,
                'timestamp': datetime.now(),
                'project_path': str(project_path),
                'ignore_patterns': ignore_patterns,
                'include_patterns': include_patterns,
                'custom_prompt': custom_prompt,
                'claims': claims,
                'documentation_files': documentation_files
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            print(f"💾 Cached analysis result")
        except (OSError, IOError) as e:
            print(f"⚠️  Failed to cache analysis result: {e}")
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Clear cache files. If cache_type is None, clears all cache."""
        if cache_type:
            pattern = f"*_{cache_type}.cache"
        else:
            pattern = "*.cache"
        
        removed_count = 0
        for cache_file in self.cache_dir.glob(pattern):
            try:
                cache_file.unlink()
                removed_count += 1
            except OSError:
                pass
        
        print(f"🧹 Cleared {removed_count} cache files")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cache usage."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        # Count by type
        repomix_count = len(list(self.cache_dir.glob("*_repomix.cache")))
        analysis_count = len(list(self.cache_dir.glob("*_analysis.cache")))
        
        # Calculate cache hit ratio
        total_requests = self.cache_hits + self.cache_misses
        hit_ratio = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'repomix_cache_count': repomix_count,
            'analysis_cache_count': analysis_count,
            'cache_dir': str(self.cache_dir),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_ratio': hit_ratio
        } 