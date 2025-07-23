**Doc status**: Living – auto-checked by doc-governance CI

# ADR-001: Contract-First Tool Interface Design

**Date**: 2025-01-27  
**Status**: Partially Implemented - 10 tools use legacy interfaces, 9 tools have unified interface, contract-first design remains architectural goal  
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

## 💡 **Trade-off Analysis**

### Options Considered

#### Option 1: Keep Status Quo (Tool-Specific Interfaces)
- **Pros**:
  - No migration effort required
  - Tools remain independent and specialized
  - Developers familiar with existing patterns
  - Quick to add new tools without constraints
  
- **Cons**:
  - Integration complexity grows exponentially with tool count
  - Agent orchestration requires complex adapter logic
  - No consistent error handling or confidence tracking
  - Theory integration would require per-tool implementation
  - Testing each tool combination separately

#### Option 2: Retrofit with Adapters
- **Pros**:
  - Preserve existing tool implementations
  - Gradual migration possible
  - Lower initial development effort
  - Can maintain backward compatibility
  
- **Cons**:
  - Adapter layer adds performance overhead
  - Theory integration still difficult
  - Two patterns to maintain (native + adapted)
  - Technical debt accumulates
  - Doesn't solve root cause of integration issues

#### Option 3: Contract-First Design [SELECTED]
- **Pros**:
  - Clean, consistent interfaces across all tools
  - Theory integration built into contract
  - Enables intelligent agent orchestration
  - Simplified testing and validation
  - Future tools automatically compatible
  - Cross-modal analysis becomes straightforward
  
- **Cons**:
  - Significant refactoring of existing tools
  - Higher upfront design effort
  - Team learning curve for new patterns
  - Risk of over-engineering contracts

#### Option 4: Microservice Architecture
- **Pros**:
  - Tools completely decoupled
  - Independent scaling and deployment
  - Technology agnostic (tools in any language)
  - Industry-standard pattern
  
- **Cons**:
  - Massive complexity increase for research platform
  - Network overhead for local processing
  - Distributed system challenges
  - Overkill for single-user academic use case

### Decision Rationale

Contract-First Design (Option 3) was selected because:

1. **Agent Enablement**: Standardized interfaces are essential for intelligent agent orchestration of tool workflows.

2. **Theory Integration**: Built-in support for theory schemas ensures consistent application of domain knowledge.

3. **Cross-Modal Requirements**: Consistent interfaces enable seamless conversion between graph, table, and vector representations.

4. **Research Quality**: Standardized confidence scoring and provenance tracking improve research reproducibility.

5. **Long-term Maintenance**: While initial effort is higher, the reduced integration complexity pays dividends over time.

6. **Testing Efficiency**: Integration tests can validate tool combinations systematically rather than ad-hoc.

### When to Reconsider

This decision should be revisited if:
- Moving from research platform to production service
- Need to integrate external tools not under our control
- Performance overhead of contracts exceeds 10%
- Team size grows beyond 5 developers
- Requirements shift from batch to real-time processing

The contract abstraction provides flexibility to evolve the implementation while maintaining interface stability.

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

## Implementation Status

This ADR describes the **target tool interface design** - the intended contract-first architecture. For current tool interface implementation status and migration progress, see:

- **[Roadmap Overview](../../roadmap/ROADMAP_OVERVIEW.md)** - Current tool interface status and unified tool completion
- **[Phase TDD Progress](../../roadmap/phases/phase-tdd/tdd-implementation-progress.md)** - Active tool interface migration progress
- **[Tool Implementation Evidence](../../roadmap/phases/phase-1-implementation-evidence.md)** - Completed unified interface implementations

**Related ADRs**: None (first ADR)  
**Related Documentation**: `ARCHITECTURE_OVERVIEW.md`, `contract-system.md`

*This ADR contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*
