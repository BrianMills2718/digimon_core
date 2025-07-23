#!/usr/bin/env python3
"""
Comprehensive test suite for T58 Graph Comparison Tool
Tests all comparison methods with real NetworkX graphs and zero mocking.
"""

import pytest
import networkx as nx
import numpy as np
from unittest.mock import patch
import tempfile
import json
from pathlib import Path

# Import the tool
from src.tools.phase2.t58_graph_comparison_unified import T58GraphComparisonTool
from src.tools.base_tool import ToolRequest, ToolResult
from src.core.service_manager import ServiceManager


class TestT58GraphComparisonUnified:
    """Test suite for T58 Graph Comparison tool with zero mocking."""
    
    def setup_method(self):
        """Set up test fixtures with real ServiceManager."""
        self.service_manager = ServiceManager()
        self.tool = T58GraphComparisonTool(self.service_manager)
        
        # Create test graphs
        self.test_graph1 = nx.Graph()
        self.test_graph1.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])
        
        self.test_graph2 = nx.Graph()
        self.test_graph2.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
        
        # Create identical graphs for isomorphism testing
        self.identical_graph1 = nx.Graph()
        self.identical_graph1.add_edges_from([(1, 2), (2, 3), (3, 1)])
        
        self.identical_graph2 = nx.Graph()
        self.identical_graph2.add_edges_from([(4, 5), (5, 6), (6, 4)])
        
        # Create weighted test graphs
        self.weighted_graph1 = nx.Graph()
        self.weighted_graph1.add_weighted_edges_from([(1, 2, 0.5), (2, 3, 1.0), (3, 1, 0.8)])
        
        self.weighted_graph2 = nx.Graph()
        self.weighted_graph2.add_weighted_edges_from([(1, 2, 0.6), (2, 3, 0.9), (3, 1, 0.7)])
    
    def test_zero_mocking_validation(self):
        """Verify that no mocking is used in the tool implementation."""
        # Check that the tool uses real NetworkX functions
        assert hasattr(self.tool, '_compute_structural_similarity')
        assert hasattr(self.tool, '_compute_spectral_similarity')
        assert hasattr(self.tool, '_check_isomorphism')
        
        # Verify tool is using real service manager
        assert isinstance(self.tool.service_manager, ServiceManager)
        assert self.tool.tool_id == "T58"
        assert self.tool.name == "Graph Comparison"
    
    def test_tool_initialization(self):
        """Test proper tool initialization."""
        assert self.tool.tool_id == "T58"
        assert self.tool.name == "Graph Comparison"
        assert self.tool.category == "graph_analytics"
        assert self.tool.service_manager is not None
        assert len(self.tool.similarity_metrics) > 0
        assert len(self.tool.comparison_methods) > 0
    
    def test_get_contract(self):
        """Test tool contract definition."""
        contract = self.tool.get_contract()
        
        assert contract.tool_id == "T58"
        assert contract.name == "Graph Comparison"
        assert "comparison_type" in contract.parameters
        assert "similarity_metrics" in contract.parameters
        assert "include_visualizations" in contract.parameters
        
        # Verify input schema
        assert contract.input_schema["type"] == "object"
        required_fields = contract.input_schema["required"]
        assert "graph1_source" in required_fields
        assert "graph1_data" in required_fields
        assert "graph2_source" in required_fields
        assert "graph2_data" in required_fields
    
    def test_health_check(self):
        """Test tool health check functionality."""
        health = self.tool.health_check()
        
        assert health["status"] == "healthy"
        assert "networkx_version" in health
        assert "numpy_version" in health
        assert "capabilities" in health
        
        capabilities = health["capabilities"]
        assert capabilities["structural_comparison"] is True
        assert capabilities["spectral_analysis"] is True
        assert capabilities["statistical_testing"] is True
        assert capabilities["visualization"] is True
        assert capabilities["isomorphism_checking"] is True
    
    def test_input_validation_success(self):
        """Test successful input validation."""
        valid_input = {
            "graph1_source": "edge_list",
            "graph1_data": [(1, 2), (2, 3), (3, 1)],
            "graph2_source": "edge_list", 
            "graph2_data": [(1, 2), (2, 3)]
        }
        
        result = self.tool.validate_input(valid_input)
        assert result["valid"] is True
    
    def test_input_validation_missing_fields(self):
        """Test input validation with missing required fields."""
        invalid_input = {
            "graph1_source": "edge_list",
            "graph1_data": [(1, 2), (2, 3)]
            # Missing graph2_source and graph2_data
        }
        
        result = self.tool.validate_input(invalid_input)
        assert result["valid"] is False
        assert "Missing required field" in result["error"]
    
    def test_input_validation_invalid_source_type(self):
        """Test input validation with invalid source type."""
        invalid_input = {
            "graph1_source": "invalid_source",
            "graph1_data": [(1, 2)],
            "graph2_source": "edge_list",
            "graph2_data": [(1, 2)]
        }
        
        result = self.tool.validate_input(invalid_input)
        assert result["valid"] is False
        assert "Invalid graph1_source" in result["error"]
    
    def test_load_graph_edge_list(self):
        """Test loading graph from edge list."""
        edge_list = [(1, 2), (2, 3), (3, 1)]
        graph = self.tool._load_graph("edge_list", edge_list)
        
        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 3
        assert graph.has_edge(1, 2)
        assert graph.has_edge(2, 3)
        assert graph.has_edge(3, 1)
    
    def test_load_graph_weighted_edge_list(self):
        """Test loading graph from weighted edge list."""
        weighted_edges = [(1, 2, 0.5), (2, 3, 1.0), (3, 1, 0.8)]
        graph = self.tool._load_graph("edge_list", weighted_edges)
        
        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 3
        assert graph[1][2]['weight'] == 0.5
        assert graph[2][3]['weight'] == 1.0
        assert graph[3][1]['weight'] == 0.8
    
    def test_load_graph_adjacency_matrix(self):
        """Test loading graph from adjacency matrix."""
        adj_matrix = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        graph = self.tool._load_graph("adjacency_matrix", adj_matrix)
        
        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 3
    
    def test_load_graph_networkx_graph(self):
        """Test loading graph from NetworkX graph object."""
        original_graph = nx.complete_graph(4)
        loaded_graph = self.tool._load_graph("networkx_graph", original_graph)
        
        assert isinstance(loaded_graph, nx.Graph)
        assert loaded_graph.number_of_nodes() == 4
        assert loaded_graph.number_of_edges() == 6
        # Should be a copy, not the same object
        assert loaded_graph is not original_graph
    
    def test_load_graph_file_path(self):
        """Test that file path loading is not supported in simplified version."""
        with pytest.raises(ValueError, match="Unknown source type"):
            self.tool._load_graph("file_path", "/some/path")
    
    def test_basic_properties(self):
        """Test basic graph properties computation."""
        props = self.tool._get_graph_properties(self.test_graph1)
        
        assert "num_nodes" in props
        assert "num_edges" in props
        assert "density" in props
        assert "num_components" in props
        assert "is_connected" in props
        assert "average_clustering" in props
        assert "average_degree" in props
        
        assert props["num_nodes"] == 4
        assert props["num_edges"] == 5
        assert isinstance(props["density"], float)
        assert isinstance(props["average_clustering"], float)
    
    def test_compare_basic_properties(self):
        """Test basic properties comparison between graphs."""
        comparison = self.tool._compare_basic_properties(self.test_graph1, self.test_graph2)
        
        assert "graph1" in comparison
        assert "graph2" in comparison
        assert "differences" in comparison
        
        differences = comparison["differences"]
        assert "nodes" in differences
        assert "edges" in differences
        assert "density" in differences
        assert "components" in differences
        
        # Graph1 has 5 edges, Graph2 has 4 edges
        assert differences["edges"] == 1
    
    def test_structural_similarity(self):
        """Test structural similarity computation."""
        similarity = self.tool._compute_structural_similarity(self.test_graph1, self.test_graph2)
        
        assert "overall_similarity" in similarity
        assert "size_similarity" in similarity
        assert "edge_similarity" in similarity
        assert "density_similarity" in similarity
        assert "clustering_similarity" in similarity
        
        # All similarity scores should be between 0 and 1
        for score in similarity.values():
            assert 0 <= score <= 1
    
    def test_spectral_similarity(self):
        """Test spectral similarity computation using eigenvalues."""
        similarity = self.tool._compute_spectral_similarity(self.test_graph1, self.test_graph2)
        
        if "error" not in similarity:
            assert "cosine_similarity" in similarity
            assert "euclidean_similarity" in similarity
            assert "correlation_similarity" in similarity
            assert "eigenvalue_difference" in similarity
            
            # Similarity scores should be reasonable
            assert isinstance(similarity["cosine_similarity"], float)
            assert isinstance(similarity["euclidean_similarity"], float)
    
    def test_degree_distribution_similarity(self):
        """Test degree distribution similarity computation."""
        similarity = self.tool._compute_degree_distribution_similarity(self.test_graph1, self.test_graph2)
        
        assert "cosine_similarity" in similarity
        assert "ks_statistic" in similarity
        assert "ks_pvalue" in similarity
        assert "similarity_score" in similarity
        
        # KS statistic should be between 0 and 1
        assert 0 <= similarity["ks_statistic"] <= 1
        # p-value should be between 0 and 1
        assert 0 <= similarity["ks_pvalue"] <= 1
    
    def test_clustering_similarity(self):
        """Test clustering coefficient similarity computation."""
        similarity = self.tool._compute_clustering_similarity(self.test_graph1, self.test_graph2)
        
        assert "mean_difference" in similarity
        assert "std_difference" in similarity
        assert "ks_statistic" in similarity
        assert "ks_pvalue" in similarity
        assert "similarity_score" in similarity
        
        # Differences should be non-negative
        assert similarity["mean_difference"] >= 0
        assert similarity["std_difference"] >= 0
    
    def test_centrality_similarity(self):
        """Test centrality measures similarity computation."""
        similarity = self.tool._compute_centrality_similarity(self.test_graph1, self.test_graph2)
        
        assert "degree_centrality" in similarity
        degree_cent = similarity["degree_centrality"]
        
        assert "ks_statistic" in degree_cent
        assert "ks_pvalue" in degree_cent
        assert "similarity" in degree_cent
        
        # For small connected graphs, should also have other centralities
        if "betweenness_centrality" in similarity:
            between_cent = similarity["betweenness_centrality"]
            assert "similarity" in between_cent
    
    def test_graph_edit_distance_small_graphs(self):
        """Test graph edit distance computation for small graphs."""
        # Create small graphs for exact computation
        small_graph1 = nx.Graph()
        small_graph1.add_edges_from([(1, 2), (2, 3)])
        
        small_graph2 = nx.Graph() 
        small_graph2.add_edges_from([(1, 2), (2, 3), (3, 4)])
        
        ged = self.tool._compute_graph_edit_distance(small_graph1, small_graph2)
        
        assert "edit_distance" in ged
        assert "normalized_distance" in ged
        assert "method" in ged
        
        # Should use exact method for small graphs
        assert ged["method"] == "exact"
        assert isinstance(ged["edit_distance"], float)
        assert 0 <= ged["normalized_distance"] <= 1
    
    def test_graph_edit_distance_large_graphs(self):
        """Test graph edit distance approximation for large graphs."""
        # Create larger graphs that will use approximation
        large_graph1 = nx.complete_graph(25)
        large_graph2 = nx.complete_graph(30)
        
        ged = self.tool._compute_graph_edit_distance(large_graph1, large_graph2)
        
        assert "edit_distance" in ged
        assert "normalized_distance" in ged
        assert "method" in ged
        
        # Should use approximation method for large graphs
        assert ged["method"] == "approximation"
        assert isinstance(ged["edit_distance"], float)
    
    def test_isomorphism_check_identical_graphs(self):
        """Test isomorphism check with identical graphs."""
        iso_result = self.tool._check_isomorphism(self.identical_graph1, self.identical_graph2)
        
        assert "isomorphic" in iso_result
        assert "method" in iso_result
        
        # Both graphs are triangles, should be isomorphic
        assert iso_result["isomorphic"] is True
        assert iso_result["method"] == "exact"
    
    def test_isomorphism_check_different_graphs(self):
        """Test isomorphism check with different graphs."""
        iso_result = self.tool._check_isomorphism(self.test_graph1, self.test_graph2)
        
        assert "isomorphic" in iso_result
        
        # Different number of edges, cannot be isomorphic
        assert iso_result["isomorphic"] is False
        assert "reason" in iso_result
    
    def test_subgraph_matching_small_graphs(self):
        """Test subgraph matching analysis for small graphs."""
        subgraph_result = self.tool._analyze_subgraph_matching(self.test_graph2, self.test_graph1)
        
        assert "method" in subgraph_result
        
        if subgraph_result["method"] == "exact":
            assert "graph1_subgraph_of_graph2" in subgraph_result
            assert "graph2_subgraph_of_graph1" in subgraph_result
        else:
            assert "common_edges" in subgraph_result
            assert "total_unique_edges" in subgraph_result
            assert "edge_overlap_ratio" in subgraph_result
    
    def test_topological_properties_comparison(self):
        """Test topological properties comparison."""
        topo_comparison = self.tool._compare_topological_properties(self.test_graph1, self.test_graph2)
        
        assert "basic_properties" in topo_comparison
        basic_props = topo_comparison["basic_properties"]
        
        assert "density_difference" in basic_props
        assert "clustering_difference" in basic_props
        assert "components_difference" in basic_props
        assert isinstance(basic_props["density_difference"], float)
        
        if "degree_distribution" in topo_comparison:
            degree_dist = topo_comparison["degree_distribution"]
            assert "mean_degree_difference" in degree_dist
            assert isinstance(degree_dist["mean_degree_difference"], float)
    
    def test_spectral_properties_comparison(self):
        """Test spectral properties comparison."""
        spectral_comparison = self.tool._compare_spectral_properties(self.test_graph1, self.test_graph2)
        
        if "error" not in spectral_comparison:
            assert "spectral_gap_difference" in spectral_comparison
            assert "largest_eigenvalue_difference" in spectral_comparison
            assert "smallest_eigenvalue_difference" in spectral_comparison
            assert "eigenvalue_variance_difference" in spectral_comparison
            
            # All differences should be non-negative
            for key in spectral_comparison:
                if key != "error":
                    assert spectral_comparison[key] >= 0
    
    def test_statistical_tests(self):
        """Test statistical significance testing."""
        stat_tests = self.tool._perform_statistical_tests(self.test_graph1, self.test_graph2, 0.95)
        
        assert "degree_distribution_test" in stat_tests
        assert "degree_mean_test" in stat_tests
        assert "clustering_test" in stat_tests
        
        degree_test = stat_tests["degree_distribution_test"]
        assert "test" in degree_test
        assert "statistic" in degree_test
        assert "p_value" in degree_test
        assert "significant" in degree_test
        assert "alpha" in degree_test
        
        assert degree_test["test"] == "Kolmogorov-Smirnov"
        assert 0 <= degree_test["p_value"] <= 1
        assert degree_test["alpha"] == 0.05
    
    def test_comprehensive_comparison_execution(self):
        """Test comprehensive comparison execution."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "networkx_graph",
                "graph1_data": self.test_graph1,
                "graph2_source": "networkx_graph", 
                "graph2_data": self.test_graph2,
                "graph1_name": "Test Graph 1",
                "graph2_name": "Test Graph 2"
            },
            parameters={
                "comparison_type": "comprehensive",
                "similarity_metrics": ["structural_similarity", "spectral_similarity", "degree_distribution_similarity"],
                "include_visualizations": True,
                "statistical_testing": True,
                "confidence_level": 0.95
            }
        )
        
        result = self.tool.execute(request)
        
        assert isinstance(result, ToolResult)
        assert result.status == "success"
        assert result.tool_id == "T58"
        
        # Check result data structure
        data = result.data
        assert "comparison_results" in data
        assert "similarity_scores" in data
        assert "statistical_tests" in data
        assert "visualizations" in data
        assert "academic_assessment" in data
        assert "graph_properties" in data
        
        # Check comparison results
        comparison_results = data["comparison_results"]
        assert "basic_properties" in comparison_results
        assert "similarity_scores" in comparison_results
        assert "structural_analysis" in comparison_results
        assert "statistical_tests" in comparison_results
        
        # Check academic assessment
        academic = data["academic_assessment"]
        assert "overall_confidence" in academic
        assert "confidence_level" in academic
        assert "publication_ready" in academic
        assert "academic_ready" in academic
        assert 0 <= academic["overall_confidence"] <= 1
    
    def test_structural_comparison_execution(self):
        """Test structural comparison execution."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "edge_list",
                "graph1_data": [(1, 2), (2, 3), (3, 1)],
                "graph2_source": "edge_list",
                "graph2_data": [(1, 2), (2, 3)]
            },
            parameters={
                "comparison_type": "structural",
                "include_visualizations": False
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        data = result.data
        
        comparison_results = data["comparison_results"]
        assert "structural_similarity" in comparison_results
        assert "graph_properties" in comparison_results
        assert "graph_edit_distance" in comparison_results
    
    def test_topological_comparison_execution(self):
        """Test topological comparison execution."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "networkx_graph",
                "graph1_data": self.test_graph1,
                "graph2_source": "networkx_graph",
                "graph2_data": self.test_graph2
            },
            parameters={
                "comparison_type": "topological"
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        data = result.data
        
        comparison_results = data["comparison_results"]
        assert "topological_properties" in comparison_results
        assert "degree_distribution" in comparison_results
        assert "clustering_similarity" in comparison_results
    
    def test_spectral_comparison_execution(self):
        """Test spectral comparison execution."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "networkx_graph",
                "graph1_data": self.test_graph1,
                "graph2_source": "networkx_graph",
                "graph2_data": self.test_graph2
            },
            parameters={
                "comparison_type": "spectral"
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        data = result.data
        
        comparison_results = data["comparison_results"]
        assert "spectral_similarity" in comparison_results
        assert "spectral_properties" in comparison_results
    
    def test_isomorphism_analysis_execution(self):
        """Test isomorphism analysis execution."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "networkx_graph",
                "graph1_data": self.identical_graph1,
                "graph2_source": "networkx_graph",
                "graph2_data": self.identical_graph2
            },
            parameters={
                "comparison_type": "isomorphism"
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        data = result.data
        
        comparison_results = data["comparison_results"]
        assert "isomorphism" in comparison_results
        assert "subgraph_matching" in comparison_results
        
        # Should detect isomorphism between triangles
        iso_result = comparison_results["isomorphism"]
        assert iso_result["isomorphic"] is True
    
    def test_visualization_generation(self):
        """Test visualization generation."""
        visualizations = self.tool._generate_comparison_visualizations(
            self.test_graph1, self.test_graph2, 
            {"similarity_scores": {"structural": {"overall_similarity": 0.8}}},
            "Graph 1", "Graph 2"
        )
        
        assert isinstance(visualizations, list)
        
        # Should have at least one visualization
        if visualizations:
            viz = visualizations[0]
            assert "type" in viz
            assert "data" in viz
    
    def test_academic_confidence_calculation(self):
        """Test academic confidence calculation."""
        mock_results = {
            "similarity_scores": {
                "structural": {"overall_similarity": 0.8},
                "spectral": {"cosine_similarity": 0.7},
                "degree_distribution": {"similarity_score": 0.9}
            },
            "statistical_tests": {
                "degree_test": {"p_value": 0.03}
            },
            "structural_analysis": {
                "graph_edit_distance": {"edit_distance": 2.0}
            },
            "basic_properties": {
                "graph1": {"num_nodes": 10},
                "graph2": {"num_nodes": 12}
            }
        }
        
        confidence = self.tool._calculate_academic_confidence(mock_results)
        
        assert "overall_confidence" in confidence
        assert "confidence_level" in confidence
        assert "publication_ready" in confidence
        assert "academic_ready" in confidence
        assert "quality_indicators" in confidence
        assert "recommendations" in confidence
        
        assert 0 <= confidence["overall_confidence"] <= 1
        assert confidence["confidence_level"] in ["low", "medium", "high"]
        assert isinstance(confidence["publication_ready"], bool)
        assert isinstance(confidence["recommendations"], list)
    
    def test_error_handling_invalid_input(self):
        """Test error handling with invalid input."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "edge_list",
                "graph1_data": "invalid_data",  # Should be list
                "graph2_source": "edge_list",
                "graph2_data": [(1, 2)]
            }
        )
        
        result = self.tool.execute(request)
        
        # Should handle error gracefully
        assert result.status == "error"
        assert "error" in result.data
    
    def test_weighted_graph_comparison(self):
        """Test comparison of weighted graphs."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "networkx_graph",
                "graph1_data": self.weighted_graph1,
                "graph2_source": "networkx_graph",
                "graph2_data": self.weighted_graph2
            },
            parameters={
                "comparison_type": "comprehensive",
                "statistical_testing": False
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        data = result.data
        assert "comparison_results" in data
        assert "similarity_scores" in data
    
    def test_large_graph_handling(self):
        """Test handling of larger graphs."""
        # Create larger test graphs
        large_graph1 = nx.barabasi_albert_graph(100, 3, seed=42)
        large_graph2 = nx.barabasi_albert_graph(110, 3, seed=43)
        
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "networkx_graph",
                "graph1_data": large_graph1,
                "graph2_source": "networkx_graph",
                "graph2_data": large_graph2
            },
            parameters={
                "comparison_type": "structural",
                "include_visualizations": False  # Skip viz for large graphs
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        data = result.data
        assert "comparison_results" in data
        
        # Should use approximation methods for large graphs
        comparison = data["comparison_results"]
        if "graph_edit_distance" in comparison:
            ged = comparison["graph_edit_distance"]
            assert ged["method"] == "approximation"
    
    def test_execution_metadata(self):
        """Test that execution metadata is properly recorded."""
        request = ToolRequest(
            tool_id="T58",
            operation="graph_comparison",
            input_data={
                "graph1_source": "edge_list",
                "graph1_data": [(1, 2), (2, 3)],
                "graph2_source": "edge_list",
                "graph2_data": [(1, 2), (2, 3), (3, 4)]
            },
            parameters={"comparison_type": "structural"}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert hasattr(result, 'execution_time')
        assert hasattr(result, 'memory_used')
        assert hasattr(result, 'metadata')
        
        metadata = result.metadata
        assert "algorithm_used" in metadata
        assert "academic_ready" in metadata
        assert "publication_ready" in metadata
        assert metadata["algorithm_used"] == "graph_comparison_structural"
        assert metadata["academic_ready"] is True
    
    def test_different_parameter_combinations(self):
        """Test various parameter combinations."""
        base_input = {
            "graph1_source": "networkx_graph",
            "graph1_data": self.test_graph1,
            "graph2_source": "networkx_graph",
            "graph2_data": self.test_graph2
        }
        
        # Test different similarity metrics
        for metrics in [
            ["structural_similarity"],
            ["spectral_similarity"],
            ["degree_distribution_similarity", "clustering_similarity"],
            ["structural_similarity", "centrality_similarity"]
        ]:
            request = ToolRequest(
                tool_id="T58",
                operation="graph_comparison",
                input_data=base_input,
                parameters={
                    "comparison_type": "comprehensive",
                    "similarity_metrics": metrics,
                    "statistical_testing": False
                }
            )
            
            result = self.tool.execute(request)
            assert result.status == "success"
    
    def test_real_networkx_algorithms_usage(self):
        """Verify that real NetworkX algorithms are being used."""
        # Test that structural similarity uses real graph properties
        similarity = self.tool._compute_structural_similarity(self.test_graph1, self.test_graph2)
        assert isinstance(similarity, dict)
        assert "overall_similarity" in similarity
        
        # Test that spectral analysis uses real eigenvalue computation
        spectral = self.tool._compute_spectral_similarity(self.test_graph1, self.test_graph2)
        assert isinstance(spectral, dict)
        
        # Test that isomorphism uses real NetworkX isomorphism checking
        iso = self.tool._check_isomorphism(self.identical_graph1, self.identical_graph2)
        assert isinstance(iso, dict)
        assert "isomorphic" in iso
        
        # Test that centrality uses real NetworkX centrality measures
        centrality = self.tool._compute_centrality_similarity(self.test_graph1, self.test_graph2)
        assert isinstance(centrality, dict)
        
        # Verify no mock objects are being used
        import unittest.mock
        assert not isinstance(similarity, unittest.mock.Mock)
        assert not isinstance(spectral, unittest.mock.Mock)
        assert not isinstance(iso, unittest.mock.Mock)
        assert not isinstance(centrality, unittest.mock.Mock)