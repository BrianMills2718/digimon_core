# KGAS Core Data Schemas

**Version**: 1.0
**Status**: Target Architecture
**Last Updated**: 2025-07-22

## Overview

This document provides concrete Pydantic schema examples for all core KGAS data types. These schemas serve as the foundation for the contract-first tool architecture and ensure type safety throughout the system.

## Core Entity Schemas

### Entity Schema

```python
from pydantic import BaseModel, Field, constr, confloat
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    """Standard entity types following theory-aware categorization"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    CONCEPT = "CONCEPT"
    EVENT = "EVENT"
    THEORETICAL_CONSTRUCT = "THEORETICAL_CONSTRUCT"
    CUSTOM = "CUSTOM"

class Entity(BaseModel):
    """Core entity representation in KGAS"""
    entity_id: constr(regex=r'^entity_[a-f0-9\-]{36}$') = Field(
        ..., 
        description="Unique entity identifier in UUID format"
    )
    canonical_name: str = Field(
        ..., 
        min_length=1,
        description="Authoritative name for the entity"
    )
    entity_type: EntityType = Field(
        ...,
        description="Type categorization of the entity"
    )
    
    # Confidence and quality
    confidence: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="Overall confidence in entity extraction"
    )
    quality_tier: str = Field(
        default="medium",
        regex=r'^(high|medium|low)$',
        description="Quality assessment tier"
    )
    
    # Embeddings for similarity
    embedding: Optional[List[float]] = Field(
        None,
        min_items=384,
        max_items=384,
        description="384-dimensional embedding vector"
    )
    
    # Theory grounding
    theory_grounding: Optional[Dict[str, Any]] = Field(
        None,
        description="Theory-specific attributes and mappings"
    )
    
    # Temporal bounds
    temporal_start: Optional[datetime] = Field(
        None,
        description="Start of entity's temporal validity"
    )
    temporal_end: Optional[datetime] = Field(
        None,
        description="End of entity's temporal validity"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Entity creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    source_references: List[str] = Field(
        default_factory=list,
        description="Document/chunk IDs where entity appears"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "entity_123e4567-e89b-12d3-a456-426614174000",
                "canonical_name": "John Smith",
                "entity_type": "PERSON",
                "confidence": 0.92,
                "quality_tier": "high",
                "theory_grounding": {
                    "stakeholder_theory": {
                        "salience": 0.8,
                        "legitimacy": 0.7,
                        "urgency": 0.3
                    }
                }
            }
        }
```

### Mention Schema

```python
class Mention(BaseModel):
    """Entity mention in text"""
    mention_id: constr(regex=r'^mention_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Unique mention identifier"
    )
    entity_id: constr(regex=r'^entity_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Referenced entity ID"
    )
    chunk_id: constr(regex=r'^chunk_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Source chunk ID"
    )
    
    # Text details
    surface_form: str = Field(
        ...,
        min_length=1,
        description="Actual text of the mention"
    )
    context: str = Field(
        ...,
        description="Surrounding context text"
    )
    
    # Position information
    start_char: int = Field(
        ...,
        ge=0,
        description="Start character position in chunk"
    )
    end_char: int = Field(
        ...,
        gt=0,
        description="End character position in chunk"
    )
    
    # Extraction confidence
    confidence: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="Mention extraction confidence"
    )
    extraction_method: str = Field(
        ...,
        description="Method used for extraction (e.g., 'spacy_ner', 'pattern_match')"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    created_by: str = Field(
        ...,
        description="Tool ID that created this mention"
    )
```

## Relationship Schemas

### Relationship Schema

```python
class RelationshipType(str, Enum):
    """Standard relationship types"""
    RELATED_TO = "RELATED_TO"
    WORKS_FOR = "WORKS_FOR"
    LOCATED_IN = "LOCATED_IN"
    MEMBER_OF = "MEMBER_OF"
    INFLUENCES = "INFLUENCES"
    CAUSES = "CAUSES"
    THEORETICAL = "THEORETICAL"
    CUSTOM = "CUSTOM"

class Relationship(BaseModel):
    """Relationship between entities"""
    relationship_id: constr(regex=r'^rel_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Unique relationship identifier"
    )
    source_entity_id: constr(regex=r'^entity_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Source entity in the relationship"
    )
    target_entity_id: constr(regex=r'^entity_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Target entity in the relationship"
    )
    relationship_type: RelationshipType = Field(
        ...,
        description="Type of relationship"
    )
    
    # Relationship properties
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional relationship properties"
    )
    
    # Confidence and evidence
    confidence: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="Relationship confidence score"
    )
    evidence_count: int = Field(
        ...,
        ge=1,
        description="Number of evidence mentions"
    )
    evidence_mentions: List[str] = Field(
        default_factory=list,
        description="Mention IDs supporting this relationship"
    )
    
    # Theory grounding
    theory_grounding: Optional[Dict[str, Any]] = Field(
        None,
        description="Theory-specific relationship attributes"
    )
    
    # Temporal validity
    temporal_start: Optional[datetime] = None
    temporal_end: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Tool that created this relationship")
```

## Document Processing Schemas

### Document Schema

```python
class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(BaseModel):
    """Document metadata and status"""
    doc_id: constr(regex=r'^doc_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Unique document identifier"
    )
    file_path: str = Field(
        ...,
        description="Original file path"
    )
    file_name: str = Field(
        ...,
        description="Original file name"
    )
    file_hash: constr(regex=r'^[a-f0-9]{64}$') = Field(
        ...,
        description="SHA-256 hash of file content"
    )
    
    # Processing status
    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        description="Current processing status"
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Processing completion timestamp"
    )
    processing_time_seconds: Optional[float] = Field(
        None,
        ge=0,
        description="Total processing duration"
    )
    
    # Document properties
    page_count: Optional[int] = Field(
        None,
        ge=1,
        description="Number of pages (for PDFs)"
    )
    word_count: Optional[int] = Field(
        None,
        ge=0,
        description="Total word count"
    )
    language: Optional[str] = Field(
        None,
        regex=r'^[a-z]{2}$',
        description="ISO 639-1 language code"
    )
    
    # Quality and confidence
    confidence: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None,
        description="Overall document quality confidence"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
```

### Chunk Schema

```python
class Chunk(BaseModel):
    """Document chunk for processing"""
    chunk_id: constr(regex=r'^chunk_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Unique chunk identifier"
    )
    doc_id: constr(regex=r'^doc_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Parent document ID"
    )
    
    # Content
    content: str = Field(
        ...,
        min_length=1,
        description="Chunk text content"
    )
    tokens: int = Field(
        ...,
        ge=1,
        description="Number of tokens in chunk"
    )
    
    # Position
    position: int = Field(
        ...,
        ge=0,
        description="Sequential position in document"
    )
    start_char: int = Field(
        ...,
        ge=0,
        description="Start character in document"
    )
    end_char: int = Field(
        ...,
        gt=0,
        description="End character in document"
    )
    page_number: Optional[int] = Field(
        None,
        ge=1,
        description="Page number (for PDFs)"
    )
    
    # Quality
    confidence: confloat(ge=0.0, le=1.0) = Field(
        default=1.0,
        description="Chunk extraction confidence"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Tool Contract Schemas

### Tool Request Schema

```python
class ToolRequest(BaseModel):
    """Standardized tool input contract"""
    input_data: Dict[str, Any] = Field(
        ...,
        description="Tool-specific input data"
    )
    theory_schema: Optional[str] = Field(
        None,
        description="Theory schema ID to apply"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific options"
    )
    
    # Context
    workflow_id: Optional[str] = Field(
        None,
        description="Parent workflow ID"
    )
    step_id: Optional[str] = Field(
        None,
        description="Workflow step ID"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_data": {
                    "text": "John Smith is the CEO of Acme Corp.",
                    "language": "en"
                },
                "theory_schema": "stakeholder_theory_v1",
                "options": {
                    "confidence_threshold": 0.7,
                    "include_context": True
                }
            }
        }
```

### Tool Result Schema

```python
class ToolStatus(str, Enum):
    """Tool execution status"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ToolResult(BaseModel):
    """Standardized tool output contract"""
    status: ToolStatus = Field(
        ...,
        description="Execution status"
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Tool-specific output data"
    )
    confidence: ConfidenceScore = Field(
        ...,
        description="Result confidence score"
    )
    
    # Metadata
    execution_time_ms: float = Field(
        ...,
        ge=0,
        description="Execution duration in milliseconds"
    )
    tool_id: str = Field(
        ...,
        description="Tool that produced this result"
    )
    tool_version: str = Field(
        ...,
        description="Tool version"
    )
    
    # Provenance
    provenance: Dict[str, Any] = Field(
        ...,
        description="Provenance information"
    )
    
    # Warnings and errors
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-fatal warnings"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error details if status is ERROR"
    )
```

## Uncertainty Schemas

### Confidence Score Schema

```python
from pydantic import BaseModel, Field, confloat, conint
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime

class ConfidenceScore(BaseModel):
    """Standardized confidence representation (from ADR-004)"""
    value: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="Normalized probability-like confidence"
    )
    evidence_weight: conint(gt=0) = Field(
        ...,
        description="Number of independent evidence items"
    )
    propagation_method: Literal[
        "bayesian_evidence_power",
        "dempster_shafer",
        "min_max",
        "unknown"
    ] = Field(
        ...,
        description="Method used for confidence propagation"
    )
    
    # CERQual dimensions
    methodological_quality: Optional[confloat(ge=0.0, le=1.0)] = None
    relevance_to_context: Optional[confloat(ge=0.0, le=1.0)] = None
    coherence_score: Optional[confloat(ge=0.0, le=1.0)] = None
    data_adequacy: Optional[confloat(ge=0.0, le=1.0)] = None
    
    # Dependencies
    depends_on: Optional[List[str]] = Field(
        None,
        description="IDs of upstream confidence scores"
    )
    
    # Temporal aspects
    assessment_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="When confidence was assessed"
    )
    validity_window: Optional[Dict[str, datetime]] = Field(
        None,
        description="Time window for confidence validity"
    )
```

## Cross-Modal Schemas

### Cross-Modal Conversion Request

```python
class ConversionMode(str, Enum):
    """Supported data modes"""
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"

class CrossModalRequest(BaseModel):
    """Request for cross-modal conversion"""
    source_data: Dict[str, Any] = Field(
        ...,
        description="Data in source format"
    )
    source_mode: ConversionMode = Field(
        ...,
        description="Current data mode"
    )
    target_mode: ConversionMode = Field(
        ...,
        description="Desired output mode"
    )
    
    # Conversion options
    enrichment_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mode-specific enrichment options"
    )
    preserve_provenance: bool = Field(
        default=True,
        description="Maintain source traceability"
    )
    
    # Context
    analysis_goal: Optional[str] = Field(
        None,
        description="Purpose of conversion for optimization"
    )
```

### Cross-Modal Result

```python
class CrossModalResult(BaseModel):
    """Result of cross-modal conversion"""
    converted_data: Dict[str, Any] = Field(
        ...,
        description="Data in target format"
    )
    target_mode: ConversionMode = Field(
        ...,
        description="Output data mode"
    )
    
    # Enrichments applied
    enrichments: List[str] = Field(
        ...,
        description="List of enrichments added during conversion"
    )
    
    # Conversion quality
    information_preserved: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="Fraction of information preserved"
    )
    confidence: ConfidenceScore = Field(
        ...,
        description="Conversion confidence"
    )
    
    # Provenance
    source_references: Dict[str, List[str]] = Field(
        ...,
        description="Mapping of output elements to source elements"
    )
```

## Workflow Schemas

### Workflow Definition

```python
class WorkflowStep(BaseModel):
    """Single step in a workflow"""
    step_id: str = Field(
        ...,
        regex=r'^step_[a-f0-9\-]{36}$',
        description="Unique step identifier"
    )
    tool_id: str = Field(
        ...,
        regex=r'^T\d{1,3}[A-Z]?$',
        description="Tool to execute"
    )
    
    # Input/output mapping
    inputs: Dict[str, Any] = Field(
        ...,
        description="Input data or references to previous outputs"
    )
    output_key: str = Field(
        ...,
        description="Key to store output in workflow context"
    )
    
    # Dependencies
    depends_on: List[str] = Field(
        default_factory=list,
        description="Step IDs that must complete first"
    )
    
    # Options
    retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts"
    )
    timeout_seconds: Optional[int] = Field(
        None,
        gt=0,
        description="Step timeout"
    )

class WorkflowDefinition(BaseModel):
    """Complete workflow specification"""
    workflow_id: constr(regex=r'^wf_[a-f0-9\-]{36}$') = Field(
        ...,
        description="Unique workflow identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable workflow name"
    )
    description: str = Field(
        ...,
        description="Workflow purpose and description"
    )
    
    # Steps
    steps: List[WorkflowStep] = Field(
        ...,
        min_items=1,
        description="Workflow steps in execution order"
    )
    
    # Configuration
    max_parallel: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum parallel step execution"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="User or system that created workflow")
    tags: List[str] = Field(default_factory=list)
```

## Theory Integration Schemas

### Theory Schema Reference

```python
class TheoryConstruct(BaseModel):
    """Theoretical construct definition"""
    construct_id: str = Field(
        ...,
        description="Unique construct identifier"
    )
    name: str = Field(
        ...,
        description="Construct name"
    )
    definition: str = Field(
        ...,
        description="Formal definition"
    )
    
    # Measurement
    operationalization: Dict[str, Any] = Field(
        ...,
        description="How to measure this construct"
    )
    required_data: List[str] = Field(
        ...,
        description="Required data types"
    )
    
    # Relationships
    related_constructs: List[str] = Field(
        default_factory=list,
        description="Related construct IDs"
    )

class TheorySchema(BaseModel):
    """Complete theory specification"""
    schema_id: str = Field(
        ...,
        description="Unique theory schema ID"
    )
    name: str = Field(
        ...,
        description="Theory name"
    )
    domain: str = Field(
        ...,
        description="Academic domain"
    )
    version: str = Field(
        ...,
        regex=r'^\d+\.\d+\.\d+$',
        description="Semantic version"
    )
    
    # Theory components
    constructs: List[TheoryConstruct] = Field(
        ...,
        min_items=1,
        description="Theory constructs"
    )
    relationships: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Relationships between constructs"
    )
    
    # Validation
    constraints: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Theory constraints and rules"
    )
    
    # Metadata
    authors: List[str] = Field(..., min_items=1)
    citations: List[str] = Field(..., min_items=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Usage Examples

### Creating an Entity

```python
# Example: Creating a person entity with theory grounding
entity = Entity(
    entity_id="entity_123e4567-e89b-12d3-a456-426614174000",
    canonical_name="Jane Doe",
    entity_type=EntityType.PERSON,
    confidence=0.95,
    quality_tier="high",
    theory_grounding={
        "stakeholder_theory": {
            "power": 0.8,
            "legitimacy": 0.9,
            "urgency": 0.6,
            "salience": 0.77  # Calculated from Mitchell et al. formula
        }
    },
    source_references=[
        "doc_abc123",
        "doc_def456"
    ]
)
```

### Processing a Tool Request

```python
# Example: Entity extraction request
request = ToolRequest(
    input_data={
        "text": "Apple Inc. CEO Tim Cook announced new products.",
        "language": "en"
    },
    theory_schema="corporate_governance_v2",
    options={
        "confidence_threshold": 0.8,
        "extract_relationships": True
    },
    workflow_id="wf_789xyz",
    step_id="step_001"
)

# Example: Tool result with entities
result = ToolResult(
    status=ToolStatus.SUCCESS,
    data={
        "entities": [
            {
                "entity_id": "entity_apple_inc",
                "canonical_name": "Apple Inc.",
                "entity_type": "ORGANIZATION",
                "confidence": 0.98
            },
            {
                "entity_id": "entity_tim_cook",
                "canonical_name": "Tim Cook",
                "entity_type": "PERSON",
                "confidence": 0.95
            }
        ],
        "relationships": [
            {
                "source": "entity_tim_cook",
                "target": "entity_apple_inc",
                "type": "CEO_OF",
                "confidence": 0.92
            }
        ]
    },
    confidence=ConfidenceScore(
        value=0.95,
        evidence_weight=2,
        propagation_method="min_max"
    ),
    execution_time_ms=127.5,
    tool_id="T23A",
    tool_version="2.1.0",
    provenance={
        "model": "spacy_en_core_web_trf",
        "timestamp": "2025-07-22T10:30:00Z"
    }
)
```

### Cross-Modal Conversion

```python
# Example: Converting graph data to table format
conversion_request = CrossModalRequest(
    source_data={
        "nodes": [...],  # Graph nodes
        "edges": [...]   # Graph edges
    },
    source_mode=ConversionMode.GRAPH,
    target_mode=ConversionMode.TABLE,
    enrichment_options={
        "compute_centrality": True,
        "include_community_detection": True,
        "aggregate_by": "entity_type"
    },
    analysis_goal="statistical_analysis"
)

# Result includes enriched tabular data
conversion_result = CrossModalResult(
    converted_data={
        "dataframe": {
            "columns": ["entity_id", "name", "type", "degree", "pagerank", "community"],
            "data": [...]
        }
    },
    target_mode=ConversionMode.TABLE,
    enrichments=[
        "degree_centrality",
        "pagerank_score",
        "louvain_community"
    ],
    information_preserved=0.98,
    confidence=ConfidenceScore(
        value=0.96,
        evidence_weight=150,
        propagation_method="bayesian_evidence_power"
    ),
    source_references={
        "row_0": ["node_123", "edges_connected"],
        "row_1": ["node_456", "edges_connected"]
    }
)
```

## Validation and Type Safety

All schemas include:
1. **Type validation**: Enforced through Pydantic's type system
2. **Value constraints**: Min/max values, regex patterns, enum restrictions
3. **Required fields**: Clearly marked with ellipsis (...)
4. **Default values**: Sensible defaults where appropriate
5. **Documentation**: Field descriptions for clarity
6. **Examples**: JSON schema examples for common use cases

These schemas ensure:
- **Contract compliance**: All tools must accept and return these types
- **Type safety**: Errors caught at development time
- **Consistency**: Same data structures throughout the system
- **Extensibility**: Optional fields allow for future additions
- **Validation**: Automatic validation of all data flows

The schemas form the foundation of KGAS's contract-first architecture, enabling reliable tool composition and cross-modal analysis.