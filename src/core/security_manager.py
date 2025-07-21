"""
Security Manager for Production Environment
Provides comprehensive security features including authentication, authorization,
data protection, and security auditing.
"""

import os
import hashlib
import secrets
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import jwt
from cryptography.fernet import Fernet
import bcrypt
import time
from functools import wraps
import re

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for different operations."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ADMIN = "admin"
    SYSTEM = "system"

class AuditAction(Enum):
    """Audit actions for security events."""
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_VIOLATION = "security_violation"
    CONFIGURATION_CHANGE = "configuration_change"

@dataclass
class SecurityEvent:
    """Security event for audit logging."""
    action: AuditAction
    user_id: Optional[str]
    resource: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"

@dataclass
class User:
    """User entity with security attributes."""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

class SecurityManager:
    """
    Production-grade security manager with comprehensive security features.
    
    Provides authentication, authorization, encryption, and audit logging.
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.users: Dict[str, User] = {}
        self.security_events: List[SecurityEvent] = []
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, List[float]] = {}
        self.blocked_ips: Set[str] = set()
        self.security_config = self._load_security_config()
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data."""
        key_material = f"{self.secret_key}_encryption"
        return Fernet.generate_key()
    
    def _load_security_config(self) -> Dict[str, Any]:
        """Load security configuration."""
        return {
            'password_min_length': 12,
            'password_require_special': True,
            'password_require_numbers': True,
            'password_require_uppercase': True,
            'max_failed_login_attempts': 5,
            'account_lockout_duration': 3600,  # 1 hour
            'session_timeout': 3600,  # 1 hour
            'jwt_expiration': 3600,  # 1 hour
            'rate_limit_requests': 100,
            'rate_limit_window': 3600,  # 1 hour
            'audit_retention_days': 90
        }
    
    def create_user(self, username: str, email: str, password: str, 
                   roles: Optional[Set[str]] = None) -> str:
        """
        Create a new user with security validations.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            roles: User roles
            
        Returns:
            User ID
            
        Raises:
            SecurityValidationError: If security requirements not met
        """
        # Validate password strength
        if not self._validate_password_strength(password):
            raise SecurityValidationError("Password does not meet security requirements")
        
        # Validate email format
        if not self._validate_email(email):
            raise SecurityValidationError("Invalid email format")
        
        # Check if user already exists
        if any(user.username == username or user.email == email for user in self.users.values()):
            raise SecurityValidationError("User already exists")
        
        # Generate user ID and hash password
        user_id = secrets.token_urlsafe(16)
        password_hash = self._hash_password(password)
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            roles=roles or set(),
            permissions=self._get_default_permissions(roles or set())
        )
        
        self.users[user_id] = user
        
        # Log security event
        self._log_security_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=None,  # System action
            resource=f"user:{user_id}",
            timestamp=datetime.now(),
            details={'action': 'user_created', 'username': username}
        ))
        
        return user_id
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: Optional[str] = None) -> Optional[str]:
        """
        Authenticate user credentials.
        
        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address
            
        Returns:
            User ID if authentication successful, None otherwise
        """
        # Check if IP is blocked
        if ip_address and ip_address in self.blocked_ips:
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="authentication",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={'reason': 'ip_blocked'},
                risk_level="high"
            ))
            return None
        
        # Find user by username or email
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="authentication",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={'reason': 'user_not_found', 'username': username},
                risk_level="medium"
            ))
            return None
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now():
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=user.user_id,
                resource="authentication",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={'reason': 'account_locked'},
                risk_level="medium"
            ))
            return None
        
        # Check if account is active
        if not user.is_active:
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=user.user_id,
                resource="authentication",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={'reason': 'account_inactive'},
                risk_level="medium"
            ))
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= self.security_config['max_failed_login_attempts']:
                user.locked_until = datetime.now() + timedelta(
                    seconds=self.security_config['account_lockout_duration']
                )
                
                self._log_security_event(SecurityEvent(
                    action=AuditAction.SECURITY_VIOLATION,
                    user_id=user.user_id,
                    resource="authentication",
                    timestamp=datetime.now(),
                    ip_address=ip_address,
                    details={'reason': 'account_locked_failed_attempts'},
                    risk_level="high"
                ))
            
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=user.user_id,
                resource="authentication",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={'reason': 'invalid_password'},
                risk_level="medium"
            ))
            return None
        
        # Reset failed attempts on successful authentication
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        
        self._log_security_event(SecurityEvent(
            action=AuditAction.LOGIN,
            user_id=user.user_id,
            resource="authentication",
            timestamp=datetime.now(),
            ip_address=ip_address,
            details={'username': user.username}
        ))
        
        return user.user_id
    
    def generate_jwt_token(self, user_id: str, expires_in: Optional[int] = None) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user_id: User ID
            expires_in: Token expiration time in seconds
            
        Returns:
            JWT token string
        """
        user = self.users.get(user_id)
        if not user:
            raise SecurityValidationError("User not found")
        
        expires_in = expires_in or self.security_config['jwt_expiration']
        expiration = datetime.now() + timedelta(seconds=expires_in)
        
        payload = {
            'user_id': user_id,
            'username': user.username,
            'roles': list(user.roles),
            'permissions': list(user.permissions),
            'exp': expiration.timestamp(),
            'iat': datetime.now().timestamp(),
            'iss': 'kgas-production'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        self._log_security_event(SecurityEvent(
            action=AuditAction.ACCESS_GRANTED,
            user_id=user_id,
            resource="jwt_token",
            timestamp=datetime.now(),
            details={'token_expiration': expiration.isoformat()}
        ))
        
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check if user still exists and is active
            user_id = payload.get('user_id')
            if user_id and user_id in self.users:
                user = self.users[user_id]
                if user.is_active:
                    return payload
            
            return None
            
        except jwt.ExpiredSignatureError:
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="jwt_token",
                timestamp=datetime.now(),
                details={'reason': 'token_expired'},
                risk_level="low"
            ))
            return None
        except jwt.InvalidTokenError:
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="jwt_token",
                timestamp=datetime.now(),
                details={'reason': 'invalid_token'},
                risk_level="medium"
            ))
            return None
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_id: User ID
            permission: Permission string
            
        Returns:
            True if user has permission, False otherwise
        """
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        
        has_permission = permission in user.permissions
        
        self._log_security_event(SecurityEvent(
            action=AuditAction.ACCESS_GRANTED if has_permission else AuditAction.ACCESS_DENIED,
            user_id=user_id,
            resource=f"permission:{permission}",
            timestamp=datetime.now(),
            details={'permission': permission, 'granted': has_permission}
        ))
        
        return has_permission
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Encrypted data as string
        """
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data as string
            
        Returns:
            Decrypted plain text data
        """
        decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    def generate_api_key(self, user_id: str, name: str, permissions: Set[str]) -> str:
        """
        Generate API key for user.
        
        Args:
            user_id: User ID
            name: API key name
            permissions: API key permissions
            
        Returns:
            API key string
        """
        api_key = secrets.token_urlsafe(32)
        
        self.api_keys[api_key] = {
            'user_id': user_id,
            'name': name,
            'permissions': permissions,
            'created_at': datetime.now(),
            'last_used': None,
            'is_active': True
        }
        
        self._log_security_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="api_key",
            timestamp=datetime.now(),
            details={'action': 'api_key_created', 'name': name}
        ))
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify API key and return information.
        
        Args:
            api_key: API key string
            
        Returns:
            API key information if valid, None otherwise
        """
        if api_key not in self.api_keys:
            return None
        
        key_info = self.api_keys[api_key]
        
        if not key_info['is_active']:
            return None
        
        # Update last used timestamp
        key_info['last_used'] = datetime.now()
        
        return key_info
    
    def rate_limit_check(self, identifier: str, requests_per_window: Optional[int] = None) -> bool:
        """
        Check rate limiting for identifier.
        
        Args:
            identifier: Rate limit identifier (IP, user ID, etc.)
            requests_per_window: Requests per time window
            
        Returns:
            True if request allowed, False if rate limited
        """
        requests_per_window = requests_per_window or self.security_config['rate_limit_requests']
        window_size = self.security_config['rate_limit_window']
        
        current_time = time.time()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Clean old requests outside window
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier]
            if current_time - req_time < window_size
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[identifier]) >= requests_per_window:
            self._log_security_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="rate_limit",
                timestamp=datetime.now(),
                details={'identifier': identifier, 'reason': 'rate_limit_exceeded'},
                risk_level="medium"
            ))
            return False
        
        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength according to security policy."""
        config = self.security_config
        
        if len(password) < config['password_min_length']:
            return False
        
        if config['password_require_uppercase'] and not re.search(r'[A-Z]', password):
            return False
        
        if config['password_require_numbers'] and not re.search(r'\d', password):
            return False
        
        if config['password_require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _get_default_permissions(self, roles: Set[str]) -> Set[str]:
        """Get default permissions for roles."""
        role_permissions = {
            'admin': {'read', 'write', 'delete', 'admin'},
            'user': {'read', 'write'},
            'viewer': {'read'}
        }
        
        permissions = set()
        for role in roles:
            permissions.update(role_permissions.get(role, set()))
        
        return permissions
    
    def _log_security_event(self, event: SecurityEvent):
        """Log security event for audit trail."""
        self.security_events.append(event)
        
        # Log to application logger
        logger.info(f"Security Event: {event.action.value} - User: {event.user_id} - Resource: {event.resource}")
        
        # Clean old events
        cutoff_date = datetime.now() - timedelta(days=self.security_config['audit_retention_days'])
        self.security_events = [e for e in self.security_events if e.timestamp > cutoff_date]
    
    def validate_input(self, input_data: Dict[str, Any], validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive input validation with security checks.
        
        Args:
            input_data: Data to validate
            validation_rules: Optional custom validation rules
            
        Returns:
            Validation result with sanitized data
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_data': {},
            'security_issues': []
        }
        
        default_rules = {
            'max_string_length': 10000,
            'max_dict_depth': 10,
            'max_list_length': 1000,
            'allowed_file_extensions': {'.txt', '.pdf', '.json', '.yaml', '.yml'},
            'blocked_patterns': {
                'sql_injection': [r'\bUNION\b', r'\bSELECT\b', r'\bDROP\b', r'\bDELETE\b'],
                'script_injection': [r'<script[^>]*>', r'javascript:', r'vbscript:'],
                'path_traversal': [r'\.\./', r'\.\.\\\\'],
                'command_injection': [r'\|', r'&', r';', r'`']
            }
        }
        
        rules = {**default_rules, **(validation_rules or {})}
        
        try:
            validation_result['sanitized_data'] = self._validate_and_sanitize(input_data, rules, validation_result)
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f'Validation error: {str(e)}')
        
        return validation_result
    
    def _validate_and_sanitize(self, data: Any, rules: Dict[str, Any], result: Dict[str, Any], depth: int = 0) -> Any:
        """Recursively validate and sanitize data."""
        if depth > rules['max_dict_depth']:
            result['errors'].append(f'Data structure too deep (max {rules["max_dict_depth"]})')
            result['valid'] = False
            return None
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Validate key
                sanitized_key = self._sanitize_string(str(key), rules, result)
                # Validate value
                sanitized_value = self._validate_and_sanitize(value, rules, result, depth + 1)
                sanitized[sanitized_key] = sanitized_value
            return sanitized
        
        elif isinstance(data, list):
            if len(data) > rules['max_list_length']:
                result['errors'].append(f'List too long (max {rules["max_list_length"]})')
                result['valid'] = False
                return data[:rules['max_list_length']]
            
            return [self._validate_and_sanitize(item, rules, result, depth + 1) for item in data]
        
        elif isinstance(data, str):
            return self._sanitize_string(data, rules, result)
        
        elif isinstance(data, (int, float, bool)) or data is None:
            return data
        
        else:
            result['warnings'].append(f'Unsupported data type: {type(data)}')
            return str(data)
    
    def _sanitize_string(self, text: str, rules: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Sanitize string input for security."""
        if len(text) > rules['max_string_length']:
            result['warnings'].append(f'String truncated (max {rules["max_string_length"]})')
            text = text[:rules['max_string_length']]
        
        # Check for security patterns
        for pattern_type, patterns in rules['blocked_patterns'].items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    result['security_issues'].append(f'{pattern_type} pattern detected: {pattern}')
                    result['valid'] = False
                    # Replace with safe placeholder
                    text = re.sub(pattern, '[BLOCKED]', text, flags=re.IGNORECASE)
        
        # Basic XSS protection
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """Validate file path for security."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_path': file_path
        }
        
        # Check for path traversal
        if '..' in file_path or '~' in file_path:
            validation_result['errors'].append('Path traversal detected')
            validation_result['valid'] = False
        
        # Check for absolute paths in restricted contexts
        if file_path.startswith('/') and not file_path.startswith('/tmp/'):
            validation_result['warnings'].append('Absolute path detected')
        
        # Validate file extension
        import os
        _, ext = os.path.splitext(file_path)
        allowed_extensions = {'.txt', '.pdf', '.json', '.yaml', '.yml', '.md', '.py'}
        if ext and ext.lower() not in allowed_extensions:
            validation_result['warnings'].append(f'Potentially unsafe file extension: {ext}')
        
        return validation_result
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize database query for injection protection."""
        # Basic SQL injection protection
        dangerous_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b',
            r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bEXEC\b'
        ]
        
        sanitized = query
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                # Log security event
                self._log_security_event(SecurityEvent(
                    action=AuditAction.SECURITY_VIOLATION,
                    user_id=None,
                    resource='database_query',
                    timestamp=datetime.now(),
                    details={'pattern_detected': pattern, 'query': query[:100]},
                    risk_level='high'
                ))
                # Replace with safe placeholder
                sanitized = re.sub(pattern, '[BLOCKED_SQL]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive security report.
        
        Returns:
            Security report with statistics and recommendations
        """
        total_events = len(self.security_events)
        
        if total_events == 0:
            return {
                'total_events': 0,
                'event_breakdown': {},
                'security_recommendations': []
            }
        
        # Event breakdown
        event_breakdown = {}
        for event in self.security_events:
            event_breakdown[event.action.value] = event_breakdown.get(event.action.value, 0) + 1
        
        # Security recommendations
        recommendations = []
        
        # Check for high-risk events
        high_risk_events = [e for e in self.security_events if e.risk_level == "high"]
        if high_risk_events:
            recommendations.append(f"High-risk security events detected: {len(high_risk_events)}")
        
        # Check for failed login attempts
        failed_logins = event_breakdown.get('access_denied', 0)
        if failed_logins > total_events * 0.1:  # More than 10% failed attempts
            recommendations.append("High number of failed login attempts detected")
        
        # Check for blocked IPs
        if self.blocked_ips:
            recommendations.append(f"Blocked IP addresses: {len(self.blocked_ips)}")
        
        return {
            'total_events': total_events,
            'event_breakdown': event_breakdown,
            'high_risk_events': len(high_risk_events),
            'active_users': len([u for u in self.users.values() if u.is_active]),
            'locked_accounts': len([u for u in self.users.values() if u.locked_until and u.locked_until > datetime.now()]),
            'active_api_keys': len([k for k in self.api_keys.values() if k['is_active']]),
            'blocked_ips': len(self.blocked_ips),
            'security_recommendations': recommendations
        }

# Security decorators
def require_authentication(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from request context
        token = kwargs.get('token') or (hasattr(args[0], 'token') and args[0].token)
        
        if not token:
            raise SecurityValidationError("Authentication required")
        
        payload = security_manager.verify_jwt_token(token)
        if not payload:
            raise SecurityValidationError("Invalid or expired token")
        
        # Add user info to context
        kwargs['user_id'] = payload['user_id']
        kwargs['user_permissions'] = payload['permissions']
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = kwargs.get('user_id')
            
            if not user_id:
                raise SecurityValidationError("Authentication required")
            
            if not security_manager.check_permission(user_id, permission):
                raise SecurityValidationError(f"Permission required: {permission}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(requests_per_window: int = 100):
    """Decorator for rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract identifier from request context
            identifier = kwargs.get('ip_address') or kwargs.get('user_id') or 'unknown'
            
            if not security_manager.rate_limit_check(identifier, requests_per_window):
                raise SecurityValidationError("Rate limit exceeded")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Custom exceptions
class SecurityValidationError(Exception):
    """Security validation error."""
    pass

class AuthenticationError(Exception):
    """Authentication error."""
    pass

class AuthorizationError(Exception):
    """Authorization error."""
    pass

# Global security manager instance
security_manager = SecurityManager()