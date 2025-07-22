### PII Pipeline
1.  **Encrypt PII**: Plaintext PII is encrypted using the `PiiService` (AES-GCM).
2.  **Generate ID**: A unique `pii_id` is generated.
3.  **Store Encrypted Data**: The `{ pii_id, ciphertext_b64, nonce_b64 }` payload is stored in the secure SQLite PII vault.
4.  **Reference in Graph**: The main knowledge graph nodes only ever store the safe `pii_id`.
5.  **Decryption**: Accessing the original PII requires calling the `PiiService.decrypt` method.

### Core Data Flow
1.  **Phase Processing**: An incoming document is processed by a series of phases coordinated by the `PipelineOrchestrator`.
2.  **Transactional Write**: All graph data (nodes, relationships) and their corresponding vector embeddings are written to Neo4j within a **single ACID transaction**.
3.  **Atomic Commit**: The transaction either fully succeeds or fully fails. There is no possibility of orphan vectors, as the graph and vector updates are atomic.
4.  **Metadata Storage**: Workflow state and provenance information are written to SQLite in separate transactions. 