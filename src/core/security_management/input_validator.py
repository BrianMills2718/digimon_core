"""
Input Validator

Handles comprehensive input validation and sanitization for security.
"""

import re
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .security_types import SecurityConfig, InputValidationError
from .audit_logger import AuditLogger
from .security_types import SecurityEvent, AuditAction


class InputValidator:
    """Comprehensive input validation with security checks."""
    
    def __init__(self, config: SecurityConfig, audit_logger: AuditLogger):
        self.config = config
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
    
    def validate_input(self, input_data: Dict[str, Any], 
                      validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        
        rules = self._merge_validation_rules(validation_rules)
        
        try:
            validation_result['sanitized_data'] = self._validate_and_sanitize(
                input_data, rules, validation_result
            )
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f'Validation error: {str(e)}')
            self.logger.error(f"Input validation failed: {e}")
        
        # Log security issues if found
        if validation_result['security_issues']:
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.SECURITY_VIOLATION,
                user_id=None,
                resource='input_validation',
                timestamp=datetime.now(),
                details={
                    'security_issues': validation_result['security_issues'],
                    'input_preview': str(input_data)[:100]
                },
                risk_level='high'
            ))
        
        return validation_result
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """
        Validate file path for security.
        
        Args:
            file_path: File path to validate
            
        Returns:
            Validation result
        """
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
            
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.SECURITY_VIOLATION,
                user_id=None,
                resource='file_path_validation',
                timestamp=datetime.now(),
                details={'path_traversal_attempt': file_path},
                risk_level='high'
            ))
        
        # Check for absolute paths in restricted contexts
        if file_path.startswith('/') and not file_path.startswith('/tmp/'):
            validation_result['warnings'].append('Absolute path detected')
        
        # Validate file extension
        _, ext = os.path.splitext(file_path)
        allowed_extensions = self.config.get('allowed_file_extensions')
        if ext and ext.lower() not in allowed_extensions:
            validation_result['warnings'].append(f'Potentially unsafe file extension: {ext}')
        
        # Check for null bytes
        if '\x00' in file_path:
            validation_result['errors'].append('Null byte in file path')
            validation_result['valid'] = False
        
        # Normalize path
        try:
            normalized_path = os.path.normpath(file_path)
            validation_result['sanitized_path'] = normalized_path
        except Exception as e:
            validation_result['errors'].append(f'Path normalization failed: {e}')
            validation_result['valid'] = False
        
        return validation_result
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize database query for injection protection.
        
        Args:
            query: Database query to sanitize
            
        Returns:
            Sanitized query
        """
        dangerous_patterns = self.config.get('blocked_sql_patterns')
        
        sanitized = query
        detected_patterns = []
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                detected_patterns.append(pattern)
                # Replace with safe placeholder
                sanitized = re.sub(pattern, '[BLOCKED_SQL]', sanitized, flags=re.IGNORECASE)
        
        # Log security violation if patterns detected
        if detected_patterns:
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.SECURITY_VIOLATION,
                user_id=None,
                resource='database_query',
                timestamp=datetime.now(),
                details={
                    'patterns_detected': detected_patterns,
                    'query_preview': query[:100]
                },
                risk_level='high'
            ))
        
        return sanitized
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        if not email or len(email) > 254:  # RFC 5321 limit
            return False
        
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        # Check for consecutive dots
        if '..' in email:
            return False
        
        # Check local part length (before @)
        local_part = email.split('@')[0]
        if len(local_part) > 64:  # RFC 5321 limit
            return False
        
        return True
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate URL for security.
        
        Args:
            url: URL to validate
            
        Returns:
            Validation result
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_url': url
        }
        
        # Basic URL pattern
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$'
        if not re.match(url_pattern, url):
            validation_result['errors'].append('Invalid URL format')
            validation_result['valid'] = False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'javascript:', r'data:', r'vbscript:', r'file://',
            r'ftp://', r'ldap://', r'gopher://'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                validation_result['errors'].append(f'Suspicious URL scheme: {pattern}')
                validation_result['valid'] = False
        
        # Check for IP addresses (often suspicious in URLs)
        ip_pattern = r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.match(ip_pattern, url):
            validation_result['warnings'].append('URL contains IP address instead of domain name')
        
        return validation_result
    
    def validate_json_input(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON input for security and structure.
        
        Args:
            json_data: JSON data to validate
            
        Returns:
            Validation result
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_data': {}
        }
        
        try:
            # Check depth
            max_depth = self.config.get('max_dict_depth')
            actual_depth = self._calculate_dict_depth(json_data)
            if actual_depth > max_depth:
                validation_result['errors'].append(f'JSON too deep: {actual_depth} > {max_depth}')
                validation_result['valid'] = False
            
            # Check size
            json_str = str(json_data)
            max_size = self.config.get('max_string_length')
            if len(json_str) > max_size:
                validation_result['errors'].append(f'JSON too large: {len(json_str)} > {max_size}')
                validation_result['valid'] = False
            
            # Sanitize the data
            validation_result['sanitized_data'] = self._sanitize_json_recursive(json_data, validation_result)
            
        except Exception as e:
            validation_result['errors'].append(f'JSON validation error: {e}')
            validation_result['valid'] = False
        
        return validation_result
    
    def _merge_validation_rules(self, custom_rules: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge custom validation rules with default rules."""
        default_rules = self.config.get_validation_rules()
        if custom_rules:
            # Deep merge rules
            merged_rules = default_rules.copy()
            merged_rules.update(custom_rules)
            return merged_rules
        return default_rules
    
    def _validate_and_sanitize(self, data: Any, rules: Dict[str, Any], 
                              result: Dict[str, Any], depth: int = 0) -> Any:
        """Recursively validate and sanitize data."""
        max_depth = rules['max_dict_depth']
        if depth > max_depth:
            result['errors'].append(f'Data structure too deep (max {max_depth})')
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
            max_length = rules['max_list_length']
            if len(data) > max_length:
                result['errors'].append(f'List too long (max {max_length})')
                result['valid'] = False
                return data[:max_length]
            
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
        if not isinstance(text, str):
            text = str(text)
        
        max_length = rules['max_string_length']
        if len(text) > max_length:
            result['warnings'].append(f'String truncated (max {max_length})')
            text = text[:max_length]
        
        # Check for security patterns
        blocked_patterns = rules['blocked_patterns']
        for pattern_type, patterns in blocked_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    result['security_issues'].append(f'{pattern_type} pattern detected: {pattern}')
                    result['valid'] = False
                    # Replace with safe placeholder
                    text = re.sub(pattern, '[BLOCKED]', text, flags=re.IGNORECASE)
        
        # Basic XSS protection
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text
    
    def _calculate_dict_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of nested dictionaries."""
        if not isinstance(data, dict):
            return current_depth
        
        if not data:  # Empty dict
            return current_depth + 1
        
        max_depth = current_depth + 1
        for value in data.values():
            if isinstance(value, dict):
                depth = self._calculate_dict_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        depth = self._calculate_dict_depth(item, current_depth + 1)
                        max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _sanitize_json_recursive(self, data: Any, result: Dict[str, Any]) -> Any:
        """Recursively sanitize JSON data."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Ensure key is safe
                safe_key = str(key).replace('\x00', '')[:100]  # Limit key length
                sanitized[safe_key] = self._sanitize_json_recursive(value, result)
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_json_recursive(item, result) for item in data]
        
        elif isinstance(data, str):
            # Basic string sanitization
            sanitized = data.replace('\x00', '')  # Remove null bytes
            if len(sanitized) > 10000:  # Limit string length
                result['warnings'].append('Large string truncated in JSON')
                sanitized = sanitized[:10000]
            return sanitized
        
        elif isinstance(data, (int, float, bool)) or data is None:
            return data
        
        else:
            result['warnings'].append(f'Unexpected JSON data type: {type(data)}')
            return str(data)