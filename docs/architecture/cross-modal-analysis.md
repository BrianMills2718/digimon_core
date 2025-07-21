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
```

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