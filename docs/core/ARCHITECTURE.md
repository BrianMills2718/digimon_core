# Super-Digimon Architecture

## System Overview

Super-Digimon is a GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data through **121 specialized tools** organized in **8 phases**. The system combines graph storage, vector search, and metadata management to provide intelligent graph analysis capabilities.

**Key Innovation**: The system can perform virtually any analytical method through flexible data structuring - seamlessly converting between graphs, tables, and vectors based on the analysis needs.

## Core Architecture

```
┌─────────────────┐
│  Claude Code    │  Natural Language Agent
│   (End User)    │  
└────────┬────────┘
         │ Natural Language
         ▼
┌─────────────────┐
│  MCP Protocol   │  Model Context Protocol
└────────┬────────┘
         │ Tool Calls
         ▼
┌─────────────────┐
│ Python MCP      │  Single MCP Server
│    Server       │  121 Tools (T01-T121)
└────────┬────────┘
         │
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│ Neo4j  ││ SQLite ││ FAISS  │
│(Graphs)││(Meta)  ││(Vector)│
└────────┘└────────┘└────────┘
```

## Technology Stack

- **Language**: Python 3.11+
- **Agent**: Claude Code (Anthropic)
- **Protocol**: MCP (Model Context Protocol)
- **Graph Database**: Neo4j 5.x
- **Vector Store**: FAISS
- **Metadata Store**: SQLite
- **Containerization**: Docker & Docker Compose

## Tool Organization (121 Tools)

### Phase Distribution
- **Phase 1 - Ingestion** (T01-T12): 12 tools for data loading
- **Phase 2 - Processing** (T13-T30): 18 tools for text/NLP processing
- **Phase 3 - Construction** (T31-T48): 18 tools for graph building
- **Phase 4 - Retrieval** (T49-T67): 19 tools for GraphRAG queries
- **Phase 5 - Analysis** (T68-T75): 8 tools for graph algorithms
- **Phase 6 - Storage** (T76-T81): 6 tools for data management
- **Phase 7 - Interface** (T82-T106): 25 tools for UI/monitoring/export
- **Phase 8 - Core Services** (T107-T121): 15 tools for infrastructure support

## Key Architectural Decisions

### 1. Single MCP Server
**Decision**: Use one Python MCP server exposing all 121 tools  
**Rationale**: Simpler than federated architecture, sufficient for prototype scope

### 2. Triple Database Architecture
- **Neo4j**: Primary storage for graph structure (nodes, relationships, communities)
- **SQLite**: Metadata storage (documents, chunks, configuration)
- **FAISS**: Vector similarity search for semantic queries

### 3. Tool Contracts
Tools declare contracts specifying requirements and guarantees:
```python
{
    "required_attributes": {
        "entity": ["canonical_name", "confidence"]
    },
    "required_state": {
        "mentions_created": true,
        "entities_resolved": "optional"  # Domain-specific
    },
    "produced_state": {
        "graph_ready": true
    }
}
```

### 4. Pass-by-Reference Pattern
Graph data passed via unique IDs, not serialized:
```python
return {
    "graph_id": "celestial_council_graph_v1",
    "node_count": 1523,
    "relationship_count": 4892
}
```

### 5. Three-Level Identity System
All text processing maintains three levels of identification:
```
Surface Form → Mention → Entity

Example:
"Apple announced..." → Mention_001 (pos: 0-5) → Entity: Apple Inc.
"AAPL rose 5%..."   → Mention_002 (pos: 0-4) → Entity: Apple Inc.
```

This enables:
- Exact provenance tracking
- Handling ambiguity (Apple Inc. vs apple fruit)
- Multiple surface forms for same entity
- Correction without losing original data

### 6. Optional Entity Resolution
Entity resolution adapts to analytical needs:

**Social Network Analysis** (No Resolution):
```python
# Keep @obama and @barackobama as separate entities
config = {"resolve_entities": false}
# Result: Track different social media personas
```

**Corporate Analysis** (With Resolution):
```python
# Merge "Apple Inc.", "Apple Computer", "AAPL"
config = {"resolve_entities": true}
# Result: Unified view of corporate entity
```

## Implementation Risk Mitigation

### Specification Drift Prevention
- **JSON Schema Validation**: Each tool validates against simple schema
- **Lightweight Contracts**: Basic input/output validation, not full frameworks
- **Manual Review Process**: Regular alignment checks during development

### Performance Bottleneck Prevention
- **Core Services Optimization**: Profile during vertical slice, optimize hot spots
- **Reference-Based Architecture**: Pass IDs, not full objects
- **Async Where Beneficial**: Use asyncio for I/O bound operations
- **Simple Monitoring**: Log timing patterns, identify trends

### PhD-Appropriate Scope
- **Essential Mitigations Only**: Prevent catastrophic problems
- **Defer Complex Infrastructure**: Focus on research goals first
- **Iterative Optimization**: Start simple, optimize when proven necessary

### 7. Universal Quality Tracking
Every data object includes quality metadata:
```python
{
    "data": {...},
    "confidence": 0.87,
    "quality_tier": "high",
    "extraction_method": "llm_v2",
    "warnings": ["OCR quality degraded on page 3"],
    "evidence": ["source_doc_001", "source_doc_002"]
}
```

### 8. Format-Agnostic Processing
Data seamlessly transforms between formats based on analytical needs:
```
Documents → Chunks → Entities/Relations → Graph
                ↓                          ↓
            Embeddings                  Tables
                ↓                          ↓
            Vectors                   Statistics
```

Key tools:
- T115: Graph → Table (for statistical analysis)
- T116: Table → Graph (for graph algorithms)
- T117: Format Auto-Selector

## Core Services Layer

Critical services that support all tools:

### Identity Service (T107)
- Manages three-level identity system
- Creates and resolves mentions
- Merges duplicate entities
- Tracks all surface forms

### Provenance Service (T110)
- Records every operation
- Traces complete lineage
- Enables impact analysis
- Supports reproducibility

### Quality Service (T111)
- Assesses confidence scores
- Propagates uncertainty
- Aggregates quality metrics
- Filters by quality thresholds

### Version Service (T108)
- Four-level versioning (schema, data, graph, analysis)
- Tracks all changes
- Enables rollback
- Supports knowledge evolution

### Workflow State Service (T121)
- Checkpoint workflow progress
- Enable crash recovery
- Support long-running analyses
- Lightweight reference storage

## Data Flow

1. **Ingestion**: Documents → Chunks → Text Processing
2. **Identity Resolution**: Surface Forms → Mentions → Entities
3. **Construction**: Entities/Relations → Graph Building → Embeddings
4. **Storage**: Graph → Neo4j, Vectors → FAISS, Metadata → SQLite
5. **Retrieval**: Query → Tool Selection → Graph Operations → Response
6. **Analysis**: Graph → Algorithms → Insights → Natural Language

## Development Approach

### Vertical Slice First Strategy
Instead of implementing all tools in phases, build one complete workflow first:

**Target**: PDF → PageRank → Answer (2 weeks)
1. **Week 1**: Minimal core services (T107, T110, T111, T121)
2. **Week 2**: Vertical slice tools (T01, T15a, T23a, T31, T34, T76, T68, T49, T90)
3. **Week 3**: Integration testing and architecture validation
4. **Week 4+**: Horizontal expansion based on learnings

### Key Implementation Patterns
- **Reference-based I/O**: All tools use references, not full objects
- **Streaming support**: Handle large datasets incrementally
- **Quality propagation**: Track confidence through pipeline
- **Partial results**: Always return what succeeded
- **Format flexibility**: Convert between graph/table/vector as needed

### Prototype Scope
- **Is**: Functionally complete GraphRAG system
- **Is Not**: Production-ready, multi-user, or performance-optimized

### Non-Goals
- Multi-user authentication
- Production security
- Distributed processing
- Real-time streaming
- Mobile interfaces

## Tool Response Format

All tools return standardized responses:
```python
{
    "status": "success",
    "data": {...},      # Tool-specific data
    "metadata": {       # Optional metadata
        "execution_time": 1.23,
        "tool_version": "1.0.0"
    },
    "error": null       # Error details if failed
}
```

## Error Handling

- Input validation at tool level
- Graceful degradation for missing attributes
- Transaction rollback for graph operations
- Detailed error messages for debugging

## Future Considerations

While not in initial scope, the architecture supports:
- Streaming responses for large datasets
- Federated MCP servers if needed
- Additional graph databases (TypeDB, Amazon Neptune)
- Custom embeddings and LLMs
- Horizontal scaling patterns