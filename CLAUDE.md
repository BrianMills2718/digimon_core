# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Status

**Documentation**: Complete and aligned with vertical slice strategy  
**Implementation**: 0% complete in main project (working code exists in super_digimon_implementation/)  
**Strategy**: Vertical slice first - PDF → PageRank → Answer workflow  
**Next Step**: Implement core services (T107, T110, T111, T121) then vertical slice tools

## Project Overview

Super-Digimon is a universal analytical platform that enables natural language querying and processing of diverse data through format-agnostic analysis. The system combines Neo4j graph storage, Qdrant vector database, and SQLite metadata to provide intelligent analytical capabilities through **121 specialized tools**.

**Implementation Approach**: Vertical slice first - implement one complete workflow (PDF → PageRank → Answer) before expanding horizontally to all tools.

## Technical Requirements

- **Python 3.11+** with comprehensive type hints
- **Docker & Docker Compose** for database services
- **8GB+ RAM** minimum, 16GB recommended
- **10GB+ disk space** for databases and indices
- **No GPU required** - CPU-based processing only

## Success Criteria (Granular + Adversarial Testing)

### Phase 0: Foundation (Week 1)
**Core Services (Each Must Pass Adversarial Testing)**:
- [ ] **T107 Identity Service**: Creates mentions, links to entities, handles duplicates
  - ✅ Test: 100 random entity names, verify no false merges
  - ✅ Test: Identical entities with different surface forms merge correctly
  - ✅ Adversarial: Unicode names, special characters, very long names
- [ ] **T110 Provenance Service**: Records all operations with full lineage
  - ✅ Test: Track 50 operations, verify complete audit trail
  - ✅ Adversarial: Concurrent operations, memory pressure, large payloads
- [ ] **T111 Quality Service**: Propagates confidence through pipeline
  - ✅ Test: Confidence degrades predictably through 5-step pipeline
  - ✅ Adversarial: Extreme confidence values (0.0001, 0.9999), negative numbers
- [ ] **T121 Workflow State**: Checkpoints and restores reliably
  - ✅ Test: 10 checkpoints, restore from each successfully
  - ✅ Adversarial: Disk full, corrupted checkpoints, missing files

**Infrastructure (Must Handle Edge Cases)**:
- [ ] **MCP Server**: All 4 core tools registered and responding
  - ✅ Test: Tool discovery, parameter validation, error responses
  - ✅ Adversarial: Malformed requests, timeout handling, concurrent calls
- [ ] **Database Integration**: All 3 databases operational
  - ✅ Test: Neo4j/SQLite/Qdrant create/read/update operations
  - ✅ Adversarial: Connection drops, full disk, memory exhaustion

### Phase 1: Vertical Slice (Weeks 2-3)
**Each Tool Must Pass Individual + Integration Tests**:
- [ ] **T01 PDF Loader**: Extracts clean text with confidence scores
  - ✅ Test: 5 different PDF types (text, scanned, multi-column)
  - ✅ Adversarial: Corrupted PDFs, 0-byte files, 100MB+ documents
- [ ] **T15a Text Chunker**: Creates overlapping chunks with position tracking
  - ✅ Test: Chunk boundaries respect token limits, overlap works
  - ✅ Adversarial: Single-token text, massive paragraphs, Unicode edge cases
- [ ] **T23a spaCy NER**: Extracts entities with position and confidence
  - ✅ Test: Standard entities detected in 10 test documents
  - ✅ Adversarial: No entities, entity-only text, nested entities
- [ ] **T27 Relationship Extractor**: Links entities with confidence weighting
  - ✅ Test: Basic subject-verb-object patterns work
  - ✅ Adversarial: Complex sentences, no relationships, ambiguous pronouns
- [ ] **T31 Entity Builder**: Converts mentions to graph nodes
  - ✅ Test: 100 mentions → entities, verify deduplication
  - ✅ Adversarial: Identical text different contexts, empty mentions
- [ ] **T34 Edge Builder**: Creates weighted relationships in graph
  - ✅ Test: Relationships match extractions, weights preserved
  - ✅ Adversarial: Self-relationships, circular dependencies, zero weights
- [ ] **T68 PageRank**: Ranks entities by centrality
  - ✅ Test: Results match NetworkX implementation ±0.001
  - ✅ Adversarial: Disconnected graphs, single nodes, identical weights
- [ ] **T49 Multi-hop Query**: Traverses graph to find answers
  - ✅ Test: 2-hop and 3-hop queries return correct paths
  - ✅ Adversarial: No paths exist, circular queries, infinite loops

**End-to-End Workflow (Critical Integration Tests)**:
- [ ] **PDF → Answer Pipeline**: Complete workflow with real test data
  - ✅ Test: 3 different PDFs → meaningful answers with <5min processing
  - ✅ Adversarial: Malformed PDFs, empty results, system failures
- [ ] **Cross-Database Integrity**: References work across Neo4j/SQLite/Qdrant
  - ✅ Test: Entity in Neo4j matches SQLite metadata and Qdrant embedding
  - ✅ Adversarial: Missing references, orphaned data, corrupted indices
- [ ] **Quality Propagation**: Confidence tracked through entire pipeline
  - ✅ Test: Input confidence 0.9 → output confidence documented at each step
  - ✅ Adversarial: Conflicting confidences, quality degradation, zero confidence

### Phase 2: Horizontal Expansion (Validation Required)
- [ ] **Additional Tools**: Only implement after Phase 1 passes ALL tests
- [ ] **Performance Optimization**: Based on real bottlenecks, not assumptions
- [ ] **Error Recovery**: Graceful degradation tested under failure conditions

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
- **Qdrant**: Vector database for semantic similarity and embeddings
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
Neo4j (Graphs) + SQLite (Metadata) + Qdrant (Vectors)
```

### Vertical Slice Implementation Priority

**Phase 0 - Core Services (REQUIRED FIRST)**:
- T107: Identity Service (minimal mention → entity linking)
- T110: Provenance Service (basic operation tracking)  
- T111: Quality Service (confidence tracking and propagation)
- T121: Workflow State Service (checkpoint/restore)

**Phase 1 - Vertical Slice Tools (PDF → PageRank → Answer)**:
- T01: PDF Loader (basic text extraction)
- T15a: Sliding Window Chunker (fixed 512-token chunks)
- T23a: spaCy NER (standard entity types)
- T27: Pattern Relationship Extractor (simple verb patterns)
- T31: Entity Node Builder (mention → entity conversion)
- T34: Relationship Edge Builder (create graph edges)
- T68: PageRank (centrality analysis)
- T49: Multi-hop Query (graph traversal for answers)

**All Other Tools**: Implement after vertical slice validates architecture

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

### Implementation Priority (Vertical Slice Strategy)
1. **Phase 0**: Core services (T107, T110, T111, T121) - MINIMAL implementations only
2. **Phase 1**: Vertical slice tools for PDF → PageRank → Answer workflow  
3. **Validation**: Ensure end-to-end workflow works with real test data
4. **Phase 2**: Horizontal expansion to additional tools based on validated architecture

**Critical**: Do NOT implement full tools initially. Use minimal viable implementations to prove architecture works.

### Technical Patterns (Granular Implementation Standards)
- **Attribute-Based Tool System**: Tools declare requirements, not fixed graph types
- **MCP Protocol**: All tools exposed via Model Context Protocol with full validation
- **Pass-by-Reference**: Efficient handling using storage://type/id format
- **Adversarial-First Development**: Each tool must handle edge cases before integration

### Granular Implementation Criteria (Per Tool)
**Every tool must meet these specific standards**:

1. **Input Validation**:
   - [ ] Parameter type checking with informative errors
   - [ ] Range validation for numerical inputs
   - [ ] Required field validation with specific missing field messages
   - [ ] Adversarial: Handle None, empty strings, extreme values gracefully

2. **Output Consistency**:
   - [ ] Always return Dict[str, Any] with standardized structure
   - [ ] Include confidence score (0.0-1.0) for all operations
   - [ ] Provide partial results on failure with detailed error information
   - [ ] Adversarial: Consistent output format even under error conditions

3. **Quality Tracking**:
   - [ ] Input confidence propagated to output with documented degradation
   - [ ] Operation metadata included (timestamp, tool_id, parameters)
   - [ ] Lineage references to source data maintained
   - [ ] Adversarial: Quality tracking works under resource pressure

4. **Error Handling**:
   - [ ] Specific exception types for different failure modes
   - [ ] Graceful degradation with partial results when possible
   - [ ] Resource cleanup on failure (connections, file handles)
   - [ ] Adversarial: Recovery from disk full, memory exhaustion, network issues

5. **Performance Requirements**:
   - [ ] Response time logged and monitored
   - [ ] Memory usage bounded and documented
   - [ ] Batch operations for efficiency when processing multiple items
   - [ ] Adversarial: Performance maintained under stress conditions

6. **Integration Standards**:
   - [ ] Provenance tracking via T110 for all operations
   - [ ] Identity resolution via T107 for entity references
   - [ ] Quality assessment via T111 for confidence management
   - [ ] Adversarial: Integration works during service degradation

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
- `QDRANT_URL=http://localhost:6333`
- `SQLITE_DB_PATH=./data/metadata.db`

## Testing Strategy (Adversarial-First Approach)

### Test Categories (All Include Adversarial Cases)
- **Unit Tests**: Individual tool functionality + edge case handling
- **Integration Tests**: Multi-tool workflows + failure propagation
- **End-to-End Tests**: Complete pipeline + system-level failures
- **Adversarial Tests**: Deliberate attempts to break each component

### Adversarial Testing Requirements
**Every tool implementation must pass adversarial tests BEFORE integration**:

1. **Input Validation**: Malformed data, extreme values, empty inputs
2. **Resource Limits**: Memory pressure, disk full, timeout scenarios
3. **Concurrency**: Race conditions, deadlocks, data corruption
4. **Error Propagation**: Graceful degradation, partial results, recovery
5. **Edge Cases**: Unicode, special characters, boundary conditions

### Running Tests (Development Workflow)
```bash
# Core adversarial test suite (must pass for each tool)
pytest tests/adversarial/ -v --tool=T107

# All tests including adversarial
pytest tests/ -v --include-adversarial

# Unit tests only (with adversarial cases)
pytest tests/unit/ -v -k "adversarial or edge_case"

# Integration tests with failure injection
pytest tests/integration/ -v --failure-injection

# End-to-end with system stress
pytest tests/e2e/ -v --stress-test

# Coverage (must be >85% including adversarial paths)
pytest --cov=src tests/ --cov-fail-under=85
```

### Validation Gates
**No tool proceeds to next phase without passing**:
- [ ] All unit tests (including adversarial)
- [ ] Integration tests with 2+ tools
- [ ] Resource exhaustion scenarios
- [ ] Error recovery validation
- [ ] Performance under stress

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
2. **Indexing**: Entities → Embeddings → Qdrant Vector Database
3. **Query**: Natural Language → Tool Selection → Graph Operations → Response
4. **Storage**: Neo4j (structure) + Qdrant (semantics) + SQLite (metadata)

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

## Key Principles (Adversarial Development Mindset)

1. **Adversarial First**: Before implementing any tool, design tests to break it
2. **Granular Validation**: Each tool must pass 6+ specific criteria before integration
3. **Minimal + Robust**: Simple implementations that handle edge cases gracefully
4. **Test-Driven Development**: Write adversarial tests before implementation
5. **Incremental + Validated**: One tool at a time, fully validated before proceeding

### Development Checklist (Per Tool)
**Complete this checklist before marking any tool as "done"**:

- [ ] **Design Phase**: List 5+ ways the tool could fail or be misused
- [ ] **Test Suite**: Write adversarial tests for identified failure modes
- [ ] **Implementation**: Code with explicit error handling for each failure mode
- [ ] **Unit Validation**: All tests pass including adversarial cases
- [ ] **Integration Testing**: Tool works with core services under stress
- [ ] **Performance Validation**: Tool performs within documented bounds
- [ ] **Documentation**: Failure modes and recovery procedures documented
- [ ] **Code Review**: Implementation reviewed for missing edge cases

### Red Flags (Stop Development If You See These)
- ❌ "This edge case is unlikely to happen in practice"
- ❌ "We can handle error cases later"
- ❌ "The test suite is comprehensive enough"
- ❌ "Performance is acceptable for now"
- ❌ "Integration works in the happy path"

### Green Flags (Good Adversarial Thinking)
- ✅ "What happens if the input is malformed?"
- ✅ "How does this behave under memory pressure?"
- ✅ "Can we recover gracefully from this failure?"
- ✅ "What partial results can we return on error?"
- ✅ "How do we maintain data integrity during crashes?"

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
│   └── qdrant/         # Vector database
└── scripts/            # Utility scripts
```

## Environment Variables
```bash
# Required
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
SQLITE_DB_PATH=./data/metadata.db
QDRANT_URL=http://localhost:6333

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
- **qdrant-client**: Vector database client
- **sqlalchemy**: SQLite ORM
- **spacy**: NLP processing (T23a)
- **sentence-transformers**: Embeddings (T41)

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Type checking
- **coverage**: Test coverage

## Special Considerations

### Qdrant Vector Database Benefits
Qdrant provides several advantages over FAISS:
1. **Native transactions**: Full ACID compliance with rollback support
2. **Rich filtering**: Combine vector similarity with metadata filtering
3. **Incremental updates**: Update vectors without rebuilding entire index
4. **Integrated metadata**: Store metadata alongside vectors for complex queries

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