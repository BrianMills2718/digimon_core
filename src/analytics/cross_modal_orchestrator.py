#!/usr/bin/env python3
"""
Cross-Modal Orchestrator - Intelligent orchestration of cross-modal analysis workflows

Implements intelligent orchestration combining mode selection, conversion, and validation
for optimal cross-modal analysis with workflow optimization and resource management.
"""

import anyio
import time
import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from ..core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from ..core.config_manager import get_config
    from ..core.logging_config import get_logger
except ImportError:
    # Fallback for direct execution - ONLY try absolute import, NO stubs
    from src.core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from src.core.config_manager import get_config
    from src.core.logging_config import get_logger
from .mode_selection_service import (
    ModeSelectionService, DataContext, ModeSelectionResult, AnalysisMode, create_data_context
)
from .cross_modal_converter import CrossModalConverter, DataFormat, ConversionResult
from .cross_modal_validator import CrossModalValidator, ValidationLevel, ValidationReport

logger = get_logger("analytics.cross_modal_orchestrator")


class WorkflowOptimizationLevel(Enum):
    """Workflow optimization levels"""
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"


@dataclass
class AnalysisRequest:
    """Request for cross-modal analysis"""
    request_id: str
    research_question: str
    data: Any
    source_format: DataFormat
    preferred_modes: Optional[List[AnalysisMode]] = None
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    optimization_level: WorkflowOptimizationLevel = WorkflowOptimizationLevel.STANDARD
    constraints: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowStep:
    """Individual step in orchestrated workflow"""
    step_id: str
    step_type: str
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_duration: float
    required_resources: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    actual_duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class OptimizedWorkflow:
    """Optimized workflow for cross-modal analysis"""
    workflow_id: str
    steps: List[WorkflowStep]
    estimated_total_duration: float
    resource_requirements: Dict[str, Any]
    parallelizable_steps: List[List[str]]
    critical_path: List[str]
    optimization_metadata: Dict[str, Any]


@dataclass
class AnalysisResult:
    """Result of orchestrated cross-modal analysis"""
    request_id: str
    workflow_id: str
    success: bool
    primary_result: Any
    secondary_results: List[Any]
    analysis_metadata: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    validation_report: Optional[ValidationReport]
    execution_time: float
    workflow_efficiency: float
    recommendations: List[str]


class WorkflowOptimizer:
    """Optimizer for cross-modal analysis workflows"""
    
    def __init__(self):
        self.logger = get_logger("analytics.workflow_optimizer")
        
        # Optimization strategies
        self.optimization_strategies = {
            WorkflowOptimizationLevel.BASIC: self._basic_optimization,
            WorkflowOptimizationLevel.STANDARD: self._standard_optimization,
            WorkflowOptimizationLevel.AGGRESSIVE: self._aggressive_optimization,
            WorkflowOptimizationLevel.ADAPTIVE: self._adaptive_optimization
        }
        
        # Performance cache for optimization decisions
        self.performance_cache = {}
        self.optimization_history = []
    
    async def optimize_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        optimization_level: WorkflowOptimizationLevel,
        constraints: Optional[Dict[str, Any]] = None
    ) -> OptimizedWorkflow:
        """Optimize workflow for performance and efficiency"""
        
        workflow_id = self._generate_workflow_id()
        
        # Convert raw steps to WorkflowStep objects
        steps = [self._create_workflow_step(step_data) for step_data in workflow_steps]
        
        # Apply optimization strategy
        optimizer_func = self.optimization_strategies[optimization_level]
        optimized_steps, optimization_metadata = await optimizer_func(steps, constraints or {})
        
        # Calculate workflow metrics
        estimated_duration = self._calculate_estimated_duration(optimized_steps)
        resource_requirements = self._calculate_resource_requirements(optimized_steps)
        parallelizable_steps = self._identify_parallelizable_steps(optimized_steps)
        critical_path = self._calculate_critical_path(optimized_steps)
        
        workflow = OptimizedWorkflow(
            workflow_id=workflow_id,
            steps=optimized_steps,
            estimated_total_duration=estimated_duration,
            resource_requirements=resource_requirements,
            parallelizable_steps=parallelizable_steps,
            critical_path=critical_path,
            optimization_metadata=optimization_metadata
        )
        
        self.logger.info(
            f"Workflow {workflow_id} optimized with {optimization_level.value} strategy: "
            f"{len(optimized_steps)} steps, estimated duration {estimated_duration:.1f}s"
        )
        
        return workflow
    
    async def _basic_optimization(
        self,
        steps: List[WorkflowStep],
        constraints: Dict[str, Any]
    ) -> Tuple[List[WorkflowStep], Dict[str, Any]]:
        """Basic optimization - minimal changes"""
        
        # Just ensure proper dependency ordering
        ordered_steps = self._order_by_dependencies(steps)
        
        metadata = {
            "optimization_level": "basic",
            "changes_made": ["dependency_ordering"],
            "optimizations_applied": 1
        }
        
        return ordered_steps, metadata
    
    async def _standard_optimization(
        self,
        steps: List[WorkflowStep],
        constraints: Dict[str, Any]
    ) -> Tuple[List[WorkflowStep], Dict[str, Any]]:
        """Standard optimization - moderate improvements"""
        
        changes_made = []
        
        # Order by dependencies
        optimized_steps = self._order_by_dependencies(steps)
        changes_made.append("dependency_ordering")
        
        # Remove redundant steps
        optimized_steps = self._remove_redundant_steps(optimized_steps)
        if len(optimized_steps) < len(steps):
            changes_made.append("redundancy_removal")
        
        # Optimize parameter passing
        optimized_steps = self._optimize_parameter_passing(optimized_steps)
        changes_made.append("parameter_optimization")
        
        metadata = {
            "optimization_level": "standard",
            "changes_made": changes_made,
            "optimizations_applied": len(changes_made),
            "steps_removed": len(steps) - len(optimized_steps)
        }
        
        return optimized_steps, metadata
    
    async def _aggressive_optimization(
        self,
        steps: List[WorkflowStep],
        constraints: Dict[str, Any]
    ) -> Tuple[List[WorkflowStep], Dict[str, Any]]:
        """Aggressive optimization - maximum performance"""
        
        changes_made = []
        
        # Start with standard optimizations
        optimized_steps, _ = await self._standard_optimization(steps, constraints)
        changes_made.extend(["dependency_ordering", "redundancy_removal", "parameter_optimization"])
        
        # Merge compatible steps
        optimized_steps = self._merge_compatible_steps(optimized_steps)
        changes_made.append("step_merging")
        
        # Add caching for expensive operations
        optimized_steps = self._add_caching_steps(optimized_steps)
        changes_made.append("caching_optimization")
        
        # Reorder for maximum parallelization
        optimized_steps = self._optimize_for_parallelization(optimized_steps)
        changes_made.append("parallelization_optimization")
        
        metadata = {
            "optimization_level": "aggressive",
            "changes_made": changes_made,
            "optimizations_applied": len(changes_made),
            "performance_boost_estimate": 0.3  # 30% estimated improvement
        }
        
        return optimized_steps, metadata
    
    async def _adaptive_optimization(
        self,
        steps: List[WorkflowStep],
        constraints: Dict[str, Any]
    ) -> Tuple[List[WorkflowStep], Dict[str, Any]]:
        """Adaptive optimization - learns from previous executions"""
        
        # Check performance history for similar workflows
        workflow_signature = self._calculate_workflow_signature(steps)
        historical_performance = self.performance_cache.get(workflow_signature, {})
        
        if historical_performance:
            # Use learned optimizations
            optimization_level = self._select_adaptive_level(historical_performance)
            optimized_steps, metadata = await self.optimization_strategies[optimization_level](steps, constraints)
            metadata["adaptive_decision"] = f"Selected {optimization_level.value} based on history"
        else:
            # Start with standard optimization for unknown workflows
            optimized_steps, metadata = await self._standard_optimization(steps, constraints)
            metadata["adaptive_decision"] = "Standard optimization for new workflow pattern"
        
        metadata["optimization_level"] = "adaptive"
        metadata["workflow_signature"] = workflow_signature
        
        return optimized_steps, metadata
    
    def _create_workflow_step(self, step_data: Dict[str, Any]) -> WorkflowStep:
        """Create WorkflowStep from step data"""
        return WorkflowStep(
            step_id=step_data.get("step_id", ""),
            step_type=step_data.get("step_type", ""),
            operation=step_data.get("operation", ""),
            parameters=step_data.get("parameters", {}),
            dependencies=step_data.get("dependencies", []),
            estimated_duration=step_data.get("estimated_duration", 60.0),
            required_resources=step_data.get("required_resources", {})
        )
    
    def _order_by_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Order steps by dependency requirements"""
        
        ordered = []
        remaining = steps.copy()
        completed_ids = set()
        
        while remaining:
            # Find steps with satisfied dependencies
            ready_steps = [
                step for step in remaining 
                if all(dep in completed_ids for dep in step.dependencies)
            ]
            
            if not ready_steps:
                # Break circular dependencies by selecting step with fewest unsatisfied deps
                ready_steps = [min(remaining, key=lambda s: len(s.dependencies))]
            
            # Add ready steps to ordered list
            for step in ready_steps:
                ordered.append(step)
                completed_ids.add(step.step_id)
                remaining.remove(step)
        
        return ordered
    
    def _remove_redundant_steps(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Remove redundant workflow steps"""
        
        unique_steps = []
        seen_operations = set()
        
        for step in steps:
            # Create signature for step
            signature = f"{step.operation}_{hash(json.dumps(step.parameters, sort_keys=True))}"
            
            if signature not in seen_operations:
                unique_steps.append(step)
                seen_operations.add(signature)
            else:
                self.logger.debug(f"Removing redundant step: {step.step_id}")
        
        return unique_steps
    
    def _optimize_parameter_passing(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Optimize parameter passing between steps"""
        
        optimized_steps = []
        
        for step in steps:
            # Look for opportunities to reuse outputs from previous steps
            for dep_id in step.dependencies:
                # Find the dependency step
                dep_step = next((s for s in steps if s.step_id == dep_id), None)
                if dep_step:
                    # Check if we can optimize parameter passing
                    if self._can_optimize_parameters(step, dep_step):
                        step.parameters["optimized_input"] = f"output_from_{dep_id}"
            
            optimized_steps.append(step)
        
        return optimized_steps
    
    def _can_optimize_parameters(self, step: WorkflowStep, dep_step: WorkflowStep) -> bool:
        """Check if parameters can be optimized between steps"""
        
        # Simple heuristic: if output format matches input format
        dep_output_format = dep_step.parameters.get("target_format")
        step_input_format = step.parameters.get("source_format")
        
        return dep_output_format == step_input_format
    
    def _merge_compatible_steps(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Merge compatible steps for efficiency"""
        
        merged_steps = []
        i = 0
        
        while i < len(steps):
            current_step = steps[i]
            
            # Look for next step that can be merged
            if i + 1 < len(steps):
                next_step = steps[i + 1]
                
                if self._can_merge_steps(current_step, next_step):
                    # Create merged step
                    merged_step = self._create_merged_step(current_step, next_step)
                    merged_steps.append(merged_step)
                    i += 2  # Skip both steps
                    continue
            
            merged_steps.append(current_step)
            i += 1
        
        return merged_steps
    
    def _can_merge_steps(self, step1: WorkflowStep, step2: WorkflowStep) -> bool:
        """Check if two steps can be merged"""
        
        # Can merge if step2 only depends on step1 and they're compatible operations
        return (
            step1.step_id in step2.dependencies and
            len(step2.dependencies) == 1 and
            step1.step_type == step2.step_type == "analysis"
        )
    
    def _create_merged_step(self, step1: WorkflowStep, step2: WorkflowStep) -> WorkflowStep:
        """Create a merged step from two compatible steps"""
        
        return WorkflowStep(
            step_id=f"merged_{step1.step_id}_{step2.step_id}",
            step_type="merged_analysis",
            operation=f"merged_{step1.operation}_{step2.operation}",
            parameters={**step1.parameters, **step2.parameters},
            dependencies=step1.dependencies,
            estimated_duration=step1.estimated_duration + step2.estimated_duration * 0.7,  # 30% savings
            required_resources=self._merge_resource_requirements(
                step1.required_resources, step2.required_resources
            )
        )
    
    def _merge_resource_requirements(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge resource requirements for merged steps"""
        
        merged = req1.copy()
        
        # Memory: take maximum
        mem1 = self._parse_memory(req1.get("memory", "0MB"))
        mem2 = self._parse_memory(req2.get("memory", "0MB"))
        merged["memory"] = f"{max(mem1, mem2)}MB"
        
        # CPU: take maximum
        cpu_levels = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
        cpu1 = cpu_levels.get(req1.get("cpu", "low"), 1)
        cpu2 = cpu_levels.get(req2.get("cpu", "low"), 1)
        cpu_names = {1: "low", 2: "medium", 3: "high", 4: "very_high"}
        merged["cpu"] = cpu_names[max(cpu1, cpu2)]
        
        return merged
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory string to MB"""
        if "GB" in memory_str:
            return int(memory_str.replace("GB", "")) * 1024
        elif "MB" in memory_str:
            return int(memory_str.replace("MB", ""))
        return 0
    
    def _add_caching_steps(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Add caching for expensive operations"""
        
        cached_steps = []
        
        for step in steps:
            # Add caching for expensive operations
            if step.estimated_duration > 60.0:  # Cache operations taking > 1 minute
                # Add cache check step
                cache_check_step = WorkflowStep(
                    step_id=f"cache_check_{step.step_id}",
                    step_type="cache",
                    operation="check_cache",
                    parameters={"target_operation": step.operation, "cache_key": self._generate_cache_key(step)},
                    dependencies=step.dependencies,
                    estimated_duration=1.0,
                    required_resources={"memory": "50MB", "cpu": "low"}
                )
                
                # Update original step to depend on cache check
                step.dependencies = [cache_check_step.step_id]
                
                cached_steps.extend([cache_check_step, step])
            else:
                cached_steps.append(step)
        
        return cached_steps
    
    def _generate_cache_key(self, step: WorkflowStep) -> str:
        """Generate cache key for step"""
        import hashlib
        content = f"{step.operation}_{json.dumps(step.parameters, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _optimize_for_parallelization(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Reorder steps to maximize parallelization opportunities"""
        
        # Group steps by their dependency level
        dependency_levels = {}
        
        for step in steps:
            level = self._calculate_dependency_level(step, steps)
            if level not in dependency_levels:
                dependency_levels[level] = []
            dependency_levels[level].append(step)
        
        # Reorder within each level to group similar operations
        optimized_steps = []
        for level in sorted(dependency_levels.keys()):
            level_steps = dependency_levels[level]
            # Sort by operation type to group similar operations
            level_steps.sort(key=lambda s: s.operation)
            optimized_steps.extend(level_steps)
        
        return optimized_steps
    
    def _calculate_dependency_level(self, step: WorkflowStep, all_steps: List[WorkflowStep]) -> int:
        """Calculate the dependency level of a step"""
        
        if not step.dependencies:
            return 0
        
        max_dep_level = 0
        for dep_id in step.dependencies:
            dep_step = next((s for s in all_steps if s.step_id == dep_id), None)
            if dep_step:
                dep_level = self._calculate_dependency_level(dep_step, all_steps)
                max_dep_level = max(max_dep_level, dep_level)
        
        return max_dep_level + 1
    
    def _calculate_estimated_duration(self, steps: List[WorkflowStep]) -> float:
        """Calculate estimated total duration considering parallelization"""
        
        # Build dependency graph
        dependency_graph = {}
        for step in steps:
            dependency_graph[step.step_id] = {
                "duration": step.estimated_duration,
                "dependencies": step.dependencies
            }
        
        # Calculate critical path
        return self._calculate_critical_path_duration(dependency_graph)
    
    def _calculate_critical_path_duration(self, dependency_graph: Dict[str, Dict]) -> float:
        """Calculate duration of critical path"""
        
        # Topological sort with duration calculation
        in_degree = {step_id: 0 for step_id in dependency_graph}
        for step_id, step_info in dependency_graph.items():
            for dep in step_info["dependencies"]:
                if dep in in_degree:
                    in_degree[step_id] += 1
        
        # Calculate earliest start times
        earliest_start = {step_id: 0 for step_id in dependency_graph}
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            current_info = dependency_graph[current]
            
            # Update dependent steps
            for step_id, step_info in dependency_graph.items():
                if current in step_info["dependencies"]:
                    earliest_start[step_id] = max(
                        earliest_start[step_id],
                        earliest_start[current] + current_info["duration"]
                    )
                    in_degree[step_id] -= 1
                    if in_degree[step_id] == 0:
                        queue.append(step_id)
        
        # Return maximum completion time
        max_completion = 0
        for step_id, step_info in dependency_graph.items():
            completion_time = earliest_start[step_id] + step_info["duration"]
            max_completion = max(max_completion, completion_time)
        
        return max_completion
    
    def _calculate_resource_requirements(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """Calculate overall resource requirements"""
        
        max_memory = 0
        max_cpu_level = 0
        cpu_levels = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
        
        for step in steps:
            # Memory
            memory = self._parse_memory(step.required_resources.get("memory", "0MB"))
            max_memory = max(max_memory, memory)
            
            # CPU
            cpu_level = cpu_levels.get(step.required_resources.get("cpu", "low"), 1)
            max_cpu_level = max(max_cpu_level, cpu_level)
        
        cpu_names = {1: "low", 2: "medium", 3: "high", 4: "very_high"}
        
        return {
            "memory": f"{max_memory}MB",
            "cpu": cpu_names[max_cpu_level],
            "estimated_peak_memory": max_memory,
            "estimated_cpu_utilization": max_cpu_level * 25  # 25% per level
        }
    
    def _identify_parallelizable_steps(self, steps: List[WorkflowStep]) -> List[List[str]]:
        """Identify groups of steps that can run in parallel"""
        
        parallelizable_groups = []
        
        # Group steps by dependency level
        dependency_levels = {}
        for step in steps:
            level = self._calculate_dependency_level(step, steps)
            if level not in dependency_levels:
                dependency_levels[level] = []
            dependency_levels[level].append(step.step_id)
        
        # Each level can potentially run in parallel
        for level, step_ids in dependency_levels.items():
            if len(step_ids) > 1:
                parallelizable_groups.append(step_ids)
        
        return parallelizable_groups
    
    def _calculate_critical_path(self, steps: List[WorkflowStep]) -> List[str]:
        """Calculate critical path through workflow"""
        
        # Build dependency graph
        dependency_graph = {}
        reverse_deps = {}
        
        for step in steps:
            dependency_graph[step.step_id] = {
                "duration": step.estimated_duration,
                "dependencies": step.dependencies
            }
            reverse_deps[step.step_id] = []
        
        # Build reverse dependency mapping
        for step_id, step_info in dependency_graph.items():
            for dep in step_info["dependencies"]:
                if dep in reverse_deps:
                    reverse_deps[dep].append(step_id)
        
        # Find critical path using longest path algorithm
        critical_path = []
        longest_paths = {}
        
        def calculate_longest_path(step_id):
            if step_id in longest_paths:
                return longest_paths[step_id]
            
            if not dependency_graph[step_id]["dependencies"]:
                longest_paths[step_id] = (dependency_graph[step_id]["duration"], [step_id])
                return longest_paths[step_id]
            
            max_duration = 0
            best_path = []
            
            for dep in dependency_graph[step_id]["dependencies"]:
                if dep in dependency_graph:
                    dep_duration, dep_path = calculate_longest_path(dep)
                    total_duration = dep_duration + dependency_graph[step_id]["duration"]
                    
                    if total_duration > max_duration:
                        max_duration = total_duration
                        best_path = dep_path + [step_id]
            
            longest_paths[step_id] = (max_duration, best_path)
            return longest_paths[step_id]
        
        # Calculate longest path for all steps
        max_duration = 0
        for step_id in dependency_graph:
            duration, path = calculate_longest_path(step_id)
            if duration > max_duration:
                max_duration = duration
                critical_path = path
        
        return critical_path
    
    def _calculate_workflow_signature(self, steps: List[WorkflowStep]) -> str:
        """Calculate signature for workflow pattern matching"""
        
        import hashlib
        
        # Create signature based on operation types and structure
        operations = [step.operation for step in steps]
        dependencies = [len(step.dependencies) for step in steps]
        
        signature_data = f"{len(steps)}_{operations}_{dependencies}"
        return hashlib.md5(signature_data.encode()).hexdigest()
    
    def _select_adaptive_level(self, historical_performance: Dict[str, Any]) -> WorkflowOptimizationLevel:
        """Select optimization level based on historical performance"""
        
        # Simple heuristic: if previous aggressive optimization worked well, use it
        if historical_performance.get("aggressive_success_rate", 0) > 0.8:
            return WorkflowOptimizationLevel.AGGRESSIVE
        elif historical_performance.get("standard_success_rate", 0) > 0.9:
            return WorkflowOptimizationLevel.STANDARD
        else:
            return WorkflowOptimizationLevel.BASIC
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"workflow_{timestamp}_{random_suffix}"


class CrossModalOrchestrator(CoreService):
    """Intelligent orchestration of cross-modal analysis workflows
    
    Coordinates mode selection, data conversion, and validation to provide
    optimal cross-modal analysis with workflow optimization and resource management.
    """
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
        self.config = get_config()
        self.logger = get_logger("analytics.cross_modal_orchestrator")
        
        # Initialize component services
        self.mode_selector = ModeSelectionService(service_manager)
        self.converter = CrossModalConverter(service_manager)
        self.validator = CrossModalValidator(self.converter, service_manager)
        self.workflow_optimizer = WorkflowOptimizer()
        
        # Performance tracking - with bounded collections to prevent memory leaks
        from collections import deque
        self.orchestration_history = deque(maxlen=100)  # Bounded to prevent memory leak
        self._history_lock = anyio.Lock()  # Thread safety for history
        self.performance_baselines = {}
        
        # Configuration
        self.default_validation_level = ValidationLevel.STANDARD
        self.default_optimization_level = WorkflowOptimizationLevel.STANDARD
        self.enable_caching = True
        
        # Cache with thread safety
        self._cache_lock = threading.Lock()
        self.cache = {}
        
        self.logger.info("CrossModalOrchestrator initialized")
    
    def initialize(self, config: Dict[str, Any]) -> ServiceResponse:
        """Initialize service with configuration"""
        try:
            # Initialize component services
            mode_selector_response = self.mode_selector.initialize(config.get("mode_selection", {}))
            converter_response = self.converter.initialize(config.get("converter", {}))
            validator_response = self.validator.initialize(config.get("validator", {}))
            
            # Check if all components initialized successfully
            if not all([mode_selector_response.success, converter_response.success, validator_response.success]):
                failed_components = []
                if not mode_selector_response.success:
                    failed_components.append("mode_selector")
                if not converter_response.success:
                    failed_components.append("converter")
                if not validator_response.success:
                    failed_components.append("validator")
                
                return create_service_response(
                    success=False,
                    data=None,
                    error_code="COMPONENT_INITIALIZATION_FAILED",
                    error_message=f"Failed to initialize components: {', '.join(failed_components)}"
                )
            
            # Update configuration
            self.default_validation_level = ValidationLevel(
                config.get('default_validation_level', ValidationLevel.STANDARD.value)
            )
            self.default_optimization_level = WorkflowOptimizationLevel(
                config.get('default_optimization_level', WorkflowOptimizationLevel.STANDARD.value)
            )
            self.enable_caching = config.get('enable_caching', True)
            
            self.logger.info("CrossModalOrchestrator initialized successfully")
            return create_service_response(
                success=True,
                data={"status": "initialized"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CrossModalOrchestrator: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="INITIALIZATION_FAILED",
                error_message=str(e)
            )
    
    async def health_check(self) -> ServiceResponse:
        """Check service health and readiness"""
        try:
            # Check component health
            component_health = {
                "mode_selector": (await self.mode_selector.health_check()).success,
                "converter": (await self.converter.health_check()).success,
                "validator": (await self.validator.health_check()).success,
                "workflow_optimizer": True  # Always healthy
            }
            
            overall_health = all(component_health.values())
            
            # Thread-safe access to history
            async with self._history_lock:
                history_size = len(self.orchestration_history)
            
            with self._cache_lock:
                cache_size = len(self.cache) if self.enable_caching else 0
            
            health_data = {
                "service_status": "healthy" if overall_health else "degraded",
                "component_health": component_health,
                "orchestration_history_size": history_size,
                "performance_baselines": len(self.performance_baselines),
                "cache_size": cache_size,
                "supported_modes": [mode.value for mode in AnalysisMode],
                "supported_formats": [fmt.value for fmt in DataFormat]
            }
            
            return create_service_response(
                success=overall_health,
                data=health_data,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def get_statistics(self) -> ServiceResponse:
        """Get service performance statistics"""
        try:
            # Get statistics without lock for monitoring (acceptable race condition)
            if not self.orchestration_history:
                    stats = {
                        "total_orchestrations": 0,
                        "success_rate": 0.0,
                        "average_execution_time": 0.0,
                        "average_workflow_efficiency": 0.0
                    }
            else:
                history_list = list(self.orchestration_history)
                total_orchestrations = len(history_list)
                successful_orchestrations = sum(1 for result in history_list if result.success)
                avg_execution_time = sum(result.execution_time for result in history_list) / total_orchestrations
                avg_efficiency = sum(result.workflow_efficiency for result in history_list) / total_orchestrations
                
                stats = {
                    "total_orchestrations": total_orchestrations,
                    "successful_orchestrations": successful_orchestrations,
                    "success_rate": successful_orchestrations / total_orchestrations,
                    "average_execution_time": avg_execution_time,
                    "average_workflow_efficiency": avg_efficiency,
                    "performance_baselines": len(self.performance_baselines),
                    "cache_hit_rate": self._calculate_cache_hit_rate()
                }
            
            return create_service_response(
                success=True,
                data=stats,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="STATISTICS_FAILED",
                error_message=str(e)
            )
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and capabilities"""
        return {
            "service_name": "CrossModalOrchestrator",
            "version": "1.0.0",
            "description": "Intelligent orchestration of cross-modal analysis workflows",
            "capabilities": [
                "intelligent_mode_selection",
                "data_format_conversion",
                "workflow_optimization", 
                "cross_modal_validation",
                "performance_monitoring",
                "result_aggregation"
            ],
            "supported_formats": [fmt.value for fmt in DataFormat],
            "supported_modes": [mode.value for mode in AnalysisMode],
            "optimization_levels": [level.value for level in WorkflowOptimizationLevel],
            "validation_levels": [level.value for level in ValidationLevel],
            "dependencies": [
                "ModeSelectionService",
                "CrossModalConverter", 
                "CrossModalValidator",
                "WorkflowOptimizer"
            ],
            "configuration_options": {
                "default_validation_level": "Level of validation to perform by default",
                "default_optimization_level": "Level of workflow optimization by default",
                "enable_caching": "Whether to enable result caching"
            },
            "performance_characteristics": {
                "typical_response_time": "5-30 seconds depending on data size and complexity",
                "memory_usage": "Moderate - scales with data size",
                "cpu_usage": "High during optimization and analysis phases"
            }
        }
    
    async def cleanup(self) -> ServiceResponse:
        """Clean up service resources"""
        try:
            # Clean up component services
            await self.mode_selector.cleanup()
            await self.converter.cleanup()
            await self.validator.cleanup()
            
            # History is automatically bounded by deque, no manual cleanup needed
            async with self._history_lock:
                if len(self.orchestration_history) > 90:
                    self.logger.debug(f"Orchestration history approaching limit: {len(self.orchestration_history)}/100")
            
            # Clean up cache (thread-safe)
            with self._cache_lock:
                if len(self.cache) > 1000:
                    # Keep only recent cache entries
                    cache_items = list(self.cache.items())
                    cache_items.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)
                    self.cache = dict(cache_items[:500])
            
            self.logger.info("CrossModalOrchestrator cleanup completed")
            return create_service_response(
                success=True,
                data={"status": "cleaned_up"},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return create_service_response(
                success=False,
                data=None,
                error_code="CLEANUP_FAILED",
                error_message=str(e)
            )
    
    async def orchestrate_analysis(
        self,
        research_question: str,
        data: Any,
        source_format: DataFormat,
        preferred_modes: Optional[List[AnalysisMode]] = None,
        validation_level: Optional[ValidationLevel] = None,
        optimization_level: Optional[WorkflowOptimizationLevel] = None,
        constraints: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Orchestrate optimal cross-modal analysis workflow"""
        request_id = self._generate_request_id()
        start_time = time.time()
        
        validation_level = validation_level or self.default_validation_level
        optimization_level = optimization_level or self.default_optimization_level
        
        self._log_analysis_start(request_id, research_question, source_format)
        
        try:
            # Create analysis request
            request = self._create_analysis_request(
                request_id, research_question, data, source_format,
                preferred_modes, validation_level, optimization_level,
                constraints, preferences
            )
            
            # Execute core analysis workflow
            result = await self._execute_core_analysis(request, start_time)
            
            # Post-process and store results
            await self._finalize_analysis_result(result, request)
            
            self._log_analysis_completion(request_id, result, time.time() - start_time)
            return result
            
        except Exception as e:
            return self._create_error_result(request_id, e, time.time() - start_time)
    
    def _log_analysis_start(self, request_id: str, research_question: str, source_format: DataFormat):
        """Log the start of analysis orchestration"""
        self.logger.info(
            f"Starting orchestrated analysis {request_id}: "
            f"question='{research_question[:100]}...', format={source_format.value}"
        )
    
    def _create_analysis_request(
        self,
        request_id: str,
        research_question: str,
        data: Any,
        source_format: DataFormat,
        preferred_modes: Optional[List[AnalysisMode]],
        validation_level: ValidationLevel,
        optimization_level: WorkflowOptimizationLevel,
        constraints: Optional[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]]
    ) -> AnalysisRequest:
        """Create analysis request object"""
        return AnalysisRequest(
            request_id=request_id,
            research_question=research_question,
            data=data,
            source_format=source_format,
            preferred_modes=preferred_modes,
            validation_level=validation_level,
            optimization_level=optimization_level,
            constraints=constraints,
            preferences=preferences
        )
    
    async def _execute_core_analysis(self, request: AnalysisRequest, start_time: float) -> AnalysisResult:
        """Execute the core analysis workflow steps"""
        # Step 1: Mode selection and workflow optimization
        data_context = self._create_data_context(request.data, request.source_format)
        mode_selection = await self.mode_selector.select_optimal_mode(
            request.research_question, data_context, request.preferences
        )
        
        optimized_workflow = await self._generate_optimized_workflow(
            request, mode_selection, data_context
        )
        
        # Step 2: Execute workflow
        execution_result = await self._execute_workflow(
            optimized_workflow, request, mode_selection
        )
        
        # Step 3: Validation and metrics
        validation_report = await self._perform_validation(
            execution_result, request
        )
        
        execution_time = time.time() - start_time
        performance_metrics, workflow_efficiency = self._calculate_metrics(
            optimized_workflow, execution_result, execution_time
        )
        
        recommendations = self._generate_analysis_recommendations(
            mode_selection, execution_result, validation_report, performance_metrics
        )
        
        # Step 4: Create final result
        return self._build_analysis_result(
            request, optimized_workflow, execution_result, data_context,
            mode_selection, performance_metrics, validation_report,
            execution_time, workflow_efficiency, recommendations
        )
    
    async def _perform_validation(
        self, 
        execution_result: Dict[str, Any], 
        request: AnalysisRequest
    ) -> Optional[Any]:
        """Perform result validation if required"""
        if request.validation_level != ValidationLevel.BASIC:
            return await self._validate_analysis_results(
                execution_result, request, request.validation_level
            )
        return None
    
    def _calculate_metrics(
        self, 
        workflow: Any, 
        execution_result: Dict[str, Any], 
        execution_time: float
    ) -> Tuple[Dict[str, Any], float]:
        """Calculate performance metrics and workflow efficiency"""
        performance_metrics = self._calculate_performance_metrics(
            workflow, execution_result, execution_time
        )
        workflow_efficiency = self._calculate_workflow_efficiency(
            workflow, execution_result, execution_time
        )
        return performance_metrics, workflow_efficiency
    
    def _build_analysis_result(
        self,
        request: AnalysisRequest,
        optimized_workflow: Any,
        execution_result: Dict[str, Any],
        data_context: Any,
        mode_selection: Any,
        performance_metrics: Dict[str, Any],
        validation_report: Optional[Any],
        execution_time: float,
        workflow_efficiency: float,
        recommendations: List[str]
    ) -> AnalysisResult:
        """Build the final analysis result object"""
        return AnalysisResult(
            request_id=request.request_id,
            workflow_id=optimized_workflow.workflow_id,
            success=execution_result.get("success", False),
            primary_result=execution_result.get("primary_result"),
            secondary_results=execution_result.get("secondary_results", []),
            analysis_metadata={
                "mode_selection": asdict(mode_selection),
                "workflow_optimization": optimized_workflow.optimization_metadata,
                "data_context": asdict(data_context)
            },
            performance_metrics=performance_metrics,
            validation_report=validation_report,
            execution_time=execution_time,
            workflow_efficiency=workflow_efficiency,
            recommendations=recommendations
        )
    
    async def _finalize_analysis_result(self, result: AnalysisResult, request: AnalysisRequest):
        """Store result in history and update baselines"""
        # Store in history (thread-safe, deque automatically bounds to 100)
        async with self._history_lock:
            self.orchestration_history.append(result)
        
        # Update performance baselines
        mode_selection = result.analysis_metadata.get("mode_selection")
        if mode_selection:
            self._update_performance_baselines(mode_selection, result.performance_metrics)
    
    def _log_analysis_completion(self, request_id: str, result: AnalysisResult, execution_time: float):
        """Log the completion of analysis orchestration"""
        self.logger.info(
            f"Orchestrated analysis {request_id} completed: "
            f"success={result.success}, efficiency={result.workflow_efficiency:.3f}, "
            f"time={execution_time:.2f}s"
        )
    
    def _create_error_result(self, request_id: str, error: Exception, execution_time: float) -> AnalysisResult:
        """Create error result for failed analysis"""
        self.logger.error(f"Orchestrated analysis {request_id} failed: {error}")
        
        return AnalysisResult(
            request_id=request_id,
            workflow_id="failed",
            success=False,
            primary_result=None,
            secondary_results=[],
            analysis_metadata={"error": str(error)},
            performance_metrics={},
            validation_report=None,
            execution_time=execution_time,
            workflow_efficiency=0.0,
            recommendations=[f"Fix orchestration error: {error}"]
        )
    
    def _create_data_context(self, data: Any, source_format: DataFormat) -> DataContext:
        """Create data context for mode selection"""
        
        # Calculate data characteristics
        data_size = self._calculate_data_size(data)
        data_types = self._identify_data_types(data, source_format)
        entity_count, relationship_count = self._count_entities_and_relationships(data, source_format)
        
        # Detect special data characteristics
        has_temporal_data = self._has_temporal_data(data, source_format)
        has_spatial_data = self._has_spatial_data(data, source_format)
        has_hierarchical_structure = self._has_hierarchical_structure(data, source_format)
        
        return create_data_context(
            data_size=data_size,
            data_types=data_types,
            entity_count=entity_count,
            relationship_count=relationship_count,
            has_temporal_data=has_temporal_data,
            has_spatial_data=has_spatial_data,
            has_hierarchical_structure=has_hierarchical_structure,
            available_formats=[source_format.value]
        )
    
    def _calculate_data_size(self, data: Any) -> int:
        """Calculate approximate data size"""
        try:
            if isinstance(data, dict):
                return len(json.dumps(data))
            elif hasattr(data, '__len__'):
                return len(data)
            else:
                return len(str(data))
        except Exception:
            return 1000  # Default size
    
    def _identify_data_types(self, data: Any, source_format: DataFormat) -> List[str]:
        """Identify data types in the data"""
        
        data_types = []
        
        if source_format == DataFormat.GRAPH:
            data_types.extend(["graph", "nodes", "edges"])
            if isinstance(data, dict):
                if data.get("nodes"):
                    data_types.append("entities")
                if data.get("edges"):
                    data_types.append("relationships")
        
        elif source_format == DataFormat.TABLE:
            data_types.extend(["table", "structured"])
            if hasattr(data, 'dtypes'):
                if any(data.dtypes == 'object'):
                    data_types.append("text")
                if any(data.dtypes.apply(lambda x: 'int' in str(x) or 'float' in str(x))):
                    data_types.append("numeric")
        
        elif source_format == DataFormat.VECTOR:
            data_types.extend(["vector", "embeddings"])
        
        return data_types
    
    def _count_entities_and_relationships(self, data: Any, source_format: DataFormat) -> Tuple[int, int]:
        """Count entities and relationships in the data"""
        
        entity_count = 0
        relationship_count = 0
        
        try:
            if source_format == DataFormat.GRAPH and isinstance(data, dict):
                entity_count = len(data.get("nodes", []))
                relationship_count = len(data.get("edges", []))
            
            elif source_format == DataFormat.TABLE and hasattr(data, '__len__'):
                entity_count = len(data)
                # Estimate relationships from data complexity
                if hasattr(data, 'columns') and len(data.columns) > 2:
                    relationship_count = entity_count // 2
            
            elif source_format == DataFormat.VECTOR:
                if hasattr(data, 'shape'):
                    entity_count = data.shape[0] if len(data.shape) > 0 else 1
        
        except Exception:
            pass
        
        return entity_count, relationship_count
    
    def _has_temporal_data(self, data: Any, source_format: DataFormat) -> bool:
        """Check if data has temporal components"""
        
        temporal_keywords = ['time', 'date', 'timestamp', 'created_at', 'updated_at', 'year', 'month']
        
        try:
            if source_format == DataFormat.GRAPH and isinstance(data, dict):
                # Check node and edge properties
                for node in data.get("nodes", []):
                    props = node.get("properties", {})
                    if any(keyword in str(key).lower() for key in props.keys() for keyword in temporal_keywords):
                        return True
                
                for edge in data.get("edges", []):
                    props = edge.get("properties", {})
                    if any(keyword in str(key).lower() for key in props.keys() for keyword in temporal_keywords):
                        return True
            
            elif source_format == DataFormat.TABLE and hasattr(data, 'columns'):
                return any(keyword in str(col).lower() for col in data.columns for keyword in temporal_keywords)
        
        except Exception:
            pass
        
        return False
    
    def _has_spatial_data(self, data: Any, source_format: DataFormat) -> bool:
        """Check if data has spatial components"""
        
        spatial_keywords = ['lat', 'lon', 'latitude', 'longitude', 'location', 'address', 'coord', 'geo']
        
        try:
            if source_format == DataFormat.GRAPH and isinstance(data, dict):
                # Check node properties for spatial data
                for node in data.get("nodes", []):
                    props = node.get("properties", {})
                    if any(keyword in str(key).lower() for key in props.keys() for keyword in spatial_keywords):
                        return True
            
            elif source_format == DataFormat.TABLE and hasattr(data, 'columns'):
                return any(keyword in str(col).lower() for col in data.columns for keyword in spatial_keywords)
        
        except Exception:
            pass
        
        return False
    
    def _has_hierarchical_structure(self, data: Any, source_format: DataFormat) -> bool:
        """Check if data has hierarchical structure"""
        
        try:
            if source_format == DataFormat.GRAPH and isinstance(data, dict):
                # Look for hierarchical relationship types
                hierarchical_relations = ['parent', 'child', 'contains', 'part_of', 'member_of']
                for edge in data.get("edges", []):
                    edge_type = edge.get("type", "").lower()
                    if any(rel in edge_type for rel in hierarchical_relations):
                        return True
            
            elif source_format == DataFormat.TABLE and hasattr(data, 'columns'):
                # Look for hierarchical column names
                hierarchical_cols = ['parent', 'child', 'level', 'depth', 'hierarchy']
                return any(keyword in str(col).lower() for col in data.columns for keyword in hierarchical_cols)
        
        except Exception:
            pass
        
        return False
    
    async def _generate_optimized_workflow(
        self,
        request: AnalysisRequest,
        mode_selection: ModeSelectionResult,
        data_context: DataContext
    ) -> OptimizedWorkflow:
        """Generate and optimize workflow for the analysis"""
        
        # Start with workflow steps from mode selection
        base_workflow_steps = mode_selection.workflow_steps
        
        # Add validation steps if requested
        if request.validation_level != ValidationLevel.BASIC:
            validation_steps = self._generate_validation_steps(request, mode_selection)
            base_workflow_steps.extend(validation_steps)
        
        # Optimize workflow
        optimized_workflow = await self.workflow_optimizer.optimize_workflow(
            base_workflow_steps, request.optimization_level, request.constraints
        )
        
        return optimized_workflow
    
    def _generate_validation_steps(
        self,
        request: AnalysisRequest,
        mode_selection: ModeSelectionResult
    ) -> List[Dict[str, Any]]:
        """Generate validation steps for the workflow"""
        
        validation_steps = []
        
        # Add conversion validation step
        validation_steps.append({
            "step_id": "conversion_validation",
            "step_type": "validation",
            "operation": "validate_conversion",
            "parameters": {
                "source_format": request.source_format.value,
                "target_format": mode_selection.primary_mode.value,
                "validation_level": request.validation_level.value
            },
            "dependencies": ["primary_analysis"],
            "estimated_duration": 30.0,
            "required_resources": {"memory": "200MB", "cpu": "medium"}
        })
        
        # Add integrity validation step for comprehensive validation
        if request.validation_level in [ValidationLevel.COMPREHENSIVE, ValidationLevel.STRESS_TEST]:
            validation_steps.append({
                "step_id": "integrity_validation",
                "step_type": "validation",
                "operation": "validate_integrity",
                "parameters": {
                    "validation_level": request.validation_level.value
                },
                "dependencies": ["conversion_validation"],
                "estimated_duration": 60.0,
                "required_resources": {"memory": "500MB", "cpu": "high"}
            })
        
        return validation_steps
    
    async def _execute_workflow(
        self,
        workflow: OptimizedWorkflow,
        request: AnalysisRequest,
        mode_selection: ModeSelectionResult
    ) -> Dict[str, Any]:
        """Execute the optimized workflow"""
        
        results = {}
        step_results = {}
        
        try:
            # Execute steps according to optimized workflow
            for step in workflow.steps:
                step_start_time = time.time()
                
                # Check if dependencies are satisfied
                if not self._dependencies_satisfied(step, step_results):
                    continue
                
                # Execute step
                step.status = "running"
                step_result = await self._execute_workflow_step(step, request, step_results)
                
                step.actual_duration = time.time() - step_start_time
                step.result = step_result
                
                if step_result.get("success", False):
                    step.status = "completed"
                    step_results[step.step_id] = step_result
                else:
                    step.status = "failed"
                    step.error = step_result.get("error", "Unknown error")
                    break
            
            # Aggregate results
            primary_result = self._extract_primary_result(step_results, mode_selection)
            secondary_results = self._extract_secondary_results(step_results, mode_selection)
            
            results = {
                "success": all(step.status == "completed" for step in workflow.steps),
                "primary_result": primary_result,
                "secondary_results": secondary_results,
                "step_results": step_results,
                "workflow_steps": workflow.steps
            }
            
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "step_results": step_results
            }
        
        return results
    
    def _dependencies_satisfied(self, step: WorkflowStep, step_results: Dict[str, Any]) -> bool:
        """Check if step dependencies are satisfied"""
        return all(dep_id in step_results for dep_id in step.dependencies)
    
    async def _execute_workflow_step(
        self,
        step: WorkflowStep,
        request: AnalysisRequest,
        step_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual workflow step"""
        
        try:
            if step.operation == "prepare_data_for_analysis":
                return await self._prepare_data_step(step, request)
            
            elif step.operation.startswith("execute_"):
                return await self._execute_analysis_step(step, request, step_results)
            
            elif step.operation == "aggregate_multimodal_results":
                return await self._aggregate_results_step(step, step_results)
            
            elif step.operation == "validate_conversion":
                return await self._validate_conversion_step(step, request, step_results)
            
            elif step.operation == "validate_integrity":
                return await self._validate_integrity_step(step, request, step_results)
            
            else:
                return {"success": False, "error": f"Unknown operation: {step.operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _prepare_data_step(self, step: WorkflowStep, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute data preparation step"""
        
        try:
            # For now, just pass through the data
            # In a full implementation, this would include data cleaning, validation, etc.
            return {
                "success": True,
                "prepared_data": request.data,
                "source_format": request.source_format.value,
                "metadata": {"preparation_completed": True}
            }
            
        except Exception as e:
            self.logger.error(f"Data preparation failed: {e}")
            return {
                "success": False,
                "error": f"Data preparation failed: {e}",
                "metadata": {"preparation_completed": False}
            }
    
    async def _execute_analysis_step(
        self,
        step: WorkflowStep,
        request: AnalysisRequest,
        step_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute analysis step"""
        
        try:
            # Extract mode from operation name
            mode_name = step.operation.replace("execute_", "")
            target_format = self._mode_to_format(mode_name)
            
            if target_format != request.source_format:
                # Need to convert data
                conversion_result = await self.converter.convert_data(
                    request.data,
                    request.source_format,
                    target_format,
                    preserve_semantics=True
                )
                
                if not conversion_result.validation_passed:
                    return {
                        "success": False,
                        "error": "Data conversion failed",
                        "conversion_warnings": conversion_result.warnings
                    }
                
                analysis_data = conversion_result.data
            else:
                analysis_data = request.data
            
            # Execute analysis (placeholder - would call actual analysis tools)
            analysis_result = {
                "success": True,
                "analysis_mode": mode_name,
                "data_format": target_format.value,
                "result_data": analysis_data,
                "analysis_metadata": {
                    "entities_analyzed": self._count_entities(analysis_data, target_format),
                    "analysis_type": "cross_modal_" + mode_name
                }
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Analysis step execution failed: {e}")
            return {
                "success": False,
                "error": f"Analysis execution failed: {e}",
                "analysis_mode": step.operation.replace("execute_", "")
            }
    
    async def _aggregate_results_step(
        self,
        step: WorkflowStep,
        step_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute result aggregation step"""
        
        try:
            # Collect all analysis results
            analysis_results = []
            for step_id, result in step_results.items():
                if result.get("analysis_mode"):
                    analysis_results.append(result)
            
            if not analysis_results:
                return {"success": False, "error": "No analysis results to aggregate"}
            
            # Simple aggregation (in a full implementation, this would be more sophisticated)
            aggregated_result = {
                "success": True,
                "aggregated_data": {
                    "primary_analysis": analysis_results[0] if analysis_results else None,
                    "secondary_analyses": analysis_results[1:] if len(analysis_results) > 1 else [],
                    "total_entities": sum(
                        result.get("analysis_metadata", {}).get("entities_analyzed", 0)
                        for result in analysis_results
                    ),
                    "analysis_modes_used": [
                        result.get("analysis_mode") for result in analysis_results
                    ]
                },
                "aggregation_metadata": {
                    "results_combined": len(analysis_results),
                    "aggregation_method": "simple_combination"
                }
            }
            
            return aggregated_result
            
        except Exception as e:
            self.logger.error(f"Results aggregation failed: {e}")
            return {
                "success": False,
                "error": f"Results aggregation failed: {e}",
                "aggregation_metadata": {"aggregation_method": "failed"}
            }
    
    async def _validate_conversion_step(
        self,
        step: WorkflowStep,
        request: AnalysisRequest,
        step_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute conversion validation step"""
        
        try:
            validation_level = ValidationLevel(step.parameters["validation_level"])
            source_format = DataFormat(step.parameters["source_format"])
            target_format = DataFormat(step.parameters["target_format"])
            
            validation_report = await self.validator.validate_cross_modal_conversion(
                request.data, source_format, target_format, validation_level
            )
            
            return {
                "success": validation_report.overall_passed,
                "validation_report": validation_report,
                "validation_score": validation_report.overall_score,
                "recommendations": validation_report.recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Conversion validation failed: {e}")
            return {
                "success": False,
                "error": f"Conversion validation failed: {e}",
                "validation_score": 0.0,
                "recommendations": ["Fix validation errors before proceeding"]
            }
    
    async def _validate_integrity_step(
        self,
        step: WorkflowStep,
        request: AnalysisRequest,
        step_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute integrity validation step"""
        
        try:
            validation_level = ValidationLevel(step.parameters["validation_level"])
            
            # Perform round-trip validation
            format_sequence = [
                request.source_format,
                DataFormat.TABLE,  # Intermediate format
                request.source_format
            ]
            
            validation_report = await self.validator.validate_round_trip_integrity(
                request.data, format_sequence, validation_level
            )
            
            return {
                "success": validation_report.overall_passed,
                "integrity_report": validation_report,
                "integrity_score": validation_report.overall_score,
                "recommendations": validation_report.recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Integrity validation failed: {e}")
            return {
                "success": False,
                "error": f"Integrity validation failed: {e}",
                "integrity_score": 0.0,
                "recommendations": ["Fix integrity validation errors before proceeding"]
            }
    
    def _mode_to_format(self, mode_name: str) -> DataFormat:
        """Convert analysis mode to data format"""
        
        mode_format_map = {
            "graph_analysis": DataFormat.GRAPH,
            "table_analysis": DataFormat.TABLE,
            "vector_analysis": DataFormat.VECTOR,
            "hybrid_graph_table": DataFormat.GRAPH,
            "hybrid_graph_vector": DataFormat.GRAPH,
            "hybrid_table_vector": DataFormat.TABLE,
            "comprehensive_multimodal": DataFormat.GRAPH  # Default to graph
        }
        
        return mode_format_map.get(mode_name, DataFormat.TABLE)
    
    def _count_entities(self, data: Any, data_format: DataFormat) -> int:
        """Count entities in data"""
        
        try:
            if data_format == DataFormat.GRAPH and isinstance(data, dict):
                return len(data.get("nodes", []))
            elif data_format == DataFormat.TABLE and hasattr(data, '__len__'):
                return len(data)
            elif data_format == DataFormat.VECTOR and hasattr(data, 'shape'):
                return data.shape[0] if len(data.shape) > 0 else 1
        except Exception:
            pass
        
        return 0
    
    def _extract_primary_result(
        self,
        step_results: Dict[str, Any],
        mode_selection: ModeSelectionResult
    ) -> Any:
        """Extract primary result from step results"""
        
        # Look for primary analysis result
        primary_step_id = f"execute_{mode_selection.primary_mode.value}"
        
        for step_id, result in step_results.items():
            if step_id == "primary_analysis" or step_id == primary_step_id:
                return result.get("result_data")
        
        # Fallback to aggregated result
        for step_id, result in step_results.items():
            if "aggregated" in step_id:
                return result.get("aggregated_data")
        
        return None
    
    def _extract_secondary_results(
        self,
        step_results: Dict[str, Any],
        mode_selection: ModeSelectionResult
    ) -> List[Any]:
        """Extract secondary results from step results"""
        
        secondary_results = []
        
        # Look for secondary analysis results
        for mode in mode_selection.secondary_modes:
            step_id = f"execute_{mode.value}"
            if step_id in step_results:
                secondary_results.append(step_results[step_id].get("result_data"))
        
        return secondary_results
    
    async def _validate_analysis_results(
        self,
        execution_result: Dict[str, Any],
        request: AnalysisRequest,
        validation_level: ValidationLevel
    ) -> Optional[ValidationReport]:
        """Validate analysis results"""
        
        try:
            # Extract validation results from execution
            validation_results = []
            
            for step_id, result in execution_result.get("step_results", {}).items():
                if "validation" in step_id and result.get("validation_report"):
                    validation_results.append(result["validation_report"])
            
            # If we have validation results, return the most comprehensive one
            if validation_results:
                return max(validation_results, key=lambda r: r.total_tests)
            
            # Otherwise, perform basic validation
            return await self.validator.validate_cross_modal_conversion(
                request.data, request.source_format, request.source_format, validation_level
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to validate analysis results: {e}")
            return None
    
    def _calculate_performance_metrics(
        self,
        workflow: OptimizedWorkflow,
        execution_result: Dict[str, Any],
        execution_time: float
    ) -> Dict[str, Any]:
        """Calculate performance metrics for the analysis"""
        
        estimated_time = workflow.estimated_total_duration
        actual_steps = execution_result.get("workflow_steps", [])
        
        metrics = {
            "execution_time": execution_time,
            "estimated_time": estimated_time,
            "time_accuracy": min(1.0, estimated_time / max(0.1, execution_time)),
            "steps_completed": sum(1 for step in actual_steps if step.status == "completed"),
            "steps_failed": sum(1 for step in actual_steps if step.status == "failed"),
            "total_steps": len(actual_steps),
            "completion_rate": sum(1 for step in actual_steps if step.status == "completed") / max(1, len(actual_steps))
        }
        
        # Resource utilization metrics
        if actual_steps:
            avg_step_time = sum(step.actual_duration or 0 for step in actual_steps) / len(actual_steps)
            max_step_time = max((step.actual_duration or 0 for step in actual_steps), default=0)
            
            metrics.update({
                "average_step_time": avg_step_time,
                "longest_step_time": max_step_time,
                "parallelization_benefit": len(workflow.parallelizable_steps) / max(1, len(actual_steps))
            })
        
        return metrics
    
    def _calculate_workflow_efficiency(
        self,
        workflow: OptimizedWorkflow,
        execution_result: Dict[str, Any],
        execution_time: float
    ) -> float:
        """Calculate overall workflow efficiency"""
        
        # Base efficiency on time accuracy and completion rate
        estimated_time = workflow.estimated_total_duration
        time_efficiency = min(1.0, estimated_time / max(0.1, execution_time))
        
        actual_steps = execution_result.get("workflow_steps", [])
        completion_rate = sum(1 for step in actual_steps if step.status == "completed") / max(1, len(actual_steps))
        
        # Overall efficiency is a combination of time and completion efficiency
        overall_efficiency = (time_efficiency + completion_rate) / 2
        
        # Bonus for optimization benefits
        optimization_bonus = len(workflow.optimization_metadata.get("changes_made", [])) * 0.05
        
        return min(1.0, overall_efficiency + optimization_bonus)
    
    def _generate_analysis_recommendations(
        self,
        mode_selection: ModeSelectionResult,
        execution_result: Dict[str, Any],
        validation_report: Optional[ValidationReport],
        performance_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis results"""
        
        recommendations = []
        
        # Mode selection recommendations
        if mode_selection.confidence < 0.8:
            recommendations.append("Consider providing more specific research question for better mode selection")
        
        if mode_selection.fallback_used:
            recommendations.append("LLM-based mode selection failed, using rule-based fallback")
        
        # Performance recommendations
        if performance_metrics.get("completion_rate", 1.0) < 1.0:
            recommendations.append("Some workflow steps failed - check data compatibility and resource availability")
        
        if performance_metrics.get("time_accuracy", 1.0) < 0.5:
            recommendations.append("Execution time significantly exceeded estimates - consider workflow optimization")
        
        # Validation recommendations
        if validation_report and not validation_report.overall_passed:
            recommendations.extend(validation_report.recommendations)
        
        # Data-specific recommendations
        if not execution_result.get("success", False):
            recommendations.append("Analysis failed - verify data format and content")
        
        return recommendations
    
    def _update_performance_baselines(
        self,
        mode_selection: ModeSelectionResult,
        performance_metrics: Dict[str, Any]
    ) -> None:
        """Update performance baselines for future optimizations"""
        
        baseline_key = f"{mode_selection.primary_mode.value}_baseline"
        current_baseline = self.performance_baselines.get(baseline_key, {})
        
        # Update with new performance data
        execution_time = performance_metrics.get("execution_time", 0)
        if not current_baseline or execution_time < current_baseline.get("best_time", float('inf')):
            self.performance_baselines[baseline_key] = {
                "best_time": execution_time,
                "completion_rate": performance_metrics.get("completion_rate", 0),
                "last_updated": datetime.now().isoformat()
            }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        
        if not self.enable_caching or not self.cache:
            return 0.0
        
        total_accesses = sum(item.get("access_count", 0) for item in self.cache.values())
        cache_hits = sum(item.get("hit_count", 0) for item in self.cache.values())
        
        return cache_hits / max(1, total_accesses)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"analysis_{timestamp}_{random_suffix}"