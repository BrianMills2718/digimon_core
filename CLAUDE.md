# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Status

**Documentation**: Refactored from 87 files to <20 core files (January 13, 2025)  
**Implementation**: Starting fresh - 0% complete  
**Next Step**: See IMPLEMENTATION_ROADMAP.md

## Project Overview

Super-Digimon is a GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data. The system combines Neo4j graph storage, FAISS vector search, and SQLite metadata to provide intelligent graph analysis through **121 specialized tools** organized in 8 lifecycle phases.

## Technical Requirements

- **Python 3.11+** with comprehensive type hints
- **Docker & Docker Compose** for database services
- **8GB+ RAM** minimum, 16GB recommended
- **10GB+ disk space** for databases and indices
- **No GPU required** - CPU-based processing only

## Success Criteria

### Phase 1: Vertical Slice (Weeks 1-2)
- [ ] Core services operational (T107, T110, T111, T121)
- [ ] PDF → PageRank → Answer workflow functional end-to-end
- [ ] Cross-database references working (neo4j:// sqlite:// faiss://)
- [ ] Quality scores propagate correctly through pipeline
- [ ] Workflow state checkpoint/restore functional

### Phase 2: Core Implementation (Month 1)
- [ ] All Phase 1-3 tools implemented (T01-T48)
- [ ] Three-level identity system working (Surface → Mention → Entity)
- [ ] Neo4j + SQLite + FAISS integration stable
- [ ] Basic performance targets met (<2min for 10MB PDF)

### Phase 3: Full System (Months 2-3)
- [ ] All 121 tools implemented and tested
- [ ] Tool contracts validated and enforced
- [ ] Complete GraphRAG operators functional (T49-T67)
- [ ] Statistical analysis integration working (Graph ↔ Table)
- [ ] Performance optimized for research workloads

### Thesis Defense Ready
- [ ] Can demonstrate all mock workflows from analysis
- [ ] Handles real research documents effectively
- [ ] Quality tracking provides audit trail
- [ ] System recovers gracefully from failures

## Key Commands

### Development Environment
```bash
# Start Neo4j database
docker-compose up -d neo4j

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Check Neo4j status
docker-compose ps

# View Neo4j logs
docker-compose logs neo4j
```

### Development Workflow
```bash
# Start development environment
docker-compose up -d
python -m src.mcp_server

# Run tests
pytest

# Clean up Docker containers
docker-compose down
```

## Architecture Overview

### Core Components
- **Claude Code**: Natural language agent that orchestrates tool execution via MCP
- **Neo4j**: Primary graph database for entities, relationships, and communities
- **FAISS**: Vector search index for semantic similarity
- **SQLite**: Metadata storage for documents and configuration
- **121 MCP Tools**: Complete system implementation across 8 phases (T01-T121)

### Storage Architecture
```
Claude Code (Agent)
      ↓
MCP Protocol  
      ↓
Python MCP Servers (121 Tools)
      ↓
Neo4j (Graphs) + SQLite (Metadata) + FAISS (Vectors)
```

### Tool Categories (121 Tools Across 8 Phases)
- **Phase 1 - Ingestion (T01-T12)**: Document loading, API connectors, database integration
- **Phase 2 - Processing (T13-T30)**: Text cleaning, NLP, entity/relationship extraction  
- **Phase 3 - Construction (T31-T48)**: Graph building, embeddings, vector indexing
- **Phase 4 - Retrieval (T49-T67)**: JayLZhou GraphRAG operators (the core 19 operators)
- **Phase 5 - Analysis (T68-T75)**: Advanced graph algorithms, centrality measures
- **Phase 6 - Storage (T76-T81)**: Database management, backup, caching
- **Phase 7 - Interface (T82-T106)**: Natural language processing, monitoring, export
- **Phase 8 - Core Services (T107-T121)**: Identity, versioning, quality, workflow state

## Key Files and Directories

### Documentation Structure (Consolidated)
```
Digimons/
├── README.md                       # Project overview
├── CLAUDE.md                       # This file
├── IMPLEMENTATION_ROADMAP.md       # Development plan
└── docs/
    ├── core/                       # Essential documentation
    │   ├── ARCHITECTURE.md         # System design
    │   ├── SPECIFICATIONS.md       # All 121 tools
    │   ├── COMPATIBILITY_MATRIX.md # Tool integration matrix
    │   ├── DATABASE_INTEGRATION.md # Database integration planning
    │   ├── IMPLEMENTATION_REQUIREMENTS.md # Complete implementation checklist
    │   ├── DEVELOPMENT_GUIDE.md    # How to develop
    │   └── DESIGN_PATTERNS.md      # Key patterns
    ├── project/                    # Project management
    │   └── HISTORY.md             # Evolution story
    └── archive/                   # Historical docs

```

### Key Documentation
- **Architecture**: `docs/core/ARCHITECTURE.md`
- **Tool Specs**: `docs/core/SPECIFICATIONS.md` (all 121 tools)
- **Integration**: `docs/core/DATABASE_INTEGRATION.md`
- **Requirements**: `docs/core/IMPLEMENTATION_REQUIREMENTS.md`
- **Compatibility**: `docs/core/COMPATIBILITY_MATRIX.md`
- **Dev Guide**: `docs/core/DEVELOPMENT_GUIDE.md`
- **Patterns**: `docs/core/DESIGN_PATTERNS.md`
- **Roadmap**: `IMPLEMENTATION_ROADMAP.md`

### Future Code Structure
- `src/`: Source code (to be created)
- `tests/`: Test files (to be created)
- `test_data/`: Sample datasets for testing
- `scripts/`: Utility scripts (to be created)

## Development Approach

### Implementation Priority
Based on the 121 tool specification:
1. **Vertical Slice First**: One complete workflow (PDF → PageRank → Answer)
2. **Core Services**: T107-T111, T121 must be implemented first
3. **Horizontal Expansion**: Fill out all phases after vertical slice works

### Technical Patterns
- **Attribute-Based Tool System**: Tools declare requirements, not fixed graph types
- **MCP Protocol**: All 121 tools exposed via Model Context Protocol
- **Pass-by-Reference**: Efficient handling of large graph data
- **Phase-Based Development**: Implement tools in dependency order

## Database Configuration

### Neo4j Connection
- Default URL: `bolt://localhost:7687`
- Default credentials: `neo4j/password`
- HTTP interface: `http://localhost:7474`

### Environment Variables
Create `.env` file in project root:
- `NEO4J_URI=bolt://localhost:7687`
- `NEO4J_USER=neo4j`
- `NEO4J_PASSWORD=password`
- `FAISS_INDEX_PATH=./data/faiss_index`
- `SQLITE_DB_PATH=./data/metadata.db`

## Testing Strategy

### Test Categories
- Unit tests: Individual component functionality
- Integration tests: Multi-component interactions  
- E2E tests: Complete workflow validation
- Performance tests: System benchmarking

### Running Tests
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest --cov=src tests/
```

## Important Constraints

### Design Philosophy
- **Prototype Focus**: Complete functionality over production optimization
- **Single User**: No multi-user or security considerations
- **Research Tool**: Academic exploration over commercial deployment
- **Attribute Flexibility**: Graph types defined by attributes, not rigid schemas

### Non-Goals
- Multi-user support or authentication
- Production-level security
- Enterprise-grade performance optimization
- Advanced graph databases or complex ontologies

## Data Flow

1. **Ingestion**: Documents → Chunks → Entities/Relationships → Graph
2. **Indexing**: Entities → Embeddings → FAISS Vector Index
3. **Query**: Natural Language → Tool Selection → Graph Operations → Response
4. **Storage**: Neo4j (structure) + FAISS (semantics) + SQLite (metadata)

## Quick Start for New Contributors

### Understanding the System
1. **Read roadmap**: `IMPLEMENTATION_ROADMAP.md`
2. **Review architecture**: `docs/core/ARCHITECTURE.md`
3. **Study specifications**: `docs/core/SPECIFICATIONS.md`
4. **Follow patterns**: `docs/core/DESIGN_PATTERNS.md`

### Development Setup
1. **Read the guide**: `docs/core/DEVELOPMENT_GUIDE.md`
2. **Set up environment**: Create venv, install deps
3. **Start services**: `docker-compose up -d`
4. **Implement T01**: Start with text loader as proof of concept

## Implementation Status

See `IMPLEMENTATION_ROADMAP.md` for detailed plan and milestones.

**Current Phase**: Starting Vertical Slice (PDF → PageRank → Answer)  
**Next Milestone**: Complete workflow demonstrating all layers

## Key Principles

1. **Start Simple**: Implement T01 first, prove the architecture works
2. **Test First**: Write tests before implementation (TDD)
3. **Follow Patterns**: Use patterns from `docs/core/DESIGN_PATTERNS.md`
4. **Document Changes**: Update specs if implementation differs
5. **Incremental Progress**: One tool at a time, commit working code

## Notes

- **No implementation exists yet** - Starting from scratch
- **Documentation is complete** - All 121 tools fully specified
- **Architecture is final** - Single MCP server, triple database, tool contracts
- **Begin with Vertical Slice** - Prove architecture with one complete workflow

## Development Standards

### Code Quality
- **Python 3.11+** with type hints on all functions
- **Black formatting** with max line length 88
- **Flake8 linting** with reasonable exclusions (E203, W503)
- **MyPy strict mode** for type checking
- **Docstrings** on all public functions (Google style)
- **main.py** as entry point for MCP server

### Testing Requirements
- **Unit tests**: Test individual tool logic with real test databases
- **Integration tests**: Test tool chains with full data flow
- **E2E tests**: Test complete workflows (PDF → Answer) with NO mocking
- **Performance tests**: Track execution time trends, not hard limits
- **Coverage target**: 85%+ for core services (T107-T121)

### Self-Healing Patterns

When implementing code, always follow these patterns for robustness:

1. **Use reference format for cross-database links**
   ```python
   # Good: "neo4j://entity/ent_123"
   # Bad: {"database": "neo4j", "type": "entity", "id": "ent_123"}
   ```

2. **Test with real databases, not mocks**
   ```python
   # Good: neo4j_container = Neo4jContainer("neo4j:5-community")
   # Bad: mock_neo4j = Mock(spec=GraphDatabase)
   ```

3. **Handle missing tools gracefully**
   ```python
   if not tool_contract_satisfied(required_state):
       return partial_result_with_warning()
   ```

4. **Use pathlib for all file operations**
   ```python
   # Good: Path(__file__).parent / "data" / "test.pdf"
   # Bad: os.path.join(os.getcwd(), "data/test.pdf")
   ```

5. **Return partial results on failure**
   ```python
   # Good: {"status": "partial", "data": processed_items, "failed": failed_items}
   # Bad: raise Exception("Some items failed")
   ```

6. **Track quality through every operation**
   ```python
   result = {
       "data": processed_data,
       "confidence": min(input_confidence * 0.95, 1.0),
       "warnings": warnings_collected
   }
   ```

## Project Structure
```
Digimons/
├── main.py              # MCP server entry point
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Database services
├── .env                 # Environment configuration
├── src/
│   ├── core/           # Core services (T107-T121)
│   ├── tools/          # Tool implementations by phase
│   │   ├── phase1/     # Ingestion (T01-T12)
│   │   ├── phase2/     # Processing (T13-T30)
│   │   └── ...         # Through phase8
│   ├── utils/          # Shared utilities
│   └── mcp_server.py   # MCP server implementation
├── tests/
│   ├── unit/           # Unit tests with test databases
│   ├── integration/    # Tool chain tests
│   └── e2e/            # End-to-end workflow tests
├── data/               # Local storage
│   ├── neo4j/          # Graph database files
│   ├── sqlite/         # Metadata database
│   └── faiss/          # Vector indices
└── scripts/            # Utility scripts
```

## Environment Variables
```bash
# Required
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
SQLITE_DB_PATH=./data/metadata.db
FAISS_INDEX_PATH=./data/faiss_index

# Optional
MCP_SERVER_PORT=3333
LOG_LEVEL=INFO
CACHE_DIR=./data/cache
MAX_WORKERS=4
```

## External Dependencies

### Core Services (via Docker)
- **Neo4j 5.x**: Graph database (port 7687, 7474)
- **Redis 7.x**: Caching layer (port 6379) - optional

### Python Libraries
- **mcp**: Model Context Protocol server
- **neo4j**: Neo4j Python driver
- **faiss-cpu**: Vector similarity search
- **sqlalchemy**: SQLite ORM
- **spacy**: NLP processing (T23a)
- **sentence-transformers**: Embeddings (T41)

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Type checking
- **coverage**: Test coverage

## Special Considerations

### FAISS Transaction Limitations
FAISS doesn't support transactions. Always:
1. Execute FAISS operations first
2. Log operations for manual rollback
3. Validate reference integrity on startup

### Memory Management
- Batch operations in chunks of 100-1000
- Use streaming/generators for large datasets
- Monitor memory usage in performance tests

### Concurrency Model (Deferred)
For vertical slice, all tools run synchronously. After validation:
- FAST tools (<100ms): Direct execution
- SLOW tools (>1s): Async work queue
- Primary bottlenecks: T01 (PDF), T23b (LLM), T68 (PageRank)

### Error Recovery Strategy
1. Checkpoint workflow state every 100 operations (T121)
2. Return partial results with detailed failure info
3. Support resume from last checkpoint
4. Log structured data for debugging