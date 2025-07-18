# tests/integration/test_theory_integration.py
import pytest
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from contracts.phase_interfaces.base_graphrag_phase import *
from contracts.phase_interfaces.phase_registry import TheoryAwarePhaseRegistry
from contracts.validation.theory_validator import TheoryValidator

class TestTheoryIntegration:
    """Integration tests for theory-aware processing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.concept_library_path = "src/ontology_library/master_concepts.py"
        self.test_document = "examples/pdfs/test_document.pdf"
        
        # Check if required files exist, skip tests if they don't
        if not os.path.exists(self.concept_library_path):
            pytest.skip(f"Concept library not found: {self.concept_library_path}")
        if not os.path.exists(self.test_document):
            pytest.skip(f"Test document not found: {self.test_document}")
    
    def test_theory_config_creation(self):
        """Test creation of theory configuration"""
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path,
            validation_enabled=True
        )
        
        assert theory_config.schema_type == TheorySchema.MASTER_CONCEPTS
        assert theory_config.concept_library_path == self.concept_library_path
        assert theory_config.validation_enabled is True
    
    def test_theory_validator_initialization(self):
        """Test TheoryValidator can be initialized"""
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path
        )
        
        validator = TheoryValidator(theory_config)
        assert validator.theory_config == theory_config
        # The validator should load without errors
        assert validator.concept_library is not None
    
    def test_entity_validation(self):
        """Test entity validation against theory schema"""
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path
        )
        
        validator = TheoryValidator(theory_config)
        
        test_entities = [
            {"name": "Tesla Inc.", "type": "ORG"},
            {"name": "Elon Musk", "type": "PERSON"},
            {"name": "Austin", "type": "GPE"}
        ]
        
        score, details = validator.validate_entities(test_entities)
        
        assert score > 0.0
        assert details["total_entities"] == 3
        assert details["validated_entities"] > 0
    
    def test_relationship_validation(self):
        """Test relationship validation against theory schema"""
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path
        )
        
        validator = TheoryValidator(theory_config)
        
        test_relationships = [
            {"source": "Elon Musk", "target": "Tesla Inc.", "type": "CEO_OF"},
            {"source": "Tesla Inc.", "target": "Austin", "type": "LOCATED_IN"}
        ]
        
        score, details = validator.validate_relationships(test_relationships)
        
        assert score > 0.0
        assert details["total_relationships"] == 2
        assert details["validated_relationships"] > 0
    
    def test_concept_mapping(self):
        """Test entity mapping to Master Concept Library"""
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path
        )
        
        validator = TheoryValidator(theory_config)
        
        test_entities = [
            {"name": "Tesla Inc.", "type": "ORG"},
            {"name": "Elon Musk", "type": "PERSON"}
        ]
        
        concept_mapping = validator.map_to_concepts(test_entities)
        
        assert len(concept_mapping) == len(test_entities)
        assert "Tesla Inc." in concept_mapping
        assert "Elon Musk" in concept_mapping
        
        # Check that mappings are sensible
        assert concept_mapping["Tesla Inc."] == "Organization"
        assert concept_mapping["Elon Musk"] == "Human_Agent"
    
    def test_processing_request_creation(self):
        """Test creation of theory-aware processing request"""
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path,
            validation_enabled=True
        )
        
        request = ProcessingRequest(
            documents=[self.test_document],
            queries=["What entities are mentioned?"],
            workflow_id="test_theory_integration",
            theory_config=theory_config
        )
        
        assert len(request.documents) == 1
        assert len(request.queries) == 1
        assert request.workflow_id == "test_theory_integration"
        assert request.theory_config.schema_type == TheorySchema.MASTER_CONCEPTS


class TestPhaseRegistryTheoryDiscovery:
    """Test phase discovery by theory schema"""
    
    def test_phase_registry_creation(self):
        """Test creating a theory-aware phase registry"""
        registry = TheoryAwarePhaseRegistry()
        assert len(registry.get_all_phases()) == 0
    
    def test_phase_registration(self):
        """Test registering phases with theory support"""
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter, Phase3Adapter
        
        registry = TheoryAwarePhaseRegistry()
        
        # Register phases
        phase1 = Phase1Adapter()
        phase2 = Phase2Adapter()
        phase3 = Phase3Adapter()
        
        registry.register_phase(phase1)
        registry.register_phase(phase2)
        registry.register_phase(phase3)
        
        # Test registration
        assert len(registry.get_all_phases()) == 3
        assert "Phase 1" in registry.get_all_phases()
        assert "Phase 2" in registry.get_all_phases()
        assert "Phase 3" in registry.get_all_phases()
    
    def test_theory_compatibility_discovery(self):
        """Test discovery of phases by theory schema"""
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
        
        registry = TheoryAwarePhaseRegistry()
        
        # Register phases
        registry.register_phase(Phase1Adapter())
        registry.register_phase(Phase2Adapter())
        
        # Test theory compatibility discovery
        master_concept_phases = registry.get_phases_for_theory(TheorySchema.MASTER_CONCEPTS)
        assert "Phase 1" in master_concept_phases
        assert "Phase 2" in master_concept_phases
        
        # Test Phase 2 supports THREE_DIMENSIONAL but Phase 1 doesn't
        three_d_phases = registry.get_phases_for_theory(TheorySchema.THREE_DIMENSIONAL)
        assert "Phase 2" in three_d_phases
        assert "Phase 1" not in three_d_phases
    
    def test_capability_discovery(self):
        """Test capability discovery including theory support"""
        from src.core.phase_adapters import Phase1Adapter
        
        registry = TheoryAwarePhaseRegistry()
        phase1 = Phase1Adapter()
        registry.register_phase(phase1)
        
        # Test capability discovery
        phase1_caps = registry.get_phase_capabilities("Phase 1")
        assert "supported_theory_schemas" in phase1_caps
        assert len(phase1_caps["supported_theory_schemas"]) > 0
        assert "master_concepts" in phase1_caps["supported_theory_schemas"]
    
    def test_compatibility_matrix(self):
        """Test compatibility matrix generation"""
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
        
        registry = TheoryAwarePhaseRegistry()
        registry.register_phase(Phase1Adapter())
        registry.register_phase(Phase2Adapter())
        
        matrix = registry.get_compatibility_matrix()
        
        # Test matrix structure
        assert "Phase 1" in matrix
        assert "Phase 2" in matrix
        
        # Test specific compatibility
        assert matrix["Phase 1"]["master_concepts"] is True
        assert matrix["Phase 2"]["master_concepts"] is True
        assert matrix["Phase 2"]["three_dimensional"] is True
        
        # Phase 1 should not support THREE_DIMENSIONAL
        assert matrix["Phase 1"]["three_dimensional"] is False


class TestTheoryAwarePhaseExecution:
    """Test theory-aware phase execution"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.concept_library_path = "src/ontology_library/master_concepts.py"
        self.test_document = "examples/pdfs/test_document.pdf"
        
        # Check if required files exist, skip tests if they don't
        if not os.path.exists(self.concept_library_path):
            pytest.skip(f"Concept library not found: {self.concept_library_path}")
        if not os.path.exists(self.test_document):
            pytest.skip(f"Test document not found: {self.test_document}")
    
    def test_phase1_theory_validation(self):
        """Test Phase 1 with theory validation (if Neo4j is available)"""
        from src.core.phase_adapters import Phase1Adapter
        
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library_path,
            validation_enabled=True
        )
        
        request = ProcessingRequest(
            documents=[self.test_document],
            queries=["What entities are mentioned?"],
            workflow_id="test_theory_integration",
            theory_config=theory_config
        )
        
        phase1 = Phase1Adapter()
        
        # Test theory config validation
        errors = phase1.validate_theory_config(theory_config)
        assert len(errors) == 0  # Should have no validation errors
        
        # Test supported schemas
        schemas = phase1.get_supported_theory_schemas()
        assert TheorySchema.MASTER_CONCEPTS in schemas
        
        # Note: We don't execute the full workflow here because it requires Neo4j
        # In a full integration test, you would execute:
        # result = phase1.execute(request)
        # assert result.status == "success"
        # assert result.theory_validated_result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])