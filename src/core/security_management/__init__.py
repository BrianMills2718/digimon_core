"""
Security Management Module

Decomposed security manager components for comprehensive security features including
authentication, authorization, encryption, audit logging, and input validation.
"""

# Import core types and configuration
from .security_types import (
    SecurityLevel,
    AuditAction,
    SecurityEvent,
    User,
    SecurityConfig,
    SecurityKeyManager,
    SecurityValidationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
    InputValidationError
)

# Import main components
from .authentication import AuthenticationManager
from .authorization import AuthorizationManager
from .audit_logger import AuditLogger
from .input_validator import InputValidator
from .rate_limiter import RateLimiter
from .encryption_manager import EncryptionManager
from .security_decorators import SecurityDecorators

# Main security manager class is in parent directory to avoid circular imports

# Import decorator functions
from .security_decorators import (
    require_authentication,
    require_permission,
    require_role,
    rate_limit,
    set_global_security_manager
)

__all__ = [
    # Core types and configuration
    "SecurityLevel",
    "AuditAction", 
    "SecurityEvent",
    "User",
    "SecurityConfig",
    "SecurityKeyManager",
    
    # Exceptions
    "SecurityValidationError",
    "AuthenticationError",
    "AuthorizationError", 
    "RateLimitExceededError",
    "InputValidationError",
    
    # Component classes
    "AuthenticationManager",
    "AuthorizationManager",
    "AuditLogger",
    "InputValidator",
    "RateLimiter",
    "EncryptionManager",
    "SecurityDecorators",
    
    # Main security manager class is in parent directory
    
    # Decorator functions
    "require_authentication",
    "require_permission",
    "require_role",
    "rate_limit",
    "set_global_security_manager"
]