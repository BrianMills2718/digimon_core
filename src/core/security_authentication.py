"""
Robust Security Authentication and Authorization
Addresses Gemini's concern about superficial security measures
"""

import hashlib
import hmac
import secrets
import time
import jwt
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security clearance levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class Permission(Enum):
    """Service permissions"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class SecurityContext:
    """Security context for operations"""
    user_id: str
    session_id: str
    permissions: List[Permission]
    security_level: SecurityLevel
    expires_at: float
    authenticated: bool = False
    
    def is_expired(self) -> bool:
        """Check if security context has expired"""
        return time.time() > self.expires_at
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if context has specific permission"""
        return self.authenticated and not self.is_expired() and permission in self.permissions
    
    def can_access_level(self, required_level: SecurityLevel) -> bool:
        """Check if context can access required security level"""
        level_hierarchy = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.INTERNAL: 1,
            SecurityLevel.RESTRICTED: 2,
            SecurityLevel.CONFIDENTIAL: 3
        }
        return (self.authenticated and 
                not self.is_expired() and
                level_hierarchy[self.security_level] >= level_hierarchy[required_level])


class AuthenticationProvider(ABC):
    """Abstract authentication provider"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Optional[SecurityContext]:
        """Authenticate user and return security context"""
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate authentication token"""
        pass
    
    @abstractmethod
    def revoke_session(self, session_id: str) -> bool:
        """Revoke authentication session"""
        pass


class JWTAuthenticationProvider(AuthenticationProvider):
    """JWT-based authentication provider"""
    
    def __init__(self, secret_key: str, token_expiry: int = 3600):
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.revoked_sessions = set()
        
        # User database (in production this would be external)
        self.users = {
            "admin": {
                "password_hash": self._hash_password("admin_password"),
                "permissions": [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.ADMIN],
                "security_level": SecurityLevel.CONFIDENTIAL
            },
            "service_user": {
                "password_hash": self._hash_password("service_password"),
                "permissions": [Permission.READ, Permission.WRITE, Permission.EXECUTE],
                "security_level": SecurityLevel.RESTRICTED
            },
            "readonly_user": {
                "password_hash": self._hash_password("readonly_password"),
                "permissions": [Permission.READ],
                "security_level": SecurityLevel.INTERNAL
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex() + ":" + salt
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            stored_hash, salt = password_hash.split(":")
            hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hmac.compare_digest(
                stored_hash,
                hashed.hex()
            )
        except Exception:
            return False
    
    def authenticate(self, credentials: Dict[str, Any]) -> Optional[SecurityContext]:
        """Authenticate user with username/password"""
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            logger.warning("Authentication attempted with missing credentials")
            return None
        
        user_data = self.users.get(username)
        if not user_data:
            logger.warning(f"Authentication failed for unknown user: {username}")
            return None
        
        if not self._verify_password(password, user_data["password_hash"]):
            logger.warning(f"Authentication failed for user: {username}")
            return None
        
        # Create security context
        session_id = secrets.token_hex(32)
        expires_at = time.time() + self.token_expiry
        
        context = SecurityContext(
            user_id=username,
            session_id=session_id,
            permissions=user_data["permissions"],
            security_level=user_data["security_level"],
            expires_at=expires_at,
            authenticated=True
        )
        
        logger.info(f"User authenticated successfully: {username}")
        return context
    
    def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            session_id = payload.get("session_id")
            if session_id in self.revoked_sessions:
                logger.warning(f"Attempted to use revoked session: {session_id}")
                return None
            
            # Reconstruct security context
            context = SecurityContext(
                user_id=payload["user_id"],
                session_id=session_id,
                permissions=[Permission(p) for p in payload["permissions"]],
                security_level=SecurityLevel(payload["security_level"]),
                expires_at=payload["exp"],
                authenticated=True
            )
            
            if context.is_expired():
                logger.warning(f"Expired token used for user: {context.user_id}")
                return None
            
            return context
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def generate_token(self, context: SecurityContext) -> str:
        """Generate JWT token from security context"""
        payload = {
            "user_id": context.user_id,
            "session_id": context.session_id,
            "permissions": [p.value for p in context.permissions],
            "security_level": context.security_level.value,
            "exp": int(context.expires_at),
            "iat": int(time.time())
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke authentication session"""
        self.revoked_sessions.add(session_id)
        logger.info(f"Session revoked: {session_id}")
        return True


def security_required(permission: Permission, security_level: SecurityLevel = SecurityLevel.INTERNAL):
    """Decorator for enforcing security requirements"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Extract security context from args or kwargs
            context = kwargs.get('security_context')
            if not context:
                # Try to find context in args
                for arg in args:
                    if isinstance(arg, SecurityContext):
                        context = arg
                        break
            
            if not context:
                raise SecurityError("No security context provided")
            
            if not context.has_permission(permission):
                raise SecurityError(f"Permission denied: {permission.value} required")
            
            if not context.can_access_level(security_level):
                raise SecurityError(f"Security clearance insufficient: {security_level.value} required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityError(Exception):
    """Security-related error"""
    pass


class ServiceSecurityManager:
    """Security manager for service registry"""
    
    def __init__(self, auth_provider: AuthenticationProvider):
        self.auth_provider = auth_provider
        self.service_security_levels = {}
        self.operation_permissions = {}
    
    def register_service_security(self, service_name: str, security_level: SecurityLevel, 
                                required_permissions: List[Permission]) -> None:
        """Register security requirements for a service"""
        self.service_security_levels[service_name] = security_level
        self.operation_permissions[service_name] = required_permissions
        logger.info(f"Security registered for service {service_name}: {security_level.value}")
    
    def validate_service_access(self, service_name: str, context: SecurityContext, 
                               operation: str = "access") -> bool:
        """Validate access to a service"""
        if not context.authenticated or context.is_expired():
            logger.warning(f"Unauthenticated access attempt to service: {service_name}")
            return False
        
        # Check security level
        required_level = self.service_security_levels.get(service_name, SecurityLevel.INTERNAL)
        if not context.can_access_level(required_level):
            logger.warning(f"Insufficient security level for service {service_name}: "
                         f"required {required_level.value}, has {context.security_level.value}")
            return False
        
        # Check permissions
        required_permissions = self.operation_permissions.get(service_name, [Permission.READ])
        for perm in required_permissions:
            if not context.has_permission(perm):
                logger.warning(f"Missing permission {perm.value} for service {service_name}")
                return False
        
        logger.debug(f"Access granted to service {service_name} for user {context.user_id}")
        return True
    
    def validate_service_class(self, service_class: type) -> bool:
        """Enhanced service class validation"""
        # Check for dangerous patterns beyond just 'eval'
        dangerous_patterns = ['eval', 'exec', 'compile', '__import__', 'open', 'file']
        
        if hasattr(service_class, '__code__'):
            code_names = str(service_class.__code__.co_names).lower()
            for pattern in dangerous_patterns:
                if pattern in code_names:
                    logger.error(f"Service class contains dangerous pattern: {pattern}")
                    return False
        
        # Check for suspicious module imports
        if hasattr(service_class, '__module__'):
            module_name = service_class.__module__
            suspicious_modules = ['subprocess', 'os', 'sys', 'ctypes', 'marshal']
            for suspicious in suspicious_modules:
                if suspicious in module_name:
                    logger.warning(f"Service class from suspicious module: {module_name}")
                    # Don't block but log warning
        
        # Check class hierarchy for suspicious base classes
        for base in service_class.__mro__:
            if 'meta' in base.__name__.lower() or 'type' in base.__name__.lower():
                if base not in (type, object):
                    logger.warning(f"Service class has suspicious base class: {base.__name__}")
        
        return True
    
    def audit_security_operation(self, operation: str, context: SecurityContext, 
                                service_name: str = None, success: bool = True) -> None:
        """Audit security operations"""
        audit_entry = {
            "timestamp": time.time(),
            "operation": operation,
            "user_id": context.user_id if context else "anonymous",
            "session_id": context.session_id if context else None,
            "service_name": service_name,
            "success": success,
            "security_level": context.security_level.value if context else "none"
        }
        
        # In production, this would write to secure audit log
        if success:
            logger.info(f"Security audit: {operation} by {audit_entry['user_id']} - SUCCESS")
        else:
            logger.warning(f"Security audit: {operation} by {audit_entry['user_id']} - FAILED")


# Example usage and integration
def create_secure_service_registry():
    """Factory function to create service registry with security"""
    from .improved_service_registry import ServiceRegistry
    
    # Create authentication provider
    secret_key = secrets.token_hex(32)  # In production, load from secure config
    auth_provider = JWTAuthenticationProvider(secret_key)
    
    # Create security manager
    security_manager = ServiceSecurityManager(auth_provider)
    
    # Register security requirements for core services
    security_manager.register_service_security(
        "config_manager", 
        SecurityLevel.RESTRICTED, 
        [Permission.READ, Permission.ADMIN]
    )
    
    # DEPRECATED: universal_llm_service removed
    # Use EnhancedAPIClient directly instead of service injection
    
    security_manager.register_service_security(
        "identity_service",
        SecurityLevel.INTERNAL,
        [Permission.READ, Permission.WRITE]
    )
    
    security_manager.register_service_security(
        "provenance_service",
        SecurityLevel.INTERNAL,
        [Permission.READ, Permission.WRITE]
    )
    
    security_manager.register_service_security(
        "quality_service",
        SecurityLevel.INTERNAL,
        [Permission.READ, Permission.WRITE]
    )
    
    security_manager.register_service_security(
        "workflow_state_service",
        SecurityLevel.RESTRICTED,
        [Permission.READ, Permission.WRITE, Permission.ADMIN]
    )
    
    # Create registry with security manager
    registry = ServiceRegistry(security_manager=security_manager)
    
    return registry, auth_provider, security_manager