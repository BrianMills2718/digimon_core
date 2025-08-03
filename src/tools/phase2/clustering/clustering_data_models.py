"""Graph Clustering Data Models

Data structures for graph clustering algorithms.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np


class ClusteringAlgorithm(Enum):
    """Supported clustering algorithms"""
    SPECTRAL = "spectral"
    KMEANS = "kmeans"
    LOUVAIN = "louvain"
    LEIDEN = "leiden"
    HIERARCHICAL = "hierarchical"
    DBSCAN = "dbscan"
    LABEL_PROPAGATION = "label_propagation"
    GREEDY_MODULARITY = "greedy_modularity"
    ALL = "all"


class LaplacianType(Enum):
    """Types of graph Laplacian matrices"""
    COMBINATORIAL = "combinatorial"
    NORMALIZED = "normalized"
    RANDOM_WALK = "random_walk"


@dataclass
class ClusteringResult:
    """Results from graph clustering"""
    algorithm: str
    clusters: List[Set[str]]
    cluster_assignments: Dict[str, int]
    num_clusters: int
    modularity: float
    silhouette_score: Optional[float]
    execution_time: float
    parameters: Dict[str, Any]
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any]


@dataclass
class ClusteringQualityMetrics:
    """Quality metrics for clustering evaluation"""
    modularity: float
    conductance: float
    silhouette_score: Optional[float]
    calinski_harabasz_score: Optional[float]
    davies_bouldin_score: Optional[float]
    cluster_coefficient: float
    separation: float
    compactness: float


@dataclass
class SpectralClusteringConfig:
    """Configuration for spectral clustering"""
    num_clusters: Optional[int] = None
    laplacian_type: LaplacianType = LaplacianType.NORMALIZED
    eigen_solver: str = "arpack"
    assign_labels: str = "kmeans"
    n_init: int = 10
    gamma: float = 1.0
    affinity: str = "rbf"
    n_neighbors: int = 10
    degree_weighted: bool = True