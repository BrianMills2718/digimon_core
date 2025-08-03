"""
Template Manager

Handles workflow template creation, management, and instantiation.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .workflow_types import (
    TemplateInfo, WorkflowResult, generate_template_id,
    extract_state_schema
)

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages workflow template creation, storage, and instantiation."""
    
    def __init__(self, storage_manager=None):
        self.storage_manager = storage_manager
        self.templates: Dict[str, Dict[str, Any]] = {}  # In-memory template cache
        self._template_metrics = {
            "total_created": 0,
            "total_loaded": 0,
            "total_instantiated": 0,
            "total_deleted": 0
        }
    
    def save_workflow_template(self, workflow_id: str, workflow_data: Dict[str, Any],
                              template_name: str, description: Optional[str] = None,
                              include_data: bool = False,
                              checkpoints_data: Optional[List[Dict[str, Any]]] = None) -> WorkflowResult:
        """Save a workflow as a reusable template.
        
        Args:
            workflow_id: ID of workflow to save as template
            workflow_data: Workflow information
            template_name: Name for the workflow template
            description: Optional description of the workflow template
            include_data: Whether to include actual data or just structure
            checkpoints_data: List of checkpoint data for the workflow
            
        Returns:
            WorkflowResult with template ID
        """
        try:
            if not template_name or not template_name.strip():
                return WorkflowResult.error_result("Template name is required")
            
            if not workflow_data:
                return WorkflowResult.error_result("Workflow data is required")
            
            if checkpoints_data is None:
                checkpoints_data = []
            
            # Create template
            template_id = generate_template_id()
            template_data = {
                "template_id": template_id,
                "template_name": template_name.strip(),
                "description": description or f"Template created from workflow {workflow_id}",
                "original_workflow_id": workflow_id,
                "workflow_structure": {
                    "name": workflow_data.get("name", workflow_id),
                    "total_steps": workflow_data.get("total_steps", 0),
                    "step_sequence": self._extract_step_sequence(checkpoints_data)
                },
                "checkpoints": [],
                "created_at": datetime.now().isoformat(),
                "include_data": include_data,
                "metadata": {
                    "original_started_at": workflow_data.get("started_at"),
                    "original_status": workflow_data.get("status"),
                    "completed_steps": workflow_data.get("completed_steps", 0),
                    "failed_steps": workflow_data.get("failed_steps", 0)
                }
            }
            
            # Process checkpoint data
            for checkpoint_info in checkpoints_data:
                template_checkpoint = {
                    "step_name": checkpoint_info.get("step_name", "unknown"),
                    "step_number": checkpoint_info.get("step_number", 0),
                    "metadata": checkpoint_info.get("metadata", {})
                }
                
                if include_data and "state_data" in checkpoint_info:
                    # Include actual state data for complete reproducibility
                    template_checkpoint["state_data"] = checkpoint_info["state_data"]
                else:
                    # Include only structure for workflow pattern reuse
                    state_data = checkpoint_info.get("state_data", {})
                    template_checkpoint["state_schema"] = extract_state_schema(state_data)
                
                template_data["checkpoints"].append(template_checkpoint)
            
            # Store in memory
            self.templates[template_id] = template_data
            
            # Save to persistent storage if available
            if self.storage_manager:
                save_result = self.storage_manager.save_template(template_data)
                if not save_result.success:
                    # Remove from memory if storage failed
                    del self.templates[template_id]
                    return WorkflowResult.error_result(f"Failed to save template: {save_result.error}")
            
            self._template_metrics["total_created"] += 1
            
            logger.info(f"Created workflow template '{template_name}' with ID {template_id}")
            
            return WorkflowResult.success_result(
                message=f"Workflow template '{template_name}' saved successfully",
                data={
                    "template_id": template_id,
                    "template_name": template_name,
                    "total_steps": template_data["workflow_structure"]["total_steps"],
                    "include_data": include_data
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to save workflow template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def load_workflow_template(self, template_id: str) -> WorkflowResult:
        """Load a workflow template.
        
        Args:
            template_id: ID of template to load
            
        Returns:
            WorkflowResult with template data
        """
        try:
            # Check in-memory cache first
            if template_id in self.templates:
                template_data = self.templates[template_id]
                return WorkflowResult.success_result(
                    message="Template loaded from cache",
                    data=template_data
                )
            
            # Load from storage if available
            if self.storage_manager:
                load_result = self.storage_manager.load_template(template_id)
                if load_result.success:
                    template_data = load_result.data
                    # Cache in memory
                    self.templates[template_id] = template_data
                    self._template_metrics["total_loaded"] += 1
                    
                    logger.debug(f"Loaded template {template_id} from storage")
                    
                    return WorkflowResult.success_result(
                        message="Template loaded successfully",
                        data=template_data
                    )
                else:
                    return WorkflowResult.error_result(f"Template {template_id} not found")
            
            return WorkflowResult.error_result(f"Template {template_id} not found")
            
        except Exception as e:
            error_msg = f"Failed to load workflow template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def create_workflow_from_template(self, template_id: str, new_workflow_name: str,
                                    initial_state: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Create workflow configuration from a template.
        
        Args:
            template_id: ID of template to use
            new_workflow_name: Name for the new workflow
            initial_state: Initial state data for the new workflow
            
        Returns:
            WorkflowResult with workflow configuration
        """
        try:
            # Load template
            template_result = self.load_workflow_template(template_id)
            if not template_result.success:
                return WorkflowResult.error_result(template_result.error)
            
            template_data = template_result.data
            workflow_structure = template_data["workflow_structure"]
            
            if not new_workflow_name or not new_workflow_name.strip():
                return WorkflowResult.error_result("New workflow name is required")
            
            # Create workflow configuration from template
            workflow_config = {
                "name": new_workflow_name.strip(),
                "total_steps": workflow_structure["total_steps"],
                "initial_state": initial_state or {},
                "template_metadata": {
                    "created_from_template": template_id,
                    "template_name": template_data["template_name"],
                    "step_sequence": workflow_structure["step_sequence"],
                    "template_description": template_data["description"]
                }
            }
            
            # Add template checkpoint structure if available
            if template_data.get("checkpoints"):
                workflow_config["checkpoint_structure"] = [
                    {
                        "step_name": cp["step_name"],
                        "step_number": cp["step_number"],
                        "metadata": cp.get("metadata", {}),
                        "state_schema": cp.get("state_schema", {}),
                        "has_template_data": "state_data" in cp
                    }
                    for cp in template_data["checkpoints"]
                ]
            
            self._template_metrics["total_instantiated"] += 1
            
            logger.info(f"Created workflow configuration from template {template_id} for '{new_workflow_name}'")
            
            return WorkflowResult.success_result(
                message=f"Workflow configuration created from template '{template_data['template_name']}'",
                data=workflow_config
            )
            
        except Exception as e:
            error_msg = f"Failed to create workflow from template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def list_workflow_templates(self) -> WorkflowResult:
        """List all available workflow templates.
        
        Returns:
            WorkflowResult with list of templates
        """
        try:
            # Get templates from storage if available
            if self.storage_manager:
                list_result = self.storage_manager.list_templates()
                if list_result.success:
                    templates_info = list_result.data
                    templates_dict = [info.to_dict() for info in templates_info]
                    
                    return WorkflowResult.success_result(
                        message=f"Found {len(templates_dict)} templates",
                        data={"templates": templates_dict, "total_templates": len(templates_dict)}
                    )
            
            # Fallback to in-memory templates
            templates = []
            for template_data in self.templates.values():
                templates.append({
                    "template_id": template_data["template_id"],
                    "template_name": template_data["template_name"],
                    "description": template_data["description"],
                    "total_steps": template_data["workflow_structure"]["total_steps"],
                    "created_at": template_data["created_at"],
                    "original_workflow_id": template_data["original_workflow_id"],
                    "step_sequence": template_data["workflow_structure"]["step_sequence"],
                    "include_data": template_data.get("include_data", False)
                })
            
            # Sort by creation date (newest first)
            templates.sort(key=lambda x: x["created_at"], reverse=True)
            
            return WorkflowResult.success_result(
                message=f"Found {len(templates)} templates",
                data={"templates": templates, "total_templates": len(templates)}
            )
            
        except Exception as e:
            error_msg = f"Failed to list templates: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def delete_workflow_template(self, template_id: str) -> WorkflowResult:
        """Delete a workflow template.
        
        Args:
            template_id: ID of template to delete
            
        Returns:
            WorkflowResult with deletion status
        """
        try:
            # Remove from storage if available
            if self.storage_manager:
                delete_result = self.storage_manager.delete_template(template_id)
                if not delete_result.success:
                    return WorkflowResult.error_result(f"Failed to delete template from storage: {delete_result.error}")
            
            # Remove from memory
            if template_id in self.templates:
                template_name = self.templates[template_id].get("template_name", template_id)
                del self.templates[template_id]
                self._template_metrics["total_deleted"] += 1
                
                logger.info(f"Deleted workflow template '{template_name}' ({template_id})")
                
                return WorkflowResult.success_result(
                    message=f"Template '{template_name}' deleted successfully",
                    data={"template_id": template_id}
                )
            else:
                return WorkflowResult.error_result(f"Template {template_id} not found in memory")
            
        except Exception as e:
            error_msg = f"Failed to delete template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific template.
        
        Args:
            template_id: ID of template
            
        Returns:
            Template information or None if not found
        """
        try:
            template_result = self.load_workflow_template(template_id)
            if not template_result.success:
                return None
            
            template_data = template_result.data
            
            return {
                "template_id": template_data["template_id"],
                "template_name": template_data["template_name"],
                "description": template_data["description"],
                "total_steps": template_data["workflow_structure"]["total_steps"],
                "created_at": template_data["created_at"],
                "original_workflow_id": template_data["original_workflow_id"],
                "step_sequence": template_data["workflow_structure"]["step_sequence"],
                "include_data": template_data.get("include_data", False),
                "checkpoint_count": len(template_data.get("checkpoints", [])),
                "metadata": template_data.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get template info for {template_id}: {e}")
            return None
    
    def duplicate_template(self, template_id: str, new_name: str, 
                          new_description: Optional[str] = None) -> WorkflowResult:
        """Create a duplicate of an existing template.
        
        Args:
            template_id: ID of template to duplicate
            new_name: Name for the new template
            new_description: Optional description for new template
            
        Returns:
            WorkflowResult with new template ID
        """
        try:
            # Load original template
            template_result = self.load_workflow_template(template_id)
            if not template_result.success:
                return WorkflowResult.error_result(f"Original template not found: {template_result.error}")
            
            original_template = template_result.data
            
            # Create new template data
            new_template_id = generate_template_id()
            new_template_data = original_template.copy()
            new_template_data.update({
                "template_id": new_template_id,
                "template_name": new_name.strip(),
                "description": new_description or f"Copy of {original_template['template_name']}",
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    **original_template.get("metadata", {}),
                    "duplicated_from": template_id,
                    "duplicated_at": datetime.now().isoformat()
                }
            })
            
            # Store new template
            self.templates[new_template_id] = new_template_data
            
            # Save to storage if available
            if self.storage_manager:
                save_result = self.storage_manager.save_template(new_template_data)
                if not save_result.success:
                    del self.templates[new_template_id]
                    return WorkflowResult.error_result(f"Failed to save duplicated template: {save_result.error}")
            
            self._template_metrics["total_created"] += 1
            
            logger.info(f"Duplicated template {template_id} as {new_template_id} ('{new_name}')")
            
            return WorkflowResult.success_result(
                message=f"Template duplicated successfully as '{new_name}'",
                data={
                    "new_template_id": new_template_id,
                    "template_name": new_name,
                    "original_template_id": template_id
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to duplicate template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get template management statistics.
        
        Returns:
            Dictionary with template statistics
        """
        try:
            # Analyze templates
            total_templates = len(self.templates)
            templates_with_data = len([
                t for t in self.templates.values() 
                if t.get("include_data", False)
            ])
            
            # Calculate average steps per template
            total_steps = sum(
                t["workflow_structure"]["total_steps"] 
                for t in self.templates.values()
            )
            avg_steps = total_steps / total_templates if total_templates > 0 else 0
            
            return {
                "total_templates": total_templates,
                "templates_with_data": templates_with_data,
                "templates_structure_only": total_templates - templates_with_data,
                "average_steps_per_template": avg_steps,
                "template_metrics": self._template_metrics.copy()
            }
            
        except Exception as e:
            logger.error(f"Failed to get template statistics: {e}")
            return {}
    
    def _extract_step_sequence(self, checkpoints_data: List[Dict[str, Any]]) -> List[str]:
        """Extract step sequence from checkpoint data.
        
        Args:
            checkpoints_data: List of checkpoint data
            
        Returns:
            List of step names in order
        """
        if not checkpoints_data:
            return []
        
        # Sort by step number and extract step names
        sorted_checkpoints = sorted(
            checkpoints_data, 
            key=lambda x: x.get("step_number", 0)
        )
        
        return [cp.get("step_name", f"step_{i}") for i, cp in enumerate(sorted_checkpoints)]