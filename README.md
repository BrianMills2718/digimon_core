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

**System**: 106 tools across 5 phases with MCP (Model Context Protocol) communication

```
Claude Code (Natural Language Agent)
           ↓
    MCP Protocol Communication  
           ↓
106 Python Tools (5 Phases)
           ↓
Neo4j (Graphs) + SQLite (Metadata) + FAISS (Vectors)
```

### Tool Phases
- **Phase 1**: Data Ingestion (T01-T03) - Document loading, API connections
- **Phase 2**: Data Processing (T04-T25) - NLP, entity extraction  
- **Phase 3**: Graph Construction (T26-T48) - Graph building, embeddings
- **Phase 4**: Core GraphRAG (T49-T67) - 19 JayLZhou operators
- **Phase 5**: Advanced & Interface (T68-T102) - Analysis, storage, UI

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
├── new_docs/                   # Authoritative tool specifications
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
- [`new_docs/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`](new_docs/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md) - Complete 106 tool specifications
- [`docs/specifications/OPTIMIZED_TOOL_SPECIFICATIONS.md`](docs/specifications/OPTIMIZED_TOOL_SPECIFICATIONS.md) - Optimized architecture (102 tools)

### **Decisions**
- [`docs/decisions/ARCHITECTURAL_DECISIONS.md`](docs/decisions/ARCHITECTURAL_DECISIONS.md) - Key architectural decisions and rationale

## Current Status

**Phase**: Foundation setup and T01 proof-of-concept planning
**Implementation**: 0 of 106 tools implemented
**Next**: Begin Phase 0 with T01 Universal Document Loader PoC

## Development Approach

1. **Phase 0**: Foundation infrastructure + T01 PoC validation
2. **Phase 1-3**: Data pipeline (ingestion → processing → graph construction)  
3. **Phase 4**: Core GraphRAG operators (19 JayLZhou tools)
4. **Phase 5**: Advanced features and interface

## Technology Stack

- **Language**: Python 3.11+
- **Protocol**: Model Context Protocol (MCP)
- **Databases**: Neo4j (graphs), SQLite (metadata), FAISS (vectors)
- **Framework**: FastAPI for MCP servers
- **Runtime**: Claude Code (claude.ai/code)

## Contributing

1. **Understanding**: Read [`CLAUDE.md`](CLAUDE.md) for development context
2. **Architecture**: Review [`ARCHITECTURE.md`](ARCHITECTURE.md) for system design
3. **Implementation**: Follow [`IMPLEMENTATION.md`](IMPLEMENTATION.md) roadmap
4. **Tools**: Check [`new_docs/`](new_docs/) for complete tool specifications

## References

- **JayLZhou GraphRAG**: [Original research](https://github.com/JayLZhou/GraphRAG) (19 core operators)
- **Model Context Protocol**: [MCP Documentation](https://modelcontextprotocol.io/)
- **Claude Code**: [Development environment](https://claude.ai/code)