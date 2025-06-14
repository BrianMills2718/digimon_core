# Super-Digimon Architecture

## Overview

Super-Digimon is a GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data through 106 specialized tools organized across 7 lifecycle phases. The system combines Neo4j graph storage, FAISS vector search, and SQLite metadata to provide intelligent graph analysis through Claude Code orchestration.

## Core Architecture

### System Stack

```
┌─────────────────────────────────────────────┐
│           Claude Code (Agent)                │
│         Natural Language Interface           │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol
┌─────────────────┴───────────────────────────┐
│         Python MCP Server (Single)           │
│            106 Tools (T01-T106)              │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────┴───────────────────────────┐
│            Storage Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Neo4j   │  │  SQLite  │  │  FAISS   │  │
│  │ (Graphs) │  │(Metadata)│  │(Vectors) │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
```

### Technology Stack

- **Agent Runtime**: Claude Code via Model Context Protocol (MCP)
- **Implementation Language**: Python 3.11+
- **Type System**: Python type hints (not PydanticAI)
- **Communication**: MCP protocol for all tool interactions
- **Databases**: Neo4j (graphs), SQLite (metadata), FAISS (vectors)
- **Development**: Docker for services, local Python development

## Tool Architecture (106 Tools)

### Phase Organization

**Phase 1: Ingestion (T01-T12)** - 12 tools
- Document loaders (PDF, Word, HTML, Markdown)
- API connectors (REST, GraphQL, SQL)
- Database integration

**Phase 2: Processing (T13-T30)** - 18 tools
- Text cleaning and normalization
- NLP operations (tokenization, language detection)
- Entity and relationship extraction

**Phase 3: Construction (T31-T48)** - 18 tools
- Graph building (nodes, edges, communities)
- Embedding generation (text, graph structure)
- Vector indexing

**Phase 4: Retrieval (T49-T67)** - 19 tools
- JayLZhou GraphRAG operators
- Entity, relationship, chunk, and subgraph operations
- Community detection and analysis

**Phase 5: Analysis (T68-T75)** - 8 tools
- Advanced graph algorithms
- Centrality measures
- Path finding and flow analysis

**Phase 6: Storage (T76-T81)** - 6 tools
- Database management
- Backup and recovery
- Cache management

**Phase 7: Interface (T82-T106)** - 25 tools
- Natural language processing
- Query planning and optimization
- Response generation and export

### MCP Server Architecture

**Decision**: Single MCP server exposing all 106 tools
- One server process for simplicity
- All tools available via unified endpoint
- Internal organization by phase
- Simpler than federated approach for prototype

## Storage Architecture

### Neo4j (Primary Graph Storage)
- **Purpose**: Store entities, relationships, communities as graph
- **Access**: Cypher queries via Neo4j Python driver
- **Schema**: Flexible attribute-based nodes and edges
- **Default**: bolt://localhost:7687

### SQLite (Metadata Storage)
- **Purpose**: Documents, configuration, query history, lineage
- **Access**: SQL queries via SQLite MCP tools
- **Benefits**: Simple relational data, easy backups
- **Location**: Local file-based storage

### FAISS (Vector Search)
- **Purpose**: Dense embeddings for similarity search
- **Access**: Direct file operations in Python
- **Benefits**: High performance, GPU-ready
- **Format**: Serialized index files

## Key Design Patterns

### Attribute-Based Compatibility

Tools declare required attributes rather than fixed graph types:

```python
@tool(requires=["embedding", "type", "graph_id"])
def entity_vdb_search(...):
    # Tool checks if graph has required attributes
    pass
```

### Pass-by-Reference

Large data structures use references:

```python
# Return references, not full data
result = {
    "graph_id": "celestial_council",
    "entity_ids": [1, 2, 3],
    "status": "success"
}
```

### Tool Response Format

Standardized response structure:

```python
class MCPToolResponse:
    status: str  # "success" or "error"
    data: Any    # Tool-specific results
    metadata: Dict  # Lineage, timing, etc.
    error: Optional[str]
```

## Development Approach

### Project Scope
- **Type**: Prototype - functionally complete, not production-ready
- **Goal**: Demonstrate complete GraphRAG workflow
- **Users**: Single-user research environment
- **Security**: None - trusted local environment

### Implementation Priority
1. **Infrastructure**: Docker, databases, MCP framework
2. **Data Pipeline**: Phases 1-3 (T01-T48)
3. **Core GraphRAG**: Phase 4 (T49-T67)
4. **Advanced Features**: Phases 5-7 (T68-T106)

### Development Workflow
```bash
# Start services
cd tools/cc_automator
docker-compose up -d neo4j

# Run MCP server locally
python mcp_server.py

# Test with Claude Code
# Natural language queries handled automatically
```

## Data Flow

1. **Ingestion**: Documents → Structured data via Phase 1 tools
2. **Processing**: Text → Entities/Relationships via Phase 2 tools
3. **Construction**: Build graph structure via Phase 3 tools
4. **Storage**: Persist to Neo4j + SQLite + FAISS
5. **Retrieval**: Query using Phase 4 GraphRAG operators
6. **Analysis**: Advanced algorithms via Phase 5 tools
7. **Response**: Natural language output via Phase 7 tools

## File Structure

```
super-digimon/
├── tools/
│   └── cc_automator/
│       ├── mcp_server.py      # Single MCP server
│       ├── tools/             # 106 tool implementations
│       ├── docker-compose.yml # Service configuration
│       └── test_files/        # Test infrastructure
├── docs/
│   ├── specifications/        # Tool specifications
│   ├── architecture/          # Architecture docs
│   └── decisions/            # Design decisions
├── test_data/                 # Sample datasets
└── config/                    # Configuration files
```

## Non-Goals (Explicit Exclusions)

- **No Multi-user Support**: Single-user prototype only
- **No Security Model**: Trusted local environment
- **No Production Optimization**: Functionality over performance
- **No Advanced Features**: TypeDB, hypergraphs excluded
- **No Commercial Features**: Research prototype only

## Success Criteria

1. **Functional**: All 106 tools operational via Claude Code
2. **Natural Language**: Complex queries understood and executed
3. **Flexible**: Multiple graph types via attributes
4. **Traceable**: Complete lineage for all operations
5. **Demonstrable**: Reproduce JayLZhou paper results

## Quick Start

1. **Setup Environment**
   ```bash
   cd tools/cc_automator
   docker-compose up -d neo4j
   pip install -r requirements.txt
   ```

2. **Verify Connection**
   ```bash
   pytest test_files/test_simple_neo4j.py -v
   ```

3. **Start Development**
   - Begin with Phase 1 tools (T01-T12)
   - Follow implementation roadmap in IMPLEMENTATION.md
   - Test each phase before proceeding

## References

- **Tool Specifications**: `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`
- **Implementation Roadmap**: `IMPLEMENTATION.md`
- **Design Decisions**: `docs/decisions/CANONICAL_DECISIONS_2025.md`
- **JayLZhou GraphRAG**: https://github.com/JayLZhou/GraphRAG