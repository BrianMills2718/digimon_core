### Neo4j Schema
```cypher
// Core Node Type with Embedding Property
(:Entity {
    id: string,
    canonical_name: string,
    entity_type: string,
    confidence: float,
    quality_tier: string,
    created_by: string,
    embedding: vector[384] // Native vector type
})

// Vector Index for Fast Similarity Search
CREATE VECTOR INDEX entity_embedding_index IF NOT EXISTS
FOR (e:Entity) ON (e.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: 'cosine'
  }
}
```

### SQLite Schemas
```sql
-- Workflow Management
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP,
    current_step INTEGER
);

-- Object Provenance
CREATE TABLE provenance (
    object_id TEXT,
    tool_id TEXT,
    operation TEXT,
    inputs JSON,
    outputs JSON,
    execution_time REAL,
    created_at TIMESTAMP
);

-- PII Vault
CREATE TABLE pii_vault (
    pii_id TEXT PRIMARY KEY,
    ciphertext_b64 TEXT NOT NULL,
    nonce_b64 TEXT NOT NULL,
    created_at TIMESTAMP
);
``` 