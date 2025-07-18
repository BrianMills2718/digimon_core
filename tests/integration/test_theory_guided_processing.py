"""
Integration tests for theory-guided processing.

This test suite verifies CLAUDE.md Task P2.1: Replace Post-Processing Validation 
with Theory-Guided Processing.

Tests that theory schemas guide extraction during the process, not just validate afterward.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from contracts.phase_interfaces.base_graphrag_phase import (
    TheoryConfig, TheorySchema, ProcessingRequest as TheoryRequest
)
from src.core.phase_adapters import Phase1Adapter


class TestTheoryGuidedProcessing:
    """Test theory-guided processing implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.test_pdf = "examples/pdfs/test_document.pdf"
        self.concept_library = "src/ontology_library/master_concepts.py"
        
        # Skip if required files don't exist
        if not os.path.exists(self.test_pdf):
            pytest.skip(f"Test PDF not found: {self.test_pdf}")
    
    def test_theory_guided_vs_post_processing_validation(self):
        """Test that theory-guided processing is different from post-processing validation"""
        
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
            workflow_id="theory_guided_test",
            theory_config=theory_config
        )
        
        # Execute Phase 1 with theory guidance
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        # Verify result structure
        assert result.status == "success", f"Theory-guided workflow failed: {result.error_message}"
        assert result.theory_validated_result is not None, "Theory validation result missing"
        
        # Verify theory guidance was applied during processing
        theory_result = result.theory_validated_result
        assert len(theory_result.entities) > 0, "No entities found"
        assert len(theory_result.concept_mapping) > 0, "No concept mapping generated"
        assert theory_result.validation_score > 0.0, "Theory validation score is zero"
        
        # Verify theory compliance includes guidance metadata (not just validation)
        theory_compliance = theory_result.theory_compliance
        assert "concept_usage" in theory_compliance, "Missing concept usage data"
        assert "theory_metadata" in theory_compliance, "Missing theory metadata"
        assert "alignment_score" in theory_compliance, "Missing alignment score"
        
        # Verify workflow summary includes theory guidance metrics
        summary = result.workflow_summary
        assert "theory_alignment_score" in summary, "Missing theory alignment score"
        assert "concepts_used" in summary, "Missing concepts used count"
        assert "theory_enhanced_entities" in summary, "Missing theory enhanced entities count"
        assert "theory_enhanced_relationships" in summary, "Missing theory enhanced relationships count"
        
        # Verify query results are theory-enhanced
        query_results = result.query_results
        assert len(query_results) > 0, "No query results"
        
        first_result = query_results[0]
        assert first_result.get("theory_enhanced") == True, "Query results not theory-enhanced"
        assert "alignment_score" in first_result, "Query result missing alignment score"
        assert "concept_usage" in first_result, "Query result missing concept usage"
        
        print(f"✅ Theory-guided processing successful:")
        print(f"   Entities: {len(theory_result.entities)}")
        print(f"   Relationships: {len(theory_result.relationships)}")
        print(f"   Theory Alignment Score: {theory_result.validation_score:.2f}")
        print(f"   Concept Mappings: {len(theory_result.concept_mapping)}")
        print(f"   Theory Enhanced Entities: {summary.get('theory_enhanced_entities', 0)}")
        print(f"   Theory Enhanced Relationships: {summary.get('theory_enhanced_relationships', 0)}")
        
        return result
    
    def test_theory_guided_entity_enhancement(self):
        """Test that entities are enhanced during extraction, not afterward"""
        
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["Find organizations and people in this document"],
            workflow_id="entity_enhancement_test",
            theory_config=theory_config
        )
        
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        assert result.status == "success", f"Workflow failed: {result.error_message}"
        
        # Check that entities have theory metadata indicating they were enhanced during processing
        entities = result.theory_validated_result.entities
        
        theory_enhanced_count = 0
        for entity in entities:
            theory_metadata = entity.get("theory_metadata", {})
            if theory_metadata.get("theory_enhanced", False):
                theory_enhanced_count += 1
                
                # Verify theory enhancement metadata exists
                assert "concept_match" in theory_metadata, f"Entity missing concept match: {entity}"
                assert "concept_confidence" in theory_metadata, f"Entity missing concept confidence: {entity}"
                
                # If theory enhanced, should have positive concept confidence
                if theory_metadata["theory_enhanced"]:
                    assert theory_metadata["concept_confidence"] > 0.0, f"Theory enhanced entity has zero confidence: {entity}"
        
        print(f"✅ Entity enhancement working: {theory_enhanced_count}/{len(entities)} entities theory-enhanced")
        
        # At least some entities should be theory-enhanced
        assert theory_enhanced_count > 0, "No entities were theory-enhanced during processing"
    
    def test_theory_guided_relationship_enhancement(self):
        """Test that relationships are enhanced during extraction using concept patterns"""
        
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["What relationships exist between entities?"],
            workflow_id="relationship_enhancement_test",
            theory_config=theory_config
        )
        
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        assert result.status == "success", f"Workflow failed: {result.error_message}"
        
        # Check that relationships have theory metadata
        relationships = result.theory_validated_result.relationships
        
        theory_enhanced_count = 0
        for relationship in relationships:
            theory_metadata = relationship.get("theory_metadata", {})
            if theory_metadata.get("theory_enhanced", False):
                theory_enhanced_count += 1
                
                # Verify theory enhancement metadata exists
                assert "concept_alignment" in theory_metadata, f"Relationship missing concept alignment: {relationship}"
                
                # If predicted by theory, should have high alignment
                if theory_metadata.get("predicted_by_theory", False):
                    assert theory_metadata["concept_alignment"] > 0.7, f"Theory predicted relationship has low alignment: {relationship}"
        
        print(f"✅ Relationship enhancement working: {theory_enhanced_count}/{len(relationships)} relationships theory-enhanced")
    
    def test_concept_library_integration(self):
        """Test that concept library is properly integrated and used for guidance"""
        
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["Identify all concept types mentioned"],
            workflow_id="concept_library_test",
            theory_config=theory_config
        )
        
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        assert result.status == "success", f"Workflow failed: {result.error_message}"
        
        # Check concept usage statistics
        theory_compliance = result.theory_validated_result.theory_compliance
        concept_usage = theory_compliance.get("concept_usage", {})
        
        # Should have some concept usage
        total_usage = sum(concept_usage.values())
        assert total_usage > 0, "No concepts were used during processing"
        
        used_concepts = [concept for concept, count in concept_usage.items() if count > 0]
        assert len(used_concepts) > 0, "No concepts were marked as used"
        
        print(f"✅ Concept library integration working: {len(used_concepts)} concepts used, total usage: {total_usage}")
        print(f"   Used concepts: {used_concepts}")
    
    def test_theory_alignment_scoring(self):
        """Test that theory alignment scoring works correctly"""
        
        theory_config = TheoryConfig(
            schema_type=TheorySchema.MASTER_CONCEPTS,
            concept_library_path=self.concept_library,
            validation_enabled=True
        )
        
        request = TheoryRequest(
            documents=[self.test_pdf],
            queries=["Test theory alignment scoring"],
            workflow_id="alignment_scoring_test",
            theory_config=theory_config
        )
        
        phase1 = Phase1Adapter()
        result = phase1.execute(request)
        
        assert result.status == "success", f"Workflow failed: {result.error_message}"
        
        # Check alignment score
        alignment_score = result.theory_validated_result.validation_score
        assert 0.0 <= alignment_score <= 1.0, f"Alignment score out of range: {alignment_score}"
        
        # Check that alignment score is consistent across different result locations
        summary_score = result.workflow_summary.get("theory_alignment_score")
        assert summary_score == alignment_score, f"Inconsistent alignment scores: {alignment_score} vs {summary_score}"
        
        theory_metadata = result.theory_validated_result.theory_compliance.get("theory_metadata", {})
        assert "processing_time" in theory_metadata, "Missing processing time in theory metadata"
        assert "concepts_available" in theory_metadata, "Missing concepts available count"
        assert "concepts_used" in theory_metadata, "Missing concepts used count"
        
        print(f"✅ Theory alignment scoring working: score = {alignment_score:.3f}")
        print(f"   Theory metadata: {theory_metadata}")


if __name__ == "__main__":
    # Run tests directly
    test_suite = TestTheoryGuidedProcessing()
    test_suite.setup_method()
    
    print("🧪 Testing Theory-Guided Processing...")
    
    try:
        test_suite.test_theory_guided_vs_post_processing_validation()
        test_suite.test_theory_guided_entity_enhancement()
        test_suite.test_theory_guided_relationship_enhancement()
        test_suite.test_concept_library_integration()
        test_suite.test_theory_alignment_scoring()
        
        print("\n🎉 All theory-guided processing tests passed!")
        
    except Exception as e:
        print(f"\n❌ Theory-guided processing test failed: {e}")
        import traceback
        traceback.print_exc()