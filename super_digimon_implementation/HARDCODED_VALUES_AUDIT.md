# Hardcoded Values Audit

Results from automated detection on January 17, 2025.

## Summary
- **31 hardcoded values** found across 13 files
- Most common: confidence thresholds (0.8, 0.9)
- Critical issues in quality/provenance services

## High Priority Fixes

### 1. Quality Service (src/core/quality_service.py)
```python
# Current hardcoded values:
confidence >= 0.8  # Line 112, 218
provenance < 0.6   # Line 127
consistency < 0.7  # Line 131
completeness < 0.8 # Line 135
stdev > 0.2        # Line 186
attributes > 50    # Line 338
warnings > 5       # Line 342
```

**Fix**: Add configurable thresholds
```python
class QualityService:
    def __init__(
        self,
        db_manager: DatabaseManager,
        high_confidence_threshold: float = 0.8,
        provenance_threshold: float = 0.6,
        consistency_threshold: float = 0.7,
        completeness_threshold: float = 0.8,
        variance_threshold: float = 0.2
    ):
```

### 2. Natural Language Query (t94)
Multiple hardcoded values affecting query success:
- `confidence = 0.9` (line 150)
- `len(results) < 3` (line 155)
- `len(chunk.text) > 200` (line 264)
- `max_tokens=500` (line 336)
- `top_score > 0.8` (line 366)

**Fix**: Make all configurable
```python
def query(
    self,
    query_text: str,
    min_results: int = 3,
    confidence_threshold: float = 0.8,
    max_tokens: int = 500,
    text_preview_length: int = 200,
    # ...
):
```

### 3. PageRank (t68)
- `confidence = 0.95` (line 129)
- `stats["std"] < 0.0001` (line 136)

**Fix**: Add convergence parameters
```python
def compute_pagerank(
    self,
    convergence_threshold: float = 0.0001,
    result_confidence: float = 0.95,
    # ...
):
```

## Pattern Analysis

### Common Hardcoded Values
1. **Confidence scores**: 0.6, 0.8, 0.9, 0.95
2. **Count thresholds**: 3, 5, 50
3. **Size limits**: 200, 500
4. **Statistical thresholds**: 0.0001, 0.2

### Root Causes
1. **Quick prototyping**: Values chosen during development
2. **Missing requirements**: Specs didn't specify configurability
3. **Copy-paste**: Similar values propagated across files

## Action Items

### Immediate (Phase 1)
- [ ] Fix Quality Service thresholds
- [ ] Fix NLQ hardcoded values (improving success rate)
- [ ] Fix PageRank convergence threshold

### Short Term (Phase 2)
- [ ] Add to ALLOWED_VALUES for truly constant values
- [ ] Create configuration classes for threshold groups
- [ ] Update tool template with common parameters

### Long Term
- [ ] Add pre-commit hook running detect_hardcoded.py
- [ ] Create configuration file for system-wide defaults
- [ ] Add parameter tuning guide

## Configuration Strategy

### 1. Group Related Thresholds
```python
@dataclass
class QualityThresholds:
    high_confidence: float = 0.8
    medium_confidence: float = 0.6
    low_confidence: float = 0.4
    variance_warning: float = 0.2
```

### 2. Use Environment Variables for Defaults
```python
DEFAULT_CONFIDENCE = float(os.getenv("GRAPHRAG_DEFAULT_CONFIDENCE", "0.8"))
```

### 3. Document Why Values Exist
```python
# Maximum 50 attributes to prevent memory issues with large graphs
MAX_ATTRIBUTES = 50  # TODO: Make configurable based on available memory
```

## Exceptions to Keep

Some values might be OK to keep hardcoded:
- API limits (e.g., max_tokens=500 for GPT-3.5)
- Physical constraints (e.g., batch_size=1000 for memory)
- Mathematical constants (e.g., 0.0001 for convergence)

But these should be:
1. Named constants, not magic numbers
2. Documented with rationale
3. Added to ALLOWED_VALUES in detector

## Next Steps

1. Fix the three high-priority tools (Quality, NLQ, PageRank)
2. Run detector again to verify fixes
3. Add detector to CI/CD pipeline
4. Create configuration management system