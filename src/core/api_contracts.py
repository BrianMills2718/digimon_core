"""API Contracts - Standard Interface Definitions

Defines standard interfaces for all GraphRAG phases to ensure consistency
and prevent parameter naming mismatches that cause integration failures.

Addresses API Standardization Debt from TECHNICAL_DEBT_AUDIT.md
"""

from typing import Dict, List, Any, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class DocumentFormat(Enum):
    """Supported document formats."""
    PDF = "pdf"
    TEXT = "txt"
    MARKDOWN = "md"
    DOCX = "docx"


@dataclass
class WorkflowInput:
    """Standardized input for all workflow executions."""
    document_paths: List[str]  # List of document file paths to process
    queries: List[str]         # List of questions to answer
    workflow_id: str           # Unique identifier for workflow tracking
    domain_description: Optional[str] = None    # Domain context for ontology generation
    configuration: Optional[Dict[str, Any]] = None  # Workflow-specific configuration
    metadata: Optional[Dict[str, Any]] = None   # Additional metadata


@dataclass
class WorkflowOutput:
    """Standardized output for all workflow executions."""
    status: str                    # "success" or "error"
    execution_time: float          # Time taken in seconds
    entity_count: int              # Number of entities extracted
    relationship_count: int        # Number of relationships found
    confidence_score: float        # Average confidence score (0.0-1.0)
    results: Dict[str, Any]        # Phase-specific results
    error_message: Optional[str] = None    # Error details if status is "error"
    warnings: Optional[List[str]] = None   # Non-fatal warnings


@dataclass
class WorkflowProgress:
    """Standardized progress tracking for workflow state."""
    workflow_id: str
    step_number: int        # Current step (standardized name, not current_step)
    step_name: str          # Human-readable step description
    status: str             # "pending", "running", "completed", "failed"
    progress_percentage: float  # Progress within current step (0.0-100.0)
    metadata: Optional[Dict[str, Any]] = None


@runtime_checkable
class WorkflowInterface(Protocol):
    """Standard interface that all GraphRAG workflows must implement."""
    
    def execute_workflow(self, input_params: WorkflowInput) -> WorkflowOutput:
        """Execute the workflow with standardized input/output."""
        ...
    
    def validate_input(self, input_params: WorkflowInput) -> List[str]:
        """Validate input parameters and return list of error messages."""
        ...
    
    def get_supported_formats(self) -> List[DocumentFormat]:
        """Return list of supported document formats."""
        ...
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Return workflow metadata (name, version, description, etc.)."""
        ...


@runtime_checkable
class WorkflowStateInterface(Protocol):
    """Standard interface for workflow state management."""
    
    def update_workflow_progress(self, workflow_id: str, step_number: int, status: str) -> Dict[str, Any]:
        """Update workflow progress with standardized parameters."""
        ...
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowProgress]:
        """Get current workflow status."""
        ...
    
    def create_workflow(self, workflow_id: str, total_steps: int) -> Dict[str, Any]:
        """Create new workflow tracking entry."""
        ...


class StandardWorkflowAdapter(ABC):
    """Base adapter that enforces standard interface compliance."""
    
    @abstractmethod
    def get_workflow_info(self) -> Dict[str, Any]:
        """Return workflow metadata."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[DocumentFormat]:
        """Return supported document formats."""
        pass
    
    @abstractmethod
    def validate_input(self, input_params: WorkflowInput) -> List[str]:
        """Validate input and return error messages."""
        pass
    
    @abstractmethod
    def _execute_legacy_workflow(self, input_params: WorkflowInput) -> WorkflowOutput:
        """Execute the underlying legacy workflow implementation."""
        pass
    
    def execute_workflow(self, input_params: WorkflowInput) -> WorkflowOutput:
        """Execute workflow with standard interface validation."""
        # Validate input
        errors = self.validate_input(input_params)
        if errors:
            return WorkflowOutput(
                status="error",
                execution_time=0.0,
                entity_count=0,
                relationship_count=0,
                confidence_score=0.0,
                results={},
                error_message=f"Input validation failed: {'; '.join(errors)}"
            )
        
        # Execute the actual workflow
        return self._execute_legacy_workflow(input_params)


class APIContractValidator:
    """Validates that implementations comply with API contracts."""
    
    @staticmethod
    def validate_workflow_interface(workflow_instance) -> List[str]:
        """Validate that an object implements WorkflowInterface correctly."""
        errors = []
        
        # Check if it implements the protocol (this is often false for duck-typed objects)
        # So we'll check methods directly instead of relying on isinstance
        
        # Check required methods exist and have correct signatures
        required_methods = ['execute_workflow', 'validate_input', 'get_supported_formats', 'get_workflow_info']
        
        for method_name in required_methods:
            if not hasattr(workflow_instance, method_name):
                errors.append(f"Missing required method: {method_name}")
            elif not callable(getattr(workflow_instance, method_name)):
                errors.append(f"Method {method_name} is not callable")
        
        return errors
    
    @staticmethod
    def validate_workflow_state_interface(state_service_instance) -> List[str]:
        """Validate that an object implements WorkflowStateInterface correctly."""
        errors = []
        
        # Check methods directly instead of relying on isinstance for duck-typed objects
        
        # Check method signatures
        required_methods = ['update_workflow_progress', 'get_workflow_status', 'create_workflow']
        
        for method_name in required_methods:
            if not hasattr(state_service_instance, method_name):
                errors.append(f"Missing required method: {method_name}")
        
        return errors
    
    @staticmethod
    def validate_method_signature(obj, method_name: str, expected_params: List[str]) -> List[str]:
        """Validate that a method has the expected parameter names."""
        errors = []
        
        if not hasattr(obj, method_name):
            errors.append(f"Method {method_name} not found")
            return errors
        
        method = getattr(obj, method_name)
        if not callable(method):
            errors.append(f"{method_name} is not callable")
            return errors
        
        # Get method signature
        import inspect
        sig = inspect.signature(method)
        actual_params = list(sig.parameters.keys())
        
        # Remove 'self' parameter for instance methods
        if actual_params and actual_params[0] == 'self':
            actual_params = actual_params[1:]
        
        # Check for required parameters
        for param in expected_params:
            if param not in actual_params:
                errors.append(f"Method {method_name} missing required parameter: {param}")
        
        # Check for deprecated parameters that should be removed
        deprecated_params = ['pdf_path', 'current_step', 'metadata']  # Legacy parameter names
        for param in deprecated_params:
            if param in actual_params:
                errors.append(f"Method {method_name} uses deprecated parameter: {param}")
        
        return errors


# Contract enforcement decorators
def enforce_workflow_contract(cls):
    """Class decorator to enforce WorkflowInterface contract."""
    def wrapper(*args, **kwargs):
        instance = cls(*args, **kwargs)
        errors = APIContractValidator.validate_workflow_interface(instance)
        if errors:
            raise ValueError(f"Workflow contract violation in {cls.__name__}: {'; '.join(errors)}")
        return instance
    return wrapper


def enforce_state_contract(cls):
    """Class decorator to enforce WorkflowStateInterface contract."""
    def wrapper(*args, **kwargs):
        instance = cls(*args, **kwargs)
        errors = APIContractValidator.validate_workflow_state_interface(instance)
        if errors:
            raise ValueError(f"State service contract violation in {cls.__name__}: {'; '.join(errors)}")
        return instance
    return wrapper


# Parameter name mappings for migration
PARAMETER_MIGRATIONS = {
    # Legacy -> Standard
    'pdf_path': 'document_paths',
    'current_step': 'step_number',
    'metadata': 'status',
    'doc_path': 'document_paths',
    'query': 'queries',
    'workflow_name': 'workflow_id'  # Added missing mapping
}


def migrate_legacy_parameters(legacy_params: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy parameter names to standard ones."""
    migrated = {}
    
    for key, value in legacy_params.items():
        # Map legacy parameter names to standard ones
        standard_key = PARAMETER_MIGRATIONS.get(key, key)
        
        # Convert single values to lists where appropriate
        if standard_key == 'document_paths' and isinstance(value, str):
            migrated[standard_key] = [value]
        elif standard_key == 'queries' and isinstance(value, str):
            migrated[standard_key] = [value]
        else:
            migrated[standard_key] = value
    
    return migrated


def create_standard_input(**kwargs) -> WorkflowInput:
    """Create standardized WorkflowInput from various parameter formats."""
    # Migrate legacy parameters
    migrated_params = migrate_legacy_parameters(kwargs)
    
    # Ensure required parameters have defaults
    document_paths = migrated_params.get('document_paths', [])
    queries = migrated_params.get('queries', [])
    workflow_id = migrated_params.get('workflow_id', 'default_workflow')
    
    return WorkflowInput(
        document_paths=document_paths,
        queries=queries,
        workflow_id=workflow_id,
        domain_description=migrated_params.get('domain_description'),
        configuration=migrated_params.get('configuration'),
        metadata=migrated_params.get('metadata')
    )