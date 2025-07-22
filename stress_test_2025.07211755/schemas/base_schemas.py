"""
Base Pydantic schemas for data type architecture
Implements universal data types that all tools can produce/consume
"""

from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class QualityTier(str, Enum):
    """Quality assessment tiers"""
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    COPPER = "copper"

class ObjectType(str, Enum):
    """Core object types in the system"""
    DOCUMENT = "document"
    CHUNK = "chunk"
    MENTION = "mention"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"

class BaseObject(BaseModel):
    """Foundation class for all data objects in the system"""
    
    # Identity
    id: str = Field(..., description="Unique identifier")
    object_type: ObjectType = Field(..., description="Type of object")
    
    # Quality (REQUIRED for all objects)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    quality_tier: QualityTier = Field(..., description="Quality assessment tier")
    
    # Provenance (REQUIRED)
    created_by: str = Field(..., description="Tool that created this object")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    workflow_id: str = Field(..., description="Workflow identifier")
    
    # Version
    version: int = Field(default=1, description="Object version number")
    
    # Optional but common
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    source_refs: List[str] = Field(default_factory=list, description="Source references")

class TextChunk(BaseObject):
    """Text chunk data structure"""
    
    text: str = Field(..., description="Raw text content")
    document_ref: str = Field(..., description="Source document reference")
    chunk_index: int = Field(..., ge=0, description="Position in document")
    start_position: int = Field(..., ge=0, description="Character start position")
    end_position: int = Field(..., ge=0, description="Character end position")
    overlap_chars: int = Field(default=0, ge=0, description="Overlap with adjacent chunks")
    
    # Chunk metadata
    word_count: int = Field(..., ge=0, description="Number of words")
    sentence_count: int = Field(..., ge=0, description="Number of sentences")
    
    @validator('end_position')
    def end_after_start(cls, v, values):
        if 'start_position' in values and v <= values['start_position']:
            raise ValueError('end_position must be greater than start_position')
        return v

class EntityMention(BaseObject):
    """Entity mention in text - Level 2 of three-level identity"""
    
    surface_text: str = Field(..., description="Exact text as it appears")
    document_ref: str = Field(..., description="Source document reference")
    chunk_ref: str = Field(..., description="Source chunk reference")
    position: int = Field(..., ge=0, description="Character position in text")
    length: int = Field(..., gt=0, description="Length of mention in characters")
    context_window: str = Field(..., description="Surrounding text context")
    
    # Entity resolution
    entity_candidates: List[tuple[str, float]] = Field(
        default_factory=list, 
        description="Possible entities with confidence scores"
    )
    selected_entity: Optional[str] = Field(None, description="Resolved entity ID")
    
    # Type classification
    entity_type: Optional[str] = Field(None, description="Classified entity type")
    type_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Type classification confidence")

class StandardEntity(BaseObject):
    """Canonical entity - Level 3 of three-level identity"""
    
    canonical_name: str = Field(..., description="Canonical entity name")
    entity_type: str = Field(..., description="Entity type classification")
    
    # Identity tracking
    surface_forms: List[str] = Field(default_factory=list, description="All known surface forms")
    mention_refs: List[str] = Field(default_factory=list, description="References to entity mentions")
    
    # Flexible properties for domain-specific attributes
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Entity attributes")
    
    # Quality indicators
    mention_count: int = Field(default=0, ge=0, description="Number of mentions found")
    consistency_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Cross-mention consistency")

class StandardRelationship(BaseObject):
    """Relationship between entities"""
    
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(..., description="Type of relationship")
    
    # Relationship properties
    weight: float = Field(default=1.0, ge=0.0, description="Relationship strength")
    direction: Literal["directed", "undirected"] = Field(default="directed", description="Relationship direction")
    
    # Evidence tracking
    mention_refs: List[str] = Field(default_factory=list, description="Supporting mentions")
    
    # ORM role names for semantic clarity
    source_role_name: Optional[str] = Field(None, description="Role of source entity")
    target_role_name: Optional[str] = Field(None, description="Role of target entity")
    
    # Additional participants for n-ary relations
    additional_participants: Dict[str, str] = Field(
        default_factory=dict, 
        description="Additional participants {role: entity_id}"
    )

class Document(BaseObject):
    """Document data structure"""
    
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full document content")
    file_path: Optional[str] = Field(None, description="Original file path")
    file_type: str = Field(default="text", description="Document type")
    
    # Document metadata
    author: Optional[str] = Field(None, description="Document author")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    word_count: int = Field(..., ge=0, description="Total word count")
    
    # Processing metadata
    extraction_method: str = Field(..., description="How content was extracted")
    preprocessing_applied: List[str] = Field(default_factory=list, description="Preprocessing steps")

class WorkflowState(BaseObject):
    """Workflow execution state"""
    
    workflow_name: str = Field(..., description="Name of the workflow")
    current_step: str = Field(..., description="Current step identifier")
    total_steps: int = Field(..., gt=0, description="Total number of steps")
    completed_steps: int = Field(..., ge=0, description="Number of completed steps")
    
    # State data
    state_data: Dict[str, Any] = Field(default_factory=dict, description="Workflow state data")
    checkpoint_data: Optional[Dict[str, Any]] = Field(None, description="Checkpoint data for recovery")
    
    # Status
    status: Literal["running", "completed", "failed", "paused"] = Field(..., description="Workflow status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    @validator('completed_steps')
    def completed_not_exceed_total(cls, v, values):
        if 'total_steps' in values and v > values['total_steps']:
            raise ValueError('completed_steps cannot exceed total_steps')
        return v

class ValidationResult(BaseModel):
    """Result of validation operations"""
    
    valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional validation metadata")
    
    # Performance metrics
    validation_time: Optional[float] = Field(None, ge=0.0, description="Validation time in seconds")
    objects_validated: Optional[int] = Field(None, ge=0, description="Number of objects validated")

# Schema registry for automatic validation
SCHEMA_REGISTRY = {
    "BaseObject": BaseObject,
    "TextChunk": TextChunk, 
    "EntityMention": EntityMention,
    "StandardEntity": StandardEntity,
    "StandardRelationship": StandardRelationship,
    "Document": Document,
    "WorkflowState": WorkflowState,
    "ValidationResult": ValidationResult
}

def get_schema(schema_name: str) -> BaseModel:
    """Get schema class by name"""
    if schema_name not in SCHEMA_REGISTRY:
        raise ValueError(f"Unknown schema: {schema_name}")
    return SCHEMA_REGISTRY[schema_name]

def validate_data_against_schema(data: Dict[str, Any], schema_name: str) -> ValidationResult:
    """Validate data against a named schema"""
    try:
        schema_class = get_schema(schema_name)
        validated_object = schema_class(**data)
        return ValidationResult(
            valid=True,
            metadata={"schema": schema_name, "object_id": getattr(validated_object, 'id', None)}
        )
    except Exception as e:
        return ValidationResult(
            valid=False,
            errors=[str(e)],
            metadata={"schema": schema_name, "attempted_data": data}
        )