"""
Identity Management Module

Decomposed identity service components for entity mention management,
resolution, and identity tracking.
"""

from .data_models import Mention, Entity, Relationship
from .database_manager import DatabaseManager, PiiVaultManager
from .entity_resolver import EntityResolver, SimilarityMatcher
from .mention_processor import MentionProcessor, SurfaceFormNormalizer
from .embedding_service import EmbeddingService, EmbeddingCache
from .persistence_layer import PersistenceLayer
from .identity_service import IdentityService

__all__ = [
    # Data models
    "Mention", "Entity", "Relationship",
    
    # Database components
    "DatabaseManager", "PiiVaultManager",
    
    # Entity resolution
    "EntityResolver", "SimilarityMatcher", 
    
    # Mention processing
    "MentionProcessor", "SurfaceFormNormalizer",
    
    # Embedding services
    "EmbeddingService", "EmbeddingCache",
    
    # Persistence
    "PersistenceLayer",
    
    # Main service
    "IdentityService"
]
