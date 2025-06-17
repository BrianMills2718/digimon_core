#!/usr/bin/env python3
"""
Super-Digimon MCP Server - Step 1A: Minimal Implementation
Goal: Basic MCP server that starts and responds to basic requests
"""

import asyncio
import json
import logging
import sys
from typing import List, Dict, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create server instance
server = Server("super-digimon")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Return list of available tools."""
    logger.info("Tools list requested")
    return [
        Tool(
            name="echo_test",
            description="Test tool that echoes input - for Step 1A verification",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool execution."""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    if name == "echo_test":
        message = arguments.get("message", "")
        response = f"Echo: {message}"
        logger.info(f"Echo response: {response}")
        return [TextContent(
            type="text",
            text=response
        )]
    else:
        error_msg = f"Unknown tool: {name}"
        logger.error(error_msg)
        raise ValueError(error_msg)

async def main():
    """Run the MCP server."""
    logger.info("Starting Super-Digimon MCP Server (Step 1A)...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server initialized successfully - ready for requests")
            await server.run(read_stream, write_stream)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user - shutting down gracefully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())