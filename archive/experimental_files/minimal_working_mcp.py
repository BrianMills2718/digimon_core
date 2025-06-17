#!/usr/bin/env python3
"""
Minimal Working MCP Server - Using low-level API to avoid FastMCP issues
"""

import asyncio
import sys
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("super-digimon")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return [
        Tool(
            name="echo",
            description="Echo a message back",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to echo"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="test_connection",
            description="Test if MCP server is working",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    if name == "echo":
        message = arguments.get("message", "")
        return [TextContent(type="text", text=f"MCP Echo: {message}")]
    elif name == "test_connection":
        return [TextContent(type="text", text="✓ MCP Server is working and connected to Claude Code!")]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, {})

if __name__ == "__main__":
    asyncio.run(main())