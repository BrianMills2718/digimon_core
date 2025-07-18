"""Performance tests for PipelineOrchestrator.

Tests pipeline performance and resource usage.
"""

import pytest
import time
import tempfile
from pathlib import Path

from src.core.pipeline_orchestrator import PipelineOrchestrator, OptimizationLevel, Phase
from src.core.tool_factory import create_unified_workflow_config
from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow


class TestOrchestratorPerformance:
    """Performance tests for PipelineOrchestrator"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_orchestrator_creation_performance(self):
        """Test that orchestrator creation is fast"""
        start_time = time.time()
        
        config = create_unified_workflow_config(
            phase=Phase.PHASE1,
            optimization_level=OptimizationLevel.STANDARD,
            workflow_storage_dir=self.temp_dir
        )
        orchestrator = PipelineOrchestrator(config)
        
        creation_time = time.time() - start_time
        
        # Orchestrator creation should be under 1 second
        assert creation_time < 1.0, f"Orchestrator creation took {creation_time:.2f}s, expected < 1.0s"
        assert orchestrator is not None
    
    def test_tool_factory_performance(self):
        """Test that tool factory operations are fast"""
        start_time = time.time()
        
        # Create configs for different phases
        configs = []
        for phase in [Phase.PHASE1, Phase.PHASE2]:
            for level in [OptimizationLevel.STANDARD, OptimizationLevel.ENHANCED]:
                if phase == Phase.PHASE1 and level == OptimizationLevel.ENHANCED:
                    continue  # Skip invalid combination
                
                config = create_unified_workflow_config(
                    phase=phase,
                    optimization_level=level,
                    workflow_storage_dir=self.temp_dir
                )
                configs.append(config)
        
        factory_time = time.time() - start_time
        
        # Creating multiple configs should be fast
        assert factory_time < 2.0, f"Tool factory operations took {factory_time:.2f}s, expected < 2.0s"
        assert len(configs) == 3  # PHASE1+STANDARD, PHASE1+OPTIMIZED, PHASE2+ENHANCED
    
    def test_workflow_initialization_performance(self):
        """Test that workflow initialization is fast"""
        start_time = time.time()
        
        # Test Phase 1 workflow initialization
        workflow1 = VerticalSliceWorkflow(workflow_storage_dir=self.temp_dir)
        
        # Test Phase 2 workflow initialization  
        workflow2 = EnhancedVerticalSliceWorkflow(workflow_storage_dir=self.temp_dir)
        
        init_time = time.time() - start_time
        
        # Workflow initialization should be under 3 seconds
        assert init_time < 3.0, f"Workflow initialization took {init_time:.2f}s, expected < 3.0s"
        assert workflow1 is not None
        assert workflow2 is not None
    
    @pytest.mark.skip(reason="Memory profiling requires psutil - optional dependency")
    def test_orchestrator_memory_usage(self):
        """Test that orchestrator doesn't consume excessive memory"""
        # This test would check memory usage with psutil
        # Skip for now to avoid adding dependency
        pass
    
    def test_tool_adapter_instantiation_performance(self):
        """Test that tool adapters can be instantiated quickly"""
        from unittest.mock import Mock
        
        start_time = time.time()
        
        # Mock services
        identity_service = Mock()
        provenance_service = Mock()
        quality_service = Mock()
        
        # Instantiate all adapters
        from src.core.tool_adapters import (
            PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter,
            RelationshipExtractorAdapter, EntityBuilderAdapter, EdgeBuilderAdapter,
            PageRankAdapter, MultiHopQueryAdapter
        )
        
        adapters = []
        
        # Basic adapters
        for adapter_class in [PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter, RelationshipExtractorAdapter]:
            adapter = adapter_class(identity_service, provenance_service, quality_service)
            adapters.append(adapter)
        
        # Neo4j adapters
        for adapter_class in [EntityBuilderAdapter, EdgeBuilderAdapter, PageRankAdapter, MultiHopQueryAdapter]:
            adapter = adapter_class(
                identity_service, provenance_service, quality_service,
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            adapters.append(adapter)
        
        instantiation_time = time.time() - start_time
        
        # Adapter instantiation should be fast
        assert instantiation_time < 1.0, f"Adapter instantiation took {instantiation_time:.2f}s, expected < 1.0s"
        assert len(adapters) == 8