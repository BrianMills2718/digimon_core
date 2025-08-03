"""Graph Data Loader for Metrics

Loads graph data from various sources for metrics calculation.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class MetricsDataLoader:
    """Load graph data from various sources for metrics calculation"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
    
    def load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None, 
                       directed: bool = False, max_nodes: int = 10000) -> Optional[nx.Graph]:
        """Load graph data from specified source"""
        try:
            if graph_source == "networkx":
                return self._load_from_networkx_data(graph_data, directed)
            elif graph_source == "edge_list":
                return self._load_from_edge_list(graph_data, directed)
            elif graph_source == "adjacency_matrix":
                return self._load_from_adjacency_matrix(graph_data, directed)
            else:
                logger.error(f"Unsupported graph source: {graph_source}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load graph data from {graph_source}: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from NetworkX data format"""
        try:
            if not graph_data or "nodes" not in graph_data or "edges" not in graph_data:
                logger.error("NetworkX data must contain 'nodes' and 'edges' keys")
                return None
            
            # Create appropriate graph type
            graph = nx.DiGraph() if directed else nx.Graph()
            
            # Add nodes with attributes
            for node_data in graph_data["nodes"]:
                node_id = node_data.get("id")
                if node_id is not None:
                    attributes = {k: v for k, v in node_data.items() if k != "id"}
                    graph.add_node(node_id, **attributes)
            
            # Add edges with attributes
            for edge_data in graph_data["edges"]:
                source = edge_data.get("source")
                target = edge_data.get("target")
                if source is not None and target is not None:
                    attributes = {k: v for k, v in edge_data.items() 
                                if k not in ["source", "target"]}
                    graph.add_edge(source, target, **attributes)
            
            logger.info(f"Loaded NetworkX graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error loading NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        try:
            if not graph_data or "edges" not in graph_data:
                logger.error("Edge list data must contain 'edges' key")
                return None
            
            # Create appropriate graph type
            graph = nx.DiGraph() if directed else nx.Graph()
            
            # Add edges
            for edge in graph_data["edges"]:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 else 1.0
                    graph.add_edge(source, target, weight=weight)
                elif isinstance(edge, dict):
                    source = edge.get("source")
                    target = edge.get("target")
                    if source is not None and target is not None:
                        attributes = {k: v for k, v in edge.items() 
                                    if k not in ["source", "target"]}
                        graph.add_edge(source, target, **attributes)
            
            # Add node attributes if provided
            if "nodes" in graph_data:
                for node_data in graph_data["nodes"]:
                    node_id = node_data.get("id")
                    if node_id in graph.nodes:
                        attributes = {k: v for k, v in node_data.items() if k != "id"}
                        graph.nodes[node_id].update(attributes)
            
            logger.info(f"Loaded edge list graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error loading edge list: {e}")
            return None
    
    def _load_from_adjacency_matrix(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        try:
            if not graph_data or "matrix" not in graph_data:
                logger.error("Adjacency matrix data must contain 'matrix' key")
                return None
            
            matrix = np.array(graph_data["matrix"])
            node_labels = graph_data.get("node_labels", [f"node_{i}" for i in range(len(matrix))])
            
            # Create graph from adjacency matrix
            if directed:
                graph = nx.from_numpy_array(matrix, create_using=nx.DiGraph)
            else:
                graph = nx.from_numpy_array(matrix)
            
            # Relabel nodes if labels provided
            if len(node_labels) == len(graph.nodes):
                mapping = {i: label for i, label in enumerate(node_labels)}
                graph = nx.relabel_nodes(graph, mapping)
            
            logger.info(f"Loaded adjacency matrix graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error loading adjacency matrix: {e}")
            return None
    
    def get_max_nodes_for_mode(self, performance_mode: str) -> int:
        """Get maximum nodes based on performance mode"""
        mode_limits = {
            "fast": 1000,
            "balanced": 5000,
            "comprehensive": 10000,
            "research": 50000
        }
        return mode_limits.get(performance_mode, 5000)