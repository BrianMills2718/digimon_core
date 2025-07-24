# Unified Error Handling Framework

## Overview

The Unified Error Handling Framework addresses the critical issue of inconsistent error handling across 802+ try blocks in the KGAS codebase. It provides a centralized, taxonomized approach to error classification, recovery, and escalation.

## Key Components

### 1. Error Taxonomy

The framework categorizes all errors into standardized categories:

```python
class ErrorCategory(Enum):
    DATA_CORRUPTION = "data_corruption"      # Critical data integrity issues
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # Memory, connections, etc.
    NETWORK_FAILURE = "network_failure"      # Network timeouts, connection errors
    AUTHENTICATION_FAILURE = "authentication_failure"  # Auth/permission issues
    VALIDATION_FAILURE = "validation_failure"  # Input validation errors
    SYSTEM_FAILURE = "system_failure"        # General system errors
    DATABASE_FAILURE = "database_failure"    # Database connection/transaction errors
    SERVICE_UNAVAILABLE = "service_unavailable"  # Service down/unreachable
    CONFIGURATION_ERROR = "configuration_error"  # Config missing/invalid
    ACADEMIC_INTEGRITY = "academic_integrity"  # Citation/provenance violations
```

### 2. Error Severity Levels

```python
class ErrorSeverity(Enum):
    LOW = "low"                # Minor issues, system continues normally
    MEDIUM = "medium"          # Degraded performance, needs attention
    HIGH = "high"              # Significant impact, immediate action needed
    CRITICAL = "critical"      # Major failure, system compromised
    CATASTROPHIC = "catastrophic"  # Data corruption, system unreliable
```

### 3. Recovery Strategies

```python
class RecoveryStrategy(Enum):
    RETRY = "retry"                    # Simple retry
    FALLBACK = "fallback"              # Use alternative approach
    CIRCUIT_BREAKER = "circuit_breaker"  # Prevent cascading failures
    GRACEFUL_DEGRADATION = "graceful_degradation"  # Reduced functionality
    ABORT_AND_ALERT = "abort_and_alert"  # Stop and notify
    ESCALATE = "escalate"              # Escalate to operators
```

## Implementation

### CentralizedErrorHandler

The main class that handles all error processing:

```python
from src.core.error_taxonomy import CentralizedErrorHandler, get_global_error_handler

# Get global handler instance
handler = get_global_error_handler()

# Handle an error
try:
    # Some operation
    pass
except Exception as e:
    context = {
        "service_name": "MyService",
        "operation": "process_data",
        "user_id": "12345"
    }
    error = await handler.handle_error(e, context)
```

### Using Decorators

The framework provides decorators for automatic error handling:

```python
from src.core.error_taxonomy import handle_errors

class MyService:
    @handle_errors("MyService", "critical_operation")
    async def critical_operation(self, data):
        # Any exceptions will be automatically handled
        result = await self.process(data)
        return result
```

### Context Managers

For block-level error handling:

```python
from src.core.error_taxonomy import handle_errors_async

async def process_batch(items):
    async with handle_errors_async("BatchProcessor", "process_batch", handler):
        for item in items:
            await process_item(item)
```

## Error Classification Rules

### Automatic Classification

The framework automatically classifies errors based on keywords:

1. **Data Corruption** (CATASTROPHIC):
   - Keywords: "corruption", "integrity", "citation fabrication", "orphaned data"
   - Example: "Data corruption detected in entity mappings"

2. **Academic Integrity** (CRITICAL):
   - Keywords: "academic integrity", "citation", "provenance"
   - Example: "Citation fabrication detected"

3. **Database Failures** (HIGH):
   - Keywords: "neo4j", "database", "transaction", "sql"
   - Example: "Neo4j connection failed"

4. **Resource Exhaustion** (HIGH):
   - Keywords: "memory", "pool", "connection", "resource"
   - Example: "Connection pool exhausted"

5. **Network Failures** (MEDIUM):
   - Keywords: "network", "timeout", "connection", "http"
   - Example: "Network timeout connecting to service"

## Recovery Mechanisms

### Built-in Recovery Strategies

1. **Database Connection Recovery**:
   ```python
   async def _recover_database_connection(error):
       # Attempts to reconnect to database
       # Clears connection pools
       # Validates connection health
   ```

2. **Memory Exhaustion Recovery**:
   ```python
   async def _recover_memory_exhaustion(error):
       # Triggers garbage collection
       # Clears caches
       # Reduces memory footprint
   ```

3. **Network Timeout Recovery**:
   ```python
   async def _recover_network_timeout(error):
       # Implements exponential backoff
       # Switches to backup endpoints
       # Uses cached data if available
   ```

### Custom Recovery Strategies

Register custom recovery strategies:

```python
async def custom_recovery(error: KGASError) -> bool:
    # Implement recovery logic
    if can_recover:
        # Do recovery
        return True
    return False

handler.register_recovery_strategy("my_error_pattern", custom_recovery)
```

## Escalation Procedures

### Automatic Escalation

Errors are automatically escalated when:
- Severity is CRITICAL or CATASTROPHIC
- Recovery attempts fail
- Academic integrity violations occur

### Custom Escalation Handlers

```python
async def alert_ops_team(error: KGASError):
    # Send alerts to monitoring systems
    # Create incident tickets
    # Notify on-call engineers
    pass

handler.register_escalation_handler(alert_ops_team)
```

## System Health Monitoring

The framework provides system health assessment:

```python
health = handler.get_system_health_from_errors()
# Returns:
# {
#     "health_score": 8,  # 1-10 scale
#     "status": "healthy",  # healthy/degraded/unhealthy
#     "error_summary": {
#         "total_errors": 15,
#         "error_breakdown": {...},
#         "recovery_success_rates": {...}
#     }
# }
```

### Health Score Calculation

- **10**: No errors (healthy)
- **8-9**: Low error rate (healthy)
- **6-7**: Moderate error rate (degraded)
- **4-5**: High error rate (degraded)
- **2-3**: Critical errors present (unhealthy)
- **1**: Data corruption detected (unreliable)

## Error Metrics

Track error patterns and recovery success:

```python
metrics = handler.error_metrics.get_error_summary()
# Returns:
# {
#     "total_errors": 100,
#     "error_breakdown": {
#         "network_failure": 45,
#         "database_failure": 20,
#         "validation_failure": 35
#     },
#     "recovery_success_rates": {
#         "retry": {"success_rate": 0.8, "total_attempts": 50},
#         "fallback": {"success_rate": 0.95, "total_attempts": 20}
#     }
# }
```

## Best Practices

### 1. Always Provide Context

```python
context = {
    "service_name": "IdentityService",
    "operation": "create_entity",
    "entity_id": entity_id,
    "user_id": user_id,
    "timestamp": datetime.now().isoformat()
}
```

### 2. Use Appropriate Error Messages

- Be specific about what failed
- Include relevant identifiers
- Avoid exposing sensitive information

### 3. Handle Academic Integrity Violations

Academic integrity violations are **never** auto-recovered:

```python
if "citation" in error_message and "fabrication" in error_message:
    # This will escalate immediately and not attempt recovery
    pass
```

### 4. Test Recovery Strategies

Always test recovery strategies in isolation:

```python
# Test recovery strategy
error = create_test_error()
success = await recovery_strategy(error)
assert success, "Recovery strategy failed"
```

## Migration Guide

### From Try/Except Blocks

Before:
```python
try:
    result = await operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise
```

After:
```python
@handle_errors("MyService", "operation")
async def operation():
    result = await do_work()
    return result
```

### From Custom Error Handling

Before:
```python
if error_type == "network":
    retry_count += 1
    if retry_count < 3:
        time.sleep(2 ** retry_count)
        continue
```

After:
```python
# Automatic retry with exponential backoff
# Handled by framework based on error classification
```

## Monitoring and Alerts

### Integration Points

1. **Logging**: All errors logged with structured format
2. **Metrics**: Prometheus-compatible metrics exported
3. **Alerts**: Integrates with alerting systems
4. **Dashboards**: Grafana dashboards for error trends

### Example Dashboard Queries

```sql
-- Error rate by category
SELECT category, COUNT(*) as count
FROM errors
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY category;

-- Recovery success rate
SELECT strategy, 
       SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*) as success_rate
FROM recovery_attempts
GROUP BY strategy;
```

## Testing

### Unit Testing Error Handling

```python
async def test_error_handling():
    handler = CentralizedErrorHandler()
    
    # Test error classification
    error = Exception("Network timeout")
    result = await handler.handle_error(error, {"service_name": "test"})
    assert result.category == ErrorCategory.NETWORK_FAILURE
    
    # Test recovery
    # ...
```

### Integration Testing

```python
async def test_service_error_handling():
    service = MyService()
    
    # Force an error condition
    with pytest.raises(Exception):
        await service.risky_operation(force_error=True)
    
    # Verify error was handled
    metrics = get_global_error_handler().error_metrics.get_error_summary()
    assert metrics["total_errors"] > 0
```

## Conclusion

The Unified Error Handling Framework provides:

- ✅ Consistent error classification across all services
- ✅ Automatic recovery strategies based on error type
- ✅ Comprehensive error tracking and metrics
- ✅ System health assessment from error patterns
- ✅ Academic integrity violation detection
- ✅ Escalation procedures for critical issues

This framework ensures that all 802+ error handling points in the codebase follow consistent patterns and provide proper recovery mechanisms.