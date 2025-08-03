"""Centrality Calculation Algorithms

Implements various centrality calculation algorithms.
"""

import networkx as nx
import numpy as np
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from .centrality_data_models import CentralityMetric, CentralityResult, CentralityConfig
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CentralityCalculator:
    """Calculate various centrality metrics for graph analysis"""
    
    def __init__(self):
        self.centrality_configs = CentralityConfig.get_default_configs()
    
    def calculate_centrality_metric(self, graph: nx.Graph, metric: CentralityMetric, 
                                  config: Optional[Dict[str, Any]] = None) -> CentralityResult:
        """Calculate a specific centrality metric"""
        try:
            start_time = time.time()
            
            # Get configuration
            base_config = self.centrality_configs.get(metric, CentralityConfig.get_default_configs()[metric])
            if config:
                # Update config with provided parameters
                for key, value in config.items():
                    if hasattr(base_config, key):
                        setattr(base_config, key, value)
            
            # Prepare graph for this metric
            prepared_graph = self._prepare_graph_for_metric(graph, metric, base_config)
            
            # Calculate centrality scores
            if metric == CentralityMetric.DEGREE:
                scores = self._calculate_degree_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.BETWEENNESS:
                scores = self._calculate_betweenness_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.CLOSENESS:
                scores = self._calculate_closeness_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.EIGENVECTOR:
                scores = self._calculate_eigenvector_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.PAGERANK:
                scores = self._calculate_pagerank_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.KATZ:
                scores = self._calculate_katz_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.HARMONIC:
                scores = self._calculate_harmonic_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.LOAD:
                scores = self._calculate_load_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.INFORMATION:
                scores = self._calculate_information_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.CURRENT_FLOW_BETWEENNESS:
                scores = self._calculate_current_flow_betweenness_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.CURRENT_FLOW_CLOSENESS:
                scores = self._calculate_current_flow_closeness_centrality(prepared_graph, base_config)
            elif metric == CentralityMetric.SUBGRAPH:
                scores = self._calculate_subgraph_centrality(prepared_graph, base_config)
            else:
                raise ValueError(f"Unknown centrality metric: {metric}")
            
            # Normalize scores if requested
            normalized_scores = self._normalize_scores(scores) if base_config.normalized else scores.copy()
            
            calculation_time = time.time() - start_time
            
            return CentralityResult(
                metric=metric.value,
                scores=scores,
                normalized_scores=normalized_scores,
                calculation_time=calculation_time,
                node_count=len(scores),
                metadata={
                    "config": base_config.__dict__,
                    "graph_type": "directed" if prepared_graph.is_directed() else "undirected",
                    "graph_nodes": len(prepared_graph.nodes),
                    "graph_edges": len(prepared_graph.edges),
                    "calculated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Centrality calculation failed for {metric}: {e}")
            return CentralityResult(
                metric=metric.value,
                scores={},
                normalized_scores={},
                calculation_time=0.0,
                node_count=0,
                metadata={"error": str(e)}
            )
    
    def _prepare_graph_for_metric(self, graph: nx.Graph, metric: CentralityMetric, 
                                 config: CentralityConfig) -> nx.Graph:
        """Prepare graph for specific centrality metric"""
        prepared_graph = graph.copy()
        
        # Convert to appropriate graph type based on metric requirements
        if metric in [CentralityMetric.EIGENVECTOR, CentralityMetric.LOAD, 
                     CentralityMetric.INFORMATION, CentralityMetric.CURRENT_FLOW_BETWEENNESS,
                     CentralityMetric.CURRENT_FLOW_CLOSENESS, CentralityMetric.SUBGRAPH]:
            if prepared_graph.is_directed():
                prepared_graph = prepared_graph.to_undirected()
        
        # Remove self-loops for most metrics
        if metric not in [CentralityMetric.PAGERANK, CentralityMetric.KATZ]:
            prepared_graph.remove_edges_from(nx.selfloop_edges(prepared_graph))
        
        return prepared_graph
    
    def _calculate_degree_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate degree centrality"""
        try:
            if graph.is_directed():
                # For directed graphs, can calculate in-degree, out-degree, or total degree
                in_centrality = nx.in_degree_centrality(graph)
                out_centrality = nx.out_degree_centrality(graph)
                # Use total degree (in + out)
                scores = {node: in_centrality[node] + out_centrality[node] for node in graph.nodes()}
            else:
                scores = nx.degree_centrality(graph)
            
            return scores
        except Exception as e:
            logger.error(f"Degree centrality calculation failed: {e}")
            return {}
    
    def _calculate_betweenness_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate betweenness centrality"""
        try:
            # Use approximation for large graphs
            if config.k_nodes and len(graph.nodes) > config.k_nodes:
                scores = nx.betweenness_centrality(
                    graph, 
                    k=config.k_nodes,
                    normalized=config.normalized,
                    weight=config.weight_attribute if config.weighted else None
                )
            else:
                scores = nx.betweenness_centrality(
                    graph,
                    normalized=config.normalized,
                    weight=config.weight_attribute if config.weighted else None
                )
            
            return scores
        except Exception as e:
            logger.error(f"Betweenness centrality calculation failed: {e}")
            return {}
    
    def _calculate_closeness_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate closeness centrality"""
        try:
            scores = nx.closeness_centrality(
                graph,
                distance=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"Closeness centrality calculation failed: {e}")
            return {}
    
    def _calculate_eigenvector_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate eigenvector centrality"""
        try:
            # Eigenvector centrality requires strongly connected graph
            if graph.is_directed():
                if not nx.is_strongly_connected(graph):
                    logger.warning("Graph not strongly connected, using largest strongly connected component")
                    largest_cc = max(nx.strongly_connected_components(graph), key=len)
                    graph = graph.subgraph(largest_cc).copy()
            else:
                if not nx.is_connected(graph):
                    logger.warning("Graph not connected, using largest connected component")
                    largest_cc = max(nx.connected_components(graph), key=len)
                    graph = graph.subgraph(largest_cc).copy()
            
            scores = nx.eigenvector_centrality(
                graph,
                max_iter=config.max_iterations,
                tol=config.tolerance,
                weight=config.weight_attribute if config.weighted else None
            )
            
            # Fill in missing nodes with 0
            all_scores = {node: scores.get(node, 0.0) for node in graph.nodes()}
            return all_scores
            
        except (nx.NetworkXError, np.linalg.LinAlgError) as e:
            logger.warning(f"Eigenvector centrality failed, using degree centrality as fallback: {e}")
            return self._calculate_degree_centrality(graph, config)
        except Exception as e:
            logger.error(f"Eigenvector centrality calculation failed: {e}")
            return {}
    
    def _calculate_pagerank_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate PageRank centrality"""
        try:
            scores = nx.pagerank(
                graph,
                alpha=0.85,  # Damping parameter
                max_iter=config.max_iterations,
                tol=config.tolerance,
                weight=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"PageRank centrality calculation failed: {e}")
            return {}
    
    def _calculate_katz_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate Katz centrality"""
        try:
            # Katz centrality requires alpha < 1/lambda_max
            # Use a conservative alpha value
            alpha = 0.1 / len(graph.nodes) if len(graph.nodes) > 0 else 0.01
            
            scores = nx.katz_centrality(
                graph,
                alpha=alpha,
                beta=1.0,
                max_iter=config.max_iterations,
                tol=config.tolerance,
                weight=config.weight_attribute if config.weighted else None
            )
            return scores
            
        except (nx.NetworkXError, np.linalg.LinAlgError) as e:
            logger.warning(f"Katz centrality failed, using PageRank as fallback: {e}")
            return self._calculate_pagerank_centrality(graph, config)
        except Exception as e:
            logger.error(f"Katz centrality calculation failed: {e}")
            return {}
    
    def _calculate_harmonic_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate harmonic centrality"""
        try:
            scores = nx.harmonic_centrality(
                graph,
                distance=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"Harmonic centrality calculation failed: {e}")
            return {}
    
    def _calculate_load_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate load centrality"""
        try:
            scores = nx.load_centrality(
                graph,
                weight=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"Load centrality calculation failed: {e}")
            return {}
    
    def _calculate_information_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate information centrality"""
        try:
            # Information centrality requires connected graph
            if not nx.is_connected(graph):
                logger.warning("Graph not connected, using largest connected component")
                largest_cc = max(nx.connected_components(graph), key=len)
                graph = graph.subgraph(largest_cc).copy()
            
            scores = nx.information_centrality(
                graph,
                weight=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"Information centrality calculation failed: {e}")
            return {}
    
    def _calculate_current_flow_betweenness_centrality(self, graph: nx.Graph, 
                                                      config: CentralityConfig) -> Dict[str, float]:
        """Calculate current flow betweenness centrality"""
        try:
            # Requires connected graph
            if not nx.is_connected(graph):
                logger.warning("Graph not connected, using largest connected component")
                largest_cc = max(nx.connected_components(graph), key=len)
                graph = graph.subgraph(largest_cc).copy()
            
            scores = nx.current_flow_betweenness_centrality(
                graph,
                weight=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"Current flow betweenness centrality calculation failed: {e}")
            return {}
    
    def _calculate_current_flow_closeness_centrality(self, graph: nx.Graph, 
                                                    config: CentralityConfig) -> Dict[str, float]:
        """Calculate current flow closeness centrality"""
        try:
            # Requires connected graph
            if not nx.is_connected(graph):
                logger.warning("Graph not connected, using largest connected component")
                largest_cc = max(nx.connected_components(graph), key=len)
                graph = graph.subgraph(largest_cc).copy()
            
            scores = nx.current_flow_closeness_centrality(
                graph,
                weight=config.weight_attribute if config.weighted else None
            )
            return scores
        except Exception as e:
            logger.error(f"Current flow closeness centrality calculation failed: {e}")
            return {}
    
    def _calculate_subgraph_centrality(self, graph: nx.Graph, config: CentralityConfig) -> Dict[str, float]:
        """Calculate subgraph centrality"""
        try:
            scores = nx.subgraph_centrality(graph)
            return scores
        except Exception as e:
            logger.error(f"Subgraph centrality calculation failed: {e}")
            return {}
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize centrality scores to [0, 1] range"""
        try:
            if not scores:
                return {}
            
            values = list(scores.values())
            min_val = min(values)
            max_val = max(values)
            
            if max_val == min_val:
                # All values are the same
                return {node: 0.5 for node in scores}
            
            normalized = {
                node: (score - min_val) / (max_val - min_val)
                for node, score in scores.items()
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Score normalization failed: {e}")
            return scores