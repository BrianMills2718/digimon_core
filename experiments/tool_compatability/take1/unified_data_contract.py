"""
Unified Data Contract for KGAS Tools

This defines the SINGLE data format that ALL tools must use.
No more "entities" vs "mentions" confusion.
No more adapters needed.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DataCategory(Enum):
    """Categories of data that tools work with"""
    TEXT = "text"  # Raw text data
    ENTITIES = "entities"  # Extracted entities
    RELATIONSHIPS = "relationships"  # Relationships between entities
    GRAPH = "graph"  # Graph structure (nodes + edges)
    TABLE = "table"  # Tabular data
    VECTOR = "vector"  # Vector embeddings
    METRICS = "metrics"  # Calculated metrics/scores


@dataclass
class Entity:
    """Standard entity format - EVERYONE uses this"""
    id: str  # Unique identifier
    text: str  # The actual text/name (NOT "surface_form" or "name")
    type: str  # PERSON, ORG, GPE, etc.
    confidence: float  # 0.0 to 1.0
    source_ref: str  # Where this came from
    start_pos: Optional[int] = None  # Position in source text
    end_pos: Optional[int] = None  # End position in source text
    attributes: Dict[str, Any] = field(default_factory=dict)  # Additional properties
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "confidence": self.confidence,
            "source_ref": self.source_ref,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            text=data["text"],
            type=data["type"],
            confidence=data["confidence"],
            source_ref=data["source_ref"],
            start_pos=data.get("start_pos"),
            end_pos=data.get("end_pos"),
            attributes=data.get("attributes", {})
        )


@dataclass
class Relationship:
    """Standard relationship format - EVERYONE uses this"""
    id: str  # Unique identifier
    source_id: str  # ID of source entity
    target_id: str  # ID of target entity
    type: str  # Relationship type (WORKS_FOR, LOCATED_IN, etc.)
    confidence: float  # 0.0 to 1.0
    source_ref: str  # Where this came from
    evidence: Optional[str] = None  # Text evidence for the relationship
    attributes: Dict[str, Any] = field(default_factory=dict)  # Additional properties
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "confidence": self.confidence,
            "source_ref": self.source_ref,
            "evidence": self.evidence,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=data["type"],
            confidence=data["confidence"],
            source_ref=data["source_ref"],
            evidence=data.get("evidence"),
            attributes=data.get("attributes", {})
        )


@dataclass
class UnifiedData:
    """
    The SINGLE data structure that flows between ALL tools.
    Tools read what they need and add what they produce.
    """
    
    # Core data types - consistent naming!
    text: Optional[str] = None  # Raw text (NEVER "content" or "data")
    entities: List[Entity] = field(default_factory=list)  # NEVER "mentions"
    relationships: List[Relationship] = field(default_factory=list)  # NEVER "edges"
    
    # Structured data
    table_data: Optional[Dict[str, Any]] = None  # Tabular representation
    vector_data: Optional[Dict[str, List[float]]] = None  # Vector embeddings
    graph_data: Optional[Dict[str, Any]] = None  # Graph structure
    metrics: Dict[str, Any] = field(default_factory=dict)  # Calculated metrics
    
    # Metadata
    source_file: Optional[str] = None  # Original source
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_history: List[str] = field(default_factory=list)  # Tools that processed this
    
    def add_entity(self, entity: Entity):
        """Add an entity to the data"""
        self.entities.append(entity)
    
    def add_relationship(self, relationship: Relationship):
        """Add a relationship to the data"""
        self.relationships.append(relationship)
    
    def add_processing_step(self, tool_id: str):
        """Track which tools have processed this data"""
        self.processing_history.append(f"{tool_id}@{datetime.now().isoformat()}")
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        return [e for e in self.entities if e.type == entity_type]
    
    def get_relationships_by_type(self, rel_type: str) -> List[Relationship]:
        """Get all relationships of a specific type"""
        return [r for r in self.relationships if r.type == rel_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships],
            "table_data": self.table_data,
            "vector_data": self.vector_data,
            "graph_data": self.graph_data,
            "metrics": self.metrics,
            "source_file": self.source_file,
            "timestamp": self.timestamp,
            "processing_history": self.processing_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedData':
        """Create from dictionary"""
        unified = cls(
            text=data.get("text"),
            table_data=data.get("table_data"),
            vector_data=data.get("vector_data"),
            graph_data=data.get("graph_data"),
            metrics=data.get("metrics", {}),
            source_file=data.get("source_file"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            processing_history=data.get("processing_history", [])
        )
        
        # Reconstruct entities
        for entity_dict in data.get("entities", []):
            unified.entities.append(Entity.from_dict(entity_dict))
        
        # Reconstruct relationships
        for rel_dict in data.get("relationships", []):
            unified.relationships.append(Relationship.from_dict(rel_dict))
        
        return unified


class ToolCategory(Enum):
    """Categories that define what tools do"""
    LOADER = "loader"  # Load data from files
    EXTRACTOR = "extractor"  # Extract entities/relationships
    BUILDER = "builder"  # Build graph structures
    ANALYZER = "analyzer"  # Analyze and compute metrics
    CONVERTER = "converter"  # Convert between formats


# Compatibility rules - which categories can feed into which
CATEGORY_COMPATIBILITY = {
    ToolCategory.LOADER: [ToolCategory.EXTRACTOR, ToolCategory.CONVERTER],
    ToolCategory.EXTRACTOR: [ToolCategory.BUILDER, ToolCategory.ANALYZER, ToolCategory.CONVERTER],
    ToolCategory.BUILDER: [ToolCategory.ANALYZER, ToolCategory.CONVERTER],
    ToolCategory.ANALYZER: [ToolCategory.CONVERTER],
    ToolCategory.CONVERTER: [ToolCategory.EXTRACTOR, ToolCategory.BUILDER, ToolCategory.ANALYZER]
}


def can_chain_categories(source_category: ToolCategory, target_category: ToolCategory) -> bool:
    """Check if one tool category can feed into another"""
    compatible_targets = CATEGORY_COMPATIBILITY.get(source_category, [])
    return target_category in compatible_targets