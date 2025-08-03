**Doc status**: Living – auto-checked by doc-governance CI

# CRITICAL: NO MOCKS Policy Violation

**Severity**: CRITICAL - Direct violation of core architectural principle  
**Issue**: `Neo4jFallbackMixin` provides mock responses when Neo4j is unavailable  
**Impact**: System pretends to work when dependencies are down, violating user trust

## 🚨 Policy Violation Details

### The NO MOCKS Policy (from CLAUDE.md)
> **NO MOCKS** - When Neo4j is down, fail clearly - don't pretend to work

### What We Found
The `src/tools/phase1/neo4j_fallback_mixin.py` directly violates this policy by:
1. Creating mock entity results when Neo4j is unavailable
2. Creating mock edge results with fake IDs
3. Creating mock PageRank results with fabricated scores
4. Returning empty query results instead of failing

### Where It's Used
- `EdgeBuilder` (T34) - Core graph construction tool
- `MultiHopQueryEngine` (T49) - Critical query functionality
- Potentially other tools inheriting from these classes

## 📊 Impact Analysis

### User Trust Violation
- **Expected**: Clear error message when Neo4j is down
- **Actual**: System returns fake data marked as "success"
- **Risk**: Users make decisions based on fabricated data

### Data Integrity Issues
```python
# Example mock response that violates policy:
{
    "status": "success",  # ❌ Lying about success
    "neo4j_id": "mock_abc123",  # ❌ Fake ID
    "properties": {
        "mock": True,  # ⚠️ Hidden in properties
        # ... fabricated data ...
    },
    "warning": "Neo4j unavailable - using mock storage"  # ⚠️ Easy to miss
}
```

### Architectural Consistency
- Contradicts ERROR_HANDLING_BEST_PRACTICES.md
- Violates principle of "Truth Before Aspiration"
- Undermines reliability claims

## 🔧 Required Remediation

### Immediate Actions
1. **Remove Neo4jFallbackMixin** entirely
2. **Update affected tools** to fail explicitly
3. **Implement proper error handling** per best practices

### Correct Implementation
```python
# What it SHOULD do:
def execute(self):
    if not self._check_neo4j_available():
        return {
            "status": "error",
            "error": "Neo4j database unavailable",
            "message": "Cannot perform graph operations without database connection",
            "recovery_suggestions": [
                "Check Neo4j is running on port 7687",
                "Verify credentials in configuration",
                "Check network connectivity"
            ]
        }
    # ... actual implementation ...
```

### Migration Path
1. **Phase 1**: Document all tools using fallback mixin
2. **Phase 2**: Create proper error handlers for each tool
3. **Phase 3**: Remove mixin and test error scenarios
4. **Phase 4**: Update integration tests to verify failures

## 📋 Affected Components

### Tools Using Mock Fallback
| Tool | Class | Mock Behavior | Priority |
|------|-------|---------------|----------|
| T34 | EdgeBuilder | Creates fake edges | CRITICAL |
| T49 | MultiHopQueryEngine | Returns empty results | CRITICAL |
| Others | TBD | Need full audit | HIGH |

### Test Files to Update
- Integration tests expecting 100% reliability
- Any tests that rely on mock behavior
- Error handling test scenarios

## 🎯 Success Criteria

### Policy Compliance
- [ ] No mock data returned when dependencies fail
- [ ] All failures have clear, actionable error messages
- [ ] Error states properly propagated to UI
- [ ] Documentation updated to reflect actual behavior

### User Experience
- [ ] Users know immediately when Neo4j is down
- [ ] Error messages suggest recovery actions
- [ ] No silent failures or fake success states
- [ ] Trust maintained through transparency

## 🚦 Priority

**CRITICAL** - This violation undermines the entire system's trustworthiness and must be addressed before any new feature development.

**Rationale**: Users rely on GraphRAG for analytical decisions. Returning fabricated data when the database is down could lead to incorrect conclusions and destroy user trust.

---

**Next Action**: Remove `Neo4jFallbackMixin` and implement proper error handling per ERROR_HANDLING_BEST_PRACTICES.md-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
