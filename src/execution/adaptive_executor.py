"""
Adaptive Execution Engine

Executes DAGs with adaptive logic that can modify execution based on intermediate results.
Provides intelligent execution control with real-time decision making.
"""

import asyncio
import logging
import time
from typing import Dict, List, Set, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .dag_builder import ExecutionDAG, DAGNode, NodeType
from .execution_planner import ExecutionPlan, ExecutionStep, ExecutionStrategy
from .dependency_resolver import DynamicDependencyResolver, ResolutionContext, ResolutionResult
from .result_analyzer import ResultAnalyzer, AnalysisResult, ResultQuality
from .execution_controller import ExecutionController, ExecutionStatus, ExecutionEvent

logger = logging.getLogger(__name__)


class AdaptiveDecision(Enum):
    """Types of adaptive decisions"""
    CONTINUE = "continue"           # Continue as planned
    SKIP_STEP = "skip_step"        # Skip current step
    MODIFY_PARAMS = "modify_params" # Modify step parameters
    ADD_STEP = "add_step"          # Add new step
    RETRY_STEP = "retry_step"      # Retry failed step
    ABORT_EXECUTION = "abort"       # Abort entire execution
    PARALLEL_BOOST = "parallel_boost" # Increase parallelization
    QUALITY_CHECK = "quality_check"   # Add quality validation


@dataclass
class AdaptiveContext:
    """Context for adaptive execution decisions"""
    current_step: ExecutionStep
    intermediate_results: Dict[str, Any]
    execution_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    resource_usage: Dict[str, float]
    time_elapsed: float
    remaining_steps: List[ExecutionStep]
    original_plan: ExecutionPlan
    constraints_status: Dict[str, Any]


@dataclass
class AdaptiveAction:
    """Action to take based on adaptive decision"""
    decision: AdaptiveDecision
    target_step_id: Optional[str] = None
    new_parameters: Dict[str, Any] = field(default_factory=dict)
    new_step: Optional[ExecutionStep] = None
    reason: str = ""
    confidence: float = 1.0
    expected_impact: Dict[str, float] = field(default_factory=dict)


class AdaptiveExecutor:
    """Executes DAGs with adaptive logic and real-time decision making"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize adaptive executor"""
        self.dependency_resolver = DynamicDependencyResolver(contracts_dir)
        self.result_analyzer = ResultAnalyzer()
        self.execution_controller = ExecutionController()
        self.logger = logger
        
        # Adaptive decision rules
        self.adaptation_rules = self._initialize_adaptation_rules()
        
        # Execution state
        self.current_execution: Optional[Dict[str, Any]] = None
        self.adaptation_history: List[AdaptiveAction] = []
        
        # Performance tracking
        self.execution_metrics = {
            'total_adaptations': 0,
            'successful_adaptations': 0,
            'time_saved': 0.0,
            'quality_improvements': 0
        }
        
        self.logger.info("Initialized adaptive executor with intelligent decision making")
    
    async def execute_adaptive_plan(self, execution_plan: ExecutionPlan,
                                  available_tools: Set[str],
                                  adaptation_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute plan with adaptive logic"""
        
        self.logger.info(f"Starting adaptive execution of plan {execution_plan.plan_id}")
        
        # Initialize execution context
        execution_context = self._initialize_execution_context(execution_plan, available_tools)
        
        # Set up adaptation configuration
        if adaptation_config:
            self._configure_adaptation_settings(adaptation_config)
        
        # Start execution monitoring
        await self.execution_controller.start_execution_monitoring(execution_plan)
        
        try:
            # Execute plan with adaptive control
            results = await self._execute_with_adaptation(execution_plan, execution_context)
            
            # Finalize execution
            final_results = await self._finalize_adaptive_execution(results, execution_context)
            
            self.logger.info(f"Adaptive execution completed successfully with {self.execution_metrics['total_adaptations']} adaptations")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Adaptive execution failed: {e}")
            await self.execution_controller.handle_execution_failure(execution_plan, str(e))
            raise
        
        finally:
            # Clean up execution state
            await self.execution_controller.stop_execution_monitoring()
            self.current_execution = None
    
    async def _execute_with_adaptation(self, plan: ExecutionPlan, 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plan with real-time adaptation"""
        
        execution_results = {}
        step_queue = plan.steps.copy()
        completed_steps = set()
        failed_steps = set()
        
        # Create adaptive context
        adaptive_context = AdaptiveContext(
            current_step=step_queue[0] if step_queue else None,
            intermediate_results={},
            execution_history=[],
            performance_metrics={},
            quality_metrics={},
            resource_usage={},
            time_elapsed=0.0,
            remaining_steps=step_queue.copy(),
            original_plan=plan,
            constraints_status={}
        )
        
        start_time = time.time()
        
        while step_queue:
            # Get next step(s) to execute
            ready_steps = self._get_ready_steps(step_queue, completed_steps)
            
            if not ready_steps:
                # Check for deadlock or unresolvable dependencies
                if not self._can_proceed(step_queue, failed_steps):
                    self.logger.warning("Execution cannot proceed - unresolvable dependencies")
                    break
                
                # Wait briefly and check again
                await asyncio.sleep(0.1)
                continue
            
            # Update adaptive context
            adaptive_context.current_step = ready_steps[0]
            adaptive_context.time_elapsed = time.time() - start_time
            adaptive_context.remaining_steps = step_queue.copy()
            
            # Make adaptive decision for each ready step
            for step in ready_steps:
                adaptive_context.current_step = step
                
                # Analyze current situation and make adaptive decision
                adaptive_action = await self._make_adaptive_decision(adaptive_context)
                
                # Execute adaptive action
                step_result = await self._execute_adaptive_action(
                    step, adaptive_action, adaptive_context, context
                )
                
                # Process step result
                if step_result['success']:
                    completed_steps.add(step.step_id)
                    execution_results[step.step_id] = step_result
                    
                    # Update adaptive context with results
                    adaptive_context.intermediate_results.update(step_result.get('outputs', {}))
                    
                    # Analyze intermediate results for further adaptations
                    await self._analyze_intermediate_results(step_result, adaptive_context)
                    
                else:
                    failed_steps.add(step.step_id)
                    self.logger.warning(f"Step {step.step_id} failed: {step_result.get('error', 'Unknown error')}")
                    
                    # Decide whether to retry or abort
                    retry_action = await self._decide_failure_response(step, step_result, adaptive_context)
                    if retry_action.decision == AdaptiveDecision.RETRY_STEP:
                        # Add step back to queue for retry
                        step_queue.append(step)
                        failed_steps.remove(step.step_id)
                
                # Remove completed/failed step from queue
                if step in step_queue:
                    step_queue.remove(step)
        
        # Calculate final performance metrics
        execution_results['_execution_summary'] = {
            'total_steps': len(plan.steps),
            'completed_steps': len(completed_steps),
            'failed_steps': len(failed_steps),
            'total_time': time.time() - start_time,
            'adaptations_made': len(self.adaptation_history),
            'performance_metrics': adaptive_context.performance_metrics,
            'quality_metrics': adaptive_context.quality_metrics
        }
        
        return execution_results
    
    async def _make_adaptive_decision(self, context: AdaptiveContext) -> AdaptiveAction:
        """Make intelligent adaptive decision based on current context"""
        
        # Analyze current situation
        situation_analysis = await self._analyze_execution_situation(context)
        
        # Check adaptation rules
        for rule in self.adaptation_rules:
            condition_result = rule['condition'](context, situation_analysis)
            if asyncio.iscoroutine(condition_result):
                condition_met = await condition_result
            else:
                condition_met = condition_result
                
            if condition_met:
                action = await rule['action'](context, situation_analysis)
                
                self.logger.info(f"Adaptive decision: {action.decision.value} - {action.reason}")
                self.adaptation_history.append(action)
                self.execution_metrics['total_adaptations'] += 1
                
                return action
        
        # Default action - continue as planned
        return AdaptiveAction(
            decision=AdaptiveDecision.CONTINUE,
            reason="No adaptation needed",
            confidence=1.0
        )
    
    async def _execute_adaptive_action(self, step: ExecutionStep, 
                                     action: AdaptiveAction,
                                     adaptive_context: AdaptiveContext,
                                     execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step with adaptive action applied"""
        
        if action.decision == AdaptiveDecision.SKIP_STEP:
            return {
                'success': True,
                'skipped': True,
                'reason': action.reason,
                'outputs': {}
            }
        
        elif action.decision == AdaptiveDecision.MODIFY_PARAMS:
            # Apply parameter modifications
            modified_step = self._apply_parameter_modifications(step, action.new_parameters)
            return await self._execute_single_step(modified_step, execution_context)
        
        elif action.decision == AdaptiveDecision.ADD_STEP:
            # Execute additional step first
            if action.new_step:
                additional_result = await self._execute_single_step(action.new_step, execution_context)
                adaptive_context.intermediate_results.update(additional_result.get('outputs', {}))
            
            # Then execute original step
            return await self._execute_single_step(step, execution_context)
        
        elif action.decision == AdaptiveDecision.QUALITY_CHECK:
            # Execute step with quality validation
            result = await self._execute_single_step(step, execution_context)
            
            if result['success']:
                # Perform quality check
                quality_result = await self._perform_quality_check(result, step)
                result['quality_check'] = quality_result
                
                if quality_result['passed']:
                    self.execution_metrics['quality_improvements'] += 1
                else:
                    # Quality check failed - might need retry
                    result['success'] = False
                    result['error'] = f"Quality check failed: {quality_result['reason']}"
            
            return result
        
        elif action.decision == AdaptiveDecision.PARALLEL_BOOST:
            # Attempt parallel execution if possible
            return await self._execute_with_parallel_boost(step, execution_context)
        
        else:
            # Default execution
            return await self._execute_single_step(step, execution_context)
    
    async def _execute_single_step(self, step: ExecutionStep, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single execution step"""
        
        self.logger.debug(f"Executing step {step.step_id}: {step.tool_ids}")
        
        start_time = time.time()
        
        try:
            # Simulate tool execution (in real implementation, this would call actual tools)
            if step.is_parallel_step:
                # Parallel execution
                results = await self._execute_parallel_tools(step.tool_ids, context)
            else:
                # Sequential execution
                results = await self._execute_sequential_tools(step.tool_ids, context)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'step_id': step.step_id,
                'tool_ids': step.tool_ids,
                'execution_time': execution_time,
                'outputs': results,
                'metadata': {
                    'start_time': start_time,
                    'end_time': time.time(),
                    'resource_usage': step.resource_allocation
                }
            }
            
        except Exception as e:
            self.logger.error(f"Step {step.step_id} execution failed: {e}")
            return {
                'success': False,
                'step_id': step.step_id,
                'tool_ids': step.tool_ids,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    async def _execute_parallel_tools(self, tool_ids: List[str], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tools in parallel"""
        
        self.logger.debug(f"Executing {len(tool_ids)} tools in parallel")
        
        # Create tasks for parallel execution
        tasks = []
        for tool_id in tool_ids:
            task = asyncio.create_task(self._execute_tool(tool_id, context))
            tasks.append((tool_id, task))
        
        # Wait for all tasks to complete
        results = {}
        for tool_id, task in tasks:
            try:
                result = await task
                results[tool_id] = result
            except Exception as e:
                results[tool_id] = {'error': str(e), 'success': False}
        
        return results
    
    async def _execute_sequential_tools(self, tool_ids: List[str],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tools sequentially"""
        
        results = {}
        for tool_id in tool_ids:
            try:
                result = await self._execute_tool(tool_id, context)
                results[tool_id] = result
                
                # Update context with intermediate results
                context['intermediate_results'].update(result.get('outputs', {}))
                
            except Exception as e:
                results[tool_id] = {'error': str(e), 'success': False}
                break  # Stop on first failure in sequential execution
        
        return results
    
    async def _execute_tool(self, tool_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual tool (simulated)"""
        
        # Simulate tool execution time
        execution_time = {
            'T01_PDF_LOADER': 2.0,
            'T15A_TEXT_CHUNKER': 1.0,
            'T23A_SPACY_NER': 3.0,
            'T27_RELATIONSHIP_EXTRACTOR': 4.0,
            'T31_ENTITY_BUILDER': 2.5,
            'T34_EDGE_BUILDER': 2.0,
            'T68_PAGE_RANK': 5.0,
            'T49_MULTI_HOP_QUERY': 1.5,
            'T85_TWITTER_EXPLORER': 6.0
        }.get(tool_id, 2.0)
        
        await asyncio.sleep(execution_time * 0.1)  # Reduced for testing
        
        # Simulate successful tool execution with outputs
        return {
            'success': True,
            'tool_id': tool_id,
            'execution_time': execution_time,
            'outputs': {
                f'{tool_id}_result': f'Output from {tool_id}',
                f'{tool_id}_confidence': 0.85 + (hash(tool_id) % 100) / 1000  # Simulated confidence
            }
        }
    
    def _get_ready_steps(self, step_queue: List[ExecutionStep], 
                        completed_steps: Set[str]) -> List[ExecutionStep]:
        """Get steps that are ready to execute"""
        
        ready_steps = []
        
        for step in step_queue:
            # Check if all dependencies are satisfied
            dependencies_satisfied = all(
                dep_id in completed_steps for dep_id in step.depends_on
            )
            
            if dependencies_satisfied:
                ready_steps.append(step)
        
        return ready_steps
    
    def _can_proceed(self, remaining_steps: List[ExecutionStep], 
                    failed_steps: Set[str]) -> bool:
        """Check if execution can proceed"""
        
        for step in remaining_steps:
            # Check if any dependencies are in failed steps
            if any(dep_id in failed_steps for dep_id in step.depends_on):
                continue  # This step cannot proceed due to failed dependency
            
            # Check if all dependencies are theoretically satisfiable
            unsatisfied_deps = [dep for dep in step.depends_on 
                              if dep not in failed_steps]
            
            if not unsatisfied_deps:
                return True  # At least one step can proceed
        
        return False
    
    async def _analyze_execution_situation(self, context: AdaptiveContext) -> Dict[str, Any]:
        """Analyze current execution situation for adaptive decisions"""
        
        situation = {
            'time_pressure': context.time_elapsed > (context.original_plan.total_estimated_time * 0.8),
            'quality_concerns': any(q < 0.7 for q in context.quality_metrics.values()),
            'resource_pressure': any(r > 0.9 for r in context.resource_usage.values()),
            'progress_rate': len(context.execution_history) / max(context.time_elapsed, 1.0),
            'remaining_complexity': len(context.remaining_steps),
            'failure_rate': sum(1 for h in context.execution_history if not h.get('success', True)) / max(len(context.execution_history), 1)
        }
        
        # Analyze intermediate results quality
        if context.intermediate_results:
            quality_analysis = await self.result_analyzer.analyze_result_quality(
                context.intermediate_results
            )
            situation['intermediate_quality'] = quality_analysis.overall_quality
        
        return situation
    
    async def _analyze_intermediate_results(self, step_result: Dict[str, Any],
                                          context: AdaptiveContext) -> None:
        """Analyze intermediate results and update context"""
        
        # Extract quality metrics from step result
        if 'outputs' in step_result:
            for tool_id, tool_result in step_result['outputs'].items():
                if isinstance(tool_result, dict) and 'confidence' in tool_result:
                    confidence = tool_result['confidence']
                    context.quality_metrics[tool_id] = confidence
        
        # Update performance metrics
        if 'execution_time' in step_result:
            execution_time = step_result['execution_time']
            estimated_time = context.current_step.estimated_duration
            
            efficiency = estimated_time / execution_time if execution_time > 0 else 1.0
            context.performance_metrics[step_result['step_id']] = efficiency
        
        # Add to execution history
        context.execution_history.append({
            'step_id': step_result['step_id'],
            'success': step_result['success'],
            'execution_time': step_result.get('execution_time', 0),
            'timestamp': time.time()
        })
    
    async def _decide_failure_response(self, step: ExecutionStep, 
                                     step_result: Dict[str, Any],
                                     context: AdaptiveContext) -> AdaptiveAction:
        """Decide how to respond to step failure"""
        
        error_type = step_result.get('error', '')
        
        # Simple retry logic for transient errors
        if 'timeout' in error_type.lower() or 'connection' in error_type.lower():
            return AdaptiveAction(
                decision=AdaptiveDecision.RETRY_STEP,
                reason=f"Retrying due to transient error: {error_type}",
                confidence=0.8
            )
        
        # Skip non-critical steps
        if step.execution_priority.value == 'low':
            return AdaptiveAction(
                decision=AdaptiveDecision.SKIP_STEP,
                reason=f"Skipping low-priority step due to error: {error_type}",
                confidence=0.9
            )
        
        # Default - don't retry
        return AdaptiveAction(
            decision=AdaptiveDecision.CONTINUE,
            reason="Continue execution despite failure",
            confidence=0.5
        )
    
    def _initialize_adaptation_rules(self) -> List[Dict[str, Callable]]:
        """Initialize adaptive decision rules"""
        
        return [
            {
                'name': 'time_pressure_optimization',
                'condition': lambda ctx, analysis: analysis.get('time_pressure', False),
                'action': self._handle_time_pressure
            },
            {
                'name': 'quality_improvement',
                'condition': lambda ctx, analysis: analysis.get('quality_concerns', False),
                'action': self._handle_quality_concerns
            },
            {
                'name': 'resource_optimization',
                'condition': lambda ctx, analysis: analysis.get('resource_pressure', False),
                'action': self._handle_resource_pressure
            },
            {
                'name': 'parallel_opportunity',
                'condition': lambda ctx, analysis: (
                    len(ctx.remaining_steps) > 1 and 
                    analysis.get('progress_rate', 0) > 1.0
                ),
                'action': self._handle_parallel_opportunity
            }
        ]
    
    async def _handle_time_pressure(self, context: AdaptiveContext, 
                                  analysis: Dict[str, Any]) -> AdaptiveAction:
        """Handle time pressure by optimizing execution"""
        
        # Skip non-essential quality checks
        if hasattr(context.current_step, 'conditions') and 'validate_output_quality' in context.current_step.conditions:
            return AdaptiveAction(
                decision=AdaptiveDecision.MODIFY_PARAMS,
                new_parameters={'skip_quality_validation': True},
                reason="Skipping quality validation due to time pressure",
                confidence=0.7,
                expected_impact={'time_saved': 2.0}
            )
        
        # Increase parallelization
        return AdaptiveAction(
            decision=AdaptiveDecision.PARALLEL_BOOST,
            reason="Increasing parallelization due to time pressure",
            confidence=0.8,
            expected_impact={'time_saved': 5.0}
        )
    
    async def _handle_quality_concerns(self, context: AdaptiveContext,
                                     analysis: Dict[str, Any]) -> AdaptiveAction:
        """Handle quality concerns by adding quality checks"""
        
        return AdaptiveAction(
            decision=AdaptiveDecision.QUALITY_CHECK,
            reason="Adding quality validation due to quality concerns",
            confidence=0.9,
            expected_impact={'quality_improvement': 0.1}
        )
    
    async def _handle_resource_pressure(self, context: AdaptiveContext,
                                      analysis: Dict[str, Any]) -> AdaptiveAction:
        """Handle resource pressure by optimizing resource usage"""
        
        return AdaptiveAction(
            decision=AdaptiveDecision.MODIFY_PARAMS,
            new_parameters={'reduce_memory_usage': True, 'batch_size': 'small'},
            reason="Reducing resource usage due to resource pressure",
            confidence=0.8,
            expected_impact={'resource_reduction': 0.3}
        )
    
    async def _handle_parallel_opportunity(self, context: AdaptiveContext,
                                         analysis: Dict[str, Any]) -> AdaptiveAction:
        """Handle opportunity for increased parallelization"""
        
        return AdaptiveAction(
            decision=AdaptiveDecision.PARALLEL_BOOST,
            reason="Increasing parallelization due to good progress rate",
            confidence=0.9,
            expected_impact={'time_saved': 3.0}
        )
    
    def _initialize_execution_context(self, plan: ExecutionPlan, 
                                    available_tools: Set[str]) -> Dict[str, Any]:
        """Initialize execution context"""
        
        return {
            'plan': plan,
            'available_tools': available_tools,
            'intermediate_results': {},
            'execution_start_time': time.time(),
            'resource_usage': {},
            'quality_metrics': {}
        }
    
    def _configure_adaptation_settings(self, config: Dict[str, Any]) -> None:
        """Configure adaptation settings"""
        
        # Configure adaptation aggressiveness
        if 'adaptation_threshold' in config:
            self.adaptation_threshold = config['adaptation_threshold']
        
        # Configure quality thresholds
        if 'quality_threshold' in config:
            self.quality_threshold = config['quality_threshold']
        
        # Configure time pressure sensitivity
        if 'time_pressure_factor' in config:
            self.time_pressure_factor = config['time_pressure_factor']
    
    async def _finalize_adaptive_execution(self, results: Dict[str, Any],
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize adaptive execution and compile results"""
        
        # Calculate adaptation effectiveness
        successful_adaptations = sum(
            1 for action in self.adaptation_history 
            if action.expected_impact
        )
        
        self.execution_metrics['successful_adaptations'] = successful_adaptations
        
        # Compile final results
        final_results = {
            'execution_results': results,
            'adaptation_summary': {
                'total_adaptations': len(self.adaptation_history),
                'successful_adaptations': successful_adaptations,
                'adaptation_history': [
                    {
                        'decision': action.decision.value,
                        'reason': action.reason,
                        'confidence': action.confidence,
                        'impact': action.expected_impact
                    }
                    for action in self.adaptation_history
                ]
            },
            'performance_metrics': self.execution_metrics,
            'execution_summary': results.get('_execution_summary', {})
        }
        
        return final_results
    
    def _apply_parameter_modifications(self, step: ExecutionStep, 
                                     modifications: Dict[str, Any]) -> ExecutionStep:
        """Apply parameter modifications to execution step"""
        
        # Create modified copy of step
        modified_step = ExecutionStep(
            step_id=step.step_id,
            node_id=step.node_id,
            tool_ids=step.tool_ids,
            estimated_start_time=step.estimated_start_time,
            estimated_duration=step.estimated_duration,
            depends_on=step.depends_on.copy(),
            resource_allocation=step.resource_allocation.copy(),
            execution_priority=step.execution_priority,
            conditions=step.conditions.copy(),
            adaptive_parameters={**step.adaptive_parameters, **modifications}
        )
        
        return modified_step
    
    async def _perform_quality_check(self, result: Dict[str, Any], 
                                   step: ExecutionStep) -> Dict[str, Any]:
        """Perform quality check on step result"""
        
        if 'outputs' not in result:
            return {'passed': False, 'reason': 'No outputs to validate'}
        
        # Analyze result quality
        quality_analysis = await self.result_analyzer.analyze_result_quality(result['outputs'])
        
        quality_threshold = step.adaptive_parameters.get('quality_threshold', 0.8)
        
        if quality_analysis.overall_quality >= quality_threshold:
            return {
                'passed': True,
                'quality_score': quality_analysis.overall_quality,
                'analysis': quality_analysis
            }
        else:
            return {
                'passed': False,
                'quality_score': quality_analysis.overall_quality,
                'reason': f"Quality {quality_analysis.overall_quality:.2f} below threshold {quality_threshold}",
                'analysis': quality_analysis
            }
    
    async def _execute_with_parallel_boost(self, step: ExecutionStep,
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step with enhanced parallelization"""
        
        if not step.is_parallel_step:
            # Can't boost non-parallel step
            return await self._execute_single_step(step, context)
        
        # Execute with enhanced parallel processing
        self.logger.info(f"Applying parallel boost to step {step.step_id}")
        
        # Record time saved from parallel boost
        start_time = time.time()
        result = await self._execute_single_step(step, context)
        actual_time = time.time() - start_time
        
        estimated_sequential_time = step.estimated_duration
        time_saved = max(0, estimated_sequential_time - actual_time)
        
        self.execution_metrics['time_saved'] += time_saved
        
        result['parallel_boost'] = {
            'applied': True,
            'time_saved': time_saved,
            'efficiency_gain': time_saved / estimated_sequential_time if estimated_sequential_time > 0 else 0
        }
        
        return result
    
    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get summary of adaptive execution performance"""
        
        return {
            'total_adaptations': self.execution_metrics['total_adaptations'],
            'successful_adaptations': self.execution_metrics['successful_adaptations'],
            'adaptation_success_rate': (
                self.execution_metrics['successful_adaptations'] / 
                max(self.execution_metrics['total_adaptations'], 1)
            ),
            'time_saved': self.execution_metrics['time_saved'],
            'quality_improvements': self.execution_metrics['quality_improvements'],
            'adaptation_types': {
                action.decision.value: 1 
                for action in self.adaptation_history
            }
        }
    
    def reset_execution_metrics(self) -> None:
        """Reset execution metrics for new execution"""
        
        self.execution_metrics = {
            'total_adaptations': 0,
            'successful_adaptations': 0,
            'time_saved': 0.0,
            'quality_improvements': 0
        }
        self.adaptation_history = []