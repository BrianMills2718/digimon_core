# KGAS Architecture Documentation

> **📍 SOLE SOURCE OF TRUTH**: This directory is the authoritative source for architectural goals, target design, and system specifications. For current implementation status and development progress, see [docs/roadmap/ROADMAP_OVERVIEW.md](../roadmap/ROADMAP_OVERVIEW.md).

## Overview

This directory contains the **target architecture** documentation for KGAS (Knowledge Graph Analysis System). These documents define the intended final system design, component relationships, data flows, and architectural decisions that guide implementation.

**Target Environment**: Academic research tool for local deployment with web access for small research groups. **NO enterprise/production scenarios** (authentication, high availability, horizontal scaling, compliance) are planned or architected.

**Important**: This directory contains NO implementation status information. For current development progress, see [docs/roadmap/ROADMAP_OVERVIEW.md](../roadmap/ROADMAP_OVERVIEW.md).

## Architecture Documentation Structure

### Core Architecture Documents
- **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)**: Single source of truth for system architecture
- **[ARCHITECTURE_CRITICAL_REVIEW.md](ARCHITECTURE_CRITICAL_REVIEW.md)**: Critical analysis of architectural inconsistencies and recommendations
- **[LIMITATIONS.md](LIMITATIONS.md)**: Documented system limitations and constraints
- **[cross-modal-analysis.md](cross-modal-analysis.md)**: Cross-modal analysis architecture details
- **[agent-interface.md](agent-interface.md)**: Three-layer agent interface specification
- **[project-structure.md](project-structure.md)**: Project organization and structure

### Specialized Architecture Areas
- **[adrs/](adrs/)**: Architecture Decision Records (ADRs) documenting key decisions
- **[concepts/](concepts/)**: Core architectural concepts and design patterns
- **[data/](data/)**: Data architecture, schemas, and storage design
- **[specifications/](specifications/)**: Formal specifications and capability registries
- **[systems/](systems/)**: Detailed design of major system components

## Key Architectural Principles

### 1. Academic Research Focus
- **Single-node design**: Optimized for local research environments
- **Flexibility over performance**: Prioritizes correctness and flexibility
- **Theory-aware processing**: Supports domain-specific ontologies and analysis
- **Reproducibility**: Full provenance tracking and audit trails

### 2. Cross-Modal Analysis Architecture
The system enables fluid movement between three data representations:
- **Graph Analysis**: Relationships, centrality, communities, paths
- **Table Analysis**: Statistical analysis, aggregations, correlations
- **Vector Analysis**: Similarity search, clustering, embeddings
- **Cross-Modal Integration**: Seamless conversion with source traceability

### 3. Bi-Store Data Architecture
- **Neo4j**: Graph and vector storage with native algorithms
- **SQLite**: Metadata, workflow state, and operational data
- **Unified Interface**: Single API across both storage systems

### 4. Service-Oriented Architecture
- **Core Services**: Pipeline orchestration, analytics, identity, provenance
- **Tool Ecosystem**: 121+ tools with standardized contracts
- **MCP Integration**: Model Context Protocol for tool access

## Documentation Standards

### Target Architecture vs Implementation Status
- **Architecture documents** define the intended design
- **Implementation status** is tracked in [docs/roadmap/](../roadmap/)
- **No mixing** of design specifications with progress tracking

### Architecture Decision Records (ADRs)
All major architectural decisions are documented in [adrs/](adrs/) following the standard ADR format:
- **Context**: Situation leading to the decision
- **Decision**: What was decided
- **Rationale**: Why this decision was made
- **Consequences**: Results of the decision
- **Alternatives**: Other options considered

## Getting Started

1. Start with [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) for the complete system design
2. Review [ARCHITECTURE_CRITICAL_REVIEW.md](ARCHITECTURE_CRITICAL_REVIEW.md) for known issues and recommendations
3. Explore specific areas in [concepts/](concepts/), [data/](data/), and [systems/](systems/)
4. Check [adrs/](adrs/) for architectural decision context

## Current Implementation Status

**This information is NOT maintained in architecture documents.**

For current implementation status, development progress, and project roadmap, see:
- **[Master Roadmap](../roadmap/ROADMAP_OVERVIEW.md)** - Overall project status
- **[Implementation Phases](../roadmap/phases/)** - Phase-by-phase progress
- **[Architecture Status Issues](../roadmap/architecture-status-issues.md)** - Critical architectural issues being addressed

## Contributing to Architecture

### Making Architecture Changes
1. **Document decisions** in ADRs for significant changes
2. **Update affected documents** to maintain consistency
3. **Avoid implementation status** - keep architecture documents focused on design
4. **Cross-reference dependencies** between related architectural decisions

### Review Process
- Major architectural changes require team consensus
- Updates must maintain alignment with core principles
- Cross-reference impacts must be assessed
- Regular consistency reviews ensure documentation quality

---

*This architecture documentation defines the target system design. All implementation progress tracking occurs in the roadmap documentation.*