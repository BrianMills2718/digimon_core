---
status: living
---

# Compatibility Matrix

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
**ORM Alignment**: Represents the foundational object type in the Object-Role Modeling framework, providing the base structure for all conceptual entities.

### 2. Mention (Three-Level Identity - Level 2)
```python
{
    **BaseObject,
    "surface_text": str,       # Exact text as appears in document
    "document_ref": str,       # Reference to source document
    "chunk_ref": str,          # Reference to containing chunk
    "position": {              # Precise location tracking
        "char_start": int,     # Character position start
        "char_end": int,       # Character position end
        "sentence_idx": int,   # Sentence number in chunk
        "token_idx": int       # Token position in sentence
    },
    "context_window": str,     # Surrounding text for disambiguation
    "entity_candidates": List[{
        "entity_id": str,      # Candidate entity reference
        "confidence": float,   # Confidence score 0.0-1.0
        "reason": str          # Why this candidate
    }],
    "selected_entity": str,    # Final resolved entity ID
    "selection_confidence": float  # Confidence in selection
}
```

### 3. Entity (Three-Level Identity - Level 3)
```python
{
    **BaseObject,
    "canonical_name": str,         # Primary name for entity
    "entity_type": str,            # Person, Organization, Location, etc.
    "surface_forms": List[str],    # All textual variations seen
    "mention_refs": List[str],     # Links to supporting mentions
    "attributes": {                # Structured properties
        "standard": Dict[str, Any],    # Common attributes
        "domain_specific": Dict[str, Any],  # Theory-specific
        "temporal": Dict[str, Any]     # Time-varying attributes
    },
    "mcl_mapping": {               # Master Concept Library alignment
        "mcl_id": str,             # MCL primary key
        "concept_type": str,       # MCL concept classification
        "confidence": float        # Mapping confidence
    },
    "embedding": List[float]       # Optional: Vector representation
}
```
**ORM Alignment**: Represents an Object Type in the Object-Role Modeling conceptual framework, mapping to standardized concepts from the Master Concept Library.

### 4. Relationship
```python
{
    **BaseObject,
    "source_id": str,          # Entity ID
    "target_id": str,          # Entity ID  
    "relationship_type": str,
    "weight": float,
    "mention_refs": List[str], # Supporting mentions
    "source_role_name": str,   # ORM role for source entity
    "target_role_name": str    # ORM role for target entity
}
```
**ORM Alignment**: Represents a Fact Type (predicate) in the Object-Role Modeling framework, explicitly defining the Roles played by participating Object Types through `source_role_name` and `target_role_name` attributes.

### 5. Chunk
```python
{
    **BaseObject,
    "content": str,                # Text content of chunk
    "document_ref": str,           # Parent document reference
    "chunk_metadata": {
        "position": int,           # Order in document
        "start_char": int,         # Character position start
        "end_char": int,           # Character position end
        "chunk_type": str,         # Paragraph, section, etc.
        "overlap_prev": int,       # Overlap with previous chunk
        "overlap_next": int        # Overlap with next chunk
    },
    "extracted_refs": {
        "mention_refs": List[str],      # Mentions found
        "entity_refs": List[str],       # Entities referenced
        "relationship_refs": List[str]  # Relationships found
    },
    "embedding": List[float]       # Optional: Chunk embedding
}
```

### 6. Graph
```python
{
    **BaseObject,
    "name": str,                   # Graph identifier
    "description": str,            # Graph purpose/content
    "graph_metadata": {
        "node_count": int,         # Number of entities
        "edge_count": int,         # Number of relationships
        "graph_type": str,         # Directed, undirected, etc.
        "created_from": str        # Source (document set, query, etc.)
    },
    "content_refs": {
        "entity_refs": List[str],      # All entities in graph
        "relationship_refs": List[str], # All relationships
        "subgraph_refs": List[str]     # Optional: Named subgraphs
    },
    "analysis_metadata": {
        "density": float,          # Graph density
        "connected_components": int,  # Number of components
        "avg_degree": float        # Average node degree
    }
}
```

### 7. Table
```python
{
    **BaseObject,
    "name": str,                   # Table identifier
    "schema": {                    # Table structure
        "columns": List[{
            "name": str,           # Column name
            "type": str,           # Data type
            "description": str,    # Column purpose
            "source_path": str     # Graph path if converted
        }],
        "primary_key": List[str],  # Primary key columns
        "indexes": List[str]       # Indexed columns
    },
    "data_refs": {
        "row_refs": List[str],     # Reference to row data
        "row_count": int,          # Number of rows
        "source_graph_ref": str    # If converted from graph
    },
    "conversion_metadata": {
        "conversion_type": str,    # How graph was flattened
        "loss_assessment": str,    # What was lost in conversion
        "reversibility": bool      # Can recreate graph exactly
    }
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
| T23b: LLM Extractor | Chunk refs | Mention + Relationship refs (mapped to Master Concept Library) | confidence: ~0.90 |
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
    ↓ [Vector representations] → Neo4j vector index storage
T76 (Neo4j Storage & Vector Index) + T77 (SQLite Storage)
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

### 3. Master Concept Library Integration
```
T23b: LLM Extractor
    ↓ [Extracts indigenous_term from text]
Master Concept Library Lookup
    ↓ [Maps to standardized concept names]
Entity/Relationship Creation
    ↓ [Uses ORM-aligned data structures]
Validation via Pydantic
    ↓ [Ensures contract compliance]
```

**Key Features:**
- **Indigenous Term Extraction**: LLM identifies domain-specific terminology from source documents
- **Standardized Mapping**: Terms are mapped to Master Concept Library's controlled vocabulary
- **ORM Compliance**: All created entities and relationships follow Object-Role Modeling principles
- **Human-in-the-Loop**: Novel terms can be proposed for library expansion

### 4. Quality-Filtered Retrieval
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

### Programmatic Contract Verification

All tool contracts are defined in structured, machine-readable formats (YAML/JSON) to enable automated validation. This aims to catch compatibility issues early in the development cycle, enforce data integrity, and ensure consistency across the 121-tool vision.

**How it Works:**

1. **Schema-Driven Definitions**: Data models (e.g., Document, Entity, Relationship) are defined using Pydantic, which directly reflects the ORM-based conceptual schema and Master Concept Library standards.

2. **Runtime Validation**: Tools leverage Pydantic's capabilities for runtime validation, ensuring all inputs and outputs strictly conform to their defined types and attributes.

3. **CI/CD Integration**: Automated tests for contract compliance are a required part of the Continuous Integration/Continuous Deployment (CI/CD) pipeline. No code that breaks a contract can be merged.

4. **Dedicated Contract Tests**: A dedicated suite of tests verifies each tool's adherence to its input/output contracts and state changes.

**Implementation Location**: See `/_schemas/theory_meta_schema_v9.jsontool_contract_schema.yaml` for the formal contract schema definition.

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
- **Neo4j Vector Index**: Entity embeddings, chunk embeddings, similarity search within Neo4j

### Reference Resolution System
All tools must use the universal reference format:
```
neo4j://entity/ent_12345
sqlite://mention/mention_67890  
neo4j://entity/ent_vector_54321
```

### Quality Tracking Integration
Every database operation must:
1. Preserve confidence scores
2. Update quality metadata
3. Record provenance via T110
4. Support quality filtering

### Transaction Coordination
Multi-database operations require:
1. Neo4j vector index operations are ACID-compliant within the same transaction
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
1. Document → SQLite → Entity extraction → Neo4j (graph + embeddings)
2. Query → Neo4j vector search → Neo4j enrichment → SQLite provenance
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

## Schema Validation and Consistency

### Pydantic Models
All data types are implemented as Pydantic models for runtime validation:

```python
# src/models/base.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseObject(BaseModel):
    """Base model for all KGAS objects"""
    id: str = Field(..., regex="^[a-zA-Z0-9_-]+$")
    object_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    quality_tier: str = Field(..., regex="^(high|medium|low)$")
    created_by: str
    created_at: datetime
    workflow_id: str
    version: int = Field(default=1, ge=1)
    warnings: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Schema Registry
Central registry ensures consistency across all tools:

```python
# src/core/schema_registry.py
class SchemaRegistry:
    """Central schema registry for data consistency"""
    
    def __init__(self):
        self.schemas = {}
        self._load_core_schemas()
    
    def register_schema(self, name: str, schema: Type[BaseModel]):
        """Register a schema for validation"""
        self.schemas[name] = schema
    
    def validate(self, object_type: str, data: Dict[str, Any]) -> BaseModel:
        """Validate data against registered schema"""
        if object_type not in self.schemas:
            raise ValueError(f"Unknown object type: {object_type}")
        
        schema = self.schemas[object_type]
        return schema(**data)  # Pydantic validation
    
    def get_schema_json(self, object_type: str) -> Dict:
        """Get JSON schema for object type"""
        schema = self.schemas[object_type]
        return schema.schema()
```

### Cross-Schema Consistency Rules

#### 1. Reference Integrity
- All `*_ref` fields must reference existing objects
- References use consistent format: `{store}://{type}/{id}`
- Orphaned references are detected and reported

#### 2. Confidence Propagation
- Child objects cannot have higher confidence than parents
- Aggregated confidence uses minimum of components
- Confidence decay is monotonic through pipelines

#### 3. MCL Alignment
- All entity types map to Master Concept Library
- New concepts require MCL review process
- Mappings include confidence scores

#### 4. Temporal Consistency
- All timestamps use ISO 8601 format
- Created_at < modified_at invariant
- Version numbers increment monotonically

### Schema Evolution Process

1. **Backward Compatibility**
   - New fields are optional with defaults
   - Field removal requires deprecation period
   - Type changes require migration scripts

2. **Version Management**
   ```python
   class SchemaVersion:
       version: str = "1.0.0"
       compatible_versions: List[str] = ["0.9.0", "0.9.1"]
       migration_required: List[str] = ["0.8.x"]
   ```

3. **Migration Support**
   ```python
   def migrate_v1_to_v2(old_data: Dict) -> Dict:
       """Migrate schema from v1 to v2"""
       new_data = old_data.copy()
       # Add new required fields with defaults
       new_data['mcl_mapping'] = {
           'mcl_id': 'unknown',
           'confidence': 0.5
       }
       return new_data
   ```

### Validation in CI/CD

```yaml
# .github/workflows/schema-validation.yml
schema-validation:
  steps:
    - name: Validate Schema Consistency
      run: |
        python scripts/validate_schemas.py
        
    - name: Check Schema Coverage
      run: |
        python scripts/check_schema_coverage.py
        
    - name: Test Schema Migrations
      run: |
        pytest tests/schema/test_migrations.py
```

### Common Schema Violations and Fixes

| Violation | Example | Fix |
|-----------|---------|-----|
| Missing confidence | `{"name": "Entity"}` | Add `"confidence": 0.95` |
| Invalid reference | `"ref": "entity123"` | Use `"ref": "neo4j://entity/entity123"` |
| Type mismatch | `"position": "5"` | Use `"position": 5` (integer) |
| Missing provenance | No created_by | Add `"created_by": "T23a"` |

This matrix supersedes all previous compatibility documentation and aligns with the 121-tool architecture defined in SPECIFICATIONS.md, with enhanced schema validation ensuring data consistency across all tools.