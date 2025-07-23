---
status: living
doc-type: contract-system
governance: doc-governance
---

# Programmatic Contract Verification in KGAS

## Overview

KGAS uses a programmatic contract system to ensure all tools, data models, and workflows are compatible, verifiable, and robust.

## Contract System Components

- **YAML/JSON Contracts**: Define required/produced data types, attributes, and workflow states for each tool.
- **Schema Enforcement**: All contracts are validated using Pydantic models.
- **Confidence Score Ontology**: All confidence/uncertainty fields **MUST** conform to the comprehensive uncertainty metrics framework defined in [ADR-007](../adrs/adr-004-uncertainty-metrics.md) (which supersedes the original ADR-004).
- **CI/CD Integration**: Automated tests ensure no code that breaks a contract can be merged.

## Contract Validator Flow

![Contract Validator Flow](docs/imgs/contract_validator_flow_v2.1.png)

The contract validator ensures all phase interfaces comply with the standardized contract format.

## Example Contract (Phase Interface v10)

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

- **Schema Location:** `/_schemas/theory_meta_schema_v10.json`
- **Validation:** Pydantic-based runtime checks
- **Testing:** Dedicated contract tests in CI/CD

## Further Reading

See `docs/architecture/COMPATIBILITY_MATRIX.md` for contract system integration and `docs/architecture/ARCHITECTURE.md` for architectural context.

<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>

## 📚 Navigation
- [KGAS Evergreen Documentation](KGAS_EVERGREEN_DOCUMENTATION.md)
- [Roadmap](ROADMAP_v2.1.md)
- [Compatibility Matrix](COMPATIBILITY_MATRIX.md)
- [Architecture](ARCHITECTURE.md)

---
