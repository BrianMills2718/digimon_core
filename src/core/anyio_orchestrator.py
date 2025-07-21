"""
AnyIO Orchestrator - Phase 2 Implementation

Migrates to AnyIO for structured concurrency and better async patterns.
"""

import anyio
from typing import List, Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
from src.core.config_manager import get_config

class AnyIOOrchestrator:
    """AnyIO-based orchestrator for structured concurrency."""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.config = get_config()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_stats = {
            'completed': 0,
            'failed': 0,
            'cancelled': 0,
            'total_execution_time': 0
        }
    
    async def execute_tasks_parallel(self, tasks: List[Callable[[], Awaitable[Any]]]) -> List[Any]:
        """Execute tasks in parallel using AnyIO task groups."""
        
        start_time = anyio.current_time()
        results = []
        
        async with anyio.create_task_group() as task_group:
            for task in tasks:
                task_group.start_soon(self._execute_single_task, task, results)
        
        execution_time = anyio.current_time() - start_time
        self.task_stats['total_execution_time'] += execution_time
        
        # Log evidence
        with open('Evidence.md', 'a') as f:
            f.write(f"\n## AnyIO Parallel Execution Evidence\n")
            f.write(f"**Timestamp**: {datetime.now().isoformat()}\n")
            f.write(f"**Tasks Executed**: {len(tasks)}\n")
            f.write(f"**Execution Time**: {execution_time:.2f}s\n")
            f.write(f"**Successful**: {len(results)}\n")
            f.write(f"**Task Stats**: {self.task_stats}\n")
            f.write(f"\n")
        
        return results
    
    async def _execute_single_task(self, task: Callable[[], Awaitable[Any]], results: List[Any]):
        """Execute a single task and collect results."""
        try:
            result = await task()
            results.append(result)
            self.task_stats['completed'] += 1
        except anyio.get_cancelled_exc_class():
            self.task_stats['cancelled'] += 1
            raise
        except Exception as e:
            self.task_stats['failed'] += 1
            results.append({"error": str(e)})
    
    async def execute_with_resource_management(self, 
                                             resource_factory: Callable[[], Any],
                                             tasks: List[Callable[[Any], Awaitable[Any]]]) -> List[Any]:
        """Execute tasks with managed resources."""
        
        async with self.resource_manager(resource_factory) as resource:
            results = []
            
            async with anyio.create_task_group() as task_group:
                for task in tasks:
                    task_group.start_soon(self._execute_with_resource, task, resource, results)
            
            return results
    
    async def resource_manager(self, resource_factory: Callable[[], Any]):
        """Context manager for resource lifecycle."""
        
        class ResourceManager:
            def __init__(self, factory):
                self.factory = factory
                self.resource = None
            
            async def __aenter__(self):
                self.resource = await anyio.to_thread.run_sync(self.factory)
                return self.resource
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if hasattr(self.resource, 'close'):
                    await anyio.to_thread.run_sync(self.resource.close)
        
        return ResourceManager(resource_factory)
    
    async def _execute_with_resource(self, task: Callable[[Any], Awaitable[Any]], resource: Any, results: List[Any]):
        """Execute task with managed resource."""
        try:
            result = await task(resource)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    
    async def rate_limited_execution(self, 
                                   tasks: List[Callable[[], Awaitable[Any]]],
                                   max_rate: float = 1.0) -> List[Any]:
        """Execute tasks with rate limiting."""
        
        results = []
        
        async with anyio.create_task_group() as task_group:
            limiter = anyio.CapacityLimiter(1)
            
            for task in tasks:
                task_group.start_soon(self._rate_limited_task, task, limiter, max_rate, results)
        
        return results
    
    async def _rate_limited_task(self, task: Callable[[], Awaitable[Any]], 
                               limiter: anyio.CapacityLimiter, 
                               max_rate: float, 
                               results: List[Any]):
        """Execute task with rate limiting."""
        async with limiter:
            await anyio.sleep(1.0 / max_rate)  # Rate limiting
            try:
                result = await task()
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task execution statistics."""
        return self.task_stats.copy()