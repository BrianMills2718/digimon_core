# CLAUDE.md

This file guides Claude Code through the Super-Digimon implementation. It travels with every session to provide actionable context and success criteria.

## Current Status

**Documentation**: Complete ✅  
**Implementation**: 0% - Starting Phase 0 (Core Services)  
**Databases**: Docker containers ready, connections not tested  
**Next Priority**: Implement T107 Identity Service with full adversarial testing

## Milestones

### Milestone 1: Core Services Complete (Phase 0)
- [ ] T107 Identity Service - Entity resolution with embeddings
- [ ] T110 Provenance Service - Operation tracking  
- [ ] T111 Quality Service - Confidence propagation
- [ ] T121 Workflow State - Checkpoint/restore
- [ ] All adversarial tests passing
- [ ] Integration tests between core services

### Milestone 2: Vertical Slice Working (Phase 1)
- [ ] PDF → PageRank → Answer pipeline functional
- [ ] All 8 tools integrated and tested
- [ ] End-to-end test completing in <5 minutes
- [ ] Quality metrics tracked throughout pipeline

## Implementation Phases

### Phase 0: Core Services (Current Priority)
Build these BEFORE any other tools. They are dependencies for everything else.

#### T107: Identity Service (Start Here)
**Purpose**: Convert mentions → entities with deduplication  
**Location**: `src/core/identity_service.py`  
**Key Methods**:
```python
def create_mention(surface_text, doc_id, position) -> str
def link_mention_to_entity(mention_id, entity_id) -> bool
def merge_entities(entity_ids: List[str]) -> str
def find_similar_entities(text: str, threshold=0.85) -> List[Entity]
```

**Implementation Steps**:
1. Create SQLite schema for mentions/entities (see `docs/core/DATABASE_INTEGRATION.md`)
2. Integrate OpenAI embeddings for similarity (text-embedding-3-small, 1536 dims)
3. Use Qdrant for vector similarity search
4. Implement three-level hierarchy: Surface → Mention → Entity

**Success Criteria**:
- [ ] 100 random names → no false merges
- [ ] "Apple Inc" and "AAPL" → same entity (with embeddings)
- [ ] "Apple" (fruit) and "Apple Inc" → different entities (context-aware)
- [ ] Unicode handling: "Zürich", "São Paulo", emoji names
- [ ] Performance: <100ms for similarity search

**Adversarial Tests** (Must Pass ALL):
```python
# tests/unit/test_identity_service_adversarial.py
- Empty strings, None values
- 10,000 character names
- Duplicate surface forms in same document
- Concurrent entity creation (threading)
- Embedding service timeout simulation
```

#### T110: Provenance Service
**After T107 works perfectly**  
See `docs/core/SPECIFICATIONS.md#T110` for details

#### T111: Quality Service  
**After T110 works perfectly**  
See `docs/core/SPECIFICATIONS.md#T111` for details

#### T121: Workflow State Service
**After T111 works perfectly**  
See `docs/core/SPECIFICATIONS.md#T121` for details

### Phase 1: Vertical Slice (After ALL Phase 0 passes)
Only start after Phase 0 is rock-solid with all adversarial tests passing.

**Tools in Order**:
1. T01: PDF Loader → See `docs/core/SPECIFICATIONS.md#T01`
2. T15a: Text Chunker → See `docs/core/SPECIFICATIONS.md#T15a`
3. T23a: spaCy NER → See `docs/core/SPECIFICATIONS.md#T23a`
4. T27: Relationship Extractor → See `docs/core/SPECIFICATIONS.md#T27`
5. T31: Entity Builder → See `docs/core/SPECIFICATIONS.md#T31`
6. T34: Edge Builder → See `docs/core/SPECIFICATIONS.md#T34`
7. T68: PageRank → See `docs/core/SPECIFICATIONS.md#T68`
8. T49: Multi-hop Query → See `docs/core/SPECIFICATIONS.md#T49`

**End-to-End Test**: `tests/e2e/test_pdf_to_answer.py`
- Load PDF → Extract entities → Build graph → Run PageRank → Query for answers
- Must complete in <5 minutes for 50-page PDF

## Development Standards

### Code Quality Requirements
- **Linting**: All code must pass `flake8 --max-line-length=100`
- **Type Checking**: All code must pass `mypy --strict`
- **Testing**: All tests must pass with `pytest -v`
- **Entry Point**: `main.py` must run successfully
- **Docstrings**: All public functions need Google-style docstrings

### Self-Healing Patterns
When implementing, ALWAYS follow these patterns to prevent common failures:

1. **Use pathlib for all file operations**
   ```python
   # Good: Portable and robust
   from pathlib import Path
   config_path = Path(__file__).parent / "config.json"
   
   # Bad: Breaks on different systems
   config_path = "/home/user/project/config.json"
   ```

2. **Handle missing dependencies gracefully**
   ```python
   # Good: Fallback behavior
   try:
       import optional_library
       HAS_OPTIONAL = True
   except ImportError:
       HAS_OPTIONAL = False
       
   # Bad: Crashes on import
   import optional_library  # Fails if not installed
   ```

3. **Validate inputs with clear errors**
   ```python
   # Good: Helpful error message
   if not isinstance(confidence, float) or not 0 <= confidence <= 1:
       raise ValueError(f"Confidence must be float between 0 and 1, got {confidence}")
       
   # Bad: Generic error
   assert 0 <= confidence <= 1
   ```

4. **Use connection pools for databases**
   ```python
   # Good: Reuse connections
   from neo4j import GraphDatabase
   _driver = None
   
   def get_driver():
       global _driver
       if _driver is None:
           _driver = GraphDatabase.driver(uri, auth=(user, password))
       return _driver
       
   # Bad: New connection every time
   def query():
       driver = GraphDatabase.driver(...)  # Expensive!
   ```

5. **Return partial results on failure**
   ```python
   # Good: Return what succeeded
   results = {"successful": [], "failed": []}
   for item in items:
       try:
           results["successful"].append(process(item))
       except Exception as e:
           results["failed"].append({"item": item, "error": str(e)})
   return results
   
   # Bad: All or nothing
   return [process(item) for item in items]  # One failure loses everything
   ```

## Critical Implementation Rules

### 1. Database Setup First
```bash
# Start databases
docker-compose up -d

# Verify connections
python scripts/test_database_connections.py

# Initialize schemas
python scripts/init_databases.py
```

### 2. Test-Driven Development
**Never implement without tests first**:
1. Write unit test with expected behavior
2. Write adversarial test with edge cases
3. Implement minimal code to pass
4. Refactor only after tests pass

### 3. Use Enhanced Services
The project has enhanced versions with LLM integration:
- `src/core/enhanced_identity_service.py` - Uses OpenAI embeddings
- Uses Gemini 2.0 Flash for structured entity extraction
- See `.env` for API keys (already configured)

### 4. Quality Gates
**Before marking ANY tool complete**:
- [ ] All unit tests pass
- [ ] All adversarial tests pass  
- [ ] Integration with dependent tools tested
- [ ] Performance benchmarked and acceptable
- [ ] Error handling for all failure modes
- [ ] Logging at appropriate levels

### 5. Reference Pattern
Always use format: `{storage}://{type}/{id}`
- `neo4j://entity/ent_123`
- `sqlite://mention/men_456`  
- `qdrant://embedding/emb_789`

## Environment Variables

Required in `.env` file:
```bash
# Database Connections
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
SQLITE_DB_PATH=./data/metadata.db
QDRANT_URL=http://localhost:6333

# API Keys (already configured)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Optional
LOG_LEVEL=INFO
CACHE_DIR=./data/cache
```

## Project Structure (Key Files for Current Phase)

```
Digimons/
├── main.py                    # MCP server entry point
├── .env                       # Environment variables (API keys configured)
├── docker-compose.yml         # Database services
├── src/
│   ├── core/                  # Core services (implement here)
│   │   ├── identity_service.py         # T107 - Create this
│   │   ├── enhanced_identity_service.py # Reference implementation
│   │   └── __init__.py
│   └── mcp_server.py          # MCP server (update with T107)
└── tests/
    └── unit/
        ├── test_identity_service.py           # Create this
        └── test_identity_service_adversarial.py # Create this
```

## Key Resources

**Specifications**: `docs/core/SPECIFICATIONS.md` - Detailed tool contracts  
**Architecture**: `docs/core/ARCHITECTURE.md` - System design and patterns  
**Database Schema**: `docs/core/DATABASE_INTEGRATION.md` - Table definitions  
**Design Patterns**: `docs/core/DESIGN_PATTERNS.md` - Pass-by-reference, etc.  
**Test Examples**: `tests/` - Reference implementations

## Common Pitfalls to Avoid

1. **Starting Phase 1 before Phase 0 is perfect** - Core services are foundations
2. **Skipping adversarial tests** - They prevent production failures
3. **Not using the enhanced services** - They already handle embeddings/LLMs
4. **Implementing all tools at once** - Vertical slice proves the architecture
5. **Ignoring confidence scores** - Quality tracking is mandatory

## Next Immediate Actions

1. [ ] Run `docker-compose up -d` to start databases
2. [ ] Create `src/core/identity_service.py` with minimal T107 implementation
3. [ ] Write `tests/unit/test_identity_service.py` with basic tests
4. [ ] Write `tests/unit/test_identity_service_adversarial.py` with edge cases
5. [ ] Implement T107 until ALL tests pass
6. [ ] Only then proceed to T110

Remember: **Quality over speed**. Each tool must be bulletproof before moving on.