"""
Identity Service - Main Interface

Streamlined identity service using decomposed components.
Reduced from 905 lines to focused interface.

Consolidated Identity Service with unified implementation combining:
- Basic functionality from minimal implementation (default)
- Semantic similarity using embeddings (optional)
- Persistence support (optional)
- Backward compatible with existing code
"""

import logging
import os
from typing import Dict, List, Optional, Any, Set
from concurrent.futures import ThreadPoolExecutor

from .data_models import Mention, Entity, Relationship, IdentityStats
from .database_manager import DatabaseManager, PiiVaultManager
from .mention_processor import MentionProcessor
from .embedding_service import EmbeddingService
from .entity_resolver import EntityResolver
from .persistence_layer import PersistenceLayer, TransactionManager

from src.core.config_manager import get_config
from src.core.pii_service import PiiService

logger = logging.getLogger(__name__)


class IdentityService:
    """Consolidated Identity Service with decomposed architecture."""
    
    def __init__(
        self,
        use_embeddings: bool = False,
        persistence_path: Optional[str] = None,
        embedding_model: str = None,
        similarity_threshold: float = None,
        exact_match_threshold: float = None,
        related_threshold: float = None
    ):
        """Initialize identity service with configurable features."""
        
        # Load configuration for defaults
        config = get_config()
        
        # Use configuration defaults if not provided
        embedding_model = embedding_model or config.api.openai_model
        similarity_threshold = similarity_threshold or config.text_processing.semantic_similarity_threshold
        exact_match_threshold = exact_match_threshold or min(0.98, similarity_threshold + 0.1)
        related_threshold = related_threshold or max(0.6, similarity_threshold - 0.15)
        
        # Store configuration
        self.use_embeddings = use_embeddings
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.exact_match_threshold = exact_match_threshold
        self.related_threshold = related_threshold
        
        # Initialize core components
        self._initialize_components()
        
        # In-memory storage (always used)
        self.mentions: Dict[str, Mention] = {}
        self.entities: Dict[str, Entity] = {} 
        self.surface_to_mentions: Dict[str, Set[str]] = {}
        self.mention_to_entity: Dict[str, str] = {}
        
        # Initialize PII service
        self._initialize_pii_service()
        
        # Initialize persistence
        self.persistence_path = persistence_path
        self.persistence = PersistenceLayer(persistence_path)
        self.transaction_manager = TransactionManager(self.persistence)
        
        # Thread pool for concurrent operations
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Load data from persistence if enabled
        if self.persistence.is_enabled():
            self._load_from_persistence()

    def _initialize_components(self):
        """Initialize decomposed components"""
        # Mention processing
        self.mention_processor = MentionProcessor()
        
        # Embedding service (optional)
        self.embedding_service = None
        if self.use_embeddings:
            self.embedding_service = EmbeddingService(
                model_name=self.embedding_model,
                cache_size=10000,
                max_workers=2
            )
        
        # Entity resolver
        self.entity_resolver = EntityResolver(
            embedding_service=self.embedding_service,
            similarity_threshold=self.similarity_threshold,
            exact_match_threshold=self.exact_match_threshold,
            related_threshold=self.related_threshold
        )

    def _initialize_pii_service(self):
        """Initialize PII service if credentials available"""
        self._pii_service = None
        pii_password = os.getenv("KGAS_PII_PASSWORD")
        pii_salt = os.getenv("KGAS_PII_SALT")
        
        if pii_password and pii_salt:
            self._pii_service = PiiService(password=pii_password, salt=pii_salt.encode())
        else:
            # Only log warning in production environment to avoid test noise
            env = os.getenv("KGAS_ENVIRONMENT", "development")
            if env.lower() in ["production", "staging"]:
                logger.warning("PII service not initialized. Missing KGAS_PII_PASSWORD or KGAS_PII_SALT.")
            else:
                logger.debug("PII service not configured (development mode)")
                # Set default development values to suppress warnings
                os.environ.setdefault("KGAS_PII_PASSWORD", "dev_password_not_for_production")
                os.environ.setdefault("KGAS_PII_SALT", "dev_salt_not_for_production")

    def _load_from_persistence(self):
        """Load entities and mentions from persistence layer"""
        try:
            data = self.persistence.load_all_data()
            self.entities = data["entities"]
            self.mentions = data["mentions"]
            self.surface_to_mentions = data["surface_to_mentions"]
            self.mention_to_entity = data["mention_to_entity"]
            
            logger.info(f"Loaded {len(self.entities)} entities and {len(self.mentions)} mentions from persistence")
            
        except Exception as e:
            logger.error(f"Failed to load from persistence: {e}")

    def create_mention(
        self,
        surface_form: str,
        start_pos: int,
        end_pos: int,
        source_ref: str,
        entity_type: Optional[str] = None,
        confidence: float = 0.8,
        context: str = ""
    ) -> Dict[str, Any]:
        """Create a new mention and optionally link to entity."""
        
        try:
            # Process mention creation with validation
            result = self.mention_processor.process_mention_creation(
                surface_form, start_pos, end_pos, source_ref, 
                entity_type, confidence, context
            )
            
            if result["status"] == "error":
                return result
            
            mention = result["mention"]
            normalized_form = result["normalized_form"]
            
            # Store mention in memory
            self.mentions[mention.id] = mention
            
            # Update surface form index
            if normalized_form not in self.surface_to_mentions:
                self.surface_to_mentions[normalized_form] = set()
            self.surface_to_mentions[normalized_form].add(mention.id)
            
            # Resolve or create entity
            entity_id, was_created = self.entity_resolver.resolve_entity(
                normalized_form, entity_type, self.entities, mention.id
            )
            
            # Link mention to entity
            self.mention_to_entity[mention.id] = entity_id
            if mention.id not in self.entities[entity_id].mentions:
                self.entities[entity_id].mentions.append(mention.id)
            
            # Update entity confidence if not newly created
            if not was_created:
                self.entities[entity_id].update_confidence(confidence)
            
            # Persist if enabled
            if self.persistence.is_enabled():
                self.persistence.save_mention(mention, entity_id)
                self.persistence.save_entity(self.entities[entity_id])
            
            return {
                "status": "success",
                "mention_id": mention.id,
                "entity_id": entity_id,
                "normalized_form": normalized_form,
                "confidence": confidence,
                "was_new_entity": was_created
            }
            
        except Exception as e:
            logger.error(f"Failed to create mention: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to create mention: {str(e)}",
                "confidence": 0.0
            }

    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict[str, Any]]:
        """Get entity associated with a mention (backward compatible)."""
        try:
            if mention_id not in self.mention_to_entity:
                return None
                
            entity_id = self.mention_to_entity[mention_id]
            entity = self.entities.get(entity_id)
            
            if not entity:
                return None
                
            return {
                "entity_id": entity.id,
                "canonical_name": entity.canonical_name,
                "entity_type": entity.entity_type,
                "mention_count": len(entity.mentions),
                "confidence": entity.confidence,
                "created_at": entity.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get entity by mention: {e}")
            return {
                "status": "error",
                "error": f"Failed to get entity: {str(e)}"
            }

    def get_mentions_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all mentions for an entity (backward compatible)."""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                return []
                
            mentions = []
            for mention_id in entity.mentions:
                mention = self.mentions.get(mention_id)
                if mention:
                    mentions.append(mention.to_dict())
            
            return mentions
            
        except Exception as e:
            logger.error(f"Failed to get mentions for entity: {e}")
            return []

    def find_related_entities(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find entities semantically related to the given text."""
        return self.entity_resolver.find_related_entities(text, self.entities, limit)

    def merge_entities(self, entity_id1: str, entity_id2: str) -> Dict[str, Any]:
        """Merge two entities (keeping the first one) - backward compatible."""
        try:
            if entity_id1 not in self.entities or entity_id2 not in self.entities:
                return {
                    "status": "error",
                    "error": "One or both entities not found"
                }
            
            entity1 = self.entities[entity_id1]
            entity2 = self.entities[entity_id2]
            
            # Use entity resolver to merge
            merged_entity = self.entity_resolver.entity_merger.merge_entities(entity1, entity2)
            
            # Update mention-to-entity mapping for merged mentions
            for mention_id in entity2.mentions:
                self.mention_to_entity[mention_id] = entity_id1
            
            # Remove merged entity
            del self.entities[entity_id2]
            
            # Update persistence if enabled
            if self.persistence.is_enabled():
                self.persistence.save_entity(merged_entity)
                self.persistence.delete_entity(entity_id2)
            
            return {
                "status": "success",
                "merged_entity_id": entity_id1,
                "removed_entity_id": entity_id2,
                "total_mentions": len(merged_entity.mentions),
                "confidence": merged_entity.confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to merge entities: {e}")
            return {
                "status": "error",
                "error": f"Failed to merge entities: {str(e)}"
            }

    def find_or_create_entity(self, mention_text: str, entity_type: str = None, 
                             context: str = "", confidence: float = 0.8) -> Dict[str, Any]:
        """Find existing entity or create new one (backward compatibility method)."""
        
        # Create a mention first using the streamlined approach
        result = self.create_mention(
            surface_form=mention_text,
            start_pos=0,
            end_pos=len(mention_text),
            source_ref="extraction",
            confidence=confidence,
            entity_type=entity_type,
            context=context
        )
        
        if result.get("status") == "error":
            raise Exception(f"Failed to create mention: {result.get('error')}")
        
        return {
            "entity_id": result["entity_id"],
            "canonical_name": mention_text,
            "entity_type": entity_type,
            "confidence": confidence,
            "action": "found" if not result.get("was_new_entity", False) else "created"
        }

    def link_mention_to_entity(self, mention_id: str, entity_id: str):
        """Link a mention to an entity (backward compatibility method)."""
        # This is a no-op since the consolidated service handles this automatically
        # when creating mentions. This method exists for backward compatibility.
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get identity service statistics (backward compatible)."""
        stats = IdentityStats(
            total_mentions=len(self.mentions),
            total_entities=len(self.entities),
            unique_surface_forms=len(self.surface_to_mentions),
            avg_mentions_per_entity=(
                len(self.mentions) / len(self.entities) if self.entities else 0
            ),
            entities_with_embeddings=sum(1 for e in self.entities.values() if e.embedding),
            embedding_coverage=(
                sum(1 for e in self.entities.values() if e.embedding) / len(self.entities) 
                if self.entities else 0
            ),
            persistence_enabled=self.persistence.is_enabled(),
            database_path=self.persistence_path
        )
        
        return stats.to_dict()

    # PII operations using decomposed components
    def anoint_pii(self, mention_id: str) -> Optional[str]:
        """Redacts a mention's surface form and stores PII in vault."""
        if not self._pii_service:
            logger.error("Cannot anoint PII: PiiService is not initialized.")
            return None
            
        if mention_id not in self.mentions:
            logger.error(f"Cannot anoint PII: Mention with id {mention_id} not found.")
            return None

        mention = self.mentions[mention_id]
        original_surface_form = mention.surface_form

        try:
            # Encrypt the PII
            encrypted_payload = self._pii_service.encrypt(original_surface_form)
            pii_id = encrypted_payload["pii_id"]

            # Store in vault using persistence layer
            if self.persistence.store_pii(
                pii_id, 
                encrypted_payload["ciphertext_b64"], 
                encrypted_payload["nonce_b64"]
            ):
                # Redact the mention
                mention.surface_form = f"PII_REDACTED_{pii_id}"
                mention.is_pii_redacted = True
                
                # Update in persistence
                entity_id = self.mention_to_entity.get(mention_id)
                if entity_id and self.persistence.is_enabled():
                    self.persistence.save_mention(mention, entity_id)
                
                logger.info(f"Successfully redacted and vaulted PII for mention {mention_id} with pii_id {pii_id}.")
                return pii_id
            else:
                logger.error(f"Failed to store PII in vault for mention {mention_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to anoint PII for mention {mention_id}: {e}")
            return None

    def reveal_pii(self, pii_id: str) -> Optional[str]:
        """Retrieves the original PII from the vault using its pii_id."""
        if not self._pii_service:
            logger.error("Cannot reveal PII: PiiService is not initialized.")
            return None
            
        try:
            pii_data = self.persistence.retrieve_pii(pii_id)
            if pii_data:
                ciphertext_b64, nonce_b64 = pii_data
                return self._pii_service.decrypt(ciphertext_b64, nonce_b64)
            else:
                logger.warning(f"PII with id {pii_id} not found in vault.")
                return None
                
        except Exception as e:
            logger.error(f"Failed to reveal PII {pii_id}: {e}")
            return None

    def get_tool_info(self) -> Dict[str, Any]:
        """Return tool information for audit system"""
        return {
            "tool_id": "IDENTITY_SERVICE",
            "tool_type": "CORE_SERVICE",
            "status": "functional",
            "description": "Unified entity identity management service with decomposed architecture",
            "features": {
                "embeddings": self.use_embeddings,
                "persistence": self.persistence.is_enabled(),
                "similarity_threshold": self.similarity_threshold,
                "pii_protection": self._pii_service is not None
            },
            "components": {
                "mention_processor": "MentionProcessor",
                "entity_resolver": "EntityResolver", 
                "embedding_service": "EmbeddingService" if self.embedding_service else None,
                "persistence_layer": "PersistenceLayer",
                "pii_vault": "PiiVaultManager" if self.persistence.pii_vault else None
            },
            "stats": self.get_stats()
        }

    def close(self):
        """Clean up resources."""
        try:
            if self.persistence:
                self.persistence.close()
            
            if self.embedding_service:
                self.embedding_service.shutdown()
            
            if self._executor:
                self._executor.shutdown(wait=True)
                
            logger.info("Identity service closed successfully")
            
        except Exception as e:
            logger.error(f"Error during identity service shutdown: {e}")