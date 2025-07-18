
# ADR-003: Vector Store Consolidation

**Date**: 2025-07-18  
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

## ✅ **Selected Solution: Bi-Store Architecture**

1.  **Data Stores**:
    -   **Neo4j**: Will store both the property graph and the vector embeddings for all entities. An `HNSW` index will be created on the `embedding` property of `:Entity` nodes.
    -   **SQLite**: Will continue to be used for the encrypted PII vault. Workflow state will be managed by Redis as per ADR-002's findings.

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
-   ✅ **Architectural Simplification**: Eliminates an entire service and the complex cross-service consistency logic.
-   ✅ **Strong Consistency**: Vector and graph data are now updated atomically within the same transaction. The orphan-reference problem is eliminated.
-   ✅ **Reduced Maintenance**: Fewer code components and operational processes to manage.
-   ✅ **Future-Proof**: The `VectorStore` interface provides a clean extension point for future scalability needs.

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

**Related ADRs**: Supersedes the "Tri-Store Consistency" section of ADR-001/ADR-002 discussions. Complements the move to Redis for workflow state. 