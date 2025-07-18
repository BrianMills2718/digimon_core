"""Bridge between existing tools and contract validation system"""

from typing import Dict, Any, List
import logging
from .contract_validator import ContractValidator
from .ontology_validator import OntologyValidator

class ToolAdapterBridge:
    """Wraps existing tools with contract validation"""
    
    def __init__(self, contracts_dir: str = "contracts/contracts/tools/"):
        self.contract_validator = ContractValidator(contracts_dir)
        self.ontology_validator = OntologyValidator()
        self.logger = logging.getLogger(__name__)
    
    def execute_with_validation(self, tool_name: str, tool_instance: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with contract validation"""
        
        # Pre-execution validation
        try:
            self.contract_validator.validate_input(tool_name, input_data)
            self.logger.info(f"Input validation passed for {tool_name}")
        except Exception as e:
            self.logger.warning(f"Input validation failed for {tool_name}: {e}")
        
        # Execute original tool using the _execute_original method
        if hasattr(tool_instance, '_execute_original'):
            result = tool_instance._execute_original(input_data)
        else:
            # Fallback to normal execution if no validation wrapper exists
            result = tool_instance.execute(input_data)
        
        # Post-execution validation
        try:
            self.contract_validator.validate_output(tool_name, result)
            self.logger.info(f"Output validation passed for {tool_name}")
        except Exception as e:
            self.logger.warning(f"Output validation failed for {tool_name}: {e}")
        
        return result