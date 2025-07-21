# AnyIO Structured Concurrency Architecture

*Status: Target Architecture*

## Overview

KGAS implements structured concurrency using AnyIO to provide reliable, predictable asynchronous operations with automatic resource management and cancellation.

## Design Principles

### Structured Concurrency Benefits
- **Automatic cancellation**: Task groups ensure all child tasks are cancelled if parent fails
- **Resource management**: Async context managers guarantee proper cleanup
- **Error propagation**: Exceptions bubble up predictably through task hierarchy
- **Deadlock prevention**: Structured approach prevents common async pitfalls

### Performance Characteristics
- **Rate limiting**: Built-in backpressure control prevents resource exhaustion
- **Monitoring**: Real-time performance tracking with evidence logging
- **Scalability**: Efficient handling of concurrent operations within single-node constraints

## Implementation Patterns

### Core Task Group Pattern
```python
async def execute_parallel_tasks(tasks: List[Task]) -> Dict[str, Any]:
    """Execute multiple tasks concurrently with structured cancellation."""
    results = {}
    
    async with anyio.create_task_group() as task_group:
        for task in tasks:
            task_group.start_soon(
                self._execute_single_task, 
                task, 
                results
            )
    
    return results

async def _execute_single_task(self, task: Task, results: Dict[str, Any]) -> None:
    """Execute single task with error handling and result storage."""
    try:
        result = await task.execute_async()
        results[task.id] = {
            "status": "success",
            "data": result,
            "execution_time": task.execution_time
        }
    except Exception as e:
        results[task.id] = {
            "status": "error", 
            "error": str(e),
            "execution_time": task.execution_time
        }
        # Error propagates to task group for structured handling
        raise
```

### Resource Management Pattern
```python
class AsyncResourceManager:
    """Manages async resources with automatic cleanup."""
    
    async def __aenter__(self):
        # Initialize async resources
        self.neo4j_session = await self.neo4j_driver.session()
        self.api_client = await self.create_api_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Guaranteed cleanup regardless of success/failure
        await self.neo4j_session.close()
        await self.api_client.close()

# Usage pattern
async def process_with_resources(data):
    async with AsyncResourceManager() as resources:
        return await resources.process(data)
    # Resources automatically cleaned up
```

### Rate Limiting and Backpressure
```python
class RateLimitedProcessor:
    """Implements rate limiting with AnyIO semaphores."""
    
    def __init__(self, max_concurrent: int = 10, rate_per_second: float = 5.0):
        self.semaphore = anyio.Semaphore(max_concurrent)
        self.rate_limiter = anyio.to_thread.current_default_thread_limiter()
        self.rate_per_second = rate_per_second
    
    async def process_batch(self, items: List[Any]) -> List[Any]:
        """Process items with rate limiting."""
        results = []
        
        async with anyio.create_task_group() as task_group:
            for item in items:
                task_group.start_soon(self._rate_limited_process, item, results)
        
        return results
    
    async def _rate_limited_process(self, item: Any, results: List[Any]) -> None:
        """Process single item with rate limiting."""
        async with self.semaphore:  # Limit concurrent operations
            await anyio.sleep(1.0 / self.rate_per_second)  # Rate limiting
            result = await self._process_item(item)
            results.append(result)
```

## Tool Contract Integration

### Async Tool Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class KGASTool(ABC):
    """Base tool contract with async support."""
    
    @abstractmethod
    async def execute_async(self, **kwargs) -> Dict[str, Any]:
        """Async execution method - primary interface."""
        pass
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Sync wrapper for backward compatibility."""
        return anyio.run(self.execute_async, **kwargs)
    
    async def validate_inputs(self, **kwargs) -> None:
        """Async input validation."""
        pass
    
    async def cleanup_resources(self) -> None:
        """Async resource cleanup."""
        pass

# Implementation example
class TextEmbedder(KGASTool):
    async def execute_async(self, texts: List[str]) -> Dict[str, Any]:
        """Embed texts using async API calls."""
        async with self.rate_limited_client() as client:
            embeddings = []
            
            async with anyio.create_task_group() as task_group:
                for text in texts:
                    task_group.start_soon(
                        self._embed_single_text, 
                        text, 
                        embeddings, 
                        client
                    )
            
            return {"embeddings": embeddings}
```

### Error Handling Strategy
```python
class StructuredErrorHandler:
    """Centralized error handling for async operations."""
    
    async def execute_with_recovery(self, operation, *args, **kwargs):
        """Execute operation with structured error handling."""
        try:
            return await operation(*args, **kwargs)
        except anyio.get_cancelled_exc_class():
            # Handle cancellation gracefully
            await self._cleanup_cancelled_operation(operation)
            raise
        except Exception as e:
            # Log error with context
            await self._log_error(operation, e, args, kwargs)
            
            # Attempt recovery if configured
            if hasattr(operation, 'recovery_strategy'):
                return await operation.recovery_strategy(e)
            
            # Fail fast - propagate error
            raise

    async def _cleanup_cancelled_operation(self, operation):
        """Clean up resources from cancelled operation."""
        if hasattr(operation, 'cleanup_resources'):
            await operation.cleanup_resources()
```

## Performance Monitoring

### Execution Tracking
```python
class PerformanceMonitor:
    """Monitor async operation performance."""
    
    async def track_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Track operation performance with evidence logging."""
        start_time = anyio.current_time()
        memory_start = self._get_memory_usage()
        
        try:
            result = await operation_func(*args, **kwargs)
            
            execution_time = anyio.current_time() - start_time
            memory_delta = self._get_memory_usage() - memory_start
            
            # Log performance evidence
            self.logger.info(f"{operation_name} completed", extra={
                "execution_time": execution_time,
                "memory_delta": memory_delta,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            execution_time = anyio.current_time() - start_time
            
            self.logger.error(f"{operation_name} failed", extra={
                "execution_time": execution_time,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            })
            
            raise
```

## Integration with Core Services

### Service Manager Pattern
```python
class AsyncServiceManager:
    """Manages core services with async lifecycle."""
    
    async def __aenter__(self):
        """Initialize all core services."""
        async with anyio.create_task_group() as task_group:
            # Initialize services concurrently
            task_group.start_soon(self._init_neo4j_service)
            task_group.start_soon(self._init_api_clients)
            task_group.start_soon(self._init_provenance_service)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Shutdown all services gracefully."""
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(self._shutdown_neo4j_service)
            task_group.start_soon(self._shutdown_api_clients)
            task_group.start_soon(self._shutdown_provenance_service)

# Usage in application
async def run_kgas_pipeline(workflow_config):
    """Run KGAS pipeline with structured concurrency."""
    async with AsyncServiceManager() as services:
        async with anyio.create_task_group() as task_group:
            # Execute workflow phases concurrently where possible
            for phase in workflow_config.phases:
                if phase.can_run_parallel:
                    task_group.start_soon(services.execute_phase, phase)
                else:
                    await services.execute_phase(phase)
```

## Migration Strategy

### Gradual Async Adoption
```python
class ToolAdapter:
    """Adapter for gradual migration to async tools."""
    
    def __init__(self, tool):
        self.tool = tool
        self.is_async = hasattr(tool, 'execute_async')
    
    async def execute(self, **kwargs):
        """Execute tool with async/sync compatibility."""
        if self.is_async:
            return await self.tool.execute_async(**kwargs)
        else:
            # Run sync tool in thread pool
            return await anyio.to_thread.run_sync(
                self.tool.execute, **kwargs
            )

# Enables gradual migration while maintaining compatibility
async def execute_mixed_tools(tools: List[KGASTool], inputs):
    """Execute mix of async and sync tools."""
    results = {}
    
    async with anyio.create_task_group() as task_group:
        for tool in tools:
            adapter = ToolAdapter(tool)
            task_group.start_soon(
                adapter.execute,
                **inputs[tool.id]
            )
    
    return results
```

## Benefits and Trade-offs

### Benefits
- **Predictable cancellation**: No orphaned tasks or resource leaks
- **Automatic cleanup**: Context managers ensure resource management
- **Clear error handling**: Structured exception propagation
- **Performance monitoring**: Built-in tracking and evidence generation
- **Scalability**: Efficient concurrent processing within node constraints

### Trade-offs
- **Learning curve**: Requires understanding of structured concurrency concepts
- **Migration effort**: Existing sync code needs adaptation
- **Complexity**: More complex than simple threading for simple cases

### Performance Expectations
- **40-50% pipeline performance improvement** through parallelization
- **Reduced resource usage** through structured cleanup
- **Better error recovery** through predictable cancellation
- **Enhanced monitoring** through async performance tracking

## Implementation Priority

### Phase 1: Core Infrastructure
1. **AsyncServiceManager**: Core service lifecycle management
2. **ToolAdapter**: Backward compatibility layer
3. **PerformanceMonitor**: Evidence-based performance tracking

### Phase 2: Tool Migration
1. **High-impact tools**: Text processing, API calls, embedding generation
2. **Workflow integration**: Pipeline orchestration with structured concurrency
3. **Error handling**: Robust error recovery and cleanup

### Phase 3: Optimization
1. **Rate limiting**: Advanced backpressure control
2. **Resource monitoring**: Real-time resource usage tracking
3. **Performance tuning**: Fine-tune concurrency parameters

This structured concurrency architecture provides the foundation for reliable, high-performance async operations while maintaining the fail-fast philosophy and evidence-based validation required by KGAS.