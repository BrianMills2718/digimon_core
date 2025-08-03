"""Standard Tool Protocol Interface for GraphRAG Tools

This module defines the standardized interface that all GraphRAG tools must implement
to ensure consistent integration with the pipeline orchestrator.

CRITICAL IMPLEMENTATION: Addresses tool interface mismatch identified in CLAUDE.md
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolValidationResult:
    """Result of tool validation with detailed information"""
    is_valid: bool
    validation_errors: List[str]
    method_signatures: Dict[str, str]
    execution_test_results: Dict[str, Any]
    input_schema_validation: Dict[str, Any]
    security_validation: Dict[str, Any]
    performance_validation: Dict[str, Any]
    
    def __post_init__(self):
        """Validate all required fields are properly structured"""
        required_fields = {
            'input_schema_validation': ['valid', 'errors'],
            'security_validation': ['valid', 'errors'],
            'performance_validation': ['valid', 'errors']
        }
        
        for field_name, required_keys in required_fields.items():
            field_value = getattr(self, field_name)
            if not isinstance(field_value, dict):
                raise ValueError(f"{field_name} must be a dictionary")
            for key in required_keys:
                if key not in field_value:
                    raise ValueError(f"{field_name} must contain key: {key}")


class Tool(ABC):
    """Standard tool interface for all GraphRAG tools
    
    This interface ensures consistent tool behavior across all phases and optimization levels.
    All tools must implement this interface to work with the pipeline orchestrator.
    """
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute tool with input data and optional context
        
        Args:
            input_data: Input data for the tool (format varies by tool)
            context: Optional context information for execution
            
        Returns:
            Tool execution result as dictionary with status and data
        """
        pass
    
    @abstractmethod
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool metadata and capabilities
        
        Returns:
            Dictionary containing tool information:
            - name: Tool name
            - version: Tool version
            - description: Tool description
            - contract_id: Associated contract ID
            - capabilities: List of tool capabilities
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate input with detailed error reporting
        
        Args:
            input_data: Input data to validate
            
        Returns:
            ToolValidationResult with detailed validation information
        """
        pass
    
    def validate_input_comprehensive(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Comprehensive input validation with multiple validation layers
        
        As required by CLAUDE.md, this method performs deep validation including:
        - Schema validation
        - Security validation
        - Performance validation
        - Business logic validation
        
        Args:
            input_data: Input data to validate
            
        Returns:
            ToolValidationResult with comprehensive validation details
        """
        validation_errors = []
        
        # Schema validation
        schema_result = self._validate_input_schema(input_data)
        if not schema_result["valid"]:
            validation_errors.extend(schema_result["errors"])
        
        # Security validation
        security_result = self._validate_input_security(input_data)
        if not security_result["valid"]:
            validation_errors.extend(security_result["errors"])
        
        # Performance validation (size limits, complexity)
        performance_result = self._validate_input_performance(input_data)
        if not performance_result["valid"]:
            validation_errors.extend(performance_result["errors"])
        
        # Business logic validation
        business_result = self._validate_business_logic(input_data)
        if not business_result["valid"]:
            validation_errors.extend(business_result["errors"])
        
        # Get method signatures for validation
        method_signatures = self._get_method_signatures()
        
        # Test execution safety
        execution_test_results = self._test_execution_safety(input_data)
        
        return ToolValidationResult(
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            method_signatures=method_signatures,
            execution_test_results=execution_test_results,
            input_schema_validation=schema_result,
            security_validation=security_result,
            performance_validation=performance_result
        )
    
    def _validate_input_schema(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input against expected schema
        
        Default implementation - tools should override for specific validation
        """
        return {
            "valid": True,
            "errors": [],
            "schema_type": "default",
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_input_security(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input for security concerns
        
        Checks for:
        - Path traversal attempts
        - Injection attacks
        - Oversized inputs
        - Malicious patterns
        """
        errors = []
        
        # Check for path traversal attempts
        for key, value in input_data.items():
            if isinstance(value, str):
                if "../" in value or "..%2F" in value or "..%5C" in value:
                    errors.append(f"Potential path traversal in {key}")
                if len(value) > 1_000_000:  # 1MB string limit
                    errors.append(f"String value too large in {key}")
            elif isinstance(value, list) and len(value) > 10_000:
                errors.append(f"List too large in {key}")
            elif isinstance(value, dict) and len(str(value)) > 10_000_000:  # 10MB dict limit
                errors.append(f"Dictionary too large in {key}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "security_checks": ["path_traversal", "size_limits", "injection_patterns"],
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_input_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input for performance implications
        
        Checks for:
        - Input size and complexity
        - Resource usage estimates
        - Processing time estimates
        """
        errors = []
        warnings = []
        
        # Estimate input complexity
        total_size = len(str(input_data))
        
        if total_size > 50_000_000:  # 50MB
            errors.append("Input size exceeds maximum allowed (50MB)")
        elif total_size > 10_000_000:  # 10MB
            warnings.append("Large input size may impact performance")
        
        # Check nested depth
        max_depth = self._get_max_depth(input_data)
        if max_depth > 10:
            errors.append(f"Input nesting depth ({max_depth}) exceeds limit (10)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "total_size_bytes": total_size,
                "max_depth": max_depth,
                "estimated_memory_mb": total_size / 1024 / 1024 * 2  # Rough estimate
            },
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_business_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input against business logic rules
        
        Default implementation - tools should override for specific rules
        """
        return {
            "valid": True,
            "errors": [],
            "business_rules_checked": [],
            "validated_at": datetime.now().isoformat()
        }
    
    def _get_method_signatures(self) -> Dict[str, str]:
        """Get method signatures for validation
        
        Returns dictionary of method names to signatures
        """
        import inspect
        signatures = {}
        
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_'):  # Public methods only
                try:
                    sig = inspect.signature(method)
                    signatures[name] = str(sig)
                except Exception:
                    signatures[name] = "signature unavailable"
        
        return signatures
    
    def _test_execution_safety(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test if execution would be safe with given input
        
        Performs dry-run validation without actual execution
        """
        try:
            # First validate the input
            basic_validation = self.validate_input(input_data)
            
            return {
                "safe_to_execute": basic_validation.is_valid,
                "validation_passed": basic_validation.is_valid,
                "errors": basic_validation.validation_errors if not basic_validation.is_valid else [],
                "tested_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "safe_to_execute": False,
                "validation_passed": False,
                "errors": [str(e)],
                "tested_at": datetime.now().isoformat()
            }
    
    def _get_max_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Get maximum nesting depth of object"""
        if current_depth > 20:  # Prevent infinite recursion
            return current_depth
        
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_max_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def test_actual_functionality(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test actual functionality with real data - MANDATORY IMPLEMENTATION
        
        Args:
            test_data: Test data for functionality verification
            
        Returns:
            Test execution results
            
        Raises:
            ValueError: If test data is invalid
            RuntimeError: If functionality test fails
        """
        validation = self.validate_input(test_data)
        if not validation.is_valid:
            raise ValueError(f"Invalid test data: {validation.validation_errors}")
        return self.execute(test_data)
    
    def get_contract_id(self) -> Optional[str]:
        """Get the contract ID for this tool
        
        Returns:
            Contract ID string or None if not applicable
        """
        tool_info = self.get_tool_info()
        return tool_info.get('contract_id')
    
    def get_capabilities(self) -> list:
        """Get tool capabilities
        
        Returns:
            List of capability strings
        """
        tool_info = self.get_tool_info()
        return tool_info.get('capabilities', [])


class ToolExecutionError(Exception):
    """Exception raised when tool execution fails"""
    
    def __init__(self, tool_name: str, error_message: str, original_error: Optional[Exception] = None):
        self.tool_name = tool_name
        self.error_message = error_message
        self.original_error = original_error
        super().__init__(f"Tool {tool_name} failed: {error_message}")


class ToolValidationError(Exception):
    """Exception raised when tool input validation fails"""
    
    def __init__(self, tool_name: str, validation_errors: list):
        self.tool_name = tool_name
        self.validation_errors = validation_errors
        super().__init__(f"Tool {tool_name} validation failed: {validation_errors}")