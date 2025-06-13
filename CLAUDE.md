# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Super-Digimon is a GraphRAG (Graph Retrieval-Augmented Generation) system that enables natural language querying of graph data. The system combines Neo4j graph storage, FAISS vector search, and SQLite metadata to provide intelligent graph analysis through **106 specialized tools** organized in 7 lifecycle phases.


## Key Commands

### Development Environment
```bash
# Start Neo4j database
cd tools/cc_automator && docker-compose up -d neo4j

# Install dependencies
pip install -r tools/cc_automator/requirements.txt

# Run tests
cd tools/cc_automator && pytest test_files/ -v

# Run specific test
pytest test_files/test_neo4j_integration.py -v

# Check Neo4j status
docker-compose ps neo4j

# View Neo4j logs
docker-compose logs neo4j
```

### Development Workflow
```bash
# Start development environment
cd tools/cc_automator
docker-compose up -d neo4j
python mcp_server.py

# Run validation tests
./run_verification.sh

# Clean up Docker containers
docker-compose down
```

## Architecture Overview

### Core Components
- **Claude Code**: Natural language agent that orchestrates tool execution via MCP
- **Neo4j**: Primary graph database for entities, relationships, and communities
- **FAISS**: Vector search index for semantic similarity
- **SQLite**: Metadata storage for documents and configuration
- **106 MCP Tools**: Complete system implementation across 7 phases (T01-T106)

### Storage Architecture
```
Claude Code (Agent)
      �
MCP Protocol  
      �
Python MCP Servers (106 Tools)
      �
Neo4j (Graphs) + SQLite (Metadata) + FAISS (Vectors)
```

### Tool Categories (106 Tools Across 7 Phases)
- **Phase 1 - Ingestion (T01-T12)**: Document loading, API connectors, database integration
- **Phase 2 - Processing (T13-T30)**: Text cleaning, NLP, entity/relationship extraction  
- **Phase 3 - Construction (T31-T48)**: Graph building, embeddings, vector indexing
- **Phase 4 - Retrieval (T49-T67)**: JayLZhou GraphRAG operators (the core 19 operators)
- **Phase 5 - Analysis (T68-T75)**: Advanced graph algorithms, centrality measures
- **Phase 6 - Storage (T76-T81)**: Database management, backup, caching
- **Phase 7 - Interface (T82-T106)**: Natural language processing, monitoring, export

## Key Files and Directories

### Codebase Structure
- `docs/specifications/`: **AUTHORITATIVE SPECIFICATIONS** for 106 tools
- `tools/cc_automator/`: Neo4j connection code and test infrastructure  
- `test_data/celestial_council/`: Sample datasets for testing
- `config/`: MCP configuration examples

### Architecture Documentation  
- `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`: **Complete 106 tool specifications**
- `docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md`: **Phase breakdown and tool organization**
- `DOCUMENTATION_REVIEW_MASTER.md`: **Multi-pass documentation review tracking**


### Test Infrastructure
- `tools/cc_automator/test_files/`: Comprehensive test suite
- `tools/cc_automator/run_verification.sh`: Automated validation script
- `test_data/celestial_council/`: Sample datasets for testing

## Development Approach

### Implementation Priority
Based on the 106 tool specification:
1. **Phase 1-3**: Infrastructure, processing, construction (48 tools) - Foundation
2. **Phase 4**: JayLZhou GraphRAG operators (19 tools) - Core functionality  
3. **Phase 5-7**: Analysis and interface (39 tools) - Advanced features

### Technical Patterns
- **Attribute-Based Tool System**: Tools declare requirements, not fixed graph types
- **MCP Protocol**: All 106 tools exposed via Model Context Protocol
- **Pass-by-Reference**: Efficient handling of large graph data
- **Phase-Based Development**: Implement tools in dependency order

## Database Configuration

### Neo4j Connection
- Default URL: `bolt://localhost:7687`
- Default credentials: `neo4j/password`
- HTTP interface: `http://localhost:7474`

### Environment Variables
Key variables in `tools/cc_automator/.env`:
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `NEO4J_DATABASE`, `COMPOSE_PROJECT_NAME`

## Testing Strategy

### Test Categories
- Unit tests: Individual component functionality
- Integration tests: Multi-component interactions  
- E2E tests: Complete workflow validation
- Performance tests: System benchmarking

### Running Tests
```bash
# All tests
pytest tools/cc_automator/test_files/ -v

# Specific milestone tests
pytest tools/cc_automator/test_files/test_m2_*.py -v

# Neo4j integration only
pytest tools/cc_automator/test_files/test_neo4j_integration.py -v
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
- Performance optimization (yet)
- Advanced features like TypeDB or hypergraphs

## Data Flow

1. **Ingestion**: Documents � Chunks � Entities/Relationships � Graph
2. **Indexing**: Entities � Embeddings � FAISS Vector Index
3. **Query**: Natural Language � Tool Selection � Graph Operations � Response
4. **Storage**: Neo4j (structure) + FAISS (semantics) + SQLite (metadata)

## Quick Start for New Contributors

### Understanding the System
1. **Read specifications**: `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`
2. **Understand tool organization**: `docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md`
3. **Review architecture**: `docs/architecture/CANONICAL_ARCHITECTURE.md`

### Development Setup
1. Start Neo4j: `cd tools/cc_automator && docker-compose up -d neo4j`
2. Install deps: `pip install -r tools/cc_automator/requirements.txt`
3. Run connection tests: `pytest tools/cc_automator/test_files/test_simple_neo4j.py -v`
4. Begin with Phase 1 tools (T01-T12) - Ingestion

## Implementation Roadmap

### Phase 1: Foundation
- Implement T01-T12 (Ingestion): Document loaders, API connectors
- Implement T76-T81 (Storage): Database management
- Set up basic infrastructure

### Phase 2: Processing
- Implement T13-T30 (Processing): NLP, entity extraction
- Build text processing pipeline

### Phase 3: Graph Construction
- Implement T31-T48 (Construction): Graph building, embeddings
- Create vector indexing system

### Phase 4: Core GraphRAG
- Implement T49-T67 (Retrieval): JayLZhou operators
- Core GraphRAG functionality

### Phase 5: Advanced Features
- Implement T68-T75 (Analysis): Graph algorithms
- Implement T82-T106 (Interface): UI, monitoring, export

## Communication Guidelines for Technical Discussions

**IMPORTANT**: When discussing technical topics or architecture decisions with the user:

1. **Always provide choices**: Present 2-3 clear options
2. **Explain tradeoffs**: Benefits and drawbacks of each option
3. **Give recommendation**: Your expert opinion with reasoning
4. **Document decisions**: All choices made should be recorded in ARCHITECTURAL_DECISIONS.md

**Example Format**:
```
**Options**:
A) Single MCP server - Simple but less scalable
B) Federated MCP - Complex but more scalable  
C) Hybrid approach - Balanced complexity/scalability

**Tradeoffs**: [Detailed comparison]
**Recommendation**: Option B because [reasoning]
```

## Development Considerations

Key areas for planning:
1. **Architecture validation**: Confirm technical approach is sound
2. **Tool dependencies**: Understand relationships between 106 tools
3. **Resource requirements**: Assess complexity of 106-tool system implementation
4. **Testing strategy**: Comprehensive validation approach