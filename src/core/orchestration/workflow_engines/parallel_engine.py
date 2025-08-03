"""Parallel Execution Engine (<200 lines)

Parallel execution for pipeline tools where possible.
Identifies parallelizable tools and executes them concurrently.
"""

from typing import List, Dict, Any, Optional
import time
import asyncio
import concurrent.futures
from ...logging_config import get_logger
from ...config_manager import ConfigurationManager
from ...tool_protocol import Tool

logger = get_logger("core.orchestration.parallel_engine")


class ParallelEngine:
    """Parallel execution engine for optimized pipeline execution"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.logger = get_logger("core.orchestration.parallel_engine")
        self.max_workers = config_manager.get_system_config().get('max_parallel_workers', 4)
        self.execution_stats = {
            "tools_executed": 0,
            "parallel_batches": 0,
            "total_time": 0.0,
            "parallelization_savings": 0.0,
            "errors": []
        }
        
    def execute_pipeline(self, tools: List[Tool], input_data: Dict[str, Any], 
                        monitors: List[Any] = None) -> Dict[str, Any]:
        """Execute pipeline tools with parallelization where possible
        
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
            # Analyze dependencies and create execution batches
            execution_batches = self._create_execution_batches(tools)
            
            self.logger.info(f"Created {len(execution_batches)} execution batches for parallel processing")
            
            for batch_index, batch in enumerate(execution_batches):
                batch_start_time = time.time()
                
                if len(batch) == 1:
                    # Single tool - execute sequentially
                    tool = batch[0]
                    result = self._execute_single_tool(tool, current_data, monitors)
                    execution_results.append(result)
                    
                    if result["status"] == "success" and "result_data" in result:
                        current_data.update(result["result_data"])
                        
                else:
                    # Multiple tools - execute in parallel
                    batch_results = self._execute_parallel_batch(batch, current_data, monitors)
                    execution_results.extend(batch_results)
                    
                    # Merge results from parallel execution
                    for result in batch_results:
                        if result["status"] == "success" and "result_data" in result:
                            current_data.update(result["result_data"])
                
                batch_time = time.time() - batch_start_time
                self.execution_stats["parallel_batches"] += 1
                
                self.logger.info(f"Completed batch {batch_index + 1}/{len(execution_batches)} in {batch_time:.2f}s")
            
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
    
    def _create_execution_batches(self, tools: List[Tool]) -> List[List[Tool]]:
        """Create batches of tools that can be executed in parallel"""
        batches = []
        
        # Simple dependency analysis based on tool types
        document_processors = []
        entity_processors = []
        graph_builders = []
        analyzers = []
        
        for tool in tools:
            tool_name = tool.__class__.__name__
            
            if any(name in tool_name for name in ['PDF', 'Text', 'Chunk']):
                document_processors.append(tool)
            elif any(name in tool_name for name in ['NER', 'Entity', 'Relationship']):
                entity_processors.append(tool)
            elif any(name in tool_name for name in ['Builder', 'Edge']):
                graph_builders.append(tool)
            else:
                analyzers.append(tool)
        
        # Create batches with dependencies
        if document_processors:
            batches.append(document_processors)
        if entity_processors:
            batches.append(entity_processors)
        if graph_builders:
            batches.append(graph_builders)
        if analyzers:
            batches.append(analyzers)
            
        # If no clear categorization, fall back to sequential
        if not batches:
            batches = [[tool] for tool in tools]
            
        return batches
    
    def _execute_single_tool(self, tool: Tool, input_data: Dict[str, Any], 
                           monitors: List[Any]) -> Dict[str, Any]:
        """Execute a single tool"""
        tool_start_time = time.time()
        
        try:
            # Notify monitors
            for monitor in monitors:
                if hasattr(monitor, 'tool_started'):
                    monitor.tool_started(tool, 0, 1)
            
            # Validate and execute
            validation_result = tool.validate_input(input_data)
            if not validation_result.is_valid:
                raise ValueError(f"Input validation failed: {validation_result.validation_errors}")
            
            result = tool.execute(input_data)
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
    
    def _execute_parallel_batch(self, batch: List[Tool], input_data: Dict[str, Any], 
                              monitors: List[Any]) -> List[Dict[str, Any]]:
        """Execute a batch of tools in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(batch), self.max_workers)) as executor:
            # Submit all tools for execution
            future_to_tool = {
                executor.submit(self._execute_single_tool, tool, input_data, monitors): tool 
                for tool in batch
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_tool):
                tool = future_to_tool[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    error_result = {
                        "tool_name": tool.__class__.__name__,
                        "status": "error",
                        "error": str(e),
                        "execution_time": 0.0
                    }
                    results.append(error_result)
                    self.execution_stats["errors"].append(f"Parallel execution failed for {tool.__class__.__name__}: {str(e)}")
            
            return results
    
    def health_check(self) -> bool:
        """Check if parallel engine is healthy"""
        try:
            # Test thread pool creation
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(lambda: True)
                return future.result(timeout=1.0)
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats = {
            "tools_executed": 0,
            "parallel_batches": 0,
            "total_time": 0.0,
            "parallelization_savings": 0.0,
            "errors": []
        }