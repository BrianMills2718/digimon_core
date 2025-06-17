# Synthesized Requirements from All Mock Workflows

## Executive Summary

After analyzing 37 detailed mock workflows, we've identified the core requirements for Super-Digimon. This synthesis prioritizes requirements for the PhD thesis prototype, excluding collaborative features and extreme scale handling as noted.

## Core Architectural Requirements

### 1. Three-Level Identity System (CRITICAL)

**Requirement**: Every piece of text must be traceable through three levels of identification.

```python
# Level 1: Surface Form
surface_form = "Apple"  # The actual text

# Level 2: Mention
mention = {
    "mention_id": "mention_001",
    "surface_text": "Apple",
    "context": "Apple announced record profits",
    "document_id": "doc_001",
    "position": 1234
}

# Level 3: Entity (Canonical)
entity = {
    "entity_id": "ent_apple_inc_001",
    "canonical_name": "Apple Inc.",
    "type": "ORG",
    "surface_forms": ["Apple", "AAPL", "Apple Computer"]
}
```

**Why Critical**: 
- Same text can mean different entities (Apple Inc. vs apple fruit)
- Entities have multiple surface forms (Apple, AAPL)
- Need exact provenance for academic rigor

### 2. Universal Quality/Confidence Framework (CRITICAL)

**Requirement**: Every data object must track its quality and confidence.

```python
class QualityTracked:
    confidence: float  # 0.0 to 1.0
    quality_tier: Literal["high", "medium", "low"]
    extraction_method: str
    evidence: List[str]
    warnings: List[str]
```

**Implementation Throughout Pipeline**:
- OCR confidence → Entity extraction confidence → Relationship confidence → Analysis confidence
- Uncertainty propagates and compounds
- Users can filter by quality thresholds

### 3. Comprehensive Versioning System (HIGH)

**Requirement**: Four types of versioning to track evolution.

```python
# 1. Schema Versioning
schema = {"version": "1.2", "migration_from": "1.1"}

# 2. Data Versioning
entity = {"version": 3, "previous_version": 2, "change_reason": "correction"}

# 3. Graph Versioning  
graph = {"version": "v2024_01_15", "parent": "v2024_01_01"}

# 4. Analysis Versioning
analysis = {"version": 2, "based_on_data": "v2024_01_15"}
```

**Why Important**: 
- Handle schema evolution
- Track corrections and updates
- Enable reproducibility
- Support knowledge evolution

### 4. Reference-Based Data Flow (CRITICAL)

**Requirement**: Never pass full data between tools, only references.

```python
# BAD: Memory overflow
output = {"chunks": [... 25,000 full text chunks ...]}

# GOOD: Scalable
output = {
    "chunk_refs": ["sqlite://chunks/batch_001/*"],
    "count": 25000,
    "sample": [... first 10 for preview ...]
}
```

**Storage Pattern**:
- SQLite: Metadata, chunks, provenance
- Neo4j: Graph structures
- FAISS: Vectors only
- References connect them

### 5. Flexible Format Transformations (CRITICAL)

**Requirement**: Seamlessly transform between formats based on analytical needs.

```
Documents → Chunks → Entities/Relations → Graph
                ↓                           ↓
            Embeddings                   Tables
                ↓                           ↓
            Vectors                    Statistics
```

**Key Insight**: Not everything needs to be a graph! Some analyses work better with tables or vectors.

## Essential Services Layer

### 1. Identity Service (CRITICAL)

```python
class IdentityService:
    def create_mention(surface_text: str, context: dict) -> str
    def resolve_mention(mention_id: str) -> str  # Returns entity_id
    def create_entity(canonical_name: str, type: str) -> str
    def merge_entities(entity_ids: List[str]) -> str
    def get_surface_forms(entity_id: str) -> List[str]
```

### 2. Provenance Service (CRITICAL)

```python
class ProvenanceService:
    def record_operation(tool_id: str, inputs: List[str], 
                        outputs: List[str], params: dict) -> str
    def trace_lineage(object_id: str) -> Dict  # Full history
    def find_affected_by_change(changed_id: str) -> List[str]
```

### 3. Quality Service (HIGH)

```python
class QualityService:
    def assess_confidence(object: Any, method: str) -> float
    def propagate_confidence(upstream: List[float], 
                           operation: str) -> float
    def aggregate_confidence(sources: List[float]) -> float
```

### 4. Constraint Engine (HIGH)

```python
class ConstraintEngine:
    def register_constraints(constraints: dict) -> str
    def check_constraints(data: Any, constraint_id: str) -> bool
    def find_almost_qualified(data: Any, constraints: dict) -> List
    def diff_constraints(v1: str, v2: str) -> dict
```

## Data Schema Requirements

### Base Object (All Data Inherits)

```python
@dataclass
class BaseObject:
    # Identity
    id: str  # UUID
    object_type: str
    
    # Version
    version: int
    created_at: datetime
    updated_at: datetime
    
    # Quality
    confidence: float
    quality_tier: str
    warnings: List[str]
    
    # Provenance
    created_by: str  # tool_id
    source_refs: List[str]
    evidence: List[str]
    
    # Workflow
    workflow_id: str
    operation_id: str
```

### Core Data Types

```python
@dataclass
class Entity(BaseObject):
    canonical_name: str
    entity_type: str
    surface_forms: List[str]
    attributes: Dict[str, Any]  # Flexible
    
    # Multi-language support
    names_by_language: Dict[str, str]
    
    # Disambiguation
    disambiguation_score: float
    alternative_entities: List[Tuple[str, float]]

@dataclass
class Relationship(BaseObject):
    source_id: str
    target_id: str
    relationship_type: str
    
    # Optional enrichments
    weight: Optional[float]
    temporal_validity: Optional[DateRange]
    
    # For conflicts
    conflicting_values: Optional[List[dict]]
    resolution_method: Optional[str]

@dataclass
class Mention(BaseObject):
    surface_text: str
    document_ref: str
    position: int
    context_window: str
    
    # Resolution
    entity_candidates: List[Tuple[str, float]]
    selected_entity: str
    resolution_confidence: float
```

## Processing Requirements

### 1. Streaming-First Design (HIGH)

```python
# Every tool should support streaming
def process_stream(
    documents: Iterator[Document], 
    batch_size: int = 1000
) -> Iterator[Entity]:
    batch = []
    for doc in documents:
        batch.append(doc)
        if len(batch) >= batch_size:
            yield from extract_entities(batch)
            batch = []
```

### 2. Partial Results Always (HIGH)

```python
{
    "success": [...],  # What worked
    "failures": [...],  # What failed  
    "partial": [...],  # What partially worked
    "summary": {
        "total": 1000,
        "successful": 950,
        "failed": 30,
        "partial": 20
    }
}
```

### 3. Uncertainty Propagation (HIGH)

```python
class UncertaintyPropagator:
    def propagate_through_chain(self, confidences: List[float], 
                               methods: List[str]) -> dict:
        # Return distribution, not just point estimate
        return {
            "mean": 0.73,
            "std": 0.12,
            "95_ci": [0.61, 0.85],
            "method": "monte_carlo"
        }
```

## Advanced Capabilities (Priority Order)

### 1. Temporal Reasoning (HIGH)
- Handle temporal paradoxes
- Multi-timeline representation
- Semantic drift over time
- Temporal validity of facts

### 2. Causal Preservation (HIGH)
- Maintain causal structure in all transformations
- Distinguish confounders from mediators
- Support counterfactual analysis
- Enable causal inference

### 3. Multi-Language Support (MEDIUM)
- Entities with names in multiple languages
- Cross-language entity resolution
- Cultural context preservation

### 4. Absence Analysis (MEDIUM)
- Represent negative relationships
- Prove something didn't happen
- Confidence decay for absence claims

### 5. Knowledge Evolution (MEDIUM)
- Detect paradigm shifts
- Track consensus changes
- Version knowledge over time

### 6. Adversarial Robustness (LOW for prototype)
- Detect anomalous data injection
- Source credibility scoring
- Defensive analysis modes

## Excluded from Initial Version

Based on PhD thesis scope:

1. **Collaborative Features**
   - Multi-user concurrent editing
   - Consensus building workflows
   - Branch-based analysis

2. **Extreme Scale**
   - Handling 10M+ node graphs in memory
   - Real-time processing requirements
   - Distributed computing

3. **Production Features**
   - User authentication
   - Advanced security
   - High availability

## Implementation Priority

### Phase 1: Core Infrastructure (Must Have)
1. Three-level identity system
2. Base data schemas with quality/provenance
3. Core services (Identity, Provenance, Quality)
4. Reference-based data flow
5. Format transformation tools

### Phase 2: Essential Processing (Should Have)
1. Streaming support
2. Uncertainty propagation
3. Partial results handling
4. Temporal reasoning basics
5. Causal structure preservation

### Phase 3: Advanced Features (Nice to Have)
1. Multi-language support
2. Absence analysis
3. Knowledge evolution tracking
4. Semantic drift handling
5. Advanced explanation generation

## Success Criteria

The system will be considered successful if it can:

1. **Handle all analytical methods** from the comprehensive taxonomy
2. **Maintain complete provenance** for PhD reproducibility
3. **Track quality/confidence** throughout pipeline
4. **Transform between formats** as needed by analysis
5. **Explain its reasoning** with sufficient detail

## Key Design Decisions

1. **Attribute-based flexibility** over rigid schemas
2. **Quality-aware processing** at every step
3. **Reference-based architecture** for scalability
4. **Format agnostic** - right structure for right task
5. **Provenance-first** design for academic rigor

This synthesis captures the essential requirements discovered through 37 mock workflows while maintaining focus on the PhD thesis goals.