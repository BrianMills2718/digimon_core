"""Core Data Models - Structured Data Types for Tool Compatibility

Defines standardized Pydantic data models that serve as contracts between tools.
All tools must produce and consume data in these standardized formats to ensure 
compatibility across the 121-tool ecosystem.

Based on COMPATIBILITY_MATRIX.md specifications and extends api_contracts.py
"""

from pydantic import BaseModel, Field, field_validator
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
    size_bytes: Optional[int] = Field(description="Size of the document in bytes")
    content_hash: Optional[str] = Field(description="Hash of content for deduplication")
    
    # Document metadata
    title: Optional[str] = Field(description="Document title")
    author: Optional[str] = Field(description="Document author")
    publication_date: Optional[datetime] = Field(description="Publication date")
    document_type: Optional[str] = Field(description="Type of document (PDF, DOCX, etc.)")
    language: Optional[str] = Field(description="Document language")
    
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
    content_hash: Optional[str] = Field(description="Hash of chunk content")
    
    # Document relationship  
    document_ref: str = Field(description="Reference to the parent Document ID")
    position: int = Field(description="Start position of the chunk within the document")
    end_position: Optional[int] = Field(description="End position of the chunk")
    chunk_index: Optional[int] = Field(description="Sequential index of chunk in document")
    
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
    embedding_ref: Optional[str] = Field(description="Reference to embedding for this chunk")
    
    # Chunk-specific metadata
    sentence_count: Optional[int] = Field(description="Number of sentences in chunk")
    token_count: Optional[int] = Field(description="Number of tokens in chunk")


# --- Entity and Mention Types (Three-Level Identity) ---
class Mention(BaseObject):
    """
    Represents a specific textual mention of an entity or concept.
    Level 2 of three-level identity system
    """
    object_type: Literal[ObjectType.MENTION] = Field(default=ObjectType.MENTION)
    
    # Text details
    surface_text: str = Field(description="The exact text span of the mention")
    normalized_text: Optional[str] = Field(description="Normalized form of the mention")
    
    # Location
    document_ref: str = Field(description="Reference to the source document ID")
    chunk_ref: Optional[str] = Field(description="Reference to the source chunk ID")
    position: int = Field(description="Character start position in the document/chunk")
    end_position: Optional[int] = Field(description="Character end position")
    sentence_index: Optional[int] = Field(description="Sentence number within chunk")
    
    # Context
    context_window: str = Field(description="Surrounding text providing context")
    context_size: int = Field(default=100, description="Size of context window in characters")
    
    # Entity resolution
    entity_candidates: List[Tuple[str, float]] = Field(
        default_factory=list,
        description="List of possible entity IDs and their confidence scores"
    )
    selected_entity: Optional[str] = Field(description="Resolved entity ID for this mention")
    entity_type: Optional[str] = Field(description="Type of the mentioned entity")
    
    # Processing metadata
    extraction_method: Optional[str] = Field(description="Method used to extract mention (spaCy, LLM, etc.)")
    is_resolved: bool = Field(default=False, description="Whether mention has been linked to entity")


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
    mention_refs: List[str] = Field(
        default_factory=list,
        description="References to associated Mention IDs"
    )
    
    # Attributes
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible key-value attributes for the entity"
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured properties with types and values"
    )
    
    # Relationships
    relationship_refs: List[str] = Field(
        default_factory=list,
        description="References to relationships involving this entity"
    )
    
    # Resolution metadata
    is_canonical: bool = Field(default=True, description="Whether this is the canonical entity")
    merged_from: List[str] = Field(
        default_factory=list,
        description="Entity IDs that were merged into this one"
    )
    disambiguation_score: Optional[float] = Field(default=None, description="Score for entity disambiguation")
    
    # External references
    external_ids: Dict[str, str] = Field(
        default_factory=dict,
        description="External database IDs (Wikidata, DBpedia, etc.)"
    )
    dolce_parent: Optional[str] = Field(None, description="IRI of DOLCE parent class")


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
    direction: str = Field(default="directed", description="'directed' or 'undirected'")
    is_temporal: bool = Field(default=False, description="Whether relationship has time dimension")
    temporal_info: Optional[Dict[str, Any]] = Field(description="Temporal information if applicable")
    
    # Evidence
    mention_refs: List[str] = Field(
        default_factory=list,
        description="References to supporting Mention IDs"
    )
    evidence_text: List[str] = Field(
        default_factory=list,
        description="Text snippets supporting this relationship"
    )
    
    # Extraction metadata
    extraction_method: Optional[str] = Field(description="Method used to extract relationship")
    extraction_rule: Optional[str] = Field(description="Specific rule or pattern used")
    
    # Validation
    is_validated: bool = Field(default=False, description="Whether relationship has been validated")
    validation_score: Optional[float] = Field(description="Validation confidence score")


# --- Graph and Table Types ---
class Graph(BaseObject):
    """
    Represents a knowledge graph structure.
    Output of graph construction tools (T31-T48)
    """
    object_type: Literal[ObjectType.GRAPH] = Field(default=ObjectType.GRAPH)
    
    # Graph structure
    entity_refs: List[str] = Field(description="References to entities in the graph")
    relationship_refs: List[str] = Field(description="References to relationships in the graph")
    
    # Graph metadata
    graph_type: str = Field(description="Type of graph (knowledge, semantic, etc.)")
    is_directed: bool = Field(default=True, description="Whether graph is directed")
    
    # Statistics
    entity_count: int = Field(description="Number of entities in graph")
    relationship_count: int = Field(description="Number of relationships in graph")
    density: Optional[float] = Field(description="Graph density metric")
    
    # Construction metadata
    construction_method: Optional[str] = Field(description="Method used to build graph")
    source_documents: List[str] = Field(
        default_factory=list,
        description="Documents used to construct this graph"
    )
    
    # Analysis results
    centrality_scores: Optional[Dict[str, float]] = Field(description="Centrality scores for entities")
    communities: Optional[List[List[str]]] = Field(description="Detected communities")
    clusters: Optional[Dict[str, List[str]]] = Field(description="Entity clusters")


class Table(BaseObject):
    """
    Represents structured tabular data.
    Output of table extraction and analysis tools
    """
    object_type: Literal[ObjectType.TABLE] = Field(default=ObjectType.TABLE)
    
    # Table structure
    headers: List[str] = Field(description="Column headers")
    rows: List[List[Any]] = Field(description="Table rows as lists of values")
    column_types: Optional[Dict[str, str]] = Field(description="Data types for each column")
    
    # Table metadata
    table_type: str = Field(description="Type of table (extracted, generated, etc.)")
    row_count: int = Field(description="Number of rows")
    column_count: int = Field(description="Number of columns")
    
    # Source information
    source_type: Optional[str] = Field(description="Source of table data")
    extraction_method: Optional[str] = Field(description="Method used to extract/generate table")
    
    # Data quality
    completeness_score: Optional[float] = Field(description="Data completeness score")
    data_quality_issues: List[str] = Field(
        default_factory=list,
        description="Identified data quality issues"
    )


# --- Processing State Types ---
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
    
    # Progress tracking
    completed_steps: List[str] = Field(
        default_factory=list,
        description="List of completed steps"
    )
    failed_steps: List[str] = Field(
        default_factory=list,
        description="List of failed steps"
    )
    progress_percentage: float = Field(description="Overall progress percentage")
    
    # State flags (as required by COMPATIBILITY_MATRIX.md)
    document_loaded: bool = Field(default=False)
    chunks_created: bool = Field(default=False)
    mentions_extracted: bool = Field(default=False)
    entities_resolved: bool = Field(default=False)
    relationships_extracted: bool = Field(default=False)
    graph_constructed: bool = Field(default=False)
    embeddings_generated: bool = Field(default=False)
    
    # Execution metadata
    start_time: datetime = Field(description="Workflow start time")
    end_time: Optional[datetime] = Field(description="Workflow end time")
    execution_time: Optional[float] = Field(description="Total execution time in seconds")
    
    # Error tracking
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of errors encountered"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings"
    )


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


class EmbeddingVector(BaseObject):
    """
    Represents a vector embedding.
    Output of embedding tools (T41, etc.)
    """
    object_type: Literal[ObjectType.EMBEDDING] = Field(default=ObjectType.EMBEDDING)
    
    # Vector data
    vector: List[float] = Field(description="The embedding vector")
    dimension: int = Field(description="Dimension of the vector")
    
    # Source information
    source_ref: str = Field(description="Reference to source object (chunk, entity, etc.)")
    source_type: str = Field(description="Type of source object")
    
    # Embedding metadata
    model_name: str = Field(description="Name of the embedding model used")
    model_version: Optional[str] = Field(description="Version of the embedding model")
    embedding_method: Optional[str] = Field(description="Method used for embedding")
    
    # Normalization
    is_normalized: bool = Field(default=False, description="Whether vector is normalized")
    norm: Optional[float] = Field(description="Vector norm if calculated")


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


def validate_reference_chain(refs: List[str]) -> List[str]:
    """Validate a list of references and return any errors"""
    errors = []
    for ref in refs:
        try:
            parse_reference(ref)
        except ValueError as e:
            errors.append(str(e))
    return errors


class DataModelsManager:
    """Wrapper class to make data_models discoverable by audit system"""
    
    def __init__(self):
        self.tool_id = "DATA_MODELS"
        self._models = {
            "Document": Document,
            "Chunk": Chunk,
            "Mention": Mention,
            "Entity": Entity,
            "Relationship": Relationship,
            "Graph": Graph,
            "Table": Table,
            "WorkflowState": WorkflowState,
            "TextForLLMProcessing": TextForLLMProcessing,
            "EmbeddingVector": EmbeddingVector
        }
    
    def get_tool_info(self):
        """Return tool information for audit system"""
        return {
            "tool_id": self.tool_id,
            "tool_type": "DATA_MODELS",
            "status": "functional",
            "description": "Pydantic data models for system compatibility",
            "models_available": list(self._models.keys()),
            "total_models": len(self._models)
        }
    
    def create_sample_instances(self):
        """Create sample instances of all models for testing"""
        try:
            instances = {}
            
            # Document
            instances["Document"] = Document(
                object_type=ObjectType.DOCUMENT,
                text_content="Sample document content",
                file_path="/path/to/sample.pdf"
            )
            
            # Chunk  
            instances["Chunk"] = Chunk(
                object_type=ObjectType.CHUNK,
                text_content="Sample chunk content",
                parent_document_id="doc-123",
                start_position=0,
                end_position=100
            )
            
            # Entity
            instances["Entity"] = Entity(
                object_type=ObjectType.ENTITY,
                canonical_name="Sample Entity",
                entity_type="ORG"
            )
            
            return {
                "status": "success",
                "instances_created": len(instances),
                "sample_instances": instances
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def get_model_schemas(self):
        """Get JSON schemas for all models"""
        schemas = {}
        for name, model_class in self._models.items():
            try:
                schemas[name] = model_class.model_json_schema()
            except Exception as e:
                schemas[name] = {"error": str(e)}
        
        return schemas