# ADR-026: Cross-Modal REST API for Local Automation

**Status**: Accepted  
**Date**: 2025-07-26  
**Author**: KGAS Development Team

## Context

The KGAS system currently provides cross-modal analysis capabilities (Graph ↔ Table ↔ Vector conversions) through:
1. Direct Python library usage
2. MCP protocol for LLM orchestration (Claude Desktop)

While these interfaces work well for their intended use cases, users need additional flexibility for:
- Building custom local web interfaces for their research workflows
- Automating repetitive analysis tasks through scripts
- Integrating KGAS capabilities with other local tools (Jupyter, R, etc.)
- Creating specialized UIs for specific research domains

This is NOT about:
- Exposing the system to other users or the internet
- Creating a cloud service
- Sharing data with external systems
- Replacing the existing MCP interface

## Decision

We will implement a **local-only REST API** using FastAPI that provides high-level endpoints for cross-modal analysis operations. This API will:

1. **Run locally only** - Bound to localhost (127.0.0.1) by default
2. **Complement MCP** - Not replace the existing MCP server
3. **Provide high-level operations** - Document analysis, format conversion, mode recommendation
4. **Support automation** - Batch processing, async operations, progress tracking
5. **Enable custom UIs** - CORS support for local web applications

## Rationale

### Why REST API?

1. **Universal compatibility**: Works with any programming language or tool
2. **Simple integration**: Standard HTTP requests, no special clients needed
3. **Web UI support**: Enables building custom browser-based interfaces
4. **Automation friendly**: Easy to use in scripts and workflows

### Why FastAPI?

1. **Already in use**: KGAS already uses FastAPI patterns
2. **Async native**: Matches KGAS async architecture
3. **Auto-documentation**: OpenAPI/Swagger UI included
4. **Type safety**: Pydantic models ensure data validation

### Why Local-Only?

1. **Security**: No external access to user's research data
2. **Simplicity**: No authentication complexity for single-user system
3. **Performance**: No network latency for large document processing
4. **Privacy**: All data stays on the user's machine

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              User's Local Machine                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Applications:                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │Python Script│  │ Web Browser │  │   Jupyter   │ │
│  │  (requests) │  │(React/Vue)  │  │  Notebook   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                 │                 │        │
│         └─────────────────┼─────────────────┘        │
│                           │                          │
│                    HTTP (localhost:8000)             │
│                           │                          │
│              ┌────────────▼────────────┐             │
│              │   FastAPI REST Server   │             │
│              │  ┌─────────────────┐   │             │
│              │  │  /api/analyze   │   │             │
│              │  │  /api/convert   │   │             │
│              │  │  /api/recommend │   │             │
│              │  └─────────────────┘   │             │
│              └────────────┬────────────┘             │
│                           │                          │
│              ┌────────────▼────────────┐             │
│              │ Cross-Modal Services    │             │
│              │ (Service Registry)      │             │
│              └─────────────────────────┘             │
│                                                     │
│  Also Available:                                   │
│  ┌─────────────────────────────────────┐           │
│  │  MCP Server (for Claude Desktop)    │           │
│  └─────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘
```

## Implementation Details

### Core Endpoints

```python
# Document Analysis
POST /api/analyze
  - Upload document (PDF, Word, etc.)
  - Returns extracted entities, relationships, embeddings
  
# Format Conversion  
POST /api/convert
  - Convert data between Graph ↔ Table ↔ Vector
  - Preserves source traceability
  
# Mode Recommendation
POST /api/recommend
  - Get AI-recommended analysis mode for task
  - Returns confidence scores and reasoning

# Batch Operations
POST /api/batch/analyze
  - Process multiple documents
  - Returns job ID for tracking
  
GET /api/jobs/{job_id}
  - Check batch job status
  - Get results when complete
```

### Security Model

1. **Default**: Localhost only (127.0.0.1:8000)
2. **Optional**: API key for local app authentication
3. **CORS**: Configured for local origins only
4. **File uploads**: Size limits and type validation
5. **No external access**: Firewall/binding prevents external connections

### Example Usage

```python
# Python script example
import requests

# Analyze a research paper
with open("paper.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": f},
        data={"target_format": "graph", "task": "extract entities"}
    )
    
results = response.json()
print(f"Found {len(results['entities'])} entities")
print(f"Found {len(results['relationships'])} relationships")

# Convert to table format for statistical analysis
table_response = requests.post(
    "http://localhost:8000/api/convert",
    json={
        "data": results["graph"],
        "source_format": "graph",
        "target_format": "table"
    }
)

table_data = table_response.json()["data"]
# Now use in pandas, R, Excel, etc.
```

## Consequences

### Positive

1. **Flexibility**: Users can build custom tools and interfaces
2. **Automation**: Repetitive tasks can be scripted
3. **Integration**: Works with existing research tools
4. **Simplicity**: Standard REST API is easy to understand
5. **Local control**: Everything stays on user's machine

### Negative

1. **Additional component**: One more service to maintain
2. **Documentation needs**: Must document API endpoints
3. **Version management**: API versioning considerations
4. **Resource usage**: Additional process running locally

### Neutral

1. **Development effort**: Moderate - reuses existing services
2. **Testing needs**: Requires API-level tests
3. **Future evolution**: May need GraphQL or WebSocket support later

## Alternatives Considered

### 1. **Extend MCP Server**
- **Rejected**: MCP is designed for LLM tool calling, not general HTTP
- Would complicate the clean MCP protocol implementation

### 2. **Direct Python Package Only**
- **Rejected**: Doesn't enable web UIs or cross-language integration
- Already available, this adds new capabilities

### 3. **GraphQL Instead of REST**
- **Rejected**: REST is simpler for document upload operations
- Could add GraphQL later if needed for complex queries

### 4. **gRPC API**
- **Rejected**: More complex, less universal than REST
- REST is sufficient for local automation needs

## Implementation Plan

1. **Phase 1**: Core endpoints (analyze, convert, recommend)
2. **Phase 2**: Batch operations and job tracking
3. **Phase 3**: WebSocket support for real-time updates
4. **Phase 4**: Client libraries (Python SDK, JavaScript SDK)

## Success Metrics

1. **User productivity**: Reduced time for repetitive analyses
2. **Integration count**: Number of user tools integrated
3. **API usage**: Adoption by users for automation
4. **Performance**: Response times for common operations

## Future Considerations

1. **Plugin system**: Allow users to add custom endpoints
2. **Workflow templates**: Pre-built analysis pipelines
3. **Export formats**: Direct integration with citation managers
4. **Visualization API**: D3.js compatible data endpoints

This REST API will empower users to build their own tools and automate their research workflows while keeping all data and processing local to their machine.