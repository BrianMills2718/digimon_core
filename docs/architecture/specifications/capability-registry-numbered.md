**Doc status**: Living – auto-checked by doc-governance CI

# CAPABILITY REGISTRY - 571 NUMBERED CAPABILITIES

**Generated**: 2025-06-19  
**Total Capabilities**: 571 specific testable capabilities  
**Evidence Required**: Each capability must have test file + execution log + evidence entry

---

## 🔍 PHASE 1: BASIC PIPELINE CAPABILITIES (1-166)

### PDF Loading & Text Processing (1-20)
**File**: `src/tools/phase1/t01_pdf_loader.py`

1. `PDFLoader.__init__()` - Initialize with identity, provenance, quality services
2. `PDFLoader.load_pdf()` - Load PDF file and extract text content
3. `PDFLoader.get_supported_formats()` - Return list of supported file formats
4. `PDFLoader.get_tool_info()` - Return tool metadata and capabilities
5. `PDFLoader._extract_text_from_pdf()` - Extract raw text from PDF using PyPDF2
6. `PDFLoader._calculate_confidence()` - Calculate extraction confidence score
7. `PDFLoader._validate_pdf_file()` - Validate PDF file exists and is readable
8. `PDFLoader._handle_extraction_errors()` - Handle PDF extraction failures gracefully
9. `PDFLoader._generate_document_id()` - Generate unique document identifier
10. `PDFLoader._create_provenance_record()` - Create operation provenance record

**File**: `src/tools/phase1/t15a_text_chunker.py`

11. `TextChunker.__init__()` - Initialize with identity, provenance, quality services
12. `TextChunker.chunk_text()` - Split text into chunks with overlap
13. `TextChunker.get_chunking_stats()` - Return chunking statistics and metadata
14. `TextChunker.get_tool_info()` - Return tool metadata and capabilities
15. `TextChunker._calculate_chunk_size()` - Calculate optimal chunk size for text
16. `TextChunker._create_overlapping_chunks()` - Create chunks with specified overlap
17. `TextChunker._validate_chunk_parameters()` - Validate chunking parameters
18. `TextChunker._calculate_chunk_confidence()` - Calculate chunk quality confidence
19. `TextChunker._generate_chunk_ids()` - Generate unique identifiers for chunks
20. `TextChunker._create_chunk_metadata()` - Create metadata for each chunk

### Entity & Relationship Extraction (21-69)
**File**: `src/tools/phase1/t23a_spacy_ner.py`

21. `SpacyNER.__init__()` - Initialize with spaCy model and services
22. `SpacyNER.extract_entities()` - Extract named entities from text chunk
23. `SpacyNER.get_supported_entity_types()` - Return supported entity types list
24. `SpacyNER.get_model_info()` - Return spaCy model information
25. `SpacyNER.get_tool_info()` - Return tool metadata and capabilities
26. `SpacyNER._load_spacy_model()` - Load and initialize spaCy NLP model
27. `SpacyNER._process_entities()` - Process spaCy entities into standard format
28. `SpacyNER._calculate_entity_confidence()` - Calculate entity extraction confidence
29. `SpacyNER._filter_entities_by_type()` - Filter entities by specified types
30. `SpacyNER._merge_overlapping_entities()` - Merge overlapping entity mentions
31. `SpacyNER._validate_entity_spans()` - Validate entity span boundaries

**File**: `src/tools/phase1/t23c_llm_entity_extractor.py`

32. `LLMEntityExtractor.__init__()` - Initialize with LLM client and services
33. `LLMEntityExtractor.extract_entities_and_relationships()` - Extract using LLM
34. `LLMEntityExtractor.extract_from_chunks()` - Process multiple text chunks
35. `LLMEntityExtractor._prepare_llm_prompt()` - Create structured extraction prompt
36. `LLMEntityExtractor._parse_llm_response()` - Parse LLM JSON response
37. `LLMEntityExtractor._validate_extracted_entities()` - Validate entity format
38. `LLMEntityExtractor._handle_llm_errors()` - Handle LLM API failures
39. `LLMEntityExtractor._calculate_extraction_confidence()` - Calculate confidence
40. `LLMEntityExtractor._merge_chunk_results()` - Merge results from multiple chunks

**File**: `src/tools/phase1/t27_relationship_extractor.py`

41. `RelationshipExtractor.__init__()` - Initialize with patterns and services
42. `RelationshipExtractor.extract_relationships()` - Extract relationships from text
43. `RelationshipExtractor.get_supported_relationship_types()` - Return supported types
44. `RelationshipExtractor.get_tool_info()` - Return tool metadata
45. `RelationshipExtractor._load_relationship_patterns()` - Load extraction patterns
46. `RelationshipExtractor._apply_pattern_matching()` - Apply patterns to text
47. `RelationshipExtractor._validate_relationships()` - Validate extracted relationships
48. `RelationshipExtractor._calculate_relationship_confidence()` - Calculate confidence
49. `RelationshipExtractor._filter_relationships_by_type()` - Filter by type
50. `RelationshipExtractor._merge_duplicate_relationships()` - Merge duplicates
51. `RelationshipExtractor._create_relationship_metadata()` - Create metadata
52. `RelationshipExtractor._handle_extraction_errors()` - Handle errors gracefully
53. `RelationshipExtractor._normalize_relationship_format()` - Normalize format
54. `RelationshipExtractor._validate_entity_references()` - Validate entity refs
55. `RelationshipExtractor._calculate_pattern_matches()` - Calculate match scores
56. `RelationshipExtractor._extract_temporal_relationships()` - Extract temporal
57. `RelationshipExtractor._extract_spatial_relationships()` - Extract spatial
58. `RelationshipExtractor._extract_causal_relationships()` - Extract causal

**File**: `src/tools/phase1/t41_text_embedder.py`

59. `TextEmbedder.__init__()` - Initialize with embedding model and services
60. `TextEmbedder.embed_text()` - Generate embeddings for text
61. `TextEmbedder.embed_entities()` - Generate embeddings for entities
62. `TextEmbedder.calculate_similarity()` - Calculate cosine similarity
63. `TextEmbedder.get_embedding_info()` - Return embedding model info
64. `TextEmbedder.get_tool_info()` - Return tool metadata
65. `TextEmbedder._load_embedding_model()` - Load embedding model
66. `TextEmbedder._preprocess_text()` - Preprocess text for embedding
67. `TextEmbedder._normalize_embeddings()` - Normalize embedding vectors
68. `TextEmbedder._cache_embeddings()` - Cache computed embeddings
69. `TextEmbedder._validate_embedding_dimensions()` - Validate dimensions

### Graph Construction (70-98)
**File**: `src/tools/phase1/t31_entity_builder.py`

70. `EntityBuilder.__init__()` - Initialize with Neo4j and services
71. `EntityBuilder.build_entities()` - Create entity nodes in Neo4j
72. `EntityBuilder.get_tool_info()` - Return tool metadata
73. `EntityBuilder._create_entity_node()` - Create single entity node
74. `EntityBuilder._set_entity_properties()` - Set node properties
75. `EntityBuilder._validate_entity_data()` - Validate entity data format
76. `EntityBuilder._handle_duplicate_entities()` - Handle duplicates
77. `EntityBuilder._calculate_entity_scores()` - Calculate importance scores
78. `EntityBuilder._create_entity_indexes()` - Create Neo4j indexes
79. `EntityBuilder._batch_create_entities()` - Batch create for performance
80. `EntityBuilder._update_entity_metadata()` - Update entity metadata
81. `EntityBuilder._validate_neo4j_connection()` - Validate connection
82. `EntityBuilder._handle_neo4j_errors()` - Handle database errors
83. `EntityBuilder._normalize_entity_names()` - Normalize entity names

**File**: `src/tools/phase1/t34_edge_builder.py`

84. `EdgeBuilder.__init__()` - Initialize with Neo4j and services
85. `EdgeBuilder.build_edges()` - Create relationship edges in Neo4j
86. `EdgeBuilder.get_tool_info()` - Return tool metadata
87. `EdgeBuilder._create_relationship_edge()` - Create single relationship
88. `EdgeBuilder._set_relationship_properties()` - Set edge properties
89. `EdgeBuilder._validate_relationship_data()` - Validate relationship data
90. `EdgeBuilder._handle_duplicate_relationships()` - Handle duplicates
91. `EdgeBuilder._calculate_relationship_weights()` - Calculate edge weights
92. `EdgeBuilder._create_relationship_indexes()` - Create indexes
93. `EdgeBuilder._batch_create_relationships()` - Batch create for performance
94. `EdgeBuilder._update_relationship_metadata()` - Update metadata
95. `EdgeBuilder._validate_entity_existence()` - Validate entities exist
96. `EdgeBuilder._handle_neo4j_errors()` - Handle database errors
97. `EdgeBuilder._normalize_relationship_types()` - Normalize types
98. `EdgeBuilder._calculate_relationship_confidence()` - Calculate confidence

### Graph Analysis & Query (99-140)
**File**: `src/tools/phase1/t68_pagerank.py`

99. `PageRankCalculator.__init__()` - Initialize with Neo4j and parameters
100. `PageRankCalculator.calculate_pagerank()` - Compute PageRank scores
101. `PageRankCalculator.get_top_entities()` - Get highest ranked entities
102. `PageRankCalculator.get_tool_info()` - Return tool metadata
103. `PageRankCalculator._build_graph_matrix()` - Build adjacency matrix
104. `PageRankCalculator._initialize_pagerank_vector()` - Initialize PR vector
105. `PageRankCalculator._iterate_pagerank()` - Perform PR iterations
106. `PageRankCalculator._check_convergence()` - Check algorithm convergence
107. `PageRankCalculator._update_neo4j_scores()` - Update scores in Neo4j
108. `PageRankCalculator._validate_graph_structure()` - Validate graph
109. `PageRankCalculator._handle_disconnected_components()` - Handle disconnected
110. `PageRankCalculator._normalize_scores()` - Normalize PageRank scores
111. `PageRankCalculator._calculate_ranking_statistics()` - Calculate statistics

**File**: `src/tools/phase1/t68_pagerank_optimized.py`

112. `OptimizedPageRank.__init__()` - Initialize optimized PageRank
113. `OptimizedPageRank.calculate_pagerank()` - Optimized PageRank computation
114. `OptimizedPageRank.get_performance_metrics()` - Get performance data
115. `OptimizedPageRank._build_sparse_matrix()` - Build sparse matrix
116. `OptimizedPageRank._vectorized_computation()` - Vectorized operations
117. `OptimizedPageRank._parallel_processing()` - Parallel computation
118. `OptimizedPageRank._memory_optimization()` - Optimize memory usage
119. `OptimizedPageRank._benchmark_performance()` - Benchmark execution

**File**: `src/tools/phase1/t49_multihop_query.py`

120. `MultiHopQuery.__init__()` - Initialize query engine
121. `MultiHopQuery.query_graph()` - Execute multi-hop graph query
122. `MultiHopQuery.get_query_engine_info()` - Return engine metadata
123. `MultiHopQuery._parse_query()` - Parse natural language query
124. `MultiHopQuery._plan_query_execution()` - Plan query execution
125. `MultiHopQuery._execute_cypher_query()` - Execute Cypher query
126. `MultiHopQuery._process_query_results()` - Process results
127. `MultiHopQuery._calculate_result_confidence()` - Calculate confidence
128. `MultiHopQuery._handle_query_errors()` - Handle query errors
129. `MultiHopQuery._optimize_query_performance()` - Optimize performance
130. `MultiHopQuery._validate_query_syntax()` - Validate syntax
131. `MultiHopQuery._cache_query_results()` - Cache results
132. `MultiHopQuery._format_query_response()` - Format response
133. `MultiHopQuery._calculate_query_statistics()` - Calculate statistics
134. `MultiHopQuery._handle_timeout()` - Handle query timeout
135. `MultiHopQuery._log_query_execution()` - Log execution details
136. `MultiHopQuery._validate_neo4j_connection()` - Validate connection

**File**: `src/tools/phase1/t49_enhanced_query.py`

137. `EnhancedMultiHopQuery.__init__()` - Initialize enhanced query system
138. `EnhancedMultiHopQuery.answer_question()` - Answer natural language questions
139. `EnhancedMultiHopQuery.understand_query()` - Parse and understand query intent
140. `EnhancedMultiHopQuery.find_entities_semantic()` - Find entities using semantics
141. `EnhancedMultiHopQuery.execute_graph_query()` - Execute graph traversal
142. `EnhancedMultiHopQuery.generate_natural_answer()` - Generate natural language answer
143. `EnhancedMultiHopQuery.close()` - Close connections and cleanup
144. `QueryIntent.validate()` - Validate query intent structure
145. `QueryPlan.execute()` - Execute planned query steps
146. `StructuredAnswer.format()` - Format structured answer response

### Workflow Orchestration (147-162)
**File**: `src/tools/phase1/vertical_slice_workflow.py`

147. `VerticalSliceWorkflow.__init__()` - Initialize Phase 1 workflow
148. `VerticalSliceWorkflow.execute_workflow()` - Execute complete workflow
149. `VerticalSliceWorkflow.get_tool_info()` - Return workflow metadata
150. `VerticalSliceWorkflow.get_workflow_status()` - Get current status
151. `VerticalSliceWorkflow.close()` - Cleanup and close connections
152. `VerticalSliceWorkflow._load_document()` - Load and process document
153. `VerticalSliceWorkflow._extract_entities()` - Extract entities step
154. `VerticalSliceWorkflow._build_graph()` - Build knowledge graph

**File**: `src/tools/phase1/vertical_slice_workflow_optimized.py`

155. `OptimizedWorkflow.__init__()` - Initialize optimized workflow
156. `OptimizedWorkflow.execute_workflow()` - Execute optimized workflow
157. `OptimizedWorkflow.get_performance_metrics()` - Get performance data
158. `OptimizedWorkflow._parallel_processing()` - Parallel execution
159. `OptimizedWorkflow._cache_intermediate_results()` - Cache results
160. `OptimizedWorkflow._optimize_memory_usage()` - Optimize memory
161. `OptimizedWorkflow._benchmark_execution()` - Benchmark performance
162. `OptimizedWorkflow._validate_optimization_gains()` - Validate gains

### MCP Tool Integration (163-166)
**File**: `src/tools/phase1/phase1_mcp_tools.py`

163. `Phase1MCPTools.load_pdf()` - MCP tool: Load PDF document
164. `Phase1MCPTools.extract_entities()` - MCP tool: Extract entities
165. `Phase1MCPTools.build_graph()` - MCP tool: Build knowledge graph
166. `Phase1MCPTools.query_graph()` - MCP tool: Query knowledge graph

---

## 🧠 PHASE 2: ENHANCED PROCESSING CAPABILITIES (167-235)

### Enhanced Extraction (167-176)
**File**: `src/tools/phase2/t23c_ontology_aware_extractor.py`

167. `OntologyAwareExtractor.__init__()` - Initialize with ontology and services
168. `OntologyAwareExtractor.extract_entities()` - Extract with ontology constraints
169. `OntologyAwareExtractor.load_ontology()` - Load domain ontology
170. `OntologyAwareExtractor.validate_against_ontology()` - Validate extractions
171. `OntologyAwareExtractor.get_tool_info()` - Return tool metadata
172. `OntologyAwareExtractor._apply_ontology_constraints()` - Apply constraints
173. `OntologyAwareExtractor._resolve_entity_types()` - Resolve types
174. `OntologyAwareExtractor._calculate_ontology_confidence()` - Calculate confidence
175. `OntologyAwareExtractor._handle_ontology_conflicts()` - Handle conflicts
176. `OntologyAwareExtractor._update_ontology()` - Update ontology

### Graph Building (177-196)
**File**: `src/tools/phase2/t31_ontology_graph_builder.py`

177. `OntologyGraphBuilder.__init__()` - Initialize ontology graph builder
178. `OntologyGraphBuilder.build_ontology_graph()` - Build ontology-constrained graph
179. `OntologyGraphBuilder.validate_graph_structure()` - Validate against ontology
180. `OntologyGraphBuilder.get_tool_info()` - Return tool metadata
181. `OntologyGraphBuilder._create_ontology_nodes()` - Create ontology nodes
182. `OntologyGraphBuilder._create_ontology_relationships()` - Create relationships
183. `OntologyGraphBuilder._validate_ontology_constraints()` - Validate constraints
184. `OntologyGraphBuilder._resolve_ontology_conflicts()` - Resolve conflicts
185. `OntologyGraphBuilder._calculate_ontology_scores()` - Calculate scores
186. `OntologyGraphBuilder._update_ontology_metadata()` - Update metadata
187. `OntologyGraphBuilder._handle_ontology_errors()` - Handle errors
188. `OntologyGraphBuilder._normalize_ontology_data()` - Normalize data
189. `OntologyGraphBuilder._create_ontology_indexes()` - Create indexes
190. `OntologyGraphBuilder._batch_ontology_operations()` - Batch operations
191. `OntologyGraphBuilder._validate_ontology_integrity()` - Validate integrity
192. `OntologyGraphBuilder._calculate_ontology_statistics()` - Calculate stats
193. `OntologyGraphBuilder._handle_ontology_updates()` - Handle updates
194. `OntologyGraphBuilder._optimize_ontology_queries()` - Optimize queries
195. `OntologyGraphBuilder._backup_ontology_state()` - Backup state
196. `OntologyGraphBuilder._restore_ontology_state()` - Restore state

### Visualization (197-218)
**File**: `src/tools/phase2/interactive_graph_visualizer.py`

197. `InteractiveGraphVisualizer.__init__()` - Initialize visualizer
198. `InteractiveGraphVisualizer.create_interactive_plot()` - Create interactive plot
199. `InteractiveGraphVisualizer.update_visualization()` - Update display
200. `InteractiveGraphVisualizer.get_tool_info()` - Return tool metadata
201. `InteractiveGraphVisualizer._fetch_graph_data()` - Fetch data from Neo4j
202. `InteractiveGraphVisualizer._prepare_node_data()` - Prepare node data
203. `InteractiveGraphVisualizer._prepare_edge_data()` - Prepare edge data
204. `InteractiveGraphVisualizer._apply_layout_algorithm()` - Apply layout
205. `InteractiveGraphVisualizer._calculate_node_sizes()` - Calculate sizes
206. `InteractiveGraphVisualizer._assign_node_colors()` - Assign colors
207. `InteractiveGraphVisualizer._create_plotly_figure()` - Create Plotly figure
208. `InteractiveGraphVisualizer._add_interactivity()` - Add interactions
209. `InteractiveGraphVisualizer._handle_node_selection()` - Handle selection
210. `InteractiveGraphVisualizer._handle_zoom_events()` - Handle zoom
211. `InteractiveGraphVisualizer._export_visualization()` - Export to file
212. `InteractiveGraphVisualizer._validate_graph_data()` - Validate data
213. `InteractiveGraphVisualizer._optimize_rendering()` - Optimize rendering
214. `InteractiveGraphVisualizer._handle_large_graphs()` - Handle large graphs
215. `InteractiveGraphVisualizer._calculate_layout_metrics()` - Calculate metrics
216. `InteractiveGraphVisualizer._save_visualization_state()` - Save state
217. `InteractiveGraphVisualizer._load_visualization_state()` - Load state
218. `InteractiveGraphVisualizer._customize_appearance()` - Customize appearance

### Workflow Orchestration (219-235)
**File**: `src/tools/phase2/enhanced_vertical_slice_workflow.py`

219. `EnhancedVerticalSliceWorkflow.__init__()` - Initialize enhanced workflow
220. `EnhancedVerticalSliceWorkflow.execute_workflow()` - Execute enhanced workflow
221. `EnhancedVerticalSliceWorkflow.get_tool_info()` - Return workflow metadata
222. `EnhancedVerticalSliceWorkflow._load_ontology()` - Load domain ontology
223. `EnhancedVerticalSliceWorkflow._extract_entities_with_ontology()` - Extract with ontology
224. `EnhancedVerticalSliceWorkflow._validate_extractions()` - Validate against ontology
225. `EnhancedVerticalSliceWorkflow._build_enhanced_graph()` - Build enhanced graph
226. `EnhancedVerticalSliceWorkflow._apply_reasoning()` - Apply reasoning rules
227. `EnhancedVerticalSliceWorkflow._generate_insights()` - Generate insights
228. `EnhancedVerticalSliceWorkflow._create_visualization()` - Create visualizations
229. `EnhancedVerticalSliceWorkflow._export_results()` - Export enhanced results
230. `EnhancedVerticalSliceWorkflow._validate_workflow_integrity()` - Validate integrity
231. `EnhancedVerticalSliceWorkflow._handle_workflow_errors()` - Handle errors
232. `EnhancedVerticalSliceWorkflow._optimize_workflow_performance()` - Optimize performance
233. `EnhancedVerticalSliceWorkflow._calculate_workflow_metrics()` - Calculate metrics
234. `EnhancedVerticalSliceWorkflow._backup_workflow_state()` - Backup state
235. `EnhancedVerticalSliceWorkflow._restore_workflow_state()` - Restore state

---

## 🔄 PHASE 3: MULTI-DOCUMENT FUSION CAPABILITIES (236-299)

### Document Fusion (236-276)
**File**: `src/tools/phase3/t301_multi_document_fusion.py`

236. `MultiDocumentFusion.__init__()` - Initialize fusion system
237. `MultiDocumentFusion.fuse_documents()` - Fuse multiple documents
238. `MultiDocumentFusion.get_tool_info()` - Return tool metadata
239. `MultiDocumentFusion._load_multiple_documents()` - Load documents
240. `MultiDocumentFusion._extract_entities_from_all()` - Extract from all docs
241. `MultiDocumentFusion._identify_duplicate_entities()` - Find duplicates
242. `MultiDocumentFusion._merge_duplicate_entities()` - Merge duplicates
243. `MultiDocumentFusion._resolve_entity_conflicts()` - Resolve conflicts
244. `MultiDocumentFusion._calculate_fusion_confidence()` - Calculate confidence
245. `MultiDocumentFusion._create_unified_graph()` - Create unified graph
246. `MultiDocumentFusion._validate_fusion_results()` - Validate results
247. `MultiDocumentFusion._generate_fusion_report()` - Generate report
248. `MultiDocumentFusion._handle_fusion_errors()` - Handle errors
249. `MultiDocumentFusion._optimize_fusion_performance()` - Optimize performance
250. `MultiDocumentFusion._calculate_similarity_scores()` - Calculate similarity
251. `MultiDocumentFusion._apply_clustering_algorithms()` - Apply clustering
252. `MultiDocumentFusion._resolve_relationship_conflicts()` - Resolve conflicts
253. `MultiDocumentFusion._merge_relationship_evidence()` - Merge evidence
254. `MultiDocumentFusion._calculate_evidence_weights()` - Calculate weights
255. `MultiDocumentFusion._validate_merged_relationships()` - Validate relationships
256. `MultiDocumentFusion._create_consensus_entities()` - Create consensus
257. `MultiDocumentFusion._handle_contradictory_information()` - Handle contradictions
258. `MultiDocumentFusion._calculate_information_quality()` - Calculate quality
259. `MultiDocumentFusion._generate_provenance_chains()` - Generate provenance
260. `MultiDocumentFusion._create_fusion_metadata()` - Create metadata
261. `MultiDocumentFusion._export_fused_knowledge()` - Export results
262. `MultiDocumentFusion._validate_knowledge_consistency()` - Validate consistency
263. `MultiDocumentFusion._calculate_fusion_statistics()` - Calculate statistics
264. `MultiDocumentFusion._backup_fusion_state()` - Backup state
265. `MultiDocumentFusion._restore_fusion_state()` - Restore state
266. `MultiDocumentFusion._compare_fusion_strategies()` - Compare strategies
267. `MultiDocumentFusion._select_optimal_strategy()` - Select strategy
268. `MultiDocumentFusion._monitor_fusion_progress()` - Monitor progress

**File**: `src/tools/phase3/basic_multi_document_workflow.py`

269. `BasicMultiDocumentWorkflow.__init__()` - Initialize basic workflow
270. `BasicMultiDocumentWorkflow.process_documents()` - Process multiple docs
271. `BasicMultiDocumentWorkflow.get_tool_info()` - Return tool metadata
272. `BasicMultiDocumentWorkflow._validate_input_documents()` - Validate inputs
273. `BasicMultiDocumentWorkflow._execute_parallel_processing()` - Parallel processing
274. `BasicMultiDocumentWorkflow._aggregate_results()` - Aggregate results
275. `BasicMultiDocumentWorkflow._generate_summary_report()` - Generate summary
276. `BasicMultiDocumentWorkflow._handle_processing_errors()` - Handle errors

### Fusion Tools (277-299)
**File**: `src/tools/phase3/t301_fusion_tools.py`

277. `SimilarityCalculator.__init__()` - Initialize similarity calculator
278. `SimilarityCalculator.calculate_entity_similarity()` - Calculate entity similarity
279. `SimilarityCalculator.calculate_relationship_similarity()` - Calculate relationship similarity
280. `SimilarityCalculator._compute_semantic_similarity()` - Compute semantic similarity
281. `SimilarityCalculator._compute_structural_similarity()` - Compute structural similarity
282. `EntityClusterFinder.__init__()` - Initialize cluster finder
283. `EntityClusterFinder.find_clusters()` - Find entity clusters
284. `EntityClusterFinder._apply_clustering_algorithm()` - Apply clustering
285. `EntityClusterFinder._validate_clusters()` - Validate clusters
286. `ConflictResolver.__init__()` - Initialize conflict resolver
287. `ConflictResolver.resolve_conflicts()` - Resolve entity conflicts
288. `ConflictResolver._identify_conflicts()` - Identify conflicts
289. `ConflictResolver._apply_resolution_strategy()` - Apply strategy

**File**: `src/tools/phase3/t301_mcp_tools.py`

290. `Phase3MCPTools.calculate_entity_similarity()` - MCP: Calculate similarity
291. `Phase3MCPTools.find_entity_clusters()` - MCP: Find clusters
292. `Phase3MCPTools.resolve_entity_conflicts()` - MCP: Resolve conflicts
293. `Phase3MCPTools.merge_relationship_evidence()` - MCP: Merge evidence
294. `Phase3MCPTools.calculate_fusion_consistency()` - MCP: Calculate consistency

**File**: `src/tools/phase3/t301_multi_document_fusion_tools.py`

295. `DocumentFusionTools.__init__()` - Initialize fusion tools
296. `DocumentFusionTools.merge_documents()` - Merge documents
297. `DocumentFusionTools.calculate_consensus()` - Calculate consensus
298. `DocumentFusionTools.validate_fusion()` - Validate fusion results
299. `DocumentFusionTools.export_results()` - Export fusion results

---

## 🛠️ CORE INFRASTRUCTURE CAPABILITIES (300-448)

### Identity & Entity Management (300-328)
**File**: `src/core/identity_service.py`

300. `IdentityService.__init__()` - Initialize identity service
301. `IdentityService.create_entity_id()` - Create unique entity identifier
302. `IdentityService.find_similar_entities()` - Find similar entities
303. `IdentityService.merge_entities()` - Merge duplicate entities
304. `IdentityService.get_entity_mentions()` - Get entity mentions
305. `IdentityService.add_entity_mention()` - Add entity mention
306. `IdentityService.update_entity()` - Update entity information
307. `IdentityService.delete_entity()` - Delete entity
308. `IdentityService.get_entity_statistics()` - Get entity statistics
309. `IdentityService._calculate_similarity_score()` - Calculate similarity
310. `IdentityService._validate_entity_data()` - Validate entity data
311. `IdentityService._handle_duplicate_detection()` - Handle duplicates
312. `IdentityService._normalize_entity_names()` - Normalize names

**File**: `src/core/enhanced_identity_service.py`

313. `EnhancedIdentityService.__init__()` - Initialize enhanced service
314. `EnhancedIdentityService.find_similar_entities()` - Find with embeddings
315. `EnhancedIdentityService.calculate_semantic_similarity()` - Semantic similarity
316. `EnhancedIdentityService.create_entity_embeddings()` - Create embeddings
317. `EnhancedIdentityService.update_similarity_index()` - Update index
318. `EnhancedIdentityService.get_embedding_statistics()` - Get stats
319. `EnhancedIdentityService._load_embedding_model()` - Load model
320. `EnhancedIdentityService._compute_embeddings()` - Compute embeddings
321. `EnhancedIdentityService._build_similarity_index()` - Build index
322. `EnhancedIdentityService._query_similarity_index()` - Query index
323. `EnhancedIdentityService._validate_embeddings()` - Validate embeddings
324. `EnhancedIdentityService._handle_embedding_errors()` - Handle errors
325. `EnhancedIdentityService._optimize_embedding_storage()` - Optimize storage
326. `EnhancedIdentityService._backup_embeddings()` - Backup embeddings
327. `EnhancedIdentityService._restore_embeddings()` - Restore embeddings
328. `EnhancedIdentityService._calculate_embedding_metrics()` - Calculate metrics

### Data Quality & Provenance (329-358)
**File**: `src/core/quality_service.py`

329. `QualityService.__init__()` - Initialize quality service
330. `QualityService.assess_confidence()` - Assess extraction confidence
331. `QualityService.calculate_quality_score()` - Calculate quality score
332. `QualityService.validate_data_integrity()` - Validate data integrity
333. `QualityService.get_quality_metrics()` - Get quality metrics
334. `QualityService.update_quality_scores()` - Update scores
335. `QualityService.identify_quality_issues()` - Identify issues
336. `QualityService.suggest_improvements()` - Suggest improvements
337. `QualityService.track_quality_trends()` - Track trends
338. `QualityService._calculate_extraction_confidence()` - Calculate confidence
339. `QualityService._validate_entity_quality()` - Validate entity quality
340. `QualityService._validate_relationship_quality()` - Validate relationship quality
341. `QualityService._calculate_graph_quality()` - Calculate graph quality
342. `QualityService._identify_outliers()` - Identify outliers
343. `QualityService._generate_quality_report()` - Generate report
344. `QualityService._handle_quality_alerts()` - Handle alerts
345. `QualityService._optimize_quality_checks()` - Optimize checks
346. `QualityService._backup_quality_data()` - Backup data

**File**: `src/core/provenance_service.py`

347. `ProvenanceService.__init__()` - Initialize provenance service
348. `ProvenanceService.record_operation()` - Record operation
349. `ProvenanceService.get_lineage()` - Get data lineage
350. `ProvenanceService.trace_entity_origin()` - Trace entity origin
351. `ProvenanceService.get_operation_history()` - Get operation history
352. `ProvenanceService.validate_provenance()` - Validate provenance
353. `ProvenanceService._create_provenance_record()` - Create record
354. `ProvenanceService._link_operations()` - Link operations
355. `ProvenanceService._calculate_lineage_depth()` - Calculate depth
356. `ProvenanceService._generate_provenance_graph()` - Generate graph
357. `ProvenanceService._export_provenance_data()` - Export data
358. `ProvenanceService._validate_provenance_integrity()` - Validate integrity

### System Services (359-381)
**File**: `src/core/service_manager.py`

359. `ServiceManager.__init__()` - Initialize service manager
360. `ServiceManager.get_instance()` - Get singleton instance
361. `ServiceManager.initialize_services()` - Initialize all services
362. `ServiceManager.get_service()` - Get specific service
363. `ServiceManager.shutdown_services()` - Shutdown all services
364. `ServiceManager.restart_service()` - Restart specific service
365. `ServiceManager.get_service_status()` - Get service status
366. `ServiceManager.validate_services()` - Validate services
367. `ServiceManager._create_service_registry()` - Create registry
368. `ServiceManager._handle_service_errors()` - Handle errors

**File**: `src/core/workflow_state_service.py`

369. `WorkflowStateService.__init__()` - Initialize state service
370. `WorkflowStateService.save_checkpoint()` - Save workflow checkpoint
371. `WorkflowStateService.load_checkpoint()` - Load checkpoint
372. `WorkflowStateService.get_workflow_status()` - Get status
373. `WorkflowStateService.update_progress()` - Update progress
374. `WorkflowStateService.cancel_workflow()` - Cancel workflow
375. `WorkflowStateService.resume_workflow()` - Resume workflow
376. `WorkflowStateService.get_workflow_history()` - Get history
377. `WorkflowStateService._create_checkpoint()` - Create checkpoint
378. `WorkflowStateService._validate_checkpoint()` - Validate checkpoint
379. `WorkflowStateService._cleanup_old_checkpoints()` - Cleanup checkpoints
380. `WorkflowStateService._monitor_workflow_progress()` - Monitor progress
381. `WorkflowStateService._handle_workflow_failures()` - Handle failures

### Phase Management (382-417)
**File**: `src/core/phase_adapters.py`

382. `Phase1Adapter.__init__()` - Initialize Phase 1 adapter
383. `Phase1Adapter.execute()` - Execute Phase 1 processing
384. `Phase1Adapter.validate_input()` - Validate Phase 1 input
385. `Phase1Adapter.format_output()` - Format Phase 1 output
386. `Phase2Adapter.__init__()` - Initialize Phase 2 adapter
387. `Phase2Adapter.execute()` - Execute Phase 2 processing
388. `Phase2Adapter.validate_input()` - Validate Phase 2 input
389. `Phase2Adapter.format_output()` - Format Phase 2 output
390. `Phase3Adapter.__init__()` - Initialize Phase 3 adapter
391. `Phase3Adapter.execute()` - Execute Phase 3 processing
392. `Phase3Adapter.validate_input()` - Validate Phase 3 input
393. `Phase3Adapter.format_output()` - Format Phase 3 output
394. `PhaseAdapter._validate_services()` - Validate required services
395. `PhaseAdapter._handle_phase_errors()` - Handle phase errors
396. `PhaseAdapter._calculate_phase_metrics()` - Calculate metrics
397. `PhaseAdapter._log_phase_execution()` - Log execution
398. `PhaseAdapter._optimize_phase_performance()` - Optimize performance

**File**: `src/core/graphrag_phase_interface.py`

399. `GraphRAGPhaseInterface.execute()` - Execute phase interface
400. `GraphRAGPhaseInterface.validate()` - Validate phase interface
401. `GraphRAGPhaseInterface.get_metadata()` - Get phase metadata
402. `GraphRAGPhaseInterface.get_requirements()` - Get requirements
403. `GraphRAGPhaseInterface.get_outputs()` - Get outputs
404. `GraphRAGPhaseInterface._standardize_input()` - Standardize input
405. `GraphRAGPhaseInterface._standardize_output()` - Standardize output
406. `GraphRAGPhaseInterface._validate_phase_contract()` - Validate contract
407. `GraphRAGPhaseInterface._handle_interface_errors()` - Handle errors
408. `GraphRAGPhaseInterface._log_interface_usage()` - Log usage
409. `GraphRAGPhaseInterface._calculate_interface_metrics()` - Calculate metrics
410. `GraphRAGPhaseInterface._optimize_interface_performance()` - Optimize performance
411. `GraphRAGPhaseInterface._backup_interface_state()` - Backup state
412. `GraphRAGPhaseInterface._restore_interface_state()` - Restore state
413. `GraphRAGPhaseInterface._validate_interface_integrity()` - Validate integrity
414. `GraphRAGPhaseInterface._monitor_interface_health()` - Monitor health
415. `GraphRAGPhaseInterface._handle_interface_failures()` - Handle failures
416. `GraphRAGPhaseInterface._generate_interface_report()` - Generate report
417. `GraphRAGPhaseInterface._export_interface_data()` - Export data

### Enhanced Storage (418-433)
**File**: `src/core/enhanced_identity_service_faiss.py`

418. `FAISSIdentityService.__init__()` - Initialize FAISS service
419. `FAISSIdentityService.build_faiss_index()` - Build FAISS index
420. `FAISSIdentityService.search_similar_entities()` - Search similar
421. `FAISSIdentityService.add_entity_to_index()` - Add to index
422. `FAISSIdentityService.remove_entity_from_index()` - Remove from index
423. `FAISSIdentityService.update_entity_in_index()` - Update in index
424. `FAISSIdentityService.get_index_statistics()` - Get statistics
425. `FAISSIdentityService._create_faiss_index()` - Create index
426. `FAISSIdentityService._train_faiss_index()` - Train index
427. `FAISSIdentityService._optimize_faiss_search()` - Optimize search
428. `FAISSIdentityService._validate_faiss_index()` - Validate index
429. `FAISSIdentityService._backup_faiss_index()` - Backup index
430. `FAISSIdentityService._restore_faiss_index()` - Restore index
431. `FAISSIdentityService._monitor_faiss_performance()` - Monitor performance
432. `FAISSIdentityService._handle_faiss_errors()` - Handle errors
433. `FAISSIdentityService._calculate_faiss_metrics()` - Calculate metrics

### Testing Framework (434-448)
**File**: `src/testing/integration_test_framework.py`

434. `IntegrationTester.__init__()` - Initialize integration tester
435. `IntegrationTester.run_full_integration_suite()` - Run full suite
436. `IntegrationTester.test_phase1_integration()` - Test Phase 1
437. `IntegrationTester.test_phase2_integration()` - Test Phase 2
438. `IntegrationTester.test_phase3_integration()` - Test Phase 3
439. `IntegrationTester.test_cross_phase_integration()` - Test cross-phase
440. `IntegrationTester.validate_system_health()` - Validate health
441. `IntegrationTester.generate_test_report()` - Generate report
442. `IntegrationTester._setup_test_environment()` - Setup environment
443. `IntegrationTester._cleanup_test_environment()` - Cleanup environment
444. `IntegrationTester._validate_test_results()` - Validate results
445. `IntegrationTester._handle_test_failures()` - Handle failures
446. `IntegrationTester._calculate_test_metrics()` - Calculate metrics
447. `IntegrationTester._optimize_test_performance()` - Optimize performance
448. `IntegrationTester._backup_test_data()` - Backup test data

---

## 🧠 KNOWLEDGE & ONTOLOGY CAPABILITIES (449-492)

### Ontology Generation (449-480)
**File**: `src/knowledge/ontology_generator.py`

449. `OntologyGenerator.__init__()` - Initialize ontology generator
450. `OntologyGenerator.generate_ontology()` - Generate domain ontology
451. `OntologyGenerator.validate_ontology()` - Validate ontology structure
452. `OntologyGenerator.export_ontology()` - Export ontology to file
453. `OntologyGenerator.import_ontology()` - Import ontology from file
454. `OntologyGenerator.merge_ontologies()` - Merge multiple ontologies
455. `OntologyGenerator.update_ontology()` - Update existing ontology
456. `OntologyGenerator.get_ontology_statistics()` - Get statistics
457. `OntologyGenerator._extract_concepts()` - Extract concepts
458. `OntologyGenerator._identify_relationships()` - Identify relationships
459. `OntologyGenerator._create_hierarchy()` - Create concept hierarchy
460. `OntologyGenerator._validate_consistency()` - Validate consistency
461. `OntologyGenerator._resolve_conflicts()` - Resolve conflicts
462. `OntologyGenerator._optimize_structure()` - Optimize structure
463. `OntologyGenerator._calculate_metrics()` - Calculate metrics
464. `OntologyGenerator._handle_generation_errors()` - Handle errors
465. `OntologyGenerator._backup_ontology()` - Backup ontology
466. `OntologyGenerator._restore_ontology()` - Restore ontology
467. `OntologyGenerator._monitor_generation_progress()` - Monitor progress
468. `OntologyGenerator._validate_generation_quality()` - Validate quality

**File**: `src/knowledge/gemini_ontology_generator.py`

469. `GeminiOntologyGenerator.__init__()` - Initialize Gemini generator
470. `GeminiOntologyGenerator.generate_with_gemini()` - Generate using Gemini
471. `GeminiOntologyGenerator.enhance_ontology()` - Enhance with Gemini
472. `GeminiOntologyGenerator.validate_with_gemini()` - Validate with Gemini
473. `GeminiOntologyGenerator._prepare_gemini_prompt()` - Prepare prompt
474. `GeminiOntologyGenerator._parse_gemini_response()` - Parse response
475. `GeminiOntologyGenerator._handle_gemini_errors()` - Handle errors
476. `GeminiOntologyGenerator._optimize_gemini_usage()` - Optimize usage
477. `GeminiOntologyGenerator._validate_gemini_output()` - Validate output
478. `GeminiOntologyGenerator._calculate_generation_cost()` - Calculate cost
479. `GeminiOntologyGenerator._monitor_gemini_performance()` - Monitor performance
480. `GeminiOntologyGenerator._backup_gemini_results()` - Backup results

### Ontology Storage (481-492)
**File**: `src/core/ontology_storage_service.py`

481. `OntologyStorageService.__init__()` - Initialize storage service
482. `OntologyStorageService.store_ontology()` - Store ontology
483. `OntologyStorageService.retrieve_ontology()` - Retrieve ontology
484. `OntologyStorageService.update_ontology()` - Update stored ontology
485. `OntologyStorageService.delete_ontology()` - Delete ontology
486. `OntologyStorageService.list_ontologies()` - List stored ontologies
487. `OntologyStorageService.get_ontology_metadata()` - Get metadata
488. `OntologyStorageService._validate_storage_format()` - Validate format
489. `OntologyStorageService._optimize_storage()` - Optimize storage
490. `OntologyStorageService._backup_ontology_storage()` - Backup storage
491. `OntologyStorageService._restore_ontology_storage()` - Restore storage
492. `OntologyStorageService._monitor_storage_health()` - Monitor health

---

## 🔌 EXTERNAL INTEGRATION CAPABILITIES (493-521)

### MCP Server (493-521)
**File**: `src/tools/mcp_server.py`

493. `MCPServer.__init__()` - Initialize MCP server
494. `MCPServer.start_server()` - Start FastMCP server
495. `MCPServer.stop_server()` - Stop MCP server
496. `MCPServer.register_tools()` - Register all MCP tools
497. `MCPServer.handle_tool_request()` - Handle tool requests
498. `MCPServer.validate_request()` - Validate incoming requests
499. `MCPServer.format_response()` - Format tool responses
500. `MCPServer.get_server_status()` - Get server status
501. `MCPServer.get_tool_registry()` - Get tool registry
502. `MCPServer.handle_server_errors()` - Handle server errors
503. `MCPServer._setup_fastmcp()` - Setup FastMCP
504. `MCPServer._configure_endpoints()` - Configure endpoints
505. `MCPServer._validate_tool_definitions()` - Validate tools
506. `MCPServer._handle_authentication()` - Handle auth
507. `MCPServer._log_requests()` - Log requests
508. `MCPServer._monitor_performance()` - Monitor performance
509. `MCPServer._handle_rate_limiting()` - Handle rate limits
510. `MCPServer._backup_server_state()` - Backup state
511. `MCPServer._restore_server_state()` - Restore state
512. `MCPServer._optimize_server_performance()` - Optimize performance
513. `MCPServer._validate_server_health()` - Validate health
514. `MCPServer._generate_server_report()` - Generate report
515. `MCPServer._handle_server_shutdown()` - Handle shutdown
516. `MCPServer._cleanup_server_resources()` - Cleanup resources
517. `MCPServer._export_server_metrics()` - Export metrics
518. `MCPServer._import_server_configuration()` - Import config
519. `MCPServer._validate_server_configuration()` - Validate config
520. `MCPServer._update_server_configuration()` - Update config
521. `MCPServer._monitor_tool_usage()` - Monitor tool usage

---

## 🎯 INFRASTRUCTURE & BASE CAPABILITIES (522-571)

### Neo4j Integration (522-531)
**File**: `src/tools/phase1/base_neo4j_tool.py`

522. `BaseNeo4jTool.__init__()` - Initialize Neo4j base tool
523. `BaseNeo4jTool.get_driver()` - Get Neo4j driver connection
524. `BaseNeo4jTool.execute_query()` - Execute Cypher query
525. `BaseNeo4jTool.close_connection()` - Close Neo4j connection
526. `BaseNeo4jTool._validate_connection()` - Validate connection
527. `BaseNeo4jTool._handle_neo4j_errors()` - Handle database errors
528. `BaseNeo4jTool._optimize_query_performance()` - Optimize queries
529. `BaseNeo4jTool._monitor_connection_health()` - Monitor health
530. `BaseNeo4jTool._backup_connection_state()` - Backup state
531. `BaseNeo4jTool._restore_connection_state()` - Restore state

### Fallback Handling (532-538)
**File**: `src/tools/phase1/neo4j_fallback_mixin.py`

532. `Neo4jFallbackMixin.handle_neo4j_failure()` - Handle Neo4j failures
533. `Neo4jFallbackMixin.switch_to_fallback()` - Switch to fallback mode
534. `Neo4jFallbackMixin.validate_fallback_mode()` - Validate fallback
535. `Neo4jFallbackMixin.restore_neo4j_connection()` - Restore connection
536. `Neo4jFallbackMixin._detect_neo4j_failure()` - Detect failures
537. `Neo4jFallbackMixin._log_fallback_events()` - Log events
538. `Neo4jFallbackMixin._monitor_recovery_attempts()` - Monitor recovery

### UI Integration (539-553)
**File**: `src/ui/ui_phase_adapter.py`

539. `UIPhaseAdapter.__init__()` - Initialize UI adapter
540. `UIPhaseAdapter.render_phase_selector()` - Render phase selector
541. `UIPhaseAdapter.handle_file_upload()` - Handle file uploads
542. `UIPhaseAdapter.execute_selected_phase()` - Execute phase
543. `UIPhaseAdapter.display_results()` - Display results
544. `UIPhaseAdapter.handle_user_input()` - Handle user input
545. `UIPhaseAdapter.validate_ui_state()` - Validate UI state
546. `UIPhaseAdapter.update_progress_display()` - Update progress
547. `UIPhaseAdapter._format_results_for_display()` - Format results
548. `UIPhaseAdapter._handle_ui_errors()` - Handle UI errors
549. `UIPhaseAdapter._optimize_ui_performance()` - Optimize performance
550. `UIPhaseAdapter._validate_user_permissions()` - Validate permissions
551. `UIPhaseAdapter._log_ui_interactions()` - Log interactions
552. `UIPhaseAdapter._backup_ui_state()` - Backup state
553. `UIPhaseAdapter._restore_ui_state()` - Restore state

### Performance & Monitoring (554-571)
**File**: `src/core/performance_monitor.py`

554. `PerformanceMonitor.__init__()` - Initialize performance monitor
555. `PerformanceMonitor.start_monitoring()` - Start monitoring
556. `PerformanceMonitor.stop_monitoring()` - Stop monitoring
557. `PerformanceMonitor.get_performance_metrics()` - Get metrics
558. `PerformanceMonitor.generate_performance_report()` - Generate report
559. `PerformanceMonitor.identify_bottlenecks()` - Identify bottlenecks
560. `PerformanceMonitor.suggest_optimizations()` - Suggest optimizations
561. `PerformanceMonitor.track_resource_usage()` - Track resources
562. `PerformanceMonitor.monitor_system_health()` - Monitor health
563. `PerformanceMonitor._collect_timing_data()` - Collect timing
564. `PerformanceMonitor._collect_memory_data()` - Collect memory
565. `PerformanceMonitor._collect_cpu_data()` - Collect CPU
566. `PerformanceMonitor._analyze_performance_trends()` - Analyze trends
567. `PerformanceMonitor._calculate_efficiency_scores()` - Calculate scores
568. `PerformanceMonitor._export_performance_data()` - Export data
569. `PerformanceMonitor._backup_monitoring_data()` - Backup data
570. `PerformanceMonitor._restore_monitoring_data()` - Restore data
571. `PerformanceMonitor._validate_monitoring_integrity()` - Validate integrity

---

**TOTAL**: 571 numbered, specific, testable capabilities

**NEXT STEP**: Create 571 individual test files (`test_capability_001.py` through `test_capability_571.py`) to test each capability individually with documented evidence.-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
