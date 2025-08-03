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
- **Error Handling Contracts**: Standardized error response formats and recovery guidance per [ADR-014](../adrs/ADR-014-Error-Handling-Strategy.md).
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

## Error Handling Contract Requirements

All KGAS tools and services must implement standardized error handling contracts that support academic research requirements for transparency and debuggability:

### Standard Error Response Format
```python
@dataclass
class StandardErrorResponse:
    """Required error response format for all KGAS components"""
    status: Literal["error"]
    error_code: str  # Standardized error classification
    error_message: str  # Human-readable error description
    operation: str  # Specific operation that failed
    context: Dict[str, Any]  # Complete error context
    recovery_guidance: List[str]  # Specific recovery instructions
    debug_info: Dict[str, Any]  # Technical debugging information
    timestamp: str  # ISO format timestamp
    
    # Optional fields for research workflows
    tool_id: Optional[str] = None
    system_state: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None  # In debug mode only
```

### Error Classification System
All errors must be classified using standardized error types:

- **`validation_error`**: Input validation failures, schema violations
- **`processing_error`**: Core operation failures, computation errors
- **`resource_error`**: Memory, disk, or CPU constraint violations
- **`integration_error`**: Database, service, or external API failures
- **`configuration_error`**: Setup, configuration, or environment issues
- **`data_error`**: Input data quality or format problems

### Recovery Guidance Requirements
Every error response must include specific, actionable recovery guidance:

```python
# Example recovery guidance for different error types
RECOVERY_GUIDANCE = {
    "validation_error": [
        "Check input data format matches expected schema",
        "Verify required fields are present and correctly typed",
        "Review tool documentation for input requirements"
    ],
    "resource_error": [
        "Check available memory and disk space",
        "Reduce processing batch size",
        "Close other applications to free resources",
        "Consider processing documents in smaller groups"
    ],
    "integration_error": [
        "Verify database services are running (Neo4j)",
        "Check database connectivity and credentials",
        "Review service logs for connection issues",
        "Restart database services if necessary"
    ]
}
```

### Fail-Fast Error Handling Requirements
All KGAS components must implement fail-fast error handling:

1. **Immediate Error Exposure**: Problems surface immediately rather than being masked
2. **Complete Failure**: System fails entirely on critical errors rather than degrading
3. **No Silent Failures**: All processing failures must be explicitly reported
4. **Academic Transparency**: Complete error information provided for research debugging

### Tool Contract Error Integration
All tool contracts must extend the base tool interface with error handling:

```python
class BaseTool(ABC):
    """Base contract all KGAS tools must implement"""
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool operation with comprehensive error handling"""
        pass
    
    def _create_error_result(
        self, 
        error_type: str, 
        error: Exception, 
        operation: str, 
        context: Dict
    ) -> ToolResult:
        """Create standardized error result for academic research"""
        return ToolResult(
            status="error",
            error_code=error_type,
            error_message=str(error),
            metadata={
                "operation": operation,
                "context": context,
                "recovery_guidance": self._generate_recovery_guidance(error_type),
                "debug_info": self._extract_debug_info(error),
                "timestamp": datetime.now().isoformat(),
                "tool_id": self.tool_id
            }
        )
```

### Academic Research Error Requirements
Error handling must specifically support academic research workflows:

- **Research Integrity**: Prevent corrupted data from propagating through analysis
- **Debugging Capability**: Provide complete technical information for issue resolution  
- **Workflow Recovery**: Enable researchers to resume work after resolving errors
- **Audit Trail**: Log all errors for research reproducibility and validation

## Implementation

- **Schema Location:** `/_schemas/theory_meta_schema_v13.json`
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
