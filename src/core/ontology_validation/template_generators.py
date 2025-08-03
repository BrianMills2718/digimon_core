"""
Template Generators for Ontology Validation

Generates templates for entities and relationships based on ontology definitions.
"""

import logging
from typing import Dict, Any, List, Optional

from src.ontology_library.ontology_service import OntologyService

logger = logging.getLogger(__name__)


class EntityTemplateGenerator:
    """Generates entity templates based on ontology definitions"""
    
    def __init__(self, ontology_service: OntologyService):
        """Initialize with ontology service"""
        self.ontology = ontology_service
        self.logger = logging.getLogger("core.ontology_validation.entity_templates")

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

    def generate_entity_templates_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate entity templates organized by category"""
        templates_by_category = {}
        
        try:
            # Get all entity types from the ontology
            all_entity_types = list(self.ontology.registry.entities.keys())
            
            for entity_type in all_entity_types:
                try:
                    template = self.get_entity_template(entity_type)
                    
                    # Determine category (could be based on entity properties or naming convention)
                    category = self._determine_entity_category(entity_type)
                    
                    if category not in templates_by_category:
                        templates_by_category[category] = []
                    
                    templates_by_category[category].append(template)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to generate template for entity type {entity_type}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to generate entity templates by category: {e}")
            
        return templates_by_category

    def _determine_entity_category(self, entity_type: str) -> str:
        """Determine category for an entity type"""
        # Simple categorization based on common patterns
        entity_type_lower = entity_type.lower()
        
        if any(word in entity_type_lower for word in ['person', 'individual', 'actor', 'human']):
            return "People"
        elif any(word in entity_type_lower for word in ['organization', 'company', 'institution', 'business']):
            return "Organizations"
        elif any(word in entity_type_lower for word in ['location', 'place', 'region', 'facility']):
            return "Locations"
        elif any(word in entity_type_lower for word in ['event', 'activity', 'process', 'action']):
            return "Events"
        elif any(word in entity_type_lower for word in ['concept', 'abstract', 'principle', 'idea']):
            return "Abstract"
        else:
            return "General"

    def validate_entity_template(self, template: Dict[str, Any]) -> List[str]:
        """Validate that an entity template is well-formed"""
        errors = []
        
        required_fields = ["entity_type", "typical_attributes", "applicable_properties", "applicable_modifiers"]
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required template field: {field}")
        
        # Validate entity type
        if "entity_type" in template:
            if not self.ontology.validate_entity_type(template["entity_type"]):
                errors.append(f"Invalid entity type in template: {template['entity_type']}")
        
        return errors

    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about available entity templates"""
        try:
            all_entity_types = list(self.ontology.registry.entities.keys())
            templates_by_category = self.generate_entity_templates_by_category()
            
            return {
                "total_entity_types": len(all_entity_types),
                "categories": list(templates_by_category.keys()),
                "templates_per_category": {
                    category: len(templates) 
                    for category, templates in templates_by_category.items()
                },
                "most_common_category": max(
                    templates_by_category.items(), 
                    key=lambda x: len(x[1])
                )[0] if templates_by_category else None
            }
        except Exception as e:
            self.logger.error(f"Failed to get template statistics: {e}")
            return {}


class RelationshipTemplateGenerator:
    """Generates relationship templates based on ontology definitions"""
    
    def __init__(self, ontology_service: OntologyService):
        """Initialize with ontology service"""
        self.ontology = ontology_service
        self.logger = logging.getLogger("core.ontology_validation.relationship_templates")

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

    def generate_relationship_templates_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate relationship templates organized by semantic type"""
        templates_by_type = {}
        
        try:
            # Get all relationship types from the ontology
            all_relationship_types = list(self.ontology.registry.connections.keys())
            
            for rel_type in all_relationship_types:
                try:
                    template = self.get_relationship_template(rel_type)
                    
                    # Determine semantic type
                    semantic_type = self._determine_relationship_semantic_type(rel_type)
                    
                    if semantic_type not in templates_by_type:
                        templates_by_type[semantic_type] = []
                    
                    templates_by_type[semantic_type].append(template)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to generate template for relationship type {rel_type}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to generate relationship templates by type: {e}")
            
        return templates_by_type

    def _determine_relationship_semantic_type(self, relationship_type: str) -> str:
        """Determine semantic type for a relationship"""
        rel_type_lower = relationship_type.lower()
        
        if any(word in rel_type_lower for word in ['member', 'part', 'component', 'belongs']):
            return "Membership"
        elif any(word in rel_type_lower for word in ['location', 'at', 'in', 'near', 'within']):
            return "Spatial"
        elif any(word in rel_type_lower for word in ['before', 'after', 'during', 'when', 'temporal']):
            return "Temporal"
        elif any(word in rel_type_lower for word in ['cause', 'effect', 'leads', 'results', 'influence']):
            return "Causal"
        elif any(word in rel_type_lower for word in ['similar', 'different', 'same', 'like', 'compare']):
            return "Similarity"
        elif any(word in rel_type_lower for word in ['interact', 'communicate', 'relate', 'connect']):
            return "Interaction"
        else:
            return "General"

    def get_compatible_relationships(self, source_entity_type: str, target_entity_type: str) -> List[Dict[str, Any]]:
        """Get relationship templates compatible with given entity types"""
        compatible_relationships = []
        
        try:
            all_relationship_types = list(self.ontology.registry.connections.keys())
            
            for rel_type in all_relationship_types:
                try:
                    template = self.get_relationship_template(rel_type)
                    
                    # Check domain/range compatibility
                    domain = template.get("domain", [])
                    range_types = template.get("range", [])
                    
                    # Check if source type is compatible with domain
                    source_compatible = (
                        "*" in domain or 
                        source_entity_type in domain or
                        any(self._is_subtype(source_entity_type, d) for d in domain)
                    )
                    
                    # Check if target type is compatible with range
                    target_compatible = (
                        "*" in range_types or
                        target_entity_type in range_types or
                        any(self._is_subtype(target_entity_type, r) for r in range_types)
                    )
                    
                    if source_compatible and target_compatible:
                        template["compatibility_score"] = self._calculate_compatibility_score(
                            source_entity_type, target_entity_type, template
                        )
                        compatible_relationships.append(template)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to check compatibility for relationship {rel_type}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to get compatible relationships: {e}")
            
        # Sort by compatibility score (highest first)
        compatible_relationships.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
        
        return compatible_relationships

    def _is_subtype(self, entity_type: str, parent_type: str) -> bool:
        """Check if entity_type is a subtype of parent_type"""
        # Simple heuristic - could be enhanced with actual ontology hierarchy
        return parent_type.lower() in entity_type.lower()

    def _calculate_compatibility_score(self, source_type: str, target_type: str, template: Dict[str, Any]) -> float:
        """Calculate compatibility score for a relationship template"""
        score = 0.0
        
        domain = template.get("domain", [])
        range_types = template.get("range", [])
        
        # Exact match gets highest score
        if source_type in domain:
            score += 1.0
        elif "*" in domain:
            score += 0.5
        
        if target_type in range_types:
            score += 1.0
        elif "*" in range_types:
            score += 0.5
        
        # Bonus for specific (non-wildcard) relationships
        if "*" not in domain and "*" not in range_types:
            score += 0.2
        
        return score

    def validate_relationship_template(self, template: Dict[str, Any]) -> List[str]:
        """Validate that a relationship template is well-formed"""
        errors = []
        
        required_fields = ["relationship_type", "domain", "range", "applicable_properties", "applicable_modifiers"]
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required template field: {field}")
        
        # Validate relationship type
        if "relationship_type" in template:
            if not self.ontology.validate_connection_type(template["relationship_type"]):
                errors.append(f"Invalid relationship type in template: {template['relationship_type']}")
        
        # Validate domain and range are lists
        for field in ["domain", "range"]:
            if field in template and not isinstance(template[field], list):
                errors.append(f"Template field '{field}' must be a list")
        
        return errors

    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about available relationship templates"""
        try:
            all_relationship_types = list(self.ontology.registry.connections.keys())
            templates_by_type = self.generate_relationship_templates_by_type()
            
            # Calculate directedness statistics
            directed_count = 0
            undirected_count = 0
            
            for rel_type in all_relationship_types:
                try:
                    template = self.get_relationship_template(rel_type)
                    if template.get("is_directed", True):
                        directed_count += 1
                    else:
                        undirected_count += 1
                except:
                    pass
            
            return {
                "total_relationship_types": len(all_relationship_types),
                "semantic_types": list(templates_by_type.keys()),
                "templates_per_semantic_type": {
                    sem_type: len(templates) 
                    for sem_type, templates in templates_by_type.items()
                },
                "directed_relationships": directed_count,
                "undirected_relationships": undirected_count,
                "most_common_semantic_type": max(
                    templates_by_type.items(), 
                    key=lambda x: len(x[1])
                )[0] if templates_by_type else None
            }
        except Exception as e:
            self.logger.error(f"Failed to get relationship template statistics: {e}")
            return {}