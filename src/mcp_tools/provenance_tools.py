"""
Provenance Service MCP Tools

T110: Provenance Service tools for operation tracking and lineage.
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from .server_config import get_mcp_config

logger = logging.getLogger(__name__)


class ProvenanceServiceTools:
    """Collection of Provenance Service tools for MCP server"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_mcp_config()
    
    @property
    def provenance_service(self):
        """Get provenance service instance"""
        return self.config.provenance_service
    
    def register_tools(self, mcp: FastMCP):
        """Register all provenance service tools with MCP server"""
        
        @mcp.tool()
        def start_operation(
            tool_id: str,
            operation_type: str,
            inputs: List[str],
            parameters: Dict[str, Any] = None
        ) -> str:
            """Start tracking a new operation.
            
            Args:
                tool_id: Identifier of the tool performing operation
                operation_type: Type of operation (create, update, delete, query)
                inputs: List of input object references
                parameters: Tool parameters
            """
            try:
                if not self.provenance_service:
                    return "error_service_unavailable"
                
                return self.provenance_service.start_operation(
                    tool_id=tool_id,
                    operation_type=operation_type,
                    inputs=inputs,
                    parameters=parameters or {}
                )
            except Exception as e:
                self.logger.error(f"Error starting operation: {e}")
                return f"error_{str(e)}"
        
        @mcp.tool()
        def complete_operation(
            operation_id: str,
            outputs: List[str],
            status: str = "success",
            metadata: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Complete an operation and record results.
            
            Args:
                operation_id: ID returned from start_operation
                outputs: List of output object references
                status: Operation status (success, failure, partial)
                metadata: Additional operation metadata
            """
            try:
                if not self.provenance_service:
                    return {"error": "Provenance service not available"}
                
                return self.provenance_service.complete_operation(
                    operation_id=operation_id,
                    outputs=outputs,
                    status=status,
                    metadata=metadata or {}
                )
            except Exception as e:
                self.logger.error(f"Error completing operation: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_lineage(object_ref: str, max_depth: int = 10) -> Dict[str, Any]:
            """Get lineage graph for an object.
            
            Args:
                object_ref: Reference to the object
                max_depth: Maximum traversal depth
            """
            try:
                if not self.provenance_service:
                    return {"error": "Provenance service not available"}
                
                return self.provenance_service.get_lineage(object_ref, max_depth)
            except Exception as e:
                self.logger.error(f"Error getting lineage: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_operation_details(operation_id: str) -> Optional[Dict[str, Any]]:
            """Get details of a specific operation.
            
            Args:
                operation_id: ID of the operation
            """
            try:
                if not self.provenance_service:
                    return {"error": "Provenance service not available"}
                
                return self.provenance_service.get_operation_details(operation_id)
            except Exception as e:
                self.logger.error(f"Error getting operation details: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_operations_for_object(object_ref: str) -> List[Dict[str, Any]]:
            """Get all operations that involved a specific object.
            
            Args:
                object_ref: Reference to the object
            """
            try:
                if not self.provenance_service:
                    return [{"error": "Provenance service not available"}]
                
                return self.provenance_service.get_operations_for_object(object_ref)
            except Exception as e:
                self.logger.error(f"Error getting operations for object: {e}")
                return [{"error": str(e)}]
        
        @mcp.tool()
        def get_tool_statistics() -> Dict[str, Any]:
            """Get provenance tracking statistics."""
            try:
                if not self.provenance_service:
                    return {"error": "Provenance service not available"}
                
                return self.provenance_service.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting tool statistics: {e}")
                return {"error": str(e)}
        
        self.logger.info("Provenance service tools registered successfully")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about provenance service tools"""
        return {
            "service": "T110_Provenance_Service",
            "tool_count": 6,
            "tools": [
                "start_operation",
                "complete_operation",
                "get_lineage",
                "get_operation_details",
                "get_operations_for_object", 
                "get_tool_statistics"
            ],
            "description": "Operation tracking and lineage management tools",
            "capabilities": [
                "operation_tracking",
                "lineage_tracing",
                "operation_completion",
                "metadata_recording",
                "statistics_reporting"
            ],
            "service_available": self.provenance_service is not None
        }