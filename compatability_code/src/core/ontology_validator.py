"""Ontology Validator - Validates data models against the Master Concept Library

This module provides validation functions that ensure entities and relationships
conform to the master concept definitions.
"""

from typing import List, Dict, Any, Optional, Union
from ..ontology_library.ontology_service import OntologyService
from .data_models import Entity, Relationship, BaseObject


class OntologyValidator:
    """Validates data objects against the Master Concept Library."""
    
    def __init__(self):
        self.ontology = OntologyService()
    
    def validate_entity(self, entity: Entity) -> List[str]:
        """Validate an Entity object against the master concept library.
        
        Returns a list of validation errors (empty if valid).
        """
        errors = []
        
        # Validate entity type
        if not self.ontology.validate_entity_type(entity.entity_type):
            errors.append(f"Unknown entity type: {entity.entity_type}")
            # If type is invalid, skip further validation
            return errors
        
        # Validate properties
        if entity.properties:
            # Get applicable properties for this entity type
            applicable_props = self.ontology.get_applicable_properties(
                entity.entity_type, "Entity"
            )
            
            for prop_name, prop_value in entity.properties.items():
                # Check if property is known
                if not self.ontology.validate_property_name(prop_name):
                    errors.append(f"Unknown property: {prop_name}")
                    continue
                
                # Check if property is applicable to this entity type
                if prop_name not in applicable_props:
                    errors.append(
                        f"Property '{prop_name}' not applicable to entity type '{entity.entity_type}'"
                    )
                    continue
                
                # Validate property value
                if not self.ontology.validate_property_value(prop_name, prop_value):
                    errors.append(
                        f"Invalid value for property '{prop_name}': {prop_value}"
                    )
        
        # Validate modifiers
        if entity.modifiers:
            # Get applicable modifiers for this entity type
            applicable_mods = self.ontology.get_applicable_modifiers(
                entity.entity_type, "Entity"
            )
            
            for mod_name, mod_value in entity.modifiers.items():
                # Check if modifier is known
                if not self.ontology.validate_modifier_name(mod_name):
                    errors.append(f"Unknown modifier: {mod_name}")
                    continue
                
                # Check if modifier is applicable
                if mod_name not in applicable_mods:
                    errors.append(
                        f"Modifier '{mod_name}' not applicable to entity type '{entity.entity_type}'"
                    )
                    continue
                
                # Validate modifier value
                valid_values = self.ontology.get_modifier_values(mod_name)
                if mod_value not in valid_values:
                    errors.append(
                        f"Invalid value for modifier '{mod_name}': {mod_value}. "
                        f"Valid values: {valid_values}"
                    )
        
        return errors
    
    def validate_relationship(self, relationship: Relationship,
                            source_entity: Optional[Entity] = None,
                            target_entity: Optional[Entity] = None) -> List[str]:
        """Validate a Relationship object against the master concept library.
        
        If source and target entities are provided, also validates domain/range constraints.
        
        Returns a list of validation errors (empty if valid).
        """
        errors = []
        
        # Validate relationship type
        if not self.ontology.validate_connection_type(relationship.relationship_type):
            errors.append(f"Unknown relationship type: {relationship.relationship_type}")
            # If type is invalid, skip further validation
            return errors
        
        # Validate domain/range if entities provided
        if source_entity and target_entity:
            if not self.ontology.validate_connection_domain_range(
                relationship.relationship_type,
                source_entity.entity_type,
                target_entity.entity_type
            ):
                errors.append(
                    f"Invalid domain/range for relationship '{relationship.relationship_type}': "
                    f"'{source_entity.entity_type}' -> '{target_entity.entity_type}'"
                )
        
        # Validate properties
        if relationship.properties:
            applicable_props = self.ontology.get_applicable_properties(
                relationship.relationship_type, "Connection"
            )
            
            for prop_name, prop_value in relationship.properties.items():
                if not self.ontology.validate_property_name(prop_name):
                    errors.append(f"Unknown property: {prop_name}")
                    continue
                
                if prop_name not in applicable_props:
                    errors.append(
                        f"Property '{prop_name}' not applicable to relationship type "
                        f"'{relationship.relationship_type}'"
                    )
                    continue
                
                if not self.ontology.validate_property_value(prop_name, prop_value):
                    errors.append(
                        f"Invalid value for property '{prop_name}': {prop_value}"
                    )
        
        # Validate modifiers
        if relationship.modifiers:
            applicable_mods = self.ontology.get_applicable_modifiers(
                relationship.relationship_type, "Connection"
            )
            
            for mod_name, mod_value in relationship.modifiers.items():
                if not self.ontology.validate_modifier_name(mod_name):
                    errors.append(f"Unknown modifier: {mod_name}")
                    continue
                
                if mod_name not in applicable_mods:
                    errors.append(
                        f"Modifier '{mod_name}' not applicable to relationship type "
                        f"'{relationship.relationship_type}'"
                    )
                    continue
                
                valid_values = self.ontology.get_modifier_values(mod_name)
                if mod_value not in valid_values:
                    errors.append(
                        f"Invalid value for modifier '{mod_name}': {mod_value}. "
                        f"Valid values: {valid_values}"
                    )
        
        return errors
    
    def suggest_entity_type(self, text: str) -> List[str]:
        """Suggest entity types based on text content.
        
        Uses indigenous terms to find matching concepts.
        """
        suggestions = []
        
        # Search for concepts matching terms in the text
        words = text.lower().split()
        for word in words:
            concepts = self.ontology.search_by_indigenous_term(word)
            for concept in concepts:
                if hasattr(concept, 'object_type') and concept.object_type == "Entity":
                    if concept.name not in suggestions:
                        suggestions.append(concept.name)
        
        return suggestions
    
    def suggest_relationship_type(self, text: str) -> List[str]:
        """Suggest relationship types based on text content.
        
        Uses indigenous terms to find matching concepts.
        """
        suggestions = []
        
        # Search for concepts matching terms in the text
        words = text.lower().split()
        for word in words:
            concepts = self.ontology.search_by_indigenous_term(word)
            for concept in concepts:
                if hasattr(concept, 'object_type') and concept.object_type == "Connection":
                    if concept.name not in suggestions:
                        suggestions.append(concept.name)
        
        return suggestions
    
    def get_entity_template(self, entity_type: str) -> Dict[str, Any]:
        """Get a template for creating an entity of the specified type.
        
        Returns a dictionary with typical attributes and applicable properties.
        """
        if not self.ontology.validate_entity_type(entity_type):
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        # Get typical attributes
        attributes = self.ontology.get_entity_attributes(entity_type)
        
        # Get applicable properties and modifiers
        properties = self.ontology.get_applicable_properties(entity_type, "Entity")
        modifiers = self.ontology.get_applicable_modifiers(entity_type, "Entity")
        
        template = {
            "entity_type": entity_type,
            "typical_attributes": attributes,
            "applicable_properties": {},
            "applicable_modifiers": {}
        }
        
        # Add property details
        for prop in properties:
            prop_def = self.ontology.get_concept(prop)
            if prop_def and hasattr(prop_def, 'value_type'):
                template["applicable_properties"][prop] = {
                    "type": prop_def.value_type,
                    "description": prop_def.description
                }
                if prop_def.value_type == "categorical" and prop_def.valid_values:
                    template["applicable_properties"][prop]["valid_values"] = prop_def.valid_values
                elif prop_def.value_type == "numeric" and prop_def.value_range:
                    template["applicable_properties"][prop]["range"] = prop_def.value_range
        
        # Add modifier details
        for mod in modifiers:
            mod_def = self.ontology.get_concept(mod)
            if mod_def and hasattr(mod_def, 'values'):
                template["applicable_modifiers"][mod] = {
                    "values": mod_def.values,
                    "default": mod_def.default_value,
                    "description": mod_def.description
                }
        
        return template
    
    def get_relationship_template(self, relationship_type: str) -> Dict[str, Any]:
        """Get a template for creating a relationship of the specified type.
        
        Returns a dictionary with domain/range constraints and applicable properties.
        """
        if not self.ontology.validate_connection_type(relationship_type):
            raise ValueError(f"Unknown relationship type: {relationship_type}")
        
        rel_def = self.ontology.get_concept(relationship_type)
        
        template = {
            "relationship_type": relationship_type,
            "domain": rel_def.domain if hasattr(rel_def, 'domain') else [],
            "range": rel_def.range if hasattr(rel_def, 'range') else [],
            "is_directed": rel_def.is_directed if hasattr(rel_def, 'is_directed') else True,
            "applicable_properties": {},
            "applicable_modifiers": {}
        }
        
        # Get applicable properties and modifiers
        properties = self.ontology.get_applicable_properties(relationship_type, "Connection")
        modifiers = self.ontology.get_applicable_modifiers(relationship_type, "Connection")
        
        # Add property details
        for prop in properties:
            prop_def = self.ontology.get_concept(prop)
            if prop_def and hasattr(prop_def, 'value_type'):
                template["applicable_properties"][prop] = {
                    "type": prop_def.value_type,
                    "description": prop_def.description
                }
        
        # Add modifier details
        for mod in modifiers:
            mod_def = self.ontology.get_concept(mod)
            if mod_def and hasattr(mod_def, 'values'):
                template["applicable_modifiers"][mod] = {
                    "values": mod_def.values,
                    "default": mod_def.default_value,
                    "description": mod_def.description
                }
        
        return template
    
    def enrich_entity(self, entity: Entity) -> Entity:
        """Enrich an entity with default modifiers from the ontology.
        
        Adds default modifier values where not already specified.
        """
        applicable_mods = self.ontology.get_applicable_modifiers(
            entity.entity_type, "Entity"
        )
        
        for mod_name in applicable_mods:
            if mod_name not in entity.modifiers:
                default_value = self.ontology.get_modifier_default(mod_name)
                if default_value is not None:
                    entity.modifiers[mod_name] = default_value
        
        return entity
    
    def enrich_relationship(self, relationship: Relationship) -> Relationship:
        """Enrich a relationship with default modifiers from the ontology.
        
        Adds default modifier values where not already specified.
        """
        applicable_mods = self.ontology.get_applicable_modifiers(
            relationship.relationship_type, "Connection"
        )
        
        for mod_name in applicable_mods:
            if mod_name not in relationship.modifiers:
                default_value = self.ontology.get_modifier_default(mod_name)
                if default_value is not None:
                    relationship.modifiers[mod_name] = default_value
        
        return relationship
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the ontology and validation."""
        return self.ontology.get_statistics()
    
    def get_valid_relationships(self, source_type: str, target_type: str) -> List[str]:
        """Get valid relationship types for a given source and target entity type."""
        valid_relationships = []
        
        for rel_name, rel_concept in self.ontology.registry.connections.items():
            # Check if source type is in allowed domain
            if source_type in rel_concept.domain or "*" in rel_concept.domain:
                # Check if target type is in allowed range
                if target_type in rel_concept.range or "*" in rel_concept.range:
                    valid_relationships.append(rel_name)
        
        return valid_relationships
    
    def get_relationship_constraints(self, relationship_type: str) -> Optional[Dict[str, List[str]]]:
        """Get domain and range constraints for a relationship type."""
        rel_concept = self.ontology.registry.connections.get(relationship_type)
        if rel_concept:
            return {
                "domain": rel_concept.domain,
                "range": rel_concept.range
            }
        return None