"""Workflow Engine - Multi-Layer Agent Interface Execution Engine

Executes YAML/JSON workflows with full provenance tracking and error handling.
Implements the execution layer for the multi-layer agent interface.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .workflow_schema import (
    WorkflowSchema, WorkflowStep, WorkflowStepType, AgentLayer,
    validate_workflow, workflow_from_yaml, workflow_from_json
)
from .tool_contract import get_tool_registry, ToolRequest, ToolResult
from .service_manager import get_service_manager


class ExecutionStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class StepExecution:
    """Track execution of a single workflow step."""
    step_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[ToolResult] = None
    error: Optional[str] = None
    retry_count: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class WorkflowExecution:
    """Track execution of an entire workflow."""
    workflow_id: str
    workflow: WorkflowSchema
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Execution tracking
    step_executions: Dict[str, StepExecution] = field(default_factory=dict)
    workflow_data: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    final_outputs: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    # Metrics
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0


class WorkflowEngine:
    """Executes workflows with full provenance tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tool_registry = get_tool_registry()
        self.service_manager = get_service_manager()
        
        # Active executions
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        # Execution callbacks
        self.step_callbacks: List[Callable] = []
        self.workflow_callbacks: List[Callable] = []
    
    def execute_workflow(
        self,
        workflow: Union[WorkflowSchema, str, dict],
        inputs: Dict[str, Any],
        workflow_id: Optional[str] = None,
        layer: AgentLayer = AgentLayer.LAYER_3
    ) -> WorkflowExecution:
        """Execute a workflow with the given inputs.
        
        Args:
            workflow: Workflow definition (schema, YAML string, or dict)
            inputs: Input data for the workflow
            workflow_id: Optional workflow ID (auto-generated if not provided)
            layer: Agent layer for execution oversight
            
        Returns:
            WorkflowExecution object with results
        """
        # Convert workflow to schema if needed
        if isinstance(workflow, str):
            if workflow.strip().startswith('{'):
                workflow_schema = workflow_from_json(workflow)
            else:
                workflow_schema = workflow_from_yaml(workflow)
        elif isinstance(workflow, dict):
            workflow_schema = WorkflowSchema(**workflow)
        else:
            workflow_schema = workflow
        
        # Validate workflow
        is_valid, errors = validate_workflow(workflow_schema)
        if not is_valid:
            raise ValueError(f"Invalid workflow: {'; '.join(errors)}")
        
        # Generate workflow ID if not provided
        if not workflow_id:
            workflow_id = f"wf_{int(time.time())}_{id(workflow_schema) % 10000}"
        
        # Create execution tracking
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow=workflow_schema,
            start_time=datetime.now(),
            total_steps=len(workflow_schema.steps),
            workflow_data=inputs.copy()
        )
        
        # Initialize step executions
        for step in workflow_schema.steps:
            execution.step_executions[step.step_id] = StepExecution(step_id=step.step_id)
        
        # Store active execution
        self.active_executions[workflow_id] = execution
        
        try:
            execution.status = ExecutionStatus.RUNNING
            execution.execution_log.append(f"Started workflow execution at {execution.start_time}")
            
            # Execute workflow based on layer
            if layer == AgentLayer.LAYER_1:
                self._execute_layer_1(execution)
            elif layer == AgentLayer.LAYER_2:
                self._execute_layer_2(execution)
            else:  # LAYER_3
                self._execute_layer_3(execution)
            
            # Finalize execution
            execution.end_time = datetime.now()
            execution.status = ExecutionStatus.COMPLETED
            execution.execution_log.append(f"Completed workflow execution at {execution.end_time}")
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            execution.execution_log.append(f"Failed workflow execution: {e}")
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
        
        return execution
    
    def _execute_layer_1(self, execution: WorkflowExecution):
        """Execute workflow with full agent automation."""
        # Layer 1: Agent generates and executes workflows automatically
        # For now, execute like Layer 3 but with agent oversight
        execution.execution_log.append("Layer 1: Agent-automated execution")
        self._execute_layer_3(execution)
    
    def _execute_layer_2(self, execution: WorkflowExecution):
        """Execute workflow with user review capability."""
        # Layer 2: Agent generates, user reviews/edits YAML, then executes
        # For now, execute like Layer 3 but mark as user-reviewed
        execution.execution_log.append("Layer 2: User-reviewed execution")
        self._execute_layer_3(execution)
    
    def _execute_layer_3(self, execution: WorkflowExecution):
        """Execute workflow directly from YAML/JSON."""
        execution.execution_log.append("Layer 3: Direct YAML execution")
        
        # Build execution order considering dependencies
        execution_order = self._build_execution_order(execution.workflow.steps)
        
        for step_id in execution_order:
            step = next(s for s in execution.workflow.steps if s.step_id == step_id)
            step_execution = execution.step_executions[step_id]
            
            try:
                self._execute_step(step, step_execution, execution)
                execution.completed_steps += 1
                
            except Exception as e:
                step_execution.status = ExecutionStatus.FAILED
                step_execution.error = str(e)
                execution.failed_steps += 1
                
                if not step.continue_on_error:
                    raise Exception(f"Step {step_id} failed: {e}")
                
                execution.execution_log.append(f"Step {step_id} failed but continuing: {e}")
    
    def _execute_step(self, step: WorkflowStep, step_execution: StepExecution, execution: WorkflowExecution):
        """Execute a single workflow step."""
        step_execution.status = ExecutionStatus.RUNNING
        step_execution.start_time = datetime.now()
        
        execution.execution_log.append(f"Executing step {step.step_id}: {step.name}")
        
        try:
            if step.step_type == WorkflowStepType.TOOL_EXECUTION:
                result = self._execute_tool_step(step, execution)
                step_execution.result = result
                
                # Map outputs to workflow data
                if step.output_mapping:
                    for output_key, workflow_key in step.output_mapping.items():
                        if hasattr(result, 'data') and isinstance(result.data, dict):
                            value = result.data.get(output_key)
                            if value is not None:
                                self._set_nested_value(execution.workflow_data, workflow_key, value)
                
            elif step.step_type == WorkflowStepType.CONDITIONAL:
                result = self._execute_conditional_step(step, execution)
                
            elif step.step_type == WorkflowStepType.PARALLEL:
                result = self._execute_parallel_step(step, execution)
                
            else:
                raise ValueError(f"Unsupported step type: {step.step_type}")
            
            step_execution.status = ExecutionStatus.COMPLETED
            step_execution.end_time = datetime.now()
            
        except Exception as e:
            step_execution.status = ExecutionStatus.FAILED
            step_execution.error = str(e)
            step_execution.end_time = datetime.now()
            raise
    
    def _execute_tool_step(self, step: WorkflowStep, execution: WorkflowExecution) -> ToolResult:
        """Execute a tool execution step."""
        # Get tool from registry
        tool = self.tool_registry.get_tool(step.tool_id)
        if not tool:
            raise ValueError(f"Tool {step.tool_id} not found in registry")
        
        # Prepare input data
        input_data = {}
        
        # Map workflow data to tool inputs
        if step.input_mapping:
            for tool_key, workflow_key in step.input_mapping.items():
                value = self._get_nested_value(execution.workflow_data, workflow_key)
                if value is not None:
                    input_data[tool_key] = value
        
        # Add tool parameters
        input_data.update(step.tool_parameters)
        
        # Create tool request
        request = ToolRequest(
            input_data=input_data,
            workflow_id=execution.workflow_id,
            options=step.tool_parameters
        )
        
        # Execute tool
        result = tool.execute(request)
        
        # Log execution
        execution.execution_log.append(
            f"Tool {step.tool_id} executed: status={result.status}, "
            f"confidence={result.confidence.value if result.confidence else 'N/A'}"
        )
        
        return result
    
    def _execute_conditional_step(self, step: WorkflowStep, execution: WorkflowExecution):
        """Execute a conditional step."""
        # Simple condition evaluation (could be enhanced)
        if step.condition:
            # For now, just log that condition was checked
            execution.execution_log.append(f"Checked condition: {step.condition}")
        return None
    
    def _execute_parallel_step(self, step: WorkflowStep, execution: WorkflowExecution):
        """Execute a parallel step."""
        # For now, just log that parallel execution was requested
        execution.execution_log.append(f"Parallel execution of: {step.parallel_steps}")
        return None
    
    def _build_execution_order(self, steps: List[WorkflowStep]) -> List[str]:
        """Build execution order considering dependencies."""
        # Topological sort
        in_degree = {step.step_id: 0 for step in steps}
        adj_list = {step.step_id: [] for step in steps}
        
        # Build dependency graph
        for step in steps:
            for dep in step.depends_on:
                adj_list[dep].append(step.step_id)
                in_degree[step.step_id] += 1
        
        # Kahn's algorithm for topological sort
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(steps):
            raise ValueError("Circular dependency detected in workflow")
        
        return result
    
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get nested value from dict using dot notation."""
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, data: Dict[str, Any], key_path: str, value: Any):
        """Set nested value in dict using dot notation."""
        keys = key_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get_execution_status(self, workflow_id: str) -> Optional[WorkflowExecution]:
        """Get status of a workflow execution."""
        return self.active_executions.get(workflow_id)
    
    def list_active_executions(self) -> List[str]:
        """List all active workflow execution IDs."""
        return list(self.active_executions.keys())
    
    def cancel_execution(self, workflow_id: str) -> bool:
        """Cancel a running workflow execution."""
        execution = self.active_executions.get(workflow_id)
        if execution and execution.status == ExecutionStatus.RUNNING:
            execution.status = ExecutionStatus.CANCELLED
            execution.end_time = datetime.now()
            execution.execution_log.append("Workflow execution cancelled")
            return True
        return False
    
    def add_step_callback(self, callback: Callable[[StepExecution], None]):
        """Add callback for step completion."""
        self.step_callbacks.append(callback)
    
    def add_workflow_callback(self, callback: Callable[[WorkflowExecution], None]):
        """Add callback for workflow completion."""
        self.workflow_callbacks.append(callback)


class WorkflowValidator:
    """Validates workflows for execution readiness."""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
    
    def validate_for_execution(self, workflow: WorkflowSchema) -> tuple[bool, List[str]]:
        """Validate that a workflow can be executed.
        
        Returns:
            Tuple of (is_executable, error_messages)
        """
        errors = []
        
        # Basic schema validation
        is_valid, schema_errors = validate_workflow(workflow)
        if not is_valid:
            errors.extend(schema_errors)
        
        # Tool availability validation
        required_tools = set()
        for step in workflow.steps:
            if step.step_type == WorkflowStepType.TOOL_EXECUTION and step.tool_id:
                required_tools.add(step.tool_id)
        
        available_tools = set(self.tool_registry.list_tools())
        missing_tools = required_tools - available_tools
        
        if missing_tools:
            errors.extend([f"Missing tool: {tool_id}" for tool_id in missing_tools])
        
        # Input/output validation
        for step in workflow.steps:
            # Check that input mappings reference valid workflow data
            for tool_key, workflow_key in step.input_mapping.items():
                # Could add more sophisticated validation here
                pass
        
        return len(errors) == 0, errors


# Utility functions

def create_simple_workflow(
    tool_sequence: List[str],
    name: str = "Generated Workflow",
    description: str = "Auto-generated workflow"
) -> WorkflowSchema:
    """Create a simple sequential workflow from a list of tools."""
    from .workflow_schema import WorkflowMetadata, WorkflowStep, WorkflowStepType
    
    steps = []
    for i, tool_id in enumerate(tool_sequence):
        step = WorkflowStep(
            step_id=f"step_{i+1}",
            step_type=WorkflowStepType.TOOL_EXECUTION,
            name=f"Execute {tool_id}",
            tool_id=tool_id,
            depends_on=[f"step_{i}"] if i > 0 else []
        )
        steps.append(step)
    
    return WorkflowSchema(
        metadata=WorkflowMetadata(name=name, description=description),
        steps=steps,
        entry_point="step_1" if steps else ""
    )


def execute_simple_workflow(tool_sequence: List[str], inputs: Dict[str, Any]) -> WorkflowExecution:
    """Execute a simple sequential workflow."""
    workflow = create_simple_workflow(tool_sequence)
    engine = WorkflowEngine()
    return engine.execute_workflow(workflow, inputs)