# KGAS Core Architecture and System Vision

**Description**: Fundamental architecture, principles, and system overview
**Generated**: Split from comprehensive architecture document
**Files Included**: 4

---

## Table of Contents

1. [ARCHITECTURE_OVERVIEW.md](#1-architectureoverviewmd)
2. [GLOSSARY.md](#2-glossarymd)
3. [project-structure.md](#3-projectstructuremd)
4. [CLAUDE.md](#4-claudemd)

---

## 1. ARCHITECTURE_OVERVIEW.md {#1-architectureoverviewmd}

**Source**: `docs/architecture/ARCHITECTURE_OVERVIEW.md`

---

---

# KGAS Architecture Overview

**Status**: Target Architecture  
**Purpose**: Single source of truth for KGAS final architecture  
**Stability**: Changes only when architectural goals change  

**This document defines the target system architecture for KGAS (Knowledge Graph Analysis System). It describes the intended design and component relationships that guide implementation. For current implementation status, see the [Roadmap Overview](../../ROADMAP_OVERVIEW.md).**

---

## System Vision

KGAS (Knowledge Graph Analysis System) is a complete computational social science research platform. It extracts theories from academic literature, converts them into executable analysis specifications, and applies them to datasets at scale. Researchers can validate theories through agent-based simulation, generate statistical models automatically from theoretical frameworks, and discover patterns by converting results between graph, table, and vector representations. The system handles everything from raw documents to publication-ready outputs with full provenance tracking.

## Unique Analytical Capabilities

KGAS enables analytical approaches impossible with traditional research tools:

### Cross-Modal Analysis Integration
- **Statistical models become networks**: SEM results convert to graph structures for centrality and community analysis
- **Network topology informs statistics**: Graph structure guides regression model specification and variable selection
- **Correlation matrices as networks**: Pearson correlations become edge weights for network analysis algorithms
- **Vector clustering enhances statistics**: Embedding-based clustering improves factor analysis and latent variable identification

### Automated Theory Operationalization  
- **Theory schemas to statistical models**: Generate SEM specifications, regression models, and experimental designs directly from theoretical frameworks
- **Theory-driven agent creation**: Convert theoretical propositions into agent behavioral rules for simulation testing
- **Executable theoretical predictions**: Transform qualitative theories into quantitative, testable hypotheses with measurement specifications
- **Multi-theory comparison**: Test competing theoretical explanations simultaneously through parallel analysis pipelines

### Scale and Automation
- **Document processing**: Analyze 1000+ documents compared to 100s possible with manual qualitative coding
- **Simultaneous multi-mode analysis**: Run graph, statistical, and vector analyses concurrently on the same data
- **Automated workflow generation**: Create complete analysis pipelines from natural language research questions
- **Real-time cross-modal conversion**: Transform results between analytical representations without data loss

### Research Workflow Automation
- **Literature to execution**: Extract theories from papers and apply them to new datasets automatically  
- **Hypothesis to test**: Generate experimental designs, power analyses, and statistical specifications from theoretical predictions
- **Analysis to publication**: Produce APA-formatted tables, publication-ready figures, and reproducible analysis reports
- **Discovery to validation**: Identify patterns through exploratory analysis, then validate through simulation and statistical testing

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

### 5. Theory Validation Through Simulation ([ADR-020](adrs/ADR-020-Agent-Based-Modeling-Integration.md))
- **Generative Agent-Based Modeling (GABM)** for theory testing
- **Theory-driven agent parameterization** using KGAS theory schemas
- **Empirical validation** against real behavioral datasets
- **Synthetic experiment generation** for counterfactual analysis

### 6. Comprehensive Statistical Analysis ([ADR-021](adrs/ADR-021-Statistical-Analysis-Integration.md))
- **Advanced statistical methods** including SEM, multivariate analysis, and Bayesian inference
- **Theory-driven model specification** from KGAS theory schemas
- **Cross-modal integration** converting statistical results to graph/vector representations
- **Publication-ready outputs** meeting academic statistical reporting standards

### 7. Fail-Fast Design Philosophy
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
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Statistical Analysis Layer                  │ │
│  │    SEM + Multivariate + Theory-Driven Models            │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Agent-Based Modeling Layer                 │ │
│  │    Theory Validation + Synthetic Experiments            │ │
│  └─────────────────────────────────────────────────────────┘ │
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
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │    ABMService      │ │ValidationEngine│ │UncertaintyMgr│ │
│  ├────────────────────┤ └────────────────┘ └─────────────┘ │
│  │StatisticalService  │                                    │
│  └────────────────────┘                                    │
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

**📊 [See Statistical Analysis Architecture](systems/statistical-analysis-architecture.md)** for comprehensive statistical capabilities including SEM, multivariate analysis, and cross-modal integration.

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
- **[ABM Service](adrs/ADR-020-Agent-Based-Modeling-Integration.md)**: Theory validation through generative agent-based modeling and synthetic experiments

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

## Research Enhancement Features

### Analysis Version Control ([ADR-018](adrs/ADR-018-Analysis-Version-Control.md))
KGAS implements Git-like version control for all analyses, enabling:
- **Checkpoint & Branching**: Save analysis states and explore alternatives
- **History Tracking**: Document how understanding evolved
- **Collaboration**: Share specific versions with reviewers or collaborators
- **Safe Exploration**: Try new approaches without losing work

### Research Assistant Personas ([ADR-019](adrs/ADR-019-Research-Assistant-Personas.md))
Configurable LLM personas provide task-appropriate expertise:
- **Methodologist**: Statistical rigor and research design
- **Domain Expert**: Deep field-specific knowledge
- **Skeptical Reviewer**: Critical analysis and weakness identification
- **Collaborative Colleague**: Supportive ideation and synthesis
- **Thesis Advisor**: Patient guidance for students

These features enhance the research workflow by supporting iterative exploration and providing diverse analytical perspectives.

## Agent-Based Modeling Integration ([ADR-020](adrs/ADR-020-Agent-Based-Modeling-Integration.md))

KGAS incorporates Generative Agent-Based Modeling (GABM) capabilities to enable theory validation through controlled simulation and synthetic experiment generation:

### Theory-Driven Agent Simulation
- **Theory-to-Agent Translation**: Convert KGAS theory schemas directly into agent behavioral rules and psychological profiles
- **Cross-Modal Environments**: Use knowledge graphs, demographic data, and vector embeddings to create rich simulation environments
- **Uncertainty-Aware Agents**: Agents make decisions considering uncertainty levels, mimicking real cognitive processes
- **Empirical Validation**: Validate simulation results against real behavioral datasets (e.g., COVID conspiracy theory dataset)

### Research Applications
- **Theory Testing**: Test competing social science theories through controlled virtual experiments
- **Counterfactual Analysis**: Explore "what if" scenarios impossible to study with real subjects
- **Synthetic Data Generation**: Generate realistic social behavior data for training and testing analytical tools
- **Emergent Behavior Detection**: Discover unexpected patterns arising from theoretical assumptions

### Validation Framework
- **Level 1: Behavioral Pattern Validation**: Compare simulated behaviors to real engagement patterns
- **Level 2: Psychological Construct Validation**: Validate agent psychological states against psychometric scales
- **COVID Dataset Integration**: Use 2,506-person COVID conspiracy theory dataset as ground truth for validation

### ABM-Specific Tools
- **T122_TheoryToAgentTranslator**: Convert theory schemas to agent configurations
- **T123_SimulationDesigner**: Design controlled experiments for theory testing
- **T124_AgentPopulationGenerator**: Generate diverse agent populations from demographic data
- **T125_SimulationValidator**: Validate simulation results against empirical data
- **T126_CounterfactualExplorer**: Explore alternative scenarios through simulation
- **T127_SyntheticDataGenerator**: Generate synthetic datasets for theory testing

## Statistical Analysis Integration ([ADR-021](adrs/ADR-021-Statistical-Analysis-Integration.md))

KGAS provides comprehensive statistical analysis capabilities integrated with its cross-modal architecture:

### Core Statistical Capabilities

- **Descriptive Statistics**: Comprehensive descriptive analysis including distribution tests
- **Inferential Statistics**: Hypothesis testing, confidence intervals, and effect sizes  
- **Regression Modeling**: Linear, logistic, GLM, mixed-effects, and regularized models
- **Multivariate Analysis**: MANOVA, discriminant analysis, canonical correlation
- **Time Series Analysis**: ARIMA, VAR, state space models, and cointegration tests

### Structural Equation Modeling (SEM)

- **Theory-Driven SEM**: Automatically generate SEM specifications from KGAS theory schemas
- **Latent Variable Modeling**: Factor analysis (EFA/CFA), latent class/profile analysis
- **Model Diagnostics**: Comprehensive fit indices, modification indices, and bootstrap CIs
- **Cross-Modal Integration**: Convert SEM results to graph structures for network analysis

### Advanced Statistical Methods

- **Bayesian Analysis**: MCMC, variational inference, and Bayesian SEM
- **Causal Inference**: Propensity scores, instrumental variables, and DAG analysis
- **Meta-Analysis**: Effect size aggregation, heterogeneity tests, and network meta-analysis
- **Machine Learning Statistics**: Regularization, feature selection, and interpretable ML

### Statistical Tool Suite (T43-T60)

**Basic Statistics (T43-T45)**:
- **T43_DescriptiveStatistics**: Mean, median, variance, distribution analysis
- **T44_CorrelationAnalysis**: Pearson, Spearman, partial correlations
- **T45_RegressionAnalysis**: Linear, logistic, mixed-effects models

**SEM & Factor Analysis (T46-T48)**:
- **T46_StructuralEquationModeling**: Full SEM with lavaan/semopy integration
- **T47_FactorAnalysis**: EFA, CFA, reliability analysis
- **T48_LatentVariableModeling**: Latent class, IRT, multilevel SEM

**Multivariate Analysis (T49-T52)**:
- **T49_MultivariateAnalysis**: MANOVA, discriminant analysis
- **T50_ClusterAnalysis**: Hierarchical, k-means, DBSCAN clustering
- **T51_TimeSeriesAnalysis**: ARIMA, VAR, Granger causality
- **T52_SurvivalAnalysis**: Cox regression, Kaplan-Meier, competing risks

**Research Design (T53-T55)**:
- **T53_ExperimentalDesign**: Power analysis, sample size calculation
- **T54_HypothesisTesting**: Parametric/non-parametric tests, multiple comparisons
- **T55_MetaAnalysis**: Effect size aggregation, forest plots

**Advanced Methods (T56-T60)**:
- **T56_BayesianAnalysis**: MCMC, prior specification, model comparison
- **T57_MachineLearningStats**: Statistical ML methods with interpretability
- **T58_CausalInference**: Propensity scores, instrumental variables
- **T59_StatisticalReporting**: APA tables, publication-ready figures
- **T60_CrossModalStatistics**: Statistical-graph-vector integration

### Cross-Modal Statistical Innovation

- **Statistical Results as Graphs**: Convert correlation matrices and SEM models to analyzable networks
- **Graph-Informed Statistics**: Use network structure to inform statistical model specification
- **Theory-Statistical Integration**: Generate statistical models directly from theory schemas
- **Uncertainty Propagation**: Track statistical uncertainty through cross-modal transformations

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

### Research Capabilities
- **Scale**: Process 1000+ documents with maintained analytical quality
- **Integration**: 121+ tools accessible through unified interface protocols
- **Reproducibility**: Complete provenance tracking from source documents to final outputs
- **Academic standards**: APA-formatted tables, publication-ready figures, statistical diagnostics

### Performance
- **Cross-modal conversion**: Real-time transformation between graph, table, and vector representations
- **Parallel analysis**: Concurrent execution of multiple analytical modes on the same dataset
- **Intelligent caching**: Reuse expensive computations across analysis sessions
- **Async processing**: Non-blocking operations for long-running statistical and simulation tasks

### Security  
- **PII encryption**: AES-GCM for sensitive research data
- **Local processing**: Complete data control without cloud dependencies
- **API key management**: Secure credential handling for LLM services
- **Research ethics**: Built-in safeguards for human subjects data

### Reliability
- **ACID transactions**: Guaranteed data consistency across bi-store architecture
- **Error recovery**: Graceful degradation with analysis checkpoint restoration
- **Uncertainty tracking**: Confidence propagation through all analytical pipelines
- **Validation frameworks**: Built-in checks for statistical assumptions and model validity

### Maintainability
- **Theory schema evolution**: Versioned theory specifications with backward compatibility
- **Service modularity**: Independent scaling and updating of analytical components
- **Contract-first design**: Stable interfaces enabling tool ecosystem growth
- **Analysis version control**: Git-like branching for exploratory research workflows

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

### 3. Multi-Paradigm Research Support

**Decision**: Support both theory-driven and data-driven research paradigms

**Capabilities**:
- ✅ **Theory-First**: Theory schemas guide extraction and analysis for hypothesis testing
- ✅ **Data-First**: Grounded theory and exploratory analysis for emergent pattern discovery
- ✅ **Mixed Methods**: Seamless integration of quantitative (SEM, statistics) and qualitative approaches
- ✅ **Cross-Modal Discovery**: Graph/vector analysis reveals patterns missed by single-mode approaches

**Trade-offs**:
- ✅ **Flexibility**: Supports diverse research methodologies and paradigms
- ✅ **Discovery**: Emergent behavior detection (T128) finds novel patterns
- ✅ **Validation**: Theory validation through simulation and statistical testing
- ❌ **Complexity**: Multiple analytical pathways require sophisticated orchestration

**Rationale**: KGAS serves the full spectrum of social science research, from exploratory grounded theory to confirmatory theory testing, enabling researchers to move fluidly between paradigms as research questions evolve.

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
- **[ADR-018](adrs/ADR-018-Analysis-Version-Control.md)**: Git-like version control for research analyses
- **[ADR-019](adrs/ADR-019-Research-Assistant-Personas.md)**: Configurable LLM personas for different research needs
- **[ADR-020](adrs/ADR-020-Agent-Based-Modeling-Integration.md)**: Theory validation through generative agent-based modeling

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

## Implementation Status

This document describes the **target architecture** - the intended final system design. For current implementation status, development progress, and phase completion details, see:

- **[Roadmap Overview](../roadmap/ROADMAP_OVERVIEW.md)** - Current status and major milestones
- **[Phase TDD Implementation](../roadmap/phases/phase-tdd/tdd-implementation-progress.md)** - Active development phase progress  
- **[Clear Implementation Roadmap](../roadmap/initiatives/clear-implementation-roadmap.md)** - Master implementation plan
- **[Tool Implementation Status](../roadmap/initiatives/uncertainty-implementation-plan.md)** - Tool-by-tool completion tracking

*This architecture document contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*

================================================================================

## 2. GLOSSARY.md {#2-glossarymd}

**Source**: `docs/architecture/GLOSSARY.md`

---

---

# KGAS Architecture Glossary

**Version**: 1.0
**Status**: Active
**Last Updated**: 2025-07-22

## Overview

This glossary defines key terms used throughout the KGAS architecture documentation to ensure consistent understanding and communication.

## Core Architectural Terms

### **Cross-Modal Analysis**
The ability to analyze and convert between three primary data representations (graph, table, vector) while preserving semantic meaning and maintaining source traceability. Unlike traditional approaches that reduce information during conversion, KGAS enriches data as it moves between modalities.

### **Theory-Aware Processing**
System components that understand and utilize theoretical frameworks from academic disciplines during analysis. This includes extracting concepts based on domain-specific theories, validating findings against theoretical predictions, and organizing results using established academic frameworks.

### **Bi-Store Architecture**
A data storage architecture using exactly two database systems with complementary strengths. In KGAS, this refers to Neo4j (for graph and vector data) and SQLite (for metadata and workflow state), chosen to balance complexity with functionality.

### **Contract-First Design**
An architectural pattern where standardized interfaces (contracts) are defined before implementation. All tools in KGAS implement the same contract, enabling consistent integration, testing, and orchestration.

### **Uncertainty Quantification**
A multi-layer approach to tracking confidence and uncertainty throughout the analysis pipeline. Includes data quality, extraction confidence, relationship strength, and theory alignment scores.

## Data Architecture Terms

### **Entity**
A distinct real-world concept extracted from documents (person, organization, location, concept, etc.) that becomes a node in the knowledge graph. Each entity has a canonical form and may have multiple surface forms (mentions).

### **Mention**
A specific reference to an entity within a document. Multiple mentions can refer to the same entity (e.g., "John Smith", "Smith", "he" all referring to the same person).

### **Canonical Name**
The authoritative, standardized form of an entity used consistently throughout the system. For example, "International Business Machines Corporation" might be the canonical name for mentions of "IBM", "Big Blue", etc.

### **Entity Resolution**
The process of determining which mentions refer to the same real-world entity, consolidating them under a single canonical representation in the knowledge graph.

### **Provenance**
Complete tracking of data lineage including source documents, processing tools, timestamps, and transformation history. Enables research reproducibility and audit trails.

## Tool Ecosystem Terms

### **Tool**
A self-contained processing component that performs a specific analysis or transformation task. Tools implement the standardized contract and can be composed into workflows.

### **Tool Contract**
The standardized interface that all tools must implement, defining input/output formats, error handling, confidence scoring, and metadata requirements.

### **Phase**
A major stage in document processing (e.g., ingestion, extraction, analysis). The original architecture defined phases, but the current implementation uses a more flexible tool-based approach.

### **Workflow**
A sequence of tool executions that accomplish a complex analysis task. Workflows can be saved as templates for reproducibility.

### **Pipeline**
The overall system for processing documents from input through analysis to results. Includes document ingestion, entity extraction, graph construction, and analysis.

## Cross-Modal Terms

### **Modal Bridge**
A tool that converts data from one representation to another (e.g., Graph to Table Bridge). Bridges preserve source information and enrich rather than reduce data.

### **Enrichment Strategy**
The architectural principle of adding information during modal conversion rather than losing it. For example, converting a graph to a table adds computed metrics rather than just flattening structure.

### **Source Traceability**
The ability to trace any analysis result back to its original source in the documents. Maintained through all modal conversions and transformations.

## Theory Integration Terms

### **Theory Schema**
A formal representation of concepts, relationships, and rules from an academic theory, expressed in a format the system can process.

### **Indigenous Term**
A concept or terminology that originates from a specific academic domain or theory, as opposed to generic terms. These require special handling to preserve domain-specific meaning.

### **Master Concept Library (MCL)**
A centralized registry of all concepts used across theories, including mappings between similar concepts in different theoretical frameworks.

### **Ontology**
A formal representation of knowledge including concepts, properties, and relationships. KGAS can integrate with existing ontologies like DOLCE or domain-specific ones.

### **DOLCE**
Descriptive Ontology for Linguistic and Cognitive Engineering - a foundational ontology that provides basic categories for describing any domain.

## Processing Terms

### **Chunk**
A meaningful segment of text extracted from a document, sized appropriately for processing. Chunks maintain position information for source traceability.

### **Confidence Score**
A numerical measure (0.0-1.0) indicating the system's confidence in a particular extraction, relationship, or analysis result.

### **Quality Tier**
A categorical assessment of data quality (high/medium/low) based on source reliability, extraction confidence, and validation results.

## Service Architecture Terms

### **Core Service**
A fundamental system component providing essential functionality (e.g., IdentityService, TheoryRepository). Core services are singletons accessible throughout the system.

### **Service Protocol**
The standardized interface that all services implement, ensuring consistent initialization, configuration, and lifecycle management.

### **Service Registry**
A central directory of all available services, enabling dynamic discovery and dependency injection.

## Analysis Terms

### **Centrality**
Graph metrics measuring the importance of nodes. Includes degree centrality (connections), betweenness centrality (bridge positions), and PageRank (influence).

### **Community**
A group of densely connected nodes in a graph, often representing related concepts or entities that frequently appear together.

### **Embedding**
A vector representation of text or entities in high-dimensional space, enabling similarity calculations and clustering.

### **Vector Index**
A data structure enabling fast nearest-neighbor searches in high-dimensional vector space. KGAS uses Neo4j's native HNSW index.

## Operational Terms

### **Workflow State**
The current execution status of a processing workflow, including completed steps, pending operations, and intermediate results.

### **Checkpoint**
A saved state of workflow execution that enables resumption after interruption or failure.

### **Reconciliation**
The process of ensuring consistency between different data stores or after system failures.

### **PII Vault**
Encrypted storage for personally identifiable information, separate from the main data stores for security.

## Performance Terms

### **Lazy Loading**
Loading data only when needed rather than eagerly fetching everything upfront. Used to manage memory with large graphs.

### **Batch Processing**
Processing multiple items together for efficiency rather than one at a time.

### **Connection Pooling**
Reusing database connections rather than creating new ones for each operation, improving performance.

### **Async Operation**
Non-blocking operations that allow other processing to continue while waiting for I/O or long-running tasks.

## Quality Assurance Terms

### **Integration Test**
Tests that verify multiple components work correctly together, especially important for tool workflows.

### **Provenance Validation**
Verifying that all data can be traced back to its source and that the processing history is complete.

### **Consistency Check**
Validation that data remains consistent across different stores and after transformations.

### **Mock-Free Testing**
Testing approach that uses real components rather than mocks wherever possible, ensuring tests reflect actual system behavior.

## Future Terms (Planned)

### **Theory Validation Engine**
Planned component for validating analysis results against theoretical predictions.

### **Uncertainty Propagation**
Planned algorithms for calculating how uncertainty compounds through multiple processing steps.

### **Modal Orchestrator**
Planned intelligent component that automatically selects the best data representation for a given analysis task.

### **Distributed Processing**
Planned capability for spreading computation across multiple nodes for large-scale analysis.

---

This glossary is a living document and will be updated as new concepts are introduced or existing terms are refined. For technical implementation details of these concepts, refer to the specific architecture documents in this directory.

================================================================================

## 3. project-structure.md {#3-projectstructuremd}

**Source**: `docs/architecture/project-structure.md`

---

---

# Project Structure Guide

## Root Directory Organization

### 📋 Core Files
- `CLAUDE.md` - Quick navigation and current status
- `README.md` - Project overview and getting started
- `main.py` - Primary entry point
- `requirements*.txt` - Python dependencies

### 📁 Main Directories
- `src/` - **Core KGAS source code** (tools, services, ontology library, MCP server)
- `docs/` - **All documentation** (architecture, planning, development, operations)
- `tests/` - **All test suites** and validation frameworks
- `examples/` - Sample documents and demonstration workflows
- `data/` - Runtime data (ignored by git)
- `config/` - Configuration files and environment settings
- `docker/` - Containerization and deployment configurations

### 🔬 **Production Integration: Automated Theory Extraction**
- `lit_review/` - **Production-ready theory extraction system** ✅
  - `src/schema_creation/` - 3-phase extraction pipeline (0.67s response time)
  - `src/schema_application/` - Theory schema application workflows  
  - `evidence/phase6_production_validation/` - Production certification (0.910 score)
  - `examples/` - Working theory extractions (Young 1996, Social Identity Theory)
  - `schemas/` - Generated theory schemas with DOLCE validation

### 🏛️ **KGAS Core Architecture**
- `src/ontology_library/` - **Master Concept Library with DOLCE alignment** ✅
  - `prototype_mcl.yaml` - DOLCE-validated social science concepts with FOAF/SIOC extensions
  - `prototype_validation.py` - Automated ontological consistency checking
  - `example_theory_schemas/` - Working theory implementations (Social Identity Theory)
- `src/core/` - Core services (orchestration, analytics, identity, provenance)
- `src/tools/` - Phase-based processing tools (Phase 1-3 implementations)
- `src/mcp_server.py` - **Model Context Protocol server** ✅
  - External tool access for LLM clients (Claude Desktop, ChatGPT)
  - Core service tools (T107: Identity, T110: Provenance, T111: Quality, T121: Workflow)
  - Theory schema application through conversational interfaces

### 🔄 **Integration Architecture**
The project integrates three major systems:
1. **KGAS Core**: Cross-modal analysis with DOLCE validation and MCP protocol access
2. **Theory Extraction**: Production-ready automated schema generation (0.910 production score)
3. **MCP Integration**: External tool access enabling natural language orchestration
4. **Integration Bridges**: 
   - Concept mapping and FOAF/SIOC extensions (Complete)
   - Automated theory extraction → MCL integration (In Development)
   - Cross-system quality assurance and governance (Complete)

### 📦 Legacy/Reference Directories  
- `archived/` - Historical implementations and experiments
- `gemini-review-tool/` - External validation and review tools

### 🚀 Launcher Scripts
- `start_graphrag_ui.py` - Main UI launcher
- `start_t301_mcp_server.py` - T301 tools server
- `simple_fastmcp_server.py` - Basic MCP server

## Current Status: Integrated Production System

### **Production-Ready Components** ✅
1. **Automated Theory Extraction**: 0.910 production score, perfect analytical balance
2. **DOLCE-Aligned MCL**: 16 core concepts with ontological validation
3. **Theory Schema Examples**: Working implementations (Social Identity, Cognitive Mapping)
4. **Integration Architecture**: Clear pathways between extraction and analysis systems

### **Development Priorities** 🚧
1. **Integration Bridge**: Complete cross-system concept mapping and validation
2. **API Integration**: Unified interface for theory extraction and analysis
3. **UI Enhancement**: Integrated user interface for complete workflow
4. **Production Deployment**: Complete integration deployment and scaling

### **Research Innovation** 🎓
The integrated system represents a breakthrough in computational social science:
- **First automated theory extraction** with perfect analytical balance
- **DOLCE-grounded social science** ontology and concept library  
- **Cross-modal intelligence** with theory-aware orchestration
- **Production-grade quality** with comprehensive testing and validation

See [Theory Extraction Integration](./systems/theory-extraction-integration.md) for detailed integration specifications.

================================================================================

## 4. CLAUDE.md {#4-claudemd}

**Source**: `docs/architecture/CLAUDE.md`

---

---

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

### 4. Service-Oriented Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                   Core Services Layer                       │
│  ┌────────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │PipelineOrchestrator│ │IdentityService │ │PiiService    │ │
│  ├────────────────────┤ ├────────────────┤ ├──────────────┤ │
│  │AnalyticsService    │ │TheoryRepository│ │QualityService│ │
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
- Non-functional requirements (performance, security, etc.)
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

### Service Integration Pattern
```python
# All components follow this integration pattern
class Component:
    def __init__(self, service_manager: ServiceManager):
        self.identity = service_manager.identity_service
        self.provenance = service_manager.provenance_service
        self.quality = service_manager.quality_service
        # Component can access all core services
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

-- Secure PII storage
CREATE TABLE pii_vault (
    pii_id TEXT PRIMARY KEY,
    ciphertext_b64 TEXT NOT NULL,
    nonce_b64 TEXT NOT NULL
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

## Security Architecture

### Research Environment Security
- **PII Protection**: AES-GCM encryption for sensitive data
- **Access Control**: Appropriate for single-user research environment
- **Data Integrity**: Transaction-based operations ensure consistency
- **Audit Trail**: Complete provenance tracking for research reproducibility

### Security Boundaries
- **Local Processing**: All data processing occurs locally
- **API Security**: Secure handling of external API keys
- **File Security**: Safe handling of uploaded documents
- **Database Security**: Parameterized queries and input validation

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

### Error Handling Architecture
```python
# Fail-fast with recovery guidance
try:
    result = process_data()
    return {"status": "success", "data": result}
except SpecificError as e:
    logger.error(f"Processing failed: {e}")
    return {
        "status": "error", 
        "error": str(e),
        "recovery": "specific_guidance",
        "fallback": alternative_approach()
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

================================================================================

