# Super-Digimon Architecture Decisions

## Overview
This document captures the key architectural decisions made for Super-Digimon implementation based on critical analysis and discussion.

## Core Decisions

### 1. **Compatibility Matrix - Simple Attribute-Based Approach**
```python
# Data structures have attributes
class Graph:
    attributes = {'nodes', 'edges', 'node_id', 'edge_source', 'edge_target'}

# Operators declare what they need
class PageRankOperator:
    requires = {'nodes', 'edges', 'edge_source', 'edge_target'}
    produces = {'pagerank_scores'}

# Simple compatibility check
def can_apply(operator, data_structure):
    return operator.requires.issubset(data_structure.attributes)
```

**Rationale**: Simple, clear, debuggable. Handles 90% of cases without complexity.

---

### 2. **Data Storage - Shared Storage Service**
```python
# Tools pass data IDs, storage service handles the data
storage = StorageService()  # Start with filesystem + JSON
graph_id = storage.put(graph_data)
result_id = tool.analyze(graph_id)
```

**Implementation Plan**:
- Phase 1: Filesystem + JSON (MVP, works to ~100K nodes)
- Phase 2: Add disk-backed storage (works to ~1M nodes)
- Phase 3: Distributed storage only if needed

**Rationale**: Handles large data, keeps tools stateless, clean MCP integration.

---

### 3. **Tool vs Data Structure - Clean Separation**
```python
# Data structures are pure data
graph_data = GraphData(nodes=[...], edges=[...])

# Tools are stateless operators
pagerank_tool = PageRankTool()
result = pagerank_tool.compute(graph_id)
```

**Rationale**: Clean MCP integration, tools can be swapped/upgraded, follows MCP patterns.

---

### 4. **MCP Message Pattern - Pass by Reference**
```python
# Never send large data over JSON-RPC
@mcp_tool
def analyze(data_id: str) -> str:
    data = storage.get(data_id)
    result = process(data)
    return storage.put(result)
```

**Exception**: Small data (<1000 nodes) can pass directly for convenience.

**Rationale**: Works for any size data, fast tool communication.

---

### 5. **Database Integration - Smart Routing**
```python
def load_from_database(query, size_check=True):
    if size_check and db.estimate_size(query) > 100_000:
        # Big data: analyze in database
        return db.analyze_in_place(query)
    else:
        # Small data: extract to memory
        return db.query_to_table(query)
```

**Note**: Start with simple extraction, add in-DB computation only if needed.

**Rationale**: Optimal performance, handles all scales, pragmatic approach.

---

### 6. **Tool Composition - Agent Orchestration + Pipeline DSL**

**Agent Orchestration**:
```python
# Read-only tools in parallel
results = await asyncio.gather(*[tool.execute() for tool in readonly_tools])

# Write tools sequential
for tool in write_tools:
    result = await tool.execute()
```

**Pipeline DSL with Progressive Enhancement**:
```python
# Simple format
pipeline = "csv_load | graph_build | pagerank"

# With inline parameters
pipeline = "csv_load(file='data.csv') | graph_build | pagerank(alpha=0.85)"

# With separate params (for complex cases)
pipeline = "csv_load | graph_build | pagerank"
params = {
    "csv_load": {"file": "data.csv"},
    "pagerank": {"alpha": 0.85}
}
```

**Rationale**: Best of both worlds - flexibility of agent, reusability of pipelines.

---

### 7. **State Management - Explicit Context Passing**
```python
@dataclass
class AnalysisContext:
    session_id: str
    decisions: Dict[str, Any]  # "influence" → "pagerank"
    data_lineage: List[str]
    user_preferences: Dict

# Tools receive and return context
def execute_tool(tool, data_id, context: AnalysisContext):
    result = tool.run(data_id, context)
    new_context = context.add_decision(tool.name, result.params)
    return result, new_context
```

**Rationale**: Maximum visibility and debuggability, fully traceable.

---

### 8. **Pipeline Compatibility Matrix**
```python
class PipelineCompatibility:
    # Which tools can connect
    connections = {
        ('csv_load', 'graph_build'): True,
        ('graph_build', 'pagerank'): True,
        ('pagerank', 'csv_export'): True,
        ('pagerank', 'statistics'): False,  # Needs adapter
    }
    
    # Auto-adapter insertion
    adapters = {
        ('graph', 'table'): 'graph_to_table',
        ('table', 'graph'): 'table_to_graph'
    }
```

**Rationale**: Enables pipeline validation and automatic adapter insertion.

---

### 9. **Attribute Type System - Progressive Enhancement**
```python
# Start simple (MVP)
attributes = {'nodes', 'edges'}

# Add types when needed
attributes = {
    'nodes': List[Node],
    'edges': List[Edge]
}

# Add constraints when problems arise
attributes = {
    'edges': {
        'type': List[Tuple[str, str]],
        'constraints': {'directed': True}
    }
}
```

**Rationale**: Start simple, enhance based on real needs.

---

### 10. **Aggregate Tools Pattern**
```python
@aggregate_tool("influence_analysis")
class InfluenceAnalysis:
    pipeline = "csv_load | graph_build | pagerank | community_detect"
    
    default_params = {
        'pagerank': {'alpha': 0.85},
        'community_detect': {'method': 'louvain'}
    }
    
    def customize(self, param_overrides: Dict):
        params = {**self.default_params, **param_overrides}
        return execute_pipeline(self.pipeline, params)
```

**Rationale**: Reusable analyses, SME-friendly, versionable.

---

## Implementation Priorities

### Week 1:
1. Basic data structures (Graph, Table, Document) with attributes
2. Storage service (filesystem + JSON)
3. 5 core tools with MCP interfaces
4. Simple pipeline DSL parser
5. First end-to-end test

### Week 2:
1. Explicit context system
2. Pipeline compatibility matrix
3. Auto-adapter insertion
4. 10+ tools integrated
5. First aggregate tool

### Week 3:
1. Smart database routing
2. Agent orchestration
3. Full 26 operators
4. Multiple aggregate tools
5. Scale testing to 1M nodes

## Key Principles

1. **Start Simple**: Use simplest approach that works, enhance when needed
2. **Explicit Over Implicit**: Visible state, clear data flow
3. **Reference Over Value**: Pass IDs for large data
4. **Progressive Enhancement**: Simple cases simple, complex cases possible
5. **Real Testing**: No mocks, actual API calls, real data

## Additional Architecture Decisions

### 11. **Storage Service - Docker Shared Volume**
```yaml
# docker-compose.yml
services:
  storage:
    image: nginx:alpine  # Simple file server
    volumes:
      - ./storage:/usr/share/nginx/html:ro
      - ./storage-write:/write:rw
      
  mcp-tool:
    volumes:
      - ./storage-write:/storage:rw  # All tools share same volume
```

**Rationale**: Simple, works immediately, easy debugging. Plan to migrate to MinIO (S3-compatible) if scaling beyond single machine.

---

### 12. **MCP Tool Granularity - Single Server**
```python
@mcp_server
class SuperDigimonServer:
    @endpoint("/entity_vdb_search")
    def entity_vdb_search(self, params): ...
    
    @endpoint("/pagerank")
    def pagerank(self, params): ...
    # ... all 26 tools as endpoints
```

**Rationale**: Single process to manage, shared context easy, lower resource usage. Can split later if needed.

---

### 13. **Pipeline DSL - Pydantic-Based Parsing**
```python
class Pipeline(BaseModel):
    steps: List[ToolCall]
    
    @classmethod
    def from_string(cls, dsl: str) -> 'Pipeline':
        """Parse DSL with basic string parsing + Pydantic validation"""
        
    def to_string(self) -> str:
        """Convert back to DSL format"""
```

**Rationale**: Consistent with rest of system, automatic validation, type safety, simpler than full parser.

---

### 14. **Entity Resolution - Post-MVP**
Entity resolution (deduplication, matching "DoD" = "Department of Defense") is deferred to post-MVP phase as a graph post-processing step.

**Rationale**: Can demonstrate core functionality without it, adds complexity that isn't needed for initial validation.

---

### 15. **Test Data - Synthetic Fictional Dataset**
```python
# Celestial Council fictional social network
- 100-1M fictional beings (no real names)
- Made-up relationships and content
- Scaled versions: small (100), medium (10K), large (1M)
```

**Rationale**: Avoids LLM using general knowledge, no copyright issues, fully controlled ground truth.

---

### 16. **Development Environment - Local Python with Docker Services**
```bash
# Local development in WSL/Ubuntu
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Docker only for external services
docker-compose -f docker-compose.services.yml up -d
```

**Services-only Docker compose**:
```yaml
services:
  redis:
    image: redis:alpine
    ports: ["6379:6379"]
  
  storage:  # Simple file server
    image: nginx:alpine
    volumes:
      - ./storage:/usr/share/nginx/html
    ports: ["8080:80"]
```

**Rationale**: 
- User has Python installed locally on WSL/Ubuntu
- Simpler development workflow (instant code changes)
- Avoid Docker complexity for Python code
- Use Docker only for external services
- Later create production Dockerfile

**WSL Best Practices**:
- Store code in WSL filesystem (~/projects) not /mnt/c/
- Use `code .` for VS Code WSL integration

---

## Out of Scope

- Multi-user collaboration
- Fixed failure recovery patterns (agent handles)
- Security/access control
- Production deployment optimization
- Evaluation metrics (until system works)
- UI (CLI first, UI last)
- Entity resolution (post-MVP)