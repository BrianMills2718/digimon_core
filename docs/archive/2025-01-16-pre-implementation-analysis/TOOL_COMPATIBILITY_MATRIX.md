# Tool Compatibility Matrix

This document defines the exact data schemas and compatibility between all 106+ tools, based on discoveries from 37 mock workflows.

## Core Data Type Definitions

### 1. BaseObject (All Data Types Inherit This)

```python
@dataclass
class BaseObject:
    # === REQUIRED ATTRIBUTES ===
    id: str                    # Unique identifier (UUID)
    object_type: str          # Entity, Relationship, Chunk, etc.
    
    # === QUALITY ATTRIBUTES (REQUIRED) ===
    confidence: float         # 0.0 to 1.0
    quality_tier: str        # "high", "medium", "low"
    
    # === PROVENANCE (REQUIRED) ===
    created_by: str          # Tool ID that created this
    created_at: datetime     # When created
    workflow_id: str         # Which workflow/analysis
    
    # === VERSION (REQUIRED) ===
    version: int             # Version number
    
    # === OPTIONAL BUT COMMON ===
    warnings: List[str] = []
    evidence: List[str] = []
    source_refs: List[str] = []
    extraction_method: str = ""
    updated_at: Optional[datetime] = None
    operation_id: Optional[str] = None
```

### 2. Mention (Critical for Three-Level Identity)

```python
@dataclass
class Mention(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    surface_text: str         # Exact text as it appears
    document_ref: str         # Reference to source document
    position: int            # Character position in document
    
    # === OPTIONAL BUT COMMON ===
    context_window: str = ""  # Surrounding text
    entity_candidates: List[Tuple[str, float]] = []  # [(entity_id, confidence)]
    selected_entity: Optional[str] = None
    resolution_confidence: float = 0.0
    language: Optional[str] = None
```

### 3. Entity

```python
@dataclass
class Entity(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    canonical_name: str       # Primary name
    entity_type: str         # PERSON, ORG, LOC, etc.
    
    # === OPTIONAL BUT COMMON ===
    surface_forms: List[str] = []  # All variations
    attributes: Dict[str, Any] = {}  # Flexible properties
    mention_refs: List[str] = []  # References to mentions
    
    # Multi-language support
    names_by_language: Dict[str, str] = {}
    
    # Disambiguation
    disambiguation_score: float = 1.0
    alternative_entities: List[Tuple[str, float]] = []
    
    # Temporal
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    
    # For vectors
    embedding: Optional[List[float]] = None
    embedding_model: Optional[str] = None
```

### 4. Relationship

```python
@dataclass
class Relationship(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    source_id: str           # Entity ID
    target_id: str           # Entity ID
    relationship_type: str   # Type of relationship
    
    # === OPTIONAL BUT COMMON ===
    weight: float = 1.0
    keywords: List[str] = []
    mention_refs: List[str] = []  # Which mentions support this
    
    # Temporal
    temporal_validity: Optional[Dict[str, datetime]] = None
    
    # For conflicts
    conflicting_values: List[Dict] = []
    resolution_method: Optional[str] = None
    
    # Causal
    causal_metadata: Optional[Dict] = None  # For PyWhy integration
```

### 5. Chunk

```python
@dataclass
class Chunk(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    content: str             # Text content
    document_ref: str        # Source document
    position: int           # Position in document
    
    # === OPTIONAL BUT COMMON ===
    chunk_index: int = 0
    total_chunks: Optional[int] = None
    
    # Extracted data
    entity_refs: List[str] = []
    relationship_refs: List[str] = []
    mention_refs: List[str] = []
    
    # For vectors
    embedding: Optional[List[float]] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
```

### 6. Document

```python
@dataclass
class Document(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    content_ref: str         # Reference to actual content
    source_type: str        # PDF, CSV, JSON, etc.
    
    # === OPTIONAL BUT COMMON ===
    title: str = ""
    author: str = ""
    created_date: Optional[datetime] = None
    
    # Processing state
    chunk_refs: List[str] = []
    processing_status: str = "pending"
    error_messages: List[str] = []
    
    # Metadata
    metadata: Dict[str, Any] = {}
    file_size: Optional[int] = None
    page_count: Optional[int] = None
```

### 7. Graph

```python
@dataclass
class Graph(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    entity_refs: List[str]    # References to entities
    relationship_refs: List[str]  # References to relationships
    
    # === OPTIONAL BUT COMMON ===
    name: str = ""
    description: str = ""
    
    # Graph properties
    node_count: int = 0
    edge_count: int = 0
    is_directed: bool = True
    
    # Subgraph support
    parent_graph_ref: Optional[str] = None
    
    # Community structure
    community_refs: List[str] = []
```

### 8. Community

```python
@dataclass
class Community(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    entity_refs: List[str]    # Member entities
    level: int               # Hierarchy level
    
    # === OPTIONAL BUT COMMON ===
    parent_community_ref: Optional[str] = None
    child_community_refs: List[str] = []
    
    # Analysis results
    summary: str = ""
    keywords: List[str] = []
    coherence_score: float = 0.0
    
    # For analysis
    internal_density: float = 0.0
    external_connectivity: float = 0.0
```

### 9. AnalysisResult

```python
@dataclass
class AnalysisResult(BaseObject):
    # === REQUIRED ATTRIBUTES ===
    analysis_type: str       # PageRank, Clustering, etc.
    input_refs: List[str]    # What was analyzed
    
    # === OPTIONAL BUT COMMON ===
    results: Dict[str, Any] = {}  # Flexible results
    metrics: Dict[str, float] = {}
    
    # For tables
    table_data: Optional[Dict] = None  # For statistical results
    
    # Visualization
    visualization_refs: List[str] = []
```

## Tool Input/Output Requirements

### Phase 1: Ingestion Tools (T01-T12)

#### T01: PDF Loader
**Required Inputs:**
- `file_path: str` (path to PDF file)

**Optional Inputs:**
- `ocr_enabled: bool = True`
- `language_hint: str = "en"`
- `page_range: Optional[Tuple[int, int]] = None`

**Outputs:**
```python
{
    "document_ref": "doc_001",  # Document object created
    "status": "success",
    "page_count": 45,
    "confidence": 0.95,  # OCR confidence if applicable
    "warnings": ["Low quality scan on pages 12-14"],
    "quality_tier": "high"
}
```

**Can Feed Into:** T15, T16 (Chunkers)

#### T02: Word Document Loader
**Required Inputs:**
- `file_path: str`

**Optional Inputs:**
- `extract_images: bool = False`
- `preserve_formatting: bool = True`

**Outputs:** Same structure as T01

**Can Feed Into:** T15, T16 (Chunkers)

#### T05: CSV Loader
**Required Inputs:**
- `file_path: str`

**Optional Inputs:**
- `delimiter: str = ","`
- `has_header: bool = True`
- `encoding: str = "utf-8"`
- `dtypes: Optional[Dict[str, str]] = None`

**Outputs:**
```python
{
    "document_ref": "doc_002",
    "table_ref": "table_001",  # Also creates table object
    "row_count": 10000,
    "column_count": 15,
    "columns": ["name", "age", "city", ...],
    "confidence": 1.0,
    "quality_tier": "high"
}
```

**Can Feed Into:** T15, T16, T115 (Table processors)

### Phase 2: Processing Tools (T13-T30)

#### T15: Document Chunker
**Required Inputs:**
- `document_ref: str` OR `document_refs: List[str]`

**Optional Inputs:**
- `chunk_size: int = 1000`
- `chunk_overlap: int = 200`
- `chunking_strategy: str = "sliding_window"`  # or "semantic", "paragraph"
- `preserve_sentences: bool = True`

**Outputs:**
```python
{
    "chunk_refs": ["chunk_001", "chunk_002", ...],
    "chunk_count": 150,
    "sample": [  # First few chunks for preview
        {"id": "chunk_001", "content": "...", "position": 0}
    ],
    "confidence": 0.98,
    "quality_tier": "high"
}
```

**Can Feed Into:** T23, T24, T41 (Entity extraction, Embedding)

#### T23: Entity Recognizer
**Required Inputs:**
- `chunk_refs: List[str]` OR `text: str`

**Optional Inputs:**
- `entity_types: List[str] = ["PERSON", "ORG", "LOC"]`
- `model: str = "spacy_large"`
- `confidence_threshold: float = 0.7`
- `create_mentions: bool = True`  # Critical for three-level system

**Outputs:**
```python
{
    "mention_refs": ["mention_001", "mention_002", ...],
    "entity_candidates": [
        {
            "surface_text": "Apple",
            "mention_ref": "mention_001",
            "candidates": [
                {"entity_type": "ORG", "confidence": 0.92},
                {"entity_type": "FRUIT", "confidence": 0.08}
            ]
        }
    ],
    "count": 245,
    "confidence": 0.87,
    "quality_tier": "high"
}
```

**Can Feed Into:** T25, T26, T29 (Coreference, Linking, Disambiguation)

#### T25: Coreference Resolver
**Required Inputs:**
- `mention_refs: List[str]`

**Optional Inputs:**
- `strategy: str = "neural"`  # or "rule_based", "hybrid"
- `context_window: int = 100`

**Outputs:**
```python
{
    "coreference_chains": [
        {
            "chain_id": "coref_001",
            "mention_refs": ["mention_001", "mention_045", "mention_089"],
            "canonical_text": "Apple Inc.",
            "confidence": 0.88
        }
    ],
    "updated_mention_refs": ["mention_001", ...],  # With coreference info
    "confidence": 0.85,
    "quality_tier": "high"
}
```

**Can Feed Into:** T26, T29, T31 (Entity linking and construction)

### Phase 3: Construction Tools (T31-T48)

#### T31: Entity Node Builder
**Required Inputs:**
- `mention_refs: List[str]` OR `coreference_chains: List[Dict]`

**Optional Inputs:**
- `merge_strategy: str = "conservative"`  # or "aggressive", "manual"
- `min_confidence: float = 0.7`
- `create_all_candidates: bool = False`

**Outputs:**
```python
{
    "entity_refs": ["ent_001", "ent_002", ...],
    "entity_count": 156,
    "merge_decisions": [
        {
            "merged_entities": ["temp_001", "temp_002"],
            "final_entity": "ent_001",
            "reason": "High coreference confidence"
        }
    ],
    "confidence": 0.83,
    "quality_tier": "high"
}
```

**Can Feed Into:** T34, T37, T41, T76 (Relationship building, Storage)

#### T34: Relationship Builder
**Required Inputs:**
- `entity_refs: List[str]`
- `chunk_refs: List[str]` OR `relationship_mentions: List[Dict]`

**Optional Inputs:**
- `relationship_types: Optional[List[str]] = None`  # None = detect all
- `min_confidence: float = 0.6`
- `use_dependency_parsing: bool = True`

**Outputs:**
```python
{
    "relationship_refs": ["rel_001", "rel_002", ...],
    "relationship_count": 423,
    "relationship_types": {
        "employed_by": 145,
        "located_in": 89,
        "acquired": 23
    },
    "confidence": 0.79,
    "quality_tier": "medium"
}
```

**Can Feed Into:** T37, T76 (Deduplication, Storage)

### Phase 4: Retrieval Tools (T49-T67)

#### T49: Entity Search (VDB)
**Required Inputs:**
- `query: str` OR `query_embedding: List[float]`

**Optional Inputs:**
- `k: int = 10`
- `entity_types: Optional[List[str]] = None`
- `min_similarity: float = 0.7`
- `search_in: str = "all"`  # or "names", "descriptions", "attributes"

**Outputs:**
```python
{
    "results": [
        {
            "entity_ref": "ent_001",
            "similarity": 0.92,
            "entity_name": "Apple Inc.",
            "entity_type": "ORG",
            "matched_on": "canonical_name"
        }
    ],
    "total_results": 10,
    "confidence": 0.88,
    "quality_tier": "high"
}
```

**Can Feed Into:** T51, T54, T56, T57 (Other retrieval and answer tools)

#### T51: Local Search
**Required Inputs:**
- `entity_refs: List[str]` OR `entity_ref: str`

**Optional Inputs:**
- `hop_limit: int = 2`
- `relationship_types: Optional[List[str]] = None`
- `direction: str = "both"`  # or "outgoing", "incoming"
- `max_nodes: int = 100`

**Outputs:**
```python
{
    "subgraph": {
        "entity_refs": ["ent_001", "ent_002", ...],
        "relationship_refs": ["rel_001", "rel_002", ...],
        "hop_distances": {"ent_001": 0, "ent_002": 1, ...}
    },
    "confidence": 0.91,
    "quality_tier": "high"
}
```

**Can Feed Into:** T57, T68-75 (Answer generation, Analysis)

### Phase 5: Analysis Tools (T68-T75)

#### T68: PageRank Calculator
**Required Inputs:**
- `entity_refs: List[str]`
- `relationship_refs: List[str]`

**Optional Inputs:**
- `damping_factor: float = 0.85`
- `iterations: int = 100`
- `personalization: Optional[Dict[str, float]] = None`
- `use_weights: bool = True`

**Outputs:**
```python
{
    "analysis_result_ref": "analysis_001",
    "scores": {
        "ent_001": 0.0234,
        "ent_002": 0.0189,
        ...
    },
    "top_k": [
        {"entity_ref": "ent_001", "score": 0.0234, "rank": 1}
    ],
    "convergence_achieved": True,
    "iterations_used": 67,
    "confidence": 0.95,
    "quality_tier": "high"
}
```

**Can Feed Into:** T115, T117 (Format converters, Statistical analysis)

### Cross-Format Conversion Tools (T115-T117)

#### T115: Graph to Table Converter
**Required Inputs:**
- `entity_refs: List[str]` OR `analysis_result_ref: str`

**Optional Inputs:**
- `include_attributes: List[str] = ["all"]`
- `relationship_aggregation: str = "count"`  # or "list", "weighted_sum"
- `output_format: str = "wide"`  # or "long", "edge_list"

**Outputs:**
```python
{
    "table_ref": "table_002",
    "schema": {
        "columns": ["entity_id", "name", "type", "pagerank_score", ...],
        "row_count": 156
    },
    "sample_rows": [...],  # First 5 rows
    "confidence": 1.0,  # Format conversion is deterministic
    "quality_tier": "high"
}
```

**Can Feed Into:** Statistical analysis tools, T117

#### T116: Table to Graph Builder
**Required Inputs:**
- `table_ref: str`
- `source_column: str`
- `target_column: str`

**Optional Inputs:**
- `relationship_type: str = "related_to"`
- `weight_column: Optional[str] = None`
- `entity_columns: List[str] = []`  # Additional columns become attributes

**Outputs:**
```python
{
    "entity_refs": [...],
    "relationship_refs": [...],
    "graph_ref": "graph_002",
    "statistics": {
        "entities_created": 89,
        "relationships_created": 234
    },
    "confidence": 0.90,
    "quality_tier": "high"
}
```

**Can Feed Into:** All graph-based tools (T49-T75)

## Tool Chain Validation Rules

### 1. Identity Preservation Chain
```
Text → T23 (Entity Recognition) → Mentions
Mentions → T25 (Coreference) → Coreference Chains  
Chains → T31 (Entity Builder) → Entities
```
**Rule**: Entity IDs must be traceable back to original mentions

### 2. Quality Propagation Rules
```python
def propagate_confidence(upstream_conf: List[float], operation: str) -> float:
    if operation == "extraction":
        return min(upstream_conf) * 0.95
    elif operation == "aggregation":
        return np.mean(upstream_conf)
    elif operation == "filtering":
        return max(upstream_conf)  # Keeps best quality
    elif operation == "inference":
        return min(upstream_conf) * 0.85
```

### 3. Reference Validation
All tools must:
- Accept references (not full objects) as input
- Return references in outputs
- Include count and sample for large results
- Never exceed memory limits with full data

### 4. Streaming Compatibility
Tools marked with streaming support must:
- Accept iterator inputs: `Iterator[ChunkRef]`
- Yield results incrementally
- Support batch_size parameter
- Maintain state between batches

## Common Tool Chain Patterns

### Pattern 1: Document to Knowledge Graph
```
T01 (PDF) → T15 (Chunker) → T23 (NER) → T25 (Coref) → 
T31 (Entities) + T34 (Relations) → T76 (Neo4j Storage)
```

### Pattern 2: Table to Graph Analysis
```
T05 (CSV) → T116 (Table→Graph) → T68 (PageRank) → 
T115 (Graph→Table) → T117 (Statistical Analysis)
```

### Pattern 3: Multi-hop Question Answering
```
T49 (Entity Search) → T51 (Local Search) → T54 (Path Finding) → 
T57 (Answer Generation)
```

### Pattern 4: Community Analysis
```
T76 (Load Graph) → T73 (Community Detection) → 
T74 (Clustering) → T115 (Graph→Table) → Statistical Analysis
```

## Adaptation Rules

### Missing Required Attributes
- Tools should provide clear error messages
- Suggest which upstream tool can provide missing data
- Never fail silently

### Missing Optional Attributes  
- Use sensible defaults
- Log what defaults were used
- Continue processing normally

### Quality Filtering
- Tools should respect min_confidence parameters
- Always return partial results with clear stats
- Mark filtered items in warnings

### Format Mismatches
- Automatically invoke converter tools (T115-T117)
- Cache conversions for efficiency
- Maintain identity across formats

## Implementation Notes

1. **Every tool** must track confidence and quality_tier
2. **Every tool** must use reference-based I/O
3. **Identity Service** (T107) manages the three-level system
4. **Provenance Service** (T110) tracks all operations
5. **Quality Service** (T111) handles confidence propagation

This matrix ensures that all 106+ tools can work together seamlessly while maintaining data quality, identity, and provenance throughout the pipeline.