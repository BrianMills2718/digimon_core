"""Reachability Analyzer

Analyzes reachability and connectivity patterns in graphs.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ReachabilityAnalyzer:
    """Analyze reachability and connectivity patterns"""
    
    def analyze_reachability(self, graph: nx.Graph, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze reachability patterns in the graph"""
        try:
            sources = input_data.get('reachability_sources', [])
            max_distance = input_data.get('max_reachability_distance', None)
            
            # If no sources specified, use sample nodes
            if not sources:
                sources = list(graph.nodes())[:min(10, len(graph.nodes()))]
            
            reachability_results = {}
            
            for source in sources:
                if source not in graph.nodes:
                    continue
                
                try:
                    reachability_data = self._compute_reachability_from_source(
                        graph, source, max_distance
                    )
                    reachability_results[source] = reachability_data
                except Exception as e:
                    logger.error(f"Reachability analysis failed for source {source}: {e}")
                    reachability_results[source] = {"error": str(e)}
            
            # Global reachability statistics
            global_stats = self._calculate_global_reachability_stats(graph, reachability_results)
            
            return {
                "source_reachability": reachability_results,
                "global_statistics": global_stats,
                "metadata": {
                    "sources_analyzed": len(sources),
                    "max_distance": max_distance,
                    "graph_type": "directed" if graph.is_directed() else "undirected",
                    "computed_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in reachability analysis: {e}")
            return {"error": str(e)}
    
    def _compute_reachability_from_source(self, graph: nx.Graph, source: str, 
                                         max_distance: Optional[int]) -> Dict[str, Any]:
        """Compute reachability from a single source"""
        try:
            # Get reachable nodes and distances
            if max_distance is not None:
                # Limited distance reachability
                reachable = {}
                current_level = {source}
                reachable[source] = 0
                
                for distance in range(1, max_distance + 1):
                    next_level = set()
                    for node in current_level:
                        for neighbor in graph.neighbors(node):
                            if neighbor not in reachable:
                                reachable[neighbor] = distance
                                next_level.add(neighbor)
                    current_level = next_level
                    if not current_level:
                        break
            else:
                # Unlimited distance reachability
                reachable = nx.single_source_shortest_path_length(graph, source)
            
            # Analyze reachability patterns
            distances = list(reachable.values())
            reachable_count = len(reachable) - 1  # Exclude source itself
            total_nodes = len(graph.nodes) - 1
            
            # Group nodes by distance
            nodes_by_distance = {}
            for node, distance in reachable.items():
                if distance not in nodes_by_distance:
                    nodes_by_distance[distance] = []
                nodes_by_distance[distance].append(node)
            
            # Reachability statistics
            stats = {
                "reachable_nodes": reachable_count,
                "total_possible_nodes": total_nodes,
                "reachability_ratio": reachable_count / total_nodes if total_nodes > 0 else 0,
                "max_distance": max(distances) if distances else 0,
                "average_distance": np.mean(distances[1:]) if len(distances) > 1 else 0,  # Exclude source (distance 0)
                "nodes_by_distance": {str(d): len(nodes) for d, nodes in nodes_by_distance.items()},
                "distance_distribution": self._calculate_distance_distribution(distances[1:])
            }
            
            return {
                "reachable_nodes": reachable,
                "statistics": stats,
                "unreachable_nodes": [node for node in graph.nodes if node not in reachable]
            }
            
        except Exception as e:
            logger.error(f"Reachability computation failed for source {source}: {e}")
            return {"error": str(e)}
    
    def _calculate_distance_distribution(self, distances: List[int]) -> Dict[str, Any]:
        """Calculate distribution statistics for distances"""
        try:
            if not distances:
                return {}
            
            unique_distances = list(set(distances))
            distance_counts = {d: distances.count(d) for d in unique_distances}
            total_count = len(distances)
            
            return {
                "unique_distances": len(unique_distances),
                "distance_counts": distance_counts,
                "distance_probabilities": {d: count / total_count 
                                         for d, count in distance_counts.items()},
                "min_distance": min(distances),
                "max_distance": max(distances),
                "mean_distance": np.mean(distances),
                "std_distance": np.std(distances) if len(distances) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Distance distribution calculation failed: {e}")
            return {}
    
    def _calculate_global_reachability_stats(self, graph: nx.Graph, 
                                           reachability_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate global reachability statistics"""
        try:
            total_nodes = len(graph.nodes)
            
            # Aggregate reachability data
            all_reachability_ratios = []
            all_max_distances = []
            all_avg_distances = []
            
            for source, data in reachability_results.items():
                if "error" not in data and "statistics" in data:
                    stats = data["statistics"]
                    all_reachability_ratios.append(stats.get("reachability_ratio", 0))
                    all_max_distances.append(stats.get("max_distance", 0))
                    all_avg_distances.append(stats.get("average_distance", 0))
            
            # Calculate global connectivity measures
            if graph.is_directed():
                strongly_connected = nx.is_strongly_connected(graph)
                weakly_connected = nx.is_weakly_connected(graph)
                components = list(nx.strongly_connected_components(graph))
                largest_component_size = max(len(comp) for comp in components) if components else 0
            else:
                connected = nx.is_connected(graph)
                components = list(nx.connected_components(graph))
                largest_component_size = max(len(comp) for comp in components) if components else 0
                strongly_connected = connected
                weakly_connected = connected
            
            # Global statistics
            global_stats = {
                "average_reachability_ratio": np.mean(all_reachability_ratios) if all_reachability_ratios else 0,
                "std_reachability_ratio": np.std(all_reachability_ratios) if all_reachability_ratios else 0,
                "min_reachability_ratio": min(all_reachability_ratios) if all_reachability_ratios else 0,
                "max_reachability_ratio": max(all_reachability_ratios) if all_reachability_ratios else 0,
                "average_max_distance": np.mean(all_max_distances) if all_max_distances else 0,
                "global_max_distance": max(all_max_distances) if all_max_distances else 0,
                "average_distance_overall": np.mean(all_avg_distances) if all_avg_distances else 0,
                "connectivity": {
                    "strongly_connected": strongly_connected,
                    "weakly_connected": weakly_connected if graph.is_directed() else connected,
                    "number_of_components": len(components),
                    "largest_component_size": largest_component_size,
                    "largest_component_ratio": largest_component_size / total_nodes if total_nodes > 0 else 0
                }
            }
            
            return global_stats
            
        except Exception as e:
            logger.error(f"Global reachability statistics calculation failed: {e}")
            return {"error": str(e)}
    
    def analyze_node_importance_by_reachability(self, graph: nx.Graph, 
                                               input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze node importance based on reachability patterns"""
        try:
            # Calculate reachability-based importance metrics
            importance_metrics = {}
            
            # Out-reachability: how many nodes can each node reach
            for node in graph.nodes():
                try:
                    reachable = nx.single_source_shortest_path_length(graph, node)
                    out_reach = len(reachable) - 1  # Exclude the node itself
                    importance_metrics[node] = {"out_reachability": out_reach}
                except Exception as e:
                    logger.warning(f"Out-reachability failed for node {node}: {e}")
                    importance_metrics[node] = {"out_reachability": 0}
            
            # In-reachability: how many nodes can reach each node
            if graph.is_directed():
                reverse_graph = graph.reverse()
                for node in graph.nodes():
                    try:
                        reachable = nx.single_source_shortest_path_length(reverse_graph, node)
                        in_reach = len(reachable) - 1
                        importance_metrics[node]["in_reachability"] = in_reach
                    except Exception as e:
                        logger.warning(f"In-reachability failed for node {node}: {e}")
                        importance_metrics[node]["in_reachability"] = 0
            else:
                # For undirected graphs, in and out reachability are the same
                for node in importance_metrics:
                    importance_metrics[node]["in_reachability"] = importance_metrics[node]["out_reachability"]
            
            # Calculate combined importance score
            total_nodes = len(graph.nodes) - 1  # Exclude self
            for node in importance_metrics:
                out_reach = importance_metrics[node]["out_reachability"]
                in_reach = importance_metrics[node]["in_reachability"]
                
                # Normalized importance scores
                out_importance = out_reach / total_nodes if total_nodes > 0 else 0
                in_importance = in_reach / total_nodes if total_nodes > 0 else 0
                combined_importance = (out_importance + in_importance) / 2
                
                importance_metrics[node].update({
                    "out_importance_normalized": out_importance,
                    "in_importance_normalized": in_importance,
                    "combined_importance": combined_importance
                })
            
            # Rank nodes by importance
            nodes_by_out_reach = sorted(importance_metrics.items(), 
                                      key=lambda x: x[1]["out_reachability"], reverse=True)
            nodes_by_in_reach = sorted(importance_metrics.items(), 
                                     key=lambda x: x[1]["in_reachability"], reverse=True)
            nodes_by_combined = sorted(importance_metrics.items(), 
                                     key=lambda x: x[1]["combined_importance"], reverse=True)
            
            return {
                "node_importance_metrics": importance_metrics,
                "rankings": {
                    "by_out_reachability": [(node, metrics["out_reachability"]) 
                                          for node, metrics in nodes_by_out_reach[:20]],
                    "by_in_reachability": [(node, metrics["in_reachability"]) 
                                         for node, metrics in nodes_by_in_reach[:20]],
                    "by_combined_importance": [(node, metrics["combined_importance"]) 
                                             for node, metrics in nodes_by_combined[:20]]
                },
                "statistics": {
                    "total_nodes_analyzed": len(importance_metrics),
                    "max_out_reachability": max(m["out_reachability"] for m in importance_metrics.values()),
                    "max_in_reachability": max(m["in_reachability"] for m in importance_metrics.values()),
                    "average_out_reachability": np.mean([m["out_reachability"] for m in importance_metrics.values()]),
                    "average_in_reachability": np.mean([m["in_reachability"] for m in importance_metrics.values()])
                }
            }
            
        except Exception as e:
            logger.error(f"Node importance analysis failed: {e}")
            return {"error": str(e)}