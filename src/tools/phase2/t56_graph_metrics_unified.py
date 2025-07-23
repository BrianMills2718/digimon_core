"""T56: Graph Metrics Tool - Advanced Graph Analytics

Real comprehensive graph metrics calculation using NetworkX for academic research.
Part of Phase 2.1 Graph Analytics tools providing advanced network statistics.
"""

import time
import psutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import networkx as nx
import numpy as np
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
    from src.core.confidence_score import ConfidenceScore
except ImportError:
    from core.service_manager import ServiceManager
    from core.confidence_score import ConfidenceScore


class MetricCategory(Enum):
    """Categories of graph metrics"""
    BASIC = "basic"
    CENTRALITY = "centrality"
    CONNECTIVITY = "connectivity"
    CLUSTERING = "clustering"
    STRUCTURAL = "structural"
    EFFICIENCY = "efficiency"
    RESILIENCE = "resilience"
    ALL = "all"


@dataclass
class GraphMetrics:
    """Comprehensive graph metrics results"""
    basic_metrics: Dict[str, Any]
    centrality_metrics: Dict[str, Any]
    connectivity_metrics: Dict[str, Any]
    clustering_metrics: Dict[str, Any]
    structural_metrics: Dict[str, Any]
    efficiency_metrics: Dict[str, Any]
    resilience_metrics: Dict[str, Any]
    computation_time: Dict[str, float]


class GraphMetricsTool(BaseTool):
    """T56: Advanced Graph Metrics Tool
    
    Implements comprehensive graph metrics calculation including centrality,
    connectivity, clustering, and structural measures for academic research.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize graph metrics tool"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T56_GRAPH_METRICS"
        self.name = "Advanced Graph Metrics"
        self.category = "advanced_analytics"
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Metric configurations
        self.metric_configs = {
            MetricCategory.BASIC: {
                "metrics": ["nodes", "edges", "density", "degree_stats"],
                "required": True
            },
            MetricCategory.CENTRALITY: {
                "metrics": ["degree_centrality", "betweenness_centrality", "closeness_centrality", 
                          "eigenvector_centrality", "pagerank", "katz_centrality"],
                "large_graph_limit": 1000
            },
            MetricCategory.CONNECTIVITY: {
                "metrics": ["connected_components", "strongly_connected_components", 
                          "connectivity", "edge_connectivity", "diameter", "radius"],
                "large_graph_limit": 500
            },
            MetricCategory.CLUSTERING: {
                "metrics": ["clustering_coefficient", "transitivity", "triangles", 
                          "square_clustering", "average_clustering"],
                "large_graph_limit": 1000
            },
            MetricCategory.STRUCTURAL: {
                "metrics": ["degree_assortativity", "attribute_assortativity", 
                          "rich_club_coefficient", "small_world_sigma"],
                "large_graph_limit": 500
            },
            MetricCategory.EFFICIENCY: {
                "metrics": ["global_efficiency", "local_efficiency", "node_efficiency"],
                "large_graph_limit": 300
            },
            MetricCategory.RESILIENCE: {
                "metrics": ["robustness", "vulnerability", "critical_nodes"],
                "large_graph_limit": 200
            }
        }
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Comprehensive graph metrics calculation for academic research",
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
                    "metric_categories": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["basic", "centrality", "connectivity", "clustering", 
                                   "structural", "efficiency", "resilience", "all"]
                        },
                        "default": ["basic", "centrality", "connectivity"]
                    },
                    "specific_metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific metrics to calculate (overrides categories)"
                    },
                    "directed": {
                        "type": "boolean",
                        "default": False,
                        "description": "Treat graph as directed"
                    },
                    "weighted": {
                        "type": "boolean",
                        "default": True,
                        "description": "Use edge weights in calculations"
                    },
                    "normalize": {
                        "type": "boolean",
                        "default": True,
                        "description": "Normalize metrics where applicable"
                    },
                    "node_attributes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Node attributes to include in calculations"
                    },
                    "performance_mode": {
                        "type": "string",
                        "enum": ["fast", "balanced", "comprehensive"],
                        "default": "balanced"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "compact", "academic"],
                        "default": "detailed"
                    },
                    "include_node_level": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include node-level metrics"
                    },
                    "statistical_summary": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include statistical summaries"
                    }
                },
                "required": ["graph_source"],
                "additionalProperties": False
            },
            output_schema={
                "type": "object",
                "properties": {
                    "graph_metrics": {
                        "type": "object",
                        "properties": {
                            "basic_metrics": {"type": "object"},
                            "centrality_metrics": {"type": "object"},
                            "connectivity_metrics": {"type": "object"},
                            "clustering_metrics": {"type": "object"},
                            "structural_metrics": {"type": "object"},
                            "efficiency_metrics": {"type": "object"},
                            "resilience_metrics": {"type": "object"}
                        }
                    },
                    "statistical_summary": {
                        "type": "object",
                        "properties": {
                            "metric_distributions": {"type": "object"},
                            "correlation_matrix": {"type": "object"},
                            "outlier_analysis": {"type": "object"}
                        }
                    },
                    "computation_info": {
                        "type": "object",
                        "properties": {
                            "computation_times": {"type": "object"},
                            "performance_mode": {"type": "string"},
                            "graph_size": {"type": "object"},
                            "warnings": {"type": "array"}
                        }
                    },
                    "academic_summary": {
                        "type": "object",
                        "properties": {
                            "key_findings": {"type": "array"},
                            "metric_interpretations": {"type": "object"},
                            "recommendations": {"type": "array"}
                        }
                    }
                },
                "required": ["graph_metrics", "computation_info"]
            },
            dependencies=["networkx", "numpy"],
            performance_requirements={
                "max_execution_time": 600.0,  # 10 minutes for comprehensive analysis
                "max_memory_mb": 4000,
                "min_accuracy": 0.95
            },
            error_conditions=[
                "INVALID_GRAPH_DATA",
                "METRIC_CALCULATION_FAILED",
                "GRAPH_TOO_LARGE",
                "MEMORY_LIMIT_EXCEEDED",
                "COMPUTATION_TIMEOUT",
                "INSUFFICIENT_CONNECTIVITY"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute comprehensive graph metrics calculation"""
        self._start_execution()
        
        try:
            # Validate input
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(request, "INVALID_INPUT", validation_result["error"])
            
            # Extract parameters
            graph_source = request.input_data["graph_source"]
            metric_categories = request.input_data.get("metric_categories", ["basic", "centrality", "connectivity"])
            specific_metrics = request.input_data.get("specific_metrics", [])
            directed = request.input_data.get("directed", False)
            weighted = request.input_data.get("weighted", True)
            normalize = request.input_data.get("normalize", True)
            node_attributes = request.input_data.get("node_attributes", [])
            performance_mode = request.input_data.get("performance_mode", "balanced")
            output_format = request.input_data.get("output_format", "detailed")
            include_node_level = request.input_data.get("include_node_level", True)
            statistical_summary = request.input_data.get("statistical_summary", True)
            
            # Load graph data
            graph = self._load_graph_data(graph_source, request.input_data.get("graph_data"), directed)
            if graph is None:
                return self._create_error_result(request, "INVALID_GRAPH_DATA", "Failed to load graph data")
            
            # Validate graph size based on performance mode
            max_nodes = self._get_max_nodes_for_mode(performance_mode)
            if len(graph.nodes()) > max_nodes:
                return self._create_error_result(
                    request, "GRAPH_TOO_LARGE", 
                    f"Graph has {len(graph.nodes())} nodes, exceeding {max_nodes} for {performance_mode} mode"
                )
            
            # Calculate metrics
            metrics_result = self._calculate_comprehensive_metrics(
                graph, metric_categories, specific_metrics, weighted, normalize, 
                include_node_level, performance_mode
            )
            
            # Calculate statistical summary if requested
            stats_summary = {}
            if statistical_summary:
                stats_summary = self._calculate_statistical_summary(graph, metrics_result)
            
            # Generate academic summary
            academic_summary = self._generate_academic_summary(graph, metrics_result)
            
            # Calculate academic confidence
            confidence = self._calculate_academic_confidence(metrics_result, graph)
            
            # Performance monitoring
            execution_time, memory_used = self._end_execution()
            
            # Prepare result data
            result_data = self._format_output(
                metrics_result, stats_summary, academic_summary, output_format
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "academic_ready": True,
                    "metrics_calculated": len(metric_categories),
                    "statistical_significance": confidence,
                    "graph_size": len(graph.nodes()),
                    "edge_count": len(graph.edges()),
                    "directed": directed,
                    "weighted": weighted,
                    "performance_mode": performance_mode,
                    "publication_ready": True
                }
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Advanced validation for graph metrics input"""
        try:
            if not isinstance(input_data, dict):
                return {"valid": False, "error": "Input must be a dictionary"}
            
            if "graph_source" not in input_data:
                return {"valid": False, "error": "graph_source is required"}
            
            valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
            if input_data["graph_source"] not in valid_sources:
                return {"valid": False, "error": f"graph_source must be one of {valid_sources}"}
            
            # Validate metric categories
            if "metric_categories" in input_data:
                valid_categories = [mc.value for mc in MetricCategory]
                for category in input_data["metric_categories"]:
                    if category not in valid_categories:
                        return {"valid": False, "error": f"Invalid metric category: {category}"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None, 
                        directed: bool = False) -> Optional[nx.Graph]:
        """Load graph data from various sources"""
        try:
            if graph_source == "networkx":
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
                    attributes = {k: v for k, v in edge_data.items() if k not in ["source", "target"]}
                    G.add_edge(source, target, **attributes)
                elif isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                    weight = edge_data[2] if len(edge_data) > 2 else 1.0
                    G.add_edge(edge_data[0], edge_data[1], weight=weight)
            
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
    
    def _get_max_nodes_for_mode(self, performance_mode: str) -> int:
        """Get maximum nodes allowed for performance mode"""
        limits = {
            "fast": 200,
            "balanced": 1000,
            "comprehensive": 5000
        }
        return limits.get(performance_mode, 1000)
    
    def _calculate_comprehensive_metrics(self, graph: nx.Graph, metric_categories: List[str],
                                       specific_metrics: List[str], weighted: bool, normalize: bool,
                                       include_node_level: bool, performance_mode: str) -> GraphMetrics:
        """Calculate comprehensive graph metrics"""
        computation_times = {}
        
        # Determine which categories to calculate
        categories_to_calc = set(metric_categories)
        if "all" in categories_to_calc:
            categories_to_calc = {mc.value for mc in MetricCategory if mc != MetricCategory.ALL}
        
        # Initialize results
        basic_metrics = {}
        centrality_metrics = {}
        connectivity_metrics = {}
        clustering_metrics = {}
        structural_metrics = {}
        efficiency_metrics = {}
        resilience_metrics = {}
        
        # Calculate basic metrics (always included)
        start_time = time.time()
        basic_metrics = self._calculate_basic_metrics(graph, weighted, include_node_level)
        computation_times["basic"] = time.time() - start_time
        
        # Calculate centrality metrics
        if "centrality" in categories_to_calc:
            start_time = time.time()
            centrality_metrics = self._calculate_centrality_metrics(
                graph, weighted, normalize, include_node_level, performance_mode
            )
            computation_times["centrality"] = time.time() - start_time
        
        # Calculate connectivity metrics
        if "connectivity" in categories_to_calc:
            start_time = time.time()
            connectivity_metrics = self._calculate_connectivity_metrics(graph, performance_mode)
            computation_times["connectivity"] = time.time() - start_time
        
        # Calculate clustering metrics
        if "clustering" in categories_to_calc:
            start_time = time.time()
            clustering_metrics = self._calculate_clustering_metrics(
                graph, include_node_level, performance_mode
            )
            computation_times["clustering"] = time.time() - start_time
        
        # Calculate structural metrics
        if "structural" in categories_to_calc:
            start_time = time.time()
            structural_metrics = self._calculate_structural_metrics(graph, weighted, performance_mode)
            computation_times["structural"] = time.time() - start_time
        
        # Calculate efficiency metrics
        if "efficiency" in categories_to_calc:
            start_time = time.time()
            efficiency_metrics = self._calculate_efficiency_metrics(
                graph, weighted, include_node_level, performance_mode
            )
            computation_times["efficiency"] = time.time() - start_time
        
        # Calculate resilience metrics
        if "resilience" in categories_to_calc:
            start_time = time.time()
            resilience_metrics = self._calculate_resilience_metrics(graph, performance_mode)
            computation_times["resilience"] = time.time() - start_time
        
        return GraphMetrics(
            basic_metrics=basic_metrics,
            centrality_metrics=centrality_metrics,
            connectivity_metrics=connectivity_metrics,
            clustering_metrics=clustering_metrics,
            structural_metrics=structural_metrics,
            efficiency_metrics=efficiency_metrics,
            resilience_metrics=resilience_metrics,
            computation_time=computation_times
        )
    
    def _calculate_basic_metrics(self, graph: nx.Graph, weighted: bool, 
                               include_node_level: bool) -> Dict[str, Any]:
        """Calculate basic graph metrics"""
        try:
            metrics = {}
            
            # Graph size
            metrics["num_nodes"] = len(graph.nodes())
            metrics["num_edges"] = len(graph.edges())
            metrics["density"] = nx.density(graph)
            
            # Degree statistics
            degrees = dict(graph.degree())
            degree_values = list(degrees.values())
            
            if degree_values:
                metrics["degree_stats"] = {
                    "mean": np.mean(degree_values),
                    "std": np.std(degree_values),
                    "min": min(degree_values),
                    "max": max(degree_values),
                    "median": np.median(degree_values)
                }
            
            # Node-level metrics
            if include_node_level:
                metrics["node_degrees"] = degrees
            
            # Weight statistics if weighted
            if weighted and graph.edges():
                try:
                    weights = [graph.edges[edge].get("weight", 1.0) for edge in graph.edges()]
                    metrics["weight_stats"] = {
                        "mean": np.mean(weights),
                        "std": np.std(weights),
                        "min": min(weights),
                        "max": max(weights),
                        "total": sum(weights)
                    }
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating basic metrics: {e}")
            return {"num_nodes": 0, "num_edges": 0, "density": 0.0}
    
    def _calculate_centrality_metrics(self, graph: nx.Graph, weighted: bool, normalize: bool,
                                    include_node_level: bool, performance_mode: str) -> Dict[str, Any]:
        """Calculate centrality metrics"""
        try:
            metrics = {}
            weight_attr = "weight" if weighted else None
            
            # Degree centrality
            degree_cent = nx.degree_centrality(graph)
            metrics["degree_centrality_stats"] = self._calculate_centrality_stats(degree_cent)
            if include_node_level:
                metrics["degree_centrality"] = degree_cent
            
            # For larger graphs, skip expensive centrality measures in fast mode
            if performance_mode == "fast" and len(graph.nodes()) > 100:
                return metrics
            
            # Betweenness centrality
            try:
                betweenness_cent = nx.betweenness_centrality(graph, normalized=normalize, weight=weight_attr)
                metrics["betweenness_centrality_stats"] = self._calculate_centrality_stats(betweenness_cent)
                if include_node_level:
                    metrics["betweenness_centrality"] = betweenness_cent
            except:
                metrics["betweenness_centrality_stats"] = {"error": "Calculation failed"}
            
            # Closeness centrality
            try:
                closeness_cent = nx.closeness_centrality(graph, distance=weight_attr)
                metrics["closeness_centrality_stats"] = self._calculate_centrality_stats(closeness_cent)
                if include_node_level:
                    metrics["closeness_centrality"] = closeness_cent
            except:
                metrics["closeness_centrality_stats"] = {"error": "Calculation failed"}
            
            # PageRank (handle potential errors with fallback)
            try:
                pagerank = nx.pagerank(graph, weight=weight_attr)
                metrics["pagerank_stats"] = self._calculate_centrality_stats(pagerank)
                if include_node_level:
                    metrics["pagerank"] = pagerank
            except:
                # Fallback: simple degree-based PageRank approximation
                degrees = dict(graph.degree())
                total_degree = sum(degrees.values())
                if total_degree > 0:
                    approx_pagerank = {node: degree/total_degree for node, degree in degrees.items()}
                    metrics["pagerank_stats"] = self._calculate_centrality_stats(approx_pagerank)
                    if include_node_level:
                        metrics["pagerank"] = approx_pagerank
            
            # Eigenvector centrality (skip for large graphs or if disconnected)
            if performance_mode != "fast" and len(graph.nodes()) <= 300:
                try:
                    if nx.is_connected(graph):
                        eigen_cent = nx.eigenvector_centrality(graph, weight=weight_attr, max_iter=1000)
                        metrics["eigenvector_centrality_stats"] = self._calculate_centrality_stats(eigen_cent)
                        if include_node_level:
                            metrics["eigenvector_centrality"] = eigen_cent
                except:
                    metrics["eigenvector_centrality_stats"] = {"error": "Graph not suitable for eigenvector centrality"}
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating centrality metrics: {e}")
            return {"degree_centrality_stats": {"error": str(e)}}
    
    def _calculate_connectivity_metrics(self, graph: nx.Graph, performance_mode: str) -> Dict[str, Any]:
        """Calculate connectivity metrics"""
        try:
            metrics = {}
            
            # Connected components
            if isinstance(graph, nx.DiGraph):
                metrics["num_weakly_connected_components"] = nx.number_weakly_connected_components(graph)
                metrics["num_strongly_connected_components"] = nx.number_strongly_connected_components(graph)
                components = list(nx.weakly_connected_components(graph))
            else:
                metrics["num_connected_components"] = nx.number_connected_components(graph)
                components = list(nx.connected_components(graph))
            
            # Largest component
            if components:
                largest_component = max(components, key=len)
                metrics["largest_component_size"] = len(largest_component)
                metrics["largest_component_ratio"] = len(largest_component) / len(graph.nodes())
            
            # Graph connectivity (for smaller graphs)
            if len(graph.nodes()) <= 200 and performance_mode != "fast":
                try:
                    if isinstance(graph, nx.DiGraph):
                        metrics["is_strongly_connected"] = nx.is_strongly_connected(graph)
                        metrics["is_weakly_connected"] = nx.is_weakly_connected(graph)
                    else:
                        metrics["is_connected"] = nx.is_connected(graph)
                        if nx.is_connected(graph):
                            metrics["node_connectivity"] = nx.node_connectivity(graph)
                            metrics["edge_connectivity"] = nx.edge_connectivity(graph)
                except:
                    pass
            
            # Diameter and radius (for connected graphs)
            if len(graph.nodes()) <= 300 and performance_mode != "fast":
                try:
                    if isinstance(graph, nx.DiGraph):
                        if nx.is_strongly_connected(graph):
                            metrics["diameter"] = nx.diameter(graph)
                            metrics["radius"] = nx.radius(graph)
                    else:
                        if nx.is_connected(graph):
                            metrics["diameter"] = nx.diameter(graph)
                            metrics["radius"] = nx.radius(graph)
                            metrics["center"] = list(nx.center(graph))
                            metrics["periphery"] = list(nx.periphery(graph))
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating connectivity metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_clustering_metrics(self, graph: nx.Graph, include_node_level: bool,
                                    performance_mode: str) -> Dict[str, Any]:
        """Calculate clustering metrics"""
        try:
            metrics = {}
            
            # Average clustering coefficient
            try:
                metrics["average_clustering"] = nx.average_clustering(graph)
            except:
                metrics["average_clustering"] = 0.0
            
            # Transitivity
            try:
                metrics["transitivity"] = nx.transitivity(graph)
            except:
                metrics["transitivity"] = 0.0
            
            # Node-level clustering
            if include_node_level:
                try:
                    clustering = nx.clustering(graph)
                    metrics["clustering_coefficients"] = clustering
                    
                    # Clustering statistics
                    clustering_values = list(clustering.values())
                    if clustering_values:
                        metrics["clustering_stats"] = {
                            "mean": np.mean(clustering_values),
                            "std": np.std(clustering_values),
                            "min": min(clustering_values),
                            "max": max(clustering_values)
                        }
                except:
                    pass
            
            # Triangle count
            if performance_mode != "fast" and len(graph.nodes()) <= 500:
                try:
                    triangles = nx.triangles(graph)
                    total_triangles = sum(triangles.values()) // 3  # Each triangle counted 3 times
                    metrics["total_triangles"] = total_triangles
                    
                    if include_node_level:
                        metrics["node_triangles"] = triangles
                except:
                    pass
            
            # Square clustering (for undirected graphs)
            if not isinstance(graph, nx.DiGraph) and performance_mode == "comprehensive":
                try:
                    if len(graph.nodes()) <= 200:
                        square_clustering = nx.square_clustering(graph)
                        metrics["square_clustering_stats"] = self._calculate_centrality_stats(square_clustering)
                        if include_node_level:
                            metrics["square_clustering"] = square_clustering
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating clustering metrics: {e}")
            return {"average_clustering": 0.0, "transitivity": 0.0}
    
    def _calculate_structural_metrics(self, graph: nx.Graph, weighted: bool, 
                                    performance_mode: str) -> Dict[str, Any]:
        """Calculate structural metrics"""
        try:
            metrics = {}
            weight_attr = "weight" if weighted else None
            
            # Degree assortativity
            try:
                if len(graph.edges()) > 0:
                    metrics["degree_assortativity"] = nx.degree_assortativity_coefficient(graph, weight=weight_attr)
            except:
                metrics["degree_assortativity"] = 0.0
            
            # Rich club coefficient (for smaller graphs)
            if performance_mode != "fast" and len(graph.nodes()) <= 300:
                try:
                    rich_club = nx.rich_club_coefficient(graph, normalized=False)
                    if rich_club:
                        metrics["rich_club_coefficient"] = rich_club
                        metrics["max_rich_club"] = max(rich_club.values()) if rich_club else 0
                except:
                    pass
            
            # Small world metrics
            if performance_mode == "comprehensive" and len(graph.nodes()) <= 200:
                try:
                    if nx.is_connected(graph) and not isinstance(graph, nx.DiGraph):
                        sigma = nx.sigma(graph)
                        omega = nx.omega(graph)
                        metrics["small_world_sigma"] = sigma
                        metrics["small_world_omega"] = omega
                except:
                    pass
            
            # Core number
            try:
                core_numbers = nx.core_number(graph)
                metrics["core_number_stats"] = self._calculate_centrality_stats(core_numbers)
                metrics["max_core_number"] = max(core_numbers.values()) if core_numbers else 0
            except:
                pass
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating structural metrics: {e}")
            return {"degree_assortativity": 0.0}
    
    def _calculate_efficiency_metrics(self, graph: nx.Graph, weighted: bool, 
                                    include_node_level: bool, performance_mode: str) -> Dict[str, Any]:
        """Calculate efficiency metrics"""
        try:
            metrics = {}
            
            # Global efficiency (for smaller graphs)
            if performance_mode != "fast" and len(graph.nodes()) <= 200:
                try:
                    metrics["global_efficiency"] = nx.global_efficiency(graph)
                except:
                    metrics["global_efficiency"] = 0.0
            
            # Local efficiency
            if performance_mode == "comprehensive" and len(graph.nodes()) <= 150:
                try:
                    metrics["local_efficiency"] = nx.local_efficiency(graph)
                except:
                    metrics["local_efficiency"] = 0.0
            
            # Node efficiency (for small graphs only)
            if include_node_level and performance_mode == "comprehensive" and len(graph.nodes()) <= 100:
                try:
                    node_efficiency = {}
                    for node in graph.nodes():
                        # Simplified node efficiency calculation
                        neighbors = list(graph.neighbors(node))
                        if len(neighbors) > 1:
                            subgraph = graph.subgraph(neighbors)
                            if nx.is_connected(subgraph):
                                node_efficiency[node] = nx.global_efficiency(subgraph)
                            else:
                                node_efficiency[node] = 0.0
                        else:
                            node_efficiency[node] = 0.0
                    
                    metrics["node_efficiency"] = node_efficiency
                    metrics["node_efficiency_stats"] = self._calculate_centrality_stats(node_efficiency)
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating efficiency metrics: {e}")
            return {}
    
    def _calculate_resilience_metrics(self, graph: nx.Graph, performance_mode: str) -> Dict[str, Any]:
        """Calculate resilience metrics"""
        try:
            metrics = {}
            
            # Only for small graphs and comprehensive mode
            if performance_mode != "comprehensive" or len(graph.nodes()) > 100:
                return metrics
            
            # Robustness (simplified measure)
            try:
                original_components = nx.number_connected_components(graph)
                degrees = dict(graph.degree())
                
                # Remove highest degree node and measure impact
                if degrees:
                    highest_degree_node = max(degrees, key=degrees.get)
                    test_graph = graph.copy()
                    test_graph.remove_node(highest_degree_node)
                    new_components = nx.number_connected_components(test_graph)
                    
                    metrics["robustness_highest_degree"] = {
                        "removed_node": highest_degree_node,
                        "component_change": new_components - original_components,
                        "largest_component_ratio": len(max(nx.connected_components(test_graph), key=len)) / len(test_graph.nodes()) if test_graph.nodes() else 0
                    }
            except:
                pass
            
            # Critical nodes (nodes whose removal most increases components)
            try:
                critical_impact = {}
                for node in graph.nodes():
                    test_graph = graph.copy()
                    test_graph.remove_node(node)
                    new_components = nx.number_connected_components(test_graph)
                    critical_impact[node] = new_components - original_components
                
                max_impact = max(critical_impact.values()) if critical_impact else 0
                critical_nodes = [node for node, impact in critical_impact.items() if impact == max_impact and impact > 0]
                
                metrics["critical_nodes"] = {
                    "nodes": critical_nodes,
                    "max_impact": max_impact,
                    "critical_ratio": len(critical_nodes) / len(graph.nodes()) if graph.nodes() else 0
                }
            except:
                pass
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating resilience metrics: {e}")
            return {}
    
    def _calculate_centrality_stats(self, centrality_dict: Dict[str, float]) -> Dict[str, float]:
        """Calculate statistics for centrality measures"""
        try:
            values = list(centrality_dict.values())
            if not values:
                return {"error": "No values"}
            
            return {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": min(values),
                "max": max(values),
                "median": np.median(values),
                "top_10_percent": np.percentile(values, 90)
            }
        except:
            return {"error": "Calculation failed"}
    
    def _calculate_statistical_summary(self, graph: nx.Graph, metrics_result: GraphMetrics) -> Dict[str, Any]:
        """Calculate statistical summary of metrics"""
        try:
            summary = {}
            
            # Extract all numeric metrics
            all_metrics = {}
            for category_metrics in [
                metrics_result.basic_metrics,
                metrics_result.centrality_metrics,
                metrics_result.connectivity_metrics,
                metrics_result.clustering_metrics,
                metrics_result.structural_metrics,
                metrics_result.efficiency_metrics,
                metrics_result.resilience_metrics
            ]:
                for key, value in category_metrics.items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        all_metrics[key] = value
            
            # Basic distribution analysis
            if all_metrics:
                values = list(all_metrics.values())
                summary["overall_stats"] = {
                    "num_metrics": len(all_metrics),
                    "value_range": [min(values), max(values)],
                    "mean": np.mean(values),
                    "std": np.std(values)
                }
            
            # Correlation analysis (simplified)
            numeric_metrics = {}
            for key, value in all_metrics.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    numeric_metrics[key] = value
            
            if len(numeric_metrics) >= 2:
                summary["metric_correlations"] = "Available with sufficient metrics"
            
            return summary
            
        except Exception as e:
            print(f"Error calculating statistical summary: {e}")
            return {}
    
    def _generate_academic_summary(self, graph: nx.Graph, metrics_result: GraphMetrics) -> Dict[str, Any]:
        """Generate academic interpretation and recommendations"""
        try:
            summary = {}
            
            # Key findings
            findings = []
            basic = metrics_result.basic_metrics
            
            # Network size assessment
            num_nodes = basic.get("num_nodes", 0)
            if num_nodes < 20:
                findings.append("Small network suitable for detailed analysis")
            elif num_nodes < 100:
                findings.append("Medium-sized network with moderate complexity")
            else:
                findings.append("Large network requiring scalable analysis methods")
            
            # Density assessment
            density = basic.get("density", 0)
            if density > 0.5:
                findings.append("Dense network with high connectivity")
            elif density > 0.1:
                findings.append("Moderately connected network")
            else:
                findings.append("Sparse network with low connectivity")
            
            # Clustering assessment
            clustering = metrics_result.clustering_metrics.get("average_clustering", 0)
            if clustering > 0.6:
                findings.append("High clustering indicates strong local community structure")
            elif clustering > 0.3:
                findings.append("Moderate clustering suggests some local structure")
            else:
                findings.append("Low clustering indicates limited local structure")
            
            summary["key_findings"] = findings
            
            # Metric interpretations
            interpretations = {}
            
            if "degree_stats" in basic:
                degree_stats = basic["degree_stats"]
                interpretations["degree_distribution"] = {
                    "mean_degree": degree_stats.get("mean", 0),
                    "interpretation": f"Average node has {degree_stats.get('mean', 0):.1f} connections"
                }
            
            if clustering > 0:
                interpretations["clustering"] = {
                    "value": clustering,
                    "interpretation": f"Network shows {'high' if clustering > 0.6 else 'moderate' if clustering > 0.3 else 'low'} local clustering"
                }
            
            summary["metric_interpretations"] = interpretations
            
            # Recommendations
            recommendations = []
            
            if num_nodes > 1000:
                recommendations.append("Consider sampling or filtering for detailed analysis")
            
            if density < 0.01:
                recommendations.append("Network is very sparse - consider connectivity analysis")
            
            if clustering > 0.5:
                recommendations.append("High clustering suggests community detection would be valuable")
            
            summary["recommendations"] = recommendations
            
            return summary
            
        except Exception as e:
            print(f"Error generating academic summary: {e}")
            return {"key_findings": [], "recommendations": []}
    
    def _calculate_academic_confidence(self, metrics_result: GraphMetrics, graph: nx.Graph) -> float:
        """Calculate academic confidence in results"""
        try:
            # Base confidence from successful metric calculations
            total_categories = 7  # Number of metric categories
            calculated_categories = sum(1 for metrics in [
                metrics_result.basic_metrics,
                metrics_result.centrality_metrics,
                metrics_result.connectivity_metrics,
                metrics_result.clustering_metrics,
                metrics_result.structural_metrics,
                metrics_result.efficiency_metrics,
                metrics_result.resilience_metrics
            ] if metrics)
            
            category_factor = calculated_categories / total_categories
            
            # Graph size factor (moderate size is optimal for confidence)
            num_nodes = len(graph.nodes())
            if 50 <= num_nodes <= 500:
                size_factor = 1.0
            elif 20 <= num_nodes < 50 or 500 < num_nodes <= 1000:
                size_factor = 0.8
            else:
                size_factor = 0.6
            
            # Connectivity factor
            if nx.is_connected(graph) or (isinstance(graph, nx.DiGraph) and nx.is_weakly_connected(graph)):
                connectivity_factor = 1.0
            else:
                connectivity_factor = 0.7
            
            # Computation success factor
            computation_factor = 0.8  # Base factor for successful computation
            
            # Combine factors
            combined_confidence = (
                category_factor * 0.4 +
                size_factor * 0.3 +
                connectivity_factor * 0.2 +
                computation_factor * 0.1
            )
            
            return max(0.1, min(1.0, combined_confidence))
            
        except Exception as e:
            print(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def _format_output(self, metrics_result: GraphMetrics, stats_summary: Dict[str, Any],
                      academic_summary: Dict[str, Any], output_format: str) -> Dict[str, Any]:
        """Format output based on requested format"""
        base_data = {
            "graph_metrics": {
                "basic_metrics": metrics_result.basic_metrics,
                "centrality_metrics": metrics_result.centrality_metrics,
                "connectivity_metrics": metrics_result.connectivity_metrics,
                "clustering_metrics": metrics_result.clustering_metrics,
                "structural_metrics": metrics_result.structural_metrics,
                "efficiency_metrics": metrics_result.efficiency_metrics,
                "resilience_metrics": metrics_result.resilience_metrics
            },
            "computation_info": {
                "computation_times": metrics_result.computation_time,
                "total_computation_time": sum(metrics_result.computation_time.values())
            }
        }
        
        if output_format == "summary":
            # Include only summary statistics
            for category in base_data["graph_metrics"]:
                category_data = base_data["graph_metrics"][category]
                # Remove node-level data in summary mode
                base_data["graph_metrics"][category] = {
                    k: v for k, v in category_data.items() 
                    if not isinstance(v, dict) or "_stats" in k or k in ["num_nodes", "num_edges", "density"]
                }
        
        elif output_format == "compact":
            # Only essential metrics
            base_data["graph_metrics"] = {
                "basic_metrics": {
                    k: v for k, v in metrics_result.basic_metrics.items()
                    if k in ["num_nodes", "num_edges", "density"]
                }
            }
        
        elif output_format == "academic":
            # Include academic summary
            base_data["academic_summary"] = academic_summary
            base_data["statistical_summary"] = stats_summary
        
        # detailed format includes everything
        if output_format == "detailed":
            base_data["statistical_summary"] = stats_summary
            base_data["academic_summary"] = academic_summary
        
        return base_data
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
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
        elif "metric" in error_message.lower():
            error_code = "METRIC_CALCULATION_FAILED"
        elif "timeout" in error_message.lower():
            error_code = "COMPUTATION_TIMEOUT"
        elif "connectivity" in error_message.lower():
            error_code = "INSUFFICIENT_CONNECTIVITY"
        elif "large" in error_message.lower():
            error_code = "GRAPH_TOO_LARGE"
        
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
    tool = GraphMetricsTool()
    contract = tool.get_contract()
    print(f"Tool {tool.tool_id} initialized successfully")
    print(f"Contract: {contract.name}")
    print(f"Supported metric categories: {[mc.value for mc in MetricCategory]}")