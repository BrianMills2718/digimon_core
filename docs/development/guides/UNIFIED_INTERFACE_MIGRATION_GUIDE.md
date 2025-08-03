# Unified Tool Interface Migration Guide

## Overview
All KGAS tools have been migrated to use a unified interface based on the `ToolRequest` and `ToolResult` pattern.
This guide helps you update your code to use the new interface.

## Migration Pattern

### Old Interface (DEPRECATED)
```python
# DON'T DO THIS - Old method-based interface
loader = PDFLoader(service_manager)
result = loader.load_pdf("document.pdf", workflow_id="wf_123")

chunker = TextChunker(service_manager)
result = chunker.chunk_text(document_ref, text_content, confidence=0.8)

ner = SpacyNER(service_manager)
result = ner.extract_entities(chunk_ref, chunk_text, confidence=0.8)
```

### New Unified Interface (CORRECT)
```python
# DO THIS - Unified interface with ToolRequest
from src.tools.base_tool import ToolRequest

# T01: PDF Loader
loader = PDFLoader(service_manager)
request = ToolRequest(
    tool_id="T01",
    operation="load_document",
    input_data={
        "file_path": "document.pdf",
        "workflow_id": "wf_123"
    },
    parameters={}
)
result = loader.execute(request)

# T15A: Text Chunker
chunker = TextChunker(service_manager)
request = ToolRequest(
    tool_id="T15A",
    operation="chunk_text",
    input_data={
        "document_ref": document_ref,
        "text": text_content,
        "confidence": 0.8
    },
    parameters={
        "chunk_size": 512,
        "overlap": 50
    }
)
result = chunker.execute(request)

# T23A: spaCy NER
ner = SpacyNER(service_manager)
request = ToolRequest(
    tool_id="T23A",
    operation="extract_entities",
    input_data={
        "chunk_ref": chunk_ref,
        "text": chunk_text,
        "confidence": 0.8
    },
    parameters={
        "confidence_threshold": 0.7
    }
)
result = ner.execute(request)
```

## Tool Request Structure

```python
@dataclass(frozen=True)
class ToolRequest:
    tool_id: str              # Tool identifier (e.g., "T01", "T15A")
    operation: str            # Operation to perform
    input_data: Any           # Required input data (dict)
    parameters: Dict[str, Any] # Optional parameters
    context: Optional[Dict[str, Any]] = None
    validation_mode: bool = False
```

## Tool Result Structure

```python
@dataclass(frozen=True)
class ToolResult:
    tool_id: str              # Tool that produced result
    status: str               # "success" or "error"
    data: Any                 # Result data (None if error)
    metadata: Dict[str, Any]  # Additional metadata
    execution_time: float     # Execution time in seconds
    memory_used: int          # Memory used in bytes
    error_code: Optional[str] # Error code if failed
    error_message: Optional[str] # Error message if failed
```

## Migration Steps

1. **Update imports**
   ```python
   from src.tools.base_tool import ToolRequest, ToolResult
   ```

2. **Replace method calls with execute()**
   - Find: `tool.method_name(args)`
   - Replace: `tool.execute(ToolRequest(...))`

3. **Map parameters to input_data and parameters**
   - Required params → `input_data`
   - Optional params → `parameters`

4. **Handle results consistently**
   - Check `result.status == "success"`
   - Access data via `result.data`
   - Handle errors via `result.error_code` and `result.error_message`

## Tool-Specific Migration

### T01: PDF Loader
```python
# Old
result = loader.load_pdf(file_path, workflow_id)

# New
request = ToolRequest(
    tool_id="T01",
    operation="load_document",
    input_data={"file_path": file_path, "workflow_id": workflow_id},
    parameters={}
)
result = loader.execute(request)
```

### T15A: Text Chunker
```python
# Old
result = chunker.chunk_text(document_ref, text, confidence)

# New
request = ToolRequest(
    tool_id="T15A",
    operation="chunk_text",
    input_data={
        "document_ref": document_ref,
        "text": text,
        "confidence": confidence
    },
    parameters={"chunk_size": 512, "overlap": 50}
)
result = chunker.execute(request)
```

### T23A: spaCy NER
```python
# Old
result = ner.extract_entities(chunk_ref, text, confidence)

# New
request = ToolRequest(
    tool_id="T23A",
    operation="extract_entities",
    input_data={
        "chunk_ref": chunk_ref,
        "text": text,
        "confidence": confidence
    },
    parameters={"confidence_threshold": 0.7}
)
result = ner.execute(request)
```

### T27: Relationship Extractor
```python
# Old
result = extractor.extract_relationships(chunk_ref, text, entities, confidence)

# New
request = ToolRequest(
    tool_id="T27",
    operation="extract_relationships",
    input_data={
        "chunk_ref": chunk_ref,
        "text": text,
        "entities": entities,
        "confidence": confidence
    },
    parameters={}
)
result = extractor.execute(request)
```

### T31: Entity Builder
```python
# Old
result = builder.build_entities(mentions, source_refs)

# New
request = ToolRequest(
    tool_id="T31",
    operation="build_entities",
    input_data={
        "mentions": mentions,
        "source_refs": source_refs
    },
    parameters={}
)
result = builder.execute(request)
```

### T34: Edge Builder
```python
# Old
result = builder.build_edges(relationships, source_refs)

# New
request = ToolRequest(
    tool_id="T34",
    operation="build_edges",
    input_data={
        "relationships": relationships,
        "source_refs": source_refs
    },
    parameters={}
)
result = builder.execute(request)
```

### T68: PageRank
```python
# Old
result = calculator.calculate_pagerank(graph_ref)

# New
request = ToolRequest(
    tool_id="T68",
    operation="calculate_pagerank",
    input_data={"graph_ref": graph_ref},
    parameters={
        "damping_factor": 0.85,
        "max_iterations": 100
    }
)
result = calculator.execute(request)
```

### T49: Multi-hop Query
```python
# Old
result = query_engine.query_graph(question, max_hops=2)

# New
request = ToolRequest(
    tool_id="T49",
    operation="query_graph",
    input_data={"question": question},
    parameters={"max_hops": 2}
)
result = query_engine.execute(request)
```

## Common Patterns

### Error Handling
```python
result = tool.execute(request)

if result.status == "success":
    # Process successful result
    data = result.data
    print(f"Success: {data}")
else:
    # Handle error
    print(f"Error {result.error_code}: {result.error_message}")
```

### Tool Chaining
```python
# Chain tools by passing output of one as input to next
t01_result = loader.execute(t01_request)
if t01_result.status == "success":
    document = t01_result.data['document']
    
    t15a_request = ToolRequest(
        tool_id="T15A",
        operation="chunk_text",
        input_data={
            "document_ref": document['document_ref'],
            "text": document['text'],
            "confidence": document['confidence']
        },
        parameters={}
    )
    t15a_result = chunker.execute(t15a_request)
```

### Validation Mode
```python
# Test if input is valid without executing
request = ToolRequest(
    tool_id="T01",
    operation="load_document",
    input_data={"file_path": "test.pdf"},
    parameters={},
    validation_mode=True  # Only validate, don't execute
)
result = loader.execute(request)
```

## Benefits of Unified Interface

1. **Consistency**: All tools use same interface pattern
2. **Discoverability**: Tool contracts document all operations
3. **Validation**: Built-in input/output validation
4. **Monitoring**: Standardized performance tracking
5. **Error Handling**: Consistent error codes and messages
6. **Orchestration**: Easier to build tool chains and workflows

## Testing Your Migration

Run the migration test to verify your updates:
```bash
python test_unified_interface_migration.py
```

This will test all tools with the unified interface and report any issues.
