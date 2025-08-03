"""Community Detection Data Models

Data structures for community detection analysis.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional


class CommunityAlgorithm(Enum):
    """Supported community detection algorithms"""
    LOUVAIN = "louvain"
    LEIDEN = "leiden"
    LABEL_PROPAGATION = "label_propagation"
    GREEDY_MODULARITY = "greedy_modularity"
    FLUID_COMMUNITIES = "fluid_communities"
    GIRVAN_NEWMAN = "girvan_newman"
    ALL = "all"


@dataclass
class CommunityResult:
    """Individual community detection result"""
    algorithm: str
    communities: Dict[str, int]  # node_id -> community_id
    modularity: float
    performance: float
    num_communities: int
    calculation_time: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "algorithm": self.algorithm,
            "communities": self.communities,
            "modularity": self.modularity,
            "performance": self.performance,
            "num_communities": self.num_communities,
            "calculation_time": self.calculation_time,
            "metadata": self.metadata
        }


@dataclass
class CommunityStats:
    """Community detection statistics"""
    total_algorithms: int
    algorithms_used: List[str]
    best_modularity: float
    best_algorithm: str
    community_size_distribution: Dict[str, Dict[int, int]]  # algorithm -> {size: count}
    average_community_sizes: Dict[str, float]
    quality_metrics: Dict[str, Dict[str, float]]
    graph_statistics: Dict[str, Any]
    analysis_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "total_algorithms": self.total_algorithms,
            "algorithms_used": self.algorithms_used,
            "best_modularity": self.best_modularity,
            "best_algorithm": self.best_algorithm,
            "community_size_distribution": self.community_size_distribution,
            "average_community_sizes": self.average_community_sizes,
            "quality_metrics": self.quality_metrics,
            "graph_statistics": self.graph_statistics,
            "analysis_metadata": self.analysis_metadata
        }


@dataclass
class CommunityConfig:
    """Configuration for community detection algorithms"""
    algorithm: CommunityAlgorithm
    resolution: float
    max_iterations: int
    tolerance: float
    min_community_size: int
    max_community_size: int
    random_seed: Optional[int]
    directed: bool
    weighted: bool
    weight_attribute: str
    
    @classmethod
    def get_default_configs(cls) -> Dict[CommunityAlgorithm, 'CommunityConfig']:
        """Get default configurations for all community detection algorithms"""
        return {
            CommunityAlgorithm.LOUVAIN: cls(
                algorithm=CommunityAlgorithm.LOUVAIN,
                resolution=1.0,
                max_iterations=100,
                tolerance=1e-6,
                min_community_size=2,
                max_community_size=1000,
                random_seed=42,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            ),
            CommunityAlgorithm.LEIDEN: cls(
                algorithm=CommunityAlgorithm.LEIDEN,
                resolution=1.0,
                max_iterations=100,
                tolerance=1e-6,
                min_community_size=2,
                max_community_size=1000,
                random_seed=42,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            ),
            CommunityAlgorithm.LABEL_PROPAGATION: cls(
                algorithm=CommunityAlgorithm.LABEL_PROPAGATION,
                resolution=1.0,
                max_iterations=100,
                tolerance=1e-6,
                min_community_size=1,
                max_community_size=1000,
                random_seed=42,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            ),
            CommunityAlgorithm.GREEDY_MODULARITY: cls(
                algorithm=CommunityAlgorithm.GREEDY_MODULARITY,
                resolution=1.0,
                max_iterations=100,
                tolerance=1e-6,
                min_community_size=2,
                max_community_size=1000,
                random_seed=None,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            ),
            CommunityAlgorithm.FLUID_COMMUNITIES: cls(
                algorithm=CommunityAlgorithm.FLUID_COMMUNITIES,
                resolution=1.0,
                max_iterations=100,
                tolerance=1e-6,
                min_community_size=2,
                max_community_size=1000,
                random_seed=42,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            ),
            CommunityAlgorithm.GIRVAN_NEWMAN: cls(
                algorithm=CommunityAlgorithm.GIRVAN_NEWMAN,
                resolution=1.0,
                max_iterations=10,  # Much more expensive algorithm
                tolerance=1e-6,
                min_community_size=2,
                max_community_size=1000,
                random_seed=None,
                directed=False,
                weighted=False,
                weight_attribute="weight"
            )
        }


@dataclass
class CommunityDetails:
    """Detailed information about a single community"""
    community_id: int
    nodes: List[str]
    size: int
    internal_edges: int
    external_edges: int
    density: float
    conductance: float
    modularity_contribution: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "community_id": self.community_id,
            "nodes": self.nodes,
            "size": self.size,
            "internal_edges": self.internal_edges,
            "external_edges": self.external_edges,
            "density": self.density,
            "conductance": self.conductance,
            "modularity_contribution": self.modularity_contribution
        }