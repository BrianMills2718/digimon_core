#!/usr/bin/env python3
"""
Graph Export Tool - Export academic knowledge graphs to multiple formats

Supports exporting to GraphML, GEXF, JSON-LD, and other standard graph formats
with comprehensive metadata preservation and format-specific optimizations.
"""

import asyncio
import time
import logging
import json
import xml.etree.ElementTree as ET
import networkx as nx
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import gzip
import zipfile

logger = logging.getLogger(__name__)


class GraphExportError(Exception):
    """Base exception for graph export operations"""
    pass


class GraphExportTool:
    """Export academic knowledge graphs to various formats"""
    
    SUPPORTED_FORMATS = [
        'graphml',      # GraphML XML format
        'gexf',         # Graph Exchange XML Format
        'json-ld',      # JSON Linked Data
        'cytoscape',    # Cytoscape JSON
        'gephi',        # Gephi-compatible
        'pajek',        # Pajek .net format
        'gml',          # Graph Modelling Language
        'dot',          # Graphviz DOT format
        'adjacency',    # Adjacency list
        'edgelist'      # Simple edge list
    ]
    
    def __init__(self, neo4j_manager, distributed_tx_manager):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        
        # Export configuration
        self.max_nodes_full_export = 100000
        self.compression_threshold = 10 * 1024 * 1024  # 10MB
        
        logger.info("GraphExportTool initialized")
    
    async def export_graph(self, output_path: str, format: str = 'graphml',
                          entity_type: str = None, relationship_type: str = None,
                          include_metadata: bool = True, compress: bool = False,
                          sampling_ratio: float = None) -> Dict[str, Any]:
        """
        Export graph to specified format
        
        Args:
            output_path: Path to save the exported file
            format: Export format (graphml, gexf, json-ld, etc.)
            entity_type: Filter by entity type
            relationship_type: Filter by relationship type
            include_metadata: Include node/edge metadata
            compress: Compress output file
            sampling_ratio: Sample graph if too large (0.0-1.0)
            
        Returns:
            Dictionary with export statistics and file info
        """
        
        tx_id = f"export_{format}_{int(time.time())}"
        logger.info(f"Starting graph export - format: {format}, tx_id: {tx_id}")
        
        if format not in self.SUPPORTED_FORMATS:
            raise GraphExportError(f"Unsupported format: {format}. Supported: {self.SUPPORTED_FORMATS}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Fetch graph data
            graph_data = await self._fetch_graph_data(
                entity_type, relationship_type, sampling_ratio
            )
            
            if not graph_data['nodes']:
                logger.warning("No nodes found for export")
                return {
                    'status': 'no_data',
                    'message': 'No nodes found for export',
                    'format': format,
                    'output_path': output_path
                }
            
            # Build NetworkX graph
            G = await self._build_networkx_graph(graph_data, include_metadata)
            
            # Export based on format
            export_stats = await self._export_by_format(
                G, output_path, format, include_metadata
            )
            
            # Compress if requested or file is large
            final_path = output_path
            if compress or export_stats['file_size'] > self.compression_threshold:
                final_path = await self._compress_file(output_path)
                export_stats['compressed'] = True
                export_stats['compressed_size'] = Path(final_path).stat().st_size
            
            # Record export operation
            await self._record_export_operation(tx_id, export_stats)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            logger.info(f"Export completed - {export_stats['node_count']} nodes, "
                       f"{export_stats['edge_count']} edges to {format}")
            
            return {
                'status': 'success',
                'format': format,
                'output_path': final_path,
                'statistics': export_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Graph export failed: {str(e)}")
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise GraphExportError(f"Export failed: {str(e)}")
    
    async def _fetch_graph_data(self, entity_type: Optional[str], 
                               relationship_type: Optional[str],
                               sampling_ratio: Optional[float]) -> Dict[str, List]:
        """Fetch graph data from Neo4j"""
        
        # Build query based on filters
        entity_filter = f":{entity_type}" if entity_type else ""
        rel_filter = f":{relationship_type}" if relationship_type else ""
        
        # Add sampling if needed
        sampling_clause = ""
        if sampling_ratio and 0 < sampling_ratio < 1:
            sampling_clause = f"WHERE rand() < {sampling_ratio}"
        
        query = f"""
        MATCH (n{entity_filter})
        {sampling_clause}
        WITH n
        OPTIONAL MATCH (n)-[r{rel_filter}]->(m)
        WITH n, collect(DISTINCT {{
            id: id(m),
            source: id(n),
            target: id(m),
            type: type(r),
            properties: properties(r)
        }}) as relationships
        RETURN 
            id(n) as node_id,
            labels(n) as labels,
            properties(n) as properties,
            relationships
        """
        
        result = await self.neo4j_manager.execute_read_query(query)
        
        nodes = []
        edges = []
        node_ids = set()
        
        for record in result:
            node_id = record['node_id']
            node_ids.add(node_id)
            
            nodes.append({
                'id': node_id,
                'labels': record['labels'],
                'properties': record.get('properties', {})
            })
            
            for rel in record['relationships']:
                if rel['target'] is not None and rel['id'] in node_ids:
                    edges.append({
                        'source': rel['source'],
                        'target': rel['target'],
                        'type': rel['type'],
                        'properties': rel.get('properties', {})
                    })
        
        return {'nodes': nodes, 'edges': edges}
    
    async def _build_networkx_graph(self, graph_data: Dict[str, List], 
                                   include_metadata: bool) -> nx.DiGraph:
        """Build NetworkX graph from data"""
        
        G = nx.DiGraph()
        
        # Add nodes with metadata
        for node in graph_data['nodes']:
            if include_metadata:
                # Prepare node attributes
                attrs = {
                    'labels': ','.join(node['labels']),
                    **node['properties']
                }
                # Convert datetime objects to strings
                for key, value in attrs.items():
                    if isinstance(value, datetime):
                        attrs[key] = value.isoformat()
                
                G.add_node(node['id'], **attrs)
            else:
                G.add_node(node['id'])
        
        # Add edges with metadata
        for edge in graph_data['edges']:
            if edge['source'] in G and edge['target'] in G:
                if include_metadata:
                    attrs = {
                        'type': edge['type'],
                        **edge.get('properties', {})
                    }
                    # Convert datetime objects to strings
                    for key, value in attrs.items():
                        if isinstance(value, datetime):
                            attrs[key] = value.isoformat()
                    
                    G.add_edge(edge['source'], edge['target'], **attrs)
                else:
                    G.add_edge(edge['source'], edge['target'])
        
        return G
    
    async def _export_by_format(self, G: nx.DiGraph, output_path: str, 
                               format: str, include_metadata: bool) -> Dict[str, Any]:
        """Export graph based on specified format"""
        
        start_time = time.time()
        
        if format == 'graphml':
            await self._export_graphml(G, output_path)
        elif format == 'gexf':
            await self._export_gexf(G, output_path)
        elif format == 'json-ld':
            await self._export_json_ld(G, output_path, include_metadata)
        elif format == 'cytoscape':
            await self._export_cytoscape(G, output_path)
        elif format == 'gephi':
            await self._export_gephi(G, output_path)
        elif format == 'pajek':
            nx.write_pajek(G, output_path)
        elif format == 'gml':
            nx.write_gml(G, output_path)
        elif format == 'dot':
            await self._export_dot(G, output_path)
        elif format == 'adjacency':
            await self._export_adjacency(G, output_path)
        elif format == 'edgelist':
            nx.write_edgelist(G, output_path, data=include_metadata)
        else:
            raise GraphExportError(f"Export format not implemented: {format}")
        
        export_time = time.time() - start_time
        file_size = Path(output_path).stat().st_size
        
        return {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'export_time': export_time,
            'file_size': file_size,
            'format': format,
            'metadata_included': include_metadata
        }
    
    async def _export_graphml(self, G: nx.DiGraph, output_path: str) -> None:
        """Export to GraphML format"""
        try:
            nx.write_graphml(G, output_path, encoding='utf-8', prettyprint=True)
        except Exception as e:
            # Handle attribute type issues
            logger.warning(f"GraphML export issue: {e}. Trying with string conversion.")
            
            # Convert problematic attributes to strings
            for node, attrs in G.nodes(data=True):
                for key, value in list(attrs.items()):
                    if not isinstance(value, (str, int, float, bool)):
                        attrs[key] = str(value)
            
            for source, target, attrs in G.edges(data=True):
                for key, value in list(attrs.items()):
                    if not isinstance(value, (str, int, float, bool)):
                        attrs[key] = str(value)
            
            nx.write_graphml(G, output_path, encoding='utf-8', prettyprint=True)
    
    async def _export_gexf(self, G: nx.DiGraph, output_path: str) -> None:
        """Export to GEXF format"""
        nx.write_gexf(G, output_path, encoding='utf-8', prettyprint=True)
    
    async def _export_json_ld(self, G: nx.DiGraph, output_path: str, 
                             include_metadata: bool) -> None:
        """Export to JSON-LD format"""
        
        json_ld = {
            "@context": {
                "@vocab": "http://schema.org/",
                "nodes": "@graph",
                "edges": "knows",
                "id": "@id",
                "type": "@type"
            },
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for node, attrs in G.nodes(data=True):
            node_data = {
                "id": f"node/{node}",
                "type": "Entity"
            }
            
            if include_metadata:
                # Add attributes
                for key, value in attrs.items():
                    if key != 'labels':
                        node_data[key] = value
                    else:
                        node_data["type"] = value.split(',')
            
            json_ld["nodes"].append(node_data)
        
        # Add edges
        for source, target, attrs in G.edges(data=True):
            edge_data = {
                "source": f"node/{source}",
                "target": f"node/{target}"
            }
            
            if include_metadata:
                for key, value in attrs.items():
                    edge_data[key] = value
            
            json_ld["edges"].append(edge_data)
        
        # Write JSON-LD
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_ld, f, indent=2, ensure_ascii=False)
    
    async def _export_cytoscape(self, G: nx.DiGraph, output_path: str) -> None:
        """Export to Cytoscape JSON format"""
        
        cytoscape_data = {
            "format_version": "1.0",
            "generated_by": "KGAS Graph Export Tool",
            "elements": {
                "nodes": [],
                "edges": []
            }
        }
        
        # Add nodes
        for node, attrs in G.nodes(data=True):
            node_element = {
                "data": {
                    "id": str(node),
                    "name": attrs.get('name', f'Node_{node}')
                }
            }
            
            # Add other attributes
            for key, value in attrs.items():
                if key not in ['name']:
                    node_element["data"][key] = str(value)
            
            cytoscape_data["elements"]["nodes"].append(node_element)
        
        # Add edges
        edge_id = 0
        for source, target, attrs in G.edges(data=True):
            edge_element = {
                "data": {
                    "id": f"e{edge_id}",
                    "source": str(source),
                    "target": str(target)
                }
            }
            
            # Add edge attributes
            for key, value in attrs.items():
                edge_element["data"][key] = str(value)
            
            cytoscape_data["elements"]["edges"].append(edge_element)
            edge_id += 1
        
        # Write Cytoscape JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cytoscape_data, f, indent=2)
    
    async def _export_gephi(self, G: nx.DiGraph, output_path: str) -> None:
        """Export in Gephi-compatible format (GEXF with additional attributes)"""
        
        # Add Gephi-specific attributes
        for node in G.nodes():
            G.nodes[node]['viz'] = {
                'size': G.degree(node),
                'position': {'x': 0, 'y': 0, 'z': 0}
            }
        
        # Export as GEXF
        await self._export_gexf(G, output_path)
    
    async def _export_dot(self, G: nx.DiGraph, output_path: str) -> None:
        """Export to Graphviz DOT format"""
        
        try:
            from networkx.drawing.nx_agraph import write_dot
            write_dot(G, output_path)
        except ImportError:
            # Fallback to manual DOT generation
            with open(output_path, 'w') as f:
                f.write("digraph G {\n")
                f.write("  rankdir=LR;\n")
                f.write("  node [shape=ellipse];\n")
                
                # Write nodes
                for node, attrs in G.nodes(data=True):
                    label = attrs.get('name', str(node))
                    f.write(f'  {node} [label="{label}"];\n')
                
                # Write edges
                for source, target, attrs in G.edges(data=True):
                    edge_type = attrs.get('type', '')
                    if edge_type:
                        f.write(f'  {source} -> {target} [label="{edge_type}"];\n')
                    else:
                        f.write(f'  {source} -> {target};\n')
                
                f.write("}\n")
    
    async def _export_adjacency(self, G: nx.DiGraph, output_path: str) -> None:
        """Export as adjacency list"""
        
        with open(output_path, 'w') as f:
            for node in G.nodes():
                neighbors = list(G.neighbors(node))
                if neighbors:
                    f.write(f"{node}: {' '.join(map(str, neighbors))}\n")
                else:
                    f.write(f"{node}:\n")
    
    async def _compress_file(self, file_path: str) -> str:
        """Compress the exported file"""
        
        if file_path.endswith('.json') or file_path.endswith('.xml'):
            # Use gzip for text files
            compressed_path = f"{file_path}.gz"
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            # Remove original file
            Path(file_path).unlink()
            
            return compressed_path
        else:
            # Use zip for other formats
            zip_path = f"{file_path}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, Path(file_path).name)
            
            # Remove original file
            Path(file_path).unlink()
            
            return zip_path
    
    async def _record_export_operation(self, tx_id: str, stats: Dict[str, Any]) -> None:
        """Record export operation in distributed transaction"""
        
        await self.dtm.record_operation(
            tx_id=tx_id,
            operation={
                'type': 'graph_export',
                'timestamp': datetime.now().isoformat(),
                'statistics': stats
            }
        )
    
    async def batch_export(self, output_dir: str, formats: List[str] = None,
                          entity_type: str = None, relationship_type: str = None) -> Dict[str, Any]:
        """
        Export graph to multiple formats in batch
        
        Args:
            output_dir: Directory to save exported files
            formats: List of formats to export (default: all supported)
            entity_type: Filter by entity type
            relationship_type: Filter by relationship type
            
        Returns:
            Dictionary with export results for each format
        """
        
        if formats is None:
            formats = ['graphml', 'gexf', 'json-ld', 'cytoscape']
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for format in formats:
            if format not in self.SUPPORTED_FORMATS:
                logger.warning(f"Skipping unsupported format: {format}")
                continue
            
            try:
                file_name = f"graph_export_{timestamp}.{self._get_file_extension(format)}"
                file_path = str(output_path / file_name)
                
                result = await self.export_graph(
                    output_path=file_path,
                    format=format,
                    entity_type=entity_type,
                    relationship_type=relationship_type
                )
                
                results[format] = result
                
            except Exception as e:
                logger.error(f"Failed to export format {format}: {str(e)}")
                results[format] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'status': 'batch_complete',
            'output_directory': str(output_path),
            'formats_exported': len([r for r in results.values() if r['status'] == 'success']),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_file_extension(self, format: str) -> str:
        """Get appropriate file extension for format"""
        
        extensions = {
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
        
        return extensions.get(format, format)
    
    async def export_subgraph(self, center_node_id: int, depth: int, 
                             output_path: str, format: str = 'graphml') -> Dict[str, Any]:
        """
        Export a subgraph centered around a specific node
        
        Args:
            center_node_id: ID of the center node
            depth: How many hops from center to include
            output_path: Path to save the exported file
            format: Export format
            
        Returns:
            Export statistics
        """
        
        tx_id = f"export_subgraph_{center_node_id}_{int(time.time())}"
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Query for subgraph
            query = f"""
            MATCH path = (center)-[*0..{depth}]-(connected)
            WHERE id(center) = $center_id
            WITH collect(DISTINCT center) + collect(DISTINCT connected) as nodes,
                 [r in collect(relationships(path)) | r] as rels
            UNWIND nodes as n
            WITH n, rels
            RETURN DISTINCT
                id(n) as node_id,
                labels(n) as labels,
                properties(n) as properties,
                [r in rels WHERE id(startNode(r)) = id(n) | {{
                    source: id(startNode(r)),
                    target: id(endNode(r)),
                    type: type(r),
                    properties: properties(r)
                }}] as relationships
            """
            
            result = await self.neo4j_manager.execute_read_query(
                query, {'center_id': center_node_id}
            )
            
            # Process results
            nodes = []
            edges = []
            
            for record in result:
                nodes.append({
                    'id': record['node_id'],
                    'labels': record['labels'],
                    'properties': record.get('properties', {})
                })
                
                for rel in record['relationships']:
                    edges.append(rel)
            
            graph_data = {'nodes': nodes, 'edges': edges}
            
            # Build and export graph
            G = await self._build_networkx_graph(graph_data, include_metadata=True)
            export_stats = await self._export_by_format(G, output_path, format, True)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            return {
                'status': 'success',
                'center_node': center_node_id,
                'depth': depth,
                'statistics': export_stats,
                'output_path': output_path
            }
            
        except Exception as e:
            logger.error(f"Subgraph export failed: {str(e)}")
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise GraphExportError(f"Subgraph export failed: {str(e)}")