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

#### **World Analysis-Focused Mode Selection**
The system provides intelligent mode selection aligned with KGAS's primary world analysis purpose:

```python
class CrossModalOrchestrator:
    """LLM-driven intelligent mode selection optimized for world analysis."""
    
    async def select_analysis_mode(self, research_question: str, human_analytical_intent: str, data_characteristics: Dict) -> AnalysisStrategy:
        """Analyze research question and recommend optimal world analysis approach."""
        
        mode_selection_prompt = f"""
        Research Question: "{research_question}"
        Human Analytical Intent: "{human_analytical_intent}"
        Data Characteristics: {data_characteristics}
        
        KGAS PRIMARY PURPOSE: Use discourse as evidence to analyze real-world phenomena
        
        Analyze this question and recommend optimal mode for WORLD ANALYSIS:
        
        GRAPH MODE optimal for world analysis of:
        - Social networks and influence patterns in real world
        - Information flow and diffusion through actual communities  
        - Power structures and hierarchies revealed in discourse
        - Real-world relationship patterns and social structures
        
        TABLE MODE optimal for world analysis of:
        - Population-level patterns and statistical trends
        - Comparative analysis across real-world groups/contexts
        - Quantitative evidence of world phenomena from discourse
        - Temporal changes in real-world conditions/behaviors
        
        VECTOR MODE optimal for world analysis of:
        - Conceptual similarity in how world phenomena are discussed
        - Thematic clustering of real-world issues/topics
        - Evolution of world understanding across discourse
        - Semantic patterns revealing world knowledge structures
        
        Human Analytical Question Types:
        - DESCRIPTIVE: "What does discourse describe?" → Text properties analysis
        - EXPLANATORY: "What does this tell us about the world?" → World phenomena analysis  
        - PREDICTIVE: "What effects might this have?" → World impact analysis
        - PRESCRIPTIVE: "How should we intervene?" → World intervention guidance
        
        Select mode(s) that best reveal real-world phenomena through discourse evidence.
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

**Example World Analysis Mode Selection**:

Research Question: *"How do media outlets influence political discourse on climate change?"*
Human Intent: "What does media discourse reveal about real-world climate policy influence?"

LLM Analysis for World Analysis:
1. **Primary Mode**: Graph - Map real-world influence networks revealed through discourse patterns
2. **Secondary Mode**: Table - Quantify actual coverage patterns showing world policy bias
3. **Tertiary Mode**: Vector - Analyze conceptual evolution of climate understanding in real discourse
4. **Workflow**: Graph (map real influence) → Table (quantify world patterns) → Vector (track conceptual evolution)

**Default Analysis Approach**: 
- **Explanatory questions** (world analysis) → Default to mode best suited for revealing world phenomena
- **Descriptive questions** (text analysis) → Default to text property analysis modes  
- **Predictive questions** (effect analysis) → Default to modes revealing discourse impact patterns
- **Prescriptive questions** (intervention) → Default to modes revealing intervention opportunities

**Conflict Resolution**: When modes conflict, LLM arbitration prioritizes world analysis effectiveness over technical convenience, aligned with KGAS's primary analytical purpose.

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