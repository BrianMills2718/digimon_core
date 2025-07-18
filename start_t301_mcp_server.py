#!/usr/bin/env python3
"""
Start the T301 MCP Server to expose fusion tools.
"""

from pathlib import Path

from src.tools.phase3.t301_multi_document_fusion import mcp

async def main():
    print("🚀 Starting T301 Multi-Document Fusion MCP Server")
    print("=" * 60)
    
    # List available tools
    print("\nAvailable MCP Tools:")
    tools = await mcp.get_tools()
    for tool_name, tool_info in tools.items():
        print(f"\n📌 {tool_name}")
        if isinstance(tool_info, dict) and 'description' in tool_info:
            desc_lines = tool_info['description'].strip().split('\n')
            print(f"   {desc_lines[0]}")
        if isinstance(tool_info, dict) and 'parameters' in tool_info:
            print("   Parameters:")
            for param_name, param_info in tool_info['parameters'].items():
                param_type = param_info.get('type', 'Any')
                print(f"     - {param_name}: {param_type}")
    
    print("\n" + "=" * 60)
    print("MCP Server is starting...")
    print("You can now connect to this server using an MCP client")
    print("=" * 60 + "\n")
    
    # Start the server
    await mcp.run_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())