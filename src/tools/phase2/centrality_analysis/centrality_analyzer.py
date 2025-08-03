"""Centrality Analysis and Statistics

Performs correlation analysis and statistical analysis of centrality results.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict
from scipy.stats import pearsonr, spearmanr
from scipy import stats

from .centrality_data_models import CentralityResult, CentralityStats
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CentralityAnalyzer:
    """Analyze centrality results and calculate statistics"""
    
    def calculate_correlation_matrix(self, all_scores: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between different centrality measures"""
        try:
            metrics = list(all_scores.keys())
            correlation_matrix = {}
            
            for metric1 in metrics:
                correlation_matrix[metric1] = {}
                for metric2 in metrics:
                    if metric1 == metric2:
                        correlation_matrix[metric1][metric2] = 1.0
                    else:
                        # Get common nodes
                        common_nodes = set(all_scores[metric1].keys()) & set(all_scores[metric2].keys())
                        
                        if len(common_nodes) > 2:
                            values1 = [all_scores[metric1][node] for node in common_nodes]
                            values2 = [all_scores[metric2][node] for node in common_nodes]
                            
                            try:
                                # Use Pearson correlation
                                correlation, p_value = pearsonr(values1, values2)
                                correlation_matrix[metric1][metric2] = correlation
                            except:
                                correlation_matrix[metric1][metric2] = 0.0
                        else:
                            correlation_matrix[metric1][metric2] = 0.0
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Correlation matrix calculation failed: {e}")
            return {}
    
    def calculate_graph_statistics(self, graph: nx.Graph) -> Dict[str, Any]:
        """Calculate comprehensive graph statistics"""
        try:
            stats = {}
            
            # Basic properties
            stats["nodes"] = len(graph.nodes)
            stats["edges"] = len(graph.edges)
            stats["directed"] = graph.is_directed()
            stats["density"] = nx.density(graph)
            
            # Connectivity
            if graph.is_directed():
                stats["weakly_connected"] = nx.is_weakly_connected(graph)
                stats["strongly_connected"] = nx.is_strongly_connected(graph)
                stats["number_weakly_connected_components"] = nx.number_weakly_connected_components(graph)
                stats["number_strongly_connected_components"] = nx.number_strongly_connected_components(graph)
            else:
                stats["connected"] = nx.is_connected(graph)
                stats["number_connected_components"] = nx.number_connected_components(graph)
            
            # Degree statistics
            degrees = dict(graph.degree())
            degree_values = list(degrees.values())
            
            stats["degree_statistics"] = {
                "mean": np.mean(degree_values),
                "median": np.median(degree_values),
                "std": np.std(degree_values),
                "min": min(degree_values),
                "max": max(degree_values)
            }
            
            # Clustering
            try:
                if graph.is_directed():
                    clustering = nx.clustering(graph.to_undirected())
                else:
                    clustering = nx.clustering(graph)
                
                clustering_values = list(clustering.values())
                stats["clustering_coefficient"] = {
                    "mean": np.mean(clustering_values),
                    "global": nx.transitivity(graph)
                }
            except:
                stats["clustering_coefficient"] = {"mean": 0.0, "global": 0.0}
            
            # Path statistics (for connected components only)
            try:
                if graph.is_directed():
                    if nx.is_strongly_connected(graph):
                        stats["average_shortest_path_length"] = nx.average_shortest_path_length(graph)
                        stats["diameter"] = nx.diameter(graph)
                    else:
                        # Use largest strongly connected component
                        largest_scc = max(nx.strongly_connected_components(graph), key=len)
                        if len(largest_scc) > 1:
                            scc_graph = graph.subgraph(largest_scc)
                            stats["average_shortest_path_length"] = nx.average_shortest_path_length(scc_graph)
                            stats["diameter"] = nx.diameter(scc_graph)
                else:
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
            except:
                stats["average_shortest_path_length"] = None
                stats["diameter"] = None
            
            # Small-world properties
            try:
                if not graph.is_directed() and nx.is_connected(graph):
                    random_clustering = stats["density"]
                    actual_clustering = stats["clustering_coefficient"]["mean"]
                    
                    if random_clustering > 0:
                        stats["small_world_sigma"] = (actual_clustering / random_clustering) / (
                            stats["average_shortest_path_length"] / np.log(len(graph.nodes))
                        ) if stats["average_shortest_path_length"] else None
                    else:
                        stats["small_world_sigma"] = None
                else:
                    stats["small_world_sigma"] = None
            except:
                stats["small_world_sigma"] = None
            
            return stats
            
        except Exception as e:
            logger.error(f"Graph statistics calculation failed: {e}")
            return {}
    
    def analyze_centrality_distributions(self, results: List[CentralityResult]) -> Dict[str, Any]:
        """Analyze distributions of centrality values"""
        try:
            distributions = {}
            
            for result in results:
                metric = result.metric
                values = list(result.normalized_scores.values())
                
                if values:
                    distributions[metric] = {
                        "mean": np.mean(values),
                        "median": np.median(values),
                        "std": np.std(values),
                        "min": min(values),
                        "max": max(values),
                        "skewness": stats.skew(values),
                        "kurtosis": stats.kurtosis(values),
                        "percentiles": {
                            "25th": np.percentile(values, 25),
                            "75th": np.percentile(values, 75),
                            "90th": np.percentile(values, 90),
                            "95th": np.percentile(values, 95)
                        }
                    }
                else:
                    distributions[metric] = {}
            
            return distributions
            
        except Exception as e:
            logger.error(f"Distribution analysis failed: {e}")
            return {}
    
    def identify_top_nodes(self, all_scores: Dict[str, Dict[str, float]], 
                          top_k: int = 20) -> Dict[str, List[tuple]]:
        """Identify top nodes for each centrality metric"""
        try:
            top_nodes = {}
            
            for metric, scores in all_scores.items():
                if scores:
                    # Sort nodes by score (descending)
                    sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                    top_nodes[metric] = sorted_nodes[:top_k]
                else:
                    top_nodes[metric] = []
            
            return top_nodes
            
        except Exception as e:
            logger.error(f"Top nodes identification failed: {e}")
            return {}
    
    def calculate_centrality_agreement(self, all_scores: Dict[str, Dict[str, float]], 
                                     top_k: int = 10) -> Dict[str, Any]:
        """Calculate agreement between different centrality measures"""
        try:
            agreement_analysis = {
                "top_node_overlap": {},
                "rank_correlation": {},
                "consensus_ranking": []
            }
            
            # Get top nodes for each metric
            top_nodes = self.identify_top_nodes(all_scores, top_k)
            
            # Calculate pairwise overlap
            metrics = list(all_scores.keys())
            for i, metric1 in enumerate(metrics):
                agreement_analysis["top_node_overlap"][metric1] = {}
                for j, metric2 in enumerate(metrics):
                    if i <= j:
                        if metric1 == metric2:
                            overlap = 1.0
                        else:
                            top1 = set(node for node, score in top_nodes.get(metric1, []))
                            top2 = set(node for node, score in top_nodes.get(metric2, []))
                            overlap = len(top1 & top2) / len(top1 | top2) if (top1 | top2) else 0.0
                        
                        agreement_analysis["top_node_overlap"][metric1][metric2] = overlap
                        agreement_analysis["top_node_overlap"][metric2] = agreement_analysis["top_node_overlap"].get(metric2, {})
                        agreement_analysis["top_node_overlap"][metric2][metric1] = overlap
            
            # Calculate rank correlation (Spearman)
            for i, metric1 in enumerate(metrics):
                agreement_analysis["rank_correlation"][metric1] = {}
                for j, metric2 in enumerate(metrics):
                    if metric1 == metric2:
                        correlation = 1.0
                    else:
                        common_nodes = set(all_scores[metric1].keys()) & set(all_scores[metric2].keys())
                        if len(common_nodes) > 2:
                            ranks1 = []
                            ranks2 = []
                            
                            # Get ranks for common nodes
                            sorted1 = sorted([(node, score) for node, score in all_scores[metric1].items() 
                                            if node in common_nodes], key=lambda x: x[1], reverse=True)
                            sorted2 = sorted([(node, score) for node, score in all_scores[metric2].items() 
                                            if node in common_nodes], key=lambda x: x[1], reverse=True)
                            
                            rank1_dict = {node: rank for rank, (node, score) in enumerate(sorted1)}
                            rank2_dict = {node: rank for rank, (node, score) in enumerate(sorted2)}
                            
                            for node in common_nodes:
                                ranks1.append(rank1_dict[node])
                                ranks2.append(rank2_dict[node])
                            
                            try:
                                correlation, p_value = spearmanr(ranks1, ranks2)
                                correlation = correlation if not np.isnan(correlation) else 0.0
                            except:
                                correlation = 0.0
                        else:
                            correlation = 0.0
                    
                    agreement_analysis["rank_correlation"][metric1][metric2] = correlation
            
            # Create consensus ranking
            if all_scores:
                # Use Borda count method
                all_nodes = set()
                for scores in all_scores.values():
                    all_nodes.update(scores.keys())
                
                borda_scores = defaultdict(float)
                for metric, scores in all_scores.items():
                    if scores:
                        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                        for rank, (node, score) in enumerate(sorted_nodes):
                            borda_scores[node] += len(sorted_nodes) - rank
                
                consensus_ranking = sorted(borda_scores.items(), key=lambda x: x[1], reverse=True)
                agreement_analysis["consensus_ranking"] = consensus_ranking[:top_k]
            
            return agreement_analysis
            
        except Exception as e:
            logger.error(f"Centrality agreement calculation failed: {e}")
            return {}
    
    def calculate_academic_confidence(self, results: List[CentralityResult], 
                                    graph: nx.Graph, 
                                    correlation_matrix: Dict[str, Dict[str, float]]) -> float:
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
            
            # Number of metrics calculated
            num_metrics = len(results)
            if num_metrics >= 8:
                confidence_factors.append(0.9)
            elif num_metrics >= 5:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Graph connectivity factor
            if graph.is_directed():
                connectivity = nx.is_strongly_connected(graph)
            else:
                connectivity = nx.is_connected(graph)
            
            confidence_factors.append(0.9 if connectivity else 0.6)
            
            # Correlation matrix completeness
            if correlation_matrix:
                total_pairs = num_metrics * (num_metrics - 1) / 2
                calculated_pairs = sum(1 for metric1 in correlation_matrix.values() 
                                     for metric2, corr in metric1.items() 
                                     if isinstance(corr, (int, float)) and not np.isnan(corr))
                
                if calculated_pairs >= total_pairs * 0.8:
                    confidence_factors.append(0.9)
                elif calculated_pairs >= total_pairs * 0.5:
                    confidence_factors.append(0.7)
                else:
                    confidence_factors.append(0.5)
            else:
                confidence_factors.append(0.3)
            
            # Calculation success rate
            successful_calculations = sum(1 for result in results if result.scores)
            if successful_calculations == len(results):
                confidence_factors.append(0.9)
            elif successful_calculations >= len(results) * 0.8:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Overall confidence
            overall_confidence = np.mean(confidence_factors)
            
            return min(0.95, max(0.1, overall_confidence))
            
        except Exception as e:
            logger.error(f"Academic confidence calculation failed: {e}")
            return 0.5