#!/usr/bin/env python3
"""
Step 1B: Simple MCP Server for Claude Code Integration
Goal: MCP server that Claude Code can actually connect to
"""

import asyncio
import logging
import sys
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure minimal logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for Claude Code
logger = logging.getLogger(__name__)

# Create server
server = Server("super-digimon")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Return available tools."""
    return [
        Tool(
            name="echo_test",
            description="Echo a message back - Step 1B verification tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "Message to echo"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="status_check",
            description="Check server status - Step 1B verification tool",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Execute tools."""
    if name == "echo_test":
        message = arguments.get("message", "")
        return [TextContent(
            type="text",
            text=f"Super-Digimon Echo: {message}"
        )]
    elif name == "status_check":
        return [TextContent(
            type="text", 
            text="✓ Super-Digimon MCP Server is running (Step 1B verified)"
        )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run MCP server for Claude Code."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())