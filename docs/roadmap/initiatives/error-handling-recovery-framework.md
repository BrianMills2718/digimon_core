# Error Handling and Recovery Framework

**Status**: TENTATIVE PROPOSAL  
**Created**: 2025-01-29  
**Related**: System reliability and operational excellence  
**Priority**: HIGH - Essential for production readiness

## Overview

KGAS currently follows a fail-fast philosophy which is good for catching bugs but provides no recovery options. This framework adds comprehensive error handling while maintaining the fail-fast principle where appropriate.

## Design Principles

1. **Fail Fast for Programming Errors** - Catch bugs early in development
2. **Recover Gracefully for Operational Issues** - Handle transient failures
3. **Provide Context** - Every error includes actionable information
4. **Guide Recovery** - Suggest specific steps to resolve issues
5. **Learn from Failures** - Track patterns for improvement

## Error Taxonomy

### Critical Errors (Fail Fast)
- Configuration errors
- Schema violations  
- Data corruption
- Security breaches
- Unrecoverable state

### Recoverable Errors (Retry/Fallback)
- Network timeouts
- Service temporarily unavailable
- Resource constraints
- Rate limits exceeded
- Concurrent modification conflicts

### Degradable Errors (Partial Service)
- Optional service failures
- Non-critical feature errors
- Performance degradation
- Capacity limits reached

## Implementation Architecture

### Core Error Handler

```python
class KGASErrorHandler:
    """Central error handling with recovery strategies"""
    
    def __init__(self):
        self.recovery_strategies = {}
        self.error_metrics = ErrorMetrics()
        self.circuit_breakers = {}
        
    def handle_error(self, error, context):
        # Classify error
        error_type = self.classify_error(error)
        
        # Log with full context
        self.log_error(error, context, error_type)
        
        # Update metrics
        self.error_metrics.record(error_type, context)
        
        # Apply recovery strategy
        strategy = self.recovery_strategies.get(error_type)
        if strategy:
            return strategy.recover(error, context)
        else:
            # Default: fail with guidance
            raise KGASError(
                error=error,
                context=context,
                recovery_suggestions=self.suggest_recovery(error)
            )
```

### Recovery Strategies

```python
class RetryStrategy:
    """Retry with exponential backoff"""
    
    def __init__(self, max_attempts=3, base_delay=1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        
    def recover(self, error, context, operation):
        for attempt in range(self.max_attempts):
            try:
                return operation()
            except Exception as e:
                if attempt == self.max_attempts - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)

class FallbackStrategy:
    """Use alternative service or degraded mode"""
    
    def __init__(self, fallback_operation):
        self.fallback = fallback_operation
        
    def recover(self, error, context):
        logger.warning(f"Using fallback due to: {error}")
        return self.fallback(context)

class CircuitBreakerStrategy:
    """Prevent cascading failures"""
    
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
        
    def recover(self, error, context, operation):
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
            else:
                raise ServiceUnavailableError("Circuit breaker open")
                
        try:
            result = operation()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

### Context Collection

```python
class ErrorContext:
    """Rich context for debugging and recovery"""
    
    def __init__(self):
        self.operation = None
        self.user_input = None
        self.system_state = {}
        self.recent_operations = []
        self.resource_usage = {}
        
    def capture(self):
        return {
            'timestamp': datetime.now(),
            'operation': self.operation,
            'user_input': self._sanitize(self.user_input),
            'system_state': self._capture_state(),
            'recent_operations': self.recent_operations[-10:],
            'resource_usage': self._capture_resources(),
            'stack_trace': traceback.format_exc()
        }
```

### Recovery Guidance

```python
class RecoveryAdvisor:
    """Provides specific recovery suggestions"""
    
    def suggest_recovery(self, error_type, context):
        suggestions = {
            'ServiceUnavailable': [
                "Wait 30 seconds and retry",
                "Check service health at /health",
                "Use fallback service if available"
            ],
            'ResourceExhausted': [
                "Reduce batch size",
                "Wait for resources to free up",
                "Upgrade resource limits"
            ],
            'DataInconsistency': [
                "Run consistency check",
                "Restore from last checkpoint",
                "Contact support with error ID"
            ]
        }
        
        return suggestions.get(error_type, ["Check logs for details"])
```

## Integration Patterns

### Tool Integration

```python
class ToolErrorWrapper:
    """Wraps tools with error handling"""
    
    def __init__(self, tool, error_handler):
        self.tool = tool
        self.error_handler = error_handler
        
    def execute(self, *args, **kwargs):
        context = ErrorContext()
        context.operation = f"{self.tool.name}.execute"
        context.user_input = {'args': args, 'kwargs': kwargs}
        
        try:
            return self.tool.execute(*args, **kwargs)
        except Exception as e:
            return self.error_handler.handle_error(e, context)
```

### Service Integration

```python
class ResilientServiceManager:
    """Service manager with error recovery"""
    
    def get_service(self, service_name):
        try:
            return self._get_primary_service(service_name)
        except ServiceUnavailableError:
            # Try fallback
            fallback = self._get_fallback_service(service_name)
            if fallback:
                return fallback
            # Enter degraded mode
            return self._get_degraded_service(service_name)
```

## Checkpoint and Resume

### Workflow Checkpointing

```python
class WorkflowCheckpoint:
    """Saves workflow state for resume"""
    
    def __init__(self, storage):
        self.storage = storage
        
    def save_checkpoint(self, workflow_id, state):
        checkpoint = {
            'workflow_id': workflow_id,
            'timestamp': datetime.now(),
            'state': state,
            'completed_steps': state.completed_steps,
            'pending_steps': state.pending_steps,
            'partial_results': state.partial_results
        }
        self.storage.save(f"checkpoint_{workflow_id}", checkpoint)
        
    def resume_workflow(self, workflow_id):
        checkpoint = self.storage.load(f"checkpoint_{workflow_id}")
        if not checkpoint:
            raise NoCheckpointError(f"No checkpoint for {workflow_id}")
            
        # Validate checkpoint is still valid
        if self._is_expired(checkpoint):
            raise CheckpointExpiredError("Checkpoint too old")
            
        return WorkflowState.from_checkpoint(checkpoint)
```

### Progress Tracking

```python
class ProgressTracker:
    """Tracks long-running operation progress"""
    
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.completed_steps = 0
        self.current_step = None
        self.step_start_time = None
        
    def start_step(self, step_name):
        self.current_step = step_name
        self.step_start_time = time.time()
        self.emit_progress()
        
    def complete_step(self):
        self.completed_steps += 1
        step_duration = time.time() - self.step_start_time
        self.emit_progress(step_duration)
        
    def emit_progress(self, duration=None):
        progress = {
            'current_step': self.current_step,
            'completed': self.completed_steps,
            'total': self.total_steps,
            'percentage': (self.completed_steps / self.total_steps) * 100,
            'duration': duration
        }
        # Send to monitoring system
        self.send_progress_update(progress)
```

## Monitoring and Alerting

### Error Metrics

```python
class ErrorMetrics:
    """Tracks error patterns and rates"""
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_rates = {}
        self.alert_thresholds = {
            'ServiceUnavailable': 10,  # per minute
            'DataCorruption': 1,       # immediate alert
            'SecurityViolation': 1     # immediate alert
        }
        
    def record(self, error_type, context):
        self.error_counts[error_type] += 1
        
        # Calculate rate
        rate = self._calculate_rate(error_type)
        
        # Check thresholds
        if rate > self.alert_thresholds.get(error_type, float('inf')):
            self.trigger_alert(error_type, rate, context)
```

### Health Checks

```python
class SystemHealthCheck:
    """Comprehensive system health monitoring"""
    
    def check_health(self):
        health = {
            'status': 'healthy',
            'timestamp': datetime.now(),
            'components': {}
        }
        
        # Check each component
        for component in self.components:
            try:
                component_health = component.health_check()
                health['components'][component.name] = component_health
            except Exception as e:
                health['components'][component.name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health['status'] = 'degraded'
                
        return health
```

## Implementation Phases

### Phase 1: Core Framework (Days 1-3)
- Implement KGASErrorHandler
- Create error taxonomy
- Basic recovery strategies
- Context collection

### Phase 2: Integration (Days 4-6)
- Wrap all tools with error handling
- Update services with resilience
- Add circuit breakers
- Implement retries

### Phase 3: Checkpoint/Resume (Days 7-9)
- Workflow checkpointing
- Progress tracking
- State persistence
- Resume capability

### Phase 4: Monitoring (Days 10-12)
- Error metrics collection
- Health check system
- Alert configuration
- Dashboard creation

## Testing Strategy

### Unit Tests
- Each recovery strategy
- Error classification
- Context sanitization
- Checkpoint/resume

### Integration Tests
- End-to-end error flows
- Service failover
- Circuit breaker behavior
- Checkpoint recovery

### Chaos Testing
- Random service failures
- Network partitions
- Resource exhaustion
- Concurrent errors

## Success Criteria

1. **95%+ errors have recovery guidance**
2. **Transient failures retry successfully**
3. **Circuit breakers prevent cascades**
4. **All workflows resumable from checkpoint**
5. **Error patterns tracked and analyzed**

## Documentation Requirements

### Operational Runbook
- Common error scenarios
- Recovery procedures
- Escalation paths
- Monitoring guide

### Developer Guide
- Error handling patterns
- Adding new strategies
- Testing approaches
- Best practices

This framework transforms KGAS from a fragile fail-fast system to a resilient platform that can handle real-world operational challenges while maintaining data integrity and system reliability.