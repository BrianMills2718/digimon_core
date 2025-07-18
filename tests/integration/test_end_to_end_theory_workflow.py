# tests/integration/test_end_to_end_theory_workflow.py
import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from contracts.phase_interfaces.base_graphrag_phase import (
    TheoryConfig, TheorySchema, ProcessingRequest as TheoryRequest
)
from src.core.phase_adapters import Phase1Adapter

class TestEndToEndTheoryWorkflow:
    """Test complete theory-aware workflow execution"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.test_pdf = "examples/pdfs/test_document.pdf"
        self.concept_library = "src/ontology_library/master_concepts.py"
        
        # Skip if required files don't exist
        if not os.path.exists(self.test_pdf):
            pytest.skip(f"Test PDF not found: {self.test_pdf}")
        if not os.path.exists(self.concept_library):
            pytest.skip(f"Concept library not found: {self.concept_library}")
    
    def test_phase1_theory_aware_complete_workflow(self):
        """Test Phase 1 with complete theory-aware processing"""
        
        # Create theory configuration
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        # Create theory-aware processing request
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["What are the main entities mentioned in this document?"],
            workflow_id="end_to_end_theory_test",
            theory_config=theory_config
        )
        
        # Execute Phase 1 with theory validation
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        # Verify result structure
        assert result.status == "success", f"Workflow failed: {result.error_message}"
        assert result.theory_validated_result is not None, "Theory validation result missing"
        
        # Verify theory validation components
        theory_result = result.theory_validated_result
        assert len(theory_result.entities) > 0, "No entities found"
        assert len(theory_result.concept_mapping) > 0, "No concept mapping generated"
        assert theory_result.validation_score > 0.0, "Theory validation score is zero"
        
        # Verify specific theory compliance data
        assert "entity_validation" in theory_result.theory_compliance
        assert "relationship_validation" in theory_result.theory_compliance
        
        # Verify entities have proper concept mappings
        expected_concepts = ["Human_Agent", "Organization", "Geographic_Location", 
                           "Temporal_Entity", "Economic_Value", "Artifact"]
        
        for entity_name, concept in theory_result.concept_mapping.items():
            assert concept in expected_concepts, \
                   f"Unknown concept mapping: {entity_name} -> {concept}"
        
        print(f"✅ End-to-end theory workflow successful:")
        print(f"   Entities: {len(theory_result.entities)}")
        print(f"   Relationships: {len(theory_result.relationships)}")
        print(f"   Validation Score: {theory_result.validation_score:.2f}")
        print(f"   Concept Mappings: {len(theory_result.concept_mapping)}")
        
        return result
    
    def test_phase2_theory_aware_complete_workflow(self):
        """Test Phase 2 with complete theory-aware processing"""
        from src.core.phase_adapters import Phase2Adapter
        
        theory_config = TheoryConfig(
            schema_type=TheorySchema.THREE_DIMENSIONAL,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["Analyze the organizational structure mentioned in this document"],
            workflow_id="end_to_end_theory_phase2_test",
            theory_config=theory_config,
            domain_description="Business and organizational analysis"
        )
        
        phase2 = Phase2Adapter()
        result = phase2.execute(request)
        
        # Phase 2 should support THREE_DIMENSIONAL schema
        assert result.status == "success", f"Phase 2 workflow failed: {result.error_message}"
        assert result.theory_validated_result is not None
        
        theory_result = result.theory_validated_result
        assert theory_result.validation_score > 0.0
        
        print(f"✅ Phase 2 theory workflow successful:")
        print(f"   Validation Score: {theory_result.validation_score:.2f}")
        
        return result
    
    def test_theory_config_validation_error_handling(self):
        """Test error handling for invalid theory configurations"""
        
        # Test invalid concept library path
        invalid_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path="nonexistent_file.py",
            validation_enabled=True
        )
        
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["test query"],
            workflow_id="invalid_config_test",
            theory_config=invalid_config
        )
        
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        # Should fail with proper error message
        assert result.status == "error", "Should fail with invalid config"
        assert "not found" in result.error_message.lower()
        
        print("✅ Error handling for invalid config working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])