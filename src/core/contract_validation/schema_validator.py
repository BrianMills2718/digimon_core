"""
Schema Validator

Validates contracts and data against JSON schemas with comprehensive error reporting.
"""

import yaml
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Tuple


class SchemaValidator:
    """Validates contracts and data against JSON schemas"""
    
    def __init__(self, schema_path: Path):
        """Initialize with contract schema path"""
        self.schema_path = schema_path
        self.contract_schema = self._load_contract_schema()
    
    def _load_contract_schema(self) -> Dict[str, Any]:
        """Load the contract schema for validation"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Contract schema not found at {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_contract_schema(self, contract: Dict[str, Any]) -> List[str]:
        """
        Validate contract against the schema
        
        Args:
            contract: Contract dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            jsonschema.validate(contract, self.contract_schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except jsonschema.SchemaError as e:
            errors.append(f"Schema error: {e.message}")
        
        return errors
    
    def validate_input(self, input_data: Dict[str, Any], input_schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate input data against input schema
        
        Args:
            input_data: Input data to validate
            input_schema: Schema to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            if not input_schema:
                return True, []  # No input schema defined
            
            # Validate against JSON Schema
            jsonschema.validate(input_data, input_schema)
            return True, []
            
        except jsonschema.ValidationError as e:
            return False, [f"Input validation error: {e.message}"]
        except Exception as e:
            return False, [f"Error validating input: {str(e)}"]
    
    def validate_output(self, output_data: Any, output_schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate output data against output schema
        
        Args:
            output_data: Output data to validate
            output_schema: Schema to validate against
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            if not output_schema:
                return True, []  # No output schema defined
            
            # Validate against JSON Schema
            jsonschema.validate(output_data, output_schema)
            return True, []
            
        except jsonschema.ValidationError as e:
            return False, [f"Output validation error: {e.message}"]
        except Exception as e:
            return False, [f"Error validating output: {str(e)}"]
    
    def validate_schema(self, data: Any, schema: Dict[str, Any], context: str) -> List[str]:
        """Validate data against schema with context"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append(f"{context} must be a dictionary")
            return errors
        
        # Validate each field in schema
        for field, field_schema in schema.items():
            if field in data:
                field_errors = self._validate_field(data[field], field_schema, f"{context}.{field}")
                errors.extend(field_errors)
            elif field_schema.get("required", False):
                errors.append(f"Required field missing: {context}.{field}")
        
        return errors
    
    def _validate_field(self, value: Any, field_schema: Dict[str, Any], field_path: str) -> List[str]:
        """Validate a single field against its schema"""
        errors = []
        
        # Check type
        expected_type = field_schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"{field_path} must be a string")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"{field_path} must be an integer")
            elif expected_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"{field_path} must be a number")
            elif expected_type == "boolean" and not isinstance(value, bool):
                errors.append(f"{field_path} must be a boolean")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"{field_path} must be an array")
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(f"{field_path} must be an object")
        
        # Check minimum/maximum for numbers
        if isinstance(value, (int, float)):
            minimum = field_schema.get("minimum")
            maximum = field_schema.get("maximum")
            
            if minimum is not None and value < minimum:
                errors.append(f"{field_path} must be >= {minimum}")
            if maximum is not None and value > maximum:
                errors.append(f"{field_path} must be <= {maximum}")
        
        # Check string length
        if isinstance(value, str):
            min_length = field_schema.get("minLength")
            max_length = field_schema.get("maxLength")
            
            if min_length is not None and len(value) < min_length:
                errors.append(f"{field_path} must be at least {min_length} characters")
            if max_length is not None and len(value) > max_length:
                errors.append(f"{field_path} must be at most {max_length} characters")
        
        # Check enum values
        enum_values = field_schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"{field_path} must be one of: {enum_values}")
        
        return errors
    
    def validate_constraints(self, data: Dict[str, Any], constraints: Dict[str, Any]) -> List[str]:
        """Validate custom constraints"""
        errors = []
        
        for constraint_name, constraint_config in constraints.items():
            if constraint_name == "mutually_exclusive":
                # Check mutually exclusive fields
                exclusive_fields = constraint_config.get("fields", [])
                present_fields = [f for f in exclusive_fields if f in data]
                
                if len(present_fields) > 1:
                    errors.append(f"Fields {present_fields} are mutually exclusive")
            
            elif constraint_name == "conditional_required":
                # Check conditional requirements
                condition_field = constraint_config.get("if_field")
                condition_value = constraint_config.get("if_value")
                required_field = constraint_config.get("then_required")
                
                if (condition_field in data and 
                    data[condition_field] == condition_value and 
                    required_field not in data):
                    errors.append(f"Field '{required_field}' is required when '{condition_field}' is '{condition_value}'")
        
        return errors
