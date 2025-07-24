#!/usr/bin/env python3
"""
Test Graph Export Tool

Comprehensive tests for GraphExportTool including multiple export formats,
compression, batch export, and subgraph export capabilities.
"""

import pytest
import asyncio
import json
import xml.etree.ElementTree as ET
import networkx as nx
import tempfile
import gzip
import zipfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.analytics.graph_export_tool import GraphExportTool, GraphExportError


class TestGraphExportTool:
    """Test suite for GraphExportTool"""
    
    @pytest.fixture
    def mock_neo4j_manager(self):
        """Create mock Neo4j manager"""
        manager = Mock()
        manager.execute_read_query = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_dtm(self):
        """Create mock distributed transaction manager"""
        dtm = Mock()
        dtm.begin_distributed_transaction = AsyncMock()
        dtm.record_operation = AsyncMock()
        dtm.commit_distributed_transaction = AsyncMock()
        dtm.rollback_distributed_transaction = AsyncMock()
        dtm.current_tx_id = "test_tx_123"
        return dtm
    
    @pytest.fixture
    def export_tool(self, mock_neo4j_manager, mock_dtm):
        """Create GraphExportTool instance"""
        return GraphExportTool(mock_neo4j_manager, mock_dtm)
    
    @pytest.fixture
    def sample_graph_data(self):
        """Create sample graph data"""
        nodes = [
            {
                'node_id': 1,
                'labels': ['Person', 'Author'],
                'properties': {
                    'name': 'Alice Smith',
                    'h_index': 25,
                    'created_date': '2023-01-01'
                }
            },
            {
                'node_id': 2,
                'labels': ['Person', 'Author'],
                'properties': {
                    'name': 'Bob Johnson',
                    'h_index': 15,
                    'created_date': '2023-02-01'
                }
            },
            {
                'node_id': 3,
                'labels': ['Paper'],
                'properties': {
                    'title': 'Graph Analysis Methods',
                    'year': 2023,
                    'doi': '10.1234/example'
                }
            }
        ]
        
        edges = [
            {
                'source': 1,
                'target': 3,
                'type': 'AUTHORED',
                'properties': {'order': 1}
            },
            {
                'source': 2,
                'target': 3,
                'type': 'AUTHORED',
                'properties': {'order': 2}
            },
            {
                'source': 1,
                'target': 2,
                'type': 'COLLABORATES_WITH',
                'properties': {'strength': 0.8}
            }
        ]
        
        return nodes, edges
    
    @pytest.fixture
    def temp_output_path(self):
        """Create temporary output path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        Path(f"{temp_path}.gz").unlink(missing_ok=True)
        Path(f"{temp_path}.zip").unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_graphml_basic(self, export_tool, mock_neo4j_manager, 
                                       sample_graph_data, temp_output_path):
        """Test basic GraphML export"""
        nodes, edges = sample_graph_data
        
        # Mock Neo4j response
        mock_response = []
        for node in nodes:
            node_edges = [e for e in edges if e['source'] == node['node_id']]
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': node_edges
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Export graph
        result = await export_tool.export_graph(
            output_path=temp_output_path,
            format='graphml'
        )
        
        # Verify results
        assert result['status'] == 'success'
        assert result['format'] == 'graphml'
        assert Path(temp_output_path).exists()
        assert result['statistics']['node_count'] == 3
        assert result['statistics']['edge_count'] == 3
        
        # Verify GraphML content
        tree = ET.parse(temp_output_path)
        root = tree.getroot()
        assert root.tag.endswith('graphml')
    
    @pytest.mark.asyncio
    async def test_export_json_ld(self, export_tool, mock_neo4j_manager,
                                 sample_graph_data, temp_output_path):
        """Test JSON-LD export"""
        nodes, edges = sample_graph_data
        
        # Change extension for JSON-LD
        json_path = temp_output_path.replace('.graphml', '.jsonld')
        
        # Mock response
        mock_response = []
        for node in nodes:
            node_edges = [e for e in edges if e['source'] == node['node_id']]
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': node_edges
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Export
        result = await export_tool.export_graph(
            output_path=json_path,
            format='json-ld'
        )
        
        assert result['status'] == 'success'
        assert Path(json_path).exists()
        
        # Verify JSON-LD content
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        assert '@context' in json_data
        assert 'nodes' in json_data
        assert 'edges' in json_data
        assert len(json_data['nodes']) == 3
        assert len(json_data['edges']) == 3
        
        # Cleanup
        Path(json_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_cytoscape(self, export_tool, mock_neo4j_manager,
                                   sample_graph_data, temp_output_path):
        """Test Cytoscape JSON export"""
        nodes, edges = sample_graph_data
        
        # Change extension
        cyjs_path = temp_output_path.replace('.graphml', '.cyjs')
        
        # Mock response
        mock_response = []
        for node in nodes:
            node_edges = [e for e in edges if e['source'] == node['node_id']]
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': node_edges
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Export
        result = await export_tool.export_graph(
            output_path=cyjs_path,
            format='cytoscape'
        )
        
        assert result['status'] == 'success'
        assert Path(cyjs_path).exists()
        
        # Verify Cytoscape format
        with open(cyjs_path, 'r') as f:
            cytoscape_data = json.load(f)
        
        assert 'elements' in cytoscape_data
        assert 'nodes' in cytoscape_data['elements']
        assert 'edges' in cytoscape_data['elements']
        assert len(cytoscape_data['elements']['nodes']) == 3
        
        # Cleanup
        Path(cyjs_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_with_compression(self, export_tool, mock_neo4j_manager,
                                         sample_graph_data, temp_output_path):
        """Test export with compression"""
        nodes, edges = sample_graph_data
        
        # Mock response
        mock_response = []
        for node in nodes:
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': []
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Export with compression
        result = await export_tool.export_graph(
            output_path=temp_output_path,
            format='graphml',
            compress=True
        )
        
        assert result['status'] == 'success'
        assert result['output_path'].endswith('.gz')
        assert Path(result['output_path']).exists()
        assert result['statistics'].get('compressed', False)
        
        # Verify compressed content
        with gzip.open(result['output_path'], 'rt') as f:
            content = f.read()
            assert '<graphml' in content
    
    @pytest.mark.asyncio
    async def test_export_with_sampling(self, export_tool, mock_neo4j_manager,
                                      sample_graph_data, temp_output_path):
        """Test export with sampling"""
        nodes, edges = sample_graph_data
        
        # Mock will be called with sampling clause
        mock_neo4j_manager.execute_read_query.return_value = [
            {
                'node_id': nodes[0]['node_id'],
                'labels': nodes[0]['labels'],
                'properties': nodes[0]['properties'],
                'relationships': []
            }
        ]
        
        # Export with sampling
        result = await export_tool.export_graph(
            output_path=temp_output_path,
            format='graphml',
            sampling_ratio=0.5
        )
        
        assert result['status'] == 'success'
        # Check that sampling was applied in query
        query_call = mock_neo4j_manager.execute_read_query.call_args[0][0]
        assert 'rand() < 0.5' in query_call
    
    @pytest.mark.asyncio
    async def test_export_no_data(self, export_tool, mock_neo4j_manager, temp_output_path):
        """Test export with no data"""
        mock_neo4j_manager.execute_read_query.return_value = []
        
        result = await export_tool.export_graph(
            output_path=temp_output_path,
            format='graphml'
        )
        
        assert result['status'] == 'no_data'
        assert result['message'] == 'No nodes found for export'
    
    @pytest.mark.asyncio
    async def test_unsupported_format(self, export_tool, temp_output_path):
        """Test export with unsupported format"""
        with pytest.raises(GraphExportError) as excinfo:
            await export_tool.export_graph(
                output_path=temp_output_path,
                format='invalid_format'
            )
        
        assert 'Unsupported format' in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_batch_export(self, export_tool, mock_neo4j_manager, sample_graph_data):
        """Test batch export to multiple formats"""
        nodes, edges = sample_graph_data
        
        # Mock response
        mock_response = []
        for node in nodes:
            node_edges = [e for e in edges if e['source'] == node['node_id']]
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': node_edges
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Batch export
            result = await export_tool.batch_export(
                output_dir=temp_dir,
                formats=['graphml', 'json-ld', 'cytoscape']
            )
            
            assert result['status'] == 'batch_complete'
            assert result['formats_exported'] == 3
            assert 'graphml' in result['results']
            assert 'json-ld' in result['results']
            assert 'cytoscape' in result['results']
            
            # Verify files were created
            output_files = list(Path(temp_dir).glob('*'))
            assert len(output_files) >= 3
    
    @pytest.mark.asyncio
    async def test_export_subgraph(self, export_tool, mock_neo4j_manager, temp_output_path):
        """Test subgraph export"""
        # Mock subgraph query response
        mock_response = [
            {
                'node_id': 1,
                'labels': ['Person'],
                'properties': {'name': 'Center Node'},
                'relationships': [
                    {
                        'source': 1,
                        'target': 2,
                        'type': 'CONNECTED_TO',
                        'properties': {}
                    }
                ]
            },
            {
                'node_id': 2,
                'labels': ['Person'],
                'properties': {'name': 'Connected Node'},
                'relationships': []
            }
        ]
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Export subgraph
        result = await export_tool.export_subgraph(
            center_node_id=1,
            depth=2,
            output_path=temp_output_path,
            format='graphml'
        )
        
        assert result['status'] == 'success'
        assert result['center_node'] == 1
        assert result['depth'] == 2
        assert Path(temp_output_path).exists()
    
    @pytest.mark.asyncio
    async def test_export_error_handling(self, export_tool, mock_neo4j_manager,
                                       mock_dtm, temp_output_path):
        """Test error handling during export"""
        # Simulate database error
        mock_neo4j_manager.execute_read_query.side_effect = Exception("Database error")
        
        with pytest.raises(GraphExportError) as excinfo:
            await export_tool.export_graph(
                output_path=temp_output_path,
                format='graphml'
            )
        
        assert "Database error" in str(excinfo.value)
        mock_dtm.rollback_distributed_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_export_formats(self, export_tool, mock_neo4j_manager, sample_graph_data):
        """Test various export formats"""
        nodes, edges = sample_graph_data
        
        # Mock response
        mock_response = []
        for node in nodes:
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': []
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        formats_to_test = ['gml', 'pajek', 'edgelist', 'adjacency']
        
        for format in formats_to_test:
            with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as f:
                temp_path = f.name
            
            try:
                result = await export_tool.export_graph(
                    output_path=temp_path,
                    format=format
                )
                
                assert result['status'] == 'success'
                assert Path(temp_path).exists()
                assert result['statistics']['format'] == format
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_metadata_handling(self, export_tool, mock_neo4j_manager,
                                   sample_graph_data, temp_output_path):
        """Test export with and without metadata"""
        nodes, edges = sample_graph_data
        
        # Mock response
        mock_response = []
        for node in nodes:
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'properties': node['properties'],
                'relationships': []
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Export without metadata
        result = await export_tool.export_graph(
            output_path=temp_output_path,
            format='graphml',
            include_metadata=False
        )
        
        assert result['status'] == 'success'
        assert not result['statistics']['metadata_included']
        
        # Export with metadata
        result = await export_tool.export_graph(
            output_path=temp_output_path.replace('.graphml', '_meta.graphml'),
            format='graphml',
            include_metadata=True
        )
        
        assert result['status'] == 'success'
        assert result['statistics']['metadata_included']
    
    @pytest.mark.asyncio
    async def test_large_graph_compression(self, export_tool, mock_neo4j_manager):
        """Test automatic compression for large graphs"""
        # Create large mock data
        large_nodes = []
        for i in range(1000):
            large_nodes.append({
                'node_id': i,
                'labels': ['Entity'],
                'properties': {'data': 'x' * 1000},  # Large properties
                'relationships': []
            })
        
        mock_neo4j_manager.execute_read_query.return_value = large_nodes
        
        with tempfile.NamedTemporaryFile(suffix='.graphml', delete=False) as f:
            temp_path = f.name
        
        try:
            # Lower compression threshold for testing
            export_tool.compression_threshold = 1024  # 1KB
            
            result = await export_tool.export_graph(
                output_path=temp_path,
                format='graphml',
                compress=False  # Should auto-compress due to size
            )
            
            # File should be compressed automatically
            assert result['output_path'].endswith('.gz')
            assert result['statistics'].get('compressed', False)
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(f"{temp_path}.gz").unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_file_extensions(self, export_tool):
        """Test file extension mapping"""
        expected_extensions = {
            'graphml': 'graphml',
            'gexf': 'gexf',
            'json-ld': 'jsonld',
            'cytoscape': 'cyjs',
            'gephi': 'gexf',
            'pajek': 'net',
            'gml': 'gml',
            'dot': 'dot',
            'adjacency': 'adj',
            'edgelist': 'edges'
        }
        
        for format, expected_ext in expected_extensions.items():
            ext = export_tool._get_file_extension(format)
            assert ext == expected_ext