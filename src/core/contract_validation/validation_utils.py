"""
Validation Utilities

Utility functions for contract validation and CI/CD integration.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from .contract_validator import ContractValidator


def validate_all_contracts(contracts_dir: str = "contracts") -> bool:
    """
    Validate all contracts in directory - suitable for CI/CD
    
    Args:
        contracts_dir: Directory containing contract files
        
    Returns:
        True if all contracts are valid, False otherwise
    """
    validator = ContractValidator(contracts_dir)
    results = validator.batch_validate_contracts()
    
    return results['summary']['invalid'] == 0


def validate_tool_contract(tool_id: str, input_data: Any, contracts_dir: str = "contracts") -> Dict[str, Any]:
    """
    Validate input data against a specific tool contract
    
    Args:
        tool_id: Tool identifier
        input_data: Input data to validate
        contracts_dir: Directory containing contract files
        
    Returns:
        Validation result dictionary
    """
    validator = ContractValidator(contracts_dir)
    return validator.validate_tool_contract(tool_id, input_data)


def generate_contract_report(tool_id: str, contracts_dir: str = "contracts") -> Dict[str, Any]:
    """
    Generate a contract validation report for a specific tool
    
    Args:
        tool_id: Tool identifier
        contracts_dir: Directory containing contract files
        
    Returns:
        Contract report dictionary
    """
    validator = ContractValidator(contracts_dir)
    return validator.generate_contract_report(tool_id)


def check_contract_compatibility(tool_a_id: str, tool_b_id: str, 
                               contracts_dir: str = "contracts") -> Dict[str, Any]:
    """
    Check if two tools are compatible based on their contracts
    
    Args:
        tool_a_id: First tool identifier
        tool_b_id: Second tool identifier
        contracts_dir: Directory containing contract files
        
    Returns:
        Compatibility analysis
    """
    validator = ContractValidator(contracts_dir)
    
    try:
        contract_a = validator.load_contract(tool_a_id)
        contract_b = validator.load_contract(tool_b_id)
        
        # Check if tool A's output can be tool B's input
        output_types_a = set()
        for dt in contract_a.get('output_contract', {}).get('produced_data_types', []):
            output_types_a.add(dt['type'])
        
        input_types_b = set()
        for dt in contract_b.get('input_contract', {}).get('required_data_types', []):
            input_types_b.add(dt['type'])
        
        compatible_types = output_types_a.intersection(input_types_b)
        
        return {
            'compatible': len(compatible_types) > 0,
            'tool_a_outputs': list(output_types_a),
            'tool_b_inputs': list(input_types_b),
            'compatible_types': list(compatible_types),
            'can_chain': len(compatible_types) > 0
        }
        
    except Exception as e:
        return {
            'compatible': False,
            'error': str(e),
            'tool_a_outputs': [],
            'tool_b_inputs': [],
            'compatible_types': [],
            'can_chain': False
        }


def create_contract_template(tool_name: str, category: str = "processing") -> Dict[str, Any]:
    """
    Create a contract template for a new tool
    
    Args:
        tool_name: Name of the tool
        category: Tool category
        
    Returns:
        Contract template
    """
    return {
        "tool_id": tool_name.upper().replace(" ", "_"),
        "tool_name": tool_name,
        "version": "1.0.0",
        "category": category,
        "description": f"Contract for {tool_name}",
        "input_contract": {
            "required_data_types": [
                {
                    "type": "Document",
                    "attributes": ["content", "original_filename"]
                }
            ]
        },
        "output_contract": {
            "produced_data_types": [
                {
                    "type": "Entity",
                    "attributes": ["canonical_name", "entity_type"]
                }
            ]
        },
        "interface": {
            "methods": [
                {
                    "name": "execute",
                    "required": True,
                    "parameters": [
                        {
                            "name": "input_data",
                            "type": "dict",
                            "required": True
                        }
                    ],
                    "return_type": "dict"
                }
            ]
        },
        "error_codes": [
            {
                "code": "INVALID_INPUT",
                "description": "Input data does not meet requirements"
            },
            {
                "code": "PROCESSING_ERROR",
                "description": "Error occurred during processing"
            }
        ],
        "performance": {
            "max_execution_time": 30.0,
            "max_memory_mb": 512
        },
        "quality": {
            "min_confidence": 0.7
        }
    }


def validate_contracts_directory(contracts_dir: str) -> Dict[str, Any]:
    """
    Validate the structure and contents of a contracts directory
    
    Args:
        contracts_dir: Directory to validate
        
    Returns:
        Validation results
    """
    contracts_path = Path(contracts_dir)
    
    if not contracts_path.exists():
        return {
            'valid': False,
            'error': f'Contracts directory does not exist: {contracts_dir}',
            'structure': {}
        }
    
    structure = {
        'has_schema': (contracts_path / 'schemas' / 'tool_contract_schema.yaml').exists(),
        'has_tools_dir': (contracts_path / 'tools').exists(),
        'has_adapters_dir': (contracts_path / 'adapters').exists(),
        'tool_contracts': 0,
        'adapter_contracts': 0
    }
    
    # Count contract files
    tools_dir = contracts_path / 'tools'
    if tools_dir.exists():
        structure['tool_contracts'] = len(list(tools_dir.glob('*.yaml')))
    
    adapters_dir = contracts_path / 'adapters'
    if adapters_dir.exists():
        structure['adapter_contracts'] = len(list(adapters_dir.glob('*.yaml')))
    
    # Check if basic structure is valid
    valid = structure['has_schema'] and structure['has_tools_dir']
    
    return {
        'valid': valid,
        'structure': structure,
        'recommendations': _generate_structure_recommendations(structure)
    }


def _generate_structure_recommendations(structure: Dict[str, Any]) -> list[str]:
    """Generate recommendations for contracts directory structure"""
    recommendations = []
    
    if not structure['has_schema']:
        recommendations.append('Create schemas/tool_contract_schema.yaml file')
    
    if not structure['has_tools_dir']:
        recommendations.append('Create tools/ directory for tool contracts')
    
    if not structure['has_adapters_dir']:
        recommendations.append('Create adapters/ directory for adapter contracts')
    
    if structure['tool_contracts'] == 0:
        recommendations.append('Add tool contract files to tools/ directory')
    
    return recommendations


def export_validation_results(results: Dict[str, Any], output_file: str, format: str = 'json'):
    """
    Export validation results to a file
    
    Args:
        results: Validation results to export
        output_file: Output file path
        format: Export format ('json' or 'yaml')
    """
    import json
    import yaml
    
    with open(output_file, 'w') as f:
        if format.lower() == 'yaml':
            yaml.dump(results, f, default_flow_style=False)
        else:
            json.dump(results, f, indent=2)
