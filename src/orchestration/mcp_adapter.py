"""
MCP Tool Adapter for KGAS Agent Orchestration.

This adapter provides a clean interface between the orchestration system
and existing KGAS MCP tools, enabling complete decoupling and easy pivoting.
Supports structured output with Pydantic validation for tool orchestration.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Set, Union
from pathlib import Path

from .base import Result, Task

logger = logging.getLogger(__name__)


class MCPToolAdapter:
    """
    Adapter to existing KGAS MCP tools - keeps orchestration decoupled.
    
    This adapter isolates the orchestration system from the specifics of
    the MCP tool implementation, making it easy to swap out tool providers.
    """
    
    def __init__(self):
        """Initialize MCP tool adapter."""
        self.server_manager = None
        self.mcp_server = None
        self.tool_registry: Dict[str, Any] = {}
        self._initialized = False
        self._available_tools: Set[str] = set()
        self._limited_mode = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Structured output components (lazy initialization)
        self._structured_llm_service = None
        self._structured_output_enabled = None
    
    async def initialize(self) -> bool:
        """
        Connect to existing MCP infrastructure.
        
        Returns:
            True if initialization successful
        """
        try:
            # Import MCP components with fallback handling
            mcp_components = self._safe_import_mcp_tools()
            if not mcp_components:
                self.logger.warning("MCP tools unavailable - running in limited mode")
                self._limited_mode = True
                # Set up mock tools for limited mode
                self._setup_limited_mode_tools()
                self._initialized = True
                return True  # Still successful, just limited
            
            get_mcp_server_manager, create_phase1_mcp_tools = mcp_components
            self.logger.info("Initializing MCP tool adapter")
            
            # Get server manager instance
            self.server_manager = get_mcp_server_manager()
            
            # Register all tools
            self.server_manager.register_all_tools()
            
            # Get FastMCP server instance
            self.mcp_server = self.server_manager.get_server()
            
            # Add Phase 1 tools
            create_phase1_mcp_tools(self.mcp_server)
            
            # Build tool registry for quick access
            self._build_tool_registry()
            
            self._initialized = True
            self.logger.info(f"MCP adapter initialized with {len(self.tool_registry)} tools")
            
            return True
            
        except ImportError as e:
            self.logger.error(f"Failed to import MCP components: {e}")
            self.logger.warning("Running in limited mode without MCP tools")
            self._initialized = False
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP adapter: {e}")
            self._initialized = False
            return False
    
    def _build_tool_registry(self) -> None:
        """Build tool registry from MCP server."""
        try:
            if not self.mcp_server:
                self.logger.warning("No MCP server available")
                # In limited mode, add mock tools for testing
                if self._limited_mode:
                    self._setup_limited_mode_tools()
                return
            
            # Access tools through FastMCP's tool manager
            tools_dict = None
            
            # FastMCP stores tools in _tool_manager._tools
            if hasattr(self.mcp_server, '_tool_manager') and hasattr(self.mcp_server._tool_manager, '_tools'):
                tools_dict = self.mcp_server._tool_manager._tools
                self.logger.debug(f"Found {len(tools_dict)} tools in _tool_manager._tools")
            # Fallback: try legacy access patterns
            elif hasattr(self.mcp_server, '_tools'):
                tools_dict = self.mcp_server._tools
                self.logger.debug("Using legacy _tools attribute")
            elif hasattr(self.mcp_server, 'tools'):
                tools_dict = self.mcp_server.tools
                self.logger.debug("Using legacy tools attribute")
            
            if tools_dict:
                self.tool_registry = dict(tools_dict)
                self._available_tools = set(tools_dict.keys())
                self.logger.info(f"Built tool registry with {len(self.tool_registry)} tools")
                
                # Log first few tools for debugging
                if self._available_tools:
                    sample_tools = list(self._available_tools)[:5]
                    self.logger.debug(f"Sample tools: {sample_tools}")
            else:
                self.logger.warning("Could not access tools from MCP server")
                self.logger.debug(f"Server attributes: {[attr for attr in dir(self.mcp_server) if 'tool' in attr.lower()]}")
                
        except Exception as e:
            self.logger.error(f"Error building tool registry: {e}")
            import traceback
            self.logger.debug(f"Full traceback: {traceback.format_exc()}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> Result:
        """
        Call existing MCP tools through adapter.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Result object with tool execution results
        """
        start_time = time.time()
        parameters = parameters or {}
        
        try:
            # Check if initialized
            if not self._initialized:
                return Result(
                    success=False,
                    error="MCP adapter not initialized",
                    metadata={
                        "tool": tool_name,
                        "execution_time": time.time() - start_time
                    }
                )
            
            # Validate tool exists
            if tool_name not in self.tool_registry:
                return Result(
                    success=False,
                    error=f"Tool '{tool_name}' not found",
                    metadata={
                        "available_tools": list(self._available_tools),
                        "execution_time": time.time() - start_time
                    }
                )
            
            # Log tool call
            self.logger.debug(f"Calling tool '{tool_name}' with parameters: {parameters}")
            
            # Handle limited mode with mock tools
            if self._limited_mode and tool_name in self.tool_registry:
                tool_func = self.tool_registry[tool_name]
                if callable(tool_func):
                    try:
                        if parameters:
                            result_data = await tool_func(**parameters)
                        else:
                            result_data = await tool_func()
                        
                        return Result(
                            success=True,
                            data=result_data,
                            metadata={
                                "tool": tool_name,
                                "adapter": "limited_mode_mock",
                                "execution_time": time.time() - start_time,
                                "parameters": parameters
                            }
                        )
                    except Exception as e:
                        return Result(
                            success=False,
                            error=f"Mock tool execution failed: {str(e)}",
                            metadata={
                                "tool": tool_name,
                                "execution_time": time.time() - start_time,
                                "error_type": type(e).__name__
                            }
                        )
            
            # Use FastMCP's tool manager to call the tool properly
            if hasattr(self.mcp_server, '_tool_manager'):
                tool_result = await self.mcp_server._tool_manager.call_tool(tool_name, parameters)
                
                # Extract result from FastMCP ToolResult object
                result_data = None
                
                if hasattr(tool_result, 'content') and tool_result.content:
                    # FastMCP returns content as a list of content objects
                    if isinstance(tool_result.content, list) and len(tool_result.content) > 0:
                        first_content = tool_result.content[0]
                        if hasattr(first_content, 'text'):
                            result_data = first_content.text
                        else:
                            result_data = str(first_content)
                    else:
                        result_data = tool_result.content
                elif hasattr(tool_result, 'result'):
                    result_data = tool_result.result
                elif hasattr(tool_result, 'data'):
                    result_data = tool_result.data
                else:
                    result_data = str(tool_result)
                
                # Try to parse JSON if it looks like JSON
                if isinstance(result_data, str):
                    try:
                        import json
                        if result_data.strip().startswith(('{', '[')):
                            result_data = json.loads(result_data)
                    except:
                        pass  # Keep as string if JSON parsing fails
                
                # Create success result
                return Result(
                    success=True,
                    data=result_data,
                    metadata={
                        "tool": tool_name,
                        "adapter": "mcp_fastmcp",
                        "execution_time": time.time() - start_time,
                        "parameters": parameters
                    }
                )
            else:
                # Fallback to direct tool calling (shouldn't happen with FastMCP)
                tool_func = self.tool_registry[tool_name]
                
                if callable(tool_func):
                    if parameters:
                        result = tool_func(**parameters)
                    else:
                        result = tool_func()
                else:
                    return Result(
                        success=False,
                        error=f"Tool '{tool_name}' is not callable",
                        execution_time=time.time() - start_time
                    )
                
                return Result(
                    success=True,
                    data=result,
                    metadata={
                        "tool": tool_name,
                        "adapter": "mcp_direct",
                        "execution_time": time.time() - start_time,
                        "parameters": parameters
                    }
                )
            
        except TypeError as e:
            # Parameter mismatch
            return Result(
                success=False,
                error=f"Tool parameter error: {str(e)}",
                metadata={
                    "tool": tool_name,
                    "execution_time": time.time() - start_time,
                    "parameters": parameters
                }
            )
            
        except Exception as e:
            # General execution error
            self.logger.error(f"Tool execution failed for '{tool_name}': {e}")
            return Result(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                metadata={
                    "tool": tool_name,
                    "execution_time": time.time() - start_time,
                    "parameters": parameters,
                    "error_type": type(e).__name__
                }
            )
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available MCP tools.
        
        Returns:
            List of tool names
        """
        return list(self._available_tools)
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information dictionary
        """
        if tool_name not in self.tool_registry:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool_func = self.tool_registry[tool_name]
        
        info = {
            "name": tool_name,
            "available": True,
            "callable": callable(tool_func)
        }
        
        # Try to get docstring
        if hasattr(tool_func, '__doc__') and tool_func.__doc__:
            info["description"] = tool_func.__doc__.strip()
        
        # Try to get signature
        try:
            import inspect
            sig = inspect.signature(tool_func)
            info["parameters"] = str(sig)
        except:
            pass
        
        return info
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """
        Get tools organized by category.
        
        Returns:
            Dictionary mapping categories to tool lists
        """
        categories = {
            "document_processing": [],
            "entity_extraction": [],
            "relationship_extraction": [],
            "graph_building": [],
            "graph_analysis": [],
            "text_processing": [],
            "server_management": [],
            "other": []
        }
        
        # Categorize tools based on name patterns
        for tool_name in self._available_tools:
            if any(pattern in tool_name for pattern in ["pdf", "document", "load"]):
                categories["document_processing"].append(tool_name)
            elif any(pattern in tool_name for pattern in ["entit", "ner"]):
                categories["entity_extraction"].append(tool_name)
            elif any(pattern in tool_name for pattern in ["relationship", "relation"]):
                categories["relationship_extraction"].append(tool_name)
            elif any(pattern in tool_name for pattern in ["build_entities", "build_edges", "graph_build"]):
                categories["graph_building"].append(tool_name)
            elif any(pattern in tool_name for pattern in ["pagerank", "query_graph", "multihop"]):
                categories["graph_analysis"].append(tool_name)
            elif any(pattern in tool_name for pattern in ["chunk", "text"]):
                categories["text_processing"].append(tool_name)
            elif any(pattern in tool_name for pattern in ["test_connection", "echo", "status"]):
                categories["server_management"].append(tool_name)
            else:
                categories["other"].append(tool_name)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of MCP adapter and tools.
        
        Returns:
            Health status dictionary
        """
        health = {
            "initialized": self._initialized,
            "server_manager": self.server_manager is not None,
            "mcp_server": self.mcp_server is not None,
            "total_tools": len(self.tool_registry),
            "tool_categories": len(self.get_tools_by_category())
        }
        
        # Test a simple tool if available
        if "test_connection" in self.tool_registry:
            try:
                result = await self.call_tool("test_connection")
                health["test_connection"] = result.success
            except:
                health["test_connection"] = False
        
        health["status"] = "healthy" if health.get("initialized") and health.get("total_tools", 0) > 0 else "unhealthy"
        
        return health
    
    def _safe_import_mcp_tools(self):
        """Import MCP components with fallback handling."""
        try:
            # Try relative import first (package context)
            from ..mcp_tools.server_manager import get_mcp_server_manager
            from ..tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
            return get_mcp_server_manager, create_phase1_mcp_tools
        except ImportError:
            try:
                # Try absolute import with path adjustment (script context)
                import sys
                from pathlib import Path
                src_dir = Path(__file__).parent.parent
                if str(src_dir) not in sys.path:
                    sys.path.insert(0, str(src_dir))
                
                from mcp_tools.server_manager import get_mcp_server_manager
                from tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
                return get_mcp_server_manager, create_phase1_mcp_tools
            except ImportError as e:
                # Log the error and return None for limited mode
                self.logger.warning(f"Failed to import MCP components: {e}")
                return None
    
    def _setup_limited_mode_tools(self) -> None:
        """Setup mock tools for limited mode testing."""
        async def mock_test_connection():
            return {"status": "connected", "mock": True}
        
        async def mock_load_pdf(file_path: str = ""):
            return {"status": "loaded", "file": file_path, "mock": True}
        
        async def mock_chunk_text(text: str = ""):
            return {"chunks": ["chunk1", "chunk2"], "mock": True}
        
        async def mock_extract_entities(text: str = ""):
            return {"entities": [{"text": "MockEntity", "type": "MOCK"}], "mock": True}
        
        # Add mock tools to registry
        self.tool_registry = {
            "test_connection": mock_test_connection,
            "load_pdf": mock_load_pdf,
            "chunk_text": mock_chunk_text,
            "extract_entities": mock_extract_entities
        }
        self._available_tools = set(self.tool_registry.keys())
        self.logger.info(f"Limited mode: Added {len(self.tool_registry)} mock tools")
    
    def _is_structured_output_enabled(self) -> bool:
        """Check if structured output is enabled for MCP adapter."""
        if self._structured_output_enabled is None:
            try:
                from ..core.feature_flags import is_structured_output_enabled
                self._structured_output_enabled = is_structured_output_enabled("mcp_adapter")
                self.logger.debug(f"MCP adapter structured output enabled: {self._structured_output_enabled}")
            except ImportError:
                self.logger.warning("Feature flags not available, using legacy mode")
                self._structured_output_enabled = False
        return self._structured_output_enabled
    
    def _get_structured_llm_service(self):
        """Get structured LLM service instance (lazy initialization)."""
        if self._structured_llm_service is None:
            try:
                from ..core.structured_llm_service import get_structured_llm_service
                self._structured_llm_service = get_structured_llm_service()
                self.logger.debug("Structured LLM service initialized for MCP adapter")
            except ImportError as e:
                self.logger.error(f"Failed to import structured LLM service: {e}")
                raise RuntimeError("Structured LLM service not available") from e
        return self._structured_llm_service
    
    async def orchestrate_tools_structured(self, 
                                          task_description: str,
                                          available_tools: Optional[List[str]] = None,
                                          context: Optional[Dict[str, Any]] = None) -> Result:
        """
        Use structured output to orchestrate tool selection and execution.
        
        Args:
            task_description: Description of the task to accomplish
            available_tools: Optional list of tools to consider (defaults to all available)
            context: Optional context information for decision making
            
        Returns:
            Result object with orchestration results
        """
        start_time = time.time()
        
        try:
            if not self._is_structured_output_enabled():
                self.logger.debug("Structured output not enabled, falling back to legacy method")
                return await self._orchestrate_tools_legacy(task_description, available_tools, context)
            
            from .reasoning_schema import MCPOrchestrationResponse, MCPToolSelection
            
            structured_llm = self._get_structured_llm_service()
            
            # Prepare tool information for LLM
            tools_list = available_tools or list(self._available_tools)
            tool_descriptions = {}
            for tool_name in tools_list:
                tool_info = self.get_tool_info(tool_name)
                tool_descriptions[tool_name] = tool_info.get("description", "No description available")
            
            # Build structured orchestration prompt
            prompt = self._build_orchestration_prompt(task_description, tool_descriptions, context)
            
            # Get structured response with retry logic
            max_retries = 2
            orchestration_response = None
            
            for attempt in range(max_retries + 1):
                try:
                    orchestration_response = structured_llm.structured_completion(
                        prompt=prompt,
                        schema=MCPOrchestrationResponse,
                        model="smart",
                        temperature=0.05,  # Optimal for structured JSON output
                        max_tokens=16000
                    )
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if attempt < max_retries:
                        self.logger.warning(f"Structured completion failed (attempt {attempt + 1}/{max_retries + 1}), retrying: {e}")
                        continue
                    else:
                        # Final attempt failed
                        self.logger.error(f"Structured completion failed after {max_retries + 1} attempts: {e}")
                        raise
            
            if orchestration_response is None:
                raise RuntimeError("Failed to get orchestration response after retries")
            
            # Execute selected tools in order
            tool_results = []
            execution_start = time.time()
            
            for tool_name in orchestration_response.decision.execution_order:
                if tool_name in orchestration_response.decision.tool_parameters:
                    params = orchestration_response.decision.tool_parameters[tool_name]
                else:
                    params = {}
                
                self.logger.info(f"Executing tool '{tool_name}' with structured orchestration")
                result = await self.call_tool(tool_name, params)
                tool_results.append(result)
                
                # Stop execution if a critical tool fails
                if not result.success and "critical" in tool_name.lower():
                    self.logger.warning(f"Critical tool '{tool_name}' failed, stopping orchestration")
                    break
            
            execution_time = time.time() - execution_start
            total_time = time.time() - start_time
            
            # Package results with structured metadata
            orchestration_result = {
                "orchestration_decision": orchestration_response.decision.model_dump(),
                "reasoning_chain": [step.model_dump() for step in orchestration_response.reasoning_chain],
                "tool_results": [r.model_dump() if hasattr(r, 'model_dump') else r.__dict__ for r in tool_results],
                "execution_summary": {
                    "total_tools_executed": len(tool_results),
                    "successful_tools": sum(1 for r in tool_results if r.success),
                    "failed_tools": sum(1 for r in tool_results if not r.success),
                    "execution_time": execution_time,
                    "confidence": orchestration_response.confidence
                }
            }
            
            success = all(r.success for r in tool_results) if tool_results else False
            
            return Result(
                success=success,
                data=orchestration_result,
                metadata={
                    "method": "structured_orchestration",
                    "llm_reasoning": "structured_output_with_pydantic",
                    "total_execution_time": total_time,
                    "orchestration_confidence": orchestration_response.confidence,
                    "alternatives_considered": len(orchestration_response.alternatives_considered)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Structured orchestration failed: {e}")
            # Fail fast - no fallback to legacy in structured mode
            return Result(
                success=False,
                error=f"Structured orchestration failed: {str(e)}",
                metadata={
                    "method": "structured_orchestration",
                    "execution_time": time.time() - start_time,
                    "error_type": type(e).__name__
                }
            )
    
    async def _orchestrate_tools_legacy(self, 
                                       task_description: str,
                                       available_tools: Optional[List[str]] = None,
                                       context: Optional[Dict[str, Any]] = None) -> Result:
        """Legacy tool orchestration method (preserved for compatibility)."""
        # Simple heuristic-based tool selection for legacy mode
        tools_to_execute = available_tools or ["test_connection"]
        
        results = []
        for tool_name in tools_to_execute:
            result = await self.call_tool(tool_name)
            results.append(result)
        
        return Result(
            success=all(r.success for r in results),
            data={"legacy_results": results},
            metadata={"method": "legacy_orchestration"}
        )
    
    def _build_orchestration_prompt(self, 
                                   task_description: str,
                                   tool_descriptions: Dict[str, str],
                                   context: Optional[Dict[str, Any]] = None) -> str:
        """Build comprehensive prompt for tool orchestration."""
        return f"""
You are an expert tool orchestrator for a knowledge graph analysis system. Your task is to select and order the optimal tools to accomplish the given task.

Task Description:
{task_description}

Available Tools:
{self._format_tool_descriptions(tool_descriptions)}

Context:
{context or "No additional context provided"}

Requirements:
- Select only the tools necessary to complete the task effectively
- Order tools in logical execution sequence (dependencies first)
- Provide specific parameters for each tool based on the task
- Explain your reasoning for tool selection and ordering
- Consider alternative approaches and explain why you chose this approach
- Provide confidence score based on task clarity and tool availability

Guidelines:
- Use document loading tools (T01) before processing tools
- Use text chunking (T15A) after loading documents
- Use entity extraction (T23A) after text chunking
- Use relationship extraction (T27) after entity extraction
- Use graph building tools (T31, T34) after extraction
- Use analysis tools (T68, T49) after graph building
- Only select tools that directly contribute to the task
"""
    
    def _format_tool_descriptions(self, tool_descriptions: Dict[str, str]) -> str:
        """Format tool descriptions for the prompt."""
        formatted = []
        for tool_name, description in tool_descriptions.items():
            formatted.append(f"- {tool_name}: {description}")
        return "\n".join(formatted)
    
    async def execute_tool_batch_structured(self, tools_and_params: List[Dict[str, Any]]) -> Result:
        """
        Execute multiple tools in batch with structured result aggregation.
        
        Args:
            tools_and_params: List of dicts with 'tool_name' and 'parameters' keys
            
        Returns:
            Result with structured batch execution results
        """
        start_time = time.time()
        
        try:
            if not self._is_structured_output_enabled():
                return await self._execute_tool_batch_legacy(tools_and_params)
            
            from .reasoning_schema import MCPBatchToolResult, MCPToolResult
            
            tool_results = []
            
            for tool_spec in tools_and_params:
                tool_name = tool_spec["tool_name"]
                parameters = tool_spec.get("parameters", {})
                
                tool_start = time.time()
                result = await self.call_tool(tool_name, parameters)
                tool_time = time.time() - tool_start
                
                # Create structured tool result
                structured_result = MCPToolResult(
                    tool_name=tool_name,
                    success=result.success,
                    output=result.data,
                    error_message=result.error if not result.success else None,
                    execution_time=tool_time,
                    metadata=result.metadata or {}
                )
                
                tool_results.append(structured_result)
            
            total_time = time.time() - start_time
            successful_count = sum(1 for r in tool_results if r.success)
            failed_count = len(tool_results) - successful_count
            
            # Create structured batch result
            batch_result = MCPBatchToolResult(
                tools_executed=tool_results,
                batch_success=failed_count == 0,
                total_execution_time=total_time,
                successful_tools=successful_count,
                failed_tools=failed_count
            )
            
            return Result(
                success=batch_result.batch_success,
                data=batch_result.model_dump(),
                metadata={
                    "method": "structured_batch_execution",
                    "total_tools": len(tool_results),
                    "execution_time": total_time
                }
            )
            
        except Exception as e:
            return Result(
                success=False,
                error=f"Structured batch execution failed: {str(e)}",
                metadata={
                    "execution_time": time.time() - start_time,
                    "error_type": type(e).__name__
                }
            )
    
    async def _execute_tool_batch_legacy(self, tools_and_params: List[Dict[str, Any]]) -> Result:
        """Legacy batch execution method."""
        results = []
        for tool_spec in tools_and_params:
            result = await self.call_tool(tool_spec["tool_name"], tool_spec.get("parameters", {}))
            results.append(result)
        
        return Result(
            success=all(r.success for r in results),
            data={"legacy_batch_results": results},
            metadata={"method": "legacy_batch_execution"}
        )

    async def cleanup(self) -> None:
        """Cleanup adapter resources."""
        self.tool_registry.clear()
        self._available_tools.clear()
        self.mcp_server = None
        self.server_manager = None
        self._initialized = False
        self._structured_llm_service = None
        self._structured_output_enabled = None
        self.logger.info("MCP adapter cleaned up")