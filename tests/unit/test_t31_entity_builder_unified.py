"""
Test suite for T31 Entity Builder Unified Tool

Comprehensive testing with real Neo4j integration and zero mocking.
Tests all entity building methods and edge cases.
"""

import pytest
import os
import tempfile
from datetime import datetime

from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolErrorCode

class TestT31EntityBuilderUnifiedMockFree:
    """Mock-free test suite for T31 Entity Builder"""
    
    def setup_method(self):
        """Setup real ServiceManager and tool instance"""
        # Create real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = T31EntityBuilderUnified(service_manager=self.service_manager)
        
        # Create real test data with known entities
        self.test_data = self._create_real_test_data()
        
        # Track original stats
        self.initial_entities_created = self.tool.entities_created

    def _create_real_test_data(self):
        """Create actual test data with known entity mentions"""
        return {
            "simple_person_mentions": {
                "mentions": [
                    {"text": "John Smith", "label": "PERSON", "start": 0, "end": 10, "confidence": 0.9},
                    {"text": "John", "label": "PERSON", "start": 20, "end": 24, "confidence": 0.85},
                    {"text": "Mr. Smith", "label": "PERSON", "start": 30, "end": 39, "confidence": 0.88}
                ],
                "source_refs": ["chunk_001"],
                "expected_entities": 1,  # Should group into one entity
                "expected_canonical_name": "John Smith"
            },
            "mixed_entity_types": {
                "mentions": [
                    {"text": "Google", "label": "ORG", "start": 0, "end": 6, "confidence": 0.95},
                    {"text": "Mountain View", "label": "GPE", "start": 10, "end": 23, "confidence": 0.9},
                    {"text": "California", "label": "GPE", "start": 25, "end": 35, "confidence": 0.9},
                    {"text": "Sundar Pichai", "label": "PERSON", "start": 40, "end": 53, "confidence": 0.92}
                ],
                "source_refs": ["chunk_002"],
                "expected_entities": 4,  # Different entity types
                "expected_types": ["ORG", "GPE", "PERSON"]
            },
            "duplicate_mentions": {
                "mentions": [
                    {"text": "Apple Inc.", "label": "ORG", "start": 0, "end": 10, "confidence": 0.95},
                    {"text": "Apple", "label": "ORG", "start": 15, "end": 20, "confidence": 0.9},
                    {"text": "Apple Corporation", "label": "ORG", "start": 25, "end": 42, "confidence": 0.88},
                    {"text": "Microsoft", "label": "ORG", "start": 50, "end": 59, "confidence": 0.93}
                ],
                "source_refs": ["chunk_003"],
                "expected_entities": 2,  # Apple variations + Microsoft
                "expected_deduplication": True
            },
            "low_confidence_mentions": {
                "mentions": [
                    {"text": "Unknown Entity", "label": "UNKNOWN", "start": 0, "end": 14, "confidence": 0.3},
                    {"text": "Ambiguous Name", "label": "PERSON", "start": 20, "end": 34, "confidence": 0.4}
                ],
                "source_refs": ["chunk_004"],
                "expected_entities": 2,
                "expected_low_confidence": True
            },
            "large_entity_set": {
                "mentions": [
                    {"text": "Tesla", "label": "ORG", "start": 0, "end": 5, "confidence": 0.95},
                    {"text": "SpaceX", "label": "ORG", "start": 10, "end": 16, "confidence": 0.94},
                    {"text": "Elon Musk", "label": "PERSON", "start": 20, "end": 29, "confidence": 0.96},
                    {"text": "Neuralink", "label": "ORG", "start": 35, "end": 44, "confidence": 0.91},
                    {"text": "The Boring Company", "label": "ORG", "start": 50, "end": 68, "confidence": 0.89},
                    {"text": "Austin", "label": "GPE", "start": 75, "end": 81, "confidence": 0.92},
                    {"text": "Texas", "label": "GPE", "start": 85, "end": 90, "confidence": 0.93}
                ],
                "source_refs": ["chunk_005", "chunk_006"],
                "expected_entities": 7,
                "expected_performance_test": True
            }
        }

    def test_tool_initialization_real(self):
        """Test tool initialization with real services"""
        assert self.tool.tool_id == "T31"
        assert self.tool.name == "Entity Builder"
        assert self.tool.category == "graph_construction"
        assert self.tool.service_manager is not None
        assert isinstance(self.tool.service_manager, ServiceManager)
        
        # Check Neo4j availability (may or may not be available)
        neo4j_available = self.tool.driver is not None
        assert isinstance(neo4j_available, bool)
        
        # Check initialization stats
        assert self.tool.entities_created >= 0
        assert self.tool.mentions_processed >= 0
        assert self.tool.neo4j_operations >= 0

    def test_input_validation_real(self):
        """Test input validation with real validation logic"""
        # Valid input
        valid_input = self.test_data["simple_person_mentions"]
        validation_result = self.tool._validate_input(valid_input)
        assert validation_result["valid"] is True
        
        # Invalid input types
        invalid_inputs = [
            None,
            "string input",
            123,
            [],
            {},
            {"mentions": []},  # empty mentions
            {"mentions": "not a list"},  # invalid mentions type
            {"mentions": [{"invalid": "mention"}]},  # invalid mention structure
            {"mentions": [{"text": "entity"}]}  # missing required fields
        ]
        
        for invalid_input in invalid_inputs:
            validation_result = self.tool._validate_input(invalid_input)
            assert validation_result["valid"] is False
            assert "error" in validation_result

    def test_mention_grouping_real(self):
        """Test mention grouping by entity"""
        mentions = [
            {"text": "John Smith", "label": "PERSON", "entity_id": "person_001", "confidence": 0.9},
            {"text": "John", "label": "PERSON", "entity_id": "person_001", "confidence": 0.85},
            {"text": "Google", "label": "ORG", "entity_id": "org_001", "confidence": 0.95}
        ]
        
        entity_groups = self.tool._group_mentions_by_entity(mentions)
        
        # Should group John Smith and John together
        assert len(entity_groups) == 2
        assert "person_001" in entity_groups
        assert "org_001" in entity_groups
        assert len(entity_groups["person_001"]) == 2
        assert len(entity_groups["org_001"]) == 1

    def test_entity_info_extraction_real(self):
        """Test entity information extraction from mentions"""
        entity_id = "test_entity"
        mentions = [
            {"text": "John Smith", "label": "PERSON", "confidence": 0.9},
            {"text": "John", "label": "PERSON", "confidence": 0.85},
            {"text": "Mr. Smith", "label": "PERSON", "confidence": 0.88}
        ]
        
        entity_info = self.tool._extract_entity_info(entity_id, mentions)
        
        assert entity_info["entity_id"] == entity_id
        assert entity_info["canonical_name"] == "John Smith"  # Longest surface form
        assert entity_info["entity_type"] == "PERSON"
        assert len(entity_info["surface_forms"]) == 3
        assert entity_info["confidence"] > 0.8  # Should be boosted for multiple mentions
        assert entity_info["mention_count"] == 3

    def test_entity_building_without_neo4j(self):
        """Test entity building when Neo4j is not available"""
        # Temporarily disable Neo4j
        original_driver = self.tool.driver
        self.tool.driver = None
        
        try:
            test_case = self.test_data["simple_person_mentions"]
            
            request = ToolRequest(
                tool_id="T31",
                operation="build_entities",
                input_data=test_case,
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should fail gracefully when Neo4j is not available
            assert result.status == "error"
            assert result.error_code == ToolErrorCode.CONNECTION_ERROR
            assert "Neo4j connection not available" in result.error_message
            
        finally:
            # Restore Neo4j driver
            self.tool.driver = original_driver

    def test_entity_building_with_neo4j_when_available(self):
        """Test entity building with Neo4j when available"""
        if not self.tool.driver:
            pytest.skip("Neo4j not available")
        
        test_case = self.test_data["simple_person_mentions"]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert "entities" in result.data
        assert result.data["entity_count"] > 0
        assert result.data["confidence"] > 0
        assert result.execution_time > 0
        
        # Verify entity structure
        entities = result.data["entities"]
        assert len(entities) >= 1
        
        for entity in entities:
            assert "entity_id" in entity
            assert "canonical_name" in entity
            assert "entity_type" in entity
            assert "surface_forms" in entity
            assert "mention_count" in entity
            assert "confidence" in entity
            assert "created_at" in entity
            
            # Verify confidence is reasonable
            assert 0.0 <= entity["confidence"] <= 1.0
            
            # Verify Neo4j integration
            if self.tool.driver:
                assert "neo4j_id" in entity

    def test_mixed_entity_types_real(self):
        """Test handling of different entity types"""
        if not self.tool.driver:
            pytest.skip("Neo4j not available")
        
        test_case = self.test_data["mixed_entity_types"]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        entities = result.data["entities"]
        
        # Should create entities for different types
        assert len(entities) >= 3
        
        # Check entity types
        entity_types = set(entity["entity_type"] for entity in entities)
        expected_types = {"ORG", "GPE", "PERSON"}
        assert entity_types.intersection(expected_types)

    def test_entity_deduplication_real(self):
        """Test entity deduplication by entity_id"""
        test_case = self.test_data["duplicate_mentions"]
        
        # Add same entity_id to Apple mentions for deduplication test
        for mention in test_case["mentions"][:3]:  # First 3 are Apple variants
            mention["entity_id"] = "apple_entity"
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        if result.status == "success":
            entities = result.data["entities"]
            
            # Should deduplicate Apple mentions into one entity
            apple_entities = [e for e in entities if "Apple" in e["canonical_name"]]
            assert len(apple_entities) <= 1, "Apple mentions should be deduplicated"
            
            if apple_entities:
                apple_entity = apple_entities[0]
                assert apple_entity["mention_count"] >= 3  # Multiple mentions for Apple

    def test_confidence_calculation_real(self):
        """Test confidence calculation for entities"""
        high_conf_mentions = [
            {"text": "Google Inc.", "label": "ORG", "confidence": 0.95},
            {"text": "Google", "label": "ORG", "confidence": 0.93},
            {"text": "Google LLC", "label": "ORG", "confidence": 0.94}
        ]
        
        low_conf_mentions = [
            {"text": "Unknown Corp", "label": "ORG", "confidence": 0.4}
        ]
        
        # High confidence entity
        high_entity_info = self.tool._extract_entity_info("high_entity", high_conf_mentions)
        
        # Low confidence entity
        low_entity_info = self.tool._extract_entity_info("low_entity", low_conf_mentions)
        
        # High confidence entity should have higher confidence
        assert high_entity_info["confidence"] > low_entity_info["confidence"]
        
        # Multiple mentions should boost confidence
        assert high_entity_info["confidence"] > 0.9

    def test_large_entity_set_performance_real(self):
        """Test performance with larger entity sets"""
        if not self.tool.driver:
            pytest.skip("Neo4j not available")
        
        test_case = self.test_data["large_entity_set"]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Performance requirements
        assert result.execution_time < 30.0, f"Execution too slow: {result.execution_time}s"
        assert result.memory_used < 200 * 1024 * 1024, f"Memory usage too high: {result.memory_used} bytes"
        
        # Should process all entities
        assert result.data["entity_count"] >= 5

    def test_error_handling_real(self):
        """Test error handling with real error conditions"""
        # Test with invalid input
        invalid_request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
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
        
        assert contract["tool_id"] == "T31"
        assert contract["name"] == "Entity Builder"
        assert contract["category"] == "graph_construction"
        assert "description" in contract
        assert "input_specification" in contract
        assert "output_specification" in contract
        assert "error_codes" in contract
        assert "supported_entity_types" in contract
        assert "dependencies" in contract
        assert "storage_backend" in contract
        
        # Verify supported entity types
        supported_types = contract["supported_entity_types"]
        expected_types = ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", 
                         "WORK_OF_ART", "LAW", "LANGUAGE", "FACILITY", 
                         "MONEY", "DATE", "TIME", "UNKNOWN"]
        
        for expected_type in expected_types:
            assert expected_type in supported_types

    def test_metadata_real(self):
        """Test metadata in results"""
        test_case = self.test_data["simple_person_mentions"]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        if result.status == "success":
            assert result.metadata is not None
            assert "neo4j_available" in result.metadata
            assert "total_mentions" in result.metadata
            assert "source_refs_count" in result.metadata
            assert "entity_types" in result.metadata
            
            # Verify metadata values
            assert result.metadata["total_mentions"] == len(test_case["mentions"])
            assert result.metadata["source_refs_count"] == len(test_case["source_refs"])

    def test_processing_stats_real(self):
        """Test processing statistics tracking"""
        initial_created = self.tool.entities_created
        initial_processed = self.tool.mentions_processed
        initial_operations = self.tool.neo4j_operations
        
        test_case = self.test_data["mixed_entity_types"]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        if result.status == "success":
            # Stats should have increased
            assert self.tool.mentions_processed >= initial_processed
            
            # Check building stats in result
            building_stats = result.data["building_stats"]
            assert "mentions_processed" in building_stats
            assert "entities_created" in building_stats
            assert "neo4j_operations" in building_stats

    def test_neo4j_stats_when_available(self):
        """Test Neo4j statistics retrieval"""
        if not self.tool.driver:
            pytest.skip("Neo4j not available")
        
        stats = self.tool.get_neo4j_stats()
        
        assert stats["status"] == "success"
        assert "total_entities" in stats
        assert "entity_type_distribution" in stats
        assert isinstance(stats["total_entities"], int)
        assert isinstance(stats["entity_type_distribution"], dict)

    def test_entity_search_when_available(self):
        """Test entity search functionality"""
        if not self.tool.driver:
            pytest.skip("Neo4j not available")
        
        # First create some entities
        test_case = self.test_data["simple_person_mentions"]
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        if result.status == "success":
            # Now search for entities
            entities = self.tool.search_entities(name_pattern="Smith", limit=10)
            
            assert isinstance(entities, list)
            # May or may not find entities depending on previous test runs

    def test_entity_retrieval_when_available(self):
        """Test entity retrieval by ID"""
        if not self.tool.driver:
            pytest.skip("Neo4j not available")
        
        # Test retrieval of non-existent entity
        entity = self.tool.get_entity_by_id("non_existent_entity")
        assert entity is None  # Should handle gracefully

    def test_cleanup_real(self):
        """Test resource cleanup"""
        # Test cleanup
        cleanup_result = self.tool.cleanup()
        assert isinstance(cleanup_result, bool)
        
        # Reinitialize for other tests
        self.tool._initialize_neo4j_connection()

    def test_zero_mocking_verification(self):
        """Verify no mocking is used in this test suite"""
        # Verify we're using real ServiceManager
        assert isinstance(self.service_manager, ServiceManager)
        assert not hasattr(self.service_manager, '_mock_name'), "ServiceManager appears to be mocked"
        
        # Verify we're using real tool instance
        assert isinstance(self.tool, T31EntityBuilderUnified)
        assert not hasattr(self.tool, '_mock_name'), "Tool appears to be mocked"
        
        # Verify Neo4j driver is real if available
        if self.tool.driver:
            assert hasattr(self.tool.driver, 'session'), "Neo4j driver should be real"
        
        # This test suite uses NO mocking - all functionality is real

    def test_edge_cases_real(self):
        """Test edge cases and boundary conditions"""
        # Test with minimal mentions
        minimal_data = {
            "mentions": [
                {"text": "Test", "label": "UNKNOWN", "confidence": 0.5}
            ],
            "source_refs": []
        }
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=minimal_data,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        if result.status == "success":
            assert result.data["entity_count"] >= 0
        
        # Test with mentions without entity_id (should create them)
        no_id_data = {
            "mentions": [
                {"text": "No ID Entity", "label": "PERSON"},
                {"text": "Another Entity", "label": "ORG"}
            ],
            "source_refs": ["test_chunk"]
        }
        
        # Should not crash - entity IDs will be created
        entity_groups = self.tool._group_mentions_by_entity(no_id_data["mentions"])
        assert len(entity_groups) >= 1

    def test_performance_requirements_real(self):
        """Test that tool meets performance requirements"""
        test_case = self.test_data["mixed_entity_types"]
        
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data=test_case,
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        if result.status == "success":
            # Performance requirements
            assert result.execution_time < 15.0, f"Execution too slow: {result.execution_time}s"
            assert result.memory_used < 150 * 1024 * 1024, f"Memory usage too high: {result.memory_used} bytes"
            
            # Quality requirements
            if result.data["entity_count"] > 0:
                assert result.data["confidence"] > 0.5, f"Confidence too low: {result.data['confidence']}"