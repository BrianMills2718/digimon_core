# Super-Digimon

A universal analytical platform that intelligently processes diverse data sources through format-agnostic analysis. Using 121 specialized tools and Claude Code's analytical intelligence, it dynamically selects optimal data structures (graphs, tables, vectors) and seamlessly transforms between formats to enable sophisticated multi-step analytical workflows.

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
python -m scripts.test_connection
```

## Architecture Overview

**System**: Universal analytical platform with intelligent format adaptation and orchestration

```
Claude Code (Analytical Intelligence)
           ↓
    Natural Language → Optimal Analysis Strategy
           ↓
    MCP Protocol Communication  
           ↓
121 Python Tools (8 Phases) + Analytical Libraries
           ↓
Neo4j (Graphs) + SQLite (Metadata) + Qdrant (Vectors)
```

**Core Innovation**: Claude Code dynamically selects data formats and tool sequences based on analytical requirements, enabling seamless transitions between graph analysis, statistical processing, and vector operations within a single workflow.

### Tool Phases (121 Tools Total)
- **Phase 1**: Ingestion (T01-T12) - Multi-format data loading, API connectors  
- **Phase 2**: Processing (T13-T30) - NLP, entity extraction, format detection
- **Phase 3**: Construction (T31-T48) - Dynamic structure building (graphs, tables, embeddings)
- **Phase 4**: Retrieval (T49-T67) - Cross-format querying and data access
- **Phase 5**: Analysis (T68-T75) - Format-specific algorithms (graph, statistical, vector)
- **Phase 6**: Storage (T76-T81) - Multi-database management, backup, caching
- **Phase 7**: Interface (T82-T106) - Natural language processing, monitoring, export
- **Phase 8**: Core Services (T107-T121) - Identity, versioning, quality tracking, workflow state

**Key Capability**: Tools work together to enable workflows like: PDF → Text → Entities → Graph → Community Detection → Table → Statistical Analysis → Visualization

## What Makes This Universal?

Unlike traditional systems that force data into a single format (e.g., always graphs), Super-Digimon:

1. **Format-Agnostic Ingestion**: Accepts PDFs, CSVs, APIs, databases, and automatically adapts processing
2. **Dynamic Structure Selection**: Claude Code chooses graphs for relationship analysis, tables for statistics, vectors for similarity
3. **Seamless Format Conversion**: Tools like T115 (Graph→Table) and T116 (Table→Graph) enable mid-workflow format changes
4. **Integrated Analytics**: Combines graph algorithms, statistical analysis, machine learning, and visualization in single workflows
5. **Intelligent Orchestration**: Claude Code reasons about optimal tool sequences and data transformations

**Example Multi-Format Workflow:**
```
Research Papers (PDF) → Text → Entities → Citation Graph → PageRank → 
Top Authors (Table) → Statistical Analysis → Geographic Clustering → 
Collaboration Network (Graph) → Community Detection → Summary Report
```

## Project Structure

```
Digimons/
├── README.md                    # This file
├── CLAUDE.md                    # Claude Code guidance
├── IMPLEMENTATION_ROADMAP.md    # Development roadmap
├── docs/                        # Documentation
│   ├── core/                   # Essential technical docs
│   │   ├── ARCHITECTURE.md     # System design
│   │   ├── SPECIFICATIONS.md   # All 121 tools
│   │   ├── COMPATIBILITY_MATRIX.md # Tool integration matrix
│   │   ├── DATABASE_INTEGRATION.md # Database integration planning
│   │   ├── IMPLEMENTATION_REQUIREMENTS.md # Complete implementation checklist
│   │   ├── MCP_SETUP_GUIDE.md  # MCP server setup reference
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
- [`docs/core/COMPATIBILITY_MATRIX.md`](docs/core/COMPATIBILITY_MATRIX.md) - Tool integration and compatibility matrix
- [`docs/core/DATABASE_INTEGRATION.md`](docs/core/DATABASE_INTEGRATION.md) - Comprehensive database integration planning
- [`docs/core/IMPLEMENTATION_REQUIREMENTS.md`](docs/core/IMPLEMENTATION_REQUIREMENTS.md) - Complete implementation checklist
- [`docs/core/MCP_SETUP_GUIDE.md`](docs/core/MCP_SETUP_GUIDE.md) - MCP server setup reference
- [`docs/core/DESIGN_PATTERNS.md`](docs/core/DESIGN_PATTERNS.md) - Implementation patterns and best practices

## Current Status

**Phase**: Phase 2 - LLM-Driven Ontology System  
**Implementation**: Phase 0 + Phase 1 complete, starting Phase 2  
**Documentation**: Complete specifications and architecture  
**Next Step**: Build Streamlit ontology chat interface with Gemini 2.5 Flash  
**Scope**: PhD thesis prototype (functionally complete, not production-ready)

## Development Approach

### Development Phases Completed
1. ✅ **Phase 0**: Core services (T107, T110, T111, T121) - All working with adversarial testing
2. ✅ **Phase 1**: Vertical slice (PDF → PageRank → Answer) - Functional but with generic spaCy entities
3. 🔄 **Phase 2**: LLM-driven ontology system - Replacing spaCy with domain-specific extraction

### Current Focus: Real GraphRAG Capabilities
**Problem**: spaCy produces generic entities (PERSON, ORG) that make GraphRAG testing meaningless
**Solution**: Conversational ontology generation → domain-specific entities → real GraphRAG evaluation

### Risk Mitigation
- **Specification Drift**: Simple JSON schema validation per tool
- **Performance Bottlenecks**: Monitor core services, optimize hot spots
- **Scope Management**: PhD-appropriate mitigations, defer complex infrastructure

## Technology Stack

- **Language**: Python 3.11+
- **Protocol**: Model Context Protocol (MCP) - Single server
- **Databases**: Neo4j (graphs) + SQLite (metadata) + Qdrant (vectors)
- **Development**: Hybrid workflow (local code + Docker services)
- **Runtime**: Claude Code - The analytical intelligence that provides format-agnostic reasoning and workflow orchestration

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

- **JayLZhou GraphRAG**: [Original research](https://github.com/JayLZhou/GraphRAG) - Inspired 19 core graph operators
- **Model Context Protocol**: [MCP Documentation](https://modelcontextprotocol.io/) - Tool integration framework
- **Claude Code**: [Development environment](https://claude.ai/code) - Analytical intelligence platform
- **Universal Data Processing**: Extends beyond GraphRAG to format-agnostic analytical workflows