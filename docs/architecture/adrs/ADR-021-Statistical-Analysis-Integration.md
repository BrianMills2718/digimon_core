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