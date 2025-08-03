"""
Super-Digimon MCP Server - Main Interface

Streamlined MCP server interface using decomposed components.
Reduced from 917 lines to focused interface.

Main MCP server exposing the core services as tools.
Provides the foundation for the 121-tool GraphRAG system.

Currently implements:
- T107: Identity Service tools
- T110: Provenance Service tools  
- T111: Quality Service tools
- T121: Workflow State Service tools
- Pipeline orchestration tools
"""

import logging
from typing import Dict, Any

from src.mcp_tools import (
    MCPServerManager, get_mcp_server_manager, create_mcp_server
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server"""
    try:
        # Create and configure server manager
        server_manager = get_mcp_server_manager()
        
        # Register all tools
        server_manager.register_all_tools()
        
        # Get server info
        server_info = server_manager.get_server_info()
        logger.info(f"✅ MCP Server initialized with {server_info['total_tools']} tools")
        
        # Print tool collection summary
        for collection_name, collection_info in server_info['tool_collections'].items():
            service_name = collection_info.get('service', collection_name)
            tool_count = collection_info.get('tool_count', 0)
            service_available = collection_info.get('service_available', False)
            status = "✅" if service_available else "⚠️"
            logger.info(f"{status} {service_name}: {tool_count} tools")
        
        # Run the server
        logger.info("Starting MCP server...")
        server_manager.run_server()
        
    except KeyboardInterrupt:
        logger.info("MCP server shutdown requested")
    except Exception as e:
        logger.error(f"MCP server failed: {e}")
        raise


def get_mcp_server():
    """Get configured MCP server instance for external use"""
    return create_mcp_server()


def get_server_status() -> Dict[str, Any]:
    """Get comprehensive server status"""
    try:
        server_manager = get_mcp_server_manager()
        return {
            "server_info": server_manager.get_server_info(),
            "health_status": server_manager.config.health_check(),
            "architecture": "decomposed_components",
            "version": "2.0.0"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


# Legacy compatibility: Initialize global server instance
try:
    # Initialize the FastMCP instance for backward compatibility
    mcp = create_mcp_server("super-digimon")
    logger.info("✅ MCP server instance created with decomposed architecture")
except Exception as e:
    logger.warning(f"Could not initialize backward compatibility MCP instance: {e}")
    mcp = None


# Export main classes and functions
__all__ = [
    "main",
    "get_mcp_server", 
    "get_server_status",
    "mcp"  # Backward compatibility
]


if __name__ == "__main__":
    main()