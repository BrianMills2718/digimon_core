"""Graph Data Loader for Path Analysis

Loads graph data from various sources for path analysis.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PathAnalysisDataLoader:
    """Load graph data from various sources for path analysis"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
    
    def create_graph_from_data(self, graph_source: str, graph_data: Dict[str, Any], 
                              input_data: Dict[str, Any]) -> Optional[nx.Graph]:
        """Create graph from various data sources"""
        try:
            directed = input_data.get('directed', False)
            weighted = input_data.get('weighted', False)
            
            if graph_source == "networkx":
                return self._create_from_networkx_data(graph_data, directed, weighted)
            elif graph_source == "edge_list":
                return self._create_from_edge_list(graph_data, directed, weighted)
            elif graph_source == "adjacency_matrix":
                return self._create_from_adjacency_matrix(graph_data, directed, weighted)
            elif graph_source == "node_edge_lists":
                return self._create_from_node_edge_lists(graph_data, directed, weighted)
            else:
                logger.error(f"Unsupported graph source: {graph_source}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create graph from {graph_source}: {e}")
            return None
    
    def _create_from_networkx_data(self, graph_data: Dict[str, Any], 
                                  directed: bool, weighted: bool) -> Optional[nx.Graph]:
        """Create graph from NetworkX data format"""
        try:
            if directed:
                graph = nx.DiGraph()
            else:
                graph = nx.Graph()
            
            # Add nodes
            if "nodes" in graph_data:
                for node in graph_data["nodes"]:
                    if isinstance(node, dict):
                        node_id = node.get("id")
                        attrs = {k: v for k, v in node.items() if k != "id"}
                        graph.add_node(node_id, **attrs)
                    else:
                        graph.add_node(node)
            
            # Add edges
            if "edges" in graph_data:
                for edge in graph_data["edges"]:
                    if isinstance(edge, dict):
                        source = edge.get("source")
                        target = edge.get("target")
                        weight = edge.get("weight", 1.0) if weighted else None
                        attrs = {k: v for k, v in edge.items() 
                               if k not in ["source", "target"]}
                        if weight is not None:
                            attrs["weight"] = weight
                        graph.add_edge(source, target, **attrs)
                    elif len(edge) >= 2:
                        source, target = edge[0], edge[1]
                        weight = edge[2] if len(edge) > 2 and weighted else 1.0
                        if weighted:
                            graph.add_edge(source, target, weight=weight)
                        else:
                            graph.add_edge(source, target)
            
            logger.info(f"Created NetworkX graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error creating NetworkX graph: {e}")
            return None
    
    def _create_from_edge_list(self, graph_data: Dict[str, Any], 
                              directed: bool, weighted: bool) -> Optional[nx.Graph]:
        """Create graph from edge list format"""
        try:
            if directed:
                graph = nx.DiGraph()
            else:
                graph = nx.Graph()
            
            edges = graph_data.get("edges", [])
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 and weighted else 1.0
                    
                    if weighted:
                        graph.add_edge(source, target, weight=weight)
                    else:
                        graph.add_edge(source, target)
                elif isinstance(edge, dict):
                    source = edge.get("source")
                    target = edge.get("target")
                    weight = edge.get("weight", 1.0) if weighted else None
                    
                    if source and target:
                        if weighted and weight is not None:
                            graph.add_edge(source, target, weight=weight)
                        else:
                            graph.add_edge(source, target)
            
            logger.info(f"Created edge list graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error creating edge list graph: {e}")
            return None
    
    def _create_from_adjacency_matrix(self, graph_data: Dict[str, Any], 
                                     directed: bool, weighted: bool) -> Optional[nx.Graph]:
        """Create graph from adjacency matrix"""
        try:
            matrix = np.array(graph_data.get("matrix", []))
            node_labels = graph_data.get("node_labels", [])
            
            if len(matrix) == 0:
                logger.error("Empty adjacency matrix")
                return None
            
            # Create graph from matrix
            if directed:
                graph = nx.from_numpy_array(matrix, create_using=nx.DiGraph)
            else:
                graph = nx.from_numpy_array(matrix, create_using=nx.Graph)
            
            # Relabel nodes if labels provided
            if node_labels and len(node_labels) == len(graph.nodes):
                mapping = {i: label for i, label in enumerate(node_labels)}
                graph = nx.relabel_nodes(graph, mapping)
            
            # Handle weighted vs unweighted
            if not weighted:
                # Remove weight attributes for unweighted graphs
                for u, v, data in graph.edges(data=True):
                    if 'weight' in data:
                        del data['weight']
            
            logger.info(f"Created adjacency matrix graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error creating adjacency matrix graph: {e}")
            return None
    
    def _create_from_node_edge_lists(self, graph_data: Dict[str, Any], 
                                    directed: bool, weighted: bool) -> Optional[nx.Graph]:
        """Create graph from separate node and edge lists"""
        try:
            if directed:
                graph = nx.DiGraph()
            else:
                graph = nx.Graph()
            
            # Add nodes
            nodes = graph_data.get("nodes", [])
            for node in nodes:
                graph.add_node(node)
            
            # Add edges
            edges = graph_data.get("edges", [])
            for edge in edges:
                if len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 and weighted else 1.0
                    
                    if weighted:
                        graph.add_edge(source, target, weight=weight)
                    else:
                        graph.add_edge(source, target)
            
            logger.info(f"Created node-edge list graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error creating node-edge list graph: {e}")
            return None
    
    def validate_graph_for_analysis(self, graph: nx.Graph, analysis_type: str) -> Dict[str, Any]:
        """Validate graph is suitable for specific analysis type"""
        validation = {"valid": True, "warnings": [], "errors": []}
        
        if graph is None:
            validation["valid"] = False
            validation["errors"].append("Graph is None")
            return validation
        
        if len(graph.nodes) == 0:
            validation["valid"] = False
            validation["errors"].append("Graph has no nodes")
            return validation
        
        if len(graph.edges) == 0:
            validation["warnings"].append("Graph has no edges - some analyses may not be meaningful")
        
        # Analysis-specific validations
        if analysis_type == "shortest_paths":
            # Check for negative weights in shortest path analysis
            for u, v, data in graph.edges(data=True):
                weight = data.get('weight', 1.0)
                if weight < 0:
                    validation["warnings"].append("Graph contains negative weights - some algorithms may not work")
                    break
        
        elif analysis_type == "flow_analysis":
            if not graph.is_directed():
                validation["warnings"].append("Flow analysis typically requires directed graphs")
            
            # Check for capacity attributes
            has_capacity = any('capacity' in data for u, v, data in graph.edges(data=True))
            if not has_capacity:
                validation["warnings"].append("No capacity attributes found - will use unit capacities")
        
        elif analysis_type == "all_pairs":
            if len(graph.nodes) > 1000:
                validation["warnings"].append("Large graph - all-pairs analysis may be slow")
        
        return validation