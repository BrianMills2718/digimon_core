"""Enhanced Identity Service using FAISS for vector similarity search"""

import os
import json
import uuid
import pickle
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class EnhancedIdentityServiceFAISS:
    """Entity resolution using FAISS vector search and OpenAI embeddings"""
    
    def __init__(self, faiss_index_path: str = "./data/faiss_index"):
        """Initialize the service with FAISS index"""
        self.index_path = Path(faiss_index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # OpenAI client for embeddings
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dim = 1536
        
        # Initialize FAISS index
        self.index = None
        self.entity_map = {}  # Maps FAISS ID to entity info
        self.entity_counter = 0
        self._init_or_load_index()
        
        # Similarity thresholds
        self.exact_match_threshold = 0.95
        self.alias_threshold = 0.85
        self.related_threshold = 0.70
        
        print("✅ Enhanced Identity Service initialized with FAISS")
    
    def _init_or_load_index(self):
        """Initialize new or load existing FAISS index"""
        index_file = self.index_path / "entity_index.faiss"
        map_file = self.index_path / "entity_map.pkl"
        
        if index_file.exists() and map_file.exists():
            # Load existing index
            self.index = faiss.read_index(str(index_file))
            with open(map_file, 'rb') as f:
                data = pickle.load(f)
                self.entity_map = data['entity_map']
                self.entity_counter = data['counter']
            print(f"  Loaded FAISS index with {self.index.ntotal} vectors")
        else:
            # Create new index
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            self.entity_map = {}
            self.entity_counter = 0
            print("  Created new FAISS index")
    
    def save_index(self):
        """Save FAISS index to disk"""
        index_file = self.index_path / "entity_index.faiss"
        map_file = self.index_path / "entity_map.pkl"
        
        faiss.write_index(self.index, str(index_file))
        with open(map_file, 'wb') as f:
            pickle.dump({
                'entity_map': self.entity_map,
                'counter': self.entity_counter
            }, f)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        try:
            response = self.openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return random normalized embedding on error
            embedding = np.random.rand(self.embedding_dim).astype(np.float32)
            return embedding / np.linalg.norm(embedding)
    
    def find_or_create_entity(
        self,
        mention_text: str,
        entity_type: str,
        context: str = "",
        confidence: float = 1.0
    ) -> Dict[str, any]:
        """Find existing entity or create new one using FAISS similarity search"""
        
        # Get embedding for the mention
        mention_embedding = self.get_embedding(mention_text)
        
        # Search FAISS index for similar entities
        if self.index.ntotal > 0:
            # Search for top-k similar entities
            k = min(10, self.index.ntotal)
            distances, indices = self.index.search(
                mention_embedding.reshape(1, -1), k
            )
            
            # Check if any match is above threshold
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx != -1:  # Valid index
                    entity_info = self.entity_map.get(idx)
                    if entity_info and entity_info['entity_type'] == entity_type:
                        # Cosine similarity from inner product (since vectors are normalized)
                        similarity = float(dist)
                        
                        if similarity >= self.alias_threshold:
                            # Found a match!
                            entity_id = entity_info['entity_id']
                            
                            # Add surface form
                            if mention_text not in entity_info['surface_forms']:
                                entity_info['surface_forms'].append(mention_text)
                                self.entity_map[idx] = entity_info  # Update
                                self.save_index()
                            
                            return {
                                "entity_id": entity_id,
                                "canonical_name": entity_info['canonical_name'],
                                "surface_form": mention_text,
                                "matched": True,
                                "similarity": similarity,
                                "confidence": confidence
                            }
        
        # No match found - create new entity
        entity_id = f"entity_{uuid.uuid4().hex[:8]}"
        
        # Add to FAISS index
        faiss_id = self.entity_counter
        self.index.add(mention_embedding.reshape(1, -1))
        
        # Store entity info
        self.entity_map[faiss_id] = {
            'entity_id': entity_id,
            'canonical_name': mention_text.strip(),
            'entity_type': entity_type,
            'surface_forms': [mention_text],
            'created_at': datetime.now().isoformat(),
            'faiss_id': faiss_id,
            'context': context
        }
        
        self.entity_counter += 1
        self.save_index()
        
        return {
            "entity_id": entity_id,
            "canonical_name": mention_text.strip(),
            "surface_form": mention_text,
            "matched": False,
            "similarity": 1.0,
            "confidence": confidence
        }
    
    def find_similar_entities(
        self, 
        query: str, 
        entity_type: Optional[str] = None,
        k: int = 10,
        threshold: float = None
    ) -> List[Dict]:
        """Find entities similar to query text"""
        if threshold is None:
            threshold = self.related_threshold
        
        if self.index.ntotal == 0:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search FAISS
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), k
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:
                entity_info = self.entity_map.get(idx)
                if entity_info:
                    similarity = float(dist)
                    
                    # Filter by entity type if specified
                    if entity_type and entity_info['entity_type'] != entity_type:
                        continue
                    
                    # Filter by threshold
                    if similarity >= threshold:
                        results.append({
                            "entity_id": entity_info['entity_id'],
                            "canonical_name": entity_info['canonical_name'],
                            "entity_type": entity_info['entity_type'],
                            "similarity": similarity,
                            "surface_forms": entity_info['surface_forms']
                        })
        
        return results
    
    def get_entity_info(self, entity_id: str) -> Optional[Dict]:
        """Get information about a specific entity"""
        for entity_info in self.entity_map.values():
            if entity_info['entity_id'] == entity_id:
                return {
                    "entity_id": entity_id,
                    "canonical_name": entity_info['canonical_name'],
                    "entity_type": entity_info['entity_type'],
                    "created_at": entity_info['created_at'],
                    "surface_forms": entity_info['surface_forms'],
                    "faiss_id": entity_info['faiss_id']
                }
        return None
    
    def merge_entities(self, entity_ids: List[str]) -> Dict[str, any]:
        """Merge multiple entities into one"""
        if len(entity_ids) < 2:
            return {"error": "Need at least 2 entities to merge"}
        
        # Find all entities
        entities_to_merge = []
        for faiss_id, entity_info in self.entity_map.items():
            if entity_info['entity_id'] in entity_ids:
                entities_to_merge.append((faiss_id, entity_info))
        
        if len(entities_to_merge) < 2:
            return {"error": "Could not find enough entities to merge"}
        
        # Choose canonical entity (shortest name)
        canonical = min(entities_to_merge, key=lambda x: len(x[1]['canonical_name']))
        canonical_id, canonical_info = canonical
        
        # Merge surface forms
        all_surface_forms = set()
        for _, entity_info in entities_to_merge:
            all_surface_forms.update(entity_info['surface_forms'])
        
        # Update canonical entity
        canonical_info['surface_forms'] = list(all_surface_forms)
        self.entity_map[canonical_id] = canonical_info
        
        # Remove other entities from FAISS (mark as deleted)
        for faiss_id, entity_info in entities_to_merge:
            if faiss_id != canonical_id:
                # We can't actually remove from FAISS index, so mark as deleted
                self.entity_map[faiss_id] = None
        
        self.save_index()
        
        return {
            "canonical_id": canonical_info['entity_id'],
            "canonical_name": canonical_info['canonical_name'],
            "merged_count": len(entities_to_merge) - 1,
            "total_surface_forms": len(all_surface_forms)
        }
    
    def get_statistics(self) -> Dict[str, int]:
        """Get service statistics"""
        stats = {
            "total_vectors": self.index.ntotal,
            "total_entities": sum(1 for e in self.entity_map.values() if e is not None),
            "entities_by_type": {}
        }
        
        # Count by type
        for entity_info in self.entity_map.values():
            if entity_info:
                entity_type = entity_info['entity_type']
                stats["entities_by_type"][entity_type] = stats["entities_by_type"].get(entity_type, 0) + 1
        
        # Count entities with multiple surface forms
        stats["entities_with_aliases"] = sum(
            1 for e in self.entity_map.values() 
            if e and len(e['surface_forms']) > 1
        )
        
        return stats
    
    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict]:
        """Compatibility method for EntityBuilder"""
        # For compatibility, treat mention_id as potential entity_id
        for entity_info in self.entity_map.values():
            if entity_info and entity_info['entity_id'] == mention_id:
                return {
                    "entity_id": entity_info['entity_id'],
                    "canonical_name": entity_info['canonical_name'],
                    "entity_type": entity_info['entity_type'],
                    "confidence": 0.9
                }
        
        # Not found - return default
        return {
            "entity_id": mention_id,
            "canonical_name": "Unknown Entity",
            "entity_type": "UNKNOWN",
            "confidence": 0.8
        }

# Example usage
if __name__ == "__main__":
    service = EnhancedIdentityServiceFAISS()
    
    print("\n🔍 Testing FAISS-based Entity Resolution:")
    
    # Test entities
    test_cases = [
        ("MIT", "ORG"),
        ("Massachusetts Institute of Technology", "ORG"),
        ("M.I.T.", "ORG"),
        ("Stanford University", "ORG"),
        ("Stanford", "ORG"),
        ("IBM", "ORG"),
        ("International Business Machines", "ORG")
    ]
    
    for name, entity_type in test_cases:
        result = service.find_or_create_entity(name, entity_type)
        print(f"\n✓ '{name}' → Entity: {result['entity_id']}")
        print(f"  Canonical: {result['canonical_name']}")
        print(f"  Matched: {result['matched']}")
        if result['matched']:
            print(f"  Similarity: {result['similarity']:.3f}")
    
    # Test similarity search
    print("\n\n🔎 Testing Similarity Search:")
    similar = service.find_similar_entities("technology institute", k=5)
    print(f"\nEntities similar to 'technology institute':")
    for entity in similar:
        print(f"  • {entity['canonical_name']} ({entity['entity_type']}) - Similarity: {entity['similarity']:.3f}")
    
    # Show statistics
    stats = service.get_statistics()
    print(f"\n\n📊 FAISS Statistics:")
    print(f"  Total vectors: {stats['total_vectors']}")
    print(f"  Total entities: {stats['total_entities']}")
    print(f"  Entities with aliases: {stats['entities_with_aliases']}")
    print(f"  By type: {stats['entities_by_type']}")