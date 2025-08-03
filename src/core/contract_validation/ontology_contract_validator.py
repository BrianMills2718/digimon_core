"""
Ontology Contract Validator

Validates entity and relationship objects against ontology constraints.
"""

from typing import Dict, List, Any

try:
    from ..ontology_validator import OntologyValidator
    from ..data_models import Entity, Relationship
except ImportError:
    # For standalone execution
    from ontology_validator import OntologyValidator
    from data_models import Entity, Relationship


class OntologyContractValidator:
    """Validates objects against ontology constraints defined in contracts"""
    
    def __init__(self):
        # Initialize ontology validator
        self.ontology_validator = OntologyValidator()
    
    def validate_ontology_constraints(self, obj: Any, validation_rules: Dict[str, Any], 
                                    data_type: str) -> List[str]:
        """Validate object against ontology constraints"""
        errors = []
        
        if data_type == "Entity":
            # Convert to Entity object if it's a dict
            if isinstance(obj, dict):
                try:
                    entity_obj = Entity(**obj)
                except Exception as e:
                    errors.append(f"Failed to convert dict to Entity: {str(e)}")
                    return errors
            else:
                entity_obj = obj
            
            # Validate entity type constraint
            if 'entity_type' in validation_rules:
                constraint = validation_rules['entity_type'].get('constraint')
                if constraint == 'must_exist_in_ontology':
                    entity_errors = self.ontology_validator.validate_entity(entity_obj)
                    errors.extend(entity_errors)
        
        elif data_type == "Relationship":
            # Convert to Relationship object if it's a dict
            if isinstance(obj, dict):
                try:
                    rel_obj = Relationship(**obj)
                except Exception as e:
                    errors.append(f"Failed to convert dict to Relationship: {str(e)}")
                    return errors
            else:
                rel_obj = obj
            
            # Validate relationship type constraint
            if 'relationship_type' in validation_rules:
                constraint = validation_rules['relationship_type'].get('constraint')
                if constraint == 'must_exist_in_ontology':
                    rel_errors = self.ontology_validator.validate_relationship(rel_obj)
                    errors.extend(rel_errors)
        
        return errors
    
    def validate_entity_consistency(self, entities: List[Any]) -> List[str]:
        """Validate consistency across multiple entities"""
        errors = []
        
        # Check for duplicate entities
        seen_entities = set()
        for entity in entities:
            if isinstance(entity, dict):
                canonical_name = entity.get('canonical_name')
                entity_type = entity.get('entity_type')
            else:
                canonical_name = getattr(entity, 'canonical_name', None)
                entity_type = getattr(entity, 'entity_type', None)
            
            if canonical_name and entity_type:
                entity_key = (canonical_name.lower(), entity_type)
                if entity_key in seen_entities:
                    errors.append(f"Duplicate entity found: {canonical_name} ({entity_type})")
                seen_entities.add(entity_key)
        
        return errors
    
    def validate_relationship_consistency(self, relationships: List[Any]) -> List[str]:
        """Validate consistency across multiple relationships"""
        errors = []
        
        # Check for dangling relationships (entities that don't exist)
        entity_refs = set()
        relationship_refs = []
        
        for rel in relationships:
            if isinstance(rel, dict):
                source_ref = rel.get('source_entity_ref')
                target_ref = rel.get('target_entity_ref')
            else:
                source_ref = getattr(rel, 'source_entity_ref', None)
                target_ref = getattr(rel, 'target_entity_ref', None)
            
            if source_ref:
                relationship_refs.append(('source', source_ref))
            if target_ref:
                relationship_refs.append(('target', target_ref))
        
        # Note: This would need access to actual entity references to validate properly
        # For now, just check that references are not empty
        for ref_type, ref_value in relationship_refs:
            if not ref_value or ref_value.strip() == "":
                errors.append(f"Empty {ref_type} entity reference in relationship")
        
        return errors
    
    def validate_ontology_coverage(self, extracted_data: Dict[str, Any], 
                                 coverage_requirements: Dict[str, Any]) -> List[str]:
        """Validate that extracted data meets ontology coverage requirements"""
        errors = []
        
        # Check minimum entity types coverage
        min_entity_types = coverage_requirements.get('min_entity_types', 0)
        if min_entity_types > 0:
            entity_types = set()
            entities = extracted_data.get('entities', [])
            
            for entity in entities:
                if isinstance(entity, dict):
                    entity_type = entity.get('entity_type')
                else:
                    entity_type = getattr(entity, 'entity_type', None)
                
                if entity_type:
                    entity_types.add(entity_type)
            
            if len(entity_types) < min_entity_types:
                errors.append(f"Insufficient entity type coverage: {len(entity_types)} < {min_entity_types}")
        
        # Check minimum relationship types coverage
        min_rel_types = coverage_requirements.get('min_relationship_types', 0)
        if min_rel_types > 0:
            rel_types = set()
            relationships = extracted_data.get('relationships', [])
            
            for rel in relationships:
                if isinstance(rel, dict):
                    rel_type = rel.get('relationship_type')
                else:
                    rel_type = getattr(rel, 'relationship_type', None)
                
                if rel_type:
                    rel_types.add(rel_type)
            
            if len(rel_types) < min_rel_types:
                errors.append(f"Insufficient relationship type coverage: {len(rel_types)} < {min_rel_types}")
        
        return errors
    
    def validate_semantic_consistency(self, extracted_data: Dict[str, Any]) -> List[str]:
        """Validate semantic consistency of extracted data"""
        errors = []
        
        entities = extracted_data.get('entities', [])
        relationships = extracted_data.get('relationships', [])
        
        # Check for semantic conflicts in entity types
        entity_name_types = {}
        for entity in entities:
            if isinstance(entity, dict):
                name = entity.get('canonical_name', '').lower()
                entity_type = entity.get('entity_type')
            else:
                name = getattr(entity, 'canonical_name', '').lower()
                entity_type = getattr(entity, 'entity_type', None)
            
            if name and entity_type:
                if name in entity_name_types and entity_name_types[name] != entity_type:
                    errors.append(f"Semantic conflict: '{name}' classified as both {entity_name_types[name]} and {entity_type}")
                entity_name_types[name] = entity_type
        
        # Check for implausible relationships
        implausible_patterns = [
            ('PERSON', 'CONTAINS', 'ORGANIZATION'),
            ('LOCATION', 'WORKS_FOR', 'PERSON'),
            ('DATE', 'OWNS', 'PERSON')
        ]
        
        for rel in relationships:
            if isinstance(rel, dict):
                rel_type = rel.get('relationship_type')
                # Would need to resolve entity references to get types
            else:
                rel_type = getattr(rel, 'relationship_type', None)
            
            # This is a simplified check - would need full entity resolution
            # for complete validation
        
        return errors
