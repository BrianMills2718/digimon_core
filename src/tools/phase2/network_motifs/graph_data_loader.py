"""Network Motifs Graph Data Loader

Handles loading graph data from various sources for motif detection.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class NetworkMotifsDataLoader:
    """Load and prepare graph data for motif detection"""
    
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
                logger.info("Neo4j connection initialized for motif analysis")
        except Exception as e:
            logger.warning(f"Neo4j connection not available: {e}")
            self.neo4j_tool = None
    
    def load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None, 
                       directed: bool = False) -> Optional[nx.Graph]:
        """Load graph data from specified source"""
        try:
            if graph_source == "neo4j":
                return self._load_from_neo4j(directed)
            elif graph_source == "networkx":
                return self._load_from_networkx_data(graph_data, directed)
            elif graph_source == "edge_list":
                return self._load_from_edge_list(graph_data, directed)
            elif graph_source == "adjacency_matrix":
                return self._load_from_adjacency_matrix(graph_data, directed)
            else:
                logger.error(f"Unsupported graph source: {graph_source}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load graph data: {e}")
            return None
    
    def _load_from_neo4j(self, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph data from Neo4j database"""
        try:
            if not self.neo4j_tool:
                logger.error("Neo4j connection not available")
                return None
            
            # Get nodes and relationships
            with self.neo4j_tool.get_driver().session() as session:
                # Get all nodes
                nodes_result = session.run("""
                    MATCH (n)
                    RETURN n.entity_id as id, labels(n) as labels, properties(n) as properties
                    LIMIT 10000
                """)
                
                # Get all relationships
                edges_result = session.run("""
                    MATCH (a)-[r]->(b)
                    RETURN a.entity_id as source, b.entity_id as target, 
                           type(r) as relationship_type, properties(r) as properties
                    LIMIT 50000
                """)
                
                # Create NetworkX graph
                if directed:
                    graph = nx.DiGraph()
                else:
                    graph = nx.Graph()
                
                # Add nodes
                for record in nodes_result:
                    node_id = record["id"]
                    if node_id:
                        graph.add_node(node_id, 
                                     labels=record["labels"],
                                     **record["properties"])
                
                # Add edges
                for record in edges_result:
                    source = record["source"]
                    target = record["target"]
                    if source and target:
                        graph.add_edge(source, target,
                                     relationship_type=record["relationship_type"],
                                     **record["properties"])
                
                logger.info(f"Loaded graph from Neo4j: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
                return graph
                
        except Exception as e:
            logger.error(f"Failed to load from Neo4j: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from NetworkX compatible data format"""
        try:
            if directed:
                graph = nx.DiGraph()
            else:
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
                        attrs = {}
                        if len(edge_data) > 2 and isinstance(edge_data[2], dict):
                            attrs = edge_data[2]
                        graph.add_edge(source, target, **attrs)
                    elif isinstance(edge_data, dict):
                        source = edge_data.get("source")
                        target = edge_data.get("target")
                        if source and target:
                            attrs = {k: v for k, v in edge_data.items() 
                                   if k not in ["source", "target"]}
                            graph.add_edge(source, target, **attrs)
            
            logger.info(f"Loaded NetworkX graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        try:
            if directed:
                graph = nx.DiGraph()
            else:
                graph = nx.Graph()
            
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
    
    def _load_from_adjacency_matrix(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        try:
            matrix = graph_data.get("matrix", [])
            nodes = graph_data.get("nodes", [])
            
            if not matrix:
                logger.error("No matrix data provided")
                return None
            
            # Convert to numpy array
            adj_matrix = np.array(matrix)
            
            # Create graph from adjacency matrix
            if directed:
                graph = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph())
            else:
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
    
    def validate_graph_for_motifs(self, graph: nx.Graph) -> Dict[str, Any]:
        """Validate graph suitability for motif detection"""
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
                validation_result["errors"].append("Graph must have at least 3 nodes for motif detection")
            
            if num_edges < 2:
                validation_result["valid"] = False
                validation_result["errors"].append("Graph must have at least 2 edges for motif detection")
            
            # Check for isolated nodes
            isolated_nodes = list(nx.isolates(graph))
            if isolated_nodes:
                validation_result["warnings"].append(f"Graph has {len(isolated_nodes)} isolated nodes")
            
            # Check connectivity
            if not graph.is_directed():
                if not nx.is_connected(graph):
                    components = list(nx.connected_components(graph))
                    validation_result["warnings"].append(f"Graph is not connected ({len(components)} components)")
            else:
                if not nx.is_weakly_connected(graph):
                    components = list(nx.weakly_connected_components(graph))
                    validation_result["warnings"].append(f"Graph is not weakly connected ({len(components)} components)")
            
            # Check graph size for performance
            if num_nodes > 10000:
                validation_result["warnings"].append("Large graph may impact performance")
            
            if num_edges > 50000:
                validation_result["warnings"].append("Dense graph may impact performance")
            
            validation_result["graph_info"] = {
                "nodes": num_nodes,
                "edges": num_edges,
                "directed": graph.is_directed(),
                "density": nx.density(graph),
                "isolated_nodes": len(isolated_nodes)
            }
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
                "graph_info": {}
            }