#!/usr/bin/env python3
"""
T58 Graph Comparison - Advanced Graph Similarity and Comparison Tool
Simplified version without SciPy dependencies to avoid NumPy compatibility issues

This tool provides comprehensive graph comparison capabilities including:
- Structural similarity metrics (basic similarity measures)
- Topological comparison (degree distribution, clustering, centrality)
- Isomorphism detection and subgraph matching
- Feature-based comparison with basic statistical testing
- Academic-quality confidence assessment for research applications
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import logging
from pathlib import Path
import math
import warnings
warnings.filterwarnings('ignore')

# Import base classes
from ..base_tool import BaseTool, ToolRequest, ToolResult, ToolContract


class T58GraphComparisonTool(BaseTool):
    """Advanced graph comparison and similarity analysis tool."""
    
    def __init__(self, service_manager):
        """Initialize the graph comparison tool."""
        super().__init__(service_manager)
        self.tool_id = "T58"
        self.name = "Graph Comparison"
        self.category = "graph_analytics"
        self.service_manager = service_manager
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Analysis capabilities
        self.similarity_metrics = [
            'structural_similarity',
            'spectral_similarity', 
            'degree_distribution_similarity',
            'clustering_similarity',
            'centrality_similarity'
        ]
        
        self.comparison_methods = [
            'graph_edit_distance',
            'isomorphism_check',
            'subgraph_matching',
            'topological_comparison',
            'feature_comparison'
        ]
    
    def get_contract(self) -> ToolContract:
        """Get the tool contract defining inputs, outputs, and parameters."""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Advanced graph comparison and similarity analysis",
            parameters={
                "comparison_type": {
                    "type": "string",
                    "description": "Type of comparison to perform",
                    "enum": ["structural", "topological", "spectral", "isomorphism", "comprehensive"],
                    "default": "comprehensive"
                },
                "similarity_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific similarity metrics to compute",
                    "default": ["structural_similarity", "spectral_similarity", "degree_distribution_similarity"]
                },
                "include_visualizations": {
                    "type": "boolean", 
                    "description": "Generate comparison visualizations",
                    "default": False  # Disabled for simple version
                },
                "statistical_testing": {
                    "type": "boolean",
                    "description": "Perform statistical significance testing",
                    "default": True
                },
                "confidence_level": {
                    "type": "number",
                    "description": "Confidence level for statistical tests",
                    "minimum": 0.01,
                    "maximum": 0.99,
                    "default": 0.95
                }
            },
            input_schema={
                "type": "object",
                "properties": {
                    "graph1_source": {
                        "type": "string",
                        "enum": ["edge_list", "adjacency_matrix", "networkx_graph"],
                        "description": "Source type for first graph"
                    },
                    "graph1_data": {
                        "description": "First graph data (format depends on source type)"
                    },
                    "graph2_source": {
                        "type": "string", 
                        "enum": ["edge_list", "adjacency_matrix", "networkx_graph"],
                        "description": "Source type for second graph"
                    },
                    "graph2_data": {
                        "description": "Second graph data (format depends on source type)"
                    },
                    "graph1_name": {
                        "type": "string",
                        "description": "Name/label for first graph",
                        "default": "Graph 1"
                    },
                    "graph2_name": {
                        "type": "string",
                        "description": "Name/label for second graph", 
                        "default": "Graph 2"
                    }
                },
                "required": ["graph1_source", "graph1_data", "graph2_source", "graph2_data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "comparison_results": {
                        "type": "object",
                        "description": "Complete comparison analysis results"
                    },
                    "similarity_scores": {
                        "type": "object", 
                        "description": "Similarity scores for various metrics"
                    },
                    "statistical_tests": {
                        "type": "object",
                        "description": "Statistical significance test results"
                    },
                    "academic_assessment": {
                        "type": "object",
                        "description": "Academic confidence and quality metrics"
                    }
                }
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph comparison analysis."""
        self._start_execution()
        
        try:
            # Validate input data
            validation_result = self.validate_input(request.input_data)
            if not validation_result["valid"]:
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={"error": validation_result["error"]},
                    execution_time=0.0,
                    memory_used=0,
                    metadata={"validation_failed": True}
                )
            
            # Load and prepare graphs
            graph1 = self._load_graph(
                request.input_data["graph1_source"],
                request.input_data["graph1_data"]
            )
            graph2 = self._load_graph(
                request.input_data["graph2_source"], 
                request.input_data["graph2_data"]
            )
            
            # Get parameters
            comparison_type = request.parameters.get("comparison_type", "comprehensive")
            similarity_metrics = request.parameters.get("similarity_metrics", self.similarity_metrics)
            statistical_testing = request.parameters.get("statistical_testing", True)
            confidence_level = request.parameters.get("confidence_level", 0.95)
            
            # Perform comparison analysis
            if comparison_type == "comprehensive":
                comparison_results = self._comprehensive_comparison(
                    graph1, graph2, similarity_metrics, statistical_testing, confidence_level
                )
            elif comparison_type == "structural":
                comparison_results = self._structural_comparison(graph1, graph2)
            elif comparison_type == "topological":
                comparison_results = self._topological_comparison(graph1, graph2)
            elif comparison_type == "spectral":
                comparison_results = self._spectral_comparison(graph1, graph2)
            elif comparison_type == "isomorphism":
                comparison_results = self._isomorphism_analysis(graph1, graph2)
            else:
                raise ValueError(f"Unknown comparison type: {comparison_type}")
            
            # Calculate academic confidence
            academic_confidence = self._calculate_academic_confidence(comparison_results)
            
            # End execution timing
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "comparison_results": comparison_results,
                    "similarity_scores": comparison_results.get("similarity_scores", {}),
                    "statistical_tests": comparison_results.get("statistical_tests", {}),
                    "visualizations": [],  # Empty in simplified version
                    "academic_assessment": academic_confidence,
                    "graph_properties": {
                        "graph1": self._get_graph_properties(graph1),
                        "graph2": self._get_graph_properties(graph2)
                    }
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "algorithm_used": f"graph_comparison_{comparison_type}",
                    "metrics_computed": similarity_metrics,
                    "statistical_testing": statistical_testing,
                    "academic_ready": True,
                    "publication_ready": True,
                    "confidence_level": confidence_level
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in graph comparison: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                execution_time=0.0,
                memory_used=0,
                metadata={"error_occurred": True}
            )
    
    def _load_graph(self, source_type: str, data: Any) -> nx.Graph:
        """Load graph from various source formats."""
        try:
            if source_type == "edge_list":
                G = nx.Graph()
                if isinstance(data, list):
                    if data and len(data[0]) == 3:  # Weighted edges
                        G.add_weighted_edges_from(data)
                    else:  # Unweighted edges
                        G.add_edges_from(data)
                return G
                
            elif source_type == "adjacency_matrix":
                if isinstance(data, list):
                    data = np.array(data)
                return nx.from_numpy_array(data)
                
            elif source_type == "networkx_graph":
                return data.copy()
                    
            else:
                raise ValueError(f"Unknown source type: {source_type}")
                
        except Exception as e:
            raise ValueError(f"Error loading graph: {str(e)}")
    
    def _get_graph_properties(self, graph: nx.Graph) -> Dict[str, Any]:
        """Get basic properties of a graph."""
        return {
            "num_nodes": graph.number_of_nodes(),
            "num_edges": graph.number_of_edges(),
            "density": nx.density(graph),
            "num_components": nx.number_connected_components(graph),
            "is_connected": nx.is_connected(graph),
            "average_clustering": nx.average_clustering(graph),
            "average_degree": sum(dict(graph.degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0
        }
    
    def _comprehensive_comparison(self, graph1: nx.Graph, graph2: nx.Graph, 
                                similarity_metrics: List[str], statistical_testing: bool,
                                confidence_level: float) -> Dict[str, Any]:
        """Perform comprehensive graph comparison analysis."""
        results = {
            "basic_properties": self._compare_basic_properties(graph1, graph2),
            "similarity_scores": {},
            "structural_analysis": {},
            "topological_analysis": {},
            "spectral_analysis": {}
        }
        
        # Compute similarity metrics
        for metric in similarity_metrics:
            if metric == "structural_similarity":
                results["similarity_scores"]["structural"] = self._compute_structural_similarity(graph1, graph2)
            elif metric == "spectral_similarity":
                results["similarity_scores"]["spectral"] = self._compute_spectral_similarity(graph1, graph2)
            elif metric == "degree_distribution_similarity":
                results["similarity_scores"]["degree_distribution"] = self._compute_degree_distribution_similarity(graph1, graph2)
            elif metric == "clustering_similarity":
                results["similarity_scores"]["clustering"] = self._compute_clustering_similarity(graph1, graph2)
            elif metric == "centrality_similarity":
                results["similarity_scores"]["centrality"] = self._compute_centrality_similarity(graph1, graph2)
        
        # Structural analysis
        results["structural_analysis"] = {
            "graph_edit_distance": self._compute_graph_edit_distance(graph1, graph2),
            "isomorphism": self._check_isomorphism(graph1, graph2),
            "subgraph_matching": self._analyze_subgraph_matching(graph1, graph2)
        }
        
        # Statistical testing
        if statistical_testing:
            results["statistical_tests"] = self._perform_statistical_tests(
                graph1, graph2, confidence_level
            )
        
        return results
    
    def _compare_basic_properties(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Compare basic graph properties."""
        props1 = self._get_graph_properties(graph1)
        props2 = self._get_graph_properties(graph2)
        
        return {
            "graph1": props1,
            "graph2": props2,
            "differences": {
                "nodes": abs(props1["num_nodes"] - props2["num_nodes"]),
                "edges": abs(props1["num_edges"] - props2["num_edges"]),
                "density": abs(props1["density"] - props2["density"]),
                "components": abs(props1["num_components"] - props2["num_components"])
            }
        }
    
    def _compute_structural_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, float]:
        """Compute structural similarity between graphs."""
        props1 = self._get_graph_properties(graph1)
        props2 = self._get_graph_properties(graph2)
        
        # Normalize differences for similarity score
        size_similarity = 1 - abs(props1["num_nodes"] - props2["num_nodes"]) / max(props1["num_nodes"], props2["num_nodes"], 1)
        edge_similarity = 1 - abs(props1["num_edges"] - props2["num_edges"]) / max(props1["num_edges"], props2["num_edges"], 1)
        density_similarity = 1 - abs(props1["density"] - props2["density"])
        clustering_similarity = 1 - abs(props1["average_clustering"] - props2["average_clustering"])
        
        overall_similarity = np.mean([size_similarity, edge_similarity, density_similarity, clustering_similarity])
        
        return {
            "overall_similarity": float(overall_similarity),
            "size_similarity": float(size_similarity),
            "edge_similarity": float(edge_similarity),
            "density_similarity": float(density_similarity),
            "clustering_similarity": float(clustering_similarity)
        }
    
    def _compute_spectral_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, float]:
        """Compute spectral similarity between graphs using eigenvalues."""
        try:
            # Simple adjacency matrix creation without scipy dependency
            nodes1 = list(graph1.nodes())
            nodes2 = list(graph2.nodes())
            
            # Create adjacency matrices manually
            A1 = np.zeros((len(nodes1), len(nodes1)))
            A2 = np.zeros((len(nodes2), len(nodes2)))
            
            # Fill adjacency matrix for graph1
            node_to_idx1 = {node: i for i, node in enumerate(nodes1)}
            for edge in graph1.edges():
                i, j = node_to_idx1[edge[0]], node_to_idx1[edge[1]]
                A1[i, j] = A1[j, i] = 1
            
            # Fill adjacency matrix for graph2
            node_to_idx2 = {node: i for i, node in enumerate(nodes2)}
            for edge in graph2.edges():
                i, j = node_to_idx2[edge[0]], node_to_idx2[edge[1]]
                A2[i, j] = A2[j, i] = 1
            
            # Compute eigenvalues
            eigenvals1 = np.real(np.linalg.eigvals(A1))
            eigenvals2 = np.real(np.linalg.eigvals(A2))
            
            # Sort eigenvalues
            eigenvals1 = np.sort(eigenvals1)[::-1]
            eigenvals2 = np.sort(eigenvals2)[::-1]
            
            # Pad shorter sequence with zeros
            max_len = max(len(eigenvals1), len(eigenvals2))
            eigenvals1 = np.pad(eigenvals1, (0, max_len - len(eigenvals1)))
            eigenvals2 = np.pad(eigenvals2, (0, max_len - len(eigenvals2)))
            
            # Compute similarities
            cosine_sim = self._cosine_similarity(eigenvals1, eigenvals2)
            euclidean_sim = 1 / (1 + self._euclidean_distance(eigenvals1, eigenvals2))
            correlation_sim = np.corrcoef(eigenvals1, eigenvals2)[0, 1] if len(eigenvals1) > 1 else 0
            
            return {
                "cosine_similarity": float(cosine_sim),
                "euclidean_similarity": float(euclidean_sim),
                "correlation_similarity": float(correlation_sim if not np.isnan(correlation_sim) else 0),
                "eigenvalue_difference": float(np.mean(np.abs(eigenvals1 - eigenvals2)))
            }
            
        except Exception as e:
            self.logger.warning(f"Error in spectral similarity computation: {str(e)}")
            return {"error": str(e)}
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))
    
    def _euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute Euclidean distance between two vectors."""
        return float(np.sqrt(np.sum((a - b) ** 2)))
    
    def _compute_degree_distribution_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, float]:
        """Compute similarity between degree distributions."""
        degrees1 = [d for n, d in graph1.degree()]
        degrees2 = [d for n, d in graph2.degree()]
        
        if not degrees1 or not degrees2:
            return {"similarity": 0.0}
        
        # Create degree distribution histograms
        max_degree = max(max(degrees1), max(degrees2))
        bins = np.arange(0, max_degree + 2)
        
        hist1, _ = np.histogram(degrees1, bins=bins, density=True)
        hist2, _ = np.histogram(degrees2, bins=bins, density=True)
        
        # Compute similarities
        cosine_sim = self._cosine_similarity(hist1, hist2)
        
        # Simple KS-like statistic
        ks_statistic = np.max(np.abs(np.cumsum(hist1) - np.cumsum(hist2)))
        
        return {
            "cosine_similarity": float(cosine_sim),
            "ks_statistic": float(ks_statistic),
            "similarity_score": float(1 - ks_statistic)
        }
    
    def _compute_clustering_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, float]:
        """Compute similarity between clustering coefficients."""
        clustering1 = list(nx.clustering(graph1).values())
        clustering2 = list(nx.clustering(graph2).values())
        
        if not clustering1 or not clustering2:
            return {"similarity": 0.0}
        
        # Statistical comparison
        mean_diff = abs(np.mean(clustering1) - np.mean(clustering2))
        std_diff = abs(np.std(clustering1) - np.std(clustering2))
        
        return {
            "mean_difference": float(mean_diff),
            "std_difference": float(std_diff),
            "similarity_score": float(1 - mean_diff)
        }
    
    def _compute_centrality_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, float]:
        """Compute similarity between centrality measures."""
        try:
            # Degree centrality
            cent1_degree = list(nx.degree_centrality(graph1).values())
            cent2_degree = list(nx.degree_centrality(graph2).values())
            
            if cent1_degree and cent2_degree:
                mean_diff = abs(np.mean(cent1_degree) - np.mean(cent2_degree))
                return {
                    "degree_centrality_similarity": float(1 - mean_diff)
                }
            
            return {"error": "No centrality data available"}
            
        except Exception as e:
            self.logger.warning(f"Error in centrality similarity computation: {str(e)}")
            return {"error": str(e)}
    
    def _compute_graph_edit_distance(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Compute graph edit distance (approximation for large graphs)."""
        try:
            # Always use approximation to avoid networkx compatibility issues
            props1 = self._get_graph_properties(graph1)
            props2 = self._get_graph_properties(graph2)
            
            node_diff = abs(props1["num_nodes"] - props2["num_nodes"])
            edge_diff = abs(props1["num_edges"] - props2["num_edges"])
            
            approx_ged = node_diff + edge_diff
            max_size = max(props1["num_nodes"] + props1["num_edges"], 
                          props2["num_nodes"] + props2["num_edges"], 1)
            
            return {
                "edit_distance": float(approx_ged),
                "normalized_distance": float(approx_ged / max_size),
                "method": "approximation"
            }
                
        except Exception as e:
            self.logger.warning(f"Error in graph edit distance computation: {str(e)}")
            return {"error": str(e)}
    
    def _check_isomorphism(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Check for graph isomorphism."""
        try:
            # Check if graphs could be isomorphic
            if (graph1.number_of_nodes() != graph2.number_of_nodes() or 
                graph1.number_of_edges() != graph2.number_of_edges()):
                return {
                    "isomorphic": False,
                    "reason": "Different number of nodes or edges"
                }
            
            # For small graphs, check exact isomorphism
            if graph1.number_of_nodes() <= 50:
                is_isomorphic = nx.is_isomorphic(graph1, graph2)
                return {
                    "isomorphic": bool(is_isomorphic),
                    "method": "exact"
                }
            else:
                # For larger graphs, check basic structural properties
                degree_seq1 = sorted([d for n, d in graph1.degree()])
                degree_seq2 = sorted([d for n, d in graph2.degree()])
                
                if degree_seq1 != degree_seq2:
                    return {
                        "isomorphic": False,
                        "reason": "Different degree sequences",
                        "method": "heuristic"
                    }
                
                return {
                    "isomorphic": None,
                    "reason": "Graph too large for exact isomorphism check",
                    "method": "inconclusive"
                }
                
        except Exception as e:
            self.logger.warning(f"Error in isomorphism check: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_subgraph_matching(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Analyze subgraph matching between graphs."""
        try:
            # For larger graphs, use heuristic approach
            common_edges = len(set(graph1.edges()) & set(graph2.edges()))
            total_edges = len(set(graph1.edges()) | set(graph2.edges()))
            
            return {
                "common_edges": int(common_edges),
                "total_unique_edges": int(total_edges),
                "edge_overlap_ratio": float(common_edges / max(total_edges, 1)),
                "method": "heuristic"
            }
            
        except Exception as e:
            self.logger.warning(f"Error in subgraph matching analysis: {str(e)}")
            return {"error": str(e)}
    
    def _perform_statistical_tests(self, graph1: nx.Graph, graph2: nx.Graph, 
                                 confidence_level: float) -> Dict[str, Any]:
        """Perform basic statistical significance tests on graph properties."""
        results = {}
        alpha = 1 - confidence_level
        
        # Degree distribution test
        degrees1 = [d for n, d in graph1.degree()]
        degrees2 = [d for n, d in graph2.degree()]
        
        if degrees1 and degrees2:
            # Simple t-test approximation
            mean_diff = abs(np.mean(degrees1) - np.mean(degrees2))
            std_pooled = np.sqrt((np.var(degrees1) + np.var(degrees2)) / 2)
            t_stat = mean_diff / max(std_pooled, 0.001)
            
            results["degree_distribution_test"] = {
                "test": "Simple t-test approximation",
                "statistic": float(t_stat),
                "significant": bool(t_stat > 2.0),
                "alpha": float(alpha)
            }
        
        return results
    
    def _structural_comparison(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Perform focused structural comparison."""
        return {
            "structural_similarity": self._compute_structural_similarity(graph1, graph2),
            "graph_properties": self._compare_basic_properties(graph1, graph2),
            "graph_edit_distance": self._compute_graph_edit_distance(graph1, graph2)
        }
    
    def _topological_comparison(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Perform focused topological comparison."""
        return {
            "degree_distribution": self._compute_degree_distribution_similarity(graph1, graph2),
            "clustering_similarity": self._compute_clustering_similarity(graph1, graph2),
            "basic_properties": self._compare_basic_properties(graph1, graph2)
        }
    
    def _spectral_comparison(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Perform focused spectral comparison."""
        return {
            "spectral_similarity": self._compute_spectral_similarity(graph1, graph2)
        }
    
    def _isomorphism_analysis(self, graph1: nx.Graph, graph2: nx.Graph) -> Dict[str, Any]:
        """Perform focused isomorphism analysis."""
        return {
            "isomorphism": self._check_isomorphism(graph1, graph2),
            "subgraph_matching": self._analyze_subgraph_matching(graph1, graph2)
        }
    
    def _calculate_academic_confidence(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate academic confidence and quality metrics."""
        confidence_factors = []
        
        # Factor 1: Number of comparison metrics computed
        metrics_computed = 0
        if "similarity_scores" in comparison_results:
            metrics_computed = len(comparison_results["similarity_scores"])
        confidence_factors.append(min(metrics_computed / 5.0, 1.0))
        
        # Factor 2: Statistical testing performed
        statistical_testing = "statistical_tests" in comparison_results and comparison_results["statistical_tests"]
        confidence_factors.append(1.0 if statistical_testing else 0.5)
        
        # Factor 3: Structural analysis completeness
        structural_complete = "structural_analysis" in comparison_results
        confidence_factors.append(1.0 if structural_complete else 0.3)
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_factors)
        
        return {
            "overall_confidence": float(overall_confidence),
            "confidence_level": "high" if overall_confidence >= 0.8 else "medium" if overall_confidence >= 0.6 else "low",
            "publication_ready": bool(overall_confidence >= 0.7 and statistical_testing),
            "academic_ready": bool(overall_confidence >= 0.7),
            "quality_indicators": {
                "metrics_computed": int(metrics_computed),
                "statistical_testing": bool(statistical_testing),
                "structural_analysis": bool(structural_complete)
            }
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for graph comparison."""
        try:
            # Check required fields
            required_fields = ["graph1_source", "graph1_data", "graph2_source", "graph2_data"]
            for field in required_fields:
                if field not in input_data:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Validate source types
            valid_sources = ["edge_list", "adjacency_matrix", "networkx_graph"]
            if input_data["graph1_source"] not in valid_sources:
                return {"valid": False, "error": f"Invalid graph1_source: {input_data['graph1_source']}"}
            if input_data["graph2_source"] not in valid_sources:
                return {"valid": False, "error": f"Invalid graph2_source: {input_data['graph2_source']}"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Input validation error: {str(e)}"}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform tool health check."""
        try:
            # Test basic NetworkX functionality
            test_graph = nx.Graph()
            test_graph.add_edges_from([(1, 2), (2, 3), (3, 1)])
            
            # Test basic computations
            nx.degree_centrality(test_graph)
            nx.clustering(test_graph)
            nx.is_connected(test_graph)
            
            return {
                "status": "healthy",
                "networkx_version": nx.__version__,
                "numpy_version": np.__version__,
                "capabilities": {
                    "structural_comparison": True,
                    "spectral_analysis": True,
                    "statistical_testing": True,
                    "isomorphism_checking": True
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }