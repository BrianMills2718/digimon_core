# Systematic Cleanup Plan

## Overview
We have 11 tools implemented out of 121, with quality issues discovered through adversarial testing. This plan provides a systematic approach to cleanup and future development.

## Phase 1: Fix Critical Bugs (1-2 days)

### 1.1 Entity Timestamp Issue ✅ FIXED
**Problem**: PageRank crashes on entities without created_at/updated_at
**Solution**: Added default timestamps in neo4j_manager._entity_from_props()
```python
if "created_at" not in props:
    props["created_at"] = datetime.utcnow()
if "updated_at" not in props:
    props["updated_at"] = datetime.utcnow()
```
**Status**: ✅ Fixed and tested

### 1.2 Embedding Text Assumption
**Problem**: T41 assumes entities have text content
**Solution**: 
- Check entity attributes for text fields
- Fall back to entity name if no text
- Skip entities with no textual content
**File**: `src/tools/phase3/t41_embedding_generator.py`

### 1.3 Natural Language Query
**Problem**: Only 25% success rate
**Solution**:
- Improve query parsing
- Add fallback strategies
- Better entity matching
**File**: `src/tools/phase7/t94_natural_language_query.py`

## Phase 2: Configurability Audit (1 day)

### 2.1 Create Tool Template
```python
"""T{number}: {Tool Name} - {Description}"""

from typing import Dict, Any, Optional
from datetime import datetime

class {ToolName}:
    """Tool description."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # Initialize services
    
    def {method_name}(
        self,
        # Required parameters first
        required_param: str,
        # Configurable parameters with defaults
        threshold: float = 1.0,
        max_iterations: int = 10,
        algorithm: str = "default",
        # Optional parameters last
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Method description.
        
        Args:
            required_param: Description
            threshold: Description (default: 1.0)
            max_iterations: Description (default: 10)
            algorithm: Description (default: "default")
            metadata: Optional metadata
            
        Returns:
            Dictionary with results and metadata
        """
        start_time = datetime.utcnow()
        warnings = []
        
        try:
            # Implementation
            pass
            
        except Exception as e:
            # Return partial results
            return {
                "status": "error",
                "error": str(e),
                "warnings": warnings,
                "metadata": {
                    "duration_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000)
                }
            }
```

### 2.2 Audit Existing Tools
Check each implemented tool for:
- [ ] Hardcoded thresholds
- [ ] Hardcoded iteration limits
- [ ] Hardcoded algorithm parameters
- [ ] Missing configurability
- [ ] Missing metadata in response

**Tools to audit**:
1. T01: PDF Document Loader
2. T13: Text Chunker ✓ (already configurable)
3. T23a: SpaCy Entity Extractor
4. T23b: LLM Entity Extractor
5. T24: Relationship Extractor
6. T31: Entity Node Builder ✓ (just fixed)
7. T41: Embedding Generator
8. T49: Multi-hop Query ✓ (already configurable)
9. T50: Neighborhood Search ✓ (already configurable)
10. T52: Path Finding ✓ (already configurable)
11. T56: Community Summary
12. T68: PageRank Analyzer
13. T94: Natural Language Query

## Phase 3: Specification Compliance (2 days)

### 3.1 Compare Implementation vs Spec
For each tool:
1. Read specification in `docs/core/SPECIFICATIONS.md`
2. Compare with actual implementation
3. Document deviations
4. Either:
   - Update implementation to match spec
   - Update spec to match implementation (with justification)

### 3.2 Known Deviations
- **T31**: Spec says "create entity nodes", implementation does community detection
  - **Decision**: Update spec to include community detection as optional feature

## Phase 4: Testing Standards (1 day)

### 4.1 Create Test Template
```python
def test_{tool_name}_configurability():
    """Test that tool accepts configurable parameters."""
    tool = ToolClass(db)
    
    # Test with default parameters
    result1 = tool.method()
    
    # Test with custom parameters
    result2 = tool.method(threshold=0.5, max_iterations=5)
    
    # Verify parameters affect behavior
    assert result1 != result2
```

### 4.2 Add Integration Tests
- Test entities created without official tools
- Test error recovery scenarios
- Test with missing optional components
- Test configurability for all parameters

## Phase 5: Documentation Update (1 day)

### 5.1 Update CLAUDE.md
- Add "Known Issues" section
- Update tool status with quality indicators
- Add "Before Implementation" checklist

### 5.2 Create TOOL_STANDARDS.md
- Configurability requirements
- Error handling patterns
- Response format standards
- Testing requirements

## Phase 6: Future Tool Implementation Process

### Before implementing any new tool:
1. **Read specification carefully**
2. **Check DESIGN_PRINCIPLES.md**
3. **Use tool template**
4. **Write tests first** (TDD)
5. **Implement with configurability**
6. **Add integration tests**
7. **Update documentation**

### Quality Gates:
- [ ] All parameters configurable
- [ ] No hardcoded values
- [ ] Returns partial results on error
- [ ] Includes timing metadata
- [ ] Handles missing timestamps
- [ ] Tests pass with various parameters
- [ ] Matches specification

## Prioritization

### Week 1: Critical Fixes
1. Fix PageRank timestamp issue (HIGH)
2. Fix Embedding text assumption (HIGH)
3. Fix NLQ success rate (HIGH)
4. Create tool template (MEDIUM)

### Week 2: Systematic Cleanup
1. Audit all tools for hardcoded values
2. Add configurability where missing
3. Create comprehensive tests
4. Update documentation

### Week 3+: Continue Implementation
1. Implement remaining Phase 1-3 tools
2. Use new standards and templates
3. Maintain quality gates

## Success Metrics

- Zero hardcoded algorithm parameters
- All tools handle missing fields gracefully
- 100% of tools follow configurability pattern
- Integration tests for all edge cases
- Clear documentation of any spec deviations

## Maintenance

- Monthly audit of new implementations
- Quarterly review of design principles
- Continuous improvement of templates
- Regular adversarial testing