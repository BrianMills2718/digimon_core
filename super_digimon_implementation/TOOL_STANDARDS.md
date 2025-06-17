# Tool Implementation Standards

## Overview
This document defines the standards and patterns that ALL Super-Digimon tools must follow.

## 1. Configurability Requirements

### MUST Have Configurable Parameters
Every algorithmic parameter MUST be configurable with sensible defaults:

```python
# ✅ GOOD - Configurable
def process(self, data: str, threshold: float = 0.7):
    if score > threshold:
        # ...

# ❌ BAD - Hardcoded
def process(self, data: str):
    if score > 0.7:  # NEVER DO THIS
        # ...
```

### Common Configurable Parameters
- `threshold`: Confidence/similarity thresholds (default: 0.5-0.8)
- `max_iterations`: Algorithm iteration limits (default: 10-100)
- `batch_size`: Processing batch sizes (default: 100-1000)
- `algorithm`: Algorithm selection (default: "default")
- `timeout_ms`: Operation timeouts (default: 30000)
- `top_k`: Result limiting (default: 10-100)

## 2. Response Format Standards

### Every Tool Response MUST Include:

```python
{
    "status": "success" | "partial" | "error",
    # Primary output fields
    "entities": [...],           # Example primary output
    "entity_count": 42,          # Count of primary output
    
    # Error handling (if applicable)
    "failed_items": [...],       # What failed
    "errors": ["error1", ...],   # Error messages (max 5)
    
    # Quality tracking
    "quality_score": 0.85,       # Overall quality
    "confidence": 0.9,           # Operation confidence
    
    # Required metadata
    "metadata": {
        "duration_ms": 1234,     # REQUIRED: Execution time
        "algorithm": "louvain",  # What algorithm was used
        "parameters": {          # What parameters were used
            "threshold": 0.7,
            "max_iterations": 10
        },
        "warnings": [...],       # Non-fatal issues
        "provenance_id": "...", # Tracking ID
        "timestamp": "..."       # When executed
    }
}
```

## 3. Error Handling Patterns

### Return Partial Results
```python
try:
    results = process_all_items(items)
except Exception as e:
    # Don't lose everything!
    return {
        "status": "partial",
        "processed": results_so_far,
        "failed": failed_items,
        "errors": [str(e)]
    }
```

### Never Raise Exceptions at Top Level
```python
# ✅ GOOD
def tool_method(self, ...):
    try:
        # implementation
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ❌ BAD
def tool_method(self, ...):
    # implementation that might raise
    raise ValueError("Something went wrong")  # DON'T DO THIS
```

## 4. Database Entity Requirements

### Always Include Required Fields
```python
# When creating entities in Neo4j
CREATE (e:Entity {
    id: $id,
    name: $name,
    entity_type: $type,
    created_at: datetime(),      # REQUIRED
    updated_at: datetime(),      # REQUIRED
    confidence: $confidence      # REQUIRED
})
```

### Handle Missing Fields Gracefully
```python
# In entity loading/processing
entity_name = entity.get('name', entity.get('id', 'Unknown'))
confidence = entity.get('confidence', 0.5)  # Default confidence
```

## 5. Testing Requirements

### Every Tool MUST Have:

1. **Configurability Test**
```python
def test_tool_configurability():
    # Test with different parameters
    result1 = tool.process(data, threshold=0.3)
    result2 = tool.process(data, threshold=0.9)
    assert result1 != result2  # Parameters affect behavior
```

2. **Error Recovery Test**
```python
def test_error_recovery():
    # Test with data that causes partial failure
    result = tool.process(mixed_good_bad_data)
    assert result['status'] == 'partial'
    assert len(result['processed']) > 0
    assert len(result['failed']) > 0
```

3. **Metadata Test**
```python
def test_metadata_presence():
    result = tool.process(data)
    assert 'metadata' in result
    assert 'duration_ms' in result['metadata']
    assert 'parameters' in result['metadata']
```

## 6. Documentation Requirements

### Tool Docstring Template
```python
def tool_method(self, ...):
    """Brief description (one line).
    
    Detailed description of what the tool does and when to use it.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: value)
        
    Returns:
        Dictionary containing:
        - field1: Description
        - field2: Description
        - metadata: Execution metadata
        
    Example:
        >>> tool = ToolClass(db)
        >>> result = tool.method(data)
        >>> print(result['status'])
        'success'
    """
```

## 7. Performance Considerations

### Batch Processing Pattern
```python
# Process in batches to avoid memory issues
for i in range(0, total_items, batch_size):
    batch = items[i:i + batch_size]
    try:
        process_batch(batch)
    except Exception as e:
        # Log but continue with next batch
        logger.warning(f"Batch {i} failed: {e}")
```

### Progress Reporting
```python
# For long operations, report progress
if i % 1000 == 0:
    logger.info(f"Processed {i}/{total_items} items")
```

## 8. Integration Patterns

### Cross-Database References
```python
# Use consistent format
entity_ref = "neo4j://entity/ent_123"
doc_ref = "sqlite://document/doc_456"
embed_ref = "faiss://embedding/emb_789"
```

### Tool Chaining
```python
# Tools should accept outputs from other tools
chunk_result = chunker.process(doc_ref)
entity_result = extractor.process(chunk_result['chunk_refs'][0])
```

## 9. Quality Tracking

### Propagate Quality Scores
```python
# Quality degrades through pipeline
output_quality = input_quality * quality_factor
result['quality_score'] = min(output_quality, 1.0)
```

### Track Confidence
```python
# Be honest about confidence
if missing_critical_data:
    confidence *= 0.5
result['confidence'] = confidence
```

## 10. Common Pitfalls to Avoid

1. **Hardcoded Thresholds**: Always make them parameters
2. **Silent Failures**: Always return status and errors
3. **Missing Metadata**: Always include timing and parameters
4. **Type Assumptions**: Check types, don't assume
5. **All-or-Nothing**: Return partial results when possible
6. **Ignored Warnings**: Collect and return warnings
7. **Resource Leaks**: Close connections in finally blocks
8. **Unbounded Operations**: Always have limits/timeouts