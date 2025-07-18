"""
GraphRAG Phase Interface - Standardized contract for all processing phases

This module defines the base interface that all GraphRAG phases must implement
to ensure consistent integration and prevent API compatibility issues.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class PhaseStatus(Enum):
    """Standard status codes for phase execution"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    RUNNING = "running"


@dataclass
class PhaseResult:
    """Standard result structure for all phases"""
    status: PhaseStatus
    phase_name: str
    execution_time: float
    entity_count: int
    relationship_count: int
    confidence_score: float
    error_message: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    
    # Phase-specific results (flexible)
    results: Optional[Dict[str, Any]] = None


@dataclass
class ProcessingRequest:
    """Standard input structure for phase processing"""
    # Core inputs (all phases)
    documents: List[str]  # File paths or text content
    queries: List[str]    # Questions to answer
    workflow_id: str      # Unique identifier for tracking
    
    # Phase-specific inputs (optional)
    domain_description: Optional[str] = None      # Phase 2+
    existing_ontology: Optional[str] = None       # Phase 2+
    fusion_strategy: Optional[str] = None         # Phase 3+
    
    # Processing options
    confidence_threshold: float = 0.7
    max_entities: Optional[int] = None
    use_mock_apis: bool = False
    
    # Phase integration data (for data flow between phases)
    phase1_graph_data: Optional[Dict[str, Any]] = None    # P1 results for P2/P3
    phase2_enhanced_data: Optional[Dict[str, Any]] = None # P2 results for P3


class GraphRAGPhase(ABC):
    """
    Base interface for all GraphRAG processing phases.
    
    This contract ensures:
    1. Consistent method signatures across phases
    2. Standardized input/output formats
    3. Uniform error handling and status reporting
    4. Integration compatibility
    """
    
    def __init__(self, phase_name: str, phase_version: str = "1.0"):
        """Initialize phase with identification"""
        self.phase_name = phase_name
        self.phase_version = phase_version
        self._validate_phase_name()
    
    def _validate_phase_name(self):
        """Validate that phase name follows expected format"""
        valid_phases = ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"]
        if not any(self.phase_name.startswith(valid.split(':')[0]) for valid in valid_phases):
            raise ValueError(f"Invalid phase name: {self.phase_name}")
    
    @abstractmethod
    def execute(self, request: ProcessingRequest) -> PhaseResult:
        """
        Execute the phase processing.
        
        Args:
            request: Standardized processing request
            
        Returns:
            PhaseResult with standardized structure
            
        Raises:
            ValueError: For invalid input parameters
            RuntimeError: For processing failures
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return phase capabilities and requirements.
        
        Returns:
            Dict containing:
            - supported_document_types: List[str]
            - required_services: List[str] 
            - optional_services: List[str]
            - max_document_size: int
            - supports_batch_processing: bool
        """
        pass
    
    @abstractmethod
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """
        Validate input request for this phase.
        
        Args:
            request: Processing request to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    def get_phase_info(self) -> Dict[str, str]:
        """Get basic phase information"""
        return {
            "name": self.phase_name,
            "version": self.phase_version,
            "interface_version": "1.0"
        }
    
    def create_error_result(self, error_message: str, execution_time: float = 0.0) -> PhaseResult:
        """Helper to create standardized error results"""
        return PhaseResult(
            status=PhaseStatus.ERROR,
            phase_name=self.phase_name,
            execution_time=execution_time,
            entity_count=0,
            relationship_count=0,
            confidence_score=0.0,
            error_message=error_message
        )
    
    def create_success_result(
        self, 
        execution_time: float,
        entity_count: int,
        relationship_count: int,
        confidence_score: float,
        results: Optional[Dict[str, Any]] = None
    ) -> PhaseResult:
        """Helper to create standardized success results"""
        return PhaseResult(
            status=PhaseStatus.SUCCESS,
            phase_name=self.phase_name,
            execution_time=execution_time,
            entity_count=entity_count,
            relationship_count=relationship_count,
            confidence_score=confidence_score,
            results=results or {}
        )


class PhaseRegistry:
    """Registry for managing available phases"""
    
    def __init__(self):
        self._phases: Dict[str, GraphRAGPhase] = {}
    
    def register_phase(self, phase: GraphRAGPhase):
        """Register a phase implementation"""
        if not isinstance(phase, GraphRAGPhase):
            raise TypeError("Phase must implement GraphRAGPhase interface")
        
        self._phases[phase.phase_name] = phase
    
    def get_phase(self, phase_name: str) -> Optional[GraphRAGPhase]:
        """Get a registered phase by name"""
        return self._phases.get(phase_name)
    
    def list_phases(self) -> List[str]:
        """List all registered phase names"""
        return list(self._phases.keys())
    
    def validate_all_phases(self) -> Dict[str, List[str]]:
        """Validate all registered phases with sample input"""
        sample_request = ProcessingRequest(
            documents=["test.pdf"],
            queries=["Test query"],
            workflow_id="validation_test"
        )
        
        validation_results = {}
        for name, phase in self._phases.items():
            try:
                errors = phase.validate_input(sample_request)
                validation_results[name] = errors
            except Exception as e:
                validation_results[name] = [f"Validation failed: {str(e)}"]
        
        return validation_results


# Global phase registry instance
phase_registry = PhaseRegistry()


def register_phase(phase: GraphRAGPhase):
    """Convenience function to register a phase"""
    phase_registry.register_phase(phase)


def get_available_phases() -> List[str]:
    """Get list of all available phases"""
    return phase_registry.list_phases()


def execute_phase(phase_name: str, request: ProcessingRequest) -> PhaseResult:
    """Execute a phase by name"""
    phase = phase_registry.get_phase(phase_name)
    if not phase:
        raise ValueError(f"Phase not found: {phase_name}")
    
    return phase.execute(request)