"""Metrics Data Models

Data structures and enums for graph metrics calculation.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class MetricCategory(Enum):
    """Categories of graph metrics"""
    BASIC = "basic"
    CENTRALITY = "centrality"
    CONNECTIVITY = "connectivity"
    CLUSTERING = "clustering"
    STRUCTURAL = "structural"
    EFFICIENCY = "efficiency"
    RESILIENCE = "resilience"
    ALL = "all"


@dataclass
class GraphMetrics:
    """Comprehensive graph metrics results"""
    basic_metrics: Dict[str, Any]
    centrality_metrics: Dict[str, Any]
    connectivity_metrics: Dict[str, Any]
    clustering_metrics: Dict[str, Any]
    structural_metrics: Dict[str, Any]
    efficiency_metrics: Dict[str, Any]
    resilience_metrics: Dict[str, Any]
    execution_time: float
    memory_used: int
    metadata: Dict[str, Any]


@dataclass
class MetricCalculationConfig:
    """Configuration for metrics calculation"""
    metric_categories: List[str]
    weighted: bool
    directed: bool
    normalize: bool
    include_node_level: bool
    performance_mode: str
    max_nodes: int
    calculation_timeout: float