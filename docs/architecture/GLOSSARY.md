# KGAS Architecture Glossary

**Version**: 1.0
**Status**: Active
**Last Updated**: 2025-07-22

## Overview

This glossary defines key terms used throughout the KGAS architecture documentation to ensure consistent understanding and communication.

## Core Architectural Terms

### **Cross-Modal Analysis**
The ability to analyze and convert between three primary data representations (graph, table, vector) while preserving semantic meaning and maintaining source traceability. Unlike traditional approaches that reduce information during conversion, KGAS enriches data as it moves between modalities.

### **Theory-Aware Processing**
System components that understand and utilize theoretical frameworks from academic disciplines during analysis. This includes extracting concepts based on domain-specific theories, validating findings against theoretical predictions, and organizing results using established academic frameworks.

### **Bi-Store Architecture**
A data storage architecture using exactly two database systems with complementary strengths. In KGAS, this refers to Neo4j (for graph and vector data) and SQLite (for metadata and workflow state), chosen to balance complexity with functionality.

### **Contract-First Design**
An architectural pattern where standardized interfaces (contracts) are defined before implementation. All tools in KGAS implement the same contract, enabling consistent integration, testing, and orchestration.

### **Uncertainty Quantification**
A multi-layer approach to tracking confidence and uncertainty throughout the analysis pipeline. Includes data quality, extraction confidence, relationship strength, and theory alignment scores.

## Data Architecture Terms

### **Entity**
A distinct real-world concept extracted from documents (person, organization, location, concept, etc.) that becomes a node in the knowledge graph. Each entity has a canonical form and may have multiple surface forms (mentions).

### **Mention**
A specific reference to an entity within a document. Multiple mentions can refer to the same entity (e.g., "John Smith", "Smith", "he" all referring to the same person).

### **Canonical Name**
The authoritative, standardized form of an entity used consistently throughout the system. For example, "International Business Machines Corporation" might be the canonical name for mentions of "IBM", "Big Blue", etc.

### **Entity Resolution**
The process of determining which mentions refer to the same real-world entity, consolidating them under a single canonical representation in the knowledge graph.

### **Provenance**
Complete tracking of data lineage including source documents, processing tools, timestamps, and transformation history. Enables research reproducibility and audit trails.

## Tool Ecosystem Terms

### **Tool**
A self-contained processing component that performs a specific analysis or transformation task. Tools implement the standardized contract and can be composed into workflows.

### **Tool Contract**
The standardized interface that all tools must implement, defining input/output formats, error handling, confidence scoring, and metadata requirements.

### **Phase**
A major stage in document processing (e.g., ingestion, extraction, analysis). The original architecture defined phases, but the current implementation uses a more flexible tool-based approach.

### **Workflow**
A sequence of tool executions that accomplish a complex analysis task. Workflows can be saved as templates for reproducibility.

### **Pipeline**
The overall system for processing documents from input through analysis to results. Includes document ingestion, entity extraction, graph construction, and analysis.

## Cross-Modal Terms

### **Modal Bridge**
A tool that converts data from one representation to another (e.g., Graph to Table Bridge). Bridges preserve source information and enrich rather than reduce data.

### **Enrichment Strategy**
The architectural principle of adding information during modal conversion rather than losing it. For example, converting a graph to a table adds computed metrics rather than just flattening structure.

### **Source Traceability**
The ability to trace any analysis result back to its original source in the documents. Maintained through all modal conversions and transformations.

## Theory Integration Terms

### **Theory Schema**
A formal representation of concepts, relationships, and rules from an academic theory, expressed in a format the system can process.

### **Indigenous Term**
A concept or terminology that originates from a specific academic domain or theory, as opposed to generic terms. These require special handling to preserve domain-specific meaning.

### **Master Concept Library (MCL)**
A centralized registry of all concepts used across theories, including mappings between similar concepts in different theoretical frameworks.

### **Ontology**
A formal representation of knowledge including concepts, properties, and relationships. KGAS can integrate with existing ontologies like DOLCE or domain-specific ones.

### **DOLCE**
Descriptive Ontology for Linguistic and Cognitive Engineering - a foundational ontology that provides basic categories for describing any domain.

## Processing Terms

### **Chunk**
A meaningful segment of text extracted from a document, sized appropriately for processing. Chunks maintain position information for source traceability.

### **Confidence Score**
A numerical measure (0.0-1.0) indicating the system's confidence in a particular extraction, relationship, or analysis result.

### **Quality Tier**
A categorical assessment of data quality (high/medium/low) based on source reliability, extraction confidence, and validation results.

## Service Architecture Terms

### **Core Service**
A fundamental system component providing essential functionality (e.g., IdentityService, TheoryRepository). Core services are singletons accessible throughout the system.

### **Service Protocol**
The standardized interface that all services implement, ensuring consistent initialization, configuration, and lifecycle management.

### **Service Registry**
A central directory of all available services, enabling dynamic discovery and dependency injection.

## Analysis Terms

### **Centrality**
Graph metrics measuring the importance of nodes. Includes degree centrality (connections), betweenness centrality (bridge positions), and PageRank (influence).

### **Community**
A group of densely connected nodes in a graph, often representing related concepts or entities that frequently appear together.

### **Embedding**
A vector representation of text or entities in high-dimensional space, enabling similarity calculations and clustering.

### **Vector Index**
A data structure enabling fast nearest-neighbor searches in high-dimensional vector space. KGAS uses Neo4j's native HNSW index.

## Operational Terms

### **Workflow State**
The current execution status of a processing workflow, including completed steps, pending operations, and intermediate results.

### **Checkpoint**
A saved state of workflow execution that enables resumption after interruption or failure.

### **Reconciliation**
The process of ensuring consistency between different data stores or after system failures.

### **PII Vault**
Encrypted storage for personally identifiable information, separate from the main data stores for security.

## Performance Terms

### **Lazy Loading**
Loading data only when needed rather than eagerly fetching everything upfront. Used to manage memory with large graphs.

### **Batch Processing**
Processing multiple items together for efficiency rather than one at a time.

### **Connection Pooling**
Reusing database connections rather than creating new ones for each operation, improving performance.

### **Async Operation**
Non-blocking operations that allow other processing to continue while waiting for I/O or long-running tasks.

## Quality Assurance Terms

### **Integration Test**
Tests that verify multiple components work correctly together, especially important for tool workflows.

### **Provenance Validation**
Verifying that all data can be traced back to its source and that the processing history is complete.

### **Consistency Check**
Validation that data remains consistent across different stores and after transformations.

### **Mock-Free Testing**
Testing approach that uses real components rather than mocks wherever possible, ensuring tests reflect actual system behavior.

## Future Terms (Planned)

### **Theory Validation Engine**
Planned component for validating analysis results against theoretical predictions.

### **Uncertainty Propagation**
Planned algorithms for calculating how uncertainty compounds through multiple processing steps.

### **Modal Orchestrator**
Planned intelligent component that automatically selects the best data representation for a given analysis task.

### **Distributed Processing**
Planned capability for spreading computation across multiple nodes for large-scale analysis.

---

This glossary is a living document and will be updated as new concepts are introduced or existing terms are refined. For technical implementation details of these concepts, refer to the specific architecture documents in this directory.