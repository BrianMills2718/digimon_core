# Super-Digimon Design Principles

## 1. Tool Configurability

**Principle**: All tools must accept configurable parameters with sensible defaults.

### ✅ Good Example:
```python
def build_entity_nodes(
    self,
    algorithm: str = "louvain",
    weight_threshold: float = 3.0,      # Configurable
    max_iterations: int = 10,           # Configurable
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

### ❌ Bad Example:
```python
# Hardcoded values buried in implementation
WHERE total_weight > 3.0  # NEVER DO THIS
for iteration in range(20):  # NEVER DO THIS
```

## 2. Error Recovery

**Principle**: Tools should return partial results rather than failing completely.

### ✅ Good Example:
```python
return {
    "status": "partial",
    "entities_processed": 45,
    "entities_failed": 5,
    "data": processed_entities,
    "errors": error_details
}
```

### ❌ Bad Example:
```python
raise Exception("Processing failed")  # Loses all work
```

## 3. Database Entity Requirements

**Principle**: Entities created in any context must have all required fields.

### ✅ Good Example:
```python
CREATE (e:Entity {
    id: $id,
    name: $name,
    entity_type: $type,
    created_at: datetime(),  # Always include
    updated_at: datetime()   # Always include
})
```

### ❌ Bad Example:
```python
CREATE (e:Entity {id: 'test', name: 'Test'})  # Missing timestamps
```

## 4. Tool Contract Adherence

**Principle**: Implementation must match specification exactly.

### Issues Found:
- T31 spec says "create entity nodes" but implementation does community detection
- T41 assumes entities have text content (not in spec)
- T94 only handles 25% of queries successfully

## 5. Testing Patterns

**Principle**: Use real databases in tests, not mocks.

### ✅ Good Example:
```python
# Real Neo4j container
from testcontainers.neo4j import Neo4jContainer
neo4j = Neo4jContainer("neo4j:5-community")
```

### ❌ Bad Example:
```python
# Mocked database
mock_neo4j = Mock(spec=GraphDatabase)
```

## 6. Attribute-Based Design

**Principle**: Tools work with entity attributes, not fixed types.

### ✅ Good Example:
```python
# Check for required attributes
if 'pagerank_score' in entity.attributes:
    # Process PageRank logic
```

### ❌ Bad Example:
```python
# Hardcoded type checking
if entity.type == "ResearchPaper":
    # Too specific!
```

## 7. Cross-Database References

**Principle**: Use consistent reference format across all databases.

### Format:
```
neo4j://entity/ent_123
sqlite://document/doc_456
faiss://embedding/emb_789
```

## 8. Quality Propagation

**Principle**: Track confidence/quality through every operation.

### ✅ Good Example:
```python
output_confidence = input_confidence * 0.95  # Degradation
result['confidence'] = min(output_confidence, 1.0)
result['quality_tier'] = self._calculate_tier(output_confidence)
```

## 9. Observability

**Principle**: Every operation should be traceable.

### Required Metadata:
- `duration_ms`: Execution time
- `warnings`: Non-fatal issues
- `entity_count`: Items processed
- `algorithm`: Method used
- `parameters`: Config values used

## 10. Graceful Degradation

**Principle**: System should work with missing components.

### Examples:
- No embeddings? Fall back to graph-only search
- LLM unavailable? Use NLP extraction
- Community detection fails? Continue without communities