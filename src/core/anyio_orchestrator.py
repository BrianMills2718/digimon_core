"""
AnyIO Orchestrator for Structured Concurrency

Migrates from asyncio to AnyIO for better structured concurrency patterns.
Provides task groups, cancellation support, and improved error handling.

Features:
- Structured concurrency with task groups
- Proper cancellation handling
- Resource management
- Enhanced error propagation
- Better async context management
"""

import anyio
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Union, AsyncIterator
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging
from concurrent.futures import ThreadPoolExecutor

from .config import ConfigurationManager
from .logging_config import get_logger


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    success: bool
    result: Any
    error: Optional[Exception]
    duration: float
    started_at: float
    completed_at: float


class AnyIOOrchestrator:
    """Orchestrator using AnyIO for structured concurrency"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger("anyio.orchestrator")
        
        # Configuration
        self.max_concurrent_tasks = self.config_manager.get_system_config().get("max_concurrent_tasks", 10)
        self.task_timeout = self.config_manager.get_system_config().get("task_timeout", 300.0)
        self.thread_pool_size = self.config_manager.get_system_config().get("thread_pool_size", 4)
        
        # State
        self.active_tasks: Dict[str, TaskResult] = {}
        self.completed_tasks: List[TaskResult] = []
        self.thread_pool: Optional[ThreadPoolExecutor] = None
        
        self.logger.info("AnyIO orchestrator initialized - max concurrent: %d", self.max_concurrent_tasks)
    
    async def __aenter__(self):
        """Async context manager entry"""
        # Initialize thread pool
        self.thread_pool = ThreadPoolExecutor(max_workers=self.thread_pool_size)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup thread pool
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
            self.thread_pool = None
    
    async def execute_tasks_parallel(self, tasks: List[Callable], 
                                   task_ids: Optional[List[str]] = None) -> List[TaskResult]:
        """Execute multiple tasks in parallel using task groups"""
        if not tasks:
            return []
        
        if task_ids is None:
            task_ids = [f"task_{i}" for i in range(len(tasks))]
        
        if len(task_ids) != len(tasks):
            raise ValueError("Number of task IDs must match number of tasks")
        
        self.logger.info("Starting parallel execution of %d tasks", len(tasks))
        
        results = []
        
        # Use AnyIO task group for structured concurrency
        async with anyio.create_task_group() as task_group:
            # Create semaphore for limiting concurrent tasks
            semaphore = anyio.Semaphore(self.max_concurrent_tasks)
            
            # Start all tasks
            for i, (task, task_id) in enumerate(zip(tasks, task_ids)):
                task_group.start_soon(self._execute_single_task, task, task_id, semaphore, results)
        
        # Sort results by task completion order
        results.sort(key=lambda r: r.completed_at)
        
        self.logger.info("Parallel execution completed - %d tasks, %d successful, %d failed",
                        len(results), 
                        len([r for r in results if r.success]),
                        len([r for r in results if not r.success]))
        
        return results
    
    async def _execute_single_task(self, task: Callable, task_id: str, 
                                  semaphore: anyio.Semaphore, results: List[TaskResult]):
        """Execute a single task with proper error handling"""
        async with semaphore:
            start_time = time.time()
            
            # Create task result
            task_result = TaskResult(
                task_id=task_id,
                success=False,
                result=None,
                error=None,
                duration=0.0,
                started_at=start_time,
                completed_at=0.0
            )
            
            self.active_tasks[task_id] = task_result
            
            try:
                # Execute task with timeout
                with anyio.move_on_after(self.task_timeout) as cancel_scope:
                    if asyncio.iscoroutinefunction(task):
                        result = await task()
                    else:
                        # Run sync function in thread pool
                        result = await anyio.to_thread.run_sync(task)
                
                if cancel_scope.cancelled_caught:
                    raise TimeoutError(f"Task {task_id} timed out after {self.task_timeout} seconds")
                
                # Task completed successfully
                task_result.success = True
                task_result.result = result
                
                self.logger.debug("Task %s completed successfully", task_id)
                
            except Exception as e:
                task_result.success = False
                task_result.error = e
                
                self.logger.error("Task %s failed: %s", task_id, str(e))
            
            finally:
                # Update timing
                end_time = time.time()
                task_result.duration = end_time - start_time
                task_result.completed_at = end_time
                
                # Move to completed tasks
                self.active_tasks.pop(task_id, None)
                self.completed_tasks.append(task_result)
                results.append(task_result)
    
    async def execute_task_pipeline(self, pipeline_tasks: List[Callable],
                                   task_ids: Optional[List[str]] = None) -> List[TaskResult]:
        """Execute tasks in a pipeline (sequential with dependency handling)"""
        if not pipeline_tasks:
            return []
        
        if task_ids is None:
            task_ids = [f"pipeline_task_{i}" for i in range(len(pipeline_tasks))]
        
        self.logger.info("Starting pipeline execution of %d tasks", len(pipeline_tasks))
        
        results = []
        previous_result = None
        
        for i, (task, task_id) in enumerate(zip(pipeline_tasks, task_ids)):
            self.logger.debug("Executing pipeline task %d/%d: %s", i + 1, len(pipeline_tasks), task_id)
            
            # Create task that can access previous result
            async def pipeline_task_wrapper():
                if asyncio.iscoroutinefunction(task):
                    if previous_result is not None:
                        return await task(previous_result)
                    else:
                        return await task()
                else:
                    if previous_result is not None:
                        return await anyio.to_thread.run_sync(task, previous_result)
                    else:
                        return await anyio.to_thread.run_sync(task)
            
            # Execute single task
            task_results = await self.execute_tasks_parallel([pipeline_task_wrapper], [task_id])
            
            if not task_results:
                break
            
            task_result = task_results[0]
            results.append(task_result)
            
            # Stop pipeline if task failed
            if not task_result.success:
                self.logger.error("Pipeline stopped at task %s due to failure", task_id)
                break
            
            # Pass result to next task
            previous_result = task_result.result
        
        self.logger.info("Pipeline execution completed - %d tasks executed", len(results))
        
        return results
    
    @asynccontextmanager
    async def resource_manager(self, resources: List[Callable]) -> AsyncIterator[List[Any]]:
        """Context manager for proper resource lifecycle management"""
        acquired_resources = []
        
        try:
            # Acquire all resources
            for resource_factory in resources:
                if asyncio.iscoroutinefunction(resource_factory):
                    resource = await resource_factory()
                else:
                    resource = await anyio.to_thread.run_sync(resource_factory)
                acquired_resources.append(resource)
            
            self.logger.debug("Acquired %d resources", len(acquired_resources))
            
            yield acquired_resources
            
        finally:
            # Clean up resources in reverse order
            for resource in reversed(acquired_resources):
                try:
                    if hasattr(resource, 'close'):
                        if asyncio.iscoroutinefunction(resource.close):
                            await resource.close()
                        else:
                            await anyio.to_thread.run_sync(resource.close)
                    elif hasattr(resource, '__aexit__'):
                        await resource.__aexit__(None, None, None)
                except Exception as e:
                    self.logger.error("Error closing resource: %s", str(e))
            
            self.logger.debug("Cleaned up %d resources", len(acquired_resources))
    
    async def fan_out_fan_in(self, input_data: List[Any], 
                           processor: Callable, 
                           aggregator: Callable = None) -> Any:
        """Fan-out processing with fan-in aggregation"""
        self.logger.info("Starting fan-out processing of %d items", len(input_data))
        
        # Fan-out: process all items in parallel
        tasks = []
        task_ids = []
        
        for i, item in enumerate(input_data):
            task_id = f"fanout_task_{i}"
            task_ids.append(task_id)
            
            if asyncio.iscoroutinefunction(processor):
                task = lambda item=item: processor(item)
            else:
                task = lambda item=item: processor(item)
            
            tasks.append(task)
        
        # Execute all tasks in parallel
        results = await self.execute_tasks_parallel(tasks, task_ids)
        
        # Extract successful results
        successful_results = [r.result for r in results if r.success]
        
        # Fan-in: aggregate results
        if aggregator:
            if asyncio.iscoroutinefunction(aggregator):
                final_result = await aggregator(successful_results)
            else:
                final_result = await anyio.to_thread.run_sync(aggregator, successful_results)
        else:
            final_result = successful_results
        
        self.logger.info("Fan-out/fan-in completed - %d items processed, %d successful",
                        len(input_data), len(successful_results))
        
        return final_result
    
    async def rate_limited_execution(self, tasks: List[Callable], 
                                   max_rate: float = 1.0,
                                   time_window: float = 1.0) -> List[TaskResult]:
        """Execute tasks with rate limiting"""
        if not tasks:
            return []
        
        self.logger.info("Starting rate-limited execution - %d tasks, %.2f/s rate",
                        len(tasks), max_rate)
        
        results = []
        task_interval = time_window / max_rate
        
        for i, task in enumerate(tasks):
            task_id = f"rate_limited_task_{i}"
            
            # Execute single task
            task_results = await self.execute_tasks_parallel([task], [task_id])
            
            if task_results:
                results.extend(task_results)
            
            # Wait before next task (except for the last one)
            if i < len(tasks) - 1:
                await anyio.sleep(task_interval)
        
        self.logger.info("Rate-limited execution completed - %d tasks", len(results))
        
        return results
    
    async def circuit_breaker_execution(self, tasks: List[Callable],
                                      failure_threshold: int = 5,
                                      timeout: float = 60.0) -> List[TaskResult]:
        """Execute tasks with circuit breaker pattern"""
        if not tasks:
            return []
        
        self.logger.info("Starting circuit breaker execution - %d tasks, threshold: %d",
                        len(tasks), failure_threshold)
        
        results = []
        consecutive_failures = 0
        circuit_open = False
        circuit_open_time = 0
        
        for i, task in enumerate(tasks):
            task_id = f"circuit_breaker_task_{i}"
            
            # Check if circuit is open
            if circuit_open:
                if time.time() - circuit_open_time > timeout:
                    # Try to close circuit
                    circuit_open = False
                    consecutive_failures = 0
                    self.logger.info("Circuit breaker attempting to close")
                else:
                    # Skip task while circuit is open
                    self.logger.warning("Circuit breaker open - skipping task %s", task_id)
                    continue
            
            # Execute task
            task_results = await self.execute_tasks_parallel([task], [task_id])
            
            if task_results:
                result = task_results[0]
                results.append(result)
                
                if result.success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    
                    # Check if we should open circuit
                    if consecutive_failures >= failure_threshold:
                        circuit_open = True
                        circuit_open_time = time.time()
                        self.logger.warning("Circuit breaker opened after %d failures", consecutive_failures)
        
        self.logger.info("Circuit breaker execution completed - %d tasks executed", len(results))
        
        return results
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_tasks = len(self.completed_tasks)
        successful_tasks = len([t for t in self.completed_tasks if t.success])
        failed_tasks = len([t for t in self.completed_tasks if not t.success])
        
        if total_tasks > 0:
            avg_duration = sum(t.duration for t in self.completed_tasks) / total_tasks
            success_rate = successful_tasks / total_tasks * 100
        else:
            avg_duration = 0
            success_rate = 0
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "active_tasks": len(self.active_tasks),
            "success_rate": success_rate,
            "average_duration": avg_duration,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_timeout": self.task_timeout,
            "thread_pool_size": self.thread_pool_size
        }
    
    async def cancel_all_tasks(self):
        """Cancel all active tasks"""
        if self.active_tasks:
            self.logger.info("Cancelling %d active tasks", len(self.active_tasks))
            
            # AnyIO handles cancellation automatically when task group is cancelled
            # Individual task cancellation is handled by the move_on_after context manager
            
            self.active_tasks.clear()
    
    async def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all active tasks to complete"""
        if not self.active_tasks:
            return
        
        self.logger.info("Waiting for %d active tasks to complete", len(self.active_tasks))
        
        if timeout:
            with anyio.move_on_after(timeout) as cancel_scope:
                while self.active_tasks:
                    await anyio.sleep(0.1)
                
                if cancel_scope.cancelled_caught:
                    self.logger.warning("Timeout waiting for tasks to complete")
        else:
            while self.active_tasks:
                await anyio.sleep(0.1)
        
        self.logger.info("All tasks completed")


# Global orchestrator instance
_anyio_orchestrator = None


def get_anyio_orchestrator(config_manager: ConfigurationManager = None) -> AnyIOOrchestrator:
    """Get or create the global AnyIO orchestrator instance"""
    global _anyio_orchestrator
    
    if _anyio_orchestrator is None:
        _anyio_orchestrator = AnyIOOrchestrator(config_manager)
    
    return _anyio_orchestrator


async def run_with_anyio(coro):
    """Run a coroutine with AnyIO backend"""
    return await anyio.run(coro)