# Database Integration and Compatibility Planning

This document provides comprehensive planning for integrating the three database systems (Neo4j, SQLite, FAISS) and ensuring seamless data flow across all 121 tools.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Layer (121 Tools)              │
│  T01-T12   T13-T30   T31-T48   T49-T67   T68-T75   T76-T81 │
│ (Ingest)  (Process) (Construct)(Retrieve)(Analyze)(Storage) │
│                    T82-T106   T107-T121                     │
│                   (Interface) (Core Services)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
              ┌───────┴───────┐
              │  Data Router  │ ← Reference Resolution Layer
              │ (T121 State)  │
              └───────┬───────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│   Neo4j  │    │  SQLite  │    │  FAISS   │
│ (Graphs) │    │(Metadata)│    │(Vectors) │
│          │    │          │    │          │
│ Entities │    │Documents │    │Embeddings│
│Relations │    │Chunks    │    │Indices   │
│Community │    │Workflow  │    │Search    │
│  State   │    │ State    │    │ Results  │
└──────────┘    └──────────┘    └──────────┘
```

## Data Storage Distribution

### Neo4j: Graph Structure Storage
**Primary Purpose**: Store structured graph data with complex relationships

**Stored Objects**:
- **Entities**: Canonical entities with resolved identities
- **Relationships**: Typed edges between entities
- **Communities**: Detected graph communities and hierarchies
- **Subgraphs**: Named graph subsets for analysis
- **Graph Metadata**: Schema, constraints, indices

**Schema Design**:
```cypher
// Core Node Types
(:Entity {id: string, canonical_name: string, entity_type: string, 
          confidence: float, quality_tier: string, created_by: string,
          surface_forms: [string], mention_refs: [string]})

(:Chunk {id: string, content: string, document_ref: string, 
         position: int, confidence: float, created_by: string})

(:Document {id: string, file_path: string, title: string,
           confidence: float, file_type: string, created_by: string})

// Relationship Types
(:Entity)-[:RELATED_TO {type: string, weight: float, confidence: float,
                       mention_refs: [string], created_by: string}]->(:Entity)

(:Chunk)-[:CONTAINS {confidence: float}]->(:Entity)
(:Document)-[:HAS_CHUNK {position: int}]->(:Chunk)
(:Entity)-[:PART_OF_COMMUNITY {level: int, confidence: float}]->(:Community)
```

**Performance Considerations**:
- Index on `Entity.canonical_name`, `Entity.id`
- Index on `Chunk.document_ref`, `Chunk.position`
- Composite index on `(entity_type, confidence)` for filtering
- Graph algorithms index on relationship weights

### SQLite: Metadata and Workflow Storage
**Primary Purpose**: Store metadata, workflow state, and structured data

**Tables Design**:
```sql
-- Workflow Management
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP,
    tool_sequence TEXT,
    current_step INTEGER,
    compression TEXT DEFAULT 'gzip'
);

-- Object Provenance
CREATE TABLE provenance (
    object_id TEXT,
    tool_id TEXT,
    operation TEXT,
    inputs JSON,
    outputs JSON,
    parameters JSON,
    execution_time REAL,
    created_at TIMESTAMP,
    INDEX(object_id), INDEX(tool_id)
);

-- Quality Tracking
CREATE TABLE quality_scores (
    object_id TEXT,
    object_type TEXT,
    confidence REAL,
    quality_tier TEXT,
    method TEXT,
    upstream_scores JSON,
    warnings JSON,
    evidence JSON,
    created_at TIMESTAMP,
    INDEX(object_id), INDEX(quality_tier)
);

-- Version Management
CREATE TABLE object_versions (
    object_id TEXT,
    version_number INTEGER,
    version_type TEXT, -- 'schema', 'data', 'graph', 'analysis'
    parent_version INTEGER,
    changes JSON,
    created_at TIMESTAMP,
    PRIMARY KEY(object_id, version_number)
);

-- Reference Registry
CREATE TABLE object_references (
    reference_id TEXT PRIMARY KEY,
    storage_type TEXT, -- 'neo4j', 'sqlite', 'faiss'
    object_type TEXT,
    internal_id TEXT,
    attributes JSON,
    created_at TIMESTAMP,
    INDEX(storage_type), INDEX(object_type)
);

-- Mention Registry (Three-Level Identity)
CREATE TABLE mentions (
    mention_id TEXT PRIMARY KEY,
    surface_text TEXT,
    document_ref TEXT,
    position INTEGER,
    context_window TEXT,
    entity_candidates JSON,
    selected_entity TEXT,
    confidence REAL,
    created_by TEXT,
    created_at TIMESTAMP,
    INDEX(document_ref), INDEX(selected_entity)
);

-- Configuration
CREATE TABLE tool_configs (
    tool_id TEXT,
    config_name TEXT,
    config_value JSON,
    domain TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY(tool_id, config_name)
);
```

### FAISS: Vector Storage and Search
**Primary Purpose**: High-performance vector similarity search

**Index Structure**:
```python
# Multi-Index Design
{
    "entity_embeddings": {
        "index_type": "IVF",
        "dimension": 384,  # sentence-transformers default
        "nlist": 100,     # for IVF
        "metric": "cosine"
    },
    "chunk_embeddings": {
        "index_type": "HNSW",
        "dimension": 384,
        "M": 16,           # HNSW parameter
        "metric": "cosine"
    },
    "relationship_embeddings": {
        "index_type": "Flat",  # Exact search for relationships
        "dimension": 384,
        "metric": "cosine"
    }
}

# Reference Mapping
{
    "entity_id_to_vector_id": {},  # Neo4j ID -> FAISS vector ID
    "vector_id_to_entity_id": {},  # FAISS vector ID -> Neo4j ID
    "metadata": {
        "entity_types": {},        # vector_id -> entity_type
        "confidence_scores": {},   # vector_id -> confidence
        "last_updated": {}         # vector_id -> timestamp
    }
}
```

## Reference System Design

### Universal Reference Format
All objects use standardized references for cross-database consistency:

```python
# Reference Format: storage://type/id
"neo4j://entity/ent_12345"
"sqlite://mention/mention_67890"
"faiss://embedding/vec_54321"

# Reference Resolution
class ReferenceResolver:
    def resolve(self, ref: str, fields: List[str] = None) -> Dict:
        storage, obj_type, obj_id = self.parse_reference(ref)
        
        if storage == "neo4j":
            return self.neo4j_client.get_node(obj_type, obj_id, fields)
        elif storage == "sqlite":
            return self.sqlite_client.get_record(obj_type, obj_id, fields)
        elif storage == "faiss":
            return self.faiss_client.get_vector(obj_id, include_metadata=True)
    
    def resolve_batch(self, refs: List[str]) -> Dict[str, Dict]:
        # Group by storage for efficient batch operations
        by_storage = defaultdict(list)
        for ref in refs:
            storage = ref.split("://")[0]
            by_storage[storage].append(ref)
        
        results = {}
        for storage, storage_refs in by_storage.items():
            results.update(self.batch_resolve(storage, storage_refs))
        
        return results
```

## Data Flow Patterns

### 1. Ingestion Flow (T01-T12 → Storage)
```python
# Document Processing Chain
def ingest_document(file_path: str) -> Dict[str, List[str]]:
    # T01: Load document
    doc_result = T01_pdf_loader(file_path=file_path)
    doc_ref = doc_result.reference  # "sqlite://document/doc_12345"
    
    # Store in SQLite with metadata
    sqlite_store(doc_result.data, table="documents")
    
    # Record provenance
    T110_provenance.record(
        tool_id="T01",
        inputs=[file_path],
        outputs=[doc_ref],
        parameters={"extract_images": False}
    )
    
    return {"document_refs": [doc_ref]}
```

### 2. Processing Flow (Extract → Store → Reference)
```python
def extract_entities(chunk_refs: List[str]) -> Dict[str, List[str]]:
    # T23a: Extract entities from chunks
    mentions = []
    for chunk_ref in chunk_refs:
        # Resolve chunk content
        chunk_data = reference_resolver.resolve(chunk_ref, fields=["content"])
        
        # Extract mentions
        mention_results = T23a_ner(text=chunk_data["content"])
        
        # Store mentions in SQLite
        for mention in mention_results:
            mention_ref = sqlite_store(mention, table="mentions")
            mentions.append(mention_ref)
    
    # T31: Build entity nodes in Neo4j
    entity_refs = []
    for mention_ref in mentions:
        entity_result = T31_entity_builder(mention_refs=[mention_ref])
        entity_ref = neo4j_store(entity_result.data, node_type="Entity")
        entity_refs.append(entity_ref)
    
    return {"entity_refs": entity_refs, "mention_refs": mentions}
```

### 3. Analysis Flow (Graph → Table → Analysis → Graph)
```python
def statistical_analysis(graph_ref: str) -> Dict:
    # T115: Convert graph to table format
    table_result = T115_graph_to_table(
        graph_ref=graph_ref,
        output_format="wide",
        include_attributes=["confidence", "entity_type"]
    )
    
    # Store table in SQLite
    table_ref = sqlite_store(table_result.data, table="analysis_tables")
    
    # Run external statistical analysis
    stats_result = run_statistical_tests(table_ref)
    
    # T116: Convert results back to graph if needed
    if stats_result.create_graph:
        enhanced_graph_ref = T116_table_to_graph(
            table_ref=table_ref,
            source_column="entity_1",
            target_column="entity_2",
            relationship_type="statistical_correlation",
            attribute_columns=["correlation_score", "p_value"]
        )
        return {"enhanced_graph_ref": enhanced_graph_ref}
    
    return {"statistics": stats_result.data}
```

### 4. Retrieval Flow (Query → Search → Rank → Return)
```python
def entity_search(query: str, top_k: int = 10) -> Dict:
    # T49: Vector search in FAISS
    query_embedding = embed_query(query)
    similar_vectors = faiss_search(
        query_embedding, 
        index="entity_embeddings", 
        k=top_k * 2  # Get more for reranking
    )
    
    # Resolve vector IDs to entity references
    entity_refs = [
        f"neo4j://entity/{vector_id_to_entity_id[vid]}" 
        for vid in similar_vectors.ids
    ]
    
    # T111: Filter by quality
    quality_filtered = T111_quality_filter(
        object_refs=entity_refs,
        min_confidence=0.7,
        quality_tiers=["high", "medium"]
    )
    
    # T68: Rank by PageRank scores (if available)
    if graph_analysis_available():
        pagerank_scores = T68_pagerank(entity_refs=quality_filtered)
        ranked_entities = combine_similarity_and_pagerank(
            similarity_scores=similar_vectors.scores,
            pagerank_scores=pagerank_scores
        )
    else:
        ranked_entities = quality_filtered[:top_k]
    
    return {"entity_refs": ranked_entities[:top_k]}
```

## Tool Integration Matrix

### Core Services Dependencies (T107-T121)
All tools depend on these core services:

| Service | Used By | Purpose |
|---------|---------|---------|
| T107: Identity | T23, T25, T31, T34 | Three-level identity management |
| T108: Versioning | ALL tools | Change tracking |
| T109: Normalizer | T31, T34 | Entity standardization |
| T110: Provenance | ALL tools | Operation tracking |
| T111: Quality | ALL tools | Confidence management |
| T121: Workflow State | MCP Server | Checkpoint/recovery |

### Database Integration Points

#### Neo4j Integration Tools
| Tool | Operation | Data Flow |
|------|-----------|-----------|
| T31 | Entity → Node | SQLite mentions → Neo4j entities |
| T34 | Relationship → Edge | Entity refs → Neo4j relationships |
| T36 | Graph Merge | Multiple graphs → Single Neo4j graph |
| T76 | Neo4j CRUD | All graph operations |
| T68-T75 | Analytics | Neo4j → Analysis results |

#### SQLite Integration Tools
| Tool | Operation | Data Flow |
|------|-----------|-----------|
| T01-T12 | Document metadata | Files → SQLite documents |
| T15a/b | Chunk storage | Documents → SQLite chunks |
| T23a/b | Mention storage | Chunks → SQLite mentions |
| T77 | SQLite CRUD | All metadata operations |
| T121 | State management | Workflow → SQLite checkpoints |

#### FAISS Integration Tools
| Tool | Operation | Data Flow |
|------|-----------|-----------|
| T41-T44 | Embedding creation | Text/Nodes → FAISS vectors |
| T45-T46 | Index building | Vectors → FAISS indices |
| T49 | Entity search | Query → FAISS → Entity refs |
| T56 | Relationship search | Query → FAISS → Relationship refs |
| T78 | FAISS CRUD | All vector operations |

## Consistency and Integrity

### Transaction Management
```python
class DatabaseTransaction:
    def __init__(self):
        self.neo4j_tx = None
        self.sqlite_tx = None
        self.faiss_operations = []
    
    def begin(self):
        self.neo4j_tx = neo4j_driver.session().begin_transaction()
        self.sqlite_tx = sqlite_conn.cursor()
        self.sqlite_conn.execute("BEGIN")
    
    def commit(self):
        # FAISS operations first (can't rollback)
        for operation in self.faiss_operations:
            operation.execute()
        
        # Then transactional databases
        self.neo4j_tx.commit()
        self.sqlite_conn.commit()
    
    def rollback(self):
        self.neo4j_tx.rollback()
        self.sqlite_conn.rollback()
        # FAISS changes can't be rolled back - log for manual cleanup
        logger.error(f"FAISS operations completed, manual cleanup needed: {self.faiss_operations}")
```

### Reference Integrity
```python
def validate_reference_integrity():
    """Ensure all references point to existing objects"""
    
    # Check SQLite → Neo4j references
    sqlite_entity_refs = get_all_entity_references_from_sqlite()
    neo4j_entities = get_all_entity_ids_from_neo4j()
    
    orphaned_refs = set(sqlite_entity_refs) - set(neo4j_entities)
    if orphaned_refs:
        logger.warning(f"Orphaned entity references in SQLite: {orphaned_refs}")
    
    # Check Neo4j → FAISS references  
    neo4j_entities_with_embeddings = get_entities_with_embedding_flag()
    faiss_vector_mappings = get_faiss_entity_mappings()
    
    missing_embeddings = set(neo4j_entities_with_embeddings) - set(faiss_vector_mappings.keys())
    if missing_embeddings:
        logger.warning(f"Entities missing embeddings: {missing_embeddings}")
```

### Quality Consistency
```python
def propagate_quality_changes(object_ref: str, new_confidence: float):
    """Update confidence scores across all databases"""
    
    # Update source object
    update_object_confidence(object_ref, new_confidence)
    
    # Find and update dependent objects
    dependents = T110_provenance.find_dependent_objects(object_ref)
    
    for dependent_ref in dependents:
        # Recalculate confidence based on propagation rules
        upstream_confidences = get_upstream_confidences(dependent_ref)
        new_dependent_confidence = T111_quality.propagate(upstream_confidences)
        
        # Recursively update
        propagate_quality_changes(dependent_ref, new_dependent_confidence)
```

## Performance Optimization

### Connection Pooling
```python
# Database connection management
class DatabaseManager:
    def __init__(self):
        # Neo4j connection pool
        self.neo4j_driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50
        )
        
        # SQLite connection pool
        self.sqlite_pool = queue.Queue(maxsize=10)
        for _ in range(10):
            conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.sqlite_pool.put(conn)
        
        # FAISS indices cached in memory
        self.faiss_indices = {}
        self.load_faiss_indices()
```

### Caching Strategy
```python
# Multi-level caching
class CacheManager:
    def __init__(self):
        # L1: In-memory cache for hot data
        self.memory_cache = {}  # LRU with 1000 items
        
        # L2: Redis cache for distributed access
        self.redis_cache = redis.Redis(host='localhost', port=6379, db=0)
        
        # L3: Disk cache for computed results
        self.disk_cache = diskcache.Cache('./cache')
    
    def get(self, key: str):
        # Check L1 first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check L2
        redis_result = self.redis_cache.get(key)
        if redis_result:
            result = pickle.loads(redis_result)
            self.memory_cache[key] = result  # Promote to L1
            return result
        
        # Check L3
        if key in self.disk_cache:
            result = self.disk_cache[key]
            self.redis_cache.setex(key, 3600, pickle.dumps(result))  # Promote to L2
            self.memory_cache[key] = result  # Promote to L1
            return result
        
        return None
```

### Batch Processing
```python
def batch_process_entities(entity_refs: List[str], batch_size: int = 100):
    """Process entities in batches for efficiency"""
    
    for i in range(0, len(entity_refs), batch_size):
        batch = entity_refs[i:i + batch_size]
        
        # Batch resolve from databases
        resolved_entities = reference_resolver.resolve_batch(batch)
        
        # Batch create embeddings
        texts = [entity['canonical_name'] for entity in resolved_entities.values()]
        embeddings = T41_sentence_embedder.embed_batch(texts)
        
        # Batch store in FAISS
        T78_faiss_manager.add_vectors_batch(embeddings, list(resolved_entities.keys()))
        
        # Update progress
        progress = min((i + batch_size) / len(entity_refs), 1.0)
        T121_workflow_state.update_progress(progress)
```

## Error Handling and Recovery

### Database-Specific Error Handling
```python
class DatabaseErrorHandler:
    def handle_neo4j_error(self, error, operation):
        if isinstance(error, ServiceUnavailable):
            # Try backup Neo4j instance
            return self.retry_with_backup_neo4j(operation)
        elif isinstance(error, TransientError):
            # Retry with exponential backoff
            return self.retry_with_backoff(operation)
        else:
            # Log and raise
            logger.error(f"Neo4j error in {operation}: {error}")
            raise
    
    def handle_sqlite_error(self, error, operation):
        if "database is locked" in str(error):
            # Wait and retry
            time.sleep(0.1)
            return self.retry_sqlite_operation(operation)
        else:
            logger.error(f"SQLite error in {operation}: {error}")
            raise
    
    def handle_faiss_error(self, error, operation):
        if "index not trained" in str(error):
            # Train index and retry
            self.train_faiss_index()
            return self.retry_faiss_operation(operation)
        else:
            logger.error(f"FAISS error in {operation}: {error}")
            raise
```

### Data Recovery Procedures
```python
def recover_from_partial_failure(workflow_id: str):
    """Recover from partial system failure"""
    
    # Get last checkpoint
    checkpoint = T121_workflow_state.get_last_checkpoint(workflow_id)
    
    # Verify data consistency at checkpoint
    integrity_check = validate_data_consistency(checkpoint.timestamp)
    
    if integrity_check.is_consistent:
        # Resume from checkpoint
        T121_workflow_state.restore_checkpoint(workflow_id, checkpoint.id)
        logger.info(f"Resumed workflow {workflow_id} from checkpoint {checkpoint.id}")
    else:
        # Rollback to previous consistent state
        previous_checkpoint = T121_workflow_state.get_previous_checkpoint(checkpoint.id)
        T121_workflow_state.restore_checkpoint(workflow_id, previous_checkpoint.id)
        logger.warning(f"Rolled back workflow {workflow_id} to checkpoint {previous_checkpoint.id}")
    
    # Clean up any inconsistent data
    cleanup_inconsistent_data(integrity_check.issues)
```

This comprehensive integration plan ensures that all 121 tools can work seamlessly across the three database systems while maintaining data consistency, performance, and reliability.