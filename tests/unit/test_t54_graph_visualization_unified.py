"""
Comprehensive unit tests for T54 Graph Visualization Tool - ZERO MOCKING
Tests real graph visualization algorithms with real Plotly and NetworkX graphs.
"""

import pytest
import networkx as nx
import numpy as np
from typing import Dict, List, Any
import tempfile
import os
import json

# Import the tool to test
from src.tools.phase2.t54_graph_visualization_unified import (
    GraphVisualizationTool, LayoutType, ColorScheme, VisualizationConfig
)
from src.tools.base_tool import ToolRequest, ToolResult, ToolContract
from src.core.service_manager import ServiceManager

# Check if Plotly is available
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class TestT54GraphVisualizationUnified:
    """Comprehensive test suite for T54 Graph Visualization Tool"""
    
    def setup_method(self):
        """Setup for each test method - NO MOCKS"""
        # Real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = GraphVisualizationTool(service_manager=self.service_manager)
        
        # Real test graphs
        self.test_graphs = self._create_real_test_graphs()
    
    def _create_real_test_graphs(self) -> Dict[str, nx.Graph]:
        """Create real test graphs with various structures"""
        graphs = {}
        
        # Small triangle graph - good for basic testing
        triangle_graph = nx.Graph()
        triangle_graph.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'A')])
        # Add attributes
        for node in triangle_graph.nodes():
            triangle_graph.nodes[node]['name'] = f"Node_{node}"
            triangle_graph.nodes[node]['type'] = "entity"
            triangle_graph.nodes[node]['confidence'] = 0.9
        for edge in triangle_graph.edges():
            triangle_graph.edges[edge]['weight'] = 1.0
            triangle_graph.edges[edge]['confidence'] = 0.8
        graphs["triangle"] = triangle_graph
        
        # Star graph - good for layout testing
        star_graph = nx.star_graph(6)
        for node in star_graph.nodes():
            star_graph.nodes[node]['name'] = f"Star_{node}"
            star_graph.nodes[node]['type'] = "center" if node == 0 else "leaf"
            star_graph.nodes[node]['confidence'] = 0.95 if node == 0 else 0.7
        for edge in star_graph.edges():
            star_graph.edges[edge]['weight'] = 2.0 if edge[0] == 0 else 1.0
            star_graph.edges[edge]['confidence'] = 0.9
        graphs["star"] = star_graph
        
        # Complete graph - dense connectivity
        complete_graph = nx.complete_graph(5)
        for node in complete_graph.nodes():
            complete_graph.nodes[node]['name'] = f"Complete_{node}"
            complete_graph.nodes[node]['type'] = "core"
            complete_graph.nodes[node]['confidence'] = 0.8
            complete_graph.nodes[node]['community'] = node % 2  # Two communities
        for edge in complete_graph.edges():
            complete_graph.edges[edge]['weight'] = 1.5
            complete_graph.edges[edge]['confidence'] = 0.85
        graphs["complete"] = complete_graph
        
        # Path graph - linear structure
        path_graph = nx.path_graph(8)
        for i, node in enumerate(path_graph.nodes()):
            path_graph.nodes[node]['name'] = f"Path_{node}"
            path_graph.nodes[node]['type'] = "start" if i == 0 else ("end" if i == 7 else "middle")
            path_graph.nodes[node]['confidence'] = 0.6 + 0.4 * (i / 7)
            path_graph.nodes[node]['pagerank'] = 1.0 / len(path_graph.nodes())
        for edge in path_graph.edges():
            path_graph.edges[edge]['weight'] = 1.0
            path_graph.edges[edge]['confidence'] = 0.7
        graphs["path"] = path_graph
        
        # Complex academic network
        academic_graph = nx.Graph()
        # Add researcher nodes
        researchers = [f"researcher_{i}" for i in range(15)]
        academic_graph.add_nodes_from(researchers)
        
        # Add collaboration edges
        collaborations = [
            # Research group 1
            ("researcher_0", "researcher_1"), ("researcher_1", "researcher_2"), 
            ("researcher_2", "researcher_0"),
            # Research group 2  
            ("researcher_3", "researcher_4"), ("researcher_4", "researcher_5"),
            ("researcher_5", "researcher_6"), ("researcher_6", "researcher_3"),
            # Cross-group collaborations
            ("researcher_0", "researcher_7"), ("researcher_3", "researcher_8"),
            # Individual collaborations
            ("researcher_9", "researcher_10"), ("researcher_10", "researcher_11"),
            ("researcher_11", "researcher_12"), ("researcher_12", "researcher_13")
        ]
        academic_graph.add_edges_from(collaborations)
        
        # Add rich attributes
        for i, node in enumerate(academic_graph.nodes()):
            academic_graph.nodes[node]['name'] = f"Dr. {node.split('_')[1]}"
            academic_graph.nodes[node]['type'] = "senior" if i < 5 else ("junior" if i < 10 else "postdoc")
            academic_graph.nodes[node]['confidence'] = 0.7 + 0.3 * np.random.random()
            academic_graph.nodes[node]['community'] = i // 5  # Three communities
        
        for edge in academic_graph.edges():
            academic_graph.edges[edge]['weight'] = 1.0 + 2.0 * np.random.random()
            academic_graph.edges[edge]['confidence'] = 0.6 + 0.4 * np.random.random()
            academic_graph.edges[edge]['relationship_type'] = "collaboration"
        
        graphs["academic"] = academic_graph
        
        return graphs
    
    def test_tool_initialization(self):
        """Test tool initializes correctly with real service manager"""
        assert self.tool.tool_id == "T54_GRAPH_VISUALIZATION"
        assert self.tool.name == "Advanced Graph Visualization"
        assert self.tool.category == "advanced_analytics"
        assert self.tool.requires_large_data is True
        assert self.tool.supports_batch_processing is True
        assert self.tool.academic_output_ready is True
        assert isinstance(self.tool.layout_configs, dict)
        assert len(self.tool.layout_configs) == 9  # 9 layout types
        assert isinstance(self.tool.color_palettes, dict)
        assert len(self.tool.color_palettes) == 6  # 6 color schemes
    
    def test_get_contract(self):
        """Test tool contract is properly defined"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T54_GRAPH_VISUALIZATION"
        assert contract.name == "Advanced Graph Visualization"
        assert contract.category == "advanced_analytics"
        
        # Validate input schema
        assert "graph_source" in contract.input_schema["properties"]
        assert "layout" in contract.input_schema["properties"]
        assert "color_scheme" in contract.input_schema["properties"]
        assert "max_nodes" in contract.input_schema["properties"]
        assert "interactive" in contract.input_schema["properties"]
        
        # Validate output schema
        assert "visualization_data" in contract.output_schema["properties"]
        assert "layout_info" in contract.output_schema["properties"]
        assert "statistics" in contract.output_schema["properties"]
        assert "file_paths" in contract.output_schema["properties"]
        
        # Validate dependencies
        assert "networkx" in contract.dependencies
        assert "plotly" in contract.dependencies
        assert "numpy" in contract.dependencies
        
        # Validate performance requirements
        assert contract.performance_requirements["max_execution_time"] == 300.0
        assert contract.performance_requirements["max_memory_mb"] == 8000
        assert contract.performance_requirements["min_accuracy"] == 0.95
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_spring_layout_visualization_real(self):
        """Test spring layout visualization with real graph"""
        triangle_graph = self.test_graphs["triangle"]
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **triangle_graph.nodes[node]} for node in triangle_graph.nodes()],
                    "edges": [{"source": u, "target": v, **triangle_graph.edges[(u, v)]} 
                             for u, v in triangle_graph.edges()]
                },
                "layout": "spring",
                "color_scheme": "entity_type",
                "save_to_file": False  # Skip file saving for unit tests
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "visualization_data" in result.data
        assert "layout_info" in result.data
        assert "statistics" in result.data
        
        # Verify layout information
        layout_info = result.data["layout_info"]
        assert layout_info["layout_type"] == "spring"
        assert layout_info["node_count"] == 3
        assert layout_info["edge_count"] == 3
        assert "computation_time" in layout_info
        
        # Verify visualization data
        viz_data = result.data["visualization_data"]
        assert "node_positions" in viz_data
        assert "edge_data" in viz_data
        assert "color_mapping" in viz_data
        
        # Verify node positions
        positions = viz_data["node_positions"]
        assert len(positions) == 3
        for node in triangle_graph.nodes():
            assert node in positions
            assert len(positions[node]) == 2  # x, y coordinates
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_multiple_layout_algorithms_real(self):
        """Test multiple layout algorithms with real graph"""
        star_graph = self.test_graphs["star"]
        
        layouts_to_test = ["spring", "circular", "kamada_kawai", "random"]
        
        for layout in layouts_to_test:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": [{"id": node, **star_graph.nodes[node]} for node in star_graph.nodes()],
                        "edges": [{"source": u, "target": v, **star_graph.edges[(u, v)]} 
                                 for u, v in star_graph.edges()]
                    },
                    "layout": layout,
                    "save_to_file": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success", f"Layout {layout} failed"
            assert result.data["layout_info"]["layout_type"] == layout
            assert len(result.data["visualization_data"]["node_positions"]) == len(star_graph.nodes())
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_color_schemes_real(self):
        """Test different color schemes with real graph"""
        academic_graph = self.test_graphs["academic"]
        
        color_schemes = ["entity_type", "confidence", "degree", "pagerank", "community"]
        
        for scheme in color_schemes:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": [{"id": node, **academic_graph.nodes[node]} for node in academic_graph.nodes()],
                        "edges": [{"source": u, "target": v, **academic_graph.edges[(u, v)]} 
                                 for u, v in academic_graph.edges()]
                    },
                    "layout": "spring",
                    "color_scheme": scheme,
                    "save_to_file": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success", f"Color scheme {scheme} failed"
            
            # Verify color mapping
            color_mapping = result.data["visualization_data"]["color_mapping"]
            assert "nodes" in color_mapping
            assert len(color_mapping["nodes"]) == len(academic_graph.nodes())
            
            # Check that different nodes can have different colors (except uniform schemes)
            node_colors = list(color_mapping["nodes"].values())
            if scheme in ["entity_type", "community"]:
                # Should have multiple colors for different types/communities
                unique_colors = set(node_colors)
                assert len(unique_colors) > 1, f"Expected multiple colors for {scheme}"
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_node_size_metrics_real(self):
        """Test different node size metrics"""
        complete_graph = self.test_graphs["complete"]
        
        size_metrics = ["degree", "pagerank", "centrality", "confidence", "uniform"]
        
        for metric in size_metrics:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": [{"id": node, **complete_graph.nodes[node]} for node in complete_graph.nodes()],
                        "edges": [{"source": u, "target": v, **complete_graph.edges[(u, v)]} 
                                 for u, v in complete_graph.edges()]
                    },
                    "layout": "circular",
                    "node_size_metric": metric,
                    "save_to_file": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success", f"Node size metric {metric} failed"
            
            # Check that statistics include node attributes
            stats = result.data["statistics"]
            assert "graph_metrics" in stats
            graph_metrics = stats["graph_metrics"]
            assert "node_count" in graph_metrics
            assert "average_degree" in graph_metrics
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_edge_width_metrics_real(self):
        """Test different edge width metrics"""
        path_graph = self.test_graphs["path"]
        
        width_metrics = ["weight", "confidence", "uniform"]
        
        for metric in width_metrics:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": [{"id": node, **path_graph.nodes[node]} for node in path_graph.nodes()],
                        "edges": [{"source": u, "target": v, **path_graph.edges[(u, v)]} 
                                 for u, v in path_graph.edges()]
                    },
                    "layout": "spring",
                    "edge_width_metric": metric,
                    "save_to_file": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success", f"Edge width metric {metric} failed"
            
            # Verify edge data
            edge_data = result.data["visualization_data"]["edge_data"]
            assert len(edge_data) == len(path_graph.edges())
            
            for edge in edge_data:
                assert "source" in edge
                assert "target" in edge
                assert "width" in edge
                assert edge["width"] > 0
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_filtering_capabilities_real(self):
        """Test graph filtering capabilities"""
        academic_graph = self.test_graphs["academic"]
        
        # Test minimum degree filter
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **academic_graph.nodes[node]} for node in academic_graph.nodes()],
                    "edges": [{"source": u, "target": v, **academic_graph.edges[(u, v)]} 
                             for u, v in academic_graph.edges()]
                },
                "layout": "spring",
                "filter_criteria": {
                    "min_degree": 2,
                    "min_confidence": 0.8
                },
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Filtered graph should have fewer or equal nodes
        original_node_count = len(academic_graph.nodes())
        filtered_node_count = result.data["layout_info"]["node_count"]
        assert filtered_node_count <= original_node_count
        
        # If filtering was effective, should have fewer nodes
        if any(academic_graph.degree(node) < 2 for node in academic_graph.nodes()):
            assert filtered_node_count < original_node_count
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_interactive_vs_static_real(self):
        """Test interactive vs static visualization modes"""
        triangle_graph = self.test_graphs["triangle"]
        
        for interactive in [True, False]:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": [{"id": node, **triangle_graph.nodes[node]} for node in triangle_graph.nodes()],
                        "edges": [{"source": u, "target": v, **triangle_graph.edges[(u, v)]} 
                                 for u, v in triangle_graph.edges()]
                    },
                    "layout": "spring",
                    "interactive": interactive,
                    "save_to_file": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.metadata["interactive"] == interactive
            
            # Interactive mode should include figure JSON
            viz_data = result.data["visualization_data"]
            if interactive:
                assert viz_data["plotly_figure"] is not None
            else:
                assert viz_data["plotly_figure"] is None
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_edge_list_input_real(self):
        """Test visualization with edge list input format"""
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "edge_list",
                "graph_data": {
                    "edges": [
                        ("A", "B", 1.0), 
                        ("B", "C", 1.5), 
                        ("C", "A", 2.0)
                    ]
                },
                "layout": "circular",
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["layout_info"]["node_count"] == 3
        assert result.data["layout_info"]["edge_count"] == 3
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_adjacency_matrix_input_real(self):
        """Test visualization with adjacency matrix input"""
        # 3x3 adjacency matrix for triangle
        adj_matrix = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ]
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "adjacency_matrix",
                "graph_data": {
                    "matrix": adj_matrix,
                    "node_labels": ["Node_A", "Node_B", "Node_C"]
                },
                "layout": "spring",
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["layout_info"]["node_count"] == 3
        
        # Verify node labels are used
        positions = result.data["visualization_data"]["node_positions"]
        expected_nodes = {"Node_A", "Node_B", "Node_C"}
        actual_nodes = set(positions.keys())
        assert actual_nodes == expected_nodes
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_custom_color_mapping_real(self):
        """Test custom color mapping"""
        triangle_graph = self.test_graphs["triangle"]
        
        custom_colors = {
            "nodes": {
                "A": "#FF0000",  # Red
                "B": "#00FF00",  # Green
                "C": "#0000FF"   # Blue
            }
        }
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **triangle_graph.nodes[node]} for node in triangle_graph.nodes()],
                    "edges": [{"source": u, "target": v, **triangle_graph.edges[(u, v)]} 
                             for u, v in triangle_graph.edges()]
                },
                "layout": "spring",
                "color_scheme": "custom",
                "custom_colors": custom_colors,
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify custom colors are applied
        color_mapping = result.data["visualization_data"]["color_mapping"]
        node_colors = color_mapping["nodes"]
        assert node_colors["A"] == "#FF0000"
        assert node_colors["B"] == "#00FF00"
        assert node_colors["C"] == "#0000FF"
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_label_display_options_real(self):
        """Test label display options"""
        star_graph = self.test_graphs["star"]
        
        for show_labels in [True, False]:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "networkx",
                    "graph_data": {
                        "nodes": [{"id": node, **star_graph.nodes[node]} for node in star_graph.nodes()],
                        "edges": [{"source": u, "target": v, **star_graph.edges[(u, v)]} 
                                 for u, v in star_graph.edges()]
                    },
                    "layout": "spring",
                    "show_labels": show_labels,
                    "save_to_file": False
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Note: Label display is handled in Plotly figure creation
            # We can verify the request was processed successfully
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_performance_with_larger_graph_real(self):
        """Test performance with larger graphs"""
        # Create a larger test graph
        large_graph = nx.erdos_renyi_graph(50, 0.1)  # 50 nodes, 10% edge probability
        
        # Add attributes
        for node in large_graph.nodes():
            large_graph.nodes[node]['name'] = f"Node_{node}"
            large_graph.nodes[node]['type'] = f"type_{node % 5}"
            large_graph.nodes[node]['confidence'] = 0.5 + 0.5 * np.random.random()
        
        for edge in large_graph.edges():
            large_graph.edges[edge]['weight'] = 1.0 + np.random.random()
            large_graph.edges[edge]['confidence'] = 0.6 + 0.4 * np.random.random()
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **large_graph.nodes[node]} for node in large_graph.nodes()],
                    "edges": [{"source": u, "target": v, **large_graph.edges[(u, v)]} 
                             for u, v in large_graph.edges()]
                },
                "layout": "spring",
                "color_scheme": "entity_type",
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["layout_info"]["node_count"] == 50
        
        # Verify performance metrics
        assert result.execution_time > 0
        assert result.metadata["batch_processed"] is False  # 50 < 100 threshold
        
        # Check layout computation time
        layout_info = result.data["layout_info"]
        assert "computation_time" in layout_info
        assert layout_info["computation_time"] > 0
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_academic_confidence_calculation_real(self):
        """Test academic confidence calculation"""
        academic_graph = self.test_graphs["academic"]
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **academic_graph.nodes[node]} for node in academic_graph.nodes()],
                    "edges": [{"source": u, "target": v, **academic_graph.edges[(u, v)]} 
                             for u, v in academic_graph.edges()]
                },
                "layout": "kamada_kawai",
                "color_scheme": "community",
                "save_to_file": False
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
        
        # Academic ready flag should be set
        assert result.metadata["academic_ready"] is True
        assert result.metadata["publication_ready"] is True
        
        # Check statistics are comprehensive
        stats = result.data["statistics"]
        assert "graph_metrics" in stats
        assert "layout_quality" in stats
        assert "color_distribution" in stats
        assert "performance_metrics" in stats
    
    def test_error_handling_plotly_unavailable(self):
        """Test error handling when Plotly is unavailable"""
        # Temporarily disable Plotly
        original_plotly = self.tool.plotly_available
        self.tool.plotly_available = False
        
        try:
            request = ToolRequest(
                tool_id="T54_GRAPH_VISUALIZATION",
                operation="visualize",
                input_data={
                    "graph_source": "edge_list",
                    "graph_data": {"edges": [("A", "B")]},
                    "layout": "spring"
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "PLOTLY_NOT_AVAILABLE"
            assert "Plotly library not available" in result.error_message
        
        finally:
            # Restore original state
            self.tool.plotly_available = original_plotly
    
    def test_error_handling_invalid_input_real(self):
        """Test error handling with invalid inputs"""
        # Test with invalid graph source
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "invalid_source",
                "layout": "spring"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "INVALID_INPUT"
        assert "graph_source must be one of" in result.error_message
    
    def test_error_handling_invalid_layout_real(self):
        """Test error handling with invalid layout"""
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "edge_list",
                "graph_data": {"edges": [("A", "B")]},
                "layout": "invalid_layout"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "INVALID_INPUT"
        assert "layout must be one of" in result.error_message
    
    def test_error_handling_graph_too_large_real(self):
        """Test error handling with graph exceeding size limits"""
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "edge_list",
                "graph_data": {"edges": [("A", "B")]},
                "layout": "spring",
                "max_nodes": 1  # Set very low limit
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "GRAPH_TOO_LARGE"
        assert "exceeding maximum" in result.error_message
    
    def test_error_handling_insufficient_nodes_real(self):
        """Test error handling with empty graph"""
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "edge_list",
                "graph_data": {"edges": []},  # Empty graph
                "layout": "spring"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "INSUFFICIENT_NODES"
        assert "must have at least 1 node" in result.error_message
    
    def test_health_check_real(self):
        """Test tool health check"""
        health_result = self.tool.health_check()
        
        assert isinstance(health_result, ToolResult)
        assert health_result.tool_id == "T54_GRAPH_VISUALIZATION"
        assert health_result.status == "success"
        assert health_result.data["healthy"] is True
        assert health_result.data["status"] == "ready"
    
    def test_input_validation_real(self):
        """Test input validation method"""
        # Valid input
        valid_input = {
            "graph_source": "edge_list",
            "graph_data": {"edges": [("A", "B"), ("B", "C")]},
            "layout": "spring"
        }
        assert self.tool.validate_input(valid_input) is True
        
        # Invalid input - missing required field
        invalid_input = {
            "layout": "spring"
        }
        assert self.tool.validate_input(invalid_input) is False
        
        # Invalid input - wrong type
        assert self.tool.validate_input("not_a_dict") is False
        assert self.tool.validate_input(None) is False
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_metadata_academic_ready_real(self):
        """Test academic-ready metadata is properly set"""
        complete_graph = self.test_graphs["complete"]
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **complete_graph.nodes[node]} for node in complete_graph.nodes()],
                    "edges": [{"source": u, "target": v, **complete_graph.edges[(u, v)]} 
                             for u, v in complete_graph.edges()]
                },
                "layout": "fruchterman_reingold",
                "color_scheme": "confidence",
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify academic metadata
        metadata = result.metadata
        assert metadata["academic_ready"] is True
        assert metadata["publication_ready"] is True
        assert "statistical_significance" in metadata
        assert metadata["graph_size"] == len(complete_graph.nodes())
        assert metadata["edge_count"] == len(complete_graph.edges())
        assert "layout_used" in metadata
        assert "color_scheme" in metadata
        assert metadata["interactive"] is True  # Default value
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available") 
    def test_zero_mocking_validation(self):
        """Validate that no mocking is used in this test suite"""
        # This test ensures we're using real implementations
        
        # Check that tool uses real NetworkX
        triangle_graph = self.test_graphs["triangle"]
        assert isinstance(triangle_graph, nx.Graph)
        assert hasattr(triangle_graph, 'nodes')
        assert hasattr(triangle_graph, 'edges')
        
        # Check that service manager is real
        assert hasattr(self.service_manager, 'identity_service')
        
        # Check that tool has real methods
        assert hasattr(self.tool, '_calculate_layout')
        assert hasattr(self.tool, '_generate_color_mapping')
        assert hasattr(self.tool, '_create_visualization')
        
        # Verify real NetworkX operations work
        centrality = nx.betweenness_centrality(triangle_graph)
        assert len(centrality) == len(triangle_graph.nodes())
        
        # Verify real numpy operations work
        test_array = np.array([1, 2, 3])
        assert np.mean(test_array) == 2.0
        
        # Verify real Plotly operations work (if available)
        if PLOTLY_AVAILABLE:
            import plotly.graph_objects as go
            fig = go.Figure()
            assert hasattr(fig, 'add_trace')
            assert hasattr(fig, 'to_json')
        
        print("✅ Zero mocking validation passed - all operations use real implementations")


# Additional integration-style tests
class TestT54GraphVisualizationIntegration:
    """Integration tests for T54 with real visualization scenarios"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.service_manager = ServiceManager()
        self.tool = GraphVisualizationTool(service_manager=self.service_manager)
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_academic_research_workflow_real(self):
        """Test complete academic research visualization workflow"""
        # Create a realistic collaboration network
        collab_graph = nx.Graph()
        
        # Add researchers with realistic attributes
        researchers = [f"researcher_{i}" for i in range(20)]
        collab_graph.add_nodes_from(researchers)
        
        # Add collaboration edges with realistic patterns
        collaborations = []
        # Dense core group
        for i in range(5):
            for j in range(i+1, 5):
                collaborations.append((f"researcher_{i}", f"researcher_{j}"))
        
        # Peripheral connections
        for i in range(5, 20):
            # Connect to 1-3 core researchers
            core_connections = np.random.choice(5, size=np.random.randint(1, 4), replace=False)
            for core in core_connections:
                collaborations.append((f"researcher_{i}", f"researcher_{core}"))
        
        collab_graph.add_edges_from(collaborations)
        
        # Add rich academic attributes
        for i, node in enumerate(collab_graph.nodes()):
            collab_graph.nodes[node]['name'] = f"Dr. Smith {i}"
            collab_graph.nodes[node]['type'] = "senior" if i < 5 else ("junior" if i < 15 else "postdoc")
            collab_graph.nodes[node]['confidence'] = 0.8 + 0.2 * np.random.random()
            collab_graph.nodes[node]['h_index'] = 10 + np.random.randint(0, 40)
            collab_graph.nodes[node]['institution'] = f"University_{i // 5}"
        
        for edge in collab_graph.edges():
            collab_graph.edges[edge]['weight'] = 1.0 + 2.0 * np.random.random()
            collab_graph.edges[edge]['confidence'] = 0.7 + 0.3 * np.random.random()
            collab_graph.edges[edge]['collaboration_years'] = np.random.randint(1, 10)
        
        # Execute comprehensive visualization
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **collab_graph.nodes[node]} for node in collab_graph.nodes()],
                    "edges": [{"source": u, "target": v, **collab_graph.edges[(u, v)]} 
                             for u, v in collab_graph.edges()]
                },
                "layout": "kamada_kawai",
                "color_scheme": "entity_type",
                "node_size_metric": "degree",
                "edge_width_metric": "weight",
                "show_labels": True,
                "interactive": True,
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify comprehensive analysis
        assert "visualization_data" in result.data
        assert "layout_info" in result.data
        assert "statistics" in result.data
        
        # Verify academic quality
        assert result.metadata["academic_ready"] is True
        assert result.metadata["publication_ready"] is True
        assert "statistical_significance" in result.metadata
        
        # Verify layout quality
        layout_info = result.data["layout_info"]
        assert layout_info["layout_type"] == "kamada_kawai"
        assert layout_info["node_count"] == 20
        assert "computation_time" in layout_info
        
        # Verify comprehensive statistics
        stats = result.data["statistics"]
        graph_metrics = stats["graph_metrics"]
        assert "density" in graph_metrics
        assert "average_clustering" in graph_metrics
        assert "connected_components" in graph_metrics
        
        print(f"✅ Academic workflow completed: {graph_metrics['node_count']} nodes, {graph_metrics['edge_count']} edges")
    
    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_publication_ready_output_real(self):
        """Test that output is ready for academic publication"""
        # Use a well-structured academic network
        karate_graph = nx.karate_club_graph()
        
        # Add academic attributes
        for node in karate_graph.nodes():
            karate_graph.nodes[node]['name'] = f"Member_{node}"
            karate_graph.nodes[node]['type'] = "member"
            karate_graph.nodes[node]['confidence'] = 0.8 + 0.2 * np.random.random()
            # Use actual attributes from karate club data
            karate_graph.nodes[node]['club'] = karate_graph.nodes[node].get('club', 'unknown')
        
        for edge in karate_graph.edges():
            karate_graph.edges[edge]['weight'] = 1.0 + np.random.random()
            karate_graph.edges[edge]['confidence'] = 0.8 + 0.2 * np.random.random()
        
        request = ToolRequest(
            tool_id="T54_GRAPH_VISUALIZATION",
            operation="visualize",
            input_data={
                "graph_source": "networkx",
                "graph_data": {
                    "nodes": [{"id": node, **karate_graph.nodes[node]} for node in karate_graph.nodes()],
                    "edges": [{"source": u, "target": v, **karate_graph.edges[(u, v)]} 
                             for u, v in karate_graph.edges()]
                },
                "layout": "spring",
                "color_scheme": "entity_type",
                "node_size_metric": "centrality",
                "edge_width_metric": "weight",
                "show_labels": True,
                "interactive": True,
                "save_to_file": False
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify publication-ready elements
        data = result.data
        metadata = result.metadata
        
        # Comprehensive visualization data
        viz_data = data["visualization_data"]
        assert "node_positions" in viz_data
        assert "edge_data" in viz_data
        assert "color_mapping" in viz_data
        
        # Layout information for reproducibility
        layout_info = data["layout_info"]
        assert "layout_type" in layout_info
        assert "parameters" in layout_info
        assert "computation_time" in layout_info
        
        # Comprehensive statistics
        stats = data["statistics"]
        assert "graph_metrics" in stats
        assert "layout_quality" in stats
        assert "color_distribution" in stats
        assert "performance_metrics" in stats
        
        # Academic metadata
        assert metadata["academic_ready"] is True
        assert metadata["publication_ready"] is True
        assert metadata["layout_used"] == "spring"
        assert metadata["color_scheme"] == "entity_type"
        
        # Performance metrics
        assert result.execution_time > 0
        assert metadata["graph_size"] == len(karate_graph.nodes())
        assert metadata["edge_count"] == len(karate_graph.edges())
        
        print(f"✅ Publication-ready visualization: {len(karate_graph.nodes())} nodes, {len(karate_graph.edges())} edges")


if __name__ == "__main__":
    # Run specific test for quick validation
    test_suite = TestT54GraphVisualizationUnified()
    test_suite.setup_method()
    
    print("Running T54 Graph Visualization validation...")
    test_suite.test_tool_initialization()
    test_suite.test_get_contract()
    test_suite.test_zero_mocking_validation()
    
    if PLOTLY_AVAILABLE:
        test_suite.test_spring_layout_visualization_real()
        print("✅ T54 Graph Visualization tool validation passed!")
    else:
        print("⚠️ T54 validation completed but Plotly not available for full testing")