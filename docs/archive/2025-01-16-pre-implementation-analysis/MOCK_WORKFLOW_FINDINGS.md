# Key Findings from Mock Workflow Analysis

## Critical Design Validations

### 1. **Data Format Flexibility is Essential**
- **Example 1** (Company Analysis): Documents → Chunks → Graph → Table → Stats
- **Example 2** (Medical Research): JSON → Graph → Paths → Time Series Table
- **Example 3** (Customer Feedback): CSV → Table throughout (no graph needed!)
- **Example 4** (Causal Analysis): Multiple tables → Causal Graph → Table → Stats

**Key Insight**: The system truly needs to support fluid transitions between formats based on the analytical task, not force everything into graphs.

### 2. **Three-Database Architecture Validated**

```
SQLite: Perfect for:
- Document/chunk metadata
- Analysis results  
- Workflow provenance
- Structured tabular data

Neo4j: Perfect for:
- Entity/relationship networks
- Graph algorithms (PageRank, paths)
- Community structures

FAISS: Perfect for:
- Similarity search
- Clustering in vector space
- Scalable nearest neighbor
```

### 3. **Reference-Based Data Flow**
Instead of passing massive data:
```python
# Bad: Passing 25,000 chunks
output = {"chunks": [... 25,000 full text chunks ...]}

# Good: Passing references
output = {
    "chunk_refs": ["chunk_001_*", "chunk_002_*"],
    "count": 25000,
    "storage": "sqlite://chunks"
}
```

### 4. **Traceability Architecture**

Every operation needs:
```python
{
    "operation_id": "uuid",
    "tool": "T23",
    "timestamp": "ISO-8601",
    "input_refs": [...],
    "output_refs": [...],
    "parameters": {...},
    "metrics": {
        "records_processed": 1000,
        "execution_time": 1.23
    },
    "provenance": {
        "workflow_id": "wf_001",
        "step": 3,
        "confidence": 0.92
    }
}
```

### 5. **Entity ID Management**

Critical requirement discovered:
```python
# Entity created in T23 must maintain same ID through entire pipeline
T23: creates entity "ent_apple_001"
T25: updates same entity with coreference
T41: adds embedding to same entity  
T68: calculates PageRank for same entity

# Solution: UUID at creation, propagate everywhere
```

### 6. **Batch Processing Patterns**

For large data:
```python
# Process in chunks to avoid memory issues
for batch in chunk_iterator(chunks, batch_size=1000):
    entities = extract_entities(batch)
    store_entities(entities)
    yield entity_refs
```

### 7. **Format-Specific Tool Requirements**

Some tools MUST work with specific formats:
- PageRank (T68): Requires graph structure
- Statistical tests (T117): Requires tabular data
- Embedding generation (T41): Works with any text
- PyWhy integration: Requires both causal graph AND tabular data

## Schema Design Implications

### 1. **Core Data Types Needed**
Based on workflows, we need exactly these types:
- **Document**: Original ingested files
- **Chunk**: Text segments with position info
- **Entity**: Things (people, companies, drugs)
- **Relationship**: Connections between entities
- **Graph**: Collection of entities + relationships
- **Table**: Structured rows and columns
- **Embedding**: Vector representation
- **Analysis Result**: Statistical outputs, answers

### 2. **Required Metadata Attributes**

Every data object needs:
```python
{
    "id": str,                    # UUID for reference
    "type": str,                  # Data type name
    "created_at": datetime,       # When created
    "created_by": str,           # Which tool
    "workflow_id": str,          # Which workflow
    "provenance": {              # Where it came from
        "source_ids": [...],
        "confidence": float,
        "evidence": [...]
    }
}
```

### 3. **Tool Compatibility Rules**

Clear patterns emerged:
- **Ingestion tools** (T01-T12): Create Documents
- **Processing tools** (T13-T30): Documents → Chunks → Entities/Relations
- **Construction tools** (T31-T48): Build Graphs or Tables
- **Analysis tools** (T49-T106): Operate on Graphs/Tables/Vectors

### 4. **Critical Integration Points**

Where we need careful schema alignment:
1. **Entity extraction → Graph building**: Entity IDs must match
2. **Graph → Table conversion**: Preserve all attributes
3. **Multiple sources → Integration**: Common key fields
4. **Analysis results → Natural language**: Maintain citations

## Recommendations for Schema Design

### 1. **Start with Minimal Required Attributes**
Define only what's absolutely necessary for tools to function, let tools add optional attributes.

### 2. **Use Composition Over Inheritance**
Instead of complex type hierarchies:
```python
# Good: Composition
Entity = BaseObject + EntityAttributes
Chunk = BaseObject + ChunkAttributes

# Avoid: Deep inheritance
Entity > Person > Employee > Manager
```

### 3. **Design for Streaming**
Assume data might be too large for memory:
```python
# Tools should accept iterators
def process(self, chunks: Iterator[Chunk]) -> Iterator[Entity]:
    for chunk in chunks:
        yield extract_entities(chunk)
```

### 4. **Explicit Format Conversion Tools**
We need tools like T115 (Graph→Table) for every major format transition.

## Next Steps

With these findings, we can now create:
1. **Concrete data schemas** that support all workflow patterns
2. **Tool compatibility matrix** based on actual usage
3. **Validation rules** that ensure smooth data flow
4. **Performance guidelines** for large-scale processing