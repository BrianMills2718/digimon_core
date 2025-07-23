# ADR-015: Cross-Modal Orchestration

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: Academic research requires flexible analysis across different data representations (graph, table, vector) with seamless conversion and source traceability.

## Decision

We will implement **cross-modal orchestration** enabling fluid movement between three analysis modes:

1. **Graph Analysis**: Relationships, centrality, communities, paths
2. **Table Analysis**: Statistical analysis, aggregations, correlations  
3. **Vector Analysis**: Similarity search, clustering, embeddings

```python
class CrossModalOrchestrator:
    """Orchestrate analysis across graph, table, and vector representations"""
    
    def __init__(self, service_manager: ServiceManager):
        self.services = service_manager
        self.neo4j = service_manager.neo4j_manager
        self.analytics = service_manager.analytics_service
    
    def convert_representation(
        self, 
        data: Any, 
        from_mode: AnalysisMode, 
        to_mode: AnalysisMode,
        preserve_provenance: bool = True
    ) -> CrossModalResult:
        """Convert data between analysis modes with provenance preservation"""
        
        converter = self._get_converter(from_mode, to_mode)
        converted_data = converter.convert(data)
        
        if preserve_provenance:
            self._link_provenance(data, converted_data, from_mode, to_mode)
        
        return CrossModalResult(
            data=converted_data,
            source_mode=from_mode,
            target_mode=to_mode,
            conversion_metadata=converter.get_metadata()
        )
```

### **Core Cross-Modal Principles**
1. **Semantic preservation**: Meaning preserved across format conversions
2. **Source traceability**: All converted data linked to original sources
3. **Analysis flexibility**: Researchers can switch modes based on research questions
4. **Quality tracking**: Confidence scores maintained through conversions

## Rationale

### **Why Cross-Modal Analysis?**

**1. Academic Research Diversity**:
Different research questions require different analytical approaches:

- **"Who are the most influential researchers?"** → Graph analysis (centrality)
- **"What theories correlate with publication impact?"** → Table analysis (correlation)
- **"Which papers are most similar to this one?"** → Vector analysis (similarity)
- **"How do research communities form over time?"** → Graph analysis (community detection)

**2. Research Method Integration**:
Academic research often requires combining multiple analytical approaches:
- **Exploratory phase**: Vector similarity to find related work
- **Network analysis**: Graph analysis to understand relationships
- **Statistical validation**: Table analysis for hypothesis testing
- **Result synthesis**: Cross-modal integration for comprehensive understanding

**3. Theory-Aware Processing**:
Social science theories often specify particular analytical approaches:
- **Stakeholder Theory**: Requires graph analysis (influence networks)
- **Diffusion of Innovations**: Requires both graph (adoption networks) and table (adoption rates)
- **Social Identity Theory**: Requires vector analysis (group similarity) and graph (group boundaries)

### **Why Not Single-Mode Analysis?**

**Graph-Only Analysis**:
- ❌ **Statistical limitations**: Poor support for correlations, regression analysis
- ❌ **Quantitative analysis**: Difficulty with statistical hypothesis testing
- ❌ **Temporal analysis**: Limited support for time-series analysis
- ❌ **Similarity search**: No efficient content-based similarity queries

**Table-Only Analysis**:
- ❌ **Relationship modeling**: Cannot efficiently model complex relationship networks
- ❌ **Path analysis**: No support for network path analysis
- ❌ **Community detection**: Cannot identify clusters in relationship networks
- ❌ **Influence analysis**: Limited support for influence propagation models

**Vector-Only Analysis**:
- ❌ **Explicit relationships**: Cannot model explicit relationship types
- ❌ **Network properties**: No access to network topology metrics
- ❌ **Statistical analysis**: Limited support for traditional statistical methods
- ❌ **Categorical analysis**: Difficulty with discrete categorical relationships

## Cross-Modal Architecture

### **Analysis Mode Definitions**
```python
class AnalysisMode(Enum):
    GRAPH = "graph"      # Neo4j graph queries and algorithms
    TABLE = "table"      # Pandas DataFrame statistical analysis
    VECTOR = "vector"    # Vector similarity and clustering

class CrossModalEntity:
    """Entity that can exist across multiple analysis modes"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.graph_node = None      # Neo4j node representation
        self.table_row = None       # DataFrame row representation  
        self.vector_embedding = None # Vector representation
        self.provenance_links = []   # Source document links
    
    def to_graph(self) -> GraphNode:
        """Convert to graph node for network analysis"""
        return GraphNode(
            id=self.entity_id,
            properties=self._extract_node_properties(),
            relationships=self._extract_relationships()
        )
    
    def to_table_row(self) -> Dict[str, Any]:
        """Convert to table row for statistical analysis"""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'confidence': self.confidence,
            **self._extract_scalar_properties()
        }
    
    def to_vector(self) -> np.ndarray:
        """Convert to vector for similarity analysis"""
        if self.vector_embedding is None:
            self.vector_embedding = self._generate_embedding()
        return self.vector_embedding
```

### **Cross-Modal Conversion System**
```python
class GraphToTableConverter:
    """Convert graph data to table format for statistical analysis"""
    
    def convert(self, graph_data: GraphData) -> pd.DataFrame:
        """Convert Neo4j graph results to pandas DataFrame"""
        
        # Extract nodes with properties
        nodes = []
        for node in graph_data.nodes:
            node_dict = {
                'entity_id': node.id,
                'entity_type': node.labels[0] if node.labels else 'Unknown',
                'confidence': node.get('confidence', 0.0)
            }
            # Add all node properties as columns
            node_dict.update(node.properties)
            nodes.append(node_dict)
        
        # Extract relationships as additional columns
        relationship_counts = self._count_relationships(graph_data)
        for node_dict in nodes:
            entity_id = node_dict['entity_id']
            node_dict.update(relationship_counts.get(entity_id, {}))
        
        return pd.DataFrame(nodes)
    
    def _count_relationships(self, graph_data: GraphData) -> Dict[str, Dict[str, int]]:
        """Count relationships for each entity"""
        counts = defaultdict(lambda: defaultdict(int))
        
        for relationship in graph_data.relationships:
            source_id = relationship.start_node.id
            target_id = relationship.end_node.id
            rel_type = relationship.type
            
            counts[source_id][f'{rel_type}_outgoing'] += 1
            counts[target_id][f'{rel_type}_incoming'] += 1
        
        return dict(counts)

class TableToVectorConverter:
    """Convert table data to vector format for similarity analysis"""
    
    def convert(self, table_data: pd.DataFrame) -> VectorSpace:
        """Convert DataFrame to vector space for similarity analysis"""
        
        # Separate numerical and categorical features
        numerical_features = table_data.select_dtypes(include=[np.number])
        categorical_features = table_data.select_dtypes(include=['object'])
        
        # Encode categorical features
        categorical_encoded = self._encode_categorical(categorical_features)
        
        # Combine features
        feature_matrix = np.hstack([
            numerical_features.values,
            categorical_encoded
        ])
        
        # Create vector space with entity mapping
        return VectorSpace(
            vectors=feature_matrix,
            entity_ids=table_data['entity_id'].tolist(),
            feature_names=self._get_feature_names(numerical_features, categorical_features)
        )

class VectorToGraphConverter:
    """Convert vector similarity results to graph format"""
    
    def convert(self, vector_results: VectorResults, similarity_threshold: float = 0.8) -> GraphData:
        """Convert vector similarity results to graph with similarity edges"""
        
        nodes = []
        relationships = []
        
        # Create nodes from entities
        for entity_id in vector_results.entity_ids:
            nodes.append(GraphNode(
                id=entity_id,
                labels=['Entity'],
                properties={'similarity_computed': True}
            ))
        
        # Create similarity relationships
        similarity_matrix = vector_results.similarity_matrix
        for i, entity_i in enumerate(vector_results.entity_ids):
            for j, entity_j in enumerate(vector_results.entity_ids):
                if i != j and similarity_matrix[i][j] > similarity_threshold:
                    relationships.append(GraphRelationship(
                        start_node_id=entity_i,
                        end_node_id=entity_j,
                        type='SIMILAR_TO',
                        properties={'similarity': similarity_matrix[i][j]}
                    ))
        
        return GraphData(nodes=nodes, relationships=relationships)
```

## Academic Research Applications

### **Multi-Modal Research Workflow**
```python
class AcademicResearchWorkflow:
    """Example academic research workflow using cross-modal analysis"""
    
    def analyze_research_community(self, papers: List[Document]) -> ResearchAnalysis:
        """Multi-modal analysis of research community"""
        
        # Phase 1: Document processing and entity extraction
        entities = self.extract_entities_from_papers(papers)
        
        # Phase 2: Graph analysis - identify research networks
        graph_data = self.build_research_graph(entities)
        communities = self.detect_research_communities(graph_data)  # Graph mode
        
        # Phase 3: Convert to table for statistical analysis
        table_data = self.orchestrator.convert_representation(
            data=graph_data,
            from_mode=AnalysisMode.GRAPH,
            to_mode=AnalysisMode.TABLE
        )
        
        # Phase 4: Statistical analysis of community characteristics
        community_stats = self.analyze_community_statistics(table_data.data)  # Table mode
        
        # Phase 5: Convert to vectors for similarity analysis
        vector_data = self.orchestrator.convert_representation(
            data=table_data.data,
            from_mode=AnalysisMode.TABLE,
            to_mode=AnalysisMode.VECTOR
        )
        
        # Phase 6: Identify similar research patterns
        similarity_clusters = self.find_research_patterns(vector_data.data)  # Vector mode
        
        # Phase 7: Cross-modal synthesis
        return ResearchAnalysis(
            communities=communities,
            statistics=community_stats,
            patterns=similarity_clusters,
            cross_modal_insights=self.synthesize_insights(communities, community_stats, similarity_clusters)
        )
```

### **Theory-Aware Cross-Modal Processing**
```python
class TheoryAwareCrossModal:
    """Apply social science theories across analysis modes"""
    
    def apply_stakeholder_theory(self, organization_data: Dict) -> StakeholderAnalysis:
        """Apply stakeholder theory using appropriate analysis modes"""
        
        # Graph mode: Identify stakeholder influence networks
        stakeholder_graph = self.build_stakeholder_graph(organization_data)
        influence_centrality = self.calculate_influence_centrality(stakeholder_graph)
        
        # Table mode: Calculate stakeholder salience scores (Mitchell et al. model)
        stakeholder_table = self.convert_to_stakeholder_table(stakeholder_graph)
        salience_scores = self.calculate_salience_scores(stakeholder_table)
        
        # Vector mode: Identify stakeholder similarity groups
        stakeholder_vectors = self.convert_to_stakeholder_vectors(stakeholder_table)
        stakeholder_clusters = self.cluster_similar_stakeholders(stakeholder_vectors)
        
        return StakeholderAnalysis(
            influence_rankings=influence_centrality,
            salience_scores=salience_scores,
            stakeholder_groups=stakeholder_clusters
        )
```

## Alternatives Considered

### **1. Single Analysis Mode Architecture**
**Rejected because**:
- **Limited research flexibility**: Cannot support diverse academic research approaches
- **Method constraints**: Researchers forced to use inappropriate analytical methods
- **Integration impossibility**: Cannot combine different analytical perspectives
- **Theory limitations**: Many theories require multiple analytical approaches

### **2. Manual Format Conversion**
```python
# Rejected approach
def manual_conversion_workflow():
    # Researcher manually exports and imports between formats
    graph_results = run_graph_analysis()
    export_to_csv(graph_results, "graph_data.csv")
    
    table_data = pd.read_csv("graph_data.csv")
    stats_results = run_statistical_analysis(table_data)
    # Loses provenance, error-prone, inefficient
```

**Rejected because**:
- **Provenance loss**: Manual conversion loses source traceability
- **Error-prone**: Manual steps introduce data corruption risk
- **Inefficient**: Significant researcher time spent on format conversion
- **Quality degradation**: Conversion quality depends on researcher expertise

### **3. Separate Analysis Systems**
**Rejected because**:
- **Integration complexity**: Multiple systems with different data formats
- **Consistency issues**: Different systems may produce conflicting results
- **Maintenance overhead**: Multiple systems to maintain and update
- **User complexity**: Researchers must learn multiple different interfaces

### **4. Format-Agnostic Single Interface**
**Rejected because**:
- **Performance penalties**: Generic interface cannot optimize for specific analysis types
- **Feature limitations**: Cannot expose mode-specific advanced features
- **Analysis constraints**: Forces lowest-common-denominator analytical capabilities
- **Academic research mismatch**: Research requires mode-specific optimizations

## Consequences

### **Positive**
- **Research flexibility**: Researchers can use optimal analysis mode for each research question
- **Method integration**: Multiple analytical approaches can be combined seamlessly
- **Source traceability**: All conversions maintain links to original sources
- **Quality preservation**: Confidence scores and quality metrics maintained across modes
- **Theory support**: Academic theories can specify appropriate analysis modes
- **Workflow efficiency**: Automatic conversion eliminates manual format translation

### **Negative**
- **System complexity**: Cross-modal conversion adds significant implementation complexity
- **Performance overhead**: Format conversions may introduce processing delays
- **Quality concerns**: Conversion quality depends on semantic mapping accuracy
- **Learning curve**: Researchers must understand when to use different analysis modes

## Implementation Requirements

### **Semantic Preservation**
All cross-modal conversions must preserve semantic meaning:
- **Entity identity**: Same entities maintain consistent identity across modes
- **Relationship semantics**: Relationship meaning preserved in appropriate target format
- **Confidence propagation**: Quality scores maintained through conversions
- **Source attribution**: All converted data linked to original sources

### **Provenance Integration**
Cross-modal operations must integrate with provenance service:
```python
def log_cross_modal_conversion(
    source_data: Any,
    target_data: Any,
    from_mode: AnalysisMode,
    to_mode: AnalysisMode,
    conversion_metadata: Dict
):
    """Log cross-modal conversion for research audit trail"""
    provenance_service.log_operation(
        operation="cross_modal_conversion",
        inputs={
            "source_mode": from_mode.value,
            "source_data_id": get_data_id(source_data)
        },
        outputs={
            "target_mode": to_mode.value,
            "target_data_id": get_data_id(target_data)
        },
        metadata=conversion_metadata
    )
```

### **Quality Tracking**
Quality service must track confidence through conversions:
- **Conversion degradation**: Model quality loss in format conversion
- **Aggregation confidence**: Handle confidence in data aggregation operations
- **Mode-specific quality**: Different quality metrics for different analysis modes

## Validation Criteria

- [ ] Data can be converted between all analysis mode combinations
- [ ] Semantic meaning preserved across all conversions
- [ ] Source provenance maintained through conversion chains
- [ ] Quality/confidence scores appropriately propagated
- [ ] Academic research workflows supported across all modes
- [ ] Theory-aware processing works across analysis modes
- [ ] Performance acceptable for typical academic research datasets

## Related ADRs

- **ADR-006**: Cross-Modal Analysis (original cross-modal concept)
- **ADR-009**: Bi-Store Database Strategy (graph and metadata storage for cross-modal)
- **ADR-008**: Core Service Architecture (cross-modal integration with services)
- **ADR-011**: Academic Research Focus (cross-modal designed for research flexibility)

This cross-modal orchestration enables KGAS to support the diverse analytical approaches required for rigorous academic research while maintaining the data integrity and source traceability essential for research validity.