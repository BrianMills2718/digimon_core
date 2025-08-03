"""Sequential Execution Engine (<200 lines)

Standard sequential execution for pipeline tools.
Provides reliable, straightforward execution with comprehensive error handling.
"""

from typing import List, Dict, Any, Optional
import time
from ...logging_config import get_logger
from ...config_manager import ConfigurationManager
from ...tool_protocol import Tool

logger = get_logger("core.orchestration.sequential_engine")


class SequentialEngine:
    """Sequential execution engine for standard pipeline execution"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.logger = get_logger("core.orchestration.sequential_engine")
        self.execution_stats = {
            "tools_executed": 0,
            "total_time": 0.0,
            "errors": []
        }
        
    def execute_pipeline(self, tools: List[Tool], input_data: Dict[str, Any], 
                        monitors: List[Any] = None) -> Dict[str, Any]:
        """Execute pipeline tools sequentially
        
        Args:
            tools: List of tools to execute
            input_data: Initial data for pipeline
            monitors: Optional list of monitors to track execution
            
        Returns:
            Results from pipeline execution
        """
        if not tools:
            raise ValueError("No tools provided for execution")
            
        current_data = input_data.copy()
        execution_results = []
        monitors = monitors or []
        
        start_time = time.time()
        
        try:
            for i, tool in enumerate(tools):
                # Notify monitors of tool start
                for monitor in monitors:
                    if hasattr(monitor, 'tool_started'):
                        monitor.tool_started(tool, i, len(tools))
                
                tool_start_time = time.time()
                
                try:
                    # Validate tool input
                    validation_result = tool.validate_input(current_data)
                    if not validation_result.is_valid:
                        raise ValueError(f"Tool {tool.__class__.__name__} input validation failed: {validation_result.validation_errors}")
                    
                    # Execute tool
                    self.logger.info(f"Executing tool {i+1}/{len(tools)}: {tool.__class__.__name__}")
                    result = tool.execute(current_data)
                    
                    # Update current data with results
                    if isinstance(result, dict):
                        current_data.update(result)
                    
                    tool_execution_time = time.time() - tool_start_time
                    
                    # Record execution result
                    execution_result = {
                        "tool_name": tool.__class__.__name__,
                        "tool_index": i,
                        "execution_time": tool_execution_time,
                        "status": "success",
                        "result_summary": self._summarize_result(result)
                    }
                    execution_results.append(execution_result)
                    
                    # Notify monitors of tool completion
                    for monitor in monitors:
                        if hasattr(monitor, 'tool_completed'):
                            monitor.tool_completed(tool, result, tool_execution_time)
                    
                    self.execution_stats["tools_executed"] += 1
                    
                except Exception as e:
                    tool_execution_time = time.time() - tool_start_time
                    error_msg = f"Tool {tool.__class__.__name__} failed: {str(e)}"
                    self.logger.error(error_msg)
                    
                    # Record error
                    execution_result = {
                        "tool_name": tool.__class__.__name__,
                        "tool_index": i,
                        "execution_time": tool_execution_time,
                        "status": "error",
                        "error": str(e)
                    }
                    execution_results.append(execution_result)
                    self.execution_stats["errors"].append(error_msg)
                    
                    # Notify monitors of error
                    for monitor in monitors:
                        if hasattr(monitor, 'tool_failed'):
                            monitor.tool_failed(tool, e, tool_execution_time)
                    
                    # Decide whether to continue or stop
                    if self._should_stop_on_error(tool, e):
                        raise
                    else:
                        self.logger.warning(f"Continuing execution despite error in {tool.__class__.__name__}")
                        continue
            
            total_execution_time = time.time() - start_time
            self.execution_stats["total_time"] = total_execution_time
            
            return {
                "status": "success",
                "execution_results": execution_results,
                "final_data": current_data,
                "execution_stats": self.execution_stats.copy(),
                "total_execution_time": total_execution_time
            }
            
        except Exception as e:
            total_execution_time = time.time() - start_time
            self.execution_stats["total_time"] = total_execution_time
            
            return {
                "status": "error",
                "error": str(e),
                "execution_results": execution_results,
                "partial_data": current_data,
                "execution_stats": self.execution_stats.copy(),
                "total_execution_time": total_execution_time
            }
    
    def _summarize_result(self, result: Any) -> Dict[str, Any]:
        """Create summary of tool execution result"""
        if isinstance(result, dict):
            summary = {
                "keys": list(result.keys()),
                "status": result.get("status", "unknown")
            }
            
            # Count items in lists
            for key, value in result.items():
                if isinstance(value, list):
                    summary[f"{key}_count"] = len(value)
                    
            return summary
        else:
            return {"type": type(result).__name__, "value": str(result)[:100]}
    
    def _should_stop_on_error(self, tool: Tool, error: Exception) -> bool:
        """Determine if execution should stop on error"""
        # Critical tools that should stop execution
        critical_tool_types = ['PDFLoader', 'EntityBuilder', 'EdgeBuilder']
        
        if any(tool_type in tool.__class__.__name__ for tool_type in critical_tool_types):
            return True
            
        # Critical error types that should stop execution
        critical_errors = ['RuntimeError', 'SystemError', 'MemoryError']
        
        if any(error_type in type(error).__name__ for error_type in critical_errors):
            return True
            
        return False
    
    def health_check(self) -> bool:
        """Check if sequential engine is healthy"""
        return True  # Sequential engine is always healthy
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats = {
            "tools_executed": 0,
            "total_time": 0.0,
            "errors": []
        }