# KGAS Architecture Overview

**This document defines the target system architecture for KGAS (Knowledge Graph Analysis System). It describes the intended design and component relationships that guide implementation.**

**Important**: For current implementation status, see [docs/roadmap/ROADMAP_OVERVIEW.md](../roadmap/ROADMAP_OVERVIEW.md).

---

## System Vision

**KGAS is designed as a theory automation proof-of-concept for future LLM capabilities, not a general research tool for human researchers.**

KGAS (Knowledge Graph Analysis System) demonstrates automated theory processing - extracting theories from academic literature, converting them into executable analysis specifications, and applying them to datasets through LLM-driven workflows. The system is architected to prepare for increasingly powerful LLMs that can autonomously conduct theory-driven research, moving fluidly between analytical modes (graph, table, vector) as theoretical requirements demand.

**Primary Goal**: Build infrastructure for automated theory operationalization, validation, and application - proving that LLMs can systematically apply social science theories to empirical data without human intervention in theory selection or analytical method choice.

## Unique Analytical Capabilities

KGAS enables analytical approaches impossible with traditional research tools:

### Cross-Modal Analysis Integration

**Purpose**: Enable LLMs to fluidly switch between analytical modes (graph, table, vector) as theoretical requirements demand, without human intervention in method selection.

- **Statistical models become networks**: SEM results convert to graph structures for centrality and community analysis - enabling theory-driven mode switching
- **Network topology informs statistics**: Graph structure guides regression model specification and variable selection - supporting automated analytical pipeline creation
- **Correlation matrices as networks**: Pearson correlations become edge weights for network analysis algorithms - demonstrating cross-modal data transformation
- **Vector clustering enhances statistics**: Embedding-based clustering improves factor analysis and latent variable identification - proving analytical mode complementarity
- **Uncertainty-aware integration**: Cross-modal convergence reduces uncertainty through analytical triangulation (designed for future LLM confidence assessment)

### Automated Theory Operationalization  
- **Theory schemas to statistical models**: Generate SEM specifications, regression models, and experimental designs directly from theoretical frameworks
- **Theory-driven agent creation**: Convert theoretical propositions into agent behavioral rules for simulation testing
- **Executable theoretical predictions**: Transform qualitative theories into quantitative, testable hypotheses with measurement specifications
- **Multi-theory comparison**: Test competing theoretical explanations simultaneously through parallel analysis pipelines

### Social Media Analysis Integration
- **Real-time Twitter data processing**: T85_TwitterExplorer enables natural language querying of Twitter data with LLM-powered query planning
- **Social network graph construction**: Extract Twitter users, tweets, and relationships into Neo4j graph structures for network analysis
- **Cross-modal social media analysis**: Convert Twitter data between graph (network analysis), table (statistical analysis), and vector (semantic analysis) formats
- **Theory-driven social media research**: Apply theoretical frameworks to social media data for hypothesis testing and pattern discovery

### Scale and Automation
- **Document processing**: Analyze 1000+ documents compared to 100s possible with manual qualitative coding
- **Simultaneous multi-mode analysis**: Run graph, statistical, and vector analyses concurrently on the same data
- **Automated workflow generation**: Create complete analysis pipelines from natural language research questions through LLM tool orchestration
- **Efficient cross-modal conversion**: Transform results between analytical representations for theory-driven analysis
- **Large tool ecosystem**: 122+ specialized tools available for LLM selection (tool count doesn't affect latency - LLM agents dynamically select appropriate tools based on descriptions and theoretical requirements)

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
- **Hybrid theory extraction**: LLM-based automated extraction with expert validation sets for academic credibility
- **Theory-guided analysis** using domain ontologies
- **Flexible theory integration** supporting multiple frameworks

### 3. IC-Informed Uncertainty Management ([ADR-029](adrs/ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md))
- **Intelligence Community methodologies** integrating ICD-203/206 standards and structured analytic techniques
- **Mathematical uncertainty propagation** using root-sum-squares for independent uncertainties
- **Evidence-based assessment** evaluating quality over quantity, avoiding Heuer's information paradox
- **Single integrated LLM analysis** with comprehensive IC-informed assessment
- **Sustainable tracking** focusing on decision-critical metrics only

### 4. Academic Research Focus
- **Single-node design** for local research environments (entire system runs on one machine for simplicity, not distributed across servers)
- **Proof-of-concept scope** designed to demonstrate theory automation capabilities rather than production deployment
- **Reproducibility first** with complete provenance tracking to validate automated theory application
- **Flexibility over performance** for exploratory research - building for future compute capabilities

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
- **Immediate error exposure**: Problems surface immediately rather than being masked - critical for validating automated theory application
- **Input validation**: Rigorous validation at system boundaries to prevent cascading errors in automated workflows
- **Complete failure**: System fails entirely on critical errors rather than degrading gracefully - ensures clean experimental conditions
- **Agent validation**: LLM-generated workflows validated against hand-constructed tool DAG networks to verify automated reasoning
- **Autonomous mode enforcement**: Agent-controlled mode fails completely on validation errors rather than degrading - maintains experimental integrity
- **Evidence-based operation**: All functionality backed by validation evidence to support theory automation claims

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│    ┌───────────────────────────────────────────────────────┐ │
│    │                KGAS Native Interface                  │ │
│    │            (Agent-Driven Workflows)                   │ │
│    │              NL → Agent → Workflow                    │ │
│    └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│               Workflow Orchestration Layer                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Layer 1:      │ │   Layer 2:      │ │   Layer 3:      │ │
│  │Agent-Controlled │ │Agent-Assisted   │ │Manual Control   │ │
│  │                 │ │                 │ │                 │ │
│  │NL→YAML→Execute  │ │YAML Review      │ │Direct YAML      │ │
│  │Complete Auto    │ │User Approval    │ │Expert Control   │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 YAML Workflow Engine                    │ │
│  │         Agent-Generated Workflows + Orchestration       │ │
│  └─────────────────────────────────────────────────────────┘ │
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
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │StatisticalService  │ │ResourceManager │ │             │ │
│  └────────────────────┘ └────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 MCP Integration Layer                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              External MCP Ecosystem                     │ │
│  │ Academic: Semantic Scholar, ArXiv • Media: YouTube, News│ │
│  │ Documents: MarkItDown, Pandoc • Infrastructure: Grafana │ │
│  └─────────────────────────────────────────────────────────┘ │
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
- **Validation Framework**: Hand-constructed tool DAG networks for LLM-generated plan validation
- **Fail-Fast Design**: System fails completely on validation errors rather than degrading
- **Optimal for**: Standard research patterns and common analysis tasks

#### Layer 2: Agent-Assisted  
- **Human-in-the-loop**: Agent generates YAML, user reviews and approves
- **Quality control**: User validates before execution
- **Optimal for**: Complex research requiring validation

#### Layer 3: Manual Control
- **Expert control**: Direct YAML workflow creation and modification
- **Maximum flexibility**: Custom workflows and edge cases
- **Optimal for**: Novel research methodologies and system debugging

### Agent Validation Architecture

#### Tool DAG Network Validation
- **Hand-Constructed Reference Networks**: Expert-created tool dependency graphs for common research workflows
- **LLM Plan Comparison**: Generated agent workflows validated against reference DAG structures
- **Validation Criteria**: Tool sequence validity, dependency satisfaction, resource requirements
- **Fail-Fast Enforcement**: Invalid workflows trigger complete system failure with detailed error reporting

#### Resource Management Integration
- **Multi-Tier Budgeting**: Session, project, and monthly resource limits with automatic enforcement
- **Cost Optimization**: Intelligent model selection, operation batching, and caching strategies  
- **Real-Time Monitoring**: Resource usage tracking with warning thresholds and emergency controls
- **Academic Focus**: Research-appropriate budgeting aligned with project timelines and computational needs

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
- **[Resource Manager](systems/COMPONENT_ARCHITECTURE_DETAILED.md#6-resource-manager)**: Multi-tier budgeting, cost optimization, and real-time resource monitoring for LLM operations
- **[ABM Service](adrs/ADR-020-Agent-Based-Modeling-Integration.md)**: Theory validation through generative agent-based modeling and synthetic experiments

## Data Storage Layer

**Note**: Bi-store design enables cross-modal analysis automation - Neo4j optimized for graph operations, SQLite for statistical analysis. Academic proof-of-concept accepts eventual consistency over enterprise ACID guarantees.

- **[Bi-Store Architecture](data/bi-store-justification.md)**: Neo4j + SQLite design with trade-off analysis - enables LLM-driven cross-modal analysis
- **[Data Models](data/schemas.md)**: Entity, relationship, and metadata schemas designed for theory automation
- **[Comprehensive Schema Ecosystem](data/SCHEMA_MANAGEMENT.md#comprehensive-modeling-paradigm-schema-ecosystem)**: 5 complete modeling paradigms (UML, RDF/OWL, ORM, TypeDB, N-ary) for diverse research approaches and automated theory processing
- **[Vector Storage](adrs/ADR-003-Vector-Store-Consolidation.md)**: Native Neo4j vectors with HNSW indexing for semantic theory matching

## Theory Integration Architecture

**This is the core innovation of KGAS - automated theory processing for future LLM capabilities.**

### Theory Automation Vision

KGAS V13 meta-schema + DOLCE integration + theory validation system enables:
- **Automated theory discovery**: LLMs identify theories applicable to research questions
- **Automated theory operationalization**: Convert theoretical frameworks into executable analysis pipelines
- **Automated theory comparison**: Test competing theoretical explanations simultaneously
- **Theory-driven tool selection**: LLMs choose appropriate analytical methods based on theoretical requirements

This infrastructure prepares for future LLMs that can autonomously conduct theory-driven research without human intervention in theory selection or analytical method choice.

### Two-Layer Theory Architecture

#### **Layer 1: Comprehensive Structure Extraction**
- **LLM-guided extraction**: Gemini 2.5 Flash with V13 meta-schema for standardized theory representation
- **Indigenous terminology preservation**: Author's exact terms maintained for theoretical fidelity
- **Cross-domain robustness**: Validated across 7 academic domains for broad applicability
- **Theory type coverage**: Mathematical, taxonomic, causal, procedural theories for comprehensive automation

#### **Layer 2: Question-Driven Analysis**
- **Flexible analytical purposes**: Same structure serves multiple research questions for LLM adaptability
- **Clean separation**: Structure extraction independent of analytical goals enables automated theory selection
- **Theory-agnostic querying**: Consistent interface across theory types for LLM tool orchestration

### Ontological Framework Integration
- **DOLCE**: Upper-level ontology for general categorization (post-hoc mapping)
- **FOAF/SIOC**: Social network and online community concepts
- **V13 Meta-Schema**: Schema with indigenous terminology support
- **[Integration Model](concepts/theoretical-framework.md)**: Two-layer approach with LLM extraction

### Theory-Aware Processing ([ADR-022](adrs/ADR-022-Theory-Selection-Architecture.md))
- **[Two-Layer Theory Architecture](two-layer-theory-architecture.md)**: Theory extraction and analysis with V13 meta-schema
- **[Theory Repository](systems/theory-repository-abstraction.md)**: Schema management with V13 meta-schema validation
- **[Extraction Integration](systems/theory-extraction-integration.md)**: LLM-guided literature to schema extraction
- **[Master Concept Library](concepts/master-concept-library.md)**: Domain concepts with indigenous terminology preservation

## Uncertainty Architecture ([IC-Informed Framework](adrs/ADR-029-IC-Informed-Uncertainty-Framework.md))

### Comprehensive Uncertainty Management System  

KGAS implements the **IC-Informed uncertainty framework** - the authoritative approach to uncertainty quantification and propagation throughout the analytical pipeline, based on proven Intelligence Community methodologies:

#### Core Framework Principles

1. **LLM-Intelligent Entity Resolution** 
   - **Realistic confidence ranges**: 0.75-0.95 for most entity resolution with context
   - **Context-aware disambiguation**: Leverages modern LLM capabilities for intelligent interpretation
   - **Strategic ambiguity detection**: Distinguishes intentional vagueness from lack of information

2. **Three-Tier Uncertainty Taxonomy**
   - **Data-level**: Text quality, temporal gaps, speaker identification (0.70-0.95 typical range)
   - **Extraction-level**: Construct operationalization, entity resolution, context interpretation (0.75-0.95 typical range)  
   - **Analytical**: Aggregation methods, modal integration, temporal dynamics (0.60-0.85 typical range)

3. **Mathematical Coherence**
   - **Frequency ≠ Confidence**: Separates entity occurrence counts from resolution confidence
   - **Distribution preservation**: Maintains probability distributions rather than forced point estimates
   - **Correlation-based propagation**: Uses modified independence assumption with correlation factors

4. **Cross-Modal Uncertainty Reduction** 
   - **Primary reduction mechanism**: Stage 4 multi-modal convergence (0.10-0.15 uncertainty reduction)
   - **Triangulation through agreement**: High cross-modal agreement (>0.80) significantly reduces uncertainty
   - **Transparent disagreement handling**: Preserves conflicts when modes disagree

5. **Research Impact Focus**
   - **Methodology guidance**: Confidence thresholds guide appropriate analytical approaches  
   - **Transparent reporting**: Clear uncertainty disclosure in research outputs
   - **Quality-driven decisions**: Uncertainty assessment determines research method suitability

See **[IC-Informed Framework](adrs/ADR-029-IC-Informed-Uncertainty-Framework.md)** for complete implementation details and **[Entity Resolution Stress Tests](../examples/entity_resolution_uncertainty_stress_tests.md)** for validation evidence.

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

KGAS leverages the Model Context Protocol (MCP) ecosystem for both internal tool access and external service integration:

### Dual MCP Strategy

#### 1. **KGAS as MCP Server** (Tool Exposure)
- **122+ KGAS tools** accessible via standardized MCP interface
- **Multiple client support**: Works with Claude Desktop, custom Streamlit UI, and other MCP clients
- **FastMCP framework**: Production-grade MCP server implementation
- **Type-safe interfaces**: Standardized tool protocols

#### 2. **KGAS as MCP Client** (External Integration)
- **Academic Services**: Connect to Semantic Scholar, ArXiv LaTeX, PubMed MCP servers
- **Document Processing**: Integrate with MarkItDown, Content Core, Pandoc MCP servers
- **Infrastructure**: Use Grafana, Docker, Logfire MCP servers for monitoring/deployment
- **Media Sources**: Access YouTube, Google News, DappierAI for discourse analysis
- **Social Media Analysis**: Twitter API integration via T85_TwitterExplorer for real-time social media graph construction and analysis

### MCP Client Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Integration Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │    MCP     │  │    MCP     │  │       MCP          │    │
│  │Orchestrator│  │  Clients   │  │    Transport       │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                  External MCP Servers                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Academic: Semantic Scholar, ArXiv LaTeX, PubMed     │    │
│  │ Media: YouTube, Google News, DappierAI              │    │
│  │ Social Media: T85_TwitterExplorer API Integration   │    │
│  │ Documents: MarkItDown, Content Core, Pandoc         │    │
│  │ Infrastructure: Grafana, Docker, Logfire            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key MCP Integration Components
- **MCP Orchestrator**: Coordinates multiple MCP servers for unified operations
- **HTTP Transport**: Manages connections to external MCP servers
- **Circuit Breakers**: Protects against external service failures
- **Rate Limiting**: Respects API limits of external services
- **Unified Search**: Query across all academic and media sources

See [MCP Architecture Details](systems/mcp-integration-architecture.md) for comprehensive integration specifications.

## Resource Management Architecture

### Multi-Tier Resource Budgeting
KGAS implements comprehensive resource management for LLM operations and computational resources:

#### Budget Hierarchy
- **Session Budgets**: Individual research session limits (API calls, compute time, cost)
- **Project Budgets**: Research project resource allocation across multiple sessions
- **Monthly Budgets**: Institutional or user monthly resource constraints

#### Cost Optimization Strategies
- **Intelligent Model Selection**: Automatic selection of optimal LLM models based on task complexity
- **Operation Batching**: Grouping similar operations to reduce API call overhead
- **Intelligent Caching**: Reuse of expensive computations across research sessions
- **Adaptive Resource Allocation**: Dynamic resource distribution based on research priorities

#### Real-Time Resource Monitoring
- **Usage Tracking**: Continuous monitoring of API calls, compute time, and costs
- **Threshold Alerts**: Automatic warnings at 80% and 95% of budget limits
- **Emergency Controls**: Automatic cost-minimal mode activation near budget limits
- **Performance Optimization**: Automatic degradation to cheaper models when appropriate

#### Academic Research Integration
- **Research-Specific Categories**: Cost tracking by research phase (literature review, analysis, synthesis)
- **Project Timeline Alignment**: Resource budgeting aligned with academic project schedules
- **Collaborative Budgeting**: Multi-user resource sharing for research teams
- **Quality-Cost Balance**: Configurable trade-offs between analysis quality and resource consumption

## Quality Attributes

### Research Capabilities
- **Scale**: Process 1000+ documents with maintained analytical quality
- **Integration**: 122+ tools accessible through unified interface protocols
- **Reproducibility**: Complete provenance tracking from source documents to final outputs
- **Academic standards**: APA-formatted tables, publication-ready figures, statistical diagnostics

### Performance
- **Cross-modal conversion**: Efficient transformation between graph, table, and vector representations
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
- **Simplicity**: Easier deployment, maintenance, and debugging
- **Cost**: Lower infrastructure and operational costs
- **Consistency**: Simplified data consistency without distributed transactions
- **Scalability**: Limited to vertical scaling (~1M entities practical limit)
- **Availability**: No built-in redundancy or failover

**Rationale**: Academic research projects typically process thousands of documents, not millions. The simplicity benefits outweigh scalability limitations for the target use case.

### 2. Bi-Store (Neo4j + SQLite) vs Alternative Architectures

**Decision**: Neo4j for graph/vectors, SQLite for metadata/workflow

**Trade-offs**:
- **Optimized Storage**: Each database used for its strengths
- **Native Features**: Graph algorithms in Neo4j, SQL queries in SQLite
- **Simplicity**: Simpler than tri-store, avoids PostgreSQL complexity
- **Consistency**: Cross-database transactions not atomic
- **Integration**: Requires entity ID synchronization

**Rationale**: The bi-store provides the right balance of capability and complexity. See [ADR-003](adrs/ADR-003-Vector-Store-Consolidation.md) for detailed analysis.

### 3. Multi-Paradigm Research Support

**Decision**: Support both theory-driven and data-driven research paradigms

**Capabilities**:
- **Theory-First**: Theory schemas guide extraction and analysis for hypothesis testing
- **Data-First**: Grounded theory and exploratory analysis for emergent pattern discovery
- **Mixed Methods**: Seamless integration of quantitative (SEM, statistics) and qualitative approaches
- **Cross-Modal Discovery**: Graph/vector analysis reveals patterns missed by single-mode approaches

**Trade-offs**:
- **Flexibility**: Supports diverse research methodologies and paradigms
- **Discovery**: Emergent behavior detection (T128) finds novel patterns
- **Validation**: Theory validation through simulation and statistical testing
- **Complexity**: Multiple analytical pathways require sophisticated orchestration

**Rationale**: KGAS serves the full spectrum of social science research, from exploratory grounded theory to confirmatory theory testing, enabling researchers to move fluidly between paradigms as research questions evolve.

### 4. Contract-First Tool Design vs Flexible Interfaces

**Decision**: All tools implement standardized contracts

**Trade-offs**:
- **Integration**: Tools compose without custom logic
- **Testing**: Standardized testing across all tools
- **Agent Orchestration**: Enables intelligent tool selection
- **Flexibility**: Tools must fit the contract model
- **Migration Effort**: Existing tools need refactoring

**Rationale**: The long-term benefits of standardization outweigh short-term migration costs. See [ADR-001](adrs/ADR-001-Phase-Interface-Design.md).

### 5. Comprehensive Uncertainty vs Simple Confidence

**Decision**: 4-layer uncertainty architecture with CERQual framework

**Trade-offs**:
- **Research Quality**: Publication-grade uncertainty quantification
- **Decision Support**: Rich information for interpretation
- **Flexibility**: Configurable complexity levels
- **Complexity**: Harder to implement and understand
- **Performance**: Additional computation overhead

**Rationale**: Research credibility requires sophisticated uncertainty handling. The architecture allows starting simple and adding layers as needed.

### 6. LLM Integration Approach

**Decision**: LLM for ontology generation and mode selection, not core processing

**Trade-offs**:
- **Reproducibility**: Core processing deterministic
- **Cost Control**: LLM used strategically, not for every operation
- **Flexibility**: Can swap LLM providers
- **Capability**: May miss LLM advances in extraction
- **Integration**: Requires careful prompt engineering

**Rationale**: Balances advanced capabilities with research requirements for reproducibility and cost management.

### 7. MCP Protocol for Tool Access

**Decision**: All tools exposed via Model Context Protocol

**Trade-offs**:
- **Ecosystem**: Integrates with Claude, ChatGPT, etc.
- **Standardization**: Industry-standard protocol
- **External Access**: Tools available to any MCP client
- **Overhead**: Additional protocol layer

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
- **[ADR-021](adrs/ADR-021-Statistical-Analysis-Integration.md)**: Comprehensive statistical analysis integration
- **[ADR-022](adrs/ADR-022-Theory-Selection-Architecture.md)**: Two-layer theory architecture with V13 meta-schema validation
- **[ADR-023](adrs/ADR-023-Comprehensive-Schema-Modeling-Ecosystem.md)**: Comprehensive schema modeling ecosystem with 5 paradigms for diverse research approaches

## Related Documentation

### Detailed Architecture
- **[Concepts](concepts/)**: Theoretical frameworks and design patterns
- **[Data Architecture](data/)**: Schemas and data flow
- **[Systems](systems/)**: Component detailed designs
- **[Specifications](specifications/)**: Formal specifications

**NOT IN THIS DOCUMENT** - See [Roadmap Overview](../../ROADMAP_OVERVIEW.md) for:
- Current implementation status and progress
- Development phases and completion evidence
- Known issues and limitations
- Timeline and milestones
- Phase-specific implementation evidence

## Architecture Governance

### Tool Ecosystem Governance
**[See Tool Governance Framework](TOOL_GOVERNANCE.md)** for comprehensive tool lifecycle management, quality standards, and the 122-tool ecosystem governance process.

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


This document describes the **target architecture** - the intended final system design. For current implementation status, development progress, and phase completion details, see:

- **[Roadmap Overview](../roadmap/ROADMAP_OVERVIEW.md)** - Current status and major milestones
- **[Phase TDD Implementation](../roadmap/phases/phase-tdd/tdd-implementation-progress.md)** - Active development phase progress  
- **[Clear Implementation Roadmap](../roadmap/initiatives/clear-implementation-roadmap.md)** - Master implementation plan
- **[Tool Implementation Status](../roadmap/initiatives/uncertainty-implementation-plan.md)** - Tool-by-tool completion tracking

*This architecture document contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*