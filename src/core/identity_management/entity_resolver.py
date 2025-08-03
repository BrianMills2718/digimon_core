"""
Entity Resolution Components

Handles entity matching, linking, and resolution using both exact matching
and semantic similarity approaches.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .data_models import Entity, Mention, EntityId, NormalizedForm
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class ExactMatcher:
    """Handles exact string matching for entity resolution"""
    
    @staticmethod
    def find_exact_match(normalized_form: str, entities: Dict[str, Entity],
                        entity_type: Optional[str] = None) -> Optional[str]:
        """Find entity with exact canonical name match"""
        for entity_id, entity in entities.items():
            # Check if canonical name matches
            if entity.canonical_name == normalized_form:
                # If entity type specified, it must match (or be None)
                if entity_type and entity.entity_type and entity.entity_type != entity_type:
                    continue
                return entity_id
        return None

    @staticmethod
    def find_fuzzy_exact_matches(normalized_form: str, entities: Dict[str, Entity],
                               max_results: int = 5) -> List[Tuple[str, float]]:
        """Find entities with very similar canonical names (case insensitive, etc.)"""
        matches = []
        target_lower = normalized_form.lower().strip()
        
        for entity_id, entity in entities.items():
            entity_name_lower = entity.canonical_name.lower().strip()
            
            if entity_name_lower == target_lower:
                matches.append((entity_id, 1.0))  # Perfect match
            elif target_lower in entity_name_lower or entity_name_lower in target_lower:
                # Calculate simple overlap score
                overlap = len(set(target_lower.split()) & set(entity_name_lower.split()))
                total_words = len(set(target_lower.split()) | set(entity_name_lower.split()))
                score = overlap / total_words if total_words > 0 else 0.0
                if score > 0.5:  # Minimum threshold for fuzzy match
                    matches.append((entity_id, score))
        
        # Sort by score (highest first) and limit results
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:max_results]


class SimilarityMatcher:
    """Handles semantic similarity matching using embeddings"""
    
    def __init__(self, embedding_service: EmbeddingService, 
                 similarity_threshold: float = 0.85):
        """Initialize similarity matcher with embedding service"""
        self.embedding_service = embedding_service
        self.similarity_threshold = similarity_threshold

    def find_similar_entity(self, normalized_form: str, entities: Dict[str, Entity],
                          entity_type: Optional[str] = None) -> Optional[str]:
        """Find most similar entity using semantic embeddings"""
        if not self.embedding_service.is_enabled():
            return None
        
        # Get embedding for target text
        target_embedding = self.embedding_service.get_embedding(normalized_form)
        if not target_embedding:
            return None
        
        best_match_id = None
        best_similarity = 0.0
        
        # Compare with all entities that have embeddings
        for entity_id, entity in entities.items():
            if not entity.embedding:
                continue
            
            # Skip if entity type doesn't match
            if entity_type and entity.entity_type and entity.entity_type != entity_type:
                continue
            
            # Calculate similarity
            similarity = self.embedding_service.similarity_calc.cosine_similarity(
                target_embedding, entity.embedding
            )
            
            if similarity >= self.similarity_threshold and similarity > best_similarity:
                best_match_id = entity_id
                best_similarity = similarity
        
        return best_match_id

    def find_all_similar_entities(self, normalized_form: str, entities: Dict[str, Entity],
                                entity_type: Optional[str] = None,
                                min_threshold: float = 0.7,
                                max_results: int = 10) -> List[Tuple[str, float]]:
        """Find all entities above similarity threshold"""
        if not self.embedding_service.is_enabled():
            return []
        
        target_embedding = self.embedding_service.get_embedding(normalized_form)
        if not target_embedding:
            return []
        
        similar_entities = []
        
        for entity_id, entity in entities.items():
            if not entity.embedding:
                continue
            
            # Skip if entity type doesn't match
            if entity_type and entity.entity_type and entity.entity_type != entity_type:
                continue
            
            similarity = self.embedding_service.similarity_calc.cosine_similarity(
                target_embedding, entity.embedding
            )
            
            if similarity >= min_threshold:
                similar_entities.append((entity_id, similarity))
        
        # Sort by similarity (highest first) and limit results
        similar_entities.sort(key=lambda x: x[1], reverse=True)
        return similar_entities[:max_results]

    def update_similarity_threshold(self, new_threshold: float):
        """Update similarity matching threshold"""
        if 0.0 <= new_threshold <= 1.0:
            self.similarity_threshold = new_threshold
        else:
            logger.warning(f"Invalid similarity threshold: {new_threshold}, keeping current: {self.similarity_threshold}")


class EntityCreator:
    """Handles creation of new entities"""
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """Initialize entity creator"""
        self.embedding_service = embedding_service

    def create_entity_id(self) -> str:
        """Generate unique entity ID"""
        return f"entity_{uuid.uuid4().hex[:8]}"

    def create_entity(self, normalized_form: str, entity_type: Optional[str] = None,
                     confidence: float = 0.8, mention_id: Optional[str] = None) -> Entity:
        """Create new entity with optional embedding"""
        entity_id = self.create_entity_id()
        
        # Get embedding if service is available
        embedding = None
        if self.embedding_service and self.embedding_service.is_enabled():
            embedding = self.embedding_service.get_embedding(normalized_form)
        
        # Create entity
        entity = Entity(
            id=entity_id,
            canonical_name=normalized_form,
            entity_type=entity_type,
            mentions=[mention_id] if mention_id else [],
            confidence=confidence,
            embedding=embedding
        )
        
        return entity

    def enhance_entity_with_embedding(self, entity: Entity) -> bool:
        """Add embedding to existing entity if not present"""
        if entity.embedding or not self.embedding_service:
            return False
        
        if not self.embedding_service.is_enabled():
            return False
        
        embedding = self.embedding_service.get_embedding(entity.canonical_name)
        if embedding:
            entity.embedding = embedding
            return True
        
        return False


class EntityMerger:
    """Handles merging of entities"""
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """Initialize entity merger"""
        self.embedding_service = embedding_service

    def merge_entities(self, entity1: Entity, entity2: Entity) -> Entity:
        """Merge two entities, keeping entity1 as primary"""
        # Merge mentions
        all_mentions = list(set(entity1.mentions + entity2.mentions))
        
        # Calculate weighted confidence
        total_mentions = len(all_mentions)
        entity1_weight = len(entity1.mentions) / total_mentions
        entity2_weight = len(entity2.mentions) / total_mentions
        merged_confidence = (entity1.confidence * entity1_weight + 
                           entity2.confidence * entity2_weight)
        
        # Merge metadata and attributes
        merged_metadata = {**entity1.metadata, **entity2.metadata}
        merged_attributes = {**entity1.attributes, **entity2.attributes}
        
        # Handle embeddings
        merged_embedding = self._merge_embeddings(entity1, entity2, entity1_weight, entity2_weight)
        
        # Update entity1 with merged data
        entity1.mentions = all_mentions
        entity1.confidence = merged_confidence
        entity1.metadata = merged_metadata
        entity1.attributes = merged_attributes
        entity1.embedding = merged_embedding
        
        return entity1

    def _merge_embeddings(self, entity1: Entity, entity2: Entity,
                         weight1: float, weight2: float) -> Optional[List[float]]:
        """Merge embeddings using weighted average"""
        if not entity1.embedding and not entity2.embedding:
            return None
        
        if entity1.embedding and not entity2.embedding:
            return entity1.embedding
        
        if entity2.embedding and not entity1.embedding:
            return entity2.embedding
        
        # Both have embeddings, use embedding service to average them
        if self.embedding_service:
            return self.embedding_service.average_embeddings(
                [entity1.embedding, entity2.embedding],
                [weight1, weight2]
            )
        
        # Simple average if no embedding service
        return [(a * weight1 + b * weight2) for a, b in zip(entity1.embedding, entity2.embedding)]

    def can_merge_entities(self, entity1: Entity, entity2: Entity,
                          similarity_threshold: float = 0.8) -> Tuple[bool, float, str]:
        """Check if two entities can be merged"""
        # Check exact name match
        if entity1.canonical_name == entity2.canonical_name:
            return True, 1.0, "exact_name_match"
        
        # Check entity type compatibility
        if (entity1.entity_type and entity2.entity_type and 
            entity1.entity_type != entity2.entity_type):
            return False, 0.0, "incompatible_types"
        
        # Check semantic similarity if embeddings available
        if entity1.embedding and entity2.embedding and self.embedding_service:
            similarity = self.embedding_service.similarity_calc.cosine_similarity(
                entity1.embedding, entity2.embedding
            )
            
            if similarity >= similarity_threshold:
                return True, similarity, "semantic_similarity"
            else:
                return False, similarity, "insufficient_similarity"
        
        # No clear way to determine merge compatibility
        return False, 0.0, "insufficient_information"


class EntityResolver:
    """Main entity resolution coordinator"""
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None,
                 similarity_threshold: float = 0.85,
                 exact_match_threshold: float = 0.98,
                 related_threshold: float = 0.7):
        """Initialize entity resolver with all matching strategies"""
        self.exact_matcher = ExactMatcher()
        self.similarity_matcher = SimilarityMatcher(embedding_service, similarity_threshold) if embedding_service else None
        self.entity_creator = EntityCreator(embedding_service)
        self.entity_merger = EntityMerger(embedding_service)
        
        self.similarity_threshold = similarity_threshold
        self.exact_match_threshold = exact_match_threshold
        self.related_threshold = related_threshold
        
        self.embedding_service = embedding_service

    def resolve_entity(self, normalized_form: str, entity_type: Optional[str],
                      entities: Dict[str, Entity],
                      mention_id: Optional[str] = None) -> Tuple[str, bool]:
        """Resolve entity using multiple strategies, return (entity_id, was_created)"""
        
        # Try exact match first
        entity_id = self.exact_matcher.find_exact_match(normalized_form, entities, entity_type)
        if entity_id:
            return entity_id, False
        
        # Try semantic similarity if available
        if self.similarity_matcher:
            entity_id = self.similarity_matcher.find_similar_entity(
                normalized_form, entities, entity_type
            )
            if entity_id:
                return entity_id, False
        
        # No match found, create new entity
        new_entity = self.entity_creator.create_entity(
            normalized_form, entity_type, mention_id=mention_id
        )
        entities[new_entity.id] = new_entity
        
        return new_entity.id, True

    def find_related_entities(self, text: str, entities: Dict[str, Entity],
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Find entities semantically related to given text"""
        if not self.similarity_matcher:
            return []
        
        similar_entities = self.similarity_matcher.find_all_similar_entities(
            text, entities, min_threshold=self.related_threshold, max_results=limit
        )
        
        related = []
        for entity_id, similarity in similar_entities:
            entity = entities[entity_id]
            related.append({
                "entity_id": entity.id,
                "canonical_name": entity.canonical_name,
                "entity_type": entity.entity_type,
                "similarity": similarity,
                "confidence": entity.confidence,
                "mention_count": len(entity.mentions)
            })
        
        return related

    def suggest_entity_merges(self, entities: Dict[str, Entity],
                            min_similarity: float = 0.9) -> List[Dict[str, Any]]:
        """Suggest entity pairs that might be merged"""
        if not self.similarity_matcher:
            return []
        
        suggestions = []
        entity_ids = list(entities.keys())
        
        # Compare all entity pairs
        for i, entity_id1 in enumerate(entity_ids):
            for entity_id2 in entity_ids[i+1:]:
                entity1 = entities[entity_id1]
                entity2 = entities[entity_id2]
                
                can_merge, similarity, reason = self.entity_merger.can_merge_entities(
                    entity1, entity2, min_similarity
                )
                
                if can_merge:
                    suggestions.append({
                        "entity1_id": entity_id1,
                        "entity1_name": entity1.canonical_name,
                        "entity2_id": entity_id2,
                        "entity2_name": entity2.canonical_name,
                        "similarity": similarity,
                        "reason": reason,
                        "combined_mentions": len(entity1.mentions) + len(entity2.mentions)
                    })
        
        # Sort by similarity (highest first)
        suggestions.sort(key=lambda x: x["similarity"], reverse=True)
        return suggestions

    def get_resolution_stats(self, entities: Dict[str, Entity]) -> Dict[str, Any]:
        """Get entity resolution statistics"""
        total_entities = len(entities)
        entities_with_embeddings = sum(1 for e in entities.values() if e.embedding)
        
        # Count entities by type
        type_counts = {}
        for entity in entities.values():
            entity_type = entity.entity_type or "unknown"
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        return {
            "total_entities": total_entities,
            "entities_with_embeddings": entities_with_embeddings,
            "embedding_coverage": entities_with_embeddings / total_entities if total_entities > 0 else 0,
            "similarity_matching_enabled": self.similarity_matcher is not None,
            "similarity_threshold": self.similarity_threshold,
            "exact_match_threshold": self.exact_match_threshold,
            "related_threshold": self.related_threshold,
            "entity_types": type_counts
        }