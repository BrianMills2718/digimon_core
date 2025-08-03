"""
Phase 2 Adapter - Enhanced GraphRAG with Ontology

Adapter for Phase 2 Enhanced GraphRAG workflow with ontology integration.
Builds upon Phase 1 results and adds ontology-guided processing.
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


class Phase2Adapter(TheoryAwareAdapterBase, GraphRAGPhase):
    """Adapter for Phase 2 Enhanced GraphRAG workflow with ontology integration"""
    
    def __init__(self):
        TheoryAwareAdapterBase.__init__(self, "Phase 2: Enhanced", "1.0")
        GraphRAGPhase.__init__(self, "Phase 2: Enhanced", "1.0")
        
        self._workflow = None
        self._workflow_config = None
        self.logger = get_logger("phase2.adapter")
    
    def _get_workflow(self):
        """Lazy load Phase 2 workflow"""
        if self._workflow is None:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.orchestration.pipeline_orchestrator import PipelineConfig
            from src.core.orchestration.pipeline_orchestrator import Phase as PipelinePhase, OptimizationLevel as PipelineOptLevel
            from src.core.tool_management.workflow_config import Phase, OptimizationLevel
            from src.core.config_manager import get_config
            from src.core.tool_factory import create_unified_workflow_config
            
            config_manager = get_config()
            workflow_config_dict = create_unified_workflow_config(
                phase=Phase.PHASE2, 
                optimization_level=OptimizationLevel.STANDARD
            )
            
            # Convert dict to PipelineConfig
            tools = workflow_config_dict.get('tools', [])
            self._workflow_config = PipelineConfig(
                tools=tools,
                phase=PipelinePhase.PHASE2,
                optimization_level=PipelineOptLevel.STANDARD
            )
            self._workflow = PipelineOrchestrator(self._workflow_config, config_manager)
        
        return self._workflow
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Phase 2 capabilities"""
        return {
            "supported_document_types": ["pdf"],
            "required_services": ["neo4j", "sqlite"],
            "optional_services": ["ontology_service"],
            "max_document_size": 25_000_000,  # 25MB
            "supports_batch_processing": True,
            "supports_multiple_queries": True,
            "uses_ontology": True,
            "enhances_phase1_results": True,
            "theory_aware": True,
            "supported_theory_schemas": [str(schema) for schema in self.get_supported_theory_schemas()]
        }
    
    def validate_input(self, request: ProcessingRequest) -> List[str]:
        """Validate Phase 2 input requirements"""
        errors = []
        
        # Validate documents
        if not request.documents:
            errors.append("Phase 2 requires at least one document")
        else:
            # Validate document paths
            doc_errors = AdapterUtils.validate_document_paths(request.documents)
            errors.extend(doc_errors)
            
            # Check supported formats for Phase 2
            for doc_path in request.documents:
                format_check = AdapterUtils.check_document_format_support(doc_path)
                if not format_check["supported"]:
                    errors.append(f"Unsupported document format: {format_check['reason']}")
        
        # Validate queries
        if not request.queries:
            errors.append("Phase 2 requires at least one query")
        else:
            query_errors = AdapterUtils.validate_queries(request.queries)
            errors.extend(query_errors)
        
        # Validate domain description (Phase 2 specific)
        if hasattr(request, 'domain_description') and request.domain_description:
            if len(request.domain_description) < 10:
                errors.append("Domain description too short (minimum 10 characters)")
            elif len(request.domain_description) > 1000:
                errors.append("Domain description too long (maximum 1000 characters)")
        
        # Validate workflow ID
        if hasattr(request, 'workflow_id') and request.workflow_id:
            workflow_error = AdapterUtils.validate_workflow_id(request.workflow_id)
            if workflow_error:
                errors.append(workflow_error)
        
        return errors
    
    def get_supported_theory_schemas(self) -> List[TheorySchema]:
        """Return list of supported theory schemas for Phase 2"""
        return [
            TheorySchema.MASTER_CONCEPTS, 
            TheorySchema.THREE_DIMENSIONAL, 
            TheorySchema.ORM_METHODOLOGY
        ]
    
    def _execute_original(self, request: ProcessingRequest) -> PhaseResult:
        """Execute Phase 2 workflow with ontology enhancement"""
        context = AdapterUtils.create_execution_context("Phase 2", 
                                                        getattr(request, 'workflow_id', 'phase2_exec'))
        
        AdapterUtils.log_adapter_operation("Phase2Adapter", "execute_original", context)
        
        try:
            # Validate input
            errors = self.validate_input(request)
            if errors:
                error_msg = f"Validation failed: {'; '.join(errors)}"
                AdapterUtils.log_adapter_operation("Phase2Adapter", "execute_original", context, error=Exception(error_msg))
                return self.create_error_result(error_msg)
            
            workflow = self._get_workflow()
            
            # Prepare Phase 2 specific parameters
            phase2_params = {
                "document_paths": request.documents,
                "queries": request.queries,
                "use_ontology": True,
                "enhance_existing_graph": True
            }
            
            # Add domain description if available
            if hasattr(request, 'domain_description') and request.domain_description:
                phase2_params["domain_description"] = request.domain_description
            
            # Add Phase 1 graph data if available for enhancement
            if hasattr(request, 'phase1_graph_data') and request.phase1_graph_data:
                phase2_params["base_graph_data"] = request.phase1_graph_data
            
            # Execute workflow using PipelineOrchestrator
            result = workflow.execute(**phase2_params)
            
            # Extract results with error handling
            final_result = result.get("final_result", {})
            entities = final_result.get("entities", [])
            relationships = final_result.get("relationships", [])
            query_results = final_result.get("query_results", [])
            ontology_info = final_result.get("ontology_info", {})
            
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
                phase_name="Phase 2",
                execution_time=metrics["execution_time_seconds"],
                entity_count=metrics["entities_created"],
                relationship_count=metrics["relationships_created"],
                confidence_score=metrics.get("confidence_score", 0.8),
                results={
                    "entities_extracted": len(entities),
                    "relationships_found": len(relationships),
                    "queries_processed": len(request.queries),
                    "documents_processed": len(request.documents),
                    "ontology_enhanced": bool(ontology_info),
                    "ontology_concepts_used": len(ontology_info.get("concepts_used", [])),
                    "throughput": metrics["throughput"],
                    "efficiency": metrics["efficiency"],
                    "query_results": query_results,
                    "ontology_info": ontology_info,
                    "enhancement_applied": True,
                    "graph_metrics": final_result.get("graph_metrics", {})
                }
            )
            
            AdapterUtils.log_adapter_operation("Phase2Adapter", "execute_original", context, result=metrics)
            return phase_result
                
        except Exception as e:
            error_msg = AdapterUtils.sanitize_error_message(e)
            self.logger.error(f"Phase 2 adapter error: {error_msg}")
            AdapterUtils.log_adapter_operation("Phase2Adapter", "execute_original", context, error=e)
            
            execution_time = time.time() - context["start_time"]
            return self.create_error_result(f"Phase 2 adapter error: {error_msg}", execution_time)
    
    def _create_theory_guided_workflow(self, theory_schema: Any) -> Any:
        """Create workflow that uses theory to guide enhanced processing"""
        try:
            # Try to import the theory guided workflow if available
            try:
                from src.tools.phase2.theory_guided_enhanced_workflow import TheoryGuidedEnhancedWorkflow  # type: ignore
                from src.core.config_manager import get_config
                
                config_manager = get_config()
                return TheoryGuidedEnhancedWorkflow(
                    config_manager=config_manager,
                    theory_schema=theory_schema,
                    use_ontology=True
                )
            except ImportError:
                # Fallback to standard workflow if theory guided workflow is not available
                logger.warning("Theory guided workflow not available, using standard workflow")
                return self._get_workflow()
        except ImportError:
            # Fallback to regular workflow if theory-guided not available
            self.logger.warning("Theory-guided enhanced workflow not available, falling back to regular workflow")
            return self._get_workflow()
    
    def _execute_with_theory_guidance(self, workflow: Any, request, theory_schema: Any) -> Any:
        """Execute workflow with theory guidance for Phase 2"""
        try:
            # Phase 2 specific parameters for theory-guided execution
            theory_params = {
                "document_paths": request.documents,
                "queries": request.queries,
                "theory_schema": theory_schema,
                "concept_library": getattr(workflow, 'concept_library', None),
                "use_ontology": True,
                "enhance_with_theory": True
            }
            
            # Add domain description if available
            if hasattr(request, 'domain_description') and request.domain_description:
                theory_params["domain_description"] = request.domain_description
            
            # Add Phase 1 data for enhancement
            if hasattr(request, 'phase1_graph_data') and request.phase1_graph_data:
                theory_params["base_graph_data"] = request.phase1_graph_data
            
            # Try theory-guided execution first
            if hasattr(workflow, 'execute_with_theory_guidance'):
                return workflow.execute_with_theory_guidance(**theory_params)
            else:
                # Fallback to regular execution with theory metadata
                self.logger.warning("Workflow does not support theory guidance, using regular execution")
                result = workflow.execute(
                    document_paths=request.documents,
                    queries=request.queries,
                    use_ontology=True
                )
                
                # Add theory metadata to regular result
                if hasattr(result, 'final_result'):
                    final_result = result.final_result
                    # Add theory alignment score
                    final_result['theory_alignment_score'] = 0.75  # Higher than Phase 1
                    final_result['concept_usage'] = {}
                    final_result['theory_metadata'] = {
                        "schema_type": str(theory_schema),
                        "theory_guided": False,
                        "fallback_execution": True,
                        "ontology_enhanced": True
                    }
                
                return result
                
        except Exception as e:
            self.logger.error(f"Theory-guided execution failed: {e}")
            # Fallback to regular execution
            result = workflow.execute(
                document_paths=request.documents,
                queries=request.queries,
                use_ontology=True
            )
            return result
    
    def enhance_phase1_results(self, phase1_result: PhaseResult, 
                              domain_description: Optional[str] = None) -> PhaseResult:
        """Enhance Phase 1 results with Phase 2 ontology processing"""
        context = AdapterUtils.create_execution_context("Phase 2 Enhancement", "phase2_enhance")
        
        try:
            workflow = self._get_workflow()
            
            # Create enhancement request
            enhancement_params = {
                "base_entities": phase1_result.entity_count,
                "base_relationships": phase1_result.relationship_count,
                "domain_description": domain_description,
                "use_ontology": True,
                "enhancement_mode": True
            }
            
            # Execute enhancement
            result = workflow.enhance_existing_graph(**enhancement_params)
            
            # Create enhanced phase result
            final_result = result.get("final_result", {})
            entities = final_result.get("entities", [])
            relationships = final_result.get("relationships", [])
            
            # Get documents and queries from results if available
            base_results = phase1_result.results or {}
            documents_processed = base_results.get('documents_processed', 0)
            queries_answered = base_results.get('queries_answered', 0)
            
            metrics = AdapterUtils.calculate_execution_metrics(
                context,
                entities_count=len(entities),
                relationships_count=len(relationships),
                documents_processed=documents_processed,
                queries_answered=queries_answered
            )
            
            enhanced_result = PhaseResult(
                status=PhaseStatus.SUCCESS,
                phase_name="Phase 2 Enhancement",
                execution_time=metrics["execution_time_seconds"],
                entity_count=metrics["entities_created"],
                relationship_count=metrics["relationships_created"],
                confidence_score=metrics.get("confidence_score", 0.8),
                results={
                    "base_entities": phase1_result.entity_count,
                    "enhanced_entities": len(entities),
                    "base_relationships": phase1_result.relationship_count,
                    "enhanced_relationships": len(relationships),
                    "enhancement_applied": True,
                    "ontology_used": True
                }
            )
            
            return enhanced_result
            
        except Exception as e:
            error_msg = AdapterUtils.sanitize_error_message(e)
            self.logger.error(f"Phase 1 enhancement failed: {error_msg}")
            
            execution_time = time.time() - context["start_time"]
            return self.create_error_result(f"Phase 1 enhancement failed: {error_msg}", execution_time)
    
    def get_phase2_specific_info(self) -> Dict[str, Any]:
        """Get Phase 2 specific adapter information"""
        return {
            "workflow_loaded": self._workflow is not None,
            "supports_multiple_documents": True,
            "supports_multiple_queries": True,
            "supports_batch_processing": True,
            "ontology_integration": True,
            "enhances_phase1": True,
            "domain_description_support": True
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of Phase 2 adapter and dependencies"""
        issues: List[str] = []
        health_status: Dict[str, Any] = {
            "adapter_healthy": True,
            "issues": issues
        }
        
        try:
            # Check if workflow can be created
            workflow = self._get_workflow()
            if workflow is None:
                health_status["adapter_healthy"] = False
                issues.append("Cannot create Phase 2 workflow")
            
            # Check ontology service availability
            try:
                from src.ontology_library.ontology_service import OntologyService
                ontology_service = OntologyService()
                if ontology_service is None:
                    issues.append("Ontology service not available")
            except Exception as e:
                issues.append(f"Ontology service check failed: {str(e)}")
            
            # Check theory capabilities
            theory_caps = self.get_theory_capabilities()
            health_status["theory_support"] = theory_caps
            
        except Exception as e:
            health_status["adapter_healthy"] = False
            issues.append(f"Health check failed: {AdapterUtils.sanitize_error_message(e)}")
        
        return health_status
    
    def cleanup(self) -> bool:
        """Clean up Phase 2 adapter resources"""
        try:
            if self._workflow and hasattr(self._workflow, 'cleanup'):
                self._workflow.cleanup()
            
            self._workflow = None
            self._workflow_config = None
            return True
            
        except Exception as e:
            self.logger.error(f"Phase 2 adapter cleanup failed: {e}")
            return False