"""
MCP Server Manager

Main orchestration component for the FastMCP server with all tools.
"""

import logging
from typing import Dict, Any
from fastmcp import FastMCP

from .server_config import get_mcp_config
from .identity_tools import IdentityServiceTools
from .provenance_tools import ProvenanceServiceTools
from .quality_tools import QualityServiceTools
from .workflow_tools import WorkflowServiceTools
from .pipeline_tools import PipelineTools
from .algorithm_tools import AlgorithmImplementationTools

logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manage the complete MCP server with all tool collections"""
    
    def __init__(self, server_name: str = "super-digimon"):
        self.server_name = server_name
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize FastMCP server
        self.mcp = FastMCP(server_name)
        
        # Initialize configuration
        self.config = get_mcp_config()
        
        # Initialize tool collections
        self.identity_tools = IdentityServiceTools()
        self.provenance_tools = ProvenanceServiceTools()
        self.quality_tools = QualityServiceTools()
        self.workflow_tools = WorkflowServiceTools()
        self.pipeline_tools = PipelineTools()
        self.algorithm_tools = AlgorithmImplementationTools()
        
        # Registration state
        self._tools_registered = False
    
    def register_all_tools(self):
        """Register all tool collections with the MCP server"""
        try:
            if self._tools_registered:
                self.logger.warning("Tools already registered")
                return
            
            # Register service-specific tools
            self.identity_tools.register_tools(self.mcp)
            self.provenance_tools.register_tools(self.mcp)
            self.quality_tools.register_tools(self.mcp)
            self.workflow_tools.register_tools(self.mcp)
            self.pipeline_tools.register_tools(self.mcp)
            self.algorithm_tools.register_tools(self.mcp)
            
            # Register server management tools
            self._register_server_tools()
            
            self._tools_registered = True
            self.logger.info("All MCP tools registered successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to register tools: {e}")
            raise
    
    def _register_server_tools(self):
        """Register server management and utility tools"""
        
        @self.mcp.tool()
        def test_connection() -> str:
            """Test MCP server connection."""
            return "MCP server connection successful"
        
        @self.mcp.tool()
        def echo(message: str) -> str:
            """Echo a message back (for testing)."""
            return f"Echo: {message}"
        
        @self.mcp.tool()
        def get_system_status() -> Dict[str, Any]:
            """Get comprehensive system status."""
            try:
                server_info = self.config.get_server_info()
                health_status = self.config.health_check()
                
                # Get tool collection info
                tool_collections = {
                    "identity_tools": self.identity_tools.get_tool_info(),
                    "provenance_tools": self.provenance_tools.get_tool_info(),
                    "quality_tools": self.quality_tools.get_tool_info(),
                    "workflow_tools": self.workflow_tools.get_tool_info(),
                    "pipeline_tools": self.pipeline_tools.get_tool_info(),
                    "algorithm_tools": self.algorithm_tools.get_tool_info()
                }
                
                total_tools = sum(info.get("tool_count", 0) for info in tool_collections.values())
                total_tools += 3  # Server management tools
                
                return {
                    "server_info": server_info,
                    "health_status": health_status,
                    "tool_collections": tool_collections,
                    "total_tools": total_tools,
                    "tools_registered": self._tools_registered,
                    "status": "operational" if health_status.get("overall_status") == "healthy" else "degraded"
                }
                
            except Exception as e:
                self.logger.error(f"Error getting system status: {e}")
                return {
                    "error": str(e),
                    "status": "error",
                    "server_name": self.server_name
                }
        
        self.logger.info("Server management tools registered")
    
    def get_server(self) -> FastMCP:
        """Get the configured FastMCP server instance"""
        if not self._tools_registered:
            self.register_all_tools()
        return self.mcp
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information"""
        return {
            "server_name": self.server_name,
            "architecture": "decomposed_mcp_tools",
            "tools_registered": self._tools_registered,
            "configuration": self.config.get_server_info(),
            "tool_collections": {
                "identity_tools": self.identity_tools.get_tool_info(),
                "provenance_tools": self.provenance_tools.get_tool_info(),
                "quality_tools": self.quality_tools.get_tool_info(),
                "workflow_tools": self.workflow_tools.get_tool_info(),
                "pipeline_tools": self.pipeline_tools.get_tool_info(),
                "algorithm_tools": self.algorithm_tools.get_tool_info()
            },
            "total_tools": (
                self.identity_tools.get_tool_info().get("tool_count", 0) +
                self.provenance_tools.get_tool_info().get("tool_count", 0) +
                self.quality_tools.get_tool_info().get("tool_count", 0) +
                self.workflow_tools.get_tool_info().get("tool_count", 0) +
                self.pipeline_tools.get_tool_info().get("tool_count", 0) +
                self.algorithm_tools.get_tool_info().get("tool_count", 0) +
                3  # Server management tools
            )
        }
    
    def run_server(self, host: str = "localhost", port: int = 8000):
        """Run the MCP server"""
        try:
            if not self._tools_registered:
                self.register_all_tools()
            
            self.logger.info(f"Starting MCP server '{self.server_name}' on {host}:{port}")
            self.mcp.run(host=host, port=port)
            
        except Exception as e:
            self.logger.error(f"Failed to run MCP server: {e}")
            raise


# Global server manager instance
_global_server_manager = None


def get_mcp_server_manager() -> MCPServerManager:
    """Get or create global MCP server manager"""
    global _global_server_manager
    if _global_server_manager is None:
        _global_server_manager = MCPServerManager()
    return _global_server_manager


def create_mcp_server(server_name: str = "super-digimon") -> FastMCP:
    """Create and configure MCP server with all tools"""
    manager = MCPServerManager(server_name)
    return manager.get_server()