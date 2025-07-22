**Doc status**: Living – auto-checked by doc-governance CI

# ADR-001: Contract-First Tool Interface Design

**Date**: 2025-01-27  
**Status**: Superseded by MVRT Architecture - Updated 2025-01-20  
**Deciders**: Development Team  
**Context**: Tool integration failures due to incompatible interfaces

---

## 🎯 **Decision**

**Use contract-first design for all tool interfaces with theory schema integration**

All tools must implement standardized contracts with theory schema support to enable agent-orchestrated workflows and cross-modal analysis.

---

## 🚨 **Problem**

### **Current Issues**
- **API Incompatibility**: Tools have different calling signatures and return formats
- **Integration Failures**: Tools tested in isolation, breaks discovered at agent runtime
- **No Theory Integration**: Theoretical concepts defined but not consistently used in processing
- **Agent Complexity**: Agent needs complex logic to handle different tool interfaces

### **Root Cause**
- **"Build First, Integrate Later"**: Tools built independently without shared contracts
- **No Interface Standards**: Each tool evolved its own API without coordination
- **Missing Theory Awareness**: Processing pipeline doesn't consistently use theoretical foundations

---

## 💡 **Considered Options**

### **Option 1: Retrofit Existing Tools (Rejected)**
- **Approach**: Keep existing tool implementations, add adapters
- **Pros**: Minimal code changes, preserve existing functionality
- **Cons**: Complex adapter logic, theory integration difficult, technical debt
- **Decision**: Rejected - would perpetuate integration problems

### **Option 2: Contract-First Design (Selected)**
- **Approach**: Define standardized tool contracts first, then implement/migrate tools
- **Pros**: Clean interfaces, theory integration built-in, agent orchestration enabled
- **Cons**: Requires refactoring existing tools, more upfront work
- **Decision**: Selected - enables agent-based workflows and cross-modal analysis

### **Option 3: Gradual Migration (Rejected)**
- **Approach**: Migrate tools one at a time to new interface
- **Pros**: Incremental approach, lower risk
- **Cons**: Extended period of mixed interfaces, complexity
- **Decision**: Rejected - would maintain integration problems longer

---

## ✅ **Selected Solution**

### **Contract-First Tool Interface**
```python
@dataclass(frozen=True)
class ToolRequest:
    """Immutable contract for ALL tool inputs"""
    input_data: Any
    theory_schema: Optional[TheorySchema] = None
    concept_library: Optional[MasterConceptLibrary] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
@dataclass(frozen=True)  
class ToolResult:
    """Immutable contract for ALL tool outputs"""
    status: Literal["success", "error"]
    data: Any
    confidence: ConfidenceScore  # From ADR-004
    metadata: Dict[str, Any]
    provenance: ProvenanceRecord

class KGASTool(ABC):
    """Contract all tools MUST implement"""
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        pass
    
    @abstractmethod
    def get_theory_compatibility(self) -> List[str]:
        """Return list of theory schema names this tool supports"""
        
    @abstractmethod 
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for expected input_data format"""
        
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return JSON schema for returned data format"""
```

### **Implementation Strategy**
1. **Phase A**: Define tool contracts and create wrappers for existing tools
2. **Phase B**: Implement theory integration and confidence scoring (ADR-004)
3. **Phase C**: Migrate tools to native contract implementation
4. **Phase D**: Enable agent orchestration and cross-modal workflows

---

## 🎯 **Consequences**

### **Positive**
- **Agent Integration**: Standardized interfaces enable intelligent agent orchestration
- **Theory Integration**: Built-in support for theory schemas and concept library
- **Cross-Modal Analysis**: Consistent interfaces enable seamless format conversion
- **Future-Proof**: New tools automatically compatible with agent workflows
- **Testing**: Integration tests can validate tool combinations
- **Confidence Tracking**: Standardized confidence scoring (ADR-004) for research quality

### **Negative**
- **Migration Effort**: Requires refactoring existing tool implementations
- **Learning Curve**: Team needs to understand contract-first approach
- **Initial Complexity**: More upfront design work required

### **Risks**
- **Scope Creep**: Contract design could become over-engineered
- **Performance**: Wrapper layers could add overhead
- **Timeline**: Contract design could delay MVRT delivery

---

## 🔧 **Implementation Plan**

### **UPDATED: Aligned with MVRT Roadmap**

### **Phase A: Tool Contracts (Days 1-3)**
- [ ] Define `ToolRequest` and `ToolResult` contracts  
- [ ] Create `KGASTool` abstract base class
- [ ] Implement `ConfidenceScore` integration (ADR-004)
- [ ] Create wrappers for existing MVRT tools (~20 tools)

### **Phase B: Agent Integration (Days 4-7)**
- [ ] Implement theory schema integration in tool contracts
- [ ] Create agent orchestration layer using standardized interfaces
- [ ] Implement cross-modal conversion using consistent tool contracts
- [ ] Create integration test framework for agent workflows

### **Phase C: Native Implementation (Days 8-14)**
- [ ] Migrate priority MVRT tools to native contract implementation
- [ ] Remove wrapper layers for performance
- [ ] Implement multi-layer UI using standardized tool interfaces
- [ ] Validate agent workflow with native tool implementations

---

## 📊 **Success Metrics**

### **Integration Success**
- [ ] All tools pass standardized integration tests
- [ ] Agent can orchestrate workflows without interface errors
- [ ] Theory schemas properly integrated into all tool processing
- [ ] Cross-modal conversions work seamlessly through tool contracts

### **Performance Impact**
- Performance targets are defined and tracked in `docs/planning/performance-targets.md`.
- The contract-first approach is not expected to introduce significant overhead.

### **Developer Experience**
- [ ] New tools can be added without integration issues
- [ ] Theory schemas can be easily integrated into any tool
- [ ] Agent can automatically discover and use new tools
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
