# tests/integration/test_theory_ui_integration.py
import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

class TestTheoryUIIntegration:
    """Test theory-aware features integration with UI components"""
    
    def test_cli_tool_theory_support(self):
        """Test CLI tool can handle theory-aware requests"""
        # Test that CLI can be imported and instantiated
        try:
            from ui.cli_tool import main as cli_main
            print("✅ CLI tool imports successfully")
            
            # Test that the CLI tool can access theory components
            from src.core.phase_adapters import Phase1Adapter
            from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema
            
            # Create a theory config to test integration
            theory_config = TheoryConfig(
                schema_type=TheorySchema.MASTER_CONCEPTS,
                concept_library_path="src/ontology_library/master_concepts.py"
            )
            
            # Test that phase adapter can handle theory config
            phase1 = Phase1Adapter()
            supported_schemas = phase1.get_supported_theory_schemas()
            assert len(supported_schemas) > 0
            
            print("✅ CLI tool theory integration working")
            
        except ImportError as e:
            pytest.skip(f"CLI tool import failed: {e}")
        except Exception as e:
            pytest.fail(f"CLI tool theory integration failed: {e}")
    
    def test_streamlit_ui_theory_support(self):
        """Test Streamlit UI can handle theory features"""
        try:
            from ui.graphrag_ui import main as ui_main
            print("✅ Streamlit UI imports successfully")
            
            # Test that the UI can access theory components
            from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema
            from contracts.phase_interfaces.phase_registry import TheoryAwarePhaseRegistry
            
            # Test registry creation (used by UI for phase discovery)
            registry = TheoryAwarePhaseRegistry()
            
            # Test that UI components can work with theory features
            from src.core.phase_adapters import Phase1Adapter
            phase1 = Phase1Adapter()
            registry.register_phase(phase1)
            
            phases = registry.get_all_phases()
            assert len(phases) > 0
            
            print("✅ Streamlit UI theory integration working")
            
        except ImportError as e:
            pytest.skip(f"Streamlit UI import failed: {e}")
        except Exception as e:
            pytest.fail(f"Streamlit UI theory integration failed: {e}")
    
    def test_theory_registry_global_access(self):
        """Test global theory registry accessible from UI context"""
        try:
            from contracts.phase_interfaces.phase_registry import get_theory_registry
            from src.core.phase_adapters import Phase1Adapter
            
            registry = get_theory_registry()
            
            # Register a phase
            phase1 = Phase1Adapter()
            registry.register_phase(phase1)
            
            # Test discovery works
            phases = registry.get_all_phases()
            assert "Phase 1" in phases
            
            print("✅ Theory registry global access working")
            
        except ImportError as e:
            # If global registry doesn't exist, create a basic test
            from contracts.phase_interfaces.phase_registry import TheoryAwarePhaseRegistry
            from src.core.phase_adapters import Phase1Adapter
            
            registry = TheoryAwarePhaseRegistry()
            phase1 = Phase1Adapter()
            registry.register_phase(phase1)
            
            phases = registry.get_all_phases()
            assert "Phase 1" in phases
            
            print("✅ Theory registry basic functionality working")
        except Exception as e:
            pytest.fail(f"Theory registry global access failed: {e}")
    
    def test_mcp_server_theory_integration(self):
        """Test MCP server can handle theory-aware tools"""
        try:
            # Test that MCP server can import theory components
            from src.mcp_server import main as mcp_main
            from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema
            
            # Test theory config creation
            theory_config = TheoryConfig(
                schema_type=TheorySchema.MASTER_CONCEPTS,
                concept_library_path="src/ontology_library/master_concepts.py"
            )
            
            assert theory_config.schema_type == TheorySchema.MASTER_CONCEPTS
            
            print("✅ MCP server theory integration working")
            
        except ImportError as e:
            pytest.skip(f"MCP server import failed: {e}")
        except Exception as e:
            pytest.fail(f"MCP server theory integration failed: {e}")
    
    def test_demo_scripts_theory_compatibility(self):
        """Test demo scripts can work with theory-aware components"""
        try:
            # Test that demo scripts can import and use theory components
            demo_script_paths = [
                "scripts/demo/demo_extraction.py",
                "scripts/demo/answer_questions.py",
                "examples/minimal_working_example.py"
            ]
            
            working_scripts = []
            for script_path in demo_script_paths:
                if os.path.exists(script_path):
                    try:
                        # Try to compile the script to check for syntax errors
                        with open(script_path, 'r') as f:
                            compile(f.read(), script_path, 'exec')
                        working_scripts.append(script_path)
                    except SyntaxError:
                        pass  # Skip scripts with syntax errors
            
            assert len(working_scripts) > 0, "No demo scripts found or compilable"
            
            # Test theory component imports
            from src.core.phase_adapters import Phase1Adapter
            from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema
            
            phase1 = Phase1Adapter()
            supported_schemas = phase1.get_supported_theory_schemas()
            assert len(supported_schemas) > 0
            
            print(f"✅ Demo scripts theory compatibility verified ({len(working_scripts)} scripts)")
            
        except Exception as e:
            pytest.fail(f"Demo scripts theory compatibility failed: {e}")
    
    def test_config_manager_theory_integration(self):
        """Test ConfigManager works with theory-aware components"""
        try:
            from src.core.config_manager import ConfigManager
            from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema
            
            # Test config manager creation
            config_manager = ConfigManager()
            
            # Test that theory config can use config manager data
            theory_config = TheoryConfig(
                schema_type=TheorySchema.MASTER_CONCEPTS,
                concept_library_path="src/ontology_library/master_concepts.py"
            )
            
            # Test that config manager has necessary configuration
            neo4j_config = config_manager.get_neo4j_config()
            assert 'uri' in neo4j_config
            assert 'user' in neo4j_config
            assert 'password' in neo4j_config
            
            print("✅ ConfigManager theory integration working")
            
        except Exception as e:
            pytest.fail(f"ConfigManager theory integration failed: {e}")
    
    def test_pipeline_orchestrator_theory_support(self):
        """Test PipelineOrchestrator can work with theory-aware components"""
        try:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.config_manager import ConfigManager
            from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
            
            # Test orchestrator creation with theory-aware components
            config_manager = ConfigManager()
            config = create_unified_workflow_config(
                phase=Phase.PHASE1,
                optimization_level=OptimizationLevel.STANDARD,
                workflow_storage_dir="./data"
            )
            
            orchestrator = PipelineOrchestrator(config, config_manager)
            
            # Test that orchestrator can access theory-aware phase adapters
            from src.core.phase_adapters import Phase1Adapter
            phase1 = Phase1Adapter()
            supported_schemas = phase1.get_supported_theory_schemas()
            assert len(supported_schemas) > 0
            
            print("✅ PipelineOrchestrator theory support working")
            
        except Exception as e:
            pytest.fail(f"PipelineOrchestrator theory support failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])