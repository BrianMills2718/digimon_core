"""T121: Workflow State Service - Streamlined Implementation

Provides workflow checkpointing and recovery capabilities using decomposed components.
Enables crash recovery and workflow resumption.
Implements Meta-Schema v9 event semantics.

This is a streamlined implementation focusing on:
- Basic checkpoint creation and storage
- Simple workflow state restoration  
- Progress tracking for long operations
- Error recovery support
- Template management for reproducibility
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .workflow_management import (
    WorkflowTracker,
    CheckpointManager,
    TemplateManager,
    StorageManager,
    WorkflowStatistics,
    WorkflowCheckpoint,
    WorkflowProgress,
    WorkflowResult
)

logger = logging.getLogger(__name__)


class WorkflowStateService:
    """T121: Workflow State Service - Checkpoint and recovery management using decomposed components."""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            from .standard_config import get_file_path
            storage_dir = f"{get_file_path('data_dir')}/workflows"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize component managers
        self.storage_manager = StorageManager(str(self.storage_dir))
        self.workflow_tracker = WorkflowTracker()
        self.checkpoint_manager = CheckpointManager(self.storage_manager)
        self.template_manager = TemplateManager(self.storage_manager)
        self.statistics = WorkflowStatistics(
            self.workflow_tracker,
            self.checkpoint_manager,
            self.template_manager,
            self.storage_manager
        )
        
        # Load existing data on startup
        self._initialize_from_storage()
        
        logger.info(f"Workflow State Service initialized with storage: {self.storage_dir}")
    
    def _initialize_from_storage(self):
        """Load existing checkpoints and templates from storage."""
        try:
            # Load checkpoints
            load_result = self.checkpoint_manager.load_checkpoints_from_storage()
            if load_result.success:
                logger.info(f"Loaded checkpoints: {load_result.message}")
            else:
                logger.warning(f"Failed to load checkpoints: {load_result.error}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize from storage: {e}")
    
    # Workflow Management Delegation
    def start_workflow(self, name: str, total_steps: int, 
                      initial_state: Dict[str, Any] = None) -> str:
        """Start a new workflow with tracking.
        
        Args:
            name: Human-readable workflow name
            total_steps: Expected total number of steps
            initial_state: Initial workflow state data
            
        Returns:
            Workflow ID for tracking
        """
        try:
            result = self.workflow_tracker.start_workflow(name, total_steps, initial_state)
            
            if result.success:
                self.statistics.record_operation(True)
                
                # Create initial checkpoint if initial state provided
                workflow_id = result.workflow_id
                if initial_state:
                    checkpoint_result = self.create_checkpoint(
                        workflow_id=workflow_id,
                        step_name="initialization",
                        step_number=0,
                        state_data=initial_state
                    )
                    
                    if checkpoint_result.success:
                        # Update workflow with checkpoint ID
                        workflow = self.workflow_tracker.workflows.get(workflow_id)
                        if workflow:
                            workflow.last_checkpoint_id = checkpoint_result.data.get("checkpoint_id")
                
                return workflow_id
            else:
                self.statistics.record_operation(False)
                raise RuntimeError(result.error)
                
        except Exception as e:
            self.statistics.record_operation(False)
            raise RuntimeError(f"Failed to start workflow: {str(e)}")
    
    def create_workflow(self, workflow_id: str, total_steps: int) -> Dict[str, Any]:
        """Create new workflow tracking entry (API contract compliance method).
        
        Args:
            workflow_id: Workflow identifier
            total_steps: Total number of steps in workflow
            
        Returns:
            Creation result with status
        """
        try:
            result = self.workflow_tracker.create_workflow(workflow_id, total_steps)
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    # Checkpoint Management Delegation
    def create_checkpoint(self, workflow_id: str, step_name: str, step_number: int,
                         state_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a workflow checkpoint.
        
        Args:
            workflow_id: ID of the workflow
            step_name: Name of the current step
            step_number: Number of the current step
            state_data: Current workflow state (must be JSON serializable)
            metadata: Additional checkpoint metadata
            
        Returns:
            Dictionary with checkpoint creation result
        """
        try:
            # Get workflow to determine total steps
            workflow = self.workflow_tracker.workflows.get(workflow_id)
            if not workflow:
                self.statistics.record_operation(False)
                return {
                    "status": "error",
                    "error": f"Workflow {workflow_id} not found"
                }
            
            result = self.checkpoint_manager.create_checkpoint(
                workflow_id, step_name, step_number, state_data, 
                workflow.total_steps, metadata
            )
            
            if result.success:
                # Update workflow progress
                workflow.step_number = step_number
                workflow.last_checkpoint_id = result.data.get("checkpoint_id")
                
                self.statistics.record_operation(True)
                return {
                    "status": "success",
                    "checkpoint_id": result.data.get("checkpoint_id"),
                    "message": result.message
                }
            else:
                self.statistics.record_operation(False)
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to create checkpoint: {str(e)}"
            }
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restore workflow state from a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore from
            
        Returns:
            Restored workflow state
        """
        try:
            result = self.checkpoint_manager.restore_from_checkpoint(checkpoint_id)
            
            if result.success:
                # Update workflow status if workflow still exists
                data = result.data
                workflow_id = data.get("workflow_id")
                
                if workflow_id and workflow_id in self.workflow_tracker.workflows:
                    workflow = self.workflow_tracker.workflows[workflow_id]
                    workflow.step_number = data.get("step_number", 0)
                    workflow.status = "running"
                    workflow.error_message = None
                
                self.statistics.record_operation(True)
                return {
                    "status": "success",
                    **data
                }
            else:
                self.statistics.record_operation(False)
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to restore checkpoint: {str(e)}"
            }
    
    # Workflow Progress Management
    def update_workflow_progress(self, workflow_id: str, step_number: int,
                               status: str = "running", 
                               error_message: Optional[str] = None) -> Dict[str, Any]:
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
            result = self.workflow_tracker.update_workflow_progress(
                workflow_id, step_number, status, error_message
            )
            
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
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
            status = self.workflow_tracker.get_workflow_status(workflow_id)
            if status:
                self.statistics.record_operation(True)
            return status
            
        except Exception as e:
            self.statistics.record_operation(False)
            logger.error(f"Failed to get workflow status: {e}")
            return None
    
    def get_workflow_checkpoints(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get all checkpoints for a workflow.
        
        Args:
            workflow_id: ID of workflow
            
        Returns:
            List of checkpoint information
        """
        try:
            checkpoints_metadata = self.checkpoint_manager.get_workflow_checkpoints(workflow_id)
            result = [metadata.to_dict() for metadata in checkpoints_metadata]
            
            self.statistics.record_operation(True)
            return result
            
        except Exception as e:
            self.statistics.record_operation(False)
            logger.error(f"Failed to get workflow checkpoints: {e}")
            return []
    
    # Template Management Delegation
    def save_workflow_template(self, workflow_id: str, template_name: str,
                              description: Optional[str] = None,
                              include_data: bool = False) -> Dict[str, Any]:
        """Save a workflow as a reusable template for reproducibility.
        
        Args:
            workflow_id: ID of completed workflow to save as template
            template_name: Name for the workflow template
            description: Optional description of the workflow template
            include_data: Whether to include actual data or just structure
            
        Returns:
            Template save result with template ID
        """
        try:
            # Get workflow data
            workflow_data = self.workflow_tracker.get_workflow_status(workflow_id)
            if not workflow_data:
                return {
                    "status": "error",
                    "error": f"Workflow {workflow_id} not found"
                }
            
            # Get checkpoint data
            checkpoints_metadata = self.checkpoint_manager.get_workflow_checkpoints(workflow_id)
            checkpoints_data = []
            
            for metadata in checkpoints_metadata:
                checkpoint = self.checkpoint_manager.get_checkpoint(metadata.checkpoint_id)
                if checkpoint:
                    checkpoints_data.append(checkpoint.to_dict())
            
            result = self.template_manager.save_workflow_template(
                workflow_id, workflow_data, template_name, description,
                include_data, checkpoints_data
            )
            
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to save workflow template: {str(e)}"
            }
    
    def load_workflow_template(self, template_id: str) -> Dict[str, Any]:
        """Load a workflow template for creating new workflows.
        
        Args:
            template_id: ID of template to load
            
        Returns:
            Template data for workflow creation
        """
        try:
            result = self.template_manager.load_workflow_template(template_id)
            self.statistics.record_operation(result.success)
            
            if result.success:
                return {
                    "status": "success",
                    "template_data": result.data,
                    "template_id": template_id,
                    "message": result.message
                }
            else:
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to load workflow template: {str(e)}"
            }
    
    def create_workflow_from_template(self, template_id: str, new_workflow_name: str,
                                    initial_state: Dict[str, Any] = None) -> str:
        """Create a new workflow based on a saved template.
        
        Args:
            template_id: ID of template to use
            new_workflow_name: Name for the new workflow
            initial_state: Initial state data for the new workflow
            
        Returns:
            New workflow ID
        """
        try:
            # Get workflow configuration from template
            config_result = self.template_manager.create_workflow_from_template(
                template_id, new_workflow_name, initial_state
            )
            
            if not config_result.success:
                self.statistics.record_operation(False)
                raise RuntimeError(config_result.error)
            
            workflow_config = config_result.data
            
            # Create new workflow with template structure
            workflow_id = self.start_workflow(
                name=workflow_config["name"],
                total_steps=workflow_config["total_steps"],
                initial_state=workflow_config["initial_state"]
            )
            
            # Add template metadata to workflow
            if workflow_id in self.workflow_tracker.workflows:
                workflow = self.workflow_tracker.workflows[workflow_id]
                workflow.metadata.update(workflow_config.get("template_metadata", {}))
            
            self.statistics.record_operation(True)
            return workflow_id
            
        except Exception as e:
            self.statistics.record_operation(False)
            raise RuntimeError(f"Failed to create workflow from template: {str(e)}")
    
    def list_workflow_templates(self) -> Dict[str, Any]:
        """List all available workflow templates.
        
        Returns:
            List of available templates with metadata
        """
        try:
            result = self.template_manager.list_workflow_templates()
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to list templates: {str(e)}"
            }
    
    def delete_workflow_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a workflow template.
        
        Args:
            template_id: ID of template to delete
            
        Returns:
            Deletion result
        """
        try:
            result = self.template_manager.delete_workflow_template(template_id)
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to delete template: {str(e)}"
            }
    
    # Maintenance and Cleanup Operations
    def cleanup_old_checkpoints(self, days_old: int = 7) -> Dict[str, Any]:
        """Remove checkpoints older than specified days.
        
        Args:
            days_old: Number of days after which to remove checkpoints
            
        Returns:
            Cleanup result
        """
        try:
            result = self.checkpoint_manager.cleanup_old_checkpoints(days_old)
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to cleanup: {str(e)}"
            }
    
    # Statistics and Monitoring
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get workflow service statistics."""
        try:
            result = self.statistics.get_service_statistics()
            self.statistics.record_operation(True)
            return result
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to get statistics: {str(e)}"
            }
    
    # Advanced Operations
    def get_workflow_health_summary(self) -> Dict[str, Any]:
        """Get overall workflow service health summary."""
        return self.statistics.get_health_summary()
    
    def get_workflow_status_distribution(self) -> Dict[str, Any]:
        """Get distribution of workflow statuses."""
        return self.statistics.get_workflow_status_distribution()
    
    def get_checkpoint_age_distribution(self) -> Dict[str, Any]:
        """Get distribution of checkpoint ages."""
        return self.statistics.get_checkpoint_age_distribution()
    
    def backup_workflow_data(self, backup_dir: str) -> Dict[str, Any]:
        """Create backup of all workflow data."""
        try:
            result = self.storage_manager.backup_storage(backup_dir)
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to create backup: {str(e)}"
            }
    
    def cleanup_storage(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old files from storage."""
        try:
            result = self.storage_manager.cleanup_storage(days_old)
            self.statistics.record_operation(result.success)
            return result.to_dict()
            
        except Exception as e:
            self.statistics.record_operation(False)
            return {
                "status": "error",
                "error": f"Failed to cleanup storage: {str(e)}"
            }
    
    # Legacy compatibility methods (for API contract compliance)
    def _extract_state_schema(self, state_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract schema information from state data without including actual values."""
        from .workflow_management.workflow_types import extract_state_schema
        return extract_state_schema(state_data)