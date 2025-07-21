"""Tool Contract System - KGASTool Interface Implementation

Implements the standardized KGASTool interface according to ADR-001 Phase Interface Design
to ensure consistency across all 121 tools in the KGAS ecosystem.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import uuid

from .confidence_score import ConfidenceScore


@dataclass(frozen=True)
class TheorySchema:
    """Theory schema specification for theory-aware tools."""
    theory_id: str
    theory_name: str
    domain: str
    ontology_definitions: Dict[str, Any]
    extraction_strategy: str = "LLM_GUIDED"
    validation_rules: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class MasterConceptLibrary:
    """Master concept library for ontology-aware processing."""
    library_id: str
    concepts: Dict[str, Any]
    relationships: Dict[str, Any]
    hierarchies: Dict[str, Any]
    version: str = "1.0.0"


@dataclass(frozen=True)
class ToolRequest:
    """Standardized input request for all KGAS tools."""
    input_data: Any
    theory_schema: Optional[TheorySchema] = None
    concept_library: Optional[MasterConceptLibrary] = None
    options: Dict[str, Any] = field(default_factory=dict)
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ToolResult:
    """Standardized output result for all KGAS tools."""
    status: str  # "success", "error", "warning"
    data: Any
    confidence: ConfidenceScore
    metadata: Dict[str, Any]
    provenance: Any  # Provenance record from provenance service
    request_id: str
    execution_time: float = 0.0
    error_details: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class ToolValidationResult:
    """Result of tool input validation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning."""
        self.warnings.append(warning)
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __str__(self) -> str:
        if self.is_valid:
            return "Valid" + (f" ({len(self.warnings)} warnings)" if self.warnings else "")
        else:
            return f"Invalid ({len(self.errors)} errors)"


class KGASTool(ABC):
    """Abstract base class defining the standard interface for all KGAS tools.
    
    This interface ensures consistency across the 121-tool ecosystem and enables
    seamless integration with the pipeline orchestrator and service manager.
    
    Key principles:
    - Fail-fast validation
    - Comprehensive provenance tracking
    - Confidence-based quality assessment
    - Theory-aware processing support
    """
    
    def __init__(self, tool_id: str, tool_name: str):
        """Initialize the tool with basic identification."""
        self.tool_id = tool_id
        self.tool_name = tool_name
        self._execution_count = 0
        self._total_execution_time = 0.0
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute the tool with standardized input/output.
        
        This is the main entry point for tool execution. Implementations must:
        1. Validate input data using validate_input()
        2. Perform the tool's core functionality
        3. Create comprehensive provenance records
        4. Return standardized ToolResult with confidence scores
        
        Args:
            request: Standardized tool request containing input data and context
            
        Returns:
            ToolResult with execution results, confidence, and provenance
            
        Raises:
            ToolExecutionError: If execution fails with critical error
            ValidationError: If input validation fails
        """
        pass
    
    @abstractmethod
    def get_theory_compatibility(self) -> List[str]:
        """Return list of theory schemas this tool is compatible with.
        
        Returns:
            List of theory_id strings that this tool can process
            Empty list if tool is not theory-aware
        """
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for validating input data.
        
        Returns:
            JSON schema dictionary defining expected input structure
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for validating output data.
        
        Returns:
            JSON schema dictionary defining output data structure
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input data against tool requirements.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            ToolValidationResult indicating validation success/failure
        """
        pass
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Return comprehensive tool metadata and capabilities.
        
        Returns:
            Dictionary containing tool information including:
            - Basic identification (id, name, version)
            - Capabilities and features
            - Performance statistics
            - Theory compatibility
            - Schema definitions
        """
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "tool_class": self.__class__.__name__,
            "version": getattr(self, 'version', '1.0.0'),
            "description": getattr(self, 'description', ''),
            "category": getattr(self, 'category', 'unknown'),
            "theory_compatibility": self.get_theory_compatibility(),
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema(),
            "execution_stats": {
                "execution_count": self._execution_count,
                "total_execution_time": self._total_execution_time,
                "average_execution_time": (
                    self._total_execution_time / self._execution_count 
                    if self._execution_count > 0 else 0.0
                )
            },
            "capabilities": getattr(self, 'capabilities', []),
            "dependencies": getattr(self, 'dependencies', []),
            "resource_requirements": getattr(self, 'resource_requirements', {})
        }
    
    def supports_theory(self, theory_id: str) -> bool:
        """Check if tool supports a specific theory schema."""
        return theory_id in self.get_theory_compatibility()
    
    def update_execution_stats(self, execution_time: float):
        """Update tool execution statistics."""
        self._execution_count += 1
        self._total_execution_time += execution_time
    
    def create_error_result(self, request: ToolRequest, error_message: str, 
                          error_details: Optional[str] = None) -> ToolResult:
        """Create standardized error result."""
        from .service_manager import get_service_manager
        
        # Create minimal provenance for error case
        provenance_service = get_service_manager().provenance_service
        provenance_record = provenance_service.create_tool_execution_record(
            tool_id=self.tool_id,
            workflow_id=request.workflow_id,
            input_summary=str(type(request.input_data).__name__),
            success=False,
            error_message=error_message
        )
        
        return ToolResult(
            status="error",
            data=None,
            confidence=ConfidenceScore.create_low_confidence(value=0.0, evidence_weight=0),
            metadata={
                "tool_id": self.tool_id,
                "error_message": error_message,
                "error_details": error_details,
                "execution_time": 0.0
            },
            provenance=provenance_record,
            request_id=request.request_id,
            execution_time=0.0,
            error_details=error_details
        )


class BaseKGASTool(KGASTool):
    """Base implementation providing common functionality for KGAS tools.
    
    This class provides default implementations for common patterns while
    still requiring tools to implement their core logic.
    """
    
    def __init__(self, tool_id: str, tool_name: str, description: str = "", 
                 category: str = "unknown", version: str = "1.0.0"):
        super().__init__(tool_id, tool_name)
        self.description = description
        self.category = category
        self.version = version
        self.capabilities = []
        self.dependencies = []
        self.resource_requirements = {}
    
    def get_theory_compatibility(self) -> List[str]:
        """Default implementation: no theory compatibility."""
        return []
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Default input schema accepting any data."""
        return {
            "type": "object",
            "properties": {
                "data": {"type": "object"}
            },
            "required": ["data"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Default output schema for tool results."""
        return {
            "type": "object",
            "properties": {
                "result": {"type": "object"},
                "metadata": {"type": "object"}
            },
            "required": ["result"]
        }
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Basic input validation - override for specific requirements."""
        result = ToolValidationResult(True)
        
        if input_data is None:
            result.add_error("Input data cannot be None")
        
        return result


class TheoryAwareKGASTool(BaseKGASTool):
    """Base class for theory-aware tools that integrate with ontology systems."""
    
    def __init__(self, tool_id: str, tool_name: str, supported_theories: List[str],
                 description: str = "", category: str = "theory_aware", version: str = "1.0.0"):
        super().__init__(tool_id, tool_name, description, category, version)
        self.supported_theories = supported_theories
    
    def get_theory_compatibility(self) -> List[str]:
        """Return supported theory schemas."""
        return self.supported_theories
    
    def validate_theory_schema(self, theory_schema: Optional[TheorySchema]) -> ToolValidationResult:
        """Validate theory schema compatibility."""
        result = ToolValidationResult(True)
        
        if theory_schema and theory_schema.theory_id not in self.supported_theories:
            result.add_error(f"Theory {theory_schema.theory_id} not supported by {self.tool_id}")
        
        return result
    
    def extract_ontology_context(self, request: ToolRequest) -> Dict[str, Any]:
        """Extract ontology context from request for theory-aware processing."""
        context = {}
        
        if request.theory_schema:
            context["theory"] = {
                "theory_id": request.theory_schema.theory_id,
                "domain": request.theory_schema.domain,
                "ontology_definitions": request.theory_schema.ontology_definitions,
                "extraction_strategy": request.theory_schema.extraction_strategy
            }
        
        if request.concept_library:
            context["concepts"] = {
                "library_id": request.concept_library.library_id,
                "concepts": request.concept_library.concepts,
                "relationships": request.concept_library.relationships
            }
        
        return context


# Utility functions and decorators
def tool_execution_wrapper(func):
    """Decorator to wrap tool execution with timing and error handling."""
    def wrapper(self, request: ToolRequest) -> ToolResult:
        start_time = datetime.now()
        
        try:
            # Validate input first
            validation_result = self.validate_input(request.input_data)
            if not validation_result.is_valid:
                error_msg = f"Input validation failed: {'; '.join(validation_result.errors)}"
                return self.create_error_result(request, error_msg)
            
            # Execute the actual tool logic
            result = func(self, request)
            
            # Update execution statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.update_execution_stats(execution_time)
            
            # Update result with execution time
            if hasattr(result, 'execution_time'):
                result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Tool execution failed: {str(e)}"
            error_result = self.create_error_result(request, error_msg, str(e))
            error_result.execution_time = execution_time
            return error_result
    
    return wrapper


class ToolExecutionError(Exception):
    """Exception raised when tool execution fails."""
    pass


class ValidationError(Exception):
    """Exception raised when input validation fails."""
    pass


# Tool registry for managing tool instances
class ToolRegistry:
    """Registry for managing tool instances and metadata."""
    
    def __init__(self):
        self._tools: Dict[str, KGASTool] = {}
        self._tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, tool: KGASTool) -> None:
        """Register a tool instance."""
        self._tools[tool.tool_id] = tool
        self._tool_metadata[tool.tool_id] = tool.get_tool_info()
    
    def get_tool(self, tool_id: str) -> Optional[KGASTool]:
        """Get tool instance by ID."""
        return self._tools.get(tool_id)
    
    def list_tools(self) -> List[str]:
        """List all registered tool IDs."""
        return list(self._tools.keys())
    
    def get_tools_by_category(self, category: str) -> List[KGASTool]:
        """Get all tools in a specific category."""
        return [
            tool for tool in self._tools.values()
            if getattr(tool, 'category', 'unknown') == category
        ]
    
    def get_theory_compatible_tools(self, theory_id: str) -> List[KGASTool]:
        """Get all tools compatible with a specific theory."""
        return [
            tool for tool in self._tools.values()
            if tool.supports_theory(theory_id)
        ]
    
    def validate_all_tools(self) -> Dict[str, ToolValidationResult]:
        """Validate all registered tools."""
        results = {}
        for tool_id, tool in self._tools.items():
            # Basic validation - tools should have required methods
            result = ToolValidationResult(True)
            
            required_methods = ['execute', 'get_theory_compatibility', 'get_input_schema', 
                             'get_output_schema', 'validate_input']
            
            for method_name in required_methods:
                if not hasattr(tool, method_name):
                    result.add_error(f"Missing required method: {method_name}")
                elif not callable(getattr(tool, method_name)):
                    result.add_error(f"Method {method_name} is not callable")
            
            results[tool_id] = result
        
        return results


# Global tool registry instance
_global_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _global_tool_registry


def register_tool(tool: KGASTool) -> None:
    """Register a tool in the global registry."""
    _global_tool_registry.register_tool(tool)