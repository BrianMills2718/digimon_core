import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.contract_validator import ContractValidator
from src.core.pipeline_orchestrator import PipelineOrchestrator

class TestContractEnforcement:
    """Test that contracts are actually enforced in the pipeline"""
    
    def test_contract_prevents_invalid_tool_input(self):
        """Test that invalid input is rejected by contract validation"""
        orchestrator = PipelineOrchestrator()
        
        # This should fail contract validation
        with pytest.raises(ValueError, match="Input validation failed"):
            orchestrator._execute_tool(
                tool_config={'tool_id': 'T01_PDFLoader'},
                input_data={'invalid_field': 'invalid_value'},  # Missing required fields
                context={'workflow_id': 'test'}
            )
    
    def test_all_contracts_are_valid(self):
        """Test that all existing contracts pass schema validation"""
        validator = ContractValidator("contracts")
        
        contract_files = list(Path("contracts/tools").glob("*.yaml"))
        assert len(contract_files) > 0, "No contract files found"
        
        for contract_file in contract_files:
            contract = validator.load_contract(contract_file.stem)
            errors = validator.validate_contract_schema(contract)
            assert not errors, f"Contract {contract_file.stem} has schema errors: {errors}"
    
    def test_contract_loading_all_tools(self):
        """Test that all critical tool contracts can be loaded"""
        validator = ContractValidator("contracts")
        
        critical_contracts = [
            'T01_PDFLoader',
            'T15A_TextChunker', 
            'T23A_SpacyNER',
            'T27_RelationshipExtractor',
            'T31_EntityBuilder',
            'T34_EdgeBuilder',
            'T49_MultiHopQuery',
            'T68_PageRank'
        ]
        
        for contract_id in critical_contracts:
            contract = validator.load_contract(contract_id)
            assert contract is not None, f"Failed to load contract: {contract_id}"
            
            # Verify required fields are present
            assert 'tool_id' in contract
            assert 'description' in contract
            assert 'category' in contract
            assert 'input_contract' in contract
            assert 'output_contract' in contract
            assert 'error_codes' in contract
    
    def test_contract_schema_compliance(self):
        """Test that contracts comply with the tool contract schema"""
        validator = ContractValidator("contracts")
        
        # Load the schema
        schema = validator.contract_schema
        assert schema is not None, "Contract schema not loaded"
        
        # Test each contract against schema
        contract_files = list(Path("contracts/tools").glob("*.yaml"))
        
        for contract_file in contract_files:
            contract = validator.load_contract(contract_file.stem)
            
            # Validate against schema
            errors = validator.validate_contract_schema(contract)
            assert not errors, f"Contract {contract_file.stem} schema validation failed: {errors}"
    
    def test_input_output_contract_structure(self):
        """Test that input/output contracts have required structure"""
        validator = ContractValidator("contracts")
        
        contract = validator.load_contract("T01_PDFLoader")
        assert contract is not None
        
        # Check input contract structure
        input_contract = contract['input_contract']
        assert 'required_data_types' in input_contract
        assert 'required_state' in input_contract
        
        # Check output contract structure
        output_contract = contract['output_contract']
        assert 'produced_data_types' in output_contract
        assert 'produced_state' in output_contract
        
        # Check data types have required fields
        for data_type in input_contract['required_data_types']:
            assert 'type' in data_type
            assert 'attributes' in data_type
        
        for data_type in output_contract['produced_data_types']:
            assert 'type' in data_type
            assert 'attributes' in data_type
    
    def test_error_codes_structure(self):
        """Test that error codes have required structure"""
        validator = ContractValidator("contracts")
        
        contract = validator.load_contract("T01_PDFLoader")
        assert contract is not None
        
        error_codes = contract['error_codes']
        assert len(error_codes) > 0
        
        for error_code in error_codes:
            assert 'code' in error_code
            assert 'description' in error_code
            assert 'severity' in error_code
            assert error_code['severity'] in ['error', 'warning', 'info']