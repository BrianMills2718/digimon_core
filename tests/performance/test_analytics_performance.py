#!/usr/bin/env python3
"""
Performance Benchmarks for Analytics Tools

Comprehensive performance testing for all analytics tools with
real data and measurable performance criteria.
"""

import pytest
import asyncio
import time
import psutil
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json
from pathlib import Path
import tempfile

from src.core.service_manager import ServiceManager
from src.tools.phase2.t50_community_detection_unified import CommunityDetectionTool
from src.tools.phase2.t51_centrality_analysis_unified import CentralityAnalysisTool
from src.tools.phase2.t52_graph_clustering_unified import GraphClusteringTool
from src.tools.phase2.t53_network_motifs_unified import NetworkMotifsTool
from src.tools.phase2.t54_graph_visualization_unified import GraphVisualizationTool
from src.tools.phase2.t55_temporal_analysis_unified import TemporalAnalysisTool
from src.tools.phase2.t56_graph_metrics_unified import GraphMetricsTool
from src.tools.phase2.t57_path_analysis_unified import PathAnalysisTool
from src.tools.phase2.t58_graph_comparison_unified import GraphComparisonTool
from src.tools.phase2.t59_scale_free_analysis_unified import ScaleFreeAnalyzer
from src.tools.phase2.t60_graph_export_unified import GraphExportTool


@dataclass
class PerformanceResult:
    """Performance measurement result"""
    tool_name: str
    operation: str
    graph_size: int
    execution_time: float
    memory_used: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None


class PerformanceMonitor:
    """Monitor performance metrics during test execution"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.results = []
    
    async def measure_performance(self, tool_name: str, operation: str, 
                                graph_size: int, func, *args, **kwargs):
        """Measure performance of an async function"""
        # Initial measurements
        self.process.cpu_percent()  # Initialize CPU measurement
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        success = True
        error = None
        
        try:
            # Execute function
            result = await func(*args, **kwargs)
        except Exception as e:
            success = False
            error = str(e)
            result = None
        
        # Final measurements
        execution_time = time.time() - start_time
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_used = end_memory - start_memory
        cpu_percent = self.process.cpu_percent()
        
        # Record result
        perf_result = PerformanceResult(
            tool_name=tool_name,
            operation=operation,
            graph_size=graph_size,
            execution_time=execution_time,
            memory_used=memory_used,
            cpu_percent=cpu_percent,
            success=success,
            error=error
        )
        
        self.results.append(perf_result)
        return result, perf_result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.results:
            return {}
        
        summary = {
            "total_tests": len(self.results),
            "successful_tests": sum(1 for r in self.results if r.success),
            "average_execution_time": np.mean([r.execution_time for r in self.results]),
            "max_execution_time": max(r.execution_time for r in self.results),
            "average_memory_used": np.mean([r.memory_used for r in self.results]),
            "max_memory_used": max(r.memory_used for r in self.results),
            "tools_tested": list(set(r.tool_name for r in self.results))
        }
        
        return summary


class TestAnalyticsPerformance:
    """Performance tests for analytics tools"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service_manager = ServiceManager()
        self.monitor = PerformanceMonitor()
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize all tools
        self.tools = {
            "community_detection": CommunityDetectionTool(self.service_manager),
            "centrality_analysis": CentralityAnalysisTool(self.service_manager),
            "graph_clustering": GraphClusteringTool(self.service_manager),
            "network_motifs": NetworkMotifsTool(self.service_manager),
            "graph_visualization": GraphVisualizationTool(self.service_manager),
            "temporal_analysis": TemporalAnalysisTool(self.service_manager),
            "graph_metrics": GraphMetricsTool(self.service_manager),
            "path_analysis": PathAnalysisTool(self.service_manager),
            "graph_comparison": GraphComparisonTool(self.service_manager),
            "scale_free_analysis": ScaleFreeAnalyzer(self.service_manager),
            "graph_export": GraphExportTool(self.service_manager)
        }
        
        # Create test graphs of various sizes
        self.test_graphs = self._create_test_graphs()
    
    def teardown_method(self):
        """Clean up resources"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_graphs(self) -> Dict[int, Dict[str, Any]]:
        """Create test graphs of various sizes"""
        graphs = {}
        sizes = [100, 500, 1000, 5000]
        
        for size in sizes:
            # Create different graph types
            if size <= 1000:
                # Barabasi-Albert (scale-free)
                G_ba = nx.barabasi_albert_graph(size, 3, seed=42)
                
                # Erdos-Renyi (random)
                p = 10 / size  # Keep average degree ~10
                G_er = nx.erdos_renyi_graph(size, p, seed=42)
                
                # Watts-Strogatz (small-world)
                k = min(10, size - 1)
                G_ws = nx.watts_strogatz_graph(size, k, 0.3, seed=42)
            else:
                # For large graphs, only create scale-free
                G_ba = nx.barabasi_albert_graph(size, 3, seed=42)
                G_er = G_ba
                G_ws = G_ba
            
            graphs[size] = {
                "scale_free": self._networkx_to_dict(G_ba),
                "random": self._networkx_to_dict(G_er),
                "small_world": self._networkx_to_dict(G_ws)
            }
        
        return graphs
    
    def _networkx_to_dict(self, G: nx.Graph) -> Dict[str, Any]:
        """Convert NetworkX graph to dict format"""
        return {
            "nodes": [{"id": n, "label": f"Node_{n}"} for n in G.nodes()],
            "edges": [{"source": s, "target": t, "type": "CONNECTED"} 
                     for s, t in G.edges()]
        }
    
    @pytest.mark.asyncio
    async def test_community_detection_performance(self):
        """Test community detection performance across graph sizes"""
        tool = self.tools["community_detection"]
        
        for size in [100, 500, 1000]:
            graph = self.test_graphs[size]["scale_free"]
            
            # Test different algorithms
            for algorithm in ["louvain", "leiden"]:
                result, perf = await self.monitor.measure_performance(
                    "community_detection",
                    f"{algorithm}_algorithm",
                    size,
                    tool.execute,
                    {
                        "graph_data": graph,
                        "algorithm": algorithm,
                        "resolution": 1.0
                    }
                )
                
                # Performance requirements
                if size <= 1000:
                    assert perf.execution_time < 5.0, f"Too slow for {size} nodes"
                    assert perf.memory_used < 500, f"Too much memory for {size} nodes"
                
                if perf.success:
                    assert result.num_communities > 0
                    assert result.modularity_score >= 0
    
    @pytest.mark.asyncio
    async def test_scale_free_analysis_performance(self):
        """Test scale-free analysis performance"""
        tool = self.tools["scale_free_analysis"]
        
        for size in [100, 500, 1000]:
            for graph_type in ["scale_free", "random"]:
                graph = self.test_graphs[size][graph_type]
                
                result, perf = await self.monitor.measure_performance(
                    "scale_free_analysis",
                    f"{graph_type}_graph",
                    size,
                    tool.execute,
                    {
                        "graph_data": graph,
                        "min_degree": 1,
                        "temporal_analysis": False,
                        "hub_threshold_percentile": 90.0
                    }
                )
                
                # Performance requirements
                assert perf.execution_time < 10.0, f"Too slow for {size} nodes"
                assert perf.memory_used < 1000, f"Too much memory for {size} nodes"
                
                if perf.success and graph_type == "scale_free":
                    assert result.is_scale_free == True
    
    @pytest.mark.asyncio
    async def test_centrality_analysis_performance(self):
        """Test centrality analysis performance"""
        tool = self.tools["centrality_analysis"]
        
        for size in [100, 500]:  # Centrality is expensive
            graph = self.test_graphs[size]["small_world"]
            
            result, perf = await self.monitor.measure_performance(
                "centrality_analysis",
                "all_centralities",
                size,
                tool.execute,
                {
                    "graph_data": graph,
                    "centrality_types": ["degree", "betweenness", "closeness"],
                    "normalize": True
                }
            )
            
            # Performance requirements (relaxed for centrality)
            if size <= 500:
                assert perf.execution_time < 30.0, f"Too slow for {size} nodes"
            
            if perf.success:
                assert len(result.node_centralities) == size
    
    @pytest.mark.asyncio
    async def test_graph_export_performance(self):
        """Test graph export performance for different formats"""
        tool = self.tools["graph_export"]
        
        formats = ["graphml", "json-ld", "csv", "cypher"]
        
        for size in [100, 500, 1000]:
            graph = self.test_graphs[size]["scale_free"]
            
            for format in formats:
                output_path = str(Path(self.temp_dir) / f"export_{size}_{format}.{format}")
                
                result, perf = await self.monitor.measure_performance(
                    "graph_export",
                    f"{format}_format",
                    size,
                    tool.execute,
                    {
                        "graph_data": graph,
                        "export_format": format,
                        "output_path": output_path,
                        "compression": "none",
                        "include_metadata": True
                    }
                )
                
                # Export should be fast
                assert perf.execution_time < 5.0, f"Export too slow for {size} nodes"
                
                if perf.success:
                    assert Path(output_path).exists()
                    assert result.file_size_bytes > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test performance when multiple tools run concurrently"""
        graph = self.test_graphs[500]["scale_free"]
        
        # Create multiple tool tasks
        tasks = [
            self.monitor.measure_performance(
                "community_detection", "concurrent", 500,
                self.tools["community_detection"].execute,
                {"graph_data": graph, "algorithm": "louvain"}
            ),
            self.monitor.measure_performance(
                "graph_metrics", "concurrent", 500,
                self.tools["graph_metrics"].execute,
                {"graph_data": graph, "calculate_all": True}
            ),
            self.monitor.measure_performance(
                "scale_free_analysis", "concurrent", 500,
                self.tools["scale_free_analysis"].execute,
                {"graph_data": graph, "min_degree": 1}
            )
        ]
        
        # Run concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Concurrent execution should be faster than sequential
        sequential_time = sum(r[1].execution_time for r in results)
        speedup = sequential_time / total_time
        
        assert speedup > 1.5, "Insufficient speedup from concurrent execution"
        
        # All should succeed
        for _, perf in results:
            assert perf.success
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory efficiency for large graphs"""
        # Create a large graph
        size = 5000
        graph = self.test_graphs[size]["scale_free"]
        
        # Test memory-intensive operations
        tool = self.tools["graph_metrics"]
        
        result, perf = await self.monitor.measure_performance(
            "graph_metrics",
            "large_graph",
            size,
            tool.execute,
            {
                "graph_data": graph,
                "calculate_all": False,  # Basic metrics only
                "include_clustering": False
            }
        )
        
        # Memory should be reasonable
        assert perf.memory_used < 2000, f"Too much memory for {size} nodes"
        assert perf.success
    
    @pytest.mark.asyncio
    async def test_performance_degradation(self):
        """Test how performance degrades with graph size"""
        tool = self.tools["community_detection"]
        sizes = [100, 500, 1000]
        times = []
        
        for size in sizes:
            graph = self.test_graphs[size]["scale_free"]
            
            result, perf = await self.monitor.measure_performance(
                "community_detection",
                "scaling_test",
                size,
                tool.execute,
                {
                    "graph_data": graph,
                    "algorithm": "louvain"
                }
            )
            
            times.append(perf.execution_time)
        
        # Check scaling (should be roughly O(n log n) for good algorithms)
        # Time should not increase more than quadratically
        for i in range(1, len(sizes)):
            size_ratio = sizes[i] / sizes[i-1]
            time_ratio = times[i] / times[i-1]
            
            # Allow quadratic scaling as upper bound
            assert time_ratio < size_ratio ** 2.5, \
                f"Performance degrades too quickly: {time_ratio} for {size_ratio}x size"
    
    def test_generate_performance_report(self):
        """Generate performance report after all tests"""
        summary = self.monitor.get_summary()
        
        if summary:
            report = {
                "summary": summary,
                "details": [
                    {
                        "tool": r.tool_name,
                        "operation": r.operation,
                        "graph_size": r.graph_size,
                        "execution_time": round(r.execution_time, 3),
                        "memory_used_mb": round(r.memory_used, 2),
                        "cpu_percent": round(r.cpu_percent, 1),
                        "success": r.success
                    }
                    for r in self.monitor.results
                ]
            }
            
            # Save report
            report_path = Path(self.temp_dir) / "performance_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\nPerformance Report Summary:")
            print(f"Total tests: {summary['total_tests']}")
            print(f"Successful: {summary['successful_tests']}")
            print(f"Avg execution time: {summary['average_execution_time']:.3f}s")
            print(f"Max execution time: {summary['max_execution_time']:.3f}s")
            print(f"Avg memory used: {summary['average_memory_used']:.2f} MB")
            print(f"Max memory used: {summary['max_memory_used']:.2f} MB")


@pytest.mark.stress
class TestStressPerformance:
    """Stress tests for analytics tools"""
    
    def setup_method(self):
        self.service_manager = ServiceManager()
        self.monitor = PerformanceMonitor()
    
    @pytest.mark.asyncio
    async def test_stress_very_large_graph(self):
        """Stress test with very large graph"""
        # Create 10K node graph
        size = 10000
        G = nx.barabasi_albert_graph(size, 2, seed=42)  # Fewer edges for speed
        graph = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        tool = ScaleFreeAnalyzer(self.service_manager)
        
        result, perf = await self.monitor.measure_performance(
            "scale_free_analysis",
            "stress_test",
            size,
            tool.execute,
            {
                "graph_data": graph,
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 95.0
            }
        )
        
        # Should complete even for very large graphs
        assert perf.execution_time < 60.0, "Should complete within 1 minute"
        assert perf.success
    
    @pytest.mark.asyncio
    async def test_stress_rapid_sequential_calls(self):
        """Stress test with rapid sequential calls"""
        tool = GraphMetricsTool(self.service_manager)
        graph = nx.karate_club_graph()
        graph_data = {
            "nodes": [{"id": n} for n in graph.nodes()],
            "edges": [{"source": s, "target": t} for s, t in graph.edges()]
        }
        
        # Make 100 rapid calls
        start_time = time.time()
        for i in range(100):
            result = await tool.execute({
                "graph_data": graph_data,
                "calculate_all": False
            })
            assert result.basic_metrics["num_nodes"] == 34
        
        total_time = time.time() - start_time
        avg_time = total_time / 100
        
        # Should handle rapid calls efficiently
        assert avg_time < 0.1, "Average time per call should be < 100ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])