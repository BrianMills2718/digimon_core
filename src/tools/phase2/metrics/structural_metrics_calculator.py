"""Structural Metrics Calculator

Calculates structural properties like clustering, efficiency, and resilience.
"""

import networkx as nx
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class StructuralMetricsCalculator:
    """Calculate structural metrics"""
    
    def calculate_clustering_metrics(self, graph: nx.Graph, include_node_level: bool,
                                   performance_mode: str) -> Dict[str, Any]:
        """Calculate clustering-related metrics"""
        try:
            metrics = {}
            
            # Global clustering coefficient
            metrics["average_clustering"] = nx.average_clustering(graph)
            
            # Transitivity (global clustering coefficient)
            metrics["transitivity"] = nx.transitivity(graph)
            
            # Node-level clustering coefficients
            if include_node_level:
                node_clustering = nx.clustering(graph)
                clustering_values = list(node_clustering.values())
                
                metrics["node_clustering"] = {
                    "values": node_clustering,
                    "distribution": {
                        "min": min(clustering_values) if clustering_values else 0,
                        "max": max(clustering_values) if clustering_values else 0,
                        "mean": np.mean(clustering_values) if clustering_values else 0,
                        "std": np.std(clustering_values) if clustering_values else 0,
                        "median": np.median(clustering_values) if clustering_values else 0
                    }
                }
            
            # Square clustering (for comprehensive mode)
            if performance_mode in ["comprehensive", "research"]:
                try:
                    metrics["square_clustering"] = nx.square_clustering(graph)
                except Exception as e:
                    logger.warning(f"Square clustering calculation failed: {e}")
                    metrics["square_clustering"] = None
            
            # Triangles count
            if performance_mode in ["balanced", "comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 10000:
                        triangles = nx.triangles(graph)
                        triangle_counts = list(triangles.values())
                        
                        metrics["triangles"] = {
                            "total": sum(triangle_counts) // 3,  # Each triangle counted 3 times
                            "node_triangles": triangles if include_node_level else {},
                            "distribution": {
                                "min": min(triangle_counts) if triangle_counts else 0,
                                "max": max(triangle_counts) if triangle_counts else 0,
                                "mean": np.mean(triangle_counts) if triangle_counts else 0,
                                "std": np.std(triangle_counts) if triangle_counts else 0
                            }
                        }
                except Exception as e:
                    logger.warning(f"Triangle calculation failed: {e}")
                    metrics["triangles"] = {"error": str(e)}
            
            logger.info(f"Calculated clustering metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating clustering metrics: {e}")
            return {"error": str(e)}
    
    def calculate_efficiency_metrics(self, graph: nx.Graph, weighted: bool, 
                                   performance_mode: str) -> Dict[str, Any]:
        """Calculate efficiency-related metrics"""
        try:
            metrics = {}
            weight_attr = 'weight' if weighted else None
            
            # Global efficiency
            if performance_mode in ["balanced", "comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 2000:
                        metrics["global_efficiency"] = nx.global_efficiency(graph, weight=weight_attr)
                    else:
                        # Approximate for larger graphs
                        logger.info("Using approximation for global efficiency on large graph")
                        metrics["global_efficiency"] = self._approximate_global_efficiency(graph, weight_attr)
                except Exception as e:
                    logger.warning(f"Global efficiency calculation failed: {e}")
                    metrics["global_efficiency"] = None
            
            # Local efficiency
            if performance_mode in ["comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 1000:
                        metrics["local_efficiency"] = nx.local_efficiency(graph, weight=weight_attr)
                except Exception as e:
                    logger.warning(f"Local efficiency calculation failed: {e}")
                    metrics["local_efficiency"] = None
            
            # Nodal efficiency (for small graphs only)
            if performance_mode == "research" and len(graph.nodes) < 500:
                try:
                    nodal_efficiency = nx.nodal_efficiency(graph, weight=weight_attr)
                    efficiency_values = list(nodal_efficiency.values())
                    
                    metrics["nodal_efficiency"] = {
                        "values": nodal_efficiency,
                        "distribution": {
                            "min": min(efficiency_values) if efficiency_values else 0,
                            "max": max(efficiency_values) if efficiency_values else 0,
                            "mean": np.mean(efficiency_values) if efficiency_values else 0,
                            "std": np.std(efficiency_values) if efficiency_values else 0
                        }
                    }
                except Exception as e:
                    logger.warning(f"Nodal efficiency calculation failed: {e}")
                    metrics["nodal_efficiency"] = {"error": str(e)}
            
            logger.info(f"Calculated efficiency metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating efficiency metrics: {e}")
            return {"error": str(e)}
    
    def calculate_resilience_metrics(self, graph: nx.Graph, performance_mode: str) -> Dict[str, Any]:
        """Calculate network resilience metrics"""
        try:
            metrics = {}
            
            # Basic resilience indicators
            metrics["isolated_nodes"] = len(list(nx.isolates(graph)))
            metrics["nodes_with_degree_1"] = sum(1 for node, degree in graph.degree() if degree == 1)
            
            # Robustness measures (for smaller graphs)
            if performance_mode in ["comprehensive", "research"] and len(graph.nodes) < 1000:
                # Node connectivity (minimum number of nodes to remove to disconnect)
                try:
                    if not graph.is_directed():
                        metrics["node_connectivity"] = nx.node_connectivity(graph)
                        metrics["edge_connectivity"] = nx.edge_connectivity(graph)
                except Exception as e:
                    logger.warning(f"Connectivity calculation failed: {e}")
                    metrics["node_connectivity"] = None
                    metrics["edge_connectivity"] = None
            
            # Degree distribution entropy (diversity measure)
            try:
                degrees = [degree for node, degree in graph.degree()]
                degree_counts = {}
                for degree in degrees:
                    degree_counts[degree] = degree_counts.get(degree, 0) + 1
                
                total_nodes = len(degrees)
                entropy = 0
                for count in degree_counts.values():
                    prob = count / total_nodes
                    if prob > 0:
                        entropy -= prob * np.log2(prob)
                
                metrics["degree_entropy"] = entropy
            except Exception as e:
                logger.warning(f"Degree entropy calculation failed: {e}")
                metrics["degree_entropy"] = None
            
            # Assortativity (resilience indicator)
            if performance_mode in ["balanced", "comprehensive", "research"]:
                try:
                    if len(graph.nodes) < 10000:
                        metrics["assortativity"] = nx.degree_assortativity_coefficient(graph)
                except Exception as e:
                    logger.warning(f"Assortativity calculation failed: {e}")
                    metrics["assortativity"] = None
            
            # Rich club coefficient (for research mode)
            if performance_mode == "research" and len(graph.nodes) < 2000:
                try:
                    rich_club = nx.rich_club_coefficient(graph, normalized=True, seed=42)
                    metrics["rich_club_coefficient"] = rich_club
                except Exception as e:
                    logger.warning(f"Rich club coefficient calculation failed: {e}")
                    metrics["rich_club_coefficient"] = {"error": str(e)}
            
            logger.info(f"Calculated resilience metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating resilience metrics: {e}")
            return {"error": str(e)}
    
    def calculate_structural_properties(self, graph: nx.Graph, weighted: bool,
                                      performance_mode: str) -> Dict[str, Any]:
        """Calculate additional structural properties"""
        try:
            metrics = {}
            
            # Graph spectrum (eigenvalues of adjacency matrix)
            if performance_mode in ["comprehensive", "research"] and len(graph.nodes) < 1000:
                try:
                    spectrum = nx.adjacency_spectrum(graph)
                    spectrum_real = np.real(spectrum)  # Take real part
                    
                    metrics["spectrum"] = {
                        "eigenvalues": spectrum_real.tolist()[:20],  # Limit output
                        "spectral_radius": max(np.abs(spectrum)),
                        "spectral_gap": float(spectrum_real[0] - spectrum_real[1]) if len(spectrum_real) > 1 else 0
                    }
                except Exception as e:
                    logger.warning(f"Spectrum calculation failed: {e}")
                    metrics["spectrum"] = {"error": str(e)}
            
            # Laplacian spectrum
            if performance_mode == "research" and len(graph.nodes) < 500:
                try:
                    laplacian_spectrum = nx.laplacian_spectrum(graph)
                    laplacian_real = np.real(laplacian_spectrum)
                    
                    metrics["laplacian_spectrum"] = {
                        "eigenvalues": laplacian_real.tolist()[:20],  # Limit output
                        "algebraic_connectivity": float(laplacian_real[1]) if len(laplacian_real) > 1 else 0
                    }
                except Exception as e:
                    logger.warning(f"Laplacian spectrum calculation failed: {e}")
                    metrics["laplacian_spectrum"] = {"error": str(e)}
            
            # Small world properties
            if performance_mode in ["balanced", "comprehensive", "research"]:
                try:
                    # Calculate clustering and path length for small world analysis
                    if len(graph.nodes) < 5000:
                        clustering = nx.average_clustering(graph)
                        if nx.is_connected(graph) and not graph.is_directed():
                            path_length = nx.average_shortest_path_length(graph)
                            
                            # Compare with random graph (simplified)
                            n = len(graph.nodes)
                            m = len(graph.edges)
                            p = 2 * m / (n * (n - 1))  # Edge probability for equivalent random graph
                            
                            random_clustering = p  # Expected clustering for random graph
                            random_path_length = np.log(n) / np.log(2 * m / n) if m > 0 else float('inf')
                            
                            metrics["small_world"] = {
                                "clustering_coefficient": clustering,
                                "average_path_length": path_length,
                                "clustering_ratio": clustering / random_clustering if random_clustering > 0 else 0,
                                "path_length_ratio": path_length / random_path_length if random_path_length > 0 else 0,
                                "small_world_sigma": (clustering / random_clustering) / (path_length / random_path_length) if random_clustering > 0 and random_path_length > 0 else 0
                            }
                except Exception as e:
                    logger.warning(f"Small world analysis failed: {e}")
                    metrics["small_world"] = {"error": str(e)}
            
            logger.info(f"Calculated structural properties")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating structural properties: {e}")
            return {"error": str(e)}
    
    def _approximate_global_efficiency(self, graph: nx.Graph, weight_attr=None):
        """Approximate global efficiency for large graphs using sampling"""
        try:
            import random
            
            nodes = list(graph.nodes())
            sample_size = min(1000, len(nodes))
            sampled_nodes = random.sample(nodes, sample_size)
            
            total_efficiency = 0
            pair_count = 0
            
            for i, source in enumerate(sampled_nodes):
                for target in sampled_nodes[i+1:]:
                    try:
                        if weight_attr:
                            path_length = nx.shortest_path_length(graph, source, target, weight=weight_attr)
                        else:
                            path_length = nx.shortest_path_length(graph, source, target)
                        
                        if path_length > 0:
                            total_efficiency += 1.0 / path_length
                        pair_count += 1
                    except nx.NetworkXNoPath:
                        pair_count += 1
            
            if pair_count > 0:
                return total_efficiency / pair_count
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error in approximate global efficiency: {e}")
            return None