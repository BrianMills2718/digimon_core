"""MCP server implementation for Super-Digimon."""

import logging
from typing import Dict, List, Any, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities

from .utils.config import Config
from .utils.database import DatabaseManager
from .tools import get_all_tools


logger = logging.getLogger(__name__)


async def run_server(config: Config):
    """Run the MCP server."""
    # Initialize server
    server = Server("super-digimon")
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    db_manager.initialize()
    
    # Check database health
    health = db_manager.health_check()
    logger.info(f"Database health: {health}")
    
    if not all(health.values()):
        logger.error("One or more databases are not healthy!")
        # Continue anyway for development
    
    # Get all tool implementations
    tools = get_all_tools(db_manager)
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """Return all available tools."""
        tool_definitions = []
        
        for tool_id, tool_impl in tools.items():
            tool_def = Tool(
                name=tool_id,
                description=tool_impl.description,
                inputSchema=tool_impl.get_schema()
            )
            tool_definitions.append(tool_def)
        
        logger.info(f"Listing {len(tool_definitions)} tools")
        return tool_definitions
    
    @server.call_tool()
    async def handle_call_tool(
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> List[TextContent]:
        """Execute a tool."""
        logger.info(f"Calling tool: {name} with args: {arguments}")
        
        if name not in tools:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        
        try:
            tool = tools[name]
            result = await tool.execute(arguments or {})
            
            # Format result as text
            if isinstance(result, dict):
                if "error" in result:
                    return [TextContent(type="text", text=f"Error: {result['error']}")]
                else:
                    # Pretty format the result
                    import json
                    text = json.dumps(result, indent=2)
                    return [TextContent(type="text", text=text)]
            else:
                return [TextContent(type="text", text=str(result))]
                
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [TextContent(type="text", text=error_msg)]
    
    # Define server capabilities
    server_capabilities = ServerCapabilities(
        tools=InitializationOptions(
            listChanged=True
        )
    )
    
    # Run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP server started on stdio")
        await server.run(
            read_stream,
            write_stream,
            server_capabilities
        )
    
    # Cleanup
    db_manager.close()
    logger.info("MCP server stopped")