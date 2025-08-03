"""
Storage Manager

Handles persistent storage of workflows, checkpoints, and templates.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .workflow_types import (
    WorkflowCheckpoint, WorkflowResult, TemplateInfo
)

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages persistent storage for workflow components."""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            from ..standard_config import get_file_path
            storage_dir = f"{get_file_path('data_dir')}/workflows"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage subdirectories
        self.checkpoints_dir = self.storage_dir / "checkpoints"
        self.templates_dir = self.storage_dir / "templates"
        self.workflows_dir = self.storage_dir / "workflows"
        
        # Create subdirectories
        self.checkpoints_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.workflows_dir.mkdir(exist_ok=True)
        
        self._storage_metrics = {
            "checkpoints_saved": 0,
            "checkpoints_loaded": 0,
            "templates_saved": 0,
            "templates_loaded": 0
        }
        
        logger.info(f"Storage manager initialized with directory: {self.storage_dir}")
    
    def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> WorkflowResult:
        """Save checkpoint to persistent storage.
        
        Args:
            checkpoint: WorkflowCheckpoint to save
            
        Returns:
            WorkflowResult with save status
        """
        try:
            # Create checkpoint file path
            checkpoint_file = self.checkpoints_dir / f"checkpoint_{checkpoint.checkpoint_id}.json"
            
            # Convert checkpoint to dictionary
            checkpoint_dict = checkpoint.to_dict()
            
            # Save to file
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_dict, f, indent=2)
            
            self._storage_metrics["checkpoints_saved"] += 1
            
            logger.debug(f"Saved checkpoint {checkpoint.checkpoint_id} to {checkpoint_file}")
            
            return WorkflowResult.success_result(
                message="Checkpoint saved successfully",
                data={"file_path": str(checkpoint_file)}
            )
            
        except Exception as e:
            error_msg = f"Failed to save checkpoint: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def load_checkpoint(self, checkpoint_id: str) -> WorkflowResult:
        """Load checkpoint from persistent storage.
        
        Args:
            checkpoint_id: ID of checkpoint to load
            
        Returns:
            WorkflowResult with checkpoint data
        """
        try:
            checkpoint_file = self.checkpoints_dir / f"checkpoint_{checkpoint_id}.json"
            
            if not checkpoint_file.exists():
                return WorkflowResult.error_result(f"Checkpoint file not found: {checkpoint_file}")
            
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Create checkpoint object
            checkpoint = WorkflowCheckpoint.from_dict(checkpoint_data)
            
            self._storage_metrics["checkpoints_loaded"] += 1
            
            logger.debug(f"Loaded checkpoint {checkpoint_id} from {checkpoint_file}")
            
            return WorkflowResult.success_result(
                message="Checkpoint loaded successfully",
                data=checkpoint
            )
            
        except Exception as e:
            error_msg = f"Failed to load checkpoint: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def delete_checkpoint(self, checkpoint_id: str) -> WorkflowResult:
        """Delete checkpoint from persistent storage.
        
        Args:
            checkpoint_id: ID of checkpoint to delete
            
        Returns:
            WorkflowResult with deletion status
        """
        try:
            checkpoint_file = self.checkpoints_dir / f"checkpoint_{checkpoint_id}.json"
            
            if not checkpoint_file.exists():
                return WorkflowResult.success_result(
                    message="Checkpoint file not found (already deleted?)"
                )
            
            checkpoint_file.unlink()
            
            logger.debug(f"Deleted checkpoint file {checkpoint_file}")
            
            return WorkflowResult.success_result(
                message="Checkpoint file deleted successfully"
            )
            
        except Exception as e:
            error_msg = f"Failed to delete checkpoint file: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def load_all_checkpoints(self) -> WorkflowResult:
        """Load all checkpoints from storage.
        
        Returns:
            WorkflowResult with list of checkpoints
        """
        try:
            checkpoints = []
            checkpoint_pattern = "checkpoint_*.json"
            
            for checkpoint_file in self.checkpoints_dir.glob(checkpoint_pattern):
                try:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                    
                    checkpoint = WorkflowCheckpoint.from_dict(checkpoint_data)
                    checkpoints.append(checkpoint)
                    
                except Exception as e:
                    # Log error and continue with other checkpoints
                    logger.warning(f"Failed to load checkpoint {checkpoint_file}: {e}")
            
            self._storage_metrics["checkpoints_loaded"] += len(checkpoints)
            
            logger.info(f"Loaded {len(checkpoints)} checkpoints from storage")
            
            return WorkflowResult.success_result(
                message=f"Loaded {len(checkpoints)} checkpoints",
                data=checkpoints
            )
            
        except Exception as e:
            error_msg = f"Failed to load checkpoints: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def save_template(self, template_data: Dict[str, Any]) -> WorkflowResult:
        """Save workflow template to persistent storage.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            WorkflowResult with save status
        """
        try:
            template_id = template_data.get("template_id")
            if not template_id:
                return WorkflowResult.error_result("Template ID is required")
            
            template_file = self.templates_dir / f"workflow_template_{template_id}.json"
            
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            self._storage_metrics["templates_saved"] += 1
            
            logger.debug(f"Saved template {template_id} to {template_file}")
            
            return WorkflowResult.success_result(
                message="Template saved successfully",
                data={"file_path": str(template_file)}
            )
            
        except Exception as e:
            error_msg = f"Failed to save template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def load_template(self, template_id: str) -> WorkflowResult:
        """Load workflow template from persistent storage.
        
        Args:
            template_id: ID of template to load
            
        Returns:
            WorkflowResult with template data
        """
        try:
            template_file = self.templates_dir / f"workflow_template_{template_id}.json"
            
            if not template_file.exists():
                return WorkflowResult.error_result(f"Template file not found: {template_file}")
            
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            self._storage_metrics["templates_loaded"] += 1
            
            logger.debug(f"Loaded template {template_id} from {template_file}")
            
            return WorkflowResult.success_result(
                message="Template loaded successfully",
                data=template_data
            )
            
        except Exception as e:
            error_msg = f"Failed to load template: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def delete_template(self, template_id: str) -> WorkflowResult:
        """Delete template from persistent storage.
        
        Args:
            template_id: ID of template to delete
            
        Returns:
            WorkflowResult with deletion status
        """
        try:
            template_file = self.templates_dir / f"workflow_template_{template_id}.json"
            
            if not template_file.exists():
                return WorkflowResult.error_result(f"Template file not found: {template_file}")
            
            template_file.unlink()
            
            logger.debug(f"Deleted template file {template_file}")
            
            return WorkflowResult.success_result(
                message="Template file deleted successfully"
            )
            
        except Exception as e:
            error_msg = f"Failed to delete template file: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def list_templates(self) -> WorkflowResult:
        """List all available workflow templates.
        
        Returns:
            WorkflowResult with list of template info
        """
        try:
            templates = []
            template_pattern = "workflow_template_*.json"
            
            for template_file in self.templates_dir.glob(template_pattern):
                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                    
                    template_info = TemplateInfo(
                        template_id=template_data["template_id"],
                        template_name=template_data["template_name"],
                        description=template_data["description"],
                        total_steps=template_data["workflow_structure"]["total_steps"],
                        created_at=datetime.fromisoformat(template_data["created_at"]),
                        original_workflow_id=template_data["original_workflow_id"],
                        step_sequence=template_data["workflow_structure"]["step_sequence"],
                        file_path=str(template_file)
                    )
                    
                    templates.append(template_info)
                    
                except Exception as e:
                    # Log error but continue with other templates
                    logger.warning(f"Failed to load template info from {template_file}: {e}")
            
            # Sort by creation date (newest first)
            templates.sort(key=lambda x: x.created_at, reverse=True)
            
            logger.debug(f"Found {len(templates)} templates in storage")
            
            return WorkflowResult.success_result(
                message=f"Found {len(templates)} templates",
                data=templates
            )
            
        except Exception as e:
            error_msg = f"Failed to list templates: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            # Count files in each directory
            checkpoint_files = len(list(self.checkpoints_dir.glob("checkpoint_*.json")))
            template_files = len(list(self.templates_dir.glob("workflow_template_*.json")))
            workflow_files = len(list(self.workflows_dir.glob("*.json")))
            
            # Calculate directory sizes (approximate)
            def get_dir_size(directory: Path) -> int:
                return sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            
            storage_size = get_dir_size(self.storage_dir)
            checkpoints_size = get_dir_size(self.checkpoints_dir)
            templates_size = get_dir_size(self.templates_dir)
            workflows_size = get_dir_size(self.workflows_dir)
            
            return {
                "storage_directory": str(self.storage_dir),
                "total_storage_size_bytes": storage_size,
                "checkpoint_files": checkpoint_files,
                "template_files": template_files,
                "workflow_files": workflow_files,
                "directory_sizes": {
                    "checkpoints": checkpoints_size,
                    "templates": templates_size,
                    "workflows": workflows_size
                },
                "storage_metrics": self._storage_metrics.copy()
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return {}
    
    def cleanup_storage(self, days_old: int = 30) -> WorkflowResult:
        """Clean up old files from storage.
        
        Args:
            days_old: Remove files older than this many days
            
        Returns:
            WorkflowResult with cleanup status
        """
        try:
            from datetime import timedelta
            
            if days_old <= 0:
                return WorkflowResult.error_result("Days old must be positive")
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_files = []
            
            # Clean up old checkpoint files
            for checkpoint_file in self.checkpoints_dir.glob("checkpoint_*.json"):
                try:
                    file_time = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        checkpoint_file.unlink()
                        removed_files.append(str(checkpoint_file))
                except Exception as e:
                    logger.warning(f"Failed to remove old checkpoint file {checkpoint_file}: {e}")
            
            # Clean up old template files
            for template_file in self.templates_dir.glob("workflow_template_*.json"):
                try:
                    file_time = datetime.fromtimestamp(template_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        template_file.unlink()
                        removed_files.append(str(template_file))
                except Exception as e:
                    logger.warning(f"Failed to remove old template file {template_file}: {e}")
            
            logger.info(f"Cleaned up {len(removed_files)} old files from storage")
            
            return WorkflowResult.success_result(
                message=f"Cleaned up {len(removed_files)} old files",
                data={
                    "removed_files": removed_files,
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_old": days_old
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to cleanup storage: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)
    
    def backup_storage(self, backup_dir: str) -> WorkflowResult:
        """Create backup of storage directory.
        
        Args:
            backup_dir: Directory to create backup in
            
        Returns:
            WorkflowResult with backup status
        """
        try:
            import shutil
            from datetime import datetime
            
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"workflow_storage_backup_{timestamp}"
            backup_full_path = backup_path / backup_name
            
            # Copy entire storage directory
            shutil.copytree(self.storage_dir, backup_full_path)
            
            logger.info(f"Created storage backup at {backup_full_path}")
            
            return WorkflowResult.success_result(
                message="Storage backup created successfully",
                data={
                    "backup_path": str(backup_full_path),
                    "timestamp": timestamp
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to create storage backup: {str(e)}"
            logger.error(error_msg)
            return WorkflowResult.error_result(error_msg)