# KGAS Analysis Architecture and Integration Systems

**Description**: Cross-modal analysis, interfaces, components, and MCP integration
**Generated**: Split from comprehensive architecture document
**Files Included**: 5

---

## Table of Contents

1. [cross-modal-analysis.md](#1-crossmodalanalysismd)
2. [agent-interface.md](#2-agentinterfacemd)
3. [COMPONENT_ARCHITECTURE_DETAILED.md](#3-componentarchitecturedetailedmd)
4. [SPECIFICATIONS.md](#4-specificationsmd)
5. [mcp-integration-architecture.md](#5-mcpintegrationarchitecturemd)

---

## 1. cross-modal-analysis.md {#1-crossmodalanalysismd}

**Source**: `docs/architecture/cross-modal-analysis.md`

---

---

# Cross-Modal Analysis Architecture

*Status: Target Architecture with Production Theory Integration*

## Overview

KGAS implements a comprehensive cross-modal analysis architecture that enables fluid movement between Graph, Table, and Vector data representations. The system integrates **production-ready automated theory extraction** with **LLM-driven intelligent orchestration** to provide theory-aware, multi-modal analysis capabilities. This design allows researchers to leverage optimal analysis modes for each research question while maintaining complete theoretical grounding and source traceability.

## Integrated Theory-Modal Architecture

KGAS combines two sophisticated systems for unprecedented analytical capability:

### **Theory-Adaptive Modal Selection** (Production-Ready Integration)
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

## 2. agent-interface.md {#2-agentinterfacemd}

**Source**: `docs/architecture/agent-interface.md`

---

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

## 3. COMPONENT_ARCHITECTURE_DETAILED.md {#3-componentarchitecturedetailedmd}

**Source**: `docs/architecture/systems/COMPONENT_ARCHITECTURE_DETAILED.md`

---

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

## 4. SPECIFICATIONS.md {#4-specificationsmd}

**Source**: `docs/architecture/specifications/SPECIFICATIONS.md`

---

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

## 5. mcp-integration-architecture.md {#5-mcpintegrationarchitecturemd}

**Source**: `docs/architecture/systems/mcp-integration-architecture.md`

---

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

