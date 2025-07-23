# ADR-013: MCP Protocol Integration

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: System requires standardized tool interface protocol for exposing analysis capabilities to external clients and enabling tool composition workflows.

## Decision

We will integrate the **Model Context Protocol (MCP)** as the standard interface for exposing KGAS tools:

```python
# MCP integration pattern
from fastmcp import FastMCP

app = FastMCP("KGAS Analysis Tools")

@app.tool()
def extract_entities(
    text: str,
    entity_types: List[str] = ["PERSON", "ORG", "CONCEPT"]
) -> Dict[str, List[Dict]]:
    """Extract entities from text using SpaCy NER with academic research optimization."""
    service_manager = ServiceManager()
    tool = T23aSpacyNERUnified(service_manager=service_manager)
    
    result = tool.execute(ToolRequest(
        tool_id="T23A",
        operation="extract_entities",
        input_data={"text": text, "entity_types": entity_types}
    ))
    
    return result.data if result.status == "success" else {"error": result.error}
```

### **Core Integration Principles**
1. **Standard interface**: All KGAS tools exposed via MCP protocol
2. **Tool composition**: MCP enables chaining tools for complex workflows  
3. **External integration**: MCP allows integration with Claude, other AI systems
4. **Academic workflow support**: MCP tools designed for research use cases

## Rationale

### **Why MCP Protocol?**

**1. Academic Research Integration**:
- **AI-assisted research**: Researchers can use Claude/GPT to orchestrate complex analysis workflows
- **Tool discoverability**: MCP provides standardized tool discovery and documentation
- **Workflow automation**: AI systems can chain KGAS tools for multi-step research analysis
- **Research reproducibility**: MCP tool calls create auditable workflow records

**2. Standardized Tool Interface**:
- **Type safety**: MCP enforces type-safe tool interfaces with JSON Schema validation
- **Documentation**: Built-in tool documentation and help system
- **Error handling**: Standardized error reporting and recovery mechanisms
- **Versioning**: Tool interface versioning for backward compatibility

**3. External Integration Capabilities**:
- **Claude integration**: Direct integration with Claude for AI-assisted research
- **Tool ecosystem**: Compatibility with broader MCP tool ecosystem
- **Academic software**: Integration with other academic research tools using MCP
- **Workflow systems**: Integration with academic workflow management systems

### **Why Not Alternative Protocol Approaches?**

**REST API**:
- ❌ **More implementation overhead**: Requires full HTTP server implementation
- ❌ **Less type safety**: JSON REST APIs lack built-in type validation
- ❌ **Manual documentation**: Requires separate API documentation maintenance
- ❌ **Limited tool composition**: No built-in support for tool chaining workflows

**GraphQL**:
- ❌ **Complexity overhead**: GraphQL adds significant complexity for simple tool interfaces
- ❌ **Academic research mismatch**: GraphQL optimized for data queries, not tool execution
- ❌ **Limited AI integration**: No specific support for AI tool orchestration
- ❌ **Learning curve**: Requires GraphQL expertise for researchers and developers

**Python API Only**:
- ❌ **Language limitation**: Restricts integration to Python-only environments
- ❌ **No external access**: Cannot be accessed by external AI systems or tools
- ❌ **Limited composition**: No standardized way to chain tools across different systems
- ❌ **Academic workflow isolation**: Cannot integrate with broader academic tool ecosystem

**Custom Protocol**:
- ❌ **Implementation burden**: Requires designing, implementing, and maintaining custom protocol
- ❌ **No ecosystem**: Lacks existing tool ecosystem and client implementations
- ❌ **Documentation overhead**: Requires custom documentation and client libraries
- ❌ **Integration barriers**: Other systems would need custom integration code

## Alternatives Considered

### **1. Pure REST API Architecture**
```python
# Rejected approach
@app.route('/api/v1/extract_entities', methods=['POST'])
def extract_entities_rest():
    data = request.get_json()
    # Process and return JSON response
```

**Rejected because**:
- **More boilerplate**: Requires manual request parsing, validation, error handling
- **Less type safety**: Manual JSON schema validation and type checking
- **Documentation overhead**: Requires separate OpenAPI/Swagger documentation
- **Limited AI integration**: No built-in support for AI tool orchestration

### **2. Direct Python API Only**
```python
# Rejected approach - no external interface
class KGASTools:
    def extract_entities(self, text: str) -> List[Entity]:
        # Direct Python API only
```

**Rejected because**:
- **No external access**: Cannot be used by Claude, other AI systems, or external tools
- **Limited workflow automation**: No way to chain tools from external orchestrators
- **Academic isolation**: Cannot integrate with broader academic research tool ecosystem
- **Reproducibility limitations**: Workflow orchestration must be done manually in Python

### **3. GraphQL Interface**
```python
# Rejected approach
@strawberry.type
class Query:
    @strawberry.field
    def extract_entities(self, text: str) -> List[EntityType]:
        # GraphQL implementation
```

**Rejected because**:
- **Complexity mismatch**: GraphQL designed for complex data querying, not tool execution
- **Academic workflow mismatch**: Research workflows are procedural, not query-based
- **Implementation overhead**: Requires GraphQL server setup and schema management
- **Limited tool composition**: No built-in support for sequential tool execution

### **4. Message Queue Integration (Celery/RQ)**
```python
# Rejected approach
@celery.task
def extract_entities_task(text: str) -> str:
    # Async task execution
```

**Rejected because**:
- **Infrastructure requirements**: Requires message broker setup (Redis/RabbitMQ)
- **Complexity overhead**: Async task management adds complexity inappropriate for academic use
- **Single-node mismatch**: Message queues designed for distributed systems
- **Academic workflow mismatch**: Research workflows are typically synchronous and interactive

## MCP Integration Implementation

### **Tool Wrapper Pattern**
```python
class MCPToolWrapper:
    """Wrapper for exposing KGAS tools via MCP"""
    
    def __init__(self, tool_class: Type[BaseTool]):
        self.tool_class = tool_class
        self.service_manager = ServiceManager()
    
    def create_mcp_tool(self) -> Callable:
        """Create MCP tool function from KGAS tool"""
        def mcp_tool_function(**kwargs) -> Dict[str, Any]:
            tool = self.tool_class(service_manager=self.service_manager)
            request = ToolRequest(
                tool_id=tool.tool_id,
                operation="execute",
                input_data=kwargs
            )
            result = tool.execute(request)
            
            if result.status == "success":
                return result.data
            else:
                return {"error": result.error, "error_code": result.error_code}
        
        return mcp_tool_function
```

### **Academic Research Tool Definitions**
```python
# Document processing tools
@app.tool()
def load_pdf_document(file_path: str, extract_metadata: bool = True) -> Dict[str, Any]:
    """Load and extract text from PDF document with academic metadata."""
    
@app.tool()
def extract_entities_academic(
    text: str, 
    entity_types: List[str] = ["PERSON", "ORG", "CONCEPT", "THEORY"],
    confidence_threshold: float = 0.8
) -> Dict[str, List[Dict]]:
    """Extract academic entities with confidence scores for research analysis."""

@app.tool()
def build_knowledge_graph(
    entities: List[Dict], 
    relationships: List[Dict],
    theory_schema: Optional[str] = None
) -> Dict[str, Any]:
    """Build knowledge graph with optional theory-aware processing."""

@app.tool()
def analyze_cross_modal(
    graph_data: Dict,
    analysis_type: str = "centrality",
    output_format: str = "academic_report"
) -> Dict[str, Any]:
    """Perform cross-modal analysis (graph/table/vector) with academic reporting."""
```

### **Research Workflow Composition**
```python
# Example: AI-orchestrated academic workflow
def research_analysis_workflow(document_paths: List[str]) -> str:
    """Example workflow that AI can orchestrate using MCP tools"""
    
    # Step 1: Load documents
    documents = []
    for path in document_paths:
        doc_result = load_pdf_document(file_path=path, extract_metadata=True)
        documents.append(doc_result)
    
    # Step 2: Extract entities from all documents
    all_entities = []
    for doc in documents:
        entities = extract_entities_academic(
            text=doc["content"],
            entity_types=["PERSON", "ORG", "CONCEPT", "THEORY"],
            confidence_threshold=0.8
        )
        all_entities.extend(entities["entities"])
    
    # Step 3: Build integrated knowledge graph
    graph = build_knowledge_graph(
        entities=all_entities,
        relationships=[],  # Would be extracted in real workflow
        theory_schema="stakeholder_theory"
    )
    
    # Step 4: Perform analysis
    analysis_result = analyze_cross_modal(
        graph_data=graph,
        analysis_type="centrality",
        output_format="academic_report"
    )
    
    return analysis_result["report"]
```

## Consequences

### **Positive**
- **AI integration**: Seamless integration with Claude and other AI systems for research workflows
- **Tool composition**: Standardized way to chain KGAS tools for complex research analysis
- **External accessibility**: KGAS tools accessible from any MCP-compatible client
- **Type safety**: Built-in type validation and error handling
- **Documentation**: Automatic tool documentation and help system
- **Academic workflow support**: Designed for research-specific use cases and requirements

### **Negative**
- **Protocol dependency**: Dependent on MCP protocol evolution and maintenance
- **Limited ecosystem**: MCP ecosystem still developing, fewer existing integrations
- **Learning curve**: Researchers need to understand MCP concepts for advanced usage
- **JSON serialization**: All data must be JSON-serializable, limiting some Python object types

## Academic Research Benefits

### **AI-Assisted Research Workflows**
Researchers can use Claude to orchestrate complex analysis:
```
Researcher: "Analyze these 20 papers on stakeholder theory. Extract all entities, identify key relationships, and generate a centrality analysis showing the most influential concepts."

Claude: I'll orchestrate a multi-step analysis using KGAS tools:
1. Load all 20 PDF documents with metadata extraction
2. Extract academic entities (PERSON, ORG, CONCEPT, THEORY) 
3. Build an integrated knowledge graph
4. Perform centrality analysis
5. Generate academic report with proper citations

[Claude executes MCP tool sequence automatically]
```

### **Reproducible Research Workflows**
MCP tool calls create auditable workflow records:
```json
{
  "workflow_id": "stakeholder_analysis_2025_07_23",
  "tool_calls": [
    {"tool": "load_pdf_document", "params": {"file_path": "paper1.pdf"}},
    {"tool": "extract_entities_academic", "params": {"text": "...", "confidence_threshold": 0.8}},
    {"tool": "build_knowledge_graph", "params": {"theory_schema": "stakeholder_theory"}}
  ],
  "results": {...}
}
```

### **Tool Ecosystem Integration**
KGAS tools can integrate with other academic MCP tools:
- **Citation management tools**: Integrate extracted entities with reference management
- **Statistical analysis tools**: Export KGAS results to statistical software
- **Visualization tools**: Generate academic figures and diagrams
- **Writing tools**: Integrate analysis results with academic writing assistance

## Implementation Requirements

### **Tool Interface Standards**
- **Type annotations**: All tool parameters and returns must have complete type annotations
- **Documentation**: Comprehensive docstrings with academic research context
- **Error handling**: Standardized error responses with recovery guidance
- **Validation**: Input parameter validation with clear error messages

### **Academic Research Optimization**
- **Confidence tracking**: All tools return confidence scores and quality metrics
- **Provenance integration**: Tool calls logged for complete research audit trails
- **Citation support**: Tools provide source attribution for extracted information
- **Theory awareness**: Tools support research theory integration where appropriate

### **Performance and Reliability**
- **Streaming support**: Large results streamed for better user experience
- **Progress tracking**: Long-running tools provide progress updates
- **Resource management**: Tools manage memory and CPU usage appropriately
- **Error recovery**: Tools provide clear guidance for error recovery

## Validation Criteria

- [ ] All KGAS tools exposed via standardized MCP interface
- [ ] AI systems (Claude) can successfully orchestrate multi-step research workflows
- [ ] Tool composition works correctly for complex academic analysis
- [ ] Type safety prevents common integration errors
- [ ] Documentation enables researchers to understand and use tools effectively
- [ ] Error handling provides clear guidance for recovery
- [ ] Academic workflow requirements (confidence, provenance, citations) supported

## Related ADRs

- **ADR-011**: Academic Research Focus (MCP tools designed for research workflows)
- **ADR-008**: Core Service Architecture (MCP tools integrate with core services)
- **ADR-010**: Quality System Design (MCP tools return confidence and quality metrics)

This MCP integration enables KGAS to participate in the broader academic research tool ecosystem while providing AI-assisted workflow capabilities that enhance researcher productivity and analysis quality.