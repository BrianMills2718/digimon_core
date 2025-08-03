"""
Identity Service - Main Interface

Streamlined identity service interface using decomposed components.
Reduced from 905 lines to focused interface.

Implements consolidated identity service with:
- Entity mention management and resolution
- Optional semantic similarity using embeddings  
- Optional persistence support with PII vault
- Backward compatible with existing code
"""

import logging
from typing import Dict, Any

# Import main service from decomposed module
from .identity_management import (
    IdentityService as IdentityServiceImpl,
    Mention, Entity, Relationship
)

logger = logging.getLogger(__name__)


class IdentityService(IdentityServiceImpl):
    """
    Main identity service interface that extends the decomposed implementation.
    
    Uses decomposed components for maintainability:
    - MentionProcessor: Mention creation, validation, normalization
    - EntityResolver: Entity matching using exact and semantic similarity  
    - EmbeddingService: Optional semantic embeddings for similarity
    - PersistenceLayer: Optional SQLite database with PII vault
    - DatabaseManager: Low-level database operations
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize identity service with decomposed architecture"""
        super().__init__(*args, **kwargs)
        
        # Log initialization with component status
        components_status = {
            "mention_processor": "initialized",
            "entity_resolver": "initialized", 
            "embedding_service": "enabled" if self.embedding_service else "disabled",
            "persistence_layer": "enabled" if self.persistence.is_enabled() else "disabled",
            "pii_service": "enabled" if self._pii_service else "disabled"
        }
        
        logger.info(f"Identity service initialized with components: {components_status}")
    
    # ServiceProtocol Implementation
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize service with configuration (ServiceProtocol implementation)"""
        try:
            # The service is already initialized in __init__, this is for DI container compatibility
            logger.info(f"IdentityService.initialize called with config: {list(config.keys())}")
            
            # Apply any additional configuration if provided
            if config:
                # Update configuration if needed
                logger.debug(f"Applying additional configuration: {config}")
            
            # Verify service is properly initialized
            if hasattr(self, 'mention_processor') and hasattr(self, 'entity_resolver'):
                logger.info("IdentityService initialization verified - all components ready")
                return True
            else:
                logger.error("IdentityService initialization failed - missing components")
                return False
                
        except Exception as e:
            logger.error(f"IdentityService initialization failed: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if service is healthy (ServiceProtocol implementation)"""
        try:
            # Check if core components are available
            if not hasattr(self, 'mention_processor') or not hasattr(self, 'entity_resolver'):
                logger.warning("IdentityService health check failed - missing core components")
                return False
            
            # Check if persistence layer is healthy (if enabled)
            if hasattr(self, 'persistence') and self.persistence.is_enabled():
                if not self.persistence.health_check():
                    logger.warning("IdentityService health check failed - persistence layer unhealthy")
                    return False
            
            # Basic functionality test - try to create a simple mention
            try:
                test_mention = self.create_mention(
                    surface_form="test_entity",
                    start_pos=0,
                    end_pos=4,
                    source_ref="health_check"
                )
                if test_mention and 'mention_id' in test_mention:
                    logger.debug("IdentityService health check passed - basic functionality verified")
                    return True
                else:
                    logger.warning("IdentityService health check failed - basic functionality test failed")
                    return False
            except Exception as e:
                logger.warning(f"IdentityService health check failed - functionality test error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"IdentityService health check error: {e}")
            return False
    
    def cleanup(self):
        """Clean up service resources (ServiceProtocol implementation)"""
        try:
            logger.info("IdentityService cleanup initiated")
            
            # Clean up persistence layer if enabled
            if hasattr(self, 'persistence') and self.persistence.is_enabled():
                try:
                    self.persistence.cleanup()
                    logger.debug("IdentityService persistence layer cleaned up")
                except Exception as e:
                    logger.warning(f"IdentityService persistence cleanup error: {e}")
            
            # Clean up embedding service if available
            if hasattr(self, 'embedding_service') and self.embedding_service:
                try:
                    if hasattr(self.embedding_service, 'cleanup'):
                        self.embedding_service.cleanup()
                    logger.debug("IdentityService embedding service cleaned up")
                except Exception as e:
                    logger.warning(f"IdentityService embedding service cleanup error: {e}")
            
            # Clear internal caches/state if any
            if hasattr(self, '_cache'):
                self._cache.clear()
                logger.debug("IdentityService cache cleared")
            
            logger.info("IdentityService cleanup completed")
            
        except Exception as e:
            logger.error(f"IdentityService cleanup error: {e}")


# Re-export data models for backward compatibility
__all__ = [
    "IdentityService",
    "Mention", 
    "Entity", 
    "Relationship"
]


def get_identity_service_info():
    """Get information about the identity service implementation"""
    return {
        "module": "identity_service",
        "version": "2.0.0", 
        "architecture": "decomposed_components",
        "description": "Consolidated identity service with modular architecture",
        "capabilities": [
            "entity_mention_management",
            "exact_name_matching", 
            "semantic_similarity_matching",
            "sqlite_persistence",
            "pii_vault_protection",
            "entity_merging",
            "relationship_tracking"
        ],
        "components": {
            "data_models": "Mention, Entity, Relationship data structures",
            "mention_processor": "Mention creation, validation, normalization",
            "entity_resolver": "Entity matching and resolution strategies", 
            "embedding_service": "Optional semantic embeddings with OpenAI",
            "persistence_layer": "SQLite database with transaction support",
            "database_manager": "Low-level database operations and PII vault"
        },
        "decomposed": True,
        "file_count": 7,  # Main file + 6 component files
        "total_lines": 180  # This main file line count
    }