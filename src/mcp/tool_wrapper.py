"""
MCP Tool Wrapper - Wraps existing tools for MCP protocol compatibility
"""
import asyncio
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

from ..core.base_tool import BaseTool, ToolRequest, ToolResult

logger = logging.getLogger(__name__)

@dataclass
class MCPToolCall:
    """Represents an MCP tool call"""
    tool_id: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None

@dataclass 
class MCPToolResponse:
    """Represents an MCP tool response"""
    call_id: Optional[str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    is_error: bool = False

class MCPToolWrapper:
    """Wraps KGAS tools for MCP protocol compatibility"""
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        
    async def handle_tool_call(self, call: MCPToolCall) -> MCPToolResponse:
        """Handle an MCP tool call"""
        try:
            # Validate tool exists
            if call.tool_id not in self.tool_registry.tools:
                return MCPToolResponse(
                    call_id=call.call_id,
                    error=f"Tool {call.tool_id} not found",
                    is_error=True
                )
            
            # Execute the tool
            result = await self.tool_registry.call_tool(call.tool_id, call.arguments)
            
            # Convert ToolResult to MCP response
            if result.status == "success":
                return MCPToolResponse(
                    call_id=call.call_id,
                    result={
                        "status": result.status,
                        "data": result.data,
                        "metadata": result.metadata
                    }
                )
            else:
                return MCPToolResponse(
                    call_id=call.call_id,
                    error=result.error_message or "Tool execution failed",
                    is_error=True
                )
                
        except Exception as e:
            logger.error(f"Error handling tool call {call.tool_id}: {e}")
            return MCPToolResponse(
                call_id=call.call_id,
                error=f"Internal error: {str(e)}",
                is_error=True
            )
    
    async def handle_batch_tool_calls(self, calls: list[MCPToolCall]) -> list[MCPToolResponse]:
        """Handle multiple tool calls, potentially in parallel"""
        if not calls:
            return []
        
        # Execute all calls concurrently
        tasks = [self.handle_tool_call(call) for call in calls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses and handle exceptions
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                processed_responses.append(MCPToolResponse(
                    call_id=calls[i].call_id,
                    error=f"Exception during execution: {str(response)}",
                    is_error=True
                ))
            else:
                processed_responses.append(response)
        
        return processed_responses
    
    def get_tool_schema(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get MCP schema for a specific tool"""
        registration = self.tool_registry.get_tool(tool_id)
        if not registration:
            return None
        
        return {
            "name": tool_id,
            "description": registration.description,
            "inputSchema": registration.input_schema,
            "outputSchema": registration.output_schema
        }
    
    def get_all_tool_schemas(self) -> Dict[str, Any]:
        """Get MCP schemas for all tools"""
        return self.tool_registry.get_tool_manifest()

class MCPCompatibilityLayer:
    """Provides MCP protocol compatibility for KGAS tools"""
    
    def __init__(self, service_manager):
        from .tool_registry import MCPToolRegistry
        
        self.tool_registry = MCPToolRegistry(service_manager)
        self.tool_wrapper = MCPToolWrapper(self.tool_registry)
        
    async def list_tools(self) -> Dict[str, Any]:
        """MCP: List available tools"""
        return self.tool_wrapper.get_all_tool_schemas()
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP: Call a specific tool"""
        call = MCPToolCall(tool_id=name, arguments=arguments)
        response = await self.tool_wrapper.handle_tool_call(call)
        
        if response.is_error:
            return {
                "isError": True,
                "content": [{"type": "text", "text": response.error}]
            }
        else:
            return {
                "content": [{"type": "text", "text": str(response.result)}]
            }
    
    async def batch_call_tools(self, calls: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """MCP: Call multiple tools in batch"""
        mcp_calls = []
        for i, call_data in enumerate(calls):
            mcp_call = MCPToolCall(
                tool_id=call_data.get('name'),
                arguments=call_data.get('arguments', {}),
                call_id=str(i)
            )
            mcp_calls.append(mcp_call)
        
        responses = await self.tool_wrapper.handle_batch_tool_calls(mcp_calls)
        
        # Convert to MCP format
        mcp_responses = []
        for response in responses:
            if response.is_error:
                mcp_responses.append({
                    "isError": True,
                    "content": [{"type": "text", "text": response.error}]
                })
            else:
                mcp_responses.append({
                    "content": [{"type": "text", "text": str(response.result)}]
                })
        
        return mcp_responses
    
    def get_capabilities(self) -> Dict[str, Any]:
        """MCP: Get server capabilities"""
        return {
            "tools": {
                "listChanged": False,
                "supportsProgress": True
            },
            "resources": {
                "listChanged": False
            },
            "prompts": {
                "listChanged": False
            },
            "experimental": {
                "batch_tool_calls": True,
                "tool_discovery": True
            }
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """MCP: Get server information"""
        stats = self.tool_registry.get_registry_stats()
        
        return {
            "name": "KGAS MCP Server",
            "version": "1.0.0",
            "protocol_version": "1.0.0",
            "capabilities": self.get_capabilities(),
            "server_stats": stats
        }