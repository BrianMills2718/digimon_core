"""
Identity Service MCP Tools

T107: Identity Service tools for entity mention management and resolution.
"""

import logging
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from .server_config import get_mcp_config

logger = logging.getLogger(__name__)


class IdentityServiceTools:
    """Collection of Identity Service tools for MCP server"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_mcp_config()
    
    @property
    def identity_service(self):
        """Get identity service instance"""
        return self.config.identity_service
    
    def register_tools(self, mcp: FastMCP):
        """Register all identity service tools with MCP server"""
        
        @mcp.tool()
        def create_mention(
            surface_form: str,
            start_pos: int,
            end_pos: int,
            source_ref: str,
            entity_type: str = None,
            confidence: float = 0.8
        ) -> Dict[str, Any]:
            """Create a new mention and link to entity.
            
            Args:
                surface_form: Exact text as it appears
                start_pos: Start character position  
                end_pos: End character position
                source_ref: Reference to source document
                entity_type: Optional entity type hint
                confidence: Confidence score (0.0-1.0)
            """
            try:
                if not self.identity_service:
                    return {"error": "Identity service not available"}
                
                return self.identity_service.create_mention(
                    surface_form=surface_form,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    source_ref=source_ref,
                    entity_type=entity_type,
                    confidence=confidence
                )
            except Exception as e:
                self.logger.error(f"Error creating mention: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_entity_by_mention(mention_id: str) -> Optional[Dict[str, Any]]:
            """Get entity associated with a mention.
            
            Args:
                mention_id: ID of the mention
            """
            try:
                if not self.identity_service:
                    return {"error": "Identity service not available"}
                
                return self.identity_service.get_entity_by_mention(mention_id)
            except Exception as e:
                self.logger.error(f"Error getting entity by mention: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_mentions_for_entity(entity_id: str) -> List[Dict[str, Any]]:
            """Get all mentions for an entity.
            
            Args:
                entity_id: ID of the entity
            """
            try:
                if not self.identity_service:
                    return [{"error": "Identity service not available"}]
                
                return self.identity_service.get_mentions_for_entity(entity_id)
            except Exception as e:
                self.logger.error(f"Error getting mentions for entity: {e}")
                return [{"error": str(e)}]
        
        @mcp.tool()
        def merge_entities(entity_id1: str, entity_id2: str) -> Dict[str, Any]:
            """Merge two entities (keeping the first one).
            
            Args:
                entity_id1: ID of entity to keep
                entity_id2: ID of entity to merge into first
            """
            try:
                if not self.identity_service:
                    return {"error": "Identity service not available"}
                
                return self.identity_service.merge_entities(entity_id1, entity_id2)
            except Exception as e:
                self.logger.error(f"Error merging entities: {e}")
                return {"error": str(e)}
        
        @mcp.tool()
        def get_identity_stats() -> Dict[str, Any]:
            """Get identity service statistics."""
            try:
                if not self.identity_service:
                    return {"error": "Identity service not available"}
                
                return self.identity_service.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting identity stats: {e}")
                return {"error": str(e)}
        
        self.logger.info("Identity service tools registered successfully")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about identity service tools"""
        return {
            "service": "T107_Identity_Service",
            "tool_count": 5,
            "tools": [
                "create_mention",
                "get_entity_by_mention", 
                "get_mentions_for_entity",
                "merge_entities",
                "get_identity_stats"
            ],
            "description": "Entity mention management and resolution tools",
            "capabilities": [
                "mention_creation",
                "entity_linking",
                "mention_retrieval",
                "entity_merging",
                "statistics_reporting"
            ],
            "service_available": self.identity_service is not None
        }