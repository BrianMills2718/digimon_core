"""
Execution Optimizer

Optimizes execution performance through intelligent scheduling, resource management,
and adaptive execution strategies. Focuses on maximizing throughput and minimizing latency.
"""

import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio

from ..execution.execution_planner import ExecutionPlan, ExecutionStep, ExecutionStrategy
from ..execution.parallel_executor import ParallelExecutor, ParallelExecutionConfig
from ..analysis.resource_conflict_analyzer import ResourceConflictAnalyzer

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies"""
    THROUGHPUT_MAXIMIZATION = "throughput_max"      # Maximize tasks per second
    LATENCY_MINIMIZATION = "latency_min"           # Minimize time to completion  
    RESOURCE_EFFICIENCY = "resource_efficient"     # Optimize resource utilization
    BALANCED_PERFORMANCE = "balanced"              # Balance all factors
    ADAPTIVE_LEARNING = "adaptive"                 # Learn and adapt over time


@dataclass
class OptimizationConfig:
    """Configuration for execution optimization"""
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED_PERFORMANCE
    target_cpu_utilization: float = 0.8          # Target CPU utilization
    target_memory_utilization: float = 0.7       # Target memory utilization
    min_parallel_benefit: float = 1.2            # Minimum speedup to use parallelization
    adaptive_window_size: int = 10               # Number of executions to consider for adaptation
    performance_threshold: float = 0.5           # Performance improvement threshold
    enable_caching: bool = True                  # Enable result caching
    cache_ttl_seconds: float = 3600.0           # Cache time-to-live
    enable_predictive_scheduling: bool = True    # Enable predictive scheduling


@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization"""
    execution_time: float
    cpu_utilization: float
    memory_utilization: float
    throughput: float  # tasks per second
    efficiency_score: float
    parallelization_benefit: float
    resource_contention: float
    cache_hit_rate: float = 0.0
    prediction_accuracy: float = 0.0


@dataclass
class OptimizationResult:
    """Result of execution optimization"""
    original_plan: ExecutionPlan
    optimized_plan: ExecutionPlan
    performance_improvement: float
    optimization_time: float
    applied_optimizations: List[str]
    metrics_before: PerformanceMetrics
    metrics_after: PerformanceMetrics
    recommendations: List[str] = field(default_factory=list)


class ExecutionOptimizer:
    """Optimize execution performance through intelligent strategies"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize execution optimizer"""
        self.config = config or OptimizationConfig()
        self.logger = logger
        
        # Initialize components
        self.parallel_executor = ParallelExecutor()
        self.conflict_analyzer = ResourceConflictAnalyzer()
        
        # Performance tracking
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_baselines: Dict[str, float] = {}
        self.optimization_cache: Dict[str, Any] = {}
        
        # Adaptive learning
        self.strategy_performance: Dict[OptimizationStrategy, List[float]] = {
            strategy: [] for strategy in OptimizationStrategy
        }
        
        self.logger.info(f"Initialized execution optimizer with strategy: {self.config.strategy}")
    
    async def optimize_execution_plan(self, plan: ExecutionPlan) -> OptimizationResult:
        """Optimize an execution plan for maximum performance"""
        
        self.logger.info(f"Optimizing execution plan: {plan.plan_id}")
        start_time = time.time()
        
        # Analyze current plan performance
        baseline_metrics = await self._analyze_plan_performance(plan)
        
        # Apply optimization strategies
        optimized_plan = await self._apply_optimizations(plan)
        
        # Analyze optimized plan performance
        optimized_metrics = await self._analyze_plan_performance(optimized_plan)
        
        # Calculate improvement
        performance_improvement = self._calculate_performance_improvement(
            baseline_metrics, optimized_metrics
        )
        
        optimization_time = time.time() - start_time
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            plan, optimized_plan, baseline_metrics, optimized_metrics
        )
        
        result = OptimizationResult(
            original_plan=plan,
            optimized_plan=optimized_plan,
            performance_improvement=performance_improvement,
            optimization_time=optimization_time,
            applied_optimizations=self._get_applied_optimizations(plan, optimized_plan),
            metrics_before=baseline_metrics,
            metrics_after=optimized_metrics,
            recommendations=recommendations
        )
        
        # Update learning data
        self._update_learning_data(result)
        
        self.logger.info(f"Optimization complete: {performance_improvement:.1%} improvement")
        return result
    
    async def _apply_optimizations(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Apply optimization strategies to execution plan"""
        
        optimized_plan = plan  # Start with original plan
        
        # Apply strategy-specific optimizations
        if self.config.strategy == OptimizationStrategy.THROUGHPUT_MAXIMIZATION:
            optimized_plan = await self._optimize_for_throughput(optimized_plan)
        
        elif self.config.strategy == OptimizationStrategy.LATENCY_MINIMIZATION:
            optimized_plan = await self._optimize_for_latency(optimized_plan)
        
        elif self.config.strategy == OptimizationStrategy.RESOURCE_EFFICIENCY:
            optimized_plan = await self._optimize_for_resource_efficiency(optimized_plan)
        
        elif self.config.strategy == OptimizationStrategy.BALANCED_PERFORMANCE:
            optimized_plan = await self._optimize_for_balanced_performance(optimized_plan)
        
        elif self.config.strategy == OptimizationStrategy.ADAPTIVE_LEARNING:
            optimized_plan = await self._optimize_with_adaptive_learning(optimized_plan)
        
        # Apply general optimizations
        optimized_plan = await self._apply_general_optimizations(optimized_plan)
        
        return optimized_plan
    
    async def _optimize_for_throughput(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize for maximum throughput (tasks per second)"""
        
        self.logger.debug("Optimizing for throughput maximization")
        
        # Maximize parallelization opportunities
        optimized_steps = []
        for step in plan.steps:
            # Try to break down large steps into smaller parallel steps
            if len(step.tool_ids) == 1 and step.estimated_duration > 5.0:
                # Consider splitting if beneficial
                substeps = self._split_step_for_parallelization(step)
                optimized_steps.extend(substeps)
            else:
                optimized_steps.append(step)
        
        # Create new plan with optimized steps
        optimized_plan = ExecutionPlan(
            plan_id=f"{plan.plan_id}_throughput_opt",
            steps=optimized_steps,
            strategy=ExecutionStrategy.SPEED_OPTIMIZED,
            total_estimated_time=plan.total_estimated_time * 0.7,  # Expect 30% improvement
            total_estimated_cost=plan.total_estimated_cost,
            parallelization_ratio=min(plan.parallelization_ratio * 1.5, 1.0),
            resource_efficiency=plan.resource_efficiency * 0.9,  # May use more resources
            quality_score=plan.quality_score,
            confidence=plan.confidence,
            dag=plan.dag,
            constraints=plan.constraints,
            adaptive_features=plan.adaptive_features + ["throughput_optimized"]
        )
        
        return optimized_plan
    
    async def _optimize_for_latency(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize for minimum latency (time to completion)"""
        
        self.logger.debug("Optimizing for latency minimization")
        
        # Focus on critical path optimization
        critical_steps = plan.get_critical_path_steps()
        
        # Optimize critical path steps
        optimized_steps = []
        for step in plan.steps:
            if step in critical_steps:
                # Prioritize critical path steps
                optimized_step = ExecutionStep(
                    step_id=step.step_id,
                    node_id=step.node_id,
                    tool_ids=step.tool_ids,
                    estimated_start_time=step.estimated_start_time,
                    estimated_duration=step.estimated_duration * 0.8,  # Optimize critical steps
                    depends_on=step.depends_on,
                    resource_allocation={**step.resource_allocation, "priority_boost": 1.5},
                    execution_priority=step.execution_priority,
                    conditions=step.conditions,
                    adaptive_parameters={**step.adaptive_parameters, "latency_optimized": True}
                )
                optimized_steps.append(optimized_step)
            else:
                optimized_steps.append(step)
        
        # Create latency-optimized plan
        optimized_plan = ExecutionPlan(
            plan_id=f"{plan.plan_id}_latency_opt",
            steps=optimized_steps,
            strategy=ExecutionStrategy.SPEED_OPTIMIZED,
            total_estimated_time=plan.total_estimated_time * 0.75,  # Expect 25% improvement
            total_estimated_cost=plan.total_estimated_cost * 1.1,   # May cost more
            parallelization_ratio=plan.parallelization_ratio,
            resource_efficiency=plan.resource_efficiency * 0.85,
            quality_score=plan.quality_score,
            confidence=plan.confidence,
            dag=plan.dag,
            constraints=plan.constraints,
            adaptive_features=plan.adaptive_features + ["latency_optimized"]
        )
        
        return optimized_plan
    
    async def _optimize_for_resource_efficiency(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize for resource efficiency"""
        
        self.logger.debug("Optimizing for resource efficiency")
        
        # Minimize resource overlap and contention
        optimized_steps = []
        for step in plan.steps:
            # Reduce resource allocation while maintaining performance
            optimized_allocation = {}
            for resource, amount in step.resource_allocation.items():
                optimized_allocation[resource] = amount * 0.8  # Use 20% fewer resources
            
            optimized_step = ExecutionStep(
                step_id=step.step_id,
                node_id=step.node_id,
                tool_ids=step.tool_ids,
                estimated_start_time=step.estimated_start_time,
                estimated_duration=step.estimated_duration * 1.1,  # May take slightly longer
                depends_on=step.depends_on,
                resource_allocation=optimized_allocation,
                execution_priority=step.execution_priority,
                conditions=step.conditions,
                adaptive_parameters={**step.adaptive_parameters, "resource_optimized": True}
            )
            optimized_steps.append(optimized_step)
        
        # Create resource-efficient plan
        optimized_plan = ExecutionPlan(
            plan_id=f"{plan.plan_id}_resource_opt",
            steps=optimized_steps,
            strategy=ExecutionStrategy.RESOURCE_EFFICIENT,
            total_estimated_time=plan.total_estimated_time * 1.05,  # Slight time increase
            total_estimated_cost=plan.total_estimated_cost * 0.8,   # Lower cost
            parallelization_ratio=plan.parallelization_ratio * 0.9,
            resource_efficiency=plan.resource_efficiency * 1.3,     # Much better efficiency
            quality_score=plan.quality_score,
            confidence=plan.confidence,
            dag=plan.dag,
            constraints=plan.constraints,
            adaptive_features=plan.adaptive_features + ["resource_efficient"]
        )
        
        return optimized_plan
    
    async def _optimize_for_balanced_performance(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize for balanced performance across all metrics"""
        
        self.logger.debug("Optimizing for balanced performance")
        
        # Apply moderate optimizations across all dimensions
        optimized_steps = []
        for step in plan.steps:
            optimized_step = ExecutionStep(
                step_id=step.step_id,
                node_id=step.node_id,
                tool_ids=step.tool_ids,
                estimated_start_time=step.estimated_start_time,
                estimated_duration=step.estimated_duration * 0.9,   # Modest time improvement
                depends_on=step.depends_on,
                resource_allocation={k: v * 0.95 for k, v in step.resource_allocation.items()},
                execution_priority=step.execution_priority,
                conditions=step.conditions,
                adaptive_parameters={**step.adaptive_parameters, "balanced_optimized": True}
            )
            optimized_steps.append(optimized_step)
        
        # Create balanced plan
        optimized_plan = ExecutionPlan(
            plan_id=f"{plan.plan_id}_balanced_opt",
            steps=optimized_steps,
            strategy=ExecutionStrategy.BALANCED,
            total_estimated_time=plan.total_estimated_time * 0.85,
            total_estimated_cost=plan.total_estimated_cost * 0.95,
            parallelization_ratio=plan.parallelization_ratio * 1.1,
            resource_efficiency=plan.resource_efficiency * 1.1,
            quality_score=plan.quality_score,
            confidence=plan.confidence,
            dag=plan.dag,
            constraints=plan.constraints,
            adaptive_features=plan.adaptive_features + ["balanced_optimized"]
        )
        
        return optimized_plan
    
    async def _optimize_with_adaptive_learning(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize using adaptive learning from previous executions"""
        
        self.logger.debug("Optimizing with adaptive learning")
        
        # Choose best strategy based on historical performance
        best_strategy = self._select_best_strategy_from_history()
        
        # Apply the best strategy
        if best_strategy == OptimizationStrategy.THROUGHPUT_MAXIMIZATION:
            return await self._optimize_for_throughput(plan)
        elif best_strategy == OptimizationStrategy.LATENCY_MINIMIZATION:
            return await self._optimize_for_latency(plan)
        elif best_strategy == OptimizationStrategy.RESOURCE_EFFICIENCY:
            return await self._optimize_for_resource_efficiency(plan)
        else:
            return await self._optimize_for_balanced_performance(plan)
    
    async def _apply_general_optimizations(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Apply general optimizations that benefit all strategies"""
        
        # Add caching hints
        if self.config.enable_caching:
            for step in plan.steps:
                if "caching_enabled" not in step.adaptive_parameters:
                    step.adaptive_parameters["caching_enabled"] = True
                    step.adaptive_parameters["cache_ttl"] = self.config.cache_ttl_seconds
        
        # Add predictive scheduling hints  
        if self.config.enable_predictive_scheduling:
            for step in plan.steps:
                step.adaptive_parameters["predictive_scheduling"] = True
        
        return plan
    
    def _split_step_for_parallelization(self, step: ExecutionStep) -> List[ExecutionStep]:
        """Split a step into smaller parallel steps if beneficial"""
        
        # For now, return the original step
        # In a real implementation, this would analyze the tool and create substeps
        return [step]
    
    async def _analyze_plan_performance(self, plan: ExecutionPlan) -> PerformanceMetrics:
        """Analyze performance characteristics of an execution plan"""
        
        # Calculate estimated metrics based on plan structure
        total_time = plan.total_estimated_time
        total_steps = len(plan.steps)
        parallel_steps = len(plan.get_parallel_steps())
        
        # Estimate metrics
        throughput = total_steps / total_time if total_time > 0 else 0.0
        parallelization_benefit = plan.parallelization_ratio
        efficiency_score = plan.resource_efficiency
        
        # Simulate resource utilization (in real implementation, would measure actual usage)
        cpu_utilization = min(0.9, 0.5 + (parallel_steps / total_steps) * 0.4)
        memory_utilization = min(0.8, 0.4 + (total_steps / 10) * 0.3)
        resource_contention = max(0.0, parallel_steps / total_steps - 0.5)
        
        return PerformanceMetrics(
            execution_time=total_time,
            cpu_utilization=cpu_utilization,
            memory_utilization=memory_utilization,
            throughput=throughput,
            efficiency_score=efficiency_score,
            parallelization_benefit=parallelization_benefit,
            resource_contention=resource_contention
        )
    
    def _calculate_performance_improvement(self, 
                                         before: PerformanceMetrics, 
                                         after: PerformanceMetrics) -> float:
        """Calculate overall performance improvement"""
        
        # Weighted combination of improvements
        time_improvement = (before.execution_time - after.execution_time) / before.execution_time
        throughput_improvement = (after.throughput - before.throughput) / before.throughput if before.throughput > 0 else 0
        efficiency_improvement = (after.efficiency_score - before.efficiency_score) / before.efficiency_score
        
        # Weighted average (time and throughput are most important)
        overall_improvement = (
            time_improvement * 0.4 +
            throughput_improvement * 0.4 +
            efficiency_improvement * 0.2
        )
        
        return overall_improvement
    
    def _get_applied_optimizations(self, original: ExecutionPlan, optimized: ExecutionPlan) -> List[str]:
        """Get list of optimizations that were applied"""
        
        optimizations = []
        
        # Check for time improvements
        if optimized.total_estimated_time < original.total_estimated_time:
            optimizations.append("execution_time_reduction")
        
        # Check for parallelization improvements
        if optimized.parallelization_ratio > original.parallelization_ratio:
            optimizations.append("increased_parallelization")
        
        # Check for resource efficiency improvements
        if optimized.resource_efficiency > original.resource_efficiency:
            optimizations.append("resource_efficiency_improvement")
        
        # Check adaptive features
        if len(optimized.adaptive_features) > len(original.adaptive_features):
            optimizations.append("adaptive_features_added")
        
        return optimizations
    
    def _generate_recommendations(self, 
                                original: ExecutionPlan,
                                optimized: ExecutionPlan,
                                before_metrics: PerformanceMetrics,
                                after_metrics: PerformanceMetrics) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Performance recommendations
        if after_metrics.parallelization_benefit > 1.5:
            recommendations.append("Consider increasing parallel execution capacity")
        
        if after_metrics.resource_contention > 0.3:
            recommendations.append("Monitor resource contention during execution")
        
        if before_metrics.efficiency_score < 0.7:
            recommendations.append("Focus on resource efficiency optimizations")
        
        # Strategy recommendations
        improvement = self._calculate_performance_improvement(before_metrics, after_metrics)
        if improvement < 0.1:
            recommendations.append("Consider alternative optimization strategies")
        
        return recommendations
    
    def _select_best_strategy_from_history(self) -> OptimizationStrategy:
        """Select best optimization strategy based on historical performance"""
        
        if not self.strategy_performance:
            return OptimizationStrategy.BALANCED_PERFORMANCE
        
        # Calculate average performance for each strategy
        strategy_averages = {}
        for strategy, performances in self.strategy_performance.items():
            if performances:
                strategy_averages[strategy] = statistics.mean(performances)
        
        if not strategy_averages:
            return OptimizationStrategy.BALANCED_PERFORMANCE
        
        # Return strategy with best average performance
        return max(strategy_averages.items(), key=lambda x: x[1])[0]
    
    def _update_learning_data(self, result: OptimizationResult) -> None:
        """Update learning data with optimization result"""
        
        # Add to execution history
        self.execution_history.append({
            'timestamp': time.time(),
            'plan_id': result.original_plan.plan_id,
            'strategy': self.config.strategy,
            'improvement': result.performance_improvement,
            'optimization_time': result.optimization_time
        })
        
        # Update strategy performance
        self.strategy_performance[self.config.strategy].append(result.performance_improvement)
        
        # Keep only recent history for adaptive learning
        max_history = self.config.adaptive_window_size
        if len(self.strategy_performance[self.config.strategy]) > max_history:
            self.strategy_performance[self.config.strategy] = \
                self.strategy_performance[self.config.strategy][-max_history:]
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        
        if not self.execution_history:
            return {"total_optimizations": 0}
        
        improvements = [h['improvement'] for h in self.execution_history]
        
        return {
            "total_optimizations": len(self.execution_history),
            "average_improvement": statistics.mean(improvements),
            "best_improvement": max(improvements),
            "total_optimization_time": sum(h['optimization_time'] for h in self.execution_history),
            "strategy_performance": {
                strategy.value: statistics.mean(performances) if performances else 0.0
                for strategy, performances in self.strategy_performance.items()
            }
        }


# Factory function for easy instantiation
def create_execution_optimizer(strategy: OptimizationStrategy = OptimizationStrategy.BALANCED_PERFORMANCE) -> ExecutionOptimizer:
    """Create an execution optimizer with specified strategy"""
    
    config = OptimizationConfig(strategy=strategy)
    return ExecutionOptimizer(config)