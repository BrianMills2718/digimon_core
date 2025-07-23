# KGAS Architecture Overview

**Status**: Target Architecture  
**Purpose**: Single source of truth for KGAS final architecture  
**Stability**: Changes only when architectural goals change  

**This document defines the target system architecture for KGAS (Knowledge Graph Analysis System). It describes the intended design and component relationships that guide implementation. For current implementation status, see the [Roadmap Overview](../../ROADMAP_OVERVIEW.md).**

---

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

### 5. Fail-Fast Design Philosophy
- **Immediate error exposure**: Problems surface immediately rather than being masked
- **Input validation**: Rigorous validation at system boundaries
- **Complete failure**: System fails entirely on critical errors rather than degrading
- **Evidence-based operation**: All functionality backed by validation evidence

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│         (Natural Language → Agent → Workflow → Results)      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Multi-Layer Agent Interface                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Layer 1:      │ │   Layer 2:      │ │   Layer 3:      │ │
│  │Agent-Controlled │ │Agent-Assisted   │ │Manual Control   │ │
│  │                 │ │                 │ │                 │ │
│  │NL→YAML→Execute  │ │YAML Review      │ │Direct YAML      │ │
│  │Complete Auto    │ │User Approval    │ │Expert Control   │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
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
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │ProvenanceService   │ │WorkflowEngine  │ │SecurityMgr  │ │
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

**📝 [See Detailed Component Architecture](systems/COMPONENT_ARCHITECTURE_DETAILED.md)** for complete specifications including interfaces, algorithms, and pseudo-code examples.

### User Interface Layer
- **[Agent Interface](agent-interface.md)**: Three-layer interface (automated, assisted, manual)
- **[MCP Integration](systems/mcp-integration-architecture.md)**: LLM tool orchestration protocol
- **Workflow Engine**: YAML-based reproducible workflows

### Multi-Layer Agent Interface
#### Layer 1: Agent-Controlled
- **Complete automation**: Natural language → YAML → execution
- **No user intervention**: Fully autonomous workflow generation
- **Optimal for**: Standard research patterns and common analysis tasks

#### Layer 2: Agent-Assisted  
- **Human-in-the-loop**: Agent generates YAML, user reviews and approves
- **Quality control**: User validates before execution
- **Optimal for**: Complex research requiring validation

#### Layer 3: Manual Control
- **Expert control**: Direct YAML workflow creation and modification
- **Maximum flexibility**: Custom workflows and edge cases
- **Optimal for**: Novel research methodologies and system debugging

### Cross-Modal Analysis Layer
- **[Cross-Modal Analysis](cross-modal-analysis.md)**: Fluid movement between representations
- **[Mode Selection](concepts/cross-modal-philosophy.md)**: LLM-driven optimal mode selection
- **[Provenance Tracking](specifications/PROVENANCE.md)**: Complete source traceability

### Core Services Layer
- **[Pipeline Orchestrator](systems/COMPONENT_ARCHITECTURE_DETAILED.md#1-pipeline-orchestrator)**: Workflow coordination with topological sorting
- **[Analytics Service](systems/COMPONENT_ARCHITECTURE_DETAILED.md#2-analytics-service)**: Cross-modal orchestration with mode selection algorithms
- **[Identity Service](systems/COMPONENT_ARCHITECTURE_DETAILED.md#3-identity-service)**: Context-aware entity resolution with multi-factor scoring
- **[Theory Repository](systems/COMPONENT_ARCHITECTURE_DETAILED.md#4-theory-repository)**: Theory schema management and validation
- **[Provenance Service](systems/COMPONENT_ARCHITECTURE_DETAILED.md#5-provenance-service)**: Complete lineage tracking for reproducibility

### Data Storage Layer
- **[Bi-Store Architecture](data/bi-store-justification.md)**: Neo4j + SQLite design with trade-off analysis
- **[Data Models](data/schemas.md)**: Entity, relationship, and metadata schemas
- **[Vector Storage](adrs/ADR-003-Vector-Store-Consolidation.md)**: Native Neo4j vectors with HNSW indexing

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

### Comprehensive Uncertainty Management System

KGAS implements a sophisticated uncertainty management framework that handles both individual extraction confidence and multi-source aggregation:

#### Core Components

1. **Base Confidence Assessment** ([ADR-010](adrs/ADR-010-Quality-System-Design.md))
   - Quality degradation through processing pipelines
   - Tool-specific confidence factors
   - Quality tier classification (HIGH/MEDIUM/LOW)

2. **Bayesian Aggregation System** ([ADR-016](adrs/ADR-016-Bayesian-Uncertainty-Aggregation.md))
   - LLM-based parameter estimation for dependent sources
   - Proper joint likelihood calculation
   - Evidence accumulation from multiple sources
   - Theory-aware prior estimation

3. **IC-Inspired Analytical Techniques** ([ADR-017](adrs/ADR-017-IC-Analytical-Techniques-Integration.md))
   - Information Value Assessment (Heuer's 4 types)
   - Analysis of Competing Hypotheses (ACH) for theory comparison
   - Collection Stopping Rules for optimal information gathering
   - Calibration System for confidence accuracy
   - Mental Model Auditing (planned Phase 3)

4. **Multi-Modal Uncertainty Representation**
   - Probability distributions for quantitative uncertainty
   - Confidence intervals for avoiding false precision
   - Process metadata for qualitative assessment
   - Interactive visualization of uncertainty levels

4. **Strategic Uncertainty Management**
   - Context-aware decision to reduce/maintain/increase uncertainty
   - Robustness testing through perturbation analysis
   - Meta-uncertainty assessment of analysis confidence

See **[Uncertainty Architecture](concepts/uncertainty-architecture.md)** for detailed implementation.

## MCP Integration Architecture

KGAS exposes all system capabilities through the Model Context Protocol (MCP) for comprehensive external tool access:

### Complete Tool Access
- **121+ KGAS tools** accessible via standardized MCP interface
- **Multiple client support**: Works with Claude Desktop, custom Streamlit UI, and other MCP clients
- **Security framework**: Comprehensive security measures addressing MCP protocol vulnerabilities
- **Performance optimization**: Mitigation strategies for MCP limitations (40-tool barrier, context scaling)

### MCP Server Integration
- **FastMCP framework**: Production-grade MCP server implementation
- **External access**: Tool access for Claude Desktop, ChatGPT, and other LLM clients
- **Type-safe interfaces**: Standardized tool protocols
- **Complete documentation**: Auto-generated capability registry

See [MCP Architecture Details](systems/mcp-integration-architecture.md) for comprehensive integration specifications.

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

## Key Architectural Trade-offs

### 1. Single-Node vs Distributed Architecture

**Decision**: Single-node architecture optimized for academic research

**Trade-offs**:
- ✅ **Simplicity**: Easier deployment, maintenance, and debugging
- ✅ **Cost**: Lower infrastructure and operational costs
- ✅ **Consistency**: Simplified data consistency without distributed transactions
- ❌ **Scalability**: Limited to vertical scaling (~1M entities practical limit)
- ❌ **Availability**: No built-in redundancy or failover

**Rationale**: Academic research projects typically process thousands of documents, not millions. The simplicity benefits outweigh scalability limitations for the target use case.

### 2. Bi-Store (Neo4j + SQLite) vs Alternative Architectures

**Decision**: Neo4j for graph/vectors, SQLite for metadata/workflow

**Trade-offs**:
- ✅ **Optimized Storage**: Each database used for its strengths
- ✅ **Native Features**: Graph algorithms in Neo4j, SQL queries in SQLite
- ✅ **Simplicity**: Simpler than tri-store, avoids PostgreSQL complexity
- ❌ **Consistency**: Cross-database transactions not atomic
- ❌ **Integration**: Requires entity ID synchronization

**Rationale**: The bi-store provides the right balance of capability and complexity. See [ADR-003](adrs/ADR-003-Vector-Store-Consolidation.md) for detailed analysis.

### 3. Theory-First vs Data-First Processing

**Decision**: Theory-aware extraction with domain ontologies

**Trade-offs**:
- ✅ **Quality**: Higher quality extractions aligned with domain knowledge
- ✅ **Research Value**: Enables theory validation and testing
- ✅ **Consistency**: Standardized concepts across analyses
- ❌ **Complexity**: Requires theory schema management
- ❌ **Coverage**: May miss emergent patterns not in theories

**Rationale**: KGAS targets theory-driven research where quality and theoretical alignment matter more than discovering completely novel patterns.

### 4. Contract-First Tool Design vs Flexible Interfaces

**Decision**: All tools implement standardized contracts

**Trade-offs**:
- ✅ **Integration**: Tools compose without custom logic
- ✅ **Testing**: Standardized testing across all tools
- ✅ **Agent Orchestration**: Enables intelligent tool selection
- ❌ **Flexibility**: Tools must fit the contract model
- ❌ **Migration Effort**: Existing tools need refactoring

**Rationale**: The long-term benefits of standardization outweigh short-term migration costs. See [ADR-001](adrs/ADR-001-Phase-Interface-Design.md).

### 5. Comprehensive Uncertainty vs Simple Confidence

**Decision**: 4-layer uncertainty architecture with CERQual framework

**Trade-offs**:
- ✅ **Research Quality**: Publication-grade uncertainty quantification
- ✅ **Decision Support**: Rich information for interpretation
- ✅ **Flexibility**: Configurable complexity levels
- ❌ **Complexity**: Harder to implement and understand
- ❌ **Performance**: Additional computation overhead

**Rationale**: Research credibility requires sophisticated uncertainty handling. The architecture allows starting simple and adding layers as needed.

### 6. LLM Integration Approach

**Decision**: LLM for ontology generation and mode selection, not core processing

**Trade-offs**:
- ✅ **Reproducibility**: Core processing deterministic
- ✅ **Cost Control**: LLM used strategically, not for every operation
- ✅ **Flexibility**: Can swap LLM providers
- ❌ **Capability**: May miss LLM advances in extraction
- ❌ **Integration**: Requires careful prompt engineering

**Rationale**: Balances advanced capabilities with research requirements for reproducibility and cost management.

### 7. MCP Protocol for Tool Access

**Decision**: All tools exposed via Model Context Protocol

**Trade-offs**:
- ✅ **Ecosystem**: Integrates with Claude, ChatGPT, etc.
- ✅ **Standardization**: Industry-standard protocol
- ✅ **External Access**: Tools available to any MCP client
- ❌ **Overhead**: Additional protocol layer
- ❌ **Limitations**: MCP's 40-tool discovery limit

**Rationale**: MCP provides immediate integration with LLM ecosystems, outweighing protocol overhead.

## Architecture Decision Records

Key architectural decisions are documented in ADRs:

- **[ADR-001](adrs/ADR-001-Phase-Interface-Design.md)**: Contract-first tool interfaces with trade-off analysis
- **[ADR-002](adrs/ADR-002-Pipeline-Orchestrator-Architecture.md)**: Pipeline orchestration design  
- **[ADR-003](adrs/ADR-003-Vector-Store-Consolidation.md)**: Bi-store data architecture with detailed trade-offs
- **[ADR-004](adrs/ADR-004-Normative-Confidence-Score-Ontology.md)**: Confidence score ontology (superseded by ADR-007)
- **[ADR-005](adrs/ADR-005-buy-vs-build-strategy.md)**: Strategic buy vs build decisions for external services
- **[ADR-007](adrs/adr-004-uncertainty-metrics.md)**: Comprehensive uncertainty metrics framework
- **[ADR-016](adrs/ADR-016-Bayesian-Uncertainty-Aggregation.md)**: Bayesian aggregation for multiple sources
- **[ADR-017](adrs/ADR-017-IC-Analytical-Techniques-Integration.md)**: Intelligence Community analytical techniques for academic research

## Related Documentation

### Detailed Architecture
- **[Concepts](concepts/)**: Theoretical frameworks and design patterns
- **[Data Architecture](data/)**: Schemas and data flow
- **[Systems](systems/)**: Component detailed designs
- **[Specifications](specifications/)**: Formal specifications

### Implementation Status
**NOT IN THIS DOCUMENT** - See [Roadmap Overview](../../ROADMAP_OVERVIEW.md) for:
- Current implementation status and progress
- Development phases and completion evidence
- Known issues and limitations
- Timeline and milestones
- Phase-specific implementation evidence

## Architecture Governance

### Tool Ecosystem Governance
**[See Tool Governance Framework](TOOL_GOVERNANCE.md)** for comprehensive tool lifecycle management, quality standards, and the 121-tool ecosystem governance process.

### Change Process
1. Architectural changes require ADR documentation
2. Major changes need team consensus
3. Updates must maintain principle alignment
4. Cross-reference impacts must be assessed

### Review Cycle
- Quarterly architecture review
- Annual principle reassessment
- Continuous ADR updates as needed
- Monthly tool governance board reviews

---

This architecture represents our target system design. For current implementation status and development plans, see the [Roadmap Overview](../../ROADMAP_OVERVIEW.md).