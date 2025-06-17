#!/usr/bin/env python3
"""
Simple FastMCP Server
"""

from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("super-digimon")

@mcp.tool()
def echo(message: str) -> str:
    """Echo back a message."""
    return f"✓ FastMCP Echo: {message}"

@mcp.tool() 
def test_connection() -> str:
    """Test MCP server connection."""
    return "✅ FastMCP Server Connected!"

if __name__ == "__main__":
    mcp.run()