"""
Test T68 PageRank Calculator Unified Tool - Mock-Free Testing

Tests the T68 PageRank Calculator with comprehensive mock-free functionality testing.
All tests use real ServiceManager, NetworkX, and Neo4j integration.
"""

import pytest
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Any, List

from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolErrorCode

class TestT68PageRankCalculatorUnifiedMockFree:
    """Mock-free testing for T68 PageRank Calculator Unified"""
    
    def setup_method(self):
        """Setup for each test method - NO mocks used"""
        # Real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = T68PageRankCalculatorUnified(service_manager=self.service_manager)
        
        # Create real test data with known graph structures
        self.test_data = self._create_real_test_data()
    
    def _create_real_test_data(self) -> Dict[str, Any]:
        """Create actual test data for PageRank calculation"""
        return {
            "simple_graph": {
                "graph_ref": "neo4j://graph/test_simple"
            },
            "filtered_graph": {
                "graph_ref": "neo4j://graph/test_filtered"
            },
            "empty_graph": {
                "graph_ref": "neo4j://graph/empty"
            },
            "large_graph": {
                "graph_ref": "neo4j://graph/large"
            }
        }
    
    def test_tool_initialization_real(self):
        """Test tool initializes correctly with real services"""
        assert self.tool.tool_id == "T68"
        assert self.tool.name == "PageRank Calculator"
        assert self.tool.category == "graph_analysis"
        assert self.tool.service_manager is not None
        
        # Test algorithm parameters
        assert self.tool.damping_factor == 0.85
        assert self.tool.max_iterations == 100
        assert self.tool.tolerance == 1e-6
        assert self.tool.min_score == 0.0001
        
        # Test performance tracking variables
        assert self.tool.entities_processed == 0
        assert self.tool.iterations_used == 0
        assert self.tool.convergence_achieved is False
        assert self.tool.neo4j_operations == 0
    
    def test_dependencies_check_real(self):
        """Test dependency checking with real library imports"""
        # Test NetworkX availability
        try:
            import networkx as nx
            networkx_available = True
        except ImportError:
            networkx_available = False
        
        # Test Neo4j availability 
        try:
            from neo4j import GraphDatabase
            neo4j_available = True
        except ImportError:
            neo4j_available = False
        
        # Tool should handle missing dependencies gracefully
        if not networkx_available:
            request = ToolRequest(
                tool_id="T68",
                operation="calculate_pagerank",
                input_data=self.test_data["simple_graph"],
                parameters={}
            )
            
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code == ToolErrorCode.PROCESSING_ERROR
            assert "NetworkX not available" in result.error_message
    
    def test_simple_pagerank_calculation_real(self):
        """Test basic PageRank calculation with real NetworkX processing"""
        request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data=self.test_data["simple_graph"],
            parameters={"result_limit": 50}
        )
        
        result = self.tool.execute(request)
        
        # Should succeed even with empty/small graphs
        assert result.status in ["success", "error"]
        assert result.execution_time > 0
        
        if result.status == "success":
            # Verify result structure
            assert "ranked_entities" in result.data
            assert "pagerank_scores" in result.data
            assert "entity_count" in result.data
            assert "confidence" in result.data
            
            # Verify PageRank scores structure
            ranked_entities = result.data["ranked_entities"]
            for entity in ranked_entities:
                assert "rank" in entity
                assert "entity_id" in entity
                assert "canonical_name" in entity
                assert "pagerank_score" in entity
                assert "confidence" in entity
                assert "percentile" in entity
                assert isinstance(entity["pagerank_score"], float)
                assert entity["pagerank_score"] >= 0.0
                assert 0.0 <= entity["confidence"] <= 1.0
            
            # Verify computation stats
            assert "computation_stats" in result.data
            stats = result.data["computation_stats"]
            assert "entities_processed" in stats
            assert "convergence_achieved" in stats
            assert "neo4j_operations" in stats
            
            # Verify graph metrics
            assert "graph_metrics" in result.data
            metrics = result.data["graph_metrics"]
            if metrics:  # Only if graph has data
                assert "node_count" in metrics
                assert "edge_count" in metrics
                assert "density" in metrics
        
        elif result.status == "error":
            # Should have proper error handling
            assert result.error_code in [
                ToolErrorCode.CONNECTION_ERROR,
                ToolErrorCode.PROCESSING_ERROR
            ]
    
    def test_graph_loading_real(self):
        """Test graph loading from Neo4j with real database queries"""
        # Test with different entity type filters
        entity_types = ["PERSON", "ORG"]
        graph_data = self.tool._load_graph_from_neo4j(entity_types, min_degree=1)
        
        # Verify graph data structure
        assert "nodes" in graph_data
        assert "edges" in graph_data
        assert "node_count" in graph_data
        assert "edge_count" in graph_data
        assert isinstance(graph_data["nodes"], dict)
        assert isinstance(graph_data["edges"], list)
        assert isinstance(graph_data["node_count"], int)
        assert isinstance(graph_data["edge_count"], int)
        
        # Verify node structure
        for node_id, node_data in graph_data["nodes"].items():
            assert "entity_id" in node_data
            assert "name" in node_data
            assert "entity_type" in node_data
            assert "confidence" in node_data
            assert isinstance(node_data["confidence"], (int, float))
        
        # Verify edge structure
        for edge in graph_data["edges"]:
            assert "source" in edge
            assert "target" in edge
            assert "weight" in edge
            assert "confidence" in edge
            assert isinstance(edge["weight"], (int, float))
            assert isinstance(edge["confidence"], (int, float))
    
    def test_networkx_graph_building_real(self):
        """Test NetworkX graph building with real graph construction"""
        # Create sample graph data
        sample_graph_data = {
            "nodes": {
                "entity_1": {
                    "entity_id": "entity_1",
                    "name": "John Smith",
                    "entity_type": "PERSON",
                    "confidence": 0.9
                },
                "entity_2": {
                    "entity_id": "entity_2", 
                    "name": "Google Inc",
                    "entity_type": "ORG",
                    "confidence": 0.8
                },
                "entity_3": {
                    "entity_id": "entity_3",
                    "name": "California",
                    "entity_type": "GPE",
                    "confidence": 0.85
                }
            },
            "edges": [
                {
                    "source": "entity_1",
                    "target": "entity_2",
                    "weight": 0.8,
                    "confidence": 0.9
                },
                {
                    "source": "entity_2",
                    "target": "entity_3",
                    "weight": 0.7,
                    "confidence": 0.8
                }
            ],
            "node_count": 3,
            "edge_count": 2
        }
        
        # Build NetworkX graph
        nx_graph = self.tool._build_networkx_graph(sample_graph_data)
        
        # Verify NetworkX graph structure
        assert nx_graph.number_of_nodes() == 3
        assert nx_graph.number_of_edges() == 2
        
        # Verify nodes have attributes
        for node_id in nx_graph.nodes():
            node_attrs = nx_graph.nodes[node_id]
            assert "entity_id" in node_attrs
            assert "name" in node_attrs
            assert "entity_type" in node_attrs
            assert "confidence" in node_attrs
        
        # Verify edges have weights
        for source, target in nx_graph.edges():
            edge_attrs = nx_graph.edges[source, target]
            assert "weight" in edge_attrs
            assert "confidence" in edge_attrs
    
    def test_pagerank_score_calculation_real(self):
        """Test PageRank score calculation with real NetworkX algorithms"""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("NetworkX not available")
        
        # Create a simple test graph
        G = nx.DiGraph()
        G.add_node("A", name="Node A")
        G.add_node("B", name="Node B") 
        G.add_node("C", name="Node C")
        G.add_edge("A", "B", weight=1.0)
        G.add_edge("B", "C", weight=1.0)
        G.add_edge("C", "A", weight=1.0)
        
        # Calculate PageRank scores
        pagerank_scores = self.tool._calculate_pagerank_scores(G)
        
        # Verify scores calculated
        assert isinstance(pagerank_scores, dict)
        assert len(pagerank_scores) == 3
        
        # Verify score properties
        total_score = sum(pagerank_scores.values())
        assert abs(total_score - 1.0) < 0.01  # PageRank scores sum to ~1.0
        
        for node_id, score in pagerank_scores.items():
            assert isinstance(score, float)
            assert score > 0.0
            assert score <= 1.0
        
        # Verify performance tracking updated
        assert self.tool.entities_processed == 3
        assert self.tool.convergence_achieved is True
    
    def test_entity_ranking_real(self):
        """Test entity ranking with real score sorting and formatting"""
        # Sample PageRank scores
        pagerank_scores = {
            "entity_1": 0.4,
            "entity_2": 0.35, 
            "entity_3": 0.25
        }
        
        # Sample graph data
        graph_data = {
            "nodes": {
                "entity_1": {"name": "John Smith", "entity_type": "PERSON", "confidence": 0.9},
                "entity_2": {"name": "Google Inc", "entity_type": "ORG", "confidence": 0.8},
                "entity_3": {"name": "California", "entity_type": "GPE", "confidence": 0.85}
            }
        }
        
        # Rank entities
        ranked_entities = self.tool._rank_entities(pagerank_scores, graph_data, limit=10)
        
        # Verify ranking
        assert len(ranked_entities) == 3
        
        # Should be sorted by PageRank score descending
        assert ranked_entities[0]["pagerank_score"] >= ranked_entities[1]["pagerank_score"]
        assert ranked_entities[1]["pagerank_score"] >= ranked_entities[2]["pagerank_score"]
        
        # Verify rank assignment
        for i, entity in enumerate(ranked_entities, 1):
            assert entity["rank"] == i
            assert "entity_id" in entity
            assert "canonical_name" in entity
            assert "entity_type" in entity
            assert "pagerank_score" in entity
            assert "confidence" in entity
            assert "percentile" in entity
            assert 0.0 <= entity["percentile"] <= 100.0
    
    def test_confidence_calculation_real(self):
        """Test confidence calculation with real scoring logic"""
        # Test various PageRank scores
        high_pagerank = 0.1
        medium_pagerank = 0.01
        low_pagerank = 0.001
        
        base_confidence = 0.8
        
        high_confidence = self.tool._calculate_pagerank_confidence(high_pagerank, base_confidence)
        medium_confidence = self.tool._calculate_pagerank_confidence(medium_pagerank, base_confidence)
        low_confidence = self.tool._calculate_pagerank_confidence(low_pagerank, base_confidence)
        
        # Higher PageRank should yield higher confidence
        assert high_confidence >= medium_confidence >= low_confidence
        
        # All confidences should be in valid range
        for conf in [high_confidence, medium_confidence, low_confidence]:
            assert 0.1 <= conf <= 1.0
    
    def test_percentile_calculation_real(self):
        """Test percentile calculation with real statistical analysis"""
        all_scores = {
            "entity_1": 0.4,
            "entity_2": 0.3,
            "entity_3": 0.2, 
            "entity_4": 0.1
        }
        
        # Test percentile for different scores
        percentile_40 = self.tool._calculate_percentile(0.4, all_scores)
        percentile_30 = self.tool._calculate_percentile(0.3, all_scores)
        percentile_20 = self.tool._calculate_percentile(0.2, all_scores)
        percentile_10 = self.tool._calculate_percentile(0.1, all_scores)
        
        # Higher scores should have higher percentiles
        assert percentile_40 >= percentile_30 >= percentile_20 >= percentile_10
        
        # All percentiles should be in valid range
        for p in [percentile_40, percentile_30, percentile_20, percentile_10]:
            assert 0.0 <= p <= 100.0
    
    def test_graph_metrics_analysis_real(self):
        """Test graph metrics analysis with real NetworkX computations"""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("NetworkX not available")
        
        # Create test graph
        G = nx.DiGraph()
        G.add_nodes_from(['A', 'B', 'C', 'D'])
        G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')])
        
        # Analyze metrics
        metrics = self.tool._analyze_graph_metrics(G)
        
        # Verify metrics structure
        assert "node_count" in metrics
        assert "edge_count" in metrics
        assert "density" in metrics
        assert "is_connected" in metrics
        assert "average_degree" in metrics
        
        # Verify metric values
        assert metrics["node_count"] == 4
        assert metrics["edge_count"] == 4
        assert isinstance(metrics["density"], float)
        assert isinstance(metrics["is_connected"], bool)
        assert metrics["average_degree"] == 2.0  # Each node has degree 2
    
    def test_score_distribution_analysis_real(self):
        """Test score distribution analysis with real statistical computations"""
        pagerank_scores = {
            "entity_1": 0.4,
            "entity_2": 0.3,
            "entity_3": 0.2,
            "entity_4": 0.1
        }
        
        distribution = self.tool._analyze_score_distribution(pagerank_scores)
        
        # Verify distribution analysis
        assert "min_score" in distribution
        assert "max_score" in distribution
        assert "mean_score" in distribution
        assert "median_score" in distribution
        assert "score_ranges" in distribution
        
        assert distribution["min_score"] == 0.1
        assert distribution["max_score"] == 0.4
        assert distribution["mean_score"] == 0.25
        assert distribution["median_score"] in [0.2, 0.3]  # Median of 4 values
        
        # Verify score ranges
        ranges = distribution["score_ranges"]
        assert "top_10_percent" in ranges
        assert "top_25_percent" in ranges
        assert "bottom_50_percent" in ranges
    
    def test_input_validation_real(self):
        """Test comprehensive input validation with real error scenarios"""
        # Test invalid input type
        invalid_input_1 = "invalid_string_input"
        validation_result_1 = self.tool._validate_input(invalid_input_1)
        assert not validation_result_1["valid"]
        assert "dictionary" in validation_result_1["error"]
        
        # Test invalid graph reference type
        invalid_input_2 = {"graph_ref": 123}
        validation_result_2 = self.tool._validate_input(invalid_input_2)
        assert not validation_result_2["valid"]
        assert "string" in validation_result_2["error"]
        
        # Test valid input
        valid_input = {"graph_ref": "neo4j://graph/test"}
        validation_result_valid = self.tool._validate_input(valid_input)
        assert validation_result_valid["valid"]
        
        # Test empty input (should use defaults)
        empty_input = {}
        validation_result_empty = self.tool._validate_input(empty_input)
        assert validation_result_empty["valid"]
    
    def test_error_handling_real(self):
        """Test error handling with real error conditions"""
        # Test with invalid input data type
        request_invalid_type = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data="invalid_string_input",
            parameters={}
        )
        
        result_invalid = self.tool.execute(request_invalid_type)
        assert result_invalid.status == "error"
        assert result_invalid.error_code == ToolErrorCode.INVALID_INPUT
        
        # Test with missing dependencies (if NetworkX not available)
        try:
            import networkx
            networkx_available = True
        except ImportError:
            networkx_available = False
        
        if not networkx_available:
            request = ToolRequest(
                tool_id="T68",
                operation="calculate_pagerank",  
                input_data=self.test_data["simple_graph"],
                parameters={}
            )
            
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code == ToolErrorCode.PROCESSING_ERROR
    
    def test_neo4j_operations_real(self):
        """Test Neo4j operations with real database interactions"""
        if not self.tool.driver:
            pytest.skip("Neo4j driver not available")
        
        # Test top entities retrieval
        top_entities = self.tool.get_top_entities(limit=5)
        assert isinstance(top_entities, list)
        assert len(top_entities) <= 5
        
        for entity in top_entities:
            assert "rank" in entity
            assert "entity_id" in entity
            assert "canonical_name" in entity
            assert "pagerank_score" in entity
            assert isinstance(entity["pagerank_score"], (int, float))
    
    def test_pagerank_stats_real(self):
        """Test PageRank statistics retrieval with real performance data"""
        stats = self.tool.get_pagerank_stats()
        
        # Verify stats structure
        assert "entities_processed" in stats
        assert "iterations_used" in stats
        assert "convergence_achieved" in stats
        assert "neo4j_operations" in stats
        assert "algorithm_params" in stats
        
        # Verify algorithm parameters
        params = stats["algorithm_params"]
        assert params["damping_factor"] == 0.85
        assert params["max_iterations"] == 100
        assert params["tolerance"] == 1e-6
        assert params["min_score"] == 0.0001
    
    def test_overall_confidence_calculation_real(self):
        """Test overall confidence calculation with real ranking data"""
        # Sample ranked entities
        ranked_entities = [
            {"rank": 1, "confidence": 0.9},
            {"rank": 2, "confidence": 0.8},
            {"rank": 3, "confidence": 0.7},
            {"rank": 4, "confidence": 0.6}
        ]
        
        overall_confidence = self.tool._calculate_overall_confidence(ranked_entities)
        
        # Should be weighted by rank (higher ranks have more impact)
        assert isinstance(overall_confidence, float)
        assert 0.0 <= overall_confidence <= 1.0
        
        # Should be higher than simple average due to rank weighting
        simple_average = sum(e["confidence"] for e in ranked_entities) / len(ranked_entities)
        assert overall_confidence >= simple_average
    
    def test_tool_contract_real(self):
        """Test tool contract specification with real schema validation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract["tool_id"] == "T68"
        assert contract["name"] == "PageRank Calculator"
        assert contract["category"] == "graph_analysis"
        assert "description" in contract
        
        # Verify input specification
        assert "input_specification" in contract
        input_spec = contract["input_specification"]
        assert input_spec["type"] == "object"
        assert "graph_ref" in input_spec["properties"]
        
        # Verify parameters
        assert "parameters" in contract
        params = contract["parameters"]
        assert "entity_types" in params
        assert "min_degree" in params
        assert "result_limit" in params
        
        # Verify output specification
        assert "output_specification" in contract
        output_spec = contract["output_specification"]
        assert "ranked_entities" in output_spec["properties"]
        assert "entity_count" in output_spec["properties"]
        
        # Verify error codes
        assert "error_codes" in contract
        assert ToolErrorCode.INVALID_INPUT in contract["error_codes"]
        assert ToolErrorCode.PROCESSING_ERROR in contract["error_codes"]
        
        # Verify algorithm info
        assert "algorithm_info" in contract
        algo_info = contract["algorithm_info"]
        assert algo_info["algorithm"] == "PageRank"
        assert algo_info["implementation"] == "NetworkX"
        assert algo_info["damping_factor"] == 0.85
        
        # Verify dependencies
        assert "dependencies" in contract
        assert "networkx" in contract["dependencies"]
        assert "neo4j" in contract["dependencies"]
    
    def test_cleanup_real(self):
        """Test resource cleanup with real connection management"""
        # Test cleanup without driver
        tool_no_driver = T68PageRankCalculatorUnified(service_manager=self.service_manager)
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
        sample_entities = [
            {
                "rank": 1,
                "entity_id": "test_entity",
                "canonical_name": "Test Entity",
                "pagerank_score": 0.5
            }
        ]
        
        # This should not raise any exceptions
        self.tool._create_service_mentions(sample_entities, {"test": "data"})
    
    def test_performance_tracking_real(self):
        """Test performance tracking with real metrics"""
        initial_processed = self.tool.entities_processed
        initial_operations = self.tool.neo4j_operations
        
        # Execute PageRank calculation
        request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data=self.test_data["simple_graph"],
            parameters={"result_limit": 10}
        )
        
        result = self.tool.execute(request)
        
        # Performance tracking should be updated (if successful)
        if result.status == "success":
            assert "computation_stats" in result.data
            stats = result.data["computation_stats"]
            assert stats["entities_processed"] >= initial_processed
            assert stats["neo4j_operations"] >= initial_operations
    
    def teardown_method(self):
        """Cleanup after each test method"""
        if hasattr(self.tool, 'cleanup'):
            self.tool.cleanup()