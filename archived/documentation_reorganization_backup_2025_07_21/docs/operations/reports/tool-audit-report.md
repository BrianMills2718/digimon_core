# Tool Functionality Audit Report

Generated: 2025-07-16T11:31:22.433969

## Summary
- Total tools tested: 54
- Functional tools: 41
- Success rate: 75.9%

## Detailed Results

### src.tools.phase1.vertical_slice_workflow
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:18.343862
- Functional Tests:
  - VerticalSliceWorkflow: instantiation successful

### src.tools.phase1.t15a_text_chunker
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:20.045976
- Functional Tests:
  - TextChunker: instantiation successful
  - TextChunker: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t01_pdf_loader
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:20.046174
- Functional Tests:
  - PDFLoader: instantiation successful
  - PDFLoader: get_tool_info() returned <class 'dict'>
  - PDFLoader: load_pdf() functional

### src.tools.phase1.t49_enhanced_query
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:20.046814
- Functional Tests:
  - EnhancedMultiHopQuery: instantiation successful
  - EnhancedMultiHopQuery: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t23a_spacy_ner
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:20.801421
- Functional Tests:
  - SpacyNER: instantiation successful
  - SpacyNER: get_tool_info() returned <class 'dict'>
  - SpacyNER: extract_entities() functional

### src.tools.phase1.t34_edge_builder
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.162923
- Functional Tests:
  - EdgeBuilder: instantiation successful
  - EdgeBuilder: get_tool_info() returned <class 'dict'>

### src.tools.phase1.neo4j_error_handler
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.168990
- Functional Tests:
  - Neo4jErrorHandler: instantiation successful

### src.tools.phase1.t23c_llm_entity_extractor
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.169097
- Functional Tests:
  - LLMEntityExtractor: instantiation successful
  - LLMEntityExtractor: get_tool_info() returned <class 'dict'>

### src.tools.phase1.phase1_mcp_tools
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.192850
- Functional Tests:
  - Phase1MCPToolsManager: instantiation successful
  - Phase1MCPToolsManager: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t41_text_embedder
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:21.250389
- Error: No classes found in module

### src.tools.phase1.base_neo4j_tool
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.264595
- Functional Tests:
  - BaseNeo4jTool: instantiation successful

### src.tools.phase1.t49_multihop_query
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.270686
- Functional Tests:
  - MultiHopQuery: instantiation successful
  - MultiHopQuery: get_tool_info() returned <class 'dict'>
  - MultiHopQueryEngine: instantiation successful
  - MultiHopQueryEngine: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t68_pagerank
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.287902
- Functional Tests:
  - PageRankCalculator: instantiation successful
  - PageRankCalculator: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t68_pagerank_optimized
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.294076
- Functional Tests:
  - PageRankCalculatorOptimized: instantiation successful
  - PageRankCalculatorOptimized: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t31_entity_builder
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.299962
- Functional Tests:
  - EntityBuilder: instantiation successful
  - EntityBuilder: get_tool_info() returned <class 'dict'>

### src.tools.phase1.t27_relationship_extractor
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.305910
- Functional Tests:
  - RelationshipExtractor: instantiation successful
  - RelationshipExtractor: get_tool_info() returned <class 'dict'>

### src.tools.phase3.basic_multi_document_workflow
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.593367
- Functional Tests:
  - BasicMultiDocumentWorkflow: instantiation successful

### src.tools.phase3.t301_multi_document_fusion
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.594878
- Functional Tests:
  - BasicMultiDocumentWorkflow: instantiation successful
  - BasicMultiDocumentWorkflow: get_tool_info() returned <class 'dict'>
  - ConflictResolver: instantiation successful
  - ConflictResolver: get_tool_info() returned <class 'dict'>
  - ConsistencyChecker: instantiation successful
  - ConsistencyChecker: get_tool_info() returned <class 'dict'>
  - EntityClusterFinder: instantiation successful
  - EntityClusterFinder: get_tool_info() returned <class 'dict'>
  - EntitySimilarityCalculator: instantiation successful
  - EntitySimilarityCalculator: get_tool_info() returned <class 'dict'>
  - MultiDocumentFusion: instantiation successful
  - MultiDocumentFusion: get_tool_info() returned <class 'dict'>
  - RelationshipMerger: instantiation successful
  - RelationshipMerger: get_tool_info() returned <class 'dict'>

### src.tools.phase2.interactive_graph_visualizer
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.729327
- Functional Tests:
  - InteractiveGraphVisualizer: instantiation successful
  - InteractiveGraphVisualizer: get_tool_info() returned <class 'dict'>

### src.tools.phase2.t23c_ontology_aware_extractor
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.911034
- Functional Tests:
  - OntologyAwareExtractor: instantiation successful
  - OntologyAwareExtractor: get_tool_info() returned <class 'dict'>

### src.tools.phase2.t31_ontology_graph_builder
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.932042
- Functional Tests:
  - OntologyAwareGraphBuilder: instantiation successful

### src.tools.phase2.enhanced_vertical_slice_workflow
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.935649
- Functional Tests:
  - EnhancedVerticalSliceWorkflow: instantiation successful

### src.core.schema_enforcer
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:21.990654
- Error: No classes found in module

### src.core.input_validator
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.990987
- Functional Tests:
  - InputValidator: instantiation successful

### src.core.production_validator
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:21.991095
- Error: 1 tests failed
- Functional Tests:
  - ProductionValidator: FAILED - ProductionValidator.__init__() missing 1 required positional argument: 'config_manager'

### src.core.pipeline_orchestrator
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:21.991438
- Functional Tests:
  - PipelineOrchestrator: instantiation successful

### src.core.ontology_storage_service
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.008868
- Functional Tests:
  - OntologyStorageService: instantiation successful

### src.core.ontology_validator
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.009298
- Functional Tests:
  - OntologyValidator: instantiation successful

### src.core.error_handler
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.009411
- Functional Tests:
  - ProductionErrorHandler: instantiation successful
  - ProductionErrorHandler: get_tool_info() returned <class 'dict'>

### src.core.identity_service
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.010487
- Functional Tests:
  - IdentityService: instantiation successful
  - IdentityService: get_tool_info() returned <class 'dict'>

### src.core.graphrag_phase_interface
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.010625
- Error: No classes found in module

### src.core.advanced_data_models
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.010735
- Error: No classes found in module

### src.core.tool_adapters
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.010849
- Functional Tests:
  - BaseToolAdapter: instantiation successful
  - EdgeBuilderAdapter: instantiation successful
  - EntityBuilderAdapter: instantiation successful
  - InteractiveGraphVisualizerAdapter: instantiation successful
  - MultiDocumentFusionAdapter: instantiation successful
  - MultiHopQueryAdapter: instantiation successful
  - OntologyAwareExtractorAdapter: instantiation successful
  - OntologyGraphBuilderAdapter: instantiation successful
  - PDFLoaderAdapter: instantiation successful
  - PageRankAdapter: instantiation successful
  - RelationshipExtractorAdapter: instantiation successful
  - SpacyNERAdapter: instantiation successful
  - TextChunkerAdapter: instantiation successful

### src.core.phase_adapters
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.385350
- Error: 1 tests failed
- Functional Tests:
  - IntegratedPipelineOrchestrator: instantiation successful
  - Phase1Adapter: instantiation successful
  - Phase2Adapter: instantiation successful
  - Phase3Adapter: instantiation successful
  - TheoryValidator: FAILED - TheoryValidator.__init__() missing 1 required positional argument: 'config'

### src.core.tool_factory
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.386284
- Error: No classes found in module

### src.core.provenance_service
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.386381
- Functional Tests:
  - ProvenanceService: instantiation successful
  - ProvenanceService: get_tool_info() returned <class 'dict'>

### src.core.health_checker
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.386484
- Error: 1 tests failed
- Functional Tests:
  - HealthChecker: FAILED - HealthChecker.__init__() missing 1 required positional argument: 'config_manager'

### src.core.theory_integration
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.391835
- Error: No classes found in module

### src.core.config
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.391940
- Functional Tests:
  - ConfigurationManager: instantiation successful

### src.core.config_manager
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.392051
- Functional Tests:
  - ConfigManager: instantiation successful

### src.core.quality_service
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.395142
- Error: 1 tests failed
- Functional Tests:
  - QualityService: instantiation successful
  - QualityService: FAILED - 'str' object has no attribute 'rule_type'

### src.core.contract_validator
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.395276
- Functional Tests:
  - ContractValidator: instantiation successful

### src.core.data_models
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.401767
- Functional Tests:
  - DataModelsManager: instantiation successful
  - DataModelsManager: get_tool_info() returned <class 'dict'>

### src.core.entity_schema
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.401909
- Error: No classes found in module

### src.core.service_manager
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.402011
- Functional Tests:
  - ServiceManager: instantiation successful

### src.core.workflow_state_service
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.402102
- Functional Tests:
  - WorkflowStateService: instantiation successful

### src.core.api_contracts
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.403251
- Functional Tests:
  - APIContractValidator: instantiation successful

### src.core.neo4j_manager
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.404454
- Functional Tests:
  - Neo4jDockerManager: instantiation successful

### src.core.evidence_logger
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.404556
- Error: No classes found in module

### src.core.logging_config
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.404639
- Functional Tests:
  - LoggingConfigManager: instantiation successful
  - LoggingConfigManager: get_tool_info() returned <class 'dict'>

### src.core.pipeline_validation
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.407152
- Functional Tests:
  - PipelineValidator: instantiation successful

### src.core.tool_adapter_bridge
- Status: BROKEN
- Timestamp: 2025-07-16T11:31:22.413990
- Error: No classes found in module

### src.ui.graphrag_ui
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.414129
- Functional Tests:
  - GraphRAGUI: instantiation successful
  - GraphRAGUI: get_tool_info() returned <class 'dict'>

### src.ui.ui_phase_adapter
- Status: FUNCTIONAL
- Timestamp: 2025-07-16T11:31:22.432425
- Functional Tests:
  - UIPhaseManager: instantiation successful

