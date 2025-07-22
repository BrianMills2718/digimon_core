# Tool Status Report

Generated: 2025-07-16T00:14:37.771117

## Summary

- Total tools: 29
- Working tools: 28
- Broken tools: 0

## Status Breakdown

- MODULE_ONLY: 1
- WORKING: 28

## Detailed Results

### t01_pdf_loader

- **Status**: WORKING
- **Module**: `src.tools.phase1.t01_pdf_loader`
- **Class**: `PDFLoader`
- **Basic Functionality**: supports 1 formats
- **Methods Found**: __init__, __str__, __repr__, load_pdf, get_supported_formats, get_tool_info
- **Timestamp**: 2025-07-16T00:14:34.324845

### t15a_text_chunker

- **Status**: WORKING
- **Module**: `src.tools.phase1.t15a_text_chunker`
- **Class**: `TextChunker`
- **Basic Functionality**: unknown
- **Methods Found**: __init__, __str__, __repr__, chunk_text, get_tool_info
- **Timestamp**: 2025-07-16T00:14:34.366731

### t23a_spacy_ner

- **Status**: WORKING
- **Module**: `src.tools.phase1.t23a_spacy_ner`
- **Class**: `SpacyNER`
- **Basic Functionality**: can extract entities
- **Methods Found**: __init__, __str__, __repr__, extract_entities, get_tool_info
- **Timestamp**: 2025-07-16T00:14:34.366975

### t27_relationship_extractor

- **Status**: WORKING
- **Module**: `src.tools.phase1.t27_relationship_extractor`
- **Class**: `RelationshipExtractor`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:35.578500

### t31_entity_builder

- **Status**: WORKING
- **Module**: `src.tools.phase1.t31_entity_builder`
- **Class**: `EntityBuilder`
- **Basic Functionality**: unknown
- **Methods Found**: __init__, __str__, __repr__, get_tool_info
- **Timestamp**: 2025-07-16T00:14:35.893948

### t34_edge_builder

- **Status**: WORKING
- **Module**: `src.tools.phase1.t34_edge_builder`
- **Class**: `EdgeBuilder`
- **Basic Functionality**: unknown
- **Methods Found**: __init__, __str__, __repr__, get_tool_info
- **Timestamp**: 2025-07-16T00:14:35.915968

### t49_multihop_query

- **Status**: WORKING
- **Module**: `src.tools.phase1.t49_multihop_query`
- **Class**: `MultiHopQuery`
- **Basic Functionality**: unknown
- **Methods Found**: __init__, __str__, __repr__, get_tool_info
- **Timestamp**: 2025-07-16T00:14:35.922676

### t68_pagerank

- **Status**: WORKING
- **Module**: `src.tools.phase1.t68_pagerank`
- **Class**: `PageRank`
- **Basic Functionality**: unknown
- **Methods Found**: __init__, __str__, __repr__, calculate_pagerank, get_tool_info
- **Timestamp**: 2025-07-16T00:14:35.928894

### base_neo4j_tool

- **Status**: WORKING
- **Module**: `src.tools.phase1.base_neo4j_tool`
- **Class**: `BaseNeo4jTool`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:36.003295

### vertical_slice_workflow

- **Status**: WORKING
- **Module**: `src.tools.phase1.vertical_slice_workflow`
- **Class**: `VerticalSliceWorkflow`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:36.009281

### t68_pagerank_optimized

- **Status**: WORKING
- **Module**: `src.tools.phase1.t68_pagerank_optimized`
- **Class**: `PageRankOptimized`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:36.545898

### t23c_llm_entity_extractor

- **Status**: WORKING
- **Module**: `src.tools.phase1.t23c_llm_entity_extractor`
- **Class**: `LLMEntityExtractor`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:36.552197

### t41_text_embedder

- **Status**: WORKING
- **Module**: `src.tools.phase1.t41_text_embedder`
- **Class**: `TextEmbedder`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.089956

### t49_enhanced_query

- **Status**: WORKING
- **Module**: `src.tools.phase1.t49_enhanced_query`
- **Class**: `EnhancedQuery`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.262264

### enhanced_vertical_slice_workflow

- **Status**: WORKING
- **Module**: `src.tools.phase2.enhanced_vertical_slice_workflow`
- **Class**: `EnhancedVerticalSliceWorkflow`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.304006

### interactive_graph_visualizer

- **Status**: WORKING
- **Module**: `src.tools.phase2.interactive_graph_visualizer`
- **Class**: `InteractiveGraphVisualizer`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.562473

### t23c_ontology_aware_extractor

- **Status**: WORKING
- **Module**: `src.tools.phase2.t23c_ontology_aware_extractor`
- **Class**: `OntologyAwareExtractor`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.628594

### t31_ontology_graph_builder

- **Status**: WORKING
- **Module**: `src.tools.phase2.t31_ontology_graph_builder`
- **Class**: `OntologyAwareGraphBuilder`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.646387

### basic_multi_document_workflow

- **Status**: WORKING
- **Module**: `src.tools.phase3.basic_multi_document_workflow`
- **Class**: `BasicMultiDocumentWorkflow`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.650452

### t301_multi_document_fusion

- **Status**: WORKING
- **Module**: `src.tools.phase3.t301_multi_document_fusion`
- **Class**: `MultiDocumentFusion`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.652244

### identity_service

- **Status**: WORKING
- **Module**: `src.core.identity_service`
- **Class**: `IdentityService`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719599

### provenance_service

- **Status**: WORKING
- **Module**: `src.core.provenance_service`
- **Class**: `ProvenanceService`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719644

### quality_service

- **Status**: WORKING
- **Module**: `src.core.quality_service`
- **Class**: `QualityService`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719660

### service_manager

- **Status**: WORKING
- **Module**: `src.core.service_manager`
- **Class**: `ServiceManager`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719677

### neo4j_manager

- **Status**: WORKING
- **Module**: `src.core.neo4j_manager`
- **Class**: `Neo4jManager`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719691

### config

- **Status**: WORKING
- **Module**: `src.core.config`
- **Class**: `Config`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719881

### pipeline_orchestrator

- **Status**: WORKING
- **Module**: `src.core.pipeline_orchestrator`
- **Class**: `PipelineOrchestrator`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.719899

### tool_factory

- **Status**: MODULE_ONLY
- **Module**: `src.core.tool_factory`
- **Class**: `None`
- **Basic Functionality**: module imported successfully
- **Methods Found**: 
- **Timestamp**: 2025-07-16T00:14:37.745994

### graphrag_ui

- **Status**: WORKING
- **Module**: `src.ui.graphrag_ui`
- **Class**: `GraphRAGUI`
- **Basic Functionality**: instantiated successfully
- **Methods Found**: __init__, __str__, __repr__
- **Timestamp**: 2025-07-16T00:14:37.746028

