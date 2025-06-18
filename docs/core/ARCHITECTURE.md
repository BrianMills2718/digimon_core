# Super-Digimon Architecture

## System Overview

Super-Digimon is a **universal analytical platform** that provides format-agnostic data processing through **121 specialized tools** organized in **8 phases**. The system dynamically selects optimal data structures (graphs, tables, vectors) and seamlessly transforms between formats to enable sophisticated multi-step analytical workflows.

**Key Innovation**: Claude Code serves as the analytical intelligence that interprets natural language requests and orchestrates optimal tool sequences, choosing the most appropriate data format (graph, table, vector) for each analytical step. This enables complex workflows that combine graph algorithms, statistical analysis, machine learning, and visualization in a single coherent process.

## Core Architecture

```
┌─────────────────┐
│  Claude Code    │  Analytical Intelligence
│                 │  • Format Selection
│                 │  • Workflow Orchestration
└────────┬────────┘
         │ Natural Language Analysis
         ▼
┌─────────────────┐
│  MCP Protocol   │  Model Context Protocol
│                 │  • Tool Discovery
│                 │  • Intelligent Routing
└────────┬────────┘
         │ Optimal Tool Sequences
         ▼
┌─────────────────┐
│ Python MCP      │  Universal Tool Platform
│    Server       │  121 Tools (T01-T121)
│                 │  • Multi-format Processing
│                 │  • Dynamic Conversion
└────────┬────────┘
         │
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│ Neo4j  ││ SQLite ││ Qdrant │
│(Graphs)││(Meta)  ││(Vector)│
└────────┘└────────┘└────────┘
```

## Technology Stack

- **Language**: Python 3.11+
- **Analytical Intelligence**: Claude Code (Anthropic) - Format-agnostic reasoning
- **Protocol**: MCP (Model Context Protocol) - Tool integration framework
- **Graph Database**: Neo4j 5.x - Relationship analysis and graph algorithms
- **Vector Store**: Qdrant - Semantic similarity and embedding operations
- **Metadata Store**: SQLite - Configuration, lineage, and structured metadata
- **Containerization**: Docker & Docker Compose - Service orchestration
- **ML/AI**: OpenAI embeddings, Gemini 2.5 Flash, statistical libraries

## Tool Organization (121 Tools)

### Phase Distribution (Universal Analytical Capabilities)
- **Phase 1 - Ingestion** (T01-T12): Multi-format data loading (PDF, CSV, APIs, databases)
- **Phase 2 - Processing** (T13-T30): Format detection, NLP, entity extraction
- **Phase 3 - Construction** (T31-T48): Dynamic structure building (graphs, tables, embeddings)
- **Phase 4 - Retrieval** (T49-T67): Cross-format querying and intelligent data access
- **Phase 5 - Analysis** (T68-T75): Format-specific algorithms (graph, statistical, vector)
- **Phase 6 - Storage** (T76-T81): Multi-database management and optimization
- **Phase 7 - Interface** (T82-T106): Natural language processing, monitoring, export
- **Phase 8 - Core Services** (T107-T121): Identity, quality, versioning, workflow orchestration

## Universal Platform Capabilities

### Format-Agnostic Processing
Unlike traditional systems that lock data into a single format, Super-Digimon enables:

1. **Dynamic Format Selection**: Claude Code analyzes analytical requirements and selects optimal data structures
2. **Seamless Format Conversion**: Tools T115-T118 enable mid-workflow format transformations
3. **Cross-Format Operations**: Combine graph algorithms with statistical analysis in single workflows
4. **Intelligent Routing**: Automatically route analytical requests to most appropriate tool chains

### Example Multi-Format Workflow
```
Scientific Papers (PDF) → 
  Text Extraction (T01) → 
  Entity Recognition (T23b) → 
  Citation Graph (T34) → 
  PageRank Analysis (T68) → 
  Top Authors Table (T115) → 
  Geographic Analysis (Statistical) → 
  Collaboration Network (T116) → 
  Community Detection (T70) → 
  Visualization (T95)
```

### Claude Code's Analytical Intelligence
- **Request Interpretation**: Understands complex analytical requirements from natural language
- **Strategy Planning**: Designs optimal tool sequences considering data characteristics
- **Format Reasoning**: Chooses graphs for relationships, tables for statistics, vectors for similarity
- **Workflow Orchestration**: Manages complex multi-step analytical pipelines
- **Quality Monitoring**: Tracks confidence and quality throughout processing chains

## Key Architectural Decisions

### 1. Single MCP Server
**Decision**: Use one Python MCP server exposing all 121 tools  
**Rationale**: Simpler than federated architecture, sufficient for prototype scope

### 2. Triple Database Architecture
- **Neo4j**: Primary storage for graph structure (nodes, relationships, communities)
- **SQLite**: Metadata storage (documents, chunks, configuration, lineage)
- **Qdrant**: Vector database for semantic similarity, embeddings, and ML operations

**Database Selection Rationale**:
- **Neo4j**: Optimized for complex relationship queries and graph algorithms
- **SQLite**: Lightweight, reliable metadata storage with excellent Python integration
- **Qdrant vs FAISS**: Chosen for flexibility over speed - enables rich filtering, metadata integration, and gradual updates rather than index rebuilds

### 3. Tool Contracts
Tools declare contracts specifying requirements and guarantees:
```python
{
    "required_attributes": {
        "entity": ["canonical_name", "confidence"]
    },
    "required_state": {
        "mentions_created": true,
        "entities_resolved": "optional"  # Domain-specific
    },
    "produced_state": {
        "graph_ready": true
    }
}
```

### 4. Pass-by-Reference Pattern
Graph data passed via unique IDs, not serialized:
```python
return {
    "graph_id": "celestial_council_graph_v1",
    "node_count": 1523,
    "relationship_count": 4892
}
```

### 5. Three-Level Identity System
All text processing maintains three levels of identification:
```
Surface Form → Mention → Entity

Example:
"Apple announced..." → Mention_001 (pos: 0-5) → Entity: Apple Inc.
"AAPL rose 5%..."   → Mention_002 (pos: 0-4) → Entity: Apple Inc.
```

This enables:
- Exact provenance tracking
- Handling ambiguity (Apple Inc. vs apple fruit)
- Multiple surface forms for same entity
- Correction without losing original data

### 6. Optional Entity Resolution
Entity resolution adapts to analytical needs:

**Social Network Analysis** (No Resolution):
```python
# Keep @obama and @barackobama as separate entities
config = {"resolve_entities": false}
# Result: Track different social media personas
```

**Corporate Analysis** (With Resolution):
```python
# Merge "Apple Inc.", "Apple Computer", "AAPL"
config = {"resolve_entities": true}
# Result: Unified view of corporate entity
```

## Implementation Risk Mitigation

### Specification Drift Prevention
- **JSON Schema Validation**: Each tool validates against simple schema
- **Lightweight Contracts**: Basic input/output validation, not full frameworks
- **Manual Review Process**: Regular alignment checks during development

### Performance Bottleneck Prevention
- **Core Services Optimization**: Profile during vertical slice, optimize hot spots
- **Reference-Based Architecture**: Pass IDs, not full objects
- **Async Where Beneficial**: Use asyncio for I/O bound operations
- **Simple Monitoring**: Log timing patterns, identify trends

### PhD-Appropriate Scope
- **Essential Mitigations Only**: Prevent catastrophic problems
- **Defer Complex Infrastructure**: Focus on research goals first
- **Iterative Optimization**: Start simple, optimize when proven necessary

### 7. Universal Quality Tracking
Every data object includes quality metadata:
```python
{
    "data": {...},
    "confidence": 0.87,
    "quality_tier": "high",
    "extraction_method": "llm_v2",
    "warnings": ["OCR quality degraded on page 3"],
    "evidence": ["source_doc_001", "source_doc_002"]
}
```

### 8. Format-Agnostic Processing
Data seamlessly transforms between formats based on analytical needs:
```
Documents → Chunks → Entities/Relations → Graph
                ↓                          ↓
            Embeddings                  Tables
                ↓                          ↓
            Vectors                   Statistics
```

Key tools:
- T115: Graph → Table (for statistical analysis)
- T116: Table → Graph (for graph algorithms)
- T117: Format Auto-Selector

## Core Services Layer

Critical services that support all tools:

### Identity Service (T107)
- Manages three-level identity system
- Creates and resolves mentions
- Merges duplicate entities
- Tracks all surface forms

### Provenance Service (T110)
- Records every operation
- Traces complete lineage
- Enables impact analysis
- Supports reproducibility

### Quality Service (T111)
- Assesses confidence scores
- Propagates uncertainty
- Aggregates quality metrics
- Filters by quality thresholds

### Version Service (T108)
- Four-level versioning (schema, data, graph, analysis)
- Tracks all changes
- Enables rollback
- Supports knowledge evolution

### Workflow State Service (T121)
- Checkpoint workflow progress
- Enable crash recovery
- Support long-running analyses
- Lightweight reference storage

## Data Flow

1. **Ingestion**: Documents → Chunks → Text Processing
2. **Identity Resolution**: Surface Forms → Mentions → Entities
3. **Construction**: Entities/Relations → Graph Building → Embeddings
4. **Storage**: Graph → Neo4j, Vectors → FAISS, Metadata → SQLite
5. **Retrieval**: Query → Tool Selection → Graph Operations → Response
6. **Analysis**: Graph → Algorithms → Insights → Natural Language

## Development Approach

### Vertical Slice First Strategy
Instead of implementing all tools in phases, build one complete workflow first:

**Target**: PDF → PageRank → Answer (2 weeks)
1. **Week 1**: Minimal core services (T107, T110, T111, T121)
2. **Week 2**: Vertical slice tools (T01, T15a, T23a, T31, T34, T76, T68, T49, T90)
3. **Week 3**: Integration testing and architecture validation
4. **Week 4+**: Horizontal expansion based on learnings

### Key Implementation Patterns
- **Reference-based I/O**: All tools use references, not full objects
- **Streaming support**: Handle large datasets incrementally
- **Quality propagation**: Track confidence through pipeline
- **Partial results**: Always return what succeeded
- **Format flexibility**: Convert between graph/table/vector as needed

### Prototype Scope
- **Is**: Functionally complete GraphRAG system
- **Is Not**: Production-ready, multi-user, or performance-optimized

### Non-Goals
- Multi-user authentication
- Production security
- Distributed processing
- Real-time streaming
- Mobile interfaces

## Tool Response Format

All tools return standardized responses:
```python
{
    "status": "success",
    "data": {...},      # Tool-specific data
    "metadata": {       # Optional metadata
        "execution_time": 1.23,
        "tool_version": "1.0.0"
    },
    "error": null       # Error details if failed
}
```

## Error Handling

- Input validation at tool level
- Graceful degradation for missing attributes
- Transaction rollback for graph operations
- Detailed error messages for debugging

## Future Considerations

While not in initial scope, the architecture supports:
- Streaming responses for large datasets
- Federated MCP servers if needed
- Additional graph databases (TypeDB, Amazon Neptune)
- Custom embeddings and LLMs
- Horizontal scaling patterns