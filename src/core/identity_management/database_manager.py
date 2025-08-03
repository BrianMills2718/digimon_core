"""
Database Management for Identity Service

Handles SQLite database operations for entity and mention persistence,
including PII vault management.
"""

import sqlite3
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .data_models import Entity, Mention, Relationship

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for identity service"""
    
    def __init__(self, database_path: str):
        """Initialize database manager with SQLite database"""
        self.database_path = database_path
        self._db_conn = None
        self._initialize_connection()
        self._create_tables()

    def _initialize_connection(self):
        """Initialize SQLite database connection"""
        try:
            # Ensure parent directory exists
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
            
            self._db_conn = sqlite3.connect(
                self.database_path, 
                check_same_thread=False,
                timeout=30.0  # 30 second timeout
            )
            
            # Enable WAL mode for better concurrency
            self._db_conn.execute("PRAGMA journal_mode=WAL")
            self._db_conn.execute("PRAGMA synchronous=NORMAL")
            self._db_conn.execute("PRAGMA cache_size=10000")
            self._db_conn.execute("PRAGMA temp_store=memory")
            
            logger.info(f"Database connection initialized: {self.database_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self._db_conn = None
            raise

    def _create_tables(self):
        """Create database tables if they don't exist"""
        if not self._db_conn:
            return
            
        try:
            cursor = self._db_conn.cursor()
            
            # Entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    canonical_name TEXT NOT NULL,
                    entity_type TEXT,
                    confidence REAL NOT NULL DEFAULT 0.8,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    attributes TEXT,
                    embedding BLOB,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mentions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentions (
                    id TEXT PRIMARY KEY,
                    surface_form TEXT NOT NULL,
                    normalized_form TEXT NOT NULL,
                    start_pos INTEGER NOT NULL,
                    end_pos INTEGER NOT NULL,
                    source_ref TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.8,
                    entity_type TEXT,
                    context TEXT,
                    created_at TEXT NOT NULL,
                    entity_id TEXT,
                    is_pii_redacted BOOLEAN DEFAULT FALSE,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE SET NULL
                )
            """)
            
            # Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.8,
                    created_at TEXT NOT NULL,
                    attributes TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
                )
            """)

            # Create indices for performance
            self._create_indices(cursor)
            
            self._db_conn.commit()
            logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            if self._db_conn:
                self._db_conn.rollback()
            raise

    def _create_indices(self, cursor):
        """Create database indices for better query performance"""
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_mentions_normalized_form ON mentions(normalized_form)",
            "CREATE INDEX IF NOT EXISTS idx_mentions_entity_id ON mentions(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_mentions_source_ref ON mentions(source_ref)",
            "CREATE INDEX IF NOT EXISTS idx_entities_canonical_name ON entities(canonical_name)",
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)",
            "CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)",
            "CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)

    def save_entity(self, entity: Entity) -> bool:
        """Save or update entity in database"""
        if not self._db_conn:
            logger.error("Cannot save entity: no database connection")
            return False
            
        try:
            cursor = self._db_conn.cursor()
            
            # Prepare embedding data
            embedding_blob = None
            if entity.embedding:
                embedding_blob = np.array(entity.embedding, dtype=np.float32).tobytes()
            
            cursor.execute("""
                INSERT OR REPLACE INTO entities 
                (id, canonical_name, entity_type, confidence, created_at, metadata, attributes, embedding, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.id,
                entity.canonical_name,
                entity.entity_type,
                entity.confidence,
                entity.created_at.isoformat(),
                json.dumps(entity.metadata),
                json.dumps(entity.attributes),
                embedding_blob,
                datetime.now().isoformat()
            ))
            
            self._db_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save entity {entity.id}: {e}")
            if self._db_conn:
                self._db_conn.rollback()
            return False

    def load_entity(self, entity_id: str) -> Optional[Entity]:
        """Load entity from database by ID"""
        if not self._db_conn:
            return None
            
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Parse embedding data
            embedding = None
            if row[7]:  # embedding column
                embedding = np.frombuffer(row[7], dtype=np.float32).tolist()
                
            # Load associated mentions
            cursor.execute("SELECT id FROM mentions WHERE entity_id = ?", (entity_id,))
            mention_ids = [row[0] for row in cursor.fetchall()]
            
            return Entity(
                id=row[0],
                canonical_name=row[1],
                entity_type=row[2],
                confidence=row[3] or 0.8,
                created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                metadata=json.loads(row[5]) if row[5] else {},
                attributes=json.loads(row[6]) if row[6] else {},
                embedding=embedding,
                mentions=mention_ids
            )
            
        except Exception as e:
            logger.error(f"Failed to load entity {entity_id}: {e}")
            return None

    def save_mention(self, mention: Mention, entity_id: str) -> bool:
        """Save or update mention in database"""
        if not self._db_conn:
            logger.error("Cannot save mention: no database connection")
            return False
            
        try:
            cursor = self._db_conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO mentions 
                (id, surface_form, normalized_form, start_pos, end_pos, source_ref, 
                 confidence, entity_type, context, created_at, entity_id, is_pii_redacted, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mention.id,
                mention.surface_form,
                mention.normalized_form,
                mention.start_pos,
                mention.end_pos,
                mention.source_ref,
                mention.confidence,
                mention.entity_type,
                mention.context,
                mention.created_at.isoformat(),
                entity_id,
                mention.is_pii_redacted,
                datetime.now().isoformat()
            ))
            
            self._db_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save mention {mention.id}: {e}")
            if self._db_conn:
                self._db_conn.rollback()
            return False

    def load_mention(self, mention_id: str) -> Optional[Mention]:
        """Load mention from database by ID"""
        if not self._db_conn:
            return None
            
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("SELECT * FROM mentions WHERE id = ?", (mention_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return Mention(
                id=row[0],
                surface_form=row[1],
                normalized_form=row[2],
                start_pos=row[3],
                end_pos=row[4],
                source_ref=row[5],
                confidence=row[6] or 0.8,
                entity_type=row[7],
                context=row[8] or "",
                created_at=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
                is_pii_redacted=bool(row[11])  # is_pii_redacted column
            )
            
        except Exception as e:
            logger.error(f"Failed to load mention {mention_id}: {e}")
            return None

    def load_all_entities(self) -> Dict[str, Entity]:
        """Load all entities from database"""
        if not self._db_conn:
            return {}
            
        entities = {}
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("SELECT * FROM entities")
            
            for row in cursor.fetchall():
                # Parse embedding data
                embedding = None
                if row[7]:  # embedding column
                    embedding = np.frombuffer(row[7], dtype=np.float32).tolist()
                    
                entity = Entity(
                    id=row[0],
                    canonical_name=row[1],
                    entity_type=row[2],
                    confidence=row[3] or 0.8,
                    created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                    metadata=json.loads(row[5]) if row[5] else {},
                    attributes=json.loads(row[6]) if row[6] else {},
                    embedding=embedding,
                    mentions=[]  # Will be populated when loading mentions
                )
                entities[entity.id] = entity
                
        except Exception as e:
            logger.error(f"Failed to load entities: {e}")
            
        return entities

    def load_all_mentions(self) -> Dict[str, Mention]:
        """Load all mentions from database"""
        if not self._db_conn:
            return {}
            
        mentions = {}
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("SELECT * FROM mentions")
            
            for row in cursor.fetchall():
                mention = Mention(
                    id=row[0],
                    surface_form=row[1],
                    normalized_form=row[2],
                    start_pos=row[3],
                    end_pos=row[4],
                    source_ref=row[5],
                    confidence=row[6] or 0.8,
                    entity_type=row[7],
                    context=row[8] or "",
                    created_at=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
                    is_pii_redacted=bool(row[11])  # is_pii_redacted column
                )
                mentions[mention.id] = mention
                
        except Exception as e:
            logger.error(f"Failed to load mentions: {e}")
            
        return mentions

    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity from database"""
        if not self._db_conn:
            return False
            
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            self._db_conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            if self._db_conn:
                self._db_conn.rollback()
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self._db_conn:
            return {}
            
        try:
            cursor = self._db_conn.cursor()
            
            # Count entities
            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]
            
            # Count mentions
            cursor.execute("SELECT COUNT(*) FROM mentions")
            mention_count = cursor.fetchone()[0]
            
            # Count entities with embeddings
            cursor.execute("SELECT COUNT(*) FROM entities WHERE embedding IS NOT NULL")
            entities_with_embeddings = cursor.fetchone()[0]
            
            # Database file size
            db_path = Path(self.database_path)
            file_size = db_path.stat().st_size if db_path.exists() else 0
            
            return {
                "entity_count": entity_count,
                "mention_count": mention_count,
                "entities_with_embeddings": entities_with_embeddings,
                "database_file_size": file_size,
                "database_path": self.database_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def close(self):
        """Close database connection"""
        if self._db_conn:
            try:
                self._db_conn.close()
                self._db_conn = None
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")


class PiiVaultManager:
    """Manages PII vault operations for secure storage of sensitive data"""
    
    def __init__(self, database_manager: DatabaseManager):
        """Initialize PII vault with database manager"""
        self.db_manager = database_manager
        self._create_pii_vault_table()

    def _create_pii_vault_table(self):
        """Create PII vault table if it doesn't exist"""
        if not self.db_manager._db_conn:
            return
            
        try:
            cursor = self.db_manager._db_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pii_vault (
                    pii_id TEXT PRIMARY KEY,
                    ciphertext_b64 TEXT NOT NULL,
                    nonce_b64 TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    accessed_at TEXT,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Create index for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pii_vault_created ON pii_vault(created_at)")
            
            self.db_manager._db_conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to create PII vault table: {e}")
            if self.db_manager._db_conn:
                self.db_manager._db_conn.rollback()

    def store_pii(self, pii_id: str, ciphertext_b64: str, nonce_b64: str) -> bool:
        """Store encrypted PII in vault"""
        if not self.db_manager._db_conn:
            return False
            
        try:
            cursor = self.db_manager._db_conn.cursor()
            cursor.execute("""
                INSERT INTO pii_vault (pii_id, ciphertext_b64, nonce_b64, created_at)
                VALUES (?, ?, ?, ?)
            """, (pii_id, ciphertext_b64, nonce_b64, datetime.now().isoformat()))
            
            self.db_manager._db_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store PII {pii_id}: {e}")
            if self.db_manager._db_conn:
                self.db_manager._db_conn.rollback()
            return False

    def retrieve_pii(self, pii_id: str) -> Optional[Tuple[str, str]]:
        """Retrieve encrypted PII from vault"""
        if not self.db_manager._db_conn:
            return None
            
        try:
            cursor = self.db_manager._db_conn.cursor()
            cursor.execute(
                "SELECT ciphertext_b64, nonce_b64 FROM pii_vault WHERE pii_id = ?", 
                (pii_id,)
            )
            result = cursor.fetchone()
            
            if result:
                # Update access tracking
                cursor.execute("""
                    UPDATE pii_vault 
                    SET accessed_at = ?, access_count = access_count + 1
                    WHERE pii_id = ?
                """, (datetime.now().isoformat(), pii_id))
                self.db_manager._db_conn.commit()
                
                return result
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve PII {pii_id}: {e}")
            return None

    def delete_pii(self, pii_id: str) -> bool:
        """Delete PII from vault"""
        if not self.db_manager._db_conn:
            return False
            
        try:
            cursor = self.db_manager._db_conn.cursor()
            cursor.execute("DELETE FROM pii_vault WHERE pii_id = ?", (pii_id,))
            self.db_manager._db_conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to delete PII {pii_id}: {e}")
            if self.db_manager._db_conn:
                self.db_manager._db_conn.rollback()
            return False

    def get_pii_stats(self) -> Dict[str, Any]:
        """Get PII vault statistics"""
        if not self.db_manager._db_conn:
            return {}
            
        try:
            cursor = self.db_manager._db_conn.cursor()
            
            # Count total PII entries
            cursor.execute("SELECT COUNT(*) FROM pii_vault")
            pii_count = cursor.fetchone()[0]
            
            # Get access statistics
            cursor.execute("SELECT SUM(access_count), AVG(access_count) FROM pii_vault")
            access_stats = cursor.fetchone()
            total_accesses = access_stats[0] or 0
            avg_accesses = access_stats[1] or 0
            
            return {
                "pii_entries": pii_count,
                "total_accesses": total_accesses,
                "average_accesses_per_entry": avg_accesses
            }
            
        except Exception as e:
            logger.error(f"Failed to get PII stats: {e}")
            return {}