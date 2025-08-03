"""
Checkpoint Manager

Handles workflow checkpoint creation, restoration, and management.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .workflow_types import (
    WorkflowCheckpoint, CheckpointMetadata, WorkflowResult,
    generate_checkpoint_id, validate_workflow_id
)

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages workflow checkpoint creation, storage, and restoration."""
    
    def __init__(self, storage_manager=None):
        self.storage_manager = storage_manager
        self.checkpoints: Dict[str, WorkflowCheckpoint] = {}
        self._checkpoint_metrics = {
            "total_created": 0,
            "total_restored": 0,
            "total_deleted": 0
        }
    
    def create_checkpoint(self, workflow_id: str, step_name: str, step_number: int,
                         state_data: Dict[str, Any], total_steps: int,
                         metadata: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Create a workflow checkpoint.
        
        Args:
            workflow_id: ID of the workflow
            step_name: Name of the current step
            step_number: Number of the current step
            state_data: Current workflow state (must be JSON serializable)
            total_steps: Total steps in the workflow
            metadata: Additional checkpoint metadata
            
        Returns:
            WorkflowResult with checkpoint ID
        """
        try:
            # Input validation
            if not validate_workflow_id(workflow_id):
                return WorkflowResult.error_result("Valid workflow ID is required")
            
            if not step_name or not step_name.strip():
                return WorkflowResult.error_result("Step name is required")
            
            if step_number < 0:
                return WorkflowResult.error_result("Step number must be non-negative")
            
            if total_steps <= 0:
                return WorkflowResult.error_result("Total steps must be positive")
            
            # Validate state_data is JSON serializable
            try:
                json.dumps(state_data)
            except (TypeError, ValueError) as e:
                return WorkflowResult.error_result(f"State data must be JSON serializable: {e}")
            
            if metadata is None:
                metadata = {}
            
            # Create checkpoint
            checkpoint_id = generate_checkpoint_id()
            checkpoint = WorkflowCheckpoint(
                checkpoint_id=checkpoint_id,
                workflow_id=workflow_id,
                step_name=step_name.strip(),
                step_number=step_number,
                total_steps=total_steps,
                state_data=state_data.copy(),
                metadata=metadata.copy()
            )
            
            # Store checkpoint in memory
            self.checkpoints[checkpoint_id] = checkpoint
            
            # Save checkpoint to storage if available
            if self.storage_manager:
                save_result = self.storage_manager.save_checkpoint(checkpoint)
                if not save_result.success:
                    # Remove from memory if storage failed
                    del self.checkpoints[checkpoint_id]
                    return WorkflowResult.error_result(f"Failed to save checkpoint: {save_result.error}")
            
            self._checkpoint_metrics["total_created"] += 1
            
            logger.info(f"Created checkpoint {checkpoint_id} for workflow {workflow_id}, step {step_number}")
            
            return WorkflowResult.success_result(
                message=f"Checkpoint created for step '{step_name}'",
                data={
                    "checkpoint_id": checkpoint_id,
                    "workflow_id": workflow_id,
                    "step_name": step_name,
                    "step_number": step_number
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to create checkpoint: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> WorkflowResult:
        """Restore workflow state from a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore from
            
        Returns:
            WorkflowResult with restored state
        """
        try:
            if checkpoint_id not in self.checkpoints:
                return WorkflowResult.error_result(f"Checkpoint {checkpoint_id} not found")
            
            checkpoint = self.checkpoints[checkpoint_id]
            self._checkpoint_metrics["total_restored"] += 1
            
            logger.info(f"Restored checkpoint {checkpoint_id} for workflow {checkpoint.workflow_id}")
            
            return WorkflowResult.success_result(
                message=f"Restored from checkpoint '{checkpoint.step_name}'",
                data={
                    "checkpoint_id": checkpoint_id,
                    "workflow_id": checkpoint.workflow_id,
                    "step_name": checkpoint.step_name,
                    "step_number": checkpoint.step_number,
                    "total_steps": checkpoint.total_steps,
                    "state_data": checkpoint.state_data.copy(),
                    "created_at": checkpoint.created_at.isoformat(),
                    "metadata": checkpoint.metadata
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to restore checkpoint: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Get a specific checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to retrieve
            
        Returns:
            WorkflowCheckpoint or None if not found
        """
        return self.checkpoints.get(checkpoint_id)
    
    def get_workflow_checkpoints(self, workflow_id: str) -> List[CheckpointMetadata]:
        """Get all checkpoints for a workflow.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            List of checkpoint metadata
        """
        try:
            checkpoints = []
            for checkpoint in self.checkpoints.values():
                if checkpoint.workflow_id == workflow_id:
                    metadata = CheckpointMetadata(
                        checkpoint_id=checkpoint.checkpoint_id,
                        step_name=checkpoint.step_name,
                        step_number=checkpoint.step_number,
                        created_at=checkpoint.created_at,
                        has_state_data=bool(checkpoint.state_data),
                        metadata=checkpoint.metadata
                    )
                    checkpoints.append(metadata)
            
            # Sort by step number
            checkpoints.sort(key=lambda x: x.step_number)
            return checkpoints
            
        except Exception as e:
            logger.error(f"Failed to get workflow checkpoints for {workflow_id}: {e}")
            return []
    
    def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Get the latest checkpoint for a workflow.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            Latest WorkflowCheckpoint or None if not found
        """
        try:
            workflow_checkpoints = [
                cp for cp in self.checkpoints.values() 
                if cp.workflow_id == workflow_id
            ]
            
            if not workflow_checkpoints:
                return None
            
            # Return checkpoint with highest step number
            return max(workflow_checkpoints, key=lambda x: x.step_number)
            
        except Exception as e:
            logger.error(f"Failed to get latest checkpoint for {workflow_id}: {e}")
            return None
    
    def delete_checkpoint(self, checkpoint_id: str) -> WorkflowResult:
        """Delete a specific checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to delete
            
        Returns:
            WorkflowResult with deletion status
        """
        try:
            if checkpoint_id not in self.checkpoints:
                return WorkflowResult.error_result(f"Checkpoint {checkpoint_id} not found")
            
            checkpoint = self.checkpoints[checkpoint_id]
            
            # Remove from storage if available
            if self.storage_manager:
                delete_result = self.storage_manager.delete_checkpoint(checkpoint_id)
                if not delete_result.success:
                    logger.warning(f"Failed to delete checkpoint from storage: {delete_result.error}")
            
            # Remove from memory
            del self.checkpoints[checkpoint_id]
            self._checkpoint_metrics["total_deleted"] += 1
            
            logger.info(f"Deleted checkpoint {checkpoint_id} for workflow {checkpoint.workflow_id}")
            
            return WorkflowResult.success_result(
                message="Checkpoint deleted successfully",
                data={"checkpoint_id": checkpoint_id}
            )
            
        except Exception as e:
            error_msg = f"Failed to delete checkpoint: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def delete_workflow_checkpoints(self, workflow_id: str) -> WorkflowResult:
        """Delete all checkpoints for a workflow.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            WorkflowResult with deletion status
        """
        try:
            # Find all checkpoints for the workflow
            checkpoint_ids = [
                cp.checkpoint_id for cp in self.checkpoints.values() 
                if cp.workflow_id == workflow_id
            ]
            
            if not checkpoint_ids:
                return WorkflowResult.success_result(
                    message="No checkpoints found for workflow",
                    data={"deleted_count": 0}
                )
            
            deleted_count = 0
            for checkpoint_id in checkpoint_ids:
                result = self.delete_checkpoint(checkpoint_id)
                if result.success:
                    deleted_count += 1
                else:
                    logger.warning(f"Failed to delete checkpoint {checkpoint_id}: {result.error}")
            
            logger.info(f"Deleted {deleted_count} checkpoints for workflow {workflow_id}")
            
            return WorkflowResult.success_result(
                message=f"Deleted {deleted_count} checkpoints",
                data={"deleted_count": deleted_count, "total_found": len(checkpoint_ids)}
            )
            
        except Exception as e:
            error_msg = f"Failed to delete workflow checkpoints: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def cleanup_old_checkpoints(self, days_old: int = 7) -> WorkflowResult:
        """Remove checkpoints older than specified days.
        
        Args:
            days_old: Number of days after which to remove checkpoints
            
        Returns:
            WorkflowResult with cleanup status
        """
        try:
            if days_old <= 0:
                return WorkflowResult.error_result("Days old must be positive")
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Find old checkpoints
            old_checkpoint_ids = [
                checkpoint_id for checkpoint_id, checkpoint in self.checkpoints.items()
                if checkpoint.created_at < cutoff_date
            ]
            
            if not old_checkpoint_ids:
                return WorkflowResult.success_result(
                    message="No old checkpoints found to clean up",
                    data={"removed_count": 0, "cutoff_date": cutoff_date.isoformat()}
                )
            
            # Remove old checkpoints
            removed_count = 0
            for checkpoint_id in old_checkpoint_ids:
                result = self.delete_checkpoint(checkpoint_id)
                if result.success:
                    removed_count += 1
                else:
                    logger.warning(f"Failed to delete old checkpoint {checkpoint_id}: {result.error}")
            
            logger.info(f"Cleaned up {removed_count} old checkpoints (older than {days_old} days)")
            
            return WorkflowResult.success_result(
                message=f"Cleaned up {removed_count} old checkpoints",
                data={
                    "removed_count": removed_count,
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_old": days_old
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to cleanup old checkpoints: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def get_checkpoint_statistics(self) -> Dict[str, Any]:
        """Get checkpoint management statistics.
        
        Returns:
            Dictionary with checkpoint statistics
        """
        try:
            # Group checkpoints by workflow
            checkpoints_by_workflow = {}
            for checkpoint in self.checkpoints.values():
                wf_id = checkpoint.workflow_id
                if wf_id not in checkpoints_by_workflow:
                    checkpoints_by_workflow[wf_id] = []
                checkpoints_by_workflow[wf_id].append(checkpoint)
            
            # Calculate statistics
            avg_checkpoints_per_workflow = (
                len(self.checkpoints) / len(checkpoints_by_workflow)
                if checkpoints_by_workflow else 0
            )
            
            # Find checkpoint age distribution
            now = datetime.now()
            recent_count = 0  # Last 24 hours
            old_count = 0     # Older than 7 days
            
            for checkpoint in self.checkpoints.values():
                age = now - checkpoint.created_at
                if age.days == 0:
                    recent_count += 1
                elif age.days > 7:
                    old_count += 1
            
            return {
                "total_checkpoints": len(self.checkpoints),
                "workflows_with_checkpoints": len(checkpoints_by_workflow),
                "average_checkpoints_per_workflow": avg_checkpoints_per_workflow,
                "recent_checkpoints_24h": recent_count,
                "old_checkpoints_7d": old_count,
                "checkpoint_metrics": self._checkpoint_metrics.copy()
            }
            
        except Exception as e:
            logger.error(f"Failed to get checkpoint statistics: {e}")
            return {}
    
    def load_checkpoints_from_storage(self) -> WorkflowResult:
        """Load existing checkpoints from storage.
        
        Returns:
            WorkflowResult with loading status
        """
        try:
            if not self.storage_manager:
                return WorkflowResult.error_result("No storage manager configured")
            
            load_result = self.storage_manager.load_all_checkpoints()
            if not load_result.success:
                return WorkflowResult.error_result(f"Failed to load checkpoints: {load_result.error}")
            
            loaded_checkpoints = load_result.data or []
            loaded_count = 0
            
            for checkpoint in loaded_checkpoints:
                if isinstance(checkpoint, WorkflowCheckpoint):
                    self.checkpoints[checkpoint.checkpoint_id] = checkpoint
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} checkpoints from storage")
            
            return WorkflowResult.success_result(
                message=f"Loaded {loaded_count} checkpoints from storage",
                data={"loaded_count": loaded_count}
            )
            
        except Exception as e:
            error_msg = f"Failed to load checkpoints from storage: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)