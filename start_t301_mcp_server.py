#!/usr/bin/env python3
"""
Start the T301 MCP Server to expose fusion tools.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.phase3.t301_multi_document_fusion_tools import mcp

if __name__ == "__main__":
    print("🚀 Starting T301 Multi-Document Fusion MCP Server")
    print("=" * 60)
    
    # List available tools
    print("\nAvailable MCP Tools:")
    for tool_name, tool in mcp.tools.items():
        print(f"\n📌 {tool_name}")
        if hasattr(tool, 'description') and tool.description:
            # First line of description
            desc_lines = tool.description.strip().split('\n')
            print(f"   {desc_lines[0]}")
        if hasattr(tool, 'parameters') and tool.parameters:
            print("   Parameters:")
            for param_name, param_info in tool.parameters.items():
                required = param_info.get('required', False)
                param_type = param_info.get('type', 'Any')
                default = param_info.get('default', 'N/A')
                print(f"     - {param_name}: {param_type} {'(required)' if required else f'(default: {default})'}")
    
    print("\n" + "=" * 60)
    print("MCP Server is starting...")
    print("You can now connect to this server using an MCP client")
    print("=" * 60 + "\n")
    
    # Start the server
    mcp.run()