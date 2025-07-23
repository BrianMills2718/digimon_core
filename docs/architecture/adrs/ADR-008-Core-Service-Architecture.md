# ADR-008: Core Service Architecture

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: System requires coordinated services for identity management, provenance tracking, quality assessment, and workflow state management.

## Decision

We will implement a **Service Manager pattern** with dependency injection to coordinate four core services:

1. **IdentityService (T107)**: Entity mention management and resolution
2. **ProvenanceService (T110)**: Operation tracking and lineage  
3. **QualityService (T111)**: Confidence assessment and propagation
4. **WorkflowStateService (T121)**: Workflow checkpoints and recovery

```python
class ServiceManager:
    """Singleton service coordinator with dependency injection"""
    
    @property
    def identity_service(self) -> IdentityService:
        return self._get_service('identity', IdentityService)
    
    @property
    def provenance_service(self) -> ProvenanceService:
        return self._get_service('provenance', ProvenanceService)
```

## Rationale

### **Why Service Manager Pattern?**

**1. Academic Research Complexity**: Research workflows require coordinated services that must maintain consistency across entity resolution, provenance tracking, and quality assessment.

**2. Cross-Service Dependencies**: 
- Identity service needs provenance for entity tracking
- Quality service needs provenance for confidence history
- Workflow state needs all services for checkpoint recovery

**3. Configuration Management**: Single point for service configuration and lifecycle management.

**4. Testing Isolation**: Services can be individually tested while maintaining integration capabilities.

### **Why These Four Services?**

**Identity Service**: Academic research requires consistent entity resolution across documents. Without this, "John Smith" in document A and "J. Smith" in document B may be treated as different entities, corrupting analysis.

**Provenance Service**: Academic integrity demands complete audit trails. Every extracted fact must be traceable to its source for citation verification and reproducibility.

**Quality Service**: Research requires confidence assessment that propagates through analysis pipelines. Quality degradation must be tracked to maintain result validity.

**Workflow State Service**: Long-running research workflows need checkpointing and recovery. Academic projects often process hundreds of documents over days/weeks.

## Alternatives Considered

### **1. Monolithic Service Architecture**
- **Rejected**: Creates tight coupling, difficult testing, and massive service complexity
- **Problem**: Single service would handle identity, provenance, quality, and state - violating separation of concerns

### **2. Direct Service Instantiation (No Manager)**
- **Rejected**: Creates circular dependencies and configuration fragmentation
- **Problem**: Each component would need to instantiate its own service dependencies

### **3. Event-Driven Service Architecture**
- **Rejected**: Over-engineering for academic research tool requirements
- **Problem**: Adds complexity without matching the academic workflow patterns

### **4. Microservices Architecture**
- **Rejected**: Academic research tools need local, single-node execution
- **Problem**: Network boundaries incompatible with local research environment

## Consequences

### **Positive**
- **Consistent Service Access**: All components access services through same interface
- **Dependency Injection**: Services can be mocked/replaced for testing
- **Configuration Centralization**: Single point for service configuration
- **Resource Management**: Controlled service lifecycle and cleanup

### **Negative**
- **Singleton Complexity**: Service manager must handle thread safety
- **Service Interdependencies**: Changes to one service may affect others
- **Initialization Ordering**: Services must be initialized in correct dependency order

## Implementation Requirements

### **Service Protocol Compliance**
All services must implement the standard `CoreService` interface:

```python
class CoreService(ABC):
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> ServiceResponse:
        pass
    
    @abstractmethod
    def health_check(self) -> ServiceResponse:
        pass
    
    @abstractmethod
    def cleanup(self) -> ServiceResponse:
        pass
```

### **Thread Safety**
Service manager must be thread-safe using proper locking mechanisms for concurrent access.

### **Error Handling**
Service failures must propagate clearly with recovery guidance rather than silent degradation.

### **Configuration Integration**
Services must integrate with the centralized configuration system (ADR-009 dependency).

## Validation Criteria

- [ ] All four core services implement `CoreService` interface
- [ ] Service manager provides thread-safe singleton access
- [ ] Service dependencies are properly injected
- [ ] Service health checks work independently and collectively
- [ ] Service cleanup prevents resource leaks
- [ ] Error propagation works correctly across service boundaries

## Related ADRs

- **ADR-009**: Bi-Store Database Strategy (services use both Neo4j and SQLite)
- **ADR-010**: Quality System Design (quality service implementation details)
- **ADR-014**: Error Handling Strategy (service error propagation)

This service architecture provides the foundation for coordinated, reliable academic research capabilities while maintaining the simplicity appropriate for single-node research environments.