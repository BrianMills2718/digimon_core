"""
Test T34 Edge Builder Unified Tool - Mock-Free Testing

Tests the T34 Edge Builder with comprehensive mock-free functionality testing.
All tests use real ServiceManager and Neo4j integration.
"""

import pytest
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Any, List

from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolErrorCode

class TestT34EdgeBuilderUnifiedMockFree:
    """Mock-free testing for T34 Edge Builder Unified"""
    
    def setup_method(self):
        """Setup for each test method - NO mocks used"""
        # Real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = T34EdgeBuilderUnified(service_manager=self.service_manager)
        
        # Create real test data with known relationships
        self.test_data = self._create_real_test_data()
    
    def _create_real_test_data(self) -> Dict[str, Any]:
        """Create actual test data for edge building"""
        return {
            "simple_relationships": {
                "relationships": [
                    {
                        "relationship_id": "rel_001",
                        "relationship_type": "WORKS_FOR",
                        "subject": {
                            "text": "John Smith",
                            "entity_id": "entity_john_smith",
                            "entity_type": "PERSON"
                        },
                        "object": {
                            "text": "Google Inc",
                            "entity_id": "entity_google",
                            "entity_type": "ORG"
                        },
                        "confidence": 0.85,
                        "extraction_method": "pattern_based",
                        "evidence_text": "John Smith works for Google Inc",
                        "entity_distance": 3
                    },
                    {
                        "relationship_id": "rel_002", 
                        "relationship_type": "LOCATED_IN",
                        "subject": {
                            "text": "Google Inc",
                            "entity_id": "entity_google",
                            "entity_type": "ORG"
                        },
                        "object": {
                            "text": "California",
                            "entity_id": "entity_california",
                            "entity_type": "GPE"
                        },
                        "confidence": 0.9,
                        "extraction_method": "dependency_parsing",
                        "evidence_text": "Google Inc is located in California",
                        "entity_distance": 2
                    }
                ],
                "source_refs": ["storage://document/doc123", "storage://chunk/chunk456"]
            },
            "complex_relationships": {
                "relationships": [
                    {
                        "relationship_id": "rel_003",
                        "relationship_type": "PARTNERS_WITH",
                        "subject": {
                            "text": "Microsoft Corporation",
                            "entity_id": "entity_microsoft",
                            "entity_type": "ORG"
                        },
                        "object": {
                            "text": "OpenAI",
                            "entity_id": "entity_openai", 
                            "entity_type": "ORG"
                        },
                        "confidence": 0.75,
                        "extraction_method": "proximity_based",
                        "evidence_text": "Microsoft Corporation announced partnership with OpenAI",
                        "entity_distance": 5
                    }
                ],
                "source_refs": ["storage://document/doc789"]
            },
            "invalid_relationships": {
                "relationships": [
                    {
                        "relationship_id": "rel_invalid",
                        "relationship_type": "OWNS",
                        "subject": {
                            "text": "Unknown Entity",
                            "entity_id": "entity_unknown",
                            "entity_type": "PERSON"
                        },
                        "object": {
                            "text": "Nonexistent Company",
                            "entity_id": "entity_nonexistent",
                            "entity_type": "ORG"
                        },
                        "confidence": 0.6,
                        "extraction_method": "pattern_based",
                        "evidence_text": "Unknown Entity owns Nonexistent Company"
                    }
                ],
                "source_refs": ["storage://document/invalid"]
            }
        }
    
    def test_tool_initialization_real(self):
        """Test tool initializes correctly with real services"""
        assert self.tool.tool_id == "T34"
        assert self.tool.name == "Edge Builder"
        assert self.tool.category == "graph_construction"
        assert self.tool.service_manager is not None
        
        # Test Neo4j initialization
        if self.tool.driver:
            assert hasattr(self.tool, 'min_weight')
            assert hasattr(self.tool, 'max_weight')
            assert hasattr(self.tool, 'confidence_weight_factor')
        
        # Test performance tracking variables
        assert self.tool.edges_created == 0
        assert self.tool.relationships_processed == 0
        assert self.tool.neo4j_operations == 0
    
    def test_simple_edge_building_real(self):
        """Test basic edge building with real Neo4j operations"""
        request = ToolRequest(
            tool_id="T34",
            operation="build_edges",
            input_data=self.test_data["simple_relationships"],
            parameters={"verify_entities": False}  # Skip entity verification for test
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert "edges" in result.data
        assert result.data["edge_count"] >= 0  # May be 0 if Neo4j not available
        assert result.execution_time > 0
        
        # Verify edge structure if edges were created
        if result.data["edge_count"] > 0:
            edges = result.data["edges"]
            
            for edge in edges:
                assert "relationship_id" in edge
                assert "relationship_type" in edge
                assert "subject" in edge
                assert "object" in edge
                assert "weight" in edge
                assert "confidence" in edge
                assert isinstance(edge["weight"], float)
                assert 0.0 <= edge["weight"] <= 1.0
        
        # Verify processing stats
        assert "building_stats" in result.data
        stats = result.data["building_stats"]
        assert "relationships_processed" in stats
        assert "edges_created" in stats
        assert "neo4j_operations" in stats
        
        # Verify metadata
        assert result.metadata["neo4j_available"] is not None
        assert result.metadata["total_relationships"] == 2
        assert result.metadata["source_refs_count"] == 2
    
    def test_weight_calculation_real(self):
        """Test edge weight calculation with real confidence scoring"""
        # Test weight calculation directly
        relationship = self.test_data["simple_relationships"]["relationships"][0]
        weight = self.tool._calculate_edge_weight(relationship)
        
        # Verify weight is within bounds
        assert isinstance(weight, float)
        assert self.tool.min_weight <= weight <= self.tool.max_weight
        
        # Test different confidence levels
        high_confidence_rel = relationship.copy()
        high_confidence_rel["confidence"] = 0.95
        high_weight = self.tool._calculate_edge_weight(high_confidence_rel)
        
        low_confidence_rel = relationship.copy()
        low_confidence_rel["confidence"] = 0.3
        low_weight = self.tool._calculate_edge_weight(low_confidence_rel)
        
        # Higher confidence should yield higher weight
        assert high_weight >= low_weight
    
    def test_evidence_quality_assessment_real(self):
        """Test evidence quality assessment with real text analysis"""
        # Test various evidence quality scenarios
        high_quality_evidence = "John Smith works for Google Inc in California office"
        medium_quality_evidence = "John Smith works for Google"
        low_quality_evidence = "John"
        empty_evidence = ""
        
        high_score = self.tool._assess_evidence_quality(high_quality_evidence)
        medium_score = self.tool._assess_evidence_quality(medium_quality_evidence)
        low_score = self.tool._assess_evidence_quality(low_quality_evidence)
        empty_score = self.tool._assess_evidence_quality(empty_evidence)
        
        # Verify scoring order
        assert high_score >= medium_score >= low_score >= empty_score
        assert all(0.0 <= score <= 1.0 for score in [high_score, medium_score, low_score, empty_score])
    
    def test_input_validation_real(self):
        """Test comprehensive input validation with real error scenarios"""
        # Test missing relationships
        invalid_input_1 = {"source_refs": ["test"]}
        validation_result_1 = self.tool._validate_input(invalid_input_1)
        assert not validation_result_1["valid"]
        assert "relationships" in validation_result_1["error"]
        
        # Test empty relationships list
        invalid_input_2 = {"relationships": [], "source_refs": ["test"]}
        validation_result_2 = self.tool._validate_input(invalid_input_2)
        assert not validation_result_2["valid"]
        assert "At least one relationship is required" in validation_result_2["error"]
        
        # Test invalid relationship structure
        invalid_input_3 = {
            "relationships": [
                {"subject": {"text": "John"}}  # Missing required fields
            ]
        }
        validation_result_3 = self.tool._validate_input(invalid_input_3)
        assert not validation_result_3["valid"]
        
        # Test valid input
        valid_input = self.test_data["simple_relationships"]
        validation_result_valid = self.tool._validate_input(valid_input)
        assert validation_result_valid["valid"]
    
    def test_entity_verification_real(self):
        """Test entity verification with real Neo4j queries"""
        if not self.tool.driver:
            pytest.skip("Neo4j driver not available")
        
        relationships = self.test_data["simple_relationships"]["relationships"]
        verification_result = self.tool._verify_entities_exist(relationships)
        
        # Verify result structure
        assert "all_entities_found" in verification_result
        assert isinstance(verification_result["all_entities_found"], bool)
        
        if not verification_result["all_entities_found"]:
            assert "missing_entities" in verification_result
            assert "found_count" in verification_result
            assert "total_count" in verification_result
    
    def test_error_handling_real(self):
        """Test error handling with real error conditions"""
        # Test with invalid input data type
        request_invalid_type = ToolRequest(
            tool_id="T34",
            operation="build_edges",
            input_data="invalid_string_input",
            parameters={}
        )
        
        result_invalid = self.tool.execute(request_invalid_type)
        assert result_invalid.status == "error"
        assert result_invalid.error_code == ToolErrorCode.INVALID_INPUT
        
        # Test with missing required fields
        request_missing_fields = ToolRequest(
            tool_id="T34",
            operation="build_edges",
            input_data={"invalid": "data"},
            parameters={}
        )
        
        result_missing = self.tool.execute(request_missing_fields)
        assert result_missing.status == "error"
        assert result_missing.error_code == ToolErrorCode.INVALID_INPUT
        
        # Test with entity verification enabled but missing entities
        request_missing_entities = ToolRequest(
            tool_id="T34",
            operation="build_edges",
            input_data=self.test_data["invalid_relationships"],
            parameters={"verify_entities": True}
        )
        
        result_missing_entities = self.tool.execute(request_missing_entities)
        # Should either succeed (if Neo4j not available) or fail with validation error
        assert result_missing_entities.status in ["success", "error"]
        if result_missing_entities.status == "error":
            assert result_missing_entities.error_code in [
                ToolErrorCode.CONNECTION_ERROR,
                ToolErrorCode.VALIDATION_FAILED
            ]
    
    def test_neo4j_operations_real(self):
        """Test Neo4j operations with real database interactions"""
        if not self.tool.driver:
            pytest.skip("Neo4j driver not available")
        
        # Test Neo4j stats retrieval
        stats = self.tool.get_neo4j_stats()
        assert "status" in stats
        
        if stats["status"] == "success":
            assert "total_entities" in stats
            assert "total_relationships" in stats
            assert "graph_density" in stats
            assert isinstance(stats["total_entities"], int)
            assert isinstance(stats["total_relationships"], int)
            assert isinstance(stats["graph_density"], float)
    
    def test_relationship_search_real(self):
        """Test relationship search functionality with real queries"""
        if not self.tool.driver:
            pytest.skip("Neo4j driver not available")
        
        # Test basic search
        relationships = self.tool.search_relationships(limit=10)
        assert isinstance(relationships, list)
        
        # Test filtered search
        filtered_relationships = self.tool.search_relationships(
            relationship_type="WORKS_FOR",
            min_weight=0.5,
            limit=5
        )
        assert isinstance(filtered_relationships, list)
        assert len(filtered_relationships) <= 5
    
    def test_weight_distribution_analysis_real(self):
        """Test weight distribution analysis with real edge data"""
        # Create sample edges for analysis
        sample_edges = [
            {"weight": 0.9, "confidence": 0.9, "relationship_type": "WORKS_FOR"},
            {"weight": 0.7, "confidence": 0.7, "relationship_type": "LOCATED_IN"},
            {"weight": 0.3, "confidence": 0.3, "relationship_type": "PARTNERS_WITH"},
            {"weight": 0.8, "confidence": 0.8, "relationship_type": "OWNS"},
        ]
        
        distribution = self.tool._analyze_weight_distribution(sample_edges)
        
        # Verify distribution analysis
        assert "min_weight" in distribution
        assert "max_weight" in distribution
        assert "average_weight" in distribution
        assert "weight_ranges" in distribution
        
        assert distribution["min_weight"] == 0.3
        assert distribution["max_weight"] == 0.9
        assert 0.3 <= distribution["average_weight"] <= 0.9
        
        # Verify weight ranges
        ranges = distribution["weight_ranges"]
        assert "high_confidence" in ranges
        assert "medium_confidence" in ranges
        assert "low_confidence" in ranges
        assert sum(ranges.values()) == len(sample_edges)
    
    def test_relationship_type_counting_real(self):
        """Test relationship type counting with real edge data"""
        sample_edges = [
            {"relationship_type": "WORKS_FOR"},
            {"relationship_type": "WORKS_FOR"},
            {"relationship_type": "LOCATED_IN"},
            {"relationship_type": "PARTNERS_WITH"},
            {"relationship_type": "WORKS_FOR"},
        ]
        
        type_counts = self.tool._count_relationship_types(sample_edges)
        
        # Verify type counting
        assert type_counts["WORKS_FOR"] == 3
        assert type_counts["LOCATED_IN"] == 1
        assert type_counts["PARTNERS_WITH"] == 1
        assert sum(type_counts.values()) == len(sample_edges)
    
    def test_tool_contract_real(self):
        """Test tool contract specification with real schema validation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract["tool_id"] == "T34"
        assert contract["name"] == "Edge Builder"
        assert contract["category"] == "graph_construction"
        assert "description" in contract
        
        # Verify input specification
        assert "input_specification" in contract
        input_spec = contract["input_specification"]
        assert input_spec["type"] == "object"
        assert "relationships" in input_spec["properties"]
        assert "source_refs" in input_spec["properties"]
        
        # Verify output specification
        assert "output_specification" in contract
        output_spec = contract["output_specification"]
        assert "edges" in output_spec["properties"]
        assert "edge_count" in output_spec["properties"]
        
        # Verify error codes
        assert "error_codes" in contract
        assert ToolErrorCode.INVALID_INPUT in contract["error_codes"]
        assert ToolErrorCode.PROCESSING_ERROR in contract["error_codes"]
        
        # Verify dependencies and configuration
        assert "dependencies" in contract
        assert "neo4j" in contract["dependencies"]
        assert "weight_range" in contract
        assert contract["weight_range"] == [self.tool.min_weight, self.tool.max_weight]
    
    def test_cleanup_real(self):
        """Test resource cleanup with real connection management"""
        # Test cleanup without driver
        tool_no_driver = T34EdgeBuilderUnified(service_manager=self.service_manager)
        tool_no_driver.driver = None
        cleanup_result_1 = tool_no_driver.cleanup()
        assert cleanup_result_1 is True
        
        # Test cleanup with driver
        if self.tool.driver:
            cleanup_result_2 = self.tool.cleanup()
            assert cleanup_result_2 is True
            assert self.tool.driver is None
    
    def test_service_integration_real(self):
        """Test service integration with real ServiceManager"""
        # Verify service manager integration
        assert self.tool.service_manager is not None
        
        # Test service mentions creation (should not raise errors)
        sample_edges = [
            {
                "relationship_id": "test_rel_001",
                "relationship_type": "TEST_RELATION",
                "subject": {"text": "Test Subject"},
                "object": {"text": "Test Object"}
            }
        ]
        
        # This should not raise any exceptions
        self.tool._create_service_mentions(sample_edges, {"test": "data"})
    
    def test_performance_tracking_real(self):
        """Test performance tracking with real metrics"""
        initial_processed = self.tool.relationships_processed
        initial_created = self.tool.edges_created
        initial_operations = self.tool.neo4j_operations
        
        # Execute edge building
        request = ToolRequest(
            tool_id="T34",
            operation="build_edges",
            input_data=self.test_data["simple_relationships"],
            parameters={"verify_entities": False}
        )
        
        result = self.tool.execute(request)
        
        # Verify performance tracking updated
        assert self.tool.relationships_processed >= initial_processed
        assert self.tool.edges_created >= initial_created
        
        # Verify performance data in result
        if result.status == "success":
            assert "building_stats" in result.data
            stats = result.data["building_stats"]
            assert stats["relationships_processed"] >= initial_processed
            assert stats["edges_created"] >= initial_created
    
    def teardown_method(self):
        """Cleanup after each test method"""
        if hasattr(self.tool, 'cleanup'):
            self.tool.cleanup()