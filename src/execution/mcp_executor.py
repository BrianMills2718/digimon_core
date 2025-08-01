"""
MCP-Based Tool Execution Engine
Executes tool chains via MCP protocol instead of direct Python calls
"""
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import time

from ..nlp.question_parser import ExecutionPlan, ExecutionStep
from ..core.base_tool import ToolResult

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of executing a tool chain"""
    tool_outputs: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    total_execution_time: float
    success_count: int
    failure_count: int
    errors: List[str]

class ResultCollector:
    """Collect and format results from tool execution"""
    
    def compile_final_result(self, tool_results: Dict[str, Any], 
                           original_question: str, 
                           execution_time: float) -> ExecutionResult:
        """Compile final result from individual tool results"""
        
        success_count = 0
        failure_count = 0
        errors = []
        
        for tool_id, result in tool_results.items():
            if isinstance(result, dict):
                if result.get('status') == 'success':
                    success_count += 1
                else:
                    failure_count += 1
                    if result.get('error'):
                        errors.append(f"{tool_id}: {result['error']}")
            elif isinstance(result, ToolResult):
                if result.status == 'success':
                    success_count += 1
                else:
                    failure_count += 1
                    if result.error:
                        errors.append(f"{tool_id}: {result.error}")
        
        execution_metadata = {
            'original_question': original_question,
            'tools_executed': list(tool_results.keys()),
            'execution_time': execution_time,
            'timestamp': time.time()
        }
        
        return ExecutionResult(
            tool_outputs=tool_results,
            execution_metadata=execution_metadata,
            total_execution_time=execution_time,
            success_count=success_count,
            failure_count=failure_count,
            errors=errors
        )

class MCPExecutor:
    """Execute tool chains via MCP protocol"""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self.result_collector = ResultCollector()
        
        # If no MCP client provided, create one from the compatibility layer
        if not self.mcp_client:
            self._initialize_mcp_client()
    
    def _initialize_mcp_client(self):
        """Initialize MCP client using compatibility layer"""
        try:
            from ..core.service_manager import ServiceManager
            from ..mcp.tool_wrapper import MCPCompatibilityLayer
            
            service_manager = ServiceManager()
            self.mcp_client = MCPCompatibilityLayer(service_manager)
            logger.info("MCP client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            self.mcp_client = None
    
    async def execute_tool_chain(self, execution_plan: ExecutionPlan, 
                                original_question: str = "") -> ExecutionResult:
        """Execute sequence of tools via MCP"""
        
        if not self.mcp_client:
            raise RuntimeError("MCP client not available")
        
        start_time = time.time()
        results = {}
        
        logger.info(f"Starting execution of {len(execution_plan.steps)} tools")
        
        # Execute steps in order (for Phase A, we'll do sequential execution)
        for i, step in enumerate(execution_plan.steps):
            logger.info(f"Executing step {i+1}/{len(execution_plan.steps)}: {step.tool_id}")
            
            try:
                # Resolve dependencies by updating arguments with previous results
                resolved_arguments = await self._resolve_step_dependencies(step, results)
                
                # Execute tool via MCP
                result = await self._execute_single_tool(step.tool_id, resolved_arguments)
                
                # Store result
                results[step.tool_id] = result
                
                logger.info(f"Step {i+1} completed successfully")
                
            except Exception as e:
                logger.error(f"Step {i+1} failed: {e}")
                
                # Store error result
                results[step.tool_id] = {
                    'status': 'error',
                    'error': str(e),
                    'result': None,
                    'metadata': {'execution_time': 0.0}
                }
                
                # Decide whether to continue or stop
                if not step.optional:
                    logger.error("Required step failed, stopping execution")
                    break
        
        total_time = time.time() - start_time
        
        # Compile final result
        execution_result = self.result_collector.compile_final_result(
            results, original_question, total_time
        )
        
        logger.info(f"Execution completed in {total_time:.2f}s. "
                   f"Success: {execution_result.success_count}, "
                   f"Failures: {execution_result.failure_count}")
        
        return execution_result
    
    async def _resolve_step_dependencies(self, step: ExecutionStep, 
                                       previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve step dependencies by updating arguments with previous results"""
        
        resolved_args = step.arguments.copy()
        
        # If this step depends on previous steps, update input_data
        if step.depends_on:
            for dependency in step.depends_on:
                if dependency in previous_results:
                    prev_result = previous_results[dependency]
                    
                    # Extract the actual result data
                    if isinstance(prev_result, dict) and 'data' in prev_result:
                        result_data = prev_result['data']
                        
                        # Update input_data based on tool type
                        if step.tool_id == "T15A_TEXT_CHUNKER" and dependency == "T01_PDF_LOADER":
                            # Text chunker needs document text
                            resolved_args["input_data"]["text"] = result_data.get("text", "")
                        elif step.tool_id == "T23A_SPACY_NER" and dependency == "T15A_TEXT_CHUNKER":
                            # NER needs chunks
                            resolved_args["input_data"]["chunks"] = result_data.get("chunks", [])
                        elif step.tool_id == "T27_RELATIONSHIP_EXTRACTOR":
                            # Relationship extractor needs text and entities
                            if dependency == "T15A_TEXT_CHUNKER":
                                resolved_args["input_data"]["chunks"] = result_data.get("chunks", [])
                            elif dependency == "T23A_SPACY_NER":
                                resolved_args["input_data"]["entities"] = result_data.get("entities", [])
                        elif step.tool_id == "T31_ENTITY_BUILDER" and dependency == "T23A_SPACY_NER":
                            # Entity builder needs entities
                            resolved_args["input_data"]["entities"] = result_data.get("entities", [])
                        elif step.tool_id == "T34_EDGE_BUILDER" and dependency == "T27_RELATIONSHIP_EXTRACTOR":
                            # Edge builder needs relationships
                            resolved_args["input_data"]["relationships"] = result_data.get("relationships", [])
        
        return resolved_args
    
    async def _execute_single_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool via MCP"""
        
        step_start_time = time.time()
        
        try:
            # Call tool via MCP
            mcp_result = await self.mcp_client.call_tool(tool_id, arguments)
            
            execution_time = time.time() - step_start_time
            
            # Parse MCP result
            if mcp_result.get('isError', False):
                error_content = mcp_result.get('content', [{}])[0].get('text', 'Unknown error')
                return {
                    'status': 'error',
                    'error': error_content,
                    'result': None,
                    'metadata': {'execution_time': execution_time}
                }
            else:
                # Parse the text response back to structured data
                content_text = mcp_result.get('content', [{}])[0].get('text', '{}')
                
                # For Phase A, we'll parse the string representation back to dict
                # In a full implementation, this would be proper JSON
                try:
                    import ast
                    result_data = ast.literal_eval(content_text)
                    
                    return {
                        'status': 'success',
                        'result': result_data.get('result', {}),
                        'error': None,
                        'metadata': {
                            'execution_time': execution_time,
                            'tool_id': tool_id
                        }
                    }
                except (ValueError, SyntaxError):
                    # If parsing fails, treat as text result
                    return {
                        'status': 'success',
                        'result': {'output': content_text},
                        'error': None,
                        'metadata': {'execution_time': execution_time}
                    }
                
        except Exception as e:
            execution_time = time.time() - step_start_time
            logger.error(f"Error executing tool {tool_id}: {e}")
            
            return {
                'status': 'error',
                'error': str(e),
                'result': None,
                'metadata': {'execution_time': execution_time}
            }
    
    async def execute_tools_parallel(self, tool_batch: List[ExecutionStep]) -> Dict[str, Any]:
        """Execute independent tools in parallel (for future use in Phase B)"""
        
        if not tool_batch:
            return {}
        
        logger.info(f"Executing {len(tool_batch)} tools in parallel")
        
        # Create tasks for parallel execution
        tasks = []
        for step in tool_batch:
            task = self._execute_single_tool(step.tool_id, step.arguments)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        parallel_results = {}
        for i, result in enumerate(results):
            tool_id = tool_batch[i].tool_id
            
            if isinstance(result, Exception):
                parallel_results[tool_id] = {
                    'status': 'error',
                    'error': str(result),
                    'result': None,
                    'metadata': {'execution_time': 0.0}
                }
            else:
                parallel_results[tool_id] = result
        
        return parallel_results
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'mcp_client_available': self.mcp_client is not None,
            'mcp_client_type': type(self.mcp_client).__name__ if self.mcp_client else None
        }

class PipelineManager:
    """Manage tool execution sequences and coordination"""
    
    def __init__(self, mcp_executor: MCPExecutor):
        self.mcp_executor = mcp_executor
        
    async def execute_pipeline(self, execution_plan: ExecutionPlan, 
                              original_question: str = "") -> ExecutionResult:
        """Execute complete pipeline with coordination and error handling"""
        
        logger.info(f"Starting pipeline execution for: {original_question}")
        
        try:
            # For Phase A, we use sequential execution
            result = await self.mcp_executor.execute_tool_chain(execution_plan, original_question)
            
            logger.info("Pipeline execution completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            
            # Return error result
            return ExecutionResult(
                tool_outputs={},
                execution_metadata={
                    'original_question': original_question,
                    'error': str(e),
                    'pipeline_failed': True
                },
                total_execution_time=0.0,
                success_count=0,
                failure_count=1,
                errors=[str(e)]
            )
    
    def validate_execution_plan(self, execution_plan: ExecutionPlan) -> List[str]:
        """Validate execution plan for potential issues"""
        
        issues = []
        
        # Check for circular dependencies
        tool_deps = {}
        for step in execution_plan.steps:
            tool_deps[step.tool_id] = step.depends_on or []
        
        # Simple cycle detection
        for tool_id in tool_deps:
            if self._has_circular_dependency(tool_id, tool_deps, set()):
                issues.append(f"Circular dependency detected involving {tool_id}")
        
        # Check for missing dependencies
        available_tools = {step.tool_id for step in execution_plan.steps}
        for step in execution_plan.steps:
            if step.depends_on:
                for dep in step.depends_on:
                    if dep not in available_tools:
                        issues.append(f"Tool {step.tool_id} depends on {dep} which is not in the execution plan")
        
        return issues
    
    def _has_circular_dependency(self, tool_id: str, tool_deps: Dict[str, List[str]], 
                               visited: set, path: set = None) -> bool:
        """Check for circular dependencies in tool execution plan"""
        
        if path is None:
            path = set()
        
        if tool_id in path:
            return True  # Circular dependency found
        
        if tool_id in visited:
            return False  # Already checked this path
        
        visited.add(tool_id)
        path.add(tool_id)
        
        for dep in tool_deps.get(tool_id, []):
            if self._has_circular_dependency(dep, tool_deps, visited, path):
                return True
        
        path.remove(tool_id)
        return False