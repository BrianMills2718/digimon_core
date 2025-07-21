# MCP Integration Architecture

**Status**: Production Implementation  
**Date**: 2025-07-21  
**Purpose**: Document KGAS Model Context Protocol (MCP) integration for external tool access

---

## Overview

KGAS implements the **Model Context Protocol (MCP)** to expose **ALL system capabilities** as standardized tools for comprehensive external integration. This enables flexible orchestration through:

- **Complete Tool Access**: All 121+ KGAS tools accessible via MCP protocol
- **LLM Client Flexibility**: Works with Claude Desktop, custom Streamlit UI, and other MCP-compatible clients  
- **Natural Language Orchestration**: Complex computational social science workflows controlled through conversation
- **Model Agnostic**: Users choose their preferred LLM (Claude, GPT-4, Gemini, etc.) for orchestration
- **Custom UI Architecture**: Streamlit frontend with FastAPI backend for seamless user experience

---

## MCP Architecture Integration

### **System Architecture with MCP Layer**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            EXTERNAL INTEGRATIONS                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   Claude Desktop │    │ Custom Streamlit│    │  Other LLM      │            │
│  │      Client      │    │ UI + FastAPI    │    │    Clients      │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                     │
│           └───────────────────────┼───────────────────────┘                     │
│                                   │                                             │
└───────────────────────────────────┼─────────────────────────────────────────────┘
                                    │
                              ┌─────▼─────┐
                              │   MCP     │
                              │ Protocol  │
                              │  Layer    │
                              └─────┬─────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────────┐
│                          KGAS MCP SERVER                                       │
│                        (FastMCP Implementation)                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    COMPLETE MCP TOOL EXPOSITION                        │  │
│  │                        ALL 121+ TOOLS ACCESSIBLE                       │  │
│  │                                                                         │  │
│  │  🏗️ CORE SERVICE TOOLS                                                 │  │
│  │  📊 T107: Identity Service (create_mention, link_entity, merge_entity) │  │
│  │  📈 T110: Provenance Service (log_operation, get_lineage, track_source)│  │
│  │  🎯 T111: Quality Service (assess_quality, validate_extraction)        │  │
│  │  🔄 T121: Workflow State Service (save_state, load_state, checkpoints) │  │
│  │                                                                         │  │
│  │  📄 PHASE 1: DOCUMENT PROCESSING TOOLS                                 │  │
│  │  T01: PDF Loader • T15A: Text Chunker • T15B: Vector Embedder         │  │
│  │  T23A: SpaCy NER • T23C: Ontology-Aware Extractor                     │  │
│  │  T27: Relationship Extractor • T31: Entity Builder                     │  │
│  │  T34: Edge Builder • T41: Async Text Embedder                          │  │
│  │  T49: Multi-hop Query • T68: PageRank Optimized                        │  │
│  │                                                                         │  │
│  │  🔬 PHASE 2: ADVANCED PROCESSING TOOLS                                 │  │
│  │  T23C: Ontology-Aware Extractor • T301: Multi-Document Fusion         │  │
│  │  Enhanced Vertical Slice Workflow • Async Multi-Document Processor     │  │
│  │                                                                         │  │
│  │  🎯 PHASE 3: ANALYSIS TOOLS                                            │  │
│  │  T301: Multi-Document Fusion • Basic Multi-Document Workflow           │  │
│  │  Advanced Cross-Modal Analysis • Theory-Aware Query Processing         │  │
│  │                                                                         │  │
│  │  📊 ANALYTICS & ORCHESTRATION TOOLS                                    │  │
│  │  Cross-Modal Analysis (Graph/Table/Vector) • Theory Schema Application │  │
│  │  LLM-Driven Mode Selection • Intelligent Format Conversion             │  │
│  │  Research Question Optimization • Source Traceability                  │  │
│  │                                                                         │  │
│  │  🔧 INFRASTRUCTURE TOOLS                                                │  │
│  │  Configuration Management • Health Monitoring • Backup/Restore         │  │
│  │  Security Management • PII Protection • Error Recovery                 │  │
│  │                                                                         │  │
│  │  All tools support: Natural language orchestration, provenance         │  │
│  │  tracking, quality assessment, checkpoint/resume, theory integration   │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      CORE KGAS SERVICES                                │  │
│  │                                                                         │  │
│  │  🏛️ Service Manager - Centralized service orchestration               │  │
│  │  🔍 Identity Service - Entity resolution and deduplication            │  │
│  │  📊 Provenance Service - Complete audit trail and lineage             │  │
│  │  🎯 Quality Service - Multi-tier quality assessment                   │  │
│  │  🔄 Pipeline Orchestrator - Multi-phase workflow management           │  │
│  │  📚 Theory Repository - DOLCE-validated theory schemas                │  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## MCP Protocol Implementation

### **FastMCP Framework Integration**

KGAS uses the FastMCP framework for streamlined MCP server implementation:

```python
# Core MCP Server Structure
from fastmcp import FastMCP
from src.core.service_manager import get_service_manager

# Initialize MCP server with KGAS integration
mcp = FastMCP("super-digimon")

# Get shared service manager for core capabilities
service_manager = get_service_manager()
identity_service = service_manager.identity_service
provenance_service = service_manager.provenance_service
quality_service = service_manager.quality_service
```

### **Tool Registration Pattern**

All KGAS capabilities exposed through MCP follow a standardized registration pattern:

```python
@mcp.tool()
def create_mention(
    surface_form: str,
    start_pos: int, 
    end_pos: int,
    source_ref: str,
    entity_type: str = None,
    confidence: float = 0.8
) -> Dict[str, Any]:
    """Create a new mention and link to entity.
    
    Enables LLM clients to perform entity mention creation with
    automatic identity resolution and quality assessment.
    """
    # Leverage core KGAS services
    result = identity_service.create_mention(
        surface_form, start_pos, end_pos, source_ref, 
        entity_type, confidence
    )
    
    # Track operation for provenance
    provenance_service.log_operation(
        operation="create_mention",
        inputs=locals(),
        outputs=result
    )
    
    # Assess and track quality
    quality_result = quality_service.assess_mention_quality(result)
    
    return {
        "mention": result,
        "quality": quality_result,
        "provenance_id": provenance_service.get_last_operation_id()
    }
```

---

## Core Service Tools (T107-T121)

### **T107: Identity Service Tools**

Identity resolution and entity management capabilities:

#### **create_mention()**
- **Purpose**: Create entity mentions with automatic linking
- **Integration**: Leverages KGAS identity resolution algorithms
- **Quality**: Includes confidence scoring and validation
- **Provenance**: Full operation tracking and audit trail

#### **link_entity()**
- **Purpose**: Cross-document entity resolution and deduplication  
- **Integration**: Uses KGAS advanced matching algorithms
- **Theory Integration**: Supports theory-aware entity types
- **DOLCE Validation**: Ensures ontological consistency

#### **get_entity_info()**
- **Purpose**: Comprehensive entity information retrieval
- **Integration**: Aggregates data across all KGAS components
- **MCL Integration**: Returns Master Concept Library alignments
- **Cross-Modal**: Provides graph, table, and vector representations

### **T110: Provenance Service Tools**

Complete audit trail and lineage tracking:

#### **log_operation()**
- **Purpose**: Track all operations for reproducibility
- **Integration**: Captures inputs, outputs, execution context
- **Temporal Tracking**: Implements `applied_at` timestamps
- **Research Integrity**: Enables exact analysis reproduction

#### **get_lineage()**
- **Purpose**: Full data lineage from source to analysis
- **Integration**: Traces through all KGAS processing phases
- **Theory Tracking**: Shows which theories influenced results
- **Source Attribution**: Complete document-to-result traceability

### **T111: Quality Service Tools**

Multi-tier quality assessment and validation:

#### **assess_quality()**
- **Purpose**: Comprehensive quality evaluation
- **Integration**: Uses KGAS quality framework (Gold/Silver/Bronze/Copper)
- **Theory Validation**: Ensures theoretical consistency
- **DOLCE Compliance**: Validates ontological correctness

#### **validate_extraction()**
- **Purpose**: Entity extraction quality validation
- **Integration**: Cross-references against MCL and theory schemas
- **Automated Assessment**: LLM-driven quality evaluation
- **Confidence Calibration**: Accuracy vs. confidence analysis

### **T121: Workflow State Service Tools**

Checkpoint and resume capabilities for complex analyses:

#### **save_state()**
- **Purpose**: Persist complete workflow state
- **Integration**: Captures full KGAS processing context
- **Resumability**: Enable interruption and resumption
- **Research Continuity**: Support long-running analyses

#### **load_state()**
- **Purpose**: Resume workflows from saved checkpoints
- **Integration**: Restores complete processing context
- **Temporal Consistency**: Maintains time-consistent theory versions
- **Quality Preservation**: Ensures consistent quality assessment

---

## Phase-Specific Tool Integration

### **Phase 1: Document Ingestion Tools**

Document processing capabilities exposed through MCP:

```python
@mcp.tool()
def process_pdf(
    file_path: str,
    extraction_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Process PDF document with full KGAS pipeline integration."""
    
    # Use KGAS PDF processing capabilities
    result = orchestrator.process_document(
        file_path=file_path,
        document_type="pdf",
        options=extraction_options or {}
    )
    
    # Automatic quality assessment
    quality_result = quality_service.assess_document_quality(result)
    
    # Complete provenance tracking
    provenance_service.log_document_processing(file_path, result)
    
    return {
        "extraction_result": result,
        "quality_assessment": quality_result,
        "entities_extracted": len(result.get("entities", [])),
        "provenance_id": provenance_service.get_last_operation_id()
    }
```

### **Theory Integration Through MCP**

Theory schemas accessible through MCP interface:

```python
@mcp.tool()
def apply_theory_schema(
    theory_id: str,
    document_content: str,
    analysis_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Apply theory schema to document analysis."""
    
    # Retrieve theory schema from repository
    theory_schema = theory_repository.get_theory(theory_id)
    
    # Apply automated theory extraction if needed
    if not theory_schema:
        theory_schema = automated_extraction.extract_theory_from_paper(theory_id)
    
    # Execute theory-aware analysis
    analysis_result = orchestrator.analyze_with_theory(
        content=document_content,
        theory_schema=theory_schema,
        options=analysis_options or {}
    )
    
    # Track theory usage for temporal analytics
    temporal_tracker.record_theory_application(theory_id, datetime.now())
    
    return {
        "theory_applied": theory_id,
        "analysis_result": analysis_result,
        "mcl_concepts_used": theory_schema.get("mcl_concepts", []),
        "dolce_validation": theory_schema.get("dolce_compliance", True)
    }
```

---

## Client Integration Patterns

### **Natural Language Orchestration via Custom UI**

The **custom Streamlit UI with FastAPI backend** enables natural language orchestration of all KGAS tools:

#### **Streamlit UI Architecture**
```python
# Custom Streamlit interface for KGAS
import streamlit as st
from fastapi_client import KGASAPIClient

# User-selectable LLM model (not fixed to one provider)
llm_model = st.selectbox("Select LLM", ["claude-3-5-sonnet", "gpt-4", "gemini-pro"])
api_client = KGASAPIClient(model=llm_model)

# Natural language workflow orchestration
user_query = st.text_area("Research Analysis Request")
if st.button("Execute Analysis"):
    # FastAPI backend orchestrates MCP tools based on user request
    result = api_client.orchestrate_analysis(user_query, llm_model)
```

#### **FastAPI Backend Integration**
```python
# FastAPI backend connects to KGAS MCP server
from fastapi import FastAPI
from mcp_client import MCPClient

app = FastAPI()
mcp_client = MCPClient("super-digimon")

@app.post("/orchestrate-analysis")
async def orchestrate_analysis(request: AnalysisRequest):
    """Orchestrate KGAS tools based on natural language request."""
    
    # LLM interprets user request and selects appropriate tools
    workflow_plan = await request.llm.plan_workflow(
        user_request=request.query,
        available_tools=mcp_client.list_tools()
    )
    
    # Execute planned workflow using MCP tools
    results = []
    for step in workflow_plan.steps:
        tool_result = await mcp_client.call_tool(
            tool_name=step.tool,
            parameters=step.parameters
        )
        results.append(tool_result)
    
    return {"workflow": workflow_plan, "results": results}
```

#### **Example: Complex Multi-Tool Orchestration**
```
User: "Analyze this policy document using Social Identity Theory, 
       ensure high quality extraction, and track full provenance."

Custom UI → FastAPI Backend → MCP Tool Orchestration:

1. T01: process_pdf() - Load and extract document content
2. T23C: ontology_aware_extraction() - Apply Social Identity Theory schema
3. T111: assess_quality() - Multi-tier quality validation  
4. T110: get_lineage() - Complete provenance trail
5. Cross-modal analysis() - Generate insights across formats
6. export_results() - Academic publication format

All orchestrated through natural language with model flexibility.
```

### **Cross-Modal Analysis via MCP**

```python
@mcp.tool() 
def cross_modal_analysis(
    entity_ids: List[str],
    analysis_modes: List[str] = ["graph", "table", "vector"],
    research_question: str = None
) -> Dict[str, Any]:
    """Perform cross-modal analysis across specified modes."""
    
    results = {}
    
    for mode in analysis_modes:
        if mode == "graph":
            results["graph"] = analytics_service.graph_analysis(entity_ids)
        elif mode == "table":
            results["table"] = analytics_service.table_analysis(entity_ids)
        elif mode == "vector":
            results["vector"] = analytics_service.vector_analysis(entity_ids)
    
    # Intelligent mode selection if research question provided
    if research_question:
        optimal_mode = mode_selector.select_optimal_mode(
            research_question, entity_ids, results
        )
        results["recommended_mode"] = optimal_mode
        results["rationale"] = mode_selector.get_selection_rationale()
    
    return results
```

---

## Security and Access Control

### **MCP Security Framework**

```python
class MCPSecurityMiddleware:
    """Security middleware for MCP tool access."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.access_control = AccessControlService()
        
    def validate_request(self, tool_name: str, params: Dict) -> bool:
        """Validate MCP tool request for security compliance."""
        
        # PII detection and scrubbing
        if self.contains_pii(params):
            params = self.scrub_pii(params)
            
        # Access control validation
        if not self.access_control.can_access_tool(tool_name):
            raise AccessDeniedError(f"Access denied for tool: {tool_name}")
            
        # Rate limiting
        if not self.rate_limiter.allow_request():
            raise RateLimitExceededError("Request rate limit exceeded")
            
        return True
```

### **Audit and Compliance**

All MCP interactions are logged for research integrity:

```python
class MCPAuditLogger:
    """Comprehensive audit logging for MCP interactions."""
    
    def log_mcp_request(self, tool_name: str, params: Dict, result: Dict):
        """Log MCP tool usage for audit trail."""
        
        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "parameters": self.sanitize_params(params),
            "result_summary": self.summarize_result(result),
            "client_id": self.get_client_identifier(),
            "session_id": self.get_session_id(),
            "provenance_chain": self.get_provenance_chain(result)
        }
        
        self.audit_service.log_record(audit_record)
```

---

## Integration Benefits

### **1. Comprehensive Tool Access**
- **Complete System Access**: All 121+ KGAS tools accessible via standardized MCP interface
- **Flexible Orchestration**: Controlling agents can combine any tools for complex analyses
- **Natural Language Control**: Complex workflows orchestrated through conversational interfaces
- **Model Agnostic**: Works with any LLM model the user prefers

### **2. Custom User Interface Architecture**
- **Streamlit Frontend**: Modern, interactive web interface for research workflows
- **FastAPI Backend**: High-performance API layer connecting UI to MCP server
- **User Choice**: Researchers select their preferred LLM model for analysis
- **Seamless Integration**: Direct connection between UI interactions and tool execution

### **3. Research Workflow Enhancement**
- **Complete Tool Ecosystem**: Document processing, extraction, analysis, and export tools
- **Reproducible Analysis**: Complete provenance and state management across all operations
- **Theory-Aware Processing**: Automated application of social science theories via MCP tools
- **Cross-Modal Intelligence**: Intelligent mode selection and format conversion

### **4. Academic Research Support**
- **Full Audit Trail**: Complete research integrity and reproducibility for all tool operations
- **Quality Assurance**: Multi-tier assessment integrated into every workflow step
- **Source Traceability**: Document-to-result attribution for academic citations
- **Export Integration**: Direct output to academic formats (LaTeX, BibTeX)

### **5. Extensibility and Interoperability**
- **Standard Protocol**: MCP ensures compatibility across all LLM clients and interfaces
- **Modular Architecture**: Easy addition of new tools to the MCP-accessible ecosystem
- **Open Integration**: External tools can leverage complete KGAS capabilities
- **Client Flexibility**: Works with desktop clients, web UIs, and custom applications

---

## Current Implementation Status

### **Production Ready** ✅
- **Core Service Tools** (T107, T110, T111, T121): Fully implemented and tested
- **Phase 1 Integration**: Document processing tools fully functional
- **FastMCP Framework**: Stable production deployment
- **Security Framework**: Basic authentication and audit logging

### **In Development** 🚧
- **Advanced Theory Tools**: Automated theory extraction via MCP
- **Cross-Modal Tools**: Unified interface for multi-modal analysis
- **Batch Processing**: Large-scale document processing capabilities
- **Advanced Security**: Enhanced access control and PII protection

### **Planned Enhancements** 🔮
- **Real-time Collaboration**: Multi-user research environments
- **Advanced Analytics**: Statistical analysis and visualization tools
- **Integration APIs**: Direct integration with research platforms
- **Community Tools**: Shared theory repository and validation

---

## Complete Tool Orchestration Architecture

### **All System Tools Available via MCP**

The key architectural principle is that **every KGAS capability is accessible through the MCP protocol**, enabling unprecedented flexibility in research workflow orchestration:

#### **Full Tool Ecosystem Access**
```python
# Example: All major tool categories accessible via MCP
available_tools = {
    "document_processing": ["T01_pdf_loader", "T15A_text_chunker", "T15B_vector_embedder"],
    "entity_extraction": ["T23A_spacy_ner", "T23C_ontology_aware_extractor"],
    "relationship_extraction": ["T27_relationship_extractor", "T31_entity_builder", "T34_edge_builder"],
    "analysis": ["T49_multihop_query", "T68_pagerank", "cross_modal_analysis"],
    "theory_application": ["apply_theory_schema", "theory_validation", "mcl_integration"],
    "quality_assurance": ["T111_quality_assessment", "confidence_propagation", "tier_filtering"],
    "provenance": ["T110_operation_tracking", "lineage_analysis", "audit_trail"],
    "workflow": ["T121_state_management", "checkpoint_creation", "workflow_resume"],
    "infrastructure": ["config_management", "health_monitoring", "security_management"]
}

# Controlling agent can use ANY combination of these tools
orchestration_plan = llm.plan_workflow(
    user_request="Complex multi-theory analysis with quality validation",
    available_tools=available_tools,
    optimization_goal="research_integrity"
)
```

#### **Natural Language → Tool Selection**
```python
# User request automatically mapped to appropriate tool sequence
user_request = """
Analyze these policy documents using both Social Identity Theory and 
Cognitive Dissonance Theory, compare the results, ensure high quality 
extraction, and export in academic format with full provenance.
"""

# LLM orchestrates complex multi-tool workflow:
workflow = [
    "T01_pdf_loader(documents)",
    "T23C_ontology_aware_extractor(theory='social_identity_theory')",
    "T23C_ontology_aware_extractor(theory='cognitive_dissonance_theory')", 
    "cross_modal_analysis(compare_theories=True)",
    "T111_quality_assessment(tier='publication_ready')",
    "T110_complete_provenance_chain()",
    "export_academic_format(format=['latex', 'bibtex'])"
]
```

### **Flexible UI Architecture**

#### **Custom Streamlit + FastAPI Pattern**
The architecture enables users to choose their preferred interaction method:

```python
# Streamlit UI provides multiple interaction patterns
def main():
    st.title("KGAS Computational Social Science Platform")
    
    # User selects their preferred LLM
    llm_choice = st.selectbox("Select Analysis Model", 
        ["claude-3-5-sonnet", "gpt-4-turbo", "gemini-2.0-flash"])
    
    # Multiple interaction modes
    interaction_mode = st.radio("Interaction Mode", [
        "Natural Language Workflow",
        "Tool-by-Tool Construction", 
        "Template-Based Analysis",
        "Expert Mode (Direct MCP)"
    ])
    
    if interaction_mode == "Natural Language Workflow":
        # User describes what they want in natural language
        research_goal = st.text_area("Describe your research analysis:")
        if st.button("Execute Analysis"):
            orchestrate_via_natural_language(research_goal, llm_choice)
    
    elif interaction_mode == "Expert Mode (Direct MCP)":
        # Advanced users can directly select and configure tools
        selected_tools = st.multiselect("Select Tools", list_all_mcp_tools())
        tool_sequence = st_ace(language="python", key="tool_config")
```

#### **Model-Agnostic Backend**
```python
# FastAPI backend adapts to any LLM choice
class AnalysisOrchestrator:
    def __init__(self, llm_model: str):
        self.mcp_client = MCPClient("super-digimon")
        self.llm = self._initialize_llm(llm_model)
    
    def _initialize_llm(self, model: str):
        """Initialize any supported LLM model."""
        if model.startswith("claude"):
            return AnthropicClient(model)
        elif model.startswith("gpt"):
            return OpenAIClient(model)
        elif model.startswith("gemini"):
            return GoogleClient(model)
        # Add support for any LLM with tool use capabilities
    
    async def orchestrate_workflow(self, user_request: str):
        """Model-agnostic workflow orchestration."""
        # Get all available MCP tools
        available_tools = await self.mcp_client.list_tools()
        
        # Let chosen LLM plan the workflow
        workflow_plan = await self.llm.plan_and_execute(
            request=user_request,
            tools=available_tools
        )
        
        return workflow_plan
```

### **Research Integrity Through Complete Access**

The comprehensive MCP tool access ensures research integrity:

#### **Complete Provenance Chains**
```python
# Every tool operation tracked regardless of orchestration method
@mcp_tool_wrapper
def any_kgas_tool(tool_params):
    """All tools automatically include provenance tracking."""
    operation_id = provenance_service.start_operation(
        tool_name=tool_params.name,
        parameters=tool_params.parameters,
        orchestration_context="mcp_client"
    )
    
    try:
        result = execute_tool(tool_params)
        provenance_service.complete_operation(operation_id, result)
        return result
    except Exception as e:
        provenance_service.log_error(operation_id, e)
        raise
```

#### **Quality Assurance Integration**
```python
# Quality assessment available for any workflow
def ensure_research_quality(workflow_results):
    """Apply quality assurance to any analysis results."""
    quality_assessments = []
    
    for step_result in workflow_results:
        quality_score = mcp_client.call_tool("assess_confidence", {
            "object_ref": step_result.id,
            "base_confidence": step_result.confidence,
            "factors": step_result.quality_factors
        })
        quality_assessments.append(quality_score)
    
    overall_quality = mcp_client.call_tool("calculate_workflow_quality", {
        "step_assessments": quality_assessments,
        "quality_requirements": "publication_standard"
    })
    
    return overall_quality
```

The MCP integration architecture transforms KGAS from a standalone system to a **comprehensively accessible computational social science platform** where controlling agents (whether through custom UI, desktop clients, or direct API access) can flexibly orchestrate any combination of the 121+ available tools through natural language interfaces while maintaining complete research integrity and reproducibility.