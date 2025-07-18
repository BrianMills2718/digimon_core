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
