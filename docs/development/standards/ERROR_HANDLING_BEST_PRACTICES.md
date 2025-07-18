**Doc status**: Living – auto-checked by doc-governance CI

# Error Handling Best Practices Guide

## Overview

This guide establishes patterns for reliable error handling across the GraphRAG system, ensuring 100% reliability through explicit failures and clear user feedback.

## Core Principles

### 1. **NO MOCKS Policy**
- **Never return fake data** when dependencies fail
- **Fail explicitly** rather than pretending to work
- **Clear error messages** over silent degradation

### 2. **100% Reliability Standard**
- System either **completes successfully** OR **fails with clear error message**
- **No unhandled exceptions** - all errors caught and processed
- **Graceful degradation** with explicit feedback

### 3. **User-Centric Error Messages**
- **What failed**: Specific component/operation
- **Why it failed**: Root cause in user terms
- **Impact**: What functionality is affected

## Error Handling Patterns

### ✅ Gold Standard Pattern (Phase 1 Tools)

**Structure:**
```python
def operation(self, inputs):
    operation_id = self.provenance_service.start_operation(...)
    
    try:
        # Input validation
        if not valid_input:
            return self._complete_with_error(
                operation_id,
                "Clear description of validation failure"
            )
        
        # Dependency check
        if not self.dependency_available():
            return self._complete_with_error(
                operation_id,
                "[Service] connection not available - cannot [specific_operation]"
            )
        
        # Core operation
        result = self._perform_operation(inputs)
        
        # Success completion
        return self._complete_success(operation_id, result)
        
    except Exception as e:
        return self._complete_with_error(
            operation_id,
            f"Unexpected error during [operation]: {str(e)}"
        )
```

**Key Components:**
- **Explicit dependency checks** before operations
- **Structured error completion** with provenance tracking
- **Clear, specific error messages**
- **Exception safety** with catch-all handler

### 📋 Error Message Templates

#### Neo4j Connection Failures
```
"Neo4j connection not available - cannot [specific_operation]"
```
**Examples:**
- "Neo4j connection not available - cannot build entity graph"
- "Neo4j connection not available - cannot calculate PageRank"
- "Neo4j connection not available - cannot query graph"

#### Input Validation Errors
```
"[Input_type] [validation_issue] - [consequence]"
```
**Examples:**
- "Query text cannot be empty"
- "No documents provided for processing"
- "Invalid file format - only PDF files supported"

#### Service Unavailable
```
"[Service_name] service unavailable - [affected_functionality]"
```
**Examples:**
- "OpenAI API unavailable - text processing disabled"
- "Vector index service unavailable - vector search disabled"

#### Configuration Errors
```
"[Component] configuration invalid - [specific_issue]"
```
**Examples:**
- "API key missing - authentication required"
- "Invalid model specified - check configuration"

## Implementation Examples

### ✅ Excellent: T31 Entity Builder

```python
def build_entities(self, mentions, source_refs):
    operation_id = self.provenance_service.start_operation(...)
    
    try:
        if not mentions:
            return self._complete_success(
                operation_id,
                [],
                "No mentions provided for entity building"
            )
        
        if not self.driver:
            return self._complete_with_error(
                operation_id,
                "Neo4j connection not available - cannot build entity graph"
            )
        
        # Process entities...
        
    except Exception as e:
        return self._complete_with_error(
            operation_id,
            f"Unexpected error during entity building: {str(e)}"
        )
```

**Why this works:**
- Clear dependency check with specific message
- Explicit success case for empty input
- Exception safety with context-specific error

### ⚠️ Needs Improvement: Service Manager

**Current:**
```python
print(f"Neo4j connection failed: {e}. Continuing without Neo4j - some features may be limited")
```

**Better:**
```python
print(f"Neo4j connection failed: {e}. Graph operations (entity building, PageRank, multi-hop queries) will be unavailable")
```

**Why:** Specific functionality impact instead of vague "limited features"

### ❌ Poor: Raw Exception Exposure

**Avoid:**
```python
self.driver = GraphDatabase.driver(uri, auth=(user, password))
# Can raise: "Cannot resolve address invalid-host:7687"
```

**Fix:**
```python
try:
    self.driver = GraphDatabase.driver(uri, auth=(user, password))
    # Test connection
    with self.driver.session() as session:
        session.run("RETURN 1")
except Exception as e:
    self.driver = None
    print(f"Neo4j connection failed: {e}")
    print("Graph operations will be unavailable")
```

## Error Response Standards

### Structured Error Response

```python
{
    "status": "error",
    "error": "Clear, user-friendly message",
    "operation_id": "tracking_id",
    "error_code": "DEPENDENCY_UNAVAILABLE",  # Optional
    "suggested_action": "Check Neo4j connection"  # Optional
}
```

### Success Response (for comparison)

```python
{
    "status": "success",
    "result": actual_data,
    "operation_id": "tracking_id",
    "metadata": {...}
}
```

## Testing Error Scenarios

### Critical Test Cases

1. **Dependency Unavailable**
   - Neo4j connection down
   - API services unreachable
   - Configuration missing

2. **Invalid Inputs**
   - Empty required fields
   - Wrong data types
   - Malformed data

3. **Runtime Failures**
   - Network interruptions
   - Resource exhaustion
   - Permission issues

### Testing Approach

```python
def test_neo4j_unavailable():
    # Simulate Neo4j down
    tool = EntityBuilder(shared_driver=None)
    
    result = tool.build_entities(sample_mentions, [])
    
    assert result["status"] == "error"
    assert "Neo4j connection not available" in result["error"]
    assert "cannot build entity graph" in result["error"]
```

## Recovery Patterns

### 1. **Graceful Degradation**
- Continue with reduced functionality
- Clear communication about limitations
- Alternative workflows when possible

### 2. **Retry Logic** (when appropriate)
- **Use for:** Transient network issues
- **Avoid for:** Configuration errors, authentication failures
- **Pattern:** Exponential backoff with limits

### 3. **Fallback Mechanisms**
- **Never:** Return mock/fake data
- **Do:** Provide alternative approaches
- **Example:** "Try smaller document chunks" when memory limited

## Documentation Requirements

### Error Logs
- **Context**: What operation was being performed
- **Inputs**: What data caused the issue
- **Environment**: Relevant system state
- **Recovery**: What user should do next

### User Documentation
- **Common errors** and solutions
- **Dependency requirements** clearly stated
- **Configuration examples** with validation

## Monitoring and Alerting

### Key Metrics
- **Error rates** by component
- **Common failure modes** trending
- **Recovery success rates**
- **User impact** assessment

### Alert Thresholds
- **Critical**: Any unhandled exceptions
- **Warning**: Dependency unavailable > 5 minutes
- **Info**: Input validation failures (tracking patterns)

## Conclusion

Following these patterns ensures:
- **Users understand** what went wrong and why
- **Systems fail safely** without corruption
- **Operations teams** can diagnose issues quickly
- **Reliability targets** (100% success-or-clear-failure) are met

The GraphRAG system prioritizes **explicit failures with clear feedback** over silent degradation or mock responses, maintaining user trust and system integrity.-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
