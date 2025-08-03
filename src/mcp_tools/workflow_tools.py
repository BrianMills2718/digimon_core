"""
Workflow Service MCP Tools

T121: Workflow State Service tools for workflow management and checkpointing.
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from .server_config import get_mcp_config

logger = logging.getLogger(__name__)


class WorkflowServiceTools:
    """Collection of Workflow Service tools for MCP server"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_mcp_config()
    
    @property
    def workflow_service(self):
        """Get workflow service instance"""
        return self.config.workflow_service
    
    def register_tools(self, mcp: FastMCP):
        """Register all workflow service tools with MCP server"""
        
        @mcp.tool()
        def start_workflow(
            workflow_type: str,
            parameters: Dict[str, Any] = None,
            metadata: Dict[str, Any] = None
        ) -> str:
            """Start a new workflow.
            
            Args:
                workflow_type: Type of workflow to start
                parameters: Workflow parameters
                metadata: Additional metadata
            """
            try:
                if not self.workflow_service:
                    return "error_service_unavailable"
                
                return self.workflow_service.start_workflow(
                    workflow_type=workflow_type,
                    parameters=parameters or {},
                    metadata=metadata or {}
                )
            except Exception as e:
                self.logger.error(f"Error starting workflow: {e}")
                return f"error_{str(e)}"
        
        @mcp.tool()
        def create_checkpoint(
            workflow_id: str,
            checkpoint_name: str,
            state_data: Dict[str, Any],
            metadata: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Create a workflow checkpoint.
            
            Args:
                workflow_id: ID of the workflow
                checkpoint_name: Name for the checkpoint
                state_data: Current workflow state data
                metadata: Additional metadata
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.create_checkpoint(
                    workflow_id=workflow_id,
                    checkpoint_name=checkpoint_name,
                    state_data=state_data,
                    metadata=metadata or {}
                )
            except Exception as e:
                self.logger.error(f"Error creating checkpoint: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def restore_from_checkpoint(checkpoint_id: str) -> Dict[str, Any]:
            """Restore workflow from a checkpoint.
            
            Args:
                checkpoint_id: ID of the checkpoint to restore from
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.restore_from_checkpoint(checkpoint_id)
            except Exception as e:
                self.logger.error(f"Error restoring from checkpoint: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def update_workflow_progress(
            workflow_id: str,
            current_step: str,
            progress_percentage: float,
            step_data: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Update workflow progress.
            
            Args:
                workflow_id: ID of the workflow
                current_step: Current step name
                progress_percentage: Progress as percentage (0-100)
                step_data: Data for the current step
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.update_workflow_progress(
                    workflow_id=workflow_id,
                    current_step=current_step,
                    progress_percentage=progress_percentage,
                    step_data=step_data or {}
                )
            except Exception as e:
                self.logger.error(f"Error updating workflow progress: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_workflow_status(workflow_id: str) -> Optional[Dict[str, Any]]:
            """Get current workflow status.
            
            Args:
                workflow_id: ID of the workflow
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.get_workflow_status(workflow_id)
            except Exception as e:
                self.logger.error(f"Error getting workflow status: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_workflow_checkpoints(workflow_id: str) -> List[Dict[str, Any]]:
            """Get all checkpoints for a workflow.
            
            Args:
                workflow_id: ID of the workflow
            """
            try:
                if not self.workflow_service:
                    return [{"error": "Workflow service not available"}]
                
                return self.workflow_service.get_workflow_checkpoints(workflow_id)
            except Exception as e:
                self.logger.error(f"Error getting workflow checkpoints: {e}")
                return [{"error": str(e)}]
        
        @mcp.tool()
        def get_workflow_statistics() -> Dict[str, Any]:
            """Get workflow service statistics."""
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting workflow statistics: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def save_workflow_template(
            template_name: str,
            workflow_definition: Dict[str, Any],
            description: str = "",
            metadata: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Save a workflow template.
            
            Args:
                template_name: Name for the template
                workflow_definition: Workflow definition structure
                description: Template description
                metadata: Additional metadata
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.save_workflow_template(
                    template_name=template_name,
                    workflow_definition=workflow_definition,
                    description=description,
                    metadata=metadata or {}
                )
            except Exception as e:
                self.logger.error(f"Error saving workflow template: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def load_workflow_template(template_id: str) -> Dict[str, Any]:
            """Load a workflow template.
            
            Args:
                template_id: ID of the template to load
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.load_workflow_template(template_id)
            except Exception as e:
                self.logger.error(f"Error loading workflow template: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def create_workflow_from_template(
            template_id: str,
            parameters: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Create a new workflow from a template.
            
            Args:
                template_id: ID of the template to use
                parameters: Parameters to override template defaults
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.create_workflow_from_template(
                    template_id=template_id,
                    parameters=parameters or {}
                )
            except Exception as e:
                self.logger.error(f"Error creating workflow from template: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def list_workflow_templates() -> Dict[str, Any]:
            """List all available workflow templates."""
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.list_workflow_templates()
            except Exception as e:
                self.logger.error(f"Error listing workflow templates: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def delete_workflow_template(template_id: str) -> Dict[str, Any]:
            """Delete a workflow template.
            
            Args:
                template_id: ID of the template to delete
            """
            try:
                if not self.workflow_service:
                    return {"error": "Workflow service not available"}
                
                return self.workflow_service.delete_workflow_template(template_id)
            except Exception as e:
                self.logger.error(f"Error deleting workflow template: {e}")
                return {"error": str(e)}
        
        self.logger.info("Workflow service tools registered successfully")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about workflow service tools"""
        return {
            "service": "T121_Workflow_State_Service",
            "tool_count": 12,
            "tools": [
                "start_workflow",
                "create_checkpoint",
                "restore_from_checkpoint",
                "update_workflow_progress",
                "get_workflow_status",
                "get_workflow_checkpoints",
                "get_workflow_statistics",
                "save_workflow_template",
                "load_workflow_template",
                "create_workflow_from_template",
                "list_workflow_templates",
                "delete_workflow_template"
            ],
            "description": "Workflow state management and checkpointing tools",
            "capabilities": [
                "workflow_lifecycle_management",
                "checkpoint_creation_restoration",
                "progress_tracking",
                "template_management",
                "state_persistence"
            ],
            "service_available": self.workflow_service is not None
        }