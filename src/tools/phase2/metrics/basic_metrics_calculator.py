"""Basic Metrics Calculator

Calculates fundamental graph metrics like nodes, edges, density, etc.
"""

import networkx as nx
import numpy as np
from typing import Dict, Any
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class BasicMetricsCalculator:
    """Calculate basic graph metrics"""
    
    def calculate_basic_metrics(self, graph: nx.Graph, weighted: bool, 
                              performance_mode: str) -> Dict[str, Any]:
        """Calculate basic graph statistics"""
        try:
            metrics = {}
            
            # Node and edge counts
            metrics["nodes"] = len(graph.nodes)
            metrics["edges"] = len(graph.edges)
            
            # Graph type
            metrics["directed"] = graph.is_directed()
            metrics["multigraph"] = graph.is_multigraph()
            metrics["weighted"] = weighted
            
            # Density
            if metrics["nodes"] > 1:
                if graph.is_directed():
                    max_edges = metrics["nodes"] * (metrics["nodes"] - 1)
                else:
                    max_edges = metrics["nodes"] * (metrics["nodes"] - 1) / 2
                metrics["density"] = metrics["edges"] / max_edges if max_edges > 0 else 0
            else:
                metrics["density"] = 0
            
            # Degree statistics
            degrees = dict(graph.degree())
            if degrees:
                degree_values = list(degrees.values())
                metrics["degree_stats"] = {
                    "min": min(degree_values),
                    "max": max(degree_values),
                    "mean": np.mean(degree_values),
                    "std": np.std(degree_values),
                    "median": np.median(degree_values)
                }
            else:
                metrics["degree_stats"] = {
                    "min": 0, "max": 0, "mean": 0, "std": 0, "median": 0
                }
            
            # Connectivity
            metrics["connected"] = nx.is_connected(graph) if not graph.is_directed() else nx.is_strongly_connected(graph)
            metrics["components"] = nx.number_connected_components(graph) if not graph.is_directed() else nx.number_strongly_connected_components(graph)
            
            # Weight statistics if weighted
            if weighted:
                weights = [data.get('weight', 1.0) for _, _, data in graph.edges(data=True)]
                if weights:
                    metrics["weight_stats"] = {
                        "min": min(weights),
                        "max": max(weights),
                        "mean": np.mean(weights),
                        "std": np.std(weights),
                        "total": sum(weights)
                    }
                else:
                    metrics["weight_stats"] = {
                        "min": 0, "max": 0, "mean": 0, "std": 0, "total": 0
                    }
            
            # Self-loops and multiple edges
            metrics["self_loops"] = nx.number_of_selfloops(graph)
            if hasattr(graph, 'number_of_edges'):
                # For multigraphs
                simple_edges = len(set(graph.edges()))
                metrics["multiple_edges"] = metrics["edges"] - simple_edges
            else:
                metrics["multiple_edges"] = 0
            
            # Isolated nodes
            metrics["isolated_nodes"] = len(list(nx.isolates(graph)))
            
            # Performance-specific metrics
            if performance_mode in ["comprehensive", "research"]:
                # Assortativity (only for larger graphs due to computation cost)
                if metrics["nodes"] < 10000:
                    try:
                        if weighted:
                            metrics["assortativity"] = nx.degree_assortativity_coefficient(graph, weight='weight')
                        else:
                            metrics["assortativity"] = nx.degree_assortativity_coefficient(graph)
                    except:
                        metrics["assortativity"] = None
                
                # Reciprocity for directed graphs
                if graph.is_directed():
                    metrics["reciprocity"] = nx.reciprocity(graph)
            
            logger.info(f"Calculated basic metrics: {metrics['nodes']} nodes, {metrics['edges']} edges")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating basic metrics: {e}")
            return {"error": str(e)}
    
    def calculate_degree_distribution(self, graph: nx.Graph) -> Dict[str, Any]:
        """Calculate degree distribution statistics"""
        try:
            degrees = dict(graph.degree())
            degree_values = list(degrees.values())
            
            if not degree_values:
                return {"distribution": {}, "statistics": {}}
            
            # Degree distribution
            degree_counts = {}
            for degree in degree_values:
                degree_counts[degree] = degree_counts.get(degree, 0) + 1
            
            # Distribution statistics
            total_nodes = len(degree_values)
            distribution = {degree: count / total_nodes 
                          for degree, count in degree_counts.items()}
            
            # Additional statistics
            statistics = {
                "unique_degrees": len(degree_counts),
                "max_degree_nodes": sum(1 for d in degree_values if d == max(degree_values)),
                "min_degree_nodes": sum(1 for d in degree_values if d == min(degree_values)),
                "power_law_alpha": self._estimate_power_law_alpha(degree_values),
                "degree_entropy": self._calculate_degree_entropy(distribution)
            }
            
            return {
                "distribution": distribution,
                "counts": degree_counts,
                "statistics": statistics
            }
            
        except Exception as e:
            logger.error(f"Error calculating degree distribution: {e}")
            return {"error": str(e)}
    
    def _estimate_power_law_alpha(self, degree_values):
        """Estimate power law exponent using method of moments"""
        try:
            # Filter out zeros and ones for power law fitting
            filtered_degrees = [d for d in degree_values if d > 1]
            if len(filtered_degrees) < 10:
                return None
            
            # Simple estimation using log-log regression
            log_degrees = np.log(filtered_degrees)
            log_probs = np.log([degree_values.count(d) / len(degree_values) 
                              for d in filtered_degrees])
            
            # Linear regression in log-log space
            coeffs = np.polyfit(log_degrees, log_probs, 1)
            alpha = -coeffs[0]  # Negative slope gives power law exponent
            
            return alpha if alpha > 0 else None
            
        except Exception as e:
            logger.error(f"Error estimating power law alpha: {e}")
            return None
    
    def _calculate_degree_entropy(self, distribution):
        """Calculate entropy of degree distribution"""
        try:
            entropy = 0
            for prob in distribution.values():
                if prob > 0:
                    entropy -= prob * np.log2(prob)
            return entropy
        except Exception as e:
            logger.error(f"Error calculating degree entropy: {e}")
            return None