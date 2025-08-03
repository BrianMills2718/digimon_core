"""Connectivity Metrics Calculator

Calculates connectivity and path-related metrics for graphs.
"""

import networkx as nx
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ConnectivityMetricsCalculator:
    """Calculate connectivity metrics"""
    
    def calculate_connectivity_metrics(self, graph: nx.Graph, performance_mode: str) -> Dict[str, Any]:
        """Calculate comprehensive connectivity metrics"""
        try:
            metrics = {}
            
            # Basic connectivity
            if graph.is_directed():
                metrics["strongly_connected"] = nx.is_strongly_connected(graph)
                metrics["weakly_connected"] = nx.is_weakly_connected(graph)
                metrics["strongly_connected_components"] = nx.number_strongly_connected_components(graph)
                metrics["weakly_connected_components"] = nx.number_weakly_connected_components(graph)
                
                # Largest strongly connected component
                if metrics["strongly_connected_components"] > 1:
                    largest_scc = max(nx.strongly_connected_components(graph), key=len)
                    metrics["largest_scc_size"] = len(largest_scc)
                    metrics["largest_scc_fraction"] = len(largest_scc) / len(graph.nodes)
                else:
                    metrics["largest_scc_size"] = len(graph.nodes)
                    metrics["largest_scc_fraction"] = 1.0
            else:
                metrics["connected"] = nx.is_connected(graph)
                metrics["connected_components"] = nx.number_connected_components(graph)
                
                # Largest connected component
                if metrics["connected_components"] > 1:
                    largest_cc = max(nx.connected_components(graph), key=len)
                    metrics["largest_cc_size"] = len(largest_cc)
                    metrics["largest_cc_fraction"] = len(largest_cc) / len(graph.nodes)
                else:
                    metrics["largest_cc_size"] = len(graph.nodes)
                    metrics["largest_cc_fraction"] = 1.0
            
            # Path metrics (computationally expensive for large graphs)
            if performance_mode in ["balanced", "comprehensive", "research"]:
                # Average shortest path length
                if len(graph.nodes) < 5000:
                    try:
                        if graph.is_directed():
                            if nx.is_strongly_connected(graph):
                                metrics["average_shortest_path_length"] = nx.average_shortest_path_length(graph)
                            else:
                                # Calculate for largest strongly connected component
                                largest_scc = max(nx.strongly_connected_components(graph), key=len)
                                scc_subgraph = graph.subgraph(largest_scc)
                                metrics["average_shortest_path_length"] = nx.average_shortest_path_length(scc_subgraph)
                        else:
                            if nx.is_connected(graph):
                                metrics["average_shortest_path_length"] = nx.average_shortest_path_length(graph)
                            else:
                                # Calculate for largest connected component
                                largest_cc = max(nx.connected_components(graph), key=len)
                                cc_subgraph = graph.subgraph(largest_cc)
                                metrics["average_shortest_path_length"] = nx.average_shortest_path_length(cc_subgraph)
                    except Exception as e:
                        logger.warning(f"Average shortest path calculation failed: {e}")
                        metrics["average_shortest_path_length"] = None
                
                # Diameter (longest shortest path)
                if len(graph.nodes) < 2000:
                    try:
                        if graph.is_directed():
                            if nx.is_strongly_connected(graph):
                                metrics["diameter"] = nx.diameter(graph)
                            else:
                                largest_scc = max(nx.strongly_connected_components(graph), key=len)
                                scc_subgraph = graph.subgraph(largest_scc)
                                metrics["diameter"] = nx.diameter(scc_subgraph)
                        else:
                            if nx.is_connected(graph):
                                metrics["diameter"] = nx.diameter(graph)
                            else:
                                largest_cc = max(nx.connected_components(graph), key=len)
                                cc_subgraph = graph.subgraph(largest_cc)
                                metrics["diameter"] = nx.diameter(cc_subgraph)
                    except Exception as e:
                        logger.warning(f"Diameter calculation failed: {e}")
                        metrics["diameter"] = None
                
                # Radius (minimum eccentricity)
                if len(graph.nodes) < 1000:
                    try:
                        if graph.is_directed():
                            if nx.is_strongly_connected(graph):
                                metrics["radius"] = nx.radius(graph)
                            else:
                                largest_scc = max(nx.strongly_connected_components(graph), key=len)
                                scc_subgraph = graph.subgraph(largest_scc)
                                metrics["radius"] = nx.radius(scc_subgraph)
                        else:
                            if nx.is_connected(graph):
                                metrics["radius"] = nx.radius(graph)
                            else:
                                largest_cc = max(nx.connected_components(graph), key=len)
                                cc_subgraph = graph.subgraph(largest_cc)
                                metrics["radius"] = nx.radius(cc_subgraph)
                    except Exception as e:
                        logger.warning(f"Radius calculation failed: {e}")
                        metrics["radius"] = None
            
            # Node and edge connectivity (expensive computations)
            if performance_mode in ["comprehensive", "research"] and len(graph.nodes) < 1000:
                try:
                    if not graph.is_directed():
                        metrics["node_connectivity"] = nx.node_connectivity(graph)
                        metrics["edge_connectivity"] = nx.edge_connectivity(graph)
                    else:
                        # For directed graphs, use approximation or skip
                        logger.info("Skipping node/edge connectivity for directed graph")
                except Exception as e:
                    logger.warning(f"Connectivity calculation failed: {e}")
                    metrics["node_connectivity"] = None
                    metrics["edge_connectivity"] = None
            
            # Algebraic connectivity (second smallest eigenvalue of Laplacian)
            if performance_mode in ["comprehensive", "research"] and len(graph.nodes) < 5000:
                try:
                    if not graph.is_directed() and nx.is_connected(graph):
                        metrics["algebraic_connectivity"] = nx.algebraic_connectivity(graph)
                    else:
                        metrics["algebraic_connectivity"] = None
                except Exception as e:
                    logger.warning(f"Algebraic connectivity calculation failed: {e}")
                    metrics["algebraic_connectivity"] = None
            
            # Wiener index (sum of all shortest path lengths)
            if performance_mode == "research" and len(graph.nodes) < 500:
                try:
                    if graph.is_directed():
                        if nx.is_strongly_connected(graph):
                            metrics["wiener_index"] = nx.wiener_index(graph)
                    else:
                        if nx.is_connected(graph):
                            metrics["wiener_index"] = nx.wiener_index(graph)
                except Exception as e:
                    logger.warning(f"Wiener index calculation failed: {e}")
                    metrics["wiener_index"] = None
            
            logger.info(f"Calculated connectivity metrics for graph with {len(graph.nodes)} nodes")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating connectivity metrics: {e}")
            return {"error": str(e)}
    
    def calculate_component_analysis(self, graph: nx.Graph) -> Dict[str, Any]:
        """Detailed analysis of graph components"""
        try:
            analysis = {}
            
            if graph.is_directed():
                # Strongly connected components
                sccs = list(nx.strongly_connected_components(graph))
                scc_sizes = [len(scc) for scc in sccs]
                
                analysis["strongly_connected_components"] = {
                    "count": len(sccs),
                    "sizes": scc_sizes,
                    "size_distribution": {
                        "max": max(scc_sizes) if scc_sizes else 0,
                        "min": min(scc_sizes) if scc_sizes else 0,
                        "mean": np.mean(scc_sizes) if scc_sizes else 0,
                        "std": np.std(scc_sizes) if scc_sizes else 0
                    }
                }
                
                # Weakly connected components
                wccs = list(nx.weakly_connected_components(graph))
                wcc_sizes = [len(wcc) for wcc in wccs]
                
                analysis["weakly_connected_components"] = {
                    "count": len(wccs),
                    "sizes": wcc_sizes,
                    "size_distribution": {
                        "max": max(wcc_sizes) if wcc_sizes else 0,
                        "min": min(wcc_sizes) if wcc_sizes else 0,
                        "mean": np.mean(wcc_sizes) if wcc_sizes else 0,
                        "std": np.std(wcc_sizes) if wcc_sizes else 0
                    }
                }
            else:
                # Connected components
                ccs = list(nx.connected_components(graph))
                cc_sizes = [len(cc) for cc in ccs]
                
                analysis["connected_components"] = {
                    "count": len(ccs),
                    "sizes": cc_sizes,
                    "size_distribution": {
                        "max": max(cc_sizes) if cc_sizes else 0,
                        "min": min(cc_sizes) if cc_sizes else 0,
                        "mean": np.mean(cc_sizes) if cc_sizes else 0,
                        "std": np.std(cc_sizes) if cc_sizes else 0
                    }
                }
            
            # Bridge analysis (edges whose removal increases components)
            try:
                if not graph.is_directed() and len(graph.edges) < 10000:
                    bridges = list(nx.bridges(graph))
                    analysis["bridges"] = {
                        "count": len(bridges),
                        "edges": bridges[:100]  # Limit output size
                    }
            except Exception as e:
                logger.warning(f"Bridge analysis failed: {e}")
                analysis["bridges"] = {"error": str(e)}
            
            # Articulation points (nodes whose removal increases components)
            try:
                if not graph.is_directed() and len(graph.nodes) < 10000:
                    articulation_points = list(nx.articulation_points(graph))
                    analysis["articulation_points"] = {
                        "count": len(articulation_points),
                        "nodes": articulation_points[:100]  # Limit output size
                    }
            except Exception as e:
                logger.warning(f"Articulation points analysis failed: {e}")
                analysis["articulation_points"] = {"error": str(e)}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in component analysis: {e}")
            return {"error": str(e)}