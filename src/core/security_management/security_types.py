"""
Security Types and Configuration

Core types, enums, and configuration for the security management system.
"""

import os
import secrets
from enum import Enum
from typing import Dict, Any, Set, Optional
from datetime import datetime
from dataclasses import dataclass, field


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


class SecurityConfig:
    """Security configuration management."""
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        self.config = self._load_default_config()
        if custom_config:
            self.config.update(custom_config)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default security configuration."""
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
            'audit_retention_days': 90,
            'max_string_length': 10000,
            'max_dict_depth': 10,
            'max_list_length': 1000,
            'allowed_file_extensions': {'.txt', '.pdf', '.json', '.yaml', '.yml', '.md', '.py'},
            'blocked_sql_patterns': [
                r'\bUNION\b', r'\bSELECT\b', r'\bDROP\b', r'\bDELETE\b',
                r'\bUPDATE\b', r'\bINSERT\b', r'\bALTER\b', r'\bCREATE\b',
                r'\bTRUNCATE\b', r'\bEXEC\b'
            ],
            'blocked_script_patterns': [
                r'<script[^>]*>', r'javascript:', r'vbscript:'
            ],
            'blocked_path_patterns': [
                r'\.\./', r'\.\.\\\\', r'~'
            ],
            'blocked_command_patterns': [
                r'\|', r'&', r';', r'`'
            ]
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for input sanitization."""
        return {
            'max_string_length': self.get('max_string_length'),
            'max_dict_depth': self.get('max_dict_depth'),
            'max_list_length': self.get('max_list_length'),
            'allowed_file_extensions': self.get('allowed_file_extensions'),
            'blocked_patterns': {
                'sql_injection': self.get('blocked_sql_patterns'),
                'script_injection': self.get('blocked_script_patterns'),
                'path_traversal': self.get('blocked_path_patterns'),
                'command_injection': self.get('blocked_command_patterns')
            }
        }


class SecurityKeyManager:
    """Manages security keys and secrets."""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    
    def get_secret_key(self) -> str:
        """Get the main secret key."""
        return self.secret_key
    
    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)
    
    def generate_user_id(self) -> str:
        """Generate a new user ID."""
        return secrets.token_urlsafe(16)
    
    def generate_session_token(self) -> str:
        """Generate a new session token."""
        return secrets.token_urlsafe(32)


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


class RateLimitExceededError(Exception):
    """Rate limit exceeded error."""
    pass


class InputValidationError(Exception):
    """Input validation error."""
    pass