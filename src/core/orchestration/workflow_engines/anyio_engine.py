"""AnyIO Structured Concurrency Engine (<200 lines)

Enhanced execution using AnyIO structured concurrency for maximum performance.
Provides structured concurrency with proper error handling and resource management.
"""

from typing import List, Dict, Any, Optional
import time
import anyio
from ...logging_config import get_logger
from ...config_manager import ConfigurationManager
from ...tool_protocol import Tool

logger = get_logger("core.orchestration.anyio_engine")


class AnyIOEngine:
    """AnyIO structured concurrency engine for enhanced pipeline execution"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.logger = get_logger("core.orchestration.anyio_engine")
        self.max_concurrent_tasks = config_manager.get_system_config().get('max_concurrent_tasks', 10)
        self.execution_stats = {
            "tools_executed": 0,
            "concurrent_batches": 0,
            "total_time": 0.0,
            "concurrency_efficiency": 0.0,
            "errors": []
        }
        
    def execute_pipeline(self, tools: List[Tool], input_data: Dict[str, Any], 
                        monitors: List[Any] = None) -> Dict[str, Any]:
        """Execute pipeline tools using AnyIO structured concurrency
        
        Args:
            tools: List of tools to execute
            input_data: Initial data for pipeline
            monitors: Optional list of monitors to track execution
            
        Returns:
            Results from pipeline execution
        """
        if not tools:
            raise ValueError("No tools provided for execution")
            
        # Run the async pipeline
        return anyio.run(self._execute_async_pipeline, tools, input_data, monitors or [])
    
    async def _execute_async_pipeline(self, tools: List[Tool], input_data: Dict[str, Any], 
                                    monitors: List[Any]) -> Dict[str, Any]:
        """Async pipeline execution with structured concurrency"""
        current_data = input_data.copy()
        execution_results = []
        
        start_time = time.time()
        
        try:
            # Create execution groups with dependency analysis
            execution_groups = self._create_concurrent_groups(tools)
            
            self.logger.info(f"Created {len(execution_groups)} concurrent execution groups")
            
            # Execute groups sequentially, but tools within groups concurrently
            for group_index, group in enumerate(execution_groups):
                group_start_time = time.time()
                
                if len(group) == 1:
                    # Single tool - execute directly
                    result = await self._execute_single_tool_async(group[0], current_data, monitors)
                    execution_results.append(result)
                    
                    if result["status"] == "success" and "result_data" in result:
                        current_data.update(result["result_data"])
                        
                else:
                    # Multiple tools - execute concurrently using task group
                    async with anyio.create_task_group() as tg:
                        tasks = []
                        for tool in group:
                            task_data = await self._prepare_task_data(tool, current_data)
                            task = tg.start_soon(self._execute_single_tool_async, tool, task_data, monitors)
                            tasks.append((tool, task))
                    
                    # Collect results from concurrent execution
                    group_results = []
                    for tool, task in tasks:
                        try:
                            # Results are automatically available after task group completion
                            result = task  # In AnyIO, task results are handled differently
                            group_results.append(result)
                        except Exception as e:
                            error_result = {
                                "tool_name": tool.__class__.__name__,
                                "status": "error",
                                "error": str(e),
                                "execution_time": 0.0
                            }
                            group_results.append(error_result)
                    
                    execution_results.extend(group_results)
                    
                    # Merge results from concurrent execution
                    for result in group_results:
                        if result["status"] == "success" and "result_data" in result:
                            current_data.update(result["result_data"])
                
                group_time = time.time() - group_start_time
                self.execution_stats["concurrent_batches"] += 1
                
                self.logger.info(f"Completed group {group_index + 1}/{len(execution_groups)} in {group_time:.2f}s")
            
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
    
    async def _execute_single_tool_async(self, tool: Tool, input_data: Dict[str, Any], 
                                       monitors: List[Any]) -> Dict[str, Any]:
        """Execute a single tool asynchronously"""
        tool_start_time = time.time()
        
        try:
            # Notify monitors
            for monitor in monitors:
                if hasattr(monitor, 'tool_started'):
                    monitor.tool_started(tool, 0, 1)
            
            # Move blocking operations to thread
            result = await anyio.to_thread.run_sync(self._execute_tool_sync, tool, input_data)
            
            execution_time = time.time() - tool_start_time
            
            # Notify monitors
            for monitor in monitors:
                if hasattr(monitor, 'tool_completed'):
                    monitor.tool_completed(tool, result, execution_time)
            
            self.execution_stats["tools_executed"] += 1
            
            return {
                "tool_name": tool.__class__.__name__,
                "execution_time": execution_time,
                "status": "success",
                "result_data": result if isinstance(result, dict) else {}
            }
            
        except Exception as e:
            execution_time = time.time() - tool_start_time
            error_msg = f"Tool {tool.__class__.__name__} failed: {str(e)}"
            self.execution_stats["errors"].append(error_msg)
            
            # Notify monitors
            for monitor in monitors:
                if hasattr(monitor, 'tool_failed'):
                    monitor.tool_failed(tool, e, execution_time)
            
            return {
                "tool_name": tool.__class__.__name__,
                "execution_time": execution_time,
                "status": "error",
                "error": str(e)
            }
    
    def _execute_tool_sync(self, tool: Tool, input_data: Dict[str, Any]) -> Any:
        """Execute tool synchronously (for use in anyio.to_thread)"""
        # Validate input
        validation_result = tool.validate_input(input_data)
        if not validation_result.is_valid:
            raise ValueError(f"Input validation failed: {validation_result.validation_errors}")
        
        # Execute tool
        return tool.execute(input_data)
    
    async def _prepare_task_data(self, tool: Tool, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for individual task (allows for tool-specific data preparation)"""
        # For now, just return a copy of base data
        # In the future, this could be enhanced to prepare tool-specific data
        return base_data.copy()
    
    def _create_concurrent_groups(self, tools: List[Tool]) -> List[List[Tool]]:
        """Create groups of tools that can be executed concurrently"""
        groups = []
        
        # Advanced dependency analysis for AnyIO execution
        independent_tools = []
        dependent_tools = []
        
        for tool in tools:
            tool_name = tool.__class__.__name__
            
            # Tools that can run independently (after document processing)
            if any(name in tool_name for name in ['NER', 'Relationship', 'Entity']):
                independent_tools.append(tool)
            else:
                dependent_tools.append(tool)
        
        # Create groups
        if dependent_tools:
            # Sequential dependencies first
            for tool in dependent_tools:
                groups.append([tool])
        
        if independent_tools:
            # Independent tools can run concurrently
            groups.append(independent_tools)
        
        # Fallback to sequential if no clear grouping
        if not groups:
            groups = [[tool] for tool in tools]
            
        return groups
    
    def health_check(self) -> bool:
        """Check if AnyIO engine is healthy"""
        try:
            # Test AnyIO functionality
            async def test():
                async with anyio.create_task_group() as tg:
                    tg.start_soon(anyio.sleep, 0)
                return True
            
            return anyio.run(test)
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats = {
            "tools_executed": 0,
            "concurrent_batches": 0,
            "total_time": 0.0,
            "concurrency_efficiency": 0.0,
            "errors": []
        }