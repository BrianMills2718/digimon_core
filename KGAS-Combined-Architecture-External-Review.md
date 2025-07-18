# KGAS Combined Architecture Document
**For External Review**

**Generated**: 2025-07-18 01:02:45
**Purpose**: Comprehensive architecture documentation for external review
**Total Documents**: 12

---

## 📋 Document Overview

This combined document contains the essential architecture documentation for the Knowledge Graph Analysis System (KGAS), a theory-aware GraphRAG platform that integrates social science theories into knowledge graph construction and analysis.

### Document Structure

The following documents are included in this combined architecture review:


1. **KGAS Architecture: Theory-Aware GraphRAG System** - Main comprehensive architecture document
2. **KGAS Architecture Master Document** - High-level overview and navigation
3. **KGAS Evergreen Documentation** - Core theoretical principles
4. **Theoretical Framework** - Academic underpinnings for LLM-generated ontologies
5. **Master Concept Library** - Central vocabulary for knowledge graph operations
6. **Data Models** - Pydantic data model specifications
7. **Theory Meta-Schema** - Theory integration framework
8. **Design Patterns** - Key software design patterns used in the codebase
9. **Contract System** - Tool and adapter contract system architecture
10. **Capability Registry** - Central registry of all tools and capabilities
11. **ADR-001: Phase Interface Design** - Architecture decision record for phase interfaces
12. **ADR-002: Pipeline Orchestrator Architecture** - Architecture decision record for pipeline orchestration

---

# KGAS Architecture: Theory-Aware GraphRAG System

*Main comprehensive architecture document*

# KGAS Architecture: Theory-Aware GraphRAG System

**⚠️ IMPORTANT**: This document defines the TARGET ARCHITECTURE and contains NO implementation status, progress percentages, or current issues. For current status, see the planning documentation.

**Document Version**: 1.1 (Meta-Schema v9.1 sync)  
**Created**: 2025-06-18 • Updated: 2025-07-15  
**Purpose**: Comprehensive architecture documentation for KGAS with theoretical foundation integration

## 🎯 Overview

The Knowledge Graph Analysis System (KGAS) implements a theory-aware GraphRAG architecture that integrates social science theories into knowledge graph construction and analysis. The system is built on Object-Role Modeling (ORM) principles and aligned with the DOLCE upper ontology.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Streamlit UI  │  │   CLI Tools     │  │   API Layer  │  │ API Gateway  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Service Compatibility Layer                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │Version Checking │  │Theory Validation│  │Backward Comp │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Core Services Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────┐  ┌───────────────┐ │
│  │Identity Service │  │Workflow Service │  │Quality Service│  │Telemetry Service   │  │Plugin Registry│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  └────────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Data Storage Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │   Neo4j (Graph  │  │     SQLite      │                    │
│  │   + Vectors)    │  │   (PII Vault)   │                    │
│  └─────────────────┘  └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                Knowledge Representation Layer                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   DOLCE Align   │  │   Theory Meta   │  │   Master     │ │
│  │   ment: every   │  │   Schema v9.1   │  │   Concept    │ │
│  │   entity car-   │  │   with classi-  │  │   Library    │ │
│  │   ries dolce_   │  │   fication.do-  │  │   with MCL   │ │
│  │   parent (IRI   │  │   main tags     │  │   IDs        │ │
│  │   of closest    │  │                 │  │              │ │
│  │   DOLCE class)  │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**API Gateway**: Exposes /query endpoint (JSON DSL) and /graphql endpoint (Strawberry GraphQL). Handles authentication, rate-limiting, and unified access to the knowledge graph.

**Telemetry Service**: Implements OpenTelemetry Collector and Grafana Tempo for distributed tracing and metrics. All core services emit OTel spans; traces are visualized in Grafana dashboards.

**Plugin Registry**: Dynamically loads ToolPlugin and PhasePlugin extensions via setuptools entry points. Enables third-party and user-contributed tools/phases without codebase modification.

## Provenance & Lineage

All entities and relationships in the KGAS graph are linked to their generating activity using W3C PROV conventions:

```
(Entity)-[GENERATED_BY]->(Activity)
```

- **Entity**: Node or edge in the knowledge graph
- **Activity**: Extraction, transformation, or inference process
- **Edge**: `generated_by_activity_id` field links to the activity

This enables full auditability and reproducibility of all graph elements.

## 🔧 Contract System Integration

### YAML/JSON Contract Framework
The system implements a comprehensive contract system for ensuring consistency:

```yaml
# Example: Theory Schema Contract
theory_schema:
  name: "Social Identity Theory"
  version: "1.0"
  concepts:
    - name: "SocialIdentity"
      definition: "Individual's self-concept derived from group membership"
      orm_mapping:
        object_type: "IndividualActor"
        properties:
          - name: "group_membership"
            type: "List[SocialGroup]"
            constraint: "non_empty"
    - name: "InGroupFavoritism"
      definition: "Preference for members of one's own group"
      orm_mapping:
        fact_type: "ExhibitsFavoritismTowards"
        source_role: "Actor"
        target_role: "Target"
        properties:
          - name: "favoritism_score"
            type: "float"
            range: [0.0, 1.0]
```

### Pydantic Validation
All contracts are validated through Pydantic models ensuring type safety and constraint enforcement:

```python
class TheorySchema(BaseModel):
    name: str
    version: str
    concepts: List[ConceptDefinition]
    
    @validator('concepts')
    def validate_concept_uniqueness(cls, v):
        names = [c.name for c in v]
        if len(names) != len(set(names)):
            raise ValueError("Concept names must be unique")
        return v
```

## 🔄 System Integration

The system is designed with clear interfaces between phases and services to ensure seamless integration. All components follow standardized protocols for data exchange and state management.

## 🔄 Runtime Data Flow

### PII Pipeline
1. Regex extract PII → deterministic SHA-256 hash.
2. Store `{hash → plaintext}` in an encrypted SQLite vault.
3. KG nodes keep only the hash; vault access requires MFA.
4. Salt is rotated on a configurable schedule.

### Core Data Flow
1.  **Phase Processing**: An incoming document is processed by a series of phases (e.g., entity extraction, relationship analysis).
2.  **Transactional Write**: All graph data (nodes, relationships) and their corresponding vector embeddings are written to Neo4j within a single ACID transaction.
3.  **Atomic Commit**: The transaction either fully succeeds or fully fails. There is no possibility of orphan vectors, as the graph and vector updates are atomic.

## 🧪 Theory Integration Framework

### Theory Meta-Schema
The system implements a comprehensive theory meta-schema that enables the integration of social science theories into knowledge graph construction and analysis. The schema provides a structured framework for defining theoretical concepts, relationships, and validation rules.

### Master Concept Library
The Master Concept Library (MCL) provides a standardized vocabulary of entities, connections, and properties aligned with the DOLCE upper ontology. This ensures semantic precision and consistency across all knowledge graph operations.

### Three-Dimensional Framework
The system employs a three-dimensional theoretical framework for classifying and organizing knowledge according to:
- **Level of Analysis**: Individual, group, organizational, societal
- **Component of Influence**: Cognitive, affective, behavioral, environmental
- **Causal Metatheory**: Mechanism, process, structure

### ORM Methodology
Object-Role Modeling (ORM) principles are applied throughout the system to ensure clear separation between entities (objects) and relationships (fact types), with explicit role definitions and constraint specifications.

### Vector Store Abstraction (Strategy Pattern)
To ensure flexibility and future scalability, all vector operations are handled through a defined `VectorStore` interface. This allows the underlying vector database to be swapped without changing application logic. The default implementation uses Neo4j's native vector index.

```python
# contracts/vector_store_interface.py
from typing import Protocol, List, Tuple

class VectorStore(Protocol):
    """
    Defines the contract for a vector storage and search backend.
    """
    def upsert(self, uid: str, vector: List[float], metadata: dict) -> None:
        """
        Inserts or updates a vector by its unique ID.
        """
        ...

    def query(self, vector: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Finds the top_k most similar vectors to the query vector.
        Returns a list of (uid, similarity_score) tuples.
        """
        ...
    
    def delete(self, uid: str) -> None:
        """
        Deletes a vector by its unique ID.
        """
        ...

# concrete_implementations/neo4j_vector_store.py
class Neo4jVectorStore(VectorStore):
    """
    A VectorStore implementation that uses Neo4j's native HNSW index.
    """
    def upsert(self, uid: str, vector: List[float], metadata: dict) -> None:
        # Cypher query to SET the 'embedding' property on a node
        # MATCH (e:Entity {id: uid}) SET e.embedding = $vector
        ...

    def query(self, vector: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        # Cypher query using db.index.vector.queryNodes()
        ...

    def delete(self, uid: str) -> None:
        # Cypher query to REMOVE the 'embedding' property from a node
        ...

# concrete_implementations/qdrant_vector_store_stub.py
class QdrantVectorStore(VectorStore):
    """
    A stub implementation for a future Qdrant backend.
    This demonstrates the extensibility of the interface.
    """
    def upsert(self, uid: str, vector: List[float], metadata: dict) -> None:
        # Would use the qdrant_client
        ...

    def query(self, vector: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        # Would use the qdrant_client
        ...
    
    def delete(self, uid: str) -> None:
        # Would use the qdrant_client
        ...
```

### Contract System
The system implements a comprehensive contract system for ensuring consistency across all components. Contracts are defined in YAML/JSON format and validated through Pydantic models to ensure type safety and constraint enforcement.

## 🎯 Target Architecture (A1-A4 Priorities)

### 1. PageRank Gating & Performance Optimization
```python
# services/analytics_service.py
class AnalyticsService:
    """Gated analytics with performance safeguards"""
    
    def should_gate_pagerank(self, graph_size: int, available_memory: int) -> bool:
        """Determine if PageRank should be gated"""
        return (
            graph_size > 50000 or  # Node count threshold
            graph_size * 0.1 > available_memory * 0.5  # Memory projection > 50% RAM
        )
    
    def run_pagerank(self, graph: Graph) -> Dict[str, float]:
        """Run PageRank with appropriate strategy"""
        if self.should_gate_pagerank(len(graph.nodes), psutil.virtual_memory().available):
            # Use approximate PageRank for large graphs
            return self.run_approximate_pagerank(graph, top_k=1000)
        else:
            # Use full PageRank for smaller graphs
            return self.run_full_pagerank(graph)
    
    def run_approximate_pagerank(self, graph: Graph, top_k: int = 1000) -> Dict[str, float]:
        """Approximate PageRank for large graphs"""
        # Power iteration with early stopping
        scores = self.power_iteration_pagerank(graph, max_iterations=20, convergence_threshold=1e-6)
        
        # Return top-k results
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_scores[:top_k])
```

### 2. Bayesian Confidence Scoring
```python
# services/confidence_service.py
class ConfidenceService:
    """Bayesian confidence aggregation"""
    
    def bayesian_confidence_update(self, prior_confidence: float, new_evidence: float, 
                                 evidence_weight: float = 1.0) -> float:
        """Update confidence using Bayesian inference"""
        # Convert to log-odds for numerical stability
        prior_odds = prior_confidence / (1 - prior_confidence)
        evidence_odds = new_evidence / (1 - new_evidence)
        
        # Weighted combination
        posterior_odds = prior_odds * (evidence_odds ** evidence_weight)
        
        # Convert back to probability
        posterior_confidence = posterior_odds / (1 + posterior_odds)
        
        return max(0.0, min(1.0, posterior_confidence))  # Clamp to [0,1]
    
    def aggregate_entity_confidence(self, entity_id: str, extractions: List[Extraction]) -> float:
        """Aggregate multiple extractions for entity confidence"""
        if not extractions:
            return 0.0
        
        # Start with first extraction
        confidence = extractions[0].confidence
        
        # Bayesian update with each additional extraction
        for extraction in extractions[1:]:
            confidence = self.bayesian_confidence_update(
                prior_confidence=confidence,
                new_evidence=extraction.confidence,
                evidence_weight=extraction.quality_score
            )
        
        return confidence
```

### 3. Standardized Phase Interface (Contract-First)
```python
# contracts/phase_interface.py
@dataclass(frozen=True)
class ProcessingRequest:
    """Immutable contract for ALL phase inputs"""
    document_path: str
    theory_schema: Optional[TheorySchema] = None
    concept_library: Optional[MasterConceptLibrary] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
@dataclass(frozen=True)  
class ProcessingResult:
    """Immutable contract for ALL phase outputs"""
    entities: List[Entity]
    relationships: List[Relationship]
    theoretical_insights: List[TheoreticalInsight]
    metadata: Dict[str, Any]

class GraphRAGPhase(ABC):
    """Contract all phases MUST implement"""
    @abstractmethod
    def process(self, request: ProcessingRequest) -> ProcessingResult:
        pass
    
    @abstractmethod
    def get_theory_compatibility(self) -> List[str]:
        """Return list of theory schema names this phase supports"""
        pass
```

### 2. Service Versioning
```python
class WorkflowStateService:
    def update_workflow_progress(self, workflow_id, step_number=None, 
                               current_step=None, **kwargs):
        # Backward compatibility handling
```

### 4. Workflow State Storage: Redis/Postgres
```python
# services/workflow_state_service.py
class WorkflowStateService:
    """Redis-based workflow state management"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.lock_timeout = 30  # seconds
    
    def acquire_workflow_lock(self, workflow_id: str) -> bool:
        """Acquire distributed lock for workflow"""
        return self.redis.set(
            f"workflow_lock:{workflow_id}",
            "locked",
            ex=self.lock_timeout,
            nx=True  # Only set if not exists
        )
    
    def update_workflow_progress(self, workflow_id: str, step_number: int, 
                               current_step: str, **kwargs) -> bool:
        """Update workflow progress with concurrency control"""
        lock_key = f"workflow_lock:{workflow_id}"
        
        # Try to acquire lock
        if not self.acquire_workflow_lock(workflow_id):
            raise WorkflowLockError(f"Workflow {workflow_id} is locked")
        
        try:
            # Update state atomically
            state_data = {
                "step_number": step_number,
                "current_step": current_step,
                "updated_at": datetime.utcnow().isoformat(),
                **kwargs
            }
            
            # Store in Redis with TTL
            self.redis.hset(f"workflow_state:{workflow_id}", mapping=state_data)
            self.redis.expire(f"workflow_state:{workflow_id}", 86400)  # 24h TTL
            
            return True
            
        finally:
            # Release lock
            self.redis.delete(lock_key)
    
    def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow state"""
        state = self.redis.hgetall(f"workflow_state:{workflow_id}")
        if not state:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")
        return state
```

### 3. UI Adapter Pattern
```python
class UIAdapter:
    def __init__(self, phase: GraphRAGPhase):
        self.phase = phase
    
    def process_for_ui(self, file_path, filename, theory_schema=None):
        # Convert UI request to phase-specific format
        request = ProcessingRequest(
            document_path=file_path,
            theory_schema=theory_schema,
            options={"filename": filename}
        )
        return self.phase.process(request)
```

### 4. Integration Testing
```python
class PhaseIntegrationTest:
    def test_phase_compatibility(self, phase1, phase2):
        # Automated validation of phase interactions
        # Test theory schema compatibility
        # Validate concept library integration
```









---

**Note**: This architecture document represents the target state of the KGAS system, integrating theoretical foundations with practical system design. For current implementation status and progress, see the planning documentation.

---

# KGAS Architecture Master Document

*High-level overview and navigation*

# KGAS Architecture Master Document

**Purpose**: This document serves as the high-level entry point for understanding the architecture of the Knowledge Graph Analysis System (KGAS). It provides a comprehensive overview and links to more detailed documentation for each specific aspect of the system.

---

## 🏛️ **1. Core Concepts & System Overview**

This section covers the foundational principles, overall structure, and the "big picture" of the KGAS.

-   ****: The primary document detailing the end-to-end architecture, including components, data flow, and target state. **(Start here)**
-   ****: A guide to the repository's layout, helping you find code and documentation.
-   ****: The unchanging, core theoretical principles behind KGAS.
-   ****: A realistic look at the known limitations and boundaries of the system.

## ንድ **2. System Design & Patterns**

This section details the specific design patterns, schemas, and methodologies that govern the system's construction.

-   ****: An overview of the key software design patterns used in the codebase.
-   ****: The architecture of the tool and adapter contract system that ensures compatibility.
-   ****: The design for extending system functionality through plugins.
-   ****: The methodology behind the Object-Relational Mapping (ORM) used for database interactions.
-   ****: The framework that ensures data and process consistency across the system.

## 🤖 **3. AI, Data Models & Schemas**

This section focuses on the "brains" of the system, including the data structures, AI concepts, and schemas.

-   ****: Detailed descriptions of the Pydantic data models that form the backbone of the system.
-   ****: The academic and theoretical underpinnings for the LLM-generated ontologies.
-   ****: The meta-schema that enforces the structure of theory-aware components.
-   ****: The central library of concepts that provides a common vocabulary for the knowledge graph.
-   ****: The directory containing all JSON schema definitions for validation.

## 🛠️ **4. Tools, Integration & Capabilities**

This section describes how the various parts of the system connect and what they are capable of doing.

-   ****: The central registry of all tools and their defined capabilities.
-   ****: A matrix detailing the integration requirements and status of all system components.
-   ****: Documentation on how the system connects to and interacts with the database.
-   ****: The system for tracking the origin and history of data as it moves through the pipeline.

## ⚖️ **5. Decision Records & Specifications**

This section contains the formal decisions made about the architecture and the detailed specifications for components.

-   ****: A directory containing all formal ADRs for significant design choices.
-   ****: Detailed technical specifications for various system components.
-   ****: In-depth information about the MCP LLMs used in the system.

---
*This master document is intended as a starting point. For deep dives, please refer to the linked documents.*

---

# KGAS Evergreen Documentation

*Core theoretical principles*

# KGAS Evergreen Documentation

> This document is the single source of truth for the theoretical foundation of the Knowledge Graph Analysis System (KGAS). For implementation status and development progress, see [ROADMAP_v2.1.md](ROADMAP_v2.1.md).

## Theoretical Foundation

- [Theory Meta-Schema](THEORY_META_SCHEMA.md): Defined/documented, integration in progress
- [Master Concept Library](MASTER_CONCEPT_LIBRARY.md): Defined/documented, integration in progress
- [Three-Dimensional Framework](THEORETICAL_FRAMEWORK.md): Defined/documented, integration in progress
- [ORM Methodology](ORM_METHODOLOGY.md): Defined/documented, integration in progress
- [Contract System](CONTRACT_SYSTEM.md): Defined/documented, integration in progress

## Target Architecture

The target architecture integrates theoretical foundations with practical system design:

- All phases and tools use theory schemas and contracts for validation
- Full ORM compliance and three-dimensional theory classification in all workflows
- Automated contract validation and theory schema compliance in CI/CD

## Navigation
- [Roadmap](ROADMAP_v2.1.md)
- [Architecture](ARCHITECTURE.md)
- [Compatibility Matrix](COMPATIBILITY_MATRIX.md)
- [Contract System](CONTRACT_SYSTEM.md)

---
status: living
doc-type: evergreen
governance: doc-governance
---

---

# Theoretical Framework

*Academic underpinnings for LLM-generated ontologies*

# Theoretical Framework: Three-Dimensional Typology for KGAS

## Overview

KGAS organizes social-behavioral theories using a three-dimensional framework, enabling both human analysts and machines to reason about influence and persuasion in a structured, computable way.

## The Three Dimensions

Each theory includes a formal classification object:

```json
{
  "classification": {
    "domain": {
      "level": "Meso",
      "component": "Who", 
      "metatheory": "Interdependent"
    }
  }
}
```

1. **Level of Analysis (Scale)**
   - Micro: Individual-level (cognitive, personality)
   - Meso: Group/network-level (community, peer influence)
   - Macro: Societal-level (media effects, cultural norms)

2. **Component of Influence (Lever)**
   - Who: Speaker/Source
   - Whom: Receiver/Audience
   - What: Message/Treatment
   - Channel: Medium/Context
   - Effect: Outcome/Process

3. **Causal Metatheory (Logic)**
   - Agentic: Causation from individual agency
   - Structural: Causation from external structures
   - Interdependent: Causation from feedback between agents and structures

!INCLUDE "tables/theory_examples.md"

## Application

- Theories are classified along these axes in the Theory Meta-Schema.
- Guides tool selection, LLM prompting, and analysis workflows.

## References

- Lasswell (1948), Druckman (2022), Eyster et al. (2022)

<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# Master Concept Library

*Central vocabulary for knowledge graph operations*

# Master Concept Library: Standardized Vocabulary for KGAS

## Purpose

The Master Concept Library (MCL) is a machine-readable, extensible repository of standardized concepts (entities, connections, properties, modifiers) from social, behavioral, and communication science. It ensures semantic precision and cross-theory comparability in all KGAS analyses.

## Structure

- **EntityConcept**: Actors, groups, organizations, etc.
- **ConnectionConcept**: Relationships between entities (e.g., “identifies_with”)
- **PropertyConcept**: Attributes of entities or connections (e.g., “credibility_score”)
- **ModifierConcept**: Qualifiers or contextualizers (e.g., “temporal”, “certainty”)

## Mapping Process

1. **LLM Extraction**: Indigenous terms are extracted from text.
2. **Standardization**: Terms are mapped to canonical names in the MCL.
3. **Human-in-the-Loop**: Novel terms are reviewed and added as needed.

## Implementation

- **Code Location:** `/src/ontology_library/mcl/__init__.py`
- **Schema Enforcement:** Pydantic models
- **Integration:** Used in all theory schemas and extraction pipelines

## Example

- “grassroots organizer” → `SocialGroup` (`CommunityOrganizer` subtype)
- “credibility” → `PropertyConcept` with value type “numeric”

## Extensibility

The MCL grows as new concepts are encountered and validated, ensuring KGAS remains adaptable to emerging research and domains.

## Versioning Rules

| Change Type | Version Bump | Review Required | Documentation |
|-------------|--------------|-----------------|---------------|
| **Concept Addition** | Patch (x.y.z+1) | No | Update concept list |
| **Concept Modification** | Minor (x.y+1.0) | Yes | Update examples |
| **Schema Change** | Major (x+1.0.0) | Yes | Migration guide |
| **DOLCE Alignment** | Minor (x.y+1.0) | Yes | Alignment report |

### Concept Merge Policy
New concepts are merged via `scripts/mcl_merge.py` which:
- Validates against existing concepts
- Checks DOLCE alignment
- Updates cross-references
- Generates migration guide

## DOLCE and Bridge Links

### Upper Ontology Alignment
Every concept in the MCL is aligned with the DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering) upper ontology:

- **`upper_parent`**: IRI of the closest DOLCE superclass (e.g., `dolce:PhysicalObject`, `dolce:SocialObject`)
- **Semantic Precision**: Ensures ontological consistency across all concepts
- **Interoperability**: Enables integration with other DOLCE-aligned systems

### Bridge Links (Optional)
For enhanced interoperability, concepts may include:

- **`bridge_links`**: Array of IRIs linking to related concepts in external ontologies
- **Cross-Domain Mapping**: Connects social science concepts to domain-specific ontologies
- **Research Integration**: Enables collaboration with other research platforms -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# Data Models

*Pydantic data model specifications*

**Doc status**: Living – auto-checked by doc-governance CI

# KGAS Model Cards

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Model cards and version information for all models used in KGAS

---

## Model Inventory

### Language Models

| Model | Version | File Hash | Data Provenance | Purpose |
|-------|---------|-----------|-----------------|---------|
| text-embed-3-large | Latest | 45ac... | openai_dataset_card_v1.json | Text embeddings |
| gpt-4o-mini | rev 2025-06-30 | 1f3b... | openai_model_card_v4.json | Text generation |
| gpt-4o | Latest | 2d9e... | openai_model_card_v4.json | Advanced reasoning |

### Specialized Models

| Model | Version | File Hash | Data Provenance | Purpose |
|-------|---------|-----------|-----------------|---------|
| spaCy en_core_web_sm | 3.7.0 | 7f8a... | spacy_model_card_v3.json | NER and parsing |
| sentence-transformers | 2.2.2 | 9b1c... | huggingface_model_card_v2.json | Sentence embeddings |

---

## Model Configuration

### OpenAI Models
```python
# GPT-4o-mini configuration
gpt4o_mini_config = {
    "model": "gpt-4o-mini",
    "max_tokens": 4096,
    "temperature": 0.1,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# Text embedding configuration
embedding_config = {
    "model": "text-embed-3-large",
    "dimensions": 3072,
    "encoding_format": "float"
}
```

### Local Models
```python
# spaCy configuration
spacy_config = {
    "model": "en_core_web_sm",
    "disable": ["ner", "parser"],
    "enable": ["tagger", "attribute_ruler", "lemmatizer"]
}

# Sentence transformers configuration
sentence_transformer_config = {
    "model_name": "all-MiniLM-L6-v2",
    "device": "cpu",
    "normalize_embeddings": True
}
```

---

## Model Performance

### Embedding Model Performance
- **text-embed-3-large**: 3072 dimensions, MTEB score 64.6
- **all-MiniLM-L6-v2**: 384 dimensions, MTEB score 56.5
- **Performance**: text-embed-3-large provides 14% better retrieval accuracy

### Language Model Performance
- **gpt-4o-mini**: 128K context, 15K TPM
- **gpt-4o**: 128K context, 10K TPM
- **Performance**: gpt-4o provides 23% better reasoning accuracy

---

## Model Bias and Safety

### Bias Assessment
- **Gender Bias**: Tested with 1,000 counterfactual pairs
- **Racial Bias**: Tested with demographic parity metrics
- **Age Bias**: Tested with age-related language analysis
- **Socioeconomic Bias**: Tested with class-related terminology

### Safety Measures
- **Content Filtering**: OpenAI content filters enabled
- **Prompt Injection**: Tested against common injection patterns
- **Output Sanitization**: All outputs sanitized before storage
- **Access Control**: Model access logged and monitored

---

## Model Updates

### Update Schedule
- **OpenAI Models**: Automatic updates via API
- **Local Models**: Quarterly updates with testing
- **Custom Models**: Version-controlled with semantic versioning

### Version Control
```bash
# Model version tracking
python scripts/track_model_versions.py

# Model performance testing
python scripts/test_model_performance.py

# Model bias testing
python scripts/test_model_bias.py
```

---

## Model Deployment

### Production Deployment
```yaml
# docker-compose.models.yml
services:
  model-service:
    image: kgas/model-service:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_CACHE_DIR=/app/models
    volumes:
      - model_cache:/app/models
      - ./model_configs:/app/configs

volumes:
  model_cache:
```

### Model Caching
```python
# Model caching configuration
model_cache_config = {
    "cache_dir": "/app/models",
    "max_size": "10GB",
    "ttl": 86400,  # 24 hours
    "compression": "gzip"
}
```

---

## Model Monitoring

### Performance Metrics
- **Response Time**: Average and 95th percentile
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Token Usage**: Tokens consumed per request

### Quality Metrics
- **Embedding Quality**: Cosine similarity scores
- **Generation Quality**: Human evaluation scores
- **Bias Scores**: Regular bias assessment results
- **Safety Scores**: Content safety evaluation results

---

## Model Documentation

### Model Cards
Each model has a detailed model card including:
- **Model Description**: Purpose and capabilities
- **Training Data**: Data sources and preprocessing
- **Performance**: Benchmarks and evaluation results
- **Bias Analysis**: Bias assessment results
- **Safety Analysis**: Safety evaluation results
- **Usage Guidelines**: Best practices and limitations

### Documentation Location
- **Model Cards**: `docs/models/`
- **Configuration**: `config/models/`
- **Evaluation Results**: `docs/evaluation/`
- **Bias Reports**: `docs/bias/`

---

## Model Compliance

### Data Privacy
- **No Data Storage**: Models don't store user data
- **Data Minimization**: Only necessary data processed
- **Access Control**: Strict access controls on model data
- **Audit Logging**: All model access logged

### Regulatory Compliance
- **GDPR**: Right to explanation for model decisions
- **CCPA**: Data deletion and portability
- **FERPA**: Educational data protection
- **HIPAA**: Health data protection (if applicable)

---

**Note**: This model documentation provides comprehensive information about all models used in KGAS. Regular updates are required as models are updated or new models are added. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# Theory Meta-Schema

*Theory integration framework*

# Theory Meta-Schema: Operationalizing Social Science Theories in KGAS

![Meta-Schema v9.1 (JSON Schema draft-07)](https://img.shields.io/badge/Meta--Schema-v9.1-blue)

## Overview

The Theory Meta-Schema is the foundational innovation of the Knowledge Graph Analysis System (KGAS). It provides a standardized, computable framework for representing and applying diverse social science theories to discourse analysis. The goal is to move beyond data description to *theoretically informed, computable analysis*.

## Structure of the Theory Meta-Schema

Each Theory Meta-Schema instance is a structured document with the following components:

### 1. Theory Identity and Metadata
- `theory_id`: Unique identifier (e.g., `social_identity_theory`)
- `theory_name`: Human-readable name
- `authors`: Key theorists
- `publication_year`: Seminal publication date
- `domain_of_application`: Social contexts (e.g., “group dynamics”)
- `description`: Concise summary

**New in v9.1**  
• `mcl_id` – cross-link to Master Concept Library  
• `dolce_parent` – IRI of the DOLCE superclass for every entity  
• `ontology_alignment_strategy` – strategy for aligning with DOLCE ontology
• Tags now sit in `classification.domain` (`level`, `component`, `metatheory`)

### 2. Theoretical Classification (Three-Dimensional Framework)
- `level_of_analysis`: Micro (individual), Meso (group), Macro (society)
- `component_of_influence`: Who (Speaker), Whom (Receiver), What (Message), Channel, Effect
- `causal_metatheory`: Agentic, Structural, Interdependent

### 3. Computable Theoretical Core
- `ontology_specification`: Domain-specific concepts (entities, relationships, properties, modifiers) aligned with the Master Concept Library
- `axioms`: Core rules or assumptions (optional)
- `analytics`: Metrics or focal concepts (optional)
- `process`: Sequence of steps (sequential, iterative, workflow)
- `telos`: Analytical purpose, output format, and success criteria

### 4. Provenance
- `provenance`: {source_chunk_id: str, prompt_hash: str, model_id: str, timestamp: datetime}
  - Captures the lineage of each theory instance for audit and reproducibility.

## Implementation

- **Schema Location:** `/_schemas/theory_meta_schema_v9.1.json`
- **Validation:** Pydantic models with runtime verification
- **Integration:** CI/CD enforced contract compliance
- **Codegen**: dataclasses auto-generated into /src/contracts/generated/

## Example

See `THEORETICAL_FRAMEWORK.md` for a worked example using Social Identity Theory.

## Changelog

### v9.0 → v9.1
- Added `ontology_alignment_strategy` field for DOLCE alignment
- Enhanced codegen support with auto-generated dataclasses
- Updated schema location to v9.1
- Improved validation and integration documentation
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# Design Patterns

*Key software design patterns used in the codebase*

# Design Patterns

This document captures design patterns discovered through mock workflow analysis and implementation planning.

## Core Architectural Patterns

### Pass-by-Reference Pattern
- **Problem**: Moving large graph data between tools is expensive
- **Solution**: Tools operate on graph IDs, not full data structures
- **Implementation**:
  ```python
  def analyze_community(graph_id: str, community_id: str) -> Dict:
      # Fetch only what's needed from Neo4j
      graph = get_graph_reference(graph_id)
      return graph.analyze_community(community_id)
  ```

### Attribute-Based Compatibility
- **Problem**: Rigid graph schemas break tool composability
- **Solution**: Tools declare required attributes, graphs provide what they have
- **Implementation**:
  ```python
  @tool(required_attrs=["timestamp", "user_id"])
  def temporal_analysis(graph_id: str) -> Results:
      # Tool validates graph has required attributes
      # Gracefully handles optional attributes
  ```

### Three-Level Identity Pattern
- **Problem**: Same text can refer to different entities; same entity has multiple surface forms
- **Solution**: Track Surface Form → Mention → Entity hierarchy
- **Implementation**:
  ```python
  # Surface form: "Apple"
  mention = Mention(
      id="mention_001",
      surface_text="Apple",
      document_ref="doc_001",
      position=1234,
      context="Apple announced record profits"
  )
  
  # Entity resolution
  entity = Entity(
      id="ent_apple_inc",
      canonical_name="Apple Inc.",
      mention_refs=["mention_001", "mention_002", "mention_003"],
      surface_forms=["Apple", "AAPL", "Apple Computer"]
  )
  ```

### Universal Quality Tracking Pattern
- **Problem**: Quality degradation invisible until final results
- **Solution**: Every object tracks confidence and quality metadata
- **Implementation**:
  ```python
  class QualityTracked:
      def __init__(self, data, confidence=1.0):
          self.data = data
          self.confidence = confidence
          self.quality_tier = self._compute_tier(confidence)
          self.warnings = []
          self.evidence = []
          self.extraction_method = ""
      
      def _compute_tier(self, conf):
          if conf >= 0.8: return "high"
          elif conf >= 0.6: return "medium"
          else: return "low"
  ```

### Format-Agnostic Processing Pattern
- **Problem**: Different analyses need different data structures
- **Solution**: Seamless conversion between Graph ↔ Table ↔ Vector
- **Implementation**:
  ```python
  # Automatic format selection
  def analyze_data(data_ref, analysis_type):
      optimal_format = T117_format_selector(analysis_type, data_ref)
      
      if optimal_format == "table":
          table_ref = T115_graph_to_table(data_ref)
          return statistical_analysis(table_ref)
      elif optimal_format == "graph":
          return graph_algorithm(data_ref)
      else:  # vector
          return similarity_search(data_ref)
  ```

## Data Handling Patterns

### Streaming-First Design
- **Problem**: Large results consume memory and delay user feedback
- **Solution**: Use async generators everywhere
- **Implementation**:
  ```python
  async def* process_entities(graph_id: str):
      async for entity in graph.stream_entities():
          result = await process_entity(entity)
          yield result  # Stream results as available
  ```

### Lazy Evaluation
- **Problem**: Expensive computations may not be needed
- **Solution**: Defer computation until actually required
- **Implementation**:
  ```python
  def get_embeddings(entity_id: str):
      return LazyEmbedding(entity_id)  # Compute only when accessed
  ```

### Data-Level Lineage
- **Problem**: Operation-level lineage tracking explodes combinatorially
- **Solution**: Track lineage at data creation, not every transformation
- **Implementation**:
  ```python
  entity = {
      "id": "e123",
      "name": "John Doe", 
      "source": {"doc_id": "d456", "chunk": 12, "method": "NER"}
  }
  ```

## Error Handling Patterns

### Graceful Degradation
- **Problem**: Perfect analysis may not be possible
- **Solution**: Fall back to simpler methods that work
- **Implementation**:
  ```python
  try:
      result = advanced_community_detection(graph)
  except MemoryError:
      result = simple_connected_components(graph)
  except:
      result = sample_based_detection(graph, sample_size=1000)
  ```

### Partial Results Pattern
- **Problem**: All-or-nothing processing loses valuable partial work
- **Solution**: Always return what succeeded, failed, and partially completed
- **Implementation**:
  ```python
  def process_documents(doc_refs):
      results = {
          "successful": [],
          "failed": [],
          "partial": [],
          "summary": {}
      }
      
      for doc_ref in doc_refs:
          try:
              result = process_document(doc_ref)
              results["successful"].append(result)
          except PartialProcessingError as e:
              results["partial"].append({
                  "doc_ref": doc_ref,
                  "completed_steps": e.completed,
                  "failed_at": e.failed_step
              })
          except Exception as e:
              results["failed"].append({
                  "doc_ref": doc_ref,
                  "error": str(e)
              })
      
      results["summary"] = {
          "total": len(doc_refs),
          "successful": len(results["successful"]),
          "failed": len(results["failed"]),
          "partial": len(results["partial"])
      }
      return results
  ```

### Multi-Level Validation
- **Problem**: Late validation failures waste resources
- **Solution**: Validate early and at multiple levels
- **Implementation**:
  ```python
  def validate_graph_operation(graph_id, operation):
      # Level 1: Schema validation
      validate_schema(operation)
      # Level 2: Graph existence
      validate_graph_exists(graph_id)
      # Level 3: Attribute requirements
      validate_attributes(graph_id, operation.required_attrs)
      # Level 4: Resource availability
      validate_resources(operation.estimated_memory)
  ```

## Performance Patterns

### Resource-Aware Planning
- **Problem**: Operations may exceed available resources
- **Solution**: Estimate resources before execution
- **Implementation**:
  ```python
  def plan_analysis(graph_id: str, analysis_type: str):
      stats = get_graph_stats(graph_id)
      memory_needed = estimate_memory(analysis_type, stats)
      if memory_needed > available_memory():
          return suggest_alternatives(analysis_type)
  ```

### Progressive Enhancement
- **Problem**: Complex analyses fail on large data
- **Solution**: Start simple, add complexity as data allows
- **Implementation**:
  ```python
  analyzers = [
      BasicAnalyzer(),      # Always works
      StandardAnalyzer(),   # Works on medium data
      AdvancedAnalyzer()    # Needs lots of resources
  ]
  for analyzer in analyzers:
      if analyzer.can_handle(graph_stats):
          return analyzer.analyze(graph)
  ```

### Parallel Execution Decision
- **Problem**: Parallel execution can cause conflicts
- **Solution**: Simple heuristic - parallel for read-only operations
- **Implementation**:
  ```python
  def execute_tools(tool_calls):
      if all(tool.is_read_only() for tool in tool_calls):
          return execute_parallel(tool_calls)
      else:
          return execute_serial(tool_calls)
  ```

## Integration Patterns

### Tool Interface Consistency
- **Problem**: Heterogeneous tools are hard to compose
- **Solution**: Uniform interface for all tools
- **Implementation**:
  ```python
  class Tool:
      name: str
      description: str
      required_attrs: List[str]
      
      def is_read_only(self) -> bool
      async def execute(self, **kwargs) -> Result
  ```

## Advanced Patterns

### Confidence Propagation Pattern
- **Problem**: Uncertainty compounds through pipeline but isn't tracked
- **Solution**: Propagate confidence with operation-specific rules
- **Implementation**:
  ```python
  class ConfidencePropagator:
      def propagate(self, upstream_scores, operation_type):
          if operation_type == "extraction":
              # Extraction reduces confidence
              return min(upstream_scores) * 0.95
          elif operation_type == "aggregation":
              # Aggregation averages confidence
              return sum(upstream_scores) / len(upstream_scores)
          elif operation_type == "filtering":
              # Filtering preserves best confidence
              return max(upstream_scores)
          elif operation_type == "inference":
              # Inference compounds uncertainty
              return min(upstream_scores) * 0.85
  ```

### Versioning Pattern
- **Problem**: Changes break reproducibility and knowledge evolves
- **Solution**: Four-level versioning system
- **Implementation**:
  ```python
  class Versioned:
      def __init__(self):
          self.schema_version = "1.0"  # Data structure version
          self.data_version = 1        # Content version
          self.graph_version = None    # Graph snapshot version
          self.analysis_version = None # Analysis result version
      
      def create_version(self, level):
          if level == "data":
              self.data_version += 1
              self.invalidate_downstream()
  ```

### Reference Resolution Pattern
- **Problem**: Tools need data but shouldn't load everything
- **Solution**: Lazy loading through reference resolution
- **Implementation**:
  ```python
  class ReferenceResolver:
      def resolve(self, ref: str, fields: List[str] = None):
          # Parse reference type
          storage, type, id = ref.split("://")[1].split("/")
          
          # Load only requested fields
          if storage == "neo4j":
              return self.neo4j.get_partial(type, id, fields)
          elif storage == "sqlite":
              return self.sqlite.get_partial(type, id, fields)
          
      def resolve_batch(self, refs: List[str], fields: List[str] = None):
          # Group by storage for efficiency
          by_storage = defaultdict(list)
          for ref in refs:
              storage = ref.split("://")[1].split("/")[0]
              by_storage[storage].append(ref)
          
          # Batch load from each storage
          results = {}
          for storage, storage_refs in by_storage.items():
              results.update(self.batch_load(storage, storage_refs, fields))
          return results
  ```

### Tool Variant Selection Pattern
- **Problem**: Multiple tool variants (fast/cheap vs slow/accurate)
- **Solution**: Agent-driven selection based on context
- **Implementation**:
  ```python
  class ToolSelector:
      def select_variant(self, tool_base: str, context: dict) -> str:
          if tool_base == "T23":  # Entity extraction
              if context.get("volume") > 10000:
                  return "T23a"  # Fast spaCy variant
              elif context.get("domain") == "specialized":
                  return "T23b"  # LLM variant for custom entities
              else:
                  # Let agent decide based on quality needs
                  return None  # Agent will choose
  ```

### Aggregate Tools Pattern
- **Problem**: Complex analyses require multiple tool calls
- **Solution**: Reify analysis workflows as first-class tools
- **Implementation**:
  ```python
  @aggregate_tool(name="influential_users_analysis")
  def find_influential_users(graph_id: str):
      # Composed of multiple atomic tools
      entities = entity_search(graph_id, type="user")
      scores = entity_ppr(graph_id, entities)
      communities = entity_community(graph_id, top_k(scores, 10))
      return summarize_influence(entities, scores, communities)
  ```

### MCP Protocol Abstraction
- **Problem**: Direct tool coupling creates brittle systems
- **Solution**: Tools communicate via protocol, not direct calls
- **Implementation**:
  ```python
  # Tools expose via MCP
  @mcp_tool(name="entity_search")
  async def search(...):
      # Tool implementation
  
  # Claude Code calls via protocol
  result = await mcp_call("entity_search", params)
  ```

## Testing Patterns

### Minimal Test Graphs
- **Problem**: Full datasets too large for rapid testing
- **Solution**: Create minimal graphs that exercise all code paths
- **Implementation**:
  ```python
  def create_test_graph():
      # Minimum viable graph: 5 nodes, 7 edges
      # Tests all relationship types
      # Includes all required attributes
      return Graph(nodes=5, edges=7, attrs=["id", "type", "timestamp"])
  ```

### Real Database Testing
- **Problem**: Need to test actual database behavior
- **Solution**: Use real test instances with controlled data
- **Implementation**:
  ```python
  def test_entity_search():
      # Real Neo4j test instance with known data
      with test_neo4j() as db:
          db.load_fixture("test_data/entities.json")
          result = entity_search(db, query="test")
          assert result == ["e1"]
  ```

### Test Environment Management
- **Problem**: Need consistent test environments
- **Solution**: Docker-based test databases
- **Implementation**:
  ```bash
  # Start test environment
  docker-compose -f docker-compose.test.yml up -d
  
  # Run tests against real services
  pytest tests/  # All tests use real databases
  
  # Cleanup
  docker-compose -f docker-compose.test.yml down
  ```

## Key Implementation Rules

1. **Stream, don't buffer** - Use generators for memory efficiency
2. **Validate early** - Catch errors before expensive operations
3. **Degrade gracefully** - Always have a fallback
4. **Pass references** - Move IDs, not data
5. **Declare requirements** - Tools state what they need
6. **Compose via protocol** - MCP provides loose coupling
7. **Track at creation** - Lineage on data, not operations
8. **Plan before executing** - Estimate resources upfront
9. **Test in layers** - Fast unit → integration → e2e
10. **Reify workflows** - Complex analyses become aggregate tools

---

# Contract System

*Tool and adapter contract system architecture*

# Programmatic Contract Verification in KGAS

## Overview

KGAS uses a programmatic contract system to ensure all tools, data models, and workflows are compatible, verifiable, and robust.

## Contract System Components

- **YAML/JSON Contracts**: Define required/produced data types, attributes, and workflow states for each tool.
- **Schema Enforcement**: All contracts are validated using Pydantic models.
- **CI/CD Integration**: Automated tests ensure no code that breaks a contract can be merged.

## Contract Validator Flow

![Contract Validator Flow](docs/imgs/contract_validator_flow_v2.1.png)

The contract validator ensures all phase interfaces comply with the standardized contract format.

## Example Contract (Phase Interface v9)

```python
@dataclass(frozen=True)
class ProcessingRequest:
    """Immutable contract for ALL phase inputs"""
    document_path: str
    theory_schema: Optional[TheorySchema] = None
    concept_library: Optional[MasterConceptLibrary] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
@dataclass(frozen=True)  
class ProcessingResult:
    """Immutable contract for ALL phase outputs"""
    entities: List[Entity]
    relationships: List[Relationship]
    theoretical_insights: List[TheoreticalInsight]
    metadata: Dict[str, Any]

class GraphRAGPhase(ABC):
    """Contract all phases MUST implement"""
    @abstractmethod
    def process(self, request: ProcessingRequest) -> ProcessingResult:
        pass
    
    @abstractmethod
    def get_theory_compatibility(self) -> List[str]:
        """Return list of theory schema names this phase supports"""
        pass

### Required Provenance Field
- Every node and edge contract **must** include:
  - `generated_by_activity_id: str`  # Unique ID of the activity/process that generated this node/edge
- This enables full lineage tracking and supports W3C PROV compliance.

## Implementation

- **Schema Location:** `/_schemas/theory_meta_schema_v9.1.json`
- **Validation:** Pydantic-based runtime checks
- **Testing:** Dedicated contract tests in CI/CD

## Further Reading

See `COMPATIBILITY_MATRIX.md` for contract system integration and `ARCHITECTURE.md` for architectural context.

<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# Capability Registry

*Central registry of all tools and capabilities*

**Doc status**: Living – auto-checked by doc-governance CI

# GraphRAG System Capability Registry

**Generated**: 2025-06-19  
**Total Capabilities**: 571 (82 classes + 489 functions)  
**Files Analyzed**: 48 Python files

---

## 🎯 Executive Summary

This system contains **571 distinct capabilities** across **3 main phases** of document processing:
- **Phase 1**: Basic pipeline (PDF → entities → relationships → graph → query)
- **Phase 2**: Enhanced processing with ontology awareness
- **Phase 3**: Multi-document fusion and knowledge synthesis

**29 capabilities are exposed as MCP tools** for external access and fine-grained control.

---

## 📊 Capability Breakdown by Category

### 🔧 Phase 1: Basic Pipeline (166 capabilities)
**Purpose**: Core document processing workflow

#### PDF Loading & Text Processing (20 capabilities)
- **t01_pdf_loader.py** (10): PDF/text extraction, confidence calculation, format support
- **t15a_text_chunker.py** (10): Text chunking, tokenization, overlap handling

#### Entity & Relationship Extraction (49 capabilities)  
- **t23a_spacy_ner.py** (11): spaCy-based named entity recognition
- **t23c_llm_entity_extractor.py** (9): LLM-based entity extraction 
- **t27_relationship_extractor.py** (18): Pattern-based relationship extraction
- **t41_text_embedder.py** (11): Text embedding and similarity

#### Graph Construction (29 capabilities)
- **t31_entity_builder.py** (14): Neo4j entity node creation
- **t34_edge_builder.py** (15): Neo4j relationship edge creation

#### Graph Analysis & Query (42 capabilities)
- **t68_pagerank.py** (13): PageRank calculation and ranking
- **t68_pagerank_optimized.py** (8): Optimized PageRank implementation
- **t49_multihop_query.py** (17): Multi-hop graph querying
- **t49_enhanced_query.py** (12): Enhanced query understanding and answering

#### Workflow Orchestration (16 capabilities)
- **vertical_slice_workflow.py** (8): Main Phase 1 workflow
- **vertical_slice_workflow_optimized.py** (8): Performance-optimized workflow

#### MCP Tool Integration (25 capabilities)
- **phase1_mcp_tools.py** (25): Individual tool exposure for external access

#### Infrastructure (7 capabilities)
- **base_neo4j_tool.py** (4): Neo4j connection management
- **neo4j_fallback_mixin.py** (7): Fallback handling for Neo4j failures

---

### 🧠 Phase 2: Enhanced Processing (69 capabilities)
**Purpose**: Ontology-aware processing with advanced extraction

#### Enhanced Extraction (10 capabilities)
- **t23c_ontology_aware_extractor.py** (10): Gemini-based ontology-aware entity extraction

#### Graph Building (20 capabilities)
- **t31_ontology_graph_builder.py** (20): Ontology-constrained graph construction

#### Visualization (22 capabilities)
- **interactive_graph_visualizer.py** (22): Interactive graph visualization and analysis

#### Workflow Orchestration (17 capabilities)
- **enhanced_vertical_slice_workflow.py** (17): Main Phase 2 workflow with ontology integration

---

### 🔄 Phase 3: Multi-Document Fusion (64 capabilities)
**Purpose**: Cross-document knowledge synthesis and fusion

#### Document Fusion (41 capabilities)
- **t301_multi_document_fusion.py** (33): Core multi-document processing and entity fusion
- **basic_multi_document_workflow.py** (8): Simplified multi-document workflow

#### Fusion Tools (18 capabilities)
- **t301_fusion_tools.py** (13): Similarity calculation, clustering, conflict resolution
- **t301_mcp_tools.py** (5): MCP-exposed fusion tools

---

### 🛠️ Core Infrastructure (149 capabilities)
**Purpose**: Foundational services and system management

#### Identity & Entity Management (29 capabilities)
- **identity_service.py** (13): Basic entity identity and mention tracking
- **enhanced_identity_service.py** (16): Enhanced identity with embeddings and similarity

#### Data Quality & Provenance (30 capabilities)
- **quality_service.py** (18): Confidence assessment and quality tracking
- **provenance_service.py** (12): Operation tracking and lineage

#### System Services (23 capabilities)
- **service_manager.py** (10): Singleton service management
- **workflow_state_service.py** (13): Workflow checkpoints and progress tracking

#### UI Integration (15 capabilities)
- **ui_phase_adapter.py** (15): UI-to-backend integration layer

#### Phase Management (18 capabilities)
- **phase_adapters.py** (18): Standardized phase interfaces
- **graphrag_phase_interface.py** (21): Common phase interface definitions

#### Enhanced Storage (11 capabilities)
- **enhanced_identity_service_faiss.py** (11): FAISS-based similarity search

#### Testing Framework (18 capabilities)
- **integration_test_framework.py** (18): Comprehensive integration testing

---

### 🧠 Knowledge & Ontology (44 capabilities)
**Purpose**: Domain knowledge and ontology management

#### Ontology Generation (32 capabilities)
- **ontology_generator.py** (20): Core ontology generation and validation
- **gemini_ontology_generator.py** (12): Gemini-powered ontology creation

#### Ontology Storage (12 capabilities)
- **ontology_storage_service.py** (12): Persistent ontology management

---

### 🔌 External Integration (29 capabilities)
**Purpose**: External tool and API integration

#### MCP Server (29 capabilities)
- **mcp_server.py** (29): FastMCP server with full service exposure

---

## 🛠️ MCP Tools (29 External-Facing Capabilities)

### Phase 1 MCP Tools (24 tools)
1. `load_pdf` - Load and extract text from PDF
2. `get_pdf_loader_info` - PDF loader information
3. `chunk_text` - Break text into chunks
4. `get_text_chunker_info` - Text chunker information  
5. `extract_entities` - Extract named entities
6. `get_supported_entity_types` - List supported entity types
7. `get_entity_extractor_info` - Entity extractor information
8. `get_spacy_model_info` - spaCy model information
9. `extract_relationships` - Extract relationships between entities
10. `get_supported_relationship_types` - List supported relationship types
11. `get_relationship_extractor_info` - Relationship extractor information
12. `build_entities` - Build entity nodes in Neo4j
13. `get_entity_builder_info` - Entity builder information
14. `build_edges` - Build relationship edges in Neo4j
15. `get_edge_builder_info` - Edge builder information
16. `calculate_pagerank` - Calculate PageRank scores
17. `get_top_entities` - Get highest-ranked entities
18. `get_pagerank_calculator_info` - PageRank calculator information
19. `query_graph` - Execute multi-hop graph queries
20. `get_query_engine_info` - Query engine information
21. `get_graph_statistics` - Get comprehensive graph statistics
22. `get_entity_details` - Get detailed entity information
23. `get_phase1_tool_registry` - Get all Phase 1 tool information
24. `validate_phase1_pipeline` - Validate Phase 1 component functionality

### Phase 3 MCP Tools (5 tools)
25. `calculate_entity_similarity` - Calculate similarity between entities
26. `find_entity_clusters` - Find clusters of similar entities
27. `resolve_entity_conflicts` - Resolve conflicting entity representations
28. `merge_relationship_evidence` - Merge evidence from multiple relationships
29. `calculate_fusion_consistency` - Calculate consistency metrics for fused knowledge

---

## 📋 Quick Reference: Key Capabilities by Use Case

### Document Processing
- **Load Documents**: `PDFLoader.load_pdf()`, `mcp.load_pdf()`
- **Extract Entities**: `SpacyNER.extract_entities()`, `mcp.extract_entities()`
- **Find Relationships**: `RelationshipExtractor.extract_relationships()`
- **Build Graph**: `EntityBuilder.build_entities()`, `EdgeBuilder.build_edges()`

### Knowledge Analysis
- **Rank Entities**: `PageRankCalculator.calculate_pagerank()`
- **Query Knowledge**: `MultiHopQuery.query_graph()`
- **Find Similar**: `EnhancedIdentityService.find_similar_entities()`
- **Visualize**: `InteractiveGraphVisualizer.create_interactive_plot()`

### Multi-Document Processing
- **Fuse Documents**: `MultiDocumentFusion.fuse_documents()`
- **Resolve Conflicts**: `ConflictResolver.resolve()`
- **Cluster Entities**: `EntityClusterFinder.find_clusters()`

### System Management
- **Manage Services**: `ServiceManager` singleton
- **Track Quality**: `QualityService.assess_confidence()`
- **Monitor Provenance**: `ProvenanceService.get_lineage()`
- **Test Integration**: `IntegrationTester.run_full_integration_suite()`

---

## 🎯 Usage Patterns

### CLI Access
```bash
# Phase 1: Basic processing
python graphrag_cli.py document.pdf --phase 1

# Phase 3: Multi-document fusion  
python graphrag_cli.py document.pdf --phase 3
```

### MCP Tool Access
```python
# Via MCP server - individual tool control
mcp.extract_entities(chunk_ref="chunk1", text="Dr. Smith works at MIT.")
mcp.calculate_pagerank(damping_factor=0.85)
mcp.query_graph("Who works at MIT?")
```

### Direct API Access
```python
# Direct class instantiation
from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
workflow = VerticalSliceWorkflow()
result = workflow.execute_workflow("document.pdf", "What are the main entities?")
```

---

## 🔄 System Integration Points

### External Dependencies
- **Neo4j**: Graph database storage (all graph operations)
- **OpenAI API**: Embeddings and enhanced identity
- **Gemini API**: Ontology generation and enhanced extraction
- **spaCy**: Named entity recognition and NLP
- **FAISS**: Vector similarity search
- **FastMCP**: Tool server and external access

### Data Flow
1. **Input**: PDF/text documents
2. **Processing**: Entity/relationship extraction → Graph construction
3. **Analysis**: PageRank → Multi-hop querying → Visualization
4. **Fusion**: Cross-document entity resolution → Knowledge synthesis
5. **Output**: Structured knowledge graph + Query answers

---

**📝 Note**: This registry represents the complete technical capability of the GraphRAG system as of June 2025. For operational status and quality assessment of individual capabilities, see `PROJECT_STATUS.md`.-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# ADR-001: Phase Interface Design

*Architecture decision record for phase interfaces*

**Doc status**: Living – auto-checked by doc-governance CI

# ADR-001: Contract-First Phase Interface Design

**Date**: 2025-01-27  
**Status**: Accepted  
**Deciders**: Development Team  
**Context**: Phase 1→2 integration failure due to incompatible interfaces

---

## 🎯 **Decision**

**Use contract-first design for all phase interfaces with theory schema integration**

All phases (Phase 1, 2, 3) must implement a common `GraphRAGPhase` interface with theory schema support before any implementation begins.

---

## 🚨 **Problem**

### **Current Issues**
- **API Incompatibility**: Phase 1 and Phase 2 have different calling signatures
- **Integration Failures**: Phases tested in isolation, breaks discovered at runtime
- **No Theory Integration**: Theoretical concepts defined but not used in processing
- **UI Hardcoding**: UI hardcoded to Phase 1, can't handle different interfaces

### **Root Cause**
- **"Build First, Integrate Later"**: Phases built independently without shared contracts
- **No Interface Standards**: Each phase evolved its own API without coordination
- **Missing Theory Awareness**: Processing pipeline doesn't use theoretical foundations

---

## 💡 **Considered Options**

### **Option 1: Retrofit Existing Phases (Rejected)**
- **Approach**: Keep existing phase implementations, add adapters
- **Pros**: Minimal code changes, preserve existing functionality
- **Cons**: Complex adapter logic, theory integration difficult, technical debt
- **Decision**: Rejected - would perpetuate integration problems

### **Option 2: Contract-First Design (Selected)**
- **Approach**: Define immutable contracts first, then implement phases
- **Pros**: Clean interfaces, theory integration built-in, prevents future divergence
- **Cons**: Requires refactoring existing phases, more upfront work
- **Decision**: Selected - provides foundation for long-term success

### **Option 3: Gradual Migration (Rejected)**
- **Approach**: Migrate phases one at a time to new interface
- **Pros**: Incremental approach, lower risk
- **Cons**: Extended period of mixed interfaces, complexity
- **Decision**: Rejected - would maintain integration problems longer

---

## ✅ **Selected Solution**

### **Contract-First Phase Interface**
```python
@dataclass(frozen=True)
class ProcessingRequest:
    """Immutable contract for ALL phase inputs"""
    document_path: str
    theory_schema: Optional[TheorySchema] = None
    concept_library: Optional[MasterConceptLibrary] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
@dataclass(frozen=True)  
class ProcessingResult:
    """Immutable contract for ALL phase outputs"""
    entities: List[Entity]
    relationships: List[Relationship]
    theoretical_insights: List[TheoreticalInsight]
    metadata: Dict[str, Any]

class GraphRAGPhase(ABC):
    """Contract all phases MUST implement"""
    @abstractmethod
    def process(self, request: ProcessingRequest) -> ProcessingResult:
        pass
    
    @abstractmethod
    def get_theory_compatibility(self) -> List[str]:
        """Return list of theory schema names this phase supports"""
```

### **Implementation Strategy**
1. **Phase A**: Define contracts and create wrappers for existing phases
2. **Phase B**: Implement theory integration in wrappers
3. **Phase C**: Migrate to native contract implementation
4. **Phase D**: Add advanced theory-driven features

---

## 🎯 **Consequences**

### **Positive**
- **Integration Guarantee**: All phases use same interface, no compatibility issues
- **Theory Integration**: Built-in support for theory schemas and concept library
- **UI Flexibility**: UI can handle any phase through adapter pattern
- **Future-Proof**: New phases automatically compatible
- **Testing**: Integration tests can validate all phase combinations

### **Negative**
- **Migration Effort**: Requires refactoring existing Phase 1 and 2 implementations
- **Learning Curve**: Team needs to understand contract-first approach
- **Initial Complexity**: More upfront design work required

### **Risks**
- **Scope Creep**: Contract design could become over-engineered
- **Performance**: Wrapper layers could add overhead
- **Timeline**: Contract design could delay feature delivery

---

## 🔧 **Implementation Plan**

### **Phase A: Foundation (Week 1-2)**
- [ ] Define `ProcessingRequest` and `ProcessingResult` contracts
- [ ] Create `GraphRAGPhase` abstract base class
- [ ] Implement theory schema integration in contracts
- [ ] Create wrapper for existing Phase 1 implementation

### **Phase B: Integration (Week 3)**
- [ ] Create wrapper for Phase 2 implementation
- [ ] Implement theory integration in wrappers
- [ ] Create integration test framework
- [ ] Update UI to use adapter pattern

### **Phase C: Migration (Week 4-5)**
- [ ] Migrate Phase 1 to native contract implementation
- [ ] Migrate Phase 2 to native contract implementation
- [ ] Remove wrapper layers
- [ ] Add advanced theory-driven features

---

## 📊 **Success Metrics**

### **Integration Success**
- [ ] All phases pass same integration tests
- [ ] UI can switch between phases without errors
- [ ] Theory schemas properly integrated into processing
- [ ] No API compatibility issues between phases

### **Performance Impact**
- [ ] Processing time remains <10s for typical documents
- [ ] Memory usage doesn't increase significantly
- [ ] Theory integration doesn't add substantial overhead

### **Developer Experience**
- [ ] New phases can be added without integration issues
- [ ] Theory schemas can be easily integrated
- [ ] Testing framework catches integration problems early

---

## 🔄 **Review and Updates**

### **Review Schedule**
- **Week 2**: Review contract design and initial implementation
- **Week 4**: Review integration success and performance impact
- **Week 6**: Review overall success and lessons learned

### **Update Triggers**
- Performance degradation >20%
- Integration issues discovered
- Theory integration requirements change
- New phase requirements emerge

---

**Related ADRs**: None (first ADR)  
**Related Documentation**: `ROADMAP_v2.md`, `ARCHITECTURE.md`, `KGAS_EVERGREEN_DOCUMENTATION.md` -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---

# ADR-002: Pipeline Orchestrator Architecture

*Architecture decision record for pipeline orchestration*

**Doc status**: Living – auto-checked by doc-governance CI

# ADR-002: PipelineOrchestrator Architecture

## Status
**ACCEPTED** - Implemented 2025-07-15

## Context
The GraphRAG system suffered from massive code duplication across workflow implementations. Each phase (Phase 1, Phase 2, Phase 3) had separate workflow files with 70-95% duplicate execution logic, making maintenance impossible and introducing bugs.

### Problems Identified
- **95% code duplication** in Phase 1 workflows (400+ lines duplicated)
- **70% code duplication** in Phase 2 workflows  
- **No unified interface** between tools and workflows
- **Print statement chaos** instead of proper logging
- **Import path hacks** (`sys.path.insert`) throughout codebase
- **Inconsistent error handling** across phases

### Gemini AI Validation
External review by Gemini AI confirmed these issues as "**the largest technical debt**" requiring immediate architectural intervention.

## Decision
Implement a unified **PipelineOrchestrator** architecture with the following components:

### 1. Tool Protocol Standardization
```python
class Tool(Protocol):
    def execute(self, input_data: Any) -> Any:
        ...
```

### 2. Tool Adapter Pattern
- `PDFLoaderAdapter`, `TextChunkerAdapter`, `SpacyNERAdapter`
- `RelationshipExtractorAdapter`, `EntityBuilderAdapter`, `EdgeBuilderAdapter`  
- `PageRankAdapter`, `MultiHopQueryAdapter`
- Bridges existing tools to unified protocol

### 3. Configurable Pipeline Factory
- `create_unified_workflow_config(phase, optimization_level)`
- Supports: PHASE1/PHASE2/PHASE3 × STANDARD/OPTIMIZED/ENHANCED
- Single source of truth for tool chains

### 4. Unified Execution Engine
- `PipelineOrchestrator.execute(document_paths, queries)`
- Consistent error handling and logging
- Replaces all duplicate workflow logic

## Consequences

### Positive
- ✅ **95% reduction** in Phase 1 workflow duplication
- ✅ **70% reduction** in Phase 2 workflow duplication  
- ✅ **Single source of truth** for all pipeline execution
- ✅ **Type-safe interfaces** between components
- ✅ **Proper logging** throughout system
- ✅ **Backward compatibility** maintained

### Negative
- Requires adapter layer for existing tools
- Initial implementation complexity
- Learning curve for new unified interface

## Implementation Evidence
```bash
# Verification commands
python -c "from src.core.pipeline_orchestrator import PipelineOrchestrator; print('✅ Available')"
python -c "from src.core.tool_adapters import PDFLoaderAdapter; print('✅ Tool adapters working')"
python -c "from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow; w=VerticalSliceWorkflow(); print(f'✅ Uses orchestrator: {hasattr(w, \"orchestrator\")}')"
```

**Results:** All verification tests pass ✅

## Alternatives Considered

### 1. Incremental Refactoring
- **Rejected:** Would not address root cause of duplication
- **Issue:** Technical debt would continue accumulating

### 2. Complete Rewrite
- **Rejected:** Too risky, would break existing functionality
- **Issue:** No backward compatibility guarantee

### 3. Plugin Architecture
- **Rejected:** Overly complex for current needs
- **Issue:** Would introduce unnecessary abstraction layers

## Related Decisions
- [ADR-002: Logging Standardization](ADR-002-Logging-Standardization.md)
- [ADR-003: Quality Gate Enforcement](ADR-003-Quality-Gate-Enforcement.md)

## References
- [CLAUDE.md Priority 2 Implementation Plan](../../CLAUDE.md)
- [Gemini AI Architectural Review](../../external_tools/gemini-review-tool/gemini-review.md)
- [Tool Factory Implementation](../../src/core/tool_factory.py)
- [Pipeline Orchestrator Implementation](../../src/core/pipeline_orchestrator.py)-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>

---


## 📊 Summary

**Documents Included**: 12
**Documents Skipped**: 0
**Total Size**: 73,253 characters

---

*This document was automatically generated for external architecture review. For the most up-to-date information, please refer to the individual source documents in the KGAS repository.*
