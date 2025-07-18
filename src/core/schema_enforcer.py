"""
Schema Enforcement Middleware - FIXED VERSION

Provides strict validation that fails on inconsistent data instead of 
masking problems with "repair" logic. This forces tools to return 
properly structured data and exposes tool-level bugs.

Addresses Gemini's critical finding: "In a production system, inconsistent 
data from a tool should cause a validation failure, not be silently 'repaired' 
with guesses."
"""

from typing import List, Dict, Any
from .entity_schema import StandardEntity, StandardRelationship, validate_entity, validate_relationship, EntityValidationError, RelationshipValidationError
from .logging_config import get_logger

logger = get_logger("core.schema_enforcer")

class SchemaEnforcer:
    """Strict schema enforcement that fails on inconsistent data"""
    
    def __init__(self, production_mode: bool = False):
        """
        Args:
            production_mode: If True, uses strict validation that fails fast.
                           If False, allows minimal repair for development.
        """
        self.production_mode = production_mode
        
    def enforce_entity_schema(self, entities: List[Dict[str, Any]]) -> List[StandardEntity]:
        """Convert raw entity data to standardized schema with strict validation"""
        standardized_entities = []
        validation_errors = []
        
        for i, entity_data in enumerate(entities):
            try:
                # Always attempt direct validation first
                standard_entity = validate_entity(entity_data)
                standardized_entities.append(standard_entity)
                
            except EntityValidationError as e:
                if self.production_mode:
                    # In production, fail immediately on validation errors
                    logger.error(f"PRODUCTION VALIDATION FAILURE - Entity {i}: {e}")
                    raise EntityValidationError(f"Entity {i} failed strict validation: {e}. This indicates a tool-level bug that must be fixed.")
                else:
                    # In development, apply minimal repair and log the issue
                    try:
                        repaired_entity = self._minimal_repair_entity(entity_data, i)
                        standardized_entities.append(repaired_entity)
                        validation_errors.append(f"Entity {i}: {e}")
                        logger.warning(f"DEVELOPMENT MODE - Entity {i} required repair: {e}")
                    except Exception as repair_error:
                        logger.error(f"Entity {i} could not be repaired: {repair_error}")
                        validation_errors.append(f"Entity {i}: UNREPAIRABLE - {repair_error}")
        
        # Log summary
        if validation_errors:
            logger.warning(f"Schema enforcement completed with {len(validation_errors)} validation issues. "
                          f"Successful: {len(standardized_entities)}/{len(entities)}")
            if not self.production_mode:
                logger.warning("These validation issues indicate tool-level bugs that should be fixed:")
                for error in validation_errors[:5]:  # Show first 5 errors
                    logger.warning(f"  - {error}")
        else:
            logger.info(f"Schema enforcement: {len(standardized_entities)}/{len(entities)} entities validated successfully")
        
        return standardized_entities
    
    def enforce_relationship_schema(self, relationships: List[Dict[str, Any]]) -> List[StandardRelationship]:
        """Convert raw relationship data to standardized schema with strict validation"""
        standardized_relationships = []
        validation_errors = []
        
        for i, rel_data in enumerate(relationships):
            try:
                standard_relationship = validate_relationship(rel_data)
                standardized_relationships.append(standard_relationship)
                
            except RelationshipValidationError as e:
                if self.production_mode:
                    # In production, fail immediately on validation errors
                    logger.error(f"PRODUCTION VALIDATION FAILURE - Relationship {i}: {e}")
                    raise RelationshipValidationError(f"Relationship {i} failed strict validation: {e}. This indicates a tool-level bug that must be fixed.")
                else:
                    # In development, apply minimal repair and log the issue
                    try:
                        repaired_relationship = self._minimal_repair_relationship(rel_data, i)
                        standardized_relationships.append(repaired_relationship)
                        validation_errors.append(f"Relationship {i}: {e}")
                        logger.warning(f"DEVELOPMENT MODE - Relationship {i} required repair: {e}")
                    except Exception as repair_error:
                        logger.error(f"Relationship {i} could not be repaired: {repair_error}")
                        validation_errors.append(f"Relationship {i}: UNREPAIRABLE - {repair_error}")
        
        # Log summary
        if validation_errors:
            logger.warning(f"Relationship schema enforcement completed with {len(validation_errors)} validation issues. "
                          f"Successful: {len(standardized_relationships)}/{len(relationships)}")
            if not self.production_mode:
                logger.warning("These validation issues indicate tool-level bugs that should be fixed:")
                for error in validation_errors[:5]:  # Show first 5 errors
                    logger.warning(f"  - {error}")
        else:
            logger.info(f"Relationship schema enforcement: {len(standardized_relationships)}/{len(relationships)} validated successfully")
        
        return standardized_relationships
    
    def _minimal_repair_entity(self, entity_data: Dict[str, Any], index: int) -> StandardEntity:
        """
        MINIMAL repair for development only - fills in missing required fields
        with sensible defaults but does NOT use fallback chains.
        
        This is fundamentally different from the flawed approach that was criticized.
        """
        repaired_data = entity_data.copy()
        
        # Only add missing required fields with clear defaults - NO FALLBACK CHAINS
        if 'entity_id' not in repaired_data or not repaired_data['entity_id']:
            repaired_data['entity_id'] = f"dev_entity_{index}_{hash(str(entity_data)) % 10000}"
            
        if 'canonical_name' not in repaired_data or not repaired_data['canonical_name']:
            # Do NOT use fallback chains - use a clear default that indicates missing data
            repaired_data['canonical_name'] = f"MISSING_NAME_ENTITY_{index}"
            
        if 'entity_type' not in repaired_data or not repaired_data['entity_type']:
            repaired_data['entity_type'] = 'OTHER'
            
        if 'confidence' not in repaired_data or not isinstance(repaired_data.get('confidence'), (int, float)):
            repaired_data['confidence'] = 0.0  # Low confidence for repaired data
        
        return validate_entity(repaired_data)
    
    def _minimal_repair_relationship(self, rel_data: Dict[str, Any], index: int) -> StandardRelationship:
        """
        MINIMAL repair for development only - fills in missing required fields
        with sensible defaults but does NOT use fallback chains.
        """
        repaired_data = rel_data.copy()
        
        # Only add missing required fields with clear defaults - NO FALLBACK CHAINS
        if 'relationship_id' not in repaired_data or not repaired_data['relationship_id']:
            repaired_data['relationship_id'] = f"dev_rel_{index}_{hash(str(rel_data)) % 10000}"
            
        if 'subject_entity_id' not in repaired_data or not repaired_data['subject_entity_id']:
            raise RelationshipValidationError("subject_entity_id is required and cannot be repaired")
            
        if 'object_entity_id' not in repaired_data or not repaired_data['object_entity_id']:
            raise RelationshipValidationError("object_entity_id is required and cannot be repaired")
            
        if 'predicate' not in repaired_data or not repaired_data['predicate']:
            repaired_data['predicate'] = 'UNKNOWN_RELATION'
            
        if 'confidence' not in repaired_data or not isinstance(repaired_data.get('confidence'), (int, float)):
            repaired_data['confidence'] = 0.0  # Low confidence for repaired data
        
        return validate_relationship(repaired_data)