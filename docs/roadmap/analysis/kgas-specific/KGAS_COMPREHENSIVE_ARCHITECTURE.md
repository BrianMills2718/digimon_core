# KGAS (Knowledge Graph Analysis System) - Comprehensive Architecture Documentation

**Generated**: Programmatically concatenated from architecture documents
**Purpose**: Single comprehensive reference for planned KGAS architecture
**Status**: Target Architecture (intended design)

---

## 1. ARCHITECTURE_OVERVIEW.md

**Source**: `docs/architecture/ARCHITECTURE_OVERVIEW.md`

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

## 2. GLOSSARY.md

**Source**: `docs/architecture/GLOSSARY.md`

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

## 3. project-structure.md

**Source**: `docs/architecture/project-structure.md`

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
- `lit_review/` - **Validated theory extraction system** ✅
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
2. **Theory Extraction**: Validated automated schema generation (0.910 operational score)
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

### **Validated Components** ✅
1. **Automated Theory Extraction**: 0.910 operational score, perfect analytical balance
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

## 4. CLAUDE.md

**Source**: `docs/architecture/CLAUDE.md`

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

## 5. kgas-theoretical-foundation.md

**Source**: `docs/architecture/concepts/kgas-theoretical-foundation.md`

---

# KGAS Evergreen Documentation: Theoretical Foundation and Core Concepts

**Document Version**: 1.0 (Consolidated)  
**Created**: 2025-01-27  
**Purpose**: Single source of truth for all theoretical foundations, core concepts, and architectural principles of the Knowledge Graph Analysis System (KGAS)

---

## 🎯 System Overview

The Knowledge Graph Analysis System (KGAS) is built upon a comprehensive theoretical framework that integrates:

1. **DOLCE Upper Ontology**: Formal ontological foundation providing semantic precision and interoperability
2. **FOAF + SIOC Social Web Schemas**: Established vocabularies for social relationships and online interactions with KGAS extensions
3. **Theory Meta-Schema**: A computable framework for representing social science theories as structured, machine-readable schemas
4. **Master Concept Library**: A standardized vocabulary of social science concepts with precise definitions and multi-ontology alignment
5. **Object-Role Modeling (ORM)**: A conceptual modeling methodology ensuring semantic precision and data consistency
6. **Three-Dimensional Theoretical Framework**: A typology categorizing social theories by scope, mechanism, and domain
7. **Programmatic Contract System**: YAML/JSON contracts with Pydantic validation for ensuring compatibility and robustness

---

## 🏗️ Complete System Architecture (Planned)

The following diagram illustrates the complete planned architecture showing how DOLCE ontological grounding integrates with theory-aware processing:

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    KGAS: THEORY-AWARE KNOWLEDGE GRAPH ANALYSIS                      ║
║                          Complete Planned Architecture                               ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌─ ONTOLOGICAL FOUNDATION ────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  🏛️ DOLCE UPPER ONTOLOGY                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Descriptive Ontology for Linguistic and Cognitive Engineering                  │  │
│  │                                                                                 │  │
│  │ dolce:Endurant ────► Persistent entities (Person, Organization)                │  │
│  │ dolce:Perdurant ───► Temporal entities (Event, Process, Meeting)               │  │
│  │ dolce:Quality ─────► Properties (Credibility, Influence, Trust)                │  │
│  │ dolce:Abstract ────► Conceptual entities (Theory, Policy, Ideology)            │  │
│  │ dolce:SocialObject ► Socially constructed (Institution, Role, Status)          │  │
│  │                                                                                 │  │
│  │ Provides: Formal semantics, ontological consistency, interoperability          │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│                                           ▼                                             │
│  📖 MASTER CONCEPT LIBRARY (MCL) + DOLCE ALIGNMENT                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Domain-Specific Concepts with DOLCE Grounding                                  │  │
│  │                                                                                 │  │
│  │ SocialActor:                    MediaOutlet:                   PolicyEvent:    │  │
│  │ ├─ indigenous_term: ["person"]  ├─ indigenous_term: ["news"]   ├─ indigenous.. │  │
│  │ ├─ upper_parent: dolce:SocialObject ├─ upper_parent: dolce:SocialObject      │  │
│  │ ├─ dolce_constraints:           ├─ dolce_constraints:          ├─ upper_parent │  │
│  │ │  └─ category: "endurant"      │  └─ category: "endurant"     │   dolce:Perdu │  │
│  │ └─ validation: ontological     └─ validation: ontological     └─ category: "pe│  │
│  │                                                                                 │  │
│  │ Indigenous Terms → MCL Canonical → DOLCE IRIs → Validation                     │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
└───────────────────────────────────────────┼─────────────────────────────────────────────┘
                                            │
                                            ▼
┌─ THEORETICAL FRAMEWORK ─────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  📚 THEORY META-SCHEMA + DOLCE VALIDATION                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Social Science Theories as DOLCE-Validated Computable Schemas                  │  │
│  │                                                                                 │  │
│  │ social_identity_theory:                                                        │  │
│  │ ├─ entities:                                                                   │  │
│  │ │  ├─ InGroupMember:                                                           │  │
│  │ │  │  ├─ mcl_id: "SocialActor"                                                 │  │
│  │ │  │  ├─ dolce_parent: "dolce:SocialObject"  ◄─── DOLCE Grounding             │  │
│  │ │  │  └─ validation: ontologically_sound                                       │  │
│  │ │  └─ GroupIdentification:                                                     │  │
│  │ │     ├─ mcl_id: "SocialProcess"                                               │  │
│  │ │     ├─ dolce_parent: "dolce:Perdurant"   ◄─── DOLCE Grounding               │  │
│  │ │     └─ validation: temporal_constraints                                      │  │
│  │ ├─ relationships:                                                              │  │
│  │ │  └─ "identifies_with" (SocialObject → SocialObject) ✓ DOLCE Valid          │  │
│  │ └─ 3D_classification: [Meso, Whom, Agentic]                                   │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│  🔧 OBJECT-ROLE MODELING + DOLCE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ • Object Types → DOLCE Categories                                              │  │
│  │ • Fact Types → Ontologically Valid Relations                                   │  │
│  │ • Constraints → DOLCE Consistency Rules                                        │  │
│  │ • Natural Language → Formal DOLCE Semantics                                    │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─ DOLCE-AWARE PROCESSING PIPELINE ───────────────────────────────────────────────────────┐
│                                                                                         │
│  📄 DOCUMENT INPUT                   🤖 DOLCE-VALIDATED EXTRACTION                     │
│  ┌─────────────────┐                 ┌─────────────────────────────────┐               │
│  │ Research        │────────────────►│ LLM + Theory Schema + DOLCE     │               │
│  │ Documents       │                 │                                 │               │
│  │                 │                 │ • Domain Conversation           │               │
│  │ "Biden announced│                 │ • MCL-Guided Extraction         │               │
│  │ new policy"     │                 │ • DOLCE Validation:             │               │
│  │                 │                 │   - "Biden" → SocialActor →     │               │
│  │                 │                 │     dolce:SocialObject ✓        │               │
│  │                 │                 │   - "announced" → Process →     │               │
│  │                 │                 │     dolce:Perdurant ✓           │               │
│  │                 │                 │   - Relation: participatesIn ✓  │               │
│  └─────────────────┘                 └─────────────────────────────────┘               │
│           │                                           │                                 │
│           ▼                                           ▼                                 │
│  📊 CROSS-MODAL ANALYSIS + DOLCE QUALITY ASSURANCE                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                 │  │
│  │  🌐 GRAPH MODE          📋 TABLE MODE          🔍 VECTOR MODE                   │  │
│  │  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐                   │  │
│  │  │DOLCE-Valid  │       │Ontologically│       │Semantically │                   │  │
│  │  │Entities     │◄─────►│Grounded     │◄─────►│Consistent   │                   │  │
│  │  │Relations    │       │Aggregations │       │Embeddings   │                   │  │
│  │  │Centrality   │       │Statistics   │       │Clustering   │                   │  │
│  │  └─────────────┘       └─────────────┘       └─────────────┘                   │  │
│  │                                                                                 │  │
│  │              🔍 DOLCE VALIDATION LAYER                                          │  │
│  │              ┌─────────────────────────────────────────────┐                   │  │
│  │              │ • Entity-Role Consistency Checking          │                   │  │
│  │              │ • Relationship Ontological Soundness       │                   │  │
│  │              │ • Temporal Constraint Validation           │                   │  │
│  │              │ • Cross-Modal Semantic Preservation        │                   │  │
│  │              └─────────────────────────────────────────────┘                   │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─ ONTOLOGICALLY-GROUNDED RESEARCH OUTPUT ────────────────────────────────────────────────┐
│                                                                                         │
│  📚 ACADEMIC PUBLICATIONS              📊 VALIDATED ANALYSIS                            │
│  ┌─────────────────────────┐          ┌──────────────────────────────────┐            │
│  │ • LaTeX Tables          │          │ • DOLCE-Consistent Visualizations│            │
│  │ • BibTeX Citations      │          │ • Ontologically Valid Queries    │            │
│  │ • Ontologically Valid   │          │ • Semantic Integrity Dashboards  │            │
│  │   Results               │          │ • Theory Validation Reports      │            │
│  │                         │          │                                  │            │
│  │ Full Provenance Chain:  │          │ Quality Assurance Metrics:       │            │
│  │ DOLCE → MCL → Theory →  │          │ • DOLCE Compliance Score          │            │
│  │ Results → Source Pages  │          │ • Ontological Consistency        │            │
│  └─────────────────────────┘          │ • Semantic Precision Index       │            │
│                                       └──────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                            DOLCE-ENHANCED INNOVATIONS                               ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  🏛️ ONTOLOGICAL GROUNDING: Every concept formally grounded in DOLCE categories      ║
║  🔄 SEMANTIC CONSISTENCY: Cross-modal analysis preserves ontological meaning        ║
║  ✅ AUTOMATED VALIDATION: Real-time DOLCE compliance checking                       ║
║  🔗 FORMAL TRACEABILITY: Results traceable to formal ontological foundations       ║
║  🎓 RIGOROUS SCIENCE: Maximum theoretical precision for computational social sci    ║
║  🌐 INTEROPERABILITY: Compatible with other DOLCE-aligned research systems         ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

┌─ EPISTEMOLOGICAL TRANSFORMATION ────────────────────────────────────────────────────────┐
│                                                                                         │
│  🧠 FROM: Ad-hoc concept extraction and analysis                                       │
│  🎯 TO: Formally grounded, ontologically consistent, interoperable science            │
│                                                                                         │
│  Theory Schema + MCL + DOLCE → Extraction → Validation → Analysis → Publication       │
│                                                                                         │
│  Every entity, relationship, and analysis operation has formal ontological            │
│  grounding, enabling unprecedented rigor in computational social science              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

This architecture represents the complete planned system where DOLCE provides foundational ontological grounding for all components, from individual concept definitions through cross-modal analysis operations. The system transforms computational social science from ad-hoc data mining to formally grounded, ontologically consistent, and interoperable scientific analysis.

### Research Context and Integrated Components

KGAS is designed as both a **PhD thesis research project** and a **practical research tool prototype**. The system integrates multiple complementary components to create a comprehensive computational social science framework:

#### **Core KGAS System** (Main Architecture)
- **DOLCE Extension**: First systematic extension of DOLCE ontology to social science research domains
- **Master Concept Library**: DOLCE-aligned standardized vocabulary for social science concepts
- **Cross-Modal Intelligence**: LLM-driven mode selection for optimal analysis approaches
- **Ontological Validation**: Real-time validation framework ensuring theoretical consistency

#### **Theory Extraction Pipeline** (Lit Review Integration)
KGAS incorporates a **validated automated theory extraction system** that transforms academic papers into computable schemas:

- **3-Phase Processing**: Vocabulary extraction → Ontological classification → Schema generation
- **Multi-Model Support**: Property graphs, hypergraphs, tables, sequences, trees, timelines
- **Perfect Analytical Balance**: 1.000 balance score across descriptive, explanatory, predictive, causal, and intervention purposes
- **Production Certified**: 0.910 overall production score with comprehensive testing

#### **Integrated Theory Development Workflow**
```
Academic Papers → Automated Extraction → Theory Schemas → MCL Integration → DOLCE Validation → Analysis Ready
```

This integrated approach enables:
1. **Systematic Theory Operationalization**: Convert any academic theory into computable form
2. **Validated Concept Development**: Ensure extracted concepts align with DOLCE and MCL standards  
3. **Comprehensive Coverage**: Process theories across all analytical purposes and social science domains
4. **Quality Assurance**: Production-grade validation and testing throughout the pipeline

For detailed information about the research contributions, PhD thesis framework, and scholarly positioning, see [Research Contributions and PhD Thesis Framework](./research-contributions.md).

---

## 📚 Theory Meta-Schema: Automated Operationalization of Social Science Theories

### Overview

The Theory Meta-Schema represents a breakthrough in computational social science: the **automated conversion of academic theories into computable, DOLCE-validated schemas**. This system combines human theoretical insight with AI-powered extraction to create a comprehensive, validated framework for theoretically informed analysis.

### Dual-Track Theory Development

KGAS employs two complementary approaches for theory schema development:

#### **Track 1: Automated Theory Extraction** (Validated)
A fully operational 3-phase system that processes academic papers:

**Phase 1: Comprehensive Vocabulary Extraction**
- Extracts ALL theoretical terms from academic papers (not limited subsets)
- Captures definitions, context, and theory-specific categories
- Preserves theoretical nuance and discipline-specific terminology

**Phase 2: Enhanced Ontological Classification** 
- Classifies terms into entities, relationships, properties, actions, measures, modifiers
- Infers specific domain/range constraints for relationships
- Maintains theoretical subcategories and hierarchical structure

**Phase 3: Theory-Adaptive Schema Generation**
- Selects optimal model type: property_graph, hypergraph, table_matrix, sequence, tree, timeline
- Generates complete JSON Schema with DOLCE validation hooks
- Achieves perfect analytical balance across all 5 purposes

#### **Track 2: Manual Concept Library Development** (MCL Integration)
Hand-crafted DOLCE-aligned concept definitions:

- **Master Concept Library**: Standardized vocabulary with DOLCE grounding
- **Example Theory Schemas**: Detailed implementations like Social Identity Theory
- **Validation Framework**: Automated DOLCE compliance checking

### Unified Theory Schema Structure

Both tracks produce schemas with these components:

#### 1. Theory Identity and Metadata
- `theory_id`: Unique identifier (e.g., `social_identity_theory`)
- `theory_name`: Human-readable name
- `authors`: Key theorists and seminal works
- `publication_year`: Seminal publication date
- `domain_of_application`: Social contexts (e.g., "group dynamics")
- `description`: Concise theoretical summary

#### **Temporal Provenance Tracking** (Production Enhancement)
- `ingested_at`: Timestamp when theory was extracted/added to system
- `applied_at`: Array of timestamps when theory was used in analyses
- `version_history`: Semantic versioning with change timestamps
- `usage_frequency`: Analytics on theory application patterns over time

**Purpose**: Enables research reproducibility questions like:
- "Show me theories added after 2025-01-01"
- "Which theories were most used in Q1 2025?"
- "Reproduce analysis using theories as they existed on specific date"

#### 2. Theoretical Classification (Multi-Dimensional Framework)
- `level_of_analysis`: Micro (individual), Meso (group), Macro (society)
- `component_of_influence`: Who (Speaker), Whom (Receiver), What (Message), Channel, Effect
- `causal_metatheory`: Agentic, Structural, Interdependent
- **NEW**: `analytical_purposes`: Descriptive, Explanatory, Predictive, Causal, Intervention

#### 3. DOLCE-Validated Theoretical Core
- `ontology_specification`: Domain-specific concepts aligned with MCL and DOLCE categories
- `mcl_concept_mappings`: Direct references to Master Concept Library entries
- `dolce_validation_checks`: Automated ontological consistency verification
- `axioms`: Core rules or assumptions with formal grounding
- `analytics`: Metrics and measures with DOLCE property validation
- `process`: Analytical workflows with cross-modal orchestration
- `telos`: Multi-purpose analytical objectives and success criteria

### Integration Architecture

The two tracks work synergistically:

```
Academic Papers → Automated Extraction → Raw Schema
                                          ↓
MCL Concepts ← Concept Alignment ← Schema Enhancement
     ↓                               ↓
DOLCE Validation ← Quality Assurance ← Final Schema
     ↓
Validated Theory Schema
```

### Implementation Status and Integration

#### **Production Components** ✅
- **Automated Extraction**: `/lit_review/src/schema_creation/multiphase_processor_improved.py`
- **Schema Generation**: Complete 3-phase pipeline with OpenAI GPT-4 integration
- **Testing Framework**: 6 comprehensive test suites with 83% success rate
- **Performance**: 0.67s average response time, 16.63 req/sec throughput
- **Quality Assurance**: Perfect 1.000 analytical balance score
- **MCP Integration**: Full Model Context Protocol implementation with external tool access

#### **Integration Components** ✅
- **MCL Integration**: `/src/ontology_library/prototype_mcl.yaml` (Complete with FOAF/SIOC/PROV extensions)
- **DOLCE Validation**: `/src/ontology_library/prototype_validation.py` (Complete)
- **Theory Schemas**: Social Identity Theory example implemented and validated
- **MCP Server**: `/src/mcp_server.py` with core service tools (T107, T110, T111, T121)
- **External Access**: Theory Meta-Schema application via MCP protocol

#### **Architecture Bridges**
- **Concept Mapping**: Automated extraction terms → MCL canonical concepts → FOAF/SIOC bridge mappings
- **DOLCE Alignment**: Real-time validation of extracted schemas against DOLCE constraints
- **Multi-Modal Integration**: Theory-adaptive model types → Cross-modal analysis orchestration
- **MCP Protocol**: Theory schemas accessible through standardized tool interface for LLM clients
- **Natural Language Orchestration**: Complete workflows controllable through conversational interfaces

For detailed MCP integration specifications, see [MCP Integration Architecture](../systems/mcp-integration-architecture.md).

---

## 📖 Master Concept Library: DOLCE-Aligned Standardized Vocabulary

### Purpose

The Master Concept Library (MCL) is a **validated, DOLCE-integrated** repository of standardized concepts from social science theories. It serves as the canonical vocabulary bridge between automated theory extraction and formal ontological analysis, ensuring semantic precision and cross-theory compatibility.

### Multi-Source Development Strategy

The MCL is developed through three complementary approaches:

#### **1. Automated Theory Extraction** → **MCL Population**
- **Source**: 200+ academic papers processed through lit_review system
- **Process**: 3-phase extraction → Concept normalization → MCL integration
- **Coverage**: Comprehensive vocabulary across all social science domains
- **Validation**: Automated DOLCE compliance checking

#### **2. Manual Concept Curation** → **DOLCE Grounding** 
- **Source**: Hand-crafted concept definitions with precise DOLCE alignment
- **Process**: Expert curation → DOLCE validation → MCL canonical form
- **Quality**: Perfect ontological consistency and theoretical precision
- **Status**: **Prototype Complete** ✅ - Working implementation with validation framework

**Prototype MCL Achievements**:
- **16 Core Concepts**: 5 entities, 4 connections, 4 properties, 3 modifiers
- **Full DOLCE Integration**: Every concept properly grounded in DOLCE categories
- **Working Validation**: Automated consistency checking with comprehensive test suite
- **Theory Integration**: Complete Social Identity Theory schema demonstrating MCL usage
- **Cross-Theory Support**: Concepts designed for multiple theoretical frameworks

#### **3. Theory Schema Integration** → **Cross-Theory Validation**
- **Source**: Working theory implementations (Social Identity Theory, Cognitive Mapping, etc.)
- **Process**: Schema validation → Concept extraction → MCL enhancement
- **Benefit**: Ensures MCL concepts support real analytical workflows

### DOLCE-Aligned Structure with FOAF/SIOC Extensions

#### **Entity Concepts** (dolce:SocialObject, dolce:Abstract + FOAF/SIOC Integration)
- **SocialActor**: Human/institutional agents (dolce:SocialObject)
  - *Extends*: `foaf:Person`, `foaf:Organization` 
  - *Bridge*: `foaf:Person rdfs:subClassOf dolce:AgentivePhysicalObject`
- **SocialGroup**: Collections with shared identity (dolce:SocialObject)  
  - *Extends*: `foaf:Group`, `sioc:Community`
  - *Bridge*: `foaf:Group rdfs:subClassOf dolce:SocialObject`
- **CognitiveElement**: Mental representations, beliefs (dolce:Abstract)
- **CommunicationMessage**: Information content (dolce:Abstract)
  - *Extends*: `sioc:Post`, `sioc:Thread`, `sioc:Item`
  - *Bridge*: `sioc:Post rdfs:subClassOf dolce:InformationObject`
- **SocialProcess**: Temporal social activities (dolce:Perdurant)
  - *Extends*: `prov:Activity` for provenance tracking
  - *Bridge*: `prov:Activity rdfs:subClassOf dolce:Perdurant`

#### **Connection Concepts** (dolce:dependsOn, dolce:participatesIn + FOAF/SIOC/PROV Integration)
- **InfluencesAttitude**: Causal attitude relationships (dolce:dependsOn)
- **ParticipatesIn**: Actor engagement in processes (dolce:participatesIn)
- **IdentifiesWith**: Psychological group attachment (dolce:dependsOn)
  - *Extends*: `foaf:knows`, `foaf:member`
  - *Bridge*: `foaf:member rdfs:subPropertyOf dolce:participantIn`
- **CausesDissonance**: Cognitive conflict relationships (dolce:dependsOn)
- **CreatesContent**: Content creation relationships
  - *Extends*: `sioc:has_creator`, `prov:wasGeneratedBy`
  - *Bridge*: `sioc:has_creator rdfs:subPropertyOf dolce:createdBy`

#### **Property Concepts** (dolce:Quality, dolce:SocialQuality)
- **ConfidenceLevel**: Certainty/conviction measures (dolce:Quality)
- **InfluencePower**: Social influence capacity (dolce:SocialQuality)
- **PsychologicalNeed**: Fundamental requirements (dolce:Quality)
- **RiskPerception**: Threat/vulnerability assessment (dolce:Quality)

#### **Modifier Concepts**
- **SocialContext**: Environmental situational factors
- **TemporalStage**: Discrete process phases  
- **ProcessingMode**: Cognitive evaluation approaches

### Automated Extraction → MCL Mapping Process

1. **Term Extraction**: Lit_review system extracts indigenous terms from academic papers
2. **Concept Normalization**: Terms mapped to MCL canonical concepts using similarity matching
3. **DOLCE Validation**: Automated checking of ontological consistency
4. **MCL Integration**: New concepts added with proper DOLCE grounding
5. **Cross-Theory Validation**: Ensure concepts support multiple theoretical frameworks

### Integration Architecture

#### **Implementation Locations**
- **Production MCL**: `/src/ontology_library/prototype_mcl.yaml` ✅ **Complete**
- **Validation Framework**: `/src/ontology_library/prototype_validation.py` ✅ **Complete** 
- **Example Theory Schema**: `/src/ontology_library/example_theory_schemas/social_identity_theory.yaml` ✅ **Complete**
- **Automated Extraction**: `/lit_review/src/schema_creation/` (3-phase pipeline) ✅ **Validated**
- **Integration Bridge**: Cross-system concept mapping (In Development)

#### **Prototype Validation System** ✅ **Working Implementation**
- **DOLCEValidator**: Real-time ontological consistency checking
- **MCLTheoryIntegrationValidator**: Schema-to-MCL concept validation
- **Automated Testing**: Complete validation demonstration with sample theory
- **Cross-Theory Compatibility**: Validated concept reuse across multiple theories

#### **Quality Metrics**
- **DOLCE Compliance**: 100% for curated concepts, automated validation for extracted
- **Prototype Coverage**: 16 concepts supporting major social science constructs
- **Cross-Theory Support**: Validated across 19 major social science theories
- **Validation Performance**: Real-time consistency checking with comprehensive reporting

### Extensibility and Evolution

The MCL continuously grows through:
- **Automated Discovery**: New concepts from paper processing
- **Validation Feedback**: Refinement based on analysis results  
- **Domain Expansion**: Extension to new social science areas
- **Community Contribution**: Open framework for researcher additions

This dual-track approach ensures the MCL maintains both comprehensive coverage (through automation) and theoretical precision (through expert curation), creating a robust foundation for computational social science analysis.

---

## 🏗️ Three-Dimensional Theoretical Framework

### Overview

KGAS organizes social-behavioral theories using a three-dimensional framework, enabling both human analysts and machines to reason about influence and persuasion in a structured, computable way.

### The Three Dimensions

#### 1. Level of Analysis (Scale)
- **Micro**: Individual-level (cognitive, personality)
- **Meso**: Group/network-level (community, peer influence)
- **Macro**: Societal-level (media effects, cultural norms)

#### 2. Component of Influence (Lever)
- **Who**: Speaker/Source
- **Whom**: Receiver/Audience
- **What**: Message/Treatment
- **Channel**: Medium/Context
- **Effect**: Outcome/Process

#### 3. Causal Metatheory (Logic)
- **Agentic**: Causation from individual agency
- **Structural**: Causation from external structures
- **Interdependent**: Causation from feedback between agents and structures

### Example Classification

| Component | Micro | Meso | Macro |
|-----------|-------|------|-------|
| Who       | Source credibility | Incidental punditry | Operational code analysis |
| Whom      | ELM, HBM | Social identity theory | The American voter model |
| What      | Message framing | Network effects | Policy agenda setting |
| Channel   | Media effects | Social networks | Mass communication |
| Effect    | Attitude change | Group polarization | Public opinion |

### Application

- Theories are classified along these axes in the Theory Meta-Schema.
- Guides tool selection, LLM prompting, and analysis workflows.

### References

- Lasswell (1948), Druckman (2022), Eyster et al. (2022)

---

## 🔧 Object-Role Modeling (ORM) Methodology

### Overview

Object-Role Modeling (ORM) is the conceptual backbone of KGAS's ontology and data model design. It ensures semantic clarity, natural language alignment, and explicit constraint definition.

### Core ORM Concepts

- **Object Types**: Kinds of things (e.g., Person, Organization)
- **Fact Types**: Elementary relationships (e.g., "Person [has] Name")
- **Roles**: The part an object plays in a fact (e.g., "Identifier")
- **Value Types/Attributes**: Properties (e.g., "credibility_score")
- **Qualifiers/Constraints**: Modifiers or schema rules

### ORM-to-KGAS Mapping

| ORM Concept      | KGAS Implementation         | Example                |
|------------------|----------------------------|------------------------|
| Object Type      | Entity                     | `IndividualActor`      |
| Fact Type        | Relationship (Connection)  | `IdentifiesWith`       |
| Role             | source_role_name, target_role_name | `Identifier` |
| Value Type       | Property                   | `CredibilityScore`     |
| Qualifier        | Modifier/Pydantic validator| Temporal modifier      |

### Hybrid Storage Justification

- **Neo4j**: Object Types → nodes, Fact Types → edges
- **SQLite**: Object Types → tables, Fact Types → foreign keys
- **Qdrant**: ORM concepts guide embedding strategies

### Implementation

- **Data Models**: Pydantic models with explicit roles and constraints
- **Validation**: Enforced at runtime and in CI/CD

---

## 📋 Programmatic Contract System

### Overview

KGAS uses a programmatic contract system to ensure all tools, data models, and workflows are compatible, verifiable, and robust.

### Contract System Components

- **YAML/JSON Contracts**: Define required/produced data types, attributes, and workflow states for each tool.
- **Schema Enforcement**: All contracts are validated using Pydantic models.
- **CI/CD Integration**: Automated tests ensure no code that breaks a contract can be merged.

### Example Contract (YAML)

```yaml
tool_id: T23b_LLM_Extractor
input_contract:
  required_data_types:
    - type: Chunk
      attributes: [content, position]
output_contract:
  produced_data_types:
    - type: Mention
      attributes: [surface_text, entity_candidates]
    - type: Relationship
      attributes: [source_id, target_id, relationship_type, source_role_name, target_role_name]
```

### Implementation

- **Schema Location:** `/compatability_code/contracts/schemas/tool_contract_schema.yaml`
- **Validation:** Pydantic-based runtime checks
- **Testing:** Dedicated contract tests in CI/CD

---

## 🔗 Integration and Relationships

### How Components Work Together

1. **Theory Meta-Schema** defines computable social theories using the **Three-Dimensional Framework** for classification
2. **Master Concept Library** provides standardized vocabulary that all theory schemas reference
3. **ORM Methodology** ensures semantic precision in data models and concept definitions
4. **Contract System** validates that all components work together correctly
5. **Three-Dimensional Framework** guides theory selection and application

### Data Flow

```
Text Input → LLM Extraction → Master Concept Library Mapping → 
ORM-Compliant Data Models → Theory Schema Validation → 
Contract System Verification → Output
```

### Cross-References

- **Development Status**: See `ROADMAP_v2.md` for implementation progress
- **Architecture Details**: See `ARCHITECTURE.md` for system design
- **Compatibility Matrix**: See `COMPATIBILITY_MATRIX.md` for integration status

---

## 🎯 Vision and Goals

### Long-term Vision

KGAS aims to become the premier platform for theoretically-grounded discourse analysis, enabling researchers and analysts to:

1. **Apply Social Science Theories Computationally**: Use the Theory Meta-Schema to apply diverse theoretical frameworks to real-world discourse
2. **Ensure Semantic Precision**: Leverage the Master Concept Library and ORM methodology for consistent, accurate analysis
3. **Enable Systematic Comparison**: Use the Three-Dimensional Framework to compare findings across different theoretical approaches
4. **Maintain Quality and Compatibility**: Use the Contract System to ensure robust, verifiable results

### Success Criteria

- **Theoretical Rigor**: All analyses are grounded in explicit, computable social science theories
- **Semantic Consistency**: Standardized vocabulary ensures comparable results across studies
- **Technical Robustness**: Contract system prevents integration errors and ensures quality
- **Extensibility**: System can accommodate new theories, concepts, and analytical approaches

---

**Note**: This document represents the theoretical foundation and core concepts of KGAS. For implementation status and development progress, see the roadmap documentation. For architectural details, see the architecture documentation. 

================================================================================

## 6. cross-modal-analysis.md

**Source**: `docs/architecture/cross-modal-analysis.md`

---

# Cross-Modal Analysis Architecture

*Status: Target Architecture with Production Theory Integration*

## Overview

KGAS implements a comprehensive cross-modal analysis architecture that enables fluid movement between Graph, Table, and Vector data representations. The system integrates **validated automated theory extraction** with **LLM-driven intelligent orchestration** to provide theory-aware, multi-modal analysis capabilities. This design allows researchers to leverage optimal analysis modes for each research question while maintaining complete theoretical grounding and source traceability.

## Integrated Theory-Modal Architecture

KGAS combines two sophisticated systems for unprecedented analytical capability:

### **Theory-Adaptive Modal Selection** (Validated Integration)
The automated theory extraction system provides **theory-specific modal guidance**:

- **Property Graph Theories**: Social Identity Theory, Cognitive Mapping → Graph mode prioritization  
- **Hypergraph Theories**: Semantic Hypergraphs, N-ary Relations → Custom hypergraph processing
- **Table/Matrix Theories**: Game Theory, Classification Systems → Table mode optimization
- **Sequence Theories**: Stage Models, Process Theories → Temporal analysis workflows
- **Tree Theories**: Taxonomies, Hierarchies → Structural decomposition
- **Timeline Theories**: Historical Development → Temporal progression analysis

### **Intelligent Modal Orchestration** (LLM-Enhanced)
Advanced reasoning layer determines optimal analysis approach by considering both:
- **Research Question Intent**: What the user wants to discover
- **Theoretical Framework**: What the underlying theory suggests
- **Data Characteristics**: What the data structure supports

## Architectural Principles

### Format-Agnostic Research
- **Research question drives format selection**: LLM analyzes research goals and automatically selects optimal analysis mode
- **Seamless transformation**: Intelligent conversion between all representation modes
- **Unified querying**: Single interface for cross-modal queries and analysis
- **Preservation of meaning**: All transformations maintain semantic integrity

### Theory-Enhanced LLM Mode Selection
KGAS combines automated theory extraction insights with advanced LLM reasoning to determine optimal analysis approaches:

#### **Enhanced Mode Selection Algorithm**
```python
async def select_analysis_mode(self, research_question: str, theory_schema: Dict, data_characteristics: Dict) -> AnalysisStrategy:
    """Theory-aware analysis mode selection with production integration."""
    
    # Get theory-specific modal preferences from extraction system
    theory_modal_preferences = self.get_theory_modal_preferences(theory_schema)
    extracted_model_type = theory_schema.get('model_type')  # From lit_review extraction
    analytical_purposes = theory_schema.get('analytical_purposes', [])
    
    mode_selection_prompt = f"""
    Research Question: "{research_question}"
    Theory Framework: {theory_schema.get('theory_name')}
    Extracted Model Type: {extracted_model_type}
    Analytical Purposes: {analytical_purposes}
    Theory Modal Preferences: {theory_modal_preferences}
    Data Characteristics: {data_characteristics}
    
    PRIORITY 1: Honor theory-specific modal preferences from automated extraction
    PRIORITY 2: Consider research question requirements  
    PRIORITY 3: Account for data characteristics and constraints
    """
```

#### **Integrated LLM-Driven Mode Selection**
The enhanced system provides both theory-grounded and question-driven analysis recommendations:

```python
class CrossModalOrchestrator:
    """LLM-driven intelligent mode selection for research questions."""
    
    async def select_analysis_mode(self, research_question: str, data_characteristics: Dict) -> AnalysisStrategy:
        """Analyze research question and recommend optimal analysis approach."""
        
        mode_selection_prompt = f"""
        Research Question: "{research_question}"
        Data Characteristics: {data_characteristics}
        
        Analyze this research question and recommend the optimal analysis approach:
        
        GRAPH MODE best for:
        - Network analysis (influence, centrality, communities)
        - Relationship exploration (who connects to whom)
        - Path analysis (how information/influence flows)
        - Structural analysis (network topology, clustering)
        
        TABLE MODE best for:
        - Statistical analysis (correlations, significance tests)
        - Aggregation and summarization (counts, averages, trends)
        - Comparative analysis (between groups, over time)
        - Quantitative hypothesis testing
        
        VECTOR MODE best for:
        - Semantic similarity (find similar content/entities)
        - Clustering (group by semantic similarity)
        - Search and retrieval (find relevant information)
        - Topic modeling and concept analysis
        
        Consider:
        1. What is the primary analytical goal?
        2. What type of insights are needed?
        3. What analysis method would best answer this question?
        4. Should multiple modes be used in sequence?
        
        Respond with recommended mode(s) and reasoning.
        """
        
        llm_recommendation = await self.llm.analyze(mode_selection_prompt)
        
        return self._parse_analysis_strategy(llm_recommendation)
        
    def _parse_analysis_strategy(self, llm_response: str) -> AnalysisStrategy:
        """Parse LLM response into structured analysis strategy."""
        
        return AnalysisStrategy(
            primary_mode=self._extract_primary_mode(llm_response),
            secondary_modes=self._extract_secondary_modes(llm_response),
            reasoning=self._extract_reasoning(llm_response),
            workflow_steps=self._extract_workflow(llm_response),
            expected_outputs=self._extract_expected_outputs(llm_response)
        )
```

**Example LLM Mode Selection**:

Research Question: *"How do media outlets influence political discourse on climate change?"*

LLM Analysis:
1. **Primary Mode**: Graph - Network analysis to map outlet→politician→topic connections
2. **Secondary Mode**: Table - Statistical analysis of coverage patterns by outlet type  
3. **Tertiary Mode**: Vector - Semantic similarity of climate discourse across outlets
4. **Workflow**: Start with Graph (identify influence networks) → Table (quantify patterns) → Vector (analyze discourse similarity)

This intelligent mode selection ensures researchers get optimal analytical approaches without needing deep knowledge of different data representation advantages.

### Source Traceability
- **Complete provenance**: All results traceable to original document sources
- **Transformation history**: Track all format conversions and processing steps
- **W3C PROV compliance**: Standard provenance tracking across all operations
- **Citation support**: Automatic generation of academic citations and references

KGAS enables researchers to leverage the strengths of different data representations:

### Data Representation Layers

```
┌─────────────────────────────────────────────────────────────┐
│                 Cross-Modal Analysis Layer                  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │Graph Queries│ │Table Queries │ │Vector Queries     │  │
│  │(Cypher)     │ │(SQL/Pandas)  │ │(Similarity)       │  │
│  └──────┬──────┘ └──────┬───────┘ └────────┬──────────┘  │
│         │                │                   │              │
│         └────────────────┴───────────────────┘              │
│                          │                                  │
│                 ┌────────┴────────┐                        │
│                 │ Result Linker   │                        │
│                 └────────┬────────┘                        │
└─────────────────────────┼───────────────────────────────────┘
                          │
                   ┌──────┴──────┐
                   │Source Tracer │
                   └─────────────┘
```

### Cross-Modal Workflows

The system supports fluid movement between representations:

1. **Graph → Table**: Export subgraphs or query results to relational tables for statistical analysis
2. **Table → Graph**: Build graphs from relational data or analysis results
3. **Graph → Vector**: Generate embeddings from graph structures for similarity analysis
4. **Vector → Graph**: Create similarity graphs from vector distances
5. **Any → Source**: Trace any result back to original document chunks

## Data Representation Modes

### Graph Analysis Mode
**Optimal for**: Relationship exploration, network analysis, influence tracking
```python
# Graph representation focuses on relationships and structure
class GraphRepresentation:
    nodes: List[Entity]  # Entities as graph nodes
    edges: List[Relationship]  # Relationships as graph edges
    metadata: GraphMetadata  # Centrality, communities, paths
    
    # Analysis capabilities
    def find_influential_entities(self) -> List[Entity]
    def detect_communities(self) -> List[Community]
    def analyze_paths(self, source: Entity, target: Entity) -> List[Path]
    def calculate_centrality(self) -> Dict[Entity, float]
```

### Table Analysis Mode
**Optimal for**: Statistical analysis, aggregation, correlation discovery
```python
# Table representation focuses on attributes and statistics
class TableRepresentation:
    entities: DataFrame  # Entities with attributes as columns
    relationships: DataFrame  # Relationships as relational table
    metadata: TableMetadata  # Statistics, distributions, correlations
    
    # Analysis capabilities
    def statistical_analysis(self) -> StatisticalSummary
    def correlation_analysis(self) -> CorrelationMatrix
    def aggregate_by_attributes(self, grouping: List[str]) -> DataFrame
    def trend_analysis(self) -> TrendAnalysis
```

### Vector Analysis Mode
**Optimal for**: Similarity search, clustering, semantic analysis
```python
# Vector representation focuses on semantic similarity
class VectorRepresentation:
    entity_embeddings: Dict[Entity, Vector]  # Entity semantic vectors
    relationship_embeddings: Dict[Relationship, Vector]  # Relationship vectors
    metadata: VectorMetadata  # Clusters, similarity scores, semantic spaces
    
    # Analysis capabilities
    def find_similar_entities(self, query: Entity, k: int) -> List[Entity]
    def cluster_entities(self) -> List[Cluster]
    def semantic_search(self, query: str) -> List[Entity]
    def dimensionality_reduction(self) -> ReducedSpace
```

## Cross-Modal Integration Architecture

### Format Conversion Layer
```python
class CrossModalConverter:
    """Intelligent conversion between all data representation modes."""
    
    async def graph_to_table(self, graph: GraphRepresentation, conversion_strategy: str) -> TableRepresentation:
        """Convert graph to table with preservation of source links."""
        
        if conversion_strategy == "entity_attributes":
            # Convert nodes to rows, attributes to columns
            entities_df = self._nodes_to_dataframe(graph.nodes)
            relationships_df = self._edges_to_dataframe(graph.edges)
            
        elif conversion_strategy == "adjacency_matrix":
            # Convert graph structure to adjacency representation
            entities_df = self._create_adjacency_matrix(graph)
            relationships_df = self._create_relationship_summary(graph.edges)
            
        elif conversion_strategy == "path_statistics":
            # Convert path analysis to statistical table
            entities_df = self._path_statistics_to_table(graph)
            relationships_df = self._relationship_statistics(graph.edges)
        
        return TableRepresentation(
            entities=entities_df,
            relationships=relationships_df,
            source_graph=graph,
            conversion_metadata=ConversionMetadata(
                strategy=conversion_strategy,
                conversion_time=datetime.now(),
                source_provenance=graph.metadata.provenance
            )
        )
    
    async def table_to_vector(self, table: TableRepresentation, embedding_strategy: str) -> VectorRepresentation:
        """Convert table to vector with semantic embedding generation."""
        
        entity_embeddings = {}
        relationship_embeddings = {}
        
        if embedding_strategy == "attribute_embedding":
            # Generate embeddings from entity attributes
            for _, entity_row in table.entities.iterrows():
                embedding = await self._generate_attribute_embedding(entity_row)
                entity_embeddings[entity_row['entity_id']] = embedding
                
        elif embedding_strategy == "statistical_embedding":
            # Generate embeddings from statistical properties
            statistical_features = self._extract_statistical_features(table)
            entity_embeddings = await self._embed_statistical_features(statistical_features)
            
        elif embedding_strategy == "hybrid_embedding":
            # Combine multiple embedding approaches
            attribute_embeddings = await self._generate_attribute_embeddings(table)
            statistical_embeddings = await self._generate_statistical_embeddings(table)
            entity_embeddings = self._combine_embeddings(attribute_embeddings, statistical_embeddings)
        
        return VectorRepresentation(
            entity_embeddings=entity_embeddings,
            relationship_embeddings=relationship_embeddings,
            source_table=table,
            conversion_metadata=ConversionMetadata(
                strategy=embedding_strategy,
                conversion_time=datetime.now(),
                source_provenance=table.metadata.provenance
            )
        )
```

### Provenance Integration
```python
class ProvenanceTracker:
    """Track provenance across all cross-modal transformations."""
    
    def track_conversion(self, source_representation: Any, target_representation: Any, conversion_metadata: ConversionMetadata) -> ProvenanceRecord:
        """Create provenance record for cross-modal conversion."""
        
        return ProvenanceRecord(
            activity_type="cross_modal_conversion",
            source_format=type(source_representation).__name__,
            target_format=type(target_representation).__name__,
            conversion_strategy=conversion_metadata.strategy,
            timestamp=conversion_metadata.conversion_time,
            source_provenance=conversion_metadata.source_provenance,
            transformation_parameters=conversion_metadata.parameters,
            quality_metrics=self._calculate_conversion_quality(source_representation, target_representation)
        )
    
    def trace_to_source(self, analysis_result: Any) -> List[SourceReference]:
        """Trace any analysis result back to original source documents."""
        
        # Walk through provenance chain
        provenance_chain = self._build_provenance_chain(analysis_result)
        
        # Extract source references
        source_references = []
        for provenance_record in provenance_chain:
            if provenance_record.activity_type == "document_processing":
                source_refs = self._extract_source_references(provenance_record)
                source_references.extend(source_refs)
        
        return self._deduplicate_sources(source_references)

## Cross-Modal Semantic Preservation

### Technical Requirements
- **Entity Identity Consistency**: Unified entity IDs maintained across all representations
- **Semantic Preservation**: Complete meaning preservation during cross-modal transformations
- **Encoding Method**: Non-lossy encoding that enables full bidirectional capability
- **Quality Metrics**: Measurable preservation metrics to validate transformation integrity

### Tool Categories Supporting Cross-Modal Analysis

#### Graph Analysis Tools (T1-T30)
- **Centrality Analysis**: PageRank, betweenness, closeness centrality
- **Community Detection**: Louvain, modularity-based clustering
- **Path Analysis**: Shortest paths, path enumeration, connectivity
- **Structure Analysis**: Density, clustering coefficient, motifs

#### Table Analysis Tools (T31-T60)
- **Statistical Analysis**: Descriptive statistics, hypothesis testing
- **Correlation Analysis**: Pearson, Spearman, partial correlations
- **Aggregation Tools**: Group-by operations, pivot tables, summaries
- **Trend Analysis**: Time series, regression, forecasting

#### Vector Analysis Tools (T61-T90)
- **Similarity Search**: Cosine similarity, nearest neighbors, ranking
- **Clustering**: K-means, hierarchical, density-based clustering
- **Dimensionality Reduction**: PCA, t-SNE, UMAP
- **Semantic Analysis**: Concept mapping, topic modeling

#### Cross-Modal Integration Tools (T91-T121)
- **Format Converters**: Intelligent conversion between all modalities
- **Provenance Trackers**: Complete source linking and transformation history
- **Quality Assessors**: Conversion quality and information preservation metrics
- **Result Integrators**: Combine results from multiple analysis modes

### Example Research Workflow

```python
# 1. Find influential entities using graph analysis
high_centrality_nodes = graph_analysis.pagerank(top_k=100)

# 2. Convert to table for statistical analysis
entity_table = cross_modal.graph_to_table(high_centrality_nodes)

# 3. Perform statistical analysis
correlation_matrix = table_analysis.correlate(entity_table)

# 4. Find similar entities using embeddings
similar_entities = vector_analysis.find_similar(entity_table.ids)

# 5. Trace everything back to sources
source_references = source_tracer.trace(similar_entities)
``` 

================================================================================

## 7. agent-interface.md

**Source**: `docs/architecture/agent-interface.md`

---

# Multi-Layer Agent Interface Architecture

## Overview

KGAS implements a three-layer agent interface that provides different levels of automation and user control, from complete automation to expert-level manual control. This architecture balances ease of use with the precision required for academic research.

## Design Principles

### Progressive Control Model
- **Layer 1**: Full automation for simple research tasks
- **Layer 2**: Assisted automation with user review and approval
- **Layer 3**: Complete manual control for expert users

### Research-Oriented Design
- **Academic workflow support**: Designed for research methodologies
- **Reproducibility**: All workflows generate reproducible YAML configurations
- **Transparency**: Clear visibility into all processing steps
- **Flexibility**: Support for diverse research questions and methodologies

## Three-Layer Architecture

### Layer 1: Agent-Controlled Interface

```
┌─────────────────────────────────────────────────────────┐
│                  Layer 1: Agent-Controlled              │
│                                                         │
│  Natural Language → LLM Analysis → YAML → Execution    │
│                                                         │
│  "Analyze sentiment in these                            │
│   customer reviews"                                     │
│              ↓                                          │
│  [Automated workflow generation and execution]          │
│              ↓                                          │
│  Complete results with source links                     │
└─────────────────────────────────────────────────────────┘
```

#### Component Design
```python
class AgentControlledInterface:
    """Layer 1: Complete automation for simple research tasks."""
    
    def __init__(self, llm_client, workflow_engine, service_manager):
        self.llm_client = llm_client
        self.workflow_engine = workflow_engine
        self.service_manager = service_manager
    
    async def process_natural_language_request(self, request: str, documents: List[str]) -> Dict[str, Any]:
        """Process request from natural language to results."""
        
        # Step 1: Analyze request and generate workflow
        workflow_yaml = await self._generate_workflow(request, documents)
        
        # Step 2: Execute workflow automatically
        execution_result = await self.workflow_engine.execute(workflow_yaml)
        
        # Step 3: Format results for user
        formatted_results = await self._format_results(execution_result)
        
        return {
            "request": request,
            "generated_workflow": workflow_yaml,
            "execution_result": execution_result,
            "formatted_results": formatted_results,
            "source_provenance": execution_result.get("provenance", [])
        }
    
    async def _generate_workflow(self, request: str, documents: List[str]) -> str:
        """Generate YAML workflow from natural language request."""
        
        prompt = f"""
        Generate a KGAS workflow YAML for this research request:
        "{request}"
        
        Documents available: {len(documents)} files
        
        Generate a complete workflow that:
        1. Processes the documents appropriately
        2. Extracts relevant entities and relationships
        3. Performs the analysis needed to answer the request
        4. Provides results with source traceability
        
        Use KGAS workflow format with proper tool selection.
        """
        
        response = await self.llm_client.generate(prompt)
        return self._extract_yaml_from_response(response)

# Usage example
agent = AgentControlledInterface(llm_client, workflow_engine, services)
results = await agent.process_natural_language_request(
    "What are the main themes in these research papers?", 
    ["paper1.pdf", "paper2.pdf"]
)
```

#### Supported Use Cases
- **Simple content analysis**: Theme extraction, sentiment analysis
- **Basic entity extraction**: People, organizations, concepts from documents
- **Straightforward queries**: "What are the main findings?", "Who are the key authors?"
- **Standard workflows**: Common research patterns with established methodologies

### Layer 2: Agent-Assisted Interface

```
┌─────────────────────────────────────────────────────────┐
│                  Layer 2: Agent-Assisted                │
│                                                         │
│  Natural Language → YAML Generation → User Review →     │
│  User Approval/Editing → Execution                      │
│                                                         │
│  "Perform network analysis on                           │
│   co-authorship patterns"                               │
│              ↓                                          │
│  [Generated YAML workflow]                              │
│              ↓                                          │
│  User reviews and modifies workflow                     │
│              ↓                                          │
│  Approved workflow executed                             │
└─────────────────────────────────────────────────────────┘
```

#### Component Design
```python
class AgentAssistedInterface:
    """Layer 2: Agent-generated workflows with user review."""
    
    async def generate_workflow_for_review(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow and present for user review."""
        
        # Generate initial workflow
        generated_workflow = await self._generate_detailed_workflow(request, context)
        
        # Validate workflow structure
        validation_result = await self.workflow_engine.validate(generated_workflow)
        
        # Prepare for user review
        review_package = {
            "original_request": request,
            "generated_workflow": generated_workflow,
            "validation": validation_result,
            "explanation": await self._explain_workflow(generated_workflow),
            "suggested_modifications": await self._suggest_improvements(generated_workflow),
            "estimated_execution_time": await self._estimate_execution_time(generated_workflow)
        }
        
        return review_package
    
    async def execute_reviewed_workflow(self, workflow_yaml: str, user_modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow after user review and approval."""
        
        # Apply user modifications
        final_workflow = await self._apply_user_modifications(workflow_yaml, user_modifications)
        
        # Final validation
        validation = await self.workflow_engine.validate(final_workflow)
        if not validation.is_valid:
            raise WorkflowValidationError(validation.errors)
        
        # Execute with user approval
        return await self.workflow_engine.execute(final_workflow)
    
    async def _explain_workflow(self, workflow_yaml: str) -> str:
        """Generate human-readable explanation of workflow."""
        
        prompt = f"""
        Explain this KGAS workflow in plain language:
        
        {workflow_yaml}
        
        Focus on:
        1. What data processing steps will occur
        2. What analysis methods will be used
        3. What outputs will be generated
        4. Any potential limitations or considerations
        """
        
        return await self.llm_client.generate(prompt)

# User interface for workflow review
class WorkflowReviewInterface:
    """Interface for reviewing and modifying generated workflows."""
    
    def display_workflow_review(self, review_package: Dict[str, Any]) -> None:
        """Display workflow for user review."""
        
        print("Generated Workflow Review")
        print("=" * 50)
        print(f"Original Request: {review_package['original_request']}")
        print(f"Estimated Execution Time: {review_package['estimated_execution_time']}")
        print()
        
        print("Workflow Explanation:")
        print(review_package['explanation'])
        print()
        
        print("Generated YAML:")
        print(review_package['generated_workflow'])
        print()
        
        if review_package['suggested_modifications']:
            print("Suggested Improvements:")
            for suggestion in review_package['suggested_modifications']:
                print(f"- {suggestion}")
    
    def get_user_modifications(self) -> Dict[str, Any]:
        """Get user modifications to the workflow."""
        # Interactive interface for workflow editing
        pass
```

#### Supported Use Cases
- **Complex analysis tasks**: Multi-step analysis requiring parameter tuning
- **Research methodology verification**: Ensuring workflow matches research standards
- **Parameter optimization**: Adjusting confidence thresholds, analysis parameters
- **Novel research questions**: Questions requiring custom workflow adaptation

### Layer 3: Manual Control Interface

```
┌─────────────────────────────────────────────────────────┐
│                   Layer 3: Manual Control               │
│                                                         │
│  Direct YAML Authoring → Validation → Execution        │
│                                                         │
│  User writes complete YAML workflow specification       │
│              ↓                                          │
│  System validates workflow structure and dependencies   │
│              ↓                                          │
│  Workflow executed with full user control              │
└─────────────────────────────────────────────────────────┘
```

#### Component Design
```python
class ManualControlInterface:
    """Layer 3: Direct YAML workflow authoring and execution."""
    
    def __init__(self, workflow_engine, schema_validator, service_manager):
        self.workflow_engine = workflow_engine
        self.schema_validator = schema_validator
        self.service_manager = service_manager
    
    async def validate_workflow(self, workflow_yaml: str) -> ValidationResult:
        """Comprehensive workflow validation."""
        
        # Parse YAML
        try:
            workflow_dict = yaml.safe_load(workflow_yaml)
        except yaml.YAMLError as e:
            return ValidationResult(False, [f"YAML parsing error: {e}"])
        
        # Schema validation
        schema_validation = await self.schema_validator.validate(workflow_dict)
        
        # Dependency validation
        dependency_validation = await self._validate_dependencies(workflow_dict)
        
        # Resource validation
        resource_validation = await self._validate_resources(workflow_dict)
        
        return ValidationResult.combine([
            schema_validation,
            dependency_validation, 
            resource_validation
        ])
    
    async def execute_workflow(self, workflow_yaml: str) -> ExecutionResult:
        """Execute manually authored workflow."""
        
        # Validate before execution
        validation = await self.validate_workflow(workflow_yaml)
        if not validation.is_valid:
            raise WorkflowValidationError(validation.errors)
        
        # Execute with full logging
        return await self.workflow_engine.execute(workflow_yaml, verbose=True)
    
    def get_workflow_schema(self) -> Dict[str, Any]:
        """Get complete workflow schema for manual authoring."""
        return {
            "workflow_schema": self.schema_validator.get_schema(),
            "available_tools": self.service_manager.get_available_tools(),
            "parameter_documentation": self._get_parameter_docs(),
            "examples": self._get_workflow_examples()
        }

# Workflow authoring support
class WorkflowAuthoringSupport:
    """Support tools for manual workflow authoring."""
    
    def generate_workflow_template(self, task_type: str) -> str:
        """Generate template for specific task types."""
        
        templates = {
            "entity_extraction": """
name: "Entity Extraction Workflow"
description: "Extract entities from documents"

phases:
  - name: "document_processing"
    tools:
      - tool: "t01_pdf_loader"
        inputs:
          file_paths: ["{{input_documents}}"]
      - tool: "t15a_text_chunker"
        inputs:
          chunk_size: 1000
          overlap: 200
  
  - name: "entity_extraction"
    tools:
      - tool: "t23c_ontology_aware_extractor"
        inputs:
          ontology_domain: "{{domain}}"
          confidence_threshold: 0.8
          
outputs:
  - name: "extracted_entities"
    format: "json"
    include_provenance: true
""",
            "graph_analysis": """
name: "Graph Analysis Workflow"
description: "Analyze knowledge graph structure"

phases:
  - name: "graph_construction"
    tools:
      - tool: "t31_entity_builder"
      - tool: "t34_edge_builder"
  
  - name: "graph_analysis"
    tools:
      - tool: "t68_pagerank"
        inputs:
          damping_factor: 0.85
          iterations: 100
      - tool: "community_detection"
        inputs:
          algorithm: "louvain"
          
outputs:
  - name: "graph_metrics"
    format: "csv"
  - name: "community_structure"
    format: "json"
"""
        }
        
        return templates.get(task_type, self._generate_generic_template())
```

#### Supported Use Cases
- **Advanced research methodologies**: Custom analysis requiring precise control
- **Experimental workflows**: Testing new combinations of tools and parameters
- **Performance optimization**: Fine-tuning workflows for specific performance requirements
- **Integration with external tools**: Custom tool integration and data flow

## Implementation Components

### WorkflowAgent: LLM-Driven Generation
```python
class WorkflowAgent:
    """LLM-powered workflow generation for Layers 1 and 2."""
    
    def __init__(self, llm_client, tool_registry, domain_knowledge):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.domain_knowledge = domain_knowledge
    
    async def generate_workflow(self, request: str, context: Dict[str, Any]) -> str:
        """Generate workflow YAML from natural language request."""
        
        # Analyze request intent
        intent_analysis = await self._analyze_request_intent(request)
        
        # Select appropriate tools
        tool_selection = await self._select_tools(intent_analysis, context)
        
        # Generate workflow structure
        workflow_structure = await self._generate_workflow_structure(
            intent_analysis, tool_selection, context
        )
        
        # Convert to YAML
        return self._structure_to_yaml(workflow_structure)
    
    async def _analyze_request_intent(self, request: str) -> IntentAnalysis:
        """Analyze user request to understand research intent."""
        
        prompt = f"""
        Analyze this research request and identify:
        1. Primary research question type (descriptive, explanatory, exploratory)
        2. Required data processing steps
        3. Analysis methods needed
        4. Expected output format
        5. Complexity level (simple, moderate, complex)
        
        Request: "{request}"
        
        Return structured analysis.
        """
        
        response = await self.llm_client.generate(prompt)
        return IntentAnalysis.from_llm_response(response)
```

### WorkflowEngine: YAML/JSON Execution
```python
class WorkflowEngine:
    """Execute workflows defined in YAML/JSON format."""
    
    def __init__(self, service_manager, tool_registry):
        self.service_manager = service_manager
        self.tool_registry = tool_registry
        self.execution_history = []
    
    async def execute(self, workflow_yaml: str, **execution_options) -> ExecutionResult:
        """Execute workflow with full provenance tracking."""
        
        workflow = yaml.safe_load(workflow_yaml)
        execution_id = self._generate_execution_id()
        
        execution_context = ExecutionContext(
            execution_id=execution_id,
            workflow=workflow,
            start_time=datetime.now(),
            options=execution_options
        )
        
        try:
            # Execute phases sequentially
            results = {}
            for phase in workflow.get('phases', []):
                phase_result = await self._execute_phase(phase, execution_context)
                results[phase['name']] = phase_result
                
                # Update context with phase results
                execution_context.add_phase_result(phase['name'], phase_result)
            
            # Generate final outputs
            outputs = await self._generate_outputs(workflow.get('outputs', []), results)
            
            return ExecutionResult(
                execution_id=execution_id,
                status="success",
                results=results,
                outputs=outputs,
                execution_time=(datetime.now() - execution_context.start_time).total_seconds(),
                provenance=execution_context.get_provenance()
            )
            
        except Exception as e:
            return ExecutionResult(
                execution_id=execution_id,
                status="error",
                error=str(e),
                execution_time=(datetime.now() - execution_context.start_time).total_seconds(),
                provenance=execution_context.get_provenance()
            )
```

### WorkflowSchema: Validation and Structure
```python
class WorkflowSchema:
    """Schema validation and structure definition for workflows."""
    
    def get_schema(self) -> Dict[str, Any]:
        """Get complete workflow schema definition."""
        return {
            "type": "object",
            "required": ["name", "phases"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string", "default": "1.0"},
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "tools"],
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parallel": {"type": "boolean", "default": False},
                            "tools": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["tool"],
                                    "properties": {
                                        "tool": {"type": "string"},
                                        "inputs": {"type": "object"},
                                        "outputs": {"type": "object"},
                                        "conditions": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                },
                "outputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "format"],
                        "properties": {
                            "name": {"type": "string"},
                            "format": {"type": "string", "enum": ["json", "csv", "yaml", "txt"]},
                            "include_provenance": {"type": "boolean", "default": True}
                        }
                    }
                }
            }
        }
```

## Integration Benefits

### Research Workflow Support
- **Methodology alignment**: Workflows map to established research methodologies
- **Reproducibility**: All workflows generate reusable YAML configurations
- **Transparency**: Clear visibility into all processing decisions
- **Flexibility**: Support for diverse research questions and approaches

### Progressive Complexity Handling
- **Simple tasks**: Layer 1 provides immediate results
- **Complex analysis**: Layer 2 enables review and refinement
- **Expert control**: Layer 3 provides complete customization

### Quality Assurance
- **Validation at every layer**: Schema, dependency, and resource validation
- **Error handling**: Structured error reporting and recovery guidance
- **Performance monitoring**: Execution time and resource usage tracking
- **Provenance tracking**: Complete audit trail for all operations

This multi-layer agent interface architecture provides the flexibility needed for academic research while maintaining the rigor and reproducibility required for scientific work.

================================================================================

## 8. COMPONENT_ARCHITECTURE_DETAILED.md

**Source**: `docs/architecture/systems/COMPONENT_ARCHITECTURE_DETAILED.md`

---

# KGAS Component Architecture - Detailed Design

**Version**: 1.0
**Status**: Target Architecture
**Last Updated**: 2025-07-22

## Overview

This document provides detailed architectural specifications for all KGAS components, including interfaces, algorithms, data structures, and interaction patterns.

## Core Services Layer

### 1. Pipeline Orchestrator

The PipelineOrchestrator coordinates all document processing workflows, managing state, handling errors, and ensuring reproducibility.

#### Interface Specification

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step_id: str
    tool_id: str
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
@dataclass
class WorkflowDefinition:
    """Complete workflow specification"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    dependencies: Dict[str, List[str]]  # step_id -> [dependency_ids]
    metadata: Dict[str, Any]

class IPipelineOrchestrator(ABC):
    """Interface for pipeline orchestration"""
    
    @abstractmethod
    async def create_workflow(self, definition: WorkflowDefinition) -> str:
        """Create new workflow instance"""
        pass
    
    @abstractmethod
    async def execute_workflow(self, workflow_id: str) -> AsyncIterator[WorkflowStep]:
        """Execute workflow, yielding progress updates"""
        pass
    
    @abstractmethod
    async def pause_workflow(self, workflow_id: str) -> None:
        """Pause running workflow"""
        pass
    
    @abstractmethod
    async def resume_workflow(self, workflow_id: str) -> AsyncIterator[WorkflowStep]:
        """Resume paused workflow"""
        pass
    
    @abstractmethod
    async def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow state"""
        pass
```

#### Core Algorithm

```python
class PipelineOrchestrator(IPipelineOrchestrator):
    """Concrete implementation of pipeline orchestration"""
    
    def __init__(self, service_manager: ServiceManager):
        self.workflows = {}  # In-memory for now
        self.tool_registry = service_manager.get_service("tool_registry")
        self.state_service = service_manager.get_service("workflow_state")
        self.provenance = service_manager.get_service("provenance")
        
    async def execute_workflow(self, workflow_id: str) -> AsyncIterator[WorkflowStep]:
        """
        Execute workflow using topological sort for dependency resolution
        
        Algorithm:
        1. Build dependency graph
        2. Topological sort to find execution order
        3. Execute steps in parallel where possible
        4. Handle errors with retry logic
        5. Checkpoint state after each step
        """
        workflow = self.workflows[workflow_id]
        
        # Build execution graph
        graph = self._build_dependency_graph(workflow)
        execution_order = self._topological_sort(graph)
        
        # Group steps that can run in parallel
        parallel_groups = self._identify_parallel_groups(execution_order, graph)
        
        for group in parallel_groups:
            # Execute steps in parallel
            tasks = []
            for step_id in group:
                step = workflow.get_step(step_id)
                task = self._execute_step(step)
                tasks.append(task)
            
            # Wait for all parallel steps to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle errors
            for step_id, result in zip(group, results):
                step = workflow.get_step(step_id)
                
                if isinstance(result, Exception):
                    step.status = WorkflowStatus.FAILED
                    step.error = str(result)
                    
                    # Retry logic
                    if self._should_retry(step, result):
                        await asyncio.sleep(self._get_backoff_time(step))
                        retry_result = await self._execute_step(step)
                        if not isinstance(retry_result, Exception):
                            result = retry_result
                        else:
                            # Propagate failure
                            raise WorkflowExecutionError(
                                f"Step {step_id} failed after retries: {result}"
                            )
                else:
                    step.outputs = result
                    step.status = WorkflowStatus.COMPLETED
                
                # Checkpoint state
                await self._checkpoint_state(workflow_id, step)
                
                # Yield progress
                yield step
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Kahn's algorithm for topological sorting
        
        Time complexity: O(V + E)
        Space complexity: O(V)
        """
        # Count in-degrees
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # Find nodes with no dependencies
        queue = [node for node in graph if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Reduce in-degree for neighbors
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(graph):
            raise ValueError("Circular dependency detected in workflow")
        
        return result
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute single workflow step with monitoring"""
        # Get tool from registry
        tool = self.tool_registry.get_tool(step.tool_id)
        
        # Create execution context
        context = ExecutionContext(
            workflow_id=step.workflow_id,
            step_id=step.step_id,
            provenance=self.provenance
        )
        
        # Execute with monitoring
        start_time = time.time()
        try:
            # Prepare request
            request = ToolRequest(
                input_data=step.inputs,
                options=step.options,
                context=context
            )
            
            # Execute tool
            result = await tool.execute(request)
            
            # Record provenance
            await self.provenance.record(
                operation=f"execute_{step.tool_id}",
                inputs=step.inputs,
                outputs=result.data,
                duration=time.time() - start_time,
                metadata={
                    "workflow_id": step.workflow_id,
                    "step_id": step.step_id,
                    "confidence": result.confidence.value
                }
            )
            
            return result.data
            
        except Exception as e:
            # Record failure
            await self.provenance.record(
                operation=f"execute_{step.tool_id}_failed",
                inputs=step.inputs,
                error=str(e),
                duration=time.time() - start_time
            )
            raise
```

### 2. Analytics Service

The AnalyticsService orchestrates cross-modal analysis operations, selecting optimal representations and coordinating conversions.

#### Interface Specification

```python
@dataclass
class AnalysisRequest:
    """Request for cross-modal analysis"""
    query: str
    data_source: Any  # Graph, Table, or Vector data
    preferred_mode: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class AnalysisResult:
    """Result of cross-modal analysis"""
    data: Any
    mode: str  # "graph", "table", "vector"
    confidence: AdvancedConfidenceScore
    provenance: List[str]  # Source references
    conversions: List[str]  # Modal conversions applied

class IAnalyticsService(ABC):
    """Interface for cross-modal analytics"""
    
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform cross-modal analysis"""
        pass
    
    @abstractmethod
    async def convert(self, data: Any, from_mode: str, to_mode: str) -> Any:
        """Convert data between modes"""
        pass
    
    @abstractmethod
    async def suggest_mode(self, query: str, data_stats: Dict) -> str:
        """Suggest optimal mode for analysis"""
        pass
```

#### Mode Selection Algorithm

```python
class AnalyticsService(IAnalyticsService):
    """Orchestrates cross-modal analysis"""
    
    def __init__(self, service_manager: ServiceManager):
        self.mode_bridges = {
            ("graph", "table"): GraphToTableBridge(),
            ("table", "vector"): TableToVectorBridge(),
            ("vector", "graph"): VectorToGraphBridge(),
            # ... other combinations
        }
        self.mode_analyzers = {
            "graph": GraphAnalyzer(),
            "table": TableAnalyzer(), 
            "vector": VectorAnalyzer()
        }
        
    async def suggest_mode(self, query: str, data_stats: Dict) -> str:
        """
        LLM-driven mode selection based on query intent
        
        Algorithm:
        1. Extract query features
        2. Match to mode capabilities
        3. Consider data characteristics
        4. Return optimal mode
        """
        # Extract query intent features
        features = self._extract_query_features(query)
        
        # Score each mode
        mode_scores = {}
        
        # Graph mode scoring
        graph_score = 0.0
        if any(term in features for term in [
            "relationship", "connection", "network", "path",
            "centrality", "community", "influence"
        ]):
            graph_score += 0.8
        
        if data_stats.get("node_count", 0) > 10:
            graph_score += 0.2
            
        mode_scores["graph"] = graph_score
        
        # Table mode scoring  
        table_score = 0.0
        if any(term in features for term in [
            "aggregate", "sum", "average", "count", "group",
            "correlation", "regression", "statistical"
        ]):
            table_score += 0.8
            
        if data_stats.get("has_numeric_features", False):
            table_score += 0.2
            
        mode_scores["table"] = table_score
        
        # Vector mode scoring
        vector_score = 0.0
        if any(term in features for term in [
            "similar", "cluster", "embed", "nearest",
            "semantic", "distance", "group"
        ]):
            vector_score += 0.8
            
        if data_stats.get("has_embeddings", False):
            vector_score += 0.2
            
        mode_scores["vector"] = vector_score
        
        # Return highest scoring mode
        return max(mode_scores.items(), key=lambda x: x[1])[0]
    
    async def convert(self, data: Any, from_mode: str, to_mode: str) -> Any:
        """
        Convert data between modes with enrichment
        
        Principle: Add information during conversion, don't lose it
        """
        bridge_key = (from_mode, to_mode)
        
        if bridge_key not in self.mode_bridges:
            # Try indirect path
            path = self._find_conversion_path(from_mode, to_mode)
            if not path:
                raise ValueError(f"No conversion path from {from_mode} to {to_mode}")
            
            # Multi-hop conversion
            result = data
            for i in range(len(path) - 1):
                bridge = self.mode_bridges[(path[i], path[i+1])]
                result = await bridge.convert(result)
            
            return result
        
        # Direct conversion
        bridge = self.mode_bridges[bridge_key]
        return await bridge.convert(data)
```

### 3. Identity Service

The IdentityService manages entity resolution and maintains consistent identity across documents.

#### Interface and Algorithm

```python
class IIdentityService(ABC):
    """Interface for entity identity management"""
    
    @abstractmethod
    async def resolve_entity(self, mention: Mention, context: str) -> Entity:
        """Resolve mention to canonical entity"""
        pass
    
    @abstractmethod
    async def merge_entities(self, entity_ids: List[str]) -> str:
        """Merge multiple entities into one"""
        pass
    
    @abstractmethod
    async def split_entity(self, entity_id: str, criteria: Dict) -> List[str]:
        """Split entity into multiple entities"""
        pass

class IdentityService(IIdentityService):
    """Advanced entity resolution with context awareness"""
    
    def __init__(self, service_manager: ServiceManager):
        self.entity_store = service_manager.get_service("entity_store")
        self.embedder = service_manager.get_service("embedder")
        self.uncertainty = service_manager.get_service("uncertainty")
        
    async def resolve_entity(self, mention: Mention, context: str) -> Entity:
        """
        Context-aware entity resolution algorithm
        
        Steps:
        1. Generate contextual embedding
        2. Search for candidate entities
        3. Score candidates with context
        4. Apply uncertainty quantification
        5. Return best match or create new
        """
        # Step 1: Contextual embedding
        mention_embedding = await self.embedder.embed_with_context(
            text=mention.surface_form,
            context=context,
            window_size=500  # tokens
        )
        
        # Step 2: Find candidates
        candidates = await self._find_candidates(mention, mention_embedding)
        
        if not candidates:
            # Create new entity
            return await self._create_entity(mention, mention_embedding)
        
        # Step 3: Context-aware scoring
        scores = []
        for candidate in candidates:
            score = await self._score_candidate(
                mention=mention,
                mention_embedding=mention_embedding,
                candidate=candidate,
                context=context
            )
            scores.append(score)
        
        # Step 4: Apply uncertainty
        best_idx = np.argmax([s.value for s in scores])
        best_score = scores[best_idx]
        best_candidate = candidates[best_idx]
        
        # Step 5: Decision with threshold
        if best_score.value > self.resolution_threshold:
            # Update entity with new mention
            await self._add_mention_to_entity(
                entity=best_candidate,
                mention=mention,
                confidence=best_score
            )
            return best_candidate
        else:
            # Uncertainty too high - create new entity
            return await self._create_entity(
                mention, 
                mention_embedding,
                similar_to=[best_candidate.entity_id]
            )
    
    async def _score_candidate(self, 
                              mention: Mention,
                              mention_embedding: np.ndarray,
                              candidate: Entity,
                              context: str) -> AdvancedConfidenceScore:
        """
        Multi-factor scoring for entity resolution
        
        Factors:
        1. Embedding similarity
        2. String similarity
        3. Type compatibility
        4. Context compatibility
        5. Temporal consistency
        """
        scores = {}
        
        # 1. Embedding similarity (cosine)
        embedding_sim = self._cosine_similarity(
            mention_embedding, 
            candidate.embedding
        )
        scores["embedding"] = embedding_sim
        
        # 2. String similarity (multiple metrics)
        string_scores = [
            self._levenshtein_similarity(
                mention.surface_form, 
                candidate.canonical_name
            ),
            self._jaro_winkler_similarity(
                mention.surface_form,
                candidate.canonical_name  
            ),
            self._token_overlap(
                mention.surface_form,
                candidate.canonical_name
            )
        ]
        scores["string"] = max(string_scores)
        
        # 3. Type compatibility
        if mention.entity_type == candidate.entity_type:
            scores["type"] = 1.0
        elif self._types_compatible(mention.entity_type, candidate.entity_type):
            scores["type"] = 0.7
        else:
            scores["type"] = 0.0
        
        # 4. Context compatibility using LLM
        context_score = await self._evaluate_context_compatibility(
            mention_context=context,
            entity_contexts=candidate.contexts[-5:],  # Last 5 contexts
            mention_text=mention.surface_form,
            entity_name=candidate.canonical_name
        )
        scores["context"] = context_score
        
        # 5. Temporal consistency
        if self._temporally_consistent(mention.timestamp, candidate.temporal_bounds):
            scores["temporal"] = 1.0
        else:
            scores["temporal"] = 0.3
        
        # Weighted combination
        weights = {
            "embedding": 0.3,
            "string": 0.2,
            "type": 0.2,
            "context": 0.2,
            "temporal": 0.1
        }
        
        final_score = sum(
            scores[factor] * weight 
            for factor, weight in weights.items()
        )
        
        # Build confidence score with CERQual
        return AdvancedConfidenceScore(
            value=final_score,
            methodological_quality=0.9,  # Well-established algorithm
            relevance_to_context=scores["context"],
            coherence_score=scores["type"] * scores["temporal"],
            data_adequacy=len(candidate.mentions) / 100,  # More mentions = better
            evidence_weight=len(candidate.mentions),
            depends_on=[mention.extraction_confidence]
        )
```

### 4. Theory Repository

The TheoryRepository manages theory schemas and provides theory-aware processing capabilities.

#### Theory Management System

```python
@dataclass
class TheorySchema:
    """Complete theory specification"""
    schema_id: str
    name: str
    domain: str
    version: str
    
    # Core components
    constructs: List[Construct]
    relationships: List[TheoryRelationship]
    measurement_models: List[MeasurementModel]
    
    # Ontological grounding
    ontology_mappings: Dict[str, str]  # construct_id -> ontology_uri
    dolce_alignment: Dict[str, str]   # construct_id -> DOLCE category
    
    # Validation rules
    constraints: List[Constraint]
    incompatibilities: List[str]  # Incompatible theory IDs
    
    # Metadata
    authors: List[str]
    citations: List[str]
    evidence_base: Dict[str, float]  # construct -> evidence strength

class ITheoryRepository(ABC):
    """Interface for theory management"""
    
    @abstractmethod
    async def register_theory(self, schema: TheorySchema) -> str:
        """Register new theory schema"""
        pass
    
    @abstractmethod
    async def get_theory(self, schema_id: str) -> TheorySchema:
        """Retrieve theory schema"""
        pass
    
    @abstractmethod
    async def validate_extraction(self, 
                                 extraction: Dict,
                                 theory_id: str) -> ValidationResult:
        """Validate extraction against theory"""
        pass
    
    @abstractmethod
    async def suggest_theories(self, 
                             domain: str,
                             text_sample: str) -> List[TheorySchema]:
        """Suggest applicable theories"""
        pass

class TheoryRepository(ITheoryRepository):
    """Advanced theory management with validation"""
    
    def __init__(self, service_manager: ServiceManager):
        self.theories: Dict[str, TheorySchema] = {}
        self.mcl = service_manager.get_service("master_concept_library")
        self.validator = TheoryValidator()
        
    async def validate_extraction(self,
                                 extraction: Dict,
                                 theory_id: str) -> ValidationResult:
        """
        Validate extraction against theory constraints
        
        Algorithm:
        1. Check construct presence
        2. Validate measurement models
        3. Check relationship consistency
        4. Apply theory constraints
        5. Calculate confidence
        """
        theory = self.theories[theory_id]
        violations = []
        warnings = []
        
        # 1. Check required constructs
        extracted_constructs = set(extraction.get("constructs", {}).keys())
        required_constructs = {
            c.id for c in theory.constructs 
            if c.required
        }
        
        missing = required_constructs - extracted_constructs
        if missing:
            violations.append(
                f"Missing required constructs: {missing}"
            )
        
        # 2. Validate measurements
        for construct_id, measurements in extraction.get("measurements", {}).items():
            construct = self._get_construct(theory, construct_id)
            if not construct:
                continue
                
            model = self._get_measurement_model(theory, construct_id)
            if model:
                valid, issues = self._validate_measurement(
                    measurements, 
                    model
                )
                if not valid:
                    violations.extend(issues)
        
        # 3. Check relationships
        for rel in extraction.get("relationships", []):
            if not self._relationship_valid(rel, theory):
                violations.append(
                    f"Invalid relationship: {rel['type']} between "
                    f"{rel['source']} and {rel['target']}"
                )
        
        # 4. Apply constraints
        for constraint in theory.constraints:
            if not self._evaluate_constraint(constraint, extraction):
                violations.append(
                    f"Constraint violation: {constraint.description}"
                )
        
        # 5. Calculate confidence
        if violations:
            confidence = 0.3  # Low confidence with violations
        elif warnings:
            confidence = 0.7  # Medium confidence with warnings
        else:
            confidence = 0.9  # High confidence when fully valid
        
        return ValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            confidence=confidence,
            suggestions=self._generate_suggestions(violations, theory)
        )
    
    async def suggest_theories(self,
                             domain: str,
                             text_sample: str) -> List[TheorySchema]:
        """
        Smart theory suggestion using domain and content analysis
        
        Algorithm:
        1. Filter by domain
        2. Extract key concepts from text
        3. Match concepts to theory constructs
        4. Rank by relevance
        5. Check compatibility
        """
        # 1. Domain filtering
        candidate_theories = [
            t for t in self.theories.values()
            if t.domain == domain or domain in t.related_domains
        ]
        
        # 2. Extract concepts using NER + domain terminology
        concepts = await self._extract_key_concepts(text_sample, domain)
        
        # 3. Score theories by concept overlap
        theory_scores = []
        for theory in candidate_theories:
            score = self._calculate_theory_relevance(
                theory=theory,
                concepts=concepts,
                text_sample=text_sample
            )
            theory_scores.append((theory, score))
        
        # 4. Rank and filter
        theory_scores.sort(key=lambda x: x[1], reverse=True)
        top_theories = [t for t, s in theory_scores[:5] if s > 0.3]
        
        # 5. Check compatibility if multiple theories
        if len(top_theories) > 1:
            compatible_sets = self._find_compatible_theory_sets(top_theories)
            # Return largest compatible set
            if compatible_sets:
                top_theories = max(compatible_sets, key=len)
        
        return top_theories
```

### 5. Provenance Service

Complete lineage tracking for reproducibility.

#### Provenance Implementation

```python
@dataclass
class ProvenanceRecord:
    """Complete provenance for an operation"""
    record_id: str
    timestamp: datetime
    operation: str
    tool_id: str
    tool_version: str
    
    # Inputs and outputs
    inputs: List[ProvenanceReference]
    outputs: List[ProvenanceReference]
    parameters: Dict[str, Any]
    
    # Execution context
    workflow_id: Optional[str]
    step_id: Optional[str]
    user_id: Optional[str]
    
    # Performance metrics
    duration_ms: float
    memory_usage_mb: float
    
    # Quality metrics
    confidence: Optional[float]
    warnings: List[str]
    
    # Lineage
    depends_on: List[str]  # Previous record IDs
    
@dataclass
class ProvenanceReference:
    """Reference to data with provenance"""
    ref_type: str  # "entity", "document", "chunk", etc.
    ref_id: str
    ref_hash: str  # Content hash for verification
    confidence: float

class ProvenanceService:
    """Comprehensive provenance tracking"""
    
    def __init__(self, storage: ProvenanceStorage):
        self.storage = storage
        self.hasher = ContentHasher()
        
    async def record_operation(self,
                             operation: str,
                             tool: Tool,
                             inputs: Dict[str, Any],
                             outputs: Dict[str, Any],
                             context: ExecutionContext) -> ProvenanceRecord:
        """
        Record complete operation provenance
        
        Features:
        1. Content hashing for verification
        2. Automatic lineage tracking
        3. Performance metrics capture
        4. Confidence propagation
        """
        # Create input references with hashing
        input_refs = []
        for key, value in inputs.items():
            ref = ProvenanceReference(
                ref_type=self._determine_type(value),
                ref_id=self._extract_id(value),
                ref_hash=self.hasher.hash(value),
                confidence=self._extract_confidence(value)
            )
            input_refs.append(ref)
        
        # Create output references
        output_refs = []
        for key, value in outputs.items():
            ref = ProvenanceReference(
                ref_type=self._determine_type(value),
                ref_id=self._extract_id(value), 
                ref_hash=self.hasher.hash(value),
                confidence=self._extract_confidence(value)
            )
            output_refs.append(ref)
        
        # Find dependencies from inputs
        depends_on = await self._find_dependencies(input_refs)
        
        # Create record
        record = ProvenanceRecord(
            record_id=self._generate_id(),
            timestamp=datetime.utcnow(),
            operation=operation,
            tool_id=tool.tool_id,
            tool_version=tool.version,
            inputs=input_refs,
            outputs=output_refs,
            parameters=tool.get_parameters(),
            workflow_id=context.workflow_id,
            step_id=context.step_id,
            user_id=context.user_id,
            duration_ms=context.duration_ms,
            memory_usage_mb=context.memory_usage_mb,
            confidence=outputs.get("confidence"),
            warnings=context.warnings,
            depends_on=depends_on
        )
        
        # Store record
        await self.storage.store(record)
        
        # Update indexes for fast queries
        await self._update_indexes(record)
        
        return record
    
    async def trace_lineage(self, 
                          artifact_id: str,
                          direction: str = "backward") -> LineageGraph:
        """
        Trace complete lineage of an artifact
        
        Algorithm:
        1. Start from artifact
        2. Follow provenance links
        3. Build DAG of operations
        4. Include confidence decay
        """
        if direction == "backward":
            return await self._trace_backward(artifact_id)
        else:
            return await self._trace_forward(artifact_id)
    
    async def _trace_backward(self, artifact_id: str) -> LineageGraph:
        """Trace how artifact was created"""
        graph = LineageGraph()
        visited = set()
        queue = [(artifact_id, 0)]  # (id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Find records that output this artifact
            records = await self.storage.find_by_output(current_id)
            
            for record in records:
                # Add node to graph
                graph.add_node(
                    node_id=record.record_id,
                    node_type="operation",
                    operation=record.operation,
                    tool=record.tool_id,
                    timestamp=record.timestamp,
                    confidence=record.confidence,
                    depth=depth
                )
                
                # Add edge from inputs to this operation
                for input_ref in record.inputs:
                    graph.add_edge(
                        source=input_ref.ref_id,
                        target=record.record_id,
                        edge_type="input_to",
                        confidence_impact=input_ref.confidence
                    )
                    
                    # Queue input for processing
                    if input_ref.ref_id not in visited:
                        queue.append((input_ref.ref_id, depth + 1))
                
                # Add edge from operation to output
                graph.add_edge(
                    source=record.record_id,
                    target=current_id,
                    edge_type="output_from",
                    confidence_impact=record.confidence
                )
        
        return graph
    
    async def verify_reproducibility(self,
                                   workflow_id: str,
                                   target_outputs: List[str]) -> ReproducibilityReport:
        """
        Verify workflow can be reproduced
        
        Checks:
        1. All inputs available
        2. All tools available with correct versions
        3. Parameters recorded
        4. No missing dependencies
        """
        records = await self.storage.find_by_workflow(workflow_id)
        
        issues = []
        missing_inputs = []
        version_conflicts = []
        
        for record in records:
            # Check input availability
            for input_ref in record.inputs:
                if not await self._artifact_exists(input_ref):
                    missing_inputs.append(input_ref)
            
            # Check tool availability
            tool = self.tool_registry.get_tool(
                record.tool_id, 
                version=record.tool_version
            )
            if not tool:
                issues.append(
                    f"Tool {record.tool_id} v{record.tool_version} not available"
                )
            elif tool.version != record.tool_version:
                version_conflicts.append(
                    f"Tool {record.tool_id}: recorded v{record.tool_version}, "
                    f"available v{tool.version}"
                )
        
        # Calculate reproducibility score
        score = 1.0
        if missing_inputs:
            score *= 0.5
        if version_conflicts:
            score *= 0.8
        if issues:
            score *= 0.3
        
        return ReproducibilityReport(
            reproducible=score > 0.7,
            score=score,
            missing_inputs=missing_inputs,
            version_conflicts=version_conflicts,
            issues=issues,
            recommendations=self._generate_recommendations(
                missing_inputs,
                version_conflicts,
                issues
            )
        )
```

## Cross-Modal Bridge Components

### Graph to Table Bridge

```python
class GraphToTableBridge:
    """Convert graph data to tabular format with enrichment"""
    
    async def convert(self, graph: Neo4jGraph) -> pd.DataFrame:
        """
        Convert graph to table with computed features
        
        Enrichment approach:
        1. Node properties → columns
        2. Add computed graph metrics
        3. Aggregate relationship data
        4. Preserve graph structure info
        """
        # Extract nodes with properties
        nodes_data = []
        
        async for node in graph.get_nodes():
            row = {
                "node_id": node.id,
                "type": node.labels[0],
                **node.properties
            }
            
            # Add graph metrics
            metrics = await self._compute_node_metrics(node, graph)
            row.update({
                "degree": metrics.degree,
                "in_degree": metrics.in_degree,
                "out_degree": metrics.out_degree,
                "pagerank": metrics.pagerank,
                "betweenness": metrics.betweenness,
                "clustering_coeff": metrics.clustering_coefficient,
                "community_id": metrics.community_id
            })
            
            # Aggregate relationship info
            rel_summary = await self._summarize_relationships(node, graph)
            row.update({
                "rel_types": rel_summary.types,
                "rel_count": rel_summary.count,
                "avg_rel_weight": rel_summary.avg_weight,
                "strongest_connection": rel_summary.strongest
            })
            
            nodes_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(nodes_data)
        
        # Add metadata
        df.attrs["source_type"] = "graph"
        df.attrs["conversion_time"] = datetime.utcnow()
        df.attrs["node_count"] = len(nodes_data)
        df.attrs["enrichments"] = [
            "degree_metrics",
            "centrality_scores", 
            "community_detection",
            "relationship_aggregation"
        ]
        
        return df
```

### Table to Vector Bridge

```python
class TableToVectorBridge:
    """Convert tabular data to vector representations"""
    
    async def convert(self, df: pd.DataFrame) -> VectorStore:
        """
        Convert table to vectors with multiple strategies
        
        Strategies:
        1. Row embeddings (each row → vector)
        2. Column embeddings (each column → vector)
        3. Cell embeddings (each cell → vector)
        4. Aggregate embeddings (groups → vectors)
        """
        vector_store = VectorStore()
        
        # Strategy 1: Row embeddings
        if self._should_embed_rows(df):
            row_vectors = await self._embed_rows(df)
            vector_store.add_vectors(
                vectors=row_vectors,
                metadata={"type": "row", "source": "table"}
            )
        
        # Strategy 2: Column embeddings for text columns
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if self._should_embed_column(df[col]):
                col_vectors = await self._embed_column(df[col])
                vector_store.add_vectors(
                    vectors=col_vectors,
                    metadata={"type": "column", "column_name": col}
                )
        
        # Strategy 3: Smart aggregations
        if "group_by" in df.attrs:
            group_col = df.attrs["group_by"]
            for group_val in df[group_col].unique():
                group_data = df[df[group_col] == group_val]
                group_vector = await self._embed_group(group_data)
                vector_store.add_vector(
                    vector=group_vector,
                    metadata={
                        "type": "group",
                        "group": f"{group_col}={group_val}",
                        "size": len(group_data)
                    }
                )
        
        return vector_store
    
    async def _embed_rows(self, df: pd.DataFrame) -> List[np.ndarray]:
        """Embed each row as a vector"""
        embeddings = []
        
        for _, row in df.iterrows():
            # Combine all row data into text
            text_parts = []
            for col, val in row.items():
                if pd.notna(val):
                    text_parts.append(f"{col}: {val}")
            
            row_text = "; ".join(text_parts)
            embedding = await self.embedder.embed(row_text)
            embeddings.append(embedding)
        
        return embeddings
```

## Tool Contract Implementation

### Example Tool: Advanced Entity Extractor

```python
class AdvancedEntityExtractor(KGASTool):
    """
    Theory-aware entity extraction with uncertainty
    
    Demonstrates:
    1. Contract compliance
    2. Theory integration
    3. Uncertainty quantification
    4. Error handling
    """
    
    def __init__(self):
        self.ner_model = self._load_model()
        self.theory_matcher = TheoryAwareMatcher()
        self.uncertainty_engine = UncertaintyEngine()
        
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "context": {"type": "string"},
                "theory_schemas": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "type": {"type": "string"},
                            "start": {"type": "integer"},
                            "end": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "theory_grounding": {"type": "object"}
                        }
                    }
                }
            }
        }
    
    async def execute(self, request: ToolRequest) -> ToolResult:
        """
        Execute entity extraction with full contract compliance
        """
        try:
            # Validate input
            text = request.input_data["text"]
            context = request.input_data.get("context", "")
            theory_ids = request.input_data.get("theory_schemas", [])
            
            # Load theories if specified
            theories = []
            if theory_ids:
                for theory_id in theory_ids:
                    theory = await self.theory_repo.get_theory(theory_id)
                    theories.append(theory)
            
            # Step 1: Base NER
            base_entities = await self._extract_base_entities(text)
            
            # Step 2: Theory-aware enhancement
            if theories:
                enhanced_entities = await self._enhance_with_theory(
                    base_entities, 
                    text,
                    theories
                )
            else:
                enhanced_entities = base_entities
            
            # Step 3: Context-aware resolution
            resolved_entities = await self._resolve_with_context(
                enhanced_entities,
                context
            )
            
            # Step 4: Uncertainty quantification
            final_entities = []
            for entity in resolved_entities:
                confidence = await self.uncertainty_engine.assess_uncertainty(
                    claim=entity,
                    context=UncertaintyContext(
                        domain=self._detect_domain(text),
                        has_theory=len(theories) > 0,
                        context_strength=len(context) / len(text)
                    )
                )
                
                entity["confidence"] = confidence.value
                entity["uncertainty_details"] = confidence.to_dict()
                final_entities.append(entity)
            
            # Build result
            return ToolResult(
                status="success",
                data={"entities": final_entities},
                confidence=self._aggregate_confidence(final_entities),
                metadata={
                    "model_version": self.ner_model.version,
                    "theories_applied": theory_ids,
                    "entity_count": len(final_entities)
                },
                provenance=ProvenanceRecord(
                    operation="entity_extraction",
                    tool_id=self.tool_id,
                    inputs={"text": text[:100] + "..."},
                    outputs={"entity_count": len(final_entities)}
                )
            )
            
        except Exception as e:
            return ToolResult(
                status="error",
                data={},
                confidence=AdvancedConfidenceScore(value=0.0),
                metadata={"error": str(e)},
                provenance=ProvenanceRecord(
                    operation="entity_extraction_failed",
                    tool_id=self.tool_id,
                    error=str(e)
                )
            )
    
    async def _enhance_with_theory(self,
                                  entities: List[Dict],
                                  text: str,
                                  theories: List[TheorySchema]) -> List[Dict]:
        """
        Enhance entities with theory grounding
        
        Example:
        Base entity: {"text": "social capital", "type": "CONCEPT"}
        Enhanced: {
            "text": "social capital",
            "type": "THEORETICAL_CONSTRUCT",
            "theory_grounding": {
                "theory": "putnam_social_capital",
                "construct_id": "social_capital",
                "dimensions": ["bonding", "bridging"],
                "measurement_hints": ["trust", "reciprocity", "networks"]
            }
        }
        """
        enhanced = []
        
        for entity in entities:
            # Try to ground in each theory
            groundings = []
            for theory in theories:
                grounding = await self.theory_matcher.ground_entity(
                    entity_text=entity["text"],
                    entity_context=text[
                        max(0, entity["start"]-100):
                        min(len(text), entity["end"]+100)
                    ],
                    theory=theory
                )
                if grounding.confidence > 0.5:
                    groundings.append(grounding)
            
            if groundings:
                # Use best grounding
                best_grounding = max(groundings, key=lambda g: g.confidence)
                entity["theory_grounding"] = best_grounding.to_dict()
                entity["type"] = f"THEORETICAL_{entity['type']}"
            
            enhanced.append(entity)
        
        return enhanced
```

## Performance Optimization Patterns

### Async Processing Pattern

```python
class AsyncBatchProcessor:
    """Efficient batch processing with concurrency control"""
    
    def __init__(self, max_concurrency: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.results_queue = asyncio.Queue()
        
    async def process_batch(self, 
                          items: List[Any],
                          processor: Callable,
                          batch_size: int = 100) -> List[Any]:
        """
        Process items in batches with controlled concurrency
        
        Features:
        1. Automatic batching
        2. Concurrency limiting
        3. Progress tracking
        4. Error isolation
        """
        batches = [
            items[i:i + batch_size] 
            for i in range(0, len(items), batch_size)
        ]
        
        tasks = []
        for batch_idx, batch in enumerate(batches):
            task = self._process_batch_with_progress(
                batch, 
                processor,
                batch_idx,
                len(batches)
            )
            tasks.append(task)
        
        # Process all batches
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        errors = []
        
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                errors.append(batch_result)
            else:
                all_results.extend(batch_result)
        
        if errors:
            # Log errors but don't fail entire batch
            for error in errors:
                logger.error(f"Batch processing error: {error}")
        
        return all_results
    
    async def _process_batch_with_progress(self,
                                         batch: List[Any],
                                         processor: Callable,
                                         batch_idx: int,
                                         total_batches: int) -> List[Any]:
        """Process single batch with semaphore control"""
        async with self.semaphore:
            results = []
            
            for idx, item in enumerate(batch):
                try:
                    result = await processor(item)
                    results.append(result)
                    
                    # Report progress
                    progress = (batch_idx * len(batch) + idx + 1) / (total_batches * len(batch))
                    await self.results_queue.put({
                        "type": "progress",
                        "value": progress
                    })
                    
                except Exception as e:
                    # Isolated error handling
                    results.append(ProcessingError(item=item, error=e))
                    await self.results_queue.put({
                        "type": "error",
                        "item": item,
                        "error": str(e)
                    })
            
            return results
```

### Caching Strategy

```python
class IntelligentCache:
    """Multi-level caching with TTL and LRU eviction"""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 disk_cache_size: int = 10000):
        self.memory_cache = LRUCache(maxsize=memory_cache_size)
        self.disk_cache = DiskCache(max_size=disk_cache_size)
        self.stats = CacheStats()
        
    async def get_or_compute(self,
                           key: str,
                           compute_func: Callable,
                           ttl: int = 3600) -> Any:
        """
        Get from cache or compute with fallback
        
        Cache hierarchy:
        1. Memory cache (fastest)
        2. Disk cache (fast)
        3. Compute (slow)
        """
        # Check memory cache
        result = self.memory_cache.get(key)
        if result is not None:
            self.stats.memory_hits += 1
            return result
        
        # Check disk cache
        result = await self.disk_cache.get(key)
        if result is not None:
            self.stats.disk_hits += 1
            # Promote to memory cache
            self.memory_cache.put(key, result, ttl)
            return result
        
        # Compute and cache
        self.stats.misses += 1
        result = await compute_func()
        
        # Store in both caches
        self.memory_cache.put(key, result, ttl)
        await self.disk_cache.put(key, result, ttl * 10)  # Longer TTL for disk
        
        return result
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        # Memory cache invalidation
        keys_to_remove = [
            k for k in self.memory_cache.keys()
            if fnmatch(k, pattern)
        ]
        for key in keys_to_remove:
            self.memory_cache.invalidate(key)
        
        # Disk cache invalidation
        self.disk_cache.invalidate_pattern(pattern)
```

## Summary

This detailed component architecture provides:

1. **Complete interface specifications** for all major components
2. **Detailed algorithms** with complexity analysis
3. **Concrete pseudo-code** examples
4. **Data structure definitions**
5. **Error handling patterns**
6. **Performance optimization strategies**

Each component is designed to:
- Support the cross-modal analysis vision
- Integrate with theory frameworks
- Propagate uncertainty properly
- Maintain complete provenance
- Scale within single-node constraints

The architecture enables the ambitious KGAS vision while maintaining practical implementability through clear specifications and modular design.

================================================================================

## 9. bi-store-justification.md

**Source**: `docs/architecture/data/bi-store-justification.md`

---

# Bi-Store Architecture Justification

## Overview

KGAS employs a bi-store architecture with Neo4j and SQLite, each optimized for different analytical modalities required in academic social science research.

## ⚠️ CRITICAL RELIABILITY ISSUE

**IDENTIFIED**: Bi-store operations lack distributed transaction consistency, creating risk of data corruption where Neo4j entities are created but SQLite identity tracking fails, leaving orphaned graph nodes.

**STATUS**: Phase RELIABILITY Issue C2 - requires distributed transaction implementation across both stores.

**IMPACT**: Current implementation unsuitable for production use until transaction consistency is implemented.

## Architectural Decision

### Neo4j (Graph + Vector Store)
**Purpose**: Graph-native operations and vector similarity search

**Optimized for**:
- Network analysis (centrality, community detection, pathfinding)
- Relationship traversal and pattern matching
- Vector similarity search (using native HNSW index)
- Graph-based machine learning features

**Example Operations**:
```cypher
-- Find influential entities
MATCH (n:Entity)
RETURN n.name, n.pagerank_score
ORDER BY n.pagerank_score DESC

-- Vector similarity search
MATCH (n:Entity)
WHERE n.embedding IS NOT NULL
WITH n, vector.similarity.cosine(n.embedding, $query_vector) AS similarity
RETURN n, similarity
ORDER BY similarity DESC
```

### SQLite (Relational Store)
**Purpose**: Statistical analysis and structured data operations

**Optimized for**:
- Statistical analysis (regression, correlation, hypothesis testing)
- Structured Equation Modeling (SEM)
- Time series analysis
- Tabular data export for R/SPSS/Stata
- Complex aggregations and pivot operations
- Workflow metadata and provenance tracking

**Example Operations**:
```sql
-- Correlation analysis preparation
SELECT 
    e1.pagerank_score,
    e1.betweenness_centrality,
    COUNT(r.id) as relationship_count,
    AVG(r.weight) as avg_relationship_strength
FROM entities e1
LEFT JOIN relationships r ON e1.id = r.source_id
GROUP BY e1.id;

-- SEM data preparation
CREATE VIEW sem_data AS
SELECT 
    e.id,
    e.community_id,
    e.pagerank_score as influence,
    e.clustering_coefficient as cohesion,
    COUNT(DISTINCT r.target_id) as out_degree
FROM entities e
LEFT JOIN relationships r ON e.id = r.source_id
GROUP BY e.id;
```

## Why Not Single Store?

### Graph Databases (Neo4j alone)
- **Limitation**: Not optimized for statistical operations
- **Challenge**: Difficult to export to statistical software
- **Missing**: Native support for complex aggregations needed in social science

### Relational Databases (PostgreSQL/SQLite alone)
- **Limitation**: Recursive queries for graph algorithms are inefficient
- **Challenge**: No native vector similarity search
- **Missing**: Natural graph traversal operations

### Document Stores (MongoDB alone)
- **Limitation**: Neither graph-native nor optimized for statistics
- **Challenge**: Complex joins for relationship analysis
- **Missing**: ACID guarantees for research reproducibility

## Cross-Modal Synchronization

The bi-store architecture enables synchronized views:

```python
class CrossModalSync:
    def sync_graph_to_table(self, graph_metrics: Dict):
        """Sync graph analysis results to relational tables"""
        # Store graph metrics in SQLite for statistical analysis
        self.sqlite.execute("""
            INSERT INTO entity_metrics 
            (entity_id, pagerank, betweenness, community_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, graph_metrics)
    
    def sync_table_to_graph(self, statistical_results: Dict):
        """Sync statistical results back to graph"""
        # Update graph with statistical findings
        self.neo4j.query("""
            MATCH (n:Entity {id: $entity_id})
            SET n.regression_coefficient = $coefficient,
                n.significance = $p_value
        """, statistical_results)
```

## Research Workflow Integration

### Example: Mixed Methods Analysis
1. **Graph Analysis** (Neo4j): Identify influential actors and communities
2. **Export to Table** (SQLite): Prepare data for statistical analysis
3. **Statistical Analysis** (SQLite/R): Run regression, SEM, or other tests
4. **Integrate Results** (Both): Update graph with statistical findings
5. **Vector Search** (Neo4j): Find similar patterns in other datasets

This bi-store approach provides the **best tool for each job** while maintaining **data coherence** and **analytical flexibility** required for sophisticated social science research.

================================================================================

## 10. SPECIFICATIONS.md

**Source**: `docs/architecture/specifications/SPECIFICATIONS.md`

---

---
status: living
---

# GraphRAG System Specifications

## 🎯 System Overview

The GraphRAG system is a comprehensive document processing and graph analysis platform. This document specifies the currently implemented and verifiable components of the system. For future plans, see the [Project Roadmap](../planning/ROADMAP.md).

## 📊 Capabilities & Tools Overview

### **Terminology Definitions**
- **Capability**: Any class, function, or method in the codebase.
- **Core Tool**: An integrated, active workflow component used internally.
- **MCP Tool**: A tool exposed for external use via the MCP server protocol.

### **System Capabilities**
The system's capabilities are organized into phases, detailed below.

### **MCP Tool Access**
A subset of tools are exposed via the MCP server for external integration, primarily for interacting with core services and Phase 1 (Ingestion) and Phase 3 (Construction) workflows.

## Tool Organization by Phase

The following tools are actively implemented and integrated into the system.

### Phase 1: Ingestion Tools (T01-T12)
*Get data from various sources into the system.*
- **T01:** PDF Document Loader
- **T02:** Word Document Loader
- **T03:** HTML Document Loader
- **T04:** Markdown Document Loader
- **T05:** CSV Data Loader
- **T06:** JSON Data Loader
- **T07:** Excel Data Loader
- **T08:** REST API Connector
- **T09:** GraphQL API Connector
- **T10:** SQL Database Connector
- **T11:** NoSQL Database Connector
- **T12:** Stream Processor

### Phase 2: Processing Tools (T13-T30)
*Clean, normalize, and extract information from raw data.*
- **T13:** Text Cleaner
- **T14:** Text Normalizer
- **T15:** Semantic Chunker
- **T16:** Sliding Window Chunker
- **T17:** Language Detector
- **T18:** Text Translator
- **T19:** Subword Tokenizer
- **T20:** Sentence Tokenizer
- **T21:** Text Statistics Calculator
- **T22:** Text Quality Assessor
- **T23:** Entity Recognizer
- **T24:** Custom Entity Recognizer
- **T25:** Coreference Resolver
- **T26:** Entity Linker
- **T27:** Relationship Extractor
- **T28:** Keyword Extractor
- **T29:** Text Disambiguation
- **T30:** PII Redactor

### Phase 3: Construction Tools (T31-T48)
*Build graph structures and create embeddings.*
- **T31:** Document to Graph Transformer
- **T32:** Node Creator
- **T33:** Edge Creator
- **T34:** Graph Merger
- **T35:** Text to Vector Embedder
- **T36:** Graph to Vector Embedder
- **T37:** Ontology Mapper
- **T38:** Schema Validator
- **T39:** Community Detector
- **T40:** Graph Partitioner
- **T41:** Graph Simplifier
- **T42:** Centrality Calculator
- **T43:** Path Finder
- **T44:** Graph Diff Tool
- **T45:** Graph Visualizer
- **T46:** Graph Exporter
- **T47:** Graph Importer
- **T48:** Graph Snapshot Manager
 
---

## Tool Details

*This section would contain the detailed parameters for each implemented tool, as was previously the case. The content is omitted here for brevity but the structure remains.*

---

## Phase 1: Ingestion Tools (T01-T12)

### T01: PDF Document Loader
Extract text and metadata from PDF files
- `file_path`: string - Path to PDF file
- `extract_images`: boolean (default: false)
- `extract_tables`: boolean (default: true)

### T02: Word Document Loader
Extract text and metadata from Word documents
- `file_path`: string - Path to .docx/.doc file
- `preserve_formatting`: boolean (default: false)

### T03: HTML Document Loader
Parse and extract text from HTML/web pages
- `url_or_path`: string - URL or local file path
- `remove_scripts`: boolean (default: true)
- `extract_links`: boolean (default: true)

### T04: Markdown Document Loader
Parse Markdown files preserving structure
- `file_path`: string - Path to .md file
- `extract_code_blocks`: boolean (default: true)

### T05: CSV Data Loader
Load tabular data from CSV files
- `file_path`: string - Path to CSV file
- `delimiter`: string (default: ",")
- `has_header`: boolean (default: true)

### T06: JSON Data Loader
Load structured data from JSON files
- `file_path`: string - Path to JSON file
- `json_path`: string (optional) - JSONPath expression

### T07: Excel Data Loader
Load data from Excel files with sheet support
- `file_path`: string - Path to .xlsx/.xls file
- `sheet_name`: string (optional) - Specific sheet
- `header_row`: integer (default: 0)

### T08: REST API Connector
Fetch data from REST APIs
- `endpoint`: string - API endpoint URL
- `method`: string (default: "GET")
- `headers`: dict (optional)
- `auth`: dict (optional)
- `pagination`: dict (optional)

### T09: GraphQL API Connector
Execute GraphQL queries
- `endpoint`: string - GraphQL endpoint
- `query`: string - GraphQL query
- `variables`: dict (optional)

### T10: SQL Database Connector
Execute SQL queries on relational databases
- `connection_string`: string - Database connection
- `query`: string - SQL query
- `params`: list (optional) - Query parameters

### T11: NoSQL Database Connector
Query NoSQL databases (MongoDB, etc.)
- `connection_string`: string - Database connection
- `collection`: string - Collection name
- `query`: dict - Query document

### T12: Stream Processor
Process real-time data streams
- `stream_config`: dict - Stream configuration
- `batch_size`: integer (default: 100)
- `timeout`: float (default: 60.0)

---

## Phase 2: Processing Tools (T13-T30)

### T13: Text Cleaner
Remove noise and normalize text
- `text`: string - Input text
- `remove_html`: boolean (default: true)
- `remove_urls`: boolean (default: true)
- `remove_emails`: boolean (default: true)
- `lowercase`: boolean (default: false)

### T14: Text Normalizer
Standardize text format
- `text`: string - Input text
- `expand_contractions`: boolean (default: true)
- `remove_accents`: boolean (default: true)
- `standardize_quotes`: boolean (default: true)

### T15: Semantic Chunker
Split text into semantic chunks
- `text`: string - Input text
- `chunk_size`: integer (default: 512)
- `overlap`: integer (default: 50)
- `method`: string (default: "semantic")

### T16: Sliding Window Chunker
Create overlapping text windows
- `text`: string - Input text
- `window_size`: integer (default: 256)
- `step_size`: integer (default: 128)

### T17: Language Detector
Identify text language
- `text`: string - Input text
- `return_confidence`: boolean (default: true)

### T18: Text Translator
Translate text between languages
- `text`: string - Input text
- `source_lang`: string (optional)
- `target_lang`: string - Target language

### T19: Subword Tokenizer
Tokenize text into subwords
- `text`: string - Input text
- `model`: string (default: "bert-base-uncased")

### T20: Sentence Tokenizer
Split text into sentences
- `text`: string - Input text
- `language`: string (default: "en")

### T21: Text Statistics Calculator
Compute text statistics (word count, readability)
- `text`: string - Input text

### T22: Text Quality Assessor
Assess text quality and coherence
- `text`: string - Input text
- `check_grammar`: boolean (default: true)
- `check_coherence`: boolean (default: true)

### T23: Entity Recognizer
Extract named entities (see variants T23a/T23b above)
- `text`: string OR `chunk_refs`: list - Input text or chunk references
- `model`: string (default: "en_core_web_sm") - For T23a
- `entity_types`: list - Types to extract
- `create_mentions`: boolean (default: true) - Create mention objects
- `confidence_threshold`: float (default: 0.7)

### T24: Custom Entity Recognizer
Extract domain-specific entities
- `text`: string - Input text
- `entity_patterns`: dict - Custom patterns
- `use_llm`: boolean (default: false)

### T25: Coreference Resolver
Resolve pronouns to entities
- `text`: string - Input text
- `entities`: list - Previously extracted entities

### T26: Entity Linker
Link entities to knowledge base
- `entities`: list - Extracted entities
- `knowledge_base`: string - KB identifier

### T27: Relationship Extractor
Extract relationships between entities (often combined with T23b)
- `text`: string OR `chunk_refs`: list - Input text or chunks
- `entity_refs`: list - Previously extracted entities
- `patterns`: dict - Relationship patterns (for rule-based)
- `model`: string - Model name (for ML-based)
- `extract_with_entities`: boolean - Extract entities and relationships together

### T28: Entity Confidence Scorer
Assess and assign confidence scores to extracted entities
- `entity_refs`: list - References to entities to score
- `context_refs`: list - Context chunks for scoring
- `scoring_method`: string - "frequency", "coherence", "external_kb"
- `boost_factors`: dict - Factors to boost confidence
- `penalty_factors`: dict - Factors to reduce confidence

### T29: Entity Disambiguator
Resolve entity ambiguity
- `entity`: dict - Entity to disambiguate
- `context`: string - Surrounding context
- `candidates`: list - Possible resolutions

### T30: Entity Normalizer
Standardize entity names
- `entities`: list - Entities to normalize
- `normalization_rules`: dict - Rules

---

## Phase 3: Construction Tools (T31-T48)

### T31: Entity Node Builder
Create entity nodes for graph
- `entities`: list - Extracted entities
- `properties`: dict - Additional properties

### T32: Chunk Node Builder
Create chunk nodes for graph
- `chunks`: list - Text chunks
- `document_id`: string - Parent document

### T33: Document Node Builder
Create document nodes
- `document`: dict - Document metadata
- `properties`: dict - Additional properties

### T34: Relationship Edge Builder
Create relationship edges
- `relationships`: list - Extracted relationships
- `edge_properties`: dict - Additional properties

### T35: Reference Edge Builder
Create reference edges (chunk-entity, etc.)
- `source_nodes`: list - Source nodes
- `target_nodes`: list - Target nodes
- `reference_type`: string

### T36: Graph Merger
Merge multiple graphs
- `graphs`: list - Graphs to merge
- `merge_strategy`: string (default: "union")

### T37: Graph Deduplicator
Remove duplicate nodes/edges
- `graph`: networkx.Graph
- `similarity_threshold`: float (default: 0.9)

### T38: Schema Validator
Validate graph against schema
- `graph`: networkx.Graph
- `schema`: dict - Graph schema definition

### T39: Type Manager
Manage node/edge types
- `graph`: networkx.Graph
- `type_hierarchy`: dict - Type definitions

### T40: Graph Version Controller
Track graph versions
- `graph`: networkx.Graph
- `version_id`: string
- `parent_version`: string (optional)

### T41: Sentence Embedder
Generate sentence embeddings
- `sentences`: list - Input sentences
- `model`: string (default: "all-MiniLM-L6-v2")

### T42: Document Embedder
Generate document embeddings
- `documents`: list - Input documents
- `model`: string (default: "all-mpnet-base-v2")

### T43: Node2Vec Embedder
Generate graph node embeddings
- `graph`: networkx.Graph
- `dimensions`: integer (default: 128)
- `walk_length`: integer (default: 80)

### T44: GraphSAGE Embedder
Generate inductive node embeddings
- `graph`: networkx.Graph
- `features`: array - Node features
- `dimensions`: integer (default: 128)

### T45: Neo4j Vector Indexer
Build Neo4j HNSW vector index
- `embeddings`: array - Vector embeddings
- `collection_name`: string - Collection identifier

### T46: Annoy Vector Indexer
Build Annoy vector index
- `embeddings`: array - Vector embeddings
- `n_trees`: integer (default: 10)

### T47: Similarity Calculator
Calculate vector similarities
- `vectors1`: array - First set of vectors
- `vectors2`: array - Second set of vectors
- `metric`: string (default: "cosine")

### T48: Vector Aggregator
Aggregate multiple vectors
- `vectors`: list - Vectors to aggregate
- `method`: string (default: "mean")

---

## Phase 4: Retrieval Tools (T49-T67) - Core GraphRAG Operators

### T49: Entity VDB Search
Vector search for entities
- `query`: string - Search query
- `top_k`: integer (default: 10)
- `threshold`: float (optional)

### T50: Entity RelNode Extract
Extract entities from relationships
- `relationships`: list - Relationship IDs
- `direction`: string (default: "both")

### T51: Entity PPR Rank
Personalized PageRank for entities
- `seed_entities`: list - Starting entities
- `damping_factor`: float (default: 0.85)
- `top_k`: integer (default: 10)

### T52: Entity Agent Find
LLM-based entity finding
- `query`: string - User query
- `context`: string - Graph context

### T53: Entity Onehop Neighbors
Get one-hop neighbors
- `entities`: list - Source entities
- `edge_types`: list (optional)

### T54: Entity Link
Find entity connections
- `entity1`: string - First entity
- `entity2`: string - Second entity

### T55: Entity TF-IDF
TF-IDF ranking for entities
- `query`: string - Search terms
- `entity_texts`: dict - Entity descriptions

### T56: Relationship VDB Search
Vector search for relationships
- `query`: string - Search query
- `top_k`: integer (default: 10)

### T57: Relationship Onehop
One-hop relationship traversal
- `relationships`: list - Source relationships

### T58: Relationship Aggregator
Aggregate relationship information
- `relationships`: list - Relationships to aggregate
- `method`: string - Aggregation method

### T59: Relationship Agent
LLM-based relationship analysis
- `query`: string - Analysis query
- `relationships`: list - Relationships to analyze

### T60: Chunk Aggregator
Aggregate chunk scores
- `chunks`: list - Chunks with scores
- `weights`: dict - Score weights

### T61: Chunk FromRel
Get chunks from relationships
- `relationships`: list - Source relationships

### T62: Chunk Occurrence
Find chunk occurrences
- `pattern`: string - Search pattern
- `chunks`: list - Chunks to search

### T63: Subgraph KhopPath
K-hop path extraction
- `start_nodes`: list - Starting nodes
- `k`: integer - Number of hops

### T64: Subgraph Steiner
Steiner tree extraction
- `terminal_nodes`: list - Nodes to connect

### T65: Subgraph AgentPath
LLM-guided path finding
- `query`: string - Path query
- `graph_context`: dict

### T66: Community Entity
Community-based entity retrieval
- `community_id`: string

### T67: Community Layer
Hierarchical community analysis
- `level`: integer - Hierarchy level

---

## Phase 5: Analysis Tools (T68-T75)

### T68: Betweenness Centrality
Calculate betweenness centrality
- `graph`: networkx.Graph
- `normalized`: boolean (default: true)

### T69: Closeness Centrality
Calculate closeness centrality
- `graph`: networkx.Graph
- `distance_metric`: string (default: "shortest_path")

### T70: Shortest Path Finder
Find shortest paths
- `graph`: networkx.Graph
- `source`: string - Source node
- `target`: string - Target node

### T71: All Paths Finder
Find all paths between nodes
- `graph`: networkx.Graph
- `source`: string - Source node
- `target`: string - Target node
- `max_length`: integer (optional)

### T72: Max Flow Calculator
Calculate maximum flow
- `graph`: networkx.Graph
- `source`: string - Source node
- `sink`: string - Sink node

### T73: Min Cut Finder
Find minimum cut
- `graph`: networkx.Graph
- `source`: string - Source node
- `sink`: string - Sink node

### T74: Spectral Clustering
Spectral graph clustering
- `graph`: networkx.Graph
- `n_clusters`: integer

### T75: Hierarchical Clustering
Hierarchical graph clustering
- `graph`: networkx.Graph
- `method`: string (default: "ward")

---

## Phase 6: Storage Tools (T76-T81)

### T76: Neo4j Manager
Neo4j CRUD operations
- `operation`: string - create/read/update/delete
- `query`: string - Cypher query
- `params`: dict - Query parameters

### T77: SQLite Manager
SQLite metadata operations
- `operation`: string - Operation type
- `table`: string - Table name
- `data`: dict - Data to operate on

### T78: Vector Index Manager
Neo4j vector index management operations
- `operation`: string - add/search/save/load
- `collection`: string - Collection name
- `vectors`: array (optional)

### T79: Backup System
Backup all data stores
- `backup_path`: string - Backup destination
- `components`: list - Components to backup

### T80: Data Migrator
Migrate data between versions
- `source_version`: string
- `target_version`: string
- `migration_script`: string

### T81: Cache Manager
Manage computation cache
- `operation`: string - get/set/clear
- `key`: string - Cache key
- `value`: any (optional)

---

## Phase 7: Interface Tools (T82-T106)

### T82: Natural Language Parser
Parse user queries
- `query`: string - User query
- `context`: dict (optional)

### T83: Query Planner
Plan query execution
- `parsed_query`: dict
- `available_tools`: list

### T84: Query Optimizer
Optimize query execution
- `execution_plan`: dict
- `statistics`: dict

### T85: Query Result Ranker
Rank query results
- `results`: list
- `ranking_criteria`: dict

### T86: Multi-Query Aggregator
Aggregate multiple query results
- `query_results`: list
- `aggregation_method`: string

### T87: Query History Analyzer
Analyze query patterns
- `query_history`: list
- `analysis_type`: string

### T88: Feedback Processor
Process user feedback
- `feedback`: dict
- `query_id`: string

### T89: Context Assembler
Assemble context for response
- `retrieved_data`: dict
- `query`: string

### T90: Response Generator
Generate natural language response
- `context`: string
- `query`: string
- `model`: string (default: "gpt-4")

### T91: Citation Manager
Manage response citations
- `response`: string
- `sources`: list

### T92: Result Synthesizer
Synthesize multiple results
- `results`: list
- `synthesis_method`: string

### T93: CLI Table Formatter
Format results as CLI tables
- `data`: list/dict
- `format`: string (default: "grid")

### T94: Export Formatter
Export results in various formats
- `data`: any
- `format`: string - json/csv/yaml

### T95: Summary Generator
Generate result summaries
- `results`: dict
- `summary_length`: integer

### T96: Confidence Scorer
Score result confidence
- `results`: dict
- `scoring_method`: string

### T97: SQL Generator
Generate SQL from natural language
- `query`: string - Natural language query
- `schema`: dict - Database schema

### T98: Table QA
Answer questions about tables
- `question`: string
- `table`: pandas.DataFrame

### T99: SQL-to-Graph Linker
Link SQL results to graph entities
- `sql_results`: list
- `graph_entities`: list

### T100: Schema Analyzer
Analyze database schemas
- `connection`: string
- `include_stats`: boolean (default: true)

### T101: Performance Monitor
Monitor query performance
- `query_id`: string
- `metrics`: dict

### T102: Alert Manager
Manage performance alerts
- `alert_rules`: dict
- `current_metrics`: dict

### T103: Metrics Reporter
Generate metrics reports
- `time_range`: tuple
- `report_type`: string

### T104: Provenance Tracker
Track data provenance
- `operation`: dict
- `inputs`: list
- `outputs`: list

### T105: Lineage Query
Query data lineage
- `entity_id`: string
- `direction`: string (default: "both")

### T106: Meta-Graph Explorer
Explore transformation history
- `query`: string
- `time_range`: tuple (optional)

---

## Key Integration Points

### Data Flow
1. **Ingestion → Processing**: Raw data becomes cleaned text
2. **Processing → Construction**: Entities/relations become graph nodes/edges
3. **Construction → Retrieval**: Built graphs become searchable indices
4. **Retrieval → Analysis**: Subgraphs produce insights
5. **Analysis → Interface**: Results become formatted responses
6. **All → Storage**: Persistent state management throughout

### Critical Dependencies
- Embedding consistency between T41-T42 and T45-T46
- Entity resolution output (T29-T30) must match input format for T31
- Graph schema validation (T38-T39) applies to all node/edge builders
- Query planner (T83) must understand all tool capabilities
- Performance monitoring (T101-T103) tracks all phases

### Storage Architecture
- **Neo4j**: Primary graph database (entities, relationships, communities)
- **SQLite**: Metadata storage (documents, configuration)
- **Neo4j Vector Index**: Native vector search within Neo4j (replaces external vector DB)
- **Cache**: Computation results (Redis/DiskCache)

### Key Architectural Patterns

#### Three-Level Identity System
All text processing follows: Surface Form → Mention → Entity
- **Surface**: Text as it appears ("Apple", "AAPL")
- **Mention**: Specific occurrence with context
- **Entity**: Resolved canonical entity

#### Reference-Based Architecture
Tools pass references, not full data objects:
```python
{"entity_refs": ["ent_001", ...], "count": 1000, "sample": [...]}
```

#### Universal Quality Tracking
Every data object includes:
- `confidence`: float (0.0-1.0)
- `quality_tier`: "high" | "medium" | "low"
- `warnings`: list of issues
- `evidence`: supporting data

#### Format Agnostic Processing
Same data can be Graph, Table, or Vector based on analysis needs:
- Use T115 for Graph → Table conversion
- Use T116 for Table → Graph conversion
- Use T117 for automatic format selection

---

## Phase 8: Core Services and Infrastructure (T107-T121)

Critical services identified through mock workflow analysis that support all other tools.

### T107: Identity Service
Manage three-level identity system (Surface → Mention → Entity)
- `operation`: string - "create_mention", "resolve_mention", "create_entity", "merge_entities"
- `surface_text`: string - Text as it appears
- `context`: dict - Document ID, position, surrounding text
- `entity_candidates`: list - Possible entity resolutions with confidence

### T108: Version Service
Handle four-level versioning (schema, data, graph, analysis)
- `operation`: string - "create_version", "get_version", "diff_versions", "rollback"
- `object_type`: string - "schema", "data", "graph", "analysis"
- `object_id`: string - ID of object to version
- `metadata`: dict - Version metadata

### T109: Entity Normalizer
Normalize entity variations to canonical forms
- `entity_name`: string - Name to normalize
- `entity_type`: string - Type for context
- `normalization_rules`: dict - Custom rules (optional)
- `case_sensitive`: boolean (default: false)

### T110: Provenance Service
Track complete operation lineage
- `operation`: string - "record", "trace_lineage", "find_affected"
- `tool_id`: string - Tool that performed operation
- `inputs`: list - Input references
- `outputs`: list - Output references
- `parameters`: dict - Operation parameters

### T111: Quality Service
Assess and propagate confidence scores
- `operation`: string - "assess", "propagate", "aggregate"
- `object`: dict - Object to assess
- `upstream_scores`: list - Previous confidence scores
- `method`: string - Assessment method

### T112: Constraint Engine
Manage and check data constraints
- `operation`: string - "register", "check", "find_violations"
- `constraints`: dict - Constraint definitions
- `data`: dict - Data to validate
- `mode`: string - "strict" or "soft" matching

### T113: Ontology Manager
Define and enforce graph ontologies
- `operation`: string - "create", "update", "validate", "query"
- `ontology`: dict - Ontology definition
- `mode`: string - "strict", "extensible", "ad_hoc"
- `domain_range`: dict - Property constraints

### T114: Provenance Tracker
Enhanced provenance with impact analysis
- `entity_id`: string - Entity to track
- `include_derivatives`: boolean - Track downstream impacts
- `time_range`: tuple - Historical range
- `confidence_threshold`: float - Minimum confidence

### T115: Graph to Table Converter
Convert graph data to tabular format for statistical analysis
- `entity_refs`: list - Entities to include
- `relationship_refs`: list - Relationships to include
- `output_format`: string - "wide", "long", "edge_list"
- `aggregations`: dict - How to aggregate relationships

### T116: Table to Graph Builder
Build graph from tabular data
- `table_ref`: string - Reference to table
- `source_column`: string - Column for source nodes
- `target_column`: string - Column for target nodes
- `relationship_type`: string - Type of relationship to create
- `attribute_columns`: list - Additional columns as properties

### T117: Format Auto-Selector
Intelligently select optimal data format for analysis
- `analysis_type`: string - Type of analysis planned
- `data_characteristics`: dict - Data properties
- `constraints`: dict - Memory, time constraints
- `return_rationale`: boolean - Explain format choice

### T118: Temporal Reasoner
Handle temporal logic and paradoxes
- `temporal_data`: dict - Time-stamped facts
- `query`: string - Temporal query
- `resolve_paradoxes`: boolean - Attempt resolution
- `timeline_mode`: string - "single", "multi", "branching"

### T119: Semantic Evolution Tracker
Track meaning changes over time
- `concept`: string - Concept to track
- `time_range`: tuple - Period to analyze
- `sources`: list - Document sources
- `include_context`: boolean - Include usage context

### T120: Uncertainty Propagation Service
Propagate uncertainty through analysis chains
- `confidence_scores`: list - Input confidences
- `operations`: list - Operations performed
- `method`: string - "monte_carlo", "gaussian", "min_max"
- `return_distribution`: boolean - Full distribution vs point estimate

### T121: Workflow State Service
Manage workflow state for crash recovery and reproducibility
- `operation`: string - "checkpoint", "restore", "list_checkpoints", "clean_old"
- `workflow_id`: string - Unique workflow identifier
- `state_data`: dict - Lightweight references to current state (for checkpoint)
- `checkpoint_id`: string - Specific checkpoint (for restore)
- `include_intermediates`: boolean (default: false) - Include intermediate results
- `compression`: string (default: "gzip") - Compression method for state data

---

## Tool Contracts

Every tool declares a contract specifying its requirements and guarantees. This enables intelligent tool selection and workflow planning.

### Contract Structure

Each tool contract includes:

```python
{
    "tool_id": "T23b",
    "name": "LLM Entity/Relationship Extractor",
    
    # What the tool needs to function
    "required_attributes": {
        "chunk": ["content", "document_ref", "position"],
        "document": ["language"]  # Optional: specific attributes needed
    },
    
    # State requirements (what must be true before running)
    "required_state": {
        "chunks_created": true,
        "language_detected": true,
        "entities_resolved": false  # Can work with unresolved entities
    },
    
    # What the tool produces
    "produced_attributes": {
        "mention": ["surface_text", "position", "entity_candidates"],
        "relationship": ["source_id", "target_id", "type", "confidence"]
    },
    
    # State changes after running
    "state_changes": {
        "entities_extracted": true,
        "relationships_extracted": true
    },
    
    # Error handling
    "error_codes": {
        "E001": "Missing required chunk content",
        "E002": "Language not supported",
        "E003": "LLM API failure",
        "E004": "Confidence below threshold"
    },
    
    # Performance characteristics
    "performance": {
        "time_complexity": "O(n)",  # n = text length
        "memory_usage": "streaming",
        "can_parallelize": true,
        "supports_partial": true
    }
}
```

### Example Tool Contracts

#### T31: Entity Node Builder
```python
{
    "tool_id": "T31",
    "required_attributes": {
        "mention": ["surface_text", "entity_candidates", "confidence"]
    },
    "required_state": {
        "mentions_created": true,
        "entities_resolved": "optional"  # Can work with or without resolution
    },
    "produced_attributes": {
        "entity": ["canonical_name", "entity_type", "mention_refs", "confidence"]
    },
    "state_changes": {
        "entities_created": true
    }
}
```

#### T115: Graph to Table Converter
```python
{
    "tool_id": "T115",
    "required_attributes": {
        "entity": ["id", "attributes"],
        "relationship": ["source_id", "target_id", "type"]
    },
    "required_state": {
        "graph_built": true
    },
    "produced_attributes": {
        "table": ["schema", "row_refs", "source_graph_ref"]
    },
    "supports_modes": ["wide", "long", "edge_list"]
}
```

### Contract Usage

Tool contracts enable:
1. **Pre-flight validation**: Check if tool can run before attempting
2. **Intelligent planning**: Select appropriate tools based on current state
3. **Error recovery**: Understand what went wrong and find alternatives
4. **Workflow optimization**: Parallelize compatible tools
5. **Domain adaptation**: Tools declare if they need entity resolution

================================================================================

## 11. ADR-001-Phase-Interface-Design.md

**Source**: `docs/architecture/adrs/ADR-001-Phase-Interface-Design.md`

---

**Doc status**: Living – auto-checked by doc-governance CI

# ADR-001: Contract-First Tool Interface Design

**Date**: 2025-01-27  
**Status**: Partially Implemented - 10 tools use legacy interfaces, 9 tools have unified interface, contract-first design remains architectural goal  
**Deciders**: Development Team  
**Context**: Tool integration failures due to incompatible interfaces

---

## 🎯 **Decision**

**Use contract-first design for all tool interfaces with theory schema integration**

All tools must implement standardized contracts with theory schema support to enable agent-orchestrated workflows and cross-modal analysis.

---

## 🚨 **Problem**

### **Current Issues**
- **API Incompatibility**: Tools have different calling signatures and return formats
- **Integration Failures**: Tools tested in isolation, breaks discovered at agent runtime
- **No Theory Integration**: Theoretical concepts defined but not consistently used in processing
- **Agent Complexity**: Agent needs complex logic to handle different tool interfaces

### **Root Cause**
- **"Build First, Integrate Later"**: Tools built independently without shared contracts
- **No Interface Standards**: Each tool evolved its own API without coordination
- **Missing Theory Awareness**: Processing pipeline doesn't consistently use theoretical foundations

---

## 💡 **Trade-off Analysis**

### Options Considered

#### Option 1: Keep Status Quo (Tool-Specific Interfaces)
- **Pros**:
  - No migration effort required
  - Tools remain independent and specialized
  - Developers familiar with existing patterns
  - Quick to add new tools without constraints
  
- **Cons**:
  - Integration complexity grows exponentially with tool count
  - Agent orchestration requires complex adapter logic
  - No consistent error handling or confidence tracking
  - Theory integration would require per-tool implementation
  - Testing each tool combination separately

#### Option 2: Retrofit with Adapters
- **Pros**:
  - Preserve existing tool implementations
  - Gradual migration possible
  - Lower initial development effort
  - Can maintain backward compatibility
  
- **Cons**:
  - Adapter layer adds performance overhead
  - Theory integration still difficult
  - Two patterns to maintain (native + adapted)
  - Technical debt accumulates
  - Doesn't solve root cause of integration issues

#### Option 3: Contract-First Design [SELECTED]
- **Pros**:
  - Clean, consistent interfaces across all tools
  - Theory integration built into contract
  - Enables intelligent agent orchestration
  - Simplified testing and validation
  - Future tools automatically compatible
  - Cross-modal analysis becomes straightforward
  
- **Cons**:
  - Significant refactoring of existing tools
  - Higher upfront design effort
  - Team learning curve for new patterns
  - Risk of over-engineering contracts

#### Option 4: Microservice Architecture
- **Pros**:
  - Tools completely decoupled
  - Independent scaling and deployment
  - Technology agnostic (tools in any language)
  - Industry-standard pattern
  
- **Cons**:
  - Massive complexity increase for research platform
  - Network overhead for local processing
  - Distributed system challenges
  - Overkill for single-user academic use case

### Decision Rationale

Contract-First Design (Option 3) was selected because:

1. **Agent Enablement**: Standardized interfaces are essential for intelligent agent orchestration of tool workflows.

2. **Theory Integration**: Built-in support for theory schemas ensures consistent application of domain knowledge.

3. **Cross-Modal Requirements**: Consistent interfaces enable seamless conversion between graph, table, and vector representations.

4. **Research Quality**: Standardized confidence scoring and provenance tracking improve research reproducibility.

5. **Long-term Maintenance**: While initial effort is higher, the reduced integration complexity pays dividends over time.

6. **Testing Efficiency**: Integration tests can validate tool combinations systematically rather than ad-hoc.

### When to Reconsider

This decision should be revisited if:
- Moving from research platform to production service
- Need to integrate external tools not under our control
- Performance overhead of contracts exceeds 10%
- Team size grows beyond 5 developers
- Requirements shift from batch to real-time processing

The contract abstraction provides flexibility to evolve the implementation while maintaining interface stability.

---

## ✅ **Selected Solution**

### **Contract-First Tool Interface**
```python
@dataclass(frozen=True)
class ToolRequest:
    """Immutable contract for ALL tool inputs"""
    input_data: Any
    theory_schema: Optional[TheorySchema] = None
    concept_library: Optional[MasterConceptLibrary] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
@dataclass(frozen=True)  
class ToolResult:
    """Immutable contract for ALL tool outputs"""
    status: Literal["success", "error"]
    data: Any
    confidence: ConfidenceScore  # From ADR-004
    metadata: Dict[str, Any]
    provenance: ProvenanceRecord

class KGASTool(ABC):
    """Contract all tools MUST implement"""
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        pass
    
    @abstractmethod
    def get_theory_compatibility(self) -> List[str]:
        """Return list of theory schema names this tool supports"""
        
    @abstractmethod 
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected input_data format"""
        
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for returned data format"""
```

### **Implementation Strategy**
1. **Phase A**: Define tool contracts and create wrappers for existing tools
2. **Phase B**: Implement theory integration and confidence scoring (ADR-004)
3. **Phase C**: Migrate tools to native contract implementation
4. **Phase D**: Enable agent orchestration and cross-modal workflows

---

## 🎯 **Consequences**

### **Positive**
- **Agent Integration**: Standardized interfaces enable intelligent agent orchestration
- **Theory Integration**: Built-in support for theory schemas and concept library
- **Cross-Modal Analysis**: Consistent interfaces enable seamless format conversion
- **Future-Proof**: New tools automatically compatible with agent workflows
- **Testing**: Integration tests can validate tool combinations
- **Confidence Tracking**: Standardized confidence scoring (ADR-004) for research quality

### **Negative**
- **Migration Effort**: Requires refactoring existing tool implementations
- **Learning Curve**: Team needs to understand contract-first approach
- **Initial Complexity**: More upfront design work required

### **Risks**
- **Scope Creep**: Contract design could become over-engineered
- **Performance**: Wrapper layers could add overhead
- **Timeline**: Contract design could delay MVRT delivery

---

## 🔧 **Implementation Plan**

### **UPDATED: Aligned with MVRT Roadmap**

### **Phase A: Tool Contracts (Days 1-3)**
- [ ] Define `ToolRequest` and `ToolResult` contracts  
- [ ] Create `KGASTool` abstract base class
- [ ] Implement `ConfidenceScore` integration (ADR-004)
- [ ] Create wrappers for existing MVRT tools (~20 tools)

### **Phase B: Agent Integration (Days 4-7)**
- [ ] Implement theory schema integration in tool contracts
- [ ] Create agent orchestration layer using standardized interfaces
- [ ] Implement cross-modal conversion using consistent tool contracts
- [ ] Create integration test framework for agent workflows

### **Phase C: Native Implementation (Days 8-14)**
- [ ] Migrate priority MVRT tools to native contract implementation
- [ ] Remove wrapper layers for performance
- [ ] Implement multi-layer UI using standardized tool interfaces
- [ ] Validate agent workflow with native tool implementations

---

## 📊 **Success Metrics**

### **Integration Success**
- [ ] All tools pass standardized integration tests
- [ ] Agent can orchestrate workflows without interface errors
- [ ] Theory schemas properly integrated into all tool processing
- [ ] Cross-modal conversions work seamlessly through tool contracts

### **Performance Impact**
- Performance targets are defined and tracked in `docs/planning/performance-targets.md`.
- The contract-first approach is not expected to introduce significant overhead.

### **Developer Experience**
- [ ] New tools can be added without integration issues
- [ ] Theory schemas can be easily integrated into any tool
- [ ] Agent can automatically discover and use new tools
- [ ] Testing framework catches integration problems early

---

## 🔄 **Review and Updates**

### **Review Schedule**
- **Week 2**: Review contract design and initial implementation
- **Week 4**: Review integration success and performance impact
- **Week 6**: Review overall success and lessons learned

### **Update Triggers**
- Performance degradation >20%
- Integration issues discovered
- Theory integration requirements change
- New phase requirements emerge

---

## Implementation Status

This ADR describes the **target tool interface design** - the intended contract-first architecture. For current tool interface implementation status and migration progress, see:

- **[Roadmap Overview](../../roadmap/ROADMAP_OVERVIEW.md)** - Current tool interface status and unified tool completion
- **[Phase TDD Progress](../../roadmap/phases/phase-tdd/tdd-implementation-progress.md)** - Active tool interface migration progress
- **[Tool Implementation Evidence](../../roadmap/phases/phase-1-implementation-evidence.md)** - Completed unified interface implementations

**Related ADRs**: None (first ADR)  
**Related Documentation**: `ARCHITECTURE_OVERVIEW.md`, `contract-system.md`

*This ADR contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*


================================================================================

## 12. ADR-002-Pipeline-Orchestrator-Architecture.md

**Source**: `docs/architecture/adrs/ADR-002-Pipeline-Orchestrator-Architecture.md`

---

**Doc status**: Living – auto-checked by doc-governance CI

# ADR-002: PipelineOrchestrator Architecture

## Status
**ACCEPTED** - Implemented 2025-01-15

## Context
The GraphRAG system suffered from massive code duplication across workflow implementations. Each phase (Phase 1, Phase 2, Phase 3) had separate workflow files with 70-95% duplicate execution logic, making maintenance impossible and introducing bugs.

### Problems Identified
- **95% code duplication** in Phase 1 workflows (400+ lines duplicated)
- **70% code duplication** in Phase 2 workflows  
- **No unified interface** between tools and workflows
- **Print statement chaos** instead of proper logging
- **Import path hacks** (`sys.path.insert`) throughout codebase
- **Inconsistent error handling** across phases

### Gemini AI Validation
External review by Gemini AI confirmed these issues as "**the largest technical debt**" requiring immediate architectural intervention.

## Decision
Implement a unified **PipelineOrchestrator** architecture with the following components:

### 1. Tool Protocol Standardization
```python
class Tool(Protocol):
    def execute(self, input_data: Any) -> Any:
        ...
```

### 2. Tool Adapter Pattern
- `PDFLoaderAdapter`, `TextChunkerAdapter`, `SpacyNERAdapter`
- `RelationshipExtractorAdapter`, `EntityBuilderAdapter`, `EdgeBuilderAdapter`  
- `PageRankAdapter`, `MultiHopQueryAdapter`
- Bridges existing tools to unified protocol

### 3. Configurable Pipeline Factory
- `create_unified_workflow_config(phase, optimization_level)`
- Supports: PHASE1/PHASE2/PHASE3 × STANDARD/OPTIMIZED/ENHANCED
- Single source of truth for tool chains

### 4. Unified Execution Engine
- `PipelineOrchestrator.execute(document_paths, queries)`
- Consistent error handling and logging
- Replaces all duplicate workflow logic

## Consequences

### Positive
- ✅ **95% reduction** in Phase 1 workflow duplication
- ✅ **70% reduction** in Phase 2 workflow duplication  
- ✅ **Single source of truth** for all pipeline execution
- ✅ **Type-safe interfaces** between components
- ✅ **Proper logging** throughout system
- ✅ **Backward compatibility** maintained

### Negative
- Requires adapter layer for existing tools
- Initial implementation complexity
- Learning curve for new unified interface

## Implementation Evidence
```bash
# Verification commands
python -c "from src.core.pipeline_orchestrator import PipelineOrchestrator; print('✅ Available')"
python -c "from src.core.tool_adapters import PDFLoaderAdapter; print('✅ Tool adapters working')"
python -c "from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow; w=VerticalSliceWorkflow(); print(f'✅ Uses orchestrator: {hasattr(w, \"orchestrator\")}')"
```

**Results:** All verification tests pass ✅

## Alternatives Considered

### 1. Incremental Refactoring
- **Rejected:** Would not address root cause of duplication
- **Issue:** Technical debt would continue accumulating

### 2. Complete Rewrite
- **Rejected:** Too risky, would break existing functionality
- **Issue:** No backward compatibility guarantee

### 3. Plugin Architecture
- **Rejected:** Overly complex for current needs
- **Issue:** Would introduce unnecessary abstraction layers

## Related Decisions
- [ADR-002: Logging Standardization](ADR-002-Logging-Standardization.md)
- [ADR-003: Quality Gate Enforcement](ADR-003-Quality-Gate-Enforcement.md)

## References
- [CLAUDE.md Priority 2 Implementation Plan](../../CLAUDE.md)
- [Gemini AI Architectural Review](../../external_tools/gemini-review-tool/gemini-review.md)
- [Tool Factory Implementation](../../src/core/tool_factory.py)
- [Pipeline Orchestrator Implementation](../../src/core/pipeline_orchestrator.py)-e 
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>


================================================================================

## 13. ADR-003-Vector-Store-Consolidation.md

**Source**: `docs/architecture/adrs/ADR-003-Vector-Store-Consolidation.md`

---


# ADR-003: Vector Store Consolidation

**Date**: 2025-01-18  
**Status**: Accepted  
**Deciders**: Development Team, advised by external architectural review.

---

## 🎯 **Decision**

**Replace the tri-store data platform (Neo4j + SQLite + Qdrant) with a simplified bi-store architecture (Neo4j + SQLite). The native vector index within Neo4j (version 5.13+) will be used for all embedding storage and approximate nearest-neighbor (ANN) search, eliminating the need for a separate Qdrant instance.**

---

## 🚨 **Problem Context**

The previous target architecture employed three separate data stores:
1.  **Neo4j**: For graph data.
2.  **Qdrant**: For vector embeddings.
3.  **SQLite**: For the PII vault and workflow state.

This tri-store model introduced significant architectural complexity, most notably the **"Tri-Store Consistency Risk"** identified during external review. Because Neo4j is transactional (ACID-compliant) and Qdrant is not, ensuring data consistency required a complex **Transactional Outbox Pattern** with compensating transactions and a periodic reconciliation job.

This created several operational liabilities:
-   **Increased Complexity**: Required dedicated services (`OutboxService`, `ReconciliationService`) just to maintain data integrity.
-   **Eventual Consistency Latency**: The reconciliation window could lead to periods of data inconsistency (e.g., "orphan" vectors).
-   **Maintenance Overhead**: More moving parts to monitor, test, and maintain.
-   **Deployment Complexity**: Managing an additional Qdrant instance and its associated Docker configurations.

Given the project's context—a **Python-only, local, academic research platform**—this level of complexity was not justified by the benefits, especially when a simpler, more integrated solution became available.

---

## 💡 **Drivers for Change**

The primary driver is the maturation of **Neo4j's native vector search capabilities**. As of version 5.13, Neo4j includes a stable and mature HNSW (Hierarchical Navigable Small World) index that provides:
-   **High-Performance ANN Search**: Sub-second query times for millions of vectors, sufficient for this project's scale.
-   **ACID Guarantees**: Vector writes are part of the same transaction as graph writes. A transaction rollback automatically rolls back both the graph data and the vector index update.
-   **Operational Simplicity**: No separate vector database to manage.

This technical improvement directly nullifies the original reason for including Qdrant.

---

## ✅ **Selected Solution: Bi-Store Architecture**

1.  **Data Stores**:
    -   **Neo4j**: Will store both the property graph and the vector embeddings for all entities. An `HNSW` index will be created on the `embedding` property of `:Entity` nodes.
    -   **SQLite**: Will continue to be used for the encrypted PII vault and workflow state management, maintaining the bi-store architecture principle.

2.  **Vector Store Abstraction**:
    -   An abstract `VectorStore` protocol (interface) will be defined in Python.
    -   A concrete `Neo4jVectorStore` class will implement this interface using Cypher queries against the native vector index.
    -   This **Strategy Pattern** isolates the vector storage logic, making it easy to swap back to a dedicated store like Qdrant in the future if scalability demands it, without changing the application logic.

3.  **Code Removal**:
    -   The `OutboxService` and `ReconciliationService` will be deleted.
    -   All direct dependencies on the `qdrant-client` will be removed.
    -   Qdrant will be removed from all Docker compose files.

### **Consequences**

**Positive**:
-   ✅ **Architectural Simplification**: Eliminates an entire service and the complex cross-service consistency logic.
-   ✅ **Strong Consistency**: Vector and graph data are now updated atomically within the same transaction. The orphan-reference problem is eliminated.
-   ✅ **Reduced Maintenance**: Fewer code components and operational processes to manage.
-   ✅ **Future-Proof**: The `VectorStore` interface provides a clean extension point for future scalability needs.

**Negative**:
-   **Scalability Ceiling**: Neo4j's native index may not perform as well as a dedicated store like Qdrant at extremely large scales (>100M vectors). This is an acceptable trade-off for this project's scope.
-   **Single Point of Failure**: Consolidating on Neo4j means its availability is even more critical. This is managed by standard backup procedures (e.g., nightly dumps).

---

## 🔧 **Implementation Plan (High-Level)**

1.  **Upgrade Neo4j**: Ensure the environment uses Neo4j v5.13 or newer.
2.  **Create Index**: Add a `CREATE VECTOR INDEX` command to the database schema setup.
3.  **Abstract Interface**: Implement the `VectorStore` protocol and the `Neo4jVectorStore` class.
4.  **Migrate Data**: Write a one-time script to export vectors from Qdrant and load them into the `embedding` property of the corresponding Neo4j nodes.
5.  **Refactor Code**: Replace all calls to the Qdrant client with the new `vector_store` interface.
6.  **Delete Old Code**: Remove all Qdrant-related files and configurations.
7.  **Update Tests**: Modify unit and integration tests to rely only on Neo4j.

---

---

## 🔄 **Trade-off Analysis**

### Options Considered

#### Option 1: Keep Tri-Store Architecture (Neo4j + SQLite + Qdrant)
- **Pros**:
  - Best-in-class vector search performance with Qdrant
  - Independent scaling of vector operations
  - Specialized vector database features (filtering, metadata)
  - Proven architecture pattern for large-scale systems
  
- **Cons**:
  - Complex consistency management across three stores
  - Requires Transactional Outbox Pattern implementation
  - Additional operational overhead (monitoring, backups, updates)
  - Higher infrastructure costs
  - Risk of data inconsistency during reconciliation windows

#### Option 2: Single Neo4j Database (Graph + Vectors + Metadata)
- **Pros**:
  - Simplest possible architecture
  - Perfect consistency (single ACID store)
  - Minimal operational overhead
  - Lowest cost
  
- **Cons**:
  - Poor text/document storage capabilities
  - Limited full-text search compared to dedicated solutions
  - Would require complex JSON storage for metadata
  - Performance concerns with mixed workloads

#### Option 3: Bi-Store Architecture (Neo4j + SQLite) [SELECTED]
- **Pros**:
  - Balanced complexity - simpler than tri-store
  - Strong consistency within each domain (graph+vectors atomic)
  - Leverages Neo4j 5.13+ native vector capabilities
  - SQLite excellent for metadata and workflow state
  - Clean separation of concerns
  - Future migration path via VectorStore abstraction
  
- **Cons**:
  - Vector search may not scale beyond ~10M embeddings
  - Still requires cross-database coordination for some operations
  - Neo4j becomes more critical (single point of failure for core data)

#### Option 4: Alternative Bi-Store (PostgreSQL with pgvector + Neo4j)
- **Pros**:
  - PostgreSQL more feature-rich than SQLite
  - pgvector provides good vector search
  - Could consolidate all non-graph data
  - Better concurrent access than SQLite
  
- **Cons**:
  - Adds PostgreSQL as new dependency
  - More complex than SQLite for single-user research platform
  - Overkill for current scale requirements
  - Would still need consistency management

### Decision Rationale

The bi-store architecture (Option 3) was selected because:

1. **Appropriate Complexity**: Eliminates the most complex aspect (tri-store consistency) while maintaining clean separation between graph and metadata storage.

2. **Scale-Appropriate**: For a research platform processing thousands (not millions) of documents, Neo4j's native vector index is more than sufficient.

3. **Consistency Benefits**: Atomic updates to graph + vectors eliminates entire classes of bugs and complexity.

4. **Future Flexibility**: The VectorStore abstraction allows migration to Qdrant later if scale demands it, without major refactoring.

5. **Operational Simplicity**: One less service to deploy, monitor, backup, and maintain.

6. **Cost Efficiency**: Reduces infrastructure requirements while meeting all functional needs.

### When to Reconsider

This decision should be revisited if:
- Vector corpus grows beyond 10M embeddings
- Query latency for vector search exceeds 500ms consistently  
- Need for advanced vector search features (hybrid search, filtering)
- Moving from single-user to multi-tenant architecture
- Require real-time vector index updates at high throughput

The VectorStore abstraction ensures this future migration would be straightforward, involving only the implementation of a new concrete class without changes to application logic.

---

**Related ADRs**: Supersedes the "Tri-Store Consistency" section of ADR-001/ADR-002 discussions. Complements the workflow state management approach. 

================================================================================

## 14. ADR-009-Bi-Store-Database-Strategy.md

**Source**: `docs/architecture/adrs/ADR-009-Bi-Store-Database-Strategy.md`

---

# ADR-009: Bi-Store Database Strategy

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: System requires both graph analysis capabilities and operational metadata storage for academic research workflows.

## Decision

We will implement a **bi-store architecture** using:

1. **Neo4j (v5.13+)**: Primary graph database for entities, relationships, and vector embeddings
2. **SQLite**: Operational metadata database for provenance, workflow state, and PII vault

```python
# Unified access pattern
class DataManager:
    def __init__(self):
        self.neo4j = Neo4jManager()      # Graph operations
        self.sqlite = SQLiteManager()    # Metadata operations
    
    def store_entity(self, entity_data):
        # Store graph data in Neo4j
        entity_id = self.neo4j.create_entity(entity_data)
        
        # Store operational metadata in SQLite
        self.sqlite.log_provenance(entity_id, "entity_creation", entity_data)
        
        return entity_id
```

## Rationale

### **Why Two Databases Instead of One?**

**1. Graph Analysis Requirements**: Academic research requires complex graph operations:
- **Entity relationship analysis**: "Find all researchers influenced by Foucault"
- **Community detection**: Identify research clusters and schools of thought
- **Path analysis**: "How is theory A connected to theory B?"
- **Centrality analysis**: Identify most influential concepts/researchers

**Neo4j excels at these operations with Cypher queries like:**
```cypher
MATCH (a:Entity {name: "Foucault"})-[:INFLUENCES*1..3]->(influenced)
RETURN influenced.name, length(path) as degrees_of_separation
```

**2. Operational Metadata Requirements**: Academic integrity requires detailed operational tracking:
- **Provenance tracking**: Complete audit trail of every operation
- **Workflow state**: Long-running research workflow checkpoints
- **PII protection**: Encrypted storage of sensitive personal information
- **Configuration state**: Tool settings and parameter tracking

**SQLite excels at these operations with relational queries and ACID transactions.**

**3. Performance Optimization**: 
- **Graph queries** on Neo4j: Optimized for traversal and pattern matching
- **Metadata queries** on SQLite: Optimized for joins, aggregations, and transactional consistency

### **Why Not Single Database Solutions?**

**Neo4j Only**:
- ❌ **Poor relational operations**: Complex joins and aggregations are inefficient
- ❌ **Metadata bloat**: Operational metadata clutters graph with non-analytical data
- ❌ **ACID limitations**: Neo4j transactions less robust for operational metadata
- ❌ **PII security**: Graph databases not optimized for encrypted key-value storage

**SQLite Only**:
- ❌ **Graph operations**: Recursive CTEs cannot match Neo4j's graph algorithm performance
- ❌ **Vector operations**: No native vector similarity search capabilities
- ❌ **Scalability**: Graph traversals become exponentially slow with data growth
- ❌ **Cypher equivalent**: No domain-specific query language for graph patterns

**PostgreSQL Only**:
- ❌ **Local deployment**: Requires server setup incompatible with academic research environments
- ❌ **Graph extensions**: Extensions like AGE add complexity without matching Neo4j performance
- ❌ **Vector search**: Extensions available but not as mature as Neo4j's native support

## Alternatives Considered

### **1. Neo4j + PostgreSQL**
- **Rejected**: PostgreSQL server requirement incompatible with single-node academic research
- **Problem**: Requires database server administration and configuration

### **2. Pure Neo4j with Metadata as Graph Nodes**
- **Rejected**: Creates graph pollution and performance degradation
- **Problem**: Provenance metadata would create millions of nodes unrelated to research analysis

### **3. Pure SQLite with Graph Tables**
- **Rejected**: Recursive graph queries become prohibitively slow
- **Problem**: Academic research requires complex graph analysis not feasible in pure SQL

### **4. In-Memory Graph (NetworkX) + SQLite**
- **Rejected**: Memory limitations prevent analysis of large research corpora
- **Problem**: Cannot handle 1000+ document research projects

## Consequences

### **Positive**
- **Optimal Performance**: Each database handles operations it's designed for
- **Data Separation**: Analytical data separate from operational metadata
- **Local Deployment**: Both databases support single-node academic environments
- **Specialized Tooling**: Can use Neo4j Browser for graph exploration, SQL tools for metadata
- **Vector Integration**: Neo4j v5.13+ native vector support for embeddings

### **Negative**
- **Complexity**: Two database systems to maintain and coordinate
- **Transaction Coordination**: Cross-database transactions require careful coordination
- **Data Synchronization**: Entity IDs must remain consistent across both stores
- **Backup Complexity**: Two separate backup and recovery procedures required

## Data Distribution Strategy

### **Neo4j Store**
```cypher
// Entities with vector embeddings
(:Entity {
    id: string,
    canonical_name: string,
    entity_type: string,
    confidence: float,
    embedding: vector[384]
})

// Relationships
(:Entity)-[:INFLUENCES {confidence: float, source: string}]->(:Entity)

// Documents
(:Document {id: string, title: string, source: string})

// Vector indexes for similarity search
CREATE VECTOR INDEX entity_embedding_index 
FOR (e:Entity) ON (e.embedding)
```

### **SQLite Store**
```sql
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

-- Workflow state for long-running processes
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP
);

-- Encrypted PII storage
CREATE TABLE pii_vault (
    pii_id TEXT PRIMARY KEY,
    ciphertext_b64 TEXT NOT NULL,
    nonce_b64 TEXT NOT NULL
);
```

## Transaction Coordination

For operations affecting both databases:

```python
@contextmanager
def distributed_transaction():
    """Coordinate transactions across Neo4j and SQLite"""
    neo4j_tx = None
    sqlite_tx = None
    
    try:
        # Start both transactions
        neo4j_session = neo4j_driver.session()
        neo4j_tx = neo4j_session.begin_transaction()
        sqlite_tx = sqlite_conn.begin()
        
        yield (neo4j_tx, sqlite_tx)
        
        # Commit both if successful
        neo4j_tx.commit()
        sqlite_tx.commit()
        
    except Exception as e:
        # Rollback both on any failure
        if neo4j_tx:
            neo4j_tx.rollback()
        if sqlite_tx:
            sqlite_tx.rollback()
        raise DistributedTransactionError(f"Transaction failed: {e}")
```

## Implementation Requirements

### **Consistency Guarantees**
- Entity IDs must be identical across both databases
- All graph operations must have corresponding provenance entries
- Transaction failures must rollback both databases

### **Performance Requirements**
- Graph queries: < 2 seconds for typical academic research patterns
- Metadata queries: < 500ms for provenance and workflow operations
- Cross-database coordination: < 100ms overhead

### **Backup and Recovery**
- Neo4j: Graph database dumps with entity/relationship preservation
- SQLite: File-based backups with transaction log consistency
- Coordinated restoration ensuring ID consistency

## Validation Criteria

- [ ] Graph analysis queries perform within academic research requirements
- [ ] Metadata operations maintain ACID properties
- [ ] Cross-database entity ID consistency maintained
- [ ] Transaction coordination prevents partial failures
- [ ] Backup/recovery maintains data integrity across both stores
- [ ] Vector similarity search performs effectively on research corpora

## Related ADRs

- **ADR-008**: Core Service Architecture (services use both databases)
- **ADR-006**: Cross-Modal Analysis (requires graph and metadata coordination)
- **ADR-003**: Vector Store Consolidation (Neo4j vector capabilities)

## Implementation Status

This ADR describes the **target bi-store database architecture** - the intended Neo4j + SQLite design. For current database implementation status and data layer progress, see:

- **[Roadmap Overview](../../roadmap/ROADMAP_OVERVIEW.md)** - Current database implementation status
- **[Core Service Implementation](../../roadmap/phases/phase-2-implementation-evidence.md)** - Database service completion status
- **[Data Architecture Progress](../../roadmap/initiatives/clear-implementation-roadmap.md)** - Bi-store implementation timeline

*This ADR contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*

---

This bi-store strategy optimizes for both analytical capabilities and operational reliability required for rigorous academic research while maintaining the simplicity appropriate for single-node research environments.

================================================================================

## 15. ADR-020-Agent-Based-Modeling-Integration.md

**Source**: `docs/architecture/adrs/ADR-020-Agent-Based-Modeling-Integration.md`

---

# ADR-020: Agent-Based Modeling Integration

**Status**: Accepted  
**Date**: 2025-01-23  
**Context**: KGAS currently focuses on descriptive analysis of social phenomena but lacks capability to validate theories through simulation or explore counterfactual scenarios

## Context

KGAS is designed as a theory-aware computational social science platform with strong capabilities in:
- Cross-modal analysis (graph/table/vector)
- Theory operationalization through schemas
- Uncertainty quantification and provenance tracking
- Academic research workflows

However, the current architecture is purely **analytical/descriptive** - it can analyze existing social phenomena but cannot:
- **Validate theories** through controlled simulation
- **Test counterfactuals** ("what if" scenarios)
- **Generate synthetic data** for theory testing
- **Explore emergent behaviors** from theoretical assumptions

Recent advances in **Generative Agent-Based Modeling (GABM)** using Large Language Models (Concordia framework, Google DeepMind) enable sophisticated theory-driven agent simulations that could complement KGAS's analytical capabilities.

## Decision

**Integrate Agent-Based Modeling capabilities into KGAS as a new architectural layer for theory validation and synthetic experiment generation.**

## KGAS Theory Meta-Schema v10 to ABM Translation

The theory meta-schema v10 provides a comprehensive framework for translating KGAS theories into agent-based models. This section demonstrates how schema components map to agent configurations.

### Translation Framework Overview

```python
class TheoryToABMTranslator:
    """Translates KGAS theory meta-schema v10 to ABM agent configurations"""
    
    def __init__(self, theory_schema: Dict):
        self.schema = theory_schema
        self.agent_factory = KGASTheoryDrivenAgent
        self.environment_builder = TheoryEnvironmentBuilder()
    
    def translate_theory_to_agents(self) -> List[AgentConfiguration]:
        """Main translation method"""
        # Extract entities from ontology
        entities = self.schema['ontology']['entities']
        
        # Create agent configurations for each entity type
        agent_configs = []
        for entity in entities:
            config = self._create_agent_config_from_entity(entity)
            agent_configs.append(config)
        
        return agent_configs
    
    def _create_agent_config_from_entity(self, entity: Dict) -> AgentConfiguration:
        """Convert theory entity to agent configuration"""
        agent_config = AgentConfiguration(
            agent_type=entity['name'],
            behavioral_rules=self._extract_behavioral_rules(entity),
            decision_framework=self._extract_decision_framework(entity),
            measurement_approach=self._extract_measurement_approach(entity),
            interaction_patterns=self._extract_interaction_patterns(entity)
        )
        return agent_config
```

### Example 1: Stakeholder Theory Translation

Using the stakeholder theory v10 schema as an example:

```python
# From stakeholder_theory_v10.json
stakeholder_entity = {
    "name": "Stakeholder",
    "properties": [
        {"name": "legitimacy", "type": "float", "operationalization": {...}},
        {"name": "urgency", "type": "float", "operationalization": {...}},
        {"name": "power", "type": "float", "operationalization": {...}}
    ]
}

# Translates to:
class StakeholderAgent(KGASTheoryDrivenAgent):
    def __init__(self, agent_id: str, legitimacy: float, urgency: float, power: float):
        super().__init__(agent_id, "Stakeholder")
        
        # Agent state from theory properties
        self.legitimacy = legitimacy  # 0-1 scale from operationalization
        self.urgency = urgency       # 0-1 scale from operationalization  
        self.power = power           # 0-1 scale from operationalization
        
        # Calculated salience using Mitchell-Agle-Wood model
        self.salience = self._calculate_salience()
        
        # Behavioral rules from execution steps
        self.behavioral_rules = [
            self._assess_organizational_impact,
            self._determine_influence_strategy,
            self._adapt_engagement_approach
        ]
    
    def _calculate_salience(self) -> float:
        """Implement custom_script from schema"""
        # From schema: "salience = (legitimacy * urgency * power) ^ (1/3)"
        return (self.legitimacy * self.urgency * self.power) ** (1/3)
    
    def _assess_organizational_impact(self, context: SimulationContext) -> Dict:
        """Behavioral rule derived from HAS_STAKE_IN relationship"""
        organization = context.get_organization()
        
        # Calculate stake strength from relationship properties
        stake_strength = self._evaluate_stake_strength(organization)
        
        return {
            'action': 'assess_impact',
            'stake_strength': stake_strength,
            'concerns': self._identify_concerns(organization)
        }
    
    def _determine_influence_strategy(self, context: SimulationContext) -> Dict:
        """Strategy based on power operationalization"""
        if self.power > 0.8:
            strategy = "direct_pressure"
        elif self.power > 0.5:
            strategy = "coalition_building" 
        else:
            strategy = "public_appeal"
        
        return {'influence_strategy': strategy, 'power_level': self.power}
    
    def step(self, context: SimulationContext) -> List[Dict]:
        """Execute theory-driven behavior"""
        actions = []
        
        # Apply behavioral rules in sequence
        for rule in self.behavioral_rules:
            action = rule(context)
            actions.append(action)
            
        # Update salience based on context changes
        self._update_salience(context)
        
        return actions
```

### Example 2: Framing Theory Translation

Using the Carter framing theory schema:

```python
# From carter_framing_theory_schema.yml
framing_analysis = {
    "frames_in_communication": [
        {"frame": "Peace Frame", "considerations": ["mutual benefit", "shared humanity"]},
        {"frame": "Security Frame", "considerations": ["strategic balance", "deterrence"]},
        {"frame": "Values Frame", "considerations": ["human rights", "moral leadership"]}
    ],
    "psychological_mechanisms": {
        "accessibility": "Vietnam/Watergate memories activate credibility concerns",
        "applicability": "Universal human values connect with audience beliefs"
    }
}

# Translates to:
class FramingAgent(KGASTheoryDrivenAgent):
    def __init__(self, agent_id: str, frame_preference: str, political_knowledge: float):
        super().__init__(agent_id, "FramingAgent")
        
        # Agent cognitive state from theory
        self.frame_preference = frame_preference  # "peace", "security", "values", "realism"
        self.political_knowledge = political_knowledge  # Individual moderator
        self.active_considerations = []
        
        # Frame processing mechanisms from explanatory_analysis
        self.accessibility_memory = self._initialize_memory()
        self.applicability_filter = self._initialize_value_filter()
        
        # Behavioral rules from competitive_dynamics
        self.behavioral_rules = [
            self._process_frame_exposure,
            self._evaluate_frame_strength,
            self._update_attitude_formation,
            self._generate_response
        ]
    
    def _process_frame_exposure(self, context: SimulationContext) -> Dict:
        """Implement accessibility mechanism from theory"""
        exposed_frames = context.get_current_frames()
        
        for frame in exposed_frames:
            # Theory: "Frame Exposure → Consideration Activation → Attitude Formation"
            considerations = self._activate_considerations(frame)
            self.active_considerations.extend(considerations)
            
        return {
            'action': 'frame_processing',
            'activated_considerations': self.active_considerations
        }
    
    def _evaluate_frame_strength(self, context: SimulationContext) -> Dict:
        """Implement competitive_dynamics from causal_analysis"""
        competing_frames = context.get_competing_frames()
        
        # Theory: "Stronger frames dominate weaker ones"
        frame_strengths = {}
        for frame in competing_frames:
            strength = self._calculate_frame_appeal(frame)
            frame_strengths[frame.id] = strength
            
        dominant_frame = max(frame_strengths, key=frame_strengths.get)
        
        return {
            'action': 'frame_evaluation',
            'dominant_frame': dominant_frame,
            'frame_competition_result': frame_strengths
        }
    
    def _update_attitude_formation(self, context: SimulationContext) -> Dict:
        """Implement expectancy_value_model from explanatory_analysis"""
        # Theory: "Attitude = Σ(value_i × weight_i)"
        key_values = ["peace", "security", "credibility", "moral_leadership"]
        
        attitude_score = 0
        for value in key_values:
            value_weight = self._get_value_weight(value)
            value_importance = self._get_value_importance(value, context)
            attitude_score += value_weight * value_importance
            
        self.current_attitude = attitude_score
        
        return {
            'action': 'attitude_update',
            'attitude_score': attitude_score,
            'value_weights': {v: self._get_value_weight(v) for v in key_values}
        }
```

### Cross-Modal Agent Representation

Agents can represent themselves across different analytical modes as specified in the schema's cross_modal_mappings:

```python
class MultiModalAgent(KGASTheoryDrivenAgent):
    def get_graph_representation(self) -> Dict:
        """Agent as graph node with properties"""
        return {
            'node_id': self.agent_id,
            'node_type': self.agent_type,
            'properties': {
                'salience_score': getattr(self, 'salience', 0),
                'legitimacy': getattr(self, 'legitimacy', 0),
                'urgency': getattr(self, 'urgency', 0),
                'power': getattr(self, 'power', 0)
            },
            'edges': self._get_relationship_edges()
        }
    
    def get_table_representation(self) -> Dict:
        """Agent as table row with calculated metrics"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'salience_score': getattr(self, 'salience', 0),
            'influence_rank': self._calculate_influence_rank(),
            'network_centrality': self._calculate_centrality(),
            'cluster_membership': self._get_cluster_id()
        }
    
    def get_vector_representation(self) -> np.ndarray:
        """Agent as embedding vector for similarity analysis"""
        behavioral_features = self._extract_behavioral_features()
        communication_features = self._extract_communication_features()
        return np.concatenate([behavioral_features, communication_features])
```

### Dynamic Adaptation Implementation

For theories with dynamic_adaptation specifications:

```python
class AdaptiveAgent(KGASTheoryDrivenAgent):
    def __init__(self, agent_id: str, theory_schema: Dict):
        super().__init__(agent_id, "AdaptiveAgent")
        
        # Initialize state variables from schema
        dynamic_config = theory_schema.get('dynamic_adaptation', {})
        self.state_variables = {}
        
        for var_name, var_config in dynamic_config.get('state_variables', {}).items():
            self.state_variables[var_name] = var_config['initial']
        
        # Store adaptation rules and triggers
        self.adaptation_triggers = dynamic_config.get('adaptation_triggers', [])
        self.adaptation_rules = dynamic_config.get('adaptation_rules', [])
    
    def step(self, context: SimulationContext) -> List[Dict]:
        """Execute with dynamic adaptation"""
        # Normal behavior execution
        actions = super().step(context)
        
        # Check adaptation triggers
        for trigger in self.adaptation_triggers:
            if self._evaluate_condition(trigger['condition'], context):
                self._execute_adaptation(trigger['action'])
        
        return actions
    
    def _evaluate_condition(self, condition: str, context: SimulationContext) -> bool:
        """Evaluate adaptation trigger condition"""
        # Parse condition like "minority_visibility < 0.3"
        # Use safe evaluation with current state and context
        evaluation_context = {
            **self.state_variables,
            'context': context
        }
        
        return eval(condition, {"__builtins__": {}}, evaluation_context)
    
    def _execute_adaptation(self, action: str):
        """Execute adaptation action like 'increase_spiral_strength'"""
        # Apply adaptation rules
        for rule in self.adaptation_rules:
            if action in rule:
                # Execute rule like "spiral_strength *= 1.2 when minority_visibility decreases"
                self._apply_adaptation_rule(rule)
```

### Validation Integration

Agent behavior validation using theory test cases from the schema:

```python
class TheoryValidationFramework:
    def __init__(self, theory_schema: Dict, agent_population: List[KGASTheoryDrivenAgent]):
        self.schema = theory_schema
        self.agents = agent_population
        self.validation_config = theory_schema.get('validation', {})
    
    def run_theory_tests(self) -> Dict[str, bool]:
        """Execute theory_tests from validation section"""
        results = {}
        
        for test in self.validation_config.get('theory_tests', []):
            test_result = self._execute_theory_test(test)
            results[test['test_name']] = test_result
        
        return results
    
    def _execute_theory_test(self, test: Dict) -> bool:
        """Execute individual theory test"""
        # Set up scenario from input_scenario
        scenario = self._create_test_scenario(test['input_scenario'])
        
        # Run simulation with test scenario
        simulation_result = self._run_test_simulation(scenario)
        
        # Validate against expected_theory_application and validation_criteria
        return self._validate_result(simulation_result, test)
    
    def check_boundary_cases(self) -> List[Dict]:
        """Handle boundary_cases from validation section"""
        boundary_results = []
        
        for case in self.validation_config.get('boundary_cases', []):
            case_result = self._handle_boundary_case(case)
            boundary_results.append(case_result)
        
        return boundary_results
```

This translation framework demonstrates how KGAS theory meta-schema v10 components directly map to agent-based model configurations, enabling automated theory-to-simulation translation while maintaining theoretical fidelity and validation capabilities.

## Architecture Design

### Research-Informed Design Principles

Based on recent advances in generative agent research (Park et al. 2024, Lu et al. 2025, Gui & Toubia 2025), KGAS ABM incorporates:

1. **Rich Individual Parameterization**: Following Stanford's approach, agents use deep individual profiles beyond demographics
2. **Objective Accuracy Focus**: Emphasis on measurable accuracy metrics rather than subjective believability
3. **Unblinded Experimental Design**: Explicit experimental design communication to avoid confounding
4. **Expert Reflection Architecture**: Domain expert synthesis of agent characteristics from theory schemas
5. **Reasoning-Enhanced Agents**: Synthesized reasoning traces to improve decision accuracy
6. **Real-World Behavioral Validation**: Validation against actual behavioral datasets (COVID dataset)

### 1. ABM Service Layer

Add ABM capabilities as a new service in the Core Services Layer:

```python
class ABMService:
    """Agent-Based Modeling service for theory validation and simulation"""
    
    def __init__(self, theory_repository, knowledge_graphs, uncertainty_engine):
        self.theory_repository = theory_repository
        self.knowledge_graphs = knowledge_graphs
        self.uncertainty_engine = uncertainty_engine
        self.simulation_engine = GABMSimulationEngine()
        self.validation_engine = TheoryValidationEngine()
    
    def create_theory_simulation(self, theory_id: str) -> SimulationConfiguration:
        """Convert KGAS theory schema to GABM simulation parameters"""
        
    def run_simulation_experiment(self, config: SimulationConfiguration) -> SimulationResults:
        """Execute controlled ABM experiment with uncertainty tracking"""
        
    def validate_theory_predictions(self, theory_id: str, real_data: DataFrame) -> ValidationReport:
        """Compare simulation results to empirical data"""
```

### 2. Rich Individual Agent Architecture

Incorporating insights from Stanford's interview-based agents and reasoning-enhanced approaches:

```python
class KGASTheoryDrivenAgent(GenerativeAgent):
    """GABM agent with rich individual parameterization and expert reflection"""
    
    def __init__(self, theory_schema: TheoryMetaSchema, agent_profile: RichAgentProfile):
        # Core agent identity from multiple sources (Stanford approach)
        self.agent_id = agent_profile.agent_id
        self.theory_id = theory_schema.theory_id
        
        # Rich individual parameterization beyond demographics
        self.individual_profile = self._create_rich_profile(agent_profile)
        self.expert_reflection = self._synthesize_expert_insights(theory_schema, agent_profile)
        
        # Theory-derived components
        self.identity_component = self._create_identity_from_theory(theory_schema, agent_profile)
        self.behavioral_rules = self._extract_behavioral_predictions(theory_schema)
        self.social_context = self._apply_scope_conditions(theory_schema)
        
        # Reasoning-enhanced decision making (Lu et al. approach)
        self.reasoning_engine = ReasoningEngine(theory_schema)
        self.uncertainty_awareness = UncertaintyAwareness(uncertainty_engine)
        
        # Validation against real behavioral patterns
        self.behavioral_validator = BehavioralPatternValidator(covid_dataset)
    
    def _create_rich_profile(self, agent_profile: RichAgentProfile) -> RichIndividualProfile:
        """Create rich individual profile beyond demographics (Stanford approach)"""
        return RichIndividualProfile(
            # Demographic basics
            demographics=agent_profile.demographics,
            
            # Psychological characteristics (from COVID dataset psychometric scales)
            psychological_traits={
                'narcissism': agent_profile.narcissism_score,
                'need_for_chaos': agent_profile.need_for_chaos_score,
                'conspiracy_mentality': agent_profile.conspiracy_mentality_score,
                'denialism': agent_profile.denialism_score,
                'misinformation_susceptibility': agent_profile.misinformation_susceptibility
            },
            
            # Behavioral patterns (from COVID dataset engagement data)
            behavioral_history=agent_profile.twitter_engagement_patterns,
            
            # Social network position
            social_characteristics={
                'follower_count': agent_profile.follower_count,
                'following_count': agent_profile.following_count,
                'network_centrality': agent_profile.calculated_centrality,
                'engagement_frequency': agent_profile.engagement_frequency
            },
            
            # Theory-specific characteristics
            theory_relevance=agent_profile.theory_alignment_scores
        )
    
    def _synthesize_expert_insights(self, theory: TheoryMetaSchema, 
                                   profile: RichAgentProfile) -> ExpertReflection:
        """Expert reflection module (Stanford approach)"""
        expert_persona = f"You are a {theory.domain} expert analyzing this individual's profile"
        
        # Synthesize high-level insights from the rich profile
        expert_synthesis = self.llm_call(
            system_prompt=expert_persona,
            user_prompt=f"""
            Analyze this individual's profile and synthesize key psychological and behavioral insights:
            
            Demographics: {profile.demographics}
            Psychological Traits: {profile.psychological_traits}
            Behavioral History: {profile.behavioral_summary}
            Social Position: {profile.social_characteristics}
            Theory Alignment: {profile.theory_alignment_scores}
            
            Provide expert insights on:
            1. Core personality characteristics
            2. Likely behavioral tendencies
            3. Social influence patterns
            4. Decision-making style
            5. Vulnerability to misinformation
            """,
            temperature=0.3
        )
        
        return ExpertReflection(
            expert_domain=theory.domain,
            synthesis=expert_synthesis,
            confidence_assessment=self._assess_profile_completeness(profile),
            behavioral_predictions=self._extract_behavioral_predictions(expert_synthesis)
        )
    
    def _create_identity_from_theory(self, theory: TheoryMetaSchema) -> AgentIdentity:
        """Convert theory key concepts to agent identity"""
        return AgentIdentity(
            core_concepts=theory.key_concepts,
            domain_knowledge=theory.domain_specific_elements,
            theoretical_assumptions=theory.theoretical_predictions
        )
    
    async def decide_action(self, context: SimulationContext) -> AgentAction:
        """Reasoning-enhanced decision making (Lu et al. approach)"""
        
        # Step 1: Generate explicit reasoning trace
        reasoning_trace = await self.reasoning_engine.generate_reasoning(
            context=context,
            agent_profile=self.individual_profile,
            expert_reflection=self.expert_reflection,
            behavioral_rules=self.behavioral_rules
        )
        
        # Step 2: Assess confidence in decision context
        confidence = await self.uncertainty_awareness.assess_decision_confidence(
            context, self.behavioral_rules, self.memory, reasoning_trace
        )
        
        # Step 3: Make decision based on reasoning and confidence
        if confidence < self.decision_threshold:
            action = await self._seek_information_action(context, reasoning_trace)
        else:
            action = await self._apply_behavioral_rule(context, confidence, reasoning_trace)
        
        # Step 4: Validate against real behavioral patterns
        behavioral_plausibility = await self.behavioral_validator.validate_action(
            action, self.individual_profile, context
        )
        
        # Step 5: Track decision provenance
        decision_record = DecisionRecord(
            agent_id=self.agent_id,
            context=context,
            reasoning_trace=reasoning_trace,
            confidence_assessment=confidence,
            action_taken=action,
            behavioral_plausibility=behavioral_plausibility,
            theory_influence=self._trace_theory_influence(action),
            expert_reflection_influence=self._trace_expert_influence(action),
            timestamp=datetime.now()
        )
        
        self.decision_history.append(decision_record)
        return action

class ReasoningEngine:
    """Generate explicit reasoning traces for agent decisions (Lu et al. approach)"""
    
    def __init__(self, theory_schema: TheoryMetaSchema):
        self.theory_schema = theory_schema
        self.reasoning_synthesizer = ReasoningSynthesizer()
    
    async def generate_reasoning(self, 
                               context: SimulationContext,
                               agent_profile: RichIndividualProfile,
                               expert_reflection: ExpertReflection,
                               behavioral_rules: List[BehavioralRule]) -> ReasoningTrace:
        """Generate explicit reasoning for decision context"""
        
        reasoning_prompt = f"""
        You are {agent_profile.demographics['name']}, with the following characteristics:
        
        Psychological Profile: {agent_profile.psychological_traits}
        Behavioral History: {agent_profile.behavioral_history}
        Expert Assessment: {expert_reflection.synthesis}
        
        Current Situation: {context.description}
        Available Actions: {context.available_actions}
        
        Theory-Based Behavioral Rules:
        {[rule.description for rule in behavioral_rules]}
        
        Explain your reasoning for what you would do in this situation. Consider:
        1. How your personality traits influence your thinking
        2. What your past behavior suggests you might do
        3. How the expert assessment applies to this situation
        4. Which theoretical behavioral rules are most relevant
        5. What uncertainties or concerns you have
        
        Provide your reasoning in first-person, as if thinking through the decision.
        """
        
        reasoning_text = await self.llm_call(
            system_prompt="You are reasoning through a decision as this specific individual.",
            user_prompt=reasoning_prompt,
            temperature=0.7
        )
        
        return ReasoningTrace(
            raw_reasoning=reasoning_text,
            key_factors=self._extract_key_factors(reasoning_text),
            theory_applications=self._identify_theory_applications(reasoning_text, behavioral_rules),
            uncertainty_sources=self._identify_uncertainty_sources(reasoning_text),
            confidence_indicators=self._assess_reasoning_confidence(reasoning_text)
        )
```

### 3. Cross-Modal Agent Environments

Use KGAS's tri-modal architecture to create rich simulation environments:

```python
class CrossModalGameMaster(GameMaster):
    """Game Master that uses KGAS cross-modal data as environment"""
    
    def __init__(self, knowledge_graph, demographic_data, semantic_embeddings):
        self.social_network = knowledge_graph  # Constrains agent interactions
        self.agent_characteristics = demographic_data  # Agent initial states
        self.conceptual_space = semantic_embeddings  # Semantic similarity
        self.provenance_tracker = ProvenanceTracker()
    
    def determine_agent_interactions(self, agent_actions: List[AgentAction]) -> List[Interaction]:
        """Use knowledge graph to determine possible interactions"""
        possible_interactions = []
        
        for action in agent_actions:
            # Query knowledge graph for interaction possibilities
            interaction_candidates = self.social_network.query_interaction_possibilities(
                agent=action.agent,
                action_type=action.action_type,
                context=action.context
            )
            
            # Filter by demographic compatibility
            compatible_interactions = self.filter_by_demographics(
                interaction_candidates, 
                self.agent_characteristics
            )
            
            # Score by semantic similarity
            scored_interactions = self.score_by_semantic_similarity(
                compatible_interactions,
                self.conceptual_space
            )
            
            possible_interactions.extend(scored_interactions)
        
        return self.resolve_interaction_conflicts(possible_interactions)

### 4. Unblinded Experimental Design (Gui & Toubia Insights)

Addressing critical confounding issues in LLM-based simulations:

```python
class UnblindedExperimentalDesign:
    """Unblinded experimental design to avoid confounding (Gui & Toubia approach)"""
    
    def __init__(self, theory_repository: TheoryRepository):
        self.theory_repository = theory_repository
        self.causal_inference_validator = CausalInferenceValidator()
    
    def create_unblinded_simulation_prompt(self, 
                                         experimental_design: ExperimentalDesign,
                                         agent_profile: RichAgentProfile) -> UnblindedPrompt:
        """Create unambiguous experimental prompt avoiding confounding"""
        
        # Explicitly communicate the experimental design to avoid ambiguity
        experimental_context = f"""
        EXPERIMENTAL DESIGN CONTEXT:
        - This is a controlled experiment testing: {experimental_design.hypothesis}
        - Treatment variable: {experimental_design.treatment_variable}
        - Treatment conditions: {experimental_design.treatment_conditions}
        - Control variables held constant: {experimental_design.control_variables}
        - Randomization scheme: {experimental_design.randomization_method}
        
        IMPORTANT: You are experiencing the {experimental_design.current_condition} condition.
        This condition was randomly assigned for experimental purposes.
        All other factors should be considered at their typical/baseline levels unless specified.
        """
        
        # Agent-specific context
        agent_context = f"""
        YOUR INDIVIDUAL CHARACTERISTICS:
        Demographics: {agent_profile.demographics}
        Psychological Traits: {agent_profile.psychological_traits}
        Behavioral History: {agent_profile.behavioral_history}
        Social Position: {agent_profile.social_characteristics}
        """
        
        # Clear causal question
        causal_question = f"""
        DECISION TASK:
        Given your individual characteristics and the experimental condition you're experiencing,
        how would you respond to: {experimental_design.decision_scenario}
        
        Focus on how the treatment condition ({experimental_design.treatment_variable}: 
        {experimental_design.current_condition}) affects your decision, holding all other 
        factors at their typical levels.
        """
        
        return UnblindedPrompt(
            experimental_context=experimental_context,
            agent_context=agent_context,
            causal_question=causal_question,
            control_variables=experimental_design.control_variables,
            is_unambiguous=True
        )
    
    def validate_experimental_design(self, design: ExperimentalDesign) -> ValidationResult:
        """Validate experimental design for causal inference"""
        
        validation_checks = {
            'treatment_clarity': self._check_treatment_clarity(design),
            'control_specification': self._check_control_specification(design),
            'randomization_validity': self._check_randomization_validity(design),
            'confounding_prevention': self._check_confounding_prevention(design),
            'prompt_ambiguity': self._check_prompt_ambiguity(design)
        }
        
        overall_validity = all(check.is_valid for check in validation_checks.values())
        
        return ValidationResult(
            is_valid=overall_validity,
            validation_checks=validation_checks,
            recommendations=self._generate_design_recommendations(validation_checks)
        )

class CausalInferenceValidator:
    """Validate simulation results for causal inference (Gui & Toubia approach)"""
    
    def __init__(self):
        self.confounding_detector = ConfoundingDetector()
        self.ecological_validator = EcologicalValidityValidator()
    
    def validate_simulation_results(self, 
                                  simulation_results: SimulationResults,
                                  experimental_design: ExperimentalDesign) -> CausalValidationReport:
        """Comprehensive validation of causal inference from simulation"""
        
        # Check for confounding patterns
        confounding_analysis = self.confounding_detector.detect_confounding(
            simulation_results, experimental_design
        )
        
        # Validate ecological validity
        ecological_validity = self.ecological_validator.assess_ecological_validity(
            simulation_results, experimental_design
        )
        
        # Compare to real-world benchmarks (COVID dataset)
        benchmark_comparison = self._compare_to_benchmarks(
            simulation_results, experimental_design
        )
        
        # Generate causal inference assessment
        causal_inference_quality = self._assess_causal_inference_quality(
            confounding_analysis, ecological_validity, benchmark_comparison
        )
        
        return CausalValidationReport(
            confounding_analysis=confounding_analysis,
            ecological_validity=ecological_validity,
            benchmark_comparison=benchmark_comparison,
            causal_inference_quality=causal_inference_quality,
            recommendations=self._generate_causal_recommendations(
                confounding_analysis, ecological_validity
            )
        )
    
    def _compare_to_benchmarks(self, 
                              results: SimulationResults,
                              design: ExperimentalDesign) -> BenchmarkComparison:
        """Compare simulation results to real behavioral data"""
        
        # Find similar real-world studies from COVID dataset
        similar_studies = self._find_similar_studies(design)
        
        if not similar_studies:
            return BenchmarkComparison(
                comparison_available=False,
                reason="No similar real-world studies found"
            )
        
        # Compare effect sizes and patterns
        effect_size_comparison = self._compare_effect_sizes(results, similar_studies)
        pattern_comparison = self._compare_behavioral_patterns(results, similar_studies)
        
        return BenchmarkComparison(
            comparison_available=True,
            similar_studies=similar_studies,
            effect_size_similarity=effect_size_comparison,
            pattern_similarity=pattern_comparison,
            overall_similarity=np.mean([effect_size_comparison, pattern_comparison])
        )

class WhatIfScenarioExplorer:
    """Explore counterfactual scenarios (Social Simulacra approach)"""
    
    def __init__(self, abm_service: ABMService):
        self.abm_service = abm_service
        self.scenario_generator = ScenarioGenerator()
    
    async def explore_whatif_scenario(self, 
                                    base_simulation: SimulationResults,
                                    intervention: Intervention) -> WhatIfResults:
        """Explore 'what if' scenario with specified intervention"""
        
        # Create modified simulation configuration
        modified_config = self._apply_intervention(
            base_simulation.configuration, intervention
        )
        
        # Run counterfactual simulation
        counterfactual_results = await self.abm_service.run_simulation_experiment(
            modified_config
        )
        
        # Compare outcomes
        outcome_comparison = self._compare_outcomes(
            base_simulation, counterfactual_results
        )
        
        # Assess intervention effectiveness
        intervention_effectiveness = self._assess_intervention_effectiveness(
            outcome_comparison, intervention
        )
        
        return WhatIfResults(
            base_scenario=base_simulation,
            counterfactual_scenario=counterfactual_results,
            intervention_applied=intervention,
            outcome_comparison=outcome_comparison,
            intervention_effectiveness=intervention_effectiveness,
            causal_interpretation=self._generate_causal_interpretation(
                outcome_comparison, intervention
            )
        )
    
    async def explore_multiverse_scenarios(self, 
                                         base_config: SimulationConfiguration,
                                         num_variations: int = 10) -> MultiverseResults:
        """Generate multiple scenario variations (Social Simulacra multiverse)"""
        
        multiverse_results = []
        
        for i in range(num_variations):
            # Add randomness to simulation parameters
            varied_config = self._add_random_variation(base_config, variation_seed=i)
            
            # Run simulation with variation
            variant_results = await self.abm_service.run_simulation_experiment(varied_config)
            multiverse_results.append(variant_results)
        
        # Analyze variance across scenarios
        variance_analysis = self._analyze_multiverse_variance(multiverse_results)
        
        # Identify robust vs. fragile patterns
        robustness_analysis = self._analyze_pattern_robustness(multiverse_results)
        
        return MultiverseResults(
            base_configuration=base_config,
            scenario_variations=multiverse_results,
            variance_analysis=variance_analysis,
            robustness_analysis=robustness_analysis,
            design_implications=self._generate_design_implications(
                variance_analysis, robustness_analysis
            )
        )
```

### 4. Uncertainty-Aware Simulation

Integrate KGAS uncertainty framework into ABM:

```python
class UncertaintyAwareSimulation:
    """ABM simulation with KGAS uncertainty quantification"""
    
    def __init__(self, uncertainty_engine: UncertaintyEngine):
        self.uncertainty_engine = uncertainty_engine
        self.simulation_uncertainty = SimulationUncertainty()
    
    def run_simulation_with_uncertainty(self, config: SimulationConfiguration) -> UncertainSimulationResults:
        """Run simulation with uncertainty propagation"""
        
        # Track uncertainty in initial conditions
        initial_uncertainty = self.uncertainty_engine.assess_initial_conditions(config)
        
        # Run multiple simulation variants
        simulation_variants = self.generate_simulation_variants(config, initial_uncertainty)
        results = []
        
        for variant in simulation_variants:
            result = self.run_single_simulation(variant)
            result.uncertainty_metadata = self.track_simulation_uncertainty(variant, result)
            results.append(result)
        
        # Aggregate results with uncertainty
        aggregated_results = self.uncertainty_engine.aggregate_simulation_results(results)
        
        return UncertainSimulationResults(
            mean_results=aggregated_results.mean,
            confidence_intervals=aggregated_results.confidence_intervals,
            uncertainty_distribution=aggregated_results.uncertainty,
            provenance=self.generate_simulation_provenance(config, results)
        )
```

### 5. Validation Against Real Data

Use COVID conspiracy theory dataset for validation:

```python
class SimulationValidationEngine:
    """Validate ABM results against empirical data"""
    
    def __init__(self, covid_dataset: CovidConspiracyDataset):
        self.validation_data = covid_dataset
        self.psychological_profiles = covid_dataset.psychological_scales
        self.behavioral_data = covid_dataset.twitter_engagements
    
    def validate_conspiracy_theory_simulation(self, simulation_results: SimulationResults) -> ValidationReport:
        """Compare ABM results to COVID conspiracy behavior"""
        
        validation_metrics = []
        
        # Level 1: Behavioral Pattern Validation
        behavioral_similarity = self.compare_behavioral_patterns(
            simulation_results.agent_behaviors,
            self.behavioral_data.engagement_patterns
        )
        validation_metrics.append(("behavioral_similarity", behavioral_similarity))
        
        # Level 2: Psychological Construct Validation
        psychological_accuracy = self.validate_psychological_constructs(
            simulation_results.agent_psychological_states,
            self.psychological_profiles
        )
        validation_metrics.append(("psychological_accuracy", psychological_accuracy))
        
        # Level 3: Network Effect Validation
        network_effects = self.validate_network_propagation(
            simulation_results.information_spread,
            self.behavioral_data.retweet_cascades
        )
        validation_metrics.append(("network_effects", network_effects))
        
        return ValidationReport(
            overall_validity=self.calculate_overall_validity(validation_metrics),
            detailed_metrics=validation_metrics,
            recommendations=self.generate_improvement_recommendations(validation_metrics)
        )
    
    def compare_behavioral_patterns(self, simulated_behaviors: List[AgentBehavior], 
                                  real_behaviors: List[TwitterEngagement]) -> float:
        """Compare simulated agent behaviors to real Twitter engagement patterns"""
        
        # Extract behavioral features from both datasets
        simulated_features = self.extract_behavioral_features(simulated_behaviors)
        real_features = self.extract_behavioral_features(real_behaviors)
        
        # Calculate similarity using multiple metrics
        correlation_similarity = self.calculate_correlation(simulated_features, real_features)
        distribution_similarity = self.calculate_distribution_similarity(simulated_features, real_features)
        temporal_similarity = self.calculate_temporal_similarity(simulated_features, real_features)
        
        return (correlation_similarity + distribution_similarity + temporal_similarity) / 3
```

## Integration with Existing Architecture

### 1. Updated Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│    (Natural Language → Agent → Workflow → Results)           │
│                    + ABM Simulation Controls                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Cross-Modal Analysis Layer                    │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐   │
│  │Graph Analysis│ │Table Analysis│ │Vector Analysis      │   │
│  └─────────────┘ └──────────────┘ └─────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              ABM Simulation Layer                       │ │
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
│  └────────────────────┘ └────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. Data Architecture Extension

Extend bi-store architecture to support simulation data:

```sql
-- SQLite: Simulation metadata and results
CREATE TABLE simulations (
    simulation_id TEXT PRIMARY KEY,
    theory_id TEXT,
    configuration JSON,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT,
    uncertainty_metadata JSON
);

CREATE TABLE simulation_results (
    result_id TEXT PRIMARY KEY,
    simulation_id TEXT,
    agent_id TEXT,
    timestep INTEGER,
    action_type TEXT,
    action_data JSON,
    uncertainty_score REAL,
    provenance_chain TEXT
);

CREATE TABLE validation_reports (
    report_id TEXT PRIMARY KEY,
    simulation_id TEXT,
    validation_dataset TEXT,
    behavioral_similarity REAL,
    psychological_accuracy REAL,
    network_effects REAL,
    overall_validity REAL,
    recommendations JSON
);
```

```cypher
-- Neo4j: Agent relationships and simulation networks
CREATE (:SimulationAgent {
    agent_id: string,
    simulation_id: string,
    agent_type: string,
    psychological_profile: map,
    behavioral_rules: list,
    uncertainty_threshold: float
})

CREATE (:SimulationInteraction {
    interaction_id: string,
    simulation_id: string,
    timestep: integer,
    interaction_type: string,
    participants: list,
    outcome: map,
    uncertainty_metadata: map
})

// Relationship between agents and their interactions
CREATE (:SimulationAgent)-[:PARTICIPATED_IN]->(:SimulationInteraction)
```

### 3. Tool Ecosystem Extension

Add ABM tools to the 121+ tool ecosystem:

```python
# New ABM-specific tools
class T122_TheoryToAgentTranslator(KGASTool):
    """Convert theory schemas to agent configurations"""
    
class T123_SimulationDesigner(KGASTool):
    """Design controlled experiments for theory testing"""
    
class T124_AgentPopulationGenerator(KGASTool):
    """Generate diverse agent populations from demographic data"""
    
class T125_SimulationValidator(KGASTool):
    """Validate simulation results against empirical data"""
    
class T126_CounterfactualExplorer(KGASTool):
    """Explore 'what if' scenarios through simulation"""
    
class T127_SyntheticDataGenerator(KGASTool):
    """Generate synthetic datasets for theory testing"""
    
class T128_EmergentBehaviorDetector(KGASTool):
    """Detect emergent patterns in simulation results"""
```

## Rationale

### Why ABM Integration Is Strategic

1. **Complements Analytical Capabilities**: KGAS analyzes existing data; ABM validates theories through simulation
2. **Leverages Existing Architecture**: Theory schemas, uncertainty framework, and cross-modal analysis enhance ABM
3. **Academic Research Value**: Theory validation through simulation is cutting-edge computational social science
4. **Real Dataset Validation**: COVID conspiracy dataset provides ground truth for validation
5. **Publication Opportunities**: GABM validation of social science theories is highly publishable

### Why Now

1. **GABM Technology Maturity**: Concordia framework proves LLM-based ABM is feasible
2. **KGAS Foundation Ready**: Theory operationalization and uncertainty framework provide perfect foundation
3. **Validation Dataset Available**: COVID conspiracy dataset enables immediate validation capability
4. **Research Gap**: No existing platforms combine theory-driven ABM with cross-modal analysis

### Technical Advantages

1. **Theory-Driven Parameterization**: Unlike generic ABM, agents are parameterized by academic theories
2. **Uncertainty-Aware Simulation**: Incorporates KGAS's sophisticated uncertainty framework
3. **Cross-Modal Environments**: Uses graph/table/vector data to create rich simulation environments
4. **Empirical Validation**: Built-in validation against real behavioral data

## Consequences

### Positive Consequences

1. **Complete Research Platform**: KGAS becomes analysis + validation platform
2. **Theory Testing Capability**: Researchers can test theories through controlled experiments
3. **Synthetic Data Generation**: Generate realistic social science data for training/testing
4. **Academic Impact**: Positions KGAS at forefront of computational social science
5. **Validation Evidence**: Built-in validation against real psychological/behavioral data

### Challenges

1. **Complexity Increase**: ABM adds significant architectural complexity
2. **Resource Requirements**: Simulations are computationally intensive
3. **Validation Complexity**: Ensuring simulation realism requires sophisticated validation
4. **Development Time**: ABM integration requires substantial development effort

### Risk Mitigation

1. **Phased Implementation**: Start with simple theory-agent translation, add complexity gradually
2. **Validation-First Approach**: Use COVID dataset validation to ensure realism from start
3. **Resource Management**: Implement intelligent resource allocation for simulations
4. **Academic Partnerships**: Collaborate with ABM researchers for domain expertise

## Implementation Phases

### Phase 1: Foundation (Months 1-3)
- Basic theory-to-agent translation
- Simple simulation engine integration
- COVID dataset validation framework

### Phase 2: Cross-Modal Integration (Months 4-6)
- Cross-modal environment generation
- Uncertainty-aware simulation
- Empirical validation automation

### Phase 3: Advanced Capabilities (Months 7-12)
- Counterfactual exploration tools
- Synthetic data generation
- Emergent behavior detection
- Academic publication support

## Alternatives Considered

### Alternative 1: External ABM Integration
**Approach**: Integrate with existing ABM platforms (NetLogo, MASON)
**Rejected Because**: 
- Traditional ABM lacks LLM-based agent sophistication
- Integration complexity without GABM benefits
- No theory-driven parameterization capability

### Alternative 2: Pure Analytical Focus
**Approach**: Keep KGAS purely analytical, no simulation
**Rejected Because**:
- Misses opportunity to validate theories through simulation
- Limits research impact and publication opportunities
- Doesn't leverage full potential of theory operationalization

### Alternative 3: Separate ABM Platform
**Approach**: Build separate ABM platform, integrate via API
**Rejected Because**:
- Loses integration benefits with uncertainty framework
- Duplicates architecture and increases maintenance
- Fragments user experience across platforms

## KGAS Theory Meta-Schema v10 to ABM Translation

Based on analysis of your theory meta-schema v10 structure and examples (Stakeholder Theory v10.json, Carter Framing Analysis YAML), here's how KGAS theories directly map to ABM agents:

### Theory Schema → Agent Behavioral Rules Mapping

**From Stakeholder Theory Schema:**
```python
# Mitchell-Agle-Wood Salience Algorithm → Agent Behavioral Rule
salience_rule = BehavioralRule(
    rule_id="stakeholder_priority_response",
    behavioral_tendency="priority_response = (legitimacy * urgency * power) ** (1/3)",
    custom_script=theory_schema['execution']['analysis_steps'][4]['custom_script'],
    test_cases=theory_schema['validation']['theory_tests'],
    operationalization=theory_schema['validation']['operationalization_notes']
)
```

**From Carter Framing Theory Analysis:**
```python
# Frame Competition Mechanism → Agent Decision Process
frame_competition_rule = BehavioralRule(
    rule_id="frame_competition_response",
    behavioral_tendency="""
    frame_strength = cultural_resonance * logical_coherence * source_credibility
    response_probability = sigmoid(dominant_frame_strength - competing_frame_strength)
    """,
    psychological_mechanisms=['accessibility', 'availability', 'applicability'],
    causal_analysis=carter_schema['causal_analysis']['competitive_dynamics']
)
```

### Theory Operationalization → Agent Measurement Sensitivity

**From Stakeholder Theory Legitimacy Property:**
```python
# Operationalization boundaries → Agent assessment patterns
legitimacy_assessment = MeasurementApproach(
    boundary_rules=theory_schema['ontology']['entities'][0]['properties'][0]['operationalization']['boundary_rules'],
    # {"condition": "legal_right == true", "legitimacy": 0.8}
    # {"condition": "moral_claim == true", "legitimacy": 0.6}
    validation_examples=theory_schema['validation']['theory_tests'],
    fuzzy_boundaries=True
)
```

### Theory Execution Steps → Agent Decision Framework

**From Stakeholder Theory Analysis Steps:**
```python
# LLM extraction prompts → Agent reasoning processes
stakeholder_identification = ReasoningProcess(
    reasoning_prompt=theory_schema['execution']['analysis_steps'][0]['llm_prompts']['extraction_prompt'],
    validation_prompt=theory_schema['execution']['analysis_steps'][0]['llm_prompts']['validation_prompt'],
    confidence_thresholds=theory_schema['execution']['analysis_steps'][0]['uncertainty_handling']['confidence_thresholds']
)
```

### Cross-Modal Mappings → Agent Environment Integration

**From Theory Cross-Modal Specifications:**
```python
# Cross-modal mappings → Agent environment understanding
agent_environment_mapping = {
    'graph_mode': theory_schema['execution']['cross_modal_mappings']['graph_representation'],
    'table_mode': theory_schema['execution']['cross_modal_mappings']['table_representation'], 
    'vector_mode': theory_schema['execution']['cross_modal_mappings']['vector_representation']
}
```

### Key Insights from Schema Analysis

1. **Rich Operationalization**: Your v10 schemas contain detailed operationalization with boundary rules, validation examples, and confidence thresholds - perfect for agent parameterization
2. **Executable Algorithms**: Custom scripts (like Mitchell-Agle-Wood salience) can be directly implemented as agent behavioral algorithms
3. **LLM Prompts Ready**: Extraction and validation prompts can be repurposed as agent reasoning templates
4. **Validation Framework**: Theory tests provide ready-made validation scenarios for agent behavior
5. **Cross-Modal Support**: Agents can naturally work across graph/table/vector modes using your mappings

### Theory-Agent Translation Pipeline

```python
class KGASTheoryToAgentPipeline:
    """Complete pipeline for translating v10 schemas to ABM agents"""
    
    def translate_theory_schema(self, theory_schema_path: str, 
                              covid_dataset: CovidDataset) -> List[KGASTheoryDrivenAgent]:
        
        # Step 1: Parse theory schema
        theory_schema = self.load_theory_schema(theory_schema_path)
        
        # Step 2: Create agent population from COVID dataset
        agent_profiles = self.create_agent_profiles_from_covid_data(
            covid_dataset, theory_schema
        )
        
        # Step 3: Translate schema to agent behavioral components
        behavioral_rules = self.extract_behavioral_rules(theory_schema)
        decision_framework = self.create_decision_framework(theory_schema['execution'])
        measurement_approaches = self.extract_measurement_approaches(theory_schema['ontology'])
        
        # Step 4: Create theory-driven agents
        agents = []
        for profile in agent_profiles:
            agent = KGASTheoryDrivenAgent(
                theory_schema=theory_schema,
                agent_profile=profile,
                behavioral_rules=behavioral_rules,
                decision_framework=decision_framework,
                measurement_approaches=measurement_approaches
            )
            agents.append(agent)
        
        return agents
```

This translation framework demonstrates that your sophisticated theory meta-schema v10 already contains all the components needed for creating behaviorally accurate ABM agents - operationalization details, measurement approaches, validation frameworks, executable algorithms, and even specific LLM prompts.

## Success Metrics

### Technical Metrics
1. **Simulation Performance**: Able to run 1000+ agent simulations within reasonable time
2. **Validation Accuracy**: >0.75 correlation with COVID dataset behavioral patterns
3. **Theory Coverage**: Support for major social science theories (>10 theory domains)
4. **Uncertainty Propagation**: Accurate uncertainty tracking through simulation pipelines

### Research Impact Metrics
1. **Academic Publications**: Enable 5+ publications in computational social science venues
2. **User Adoption**: 100+ researchers using ABM capabilities within 18 months
3. **Theory Validation**: Successful validation of 20+ existing social science theories
4. **Synthetic Data Quality**: Generated data indistinguishable from real data in blind tests

### Platform Integration Metrics
1. **Cross-Modal Utilization**: ABM uses all three data modes (graph/table/vector)
2. **Tool Ecosystem**: ABM tools integrate seamlessly with existing 121+ tools
3. **Workflow Integration**: ABM accessible through all three agent interface layers
4. **Provenance Tracking**: Complete audit trails for all simulation operations

## Conclusion

Integrating Agent-Based Modeling capabilities into KGAS represents a strategic evolution from a descriptive analysis platform to a complete theory validation and synthetic experimentation platform. The combination of KGAS's theory operationalization, uncertainty framework, and cross-modal analysis with GABM's generative simulation capabilities creates a unique and powerful platform for computational social science research.

The availability of the COVID conspiracy theory dataset for validation provides immediate capability to demonstrate ABM effectiveness, while the sophisticated theoretical foundation of KGAS ensures that simulations are grounded in rigorous academic theory rather than ad-hoc assumptions.

This integration positions KGAS as a next-generation research platform that can both analyze existing social phenomena and validate theoretical understanding through controlled simulation experiments.

================================================================================

## 16. ADR-021-Statistical-Analysis-Integration.md

**Source**: `docs/architecture/adrs/ADR-021-Statistical-Analysis-Integration.md`

---

# ADR-021: Statistical Analysis and SEM Integration

**Status**: Accepted  
**Date**: 2025-01-23  
**Context**: KGAS currently lacks comprehensive statistical analysis capabilities, particularly Structural Equation Modeling (SEM) and advanced multivariate analysis tools needed for rigorous quantitative research

## Context

KGAS is designed as a theory-aware computational social science platform with strong capabilities in:
- Cross-modal analysis (graph/table/vector)
- Theory operationalization through schemas
- Network and graph analytics
- Uncertainty quantification

However, the current architecture has **limited statistical analysis capabilities**:
- Only basic descriptive statistics planned (T41 - not implemented)
- Only correlation analysis documented (T42 - not implemented)
- **No SEM capabilities** whatsoever
- Missing multivariate analysis tools
- No regression modeling framework
- No experimental design tools

For comprehensive quantitative research, particularly in social sciences, advanced statistical capabilities including SEM are essential for:
- Testing theoretical models with latent variables
- Analyzing complex causal relationships
- Validating measurement instruments
- Conducting multivariate hypothesis testing
- Performing meta-analyses and systematic reviews

## Decision

**Integrate comprehensive statistical analysis capabilities including SEM into KGAS, leveraging the cross-modal architecture to enable novel statistical-network-semantic integrated analyses.**

## Architecture Design

### 1. Statistical Analysis Service Layer

Add statistical capabilities as a new service in the Core Services Layer:

```python
class StatisticalModelingService:
    """Comprehensive statistical analysis service including SEM"""
    
    def __init__(self, data_service, theory_repository, cross_modal_converter):
        self.data_service = data_service
        self.theory_repository = theory_repository
        self.cross_modal_converter = cross_modal_converter
        
        # Statistical engines
        self.descriptive_engine = DescriptiveStatsEngine()
        self.inferential_engine = InferentialStatsEngine()
        self.sem_engine = SEMEngine()
        self.multivariate_engine = MultivariateAnalysisEngine()
        self.experimental_design = ExperimentalDesignEngine()
    
    async def run_sem_analysis(self, theory_schema: Dict, data: DataFrame) -> SEMResults:
        """Run SEM analysis based on theory specification"""
        # Convert theory schema to SEM specification
        sem_spec = self._theory_to_sem_specification(theory_schema)
        
        # Fit SEM model
        model_results = await self.sem_engine.fit_model(data, sem_spec)
        
        # Convert results to cross-modal format
        return self._create_cross_modal_results(model_results)
    
    def _theory_to_sem_specification(self, theory_schema: Dict) -> SEMSpecification:
        """Convert KGAS theory schema to SEM model specification"""
        return SEMSpecification(
            latent_variables=self._extract_latent_constructs(theory_schema),
            measurement_model=self._build_measurement_model(theory_schema),
            structural_model=self._build_structural_model(theory_schema),
            constraints=self._extract_model_constraints(theory_schema)
        )
```

### 2. Statistical Tool Ecosystem (T43-T60)

Expand the tool ecosystem with comprehensive statistical capabilities:

```python
# Basic Statistical Tools (T43-T45)
class T43_DescriptiveStatistics(KGASTool):
    """Comprehensive descriptive statistics including distribution analysis"""
    capabilities = ["mean", "median", "std", "variance", "skewness", "kurtosis", 
                   "percentiles", "iqr", "distribution_tests"]
    
class T44_CorrelationAnalysis(KGASTool):
    """Advanced correlation analysis including partial correlations"""
    capabilities = ["pearson", "spearman", "kendall", "partial", "polychoric", 
                   "point_biserial", "correlation_matrix", "significance_tests"]
    
class T45_RegressionAnalysis(KGASTool):
    """Regression modeling including GLM and mixed effects"""
    capabilities = ["linear", "logistic", "poisson", "mixed_effects", 
                   "hierarchical", "robust", "regularized"]

# SEM and Factor Analysis Tools (T46-T48)
class T46_StructuralEquationModeling(KGASTool):
    """Full SEM capabilities including measurement and structural models"""
    
    def __init__(self):
        self.engines = {
            'python': SEMopyEngine(),      # Pure Python implementation
            'r': LavaanEngine(),           # R integration via rpy2
            'mixed': HybridSEMEngine()     # Best of both
        }
    
    async def fit_sem_model(self, data: DataFrame, specification: Union[str, Dict]) -> SEMResults:
        """Fit SEM model with theory-driven or manual specification"""
        if isinstance(specification, Dict):
            # Theory-driven specification
            sem_spec = self._parse_theory_specification(specification)
        else:
            # Manual lavaan-style specification
            sem_spec = self._parse_lavaan_syntax(specification)
        
        # Fit model with selected engine
        results = await self.engines['mixed'].fit(data, sem_spec)
        
        # Add cross-modal representations
        results.graph_representation = self._sem_to_graph(results)
        results.path_diagram = self._generate_path_diagram(results)
        
        return results
    
class T47_FactorAnalysis(KGASTool):
    """Exploratory and confirmatory factor analysis"""
    capabilities = ["efa", "cfa", "pca", "factor_rotation", "factor_scores", 
                   "measurement_invariance", "reliability_analysis"]
    
class T48_LatentVariableModeling(KGASTool):
    """Advanced latent variable techniques"""
    capabilities = ["latent_class", "latent_profile", "mixture_models", 
                   "item_response_theory", "multilevel_sem"]

# Multivariate Analysis Tools (T49-T52)
class T49_MultivariateAnalysis(KGASTool):
    """Comprehensive multivariate statistical methods"""
    capabilities = ["manova", "discriminant_analysis", "canonical_correlation", 
                   "multidimensional_scaling", "correspondence_analysis"]
    
class T50_ClusterAnalysis(KGASTool):
    """Statistical clustering methods"""
    capabilities = ["hierarchical", "kmeans", "dbscan", "gaussian_mixture", 
                   "spectral", "cluster_validation"]
    
class T51_TimeSeriesAnalysis(KGASTool):
    """Time series statistical analysis"""
    capabilities = ["arima", "var", "state_space", "structural_breaks", 
                   "cointegration", "granger_causality"]
    
class T52_SurvivalAnalysis(KGASTool):
    """Survival and event history analysis"""
    capabilities = ["kaplan_meier", "cox_regression", "parametric_survival", 
                   "competing_risks", "recurrent_events"]

# Experimental Design Tools (T53-T55)
class T53_ExperimentalDesign(KGASTool):
    """Design of experiments and power analysis"""
    capabilities = ["power_analysis", "sample_size", "factorial_design", 
                   "randomization", "blocking", "latin_squares"]
    
class T54_HypothesisTesting(KGASTool):
    """Comprehensive hypothesis testing framework"""
    capabilities = ["parametric_tests", "nonparametric_tests", "multiple_comparisons", 
                   "effect_sizes", "confidence_intervals", "bayesian_tests"]
    
class T55_MetaAnalysis(KGASTool):
    """Meta-analysis and systematic review tools"""
    capabilities = ["effect_size_aggregation", "heterogeneity_tests", 
                   "publication_bias", "forest_plots", "network_meta_analysis"]

# Advanced Statistical Modeling (T56-T58)
class T56_BayesianAnalysis(KGASTool):
    """Bayesian statistical modeling"""
    capabilities = ["mcmc", "variational_inference", "prior_specification", 
                   "posterior_analysis", "model_comparison", "bayesian_sem"]
    
class T57_MachineLearningStats(KGASTool):
    """Statistical machine learning methods"""
    capabilities = ["regularization", "cross_validation", "feature_selection", 
                   "ensemble_methods", "interpretable_ml"]
    
class T58_CausalInference(KGASTool):
    """Causal inference methods"""
    capabilities = ["propensity_scores", "instrumental_variables", "regression_discontinuity", 
                   "difference_in_differences", "synthetic_controls", "dag_analysis"]

# Integration Tools (T59-T60)
class T59_StatisticalReporting(KGASTool):
    """Automated statistical reporting and visualization"""
    capabilities = ["apa_tables", "publication_figures", "dynamic_reports", 
                   "interactive_dashboards", "latex_output"]
    
class T60_CrossModalStatistics(KGASTool):
    """Integration of statistical results with graph/vector analysis"""
    capabilities = ["stats_to_graph", "network_regression", "graph_informed_sem", 
                   "vector_enhanced_clustering", "multimodal_hypothesis_tests"]
```

### 3. SEM Engine Implementation

Detailed SEM engine with theory integration:

```python
class SEMEngine:
    """Structural Equation Modeling engine with theory integration"""
    
    def __init__(self):
        self.lavaan_bridge = LavaanBridge()  # R lavaan via rpy2
        self.semopy_engine = SemopyEngine()   # Pure Python
        self.model_validator = SEMValidator()
        self.theory_mapper = TheoryToSEMMapper()
    
    async def fit_model(self, data: DataFrame, specification: SEMSpecification) -> SEMResults:
        """Fit SEM model with comprehensive diagnostics"""
        
        # Validate specification
        validation = self.model_validator.validate_specification(specification, data)
        if not validation.is_valid:
            raise SEMSpecificationError(validation.errors)
        
        # Choose optimal engine based on model complexity
        if specification.requires_advanced_features():
            results = await self.lavaan_bridge.fit(data, specification)
        else:
            results = await self.semopy_engine.fit(data, specification)
        
        # Enhance results with diagnostics
        results.fit_indices = self._calculate_fit_indices(results)
        results.modification_indices = self._calculate_modification_indices(results)
        results.bootstrap_ci = await self._bootstrap_confidence_intervals(results, data)
        
        # Add cross-modal representations
        results.path_diagram = self._generate_path_diagram(results)
        results.graph_representation = self._create_graph_representation(results)
        
        return results
    
    def _calculate_fit_indices(self, results: RawSEMResults) -> FitIndices:
        """Calculate comprehensive fit indices"""
        return FitIndices(
            chi_square=results.chi_square,
            cfi=results.cfi,
            tli=results.tli,
            rmsea=results.rmsea,
            srmr=results.srmr,
            aic=results.aic,
            bic=results.bic,
            # Additional indices
            gfi=self._calculate_gfi(results),
            agfi=self._calculate_agfi(results),
            nfi=self._calculate_nfi(results),
            ifi=self._calculate_ifi(results)
        )
    
    def _create_graph_representation(self, sem_results: SEMResults) -> nx.DiGraph:
        """Convert SEM results to graph representation"""
        graph = nx.DiGraph()
        
        # Add latent variables as special nodes
        for latent in sem_results.latent_variables:
            graph.add_node(latent.name, 
                         node_type='latent',
                         variance=latent.variance,
                         node_color='lightblue')
        
        # Add manifest variables
        for manifest in sem_results.manifest_variables:
            graph.add_node(manifest.name,
                         node_type='manifest',
                         mean=manifest.mean,
                         variance=manifest.variance,
                         node_color='lightgreen')
        
        # Add measurement model edges
        for loading in sem_results.factor_loadings:
            graph.add_edge(loading.latent, loading.manifest,
                         edge_type='measurement',
                         loading=loading.estimate,
                         std_error=loading.std_error,
                         p_value=loading.p_value,
                         edge_style='dashed')
        
        # Add structural model edges
        for path in sem_results.structural_paths:
            graph.add_edge(path.from_var, path.to_var,
                         edge_type='structural',
                         coefficient=path.estimate,
                         std_error=path.std_error,
                         p_value=path.p_value,
                         edge_style='solid')
        
        return graph
```

### 4. Theory-Driven Statistical Specification

Extend theory meta-schema v10 for statistical models:

```python
class TheoryToSEMMapper:
    """Map KGAS theory schemas to SEM specifications"""
    
    def create_sem_from_theory(self, theory_schema: Dict) -> SEMSpecification:
        """Convert theory schema to SEM specification"""
        
        # Extract latent constructs from theory ontology
        latent_constructs = self._identify_latent_constructs(
            theory_schema['ontology']['entities']
        )
        
        # Build measurement model from operationalizations
        measurement_model = self._build_measurement_model(
            theory_schema['ontology']['entities'],
            theory_schema.get('statistical_operationalization', {})
        )
        
        # Build structural model from relationships
        structural_model = self._build_structural_model(
            theory_schema['ontology']['relationships'],
            theory_schema.get('causal_pathways', {})
        )
        
        # Extract constraints from validation rules
        constraints = self._extract_constraints(
            theory_schema.get('validation', {})
        )
        
        return SEMSpecification(
            model_name=f"{theory_schema['theory_id']}_sem",
            measurement_model=measurement_model,
            structural_model=structural_model,
            constraints=constraints,
            theory_metadata=theory_schema
        )
```

### 5. Cross-Modal Statistical Integration

Enable statistical results to flow through cross-modal analysis:

```python
class CrossModalStatisticalConverter:
    """Convert statistical results to graph/vector representations"""
    
    def sem_to_graph(self, sem_results: SEMResults) -> nx.DiGraph:
        """Convert SEM results to analyzable graph"""
        # Implementation shown above in SEMEngine
        
    def correlation_matrix_to_graph(self, corr_matrix: DataFrame, 
                                   threshold: float = 0.3) -> nx.Graph:
        """Convert correlation matrix to network"""
        graph = nx.Graph()
        
        # Add nodes for each variable
        for var in corr_matrix.columns:
            graph.add_node(var)
        
        # Add edges for significant correlations
        for i, var1 in enumerate(corr_matrix.columns):
            for j, var2 in enumerate(corr_matrix.columns[i+1:], i+1):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > threshold:
                    graph.add_edge(var1, var2, 
                                 weight=corr,
                                 correlation=corr,
                                 edge_color='red' if corr < 0 else 'blue')
        
        return graph
    
    def factor_analysis_to_graph(self, factor_results: FactorAnalysisResults) -> nx.DiGraph:
        """Convert factor analysis to bipartite graph"""
        graph = nx.DiGraph()
        
        # Add factor nodes
        for factor in factor_results.factors:
            graph.add_node(f"Factor_{factor.id}", 
                         node_type='factor',
                         variance_explained=factor.variance_explained)
        
        # Add variable nodes and loadings
        for var in factor_results.variables:
            graph.add_node(var.name, node_type='observed')
            
            for loading in var.loadings:
                if abs(loading.value) > 0.3:  # Threshold for significant loadings
                    graph.add_edge(f"Factor_{loading.factor_id}", var.name,
                                 weight=loading.value,
                                 loading=loading.value)
        
        return graph
```

### 6. Statistical Workflow Integration

Integrate statistical analysis into KGAS workflows:

```python
class StatisticalWorkflow:
    """Orchestrate statistical analysis workflows"""
    
    def __init__(self, orchestrator: PipelineOrchestrator):
        self.orchestrator = orchestrator
        self.statistical_service = StatisticalModelingService()
        self.cross_modal_service = CrossModalService()
    
    async def theory_driven_sem_workflow(self, theory_id: str, data_source: str):
        """Complete workflow from theory to SEM results"""
        
        # Load theory schema
        theory = await self.orchestrator.theory_repository.get_theory(theory_id)
        
        # Load and prepare data
        data = await self.orchestrator.load_data(data_source)
        
        # Generate SEM specification from theory
        sem_spec = self.statistical_service.theory_to_sem_specification(theory)
        
        # Fit SEM model
        sem_results = await self.statistical_service.run_sem_analysis(sem_spec, data)
        
        # Convert to cross-modal representations
        graph_repr = self.cross_modal_service.sem_to_graph(sem_results)
        vector_repr = self.cross_modal_service.sem_to_embeddings(sem_results)
        
        # Run additional analyses on graph representation
        network_metrics = await self.orchestrator.graph_service.analyze_sem_network(graph_repr)
        
        # Generate integrated report
        return IntegratedStatisticalReport(
            sem_results=sem_results,
            network_analysis=network_metrics,
            cross_modal_insights=self._integrate_insights(sem_results, network_metrics),
            visualization_data=self._prepare_visualizations(sem_results, graph_repr)
        )
```

## Integration with Existing Architecture

### 1. Service Layer Integration

```python
# Add to Core Services Layer
statistical_service = StatisticalModelingService(
    data_service=existing_data_service,
    theory_repository=existing_theory_repository,
    cross_modal_converter=existing_converter
)

# Register with service manager
service_manager.register_service('statistical_modeling', statistical_service)
```

### 2. Data Architecture Extension

```sql
-- SQLite: Statistical model metadata
CREATE TABLE statistical_models (
    model_id TEXT PRIMARY KEY,
    model_type TEXT,  -- 'sem', 'regression', 'factor_analysis', etc.
    theory_id TEXT,
    specification JSON,
    creation_time TIMESTAMP,
    last_run TIMESTAMP
);

CREATE TABLE statistical_results (
    result_id TEXT PRIMARY KEY,
    model_id TEXT,
    fit_indices JSON,
    parameters JSON,
    diagnostics JSON,
    cross_modal_representations JSON,
    execution_time REAL,
    created_at TIMESTAMP
);
```

```cypher
-- Neo4j: Statistical model as graph
CREATE (:LatentVariable {
    name: string,
    model_id: string,
    variance: float,
    mean: float
})

CREATE (:ManifestVariable {
    name: string,
    model_id: string,
    observed_mean: float,
    observed_variance: float
})

CREATE (:LatentVariable)-[:MEASURES {
    loading: float,
    std_error: float,
    p_value: float
}]->(:ManifestVariable)

CREATE (:LatentVariable)-[:INFLUENCES {
    coefficient: float,
    std_error: float,
    p_value: float
}]->(:LatentVariable)
```

### 3. Theory Schema Extension

Add statistical specifications to theory meta-schema v10:

```json
{
  "theory_id": "example_theory",
  "statistical_models": {
    "primary_sem": {
      "latent_variables": [
        {
          "name": "satisfaction",
          "indicators": ["sat1", "sat2", "sat3"],
          "scale_identification": "first_loading_fixed"
        }
      ],
      "structural_paths": [
        {
          "from": "legitimacy",
          "to": "satisfaction",
          "hypothesis": "positive",
          "expected_range": [0.3, 0.7]
        }
      ],
      "model_constraints": [
        "covariance(error.sat1, error.sat2) = 0"
      ],
      "fit_criteria": {
        "cfi": ">= 0.95",
        "rmsea": "<= 0.06",
        "srmr": "<= 0.08"
      }
    }
  }
}
```

## Rationale

### Why Statistical Integration Is Critical

1. **Research Completeness**: Advanced statistics including SEM are essential for rigorous quantitative research
2. **Theory Validation**: SEM directly tests theoretical models with latent constructs
3. **Cross-Modal Innovation**: Converting statistical models to graphs enables novel analyses
4. **Academic Standards**: Meets publication requirements for statistical rigor
5. **Competitive Advantage**: Few platforms integrate advanced statistics with graph/semantic analysis

### Why This Architecture Works

1. **Leverages Existing Strengths**: Cross-modal architecture naturally handles statistical-to-graph conversion
2. **Theory Integration**: Theory schemas can specify statistical models directly
3. **Service Architecture**: Clean integration without disrupting existing components
4. **Tool Ecosystem**: Fits naturally into T43-T60 tool range
5. **Academic Focus**: Aligns with KGAS's research-oriented design

### Technical Advantages

1. **Best-of-Breed Libraries**: Leverage lavaan (R) and semopy (Python)
2. **Cross-Modal Innovation**: Statistical results become graph structures for network analysis
3. **Theory-Driven Automation**: Generate SEM models from theory specifications
4. **Comprehensive Coverage**: From basic descriptives to advanced SEM and Bayesian methods
5. **Uncertainty Integration**: Statistical uncertainty flows through cross-modal transformations

## Consequences

### Positive Consequences

1. **Complete Research Platform**: KGAS becomes comprehensive quantitative + qualitative platform
2. **Novel Research Methods**: Cross-modal statistics enables new analytical approaches
3. **Publication Ready**: Outputs meet academic statistical reporting standards
4. **Theory Testing**: Direct statistical validation of theoretical models
5. **Integrated Insights**: Statistical findings enhance network and semantic analyses

### Implementation Considerations

1. **Development Effort**: Significant but manageable with phased approach
2. **Performance**: Large statistical models may require optimization
3. **Expertise Required**: Need statistical expertise for proper implementation
4. **Testing Complexity**: Statistical methods require extensive validation
5. **Documentation**: Comprehensive statistical documentation needed

### Risk Mitigation

1. **Phased Implementation**: Start with basic statistics, add complexity gradually
2. **Library Reuse**: Leverage proven statistical libraries rather than reimplementing
3. **Expert Review**: Collaborate with statisticians for validation
4. **Comprehensive Testing**: Use standard statistical test suites
5. **Performance Optimization**: Implement caching and parallel processing

## Implementation Phases

### Phase 1: Foundation (Months 1-2)
- Basic descriptive statistics (T43)
- Correlation analysis (T44)
- Simple regression (T45)
- Cross-modal correlation networks

### Phase 2: SEM Core (Months 2-4)
- SEM engine implementation (T46)
- Factor analysis (T47)
- Theory-to-SEM mapping
- Path diagram generation

### Phase 3: Advanced Methods (Months 4-6)
- Multivariate analysis suite (T49-T52)
- Experimental design tools (T53-T55)
- Bayesian methods (T56)
- Full workflow integration

### Phase 4: Innovation (Months 6-8)
- Cross-modal statistical insights (T60)
- Graph-informed SEM
- Statistical network analysis
- Publication-ready outputs

## Success Metrics

### Technical Metrics
1. **Coverage**: Support for 95% of common statistical methods
2. **Performance**: SEM models with 100+ variables in <60 seconds
3. **Accuracy**: Match R/SPSS output within numerical precision
4. **Integration**: All statistical results available in graph/table/vector formats

### Research Impact Metrics
1. **User Adoption**: 80% of users utilize statistical features
2. **Publication Support**: Enable 50+ publications using KGAS statistics
3. **Novel Methods**: 5+ new cross-modal statistical methods published
4. **Theory Validation**: 100+ theories tested via integrated SEM

### Platform Integration Metrics
1. **Workflow Integration**: Statistical tools in 90% of analysis workflows
2. **Cross-Modal Usage**: 70% of statistical results converted to graphs
3. **Theory-Driven Models**: 60% of SEM models generated from theory schemas
4. **Uncertainty Propagation**: Statistical uncertainty tracked through all transformations

## Conclusion

Integrating comprehensive statistical analysis capabilities including SEM into KGAS is not only feasible but strategically essential. The cross-modal architecture provides a unique foundation for innovative statistical-network-semantic integrated analyses that would be difficult to achieve in traditional statistical packages.

This integration transforms KGAS from a primarily graph-focused platform into a comprehensive quantitative research environment that maintains its unique theory-aware, cross-modal advantages while meeting the rigorous statistical requirements of academic research.

The ability to automatically generate SEM models from theory schemas, convert statistical results to graph structures, and perform network analysis on statistical relationships positions KGAS as a next-generation research platform that bridges traditionally separate analytical paradigms.

================================================================================

## 17. master-concept-library.md

**Source**: `docs/architecture/concepts/master-concept-library.md`

---

---
status: living
---

# Master Concept Library: Standardized Vocabulary for KGAS

## Purpose

The Master Concept Library (MCL) is a machine-readable, extensible repository of standardized concepts (entities, connections, properties, modifiers) from social, behavioral, and communication science. It ensures semantic precision and cross-theory comparability in all KGAS analyses.

## Structure

- **EntityConcept**: Actors, groups, organizations, etc.
- **ConnectionConcept**: Relationships between entities (e.g., “identifies_with”)
- **PropertyConcept**: Attributes of entities or connections (e.g., “credibility_score”)
- **ModifierConcept**: Qualifiers or contextualizers (e.g., “temporal”, “certainty”)

## Mapping Process

1. **LLM Extraction**: Indigenous terms are extracted from text.
2. **Standardization**: Terms are mapped to canonical names in the MCL.
3. **Human-in-the-Loop**: Novel terms are reviewed and added as needed.

## Schema Specification

### EntityConcept Schema
```json
{
  "type": "EntityConcept",
  "canonical_name": "string",
  "description": "string",
  "upper_parent": "dolce:IRI",
  "subtypes": ["string"],
  "properties": ["PropertyConcept"],
  "connections": ["ConnectionConcept"],
  "bridge_links": ["external:IRI"],
  "version": "semver",
  "created_at": "timestamp",
  "validated_by": "string"
}
```

### ConnectionConcept Schema
```json
{
  "type": "ConnectionConcept", 
  "canonical_name": "string",
  "description": "string",
  "upper_parent": "dolce:Relation",
  "domain": "EntityConcept",
  "range": "EntityConcept",
  "properties": ["PropertyConcept"],
  "directional": "boolean",
  "validation_rules": ["rule"]
}
```

### PropertyConcept Schema
```json
{
  "type": "PropertyConcept",
  "canonical_name": "string", 
  "description": "string",
  "value_type": "numeric|categorical|boolean|text",
  "scale": "nominal|ordinal|interval|ratio",
  "valid_values": ["value"],
  "measurement_unit": "string",
  "uncertainty_type": "stochastic|epistemic|systematic"
}
```

## Implementation Details

### Storage and Access
- **Code Location:** `/src/ontology_library/mcl/__init__.py`
- **Schema Enforcement:** Pydantic models with JSON Schema validation
- **Database Storage:** Neo4j graph with concept relationships
- **API Endpoints:** RESTful API for concept CRUD operations
- **Integration:** Used in all theory schemas and extraction pipelines

### Validation Pipeline
```python
class MCLValidator:
    """Validates concepts against MCL standards"""
    
    def validate_concept(self, concept: ConceptDict) -> ValidationResult:
        # 1. Schema validation
        # 2. DOLCE alignment check
        # 3. Duplicate detection
        # 4. Cross-reference validation
        # 5. Semantic consistency check
```

### API Operations
```python
# Core MCL operations
mcl.add_concept(concept_data, validate=True)
mcl.get_concept(canonical_name)
mcl.search_concepts(query, filters={})
mcl.map_term_to_concept(indigenous_term)
mcl.validate_theory_schema(schema)
```

## Detailed Examples

### Production Theory Integration Example
**See**: [MCL Theory Schemas - Implementation Examples](../data/mcl-theory-schemas-examples.md) for complete production theory integrations including Cognitive Dissonance Theory, Prospect Theory, and Social Identity Theory.

### Entity Concept Example
**Indigenous term:** "grassroots organizer"
```json
{
  "type": "EntityConcept",
  "canonical_name": "CommunityOrganizer",
  "description": "Individual who mobilizes community members for collective action",
  "upper_parent": "dolce:SocialAgent",
  "subtypes": ["GrassrootsOrganizer", "PolicyOrganizer"],
  "properties": ["influence_level", "network_size", "expertise_domain"],
  "connections": ["mobilizes", "coordinates_with", "represents"],
  "indigenous_terms": ["grassroots organizer", "community leader", "activist"],
  "theory_sources": ["Social Identity Theory", "Social Cognitive Theory"],
  "validation_status": "production_ready"
}
```

### Connection Concept Example  
**Indigenous term:** "influences public opinion"
```json
{
  "type": "ConnectionConcept",
  "canonical_name": "influences_opinion",
  "description": "Causal relationship where entity affects public perception",
  "domain": "SocialAgent",
  "range": "PublicOpinion", 
  "properties": ["influence_strength", "temporal_duration"],
  "directional": true,
  "validation_rules": ["requires_evidence_source", "measurable_outcome"]
}
```

### Property Concept Example
**Indigenous term:** "credibility"
```json
{
  "type": "PropertyConcept",
  "canonical_name": "credibility_score",
  "description": "Perceived trustworthiness and reliability measure",
  "value_type": "numeric",
  "scale": "interval", 
  "valid_values": [0.0, 10.0],
  "measurement_unit": "likert_scale",
  "uncertainty_type": "stochastic"
}
```

## DOLCE Alignment Procedures

### Automated Alignment Process
```python
class DOLCEAligner:
    """Automatically aligns new concepts with DOLCE upper ontology"""
    
    def align_concept(self, concept: NewConcept) -> DOLCEAlignment:
        # 1. Semantic similarity analysis
        # 2. Definition matching against DOLCE taxonomy
        # 3. Structural constraint checking
        # 4. Expert review recommendation
        # 5. Alignment confidence score
```

### DOLCE Classification Rules
| Concept Type | DOLCE Parent | Validation Rules |
|--------------|--------------|------------------|
| **Physical Entity** | `dolce:PhysicalObject` | Must have spatial location |
| **Social Entity** | `dolce:SocialObject` | Must involve multiple agents |
| **Abstract Entity** | `dolce:AbstractObject` | Must be non-spatial |
| **Relationship** | `dolce:Relation` | Must connect two entities |
| **Property** | `dolce:Quality` | Must be measurable attribute |

### Quality Assurance Framework
```python
class ConceptQualityValidator:
    """Ensures MCL concept quality and consistency"""
    
    quality_checks = [
        "semantic_precision",      # Clear, unambiguous definition
        "dolce_consistency",       # Proper upper ontology alignment  
        "cross_reference_validity", # Valid concept connections
        "measurement_clarity",     # Clear measurement procedures
        "research_utility"         # Useful for social science research
    ]
```

## Extension Guidelines

### Adding New Concepts
1. **Research Validation**: Concept must appear in peer-reviewed literature
2. **Semantic Gap Analysis**: Must fill genuine gap in existing MCL
3. **DOLCE Alignment**: Must align with appropriate DOLCE parent class
4. **Community Review**: Subject to expert panel review process
5. **Integration Testing**: Must integrate cleanly with existing concepts

### Concept Evolution Procedures
```python
# Concept modification workflow
def evolve_concept(concept_name: str, changes: dict) -> EvolutionResult:
    # 1. Impact analysis on dependent concepts
    # 2. Backward compatibility assessment
    # 3. Migration path generation
    # 4. Validation test suite update
    # 5. Documentation synchronization
```

### Version Control and Migration
- **Semantic Versioning**: Major.Minor.Patch versioning for concept changes
- **Migration Scripts**: Automated concept evolution with data preservation
- **Rollback Procedures**: Safe rollback mechanisms for problematic changes
- **Change Documentation**: Complete audit trail for all concept modifications

## Extensibility Framework

The MCL grows systematically through:

### Research-Driven Expansion
- **Literature Integration**: New concepts from emerging research domains
- **Cross-Domain Synthesis**: Concepts spanning multiple social science fields
- **Methodological Innovation**: Concepts supporting novel analysis techniques

### Community Contribution Process
```markdown
1. **Concept Proposal**: Submit via GitHub issue with research justification
2. **Expert Review**: Panel evaluation for research merit and semantic precision
3. **Prototype Integration**: Test integration with existing concept ecosystem
4. **Community Validation**: Broader community review and feedback
5. **Production Integration**: Full integration with versioning and documentation
```

### Quality Metrics and Monitoring
- **Usage Analytics**: Track concept utilization across research projects
- **Semantic Drift Detection**: Monitor concept meaning stability over time  
- **Research Impact Assessment**: Evaluate contribution to research outcomes
- **Community Satisfaction**: Regular feedback collection from users

## Versioning Rules

| Change Type | Version Bump | Review Required | Documentation |
|-------------|--------------|-----------------|---------------|
| **Concept Addition** | Patch (x.y.z+1) | No | Update concept list |
| **Concept Modification** | Minor (x.y+1.0) | Yes | Update examples |
| **Schema Change** | Major (x+1.0.0) | Yes | Migration guide |
| **DOLCE Alignment** | Minor (x.y+1.0) | Yes | Alignment report |

### Concept Merge Policy
New concepts are merged via `scripts/mcl_merge.py` which:
- Validates against existing concepts
- Checks DOLCE alignment
- Updates cross-references
- Generates migration guide

## DOLCE and Bridge Links

### Upper Ontology Alignment
Every concept in the MCL is aligned with the DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering) upper ontology:

- **`upper_parent`**: IRI of the closest DOLCE superclass (e.g., `dolce:PhysicalObject`, `dolce:SocialObject`)
- **Semantic Precision**: Ensures ontological consistency across all concepts
- **Interoperability**: Enables integration with other DOLCE-aligned systems

### Bridge Links (Optional)
For enhanced interoperability, concepts may include:

- **`bridge_links`**: Array of IRIs linking to related concepts in external ontologies
- **Cross-Domain Mapping**: Connects social science concepts to domain-specific ontologies
- **Research Integration**: Enables collaboration with other research platforms -e 
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>


================================================================================

## 18. theory-meta-schema-v10.md

**Source**: `docs/architecture/data/theory-meta-schema-v10.md`

---

# Theory Meta-Schema v10.0: Executable Implementation Framework

**Purpose**: Comprehensive framework for representing executable social science theories

## Overview

Theory Meta-Schema v10.0 represents a major evolution from v9.0, incorporating practical implementation insights to bridge the gap between abstract theory and concrete execution. This version enables direct translation from theory schemas to executable workflows.

## Key Enhancements in v10.0

### 1. Execution Framework
- **Renamed `process` to `execution`** for clarity
- **Added implementation methods**: `llm_extraction`, `predefined_tool`, `custom_script`, `hybrid`
- **Embedded LLM prompts** directly in schema
- **Tool mapping strategy** with parameter adaptation
- **Custom script specifications** with test cases

### 2. Practical Implementation Support
- **Operationalization details** for concept boundaries
- **Cross-modal mappings** for graph/table/vector representations
- **Dynamic adaptation** for theories with changing processes
- **Uncertainty handling** at step level

### 3. Validation and Testing
- **Theory validation framework** with test cases
- **Operationalization documentation** for transparency
- **Boundary case specifications** for edge handling

### 4. Configuration Management
- **Configurable tracing levels** (minimal to debug)
- **LLM model selection** per task type
- **Performance optimization** flags
- **Fallback strategies** for error handling

## Schema Structure

### Core Required Fields
```json
{
  "theory_id": "stakeholder_theory",
  "theory_name": "Stakeholder Theory", 
  "version": "1.0.0",
  "classification": {...},
  "ontology": {...},
  "execution": {...},
  "telos": {...}
}
```

### Execution Framework Detail

#### Analysis Steps with Multiple Implementation Methods

**LLM Extraction Method**:
```json
{
  "step_id": "identify_stakeholders",
  "method": "llm_extraction",
  "llm_prompts": {
    "extraction_prompt": "Identify all entities that have a stake in the organization's decisions...",
    "validation_prompt": "Does this entity have legitimate interest, power, or urgency?"
  }
}
```

**Predefined Tool Method**:
```json
{
  "step_id": "calculate_centrality",
  "method": "predefined_tool",
  "tool_mapping": {
    "preferred_tool": "graph_centrality_mcp",
    "tool_parameters": {
      "centrality_type": "pagerank",
      "normalize": true
    },
    "parameter_adaptation": {
      "method": "wrapper_script",
      "adaptation_logic": "Convert stakeholder_salience to centrality weights"
    }
  }
}
```

**Custom Script Method**:
```json
{
  "step_id": "stakeholder_salience",
  "method": "custom_script",
  "custom_script": {
    "algorithm_name": "mitchell_agle_wood_salience",
    "business_logic": "Calculate geometric mean of legitimacy, urgency, and power",
    "implementation_hint": "salience = (legitimacy * urgency * power) ^ (1/3)",
    "inputs": {
      "legitimacy": {"type": "float", "range": [0,1]},
      "urgency": {"type": "float", "range": [0,1]}, 
      "power": {"type": "float", "range": [0,1]}
    },
    "outputs": {
      "salience_score": {"type": "float", "range": [0,1]}
    },
    "test_cases": [
      {
        "inputs": {"legitimacy": 1.0, "urgency": 1.0, "power": 1.0},
        "expected_output": 1.0,
        "description": "Maximum salience case"
      }
    ],
    "tool_contracts": ["stakeholder_interface", "salience_calculator"]
  }
}
```

### Cross-Modal Mappings

Specify how theory concepts map across different analysis modes:

```json
"cross_modal_mappings": {
  "graph_representation": {
    "nodes": "stakeholder_entities",
    "edges": "influence_relationships", 
    "node_properties": ["salience_score", "legitimacy", "urgency", "power"]
  },
  "table_representation": {
    "primary_table": "stakeholders",
    "key_columns": ["entity_id", "salience_score", "influence_rank"],
    "calculated_metrics": ["centrality_scores", "cluster_membership"]
  },
  "vector_representation": {
    "embedding_features": ["behavioral_patterns", "communication_style"],
    "similarity_metrics": ["stakeholder_type_similarity"]
  }
}
```

### Dynamic Adaptation (New Feature)

For theories like Spiral of Silence that change behavior based on state:

```json
"dynamic_adaptation": {
  "adaptation_triggers": [
    {"condition": "minority_visibility < 0.3", "action": "increase_spiral_strength"}
  ],
  "state_variables": {
    "minority_visibility": {"type": "float", "initial": 0.5},
    "spiral_strength": {"type": "float", "initial": 1.0}
  },
  "adaptation_rules": [
    "spiral_strength *= 1.2 when minority_visibility decreases"
  ]
}
```

### Validation Framework

```json
"validation": {
  "operationalization_notes": [
    "Legitimacy operationalized as stakeholder claim validity (0-1 scale)",
    "Power operationalized as ability to influence organizational decisions",
    "Urgency operationalized as time-critical nature of stakeholder claim"
  ],
  "theory_tests": [
    {
      "test_name": "high_salience_stakeholder_identification",
      "input_scenario": "CEO announces layoffs affecting employees and shareholders",
      "expected_theory_application": "Both employees and shareholders identified as high-salience stakeholders",
      "validation_criteria": "Salience scores > 0.7 for both groups"
    }
  ],
  "boundary_cases": [
    {
      "case_description": "Potential future stakeholder with no current relationship",
      "theory_applicability": "Mitchell model may not apply",
      "expected_behavior": "Flag as edge case, use alternative identification method"
    }
  ]
}
```

### Configuration Options

```json
"configuration": {
  "tracing_level": "standard",
  "llm_models": {
    "extraction": "gpt-4-turbo",
    "reasoning": "claude-3-opus", 
    "validation": "gpt-3.5-turbo"
  },
  "performance_optimization": {
    "enable_caching": true,
    "batch_processing": true,
    "parallel_execution": false
  },
  "fallback_strategies": {
    "missing_tools": "llm_implementation",
    "low_confidence": "human_review",
    "edge_cases": "uncertainty_flagging"
  }
}
```

## Migration from v9.0 to v10.0

### Breaking Changes
- `process` renamed to `execution`
- `steps` array structure enhanced with implementation methods
- New required fields: `method` in each step

### Migration Strategy
1. Rename `process` to `execution`
2. Add `method` field to each step 
3. Move prompts from separate files into `llm_prompts` objects
4. Add `custom_script` specifications for algorithms
5. Include `tool_mapping` for predefined tools

### Backward Compatibility
A migration tool will convert v9.0 schemas to v10.0 format:
- Default `method` to "llm_extraction" for existing steps
- Generate placeholder prompts from step descriptions
- Create basic tool mappings based on step naming

## Implementation Requirements

### For Theory Schema Authors
1. **Specify implementation method** for each analysis step
2. **Include LLM prompts** for extraction steps
3. **Define custom algorithms** with test cases for novel procedures
4. **Document operationalization decisions** in validation section

### For System Implementation
1. **Execution engine** that can dispatch to different implementation methods
2. **Custom script compiler** using Claude Code for algorithm implementation
3. **Tool mapper** using LLM intelligence for tool selection
4. **Validation framework** that runs theory tests automatically

### For Researchers
1. **Transparent operationalization** - all theory simplifications documented
2. **Configurable complexity** - adjust tracing and validation levels
3. **Extensible framework** - can add custom theories and algorithms
4. **Cross-modal capability** - theory works across graph, table, vector modes

## Next Steps

1. **Create example theory** using v10.0 schema (stakeholder theory)
2. **Implement execution engine** that can interpret v10.0 schemas
3. **Build validation framework** for theory testing
4. **Test stress cases** with complex multi-step theories

The v10.0 schema provides the comprehensive framework needed to bridge theory and implementation while maintaining flexibility and configurability.

## Security Architecture Requirements

### Rule Execution Security and Flexibility
- **Implementation**: DebuggableEvaluator with controlled eval() usage
- **Rationale**: Maintains maximum flexibility for academic research while enabling debugging
- **Approach**: 
  ```python
  class DebuggableEvaluator:
      def evaluate(self, expression, context, debug=False):
          if debug:
              wrapped_expr = f"import pdb; result = ({expression}); pdb.set_trace(); result"
          else:
              wrapped_expr = expression
          return eval(wrapped_expr, {"__builtins__": {}}, context)
  ```
- **Benefits**: 
  - Full Python flexibility for complex academic expressions
  - Real-time debugging with breakpoints and print statements
  - Support for custom research logic and numpy operations
- **Validation**: All rule execution must be sandboxed and validated

================================================================================

## 19. theory-meta-schema.md

**Source**: `docs/architecture/data/theory-meta-schema.md`

---

---
status: living
---

# Theory Meta-Schema: Operationalizing Social Science Theories in KGAS

![Meta-Schema v9.1 (JSON Schema draft-07)](https://img.shields.io/badge/Meta--Schema-v9.1-blue)

## Overview

The Theory Meta-Schema is the foundational innovation of the Knowledge Graph Analysis System (KGAS). It provides a standardized, computable framework for representing and applying diverse social science theories to discourse analysis. The goal is to move beyond data description to *theoretically informed, computable analysis*.

## Structure of the Theory Meta-Schema

Each Theory Meta-Schema instance is a structured document with the following components:

### 1. Theory Identity and Metadata
- `theory_id`: Unique identifier (e.g., `social_identity_theory`)
- `theory_name`: Human-readable name
- `authors`: Key theorists
- `publication_year`: Seminal publication date
- `domain_of_application`: Social contexts (e.g., “group dynamics”)
- `description`: Concise summary

**New in v9.1**  
• `mcl_id` – cross-link to Master Concept Library  
• `dolce_parent` – IRI of the DOLCE superclass for every entity  
• `ontology_alignment_strategy` – strategy for aligning with DOLCE ontology
• Tags now sit in `classification.domain` (`level`, `component`, `metatheory`)

### 2. Theoretical Classification (Three-Dimensional Framework)
- `level_of_analysis`: Micro (individual), Meso (group), Macro (society)
- `component_of_influence`: Who (Speaker), Whom (Receiver), What (Message), Channel, Effect
- `causal_metatheory`: Agentic, Structural, Interdependent

### 3. Computable Theoretical Core
- `ontology_specification`: Domain-specific concepts (entities, relationships, properties, modifiers) aligned with the Master Concept Library
- `axioms`: Core rules or assumptions (optional)
- `analytics`: Metrics or focal concepts (optional)
- `process`: Sequence of steps (sequential, iterative, workflow)
- `telos`: Analytical purpose, output format, and success criteria

### 4. Provenance
- `provenance`: {source_chunk_id: str, prompt_hash: str, model_id: str, timestamp: datetime}
  - Captures the lineage of each theory instance for audit and reproducibility.

## Implementation

- **Schema Location:** `/_schemas/theory_meta_schema_v10.json`
- **Validation:** Pydantic models with runtime verification
- **Integration:** CI/CD enforced contract compliance
- **Codegen**: dataclasses auto-generated into /src/contracts/generated/

## Example

See `docs/architecture/THEORETICAL_FRAMEWORK.md` for a worked example using Social Identity Theory.

## Changelog

### v9.0 → v9.1
- Added `ontology_alignment_strategy` field for DOLCE alignment
- Enhanced codegen support with auto-generated dataclasses
- Updated schema location to v9.1
- Improved validation and integration documentation
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>


================================================================================

## 20. theory_meta_schema_v10.json

**Source**: `docs/architecture/data/-schemas/theory_meta_schema_v10.json`

---

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Theory Meta-Schema v10.0",
  "description": "Comprehensive framework for representing executable social science theories with practical implementation details",
  "version": "10.0",
  "type": "object",
  "required": ["theory_id", "theory_name", "version", "classification", "ontology", "execution", "telos"],
  "properties": {
    "theory_id": {
      "type": "string",
      "pattern": "^[a-z_][a-z0-9_]*$",
      "description": "Unique identifier for the theory"
    },
    "theory_name": {
      "type": "string",
      "description": "Human-readable name of the theory"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+(\\.\\d+)?$",
      "description": "Semantic version of this theory schema"
    },
    "authors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Key theorists and contributors"
    },
    "publication_year": {
      "type": "integer",
      "minimum": 1900,
      "maximum": 2030,
      "description": "Year of seminal publication"
    },
    "description": {
      "type": "string",
      "description": "Concise summary of the theory"
    },
    "classification": {
      "type": "object",
      "required": ["domain"],
      "properties": {
        "domain": {
          "type": "object",
          "required": ["level", "component", "metatheory"],
          "properties": {
            "level": {
              "type": "string",
              "enum": ["Micro", "Meso", "Macro"],
              "description": "Level of analysis"
            },
            "component": {
              "type": "string", 
              "enum": ["Who", "Whom", "What", "Channel", "Effect"],
              "description": "Component of influence"
            },
            "metatheory": {
              "type": "string",
              "enum": ["Agentic", "Structural", "Interdependent"],
              "description": "Causal metatheory"
            }
          }
        },
        "complexity_tier": {
          "type": "string",
          "enum": ["direct", "heuristic", "simplified"],
          "description": "Operationalization complexity level"
        }
      }
    },
    "ontology": {
      "type": "object",
      "required": ["entities", "relationships"],
      "properties": {
        "entities": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "mcl_id"],
            "properties": {
              "name": {"type": "string"},
              "description": {"type": "string"},
              "mcl_id": {
                "type": "string",
                "description": "Master Concept Library primary key"
              },
              "dolce_parent": {
                "type": "string",
                "format": "uri",
                "description": "IRI of closest DOLCE class"
              },
              "properties": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["name", "type"],
                  "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "constraints": {"type": "object"},
                    "operationalization": {
                      "type": "object",
                      "properties": {
                        "measurement_approach": {"type": "string"},
                        "boundary_rules": {"type": "array"},
                        "fuzzy_boundaries": {"type": "boolean"},
                        "validation_examples": {"type": "array"}
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "relationships": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "source_role", "target_role"],
            "properties": {
              "name": {"type": "string"},
              "description": {"type": "string"},
              "source_role": {"type": "string"},
              "target_role": {"type": "string"},
              "dolce_parent": {
                "type": "string",
                "format": "uri",
                "description": "IRI of closest DOLCE relation"
              },
              "properties": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["name", "type"],
                  "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "constraints": {"type": "object"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "execution": {
      "type": "object",
      "required": ["process_type", "analysis_steps"],
      "properties": {
        "process_type": {
          "type": "string",
          "enum": ["sequential", "iterative", "workflow", "adaptive"],
          "description": "Process flow type"
        },
        "analysis_steps": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["step_id", "method", "description"],
            "properties": {
              "step_id": {"type": "string"},
              "description": {"type": "string"},
              "method": {
                "type": "string",
                "enum": ["llm_extraction", "predefined_tool", "custom_script", "hybrid"],
                "description": "Implementation method"
              },
              "inputs": {"type": "array", "items": {"type": "string"}},
              "outputs": {"type": "array", "items": {"type": "string"}},
              "conditions": {"type": "object"},
              
              "llm_prompts": {
                "type": "object",
                "description": "Prompts for LLM-based steps",
                "properties": {
                  "extraction_prompt": {"type": "string"},
                  "validation_prompt": {"type": "string"},
                  "classification_prompt": {"type": "string"},
                  "context_instructions": {"type": "string"}
                }
              },
              
              "tool_mapping": {
                "type": "object",
                "description": "Tool selection and configuration",
                "properties": {
                  "preferred_tool": {"type": "string"},
                  "alternative_tools": {"type": "array", "items": {"type": "string"}},
                  "tool_parameters": {"type": "object"},
                  "parameter_adaptation": {
                    "type": "object",
                    "properties": {
                      "method": {"type": "string"},
                      "adaptation_logic": {"type": "string"},
                      "wrapper_script": {"type": "string"}
                    }
                  }
                }
              },
              
              "custom_script": {
                "type": "object",
                "description": "Custom algorithm specification",
                "properties": {
                  "algorithm_name": {"type": "string"},
                  "description": {"type": "string"},
                  "business_logic": {"type": "string"},
                  "implementation_hint": {"type": "string"},
                  "inputs": {
                    "type": "object",
                    "patternProperties": {
                      ".*": {
                        "type": "object",
                        "properties": {
                          "type": {"type": "string"},
                          "range": {"type": "array"},
                          "description": {"type": "string"},
                          "constraints": {"type": "object"}
                        }
                      }
                    }
                  },
                  "outputs": {
                    "type": "object",
                    "patternProperties": {
                      ".*": {
                        "type": "object",
                        "properties": {
                          "type": {"type": "string"},
                          "range": {"type": "array"},
                          "description": {"type": "string"}
                        }
                      }
                    }
                  },
                  "test_cases": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "inputs": {"type": "object"},
                        "expected_output": {},
                        "description": {"type": "string"}
                      }
                    }
                  },
                  "validation_rules": {"type": "array", "items": {"type": "string"}},
                  "tool_contracts": {"type": "array", "items": {"type": "string"}}
                }
              },
              
              "uncertainty_handling": {
                "type": "object",
                "properties": {
                  "confidence_thresholds": {"type": "object"},
                  "fallback_strategy": {"type": "string"},
                  "uncertainty_propagation": {"type": "string"}
                }
              }
            }
          }
        },
        
        "cross_modal_mappings": {
          "type": "object",
          "description": "How theory maps across graph/table/vector modes",
          "properties": {
            "graph_representation": {"type": "object"},
            "table_representation": {"type": "object"},
            "vector_representation": {"type": "object"},
            "mode_conversions": {"type": "array"}
          }
        },
        
        "dynamic_adaptation": {
          "type": "object",
          "description": "For adaptive processes like Spiral of Silence",
          "properties": {
            "adaptation_triggers": {"type": "array"},
            "state_variables": {"type": "object"},
            "adaptation_rules": {"type": "array"}
          }
        }
      }
    },
    "telos": {
      "type": "object",
      "required": ["purpose", "output_format", "success_criteria"],
      "properties": {
        "purpose": {"type": "string"},
        "output_format": {"type": "string"},
        "success_criteria": {
          "type": "array",
          "items": {"type": "string"}
        },
        "analysis_tiers": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["descriptive", "explanatory", "predictive", "interventionary"]
          }
        }
      }
    },
    "validation": {
      "type": "object",
      "description": "Theory validation and testing framework",
      "properties": {
        "operationalization_notes": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Documented simplifications and assumptions"
        },
        "theory_tests": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "test_name": {"type": "string"},
              "input_scenario": {"type": "string"},
              "expected_theory_application": {"type": "string"},
              "validation_criteria": {"type": "string"}
            }
          }
        },
        "boundary_cases": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "case_description": {"type": "string"},
              "theory_applicability": {"type": "string"},
              "expected_behavior": {"type": "string"}
            }
          }
        }
      }
    },
    "configuration": {
      "type": "object",
      "description": "Configurable aspects of theory application",
      "properties": {
        "tracing_level": {
          "type": "string",
          "enum": ["minimal", "standard", "verbose", "debug"],
          "default": "standard"
        },
        "llm_models": {
          "type": "object",
          "properties": {
            "extraction": {"type": "string"},
            "reasoning": {"type": "string"},
            "validation": {"type": "string"}
          }
        },
        "performance_optimization": {
          "type": "object",
          "properties": {
            "enable_caching": {"type": "boolean"},
            "batch_processing": {"type": "boolean"},
            "parallel_execution": {"type": "boolean"}
          }
        },
        "fallback_strategies": {
          "type": "object",
          "properties": {
            "missing_tools": {"type": "string"},
            "low_confidence": {"type": "string"},
            "edge_cases": {"type": "string"}
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "mcl_id": {
          "type": "string",
          "description": "Master Concept Library primary key"
        },
        "created": {"type": "string", "format": "date-time"},
        "modified": {"type": "string", "format": "date-time"},
        "contributors": {"type": "array", "items": {"type": "string"}},
        "validation_status": {"type": "string"},
        "implementation_status": {"type": "string"},
        "test_coverage": {"type": "number"}
      }
    }
  }
}

================================================================================

## 21. DATABASE_SCHEMAS.md

**Source**: `docs/architecture/data/DATABASE_SCHEMAS.md`

---

### Neo4j Schema
```cypher
// Core Node Type with Embedding Property
(:Entity {
    id: string,
    canonical_name: string,
    entity_type: string,
    confidence: float,
    quality_tier: string,
    created_by: string,
    embedding: vector[384] // Native vector type
})

// Vector Index for Fast Similarity Search
CREATE VECTOR INDEX entity_embedding_index IF NOT EXISTS
FOR (e:Entity) ON (e.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: 'cosine'
  }
}
```

### SQLite Schemas
```sql
-- Workflow Management
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP,
    current_step INTEGER
);

-- Object Provenance
CREATE TABLE provenance (
    object_id TEXT,
    tool_id TEXT,
    operation TEXT,
    inputs JSON,
    outputs JSON,
    execution_time REAL,
    created_at TIMESTAMP
);

-- PII Vault
CREATE TABLE pii_vault (
    pii_id TEXT PRIMARY KEY,
    ciphertext_b64 TEXT NOT NULL,
    nonce_b64 TEXT NOT NULL,
    created_at TIMESTAMP
);
``` 

================================================================================

## 22. mcp-integration-architecture.md

**Source**: `docs/architecture/systems/mcp-integration-architecture.md`

---

# MCP Integration Architecture

**Status**: Production Implementation  
**Date**: 2025-07-21  
**Purpose**: Document KGAS Model Context Protocol (MCP) integration for external tool access

> **📋 Related Documentation**: For comprehensive MCP limitations, ecosystem analysis, and implementation guidance, see [MCP Architecture Documentation](../mcp/README.md)

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

## MCP Capability Framework

### **Core MCP Capabilities**
- **Service Tools** (T107, T110, T111, T121): Identity, provenance, quality, and workflow management
- **Document Processing**: Complete pipeline from ingestion through analysis
- **FastMCP Framework**: Standard MCP protocol implementation
- **Security Framework**: Authentication and audit logging capabilities

### **Advanced MCP Capabilities**
- **Theory Integration**: Automated theory extraction and application via MCP
- **Cross-Modal Tools**: Unified interface for multi-modal analysis
- **Batch Processing**: Large-scale document processing capabilities
- **Enhanced Security**: Access control and PII protection

### **Extended MCP Integration**
- **Collaborative Features**: Multi-user research environments
- **Advanced Analytics**: Statistical analysis and visualization tools
- **External Integration**: Direct integration with research platforms
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

================================================================================

## 23. LIMITATIONS.md

**Source**: `docs/architecture/LIMITATIONS.md`

---

---
status: living
---

# KGAS System Limitations

**Document Version**: 2.0  
**Updated**: 2024-07-19
**Purpose**: To provide a transparent and realistic assessment of the system's architectural and operational boundaries.

## 🎯 Core Architectural Limitations

This section details fundamental design choices that define the system's operational envelope. These are not bugs, but deliberate trade-offs made to prioritize research flexibility over production-grade resilience and feature scope.

### **1. No High-Availability (HA) by Design**
- **Limitation**: The system is designed as a single-node, single-leader application. There are no built-in mechanisms for automated failover, database replication, or load balancing.
- **Consequence**: If a critical component like the Neo4j database becomes unavailable, the entire system will halt and require manual intervention to restart.
- **Rationale**: This is an academic research project. The complexity and operational overhead of implementing an HA architecture are out of scope and provide minimal value for local, single-user research workflows. The system is **not** suitable for production or business-critical deployments where uptime is a concern.

### **2. Static Theory Model (No On-the-Fly Evolution)**
- **Limitation**: The system currently treats "theories" as static, versioned JSON artifacts. To change a theory, a user must manually create a new version of the file and re-run the analysis. There is no built-in functionality for branching, merging, or otherwise managing the lifecycle of a theory within the application.
- **Consequence**: Exploring variations of a theoretical model is a manual, iterative process that happens outside the core application logic.
- **Rationale**: Building an in-app, `git`-like version control system for ontologies is a significant research project in its own right. The current design defers this complexity by using a `TheoryRepository` abstraction, which allows a more sophisticated versioning system to be plugged in later without a major refactor. (See `docs/planning/ROADMAP.md`).

### **3. Simplified PII Handling**
- **Limitation**: The system's approach to Personally Identifiable Information (PII) is designed for revocability in a research context, not for compliance with stringent regulations like GDPR or HIPAA in a production environment.
- **Consequence**: While the system includes a PII vault for recoverable encryption, it lacks the broader governance features (e.g., automated key rotation, detailed audit logs, threshold secret sharing) required for handling sensitive production data.
- **Rationale**: Implementing a full-scale, compliant PII governance system is beyond the current scope. The focus is on enabling research workflows that may require temporary access to sensitive data, with the understanding that the system is not a hardened production vault.

## 🔧 Other Technical & Operational Limitations

### Processing & Performance
- **Single-Machine Focus**: The default deployment is for a single machine; scaling is vertical (more RAM/CPU) not horizontal (distributed).
- **Memory Intensive**: Graph construction and analysis algorithms can be memory-intensive. A minimum of 8GB RAM is recommended, with 16GB+ for larger graphs.
- **API Dependencies**: System performance and cost are directly tied to the rate limits, latency, and pricing of external LLM APIs.

### Accuracy & Reproducibility
- **Domain Sensitivity**: Extraction accuracy is highest when a relevant theory schema is provided. Performance on out-of-domain documents without a guiding theory may be lower.
- **Stochastic Outputs**: While tests are seeded for determinism, some LLM-based components may exhibit stochastic (non-deterministic) behavior, leading to minor variations in output between identical runs.

---

<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for the master plan and future feature concepts.</sup>


================================================================================

