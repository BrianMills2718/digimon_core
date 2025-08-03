"""
Identity Service Adapter for Dependency Injection

Adapts the existing IdentityService to work with the dependency injection framework
while maintaining backward compatibility.
"""

import logging
from typing import Dict, Any, Optional
import asyncio

from ..interfaces.service_interfaces import IdentityServiceInterface, ServiceResponse
from ..identity_service import IdentityService as ExistingIdentityService

logger = logging.getLogger(__name__)


class IdentityServiceAdapter(IdentityServiceInterface):
    """
    Adapter that wraps the existing IdentityService to implement the standard interface
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the identity service adapter
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}
        self._service: Optional[ExistingIdentityService] = None
        self._initialized = False
        
        # Initialize the underlying service
        try:
            # Pass configuration to existing service
            service_config = self._config.get('identity', {})
            self._service = ExistingIdentityService(**service_config)
            logger.info("IdentityServiceAdapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize IdentityService: {e}")
            raise
    
    async def startup(self) -> None:
        """Initialize service and establish connections"""
        if self._initialized:
            return
        
        try:
            # Initialize underlying service if it has startup method
            if hasattr(self._service, 'startup') and callable(self._service.startup):
                if asyncio.iscoroutinefunction(self._service.startup):
                    await self._service.startup()
                else:
                    self._service.startup()
            
            self._initialized = True
            logger.info("IdentityServiceAdapter started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start IdentityServiceAdapter: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Cleanup resources and close connections"""
        if not self._initialized:
            return
        
        try:
            # Shutdown underlying service if it has shutdown method
            if hasattr(self._service, 'shutdown') and callable(self._service.shutdown):
                if asyncio.iscoroutinefunction(self._service.shutdown):
                    await self._service.shutdown()
                else:
                    self._service.shutdown()
            
            self._initialized = False
            logger.info("IdentityServiceAdapter shut down successfully")
            
        except Exception as e:
            logger.error(f"Error shutting down IdentityServiceAdapter: {e}")
    
    async def health_check(self) -> ServiceResponse:
        """Check service health and return status"""
        try:
            if not self._service:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error="Service not initialized",
                    metadata={"service": "identity"}
                )
            
            # Check if underlying service has health check
            if hasattr(self._service, 'health_check'):
                health_result = self._service.health_check()
                if hasattr(health_result, 'success'):
                    # Already a ServiceResponse
                    return health_result
                else:
                    # Convert to ServiceResponse
                    return ServiceResponse(
                        success=True,
                        data=health_result,
                        metadata={"service": "identity"}
                    )
            
            # Basic health check - verify service is operational
            return ServiceResponse(
                success=self._initialized,
                data={"status": "healthy" if self._initialized else "not_initialized"},
                metadata={"service": "identity", "initialized": self._initialized}
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ServiceResponse(
                success=False,
                data=None,
                error=str(e),
                metadata={"service": "identity"}
            )
    
    async def create_mention(self, surface_form: str, context: str = None, 
                           confidence: float = None, **kwargs) -> ServiceResponse:
        """Create a new entity mention"""
        try:
            if not self._service:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error="Service not initialized",
                    metadata={"operation": "create_mention"}
                )
            
            # Call the existing service method
            result = self._service.create_mention(
                surface_form=surface_form,
                start_pos=kwargs.get('start_pos', 0),
                end_pos=kwargs.get('end_pos', len(surface_form)),
                source_ref=kwargs.get('source_ref', 'unknown'),
                entity_type=kwargs.get('entity_type'),
                confidence=confidence or 0.8
            )
            
            return ServiceResponse(
                success=True,
                data=result,
                metadata={
                    "operation": "create_mention",
                    "surface_form": surface_form,
                    "confidence": confidence
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create mention: {e}")
            return ServiceResponse(
                success=False,
                data=None,
                error=str(e),
                metadata={"operation": "create_mention"}
            )
    
    async def resolve_entity(self, mention_id: str) -> ServiceResponse:
        """Resolve a mention to a canonical entity"""
        try:
            if not self._service:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error="Service not initialized",
                    metadata={"operation": "resolve_entity"}
                )
            
            # Get mention by ID and resolve to entity
            mention = self._service.get_mention_by_id(mention_id)
            if mention:
                entity = self._service.get_entity_by_mention(mention_id)
                return ServiceResponse(
                    success=True,
                    data=entity,
                    metadata={
                        "operation": "resolve_entity",
                        "mention_id": mention_id
                    }
                )
            else:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error=f"Mention not found: {mention_id}",
                    metadata={"operation": "resolve_entity"}
                )
                
        except Exception as e:
            logger.error(f"Failed to resolve entity: {e}")
            return ServiceResponse(
                success=False,
                data=None,
                error=str(e),
                metadata={"operation": "resolve_entity"}
            )
    
    async def get_entity_by_id(self, entity_id: str) -> ServiceResponse:
        """Get entity by canonical ID"""
        try:
            if not self._service:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error="Service not initialized",
                    metadata={"operation": "get_entity_by_id"}
                )
            
            # Use existing service method
            entity = self._service.get_entity_by_id(entity_id)
            
            return ServiceResponse(
                success=entity is not None,
                data=entity,
                error=None if entity else f"Entity not found: {entity_id}",
                metadata={
                    "operation": "get_entity_by_id",
                    "entity_id": entity_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get entity: {e}")
            return ServiceResponse(
                success=False,
                data=None,
                error=str(e),
                metadata={"operation": "get_entity_by_id"}
            )
    
    async def search_entities(self, query: str, limit: int = 10) -> ServiceResponse:
        """Search for entities by text query"""
        try:
            if not self._service:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error="Service not initialized",
                    metadata={"operation": "search_entities"}
                )
            
            # Use existing service search if available
            if hasattr(self._service, 'search_entities'):
                results = self._service.search_entities(query, limit)
            else:
                # Fallback to basic entity listing
                results = []
                logger.warning("search_entities not implemented in underlying service")
            
            return ServiceResponse(
                success=True,
                data=results,
                metadata={
                    "operation": "search_entities",
                    "query": query,
                    "limit": limit,
                    "result_count": len(results) if results else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            return ServiceResponse(
                success=False,
                data=None,
                error=str(e),
                metadata={"operation": "search_entities"}
            )
    
    async def link_entities(self, entity1_id: str, entity2_id: str, 
                          relationship_type: str) -> ServiceResponse:
        """Create a relationship between two entities"""
        try:
            if not self._service:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error="Service not initialized",
                    metadata={"operation": "link_entities"}
                )
            
            # Use existing service method if available
            if hasattr(self._service, 'create_relationship'):
                result = self._service.create_relationship(
                    entity1_id, entity2_id, relationship_type
                )
            else:
                # Log that this functionality isn't available
                logger.warning("link_entities not implemented in underlying service")
                result = {
                    "entity1_id": entity1_id,
                    "entity2_id": entity2_id,
                    "relationship_type": relationship_type,
                    "status": "not_implemented"
                }
            
            return ServiceResponse(
                success=True,
                data=result,
                metadata={
                    "operation": "link_entities",
                    "entity1_id": entity1_id,
                    "entity2_id": entity2_id,
                    "relationship_type": relationship_type
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to link entities: {e}")
            return ServiceResponse(
                success=False,
                data=None,
                error=str(e),
                metadata={"operation": "link_entities"}
            )
    
    # Additional methods for backward compatibility
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        if hasattr(self._service, 'get_service_stats'):
            return self._service.get_service_stats()
        
        return {
            "initialized": self._initialized,
            "service_type": "identity",
            "adapter_version": "1.0"
        }