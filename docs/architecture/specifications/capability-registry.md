**Doc status**: Living – auto-checked by doc-governance CI

# GraphRAG System Capability Registry

**Generated**: 2025-06-19  
**Total Capabilities**: 571 (82 classes + 489 functions)  
**Files Analyzed**: 48 Python files

---

## 🎯 Executive Summary

This system contains **571 distinct capabilities** across **3 main phases** of document processing:
- **Phase 1**: Basic pipeline (PDF → entities → relationships → graph → query)
- **Phase 2**: Enhanced processing with ontology awareness
- **Phase 3**: Multi-document fusion and knowledge synthesis

**29 capabilities are exposed as MCP tools** for external access and fine-grained control.

---

## 📊 Capability Breakdown by Category

### 🔧 Phase 1: Basic Pipeline (166 capabilities)
**Purpose**: Core document processing workflow

#### PDF Loading & Text Processing (20 capabilities)
- **t01_pdf_loader.py** (10): PDF/text extraction, confidence calculation, format support
- **t15a_text_chunker.py** (10): Text chunking, tokenization, overlap handling

#### Entity & Relationship Extraction (49 capabilities)  
- **t23a_spacy_ner.py** (11): spaCy-based named entity recognition
- **t23c_llm_entity_extractor.py** (9): LLM-based entity extraction 
- **t27_relationship_extractor.py** (18): Pattern-based relationship extraction
- **t41_text_embedder.py** (11): Text embedding and similarity

#### Graph Construction (29 capabilities)
- **t31_entity_builder.py** (14): Neo4j entity node creation
- **t34_edge_builder.py** (15): Neo4j relationship edge creation

#### Graph Analysis & Query (42 capabilities)
- **t68_pagerank.py** (13): PageRank calculation and ranking
- **t68_pagerank_optimized.py** (8): Optimized PageRank implementation
- **t49_multihop_query.py** (17): Multi-hop graph querying
- **t49_enhanced_query.py** (12): Enhanced query understanding and answering

#### Workflow Orchestration (16 capabilities)
- **vertical_slice_workflow.py** (8): Main Phase 1 workflow
- **vertical_slice_workflow_optimized.py** (8): Performance-optimized workflow

#### MCP Tool Integration (25 capabilities)
- **phase1_mcp_tools.py** (25): Individual tool exposure for external access

#### Infrastructure (7 capabilities)
- **base_neo4j_tool.py** (4): Neo4j connection management
- **neo4j_fallback_mixin.py** (7): Fallback handling for Neo4j failures

---

### 🧠 Phase 2: Enhanced Processing (69 capabilities)
**Purpose**: Ontology-aware processing with advanced extraction

#### Enhanced Extraction (10 capabilities)
- **t23c_ontology_aware_extractor.py** (10): Gemini-based ontology-aware entity extraction

#### Graph Building (20 capabilities)
- **t31_ontology_graph_builder.py** (20): Ontology-constrained graph construction

#### Visualization (22 capabilities)
- **interactive_graph_visualizer.py** (22): Interactive graph visualization and analysis

#### Workflow Orchestration (17 capabilities)
- **enhanced_vertical_slice_workflow.py** (17): Main Phase 2 workflow with ontology integration

---

### 🔄 Phase 3: Multi-Document Fusion (64 capabilities)
**Purpose**: Cross-document knowledge synthesis and fusion

#### Document Fusion (41 capabilities)
- **t301_multi_document_fusion.py** (33): Core multi-document processing and entity fusion
- **basic_multi_document_workflow.py** (8): Simplified multi-document workflow

#### Fusion Tools (18 capabilities)
- **t301_fusion_tools.py** (13): Similarity calculation, clustering, conflict resolution
- **t301_mcp_tools.py** (5): MCP-exposed fusion tools

---

### 🛠️ Core Infrastructure (149 capabilities)
**Purpose**: Foundational services and system management

#### Identity & Entity Management (29 capabilities)
- **identity_service.py** (13): Basic entity identity and mention tracking
- **enhanced_identity_service.py** (16): Enhanced identity with embeddings and similarity

#### Data Quality & Provenance (30 capabilities)
- **quality_service.py** (18): Confidence assessment and quality tracking
- **provenance_service.py** (12): Operation tracking and lineage

#### System Services (23 capabilities)
- **service_manager.py** (10): Singleton service management
- **workflow_state_service.py** (13): Workflow checkpoints and progress tracking

#### UI Integration (15 capabilities)
- **ui_phase_adapter.py** (15): UI-to-backend integration layer

#### Phase Management (18 capabilities)
- **phase_adapters.py** (18): Standardized phase interfaces
- **graphrag_phase_interface.py** (21): Common phase interface definitions

#### Enhanced Storage (11 capabilities)
- **enhanced_identity_service_faiss.py** (11): FAISS-based similarity search

#### Testing Framework (18 capabilities)
- **integration_test_framework.py** (18): Comprehensive integration testing

---

### 🧠 Knowledge & Ontology (44 capabilities)
**Purpose**: Domain knowledge and ontology management

#### Ontology Generation (32 capabilities)
- **ontology_generator.py** (20): Core ontology generation and validation
- **gemini_ontology_generator.py** (12): Gemini-powered ontology creation

#### Ontology Storage (12 capabilities)
- **ontology_storage_service.py** (12): Persistent ontology management

---

### 🔌 External Integration (29 capabilities)
**Purpose**: External tool and API integration

#### MCP Server (29 capabilities)
- **mcp_server.py** (29): FastMCP server with full service exposure

---

## 🛠️ MCP Tools (29 External-Facing Capabilities)

### Phase 1 MCP Tools (24 tools)
1. `load_pdf` - Load and extract text from PDF
2. `get_pdf_loader_info` - PDF loader information
3. `chunk_text` - Break text into chunks
4. `get_text_chunker_info` - Text chunker information  
5. `extract_entities` - Extract named entities
6. `get_supported_entity_types` - List supported entity types
7. `get_entity_extractor_info` - Entity extractor information
8. `get_spacy_model_info` - spaCy model information
9. `extract_relationships` - Extract relationships between entities
10. `get_supported_relationship_types` - List supported relationship types
11. `get_relationship_extractor_info` - Relationship extractor information
12. `build_entities` - Build entity nodes in Neo4j
13. `get_entity_builder_info` - Entity builder information
14. `build_edges` - Build relationship edges in Neo4j
15. `get_edge_builder_info` - Edge builder information
16. `calculate_pagerank` - Calculate PageRank scores
17. `get_top_entities` - Get highest-ranked entities
18. `get_pagerank_calculator_info` - PageRank calculator information
19. `query_graph` - Execute multi-hop graph queries
20. `get_query_engine_info` - Query engine information
21. `get_graph_statistics` - Get comprehensive graph statistics
22. `get_entity_details` - Get detailed entity information
23. `get_phase1_tool_registry` - Get all Phase 1 tool information
24. `validate_phase1_pipeline` - Validate Phase 1 component functionality

### Phase 3 MCP Tools (5 tools)
25. `calculate_entity_similarity` - Calculate similarity between entities
26. `find_entity_clusters` - Find clusters of similar entities
27. `resolve_entity_conflicts` - Resolve conflicting entity representations
28. `merge_relationship_evidence` - Merge evidence from multiple relationships
29. `calculate_fusion_consistency` - Calculate consistency metrics for fused knowledge

---

## 📋 Quick Reference: Key Capabilities by Use Case

### Document Processing
- **Load Documents**: `PDFLoader.load_pdf()`, `mcp.load_pdf()`
- **Extract Entities**: `SpacyNER.extract_entities()`, `mcp.extract_entities()`
- **Find Relationships**: `RelationshipExtractor.extract_relationships()`
- **Build Graph**: `EntityBuilder.build_entities()`, `EdgeBuilder.build_edges()`

### Knowledge Analysis
- **Rank Entities**: `PageRankCalculator.calculate_pagerank()`
- **Query Knowledge**: `MultiHopQuery.query_graph()`
- **Find Similar**: `EnhancedIdentityService.find_similar_entities()`
- **Visualize**: `InteractiveGraphVisualizer.create_interactive_plot()`

### Multi-Document Processing
- **Fuse Documents**: `MultiDocumentFusion.fuse_documents()`
- **Resolve Conflicts**: `ConflictResolver.resolve()`
- **Cluster Entities**: `EntityClusterFinder.find_clusters()`

### System Management
- **Manage Services**: `ServiceManager` singleton
- **Track Quality**: `QualityService.assess_confidence()`
- **Monitor Provenance**: `ProvenanceService.get_lineage()`
- **Test Integration**: `IntegrationTester.run_full_integration_suite()`

---

## 🎯 Usage Patterns

### CLI Access
```bash
# Phase 1: Basic processing
python graphrag_cli.py document.pdf --phase 1

# Phase 3: Multi-document fusion  
python graphrag_cli.py document.pdf --phase 3
```

### MCP Tool Access
```python
# Via MCP server - individual tool control
mcp.extract_entities(chunk_ref="chunk1", text="Dr. Smith works at MIT.")
mcp.calculate_pagerank(damping_factor=0.85)
mcp.query_graph("Who works at MIT?")
```

### Direct API Access
```python
# Direct class instantiation
from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
workflow = VerticalSliceWorkflow()
result = workflow.execute_workflow("document.pdf", "What are the main entities?")
```

---

## 🔄 System Integration Points

### External Dependencies
- **Neo4j**: Graph database storage (all graph operations)
- **OpenAI API**: Embeddings and enhanced identity
- **Gemini API**: Ontology generation and enhanced extraction
- **spaCy**: Named entity recognition and NLP
- **FAISS**: Vector similarity search
- **FastMCP**: Tool server and external access

### Data Flow
1. **Input**: PDF/text documents
2. **Processing**: Entity/relationship extraction → Graph construction
3. **Analysis**: PageRank → Multi-hop querying → Visualization
4. **Fusion**: Cross-document entity resolution → Knowledge synthesis
5. **Output**: Structured knowledge graph + Query answers

---

**📝 Note**: This registry represents the complete technical capability of the GraphRAG system as of June 2025. For operational status and quality assessment of individual capabilities, see `PROJECT_STATUS.md`.-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
