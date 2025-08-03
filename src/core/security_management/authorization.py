"""
Authorization Management

Handles authorization, permissions, JWT tokens, and API keys.
"""

import jwt
import logging
from typing import Dict, Any, Optional, Set, List
from datetime import datetime, timedelta

from .security_types import (
    SecurityEvent, AuditAction, SecurityConfig, SecurityKeyManager,
    SecurityValidationError, AuthorizationError
)
from .authentication import AuthenticationManager
from .audit_logger import AuditLogger


class AuthorizationManager:
    """Manages user authorization, permissions, and access tokens."""
    
    def __init__(self, config: SecurityConfig, key_manager: SecurityKeyManager,
                 auth_manager: AuthenticationManager, audit_logger: AuditLogger):
        self.config = config
        self.key_manager = key_manager
        self.auth_manager = auth_manager
        self.audit_logger = audit_logger
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    def generate_jwt_token(self, user_id: str, expires_in: Optional[int] = None) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user_id: User ID
            expires_in: Token expiration time in seconds
            
        Returns:
            JWT token string
        """
        user = self.auth_manager.get_user(user_id)
        if not user:
            raise SecurityValidationError("User not found")
        
        expires_in = expires_in or self.config.get('jwt_expiration')
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
        
        token = jwt.encode(payload, self.key_manager.get_secret_key(), algorithm='HS256')
        
        self.audit_logger.log_event(SecurityEvent(
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
            payload = jwt.decode(token, self.key_manager.get_secret_key(), algorithms=['HS256'])
            
            # Check if user still exists and is active
            user_id = payload.get('user_id')
            if user_id:
                user = self.auth_manager.get_user(user_id)
                if user and user.is_active:
                    return payload
            
            return None
            
        except jwt.ExpiredSignatureError:
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="jwt_token",
                timestamp=datetime.now(),
                details={'reason': 'token_expired'},
                risk_level="low"
            ))
            return None
        except jwt.InvalidTokenError:
            self.audit_logger.log_event(SecurityEvent(
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
        user = self.auth_manager.get_user(user_id)
        if not user or not user.is_active:
            return False
        
        has_permission = permission in user.permissions
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.ACCESS_GRANTED if has_permission else AuditAction.ACCESS_DENIED,
            user_id=user_id,
            resource=f"permission:{permission}",
            timestamp=datetime.now(),
            details={'permission': permission, 'granted': has_permission}
        ))
        
        return has_permission
    
    def check_role(self, user_id: str, role: str) -> bool:
        """
        Check if user has specific role.
        
        Args:
            user_id: User ID
            role: Role string
            
        Returns:
            True if user has role, False otherwise
        """
        user = self.auth_manager.get_user(user_id)
        if not user or not user.is_active:
            return False
        
        has_role = role in user.roles
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.ACCESS_GRANTED if has_role else AuditAction.ACCESS_DENIED,
            user_id=user_id,
            resource=f"role:{role}",
            timestamp=datetime.now(),
            details={'role': role, 'granted': has_role}
        ))
        
        return has_role
    
    def add_user_permission(self, user_id: str, permission: str) -> bool:
        """Add permission to user."""
        user = self.auth_manager.get_user(user_id)
        if not user:
            return False
        
        user.permissions.add(permission)
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_permissions",
            timestamp=datetime.now(),
            details={'action': 'permission_added', 'permission': permission}
        ))
        
        return True
    
    def remove_user_permission(self, user_id: str, permission: str) -> bool:
        """Remove permission from user."""
        user = self.auth_manager.get_user(user_id)
        if not user:
            return False
        
        user.permissions.discard(permission)
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_permissions",
            timestamp=datetime.now(),
            details={'action': 'permission_removed', 'permission': permission}
        ))
        
        return True
    
    def add_user_role(self, user_id: str, role: str) -> bool:
        """Add role to user."""
        user = self.auth_manager.get_user(user_id)
        if not user:
            return False
        
        user.roles.add(role)
        # Update permissions based on new role
        user.permissions.update(self.auth_manager._get_default_permissions({role}))
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_roles",
            timestamp=datetime.now(),
            details={'action': 'role_added', 'role': role}
        ))
        
        return True
    
    def remove_user_role(self, user_id: str, role: str) -> bool:
        """Remove role from user."""
        user = self.auth_manager.get_user(user_id)
        if not user:
            return False
        
        user.roles.discard(role)
        # Recalculate permissions based on remaining roles
        user.permissions = self.auth_manager._get_default_permissions(user.roles)
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=user_id,
            resource="user_roles",
            timestamp=datetime.now(),
            details={'action': 'role_removed', 'role': role}
        ))
        
        return True
    
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
        user = self.auth_manager.get_user(user_id)
        if not user:
            raise SecurityValidationError("User not found")
        
        api_key = self.key_manager.generate_api_key()
        
        self.api_keys[api_key] = {
            'user_id': user_id,
            'name': name,
            'permissions': permissions,
            'created_at': datetime.now(),
            'last_used': None,
            'is_active': True
        }
        
        self.audit_logger.log_event(SecurityEvent(
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
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="api_key",
                timestamp=datetime.now(),
                details={'reason': 'api_key_not_found'},
                risk_level="medium"
            ))
            return None
        
        key_info = self.api_keys[api_key]
        
        if not key_info['is_active']:
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=key_info['user_id'],
                resource="api_key",
                timestamp=datetime.now(),
                details={'reason': 'api_key_inactive'},
                risk_level="medium"
            ))
            return None
        
        # Check if user is still active
        user = self.auth_manager.get_user(key_info['user_id'])
        if not user or not user.is_active:
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=key_info['user_id'],
                resource="api_key",
                timestamp=datetime.now(),
                details={'reason': 'user_inactive'},
                risk_level="medium"
            ))
            return None
        
        # Update last used timestamp
        key_info['last_used'] = datetime.now()
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.ACCESS_GRANTED,
            user_id=key_info['user_id'],
            resource="api_key",
            timestamp=datetime.now(),
            details={'name': key_info['name']}
        ))
        
        return key_info
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key."""
        if api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        key_info['is_active'] = False
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.DATA_MODIFICATION,
            user_id=key_info['user_id'],
            resource="api_key",
            timestamp=datetime.now(),
            details={'action': 'api_key_revoked', 'name': key_info['name']}
        ))
        
        return True
    
    def list_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List API keys for user."""
        user_keys = []
        for api_key, key_info in self.api_keys.items():
            if key_info['user_id'] == user_id:
                # Return safe information (without the actual key)
                safe_info = {
                    'name': key_info['name'],
                    'permissions': list(key_info['permissions']),
                    'created_at': key_info['created_at'].isoformat(),
                    'last_used': key_info['last_used'].isoformat() if key_info['last_used'] else None,
                    'is_active': key_info['is_active'],
                    'key_preview': api_key[:8] + '...'  # First 8 chars only
                }
                user_keys.append(safe_info)
        
        return user_keys
    
    def check_api_key_permission(self, api_key: str, permission: str) -> bool:
        """Check if API key has specific permission."""
        key_info = self.verify_api_key(api_key)
        if not key_info:
            return False
        
        has_permission = permission in key_info['permissions']
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.ACCESS_GRANTED if has_permission else AuditAction.ACCESS_DENIED,
            user_id=key_info['user_id'],
            resource=f"api_key_permission:{permission}",
            timestamp=datetime.now(),
            details={'permission': permission, 'granted': has_permission, 'api_key_name': key_info['name']}
        ))
        
        return has_permission
    
    def get_authorization_statistics(self) -> Dict[str, Any]:
        """Get authorization statistics."""
        total_api_keys = len(self.api_keys)
        active_api_keys = len([k for k in self.api_keys.values() if k['is_active']])
        
        return {
            'total_api_keys': total_api_keys,
            'active_api_keys': active_api_keys,
            'inactive_api_keys': total_api_keys - active_api_keys,
            'users_with_api_keys': len(set(k['user_id'] for k in self.api_keys.values()))
        }