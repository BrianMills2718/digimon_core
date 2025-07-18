"""Vector Store Interface for GraphRAG System

This module provides the abstract interface for vector storage systems
and implementations for persistent vector storage as required by CLAUDE.md.

CRITICAL IMPLEMENTATION: Addresses missing persistent vector storage functionality
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum


class VectorDistance(Enum):
    """Distance metrics for vector similarity"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


@dataclass
class VectorMetadata:
    """Metadata associated with a vector"""
    text: str
    chunk_id: Optional[str] = None
    document_id: Optional[str] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    workflow_id: Optional[str] = None
    timestamp: Optional[str] = None
    confidence: Optional[float] = None
    additional_metadata: Optional[Dict[str, Any]] = None


@dataclass
class VectorSearchResult:
    """Result of a vector similarity search"""
    id: str
    score: float
    vector: Optional[np.ndarray] = None
    metadata: Optional[VectorMetadata] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "score": self.score,
            "vector": self.vector.tolist() if self.vector is not None else None,
            "metadata": self.metadata.__dict__ if self.metadata else None
        }


class VectorStore(ABC):
    """Abstract interface for vector storage systems"""
    
    @abstractmethod
    def add_vectors(self, vectors: List[np.ndarray], metadata: List[VectorMetadata]) -> List[str]:
        """Add vectors with metadata to the store
        
        Args:
            vectors: List of numpy arrays representing vectors
            metadata: List of VectorMetadata objects
            
        Returns:
            List of vector IDs assigned to the stored vectors
        """
        pass
    
    @abstractmethod
    def search_similar(self, query_vector: np.ndarray, k: int = 10, 
                      filter_criteria: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        """Search for similar vectors
        
        Args:
            query_vector: Query vector as numpy array
            k: Number of results to return
            filter_criteria: Optional metadata filters
            
        Returns:
            List of VectorSearchResult objects
        """
        pass
    
    @abstractmethod
    def get_vector(self, vector_id: str) -> Optional[VectorSearchResult]:
        """Retrieve a specific vector by ID
        
        Args:
            vector_id: ID of the vector to retrieve
            
        Returns:
            VectorSearchResult or None if not found
        """
        pass
    
    @abstractmethod
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by ID
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def update_vector_metadata(self, vector_id: str, metadata: VectorMetadata) -> bool:
        """Update metadata for a vector
        
        Args:
            vector_id: ID of the vector to update
            metadata: New metadata
            
        Returns:
            True if update was successful
        """
        pass
    
    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector collection
        
        Returns:
            Dictionary with collection statistics
        """
        pass
    
    @abstractmethod
    def initialize_collection(self, vector_dimension: int, 
                            distance_metric: VectorDistance = VectorDistance.COSINE) -> bool:
        """Initialize the vector collection
        
        Args:
            vector_dimension: Dimension of vectors to store
            distance_metric: Distance metric to use
            
        Returns:
            True if initialization was successful
        """
        pass


class VectorStoreError(Exception):
    """Base exception for vector store operations"""
    pass


class VectorStoreConnectionError(VectorStoreError):
    """Exception raised when vector store connection fails"""
    pass


class VectorStoreOperationError(VectorStoreError):
    """Exception raised when vector store operation fails"""
    pass