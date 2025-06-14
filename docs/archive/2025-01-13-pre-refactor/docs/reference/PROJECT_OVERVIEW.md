# Super-Digimon Project Overview (Concise)

## What We're Building
**Super-Digimon**: A GraphRAG meta-analytic platform that lets researchers ask questions about graph data in natural language using Claude Code.

## Core Architecture
```
Natural Language → Claude Code → MCP Tools → Storage → Response
```

### Storage (Triple Database)
- **Neo4j**: Graph data (entities, relationships, communities)
- **SQLite**: Metadata (documents, config, history)
- **FAISS**: Vector embeddings

### Tools Needed: 106 Tools Across 7 Phases
- **Phase 1-3 (T01-T48)**: Data pipeline - ingestion, processing, construction
- **Phase 4 (T49-T67)**: Core GraphRAG retrieval operators
- **Phase 5-7 (T68-T106)**: Advanced analysis, storage, and interface tools

**Complete specifications**: See `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md`

## Docker Development Approach
**Key Decision**: Hybrid approach - Docker for services + local Python for development

### What's in Docker:
- Neo4j database (always)
- Future: Vector DB (Qdrant/Weaviate)
- Future: Redis, monitoring

### What's NOT in Docker (during dev):
- Python MCP servers (run locally for hot reloading)
- TypeScript visualization (npm run dev)
- Claude Code (installed globally)

### Development Workflow:
```bash
# 1. Start Docker services (databases only)
docker-compose up -d

# 2. Set up local Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run Python code locally (with hot reload)
python -m super_digimon.mcp_server
```

**Why this approach?**
- Fast iteration (no Docker rebuild for code changes)
- Consistent database environment
- Same Docker images work in production

## Current Status
- ✅ Cleaned repository (removed legacy implementations)
- ✅ Working Neo4j integration from cc_automator
- ✅ Complete documentation and planning
- ✅ Test data (Celestial Council)
- 🚧 Ready to build Super-Digimon from specifications

## Key Design Decisions
1. **No PydanticAI** - Use Python type hints
2. **Pass-by-reference** - Large data referenced by ID
3. **Graph-type aware** - Different operators for different graphs
4. **Prototype first** - Make it work, then optimize

## Foundation Resources
- **Historical Patterns**: Reference patterns documented in archive
- **cc_automator**: Development framework with Neo4j integration
- **Specifications**: Complete tool and architecture documentation
- **Test Data**: Celestial Council dataset ready to use

## Implementation Order
1. **Project structure** (super_digimon/ folder)
2. **Base infrastructure** (MCP server, tool interface)
3. **Storage connections** (Neo4j, SQLite, FAISS)
4. **Core tools** (T01-T08: ingestion and construction)
5. **Retrieval operators** (T49-T67: the 19 JayLZhou operators in Phase 4)
6. **Extensions** (T20-T26+: additional capabilities)

## Next Immediate Steps
1. Create project structure
2. Set up Docker services (Neo4j)
3. Create base MCP server
4. Implement tool interface
5. Start with T01: Document Loader

## Remember
- We have complete specifications to implement from scratch
- Docker is for databases only during development
- Claude Code is the runtime, not something we implement
- 106 tools covering GraphRAG, SQL/table analysis, monitoring, and more