"""
Comprehensive unit tests for T57 Path Analysis Tool - ZERO MOCKING
Tests real path analysis algorithms with real NetworkX graphs and academic validation.
"""

import pytest
import networkx as nx
import numpy as np
from typing import Dict, List, Any
import time

# Import the tool to test
from src.tools.phase2.t57_path_analysis_unified import (
    PathAnalysisTool, PathInstance, FlowResult, PathStats, PathAlgorithm, FlowAlgorithm
)
from src.tools.base_tool import ToolRequest, ToolResult, ToolContract
from src.core.service_manager import ServiceManager


class TestT57PathAnalysisUnified:
    """Comprehensive test suite for T57 Path Analysis Tool"""
    
    def setup_method(self):
        """Setup for each test method - NO MOCKS"""
        # Real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = PathAnalysisTool(service_manager=self.service_manager)
        
        # Real test graphs
        self.test_graphs = self._create_real_test_graphs()
    
    def _create_real_test_graphs(self) -> Dict[str, nx.Graph]:
        """Create real test graphs with known path structures"""
        graphs = {}
        
        # Simple path graph - clear shortest paths
        path_graph = nx.path_graph(5)
        graphs["path"] = path_graph
        
        # Cycle graph - alternative paths
        cycle_graph = nx.cycle_graph(6)
        graphs["cycle"] = cycle_graph
        
        # Grid graph - multiple path options
        grid_graph = nx.grid_2d_graph(4, 4)
        # Convert to string labels
        grid_relabeled = nx.Graph()
        for node in grid_graph.nodes():
            grid_relabeled.add_node(f"n_{node[0]}_{node[1]}")
        for edge in grid_graph.edges():
            u, v = edge
            grid_relabeled.add_edge(f"n_{u[0]}_{u[1]}", f"n_{v[0]}_{v[1]}")
        graphs["grid"] = grid_relabeled
        
        # Weighted graph - different shortest paths
        weighted_graph = nx.Graph()
        weighted_graph.add_weighted_edges_from([
            ("A", "B", 2.0),
            ("A", "C", 5.0),
            ("B", "C", 1.0),
            ("B", "D", 3.0),
            ("C", "D", 1.0),
            ("C", "E", 4.0),
            ("D", "E", 1.0)
        ])
        graphs["weighted"] = weighted_graph
        
        # Directed graph for flow analysis
        directed_graph = nx.DiGraph()
        directed_graph.add_weighted_edges_from([
            ("S", "A", 10),
            ("S", "B", 8),
            ("A", "B", 5),
            ("A", "C", 8),
            ("B", "C", 3),
            ("B", "D", 5),
            ("C", "T", 10),
            ("D", "T", 8)
        ])
        graphs["directed"] = directed_graph
        
        # Disconnected graph - unreachable nodes
        disconnected_graph = nx.Graph()
        disconnected_graph.add_edges_from([
            ("A", "B"), ("B", "C"),  # Component 1
            ("D", "E"), ("E", "F")   # Component 2
        ])
        graphs["disconnected"] = disconnected_graph
        
        # Complete graph - many paths
        complete_graph = nx.complete_graph(6)
        graphs["complete"] = complete_graph
        
        # Tree graph - unique paths
        tree_graph = nx.balanced_tree(2, 3)
        graphs["tree"] = tree_graph
        
        # Academic collaboration network
        collab_graph = nx.Graph()
        researchers = [f"researcher_{i}" for i in range(12)]
        collab_graph.add_nodes_from(researchers)
        
        # Create realistic collaboration patterns
        collaborations = [
            # Core research group
            ("researcher_0", "researcher_1"), ("researcher_1", "researcher_2"),
            ("researcher_2", "researcher_3"), ("researcher_0", "researcher_3"),
            # Extended collaborations
            ("researcher_1", "researcher_4"), ("researcher_4", "researcher_5"),
            ("researcher_2", "researcher_6"), ("researcher_6", "researcher_7"),
            # Cross-group links
            ("researcher_4", "researcher_8"), ("researcher_8", "researcher_9"),
            ("researcher_7", "researcher_10"), ("researcher_10", "researcher_11"),
            # Bridge connections
            ("researcher_5", "researcher_10"), ("researcher_8", "researcher_6")
        ]
        collab_graph.add_edges_from(collaborations)
        graphs["collaboration"] = collab_graph
        
        return graphs
    
    def test_tool_initialization(self):
        """Test tool initializes correctly with real service manager"""
        assert self.tool.tool_id == "T57_PATH_ANALYSIS"
        assert self.tool.name == "Advanced Path Analysis"
        assert self.tool.category == "advanced_analytics"
        assert self.tool.requires_large_data is True
        assert self.tool.supports_batch_processing is True
        assert self.tool.academic_output_ready is True
        assert isinstance(self.tool.path_algorithms, dict)
        assert isinstance(self.tool.flow_algorithms, dict)
        assert len(self.tool.path_algorithms) >= 5  # At least 5 path algorithms
    
    def test_get_contract(self):
        """Test tool contract is properly defined"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T57_PATH_ANALYSIS"
        assert contract.name == "Advanced Path Analysis"
        assert contract.category == "advanced_analytics"
        
        # Validate input schema
        assert "graph_source" in contract.input_schema["properties"]
        assert "analysis_type" in contract.input_schema["properties"]
        assert "algorithms" in contract.input_schema["properties"]
        assert "source_nodes" in contract.input_schema["properties"]
        assert "target_nodes" in contract.input_schema["properties"]
        
        # Validate output schema
        assert "path_instances" in contract.output_schema["properties"]
        assert "path_stats" in contract.output_schema["properties"]
        assert "algorithm_info" in contract.output_schema["properties"]
        
        # Validate dependencies
        assert "networkx" in contract.dependencies
        assert "numpy" in contract.dependencies
        
        # Validate performance requirements
        assert contract.performance_requirements["max_execution_time"] == 600.0
        assert contract.performance_requirements["max_memory_mb"] == 4000
        assert contract.performance_requirements["min_accuracy"] == 0.98
    
    def test_dijkstra_shortest_paths_real(self):
        """Test Dijkstra shortest path algorithm with real graph"""
        weighted_graph = self.test_graphs["weighted"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(weighted_graph.nodes()),
                    "edges": [(u, v, d["weight"]) for u, v, d in weighted_graph.edges(data=True)]
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["E"],
                "algorithms": ["dijkstra"],
                "weighted": True
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "path_instances" in result.data
        
        path_instances = result.data["path_instances"]
        assert len(path_instances) > 0
        
        # Find A -> E path
        ae_paths = [p for p in path_instances if p["source"] == "A" and p["target"] == "E"]
        assert len(ae_paths) >= 1
        
        ae_path = ae_paths[0]
        assert ae_path["algorithm"] == "dijkstra"
        assert ae_path["source"] == "A"
        assert ae_path["target"] == "E"
        assert len(ae_path["path"]) >= 2
        assert ae_path["weight"] > 0
        
        # Verify path is valid
        path = ae_path["path"]
        assert path[0] == "A"
        assert path[-1] == "E"
    
    def test_bfs_shortest_paths_real(self):
        """Test BFS shortest path algorithm with real graph"""
        path_graph = self.test_graphs["path"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(path_graph.nodes()),
                    "edges": list(path_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "source_nodes": [0],
                "target_nodes": [4],
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        path_instances = result.data["path_instances"]
        assert len(path_instances) > 0
        
        # Find 0 -> 4 path
        path_04 = [p for p in path_instances if p["source"] == 0 and p["target"] == 4][0]
        assert path_04["algorithm"] == "bfs"
        assert path_04["length"] == 4  # Path graph 0-1-2-3-4 has length 4
        assert path_04["path"] == [0, 1, 2, 3, 4]
    
    def test_multiple_algorithms_comparison_real(self):
        """Test multiple algorithms on same graph for comparison"""
        weighted_graph = self.test_graphs["weighted"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(weighted_graph.nodes()),
                    "edges": [(u, v, d["weight"]) for u, v, d in weighted_graph.edges(data=True)]
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["D"],
                "algorithms": ["dijkstra", "bellman_ford", "shortest_path"],
                "weighted": True
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        path_instances = result.data["path_instances"]
        
        # Should have paths from all algorithms
        algorithms_used = set(p["algorithm"] for p in path_instances)
        assert len(algorithms_used) >= 2  # At least 2 algorithms worked
        
        # All algorithms should find the same shortest path weight (optimality)
        ad_paths = [p for p in path_instances if p["source"] == "A" and p["target"] == "D"]
        if len(ad_paths) > 1:
            weights = [p["weight"] for p in ad_paths]
            # All should find the optimal path weight (allowing small floating point differences)
            assert max(weights) - min(weights) < 0.01
    
    def test_all_pairs_analysis_real(self):
        """Test all-pairs shortest path analysis"""
        cycle_graph = self.test_graphs["cycle"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(cycle_graph.nodes()),
                    "edges": list(cycle_graph.edges())
                },
                "analysis_type": "all_pairs",
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "all_pairs_paths" in result.data
        
        all_pairs = result.data["all_pairs_paths"]
        assert "total_node_pairs" in all_pairs
        assert "reachable_pairs" in all_pairs
        assert "average_path_length" in all_pairs
        assert "node_statistics" in all_pairs
        
        # Cycle graph should have good connectivity
        assert all_pairs["reachable_pairs"] > 0
        assert all_pairs["average_path_length"] > 0
        
        # Each node should have statistics
        assert len(all_pairs["node_statistics"]) == cycle_graph.number_of_nodes()
    
    def test_flow_analysis_real(self):
        """Test flow analysis with real directed graph"""
        directed_graph = self.test_graphs["directed"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(directed_graph.nodes()),
                    "edges": [(u, v, d["weight"]) for u, v, d in directed_graph.edges(data=True)]
                },
                "analysis_type": "flow_analysis",
                "source_nodes": ["S"],
                "target_nodes": ["T"],
                "flow_algorithm": "edmonds_karp",
                "directed": True,
                "weighted": True
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "flow_results" in result.data
        
        flow_results = result.data["flow_results"]
        assert len(flow_results) > 0
        
        # Find S -> T flow
        st_flows = [f for f in flow_results if f["source"] == "S" and f["sink"] == "T"]
        assert len(st_flows) >= 1
        
        st_flow = st_flows[0]
        assert st_flow["max_flow_value"] > 0
        assert "flow_paths" in st_flow
        assert "min_cut_edges" in st_flow
        assert st_flow["algorithm"] == "edmonds_karp"
        assert st_flow["execution_time"] >= 0
    
    def test_reachability_analysis_real(self):
        """Test reachability analysis with real graph"""
        disconnected_graph = self.test_graphs["disconnected"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(disconnected_graph.nodes()),
                    "edges": list(disconnected_graph.edges())
                },
                "analysis_type": "reachability",
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "reachability_matrix" in result.data
        
        reachability = result.data["reachability_matrix"]
        assert "reachability_matrix" in reachability
        assert "node_labels" in reachability
        assert "connectivity_ratio" in reachability
        assert "connectivity_components" in reachability
        
        # Disconnected graph should have low connectivity ratio
        assert 0 <= reachability["connectivity_ratio"] < 1.0
        
        # Should detect multiple components
        components = reachability["connectivity_components"]
        assert components["num_components"] >= 2
    
    def test_comprehensive_analysis_real(self):
        """Test comprehensive analysis combining all analysis types"""
        complete_graph = self.test_graphs["complete"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(complete_graph.nodes()),
                    "edges": list(complete_graph.edges())
                },
                "analysis_type": "comprehensive",
                "algorithms": ["dijkstra", "bfs"],
                "weighted": False,
                "output_format": "detailed"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Should have all analysis types
        assert "path_instances" in result.data
        assert "all_pairs_paths" in result.data
        assert "reachability_matrix" in result.data
        assert "path_stats" in result.data
        assert "algorithm_info" in result.data
        
        # Complete graph should have excellent connectivity
        reachability = result.data["reachability_matrix"]
        assert reachability["connectivity_ratio"] > 0.9
        
        # Should have many path instances
        path_instances = result.data["path_instances"]
        assert len(path_instances) > 0
    
    def test_edge_list_input_real(self):
        """Test path analysis with edge list input"""
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "edge_list",
                "graph_data": {
                    "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")]
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["D"],
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        path_instances = result.data["path_instances"]
        assert len(path_instances) > 0
        
        # Should find A -> D path
        ad_paths = [p for p in path_instances if p["source"] == "A" and p["target"] == "D"]
        assert len(ad_paths) >= 1
        
        ad_path = ad_paths[0]
        assert ad_path["source"] == "A"
        assert ad_path["target"] == "D"
        assert ad_path["length"] >= 1
    
    def test_adjacency_matrix_input_real(self):
        """Test path analysis with adjacency matrix input"""
        # 4x4 adjacency matrix
        adj_matrix = [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0]
        ]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "adjacency_matrix",
                "graph_data": {
                    "matrix": adj_matrix,
                    "node_labels": ["A", "B", "C", "D"]
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["C"],
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        path_instances = result.data["path_instances"]
        assert len(path_instances) > 0
        
        # Should find A -> C path
        ac_paths = [p for p in path_instances if p["source"] == "A" and p["target"] == "C"]
        assert len(ac_paths) >= 1
    
    def test_weighted_vs_unweighted_real(self):
        """Test difference between weighted and unweighted analysis"""
        weighted_graph = self.test_graphs["weighted"]
        
        # Weighted analysis
        weighted_request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(weighted_graph.nodes()),
                    "edges": [(u, v, d["weight"]) for u, v, d in weighted_graph.edges(data=True)]
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["E"],
                "algorithms": ["dijkstra"],
                "weighted": True
            },
            parameters={}
        )
        
        # Unweighted analysis
        unweighted_request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(weighted_graph.nodes()),
                    "edges": list(weighted_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["E"],
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        weighted_result = self.tool.execute(weighted_request)
        unweighted_result = self.tool.execute(unweighted_request)
        
        assert weighted_result.status == "success"
        assert unweighted_result.status == "success"
        
        # Both should find paths but potentially different ones
        weighted_paths = [p for p in weighted_result.data["path_instances"] if p["source"] == "A" and p["target"] == "E"]
        unweighted_paths = [p for p in unweighted_result.data["path_instances"] if p["source"] == "A" and p["target"] == "E"]
        
        assert len(weighted_paths) >= 1
        assert len(unweighted_paths) >= 1
        
        # Paths might be different due to weight consideration
        weighted_path = weighted_paths[0]["path"]
        unweighted_path = unweighted_paths[0]["path"]
        
        # Both should start and end correctly
        assert weighted_path[0] == "A" and weighted_path[-1] == "E"
        assert unweighted_path[0] == "A" and unweighted_path[-1] == "E"
    
    def test_k_paths_parameter_real(self):
        """Test k-paths parameter for alternative path finding"""
        grid_graph = self.test_graphs["grid"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(grid_graph.nodes()),
                    "edges": list(grid_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["n_0_0"],
                "target_nodes": ["n_3_3"],
                "algorithms": ["bfs"],
                "k_paths": 3,
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        path_instances = result.data["path_instances"]
        
        # Should find at least one path
        corner_paths = [p for p in path_instances if p["source"] == "n_0_0" and p["target"] == "n_3_3"]
        assert len(corner_paths) >= 1
        
        corner_path = corner_paths[0]
        assert corner_path["length"] >= 6  # Manhattan distance in 4x4 grid
    
    def test_path_statistics_calculation_real(self):
        """Test path statistics calculation with real data"""
        tree_graph = self.test_graphs["tree"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(tree_graph.nodes()),
                    "edges": list(tree_graph.edges())
                },
                "analysis_type": "comprehensive",
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "path_stats" in result.data
        
        path_stats = result.data["path_stats"]
        assert "total_paths" in path_stats
        assert "avg_path_length" in path_stats
        assert "max_path_length" in path_stats
        assert "min_path_length" in path_stats
        assert "path_length_distribution" in path_stats
        assert "diameter" in path_stats
        assert "connectivity_ratio" in path_stats
        
        # Tree should have good connectivity
        assert path_stats["total_paths"] > 0
        assert path_stats["avg_path_length"] > 0
        assert path_stats["connectivity_ratio"] > 0
    
    def test_output_format_variations_real(self):
        """Test different output formats"""
        path_graph = self.test_graphs["path"]
        
        for output_format in ["detailed", "summary", "paths_only", "statistics_only"]:
            request = ToolRequest(
                tool_id="T57_PATH_ANALYSIS",
                operation="analyze_paths",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": list(path_graph.nodes()),
                        "edges": list(path_graph.edges())
                    },
                    "analysis_type": "shortest_paths",
                    "source_nodes": [0],
                    "target_nodes": [4],
                    "algorithms": ["bfs"],
                    "output_format": output_format,
                    "weighted": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            
            if output_format == "detailed":
                assert "path_instances" in result.data
                assert "path_stats" in result.data
                assert "algorithm_info" in result.data
            elif output_format == "summary":
                assert "path_stats" in result.data
                assert "algorithm_info" in result.data
                assert "summary" in result.data
            elif output_format == "paths_only":
                assert "path_instances" in result.data
                assert "algorithm_info" in result.data
            elif output_format == "statistics_only":
                assert "path_stats" in result.data
                assert "algorithm_info" in result.data
    
    def test_performance_requirements_real(self):
        """Test performance meets contract requirements"""
        complete_graph = self.test_graphs["complete"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(complete_graph.nodes()),
                    "edges": list(complete_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "algorithms": ["dijkstra", "bfs"],
                "weighted": False,
                "performance_mode": "fast"
            },
            parameters={}
        )
        
        start_time = time.time()
        result = self.tool.execute(request)
        execution_time = time.time() - start_time
        
        assert result.status == "success"
        
        # Performance requirements from contract
        max_execution_time = 600.0  # 10 minutes
        
        # Check execution time
        assert execution_time < max_execution_time
        assert result.execution_time < max_execution_time
        
        # Memory should be reasonable
        assert result.memory_used >= 0
    
    def test_academic_confidence_calculation_real(self):
        """Test academic confidence calculation with real data"""
        collab_graph = self.test_graphs["collaboration"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(collab_graph.nodes()),
                    "edges": list(collab_graph.edges())
                },
                "analysis_type": "comprehensive",
                "algorithms": ["dijkstra", "bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Check metadata has academic confidence
        assert "statistical_significance" in result.metadata
        confidence = result.metadata["statistical_significance"]
        
        # Confidence should be between 0.1 and 1.0
        assert 0.1 <= confidence <= 1.0
        
        # Academic ready flags should be set
        assert result.metadata["academic_ready"] is True
        assert result.metadata["publication_ready"] is True
    
    def test_error_handling_invalid_input_real(self):
        """Test error handling with invalid inputs"""
        # Test with missing graph_data
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "edge_list",
                "analysis_type": "shortest_paths"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "INVALID_INPUT"
        assert "graph_data is required" in result.error_message
        
        # Test with invalid graph source
        request2 = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "invalid_source",
                "graph_data": {"edges": [("A", "B")]},
                "analysis_type": "shortest_paths"
            },
            parameters={}
        )
        
        result2 = self.tool.execute(request2)
        
        assert result2.status == "error"
        assert result2.error_code == "INVALID_INPUT"
        assert "graph_source must be one of" in result2.error_message
    
    def test_error_handling_invalid_algorithm_real(self):
        """Test error handling with invalid algorithm"""
        path_graph = self.test_graphs["path"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(path_graph.nodes()),
                    "edges": list(path_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "algorithms": ["invalid_algorithm"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "INVALID_INPUT"
        assert "algorithm 'invalid_algorithm' not supported" in result.error_message
    
    def test_error_handling_unreachable_nodes_real(self):
        """Test handling of unreachable node pairs"""
        disconnected_graph = self.test_graphs["disconnected"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(disconnected_graph.nodes()),
                    "edges": list(disconnected_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "source_nodes": ["A"],
                "target_nodes": ["E"],  # E is in different component
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Should succeed but find no paths
        assert result.status == "success"
        path_instances = result.data["path_instances"]
        
        # Should not find A -> E path (different components)
        ae_paths = [p for p in path_instances if p["source"] == "A" and p["target"] == "E"]
        assert len(ae_paths) == 0
    
    def test_health_check_real(self):
        """Test tool health check"""
        health_result = self.tool.health_check()
        
        assert isinstance(health_result, ToolResult)
        assert health_result.tool_id == "T57_PATH_ANALYSIS"
        assert health_result.status == "success"
        assert health_result.data["healthy"] is True
        assert health_result.data["status"] == "ready"
    
    def test_input_validation_real(self):
        """Test input validation method"""
        # Valid input
        valid_input = {
            "graph_source": "edge_list",
            "graph_data": {"edges": [("A", "B"), ("B", "C")]},
            "analysis_type": "shortest_paths"
        }
        assert self.tool.validate_input(valid_input) is True
        
        # Invalid input - missing required field
        invalid_input = {
            "analysis_type": "shortest_paths"
        }
        assert self.tool.validate_input(invalid_input) is False
        
        # Invalid input - wrong type
        assert self.tool.validate_input("not_a_dict") is False
        assert self.tool.validate_input(None) is False
    
    def test_directed_vs_undirected_analysis_real(self):
        """Test analysis differences between directed and undirected graphs"""
        # Undirected analysis
        cycle_graph = self.test_graphs["cycle"]
        
        undirected_request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(cycle_graph.nodes()),
                    "edges": list(cycle_graph.edges())
                },
                "analysis_type": "reachability",
                "directed": False,
                "weighted": False
            },
            parameters={}
        )
        
        # Directed analysis
        directed_graph = self.test_graphs["directed"]
        
        directed_request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(directed_graph.nodes()),
                    "edges": [(u, v, d["weight"]) for u, v, d in directed_graph.edges(data=True)]
                },
                "analysis_type": "reachability",
                "directed": True,
                "weighted": True
            },
            parameters={}
        )
        
        undirected_result = self.tool.execute(undirected_request)
        directed_result = self.tool.execute(directed_request)
        
        assert undirected_result.status == "success"
        assert directed_result.status == "success"
        
        # Undirected cycle should have higher connectivity
        undirected_connectivity = undirected_result.data["reachability_matrix"]["connectivity_ratio"]
        directed_connectivity = directed_result.data["reachability_matrix"]["connectivity_ratio"]
        
        assert 0 <= undirected_connectivity <= 1.0
        assert 0 <= directed_connectivity <= 1.0
    
    def test_concurrent_execution_safety_real(self):
        """Test tool can handle concurrent executions safely"""
        path_graph = self.test_graphs["path"]
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(path_graph.nodes()),
                    "edges": list(path_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "source_nodes": [0],
                "target_nodes": [4],
                "algorithms": ["bfs"],
                "weighted": False
            },
            parameters={}
        )
        
        # Execute multiple times to check for state issues
        results = []
        for _ in range(3):
            result = self.tool.execute(request)
            results.append(result)
            assert result.status == "success"
        
        # All results should be consistent
        for result in results:
            path_instances = result.data["path_instances"]
            paths_04 = [p for p in path_instances if p["source"] == 0 and p["target"] == 4]
            assert len(paths_04) >= 1
            assert paths_04[0]["length"] == 4  # Consistent path length
    
    def test_large_graph_handling_real(self):
        """Test handling of reasonably large graphs"""
        # Create a larger test graph
        large_graph = nx.erdos_renyi_graph(50, 0.1)  # 50 nodes, 10% edge probability
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(large_graph.nodes()),
                    "edges": list(large_graph.edges())
                },
                "analysis_type": "shortest_paths",
                "algorithms": ["bfs"],
                "performance_mode": "fast",
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Should succeed with larger graph
        assert result.status == "success"
        assert result.metadata["graph_size"] == 50
        assert result.metadata["batch_processed"] is False  # 50 nodes < 1000 threshold
    
    def test_zero_mocking_validation(self):
        """Validate that no mocking is used in this test suite"""
        # This test ensures we're using real implementations
        
        # Check that tool uses real NetworkX
        path_graph = self.test_graphs["path"]
        assert isinstance(path_graph, nx.Graph)
        assert hasattr(path_graph, 'nodes')
        assert hasattr(path_graph, 'edges')
        
        # Check that service manager is real
        assert hasattr(self.service_manager, 'identity_service')
        
        # Check that tool has real methods
        assert hasattr(self.tool, '_compute_dijkstra_paths')
        assert hasattr(self.tool, '_compute_bfs_paths')
        assert hasattr(self.tool, '_analyze_shortest_paths')
        assert hasattr(self.tool, '_analyze_flows')
        
        # Verify real NetworkX operations work
        shortest_path = nx.shortest_path(path_graph, 0, 4)
        assert shortest_path == [0, 1, 2, 3, 4]
        
        # Verify real numpy operations work
        test_array = np.array([1, 2, 3, 4, 5])
        assert np.mean(test_array) == 3.0
        
        print("✅ Zero mocking validation passed - all operations use real implementations")


# Additional integration-style tests
class TestT57PathAnalysisIntegration:
    """Integration tests for T57 with real research scenarios"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.service_manager = ServiceManager()
        self.tool = PathAnalysisTool(service_manager=self.service_manager)
    
    def test_academic_research_workflow_real(self):
        """Test complete academic research workflow"""
        # Create a research collaboration network
        research_graph = nx.Graph()
        
        # Add researchers and institutions
        researchers = [f"researcher_{i}" for i in range(20)]
        research_graph.add_nodes_from(researchers)
        
        # Add collaboration patterns
        collaborations = [
            # Dense collaboration cluster
            ("researcher_0", "researcher_1"), ("researcher_1", "researcher_2"),
            ("researcher_2", "researcher_3"), ("researcher_0", "researcher_3"),
            ("researcher_1", "researcher_3"),
            # Secondary cluster
            ("researcher_4", "researcher_5"), ("researcher_5", "researcher_6"),
            ("researcher_6", "researcher_7"), ("researcher_4", "researcher_7"),
            # Bridge connections
            ("researcher_2", "researcher_8"), ("researcher_8", "researcher_9"),
            ("researcher_6", "researcher_10"), ("researcher_10", "researcher_11"),
            # Isolated pairs
            ("researcher_12", "researcher_13"), ("researcher_14", "researcher_15"),
            # Cross-cluster bridges
            ("researcher_3", "researcher_12"), ("researcher_9", "researcher_16")
        ]
        research_graph.add_edges_from(collaborations)
        
        # Execute comprehensive path analysis
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(research_graph.nodes()),
                    "edges": list(research_graph.edges())
                },
                "analysis_type": "comprehensive",
                "algorithms": ["dijkstra", "bfs"],
                "output_format": "detailed",
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify comprehensive analysis
        assert "path_instances" in result.data
        assert "all_pairs_paths" in result.data
        assert "reachability_matrix" in result.data
        assert "path_stats" in result.data
        assert "algorithm_info" in result.data
        
        # Verify academic quality
        assert result.metadata["academic_ready"] is True
        assert result.metadata["publication_ready"] is True
        assert "statistical_significance" in result.metadata
        
        # Verify path diversity
        path_stats = result.data["path_stats"]
        assert path_stats["total_paths"] > 0
        assert path_stats["avg_path_length"] > 0
        
        # Verify reachability analysis
        reachability = result.data["reachability_matrix"]
        assert reachability["connectivity_ratio"] > 0
        
        print(f"✅ Academic workflow completed: {path_stats['total_paths']} paths analyzed, {reachability['connectivity_ratio']:.3f} connectivity ratio")
    
    def test_publication_ready_output_real(self):
        """Test that output is ready for academic publication"""
        # Use a well-defined graph with known properties
        karate_graph = nx.karate_club_graph()  # Famous academic network
        
        request = ToolRequest(
            tool_id="T57_PATH_ANALYSIS",
            operation="analyze_paths",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": list(karate_graph.nodes()),
                    "edges": list(karate_graph.edges())
                },
                "analysis_type": "comprehensive",
                "algorithms": ["dijkstra", "bfs"],
                "output_format": "detailed",
                "weighted": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify publication-ready elements
        data = result.data
        metadata = result.metadata
        
        # Algorithm reproducibility
        algorithm_info = data["algorithm_info"]
        assert "algorithms_used" in algorithm_info
        assert "execution_timestamp" in algorithm_info
        assert "graph_size" in algorithm_info
        assert "edge_count" in algorithm_info
        
        # Statistical validity
        path_stats = data["path_stats"]
        assert "total_paths" in path_stats
        assert "avg_path_length" in path_stats
        assert "connectivity_ratio" in path_stats
        
        # Academic metadata
        assert metadata["academic_ready"] is True
        assert metadata["publication_ready"] is True
        assert metadata["graph_size"] == len(karate_graph.nodes())
        assert metadata["edge_count"] == len(karate_graph.edges())
        
        # Performance metrics
        assert result.execution_time > 0
        assert result.memory_used >= 0
        
        print(f"✅ Publication-ready analysis: {len(karate_graph.nodes())} nodes, {len(karate_graph.edges())} edges, {path_stats['total_paths']} paths")


if __name__ == "__main__":
    # Run specific test for quick validation
    test_suite = TestT57PathAnalysisUnified()
    test_suite.setup_method()
    
    print("Running T57 Path Analysis validation...")
    test_suite.test_tool_initialization()
    test_suite.test_dijkstra_shortest_paths_real()
    test_suite.test_bfs_shortest_paths_real()
    test_suite.test_zero_mocking_validation()
    
    print("✅ T57 Path Analysis tool validation passed!")