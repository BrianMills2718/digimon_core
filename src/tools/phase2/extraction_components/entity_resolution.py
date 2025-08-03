"""Entity Resolution Component (<200 lines)

Handles entity creation, mention management, and ontology validation.
Provides entity resolution and linking functionality.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EntityResolver:
    """Resolves and creates entities with ontology validation."""
    
    def __init__(self, identity_service=None):
        """Initialize entity resolver."""
        self.identity_service = identity_service
        self.entity_cache = {}
        self.mention_cache = {}
        
    def create_mention(self, surface_text: str, entity_type: str, source_ref: str,
                      confidence: float = 0.8, context: str = "") -> 'Mention':
        """Create a mention with validation."""
        try:
            # Validate inputs
            if not surface_text or not surface_text.strip():
                raise ValueError("Surface text cannot be empty")
            
            if not entity_type:
                raise ValueError("Entity type is required")
            
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("Confidence must be between 0.0 and 1.0")
            
            # Create mention through identity service
            if self.identity_service:
                mention_result = self.identity_service.create_mention(
                    surface_form=surface_text.strip(),
                    start_pos=0,  # Position would be set by caller
                    end_pos=len(surface_text.strip()),
                    source_ref=source_ref,
                    entity_type=entity_type,
                    confidence=confidence
                )
                
                # Handle identity service returning result dict instead of object
                if isinstance(mention_result, dict) and mention_result.get('status') == 'success':
                    # Create proper Mention object from result dict
                    mention = self._create_mention_from_result(
                        mention_result, surface_text, entity_type, source_ref, confidence, context
                    )
                else:
                    # Assume it's already a Mention object (backward compatibility)
                    mention = mention_result
            else:
                # Fallback mention creation
                mention = self._create_fallback_mention(
                    surface_text, entity_type, source_ref, confidence, context
                )
            
            # Cache mention
            self.mention_cache[mention.id] = mention
            
            logger.debug(f"Created mention: {mention.id} for '{surface_text}' as {entity_type}")
            return mention
            
        except Exception as e:
            logger.error(f"Failed to create mention for '{surface_text}': {e}")
            raise
    
    def resolve_or_create_entity(self, surface_text: str, entity_type: str, 
                               ontology: 'DomainOntology', confidence: float = 0.8) -> 'Entity':
        """Resolve existing entity or create new one."""
        try:
            # Create entity key for deduplication
            entity_key = f"{surface_text.lower()}_{entity_type}"
            
            # Check cache first
            if entity_key in self.entity_cache:
                cached_entity = self.entity_cache[entity_key]
                # Update confidence if higher
                if confidence > cached_entity.confidence:
                    cached_entity.confidence = confidence
                return cached_entity
            
            # Validate entity type against ontology
            if not self._is_valid_entity_type(entity_type, ontology):
                logger.warning(f"Invalid entity type '{entity_type}' for ontology '{ontology.domain_name}'")
                # Still create entity but mark as unvalidated
            
            # Create entity through identity service
            if self.identity_service:
                entity_result = self.identity_service.find_or_create_entity(
                    mention_text=surface_text.strip(),
                    entity_type=entity_type,
                    confidence=confidence,
                    context=f"ontology_domain={ontology.domain_name}"
                )
                
                # Handle identity service returning result dict
                if isinstance(entity_result, dict) and 'entity_id' in entity_result:
                    # Create Entity object from result dict
                    entity = self._create_entity_from_result(
                        entity_result, surface_text, entity_type, confidence, ontology
                    )
                else:
                    # Assume it's already an Entity object (fallback for compatibility)
                    entity = entity_result
                    if hasattr(entity, 'confidence'):
                        entity.confidence = confidence
            else:
                # Fallback entity creation
                entity = self._create_fallback_entity(
                    surface_text, entity_type, confidence, ontology
                )
            
            # Cache entity
            self.entity_cache[entity_key] = entity
            
            logger.debug(f"Created entity: {entity.id} for '{surface_text}' as {entity_type}")
            return entity
            
        except Exception as e:
            logger.error(f"Failed to resolve/create entity for '{surface_text}': {e}")
            raise
    
    def link_mention_to_entity(self, mention_id: str, entity_id: str) -> bool:
        """Link a mention to an entity."""
        try:
            if self.identity_service:
                self.identity_service.link_mention_to_entity(mention_id, entity_id)
            
            logger.debug(f"Linked mention {mention_id} to entity {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to link mention {mention_id} to entity {entity_id}: {e}")
            return False
    
    def validate_entity_against_ontology(self, entity: 'Entity', 
                                       ontology: 'DomainOntology') -> Dict[str, Any]:
        """Validate entity against ontology constraints."""
        validation_result = {
            'is_valid': True,
            'validation_errors': [],
            'validation_warnings': [],
            'ontology_coverage': 0.0
        }
        
        try:
            # Check entity type validity
            if not self._is_valid_entity_type(entity.entity_type, ontology):
                validation_result['is_valid'] = False
                validation_result['validation_errors'].append(
                    f"Entity type '{entity.entity_type}' not found in ontology"
                )
            
            # Check required attributes
            entity_type_def = self._get_entity_type_definition(entity.entity_type, ontology)
            if entity_type_def:
                required_attrs = set(entity_type_def.attributes)
                entity_attrs = set(entity.attributes.keys())
                
                missing_attrs = required_attrs - entity_attrs
                if missing_attrs:
                    validation_result['validation_warnings'].append(
                        f"Missing recommended attributes: {', '.join(missing_attrs)}"
                    )
                
                # Calculate ontology coverage
                if required_attrs:
                    coverage = len(entity_attrs & required_attrs) / len(required_attrs)
                    validation_result['ontology_coverage'] = coverage
            
            # Check confidence threshold
            if entity.confidence < 0.5:
                validation_result['validation_warnings'].append(
                    f"Low confidence score: {entity.confidence}"
                )
            
            logger.debug(f"Validated entity {entity.id}: valid={validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Entity validation failed for {entity.id}: {e}")
            validation_result['is_valid'] = False
            validation_result['validation_errors'].append(f"Validation error: {str(e)}")
            return validation_result
    
    def _is_valid_entity_type(self, entity_type: str, ontology: 'DomainOntology') -> bool:
        """Check if entity type is valid in ontology."""
        valid_types = {et.name for et in ontology.entity_types}
        return entity_type in valid_types
    
    def _is_valid_relationship_type(self, relationship_type: str, ontology: 'DomainOntology') -> bool:
        """Check if relationship type is valid in ontology."""
        valid_types = {rt.name for rt in ontology.relationship_types}
        return relationship_type in valid_types
    
    def _get_entity_type_definition(self, entity_type: str, ontology: 'DomainOntology'):
        """Get entity type definition from ontology."""
        for et in ontology.entity_types:
            if et.name == entity_type:
                return et
        return None
    
    def _create_entity_from_result(self, entity_result: dict, surface_text: str, 
                                  entity_type: str, confidence: float, ontology: 'DomainOntology') -> 'Entity':
        """Create Entity object from identity service result dict."""
        from src.core.identity_service import Entity
        
        entity = Entity(
            id=entity_result['entity_id'],
            canonical_name=entity_result['canonical_name'],
            entity_type=entity_type,
            confidence=confidence,
            created_at=datetime.now(),
            attributes={
                'ontology_domain': ontology.domain_name,
                'extraction_method': 'ontology_aware',
                'action': entity_result.get('action', 'unknown')
            }
        )
        
        return entity
    
    def _create_mention_from_result(self, mention_result: dict, surface_text: str, 
                                   entity_type: str, source_ref: str, confidence: float, context: str) -> 'Mention':
        """Create Mention object from identity service result dict."""
        from src.core.identity_service import Mention
        
        mention = Mention(
            id=mention_result['mention_id'],
            surface_form=surface_text.strip(),
            normalized_form=mention_result.get('normalized_form', surface_text.strip().lower()),
            start_pos=0,
            end_pos=len(surface_text.strip()),
            source_ref=source_ref,
            entity_type=entity_type,
            confidence=confidence,
            context=context,
            created_at=datetime.now()
        )
        
        return mention
    
    def _create_fallback_mention(self, surface_text: str, entity_type: str, 
                                source_ref: str, confidence: float, context: str) -> 'Mention':
        """Create fallback mention when identity service is not available."""
        from src.core.identity_service import Mention
        
        mention = Mention(
            id=f"mention_{uuid.uuid4().hex[:8]}",
            surface_form=surface_text.strip(),
            normalized_form=surface_text.strip().lower(),
            start_pos=0,
            end_pos=len(surface_text.strip()),
            source_ref=source_ref,
            entity_type=entity_type,
            confidence=confidence,
            context=context,
            created_at=datetime.now()
        )
        
        return mention
    
    def _create_fallback_entity(self, surface_text: str, entity_type: str, 
                               confidence: float, ontology: 'DomainOntology') -> 'Entity':
        """Create fallback entity when identity service is not available."""
        from src.core.identity_service import Entity
        
        entity = Entity(
            id=f"entity_{uuid.uuid4().hex[:8]}",
            canonical_name=surface_text.strip(),
            entity_type=entity_type,
            confidence=confidence,
            created_at=datetime.now(),
            attributes={
                'ontology_domain': ontology.domain_name,
                'extraction_method': 'ontology_aware',
                'fallback_creation': True,
                'validation_status': 'unvalidated'
            }
        )
        
        return entity
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about resolved entities."""
        return {
            'total_entities': len(self.entity_cache),
            'total_mentions': len(self.mention_cache),
            'entity_types': self._get_entity_type_distribution(),
            'confidence_distribution': self._get_confidence_distribution()
        }
    
    def _get_entity_type_distribution(self) -> Dict[str, int]:
        """Get distribution of entity types."""
        type_counts = {}
        for entity in self.entity_cache.values():
            entity_type = entity.entity_type
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    def _get_confidence_distribution(self) -> Dict[str, int]:
        """Get distribution of confidence scores."""
        confidence_ranges = {
            '0.0-0.3': 0,
            '0.3-0.5': 0, 
            '0.5-0.7': 0,
            '0.7-0.9': 0,
            '0.9-1.0': 0
        }
        
        for entity in self.entity_cache.values():
            conf = entity.confidence
            if conf < 0.3:
                confidence_ranges['0.0-0.3'] += 1
            elif conf < 0.5:
                confidence_ranges['0.3-0.5'] += 1
            elif conf < 0.7:
                confidence_ranges['0.5-0.7'] += 1
            elif conf < 0.9:
                confidence_ranges['0.7-0.9'] += 1
            else:
                confidence_ranges['0.9-1.0'] += 1
        
        return confidence_ranges
    
    def clear_cache(self):
        """Clear entity and mention caches."""
        self.entity_cache.clear()
        self.mention_cache.clear()
        logger.debug("Cleared entity and mention caches")


class RelationshipResolver:
    """Resolves and creates relationships between entities."""
    
    def __init__(self):
        """Initialize relationship resolver."""
        self.relationship_cache = {}
    
    def create_relationship(self, source_entity_id: str, target_entity_id: str,
                          relationship_type: str, confidence: float = 0.8,
                          context: str = "", source_ref: str = "") -> 'Relationship':
        """Create a relationship between entities."""
        try:
            from src.core.identity_service import Relationship
            
            # Validate inputs
            if not source_entity_id or not target_entity_id:
                raise ValueError("Source and target entity IDs are required")
            
            if not relationship_type:
                raise ValueError("Relationship type is required")
            
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("Confidence must be between 0.0 and 1.0")
            
            # Create relationship
            relationship = Relationship(
                id=f"rel_{uuid.uuid4().hex[:8]}",
                source_id=source_entity_id,
                target_id=target_entity_id,
                relationship_type=relationship_type,
                confidence=confidence,
                attributes={
                    'context': context,
                    'source_ref': source_ref,
                    'extraction_method': 'ontology_aware',
                    'created_at': datetime.now().isoformat()
                }
            )
            
            # Cache relationship
            rel_key = f"{source_entity_id}_{target_entity_id}_{relationship_type}"
            self.relationship_cache[rel_key] = relationship
            
            logger.debug(f"Created relationship: {relationship.id} ({relationship_type})")
            return relationship
            
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            raise
    
    def validate_relationship_against_ontology(self, relationship: 'Relationship',
                                             ontology: 'DomainOntology') -> Dict[str, Any]:
        """Validate relationship against ontology constraints."""
        validation_result = {
            'is_valid': True,
            'validation_errors': [],
            'validation_warnings': []
        }
        
        try:
            # Check relationship type validity
            valid_rel_types = {rt.name for rt in ontology.relationship_types}
            if relationship.relationship_type not in valid_rel_types:
                validation_result['is_valid'] = False
                validation_result['validation_errors'].append(
                    f"Relationship type '{relationship.relationship_type}' not found in ontology"
                )
            
            # Additional validation could include:
            # - Source/target entity type compatibility
            # - Domain-specific constraints
            # - Confidence thresholds
            
            logger.debug(f"Validated relationship {relationship.id}: valid={validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Relationship validation failed for {relationship.id}: {e}")
            validation_result['is_valid'] = False
            validation_result['validation_errors'].append(f"Validation error: {str(e)}")
            return validation_result
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get statistics about resolved relationships."""
        return {
            'total_relationships': len(self.relationship_cache),
            'relationship_types': self._get_relationship_type_distribution(),
            'confidence_distribution': self._get_relationship_confidence_distribution()
        }
    
    def _get_relationship_type_distribution(self) -> Dict[str, int]:
        """Get distribution of relationship types."""
        type_counts = {}
        for rel in self.relationship_cache.values():
            rel_type = rel.relationship_type
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts
    
    def _get_relationship_confidence_distribution(self) -> Dict[str, int]:
        """Get distribution of relationship confidence scores."""
        confidence_ranges = {
            '0.0-0.3': 0,
            '0.3-0.5': 0,
            '0.5-0.7': 0, 
            '0.7-0.9': 0,
            '0.9-1.0': 0
        }
        
        for rel in self.relationship_cache.values():
            conf = rel.confidence
            if conf < 0.3:
                confidence_ranges['0.0-0.3'] += 1
            elif conf < 0.5:
                confidence_ranges['0.3-0.5'] += 1
            elif conf < 0.7:
                confidence_ranges['0.5-0.7'] += 1
            elif conf < 0.9:
                confidence_ranges['0.7-0.9'] += 1
            else:
                confidence_ranges['0.9-1.0'] += 1
        
        return confidence_ranges
    
    def clear_cache(self):
        """Clear relationship cache."""
        self.relationship_cache.clear()
        logger.debug("Cleared relationship cache")