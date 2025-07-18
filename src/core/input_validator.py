import re
import html
import logging
from typing import Any, Dict, List, Union, Optional
from pathlib import Path

class InputValidator:
    """Security-focused input validation and sanitization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced SQL injection patterns with more sophisticated detection
        self.sql_injection_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|truncate|exec|execute)\b)",
            r"(--|/\*|\*/|;|\bxp_)",
            r"(\b(or|and)\s+\d+\s*=\s*\d+)",
            r"(\b(information_schema|sys\.|sysobjects|syscolumns)\b)",
            r"(\bcast\s*\(.*\bas\b)",
            r"(\bhex\s*\(|\bascii\s*\(|\bchar\s*\()",
            r"(\bwaitfor\s+delay\b|\bwaitfor\s+time\b)",
            r"(\binto\s+(out|dump)file\b)",
            r"('[^']*'\s*or\s*'[^']*'='[^']*')",  # Classic SQL injection pattern
            r"(\'\s*or\s*\')",  # Simple quote-based OR injection
        ]
        
        # Enhanced Cypher injection patterns - focus on dangerous combinations
        self.cypher_injection_patterns = [
            r"(\b(or|and)\s+\d+\s*=\s*\d+)",  # Boolean injection
            r"(\bdrop\s+(constraint|index|database)\b)",  # Drop operations
            r"(;\s*(match|create|merge|delete|call))",  # Query chaining
            r"(\bload\s+csv\s+from\s+[\"']http)",  # Remote CSV loading
            r"(\bcall\s+apoc\.|dbms\.|algo\.)",  # Dangerous procedure calls
            r"(\bforeach\s*\(.*\|\s*delete\b)",  # Bulk delete operations
            r"(\bdetach\s+delete\s+n\s*;\s*match)",  # Delete all + query
        ]
        
        # Enhanced path traversal patterns
        self.path_traversal_patterns = [
            r"(\.\./|\.\.\\|\.\.%2f|\.\.%5c)",
            r"(/etc/|/var/|/home/|/root/|/usr/|/proc/|/sys/|C:\\|%windir%)",
            r"(~[/\\]|%userprofile%)",
            r"(\\\\\?\\|\\\\\.\\)",
            r"(file://|ftp://|http://|https://)",
        ]
        
        # Parameterized query enforcement patterns
        self.non_parameterized_patterns = [
            r"(query\s*=\s*[\"'].*\+.*[\"'])",  # String concatenation in queries
            r"(f[\"'].*\{.*\}.*[\"'])",  # F-string usage in queries
            r"(\.format\s*\()",  # .format() usage
            r"(%s|%d|%f)",  # % formatting
            r"([\"'].*\+.*[\"'])",  # Direct string concatenation
            r"([\"'][^\"']*\"\s*\+\s*[\"'][^\"']*[\"'])",  # String concatenation pattern
        ]
    
    def validate_file_path(self, file_path: str, allowed_extensions: List[str] = None) -> Dict[str, Any]:
        """Validate and sanitize file paths"""
        validation_result = {
            'is_valid': True,
            'sanitized_path': file_path,
            'errors': []
        }
        
        try:
            # Check for path traversal attempts
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Path traversal attempt detected: {pattern}")
            
            # Normalize the path
            path_obj = Path(file_path).resolve()
            validation_result['sanitized_path'] = str(path_obj)
            
            # Check if file exists and is accessible
            if not path_obj.exists():
                validation_result['is_valid'] = False
                validation_result['errors'].append("File does not exist")
            
            # Check file extension if restrictions are specified
            if allowed_extensions:
                if path_obj.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"File extension not allowed. Allowed: {allowed_extensions}")
            
            # Check file size (prevent DoS)
            if path_obj.exists():
                file_size = path_obj.stat().st_size
                max_size = 100 * 1024 * 1024  # 100MB limit
                if file_size > max_size:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"File too large: {file_size} bytes (max: {max_size})")
        
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Path validation error: {str(e)}")
        
        return validation_result
    
    def validate_text_input(self, text: str, max_length: int = 10000) -> Dict[str, Any]:
        """Validate and sanitize text input"""
        validation_result = {
            'is_valid': True,
            'sanitized_text': text,
            'errors': []
        }
        
        # Check length
        if len(text) > max_length:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Text too long: {len(text)} characters (max: {max_length})")
        
        # Check for injection attempts
        for pattern in self.sql_injection_patterns + self.cypher_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Potential injection attempt detected")
                break
        
        # Sanitize HTML if present
        if '<' in text and '>' in text:
            validation_result['sanitized_text'] = html.escape(text)
        
        return validation_result
    
    def validate_neo4j_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters for Neo4j queries"""
        validation_result = {
            'is_valid': True,
            'sanitized_params': {},
            'errors': []
        }
        
        for key, value in params.items():
            # Validate key names (no special characters)
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Invalid parameter name: {key}")
                continue
            
            # Validate and sanitize values
            if isinstance(value, str):
                text_validation = self.validate_text_input(value)
                if not text_validation['is_valid']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].extend(text_validation['errors'])
                else:
                    validation_result['sanitized_params'][key] = text_validation['sanitized_text']
            else:
                validation_result['sanitized_params'][key] = value
        
        return validation_result
    
    def validate_parameterized_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that queries use parameterized format and detect injection attempts"""
        validation_result = {
            'is_valid': True,
            'sanitized_query': query,
            'sanitized_params': {},
            'errors': [],
            'warnings': []
        }
        
        # Check for non-parameterized patterns in the query
        for pattern in self.non_parameterized_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Non-parameterized query detected: avoid string concatenation, use parameters instead")
                break
        
        # Enhanced injection detection in query
        for pattern in self.sql_injection_patterns + self.cypher_injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                validation_result['warnings'].append(f"Potential injection pattern detected in query: {pattern}")
                self.logger.warning(f"Query contains potentially dangerous pattern: {pattern}")
        
        # Validate parameters
        param_validation = self.validate_neo4j_params(params)
        if not param_validation['is_valid']:
            validation_result['is_valid'] = False
            validation_result['errors'].extend(param_validation['errors'])
        else:
            validation_result['sanitized_params'] = param_validation['sanitized_params']
        
        # Check for parameter placeholders in query
        expected_params = set(re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', query))
        provided_params = set(params.keys())
        
        missing_params = expected_params - provided_params
        extra_params = provided_params - expected_params
        
        if missing_params:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Missing parameters: {missing_params}")
        
        if extra_params:
            validation_result['warnings'].append(f"Extra parameters provided: {extra_params}")
        
        # Check for hardcoded queries (queries without parameters)
        if not expected_params and not provided_params:
            # Check if this looks like a static query that should use parameters
            if re.search(r"(where|set|values).*[\"'][^\"']*[\"']", query, re.IGNORECASE):
                validation_result['warnings'].append("Query contains hardcoded values - consider using parameters")
        
        return validation_result
    
    def validate_cypher_query_safe(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Specifically validate Cypher queries for Neo4j with enhanced security"""
        validation_result = self.validate_parameterized_query(query, params)
        
        # Additional Cypher-specific validations
        dangerous_cypher_patterns = [
            r"(\bapoc\.|dbms\.|algo\.)",  # Procedure calls that might be dangerous
            r"(\bload\s+csv\s+from\s+[\"'](?!file:///)[\"'])",  # External CSV loading
            r"(\bcall\s+\{)",  # Dynamic procedure calls
            r"(\bforeach\s*\(.*\|\s*create\b)",  # Bulk operations
        ]
        
        for pattern in dangerous_cypher_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Dangerous Cypher pattern detected: {pattern}")
                self.logger.error(f"Dangerous Cypher pattern blocked: {pattern}")
        
        # Validate query structure for basic safety
        if not re.search(r'^\s*(MATCH|CREATE|MERGE|RETURN|WITH|CALL)\b', query, re.IGNORECASE):
            validation_result['warnings'].append("Query should start with a valid Cypher clause")
        
        return validation_result
    
    def enforce_parameterized_execution(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce that only parameterized queries are executed"""
        validation_result = self.validate_cypher_query_safe(query, params)
        
        if not validation_result['is_valid']:
            raise ValueError(f"Query validation failed: {validation_result['errors']}")
        
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                self.logger.warning(f"Query validation warning: {warning}")
        
        return {
            'query': validation_result['sanitized_query'],
            'params': validation_result['sanitized_params']
        }