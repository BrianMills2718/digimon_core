# Tool Compatibility Matrix (120-Tool Architecture)

This is the authoritative compatibility matrix for Super-Digimon's 120 tools. It incorporates the three-level identity system and universal quality tracking discovered through mock workflow analysis.

## Core Data Types

All data types inherit from BaseObject and include quality tracking:

### 1. BaseObject (Foundation for all types)
```python
{
    # Identity
    "id": str,              # Unique identifier
    "object_type": str,     # Entity, Relationship, Chunk, etc.
    
    # Quality (REQUIRED for all objects)
    "confidence": float,    # 0.0 to 1.0
    "quality_tier": str,    # "high", "medium", "low"
    
    # Provenance (REQUIRED)
    "created_by": str,      # Tool that created this
    "created_at": datetime,
    "workflow_id": str,
    
    # Version
    "version": int,
    
    # Optional but common
    "warnings": List[str],
    "evidence": List[str],
    "source_refs": List[str]
}
```

### 2. Mention (Three-Level Identity - Level 2)
```python
{
    **BaseObject,
    "surface_text": str,       # Exact text
    "document_ref": str,       # Source document
    "position": int,           # Character position
    "context_window": str,     # Surrounding text
    "entity_candidates": List[Tuple[str, float]],  # Possible entities
    "selected_entity": str     # Resolved entity ID
}
```

### 3. Entity (Three-Level Identity - Level 3)
```python
{
    **BaseObject,
    "canonical_name": str,
    "entity_type": str,
    "surface_forms": List[str],    # All variations
    "mention_refs": List[str],     # Links to mentions
    "attributes": Dict[str, Any]   # Flexible properties
}
```

### 4. Relationship
```python
{
    **BaseObject,
    "source_id": str,          # Entity ID
    "target_id": str,          # Entity ID  
    "relationship_type": str,
    "weight": float,
    "mention_refs": List[str]  # Supporting mentions
}
```

### 5. Chunk
```python
{
    **BaseObject,
    "content": str,
    "document_ref": str,
    "position": int,
    "entity_refs": List[str],
    "relationship_refs": List[str],
    "mention_refs": List[str]
}
```

### 6. Graph
```python
{
    **BaseObject,
    "entity_refs": List[str],
    "relationship_refs": List[str],
    "name": str,
    "description": str
}
```

### 7. Table
```python
{
    **BaseObject,
    "schema": Dict,
    "row_refs": List[str],     # Reference-based rows
    "source_graph_ref": str    # If converted from graph
}
```

## Tool Input/Output Matrix

### Phase 1: Ingestion (T01-T12)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T01: PDF Loader | file_path | Document (with confidence based on OCR quality) | Initial quality set |
| T05: CSV Loader | file_path | Document + Table | confidence: 1.0 (structured) |
| T06: JSON Loader | file_path | Document | confidence: 1.0 (structured) |

### Phase 2: Processing (T13-T30)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T15a: Sliding Window Chunker | Document refs | Chunk refs | Preserves document confidence |
| T15b: Semantic Chunker | Document refs | Chunk refs | May reduce confidence slightly |
| T23a: Traditional NER | Chunk refs | Mention refs | confidence: ~0.85 |
| T23b: LLM Extractor | Chunk refs | Mention + Relationship refs | confidence: ~0.90 |
| T25: Coreference | Mention refs | Updated Mention refs | Propagates lowest confidence |

### Phase 3: Construction (T31-T48)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T31: Entity Builder | Mention refs | Entity refs | Aggregates mention confidence |
| T34: Relationship Builder | Entity + Chunk refs | Relationship refs | Min of entity confidences |
| T41: Embedder | Entity/Chunk refs | Embedding vectors | Preserves source confidence |

### Phase 4: Retrieval (T49-T67)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T49: Entity Search | Query + Entity refs | Ranked Entity refs | Adds similarity confidence |
| T51: Local Search | Entity refs | Subgraph | Propagates confidence |
| T54: Path Finding | Source/Target entities | Path refs | Min confidence along path |

### Phase 5: Analysis (T68-T75)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T68: PageRank | Entity + Relationship refs | Analysis result | Statistical confidence |
| T73: Community Detection | Graph refs | Community refs | Clustering confidence |

### Phase 6: Storage (T76-T81)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T76: Neo4j Storage | Any refs | Storage confirmation | No quality change |
| T77: SQLite Storage | Metadata | Storage confirmation | No quality change |
| T78: FAISS Storage | Embedding refs | Index confirmation | No quality change |

### Phase 7: Interface (T82-T106)

| Tool | Inputs | Outputs | Quality Impact |
|------|--------|---------|----------------|
| T82-89: NLP Tools | Various | Processed text | Task-specific confidence |
| T90-106: UI/Export | Various | Formatted output | Preserves confidence |

### Phase 8: Core Services (T107-T120) - FOUNDATIONAL

| Tool | Purpose | Interactions | Critical for |
|------|---------|--------------|--------------|
| T107: Identity Service | Three-level identity management | Used by ALL entity-related tools | T23, T25, T31 |
| T108: Version Service | Four-level versioning | ALL tools that modify data | Everything |
| T109: Entity Normalizer | Canonical forms | T31, T34 | Entity consistency |
| T110: Provenance Service | Operation tracking | ALL tools | Reproducibility |
| T111: Quality Service | Confidence assessment | ALL tools | Quality tracking |
| T112: Constraint Engine | Data validation | T31, T34, construction tools | Data integrity |
| T113: Ontology Manager | Schema enforcement | T23, T31, T34 | Type consistency |
| T114: Provenance Tracker | Enhanced lineage | Analysis tools | Impact analysis |
| T115: Graph→Table | Format conversion | Analysis tools needing tables | Statistical analysis |
| T116: Table→Graph | Format conversion | Ingestion of structured data | Graph building |
| T117: Format Auto-Selector | Optimal format choice | Analysis planning | Performance |
| T118: Temporal Reasoner | Time-based logic | Temporal data tools | Time analysis |
| T119: Semantic Evolution | Meaning tracking | Long-term analysis | Knowledge evolution |
| T120: Uncertainty Service | Propagation | ALL analysis tools | Uncertainty tracking |

## Critical Tool Chains

### 1. Document to Knowledge Graph (Most Common)
```
T01/T05/T06 (Ingestion) 
    ↓ [Document with initial confidence]
T15a/b (Chunking)
    ↓ [Chunks inherit document confidence]
T23a/b (Entity/Relationship Extraction)
    ↓ [Mentions with extraction confidence]
T25 (Coreference)
    ↓ [Linked mentions, confidence propagated]
T31 (Entity Building) - Uses T107 Identity Service
    ↓ [Entities with aggregated confidence]
T34 (Relationship Building)
    ↓ [Relationships with min entity confidence]
T76 (Neo4j Storage)
```

### 2. Graph to Statistical Analysis
```
T76 (Load from Neo4j)
    ↓ [Graph with stored confidence]
T115 (Graph→Table Converter)
    ↓ [Table preserving all attributes]
External Statistical Tools (via Python)
    ↓ [Statistical results]
T117 (Statistical Test Runner)
```

### 3. Quality-Filtered Retrieval
```
T49 (Entity Search)
    ↓ [All matches with confidence]
T111 (Quality Service - Filter)
    ↓ [Only high-confidence results]
T51 (Local Search)
    ↓ [Subgraph of quality entities]
T57 (Answer Generation)
```

## Implementation Requirements

### Every Tool MUST:
1. Accept and propagate confidence scores
2. Use reference-based I/O (never full objects)
3. Record provenance via T110
4. Support quality filtering
5. Work with partial data

### Core Services Integration:
- T107-T111 must be implemented FIRST
- All other tools depend on these services
- No tool bypasses the identity/quality system

### Data Flow Rules:
1. Confidence only decreases (or stays same)
2. Quality tier can be upgraded only with evidence
3. Provenance is append-only
4. References are immutable

This matrix supersedes all previous compatibility documentation and aligns with the 120-tool architecture defined in SPECIFICATIONS.md.