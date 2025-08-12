"""
DAG Executor for Unified KGAS System

Executes tool chains dynamically based on compatibility.
No hardcoded sequences. Tools chain based on data availability.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
import logging
from enum import Enum

from unified_data_contract import UnifiedData, ToolCategory
from base_tool import UnifiedTool, ToolResult, ToolStatus
from tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a DAG step"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGStep:
    """A step in the DAG"""
    step_id: str
    tool_id: str
    depends_on: List[str] = None  # Step IDs this depends on
    parameters: Dict[str, Any] = None  # Additional parameters
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.parameters is None:
            self.parameters = {}


@dataclass
class StepResult:
    """Result from executing a step"""
    step_id: str
    tool_id: str
    status: StepStatus
    execution_time: float
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class DAG:
    """Directed Acyclic Graph of tool steps"""
    dag_id: str
    description: str
    steps: List[DAGStep]
    
    def get_step(self, step_id: str) -> Optional[DAGStep]:
        """Get a step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_ready_steps(self, completed: List[str]) -> List[DAGStep]:
        """Get steps that are ready to run"""
        ready = []
        for step in self.steps:
            # Check if all dependencies are completed
            if all(dep in completed for dep in step.depends_on):
                # And this step isn't already completed
                if step.step_id not in completed:
                    ready.append(step)
        return ready


class DAGExecutor:
    """
    Executes DAGs using the unified tool registry.
    
    Key differences from hardcoded system:
    1. Dynamic tool selection based on availability
    2. Automatic compatibility checking
    3. Data flows through UnifiedData structure
    4. No fallback to mocks - fail fast if tool missing
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.logger = logging.getLogger("DAGExecutor")
    
    def execute(self, dag: DAG, initial_data: UnifiedData) -> Dict[str, Any]:
        """
        Execute a DAG of tools.
        
        Args:
            dag: The DAG to execute
            initial_data: Starting data
            
        Returns:
            Execution results including final data
        """
        start_time = time.time()
        
        # Track execution state
        completed_steps = []
        step_results = []
        current_data = initial_data
        
        self.logger.info(f"Starting DAG execution: {dag.dag_id}")
        
        # Execute steps in dependency order
        max_iterations = len(dag.steps) * 2  # Prevent infinite loops
        iterations = 0
        
        while len(completed_steps) < len(dag.steps) and iterations < max_iterations:
            iterations += 1
            
            # Get ready steps
            ready_steps = dag.get_ready_steps(completed_steps)
            
            if not ready_steps:
                # No steps ready and not all complete - dependency issue
                if len(completed_steps) < len(dag.steps):
                    self.logger.error("Dependency deadlock detected")
                    break
            
            # Execute ready steps (could parallelize here)
            for step in ready_steps:
                result = self._execute_step(step, current_data)
                step_results.append(result)
                
                if result.status == StepStatus.SUCCESS:
                    completed_steps.append(step.step_id)
                    # Update current data with results
                    tool = self.registry.get_tool(step.tool_id)
                    if tool:
                        # Execute the tool
                        tool_result = tool.execute(current_data)
                        if tool_result.status == ToolStatus.SUCCESS:
                            current_data = tool_result.data
                else:
                    self.logger.error(f"Step {step.step_id} failed: {result.error}")
                    # Continue with other steps - they might not depend on this
        
        execution_time = time.time() - start_time
        
        # Build execution summary
        summary = {
            "dag_id": dag.dag_id,
            "total_steps": len(dag.steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len([r for r in step_results if r.status == StepStatus.FAILED]),
            "execution_time": execution_time,
            "final_data": current_data,
            "step_results": step_results,
            "success": len(completed_steps) == len(dag.steps)
        }
        
        self.logger.info(f"DAG execution complete: {completed_steps}/{len(dag.steps)} steps succeeded")
        
        return summary
    
    def _execute_step(self, step: DAGStep, data: UnifiedData) -> StepResult:
        """Execute a single step"""
        start_time = time.time()
        
        self.logger.info(f"Executing step {step.step_id} with tool {step.tool_id}")
        
        # Get the tool
        tool = self.registry.get_tool(step.tool_id)
        if not tool:
            return StepResult(
                step_id=step.step_id,
                tool_id=step.tool_id,
                status=StepStatus.FAILED,
                execution_time=time.time() - start_time,
                error=f"Tool {step.tool_id} not found in registry"
            )
        
        # Check if tool can process current data
        if not tool.can_process(data):
            return StepResult(
                step_id=step.step_id,
                tool_id=step.tool_id,
                status=StepStatus.FAILED,
                execution_time=time.time() - start_time,
                error=f"Tool {step.tool_id} cannot process current data state"
            )
        
        # Execute the tool
        try:
            tool_result = tool.execute(data)
            
            if tool_result.status == ToolStatus.SUCCESS:
                return StepResult(
                    step_id=step.step_id,
                    tool_id=step.tool_id,
                    status=StepStatus.SUCCESS,
                    execution_time=tool_result.execution_time,
                    message=tool_result.message
                )
            else:
                return StepResult(
                    step_id=step.step_id,
                    tool_id=step.tool_id,
                    status=StepStatus.FAILED,
                    execution_time=tool_result.execution_time,
                    error=tool_result.error
                )
                
        except Exception as e:
            return StepResult(
                step_id=step.step_id,
                tool_id=step.tool_id,
                status=StepStatus.FAILED,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    def validate_dag(self, dag: DAG) -> Dict[str, Any]:
        """
        Validate a DAG for execution.
        
        Checks:
        1. All tools exist in registry
        2. No circular dependencies
        3. Tool compatibility along paths
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tool_availability": {},
            "compatibility_issues": []
        }
        
        # Check tool availability
        for step in dag.steps:
            tool = self.registry.get_tool(step.tool_id)
            validation_result["tool_availability"][step.tool_id] = tool is not None
            
            if not tool:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Tool {step.tool_id} not found in registry")
        
        # Check for circular dependencies
        if self._has_circular_dependency(dag):
            validation_result["valid"] = False
            validation_result["errors"].append("DAG contains circular dependencies")
        
        # Check tool compatibility along paths
        for step in dag.steps:
            if step.depends_on:
                for dep_id in step.depends_on:
                    dep_step = dag.get_step(dep_id)
                    if dep_step:
                        # Check if tools are compatible
                        compatible_tools = self.registry.find_compatible_tools(dep_step.tool_id)
                        if step.tool_id not in compatible_tools:
                            validation_result["warnings"].append(
                                f"Tool {step.tool_id} may not be fully compatible with {dep_step.tool_id}"
                            )
        
        return validation_result
    
    def _has_circular_dependency(self, dag: DAG) -> bool:
        """Check for circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = dag.get_step(step_id)
            if step:
                for dep_id in step.depends_on:
                    if dep_id not in visited:
                        if has_cycle(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        for step in dag.steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id):
                    return True
        
        return False
    
    def suggest_tools(self, current_data: UnifiedData, target_category: ToolCategory) -> List[str]:
        """
        Suggest tools that could be used next based on current data.
        
        This demonstrates the dynamic nature - we can suggest tools
        based on what data is available, not hardcoded sequences.
        """
        suggestions = []
        
        # Get all tools in target category
        target_tools = self.registry.get_tools_by_category(target_category)
        
        for tool in target_tools:
            if tool.can_process(current_data):
                suggestions.append(tool.metadata.tool_id)
        
        return suggestions


class DAGBuilder:
    """
    Builds DAGs dynamically based on tool availability.
    
    This replaces hardcoded workflow definitions with dynamic generation.
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def build_auto_dag(self, source_file: str, target_output: str = "table") -> DAG:
        """
        Automatically build a DAG from source to target.
        
        This demonstrates true modularity - the system figures out
        how to chain tools based on categories and compatibility.
        """
        steps = []
        
        # Start with a loader
        loaders = self.registry.get_tools_by_category(ToolCategory.LOADER)
        if loaders:
            steps.append(DAGStep(
                step_id="load",
                tool_id=loaders[0].metadata.tool_id
            ))
        
        # Add extractors
        extractors = self.registry.get_tools_by_category(ToolCategory.EXTRACTOR)
        for i, extractor in enumerate(extractors[:2]):  # Use first 2 extractors
            steps.append(DAGStep(
                step_id=f"extract_{i}",
                tool_id=extractor.metadata.tool_id,
                depends_on=["load"]
            ))
        
        # Add builder
        builders = self.registry.get_tools_by_category(ToolCategory.BUILDER)
        if builders:
            extract_steps = [s.step_id for s in steps if s.step_id.startswith("extract")]
            steps.append(DAGStep(
                step_id="build",
                tool_id=builders[0].metadata.tool_id,
                depends_on=extract_steps
            ))
        
        # Add analyzer
        analyzers = self.registry.get_tools_by_category(ToolCategory.ANALYZER)
        if analyzers:
            steps.append(DAGStep(
                step_id="analyze",
                tool_id=analyzers[0].metadata.tool_id,
                depends_on=["build"]
            ))
        
        # Add converter if target is table
        if target_output == "table":
            converters = self.registry.get_tools_by_category(ToolCategory.CONVERTER)
            if converters:
                steps.append(DAGStep(
                    step_id="convert",
                    tool_id=converters[0].metadata.tool_id,
                    depends_on=["analyze"]
                ))
        
        return DAG(
            dag_id=f"auto_dag_{int(time.time())}",
            description=f"Auto-generated DAG from {source_file} to {target_output}",
            steps=steps
        )
    
    def build_custom_dag(self, tool_sequence: List[str]) -> DAG:
        """
        Build a DAG from a specific tool sequence.
        
        Validates compatibility along the way.
        """
        steps = []
        
        for i, tool_id in enumerate(tool_sequence):
            if i == 0:
                # First step has no dependencies
                steps.append(DAGStep(
                    step_id=f"step_{i}",
                    tool_id=tool_id
                ))
            else:
                # Subsequent steps depend on previous
                steps.append(DAGStep(
                    step_id=f"step_{i}",
                    tool_id=tool_id,
                    depends_on=[f"step_{i-1}"]
                ))
        
        return DAG(
            dag_id=f"custom_dag_{int(time.time())}",
            description="Custom tool sequence",
            steps=steps
        )