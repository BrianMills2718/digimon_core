"""
Secure Error Handling Module
============================

Handles errors securely without leaking sensitive information.
Prevents timing attacks and information disclosure through error messages.

Security principles:
- No sensitive data in error messages
- No file path information disclosure
- No system architecture details in exceptions
- Consistent timing for error responses
"""

import re
import time
import logging
from typing import Any, Dict, Optional
from pathlib import Path


class SecureErrorHandler:
    """
    Secure error handler that prevents information leakage.
    
    All error messages are sanitized to prevent disclosure of:
    - File system paths
    - Sensitive data content
    - System architecture details
    - Internal implementation details
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns that should be redacted from error messages
        self.redaction_patterns = [
            # File paths
            (r'/[a-zA-Z0-9_/.-]+', '[PATH_REDACTED]'),
            (r'[A-Z]:\\[a-zA-Z0-9_\\.-]+', '[PATH_REDACTED]'),
            
            # API keys and tokens (comprehensive patterns)
            (r'sk-[a-zA-Z0-9]+', '[API_KEY_REDACTED]'),  # OpenAI style keys (any length)
            (r'[Aa]uth[a-zA-Z]*[:\s=]+[a-zA-Z0-9+/]{10,}', '[AUTH_TOKEN_REDACTED]'),
            (r'Bearer\s+[a-zA-Z0-9_\-\.]+', '[AUTH_TOKEN_REDACTED]'),  # Bearer tokens
            (r'api[_-]?key[:\s=]+[^\s]+', 'api_key=[REDACTED]'),  # API key patterns
            
            # Common sensitive patterns
            (r'password[:\s=]+[^\s]+', 'password=[REDACTED]'),
            (r'secret[:\s=]+[^\s]+', 'secret=[REDACTED]'),
            (r'token[:\s=]+[^\s]+', 'token=[REDACTED]'),
            
            # Stack trace paths (keep only the relevant error info)
            (r'File "[^"]+", line \d+', 'File "[REDACTED]", line [REDACTED]'),
            
            # Memory addresses
            (r'0x[0-9a-fA-F]+', '[MEMORY_ADDRESS_REDACTED]'),
            
            # Hostnames and ports
            (r'localhost:\d+', '[HOST_REDACTED]'),
            (r'127\.0\.0\.1:\d+', '[HOST_REDACTED]'),
        ]
        
        # Generic error messages for common error types
        self.generic_error_messages = {
            'FileNotFoundError': 'Required file not found',
            'PermissionError': 'Access denied',
            'ConnectionError': 'Network connection failed',
            'TimeoutError': 'Operation timed out',
            'ValueError': 'Invalid input value',
            'TypeError': 'Invalid data type',
            'KeyError': 'Required parameter missing',
            'AttributeError': 'Invalid operation',
            'IOError': 'Input/output operation failed',
            'OSError': 'System operation failed',
        }
    
    def sanitize_error_message(self, error_message: str, error_type: str = None) -> str:
        """
        Sanitize error message to prevent information leakage.
        
        Args:
            error_message: Original error message
            error_type: Type of error (optional)
            
        Returns:
            Sanitized error message safe for logging/display
        """
        if not error_message:
            return "Unknown error occurred"
        
        # Start with the original message
        sanitized = str(error_message)
        
        # Apply redaction patterns - order matters!
        for pattern, replacement in self.redaction_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Additional comprehensive sanitization
        # Remove any remaining sensitive patterns that might have been missed
        additional_patterns = [
            (r'sk-[a-zA-Z0-9]{32,}', '[API_KEY_REDACTED]'),  # More specific OpenAI key pattern
            (r'[a-zA-Z0-9_-]{32,}', '[TOKEN_REDACTED]'),     # Generic long tokens
            (r'Bearer\s+[a-zA-Z0-9_\-\.]+', '[AUTH_TOKEN_REDACTED]'),  # Bearer tokens
            (r'api_?key[:\s=]+[^\s]+', 'api_key=[REDACTED]'),  # API key patterns
        ]
        
        for pattern, replacement in additional_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Use generic message for common error types if available
        if error_type and error_type in self.generic_error_messages:
            # For well-known error types, use generic messages to prevent info disclosure
            generic_msg = self.generic_error_messages[error_type]
            
            # Only include sanitized details if they add value and are truly clean
            if (len(sanitized) < 100 and 
                not any(redacted in sanitized for redacted in ['[REDACTED]', '[PATH_REDACTED]', '[API_KEY_REDACTED]']) and
                not re.search(r'sk-[a-zA-Z0-9]+', sanitized, re.IGNORECASE)):
                return f"{generic_msg}: {sanitized}"
            else:
                return generic_msg
        
        return sanitized
    
    def create_safe_error_response(self, 
                                   operation: str,
                                   error: Exception,
                                   error_code: str = None,
                                   include_details: bool = False) -> Dict[str, Any]:
        """
        Create a safe error response that doesn't leak information.
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
            error_code: Specific error code for the error type
            include_details: Whether to include sanitized error details
            
        Returns:
            Safe error response dictionary
        """
        error_type = type(error).__name__
        
        # Sanitize the error message
        sanitized_message = self.sanitize_error_message(str(error), error_type)
        
        # Create base response
        response = {
            'success': False,
            'operation': operation,
            'error_code': error_code or error_type.upper(),
            'timestamp': time.time()
        }
        
        # Only include details if explicitly requested and safe
        if include_details:
            response['error_message'] = sanitized_message
        else:
            # Use generic message based on error type
            response['error_message'] = self.generic_error_messages.get(
                error_type, 
                f"Operation '{operation}' failed"
            )
        
        # Log the full error internally (with sanitization)
        self.logger.error(
            f"Operation failed: {operation}, "
            f"Error: {error_type}, "
            f"Sanitized message: {sanitized_message}"
        )
        
        return response
    
    def timing_safe_error_response(self, 
                                   success_time: float,
                                   error_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return error response with timing that matches successful operations.
        
        This prevents timing attacks that could distinguish between different
        error conditions or reveal information about system state.
        
        Args:
            success_time: Expected time for successful operation
            error_response: The error response to return
            
        Returns:
            Error response after timing normalization
        """
        # Calculate elapsed time since error occurred
        current_time = time.time()
        elapsed = current_time - error_response['timestamp']
        
        # If we're faster than expected success time, wait
        if elapsed < success_time:
            time.sleep(success_time - elapsed)
        
        # Update timestamp to reflect actual response time
        error_response['timestamp'] = time.time()
        
        return error_response
    
    def is_error_message_safe(self, message: str) -> bool:
        """
        Check if an error message is safe for external disclosure.
        
        Args:
            message: Error message to check
            
        Returns:
            True if message is safe, False if it contains sensitive information
        """
        if not message:
            return True
        
        # Check for patterns that indicate sensitive information
        for pattern, _ in self.redaction_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False
        
        # Check for common sensitive keywords
        sensitive_keywords = [
            'password', 'secret', 'token', 'key', 'credential',
            'internal', 'debug', 'trace', 'stack', 'memory',
            'localhost', '127.0.0.1', 'admin', 'root'
        ]
        
        message_lower = message.lower()
        for keyword in sensitive_keywords:
            if keyword in message_lower:
                return False
        
        return True
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log security-related events with appropriate sanitization.
        
        Supported event types:
        - SERVICE_STARTUP: Service initialization and startup
        - SERVICE_SHUTDOWN: Service shutdown and cleanup
        - CONFIG_FILE_CHANGE: Configuration file modifications
        - DATABASE_CONNECTION: Database connection events
        - CREDENTIAL_ACCESS: Credential retrieval attempts
        - SECURITY_VIOLATION: Security policy violations
        - ACCESS_DENIED: Permission denied events
        - ENCRYPTION_OPERATION: Encryption/decryption operations
        
        Args:
            event_type: Type of security event
            details: Event details to log
        """
        # Sanitize details before logging
        sanitized_details = {}
        for key, value in details.items():
            if isinstance(value, str):
                # Apply comprehensive sanitization to string values
                sanitized_value = self.sanitize_error_message(value)
                
                # Additional security-specific sanitization for common sensitive keys
                if key.lower() in ['api_key', 'token', 'password', 'secret', 'credential']:
                    sanitized_value = '[REDACTED]'
                elif 'key' in key.lower() and len(str(value)) > 8:
                    sanitized_value = '[REDACTED]'
                    
                sanitized_details[key] = sanitized_value
            else:
                sanitized_details[key] = str(value)
        
        self.logger.warning(
            f"Security event: {event_type}, "
            f"Details: {sanitized_details}"
        )
    
    def log_service_startup(self, service_name: str, version: str = None, config_source: str = None) -> None:
        """Log service startup event for audit trail."""
        self.log_security_event("SERVICE_STARTUP", {
            "service_name": service_name,
            "version": version or "unknown",
            "config_source": config_source or "default",
            "timestamp": time.time(),
            "process_id": self._get_process_id()
        })
    
    def log_service_shutdown(self, service_name: str, reason: str = "normal", cleanup_status: str = "success") -> None:
        """Log service shutdown event for audit trail."""
        self.log_security_event("SERVICE_SHUTDOWN", {
            "service_name": service_name,
            "shutdown_reason": reason,
            "cleanup_status": cleanup_status,
            "timestamp": time.time(),
            "process_id": self._get_process_id()
        })
    
    def log_config_file_change(self, file_path: str, operation: str, user: str = None, checksum_before: str = None, checksum_after: str = None) -> None:
        """Log configuration file changes for audit trail."""
        self.log_security_event("CONFIG_FILE_CHANGE", {
            "config_file": self.sanitize_error_message(file_path),  # Sanitize file path
            "operation": operation,  # created, modified, deleted
            "user": user or "system",
            "checksum_before": checksum_before,
            "checksum_after": checksum_after,
            "timestamp": time.time()
        })
    
    def log_database_connection(self, database_name: str, operation: str, status: str, connection_id: str = None, error_code: str = None) -> None:
        """Log database connection events for audit trail."""
        self.log_security_event("DATABASE_CONNECTION", {
            "database": database_name,
            "operation": operation,  # connect, disconnect, reconnect, failed
            "status": status,  # success, failed, timeout
            "connection_id": connection_id or "unknown",
            "error_code": error_code,
            "timestamp": time.time(),
            "process_id": self._get_process_id()
        })
    
    def _get_process_id(self) -> str:
        """Get current process ID for audit tracking."""
        import os
        return str(os.getpid())


# Global secure error handler instance
_secure_error_handler = None


def get_secure_error_handler() -> SecureErrorHandler:
    """Get global secure error handler instance."""
    global _secure_error_handler
    if _secure_error_handler is None:
        _secure_error_handler = SecureErrorHandler()
    return _secure_error_handler


def secure_error_response(operation: str, 
                         error: Exception,
                         error_code: str = None,
                         include_details: bool = False) -> Dict[str, Any]:
    """
    Convenience function to create secure error response.
    
    Args:
        operation: Name of the operation that failed
        error: The exception that occurred
        error_code: Specific error code
        include_details: Whether to include sanitized details
        
    Returns:
        Safe error response dictionary
    """
    handler = get_secure_error_handler()
    return handler.create_safe_error_response(operation, error, error_code, include_details)


if __name__ == "__main__":
    # Test secure error handling
    handler = SecureErrorHandler()
    
    # Test error message sanitization
    test_messages = [
        "File '/home/user/secret/api_key.txt' not found",
        "Connection failed to sk-1234567890abcdef",
        "Permission denied for /etc/password",
        "Invalid token: Bearer abc123xyz789",
        "Database error at localhost:5432"
    ]
    
    print("Error Message Sanitization Tests:")
    for msg in test_messages:
        sanitized = handler.sanitize_error_message(msg)
        safe = handler.is_error_message_safe(sanitized)
        print(f"Original: {msg}")
        print(f"Sanitized: {sanitized}")
        print(f"Safe: {safe}")
        print("-" * 50)
    
    # Test safe error response creation
    try:
        raise FileNotFoundError("/sensitive/path/credentials.json not found")
    except Exception as e:
        response = handler.create_safe_error_response("test_operation", e)
        print(f"Safe error response: {response}")
    
    print("✅ Secure error handling tests completed")