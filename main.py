#!/usr/bin/env python3
"""Super-Digimon MCP Server Entry Point

Main entry point for the Super-Digimon GraphRAG MCP server.
This server provides the foundation for the 121-tool system with
core services for identity, provenance, quality, and workflow management.
"""

import os
from pathlib import Path

# Import configuration system
from config.config_loader import get_settings

# Import and run the MCP server (using proper package imports)
from src.mcp_server import mcp

if __name__ == "__main__":
    # Load configuration
    settings = get_settings()
    
    # Set up environment with configuration
    os.environ.setdefault("WORKFLOW_STORAGE_DIR", "./data/workflows")
    
    # Apply configuration settings
    if settings.database_url:
        os.environ["NEO4J_URL"] = settings.database_url
    
    # Set logging level
    os.environ["LOG_LEVEL"] = settings.log_level
    
    # Ensure data directory exists
    Path("./data").mkdir(exist_ok=True)
    Path("./data/workflows").mkdir(exist_ok=True)
    
    print("🚀 Starting Super-Digimon MCP Server...")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔗 Database: {settings.database_url}")
    print(f"🤖 LLM Provider: {settings.llm_provider}")
    print("📊 Core services: Identity, Provenance, Quality, Workflow State")
    print("🔗 Ready for vertical slice implementation")
    
    # Run the server
    mcp.run()