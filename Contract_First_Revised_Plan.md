# Contract-First Implementation: Revised Plan (No Backwards Compatibility)

**Date**: 2025-08-05  
**Key Decision**: No backwards compatibility needed - single user, development phase

## Simplified 4-Week Aggressive Plan

### Week 1: Foundation & Orchestrator Update

#### Day 1-2: Fix Core Issues
1. **Fix validation attribute** in tool_contract.py
   - Simple: Add `validation_errors` property
   
2. **Update Orchestrator directly**
   ```python
   # Change from:
   def execute_pipeline(tools, input_data: Dict)
   
   # To:
   def execute_pipeline(tools, request: ToolRequest)
   ```

3. **Remove field adapters entirely**
   - Delete field_adapters.py
   - Remove all adapter usage

#### Day 3-5: Update Core Services
- Fix service interfaces (no adapters)
- Tools will use actual service methods
- Document the real APIs

### Week 2: Simple Tool Migration (Category A)

**Target**: 15 file loader tools (T01-T14)

**Process per tool**:
1. Change from BaseTool to KGASTool
2. Update execute signature
3. Fix service calls
4. Test individually
5. Delete old implementation

**No backwards compatibility = Clean cuts!**

### Week 3: Complex Tool Migration (Categories B, C)

**Target**: 
- Processing tools (T15A, T15B)
- Neo4j tools (T31, T34, T49, T68)

**Focus**: 
- Proper service integration
- Schema definitions
- Remove all mock patterns

### Week 4: Analysis Tools & Cleanup

**Target**:
- Remaining analysis tools
- Complete cleanup
- Documentation update

**Final steps**:
1. Delete all BaseTool code
2. Delete tool_protocol.py (old interface)
3. Update all imports
4. Final testing

## Key Advantages of No Backwards Compatibility

1. **No Bridge Code**: Direct implementation only
2. **No Feature Flags**: Simple cutover
3. **No Adapter Methods**: Clean service interfaces
4. **Faster Migration**: No compatibility testing
5. **Cleaner Codebase**: No legacy code during migration

## Simplified Success Metrics

- Week 1: Orchestrator uses ToolRequest/ToolResult
- Week 2: All loaders migrated
- Week 3: Core pipeline tools migrated
- Week 4: Everything on contract-first, old code deleted

## Risk Mitigation (Simplified)

Since you're the only user:
1. **Git branches**: Create `contract-first` branch
2. **Test frequently**: Run after each tool migration
3. **Rollback plan**: Keep `master` stable until complete

## Next Immediate Actions

1. Create new branch: `git checkout -b contract-first`
2. Fix validation attribute (15 min)
3. Update orchestrator to use ToolRequest (2 hours)
4. Test with one tool (1 hour)
5. If successful, proceed with aggressive migration

This is MUCH simpler than the original plan!