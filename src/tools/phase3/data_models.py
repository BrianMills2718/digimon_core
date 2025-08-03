"""
T301 Multi-Document Fusion - Data Models
Shared data models for fusion components.

This module contains all the data classes and result structures
used by the decomposed fusion modules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


class EntityConflictResolutionError(Exception):
    """Exception raised when LLM conflict resolution fails."""
    pass


class TemporalConsistencyError(Exception):
    """Exception raised when temporal consistency calculation fails."""
    pass


class AccuracyMeasurementError(Exception):
    """Exception raised when accuracy measurement fails."""
    pass


@dataclass
class FusionResult:
    """Result from multi-document fusion process"""
    total_documents: int = 0
    entities_before_fusion: int = 0
    entities_after_fusion: int = 0
    relationships_before_fusion: int = 0
    relationships_after_fusion: int = 0
    conflicts_resolved: int = 0
    fusion_time_seconds: float = 0.0
    consistency_score: float = 0.0
    evidence_chains: List[Dict[str, Any]] = field(default_factory=list)
    duplicate_clusters: List[List[str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "total_documents": self.total_documents,
            "entities_before_fusion": self.entities_before_fusion,
            "entities_after_fusion": self.entities_after_fusion,
            "relationships_before_fusion": self.relationships_before_fusion,
            "relationships_after_fusion": self.relationships_after_fusion,
            "conflicts_resolved": self.conflicts_resolved,
            "fusion_time_seconds": self.fusion_time_seconds,
            "consistency_score": self.consistency_score,
            "evidence_chains": self.evidence_chains,
            "duplicate_clusters": self.duplicate_clusters,
            "warnings": self.warnings
        }


@dataclass
class ConsistencyMetrics:
    """Metrics for knowledge consistency assessment"""
    entity_consistency: float = 0.0
    relationship_consistency: float = 0.0
    temporal_consistency: float = 0.0
    ontological_compliance: float = 0.0
    overall_score: float = 0.0
    inconsistencies: List[Dict[str, Any]] = field(default_factory=list)

    def calculate_overall_score(self) -> float:
        """Calculate overall consistency score from components"""
        scores = [
            self.entity_consistency,
            self.relationship_consistency,
            self.temporal_consistency,
            self.ontological_compliance
        ]
        self.overall_score = sum(scores) / len(scores) if scores else 0.0
        return self.overall_score


@dataclass
class EntityCluster:
    """Cluster of similar entities"""
    cluster_id: str = "default_cluster"
    entities: List[Dict[str, Any]] = field(default_factory=list)
    canonical_entity: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)

    def add_entity(self, entity: Dict[str, Any]) -> None:
        """Add entity to cluster"""
        self.entities.append(entity)
        
    def get_entity_count(self) -> int:
        """Get number of entities in cluster"""
        return len(self.entities)