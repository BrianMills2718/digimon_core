"""
Qdrant Vector Store Implementation

This module provides a Qdrant vector store implementation for compatibility with existing tests.
Note: This is a simplified implementation for test compatibility.
"""

import uuid
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class QdrantConfig:
    """Configuration for Qdrant connection"""
    
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "vectors"):
        self.host = host
        self.port = port  
        self.collection_name = collection_name


class QdrantStore:
    """Simplified Qdrant store implementation for compatibility"""
    
    def __init__(self, config: QdrantConfig = None):
        self.config = config or QdrantConfig()
        self._vectors: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Initialized QdrantStore (mock) with collection: {self.config.collection_name}")
    
    async def add_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Add vectors to the store"""
        try:
            for vector in vectors:
                vector_id = vector.get('id', str(uuid.uuid4()))
                self._vectors[vector_id] = vector
            return True
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            return False
    
    async def search_vectors(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        try:
            # Simplified similarity search - return first 'limit' vectors
            results = list(self._vectors.values())[:limit]
            return results
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by IDs"""
        try:
            for vector_id in ids:
                self._vectors.pop(vector_id, None)
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if the store is healthy"""
        return True
    
    async def close(self):
        """Close the connection"""
        self._vectors.clear()
        logger.info("QdrantStore connection closed")


# Factory function for backward compatibility
def create_qdrant_store(config: QdrantConfig = None) -> QdrantStore:
    """Create a QdrantStore instance"""
    return QdrantStore(config)

class VectorMetadata:
    """Metadata for vector entries"""
    
    def __init__(self, document_id: str = None, chunk_id: str = None, 
                 entity_type: str = None, confidence: float = 1.0, **kwargs):
        self.document_id = document_id
        self.chunk_id = chunk_id
        self.entity_type = entity_type
        self.confidence = confidence
        self.extra = kwargs


class InMemoryVectorStore(QdrantStore):
    """In-memory vector store for testing"""
    
    def __init__(self, config: QdrantConfig = None):
        super().__init__(config)
        logger.info("Initialized InMemoryVectorStore (in-memory implementation)")
    
    async def add_vector_with_metadata(self, vector: List[float], 
                                     metadata: VectorMetadata) -> str:
        """Add vector with metadata"""
        vector_id = str(uuid.uuid4())
        self._vectors[vector_id] = {
            'id': vector_id,
            'vector': vector,
            'metadata': metadata.__dict__
        }
        return vector_id


# Backward compatibility aliases  
QdrantVectorStore = QdrantStore