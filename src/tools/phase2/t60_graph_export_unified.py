#!/usr/bin/env python3
"""
T60: Graph Export Tool (Unified Interface)
=========================================

Exports knowledge graphs to multiple formats with compression and batch support.

This tool provides:
- 10+ export formats (GraphML, GEXF, JSON-LD, etc.)
- Compression support (gzip, zip)
- Batch export capabilities
- Format-specific optimizations
- Metadata preservation
"""

import json
import xml.etree.ElementTree as ET
import gzip
import zipfile
import io
import networkx as nx
import anyio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from pathlib import Path
import logging
from enum import Enum

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult


class ExportFormat(str, Enum):
    """Supported export formats"""
    GRAPHML = "graphml"
    GEXF = "gexf"
    JSON_LD = "json-ld"
    CYPHER = "cypher"
    DOT = "dot"
    CSV = "csv"
    TSV = "tsv"
    ADJACENCY_LIST = "adjacency_list"
    EDGE_LIST = "edge_list"
    PAJEK = "pajek"


class CompressionType(str, Enum):
    """Supported compression types"""
    NONE = "none"
    GZIP = "gzip"
    ZIP = "zip"


# Input parameters are passed via ToolRequest


# Output is returned via ToolResult


class GraphExportTool(BaseTool):
    """
    Graph Export Tool
    
    Exports knowledge graphs to various formats with support for
    compression and batch operations.
    """
    
    def __init__(self, service_manager=None):
        """Initialize graph export tool"""
        if service_manager is None:
            from src.core.service_manager import ServiceManager
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T60"
        self.name = "Graph Export Tool"
        self.description = "Exports knowledge graphs to multiple formats"
        self.version = "1.0.0"
        self.tool_type = "export"
        self.logger = logging.getLogger(__name__)
    
    def get_contract(self) -> dict:
        """Return tool contract specification"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.tool_type,
            "input_schema": {
                "type": "object",
                "properties": {
                    "graph_data": {
                        "type": "object",
                        "properties": {
                            "nodes": {"type": "array"},
                            "edges": {"type": "array"}
                        },
                        "required": ["nodes", "edges"]
                    },
                    "export_format": {"type": "string", "enum": [f.value for f in ExportFormat]},
                    "output_path": {"type": "string"},
                    "compression": {"type": "string", "enum": [c.value for c in CompressionType]},
                    "include_metadata": {"type": "boolean"},
                    "batch_export": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["graph_data", "export_format"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "export_path": {"type": "string"},
                    "export_format": {"type": "string"},
                    "file_size_bytes": {"type": "integer"},
                    "num_nodes_exported": {"type": "integer"},
                    "num_edges_exported": {"type": "integer"}
                }
            }
        }
    
    async def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph export operation"""
        try:
            # Extract parameters from request
            input_data = request.input_data
            graph_data = input_data.get('graph_data', {})
            export_format = ExportFormat(input_data.get('export_format', 'graphml'))
            output_path = input_data.get('output_path')
            compression = CompressionType(input_data.get('compression', 'none'))
            include_metadata = input_data.get('include_metadata', True)
            batch_export = input_data.get('batch_export')
            
            # Convert to NetworkX graph
            G = self._build_networkx_graph(graph_data)
            
            # Handle batch export if requested
            if batch_export:
                batch_results = await self._batch_export(
                    G, 
                    [ExportFormat(f) for f in batch_export],
                    output_path,
                    compression,
                    include_metadata
                )
                
                # Calculate total size
                total_size = sum(r['file_size_bytes'] for r in batch_results)
                
                return ToolResult(
                    tool_id=self.tool_id,
                    status="success",
                    data={
                        "export_path": str(Path(output_path or "./exports").parent),
                        "export_format": "batch",
                        "file_size_bytes": total_size,
                        "num_nodes_exported": len(G.nodes()),
                        "num_edges_exported": len(G.edges()),
                        "compression_used": compression.value,
                        "batch_results": batch_results,
                        "export_metadata": {
                            "formats_exported": batch_export,
                            "export_timestamp": datetime.now().isoformat()
                        }
                    },
                    metadata={
                        "tool_version": self.version,
                        "operation": request.operation
                    },
                    execution_time=0.0,
                    memory_used=0
                )
            
            # Single format export
            export_result = await self._export_graph(
                G,
                export_format,
                output_path,
                compression,
                include_metadata
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "export_path": export_result['path'],
                    "export_format": export_format.value,
                    "file_size_bytes": export_result['size'],
                    "num_nodes_exported": len(G.nodes()),
                    "num_edges_exported": len(G.edges()),
                    "compression_used": compression.value,
                    "compression_ratio": export_result.get('compression_ratio'),
                    "export_metadata": {
                        "export_timestamp": datetime.now().isoformat(),
                        "networkx_version": nx.__version__
                    }
                },
                metadata={
                    "tool_version": self.version,
                    "operation": request.operation
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except anyio.get_cancelled_exc_class():
            # Proper cancellation handling for AnyIO
            self.logger.info("Graph export was cancelled")
            return ToolResult(
                tool_id=self.tool_id,
                status="cancelled",
                data={"message": "Export was cancelled by user or timeout"},
                metadata={"tool_version": self.version},
                execution_time=0.0,
                memory_used=0
            )
        except Exception as e:
            self.logger.error(f"Graph export failed: {str(e)}")
            raise
    
    def _build_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.Graph:
        """Convert input graph data to NetworkX graph"""
        G = nx.Graph()
        
        # Add nodes with properties
        for node in graph_data.get('nodes', []):
            node_id = node.get('id', node.get('node_id'))
            properties = node.get('properties', {})
            label = node.get('label', '')
            
            # Combine all attributes
            node_attrs = {'label': label}
            node_attrs.update(properties)
            
            G.add_node(node_id, **node_attrs)
        
        # Add edges with properties
        for edge in graph_data.get('edges', []):
            source = edge.get('source', edge.get('from'))
            target = edge.get('target', edge.get('to'))
            edge_type = edge.get('type', edge.get('relationship_type', 'RELATED'))
            properties = edge.get('properties', {})
            
            # Combine all attributes
            edge_attrs = {'type': edge_type}
            edge_attrs.update(properties)
            
            G.add_edge(source, target, **edge_attrs)
        
        return G
    
    async def _export_graph(self, G: nx.Graph, format: ExportFormat, 
                          output_path: Optional[str], compression: CompressionType,
                          include_metadata: bool) -> Dict[str, Any]:
        """Export graph in specified format"""
        # Generate default path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"graph_export_{timestamp}.{format.value}"
        
        # Export based on format (CPU-intensive for large graphs)
        content = await anyio.to_thread.run_sync(
            self._format_graph,
            G, format, include_metadata,
            cancellable=True
        )
        
        # Calculate original size before compression
        if isinstance(content, str):
            original_size = len(content.encode('utf-8'))
        else:
            original_size = len(content)
        
        # Apply compression if requested (CPU-intensive)
        if compression != CompressionType.NONE:
            content, output_path = await anyio.to_thread.run_sync(
                self._compress_content,
                content, output_path, compression,
                cancellable=True
            )
        
        # Write to file using AnyIO (truly async I/O)
        if isinstance(content, bytes):
            async with await anyio.open_file(output_path, 'wb') as f:
                await f.write(content)
        else:
            async with await anyio.open_file(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
        
        # Calculate file size (I/O operation)
        file_size = await anyio.to_thread.run_sync(
            lambda: Path(output_path).stat().st_size,
            cancellable=True
        )
        compression_ratio = None
        if compression != CompressionType.NONE and original_size > 0:
            compression_ratio = file_size / original_size
        
        return {
            'path': output_path,
            'size': file_size,
            'compression_ratio': compression_ratio
        }
    
    def _format_graph(self, G: nx.Graph, format: ExportFormat, include_metadata: bool) -> Union[str, bytes]:
        """Format graph based on export format"""
        if format == ExportFormat.GRAPHML:
            return self._to_graphml(G, include_metadata)
        elif format == ExportFormat.GEXF:
            return self._to_gexf(G, include_metadata)
        elif format == ExportFormat.JSON_LD:
            return self._to_json_ld(G, include_metadata)
        elif format == ExportFormat.CYPHER:
            return self._to_cypher(G)
        elif format == ExportFormat.DOT:
            return self._to_dot(G)
        elif format == ExportFormat.CSV:
            return self._to_csv(G)
        elif format == ExportFormat.TSV:
            return self._to_tsv(G)
        elif format == ExportFormat.ADJACENCY_LIST:
            return self._to_adjacency_list(G)
        elif format == ExportFormat.EDGE_LIST:
            return self._to_edge_list(G)
        elif format == ExportFormat.PAJEK:
            return self._to_pajek(G)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _to_graphml(self, G: nx.Graph, include_metadata: bool) -> str:
        """Convert to GraphML format"""
        # NetworkX has built-in GraphML support
        buffer = io.BytesIO()
        nx.write_graphml(G, buffer)
        return buffer.getvalue().decode('utf-8')
    
    def _to_gexf(self, G: nx.Graph, include_metadata: bool) -> str:
        """Convert to GEXF format"""
        # Use BytesIO for GEXF and then decode
        buffer = io.BytesIO()
        nx.write_gexf(G, buffer)
        return buffer.getvalue().decode('utf-8')
    
    def _to_json_ld(self, G: nx.Graph, include_metadata: bool) -> str:
        """Convert to JSON-LD format"""
        json_ld = {
            "@context": {
                "@vocab": "http://schema.org/",
                "nodes": "@graph",
                "edges": "hasPart"
            },
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for node, attrs in G.nodes(data=True):
            node_data = {
                "@id": str(node),
                "@type": attrs.get('label', 'Thing')
            }
            node_data.update(attrs)
            json_ld["nodes"].append(node_data)
        
        # Add edges
        for source, target, attrs in G.edges(data=True):
            edge_data = {
                "@type": attrs.get('type', 'Relationship'),
                "source": {"@id": str(source)},
                "target": {"@id": str(target)}
            }
            edge_data.update(attrs)
            json_ld["edges"].append(edge_data)
        
        if include_metadata:
            json_ld["metadata"] = {
                "exportDate": datetime.now().isoformat(),
                "nodeCount": len(G.nodes()),
                "edgeCount": len(G.edges())
            }
        
        return json.dumps(json_ld, indent=2)
    
    def _to_cypher(self, G: nx.Graph) -> str:
        """Convert to Cypher query format"""
        cypher_statements = []
        
        # Create nodes
        for node, attrs in G.nodes(data=True):
            label = attrs.get('label', 'Node')
            properties = {k: v for k, v in attrs.items() if k != 'label'}
            prop_str = ", ".join([f"{k}: '{v}'" for k, v in properties.items()])
            
            cypher = f"CREATE (n{node}:{label} {{{prop_str}}})"
            cypher_statements.append(cypher)
        
        # Create relationships
        for source, target, attrs in G.edges(data=True):
            rel_type = attrs.get('type', 'RELATED_TO')
            properties = {k: v for k, v in attrs.items() if k != 'type'}
            prop_str = ", ".join([f"{k}: '{v}'" for k, v in properties.items()])
            
            cypher = f"CREATE (n{source})-[:{rel_type} {{{prop_str}}}]->(n{target})"
            cypher_statements.append(cypher)
        
        return ";\n".join(cypher_statements) + ";"
    
    def _to_dot(self, G: nx.Graph) -> str:
        """Convert to DOT format with fallback if pygraphviz not available"""
        try:
            from networkx.drawing.nx_agraph import to_agraph
            A = to_agraph(G)
            return str(A)
        except ImportError:
            # Fallback to simple DOT format if pygraphviz not available
            self.logger.warning("pygraphviz not available, using simple DOT format")
            return self._to_simple_dot(G)
    
    def _to_simple_dot(self, G: nx.Graph) -> str:
        """Simple DOT format without pygraphviz dependency"""
        lines = ["digraph G {"]
        
        # Add nodes
        for node, attrs in G.nodes(data=True):
            label = attrs.get('label', str(node))
            lines.append(f'  {node} [label="{label}"];')
        
        # Add edges
        for source, target, attrs in G.edges(data=True):
            edge_type = attrs.get('type', '')
            if edge_type:
                lines.append(f'  {source} -> {target} [label="{edge_type}"];')
            else:
                lines.append(f'  {source} -> {target};')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _to_csv(self, G: nx.Graph) -> str:
        """Convert to CSV edge list"""
        lines = ["source,target,type,weight"]
        for source, target, attrs in G.edges(data=True):
            edge_type = attrs.get('type', 'RELATED')
            weight = attrs.get('weight', 1.0)
            lines.append(f"{source},{target},{edge_type},{weight}")
        return "\n".join(lines)
    
    def _to_tsv(self, G: nx.Graph) -> str:
        """Convert to TSV edge list"""
        lines = ["source\ttarget\ttype\tweight"]
        for source, target, attrs in G.edges(data=True):
            edge_type = attrs.get('type', 'RELATED')
            weight = attrs.get('weight', 1.0)
            lines.append(f"{source}\t{target}\t{edge_type}\t{weight}")
        return "\n".join(lines)
    
    def _to_adjacency_list(self, G: nx.Graph) -> str:
        """Convert to adjacency list format"""
        lines = []
        for node in G.nodes():
            neighbors = list(G.neighbors(node))
            if neighbors:
                lines.append(f"{node}: {' '.join(map(str, neighbors))}")
        return "\n".join(lines)
    
    def _to_edge_list(self, G: nx.Graph) -> str:
        """Convert to simple edge list"""
        lines = []
        for source, target in G.edges():
            lines.append(f"{source} {target}")
        return "\n".join(lines)
    
    def _to_pajek(self, G: nx.Graph) -> str:
        """Convert to Pajek format"""
        buffer = io.StringIO()
        nx.write_pajek(G, buffer)
        return buffer.getvalue()
    
    def _compress_content(self, content: Union[str, bytes], 
                         output_path: str, compression: CompressionType) -> Tuple[bytes, str]:
        """Compress content based on compression type"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if compression == CompressionType.GZIP:
            compressed = gzip.compress(content)
            output_path = output_path + '.gz'
            return compressed, output_path
        
        elif compression == CompressionType.ZIP:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                filename = Path(output_path).name
                zf.writestr(filename, content)
            compressed = buffer.getvalue()
            output_path = output_path + '.zip'
            return compressed, output_path
        
        return content, output_path
    
    async def _batch_export(self, G: nx.Graph, formats: List[ExportFormat],
                          base_path: Optional[str], compression: CompressionType,
                          include_metadata: bool) -> List[Dict[str, Any]]:
        """Export graph to multiple formats"""
        results = []
        
        if not base_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_path = f"graph_export_{timestamp}"
        
        base_dir = Path(base_path).parent
        base_name = Path(base_path).stem
        
        for format in formats:
            output_path = str(base_dir / f"{base_name}.{format.value}")
            result = await self._export_graph(G, format, output_path, compression, include_metadata)
            results.append({
                'format': format.value,
                'path': result['path'],
                'file_size_bytes': result['size'],
                'compression_ratio': result.get('compression_ratio')
            })
        
        return results


# Tool registration
def get_tool_class():
    """Return the tool class for registration"""
    return GraphExportTool