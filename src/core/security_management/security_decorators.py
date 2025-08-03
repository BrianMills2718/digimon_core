"""
Security Decorators

Provides decorators for authentication, authorization, and rate limiting.
"""

import logging
from functools import wraps
from typing import Callable, Any, Optional

from .security_types import SecurityValidationError, AuthenticationError, AuthorizationError, RateLimitExceededError


class SecurityDecorators:
    """Security decorators for function-level security enforcement."""
    
    def __init__(self, security_manager):
        self.security_manager = security_manager
        self.logger = logging.getLogger(__name__)
    
    def require_authentication(self, f: Callable) -> Callable:
        """
        Decorator to require authentication.
        
        Usage:
            @require_authentication
            def protected_function(token=None, **kwargs):
                pass
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract token from kwargs or args
            token = kwargs.get('token')
            if not token and hasattr(args[0] if args else None, 'token'):
                token = args[0].token
            
            if not token:
                self.logger.warning("Authentication required but no token provided")
                raise AuthenticationError("Authentication required")
            
            # Verify token
            payload = self.security_manager.authorization.verify_jwt_token(token)
            if not payload:
                self.logger.warning("Invalid or expired token provided")
                raise AuthenticationError("Invalid or expired token")
            
            # Add user info to context
            kwargs['user_id'] = payload['user_id']
            kwargs['user_permissions'] = payload['permissions']
            kwargs['user_roles'] = payload['roles']
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_permission(self, permission: str) -> Callable:
        """
        Decorator to require specific permission.
        
        Args:
            permission: Required permission string
            
        Usage:
            @require_permission('admin')
            def admin_function(user_id=None, **kwargs):
                pass
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = kwargs.get('user_id')
                
                if not user_id:
                    self.logger.warning("Permission check requires authenticated user")
                    raise AuthenticationError("Authentication required for permission check")
                
                if not self.security_manager.authorization.check_permission(user_id, permission):
                    self.logger.warning(f"User {user_id} lacks required permission: {permission}")
                    raise AuthorizationError(f"Permission required: {permission}")
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def require_role(self, role: str) -> Callable:
        """
        Decorator to require specific role.
        
        Args:
            role: Required role string
            
        Usage:
            @require_role('admin')
            def admin_function(user_id=None, **kwargs):
                pass
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = kwargs.get('user_id')
                
                if not user_id:
                    self.logger.warning("Role check requires authenticated user")
                    raise AuthenticationError("Authentication required for role check")
                
                if not self.security_manager.authorization.check_role(user_id, role):
                    self.logger.warning(f"User {user_id} lacks required role: {role}")
                    raise AuthorizationError(f"Role required: {role}")
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def rate_limit(self, requests_per_window: int = 100, window_seconds: Optional[int] = None) -> Callable:
        """
        Decorator for rate limiting.
        
        Args:
            requests_per_window: Maximum requests per time window
            window_seconds: Time window in seconds (uses config default if None)
            
        Usage:
            @rate_limit(requests_per_window=50)
            def api_function(ip_address=None, user_id=None, **kwargs):
                pass
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Extract identifier from request context
                identifier = (kwargs.get('ip_address') or 
                            kwargs.get('user_id') or 
                            'unknown')
                
                try:
                    self.security_manager.rate_limiter.enforce_rate_limit(
                        identifier, requests_per_window
                    )
                except RateLimitExceededError as e:
                    self.logger.warning(f"Rate limit exceeded for {identifier}: {e}")
                    raise
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def validate_input(self, validation_rules: Optional[dict] = None) -> Callable:
        """
        Decorator for input validation.
        
        Args:
            validation_rules: Custom validation rules
            
        Usage:
            @validate_input({'max_string_length': 1000})
            def process_data(input_data=None, **kwargs):
                pass
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                input_data = kwargs.get('input_data')
                
                if input_data and isinstance(input_data, dict):
                    validation_result = self.security_manager.input_validator.validate_input(
                        input_data, validation_rules
                    )
                    
                    if not validation_result['valid']:
                        error_msg = f"Input validation failed: {validation_result['errors']}"
                        self.logger.warning(error_msg)
                        raise SecurityValidationError(error_msg)
                    
                    # Replace input_data with sanitized version
                    kwargs['input_data'] = validation_result['sanitized_data']
                    
                    # Add validation warnings to context if any
                    if validation_result['warnings']:
                        kwargs['validation_warnings'] = validation_result['warnings']
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def block_suspicious_ips(self, f: Callable) -> Callable:
        """
        Decorator to block access from suspicious IP addresses.
        
        Usage:
            @block_suspicious_ips
            def sensitive_function(ip_address=None, **kwargs):
                pass
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = kwargs.get('ip_address')
            
            if ip_address and self.security_manager.rate_limiter.is_ip_blocked(ip_address):
                self.logger.warning(f"Access denied for blocked IP: {ip_address}")
                raise SecurityValidationError("Access denied from this IP address")
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def audit_access(self, resource_name: str, action: str = "access") -> Callable:
        """
        Decorator to audit function access.
        
        Args:
            resource_name: Name of the resource being accessed
            action: Type of action being performed
            
        Usage:
            @audit_access('user_data', 'read')
            def get_user_data(user_id=None, **kwargs):
                pass
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = kwargs.get('user_id')
                ip_address = kwargs.get('ip_address')
                
                # Log access attempt
                from .security_types import SecurityEvent, AuditAction
                from datetime import datetime
                
                self.security_manager.audit_logger.log_event(SecurityEvent(
                    action=AuditAction.DATA_ACCESS,
                    user_id=user_id,
                    resource=resource_name,
                    timestamp=datetime.now(),
                    ip_address=ip_address,
                    details={
                        'function': f.__name__,
                        'action': action,
                        'module': f.__module__
                    }
                ))
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def require_secure_connection(self, f: Callable) -> Callable:
        """
        Decorator to require secure connection (HTTPS).
        
        Usage:
            @require_secure_connection
            def secure_function(request_secure=False, **kwargs):
                pass
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_secure = kwargs.get('request_secure', False)
            
            if not is_secure:
                self.logger.warning("Secure connection required but not provided")
                raise SecurityValidationError("Secure connection (HTTPS) required")
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def log_sensitive_operation(self, operation_name: str) -> Callable:
        """
        Decorator to log sensitive operations.
        
        Args:
            operation_name: Name of the sensitive operation
            
        Usage:
            @log_sensitive_operation('password_change')
            def change_password(user_id=None, **kwargs):
                pass
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = kwargs.get('user_id')
                ip_address = kwargs.get('ip_address')
                
                # Log sensitive operation
                from .security_types import SecurityEvent, AuditAction
                from datetime import datetime
                
                self.security_manager.audit_logger.log_event(SecurityEvent(
                    action=AuditAction.DATA_MODIFICATION,
                    user_id=user_id,
                    resource=f"sensitive_operation:{operation_name}",
                    timestamp=datetime.now(),
                    ip_address=ip_address,
                    details={
                        'operation': operation_name,
                        'function': f.__name__
                    },
                    risk_level="high"
                ))
                
                try:
                    result = f(*args, **kwargs)
                    
                    # Log successful completion
                    self.security_manager.audit_logger.log_event(SecurityEvent(
                        action=AuditAction.DATA_MODIFICATION,
                        user_id=user_id,
                        resource=f"sensitive_operation:{operation_name}",
                        timestamp=datetime.now(),
                        ip_address=ip_address,
                        details={
                            'operation': operation_name,
                            'function': f.__name__,
                            'status': 'completed'
                        }
                    ))
                    
                    return result
                    
                except Exception as e:
                    # Log failed operation
                    self.security_manager.audit_logger.log_event(SecurityEvent(
                        action=AuditAction.SECURITY_VIOLATION,
                        user_id=user_id,
                        resource=f"sensitive_operation:{operation_name}",
                        timestamp=datetime.now(),
                        ip_address=ip_address,
                        details={
                            'operation': operation_name,
                            'function': f.__name__,
                            'status': 'failed',
                            'error': str(e)
                        },
                        risk_level="high"
                    ))
                    raise
            
            return decorated_function
        return decorator


# Global security manager instance (will be set by SecurityManager)
_global_security_manager = None

def set_global_security_manager(security_manager):
    """Set the global security manager instance."""
    global _global_security_manager
    _global_security_manager = security_manager

# Convenience decorator functions that use global security manager
def require_authentication(f: Callable) -> Callable:
    """Global authentication decorator."""
    if not _global_security_manager:
        raise RuntimeError("Global security manager not set")
    return _global_security_manager.decorators.require_authentication(f)

def require_permission(permission: str) -> Callable:
    """Global permission decorator."""
    if not _global_security_manager:
        raise RuntimeError("Global security manager not set")
    return _global_security_manager.decorators.require_permission(permission)

def require_role(role: str) -> Callable:
    """Global role decorator."""
    if not _global_security_manager:
        raise RuntimeError("Global security manager not set")
    return _global_security_manager.decorators.require_role(role)

def rate_limit(requests_per_window: int = 100) -> Callable:
    """Global rate limit decorator."""
    if not _global_security_manager:
        raise RuntimeError("Global security manager not set")
    return _global_security_manager.decorators.rate_limit(requests_per_window)