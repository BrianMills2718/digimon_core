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

**Core: 26 Tools** (T01-T26) for essential GraphRAG operations
**Vision: 106 Tools** organized by lifecycle phase (future expansion):

#### Core Tools (T01-T26) - Current Focus:
- **T01-T08**: Document loading, chunking, entity/relationship extraction, graph building
- **T09-T15**: Similarity search, community detection, traversal, context retrieval
- **T16-T26**: Advanced algorithms, PPR, visualization, specialized operators

#### Future Expansion (T27-T106) - Vision:
- **Ingestion Tools**: Multi-format loaders, API connectors, streaming
- **Processing Tools**: Advanced NLP, disambiguation, multi-language
- **Construction Tools**: Complex graph operations, schema management
- **Analysis Tools**: Deep graph algorithms, ML integration
- **Storage Tools**: Advanced persistence, caching, optimization
- **Interface Tools**: CLI, monitoring, SQL analysis, provenance

### 5. Development Approach

- **Prototype, Not MVP**: Complete functionality, not production-ready
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

1. **Functional**: All 26 core tools working via Claude Code
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
│   ├── graphrag.py       # Core 26 GraphRAG tools
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

1. **Build from Specifications** - Implement 26 core tools
2. **Install Dependencies** - `pip install -r requirements.txt`
3. **Start Services** - `docker-compose up -d neo4j`
4. **Run Tests** - `pytest tests/`
5. **Launch Claude Code** - `./super-digimon`

## Living Document

This architecture will evolve based on:
- User feedback
- Performance requirements
- New research insights
- Community contributions

Last Updated: January 2025