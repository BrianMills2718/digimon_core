# Structured Output Migration Plan

## Current State Analysis

### Files Using Manual JSON Parsing (Need Migration)

#### 1. **LLM Reasoning Engine** (`src/orchestration/llm_reasoning.py`)
**Status:** PRIMARY TARGET - Most critical
**Issues:** 
- Lines 400-450: Complex manual JSON parsing with 4 fallback strategies
- Lines 562-680: `_extract_json_from_response()` with markdown handling
- Token limit too low: `max_tokens=4000` (should be 32000+)

#### 2. **LLM Integration Component** (`src/tools/phase2/extraction_components/llm_integration.py`)
**Status:** SECONDARY TARGET
**Issues:**
- Lines 160-180: Manual JSON extraction with text manipulation
- Complex fallback to pattern matching when JSON parsing fails

#### 3. **Other Files with Manual json.loads()**
- `src/orchestration/mcp_adapter.py:194` - Manual JSON loads
- Various tools in phase2/phase3 (lower priority)

### Existing Structured Output Infrastructure ✅
- `src/orchestration/reasoning_schema.py` - Pydantic schemas already defined
- `universal_llm_kit/` - Reference implementation available
- LiteLLM already integrated in codebase

## Migration Plan

### Phase 1: Core Infrastructure (Week 1)

#### 1.1 Fix Token Limits (Day 1)
**Target:** `src/orchestration/llm_reasoning.py`
```python
# Change from:
"max_tokens": 4000,  # Line 111
max_tokens=4000      # Line 439

# To:
"max_tokens": 32000,  # Reasonable for complex schemas
max_tokens=32000      # Match Gemini's capacity better
```

#### 1.2 Create Universal LLM Service Integration (Day 2)
**Target:** New file `src/core/structured_llm_service.py`
```python
from universal_llm import structured
from pydantic import BaseModel
from typing import TypeVar, Type

T = TypeVar('T', bound=BaseModel)

class StructuredLLMService:
    def __init__(self):
        # Initialize with proper token limits
        pass
    
    def structured_completion(
        self, 
        prompt: str, 
        schema: Type[T], 
        model: str = "gemini/gemini-2.5-flash"
    ) -> T:
        """Get structured output with fail-fast validation"""
        try:
            response = structured(prompt, schema)
            return schema.model_validate_json(response)
        except Exception as e:
            logger.error(f"Structured output failed: {e}")
            logger.debug(f"Raw response: {response}")
            raise  # Fail fast with context
```

#### 1.3 Create Feature Flag System (Day 3)
**Target:** `src/core/config.py`
```python
STRUCTURED_OUTPUT_ENABLED = {
    "llm_reasoning": True,     # Start with reasoning engine
    "entity_extraction": False, # Enable later
    "mcp_adapter": False       # Enable last
}
```

### Phase 2: LLM Reasoning Engine Migration (Week 2)

#### 2.1 Replace Manual Parsing (Days 1-2)
**Target:** `src/orchestration/llm_reasoning.py`

**Before:**
```python
async def _execute_llm_reasoning(self, prompt, context):
    # Complex LiteLLM call + manual parsing
    response = litellm.completion(...)
    response_text = response.choices[0].message.content
    # Then 100+ lines of manual JSON extraction
    return self._extract_json_from_response(response_text)
```

**After:**
```python
async def _execute_llm_reasoning(self, prompt, context):
    if config.STRUCTURED_OUTPUT_ENABLED["llm_reasoning"]:
        return await self._execute_structured_reasoning(prompt, context)
    else:
        return await self._execute_legacy_reasoning(prompt, context)

async def _execute_structured_reasoning(self, prompt, context):
    schema = EntityExtractionResponse if context.task.task_type == "entity_extraction" else ReasoningResponse
    
    try:
        return self.structured_llm.structured_completion(prompt, schema)
    except Exception as e:
        logger.error(f"Structured reasoning failed for {context.reasoning_type.value}: {e}")
        raise  # Fail fast with full context
```

#### 2.2 Remove Manual Parsing Code (Day 3)
**Target:** Delete methods:
- `_extract_json_from_response()` (~120 lines)
- `_find_complete_json()`
- `_extract_between_braces()`
- `_clean_and_extract()`

#### 2.3 Testing and Validation (Days 4-5)
**Create:** `test_structured_reasoning_migration.py`
```python
async def test_all_reasoning_types_structured():
    """Test all 4 reasoning types with structured output"""
    for reasoning_type in [STRATEGIC, TACTICAL, ADAPTIVE, DIAGNOSTIC]:
        # Test with structured output enabled
        # Verify schema compliance
        # Compare results with legacy method
```

### Phase 3: Entity Extraction Migration (Week 3)

#### 3.1 LLM Integration Component (Days 1-3)
**Target:** `src/tools/phase2/extraction_components/llm_integration.py`

**Replace:**
```python
# Lines 160-180: Manual JSON parsing
extraction_data = json.loads(response_content)
```

**With:**
```python
from pydantic import BaseModel

class ExtractionResult(BaseModel):
    entities: List[EntityData]
    relationships: List[RelationshipData]

# Use structured output
result = self.structured_llm.structured_completion(prompt, ExtractionResult)
```

#### 3.2 T23A LLM Enhanced Tool (Days 4-5)
**Target:** `src/tools/phase1/t23a_llm_enhanced.py`
- Integrate with structured LLM service
- Remove any manual JSON handling
- Ensure entity extraction uses proper schemas

### Phase 4: MCP Adapter and Remaining Files (Week 4)

#### 4.1 MCP Adapter (Days 1-2)
**Target:** `src/orchestration/mcp_adapter.py:194`

#### 4.2 Clean Up Remaining Files (Days 3-5)
**Targets:**
- Any remaining manual `json.loads()` in tools
- Phase 3 files with parsing issues
- Update all error handling to fail-fast pattern

### Phase 5: Documentation and Monitoring (Week 5)

#### 5.1 Update Documentation (Days 1-3)
- Update CLAUDE.md with structured output status
- Create migration evidence files
- Update API documentation

#### 5.2 Add Monitoring (Days 4-5)
- Add structured output success rate metrics
- Monitor validation failure patterns
- Create alerts for parsing failures

## Success Criteria

### Phase 1 Success
- [ ] Token limits increased to 32000+
- [ ] Universal LLM service created and tested
- [ ] Feature flags working

### Phase 2 Success  
- [ ] LLM reasoning engine uses structured output
- [ ] No manual JSON parsing in reasoning engine
- [ ] All 4 reasoning types working with schemas
- [ ] Evidence file: `Evidence_Reasoning_Structured_Output.md`

### Phase 3 Success
- [ ] Entity extraction uses structured output
- [ ] No manual JSON parsing in extraction components
- [ ] F1 scores maintained or improved
- [ ] Evidence file: `Evidence_Entity_Extraction_Structured.md`

### Phase 4 Success
- [ ] All manual `json.loads()` replaced with schema validation
- [ ] MCP adapter uses structured output
- [ ] Evidence file: `Evidence_Complete_Structured_Migration.md`

### Final Success Metrics
- [ ] 0 instances of manual JSON parsing in critical paths
- [ ] All LLM outputs validated with Pydantic schemas
- [ ] Fail-fast behavior on schema validation errors
- [ ] Performance maintained or improved
- [ ] Full evidence documentation

## Risk Mitigation

### High Risk: Schema Validation Failures
**Mitigation:** Comprehensive logging of all failures
```python
except ValidationError as e:
    logger.error(f"Schema validation failed: {e}")
    logger.debug(f"Raw response: {response}")
    logger.debug(f"Expected schema: {schema.model_json_schema()}")
    raise
```

### Medium Risk: Performance Regression  
**Mitigation:** Before/after benchmarks for each phase
```python
# Measure response time, token usage, success rate
# Compare structured vs manual parsing performance
```

### Low Risk: Model Compatibility
**Mitigation:** Test with multiple models during each phase
- Gemini 2.5 Flash (primary)
- OpenAI GPT-4 (secondary)
- Anthropic Claude (if available)

## Implementation Notes

- **No gradual degradation** - fail fast on any schema validation error
- **Comprehensive logging** - log all failures with full context
- **Evidence-based progress** - create evidence file for each phase completion
- **Real API testing only** - no mocks or simulations
- **Performance monitoring** - track before/after metrics

## Validation Commands

```bash
# Test structured output migration
python test_structured_reasoning_migration.py

# Verify no manual JSON parsing remains
grep -r "json\.loads.*response" src/ --exclude-dir=__pycache__

# Check token limit configuration
grep -r "max_tokens.*[0-9]" src/orchestration/

# Validate all schemas work
python test_all_schemas_validation.py
```