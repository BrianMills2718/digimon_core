"""
Persistence Layer for Identity Management

Coordinates database operations and provides high-level persistence interface.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .data_models import Entity, Mention, Relationship, IdentityStats
from .database_manager import DatabaseManager, PiiVaultManager

logger = logging.getLogger(__name__)


class PersistenceLayer:
    """High-level persistence interface for identity management"""
    
    def __init__(self, database_path: Optional[str] = None):
        """Initialize persistence layer"""
        self.database_path = database_path
        self.db_manager = None
        self.pii_vault = None
        self._enabled = False
        
        if database_path:
            self._initialize_persistence()

    def _initialize_persistence(self):
        """Initialize database and PII vault"""
        try:
            self.db_manager = DatabaseManager(self.database_path)
            self.pii_vault = PiiVaultManager(self.db_manager)
            self._enabled = True
            logger.info(f"Persistence layer initialized: {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to initialize persistence layer: {e}")
            self._enabled = False

    def is_enabled(self) -> bool:
        """Check if persistence is enabled and ready"""
        return self._enabled and self.db_manager is not None

    def load_all_data(self) -> Dict[str, Any]:
        """Load all entities and mentions from database"""
        if not self.is_enabled():
            return {
                "entities": {},
                "mentions": {},
                "surface_to_mentions": {},
                "mention_to_entity": {}
            }
        
        try:
            # Load entities and mentions
            entities = self.db_manager.load_all_entities()
            mentions = self.db_manager.load_all_mentions()
            
            # Build indices
            surface_to_mentions = {}
            mention_to_entity = {}
            
            # Process mentions to build indices and link to entities
            for mention_id, mention in mentions.items():
                # Build surface form index
                normalized_form = mention.normalized_form
                if normalized_form not in surface_to_mentions:
                    surface_to_mentions[normalized_form] = set()
                surface_to_mentions[normalized_form].add(mention_id)
                
                # Find the entity this mention belongs to
                entity_id = self._find_entity_for_mention(mention_id, entities)
                if entity_id:
                    mention_to_entity[mention_id] = entity_id
                    # Add mention to entity's mention list if not already there
                    if mention_id not in entities[entity_id].mentions:
                        entities[entity_id].mentions.append(mention_id)
            
            logger.info(f"Loaded {len(entities)} entities and {len(mentions)} mentions from database")
            
            return {
                "entities": entities,
                "mentions": mentions,
                "surface_to_mentions": surface_to_mentions,
                "mention_to_entity": mention_to_entity
            }
            
        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")
            return {
                "entities": {},
                "mentions": {},
                "surface_to_mentions": {},
                "mention_to_entity": {}
            }

    def _find_entity_for_mention(self, mention_id: str, entities: Dict[str, Entity]) -> Optional[str]:
        """Find which entity a mention belongs to"""
        for entity_id, entity in entities.items():
            if mention_id in entity.mentions:
                return entity_id
        return None

    def save_mention(self, mention: Mention, entity_id: str) -> bool:
        """Save mention to database"""
        if not self.is_enabled():
            return False
        
        try:
            return self.db_manager.save_mention(mention, entity_id)
        except Exception as e:
            logger.error(f"Failed to save mention {mention.id}: {e}")
            return False

    def save_entity(self, entity: Entity) -> bool:
        """Save entity to database"""
        if not self.is_enabled():
            return False
        
        try:
            return self.db_manager.save_entity(entity)
        except Exception as e:
            logger.error(f"Failed to save entity {entity.id}: {e}")
            return False

    def save_entity_and_mentions(self, entity: Entity, mentions: Dict[str, Mention]) -> bool:
        """Save entity and all its mentions in a transaction-like manner"""
        if not self.is_enabled():
            return False
        
        try:
            # Save entity first
            if not self.save_entity(entity):
                return False
            
            # Save all mentions associated with this entity
            for mention_id in entity.mentions:
                if mention_id in mentions:
                    mention = mentions[mention_id]
                    if not self.save_mention(mention, entity.id):
                        logger.warning(f"Failed to save mention {mention_id} for entity {entity.id}")
                        # Continue with other mentions rather than fail completely
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save entity and mentions for {entity.id}: {e}")
            return False

    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity from database"""
        if not self.is_enabled():
            return False
        
        try:
            return self.db_manager.delete_entity(entity_id)
        except Exception as e:
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            return False

    def update_entity_confidence(self, entity_id: str, new_confidence: float) -> bool:
        """Update entity confidence in database"""
        if not self.is_enabled():
            return False
        
        try:
            # Load entity, update confidence, save back
            entity = self.db_manager.load_entity(entity_id)
            if entity:
                entity.confidence = new_confidence
                return self.db_manager.save_entity(entity)
            return False
            
        except Exception as e:
            logger.error(f"Failed to update entity confidence for {entity_id}: {e}")
            return False

    def batch_save_entities(self, entities: Dict[str, Entity]) -> Dict[str, bool]:
        """Save multiple entities, return success status for each"""
        results = {}
        
        if not self.is_enabled():
            return {entity_id: False for entity_id in entities.keys()}
        
        for entity_id, entity in entities.items():
            results[entity_id] = self.save_entity(entity)
        
        return results

    def batch_save_mentions(self, mentions: Dict[str, Mention], 
                          mention_to_entity: Dict[str, str]) -> Dict[str, bool]:
        """Save multiple mentions, return success status for each"""
        results = {}
        
        if not self.is_enabled():
            return {mention_id: False for mention_id in mentions.keys()}
        
        for mention_id, mention in mentions.items():
            entity_id = mention_to_entity.get(mention_id)
            if entity_id:
                results[mention_id] = self.save_mention(mention, entity_id)
            else:
                logger.warning(f"No entity mapping found for mention {mention_id}")
                results[mention_id] = False
        
        return results

    def get_persistence_stats(self) -> Dict[str, Any]:
        """Get persistence layer statistics"""
        if not self.is_enabled():
            return {
                "enabled": False,
                "database_path": self.database_path
            }
        
        try:
            db_stats = self.db_manager.get_database_stats()
            pii_stats = self.pii_vault.get_pii_stats() if self.pii_vault else {}
            
            return {
                "enabled": True,
                "database_path": self.database_path,
                "database_stats": db_stats,
                "pii_vault_stats": pii_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get persistence stats: {e}")
            return {
                "enabled": False,
                "error": str(e)
            }

    def compact_database(self) -> bool:
        """Compact database to reclaim space"""
        if not self.is_enabled():
            return False
        
        try:
            if self.db_manager._db_conn:
                cursor = self.db_manager._db_conn.cursor()
                cursor.execute("VACUUM")
                self.db_manager._db_conn.commit()
                logger.info("Database compaction completed")
                return True
        except Exception as e:
            logger.error(f"Database compaction failed: {e}")
        
        return False

    def backup_database(self, backup_path: str) -> bool:
        """Create backup of database"""
        if not self.is_enabled():
            return False
        
        try:
            import shutil
            shutil.copy2(self.database_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False

    # PII Vault operations
    def store_pii(self, pii_id: str, ciphertext_b64: str, nonce_b64: str) -> bool:
        """Store encrypted PII in vault"""
        if not self.is_enabled() or not self.pii_vault:
            return False
        
        return self.pii_vault.store_pii(pii_id, ciphertext_b64, nonce_b64)

    def retrieve_pii(self, pii_id: str) -> Optional[tuple]:
        """Retrieve encrypted PII from vault"""
        if not self.is_enabled() or not self.pii_vault:
            return None
        
        return self.pii_vault.retrieve_pii(pii_id)

    def delete_pii(self, pii_id: str) -> bool:
        """Delete PII from vault"""
        if not self.is_enabled() or not self.pii_vault:
            return False
        
        return self.pii_vault.delete_pii(pii_id)

    def close(self):
        """Close persistence layer and cleanup resources"""
        if self.db_manager:
            try:
                self.db_manager.close()
                logger.info("Persistence layer closed")
            except Exception as e:
                logger.error(f"Error closing persistence layer: {e}")
        
        self._enabled = False


class TransactionManager:
    """Manages database transactions for complex operations"""
    
    def __init__(self, persistence_layer: PersistenceLayer):
        """Initialize transaction manager"""
        self.persistence = persistence_layer
        self._in_transaction = False

    def begin_transaction(self) -> bool:
        """Begin database transaction"""
        if not self.persistence.is_enabled() or self._in_transaction:
            return False
        
        try:
            if self.persistence.db_manager._db_conn:
                self.persistence.db_manager._db_conn.execute("BEGIN")
                self._in_transaction = True
                return True
        except Exception as e:
            logger.error(f"Failed to begin transaction: {e}")
        
        return False

    def commit_transaction(self) -> bool:
        """Commit database transaction"""
        if not self._in_transaction:
            return False
        
        try:
            if self.persistence.db_manager._db_conn:
                self.persistence.db_manager._db_conn.commit()
                self._in_transaction = False
                return True
        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            self.rollback_transaction()
        
        return False

    def rollback_transaction(self) -> bool:
        """Rollback database transaction"""
        if not self._in_transaction:
            return False
        
        try:
            if self.persistence.db_manager._db_conn:
                self.persistence.db_manager._db_conn.rollback()
                self._in_transaction = False
                return True
        except Exception as e:
            logger.error(f"Failed to rollback transaction: {e}")
        
        return False

    def __enter__(self):
        """Context manager entry"""
        if self.begin_transaction():
            return self
        else:
            raise RuntimeError("Failed to begin transaction")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is not None:
            # Exception occurred, rollback
            self.rollback_transaction()
        else:
            # No exception, commit
            if not self.commit_transaction():
                raise RuntimeError("Failed to commit transaction")