# Super-Digimon

A GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data through 121 specialized tools.

## Quick Start

```bash
# 1. Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Start Neo4j database
docker-compose up -d neo4j

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify setup
python -m tools.test_connection
```

## Architecture Overview

**System**: 121 tools across 8 phases with single MCP server communication

```
Claude Code (Natural Language Agent)
           ↓
    MCP Protocol Communication  
           ↓
121 Python Tools (8 Phases)
           ↓
Neo4j (Graphs) + SQLite (Metadata) + FAISS (Vectors)
```

### Tool Phases (121 Tools Total)
- **Phase 1**: Ingestion (T01-T12) - Document loading, API connectors  
- **Phase 2**: Processing (T13-T30) - NLP, entity extraction
- **Phase 3**: Construction (T31-T48) - Graph building, embeddings
- **Phase 4**: Retrieval (T49-T67) - 19 JayLZhou operators + infrastructure
- **Phase 5**: Analysis (T68-T75) - Graph algorithms, centrality measures
- **Phase 6**: Storage (T76-T81) - Database management, backup, caching
- **Phase 7**: Interface (T82-T106) - Natural language processing, monitoring, export
- **Phase 8**: Core Services (T107-T121) - Identity, versioning, quality tracking, workflow state

## Project Structure

```
Digimons/
├── README.md                    # This file
├── CLAUDE.md                    # Claude Code guidance
├── IMPLEMENTATION_ROADMAP.md    # Development roadmap
├── docs/                        # Documentation
│   ├── core/                   # Essential technical docs
│   │   ├── ARCHITECTURE.md     # System design
│   │   ├── SPECIFICATIONS.md   # All 106 tools
│   │   ├── DEVELOPMENT_GUIDE.md # Setup guide
│   │   └── DESIGN_PATTERNS.md  # Best practices
│   ├── project/                # Project management
│   └── archive/                # Historical docs
└── test_data/                  # Sample datasets
```

## Key Documents

### **For Developers**
- [`CLAUDE.md`](CLAUDE.md) - Guidance for Claude Code development
- [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md) - Development roadmap and phases
- [`docs/core/ARCHITECTURE.md`](docs/core/ARCHITECTURE.md) - System architecture and design
- [`docs/core/DEVELOPMENT_GUIDE.md`](docs/core/DEVELOPMENT_GUIDE.md) - Setup and development guide

### **Specifications**
- [`docs/core/SPECIFICATIONS.md`](docs/core/SPECIFICATIONS.md) - Complete 121 tool specifications
- [`docs/core/COMPATIBILITY_MATRIX.md`](docs/core/COMPATIBILITY_MATRIX.md) - Tool input/output compatibility (authoritative)
- [`docs/core/DESIGN_PATTERNS.md`](docs/core/DESIGN_PATTERNS.md) - Implementation patterns and best practices

## Current Status

**Phase**: Phase 0 - Foundation Setup  
**Implementation**: 0 of 121 tools implemented  
**Documentation**: Complete specifications, architecture, and roadmap  
**Next Step**: Create project structure and core data models (see [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md))  
**Scope**: PhD thesis prototype (functionally complete, not production-ready)

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
- **Runtime**: Claude Code - An AI assistant that orchestrates tool execution via natural language

## Contributing

1. **Understanding**: Read [`CLAUDE.md`](CLAUDE.md) for development context
2. **Architecture**: Review [`ARCHITECTURE.md`](ARCHITECTURE.md) for system design
3. **Implementation**: Follow [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md) for development phases
4. **Specifications**: Check [`docs/core/SPECIFICATIONS.md`](docs/core/SPECIFICATIONS.md) for tool details

**Important**: Update documentation when implementation differs from specification. Include doc updates in pull requests.

## Testing Strategy

- **Unit Tests**: Each tool tested with real test databases
- **Integration Tests**: Tool chain workflows validated end-to-end
- **Quality Tests**: Confidence propagation and partial results verified
- **Test Data**: Sample datasets in `test_data/` for reproducible testing

## Configuration Management

- **Environment Variables**: Use `.env` file (see `.env.example`)
- **Database Config**: Neo4j, SQLite, and FAISS connection settings
- **API Keys**: Store in environment variables, never commit
- **Docker Config**: All services configured via `docker-compose.yml`

## Deployment

- **Prototype Deployment**: Docker Compose for local demonstration
- **Sharing**: Export Docker images and data for reproducibility
- **Documentation**: Jupyter notebooks for thesis demonstrations
- **Not Included**: Production deployment, scaling, security hardening

## References

- **JayLZhou GraphRAG**: [Original research](https://github.com/JayLZhou/GraphRAG) (19 core operators)
- **Model Context Protocol**: [MCP Documentation](https://modelcontextprotocol.io/)
- **Claude Code**: [Development environment](https://claude.ai/code)