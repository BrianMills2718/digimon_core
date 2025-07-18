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