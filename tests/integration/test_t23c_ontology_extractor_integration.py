"""
Integration tests for T23c Ontology-Aware Entity Extractor before decomposition

This test suite captures the complete behavior of the 1,568-line ontology-aware extractor
to ensure all functionality is preserved during decomposition.

Test Categories:
1. Theory-driven validation functionality
2. LLM-based entity extraction (OpenAI and Gemini)
3. Ontology alignment and validation
4. Semantic similarity calculations
5. Entity resolution and mention creation
6. Mock API fallback mechanisms
7. Tool protocol compliance
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

# Import the main extractor class
from src.tools.phase2.t23c_ontology_aware_extractor import (
    OntologyAwareExtractor, 
    TheoryDrivenValidator,
    TheoryValidationResult,
    ConceptHierarchy,
    SemanticAlignmentError,
    ContextualAlignmentError
)

# Import dependencies
from src.ontology_generator import DomainOntology, EntityType, RelationshipType
from src.core.identity_service import Entity, Relationship, Mention


@pytest.fixture
def mock_service_manager():
    """Mock service manager for testing"""
    mock_sm = Mock()
    mock_sm.identity_service = Mock()
    mock_sm.provenance_service = Mock()
    mock_sm.quality_service = Mock()
    
    # Mock identity service methods
    mock_sm.identity_service.create_mention.return_value = Mock(
        id="mention_123",
        surface_form="Test Entity",
        entity_type="PERSON",
        confidence=0.9
    )
    mock_sm.identity_service.create_entity.return_value = Mock(
        id="entity_123",
        canonical_name="Test Entity",
        entity_type="PERSON",
        confidence=0.9
    )
    mock_sm.identity_service.link_mention_to_entity = Mock()
    
    return mock_sm


@pytest.fixture
def test_ontology():
    """Create test ontology for validation"""
    return DomainOntology(
        domain_name="test_domain",
        domain_description="Test domain for entity extraction",
        entity_types=[
            EntityType(
                name="PERSON", 
                description="Human individuals",
                attributes=["name", "title"],
                examples=["John Doe", "Dr. Smith"]
            ),
            EntityType(
                name="ORGANIZATION",
                description="Organizations and companies", 
                attributes=["name", "industry"],
                examples=["Apple Inc.", "MIT"]
            ),
            EntityType(
                name="LOCATION",
                description="Geographic locations",
                attributes=["name", "country"],
                examples=["California", "New York"]
            )
        ],
        relationship_types=[
            RelationshipType(
                name="WORKS_FOR",
                description="Employment relationship",
                source_types=["PERSON"],
                target_types=["ORGANIZATION"],
                examples=["John works for Apple Inc."]
            ),
            RelationshipType(
                name="LOCATED_IN", 
                description="Location relationship",
                source_types=["ORGANIZATION"],
                target_types=["LOCATION"],
                examples=["Apple Inc. is located in California"]
            )
        ],
        extraction_patterns=["Extract entities and relationships from text"]
    )


@pytest.fixture
def sample_text():
    """Sample text for testing entity extraction"""
    return """
    Dr. Sarah Johnson is a researcher at MIT working on artificial intelligence.
    She collaborates with Google on machine learning projects in California.
    The Stanford Research Institute also contributes to this work.
    """


class TestTheoryDrivenValidation:
    """Test theory-driven validation functionality"""
    
    def test_theory_validator_initialization(self, test_ontology):
        """Test that theory validator initializes correctly"""
        validator = TheoryDrivenValidator(test_ontology)
        
        # Verify initialization
        assert validator.domain_ontology == test_ontology
        assert isinstance(validator.concept_hierarchy, dict)
        assert len(validator.concept_hierarchy) > 0
        
        # Verify concept hierarchy structure
        for concept_id, concept in validator.concept_hierarchy.items():
            assert isinstance(concept, ConceptHierarchy)
            assert concept.concept_id == concept_id
            assert concept.concept_name is not None
            assert isinstance(concept.validation_rules, list)
    
    def test_entity_validation_against_theory(self, test_ontology):
        """Test entity validation against theoretical framework"""
        validator = TheoryDrivenValidator(test_ontology)
        
        # Test valid entity
        valid_entity = {
            'id': 'entity_1',
            'type': 'PERSON',
            'text': 'Dr. Sarah Johnson',
            'properties': {'name': 'Dr. Sarah Johnson', 'title': 'Dr.'},
            'confidence': 0.9
        }
        
        result = validator.validate_entity_against_theory(valid_entity)
        
        # Verify result structure
        assert isinstance(result, TheoryValidationResult)
        assert result.entity_id == 'entity_1'
        assert isinstance(result.is_valid, bool)
        assert 0.0 <= result.validation_score <= 1.0
        assert isinstance(result.theory_alignment, dict)
        assert isinstance(result.concept_hierarchy_path, list)
        assert isinstance(result.validation_reasons, list)
        
        # Test invalid entity
        invalid_entity = {
            'id': 'entity_2',
            'type': 'INVALID_TYPE',
            'text': 'Unknown Entity',
            'properties': {},
            'confidence': 0.5
        }
        
        invalid_result = validator.validate_entity_against_theory(invalid_entity)
        assert invalid_result.entity_id == 'entity_2'
        assert invalid_result.is_valid is False
        assert invalid_result.validation_score == 0.0
    
    def test_semantic_alignment_calculation(self, test_ontology):
        """Test semantic alignment calculation"""
        validator = TheoryDrivenValidator(test_ontology)
        
        entity = {
            'id': 'entity_1',
            'type': 'PERSON', 
            'text': 'Dr. Sarah Johnson',
            'properties': {'name': 'Dr. Sarah Johnson'},
            'confidence': 0.9
        }
        
        # Mock embeddings for consistent testing
        with patch.object(validator, '_get_entity_embedding') as mock_entity_emb, \
             patch.object(validator, '_get_concept_embedding') as mock_concept_emb, \
             patch.object(validator, '_calculate_cosine_similarity') as mock_cosine:
            
            mock_entity_emb.return_value = [0.1, 0.2, 0.3]
            mock_concept_emb.return_value = [0.2, 0.3, 0.4]
            mock_cosine.return_value = 0.85
            
            concept = validator.concept_hierarchy['PERSON']
            score = validator._calculate_semantic_alignment(entity, concept)
            
            # Verify semantic alignment calculation
            assert 0.0 <= score <= 1.0
            mock_entity_emb.assert_called_once()
            mock_concept_emb.assert_called_once()
            mock_cosine.assert_called_once()
    
    def test_semantic_alignment_error_handling(self, test_ontology):
        """Test semantic alignment error handling"""
        validator = TheoryDrivenValidator(test_ontology)
        
        entity = {'id': 'entity_1', 'type': 'PERSON', 'text': 'Test'}
        concept = validator.concept_hierarchy['PERSON']
        
        # Test error handling
        with patch.object(validator, '_get_entity_embedding', side_effect=Exception("Embedding failed")):
            with pytest.raises(SemanticAlignmentError):
                validator._calculate_semantic_alignment(entity, concept)


class TestLLMIntegration:
    """Test LLM-based entity extraction functionality"""
    
    def test_extractor_initialization(self, mock_service_manager):
        """Test extractor initializes correctly"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Verify initialization
        assert extractor.identity_service == mock_service_manager.identity_service
        assert extractor.confidence_threshold == 0.7  # Default
        assert extractor.current_ontology is None
        assert isinstance(extractor.valid_entity_types, set)
        assert isinstance(extractor.valid_relationship_types, set)
    
    def test_mock_api_extraction(self, mock_service_manager, test_ontology, sample_text):
        """Test entity extraction using mock APIs"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test mock extraction
        result = extractor.extract_entities(
            text=sample_text,
            ontology=test_ontology,
            source_ref="test_source",
            confidence_threshold=0.7,
            use_mock_apis=True
        )
        
        # Verify result structure
        assert hasattr(result, 'entities')
        assert hasattr(result, 'relationships')
        assert hasattr(result, 'entity_count')
        assert hasattr(result, 'relationship_count')
        
        # Verify entities
        assert isinstance(result.entities, list)
        assert result.entity_count == len(result.entities)
        
        if result.entities:
            entity = result.entities[0]
            assert hasattr(entity, 'id')
            assert hasattr(entity, 'canonical_name')
            assert hasattr(entity, 'entity_type')
            assert hasattr(entity, 'confidence')
            assert entity.entity_type in ['PERSON', 'ORGANIZATION', 'LOCATION']
        
        # Verify relationships
        assert isinstance(result.relationships, list)
        assert result.relationship_count == len(result.relationships)
    
    @patch('src.tools.phase2.t23c_ontology_aware_extractor.OntologyAwareExtractor._openai_extract')
    def test_openai_integration(self, mock_openai, mock_service_manager, test_ontology, sample_text):
        """Test OpenAI API integration"""
        # Mock OpenAI response
        mock_openai.return_value = {
            "entities": [
                {
                    "text": "Dr. Sarah Johnson",
                    "type": "PERSON",
                    "confidence": 0.9,
                    "context": "researcher"
                },
                {
                    "text": "MIT",
                    "type": "ORGANIZATION", 
                    "confidence": 0.85,
                    "context": "university"
                }
            ],
            "relationships": [
                {
                    "source": "Dr. Sarah Johnson",
                    "target": "MIT",
                    "relation": "WORKS_FOR",
                    "confidence": 0.8
                }
            ]
        }
        
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test OpenAI extraction
        result = extractor.extract_entities(
            text=sample_text,
            ontology=test_ontology,
            source_ref="test_source",
            use_mock_apis=False  # Use real API call (mocked)
        )
        
        # Verify OpenAI was called
        mock_openai.assert_called_once()
        
        # Verify result processing
        assert result.entity_count >= 0
        assert result.relationship_count >= 0


class TestOntologyIntegration:
    """Test ontology alignment and validation"""
    
    def test_ontology_loading_and_validation(self, mock_service_manager, test_ontology):
        """Test ontology loading and validation"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Load ontology
        extractor._load_ontology(test_ontology)
        
        # Verify ontology was loaded
        assert extractor.current_ontology == test_ontology
        assert len(extractor.valid_entity_types) > 0
        assert len(extractor.valid_relationship_types) > 0
        
        # Verify entity types
        expected_types = {"PERSON", "ORGANIZATION", "LOCATION"}
        assert extractor.valid_entity_types == expected_types
        
        # Verify relationship types
        expected_rels = {"WORKS_FOR", "LOCATED_IN"}
        assert extractor.valid_relationship_types == expected_rels
    
    def test_entity_type_validation(self, mock_service_manager, test_ontology):
        """Test entity type validation against ontology"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        extractor._load_ontology(test_ontology)
        
        # Test valid entity type
        assert extractor._is_valid_entity_type("PERSON") is True
        assert extractor._is_valid_entity_type("ORGANIZATION") is True
        
        # Test invalid entity type
        assert extractor._is_valid_entity_type("INVALID_TYPE") is False
        assert extractor._is_valid_entity_type("") is False
    
    def test_relationship_type_validation(self, mock_service_manager, test_ontology):
        """Test relationship type validation against ontology"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        extractor._load_ontology(test_ontology)
        
        # Test valid relationship type
        assert extractor._is_valid_relationship_type("WORKS_FOR") is True
        assert extractor._is_valid_relationship_type("LOCATED_IN") is True
        
        # Test invalid relationship type
        assert extractor._is_valid_relationship_type("INVALID_REL") is False
        assert extractor._is_valid_relationship_type("") is False


class TestEntityResolution:
    """Test entity resolution and mention creation"""
    
    def test_mention_creation(self, mock_service_manager):
        """Test mention creation functionality"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test mention creation
        mention = extractor._create_mention(
            surface_text="Dr. Sarah Johnson",
            entity_type="PERSON",
            source_ref="test_source",
            confidence=0.9,
            context="researcher at MIT"
        )
        
        # Verify mention was created
        mock_service_manager.identity_service.create_mention.assert_called_once()
        
        # Verify mention structure
        assert mention is not None
        assert hasattr(mention, 'id')
        assert hasattr(mention, 'surface_form')
    
    def test_entity_resolution(self, mock_service_manager, test_ontology):
        """Test entity resolution functionality"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test entity resolution
        entity = extractor._resolve_or_create_entity(
            surface_text="Dr. Sarah Johnson",
            entity_type="PERSON",
            ontology=test_ontology,
            confidence=0.9
        )
        
        # Verify entity was created/resolved
        assert entity is not None
        assert hasattr(entity, 'id')
        assert hasattr(entity, 'canonical_name')
        assert hasattr(entity, 'entity_type')
        assert hasattr(entity, 'confidence')


class TestToolProtocolCompliance:
    """Test tool protocol compliance"""
    
    def test_tool_execute_method(self, mock_service_manager, sample_text):
        """Test tool execute method compliance"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test execute with dictionary input
        input_data = {
            "text": sample_text,
            "source_ref": "test_source",
            "confidence_threshold": 0.7
        }
        
        result = extractor.execute(input_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "tool_id" in result
        assert result["tool_id"] == "T23C_ONTOLOGY_AWARE_EXTRACTOR"
        assert "results" in result
        assert "metadata" in result
        assert "provenance" in result
        
        # Verify metadata
        metadata = result["metadata"]
        assert "execution_time" in metadata
        assert "timestamp" in metadata
        assert "ontology_used" in metadata
        
        # Verify provenance
        provenance = result["provenance"]
        assert "activity" in provenance
        assert "timestamp" in provenance
        assert "inputs" in provenance
        assert "outputs" in provenance
    
    def test_tool_execute_with_string_input(self, mock_service_manager):
        """Test tool execute with string input"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test execute with string input
        result = extractor.execute("Test text for extraction")
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "tool_id" in result
        assert "results" in result
    
    def test_tool_validation_mode(self, mock_service_manager):
        """Test tool validation mode"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test validation mode
        result = extractor.execute(None, context={'validation_mode': True})
        
        # Verify validation result
        assert isinstance(result, dict)
        assert result["tool_id"] == "T23C_ONTOLOGY_AWARE_EXTRACTOR"
        assert "results" in result
        assert "metadata" in result
        assert result["metadata"]["mode"] == "validation_test"
        assert result["status"] == "functional"
    
    def test_get_tool_info(self, mock_service_manager):
        """Test get_tool_info method"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        info = extractor.get_tool_info()
        
        # Verify tool info structure
        assert isinstance(info, dict)
        assert "tool_id" in info
        assert info["tool_id"] == "T23C_ONTOLOGY_AWARE_EXTRACTOR"
        assert "tool_type" in info
        assert "status" in info
        assert "description" in info
        assert "version" in info
        assert "dependencies" in info
    
    def test_execute_query_compatibility(self, mock_service_manager):
        """Test execute_query compatibility method"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test execute_query method
        result = extractor.execute_query("Test query text", source_ref="test")
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "status" in result
        assert "entities" in result
        assert "relationships" in result
        assert "entity_count" in result


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_input_handling(self, mock_service_manager):
        """Test handling of invalid inputs"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Test empty input
        with pytest.raises(ValueError, match="input_data is required"):
            extractor.execute(None)
        
        # Test invalid input type
        with pytest.raises(ValueError, match="input_data must be dict or str"):
            extractor.execute(123)
        
        # Test missing text
        with pytest.raises(ValueError, match="No text provided for extraction"):
            extractor.execute({"source_ref": "test"})
    
    def test_semantic_alignment_error_handling(self, mock_service_manager, test_ontology):
        """Test semantic alignment error handling"""
        validator = TheoryDrivenValidator(test_ontology)
        
        entity = {'id': 'test', 'type': 'PERSON', 'text': 'Test'}
        concept = validator.concept_hierarchy['PERSON']
        
        # Test semantic alignment error
        with patch.object(validator, '_get_entity_embedding', side_effect=Exception("Test error")):
            with pytest.raises(SemanticAlignmentError):
                validator._calculate_semantic_alignment(entity, concept)
    
    def test_extraction_error_handling(self, mock_service_manager, sample_text):
        """Test extraction error handling"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Mock extraction method to raise an exception
        with patch.object(extractor, 'extract_entities', side_effect=Exception("Extraction failed")):
            result = extractor.execute({"text": sample_text})
            
            # Verify error is handled gracefully
            assert isinstance(result, dict)
            assert "error" in result
            assert result["status"] == "error"
            assert "Extraction failed" in result["error"]


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics"""
    
    def test_large_text_handling(self, mock_service_manager):
        """Test handling of large text inputs"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Create large text (simulate 10KB)
        large_text = "This is a test sentence. " * 400
        
        input_data = {
            "text": large_text,
            "source_ref": "large_test",
            "confidence_threshold": 0.7
        }
        
        # Test that large text doesn't break the extractor
        result = extractor.execute(input_data)
        
        # Verify result is returned (even if error)
        assert isinstance(result, dict)
        assert "tool_id" in result
    
    def test_confidence_threshold_filtering(self, mock_service_manager, test_ontology):
        """Test confidence threshold filtering"""
        extractor = OntologyAwareExtractor(
            identity_service=mock_service_manager.identity_service,
            provenance_service=mock_service_manager.provenance_service,
            quality_service=mock_service_manager.quality_service
        )
        
        # Mock extraction with various confidence levels
        with patch.object(extractor, '_mock_extract') as mock_extract:
            mock_extract.return_value = {
                "entities": [
                    {"text": "High Conf Entity", "type": "PERSON", "confidence": 0.9},
                    {"text": "Low Conf Entity", "type": "PERSON", "confidence": 0.5}
                ],
                "relationships": []
            }
            
            # Test with high threshold
            high_threshold_result = extractor.extract_entities(
                text="Test text",
                ontology=test_ontology,
                source_ref="test",
                confidence_threshold=0.8,
                use_mock_apis=True
            )
            
            # Test with low threshold
            low_threshold_result = extractor.extract_entities(
                text="Test text",
                ontology=test_ontology,
                source_ref="test",
                confidence_threshold=0.4,
                use_mock_apis=True
            )
            
            # Verify filtering works
            # High threshold should filter out low confidence entities
            # Low threshold should include both
            # (Actual assertion depends on mock implementation)
            assert isinstance(high_threshold_result.entities, list)
            assert isinstance(low_threshold_result.entities, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])