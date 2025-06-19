"""T121: Workflow State Service - Checkpoint/recovery for long operations."""

import json
import logging
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from uuid import uuid4

from ..models import WorkflowCheckpoint
from ..utils.database import DatabaseManager


logger = logging.getLogger(__name__)


@dataclass
class WorkflowState:
    """Active workflow state."""
    
    workflow_id: str
    workflow_type: str
    current_step: int
    total_steps: int
    start_time: datetime
    last_checkpoint: Optional[datetime] = None
    operation_count: int = 0
    checkpoint_interval: int = 100
    state_data: Dict[str, Any] = field(default_factory=dict)
    completed_operations: Set[str] = field(default_factory=set)
    failed_operations: Set[str] = field(default_factory=set)
    
    def should_checkpoint(self) -> bool:
        """Check if checkpoint is needed."""
        return self.operation_count >= self.checkpoint_interval


class WorkflowStateService:
    """
    T121: Workflow State Service
    
    Manages workflow state with checkpoint/recovery capabilities.
    Enables resumption of long-running operations after failures.
    """
    
    def __init__(self, db_manager: DatabaseManager, checkpoint_dir: Optional[Path] = None):
        self.db = db_manager
        self.checkpoint_dir = checkpoint_dir or Path("./data/checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._active_workflows: Dict[str, WorkflowState] = {}
    
    def start_workflow(
        self,
        workflow_type: str,
        total_steps: int,
        metadata: Optional[Dict[str, Any]] = None,
        checkpoint_interval: int = 100
    ) -> str:
        """Start a new workflow."""
        workflow_id = str(uuid4())
        
        state = WorkflowState(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            current_step=0,
            total_steps=total_steps,
            start_time=datetime.utcnow(),
            checkpoint_interval=checkpoint_interval,
            state_data={"metadata": metadata or {}}
        )
        
        self._active_workflows[workflow_id] = state
        
        # Create initial checkpoint
        self._create_checkpoint(state)
        
        logger.info(f"Started workflow: {workflow_id} ({workflow_type})")
        return workflow_id
    
    def update_progress(
        self,
        workflow_id: str,
        step_number: int,
        operation_id: Optional[str] = None,
        state_updates: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update workflow progress."""
        if workflow_id not in self._active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        state = self._active_workflows[workflow_id]
        state.current_step = step_number
        state.operation_count += 1
        
        if operation_id:
            state.completed_operations.add(operation_id)
        
        if state_updates:
            state.state_data.update(state_updates)
        
        # Check if checkpoint needed
        if state.should_checkpoint():
            self._create_checkpoint(state)
            state.operation_count = 0
        
        logger.debug(
            f"Updated workflow {workflow_id}: "
            f"step {step_number}/{state.total_steps}"
        )
    
    def record_failure(
        self,
        workflow_id: str,
        operation_id: str,
        error_message: str
    ) -> None:
        """Record a failed operation in the workflow."""
        if workflow_id not in self._active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        state = self._active_workflows[workflow_id]
        state.failed_operations.add(operation_id)
        
        # Add to warnings
        if "failures" not in state.state_data:
            state.state_data["failures"] = []
        
        state.state_data["failures"].append({
            "operation_id": operation_id,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Force checkpoint on failure
        self._create_checkpoint(state)
        
        logger.warning(f"Recorded failure in workflow {workflow_id}: {operation_id}")
    
    def complete_workflow(
        self,
        workflow_id: str,
        final_state: Optional[Dict[str, Any]] = None
    ) -> WorkflowCheckpoint:
        """Complete a workflow."""
        if workflow_id not in self._active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        state = self._active_workflows[workflow_id]
        state.current_step = state.total_steps
        
        if final_state:
            state.state_data.update(final_state)
        
        # Create final checkpoint
        checkpoint = self._create_checkpoint(state)
        
        # Clean up
        del self._active_workflows[workflow_id]
        
        logger.info(
            f"Completed workflow {workflow_id}: "
            f"{len(state.completed_operations)} operations completed, "
            f"{len(state.failed_operations)} failed"
        )
        
        return checkpoint
    
    def resume_workflow(
        self,
        workflow_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Resume a workflow from checkpoint."""
        # Find checkpoint
        if checkpoint_id:
            checkpoint = self.db.sqlite.get_checkpoint(checkpoint_id)
        else:
            # Get latest checkpoint for workflow
            checkpoint = self.db.sqlite.get_latest_checkpoint(workflow_id)
        
        if not checkpoint:
            raise ValueError(f"No checkpoint found for workflow: {workflow_id}")
        
        # Restore state
        state = WorkflowState(
            workflow_id=checkpoint.workflow_id,
            workflow_type=checkpoint.workflow_type,
            current_step=checkpoint.step_number,
            total_steps=checkpoint.total_steps,
            start_time=checkpoint.created_at,
            last_checkpoint=datetime.utcnow(),
            state_data=checkpoint.state_data,
            completed_operations=set(checkpoint.completed_operations),
            failed_operations=set(checkpoint.failed_operations)
        )
        
        self._active_workflows[workflow_id] = state
        
        # Load binary state if exists
        binary_path = self._get_binary_path(checkpoint.id)
        if binary_path.exists():
            with open(binary_path, "rb") as f:
                binary_state = pickle.load(f)
                state.state_data["binary_state"] = binary_state
        
        logger.info(
            f"Resumed workflow {workflow_id} from step "
            f"{checkpoint.step_number}/{checkpoint.total_steps}"
        )
        
        return {
            "workflow_id": workflow_id,
            "current_step": checkpoint.step_number,
            "total_steps": checkpoint.total_steps,
            "completed_operations": checkpoint.completed_operations,
            "failed_operations": checkpoint.failed_operations,
            "state_data": state.state_data
        }
    
    def list_checkpoints(
        self,
        workflow_id: Optional[str] = None,
        workflow_type: Optional[str] = None
    ) -> List[WorkflowCheckpoint]:
        """List available checkpoints."""
        return self.db.sqlite.list_checkpoints(
            workflow_id=workflow_id,
            workflow_type=workflow_type
        )
    
    def cleanup_checkpoints(
        self,
        workflow_id: str,
        keep_latest: int = 3
    ) -> int:
        """Clean up old checkpoints for a workflow."""
        checkpoints = self.db.sqlite.list_checkpoints(workflow_id=workflow_id)
        
        if len(checkpoints) <= keep_latest:
            return 0
        
        # Sort by creation time
        checkpoints.sort(key=lambda c: c.created_at, reverse=True)
        
        # Delete old checkpoints
        deleted = 0
        for checkpoint in checkpoints[keep_latest:]:
            # Delete database record
            self.db.sqlite.delete_checkpoint(checkpoint.id)
            
            # Delete binary file
            binary_path = self._get_binary_path(checkpoint.id)
            if binary_path.exists():
                binary_path.unlink()
            
            deleted += 1
        
        logger.info(f"Deleted {deleted} old checkpoints for workflow {workflow_id}")
        return deleted
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow."""
        if workflow_id in self._active_workflows:
            state = self._active_workflows[workflow_id]
            return {
                "status": "active",
                "workflow_id": workflow_id,
                "workflow_type": state.workflow_type,
                "current_step": state.current_step,
                "total_steps": state.total_steps,
                "progress_percent": (state.current_step / state.total_steps * 100),
                "completed_operations": len(state.completed_operations),
                "failed_operations": len(state.failed_operations),
                "start_time": state.start_time.isoformat(),
                "last_checkpoint": state.last_checkpoint.isoformat() if state.last_checkpoint else None
            }
        else:
            # Check for completed workflow
            checkpoint = self.db.sqlite.get_latest_checkpoint(workflow_id)
            if checkpoint:
                return {
                    "status": "completed" if checkpoint.step_number >= checkpoint.total_steps else "suspended",
                    "workflow_id": workflow_id,
                    "workflow_type": checkpoint.workflow_type,
                    "current_step": checkpoint.step_number,
                    "total_steps": checkpoint.total_steps,
                    "progress_percent": (checkpoint.step_number / checkpoint.total_steps * 100),
                    "completed_operations": len(checkpoint.completed_operations),
                    "failed_operations": len(checkpoint.failed_operations),
                    "last_checkpoint": checkpoint.created_at.isoformat()
                }
            else:
                return {
                    "status": "not_found",
                    "workflow_id": workflow_id
                }
    
    def _create_checkpoint(self, state: WorkflowState) -> WorkflowCheckpoint:
        """Create a checkpoint from current state."""
        checkpoint = WorkflowCheckpoint(
            workflow_id=state.workflow_id,
            workflow_type=state.workflow_type,
            step_number=state.current_step,
            total_steps=state.total_steps,
            state_data={k: v for k, v in state.state_data.items() if k != "binary_state"},
            completed_operations=list(state.completed_operations),
            pending_operations=[],  # Could be calculated from total - completed
            failed_operations=list(state.failed_operations),
            metadata={
                "duration_seconds": (datetime.utcnow() - state.start_time).total_seconds(),
                "operation_count": len(state.completed_operations)
            }
        )
        
        # Save to database
        self.db.sqlite.save_checkpoint(checkpoint)
        
        # Save binary state if present
        if "binary_state" in state.state_data:
            binary_path = self._get_binary_path(checkpoint.id)
            with open(binary_path, "wb") as f:
                pickle.dump(state.state_data["binary_state"], f)
        
        state.last_checkpoint = datetime.utcnow()
        
        logger.debug(f"Created checkpoint {checkpoint.id} for workflow {state.workflow_id}")
        return checkpoint
    
    def _get_binary_path(self, checkpoint_id: str) -> Path:
        """Get path for binary state file."""
        return self.checkpoint_dir / f"{checkpoint_id}.pkl"