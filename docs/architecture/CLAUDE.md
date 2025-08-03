# Architecture Documentation - CLAUDE.md

## Overview
The `docs/architecture/` directory contains the authoritative architectural documentation for KGAS. This documentation defines the target system design, component relationships, data flows, and architectural decisions that guide implementation.

## Documentation Structure

### Core Architecture Documents
- **`ARCHITECTURE_OVERVIEW.md`**: Single source of truth for system architecture
- **`LIMITATIONS.md`**: Documented system limitations and constraints
- **`cross-modal-analysis.md`**: Cross-modal analysis architecture details
- **`agent-interface.md`**: Three-layer agent interface specification
- **`project-structure.md`**: Project organization and structure

### Specialized Architecture Areas
- **`adrs/`**: Architecture Decision Records (ADRs) documenting key decisions
- **`concepts/`**: Core architectural concepts and design patterns
- **`data/`**: Data architecture, schemas, and storage design
- **`specifications/`**: Formal specifications and capability registries
- **`systems/`**: Detailed design of major system components

## Key Architectural Principles

### 1. Academic Research Focus
- **Single-node design**: Optimized for local research environments
- **Flexibility over performance**: Prioritizes correctness and flexibility
- **Theory-aware processing**: Supports domain-specific ontologies and analysis
- **Reproducibility**: Full provenance tracking and audit trails

### 2. Cross-Modal Analysis Architecture
The system enables fluid movement between three data representations:
- **Graph Analysis**: Relationships, centrality, communities, paths
- **Table Analysis**: Statistical analysis, aggregations, correlations
- **Vector Analysis**: Similarity search, clustering, embeddings
- **Cross-Modal Integration**: Seamless conversion with source traceability

### 3. Bi-Store Data Architecture
```
┌─────────────────────────────────────┐
│           Application Layer          │
└────────────────┬────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌──────────────────┐    ┌──────────┐
│  Neo4j (v5.13+)  │    │  SQLite  │
│(Graph & Vectors) │    │(Metadata)│
└──────────────────┘    └──────────┘
```

### 4. Service-Oriented Architecture with Structured Output
```
┌─────────────────────────────────────────────────────────────┐
│                   Core Services Layer                       │
│  ┌────────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │PipelineOrchestrator│ │IdentityService │ │PiiService    │ │
│  ├────────────────────┤ ├────────────────┤ ├──────────────┤ │
│  │AnalyticsService    │ │TheoryRepository│ │QualityService│ │
│  └────────────────────┘ └────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
├─── Structured LLM Infrastructure ──────────────────────────┐
│  ┌────────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │StructuredLLMService│ │Pydantic Schemas│ │Monitoring    │ │
│  ├────────────────────┤ ├────────────────┤ ├──────────────┤ │
│  │LiteLLM Integration │ │Validation Engine│ │Health Alerts │ │
│  └────────────────────┘ └────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Documentation Standards

### Document Types

#### **Target Architecture** (What we're building toward)
- **Purpose**: Define the end-state system design
- **Stability**: Should change rarely, only for major architectural shifts
- **Content**: Component designs, interfaces, data flows, decisions
- **Examples**: `KGAS_ARCHITECTURE_V3.md`, ADRs, system specifications

#### **Current Implementation** (What exists now)
- **Purpose**: Document what is actually implemented and working
- **Stability**: Updated as implementation progresses
- **Content**: Working components, known issues, implementation status
- **Location**: Should reference [docs/roadmap/ROADMAP_OVERVIEW.md](../roadmap/ROADMAP_OVERVIEW.md) for current status

#### **Implementation Guidance** (How to build it)
- **Purpose**: Guide developers in implementing the target architecture
- **Content**: Design patterns, integration guides, best practices
- **Examples**: Concept documents, implementation requirements

### Writing Architecture Documentation

#### **Target Architecture Documents**
```markdown
# Component Name Architecture

## Purpose
Clear statement of what this component does and why it exists.

## Interface Design
### Inputs
- Clearly defined input formats and sources
### Outputs  
- Expected output formats and destinations
### Dependencies
- Required services and components

## Implementation Requirements
- Non-functional requirements (performance, reliability, etc.)
- Integration points with other components
- Quality and reliability standards

## Design Decisions
- Key architectural decisions and rationale
- Trade-offs considered
- Alternative approaches rejected and why
```

#### **Status and Progress Tracking**
- **Do NOT include** in architecture documents
- **Reference [docs/roadmap/ROADMAP_OVERVIEW.md](../roadmap/ROADMAP_OVERVIEW.md)** for current implementation status
- **Focus on design** rather than progress toward design

## Key Architectural Concepts

### Cross-Modal Analysis Flow
```
Research Question
        ↓
Document Processing (PDF/Word → Text → Entities)
        ↓
Graph Construction (Entities → Knowledge Graph)
        ↓
Analysis Selection (Graph/Table/Vector based on question)
        ↓
Cross-Modal Processing (Convert between formats as needed)
        ↓
Source-Linked Results (All results traceable to documents)
```

### Theory-Aware Processing
```
Domain Conversation → LLM Ontology Generation → Theory-Aware Extraction
        ↓                       ↓                        ↓
    User Intent          Domain Ontology         Quality Entities
        ↓                       ↓                        ↓
Theory Repository ← Ontology Validation → Enhanced Graph Quality
```

### Service Integration Pattern with Structured Output
```python
# All components follow this integration pattern
class Component:
    def __init__(self, service_manager: ServiceManager):
        self.identity = service_manager.identity_service
        self.provenance = service_manager.provenance_service
        self.quality = service_manager.quality_service
        # Component can access all core services
        
        # Structured LLM operations follow this pattern
        self.structured_llm = service_manager.structured_llm_service
        
    def process_with_llm(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        """All LLM operations use structured output with schema validation"""
        return self.structured_llm.structured_completion(
            prompt=prompt,
            schema=schema,
            temperature=0.05  # Optimized for reliability
        )
```

## Architecture Decision Records (ADRs)

### ADR Format
```markdown
# ADR-XXX: Decision Title

**Status**: Accepted/Rejected/Deprecated
**Date**: YYYY-MM-DD
**Context**: What situation led to this decision?
**Decision**: What did we decide?
**Rationale**: Why did we decide this?
**Consequences**: What are the results of this decision?
**Alternatives**: What other options were considered?
```

### Current ADRs
- **ADR-001**: Phase Interface Design
- **ADR-003**: Vector Store Consolidation (Bi-store architecture)
- **ADR-017**: Structured Output Migration (Pydantic schema-first LLM integration)
- **Future ADRs**: Cross-modal orchestration, theory integration, performance optimization

## System Component Architecture

### Core Services

#### **PipelineOrchestrator**
- **Purpose**: Coordinates document processing workflows
- **Responsibilities**: Phase management, state tracking, error recovery
- **Integration**: Works with all core services for complete processing

#### **AnalyticsService**  
- **Purpose**: Orchestrates cross-modal analysis operations
- **Responsibilities**: Format selection, conversion coordination, result integration
- **Innovation**: Enables fluid movement between graph/table/vector representations

#### **IdentityService**
- **Purpose**: Entity resolution and identity management
- **Responsibilities**: Entity deduplication, cross-document linking, mention tracking
- **Integration**: Central to maintaining consistent entity representation

#### **TheoryRepository**
- **Purpose**: Manages theory schemas and ontologies
- **Responsibilities**: Theory validation, ontology provisioning, analytics configuration
- **Innovation**: Enables theory-aware extraction and analysis

#### **StructuredLLMService**
- **Purpose**: Provides schema-validated LLM operations across all system components
- **Responsibilities**: LiteLLM integration, Pydantic validation, performance monitoring
- **Innovation**: Eliminates manual JSON parsing with fail-fast validation
- **Monitoring**: Real-time performance tracking, health validation, error categorization

### Data Architecture

#### **Neo4j Store**
```cypher
// Unified graph and vector storage
(:Entity {
    id: string,
    canonical_name: string,
    entity_type: string,
    confidence: float,
    quality_tier: string,
    embedding: vector[384]  // Native vector support
})

// Vector index for similarity search
CREATE VECTOR INDEX entity_embedding_index 
FOR (e:Entity) ON (e.embedding)
```

#### **SQLite Store**
```sql
-- Operational metadata
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP
);

-- Complete provenance tracking
CREATE TABLE provenance (
    object_id TEXT,
    tool_id TEXT,
    operation TEXT,
    inputs JSON,
    outputs JSON,
    execution_time REAL,
    created_at TIMESTAMP
);

-- Basic data storage
CREATE TABLE research_data (
    data_id TEXT PRIMARY KEY,
    content_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Architecture

### Scalability Constraints
- **Single-node design**: Optimized for local research environments
- **Academic focus**: Flexibility and correctness over enterprise performance
- **Resource management**: Intelligent resource usage within node constraints

### Performance Patterns
- **Async processing**: Core operations support asynchronous execution
- **Caching strategies**: Intelligent caching of expensive operations
- **Resource monitoring**: Track memory, CPU, and storage usage
- **Graceful degradation**: Fallback strategies for resource constraints

## Data Integrity Architecture

### Research Environment Data Protection
- **Data Integrity**: Transaction-based operations ensure consistency
- **Audit Trail**: Complete provenance tracking for research reproducibility
- **Local Processing**: All data processing occurs locally
- **Input Validation**: Parameterized queries and input validation

## Integration Architecture

### External Integration Points
- **LLM APIs**: OpenAI, Anthropic, Google for ontology generation and extraction
- **File Formats**: PDF, Word, Markdown, CSV, JSON support
- **Export Formats**: LaTeX, BibTeX, CSV for academic publication
- **Visualization**: Interactive graph and data visualization

### MCP Protocol Integration
- **Tool Exposure**: All tools available via MCP protocol
- **Protocol Compliance**: Standard MCP tool interface implementation
- **Service Discovery**: Dynamic tool discovery and registration

## Common Architecture Patterns

### Structured Output Architecture Pattern
```python
# Schema-first LLM integration pattern (preferred)
from pydantic import BaseModel, Field
from typing import List

class EntityExtractionResponse(BaseModel):
    """Pydantic schema for entity extraction results"""
    entities: List[dict] = Field(description="Extracted entities with metadata")
    confidence: float = Field(description="Overall extraction confidence", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of extraction approach")

# Usage across all components
def extract_entities(text: str) -> EntityExtractionResponse:
    """All LLM operations use structured output with validation"""
    return structured_llm.structured_completion(
        prompt=f"Extract entities from: {text}",
        schema=EntityExtractionResponse,
        temperature=0.05  # Optimized for JSON reliability
    )
```

### Error Handling Architecture
```python
# Fail-fast with recovery guidance and monitoring integration
from src.monitoring import track_structured_output

def process_with_monitoring(component: str, schema_name: str):
    with track_structured_output(component, schema_name) as tracker:
        try:
            result = process_data()
            tracker.set_success(True, result)
            return {"status": "success", "data": result}
        except ValidationError as e:
            tracker.set_validation_error(str(e))
            logger.error(f"Schema validation failed: {e}")
            return {
                "status": "validation_error", 
                "error": str(e),
                "recovery": "check_schema_compatibility"
            }
        except Exception as e:
            tracker.set_llm_error(str(e))
            logger.error(f"Processing failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "recovery": "specific_guidance"
            }
```

### Provenance Architecture
```python
# All operations tracked for reproducibility
def tracked_operation(operation_name, inputs, processor):
    start_time = time.time()
    try:
        result = processor(inputs)
        provenance.log_execution(
            operation=operation_name,
            inputs=inputs,
            outputs=result,
            execution_time=time.time() - start_time,
            status="success"
        )
        return result
    except Exception as e:
        provenance.log_execution(
            operation=operation_name,
            inputs=inputs,
            error=str(e),
            execution_time=time.time() - start_time,
            status="error"
        )
        raise
```

## Future Architecture Evolution

### Planned Enhancements
- **Advanced Cross-Modal Orchestration**: Intelligent format selection
- **Theory Ecosystem**: Rich theory integration and validation
- **Performance Optimization**: Advanced caching and resource management
- **Export Enhancement**: Enhanced academic publication support

### Architecture Stability
- **Core Services**: Stable interface, implementation improvements
- **Data Architecture**: Stable bi-store design, schema evolution
- **Cross-Modal**: Stable concept, enhanced orchestration capabilities
- **Theory Integration**: Stable meta-schema, expanded theory library

## Documentation Maintenance

### Review Process
1. **Architecture changes** require ADR documentation
2. **Major decisions** should be captured in concepts/
3. **Component changes** update relevant system documentation
4. **Regular reviews** ensure documentation accuracy

### Quality Standards
- **Clarity**: Architecture should be understandable by new team members
- **Completeness**: All major components and decisions documented
- **Accuracy**: Documentation reflects actual architectural decisions
- **Traceability**: Clear links between decisions and implementations

The architecture documentation serves as the authoritative source for understanding KGAS design decisions and guiding implementation efforts toward the cross-modal analysis vision.