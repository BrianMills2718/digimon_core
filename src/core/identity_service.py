"""Consolidated Identity Service - Unified Implementation

Combines features from all three identity service implementations:
- Basic functionality from minimal implementation (default)
- Semantic similarity using embeddings (optional)
- Persistence support (optional)
- Backward compatible with existing code

This implementation follows a configuration-based approach to enable features.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid
import re
import json
import sqlite3
from pathlib import Path
import numpy as np
from .config import get_config
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


@dataclass
class Mention:
    """A surface form occurrence in text."""
    id: str
    surface_form: str  # Exact text as it appears
    normalized_form: str  # Cleaned/normalized version
    start_pos: int
    end_pos: int
    source_ref: str  # Reference to source document/chunk
    confidence: float = 0.8
    entity_type: Optional[str] = None
    context: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass  
class Entity:
    """A canonical entity with one or more mentions."""
    id: str
    canonical_name: str  # Primary identifier
    entity_type: Optional[str] = None
    mentions: List[str] = field(default_factory=list)  # Mention IDs
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # For semantic similarity


@dataclass
class Relationship:
    """A relationship between two entities."""
    id: str
    source_id: str  # Source entity ID
    target_id: str  # Target entity ID
    relationship_type: str
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)


class IdentityService:
    """Consolidated Identity Service with optional advanced features."""
    
    def __init__(
        self,
        use_embeddings: bool = False,
        persistence_path: Optional[str] = None,
        embedding_model: str = None,
        similarity_threshold: float = None,
        exact_match_threshold: float = None,
        related_threshold: float = None
    ):
        """Initialize identity service with configurable features.
        
        Args:
            use_embeddings: Enable semantic similarity using embeddings
            persistence_path: Path to SQLite database for persistence
            embedding_model: OpenAI model for embeddings (uses config default if None)
            similarity_threshold: Threshold for entity matching (uses config default if None)
            exact_match_threshold: Threshold for exact matches (calculated from config if None)
            related_threshold: Threshold for related entities (calculated from config if None)
        """
        # Load configuration for defaults
        config = get_config()
        
        # Use configuration defaults if not provided
        embedding_model = embedding_model or config.api.openai_model
        similarity_threshold = similarity_threshold or config.text_processing.semantic_similarity_threshold
        exact_match_threshold = exact_match_threshold or min(0.98, similarity_threshold + 0.1)
        related_threshold = related_threshold or max(0.6, similarity_threshold - 0.15)
        # In-memory storage (always used)
        self.mentions: Dict[str, Mention] = {}
        self.entities: Dict[str, Entity] = {} 
        self.surface_to_mentions: Dict[str, Set[str]] = {}
        self.mention_to_entity: Dict[str, str] = {}
        
        # Configuration
        self.use_embeddings = use_embeddings
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.exact_match_threshold = exact_match_threshold
        self.related_threshold = related_threshold
        
        # Optional features
        self._openai_client = None
        self._embedding_cache: Dict[str, List[float]] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Persistence
        self.persistence_path = persistence_path
        self._db_conn = None
        if persistence_path:
            self._init_database()
            self._load_from_database()
    
    def _init_database(self):
        """Initialize SQLite database for persistence."""
        try:
            self._db_conn = sqlite3.connect(self.persistence_path, check_same_thread=False)
            cursor = self._db_conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    canonical_name TEXT NOT NULL,
                    entity_type TEXT,
                    confidence REAL,
                    created_at TEXT,
                    metadata TEXT,
                    attributes TEXT,
                    embedding BLOB
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentions (
                    id TEXT PRIMARY KEY,
                    surface_form TEXT NOT NULL,
                    normalized_form TEXT NOT NULL,
                    start_pos INTEGER,
                    end_pos INTEGER,
                    source_ref TEXT,
                    confidence REAL,
                    entity_type TEXT,
                    context TEXT,
                    created_at TEXT,
                    entity_id TEXT,
                    FOREIGN KEY (entity_id) REFERENCES entities(id)
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_normalized_form ON mentions(normalized_form)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_canonical ON entities(canonical_name)")
            
            self._db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self._db_conn = None
    
    def _load_from_database(self):
        """Load entities and mentions from database."""
        if not self._db_conn:
            return
            
        try:
            cursor = self._db_conn.cursor()
            
            # Load entities
            cursor.execute("SELECT * FROM entities")
            for row in cursor.fetchall():
                entity = Entity(
                    id=row[0],
                    canonical_name=row[1],
                    entity_type=row[2],
                    confidence=row[3] or 0.8,
                    created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                    metadata=json.loads(row[5]) if row[5] else {},
                    attributes=json.loads(row[6]) if row[6] else {},
                    embedding=np.frombuffer(row[7], dtype=np.float32).tolist() if row[7] else None,
                    mentions=[]  # Will be populated when loading mentions
                )
                self.entities[entity.id] = entity
            
            # Load mentions
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
                    created_at=datetime.fromisoformat(row[9]) if row[9] else datetime.now()
                )
                self.mentions[mention.id] = mention
                
                # Rebuild indices
                if mention.normalized_form not in self.surface_to_mentions:
                    self.surface_to_mentions[mention.normalized_form] = set()
                self.surface_to_mentions[mention.normalized_form].add(mention.id)
                
                # Rebuild mention-entity mapping
                entity_id = row[10]
                if entity_id:
                    self.mention_to_entity[mention.id] = entity_id
                    if entity_id in self.entities:
                        self.entities[entity_id].mentions.append(mention.id)
                        
        except Exception as e:
            logger.error(f"Failed to load from database: {e}")
    
    def _get_openai_client(self):
        """Lazy load OpenAI client."""
        if self._openai_client is None and self.use_embeddings:
            try:
                import openai
                import os
                self._openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.use_embeddings = False
        return self._openai_client
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using OpenAI."""
        if not self.use_embeddings:
            return None
            
        # Check cache
        if text in self._embedding_cache:
            return self._embedding_cache[text]
            
        client = self._get_openai_client()
        if not client:
            return None
            
        try:
            response = client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            embedding = response.data[0].embedding
            
            # Cache it
            self._embedding_cache[text] = embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))
    
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
        """Create a new mention and optionally link to entity.
        
        Backward compatible with minimal implementation.
        """
        try:
            # Input validation (same as minimal)
            if not surface_form or not surface_form.strip():
                return {
                    "status": "error",
                    "error": "surface_form cannot be empty",
                    "confidence": 0.0
                }
                
            if start_pos < 0 or end_pos <= start_pos:
                return {
                    "status": "error", 
                    "error": "Invalid position range",
                    "confidence": 0.0
                }
                
            if not (0.0 <= confidence <= 1.0):
                return {
                    "status": "error",
                    "error": "Confidence must be between 0.0 and 1.0", 
                    "confidence": 0.0
                }
            
            # Create mention
            mention_id = f"mention_{uuid.uuid4().hex[:8]}"
            normalized_form = self._normalize_surface_form(surface_form)
            
            mention = Mention(
                id=mention_id,
                surface_form=surface_form,
                normalized_form=normalized_form,
                start_pos=start_pos,
                end_pos=end_pos,
                source_ref=source_ref,
                confidence=confidence,
                entity_type=entity_type,
                context=context
            )
            
            # Store mention
            self.mentions[mention_id] = mention
            
            # Update surface form index
            if normalized_form not in self.surface_to_mentions:
                self.surface_to_mentions[normalized_form] = set()
            self.surface_to_mentions[normalized_form].add(mention_id)
            
            # Link to entity (uses embeddings if enabled)
            entity_id = self._link_or_create_entity(
                mention_id, normalized_form, entity_type, confidence
            )
            
            # Persist if enabled
            if self._db_conn:
                self._persist_mention(mention, entity_id)
            
            return {
                "status": "success",
                "mention_id": mention_id,
                "entity_id": entity_id,
                "normalized_form": normalized_form,
                "confidence": confidence
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create mention: {str(e)}",
                "confidence": 0.0
            }
    
    def _normalize_surface_form(self, surface_form: str) -> str:
        """Normalize surface form for entity matching."""
        # Same as minimal implementation
        normalized = re.sub(r'\s+', ' ', surface_form.strip().lower())
        return normalized
    
    def _link_or_create_entity(
        self, 
        mention_id: str, 
        normalized_form: str,
        entity_type: Optional[str],
        confidence: float
    ) -> str:
        """Link mention to existing entity or create new one."""
        
        # Try exact match first (backward compatibility)
        existing_entity_id = self._find_matching_entity(normalized_form, entity_type)
        
        # If embeddings enabled and no exact match, try semantic similarity
        if not existing_entity_id and self.use_embeddings:
            existing_entity_id = self._find_similar_entity(normalized_form, entity_type)
        
        if existing_entity_id:
            # Link to existing entity
            self.entities[existing_entity_id].mentions.append(mention_id)
            self.mention_to_entity[mention_id] = existing_entity_id
            
            # Update entity confidence
            entity = self.entities[existing_entity_id]
            mention_count = len(entity.mentions)
            entity.confidence = (entity.confidence * (mention_count - 1) + confidence) / mention_count
            
            # Update in database if persistence enabled
            if self._db_conn:
                self._update_entity_in_db(entity)
            
            return existing_entity_id
        else:
            # Create new entity
            entity_id = f"entity_{uuid.uuid4().hex[:8]}"
            
            # Get embedding if enabled
            embedding = None
            if self.use_embeddings:
                embedding = self._get_embedding(normalized_form)
            
            entity = Entity(
                id=entity_id,
                canonical_name=normalized_form,
                entity_type=entity_type,
                mentions=[mention_id],
                confidence=confidence,
                embedding=embedding
            )
            
            self.entities[entity_id] = entity
            self.mention_to_entity[mention_id] = entity_id
            
            # Persist if enabled
            if self._db_conn:
                self._persist_entity(entity)
            
            return entity_id
    
    def _find_matching_entity(self, normalized_form: str, entity_type: Optional[str]) -> Optional[str]:
        """Find existing entity that matches the normalized form (exact match)."""
        # Same as minimal implementation
        for entity_id, entity in self.entities.items():
            if entity.canonical_name == normalized_form:
                if entity_type and entity.entity_type and entity.entity_type != entity_type:
                    continue
                return entity_id
        return None
    
    def _find_similar_entity(self, normalized_form: str, entity_type: Optional[str]) -> Optional[str]:
        """Find entity using semantic similarity (embeddings)."""
        if not self.use_embeddings:
            return None
            
        # Get embedding for new text
        new_embedding = self._get_embedding(normalized_form)
        if not new_embedding:
            return None
            
        best_match_id = None
        best_similarity = 0.0
        
        # Compare with all entities that have embeddings
        for entity_id, entity in self.entities.items():
            if not entity.embedding:
                continue
                
            # Skip if type mismatch
            if entity_type and entity.entity_type and entity.entity_type != entity_type:
                continue
                
            similarity = self._cosine_similarity(new_embedding, entity.embedding)
            
            if similarity >= self.similarity_threshold and similarity > best_similarity:
                best_match_id = entity_id
                best_similarity = similarity
        
        return best_match_id
    
    def find_related_entities(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find entities semantically related to the given text."""
        if not self.use_embeddings:
            return []
            
        embedding = self._get_embedding(text)
        if not embedding:
            return []
            
        related = []
        
        for entity_id, entity in self.entities.items():
            if not entity.embedding:
                continue
                
            similarity = self._cosine_similarity(embedding, entity.embedding)
            
            if similarity >= self.related_threshold:
                related.append({
                    "entity_id": entity.id,
                    "canonical_name": entity.canonical_name,
                    "entity_type": entity.entity_type,
                    "similarity": similarity,
                    "confidence": entity.confidence
                })
        
        # Sort by similarity
        related.sort(key=lambda x: x["similarity"], reverse=True)
        
        return related[:limit]
    
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
                    mentions.append({
                        "mention_id": mention.id,
                        "surface_form": mention.surface_form,
                        "normalized_form": mention.normalized_form,
                        "start_pos": mention.start_pos,
                        "end_pos": mention.end_pos,
                        "source_ref": mention.source_ref,
                        "confidence": mention.confidence
                    })
            
            return mentions
            
        except Exception as e:
            return []
    
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
            
            # Merge mentions
            entity1.mentions.extend(entity2.mentions)
            
            # Update mention-to-entity mapping
            for mention_id in entity2.mentions:
                self.mention_to_entity[mention_id] = entity_id1
            
            # Update confidence (weighted average)
            total_mentions = len(entity1.mentions)
            entity1_mentions = total_mentions - len(entity2.mentions)
            entity2_mentions = len(entity2.mentions)
            
            entity1.confidence = (
                (entity1.confidence * entity1_mentions + entity2.confidence * entity2_mentions) 
                / total_mentions
            )
            
            # Merge embeddings if available
            if self.use_embeddings and entity1.embedding and entity2.embedding:
                # Average embeddings
                entity1.embedding = [
                    (a * entity1_mentions + b * entity2_mentions) / total_mentions
                    for a, b in zip(entity1.embedding, entity2.embedding)
                ]
            
            # Remove merged entity
            del self.entities[entity_id2]
            
            # Update database if persistence enabled
            if self._db_conn:
                self._update_entity_in_db(entity1)
                self._delete_entity_from_db(entity_id2)
            
            return {
                "status": "success",
                "merged_entity_id": entity_id1,
                "removed_entity_id": entity_id2,
                "total_mentions": total_mentions,
                "confidence": entity1.confidence
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to merge entities: {str(e)}"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get identity service statistics (backward compatible)."""
        stats = {
            "total_mentions": len(self.mentions),
            "total_entities": len(self.entities),
            "unique_surface_forms": len(self.surface_to_mentions),
            "avg_mentions_per_entity": (
                len(self.mentions) / len(self.entities) if self.entities else 0
            )
        }
        
        # Add enhanced stats if features enabled
        if self.use_embeddings:
            entities_with_embeddings = sum(1 for e in self.entities.values() if e.embedding)
            stats["entities_with_embeddings"] = entities_with_embeddings
            stats["embedding_coverage"] = entities_with_embeddings / len(self.entities) if self.entities else 0
        
        if self._db_conn:
            stats["persistence_enabled"] = True
            stats["database_path"] = self.persistence_path
        
        return stats
    
    def find_or_create_entity(self, mention_text: str, entity_type: str = None, 
                             context: str = "", confidence: float = 0.8) -> Dict[str, Any]:
        """Find existing entity or create new one (backward compatibility method).
        
        This method provides backward compatibility with the old EnhancedIdentityService API.
        
        Args:
            mention_text: The surface text of the mention
            entity_type: Type of entity
            context: Additional context
            confidence: Confidence score
            
        Returns:
            Dict with entity_id, canonical_name, and action (found/created)
        """
        # Create a mention first
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
        
        mention_id = result["mention_id"]
        
        # Get the linked entity
        entity_id = self.mention_to_entity.get(mention_id)
        if entity_id and entity_id in self.entities:
            entity = self.entities[entity_id]
            return {
                "entity_id": entity.id,
                "canonical_name": entity.canonical_name,
                "entity_type": entity.entity_type,
                "confidence": entity.confidence,
                "action": "found" if len(entity.mentions) > 1 else "created"
            }
        else:
            # This shouldn't happen with the current implementation, but handle gracefully
            return {
                "entity_id": mention_id,  # Use mention ID as fallback
                "canonical_name": mention_text,
                "entity_type": entity_type,
                "confidence": confidence,
                "action": "created"
            }
    
    def link_mention_to_entity(self, mention_id: str, entity_id: str):
        """Link a mention to an entity (backward compatibility method).
        
        Args:
            mention_id: ID of the mention
            entity_id: ID of the entity
        """
        # This is a no-op since the consolidated service handles this automatically
        # when creating mentions. This method exists for backward compatibility.
        pass
    
    # Persistence methods
    def _persist_entity(self, entity: Entity):
        """Save entity to database."""
        if not self._db_conn:
            return
            
        try:
            cursor = self._db_conn.cursor()
            
            embedding_blob = None
            if entity.embedding:
                embedding_blob = np.array(entity.embedding, dtype=np.float32).tobytes()
            
            cursor.execute("""
                INSERT OR REPLACE INTO entities 
                (id, canonical_name, entity_type, confidence, created_at, metadata, attributes, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.id,
                entity.canonical_name,
                entity.entity_type,
                entity.confidence,
                entity.created_at.isoformat(),
                json.dumps(entity.metadata),
                json.dumps(entity.attributes),
                embedding_blob
            ))
            
            self._db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist entity: {e}")
    
    def _persist_mention(self, mention: Mention, entity_id: str):
        """Save mention to database."""
        if not self._db_conn:
            return
            
        try:
            cursor = self._db_conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO mentions 
                (id, surface_form, normalized_form, start_pos, end_pos, source_ref, 
                 confidence, entity_type, context, created_at, entity_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                entity_id
            ))
            
            self._db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist mention: {e}")
    
    def _update_entity_in_db(self, entity: Entity):
        """Update entity in database."""
        self._persist_entity(entity)  # Same implementation
    
    def _delete_entity_from_db(self, entity_id: str):
        """Delete entity from database."""
        if not self._db_conn:
            return
            
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            self._db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to delete entity: {e}")
    
    def close(self):
        """Clean up resources."""
        if self._db_conn:
            self._db_conn.close()
        self._executor.shutdown()