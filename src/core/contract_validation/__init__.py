"""
Contract Validation Module

Decomposed contract validation components for tool compatibility verification.
Provides comprehensive validation across the 121-tool ecosystem.
"""

# Import core validation types
from .validation_types import (
    ContractValidationError,
    ToolValidationError
)

# Import main validator components
from .contract_loader import ContractLoader
from .schema_validator import SchemaValidator
from .interface_validator import InterfaceValidator
from .data_flow_validator import DataFlowValidator
from .ontology_contract_validator import OntologyContractValidator
from .enforcement_engine import ContractEnforcementEngine

# Import main validator class
from .contract_validator import ContractValidator

# Import test framework
from .test_framework import ContractTestFramework

# Import utility functions
from .validation_utils import validate_all_contracts

__all__ = [
    # Exception types
    "ContractValidationError",
    "ToolValidationError",
    
    # Component validators
    "ContractLoader",
    "SchemaValidator",
    "InterfaceValidator",
    "DataFlowValidator",
    "OntologyContractValidator",
    "ContractEnforcementEngine",
    
    # Main validator
    "ContractValidator",
    
    # Test framework
    "ContractTestFramework",
    
    # Utility functions
    "validate_all_contracts"
]
