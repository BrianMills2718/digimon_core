"""FAISS vector index manager."""

import json
import logging
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import faiss
import numpy as np


logger = logging.getLogger(__name__)


class FAISSManager:
    """Manager for FAISS vector index operations."""
    
    def __init__(self, index_path: Path, dimension: int = 768):
        self.index_path = index_path
        self.dimension = dimension
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Paths for auxiliary data
        self.metadata_path = self.index_path.with_suffix('.meta')
        self.id_map_path = self.index_path.with_suffix('.idmap')
        
        self._index: Optional[faiss.IndexFlatL2] = None
        self._id_to_ref: Dict[int, str] = {}
        self._ref_to_id: Dict[str, int] = {}
        self._next_id: int = 0
    
    @property
    def index(self) -> faiss.IndexFlatL2:
        """Lazy-load FAISS index."""
        if self._index is None:
            self._load_or_create_index()
        return self._index
    
    def initialize_index(self) -> None:
        """Initialize a new FAISS index."""
        logger.info(f"Initializing FAISS index with dimension {self.dimension}")
        self._index = faiss.IndexFlatL2(self.dimension)
        self._id_to_ref = {}
        self._ref_to_id = {}
        self._next_id = 0
        self._save_index()
    
    def health_check(self) -> bool:
        """Check if FAISS index is accessible."""
        try:
            # Try to access the index
            _ = self.index.ntotal
            return True
        except Exception as e:
            logger.error(f"FAISS health check failed: {e}")
            return False
    
    def add_vectors(
        self,
        vectors: np.ndarray,
        references: List[str]
    ) -> List[str]:
        """Add vectors to the index with references."""
        if vectors.shape[0] != len(references):
            raise ValueError("Number of vectors must match number of references")
        
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Assign IDs and store mappings
        faiss_refs = []
        for i, ref in enumerate(references):
            if ref in self._ref_to_id:
                # Update existing vector
                faiss_id = self._ref_to_id[ref]
                logger.warning(f"Updating existing vector for reference: {ref}")
            else:
                # New vector
                faiss_id = self._next_id
                self._next_id += 1
                self._id_to_ref[faiss_id] = ref
                self._ref_to_id[ref] = faiss_id
            
            faiss_refs.append(f"faiss://embedding/{faiss_id}")
        
        # Add to index
        self.index.add(vectors.astype(np.float32))
        
        # Save updated index and mappings
        self._save_index()
        
        logger.debug(f"Added {len(vectors)} vectors to FAISS index")
        return faiss_refs
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Search for similar vectors."""
        if query_vector.shape[0] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[0]} doesn't match index dimension {self.dimension}")
        
        # Check if index is empty
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty - no vectors to search")
            return []
        
        # Reshape for FAISS
        query = query_vector.reshape(1, -1).astype(np.float32)
        
        # Search
        distances, indices = self.index.search(query, min(k, self.index.ntotal))
        
        # Convert to references with scores
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # No more results
                break
            
            # Convert L2 distance to similarity score (0-1)
            # Using exponential decay: score = exp(-distance)
            score = float(np.exp(-dist))
            
            # Apply threshold if specified
            if threshold and score < threshold:
                continue
            
            # Get reference
            if idx in self._id_to_ref:
                ref = self._id_to_ref[idx]
                results.append((ref, score))
            else:
                logger.warning(f"FAISS index {idx} has no reference mapping")
        
        return results
    
    def get_vector(self, reference: str) -> Optional[np.ndarray]:
        """Get a vector by reference."""
        if reference not in self._ref_to_id:
            return None
        
        faiss_id = self._ref_to_id[reference]
        
        # FAISS doesn't support direct retrieval, so we search for exact match
        # This is inefficient but works for small indices
        if faiss_id < self.index.ntotal:
            # Reconstruct vector (only works for flat indices)
            vector = self.index.reconstruct(faiss_id)
            return vector
        
        return None
    
    def remove_vector(self, reference: str) -> bool:
        """Remove a vector from the index."""
        if reference not in self._ref_to_id:
            return False
        
        # FAISS doesn't support removal, so we need to rebuild
        logger.warning("Vector removal requires index rebuild - this is expensive")
        
        # Get all vectors except the one to remove
        vectors = []
        refs = []
        
        for ref, faiss_id in self._ref_to_id.items():
            if ref != reference and faiss_id < self.index.ntotal:
                vector = self.index.reconstruct(faiss_id)
                vectors.append(vector)
                refs.append(ref)
        
        # Rebuild index
        self.initialize_index()
        if vectors:
            self.add_vectors(np.array(vectors), refs)
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "memory_usage_mb": self._estimate_memory_usage(),
            "unique_references": len(self._ref_to_id)
        }
    
    def clear(self) -> None:
        """Clear all vectors from the index."""
        self.initialize_index()
        logger.info("FAISS index cleared")
    
    def close(self) -> None:
        """Save and close the index."""
        if self._index is not None:
            self._save_index()
            self._index = None
    
    def _load_or_create_index(self) -> None:
        """Load existing index or create new one."""
        if self.index_path.exists():
            try:
                # Load index
                self._index = faiss.read_index(str(self.index_path))
                
                # Load ID mappings
                if self.id_map_path.exists():
                    with open(self.id_map_path, 'rb') as f:
                        data = pickle.load(f)
                        self._id_to_ref = data['id_to_ref']
                        self._ref_to_id = data['ref_to_id']
                        self._next_id = data['next_id']
                
                logger.info(f"Loaded FAISS index with {self._index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self.initialize_index()
        else:
            self.initialize_index()
    
    def _save_index(self) -> None:
        """Save index and mappings to disk."""
        if self._index is not None:
            # Save index
            faiss.write_index(self._index, str(self.index_path))
            
            # Save ID mappings
            with open(self.id_map_path, 'wb') as f:
                pickle.dump({
                    'id_to_ref': self._id_to_ref,
                    'ref_to_id': self._ref_to_id,
                    'next_id': self._next_id
                }, f)
            
            # Save metadata
            with open(self.metadata_path, 'w') as f:
                json.dump({
                    'dimension': self.dimension,
                    'total_vectors': self._index.ntotal,
                    'index_type': type(self._index).__name__
                }, f)
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        if self._index is None:
            return 0.0
        
        # Estimate: 4 bytes per float * dimension * number of vectors
        vector_memory = 4 * self.dimension * self.index.ntotal / (1024 * 1024)
        
        # Add overhead for mappings (rough estimate)
        mapping_memory = len(self._ref_to_id) * 100 / (1024 * 1024)
        
        return vector_memory + mapping_memory