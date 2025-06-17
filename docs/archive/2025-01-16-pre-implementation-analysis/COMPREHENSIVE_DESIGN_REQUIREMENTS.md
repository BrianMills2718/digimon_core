# Comprehensive Design Requirements from Mock Workflows

## Critical Discoveries from All Mock Workflows

### 1. **Three-Level Identity System (CRITICAL)**

We need THREE levels of identification, not just entity IDs:

```python
# Level 1: Surface Form (what appears in text)
"Apple", "Cambridge", "PowerWidget Pro"

# Level 2: Mention (specific occurrence)
{
  "mention_id": "mention_001",
  "surface_text": "Apple",
  "document_id": "doc_001", 
  "position": 1234,
  "context": "Apple announced record iPhone sales"
}

# Level 3: Entity (canonical resolved entity)
{
  "entity_id": "ent_apple_inc_001",
  "canonical_name": "Apple Inc.",
  "surface_forms": ["Apple", "AAPL", "Apple Computer"],
  "type": "ORG"
}
```

**Why this matters**: 
- Same surface form → multiple entities (Apple Inc. vs apple fruit)
- Same entity → multiple surface forms (Apple, AAPL)
- Need to track specific mentions for provenance

### 2. **Universal Quality/Confidence Tracking**

EVERY data object needs quality indicators:

```python
class QualityAware:
    confidence: float  # 0.0 to 1.0
    quality_tier: Enum["high", "medium", "low"]
    extraction_method: str
    evidence: List[str]
    warnings: List[str]
```

Examples:
- Document: OCR quality, corruption status
- Entity: Extraction confidence, disambiguation score
- Relationship: Evidence strength, source agreement
- Analysis: Exact vs approximate, sample size

### 3. **Comprehensive Versioning System**

Four types of versioning needed:

```python
# 1. Schema Versioning
{
  "schema_version": "1.2",
  "migration_from": "1.1",
  "new_fields": ["language"],
  "deprecated_fields": []
}

# 2. Data Versioning  
{
  "entity_id": "ent_apple_001",
  "version": 3,
  "valid_from": "2024-01-15",
  "previous_version": 2,
  "change_reason": "Revenue correction"
}

# 3. Graph Versioning
{
  "graph_id": "company_network",
  "version": "v2024_01_15",
  "parent_version": "v2024_01_01",
  "nodes_added": 127,
  "nodes_modified": 89
}

# 4. Analysis Versioning
{
  "analysis_id": "market_analysis_001",
  "version": 2,
  "based_on_data_version": "v2024_01_15",
  "supercedes": "market_analysis_001_v1"
}
```

### 4. **Streaming-First Architecture**

Most tools need streaming variants:

```python
# Traditional (memory limited)
def process_all(documents: List[Document]) -> List[Entity]:
    return extract_entities(documents)

# Streaming (scalable)
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

### 5. **Conflict Resolution Framework**

Multiple values for same fact is common:

```python
class ConflictResolver:
    strategies = [
        "source_hierarchy",    # Primary sources win
        "recency",            # Newest wins
        "consensus",          # Majority wins
        "confidence_weighted" # Highest confidence wins
    ]
    
    def resolve(self, conflicts, strategy="source_hierarchy"):
        # Return primary + preserve alternatives
        return {
            "selected_value": best_value,
            "confidence": computed_confidence,
            "alternatives": other_values,
            "resolution_method": strategy
        }
```

### 6. **Provenance and Lineage Tracking**

Every operation must record:

```python
{
  "operation_id": "op_001",
  "tool": "T23",
  "inputs": ["doc_001", "doc_002"],
  "outputs": ["ent_001", "ent_002"],
  "parameters": {...},
  "timestamp": "2024-01-15T10:00:00Z",
  "workflow_id": "wf_001",
  "upstream_ops": ["op_000"],
  "downstream_ops": ["op_002"],
  "invalidated_by": null  # Set if input data changes
}
```

### 7. **Progressive Processing Patterns**

Support for:
- Checkpointing (save state between phases)
- Partial results (some succeed, some fail)
- Incremental updates (add new data without full reprocess)
- Recovery (resume from failure point)

### 8. **Cross-Format Entity Consistency**

Entity must be findable regardless of storage:

```python
class EntityRegistry:
    def register_entity(entity_id: str, locations: List[StorageRef]):
        """
        Track where entity exists:
        - Neo4j: node with id=entity_id
        - SQLite: rows with entity_id foreign key
        - FAISS: vectors with metadata.entity_id
        """
    
    def get_entity_locations(entity_id: str) -> List[StorageRef]:
        """Find entity across all storage systems"""
```

## Required Components Before Implementation

### 1. **Core Services**

```python
# a) Identity Service
class IdentityService:
    def create_mention(surface_text, context) -> mention_id
    def resolve_mention(mention_id) -> entity_id
    def create_entity(canonical_name, type) -> entity_id
    def merge_entities(entity_ids) -> merged_entity_id
    def get_all_mentions(entity_id) -> List[mention_id]

# b) Version Service  
class VersionService:
    def create_version(object_type, object_id, changes)
    def get_version_history(object_id)
    def rollback_version(object_id, target_version)
    def diff_versions(v1, v2)

# c) Provenance Service
class ProvenanceService:
    def record_operation(tool, inputs, outputs, params)
    def trace_lineage(object_id) -> dependency_graph
    def find_affected_by_change(changed_object_id)
    def invalidate_downstream(object_id)

# d) Quality Service
class QualityService:
    def assess_confidence(object, method) -> float
    def assign_tier(confidence) -> QualityTier
    def propagate_confidence(upstream_conf, operation) -> downstream_conf
    def aggregate_confidence(multiple_sources) -> combined_conf
```

### 2. **Storage Abstractions**

```python
# Unified storage interface
class StorageManager:
    def store(object_id, object_data, storage_type):
        if storage_type == "graph":
            return self.neo4j.store(object_id, object_data)
        elif storage_type == "table":
            return self.sqlite.store(object_id, object_data)
        elif storage_type == "vector":
            return self.faiss.store(object_id, object_data)
    
    def retrieve(object_id) -> (object_data, storage_type):
        # Check all stores
        
    def query_cross_store(query) -> results:
        # Federated query across stores
```

### 3. **Data Schemas with All Requirements**

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
    quality_tier: QualityTier
    warnings: List[str]
    
    # Provenance  
    created_by: str  # tool_id
    source_refs: List[str]
    evidence: List[str]
    
    # Workflow
    workflow_id: str
    operation_id: str

@dataclass
class Entity(BaseObject):
    # Core attributes
    canonical_name: str
    entity_type: str
    
    # Flexibility
    attributes: Dict[str, Any]  # Domain-specific
    
    # Disambiguation
    surface_forms: List[str]
    disambiguation_score: float
    alternative_entities: List[Tuple[str, float]]
    
    # Optional enrichments
    description: Optional[str]
    embedding: Optional[List[float]]

@dataclass  
class Mention:
    mention_id: str
    surface_text: str
    document_ref: str
    position: int
    context_window: str
    entity_candidates: List[Tuple[str, float]]
    selected_entity: str
```

## Pre-Implementation Checklist

### ✅ Must Have Before Coding

1. **Complete Data Schemas** (3 days)
   - [ ] All object types defined
   - [ ] Required vs optional fields clear
   - [ ] Validation rules specified
   - [ ] Serialization formats defined

2. **Service Specifications** (2 days)
   - [ ] Identity Service API
   - [ ] Version Service API  
   - [ ] Provenance Service API
   - [ ] Quality Service API

3. **Storage Patterns** (2 days)
   - [ ] Cross-store query patterns
   - [ ] Reference vs embedding patterns
   - [ ] Streaming storage patterns
   - [ ] Transaction boundaries

4. **Tool Compatibility Matrix** (3 days)
   - [ ] Input/output schemas per tool
   - [ ] Streaming capabilities marked
   - [ ] Quality degradation rules
   - [ ] Recovery capabilities

5. **Workflow Patterns** (2 days)
   - [ ] Checkpoint specifications
   - [ ] Error handling patterns
   - [ ] Partial result handling
   - [ ] Update cascade patterns

### 🎯 Implementation Order

1. **Phase 0**: Core services + schemas
2. **Phase 1**: Basic tools with full service integration  
3. **Phase 2**: Streaming + quality tracking
4. **Phase 3**: Versioning + provenance
5. **Phase 4**: Advanced patterns

## Summary

The mock workflows revealed that Super-Digimon needs:
- **Complex identity management** (surface → mention → entity)
- **Pervasive quality tracking** (confidence everywhere)
- **Comprehensive versioning** (schema, data, graph, analysis)
- **Streaming-first design** (handle any scale)
- **Graceful degradation** (partial > nothing)
- **Full provenance** (trace everything)

This is more complex than initially envisioned, but the architecture can handle it. The key is building the right abstractions and services before diving into tool implementation.