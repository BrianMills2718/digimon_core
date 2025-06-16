# Tool Data Compatibility Matrix

**CRITICAL GAP IDENTIFIED**: Our current specifications don't define data requirements or compatibility between tools. This document proposes how to fix this.

## Core Data Types (Proposed)

### 1. Entity
```python
Entity = {
    "id": str,                    # Required: Unique identifier
    "name": str,                  # Required: Display name
    "type": str | None,           # Optional: Entity type (Person, Place, etc.)
    "description": str | None,    # Optional: Detailed description
    "attributes": dict | None,    # Optional: Custom attributes
    "embedding": list[float] | None, # Optional: Vector representation
    "source_ref": str | None      # Optional: Reference to source document/chunk
}
```

### 2. Relationship
```python
Relationship = {
    "id": str,                    # Required: Unique identifier
    "source_id": str,             # Required: Source entity ID
    "target_id": str,             # Required: Target entity ID
    "type": str,                  # Required: Relationship type/name
    "weight": float | None,       # Optional: Edge weight
    "attributes": dict | None,    # Optional: Custom attributes
    "keywords": list[str] | None, # Optional: Associated keywords
    "description": str | None,    # Optional: Detailed description
    "embedding": list[float] | None # Optional: Vector representation
}
```

### 3. Chunk
```python
Chunk = {
    "id": str,                    # Required: Unique identifier
    "content": str,               # Required: Text content
    "source_doc": str,            # Required: Source document ID
    "position": int,              # Required: Position in document
    "entities": list[str] | None, # Optional: Entity IDs in chunk
    "relationships": list[str] | None, # Optional: Relationship IDs in chunk
    "embedding": list[float] | None, # Optional: Vector representation
    "metadata": dict | None       # Optional: Additional metadata
}
```

### 4. Graph
```python
Graph = {
    "nodes": list[Entity],        # Required: List of entities
    "edges": list[Relationship],  # Required: List of relationships
    "metadata": dict | None       # Optional: Graph-level metadata
}
```

### 5. Community
```python
Community = {
    "id": str,                    # Required: Unique identifier
    "entity_ids": list[str],      # Required: Member entity IDs
    "level": int,                 # Required: Hierarchy level
    "summary": str | None,        # Optional: Community description
    "keywords": list[str] | None, # Optional: Key terms
    "parent_id": str | None       # Optional: Parent community
}
```

## Tool Compatibility Matrix

### Phase 4: GraphRAG Operators (T49-T67)

| Tool | Required Input Attributes | Optional Attributes | Output Format | Compatible With |
|------|--------------------------|-------------------|---------------|-----------------|
| **T49: Entity VDB** | - query: str<br>- entities must have: `embedding` | - entities can use: `name`, `type`, `description` | List[Entity] with similarity scores | T51-T55, T63-T67 |
| **T50: RelNode** | - relationships must have: `source_id`, `target_id`, `type` | - can use: `weight`, `description` | List[Entity] | T51, T56-T59 |
| **T51: Local Search** | - entity must have: `id` | - can use: all Entity attributes | Graph (localized) | T53, T54, T63-T65 |
| **T52: Global Search** | - entities must have: `id`<br>- relationships must have: `source_id`, `target_id` | - can use: all attributes | Graph (full) | T53, T54, T63-T67 |
| **T53: Subgraph** | - entities must have: `id`<br>- relationships must have: `source_id`, `target_id` | - can use: all attributes | Graph (filtered) | T57, T58, T66, T67 |
| **T54: Path Finding** | - entities must have: `id`<br>- relationships must have: `source_id`, `target_id` | - can use: `weight` for shortest path | List[List[Entity]] (paths) | T57, T65 |
| **T55: Relation Extract** | - chunks must have: `content` | - can use: `entities`, `relationships` | List[Relationship] | T50, T53, T59 |
| **T56: Similarity** | - query: str<br>- items must have: `embedding` | - can use: any attributes | List[Any] with scores | T57, T58 |
| **T57: Answer Gen** | - chunks must have: `content` | - can use: `entities`, `relationships` | str (answer) | Terminal |
| **T58: Summarization** | - chunks must have: `content` | - can use: all Chunk attributes | str (summary) | Terminal |
| **T59: Relation VDB** | - relationships must have: `embedding` | - can use: `type`, `keywords` | List[Relationship] | T50, T53 |
| **T60: Chunk Aggregator** | - chunks must have: `content`<br>- relationships must have: scores | - can use: all attributes | List[Chunk] ranked | T57, T58 |
| **T61: Chunk FromRel** | - chunks must have: `relationships`<br>- relationships must have: `id` | - can use: all attributes | List[Chunk] | T57, T58 |
| **T62: Chunk Occurrence** | - chunks must have: `entities`<br>- entities must have: `id` | - can use: all attributes | List[Chunk] ranked | T57, T58 |
| **T63: KHopPath** | - entities must have: `id`<br>- relationships must have: `source_id`, `target_id` | - can use: `weight` | List[Graph] (paths) | T57, T65 |
| **T64: Steiner Tree** | - entities must have: `id`<br>- relationships must have: `source_id`, `target_id`, `weight` | - can use: all attributes | Graph (tree) | T57, T66 |
| **T65: AgentPath** | - paths from T54 or T63<br>- must have: serializable format | - can use: all attributes | List[Graph] filtered | T57 |
| **T66: Community Entity** | - communities must have: `entity_ids`<br>- entities must have: `id` | - can use: `level`, `summary` | List[Community] | T67 |
| **T67: Community Layer** | - communities must have: `level` | - can use: `parent_id`, `summary` | List[Community] | T66 |

## Attribute Compatibility Rules

### 1. Minimum Viable Graphs
```python
# Simplest KG (Knowledge Graph)
MinimalKG = {
    "entities": [{"id": "1", "name": "Obama"}],
    "relationships": [{"id": "r1", "source_id": "1", "target_id": "2", "type": "spouse"}]
}

# Rich TKG (Text + Knowledge Graph)  
RichTKG = {
    "entities": [
        {
            "id": "1",
            "name": "Obama",
            "type": "Person",
            "description": "44th President of the United States",
            "embedding": [0.1, 0.2, ...],
            "attributes": {"birth_year": 1961}
        }
    ],
    "relationships": [
        {
            "id": "r1",
            "source_id": "1",
            "target_id": "2",
            "type": "spouse",
            "description": "Married to",
            "weight": 1.0,
            "keywords": ["marriage", "family"]
        }
    ]
}
```

### 2. Tool Adaptation Rules

**Rule 1**: Tools MUST work with minimum required attributes
```python
# T51 (Local Search) MUST work with just:
entity = {"id": "1"}  # Minimum requirement

# But CAN use additional attributes if present:
entity = {"id": "1", "name": "Obama", "type": "Person"}  # Enhanced functionality
```

**Rule 2**: Tools SHOULD gracefully handle missing optional attributes
```python
def local_search(entity, graph):
    # Use name if available, fall back to ID
    label = entity.get("name", entity["id"])
    
    # Use weight if available, default to 1.0
    for edge in graph.edges:
        weight = edge.get("weight", 1.0)
```

**Rule 3**: Tools MUST declare what attributes they ADD to output
```python
# T39 (Text Embedding) adds:
output_entity = input_entity.copy()
output_entity["embedding"] = compute_embedding(input_entity["name"])
```

## Critical Missing Specifications

1. **Vector Dimension Consistency**: All embeddings must have same dimension
2. **ID Namespace Management**: How to ensure unique IDs across tools
3. **Attribute Preservation**: Which tools preserve vs drop attributes
4. **Error Handling**: What happens with missing required attributes
5. **Type Validation**: How to validate attribute types at runtime

## Recommendations for Documentation Update

1. **Add to each tool in SPECIFICATIONS.md**:
   - Required input attributes
   - Optional input attributes  
   - Output schema
   - Compatibility list

2. **Create data type definitions section**:
   - Standard data types (Entity, Relationship, etc.)
   - Minimum required attributes
   - Optional enhancement attributes

3. **Add compatibility matrix**:
   - Visual diagram of tool connections
   - Data flow examples
   - Common tool chains

4. **Include validation rules**:
   - Runtime checks for required attributes
   - Type validation
   - Graceful degradation strategies

This compatibility matrix should be a core part of our documentation to ensure tools work together seamlessly!