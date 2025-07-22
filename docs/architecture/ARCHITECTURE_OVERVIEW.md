# KGAS Architecture Overview

**Status**: Target Architecture  
**Purpose**: Single source of truth for KGAS final architecture  
**Stability**: Changes only when architectural goals change

## System Vision

KGAS (Knowledge Graph Analysis System) is a theory-aware, cross-modal analysis platform for academic social science research. It enables researchers to fluidly analyze documents through graph, table, and vector representations while maintaining theoretical grounding and complete source traceability.

## Core Architectural Principles

### 1. Cross-Modal Analysis
- **Synchronized multi-modal views** (graph, table, vector) not lossy conversions
- **Optimal representation selection** based on research questions
- **Full analytical capabilities** preserved in each mode

### 2. Theory-Aware Processing  
- **Automated theory extraction** from academic literature
- **Theory-guided analysis** using domain ontologies
- **Flexible theory integration** supporting multiple frameworks

### 3. Uncertainty Quantification
- **CERQual-based assessment** for all analytical outputs
- **Configurable complexity** from simple confidence to advanced Bayesian
- **Uncertainty propagation** through analytical pipelines

### 4. Academic Research Focus
- **Single-node design** for local research environments  
- **Reproducibility first** with complete provenance tracking
- **Flexibility over performance** for exploratory research

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│         (Natural Language → Agent → Workflow → Results)      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Cross-Modal Analysis Layer                   │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐   │
│  │Graph Analysis│ │Table Analysis│ │Vector Analysis    │   │
│  └─────────────┘ └──────────────┘ └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Core Services Layer                        │
│  ┌────────────────────┐ ┌────────────────┐ ┌─────────────┐ │
│  │PipelineOrchestrator│ │IdentityService │ │PiiService   │ │
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │AnalyticsService    │ │TheoryRepository│ │QualityService│ │
│  └────────────────────┘ └────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                        │
│         ┌──────────────────┐    ┌──────────────┐           │
│         │  Neo4j (v5.13+)  │    │    SQLite    │           │
│         │(Graph & Vectors) │    │  (Relational) │           │
│         └──────────────────┘    └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### User Interface Layer
- **[Agent Interface](agent-interface.md)**: Three-layer interface (automated, assisted, manual)
- **[MCP Integration](systems/mcp-integration-architecture.md)**: LLM tool orchestration protocol
- **Workflow Engine**: YAML-based reproducible workflows

### Cross-Modal Analysis Layer
- **[Cross-Modal Analysis](cross-modal-analysis.md)**: Fluid movement between representations
- **[Mode Selection](concepts/cross-modal-philosophy.md)**: LLM-driven optimal mode selection
- **[Provenance Tracking](specifications/PROVENANCE.md)**: Complete source traceability

### Core Services Layer
- **[Pipeline Orchestrator](adrs/ADR-002-Pipeline-Orchestrator-Architecture.md)**: Workflow coordination
- **[Service Architecture](systems/)**:  Modular service design
- **[Tool Contracts](adrs/ADR-001-Phase-Interface-Design.md)**: Standardized interfaces

### Data Storage Layer
- **[Bi-Store Architecture](data/bi-store-justification.md)**: Neo4j + SQLite design
- **[Data Models](data/schemas.md)**: Entity, relationship, and metadata schemas
- **[Vector Storage](adrs/ADR-003-Vector-Store-Consolidation.md)**: Native Neo4j vectors

## Theory Integration Architecture

### Ontological Framework Integration
- **DOLCE**: Upper-level ontology for general categorization
- **FOAF/SIOC**: Social network and online community concepts
- **Custom Typology**: Three-dimensional theory classification
- **[Integration Model](concepts/theoretical-framework.md)**: Hierarchical integration approach

### Theory-Aware Processing
- **[Theory Repository](systems/theory-repository-abstraction.md)**: Schema management
- **[Extraction Integration](systems/theory-extraction-integration.md)**: Literature to schema
- **[Master Concept Library](concepts/master-concept-library.md)**: Domain concepts

## Uncertainty Architecture

### Four-Layer Uncertainty System
1. **Contextual Entity Resolution**: Dynamic disambiguation
2. **Temporal Knowledge Graph**: Time-bounded confidence
3. **Bayesian Pipeline**: Dependency modeling
4. **Distribution Preservation**: Full uncertainty propagation

See **[Uncertainty Architecture](concepts/uncertainty-architecture.md)** for details.

## Quality Attributes

### Performance
- **Single-node optimization**: Vertical scaling approach
- **Async processing**: Non-blocking operations where possible
- **Intelligent caching**: Expensive computation results

### Security  
- **PII encryption**: AES-GCM for sensitive data
- **Local processing**: No cloud dependencies
- **API key management**: Secure credential handling

### Reliability
- **ACID transactions**: Neo4j transactional guarantees
- **Error recovery**: Graceful degradation strategies
- **Checkpoint/restart**: Workflow state persistence

### Maintainability
- **Service modularity**: Clear separation of concerns
- **Contract-first design**: Stable interfaces
- **Comprehensive logging**: Structured operational logs

## Architecture Decision Records

Key architectural decisions are documented in ADRs:

- **[ADR-001](adrs/ADR-001-Phase-Interface-Design.md)**: Contract-first tool interfaces
- **[ADR-002](adrs/ADR-002-Pipeline-Orchestrator-Architecture.md)**: Pipeline orchestration design  
- **[ADR-003](adrs/ADR-003-Vector-Store-Consolidation.md)**: Bi-store data architecture
- **[ADR-004](adrs/ADR-004-Normative-Confidence-Score-Ontology.md)**: Uncertainty quantification

## Related Documentation

### Detailed Architecture
- **[Concepts](concepts/)**: Theoretical frameworks and design patterns
- **[Data Architecture](data/)**: Schemas and data flow
- **[Systems](systems/)**: Component detailed designs
- **[Specifications](specifications/)**: Formal specifications

### Implementation Guidance
**NOT IN THIS DOCUMENT** - See [Roadmap](../planning/roadmap.md) for:
- Current implementation status
- Development phases
- Known issues and limitations
- Timeline and milestones

## Architecture Governance

### Change Process
1. Architectural changes require ADR documentation
2. Major changes need team consensus
3. Updates must maintain principle alignment
4. Cross-reference impacts must be assessed

### Review Cycle
- Quarterly architecture review
- Annual principle reassessment
- Continuous ADR updates as needed

---

This architecture represents our target system design. For current implementation status and development plans, see the [Roadmap Overview](../planning/roadmap.md).