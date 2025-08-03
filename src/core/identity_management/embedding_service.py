"""
Embedding Service Components

Handles semantic embeddings for entity similarity matching.
"""

import logging
import threading
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import os

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Thread-safe cache for embeddings"""
    
    def __init__(self, max_size: int = 10000):
        """Initialize embedding cache with maximum size"""
        self.max_size = max_size
        self._cache: Dict[str, List[float]] = {}
        self._access_order: List[str] = []
        self._lock = threading.RLock()

    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        with self._lock:
            if text in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(text)
                self._access_order.append(text)
                return self._cache[text].copy()
            return None

    def put(self, text: str, embedding: List[float]) -> None:
        """Store embedding in cache with LRU eviction"""
        with self._lock:
            # Remove if already exists
            if text in self._cache:
                self._access_order.remove(text)
            
            # Evict oldest if at capacity
            while len(self._cache) >= self.max_size and self._access_order:
                oldest = self._access_order.pop(0)
                del self._cache[oldest]
            
            # Add new embedding
            self._cache[text] = embedding.copy()
            self._access_order.append(text)

    def clear(self) -> None:
        """Clear all cached embeddings"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "current_size": len(self._cache),
                "max_size": self.max_size,
                "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0,
                "keys_sample": list(self._cache.keys())[:10]  # First 10 keys
            }


class SimilarityCalculator:
    """Handles similarity calculations between embeddings"""
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        if len(vec1) != len(vec2):
            logger.warning(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")
            return 0.0
        
        try:
            vec1_np = np.array(vec1, dtype=np.float32)
            vec2_np = np.array(vec2, dtype=np.float32)
            
            # Calculate dot product
            dot_product = np.dot(vec1_np, vec2_np)
            
            # Calculate norms
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = float(dot_product / (norm1 * norm2))
            
            # Ensure result is in valid range
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    @staticmethod
    def euclidean_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean similarity (1 / (1 + distance))"""
        if not vec1 or not vec2:
            return 0.0
        
        if len(vec1) != len(vec2):
            return 0.0
        
        try:
            vec1_np = np.array(vec1, dtype=np.float32)
            vec2_np = np.array(vec2, dtype=np.float32)
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(vec1_np - vec2_np)
            
            # Convert to similarity (closer to 1 means more similar)
            similarity = 1.0 / (1.0 + distance)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating Euclidean similarity: {e}")
            return 0.0

    @staticmethod
    def manhattan_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate Manhattan similarity (1 / (1 + distance))"""
        if not vec1 or not vec2:
            return 0.0
        
        if len(vec1) != len(vec2):
            return 0.0
        
        try:
            vec1_np = np.array(vec1, dtype=np.float32)
            vec2_np = np.array(vec2, dtype=np.float32)
            
            # Calculate Manhattan distance
            distance = np.sum(np.abs(vec1_np - vec2_np))
            
            # Convert to similarity
            similarity = 1.0 / (1.0 + distance)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating Manhattan similarity: {e}")
            return 0.0


class EmbeddingService:
    """Main service for generating and managing embeddings"""
    
    def __init__(self, 
                 model_name: str = "text-embedding-ada-002",
                 cache_size: int = 10000,
                 max_workers: int = 4):
        """Initialize embedding service"""
        self.model_name = model_name
        self.cache = EmbeddingCache(max_size=cache_size)
        self.similarity_calc = SimilarityCalculator()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._openai_client = None
        self._enabled = False
        
        # Try to initialize OpenAI client
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.debug("No OpenAI API key found, embedding service disabled")
                return
            
            import openai
            self._openai_client = openai.OpenAI(api_key=api_key)
            self._enabled = True
            logger.info("Embedding service initialized successfully")
            
        except ImportError:
            logger.warning("OpenAI package not installed, embedding service disabled")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")

    def is_enabled(self) -> bool:
        """Check if embedding service is enabled and ready"""
        return self._enabled and self._openai_client is not None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text, using cache if available"""
        if not self.is_enabled():
            return None
        
        if not text or not text.strip():
            return None
        
        # Check cache first
        text_key = text.strip()
        cached_embedding = self.cache.get(text_key)
        if cached_embedding:
            return cached_embedding
        
        # Generate new embedding
        try:
            response = self._openai_client.embeddings.create(
                input=text_key,
                model=self.model_name
            )
            
            embedding = response.data[0].embedding
            
            # Cache the result
            self.cache.put(text_key, embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to get embedding for text: {e}")
            return None

    def get_embeddings_batch(self, texts: List[str]) -> Dict[str, Optional[List[float]]]:
        """Get embeddings for multiple texts efficiently"""
        if not self.is_enabled():
            return {text: None for text in texts}
        
        results = {}
        uncached_texts = []
        
        # Check cache for each text
        for text in texts:
            if not text or not text.strip():
                results[text] = None
                continue
            
            text_key = text.strip()
            cached_embedding = self.cache.get(text_key)
            if cached_embedding:
                results[text] = cached_embedding
            else:
                uncached_texts.append(text)
        
        # Get embeddings for uncached texts
        if uncached_texts:
            try:
                # OpenAI supports batch requests
                response = self._openai_client.embeddings.create(
                    input=uncached_texts,
                    model=self.model_name
                )
                
                # Process results
                for i, text in enumerate(uncached_texts):
                    embedding = response.data[i].embedding
                    results[text] = embedding
                    
                    # Cache the result
                    self.cache.put(text.strip(), embedding)
                    
            except Exception as e:
                logger.error(f"Failed to get batch embeddings: {e}")
                # Set failed texts to None
                for text in uncached_texts:
                    results[text] = None
        
        return results

    def calculate_similarity(self, text1: str, text2: str, 
                           method: str = "cosine") -> float:
        """Calculate similarity between two texts using embeddings"""
        if not self.is_enabled():
            return 0.0
        
        # Get embeddings for both texts
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        
        if not embedding1 or not embedding2:
            return 0.0
        
        # Calculate similarity based on method
        if method == "cosine":
            return self.similarity_calc.cosine_similarity(embedding1, embedding2)
        elif method == "euclidean":
            return self.similarity_calc.euclidean_similarity(embedding1, embedding2)
        elif method == "manhattan":
            return self.similarity_calc.manhattan_similarity(embedding1, embedding2)
        else:
            logger.warning(f"Unknown similarity method: {method}, using cosine")
            return self.similarity_calc.cosine_similarity(embedding1, embedding2)

    def find_most_similar(self, target_text: str, candidates: List[str],
                         threshold: float = 0.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Find most similar texts from candidates"""
        if not self.is_enabled() or not candidates:
            return []
        
        target_embedding = self.get_embedding(target_text)
        if not target_embedding:
            return []
        
        # Get embeddings for all candidates
        candidate_embeddings = self.get_embeddings_batch(candidates)
        
        # Calculate similarities
        similarities = []
        for candidate in candidates:
            candidate_embedding = candidate_embeddings.get(candidate)
            if candidate_embedding:
                similarity = self.similarity_calc.cosine_similarity(
                    target_embedding, candidate_embedding
                )
                
                if similarity >= threshold:
                    similarities.append({
                        "text": candidate,
                        "similarity": similarity
                    })
        
        # Sort by similarity (highest first) and limit results
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:limit]

    def average_embeddings(self, embeddings: List[List[float]], 
                          weights: Optional[List[float]] = None) -> Optional[List[float]]:
        """Calculate weighted average of embeddings"""
        if not embeddings:
            return None
        
        try:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            if weights:
                if len(weights) != len(embeddings):
                    logger.warning("Weight count doesn't match embedding count, using equal weights")
                    weights = None
                else:
                    weights_array = np.array(weights, dtype=np.float32)
                    weights_array = weights_array / np.sum(weights_array)  # Normalize
                    averaged = np.average(embeddings_array, axis=0, weights=weights_array)
            else:
                averaged = np.mean(embeddings_array, axis=0)
            
            return averaged.tolist()
            
        except Exception as e:
            logger.error(f"Error averaging embeddings: {e}")
            return None

    def get_service_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            "enabled": self.is_enabled(),
            "model_name": self.model_name,
            "cache_stats": self.cache.get_stats(),
            "executor_stats": {
                "max_workers": self._executor._max_workers,
                "active_threads": len(self._executor._threads) if hasattr(self._executor, '_threads') else 0
            }
        }

    def clear_cache(self) -> None:
        """Clear embedding cache"""
        self.cache.clear()
        logger.info("Embedding cache cleared")

    def shutdown(self):
        """Shutdown embedding service and cleanup resources"""
        try:
            self._executor.shutdown(wait=True)
            self.cache.clear()
            logger.info("Embedding service shutdown complete")
        except Exception as e:
            logger.error(f"Error during embedding service shutdown: {e}")