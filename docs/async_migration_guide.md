# Async Migration Guide

This guide documents the migration from blocking `time.sleep()` calls to proper async patterns in the KGAS codebase.

## Summary of Changes

### Blocking Calls Found
- `src/core/api_rate_limiter.py` - 2 instances
- `src/core/error_handler.py` - 2 instances  
- `src/core/memory_manager.py` - 2 instances
- `src/core/api_auth_manager.py` - 2 instances
- `src/core/neo4j_manager.py` - 3 instances
- `src/core/error_tracker.py` - 2 instances
- `src/tools/phase1/t13_web_scraper_unified.py` - 2 instances

### New Async-Safe Implementations

1. **AsyncRateLimiter** (`src/core/async_rate_limiter.py`)
   - Replaces blocking rate limiter
   - Uses token bucket algorithm
   - Non-blocking with `asyncio.sleep()`
   - Backwards-compatible wrapper available

2. **AsyncErrorHandler** (`src/core/async_error_handler.py`)
   - Replaces blocking error handler
   - Non-blocking retry delays
   - Exponential backoff support
   - Async decorators

## Migration Steps

### 1. Rate Limiting

**Old (Blocking):**
```python
import time
time.sleep(min(sleep_time, 0.1))  # Blocks event loop!
```

**New (Async):**
```python
from src.core.async_rate_limiter import AsyncRateLimiter

limiter = AsyncRateLimiter()
await limiter.set_rate_limit("service_name", calls_per_minute=60)
await limiter.acquire("service_name")  # Non-blocking wait
```

### 2. Error Handling with Retry

**Old (Blocking):**
```python
for attempt in range(max_attempts):
    try:
        result = operation()
    except Exception:
        time.sleep(delay)  # Blocks!
```

**New (Async):**
```python
from src.core.async_error_handler import with_retry

@with_retry(max_attempts=3, delay=1.0)
async def operation():
    # Your async operation
    pass
```

### 3. General Sleep Replacement

**Old:**
```python
time.sleep(0.1)
```

**New:**
```python
await asyncio.sleep(0.1)
```

## Files Requiring Updates

### Priority 1: Core Services
- [ ] `api_rate_limiter.py` → Use `AsyncRateLimiter`
- [ ] `error_handler.py` → Use `AsyncErrorHandler`
- [ ] `neo4j_manager.py` → Replace sleep with asyncio.sleep

### Priority 2: Supporting Services  
- [ ] `memory_manager.py` → Async memory monitoring
- [ ] `api_auth_manager.py` → Async auth refresh
- [ ] `error_tracker.py` → Async error tracking

### Priority 3: Tools
- [ ] `t13_web_scraper_unified.py` → Async web scraping delays

## Testing Strategy

1. **Unit Tests**: Test each async component in isolation
2. **Integration Tests**: Test async components working together
3. **Performance Tests**: Verify no event loop blocking
4. **Load Tests**: Ensure system handles concurrent requests

## Verification Checklist

- [ ] No `time.sleep()` in async contexts
- [ ] All delays use `await asyncio.sleep()`
- [ ] Event loop remains responsive under load
- [ ] Concurrent operations execute in parallel
- [ ] Timeouts handled gracefully
- [ ] Backwards compatibility maintained

## Performance Benefits

1. **Non-blocking I/O**: Event loop stays responsive
2. **Better Concurrency**: Multiple operations in parallel
3. **Resource Efficiency**: Single thread handles many operations
4. **Improved Throughput**: No artificial blocking delays