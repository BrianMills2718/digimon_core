#!/usr/bin/env python3
"""
Step 1A Test: Test basic MCP functionality
"""

import asyncio
import json
import sys
from mcp.server import Server
from mcp.types import Tool, TextContent

async def test_basic_mcp():
    """Test basic MCP server functionality."""
    print("=== Step 1A: Basic MCP Server Test ===")
    
    try:
        # Create server
        server = Server("test-server")
        print("✓ MCP Server created")
        
        # Test tool definition
        @server.list_tools()
        async def handle_list_tools():
            return [
                Tool(
                    name="test_tool",
                    description="Test tool",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"}
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        # Test tool execution
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            if name == "test_tool":
                return [TextContent(type="text", text=f"Echo: {arguments.get('message', '')}")]
            raise ValueError(f"Unknown tool: {name}")
        
        print("✓ Tool handlers registered")
        
        # Test tool listing
        tools = await handle_list_tools()
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
        print("✓ Tool listing works")
        
        # Test tool execution
        result = await handle_call_tool("test_tool", {"message": "hello"})
        assert len(result) == 1
        assert result[0].text == "Echo: hello"
        print("✓ Tool execution works")
        
        return True
        
    except Exception as e:
        print(f"✗ MCP test failed: {e}")
        return False

async def main():
    success = await test_basic_mcp()
    if success:
        print("\n✓ Step 1A: Basic MCP functionality verified")
        with open("step1A_verification.txt", "w") as f:
            f.write("PASS: Basic MCP functionality works\n")
            f.write(f"Date: {asyncio.get_event_loop().time()}\n")
    else:
        print("\n✗ Step 1A: MCP functionality failed")
        with open("step1A_verification.txt", "w") as f:
            f.write("FAIL: Basic MCP functionality failed\n")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())