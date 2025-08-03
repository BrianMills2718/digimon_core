"""Shortest Path Analyzer

Implements various shortest path algorithms for graph analysis.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .path_data_models import PathAlgorithm, PathResult
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ShortestPathAnalyzer:
    """Analyze shortest paths using various algorithms"""
    
    def analyze_shortest_paths(self, graph: nx.Graph, input_data: Dict[str, Any], 
                             algorithms: List[str]) -> Dict[str, Any]:
        """Analyze shortest paths using specified algorithms"""
        try:
            sources = input_data.get('sources', [])
            targets = input_data.get('targets', [])
            weight = input_data.get('weight_attribute') if input_data.get('weighted') else None
            
            # If no sources/targets specified, use sample nodes
            if not sources:
                sources = list(graph.nodes())[:min(10, len(graph.nodes()))]
            if not targets:
                targets = list(graph.nodes())[:min(10, len(graph.nodes()))]
            
            results = {}
            
            for algorithm in algorithms:
                try:
                    if algorithm == "dijkstra":
                        results[algorithm] = self._compute_dijkstra_paths(graph, sources, targets, weight)
                    elif algorithm == "bellman_ford":
                        results[algorithm] = self._compute_bellman_ford_paths(graph, sources, targets, weight)
                    elif algorithm == "bfs":
                        results[algorithm] = self._compute_bfs_paths(graph, sources, targets)
                    elif algorithm == "shortest_path":
                        results[algorithm] = self._compute_generic_shortest_paths(graph, sources, targets, weight)
                    else:
                        logger.warning(f"Unknown algorithm: {algorithm}")
                except Exception as e:
                    logger.error(f"Algorithm {algorithm} failed: {e}")
                    results[algorithm] = {"error": str(e)}
            
            return results
            
        except Exception as e:
            logger.error(f"Error in shortest path analysis: {e}")
            return {"error": str(e)}
    
    def _compute_dijkstra_paths(self, graph: nx.Graph, sources: List[str], 
                               targets: List[str], weight: Optional[str]) -> List[Dict[str, Any]]:
        """Compute shortest paths using Dijkstra's algorithm"""
        try:
            results = []
            
            for source in sources:
                if source not in graph.nodes:
                    continue
                
                try:
                    # Compute single-source shortest paths
                    if weight:
                        lengths, paths = nx.single_source_dijkstra(graph, source, weight=weight)
                    else:
                        lengths, paths = nx.single_source_dijkstra(graph, source)
                    
                    # Extract paths to specified targets
                    for target in targets:
                        if target in paths:
                            path_result = PathResult(
                                source=source,
                                target=target,
                                path=paths[target],
                                length=len(paths[target]) - 1,
                                weight=lengths[target] if weight else len(paths[target]) - 1,
                                algorithm="dijkstra",
                                metadata={
                                    "weight_attribute": weight,
                                    "path_exists": True,
                                    "computed_at": datetime.now().isoformat()
                                }
                            )
                            results.append(path_result.to_dict())
                        else:
                            # No path exists
                            path_result = PathResult(
                                source=source,
                                target=target,
                                path=[],
                                length=float('inf'),
                                weight=float('inf'),
                                algorithm="dijkstra",
                                metadata={
                                    "weight_attribute": weight,
                                    "path_exists": False,
                                    "computed_at": datetime.now().isoformat()
                                }
                            )
                            results.append(path_result.to_dict())
                
                except nx.NetworkXNoPath:
                    # Handle case where no path exists from source
                    for target in targets:
                        path_result = PathResult(
                            source=source,
                            target=target,
                            path=[],
                            length=float('inf'),
                            weight=float('inf'),
                            algorithm="dijkstra",
                            metadata={
                                "weight_attribute": weight,
                                "path_exists": False,
                                "no_path_reason": "NetworkXNoPath",
                                "computed_at": datetime.now().isoformat()
                            }
                        )
                        results.append(path_result.to_dict())
            
            return results
            
        except Exception as e:
            logger.error(f"Dijkstra computation failed: {e}")
            return [{"error": str(e)}]
    
    def _compute_bellman_ford_paths(self, graph: nx.Graph, sources: List[str], 
                                   targets: List[str], weight: Optional[str]) -> List[Dict[str, Any]]:
        """Compute shortest paths using Bellman-Ford algorithm"""
        try:
            results = []
            
            for source in sources:
                if source not in graph.nodes:
                    continue
                
                try:
                    # Bellman-Ford can handle negative weights
                    if weight:
                        lengths, paths = nx.single_source_bellman_ford(graph, source, weight=weight)
                    else:
                        lengths, paths = nx.single_source_bellman_ford(graph, source)
                    
                    # Extract paths to specified targets
                    for target in targets:
                        if target in paths:
                            path_result = PathResult(
                                source=source,
                                target=target,
                                path=paths[target],
                                length=len(paths[target]) - 1,
                                weight=lengths[target] if weight else len(paths[target]) - 1,
                                algorithm="bellman_ford",
                                metadata={
                                    "weight_attribute": weight,
                                    "path_exists": True,
                                    "handles_negative_weights": True,
                                    "computed_at": datetime.now().isoformat()
                                }
                            )
                            results.append(path_result.to_dict())
                        else:
                            path_result = PathResult(
                                source=source,
                                target=target,
                                path=[],
                                length=float('inf'),
                                weight=float('inf'),
                                algorithm="bellman_ford",
                                metadata={
                                    "weight_attribute": weight,
                                    "path_exists": False,
                                    "computed_at": datetime.now().isoformat()
                                }
                            )
                            results.append(path_result.to_dict())
                
                except nx.NetworkXError as e:
                    # Handle negative cycle detection
                    logger.warning(f"Bellman-Ford detected issue for source {source}: {e}")
                    for target in targets:
                        path_result = PathResult(
                            source=source,
                            target=target,
                            path=[],
                            length=float('inf'),
                            weight=float('inf'),
                            algorithm="bellman_ford",
                            metadata={
                                "weight_attribute": weight,
                                "path_exists": False,
                                "error": str(e),
                                "computed_at": datetime.now().isoformat()
                            }
                        )
                        results.append(path_result.to_dict())
            
            return results
            
        except Exception as e:
            logger.error(f"Bellman-Ford computation failed: {e}")
            return [{"error": str(e)}]
    
    def _compute_bfs_paths(self, graph: nx.Graph, sources: List[str], 
                          targets: List[str]) -> List[Dict[str, Any]]:
        """Compute shortest paths using BFS (unweighted)"""
        try:
            results = []
            
            for source in sources:
                if source not in graph.nodes:
                    continue
                
                try:
                    # BFS for unweighted shortest paths
                    lengths = nx.single_source_shortest_path_length(graph, source)
                    paths = nx.single_source_shortest_path(graph, source)
                    
                    for target in targets:
                        if target in paths:
                            path_result = PathResult(
                                source=source,
                                target=target,
                                path=paths[target],
                                length=lengths[target],
                                weight=lengths[target],  # For BFS, length equals weight
                                algorithm="bfs",
                                metadata={
                                    "weight_attribute": None,
                                    "path_exists": True,
                                    "unweighted": True,
                                    "computed_at": datetime.now().isoformat()
                                }
                            )
                            results.append(path_result.to_dict())
                        else:
                            path_result = PathResult(
                                source=source,
                                target=target,
                                path=[],
                                length=float('inf'),
                                weight=float('inf'),
                                algorithm="bfs",
                                metadata={
                                    "weight_attribute": None,
                                    "path_exists": False,
                                    "computed_at": datetime.now().isoformat()
                                }
                            )
                            results.append(path_result.to_dict())
                
                except Exception as e:
                    logger.warning(f"BFS failed for source {source}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"BFS computation failed: {e}")
            return [{"error": str(e)}]
    
    def _compute_generic_shortest_paths(self, graph: nx.Graph, sources: List[str], 
                                       targets: List[str], weight: Optional[str]) -> List[Dict[str, Any]]:
        """Compute shortest paths using NetworkX generic algorithm"""
        try:
            results = []
            
            for source in sources:
                if source not in graph.nodes:
                    continue
                
                for target in targets:
                    if target not in graph.nodes:
                        continue
                    
                    try:
                        # Use NetworkX's generic shortest path
                        if weight:
                            path = nx.shortest_path(graph, source, target, weight=weight)
                            path_length = nx.shortest_path_length(graph, source, target, weight=weight)
                        else:
                            path = nx.shortest_path(graph, source, target)
                            path_length = nx.shortest_path_length(graph, source, target)
                        
                        path_result = PathResult(
                            source=source,
                            target=target,
                            path=path,
                            length=len(path) - 1,
                            weight=path_length,
                            algorithm="shortest_path",
                            metadata={
                                "weight_attribute": weight,
                                "path_exists": True,
                                "computed_at": datetime.now().isoformat()
                            }
                        )
                        results.append(path_result.to_dict())
                    
                    except nx.NetworkXNoPath:
                        path_result = PathResult(
                            source=source,
                            target=target,
                            path=[],
                            length=float('inf'),
                            weight=float('inf'),
                            algorithm="shortest_path",
                            metadata={
                                "weight_attribute": weight,
                                "path_exists": False,
                                "computed_at": datetime.now().isoformat()
                            }
                        )
                        results.append(path_result.to_dict())
            
            return results
            
        except Exception as e:
            logger.error(f"Generic shortest path computation failed: {e}")
            return [{"error": str(e)}]
    
    def analyze_all_pairs_paths(self, graph: nx.Graph, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all-pairs shortest paths"""
        try:
            weight = input_data.get('weight_attribute') if input_data.get('weighted') else None
            limit_nodes = input_data.get('max_nodes', 100)
            
            # Limit analysis for performance
            if len(graph.nodes) > limit_nodes:
                logger.warning(f"Graph too large ({len(graph.nodes)} nodes), sampling {limit_nodes} nodes")
                nodes = list(graph.nodes())[:limit_nodes]
                subgraph = graph.subgraph(nodes)
            else:
                subgraph = graph
            
            if weight:
                # Weighted all-pairs shortest paths
                try:
                    all_pairs_lengths = dict(nx.all_pairs_dijkstra_path_length(subgraph, weight=weight))
                    all_pairs_paths = dict(nx.all_pairs_dijkstra_path(subgraph, weight=weight))
                except:
                    # Fallback to Floyd-Warshall for negative weights
                    all_pairs_lengths = dict(nx.floyd_warshall(subgraph, weight=weight))
                    all_pairs_paths = dict(nx.all_pairs_shortest_path(subgraph, weight=weight))
            else:
                # Unweighted all-pairs shortest paths
                all_pairs_lengths = dict(nx.all_pairs_shortest_path_length(subgraph))
                all_pairs_paths = dict(nx.all_pairs_shortest_path(subgraph))
            
            # Calculate statistics
            all_lengths = []
            reachable_pairs = 0
            total_pairs = 0
            
            for source in all_pairs_lengths:
                for target, length in all_pairs_lengths[source].items():
                    if source != target:  # Exclude self-loops
                        total_pairs += 1
                        if length != float('inf'):
                            all_lengths.append(length)
                            reachable_pairs += 1
            
            # Compute path statistics
            if all_lengths:
                avg_length = np.mean(all_lengths)
                median_length = np.median(all_lengths)
                std_length = np.std(all_lengths)
                min_length = min(all_lengths)
                max_length = max(all_lengths)
            else:
                avg_length = median_length = std_length = min_length = max_length = 0
            
            return {
                "all_pairs_lengths": all_pairs_lengths,
                "all_pairs_paths": all_pairs_paths,
                "statistics": {
                    "total_node_pairs": total_pairs,
                    "reachable_pairs": reachable_pairs,
                    "unreachable_pairs": total_pairs - reachable_pairs,
                    "connectivity_ratio": reachable_pairs / total_pairs if total_pairs > 0 else 0,
                    "average_path_length": avg_length,
                    "median_path_length": median_length,
                    "std_path_length": std_length,
                    "min_path_length": min_length,
                    "max_path_length": max_length,
                    "diameter": max_length if all_lengths else 0,
                    "nodes_analyzed": len(subgraph.nodes),
                    "weight_attribute": weight
                },
                "metadata": {
                    "algorithm": "all_pairs_shortest_path",
                    "weighted": weight is not None,
                    "graph_size_limited": len(graph.nodes) > limit_nodes,
                    "computed_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"All-pairs path analysis failed: {e}")
            return {"error": str(e)}