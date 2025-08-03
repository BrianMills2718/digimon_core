"""
Phase 3 Adapter - Multi-document Fusion

Adapter for Phase 3 Multi-document fusion workflow.
Builds upon Phase 1 and Phase 2 results to create unified knowledge graphs.
"""

import time
import logging
from typing import Dict, Any, List, Optional

from ..graphrag_phase_interface import (
    GraphRAGPhase, PhaseResult, ProcessingRequest, PhaseStatus
)
from .theory_aware_base import TheoryAwareAdapterBase, TheorySchema
from .adapter_utils import AdapterUtils
from ..logging_config import get_logger

logger = logging.getLogger(__name__)


class Phase3Adapter(TheoryAwareAdapterBase, GraphRAGPhase):
    """Adapter for Phase 3 Multi-document fusion workflow"""
    
    def __init__(self):
        TheoryAwareAdapterBase.__init__(self, "Phase 3: Fusion", "1.0")
        GraphRAGPhase.__init__(self, "Phase 3: Fusion", "1.0")
        
        self._workflow = None
        self._workflow_config = None
        self.logger = get_logger("phase3.adapter")
    
    def _get_workflow(self):
        """Lazy load Phase 3 workflow"""
        if self._workflow is None:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.orchestration.pipeline_orchestrator import PipelineConfig
            from src.core.orchestration.pipeline_orchestrator import Phase as PipelinePhase, OptimizationLevel as PipelineOptLevel
            from src.core.config_manager import get_config
            from src.core.tool_factory import create_unified_workflow_config
            from src.core.tool_management.workflow_config import Phase, OptimizationLevel
            
            config_manager = get_config()
            workflow_config_dict = create_unified_workflow_config(
                phase=Phase.PHASE3, 
                optimization_level=OptimizationLevel.STANDARD
            )
            
            # Convert dict to PipelineConfig
            tools = workflow_config_dict.get('tools', [])
            self._workflow_config = PipelineConfig(
                tools=tools,
                phase=PipelinePhase.PHASE3,
                optimization_level=PipelineOptLevel.STANDARD
            )
            self._workflow = PipelineOrchestrator(self._workflow_config, config_manager)
        
        return self._workflow
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Phase 3 capabilities"""
        return {
            "supported_document_types": ["pdf"],
            "required_services": ["neo4j", "sqlite"],
            "optional_services": ["ontology_service", "fusion_service"],
            "max_document_size": 50_000_000,  # 50MB
            "supports_batch_processing": True,
            "supports_multiple_queries": True,
            "uses_ontology": True,
            "multi_document_fusion": True,
            "builds_on_previous_phases": True,
            "theory_aware": True,
            "supported_theory_schemas": [str(schema) for schema in self.get_supported_theory_schemas()]
        }
    
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """Validate Phase 3 input requirements"""
        errors = []
        
        # Validate documents
        if not request.documents:
            errors.append("Phase 3 requires at least one document")
        else:
            doc_errors = AdapterUtils.validate_document_paths(request.documents)
            errors.extend(doc_errors)
            
            # Check supported formats
            for doc_path in request.documents:
                format_check = AdapterUtils.check_document_format_support(doc_path)
                if not format_check["supported"]:
                    errors.append(f"Unsupported document format: {format_check['reason']}")
        
        # Validate queries
        if not request.queries:
            errors.append("Phase 3 requires at least one query")
        else:
            query_errors = AdapterUtils.validate_queries(request.queries)
            errors.extend(query_errors)
        
        # Validate fusion strategy
        if hasattr(request, 'fusion_strategy') and request.fusion_strategy:
            valid_strategies = ["basic", "advanced", "semantic", "hierarchical"]
            if request.fusion_strategy not in valid_strategies:
                errors.append(f"Invalid fusion strategy: {request.fusion_strategy}. Valid options: {valid_strategies}")
        
        return errors
    
    def get_supported_theory_schemas(self) -> List[TheorySchema]:
        """Return list of supported theory schemas for Phase 3"""
        return [
            TheorySchema.MASTER_CONCEPTS, 
            TheorySchema.THREE_DIMENSIONAL, 
            TheorySchema.ORM_METHODOLOGY
        ]
    
    def _execute_original(self, request: ProcessingRequest) -> PhaseResult:
        """Execute Phase 3 workflow with multi-document fusion"""
        context = AdapterUtils.create_execution_context("Phase 3", 
                                                        getattr(request, 'workflow_id', 'phase3_exec'))
        
        AdapterUtils.log_adapter_operation("Phase3Adapter", "execute_original", context)
        
        try:
            # Validate input
            errors = self.validate_input(request)
            if errors:
                error_msg = f"Validation failed: {'; '.join(errors)}"
                AdapterUtils.log_adapter_operation("Phase3Adapter", "execute_original", context, error=Exception(error_msg))
                return self.create_error_result(error_msg)
            
            workflow = self._get_workflow()
            
            # Prepare Phase 3 specific parameters
            phase3_params = {
                "document_paths": request.documents,
                "queries": request.queries,
                "fusion_strategy": getattr(request, 'fusion_strategy', 'basic'),
                "use_ontology": True,
                "multi_document_mode": True
            }
            
            # Add previous phase data if available
            if hasattr(request, 'phase1_graph_data') and request.phase1_graph_data:
                phase3_params["phase1_data"] = request.phase1_graph_data
            
            if hasattr(request, 'phase2_enhanced_data') and request.phase2_enhanced_data:
                phase3_params["phase2_data"] = request.phase2_enhanced_data
            
            # Execute workflow
            result = workflow.execute(**phase3_params)
            
            # Extract results
            final_result = result.get("final_result", {})
            entities = final_result.get("entities", [])
            relationships = final_result.get("relationships", [])
            query_results = final_result.get("query_results", [])
            fusion_metrics = final_result.get("fusion_metrics", {})
            
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
                phase_name="Phase 3",
                execution_time=metrics["execution_time_seconds"],
                entity_count=metrics["entities_created"],
                relationship_count=metrics["relationships_created"],
                confidence_score=metrics.get("confidence_score", 0.8),
                results={
                    "entities_fused": len(entities),
                    "relationships_fused": len(relationships),
                    "documents_processed": len(request.documents),
                    "documents_processed_count": metrics["documents_processed"],
                    "queries_answered_count": metrics["queries_answered"],
                    "fusion_strategy": getattr(request, 'fusion_strategy', 'basic'),
                    "fusion_applied": bool(fusion_metrics),
                    "throughput": metrics["throughput"],
                    "efficiency": metrics["efficiency"],
                    "query_results": query_results,
                    "fusion_metrics": fusion_metrics,
                    "multi_document_processing": True,
                    "fusion_enhanced": True
                }
            )
            
            AdapterUtils.log_adapter_operation("Phase3Adapter", "execute_original", context, result=metrics)
            return phase_result
                
        except Exception as e:
            error_msg = AdapterUtils.sanitize_error_message(e)
            self.logger.error(f"Phase 3 adapter error: {error_msg}")
            AdapterUtils.log_adapter_operation("Phase3Adapter", "execute_original", context, error=e)
            
            execution_time = time.time() - context["start_time"]
            return self.create_error_result(f"Phase 3 adapter error: {error_msg}", execution_time)
    
    def _create_theory_guided_workflow(self, theory_schema: Any) -> Any:
        """Create workflow that uses theory to guide fusion processing"""
        try:
            from src.tools.phase3.theory_guided_fusion_workflow import TheoryGuidedFusionWorkflow  # type: ignore[import-not-found]
            from src.core.config_manager import get_config
            
            config_manager = get_config()
            return TheoryGuidedFusionWorkflow(
                config_manager=config_manager,
                theory_schema=theory_schema
            )
        except ImportError:
            self.logger.warning("Theory-guided fusion workflow not available, falling back to regular workflow")
            return self._get_workflow()
    
    def cleanup(self) -> bool:
        """Clean up Phase 3 adapter resources"""
        try:
            if self._workflow and hasattr(self._workflow, 'cleanup'):
                self._workflow.cleanup()
            
            self._workflow = None
            self._workflow_config = None
            return True
            
        except Exception as e:
            self.logger.error(f"Phase 3 adapter cleanup failed: {e}")
            return False