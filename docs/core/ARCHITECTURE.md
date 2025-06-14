# Super-Digimon Architecture

## System Overview

Super-Digimon is a GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data through **106 specialized tools** organized in **7 lifecycle phases**. The system combines graph storage, vector search, and metadata management to provide intelligent graph analysis capabilities.

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
│    Server       │  106 Tools (T01-T106)
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

## Tool Organization (106 Tools)

### Phase Distribution
- **Phase 1 - Ingestion** (T01-T12): 12 tools for data loading
- **Phase 2 - Processing** (T13-T30): 18 tools for text/NLP processing
- **Phase 3 - Construction** (T31-T48): 18 tools for graph building
- **Phase 4 - Retrieval** (T49-T67): 19 tools for GraphRAG queries
- **Phase 5 - Analysis** (T68-T75): 8 tools for graph algorithms
- **Phase 6 - Storage** (T76-T81): 6 tools for data management
- **Phase 7 - Interface** (T82-T106): 25 tools for UI/monitoring/export

## Key Architectural Decisions

### 1. Single MCP Server
**Decision**: Use one Python MCP server exposing all 106 tools  
**Rationale**: Simpler than federated architecture, sufficient for prototype scope

### 2. Triple Database Architecture
- **Neo4j**: Primary storage for graph structure (nodes, relationships, communities)
- **SQLite**: Metadata storage (documents, chunks, configuration)
- **FAISS**: Vector similarity search for semantic queries

### 3. Attribute-Based Tool System
Tools declare required attributes, not fixed graph types:
```python
required_attributes = {
    "node": ["embedding"],
    "relationship": ["weight"]
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

## Data Flow

1. **Ingestion**: Documents → Chunks → Text Processing
2. **Construction**: Entities/Relations → Graph Building → Embeddings
3. **Storage**: Graph → Neo4j, Vectors → FAISS, Metadata → SQLite
4. **Retrieval**: Query → Tool Selection → Graph Operations → Response
5. **Analysis**: Graph → Algorithms → Insights → Natural Language

## Development Approach

### Implementation Priority
1. **Infrastructure First**: Docker, databases, basic MCP server
2. **Core Pipeline**: Phases 1-3 (ingestion, processing, construction)
3. **GraphRAG Core**: Phase 4 (JayLZhou operators)
4. **Advanced Features**: Phases 5-7 (analysis, interface)

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