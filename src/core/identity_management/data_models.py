"""
Identity Management Data Models

Core data structures for entity mentions, entities, and relationships.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Mention:
    """A surface form occurrence in text."""
    id: str
    surface_form: str  # Exact text as it appears
    normalized_form: str  # Cleaned/normalized version
    start_pos: int
    end_pos: int
    source_ref: str  # Reference to source document/chunk
    confidence: float = 0.8
    entity_type: Optional[str] = None
    context: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_pii_redacted: bool = False  # Added for PII redacting

    def to_dict(self) -> Dict[str, Any]:
        """Convert mention to dictionary format"""
        return {
            "mention_id": self.id,
            "surface_form": self.surface_form,
            "normalized_form": self.normalized_form,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "source_ref": self.source_ref,
            "confidence": self.confidence,
            "entity_type": self.entity_type,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "is_pii_redacted": self.is_pii_redacted
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Mention":
        """Create mention from dictionary data"""
        return cls(
            id=data["mention_id"],
            surface_form=data["surface_form"],
            normalized_form=data["normalized_form"],
            start_pos=data["start_pos"],
            end_pos=data["end_pos"],
            source_ref=data["source_ref"],
            confidence=data.get("confidence", 0.8),
            entity_type=data.get("entity_type"),
            context=data.get("context", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            is_pii_redacted=data.get("is_pii_redacted", False)
        )


@dataclass  
class Entity:
    """A canonical entity with one or more mentions."""
    id: str
    canonical_name: str  # Primary identifier
    entity_type: Optional[str] = None
    mentions: List[str] = field(default_factory=list)  # Mention IDs
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # For semantic similarity

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary format"""
        return {
            "entity_id": self.id,
            "canonical_name": self.canonical_name,
            "entity_type": self.entity_type,
            "mentions": self.mentions.copy(),
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata.copy(),
            "attributes": self.attributes.copy(),
            "embedding": self.embedding.copy() if self.embedding else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        """Create entity from dictionary data"""
        return cls(
            id=data["entity_id"],
            canonical_name=data["canonical_name"],
            entity_type=data.get("entity_type"),
            mentions=data.get("mentions", []).copy(),
            confidence=data.get("confidence", 0.8),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            metadata=data.get("metadata", {}).copy(),
            attributes=data.get("attributes", {}).copy(),
            embedding=data.get("embedding", []).copy() if data.get("embedding") else None
        )

    def add_mention(self, mention_id: str) -> None:
        """Add mention to entity"""
        if mention_id not in self.mentions:
            self.mentions.append(mention_id)

    def remove_mention(self, mention_id: str) -> bool:
        """Remove mention from entity"""
        if mention_id in self.mentions:
            self.mentions.remove(mention_id)
            return True
        return False

    def get_mention_count(self) -> int:
        """Get number of mentions for this entity"""
        return len(self.mentions)

    def update_confidence(self, new_confidence: float) -> None:
        """Update entity confidence using weighted average with existing mentions"""
        mention_count = self.get_mention_count()
        if mention_count > 1:
            self.confidence = (self.confidence * (mention_count - 1) + new_confidence) / mention_count
        else:
            self.confidence = new_confidence


@dataclass
class Relationship:
    """A relationship between two entities."""
    id: str
    source_id: str  # Source entity ID
    target_id: str  # Target entity ID
    relationship_type: str
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary format"""
        return {
            "relationship_id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "attributes": self.attributes.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """Create relationship from dictionary data"""
        return cls(
            id=data["relationship_id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=data["relationship_type"],
            confidence=data.get("confidence", 0.8),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            attributes=data.get("attributes", {}).copy()
        )

    def reverse(self) -> "Relationship":
        """Create reverse relationship"""
        return Relationship(
            id=f"rev_{self.id}",
            source_id=self.target_id,
            target_id=self.source_id,
            relationship_type=f"reverse_{self.relationship_type}",
            confidence=self.confidence,
            created_at=self.created_at,
            attributes=self.attributes.copy()
        )


@dataclass
class IdentityStats:
    """Statistics for identity management system"""
    total_mentions: int = 0
    total_entities: int = 0
    unique_surface_forms: int = 0
    avg_mentions_per_entity: float = 0.0
    entities_with_embeddings: int = 0
    embedding_coverage: float = 0.0
    persistence_enabled: bool = False
    database_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary format"""
        return {
            "total_mentions": self.total_mentions,
            "total_entities": self.total_entities,
            "unique_surface_forms": self.unique_surface_forms,
            "avg_mentions_per_entity": self.avg_mentions_per_entity,
            "entities_with_embeddings": self.entities_with_embeddings,
            "embedding_coverage": self.embedding_coverage,
            "persistence_enabled": self.persistence_enabled,
            "database_path": self.database_path
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IdentityStats":
        """Create stats from dictionary data"""
        return cls(
            total_mentions=data.get("total_mentions", 0),
            total_entities=data.get("total_entities", 0),
            unique_surface_forms=data.get("unique_surface_forms", 0),
            avg_mentions_per_entity=data.get("avg_mentions_per_entity", 0.0),
            entities_with_embeddings=data.get("entities_with_embeddings", 0),
            embedding_coverage=data.get("embedding_coverage", 0.0),
            persistence_enabled=data.get("persistence_enabled", False),
            database_path=data.get("database_path")
        )


# Type aliases for better code readability
MentionId = str
EntityId = str
RelationshipId = str
SurfaceForm = str
NormalizedForm = str
EmbeddingVector = List[float]