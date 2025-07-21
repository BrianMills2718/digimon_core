# KGAS Architecture Overview

*Status: Target Architecture Documentation*

**This document defines the target system architecture for KGAS (Knowledge Graph Analysis System). It describes the intended design and component relationships that guide implementation. For current implementation status, see the [Roadmap Overview](./ROADMAP_OVERVIEW.md).**

---

## 1. Core Architectural Principles

### Academic Research Focus
- **Single-node design**: Optimized for local research environments, not distributed systems
- **Flexibility over performance**: Prioritizes correctness and analytical flexibility
- **Theory-aware processing**: Supports domain-specific ontologies and analysis
- **Reproducibility**: Complete provenance tracking and audit trails

### Cross-Modal Analysis Architecture
- **Multi-modal data representation**: Graph, Table, and Vector analysis modes
- **Seamless format conversion**: Intelligent transformation between analysis modes
- **Source traceability**: All results linked back to original documents
- **Format-agnostic queries**: Research questions drive optimal format selection

### Fail-Fast Design Philosophy
- **Immediate error exposure**: Problems surface immediately rather than being masked
- **Input validation**: Rigorous validation at system boundaries
- **Complete failure**: System fails entirely on critical errors rather than degrading
- **Evidence-based operation**: All functionality backed by validation evidence

---

## 2. System Architecture Overview

KGAS is a theory-aware, cross-modal analysis system that extracts structured knowledge graphs from unstructured text and enables fluid analysis across Graph, Table, and Vector representations.

### Core Architecture Components

#### Multi-Layer Agent Interface
```
┌─────────────────────────────────────────────────────────────┐
│                Agent Interface Layers                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Layer 1:      │ │   Layer 2:      │ │   Layer 3:      │ │
│  │Agent-Controlled │ │Agent-Assisted   │ │Manual Control   │ │
│  │                 │ │                 │ │                 │ │
│  │NL→YAML→Execute  │ │YAML Review      │ │Direct YAML      │ │
│  │Complete Auto    │ │User Approval    │ │Expert Control   │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 Core Services Layer                         │
│  ┌────────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │PipelineOrchestrator│ │IdentityService │ │PiiService    │ │
│  ├────────────────────┤ ├────────────────┤ ├──────────────┤ │
│  │AnalyticsService    │ │TheoryRepository│ │QualityService│ │
│  ├────────────────────┤ ├────────────────┤ ├──────────────┤ │
│  │ProvenanceService   │ │WorkflowEngine  │ │SecurityMgr   │ │
│  └────────────────────┘ └────────────────┘ └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
┌──────────────────────┐    ┌──────────┐
│  Neo4j (v5.13+)      │    │  SQLite  │
│(Graph & Vectors)     │    │(Metadata)│
└──────────────────────┘    └──────────┘
```

#### Cross-Modal Analysis Flow
```
Research Question → Document Processing → Knowledge Graph → Analysis Mode Selection
        │                    │                   │              │
        │                    │                   │              ├─ Graph Analysis
        │                    │                   │              ├─ Table Analysis  
        │                    │                   │              └─ Vector Analysis
        │                    │                   │
        └─────────── Source Traceability ──────────────────────────────────────────┘
```

---

## 3. Data Storage Layer (The "Where")

The system uses a **bi-store architecture** as decided in [ADR-003](./adrs/ADR-003-Vector-Store-Consolidation.md).

-   **Neo4j (v5.13+):** Unified store for the property graph and vector embeddings.
-   **SQLite:** Store for operational data (workflow state, provenance, PII vault).

### Schemas
*   [View Neo4j & SQLite Schemas](./data/schemas.md)

---

## 4. Core Services & Pipeline (The "How")

The system is orchestrated by a central `PipelineOrchestrator` service.

### Core Services
-   **PipelineOrchestrator**: Manages the document processing pipeline.
-   **IdentityService**: Handles entity resolution.
-   **PiiService**: Provides research-focused pseudonymization.
-   **QualityService**: Manages confidence scoring and data quality.
-   **AnalyticsService**: Orchestrates cross-modal analysis.
-   **TheoryRepository**: Manages theory schemas and ontologies.

### Core Data Flow & PII
-   See [Detailed Data Flow](./data/data-flow.md) for specifics on the PII pipeline and transactional integrity.

---

## 5. Cross-Modal Analysis Architecture
KGAS enables fluid movement between Graph, Relational, and Vector representations.
-   [View Cross-Modal Analysis Details](./cross-modal-analysis.md)

---

## 6. MCP Integration Architecture

KGAS exposes all system capabilities through the Model Context Protocol (MCP) for comprehensive external tool access:

-   **Complete Tool Access**: All 121+ KGAS tools accessible via standardized MCP interface
-   **Multiple Client Support**: Works with Claude Desktop, custom Streamlit UI, and other MCP clients  
-   **Security Framework**: Comprehensive security measures addressing MCP protocol vulnerabilities
-   **Performance Optimization**: Mitigation strategies for MCP limitations (40-tool barrier, context scaling)

-   [View MCP Architecture Details](./docs/architecture/systems/mcp-integration-architecture.md)
-   [View MCP Limitations & Solutions](./docs/architecture/mcp/limitations.md)
-   [View Complete MCP Documentation](./docs/architecture/mcp/README.md)

---

## 7. Known Limitations
This system is **NOT** production-ready. 
-   [View Full System Limitations](./LIMITATIONS.md) 