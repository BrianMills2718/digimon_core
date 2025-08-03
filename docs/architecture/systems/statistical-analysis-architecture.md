# Statistical Analysis System Architecture

**Status**: Target Architecture  
**Purpose**: Define comprehensive statistical analysis capabilities for KGAS  
**Related ADR**: [ADR-021](../adrs/ADR-021-Statistical-Analysis-Integration.md)

## Overview

The Statistical Analysis System provides comprehensive quantitative analysis capabilities **aligned with KGAS's world analysis purpose**. This system enables researchers to perform advanced statistical analyses including SEM, multivariate analysis, and theory-driven model specification to **understand real-world phenomena through discourse analysis**, while maintaining full integration with graph and vector analysis capabilities.

## World Analysis-Focused Statistical Architecture

### **Statistical Analysis for World Phenomena Understanding**

**Primary Focus**: Use statistical methods to **quantify and analyze world phenomena** as revealed through discourse patterns, not just text properties.

**V13 Theory Integration**: Statistical analyses are **guided by V13 theory schemas** that specify:
- **Expected relationships** (`theoretical_structure.relations`) → Statistical model specifications
- **Measurable properties** (`entities.properties.measurement`) → Variable definitions and scales  
- **Mathematical formulas** (`algorithms.mathematical`) → Direct computational implementations
- **Analytical purposes** (`telos.analytical_questions`) → Appropriate statistical methods

**World Analysis Statistical Workflow**:
1. **Theory Selection** → V13 `telos.analytical_questions` matches human research questions
2. **Variable Extraction** → V13 `theoretical_structure` guides entity/property measurement from discourse
3. **Model Specification** → V13 `algorithms` section provides statistical formulations
4. **Analysis Execution** → Statistical methods reveal world patterns through discourse data
5. **Interpretation** → Results interpreted as insights about world phenomena, not text patterns

**Cross-Modal Statistical Integration**:
- **Graph → Statistics**: Network structures inform statistical model specifications (e.g., SEM path models)
- **Statistics → Graph**: Statistical relationships converted to analyzable network structures  
- **Vector → Statistics**: Semantic similarities inform clustering and classification analyses
- **Theory Guidance**: V13 `computational_representation.primary_format` determines optimal cross-modal flow

## System Architecture

### 1. Service Layer Architecture

```python
class StatisticalModelingService:
    """Core statistical analysis service with cross-modal integration"""
    
    def __init__(self, service_manager: ServiceManager):
        # Core service dependencies
        self.data_service = service_manager.data_service
        self.theory_repository = service_manager.theory_repository
        self.cross_modal_converter = service_manager.cross_modal_converter
        self.uncertainty_engine = service_manager.uncertainty_engine
        self.provenance_service = service_manager.provenance_service
        
        # Statistical engines
        self.descriptive_engine = DescriptiveStatsEngine()
        self.inferential_engine = InferentialStatsEngine()
        self.sem_engine = SEMEngine()
        self.multivariate_engine = MultivariateAnalysisEngine()
        self.bayesian_engine = BayesianAnalysisEngine()
        self.causal_engine = CausalInferenceEngine()
        self.experimental_design = ExperimentalDesignEngine()
        
        # Cross-modal integration
        self.stats_to_graph = StatisticalGraphConverter()
        self.stats_to_vector = StatisticalVectorConverter()
        self.graph_to_stats = GraphStatisticalConverter()
```

### 2. Statistical Engine Components

#### 2.1 Descriptive Statistics Engine

```python
class DescriptiveStatsEngine:
    """Comprehensive descriptive statistical analysis"""
    
    def __init__(self):
        self.calculator = DescriptiveCalculator()
        self.distribution_analyzer = DistributionAnalyzer()
        self.outlier_detector = OutlierDetector()
        
    async def analyze(self, data: DataFrame, config: DescriptiveConfig) -> DescriptiveResults:
        """Perform comprehensive descriptive analysis"""
        
        results = DescriptiveResults()
        
        # Central tendency and dispersion
        results.central_tendency = self.calculator.calculate_central_tendency(data)
        results.dispersion = self.calculator.calculate_dispersion(data)
        
        # Distribution analysis
        results.distribution = await self.distribution_analyzer.analyze_distribution(data)
        results.normality_tests = await self.distribution_analyzer.test_normality(data)
        
        # Outlier detection
        results.outliers = await self.outlier_detector.detect_outliers(
            data, 
            methods=['iqr', 'zscore', 'isolation_forest']
        )
        
        # Uncertainty quantification
        results.uncertainty = self._quantify_uncertainty(results, data.shape[0])
        
        return results
```

#### 2.2 SEM Engine Architecture

```python
class SEMEngine:
    """Structural Equation Modeling engine with theory integration"""
    
    def __init__(self):
        # Multiple backend support
        self.backends = {
            'lavaan': LavaanBackend(),      # R lavaan via rpy2
            'semopy': SemopyBackend(),      # Pure Python
            'lisrel': LisrelBackend(),      # Optional commercial
            'hybrid': HybridSEMBackend()    # Intelligent selection
        }
        
        # Components
        self.specification_builder = SEMSpecificationBuilder()
        self.model_validator = SEMModelValidator()
        self.fit_evaluator = ModelFitEvaluator()
        self.modification_analyzer = ModificationIndexAnalyzer()
        self.bootstrap_engine = BootstrapEngine()
        
    async def fit_model(self, 
                       data: DataFrame, 
                       specification: Union[str, Dict, TheorySchema],
                       config: SEMConfig = None) -> SEMResults:
        """Fit SEM model with comprehensive diagnostics"""
        
        # Convert specification to standard format
        if isinstance(specification, TheorySchema):
            sem_spec = await self.specification_builder.from_theory(specification)
        elif isinstance(specification, str):
            sem_spec = self.specification_builder.parse_lavaan_syntax(specification)
        else:
            sem_spec = SEMSpecification(**specification)
        
        # Validate specification
        validation = await self.model_validator.validate(sem_spec, data)
        if not validation.is_valid:
            raise SEMSpecificationError(validation.errors)
        
        # Select optimal backend
        backend = self._select_backend(sem_spec, config)
        
        # Fit model
        raw_results = await backend.fit(data, sem_spec)
        
        # Enhance results
        results = await self._enhance_results(raw_results, data, sem_spec)
        
        # Cross-modal conversion
        results.graph_representation = await self._create_graph_representation(results)
        results.path_diagram = await self._generate_path_diagram(results)
        
        return results
```

## Part 2: Theory-Driven Statistical Specification

### 3. Theory to Statistical Model Translation

```python
class TheoryToStatisticalModelTranslator:
    """Translate KGAS theory schemas to statistical model specifications"""
    
    def __init__(self):
        self.sem_mapper = TheoryToSEMMapper()
        self.regression_mapper = TheoryToRegressionMapper()
        self.multivariate_mapper = TheoryToMultivariateMapper()
        self.hypothesis_generator = TheoryHypothesisGenerator()
    
    async def translate_theory_to_statistical_models(self, 
                                                   theory_schema: TheorySchema) -> StatisticalModelSuite:
        """Generate complete statistical model suite from theory"""
        
        model_suite = StatisticalModelSuite(theory_id=theory_schema.theory_id)
        
        # Identify statistical analysis opportunities
        analysis_opportunities = self._identify_statistical_opportunities(theory_schema)
        
        # Generate appropriate models
        if analysis_opportunities.has_latent_constructs:
            model_suite.sem_models = await self.sem_mapper.create_sem_models(theory_schema)
        
        if analysis_opportunities.has_causal_paths:
            model_suite.regression_models = await self.regression_mapper.create_regression_models(theory_schema)
        
        if analysis_opportunities.has_multiple_outcomes:
            model_suite.multivariate_models = await self.multivariate_mapper.create_multivariate_models(theory_schema)
        
        # Generate testable hypotheses
        model_suite.hypotheses = await self.hypothesis_generator.generate_hypotheses(theory_schema)
        
        return model_suite

class TheoryToSEMMapper:
    """Map theory schemas to SEM specifications"""
    
    async def create_sem_models(self, theory_schema: TheorySchema) -> List[SEMSpecification]:
        """Create SEM specifications from theory"""
        
        sem_models = []
        
        # Extract latent constructs from entities with multiple indicators
        latent_constructs = self._extract_latent_constructs(theory_schema)
        
        # Build measurement models
        for construct in latent_constructs:
            measurement_model = self._build_measurement_model(construct)
            sem_models.append(measurement_model)
        
        # Build structural models from relationships
        if theory_schema.ontology.relationships:
            structural_model = self._build_structural_model(
                theory_schema.ontology.relationships,
                latent_constructs
            )
            sem_models.append(structural_model)
        
        # Build integrated model
        integrated_model = self._build_integrated_model(theory_schema)
        sem_models.append(integrated_model)
        
        return sem_models
    
    def _build_measurement_model(self, construct: LatentConstruct) -> SEMSpecification:
        """Build measurement model for latent construct"""
        
        specification = SEMSpecification(
            model_name=f"{construct.name}_measurement",
            model_type="cfa"
        )
        
        # Define latent variable
        specification.add_latent_variable(
            name=construct.name,
            indicators=[ind.name for ind in construct.indicators]
        )
        
        # Add measurement equations
        for i, indicator in enumerate(construct.indicators):
            if i == 0:
                # Fix first loading for identification
                specification.add_measurement(
                    latent=construct.name,
                    manifest=indicator.name,
                    fixed_loading=1.0
                )
            else:
                specification.add_measurement(
                    latent=construct.name,
                    manifest=indicator.name
                )
        
        # Add quality constraints from theory
        if construct.reliability_expectation:
            specification.add_constraint(
                f"reliability({construct.name}) >= {construct.reliability_expectation}"
            )
        
        return specification
```

## Part 3: Cross-Modal Statistical Integration

### 4. Statistical to Graph Conversion

```python
class StatisticalGraphConverter:
    """Convert statistical results to graph representations"""
    
    def __init__(self):
        self.node_builder = StatisticalNodeBuilder()
        self.edge_builder = StatisticalEdgeBuilder()
        self.layout_engine = StatisticalGraphLayout()
    
    async def sem_to_graph(self, sem_results: SEMResults) -> nx.DiGraph:
        """Convert SEM results to analyzable graph structure"""
        
        graph = nx.DiGraph()
        
        # Add latent variables as special nodes
        for latent in sem_results.latent_variables:
            node_attrs = {
                'node_type': 'latent_variable',
                'variance': latent.variance,
                'mean': latent.mean if hasattr(latent, 'mean') else 0,
                'reliability': latent.reliability,
                'ave': latent.average_variance_extracted,
                'node_size': self._scale_by_importance(latent.variance),
                'node_color': 'lightblue',
                'shape': 'ellipse'
            }
            graph.add_node(latent.name, **node_attrs)
        
        # Add manifest variables
        for manifest in sem_results.manifest_variables:
            node_attrs = {
                'node_type': 'manifest_variable',
                'mean': manifest.mean,
                'variance': manifest.variance,
                'loading': manifest.factor_loading if hasattr(manifest, 'factor_loading') else None,
                'communality': manifest.communality if hasattr(manifest, 'communality') else None,
                'node_size': self._scale_by_importance(manifest.communality or manifest.variance),
                'node_color': 'lightgreen',
                'shape': 'rectangle'
            }
            graph.add_node(manifest.name, **node_attrs)
        
        # Add measurement relationships
        for loading in sem_results.factor_loadings:
            edge_attrs = {
                'edge_type': 'measurement',
                'loading': loading.estimate,
                'standardized': loading.std_estimate,
                'std_error': loading.std_error,
                'z_value': loading.z_value,
                'p_value': loading.p_value,
                'significant': loading.p_value < 0.05,
                'edge_width': abs(loading.std_estimate) * 3,
                'edge_color': 'blue' if loading.estimate > 0 else 'red',
                'edge_style': 'dashed'
            }
            graph.add_edge(loading.latent, loading.manifest, **edge_attrs)
        
        # Add structural relationships
        for path in sem_results.structural_paths:
            edge_attrs = {
                'edge_type': 'structural',
                'coefficient': path.estimate,
                'standardized': path.std_estimate,
                'std_error': path.std_error,
                'z_value': path.z_value,
                'p_value': path.p_value,
                'significant': path.p_value < 0.05,
                'effect_size': self._calculate_effect_size(path),
                'edge_width': abs(path.std_estimate) * 3,
                'edge_color': 'green' if path.estimate > 0 else 'orange',
                'edge_style': 'solid',
                'arrow_style': '->'
            }
            graph.add_edge(path.from_var, path.to_var, **edge_attrs)
        
        # Add covariances as undirected edges
        for cov in sem_results.covariances:
            if cov.estimate != 0:
                edge_attrs = {
                    'edge_type': 'covariance',
                    'covariance': cov.estimate,
                    'correlation': cov.correlation,
                    'p_value': cov.p_value,
                    'edge_style': 'dotted',
                    'edge_color': 'gray',
                    'bidirectional': True
                }
                graph.add_edge(cov.var1, cov.var2, **edge_attrs)
        
        # Add model fit as graph attributes
        graph.graph['model_fit'] = {
            'chi_square': sem_results.fit_indices.chi_square,
            'cfi': sem_results.fit_indices.cfi,
            'rmsea': sem_results.fit_indices.rmsea,
            'srmr': sem_results.fit_indices.srmr
        }
        
        return graph
    
    async def correlation_matrix_to_graph(self, 
                                        corr_matrix: DataFrame,
                                        threshold: float = 0.3,
                                        p_values: DataFrame = None) -> nx.Graph:
        """Convert correlation matrix to network representation"""
        
        graph = nx.Graph()
        
        # Add nodes for each variable
        for var in corr_matrix.columns:
            graph.add_node(var, node_type='variable')
        
        # Add edges for significant correlations
        for i, var1 in enumerate(corr_matrix.columns):
            for j, var2 in enumerate(corr_matrix.columns[i+1:], i+1):
                corr = corr_matrix.iloc[i, j]
                
                if abs(corr) >= threshold:
                    edge_attrs = {
                        'correlation': corr,
                        'edge_weight': abs(corr),
                        'edge_color': 'blue' if corr > 0 else 'red',
                        'edge_width': abs(corr) * 3
                    }
                    
                    # Add p-value if available
                    if p_values is not None:
                        p_val = p_values.iloc[i, j]
                        edge_attrs['p_value'] = p_val
                        edge_attrs['significant'] = p_val < 0.05
                    
                    graph.add_edge(var1, var2, **edge_attrs)
        
        # Calculate network metrics
        graph.graph['density'] = nx.density(graph)
        graph.graph['clustering'] = nx.average_clustering(graph)
        
        return graph
```

### 5. Graph-Informed Statistical Analysis

```python
class GraphStatisticalConverter:
    """Use graph structure to inform statistical analysis"""
    
    def __init__(self):
        self.path_analyzer = GraphPathAnalyzer()
        self.community_detector = CommunityDetector()
        self.centrality_calculator = CentralityCalculator()
    
    async def graph_to_regression_specification(self, 
                                              graph: nx.DiGraph,
                                              target_variable: str) -> RegressionSpecification:
        """Generate regression model from graph structure"""
        
        spec = RegressionSpecification()
        
        # Identify direct predictors (in-edges to target)
        direct_predictors = list(graph.predecessors(target_variable))
        spec.add_predictors(direct_predictors)
        
        # Identify indirect effects through paths
        for node in graph.nodes():
            if node != target_variable and node not in direct_predictors:
                paths = list(nx.all_simple_paths(graph, node, target_variable, cutoff=3))
                if paths:
                    # Add as potential mediator
                    spec.add_mediation_path(paths[0])
        
        # Identify potential moderators (nodes connected to predictors)
        for predictor in direct_predictors:
            neighbors = set(graph.neighbors(predictor)) - {target_variable}
            for neighbor in neighbors:
                spec.add_interaction(predictor, neighbor)
        
        # Use centrality to suggest variable importance
        centrality = nx.betweenness_centrality(graph)
        spec.set_variable_weights({k: v for k, v in centrality.items() 
                                  if k in direct_predictors})
        
        return spec
    
    async def graph_to_sem_specification(self, 
                                       graph: nx.DiGraph,
                                       theory_guidance: Dict = None) -> SEMSpecification:
        """Generate SEM model from graph structure"""
        
        spec = SEMSpecification()
        
        # Detect communities as potential latent variables
        communities = await self.community_detector.detect_communities(graph)
        
        for comm_id, members in communities.items():
            if len(members) > 2:
                # Create latent variable for community
                latent_name = f"Factor_{comm_id}"
                if theory_guidance and comm_id in theory_guidance:
                    latent_name = theory_guidance[comm_id]['name']
                
                spec.add_latent_variable(latent_name, indicators=members)
        
        # Use graph paths for structural model
        for latent1 in spec.latent_variables:
            for latent2 in spec.latent_variables:
                if latent1 != latent2:
                    # Check if path exists between community members
                    if self._path_exists_between_communities(
                        graph, 
                        communities[latent1], 
                        communities[latent2]
                    ):
                        spec.add_structural_path(latent1, latent2)
        
        return spec
```

## Part 4: Implementation Details

### 6. Tool Implementation Examples

#### T46: Structural Equation Modeling Tool

```python
class T46_StructuralEquationModeling(KGASTool):
    """Comprehensive SEM capabilities with cross-modal integration"""
    
    def __init__(self):
        super().__init__()
        self.tool_id = "T46"
        self.name = "Structural Equation Modeling"
        self.category = "statistical_analysis"
        
        # Initialize backends
        self.backends = {
            'lavaan': LavaanBackend(),
            'semopy': SemopyBackend(),
            'hybrid': HybridBackend()
        }
        
        # Components
        self.validator = SEMValidator()
        self.visualizer = SEMVisualizer()
        self.reporter = SEMReporter()
    
    @input_validation(schema=SEMInputSchema)
    @output_validation(schema=SEMOutputSchema)
    @provenance_tracking
    @uncertainty_propagation
    async def execute(self, 
                     data: Union[str, DataFrame],
                     specification: Union[str, Dict],
                     backend: str = 'hybrid',
                     bootstrap_samples: int = 1000,
                     theory_id: str = None) -> ToolOutput:
        """Execute SEM analysis with full integration"""
        
        try:
            # Load data if path provided
            if isinstance(data, str):
                data = await self.load_data(data)
            
            # Convert theory to specification if provided
            if theory_id:
                theory = await self.theory_repository.get_theory(theory_id)
                specification = await self.theory_to_sem_mapper.create_specification(theory)
            
            # Validate inputs
            validation = await self.validator.validate_inputs(data, specification)
            if not validation.is_valid:
                return ToolOutput(
                    success=False,
                    error=f"Validation failed: {validation.errors}"
                )
            
            # Run SEM analysis
            backend_engine = self.backends[backend]
            sem_results = await backend_engine.fit(data, specification)
            
            # Bootstrap confidence intervals
            if bootstrap_samples > 0:
                bootstrap_results = await backend_engine.bootstrap(
                    data, 
                    specification, 
                    n_samples=bootstrap_samples
                )
                sem_results.bootstrap_ci = bootstrap_results
            
            # Generate cross-modal representations
            graph_repr = await self.stats_to_graph_converter.sem_to_graph(sem_results)
            vector_repr = await self.stats_to_vector_converter.sem_to_embeddings(sem_results)
            
            # Create visualizations
            path_diagram = await self.visualizer.create_path_diagram(sem_results)
            fit_plot = await self.visualizer.create_fit_indices_plot(sem_results)
            
            # Generate report
            report = await self.reporter.generate_sem_report(
                sem_results,
                include_technical=True,
                apa_format=True
            )
            
            # Track provenance
            self.provenance_service.record_operation(
                tool_id=self.tool_id,
                inputs={'data_shape': data.shape, 'specification': specification},
                outputs={'fit_indices': sem_results.fit_indices.to_dict()},
                parameters={'backend': backend, 'bootstrap_samples': bootstrap_samples}
            )
            
            return ToolOutput(
                success=True,
                data={
                    'model_results': sem_results,
                    'graph_representation': graph_repr,
                    'vector_representation': vector_repr,
                    'visualizations': {
                        'path_diagram': path_diagram,
                        'fit_indices': fit_plot
                    },
                    'report': report
                },
                metadata={
                    'execution_time': sem_results.execution_time,
                    'converged': sem_results.converged,
                    'warnings': sem_results.warnings
                },
                uncertainty=self._calculate_model_uncertainty(sem_results)
            )
            
        except Exception as e:
            self.logger.error(f"SEM analysis failed: {str(e)}")
            return ToolOutput(
                success=False,
                error=str(e),
                traceback=traceback.format_exc()
            )
```

### 7. Workflow Integration

```python
class StatisticalAnalysisWorkflow:
    """Orchestrate complex statistical analysis workflows"""
    
    def __init__(self, orchestrator: PipelineOrchestrator):
        self.orchestrator = orchestrator
        self.statistical_service = orchestrator.services.statistical_service
        self.cross_modal_service = orchestrator.services.cross_modal_service
    
    async def theory_driven_analysis_workflow(self, 
                                            theory_id: str,
                                            data_sources: List[str],
                                            analysis_config: StatisticalConfig):
        """Complete theory-driven statistical analysis workflow"""
        
        workflow_id = str(uuid.uuid4())
        
        # Step 1: Load theory and data
        theory = await self.orchestrator.theory_repository.get_theory(theory_id)
        data = await self.orchestrator.load_and_merge_data(data_sources)
        
        # Step 2: Generate statistical models from theory
        model_suite = await self.statistical_service.generate_models_from_theory(theory)
        
        # Step 3: Run descriptive analysis
        descriptive_results = await self.statistical_service.run_descriptive_analysis(data)
        
        # Step 4: Test statistical assumptions
        assumptions = await self.statistical_service.test_assumptions(data, model_suite)
        
        # Step 5: Run primary analyses
        analysis_results = {}
        
        # SEM if applicable
        if model_suite.has_sem_models:
            sem_results = await self.statistical_service.run_sem_analysis(
                data,
                model_suite.primary_sem_model
            )
            analysis_results['sem'] = sem_results
            
            # Convert to graph for network analysis
            sem_graph = await self.cross_modal_service.sem_to_graph(sem_results)
            network_insights = await self.orchestrator.graph_service.analyze_sem_network(sem_graph)
            analysis_results['network_insights'] = network_insights
        
        # Regression models
        if model_suite.has_regression_models:
            regression_results = await self.statistical_service.run_regression_suite(
                data,
                model_suite.regression_models
            )
            analysis_results['regression'] = regression_results
        
        # Multivariate analyses
        if model_suite.has_multivariate_models:
            multivariate_results = await self.statistical_service.run_multivariate_analyses(
                data,
                model_suite.multivariate_models
            )
            analysis_results['multivariate'] = multivariate_results
        
        # Step 6: Cross-modal integration
        integrated_insights = await self._integrate_cross_modal_insights(
            analysis_results,
            descriptive_results
        )
        
        # Step 7: Generate comprehensive report
        report = await self.statistical_service.generate_comprehensive_report(
            theory=theory,
            descriptive_results=descriptive_results,
            analysis_results=analysis_results,
            integrated_insights=integrated_insights,
            format='publication_ready'
        )
        
        return WorkflowResult(
            workflow_id=workflow_id,
            success=True,
            results=analysis_results,
            report=report,
            visualizations=self._collect_visualizations(analysis_results),
            provenance=self.orchestrator.get_workflow_provenance(workflow_id)
        )
```

## Part 5: Performance and Validation

### 8. Performance Optimization

```python
class StatisticalPerformanceOptimizer:
    """Optimize statistical computations for large datasets"""
    
    def __init__(self):
        self.cache_manager = StatisticalCacheManager()
        self.parallel_executor = ParallelStatisticalExecutor()
        self.chunk_processor = ChunkwiseProcessor()
    
    async def optimize_large_sem(self, 
                               data: DataFrame,
                               specification: SEMSpecification) -> OptimizationStrategy:
        """Optimize SEM for large datasets"""
        
        strategy = OptimizationStrategy()
        
        # Check if we can use cached sufficient statistics
        cache_key = self._generate_cache_key(data, specification)
        cached_stats = await self.cache_manager.get_sufficient_statistics(cache_key)
        
        if cached_stats:
            strategy.use_cached_statistics = True
            strategy.sufficient_statistics = cached_stats
        else:
            # Calculate and cache sufficient statistics
            if data.shape[0] > 10000:
                strategy.use_sampling = True
                strategy.sample_size = self._calculate_optimal_sample_size(data.shape)
            
            if specification.n_parameters > 100:
                strategy.use_sparse_methods = True
                strategy.sparse_algorithm = 'coordinate_descent'
        
        # Parallel processing for bootstrap
        if data.shape[0] * specification.n_parameters > 1e6:
            strategy.parallel_bootstrap = True
            strategy.n_workers = self._calculate_optimal_workers()
        
        return strategy
    
    async def chunked_correlation_analysis(self, 
                                         data: DataFrame,
                                         chunk_size: int = 10000) -> CorrelationResults:
        """Calculate correlations in chunks for memory efficiency"""
        
        n_vars = data.shape[1]
        correlation_matrix = np.zeros((n_vars, n_vars))
        p_value_matrix = np.zeros((n_vars, n_vars))
        
        # Process in chunks
        for chunk in self.chunk_processor.generate_chunks(data, chunk_size):
            chunk_corr, chunk_p = await self._calculate_chunk_correlations(chunk)
            
            # Update running statistics
            correlation_matrix = self._update_correlation_estimate(
                correlation_matrix, 
                chunk_corr, 
                chunk.shape[0]
            )
        
        return CorrelationResults(
            correlations=correlation_matrix,
            p_values=p_value_matrix,
            n_observations=data.shape[0]
        )
```

### 9. Validation Framework

```python
class StatisticalValidationFramework:
    """Comprehensive validation for statistical analyses"""
    
    def __init__(self):
        self.assumption_tester = AssumptionTester()
        self.diagnostic_calculator = DiagnosticCalculator()
        self.sensitivity_analyzer = SensitivityAnalyzer()
    
    async def validate_sem_model(self, 
                               sem_results: SEMResults,
                               data: DataFrame) -> ValidationReport:
        """Comprehensive SEM model validation"""
        
        report = ValidationReport()
        
        # Model fit validation
        fit_validation = self._validate_model_fit(sem_results.fit_indices)
        report.add_section('model_fit', fit_validation)
        
        # Assumption testing
        assumptions = await self.assumption_tester.test_sem_assumptions(data, sem_results)
        report.add_section('assumptions', assumptions)
        
        # Diagnostic checks
        diagnostics = await self.diagnostic_calculator.calculate_sem_diagnostics(sem_results)
        report.add_section('diagnostics', diagnostics)
        
        # Sensitivity analysis
        sensitivity = await self.sensitivity_analyzer.analyze_sem_sensitivity(
            sem_results, 
            data,
            methods=['case_deletion', 'parameter_perturbation']
        )
        report.add_section('sensitivity', sensitivity)
        
        # Cross-validation
        cv_results = await self._cross_validate_sem(data, sem_results.specification)
        report.add_section('cross_validation', cv_results)
        
        # Generate recommendations
        report.recommendations = self._generate_validation_recommendations(report)
        
        return report
    
    def _validate_model_fit(self, fit_indices: FitIndices) -> FitValidation:
        """Validate model fit against standard criteria"""
        
        validation = FitValidation()
        
        # CFI criteria
        if fit_indices.cfi >= 0.95:
            validation.cfi_status = 'excellent'
        elif fit_indices.cfi >= 0.90:
            validation.cfi_status = 'acceptable'
        else:
            validation.cfi_status = 'poor'
        
        # RMSEA criteria
        if fit_indices.rmsea <= 0.05:
            validation.rmsea_status = 'excellent'
        elif fit_indices.rmsea <= 0.08:
            validation.rmsea_status = 'acceptable'
        else:
            validation.rmsea_status = 'poor'
        
        # SRMR criteria
        if fit_indices.srmr <= 0.05:
            validation.srmr_status = 'excellent'
        elif fit_indices.srmr <= 0.08:
            validation.srmr_status = 'acceptable'
        else:
            validation.srmr_status = 'poor'
        
        # Overall assessment
        statuses = [validation.cfi_status, validation.rmsea_status, validation.srmr_status]
        if all(s == 'excellent' for s in statuses):
            validation.overall = 'excellent'
        elif all(s in ['excellent', 'acceptable'] for s in statuses):
            validation.overall = 'acceptable'
        else:
            validation.overall = 'poor'
        
        return validation
```

## Integration Points

### Service Integration
- Integrates with all core KGAS services
- Uses uncertainty engine for confidence quantification
- Leverages provenance service for reproducibility
- Connects with theory repository for model generation

### Cross-Modal Integration
- Statistical results convertible to graph structures
- Graph metrics inform statistical model specification
- Vector embeddings enhance clustering and classification
- Unified uncertainty propagation across modes

### Data Architecture
- SQLite stores model specifications and results
- Neo4j stores statistical models as graphs
- Cached sufficient statistics for performance
- Complete provenance tracking

## Performance Characteristics

### Scalability
- Handles datasets with 1M+ observations
- SEM models with 100+ variables
- Parallel bootstrap for confidence intervals
- Intelligent backend selection for optimal performance

### Resource Management
- Chunked processing for memory efficiency
- Cached computations for repeated analyses
- Async execution for non-blocking operations
- Progress tracking for long-running analyses

## Validation and Quality

### Statistical Rigor
- Comprehensive assumption testing
- Multiple fit indices for model evaluation
- Bootstrap confidence intervals
- Cross-validation for model stability

### Academic Standards
- APA-formatted output tables
- Publication-ready visualizations
- Complete diagnostic information
- Reproducible analysis workflows

## Future Extensions

### Planned Enhancements
1. Real-time collaborative statistical analysis
2. Automated model selection algorithms
3. Bayesian network integration
4. Time-varying coefficient models
5. Spatial statistical methods

### Research Opportunities
1. Graph-informed SEM specification
2. Cross-modal hypothesis testing
3. Theory-driven model comparison
4. Uncertainty-aware statistical inference

## Conclusion

The Statistical Analysis System transforms KGAS into a comprehensive quantitative research platform while maintaining its unique cross-modal and theory-aware advantages. By integrating advanced statistical methods with graph and vector analysis capabilities, researchers can perform novel analyses that bridge traditionally separate analytical paradigms.