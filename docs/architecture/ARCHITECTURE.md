---
**Document Type**: Architecture  
**Purpose**: Define the target/final architecture for the KGAS system  
**Status**: Living  
**Governance**: doc-governance  
---

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



## 📚 Navigation
- [KGAS Evergreen Documentation](KGAS_EVERGREEN_DOCUMENTATION.md)
- [Roadmap](ROADMAP_v2.1.md)
- [Compatibility Matrix](COMPATIBILITY_MATRIX.md)
- [Contract System](CONTRACT_SYSTEM.md)
