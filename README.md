# Super-Digimon

A GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data through 106 specialized tools.

## Quick Start

```bash
# 1. Start Neo4j database  
cd tools/cc_automator && docker-compose up -d neo4j

# 2. Install dependencies
pip install -r tools/cc_automator/requirements.txt

# 3. Run connection test
pytest tools/cc_automator/test_files/test_simple_neo4j.py -v
```

## Architecture Overview

**System**: 106 tools across 7 phases with single MCP server communication

```
Claude Code (Natural Language Agent)
           ↓
    MCP Protocol Communication  
           ↓
106 Python Tools (7 Phases)
           ↓
Neo4j (Graphs) + SQLite (Metadata) + FAISS (Vectors)
```

### Tool Phases (106 Tools Total)
- **Phase 1**: Ingestion (T01-T12) - Document loading, API connectors  
- **Phase 2**: Processing (T13-T30) - NLP, entity extraction
- **Phase 3**: Construction (T31-T48) - Graph building, embeddings
- **Phase 4**: Retrieval (T49-T67) - 19 JayLZhou operators + infrastructure
- **Phase 5**: Analysis (T68-T75) - Graph algorithms, centrality measures
- **Phase 6**: Storage (T76-T81) - Database management, backup, caching
- **Phase 7**: Interface (T82-T106) - Natural language processing, monitoring, export

## Project Structure

```
super-digimon/
├── README.md                    # This file
├── CLAUDE.md                    # Claude Code guidance
├── ARCHITECTURE.md              # System architecture  
├── IMPLEMENTATION.md            # Development roadmap
├── docs/                        # Organized documentation
│   ├── decisions/              # Architecture decisions
│   ├── specifications/         # Technical specifications  
│   ├── planning/              # Planning documents
│   └── reference/             # Reference materials
├── docs/specifications/        # Authoritative tool specifications
├── tools/cc_automator/         # Implementation and tests
├── test_data/                  # Sample datasets
└── config/                     # Configuration files
```

## Key Documents

### **For Developers**
- [`CLAUDE.md`](CLAUDE.md) - Guidance for Claude Code development
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - System architecture and design
- [`IMPLEMENTATION.md`](IMPLEMENTATION.md) - Development roadmap and phases

### **Specifications**
- [`docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`](docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md) - Complete 106 tool specifications (canonical)
- [`docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md`](docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md) - Phase organization and tool breakdown

### **Decisions**
- [`docs/decisions/CANONICAL_DECISIONS_2025.md`](docs/decisions/CANONICAL_DECISIONS_2025.md) - Authoritative architectural decisions and final scope

## Current Status

**Phase**: Specification complete, ready for implementation
**Implementation**: 0 of 106 Super-Digimon tools implemented
**Development Code**: CC_Automator exists as separate development/testing tool
**Next**: Begin Phase 0 infrastructure setup for 106-tool system
**Scope**: Prototype (functionally complete, not production-ready)

## Development Approach

1. **Phase 0**: Infrastructure setup (Docker, databases, MCP framework)
2. **Phase 1-3**: Data pipeline (T01-T48) - Ingestion through construction
3. **Phase 4**: Core GraphRAG (T49-T67) - JayLZhou operators  
4. **Phase 5-7**: Advanced features (T68-T106) - Analysis and interface

## Technology Stack

- **Language**: Python 3.11+
- **Protocol**: Model Context Protocol (MCP) - Single server
- **Databases**: Neo4j (graphs) + SQLite (metadata) + FAISS (vectors)
- **Development**: Hybrid workflow (local code + Docker services)
- **Runtime**: Claude Code (claude.ai/code)

## Contributing

1. **Understanding**: Read [`CLAUDE.md`](CLAUDE.md) for development context
2. **Architecture**: Review [`ARCHITECTURE.md`](ARCHITECTURE.md) for system design
3. **Implementation**: Follow [`IMPLEMENTATION.md`](IMPLEMENTATION.md) roadmap
4. **Tools**: Check [`docs/specifications/`](docs/specifications/) for complete tool specifications

## References

- **JayLZhou GraphRAG**: [Original research](https://github.com/JayLZhou/GraphRAG) (19 core operators)
- **Model Context Protocol**: [MCP Documentation](https://modelcontextprotocol.io/)
- **Claude Code**: [Development environment](https://claude.ai/code)