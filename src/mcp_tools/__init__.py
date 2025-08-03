"""
MCP Tools Module

Decomposed MCP server components organized by service type.
Provides focused tool collections for FastMCP server registration.
"""

from .identity_tools import IdentityServiceTools
from .provenance_tools import ProvenanceServiceTools  
from .quality_tools import QualityServiceTools
from .workflow_tools import WorkflowServiceTools
from .pipeline_tools import PipelineTools
from .algorithm_tools import AlgorithmImplementationTools
from .server_manager import MCPServerManager
from .server_config import MCPServerConfig

__all__ = [
    # Service-specific tool collections
    "IdentityServiceTools",
    "ProvenanceServiceTools", 
    "QualityServiceTools",
    "WorkflowServiceTools",
    "PipelineTools",
    "AlgorithmImplementationTools",
    
    # Server management
    "MCPServerManager",
    "MCPServerConfig",
    
    # Helper functions
    "get_mcp_server_manager",
    "create_mcp_server"
]


# Singleton instance of server manager
_server_manager = None


def get_mcp_server_manager() -> MCPServerManager:
    """Get or create the singleton MCP server manager"""
    global _server_manager
    if _server_manager is None:
        _server_manager = MCPServerManager()
    return _server_manager


def create_mcp_server(server_name: str = "super-digimon"):
    """Create a new MCP server instance"""
    manager = MCPServerManager(server_name)
    manager.register_all_tools()
    return manager.get_server()