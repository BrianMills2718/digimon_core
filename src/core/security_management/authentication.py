"""
Authentication Management

Handles user authentication, password management, and session control.
"""

import re
import bcrypt
import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta

from .security_types import (
    User, SecurityEvent, AuditAction, SecurityConfig, SecurityKeyManager,
    SecurityValidationError, AuthenticationError
)
from .audit_logger import AuditLogger


class AuthenticationManager:
    """Manages user authentication and password security."""
    
    def __init__(self, config: SecurityConfig, key_manager: SecurityKeyManager, 
                 audit_logger: AuditLogger):
        self.config = config
        self.key_manager = key_manager
        self.audit_logger = audit_logger
        self.users: Dict[str, User] = {}
        self.logger = logging.getLogger(__name__)
    
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
        user_id = self.key_manager.generate_user_id()
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
        self.audit_logger.log_event(SecurityEvent(
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
        # Find user by username or email
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            self.audit_logger.log_event(SecurityEvent(
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
            self.audit_logger.log_event(SecurityEvent(
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
            self.audit_logger.log_event(SecurityEvent(
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
            max_attempts = self.config.get('max_failed_login_attempts')
            if user.failed_login_attempts >= max_attempts:
                lockout_duration = self.config.get('account_lockout_duration')
                user.locked_until = datetime.now() + timedelta(seconds=lockout_duration)
                
                self.audit_logger.log_event(SecurityEvent(
                    action=AuditAction.SECURITY_VIOLATION,
                    user_id=user.user_id,
                    resource="authentication",
                    timestamp=datetime.now(),
                    ip_address=ip_address,
                    details={'reason': 'account_locked_failed_attempts'},
                    risk_level="high"
                ))
            
            self.audit_logger.log_event(SecurityEvent(
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
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.LOGIN,
            user_id=user.user_id,
            resource="authentication",
            timestamp=datetime.now(),
            ip_address=ip_address,
            details={'username': user.username}
        ))
        
        return user.user_id
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password with validation.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            SecurityValidationError: If validation fails
        """
        user = self.users.get(user_id)
        if not user:
            raise SecurityValidationError("User not found")
        
        # Verify old password
        if not self._verify_password(old_password, user.password_hash):
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=user_id,
                resource="password_change",
                timestamp=datetime.now(),
                details={'reason': 'invalid_old_password'},
                risk_level="medium"
            ))
            raise AuthenticationError("Invalid current password")
        
        # Validate new password strength
        if not self._validate_password_strength(new_password):
            raise SecurityValidationError("New password does not meet security requirements")
        
        # Update password
        user.password_hash = self._hash_password(new_password)
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="password_change",
            timestamp=datetime.now(),
            details={'action': 'password_changed'}
        ))
        
        return True
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """
        Reset user password (admin function).
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            True if password reset successfully
        """
        user = self.users.get(user_id)
        if not user:
            raise SecurityValidationError("User not found")
        
        # Validate new password strength
        if not self._validate_password_strength(new_password):
            raise SecurityValidationError("Password does not meet security requirements")
        
        # Update password and unlock account
        user.password_hash = self._hash_password(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="password_reset",
            timestamp=datetime.now(),
            details={'action': 'password_reset_by_admin'}
        ))
        
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def activate_user(self, user_id: str) -> bool:
        """Activate user account."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.is_active = True
        user.failed_login_attempts = 0
        user.locked_until = None
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_activation",
            timestamp=datetime.now(),
            details={'action': 'user_activated'}
        ))
        
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.is_active = False
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_deactivation",
            timestamp=datetime.now(),
            details={'action': 'user_deactivated'}
        ))
        
        return True
    
    def unlock_user(self, user_id: str) -> bool:
        """Unlock user account."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.failed_login_attempts = 0
        user.locked_until = None
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_unlock",
            timestamp=datetime.now(),
            details={'action': 'user_unlocked'}
        ))
        
        return True
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength according to security policy."""
        min_length = self.config.get('password_min_length')
        if len(password) < min_length:
            return False
        
        if self.config.get('password_require_uppercase') and not re.search(r'[A-Z]', password):
            return False
        
        if self.config.get('password_require_numbers') and not re.search(r'\d', password):
            return False
        
        if self.config.get('password_require_special') and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
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
    
    def get_authentication_statistics(self) -> Dict[str, Any]:
        """Get authentication statistics."""
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.is_active])
        locked_users = len([u for u in self.users.values() 
                           if u.locked_until and u.locked_until > datetime.now()])
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'locked_users': locked_users,
            'users_with_failed_attempts': len([u for u in self.users.values() 
                                             if u.failed_login_attempts > 0])
        }