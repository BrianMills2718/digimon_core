# Super-Digimon Canonical Architecture

## Executive Summary

This document is the **single source of truth** for Super-Digimon's architecture. All other documents should reference this for technical decisions.

## Core Architecture Decisions

### 1. Runtime & Orchestration
- **Agent Runtime**: Claude Code (via MCP)
- **Why**: Natural language understanding, proven reliability, automatic tool orchestration
- **How**: Claude Code receives queries, plans execution, calls tools, synthesizes responses

### 2. Implementation Language
- **Primary**: Python 3.11+
- **Secondary**: TypeScript/JavaScript (visualization only)
- **Type Safety**: Python type hints (NOT PydanticAI)

### 3. Storage Architecture

```
┌─────────────────────────────────────────────┐
│           Claude Code (Agent)                │
│                    ↓                         │
│              MCP Protocol                    │
│                    ↓                         │
├─────────────────────────────────────────────┤
│        Python MCP Servers (Tools)           │
│                    ↓                         │
├─────────────────────────────────────────────┤
│            Storage Layer                     │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Neo4j   │  │  SQLite  │  │  FAISS   │  │
│  │ (Graphs) │  │(Metadata)│  │(Vectors) │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
```

#### Neo4j (Primary Graph Storage)
- **What**: Entities, relationships, communities, chunks as graph nodes
- **Why**: Native graph operations, Cypher queries, built-in algorithms
- **Access**: Via Neo4j MCP server

#### SQLite (Supporting Data)
- **What**: Documents, evaluation data, query history, configuration
- **Why**: Simple relational data, easy backups, MCP support
- **Access**: Via SQLite MCP server

#### FAISS (Vector Embeddings)
- **What**: Dense embeddings for similarity search
- **Why**: File-based, high performance, GPU-ready
- **Access**: Direct file operations in Python

### 4. Tool Architecture

**Total: 106 Tools (Canonical)** organized across 7 phases:

**Phase 1: Ingestion (T01-T12)** - 12 tools  
Document loading and API connectors

**Phase 2: Processing (T13-T30)** - 18 tools  
Text processing, NLP, entity/relationship extraction

**Phase 3: Construction (T31-T48)** - 18 tools  
Graph building, embeddings, vector indexing

**Phase 4: Retrieval (T49-T67)** - 19 tools  
Core GraphRAG operations (JayLZhou operators + infrastructure)

**Phase 5: Analysis (T68-T75)** - 8 tools  
Advanced graph algorithms, centrality measures

**Phase 6: Storage (T76-T81)** - 6 tools  
Database management, backup, caching

**Phase 7: Interface (T82-T106)** - 25 tools  
Natural language processing, monitoring, export

### 5. Development Approach

**Scope**: Prototype (functionally complete, not production-ready)
- All 106 tools functional
- Demonstrates complete GraphRAG workflow  
- Not optimized for scale or production deployment

**Development Environment**: Hybrid workflow
- Local Python development for rapid iteration
- Docker services for stateful components (Neo4j)
- Single MCP server exposing all tools
- **No Timelines**: Priority-based development
- **Explicit Non-Goals**:
  - No multi-user support
  - No security model
  - No performance optimization (yet)
  - No advanced features (TypeDB, hypergraphs)

### 6. Key Design Patterns

#### Attribute-Based Compatibility
```python
# Tools declare requirements
@tool(requires=["embedding", "type", "graph_id"])
def entity_vdb_search(...):
    pass

# Graphs declare available attributes
graph.attributes = ["id", "embedding", "type", "graph_id", "custom_field"]

# Runtime checks compatibility automatically
```

#### Pass-by-Reference for Large Data
```python
# Don't pass full graphs
result = {"graph_id": "celestial_council", "entity_ids": [...]}

# Tools fetch what they need
entities = neo4j.get_entities(graph_id, entity_ids)
```

### 7. Deployment Strategy

#### Development
```bash
# Services in Docker
docker-compose up neo4j

# Code runs locally
python -m super_digimon.mcp_server
```

#### Production
```bash
# Everything in Docker
docker-compose -f docker-compose.prod.yml up -d
```

### 8. Success Criteria

1. **Functional**: All 106 tools working via Claude Code
2. **Natural Language**: Complex queries understood and executed
3. **Flexible**: Multiple graph types supported via attributes
4. **Traceable**: Full lineage for all operations
5. **Demonstrable**: Can reproduce JayLZhou paper results

## What This Is NOT

1. **Not a Framework**: It's a specific implementation
2. **Not Production-Ready**: It's a research prototype
3. **Not Optimized**: Functionality over performance
4. **Not Secure**: Single-user, trusted environment
5. **Not Final**: Will evolve based on usage

## Quick Reference

- **Ask Claude Code**: "What graphs are available?"
- **Run Analysis**: "Find influential members of the Celestial Council"
- **Transform Data**: "Convert this graph to a table for statistical analysis"
- **Visualize**: "Show me the community structure"

## File Structure

```
super-digimon/
├── mcp_servers/          # Python MCP implementations
│   ├── graphrag.py       # Main 106 tools
│   └── viz.py           # Visualization server
├── docker/               # Docker configurations
│   ├── docker-compose.yml
│   └── Dockerfile
├── data/                 # Local storage
│   ├── indices/         # FAISS files
│   ├── graphrag.db      # SQLite database
│   └── cache/           # Query cache
└── docs/                # Documentation
```

## For Developers

1. **Review Specifications** - Read `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`
2. **Install Dependencies** - `pip install -r tools/cc_automator/requirements.txt`
3. **Start Services** - `cd tools/cc_automator && docker-compose up -d neo4j`
4. **Run Connection Tests** - `pytest tools/cc_automator/test_files/test_simple_neo4j.py -v`
5. **Begin Implementation** - Start with Phase 1 tools (T01-T12)

## Living Document

This architecture will evolve based on:
- User feedback
- Performance requirements
- New research insights
- Community contributions

Last Updated: January 2025