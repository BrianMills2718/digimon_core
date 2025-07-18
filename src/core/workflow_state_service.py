"""T121: Workflow State Service - Minimal Implementation

Provides workflow checkpointing and recovery capabilities.
Enables crash recovery and workflow resumption.
Implements Meta-Schema v9 event semantics.

This is a MINIMAL implementation focusing on:
- Basic checkpoint creation and storage
- Simple workflow state restoration  
- Progress tracking for long operations
- Error recovery support

Deferred features:
- State compression algorithms
- Automatic cleanup policies
- Advanced recovery strategies
- Performance optimization
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid
import json
import pickle
from pathlib import Path
import os


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


class WorkflowStateService:
    """T121: Workflow State Service - Checkpoint and recovery management."""
    
    def __init__(self, storage_dir: str = "./data/workflows"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.checkpoints: Dict[str, WorkflowCheckpoint] = {}
        self.workflows: Dict[str, WorkflowProgress] = {}
        self.checkpoint_files: Dict[str, Path] = {}  # checkpoint_id -> file_path
        
        # Load existing checkpoints on startup
        self._load_existing_checkpoints()
    
    def _load_existing_checkpoints(self):
        """Load existing checkpoints from storage directory."""
        try:
            checkpoint_pattern = "checkpoint_*.json"
            for checkpoint_file in self.storage_dir.glob(checkpoint_pattern):
                try:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                    
                    # Reconstruct checkpoint object
                    checkpoint_data['created_at'] = datetime.fromisoformat(
                        checkpoint_data['created_at']
                    )
                    checkpoint = WorkflowCheckpoint(**checkpoint_data)
                    
                    self.checkpoints[checkpoint.checkpoint_id] = checkpoint
                    self.checkpoint_files[checkpoint.checkpoint_id] = checkpoint_file
                    
                except Exception as e:
                    # Log error and continue with other checkpoints
                    logger.info(f"Warning: Failed to load checkpoint {checkpoint_file}: {e}")
                    
        except Exception as e:
            logger.info(f"Warning: Failed to load checkpoints directory: {e}")
    
    def start_workflow(
        self,
        name: str,
        total_steps: int,
        initial_state: Dict[str, Any] = None
    ) -> str:
        """Start a new workflow with tracking.
        
        Args:
            name: Human-readable workflow name
            total_steps: Expected total number of steps
            initial_state: Initial workflow state data
            
        Returns:
            Workflow ID for tracking
        """
        try:
            # Input validation
            if not name or total_steps <= 0:
                raise ValueError("Name and positive total_steps are required")
            
            if initial_state is None:
                initial_state = {}
            
            # Create workflow
            workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
            workflow = WorkflowProgress(
                workflow_id=workflow_id,
                name=name,
                started_at=datetime.now(),
                step_number=0,
                total_steps=total_steps
            )
            
            self.workflows[workflow_id] = workflow
            
            # Create initial checkpoint
            if initial_state:
                checkpoint_id = self.create_checkpoint(
                    workflow_id=workflow_id,
                    step_name="initialization",
                    step_number=0,
                    state_data=initial_state
                )
                workflow.last_checkpoint_id = checkpoint_id
            
            return workflow_id
            
        except Exception as e:
            raise RuntimeError(f"Failed to start workflow: {str(e)}")
    
    def create_checkpoint(
        self,
        workflow_id: str,
        step_name: str,
        step_number: int,
        state_data: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a workflow checkpoint.
        
        Args:
            workflow_id: ID of the workflow
            step_name: Name of the current step
            step_number: Number of the current step
            state_data: Current workflow state (must be JSON serializable)
            metadata: Additional checkpoint metadata
            
        Returns:
            Checkpoint ID
        """
        try:
            # Input validation
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if not step_name:
                raise ValueError("step_name is required")
            
            if step_number < 0:
                raise ValueError("step_number must be non-negative")
            
            # Validate state_data is JSON serializable
            try:
                json.dumps(state_data)
            except (TypeError, ValueError) as e:
                raise ValueError(f"state_data must be JSON serializable: {e}")
            
            if metadata is None:
                metadata = {}
            
            # Create checkpoint
            checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:8]}"
            workflow = self.workflows[workflow_id]
            
            checkpoint = WorkflowCheckpoint(
                checkpoint_id=checkpoint_id,
                workflow_id=workflow_id,
                step_name=step_name,
                step_number=step_number,
                total_steps=workflow.total_steps,
                state_data=state_data.copy(),
                metadata=metadata.copy()
            )
            
            # Store checkpoint in memory
            self.checkpoints[checkpoint_id] = checkpoint
            
            # Save checkpoint to file
            checkpoint_file = self.storage_dir / f"checkpoint_{checkpoint_id}.json"
            checkpoint_dict = asdict(checkpoint)
            checkpoint_dict['created_at'] = checkpoint.created_at.isoformat()
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_dict, f, indent=2)
            
            self.checkpoint_files[checkpoint_id] = checkpoint_file
            
            # Update workflow progress
            workflow.step_number = step_number
            workflow.last_checkpoint_id = checkpoint_id
            
            return checkpoint_id
            
        except Exception as e:
            raise RuntimeError(f"Failed to create checkpoint: {str(e)}")
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restore workflow state from a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore from
            
        Returns:
            Restored workflow state
        """
        try:
            if checkpoint_id not in self.checkpoints:
                return {
                    "status": "error",
                    "error": f"Checkpoint {checkpoint_id} not found"
                }
            
            checkpoint = self.checkpoints[checkpoint_id]
            
            # Update workflow status if workflow still exists
            if checkpoint.workflow_id in self.workflows:
                workflow = self.workflows[checkpoint.workflow_id]
                workflow.current_step = checkpoint.step_number
                workflow.status = "running"
                workflow.error_message = None
            
            return {
                "status": "success",
                "checkpoint_id": checkpoint_id,
                "workflow_id": checkpoint.workflow_id,
                "step_name": checkpoint.step_name,
                "step_number": checkpoint.step_number,
                "total_steps": checkpoint.total_steps,
                "state_data": checkpoint.state_data.copy(),
                "created_at": checkpoint.created_at.isoformat(),
                "metadata": checkpoint.metadata
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to restore checkpoint: {str(e)}"
            }
    
    def update_workflow_progress(
        self,
        workflow_id: str,
        step_number: int,
        status: str = "running",
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update workflow progress.
        
        Args:
            workflow_id: ID of workflow to update
            step_number: Current step number
            status: Workflow status (running, completed, failed, paused)
            error_message: Error message if failed
            
        Returns:
            Update result
        """
        try:
            if workflow_id not in self.workflows:
                return {
                    "status": "error",
                    "error": f"Workflow {workflow_id} not found"
                }
            
            workflow = self.workflows[workflow_id]
            workflow.step_number = step_number
            workflow.status = status
            workflow.error_message = error_message
            
            # Update completed/failed steps
            if status == "completed":
                workflow.completed_steps.add(step_number)
                workflow.failed_steps.discard(step_number)
            elif status == "failed":
                workflow.failed_steps.add(step_number)
                workflow.completed_steps.discard(step_number)
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "step_number": step_number,
                "workflow_status": status,
                "progress_percent": (len(workflow.completed_steps) / workflow.total_steps) * 100
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to update progress: {str(e)}"
            }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            Workflow status information
        """
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return None
            
            progress_percent = (len(workflow.completed_steps) / workflow.total_steps) * 100
            
            return {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status,
                "started_at": workflow.started_at.isoformat(),
                "step_number": workflow.step_number,
                "total_steps": workflow.total_steps,
                "completed_steps": len(workflow.completed_steps),
                "failed_steps": len(workflow.failed_steps),
                "progress_percent": progress_percent,
                "last_checkpoint_id": workflow.last_checkpoint_id,
                "error_message": workflow.error_message
            }
            
        except Exception:
            return None
    
    def get_workflow_checkpoints(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get all checkpoints for a workflow.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            List of checkpoint information
        """
        try:
            checkpoints = []
            for checkpoint in self.checkpoints.values():
                if checkpoint.workflow_id == workflow_id:
                    checkpoints.append({
                        "checkpoint_id": checkpoint.checkpoint_id,
                        "step_name": checkpoint.step_name,
                        "step_number": checkpoint.step_number,
                        "created_at": checkpoint.created_at.isoformat(),
                        "has_state_data": bool(checkpoint.state_data),
                        "metadata": checkpoint.metadata
                    })
            
            # Sort by step number
            checkpoints.sort(key=lambda x: x["step_number"])
            return checkpoints
            
        except Exception:
            return []
    
    def cleanup_old_checkpoints(self, days_old: int = 7) -> Dict[str, Any]:
        """Remove checkpoints older than specified days.
        
        Args:
            days_old: Number of days after which to remove checkpoints
            
        Returns:
            Cleanup result
        """
        try:
            cutoff_date = datetime.now() - datetime.timedelta(days=days_old)
            removed_count = 0
            
            # Find old checkpoints
            old_checkpoint_ids = []
            for checkpoint_id, checkpoint in self.checkpoints.items():
                if checkpoint.created_at < cutoff_date:
                    old_checkpoint_ids.append(checkpoint_id)
            
            # Remove checkpoints
            for checkpoint_id in old_checkpoint_ids:
                # Remove file
                if checkpoint_id in self.checkpoint_files:
                    file_path = self.checkpoint_files[checkpoint_id]
                    try:
                        file_path.unlink()
                    except Exception:
                        pass  # File might already be deleted
                    del self.checkpoint_files[checkpoint_id]
                
                # Remove from memory
                if checkpoint_id in self.checkpoints:
                    del self.checkpoints[checkpoint_id]
                
                removed_count += 1
            
            return {
                "status": "success",
                "removed_checkpoints": removed_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to cleanup: {str(e)}"
            }
    
    def create_workflow(self, workflow_id: str, total_steps: int) -> Dict[str, Any]:
        """Create new workflow tracking entry (API contract compliance method).
        
        Creates a workflow with the specified ID rather than generating one.
        
        Args:
            workflow_id: Workflow identifier
            total_steps: Total number of steps in workflow
            
        Returns:
            Creation result with status
        """
        try:
            # Input validation
            if not workflow_id or total_steps <= 0:
                return {
                    "status": "error",
                    "error": "Workflow ID and positive total_steps are required",
                    "workflow_id": workflow_id
                }
            
            # Check if workflow already exists
            if workflow_id in self.workflows:
                return {
                    "status": "error",
                    "error": f"Workflow {workflow_id} already exists",
                    "workflow_id": workflow_id
                }
            
            # Create workflow directly with specified ID
            workflow = WorkflowProgress(
                workflow_id=workflow_id,
                name=workflow_id,  # Use ID as name for API contract compliance
                started_at=datetime.now(),
                step_number=0,
                total_steps=total_steps
            )
            
            self.workflows[workflow_id] = workflow
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "total_steps": total_steps,
                "message": "Workflow created successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get workflow service statistics."""
        try:
            # Workflow status distribution
            status_counts = {}
            for workflow in self.workflows.values():
                status_counts[workflow.status] = status_counts.get(workflow.status, 0) + 1
            
            # Checkpoint statistics
            checkpoint_count_by_workflow = {}
            for checkpoint in self.checkpoints.values():
                wf_id = checkpoint.workflow_id
                checkpoint_count_by_workflow[wf_id] = checkpoint_count_by_workflow.get(wf_id, 0) + 1
            
            return {
                "status": "success",
                "total_workflows": len(self.workflows),
                "total_checkpoints": len(self.checkpoints),
                "workflow_status_distribution": status_counts,
                "average_checkpoints_per_workflow": (
                    len(self.checkpoints) / len(self.workflows) if self.workflows else 0
                ),
                "storage_directory": str(self.storage_dir),
                "checkpoint_files_on_disk": len(list(self.storage_dir.glob("checkpoint_*.json")))
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get statistics: {str(e)}"
            }