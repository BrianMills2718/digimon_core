"""
Phase Adapters - Bridge existing phase implementations to the standard interface

These adapters wrap existing phase implementations to provide a consistent
interface without requiring massive refactoring of working code.
"""

import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from .graphrag_phase_interface import (
    GraphRAGPhase, PhaseResult, ProcessingRequest, PhaseStatus, register_phase
)


class Phase1Adapter(GraphRAGPhase):
    """Adapter for Phase 1 Basic GraphRAG workflow"""
    
    def __init__(self):
        super().__init__("Phase 1: Basic", "1.0")
        self._workflow = None
    
    def _get_workflow(self):
        """Lazy load Phase 1 workflow to avoid import issues"""
        if self._workflow is None:
            from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
            self._workflow = VerticalSliceWorkflow()
        return self._workflow
    
    def execute(self, request: ProcessingRequest) -> PhaseResult:
        """Execute Phase 1 workflow with adapter translation"""
        start_time = time.time()
        
        try:
            # Validate input
            errors = self.validate_input(request)
            if errors:
                return self.create_error_result(f"Validation failed: {'; '.join(errors)}")
            
            workflow = self._get_workflow()
            
            # Phase 1 only handles single document and single query
            pdf_path = request.documents[0] if request.documents else ""
            query = request.queries[0] if request.queries else ""
            
            # Execute original Phase 1 workflow
            result = workflow.execute_workflow(
                pdf_path=pdf_path,
                query=query,
                workflow_name=request.workflow_id
            )
            
            execution_time = time.time() - start_time
            
            # Translate result to standard format
            if result.get("status") == "success":
                return self.create_success_result(
                    execution_time=execution_time,
                    entity_count=result.get("entity_count", 0),
                    relationship_count=result.get("relationship_count", 0),
                    confidence_score=result.get("average_confidence", 0.0),
                    results={
                        "graph_metrics": result.get("graph_metrics", {}),
                        "query_result": result.get("query_result", {}),
                        "phase1_raw": result  # Include original for debugging
                    }
                )
            else:
                return self.create_error_result(
                    result.get("error", "Phase 1 execution failed"),
                    execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return self.create_error_result(f"Phase 1 adapter error: {str(e)}", execution_time)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Phase 1 capabilities"""
        return {
            "supported_document_types": ["pdf"],
            "required_services": ["neo4j", "sqlite"],
            "optional_services": [],
            "max_document_size": 10_000_000,  # 10MB
            "supports_batch_processing": False,
            "supports_multiple_queries": False,
            "uses_ontology": False
        }
    
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """Validate Phase 1 input requirements"""
        errors = []
        
        if not request.documents:
            errors.append("Phase 1 requires at least one document")
        elif len(request.documents) > 1:
            errors.append("Phase 1 only supports single document processing")
        
        if not request.queries:
            errors.append("Phase 1 requires at least one query")
        elif len(request.queries) > 1:
            errors.append("Phase 1 only supports single query processing")
        
        # Check if document exists
        if request.documents:
            doc_path = Path(request.documents[0])
            if not doc_path.exists():
                errors.append(f"Document not found: {request.documents[0]}")
            elif not doc_path.suffix.lower() == '.pdf':
                errors.append("Phase 1 only supports PDF documents")
        
        return errors


class Phase2Adapter(GraphRAGPhase):
    """Adapter for Phase 2 Enhanced GraphRAG workflow"""
    
    def __init__(self):
        super().__init__("Phase 2: Enhanced", "1.0")
        self._workflow = None
    
    def _get_workflow(self):
        """Lazy load Phase 2 workflow to avoid import issues"""
        if self._workflow is None:
            from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
            self._workflow = EnhancedVerticalSliceWorkflow()
        return self._workflow
    
    def execute(self, request: ProcessingRequest) -> PhaseResult:
        """Execute Phase 2 workflow with adapter translation"""
        start_time = time.time()
        
        try:
            # Validate input
            errors = self.validate_input(request)
            if errors:
                return self.create_error_result(f"Validation failed: {'; '.join(errors)}")
            
            workflow = self._get_workflow()
            
            # Phase 2 handles single document but multiple queries
            pdf_path = request.documents[0] if request.documents else ""
            domain_description = request.domain_description or "General domain analysis"
            
            # Execute original Phase 2 workflow
            result = workflow.execute_enhanced_workflow(
                pdf_path=pdf_path,
                domain_description=domain_description,
                queries=request.queries,
                workflow_name=request.workflow_id,
                use_existing_ontology=request.existing_ontology
            )
            
            execution_time = time.time() - start_time
            
            # Translate result to standard format
            if result.get("status") == "success":
                return self.create_success_result(
                    execution_time=execution_time,
                    entity_count=result.get("entity_count", 0),
                    relationship_count=result.get("relationship_count", 0),
                    confidence_score=result.get("average_confidence", 0.0),
                    results={
                        "ontology_info": result.get("ontology_info", {}),
                        "graph_metrics": result.get("graph_metrics", {}),
                        "query_results": result.get("query_results", {}),
                        "visualizations": result.get("visualizations", {}),
                        "phase2_raw": result  # Include original for debugging
                    }
                )
            else:
                return self.create_error_result(
                    result.get("error", "Phase 2 execution failed"),
                    execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return self.create_error_result(f"Phase 2 adapter error: {str(e)}", execution_time)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Phase 2 capabilities"""
        return {
            "supported_document_types": ["pdf"],
            "required_services": ["neo4j", "sqlite", "openai", "google"],
            "optional_services": ["qdrant"],
            "max_document_size": 10_000_000,  # 10MB
            "supports_batch_processing": False,
            "supports_multiple_queries": True,
            "uses_ontology": True,
            "requires_domain_description": True
        }
    
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """Validate Phase 2 input requirements"""
        errors = []
        
        if not request.documents:
            errors.append("Phase 2 requires at least one document")
        elif len(request.documents) > 1:
            errors.append("Phase 2 only supports single document processing")
        
        if not request.queries:
            errors.append("Phase 2 requires at least one query")
        
        if not request.domain_description:
            errors.append("Phase 2 requires domain_description for ontology generation")
        
        # Check if document exists
        if request.documents:
            doc_path = Path(request.documents[0])
            if not doc_path.exists():
                errors.append(f"Document not found: {request.documents[0]}")
            elif not doc_path.suffix.lower() == '.pdf':
                errors.append("Phase 2 only supports PDF documents")
        
        return errors


class Phase3Adapter(GraphRAGPhase):
    """Adapter for Phase 3 Multi-Document workflow (placeholder for future implementation)"""
    
    def __init__(self):
        super().__init__("Phase 3: Multi-Document", "1.0")
    
    def execute(self, request: ProcessingRequest) -> PhaseResult:
        """Phase 3 is not yet fully implemented"""
        return self.create_error_result("Phase 3 multi-document workflow not yet implemented")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Phase 3 planned capabilities"""
        return {
            "supported_document_types": ["pdf", "docx", "txt", "html"],
            "required_services": ["neo4j", "sqlite", "openai", "google"],
            "optional_services": ["qdrant"],
            "max_document_size": 50_000_000,  # 50MB
            "supports_batch_processing": True,
            "supports_multiple_queries": True,
            "uses_ontology": True,
            "supports_multi_document": True,
            "fusion_strategies": ["horizontal", "vertical", "semantic"]
        }
    
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """Validate Phase 3 input requirements"""
        return ["Phase 3 is not yet implemented"]


def initialize_phase_adapters():
    """Register all phase adapters with the global registry"""
    try:
        # Register Phase 1
        phase1 = Phase1Adapter()
        register_phase(phase1)
        print("✓ Phase 1 adapter registered")
        
        # Register Phase 2
        phase2 = Phase2Adapter()
        register_phase(phase2)
        print("✓ Phase 2 adapter registered")
        
        # Register Phase 3 (placeholder)
        phase3 = Phase3Adapter()
        register_phase(phase3)
        print("✓ Phase 3 adapter registered (placeholder)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize phase adapters: {e}")
        return False


if __name__ == "__main__":
    # Test adapter initialization
    success = initialize_phase_adapters()
    if success:
        from .graphrag_phase_interface import get_available_phases
        print(f"\nAvailable phases: {get_available_phases()}")
    else:
        print("Adapter initialization failed")