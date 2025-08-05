# Next Steps: Contract-First Implementation

## Current Status

We have successfully:
1. ✅ Reviewed architecture documentation (ADR-001, ADR-028)
2. ✅ Implemented Layer 2 tool adapter for contract-first design
3. ✅ Created orchestrator compatibility layer
4. ✅ Demonstrated the architectural alignment

## Immediate Issues to Address

### 1. Orchestrator Contract Mismatch
**Problem**: The sequential engine passes raw dicts to tools, but tools expect ToolRequest objects.

**Solution Options**:
- **Option A**: Modify orchestrator to create ToolRequest objects
- **Option B**: Add transformation layer in the adapter
- **Option C**: Create new orchestrator implementation following contract-first design

### 2. ProvenanceService API Mismatch
**Problem**: The service doesn't have `create_tool_execution_record` method.

**Solution**: Either add the missing method or update tools to use existing API.

### 3. Tool Validation Issues
**Problem**: Tools fail validation with empty error arrays.

**Solution**: Debug the validation logic to understand why valid tools are failing.

## Recommended Path Forward

### Phase 1: Fix Immediate Blockers (1-2 days)
1. Update orchestrator to pass ToolRequest objects
2. Fix ProvenanceService API or update tool adapter
3. Debug and fix validation logic

### Phase 2: Tool Migration (3-5 days)
1. Select 5 pilot tools for direct KGASTool implementation
2. Remove adapter layers for these tools
3. Validate end-to-end pipeline execution
4. Document migration patterns

### Phase 3: System-Wide Adoption (1-2 weeks)
1. Create tool migration guide
2. Migrate remaining tools to contract-first design
3. Deprecate legacy interfaces
4. Remove field adapter system

### Phase 4: Clean Architecture (ongoing)
1. Consolidate all ToolRequest/ToolResult definitions
2. Remove duplicate contract definitions
3. Update all documentation
4. Create comprehensive test suite

## Technical Debt to Address

1. **Multiple Contract Definitions**: 
   - `/src/core/tool_contract.py` (canonical)
   - `/src/tools/base_tool.py` (legacy)
   - `/src/tools/base_tool_fixed.py` (interim)
   - `/src/tools/base_classes/tool_protocol.py` (protocol version)

2. **Inconsistent Tool Interfaces**:
   - Some tools use `execute(input_data)`
   - Some tools use `process(data)`
   - Some tools use `execute(request: ToolRequest)`

3. **Service Interface Evolution**:
   - Services have evolved but tools haven't been updated
   - Need comprehensive API documentation

## Success Criteria

The contract-first implementation will be complete when:
1. All tools implement KGASTool interface directly
2. No field adapters are needed
3. Orchestrator uses ToolRequest/ToolResult contracts
4. All tests pass without adapter workarounds
5. Documentation reflects actual implementation

## Benefits of Completion

1. **Simplified Integration**: New tools automatically work with the system
2. **Theory Integration**: Built-in support for ontology-aware processing
3. **Consistent Error Handling**: Standardized error propagation
4. **Better Testing**: Contract-based testing for all tools
5. **AI Orchestration Ready**: Clean interfaces for LLM-based tool composition