"""
Parallel Orchestrator for Concurrent Agent Execution.

This orchestrator enables parallel execution of reasoning-enhanced agents
with proper resource management, synchronization, and result aggregation.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor

from .base import Orchestrator, Task, Result, TaskPriority
from .simple_orchestrator import SimpleSequentialOrchestrator
from .mcp_adapter import MCPToolAdapter

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes for parallel orchestration."""
    PARALLEL = "parallel"           # Full parallel execution
    BATCH = "batch"                 # Batch-based parallel execution
    PIPELINE = "pipeline"           # Pipelined parallel execution
    ADAPTIVE = "adaptive"           # Adaptive parallelism based on resources


@dataclass
class ParallelTask:
    """Enhanced task for parallel execution."""
    task: Task
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    can_parallelize: bool = True
    priority_boost: float = 0.0
    
    @property
    def effective_priority(self) -> float:
        """Calculate effective priority including boost."""
        base_priority = {
            TaskPriority.CRITICAL: 1.0,
            TaskPriority.HIGH: 0.8,
            TaskPriority.MEDIUM: 0.5,
            TaskPriority.LOW: 0.2
        }
        return base_priority.get(self.task.priority, 0.5) + self.priority_boost


@dataclass 
class ResourcePool:
    """Resource pool for managing parallel execution resources."""
    max_concurrent_agents: int = 5
    max_memory_mb: int = 2048
    max_reasoning_threads: int = 3
    available_agents: int = 5
    used_memory_mb: int = 0
    active_reasoning: int = 0
    
    def can_allocate(self, requirements: Dict[str, Any]) -> bool:
        """Check if resources can be allocated with validation."""
        if not requirements:
            return False
            
        required_agents = max(0, requirements.get("agents", 1))
        required_memory = max(0, requirements.get("memory_mb", 256))
        required_reasoning = max(0, requirements.get("reasoning_threads", 0))
        
        # Validate requirements don't exceed maximums
        if (required_agents > self.max_concurrent_agents or 
            required_memory > self.max_memory_mb or
            required_reasoning > self.max_reasoning_threads):
            return False
        
        return (
            self.available_agents >= required_agents and
            (self.used_memory_mb + required_memory) <= self.max_memory_mb and
            (self.active_reasoning + required_reasoning) <= self.max_reasoning_threads
        )
    
    def allocate(self, requirements: Dict[str, Any]) -> bool:
        """Allocate resources if available with logging."""
        if not self.can_allocate(requirements):
            logger.debug(f"Cannot allocate resources: {requirements}. Current state: agents={self.available_agents}, memory={self.used_memory_mb}MB, reasoning={self.active_reasoning}")
            return False
            
        # Perform allocation
        agents_needed = requirements.get("agents", 1)
        memory_needed = requirements.get("memory_mb", 256)
        reasoning_needed = requirements.get("reasoning_threads", 0)
        
        self.available_agents -= agents_needed
        self.used_memory_mb += memory_needed
        self.active_reasoning += reasoning_needed
        
        logger.debug(f"Allocated resources: agents={agents_needed}, memory={memory_needed}MB, reasoning={reasoning_needed}. Remaining: agents={self.available_agents}, memory={self.max_memory_mb - self.used_memory_mb}MB")
        return True
    
    def release(self, requirements: Dict[str, Any]) -> None:
        """Release allocated resources with validation."""
        if not requirements:
            return
            
        agents_to_release = requirements.get("agents", 1)
        memory_to_release = requirements.get("memory_mb", 256)
        reasoning_to_release = requirements.get("reasoning_threads", 0)
        
        # Release resources
        self.available_agents += agents_to_release
        self.used_memory_mb -= memory_to_release
        self.active_reasoning -= reasoning_to_release
        
        # Ensure we don't go negative or exceed maximums
        self.available_agents = min(max(0, self.available_agents), self.max_concurrent_agents)
        self.used_memory_mb = max(0, self.used_memory_mb)
        self.active_reasoning = max(0, self.active_reasoning)
        
        logger.debug(f"Released resources: agents={agents_to_release}, memory={memory_to_release}MB, reasoning={reasoning_to_release}. Available: agents={self.available_agents}, memory={self.max_memory_mb - self.used_memory_mb}MB")


class ParallelOrchestrator(SimpleSequentialOrchestrator):
    """
    Parallel orchestrator for concurrent agent execution.
    
    Extends SimpleSequentialOrchestrator with parallel execution capabilities,
    resource management, and advanced coordination features.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize parallel orchestrator.
        
        Args:
            config_path: Path to configuration file
        """
        super().__init__(config_path)
        
        # Parallel execution configuration
        parallel_config = self.config.get("parallel", {})
        self.execution_mode = ExecutionMode(parallel_config.get("execution_mode", "parallel"))
        self.max_parallel_tasks = parallel_config.get("max_parallel_tasks", 5)
        self.batch_size = parallel_config.get("batch_size", 3)
        self.enable_resource_management = parallel_config.get("enable_resource_management", True)
        self.enable_adaptive_parallelism = parallel_config.get("enable_adaptive_parallelism", True)
        
        # Resource management
        resource_config = parallel_config.get("resources", {})
        self.resource_pool = ResourcePool(
            max_concurrent_agents=resource_config.get("max_concurrent_agents", 5),
            max_memory_mb=resource_config.get("max_memory_mb", 2048),
            max_reasoning_threads=resource_config.get("max_reasoning_threads", 3)
        )
        
        # Execution tracking
        self._active_tasks: Set[str] = set()
        self._completed_tasks: Dict[str, Result] = {}
        self._task_dependencies: Dict[str, List[str]] = {}
        self._execution_semaphore = None
        
        # Thread pool for CPU-bound operations
        self._thread_pool = ThreadPoolExecutor(
            max_workers=parallel_config.get("max_worker_threads", 4)
        )
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize parallel orchestrator and dependencies."""
        # Initialize base orchestrator
        if not await super().initialize():
            return False
        
        # Initialize execution semaphore
        self._execution_semaphore = asyncio.Semaphore(self.max_parallel_tasks)
        
        self.logger.info(
            f"Parallel orchestrator initialized: mode={self.execution_mode.value}, "
            f"max_parallel={self.max_parallel_tasks}, resource_management={self.enable_resource_management}"
        )
        
        return True
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Result:
        """
        Process request with parallel execution capabilities and comprehensive monitoring.
        
        Args:
            request: User request string
            context: Optional initial context
            
        Returns:
            Result of parallel processing
        """
        start_time = time.time()
        self._current_workflow_id = str(uuid.uuid4())
        self._workflow_start_time = datetime.now()
        
        # Initialize performance metrics
        performance_metrics = {
            "workflow_id": self._current_workflow_id,
            "start_time": start_time,
            "request_length": len(request),
            "initial_resource_state": {
                "available_agents": self.resource_pool.available_agents,
                "used_memory_mb": self.resource_pool.used_memory_mb,
                "active_reasoning": self.resource_pool.active_reasoning
            }
        }
        
        try:
            # Validate request with timing
            validation_start = time.time()
            if not await self.validate_request(request):
                return Result(
                    success=False,
                    error="Invalid request - failed validation checks",
                    execution_time=time.time() - start_time,
                    metadata={"performance_metrics": performance_metrics}
                )
            performance_metrics["validation_time"] = time.time() - validation_start
            
            # Determine workflow and create parallel tasks
            workflow_start = time.time()
            workflow = self._determine_workflow(request)
            parallel_tasks = await self._create_parallel_tasks(workflow, request, context)
            performance_metrics["workflow_planning_time"] = time.time() - workflow_start
            performance_metrics["task_count"] = len(parallel_tasks)
            
            if not parallel_tasks:
                return Result(
                    success=False,
                    error="No executable tasks could be created from request",
                    execution_time=time.time() - start_time,
                    metadata={"performance_metrics": performance_metrics}
                )
            
            self.logger.info(
                f"Executing parallel workflow: {workflow['name']} with {len(parallel_tasks)} tasks (mode: {self.execution_mode.value})"
            )
            
            # Execute based on mode with timing
            execution_start = time.time()
            if self.execution_mode == ExecutionMode.PARALLEL:
                results = await self._execute_full_parallel(parallel_tasks)
            elif self.execution_mode == ExecutionMode.BATCH:
                results = await self._execute_batch_parallel(parallel_tasks)
            elif self.execution_mode == ExecutionMode.PIPELINE:
                results = await self._execute_pipeline_parallel(parallel_tasks)
            else:  # ADAPTIVE
                results = await self._execute_adaptive_parallel(parallel_tasks)
            
            performance_metrics["execution_time"] = time.time() - execution_start
            performance_metrics["successful_tasks"] = sum(1 for r in results if r.success)
            performance_metrics["failed_tasks"] = sum(1 for r in results if not r.success)
            
            # Compile final results
            aggregation_start = time.time()
            final_result = await self._aggregate_parallel_results(results, workflow, request)
            performance_metrics["aggregation_time"] = time.time() - aggregation_start
            performance_metrics["total_time"] = time.time() - start_time
            
            # Add performance metrics to result
            final_result.execution_time = performance_metrics["total_time"]
            if not final_result.metadata:
                final_result.metadata = {}
            final_result.metadata["performance_metrics"] = performance_metrics
            
            self.logger.info(
                f"Parallel workflow completed: {performance_metrics['successful_tasks']}/{performance_metrics['task_count']} tasks successful "
                f"in {performance_metrics['total_time']:.2f}s"
            )
            
            return final_result
            
        except asyncio.CancelledError:
            self.logger.warning(f"Parallel orchestration cancelled for workflow {self._current_workflow_id}")
            performance_metrics["cancellation_time"] = time.time() - start_time
            return Result(
                success=False,
                error="Parallel orchestration was cancelled",
                execution_time=time.time() - start_time,
                metadata={"performance_metrics": performance_metrics}
            )
        except Exception as e:
            self.logger.error(f"Parallel orchestration failed: {e}", exc_info=True)
            performance_metrics["error_time"] = time.time() - start_time
            performance_metrics["error_type"] = type(e).__name__
            return Result(
                success=False,
                error=f"Parallel orchestration failed: {str(e)}",
                execution_time=time.time() - start_time,
                metadata={"performance_metrics": performance_metrics}
            )
        finally:
            # Log final resource state
            final_resource_state = {
                "available_agents": self.resource_pool.available_agents,
                "used_memory_mb": self.resource_pool.used_memory_mb,
                "active_reasoning": self.resource_pool.active_reasoning
            }
            self.logger.debug(f"Final resource state: {final_resource_state}")
            
            # Clear execution state
            self._active_tasks.clear()
            self._completed_tasks.clear()
            self._task_dependencies.clear()
    
    async def _create_parallel_tasks(
        self, 
        workflow: Dict[str, Any], 
        request: str,
        context: Dict[str, Any] = None
    ) -> List[ParallelTask]:
        """Create parallel tasks from workflow definition."""
        parallel_tasks = []
        workflow_context = context or {}
        workflow_context["original_request"] = request
        workflow_context["workflow_id"] = self._current_workflow_id
        
        for i, step in enumerate(workflow["steps"]):
            # Create base task
            task = Task(
                task_id=f"{self._current_workflow_id}_step_{i+1}",
                task_type=step["task_type"],
                parameters=step.get("parameters", {}),
                context=workflow_context.copy(),
                timeout=step.get("timeout", 300),
                priority=TaskPriority[step.get("priority", "MEDIUM").upper()]
            )
            
            # Determine dependencies
            dependencies = []
            if step.get("depends_on"):
                # Explicit dependencies
                for dep_idx in step["depends_on"]:
                    dependencies.append(f"{self._current_workflow_id}_step_{dep_idx}")
            elif not step.get("can_parallelize", True):
                # Sequential dependency on previous step
                if i > 0:
                    dependencies.append(f"{self._current_workflow_id}_step_{i}")
            
            # Determine resource requirements
            agent_type = step["agent"]
            resource_requirements = self._estimate_resource_requirements(agent_type, task)
            
            # Create parallel task
            parallel_task = ParallelTask(
                task=task,
                dependencies=dependencies,
                resource_requirements=resource_requirements,
                can_parallelize=step.get("can_parallelize", True),
                priority_boost=step.get("priority_boost", 0.0)
            )
            
            parallel_tasks.append(parallel_task)
            self._task_dependencies[task.task_id] = dependencies
        
        return parallel_tasks
    
    def _estimate_resource_requirements(
        self, 
        agent_type: str, 
        task: Task
    ) -> Dict[str, Any]:
        """Estimate resource requirements for a task."""
        # Base requirements by agent type
        base_requirements = {
            "document": {"agents": 1, "memory_mb": 512, "reasoning_threads": 1},
            "analysis": {"agents": 1, "memory_mb": 256, "reasoning_threads": 1},
            "graph": {"agents": 1, "memory_mb": 1024, "reasoning_threads": 0},
            "insight": {"agents": 1, "memory_mb": 256, "reasoning_threads": 2}
        }
        
        requirements = base_requirements.get(agent_type, {
            "agents": 1, "memory_mb": 256, "reasoning_threads": 0
        })
        
        # Adjust based on task parameters
        if task.parameters.get("large_dataset"):
            requirements["memory_mb"] *= 2
        
        if task.parameters.get("enable_reasoning", True):
            requirements["reasoning_threads"] = max(1, requirements.get("reasoning_threads", 0))
        
        return requirements
    
    async def _execute_full_parallel(
        self, 
        parallel_tasks: List[ParallelTask]
    ) -> List[Tuple[ParallelTask, Result]]:
        """Execute all parallelizable tasks concurrently."""
        results = []
        
        # Group tasks by dependencies
        ready_tasks = [pt for pt in parallel_tasks if not pt.dependencies]
        waiting_tasks = [pt for pt in parallel_tasks if pt.dependencies]
        
        # Execute in waves
        while ready_tasks or waiting_tasks:
            # Execute ready tasks in parallel
            if ready_tasks:
                wave_results = await asyncio.gather(
                    *[self._execute_parallel_task(pt) for pt in ready_tasks],
                    return_exceptions=True
                )
                
                # Process results
                for pt, result in zip(ready_tasks, wave_results):
                    if isinstance(result, Exception):
                        error_result = Result(
                            success=False,
                            error=str(result),
                            task_id=pt.task.task_id
                        )
                        results.append((pt, error_result))
                    else:
                        results.append((pt, result))
                    
                    # Mark as completed
                    self._completed_tasks[pt.task.task_id] = result
                    self._active_tasks.discard(pt.task.task_id)
            
            # Check for newly ready tasks
            ready_tasks = []
            still_waiting = []
            
            for pt in waiting_tasks:
                if all(dep_id in self._completed_tasks for dep_id in pt.dependencies):
                    # All dependencies satisfied
                    ready_tasks.append(pt)
                else:
                    still_waiting.append(pt)
            
            waiting_tasks = still_waiting
            
            # Break if no progress can be made
            if not ready_tasks and waiting_tasks:
                self.logger.error("Deadlock detected in parallel execution")
                break
        
        return results
    
    async def _execute_batch_parallel(
        self, 
        parallel_tasks: List[ParallelTask]
    ) -> List[Tuple[ParallelTask, Result]]:
        """Execute tasks in batches."""
        results = []
        
        # Sort by priority
        sorted_tasks = sorted(
            parallel_tasks, 
            key=lambda pt: pt.effective_priority, 
            reverse=True
        )
        
        # Execute in batches
        for i in range(0, len(sorted_tasks), self.batch_size):
            batch = sorted_tasks[i:i + self.batch_size]
            
            batch_results = await asyncio.gather(
                *[self._execute_parallel_task(pt) for pt in batch],
                return_exceptions=True
            )
            
            for pt, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    error_result = Result(
                        success=False,
                        error=str(result),
                        task_id=pt.task.task_id
                    )
                    results.append((pt, error_result))
                else:
                    results.append((pt, result))
        
        return results
    
    async def _execute_pipeline_parallel(
        self, 
        parallel_tasks: List[ParallelTask]
    ) -> List[Tuple[ParallelTask, Result]]:
        """Execute tasks in a pipeline fashion."""
        results = []
        
        # Create pipeline stages based on dependencies
        stages = self._create_pipeline_stages(parallel_tasks)
        
        # Execute stages with overlap
        stage_tasks = []
        
        for stage_idx, stage in enumerate(stages):
            # Start executing current stage
            stage_future = asyncio.create_task(
                self._execute_pipeline_stage(stage, stage_idx)
            )
            stage_tasks.append((stage, stage_future))
            
            # Allow overlap between stages
            if stage_idx < len(stages) - 1:
                await asyncio.sleep(0.1)  # Small delay for pipeline effect
        
        # Collect all results
        for stage, stage_future in stage_tasks:
            stage_results = await stage_future
            results.extend(stage_results)
        
        return results
    
    async def _execute_adaptive_parallel(
        self, 
        parallel_tasks: List[ParallelTask]
    ) -> List[Tuple[ParallelTask, Result]]:
        """Execute with adaptive parallelism based on resource availability."""
        results = []
        pending_tasks = parallel_tasks.copy()
        active_futures = {}
        
        while pending_tasks or active_futures:
            # Check resource availability and start new tasks
            tasks_to_start = []
            
            for pt in pending_tasks[:]:
                # Check dependencies
                deps_satisfied = all(
                    dep_id in self._completed_tasks 
                    for dep_id in pt.dependencies
                )
                
                if not deps_satisfied:
                    continue
                
                # Check resources
                if self.enable_resource_management:
                    if self.resource_pool.can_allocate(pt.resource_requirements):
                        self.resource_pool.allocate(pt.resource_requirements)
                        tasks_to_start.append(pt)
                        pending_tasks.remove(pt)
                    else:
                        # Try with reduced requirements
                        reduced_reqs = self._reduce_requirements(pt.resource_requirements)
                        if self.resource_pool.can_allocate(reduced_reqs):
                            self.resource_pool.allocate(reduced_reqs)
                            pt.resource_requirements = reduced_reqs
                            tasks_to_start.append(pt)
                            pending_tasks.remove(pt)
                else:
                    # No resource management - just respect concurrency limit
                    if len(active_futures) < self.max_parallel_tasks:
                        tasks_to_start.append(pt)
                        pending_tasks.remove(pt)
            
            # Start new tasks
            for pt in tasks_to_start:
                future = asyncio.create_task(self._execute_parallel_task(pt))
                active_futures[future] = pt
            
            # Wait for at least one task to complete
            if active_futures:
                done, pending = await asyncio.wait(
                    active_futures.keys(), 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for future in done:
                    pt = active_futures.pop(future)
                    try:
                        result = await future
                        results.append((pt, result))
                        self._completed_tasks[pt.task.task_id] = result
                        
                        # Release resources
                        if self.enable_resource_management:
                            self.resource_pool.release(pt.resource_requirements)
                    except Exception as e:
                        error_result = Result(
                            success=False,
                            error=str(e),
                            task_id=pt.task.task_id
                        )
                        results.append((pt, error_result))
                        self._completed_tasks[pt.task.task_id] = error_result
                        
                        if self.enable_resource_management:
                            self.resource_pool.release(pt.resource_requirements)
            
            # Adaptive adjustment
            if self.enable_adaptive_parallelism:
                self._adjust_parallelism_level()
        
        return results
    
    async def _execute_parallel_task(self, parallel_task: ParallelTask) -> Result:
        """Execute a single task with resource management."""
        async with self._execution_semaphore:
            task = parallel_task.task
            agent_name = self._get_agent_for_task(task.task_type)
            
            if not agent_name:
                return Result(
                    success=False,
                    error=f"No agent available for task type: {task.task_type}",
                    task_id=task.task_id
                )
            
            agent = self.agents.get(agent_name)
            if not agent:
                return Result(
                    success=False,
                    error=f"Agent '{agent_name}' not found",
                    task_id=task.task_id
                )
            
            # Mark as active
            self._active_tasks.add(task.task_id)
            
            try:
                # Add dependency results to context
                if parallel_task.dependencies:
                    task.context = task.context or {}
                    task.context["dependency_results"] = {
                        dep_id: self._completed_tasks.get(dep_id)
                        for dep_id in parallel_task.dependencies
                    }
                
                # Execute task
                self.logger.debug(f"Executing parallel task: {task.task_id}")
                result = await agent.execute(task)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Parallel task execution failed: {e}")
                return Result(
                    success=False,
                    error=str(e),
                    task_id=task.task_id
                )
            finally:
                self._active_tasks.discard(task.task_id)
    
    def _get_agent_for_task(self, task_type: str) -> Optional[str]:
        """Determine which agent should handle a task type."""
        # Task type to agent mapping
        task_agent_mapping = {
            "document_processing": "document",
            "load_documents": "document",
            "text_chunking": "document",
            "entity_extraction": "analysis",
            "relationship_extraction": "analysis",
            "analysis": "analysis",
            "graph_building": "graph",
            "graph_query": "graph",
            "insight_generation": "insight",
            "query_processing": "insight"
        }
        
        return task_agent_mapping.get(task_type)
    
    def _create_pipeline_stages(
        self, 
        parallel_tasks: List[ParallelTask]
    ) -> List[List[ParallelTask]]:
        """Create pipeline stages based on task dependencies."""
        stages = []
        assigned = set()
        
        # Assign tasks to stages
        while len(assigned) < len(parallel_tasks):
            stage = []
            
            for pt in parallel_tasks:
                if pt.task.task_id in assigned:
                    continue
                
                # Check if all dependencies are in previous stages
                deps_satisfied = all(
                    dep_id in assigned or dep_id == pt.task.task_id
                    for dep_id in pt.dependencies
                )
                
                if deps_satisfied:
                    stage.append(pt)
            
            if not stage:
                # No progress - break to avoid infinite loop
                self.logger.warning("Could not create valid pipeline stages")
                # Add remaining tasks to final stage
                remaining = [pt for pt in parallel_tasks if pt.task.task_id not in assigned]
                if remaining:
                    stages.append(remaining)
                break
            
            stages.append(stage)
            for pt in stage:
                assigned.add(pt.task.task_id)
        
        return stages
    
    async def _execute_pipeline_stage(
        self, 
        stage: List[ParallelTask], 
        stage_idx: int
    ) -> List[Tuple[ParallelTask, Result]]:
        """Execute a single pipeline stage."""
        self.logger.debug(f"Executing pipeline stage {stage_idx + 1} with {len(stage)} tasks")
        
        results = await asyncio.gather(
            *[self._execute_parallel_task(pt) for pt in stage],
            return_exceptions=True
        )
        
        stage_results = []
        for pt, result in zip(stage, results):
            if isinstance(result, Exception):
                error_result = Result(
                    success=False,
                    error=str(result),
                    task_id=pt.task.task_id
                )
                stage_results.append((pt, error_result))
            else:
                stage_results.append((pt, result))
            
            self._completed_tasks[pt.task.task_id] = result
        
        return stage_results
    
    def _reduce_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce resource requirements for adaptive execution."""
        reduced = requirements.copy()
        
        # Reduce memory by 25%
        if "memory_mb" in reduced:
            reduced["memory_mb"] = int(reduced["memory_mb"] * 0.75)
        
        # Reduce reasoning threads but keep at least 1 if originally requested
        if "reasoning_threads" in reduced and reduced["reasoning_threads"] > 0:
            reduced["reasoning_threads"] = max(1, reduced["reasoning_threads"] - 1)
        
        return reduced
    
    def _adjust_parallelism_level(self):
        """Dynamically adjust parallelism based on system performance."""
        # Calculate resource utilization
        memory_utilization = self.resource_pool.used_memory_mb / self.resource_pool.max_memory_mb
        agent_utilization = (
            (self.resource_pool.max_concurrent_agents - self.resource_pool.available_agents) / 
            self.resource_pool.max_concurrent_agents
        )
        
        # Adjust maximum parallel tasks based on utilization
        if memory_utilization > 0.9 or agent_utilization > 0.9:
            # High utilization - reduce parallelism
            self.max_parallel_tasks = max(2, self.max_parallel_tasks - 1)
            self.logger.debug(f"Reduced parallelism to {self.max_parallel_tasks}")
        elif memory_utilization < 0.5 and agent_utilization < 0.5:
            # Low utilization - increase parallelism
            original_max = self.config.get("parallel", {}).get("max_parallel_tasks", 5)
            self.max_parallel_tasks = min(original_max, self.max_parallel_tasks + 1)
            self.logger.debug(f"Increased parallelism to {self.max_parallel_tasks}")
    
    async def _aggregate_parallel_results(
        self,
        task_results: List[Tuple[ParallelTask, Result]],
        workflow: Dict[str, Any],
        request: str
    ) -> Result:
        """Aggregate results from parallel execution."""
        # Sort results by task order
        sorted_results = sorted(
            task_results,
            key=lambda x: x[0].task.task_id
        )
        
        # Check overall success
        all_successful = all(
            result.success for _, result in sorted_results
            if not result.metadata or not result.metadata.get("optional", False)
        )
        
        # Compile execution statistics
        total_tasks = len(sorted_results)
        successful_tasks = sum(1 for _, result in sorted_results if result.success)
        failed_tasks = total_tasks - successful_tasks
        
        # Calculate parallel speedup
        sequential_time = sum(result.execution_time for _, result in sorted_results)
        parallel_time = max(result.execution_time for _, result in sorted_results) if sorted_results else 0
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
        
        # Aggregate data from all results
        aggregated_data = {
            "workflow_results": [result for _, result in sorted_results],
            "execution_stats": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "execution_mode": self.execution_mode.value,
                "speedup": round(speedup, 2),
                "sequential_time": round(sequential_time, 3),
                "parallel_time": round(parallel_time, 3)
            },
            "resource_usage": {
                "peak_memory_mb": self.resource_pool.max_memory_mb - min(
                    self.resource_pool.available_agents for _, _ in sorted_results
                ),
                "peak_agents": self.resource_pool.max_concurrent_agents - min(
                    self.resource_pool.available_agents for _, _ in sorted_results
                ),
                "peak_reasoning_threads": self.resource_pool.max_reasoning_threads
            }
        }
        
        # Extract key insights from results
        insights = self._extract_parallel_insights(sorted_results)
        if insights:
            aggregated_data["parallel_insights"] = insights
        
        # Create final result
        return Result(
            success=all_successful,
            data=aggregated_data,
            warnings=[
                f"Task {pt.task.task_id} failed: {result.error}"
                for pt, result in sorted_results
                if not result.success
            ],
            metadata={
                "orchestrator": "parallel",
                "workflow": workflow["name"],
                "original_request": request,
                "parallelism_achieved": speedup > 1.2
            }
        )
    
    def _extract_parallel_insights(
        self, 
        results: List[Tuple[ParallelTask, Result]]
    ) -> Dict[str, Any]:
        """Extract insights from parallel execution results."""
        insights = {
            "execution_patterns": [],
            "bottlenecks": [],
            "optimization_opportunities": []
        }
        
        # Analyze execution patterns
        reasoning_tasks = [
            (pt, r) for pt, r in results 
            if r.metadata and r.metadata.get("reasoning", {}).get("applied")
        ]
        
        if reasoning_tasks:
            insights["execution_patterns"].append({
                "pattern": "reasoning_utilization",
                "tasks_with_reasoning": len(reasoning_tasks),
                "average_confidence": sum(
                    r.metadata["reasoning"]["confidence"] 
                    for _, r in reasoning_tasks
                ) / len(reasoning_tasks)
            })
        
        # Identify bottlenecks
        slowest_task = max(results, key=lambda x: x[1].execution_time)
        if slowest_task[1].execution_time > 5.0:
            insights["bottlenecks"].append({
                "task_id": slowest_task[0].task.task_id,
                "execution_time": slowest_task[1].execution_time,
                "task_type": slowest_task[0].task.task_type
            })
        
        # Suggest optimizations
        if len(results) > 5 and self.execution_mode != ExecutionMode.ADAPTIVE:
            insights["optimization_opportunities"].append(
                "Consider using adaptive execution mode for better resource utilization"
            )
        
        return insights
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status including parallel execution metrics."""
        base_status = super().get_status()
        
        # Add parallel-specific status
        parallel_status = {
            "execution_mode": self.execution_mode.value,
            "max_parallel_tasks": self.max_parallel_tasks,
            "active_tasks": len(self._active_tasks),
            "completed_tasks": len(self._completed_tasks),
            "resource_pool": {
                "available_agents": self.resource_pool.available_agents,
                "used_memory_mb": self.resource_pool.used_memory_mb,
                "active_reasoning": self.resource_pool.active_reasoning,
                "utilization": {
                    "agents": f"{((self.resource_pool.max_concurrent_agents - self.resource_pool.available_agents) / self.resource_pool.max_concurrent_agents * 100):.1f}%",
                    "memory": f"{(self.resource_pool.used_memory_mb / self.resource_pool.max_memory_mb * 100):.1f}%",
                    "reasoning": f"{(self.resource_pool.active_reasoning / self.resource_pool.max_reasoning_threads * 100):.1f}%"
                }
            }
        }
        
        base_status.update(parallel_status)
        return base_status
    
    async def cleanup(self) -> None:
        """Cleanup orchestrator resources including thread pool."""
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
        
        # Clear execution state
        self._active_tasks.clear()
        self._completed_tasks.clear()
        self._task_dependencies.clear()
        
        # Cleanup base orchestrator
        await super().cleanup()
        
        self.logger.info("Parallel orchestrator cleaned up")