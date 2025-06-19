# Session Handoff Protocol

**Purpose**: Prevent parallel implementations and API divergence between sessions.

## ⚠️ CRITICAL RULES

1. **Single Implementation**: ALL code in `/src/` - NO exceptions
2. **No Parallel Rewrites**: Refactor in place, don't create new directories
3. **Contract-First**: Define APIs before implementation
4. **Integration Tests**: Required before claiming phase complete

## 📍 Current State (2025-06-18)

### Implementation Location
- **Active**: `/src/` (ONLY implementation)
- **Archive**: `super_digimon_implementation/` (DO NOT USE - parallel attempt that caused issues)

### What Works
- **Phase 1**: ✅ Basic pipeline (484 entities from test)
- **Phase 2**: ❌ Broken (API mismatch: `current_step` vs `step_number`)
- **Phase 3**: 🔧 Standalone only

### Known Issues
- **A1**: WorkflowStateService expects `step_number`, Phase 2 passes `current_step`
- **A2**: No standard phase interface
- **A3**: UI hardcoded to Phase 1
- **A4**: No integration testing

## 🔧 Service Contracts in Effect

### WorkflowStateService v1
```python
def update_workflow_progress(
    workflow_id: str,
    step_number: int,  # NOT current_step!
    status: str = "running",
    error_message: Optional[str] = None
)
```

### Phase Processing (Proposed)
```python
class ProcessingRequest:
    document_path: str
    options: Dict[str, Any]

class ProcessingResult:
    entities: List[Entity]
    relationships: List[Relationship]
    metadata: Dict[str, Any]
```

## ✅ Before Making Changes

### Adding New Phase
1. [ ] Define contract in `contracts/`
2. [ ] Write integration test with existing phases
3. [ ] Implement in `/src/tools/phaseX/`
4. [ ] Update compatibility matrix
5. [ ] Test with UI before claiming complete

### Modifying Service API
1. [ ] Add version parameter
2. [ ] Support old parameter names
3. [ ] Update all callers
4. [ ] Test all phases still work
5. [ ] Document migration path

### Starting New Session
1. [ ] Read this file
2. [ ] Check git status
3. [ ] Run integration tests
4. [ ] Update this file with changes

## 🚫 DO NOT

- Create new implementation directories
- Change APIs without backward compatibility
- Claim phase complete without integration test
- Write aspirational documentation
- Start "clean rewrites" in parallel

## 📝 Session Log

### 2025-06-18
- Discovered parallel implementation caused Phase 1→2 failure
- Documented root cause: API divergence
- Plan: Fix Phase 2 API calls, archive parallel implementation

### [Add your session updates here]
- Date:
- What changed:
- Known issues:
- Next steps: