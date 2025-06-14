# Super-Digimon Tool Specifications

## Overview

Super-Digimon is a GraphRAG system with **106 specialized tools** organized into 7 lifecycle phases. This document provides the authoritative specification for all tools.

## Tool Organization by Phase

### Phase 1: Ingestion (12 tools)
Get data from various sources into the system.

### Phase 2: Processing (18 tools)
Clean, normalize, and extract information from raw data.

### Phase 3: Construction (18 tools)
Build graph structures and create embeddings.

### Phase 4: Retrieval (19 tools)
Core GraphRAG operators for querying graph data.

### Phase 5: Analysis (8 tools)
Advanced graph algorithms and analytics.

### Phase 6: Storage (6 tools)
Manage persistent data stores.

### Phase 7: Interface (25 tools)
Handle user interactions and system monitoring.

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

### T23: SpaCy Entity Recognizer
Extract named entities using SpaCy
- `text`: string - Input text
- `model`: string (default: "en_core_web_sm")

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

### T27: Rule-based Relationship Extractor
Extract relationships using patterns
- `text`: string - Input text
- `entities`: list - Extracted entities
- `patterns`: dict - Relationship patterns

### T28: ML-based Relationship Extractor
Extract relationships using ML models
- `text`: string - Input text
- `entities`: list - Extracted entities
- `model`: string (default: "rebel-base")

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

### T45: FAISS Vector Indexer
Build FAISS vector index
- `embeddings`: array - Vector embeddings
- `index_type`: string (default: "IVF")

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

### T78: FAISS Manager
FAISS index operations
- `operation`: string - add/search/save/load
- `index`: faiss.Index
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
- **FAISS**: Vector search indices
- **Cache**: Computation results (Redis/DiskCache)