"""Network Motifs Data Models

Data structures for network motifs detection.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Any


class MotifType(Enum):
    """Supported motif types for detection"""
    TRIANGLES = "triangles"
    SQUARES = "squares"
    WEDGES = "wedges"
    FEED_FORWARD_LOOPS = "feed_forward_loops"
    BI_FANS = "bi_fans"
    THREE_CHAINS = "three_chains"
    FOUR_CHAINS = "four_chains"
    CLIQUES = "cliques"
    ALL = "all"


@dataclass
class MotifInstance:
    """Individual motif instance"""
    motif_type: str
    nodes: List[str]
    edges: List[Tuple[str, str]]
    pattern_id: str
    significance_score: float
    frequency: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "motif_type": self.motif_type,
            "nodes": self.nodes,
            "edges": self.edges,
            "pattern_id": self.pattern_id,
            "significance_score": self.significance_score,
            "frequency": self.frequency
        }


@dataclass
class MotifStats:
    """Network motif statistics"""
    total_motifs: int
    motif_types: Dict[str, int]
    significance_scores: Dict[str, float]
    enrichment_ratios: Dict[str, float]
    z_scores: Dict[str, float]
    p_values: Dict[str, float]
    random_baseline: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "total_motifs": self.total_motifs,
            "motif_types": self.motif_types,
            "significance_scores": self.significance_scores,
            "enrichment_ratios": self.enrichment_ratios,
            "z_scores": self.z_scores,
            "p_values": self.p_values,
            "random_baseline": self.random_baseline
        }


@dataclass
class MotifDetectionConfig:
    """Configuration for motif detection"""
    motif_type: MotifType
    size: int
    pattern: str
    min_frequency: int
    max_instances: int
    directed: bool
    
    @classmethod
    def get_default_configs(cls) -> Dict[MotifType, 'MotifDetectionConfig']:
        """Get default configurations for all motif types"""
        return {
            MotifType.TRIANGLES: cls(
                motif_type=MotifType.TRIANGLES,
                size=3,
                pattern="complete",
                min_frequency=1,
                max_instances=10000,
                directed=True
            ),
            MotifType.SQUARES: cls(
                motif_type=MotifType.SQUARES,
                size=4,
                pattern="cycle",
                min_frequency=1,
                max_instances=5000,
                directed=False
            ),
            MotifType.WEDGES: cls(
                motif_type=MotifType.WEDGES,
                size=3,
                pattern="path",
                min_frequency=1,
                max_instances=20000,
                directed=False
            ),
            MotifType.FEED_FORWARD_LOOPS: cls(
                motif_type=MotifType.FEED_FORWARD_LOOPS,
                size=3,
                pattern="directed_triangle",
                min_frequency=1,
                max_instances=5000,
                directed=True
            ),
            MotifType.BI_FANS: cls(
                motif_type=MotifType.BI_FANS,
                size=4,
                pattern="bipartite",
                min_frequency=1,
                max_instances=3000,
                directed=False
            ),
            MotifType.THREE_CHAINS: cls(
                motif_type=MotifType.THREE_CHAINS,
                size=3,
                pattern="path",
                min_frequency=1,
                max_instances=15000,
                directed=True
            ),
            MotifType.FOUR_CHAINS: cls(
                motif_type=MotifType.FOUR_CHAINS,
                size=4,
                pattern="path",
                min_frequency=1,
                max_instances=10000,
                directed=True
            ),
            MotifType.CLIQUES: cls(
                motif_type=MotifType.CLIQUES,
                size=3,
                pattern="complete",
                min_frequency=1,
                max_instances=5000,
                directed=False
            )
        }