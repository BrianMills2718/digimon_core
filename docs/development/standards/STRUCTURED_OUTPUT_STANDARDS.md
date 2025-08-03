# Structured Output Development Standards

**Status**: ✅ REQUIRED FOR ALL NEW DEVELOPMENT  
**Implementation**: `src/core/structured_llm_service.py`, `src/orchestration/reasoning_schema.py`  
**Monitoring**: `src/monitoring/structured_output_monitor.py`  
**Last Updated**: 2025-08-03  

## Overview

All LLM integrations in the KGAS system MUST use structured output with Pydantic schema validation. This standard eliminates manual JSON parsing, ensures type safety, and provides comprehensive monitoring capabilities.

## Mandatory Requirements

### 1. Schema-First Development
**REQUIRED**: All LLM operations must define Pydantic schemas before implementation.

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ComponentResponse(BaseModel):
    """Pydantic schema for component LLM operations"""
    results: List[dict] = Field(description="Processing results with metadata")
    confidence: float = Field(description="Operation confidence", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of processing approach")
    metadata: Optional[dict] = Field(description="Additional metadata", default=None)
```

### 2. StructuredLLMService Usage
**REQUIRED**: All LLM operations must use the centralized StructuredLLMService.

```python
from src.core.structured_llm_service import get_structured_llm_service

def component_llm_operation(prompt: str) -> ComponentResponse:
    """Standard pattern for LLM operations"""
    llm_service = get_structured_llm_service()
    
    return llm_service.structured_completion(
        prompt=prompt,
        schema=ComponentResponse,
        temperature=0.05,  # Optimized for JSON reliability
        max_tokens=32000
    )
```

### 3. Monitoring Integration
**REQUIRED**: All structured output operations must include monitoring.

```python
from src.monitoring.structured_output_monitor import track_structured_output

def monitored_llm_operation(component_name: str, input_data: str):
    """LLM operation with integrated monitoring"""
    with track_structured_output(component_name, "ComponentResponse") as tracker:
        try:
            result = llm_service.structured_completion(
                prompt=build_prompt(input_data),
                schema=ComponentResponse
            )
            tracker.set_success(True, result)
            return result
        except ValidationError as e:
            tracker.set_validation_error(str(e))
            raise
        except Exception as e:
            tracker.set_llm_error(str(e))
            raise
```

### 4. Error Handling Standards
**REQUIRED**: All LLM operations must implement comprehensive error handling.

```python
from pydantic import ValidationError

def robust_llm_operation(input_data: dict) -> dict:
    """Standard error handling pattern"""
    try:
        # Validate inputs
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        # Structured completion
        result = llm_service.structured_completion(
            prompt=build_prompt(input_data),
            schema=ComponentResponse,
            temperature=0.05
        )
        
        return {
            "status": "success",
            "data": result.model_dump(),
            "confidence": result.confidence
        }
        
    except ValidationError as e:
        logger.error(f"Schema validation failed: {e}")
        return {
            "status": "validation_error",
            "error": str(e),
            "recovery": "Check LLM output format and schema compatibility"
        }
        
    except Exception as e:
        logger.error(f"LLM operation failed: {e}")
        return {
            "status": "llm_error", 
            "error": str(e),
            "recovery": "Check API availability and retry with exponential backoff"
        }
```

## Schema Design Standards

### 1. Field Descriptions
**REQUIRED**: All schema fields must have descriptive Field annotations.

```python
class WellDocumentedSchema(BaseModel):
    """Well-documented schema following standards"""
    
    entities: List[dict] = Field(
        description="Extracted entities with type, confidence, and position data"
    )
    
    confidence: float = Field(
        description="Overall extraction confidence score",
        ge=0.0,  # Validation constraint
        le=1.0
    )
    
    processing_metadata: dict = Field(
        description="Metadata about processing including model used and timing",
        default_factory=dict
    )
```

### 2. Validation Constraints
**REQUIRED**: Use Pydantic validators for data integrity.

```python
from pydantic import validator

class ValidatedSchema(BaseModel):
    """Schema with comprehensive validation"""
    
    confidence: float = Field(ge=0.0, le=1.0)
    entity_count: int = Field(ge=0)
    processing_time: float = Field(gt=0.0)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Custom validation for confidence scores"""
        if not isinstance(v, (int, float)):
            raise ValueError("Confidence must be numeric")
        return float(v)
    
    @validator('entity_count')
    def validate_entity_count(cls, v):
        """Ensure entity count is reasonable"""
        if v > 10000:  # Sanity check
            raise ValueError("Entity count exceeds reasonable limit")
        return v
```

### 3. Composable Schemas
**RECOMMENDED**: Design reusable schema components.

```python
class BaseOperationMetadata(BaseModel):
    """Reusable metadata component"""
    operation_id: str
    timestamp: str
    model_used: str
    execution_time: float

class EntityExtractionResponse(BaseOperationMetadata):
    """Composed schema using base metadata"""
    entities: List[dict]
    confidence: float
    
class RelationshipExtractionResponse(BaseOperationMetadata):
    """Another schema reusing base metadata"""
    relationships: List[dict]
    confidence: float
```

## Performance Standards

### 1. Temperature Optimization
**REQUIRED**: Use temperature=0.05 for maximum JSON reliability.

```python
# Correct - optimized for structured output
result = llm_service.structured_completion(
    prompt=prompt,
    schema=schema,
    temperature=0.05  # Maximum reliability
)

# Incorrect - high temperature causes JSON errors
result = llm_service.structured_completion(
    prompt=prompt,
    schema=schema,
    temperature=0.8  # Too high for structured output
)
```

### 2. Prompt Engineering
**REQUIRED**: Follow structured output prompt patterns.

```python
def build_structured_prompt(input_data: str, schema: type) -> str:
    """Standard prompt building for structured output"""
    schema_description = schema.model_json_schema()
    
    return f"""
Analyze the following data and provide a structured response.

Input Data:
{input_data}

Requirements:
- Provide accurate analysis based on the input
- Include confidence scores for all assessments  
- Explain reasoning for major decisions
- Follow the exact output schema provided

Output Schema:
{schema_description}

Respond with valid JSON only, no markdown formatting.
"""
```

### 3. Performance Monitoring
**REQUIRED**: Monitor response times and success rates.

```python
def performance_aware_operation():
    """Operation with performance monitoring"""
    start_time = time.time()
    
    try:
        result = llm_service.structured_completion(
            prompt=prompt,
            schema=schema,
            temperature=0.05
        )
        
        execution_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"LLM operation completed in {execution_time:.3f}s")
        
        # Performance alerting
        if execution_time > 10.0:  # 10 second threshold
            logger.warning(f"Slow LLM operation: {execution_time:.3f}s")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"LLM operation failed after {execution_time:.3f}s: {e}")
        raise
```

## Testing Standards

### 1. Schema Validation Testing
**REQUIRED**: Test schema validation with valid and invalid data.

```python
import pytest
from pydantic import ValidationError

class TestComponentSchema:
    """Standard schema testing pattern"""
    
    def test_valid_schema_data(self):
        """Test schema accepts valid data"""
        valid_data = {
            "results": [{"entity": "test", "type": "PERSON"}],
            "confidence": 0.9,
            "reasoning": "High confidence extraction"
        }
        
        result = ComponentResponse(**valid_data)
        assert result.confidence == 0.9
        assert len(result.results) == 1
    
    def test_invalid_confidence_range(self):
        """Test schema rejects invalid confidence values"""
        invalid_data = {
            "results": [],
            "confidence": 1.5,  # Invalid - exceeds 1.0
            "reasoning": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ComponentResponse(**invalid_data)
        
        assert "ensure this value is less than or equal to 1" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test schema requires all mandatory fields"""
        incomplete_data = {
            "results": []
            # Missing confidence and reasoning
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ComponentResponse(**incomplete_data)
        
        assert "field required" in str(exc_info.value)
```

### 2. Integration Testing
**REQUIRED**: Test with real LLM service integration.

```python
class TestLLMIntegration:
    """Integration testing with real LLM service"""
    
    def test_real_llm_structured_completion(self):
        """Test with actual LLM service"""
        llm_service = get_structured_llm_service()
        
        if not llm_service.available:
            pytest.skip("LLM service not available")
        
        result = llm_service.structured_completion(
            prompt="Extract entities from: Apple Inc. was founded by Steve Jobs",
            schema=ComponentResponse,
            temperature=0.05
        )
        
        # Validate result structure
        assert isinstance(result, ComponentResponse)
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.reasoning) > 0
        assert isinstance(result.results, list)
    
    def test_monitoring_integration(self):
        """Test monitoring integration"""
        from src.monitoring.structured_output_monitor import get_monitor
        
        monitor = get_monitor()
        initial_count = len(monitor.metrics_history)
        
        # Execute monitored operation
        with track_structured_output("test_component", "ComponentResponse"):
            time.sleep(0.1)  # Simulate processing
        
        # Verify monitoring captured the operation
        assert len(monitor.metrics_history) > initial_count
        
        latest_metric = monitor.metrics_history[-1]
        assert latest_metric.component == "test_component"
        assert latest_metric.schema_name == "ComponentResponse"
```

### 3. Error Handling Testing
**REQUIRED**: Test all error conditions and recovery patterns.

```python
class TestErrorHandling:
    """Test error handling patterns"""
    
    def test_validation_error_handling(self):
        """Test handling of schema validation errors"""
        with patch.object(llm_service, 'structured_completion') as mock_llm:
            # Mock LLM to return invalid data
            mock_llm.side_effect = ValidationError("Invalid schema data", ComponentResponse)
            
            result = robust_llm_operation({"test": "data"})
            
            assert result["status"] == "validation_error"
            assert "recovery" in result
            assert "schema compatibility" in result["recovery"]
    
    def test_llm_service_unavailable(self):
        """Test handling when LLM service is unavailable"""
        with patch.object(llm_service, 'structured_completion') as mock_llm:
            mock_llm.side_effect = RuntimeError("API service unavailable")
            
            result = robust_llm_operation({"test": "data"})
            
            assert result["status"] == "llm_error"
            assert "API availability" in result["recovery"]
```

## Migration Guidelines

### For Existing Components
1. **Identify LLM operations** using manual JSON parsing
2. **Define Pydantic schemas** for expected outputs  
3. **Replace json.loads()** with structured_completion calls
4. **Add monitoring integration** 
5. **Implement comprehensive error handling**
6. **Add validation tests**

### Migration Checklist
```python
# ❌ OLD PATTERN (DEPRECATED)
import json

def old_llm_operation(prompt: str):
    response = openai.completion(prompt=prompt)
    try:
        result = json.loads(response.content)  # Manual parsing
        return result
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}  # Poor error handling

# ✅ NEW PATTERN (REQUIRED)
from src.core.structured_llm_service import get_structured_llm_service
from src.monitoring.structured_output_monitor import track_structured_output

def new_llm_operation(prompt: str) -> ComponentResponse:
    llm_service = get_structured_llm_service()
    
    with track_structured_output("component_name", "ComponentResponse"):
        return llm_service.structured_completion(
            prompt=prompt,
            schema=ComponentResponse,
            temperature=0.05
        )
```

## Quality Assurance

### Code Review Checklist
- [ ] Uses StructuredLLMService instead of manual JSON parsing
- [ ] Defines proper Pydantic schema with Field descriptions
- [ ] Includes monitoring integration with track_structured_output
- [ ] Implements comprehensive error handling (validation + LLM errors)
- [ ] Uses temperature=0.05 for maximum reliability
- [ ] Includes validation tests for schema and integration
- [ ] Follows naming conventions and documentation standards

### Performance Benchmarks
- **Success Rate**: >95% for structured operations
- **Response Time**: <5 seconds average for standard operations
- **Validation Rate**: 100% schema compliance
- **Error Rate**: <2% for LLM errors, <5% for validation errors

### Monitoring Requirements
- **Real-time tracking**: All operations monitored automatically
- **Health validation**: System health checks every 5 minutes
- **Alert thresholds**: Success rate <95%, response time >5s
- **Performance analytics**: Component-specific breakdowns available

## Enforcement

### Automated Checks
```bash
# Pre-commit hooks
make test-structured-output  # Validate all structured output operations
make lint-schemas           # Check schema definitions and usage
make monitor-health         # Verify monitoring integration
```

### CI/CD Integration
```yaml
# Required checks in CI pipeline
- name: Validate Structured Output Compliance
  run: |
    python scripts/validate_structured_output.py
    python scripts/check_schema_coverage.py
    python scripts/verify_monitoring_integration.py
```

### Documentation Requirements
- **Schema Documentation**: All schemas must be documented with examples
- **Integration Examples**: Components must include usage examples
- **Performance Metrics**: Include expected performance characteristics
- **Error Handling**: Document all error conditions and recovery patterns

## Conclusion

The structured output standards ensure reliable, maintainable, and observable LLM integrations across the KGAS system. By mandating schema-first development, centralized service usage, and comprehensive monitoring, we eliminate the reliability issues inherent in manual JSON parsing while providing production-ready observability.

**All new development MUST follow these standards. Existing code should be migrated as soon as feasible.**