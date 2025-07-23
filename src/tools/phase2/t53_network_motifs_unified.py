"""T53: Network Motifs Detection Tool - Advanced Graph Analytics

Real motif detection using NetworkX subgraph algorithms with statistical significance testing.
Part of Phase 2.1 Graph Analytics tools providing advanced network analysis capabilities.
"""

import time
import psutil
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
import networkx as nx
import numpy as np
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import itertools
import random

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
    from src.core.confidence_score import ConfidenceScore
except ImportError:
    from core.service_manager import ServiceManager
    from core.confidence_score import ConfidenceScore

# Import Neo4j integration
from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
from src.tools.phase1.neo4j_error_handler import Neo4jErrorHandler


class MotifType(Enum):
    """Supported motif types for detection"""
    TRIANGLES = "triangles"
    SQUARES = "squares"
    WEDGES = "wedges"
    FEED_FORWARD_LOOPS = "feed_forward_loops"
    BI_FANS = "bi_fans"
    THREE_CHAINS = "three_chains"
    FOUR_CHAINS = "four_chains"
    CLIQUES = "cliques"
    ALL = "all"


@dataclass
class MotifInstance:
    """Individual motif instance"""
    motif_type: str
    nodes: List[str]
    edges: List[Tuple[str, str]]
    pattern_id: str
    significance_score: float
    frequency: int


@dataclass
class MotifStats:
    """Network motif statistics"""
    total_motifs: int
    motif_types: Dict[str, int]
    significance_scores: Dict[str, float]
    enrichment_ratios: Dict[str, float]
    z_scores: Dict[str, float]
    p_values: Dict[str, float]
    random_baseline: Dict[str, float]


class NetworkMotifsDetectionTool(BaseTool):
    """T53: Advanced Network Motifs Detection Tool
    
    Implements real motif detection algorithms including triangle detection,
    feed-forward loops, bi-fans, and other structural patterns with statistical
    significance testing for academic research networks.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize network motifs detection tool with advanced capabilities"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T53_NETWORK_MOTIFS"
        self.name = "Advanced Network Motifs Detection"
        self.category = "advanced_analytics"
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Initialize Neo4j connection for graph data
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
        
        # Motif detection configurations
        self.motif_configs = {
            MotifType.TRIANGLES: {
                "size": 3,
                "pattern": "complete",
                "min_frequency": 1
            },
            MotifType.SQUARES: {
                "size": 4,
                "pattern": "cycle",
                "min_frequency": 1
            },
            MotifType.WEDGES: {
                "size": 3,
                "pattern": "path",
                "min_frequency": 1
            },
            MotifType.FEED_FORWARD_LOOPS: {
                "size": 3,
                "pattern": "feed_forward",
                "min_frequency": 1
            },
            MotifType.BI_FANS: {
                "size": 4,
                "pattern": "bi_fan",
                "min_frequency": 1
            },
            MotifType.THREE_CHAINS: {
                "size": 3,
                "pattern": "chain",
                "min_frequency": 1
            },
            MotifType.FOUR_CHAINS: {
                "size": 4,
                "pattern": "chain",
                "min_frequency": 1
            },
            MotifType.CLIQUES: {
                "size": "variable",
                "pattern": "complete",
                "min_frequency": 1,
                "max_size": 6
            }
        }
        
        # Random graph generation parameters for significance testing
        self.random_baseline_params = {
            "num_random_graphs": 100,
            "preserve_degree_sequence": True,
            "max_iterations": 1000
        }
    
    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection for graph data access"""
        try:
            self.neo4j_tool = BaseNeo4jTool()
        except Exception as e:
            print(f"Warning: Could not initialize Neo4j connection: {e}")
            self.neo4j_tool = None
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Advanced network motifs detection with statistical significance testing",
            category=self.category,
            input_schema={
                "type": "object",
                "properties": {
                    "graph_source": {
                        "type": "string",
                        "enum": ["neo4j", "networkx", "edge_list", "adjacency_matrix"],
                        "description": "Source of graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data when not using Neo4j"
                    },
                    "motif_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["triangles", "squares", "wedges", "feed_forward_loops", 
                                   "bi_fans", "three_chains", "four_chains", "cliques", "all"]
                        },
                        "default": ["triangles", "feed_forward_loops"]
                    },
                    "motif_sizes": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 3, "maximum": 8},
                        "default": [3, 4]
                    },
                    "significance_testing": {
                        "type": "boolean",
                        "default": True,
                        "description": "Perform statistical significance testing"
                    },
                    "num_random_graphs": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 1000,
                        "default": 100
                    },
                    "min_frequency": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 2
                    },
                    "directed": {
                        "type": "boolean",
                        "default": False,
                        "description": "Treat graph as directed"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "patterns_only"],
                        "default": "detailed"
                    },
                    "store_results": {
                        "type": "boolean",
                        "default": False,
                        "description": "Store motif results back to Neo4j"
                    }
                },
                "required": ["graph_source"],
                "additionalProperties": False
            },
            output_schema={
                "type": "object",
                "properties": {
                    "motif_instances": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "motif_type": {"type": "string"},
                                "nodes": {"type": "array", "items": {"type": "string"}},
                                "edges": {"type": "array"},
                                "pattern_id": {"type": "string"},
                                "significance_score": {"type": "number"},
                                "frequency": {"type": "integer"}
                            },
                            "required": ["motif_type", "nodes", "edges", "frequency"]
                        }
                    },
                    "motif_stats": {
                        "type": "object",
                        "properties": {
                            "total_motifs": {"type": "integer"},
                            "motif_types": {"type": "object"},
                            "significance_scores": {"type": "object"},
                            "enrichment_ratios": {"type": "object"},
                            "z_scores": {"type": "object"},
                            "p_values": {"type": "object"},
                            "random_baseline": {"type": "object"}
                        },
                        "required": ["total_motifs", "motif_types"]
                    },
                    "algorithm_info": {
                        "type": "object",
                        "properties": {
                            "motifs_detected": {"type": "array"},
                            "parameters": {"type": "object"},
                            "execution_time": {"type": "number"},
                            "significance_testing": {"type": "boolean"}
                        }
                    },
                    "pattern_catalog": {
                        "type": "object",
                        "description": "Catalog of unique patterns found"
                    }
                },
                "required": ["motif_instances", "motif_stats", "algorithm_info", "pattern_catalog"]
            },
            dependencies=["networkx", "numpy", "neo4j_service"],
            performance_requirements={
                "max_execution_time": 600.0,  # 10 minutes for large graphs with significance testing
                "max_memory_mb": 4000,  # 4GB for large academic networks
                "min_accuracy": 0.95  # High accuracy for motif detection
            },
            error_conditions=[
                "INVALID_GRAPH_DATA",
                "MOTIF_TYPE_NOT_SUPPORTED",
                "GRAPH_TOO_LARGE",
                "SIGNIFICANCE_TESTING_FAILED",
                "NEO4J_CONNECTION_ERROR",
                "INSUFFICIENT_NODES",
                "MEMORY_LIMIT_EXCEEDED",
                "SUBGRAPH_ENUMERATION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute network motifs detection with real algorithms"""
        self._start_execution()
        
        try:
            # Validate input against contract
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(request, "INVALID_INPUT", validation_result["error"])
            
            # Extract parameters
            graph_source = request.input_data["graph_source"]
            motif_types = [MotifType(mt) for mt in request.input_data.get("motif_types", ["triangles", "feed_forward_loops"])]
            motif_sizes = request.input_data.get("motif_sizes", [3, 4])
            significance_testing = request.input_data.get("significance_testing", True)
            num_random_graphs = request.input_data.get("num_random_graphs", 100)
            min_frequency = request.input_data.get("min_frequency", 2)
            directed = request.input_data.get("directed", False)
            output_format = request.input_data.get("output_format", "detailed")
            store_results = request.input_data.get("store_results", False)
            
            # Load graph data
            graph = self._load_graph_data(graph_source, request.input_data.get("graph_data"), directed)
            if graph is None:
                return self._create_error_result(request, "INVALID_GRAPH_DATA", "Failed to load graph data")
            
            # Validate graph size - check if we have enough nodes for the motifs we're trying to detect
            min_nodes_needed = 3  # Most motifs need at least 3 nodes
            if motif_types:
                for motif_type in motif_types:
                    if motif_type in [MotifType.SQUARES, MotifType.BI_FANS, MotifType.FOUR_CHAINS]:
                        min_nodes_needed = max(min_nodes_needed, 4)
                    elif motif_type == MotifType.CLIQUES and motif_sizes:
                        min_nodes_needed = max(min_nodes_needed, max(motif_sizes))
            
            if len(graph.nodes()) < min_nodes_needed:
                return self._create_error_result(
                    request, "INSUFFICIENT_NODES", 
                    f"Graph must have at least {min_nodes_needed} nodes for requested motif types"
                )
            
            if len(graph.nodes()) > 50000:  # Large graph threshold for motif detection
                return self._create_error_result(request, "GRAPH_TOO_LARGE", "Graph too large for motif detection")
            
            # Detect motifs
            motif_instances, algorithm_info = self._detect_motifs(
                graph, motif_types, motif_sizes, min_frequency
            )
            
            # Perform significance testing if requested
            motif_stats = None
            if significance_testing:
                motif_stats = self._calculate_motif_significance(
                    graph, motif_instances, num_random_graphs
                )
            else:
                motif_stats = self._calculate_basic_motif_stats(motif_instances)
            
            # Generate pattern catalog
            pattern_catalog = self._generate_pattern_catalog(motif_instances)
            
            # Store results to Neo4j if requested
            storage_info = {}
            if store_results and self.neo4j_tool:
                storage_info = self._store_motif_results(motif_instances, algorithm_info)
            
            # Calculate academic confidence
            confidence = self._calculate_academic_confidence(motif_stats, algorithm_info)
            
            # Performance monitoring
            execution_time, memory_used = self._end_execution()
            
            # Prepare result data based on output format
            result_data = self._format_output(
                motif_instances, motif_stats, algorithm_info,
                pattern_catalog, output_format
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "academic_ready": True,
                    "motifs_detected": [mt.value for mt in motif_types],
                    "statistical_significance": confidence,
                    "batch_processed": len(graph.nodes()) > 1000,
                    "graph_size": len(graph.nodes()),
                    "edge_count": len(graph.edges()),
                    "directed": directed,
                    "significance_testing": significance_testing,
                    "storage_info": storage_info,
                    "publication_ready": True
                }
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Advanced validation for motif detection input"""
        try:
            # Basic type checking
            if not isinstance(input_data, dict):
                return {"valid": False, "error": "Input must be a dictionary"}
            
            # Required fields
            if "graph_source" not in input_data:
                return {"valid": False, "error": "graph_source is required"}
            
            # Validate graph source
            valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
            if input_data["graph_source"] not in valid_sources:
                return {"valid": False, "error": f"graph_source must be one of {valid_sources}"}
            
            # Validate motif types if provided
            if "motif_types" in input_data:
                valid_motif_types = [mt.value for mt in MotifType]
                for motif_type in input_data["motif_types"]:
                    if motif_type not in valid_motif_types:
                        return {"valid": False, "error": f"motif_type '{motif_type}' not supported. Valid types: {valid_motif_types}"}
            
            # Validate motif sizes
            if "motif_sizes" in input_data:
                sizes = input_data["motif_sizes"]
                if not isinstance(sizes, list) or not all(isinstance(s, int) and 3 <= s <= 8 for s in sizes):
                    return {"valid": False, "error": "motif_sizes must be a list of integers between 3 and 8"}
            
            # Validate random graph parameters
            if "num_random_graphs" in input_data:
                num_random = input_data["num_random_graphs"]
                if not isinstance(num_random, int) or not (1 <= num_random <= 1000):
                    return {"valid": False, "error": "num_random_graphs must be an integer between 1 and 1000"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None, 
                        directed: bool = False) -> Optional[nx.Graph]:
        """Load graph data from various sources"""
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
                return None
                
        except Exception as e:
            print(f"Error loading graph data: {e}")
            return None
    
    def _load_from_neo4j(self, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from Neo4j database"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return None
        
        try:
            with self.neo4j_tool.driver.session() as session:
                # Load nodes
                nodes_result = session.run("""
                MATCH (n:Entity)
                RETURN n.entity_id as id, n.canonical_name as name, 
                       n.entity_type as type, n.pagerank_score as pagerank
                """)
                
                # Load edges
                edges_result = session.run("""
                MATCH (a:Entity)-[r]->(b:Entity)
                RETURN a.entity_id as source, b.entity_id as target, 
                       r.weight as weight, type(r) as relationship_type
                """)
                
                # Create NetworkX graph
                G = nx.DiGraph() if directed else nx.Graph()
                
                # Add nodes with attributes
                for record in nodes_result:
                    G.add_node(
                        record["id"],
                        name=record["name"],
                        type=record["type"],
                        pagerank=record["pagerank"] or 0.0
                    )
                
                # Add edges with attributes
                for record in edges_result:
                    G.add_edge(
                        record["source"],
                        record["target"],
                        weight=record["weight"] or 1.0,
                        relationship_type=record["relationship_type"]
                    )
                
                return G
                
        except Exception as e:
            print(f"Error loading from Neo4j: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from NetworkX data format"""
        if not graph_data or "nodes" not in graph_data or "edges" not in graph_data:
            return None
        
        try:
            G = nx.DiGraph() if directed else nx.Graph()
            
            # Add nodes
            for node_data in graph_data["nodes"]:
                if isinstance(node_data, dict):
                    node_id = node_data.get("id")
                    attributes = {k: v for k, v in node_data.items() if k != "id"}
                    G.add_node(node_id, **attributes)
                else:
                    G.add_node(node_data)
            
            # Add edges
            for edge_data in graph_data["edges"]:
                if isinstance(edge_data, dict):
                    source = edge_data.get("source")
                    target = edge_data.get("target")
                    weight = edge_data.get("weight", 1.0)
                    G.add_edge(source, target, weight=weight)
                elif isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                    G.add_edge(edge_data[0], edge_data[1])
            
            return G
            
        except Exception as e:
            print(f"Error loading NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        if not graph_data or "edges" not in graph_data:
            return None
        
        try:
            G = nx.DiGraph() if directed else nx.Graph()
            
            for edge in graph_data["edges"]:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 else 1.0
                    G.add_edge(source, target, weight=weight)
                elif isinstance(edge, dict):
                    source = edge.get("source")
                    target = edge.get("target")
                    weight = edge.get("weight", 1.0)
                    if source and target:
                        G.add_edge(source, target, weight=weight)
            
            return G
            
        except Exception as e:
            print(f"Error loading edge list: {e}")
            return None
    
    def _load_from_adjacency_matrix(self, graph_data: Dict, directed: bool = False) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        if not graph_data or "matrix" not in graph_data:
            return None
        
        try:
            matrix = np.array(graph_data["matrix"])
            node_labels = graph_data.get("node_labels", list(range(len(matrix))))
            
            if directed:
                G = nx.from_numpy_array(matrix, create_using=nx.DiGraph)
            else:
                G = nx.from_numpy_array(matrix)
            
            # Relabel nodes if labels provided
            if len(node_labels) == len(matrix):
                mapping = {i: label for i, label in enumerate(node_labels)}
                G = nx.relabel_nodes(G, mapping)
            
            return G
            
        except Exception as e:
            print(f"Error loading adjacency matrix: {e}")
            return None
    
    def _detect_motifs(self, graph: nx.Graph, motif_types: List[MotifType], 
                      motif_sizes: List[int], min_frequency: int) -> Tuple[List[MotifInstance], Dict[str, Any]]:
        """Perform comprehensive motif detection"""
        start_time = time.time()
        all_motif_instances = []
        
        try:
            for motif_type in motif_types:
                if motif_type == MotifType.ALL:
                    # Detect all motif types
                    for specific_type in MotifType:
                        if specific_type != MotifType.ALL:
                            instances = self._detect_specific_motif(graph, specific_type, motif_sizes, min_frequency)
                            all_motif_instances.extend(instances)
                else:
                    instances = self._detect_specific_motif(graph, motif_type, motif_sizes, min_frequency)
                    all_motif_instances.extend(instances)
            
            execution_time = time.time() - start_time
            
            algorithm_info = {
                "motifs_detected": [mt.value for mt in motif_types],
                "parameters": {
                    "motif_sizes": motif_sizes,
                    "min_frequency": min_frequency,
                    "directed": isinstance(graph, nx.DiGraph)
                },
                "execution_time": execution_time,
                "total_instances": len(all_motif_instances)
            }
            
            return all_motif_instances, algorithm_info
            
        except Exception as e:
            raise RuntimeError(f"Motif detection failed: {str(e)}")
    
    def _detect_specific_motif(self, graph: nx.Graph, motif_type: MotifType, 
                             motif_sizes: List[int], min_frequency: int) -> List[MotifInstance]:
        """Detect specific type of motifs"""
        instances = []
        
        try:
            if motif_type == MotifType.TRIANGLES:
                instances = self._detect_triangles(graph, min_frequency)
            elif motif_type == MotifType.SQUARES:
                instances = self._detect_squares(graph, min_frequency)
            elif motif_type == MotifType.WEDGES:
                instances = self._detect_wedges(graph, min_frequency)
            elif motif_type == MotifType.FEED_FORWARD_LOOPS:
                instances = self._detect_feed_forward_loops(graph, min_frequency)
            elif motif_type == MotifType.BI_FANS:
                instances = self._detect_bi_fans(graph, min_frequency)
            elif motif_type == MotifType.THREE_CHAINS:
                instances = self._detect_chains(graph, 3, min_frequency)
            elif motif_type == MotifType.FOUR_CHAINS:
                instances = self._detect_chains(graph, 4, min_frequency)
            elif motif_type == MotifType.CLIQUES:
                instances = self._detect_cliques(graph, motif_sizes, min_frequency)
            
            return instances
            
        except Exception as e:
            print(f"Error detecting {motif_type.value}: {e}")
            return []
    
    def _detect_triangles(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect triangle motifs using NetworkX"""
        instances = []
        triangles = list(nx.enumerate_all_cliques(graph))
        triangle_3 = [clique for clique in triangles if len(clique) == 3]
        
        for i, triangle in enumerate(triangle_3):
            edges = [(triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[0], triangle[2])]
            # Filter to actual edges in graph
            actual_edges = [(u, v) for u, v in edges if graph.has_edge(u, v)]
            
            if len(actual_edges) >= 2:  # At least 2 edges for a meaningful pattern
                instances.append(MotifInstance(
                    motif_type="triangles",
                    nodes=list(triangle),
                    edges=actual_edges,
                    pattern_id=f"triangle_{i}",
                    significance_score=0.0,  # Will be calculated in significance testing
                    frequency=1
                ))
        
        return instances
    
    def _detect_squares(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect square (4-cycle) motifs"""
        instances = []
        
        # Find 4-cycles using NetworkX
        try:
            cycles = list(nx.simple_cycles(graph.to_directed(), length_bound=4))
            four_cycles = [cycle for cycle in cycles if len(cycle) == 4]
            
            for i, cycle in enumerate(four_cycles):
                edges = [(cycle[j], cycle[(j+1) % 4]) for j in range(4)]
                actual_edges = [(u, v) for u, v in edges if graph.has_edge(u, v)]
                
                if len(actual_edges) >= 3:  # At least 3 edges for a square-like pattern
                    instances.append(MotifInstance(
                        motif_type="squares",
                        nodes=list(cycle),
                        edges=actual_edges,
                        pattern_id=f"square_{i}",
                        significance_score=0.0,
                        frequency=1
                    ))
        except:
            # Fallback to manual detection for undirected graphs
            for nodes in itertools.combinations(graph.nodes(), 4):
                subgraph = graph.subgraph(nodes)
                if subgraph.number_of_edges() == 4 and nx.is_connected(subgraph):
                    # Check if it forms a cycle
                    try:
                        cycle = nx.find_cycle(subgraph)
                        if len(cycle) == 4:
                            instances.append(MotifInstance(
                                motif_type="squares",
                                nodes=list(nodes),
                                edges=list(subgraph.edges()),
                                pattern_id=f"square_{len(instances)}",
                                significance_score=0.0,
                                frequency=1
                            ))
                    except nx.NetworkXNoCycle:
                        continue
        
        return instances
    
    def _detect_wedges(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect wedge (path of length 2) motifs"""
        instances = []
        
        # A wedge is a path of length 2: A-B-C
        for center_node in graph.nodes():
            neighbors = list(graph.neighbors(center_node))
            if len(neighbors) >= 2:
                for i, neighbor1 in enumerate(neighbors):
                    for neighbor2 in neighbors[i+1:]:
                        # Ensure neighbor1 and neighbor2 are not connected (pure wedge)
                        if not graph.has_edge(neighbor1, neighbor2):
                            edges = [(neighbor1, center_node), (center_node, neighbor2)]
                            instances.append(MotifInstance(
                                motif_type="wedges",
                                nodes=[neighbor1, center_node, neighbor2],
                                edges=edges,
                                pattern_id=f"wedge_{len(instances)}",
                                significance_score=0.0,
                                frequency=1
                            ))
        
        return instances
    
    def _detect_feed_forward_loops(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect feed-forward loop motifs (directed graphs)"""
        instances = []
        
        if not isinstance(graph, nx.DiGraph):
            # Convert to directed for analysis
            graph = graph.to_directed()
        
        # Feed-forward loop: A->B, A->C, B->C
        for nodeA in graph.nodes():
            out_neighbors_A = set(graph.successors(nodeA))
            if len(out_neighbors_A) >= 2:
                for nodeB in out_neighbors_A:
                    for nodeC in out_neighbors_A:
                        if nodeB != nodeC and graph.has_edge(nodeB, nodeC):
                            # Found feed-forward loop
                            edges = [(nodeA, nodeB), (nodeA, nodeC), (nodeB, nodeC)]
                            instances.append(MotifInstance(
                                motif_type="feed_forward_loops",
                                nodes=[nodeA, nodeB, nodeC],
                                edges=edges,
                                pattern_id=f"ffl_{len(instances)}",
                                significance_score=0.0,
                                frequency=1
                            ))
        
        return instances
    
    def _detect_bi_fans(self, graph: nx.Graph, min_frequency: int) -> List[MotifInstance]:
        """Detect bi-fan motifs (2 nodes connected to 2 other nodes)"""
        instances = []
        
        # Bi-fan: Two nodes each connected to two other nodes
        for node_pair in itertools.combinations(graph.nodes(), 2):
            nodeA, nodeB = node_pair
            neighbors_A = set(graph.neighbors(nodeA))
            neighbors_B = set(graph.neighbors(nodeB))
            
            # Find common neighbors
            common_neighbors = neighbors_A.intersection(neighbors_B)
            if len(common_neighbors) >= 2:
                for target_pair in itertools.combinations(common_neighbors, 2):
                    nodeC, nodeD = target_pair
                    # Verify all connections exist
                    required_edges = [(nodeA, nodeC), (nodeA, nodeD), (nodeB, nodeC), (nodeB, nodeD)]
                    actual_edges = [(u, v) for u, v in required_edges if graph.has_edge(u, v)]
                    
                    if len(actual_edges) == 4:  # Perfect bi-fan
                        instances.append(MotifInstance(
                            motif_type="bi_fans",
                            nodes=[nodeA, nodeB, nodeC, nodeD],
                            edges=actual_edges,
                            pattern_id=f"bifan_{len(instances)}",
                            significance_score=0.0,
                            frequency=1
                        ))
        
        return instances
    
    def _detect_chains(self, graph: nx.Graph, chain_length: int, min_frequency: int) -> List[MotifInstance]:
        """Detect chain motifs of specified length"""
        instances = []
        
        # Find all simple paths of the specified length
        for start_node in graph.nodes():
            for end_node in graph.nodes():
                if start_node != end_node:
                    try:
                        paths = list(nx.all_simple_paths(graph, start_node, end_node, cutoff=chain_length-1))
                        for path in paths:
                            if len(path) == chain_length:
                                edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                                instances.append(MotifInstance(
                                    motif_type=f"{chain_length}_chains",
                                    nodes=path,
                                    edges=edges,
                                    pattern_id=f"chain_{chain_length}_{len(instances)}",
                                    significance_score=0.0,
                                    frequency=1
                                ))
                    except:
                        continue  # Skip if path finding fails
        
        return instances
    
    def _detect_cliques(self, graph: nx.Graph, motif_sizes: List[int], min_frequency: int) -> List[MotifInstance]:
        """Detect clique motifs of various sizes"""
        instances = []
        
        # Find all maximal cliques
        cliques = list(nx.find_cliques(graph))
        
        for size in motif_sizes:
            size_cliques = [clique for clique in cliques if len(clique) == size]
            for i, clique in enumerate(size_cliques):
                # Get all edges in the clique
                clique_subgraph = graph.subgraph(clique)
                edges = list(clique_subgraph.edges())
                
                instances.append(MotifInstance(
                    motif_type="cliques",
                    nodes=list(clique),
                    edges=edges,
                    pattern_id=f"clique_{size}_{i}",
                    significance_score=0.0,
                    frequency=1
                ))
        
        return instances
    
    def _calculate_motif_significance(self, graph: nx.Graph, motif_instances: List[MotifInstance], 
                                    num_random_graphs: int) -> MotifStats:
        """Calculate statistical significance of motifs using random graph comparison"""
        # Count observed motifs by type
        observed_counts = Counter(instance.motif_type for instance in motif_instances)
        
        # Generate random graphs and count motifs
        random_counts = defaultdict(list)
        
        for _ in range(num_random_graphs):
            try:
                # Generate random graph with same degree sequence
                random_graph = self._generate_random_graph(graph)
                
                # Detect motifs in random graph
                for motif_type in observed_counts.keys():
                    random_instances = self._detect_specific_motif(
                        random_graph, MotifType(motif_type), [3, 4, 5, 6], 1
                    )
                    random_counts[motif_type].append(len(random_instances))
            except:
                # If random graph generation fails, use simpler null model
                continue
        
        # Calculate statistics
        significance_scores = {}
        enrichment_ratios = {}
        z_scores = {}
        p_values = {}
        random_baseline = {}
        
        for motif_type, observed_count in observed_counts.items():
            if motif_type in random_counts and random_counts[motif_type]:
                random_values = random_counts[motif_type]
                mean_random = np.mean(random_values)
                std_random = np.std(random_values)
                
                random_baseline[motif_type] = mean_random
                
                if mean_random > 0:
                    enrichment_ratios[motif_type] = observed_count / mean_random
                else:
                    enrichment_ratios[motif_type] = float('inf') if observed_count > 0 else 1.0
                
                if std_random > 0:
                    z_scores[motif_type] = (observed_count - mean_random) / std_random
                    # Calculate p-value (two-tailed test)
                    p_values[motif_type] = 2 * (1 - abs(z_scores[motif_type]) / np.sqrt(2 * np.pi))
                else:
                    z_scores[motif_type] = 0.0
                    p_values[motif_type] = 1.0
                
                significance_scores[motif_type] = abs(z_scores[motif_type])
            else:
                significance_scores[motif_type] = 0.0
                enrichment_ratios[motif_type] = 1.0
                z_scores[motif_type] = 0.0
                p_values[motif_type] = 1.0
                random_baseline[motif_type] = 0.0
        
        return MotifStats(
            total_motifs=len(motif_instances),
            motif_types=dict(observed_counts),
            significance_scores=significance_scores,
            enrichment_ratios=enrichment_ratios,
            z_scores=z_scores,
            p_values=p_values,
            random_baseline=random_baseline
        )
    
    def _calculate_basic_motif_stats(self, motif_instances: List[MotifInstance]) -> MotifStats:
        """Calculate basic motif statistics without significance testing"""
        motif_type_counts = Counter(instance.motif_type for instance in motif_instances)
        
        return MotifStats(
            total_motifs=len(motif_instances),
            motif_types=dict(motif_type_counts),
            significance_scores={},
            enrichment_ratios={},
            z_scores={},
            p_values={},
            random_baseline={}
        )
    
    def _generate_random_graph(self, graph: nx.Graph) -> nx.Graph:
        """Generate random graph with same degree sequence"""
        try:
            # Try to preserve degree sequence
            degree_sequence = [d for n, d in graph.degree()]
            if isinstance(graph, nx.DiGraph):
                in_degree_sequence = [d for n, d in graph.in_degree()]
                out_degree_sequence = [d for n, d in graph.out_degree()]
                random_graph = nx.directed_configuration_model(in_degree_sequence, out_degree_sequence)
            else:
                random_graph = nx.configuration_model(degree_sequence)
                random_graph = nx.Graph(random_graph)  # Remove multi-edges and self-loops
            
            # Remove self-loops
            random_graph.remove_edges_from(nx.selfloop_edges(random_graph))
            
            return random_graph
        except:
            # Fallback: Erdős–Rényi random graph
            n = graph.number_of_nodes()
            m = graph.number_of_edges()
            p = 2 * m / (n * (n - 1)) if n > 1 else 0
            
            if isinstance(graph, nx.DiGraph):
                return nx.erdos_renyi_graph(n, p, directed=True)
            else:
                return nx.erdos_renyi_graph(n, p)
    
    def _generate_pattern_catalog(self, motif_instances: List[MotifInstance]) -> Dict[str, Any]:
        """Generate a catalog of unique patterns found"""
        pattern_catalog = defaultdict(list)
        
        for instance in motif_instances:
            pattern_catalog[instance.motif_type].append({
                "pattern_id": instance.pattern_id,
                "nodes": instance.nodes,
                "edges": instance.edges,
                "size": len(instance.nodes)
            })
        
        # Add summary statistics
        catalog_summary = {}
        for motif_type, patterns in pattern_catalog.items():
            catalog_summary[motif_type] = {
                "count": len(patterns),
                "sizes": list(set(p["size"] for p in patterns)),
                "unique_patterns": len(set(p["pattern_id"] for p in patterns))
            }
        
        return {
            "patterns": dict(pattern_catalog),
            "summary": catalog_summary
        }
    
    def _store_motif_results(self, motif_instances: List[MotifInstance], 
                           algorithm_info: Dict[str, Any]) -> Dict[str, Any]:
        """Store motif detection results to Neo4j"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return {"status": "failed", "reason": "Neo4j not available"}
        
        try:
            with self.neo4j_tool.driver.session() as session:
                # Store motif instances as relationships or separate nodes
                stored_count = 0
                for instance in motif_instances:
                    # Create motif instance node
                    result = session.run("""
                    CREATE (m:MotifInstance {
                        motif_type: $motif_type,
                        pattern_id: $pattern_id,
                        nodes: $nodes,
                        significance_score: $significance_score,
                        frequency: $frequency,
                        created_at: $timestamp
                    })
                    RETURN id(m) as motif_id
                    """, {
                        "motif_type": instance.motif_type,
                        "pattern_id": instance.pattern_id,
                        "nodes": instance.nodes,
                        "significance_score": instance.significance_score,
                        "frequency": instance.frequency,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    stored_count += 1
                
                return {
                    "status": "success", 
                    "motifs_stored": stored_count,
                    "algorithm": "network_motifs_detection"
                }
                
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    
    def _calculate_academic_confidence(self, stats: MotifStats, 
                                     algorithm_info: Dict[str, Any]) -> float:
        """Calculate academic-quality confidence for motif detection results"""
        try:
            # Base confidence from number of motifs found
            motif_confidence = min(1.0, stats.total_motifs / 100.0)  # Normalize to reasonable scale
            
            # Significance testing bonus
            significance_bonus = 0.0
            if stats.significance_scores:
                avg_significance = np.mean(list(stats.significance_scores.values()))
                significance_bonus = min(0.3, avg_significance / 10.0)  # Up to 30% bonus
            
            # Pattern diversity factor
            diversity_factor = 0.0
            if stats.motif_types:
                num_types = len(stats.motif_types)
                diversity_factor = min(0.2, num_types / 10.0)  # Up to 20% for pattern diversity
            
            # Execution quality factor
            execution_quality = 0.0
            if algorithm_info.get("total_instances", 0) > 0:
                execution_quality = 0.2  # Base quality for successful execution
            
            # Combine factors
            combined_confidence = (
                motif_confidence * 0.4 +
                significance_bonus +
                diversity_factor +
                execution_quality
            )
            
            return max(0.1, min(1.0, combined_confidence))
            
        except Exception as e:
            print(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def _format_output(self, motif_instances: List[MotifInstance], stats: MotifStats,
                      algorithm_info: Dict, pattern_catalog: Dict[str, Any], 
                      output_format: str) -> Dict[str, Any]:
        """Format output based on requested format"""
        # Convert motif instances to dictionaries
        motif_data = []
        for instance in motif_instances:
            motif_data.append({
                "motif_type": instance.motif_type,
                "nodes": instance.nodes,
                "edges": instance.edges,
                "pattern_id": instance.pattern_id,
                "significance_score": instance.significance_score,
                "frequency": instance.frequency
            })
        
        base_data = {
            "motif_stats": {
                "total_motifs": stats.total_motifs,
                "motif_types": stats.motif_types,
                "significance_scores": stats.significance_scores,
                "enrichment_ratios": stats.enrichment_ratios,
                "z_scores": stats.z_scores,
                "p_values": stats.p_values,
                "random_baseline": stats.random_baseline
            },
            "algorithm_info": algorithm_info,
            "pattern_catalog": pattern_catalog
        }
        
        if output_format == "summary":
            base_data["motif_instances"] = [
                {
                    "motif_type": instance["motif_type"],
                    "nodes_count": len(instance["nodes"]),
                    "edges_count": len(instance["edges"])
                }
                for instance in motif_data
            ]
        elif output_format == "patterns_only":
            base_data = {"pattern_catalog": pattern_catalog}
        else:  # detailed
            base_data["motif_instances"] = motif_data
        
        return base_data
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract - override base implementation"""
        validation_result = self._validate_advanced_input(input_data)
        return validation_result["valid"]
    
    def _handle_advanced_error(self, error: Exception, request: ToolRequest) -> ToolResult:
        """Handle advanced analytics errors"""
        execution_time, memory_used = self._end_execution()
        
        error_message = str(error)
        error_code = "UNEXPECTED_ERROR"
        
        # Categorize specific errors
        if "memory" in error_message.lower():
            error_code = "MEMORY_LIMIT_EXCEEDED"
        elif "subgraph" in error_message.lower():
            error_code = "SUBGRAPH_ENUMERATION_FAILED"
        elif "significance" in error_message.lower():
            error_code = "SIGNIFICANCE_TESTING_FAILED"
        elif "neo4j" in error_message.lower():
            error_code = "NEO4J_CONNECTION_ERROR"
        elif "motif" in error_message.lower():
            error_code = "MOTIF_TYPE_NOT_SUPPORTED"
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data=None,
            execution_time=execution_time,
            memory_used=memory_used,
            error_code=error_code,
            error_message=error_message,
            metadata={
                "operation": request.operation,
                "timestamp": datetime.now().isoformat(),
                "academic_ready": False
            }
        )


# Example usage and validation
if __name__ == "__main__":
    # Quick validation test
    tool = NetworkMotifsDetectionTool()
    contract = tool.get_contract()
    print(f"Tool {tool.tool_id} initialized successfully")
    print(f"Contract: {contract.name}")
    print(f"Supported motif types: {[mt.value for mt in MotifType]}")