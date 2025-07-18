"""T41: Text Embedder - Creates embeddings for entities and stores in FAISS

This tool creates vector embeddings for text using OpenAI's text-embedding-3-small
and stores them in FAISS for efficient similarity search.
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import pickle

# Load environment variables
load_dotenv()

# Import core services
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService

class TextEmbedder:
    """T41: Creates and manages text embeddings in FAISS"""
    
    def __init__(
        self,
        provenance_service: Optional[ProvenanceService] = None,
        quality_service: Optional[QualityService] = None,
        faiss_index_path: str = "./data/faiss_index"
    ):
        self.provenance_service = provenance_service
        self.quality_service = quality_service
        self.tool_id = "T41_TEXT_EMBEDDER"
        
        # OpenAI setup
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dim = 1536
        
        # FAISS setup
        self.index_path = Path(faiss_index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index = None
        self.id_map = {}  # Maps FAISS ID to entity reference
        self.ref_to_faiss = {}  # Maps entity reference to FAISS ID
        self.counter = 0
        self._init_or_load_index()
        
        print(f"✅ Text Embedder initialized with FAISS at {self.index_path}")
    
    def _init_or_load_index(self):
        """Initialize or load FAISS index"""
        index_file = self.index_path / "embeddings.faiss"
        map_file = self.index_path / "embeddings_map.pkl"
        
        if index_file.exists() and map_file.exists():
            # Load existing
            self.index = faiss.read_index(str(index_file))
            with open(map_file, 'rb') as f:
                data = pickle.load(f)
                self.id_map = data['id_map']
                self.ref_to_faiss = data['ref_to_faiss']
                self.counter = data['counter']
            print(f"  Loaded {self.index.ntotal} embeddings from FAISS")
        else:
            # Create new
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            print("  Created new FAISS index")
    
    def save_index(self):
        """Save FAISS index to disk"""
        index_file = self.index_path / "embeddings.faiss"
        map_file = self.index_path / "embeddings_map.pkl"
        
        faiss.write_index(self.index, str(index_file))
        with open(map_file, 'wb') as f:
            pickle.dump({
                'id_map': self.id_map,
                'ref_to_faiss': self.ref_to_faiss,
                'counter': self.counter
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
            raise
    
    def embed_entities(
        self,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create embeddings for entities and store in FAISS
        
        Args:
            entities: List of entities with text and metadata
            
        Returns:
            Result with embedding references
        """
        # Start operation tracking
        operation_id = None
        if self.provenance_service:
            entity_refs = [e.get("entity_ref", "") for e in entities]
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="embed_entities",
                inputs=entity_refs,
                parameters={
                    "entity_count": len(entities),
                    "embedding_model": self.embedding_model
                }
            )
        
        try:
            embedded_entities = []
            embedding_refs = []
            
            # Process entities in batches
            batch_size = 100
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                
                # Get texts to embed
                texts = []
                for entity in batch:
                    # Combine canonical name with entity type for better embeddings
                    text = f"{entity.get('canonical_name', entity.get('text', ''))} ({entity.get('entity_type', 'UNKNOWN')})"
                    texts.append(text)
                
                # Get embeddings
                if texts:
                    embeddings = self._get_batch_embeddings(texts)
                    
                    # Store in FAISS
                    for j, (entity, embedding) in enumerate(zip(batch, embeddings)):
                        if embedding is not None:
                            # Check if already embedded
                            entity_ref = entity.get("entity_ref", entity.get("entity_id", f"entity_{i+j}"))
                            
                            if entity_ref in self.ref_to_faiss:
                                # Update existing
                                faiss_id = self.ref_to_faiss[entity_ref]
                                # FAISS doesn't support update, so we track it's already there
                                embedding_ref = f"storage://faiss_embedding/{faiss_id}"
                            else:
                                # Add new
                                faiss_id = self.counter
                                self.index.add(embedding.reshape(1, -1))
                                
                                # Update mappings
                                self.id_map[faiss_id] = {
                                    'entity_ref': entity_ref,
                                    'text': texts[j],
                                    'entity_type': entity.get('entity_type', 'UNKNOWN'),
                                    'canonical_name': entity.get('canonical_name', ''),
                                    'embedded_at': datetime.now().isoformat()
                                }
                                self.ref_to_faiss[entity_ref] = faiss_id
                                self.counter += 1
                                
                                embedding_ref = f"storage://faiss_embedding/{faiss_id}"
                            
                            embedded_entity = {
                                'entity_ref': entity_ref,
                                'embedding_ref': embedding_ref,
                                'faiss_id': faiss_id,
                                'embedded': True
                            }
                            
                            embedded_entities.append(embedded_entity)
                            embedding_refs.append(embedding_ref)
            
            # Save index
            self.save_index()
            
            # Assess quality
            confidence = 0.95  # High confidence for OpenAI embeddings
            if self.quality_service:
                quality_result = self.quality_service.assess_confidence(
                    object_ref=f"storage://embeddings_batch/{operation_id or 'batch'}",
                    base_confidence=confidence,
                    factors={
                        "embedding_model_quality": 0.95,
                        "batch_completeness": len(embedded_entities) / len(entities) if entities else 0
                    }
                )
                confidence = quality_result.get("confidence", confidence)
            
            result = {
                "status": "success",
                "embedded_count": len(embedded_entities),
                "embeddings": embedded_entities,
                "total_in_index": self.index.ntotal,
                "confidence": confidence
            }
            
            # Complete operation
            if self.provenance_service and operation_id:
                self.provenance_service.complete_operation(
                    operation_id=operation_id,
                    outputs=embedding_refs,
                    success=True,
                    metadata=result
                )
            
            return result
            
        except Exception as e:
            error_msg = f"Embedding failed: {str(e)}"
            if self.provenance_service and operation_id:
                self.provenance_service.complete_operation(
                    operation_id=operation_id,
                    outputs=[],
                    success=False,
                    error_message=error_msg
                )
            
            return {
                "status": "error",
                "error": error_msg,
                "embedded_count": 0
            }
    
    def _get_batch_embeddings(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Get embeddings for a batch of texts"""
        try:
            response = self.openai.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = []
            for item in response.data:
                embedding = np.array(item.embedding, dtype=np.float32)
                # Normalize
                embedding = embedding / np.linalg.norm(embedding)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [None] * len(texts)
    
    def find_similar(
        self,
        query_text: str,
        k: int = 10,
        threshold: float = 0.7,
        entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find similar entities using FAISS
        
        Args:
            query_text: Text to search for
            k: Number of results
            threshold: Minimum similarity threshold
            entity_type: Filter by entity type
            
        Returns:
            List of similar entities with scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query_text)
        
        # Search FAISS
        k = min(k * 2, self.index.ntotal)  # Get more to filter
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), k
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx in self.id_map:
                entity_info = self.id_map[idx]
                
                # Filter by type if specified
                if entity_type and entity_info.get('entity_type') != entity_type:
                    continue
                
                # Filter by threshold
                similarity = float(dist)  # Cosine similarity since normalized
                if similarity >= threshold:
                    results.append({
                        'entity_ref': entity_info['entity_ref'],
                        'canonical_name': entity_info.get('canonical_name', ''),
                        'entity_type': entity_info.get('entity_type', 'UNKNOWN'),
                        'similarity': similarity,
                        'faiss_id': idx
                    })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]
    
    def get_embedding_by_ref(self, entity_ref: str) -> Optional[np.ndarray]:
        """Get embedding vector for an entity reference"""
        if entity_ref not in self.ref_to_faiss:
            return None
        
        faiss_id = self.ref_to_faiss[entity_ref]
        
        # Reconstruct the vector
        try:
            vector = self.index.reconstruct(int(faiss_id))
            return vector
        except Exception as e:
            print(f"Error reconstructing vector for {entity_ref}: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get FAISS index statistics"""
        entity_types = {}
        for info in self.id_map.values():
            etype = info.get('entity_type', 'UNKNOWN')
            entity_types[etype] = entity_types.get(etype, 0) + 1
        
        return {
            "total_embeddings": self.index.ntotal,
            "unique_entities": len(self.ref_to_faiss),
            "entity_types": entity_types,
            "index_size_mb": self.index.ntotal * self.embedding_dim * 4 / (1024 * 1024),  # Approximate
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dim
        }

# Test function
def test_embedder():
    """Test the text embedder"""
    from src.core.provenance_service import ProvenanceService
    from src.core.quality_service import QualityService
    
    provenance = ProvenanceService()
    quality = QualityService()
    
    embedder = TextEmbedder(
        provenance_service=provenance,
        quality_service=quality
    )
    
    # Test entities
    test_entities = [
        {
            "entity_id": "ent_001",
            "entity_ref": "storage://entity/ent_001",
            "canonical_name": "Massachusetts Institute of Technology",
            "entity_type": "ORG",
            "text": "MIT"
        },
        {
            "entity_id": "ent_002",
            "entity_ref": "storage://entity/ent_002",
            "canonical_name": "Stanford University",
            "entity_type": "ORG",
            "text": "Stanford"
        },
        {
            "entity_id": "ent_003",
            "entity_ref": "storage://entity/ent_003",
            "canonical_name": "Dr. Sarah Johnson",
            "entity_type": "PERSON",
            "text": "Dr. Sarah Johnson"
        }
    ]
    
    print("🚀 Testing Text Embedder with FAISS\n")
    
    # Embed entities
    print("📊 Embedding entities...")
    result = embedder.embed_entities(test_entities)
    
    if result["status"] == "success":
        print(f"✅ Embedded {result['embedded_count']} entities")
        print(f"📈 Total embeddings in index: {result['total_in_index']}")
    else:
        print(f"❌ Error: {result.get('error')}")
        return
    
    # Test similarity search
    print("\n🔍 Testing similarity search...")
    
    queries = [
        ("technology university", "ORG"),
        ("academic institution", "ORG"),
        ("professor", "PERSON"),
        ("MIT", None)
    ]
    
    for query, filter_type in queries:
        print(f"\nQuery: '{query}'" + (f" (type={filter_type})" if filter_type else ""))
        similar = embedder.find_similar(query, k=3, entity_type=filter_type)
        
        if similar:
            for entity in similar:
                print(f"  • {entity['canonical_name']} ({entity['entity_type']}) - Similarity: {entity['similarity']:.3f}")
        else:
            print("  No results found")
    
    # Show statistics
    stats = embedder.get_statistics()
    print(f"\n📊 FAISS Statistics:")
    print(f"  Total embeddings: {stats['total_embeddings']}")
    print(f"  Unique entities: {stats['unique_entities']}")
    print(f"  Index size: {stats['index_size_mb']:.2f} MB")
    print(f"  Entity types: {stats['entity_types']}")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        exit(1)
    
    test_embedder()