"""
Dynamic Dependency Resolver

Resolves tool dependencies dynamically based on runtime conditions.
Handles conditional dependencies, dynamic tool selection, and adaptive execution.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..analysis.contract_analyzer import ToolContractAnalyzer, DependencyGraph
from .dag_builder import ExecutionDAG, DAGNode
from .execution_planner import ExecutionPlan, ExecutionStep
from ..nlp.advanced_intent_classifier import QuestionIntent
from ..nlp.context_extractor import QuestionContext

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies"""
    HARD = "hard"               # Must be satisfied
    SOFT = "soft"               # Preferred but optional
    CONDITIONAL = "conditional"  # Depends on runtime conditions
    ADAPTIVE = "adaptive"       # Changes based on context


@dataclass
class DependencyRequirement:
    """Single dependency requirement"""
    dependency_id: str
    dependency_type: DependencyType
    required_data: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    priority: float = 1.0
    optional: bool = False


@dataclass
class ResolutionContext:
    """Context for dependency resolution"""
    available_tools: Set[str]
    completed_tools: Set[str]
    failed_tools: Set[str]
    intermediate_results: Dict[str, Any]
    execution_constraints: Dict[str, Any]
    runtime_conditions: Dict[str, Any]
    question_context: Optional[QuestionContext] = None


@dataclass
class ResolutionResult:
    """Result of dependency resolution"""
    resolved_dependencies: Dict[str, List[str]]
    unresolved_dependencies: Dict[str, List[DependencyRequirement]]
    alternative_paths: Dict[str, List[List[str]]]
    resolution_confidence: float
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class DynamicDependencyResolver:
    """Resolves tool dependencies dynamically at runtime"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with contract analyzer"""
        self.contract_analyzer = ToolContractAnalyzer(contracts_dir)
        self.logger = logger
        
        # Load static dependency graph
        self.base_dependency_graph = self.contract_analyzer.build_dependency_graph()
        
        # Conditional dependency rules
        self.conditional_rules = self._load_conditional_rules()
        
        # Alternative tool mappings
        self.alternative_mappings = self._load_alternative_mappings()
    
    def resolve_dependencies(self, execution_plan: ExecutionPlan,
                           context: ResolutionContext) -> ResolutionResult:
        """Resolve dependencies for an execution plan"""
        
        self.logger.info(f"Resolving dependencies for {len(execution_plan.steps)} steps")
        
        resolved_deps = {}
        unresolved_deps = {}
        alternative_paths = {}
        warnings = []
        suggestions = []
        
        # Process each step in the execution plan
        for step in execution_plan.steps:
            step_result = self._resolve_step_dependencies(step, context)
            
            resolved_deps[step.step_id] = step_result.resolved_dependencies.get(step.step_id, [])
            
            if step.step_id in step_result.unresolved_dependencies:
                unresolved_deps[step.step_id] = step_result.unresolved_dependencies[step.step_id]
            
            if step.step_id in step_result.alternative_paths:
                alternative_paths[step.step_id] = step_result.alternative_paths[step.step_id]
            
            warnings.extend(step_result.warnings)
            suggestions.extend(step_result.suggestions)
        
        # Calculate overall resolution confidence
        total_deps = sum(len(deps) for deps in resolved_deps.values())
        total_unresolved = sum(len(deps) for deps in unresolved_deps.values())
        confidence = total_deps / (total_deps + total_unresolved) if (total_deps + total_unresolved) > 0 else 1.0
        
        result = ResolutionResult(
            resolved_dependencies=resolved_deps,
            unresolved_dependencies=unresolved_deps,
            alternative_paths=alternative_paths,
            resolution_confidence=confidence,
            warnings=warnings,
            suggestions=suggestions
        )
        
        self.logger.info(f"Dependency resolution complete: {confidence:.1%} resolved")
        return result
    
    def _resolve_step_dependencies(self, step: ExecutionStep, 
                                  context: ResolutionContext) -> ResolutionResult:
        """Resolve dependencies for a single execution step"""
        
        resolved = {}
        unresolved = {}
        alternatives = {}
        warnings = []
        suggestions = []
        
        # Get base dependencies for each tool in the step
        all_requirements = []
        
        for tool_id in step.tool_ids:
            requirements = self._get_tool_requirements(tool_id, step, context)
            all_requirements.extend(requirements)
        
        # Resolve each requirement
        resolved_list = []
        unresolved_list = []
        
        for req in all_requirements:
            resolution = self._resolve_single_requirement(req, context)
            
            if resolution['resolved']:
                resolved_list.extend(resolution['dependencies'])
            else:
                unresolved_list.append(req)
                
                # Look for alternatives
                if req.alternatives:
                    alt_paths = self._find_alternative_paths(req, context)
                    if alt_paths:
                        alternatives[step.step_id] = alt_paths
                        suggestions.append(f"Alternative paths available for {req.dependency_id}")
        
        if resolved_list:
            resolved[step.step_id] = resolved_list
        
        if unresolved_list:
            unresolved[step.step_id] = unresolved_list
            warnings.append(f"Unresolved dependencies in step {step.step_id}")
        
        return ResolutionResult(
            resolved_dependencies=resolved,
            unresolved_dependencies=unresolved,
            alternative_paths=alternatives,
            resolution_confidence=1.0,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _get_tool_requirements(self, tool_id: str, step: ExecutionStep, 
                              context: ResolutionContext) -> List[DependencyRequirement]:
        """Get dependency requirements for a tool"""
        
        requirements = []
        
        # Get static dependencies from contracts
        if tool_id in self.base_dependency_graph.edges:
            static_deps = self.base_dependency_graph.edges[tool_id]
            
            for dep_id in static_deps:
                req = DependencyRequirement(
                    dependency_id=dep_id,
                    dependency_type=DependencyType.HARD,
                    required_data=[f"output_of_{dep_id}"]
                )
                requirements.append(req)
        
        # Add conditional dependencies
        conditional_deps = self._get_conditional_dependencies(tool_id, step, context)
        requirements.extend(conditional_deps)
        
        # Add adaptive dependencies
        adaptive_deps = self._get_adaptive_dependencies(tool_id, step, context)
        requirements.extend(adaptive_deps)
        
        return requirements
    
    def _get_conditional_dependencies(self, tool_id: str, step: ExecutionStep,
                                     context: ResolutionContext) -> List[DependencyRequirement]:
        """Get conditional dependencies based on runtime conditions"""
        
        conditional_deps = []
        
        # Check conditional rules
        for rule in self.conditional_rules.get(tool_id, []):
            if self._evaluate_condition(rule['condition'], context):
                req = DependencyRequirement(
                    dependency_id=rule['dependency'],
                    dependency_type=DependencyType.CONDITIONAL,
                    conditions=[rule['condition']],
                    optional=rule.get('optional', False)
                )
                conditional_deps.append(req)
        
        return conditional_deps
    
    def _get_adaptive_dependencies(self, tool_id: str, step: ExecutionStep,
                                  context: ResolutionContext) -> List[DependencyRequirement]:
        """Get adaptive dependencies based on question context"""
        
        adaptive_deps = []
        
        # Temporal context dependencies
        if (context.question_context and 
            hasattr(context.question_context, 'temporal_context') and
            context.question_context.temporal_context):
            
            # Tools that benefit from temporal filtering
            if tool_id in ['T23A_SPACY_NER', 'T27_RELATIONSHIP_EXTRACTOR']:
                req = DependencyRequirement(
                    dependency_id='temporal_filter',
                    dependency_type=DependencyType.ADAPTIVE,
                    required_data=['temporal_context'],
                    optional=True
                )
                adaptive_deps.append(req)
        
        # Entity context dependencies
        if (context.question_context and
            hasattr(context.question_context, 'entity_context') and
            context.question_context.entity_context):
            
            # Tools that benefit from entity context
            if tool_id in ['T31_ENTITY_BUILDER', 'T49_MULTI_HOP_QUERY']:
                req = DependencyRequirement(
                    dependency_id='entity_context',
                    dependency_type=DependencyType.ADAPTIVE,
                    required_data=['entity_mentions'],
                    optional=True
                )
                adaptive_deps.append(req)
        
        return adaptive_deps
    
    def _resolve_single_requirement(self, req: DependencyRequirement,
                                   context: ResolutionContext) -> Dict[str, Any]:
        """Resolve a single dependency requirement"""
        
        # Check if dependency is available
        if req.dependency_id in context.available_tools:
            # Check if already completed
            if req.dependency_id in context.completed_tools:
                return {
                    'resolved': True,
                    'dependencies': [req.dependency_id],
                    'method': 'completed'
                }
            
            # Check if failed
            if req.dependency_id in context.failed_tools:
                if req.optional or req.alternatives:
                    return {
                        'resolved': False,
                        'dependencies': [],
                        'method': 'failed_optional'
                    }
                else:
                    return {
                        'resolved': False,
                        'dependencies': [],
                        'method': 'failed_required'
                    }
            
            # Dependency is available but not yet executed
            return {
                'resolved': True,
                'dependencies': [req.dependency_id],
                'method': 'scheduled'
            }
        
        # Check for alternatives
        if req.alternatives:
            for alt_id in req.alternatives:
                if alt_id in context.available_tools and alt_id not in context.failed_tools:
                    return {
                        'resolved': True,
                        'dependencies': [alt_id],
                        'method': 'alternative'
                    }
        
        # Check if optional
        if req.optional:
            return {
                'resolved': True,
                'dependencies': [],
                'method': 'optional_skipped'
            }
        
        # Unresolved
        return {
            'resolved': False,
            'dependencies': [],
            'method': 'unresolved'
        }
    
    def _find_alternative_paths(self, req: DependencyRequirement,
                               context: ResolutionContext) -> List[List[str]]:
        """Find alternative execution paths for unresolved dependencies"""
        
        alternative_paths = []
        
        # Check direct alternatives
        for alt_id in req.alternatives:
            if alt_id in context.available_tools:
                alternative_paths.append([alt_id])
        
        # Check tool mappings for functional alternatives
        if req.dependency_id in self.alternative_mappings:
            for alt_mapping in self.alternative_mappings[req.dependency_id]:
                if all(tool in context.available_tools for tool in alt_mapping):
                    alternative_paths.append(alt_mapping)
        
        return alternative_paths
    
    def _evaluate_condition(self, condition: str, context: ResolutionContext) -> bool:
        """Evaluate a conditional dependency condition"""
        
        # Simple condition evaluation
        if condition == "has_temporal_data":
            return bool(context.runtime_conditions.get('temporal_data'))
        
        elif condition == "complex_query":
            return context.runtime_conditions.get('query_complexity', 'simple') == 'complex'
        
        elif condition == "large_dataset":
            return context.runtime_conditions.get('dataset_size', 'small') == 'large'
        
        elif condition == "high_accuracy_required":
            return context.execution_constraints.get('quality_threshold', 0.8) > 0.9
        
        # Default to False for unknown conditions
        return False
    
    def _load_conditional_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load conditional dependency rules"""
        
        return {
            'T68_PAGE_RANK': [
                {
                    'condition': 'large_dataset',
                    'dependency': 'T68_PREPROCESSING',
                    'optional': True
                }
            ],
            'T49_MULTI_HOP_QUERY': [
                {
                    'condition': 'complex_query',
                    'dependency': 'T49_QUERY_OPTIMIZER',
                    'optional': True
                }
            ],
            'T23A_SPACY_NER': [
                {
                    'condition': 'high_accuracy_required',
                    'dependency': 'T23A_QUALITY_VALIDATOR',
                    'optional': True
                }
            ]
        }
    
    def _load_alternative_mappings(self) -> Dict[str, List[List[str]]]:
        """Load alternative tool mappings"""
        
        return {
            'T23A_SPACY_NER': [
                ['T23B_ALTERNATIVE_NER'],  # Alternative NER tool
                ['T23A_SPACY_NER_SIMPLE']  # Simplified version
            ],
            'T68_PAGE_RANK': [
                ['T68_CENTRALITY_ALTERNATIVE'],  # Alternative centrality measure
                ['T68_SIMPLE_RANKING']  # Simplified ranking
            ]
        }
    
    def adapt_execution_plan(self, execution_plan: ExecutionPlan,
                           resolution_result: ResolutionResult,
                           context: ResolutionContext) -> ExecutionPlan:
        """Adapt execution plan based on dependency resolution results"""
        
        self.logger.info("Adapting execution plan based on dependency resolution")
        
        adapted_steps = []
        
        for step in execution_plan.steps:
            adapted_step = self._adapt_execution_step(step, resolution_result, context)
            adapted_steps.append(adapted_step)
        
        # Create new execution plan with adapted steps
        adapted_plan = ExecutionPlan(
            plan_id=f"{execution_plan.plan_id}_adapted",
            steps=adapted_steps,
            strategy=execution_plan.strategy,
            total_estimated_time=execution_plan.total_estimated_time,
            total_estimated_cost=execution_plan.total_estimated_cost,
            parallelization_ratio=execution_plan.parallelization_ratio,
            resource_efficiency=execution_plan.resource_efficiency,
            quality_score=execution_plan.quality_score,
            confidence=execution_plan.confidence * resolution_result.resolution_confidence,
            dag=execution_plan.dag,
            constraints=execution_plan.constraints,
            adaptive_features=execution_plan.adaptive_features + ['dependency_adaptation']
        )
        
        self.logger.info(f"Execution plan adapted with {len(adapted_steps)} steps")
        return adapted_plan
    
    def _adapt_execution_step(self, step: ExecutionStep, 
                             resolution_result: ResolutionResult,
                             context: ResolutionContext) -> ExecutionStep:
        """Adapt a single execution step based on resolution results"""
        
        adapted_step = ExecutionStep(
            step_id=step.step_id,
            node_id=step.node_id,
            tool_ids=step.tool_ids.copy(),
            estimated_start_time=step.estimated_start_time,
            estimated_duration=step.estimated_duration,
            depends_on=step.depends_on.copy(),
            resource_allocation=step.resource_allocation.copy(),
            execution_priority=step.execution_priority,
            conditions=step.conditions.copy(),
            adaptive_parameters=step.adaptive_parameters.copy()
        )
        
        # Update dependencies based on resolution
        if step.step_id in resolution_result.resolved_dependencies:
            resolved_deps = resolution_result.resolved_dependencies[step.step_id]
            adapted_step.depends_on = list(set(adapted_step.depends_on + resolved_deps))
        
        # Add alternative paths if main dependencies failed
        if step.step_id in resolution_result.alternative_paths:
            alternatives = resolution_result.alternative_paths[step.step_id]
            if alternatives:
                # Use first alternative path
                alt_path = alternatives[0]
                adapted_step.depends_on = list(set(adapted_step.depends_on + alt_path))
                adapted_step.adaptive_parameters['using_alternatives'] = alt_path
        
        # Add conditions based on unresolved dependencies
        if step.step_id in resolution_result.unresolved_dependencies:
            unresolved = resolution_result.unresolved_dependencies[step.step_id]
            for req in unresolved:
                if not req.optional:
                    adapted_step.conditions.append(f"verify_{req.dependency_id}_available")
        
        return adapted_step
    
    def validate_resolution(self, resolution_result: ResolutionResult) -> Dict[str, Any]:
        """Validate the dependency resolution result"""
        
        validation = {
            'is_valid': True,
            'critical_issues': [],
            'warnings': resolution_result.warnings.copy(),
            'recommendations': resolution_result.suggestions.copy()
        }
        
        # Check for critical unresolved dependencies
        for step_id, unresolved_deps in resolution_result.unresolved_dependencies.items():
            critical_deps = [dep for dep in unresolved_deps 
                           if dep.dependency_type == DependencyType.HARD and not dep.optional]
            
            if critical_deps:
                validation['is_valid'] = False
                validation['critical_issues'].append(
                    f"Step {step_id} has unresolved critical dependencies: "
                    f"{[dep.dependency_id for dep in critical_deps]}"
                )
        
        # Check resolution confidence
        if resolution_result.resolution_confidence < 0.8:
            validation['warnings'].append(
                f"Low resolution confidence: {resolution_result.resolution_confidence:.1%}"
            )
        
        return validation
    
    def get_dependency_summary(self, resolution_result: ResolutionResult) -> str:
        """Generate human-readable summary of dependency resolution"""
        
        lines = []
        lines.append("DEPENDENCY RESOLUTION SUMMARY")
        lines.append("=" * 50)
        lines.append(f"Resolution Confidence: {resolution_result.resolution_confidence:.1%}")
        lines.append("")
        
        # Resolved dependencies
        total_resolved = sum(len(deps) for deps in resolution_result.resolved_dependencies.values())
        lines.append(f"Resolved Dependencies: {total_resolved}")
        
        for step_id, deps in resolution_result.resolved_dependencies.items():
            if deps:
                lines.append(f"  {step_id}: {deps}")
        
        # Unresolved dependencies
        total_unresolved = sum(len(deps) for deps in resolution_result.unresolved_dependencies.values())
        if total_unresolved > 0:
            lines.append(f"\nUnresolved Dependencies: {total_unresolved}")
            
            for step_id, deps in resolution_result.unresolved_dependencies.items():
                if deps:
                    lines.append(f"  {step_id}: {[dep.dependency_id for dep in deps]}")
        
        # Alternative paths
        if resolution_result.alternative_paths:
            lines.append(f"\nAlternative Paths Available:")
            for step_id, paths in resolution_result.alternative_paths.items():
                lines.append(f"  {step_id}: {len(paths)} alternatives")
        
        # Warnings and suggestions
        if resolution_result.warnings:
            lines.append(f"\nWarnings:")
            for warning in resolution_result.warnings:
                lines.append(f"  ⚠️  {warning}")
        
        if resolution_result.suggestions:
            lines.append(f"\nSuggestions:")
            for suggestion in resolution_result.suggestions:
                lines.append(f"  💡 {suggestion}")
        
        return "\n".join(lines)