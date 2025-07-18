#!/usr/bin/env python3
"""Super-Digimon MCP Server Entry Point

Main entry point for the Super-Digimon GraphRAG MCP server.
This server provides the foundation for the 121-tool system with
core services for identity, provenance, quality, and workflow management.
"""

import os
from pathlib import Path

# Import and run the MCP server (using proper package imports)
from src.mcp_server import mcp

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("WORKFLOW_STORAGE_DIR", "./data/workflows")
    
    # Ensure data directory exists
    Path("./data").mkdir(exist_ok=True)
    Path("./data/workflows").mkdir(exist_ok=True)
    
    print("🚀 Starting Super-Digimon MCP Server...")
    print("📊 Core services: Identity, Provenance, Quality, Workflow State")
    print("🔗 Ready for vertical slice implementation")
    
    # Run the server
    mcp.run()