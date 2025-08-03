"""Community Analysis and Statistics

Performs analysis and statistics calculation for community detection results.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any
from collections import Counter, defaultdict

from .community_data_models import CommunityResult, CommunityStats, CommunityDetails
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CommunityAnalyzer:
    """Analyze community detection results and calculate statistics"""
    
    def calculate_community_statistics(self, graph: nx.Graph, 
                                     community_results: List[CommunityResult]) -> CommunityStats:
        """Calculate comprehensive community detection statistics"""
        try:
            # Basic statistics
            algorithms_used = [result.algorithm for result in community_results if result.communities]
            
            # Find best algorithm by modularity
            best_modularity = -1
            best_algorithm = "none"
            for result in community_results:
                if result.modularity > best_modularity:
                    best_modularity = result.modularity
                    best_algorithm = result.algorithm
            
            # Calculate community size distributions
            community_size_distribution = {}
            average_community_sizes = {}
            
            for result in community_results:
                if result.communities:
                    # Count community sizes
                    community_sizes = Counter(result.communities.values())
                    size_counts = Counter(community_sizes.values())
                    
                    community_size_distribution[result.algorithm] = dict(size_counts)
                    average_community_sizes[result.algorithm] = np.mean(list(community_sizes.values()))
            
            # Calculate quality metrics for each algorithm
            quality_metrics = {}
            for result in community_results:
                if result.communities:
                    quality_metrics[result.algorithm] = {
                        "modularity": result.modularity,
                        "performance": result.performance,
                        "num_communities": result.num_communities,
                        "coverage": len(result.communities) / len(graph.nodes) if len(graph.nodes) > 0 else 0
                    }
            
            # Calculate graph statistics
            graph_statistics = self._calculate_graph_statistics(graph)
            
            return CommunityStats(
                total_algorithms=len(community_results),
                algorithms_used=algorithms_used,
                best_modularity=best_modularity,
                best_algorithm=best_algorithm,
                community_size_distribution=community_size_distribution,
                average_community_sizes=average_community_sizes,
                quality_metrics=quality_metrics,
                graph_statistics=graph_statistics,
                analysis_metadata={
                    "successful_algorithms": len([r for r in community_results if r.communities]),
                    "failed_algorithms": len([r for r in community_results if not r.communities])
                }
            )
            
        except Exception as e:
            logger.error(f"Community statistics calculation failed: {e}")
            return CommunityStats(
                total_algorithms=0,
                algorithms_used=[],
                best_modularity=0.0,
                best_algorithm="none",
                community_size_distribution={},
                average_community_sizes={},
                quality_metrics={},
                graph_statistics={},
                analysis_metadata={}
            )
    
    def analyze_communities_detailed(self, graph: nx.Graph, 
                                   communities: Dict[str, int]) -> List[CommunityDetails]:
        """Analyze individual communities in detail"""
        try:
            community_details = []
            
            # Group nodes by community
            communities_nodes = defaultdict(list)
            for node, community_id in communities.items():
                communities_nodes[community_id].append(node)
            
            # Analyze each community
            for community_id, nodes in communities_nodes.items():
                try:
                    details = self._analyze_single_community(graph, community_id, nodes, communities)
                    community_details.append(details)
                except Exception as e:
                    logger.warning(f"Failed to analyze community {community_id}: {e}")
                    continue
            
            # Sort by size (largest first)
            community_details.sort(key=lambda x: x.size, reverse=True)
            
            return community_details
            
        except Exception as e:
            logger.error(f"Detailed community analysis failed: {e}")
            return []
    
    def _analyze_single_community(self, graph: nx.Graph, community_id: int, 
                                 nodes: List[str], all_communities: Dict[str, int]) -> CommunityDetails:
        """Analyze a single community in detail"""
        try:
            # Create subgraph for this community
            subgraph = graph.subgraph(nodes)
            
            # Count internal edges
            internal_edges = len(subgraph.edges)
            
            # Count external edges
            external_edges = 0
            for node in nodes:
                for neighbor in graph.neighbors(node):
                    if neighbor not in nodes:
                        external_edges += 1
            
            # Calculate density
            n_nodes = len(nodes)
            max_internal_edges = n_nodes * (n_nodes - 1) // 2 if n_nodes > 1 else 0
            density = internal_edges / max_internal_edges if max_internal_edges > 0 else 0
            
            # Calculate conductance
            total_edges = internal_edges + external_edges
            conductance = external_edges / total_edges if total_edges > 0 else 0
            
            # Calculate modularity contribution
            modularity_contribution = self._calculate_community_modularity_contribution(
                graph, nodes, all_communities
            )
            
            return CommunityDetails(
                community_id=community_id,
                nodes=nodes,
                size=len(nodes),
                internal_edges=internal_edges,
                external_edges=external_edges,
                density=density,
                conductance=conductance,
                modularity_contribution=modularity_contribution
            )
            
        except Exception as e:
            logger.error(f"Single community analysis failed: {e}")
            return CommunityDetails(
                community_id=community_id,
                nodes=nodes,
                size=len(nodes),
                internal_edges=0,
                external_edges=0,
                density=0.0,
                conductance=0.0,
                modularity_contribution=0.0
            )
    
    def _calculate_community_modularity_contribution(self, graph: nx.Graph, 
                                                   community_nodes: List[str],
                                                   all_communities: Dict[str, int]) -> float:
        """Calculate modularity contribution of a single community"""
        try:
            m = len(graph.edges)  # Total number of edges
            if m == 0:
                return 0.0
            
            # Calculate internal edges
            internal_edges = 0
            for node in community_nodes:
                for neighbor in graph.neighbors(node):
                    if neighbor in community_nodes:
                        internal_edges += 1
            internal_edges = internal_edges // 2  # Each edge counted twice
            
            # Calculate sum of degrees
            degree_sum = sum(graph.degree(node) for node in community_nodes)
            
            # Modularity contribution for this community
            contribution = (internal_edges / m) - (degree_sum / (2 * m)) ** 2
            
            return contribution
            
        except Exception as e:
            logger.error(f"Modularity contribution calculation failed: {e}")
            return 0.0
    
    def _calculate_graph_statistics(self, graph: nx.Graph) -> Dict[str, Any]:
        """Calculate comprehensive graph statistics"""
        try:
            stats = {}
            
            # Basic properties
            stats["nodes"] = len(graph.nodes)
            stats["edges"] = len(graph.edges)
            stats["directed"] = graph.is_directed()
            stats["density"] = nx.density(graph)
            
            # Connectivity
            stats["connected"] = nx.is_connected(graph)
            stats["number_connected_components"] = nx.number_connected_components(graph)
            
            # Degree statistics
            degrees = dict(graph.degree())
            degree_values = list(degrees.values())
            
            if degree_values:
                stats["degree_statistics"] = {
                    "mean": np.mean(degree_values),
                    "median": np.median(degree_values),
                    "std": np.std(degree_values),
                    "min": min(degree_values),
                    "max": max(degree_values)
                }
            else:
                stats["degree_statistics"] = {
                    "mean": 0, "median": 0, "std": 0, "min": 0, "max": 0
                }
            
            # Clustering
            try:
                clustering = nx.clustering(graph)
                clustering_values = list(clustering.values())
                stats["clustering_coefficient"] = {
                    "mean": np.mean(clustering_values) if clustering_values else 0,
                    "global": nx.transitivity(graph)
                }
            except:
                stats["clustering_coefficient"] = {"mean": 0.0, "global": 0.0}
            
            # Path statistics (only for connected graphs)
            try:
                if nx.is_connected(graph):
                    stats["average_shortest_path_length"] = nx.average_shortest_path_length(graph)
                    stats["diameter"] = nx.diameter(graph)
                else:
                    # Use largest connected component
                    largest_cc = max(nx.connected_components(graph), key=len)
                    if len(largest_cc) > 1:
                        cc_graph = graph.subgraph(largest_cc)
                        stats["average_shortest_path_length"] = nx.average_shortest_path_length(cc_graph)
                        stats["diameter"] = nx.diameter(cc_graph)
                    else:
                        stats["average_shortest_path_length"] = 0
                        stats["diameter"] = 0
            except:
                stats["average_shortest_path_length"] = None
                stats["diameter"] = None
            
            return stats
            
        except Exception as e:
            logger.error(f"Graph statistics calculation failed: {e}")
            return {}
    
    def compare_algorithms(self, results: List[CommunityResult]) -> Dict[str, Any]:
        """Compare different community detection algorithms"""
        try:
            comparison = {
                "algorithm_rankings": {},
                "quality_comparison": {},
                "stability_analysis": {},
                "computational_efficiency": {}
            }
            
            # Rank algorithms by different metrics
            successful_results = [r for r in results if r.communities]
            
            if successful_results:
                # Rank by modularity
                modularity_ranking = sorted(successful_results, 
                                          key=lambda x: x.modularity, reverse=True)
                comparison["algorithm_rankings"]["by_modularity"] = [
                    (r.algorithm, r.modularity) for r in modularity_ranking
                ]
                
                # Rank by performance
                performance_ranking = sorted(successful_results, 
                                           key=lambda x: x.performance, reverse=True)
                comparison["algorithm_rankings"]["by_performance"] = [
                    (r.algorithm, r.performance) for r in performance_ranking
                ]
                
                # Rank by number of communities
                community_count_ranking = sorted(successful_results, 
                                               key=lambda x: x.num_communities)
                comparison["algorithm_rankings"]["by_community_count"] = [
                    (r.algorithm, r.num_communities) for r in community_count_ranking
                ]
                
                # Quality comparison
                for result in successful_results:
                    comparison["quality_comparison"][result.algorithm] = {
                        "modularity": result.modularity,
                        "performance": result.performance,
                        "num_communities": result.num_communities,
                        "coverage": len(result.communities) / max(1, len(result.communities))
                    }
                
                # Computational efficiency
                for result in successful_results:
                    comparison["computational_efficiency"][result.algorithm] = {
                        "calculation_time": result.calculation_time,
                        "time_per_node": result.calculation_time / max(1, len(result.communities))
                    }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Algorithm comparison failed: {e}")
            return {}
    
    def calculate_academic_confidence(self, stats: CommunityStats, 
                                    graph: nx.Graph, 
                                    results: List[CommunityResult]) -> float:
        """Calculate academic confidence score for research purposes"""
        try:
            confidence_factors = []
            
            # Graph size factor
            n_nodes = len(graph.nodes)
            if n_nodes >= 100:
                confidence_factors.append(0.9)
            elif n_nodes >= 50:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Algorithm diversity factor
            successful_algorithms = len([r for r in results if r.communities])
            if successful_algorithms >= 4:
                confidence_factors.append(0.9)
            elif successful_algorithms >= 2:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Modularity quality factor
            if stats.best_modularity > 0.3:
                confidence_factors.append(0.9)
            elif stats.best_modularity > 0.1:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.4)
            
            # Graph connectivity factor
            if stats.graph_statistics.get("connected", False):
                confidence_factors.append(0.9)
            elif stats.graph_statistics.get("number_connected_components", 0) <= 3:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Community structure clarity factor
            if stats.best_modularity > 0.4 and len(stats.algorithms_used) >= 2:
                # Check agreement between algorithms
                community_counts = [stats.quality_metrics[alg]["num_communities"] 
                                  for alg in stats.algorithms_used 
                                  if alg in stats.quality_metrics]
                if community_counts:
                    cv = np.std(community_counts) / np.mean(community_counts) if np.mean(community_counts) > 0 else 1
                    if cv < 0.3:  # Low coefficient of variation indicates agreement
                        confidence_factors.append(0.9)
                    elif cv < 0.6:
                        confidence_factors.append(0.7)
                    else:
                        confidence_factors.append(0.5)
                else:
                    confidence_factors.append(0.5)
            else:
                confidence_factors.append(0.5)
            
            # Overall confidence
            overall_confidence = np.mean(confidence_factors)
            
            return min(0.95, max(0.1, overall_confidence))
            
        except Exception as e:
            logger.error(f"Academic confidence calculation failed: {e}")
            return 0.5