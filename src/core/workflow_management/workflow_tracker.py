"""
Workflow Tracker

Handles workflow creation, progress tracking, and status management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .workflow_types import (
    WorkflowProgress, WorkflowStatus, WorkflowResult,
    generate_workflow_id, validate_workflow_id, validate_step_number
)

logger = logging.getLogger(__name__)


class WorkflowTracker:
    """Manages workflow creation, progress tracking, and status updates."""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowProgress] = {}
        self._workflow_metrics = {
            "total_created": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_cancelled": 0
        }
    
    def start_workflow(self, name: str, total_steps: int, 
                      initial_state: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Start a new workflow with tracking.
        
        Args:
            name: Human-readable workflow name
            total_steps: Expected total number of steps
            initial_state: Initial workflow state data
            
        Returns:
            WorkflowResult with workflow ID
        """
        try:
            # Input validation
            if not name or not name.strip():
                return WorkflowResult.error_result("Workflow name is required")
            
            if total_steps <= 0:
                return WorkflowResult.error_result("Total steps must be positive")
            
            if initial_state is None:
                initial_state = {}
            
            # Create workflow
            workflow_id = generate_workflow_id()
            workflow = WorkflowProgress(
                workflow_id=workflow_id,
                name=name.strip(),
                started_at=datetime.now(),
                step_number=0,
                total_steps=total_steps
            )
            
            # Store initial state in metadata if provided
            if initial_state:
                workflow.metadata["initial_state"] = initial_state
            
            self.workflows[workflow_id] = workflow
            self._workflow_metrics["total_created"] += 1
            
            logger.info(f"Started workflow '{name}' with ID {workflow_id}, {total_steps} steps")
            
            return WorkflowResult.success_result(
                message=f"Workflow '{name}' started successfully",
                data={"workflow_id": workflow_id, "total_steps": total_steps},
                workflow_id=workflow_id
            )
            
        except Exception as e:
            error_msg = f"Failed to start workflow: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def create_workflow(self, workflow_id: str, total_steps: int, 
                       name: Optional[str] = None) -> WorkflowResult:
        """Create new workflow tracking entry with specified ID.
        
        Args:
            workflow_id: Workflow identifier
            total_steps: Total number of steps in workflow
            name: Optional workflow name (defaults to workflow_id)
            
        Returns:
            WorkflowResult with creation status
        """
        try:
            # Input validation
            if not validate_workflow_id(workflow_id):
                return WorkflowResult.error_result(
                    "Valid workflow ID is required", workflow_id
                )
            
            if total_steps <= 0:
                return WorkflowResult.error_result(
                    "Total steps must be positive", workflow_id
                )
            
            # Check if workflow already exists
            if workflow_id in self.workflows:
                return WorkflowResult.error_result(
                    f"Workflow {workflow_id} already exists", workflow_id
                )
            
            # Create workflow directly with specified ID
            workflow = WorkflowProgress(
                workflow_id=workflow_id,
                name=name or workflow_id,  # Use provided name or default to ID
                started_at=datetime.now(),
                step_number=0,
                total_steps=total_steps
            )
            
            self.workflows[workflow_id] = workflow
            self._workflow_metrics["total_created"] += 1
            
            logger.info(f"Created workflow {workflow_id} with {total_steps} steps")
            
            return WorkflowResult.success_result(
                message="Workflow created successfully",
                data={"workflow_id": workflow_id, "total_steps": total_steps},
                workflow_id=workflow_id
            )
            
        except Exception as e:
            error_msg = f"Failed to create workflow: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg, workflow_id)
    
    def update_workflow_progress(self, workflow_id: str, step_number: int,
                               status: str = "running", 
                               error_message: Optional[str] = None) -> WorkflowResult:
        """Update workflow progress.
        
        Args:
            workflow_id: ID of workflow to update
            step_number: Current step number
            status: Workflow status (running, completed, failed, paused)
            error_message: Error message if failed
            
        Returns:
            WorkflowResult with update status
        """
        try:
            if workflow_id not in self.workflows:
                return WorkflowResult.error_result(
                    f"Workflow {workflow_id} not found", workflow_id
                )
            
            workflow = self.workflows[workflow_id]
            
            # Validate step number
            if not validate_step_number(step_number, workflow.total_steps):
                return WorkflowResult.error_result(
                    f"Invalid step number {step_number} (max: {workflow.total_steps})",
                    workflow_id
                )
            
            # Validate status
            valid_statuses = [s.value for s in WorkflowStatus]
            if status not in valid_statuses:
                return WorkflowResult.error_result(
                    f"Invalid status '{status}'. Valid: {valid_statuses}",
                    workflow_id
                )
            
            # Update workflow
            old_status = workflow.status
            workflow.step_number = step_number
            workflow.status = status
            workflow.error_message = error_message
            
            # Update completed/failed steps
            if status == WorkflowStatus.COMPLETED.value:
                workflow.completed_steps.add(step_number)
                workflow.failed_steps.discard(step_number)
                if old_status != WorkflowStatus.COMPLETED.value:
                    self._workflow_metrics["total_completed"] += 1
            elif status == WorkflowStatus.FAILED.value:
                workflow.failed_steps.add(step_number)
                workflow.completed_steps.discard(step_number)
                if old_status != WorkflowStatus.FAILED.value:
                    self._workflow_metrics["total_failed"] += 1
            
            progress_percent = workflow.get_progress_percent()
            
            logger.debug(f"Updated workflow {workflow_id}: step {step_number}, status {status}")
            
            return WorkflowResult.success_result(
                message=f"Workflow progress updated to step {step_number}",
                data={
                    "workflow_id": workflow_id,
                    "step_number": step_number,
                    "workflow_status": status,
                    "progress_percent": progress_percent
                },
                workflow_id=workflow_id
            )
            
        except Exception as e:
            error_msg = f"Failed to update workflow progress: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg, workflow_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            Workflow status information or None if not found
        """
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return None
            
            return workflow.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to get workflow status for {workflow_id}: {e}")
            return None
    
    def list_workflows(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all workflows, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of workflow information
        """
        try:
            workflows = []
            for workflow in self.workflows.values():
                if status_filter is None or workflow.status == status_filter:
                    workflows.append(workflow.to_dict())
            
            # Sort by started date (newest first)
            workflows.sort(key=lambda x: x["started_at"], reverse=True)
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    def complete_workflow(self, workflow_id: str) -> WorkflowResult:
        """Mark workflow as completed.
        
        Args:
            workflow_id: ID of workflow to complete
            
        Returns:
            WorkflowResult with completion status
        """
        return self.update_workflow_progress(
            workflow_id, 
            self.workflows[workflow_id].total_steps if workflow_id in self.workflows else 0,
            WorkflowStatus.COMPLETED.value
        )
    
    def fail_workflow(self, workflow_id: str, error_message: str) -> WorkflowResult:
        """Mark workflow as failed.
        
        Args:
            workflow_id: ID of workflow to fail
            error_message: Reason for failure
            
        Returns:
            WorkflowResult with failure status
        """
        return self.update_workflow_progress(
            workflow_id,
            self.workflows[workflow_id].step_number if workflow_id in self.workflows else 0,
            WorkflowStatus.FAILED.value,
            error_message
        )
    
    def pause_workflow(self, workflow_id: str) -> WorkflowResult:
        """Pause a running workflow.
        
        Args:
            workflow_id: ID of workflow to pause
            
        Returns:
            WorkflowResult with pause status
        """
        return self.update_workflow_progress(
            workflow_id,
            self.workflows[workflow_id].step_number if workflow_id in self.workflows else 0,
            WorkflowStatus.PAUSED.value
        )
    
    def resume_workflow(self, workflow_id: str) -> WorkflowResult:
        """Resume a paused workflow.
        
        Args:
            workflow_id: ID of workflow to resume
            
        Returns:
            WorkflowResult with resume status
        """
        return self.update_workflow_progress(
            workflow_id,
            self.workflows[workflow_id].step_number if workflow_id in self.workflows else 0,
            WorkflowStatus.RUNNING.value
        )
    
    def cancel_workflow(self, workflow_id: str, reason: str = "Cancelled by user") -> WorkflowResult:
        """Cancel a workflow.
        
        Args:
            workflow_id: ID of workflow to cancel
            reason: Reason for cancellation
            
        Returns:
            WorkflowResult with cancellation status
        """
        try:
            if workflow_id not in self.workflows:
                return WorkflowResult.error_result(
                    f"Workflow {workflow_id} not found", workflow_id
                )
            
            workflow = self.workflows[workflow_id]
            old_status = workflow.status
            
            workflow.status = WorkflowStatus.CANCELLED.value
            workflow.error_message = reason
            
            if old_status != WorkflowStatus.CANCELLED.value:
                self._workflow_metrics["total_cancelled"] += 1
            
            logger.info(f"Cancelled workflow {workflow_id}: {reason}")
            
            return WorkflowResult.success_result(
                message=f"Workflow cancelled: {reason}",
                workflow_id=workflow_id
            )
            
        except Exception as e:
            error_msg = f"Failed to cancel workflow: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg, workflow_id)
    
    def remove_workflow(self, workflow_id: str) -> WorkflowResult:
        """Remove a workflow from tracking.
        
        Args:
            workflow_id: ID of workflow to remove
            
        Returns:
            WorkflowResult with removal status
        """
        try:
            if workflow_id not in self.workflows:
                return WorkflowResult.error_result(
                    f"Workflow {workflow_id} not found", workflow_id
                )
            
            workflow = self.workflows[workflow_id]
            del self.workflows[workflow_id]
            
            logger.info(f"Removed workflow {workflow_id} from tracking")
            
            return WorkflowResult.success_result(
                message="Workflow removed from tracking",
                workflow_id=workflow_id
            )
            
        except Exception as e:
            error_msg = f"Failed to remove workflow: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg, workflow_id)
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow tracking metrics.
        
        Returns:
            Dictionary with workflow metrics
        """
        try:
            active_workflows = len([w for w in self.workflows.values() if w.is_running()])
            completed_workflows = len([w for w in self.workflows.values() if w.is_completed()])
            failed_workflows = len([w for w in self.workflows.values() if w.is_failed()])
            
            return {
                "total_workflows": len(self.workflows),
                "active_workflows": active_workflows,
                "completed_workflows": completed_workflows,
                "failed_workflows": failed_workflows,
                "workflow_metrics": self._workflow_metrics.copy(),
                "success_rate": (
                    completed_workflows / len(self.workflows) * 100
                    if self.workflows else 0.0
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow metrics: {e}")
            return {}
    
    def cleanup_completed_workflows(self, keep_recent: int = 10) -> WorkflowResult:
        """Clean up old completed workflows, keeping only recent ones.
        
        Args:
            keep_recent: Number of recent completed workflows to keep
            
        Returns:
            WorkflowResult with cleanup status
        """
        try:
            completed_workflows = [
                (wf_id, wf) for wf_id, wf in self.workflows.items() 
                if wf.is_completed()
            ]
            
            if len(completed_workflows) <= keep_recent:
                return WorkflowResult.success_result(
                    message=f"No cleanup needed, {len(completed_workflows)} completed workflows"
                )
            
            # Sort by start time and keep only recent ones
            completed_workflows.sort(key=lambda x: x[1].started_at, reverse=True)
            workflows_to_remove = completed_workflows[keep_recent:]
            
            removed_count = 0
            for workflow_id, _ in workflows_to_remove:
                del self.workflows[workflow_id]
                removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} completed workflows")
            
            return WorkflowResult.success_result(
                message=f"Cleaned up {removed_count} completed workflows",
                data={"removed_count": removed_count, "kept_count": keep_recent}
            )
            
        except Exception as e:
            error_msg = f"Failed to cleanup workflows: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)