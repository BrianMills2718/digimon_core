#!/usr/bin/env python3
"""
Parallel Processing Framework for Batch Document Analysis

Provides sophisticated parallel processing capabilities for large-scale document analysis,
including task distribution, load balancing, fault tolerance, progress tracking,
and performance optimization for multi-core document processing workflows.
"""

import logging
import asyncio
import threading
import multiprocessing as mp
import time
import psutil
import queue
from typing import (
    Dict, List, Optional, Any, Callable, Union, Iterator, 
    Tuple, TypeVar, Generic, Protocol
)
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import (
    ThreadPoolExecutor, ProcessPoolExecutor, 
    as_completed, Future, TimeoutError
)
from contextlib import asynccontextmanager, contextmanager
from abc import ABC, abstractmethod
from enum import Enum
import pickle
import traceback
import signal
import os
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class ProcessingStrategy(Enum):
    """Different parallel processing strategies"""
    THREAD_POOL = "thread_pool"
    PROCESS_POOL = "process_pool" 
    ASYNC_CONCURRENT = "async_concurrent"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class TaskResult:
    """Result of a parallel task execution"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    worker_id: Optional[str] = None
    memory_usage_mb: float = 0.0
    retry_count: int = 0
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelTask:
    """Task for parallel execution"""
    task_id: str
    function: Callable
    args: Tuple = ()
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: Optional[float] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = f"task_{int(time.time() * 1000000)}"


class TaskProcessor(Protocol):
    """Protocol for task processors"""
    
    def process(self, task: ParallelTask) -> TaskResult:
        """Process a single task"""
        ...


@dataclass
class ProcessingStats:
    """Statistics for parallel processing"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    average_execution_time: float = 0.0
    total_execution_time: float = 0.0
    throughput_tasks_per_second: float = 0.0
    peak_memory_usage_mb: float = 0.0
    active_workers: int = 0
    queue_size: int = 0
    cpu_utilization_percent: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    
    def update_completion(self, execution_time: float, memory_mb: float):
        """Update stats when a task completes"""
        self.completed_tasks += 1
        self.total_execution_time += execution_time
        
        if self.completed_tasks > 0:
            self.average_execution_time = self.total_execution_time / self.completed_tasks
        
        if memory_mb > self.peak_memory_usage_mb:
            self.peak_memory_usage_mb = memory_mb
        
        # Calculate throughput
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > 0:
            self.throughput_tasks_per_second = self.completed_tasks / elapsed_time


class TaskQueue:
    """Priority-based task queue with dependency management"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._queues = {
            TaskPriority.CRITICAL: deque(),
            TaskPriority.HIGH: deque(),
            TaskPriority.NORMAL: deque(),
            TaskPriority.LOW: deque()
        }
        self._task_map = {}  # task_id -> task
        self._dependencies = {}  # task_id -> set of dependency task_ids
        self._dependents = defaultdict(set)  # task_id -> set of dependent task_ids
        self._completed_tasks = set()
        self._lock = threading.RLock()
    
    def add_task(self, task: ParallelTask) -> bool:
        """Add task to queue"""
        with self._lock:
            if len(self._task_map) >= self.max_size:
                logger.warning(f"Task queue is full ({self.max_size} tasks)")
                return False
            
            # Check for circular dependencies
            if self._has_circular_dependency(task):
                logger.error(f"Circular dependency detected for task {task.task_id}")
                return False
            
            # Store task
            self._task_map[task.task_id] = task
            
            # Set up dependencies
            if task.dependencies:
                self._dependencies[task.task_id] = set(task.dependencies)
                for dep_id in task.dependencies:
                    self._dependents[dep_id].add(task.task_id)
            
            # Add to appropriate queue if ready
            if self._is_task_ready(task):
                self._queues[task.priority].append(task.task_id)
            
            return True
    
    def get_next_task(self) -> Optional[ParallelTask]:
        """Get next ready task by priority"""
        with self._lock:
            # Check queues in priority order
            for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                           TaskPriority.NORMAL, TaskPriority.LOW]:
                queue = self._queues[priority]
                
                while queue:
                    task_id = queue.popleft()
                    task = self._task_map.get(task_id)
                    
                    if task and self._is_task_ready(task):
                        return task
            
            return None
    
    def mark_task_completed(self, task_id: str):
        """Mark task as completed and unlock dependent tasks"""
        with self._lock:
            self._completed_tasks.add(task_id)
            
            # Check if any dependent tasks are now ready
            for dependent_id in self._dependents.get(task_id, set()):
                dependent_task = self._task_map.get(dependent_id)
                if dependent_task and self._is_task_ready(dependent_task):
                    # Add to appropriate priority queue
                    self._queues[dependent_task.priority].append(dependent_id)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from queue"""
        with self._lock:
            if task_id not in self._task_map:
                return False
            
            # Remove from all queues
            for queue in self._queues.values():
                if task_id in queue:
                    queue.remove(task_id)
            
            # Clean up dependencies
            task = self._task_map[task_id]
            if task.dependencies:
                for dep_id in task.dependencies:
                    self._dependents[dep_id].discard(task_id)
            
            del self._task_map[task_id]
            self._dependencies.pop(task_id, None)
            self._dependents.pop(task_id, None)
            
            return True
    
    def _is_task_ready(self, task: ParallelTask) -> bool:
        """Check if task dependencies are satisfied"""
        if not task.dependencies:
            return True
        
        return all(dep_id in self._completed_tasks for dep_id in task.dependencies)
    
    def _has_circular_dependency(self, task: ParallelTask) -> bool:
        """Check for circular dependencies"""
        if not task.dependencies:
            return False
        
        visited = set()
        
        def dfs(task_id: str, path: set) -> bool:
            if task_id in path:
                return True  # Circular dependency found
            
            if task_id in visited:
                return False
            
            visited.add(task_id)
            path.add(task_id)
            
            # Check dependencies of this task
            deps = self._dependencies.get(task_id, set())
            for dep_id in deps:
                if dfs(dep_id, path):
                    return True
            
            path.remove(task_id)
            return False
        
        return dfs(task.task_id, set())
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self._lock:
            return {
                "total_tasks": len(self._task_map),
                "completed_tasks": len(self._completed_tasks),
                "pending_by_priority": {
                    priority.name: len(queue) 
                    for priority, queue in self._queues.items()
                },
                "tasks_with_dependencies": len(self._dependencies),
                "max_size": self.max_size
            }


class WorkerPool:
    """Manages a pool of workers for parallel processing"""
    
    def __init__(self, 
                 strategy: ProcessingStrategy = ProcessingStrategy.THREAD_POOL,
                 max_workers: Optional[int] = None,
                 worker_timeout: float = 300.0):
        
        self.strategy = strategy
        self.worker_timeout = worker_timeout
        
        # Determine optimal worker count
        if max_workers is None:
            if strategy == ProcessingStrategy.PROCESS_POOL:
                max_workers = min(mp.cpu_count(), 8)  # Limit for memory reasons
            else:
                max_workers = min(mp.cpu_count() * 2, 16)  # More threads for I/O
        
        self.max_workers = max_workers
        self.executor = None
        self.active_futures = {}  # future -> task_id
        self.worker_stats = defaultdict(dict)
        self._initialize_executor()
        
        logger.info(f"WorkerPool initialized: {strategy.value}, {max_workers} workers")
    
    def _initialize_executor(self):
        """Initialize the appropriate executor"""
        if self.strategy == ProcessingStrategy.THREAD_POOL:
            self.executor = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="doc_processor"
            )
        
        elif self.strategy == ProcessingStrategy.PROCESS_POOL:
            self.executor = ProcessPoolExecutor(
                max_workers=self.max_workers,
                mp_context=mp.get_context('spawn')  # More reliable than fork
            )
        
        else:
            raise ValueError(f"Unsupported strategy: {self.strategy}")
    
    def submit_task(self, task: ParallelTask, processor: Callable) -> Future:
        """Submit task for execution"""
        if not self.executor:
            raise RuntimeError("WorkerPool not initialized")
        
        # Wrap processor to handle task execution
        def execute_task():
            return self._execute_task_safely(task, processor)
        
        future = self.executor.submit(execute_task)
        self.active_futures[future] = task.task_id
        
        return future
    
    def _execute_task_safely(self, task: ParallelTask, processor: Callable) -> TaskResult:
        """Execute task with error handling and monitoring"""
        start_time = time.time()
        worker_id = f"{threading.current_thread().name}_{os.getpid()}"
        
        try:
            # Set up timeout if specified
            if task.timeout_seconds:
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(int(task.timeout_seconds))
            
            # Execute the actual task
            if hasattr(processor, '__call__'):
                if task.args and task.kwargs:
                    result = processor(*task.args, **task.kwargs)
                elif task.args:
                    result = processor(*task.args)
                elif task.kwargs:
                    result = processor(**task.kwargs)
                else:
                    result = processor()
            else:
                result = processor
            
            # Cancel timeout
            if task.timeout_seconds:
                signal.alarm(0)
            
            execution_time = time.time() - start_time
            memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)
            
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                worker_id=worker_id,
                memory_usage_mb=memory_usage,
                completed_at=datetime.now()
            )
            
        except TimeoutError:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="Task timeout",
                execution_time=time.time() - start_time,
                worker_id=worker_id
            )
            
        except Exception as e:
            error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=error_details,
                execution_time=time.time() - start_time,
                worker_id=worker_id
            )
        
        finally:
            # Always cancel timeout
            if task.timeout_seconds:
                signal.alarm(0)
    
    def _timeout_handler(self, signum, frame):
        """Handle task timeout"""
        raise TimeoutError("Task execution timed out")
    
    def get_completed_tasks(self) -> Iterator[Tuple[str, TaskResult]]:
        """Get completed tasks (non-blocking)"""
        completed_futures = []
        
        for future in as_completed(self.active_futures.keys(), timeout=0.1):
            try:
                task_id = self.active_futures[future]
                result = future.result()
                completed_futures.append((task_id, result))
                
            except Exception as e:
                task_id = self.active_futures[future]
                error_result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=str(e)
                )
                completed_futures.append((task_id, error_result))
        
        # Clean up completed futures
        for future in [f for f, _ in completed_futures]:
            if future in self.active_futures:
                del self.active_futures[future]
        
        return iter(completed_futures)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task"""
        for future, fid in self.active_futures.items():
            if fid == task_id:
                success = future.cancel()
                if success:
                    del self.active_futures[future]
                return success
        return False
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics"""
        return {
            "strategy": self.strategy.value,
            "max_workers": self.max_workers,
            "active_tasks": len(self.active_futures),
            "worker_timeout": self.worker_timeout,
            "executor_type": type(self.executor).__name__
        }
    
    def shutdown(self, wait: bool = True):
        """Shutdown worker pool"""
        if self.executor:
            self.executor.shutdown(wait=wait)
            self.executor = None
        
        self.active_futures.clear()


class ParallelProcessor:
    """Main parallel processing coordinator"""
    
    def __init__(self,
                 strategy: ProcessingStrategy = ProcessingStrategy.ADAPTIVE,
                 max_workers: Optional[int] = None,
                 max_queue_size: int = 10000,
                 worker_timeout: float = 300.0,
                 enable_monitoring: bool = True):
        
        self.strategy = strategy
        self.max_workers = max_workers
        self.worker_timeout = worker_timeout
        self.enable_monitoring = enable_monitoring
        
        # Initialize components
        self.task_queue = TaskQueue(max_queue_size)
        self.worker_pool = None
        self.stats = ProcessingStats()
        
        # Task tracking
        self.task_results = {}  # task_id -> TaskResult
        self.retry_queue = deque()
        self.failed_tasks = {}
        
        # Monitoring
        self._monitoring_active = False
        self._monitor_thread = None
        self._shutdown_event = threading.Event()
        
        # Initialize worker pool
        self._initialize_worker_pool()
        
        if enable_monitoring:
            self._start_monitoring()
        
        logger.info(f"ParallelProcessor initialized with {strategy.value} strategy")
    
    def _initialize_worker_pool(self):
        """Initialize worker pool based on strategy"""
        if self.strategy == ProcessingStrategy.ADAPTIVE:
            # Start with thread pool, can adapt later
            pool_strategy = ProcessingStrategy.THREAD_POOL
        else:
            pool_strategy = self.strategy
        
        self.worker_pool = WorkerPool(
            strategy=pool_strategy,
            max_workers=self.max_workers,
            worker_timeout=self.worker_timeout
        )
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_processing,
                daemon=True
            )
            self._monitor_thread.start()
    
    def _monitor_processing(self):
        """Background monitoring of processing status"""
        while self._monitoring_active and not self._shutdown_event.is_set():
            try:
                # Update CPU utilization
                self.stats.cpu_utilization_percent = psutil.cpu_percent(interval=1)
                
                # Update queue size
                queue_stats = self.task_queue.get_queue_stats()
                self.stats.queue_size = queue_stats['total_tasks'] - queue_stats['completed_tasks']
                
                # Update active workers
                pool_stats = self.worker_pool.get_pool_stats()
                self.stats.active_workers = pool_stats['active_tasks']
                
                # Process completed tasks
                self._process_completed_tasks()
                
                # Handle retries
                self._process_retry_queue()
                
                # Adaptive strategy adjustment
                if self.strategy == ProcessingStrategy.ADAPTIVE:
                    self._adjust_strategy_if_needed()
                
            except Exception as e:
                logger.error(f"Error in monitoring thread: {e}")
            
            # Wait with shutdown awareness
            self._shutdown_event.wait(timeout=5.0)
    
    def _process_completed_tasks(self):
        """Process completed tasks from worker pool"""
        for task_id, result in self.worker_pool.get_completed_tasks():
            self.task_results[task_id] = result
            
            if result.status == TaskStatus.COMPLETED:
                self.task_queue.mark_task_completed(task_id)
                self.stats.update_completion(result.execution_time, result.memory_usage_mb)
                
            elif result.status == TaskStatus.FAILED:
                self.stats.failed_tasks += 1
                task = self.task_queue._task_map.get(task_id)
                
                if task and result.retry_count < task.max_retries:
                    # Schedule for retry
                    retry_task = ParallelTask(
                        task_id=f"{task_id}_retry_{result.retry_count + 1}",
                        function=task.function,
                        args=task.args,
                        kwargs=task.kwargs,
                        priority=task.priority,
                        timeout_seconds=task.timeout_seconds,
                        max_retries=task.max_retries,
                        retry_delay=task.retry_delay,
                        metadata={**task.metadata, 'original_task_id': task_id, 'retry_count': result.retry_count + 1}
                    )
                    
                    # Add delay before retry
                    retry_time = time.time() + task.retry_delay * (2 ** result.retry_count)  # Exponential backoff
                    self.retry_queue.append((retry_time, retry_task))
                    
                else:
                    # Max retries exceeded
                    self.failed_tasks[task_id] = result
                    logger.error(f"Task {task_id} failed after {result.retry_count} retries: {result.error}")
    
    def _process_retry_queue(self):
        """Process tasks scheduled for retry"""
        current_time = time.time()
        
        while self.retry_queue:
            retry_time, retry_task = self.retry_queue[0]
            
            if retry_time <= current_time:
                self.retry_queue.popleft()
                self.submit_task(retry_task)
                logger.info(f"Retrying task {retry_task.task_id}")
            else:
                break  # Queue is ordered, no more ready tasks
    
    def _adjust_strategy_if_needed(self):
        """Adjust processing strategy based on performance metrics"""
        if not self.strategy == ProcessingStrategy.ADAPTIVE:
            return
        
        # Simple adaptive logic - could be more sophisticated
        cpu_usage = self.stats.cpu_utilization_percent
        avg_execution_time = self.stats.average_execution_time
        
        current_strategy = self.worker_pool.strategy
        new_strategy = current_strategy
        
        # If CPU usage is low and tasks are I/O bound (longer execution), prefer threads
        if cpu_usage < 50 and avg_execution_time > 5.0:
            new_strategy = ProcessingStrategy.THREAD_POOL
        
        # If CPU usage is high and tasks are CPU bound (shorter execution), prefer processes
        elif cpu_usage > 80 and avg_execution_time < 2.0:
            new_strategy = ProcessingStrategy.PROCESS_POOL
        
        # Switch strategies if beneficial
        if new_strategy != current_strategy:
            logger.info(f"Adapting strategy from {current_strategy.value} to {new_strategy.value}")
            self._switch_worker_pool_strategy(new_strategy)
    
    def _switch_worker_pool_strategy(self, new_strategy: ProcessingStrategy):
        """Switch worker pool to new strategy"""
        try:
            # Gracefully shutdown current pool
            old_pool = self.worker_pool
            old_pool.shutdown(wait=False)
            
            # Create new pool
            self.worker_pool = WorkerPool(
                strategy=new_strategy,
                max_workers=self.max_workers,
                worker_timeout=self.worker_timeout
            )
            
            logger.info(f"Successfully switched to {new_strategy.value} strategy")
            
        except Exception as e:
            logger.error(f"Failed to switch worker pool strategy: {e}")
    
    def submit_task(self, task: ParallelTask, processor: Optional[Callable] = None) -> bool:
        """Submit task for parallel processing"""
        try:
            # Use task's function if no processor provided
            if processor is None:
                processor = task.function
            
            if not processor:
                logger.error(f"No processor function provided for task {task.task_id}")
                return False
            
            # Add to task queue
            if not self.task_queue.add_task(task):
                logger.error(f"Failed to add task {task.task_id} to queue")
                return False
            
            self.stats.total_tasks += 1
            
            # Submit to worker pool if no dependencies
            if not task.dependencies:
                future = self.worker_pool.submit_task(task, processor)
                logger.debug(f"Submitted task {task.task_id} for execution")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit task {task.task_id}: {e}")
            return False
    
    def submit_batch(self, tasks: List[ParallelTask], 
                    processor: Optional[Callable] = None) -> Dict[str, bool]:
        """Submit batch of tasks for processing"""
        results = {}
        
        for task in tasks:
            results[task.task_id] = self.submit_task(task, processor)
        
        successful_tasks = sum(results.values())
        logger.info(f"Submitted batch: {successful_tasks}/{len(tasks)} tasks successful")
        
        return results
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete"""
        start_time = time.time()
        
        while True:
            queue_stats = self.task_queue.get_queue_stats()
            pending_tasks = queue_stats['total_tasks'] - queue_stats['completed_tasks']
            active_tasks = len(self.worker_pool.active_futures)
            
            if pending_tasks == 0 and active_tasks == 0 and len(self.retry_queue) == 0:
                logger.info("All tasks completed successfully")
                return True
            
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Timeout reached waiting for task completion")
                return False
            
            time.sleep(1.0)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task"""
        # Try to cancel in worker pool first
        cancelled_in_pool = self.worker_pool.cancel_task(task_id)
        
        # Remove from task queue
        removed_from_queue = self.task_queue.remove_task(task_id)
        
        # Remove from retry queue
        self.retry_queue = deque([
            (retry_time, task) for retry_time, task in self.retry_queue
            if task.task_id != task_id
        ])
        
        if cancelled_in_pool or removed_from_queue:
            self.stats.cancelled_tasks += 1
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    def cancel_all_tasks(self) -> int:
        """Cancel all pending and active tasks"""
        cancelled_count = 0
        
        # Cancel active tasks in worker pool
        for future in list(self.worker_pool.active_futures.keys()):
            if future.cancel():
                cancelled_count += 1
        
        # Clear task queue
        queue_stats = self.task_queue.get_queue_stats()
        pending_tasks = queue_stats['total_tasks'] - queue_stats['completed_tasks']
        cancelled_count += pending_tasks
        
        # Clear retry queue
        cancelled_count += len(self.retry_queue)
        self.retry_queue.clear()
        
        self.stats.cancelled_tasks += cancelled_count
        logger.info(f"Cancelled {cancelled_count} tasks")
        
        return cancelled_count
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result for specific task"""
        return self.task_results.get(task_id)
    
    def get_all_results(self) -> Dict[str, TaskResult]:
        """Get all task results"""
        return self.task_results.copy()
    
    def get_processing_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        # Update real-time stats
        self.stats.total_tasks = len(self.task_queue._task_map)
        self.stats.queue_size = self.task_queue.get_queue_stats()['total_tasks'] - self.task_queue.get_queue_stats()['completed_tasks']
        self.stats.active_workers = len(self.worker_pool.active_futures) if self.worker_pool else 0
        
        return self.stats
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive processing status"""
        stats = self.get_processing_stats()
        queue_stats = self.task_queue.get_queue_stats()
        pool_stats = self.worker_pool.get_pool_stats() if self.worker_pool else {}
        
        return {
            "processing_stats": {
                "total_tasks": stats.total_tasks,
                "completed_tasks": stats.completed_tasks,
                "failed_tasks": stats.failed_tasks,
                "cancelled_tasks": stats.cancelled_tasks,
                "success_rate": (stats.completed_tasks / max(1, stats.total_tasks)) * 100,
                "average_execution_time": stats.average_execution_time,
                "throughput_tasks_per_second": stats.throughput_tasks_per_second,
                "peak_memory_usage_mb": stats.peak_memory_usage_mb,
                "cpu_utilization_percent": stats.cpu_utilization_percent
            },
            "queue_stats": queue_stats,
            "worker_pool_stats": pool_stats,
            "retry_queue_size": len(self.retry_queue),
            "failed_tasks_count": len(self.failed_tasks),
            "configuration": {
                "strategy": self.strategy.value,
                "max_workers": self.max_workers,
                "worker_timeout": self.worker_timeout,
                "monitoring_enabled": self.enable_monitoring
            }
        }
    
    def export_results(self, export_path: str, 
                      include_failed: bool = True,
                      include_metadata: bool = True) -> bool:
        """Export processing results to file"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "processing_stats": self.get_processing_stats().__dict__,
                "successful_results": {},
                "failed_results": {} if include_failed else None
            }
            
            # Export successful results
            for task_id, result in self.task_results.items():
                if result.status == TaskStatus.COMPLETED:
                    result_data = {
                        "task_id": result.task_id,
                        "execution_time": result.execution_time,
                        "memory_usage_mb": result.memory_usage_mb,
                        "worker_id": result.worker_id,
                        "completed_at": result.completed_at.isoformat() if result.completed_at else None
                    }
                    
                    if include_metadata:
                        result_data["metadata"] = result.metadata
                        result_data["result"] = str(result.result)  # Convert to string for JSON
                    
                    export_data["successful_results"][task_id] = result_data
            
            # Export failed results if requested
            if include_failed:
                for task_id, result in self.failed_tasks.items():
                    export_data["failed_results"][task_id] = {
                        "task_id": result.task_id,
                        "error": result.error,
                        "retry_count": result.retry_count,
                        "execution_time": result.execution_time
                    }
            
            # Write to file
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w') as f:
                import json
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported processing results to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            return False
    
    def shutdown(self, wait: bool = True, timeout: float = 30.0):
        """Shutdown parallel processor"""
        logger.info("Shutting down ParallelProcessor")
        
        # Stop monitoring
        self._monitoring_active = False
        self._shutdown_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        # Cancel all tasks
        self.cancel_all_tasks()
        
        # Shutdown worker pool
        if self.worker_pool:
            self.worker_pool.shutdown(wait=wait)
        
        logger.info("ParallelProcessor shutdown complete")


# Factory functions for common use cases
def create_document_processor(max_workers: Optional[int] = None,
                            strategy: ProcessingStrategy = ProcessingStrategy.ADAPTIVE) -> ParallelProcessor:
    """Create processor optimized for document analysis"""
    
    return ParallelProcessor(
        strategy=strategy,
        max_workers=max_workers,
        max_queue_size=5000,
        worker_timeout=600.0,  # 10 minutes for document processing
        enable_monitoring=True
    )


def create_batch_processor(batch_size: int = 100,
                         max_workers: Optional[int] = None) -> ParallelProcessor:
    """Create processor optimized for batch processing"""
    
    return ParallelProcessor(
        strategy=ProcessingStrategy.PROCESS_POOL,  # Better for CPU-intensive batches
        max_workers=max_workers,
        max_queue_size=batch_size * 10,
        worker_timeout=300.0,
        enable_monitoring=True
    )


# Context manager for easy parallel processing
@contextmanager
def parallel_processing_context(strategy: ProcessingStrategy = ProcessingStrategy.ADAPTIVE,
                              max_workers: Optional[int] = None):
    """Context manager for parallel processing"""
    processor = ParallelProcessor(
        strategy=strategy,
        max_workers=max_workers,
        enable_monitoring=True
    )
    
    try:
        yield processor
    finally:
        processor.shutdown(wait=True, timeout=30.0)


# Example usage and testing
if __name__ == "__main__":
    def example_document_processor(document_path: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
        """Example document processing function"""
        import time
        import random
        
        # Simulate document processing
        processing_time = random.uniform(1.0, 5.0)
        time.sleep(processing_time)
        
        return {
            "document_path": document_path,
            "analysis_type": analysis_type,
            "processing_time": processing_time,
            "result": f"Processed {document_path} with {analysis_type} analysis",
            "confidence": random.uniform(0.7, 1.0)
        }
    
    def test_parallel_processing():
        # Test document processing
        with parallel_processing_context(ProcessingStrategy.THREAD_POOL, max_workers=4) as processor:
            
            # Create test tasks
            test_documents = [f"document_{i}.txt" for i in range(20)]
            tasks = []
            
            for i, doc_path in enumerate(test_documents):
                task = ParallelTask(
                    task_id=f"doc_task_{i}",
                    function=example_document_processor,
                    args=(doc_path,),
                    kwargs={"analysis_type": "sentiment"},
                    priority=TaskPriority.NORMAL,
                    timeout_seconds=10.0
                )
                tasks.append(task)
            
            # Submit batch
            print(f"Submitting {len(tasks)} tasks for processing...")
            submission_results = processor.submit_batch(tasks)
            
            print(f"Submitted: {sum(submission_results.values())}/{len(tasks)} tasks")
            
            # Wait for completion
            success = processor.wait_for_completion(timeout=60.0)
            
            if success:
                print("All tasks completed!")
                
                # Get results
                results = processor.get_all_results()
                successful_tasks = [r for r in results.values() if r.status == TaskStatus.COMPLETED]
                
                print(f"Results: {len(successful_tasks)} successful, {len(results) - len(successful_tasks)} failed")
                
                # Show statistics
                stats = processor.get_comprehensive_status()
                print(f"Processing Statistics:")
                print(f"  - Total execution time: {stats['processing_stats']['average_execution_time']:.2f}s")
                print(f"  - Throughput: {stats['processing_stats']['throughput_tasks_per_second']:.2f} tasks/sec")
                print(f"  - Peak memory: {stats['processing_stats']['peak_memory_usage_mb']:.1f}MB")
                print(f"  - Success rate: {stats['processing_stats']['success_rate']:.1f}%")
                
                # Export results
                processor.export_results("test_results.json")
                print("Results exported to test_results.json")
            
            else:
                print("Processing timed out or failed")
    
    test_parallel_processing()