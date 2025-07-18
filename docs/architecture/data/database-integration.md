---
status: living
---

# Database Integration

This document provides a comprehensive overview of the database systems used in the KGAS project, focusing on the simplified **bi-store architecture** as decided in **ADR-003**. The system leverages Neo4j for graph and vector data, and SQLite for PII and metadata storage.

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
              │  Data Router  │ ← Manages data access
              │ (T121 State)  │
              └───────┬───────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
┌──────────────────────┐    ┌──────────┐
│  Neo4j (v5.13+)      │    │  SQLite  │
│                      │    │(Metadata)│
│ ┌──────────────────┐ │    │          │
│ │ Graph Store      │ │    │ Documents│
│ │ (Entities, Rels) │ │    │ Workflow │
│ └──────────────────┘ │    │  State   │
│ ┌──────────────────┐ │    │ PII Vault│
│ │ Vector Index     │ │    └──────────┘
│ │ (HNSW Embeddings)│ │
│ └──────────────────┘ │
└──────────────────────┘
```

## Data Storage Distribution

### Neo4j: Unified Graph and Vector Storage
**Primary Purpose**: Store structured graph data and their corresponding vector embeddings within a single, transactionally consistent database.

**Stored Objects**:
-   **Entities**: Canonical entities with resolved identities.
-   **Relationships**: Typed edges between entities.
-   **Vector Embeddings**: High-dimensional vectors stored as a property on entity nodes, indexed for fast similarity search.
-   **Graph Metadata**: Schema, constraints, and both property and vector indices.

**Schema Design**:
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
**Performance Considerations**:
-   The native HNSW vector index in Neo4j 5.13+ provides sub-second approximate nearest-neighbor search.
-   Standard property indexes on `Entity.id` and `Entity.canonical_name` are still crucial for lookups.

### SQLite: Metadata and PII Vault
**Primary Purpose**: Store workflow state, operational metadata, and the encrypted vault for Personally Identifiable Information (PII).

**Tables Design**:
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

-- PII Vault (Example)
CREATE TABLE pii_vault (
    hash_id TEXT PRIMARY KEY,
    encrypted_plaintext BLOB,
    nonce BLOB,
    tag BLOB,
    created_at TIMESTAMP
);
```

## Data Flow and Consistency

The bi-store architecture dramatically simplifies data consistency.

1.  **Phase Processing**: An incoming document is processed by a series of phases (e.g., entity extraction, relationship analysis, embedding generation).
2.  **Transactional Write**: All graph data (nodes, relationships) and their corresponding vector embeddings are written to Neo4j within a **single ACID transaction**.
3.  **Atomic Commit**: The transaction either fully succeeds or fully fails. This **eliminates the risk of orphan vectors** or inconsistencies between the graph and the vector index, as the updates are atomic.
4.  **Metadata Storage**: Workflow state and provenance information are written to SQLite in separate transactions, as they are not part of the core graph's semantic integrity.

This model removes the need for complex two-phase commits, transactional outboxes, or reconciliation jobs, leading to a more robust and maintainable system.