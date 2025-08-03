"""
Dynamic Execution Planner

Plans optimal execution strategies based on question analysis and DAG structure.
Adapts execution plans based on context, resources, and performance requirements.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time

from .dag_builder import DynamicDAGBuilder, ExecutionDAG, DAGNode, NodeType
from ..nlp.advanced_intent_classifier import QuestionIntent
from ..nlp.question_complexity_analyzer import ComplexityLevel
from ..nlp.context_extractor import QuestionContext

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Different execution strategies"""
    SPEED_OPTIMIZED = "speed_optimized"         # Minimize total execution time
    QUALITY_OPTIMIZED = "quality_optimized"     # Maximize result quality
    RESOURCE_EFFICIENT = "resource_efficient"   # Minimize resource usage
    BALANCED = "balanced"                        # Balance speed, quality, resources
    ADAPTIVE = "adaptive"                        # Adapt based on question context


class ExecutionPriority(Enum):
    """Execution priorities"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ADAPTIVE = "adaptive"


@dataclass
class ExecutionConstraints:
    """Constraints for execution planning"""
    max_execution_time: Optional[float] = None
    max_memory_usage: Optional[float] = None
    max_parallel_tools: Optional[int] = None
    required_quality_threshold: Optional[float] = None
    available_resources: Dict[str, float] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStep:
    """Individual step in execution plan"""
    step_id: str
    node_id: str
    tool_ids: List[str]  # Single tool or multiple for parallel execution
    estimated_start_time: float
    estimated_duration: float
    depends_on: List[str] = field(default_factory=list)
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    execution_priority: ExecutionPriority = ExecutionPriority.MEDIUM
    conditions: List[str] = field(default_factory=list)
    adaptive_parameters: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def estimated_end_time(self) -> float:
        """Calculate estimated end time"""
        return self.estimated_start_time + self.estimated_duration
    
    @property
    def is_parallel_step(self) -> bool:
        """Check if this is a parallel execution step"""
        return len(self.tool_ids) > 1


@dataclass
class ExecutionPlan:
    """Complete execution plan with steps and metadata"""
    plan_id: str
    steps: List[ExecutionStep]
    strategy: ExecutionStrategy
    total_estimated_time: float
    total_estimated_cost: float
    parallelization_ratio: float
    resource_efficiency: float
    quality_score: float
    confidence: float
    dag: ExecutionDAG
    constraints: ExecutionConstraints
    adaptive_features: List[str] = field(default_factory=list)
    
    def get_steps_at_time(self, time_point: float) -> List[ExecutionStep]:
        """Get steps executing at a specific time"""
        return [step for step in self.steps 
                if step.estimated_start_time <= time_point <= step.estimated_end_time]
    
    def get_critical_path_steps(self) -> List[ExecutionStep]:
        """Get steps on the critical path"""
        critical_node_ids = set(self.dag.critical_path)
        return [step for step in self.steps if step.node_id in critical_node_ids]
    
    def get_parallel_steps(self) -> List[ExecutionStep]:
        """Get all parallel execution steps"""
        return [step for step in self.steps if step.is_parallel_step]


class DynamicExecutionPlanner:
    """Plans optimal execution strategies dynamically"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with DAG builder"""
        self.dag_builder = DynamicDAGBuilder(contracts_dir)
        self.logger = logger
        
        # Strategy configurations
        self.strategy_configs = {
            ExecutionStrategy.SPEED_OPTIMIZED: {
                'prioritize_parallelization': True,
                'quality_threshold': 0.7,
                'resource_limit_factor': 1.5,
                'time_weight': 1.0,
                'quality_weight': 0.3
            },
            ExecutionStrategy.QUALITY_OPTIMIZED: {
                'prioritize_parallelization': False,
                'quality_threshold': 0.95,
                'resource_limit_factor': 2.0,
                'time_weight': 0.3,
                'quality_weight': 1.0
            },
            ExecutionStrategy.RESOURCE_EFFICIENT: {
                'prioritize_parallelization': False,
                'quality_threshold': 0.8,
                'resource_limit_factor': 0.8,
                'time_weight': 0.5,
                'quality_weight': 0.5
            },
            ExecutionStrategy.BALANCED: {
                'prioritize_parallelization': True,
                'quality_threshold': 0.85,
                'resource_limit_factor': 1.2,
                'time_weight': 0.7,
                'quality_weight': 0.7
            }
        }
    
    def create_execution_plan(self, required_tools: List[str],
                            question_intent: Optional[QuestionIntent] = None,
                            complexity: Optional[ComplexityLevel] = None,
                            context: Optional[QuestionContext] = None,
                            strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE,
                            constraints: Optional[ExecutionConstraints] = None) -> ExecutionPlan:
        """Create optimal execution plan"""
        
        self.logger.info(f"Creating execution plan for {len(required_tools)} tools")
        
        # Determine internal strategy if adaptive (but preserve original for plan)
        internal_strategy = strategy
        original_strategy = strategy
        if strategy == ExecutionStrategy.ADAPTIVE:
            internal_strategy = self._determine_adaptive_strategy(question_intent, complexity, context)
            self.logger.info(f"Adaptive strategy selected: {internal_strategy.value}")
        
        # Set default constraints if none provided
        if constraints is None:
            constraints = self._create_default_constraints(internal_strategy, complexity)
        
        # Build execution DAG
        question_context_dict = self._extract_context_dict(context) if context else {}
        dag = self.dag_builder.build_execution_dag(required_tools, question_intent, question_context_dict)
        
        # Create execution steps from DAG
        steps = self._create_execution_steps(dag, internal_strategy, constraints)
        
        # Optimize step scheduling
        optimized_steps = self._optimize_step_scheduling(steps, internal_strategy, constraints)
        
        # Calculate plan metrics
        plan_metrics = self._calculate_plan_metrics(optimized_steps, dag, internal_strategy)
        
        # Create execution plan (preserve original strategy)
        plan = ExecutionPlan(
            plan_id=f"plan_{int(time.time())}",
            steps=optimized_steps,
            strategy=original_strategy,  # Keep original ADAPTIVE strategy
            dag=dag,
            constraints=constraints,
            **plan_metrics
        )
        
        # Add adaptive features if applicable
        plan = self._add_adaptive_features(plan, context)
        
        self.logger.info(f"Created execution plan: {len(plan.steps)} steps, "
                        f"{plan.total_estimated_time:.1f}s, "
                        f"{plan.parallelization_ratio:.1%} parallel")
        
        return plan
    
    def _determine_adaptive_strategy(self, question_intent: Optional[QuestionIntent],
                                   complexity: Optional[ComplexityLevel],
                                   context: Optional[QuestionContext]) -> ExecutionStrategy:
        """Determine optimal strategy based on question characteristics"""
        
        # Speed optimization for simple questions
        if complexity == ComplexityLevel.SIMPLE:
            return ExecutionStrategy.SPEED_OPTIMIZED
        
        # Quality optimization for analysis-heavy intents
        if question_intent in [QuestionIntent.COMPARATIVE_ANALYSIS, QuestionIntent.CAUSAL_ANALYSIS, 
                             QuestionIntent.STATISTICAL_ANALYSIS, QuestionIntent.NETWORK_ANALYSIS]:
            return ExecutionStrategy.QUALITY_OPTIMIZED
        
        # Resource efficiency for large-scale processing
        if complexity == ComplexityLevel.COMPLEX:
            return ExecutionStrategy.RESOURCE_EFFICIENT
        
        # Default to balanced approach
        return ExecutionStrategy.BALANCED
    
    def _create_default_constraints(self, strategy: ExecutionStrategy,
                                   complexity: Optional[ComplexityLevel]) -> ExecutionConstraints:
        """Create default constraints based on strategy and complexity"""
        
        base_constraints = ExecutionConstraints()
        
        # Set constraints based on strategy
        if strategy == ExecutionStrategy.SPEED_OPTIMIZED:
            base_constraints.max_execution_time = 60.0  # 1 minute max
            base_constraints.max_parallel_tools = 8
        elif strategy == ExecutionStrategy.QUALITY_OPTIMIZED:
            base_constraints.required_quality_threshold = 0.95
            base_constraints.max_execution_time = 300.0  # 5 minutes max
        elif strategy == ExecutionStrategy.RESOURCE_EFFICIENT:
            base_constraints.max_memory_usage = 2000.0  # 2GB max
            base_constraints.max_parallel_tools = 2
        
        # Adjust based on complexity
        if complexity == ComplexityLevel.COMPLEX:
            if base_constraints.max_execution_time:
                base_constraints.max_execution_time *= 2
            if base_constraints.max_memory_usage:
                base_constraints.max_memory_usage *= 1.5
        
        return base_constraints
    
    def _extract_context_dict(self, context: QuestionContext) -> Dict[str, Any]:
        """Extract context information for DAG building"""
        context_dict = {}
        
        if hasattr(context, 'temporal_context') and context.temporal_context:
            context_dict['temporal'] = True
            context_dict['time_periods'] = getattr(context.temporal_context, 'time_periods', [])
        
        if hasattr(context, 'entity_context') and context.entity_context:
            context_dict['entities'] = getattr(context.entity_context, 'mentioned_entities', [])
        
        if hasattr(context, 'comparison_context') and context.comparison_context:
            context_dict['comparison'] = True
            
        return context_dict
    
    def _create_execution_steps(self, dag: ExecutionDAG, strategy: ExecutionStrategy,
                               constraints: ExecutionConstraints) -> List[ExecutionStep]:
        """Create execution steps from DAG"""
        
        steps = []
        step_counter = 0
        
        # Topologically sort DAG nodes
        sorted_nodes = self._topological_sort_dag(dag)
        
        # Create steps for each node
        for node_id in sorted_nodes:
            node = dag.get_node(node_id)
            if not node:
                continue
            
            step_counter += 1
            
            # Determine tool IDs for this step
            if node.node_type == NodeType.PARALLEL_GROUP:
                tool_ids = node.parallel_tools
            else:
                tool_ids = [node.tool_id] if node.tool_id else []
            
            # Calculate dependencies
            depends_on = [dep for dep in dag.get_dependencies(node_id) if dep in dag.nodes]
            
            # Determine execution priority
            priority = self._determine_step_priority(node, strategy, constraints)
            
            # Create execution step
            step = ExecutionStep(
                step_id=f"step_{step_counter:03d}",
                node_id=node_id,
                tool_ids=tool_ids,
                estimated_start_time=0.0,  # Will be calculated during scheduling
                estimated_duration=node.estimated_time,
                depends_on=depends_on,
                resource_allocation=node.resource_requirements,
                execution_priority=priority,
                adaptive_parameters=self._create_adaptive_parameters(node, strategy)
            )
            
            steps.append(step)
        
        return steps
    
    def _optimize_step_scheduling(self, steps: List[ExecutionStep], 
                                 strategy: ExecutionStrategy,
                                 constraints: ExecutionConstraints) -> List[ExecutionStep]:
        """Optimize scheduling of execution steps"""
        
        # Create dependency map
        step_map = {step.step_id: step for step in steps}
        
        # Calculate start times using critical path method
        self._calculate_step_start_times(steps, step_map)
        
        # Apply strategy-specific optimizations
        optimized_steps = self._apply_strategy_optimizations(steps, strategy, constraints)
        
        # Validate resource constraints
        validated_steps = self._validate_resource_constraints(optimized_steps, constraints)
        
        return validated_steps
    
    def _calculate_step_start_times(self, steps: List[ExecutionStep], 
                                   step_map: Dict[str, ExecutionStep]) -> None:
        """Calculate start times for all steps"""
        
        # Find steps with no dependencies (can start immediately)
        ready_steps = [step for step in steps if not step.depends_on]
        
        # Initialize start times
        for step in ready_steps:
            step.estimated_start_time = 0.0
        
        # Calculate start times for dependent steps
        processed = set()
        to_process = ready_steps.copy()
        
        while to_process:
            current_step = to_process.pop(0)
            if current_step.step_id in processed:
                continue
            
            processed.add(current_step.step_id)
            
            # Find steps that depend on this one
            dependent_steps = [step for step in steps 
                             if current_step.node_id in step.depends_on]
            
            for dependent_step in dependent_steps:
                # Calculate earliest possible start time
                dependency_end_times = []
                for dep_node_id in dependent_step.depends_on:
                    # Find step for this dependency
                    dep_step = next((s for s in steps if s.node_id == dep_node_id), None)
                    if dep_step:
                        dependency_end_times.append(dep_step.estimated_end_time)
                
                if dependency_end_times:
                    dependent_step.estimated_start_time = max(dependency_end_times)
                
                if dependent_step not in to_process:
                    to_process.append(dependent_step)
    
    def _apply_strategy_optimizations(self, steps: List[ExecutionStep],
                                     strategy: ExecutionStrategy,
                                     constraints: ExecutionConstraints) -> List[ExecutionStep]:
        """Apply strategy-specific optimizations"""
        
        config = self.strategy_configs.get(strategy, {})
        
        # Speed optimization: Maximize parallelization
        if config.get('prioritize_parallelization', False):
            steps = self._optimize_for_parallelization(steps)
        
        # Quality optimization: Add quality checkpoints
        if strategy == ExecutionStrategy.QUALITY_OPTIMIZED:
            steps = self._add_quality_checkpoints(steps)
        
        # Resource optimization: Minimize resource overlap
        if strategy == ExecutionStrategy.RESOURCE_EFFICIENT:
            steps = self._optimize_resource_usage(steps)
        
        return steps
    
    def _optimize_for_parallelization(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """Optimize steps for maximum parallelization"""
        
        # Look for opportunities to run steps in parallel
        # This is already handled by DAG parallel groups, but we can fine-tune timing
        
        # Adjust start times to maximize parallel execution
        for step in steps:
            if step.is_parallel_step:
                # Ensure parallel tools can actually start together
                pass  # Already handled in step creation
        
        return steps
    
    def _add_quality_checkpoints(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """Add quality checkpoints for quality-optimized execution"""
        
        # Add conditions for quality validation
        for step in steps:
            if step.tool_ids and any(tool in ['T23A_SPACY_NER', 'T27_RELATIONSHIP_EXTRACTOR'] 
                                   for tool in step.tool_ids):
                step.conditions.append("validate_output_quality")
                step.adaptive_parameters['quality_threshold'] = 0.95
        
        return steps
    
    def _optimize_resource_usage(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """Optimize for efficient resource usage"""
        
        # Spread resource-intensive operations over time
        high_resource_steps = [step for step in steps 
                              if step.resource_allocation.get('memory', 0) > 500]
        
        # Add delays between high-resource steps if needed
        for i, step in enumerate(high_resource_steps[1:], 1):
            prev_step = high_resource_steps[i-1]
            min_gap = 2.0  # 2 second gap between high-resource operations
            
            if step.estimated_start_time < prev_step.estimated_end_time + min_gap:
                step.estimated_start_time = prev_step.estimated_end_time + min_gap
        
        return steps
    
    def _validate_resource_constraints(self, steps: List[ExecutionStep],
                                      constraints: ExecutionConstraints) -> List[ExecutionStep]:
        """Validate and adjust for resource constraints"""
        
        # Check memory constraints
        if constraints.max_memory_usage:
            self._validate_memory_constraints(steps, constraints.max_memory_usage)
        
        # Check parallel execution constraints
        if constraints.max_parallel_tools:
            self._validate_parallelism_constraints(steps, constraints.max_parallel_tools)
        
        # Check time constraints
        if constraints.max_execution_time:
            total_time = max(step.estimated_end_time for step in steps) if steps else 0
            if total_time > constraints.max_execution_time:
                self.logger.warning(f"Execution plan exceeds time constraint: "
                                  f"{total_time:.1f}s > {constraints.max_execution_time:.1f}s")
        
        return steps
    
    def _validate_memory_constraints(self, steps: List[ExecutionStep], max_memory: float) -> None:
        """Validate memory usage constraints"""
        
        # Sample memory usage over time
        time_points = sorted(set([step.estimated_start_time for step in steps] + 
                                [step.estimated_end_time for step in steps]))
        
        for time_point in time_points:
            active_steps = [step for step in steps 
                           if step.estimated_start_time <= time_point < step.estimated_end_time]
            
            total_memory = sum(step.resource_allocation.get('memory', 0) for step in active_steps)
            
            if total_memory > max_memory:
                self.logger.warning(f"Memory constraint violation at time {time_point:.1f}s: "
                                  f"{total_memory:.1f}MB > {max_memory:.1f}MB")
    
    def _validate_parallelism_constraints(self, steps: List[ExecutionStep], max_parallel: int) -> None:
        """Validate parallel execution constraints"""
        
        for step in steps:
            if len(step.tool_ids) > max_parallel:
                self.logger.warning(f"Step {step.step_id} exceeds parallel tool limit: "
                                  f"{len(step.tool_ids)} > {max_parallel}")
    
    def _calculate_plan_metrics(self, steps: List[ExecutionStep], dag: ExecutionDAG,
                               strategy: ExecutionStrategy) -> Dict[str, float]:
        """Calculate metrics for the execution plan"""
        
        # Total execution time (makespan)
        total_time = max(step.estimated_end_time for step in steps) if steps else 0.0
        
        # Total cost (simplified as sum of execution times)
        total_cost = sum(step.estimated_duration for step in steps)
        
        # Parallelization ratio
        total_work = sum(step.estimated_duration for step in steps)
        parallelization_ratio = (total_work - total_time) / total_work if total_work > 0 else 0.0
        
        # Resource efficiency (work done per resource unit)
        total_resources = sum(sum(step.resource_allocation.values()) for step in steps)
        resource_efficiency = total_work / total_resources if total_resources > 0 else 1.0
        
        # Quality score (based on strategy and tool selection)
        quality_score = self._calculate_quality_score(steps, strategy)
        
        # Confidence (based on plan complexity and strategy fit)
        confidence = self._calculate_plan_confidence(steps, dag, strategy)
        
        return {
            'total_estimated_time': total_time,
            'total_estimated_cost': total_cost,
            'parallelization_ratio': parallelization_ratio,
            'resource_efficiency': resource_efficiency,
            'quality_score': quality_score,
            'confidence': confidence
        }
    
    def _calculate_quality_score(self, steps: List[ExecutionStep], 
                                strategy: ExecutionStrategy) -> float:
        """Calculate quality score for the plan"""
        
        base_quality = 0.8
        
        # Strategy-based adjustments
        if strategy == ExecutionStrategy.QUALITY_OPTIMIZED:
            base_quality = 0.95
        elif strategy == ExecutionStrategy.SPEED_OPTIMIZED:
            base_quality = 0.7
        
        # Adjust based on tool selection and sequencing
        quality_tools = ['T23A_SPACY_NER', 'T27_RELATIONSHIP_EXTRACTOR', 'T68_PAGE_RANK']
        quality_tool_count = sum(1 for step in steps 
                                for tool_id in step.tool_ids 
                                if tool_id in quality_tools)
        
        total_tools = sum(len(step.tool_ids) for step in steps)
        quality_ratio = quality_tool_count / total_tools if total_tools > 0 else 0
        
        return min(base_quality + quality_ratio * 0.1, 1.0)
    
    def _calculate_plan_confidence(self, steps: List[ExecutionStep], dag: ExecutionDAG,
                                  strategy: ExecutionStrategy) -> float:
        """Calculate confidence in the execution plan"""
        
        base_confidence = 0.85
        
        # Reduce confidence for very complex plans
        if len(steps) > 10:
            base_confidence -= 0.1
        
        # Increase confidence for well-parallelized plans
        parallel_steps = len([step for step in steps if step.is_parallel_step])
        if parallel_steps > 0:
            base_confidence += 0.05
        
        # Strategy-specific adjustments
        if strategy == ExecutionStrategy.ADAPTIVE:
            base_confidence += 0.1  # Adaptive strategy is robust
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _add_adaptive_features(self, plan: ExecutionPlan, 
                              context: Optional[QuestionContext]) -> ExecutionPlan:
        """Add adaptive features to the execution plan"""
        
        adaptive_features = []
        
        # Add temporal adaptation if context has temporal elements
        if context and hasattr(context, 'temporal_context') and context.temporal_context:
            adaptive_features.append("temporal_filtering")
        
        # Add complexity adaptation for complex questions
        if len(plan.steps) > 5:
            adaptive_features.append("complexity_scaling")
        
        # Add resource adaptation for resource-intensive plans
        if any(sum(step.resource_allocation.values()) > 1000 for step in plan.steps):
            adaptive_features.append("resource_monitoring")
        
        plan.adaptive_features = adaptive_features
        
        return plan
    
    def _topological_sort_dag(self, dag: ExecutionDAG) -> List[str]:
        """Topologically sort DAG nodes"""
        
        # Use NetworkX for robust topological sorting
        G = dag.to_networkx()
        
        try:
            import networkx as nx
            return list(nx.topological_sort(G))
        except:
            # Fallback to simple ordering
            return list(dag.nodes.keys())
    
    def _determine_step_priority(self, node: DAGNode, strategy: ExecutionStrategy,
                                constraints: ExecutionConstraints) -> ExecutionPriority:
        """Determine execution priority for a step"""
        
        # Critical path steps get high priority
        if node.node_id in getattr(node, 'critical_path', []):
            return ExecutionPriority.HIGH
        
        # Parallel groups get medium priority
        if node.node_type == NodeType.PARALLEL_GROUP:
            return ExecutionPriority.MEDIUM
        
        # Default priority
        return ExecutionPriority.MEDIUM
    
    def _create_adaptive_parameters(self, node: DAGNode, 
                                   strategy: ExecutionStrategy) -> Dict[str, Any]:
        """Create adaptive parameters for a step"""
        
        params = {}
        
        # Add strategy-specific parameters
        if strategy == ExecutionStrategy.QUALITY_OPTIMIZED:
            params['quality_threshold'] = 0.95
            params['retry_on_low_quality'] = True
        
        # Add node-specific parameters
        if node.tool_id in ['T23A_SPACY_NER', 'T27_RELATIONSHIP_EXTRACTOR']:
            params['confidence_threshold'] = 0.8
        
        return params
    
    def visualize_execution_plan(self, plan: ExecutionPlan) -> str:
        """Generate text visualization of execution plan"""
        
        lines = []
        lines.append("EXECUTION PLAN VISUALIZATION")
        lines.append("=" * 60)
        lines.append(f"Strategy: {plan.strategy.value}")
        lines.append(f"Total Time: {plan.total_estimated_time:.1f}s")
        lines.append(f"Parallelization: {plan.parallelization_ratio:.1%}")
        lines.append(f"Quality Score: {plan.quality_score:.2f}")
        lines.append(f"Confidence: {plan.confidence:.2f}")
        lines.append("")
        
        # Sort steps by start time
        sorted_steps = sorted(plan.steps, key=lambda s: s.estimated_start_time)
        
        for step in sorted_steps:
            if step.is_parallel_step:
                lines.append(f"⚡ {step.step_id}: PARALLEL {step.tool_ids}")
            else:
                lines.append(f"📋 {step.step_id}: {step.tool_ids[0] if step.tool_ids else 'N/A'}")
            
            lines.append(f"   Start: {step.estimated_start_time:.1f}s, "
                        f"Duration: {step.estimated_duration:.1f}s, "
                        f"Priority: {step.execution_priority.value}")
            
            if step.conditions:
                lines.append(f"   Conditions: {step.conditions}")
            lines.append("")
        
        return "\n".join(lines)