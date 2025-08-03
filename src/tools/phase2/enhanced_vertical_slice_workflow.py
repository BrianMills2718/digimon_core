"""Enhanced Vertical Slice Workflow - Refactored to use PipelineOrchestrator

PRIORITY 2 REFACTOR: Phase 2 workflow now uses unified orchestrator
with Phase 2 enhanced tools instead of duplicate execution logic.

CRITICAL-2 IMPLEMENTATION: Eliminates duplicate execution logic in Phase 2
by delegating to PipelineOrchestrator while preserving ontology-aware functionality.

Enhanced Workflow Steps (now via orchestrator):
1. T01: Load PDF document
2. T15a: Chunk text into segments
3. T120: Generate domain ontology (or use existing)
4. T23c: Ontology-aware entity extraction
5. T31: Enhanced graph building with semantic validation
6. T68: Calculate PageRank scores
7. T49: Enhanced multi-hop queries with ontological reasoning
8. Interactive visualization and analysis

This demonstrates the unified orchestrator with Phase 2 enhanced capabilities.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from src.core.pipeline_orchestrator import PipelineOrchestrator, OptimizationLevel, Phase
from src.core.tool_factory import create_unified_workflow_config
from src.core.logging_config import get_logger


class EnhancedVerticalSliceWorkflow:
    """Enhanced Phase 2 workflow using unified orchestrator with ontology awareness.
    
    REFACTORED: This class now delegates to PipelineOrchestrator instead of
    containing duplicate tool execution logic, while supporting Phase 2 enhancements.
    """
    
    def __init__(self, workflow_storage_dir: str = None):
        if workflow_storage_dir is None:
            from ...core.standard_config import get_file_path
            workflow_storage_dir = f"{get_file_path('data_dir')}/workflows"
        """Initialize enhanced workflow with PipelineOrchestrator
        
        Args:
            workflow_storage_dir: Directory for workflow state storage
        """
        self.logger = get_logger("phase2.enhanced_workflow")
        self.logger.info("Initializing EnhancedVerticalSliceWorkflow with unified orchestrator")
        
        # Create Phase 2 enhanced pipeline configuration
        self.config = create_unified_workflow_config(
            phase=Phase.PHASE2,
            optimization_level=OptimizationLevel.ENHANCED,
            workflow_storage_dir=workflow_storage_dir
        )
        
        # Initialize orchestrator with Phase 2 configuration
        self.orchestrator = PipelineOrchestrator(self.config)
        self.logger.info("EnhancedVerticalSliceWorkflow initialized with %d enhanced tools", len(self.config.tools))
    
    def execute_enhanced_workflow(
        self,
        document_paths: List[str],
        queries: List[str] = None,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Execute enhanced Phase 2 workflow with ontology awareness.
        
        REFACTORED: This method now delegates to PipelineOrchestrator instead of
        implementing its own enhanced tool execution loop.
        
        Args:
            document_paths: List of document paths to process
            queries: Optional list of queries to execute
            confidence_threshold: Confidence threshold for ontology matching
            
        Returns:
            Enhanced workflow execution result
        """
        queries = queries or []
        workflow_id = f"enhanced_workflow_{len(document_paths)}docs_{len(queries)}queries"
        
        self.logger.info("Starting enhanced Phase 2 workflow - ID: %s, Documents: %d, Queries: %d, Threshold: %f", 
                        workflow_id, len(document_paths), len(queries), confidence_threshold)
        
        try:
            # Execute using unified orchestrator with Phase 2 tools
            # Note: confidence_threshold would be passed to orchestrator config in future enhancement
            result = self.orchestrator.execute(document_paths, queries)
            
            # Add Phase 2 specific metadata
            result["enhanced_metadata"] = {
                "workflow_id": workflow_id,
                "phase": "phase2",
                "ontology_aware": True,
                "confidence_threshold": confidence_threshold,
                "enhancement_level": "full",
                "orchestrator_used": True
            }
            
            # Determine success based on orchestrator result
            if result.get("execution_metadata", {}).get("success", False):
                result["status"] = "success"
                self.logger.info("Enhanced workflow completed successfully - ID: %s", workflow_id)
            else:
                error_msg = result.get("execution_metadata", {}).get("error_summary", "Unknown error")
                result["status"] = "failed"
                self.logger.error("Enhanced workflow failed - ID: %s, Error: %s", workflow_id, error_msg)
            
            return result
            
        except Exception as e:
            error_msg = f"Enhanced workflow failed: {str(e)}"
            self.logger.error("Enhanced workflow exception - ID: %s, Error: %s", workflow_id, error_msg, exc_info=True)
            return {
                "status": "error",
                "error": error_msg,
                "enhanced_metadata": {
                    "workflow_id": workflow_id,
                    "phase": "phase2",
                    "error": True,
                    "orchestrator_used": True
                }
            }
    
    def close(self):
        """Close enhanced workflow resources
        
        CLEANUP: Properly close orchestrator and service manager resources.
        """
        self.logger.info("Closing EnhancedVerticalSliceWorkflow resources")
        
        # Close orchestrator resources
        if hasattr(self.orchestrator, 'service_manager') and self.orchestrator.service_manager:
            try:
                self.orchestrator.service_manager.close_all()
                self.logger.info("Enhanced workflow service manager resources closed")
            except Exception as e:
                self.logger.warning("Error closing enhanced workflow service manager: %s", str(e))
        
        self.logger.info("EnhancedVerticalSliceWorkflow closed successfully")
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced workflow statistics and configuration info
        
        NEW: Provides visibility into Phase 2 orchestrator configuration.
        
        Returns:
            Enhanced workflow statistics and configuration
        """
        stats = {
            "orchestrator_config": {
                "phase": self.config.phase.value,
                "optimization_level": self.config.optimization_level.value,
                "tools_count": len(self.config.tools),
                "tool_names": [getattr(tool, 'tool_name', type(tool).__name__) for tool in self.config.tools],
                "enhanced_features": ["ontology_aware", "semantic_validation", "enhanced_queries"]
            }
        }
        
        # Add orchestrator execution stats if available
        if hasattr(self.orchestrator, 'execution_stats'):
            stats["execution_stats"] = self.orchestrator.get_execution_stats()
        
        return stats