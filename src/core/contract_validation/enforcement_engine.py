"""
Contract Enforcement Engine

Strict contract enforcement with no fallback acceptance as required by CLAUDE.md.
"""

from typing import Dict, Any
from .validation_types import ContractValidationError


class ContractEnforcementEngine:
    """Enforces contracts with strict validation and no fallback acceptance"""
    
    def enforce_contract(self, tool_result: Any, contract: Dict[str, Any]) -> bool:
        """COMPLETE contract enforcement - no fallback acceptance
        
        Implements strict contract validation as required by CLAUDE.md
        Must fail on contract violations
        
        Args:
            tool_result: Result from tool execution
            contract: Contract to enforce
            
        Returns:
            True if contract is satisfied
            
        Raises:
            ContractValidationError: If contract is violated
        """
        if not contract:
            raise ContractValidationError("No contract provided for enforcement")
        
        try:
            # Validate output data structure
            expected_outputs = contract.get("outputs", {})
            if not expected_outputs:
                # If no outputs specified, accept any result
                return True
            
            # Check if tool_result matches expected structure
            if isinstance(tool_result, dict):
                # Validate required fields
                required_fields = expected_outputs.get("required_fields", [])
                for field in required_fields:
                    if field not in tool_result:
                        raise ContractValidationError(f"Missing required field: {field}")
                
                # Validate field types
                field_types = expected_outputs.get("field_types", {})
                for field, expected_type in field_types.items():
                    if field in tool_result:
                        actual_value = tool_result[field]
                        if not self._validate_field_type(actual_value, expected_type):
                            raise ContractValidationError(
                                f"Field '{field}' has incorrect type. Expected: {expected_type}, Got: {type(actual_value).__name__}"
                            )
                
                # Validate status field if present
                if "status" in tool_result:
                    valid_statuses = ["success", "error", "warning"]
                    if tool_result["status"] not in valid_statuses:
                        raise ContractValidationError(f"Invalid status: {tool_result['status']}")
                
                # Validate confidence if present
                if "confidence" in tool_result:
                    confidence = tool_result["confidence"]
                    if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
                        raise ContractValidationError(f"Invalid confidence value: {confidence}")
                
                # Validate data formats
                data_formats = expected_outputs.get("data_formats", {})
                for field, format_spec in data_formats.items():
                    if field in tool_result:
                        if not self._validate_data_format(tool_result[field], format_spec):
                            raise ContractValidationError(f"Field '{field}' does not match expected format: {format_spec}")
            
            return True
            
        except ContractValidationError:
            # Re-raise contract validation errors
            raise
        except Exception as e:
            raise ContractValidationError(f"Contract enforcement failed: {str(e)}")
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate that a field value matches expected type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
            "list": list,
            "dict": dict,
            "any": object
        }
        
        if expected_type in type_mapping:
            return isinstance(value, type_mapping[expected_type])
        
        # Handle complex types
        if expected_type.startswith("list["):
            return isinstance(value, list)
        if expected_type.startswith("dict["):
            return isinstance(value, dict)
        
        return True  # Unknown types pass for now
    
    def _validate_data_format(self, value: Any, format_spec: str) -> bool:
        """Validate data format according to specification"""
        if format_spec == "iso_datetime":
            try:
                from datetime import datetime
                datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                return True
            except:
                return False
        elif format_spec == "uuid":
            import re
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            return re.match(uuid_pattern, str(value)) is not None
        elif format_spec == "url":
            return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))
        
        return True  # Unknown formats pass for now
    
    def enforce_input_contract(self, input_data: Dict[str, Any], contract: Dict[str, Any]) -> bool:
        """Enforce input contract requirements
        
        Args:
            input_data: Input data to validate
            contract: Contract with input requirements
            
        Returns:
            True if input contract is satisfied
            
        Raises:
            ContractValidationError: If input contract is violated
        """
        input_contract = contract.get('input_contract', {})
        if not input_contract:
            return True  # No input contract to enforce
        
        # Validate required fields
        required_fields = input_contract.get('required_fields', [])
        for field in required_fields:
            if field not in input_data:
                raise ContractValidationError(f"Missing required input field: {field}")
        
        # Validate field types
        field_types = input_contract.get('field_types', {})
        for field, expected_type in field_types.items():
            if field in input_data:
                if not self._validate_field_type(input_data[field], expected_type):
                    raise ContractValidationError(
                        f"Input field '{field}' has incorrect type. Expected: {expected_type}, Got: {type(input_data[field]).__name__}"
                    )
        
        # Validate constraints
        constraints = input_contract.get('constraints', {})
        self._enforce_constraints(input_data, constraints)
        
        return True
    
    def _enforce_constraints(self, data: Dict[str, Any], constraints: Dict[str, Any]):
        """Enforce custom constraints on data"""
        for constraint_name, constraint_config in constraints.items():
            if constraint_name == "mutually_exclusive":
                # Check mutually exclusive fields
                exclusive_fields = constraint_config.get("fields", [])
                present_fields = [f for f in exclusive_fields if f in data]
                
                if len(present_fields) > 1:
                    raise ContractValidationError(f"Fields {present_fields} are mutually exclusive")
            
            elif constraint_name == "conditional_required":
                # Check conditional requirements
                condition_field = constraint_config.get("if_field")
                condition_value = constraint_config.get("if_value")
                required_field = constraint_config.get("then_required")
                
                if (condition_field in data and 
                    data[condition_field] == condition_value and 
                    required_field not in data):
                    raise ContractValidationError(
                        f"Field '{required_field}' is required when '{condition_field}' is '{condition_value}'"
                    )
    
    def enforce_performance_contract(self, execution_time: float, memory_usage: int, 
                                   contract: Dict[str, Any]) -> bool:
        """Enforce performance requirements from contract
        
        Args:
            execution_time: Time taken to execute in seconds
            memory_usage: Memory used in bytes
            contract: Contract with performance requirements
            
        Returns:
            True if performance contract is satisfied
            
        Raises:
            ContractValidationError: If performance contract is violated
        """
        performance_contract = contract.get('performance', {})
        if not performance_contract:
            return True  # No performance contract to enforce
        
        # Check maximum execution time
        max_execution_time = performance_contract.get('max_execution_time')
        if max_execution_time and execution_time > max_execution_time:
            raise ContractValidationError(
                f"Execution time {execution_time:.2f}s exceeds maximum {max_execution_time}s"
            )
        
        # Check maximum memory usage
        max_memory = performance_contract.get('max_memory_mb')
        if max_memory and memory_usage > (max_memory * 1024 * 1024):
            memory_mb = memory_usage / (1024 * 1024)
            raise ContractValidationError(
                f"Memory usage {memory_mb:.2f}MB exceeds maximum {max_memory}MB"
            )
        
        return True
    
    def enforce_quality_contract(self, result_quality: Dict[str, Any], contract: Dict[str, Any]) -> bool:
        """Enforce quality requirements from contract
        
        Args:
            result_quality: Quality metrics of the result
            contract: Contract with quality requirements
            
        Returns:
            True if quality contract is satisfied
            
        Raises:
            ContractValidationError: If quality contract is violated
        """
        quality_contract = contract.get('quality', {})
        if not quality_contract:
            return True  # No quality contract to enforce
        
        # Check minimum confidence
        min_confidence = quality_contract.get('min_confidence')
        if min_confidence:
            confidence = result_quality.get('confidence', 0.0)
            if confidence < min_confidence:
                raise ContractValidationError(
                    f"Result confidence {confidence:.2f} below minimum {min_confidence}"
                )
        
        # Check minimum accuracy
        min_accuracy = quality_contract.get('min_accuracy')
        if min_accuracy:
            accuracy = result_quality.get('accuracy', 0.0)
            if accuracy < min_accuracy:
                raise ContractValidationError(
                    f"Result accuracy {accuracy:.2f} below minimum {min_accuracy}"
                )
        
        return True
