"""Metrics Aggregator

Aggregates and analyzes metrics from all calculators.
"""

import networkx as nx
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from .metrics_data_models import GraphMetrics, MetricCategory
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class MetricsAggregator:
    """Aggregate and analyze comprehensive graph metrics"""
    
    def create_comprehensive_metrics(self, basic_metrics: Dict[str, Any], 
                                   centrality_metrics: Dict[str, Any],
                                   connectivity_metrics: Dict[str, Any],
                                   clustering_metrics: Dict[str, Any],
                                   structural_metrics: Dict[str, Any],
                                   efficiency_metrics: Dict[str, Any],
                                   resilience_metrics: Dict[str, Any],
                                   execution_time: float,
                                   memory_used: int) -> GraphMetrics:
        """Create comprehensive metrics object"""
        return GraphMetrics(
            basic_metrics=basic_metrics,
            centrality_metrics=centrality_metrics,
            connectivity_metrics=connectivity_metrics,
            clustering_metrics=clustering_metrics,
            structural_metrics=structural_metrics,
            efficiency_metrics=efficiency_metrics,
            resilience_metrics=resilience_metrics,
            execution_time=execution_time,
            memory_used=memory_used,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "metrics_calculated": self._count_calculated_metrics(
                    basic_metrics, centrality_metrics, connectivity_metrics,
                    clustering_metrics, structural_metrics, efficiency_metrics, resilience_metrics
                )
            }
        )
    
    def calculate_statistical_summary(self, graph: nx.Graph, metrics_result: GraphMetrics) -> Dict[str, Any]:
        """Calculate statistical summary of all metrics"""
        try:
            summary = {
                "graph_overview": {
                    "nodes": len(graph.nodes),
                    "edges": len(graph.edges),
                    "density": metrics_result.basic_metrics.get("density", 0),
                    "connected": metrics_result.connectivity_metrics.get("connected", False)
                },
                "centrality_summary": self._summarize_centrality_metrics(metrics_result.centrality_metrics),
                "structural_summary": self._summarize_structural_metrics(
                    metrics_result.clustering_metrics, 
                    metrics_result.structural_metrics
                ),
                "connectivity_summary": self._summarize_connectivity_metrics(metrics_result.connectivity_metrics),
                "performance_summary": {
                    "execution_time": metrics_result.execution_time,
                    "memory_used_mb": metrics_result.memory_used / (1024 * 1024),
                    "metrics_calculated": len(self._get_all_metric_names(metrics_result))
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating statistical summary: {e}")
            return {"error": str(e)}
    
    def generate_academic_summary(self, graph: nx.Graph, metrics_result: GraphMetrics) -> Dict[str, Any]:
        """Generate academic research summary"""
        try:
            summary = {
                "network_characterization": {
                    "type": "directed" if metrics_result.basic_metrics.get("directed") else "undirected",
                    "scale": self._classify_network_scale(len(graph.nodes)),
                    "density_class": self._classify_density(metrics_result.basic_metrics.get("density", 0)),
                    "connectivity_class": self._classify_connectivity(metrics_result.connectivity_metrics)
                },
                "topological_properties": {
                    "degree_distribution": self._analyze_degree_distribution(metrics_result.basic_metrics),
                    "clustering_properties": self._analyze_clustering_properties(metrics_result.clustering_metrics),
                    "path_properties": self._analyze_path_properties(metrics_result.connectivity_metrics),
                    "centrality_dominance": self._analyze_centrality_dominance(metrics_result.centrality_metrics)
                },
                "structural_significance": {
                    "small_world_properties": self._assess_small_world(metrics_result.structural_metrics),
                    "scale_free_properties": self._assess_scale_free(metrics_result.basic_metrics),
                    "resilience_assessment": self._assess_resilience(metrics_result.resilience_metrics),
                    "efficiency_assessment": self._assess_efficiency(metrics_result.efficiency_metrics)
                },
                "research_implications": {
                    "complexity_indicators": self._identify_complexity_indicators(metrics_result),
                    "analytical_recommendations": self._generate_analytical_recommendations(metrics_result),
                    "methodological_notes": self._generate_methodological_notes(graph, metrics_result)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating academic summary: {e}")
            return {"error": str(e)}
    
    def calculate_academic_confidence(self, metrics_result: GraphMetrics, graph: nx.Graph) -> float:
        """Calculate confidence score for academic use"""
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
            
            # Connectivity factor
            if metrics_result.connectivity_metrics.get("connected", False):
                confidence_factors.append(0.9)
            else:
                largest_cc_fraction = metrics_result.connectivity_metrics.get("largest_cc_fraction", 0)
                confidence_factors.append(0.3 + 0.6 * largest_cc_fraction)
            
            # Metrics completeness factor
            total_possible_metrics = 50  # Approximate
            calculated_metrics = len(self._get_all_metric_names(metrics_result))
            completeness = calculated_metrics / total_possible_metrics
            confidence_factors.append(0.5 + 0.5 * completeness)
            
            # Centrality consistency factor
            centrality_correlations = self._estimate_centrality_consistency(metrics_result.centrality_metrics)
            confidence_factors.append(centrality_correlations)
            
            # Overall confidence
            overall_confidence = np.mean(confidence_factors)
            
            return min(0.95, max(0.1, overall_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def format_output(self, metrics_result: GraphMetrics, stats_summary: Dict[str, Any],
                     academic_summary: Dict[str, Any], confidence_score: float) -> Dict[str, Any]:
        """Format comprehensive output"""
        return {
            "metrics": {
                "basic": metrics_result.basic_metrics,
                "centrality": metrics_result.centrality_metrics,
                "connectivity": metrics_result.connectivity_metrics,
                "clustering": metrics_result.clustering_metrics,
                "structural": metrics_result.structural_metrics,
                "efficiency": metrics_result.efficiency_metrics,
                "resilience": metrics_result.resilience_metrics
            },
            "summary": {
                "statistical": stats_summary,
                "academic": academic_summary,
                "confidence_score": confidence_score
            },
            "metadata": {
                "execution_time": metrics_result.execution_time,
                "memory_used": metrics_result.memory_used,
                "timestamp": metrics_result.metadata.get("timestamp"),
                "metrics_calculated": metrics_result.metadata.get("metrics_calculated", 0)
            }
        }
    
    def _count_calculated_metrics(self, *metric_dicts) -> int:
        """Count total number of calculated metrics"""
        count = 0
        for metric_dict in metric_dicts:
            if isinstance(metric_dict, dict):
                count += len([k for k, v in metric_dict.items() 
                            if not isinstance(v, dict) or "error" not in v])
        return count
    
    def _summarize_centrality_metrics(self, centrality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize centrality metrics"""
        summary = {}
        for measure, data in centrality_metrics.items():
            if isinstance(data, dict) and "stats" in data:
                stats = data["stats"]
                summary[measure] = {
                    "max_value": stats.get("max", 0),
                    "mean_value": stats.get("mean", 0),
                    "centralization": stats.get("centralization", 0),
                    "top_node": stats.get("top_nodes", [{}])[0] if stats.get("top_nodes") else {}
                }
        return summary
    
    def _summarize_structural_metrics(self, clustering_metrics: Dict[str, Any], 
                                    structural_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize structural metrics"""
        return {
            "clustering": {
                "average": clustering_metrics.get("average_clustering", 0),
                "transitivity": clustering_metrics.get("transitivity", 0)
            },
            "small_world": structural_metrics.get("small_world", {}),
            "spectrum": structural_metrics.get("spectrum", {})
        }
    
    def _summarize_connectivity_metrics(self, connectivity_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize connectivity metrics"""
        return {
            "connected": connectivity_metrics.get("connected", False),
            "components": connectivity_metrics.get("connected_components", 0),
            "diameter": connectivity_metrics.get("diameter"),
            "average_path_length": connectivity_metrics.get("average_shortest_path_length")
        }
    
    def _get_all_metric_names(self, metrics_result: GraphMetrics) -> List[str]:
        """Get all metric names from results"""
        names = []
        for metric_dict in [metrics_result.basic_metrics, metrics_result.centrality_metrics,
                           metrics_result.connectivity_metrics, metrics_result.clustering_metrics,
                           metrics_result.structural_metrics, metrics_result.efficiency_metrics,
                           metrics_result.resilience_metrics]:
            if isinstance(metric_dict, dict):
                names.extend(metric_dict.keys())
        return names
    
    def _classify_network_scale(self, n_nodes: int) -> str:
        """Classify network scale"""
        if n_nodes < 100:
            return "small"
        elif n_nodes < 1000:
            return "medium"
        elif n_nodes < 10000:
            return "large"
        else:
            return "very_large"
    
    def _classify_density(self, density: float) -> str:
        """Classify network density"""
        if density < 0.01:
            return "sparse"
        elif density < 0.1:
            return "moderate"
        else:
            return "dense"
    
    def _classify_connectivity(self, connectivity_metrics: Dict[str, Any]) -> str:
        """Classify connectivity"""
        if connectivity_metrics.get("connected", False):
            return "connected"
        else:
            largest_cc_fraction = connectivity_metrics.get("largest_cc_fraction", 0)
            if largest_cc_fraction > 0.8:
                return "mostly_connected"
            elif largest_cc_fraction > 0.5:
                return "partially_connected"
            else:
                return "fragmented"
    
    def _analyze_degree_distribution(self, basic_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze degree distribution properties"""
        degree_stats = basic_metrics.get("degree_stats", {})
        return {
            "heterogeneity": degree_stats.get("std", 0) / max(degree_stats.get("mean", 1), 1),
            "max_degree": degree_stats.get("max", 0),
            "degree_variance": degree_stats.get("std", 0) ** 2
        }
    
    def _analyze_clustering_properties(self, clustering_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze clustering properties"""
        return {
            "global_clustering": clustering_metrics.get("average_clustering", 0),
            "transitivity": clustering_metrics.get("transitivity", 0),
            "clustering_heterogeneity": self._calculate_clustering_heterogeneity(clustering_metrics)
        }
    
    def _analyze_path_properties(self, connectivity_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze path properties"""
        return {
            "characteristic_path_length": connectivity_metrics.get("average_shortest_path_length"),
            "diameter": connectivity_metrics.get("diameter"),
            "radius": connectivity_metrics.get("radius")
        }
    
    def _analyze_centrality_dominance(self, centrality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze centrality dominance"""
        dominance = {}
        for measure, data in centrality_metrics.items():
            if isinstance(data, dict) and "stats" in data:
                centralization = data["stats"].get("centralization", 0)
                dominance[f"{measure}_dominance"] = "high" if centralization > 0.7 else "moderate" if centralization > 0.3 else "low"
        return dominance
    
    def _assess_small_world(self, structural_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess small world properties"""
        small_world = structural_metrics.get("small_world", {})
        if small_world and not isinstance(small_world, dict) or "error" in small_world:
            return {"assessment": "undetermined"}
        
        sigma = small_world.get("small_world_sigma", 0)
        if sigma > 1:
            return {"assessment": "small_world", "sigma": sigma}
        else:
            return {"assessment": "not_small_world", "sigma": sigma}
    
    def _assess_scale_free(self, basic_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess scale-free properties"""
        # Simple heuristic based on degree distribution
        degree_stats = basic_metrics.get("degree_stats", {})
        mean_degree = degree_stats.get("mean", 0)
        max_degree = degree_stats.get("max", 0)
        
        if mean_degree > 0 and max_degree / mean_degree > 10:
            return {"assessment": "potentially_scale_free", "degree_ratio": max_degree / mean_degree}
        else:
            return {"assessment": "not_scale_free", "degree_ratio": max_degree / mean_degree if mean_degree > 0 else 0}
    
    def _assess_resilience(self, resilience_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess network resilience"""
        connectivity = resilience_metrics.get("node_connectivity", 0)
        assortativity = resilience_metrics.get("assortativity", 0)
        
        if connectivity is None or connectivity == 0:
            resilience_level = "low"
        elif connectivity >= 3:
            resilience_level = "high"
        else:
            resilience_level = "moderate"
        
        return {
            "resilience_level": resilience_level,
            "connectivity": connectivity,
            "assortativity": assortativity
        }
    
    def _assess_efficiency(self, efficiency_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess network efficiency"""
        global_eff = efficiency_metrics.get("global_efficiency")
        local_eff = efficiency_metrics.get("local_efficiency")
        
        if global_eff is None:
            return {"assessment": "undetermined"}
        
        if global_eff > 0.5:
            efficiency_level = "high"
        elif global_eff > 0.2:
            efficiency_level = "moderate"
        else:
            efficiency_level = "low"
        
        return {
            "efficiency_level": efficiency_level,
            "global_efficiency": global_eff,
            "local_efficiency": local_eff
        }
    
    def _identify_complexity_indicators(self, metrics_result: GraphMetrics) -> List[str]:
        """Identify complexity indicators"""
        indicators = []
        
        # High clustering
        if metrics_result.clustering_metrics.get("average_clustering", 0) > 0.3:
            indicators.append("high_clustering")
        
        # Scale-free properties
        basic = metrics_result.basic_metrics
        degree_stats = basic.get("degree_stats", {})
        if degree_stats.get("max", 0) > 10 * degree_stats.get("mean", 1):
            indicators.append("scale_free_tendencies")
        
        # Small world
        small_world = metrics_result.structural_metrics.get("small_world", {})
        if isinstance(small_world, dict) and small_world.get("small_world_sigma", 0) > 1:
            indicators.append("small_world_properties")
        
        return indicators
    
    def _generate_analytical_recommendations(self, metrics_result: GraphMetrics) -> List[str]:
        """Generate analytical recommendations"""
        recommendations = []
        
        # Based on connectivity
        if not metrics_result.connectivity_metrics.get("connected", False):
            recommendations.append("Consider component-wise analysis due to disconnected structure")
        
        # Based on size
        n_nodes = metrics_result.basic_metrics.get("nodes", 0)
        if n_nodes < 50:
            recommendations.append("Small network size may limit statistical significance of some metrics")
        
        # Based on density
        density = metrics_result.basic_metrics.get("density", 0)
        if density > 0.5:
            recommendations.append("High density may indicate over-connected or artificial network")
        
        return recommendations
    
    def _generate_methodological_notes(self, graph: nx.Graph, metrics_result: GraphMetrics) -> List[str]:
        """Generate methodological notes"""
        notes = []
        
        notes.append(f"Analysis performed on {'directed' if graph.is_directed() else 'undirected'} graph")
        notes.append(f"Graph contains {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        
        if metrics_result.execution_time > 60:
            notes.append("Long computation time may indicate approximations were used for some metrics")
        
        return notes
    
    def _calculate_clustering_heterogeneity(self, clustering_metrics: Dict[str, Any]) -> float:
        """Calculate clustering coefficient heterogeneity"""
        node_clustering = clustering_metrics.get("node_clustering", {})
        if isinstance(node_clustering, dict) and "distribution" in node_clustering:
            dist = node_clustering["distribution"]
            mean_val = dist.get("mean", 0)
            std_val = dist.get("std", 0)
            return std_val / max(mean_val, 0.001)
        return 0
    
    def _estimate_centrality_consistency(self, centrality_metrics: Dict[str, Any]) -> float:
        """Estimate centrality measure consistency"""
        # Simple heuristic: if multiple centrality measures are available and correlated
        measures_with_values = [name for name, data in centrality_metrics.items() 
                              if isinstance(data, dict) and "values" in data]
        
        if len(measures_with_values) >= 2:
            return 0.8  # Assume good consistency if multiple measures calculated
        elif measures_with_values:
            return 0.6  # Moderate consistency with single measure
        else:
            return 0.3  # Low consistency without centrality measures