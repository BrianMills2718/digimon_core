"""Temporal Analysis Data Models

Data structures and models for temporal graph analysis.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import networkx as nx


class TemporalAnalysisType(Enum):
    """Supported temporal analysis types"""
    EVOLUTION = "evolution"
    CHANGE_DETECTION = "change_detection"
    TREND_ANALYSIS = "trend_analysis"
    SNAPSHOT_COMPARISON = "snapshot_comparison"
    DYNAMIC_CENTRALITY = "dynamic_centrality"
    TEMPORAL_PATHS = "temporal_paths"
    COMMUNITY_EVOLUTION = "community_evolution"
    ALL = "all"


class ChangeType(Enum):
    """Types of changes in temporal networks"""
    NODE_ADDITION = "node_addition"
    NODE_REMOVAL = "node_removal"
    EDGE_ADDITION = "edge_addition"
    EDGE_REMOVAL = "edge_removal"
    WEIGHT_CHANGE = "weight_change"
    ATTRIBUTE_CHANGE = "attribute_change"
    COMMUNITY_CHANGE = "community_change"


@dataclass
class TemporalSnapshot:
    """Temporal graph snapshot"""
    timestamp: str
    graph: nx.Graph
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class ChangeEvent:
    """Graph change event"""
    timestamp: str
    change_type: ChangeType
    affected_elements: List[str]
    magnitude: float
    details: Dict[str, Any]


@dataclass
class TemporalTrend:
    """Temporal trend in graph metrics"""
    metric_name: str
    values: List[float]
    timestamps: List[str]
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: float
    change_points: List[str]