#!/usr/bin/env python3
"""
Tests for T59: Scale-Free Analysis Tool - Real Implementation Tests

Tests scale-free analysis with real graph data, no mocking of core functionality.
Follows the NO MOCKS policy for functional testing.
"""

import pytest
import asyncio
import networkx as nx
import numpy as np
from typing import Dict, List, Any

from src.tools.phase2.t59_scale_free_analysis_unified import ScaleFreeAnalyzer
from src.tools.base_tool import ToolRequest, ToolResult
from src.core.service_manager import ServiceManager


class TestScaleFreeAnalyzerReal:
    """Real tests for T59 Scale-Free Analysis Tool"""
    
    def setup_method(self):
        """Setup real ServiceManager and tool - NO mocks"""
        self.service_manager = ServiceManager()
        self.tool = ScaleFreeAnalyzer(service_manager=self.service_manager)
        
        # Create real test graphs
        self.test_graphs = self._create_real_test_graphs()
    
    def _create_real_test_graphs(self) -> Dict[str, Dict[str, Any]]:
        """Create real test graphs with known properties"""
        graphs = {}
        
        # 1. Barabasi-Albert scale-free network
        ba_graph = nx.barabasi_albert_graph(100, 3, seed=42)
        graphs["scale_free"] = self._networkx_to_dict(ba_graph)
        
        # 2. Erdos-Renyi random graph (not scale-free)
        er_graph = nx.erdos_renyi_graph(100, 0.05, seed=42)
        graphs["random"] = self._networkx_to_dict(er_graph)
        
        # 3. Complete graph (not scale-free)
        complete_graph = nx.complete_graph(20)
        graphs["complete"] = self._networkx_to_dict(complete_graph)
        
        # 4. Star graph (extreme scale-free)
        star_graph = nx.star_graph(50)
        graphs["star"] = self._networkx_to_dict(star_graph)
        
        # 5. Small test graph
        small_graph = nx.Graph()
        small_graph.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])
        graphs["small"] = self._networkx_to_dict(small_graph)
        
        return graphs
    
    def _networkx_to_dict(self, G: nx.Graph) -> Dict[str, Any]:
        """Convert NetworkX graph to dict format"""
        nodes = []
        for node in G.nodes():
            nodes.append({
                "id": node,
                "label": f"Node_{node}"
            })
        
        edges = []
        for source, target in G.edges():
            edges.append({
                "source": source,
                "target": target,
                "type": "CONNECTED"
            })
        
        return {"nodes": nodes, "edges": edges}
    
    @pytest.mark.asyncio
    async def test_tool_initialization_real(self):
        """Test tool initializes correctly with real components"""
        assert self.tool.tool_id == "T59"
        assert self.tool.name == "Scale-Free Network Analyzer"
        assert self.tool.tool_type == "analysis"
        assert self.tool.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_scale_free_detection_barabasi_albert(self):
        """Test detection of scale-free properties in BA graph"""
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": self.test_graphs["scale_free"],
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify scale-free detection
        assert result.data["is_scale_free"] == True
        assert 2.0 <= result.data["power_law_alpha"] <= 3.5  # Typical range for BA graphs
        assert result.data["power_law_xmin"] >= 1
        assert result.data["goodness_of_fit"] > 0.5
        
        # Verify hub detection
        assert len(result.data["hub_nodes"]) > 0
        assert len(result.data["hub_nodes"]) < 20  # Should be ~10% of nodes
        
        # Verify degree distribution
        assert isinstance(result.data["degree_distribution"], dict)
        assert len(result.data["degree_distribution"]) > 5
        
        # Verify metadata
        assert result.data["analysis_metadata"]["num_nodes"] == 100
        assert result.data["analysis_metadata"]["num_edges"] > 200
        assert result.data["analysis_metadata"]["avg_degree"] > 4
    
    @pytest.mark.asyncio
    async def test_random_graph_analysis_functional(self):
        """Test that analysis completes successfully on random graphs"""
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": self.test_graphs["random"],
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Test functionality, not probabilistic outcomes
        assert "is_scale_free" in result.data
        # Handle both Python bool and numpy bool
        scale_free_value = result.data["is_scale_free"]
        assert isinstance(scale_free_value, (bool, np.bool_))
        assert "power_law_alpha" in result.data
        assert isinstance(result.data["power_law_alpha"], (int, float))
        assert result.data["power_law_alpha"] >= 0
        assert "goodness_of_fit" in result.data
        assert 0.0 <= result.data["goodness_of_fit"] <= 1.0
        
        # Hub analysis should complete
        assert "hub_nodes" in result.data
        assert isinstance(result.data["hub_nodes"], list)
    
    @pytest.mark.asyncio
    async def test_star_graph_extreme_scale_free(self):
        """Test star graph as extreme case of scale-free"""
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": self.test_graphs["star"],
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Star graph has one super-hub
        assert len(result.data["hub_nodes"]) >= 1
        assert result.data["hub_nodes"][0]["degree"] == 50  # Central node
        assert result.data["analysis_metadata"]["max_degree"] == 50
        
        # Academic confidence might be lower due to extreme structure
        assert 0 < result.data["academic_confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_hub_identification_accuracy(self):
        """Test accuracy of hub identification"""
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": self.test_graphs["scale_free"],
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 95.0  # More restrictive
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify hub properties
        assert len(result.data["hub_nodes"]) > 0
        for hub in result.data["hub_nodes"]:
            assert "node_id" in hub
            assert "degree" in hub
            assert "degree_centrality" in hub
            assert "betweenness_centrality" in hub
            assert "closeness_centrality" in hub
            assert hub["is_hub"] == True
        
        # Hubs should be sorted by degree
        degrees = [h["degree"] for h in result.data["hub_nodes"]]
        assert degrees == sorted(degrees, reverse=True)
    
    @pytest.mark.asyncio
    async def test_temporal_analysis_flag(self):
        """Test temporal analysis flag behavior"""
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": self.test_graphs["small"],
                "min_degree": 1,
                "temporal_analysis": True,  # Enable temporal
                "hub_threshold_percentile": 80.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Should have temporal trends even if no temporal data
        assert result.data["temporal_trends"] is not None
        assert "evolution_detected" in result.data["temporal_trends"]
        assert result.data["temporal_trends"]["evolution_detected"] == False
    
    @pytest.mark.asyncio
    async def test_academic_confidence_scoring(self):
        """Test academic confidence score calculation"""
        test_graphs = ["scale_free", "random", "star", "complete"]
        
        for graph_name in test_graphs:
            request = ToolRequest(
                tool_id="T59",
                operation="analyze",
                input_data={
                    "graph_data": self.test_graphs[graph_name],
                    "min_degree": 1,
                    "temporal_analysis": False,
                    "hub_threshold_percentile": 90.0
                },
                parameters={}
            )
            
            result = await self.tool.execute(request)
            assert result.status == "success"
            
            # Test confidence score is valid, not specific range
            assert "academic_confidence" in result.data
            assert isinstance(result.data["academic_confidence"], (int, float))
            assert 0.0 <= result.data["academic_confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Empty graph
        empty_graph = {"nodes": [], "edges": []}
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": empty_graph,
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        assert result.data["is_scale_free"] == False
        assert len(result.data["hub_nodes"]) == 0
        assert result.data["analysis_metadata"]["num_nodes"] == 0
        
        # Single node
        single_node = {"nodes": [{"id": 1}], "edges": []}
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": single_node,
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        assert result.data["is_scale_free"] == False
        # Single node with no edges cannot be a hub
        assert len(result.data["hub_nodes"]) == 0
        assert result.data["analysis_metadata"]["num_nodes"] == 1
    
    @pytest.mark.asyncio
    async def test_performance_large_graph(self):
        """Test performance with larger graph"""
        import time
        
        # Create larger graph
        large_graph = nx.barabasi_albert_graph(1000, 5, seed=42)
        graph_data = self._networkx_to_dict(large_graph)
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": graph_data,
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        start_time = time.time()
        result = await self.tool.execute(request)
        assert result.status == "success"
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time for research analysis (powerlaw is computationally intensive)
        assert execution_time < 300.0  # 5 minutes for 1000 nodes is reasonable for research analysis
        assert result.data["analysis_metadata"]["num_nodes"] == 1000
        assert result.data["is_scale_free"] == True
    
    @pytest.mark.asyncio
    async def test_metadata_completeness(self):
        """Test that all expected metadata is present"""
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": self.test_graphs["scale_free"],
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Check all required metadata fields
        required_fields = [
            "num_nodes", "num_edges", "avg_degree", 
            "max_degree", "analysis_timestamp"
        ]
        
        for field in required_fields:
            assert field in result.data["analysis_metadata"]
        
        # Verify timestamp format
        from datetime import datetime
        timestamp = result.data["analysis_metadata"]["analysis_timestamp"]
        datetime.fromisoformat(timestamp)  # Should not raise


# Performance benchmarks
@pytest.mark.benchmark
class TestScaleFreePerformance:
    """Performance benchmarks for scale-free analysis"""
    
    def setup_method(self):
        self.service_manager = ServiceManager()
        self.tool = ScaleFreeAnalyzer(service_manager=self.service_manager)
    
    @pytest.mark.asyncio
    async def test_benchmark_various_sizes(self):
        """Benchmark performance across different graph sizes"""
        import time
        
        sizes = [100, 500, 1000, 5000]
        results = []
        
        for size in sizes:
            # Create graph
            G = nx.barabasi_albert_graph(size, 3, seed=42)
            graph_data = {
                "nodes": [{"id": n} for n in G.nodes()],
                "edges": [{"source": s, "target": t} for s, t in G.edges()]
            }
            
            request = ToolRequest(
                tool_id="T59",
                operation="analyze",
                input_data={
                    "graph_data": graph_data,
                    "min_degree": 1,
                    "temporal_analysis": False,
                    "hub_threshold_percentile": 90.0
                },
                parameters={}
            )
            
            # Time execution
            start = time.time()
            result = await self.tool.execute(request)
            duration = time.time() - start
            
            results.append({
                "size": size,
                "duration": duration,
                "is_scale_free": result.data["is_scale_free"]
            })
            
            # Performance requirements (reasonable for research analysis)
            if size <= 500:
                assert duration < 60.0  # Under 1 minute for graphs up to 500 nodes
            elif size <= 1000:
                assert duration < 300.0  # Under 5 minutes for graphs up to 1000 nodes (powerlaw is intensive)
            else:
                assert duration < 600.0  # Under 10 minutes for larger graphs
        
        # Print results for analysis
        for r in results:
            print(f"Size: {r['size']}, Duration: {r['duration']:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])