"""Community Detection Graph Data Loader

Handles loading graph data from various sources for community detection.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CommunityGraphDataLoader:
    """Load and prepare graph data for community detection"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
    
    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection if available"""
        try:
            if self.service_manager and hasattr(self.service_manager, 'neo4j_service'):
                from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
                self.neo4j_tool = BaseNeo4jTool(self.service_manager)
                logger.info("Neo4j connection initialized for community detection")
        except Exception as e:
            logger.warning(f"Neo4j connection not available: {e}")
            self.neo4j_tool = None
    
    def load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None) -> Optional[nx.Graph]:
        """Load graph data from specified source for community detection"""
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
            logger.error(f"Failed to load graph data: {e}")
            return None
    
    def _load_from_neo4j(self) -> Optional[nx.Graph]:
        """Load graph data from Neo4j database"""
        try:
            if not self.neo4j_tool:
                logger.error("Neo4j connection not available")
                return None
            
            with self.neo4j_tool.get_driver().session() as session:
                # Get all nodes with their properties
                nodes_result = session.run("""
                    MATCH (n)
                    RETURN n.entity_id as id, labels(n) as labels, properties(n) as properties
                    LIMIT 10000
                """)
                
                # Get all relationships with their properties
                edges_result = session.run("""
                    MATCH (a)-[r]->(b)
                    RETURN a.entity_id as source, b.entity_id as target, 
                           type(r) as relationship_type, properties(r) as properties
                    LIMIT 50000
                """)
                
                # Create undirected graph for community detection (most algorithms work better on undirected)
                graph = nx.Graph()
                
                # Add nodes with attributes
                for record in nodes_result:
                    node_id = record["id"]
                    if node_id:
                        graph.add_node(node_id, 
                                     labels=record["labels"],
                                     **record["properties"])
                
                # Add edges with attributes
                for record in edges_result:
                    source = record["source"]
                    target = record["target"]
                    if source and target:
                        edge_attrs = record["properties"] or {}
                        edge_attrs["relationship_type"] = record["relationship_type"]
                        # Add default weight if not present
                        if "weight" not in edge_attrs:
                            edge_attrs["weight"] = 1.0
                        graph.add_edge(source, target, **edge_attrs)
                
                logger.info(f"Loaded graph from Neo4j: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
                return graph
                
        except Exception as e:
            logger.error(f"Failed to load from Neo4j: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from NetworkX compatible data format"""
        try:
            # Default to undirected graph for community detection
            graph = nx.Graph()
            
            # Add nodes
            if "nodes" in graph_data:
                for node_data in graph_data["nodes"]:
                    if isinstance(node_data, str):
                        graph.add_node(node_data)
                    elif isinstance(node_data, dict):
                        node_id = node_data.get("id")
                        if node_id:
                            attrs = {k: v for k, v in node_data.items() if k != "id"}
                            graph.add_node(node_id, **attrs)
            
            # Add edges
            if "edges" in graph_data:
                for edge_data in graph_data["edges"]:
                    if isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                        source, target = edge_data[0], edge_data[1]
                        weight = edge_data[2] if len(edge_data) > 2 else 1.0
                        graph.add_edge(source, target, weight=weight)
                    elif isinstance(edge_data, dict):
                        source = edge_data.get("source")
                        target = edge_data.get("target")
                        if source and target:
                            attrs = {k: v for k, v in edge_data.items() 
                                   if k not in ["source", "target"]}
                            if "weight" not in attrs:
                                attrs["weight"] = 1.0
                            graph.add_edge(source, target, **attrs)
            
            logger.info(f"Loaded NetworkX graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        try:
            graph = nx.Graph()  # Undirected for community detection
            edges = graph_data.get("edges", [])
            
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = str(edge[0]), str(edge[1])
                    weight = edge[2] if len(edge) > 2 else 1.0
                    graph.add_edge(source, target, weight=weight)
                elif isinstance(edge, dict):
                    source = str(edge.get("source", ""))
                    target = str(edge.get("target", ""))
                    weight = edge.get("weight", 1.0)
                    if source and target:
                        graph.add_edge(source, target, weight=weight)
            
            logger.info(f"Loaded edge list graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load edge list: {e}")
            return None
    
    def _load_from_adjacency_matrix(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        try:
            matrix = graph_data.get("matrix", [])
            nodes = graph_data.get("nodes", [])
            
            if not matrix:
                logger.error("No matrix data provided")
                return None
            
            # Convert to numpy array
            adj_matrix = np.array(matrix)
            
            # Create undirected graph from adjacency matrix
            graph = nx.from_numpy_array(adj_matrix, create_using=nx.Graph())
            
            # Relabel nodes if provided
            if nodes and len(nodes) == len(graph.nodes):
                mapping = {i: str(nodes[i]) for i in range(len(nodes))}
                graph = nx.relabel_nodes(graph, mapping)
            else:
                # Use string node IDs
                mapping = {i: str(i) for i in graph.nodes}
                graph = nx.relabel_nodes(graph, mapping)
            
            logger.info(f"Loaded adjacency matrix graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load adjacency matrix: {e}")
            return None
    
    def validate_graph_for_communities(self, graph: nx.Graph) -> Dict[str, Any]:
        """Validate graph suitability for community detection"""
        try:
            validation_result = {
                "valid": True,
                "warnings": [],
                "errors": []
            }
            
            # Check basic graph properties
            num_nodes = len(graph.nodes)
            num_edges = len(graph.edges)
            
            if num_nodes < 3:
                validation_result["valid"] = False
                validation_result["errors"].append("Graph must have at least 3 nodes for community detection")
            
            if num_edges < 2:
                validation_result["valid"] = False
                validation_result["errors"].append("Graph must have at least 2 edges for community detection")
            
            # Check for isolated nodes
            isolated_nodes = list(nx.isolates(graph))
            if isolated_nodes:
                validation_result["warnings"].append(f"Graph has {len(isolated_nodes)} isolated nodes")
            
            # Check connectivity
            if not nx.is_connected(graph):
                components = list(nx.connected_components(graph))
                validation_result["warnings"].append(f"Graph is not connected ({len(components)} components)")
            
            # Check graph size for performance
            if num_nodes > 10000:
                validation_result["warnings"].append("Large graph may impact performance of some algorithms")
            
            if num_edges > 100000:
                validation_result["warnings"].append("Dense graph may impact performance")
            
            # Check for self-loops
            self_loops = list(nx.selfloop_edges(graph))
            if self_loops:
                validation_result["warnings"].append(f"Graph has {len(self_loops)} self-loops")
            
            # Check density
            density = nx.density(graph)
            if density > 0.5:
                validation_result["warnings"].append("Very dense graph may not have clear community structure")
            elif density < 0.001:
                validation_result["warnings"].append("Very sparse graph may have poor community detection")
            
            validation_result["graph_info"] = {
                "nodes": num_nodes,
                "edges": num_edges,
                "directed": graph.is_directed(),
                "density": density,
                "connected": nx.is_connected(graph),
                "isolated_nodes": len(isolated_nodes),
                "self_loops": len(self_loops),
                "components": nx.number_connected_components(graph)
            }
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
                "graph_info": {}
            }
    
    def prepare_graph_for_algorithm(self, graph: nx.Graph, algorithm: str) -> nx.Graph:
        """Prepare graph for specific community detection algorithm"""
        try:
            prepared_graph = graph.copy()
            
            # Convert to undirected for most algorithms
            if prepared_graph.is_directed():
                prepared_graph = prepared_graph.to_undirected()
            
            # Remove self-loops for most algorithms
            prepared_graph.remove_edges_from(nx.selfloop_edges(prepared_graph))
            
            # Add weight attributes if missing
            for u, v, data in prepared_graph.edges(data=True):
                if "weight" not in data:
                    data["weight"] = 1.0
            
            # Remove isolated nodes (they form trivial communities)
            isolated_nodes = list(nx.isolates(prepared_graph))
            if isolated_nodes:
                logger.info(f"Removing {len(isolated_nodes)} isolated nodes")
                prepared_graph.remove_nodes_from(isolated_nodes)
            
            return prepared_graph
            
        except Exception as e:
            logger.error(f"Graph preparation failed: {e}")
            return graph