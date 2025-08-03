"""
Workflow Statistics

Handles workflow service statistics, monitoring, and reporting.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WorkflowStatistics:
    """Manages workflow service statistics and monitoring."""
    
    def __init__(self, workflow_tracker=None, checkpoint_manager=None, 
                 template_manager=None, storage_manager=None):
        self.workflow_tracker = workflow_tracker
        self.checkpoint_manager = checkpoint_manager
        self.template_manager = template_manager
        self.storage_manager = storage_manager
        
        # Service-level metrics
        self._service_metrics = {
            "service_started_at": datetime.now().isoformat(),
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0
        }
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow service statistics.
        
        Returns:
            Dictionary with complete service statistics
        """
        try:
            statistics = {
                "service_info": self._get_service_info(),
                "workflow_statistics": self._get_workflow_statistics(),
                "checkpoint_statistics": self._get_checkpoint_statistics(),
                "template_statistics": self._get_template_statistics(),
                "storage_statistics": self._get_storage_statistics(),
                "performance_metrics": self._get_performance_metrics(),
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "statistics": statistics
            }
            
        except Exception as e:
            error_msg = f"Failed to get service statistics: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def _get_service_info(self) -> Dict[str, Any]:
        """Get basic service information."""
        uptime = datetime.now() - datetime.fromisoformat(self._service_metrics["service_started_at"])
        
        return {
            "service_name": "WorkflowStateService",
            "service_started_at": self._service_metrics["service_started_at"],
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime),
            "total_operations": self._service_metrics["total_operations"],
            "successful_operations": self._service_metrics["successful_operations"],
            "failed_operations": self._service_metrics["failed_operations"],
            "success_rate": (
                self._service_metrics["successful_operations"] / self._service_metrics["total_operations"] * 100
                if self._service_metrics["total_operations"] > 0 else 0.0
            )
        }
    
    def _get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow tracking statistics."""
        if not self.workflow_tracker:
            return {"error": "Workflow tracker not available"}
        
        try:
            return self.workflow_tracker.get_workflow_metrics()
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            return {"error": str(e)}
    
    def _get_checkpoint_statistics(self) -> Dict[str, Any]:
        """Get checkpoint management statistics."""
        if not self.checkpoint_manager:
            return {"error": "Checkpoint manager not available"}
        
        try:
            return self.checkpoint_manager.get_checkpoint_statistics()
        except Exception as e:
            logger.error(f"Failed to get checkpoint statistics: {e}")
            return {"error": str(e)}
    
    def _get_template_statistics(self) -> Dict[str, Any]:
        """Get template management statistics."""
        if not self.template_manager:
            return {"error": "Template manager not available"}
        
        try:
            return self.template_manager.get_template_statistics()
        except Exception as e:
            logger.error(f"Failed to get template statistics: {e}")
            return {"error": str(e)}
    
    def _get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage management statistics."""
        if not self.storage_manager:
            return {"error": "Storage manager not available"}
        
        try:
            return self.storage_manager.get_storage_statistics()
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {e}")
            return {"error": str(e)}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related metrics."""
        try:
            # Calculate average operation time if available
            avg_operation_time = 0.0
            if self._service_metrics["total_operations"] > 0:
                # This would need to be tracked during operations
                # For now, just provide structure
                avg_operation_time = 0.1  # Placeholder
            
            return {
                "average_operation_time_seconds": avg_operation_time,
                "operations_per_minute": self._calculate_operations_per_minute(),
                "memory_usage": self._get_memory_usage_info(),
                "error_rate": (
                    self._service_metrics["failed_operations"] / self._service_metrics["total_operations"] * 100
                    if self._service_metrics["total_operations"] > 0 else 0.0
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_operations_per_minute(self) -> float:
        """Calculate operations per minute based on service uptime."""
        try:
            uptime = datetime.now() - datetime.fromisoformat(self._service_metrics["service_started_at"])
            uptime_minutes = uptime.total_seconds() / 60
            
            if uptime_minutes > 0:
                return self._service_metrics["total_operations"] / uptime_minutes
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _get_memory_usage_info(self) -> Dict[str, Any]:
        """Get memory usage information if available."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                "memory_usage_mb": memory_info.rss / 1024 / 1024,
                "memory_percent": process.memory_percent(),
                "available": True
            }
            
        except ImportError:
            return {"available": False, "reason": "psutil not available"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def get_workflow_status_distribution(self) -> Dict[str, Any]:
        """Get distribution of workflow statuses.
        
        Returns:
            Dictionary with status distribution
        """
        try:
            if not self.workflow_tracker:
                return {"error": "Workflow tracker not available"}
            
            status_counts: Dict[str, int] = {}
            total_workflows = 0
            
            for workflow in self.workflow_tracker.workflows.values():
                status = workflow.status
                status_counts[status] = status_counts.get(status, 0) + 1
                total_workflows += 1
            
            # Calculate percentages
            status_percentages = {}
            for status, count in status_counts.items():
                status_percentages[status] = (count / total_workflows * 100) if total_workflows > 0 else 0
            
            return {
                "status": "success",
                "total_workflows": total_workflows,
                "status_counts": status_counts,
                "status_percentages": status_percentages
            }
            
        except Exception as e:
            error_msg = f"Failed to get workflow status distribution: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    def get_checkpoint_age_distribution(self) -> Dict[str, Any]:
        """Get distribution of checkpoint ages.
        
        Returns:
            Dictionary with checkpoint age distribution
        """
        try:
            if not self.checkpoint_manager:
                return {"error": "Checkpoint manager not available"}
            
            now = datetime.now()
            age_buckets = {
                "last_hour": 0,
                "last_day": 0,
                "last_week": 0,
                "last_month": 0,
                "older": 0
            }
            
            for checkpoint in self.checkpoint_manager.checkpoints.values():
                age = now - checkpoint.created_at
                
                if age.total_seconds() < 3600:  # 1 hour
                    age_buckets["last_hour"] += 1
                elif age.days < 1:
                    age_buckets["last_day"] += 1
                elif age.days < 7:
                    age_buckets["last_week"] += 1
                elif age.days < 30:
                    age_buckets["last_month"] += 1
                else:
                    age_buckets["older"] += 1
            
            total_checkpoints = sum(age_buckets.values())
            
            return {
                "status": "success",
                "total_checkpoints": total_checkpoints,
                "age_distribution": age_buckets
            }
            
        except Exception as e:
            error_msg = f"Failed to get checkpoint age distribution: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    def get_template_usage_statistics(self) -> Dict[str, Any]:
        """Get template usage statistics.
        
        Returns:
            Dictionary with template usage data
        """
        try:
            if not self.template_manager:
                return {"error": "Template manager not available"}
            
            # Get basic template metrics
            template_metrics = self.template_manager.get_template_statistics()
            
            # Add usage analysis
            templates_list = self.template_manager.list_workflow_templates()
            if templates_list.success:
                templates = templates_list.data.get("templates", [])
                
                # Analyze template characteristics
                data_templates = len([t for t in templates if t.get("include_data", False)])
                structure_templates = len(templates) - data_templates
                
                # Average steps analysis
                if templates:
                    step_counts = [t.get("total_steps", 0) for t in templates]
                    avg_steps = sum(step_counts) / len(step_counts)
                    min_steps = min(step_counts)
                    max_steps = max(step_counts)
                else:
                    avg_steps = min_steps = max_steps = 0
                
                template_metrics.update({
                    "data_vs_structure": {
                        "with_data": data_templates,
                        "structure_only": structure_templates
                    },
                    "step_analysis": {
                        "average_steps": avg_steps,
                        "min_steps": min_steps,
                        "max_steps": max_steps
                    }
                })
            
            return {
                "status": "success",
                "template_statistics": template_metrics
            }
            
        except Exception as e:
            error_msg = f"Failed to get template usage statistics: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    def record_operation(self, success: bool = True):
        """Record an operation for statistics tracking.
        
        Args:
            success: Whether the operation was successful
        """
        try:
            self._service_metrics["total_operations"] += 1
            if success:
                self._service_metrics["successful_operations"] += 1
            else:
                self._service_metrics["failed_operations"] += 1
                
        except Exception as e:
            logger.error(f"Failed to record operation: {e}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall service health summary.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Check each component
            components_health = {
                "workflow_tracker": self.workflow_tracker is not None,
                "checkpoint_manager": self.checkpoint_manager is not None,
                "template_manager": self.template_manager is not None,
                "storage_manager": self.storage_manager is not None
            }
            
            # Calculate overall health
            healthy_components = sum(components_health.values())
            total_components = len(components_health)
            health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 0
            
            # Determine status
            if health_percentage == 100:
                status = "healthy"
            elif health_percentage >= 75:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "health_percentage": health_percentage,
                "components": components_health,
                "service_metrics": self._service_metrics.copy(),
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to get health summary: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "checked_at": datetime.now().isoformat()
            }