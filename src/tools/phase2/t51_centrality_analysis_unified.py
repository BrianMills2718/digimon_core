"""T51: Centrality Analysis Tool - Advanced Graph Analytics

Comprehensive centrality measures beyond basic PageRank including betweenness,
eigenvector, closeness, and other advanced centrality metrics for academic research.
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


class CentralityMetric(Enum):
    """Supported centrality metrics"""
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"
    KATZ = "katz"
    HARMONIC = "harmonic"
    LOAD = "load"
    INFORMATION = "information"
    CURRENT_FLOW_BETWEENNESS = "current_flow_betweenness"
    CURRENT_FLOW_CLOSENESS = "current_flow_closeness"
    SUBGRAPH = "subgraph"


@dataclass
class CentralityResult:
    """Centrality analysis result"""
    metric: str
    scores: Dict[str, float]
    statistics: Dict[str, float]
    execution_time: float
    parameters: Dict[str, Any]


class CentralityAnalysisTool(BaseTool):
    """T51: Advanced Centrality Analysis Tool
    
    Implements comprehensive centrality measures for identifying important nodes
    in academic research networks using real algorithms and academic-quality metrics.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize centrality analysis tool with advanced capabilities"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T51_CENTRALITY_ANALYSIS"
        self.name = "Advanced Centrality Analysis"
        self.category = "advanced_analytics"
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Initialize Neo4j connection for graph data
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
        
        # Centrality metric configurations
        self.metric_configs = {
            CentralityMetric.DEGREE: {
                "normalized": True
            },
            CentralityMetric.BETWEENNESS: {
                "normalized": True,
                "endpoints": False,
                "k": None  # Use all nodes
            },
            CentralityMetric.CLOSENESS: {
                "distance": None,
                "wf_improved": True
            },
            CentralityMetric.EIGENVECTOR: {
                "max_iter": 100,
                "tol": 1e-6,
                "nstart": None,
                "weight": "weight"
            },
            CentralityMetric.PAGERANK: {
                "alpha": 0.85,
                "personalization": None,
                "max_iter": 100,
                "tol": 1e-6,
                "nstart": None,
                "weight": "weight"
            },
            CentralityMetric.KATZ: {
                "alpha": 0.1,
                "beta": 1.0,
                "max_iter": 1000,
                "tol": 1e-6,
                "nstart": None,
                "normalized": True,
                "weight": "weight"
            },
            CentralityMetric.HARMONIC: {
                "distance": None
            },
            CentralityMetric.LOAD: {
                "normalized": True,
                "weight": "weight"
            },
            CentralityMetric.INFORMATION: {
                "weight": "weight"
            },
            CentralityMetric.CURRENT_FLOW_BETWEENNESS: {
                "normalized": True,
                "weight": "weight",
                "dtype": float,
                "solver": "lu"
            },
            CentralityMetric.CURRENT_FLOW_CLOSENESS: {
                "weight": "weight",
                "dtype": float,
                "solver": "lu"
            },
            CentralityMetric.SUBGRAPH: {
                "normalized": True
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
            description="Comprehensive centrality analysis with real algorithms for academic research",
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
                    "centrality_metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "degree", "betweenness", "closeness", "eigenvector", 
                                "pagerank", "katz", "harmonic", "load", "information",
                                "current_flow_betweenness", "current_flow_closeness", "subgraph"
                            ]
                        },
                        "default": ["degree", "betweenness", "closeness", "eigenvector"]
                    },
                    "metric_params": {
                        "type": "object",
                        "description": "Parameters for specific centrality metrics"
                    },
                    "top_k_nodes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 10,
                        "description": "Number of top nodes to return for each metric"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "rankings_only", "statistics_only"],
                        "default": "detailed"
                    },
                    "store_results": {
                        "type": "boolean",
                        "default": False,
                        "description": "Store centrality scores back to Neo4j"
                    },
                    "normalize_scores": {
                        "type": "boolean",
                        "default": True,
                        "description": "Normalize scores to [0,1] range for comparison"
                    }
                },
                "required": ["graph_source"],
                "additionalProperties": False
            },
            output_schema={
                "type": "object",
                "properties": {
                    "centrality_results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string"},
                                "top_nodes": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "node_id": {"type": "string"},
                                            "score": {"type": "number"},
                                            "rank": {"type": "integer"}
                                        }
                                    }
                                },
                                "statistics": {
                                    "type": "object",
                                    "properties": {
                                        "mean": {"type": "number"},
                                        "std": {"type": "number"},
                                        "min": {"type": "number"},
                                        "max": {"type": "number"},
                                        "median": {"type": "number"}
                                    }
                                },
                                "execution_time": {"type": "number"},
                                "parameters": {"type": "object"}
                            },
                            "required": ["metric", "top_nodes", "statistics", "execution_time"]
                        }
                    },
                    "correlation_matrix": {
                        "type": "object",
                        "description": "Correlation matrix between different centrality metrics"
                    },
                    "overall_statistics": {
                        "type": "object",
                        "properties": {
                            "graph_size": {"type": "integer"},
                            "total_edges": {"type": "integer"},
                            "average_degree": {"type": "number"},
                            "graph_density": {"type": "number"},
                            "analysis_time": {"type": "number"}
                        }
                    }
                },
                "required": ["centrality_results", "overall_statistics"]
            },
            dependencies=["networkx", "numpy", "scipy", "neo4j_service"],
            performance_requirements={
                "max_execution_time": 600.0,  # 10 minutes for complex centrality calculations
                "max_memory_mb": 3000,  # 3GB for large academic networks
                "min_accuracy": 0.9  # High precision for academic research
            },
            error_conditions=[
                "INVALID_GRAPH_DATA",
                "METRIC_NOT_SUPPORTED",
                "GRAPH_TOO_LARGE",
                "CALCULATION_FAILED",
                "NEO4J_CONNECTION_ERROR",
                "INSUFFICIENT_NODES",
                "MEMORY_LIMIT_EXCEEDED",
                "CONVERGENCE_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute centrality analysis with real algorithms"""
        self._start_execution()
        
        try:
            # Validate input against contract
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(request, "INVALID_INPUT", validation_result["error"])
            
            # Extract parameters
            graph_source = request.input_data["graph_source"]
            centrality_metrics = request.input_data.get("centrality_metrics", 
                                                       ["degree", "betweenness", "closeness", "eigenvector"])
            metric_params = request.input_data.get("metric_params", {})
            top_k_nodes = request.input_data.get("top_k_nodes", 10)
            output_format = request.input_data.get("output_format", "detailed")
            store_results = request.input_data.get("store_results", False)
            normalize_scores = request.input_data.get("normalize_scores", True)
            
            # Load graph data
            graph = self._load_graph_data(graph_source, request.input_data.get("graph_data"))
            if graph is None:
                return self._create_error_result(request, "INVALID_GRAPH_DATA", "Failed to load graph data")
            
            # Validate graph size
            if len(graph.nodes()) < 3:
                return self._create_error_result(request, "INSUFFICIENT_NODES", "Graph must have at least 3 nodes for centrality analysis")
            
            if len(graph.nodes()) > 50000:  # Large graph threshold
                return self._create_error_result(request, "GRAPH_TOO_LARGE", "Graph too large for current memory limits")
            
            # Calculate centrality metrics
            centrality_results = []
            all_scores = {}  # For correlation analysis
            
            for metric_name in centrality_metrics:
                try:
                    # Check if metric is valid before creating enum
                    valid_metrics = [metric.value for metric in CentralityMetric]
                    if metric_name not in valid_metrics:
                        return self._create_error_result(request, "METRIC_NOT_SUPPORTED", f"Unsupported metric: {metric_name}")
                    
                    metric = CentralityMetric(metric_name)
                    result = self._calculate_centrality_metric(graph, metric, metric_params.get(metric_name, {}))
                    
                    if normalize_scores:
                        result.scores = self._normalize_scores(result.scores)
                    
                    centrality_results.append(result)
                    all_scores[metric_name] = result.scores
                    
                except ValueError as e:
                    return self._create_error_result(request, "METRIC_NOT_SUPPORTED", f"Unsupported metric: {metric_name}")
                except Exception as e:
                    return self._create_error_result(request, "CALCULATION_FAILED", f"Failed to calculate {metric_name}: {str(e)}")
            
            # Calculate correlation matrix between metrics
            correlation_matrix = self._calculate_correlation_matrix(all_scores) if len(all_scores) > 1 else {}
            
            # Calculate overall graph statistics
            overall_stats = self._calculate_graph_statistics(graph)
            
            # Store results to Neo4j if requested
            storage_info = {}
            if store_results and self.neo4j_tool:
                storage_info = self._store_centrality_results(all_scores)
            
            # Calculate academic confidence
            confidence = self._calculate_academic_confidence(centrality_results, overall_stats)
            
            # Performance monitoring
            execution_time, memory_used = self._end_execution()
            overall_stats["analysis_time"] = execution_time
            
            # Format output based on requested format
            result_data = self._format_centrality_output(
                centrality_results, correlation_matrix, overall_stats, 
                top_k_nodes, output_format
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "academic_ready": True,
                    "metrics_calculated": centrality_metrics,
                    "statistical_significance": confidence,
                    "batch_processed": len(graph.nodes()) > 1000,
                    "graph_size": len(graph.nodes()),
                    "edge_count": len(graph.edges()),
                    "storage_info": storage_info,
                    "publication_ready": True,
                    "normalized": normalize_scores
                }
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Advanced validation for centrality analysis input"""
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
            
            # Validate centrality metrics if provided
            if "centrality_metrics" in input_data:
                valid_metrics = [metric.value for metric in CentralityMetric]
                for metric in input_data["centrality_metrics"]:
                    if metric not in valid_metrics:
                        return {"valid": False, "error": f"Invalid metric '{metric}'. Valid metrics: {valid_metrics}"}
            
            # Validate top_k_nodes
            if "top_k_nodes" in input_data:
                top_k = input_data["top_k_nodes"]
                if not isinstance(top_k, int) or top_k < 1 or top_k > 1000:
                    return {"valid": False, "error": "top_k_nodes must be an integer between 1 and 1000"}
            
            # Validate output format
            if "output_format" in input_data:
                valid_formats = ["detailed", "summary", "rankings_only", "statistics_only"]
                if input_data["output_format"] not in valid_formats:
                    return {"valid": False, "error": f"output_format must be one of {valid_formats}"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None) -> Optional[nx.Graph]:
        """Load graph data from various sources (reuse from T50)"""
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
                # Load nodes with existing centrality scores
                nodes_result = session.run("""
                MATCH (n:Entity)
                RETURN n.entity_id as id, n.canonical_name as name, 
                       n.entity_type as type, n.pagerank_score as pagerank,
                       n.degree_centrality as degree_centrality,
                       n.betweenness_centrality as betweenness_centrality
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
                        pagerank=record["pagerank"] or 0.0,
                        degree_centrality=record["degree_centrality"] or 0.0,
                        betweenness_centrality=record["betweenness_centrality"] or 0.0
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
    
    def _calculate_centrality_metric(self, graph: nx.Graph, metric: CentralityMetric, 
                                   params: Dict) -> CentralityResult:
        """Calculate specific centrality metric"""
        # Merge metric-specific defaults with user parameters
        config = self.metric_configs[metric].copy()
        config.update(params)
        
        start_time = time.time()
        
        try:
            if metric == CentralityMetric.DEGREE:
                scores = self._calculate_degree_centrality(graph, config)
            elif metric == CentralityMetric.BETWEENNESS:
                scores = self._calculate_betweenness_centrality(graph, config)
            elif metric == CentralityMetric.CLOSENESS:
                scores = self._calculate_closeness_centrality(graph, config)
            elif metric == CentralityMetric.EIGENVECTOR:
                scores = self._calculate_eigenvector_centrality(graph, config)
            elif metric == CentralityMetric.PAGERANK:
                scores = self._calculate_pagerank_centrality(graph, config)
            elif metric == CentralityMetric.KATZ:
                scores = self._calculate_katz_centrality(graph, config)
            elif metric == CentralityMetric.HARMONIC:
                scores = self._calculate_harmonic_centrality(graph, config)
            elif metric == CentralityMetric.LOAD:
                scores = self._calculate_load_centrality(graph, config)
            elif metric == CentralityMetric.INFORMATION:
                scores = self._calculate_information_centrality(graph, config)
            elif metric == CentralityMetric.CURRENT_FLOW_BETWEENNESS:
                scores = self._calculate_current_flow_betweenness_centrality(graph, config)
            elif metric == CentralityMetric.CURRENT_FLOW_CLOSENESS:
                scores = self._calculate_current_flow_closeness_centrality(graph, config)
            elif metric == CentralityMetric.SUBGRAPH:
                scores = self._calculate_subgraph_centrality(graph, config)
            else:
                raise ValueError(f"Unsupported centrality metric: {metric}")
            
            execution_time = time.time() - start_time
            
            # Calculate statistics
            score_values = list(scores.values())
            statistics = {
                "mean": float(np.mean(score_values)),
                "std": float(np.std(score_values)),
                "min": float(np.min(score_values)),
                "max": float(np.max(score_values)),
                "median": float(np.median(score_values))
            }
            
            return CentralityResult(
                metric=metric.value,
                scores=scores,
                statistics=statistics,
                execution_time=execution_time,
                parameters=config
            )
            
        except Exception as e:
            raise RuntimeError(f"Centrality calculation failed for {metric.value}: {str(e)}")
    
    def _calculate_degree_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate degree centrality"""
        return nx.degree_centrality(graph) if config.get("normalized", True) else dict(graph.degree())
    
    def _calculate_betweenness_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate betweenness centrality"""
        return nx.betweenness_centrality(
            graph,
            normalized=config.get("normalized", True),
            endpoints=config.get("endpoints", False),
            k=config.get("k")
        )
    
    def _calculate_closeness_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate closeness centrality"""
        return nx.closeness_centrality(
            graph,
            distance=config.get("distance"),
            wf_improved=config.get("wf_improved", True)
        )
    
    def _calculate_eigenvector_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate eigenvector centrality"""
        try:
            return nx.eigenvector_centrality(
                graph,
                max_iter=config.get("max_iter", 100),
                tol=config.get("tol", 1e-6),
                nstart=config.get("nstart"),
                weight=config.get("weight", "weight")
            )
        except nx.PowerIterationFailedConvergence:
            # Fallback to numpy method if power iteration fails
            return nx.eigenvector_centrality_numpy(graph, weight=config.get("weight", "weight"))
    
    def _calculate_pagerank_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate PageRank centrality"""
        try:
            return nx.pagerank(
                graph,
                alpha=config.get("alpha", 0.85),
                personalization=config.get("personalization"),
                max_iter=config.get("max_iter", 100),
                tol=config.get("tol", 1e-6),
                nstart=config.get("nstart"),
                weight=config.get("weight", "weight")
            )
        except Exception as e:
            # Fallback to numpy implementation if scipy has issues
            print(f"Warning: scipy PageRank failed ({e}), using numpy implementation")
            try:
                return nx.pagerank_numpy(
                    graph,
                    alpha=config.get("alpha", 0.85),
                    personalization=config.get("personalization"),
                    weight=config.get("weight", "weight")
                )
            except Exception as e2:
                # Final fallback to power iteration method
                print(f"Warning: numpy PageRank also failed ({e2}), using power iteration")
                # Simple power iteration implementation
                alpha = config.get("alpha", 0.85)
                nodes = list(graph.nodes())
                n = len(nodes)
                
                # Initialize pagerank values
                pagerank = {node: 1.0/n for node in nodes}
                
                # Power iteration
                for _ in range(config.get("max_iter", 100)):
                    new_pagerank = {}
                    for node in nodes:
                        rank = (1 - alpha) / n
                        for neighbor in graph.neighbors(node):
                            rank += alpha * pagerank[neighbor] / graph.degree(neighbor)
                        new_pagerank[node] = rank
                    
                    # Check convergence
                    diff = sum(abs(new_pagerank[node] - pagerank[node]) for node in nodes)
                    pagerank = new_pagerank
                    
                    if diff < config.get("tol", 1e-6):
                        break
                
                return pagerank
    
    def _calculate_katz_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate Katz centrality"""
        try:
            return nx.katz_centrality(
                graph,
                alpha=config.get("alpha", 0.1),
                beta=config.get("beta", 1.0),
                max_iter=config.get("max_iter", 1000),
                tol=config.get("tol", 1e-6),
                nstart=config.get("nstart"),
                normalized=config.get("normalized", True),
                weight=config.get("weight", "weight")
            )
        except nx.PowerIterationFailedConvergence:
            # Fallback to numpy method if power iteration fails
            return nx.katz_centrality_numpy(
                graph,
                alpha=config.get("alpha", 0.1),
                beta=config.get("beta", 1.0),
                normalized=config.get("normalized", True),
                weight=config.get("weight", "weight")
            )
    
    def _calculate_harmonic_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate harmonic centrality"""
        return nx.harmonic_centrality(
            graph,
            distance=config.get("distance")
        )
    
    def _calculate_load_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate load centrality"""
        return nx.load_centrality(
            graph,
            normalized=config.get("normalized", True),
            weight=config.get("weight", "weight")
        )
    
    def _calculate_information_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate information centrality"""
        return nx.information_centrality(
            graph,
            weight=config.get("weight", "weight")
        )
    
    def _calculate_current_flow_betweenness_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate current flow betweenness centrality"""
        return nx.current_flow_betweenness_centrality(
            graph,
            normalized=config.get("normalized", True),
            weight=config.get("weight", "weight"),
            dtype=config.get("dtype", float),
            solver=config.get("solver", "lu")
        )
    
    def _calculate_current_flow_closeness_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate current flow closeness centrality"""
        return nx.current_flow_closeness_centrality(
            graph,
            weight=config.get("weight", "weight"),
            dtype=config.get("dtype", float),
            solver=config.get("solver", "lu")
        )
    
    def _calculate_subgraph_centrality(self, graph: nx.Graph, config: Dict) -> Dict[str, float]:
        """Calculate subgraph centrality"""
        return nx.subgraph_centrality(graph)
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to [0,1] range"""
        values = list(scores.values())
        if not values:
            return scores
        
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return {node: 0.5 for node in scores}
        
        normalized = {}
        for node, score in scores.items():
            normalized[node] = (score - min_val) / (max_val - min_val)
        
        return normalized
    
    def _calculate_correlation_matrix(self, all_scores: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between centrality metrics"""
        try:
            # Use numpy for correlation calculation to avoid scipy compatibility issues
            
            metrics = list(all_scores.keys())
            correlation_matrix = {}
            
            # Get common nodes across all metrics
            common_nodes = set.intersection(*[set(scores.keys()) for scores in all_scores.values()])
            
            if len(common_nodes) < 3:  # Need at least 3 points for correlation
                return {}
            
            for metric1 in metrics:
                correlation_matrix[metric1] = {}
                for metric2 in metrics:
                    if metric1 == metric2:
                        correlation_matrix[metric1][metric2] = 1.0
                    else:
                        # Calculate Pearson correlation using numpy
                        scores1 = np.array([all_scores[metric1][node] for node in common_nodes])
                        scores2 = np.array([all_scores[metric2][node] for node in common_nodes])
                        
                        # Calculate correlation coefficient
                        correlation = np.corrcoef(scores1, scores2)[0, 1]
                        correlation_matrix[metric1][metric2] = float(correlation) if not np.isnan(correlation) else 0.0
            
            return correlation_matrix
            
        except Exception as e:
            print(f"Error calculating correlation matrix: {e}")
            return {}
    
    def _calculate_graph_statistics(self, graph: nx.Graph) -> Dict[str, Any]:
        """Calculate overall graph statistics"""
        num_nodes = len(graph.nodes())
        num_edges = len(graph.edges())
        
        statistics = {
            "graph_size": num_nodes,
            "total_edges": num_edges,
            "graph_density": nx.density(graph),
            "average_degree": 2 * num_edges / num_nodes if num_nodes > 0 else 0.0
        }
        
        # Add connectivity information
        if nx.is_connected(graph):
            statistics["connected"] = True
            statistics["diameter"] = nx.diameter(graph)
            statistics["average_path_length"] = nx.average_shortest_path_length(graph)
        else:
            statistics["connected"] = False
            statistics["connected_components"] = nx.number_connected_components(graph)
            statistics["largest_component_size"] = len(max(nx.connected_components(graph), key=len))
        
        return statistics
    
    def _store_centrality_results(self, all_scores: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Store centrality results to Neo4j"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return {"status": "failed", "reason": "Neo4j not available"}
        
        try:
            with self.neo4j_tool.driver.session() as session:
                stored_count = 0
                
                # Get all nodes that have scores
                all_nodes = set()
                for scores in all_scores.values():
                    all_nodes.update(scores.keys())
                
                # Update each node with its centrality scores
                for node_id in all_nodes:
                    update_data = {"node_id": node_id, "timestamp": datetime.now().isoformat()}
                    
                    # Add all available centrality scores
                    for metric, scores in all_scores.items():
                        if node_id in scores:
                            update_data[f"{metric}_centrality"] = scores[node_id]
                    
                    # Build dynamic SET clause
                    set_clauses = [f"e.{key} = ${key}" for key in update_data.keys() if key != "node_id"]
                    set_clause = ", ".join(set_clauses)
                    
                    result = session.run(f"""
                    MATCH (e:Entity {{entity_id: $node_id}})
                    SET {set_clause}
                    RETURN e
                    """, update_data)
                    
                    if result.single():
                        stored_count += 1
                
                return {
                    "status": "success", 
                    "nodes_updated": stored_count,
                    "metrics_stored": list(all_scores.keys())
                }
                
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    
    def _calculate_academic_confidence(self, results: List[CentralityResult], 
                                     graph_stats: Dict[str, Any]) -> float:
        """Calculate academic-quality confidence for centrality analysis"""
        try:
            # Base confidence from successful metric calculations
            calculation_success = len(results) / 12  # 12 total possible metrics
            
            # Graph structure quality
            graph_quality = 0.0
            if graph_stats["graph_size"] > 0:
                # Reward well-connected graphs
                connectivity_factor = min(1.0, graph_stats["average_degree"] / 4.0)  # Good if avg degree >= 4
                density_factor = min(1.0, graph_stats["graph_density"] * 10)  # Reward reasonable density
                size_factor = min(1.0, graph_stats["graph_size"] / 100)  # Larger graphs are better
                
                graph_quality = (connectivity_factor * 0.4 + density_factor * 0.3 + size_factor * 0.3)
            
            # Statistical consistency (variance in execution times should be low)
            execution_times = [result.execution_time for result in results]
            if len(execution_times) > 1:
                time_consistency = 1.0 - min(1.0, np.std(execution_times) / np.mean(execution_times))
            else:
                time_consistency = 1.0
            
            # Combine factors
            combined_confidence = (
                calculation_success * 0.5 +
                graph_quality * 0.3 +
                time_consistency * 0.2
            )
            
            return max(0.1, min(1.0, combined_confidence))
            
        except Exception as e:
            print(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def _format_centrality_output(self, results: List[CentralityResult], 
                                correlation_matrix: Dict, overall_stats: Dict,
                                top_k: int, output_format: str) -> Dict[str, Any]:
        """Format centrality analysis output"""
        
        formatted_results = []
        
        for result in results:
            # Get top-k nodes for this metric
            sorted_nodes = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)
            top_nodes = [
                {
                    "node_id": node_id,
                    "score": score,
                    "rank": rank + 1
                }
                for rank, (node_id, score) in enumerate(sorted_nodes[:top_k])
            ]
            
            if output_format == "rankings_only":
                formatted_result = {
                    "metric": result.metric,
                    "top_nodes": top_nodes
                }
            elif output_format == "statistics_only":
                formatted_result = {
                    "metric": result.metric,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            elif output_format == "summary":
                formatted_result = {
                    "metric": result.metric,
                    "top_nodes": top_nodes[:5],  # Only top 5 for summary
                    "statistics": result.statistics,
                    "execution_time": result.execution_time
                }
            else:  # detailed
                formatted_result = {
                    "metric": result.metric,
                    "top_nodes": top_nodes,
                    "statistics": result.statistics,
                    "execution_time": result.execution_time,
                    "parameters": result.parameters
                }
            
            formatted_results.append(formatted_result)
        
        base_data = {
            "centrality_results": formatted_results,
            "overall_statistics": overall_stats
        }
        
        # Add correlation matrix for detailed output
        if output_format in ["detailed", "summary"]:
            base_data["correlation_matrix"] = correlation_matrix if correlation_matrix else {}
        
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
        elif "calculation" in error_message.lower():
            error_code = "CALCULATION_FAILED"
        elif "metric" in error_message.lower():
            error_code = "METRIC_NOT_SUPPORTED"
        
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
    tool = CentralityAnalysisTool()
    contract = tool.get_contract()
    print(f"Tool {tool.tool_id} initialized successfully")
    print(f"Contract: {contract.name}")
    print(f"Supported metrics: {[metric.value for metric in CentralityMetric]}")