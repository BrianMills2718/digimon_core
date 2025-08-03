"""
Contract Validator - Main Interface

Main validator class that orchestrates all contract validation components.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .validation_types import ContractValidationError, ToolValidationError
from .contract_loader import ContractLoader
from .schema_validator import SchemaValidator
from .interface_validator import InterfaceValidator
from .data_flow_validator import DataFlowValidator
from .ontology_contract_validator import OntologyContractValidator
from .enforcement_engine import ContractEnforcementEngine


class ContractValidator:
    """Main validator for tool contracts and implementations"""
    
    def __init__(self, contracts_dir: str = "contracts"):
        """
        Initialize validator with contracts directory
        
        Args:
            contracts_dir: Path to directory containing contract files
        """
        self.contracts_dir = Path(contracts_dir)
        
        # Initialize component validators
        self.contract_loader = ContractLoader(contracts_dir)
        self.schema_validator = SchemaValidator(self.contracts_dir / "schemas" / "tool_contract_schema.yaml")
        self.interface_validator = InterfaceValidator()
        self.data_flow_validator = DataFlowValidator()
        self.ontology_validator = OntologyContractValidator()
        self.enforcement_engine = ContractEnforcementEngine()
    
    def load_contract(self, tool_id: str, contract_type: str = "tool") -> Dict[str, Any]:
        """Load a specific tool contract"""
        return self.contract_loader.load_contract(tool_id, contract_type)
    
    def validate_contract_schema(self, contract: Dict[str, Any]) -> List[str]:
        """Validate contract against the schema"""
        return self.schema_validator.validate_contract_schema(contract)
    
    def validate_input(self, tool_id: str, input_data: Dict[str, Any], contract_type: str = "tool") -> Tuple[bool, List[str]]:
        """Validate input data against tool's input contract"""
        try:
            contract = self.load_contract(tool_id, contract_type)
            input_schema = contract.get('input_contract', {})
            return self.schema_validator.validate_input(input_data, input_schema)
        except Exception as e:
            return False, [f"Error validating input: {str(e)}"]
    
    def validate_output(self, tool_id: str, output_data: Any, contract_type: str = "tool") -> Tuple[bool, List[str]]:
        """Validate output data against tool's output contract"""
        try:
            contract = self.load_contract(tool_id, contract_type)
            output_schema = contract.get('output_contract', {})
            return self.schema_validator.validate_output(output_data, output_schema)
        except Exception as e:
            return False, [f"Error validating output: {str(e)}"]
    
    def validate_tool_interface(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate that a tool instance matches its contract interface"""
        return self.interface_validator.validate_tool_interface(tool_instance, contract)
    
    def validate_data_flow(self, tool_instance: Any, contract: Dict[str, Any], 
                          test_input: Dict[str, Any]) -> Tuple[bool, List[str], Any]:
        """Validate data flow through a tool using test input"""
        return self.data_flow_validator.validate_data_flow(tool_instance, contract, test_input)
    
    def enforce_contract(self, tool_result: Any, contract: Dict[str, Any]) -> bool:
        """Enforce contract with strict validation"""
        return self.enforcement_engine.enforce_contract(tool_result, contract)
    
    def validate_tool_contract(self, tool_name: str, input_data: Any) -> Dict[str, Any]:
        """Validate input data against tool contract"""
        errors = []
        warnings = []
        
        try:
            contract = self.load_contract(tool_name)
            
            # Validate input schema (updated to use new format and proper JSON schema validation)
            input_schema = contract.get("input_schema", contract.get("input_contract", {}))
            if input_schema:
                is_valid, validation_errors = self.schema_validator.validate_input(input_data, input_schema)
                if not is_valid:
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
            constraint_errors = self.schema_validator.validate_constraints(input_data, constraints)
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
            tools_dir = self.contracts_dir / "tools"
            adapters_dir = self.contracts_dir / "adapters"
        
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
    
    def create_default_contract(self, tool_name: str) -> Dict[str, Any]:
        """Create a default contract template"""
        return self.contract_loader.create_default_contract(tool_name)
    
    def validate_comprehensive(self, tool_id: str, tool_instance: Any, 
                             test_input: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive validation of a tool"""
        results = {
            'tool_id': tool_id,
            'overall_valid': True,
            'contract_validation': {},
            'interface_validation': {},
            'data_flow_validation': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load contract
            contract = self.load_contract(tool_id)
            
            # Validate contract schema
            schema_errors = self.validate_contract_schema(contract)
            results['contract_validation'] = {
                'valid': len(schema_errors) == 0,
                'errors': schema_errors
            }
            if schema_errors:
                results['overall_valid'] = False
                results['errors'].extend(schema_errors)
            
            # Validate tool interface
            interface_errors = self.validate_tool_interface(tool_instance, contract)
            results['interface_validation'] = {
                'valid': len(interface_errors) == 0,
                'errors': interface_errors
            }
            if interface_errors:
                results['overall_valid'] = False
                results['errors'].extend(interface_errors)
            
            # Validate data flow
            flow_success, flow_errors, output = self.validate_data_flow(tool_instance, contract, test_input)
            results['data_flow_validation'] = {
                'valid': flow_success,
                'errors': flow_errors,
                'output': output
            }
            if not flow_success:
                results['overall_valid'] = False
                results['errors'].extend(flow_errors)
            
            # Test contract enforcement if we have output
            if output is not None:
                try:
                    self.enforce_contract(output, contract)
                    results['contract_enforcement'] = {'valid': True, 'errors': []}
                except ContractValidationError as e:
                    results['contract_enforcement'] = {'valid': False, 'errors': [str(e)]}
                    results['overall_valid'] = False
                    results['errors'].append(f"Contract enforcement failed: {str(e)}")
            
        except Exception as e:
            results['overall_valid'] = False
            results['errors'].append(f"Comprehensive validation failed: {str(e)}")
        
        return results
