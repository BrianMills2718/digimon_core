"""
Theory Integration Framework

Unifies theory-guided processing into the main pipeline instead of maintaining
a separate parallel implementation.
"""

from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from .entity_schema import StandardEntity, StandardRelationship
from .logging_config import get_logger

logger = get_logger("core.theory_integration")

class TheoryEnhancer:
    """Enhances tool outputs with theory-guided analysis"""
    
    def __init__(self, concept_library: Dict[str, Any]):
        self.concept_library = concept_library
        
    def enhance_entities(self, entities: List[StandardEntity]) -> List[StandardEntity]:
        """Add theory enhancements to entities during main pipeline execution"""
        enhanced_entities = []
        
        for entity in entities:
            # Find concept match
            concept_match = self._find_best_concept_match(
                entity.canonical_name, 
                entity.entity_type, 
                self.concept_library
            )
            
            # Create enhanced entity
            enhanced_entity = entity.copy(deep=True)
            if concept_match:
                enhanced_entity.theory_metadata = {
                    **enhanced_entity.theory_metadata,
                    "concept_match": concept_match["concept"],
                    "concept_confidence": concept_match["confidence"],
                    "theory_enhanced": True,
                    "concept_description": concept_match.get("description", "")
                }
                
                # Boost confidence for theory-aligned entities
                enhanced_entity.confidence = min(1.0, enhanced_entity.confidence + 0.1)
            else:
                enhanced_entity.theory_metadata = {
                    **enhanced_entity.theory_metadata,
                    "concept_match": None,
                    "concept_confidence": 0.0,
                    "theory_enhanced": False
                }
            
            enhanced_entities.append(enhanced_entity)
        
        return enhanced_entities
    
    def enhance_relationships(self, relationships: List[StandardRelationship], entities: List[StandardEntity]) -> List[StandardRelationship]:
        """Add theory enhancements to relationships during main pipeline execution"""
        enhanced_relationships = []
        
        # Create entity lookup for quick access
        entity_lookup = {entity.entity_id: entity for entity in entities}
        
        for relationship in relationships:
            # Get subject and object entities
            subject_entity = entity_lookup.get(relationship.subject_entity_id)
            object_entity = entity_lookup.get(relationship.object_entity_id)
            
            enhanced_relationship = relationship.copy(deep=True)
            
            if subject_entity and object_entity:
                # Calculate relationship alignment with theory
                alignment_score = self._calculate_relationship_alignment(
                    subject_entity, object_entity, relationship, self.concept_library
                )
                
                enhanced_relationship.theory_metadata = {
                    **enhanced_relationship.theory_metadata,
                    "concept_alignment": alignment_score,
                    "theory_enhanced": alignment_score > 0.5,
                    "predicted_by_theory": alignment_score > 0.7
                }
                
                # Boost confidence for theory-aligned relationships
                if alignment_score > 0.5:
                    enhanced_relationship.confidence = min(1.0, enhanced_relationship.confidence + 0.1)
            
            enhanced_relationships.append(enhanced_relationship)
        
        return enhanced_relationships
    
    def _find_best_concept_match(self, canonical_name: str, entity_type: str, concept_library: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best concept match for an entity"""
        best_match = None
        best_score = 0.0
        
        name_lower = canonical_name.lower()
        type_lower = entity_type.lower()
        
        for concept, info in concept_library.items():
            score = 0.0
            
            # Check if entity type matches concept
            if concept.lower() in type_lower or type_lower in concept.lower():
                score += 0.5
            
            # Check pattern matches
            patterns = info.get("patterns", [])
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    score += 0.3
                    break
            
            # Check direct name match
            if concept.lower() in name_lower:
                score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = {
                    "concept": concept,
                    "confidence": score,
                    "description": info.get("description", "")
                }
        
        return best_match if best_score > 0.3 else None
    
    def _calculate_relationship_alignment(self, subject_entity: StandardEntity, object_entity: StandardEntity, 
                                        relationship: StandardRelationship, concept_library: Dict[str, Any]) -> float:
        """Calculate how well a relationship aligns with concept library patterns"""
        score = 0.0
        
        # Get concept matches for entities
        subject_concept = subject_entity.theory_metadata.get("concept_match")
        object_concept = object_entity.theory_metadata.get("concept_match")
        
        if not subject_concept or not object_concept:
            return 0.0
        
        # Check if relationship type is expected between these concepts
        subject_info = concept_library.get(subject_concept, {})
        expected_relationships = subject_info.get("relationships", [])
        
        predicate_lower = relationship.predicate.lower()
        
        for expected_rel in expected_relationships:
            if expected_rel.lower() in predicate_lower or predicate_lower in expected_rel.lower():
                score += 0.8
                break
        
        # Bonus for high-confidence concept matches
        subject_conf = subject_entity.theory_metadata.get("concept_confidence", 0.0)
        object_conf = object_entity.theory_metadata.get("concept_confidence", 0.0)
        
        score += (subject_conf + object_conf) / 2 * 0.2
        
        return min(1.0, score)

def theory_aware_tool(concept_library: Dict[str, Any]):
    """Decorator to make any tool theory-aware without separate implementation"""
    def decorator(tool_method: Callable):
        @wraps(tool_method)
        def wrapper(self, *args, **kwargs):
            # Execute normal tool logic
            result = tool_method(self, *args, **kwargs)
            
            # Add theory enhancement if enabled
            if hasattr(self, 'config_manager') and self.config_manager.get('theory', {}).get('enabled', False):
                try:
                    enhancer = TheoryEnhancer(concept_library)
                    
                    # Enhance entities if present
                    if 'entities' in result and result['entities']:
                        # Convert to StandardEntity objects
                        from .entity_schema import validate_entity
                        standard_entities = [validate_entity(e) for e in result['entities']]
                        
                        # Apply theory enhancement
                        enhanced_entities = enhancer.enhance_entities(standard_entities)
                        
                        # Convert back to dict format
                        result['entities'] = [e.dict() for e in enhanced_entities]
                        result['theory_enhanced'] = True
                    
                    # Enhance relationships if present  
                    if 'relationships' in result and result['relationships']:
                        from .entity_schema import validate_relationship
                        standard_relationships = [validate_relationship(r) for r in result['relationships']]
                        
                        # Need entities for relationship enhancement
                        if 'entities' in result:
                            standard_entities = [validate_entity(e) for e in result['entities']]
                            enhanced_relationships = enhancer.enhance_relationships(standard_relationships, standard_entities)
                            result['relationships'] = [r.dict() for r in enhanced_relationships]
                    
                except Exception as e:
                    logger.warning(f"Theory enhancement failed, continuing with normal result: {e}")
                    result['theory_enhanced'] = False
            
            return result
        return wrapper
    return decorator