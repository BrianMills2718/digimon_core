# Contract-First Implementation: Methodical Action Plan

**Date**: 2025-08-05  
**Status**: Ready for Implementation

## Executive Summary

The KGAS codebase has two competing tool interface designs:
1. **Current Reality**: Tools use `Tool` protocol expected by orchestrator
2. **Target Architecture**: Contract-first `KGASTool` design from ADR-001

We need a methodical migration without breaking existing functionality.

## Phase 1: Quick Fixes (Day 1)

### 1.1 Fix Validation Attribute Mismatch (30 min)

**Problem**: Orchestrator expects `validation_errors`, KGASTool has `errors`

**Solution**: Add property to ToolValidationResult in tool_contract.py
```python
@property
def validation_errors(self) -> List[str]:
    """Compatibility property for orchestrator"""
    return self.errors
```

### 1.2 Add Service Adapter Methods (1 hour)

**Problem**: Tools expect methods that don't exist in services

**Solution**: Add compatibility methods to services
- ProvenanceService: Add `create_tool_execution_record`
- IdentityService: Add `resolve_entity`

### 1.3 Create Minimal Test (1 hour)

**Goal**: Prove one tool works end-to-end with contract-first design

**Steps**:
1. Pick simplest tool (T03TextLoader)
2. Implement KGASTool interface
3. Test with orchestrator using adapter
4. Document issues found

## Phase 2: Documentation Update (Day 2)

### 2.1 Update Architecture Documentation

**Files to Update**:
- `/docs/architecture/CLAUDE.md` - Add interface migration notes
- `/docs/architecture/adrs/ADR-001-Phase-Interface-Design.md` - Add implementation status
- `/docs/architecture/adrs/ADR-028-Tool-Interface-Layer-Architecture.md` - Add current state

**Content**:
- Current state vs target state
- Migration in progress
- Temporary compatibility measures

### 2.2 Create Migration Guide

**New File**: `/docs/architecture/TOOL_MIGRATION_GUIDE.md`

**Contents**:
1. Step-by-step tool conversion process
2. Common pitfalls and solutions
3. Testing requirements
4. Examples from pilot migrations

## Phase 3: Orchestrator Bridge (Day 3-4)

### 3.1 Create Bridge Pattern

**New File**: `src/core/orchestration/contract_bridge.py`

```python
class ContractBridge:
    """Bridges current orchestrator to contract-first tools"""
    
    def wrap_for_orchestrator(self, kgas_tool: KGASTool) -> Tool:
        """Wrap KGASTool to work with current orchestrator"""
        
    def convert_input(self, dict_input: Dict[str, Any]) -> ToolRequest:
        """Convert orchestrator dict to ToolRequest"""
        
    def convert_output(self, tool_result: ToolResult) -> Dict[str, Any]:
        """Convert ToolResult back to dict for orchestrator"""
```

### 3.2 Test Bridge with Multiple Tools

**Test Tools**:
1. T03TextLoader (simple input/output)
2. T15ATextChunker (transformation)
3. T31EntityBuilder (Neo4j integration)

## Phase 4: Pilot Migration (Week 2)

### 4.1 Migrate Category A Tools (Simple Loaders)

**Tools**: T01-T14 file loaders
**Why**: Minimal dependencies, clear input/output

**Process per tool**:
1. Create new file: `tool_name_kgas.py`
2. Implement KGASTool interface
3. Define schemas
4. Add tests
5. Update tool registry

### 4.2 Parallel Testing

**Setup**:
- Run old and new versions in parallel
- Compare outputs
- Measure performance
- Document differences

## Phase 5: Service Integration (Week 3)

### 5.1 Standardize Service Interfaces

**Goal**: Remove need for adapter methods

**Steps**:
1. Define standard service interfaces
2. Version service APIs
3. Update services with deprecation warnings
4. Migrate tools to new methods

### 5.2 Remove Field Adapters

**Current**: Field adapters transform data between tools
**Target**: Standardized contracts eliminate need

**Process**:
1. Identify all field adapter usage
2. Ensure contract alignment
3. Remove adapter calls
4. Test data flow

## Phase 6: Full Migration (Week 4-6)

### 6.1 Category B: Processing Tools
- Schema definition focus
- State management considerations

### 6.2 Category C: Neo4j Tools  
- Service integration focus
- Transaction management

### 6.3 Category D: Analysis Tools
- Complex output schemas
- Performance considerations

### 6.4 Category E: Extraction Tools
- LLM integration patterns
- Async considerations

## Phase 7: Cleanup (Week 7)

### 7.1 Remove Legacy Code
- Delete old tool implementations
- Remove compatibility layers
- Clean up duplicate contracts

### 7.2 Update Documentation
- Remove migration guides
- Update all references
- Archive migration history

## Risk Mitigation

### Parallel Running
- Keep both implementations during migration
- Feature flag for switching
- Gradual rollout

### Rollback Plan
- Git tags at each phase
- Database migration scripts
- Quick revert procedures

### Testing Strategy
- Unit tests for each tool
- Integration tests for pipelines
- Performance benchmarks
- User acceptance tests

## Success Metrics

### Phase Metrics
- Phase 1: Validation fix works, one tool migrated
- Phase 2: Documentation complete and reviewed
- Phase 3: Bridge handles 3+ tools successfully
- Phase 4: All Category A tools migrated
- Phase 5: Services standardized
- Phase 6: 80% tools migrated
- Phase 7: Legacy code removed

### Overall Metrics
- Zero production incidents during migration
- Performance within 5% of current
- All tests passing
- Documentation up to date

## Decision Log

### Key Decisions Made
1. **Use adapter pattern** rather than modifying orchestrator
2. **Migrate incrementally** rather than big bang
3. **Keep backward compatibility** during migration
4. **Document first** to guide implementation

### Decisions Needed
1. **Feature flag system** - How to switch between implementations?
2. **Performance targets** - What's acceptable overhead?
3. **Migration timeline** - Aggressive or conservative?
4. **Team allocation** - Who owns what parts?

## Communication Plan

### Stakeholders
- Development team
- QA team
- DevOps team
- Product owners

### Updates
- Weekly progress reports
- Phase completion announcements
- Issue escalation process
- Final migration celebration

## Conclusion

This methodical approach minimizes risk while achieving the contract-first goal. By starting with quick fixes and documentation, we build confidence before tackling complex migrations. The bridge pattern allows gradual migration without breaking existing functionality.

**Next Action**: Start Phase 1.1 - Fix validation attribute mismatch