"""Workflow Schema Definition - Multi-Layer Agent Interface

Defines YAML/JSON workflow schemas for agent-driven workflow generation
and execution according to CLAUDE.md Task 2 requirements.
"""

from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
import yaml


class WorkflowStepType(str, Enum):
    """Types of workflow steps."""
    TOOL_EXECUTION = "tool_execution"
    DATA_TRANSFORMATION = "data_transformation"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    PARALLEL = "parallel"
    HUMAN_REVIEW = "human_review"


class WorkflowStep(BaseModel):
    """Individual step in a workflow."""
    
    step_id: str = Field(description="Unique identifier for this step")
    step_type: WorkflowStepType = Field(description="Type of workflow step")
    name: str = Field(description="Human-readable name for the step")
    description: Optional[str] = Field(default="", description="Detailed description of what this step does")
    
    # Tool execution parameters
    tool_id: Optional[str] = Field(default=None, description="Tool to execute (for tool_execution steps)")
    tool_parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters to pass to the tool")
    
    # Flow control
    depends_on: List[str] = Field(default_factory=list, description="Step IDs this step depends on")
    condition: Optional[str] = Field(default=None, description="Condition for conditional steps")
    parallel_steps: List[str] = Field(default_factory=list, description="Steps to run in parallel")
    
    # Data handling
    input_mapping: Dict[str, str] = Field(default_factory=dict, description="Map workflow data to tool inputs")
    output_mapping: Dict[str, str] = Field(default_factory=dict, description="Map tool outputs to workflow data")
    
    # Execution options
    retry_count: int = Field(default=0, description="Number of retries on failure")
    timeout_seconds: Optional[int] = Field(default=None, description="Step timeout in seconds")
    continue_on_error: bool = Field(default=False, description="Continue workflow if this step fails")
    
    @validator('step_id')
    def step_id_must_be_valid(cls, v):
        if not v or not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('step_id must be alphanumeric with underscores/hyphens')
        return v


class WorkflowMetadata(BaseModel):
    """Metadata for a workflow."""
    
    name: str = Field(description="Workflow name")
    description: str = Field(description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    author: Optional[str] = Field(default=None, description="Workflow author")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    tags: List[str] = Field(default_factory=list, description="Workflow tags")
    
    # Workflow characteristics
    estimated_duration: Optional[str] = Field(default=None, description="Estimated execution time")
    required_tools: List[str] = Field(default_factory=list, description="Required tool IDs")
    input_requirements: Dict[str, str] = Field(default_factory=dict, description="Required input data")
    output_description: Dict[str, str] = Field(default_factory=dict, description="Expected outputs")


class WorkflowConfiguration(BaseModel):
    """Configuration options for workflow execution."""
    
    execution_mode: Literal["sequential", "parallel", "hybrid"] = Field(
        default="sequential", description="Workflow execution mode"
    )
    error_handling: Literal["stop", "continue", "retry"] = Field(
        default="stop", description="How to handle step failures"
    )
    max_retries: int = Field(default=3, description="Maximum retries for failed steps")
    timeout_seconds: int = Field(default=3600, description="Overall workflow timeout")
    
    # Agent configuration
    agent_oversight: bool = Field(default=True, description="Enable agent oversight of execution")
    human_approval_required: bool = Field(default=False, description="Require human approval for execution")
    auto_optimize: bool = Field(default=True, description="Allow agent to optimize workflow")
    
    # Logging and monitoring
    detailed_logging: bool = Field(default=True, description="Enable detailed execution logging")
    checkpoint_frequency: int = Field(default=5, description="Create checkpoint every N steps")


class WorkflowSchema(BaseModel):
    """Complete workflow definition schema."""
    
    metadata: WorkflowMetadata = Field(description="Workflow metadata")
    configuration: WorkflowConfiguration = Field(default_factory=WorkflowConfiguration)
    
    # Workflow definition
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow input schema")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow output schema")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Workflow variables")
    
    steps: List[WorkflowStep] = Field(description="Workflow steps in execution order")
    
    # Flow control
    entry_point: str = Field(description="ID of the first step to execute")
    exit_conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditions for workflow completion")
    
    @validator('steps')
    def steps_must_have_unique_ids(cls, v):
        step_ids = [step.step_id for step in v]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError('All step IDs must be unique')
        return v
    
    @validator('entry_point')
    def entry_point_must_exist(cls, v, values):
        if 'steps' in values:
            step_ids = [step.step_id for step in values['steps']]
            if v not in step_ids:
                raise ValueError(f'entry_point {v} must be a valid step_id')
        return v


class AgentLayer(str, Enum):
    """Agent interface layers as specified in CLAUDE.md."""
    LAYER_1 = "layer_1"  # Agent generates and executes workflows automatically
    LAYER_2 = "layer_2"  # Agent generates, user reviews/edits YAML, then executes
    LAYER_3 = "layer_3"  # User writes YAML directly, engine executes


class AgentRequest(BaseModel):
    """Request for agent workflow generation."""
    
    natural_language_description: str = Field(description="Natural language description of desired workflow")
    layer: AgentLayer = Field(description="Which agent layer to use")
    
    # Context
    available_documents: List[str] = Field(default_factory=list, description="Available document paths")
    target_outputs: List[str] = Field(default_factory=list, description="Desired output types")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Execution constraints")
    
    # Preferences
    preferred_tools: List[str] = Field(default_factory=list, description="Preferred tools to use")
    execution_time_limit: Optional[int] = Field(default=None, description="Maximum execution time in seconds")
    quality_requirements: Dict[str, float] = Field(default_factory=dict, description="Quality thresholds")


class AgentResponse(BaseModel):
    """Response from agent workflow generation."""
    
    status: Literal["success", "error", "requires_review"] = Field(description="Response status")
    
    # Generated workflow
    generated_workflow: Optional[WorkflowSchema] = Field(default=None, description="Generated workflow")
    workflow_yaml: Optional[str] = Field(default=None, description="YAML representation of workflow")
    
    # Agent reasoning
    reasoning: str = Field(description="Agent's reasoning for workflow design")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made by agent")
    alternatives: List[str] = Field(default_factory=list, description="Alternative approaches considered")
    
    # Execution readiness
    ready_to_execute: bool = Field(description="Whether workflow is ready for execution")
    missing_requirements: List[str] = Field(default_factory=list, description="Missing requirements for execution")
    
    # Error handling
    error_message: Optional[str] = Field(default=None, description="Error message if generation failed")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for user")


# Utility functions for workflow manipulation

def workflow_to_yaml(workflow: WorkflowSchema) -> str:
    """Convert workflow schema to YAML string."""
    # Convert to dict with proper enum serialization
    data = workflow.dict()
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def workflow_from_yaml(yaml_content: str) -> WorkflowSchema:
    """Create workflow schema from YAML string."""
    data = yaml.safe_load(yaml_content)
    return WorkflowSchema(**data)


def workflow_to_json(workflow: WorkflowSchema) -> str:
    """Convert workflow schema to JSON string."""
    return workflow.json(indent=2)


def workflow_from_json(json_content: str) -> WorkflowSchema:
    """Create workflow schema from JSON string."""
    data = json.loads(json_content)
    return WorkflowSchema(**data)


def validate_workflow(workflow_data: Union[dict, str, WorkflowSchema]) -> tuple[bool, List[str]]:
    """Validate a workflow definition.
    
    Args:
        workflow_data: Workflow as dict, YAML/JSON string, or WorkflowSchema
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        # Convert to WorkflowSchema if needed
        if isinstance(workflow_data, str):
            if workflow_data.strip().startswith('{'):
                workflow = workflow_from_json(workflow_data)
            else:
                workflow = workflow_from_yaml(workflow_data)
        elif isinstance(workflow_data, dict):
            workflow = WorkflowSchema(**workflow_data)
        elif isinstance(workflow_data, WorkflowSchema):
            workflow = workflow_data
        else:
            return False, ["Invalid workflow data type"]
        
        # Additional validation
        step_ids = [step.step_id for step in workflow.steps]
        
        # Validate dependencies
        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step {step.step_id} depends on non-existent step {dep}")
        
        # Validate tool references
        for step in workflow.steps:
            if step.step_type == WorkflowStepType.TOOL_EXECUTION and not step.tool_id:
                errors.append(f"Tool execution step {step.step_id} missing tool_id")
        
        # Check for circular dependencies
        if _has_circular_dependencies(workflow.steps):
            errors.append("Workflow contains circular dependencies")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]


def _has_circular_dependencies(steps: List[WorkflowStep]) -> bool:
    """Check if workflow steps have circular dependencies."""
    # Build dependency graph
    deps = {step.step_id: set(step.depends_on) for step in steps}
    
    # Use DFS to detect cycles
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        if node in rec_stack:
            return True
        if node in visited:
            return False
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in deps.get(node, []):
            if has_cycle(neighbor):
                return True
        
        rec_stack.remove(node)
        return False
    
    for step_id in deps:
        if has_cycle(step_id):
            return True
    
    return False


# Predefined workflow templates

WORKFLOW_TEMPLATES = {
    "pdf_analysis": {
        "metadata": {
            "name": "PDF Document Analysis",
            "description": "Analyze PDF documents and extract entities and relationships",
            "version": "1.0.0",
            "required_tools": ["T01_PDF_LOADER", "T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        },
        "steps": [
            {
                "step_id": "load_pdf",
                "step_type": "tool_execution",
                "name": "Load PDF Document",
                "tool_id": "T01_PDF_LOADER",
                "input_mapping": {"file_path": "input.document_path"},
                "output_mapping": {"document": "document_data"}
            },
            {
                "step_id": "extract_entities",
                "step_type": "tool_execution", 
                "name": "Extract Named Entities",
                "tool_id": "T23A_SPACY_NER",
                "depends_on": ["load_pdf"],
                "input_mapping": {"text_content": "document_data.text"},
                "output_mapping": {"entities": "extracted_entities"}
            },
            {
                "step_id": "extract_relationships",
                "step_type": "tool_execution",
                "name": "Extract Relationships",
                "tool_id": "T27_RELATIONSHIP_EXTRACTOR", 
                "depends_on": ["extract_entities"],
                "input_mapping": {
                    "text_content": "document_data.text",
                    "entities": "extracted_entities"
                },
                "output_mapping": {"relationships": "extracted_relationships"}
            }
        ],
        "entry_point": "load_pdf"
    },
    
    "multi_document_fusion": {
        "metadata": {
            "name": "Multi-Document Entity Fusion",
            "description": "Process multiple documents and fuse entities across documents",
            "version": "1.0.0",
            "required_tools": ["T01_PDF_LOADER", "T23C_ONTOLOGY_AWARE_EXTRACTOR", "T301_MULTI_DOCUMENT_FUSION"]
        },
        "steps": [
            {
                "step_id": "process_documents",
                "step_type": "parallel",
                "name": "Process Multiple Documents",
                "parallel_steps": ["load_doc1", "load_doc2", "load_doc3"]
            },
            {
                "step_id": "fuse_entities",
                "step_type": "tool_execution",
                "name": "Fuse Entities Across Documents", 
                "tool_id": "T301_MULTI_DOCUMENT_FUSION",
                "depends_on": ["process_documents"]
            }
        ],
        "entry_point": "process_documents"
    }
}


def get_workflow_template(template_name: str) -> Optional[WorkflowSchema]:
    """Get a predefined workflow template."""
    template_data = WORKFLOW_TEMPLATES.get(template_name)
    if template_data:
        return WorkflowSchema(**template_data)
    return None


def list_workflow_templates() -> List[str]:
    """List available workflow template names."""
    return list(WORKFLOW_TEMPLATES.keys())