# KGAS Architecture Master Document

**Purpose**: This document serves as the high-level entry point for understanding the architecture of the Knowledge Graph Analysis System (KGAS). It provides a comprehensive overview and links to more detailed documentation for each specific aspect of the system.

---

## 🏛️ **1. Core Concepts & System Overview**

This section covers the foundational principles, overall structure, and the "big picture" of the KGAS.

-   **[System Architecture](./ARCHITECTURE.md)**: The primary document detailing the end-to-end architecture, including components, data flow, and target state. **(Start here)**
-   **[Project Structure](./project-structure.md)**: A guide to the repository's layout, helping you find code and documentation.
-   **[Evergreen Documentation](./concepts/kgas-evergreen-documentation.md)**: The unchanging, core theoretical principles behind KGAS.
-   **[System Limitations](./LIMITATIONS.md)**: A realistic look at the known limitations and boundaries of the system.

## ንድ **2. System Design & Patterns**

This section details the specific design patterns, schemas, and methodologies that govern the system's construction.

-   **[Design Patterns](./concepts/design-patterns.md)**: An overview of the key software design patterns used in the codebase.
-   **[Contract System](./systems/contract-system.md)**: The architecture of the tool and adapter contract system that ensures compatibility.
-   **[Plugin System](./systems/plugin-system.md)**: The design for extending system functionality through plugins.
-   **[ORM Methodology](./data/orm-methodology.md)**: The methodology behind the Object-Relational Mapping (ORM) used for database interactions.
-   **[Consistency Framework](./specifications/consistency-framework.md)**: The framework that ensures data and process consistency across the system.

## 🤖 **3. AI, Data Models & Schemas**

This section focuses on the "brains" of the system, including the data structures, AI concepts, and schemas.

-   **[Data Models](./data/MODELS.md)**: Detailed descriptions of the Pydantic data models that form the backbone of the system.
-   **[Theoretical Framework](./concepts/theoretical-framework.md)**: The academic and theoretical underpinnings for the LLM-generated ontologies.
-   **[Theory Meta-Schema](./data/theory-meta-schema.md)**: The meta-schema that enforces the structure of theory-aware components.
-   **[Master Concept Library](./concepts/master-concept-library.md)**: The central library of concepts that provides a common vocabulary for the knowledge graph.
-   **[Schemas](./data/-schemas/)**: The directory containing all JSON schema definitions for validation.

## 🛠️ **4. Tools, Integration & Capabilities**

This section describes how the various parts of the system connect and what they are capable of doing.

-   **[Capability Registry](./specifications/capability-registry.md)**: The central registry of all tools and their defined capabilities.
-   **[Compatibility Matrix](./specifications/compatibility-matrix.md)**: A matrix detailing the integration requirements and status of all system components.
-   **[Database Integration](./data/database-integration.md)**: Documentation on how the system connects to and interacts with the database.
-   **[Provenance System](./specifications/PROVENANCE.md)**: The system for tracking the origin and history of data as it moves through the pipeline.

## ⚖️ **5. Decision Records & Specifications**

This section contains the formal decisions made about the architecture and the detailed specifications for components.

-   **[Architecture Decision Records (ADRs)](./adrs/)**: A directory containing all formal ADRs for significant design choices.
-   **[Specifications](./specifications/SPECIFICATIONS.md)**: Detailed technical specifications for various system components.
-   **[LLM Information](./mcp-llms-full-information.txt)**: In-depth information about the MCP LLMs used in the system.

---
*This master document is intended as a starting point. For deep dives, please refer to the linked documents.* 