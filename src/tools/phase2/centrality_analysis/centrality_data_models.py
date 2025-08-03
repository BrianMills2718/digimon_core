"""Centrality Analysis Data Models

Data structures for centrality analysis.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any


class CentralityMetric(Enum):
    """Supported centrality metrics"""
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"
    KATZ = "katz"
    HARMONIC = "harmonic"
    LOAD = "load"
    INFORMATION = "information"
    CURRENT_FLOW_BETWEENNESS = "current_flow_betweenness"
    CURRENT_FLOW_CLOSENESS = "current_flow_closeness"
    SUBGRAPH = "subgraph"
    ALL = "all"


@dataclass
class CentralityResult:
    """Individual centrality result"""
    metric: str
    scores: Dict[str, float]
    normalized_scores: Dict[str, float]
    calculation_time: float
    node_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "metric": self.metric,
            "scores": self.scores,
            "normalized_scores": self.normalized_scores,
            "calculation_time": self.calculation_time,
            "node_count": self.node_count,
            "metadata": self.metadata
        }


@dataclass
class CentralityStats:
    """Centrality analysis statistics"""
    total_metrics: int
    metrics_calculated: List[str]
    correlation_matrix: Dict[str, Dict[str, float]]
    top_nodes_by_metric: Dict[str, List[tuple]]
    graph_statistics: Dict[str, Any]
    analysis_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "total_metrics": self.total_metrics,
            "metrics_calculated": self.metrics_calculated,
            "correlation_matrix": self.correlation_matrix,
            "top_nodes_by_metric": self.top_nodes_by_metric,
            "graph_statistics": self.graph_statistics,
            "analysis_metadata": self.analysis_metadata
        }


@dataclass
class CentralityConfig:
    """Configuration for centrality calculations"""
    metric: CentralityMetric
    normalized: bool
    k_nodes: int  # For approximation algorithms
    max_iterations: int
    tolerance: float
    directed: bool
    weighted: bool
    weight_attribute: str
    
    @classmethod
    def get_default_configs(cls) -> Dict[CentralityMetric, 'CentralityConfig']:
        """Get default configurations for all centrality metrics"""
        return {
            CentralityMetric.DEGREE: cls(
                metric=CentralityMetric.DEGREE,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=True,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.BETWEENNESS: cls(
                metric=CentralityMetric.BETWEENNESS,
                normalized=True,
                k_nodes=100,  # Sample for large graphs
                max_iterations=100,
                tolerance=1e-6,
                directed=True,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.CLOSENESS: cls(
                metric=CentralityMetric.CLOSENESS,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=True,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.EIGENVECTOR: cls(
                metric=CentralityMetric.EIGENVECTOR,
                normalized=True,
                k_nodes=None,
                max_iterations=1000,
                tolerance=1e-6,
                directed=False,  # Typically for undirected
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.PAGERANK: cls(
                metric=CentralityMetric.PAGERANK,
                normalized=True,
                k_nodes=None,
                max_iterations=1000,
                tolerance=1e-6,
                directed=True,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.KATZ: cls(
                metric=CentralityMetric.KATZ,
                normalized=True,
                k_nodes=None,
                max_iterations=1000,
                tolerance=1e-6,
                directed=True,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.HARMONIC: cls(
                metric=CentralityMetric.HARMONIC,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=True,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.LOAD: cls(
                metric=CentralityMetric.LOAD,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            ),
            CentralityMetric.INFORMATION: cls(
                metric=CentralityMetric.INFORMATION,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=False,
                weighted=True,
                weight_attribute="weight"
            ),
            CentralityMetric.CURRENT_FLOW_BETWEENNESS: cls(
                metric=CentralityMetric.CURRENT_FLOW_BETWEENNESS,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=False,
                weighted=True,
                weight_attribute="weight"
            ),
            CentralityMetric.CURRENT_FLOW_CLOSENESS: cls(
                metric=CentralityMetric.CURRENT_FLOW_CLOSENESS,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=False,
                weighted=True,
                weight_attribute="weight"
            ),
            CentralityMetric.SUBGRAPH: cls(
                metric=CentralityMetric.SUBGRAPH,
                normalized=True,
                k_nodes=None,
                max_iterations=100,
                tolerance=1e-6,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            )
        }