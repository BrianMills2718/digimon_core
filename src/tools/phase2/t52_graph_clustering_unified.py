"""
Compatibility module for t52_graph_clustering_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t52_graph_clustering import *

# Backward compatibility aliases
T52GraphClusteringTool = GraphClusteringTool

# Add missing enum for compatibility
from enum import Enum
class LaplacianType(Enum):
    UNNORMALIZED = "unnormalized"
    NORMALIZED = "normalized"
    RANDOM_WALK = "random_walk"

# Add missing result class for compatibility
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ClusteringResult:
    """Result of clustering analysis."""
    clusters: List[List[str]]
    cluster_labels: Dict[str, int] 
    modularity: float
    num_clusters: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}