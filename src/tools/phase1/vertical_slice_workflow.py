"""
Compatibility module for vertical_slice_workflow.

This module provides backward compatibility by importing from the pipeline orchestrator.
"""

# Import from pipeline orchestrator as the replacement
from src.core.pipeline_orchestrator import PipelineOrchestrator, PipelineConfig, Phase, OptimizationLevel

class VerticalSliceWorkflow:
    """Backward compatibility wrapper for PipelineOrchestrator"""
    
    def __init__(self, config=None):
        if config is None:
            # Create default Phase 1 configuration
            from src.core.orchestration.workflow_configuration import create_unified_workflow_config
            config = create_unified_workflow_config(
                phase=Phase.PHASE1, 
                optimization_level=OptimizationLevel.STANDARD
            )
        self.orchestrator = PipelineOrchestrator(config)
    
    def execute_workflow(self, *args, **kwargs):
        """Execute workflow using pipeline orchestrator"""
        return self.orchestrator.execute_workflow(*args, **kwargs)
    
    def execute_pdf_workflow(self, pdf_paths, queries):
        """Execute PDF workflow"""
        return self.orchestrator.execute_pdf_workflow(pdf_paths, queries)