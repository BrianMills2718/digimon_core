# Operator Attribute Requirements

## Overview

This document specifies exactly what attributes each operator requires and how the compatibility system works.

## How Attribute Compatibility Works

```python
# Operators declare requirements
@operator(requires=["id", "embedding", "type"])
def entity_vdb_search(...):
    pass

# Graphs declare available attributes  
graph.attributes = ["id", "name", "embedding", "type", "created_at", "custom_field"]

# System checks: requires ⊆ available
can_run = all(attr in graph.attributes for attr in operator.requires)
```

## Entity Operators

### entity_vdb_search
**Requires**: `["id", "embedding"]`
**Optional**: `["name", "type"]`
**Why**: Need embeddings for similarity search

### entity_ppr
**Requires**: `["id"]`
**Optional**: `["weight"]`
**Why**: Only needs entity identifiers for PageRank

### entity_onehop_neighbors  
**Requires**: `["id"]`
**Optional**: `["type", "direction"]`
**Why**: Graph traversal only needs IDs

### entity_relnode_extract
**Requires**: `["id", "source_id", "target_id"]`
**Optional**: `["type"]`
**Why**: Needs relationship endpoint IDs

### entity_agent_find
**Requires**: `["id", "name"]`
**Optional**: `["description", "type"]`
**Why**: LLM needs human-readable info

### entity_similarity_link
**Requires**: `["id", "embedding"]`
**Optional**: `["type"]`
**Why**: Needs embeddings for similarity

### entity_tfidf_rank
**Requires**: `["id", "text_content"]`
**Optional**: `["type"]`
**Why**: Needs text for TF-IDF calculation

## Relationship Operators

### relationship_vdb_search
**Requires**: `["id", "embedding"]`
**Optional**: `["type", "source_id", "target_id"]`
**Why**: Need embeddings for similarity

### relationship_onehop_extract
**Requires**: `["source_id", "target_id"]`
**Optional**: `["type", "weight"]`
**Why**: Need endpoints for traversal

### relationship_score_aggregate  
**Requires**: `["source_id", "target_id"]`
**Optional**: `["weight", "type"]`
**Why**: Aggregates scores from endpoints

### relationship_agent_find
**Requires**: `["source_id", "target_id", "type"]`
**Optional**: `["description"]`
**Why**: LLM needs context

## Chunk Operators

### chunk_score_aggregate
**Requires**: `["id", "relationship_ids"]`
**Optional**: `["score", "content"]`
**Why**: Maps chunks to relationships

### chunk_from_relationships
**Requires**: `["id", "content", "entity_ids"]`
**Optional**: `["position", "source"]`
**Why**: Need content and entity links

### chunk_entity_occurrence
**Requires**: `["id", "entity_ids"]`
**Optional**: `["content"]`
**Why**: Count entity mentions

## Special Cases

### Graph Type Compatibility

Some operators only work with certain graph structures:

```python
# ChunkTree - nodes ARE chunks
if graph.type == "ChunkTree":
    # These operators won't work
    incompatible = ["chunk_from_relationships", "chunk_entity_occurrence"]
    # Because chunks don't link to entities, they ARE the entities

# PassageGraph - nodes ARE passages  
if graph.type == "PassageGraph":
    # Similar restrictions
    incompatible = ["chunk_score_aggregate"]
```

### Handling Missing Attributes

```python
# Option 1: Fail gracefully
if "embedding" not in graph.attributes:
    raise AttributeError("entity_vdb_search requires embeddings")

# Option 2: Degrade functionality
if "type" not in graph.attributes:
    # Search without type filtering
    results = search_all_entities(query)

# Option 3: Compute on-demand
if "embedding" not in entity:
    entity["embedding"] = compute_embedding(entity["name"])
```

## Attribute Definitions

### Core Attributes (Usually Required)
- `id`: Unique identifier
- `embedding`: Vector representation
- `name`: Human-readable name
- `type`: Category (Person, Organization, etc.)

### Relationship Attributes
- `source_id`: Starting entity ID
- `target_id`: Ending entity ID  
- `weight`: Connection strength
- `direction`: directed/undirected

### Content Attributes
- `content`: Full text
- `text_content`: Processable text
- `position`: Location in source
- `source`: Origin document

### Metadata Attributes
- `created_at`: Timestamp
- `confidence`: Extraction confidence
- `description`: Long-form text

## Best Practices

1. **Declare Minimal Requirements**
   ```python
   # Good: Only what's essential
   requires = ["id", "embedding"]
   
   # Bad: Everything you might use
   requires = ["id", "embedding", "type", "name", "description"]
   ```

2. **Handle Optional Attributes**
   ```python
   # Use get() with defaults
   entity_type = entity.get("type", "Unknown")
   ```

3. **Document Why**
   ```python
   @operator(
       requires=["id", "embedding"],
       why="Need embeddings for vector similarity search"
   )
   ```

4. **Validate Early**
   ```python
   def validate_graph(graph, operator):
       missing = set(operator.requires) - set(graph.attributes)
       if missing:
           raise ValueError(f"Missing attributes: {missing}")
   ```

## Common Patterns

### Search Operators
Usually need: `["id", "embedding"]`

### Traversal Operators  
Usually need: `["id"]` or `["source_id", "target_id"]`

### Aggregation Operators
Usually need: `["id", "score"]` or similar

### LLM-based Operators
Usually need: `["id", "name", "description"]` - human-readable content

This system ensures operators work across different graph types while maintaining clear requirements.