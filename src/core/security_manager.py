"""
Security Manager for Production Environment

Unified security manager using decomposed components for comprehensive security features
including authentication, authorization, data protection, and security auditing.
"""

import logging
from typing import Dict, Any, Optional, Set, List
from datetime import datetime

from .security_management import (
    SecurityConfig,
    SecurityKeyManager,
    AuthenticationManager,
    AuthorizationManager,
    AuditLogger,
    InputValidator,
    RateLimiter,
    EncryptionManager,
    SecurityDecorators,
    SecurityLevel,
    AuditAction,
    SecurityEvent,
    User,
    SecurityValidationError,
    AuthenticationError,
    AuthorizationError,
    set_global_security_manager
)


class SecurityManager:
    """
    Production-grade security manager with comprehensive security features.
    
    Provides authentication, authorization, encryption, and audit logging
    through decomposed, focused components.
    """
    
    def __init__(self, secret_key: Optional[str] = None, custom_config: Optional[Dict[str, Any]] = None):
        """
        Initialize security manager with all components.
        
        Args:
            secret_key: Secret key for JWT tokens and encryption
            custom_config: Custom security configuration
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.config = SecurityConfig(custom_config)
        self.key_manager = SecurityKeyManager(secret_key)
        self.audit_logger = AuditLogger(self.config)
        self.input_validator = InputValidator(self.config, self.audit_logger)
        self.rate_limiter = RateLimiter(self.config, self.audit_logger)
        self.encryption = EncryptionManager(self.config, self.key_manager)
        
        # Initialize authentication and authorization
        self.authentication = AuthenticationManager(self.config, self.key_manager, self.audit_logger)
        self.authorization = AuthorizationManager(self.config, self.key_manager, self.authentication, self.audit_logger)
        
        # Initialize decorators
        self.decorators = SecurityDecorators(self)
        
        # Set global security manager for decorator functions
        set_global_security_manager(self)
        
        self.logger.info("SecurityManager initialized with all components")
    
    # Authentication Methods (delegated to AuthenticationManager)
    def create_user(self, username: str, email: str, password: str, 
                   roles: Optional[Set[str]] = None) -> str:
        """Create a new user with security validations."""
        return self.authentication.create_user(username, email, password, roles)
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: Optional[str] = None) -> Optional[str]:
        """Authenticate user credentials."""
        return self.authentication.authenticate_user(username, password, ip_address)
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password with validation."""
        return self.authentication.change_password(user_id, old_password, new_password)
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user password (admin function)."""
        return self.authentication.reset_password(user_id, new_password)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.authentication.get_user(user_id)
    
    def activate_user(self, user_id: str) -> bool:
        """Activate user account."""
        return self.authentication.activate_user(user_id)
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account."""
        return self.authentication.deactivate_user(user_id)
    
    def unlock_user(self, user_id: str) -> bool:
        """Unlock user account."""
        return self.authentication.unlock_user(user_id)
    
    # Authorization Methods (delegated to AuthorizationManager)
    def generate_jwt_token(self, user_id: str, expires_in: Optional[int] = None) -> str:
        """Generate JWT token for authenticated user."""
        return self.authorization.generate_jwt_token(user_id, expires_in)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        return self.authorization.verify_jwt_token(token)
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        return self.authorization.check_permission(user_id, permission)
    
    def check_role(self, user_id: str, role: str) -> bool:
        """Check if user has specific role."""
        return self.authorization.check_role(user_id, role)
    
    def add_user_permission(self, user_id: str, permission: str) -> bool:
        """Add permission to user."""
        return self.authorization.add_user_permission(user_id, permission)
    
    def remove_user_permission(self, user_id: str, permission: str) -> bool:
        """Remove permission from user."""
        return self.authorization.remove_user_permission(user_id, permission)
    
    def add_user_role(self, user_id: str, role: str) -> bool:
        """Add role to user."""
        return self.authorization.add_user_role(user_id, role)
    
    def remove_user_role(self, user_id: str, role: str) -> bool:
        """Remove role from user."""
        return self.authorization.remove_user_role(user_id, role)
    
    def generate_api_key(self, user_id: str, name: str, permissions: Set[str]) -> str:
        """Generate API key for user."""
        return self.authorization.generate_api_key(user_id, name, permissions)
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return information."""
        return self.authorization.verify_api_key(api_key)
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key."""
        return self.authorization.revoke_api_key(api_key)
    
    # Encryption Methods (delegated to EncryptionManager)
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.encryption.encrypt_sensitive_data(data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.encryption.decrypt_sensitive_data(encrypted_data)
    
    def encrypt_dict(self, data_dict: Dict[str, Any], 
                    sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Encrypt sensitive fields in a dictionary."""
        return self.encryption.encrypt_dict(data_dict, sensitive_fields)
    
    def decrypt_dict(self, encrypted_dict: Dict[str, Any],
                    sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Decrypt sensitive fields in a dictionary."""
        return self.encryption.decrypt_dict(encrypted_dict, sensitive_fields)
    
    # Input Validation Methods (delegated to InputValidator)
    def validate_input(self, input_data: Dict[str, Any], 
                      validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive input validation with security checks."""
        return self.input_validator.validate_input(input_data, validation_rules)
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """Validate file path for security."""
        return self.input_validator.validate_file_path(file_path)
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize database query for injection protection."""
        return self.input_validator.sanitize_query(query)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        return self.input_validator.validate_email(email)
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL for security."""
        return self.input_validator.validate_url(url)
    
    # Rate Limiting Methods (delegated to RateLimiter)
    def rate_limit_check(self, identifier: str, requests_per_window: Optional[int] = None) -> bool:
        """Check rate limiting for identifier."""
        return self.rate_limiter.check_rate_limit(identifier, requests_per_window)
    
    def block_ip(self, ip_address: str, duration_hours: int = 24, reason: str = "manual_block") -> bool:
        """Block IP address for specified duration."""
        return self.rate_limiter.block_ip(ip_address, duration_hours, reason)
    
    def unblock_ip(self, ip_address: str, reason: str = "manual_unblock") -> bool:
        """Unblock IP address."""
        return self.rate_limiter.unblock_ip(ip_address, reason)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        return self.rate_limiter.is_ip_blocked(ip_address)
    
    # Audit and Reporting Methods (delegated to AuditLogger)
    def get_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        return self.audit_logger.generate_security_report(hours)
    
    def get_recent_events(self, hours: int = 24, limit: int = 100) -> List[SecurityEvent]:
        """Get recent security events."""
        return self.audit_logger.get_recent_events(hours, limit)
    
    def get_failed_login_attempts(self, hours: int = 24) -> List[SecurityEvent]:
        """Get failed login attempts in the specified time period."""
        return self.audit_logger.get_failed_login_attempts(hours)
    
    def get_security_violations(self, hours: int = 24) -> List[SecurityEvent]:
        """Get security violations in the specified time period."""
        return self.audit_logger.get_security_violations(hours)
    
    def export_events_for_compliance(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Export events for compliance reporting."""
        return self.audit_logger.export_events_for_compliance(start_date, end_date)
    
    # Comprehensive Security Status
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status across all components."""
        return {
            'timestamp': self.audit_logger.get_recent_events(1, 1)[0].timestamp.isoformat() if self.audit_logger.get_recent_events(1, 1) else None,
            'authentication': self.authentication.get_authentication_statistics(),
            'authorization': self.authorization.get_authorization_statistics(),
            'audit': self.audit_logger.get_audit_statistics(),
            'rate_limiting': self.rate_limiter.get_rate_limit_statistics(),
            'encryption': self.encryption.get_encryption_info(),
            'security_config': {
                'password_policy': {
                    'min_length': self.config.get('password_min_length'),
                    'require_special': self.config.get('password_require_special'),
                    'require_numbers': self.config.get('password_require_numbers'),
                    'require_uppercase': self.config.get('password_require_uppercase')
                },
                'rate_limits': {
                    'requests_per_window': self.config.get('rate_limit_requests'),
                    'window_seconds': self.config.get('rate_limit_window')
                },
                'audit_retention_days': self.config.get('audit_retention_days')
            }
        }
    
    # Cleanup and Maintenance
    def perform_security_maintenance(self) -> Dict[str, Any]:
        """Perform security maintenance tasks."""
        maintenance_results = {
            'timestamp': datetime.now().isoformat(),
            'tasks_performed': [],
            'issues_found': [],
            'recommendations': []
        }
        
        try:
            # Clean up expired IP blocks
            expired_blocks = self.rate_limiter.cleanup_expired_blocks()
            if expired_blocks > 0:
                maintenance_results['tasks_performed'].append(f"Removed {expired_blocks} expired IP blocks")
            
            # Generate security report for analysis
            security_report = self.get_security_report(24)
            if security_report['security_recommendations']:
                maintenance_results['recommendations'].extend(security_report['security_recommendations'])
            
            # Check for high-risk events
            high_risk_events = len([e for e in self.get_recent_events(24, 1000) if e.risk_level == "high"])
            if high_risk_events > 10:
                maintenance_results['issues_found'].append(f"High number of high-risk events: {high_risk_events}")
            
            maintenance_results['tasks_performed'].append("Security maintenance completed successfully")
            
        except Exception as e:
            maintenance_results['issues_found'].append(f"Maintenance task failed: {e}")
            self.logger.error(f"Security maintenance failed: {e}")
        
        return maintenance_results


# Global security manager instance
security_manager = SecurityManager()

# Export types for backward compatibility
SecurityValidationError = SecurityValidationError
AuthenticationError = AuthenticationError  
AuthorizationError = AuthorizationError