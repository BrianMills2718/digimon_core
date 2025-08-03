"""
Phase 1 Adapter - Basic GraphRAG Workflow

Adapter for Phase 1 Basic GraphRAG workflow with theory-aware support.
Wraps existing Phase 1 implementation to provide consistent interface.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..graphrag_phase_interface import (
    GraphRAGPhase, PhaseResult, ProcessingRequest, PhaseStatus
)
from .theory_aware_base import TheoryAwareAdapterBase, TheorySchema
from .adapter_utils import AdapterUtils
from ..logging_config import get_logger

logger = logging.getLogger(__name__)


class Phase1Adapter(TheoryAwareAdapterBase, GraphRAGPhase):
    """Adapter for Phase 1 Basic GraphRAG workflow with theory-aware support"""
    
    def __init__(self):
        TheoryAwareAdapterBase.__init__(self, "Phase 1: Basic", "1.0")
        GraphRAGPhase.__init__(self, "Phase 1: Basic", "1.0")
        
        self._workflow = None
        self._workflow_config = None
        self.logger = get_logger("phase1.adapter")
    
    def _get_workflow(self):
        """Lazy load Phase 1 workflow"""
        if self._workflow is None:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.orchestration.pipeline_orchestrator import PipelineConfig
            from src.core.orchestration.pipeline_orchestrator import Phase as PipelinePhase, OptimizationLevel as PipelineOptLevel
            from src.core.config_manager import get_config
            from src.core.tool_factory import create_unified_workflow_config
            from src.core.tool_management.workflow_config import Phase, OptimizationLevel
            
            config_manager = get_config()
            workflow_config_dict = create_unified_workflow_config(
                phase=Phase.PHASE1, 
                optimization_level=OptimizationLevel.STANDARD
            )
            
            # Convert dict to PipelineConfig
            tools = workflow_config_dict.get('tools', [])
            self._workflow_config = PipelineConfig(
                tools=tools,
                phase=PipelinePhase.PHASE1,
                optimization_level=PipelineOptLevel.STANDARD
            )
            self._workflow = PipelineOrchestrator(self._workflow_config, config_manager)
        
        return self._workflow
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Phase 1 capabilities"""
        return {
            "supported_document_types": ["pdf"],
            "required_services": ["neo4j", "sqlite"],
            "optional_services": [],
            "max_document_size": 10_000_000,  # 10MB
            "supports_batch_processing": False,
            "supports_multiple_queries": False,
            "uses_ontology": False,
            "theory_aware": True,
            "supported_theory_schemas": [str(schema) for schema in self.get_supported_theory_schemas()]
        }
    
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """Validate Phase 1 input requirements"""
        errors: List[str] = []
        
        # Validate documents
        if not request.documents:
            errors.append("Phase 1 requires at least one document")
        elif len(request.documents) > 1:
            errors.append("Phase 1 only supports single document processing")
        else:
            # Validate document paths
            doc_errors = AdapterUtils.validate_document_paths(request.documents)
            errors.extend(doc_errors)
            
            # Check PDF format specifically for Phase 1
            for doc_path in request.documents:
                if Path(doc_path).suffix.lower() != '.pdf':
                    errors.append("Phase 1 only supports PDF documents")
        
        # Validate queries
        if not request.queries:
            errors.append("Phase 1 requires at least one query")
        elif len(request.queries) > 1:
            errors.append("Phase 1 only supports single query processing")
        else:
            query_errors = AdapterUtils.validate_queries(request.queries)
            errors.extend(query_errors)
        
        # Validate workflow ID
        if hasattr(request, 'workflow_id') and request.workflow_id:
            workflow_error = AdapterUtils.validate_workflow_id(request.workflow_id)
            if workflow_error:
                errors.append(workflow_error)
        
        return errors
    
    def get_supported_theory_schemas(self) -> List[TheorySchema]:
        """Return list of supported theory schemas for Phase 1"""
        return [TheorySchema.MASTER_CONCEPTS, TheorySchema.ORM_METHODOLOGY]
    
    def _execute_original(self, request: ProcessingRequest) -> PhaseResult:
        """Execute Phase 1 workflow with original adapter translation"""
        context = AdapterUtils.create_execution_context("Phase 1", 
                                                        getattr(request, 'workflow_id', 'phase1_exec'))
        
        AdapterUtils.log_adapter_operation("Phase1Adapter", "execute_original", context)
        
        try:
            # Validate input
            errors = self.validate_input(request)
            if errors:
                error_msg = f"Validation failed: {'; '.join(errors)}"
                AdapterUtils.log_adapter_operation("Phase1Adapter", "execute_original", context, error=Exception(error_msg))
                return self.create_error_result(error_msg)
            
            workflow = self._get_workflow()
            
            # Execute workflow using PipelineOrchestrator
            result = workflow.execute(
                document_paths=request.documents,
                queries=request.queries
            )
            
            # Extract results with error handling
            final_result = result.get("final_result", {})
            entities = final_result.get("entities", [])
            relationships = final_result.get("relationships", [])
            query_results = final_result.get("query_results", [])
            
            # Calculate metrics
            metrics = AdapterUtils.calculate_execution_metrics(
                context,
                entities_count=len(entities),
                relationships_count=len(relationships),
                documents_processed=len(request.documents),
                queries_answered=len(query_results)
            )
            
            phase_result = PhaseResult(
                status=PhaseStatus.SUCCESS,
                phase_name="Phase 1",
                execution_time=metrics["execution_time_seconds"],
                entity_count=metrics["entities_created"],
                relationship_count=metrics["relationships_created"],
                confidence_score=metrics.get("confidence_score", 0.8),
                results={
                    "entities_extracted": len(entities),
                    "relationships_found": len(relationships),
                    "queries_processed": len(request.queries),
                    "documents_processed": len(request.documents),
                    "documents_processed_count": metrics["documents_processed"],
                    "queries_answered_count": metrics["queries_answered"],
                    "throughput": metrics["throughput"],
                    "efficiency": metrics["efficiency"],
                    "query_results": query_results
                }
            )
            
            AdapterUtils.log_adapter_operation("Phase1Adapter", "execute_original", context, result=metrics)
            return phase_result
                
        except Exception as e:
            error_msg = AdapterUtils.sanitize_error_message(e)
            self.logger.error(f"Phase 1 adapter error: {error_msg}")
            AdapterUtils.log_adapter_operation("Phase1Adapter", "execute_original", context, error=e)
            
            execution_time = time.time() - context["start_time"]
            return self.create_error_result(f"Phase 1 adapter error: {error_msg}", execution_time)
    
    def _create_theory_guided_workflow(self, theory_schema: Any) -> Any:
        """Create workflow that uses theory to guide extraction"""
        try:
            from src.tools.phase1.theory_guided_workflow import TheoryGuidedWorkflow  # type: ignore[import-not-found]
            from src.core.config_manager import get_config
            
            config_manager = get_config()
            return TheoryGuidedWorkflow(
                config_manager=config_manager,
                theory_schema=theory_schema
            )
        except ImportError:
            # Fallback to regular workflow if theory-guided not available
            self.logger.warning("Theory-guided workflow not available, falling back to regular workflow")
            return self._get_workflow()
    
    def _execute_with_theory_guidance(self, workflow: Any, request, theory_schema: Any) -> Any:
        """Execute workflow with theory guidance for Phase 1"""
        try:
            # Try theory-guided execution first
            if hasattr(workflow, 'execute_with_theory_guidance'):
                return workflow.execute_with_theory_guidance(
                    document_paths=request.documents,
                    queries=request.queries,
                    theory_schema=theory_schema,
                    concept_library=getattr(workflow, 'concept_library', None)
                )
            else:
                # Fallback to regular execution
                self.logger.warning("Workflow does not support theory guidance, using regular execution")
                result = workflow.execute(
                    document_paths=request.documents,
                    queries=request.queries
                )
                
                # Add theory metadata to regular result
                if hasattr(result, 'final_result'):
                    final_result = result.final_result
                    # Add theory alignment score
                    final_result['theory_alignment_score'] = 0.7  # Default score
                    final_result['concept_usage'] = {}
                    final_result['theory_metadata'] = {
                        "schema_type": str(theory_schema),
                        "theory_guided": False,
                        "fallback_execution": True
                    }
                
                return result
                
        except Exception as e:
            self.logger.error(f"Theory-guided execution failed: {e}")
            # Fallback to regular execution
            result = workflow.execute(
                document_paths=request.documents,
                queries=request.queries
            )
            return result
    
    def get_phase1_specific_info(self) -> Dict[str, Any]:
        """Get Phase 1 specific adapter information"""
        return {
            "workflow_loaded": self._workflow is not None,
            "supports_pdf_only": True,
            "single_document_processing": True,
            "single_query_processing": True,
            "basic_graphrag": True,
            "neo4j_required": True,
            "sqlite_required": True
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of Phase 1 adapter and dependencies"""
        issues_list: List[str] = []
        health_status: Dict[str, Any] = {
            "adapter_healthy": True,
            "issues": issues_list
        }
        
        try:
            # Check if workflow can be created
            workflow = self._get_workflow()
            if workflow is None:
                health_status["adapter_healthy"] = False
                issues_list.append("Cannot create Phase 1 workflow")
            
            # Check theory capabilities
            theory_caps = self.get_theory_capabilities()
            health_status["theory_support"] = theory_caps
            
        except Exception as e:
            health_status["adapter_healthy"] = False
            issues_list.append(f"Health check failed: {AdapterUtils.sanitize_error_message(e)}")
        
        return health_status
    
    def cleanup(self) -> bool:
        """Clean up Phase 1 adapter resources"""
        try:
            if self._workflow and hasattr(self._workflow, 'cleanup'):
                self._workflow.cleanup()
            
            self._workflow = None
            self._workflow_config = None
            return True
            
        except Exception as e:
            self.logger.error(f"Phase 1 adapter cleanup failed: {e}")
            return False