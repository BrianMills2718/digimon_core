"""Progress Monitor (<150 lines)

Tracks execution progress and provides real-time status updates.
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime
from ...logging_config import get_logger

logger = get_logger("core.orchestration.progress_monitor")


class ProgressMonitor:
    """Monitor and track pipeline execution progress"""
    
    def __init__(self):
        self.logger = get_logger("core.orchestration.progress_monitor")
        self.execution_start_time = None
        self.execution_context = None
        self.tool_progress = []
        self.current_tool_index = 0
        self.total_tools = 0
        self.is_active = False
        
    def start_execution(self, context: Dict[str, Any]):
        """Start monitoring execution with given context"""
        self.execution_start_time = time.time()
        self.execution_context = context.copy()
        self.tool_progress = []
        self.current_tool_index = 0
        self.total_tools = 0
        self.is_active = True
        
        self.logger.info(f"Started progress monitoring for workflow: {context.get('workflow_id', 'unknown')}")
        
    def tool_started(self, tool: Any, tool_index: int, total_tools: int):
        """Record that a tool has started execution"""
        if not self.is_active:
            return
            
        self.current_tool_index = tool_index
        self.total_tools = total_tools
        
        tool_info = {
            "tool_name": tool.__class__.__name__,
            "tool_index": tool_index,
            "start_time": time.time(),
            "status": "running"
        }
        
        self.tool_progress.append(tool_info)
        
        progress_percent = (tool_index / total_tools) * 100 if total_tools > 0 else 0
        self.logger.info(f"Tool {tool_index + 1}/{total_tools} started: {tool.__class__.__name__} ({progress_percent:.1f}%)")
        
    def tool_completed(self, tool: Any, result: Any, execution_time: float):
        """Record that a tool has completed successfully"""
        if not self.is_active:
            return
            
        # Find and update the tool progress entry
        for tool_info in self.tool_progress:
            if (tool_info["tool_name"] == tool.__class__.__name__ and 
                tool_info["status"] == "running"):
                tool_info.update({
                    "status": "completed",
                    "end_time": time.time(),
                    "execution_time": execution_time,
                    "result_summary": self._summarize_result(result)
                })
                break
        
        progress_percent = ((self.current_tool_index + 1) / self.total_tools) * 100 if self.total_tools > 0 else 0
        self.logger.info(f"Tool {self.current_tool_index + 1}/{self.total_tools} completed: {tool.__class__.__name__} in {execution_time:.2f}s ({progress_percent:.1f}%)")
        
    def tool_failed(self, tool: Any, error: Exception, execution_time: float):
        """Record that a tool has failed"""
        if not self.is_active:
            return
            
        # Find and update the tool progress entry
        for tool_info in self.tool_progress:
            if (tool_info["tool_name"] == tool.__class__.__name__ and 
                tool_info["status"] == "running"):
                tool_info.update({
                    "status": "failed",
                    "end_time": time.time(),
                    "execution_time": execution_time,
                    "error": str(error)
                })
                break
        
        self.logger.error(f"Tool {self.current_tool_index + 1}/{self.total_tools} failed: {tool.__class__.__name__} - {str(error)}")
        
    def complete_execution(self):
        """Mark execution as complete"""
        if not self.is_active:
            return
            
        self.is_active = False
        total_execution_time = time.time() - self.execution_start_time if self.execution_start_time else 0
        
        completed_tools = len([t for t in self.tool_progress if t["status"] == "completed"])
        failed_tools = len([t for t in self.tool_progress if t["status"] == "failed"])
        
        self.logger.info(f"Execution completed: {completed_tools} tools succeeded, {failed_tools} tools failed, total time: {total_execution_time:.2f}s")
        
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information"""
        if not self.execution_start_time:
            return {"status": "not_started"}
            
        current_time = time.time()
        elapsed_time = current_time - self.execution_start_time
        
        completed_tools = len([t for t in self.tool_progress if t["status"] == "completed"])
        failed_tools = len([t for t in self.tool_progress if t["status"] == "failed"])
        running_tools = len([t for t in self.tool_progress if t["status"] == "running"])
        
        progress_percent = (completed_tools / self.total_tools) * 100 if self.total_tools > 0 else 0
        
        return {
            "status": "running" if self.is_active else "completed",
            "workflow_id": self.execution_context.get("workflow_id", "unknown") if self.execution_context else "unknown",
            "elapsed_time": elapsed_time,
            "progress_percent": progress_percent,
            "tools": {
                "total": self.total_tools,
                "completed": completed_tools,
                "failed": failed_tools,
                "running": running_tools
            },
            "current_tool": self.current_tool_index + 1 if self.total_tools > 0 else 0,
            "tool_progress": self.tool_progress.copy()
        }
        
    def get_estimated_completion_time(self) -> Optional[float]:
        """Estimate time to completion based on current progress"""
        if not self.is_active or self.total_tools == 0:
            return None
            
        completed_tools = len([t for t in self.tool_progress if t["status"] == "completed"])
        
        if completed_tools == 0:
            return None
            
        elapsed_time = time.time() - self.execution_start_time
        avg_time_per_tool = elapsed_time / completed_tools
        remaining_tools = self.total_tools - completed_tools
        
        return remaining_tools * avg_time_per_tool
        
    def _summarize_result(self, result: Any) -> Dict[str, Any]:
        """Create summary of tool result"""
        if isinstance(result, dict):
            summary = {
                "status": result.get("status", "unknown"),
                "keys": list(result.keys())[:5]  # Limit to first 5 keys
            }
            
            # Count items in common result fields
            for key in ["entities", "relationships", "chunks", "documents"]:
                if key in result and isinstance(result[key], list):
                    summary[f"{key}_count"] = len(result[key])
                    
            return summary
        else:
            return {"type": type(result).__name__}
    
    def health_check(self) -> bool:
        """Check if progress monitor is healthy"""
        return True  # Progress monitor is stateless and always healthy