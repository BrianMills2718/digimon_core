"""Graph Data Loader for Clustering

Load graph data from various sources for clustering analysis.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import networkx as nx
import numpy as np

from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class GraphDataLoader(BaseNeo4jTool):
    """Load graph data from various sources"""
    
    def __init__(self, service_manager=None):
        super().__init__(service_manager)
        self.tool_id = "GRAPH_DATA_LOADER"
    
    def load_graph_data(self, input_data: Dict[str, Any]) -> Optional[nx.Graph]:
        """Load graph data from various sources"""
        try:
            data_source = input_data.get("data_source", "neo4j")
            
            if data_source == "neo4j":
                neo4j_config = input_data.get("neo4j_config", {})
                return self._load_from_neo4j(neo4j_config)
            
            elif data_source == "networkx":
                graph_data = input_data.get("graph_data", {})
                return self._load_from_networkx_data(graph_data)
            
            elif data_source == "edge_list":
                edges = input_data.get("edges", [])
                return self._load_from_edge_list(edges)
            
            elif data_source == "adjacency_matrix":
                adj_matrix = input_data.get("adjacency_matrix")
                return self._load_from_adjacency_matrix(adj_matrix)
            
            elif data_source == "mock":
                return self._create_mock_graph()
            
            else:
                logger.error(f"Unsupported data source: {data_source}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load graph data: {e}")
            return None
    
    def _load_from_neo4j(self, neo4j_config: Dict[str, Any]) -> Optional[nx.Graph]:
        """Load graph from Neo4j database"""
        try:
            # Default Neo4j query to get all entities and relationships
            entity_query = neo4j_config.get("entity_query", """
                MATCH (e:Entity)
                RETURN e.entity_id as id, e.name as name, e.type as type,
                       e.confidence as confidence
                LIMIT 1000
            """)
            
            relationship_query = neo4j_config.get("relationship_query", """
                MATCH (e1:Entity)-[r:RELATIONSHIP]->(e2:Entity)
                RETURN e1.entity_id as source, e2.entity_id as target,
                       r.type as relationship_type, r.confidence as confidence
                LIMIT 5000
            """)
            
            # Execute queries
            entities = self.neo4j_manager.execute_query(entity_query)
            relationships = self.neo4j_manager.execute_query(relationship_query)
            
            # Build NetworkX graph
            graph = nx.Graph()
            
            # Add nodes
            for entity in entities:
                node_id = entity.get("id", entity.get("name"))
                graph.add_node(node_id, **{k: v for k, v in entity.items() if k != "id"})
            
            # Add edges
            for rel in relationships:
                source = rel.get("source")
                target = rel.get("target")
                if source and target:
                    edge_attrs = {k: v for k, v in rel.items() if k not in ["source", "target"]}
                    graph.add_edge(source, target, **edge_attrs)
            
            logger.info(f"Loaded graph from Neo4j: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load from Neo4j: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict[str, Any]) -> Optional[nx.Graph]:
        """Load graph from NetworkX data format"""
        try:
            graph = nx.Graph()
            
            # Add nodes
            nodes = graph_data.get("nodes", [])
            for node_data in nodes:
                if isinstance(node_data, dict):
                    node_id = node_data.pop("id", node_data.pop("name", str(len(graph.nodes))))
                    graph.add_node(node_id, **node_data)
                else:
                    graph.add_node(node_data)
            
            # Add edges
            edges = graph_data.get("edges", [])
            for edge_data in edges:
                if isinstance(edge_data, dict):
                    source = edge_data.pop("source")
                    target = edge_data.pop("target")
                    graph.add_edge(source, target, **edge_data)
                elif isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                    graph.add_edge(edge_data[0], edge_data[1])
            
            logger.info(f"Loaded NetworkX graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, edges: List[Union[Tuple, List, Dict]]) -> Optional[nx.Graph]:
        """Load graph from edge list"""
        try:
            graph = nx.Graph()
            
            for edge in edges:
                if isinstance(edge, dict):
                    source = edge.get("source")
                    target = edge.get("target")
                    weight = edge.get("weight", 1.0)
                    if source and target:
                        graph.add_edge(source, target, weight=weight)
                
                elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 else 1.0
                    graph.add_edge(source, target, weight=weight)
            
            logger.info(f"Loaded edge list graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load edge list: {e}")
            return None
    
    def _load_from_adjacency_matrix(self, adj_matrix: Union[List[List], np.ndarray]) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix"""
        try:
            if isinstance(adj_matrix, list):
                adj_matrix = np.array(adj_matrix)
            
            graph = nx.from_numpy_array(adj_matrix)
            
            logger.info(f"Loaded adjacency matrix graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load adjacency matrix: {e}")
            return None
    
    def _create_mock_graph(self) -> nx.Graph:
        """Create a mock graph for testing"""
        try:
            # Create a graph with known community structure
            graph = nx.Graph()
            
            # Community 1: nodes 0-9
            for i in range(10):
                for j in range(i + 1, 10):
                    if np.random.random() < 0.7:  # High intra-community density
                        graph.add_edge(f"node_{i}", f"node_{j}")
            
            # Community 2: nodes 10-19
            for i in range(10, 20):
                for j in range(i + 1, 20):
                    if np.random.random() < 0.7:
                        graph.add_edge(f"node_{i}", f"node_{j}")
            
            # Community 3: nodes 20-29
            for i in range(20, 30):
                for j in range(i + 1, 30):
                    if np.random.random() < 0.7:
                        graph.add_edge(f"node_{i}", f"node_{j}")
            
            # Inter-community edges (sparse)
            for i in range(0, 10):
                for j in range(10, 20):
                    if np.random.random() < 0.1:
                        graph.add_edge(f"node_{i}", f"node_{j}")
            
            for i in range(10, 20):
                for j in range(20, 30):
                    if np.random.random() < 0.1:
                        graph.add_edge(f"node_{i}", f"node_{j}")
            
            logger.info(f"Created mock graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to create mock graph: {e}")
            return nx.Graph()  # Return empty graph as fallback