# Super-Digimon Tool Specifications

## Overview

Super-Digimon is a GraphRAG system with **121 specialized tools** organized into 7 lifecycle phases plus critical infrastructure services. This document provides the authoritative specification for all tools.

**Update**: Added 14 new tools (T107-T120) based on mock workflow analysis, including identity services, format converters, and advanced capabilities.

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

### Phase 8: Core Services (14 tools)
Infrastructure services supporting all phases.

## Tool Variants

Many tools offer multiple implementation variants to balance quality, speed, and cost:

### Entity/Relationship Extraction Variants
- **T23a**: Traditional NER (spaCy/transformers) - Fast, cheap, good for standard entities
- **T23b**: LLM Entity/Relationship Extractor - Better quality, handles custom types and relationships

### Chunking Variants  
- **T15a**: Sliding Window Chunker - Simple, fast, predictable
- **T15b**: Semantic Chunker - Uses embeddings to find natural boundaries
- **T15c**: LLM-based Chunker - Understands topics and structure

### Coreference Variants
- **T25a**: Rule-based Coreference - Fast, deterministic
- **T25b**: Neural Coreference - Better accuracy, handles complex cases
- **T25c**: LLM-based Coreference - Best quality, understands context

### Disambiguation Variants
- **T29a**: Embedding-based Disambiguation - Fast, works offline
- **T29b**: Knowledge Base Disambiguation - Links to existing KB
- **T29c**: LLM-based Disambiguation - Reasons about context

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

### T23: Entity Recognizer
Extract named entities (see variants T23a/T23b above)
- `text`: string OR `chunk_refs`: list - Input text or chunk references
- `model`: string (default: "en_core_web_sm") - For T23a
- `entity_types`: list - Types to extract
- `create_mentions`: boolean (default: true) - Create mention objects
- `confidence_threshold`: float (default: 0.7)

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

### T27: Relationship Extractor
Extract relationships between entities (often combined with T23b)
- `text`: string OR `chunk_refs`: list - Input text or chunks
- `entity_refs`: list - Previously extracted entities
- `patterns`: dict - Relationship patterns (for rule-based)
- `model`: string - Model name (for ML-based)
- `extract_with_entities`: boolean - Extract entities and relationships together

### T28: Entity Confidence Scorer
Assess and assign confidence scores to extracted entities
- `entity_refs`: list - References to entities to score
- `context_refs`: list - Context chunks for scoring
- `scoring_method`: string - "frequency", "coherence", "external_kb"
- `boost_factors`: dict - Factors to boost confidence
- `penalty_factors`: dict - Factors to reduce confidence

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

### Key Architectural Patterns

#### Three-Level Identity System
All text processing follows: Surface Form → Mention → Entity
- **Surface**: Text as it appears ("Apple", "AAPL")
- **Mention**: Specific occurrence with context
- **Entity**: Resolved canonical entity

#### Reference-Based Architecture
Tools pass references, not full data objects:
```python
{"entity_refs": ["ent_001", ...], "count": 1000, "sample": [...]}
```

#### Universal Quality Tracking
Every data object includes:
- `confidence`: float (0.0-1.0)
- `quality_tier`: "high" | "medium" | "low"
- `warnings`: list of issues
- `evidence`: supporting data

#### Format Agnostic Processing
Same data can be Graph, Table, or Vector based on analysis needs:
- Use T115 for Graph → Table conversion
- Use T116 for Table → Graph conversion
- Use T117 for automatic format selection

---

## Phase 8: Core Services and Infrastructure (T107-T121)

Critical services identified through mock workflow analysis that support all other tools.

### T107: Identity Service
Manage three-level identity system (Surface → Mention → Entity)
- `operation`: string - "create_mention", "resolve_mention", "create_entity", "merge_entities"
- `surface_text`: string - Text as it appears
- `context`: dict - Document ID, position, surrounding text
- `entity_candidates`: list - Possible entity resolutions with confidence

### T108: Version Service
Handle four-level versioning (schema, data, graph, analysis)
- `operation`: string - "create_version", "get_version", "diff_versions", "rollback"
- `object_type`: string - "schema", "data", "graph", "analysis"
- `object_id`: string - ID of object to version
- `metadata`: dict - Version metadata

### T109: Entity Normalizer
Normalize entity variations to canonical forms
- `entity_name`: string - Name to normalize
- `entity_type`: string - Type for context
- `normalization_rules`: dict - Custom rules (optional)
- `case_sensitive`: boolean (default: false)

### T110: Provenance Service
Track complete operation lineage
- `operation`: string - "record", "trace_lineage", "find_affected"
- `tool_id`: string - Tool that performed operation
- `inputs`: list - Input references
- `outputs`: list - Output references
- `parameters`: dict - Operation parameters

### T111: Quality Service
Assess and propagate confidence scores
- `operation`: string - "assess", "propagate", "aggregate"
- `object`: dict - Object to assess
- `upstream_scores`: list - Previous confidence scores
- `method`: string - Assessment method

### T112: Constraint Engine
Manage and check data constraints
- `operation`: string - "register", "check", "find_violations"
- `constraints`: dict - Constraint definitions
- `data`: dict - Data to validate
- `mode`: string - "strict" or "soft" matching

### T113: Ontology Manager
Define and enforce graph ontologies
- `operation`: string - "create", "update", "validate", "query"
- `ontology`: dict - Ontology definition
- `mode`: string - "strict", "extensible", "ad_hoc"
- `domain_range`: dict - Property constraints

### T114: Provenance Tracker
Enhanced provenance with impact analysis
- `entity_id`: string - Entity to track
- `include_derivatives`: boolean - Track downstream impacts
- `time_range`: tuple - Historical range
- `confidence_threshold`: float - Minimum confidence

### T115: Graph to Table Converter
Convert graph data to tabular format for statistical analysis
- `entity_refs`: list - Entities to include
- `relationship_refs`: list - Relationships to include
- `output_format`: string - "wide", "long", "edge_list"
- `aggregations`: dict - How to aggregate relationships

### T116: Table to Graph Builder
Build graph from tabular data
- `table_ref`: string - Reference to table
- `source_column`: string - Column for source nodes
- `target_column`: string - Column for target nodes
- `relationship_type`: string - Type of relationship to create
- `attribute_columns`: list - Additional columns as properties

### T117: Format Auto-Selector
Intelligently select optimal data format for analysis
- `analysis_type`: string - Type of analysis planned
- `data_characteristics`: dict - Data properties
- `constraints`: dict - Memory, time constraints
- `return_rationale`: boolean - Explain format choice

### T118: Temporal Reasoner
Handle temporal logic and paradoxes
- `temporal_data`: dict - Time-stamped facts
- `query`: string - Temporal query
- `resolve_paradoxes`: boolean - Attempt resolution
- `timeline_mode`: string - "single", "multi", "branching"

### T119: Semantic Evolution Tracker
Track meaning changes over time
- `concept`: string - Concept to track
- `time_range`: tuple - Period to analyze
- `sources`: list - Document sources
- `include_context`: boolean - Include usage context

### T120: Uncertainty Propagation Service
Propagate uncertainty through analysis chains
- `confidence_scores`: list - Input confidences
- `operations`: list - Operations performed
- `method`: string - "monte_carlo", "gaussian", "min_max"
- `return_distribution`: boolean - Full distribution vs point estimate

### T121: Workflow State Service
Manage workflow state for crash recovery and reproducibility
- `operation`: string - "checkpoint", "restore", "list_checkpoints", "clean_old"
- `workflow_id`: string - Unique workflow identifier
- `state_data`: dict - Lightweight references to current state (for checkpoint)
- `checkpoint_id`: string - Specific checkpoint (for restore)
- `include_intermediates`: boolean (default: false) - Include intermediate results
- `compression`: string (default: "gzip") - Compression method for state data

---

## Tool Contracts

Every tool declares a contract specifying its requirements and guarantees. This enables intelligent tool selection and workflow planning.

### Contract Structure

Each tool contract includes:

```python
{
    "tool_id": "T23b",
    "name": "LLM Entity/Relationship Extractor",
    
    # What the tool needs to function
    "required_attributes": {
        "chunk": ["content", "document_ref", "position"],
        "document": ["language"]  # Optional: specific attributes needed
    },
    
    # State requirements (what must be true before running)
    "required_state": {
        "chunks_created": true,
        "language_detected": true,
        "entities_resolved": false  # Can work with unresolved entities
    },
    
    # What the tool produces
    "produced_attributes": {
        "mention": ["surface_text", "position", "entity_candidates"],
        "relationship": ["source_id", "target_id", "type", "confidence"]
    },
    
    # State changes after running
    "state_changes": {
        "entities_extracted": true,
        "relationships_extracted": true
    },
    
    # Error handling
    "error_codes": {
        "E001": "Missing required chunk content",
        "E002": "Language not supported",
        "E003": "LLM API failure",
        "E004": "Confidence below threshold"
    },
    
    # Performance characteristics
    "performance": {
        "time_complexity": "O(n)",  # n = text length
        "memory_usage": "streaming",
        "can_parallelize": true,
        "supports_partial": true
    }
}
```

### Example Tool Contracts

#### T31: Entity Node Builder
```python
{
    "tool_id": "T31",
    "required_attributes": {
        "mention": ["surface_text", "entity_candidates", "confidence"]
    },
    "required_state": {
        "mentions_created": true,
        "entities_resolved": "optional"  # Can work with or without resolution
    },
    "produced_attributes": {
        "entity": ["canonical_name", "entity_type", "mention_refs", "confidence"]
    },
    "state_changes": {
        "entities_created": true
    }
}
```

#### T115: Graph to Table Converter
```python
{
    "tool_id": "T115",
    "required_attributes": {
        "entity": ["id", "attributes"],
        "relationship": ["source_id", "target_id", "type"]
    },
    "required_state": {
        "graph_built": true
    },
    "produced_attributes": {
        "table": ["schema", "row_refs", "source_graph_ref"]
    },
    "supports_modes": ["wide", "long", "edge_list"]
}
```

### Contract Usage

Tool contracts enable:
1. **Pre-flight validation**: Check if tool can run before attempting
2. **Intelligent planning**: Select appropriate tools based on current state
3. **Error recovery**: Understand what went wrong and find alternatives
4. **Workflow optimization**: Parallelize compatible tools
5. **Domain adaptation**: Tools declare if they need entity resolution