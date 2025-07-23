# ADR-009: Bi-Store Database Strategy

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: System requires both graph analysis capabilities and operational metadata storage for academic research workflows.

## Decision

We will implement a **bi-store architecture** using:

1. **Neo4j (v5.13+)**: Primary graph database for entities, relationships, and vector embeddings
2. **SQLite**: Operational metadata database for provenance, workflow state, and PII vault

```python
# Unified access pattern
class DataManager:
    def __init__(self):
        self.neo4j = Neo4jManager()      # Graph operations
        self.sqlite = SQLiteManager()    # Metadata operations
    
    def store_entity(self, entity_data):
        # Store graph data in Neo4j
        entity_id = self.neo4j.create_entity(entity_data)
        
        # Store operational metadata in SQLite
        self.sqlite.log_provenance(entity_id, "entity_creation", entity_data)
        
        return entity_id
```

## Rationale

### **Why Two Databases Instead of One?**

**1. Graph Analysis Requirements**: Academic research requires complex graph operations:
- **Entity relationship analysis**: "Find all researchers influenced by Foucault"
- **Community detection**: Identify research clusters and schools of thought
- **Path analysis**: "How is theory A connected to theory B?"
- **Centrality analysis**: Identify most influential concepts/researchers

**Neo4j excels at these operations with Cypher queries like:**
```cypher
MATCH (a:Entity {name: "Foucault"})-[:INFLUENCES*1..3]->(influenced)
RETURN influenced.name, length(path) as degrees_of_separation
```

**2. Operational Metadata Requirements**: Academic integrity requires detailed operational tracking:
- **Provenance tracking**: Complete audit trail of every operation
- **Workflow state**: Long-running research workflow checkpoints
- **PII protection**: Encrypted storage of sensitive personal information
- **Configuration state**: Tool settings and parameter tracking

**SQLite excels at these operations with relational queries and ACID transactions.**

**3. Performance Optimization**: 
- **Graph queries** on Neo4j: Optimized for traversal and pattern matching
- **Metadata queries** on SQLite: Optimized for joins, aggregations, and transactional consistency

### **Why Not Single Database Solutions?**

**Neo4j Only**:
- ❌ **Poor relational operations**: Complex joins and aggregations are inefficient
- ❌ **Metadata bloat**: Operational metadata clutters graph with non-analytical data
- ❌ **ACID limitations**: Neo4j transactions less robust for operational metadata
- ❌ **PII security**: Graph databases not optimized for encrypted key-value storage

**SQLite Only**:
- ❌ **Graph operations**: Recursive CTEs cannot match Neo4j's graph algorithm performance
- ❌ **Vector operations**: No native vector similarity search capabilities
- ❌ **Scalability**: Graph traversals become exponentially slow with data growth
- ❌ **Cypher equivalent**: No domain-specific query language for graph patterns

**PostgreSQL Only**:
- ❌ **Local deployment**: Requires server setup incompatible with academic research environments
- ❌ **Graph extensions**: Extensions like AGE add complexity without matching Neo4j performance
- ❌ **Vector search**: Extensions available but not as mature as Neo4j's native support

## Alternatives Considered

### **1. Neo4j + PostgreSQL**
- **Rejected**: PostgreSQL server requirement incompatible with single-node academic research
- **Problem**: Requires database server administration and configuration

### **2. Pure Neo4j with Metadata as Graph Nodes**
- **Rejected**: Creates graph pollution and performance degradation
- **Problem**: Provenance metadata would create millions of nodes unrelated to research analysis

### **3. Pure SQLite with Graph Tables**
- **Rejected**: Recursive graph queries become prohibitively slow
- **Problem**: Academic research requires complex graph analysis not feasible in pure SQL

### **4. In-Memory Graph (NetworkX) + SQLite**
- **Rejected**: Memory limitations prevent analysis of large research corpora
- **Problem**: Cannot handle 1000+ document research projects

## Consequences

### **Positive**
- **Optimal Performance**: Each database handles operations it's designed for
- **Data Separation**: Analytical data separate from operational metadata
- **Local Deployment**: Both databases support single-node academic environments
- **Specialized Tooling**: Can use Neo4j Browser for graph exploration, SQL tools for metadata
- **Vector Integration**: Neo4j v5.13+ native vector support for embeddings

### **Negative**
- **Complexity**: Two database systems to maintain and coordinate
- **Transaction Coordination**: Cross-database transactions require careful coordination
- **Data Synchronization**: Entity IDs must remain consistent across both stores
- **Backup Complexity**: Two separate backup and recovery procedures required

## Data Distribution Strategy

### **Neo4j Store**
```cypher
// Entities with vector embeddings
(:Entity {
    id: string,
    canonical_name: string,
    entity_type: string,
    confidence: float,
    embedding: vector[384]
})

// Relationships
(:Entity)-[:INFLUENCES {confidence: float, source: string}]->(:Entity)

// Documents
(:Document {id: string, title: string, source: string})

// Vector indexes for similarity search
CREATE VECTOR INDEX entity_embedding_index 
FOR (e:Entity) ON (e.embedding)
```

### **SQLite Store**
```sql
-- Complete provenance tracking
CREATE TABLE provenance (
    object_id TEXT,
    tool_id TEXT,
    operation TEXT,
    inputs JSON,
    outputs JSON,
    execution_time REAL,
    created_at TIMESTAMP
);

-- Workflow state for long-running processes
CREATE TABLE workflow_states (
    workflow_id TEXT PRIMARY KEY,
    state_data JSON,
    checkpoint_time TIMESTAMP
);

-- Encrypted PII storage
CREATE TABLE pii_vault (
    pii_id TEXT PRIMARY KEY,
    ciphertext_b64 TEXT NOT NULL,
    nonce_b64 TEXT NOT NULL
);
```

## Transaction Coordination

For operations affecting both databases:

```python
@contextmanager
def distributed_transaction():
    """Coordinate transactions across Neo4j and SQLite"""
    neo4j_tx = None
    sqlite_tx = None
    
    try:
        # Start both transactions
        neo4j_session = neo4j_driver.session()
        neo4j_tx = neo4j_session.begin_transaction()
        sqlite_tx = sqlite_conn.begin()
        
        yield (neo4j_tx, sqlite_tx)
        
        # Commit both if successful
        neo4j_tx.commit()
        sqlite_tx.commit()
        
    except Exception as e:
        # Rollback both on any failure
        if neo4j_tx:
            neo4j_tx.rollback()
        if sqlite_tx:
            sqlite_tx.rollback()
        raise DistributedTransactionError(f"Transaction failed: {e}")
```

## Implementation Requirements

### **Consistency Guarantees**
- Entity IDs must be identical across both databases
- All graph operations must have corresponding provenance entries
- Transaction failures must rollback both databases

### **Performance Requirements**
- Graph queries: < 2 seconds for typical academic research patterns
- Metadata queries: < 500ms for provenance and workflow operations
- Cross-database coordination: < 100ms overhead

### **Backup and Recovery**
- Neo4j: Graph database dumps with entity/relationship preservation
- SQLite: File-based backups with transaction log consistency
- Coordinated restoration ensuring ID consistency

## Validation Criteria

- [ ] Graph analysis queries perform within academic research requirements
- [ ] Metadata operations maintain ACID properties
- [ ] Cross-database entity ID consistency maintained
- [ ] Transaction coordination prevents partial failures
- [ ] Backup/recovery maintains data integrity across both stores
- [ ] Vector similarity search performs effectively on research corpora

## Related ADRs

- **ADR-008**: Core Service Architecture (services use both databases)
- **ADR-006**: Cross-Modal Analysis (requires graph and metadata coordination)
- **ADR-003**: Vector Store Consolidation (Neo4j vector capabilities)

## Implementation Status

This ADR describes the **target bi-store database architecture** - the intended Neo4j + SQLite design. For current database implementation status and data layer progress, see:

- **[Roadmap Overview](../../roadmap/ROADMAP_OVERVIEW.md)** - Current database implementation status
- **[Core Service Implementation](../../roadmap/phases/phase-2-implementation-evidence.md)** - Database service completion status
- **[Data Architecture Progress](../../roadmap/initiatives/clear-implementation-roadmap.md)** - Bi-store implementation timeline

*This ADR contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*

---

This bi-store strategy optimizes for both analytical capabilities and operational reliability required for rigorous academic research while maintaining the simplicity appropriate for single-node research environments.