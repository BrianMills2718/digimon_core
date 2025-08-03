"""Visualization Data Models

Data structures and enums for graph visualization.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class LayoutType(Enum):
    """Supported graph layout algorithms"""
    SPRING = "spring"
    CIRCULAR = "circular"
    KAMADA_KAWAI = "kamada_kawai"
    FRUCHTERMAN_REINGOLD = "fruchterman_reingold"
    SPECTRAL = "spectral"
    PLANAR = "planar"
    SHELL = "shell"
    SPIRAL = "spiral"
    RANDOM = "random"


class ColorScheme(Enum):
    """Supported color schemes for visualization"""
    ENTITY_TYPE = "entity_type"
    CONFIDENCE = "confidence"
    CENTRALITY = "centrality"
    COMMUNITY = "community"
    DEGREE = "degree"
    PAGERANK = "pagerank"
    CUSTOM = "custom"


@dataclass
class VisualizationConfig:
    """Configuration for graph visualization"""
    layout: LayoutType
    color_scheme: ColorScheme
    max_nodes: int
    max_edges: int
    node_size_metric: str
    edge_width_metric: str
    show_labels: bool
    interactive: bool
    output_format: str


@dataclass
class VisualizationResult:
    """Result of graph visualization"""
    visualization_data: Dict[str, Any]
    layout_info: Dict[str, Any]
    statistics: Dict[str, Any]
    file_paths: List[str]
    metadata: Dict[str, Any]