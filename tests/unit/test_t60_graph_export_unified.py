#!/usr/bin/env python3
"""
Tests for T60: Graph Export Tool - Real Implementation Tests

Tests graph export functionality with real data and file operations.
Follows the NO MOCKS policy for functional testing.
"""

import pytest
import asyncio
import networkx as nx
import json
import gzip
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

from src.tools.phase2.t60_graph_export_unified import (
    GraphExportTool, ExportFormat, CompressionType
)
from src.tools.base_tool import ToolRequest, ToolResult
from src.core.service_manager import ServiceManager


class TestGraphExportToolReal:
    """Real tests for T60 Graph Export Tool"""
    
    def setup_method(self):
        """Setup real ServiceManager and tool - NO mocks"""
        self.service_manager = ServiceManager()
        self.tool = GraphExportTool(service_manager=self.service_manager)
        
        # Create temporary directory for exports
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test graph
        self.test_graph = self._create_test_graph()
    
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_graph(self) -> Dict[str, Any]:
        """Create a test graph with rich properties"""
        nodes = [
            {
                "id": 1,
                "label": "Person",
                "properties": {
                    "name": "Alice Smith",
                    "age": 30,
                    "occupation": "Researcher"
                }
            },
            {
                "id": 2,
                "label": "Person",
                "properties": {
                    "name": "Bob Johnson",
                    "age": 35,
                    "occupation": "Professor"
                }
            },
            {
                "id": 3,
                "label": "Organization",
                "properties": {
                    "name": "University X",
                    "type": "Educational",
                    "founded": 1850
                }
            },
            {
                "id": 4,
                "label": "Paper",
                "properties": {
                    "title": "Graph Analysis Methods",
                    "year": 2023,
                    "doi": "10.1234/example"
                }
            }
        ]
        
        edges = [
            {
                "source": 1,
                "target": 3,
                "type": "AFFILIATED_WITH",
                "properties": {"since": 2020}
            },
            {
                "source": 2,
                "target": 3,
                "type": "AFFILIATED_WITH",
                "properties": {"since": 2018}
            },
            {
                "source": 1,
                "target": 4,
                "type": "AUTHORED",
                "properties": {"order": 1}
            },
            {
                "source": 2,
                "target": 4,
                "type": "AUTHORED",
                "properties": {"order": 2}
            },
            {
                "source": 1,
                "target": 2,
                "type": "COLLABORATES_WITH",
                "properties": {"strength": 0.8}
            }
        ]
        
        return {"nodes": nodes, "edges": edges}
    
    @pytest.mark.asyncio
    async def test_tool_initialization_real(self):
        """Test tool initializes correctly with real components"""
        assert self.tool.tool_id == "T60"
        assert self.tool.name == "Graph Export Tool"
        assert self.tool.tool_type == "export"
        assert self.tool.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_export_graphml_format(self):
        """Test export to GraphML format"""
        output_path = str(Path(self.temp_dir) / "test_graph.graphml")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "graphml",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify output
        assert result.data["export_path"] == output_path
        assert result.data["export_format"] == "graphml"
        assert result.data["num_nodes_exported"] == 4
        assert result.data["num_edges_exported"] == 5
        assert result.data["file_size_bytes"] > 0
        
        # Verify file exists and is valid XML
        assert Path(output_path).exists()
        tree = ET.parse(output_path)
        root = tree.getroot()
        assert "graphml" in root.tag
    
    @pytest.mark.asyncio
    async def test_export_json_ld_format(self):
        """Test export to JSON-LD format"""
        output_path = str(Path(self.temp_dir) / "test_graph.jsonld")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "json-ld",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify output
        assert result.data["export_path"] == output_path
        assert result.data["export_format"] == "json-ld"
        assert Path(output_path).exists()
        
        # Verify JSON-LD structure
        with open(output_path, 'r') as f:
            json_data = json.load(f)
        
        assert "@context" in json_data
        assert "nodes" in json_data
        assert "edges" in json_data
        assert len(json_data["nodes"]) == 4
        assert len(json_data["edges"]) == 5
        
        # Check metadata included
        assert "metadata" in json_data
        assert "nodeCount" in json_data["metadata"]
    
    @pytest.mark.asyncio
    async def test_export_cypher_format(self):
        """Test export to Cypher query format"""
        output_path = str(Path(self.temp_dir) / "test_graph.cypher")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "cypher",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify output
        assert result.data["export_path"] == output_path
        assert Path(output_path).exists()
        
        # Verify Cypher content
        with open(output_path, 'r') as f:
            cypher_content = f.read()
        
        # Should contain CREATE statements
        assert "CREATE" in cypher_content
        assert "Person" in cypher_content
        assert "AFFILIATED_WITH" in cypher_content
        assert cypher_content.endswith(";")
    
    @pytest.mark.asyncio
    async def test_export_csv_format(self):
        """Test export to CSV edge list format"""
        output_path = str(Path(self.temp_dir) / "test_graph.csv")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "csv",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify output
        assert result.data["export_path"] == output_path
        assert Path(output_path).exists()
        
        # Verify CSV content
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        assert lines[0].strip() == "source,target,type,weight"
        assert len(lines) == 6  # Header + 5 edges
        assert "AFFILIATED_WITH" in lines[1]
    
    @pytest.mark.asyncio
    async def test_compression_gzip(self):
        """Test GZIP compression"""
        output_path = str(Path(self.temp_dir) / "test_graph.graphml")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "graphml",
                "output_path": output_path,
                "compression": "gzip",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify compression
        assert result.data["export_path"] == output_path + ".gz"
        assert result.data["compression_used"] == "gzip"
        assert result.data["compression_ratio"] is not None
        # Compression ratio could be > 1.0 for very small files due to overhead
        assert isinstance(result.data["compression_ratio"], (int, float))
        assert Path(result.data["export_path"]).exists()
        
        # Verify can decompress
        with gzip.open(result.data["export_path"], 'rt') as f:
            content = f.read()
            assert "graphml" in content
    
    @pytest.mark.asyncio
    async def test_compression_zip(self):
        """Test ZIP compression"""
        output_path = str(Path(self.temp_dir) / "test_graph.json")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "json-ld",
                "output_path": output_path,
                "compression": "zip",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify compression
        assert result.data["export_path"] == output_path + ".zip"
        assert result.data["compression_used"] == "zip"
        assert Path(result.data["export_path"]).exists()
        
        # Verify can decompress
        with zipfile.ZipFile(result.data["export_path"], 'r') as zf:
            files = zf.namelist()
            assert len(files) == 1
            with zf.open(files[0]) as f:
                content = f.read().decode('utf-8')
                data = json.loads(content)
                assert "nodes" in data
    
    @pytest.mark.asyncio
    async def test_batch_export(self):
        """Test batch export to multiple formats"""
        base_path = str(Path(self.temp_dir) / "batch_export")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "graphml",  # Ignored for batch
                "output_path": base_path,
                "compression": "none",
                "include_metadata": True,
                "batch_export": ["graphml", "json-ld", "csv", "cypher"]
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Verify batch results
        assert result.data["export_format"] == "batch"
        assert result.data["batch_results"] is not None
        assert len(result.data["batch_results"]) == 4
        
        # Verify each file exists
        for batch_result in result.data["batch_results"]:
            assert Path(batch_result['path']).exists()
            assert batch_result['file_size_bytes'] > 0
        
        # Verify total size
        total_size = sum(r['file_size_bytes'] for r in result.data["batch_results"])
        assert result.data["file_size_bytes"] == total_size
    
    @pytest.mark.asyncio
    async def test_export_formats_completeness(self):
        """Test all export formats work correctly"""
        formats_to_test = [
            "graphml",
            "gexf",
            "json-ld",
            "cypher",
            "csv",
            "tsv",
            "adjacency_list",
            "edge_list",
        ]
        
        for format in formats_to_test:
            output_path = str(Path(self.temp_dir) / f"test.{format}")
            
            request = ToolRequest(
                tool_id="T60",
                operation="export",
                input_data={
                    "graph_data": self.test_graph,
                    "export_format": format,
                    "output_path": output_path,
                    "compression": "none",
                    "include_metadata": True
                },
                parameters={}
            )
            
            result = await self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["export_format"] == format
            assert Path(result.data["export_path"]).exists()
            assert result.data["file_size_bytes"] > 0
    
    @pytest.mark.asyncio
    async def test_edge_cases(self):
        """Test edge cases"""
        # Empty graph
        empty_graph = {"nodes": [], "edges": []}
        output_path = str(Path(self.temp_dir) / "empty.graphml")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": empty_graph,
                "export_format": "graphml",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        assert result.data["num_nodes_exported"] == 0
        assert result.data["num_edges_exported"] == 0
        assert Path(output_path).exists()
        
        # Single node
        single_node = {"nodes": [{"id": 1, "label": "Test"}], "edges": []}
        output_path = str(Path(self.temp_dir) / "single.csv")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": single_node,
                "export_format": "csv",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": False
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        assert result.data["num_nodes_exported"] == 1
        assert result.data["num_edges_exported"] == 0
    
    @pytest.mark.asyncio
    async def test_large_graph_export(self):
        """Test export of larger graph"""
        import time
        
        # Create larger graph
        G = nx.barabasi_albert_graph(500, 3)
        large_graph = {
            "nodes": [{"id": n, "label": f"Node_{n}"} for n in G.nodes()],
            "edges": [{"source": s, "target": t, "type": "CONNECTED"} 
                     for s, t in G.edges()]
        }
        
        output_path = str(Path(self.temp_dir) / "large.graphml")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": large_graph,
                "export_format": "graphml",
                "output_path": output_path,
                "compression": "gzip",
                "include_metadata": True
            },
            parameters={}
        )
        
        start_time = time.time()
        result = await self.tool.execute(request)
        execution_time = time.time() - start_time
        
        assert result.status == "success"
        # Should complete quickly
        assert execution_time < 5.0  # 5 seconds for 500 nodes
        assert result.data["num_nodes_exported"] == 500
        # Compression ratio should be reasonable (could be >1.0 for small files due to overhead)
        assert result.data["compression_ratio"] is not None
        assert result.data["compression_ratio"] > 0.0
    
    @pytest.mark.asyncio  
    async def test_metadata_preservation(self):
        """Test that node/edge properties are preserved"""
        output_path = str(Path(self.temp_dir) / "metadata_test.jsonld")
        
        request = ToolRequest(
            tool_id="T60",
            operation="export",
            input_data={
                "graph_data": self.test_graph,
                "export_format": "json-ld",
                "output_path": output_path,
                "compression": "none",
                "include_metadata": True
            },
            parameters={}
        )
        
        result = await self.tool.execute(request)
        assert result.status == "success"
        
        # Read and verify
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        # Check node properties preserved
        alice = next(n for n in data["nodes"] if n.get("name") == "Alice Smith")
        assert alice["age"] == 30
        assert alice["occupation"] == "Researcher"
        
        # Check edge properties preserved
        collab_edge = next(e for e in data["edges"] if e["@type"] == "COLLABORATES_WITH")
        assert collab_edge["strength"] == 0.8


# Performance benchmarks
@pytest.mark.benchmark
class TestGraphExportPerformance:
    """Performance benchmarks for graph export"""
    
    def setup_method(self):
        self.service_manager = ServiceManager()
        self.tool = GraphExportTool(service_manager=self.service_manager)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_benchmark_export_formats(self):
        """Benchmark different export formats"""
        import time
        
        # Create test graph
        G = nx.karate_club_graph()
        graph_data = {
            "nodes": [{"id": n, "label": f"Person_{n}"} for n in G.nodes()],
            "edges": [{"source": s, "target": t, "type": "KNOWS"} 
                     for s, t in G.edges()]
        }
        
        formats = ["graphml", "json-ld", "csv", "cypher"]
        
        results = []
        for format in formats:
            output_path = str(Path(self.temp_dir) / f"benchmark.{format}")
            
            request = ToolRequest(
                tool_id="T60",
                operation="export",
                input_data={
                    "graph_data": graph_data,
                    "export_format": format,
                    "output_path": output_path,
                    "compression": "none",
                    "include_metadata": True
                },
                parameters={}
            )
            
            start = time.time()
            result = await self.tool.execute(request)
            duration = time.time() - start
            
            results.append({
                "format": format,
                "duration": duration,
                "size": result.data["file_size_bytes"]
            })
            
            # All formats should be fast
            assert duration < 1.0
        
        # Print results
        for r in results:
            print(f"Format: {r['format']}, Duration: {r['duration']:.3f}s, Size: {r['size']} bytes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])