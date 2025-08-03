"""
Contract Loader

Handles loading and caching of tool contracts from various sources.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .validation_types import ContractValidationError
from .schema_validator import SchemaValidator


class ContractLoader:
    """Loads and caches tool contracts with validation"""
    
    def __init__(self, contracts_dir: str = "contracts"):
        """
        Initialize contract loader
        
        Args:
            contracts_dir: Path to directory containing contract files
        """
        self.contracts_dir = Path(contracts_dir)
        self.schema_path = self.contracts_dir / "schemas" / "tool_contract_schema.yaml"
        self.tools_dir = self.contracts_dir / "tools"
        self.adapters_dir = self.contracts_dir / "adapters"
        
        # Loaded contracts cache
        self._contracts_cache: Dict[str, Dict[str, Any]] = {}
        
        # Tool ID to filename mapping (handles both T31 and T31_ENTITY_BUILDER patterns)
        self._tool_filename_map = {
            "T01": "T01_PDF_LOADER",
            "T15A": "T15A_TEXT_CHUNKER", 
            "T23A": "T23A_SPACY_NER",
            "T27": "T27_RELATIONSHIP_EXTRACTOR",
            "T31": "T31_ENTITY_BUILDER",
            "T34": "T34_EDGE_BUILDER",
            "T49": "T49_MULTI_HOP_QUERY",
            "T68": "T68_PAGE_RANK"
        }
        
        # Initialize schema validator
        self.schema_validator = SchemaValidator(self.schema_path)
    
    def load_contract(self, tool_id: str, contract_type: str = "tool") -> Dict[str, Any]:
        """
        Load a specific tool contract
        
        Args:
            tool_id: Tool identifier (e.g., "T01_PDF_LOADER")
            contract_type: Type of contract ("tool" or "adapter")
            
        Returns:
            Contract dictionary
        """
        cache_key = f"{contract_type}:{tool_id}"
        if cache_key in self._contracts_cache:
            return self._contracts_cache[cache_key]
        
        # Determine contract file path
        if contract_type == "tool":
            # Try mapped filename first, then direct filename
            filename = self._tool_filename_map.get(tool_id, tool_id)
            contract_path = self.tools_dir / f"{filename}.yaml"
            
            # If mapped file doesn't exist, try direct tool_id
            if not contract_path.exists():
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
        schema_errors = self.schema_validator.validate_contract_schema(contract)
        if schema_errors:
            raise ContractValidationError(f"Schema validation failed: {schema_errors}")
        
        # Cache and return
        self._contracts_cache[cache_key] = contract
        return contract
    
    def get_all_tool_contracts(self) -> Dict[str, Dict[str, Any]]:
        """Load all tool contracts"""
        contracts = {}
        
        if self.tools_dir.exists():
            for contract_file in self.tools_dir.glob("*.yaml"):
                tool_id = contract_file.stem
                try:
                    contracts[tool_id] = self.load_contract(tool_id, "tool")
                except Exception as e:
                    contracts[tool_id] = {"error": str(e)}
        
        return contracts
    
    def get_all_adapter_contracts(self) -> Dict[str, Dict[str, Any]]:
        """Load all adapter contracts"""
        contracts = {}
        
        if self.adapters_dir.exists():
            for contract_file in self.adapters_dir.glob("*.yaml"):
                adapter_id = contract_file.stem
                try:
                    contracts[adapter_id] = self.load_contract(adapter_id, "adapter")
                except Exception as e:
                    contracts[adapter_id] = {"error": str(e)}
        
        return contracts
    
    def clear_cache(self):
        """Clear the contracts cache"""
        self._contracts_cache.clear()
    
    def reload_contract(self, tool_id: str, contract_type: str = "tool") -> Dict[str, Any]:
        """Force reload a contract from disk"""
        cache_key = f"{contract_type}:{tool_id}"
        if cache_key in self._contracts_cache:
            del self._contracts_cache[cache_key]
        return self.load_contract(tool_id, contract_type)
    
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
    
    def get_contract_summary(self, tool_id: str, contract_type: str = "tool") -> Dict[str, Any]:
        """Get summary information about a contract"""
        try:
            contract = self.load_contract(tool_id, contract_type)
            return {
                'tool_id': tool_id,
                'category': contract.get('category'),
                'input_types': [dt['type'] for dt in contract.get('input_contract', {}).get('required_data_types', [])],
                'output_types': [dt['type'] for dt in contract.get('output_contract', {}).get('produced_data_types', [])],
                'error_codes': [ec['code'] for ec in contract.get('error_codes', [])]
            }
        except Exception as e:
            return {
                'tool_id': tool_id,
                'error': str(e)
            }
