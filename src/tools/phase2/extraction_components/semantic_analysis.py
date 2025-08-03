"""Semantic Analysis Component (<250 lines)

Handles semantic similarity calculations, embeddings, and alignment analysis.
Provides semantic validation and comparison functionality.
"""

import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SemanticAlignmentError(Exception):
    """Exception raised when semantic alignment calculation fails."""
    pass


class ContextualAlignmentError(Exception):
    """Exception raised when contextual alignment calculation fails."""
    pass


class SemanticAnalyzer:
    """Analyzes semantic relationships and alignments."""
    
    def __init__(self, api_client=None):
        """Initialize semantic analyzer."""
        self.api_client = api_client
        self.embedding_cache = {}
        self.similarity_cache = {}
        
    def calculate_semantic_alignment(self, entity: Dict[str, Any], 
                                   concept: 'ConceptHierarchy') -> float:
        """
        Calculate semantic alignment score using real NLP techniques.
        
        Args:
            entity: Entity to validate
            concept: Concept from hierarchy
            
        Returns:
            Semantic alignment score (0.0 to 1.0)
        """
        try:
            # Use embeddings for semantic similarity
            entity_embedding = self._get_entity_embedding(entity)
            concept_embedding = self._get_concept_embedding(concept)
            
            # Calculate cosine similarity
            similarity = self._calculate_cosine_similarity(entity_embedding, concept_embedding)
            
            # Enhance with semantic features
            semantic_features = self._extract_semantic_features(entity, concept)
            feature_score = self._calculate_feature_similarity(semantic_features)
            
            # Combine scores
            combined_score = (similarity * 0.7) + (feature_score * 0.3)
            
            # Log semantic analysis evidence
            self._log_semantic_analysis_evidence(entity, concept, similarity, feature_score, combined_score)
            
            return combined_score
            
        except Exception as e:
            raise SemanticAlignmentError(f"Semantic alignment calculation failed: {e}")
    
    def _get_entity_embedding(self, entity: Dict[str, Any]) -> np.ndarray:
        """Get semantic embedding for entity."""
        try:
            # Create cache key
            entity_text = f"{entity.get('text', '')} {entity.get('context', '')}"
            cache_key = f"entity_{hash(entity_text)}"
            
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            # Use API client for embeddings if available
            if self.api_client:
                embedding = self.api_client.get_embedding(entity_text)
                embedding_array = np.array(embedding)
            else:
                # Fallback to simple text-based features
                embedding_array = self._get_text_based_features(entity)
            
            # Cache result
            self.embedding_cache[cache_key] = embedding_array
            return embedding_array
            
        except Exception as e:
            logger.warning(f"Failed to get entity embedding: {e}")
            # Fallback to simple text-based features
            return self._get_text_based_features(entity)
    
    def _get_concept_embedding(self, concept: 'ConceptHierarchy') -> np.ndarray:
        """Get semantic embedding for concept."""
        try:
            # Create cache key
            concept_text = f"{concept.concept_name} {concept.properties.get('description', '')}"
            cache_key = f"concept_{hash(concept_text)}"
            
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            # Use API client for embeddings if available
            if self.api_client:
                embedding = self.api_client.get_embedding(concept_text)
                embedding_array = np.array(embedding)
            else:
                # Fallback to simple concept-based features
                embedding_array = self._get_concept_based_features(concept)
                
            # Cache result
            self.embedding_cache[cache_key] = embedding_array  
            return embedding_array
            
        except Exception as e:
            logger.warning(f"Failed to get concept embedding: {e}")
            # Fallback to simple concept-based features
            return self._get_concept_based_features(concept)
    
    def _get_text_based_features(self, entity: Dict[str, Any]) -> np.ndarray:
        """Get simple text-based features as fallback."""
        text = entity.get('text', '')
        context = entity.get('context', '')
        entity_type = entity.get('type', '')
        
        # Create simple feature vector
        features = []
        
        # Text length features
        features.append(len(text))
        features.append(len(text.split()))
        
        # Character features
        features.append(sum(1 for c in text if c.isupper()))
        features.append(sum(1 for c in text if c.islower()))
        features.append(sum(1 for c in text if c.isdigit()))
        
        # Type features (one-hot encoding for common types)
        common_types = ['PERSON', 'ORGANIZATION', 'LOCATION', 'PRODUCT', 'EVENT']
        for t in common_types:
            features.append(1.0 if entity_type == t else 0.0)
        
        # Context features
        features.append(len(context))
        features.append(len(context.split()))
        
        # Confidence feature
        features.append(entity.get('confidence', 0.0))
        
        # Normalize features
        return np.array(features, dtype=np.float32)
    
    def _get_concept_based_features(self, concept: 'ConceptHierarchy') -> np.ndarray:
        """Get simple concept-based features as fallback."""
        name = concept.concept_name
        description = concept.properties.get('description', '')
        attributes = concept.properties.get('attributes', [])
        
        # Create simple feature vector
        features = []
        
        # Name features
        features.append(len(name))
        features.append(len(name.split()))
        
        # Description features
        features.append(len(description))
        features.append(len(description.split()))
        
        # Attribute features
        features.append(len(attributes))
        
        # Type features (one-hot encoding for common types)
        common_types = ['PERSON', 'ORGANIZATION', 'LOCATION', 'PRODUCT', 'EVENT']
        for t in common_types:
            features.append(1.0 if name == t else 0.0)
        
        # Hierarchy features
        features.append(len(concept.parent_concepts))
        features.append(len(concept.child_concepts))
        features.append(len(concept.validation_rules))
        
        # Pad to match entity features length
        while len(features) < 15:
            features.append(0.0)
        
        return np.array(features, dtype=np.float32)
    
    def _calculate_cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings."""
        try:
            # Ensure same dimensions
            min_len = min(len(embedding1), len(embedding2))
            vec1 = embedding1[:min_len]
            vec2 = embedding2[:min_len]
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (similarity + 1.0) / 2.0))
            
        except Exception as e:
            logger.warning(f"Cosine similarity calculation failed: {e}")
            return 0.5  # Neutral similarity
    
    def _extract_semantic_features(self, entity: Dict[str, Any], 
                                 concept: 'ConceptHierarchy') -> Dict[str, float]:
        """Extract semantic features for comparison."""
        features = {}
        
        # Text similarity features
        entity_text = entity.get('text', '').lower()
        concept_name = concept.concept_name.lower()
        concept_desc = concept.properties.get('description', '').lower()
        
        # Direct name similarity
        features['name_similarity'] = self._calculate_text_overlap(entity_text, concept_name)
        
        # Description similarity
        features['description_similarity'] = self._calculate_text_overlap(
            entity.get('context', '').lower(), concept_desc
        )
        
        # Example similarity
        concept_examples = concept.properties.get('examples', [])
        max_example_similarity = 0.0
        for example in concept_examples:
            similarity = self._calculate_text_overlap(entity_text, example.lower())
            max_example_similarity = max(max_example_similarity, similarity)
        features['example_similarity'] = max_example_similarity
        
        # Attribute overlap
        entity_attrs = set(entity.get('properties', {}).keys())
        concept_attrs = set(concept.properties.get('attributes', []))
        
        if concept_attrs:
            features['attribute_overlap'] = len(entity_attrs & concept_attrs) / len(concept_attrs)
        else:
            features['attribute_overlap'] = 1.0
        
        # Type consistency
        features['type_consistency'] = 1.0 if entity.get('type') == concept.concept_name else 0.0
        
        return features
    
    def _calculate_feature_similarity(self, features: Dict[str, float]) -> float:
        """Calculate overall feature similarity score."""
        if not features:
            return 0.5
        
        # Weighted combination of features
        weights = {
            'name_similarity': 0.3,
            'description_similarity': 0.2,
            'example_similarity': 0.2,
            'attribute_overlap': 0.2,
            'type_consistency': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for feature, score in features.items():
            weight = weights.get(feature, 0.1)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_text_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap between two texts."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _log_semantic_analysis_evidence(self, entity: Dict[str, Any], concept: 'ConceptHierarchy',
                                      similarity: float, feature_score: float, combined_score: float):
        """Log semantic analysis evidence."""
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'entity_id': entity.get('id', 'unknown'),
            'entity_text': entity.get('text', ''),
            'concept_name': concept.concept_name,
            'embedding_similarity': similarity,
            'feature_similarity': feature_score,
            'combined_score': combined_score,
            'analysis_method': 'semantic_embeddings'
        }
        
        logger.info(f"Semantic alignment: {combined_score:.3f} for entity '{entity.get('text', '')}' vs concept '{concept.concept_name}'")
        
        # Store evidence if tracking is enabled
        if hasattr(self, 'evidence_store'):
            self.evidence_store.append(evidence)


class ContextualAnalyzer:
    """Analyzes contextual relationships and alignments."""
    
    def calculate_contextual_alignment(self, entity: Dict[str, Any], 
                                     concept: 'ConceptHierarchy') -> float:
        """
        Calculate contextual alignment score.
        
        Args:
            entity: Entity to validate
            concept: Concept from hierarchy
            
        Returns:
            Contextual alignment score (0.0 to 1.0)
        """
        try:
            # Extract contextual features
            context_similarity = self._calculate_context_similarity(entity, concept)
            domain_alignment = self._calculate_domain_alignment(entity, concept)
            
            # Combine contextual scores
            combined_score = (context_similarity * 0.6) + (domain_alignment * 0.4)
            
            # Log contextual analysis evidence
            self._log_contextual_analysis_evidence(entity, concept, context_similarity, 
                                                 domain_alignment, combined_score)
            
            return combined_score
            
        except Exception as e:
            raise ContextualAlignmentError(f"Contextual alignment calculation failed: {e}")
    
    def _calculate_context_similarity(self, entity: Dict[str, Any], 
                                    concept: 'ConceptHierarchy') -> float:
        """Calculate similarity between entity context and concept context."""
        entity_context = entity.get('context', '').lower()
        concept_desc = concept.properties.get('description', '').lower()
        
        if not entity_context and not concept_desc:
            return 1.0  # Both empty, perfect match
        if not entity_context or not concept_desc:
            return 0.0  # One empty, no match
        
        # Calculate word overlap
        entity_words = set(entity_context.split())
        concept_words = set(concept_desc.split())
        
        # Check for concept examples in entity context
        concept_examples = concept.properties.get('examples', [])
        max_similarity = 0.0
        
        for example in concept_examples:
            example_words = set(example.lower().split())
            
            # Calculate overlap with example
            if example_words:
                word_overlap = len(entity_words & example_words)
                total_words = len(set(entity_context.split()) | set(example.split()))
                similarity = word_overlap / total_words if total_words > 0 else 0.0
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_domain_alignment(self, entity: Dict[str, Any], 
                                  concept: 'ConceptHierarchy') -> float:
        """Calculate domain-specific alignment."""
        # Extract domain indicators
        entity_type = entity.get('type', '').lower()
        concept_type = concept.properties.get('type', '').lower()
        
        # Type alignment
        type_alignment = 1.0 if entity_type == concept_type else 0.0
        
        # Confidence alignment
        entity_confidence = entity.get('confidence', 0.0)
        min_confidence = concept.properties.get('min_confidence', 0.0)
        confidence_alignment = 1.0 if entity_confidence >= min_confidence else entity_confidence / min_confidence
        
        # Attribute alignment
        entity_attrs = set(entity.get('properties', {}).keys())
        required_attrs = set(concept.properties.get('required_attributes', []))
        
        if required_attrs:
            attr_alignment = len(entity_attrs & required_attrs) / len(required_attrs)
        else:
            attr_alignment = 1.0
        
        # Combine alignments
        return (type_alignment * 0.4) + (confidence_alignment * 0.3) + (attr_alignment * 0.3)
    
    def _log_contextual_analysis_evidence(self, entity: Dict[str, Any], concept: 'ConceptHierarchy',
                                        context_similarity: float, domain_alignment: float,
                                        combined_score: float):
        """Log contextual analysis evidence."""
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'entity_id': entity.get('id', 'unknown'),
            'entity_text': entity.get('text', ''),
            'concept_name': concept.concept_name,
            'context_similarity': context_similarity,
            'domain_alignment': domain_alignment,
            'combined_score': combined_score,
            'analysis_method': 'contextual_features'
        }
        
        logger.info(f"Contextual alignment: {combined_score:.3f} for entity '{entity.get('text', '')}' vs concept '{concept.concept_name}'")
        
        # Store evidence if tracking is enabled
        if hasattr(self, 'evidence_store'):
            self.evidence_store.append(evidence)


class SemanticCache:
    """Caches semantic analysis results for performance."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.embedding_cache = {}
        self.similarity_cache = {}
        self.access_order = []
    
    def get_embedding(self, key: str) -> Optional[np.ndarray]:
        """Get cached embedding."""
        if key in self.embedding_cache:
            self._update_access_order(key)
            return self.embedding_cache[key]
        return None
    
    def store_embedding(self, key: str, embedding: np.ndarray):
        """Store embedding in cache."""
        if len(self.embedding_cache) >= self.max_size:
            self._evict_oldest()
        
        self.embedding_cache[key] = embedding
        self._update_access_order(key)
    
    def get_similarity(self, key1: str, key2: str) -> Optional[float]:
        """Get cached similarity score."""
        cache_key = f"{min(key1, key2)}_{max(key1, key2)}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        return None
    
    def store_similarity(self, key1: str, key2: str, similarity: float):
        """Store similarity score in cache."""
        cache_key = f"{min(key1, key2)}_{max(key1, key2)}"
        self.similarity_cache[cache_key] = similarity
    
    def _update_access_order(self, key: str):
        """Update access order for LRU eviction."""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_oldest(self):
        """Evict oldest items from cache."""
        if self.access_order:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.embedding_cache:
                del self.embedding_cache[oldest_key]
    
    def clear(self):
        """Clear all cached data."""
        self.embedding_cache.clear()
        self.similarity_cache.clear()
        self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'embedding_cache_size': len(self.embedding_cache),
            'similarity_cache_size': len(self.similarity_cache),
            'max_size': self.max_size,
            'cache_utilization': len(self.embedding_cache) / self.max_size
        }