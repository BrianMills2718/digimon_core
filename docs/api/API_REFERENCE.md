---
status: living
---

# KGAS API Reference

## /query Endpoint

The `/query` endpoint provides a unified interface for querying the KGAS knowledge graph using a JSON-based DSL or GraphQL.

### HTTP Endpoint
- **POST /query**
- **Content-Type**: application/json

### JSON DSL Grammar
```json
{
  "select": ["entity", "relationship"],
  "where": {
    "entity_type": "Person",
    "property": {"name": "Alice"}
  },
  "limit": 10,
  "order_by": "confidence",
  "desc": true
}
```
- **select**: List of result types ("entity", "relationship")
- **where**: Filter conditions (entity type, properties, relationship type, etc.)
- **limit**: Max results
- **order_by**: Field to sort by (e.g., "confidence")
- **desc**: Sort descending if true

### Example Query
```json
{
  "select": ["relationship"],
  "where": {
    "relationship_type": "IdentifiesWith",
    "confidence": {"$gte": 0.8}
  },
  "limit": 5
}
```

### GraphQL Support
- The API also supports GraphQL queries via Strawberry (see /graphql endpoint).
- Example:
```graphql
query {
  relationships(type: "IdentifiesWith", minConfidence: 0.8) {
    source { name }
    target { name }
    confidence
  }
}
```

### Response Format
```json
{
  "results": [
    {"entity_id": "123", "name": "Alice", ...},
    ...
  ],
  "count": 2
}
```

---

## MCP (Model Context Protocol) Endpoints

KGAS exposes all core services and tools via the Model Context Protocol (MCP), enabling agent orchestration and tool composition.

### MCP Server Configuration
- **Server Name**: `super-digimon`
- **Default Port**: Auto-configured
- **Tools Available**: 33+ tools across 4 core services + Phase 1 pipeline

### Core Service Tools

#### T107: Identity Service Tools
Manage entity mentions and identity resolution:

```python
# Create mention and link to entity
create_mention(
    surface_form="John Smith",
    start_pos=0,
    end_pos=10,
    source_ref="storage://document/doc123",
    entity_type="PERSON",
    confidence=0.85
)

# Get entity by mention
get_entity_by_mention(mention_id="mention_456")

# Get all mentions for entity
get_mentions_for_entity(entity_id="entity_789")

# Merge duplicate entities
merge_entities(entity_id1="entity_123", entity_id2="entity_456")

# Get identity service statistics
get_identity_stats()
```

#### T110: Provenance Service Tools
Track operation lineage and data provenance:

```python
# Start operation tracking
operation_id = start_operation(
    tool_id="T23A_SPACY_NER",
    operation_type="extract_entities",
    inputs=["storage://chunk/chunk123"],
    parameters={"model": "en_core_web_sm"}
)

# Complete operation
complete_operation(
    operation_id=operation_id,
    outputs=["storage://mention/mention456"],
    success=True,
    metadata={"entities_extracted": 5}
)

# Get lineage chain
get_lineage(object_ref="storage://entity/entity789", max_depth=10)

# Get operation details
get_operation_details(operation_id=operation_id)

# Get operations for object
get_operations_for_object(object_ref="storage://entity/entity789")

# Get tool usage statistics
get_tool_statistics()
```

#### T111: Quality Service Tools
Assess and track confidence scores:

```python
# Assess confidence for object
assess_confidence(
    object_ref="storage://entity/entity789",
    base_confidence=0.85,
    factors={"length_factor": 0.9, "type_confidence": 0.8},
    metadata={"extraction_method": "spacy_ner"}
)

# Propagate confidence through operations
propagate_confidence(
    input_refs=["storage://chunk/chunk123"],
    operation_type="entity_extraction",
    boost_factor=1.0
)

# Get quality assessment
get_quality_assessment(object_ref="storage://entity/entity789")

# Get confidence trend
get_confidence_trend(object_ref="storage://entity/entity789")

# Filter by quality criteria
filter_by_quality(
    object_refs=["entity1", "entity2", "entity3"],
    min_tier="MEDIUM",
    min_confidence=0.7
)

# Get quality statistics
get_quality_statistics()
```

#### T121: Workflow State Service Tools
Manage workflow checkpoints and state:

```python
# Start workflow tracking
workflow_id = start_workflow(
    name="PDF Entity Extraction",
    total_steps=5,
    initial_state={"document_type": "research_paper"}
)

# Create checkpoint
checkpoint_id = create_checkpoint(
    workflow_id=workflow_id,
    step_name="entity_extraction",
    step_number=2,
    state_data={"entities": [...], "relationships": [...]},
    metadata={"processing_time": 45.2}
)

# Restore from checkpoint
restore_from_checkpoint(checkpoint_id=checkpoint_id)

# Update workflow progress
update_workflow_progress(
    workflow_id=workflow_id,
    step_number=3,
    status="running"
)

# Get workflow status
get_workflow_status(workflow_id=workflow_id)

# Get workflow checkpoints
get_workflow_checkpoints(workflow_id=workflow_id)

# Get workflow statistics
get_workflow_statistics()

# Save workflow as reusable template
save_workflow_template(
    workflow_id=workflow_id,
    template_name="PDF Entity Extraction Pipeline",
    description="Standard workflow for extracting entities from PDF documents",
    include_data=False  # Structure only for pattern reuse
)

# Load workflow template
load_workflow_template(template_id="template_abc123")

# Create new workflow from template
new_workflow_id = create_workflow_from_template(
    template_id="template_abc123",
    new_workflow_name="Research Paper Analysis",
    initial_state={"document_type": "research_paper"}
)

# List available templates
list_workflow_templates()

# Delete workflow template
delete_workflow_template(template_id="template_abc123")
```

### Phase 1 Pipeline Tools

#### T01: Document Loading
```python
# Load multiple documents
load_documents(document_paths=["paper1.pdf", "paper2.pdf"])

# Get PDF loader information
get_pdf_loader_info()
```

#### T15a: Text Chunking
```python
# Chunk text for processing
chunk_text(
    document_ref="storage://document/doc123",
    text="Long text content...",
    document_confidence=0.9,
    chunk_size=500,
    overlap=50
)

# Get text chunker information
get_text_chunker_info()
```

#### T23a: Entity Extraction
```python
# Extract entities from text
extract_entities(
    chunk_ref="storage://chunk/chunk123",
    text="John Smith works for Microsoft in Seattle.",
    chunk_confidence=0.8
)

# Get supported entity types
get_supported_entity_types()  # Returns: PERSON, ORG, GPE, etc.
```

#### T27: Relationship Extraction
```python
# Extract relationships between entities
extract_relationships(
    chunk_ref="storage://chunk/chunk123",
    text="John Smith works for Microsoft in Seattle.",
    entities=[...],  # Previously extracted entities
    chunk_confidence=0.8
)

# Get supported relationship types
get_supported_relationship_types()
```

#### T31: Entity Building
```python
# Build entities from mentions
build_entities(
    mentions=[...],  # List of extracted mentions
    source_refs=["storage://chunk/chunk123"]
)
```

#### T34: Edge Building
```python
# Build graph edges from relationships
build_edges(
    relationships=[...],  # List of extracted relationships
    source_refs=["storage://chunk/chunk123"]
)
```

#### T68: PageRank Analysis
```python
# Calculate PageRank scores
calculate_pagerank(graph_ref="neo4j://graph/main")

# Get top entities by PageRank
get_top_entities_by_pagerank(limit=10)
```

#### T49: Multi-hop Query
```python
# Query graph with natural language
query_graph(query="What companies does John Smith work for?")

# Execute structured query
execute_query(
    query_entities=["John Smith"],
    query_type="employment",
    max_hops=2
)
```

### Workflow Orchestration

#### Complete Pipeline Execution
```python
# Execute full PDF → Answer workflow
execute_pdf_to_answer_workflow(
    document_paths=["research_paper.pdf"],
    query="What are the main findings?",
    workflow_name="Research Analysis"
)

# Get orchestrator information
get_orchestrator_info()
```

### System Tools

#### Connection and Status
```python
# Test MCP connection
test_connection()  # Returns: "✅ Super-Digimon MCP Server Connected!"

# Echo test
echo(message="Hello MCP")  # Returns: "Echo: Hello MCP"

# Get system status
get_system_status()
# Returns: {
#   "status": "operational",
#   "services": {"identity_service": "active", ...},
#   "core_services_count": 4,
#   "phase1_tools_count": 33,
#   "orchestrator_ready": True
# }
```

### MCP Tool Discovery

All tools are automatically discoverable via the MCP protocol:

```bash
# List available tools
mcp list-tools

# Get tool schema
mcp describe-tool create_mention

# Execute tool
mcp call create_mention \
  --surface_form "John Smith" \
  --start_pos 0 \
  --end_pos 10 \
  --source_ref "doc123"
```

### Error Handling

All MCP tools follow standardized error responses:

```json
{
  "status": "error",
  "error": "Entity not found: entity_123",
  "tool_id": "T107_IDENTITY_SERVICE",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### Performance Considerations

- **Caching**: Core services use intelligent caching
- **Batch Operations**: Group related operations for efficiency
- **Connection Pooling**: Shared Neo4j connections across tools
- **Async Support**: Phase 2 tools support async execution

### Integration Examples

#### Agent Workflow Composition
```python
# Agent can compose tools automatically:
# 1. Load document
doc_result = load_documents(["paper.pdf"])

# 2. Chunk text
chunk_result = chunk_text(
    document_ref=doc_result["documents"][0]["ref"],
    text=doc_result["documents"][0]["text"]
)

# 3. Extract entities
entity_result = extract_entities(
    chunk_ref=chunk_result["chunks"][0]["ref"],
    text=chunk_result["chunks"][0]["text"]
)

# 4. Query knowledge
answer = query_graph("What are the main conclusions?")
```

#### Cross-Modal Analysis via MCP
Tools enable seamless format conversion:
- **Graph → Table**: Export graph data as structured tables
- **Table → Vector**: Convert tabular data to embeddings  
- **Vector → Graph**: Build graph from similarity relationships
- **All → Source**: Trace any result back to original documents

---
For authentication, error codes, and advanced usage, see SECURITY.md and ARCHITECTURE.md. 