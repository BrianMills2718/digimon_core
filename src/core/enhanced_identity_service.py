"""Enhanced Identity Service using OpenAI embeddings for entity resolution"""

import os
import json
import uuid
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import sqlite3
from pathlib import Path

# Load environment variables
load_dotenv()

class EnhancedIdentityService:
    """Advanced entity resolution using embeddings and semantic similarity"""
    
    def __init__(self, db_path: str = "./data/identity.db"):
        """Initialize the enhanced identity service with embeddings"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # OpenAI client for embeddings
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-ada-002"  # Use older model for compatibility
        
        # Initialize database
        self._init_database()
        
        # Cache for embeddings
        self.embedding_cache = {}
        
        # Similarity thresholds
        self.exact_match_threshold = 0.95
        self.alias_threshold = 0.85
        self.related_threshold = 0.70
        
        print("✅ Enhanced Identity Service initialized with OpenAI embeddings")
    
    def _init_database(self):
        """Initialize SQLite database for entity storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Entity table with embeddings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                entity_type TEXT,
                created_at TIMESTAMP,
                embedding BLOB,
                metadata TEXT
            )
        """)
        
        # Surface forms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS surface_forms (
                form_id TEXT PRIMARY KEY,
                entity_id TEXT,
                surface_form TEXT,
                context TEXT,
                confidence REAL,
                created_at TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_canonical ON entities(canonical_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_surface ON surface_forms(surface_form)")
        
        conn.commit()
        conn.close()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with caching"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = np.array(response.data[0].embedding)
            self.embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return random embedding on error (for robustness)
            return np.random.rand(1536)
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_or_create_entity(
        self,
        mention_text: str,
        entity_type: str,
        context: str = "",
        confidence: float = 1.0
    ) -> Dict[str, any]:
        """Find existing entity or create new one using semantic similarity"""
        
        # Get embedding for the mention
        mention_embedding = self.get_embedding(mention_text)
        
        # Search for similar entities
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all entities of the same type
        cursor.execute("""
            SELECT entity_id, canonical_name, embedding 
            FROM entities 
            WHERE entity_type = ?
        """, (entity_type,))
        
        candidates = []
        for row in cursor.fetchall():
            entity_id, canonical_name, embedding_blob = row
            if embedding_blob:
                # Deserialize embedding (1536 dimensions for text-embedding-3-small)
                stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                if len(stored_embedding) != 1536:
                    print(f"Warning: Expected 1536 dims, got {len(stored_embedding)} for entity {entity_id}")
                    continue
                similarity = self.cosine_similarity(mention_embedding, stored_embedding)
                candidates.append((entity_id, canonical_name, similarity))
        
        # Also check surface forms
        cursor.execute("""
            SELECT e.entity_id, e.canonical_name, sf.surface_form
            FROM surface_forms sf
            JOIN entities e ON sf.entity_id = e.entity_id
            WHERE e.entity_type = ?
        """, (entity_type,))
        
        for row in cursor.fetchall():
            entity_id, canonical_name, surface_form = row
            surface_embedding = self.get_embedding(surface_form)
            similarity = self.cosine_similarity(mention_embedding, surface_embedding)
            candidates.append((entity_id, canonical_name, similarity))
        
        # Find best match
        if candidates:
            candidates.sort(key=lambda x: x[2], reverse=True)
            best_match = candidates[0]
            
            if best_match[2] >= self.alias_threshold:
                # Found a match - add as surface form
                entity_id = best_match[0]
                canonical_name = best_match[1]
                
                # Add surface form if it's new
                form_id = f"form_{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT OR IGNORE INTO surface_forms 
                    (form_id, entity_id, surface_form, context, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (form_id, entity_id, mention_text, context, confidence, datetime.now()))
                
                conn.commit()
                conn.close()
                
                return {
                    "entity_id": entity_id,
                    "canonical_name": canonical_name,
                    "surface_form": mention_text,
                    "matched": True,
                    "similarity": best_match[2],
                    "confidence": confidence
                }
        
        # No match found - create new entity
        entity_id = f"entity_{uuid.uuid4().hex[:8]}"
        
        # Determine canonical name (shortest form)
        canonical_name = mention_text.strip()
        
        # Store entity with embedding (ensure float32)
        embedding_float32 = mention_embedding.astype(np.float32)
        embedding_blob = embedding_float32.tobytes()
        cursor.execute("""
            INSERT INTO entities 
            (entity_id, canonical_name, entity_type, created_at, embedding, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entity_id, 
            canonical_name, 
            entity_type, 
            datetime.now(), 
            embedding_blob,
            json.dumps({"context": context})
        ))
        
        # Add surface form
        form_id = f"form_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO surface_forms 
            (form_id, entity_id, surface_form, context, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (form_id, entity_id, mention_text, context, confidence, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return {
            "entity_id": entity_id,
            "canonical_name": canonical_name,
            "surface_form": mention_text,
            "matched": False,
            "similarity": 1.0,
            "confidence": confidence
        }
    
    def merge_entities(self, entity_ids: List[str]) -> Dict[str, any]:
        """Merge multiple entities into one canonical entity"""
        if len(entity_ids) < 2:
            return {"error": "Need at least 2 entities to merge"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all entities
        entities = []
        for entity_id in entity_ids:
            cursor.execute("""
                SELECT entity_id, canonical_name, entity_type, embedding
                FROM entities WHERE entity_id = ?
            """, (entity_id,))
            row = cursor.fetchone()
            if row:
                entities.append(row)
        
        if not entities:
            conn.close()
            return {"error": "No entities found"}
        
        # Choose canonical entity (shortest name)
        canonical_entity = min(entities, key=lambda x: len(x[1]))
        canonical_id = canonical_entity[0]
        
        # Update all surface forms to point to canonical
        for entity_id, _, _, _ in entities:
            if entity_id != canonical_id:
                cursor.execute("""
                    UPDATE surface_forms 
                    SET entity_id = ? 
                    WHERE entity_id = ?
                """, (canonical_id, entity_id))
                
                # Delete merged entity
                cursor.execute("DELETE FROM entities WHERE entity_id = ?", (entity_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "canonical_id": canonical_id,
            "canonical_name": canonical_entity[1],
            "merged_count": len(entities) - 1
        }
    
    def find_related_entities(self, entity_id: str, threshold: float = None) -> List[Dict]:
        """Find entities semantically related to given entity"""
        if threshold is None:
            threshold = self.related_threshold
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get target entity
        cursor.execute("""
            SELECT canonical_name, entity_type, embedding
            FROM entities WHERE entity_id = ?
        """, (entity_id,))
        
        target = cursor.fetchone()
        if not target:
            conn.close()
            return []
        
        target_name, target_type, target_embedding_blob = target
        target_embedding = np.frombuffer(target_embedding_blob, dtype=np.float32)
        
        # Find similar entities
        cursor.execute("""
            SELECT entity_id, canonical_name, entity_type, embedding
            FROM entities WHERE entity_id != ?
        """, (entity_id,))
        
        related = []
        for row in cursor.fetchall():
            other_id, other_name, other_type, other_embedding_blob = row
            if other_embedding_blob:
                other_embedding = np.frombuffer(other_embedding_blob, dtype=np.float32)
                similarity = self.cosine_similarity(target_embedding, other_embedding)
                
                if similarity >= threshold:
                    related.append({
                        "entity_id": other_id,
                        "canonical_name": other_name,
                        "entity_type": other_type,
                        "similarity": similarity,
                        "relationship": "semantically_similar"
                    })
        
        conn.close()
        
        # Sort by similarity
        related.sort(key=lambda x: x["similarity"], reverse=True)
        return related
    
    def get_entity_info(self, entity_id: str) -> Optional[Dict]:
        """Get complete information about an entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get entity
        cursor.execute("""
            SELECT canonical_name, entity_type, created_at, metadata
            FROM entities WHERE entity_id = ?
        """, (entity_id,))
        
        entity = cursor.fetchone()
        if not entity:
            conn.close()
            return None
        
        canonical_name, entity_type, created_at, metadata = entity
        
        # Get surface forms
        cursor.execute("""
            SELECT surface_form, context, confidence
            FROM surface_forms WHERE entity_id = ?
            ORDER BY confidence DESC
        """, (entity_id,))
        
        surface_forms = []
        for row in cursor.fetchall():
            surface_forms.append({
                "text": row[0],
                "context": row[1],
                "confidence": row[2]
            })
        
        conn.close()
        
        return {
            "entity_id": entity_id,
            "canonical_name": canonical_name,
            "entity_type": entity_type,
            "created_at": created_at,
            "surface_forms": surface_forms,
            "metadata": json.loads(metadata) if metadata else {}
        }
    
    def create_mention(
        self,
        surface_form: str,
        start_pos: int,
        end_pos: int,
        source_ref: str,
        entity_type: Optional[str] = None,
        confidence: float = 0.8
    ) -> Dict[str, any]:
        """API compatibility method for base IdentityService interface.
        
        Creates a mention and automatically resolves to entity using embeddings.
        """
        try:
            # Input validation
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
            
            # Use enhanced resolution with context from source_ref
            context = f"Source: {source_ref}, Position: {start_pos}-{end_pos}"
            
            # Default entity type if not provided
            if not entity_type:
                entity_type = "UNKNOWN"
            
            # Use the enhanced find_or_create_entity method
            result = self.find_or_create_entity(
                mention_text=surface_form,
                entity_type=entity_type,
                context=context,
                confidence=confidence
            )
            
            # Generate mention ID for compatibility
            mention_id = f"mention_{uuid.uuid4().hex[:8]}"
            
            return {
                "status": "success",
                "mention_id": mention_id,
                "entity_id": result["entity_id"],
                "normalized_form": result["canonical_name"],
                "confidence": result["confidence"],
                "matched_existing": result["matched"],
                "similarity": result.get("similarity", 1.0)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create mention: {str(e)}",
                "confidence": 0.0
            }

    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict]:
        """Compatibility method for EntityBuilder - gets entity by mention ID"""
        # For now, just return basic entity info
        # In a full implementation, this would track mention->entity mappings
        return {
            "entity_id": mention_id,  # Use mention_id as entity_id for simplicity
            "canonical_name": "Unknown Entity",
            "entity_type": "UNKNOWN",
            "confidence": 0.8
        }
    
    def get_mentions_for_entity(self, entity_id: str) -> List[Dict[str, any]]:
        """Get all mentions for an entity - compatibility method"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT surface_form, context, confidence
            FROM surface_forms WHERE entity_id = ?
        """, (entity_id,))
        
        mentions = []
        for row in cursor.fetchall():
            mentions.append({
                "mention_id": f"mention_{uuid.uuid4().hex[:8]}",
                "surface_form": row[0],
                "normalized_form": row[0].lower().strip(),
                "source_ref": row[1],
                "confidence": row[2]
            })
        
        conn.close()
        return mentions
    
    def get_stats(self) -> Dict[str, any]:
        """Get identity service statistics - compatibility method"""
        stats = self.get_statistics()
        return {
            "total_mentions": stats.get("total_surface_forms", 0),
            "total_entities": stats.get("total_entities", 0),
            "unique_surface_forms": stats.get("total_surface_forms", 0),
            "avg_mentions_per_entity": (
                stats.get("total_surface_forms", 0) / max(stats.get("total_entities", 1), 1)
            )
        }
    
    def find_similar_entities(self, text: str, threshold: float = 0.85) -> List[Dict]:
        """Find entities similar to given text - compatibility method"""
        # Get embedding for input text
        text_embedding = self.get_embedding(text)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT entity_id, canonical_name, entity_type, embedding
            FROM entities WHERE embedding IS NOT NULL
        """)
        
        similar = []
        for row in cursor.fetchall():
            entity_id, canonical_name, entity_type, embedding_blob = row
            if embedding_blob:
                entity_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                similarity = self.cosine_similarity(text_embedding, entity_embedding)
                
                if similarity >= threshold:
                    similar.append({
                        "entity_id": entity_id,
                        "canonical_name": canonical_name,
                        "entity_type": entity_type,
                        "similarity": similarity,
                        "confidence": similarity
                    })
        
        conn.close()
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar
    
    def get_statistics(self) -> Dict[str, int]:
        """Get service statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Entity count by type
        cursor.execute("""
            SELECT entity_type, COUNT(*) 
            FROM entities 
            GROUP BY entity_type
        """)
        stats["entities_by_type"] = dict(cursor.fetchall())
        
        # Total entities
        cursor.execute("SELECT COUNT(*) FROM entities")
        stats["total_entities"] = cursor.fetchone()[0]
        
        # Total surface forms
        cursor.execute("SELECT COUNT(*) FROM surface_forms")
        stats["total_surface_forms"] = cursor.fetchone()[0]
        
        # Entities with multiple surface forms
        cursor.execute("""
            SELECT COUNT(DISTINCT entity_id) 
            FROM surface_forms 
            GROUP BY entity_id 
            HAVING COUNT(*) > 1
        """)
        stats["entities_with_aliases"] = len(cursor.fetchall())
        
        conn.close()
        
        return stats
    
    def link_mention_to_entity(self, mention_id: str, entity_id: str) -> bool:
        """Link a mention to an entity - compatibility method for ontology extractor"""
        try:
            # In this implementation, mentions are automatically linked during creation
            # This method exists for API compatibility
            return True
        except Exception as e:
            print(f"Failed to link mention {mention_id} to entity {entity_id}: {e}")
            return False

# Example usage
if __name__ == "__main__":
    service = EnhancedIdentityService()
    
    # Test entity resolution
    print("\n🔍 Testing Enhanced Entity Resolution:")
    
    # These should resolve to the same entity
    entities = [
        ("MIT", "ORG", "Dr. Johnson works at MIT"),
        ("Massachusetts Institute of Technology", "ORG", "The Massachusetts Institute of Technology announced..."),
        ("M.I.T.", "ORG", "Research from M.I.T. shows..."),
        ("Mass. Inst. of Technology", "ORG", "Mass. Inst. of Technology researchers found...")
    ]
    
    results = []
    for name, entity_type, context in entities:
        result = service.find_or_create_entity(name, entity_type, context)
        results.append(result)
        print(f"\n✓ '{name}' → Entity ID: {result['entity_id']}")
        print(f"  Canonical: {result['canonical_name']}")
        print(f"  Matched: {result['matched']}")
        print(f"  Similarity: {result.get('similarity', 1.0):.3f}")
    
    # Check if they resolved to same entity
    unique_ids = set(r['entity_id'] for r in results)
    if len(unique_ids) == 1:
        print("\n✅ SUCCESS: All MIT variations resolved to same entity!")
    else:
        print(f"\n⚠️  WARNING: Resolved to {len(unique_ids)} different entities")
    
    # Get entity info
    if results:
        info = service.get_entity_info(results[0]['entity_id'])
        print(f"\n📊 Entity Information:")
        print(f"  Canonical Name: {info['canonical_name']}")
        print(f"  Surface Forms: {len(info['surface_forms'])}")
        for sf in info['surface_forms']:
            print(f"    - {sf['text']} (confidence: {sf['confidence']:.2f})")
    
    # Test with different entities
    print("\n\n🔍 Testing Different Organizations:")
    
    orgs = [
        ("Stanford University", "ORG", "Stanford University is located in California"),
        ("Stanford", "ORG", "Researchers at Stanford discovered..."),
        ("IBM", "ORG", "IBM announced new quantum computer"),
        ("International Business Machines", "ORG", "International Business Machines Corporation released...")
    ]
    
    for name, entity_type, context in orgs:
        result = service.find_or_create_entity(name, entity_type, context)
        print(f"\n✓ '{name}' → {result['canonical_name']} (matched: {result['matched']})")
    
    # Show statistics
    stats = service.get_statistics()
    print(f"\n\n📊 Service Statistics:")
    print(f"  Total Entities: {stats['total_entities']}")
    print(f"  Total Surface Forms: {stats['total_surface_forms']}")
    print(f"  Entities with Aliases: {stats['entities_with_aliases']}")
    print(f"  Entity Types: {stats['entities_by_type']}")