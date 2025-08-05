# Contract-First Implementation: Uncertainty Analysis

**Date**: 2025-08-05  
**Status**: Analysis Complete

## Key Uncertainties Identified

### 1. **Multiple Competing Interfaces**

The codebase has **THREE different tool interface definitions**:

1. **`src/core/tool_protocol.py`** (What orchestrator expects):
   - `Tool` ABC with `execute(input_data: Dict, context: Optional[Dict])`
   - `ToolValidationResult` with `validation_errors` attribute
   - Currently used by sequential_engine

2. **`src/core/tool_contract.py`** (ADR-001 contract-first design):
   - `KGASTool` ABC with `execute(request: ToolRequest) -> ToolResult`
   - `ToolValidationResult` with `errors` attribute (not `validation_errors`)
   - Theory-aware, confidence scoring, provenance tracking

3. **Various `base_tool.py` files** (Legacy implementations):
   - Different ToolRequest/ToolResult definitions
   - Inconsistent interfaces across tools

### 2. **Interface Mismatch Details**

```python
# Orchestrator expects (from tool_protocol.py):
tool.execute(input_data: Dict[str, Any], context: Optional[Dict])
validation_result.validation_errors  # List[str]

# Contract-first design has (from tool_contract.py):
tool.execute(request: ToolRequest) -> ToolResult
validation_result.errors  # List[str] (different attribute name!)
```

### 3. **Data Flow Mismatch**

- Orchestrator passes raw dictionaries between tools
- Tools expect structured ToolRequest objects
- Field adapters are currently bridging this gap (bad practice)

### 4. **Service API Evolution**

- ProvenanceService doesn't have `create_tool_execution_record` method
- Tools expect different service interfaces than what exists
- No clear API documentation for services

## Root Cause Analysis

The core issue is that **the orchestrator was built against `tool_protocol.py` while the contract-first design in `tool_contract.py` was developed separately**. They represent two different evolutionary paths:

1. **Path A**: Simple Tool protocol → Orchestrator implementation
2. **Path B**: Contract-first KGASTool → Theory integration

These paths never converged, creating the current split-brain situation.

## Methodical Approach to Resolution

### Phase 1: Documentation First (Recommended) ✅

**Why**: Clear documentation prevents further divergence and guides implementation.

1. **Document Current State**:
   - Map which tools use which interface
   - Document service API contracts
   - Identify all interface touchpoints

2. **Define Target State**:
   - Single unified interface (KGASTool)
   - Clear migration path
   - Deprecation timeline

3. **Create Migration Guide**:
   - Step-by-step tool conversion
   - Orchestrator update plan
   - Testing requirements

### Phase 2: Minimal Working Example

**Goal**: Prove the contract-first design works end-to-end

1. **Create Bridge Orchestrator**:
   - Wraps existing orchestrator
   - Converts Dict → ToolRequest
   - Handles ToolResult → Dict

2. **Migrate One Tool Completely**:
   - Remove all adapters
   - Implement KGASTool directly
   - Full contract compliance

3. **Test End-to-End**:
   - Single tool pipeline
   - Verify all contracts
   - Document issues

### Phase 3: Systematic Migration

**Based on documentation and proven example**:

1. **Update Orchestrator**:
   - Support both interfaces temporarily
   - Deprecation warnings for old interface
   - Full ToolRequest/ToolResult support

2. **Migrate Tools in Batches**:
   - Group by similarity
   - Test each batch
   - Update documentation

3. **Remove Legacy Code**:
   - Delete old interfaces
   - Remove field adapters
   - Clean up duplicates

## Specific Decisions Needed

### 1. **Which Interface Wins?**

**Recommendation**: `tool_contract.py` (KGASTool) should be the target because:
- Aligns with ADR-001 and ADR-028
- Supports theory integration
- Has proper contracts for AI orchestration
- More future-proof design

### 2. **How to Handle Orchestrator?**

**Options**:
- A) Modify existing orchestrator to support both interfaces
- B) Create new contract-first orchestrator
- C) Use adapter pattern at orchestrator level

**Recommendation**: Option A with deprecation path

### 3. **Service API Standardization?**

**Recommendation**: 
- Document existing service APIs first
- Add missing methods as needed
- Version service interfaces

## Immediate Next Steps

1. **Create Interface Mapping** (30 min):
   ```bash
   # Find all tools and their interfaces
   grep -r "class.*Tool.*:" src/tools/
   grep -r "def execute" src/tools/
   ```

2. **Document Service APIs** (1 hour):
   - ProvenanceService actual methods
   - IdentityService actual methods
   - Expected vs actual interfaces

3. **Fix Validation Attribute** (15 min):
   - Standardize on `errors` not `validation_errors`
   - Or add property for compatibility

4. **Create Minimal Bridge** (2 hours):
   - Simple orchestrator wrapper
   - Dict ↔ ToolRequest conversion
   - Test with one tool

## Risk Assessment

### High Risk
- Breaking existing pipelines during migration
- Service API incompatibilities
- Hidden dependencies on field adapters

### Medium Risk
- Performance impact from additional abstraction
- Learning curve for developers
- Incomplete tool migrations

### Low Risk
- Documentation becoming outdated
- Temporary code duplication
- Test coverage gaps

## Success Metrics

1. **Short Term** (1 week):
   - One tool fully migrated to KGASTool
   - Orchestrator supports both interfaces
   - Documentation complete

2. **Medium Term** (1 month):
   - 50% tools migrated
   - Field adapters deprecated
   - New tools use KGASTool only

3. **Long Term** (3 months):
   - All tools on KGASTool interface
   - Legacy interfaces removed
   - Clean architecture achieved

## Conclusion

The path forward is clear but requires careful execution:

1. **Document first** to prevent further divergence
2. **Prove the concept** with minimal example
3. **Migrate systematically** with backward compatibility
4. **Clean up completely** once migration done

The contract-first design (KGASTool) is the correct target architecture. The challenge is migrating from the current split-brain state without breaking existing functionality.