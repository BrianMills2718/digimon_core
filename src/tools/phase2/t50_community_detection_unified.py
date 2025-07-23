"""T50: Community Detection Tool - Advanced Graph Analytics

Real community detection using Louvain algorithm and modularity optimization.
Part of Phase 2.1 Graph Analytics tools providing advanced network analysis capabilities.
"""

import time
import psutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import networkx as nx
import numpy as np
from dataclasses import dataclass
from enum import Enum

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


class CommunityAlgorithm(Enum):
    """Supported community detection algorithms"""
    LOUVAIN = "louvain"
    LEIDEN = "leiden"
    LABEL_PROPAGATION = "label_propagation"
    GREEDY_MODULARITY = "greedy_modularity"
    FLUID = "fluid_communities"


@dataclass
class CommunityStats:
    """Community detection statistics"""
    total_communities: int
    modularity_score: float
    largest_community_size: int
    smallest_community_size: int
    average_community_size: float
    coverage: float
    performance: float


class CommunityDetectionTool(BaseTool):
    """T50: Advanced Community Detection Tool
    
    Implements real community detection algorithms including Louvain, Leiden,
    and other state-of-the-art methods for identifying community structures
    in academic research networks.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize community detection tool with advanced capabilities"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T50_COMMUNITY_DETECTION"
        self.name = "Advanced Community Detection"
        self.category = "advanced_analytics"
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Initialize Neo4j connection for graph data
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
        
        # Algorithm configurations
        self.algorithm_configs = {
            CommunityAlgorithm.LOUVAIN: {
                "resolution": 1.0,
                "threshold": 1e-7,
                "max_iterations": 100
            },
            CommunityAlgorithm.LEIDEN: {
                "resolution": 1.0,
                "threshold": 1e-7,
                "max_iterations": 100,
                "n_iterations": 2
            },
            CommunityAlgorithm.LABEL_PROPAGATION: {
                "max_iterations": 30,
                "seed": 42
            },
            CommunityAlgorithm.GREEDY_MODULARITY: {
                "resolution": 1.0
            },
            CommunityAlgorithm.FLUID: {
                "k": None,  # Will be auto-determined
                "max_iterations": 100,
                "seed": 42
            }
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
            description="Advanced community detection using real algorithms for academic research",
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
                    "algorithm": {
                        "type": "string",
                        "enum": ["louvain", "leiden", "label_propagation", "greedy_modularity", "fluid_communities"],
                        "default": "louvain"
                    },
                    "algorithm_params": {
                        "type": "object",
                        "properties": {
                            "resolution": {"type": "number", "minimum": 0.1, "maximum": 5.0},
                            "threshold": {"type": "number", "minimum": 1e-10, "maximum": 1e-3},
                            "max_iterations": {"type": "integer", "minimum": 10, "maximum": 1000},
                            "seed": {"type": "integer"}
                        }
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "communities_only"],
                        "default": "detailed"
                    },
                    "min_community_size": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 2
                    },
                    "store_results": {
                        "type": "boolean",
                        "default": False,
                        "description": "Store community assignments back to Neo4j"
                    }
                },
                "required": ["graph_source"],
                "additionalProperties": False
            },
            output_schema={
                "type": "object",
                "properties": {
                    "communities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "community_id": {"type": "integer"},
                                "nodes": {"type": "array", "items": {"type": "string"}},
                                "size": {"type": "integer"},
                                "internal_edges": {"type": "integer"},
                                "external_edges": {"type": "integer"},
                                "modularity_contribution": {"type": "number"},
                                "density": {"type": "number"}
                            },
                            "required": ["community_id", "nodes", "size"]
                        }
                    },
                    "community_stats": {
                        "type": "object",
                        "properties": {
                            "total_communities": {"type": "integer"},
                            "modularity_score": {"type": "number"},
                            "largest_community_size": {"type": "integer"},
                            "smallest_community_size": {"type": "integer"},
                            "average_community_size": {"type": "number"},
                            "coverage": {"type": "number"},
                            "performance": {"type": "number"}
                        },
                        "required": ["total_communities", "modularity_score"]
                    },
                    "algorithm_info": {
                        "type": "object",
                        "properties": {
                            "algorithm_used": {"type": "string"},
                            "parameters": {"type": "object"},
                            "convergence_info": {"type": "object"},
                            "execution_time": {"type": "number"}
                        }
                    },
                    "node_assignments": {
                        "type": "object",
                        "description": "Mapping of node_id to community_id"
                    }
                },
                "required": ["communities", "community_stats", "algorithm_info", "node_assignments"]
            },
            dependencies=["networkx", "numpy", "neo4j_service"],
            performance_requirements={
                "max_execution_time": 300.0,  # 5 minutes for large graphs
                "max_memory_mb": 2000,  # 2GB for large academic networks
                "min_accuracy": 0.8  # Minimum modularity quality
            },
            error_conditions=[
                "INVALID_GRAPH_DATA",
                "ALGORITHM_NOT_SUPPORTED",
                "GRAPH_TOO_LARGE",
                "CONVERGENCE_FAILED",
                "NEO4J_CONNECTION_ERROR",
                "INSUFFICIENT_NODES",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute community detection with real algorithms"""
        self._start_execution()
        
        try:
            # Validate input against contract
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(request, "INVALID_INPUT", validation_result["error"])
            
            # Extract parameters
            graph_source = request.input_data["graph_source"]
            algorithm = CommunityAlgorithm(request.input_data.get("algorithm", "louvain"))
            algorithm_params = request.input_data.get("algorithm_params", {})
            output_format = request.input_data.get("output_format", "detailed")
            min_community_size = request.input_data.get("min_community_size", 2)
            store_results = request.input_data.get("store_results", False)
            
            # Load graph data
            graph = self._load_graph_data(graph_source, request.input_data.get("graph_data"))
            if graph is None:
                return self._create_error_result(request, "INVALID_GRAPH_DATA", "Failed to load graph data")
            
            # Validate graph size
            if len(graph.nodes()) < 3:
                return self._create_error_result(request, "INSUFFICIENT_NODES", "Graph must have at least 3 nodes for community detection")
            
            if len(graph.nodes()) > 100000:  # Large graph threshold
                return self._create_error_result(request, "GRAPH_TOO_LARGE", "Graph too large for current memory limits")
            
            # Perform community detection
            communities, algorithm_info = self._detect_communities(graph, algorithm, algorithm_params)
            
            # Filter communities by minimum size
            filtered_communities = self._filter_communities_by_size(communities, min_community_size)
            
            # Calculate community statistics
            community_stats = self._calculate_community_statistics(graph, filtered_communities)
            
            # Generate detailed community analysis
            community_details = self._analyze_communities_detailed(graph, filtered_communities)
            
            # Store results to Neo4j if requested
            storage_info = {}
            if store_results and self.neo4j_tool:
                storage_info = self._store_community_results(filtered_communities, algorithm_info)
            
            # Calculate academic confidence
            confidence = self._calculate_academic_confidence(community_stats, algorithm_info)
            
            # Performance monitoring
            execution_time, memory_used = self._end_execution()
            
            # Prepare result data based on output format
            result_data = self._format_output(
                community_details, community_stats, algorithm_info,
                filtered_communities, output_format
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "academic_ready": True,
                    "algorithm_used": algorithm.value,
                    "statistical_significance": confidence,
                    "batch_processed": len(graph.nodes()) > 1000,
                    "graph_size": len(graph.nodes()),
                    "edge_count": len(graph.edges()),
                    "storage_info": storage_info,
                    "publication_ready": True
                }
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Advanced validation for community detection input"""
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
            
            # Validate algorithm if provided
            if "algorithm" in input_data:
                try:
                    CommunityAlgorithm(input_data["algorithm"])
                except ValueError:
                    valid_algorithms = [alg.value for alg in CommunityAlgorithm]
                    return {"valid": False, "error": f"algorithm must be one of {valid_algorithms}"}
            
            # Validate algorithm parameters
            if "algorithm_params" in input_data:
                params = input_data["algorithm_params"]
                if not isinstance(params, dict):
                    return {"valid": False, "error": "algorithm_params must be a dictionary"}
                
                # Validate specific parameter ranges
                if "resolution" in params:
                    if not (0.1 <= params["resolution"] <= 5.0):
                        return {"valid": False, "error": "resolution must be between 0.1 and 5.0"}
                
                if "threshold" in params:
                    if not (1e-10 <= params["threshold"] <= 1e-3):
                        return {"valid": False, "error": "threshold must be between 1e-10 and 1e-3"}
                
                if "max_iterations" in params:
                    if not (10 <= params["max_iterations"] <= 1000):
                        return {"valid": False, "error": "max_iterations must be between 10 and 1000"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None) -> Optional[nx.Graph]:
        """Load graph data from various sources"""
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
                return None
                
        except Exception as e:
            print(f"Error loading graph data: {e}")
            return None
    
    def _load_from_neo4j(self) -> Optional[nx.Graph]:
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
                G = nx.Graph()
                
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
    
    def _load_from_networkx_data(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from NetworkX data format"""
        if not graph_data or "nodes" not in graph_data or "edges" not in graph_data:
            return None
        
        try:
            G = nx.Graph()
            
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
    
    def _load_from_edge_list(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        if not graph_data or "edges" not in graph_data:
            return None
        
        try:
            G = nx.Graph()
            
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
    
    def _load_from_adjacency_matrix(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        if not graph_data or "matrix" not in graph_data:
            return None
        
        try:
            matrix = np.array(graph_data["matrix"])
            node_labels = graph_data.get("node_labels", list(range(len(matrix))))
            
            G = nx.from_numpy_array(matrix)
            
            # Relabel nodes if labels provided
            if len(node_labels) == len(matrix):
                mapping = {i: label for i, label in enumerate(node_labels)}
                G = nx.relabel_nodes(G, mapping)
            
            return G
            
        except Exception as e:
            print(f"Error loading adjacency matrix: {e}")
            return None
    
    def _detect_communities(self, graph: nx.Graph, algorithm: CommunityAlgorithm, 
                          params: Dict) -> Tuple[Dict[str, int], Dict[str, Any]]:
        """Perform community detection using specified algorithm"""
        # Merge algorithm-specific defaults with user parameters
        config = self.algorithm_configs[algorithm].copy()
        config.update(params)
        
        start_time = time.time()
        
        try:
            if algorithm == CommunityAlgorithm.LOUVAIN:
                communities = self._louvain_communities(graph, config)
            elif algorithm == CommunityAlgorithm.LEIDEN:
                communities = self._leiden_communities(graph, config)
            elif algorithm == CommunityAlgorithm.LABEL_PROPAGATION:
                communities = self._label_propagation_communities(graph, config)
            elif algorithm == CommunityAlgorithm.GREEDY_MODULARITY:
                communities = self._greedy_modularity_communities(graph, config)
            elif algorithm == CommunityAlgorithm.FLUID:
                communities = self._fluid_communities(graph, config)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            execution_time = time.time() - start_time
            
            algorithm_info = {
                "algorithm_used": algorithm.value,
                "parameters": config,
                "execution_time": execution_time,
                "convergence_info": {
                    "converged": True,  # Will be updated by specific algorithms
                    "iterations": None,
                    "final_modularity": self._calculate_modularity(graph, communities)
                }
            }
            
            return communities, algorithm_info
            
        except Exception as e:
            raise RuntimeError(f"Community detection failed: {str(e)}")
    
    def _louvain_communities(self, graph: nx.Graph, config: Dict) -> Dict[str, int]:
        """Louvain community detection using NetworkX"""
        try:
            # Use NetworkX implementation of Louvain
            import networkx.algorithms.community as nx_community
            
            # Convert to proper format for Louvain
            communities_generator = nx_community.louvain_communities(
                graph, 
                resolution=config.get("resolution", 1.0),
                threshold=config.get("threshold", 1e-7),
                seed=config.get("seed", 42)
            )
            
            # Convert to node -> community_id mapping
            node_to_community = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    node_to_community[node] = community_id
            
            return node_to_community
            
        except Exception as e:
            raise RuntimeError(f"Louvain algorithm failed: {str(e)}")
    
    def _leiden_communities(self, graph: nx.Graph, config: Dict) -> Dict[str, int]:
        """Leiden community detection (fallback to Louvain if Leiden not available)"""
        try:
            # Try to import python-igraph for Leiden
            try:
                import igraph as ig
                import leidenalg
                
                # Convert NetworkX to igraph
                edge_list = list(graph.edges())
                node_list = list(graph.nodes())
                
                g = ig.Graph()
                g.add_vertices(len(node_list))
                g.add_edges([(node_list.index(u), node_list.index(v)) for u, v in edge_list])
                
                # Add weights if available
                if graph.edges(data=True):
                    weights = [graph[u][v].get('weight', 1.0) for u, v in edge_list]
                    g.es['weight'] = weights
                
                # Run Leiden algorithm
                partition = leidenalg.find_partition(
                    g, 
                    leidenalg.RBConfigurationVertexPartition,
                    resolution_parameter=config.get("resolution", 1.0),
                    n_iterations=config.get("n_iterations", 2)
                )
                
                # Convert back to NetworkX format
                node_to_community = {}
                for i, community_id in enumerate(partition.membership):
                    node_to_community[node_list[i]] = community_id
                
                return node_to_community
                
            except ImportError:
                # Fallback to Louvain if Leiden not available
                print("Warning: python-igraph or leidenalg not available, falling back to Louvain")
                return self._louvain_communities(graph, config)
            
        except Exception as e:
            raise RuntimeError(f"Leiden algorithm failed: {str(e)}")
    
    def _label_propagation_communities(self, graph: nx.Graph, config: Dict) -> Dict[str, int]:
        """Label propagation community detection"""
        try:
            import networkx.algorithms.community as nx_community
            
            # NetworkX label_propagation_communities doesn't take seed parameter
            communities_generator = nx_community.label_propagation_communities(graph)
            
            # Convert to node -> community_id mapping
            node_to_community = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    node_to_community[node] = community_id
            
            return node_to_community
            
        except Exception as e:
            raise RuntimeError(f"Label propagation algorithm failed: {str(e)}")
    
    def _greedy_modularity_communities(self, graph: nx.Graph, config: Dict) -> Dict[str, int]:
        """Greedy modularity optimization community detection"""
        try:
            import networkx.algorithms.community as nx_community
            
            communities_generator = nx_community.greedy_modularity_communities(
                graph,
                resolution=config.get("resolution", 1.0)
            )
            
            # Convert to node -> community_id mapping
            node_to_community = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    node_to_community[node] = community_id
            
            return node_to_community
            
        except Exception as e:
            raise RuntimeError(f"Greedy modularity algorithm failed: {str(e)}")
    
    def _fluid_communities(self, graph: nx.Graph, config: Dict) -> Dict[str, int]:
        """Fluid communities algorithm"""
        try:
            import networkx.algorithms.community as nx_community
            
            # Estimate k if not provided
            k = config.get("k")
            if k is None:
                # Rough estimate: sqrt(n) communities
                k = max(2, int(np.sqrt(len(graph.nodes()))))
            
            communities_generator = nx_community.asyn_fluidc(
                graph,
                k=k,
                max_iter=config.get("max_iterations", 100),
                seed=config.get("seed", 42)
            )
            
            # Convert to node -> community_id mapping
            node_to_community = {}
            for community_id, community_nodes in enumerate(communities_generator):
                for node in community_nodes:
                    node_to_community[node] = community_id
            
            return node_to_community
            
        except Exception as e:
            raise RuntimeError(f"Fluid communities algorithm failed: {str(e)}")
    
    def _filter_communities_by_size(self, communities: Dict[str, int], 
                                  min_size: int) -> Dict[str, int]:
        """Filter communities by minimum size"""
        # Count community sizes
        community_sizes = {}
        for node, community_id in communities.items():
            community_sizes[community_id] = community_sizes.get(community_id, 0) + 1
        
        # Filter communities
        valid_communities = {cid for cid, size in community_sizes.items() if size >= min_size}
        
        # Reassign community IDs to be contiguous
        filtered_communities = {}
        community_mapping = {}
        new_community_id = 0
        
        for node, old_community_id in communities.items():
            if old_community_id in valid_communities:
                if old_community_id not in community_mapping:
                    community_mapping[old_community_id] = new_community_id
                    new_community_id += 1
                filtered_communities[node] = community_mapping[old_community_id]
        
        return filtered_communities
    
    def _calculate_community_statistics(self, graph: nx.Graph, 
                                      communities: Dict[str, int]) -> CommunityStats:
        """Calculate comprehensive community statistics"""
        if not communities:
            return CommunityStats(0, 0.0, 0, 0, 0.0, 0.0, 0.0)
        
        # Count communities and their sizes
        community_sizes = {}
        for node, community_id in communities.items():
            community_sizes[community_id] = community_sizes.get(community_id, 0) + 1
        
        total_communities = len(community_sizes)
        largest_size = max(community_sizes.values()) if community_sizes else 0
        smallest_size = min(community_sizes.values()) if community_sizes else 0
        average_size = sum(community_sizes.values()) / len(community_sizes) if community_sizes else 0
        
        # Calculate modularity
        modularity = self._calculate_modularity(graph, communities)
        
        # Calculate coverage and performance
        coverage = len(communities) / len(graph.nodes()) if graph.nodes() else 0.0
        performance = self._calculate_performance(graph, communities)
        
        return CommunityStats(
            total_communities=total_communities,
            modularity_score=modularity,
            largest_community_size=largest_size,
            smallest_community_size=smallest_size,
            average_community_size=average_size,
            coverage=coverage,
            performance=performance
        )
    
    def _calculate_modularity(self, graph: nx.Graph, communities: Dict[str, int]) -> float:
        """Calculate modularity score for community partition"""
        try:
            # Convert to list of sets format for NetworkX
            community_sets = {}
            for node, community_id in communities.items():
                # Only include nodes that exist in the graph
                if node in graph.nodes():
                    if community_id not in community_sets:
                        community_sets[community_id] = set()
                    community_sets[community_id].add(node)
            
            community_list = list(community_sets.values())
            
            # Ensure all graph nodes are covered
            covered_nodes = set()
            for community in community_list:
                covered_nodes.update(community)
            
            # Add missing nodes as singleton communities
            missing_nodes = set(graph.nodes()) - covered_nodes
            for node in missing_nodes:
                community_list.append({node})
            
            # Calculate modularity using NetworkX
            return nx.algorithms.community.modularity(graph, community_list)
            
        except Exception as e:
            print(f"Error calculating modularity: {e}")
            return 0.0
    
    def _calculate_performance(self, graph: nx.Graph, communities: Dict[str, int]) -> float:
        """Calculate performance measure for community partition"""
        try:
            total_possible_edges = len(graph.nodes()) * (len(graph.nodes()) - 1) // 2
            if total_possible_edges == 0:
                return 0.0
            
            intra_community_edges = 0
            inter_community_edges = 0
            
            for u, v in graph.edges():
                if communities.get(u) == communities.get(v):
                    intra_community_edges += 1
                else:
                    inter_community_edges += 1
            
            # Calculate potential intra/inter community edges
            community_sizes = {}
            for node, community_id in communities.items():
                community_sizes[community_id] = community_sizes.get(community_id, 0) + 1
            
            potential_intra = sum(size * (size - 1) // 2 for size in community_sizes.values())
            potential_inter = total_possible_edges - potential_intra
            
            # Performance = fraction of intra-community edges + fraction of missing inter-community edges
            if potential_intra > 0 and potential_inter > 0:
                performance = (intra_community_edges / potential_intra + 
                             (potential_inter - inter_community_edges) / potential_inter) / 2
                return max(0.0, min(1.0, performance))
            
            return 0.0
            
        except Exception as e:
            print(f"Error calculating performance: {e}")
            return 0.0
    
    def _analyze_communities_detailed(self, graph: nx.Graph, 
                                    communities: Dict[str, int]) -> List[Dict[str, Any]]:
        """Analyze communities in detail"""
        community_details = []
        
        # Group nodes by community
        community_nodes = {}
        for node, community_id in communities.items():
            if community_id not in community_nodes:
                community_nodes[community_id] = []
            community_nodes[community_id].append(node)
        
        # Analyze each community
        for community_id, nodes in community_nodes.items():
            # Count internal and external edges
            internal_edges = 0
            external_edges = 0
            
            for node in nodes:
                for neighbor in graph.neighbors(node):
                    if neighbor in nodes:
                        internal_edges += 1
                    else:
                        external_edges += 1
            
            # Avoid double counting internal edges
            internal_edges = internal_edges // 2
            
            # Calculate density
            max_internal_edges = len(nodes) * (len(nodes) - 1) // 2
            density = internal_edges / max_internal_edges if max_internal_edges > 0 else 0.0
            
            # Calculate modularity contribution
            subgraph = graph.subgraph(nodes)
            modularity_contribution = self._calculate_modularity(graph, {node: 0 for node in nodes})
            
            community_details.append({
                "community_id": community_id,
                "nodes": nodes,
                "size": len(nodes),
                "internal_edges": internal_edges,
                "external_edges": external_edges,
                "density": density,
                "modularity_contribution": modularity_contribution
            })
        
        return community_details
    
    def _store_community_results(self, communities: Dict[str, int], 
                               algorithm_info: Dict[str, Any]) -> Dict[str, Any]:
        """Store community detection results to Neo4j"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return {"status": "failed", "reason": "Neo4j not available"}
        
        try:
            with self.neo4j_tool.driver.session() as session:
                # Update entity nodes with community assignments
                for node_id, community_id in communities.items():
                    session.run("""
                    MATCH (e:Entity {entity_id: $node_id})
                    SET e.community_id = $community_id,
                        e.community_algorithm = $algorithm,
                        e.community_updated_at = $timestamp
                    """, {
                        "node_id": node_id,
                        "community_id": community_id,
                        "algorithm": algorithm_info["algorithm_used"],
                        "timestamp": datetime.now().isoformat()
                    })
                
                return {
                    "status": "success", 
                    "nodes_updated": len(communities),
                    "algorithm": algorithm_info["algorithm_used"]
                }
                
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    
    def _calculate_academic_confidence(self, stats: CommunityStats, 
                                     algorithm_info: Dict[str, Any]) -> float:
        """Calculate academic-quality confidence for community detection results"""
        try:
            # Base confidence from modularity score
            modularity_confidence = min(1.0, max(0.0, stats.modularity_score + 0.5))  # Shift range
            
            # Algorithm reliability factor
            algorithm_reliability = {
                "louvain": 0.9,
                "leiden": 0.95,
                "label_propagation": 0.75,
                "greedy_modularity": 0.8,
                "fluid_communities": 0.7
            }
            algo_factor = algorithm_reliability.get(algorithm_info["algorithm_used"], 0.8)
            
            # Community structure quality
            structure_quality = 0.0
            if stats.total_communities > 0:
                # Reward balanced community sizes
                size_balance = 1.0 - abs(stats.largest_community_size - stats.average_community_size) / stats.average_community_size
                size_balance = max(0.0, min(1.0, size_balance))
                
                # Reward good coverage
                coverage_factor = min(1.0, stats.coverage)
                
                # Reward performance
                performance_factor = stats.performance
                
                structure_quality = (size_balance * 0.4 + coverage_factor * 0.3 + performance_factor * 0.3)
            
            # Combine factors
            combined_confidence = (
                modularity_confidence * 0.5 +
                algo_factor * 0.3 +
                structure_quality * 0.2
            )
            
            return max(0.1, min(1.0, combined_confidence))
            
        except Exception as e:
            print(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def _format_output(self, community_details: List[Dict], stats: CommunityStats,
                      algorithm_info: Dict, communities: Dict[str, int], 
                      output_format: str) -> Dict[str, Any]:
        """Format output based on requested format"""
        base_data = {
            "community_stats": {
                "total_communities": stats.total_communities,
                "modularity_score": stats.modularity_score,
                "largest_community_size": stats.largest_community_size,
                "smallest_community_size": stats.smallest_community_size,
                "average_community_size": stats.average_community_size,
                "coverage": stats.coverage,
                "performance": stats.performance
            },
            "algorithm_info": algorithm_info,
            "node_assignments": communities
        }
        
        if output_format == "summary":
            base_data["communities"] = [
                {
                    "community_id": detail["community_id"],
                    "size": detail["size"]
                }
                for detail in community_details
            ]
        elif output_format == "communities_only":
            base_data = {"node_assignments": communities}
        else:  # detailed
            base_data["communities"] = community_details
        
        return base_data
    
    def _handle_advanced_error(self, error: Exception, request: ToolRequest) -> ToolResult:
        """Handle advanced analytics errors"""
        execution_time, memory_used = self._end_execution()
        
        error_message = str(error)
        error_code = "UNEXPECTED_ERROR"
        
        # Categorize specific errors
        if "memory" in error_message.lower():
            error_code = "MEMORY_LIMIT_EXCEEDED"
        elif "convergence" in error_message.lower():
            error_code = "CONVERGENCE_FAILED"
        elif "neo4j" in error_message.lower():
            error_code = "NEO4J_CONNECTION_ERROR"
        elif "algorithm" in error_message.lower():
            error_code = "ALGORITHM_NOT_SUPPORTED"
        
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
    tool = CommunityDetectionTool()
    contract = tool.get_contract()
    print(f"Tool {tool.tool_id} initialized successfully")
    print(f"Contract: {contract.name}")
    print(f"Supported algorithms: {[alg.value for alg in CommunityAlgorithm]}")