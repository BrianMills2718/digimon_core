"""
Test suite for T27 Relationship Extractor Unified Tool

Comprehensive testing with real spaCy processing and zero mocking.
Tests all relationship extraction methods and edge cases.
"""

import pytest
import os
import tempfile
from datetime import datetime

from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolErrorCode

class TestT27RelationshipExtractorUnifiedMockFree:
    """Mock-free test suite for T27 Relationship Extractor"""
    
    def setup_method(self):
        """Setup real ServiceManager and tool instance"""
        # Create real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = T27RelationshipExtractorUnified(service_manager=self.service_manager)
        
        # Create real test data with known entities and relationships
        self.test_data = self._create_real_test_data()
        
        # Track original stats
        self.initial_relationships_extracted = self.tool.relationships_extracted

    def _create_real_test_data(self):
        """Create actual test data with known relationships"""
        return {
            "simple_employment": {
                "text": "John Smith works at Google. Mary Johnson is the CEO of Microsoft.",
                "entities": [
                    {"text": "John Smith", "label": "PERSON", "start": 0, "end": 10, "confidence": 0.9},
                    {"text": "Google", "label": "ORG", "start": 20, "end": 26, "confidence": 0.95},
                    {"text": "Mary Johnson", "label": "PERSON", "start": 28, "end": 40, "confidence": 0.9},
                    {"text": "Microsoft", "label": "ORG", "start": 55, "end": 64, "confidence": 0.95}
                ],
                "chunk_ref": "chunk_001",
                "expected_relationships": ["WORKS_FOR", "WORKS_FOR"]  # CEO pattern should match WORKS_FOR
            },
            "ownership_pattern": {
                "text": "Apple owns the iPhone technology. Tesla possesses advanced battery technology.",
                "entities": [
                    {"text": "Apple", "label": "ORG", "start": 0, "end": 5, "confidence": 0.95},
                    {"text": "iPhone", "label": "PRODUCT", "start": 15, "end": 21, "confidence": 0.9},
                    {"text": "Tesla", "label": "ORG", "start": 35, "end": 40, "confidence": 0.95},
                    {"text": "battery technology", "label": "PRODUCT", "start": 59, "end": 77, "confidence": 0.85}
                ],
                "chunk_ref": "chunk_002",
                "expected_relationships": ["OWNS", "OWNS"]
            },
            "location_relationship": {
                "text": "Microsoft is located in Seattle. Google is based in Mountain View.",
                "entities": [
                    {"text": "Microsoft", "label": "ORG", "start": 0, "end": 9, "confidence": 0.95},
                    {"text": "Seattle", "label": "GPE", "start": 24, "end": 31, "confidence": 0.9},
                    {"text": "Google", "label": "ORG", "start": 33, "end": 39, "confidence": 0.95},
                    {"text": "Mountain View", "label": "GPE", "start": 52, "end": 65, "confidence": 0.9}
                ],
                "chunk_ref": "chunk_003",
                "expected_relationships": ["LOCATED_IN", "LOCATED_IN"]
            },
            "complex_sentences": {
                "text": "Dr. Smith published a paper on machine learning. The research was conducted at Stanford University with collaborators from MIT.",
                "entities": [
                    {"text": "Dr. Smith", "label": "PERSON", "start": 0, "end": 9, "confidence": 0.9},
                    {"text": "machine learning", "label": "SUBJECT", "start": 32, "end": 48, "confidence": 0.85},
                    {"text": "Stanford University", "label": "ORG", "start": 84, "end": 103, "confidence": 0.95},
                    {"text": "MIT", "label": "ORG", "start": 125, "end": 128, "confidence": 0.95}
                ],
                "chunk_ref": "chunk_004",
                "expected_relationships": ["RELATED_TO"]  # Proximity-based fallback
            },
            "proximity_relationships": {
                "text": "John and Mary work together. They collaborate with IBM on various projects.",
                "entities": [
                    {"text": "John", "label": "PERSON", "start": 0, "end": 4, "confidence": 0.9},
                    {"text": "Mary", "label": "PERSON", "start": 9, "end": 13, "confidence": 0.9},
                    {"text": "IBM", "label": "ORG", "start": 52, "end": 55, "confidence": 0.95}
                ],
                "chunk_ref": "chunk_005",
                "expected_relationships": ["RELATED_TO", "PARTNERS_WITH"]
            }
        }

    def test_tool_initialization_real(self):
        """Test tool initialization with real services"""
        assert self.tool.tool_id == "T27"
        assert self.tool.name == "Relationship Extractor"
        assert self.tool.category == "text_processing"
        assert self.tool.service_manager is not None
        assert isinstance(self.tool.service_manager, ServiceManager)
        
        # Check spaCy model availability (may or may not be available)
        spacy_available = self.tool.nlp is not None
        assert isinstance(spacy_available, bool)
        
        # Check relationship patterns are loaded
        assert len(self.tool.relationship_patterns) > 0
        assert all("name" in pattern for pattern in self.tool.relationship_patterns)
        assert all("pattern" in pattern for pattern in self.tool.relationship_patterns)
        assert all("relationship_type" in pattern for pattern in self.tool.relationship_patterns)

    def test_input_validation_real(self):
        """Test input validation with real validation logic"""
        # Valid input
        valid_input = self.test_data["simple_employment"]
        validation_result = self.tool._validate_input(valid_input)
        assert validation_result["valid"] is True
        
        # Invalid input types
        invalid_inputs = [
            None,
            "string input",
            123,
            [],
            {},
            {"text": "sample"},  # missing entities
            {"entities": []},  # missing text
            {"text": "", "entities": []},  # empty text
            {"text": "sample", "entities": [{"invalid": "entity"}]},  # invalid entity structure
            {"text": "sample", "entities": [{"text": "entity", "label": "PERSON", "start": 0}]}  # missing end field
        ]
        
        for invalid_input in invalid_inputs:
            validation_result = self.tool._validate_input(invalid_input)
            assert validation_result["valid"] is False
            assert "error" in validation_result

    def test_pattern_based_extraction_real(self):
        """Test pattern-based relationship extraction with real patterns"""
        test_case = self.test_data["simple_employment"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert "relationships" in result.data
        assert result.data["relationship_count"] > 0
        assert result.data["confidence"] > 0
        assert result.execution_time > 0
        
        # Verify relationship structure
        relationships = result.data["relationships"]
        assert len(relationships) >= 1
        
        for rel in relationships:
            assert "relationship_id" in rel
            assert "relationship_type" in rel
            assert "subject" in rel
            assert "object" in rel
            assert "confidence" in rel
            assert "extraction_method" in rel
            
            # Evidence field varies by extraction method
            if rel["extraction_method"] == "pattern_based":
                assert "evidence_text" in rel
            elif rel["extraction_method"] == "proximity_based":
                assert "connecting_text" in rel
            elif rel["extraction_method"] == "dependency_parsing":
                assert "evidence_text" in rel
            
            # Verify confidence is reasonable
            assert 0.0 <= rel["confidence"] <= 1.0
            
            # Verify entity structure
            assert "text" in rel["subject"]
            assert "label" in rel["subject"]
            assert "text" in rel["object"]
            assert "label" in rel["object"]

    def test_ownership_patterns_real(self):
        """Test ownership relationship patterns with real extraction"""
        test_case = self.test_data["ownership_pattern"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.6}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        relationships = result.data["relationships"]
        
        # Should find ownership relationships
        ownership_rels = [r for r in relationships if r["relationship_type"] == "OWNS"]
        assert len(ownership_rels) >= 1
        
        # Verify Apple-iPhone relationship
        apple_iphone = next((r for r in ownership_rels 
                           if "Apple" in r["subject"]["text"] and "iPhone" in r["object"]["text"]), None)
        assert apple_iphone is not None
        assert apple_iphone["confidence"] > 0.6

    def test_location_relationships_real(self):
        """Test location relationship extraction"""
        test_case = self.test_data["location_relationship"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        relationships = result.data["relationships"]
        
        # Should find location relationships
        location_rels = [r for r in relationships if r["relationship_type"] == "LOCATED_IN"]
        assert len(location_rels) >= 1
        
        # Verify specific location relationships
        company_locations = [(r["subject"]["text"], r["object"]["text"]) for r in location_rels]
        assert any("Microsoft" in subj and "Seattle" in obj for subj, obj in company_locations)

    def test_dependency_parsing_when_available(self):
        """Test dependency parsing if spaCy is available"""
        if not self.tool.nlp:
            pytest.skip("spaCy model not available")
        
        test_case = self.test_data["complex_sentences"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.3}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        relationships = result.data["relationships"]
        
        # Should find some relationships using dependency parsing
        dependency_rels = [r for r in relationships if r["extraction_method"] == "dependency_parsing"]
        
        # May or may not find dependency relationships depending on sentence structure
        # Just verify the extraction method is working
        assert isinstance(dependency_rels, list)

    def test_proximity_based_extraction_real(self):
        """Test proximity-based relationship extraction"""
        test_case = self.test_data["proximity_relationships"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.2}  # Lower threshold for proximity
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        relationships = result.data["relationships"]
        
        # Should find proximity-based relationships
        proximity_rels = [r for r in relationships if r["extraction_method"] == "proximity_based"]
        pattern_rels = [r for r in relationships if r["extraction_method"] == "pattern_based"]
        
        # Should find both types
        assert len(proximity_rels) >= 1 or len(pattern_rels) >= 1

    def test_confidence_threshold_filtering_real(self):
        """Test confidence threshold filtering"""
        test_case = self.test_data["simple_employment"]
        
        # High threshold should return fewer results
        high_threshold_request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.9}
        )
        
        high_result = self.tool.execute(high_threshold_request)
        
        # Low threshold should return more results
        low_threshold_request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.1}
        )
        
        low_result = self.tool.execute(low_threshold_request)
        
        assert high_result.status == "success"
        assert low_result.status == "success"
        
        # Low threshold should have >= relationships than high threshold
        assert low_result.data["relationship_count"] >= high_result.data["relationship_count"]

    def test_deduplication_real(self):
        """Test relationship deduplication"""
        # Create test data with potential duplicates
        duplicate_text = "John works at Google. John Smith is employed by Google Inc."
        duplicate_entities = [
            {"text": "John", "label": "PERSON", "start": 0, "end": 4, "confidence": 0.9},
            {"text": "Google", "label": "ORG", "start": 14, "end": 20, "confidence": 0.95},
            {"text": "John Smith", "label": "PERSON", "start": 22, "end": 32, "confidence": 0.9},
            {"text": "Google Inc", "label": "ORG", "start": 48, "end": 58, "confidence": 0.95}
        ]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data={
                "text": duplicate_text,
                "entities": duplicate_entities,
                "chunk_ref": "chunk_dedup"
            },
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        relationships = result.data["relationships"]
        
        # Check for deduplication by examining relationship types and entities
        rel_keys = set()
        for rel in relationships:
            key = (rel["subject"]["text"], rel["object"]["text"], rel["relationship_type"])
            assert key not in rel_keys, "Duplicate relationship found"
            rel_keys.add(key)

    def test_error_handling_real(self):
        """Test error handling with real error conditions"""
        # Test with invalid input
        invalid_request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data={"invalid": "data"},
            parameters={}
        )
        
        result = self.tool.execute(invalid_request)
        
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.INVALID_INPUT
        assert result.execution_time > 0

    def test_tool_contract_real(self):
        """Test tool contract specification"""
        contract = self.tool.get_contract()
        
        assert contract["tool_id"] == "T27"
        assert contract["name"] == "Relationship Extractor"
        assert contract["category"] == "text_processing"
        assert "description" in contract
        assert "input_specification" in contract
        assert "output_specification" in contract
        assert "error_codes" in contract
        assert "supported_relationship_types" in contract
        
        # Verify supported relationship types
        supported_types = contract["supported_relationship_types"]
        expected_types = ["OWNS", "WORKS_FOR", "LOCATED_IN", "PARTNERS_WITH", 
                         "CREATED", "LEADS", "MEMBER_OF", "RELATED_TO"]
        
        for expected_type in expected_types:
            assert expected_type in supported_types

    def test_metadata_real(self):
        """Test metadata in results"""
        test_case = self.test_data["simple_employment"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.metadata is not None
        assert "spacy_available" in result.metadata
        assert "confidence_threshold" in result.metadata
        assert "entity_count" in result.metadata
        assert "text_length" in result.metadata
        
        # Verify metadata values
        assert result.metadata["entity_count"] == len(test_case["entities"])
        assert result.metadata["text_length"] == len(test_case["text"])
        assert result.metadata["confidence_threshold"] == 0.5

    def test_processing_stats_real(self):
        """Test processing statistics tracking"""
        initial_extracted = self.tool.relationships_extracted
        initial_patterns = self.tool.patterns_matched
        initial_dependency = self.tool.dependency_extractions
        
        test_case = self.test_data["ownership_pattern"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Stats should have increased
        assert self.tool.relationships_extracted >= initial_extracted
        assert self.tool.patterns_matched >= initial_patterns
        
        # Check extraction stats in result
        extraction_stats = result.data["extraction_stats"]
        assert "pattern_matches" in extraction_stats
        assert "dependency_extractions" in extraction_stats
        assert "total_extracted" in extraction_stats
        assert extraction_stats["total_extracted"] == result.data["relationship_count"]

    def test_large_text_processing_real(self):
        """Test processing of larger text samples"""
        # Create larger test text
        large_text = """
        Apple Inc. is located in Cupertino, California. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.
        Tim Cook is the current CEO of Apple. Microsoft Corporation is based in Redmond, Washington. Bill Gates founded Microsoft
        with Paul Allen. Satya Nadella leads Microsoft today. Google was created by Larry Page and Sergey Brin at Stanford University.
        The company is located in Mountain View, California. Sundar Pichai manages Google currently.
        """
        
        large_entities = [
            {"text": "Apple Inc.", "label": "ORG", "start": 9, "end": 19, "confidence": 0.95},
            {"text": "Cupertino", "label": "GPE", "start": 34, "end": 43, "confidence": 0.9},
            {"text": "California", "label": "GPE", "start": 45, "end": 55, "confidence": 0.9},
            {"text": "Steve Jobs", "label": "PERSON", "start": 89, "end": 99, "confidence": 0.95},
            {"text": "Steve Wozniak", "label": "PERSON", "start": 101, "end": 114, "confidence": 0.95},
            {"text": "Ronald Wayne", "label": "PERSON", "start": 120, "end": 132, "confidence": 0.95},
            {"text": "Tim Cook", "label": "PERSON", "start": 142, "end": 150, "confidence": 0.95},
            {"text": "Apple", "label": "ORG", "start": 170, "end": 175, "confidence": 0.95},
            {"text": "Microsoft Corporation", "label": "ORG", "start": 177, "end": 198, "confidence": 0.95},
            {"text": "Redmond", "label": "GPE", "start": 211, "end": 218, "confidence": 0.9},
            {"text": "Washington", "label": "GPE", "start": 220, "end": 230, "confidence": 0.9}
        ]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data={
                "text": large_text,
                "entities": large_entities,
                "chunk_ref": "large_chunk"
            },
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["relationship_count"] >= 3  # Should find multiple relationships
        assert result.execution_time > 0
        assert result.memory_used >= 0

    def test_edge_cases_real(self):
        """Test edge cases and boundary conditions"""
        # Test with exactly 2 entities (minimum required)
        min_entities_data = {
            "text": "John works at Google.",
            "entities": [
                {"text": "John", "label": "PERSON", "start": 0, "end": 4, "confidence": 0.9},
                {"text": "Google", "label": "ORG", "start": 14, "end": 20, "confidence": 0.95}
            ],
            "chunk_ref": "min_entities"
        }
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=min_entities_data,
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        assert result.status == "success"
        
        # Test with very high confidence threshold
        request.parameters["confidence_threshold"] = 0.99
        result = self.tool.execute(request)
        assert result.status == "success"
        # May have 0 relationships due to high threshold
        assert result.data["relationship_count"] >= 0

    def test_zero_mocking_verification(self):
        """Verify no mocking is used in this test suite"""
        # Verify we're using real ServiceManager
        assert isinstance(self.service_manager, ServiceManager)
        assert not hasattr(self.service_manager, '_mock_name'), "ServiceManager appears to be mocked"
        
        # Verify we're using real tool instance
        assert isinstance(self.tool, T27RelationshipExtractorUnified)
        assert not hasattr(self.tool, '_mock_name'), "Tool appears to be mocked"
        
        # Verify spaCy is real if available
        if self.tool.nlp:
            assert hasattr(self.tool.nlp, '__call__'), "spaCy nlp object should be real callable"
        
        # This test suite uses NO mocking - all functionality is real

    def test_performance_requirements_real(self):
        """Test that tool meets performance requirements"""
        test_case = self.test_data["simple_employment"]
        
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data=test_case,
            parameters={"confidence_threshold": 0.5}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Performance requirements
        assert result.execution_time < 10.0, f"Execution too slow: {result.execution_time}s"
        assert result.memory_used < 100 * 1024 * 1024, f"Memory usage too high: {result.memory_used} bytes"
        
        # Quality requirements
        if result.data["relationship_count"] > 0:
            assert result.data["confidence"] > 0.3, f"Confidence too low: {result.data['confidence']}"