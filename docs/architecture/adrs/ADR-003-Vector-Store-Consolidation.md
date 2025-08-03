
# ADR-003: Vector Store Consolidation

**Date**: 2025-01-18  
**Status**: Accepted  
**Deciders**: Development Team, advised by external architectural review.

---

## 🎯 **Decision**

**Replace the tri-store data platform (Neo4j + SQLite + Qdrant) with a simplified bi-store architecture (Neo4j + SQLite). The native vector index within Neo4j (version 5.13+) will be used for all embedding storage and approximate nearest-neighbor (ANN) search, eliminating the need for a separate Qdrant instance.**

---

## 🚨 **Problem Context**

The previous target architecture employed three separate data stores:
1.  **Neo4j**: For graph data.
2.  **Qdrant**: For vector embeddings.
3.  **SQLite**: For the PII vault and workflow state.

This tri-store model introduced significant architectural complexity, most notably the **"Tri-Store Consistency Risk"** identified during external review. Because Neo4j is transactional (ACID-compliant) and Qdrant is not, ensuring data consistency required a complex **Transactional Outbox Pattern** with compensating transactions and a periodic reconciliation job.

This created several operational liabilities:
-   **Increased Complexity**: Required dedicated services (`OutboxService`, `ReconciliationService`) just to maintain data integrity.
-   **Eventual Consistency Latency**: The reconciliation window could lead to periods of data inconsistency (e.g., "orphan" vectors).
-   **Maintenance Overhead**: More moving parts to monitor, test, and maintain.
-   **Deployment Complexity**: Managing an additional Qdrant instance and its associated Docker configurations.

Given the project's context—a **Python-only, local, academic research platform**—this level of complexity was not justified by the benefits, especially when a simpler, more integrated solution became available.

---

## 💡 **Drivers for Change**

The primary driver is the maturation of **Neo4j's native vector search capabilities**. As of version 5.13, Neo4j includes a production-ready HNSW (Hierarchical Navigable Small World) index that provides:
-   **High-Performance ANN Search**: Sub-second query times for millions of vectors, sufficient for this project's scale.
-   **ACID Guarantees**: Vector writes are part of the same transaction as graph writes. A transaction rollback automatically rolls back both the graph data and the vector index update.
-   **Operational Simplicity**: No separate vector database to manage.

This technical improvement directly nullifies the original reason for including Qdrant.

---

## **Selected Solution: Bi-Store Architecture**

1.  **Data Stores**:
    -   **Neo4j**: Will store both the property graph and the vector embeddings for all entities. An `HNSW` index will be created on the `embedding` property of `:Entity` nodes.
    -   **SQLite**: Will continue to be used for the encrypted PII vault and workflow state management, maintaining the bi-store architecture principle.

2.  **Vector Store Abstraction**:
    -   An abstract `VectorStore` protocol (interface) will be defined in Python.
    -   A concrete `Neo4jVectorStore` class will implement this interface using Cypher queries against the native vector index.
    -   This **Strategy Pattern** isolates the vector storage logic, making it easy to swap back to a dedicated store like Qdrant in the future if scalability demands it, without changing the application logic.

3.  **Code Removal**:
    -   The `OutboxService` and `ReconciliationService` will be deleted.
    -   All direct dependencies on the `qdrant-client` will be removed.
    -   Qdrant will be removed from all Docker compose files.

### **Consequences**

**Positive**:
-   **Architectural Simplification**: Eliminates an entire service and the complex cross-service consistency logic.
-   **Strong Consistency**: Vector and graph data are now updated atomically within the same transaction. The orphan-reference problem is eliminated.
-   **Reduced Maintenance**: Fewer code components and operational processes to manage.
-   **Future-Proof**: The `VectorStore` interface provides a clean extension point for future scalability needs.

**Negative**:
-   **Scalability Ceiling**: Neo4j's native index may not perform as well as a dedicated store like Qdrant at extremely large scales (>100M vectors). This is an acceptable trade-off for this project's scope.
-   **Single Point of Failure**: Consolidating on Neo4j means its availability is even more critical. This is managed by standard backup procedures (e.g., nightly dumps).

---

## 🔧 **Implementation Plan (High-Level)**

1.  **Upgrade Neo4j**: Ensure the environment uses Neo4j v5.13 or newer.
2.  **Create Index**: Add a `CREATE VECTOR INDEX` command to the database schema setup.
3.  **Abstract Interface**: Implement the `VectorStore` protocol and the `Neo4jVectorStore` class.
4.  **Migrate Data**: Write a one-time script to export vectors from Qdrant and load them into the `embedding` property of the corresponding Neo4j nodes.
5.  **Refactor Code**: Replace all calls to the Qdrant client with the new `vector_store` interface.
6.  **Delete Old Code**: Remove all Qdrant-related files and configurations.
7.  **Update Tests**: Modify unit and integration tests to rely only on Neo4j.

---

---

## 🔄 **Trade-off Analysis**

### Options Considered

#### Option 1: Keep Tri-Store Architecture (Neo4j + SQLite + Qdrant)
- **Pros**:
  - Best-in-class vector search performance with Qdrant
  - Independent scaling of vector operations
  - Specialized vector database features (filtering, metadata)
  - Proven architecture pattern for large-scale systems
  
- **Cons**:
  - Complex consistency management across three stores
  - Requires Transactional Outbox Pattern implementation
  - Additional operational overhead (monitoring, backups, updates)
  - Higher infrastructure costs
  - Risk of data inconsistency during reconciliation windows

#### Option 2: Single Neo4j Database (Graph + Vectors + Metadata)
- **Pros**:
  - Simplest possible architecture
  - Perfect consistency (single ACID store)
  - Minimal operational overhead
  - Lowest cost
  
- **Cons**:
  - Poor text/document storage capabilities
  - Limited full-text search compared to dedicated solutions
  - Would require complex JSON storage for metadata
  - Performance concerns with mixed workloads

#### Option 3: Bi-Store Architecture (Neo4j + SQLite) [SELECTED]
- **Pros**:
  - Balanced complexity - simpler than tri-store
  - Strong consistency within each domain (graph+vectors atomic)
  - Leverages Neo4j 5.13+ native vector capabilities
  - SQLite excellent for metadata and workflow state
  - Clean separation of concerns
  - Future migration path via VectorStore abstraction
  
- **Cons**:
  - Vector search may not scale beyond ~10M embeddings
  - Still requires cross-database coordination for some operations
  - Neo4j becomes more critical (single point of failure for core data)

#### Option 4: Alternative Bi-Store (PostgreSQL with pgvector + Neo4j)
- **Pros**:
  - PostgreSQL more feature-rich than SQLite
  - pgvector provides good vector search
  - Could consolidate all non-graph data
  - Better concurrent access than SQLite
  
- **Cons**:
  - Adds PostgreSQL as new dependency
  - More complex than SQLite for single-user research platform
  - Overkill for current scale requirements
  - Would still need consistency management

### Decision Rationale

The bi-store architecture (Option 3) was selected because:

1. **Appropriate Complexity**: Eliminates the most complex aspect (tri-store consistency) while maintaining clean separation between graph and metadata storage.

2. **Scale-Appropriate**: For a research platform processing thousands (not millions) of documents, Neo4j's native vector index is more than sufficient.

3. **Consistency Benefits**: Atomic updates to graph + vectors eliminates entire classes of bugs and complexity.

4. **Future Flexibility**: The VectorStore abstraction allows migration to Qdrant later if scale demands it, without major refactoring.

5. **Operational Simplicity**: One less service to deploy, monitor, backup, and maintain.

6. **Cost Efficiency**: Reduces infrastructure requirements while meeting all functional needs.

### When to Reconsider

This decision should be revisited if:
- Vector corpus grows beyond 10M embeddings
- Query latency for vector search exceeds 500ms consistently  
- Need for advanced vector search features (hybrid search, filtering)
- Moving from single-user to multi-tenant architecture
- Require real-time vector index updates at high throughput

The VectorStore abstraction ensures this future migration would be straightforward, involving only the implementation of a new concrete class without changes to application logic.

---

**Related ADRs**: 
- Supersedes the "Tri-Store Consistency" section of ADR-001/ADR-002 discussions
- **[ADR-009: Bi-Store Database Strategy Rationale](ADR-009-Bi-Store-Database-Strategy.md)**: Provides comprehensive academic workflow rationale for the bi-store architecture established by this ADR
- Complements the workflow state management approach 