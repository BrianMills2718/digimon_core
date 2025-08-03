"""Graph Data Loader for Visualization

Loads graph data from various sources for visualization.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class VisualizationDataLoader:
    """Load graph data from various sources"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
    
    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection for graph data access"""
        try:
            self.neo4j_tool = BaseNeo4jTool()
        except Exception as e:
            logger.warning(f"Could not initialize Neo4j connection: {e}")
            self.neo4j_tool = None
    
    def load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None) -> Optional[nx.Graph]:
        """Load graph data from specified source"""
        try:
            if graph_source == "neo4j":
                return self._load_from_neo4j()
            elif graph_source == "networkx":
                return self._load_from_networkx_data(graph_data)
            elif graph_source == "edge_list":
                return self._load_from_edge_list(graph_data)
            elif graph_source == "adjacency_matrix":
                return self._load_from_adjacency_matrix(graph_data)
            else:
                logger.error(f"Unsupported graph source: {graph_source}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load graph data from {graph_source}: {e}")
            return None
    
    def _load_from_neo4j(self) -> Optional[nx.Graph]:
        """Load graph data from Neo4j database"""
        if not self.neo4j_tool:
            logger.error("Neo4j connection not available")
            return None
        
        try:
            # Query to get nodes and relationships
            nodes_query = """
            MATCH (n)
            RETURN id(n) as node_id, labels(n) as labels, properties(n) as properties
            LIMIT 10000
            """
            
            edges_query = """
            MATCH (a)-[r]->(b)
            RETURN id(a) as source, id(b) as target, type(r) as rel_type, 
                   properties(r) as properties
            LIMIT 50000
            """
            
            # Execute queries
            nodes_result = self.neo4j_tool.execute_query(nodes_query)
            edges_result = self.neo4j_tool.execute_query(edges_query)
            
            if not nodes_result.success or not edges_result.success:
                logger.error("Failed to query Neo4j for graph data")
                return None
            
            # Create NetworkX graph
            graph = nx.Graph()
            
            # Add nodes
            for record in nodes_result.data:
                node_id = str(record["node_id"])
                labels = record.get("labels", [])
                properties = record.get("properties", {})
                
                graph.add_node(node_id, 
                             labels=labels,
                             entity_type=labels[0] if labels else "UNKNOWN",
                             **properties)
            
            # Add edges
            for record in edges_result.data:
                source = str(record["source"])
                target = str(record["target"])
                rel_type = record.get("rel_type", "RELATED")
                properties = record.get("properties", {})
                
                if source in graph.nodes and target in graph.nodes:
                    graph.add_edge(source, target,
                                 relationship_type=rel_type,
                                 **properties)
            
            logger.info(f"Loaded graph from Neo4j: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error loading from Neo4j: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from NetworkX data format"""
        try:
            if "nodes" in graph_data and "edges" in graph_data:
                graph = nx.Graph()
                
                # Add nodes
                for node_data in graph_data["nodes"]:
                    node_id = node_data.get("id")
                    if node_id:
                        graph.add_node(node_id, **{k: v for k, v in node_data.items() if k != "id"})
                
                # Add edges
                for edge_data in graph_data["edges"]:
                    source = edge_data.get("source")
                    target = edge_data.get("target")
                    if source and target:
                        graph.add_edge(source, target, **{k: v for k, v in edge_data.items() 
                                                       if k not in ["source", "target"]})
                
                return graph
            else:
                logger.error("NetworkX data must contain 'nodes' and 'edges' keys")
                return None
                
        except Exception as e:
            logger.error(f"Error loading NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        try:
            if "edges" not in graph_data:
                logger.error("Edge list data must contain 'edges' key")
                return None
            
            graph = nx.Graph()
            
            for edge in graph_data["edges"]:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 else 1.0
                    graph.add_edge(source, target, weight=weight)
                elif isinstance(edge, dict):
                    source = edge.get("source")
                    target = edge.get("target")
                    if source and target:
                        graph.add_edge(source, target, **{k: v for k, v in edge.items() 
                                                       if k not in ["source", "target"]})
            
            # Add node attributes if provided
            if "nodes" in graph_data:
                for node_data in graph_data["nodes"]:
                    node_id = node_data.get("id")
                    if node_id in graph.nodes:
                        graph.nodes[node_id].update({k: v for k, v in node_data.items() if k != "id"})
            
            return graph
            
        except Exception as e:
            logger.error(f"Error loading edge list: {e}")
            return None
    
    def _load_from_adjacency_matrix(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        try:
            if "matrix" not in graph_data:
                logger.error("Adjacency matrix data must contain 'matrix' key")
                return None
            
            matrix = np.array(graph_data["matrix"])
            node_labels = graph_data.get("node_labels", [f"node_{i}" for i in range(len(matrix))])
            
            # Create graph from adjacency matrix
            graph = nx.from_numpy_array(matrix)
            
            # Relabel nodes if labels provided
            if len(node_labels) == len(graph.nodes):
                mapping = {i: label for i, label in enumerate(node_labels)}
                graph = nx.relabel_nodes(graph, mapping)
            
            return graph
            
        except Exception as e:
            logger.error(f"Error loading adjacency matrix: {e}")
            return None
    
    def apply_filters(self, graph: nx.Graph, filter_criteria: Dict[str, Any]) -> nx.Graph:
        """Apply filters to reduce graph size and focus on relevant data"""
        try:
            filtered_graph = graph.copy()
            
            # Filter by node attributes
            if "node_filters" in filter_criteria:
                nodes_to_remove = []
                for node, data in filtered_graph.nodes(data=True):
                    for attr, value in filter_criteria["node_filters"].items():
                        if attr in data:
                            if isinstance(value, list):
                                if data[attr] not in value:
                                    nodes_to_remove.append(node)
                                    break
                            elif data[attr] != value:
                                nodes_to_remove.append(node)
                                break
                
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            # Filter by edge attributes
            if "edge_filters" in filter_criteria:
                edges_to_remove = []
                for source, target, data in filtered_graph.edges(data=True):
                    for attr, value in filter_criteria["edge_filters"].items():
                        if attr in data:
                            if isinstance(value, list):
                                if data[attr] not in value:
                                    edges_to_remove.append((source, target))
                                    break
                            elif data[attr] != value:
                                edges_to_remove.append((source, target))
                                break
                
                filtered_graph.remove_edges_from(edges_to_remove)
            
            # Filter by degree
            if "min_degree" in filter_criteria:
                min_degree = filter_criteria["min_degree"]
                nodes_to_remove = [node for node, degree in dict(filtered_graph.degree()).items() 
                                 if degree < min_degree]
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            # Limit graph size
            max_nodes = filter_criteria.get("max_nodes")
            if max_nodes and len(filtered_graph.nodes) > max_nodes:
                # Keep highest degree nodes
                nodes_by_degree = sorted(filtered_graph.degree(), key=lambda x: x[1], reverse=True)
                nodes_to_keep = [node for node, degree in nodes_by_degree[:max_nodes]]
                nodes_to_remove = set(filtered_graph.nodes) - set(nodes_to_keep)
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            logger.info(f"Filtered graph: {len(graph.nodes)} -> {len(filtered_graph.nodes)} nodes, "
                       f"{len(graph.edges)} -> {len(filtered_graph.edges)} edges")
            
            return filtered_graph
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return graph