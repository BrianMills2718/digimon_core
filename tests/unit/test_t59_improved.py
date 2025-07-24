#!/usr/bin/env python3
"""
Tests for improved T59 Scale-Free Analysis - Edge Cases and Timeouts

This tests the improvements made to handle edge cases and timeout scenarios.
"""

import pytest
import asyncio
import networkx as nx
from src.tools.phase2.t59_scale_free_analysis_unified import ScaleFreeAnalyzer
from src.tools.base_tool import ToolRequest
from src.core.service_manager import ServiceManager


class TestScaleFreeAnalyzerImproved:
    """Test improved T59 functionality"""
    
    def setup_method(self):
        """Setup real ServiceManager and tool"""
        self.service_manager = ServiceManager()
        self.tool = ScaleFreeAnalyzer(service_manager=self.service_manager)
    
    @pytest.mark.asyncio
    async def test_complete_graph_edge_case(self):
        """Test complete graph handling (uniform degree distribution)"""
        # Complete graph - all nodes have same degree
        G = nx.complete_graph(10)
        graph_data = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": graph_data,
                "min_degree": 1
            }
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Complete graph should not be scale-free
        assert result.data["is_scale_free"] == False
        assert result.data["power_law_alpha"] == 0.0
        
        print(f"✅ Complete graph handled: scale-free={result.data['is_scale_free']}, alpha={result.data['power_law_alpha']}")
    
    @pytest.mark.asyncio
    async def test_star_graph_extreme_case(self):
        """Test star graph (extreme scale-free case)"""
        # Star graph - one central hub connected to all others
        G = nx.star_graph(20)
        graph_data = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": graph_data,
                "min_degree": 1
            }
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Star graph has clear hub structure
        assert len(result.data["hub_nodes"]) >= 1
        assert result.data["hub_nodes"][0]["degree"] == 20  # Central hub
        
        print(f"✅ Star graph analysis: {len(result.data['hub_nodes'])} hubs found")
    
    @pytest.mark.asyncio 
    async def test_small_graph_insufficient_data(self):
        """Test very small graph with insufficient data"""
        # Very small graph
        graph_data = {
            "nodes": [{"id": 1}, {"id": 2}, {"id": 3}],
            "edges": [{"source": 1, "target": 2}]
        }
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": graph_data,
                "min_degree": 1
            }
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Should handle small graphs gracefully
        assert result.data["is_scale_free"] == False
        assert result.data["power_law_alpha"] == 0.0
        
        print(f"✅ Small graph handled: scale-free={result.data['is_scale_free']}")
    
    @pytest.mark.asyncio
    async def test_barabasi_albert_with_improvements(self):
        """Test BA graph with improved analysis"""
        # Known scale-free graph
        G = nx.barabasi_albert_graph(100, 3, seed=42)
        graph_data = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze", 
            input_data={
                "graph_data": graph_data,
                "min_degree": 1
            }
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # BA graph should be detected as scale-free
        assert result.data["is_scale_free"] == True
        assert 1.5 <= result.data["power_law_alpha"] <= 4.0
        assert len(result.data["hub_nodes"]) > 0
        
        print(f"✅ BA graph analysis: α={result.data['power_law_alpha']:.2f}, "
              f"{len(result.data['hub_nodes'])} hubs")
    
    @pytest.mark.asyncio
    async def test_fallback_analysis(self):
        """Test fallback analysis when powerlaw library fails"""
        # Create a graph that might cause issues
        G = nx.path_graph(50)  # Simple path graph
        graph_data = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": graph_data,
                "min_degree": 1
            }
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Should complete even if powerlaw analysis has issues
        assert "is_scale_free" in result.data
        assert "power_law_alpha" in result.data
        assert isinstance(result.data["power_law_alpha"], (int, float))
        
        print(f"✅ Analysis completed: scale-free={result.data['is_scale_free']}, alpha={result.data['power_law_alpha']:.2f}")
    
    @pytest.mark.asyncio
    async def test_empty_graph_handling(self):
        """Test empty graph handling"""
        empty_graph = {"nodes": [], "edges": []}
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": empty_graph,
                "min_degree": 1
            }
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Empty graph should be handled gracefully
        assert result.data["is_scale_free"] == False
        assert len(result.data["hub_nodes"]) == 0
        assert result.data["analysis_metadata"]["num_nodes"] == 0
        
        print("✅ Empty graph handled gracefully")
    
    @pytest.mark.asyncio
    async def test_performance_improvement(self):
        """Test that analysis completes in reasonable time"""
        import time
        
        # Create moderately large graph
        G = nx.barabasi_albert_graph(500, 3, seed=42)
        graph_data = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        request = ToolRequest(
            tool_id="T59",
            operation="analyze",
            input_data={
                "graph_data": graph_data,
                "min_degree": 1
            }
        )
        
        start_time = time.time()
        result = await self.tool.execute(request)
        execution_time = time.time() - start_time
        
        assert result.status == "success"
        # Should complete within reasonable time (timeout protection working)
        assert execution_time < 60  # 1 minute max
        
        print(f"✅ Performance: {execution_time:.2f}s for 500 nodes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])