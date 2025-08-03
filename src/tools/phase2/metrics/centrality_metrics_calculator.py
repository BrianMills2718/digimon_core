"""Centrality Metrics Calculator

Calculates various centrality measures for graph nodes.
"""

import networkx as nx
import numpy as np
from typing import Dict, Any
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CentralityMetricsCalculator:
    """Calculate centrality metrics"""
    
    def calculate_centrality_metrics(self, graph: nx.Graph, weighted: bool, normalize: bool,
                                   performance_mode: str) -> Dict[str, Any]:
        """Calculate comprehensive centrality metrics"""
        try:
            metrics = {}
            weight_attr = 'weight' if weighted else None
            
            # Degree centrality (always fast)
            degree_centrality = nx.degree_centrality(graph)
            metrics["degree"] = {
                "values": degree_centrality,
                "stats": self._calculate_centrality_stats(degree_centrality)
            }
            
            # Betweenness centrality (computationally expensive)
            if performance_mode in ["balanced", "comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 5000:  # Full calculation for smaller graphs
                        betweenness = nx.betweenness_centrality(graph, normalized=normalize, weight=weight_attr)
                    else:  # Sample-based approximation for larger graphs
                        k = min(1000, len(graph.nodes) // 10)
                        betweenness = nx.betweenness_centrality(graph, k=k, normalized=normalize, weight=weight_attr)
                    
                    metrics["betweenness"] = {
                        "values": betweenness,
                        "stats": self._calculate_centrality_stats(betweenness)
                    }
                except Exception as e:
                    logger.warning(f"Betweenness centrality calculation failed: {e}")
                    metrics["betweenness"] = {"error": str(e)}
            
            # Closeness centrality
            if performance_mode in ["balanced", "comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 10000:  # Reasonable limit for closeness
                        closeness = nx.closeness_centrality(graph, distance=weight_attr)
                        metrics["closeness"] = {
                            "values": closeness,
                            "stats": self._calculate_centrality_stats(closeness)
                        }
                except Exception as e:
                    logger.warning(f"Closeness centrality calculation failed: {e}")
                    metrics["closeness"] = {"error": str(e)}
            
            # Eigenvector centrality
            if performance_mode in ["comprehensive", "research"]:
                try:
                    eigenvector = nx.eigenvector_centrality(graph, max_iter=1000, weight=weight_attr)
                    metrics["eigenvector"] = {
                        "values": eigenvector,
                        "stats": self._calculate_centrality_stats(eigenvector)
                    }
                except Exception as e:
                    logger.warning(f"Eigenvector centrality calculation failed: {e}")
                    metrics["eigenvector"] = {"error": str(e)}
            
            # PageRank (works well for larger graphs)
            try:
                pagerank = nx.pagerank(graph, alpha=0.85, max_iter=1000, weight=weight_attr)
                metrics["pagerank"] = {
                    "values": pagerank,
                    "stats": self._calculate_centrality_stats(pagerank)
                }
            except Exception as e:
                logger.warning(f"PageRank calculation failed: {e}")
                metrics["pagerank"] = {"error": str(e)}
            
            # Katz centrality (for research mode)
            if performance_mode == "research":
                try:
                    # Use smaller alpha for stability
                    katz = nx.katz_centrality(graph, alpha=0.01, max_iter=1000, weight=weight_attr)
                    metrics["katz"] = {
                        "values": katz,
                        "stats": self._calculate_centrality_stats(katz)
                    }
                except Exception as e:
                    logger.warning(f"Katz centrality calculation failed: {e}")
                    metrics["katz"] = {"error": str(e)}
            
            # Load centrality (edge centrality)
            if performance_mode in ["comprehensive", "research"] and len(graph.edges) < 50000:
                try:
                    load_centrality = nx.load_centrality(graph, normalized=normalize, weight=weight_attr)
                    metrics["load"] = {
                        "values": load_centrality,
                        "stats": self._calculate_centrality_stats(load_centrality)
                    }
                except Exception as e:
                    logger.warning(f"Load centrality calculation failed: {e}")
                    metrics["load"] = {"error": str(e)}
            
            # Harmonic centrality (alternative to closeness for disconnected graphs)
            if performance_mode in ["comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 5000:
                        harmonic = nx.harmonic_centrality(graph, distance=weight_attr)
                        metrics["harmonic"] = {
                            "values": harmonic,
                            "stats": self._calculate_centrality_stats(harmonic)
                        }
                except Exception as e:
                    logger.warning(f"Harmonic centrality calculation failed: {e}")
                    metrics["harmonic"] = {"error": str(e)}
            
            # Current flow centrality (for research mode, small graphs only)
            if performance_mode == "research" and len(graph.nodes) < 1000:
                try:
                    current_flow_betweenness = nx.current_flow_betweenness_centrality(
                        graph, normalized=normalize, weight=weight_attr
                    )
                    metrics["current_flow_betweenness"] = {
                        "values": current_flow_betweenness,
                        "stats": self._calculate_centrality_stats(current_flow_betweenness)
                    }
                except Exception as e:
                    logger.warning(f"Current flow betweenness calculation failed: {e}")
                    metrics["current_flow_betweenness"] = {"error": str(e)}
            
            logger.info(f"Calculated centrality metrics for {len(graph.nodes)} nodes")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating centrality metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_centrality_stats(self, centrality_dict: Dict[str, float]) -> Dict[str, float]:
        """Calculate statistics for centrality measures"""
        try:
            if not centrality_dict:
                return {}
            
            values = list(centrality_dict.values())
            
            stats = {
                "min": min(values),
                "max": max(values),
                "mean": np.mean(values),
                "std": np.std(values),
                "median": np.median(values),
                "sum": sum(values)
            }
            
            # Find top nodes
            sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
            stats["top_nodes"] = [{"node": node, "value": value} 
                                for node, value in sorted_nodes[:10]]
            
            # Centralization index (how much centrality is concentrated)
            n = len(values)
            if n > 1:
                max_possible = (n - 1) * (stats["max"] - stats["mean"])
                actual = sum(stats["max"] - v for v in values)
                stats["centralization"] = actual / max_possible if max_possible > 0 else 0
            else:
                stats["centralization"] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating centrality statistics: {e}")
            return {"error": str(e)}
    
    def calculate_centrality_correlations(self, centrality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate correlations between different centrality measures"""
        try:
            correlations = {}
            
            # Extract centrality measures that have values
            measures = {}
            for measure_name, measure_data in centrality_metrics.items():
                if isinstance(measure_data, dict) and "values" in measure_data:
                    measures[measure_name] = measure_data["values"]
            
            # Calculate pairwise correlations
            measure_names = list(measures.keys())
            for i, measure1 in enumerate(measure_names):
                for j, measure2 in enumerate(measure_names[i+1:], i+1):
                    # Get common nodes
                    common_nodes = set(measures[measure1].keys()) & set(measures[measure2].keys())
                    if len(common_nodes) < 2:
                        continue
                    
                    # Extract values for common nodes
                    values1 = [measures[measure1][node] for node in common_nodes]
                    values2 = [measures[measure2][node] for node in common_nodes]
                    
                    # Calculate Pearson correlation
                    correlation = np.corrcoef(values1, values2)[0, 1]
                    correlations[f"{measure1}_vs_{measure2}"] = {
                        "correlation": correlation,
                        "nodes_compared": len(common_nodes)
                    }
            
            logger.info(f"Calculated {len(correlations)} centrality correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating centrality correlations: {e}")
            return {"error": str(e)}