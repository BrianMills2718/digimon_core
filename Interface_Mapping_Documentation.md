# Interface Mapping Documentation

**Date**: 2025-08-05  
**Purpose**: Map current tool interfaces to guide contract-first migration

## Overview

The KGAS codebase currently has **three distinct tool interface hierarchies**:

1. **BaseTool** (from `base_tool.py` and `base_tool_fixed.py`)
2. **Tool Protocol** (from `src/core/tool_protocol.py`) 
3. **KGASTool** (from `src/core/tool_contract.py`)

## Current Tool Distribution

### Tools Using BaseTool (~50+ tools)

Most unified tools inherit from `BaseTool`:

```python
# Pattern found in most tools:
class T##ToolNameUnified(BaseTool):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
```

**Examples**:
- T01PDFLoaderUnified
- T31EntityBuilderUnified  
- T34EdgeBuilderUnified
- T68PageRankCalculatorUnified
- All phase1 unified tools
- Most phase2 unified tools

### Tools Using Tool Protocol (Orchestrator Interface)

The orchestrator (`sequential_engine.py`) expects tools implementing:

```python
class Tool(ABC):
    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult
    def get_tool_info(self) -> Dict[str, Any]
```

**Key difference**: Has optional `context` parameter in execute method.

### Tools Using KGASTool (Target Contract-First Design)

Currently **no tools directly implement KGASTool**, but it's the target interface:

```python
class KGASTool(ABC):
    def execute(self, request: ToolRequest) -> ToolResult
    def validate_input(self, input_data: Any) -> ToolValidationResult  
    def get_theory_compatibility(self) -> List[str]
    def get_input_schema(self) -> Dict[str, Any]
    def get_output_schema(self) -> Dict[str, Any]
```

## Interface Comparison

| Feature | BaseTool | Tool Protocol | KGASTool |
|---------|----------|---------------|----------|
| Execute Input | Dict[str, Any] | Dict + context | ToolRequest |
| Execute Output | Dict[str, Any] | Dict[str, Any] | ToolResult |
| Validation Result | Custom | ToolValidationResult | ToolValidationResult |
| Theory Support | No | No | Yes |
| Schema Definition | Optional | No | Required |
| Provenance | Manual | No | Built-in |
| Confidence Scoring | Manual | No | Built-in |

## Key Incompatibilities

### 1. Validation Result Attributes
- Tool Protocol expects: `validation_result.validation_errors`
- KGASTool provides: `validation_result.errors`

### 2. Execute Method Signatures
```python
# BaseTool & most tools:
execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]

# Tool Protocol (orchestrator expects):
execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]

# KGASTool (target design):
execute(self, request: ToolRequest) -> ToolResult
```

### 3. Data Flow
- Current: Orchestrator passes raw dicts between tools
- Target: Structured ToolRequest/ToolResult objects

## Migration Categories

### Category A: Simple Loaders (15 tools)
Tools that load files and return structured data.
- **Current**: BaseTool with dict input/output
- **Migration**: Straightforward - wrap dict in ToolRequest
- **Examples**: T01-T14 loaders

### Category B: Processing Tools (10 tools)
Tools that transform data (chunking, embedding).
- **Current**: BaseTool with specific input requirements
- **Migration**: Need schema definition
- **Examples**: T15A (chunker), T15B (embedder)

### Category C: Neo4j Tools (8 tools)
Tools that interact with Neo4j database.
- **Current**: BaseTool with Neo4j dependencies
- **Migration**: Complex - need service integration
- **Examples**: T31, T34, T49, T68

### Category D: Analysis Tools (20+ tools)
Phase 2/3 tools for graph analysis.
- **Current**: Mix of BaseTool and custom interfaces
- **Migration**: Varied complexity
- **Examples**: T50-T60 analysis tools

### Category E: Extraction Tools (5 tools)
NLP/LLM-based extraction tools.
- **Current**: Complex custom interfaces
- **Migration**: High complexity - LLM integration
- **Examples**: T23A, T23C, T27

## Service Dependencies

Tools rely on services that may not match expected interfaces:

| Service | Expected Methods | Actual Methods | Status |
|---------|-----------------|----------------|---------|
| ProvenanceService | create_tool_execution_record | Unknown | ❌ Needs verification |
| IdentityService | create_mention, resolve_entity | Unknown | ❌ Needs verification |
| QualityService | calculate_confidence | Unknown | ❌ Needs verification |

## Recommended Migration Order

### Phase 1: Foundation (Week 1)
1. Fix validation attribute mismatch
2. Document service APIs
3. Create orchestrator bridge
4. Test with one simple loader (T03TextLoader)

### Phase 2: Simple Tools (Week 2)
- Migrate all Category A loaders
- These have minimal dependencies
- Good for establishing patterns

### Phase 3: Processing Tools (Week 3)
- Migrate Category B tools
- Define schemas for each
- Test data flow between tools

### Phase 4: Complex Tools (Weeks 4-6)
- Migrate Categories C, D, E
- Handle service dependencies
- Theory integration for applicable tools

## Migration Checklist per Tool

- [ ] Inherit from KGASTool instead of BaseTool
- [ ] Change execute signature to use ToolRequest/ToolResult
- [ ] Define input/output schemas
- [ ] Implement theory compatibility (if applicable)
- [ ] Add proper confidence scoring
- [ ] Integrate with provenance service
- [ ] Update tests for new interface
- [ ] Remove field adapter dependencies
- [ ] Document migration changes

## Success Metrics

1. **Interface Compliance**: Tool passes KGASTool interface checks
2. **Schema Validation**: Input/output schemas properly defined
3. **Service Integration**: All service calls use correct APIs
4. **Test Coverage**: Tool has contract-based tests
5. **Documentation**: Tool interface documented

## Next Steps

1. **Immediate**: Fix validation attribute mismatch in tool_contract.py
2. **Short-term**: Create service API documentation
3. **Medium-term**: Build orchestrator bridge for testing
4. **Long-term**: Systematic tool migration following this mapping