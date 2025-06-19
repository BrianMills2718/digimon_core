# Tool Implementation Checklist

Use this checklist BEFORE implementing any new tool.

## Pre-Implementation (Planning)

- [ ] **Read the specification** for this tool in `docs/core/SPECIFICATIONS.md`
- [ ] **Identify the tool's phase** (1-8) and dependencies
- [ ] **Check tool contract** - what state does it expect?
- [ ] **Review similar tools** in the same phase for patterns
- [ ] **List all parameters** that should be configurable
- [ ] **Plan error scenarios** - what could go wrong?

## Implementation

### Setup
- [ ] Copy `TOOL_TEMPLATE.py` as starting point
- [ ] Update all placeholders with actual values
- [ ] Import required models and utilities
- [ ] Initialize required services in `__init__`

### Core Method
- [ ] All algorithmic parameters have defaults
- [ ] NO hardcoded thresholds or limits
- [ ] Input validation with helpful error messages
- [ ] Try-except wraps main logic
- [ ] Returns partial results on failure

### Response Format
- [ ] Includes `status` field ("success", "partial", "error")
- [ ] Includes primary output fields
- [ ] Includes count fields (e.g., `entity_count`)
- [ ] Includes `metadata` dict with:
  - [ ] `duration_ms`
  - [ ] `algorithm` used
  - [ ] `parameters` used
  - [ ] `warnings` list
  - [ ] `errors` list (if applicable)
- [ ] Includes `quality_score` or `confidence`

### Error Handling
- [ ] Catches specific exceptions where possible
- [ ] Logs errors with context
- [ ] Returns partial results
- [ ] Limits error messages to 5
- [ ] Continues processing after batch failures

### Database Operations
- [ ] Entities include `created_at` and `updated_at`
- [ ] Handles missing fields gracefully
- [ ] Uses transactions appropriately
- [ ] Closes connections properly

## Testing

### Unit Tests
- [ ] Test with default parameters
- [ ] Test with custom parameters
- [ ] Test parameter validation
- [ ] Test with empty input
- [ ] Test with invalid input
- [ ] Test partial failure scenarios

### Integration Tests
- [ ] Test with real database
- [ ] Test with data from upstream tools
- [ ] Test output works with downstream tools
- [ ] Test with missing optional services

### Configurability Tests
- [ ] Verify each parameter affects behavior
- [ ] Test parameter edge cases
- [ ] Test invalid parameter handling

### Performance Tests
- [ ] Test with small dataset (10 items)
- [ ] Test with medium dataset (1000 items)
- [ ] Test with large dataset (10000+ items)
- [ ] Verify batch processing works
- [ ] Check memory usage

## Documentation

### Code Documentation
- [ ] Class docstring explains purpose
- [ ] Method docstring follows template
- [ ] Includes usage example
- [ ] Documents all parameters
- [ ] Documents return format
- [ ] Includes type hints

### Update Project Docs
- [ ] Update tool count in CLAUDE.md
- [ ] Add to implemented tools list
- [ ] Note any deviations from spec
- [ ] Document new patterns discovered

## Quality Checks

### Code Quality
- [ ] Follows naming conventions
- [ ] No code duplication
- [ ] Clear variable names
- [ ] Appropriate logging levels
- [ ] No commented-out code

### Standards Compliance
- [ ] Follows patterns in TOOL_STANDARDS.md
- [ ] Matches specification behavior
- [ ] Uses established patterns
- [ ] Integrates with quality service
- [ ] Integrates with provenance service

## Final Review

- [ ] Run all tests
- [ ] Check test coverage (aim for >80%)
- [ ] Review with fresh eyes
- [ ] Test error scenarios manually
- [ ] Verify response format
- [ ] Check for hardcoded values

## Post-Implementation

- [ ] Commit with descriptive message
- [ ] Update progress tracking
- [ ] Plan integration with next tools
- [ ] Document lessons learned

---

## Red Flags 🚩

If you find yourself doing any of these, STOP and reconsider:

- Writing `if value > 3.0` with a hardcoded number
- Using `raise Exception()` without catching it
- Returning `None` or empty dict on error
- Skipping the "partial results" logic
- Assuming data types without checking
- Ignoring the metadata requirement
- Creating entities without timestamps
- Not testing configurability

## Examples of Good Patterns

```python
# Configurable threshold
def process(self, data, confidence_threshold: float = 0.7):
    if confidence > confidence_threshold:
        # ...

# Partial results
try:
    results = process_all()
except Exception as e:
    return {
        "status": "partial",
        "processed": results_so_far,
        "failed": failed_items,
        "metadata": {...}
    }

# Proper metadata
return {
    "status": "success",
    "entities": entities,
    "entity_count": len(entities),
    "metadata": {
        "duration_ms": int(elapsed * 1000),
        "threshold": confidence_threshold,
        "warnings": warnings
    }
}
```