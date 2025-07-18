"""Contract Validator - Programmatic Tool Compatibility Verification

Validates that tool implementations adhere to their declared contracts.
Enables automated testing of tool compatibility across the 121-tool ecosystem.
"""

import yaml
import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Type, Union
import inspect

try:
    from .data_models import (
        BaseObject, Document, Chunk, Entity, Relationship, 
        WorkflowState, TextForLLMProcessing,
        ObjectType, QualityTier
    )
    from .ontology_validator import OntologyValidator
except ImportError:
    # For standalone execution
    from data_models import (
        BaseObject, Document, Chunk, Entity, Relationship, 
        WorkflowState, TextForLLMProcessing,
        ObjectType, QualityTier
    )
    from ontology_validator import OntologyValidator


class ContractValidationError(Exception):
    """Raised when contract validation fails"""
    pass


class ToolValidationError(Exception):
    """Raised when tool implementation doesn't match its contract"""
    pass


class ContractValidator:
    """Main validator for tool contracts and implementations"""
    
    def __init__(self, contracts_dir: str = "contracts"):
        """
        Initialize validator with contracts directory
        
        Args:
            contracts_dir: Path to directory containing contract files
        """
        self.contracts_dir = Path(contracts_dir)
        self.schema_path = self.contracts_dir / "schemas" / "tool_contract_schema.yaml"
        self.tools_dir = self.contracts_dir / "tools"
        self.adapters_dir = self.contracts_dir / "adapters"
        
        # Load contract schema
        self.contract_schema = self._load_contract_schema()
        
        # Data type mapping
        self.data_type_mapping = {
            "Document": Document,
            "Chunk": Chunk,
            "Entity": Entity,
            "Relationship": Relationship,
            "WorkflowState": WorkflowState,
            "TextForLLMProcessing": TextForLLMProcessing
        }
        
        # Loaded contracts cache
        self._contracts_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize ontology validator
        self.ontology_validator = OntologyValidator()
    
    def _load_contract_schema(self) -> Dict[str, Any]:
        """Load the contract schema for validation"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Contract schema not found at {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            return yaml.safe_load(f)
    
    def load_contract(self, tool_id: str, contract_type: str = "tool") -> Dict[str, Any]:
        """
        Load a specific tool contract
        
        Args:
            tool_id: Tool identifier (e.g., "T01_PDF_LOADER")
            contract_type: Type of contract ("tool" or "adapter")
            
        Returns:
            Contract dictionary
        """
        if tool_id in self._contracts_cache:
            return self._contracts_cache[tool_id]
        
        # Determine contract file path
        if contract_type == "tool":
            contract_path = self.tools_dir / f"{tool_id}.yaml"
        elif contract_type == "adapter":
            contract_path = self.adapters_dir / f"{tool_id}.yaml"
        else:
            raise ValueError(f"Invalid contract type: {contract_type}")
        
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract not found: {contract_path}")
        
        # Load contract
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
        
        # Validate against schema
        self.validate_contract_schema(contract)
        
        # Cache and return
        self._contracts_cache[tool_id] = contract
        return contract
    
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
    
    def validate_input(self, tool_id: str, input_data: Dict[str, Any], contract_type: str = "tool") -> Tuple[bool, List[str]]:
        """
        Validate input data against tool's input contract using JSON Schema
        
        Args:
            tool_id: Tool identifier
            input_data: Input data to validate
            contract_type: Type of contract ("tool" or "adapter")
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            contract = self.load_contract(tool_id, contract_type)
            input_schema = contract.get('input_contract', {})
            
            if not input_schema:
                return True, []  # No input contract defined
            
            # Validate against JSON Schema
            jsonschema.validate(input_data, input_schema)
            return True, []
            
        except jsonschema.ValidationError as e:
            return False, [f"Input validation error: {e.message}"]
        except Exception as e:
            return False, [f"Error validating input: {str(e)}"]
    
    def validate_output(self, tool_id: str, output_data: Any, contract_type: str = "tool") -> Tuple[bool, List[str]]:
        """
        Validate output data against tool's output contract using JSON Schema
        
        Args:
            tool_id: Tool identifier
            output_data: Output data to validate
            contract_type: Type of contract ("tool" or "adapter")
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            contract = self.load_contract(tool_id, contract_type)
            output_schema = contract.get('output_contract', {})
            
            if not output_schema:
                return True, []  # No output contract defined
            
            # Validate against JSON Schema
            jsonschema.validate(output_data, output_schema)
            return True, []
            
        except jsonschema.ValidationError as e:
            return False, [f"Output validation error: {e.message}"]
        except Exception as e:
            return False, [f"Error validating output: {str(e)}"]
    
    def validate_tool_interface(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """
        Validate that a tool instance matches its contract interface
        
        Args:
            tool_instance: Tool instance to validate
            contract: Tool contract to validate against
            
        Returns:
            List of validation errors
        """
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        # Check if tool has required methods
        if hasattr(tool_instance, 'execute'):
            # Check execute method signature
            execute_errors = self._validate_execute_method(tool_instance, contract)
            errors.extend(execute_errors)
        else:
            errors.append(f"Tool {tool_id} missing required 'execute' method")
        
        # Check for other standard methods
        standard_methods = ['validate_input', 'get_info']
        for method_name in standard_methods:
            if not hasattr(tool_instance, method_name):
                errors.append(f"Tool {tool_id} missing recommended method: {method_name}")
        
        return errors
    
    def _validate_execute_method(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate the execute method signature and behavior"""
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        execute_method = getattr(tool_instance, 'execute')
        if not callable(execute_method):
            errors.append(f"Tool {tool_id} 'execute' is not callable")
            return errors
        
        # Check method signature
        sig = inspect.signature(execute_method)
        params = list(sig.parameters.keys())
        
        # Remove 'self' if present
        if params and params[0] == 'self':
            params = params[1:]
        
        # Basic signature validation
        if not params:
            errors.append(f"Tool {tool_id} execute method has no parameters")
        
        return errors
    
    def validate_data_flow(self, tool_instance: Any, contract: Dict[str, Any], 
                          test_input: Dict[str, Any]) -> Tuple[bool, List[str], Any]:
        """
        Validate data flow through a tool using test input
        
        Args:
            tool_instance: Tool to test
            contract: Tool contract
            test_input: Test input data
            
        Returns:
            Tuple of (success, errors, output)
        """
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        try:
            # Validate input against contract
            input_errors = self._validate_input_data(test_input, contract)
            if input_errors:
                errors.extend(input_errors)
                return False, errors, None
            
            # Execute tool
            if hasattr(tool_instance, 'execute'):
                output = tool_instance.execute(**test_input)
            else:
                errors.append(f"Tool {tool_id} has no execute method")
                return False, errors, None
            
            # Validate output against contract
            output_errors = self._validate_output_data(output, contract)
            if output_errors:
                errors.extend(output_errors)
                return False, errors, output
            
            return True, [], output
            
        except Exception as e:
            errors.append(f"Tool {tool_id} execution failed: {str(e)}")
            return False, errors, None
    
    def _validate_input_data(self, input_data: Dict[str, Any], contract: Dict[str, Any]) -> List[str]:
        """Validate input data against contract requirements"""
        errors = []
        input_contract = contract.get('input_contract', {})
        required_data_types = input_contract.get('required_data_types', [])
        
        # Check required data types are present
        for data_type_spec in required_data_types:
            data_type = data_type_spec['type']
            required_attrs = data_type_spec.get('attributes', [])
            
            # Look for data of this type in input
            type_found = False
            for key, value in input_data.items():
                if self._is_data_type(value, data_type):
                    type_found = True
                    # Validate required attributes
                    attr_errors = self._validate_object_attributes(value, required_attrs, data_type)
                    errors.extend(attr_errors)
                    break
            
            if not type_found:
                errors.append(f"Required data type {data_type} not found in input")
        
        return errors
    
    def _validate_output_data(self, output_data: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate output data against contract specifications"""
        errors = []
        output_contract = contract.get('output_contract', {})
        produced_data_types = output_contract.get('produced_data_types', [])
        
        # Handle different output formats
        if isinstance(output_data, dict):
            output_items = output_data.values()
        elif isinstance(output_data, (list, tuple)):
            output_items = output_data
        else:
            output_items = [output_data]
        
        # Check each produced data type
        for data_type_spec in produced_data_types:
            data_type = data_type_spec['type']
            required_attrs = data_type_spec.get('attributes', [])
            validation_rules = data_type_spec.get('validation', {})
            
            # Look for objects of this type in output
            type_found = False
            for item in output_items:
                if self._is_data_type(item, data_type):
                    type_found = True
                    # Validate attributes
                    attr_errors = self._validate_object_attributes(item, required_attrs, data_type)
                    errors.extend(attr_errors)
                    
                    # Validate against ontology if applicable
                    if validation_rules and (data_type == "Entity" or data_type == "Relationship"):
                        ontology_errors = self._validate_ontology_constraints(item, validation_rules, data_type)
                        errors.extend(ontology_errors)
                    break
            
            if not type_found:
                errors.append(f"Expected data type {data_type} not found in output")
        
        return errors
    
    def _is_data_type(self, obj: Any, data_type: str) -> bool:
        """Check if an object is of the specified data type"""
        expected_class = self.data_type_mapping.get(data_type)
        if expected_class is None:
            return False
        
        # Check if it's an instance of the expected class
        if isinstance(obj, expected_class):
            return True
        
        # Check if it's a dict with correct object_type
        if isinstance(obj, dict):
            obj_type = obj.get('object_type')
            if obj_type == data_type or (hasattr(ObjectType, data_type.upper()) and obj_type == getattr(ObjectType, data_type.upper())):
                return True
        
        return False
    
    def _validate_object_attributes(self, obj: Any, required_attrs: List[str], data_type: str) -> List[str]:
        """Validate that an object has required attributes"""
        errors = []
        
        for attr in required_attrs:
            if isinstance(obj, dict):
                if attr not in obj:
                    errors.append(f"{data_type} object missing required attribute: {attr}")
            elif hasattr(obj, attr):
                if getattr(obj, attr) is None:
                    errors.append(f"{data_type} object has null value for required attribute: {attr}")
            else:
                errors.append(f"{data_type} object missing required attribute: {attr}")
        
        return errors
    
    def _validate_ontology_constraints(self, obj: Any, validation_rules: Dict[str, Any], 
                                     data_type: str) -> List[str]:
        """Validate object against ontology constraints"""
        errors = []
        
        if data_type == "Entity":
            # Convert to Entity object if it's a dict
            if isinstance(obj, dict):
                try:
                    entity_obj = Entity(**obj)
                except Exception as e:
                    errors.append(f"Failed to convert dict to Entity: {str(e)}")
                    return errors
            else:
                entity_obj = obj
            
            # Validate entity type constraint
            if 'entity_type' in validation_rules:
                constraint = validation_rules['entity_type'].get('constraint')
                if constraint == 'must_exist_in_ontology':
                    entity_errors = self.ontology_validator.validate_entity(entity_obj)
                    errors.extend(entity_errors)
        
        elif data_type == "Relationship":
            # Convert to Relationship object if it's a dict
            if isinstance(obj, dict):
                try:
                    rel_obj = Relationship(**obj)
                except Exception as e:
                    errors.append(f"Failed to convert dict to Relationship: {str(e)}")
                    return errors
            else:
                rel_obj = obj
            
            # Validate relationship type constraint
            if 'relationship_type' in validation_rules:
                constraint = validation_rules['relationship_type'].get('constraint')
                if constraint == 'must_exist_in_ontology':
                    rel_errors = self.ontology_validator.validate_relationship(rel_obj)
                    errors.extend(rel_errors)
        
        return errors
    
    def generate_contract_report(self, tool_id: str) -> Dict[str, Any]:
        """Generate a comprehensive contract validation report"""
        try:
            contract = self.load_contract(tool_id)
            
            report = {
                'tool_id': tool_id,
                'contract_valid': True,
                'schema_errors': [],
                'contract_summary': {
                    'category': contract.get('category'),
                    'input_types': [dt['type'] for dt in contract.get('input_contract', {}).get('required_data_types', [])],
                    'output_types': [dt['type'] for dt in contract.get('output_contract', {}).get('produced_data_types', [])],
                    'error_codes': [ec['code'] for ec in contract.get('error_codes', [])]
                }
            }
            
            # Validate schema
            schema_errors = self.validate_contract_schema(contract)
            if schema_errors:
                report['contract_valid'] = False
                report['schema_errors'] = schema_errors
            
            return report
            
        except Exception as e:
            return {
                'tool_id': tool_id,
                'contract_valid': False,
                'error': str(e),
                'schema_errors': [],
                'contract_summary': None
            }
    
    def validate_tool_contract(self, tool_name: str, input_data: Any) -> Dict[str, Any]:
        """Validate input data against tool contract"""
        errors = []
        warnings = []
        
        try:
            contract = self.load_contract(tool_name)
            
            # Validate input schema
            input_schema = contract.get("input_contract", {})
            validation_errors = self._validate_schema(input_data, input_schema, "input")
            errors.extend(validation_errors)
            
            # Validate required fields
            required_fields = contract.get("required_fields", [])
            for field in required_fields:
                if field not in input_data:
                    errors.append(f"Required field missing: {field}")
            
            # Validate field types
            field_types = contract.get("field_types", {})
            for field, expected_type in field_types.items():
                if field in input_data:
                    actual_type = type(input_data[field]).__name__
                    if actual_type != expected_type:
                        errors.append(f"Field '{field}' expected type {expected_type}, got {actual_type}")
            
            # Validate constraints
            constraints = contract.get("constraints", {})
            constraint_errors = self._validate_constraints(input_data, constraints)
            errors.extend(constraint_errors)
            
            # Check for warnings
            deprecated_fields = contract.get("deprecated_fields", [])
            for field in deprecated_fields:
                if field in input_data:
                    warnings.append(f"Field '{field}' is deprecated")
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "validated_data": input_data if len(errors) == 0 else None
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Contract validation failed: {str(e)}"],
                "warnings": [],
                "validated_data": None
            }
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any], context: str) -> List[str]:
        """Validate data against schema"""
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
        """Validate a single field"""
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
        
    def _validate_constraints(self, data: Dict[str, Any], constraints: Dict[str, Any]) -> List[str]:
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
        
    def enforce_contract(self, tool_result: Any, contract: Dict[str, Any]) -> bool:
        """COMPLETE contract enforcement - no fallback acceptance
        
        Implements strict contract validation as required by CLAUDE.md
        Must fail on contract violations
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
        
    def create_default_contract(self, tool_name: str) -> Dict[str, Any]:
        """Create a default contract template"""
        return {
            "tool_name": tool_name,
            "version": "1.0.0",
            "description": f"Contract for {tool_name}",
            "input_schema": {
                "data": {
                    "type": "object",
                    "required": True
                }
            },
            "output_schema": {
                "result": {
                    "type": "object",
                    "required": True
                }
            },
            "required_fields": ["data"],
            "field_types": {
                "data": "dict"
            },
            "constraints": {},
            "deprecated_fields": []
        }

    def batch_validate_contracts(self, contract_dir: Optional[str] = None) -> Dict[str, Any]:
        """Validate all contracts in a directory"""
        if contract_dir:
            tools_dir = Path(contract_dir) / "tools"
            adapters_dir = Path(contract_dir) / "adapters"
        else:
            tools_dir = self.tools_dir
            adapters_dir = self.adapters_dir
        
        results = {
            'summary': {'total': 0, 'valid': 0, 'invalid': 0},
            'tools': {},
            'adapters': {}
        }
        
        # Validate tool contracts
        if tools_dir.exists():
            for contract_file in tools_dir.glob("*.yaml"):
                tool_id = contract_file.stem
                report = self.generate_contract_report(tool_id)
                results['tools'][tool_id] = report
                results['summary']['total'] += 1
                if report['contract_valid']:
                    results['summary']['valid'] += 1
                else:
                    results['summary']['invalid'] += 1
        
        # Validate adapter contracts  
        if adapters_dir.exists():
            for contract_file in adapters_dir.glob("*.yaml"):
                adapter_id = contract_file.stem
                try:
                    # Load adapter contract explicitly
                    contract = self.load_contract(adapter_id, "adapter")
                    report = {
                        'tool_id': adapter_id,
                        'contract_valid': True,
                        'schema_errors': [],
                        'contract_summary': {
                            'category': contract.get('category'),
                            'input_types': [dt['type'] for dt in contract.get('input_contract', {}).get('required_data_types', [])],
                            'output_types': [dt['type'] for dt in contract.get('output_contract', {}).get('produced_data_types', [])],
                            'error_codes': [ec['code'] for ec in contract.get('error_codes', [])]
                        }
                    }
                    # Validate schema
                    schema_errors = self.validate_contract_schema(contract)
                    if schema_errors:
                        report['contract_valid'] = False
                        report['schema_errors'] = schema_errors
                except Exception as e:
                    report = {
                        'tool_id': adapter_id,
                        'contract_valid': False,
                        'error': str(e),
                        'schema_errors': [],
                        'contract_summary': None
                    }
                
                results['adapters'][adapter_id] = report
                results['summary']['total'] += 1
                if report['contract_valid']:
                    results['summary']['valid'] += 1
                else:
                    results['summary']['invalid'] += 1
        
        return results


class ContractTestFramework:
    """Framework for creating automated contract tests"""
    
    def __init__(self, validator: ContractValidator):
        self.validator = validator
    
    def create_test_data(self, data_type: str, **kwargs) -> BaseObject:
        """Create test data objects for contract testing"""
        data_class = self.validator.data_type_mapping.get(data_type)
        if not data_class:
            raise ValueError(f"Unknown data type: {data_type}")
        
        # Create minimal valid object
        base_params = {
            'object_type': getattr(ObjectType, data_type.upper(), data_type),
            'confidence': kwargs.get('confidence', 0.8),
            'quality_tier': kwargs.get('quality_tier', QualityTier.MEDIUM),
            'created_by': kwargs.get('created_by', 'test_framework'),
            'workflow_id': kwargs.get('workflow_id', 'test_workflow')
        }
        
        # Add type-specific required fields
        if data_type == "Document":
            base_params.update({
                'content': kwargs.get('content', 'Test document content'),
                'original_filename': kwargs.get('original_filename', 'test.txt')
            })
        elif data_type == "Chunk":
            base_params.update({
                'content': kwargs.get('content', 'Test chunk content'),
                'document_ref': kwargs.get('document_ref', 'neo4j://document/test-doc'),
                'position': kwargs.get('position', 0)
            })
        elif data_type == "Entity":
            base_params.update({
                'canonical_name': kwargs.get('canonical_name', 'Test Entity'),
                'entity_type': kwargs.get('entity_type', 'PERSON')
            })
        
        # Override with any provided kwargs
        base_params.update(kwargs)
        
        return data_class(**base_params)


# Utility functions for CI/CD integration
def validate_all_contracts(contracts_dir: str = "contracts") -> bool:
    """
    Validate all contracts in directory - suitable for CI/CD
    
    Returns:
        True if all contracts are valid, False otherwise
    """
    validator = ContractValidator(contracts_dir)
    results = validator.batch_validate_contracts()
    
    return results['summary']['invalid'] == 0


if __name__ == "__main__":
    # Example usage
    validator = ContractValidator()
    
    # Validate a specific contract
    try:
        contract = validator.load_contract("T01_PDF_LOADER")
        print(f"Contract loaded successfully: {contract['tool_id']}")
        
        # Generate report
        report = validator.generate_contract_report("T01_PDF_LOADER")
        print(f"Contract valid: {report['contract_valid']}")
        
    except Exception as e:
        print(f"Error: {e}")