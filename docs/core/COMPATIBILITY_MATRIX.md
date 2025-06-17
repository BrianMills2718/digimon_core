# Tool Compatibility Matrix (121-Tool Architecture)

This is the authoritative compatibility matrix for Super-Digimon's 121 tools. It incorporates the three-level identity system, universal quality tracking, and tool contracts for intelligent workflow planning.

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
| T28: Confidence Scorer | Entity + Context refs | Enhanced Entity refs | Reassesses confidence |

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

### Phase 8: Core Services (T107-T121) - FOUNDATIONAL

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
| T121: Workflow State | Checkpointing & recovery | Orchestrator | Crash recovery |

## Critical Tool Chains

### 1. Document to Knowledge Graph (Most Common)
```
T01/T05/T06 (Ingestion) 
    ↓ [Document with initial confidence] → SQLite storage
T15a/b (Chunking)
    ↓ [Chunks inherit document confidence] → SQLite storage
T23a/b (Entity/Relationship Extraction)
    ↓ [Mentions with extraction confidence] → SQLite storage
T28 (Entity Confidence Scoring)
    ↓ [Enhanced confidence scores]
T25 (Coreference)
    ↓ [Linked mentions, confidence propagated]
T31 (Entity Building) - Uses T107 Identity Service
    ↓ [Entities with aggregated confidence] → Neo4j storage
T34 (Relationship Building)
    ↓ [Relationships with min entity confidence] → Neo4j storage
T41 (Entity Embeddings)
    ↓ [Vector representations] → FAISS storage
T76 (Neo4j Storage) + T77 (SQLite Storage) + T78 (FAISS Storage)
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

## Tool Contract Specifications

### Contract-Based Tool Selection

Tools declare contracts that specify:
1. **Required Attributes**: What data fields must exist
2. **Required State**: What processing must have occurred
3. **Produced Attributes**: What the tool creates
4. **State Changes**: How the tool changes workflow state
5. **Error Codes**: Structured error reporting

### Example: Entity Resolution Chain

```python
# T23b Contract (Entity/Relationship Extractor)
{
    "required_state": {
        "chunks_created": true,
        "entities_resolved": false  # Can work without resolution
    },
    "produced_state": {
        "mentions_created": true,
        "relationships_extracted": true
    }
}

# T25 Contract (Coreference Resolver)
{
    "required_state": {
        "mentions_created": true,
        "entities_resolved": "optional"  # Adapts based on domain
    },
    "produced_state": {
        "coreferences_resolved": true
    }
}

# T31 Contract (Entity Node Builder)
{
    "required_state": {
        "mentions_created": true,
        "entities_resolved": "optional"  # Domain choice
    },
    "produced_state": {
        "entities_created": true,
        "graph_ready": true
    }
}
```

### Domain-Specific Resolution

Entity resolution is now optional based on analytical needs:

#### Social Network Analysis (No Resolution)
```python
# Keep @obama and @barackobama as separate entities
workflow_config = {
    "resolve_entities": false,
    "reason": "Track separate social media identities"
}
```

#### Corporate Analysis (With Resolution)
```python
# Merge "Apple Inc.", "Apple Computer", "AAPL"
workflow_config = {
    "resolve_entities": true,
    "reason": "Unified corporate entity analysis"
}
```

### Contract Validation

Before executing any tool:
1. Check required_attributes exist in input data
2. Verify required_state matches current workflow state
3. Ensure resources available for performance requirements
4. Plan error handling based on declared error codes

This contract system enables:
- Automatic tool selection based on current state
- Intelligent error recovery with alternative tools
- Domain-adaptive workflows
- Pre-flight validation before execution

## Database Integration Requirements

### Storage Distribution Strategy
- **Neo4j**: Entities, relationships, communities, graph structure
- **SQLite**: Mentions, documents, chunks, workflow state, provenance, quality scores
- **FAISS**: Entity embeddings, chunk embeddings, similarity indices

### Reference Resolution System
All tools must use the universal reference format:
```
neo4j://entity/ent_12345
sqlite://mention/mention_67890  
faiss://embedding/vec_54321
```

### Quality Tracking Integration
Every database operation must:
1. Preserve confidence scores
2. Update quality metadata
3. Record provenance via T110
4. Support quality filtering

### Transaction Coordination
Multi-database operations require:
1. FAISS operations first (non-transactional)
2. Neo4j and SQLite in coordinated transactions
3. Rollback procedures for partial failures
4. Integrity validation across databases

### Performance Requirements
- Reference resolution: <10ms for single objects
- Batch operations: Handle 1000+ objects efficiently
- Search operations: Sub-second response times
- Quality propagation: Async for large dependency chains

### Error Recovery
- Checkpoint workflow state every 100 operations
- Validate reference integrity on startup
- Support partial result recovery
- Log database-specific errors with context

## Integration Testing Requirements

### Multi-Database Workflows
Test complete data flows across all three databases:
1. Document → SQLite → Entity extraction → Neo4j → Embeddings → FAISS
2. Query → FAISS search → Neo4j enrichment → SQLite provenance
3. Analysis → Neo4j algorithms → Statistical conversion → Results storage

### Consistency Validation
Regular checks for:
- Orphaned references between databases
- Quality score consistency
- Provenance chain completeness
- Version synchronization

### Performance Benchmarks
- 10MB PDF processing: <2 minutes end-to-end
- 1000 entity search: <1 second
- Graph analysis (10K nodes): <30 seconds
- Quality propagation (1000 objects): <5 seconds

This matrix supersedes all previous compatibility documentation and aligns with the 121-tool architecture defined in SPECIFICATIONS.md.