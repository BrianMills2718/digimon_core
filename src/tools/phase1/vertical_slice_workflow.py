"""
DEPRECATED: VerticalSliceWorkflow
This class is deprecated. Use PipelineOrchestrator instead.

This addresses CLAUDE.md Critical Issue 2: Deprecate Competing Workflows
"""

import warnings
from typing import Dict, List, Optional, Any
from pathlib import Path

from ...core.pipeline_orchestrator import PipelineOrchestrator, OptimizationLevel, Phase
from ...core.tool_factory import create_unified_workflow_config
from ...core.config import ConfigurationManager


class VerticalSliceWorkflow:
    """
    DEPRECATED: Use PipelineOrchestrator instead.
    
    This class is a compatibility wrapper around PipelineOrchestrator.
    It will be removed in a future version.
    """
    
    def __init__(self, workflow_storage_dir: str = "./data/workflows"):
        """Initialize workflow with PipelineOrchestrator
        
        Args:
            workflow_storage_dir: Directory for workflow state storage
        """
        warnings.warn(
            "VerticalSliceWorkflow is deprecated. Use PipelineOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Initialize with PipelineOrchestrator
        self.config_manager = ConfigManager()
        self.config = create_unified_workflow_config(
            phase=Phase.PHASE1,
            optimization_level=OptimizationLevel.STANDARD,
            workflow_storage_dir=workflow_storage_dir
        )
        self.orchestrator = PipelineOrchestrator(self.config, self.config_manager)
    
    def execute_pdf_workflow(
        self,
        document_paths: List[str],
        queries: List[str] = None
    ) -> Dict[str, Any]:
        """Execute workflow using PipelineOrchestrator (deprecated)"""
        return self.orchestrator.execute(document_paths, queries)
    
    def execute_workflow(
        self,
        pdf_path: str,
        query: str,
        workflow_name: str = "default",
        skip_pagerank: bool = False
    ) -> Dict[str, Any]:
        """Legacy interface - delegates to PipelineOrchestrator (deprecated)"""
        document_paths = [pdf_path] if pdf_path else []
        queries = [query] if query else []
        return self.orchestrator.execute(document_paths, queries)
    
    def execute(self, document_paths: List[str], queries: List[str] = None) -> Dict[str, Any]:
        """Execute workflow using PipelineOrchestrator"""
        return self.orchestrator.execute(document_paths, queries)