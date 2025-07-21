"""Core Data Models - Structured Data Types for Tool Compatibility

Defines standardized Pydantic data models that serve as contracts between tools.
All tools must produce and consume data in these standardized formats to ensure 
compatibility across the 121-tool ecosystem.

Based on COMPATIBILITY_MATRIX.md specifications
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional, Tuple, Union, Literal
from datetime import datetime
from enum import Enum
import uuid


class QualityTier(Enum):
    """Quality tiers for data objects"""
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"


class ObjectType(Enum):
    """Standard object types in the system"""
    DOCUMENT = "Document"
    CHUNK = "Chunk"
    MENTION = "Mention"
    ENTITY = "Entity"
    RELATIONSHIP = "Relationship"
    GRAPH = "Graph"
    TABLE = "Table"
    EMBEDDING = "Embedding"
    WORKFLOW_STATE = "WorkflowState"


# --- BaseObject (Foundation for all types) ---
class BaseObject(BaseModel):
    """
    Foundation for all data objects in the system.
    Provides identity, quality, and provenance tracking as required by COMPATIBILITY_MATRIX.md
    """
    # Identity (REQUIRED)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the object"
    )
    object_type: ObjectType = Field(description="Category of the object")

    # Quality (REQUIRED for all objects)
    confidence: float = Field(
        ge=0.0, le=1.0, 
        description="Confidence score (0.0 to 1.0)"
    )
    quality_tier: QualityTier = Field(
        description="Quality tier classification"
    )

    # Provenance (REQUIRED)
    created_by: str = Field(description="Tool or service that created this object")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of object creation"
    )
    workflow_id: str = Field(description="ID of the workflow that created this object")

    # Version (REQUIRED)
    version: int = Field(default=1, description="Version of this object")

    # Optional but common
    warnings: List[str] = Field(
        default_factory=list, 
        description="List of warnings associated with the object"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="References to evidence supporting this object"
    )
    source_refs: List[str] = Field(
        default_factory=list,
        description="List of source document references"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata specific to the object"
    )

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

    def to_reference(self) -> str:
        """Generate universal reference format as required by COMPATIBILITY_MATRIX.md"""
        return f"neo4j://{self.object_type.value.lower()}/{self.id}"


# --- Document Processing Types ---
class Document(BaseObject):
    """
    Represents a source document.
    Primary output of Ingestion phase (T01-T12)
    """
    object_type: Literal[ObjectType.DOCUMENT] = Field(default=ObjectType.DOCUMENT)
    
    # Content
    content: str = Field(description="Full text content of the document")
    original_filename: Optional[str] = Field(description="Original filename if applicable")
    size_bytes: Optional[int] = Field(default=None, description="Size of the document in bytes")
    content_hash: Optional[str] = Field(default=None, description="Hash of content for deduplication")
    
    # Document metadata
    title: Optional[str] = Field(default=None, description="Document title")
    author: Optional[str] = Field(default=None, description="Document author")
    publication_date: Optional[datetime] = Field(default=None, description="Publication date")
    document_type: Optional[str] = Field(default=None, description="Type of document (PDF, DOCX, etc.)")
    language: Optional[str] = Field(default=None, description="Document language")
    
    # Processing state
    is_processed: bool = Field(default=False, description="Whether document has been chunked")
    chunk_refs: List[str] = Field(
        default_factory=list,
        description="References to Chunk objects derived from this document"
    )


class Chunk(BaseObject):
    """
    Represents a textual chunk derived from a document.
    Primary output of text chunking tools (T15a, etc.)
    """
    object_type: Literal[ObjectType.CHUNK] = Field(default=ObjectType.CHUNK)
    
    # Content
    content: str = Field(description="Text content of the chunk")
    content_hash: Optional[str] = Field(default=None, description="Hash of chunk content")
    
    # Document relationship  
    document_ref: str = Field(description="Reference to the parent Document ID")
    position: int = Field(description="Start position of the chunk within the document")
    end_position: Optional[int] = Field(default=None, description="End position of the chunk")
    chunk_index: Optional[int] = Field(default=None, description="Sequential index of chunk in document")
    
    # Processing results
    entity_refs: List[str] = Field(
        default_factory=list,
        description="References to entities identified in this chunk"
    )
    relationship_refs: List[str] = Field(
        default_factory=list,
        description="References to relationships identified in this chunk"
    )
    mention_refs: List[str] = Field(
        default_factory=list,
        description="References to mentions within this chunk"
    )
    embedding_ref: Optional[str] = Field(default=None, description="Reference to embedding for this chunk")
    
    # Chunk-specific metadata
    sentence_count: Optional[int] = Field(default=None, description="Number of sentences in chunk")
    token_count: Optional[int] = Field(default=None, description="Number of tokens in chunk")


class Entity(BaseObject):
    """
    Represents a canonical entity.
    Level 3 of three-level identity system
    """
    object_type: Literal[ObjectType.ENTITY] = Field(default=ObjectType.ENTITY)
    
    # Identity
    canonical_name: str = Field(description="Standardized name for the entity")
    entity_type: str = Field(description="Type: PERSON, ORG, GPE, EVENT, CONCEPT, etc.")
    
    # Variations
    surface_forms: List[str] = Field(
        default_factory=list,
        description="All known textual variations/aliases of the entity"
    )
    
    # Attributes
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible key-value attributes for the entity"
    )
    
    # Ontology validation fields
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Properties from master concept library"
    )
    modifiers: Dict[str, str] = Field(
        default_factory=dict,
        description="Modifiers from master concept library"
    )
    
    @model_validator(mode='after')
    def validate_against_ontology(self):
        """Validate entity type and properties against master concept library"""
        try:
            from src.ontology_library.ontology_service import OntologyService
            ontology = OntologyService()
            
            # Validate entity type
            if not ontology.validate_entity_type(self.entity_type):
                raise ValueError(f"Unknown entity type: {self.entity_type}. Valid types: {', '.join(ontology.registry.entities.keys())}")
            
            # Validate properties if present
            if self.properties:
                applicable_props = ontology.get_applicable_properties(self.entity_type, "Entity")
                for prop_name in self.properties:
                    if prop_name not in applicable_props:
                        raise ValueError(f"Property '{prop_name}' not applicable to entity type '{self.entity_type}'")
            
            # Validate modifiers if present
            if self.modifiers:
                applicable_mods = ontology.get_applicable_modifiers(self.entity_type, "Entity")
                for mod_name, mod_value in self.modifiers.items():
                    if mod_name not in applicable_mods:
                        raise ValueError(f"Modifier '{mod_name}' not applicable to entity type '{self.entity_type}'")
                    valid_values = ontology.get_modifier_values(mod_name)
                    if mod_value not in valid_values:
                        raise ValueError(f"Invalid value '{mod_value}' for modifier '{mod_name}'. Valid values: {valid_values}")
        except ImportError:
            # If ontology service not available, skip validation
            # This allows using data models without ontology in some contexts
            pass
        except Exception as e:
            # Re-raise validation errors
            if "Unknown entity type" in str(e) or "not applicable" in str(e) or "Invalid value" in str(e):
                raise
            # Log other errors but don't fail
            if self.warnings is not None:
                self.warnings.append(f"Ontology validation warning: {str(e)}")
        
        return self


class Relationship(BaseObject):
    """
    Represents a relationship between two entities.
    Output of relationship extraction tools (T27, etc.)
    """
    object_type: Literal[ObjectType.RELATIONSHIP] = Field(default=ObjectType.RELATIONSHIP)
    
    # Core relationship
    source_id: str = Field(description="ID of the source entity")
    target_id: str = Field(description="ID of the target entity")
    relationship_type: str = Field(
        description="Type of relationship (e.g., FOUNDED, LOCATED_IN, WORKS_FOR)"
    )
    
    # Relationship properties
    weight: float = Field(default=1.0, description="Numerical weight/strength of the relationship")
    
    # Ontology validation fields
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Properties from master concept library"
    )
    modifiers: Dict[str, str] = Field(
        default_factory=dict,
        description="Modifiers from master concept library"
    )
    
    @model_validator(mode='after')
    def validate_against_ontology(self):
        """Validate relationship type against master concept library"""
        try:
            from src.ontology_library.ontology_service import OntologyService
            ontology = OntologyService()
            
            # Validate relationship type
            if not ontology.validate_connection_type(self.relationship_type):
                raise ValueError(f"Unknown relationship type: {self.relationship_type}. Valid types: {', '.join(ontology.registry.connections.keys())}")
            
            # Validate properties if present
            if self.properties:
                applicable_props = ontology.get_applicable_properties(self.relationship_type, "Connection")
                for prop_name in self.properties:
                    if prop_name not in applicable_props:
                        raise ValueError(f"Property '{prop_name}' not applicable to relationship type '{self.relationship_type}'")
            
            # Validate modifiers if present
            if self.modifiers:
                applicable_mods = ontology.get_applicable_modifiers(self.relationship_type, "Connection")
                for mod_name, mod_value in self.modifiers.items():
                    if mod_name not in applicable_mods:
                        raise ValueError(f"Modifier '{mod_name}' not applicable to relationship type '{self.relationship_type}'")
                    valid_values = ontology.get_modifier_values(mod_name)
                    if mod_value not in valid_values:
                        raise ValueError(f"Invalid value '{mod_value}' for modifier '{mod_name}'. Valid values: {valid_values}")
        except ImportError:
            # If ontology service not available, skip validation
            # This allows using data models without ontology in some contexts
            pass
        except Exception as e:
            # Re-raise validation errors
            if "Unknown relationship type" in str(e) or "not applicable" in str(e) or "Invalid value" in str(e):
                raise
            # Log other errors but don't fail
            if self.warnings is not None:
                self.warnings.append(f"Ontology validation warning: {str(e)}")
        
        return self


class WorkflowState(BaseObject):
    """
    Represents the state of a workflow execution.
    Managed by WorkflowStateService (T121)
    """
    object_type: Literal[ObjectType.WORKFLOW_STATE] = Field(default=ObjectType.WORKFLOW_STATE)
    
    # Workflow identification
    workflow_name: str = Field(description="Name of the workflow")
    execution_id: str = Field(description="Unique execution identifier")
    
    # State tracking
    current_phase: str = Field(description="Current phase being executed")
    current_step: str = Field(description="Current step within phase")
    status: str = Field(description="Overall workflow status")
    
    # State flags (as required by COMPATIBILITY_MATRIX.md)
    document_loaded: bool = Field(default=False)
    chunks_created: bool = Field(default=False)
    mentions_extracted: bool = Field(default=False)
    entities_resolved: bool = Field(default=False)
    relationships_extracted: bool = Field(default=False)
    graph_constructed: bool = Field(default=False)


# --- Tool-Specific Data Types ---
class TextForLLMProcessing(BaseModel):
    """
    Specialized data type for LLM input processing.
    Used by adapters to transform chunks for LLM tools
    """
    text_content: str = Field(description="Text content for LLM processing")
    chunk_id: str = Field(description="ID of source chunk")
    context: Optional[str] = Field(description="Additional context for LLM")
    processing_instructions: Optional[str] = Field(description="Specific instructions for LLM")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Utility functions for data model operations
def create_reference(obj: BaseObject) -> str:
    """Create a standard reference for any BaseObject"""
    return obj.to_reference()


def parse_reference(ref: str) -> Tuple[str, str]:
    """Parse a reference string into object type and ID"""
    if not ref.startswith("neo4j://"):
        raise ValueError(f"Invalid reference format: {ref}")
    
    parts = ref.replace("neo4j://", "").split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid reference format: {ref}")
    
    return parts[0], parts[1]