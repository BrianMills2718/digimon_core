#!/usr/bin/env python3
"""
Simple FastMCP Server for Testing
"""

from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("simple-test")

@mcp.tool()
def test_connection() -> str:
    """Test MCP server connection."""
    return "✅ MCP Server Connected!"

@mcp.tool()
def echo(text: str) -> str:
    """Echo the input text."""
    return f"Echo: {text}"

if __name__ == "__main__":
    mcp.run()