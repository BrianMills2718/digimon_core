"""Base adapter class for tool contract enforcement and ontology validation."""

import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import logging

from ..core.data_models import BaseObject
from ..core.contract_validator import ContractValidator
from ..core.ontology_validator import OntologyValidator


class BaseToolAdapter(ABC):
    """Base class for tool adapters that enforce contracts and ontology validation."""
    
    def __init__(self, tool_name: str, contract_type: str = "tool"):
        self.tool_name = tool_name
        self.contract_type = contract_type
        self.logger = logging.getLogger(f"adapter.{tool_name}")
        
        # Initialize validators
        self.contract_validator = ContractValidator()
        self.ontology_validator = OntologyValidator()
        
        # Load contract
        self.contract = self.contract_validator.load_contract(tool_name, contract_type)
        if not self.contract:
            raise ValueError(f"Contract not found for {tool_name}")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with full validation pipeline."""
        start_time = time.time()
        
        try:
            # 1. Validate input against contract
            self.logger.info(f"Validating input for {self.tool_name}")
            input_valid, input_errors = self.contract_validator.validate_input(
                self.tool_name, input_data, self.contract_type
            )
            
            if not input_valid:
                return self._create_error_response(
                    "Input validation failed",
                    {"validation_errors": input_errors},
                    time.time() - start_time
                )
            
            # 2. Execute the actual tool logic
            self.logger.info(f"Executing {self.tool_name}")
            result = self._execute_tool_logic(input_data)
            
            # 3. Apply ontology validation/enrichment if applicable
            if self._should_apply_ontology_validation():
                self.logger.info(f"Applying ontology validation for {self.tool_name}")
                result = self._apply_ontology_validation(result)
            
            # 4. Add execution metadata
            execution_time = time.time() - start_time
            result = self._add_execution_metadata(result, execution_time)
            
            # 5. Validate output against contract
            self.logger.info(f"Validating output for {self.tool_name}")
            output_valid, output_errors = self.contract_validator.validate_output(
                self.tool_name, result, self.contract_type
            )
            
            if not output_valid:
                return self._create_error_response(
                    "Output validation failed",
                    {"validation_errors": output_errors},
                    execution_time
                )
            
            self.logger.info(f"{self.tool_name} executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing {self.tool_name}: {str(e)}")
            return self._create_error_response(
                f"Execution error: {str(e)}",
                {"exception_type": type(e).__name__},
                time.time() - start_time
            )
    
    @abstractmethod
    def _execute_tool_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual tool logic. Must be implemented by subclasses."""
        pass
    
    def _should_apply_ontology_validation(self) -> bool:
        """Check if this tool should apply ontology validation."""
        # Check if contract has ontology_integration section
        return "ontology_integration" in self.contract
    
    def _apply_ontology_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ontology validation to the result. Override in subclasses as needed."""
        return result
    
    def _add_execution_metadata(self, result: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
        """Add standard execution metadata to result."""
        if "execution_metadata" not in result:
            result["execution_metadata"] = {}
        
        result["execution_metadata"].update({
            "tool_name": self.tool_name,
            "execution_time": execution_time,
            "adapter_version": "1.0",
            "validation_applied": True
        })
        
        return result
    
    def _create_error_response(self, error_message: str, error_details: Dict[str, Any], 
                              execution_time: float) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "status": "error",
            "error": error_message,
            "error_details": error_details,
            "execution_metadata": {
                "tool_name": self.tool_name,
                "execution_time": execution_time,
                "adapter_version": "1.0",
                "validation_applied": True
            }
        }
    
    def _generate_id(self) -> str:
        """Generate UUID for entities/relationships."""
        return str(uuid.uuid4())