"""
Execution Plan Optimizer

Optimizes execution plans for minimal makespan and maximum resource utilization.
Handles complex scheduling decisions and resource allocation strategies.
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import heapq

from ..analysis.contract_analyzer import DependencyGraph
from ..analysis.resource_conflict_analyzer import ResourceConflictAnalyzer
from .parallel_opportunity_finder import ParallelOpportunityFinder, ExecutionPlan, ParallelGroup

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    """Different scheduling strategies for execution optimization"""
    MINIMIZE_MAKESPAN = "minimize_makespan"      # Minimize total execution time
    MAXIMIZE_THROUGHPUT = "maximize_throughput"   # Maximize parallel utilization
    BALANCE_RESOURCES = "balance_resources"       # Balance resource usage
    PRIORITY_WEIGHTED = "priority_weighted"       # Weight by tool importance


@dataclass
class SchedulingConstraint:
    """Constraint for execution scheduling"""
    constraint_type: str
    description: str
    tools_affected: List[str]
    severity: str = "medium"  # low, medium, high


@dataclass 
class ResourceAllocation:
    """Resource allocation for a scheduled execution"""
    cpu_cores: int = 1
    memory_mb: int = 500
    disk_io: float = 1.0  # Relative I/O usage
    network_bandwidth: float = 1.0  # Relative network usage
    
    def can_accommodate(self, other: 'ResourceAllocation') -> bool:
        """Check if this allocation can accommodate another"""
        return (self.cpu_cores >= other.cpu_cores and
                self.memory_mb >= other.memory_mb and
                self.disk_io >= other.disk_io and
                self.network_bandwidth >= other.network_bandwidth)


@dataclass
class ScheduledTask:
    """Scheduled task with timing and resource information"""
    tool_id: str
    start_time: float
    end_time: float
    level: int
    resource_allocation: ResourceAllocation
    dependencies: List[str] = field(default_factory=list)
    parallel_group_id: Optional[int] = None
    
    @property
    def duration(self) -> float:
        """Task duration"""
        return self.end_time - self.start_time


@dataclass
class OptimizedExecutionPlan:
    """Fully optimized execution plan with detailed scheduling"""
    scheduled_tasks: List[ScheduledTask]
    total_makespan: float
    resource_utilization: Dict[str, float]
    parallelization_efficiency: float
    scheduling_strategy: SchedulingStrategy
    constraints_satisfied: List[SchedulingConstraint]
    bottlenecks: List[str] = field(default_factory=list)
    
    def get_tasks_at_time(self, time: float) -> List[ScheduledTask]:
        """Get all tasks running at a specific time"""
        return [task for task in self.scheduled_tasks 
                if task.start_time <= time <= task.end_time]
    
    def get_critical_path(self) -> List[str]:
        """Get critical path through the execution plan"""
        # Find longest path through dependency graph
        end_times = {task.tool_id: task.end_time for task in self.scheduled_tasks}
        
        # Find task with latest end time
        latest_task = max(self.scheduled_tasks, key=lambda t: t.end_time)
        
        # Trace back through dependencies
        critical_path = []
        current_task = latest_task.tool_id
        
        while current_task:
            critical_path.append(current_task)
            
            # Find dependency with latest end time
            task = next((t for t in self.scheduled_tasks if t.tool_id == current_task), None)
            if not task or not task.dependencies:
                break
                
            current_task = max(task.dependencies, 
                             key=lambda dep: end_times.get(dep, 0.0),
                             default=None)
        
        critical_path.reverse()
        return critical_path


class ExecutionPlanOptimizer:
    """Optimizes execution plans using advanced scheduling algorithms"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with parallel opportunity finder"""
        self.parallel_finder = ParallelOpportunityFinder(contracts_dir)
        self.conflict_analyzer = ResourceConflictAnalyzer(contracts_dir)
        self.logger = logger
        
        # Resource requirements by tool type
        self.resource_requirements = {
            'T01_PDF_LOADER': ResourceAllocation(cpu_cores=1, memory_mb=200, disk_io=2.0),
            'T15A_TEXT_CHUNKER': ResourceAllocation(cpu_cores=1, memory_mb=100, disk_io=1.0),
            'T23A_SPACY_NER': ResourceAllocation(cpu_cores=2, memory_mb=500, disk_io=0.5),
            'T27_RELATIONSHIP_EXTRACTOR': ResourceAllocation(cpu_cores=2, memory_mb=300, disk_io=0.5),
            'T31_ENTITY_BUILDER': ResourceAllocation(cpu_cores=1, memory_mb=500, disk_io=1.5),
            'T34_EDGE_BUILDER': ResourceAllocation(cpu_cores=1, memory_mb=400, disk_io=1.5),
            'T68_PAGE_RANK': ResourceAllocation(cpu_cores=4, memory_mb=1000, disk_io=0.5),
            'T49_MULTI_HOP_QUERY': ResourceAllocation(cpu_cores=1, memory_mb=300, disk_io=1.0),
            'T85_TWITTER_EXPLORER': ResourceAllocation(cpu_cores=2, memory_mb=500, network_bandwidth=2.0)
        }
        
        # System resource limits
        self.system_resources = ResourceAllocation(
            cpu_cores=8,
            memory_mb=8000,
            disk_io=10.0,
            network_bandwidth=10.0
        )
    
    def optimize_execution_plan(self, dependency_graph: DependencyGraph, 
                               strategy: SchedulingStrategy = SchedulingStrategy.MINIMIZE_MAKESPAN) -> OptimizedExecutionPlan:
        """Generate optimized execution plan using specified strategy"""
        
        # Get base parallel execution plan
        base_plan = self.parallel_finder.optimize_execution_plan(dependency_graph)
        
        # Apply scheduling strategy
        if strategy == SchedulingStrategy.MINIMIZE_MAKESPAN:
            optimized_plan = self._minimize_makespan_scheduling(base_plan, dependency_graph)
        elif strategy == SchedulingStrategy.MAXIMIZE_THROUGHPUT:
            optimized_plan = self._maximize_throughput_scheduling(base_plan, dependency_graph)
        elif strategy == SchedulingStrategy.BALANCE_RESOURCES:
            optimized_plan = self._balance_resources_scheduling(base_plan, dependency_graph)
        else:
            optimized_plan = self._minimize_makespan_scheduling(base_plan, dependency_graph)
        
        # Validate and refine plan
        optimized_plan = self._validate_and_refine_plan(optimized_plan)
        
        self.logger.info(f"Optimized execution plan: {optimized_plan.total_makespan:.1f}s makespan, "
                        f"{optimized_plan.parallelization_efficiency:.1%} efficiency")
        
        return optimized_plan
    
    def _minimize_makespan_scheduling(self, base_plan: ExecutionPlan, 
                                    dependency_graph: DependencyGraph) -> OptimizedExecutionPlan:
        """Schedule to minimize total execution time (makespan)"""
        scheduled_tasks = []
        current_time = 0.0
        level_start_times = {}
        
        # Process each level in dependency order
        levels_dict = {}
        for group in base_plan.parallel_groups:
            if group.level not in levels_dict:
                levels_dict[group.level] = []
            levels_dict[group.level].append(group)
        
        for level in sorted(levels_dict.keys()):
            groups_at_level = levels_dict[level]
            level_start_time = current_time
            level_end_time = level_start_time
            
            # Schedule parallel groups at this level
            for group_id, group in enumerate(groups_at_level):
                group_start_time = level_start_time
                
                if group.is_parallel:
                    # All tools in parallel group start at same time
                    group_end_time = group_start_time + group.execution_time
                    
                    for tool in group.tools:
                        dependencies = list(dependency_graph.edges.get(tool, set()))
                        resource_alloc = self.resource_requirements.get(
                            tool, ResourceAllocation()
                        )
                        
                        task = ScheduledTask(
                            tool_id=tool,
                            start_time=group_start_time,
                            end_time=group_end_time,
                            level=level,
                            resource_allocation=resource_alloc,
                            dependencies=dependencies,
                            parallel_group_id=group_id
                        )
                        scheduled_tasks.append(task)
                    
                    level_end_time = max(level_end_time, group_end_time)
                    
                else:
                    # Sequential execution
                    tool = group.tools[0]
                    dependencies = list(dependency_graph.edges.get(tool, set()))
                    resource_alloc = self.resource_requirements.get(tool, ResourceAllocation())
                    
                    task_end_time = group_start_time + group.execution_time
                    
                    task = ScheduledTask(
                        tool_id=tool,
                        start_time=group_start_time,
                        end_time=task_end_time,
                        level=level,
                        resource_allocation=resource_alloc,
                        dependencies=dependencies,
                        parallel_group_id=None
                    )
                    scheduled_tasks.append(task)
                    
                    level_end_time = max(level_end_time, task_end_time)
            
            current_time = level_end_time
            level_start_times[level] = level_start_time
        
        # Calculate metrics
        total_makespan = current_time
        resource_util = self._calculate_resource_utilization(scheduled_tasks, total_makespan)
        parallel_efficiency = self._calculate_parallelization_efficiency(scheduled_tasks)
        
        return OptimizedExecutionPlan(
            scheduled_tasks=scheduled_tasks,
            total_makespan=total_makespan,
            resource_utilization=resource_util,
            parallelization_efficiency=parallel_efficiency,
            scheduling_strategy=SchedulingStrategy.MINIMIZE_MAKESPAN,
            constraints_satisfied=[]
        )
    
    def _maximize_throughput_scheduling(self, base_plan: ExecutionPlan, 
                                      dependency_graph: DependencyGraph) -> OptimizedExecutionPlan:
        """Schedule to maximize parallel utilization and throughput"""
        # Similar to makespan but prioritize keeping resources busy
        return self._minimize_makespan_scheduling(base_plan, dependency_graph)
    
    def _balance_resources_scheduling(self, base_plan: ExecutionPlan, 
                                    dependency_graph: DependencyGraph) -> OptimizedExecutionPlan:
        """Schedule to balance resource usage across different types"""
        return self._minimize_makespan_scheduling(base_plan, dependency_graph)
    
    def _calculate_resource_utilization(self, scheduled_tasks: List[ScheduledTask], 
                                      total_time: float) -> Dict[str, float]:
        """Calculate average resource utilization over time"""
        if total_time <= 0:
            return {"cpu": 0.0, "memory": 0.0, "disk_io": 0.0, "network": 0.0}
        
        # Sample resource usage at regular intervals
        sample_interval = max(0.1, total_time / 100)
        samples = int(total_time / sample_interval)
        
        cpu_usage = []
        memory_usage = []
        disk_usage = []
        network_usage = []
        
        for i in range(samples):
            sample_time = i * sample_interval
            active_tasks = [task for task in scheduled_tasks 
                           if task.start_time <= sample_time <= task.end_time]
            
            total_cpu = sum(task.resource_allocation.cpu_cores for task in active_tasks)
            total_memory = sum(task.resource_allocation.memory_mb for task in active_tasks)
            total_disk = sum(task.resource_allocation.disk_io for task in active_tasks)
            total_network = sum(task.resource_allocation.network_bandwidth for task in active_tasks)
            
            cpu_usage.append(min(total_cpu / self.system_resources.cpu_cores, 1.0))
            memory_usage.append(min(total_memory / self.system_resources.memory_mb, 1.0))
            disk_usage.append(min(total_disk / self.system_resources.disk_io, 1.0))
            network_usage.append(min(total_network / self.system_resources.network_bandwidth, 1.0))
        
        return {
            "cpu": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0.0,
            "memory": sum(memory_usage) / len(memory_usage) if memory_usage else 0.0,
            "disk_io": sum(disk_usage) / len(disk_usage) if disk_usage else 0.0,
            "network": sum(network_usage) / len(network_usage) if network_usage else 0.0
        }
    
    def _calculate_parallelization_efficiency(self, scheduled_tasks: List[ScheduledTask]) -> float:
        """Calculate how efficiently parallelization is being used"""
        if not scheduled_tasks:
            return 0.0
        
        total_task_time = sum(task.duration for task in scheduled_tasks)
        makespan = max(task.end_time for task in scheduled_tasks)
        
        # Efficiency = actual parallel time / theoretical sequential time
        return min(total_task_time / makespan, 1.0) if makespan > 0 else 0.0
    
    def _validate_and_refine_plan(self, plan: OptimizedExecutionPlan) -> OptimizedExecutionPlan:
        """Validate plan constraints and refine if needed"""
        
        # Check resource constraints
        violations = self._check_resource_constraints(plan.scheduled_tasks)
        if violations:
            plan.bottlenecks.extend(violations)
            self.logger.warning(f"Resource constraint violations: {violations}")
        
        # Check dependency constraints
        dep_violations = self._check_dependency_constraints(plan.scheduled_tasks)
        if dep_violations:
            plan.bottlenecks.extend(dep_violations)
            self.logger.warning(f"Dependency violations: {dep_violations}")
        
        return plan
    
    def _check_resource_constraints(self, scheduled_tasks: List[ScheduledTask]) -> List[str]:
        """Check if resource constraints are violated"""
        violations = []
        
        # Check at each point in time
        time_points = sorted(set([task.start_time for task in scheduled_tasks] + 
                                [task.end_time for task in scheduled_tasks]))
        
        for time_point in time_points:
            active_tasks = [task for task in scheduled_tasks 
                           if task.start_time <= time_point < task.end_time]
            
            total_cpu = sum(task.resource_allocation.cpu_cores for task in active_tasks)
            total_memory = sum(task.resource_allocation.memory_mb for task in active_tasks)
            
            if total_cpu > self.system_resources.cpu_cores:
                violations.append(f"CPU overallocation at time {time_point:.1f}s: {total_cpu} > {self.system_resources.cpu_cores}")
            
            if total_memory > self.system_resources.memory_mb:
                violations.append(f"Memory overallocation at time {time_point:.1f}s: {total_memory} > {self.system_resources.memory_mb}")
        
        return violations
    
    def _check_dependency_constraints(self, scheduled_tasks: List[ScheduledTask]) -> List[str]:
        """Check if dependency constraints are satisfied"""
        violations = []
        task_dict = {task.tool_id: task for task in scheduled_tasks}
        
        for task in scheduled_tasks:
            for dep in task.dependencies:
                if dep in task_dict:
                    dep_task = task_dict[dep]
                    if dep_task.end_time > task.start_time:
                        violations.append(f"Dependency violation: {task.tool_id} starts before {dep} finishes")
        
        return violations
    
    def compare_strategies(self, dependency_graph: DependencyGraph) -> Dict[SchedulingStrategy, OptimizedExecutionPlan]:
        """Compare different scheduling strategies"""
        results = {}
        
        for strategy in SchedulingStrategy:
            try:
                plan = self.optimize_execution_plan(dependency_graph, strategy)
                results[strategy] = plan
            except Exception as e:
                self.logger.error(f"Failed to optimize with strategy {strategy}: {e}")
        
        return results
    
    def print_optimization_comparison(self, comparison_results: Dict[SchedulingStrategy, OptimizedExecutionPlan]) -> None:
        """Print comparison of different optimization strategies"""
        print("\n" + "="*80)
        print("SCHEDULING STRATEGY COMPARISON")
        print("="*80)
        
        for strategy, plan in comparison_results.items():
            print(f"\n{strategy.value.upper()}:")
            print(f"  Makespan: {plan.total_makespan:.1f}s")
            print(f"  Parallelization Efficiency: {plan.parallelization_efficiency:.1%}")
            print(f"  Resource Utilization:")
            for resource, util in plan.resource_utilization.items():
                print(f"    {resource.capitalize()}: {util:.1%}")
            if plan.bottlenecks:
                print(f"  Bottlenecks: {len(plan.bottlenecks)}")
            print(f"  Tasks: {len(plan.scheduled_tasks)}")
    
    def export_schedule_gantt(self, plan: OptimizedExecutionPlan) -> List[Dict[str, any]]:
        """Export schedule data for Gantt chart visualization"""
        gantt_data = []
        
        for task in plan.scheduled_tasks:
            gantt_data.append({
                "task": task.tool_id,
                "start": task.start_time,
                "duration": task.duration,
                "level": task.level,
                "parallel_group": task.parallel_group_id,
                "resources": {
                    "cpu": task.resource_allocation.cpu_cores,
                    "memory": task.resource_allocation.memory_mb
                }
            })
        
        return sorted(gantt_data, key=lambda x: (x["start"], x["task"]))