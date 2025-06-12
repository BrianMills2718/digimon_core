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

**Total: 26 Tools** organized as:

#### Infrastructure Tools (T01-T08)
Foundation for building and managing graph data:
- T01: Document loader
- T02: Text chunker
- T03: Node creator
- T04: Entity extractor
- T05: Relationship extractor
- T06: Graph builder
- T07: Embedding generator
- T08: Vector index builder

#### Retrieval Operators (T09-T19)
Core GraphRAG operations from JayLZhou paper:
- T09: Similarity search (entity_vdb_search)
- T10: Community detector
- T11: Community summarizer
- T12: Graph traversal (entity_onehop)
- T13: Context retriever
- T17: PPR calculator (entity_ppr)
- T19: Relationship vector search
- (etc.)

#### Processing & Extensions (T14-T16, T20-T26)
Output generation and advanced features:
- T14: Response generator
- T15: Result synthesizer
- T16: Visualizer
- T20-T26: Advanced algorithms and transformations

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

1. **Functional**: All 26 tools working via Claude Code
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
│   ├── graphrag.py       # Main 26 tools
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

1. **Clone Digimon CC2** - Has all 26 tools implemented
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