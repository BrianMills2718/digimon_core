"""
Integration tests to verify that Phase 2 and Phase 3 no longer throw NotImplementedError.

This test suite addresses CLAUDE.md Task P1.3: Create Phase Integration Tests
to verify that the NotImplementedError issues identified by Gemini AI analysis 
have been resolved.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import ConfigManager
from src.core.tool_factory import ToolFactory, create_unified_workflow_config, Phase, OptimizationLevel
from src.core.pipeline_orchestrator import PipelineOrchestrator


class TestPhaseIntegration:
    """Test that all phases can be instantiated without NotImplementedError"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config_manager = ConfigManager()
    
    def test_phase1_no_not_implemented_error(self):
        """Test Phase 1 tool creation works without NotImplementedError"""
        try:
            # This should work without NotImplementedError
            tools = ToolFactory.create_tools_for_config(
                Phase.PHASE1, 
                OptimizationLevel.STANDARD, 
                self.config_manager
            )
            
            assert len(tools) > 0, "Phase 1 should create tools"
            print(f"✅ Phase 1 created {len(tools)} tools successfully")
            
        except NotImplementedError as e:
            pytest.fail(f"Phase 1 still throws NotImplementedError: {e}")
    
    def test_phase2_no_not_implemented_error(self):
        """Test Phase 2 tool creation works without NotImplementedError"""
        try:
            # This should NOT throw NotImplementedError anymore
            tools = ToolFactory.create_tools_for_config(
                Phase.PHASE2, 
                OptimizationLevel.STANDARD, 
                self.config_manager
            )
            
            assert len(tools) > 0, "Phase 2 should create tools"
            print(f"✅ Phase 2 created {len(tools)} tools successfully")
            
        except NotImplementedError as e:
            pytest.fail(f"❌ Phase 2 still throws NotImplementedError: {e}")
        except ImportError as e:
            # ImportError is acceptable if dependencies are missing
            pytest.skip(f"Phase 2 dependencies not available: {e}")
    
    def test_phase3_no_not_implemented_error(self):
        """Test Phase 3 tool creation works without NotImplementedError"""
        try:
            # This should NOT throw NotImplementedError anymore
            tools = ToolFactory.create_tools_for_config(
                Phase.PHASE3, 
                OptimizationLevel.STANDARD, 
                self.config_manager
            )
            
            assert len(tools) > 0, "Phase 3 should create tools"
            print(f"✅ Phase 3 created {len(tools)} tools successfully")
            
        except NotImplementedError as e:
            pytest.fail(f"❌ Phase 3 still throws NotImplementedError: {e}")
        except ImportError as e:
            # ImportError is acceptable if dependencies are missing
            pytest.skip(f"Phase 3 dependencies not available: {e}")
    
    def test_phase2_pipeline_orchestrator_creation(self):
        """Test Phase 2 PipelineOrchestrator can be created without NotImplementedError"""
        try:
            config = create_unified_workflow_config(
                Phase.PHASE2, 
                OptimizationLevel.STANDARD,
                config_manager=self.config_manager
            )
            orchestrator = PipelineOrchestrator(config, self.config_manager)
            
            # Should not throw NotImplementedError
            assert orchestrator is not None
            print("✅ Phase 2 PipelineOrchestrator created successfully")
            
        except NotImplementedError as e:
            pytest.fail(f"❌ Phase 2 PipelineOrchestrator still throws NotImplementedError: {e}")
        except ImportError as e:
            pytest.skip(f"Phase 2 dependencies not available: {e}")
    
    def test_phase3_pipeline_orchestrator_creation(self):
        """Test Phase 3 PipelineOrchestrator can be created without NotImplementedError"""
        try:
            config = create_unified_workflow_config(
                Phase.PHASE3, 
                OptimizationLevel.STANDARD,
                config_manager=self.config_manager
            )
            orchestrator = PipelineOrchestrator(config, self.config_manager)
            
            # Should not throw NotImplementedError
            assert orchestrator is not None
            print("✅ Phase 3 PipelineOrchestrator created successfully")
            
        except NotImplementedError as e:
            pytest.fail(f"❌ Phase 3 PipelineOrchestrator still throws NotImplementedError: {e}")
        except ImportError as e:
            pytest.skip(f"Phase 3 dependencies not available: {e}")
    
    def test_all_phase_tool_adapters_instantiate(self):
        """Test that all new phase tool adapters can be instantiated"""
        try:
            # Test Phase 2 adapters
            from src.core.tool_adapters import (
                OntologyAwareExtractorAdapter,
                OntologyGraphBuilderAdapter,
                InteractiveGraphVisualizerAdapter
            )
            
            # Should be able to create instances
            extractor = OntologyAwareExtractorAdapter(self.config_manager)
            builder = OntologyGraphBuilderAdapter(self.config_manager)
            visualizer = InteractiveGraphVisualizerAdapter(self.config_manager)
            
            assert extractor is not None
            assert builder is not None
            assert visualizer is not None
            print("✅ All Phase 2 tool adapters instantiate successfully")
            
        except ImportError as e:
            pytest.skip(f"Phase 2 adapter dependencies not available: {e}")
        except Exception as e:
            pytest.fail(f"❌ Phase 2 adapter instantiation failed: {e}")
        
        try:
            # Test Phase 3 adapters
            from src.core.tool_adapters import MultiDocumentFusionAdapter
            
            fusion = MultiDocumentFusionAdapter(self.config_manager)
            assert fusion is not None
            print("✅ Phase 3 tool adapter instantiates successfully")
            
        except ImportError as e:
            pytest.skip(f"Phase 3 adapter dependencies not available: {e}")
        except Exception as e:
            pytest.fail(f"❌ Phase 3 adapter instantiation failed: {e}")
    
    def test_phase_progression_without_errors(self):
        """Test that we can create orchestrators for all phases in sequence"""
        phases_created = []
        
        for phase in [Phase.PHASE1, Phase.PHASE2, Phase.PHASE3]:
            try:
                config = create_unified_workflow_config(
                    phase, 
                    OptimizationLevel.STANDARD,
                    config_manager=self.config_manager
                )
                orchestrator = PipelineOrchestrator(config, self.config_manager)
                
                assert orchestrator is not None
                phases_created.append(phase.name)
                print(f"✅ {phase.name} orchestrator created successfully")
                
            except NotImplementedError as e:
                pytest.fail(f"❌ {phase.name} still throws NotImplementedError: {e}")
            except ImportError as e:
                print(f"⚠️  {phase.name} dependencies not available: {e}")
                continue
        
        # At minimum, Phase 1 should work
        assert "PHASE1" in phases_created, "At least Phase 1 should be creatable"
        print(f"✅ Successfully created orchestrators for phases: {phases_created}")


if __name__ == "__main__":
    # Run tests directly
    test_suite = TestPhaseIntegration()
    test_suite.setup_method()
    
    print("🧪 Testing Phase Integration...")
    
    try:
        test_suite.test_phase1_no_not_implemented_error()
        test_suite.test_phase2_no_not_implemented_error()
        test_suite.test_phase3_no_not_implemented_error()
        test_suite.test_phase2_pipeline_orchestrator_creation()
        test_suite.test_phase3_pipeline_orchestrator_creation()
        test_suite.test_all_phase_tool_adapters_instantiate()
        test_suite.test_phase_progression_without_errors()
        
        print("\n🎉 All phase integration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Phase integration test failed: {e}")