---
status: living
---

# Services vs Tools Architecture

## Overview

KGAS uses a two-layer architecture that separates orchestration concerns (Services) from execution concerns (Tools). This document clarifies the distinction and their interaction patterns.

## Architectural Layers

### Services Layer (Orchestration)
Services are long-running, stateful components that orchestrate and optimize the execution of analysis tasks. They handle:

- **Resource Management**: Memory monitoring, performance optimization
- **Safety Gates**: Preventing resource exhaustion
- **Orchestration**: Coordinating multiple tools for complex workflows
- **State Management**: Maintaining context across operations
- **Cross-Cutting Concerns**: Logging, monitoring, error handling

**Location**: `/src/services/`

### Tools Layer (Execution)
Tools are stateless, single-purpose functions exposed via the MCP protocol. They handle:

- **Specific Tasks**: One tool = one specific analysis capability
- **Atomic Operations**: Each tool completes independently
- **Data Transformation**: Converting between formats
- **Analysis Algorithms**: Implementing specific calculations
- **External Integration**: Connecting to APIs or databases

**Location**: `/src/tools/`

## Service-Tool Interaction Pattern

```
User Request
     │
     ▼
┌─────────────────┐
│  API Endpoint   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│AnalyticsService │ ← Orchestration Layer
│ - Safety checks │
│ - Resource mgmt │
│ - Workflow coord│
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│T1-T30  ││T31-T60 ││T61-T90 ││T91-T121│ ← Execution Layer
│Graph   ││Table   ││Vector  ││Cross-  │
│Tools   ││Tools   ││Tools   ││Modal   │
└────────┘└────────┘└────────┘└────────┘
```

## Example: PageRank Analysis

### Without Service (Direct Tool Call)
```python
# Direct tool call - no safety checks
result = t68_pagerank.execute(graph)  # May crash on large graphs
```

### With Service (Orchestrated)
```python
# Service-orchestrated call - includes safety checks
analytics = AnalyticsService()
result = analytics.run_pagerank(graph)
# Service checks graph size, memory, and selects appropriate algorithm
```

## Service Implementations

### AnalyticsService
**Purpose**: Orchestrates all analysis operations across modalities

**Responsibilities**:
- Safety gates for expensive operations
- Algorithm selection based on data characteristics
- Cross-modal workflow coordination
- Performance optimization
- Result caching and reuse

**Interacts with**:
- Graph analysis tools (T1-T30)
- Table analysis tools (T31-T60)
- Vector analysis tools (T61-T90)
- Cross-modal tools (T91-T121)

### PipelineOrchestrator
**Purpose**: Manages document processing workflows

**Responsibilities**:
- Phase coordination
- State management between phases
- Error recovery
- Progress tracking

**Interacts with**:
- Document loaders
- Entity extractors
- Graph builders
- All core services

### IdentityService
**Purpose**: Entity resolution and management

**Responsibilities**:
- Entity deduplication
- Cross-document entity linking
- Entity ID generation
- Mention tracking

**Interacts with**:
- Entity extraction tools
- Graph building tools
- PII service for redaction

### TheoryRepository
**Purpose**: Theory schema and ontology management

**Responsibilities**:
- Theory validation against meta-schema
- Ontology provisioning for extractors
- Theory-specific configuration
- Analytics metric selection

**Interacts with**:
- Theory-aware extraction tools
- Validation tools
- Analytics configuration

## Tool Categories and Examples

### Graph Analysis Tools (T1-T30)
- **T1**: Degree Centrality Calculator
- **T2**: PageRank Calculator (called by AnalyticsService)
- **T3**: Betweenness Centrality
- **T4**: Community Detection (Louvain)
- **T5**: Shortest Path Finder
- ...

### Table Analysis Tools (T31-T60)
- **T31**: Graph to Table Converter
- **T32**: Statistical Summary Generator
- **T33**: Correlation Matrix Calculator
- **T34**: Pivot Table Creator
- **T35**: SQL Query Executor
- ...

### Vector Analysis Tools (T61-T90)
- **T61**: Embedding Generator
- **T62**: Cosine Similarity Calculator
- **T63**: K-Means Clusterer
- **T64**: Semantic Search
- **T65**: Dimensionality Reducer (t-SNE)
- ...

### Cross-Modal Tools (T91-T121)
- **T91**: Table to Vector Converter
- **T92**: Vector to Graph Builder
- **T93**: Source Document Linker
- **T94**: Multi-Modal Query Executor
- **T95**: Result Format Selector
- ...

## Design Principles

### Services Should:
- Orchestrate complex workflows
- Manage resources and safety
- Maintain state when needed
- Handle cross-cutting concerns
- Make intelligent decisions about tool selection

### Tools Should:
- Perform one specific task well
- Be stateless and idempotent
- Have clear inputs and outputs
- Be independently testable
- Follow the MCP protocol

### Services Should NOT:
- Implement analysis algorithms directly
- Be tightly coupled to specific tools
- Make assumptions about tool availability

### Tools Should NOT:
- Manage state between calls
- Make decisions about resource usage
- Orchestrate other tools
- Handle cross-cutting concerns

## Benefits of This Architecture

1. **Separation of Concerns**: Clear boundaries between orchestration and execution
2. **Flexibility**: Easy to add new tools without changing services
3. **Safety**: Services ensure safe execution of potentially expensive operations
4. **Reusability**: Tools can be called directly or through services
5. **Testability**: Tools can be tested in isolation
6. **Extensibility**: New analysis types can be added as new tool categories

## Future Extensions

As KGAS evolves, new services may be added:

- **CacheService**: Intelligent result caching across tools
- **MonitoringService**: Real-time performance monitoring
- **SchedulerService**: Batch job scheduling and management
- **NotificationService**: Research progress notifications

Each would follow the same pattern: orchestrating tools while managing cross-cutting concerns.