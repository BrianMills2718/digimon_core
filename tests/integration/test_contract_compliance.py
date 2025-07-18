# tests/integration/test_contract_compliance.py
import pytest
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from contracts.phase_interfaces.base_graphrag_phase import TheoryAwareGraphRAGPhase, TheorySchema


class TestContractCompliance:
    """Test that all phases implement TheoryAwareGraphRAGPhase correctly"""
    
    def test_all_phases_implement_theory_contract(self):
        """Test that all phases implement TheoryAwareGraphRAGPhase correctly"""
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter, Phase3Adapter
        
        phases = [Phase1Adapter(), Phase2Adapter(), Phase3Adapter()]
        
        for phase in phases:
            # Test contract compliance - check all required methods exist
            assert hasattr(phase, 'get_name'), f"{phase.__class__.__name__} missing get_name method"
            assert hasattr(phase, 'get_version'), f"{phase.__class__.__name__} missing get_version method"
            assert hasattr(phase, 'get_supported_theory_schemas'), f"{phase.__class__.__name__} missing get_supported_theory_schemas method"
            assert hasattr(phase, 'validate_theory_config'), f"{phase.__class__.__name__} missing validate_theory_config method"
            assert hasattr(phase, 'execute'), f"{phase.__class__.__name__} missing execute method"
            assert hasattr(phase, 'get_capabilities'), f"{phase.__class__.__name__} missing get_capabilities method"
            
            # Test that methods return expected types
            name = phase.get_name()
            assert isinstance(name, str), f"{phase.__class__.__name__}.get_name() should return string"
            assert len(name) > 0, f"{phase.__class__.__name__}.get_name() should return non-empty string"
            
            version = phase.get_version()
            assert isinstance(version, str), f"{phase.__class__.__name__}.get_version() should return string"
            assert len(version) > 0, f"{phase.__class__.__name__}.get_version() should return non-empty string"
            
            # Test theory schema support
            schemas = phase.get_supported_theory_schemas()
            assert isinstance(schemas, list), f"{phase.__class__.__name__}.get_supported_theory_schemas() should return list"
            assert len(schemas) > 0, f"{phase.__class__.__name__} should support at least one theory schema"
            assert all(isinstance(schema, TheorySchema) for schema in schemas), f"{phase.__class__.__name__} schemas should be TheorySchema instances"
            
            # Test capabilities
            capabilities = phase.get_capabilities()
            assert isinstance(capabilities, dict), f"{phase.__class__.__name__}.get_capabilities() should return dict"
    
    def test_phase_naming_consistency(self):
        """Test that phase names are consistent"""
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter, Phase3Adapter
        
        phase1 = Phase1Adapter()
        phase2 = Phase2Adapter()
        phase3 = Phase3Adapter()
        
        # Test consistent naming pattern
        assert phase1.get_name() == "Phase 1"
        assert phase2.get_name() == "Phase 2"
        assert phase3.get_name() == "Phase 3"
        
        # Test version consistency
        assert phase1.get_version() == "1.0"
        assert phase2.get_version() == "1.0"
        assert phase3.get_version() == "1.0"
    
    def test_theory_schema_support_hierarchy(self):
        """Test that theory schema support follows expected hierarchy"""
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter, Phase3Adapter
        
        phase1 = Phase1Adapter()
        phase2 = Phase2Adapter()
        phase3 = Phase3Adapter()
        
        # All phases should support MASTER_CONCEPTS
        assert TheorySchema.MASTER_CONCEPTS in phase1.get_supported_theory_schemas()
        assert TheorySchema.MASTER_CONCEPTS in phase2.get_supported_theory_schemas()
        assert TheorySchema.MASTER_CONCEPTS in phase3.get_supported_theory_schemas()
        
        # Phase 2 and 3 should support more advanced schemas
        phase2_schemas = phase2.get_supported_theory_schemas()
        phase3_schemas = phase3.get_supported_theory_schemas()
        
        # Phase 2 and 3 should support THREE_DIMENSIONAL and ORM_METHODOLOGY
        assert TheorySchema.THREE_DIMENSIONAL in phase2_schemas
        assert TheorySchema.ORM_METHODOLOGY in phase2_schemas
        assert TheorySchema.THREE_DIMENSIONAL in phase3_schemas
        assert TheorySchema.ORM_METHODOLOGY in phase3_schemas
        
        # Phase 1 has more limited theory support
        phase1_schemas = phase1.get_supported_theory_schemas()
        assert len(phase1_schemas) <= len(phase2_schemas)
    
    def test_theory_config_validation(self):
        """Test theory configuration validation"""
        from src.core.phase_adapters import Phase1Adapter
        from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig
        
        phase1 = Phase1Adapter()
        
        # Test valid configuration
        valid_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path="src/ontology_library/master_concepts.py"
        )
        
        if os.path.exists("src/ontology_library/master_concepts.py"):
            errors = phase1.validate_theory_config(valid_config)
            assert len(errors) == 0, f"Valid config should have no errors: {errors}"
        
        # Test invalid schema type
        invalid_config = TheoryConfig(
            schema_type=TheorySchema.CUSTOM,  # Phase 1 doesn't support CUSTOM
            concept_library_path="src/ontology_library/master_concepts.py"
        )
        
        errors = phase1.validate_theory_config(invalid_config)
        assert len(errors) > 0, "Invalid schema type should produce errors"
        assert any("Unsupported theory schema" in error for error in errors)
        
        # Test invalid file path
        invalid_path_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path="nonexistent_file.py"
        )
        
        errors = phase1.validate_theory_config(invalid_path_config)
        assert len(errors) > 0, "Invalid file path should produce errors"
        assert any("not found" in error for error in errors)
    
    def test_dual_interface_support(self):
        """Test that phases support both old and new interfaces"""
        from src.core.phase_adapters import Phase1Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest as OldRequest
        from contracts.phase_interfaces.base_graphrag_phase import ProcessingRequest as NewRequest, TheoryConfig
        
        phase1 = Phase1Adapter()
        
        # Test that phase is instance of both interfaces
        assert isinstance(phase1, TheoryAwareGraphRAGPhase)
        
        # Note: Full execution tests would require Neo4j and test documents
        # Here we just test that the execute method exists and can handle type checking
        assert hasattr(phase1, 'execute')
        assert hasattr(phase1, '_execute_original')
        assert hasattr(phase1, '_execute_theory_aware')


class TestRegistryIntegration:
    """Test integration with the global phase registry"""
    
    def test_global_registry_functions(self):
        """Test global registry functions work correctly"""
        from contracts.phase_interfaces.phase_registry import (
            get_theory_registry, register_theory_phase, discover_phases_for_theory
        )
        
        registry = get_theory_registry()
        assert registry is not None
        
        # The registry should be a singleton
        registry2 = get_theory_registry()
        assert registry is registry2
    
    def test_phase_registration_integration(self):
        """Test registering phases with global registry"""
        from contracts.phase_interfaces.phase_registry import register_theory_phase, get_theory_registry
        from src.core.phase_adapters import Phase1Adapter
        
        # Clear registry for test
        registry = get_theory_registry()
        registry._phases.clear()
        registry._theory_compatibility.clear()
        
        # Register a phase
        phase1 = Phase1Adapter()
        register_theory_phase(phase1)
        
        # Test registration worked
        assert "Phase 1" in registry.get_all_phases()
        
        # Test discovery
        master_concepts_phases = registry.get_phases_for_theory(TheorySchema.MASTER_CONCEPTS)
        assert "Phase 1" in master_concepts_phases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])