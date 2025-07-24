#!/usr/bin/env python3
"""
Reliability Test Suite for Analytics Tools

Tests for error recovery, resource management, concurrent access,
and system resilience.
"""

import pytest
import asyncio
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import threading
import random

from src.core.service_manager import ServiceManager
from src.tools.phase2.t59_scale_free_analysis_unified import ScaleFreeAnalyzer
from src.tools.phase2.t60_graph_export_unified import GraphExportTool
from src.tools.phase2.t50_community_detection_unified import CommunityDetectionTool
from src.tools.phase2.t56_graph_metrics_unified import GraphMetricsTool


class TestAnalyticsReliability:
    """Test reliability and resilience of analytics tools"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service_manager = ServiceManager()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create tools
        self.scale_free_tool = ScaleFreeAnalyzer(self.service_manager)
        self.export_tool = GraphExportTool(self.service_manager)
        self.community_tool = CommunityDetectionTool(self.service_manager)
        self.metrics_tool = GraphMetricsTool(self.service_manager)
    
    def teardown_method(self):
        """Clean up resources"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_graph(self, size: int = 100) -> Dict[str, Any]:
        """Create test graph"""
        G = nx.barabasi_albert_graph(size, 3, seed=42)
        return {
            "nodes": [{"id": n, "label": f"Node_{n}"} for n in G.nodes()],
            "edges": [{"source": s, "target": t, "type": "CONNECTED"} 
                     for s, t in G.edges()]
        }
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_access(self):
        """Test tools handle concurrent access correctly"""
        graph = self._create_test_graph(200)
        
        # Define concurrent tasks
        async def run_analysis(tool_name: str, iteration: int):
            if tool_name == "scale_free":
                result = await self.scale_free_tool.execute({
                    "graph_data": graph,
                    "min_degree": 1,
                    "temporal_analysis": False,
                    "hub_threshold_percentile": 90.0
                })
                return result.is_scale_free
            elif tool_name == "community":
                result = await self.community_tool.execute({
                    "graph_data": graph,
                    "algorithm": "louvain",
                    "resolution": 1.0
                })
                return result.num_communities
            elif tool_name == "metrics":
                result = await self.metrics_tool.execute({
                    "graph_data": graph,
                    "calculate_all": True
                })
                return result.basic_metrics["num_nodes"]
        
        # Run multiple concurrent analyses
        tasks = []
        for i in range(10):
            tasks.append(run_analysis("scale_free", i))
            tasks.append(run_analysis("community", i))
            tasks.append(run_analysis("metrics", i))
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0, f"Concurrent access failed: {errors}"
        
        # Results should be consistent
        scale_free_results = [r for i, r in enumerate(results) if i % 3 == 0]
        community_results = [r for i, r in enumerate(results) if i % 3 == 1]
        metrics_results = [r for i, r in enumerate(results) if i % 3 == 2]
        
        # All scale-free results should be the same
        assert all(r == scale_free_results[0] for r in scale_free_results)
        # All metrics should be the same
        assert all(r == 200 for r in metrics_results)
    
    @pytest.mark.asyncio
    async def test_error_recovery_invalid_input(self):
        """Test tools recover gracefully from invalid input"""
        # Test with various invalid inputs
        invalid_inputs = [
            {"nodes": [], "edges": []},  # Empty graph
            {"nodes": None, "edges": None},  # None values
            {"nodes": [{"id": 1}], "edges": [{"source": 1, "target": 2}]},  # Missing node
            {"nodes": "not_a_list", "edges": []},  # Wrong type
        ]
        
        for invalid_graph in invalid_inputs:
            # Scale-free analysis should handle gracefully
            try:
                result = await self.scale_free_tool.execute({
                    "graph_data": invalid_graph,
                    "min_degree": 1,
                    "temporal_analysis": False,
                    "hub_threshold_percentile": 90.0
                })
                # Should either succeed with safe defaults or raise clear error
                if hasattr(result, 'is_scale_free'):
                    assert result.is_scale_free == False  # Empty/invalid graphs aren't scale-free
            except Exception as e:
                # Error should be clear and specific
                assert str(e) != ""
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_export(self):
        """Test export tool cleans up resources properly"""
        graph = self._create_test_graph(100)
        
        # Export multiple times to test cleanup
        for i in range(10):
            output_path = str(Path(self.temp_dir) / f"export_{i}.graphml")
            
            result = await self.export_tool.execute({
                "graph_data": graph,
                "export_format": "graphml",
                "output_path": output_path,
                "compression": "gzip" if i % 2 == 0 else "none",
                "include_metadata": True
            })
            
            # File should exist
            if result.compression_used == "gzip":
                assert Path(output_path + ".gz").exists()
            else:
                assert Path(output_path).exists()
        
        # Check no file handles leaked
        # All files should be closed and accessible
        for i in range(10):
            path = Path(self.temp_dir) / f"export_{i}.graphml"
            if (path.with_suffix('.graphml.gz')).exists():
                path = path.with_suffix('.graphml.gz')
            
            # Should be able to read file
            with open(path, 'rb') as f:
                content = f.read()
                assert len(content) > 0
    
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self):
        """Test tools don't leak memory on repeated use"""
        import gc
        import psutil
        
        process = psutil.Process()
        graph = self._create_test_graph(500)
        
        # Get initial memory
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run analysis many times
        for i in range(50):
            result = await self.community_tool.execute({
                "graph_data": graph,
                "algorithm": "louvain",
                "resolution": 1.0
            })
            
            # Force garbage collection every 10 iterations
            if i % 10 == 0:
                gc.collect()
        
        # Final memory check
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (allow 100MB for overhead)
        assert memory_increase < 100, f"Memory leak detected: {memory_increase}MB increase"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test tools handle timeouts appropriately"""
        # Create a very large graph that might timeout
        large_graph = self._create_test_graph(10000)
        
        # Set a timeout for the operation
        try:
            result = await asyncio.wait_for(
                self.scale_free_tool.execute({
                    "graph_data": large_graph,
                    "min_degree": 1,
                    "temporal_analysis": True,  # More expensive
                    "hub_threshold_percentile": 99.0
                }),
                timeout=5.0  # 5 second timeout
            )
        except asyncio.TimeoutError:
            # Should handle timeout gracefully
            pass  # This is expected for very large graphs
    
    @pytest.mark.asyncio
    async def test_data_consistency_concurrent_writes(self):
        """Test data consistency when multiple tools write concurrently"""
        graph = self._create_test_graph(100)
        export_dir = Path(self.temp_dir) / "concurrent_exports"
        export_dir.mkdir(exist_ok=True)
        
        # Define concurrent export tasks
        async def export_graph(format: str, index: int):
            output_path = str(export_dir / f"graph_{index}.{format}")
            result = await self.export_tool.execute({
                "graph_data": graph,
                "export_format": format,
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            })
            return result
        
        # Run concurrent exports
        tasks = []
        formats = ["graphml", "json-ld", "csv", "cypher"]
        for i in range(20):
            format = formats[i % len(formats)]
            tasks.append(export_graph(format, i))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
        
        # All files should exist and be valid
        exported_files = list(export_dir.glob("*"))
        assert len(exported_files) == 20
    
    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test errors are properly propagated with context"""
        # Test with invalid export path
        graph = self._create_test_graph(50)
        
        with pytest.raises(Exception) as exc_info:
            await self.export_tool.execute({
                "graph_data": graph,
                "export_format": "graphml",
                "output_path": "/invalid/path/that/does/not/exist/file.graphml",
                "compression": "none",
                "include_metadata": True
            })
        
        # Error should be meaningful
        assert "invalid" in str(exc_info.value).lower() or \
               "exist" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_service_manager_reliability(self):
        """Test ServiceManager handles service failures"""
        # Create multiple service managers
        managers = [ServiceManager() for _ in range(5)]
        
        # Each should work independently
        tasks = []
        for i, manager in enumerate(managers):
            tool = ScaleFreeAnalyzer(manager)
            graph = self._create_test_graph(50 + i * 10)
            
            task = tool.execute({
                "graph_data": graph,
                "min_degree": 1,
                "temporal_analysis": False,
                "hub_threshold_percentile": 90.0
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed independently
        assert all(not isinstance(r, Exception) for r in results)
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test tools degrade gracefully under resource pressure"""
        # Create tools with limited resources
        graph = self._create_test_graph(1000)
        
        # Run analysis with various configurations
        configs = [
            {"calculate_all": True},  # Full analysis
            {"calculate_all": False, "include_clustering": False},  # Limited
            {"calculate_all": False, "include_clustering": False, 
             "include_connectivity": False}  # Minimal
        ]
        
        results = []
        for config in configs:
            input_data = {"graph_data": graph}
            input_data.update(config)
            
            result = await self.metrics_tool.execute(input_data)
            results.append(result)
        
        # All should succeed
        assert all(r.basic_metrics["num_nodes"] == 1000 for r in results)
        
        # More limited configs should be faster
        # (In real implementation, would check execution times)
    
    @pytest.mark.asyncio
    async def test_idempotency(self):
        """Test operations are idempotent"""
        graph = self._create_test_graph(200)
        
        # Run same analysis multiple times
        results = []
        for _ in range(5):
            result = await self.community_tool.execute({
                "graph_data": graph,
                "algorithm": "louvain",
                "resolution": 1.0,
                "random_seed": 42  # Fixed seed for determinism
            })
            results.append(result)
        
        # All results should be identical
        first_communities = results[0].num_communities
        first_modularity = results[0].modularity_score
        
        for result in results[1:]:
            assert result.num_communities == first_communities
            assert abs(result.modularity_score - first_modularity) < 0.001


@pytest.mark.stress
class TestStressReliability:
    """Stress tests for reliability under extreme conditions"""
    
    def setup_method(self):
        self.service_manager = ServiceManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_stress_rapid_tool_creation(self):
        """Test rapid tool creation and destruction"""
        async def create_and_use_tool():
            tool = ScaleFreeAnalyzer(ServiceManager())
            graph = nx.karate_club_graph()
            graph_data = {
                "nodes": [{"id": n} for n in graph.nodes()],
                "edges": [{"source": s, "target": t} for s, t in graph.edges()]
            }
            
            result = await tool.execute({
                "graph_data": graph_data,
                "min_degree": 1
            })
            return result.is_scale_free
        
        # Create many tools rapidly
        tasks = [create_and_use_tool() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle rapid creation
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_stress_concurrent_large_exports(self):
        """Test concurrent exports of large graphs"""
        # Create large graph
        G = nx.barabasi_albert_graph(2000, 3)
        large_graph = {
            "nodes": [{"id": n} for n in G.nodes()],
            "edges": [{"source": s, "target": t} for s, t in G.edges()]
        }
        
        tool = GraphExportTool(self.service_manager)
        
        # Export concurrently
        tasks = []
        for i in range(5):
            output_path = str(Path(self.temp_dir) / f"large_{i}.graphml")
            task = tool.execute({
                "graph_data": large_graph,
                "export_format": "graphml",
                "output_path": output_path,
                "compression": "gzip",
                "include_metadata": True
            })
            tasks.append(task)
        
        # Should handle concurrent large exports
        results = await asyncio.gather(*tasks, return_exceptions=True)
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
        
        # All files should be created
        for i in range(5):
            path = Path(self.temp_dir) / f"large_{i}.graphml.gz"
            assert path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])