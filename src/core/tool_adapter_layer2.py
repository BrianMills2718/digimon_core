"""Layer 2 Tool Adapter - Implements contract-first design from ADR-001

This adapter enables tools to work with the orchestrator by implementing
the proper KGASTool interface and ToolValidationResult compatibility.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import time

from .tool_contract import (
    KGASTool, ToolRequest, ToolResult, ToolValidationResult,
    ConfidenceScore, BaseKGASTool
)
from .service_manager import ServiceManager

logger = logging.getLogger(__name__)


class Layer2ToolAdapter(BaseKGASTool):
    """Adapts existing tools to Layer 2 KGASTool interface.
    
    This adapter implements the contract-first design (ADR-001) for tools
    that don't yet implement the KGASTool interface directly.
    """
    
    def __init__(self, wrapped_tool: Any, service_manager: ServiceManager):
        """Initialize adapter with wrapped tool.
        
        Args:
            wrapped_tool: The existing tool to adapt
            service_manager: Service manager for dependency injection
        """
        # Extract tool metadata
        tool_id = getattr(wrapped_tool, 'tool_id', wrapped_tool.__class__.__name__)
        tool_name = getattr(wrapped_tool, 'name', wrapped_tool.__class__.__name__)
        description = getattr(wrapped_tool, 'description', 'Adapted tool')
        
        super().__init__(
            tool_id=tool_id,
            tool_name=tool_name,
            description=description,
            category="adapted"
        )
        
        self.wrapped_tool = wrapped_tool
        self.service_manager = service_manager
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute wrapped tool with Layer 2 contract interface."""
        start_time = time.time()
        
        try:
            # Validate input using wrapped tool's validation if available
            if hasattr(self.wrapped_tool, 'validate_input'):
                validation_result = self.wrapped_tool.validate_input(request.input_data)
                
                # Handle the validation result properly
                if hasattr(validation_result, 'is_valid') and not validation_result.is_valid:
                    # Get errors from the validation result
                    errors = getattr(validation_result, 'errors', [])
                    error_msg = f"Validation failed: {', '.join(errors)}"
                    return self.create_error_result(request, error_msg)
            
            # Execute the wrapped tool
            if hasattr(self.wrapped_tool, 'execute'):
                # Tool has execute method - use it
                result = self.wrapped_tool.execute(request.input_data)
            elif hasattr(self.wrapped_tool, 'process'):
                # Tool has process method - use it
                result = self.wrapped_tool.process(request.input_data)
            elif callable(self.wrapped_tool):
                # Tool is callable - call it
                result = self.wrapped_tool(request.input_data)
            else:
                raise ValueError(f"Tool {self.tool_id} has no executable method")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create provenance record
            provenance_record = None
            if self.service_manager and hasattr(self.service_manager, 'provenance_service'):
                provenance_record = self.service_manager.provenance_service.create_tool_execution_record(
                    tool_id=self.tool_id,
                    workflow_id=request.workflow_id,
                    input_summary=str(type(request.input_data).__name__),
                    success=True,
                    execution_time=execution_time
                )
            
            # Calculate confidence based on result
            confidence = self._calculate_confidence(result)
            
            # Return standardized ToolResult
            return ToolResult(
                status="success",
                data=result,
                confidence=confidence,
                metadata={
                    "tool_id": self.tool_id,
                    "execution_time": execution_time,
                    "adapted_tool": True
                },
                provenance=provenance_record,
                request_id=request.request_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool {self.tool_id} execution failed: {str(e)}")
            return self.create_error_result(request, str(e), str(e))
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input using wrapped tool's validation or basic checks."""
        if hasattr(self.wrapped_tool, 'validate_input'):
            # Use wrapped tool's validation
            wrapped_result = self.wrapped_tool.validate_input(input_data)
            
            # Convert to ToolValidationResult if needed
            if isinstance(wrapped_result, ToolValidationResult):
                return wrapped_result
            elif hasattr(wrapped_result, 'is_valid'):
                # Create ToolValidationResult from wrapped result
                result = ToolValidationResult(
                    is_valid=wrapped_result.is_valid,
                    errors=getattr(wrapped_result, 'errors', []),
                    warnings=getattr(wrapped_result, 'warnings', [])
                )
                return result
            else:
                # Assume boolean result
                return ToolValidationResult(is_valid=bool(wrapped_result))
        else:
            # Basic validation
            return super().validate_input(input_data)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema from wrapped tool or use default."""
        if hasattr(self.wrapped_tool, 'get_input_schema'):
            return self.wrapped_tool.get_input_schema()
        elif hasattr(self.wrapped_tool, 'input_schema'):
            return self.wrapped_tool.input_schema
        elif hasattr(self.wrapped_tool, 'get_contract'):
            contract = self.wrapped_tool.get_contract()
            if isinstance(contract, dict):
                return contract.get('input_schema', {})
            elif hasattr(contract, 'input_schema'):
                return contract.input_schema
        
        return super().get_input_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema from wrapped tool or use default."""
        if hasattr(self.wrapped_tool, 'get_output_schema'):
            return self.wrapped_tool.get_output_schema()
        elif hasattr(self.wrapped_tool, 'output_schema'):
            return self.wrapped_tool.output_schema
        elif hasattr(self.wrapped_tool, 'get_contract'):
            contract = self.wrapped_tool.get_contract()
            if isinstance(contract, dict):
                return contract.get('output_schema', {})
            elif hasattr(contract, 'output_schema'):
                return contract.output_schema
        
        return super().get_output_schema()
    
    def _calculate_confidence(self, result: Any) -> ConfidenceScore:
        """Calculate confidence score based on result."""
        # Check if result includes confidence
        if isinstance(result, dict) and 'confidence' in result:
            conf_value = result['confidence']
            if isinstance(conf_value, ConfidenceScore):
                return conf_value
            elif isinstance(conf_value, (int, float)):
                return ConfidenceScore.create_high_confidence(
                    value=conf_value,
                    evidence_weight=10
                )
        
        # Default to medium confidence for successful execution
        return ConfidenceScore.create_medium_confidence(
            value=0.7,
            evidence_weight=5
        )


class OrchestratorCompatibilityAdapter:
    """Ensures tools are compatible with the orchestrator's expectations.
    
    This adapter specifically handles the mismatch between what the orchestrator
    expects (validation_errors) and what ToolValidationResult provides (errors).
    """
    
    def __init__(self, tool: Any):
        """Wrap a tool to ensure orchestrator compatibility."""
        self.tool = tool
        
    def __getattr__(self, name):
        """Delegate attribute access to wrapped tool."""
        return getattr(self.tool, name)
    
    def validate_input(self, input_data: Any):
        """Validate input and return orchestrator-compatible result."""
        # Call wrapped tool's validation
        result = self.tool.validate_input(input_data)
        
        # Ensure the result has validation_errors attribute for orchestrator
        if hasattr(result, 'errors') and not hasattr(result, 'validation_errors'):
            result.validation_errors = result.errors
        
        return result


def adapt_tool_for_orchestrator(tool: Any, service_manager: ServiceManager) -> Any:
    """Adapt any tool to be compatible with the orchestrator.
    
    This function applies the necessary adapters to ensure a tool works
    with the sequential_engine orchestrator.
    
    Args:
        tool: The tool to adapt
        service_manager: Service manager for dependency injection
        
    Returns:
        Adapted tool that's compatible with the orchestrator
    """
    # Check if tool already implements KGASTool
    if isinstance(tool, KGASTool):
        # Just ensure orchestrator compatibility
        return OrchestratorCompatibilityAdapter(tool)
    
    # Otherwise, apply full Layer 2 adaptation
    layer2_tool = Layer2ToolAdapter(tool, service_manager)
    return OrchestratorCompatibilityAdapter(layer2_tool)