"""
UI Phase Adapter - Interface between Streamlit UI and GraphRAG Phase Interface

This adapter provides a clean interface for the UI to interact with any GraphRAG phase
without needing to know the specific implementation details of each phase.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from src.core.graphrag_phase_interface import (
    ProcessingRequest, PhaseResult, PhaseStatus, 
    get_available_phases, execute_phase, phase_registry
)
from src.core.phase_adapters import initialize_phase_adapters


@dataclass
class UIProcessingResult:
    """UI-friendly result structure"""
    # Basic info
    filename: str
    phase_name: str
    status: str  # "success", "error", "partial"
    processing_time: float
    
    # Core metrics
    entity_count: int
    relationship_count: int
    confidence_score: float
    
    # Error info
    error_message: Optional[str] = None
    
    # Detailed results (for visualization)
    graph_data: Optional[Dict[str, Any]] = None
    query_results: Optional[List[Dict[str, Any]]] = None
    visualizations: Optional[Dict[str, Any]] = None
    
    # Phase-specific data
    phase_specific_data: Optional[Dict[str, Any]] = None


class UIPhaseManager:
    """Manages phase selection and execution for the UI"""
    
    def __init__(self):
        self._initialized = False
        self._available_phases = []
        self._phase_capabilities = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize the phase system"""
        try:
            # Initialize phase adapters
            success = initialize_phase_adapters()
            if not success:
                raise RuntimeError("Failed to initialize phase adapters")
            
            # Get available phases
            self._available_phases = get_available_phases()
            
            # Cache phase capabilities
            for phase_name in self._available_phases:
                phase = phase_registry.get_phase(phase_name)
                if phase:
                    self._phase_capabilities[phase_name] = phase.get_capabilities()
            
            self._initialized = True
            print(f"✅ UI Phase Manager initialized with {len(self._available_phases)} phases")
            
        except Exception as e:
            print(f"❌ UI Phase Manager initialization failed: {e}")
            self._initialized = False
    
    def is_initialized(self) -> bool:
        """Check if the manager is properly initialized"""
        return self._initialized
    
    def get_available_phases(self) -> List[str]:
        """Get list of available phase names"""
        return self._available_phases.copy()
    
    def get_phase_capabilities(self, phase_name: str) -> Dict[str, Any]:
        """Get capabilities for a specific phase"""
        return self._phase_capabilities.get(phase_name, {})
    
    def validate_phase_input(
        self, 
        phase_name: str, 
        documents: List[str], 
        queries: List[str],
        domain_description: Optional[str] = None
    ) -> List[str]:
        """Validate input for a specific phase"""
        if not self._initialized:
            return ["Phase manager not initialized"]
        
        if phase_name not in self._available_phases:
            return [f"Phase not available: {phase_name}"]
        
        # Create request for validation
        request = ProcessingRequest(
            documents=documents,
            queries=queries,
            workflow_id="validation_test",
            domain_description=domain_description
        )
        
        phase = phase_registry.get_phase(phase_name)
        if phase:
            return phase.validate_input(request)
        else:
            return [f"Phase not found: {phase_name}"]
    
    def process_document(
        self,
        phase_name: str,
        file_path: str,
        filename: str,
        queries: List[str],
        domain_description: Optional[str] = None,
        **kwargs
    ) -> UIProcessingResult:
        """Process a single document using the specified phase"""
        
        if not self._initialized:
            return UIProcessingResult(
                filename=filename,
                phase_name=phase_name,
                status="error",
                processing_time=0.0,
                entity_count=0,
                relationship_count=0,
                confidence_score=0.0,
                error_message="Phase manager not initialized"
            )
        
        start_time = time.time()
        
        try:
            # Create processing request
            request = ProcessingRequest(
                documents=[file_path],
                queries=queries,
                workflow_id=f"ui_{filename}_{int(time.time())}",
                domain_description=domain_description,
                **kwargs
            )
            
            # Validate input
            validation_errors = self.validate_phase_input(
                phase_name, request.documents, request.queries, domain_description
            )
            
            if validation_errors:
                return UIProcessingResult(
                    filename=filename,
                    phase_name=phase_name,
                    status="error",
                    processing_time=time.time() - start_time,
                    entity_count=0,
                    relationship_count=0,
                    confidence_score=0.0,
                    error_message=f"Validation failed: {'; '.join(validation_errors)}"
                )
            
            # Execute phase
            result = execute_phase(phase_name, request)
            
            # Convert to UI result
            return self._convert_phase_result(result, filename)
            
        except Exception as e:
            processing_time = time.time() - start_time
            return UIProcessingResult(
                filename=filename,
                phase_name=phase_name,
                status="error",
                processing_time=processing_time,
                entity_count=0,
                relationship_count=0,
                confidence_score=0.0,
                error_message=f"Processing failed: {str(e)}"
            )
    
    def _convert_phase_result(self, phase_result: PhaseResult, filename: str) -> UIProcessingResult:
        """Convert PhaseResult to UIProcessingResult"""
        
        # Extract visualization data if available
        graph_data = None
        query_results = None
        visualizations = None
        
        if phase_result.results:
            # Try to extract common visualization data
            graph_data = phase_result.results.get("graph_metrics")
            query_results = phase_result.results.get("query_results", [])
            if not isinstance(query_results, list):
                query_results = [query_results] if query_results else []
            
            visualizations = phase_result.results.get("visualizations")
        
        return UIProcessingResult(
            filename=filename,
            phase_name=phase_result.phase_name,
            status=phase_result.status.value,
            processing_time=phase_result.execution_time,
            entity_count=phase_result.entity_count,
            relationship_count=phase_result.relationship_count,
            confidence_score=phase_result.confidence_score,
            error_message=phase_result.error_message,
            graph_data=graph_data,
            query_results=query_results,
            visualizations=visualizations,
            phase_specific_data=phase_result.results
        )
    
    def get_phase_requirements(self, phase_name: str) -> Dict[str, Any]:
        """Get user-friendly requirements for a phase"""
        capabilities = self.get_phase_capabilities(phase_name)
        
        requirements = {
            "supported_files": capabilities.get("supported_document_types", ["pdf"]),
            "requires_domain": capabilities.get("requires_domain_description", False),
            "supports_multiple_queries": capabilities.get("supports_multiple_queries", False),
            "required_services": capabilities.get("required_services", []),
            "max_file_size": capabilities.get("max_document_size", 10_000_000)
        }
        
        return requirements


# Global UI phase manager instance
ui_phase_manager = UIPhaseManager()


def get_ui_phase_manager() -> UIPhaseManager:
    """Get the global UI phase manager instance"""
    return ui_phase_manager


def process_document_with_phase(
    phase_name: str,
    file_path: str, 
    filename: str,
    queries: List[str],
    domain_description: Optional[str] = None
) -> UIProcessingResult:
    """Convenience function for processing a document"""
    manager = get_ui_phase_manager()
    return manager.process_document(
        phase_name=phase_name,
        file_path=file_path,
        filename=filename,
        queries=queries,
        domain_description=domain_description
    )


def get_available_ui_phases() -> List[str]:
    """Get list of phases available in the UI"""
    manager = get_ui_phase_manager()
    return manager.get_available_phases()


def validate_ui_phase_input(
    phase_name: str,
    documents: List[str],
    queries: List[str],
    domain_description: Optional[str] = None
) -> List[str]:
    """Validate input for UI phase processing"""
    manager = get_ui_phase_manager()
    return manager.validate_phase_input(phase_name, documents, queries, domain_description)