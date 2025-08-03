# ADR-028: Tool Interface Layer Architecture

**Status**: Accepted  
**Date**: 2025-07-29  
**Supersedes**: Clarifies [ADR-001](ADR-001-Phase-Interface-Design.md), [ADR-002](ADR-002-Pipeline-Orchestrator-Architecture.md), [ADR-013](ADR-013-MCP-Protocol-Integration.md)  
**Context**: Resolves architectural confusion between three different tool interface approaches by defining them as complementary layers

## Problem

The KGAS architecture contains three tool interface approaches that appeared to be incompatible:

1. **ADR-001**: Contract-first tool interface design with `ToolRequest`/`ToolResult`
2. **ADR-002**: Tool adapter pattern for existing tools with `Tool` Protocol
3. **ADR-013**: MCP Protocol integration for external API access

This created confusion about which interface to use when implementing new tools, leading to:
- **Development paralysis**: Developers unsure which pattern to follow
- **Inconsistent implementations**: Tools using different interface patterns
- **Integration complexity**: No clear precedence rules between approaches
- **Architectural drift**: Each approach evolving independently

## Decision

**We adopt a three-layer tool interface architecture** where each ADR defines a specific layer with clear responsibilities and usage patterns:

```
┌─────────────────────────────────────────────────────────┐
│            Layer 3: External API Access                │
│                  (ADR-013: MCP Protocol)                │
│  ┌─────────────────────────────────────────────────┐    │
│  │  @app.tool()                                    │    │
│  │  def extract_entities(text: str) -> Dict:       │    │
│  │      # JSON interface for AI orchestration      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │ wraps
┌─────────────────────▼───────────────────────────────────┐
│           Layer 2: Internal Contract                   │
│            (ADR-001: Contract-First Design)            │
│  ┌─────────────────────────────────────────────────┐    │
│  │  class T23aSpacyNERUnified(KGASTool):          │    │
│  │      def execute(self, request: ToolRequest)    │    │
│  │          -> ToolResult:                         │    │
│  │          # Theory integration, confidence       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │ implemented by
┌─────────────────────▼───────────────────────────────────┐
│          Layer 1: Tool Implementation                  │
│           (ADR-002: Adapter Pattern)                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │  # New tools: Direct implementation             │    │
│  │  class SpacyNERTool: ...                       │    │
│  │                                                 │    │
│  │  # Legacy tools: Adapter pattern               │    │
│  │  class SpacyNERAdapter(Tool): ...              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Layer Definitions

#### **Layer 1: Tool Implementation**
- **Purpose**: Raw tool logic and legacy tool adaptation
- **Scope**: Actual processing algorithms and data transformations
- **Patterns**: 
  - New tools: Direct implementation of core logic
  - Legacy tools: ADR-002 adapter pattern with `Tool` Protocol

#### **Layer 2: Internal Contract** 
- **Purpose**: Standardized internal interfaces with theory integration
- **Scope**: KGAS internal services, agent orchestration, cross-modal analysis
- **Pattern**: ADR-001 contract-first design with `ToolRequest`/`ToolResult`
- **Features**: Theory schema integration, confidence scoring, provenance tracking

#### **Layer 3: External API Access**
- **Purpose**: External system integration and AI orchestration
- **Scope**: Claude integration, external MCP clients, cross-language compatibility
- **Pattern**: ADR-013 MCP Protocol with JSON interfaces
- **Features**: Type-safe external APIs, documentation, AI tool composition

## Architecture Rules

### **Interface Precedence**
1. **New tools**: Implement Layer 2 (`KGASTool`) directly
2. **Legacy tools**: Use Layer 1 + ADR-002 adapter → Layer 2 contract
3. **External access**: Always through Layer 3 MCP interface
4. **Internal orchestration**: Use Layer 2 contracts exclusively
5. **AI integration**: Use Layer 3 for Claude/LLM orchestration

### **Data Flow Patterns**
```python
# Pattern 1: New Tool Implementation
class NewAnalysisTool(KGASTool):  # Layer 2 directly
    def execute(self, request: ToolRequest) -> ToolResult:
        # Direct implementation with theory integration
        pass

# Pattern 2: Legacy Tool Integration  
class LegacyTool:  # Layer 1: Existing logic
    def process(self, data): pass

class LegacyToolAdapter(Tool):  # Layer 1→2: ADR-002 adapter
    def execute(self, input_data): 
        return self.legacy_tool.process(input_data)

class LegacyToolUnified(KGASTool):  # Layer 2: Contract wrapper
    def execute(self, request: ToolRequest) -> ToolResult:
        adapter = LegacyToolAdapter()
        result = adapter.execute(request.input_data)
        return ToolResult(...)  # Add confidence, provenance

# Pattern 3: External Access
@app.tool()  # Layer 3: MCP exposure
def analyze_data(data: Dict) -> Dict:
    tool = NewAnalysisTool(service_manager)
    request = ToolRequest(input_data=data)
    result = tool.execute(request)
    return result.data if result.status == "success" else {"error": result.error}
```

### **Interface Boundaries**
- **Layer 1↔2**: Python objects, can be type-complex
- **Layer 2↔3**: JSON serializable only, type-safe with schemas
- **Cross-layer**: No direct Layer 1↔3 communication (must go through Layer 2)

## Implementation Strategy

### **Phase 1: Documentation Clarification**
- [x] Create ADR-028 defining layer architecture
- [ ] Update ADR-001, ADR-002, ADR-013 with layer context
- [ ] Update architecture documentation with layer diagrams

### **Phase 2: Tool Migration Assessment**
```bash
# Assess current tool implementations
find src/ -name "*.py" -exec grep -l "class.*Tool" {} \;
# Categorize into: Direct Layer 2, Needs Adapter, Legacy Only
```

### **Phase 3: Implementation Standards**
- [ ] Create tool implementation templates for each pattern
- [ ] Update developer documentation with layer guidelines
- [ ] Create automated tests validating layer compliance

### **Phase 4: Validation**
- [ ] Verify all tools accessible through appropriate layers
- [ ] Test AI orchestration through Layer 3 MCP
- [ ] Validate internal service integration through Layer 2

## Benefits of Layered Architecture

### **Clarity and Maintainability**
- **Clear purpose**: Each layer has specific, non-overlapping responsibilities
- **Migration path**: Legacy tools can be modernized layer-by-layer
- **Interface stability**: Changes in one layer don't affect others
- **Testing boundaries**: Each layer can be tested independently

### **Flexibility and Evolution**
- **Technology independence**: Layer 1 can use any implementation approach
- **API evolution**: Layer 3 can evolve external interfaces without breaking internal logic
- **Theory integration**: Layer 2 provides consistent theory schema support
- **AI orchestration**: Layer 3 enables advanced AI workflow composition

### **Integration Benefits**
- **Internal consistency**: All internal services use Layer 2 contracts
- **External accessibility**: All tools available via Layer 3 MCP
- **Cross-modal support**: Layer 2 enables seamless format conversion
- **Provenance tracking**: Built into Layer 2 for research reproducibility

## Consequences

### **Positive**
- **Eliminates confusion**: Clear guidelines for when to use each interface
- **Preserves existing work**: All three ADRs remain valid and valuable
- **Enables evolution**: Tools can be modernized incrementally
- **Improves integration**: Clear boundaries reduce integration complexity
- **Supports AI workflows**: Layer 3 enables sophisticated AI orchestration

### **Negative**
- **Complexity**: Three layers require understanding multiple patterns
- **Abstraction overhead**: Multiple layers can impact performance slightly
- **Documentation burden**: Need to maintain layer-specific documentation
- **Learning curve**: Developers need to understand appropriate layer usage

### **Risks and Mitigations**
- **Risk**: Over-abstraction leading to unnecessary complexity
  - **Mitigation**: Use direct Layer 2 implementation for new tools when possible
- **Risk**: Performance impact from multiple layers
  - **Mitigation**: Profile and optimize layer transitions if needed
- **Risk**: Developer confusion about layer boundaries
  - **Mitigation**: Clear documentation and implementation templates

## Tool Implementation Guide

### **Decision Tree for New Tools**
```
New Tool Development:
├─ Is this a completely new tool?
│  └─ YES: Implement KGASTool (Layer 2) directly
└─ NO: Is there existing logic to wrap?
   ├─ Legacy Python tool?
   │  └─ Create ADR-002 adapter → KGASTool wrapper
   └─ External service integration?
      └─ Create service client → KGASTool wrapper

External Access Needed?
├─ YES: Add MCP @app.tool() wrapper (Layer 3)
└─ NO: Layer 2 interface sufficient

AI Orchestration Required?
├─ YES: Must expose via Layer 3 MCP
└─ NO: Internal Layer 2 usage only
```

### **Code Templates**

#### **Template 1: New Tool (Direct Layer 2)**
```python
class T###_NewTool(KGASTool):
    """New tool implementing Layer 2 directly"""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T###"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        try:
            # Core processing logic here
            result_data = self._process(request.input_data)
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=self._calculate_confidence(result_data),
                metadata={"tool_version": "1.0"},
                provenance=self._create_provenance(request)
            )
        except Exception as e:
            return ToolResult(
                status="error",
                error=str(e),
                confidence=0.0,
                metadata={},
                provenance=self._create_provenance(request)
            )
    
    def _process(self, input_data: Dict) -> Any:
        # Implement core logic
        pass
```

#### **Template 2: Legacy Tool Integration**
```python
# Layer 1: Existing tool (don't modify)
class ExistingLegacyTool:
    def analyze(self, data): 
        return {"results": "legacy_output"}

# Layer 1→2: ADR-002 Adapter
class LegacyToolAdapter(Tool):
    def __init__(self):
        self.legacy_tool = ExistingLegacyTool()
    
    def execute(self, input_data: Any) -> Any:
        return self.legacy_tool.analyze(input_data)

# Layer 2: Contract Interface
class T###_LegacyToolUnified(KGASTool):
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.adapter = LegacyToolAdapter()
        self.tool_id = "T###"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        try:
            raw_result = self.adapter.execute(request.input_data)
            
            return ToolResult(
                status="success",
                data=raw_result,
                confidence=self._estimate_confidence(raw_result),
                metadata={"legacy_tool": True},
                provenance=self._create_provenance(request)
            )
        except Exception as e:
            return ToolResult(
                status="error",
                error=str(e),
                confidence=0.0,
                metadata={},
                provenance=self._create_provenance(request)
            )
```

#### **Template 3: MCP External Access (Layer 3)**
```python
@app.tool()
def tool_external_interface(
    input_param: str,
    options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Tool description for external users and AI systems"""
    
    service_manager = ServiceManager()
    tool = T###_ToolImplementation(service_manager)
    
    request = ToolRequest(
        tool_id="T###",
        input_data={"input_param": input_param, "options": options or {}},
        operation="execute"
    )
    
    result = tool.execute(request)
    
    if result.status == "success":
        return {
            "success": True,
            "data": result.data,
            "confidence": result.confidence,
            "metadata": result.metadata
        }
    else:
        return {
            "success": False,
            "error": result.error,
            "error_type": "processing_error",
            "recovery_guidance": "Check input parameters and retry"
        }
```

## Validation Criteria

### **Architecture Compliance**
- [ ] All new tools implement Layer 2 KGASTool interface
- [ ] Legacy tools use ADR-002 adapters correctly
- [ ] External access exclusively through Layer 3 MCP
- [ ] No direct Layer 1→3 communication bypassing Layer 2

### **Integration Success**
- [ ] All tools work correctly through internal Layer 2 orchestration
- [ ] MCP tools can be composed by AI systems (Claude)
- [ ] Cross-modal analysis works seamlessly across all tool types
- [ ] Theory schema integration functions correctly for all Layer 2 tools

### **Developer Experience**
- [ ] Clear decision tree guides tool implementation choices
- [ ] Code templates reduce development time and errors
- [ ] Documentation enables understanding of layer boundaries
- [ ] Automated tests validate layer compliance

## Related ADRs

- **[ADR-001](ADR-001-Phase-Interface-Design.md)**: Defines Layer 2 Internal Contract interface
- **[ADR-002](ADR-002-Pipeline-Orchestrator-Architecture.md)**: Provides Layer 1→2 adapter pattern for legacy tools
- **[ADR-013](ADR-013-MCP-Protocol-Integration.md)**: Defines Layer 3 External API via MCP Protocol
- **[ADR-008](ADR-008-Core-Service-Architecture.md)**: Core services that integrate with Layer 2 tools
- **[ADR-011](ADR-011-Academic-Research-Focus.md)**: Academic requirements that inform layer design

## Future Evolution

### **Layer Enhancement Opportunities**
- **Layer 1**: Could support additional implementation languages or frameworks
- **Layer 2**: May add advanced theory integration features or enhanced provenance
- **Layer 3**: Could expand to additional API protocols beyond MCP

### **Architecture Stability**
- **Layer boundaries**: Expected to remain stable as core architectural principle
- **Interface contracts**: May evolve with backward compatibility requirements
- **Implementation details**: Can be optimized and enhanced within each layer

This layered architecture transforms the apparent tool interface confusion into a clear, purposeful design that supports both current needs and future evolution while preserving all existing architectural investments.