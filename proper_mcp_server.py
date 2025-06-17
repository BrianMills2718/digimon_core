#!/usr/bin/env python3
"""
Proper MCP Server - Based on official FastMCP documentation
Following the official Python MCP SDK examples
"""

from mcp.server.fastmcp import FastMCP

# Create MCP server with a friendly name
mcp = FastMCP("Super-Digimon")

@mcp.tool()
def echo(message: str) -> str:
    """Echo a message back to test MCP functionality."""
    return f"Super-Digimon Echo: {message}"

@mcp.tool()
def test_connection() -> str:
    """Test if the MCP server is properly connected and working."""
    return "✅ Super-Digimon MCP Server is working perfectly! Connection verified."

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def get_server_info() -> dict:
    """Get information about this Super-Digimon MCP server."""
    return {
        "name": "Super-Digimon",
        "version": "1.0.0",
        "status": "operational",
        "tools_available": 4,
        "description": "GraphRAG system MCP server for Claude Code integration"
    }

# Resource example
@mcp.resource("status://server")
def get_server_status() -> str:
    """Get the current status of the Super-Digimon server."""
    return "Super-Digimon MCP Server is running and ready to handle requests."

if __name__ == "__main__":
    # Run the server using FastMCP's built-in runner
    mcp.run()