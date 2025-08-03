"""
Workflow Types and Data Models

Core types, enums, and data structures for workflow management.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowCheckpoint:
    """A workflow state checkpoint."""
    checkpoint_id: str
    workflow_id: str
    step_name: str
    step_number: int
    total_steps: int
    state_data: Dict[str, Any]  # Serializable workflow state
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_id": self.workflow_id,
            "step_name": self.step_name,
            "step_number": self.step_number,
            "total_steps": self.total_steps,
            "state_data": self.state_data,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowCheckpoint':
        """Create checkpoint from dictionary."""
        data_copy = data.copy()
        data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        return cls(**data_copy)


@dataclass
class WorkflowProgress:
    """Workflow progress tracking."""
    workflow_id: str
    name: str
    started_at: datetime
    step_number: int  # Standardized parameter name (was current_step)
    total_steps: int
    completed_steps: Set[int] = field(default_factory=set)
    failed_steps: Set[int] = field(default_factory=set)
    status: str = "running"  # running, completed, failed, paused
    last_checkpoint_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_steps <= 0:
            return 0.0
        return (len(self.completed_steps) / self.total_steps) * 100
    
    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        return self.status == WorkflowStatus.COMPLETED.value
    
    def is_failed(self) -> bool:
        """Check if workflow is failed."""
        return self.status == WorkflowStatus.FAILED.value
    
    def is_running(self) -> bool:
        """Check if workflow is currently running."""
        return self.status == WorkflowStatus.RUNNING.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow progress to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "step_number": self.step_number,
            "total_steps": self.total_steps,
            "completed_steps": list(self.completed_steps),
            "failed_steps": list(self.failed_steps),
            "progress_percent": self.get_progress_percent(),
            "last_checkpoint_id": self.last_checkpoint_id,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class CheckpointMetadata:
    """Metadata for checkpoint operations."""
    checkpoint_id: str
    step_name: str
    step_number: int
    created_at: datetime
    has_state_data: bool
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "step_name": self.step_name,
            "step_number": self.step_number,
            "created_at": self.created_at.isoformat(),
            "has_state_data": self.has_state_data,
            "file_path": self.file_path,
            "metadata": self.metadata
        }


@dataclass
class TemplateInfo:
    """Information about a workflow template."""
    template_id: str
    template_name: str
    description: str
    total_steps: int
    created_at: datetime
    original_workflow_id: str
    step_sequence: List[str]
    include_data: bool = False
    file_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "template_id": self.template_id,
            "template_name": self.template_name,
            "description": self.description,
            "total_steps": self.total_steps,
            "created_at": self.created_at.isoformat(),
            "original_workflow_id": self.original_workflow_id,
            "step_sequence": self.step_sequence,
            "include_data": self.include_data,
            "file_path": self.file_path
        }


@dataclass
class WorkflowResult:
    """Result of workflow operation."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    workflow_id: Optional[str] = None
    
    @classmethod
    def success_result(cls, message: str, data: Any = None, workflow_id: Optional[str] = None) -> 'WorkflowResult':
        """Create success result."""
        return cls(success=True, message=message, data=data, workflow_id=workflow_id)
    
    @classmethod
    def error_result(cls, error: str, workflow_id: Optional[str] = None) -> 'WorkflowResult':
        """Create error result."""
        return cls(success=False, message="Operation failed", error=error, workflow_id=workflow_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "status": "success" if self.success else "error",
            "message": self.message
        }
        
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
        if self.workflow_id is not None:
            result["workflow_id"] = self.workflow_id
            
        return result


def generate_workflow_id() -> str:
    """Generate a unique workflow ID."""
    return f"workflow_{uuid.uuid4().hex[:8]}"


def generate_checkpoint_id() -> str:
    """Generate a unique checkpoint ID."""
    return f"checkpoint_{uuid.uuid4().hex[:8]}"


def generate_template_id() -> str:
    """Generate a unique template ID."""
    return f"template_{uuid.uuid4().hex[:8]}"


def validate_workflow_id(workflow_id: str) -> bool:
    """Validate workflow ID format."""
    if not workflow_id or not isinstance(workflow_id, str):
        return False
    return len(workflow_id.strip()) > 0


def validate_step_number(step_number: int, total_steps: int) -> bool:
    """Validate step number is within valid range."""
    return 0 <= step_number <= total_steps


def extract_state_schema(state_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract schema information from state data without including actual values."""
    schema = {}
    for key, value in state_data.items():
        if isinstance(value, dict):
            schema[key] = "dict"
        elif isinstance(value, list):
            schema[key] = "list"
        elif isinstance(value, str):
            schema[key] = "string"
        elif isinstance(value, (int, float)):
            schema[key] = "number"
        elif isinstance(value, bool):
            schema[key] = "boolean"
        else:
            schema[key] = "unknown"
    return schema