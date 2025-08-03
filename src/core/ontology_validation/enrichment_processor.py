"""
Enrichment Processor for Ontology Validation

Enriches entities and relationships with default values and additional
metadata based on ontology definitions.
"""

import logging
from typing import Dict, Any, List, Optional

from src.ontology_library.ontology_service import OntologyService
from ..data_models import Entity, Relationship

logger = logging.getLogger(__name__)


class EntityEnricher:
    """Enriches entities with ontology-based defaults and metadata"""
    
    def __init__(self, ontology_service: OntologyService):
        """Initialize with ontology service"""
        self.ontology = ontology_service
        self.logger = logging.getLogger("core.ontology_validation.entity_enricher")

    def enrich_entity(self, entity: Entity) -> Entity:
        """Enrich an entity with default modifiers from the ontology.
        
        Adds default modifier values where not already specified.
        """
        try:
            # Get applicable modifiers for this entity type
            applicable_mods = self.ontology.get_applicable_modifiers(
                entity.entity_type, "Entity"
            )
            
            # Add default modifiers where not already present
            for mod_name in applicable_mods:
                if mod_name not in entity.modifiers:
                    default_value = self.ontology.get_modifier_default(mod_name)
                    if default_value is not None:
                        entity.modifiers[mod_name] = default_value
                        self.logger.debug(f"Added default modifier {mod_name}={default_value} to entity {entity.entity_id}")
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to enrich entity {entity.entity_id}: {e}")
            return entity

    def enrich_entity_with_properties(self, entity: Entity, auto_populate: bool = True) -> Entity:
        """Enrich entity with recommended properties based on entity type"""
        try:
            # Get applicable properties for this entity type
            applicable_props = self.ontology.get_applicable_properties(
                entity.entity_type, "Entity"
            )
            
            for prop_name in applicable_props:
                if prop_name not in entity.properties:
                    if auto_populate:
                        # Try to get default or recommended value
                        default_value = self._get_property_default_value(prop_name, entity)
                        if default_value is not None:
                            entity.properties[prop_name] = default_value
                            self.logger.debug(f"Added default property {prop_name}={default_value} to entity {entity.entity_id}")
                    else:
                        # Just mark as recommended without adding value
                        if not hasattr(entity, '_recommended_properties'):
                            entity._recommended_properties = []
                        entity._recommended_properties.append(prop_name)
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to enrich entity properties for {entity.entity_id}: {e}")
            return entity

    def enrich_entity_with_metadata(self, entity: Entity) -> Entity:
        """Enrich entity with ontology-derived metadata"""
        try:
            entity_type_info = self.ontology.get_concept(entity.entity_type)
            
            if entity_type_info:
                # Add ontology metadata
                ontology_metadata = {
                    "ontology_source": "master_concept_library",
                    "entity_type_description": getattr(entity_type_info, 'description', ''),
                    "entity_category": self._determine_entity_category(entity.entity_type),
                    "applicable_modifiers": list(self.ontology.get_applicable_modifiers(entity.entity_type, "Entity")),
                    "applicable_properties": list(self.ontology.get_applicable_properties(entity.entity_type, "Entity"))
                }
                
                # Add to entity metadata without overwriting existing
                if not hasattr(entity, 'metadata') or entity.metadata is None:
                    entity.metadata = {}
                
                for key, value in ontology_metadata.items():
                    if key not in entity.metadata:
                        entity.metadata[key] = value
            
            return entity
            
        except Exception as e:
            self.logger.error(f"Failed to enrich entity metadata for {entity.entity_id}: {e}")
            return entity

    def _get_property_default_value(self, property_name: str, entity: Entity) -> Optional[Any]:
        """Get default value for a property based on entity context"""
        try:
            prop_def = self.ontology.get_concept(property_name)
            
            if prop_def and hasattr(prop_def, 'default_value'):
                return prop_def.default_value
            
            # Context-specific defaults
            if property_name.lower() == "status" and "organization" in entity.entity_type.lower():
                return "active"
            elif property_name.lower() == "type" and "person" in entity.entity_type.lower():
                return "individual"
            elif property_name.lower() == "visibility":
                return "public"
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Could not get default value for property {property_name}: {e}")
            return None

    def _determine_entity_category(self, entity_type: str) -> str:
        """Determine high-level category for an entity type"""
        entity_type_lower = entity_type.lower()
        
        if any(word in entity_type_lower for word in ['person', 'individual', 'human', 'actor']):
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

    def batch_enrich_entities(self, entities: List[Entity], 
                            include_properties: bool = True,
                            include_metadata: bool = True) -> List[Entity]:
        """Enrich multiple entities in batch"""
        enriched_entities = []
        
        for entity in entities:
            try:
                enriched_entity = self.enrich_entity(entity)
                
                if include_properties:
                    enriched_entity = self.enrich_entity_with_properties(enriched_entity)
                
                if include_metadata:
                    enriched_entity = self.enrich_entity_with_metadata(enriched_entity)
                
                enriched_entities.append(enriched_entity)
                
            except Exception as e:
                self.logger.error(f"Failed to enrich entity {entity.entity_id}: {e}")
                enriched_entities.append(entity)  # Add original if enrichment fails
        
        return enriched_entities

    def get_enrichment_statistics(self, entity: Entity) -> Dict[str, Any]:
        """Get statistics about potential enrichments for an entity"""
        try:
            applicable_mods = self.ontology.get_applicable_modifiers(entity.entity_type, "Entity")
            applicable_props = self.ontology.get_applicable_properties(entity.entity_type, "Entity")
            
            current_mods = set(entity.modifiers.keys()) if entity.modifiers else set()
            current_props = set(entity.properties.keys()) if entity.properties else set()
            
            missing_mods = set(applicable_mods) - current_mods
            missing_props = set(applicable_props) - current_props
            
            return {
                "entity_id": entity.entity_id,
                "entity_type": entity.entity_type,
                "applicable_modifiers": len(applicable_mods),
                "current_modifiers": len(current_mods),
                "missing_modifiers": list(missing_mods),
                "applicable_properties": len(applicable_props),
                "current_properties": len(current_props),
                "missing_properties": list(missing_props),
                "enrichment_potential": {
                    "modifiers": len(missing_mods) / len(applicable_mods) if applicable_mods else 0,
                    "properties": len(missing_props) / len(applicable_props) if applicable_props else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get enrichment statistics for {entity.entity_id}: {e}")
            return {}


class RelationshipEnricher:
    """Enriches relationships with ontology-based defaults and metadata"""
    
    def __init__(self, ontology_service: OntologyService):
        """Initialize with ontology service"""
        self.ontology = ontology_service
        self.logger = logging.getLogger("core.ontology_validation.relationship_enricher")

    def enrich_relationship(self, relationship: Relationship) -> Relationship:
        """Enrich a relationship with default modifiers from the ontology.
        
        Adds default modifier values where not already specified.
        """
        try:
            # Get applicable modifiers for this relationship type
            applicable_mods = self.ontology.get_applicable_modifiers(
                relationship.relationship_type, "Connection"
            )
            
            # Add default modifiers where not already present
            for mod_name in applicable_mods:
                if mod_name not in relationship.modifiers:
                    default_value = self.ontology.get_modifier_default(mod_name)
                    if default_value is not None:
                        relationship.modifiers[mod_name] = default_value
                        self.logger.debug(f"Added default modifier {mod_name}={default_value} to relationship {relationship.relationship_id}")
            
            return relationship
            
        except Exception as e:
            self.logger.error(f"Failed to enrich relationship {relationship.relationship_id}: {e}")
            return relationship

    def enrich_relationship_with_properties(self, relationship: Relationship, auto_populate: bool = True) -> Relationship:
        """Enrich relationship with recommended properties based on relationship type"""
        try:
            # Get applicable properties for this relationship type
            applicable_props = self.ontology.get_applicable_properties(
                relationship.relationship_type, "Connection"
            )
            
            for prop_name in applicable_props:
                if prop_name not in relationship.properties:
                    if auto_populate:
                        # Try to get default or recommended value
                        default_value = self._get_property_default_value(prop_name, relationship)
                        if default_value is not None:
                            relationship.properties[prop_name] = default_value
                            self.logger.debug(f"Added default property {prop_name}={default_value} to relationship {relationship.relationship_id}")
                    else:
                        # Just mark as recommended without adding value
                        if not hasattr(relationship, '_recommended_properties'):
                            relationship._recommended_properties = []
                        relationship._recommended_properties.append(prop_name)
            
            return relationship
            
        except Exception as e:
            self.logger.error(f"Failed to enrich relationship properties for {relationship.relationship_id}: {e}")
            return relationship

    def enrich_relationship_with_metadata(self, relationship: Relationship) -> Relationship:
        """Enrich relationship with ontology-derived metadata"""
        try:
            rel_type_info = self.ontology.get_concept(relationship.relationship_type)
            
            if rel_type_info:
                # Add ontology metadata
                ontology_metadata = {
                    "ontology_source": "master_concept_library",
                    "relationship_type_description": getattr(rel_type_info, 'description', ''),
                    "relationship_category": self._determine_relationship_category(relationship.relationship_type),
                    "is_directed": getattr(rel_type_info, 'is_directed', True),
                    "domain": getattr(rel_type_info, 'domain', []),
                    "range": getattr(rel_type_info, 'range', []),
                    "applicable_modifiers": list(self.ontology.get_applicable_modifiers(relationship.relationship_type, "Connection")),
                    "applicable_properties": list(self.ontology.get_applicable_properties(relationship.relationship_type, "Connection"))
                }
                
                # Add to relationship metadata without overwriting existing
                if not hasattr(relationship, 'metadata') or relationship.metadata is None:
                    relationship.metadata = {}
                
                for key, value in ontology_metadata.items():
                    if key not in relationship.metadata:
                        relationship.metadata[key] = value
            
            return relationship
            
        except Exception as e:
            self.logger.error(f"Failed to enrich relationship metadata for {relationship.relationship_id}: {e}")
            return relationship

    def _get_property_default_value(self, property_name: str, relationship: Relationship) -> Optional[Any]:
        """Get default value for a property based on relationship context"""
        try:
            prop_def = self.ontology.get_concept(property_name)
            
            if prop_def and hasattr(prop_def, 'default_value'):
                return prop_def.default_value
            
            # Context-specific defaults
            if property_name.lower() == "strength" and "connect" in relationship.relationship_type.lower():
                return "medium"
            elif property_name.lower() == "confidence":
                return 0.8
            elif property_name.lower() == "temporal_scope":
                return "current"
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Could not get default value for property {property_name}: {e}")
            return None

    def _determine_relationship_category(self, relationship_type: str) -> str:
        """Determine high-level category for a relationship type"""
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

    def batch_enrich_relationships(self, relationships: List[Relationship],
                                 include_properties: bool = True,
                                 include_metadata: bool = True) -> List[Relationship]:
        """Enrich multiple relationships in batch"""
        enriched_relationships = []
        
        for relationship in relationships:
            try:
                enriched_relationship = self.enrich_relationship(relationship)
                
                if include_properties:
                    enriched_relationship = self.enrich_relationship_with_properties(enriched_relationship)
                
                if include_metadata:
                    enriched_relationship = self.enrich_relationship_with_metadata(enriched_relationship)
                
                enriched_relationships.append(enriched_relationship)
                
            except Exception as e:
                self.logger.error(f"Failed to enrich relationship {relationship.relationship_id}: {e}")
                enriched_relationships.append(relationship)  # Add original if enrichment fails
        
        return enriched_relationships

    def get_enrichment_statistics(self, relationship: Relationship) -> Dict[str, Any]:
        """Get statistics about potential enrichments for a relationship"""
        try:
            applicable_mods = self.ontology.get_applicable_modifiers(relationship.relationship_type, "Connection")
            applicable_props = self.ontology.get_applicable_properties(relationship.relationship_type, "Connection")
            
            current_mods = set(relationship.modifiers.keys()) if relationship.modifiers else set()
            current_props = set(relationship.properties.keys()) if relationship.properties else set()
            
            missing_mods = set(applicable_mods) - current_mods
            missing_props = set(applicable_props) - current_props
            
            return {
                "relationship_id": relationship.relationship_id,
                "relationship_type": relationship.relationship_type,
                "applicable_modifiers": len(applicable_mods),
                "current_modifiers": len(current_mods),
                "missing_modifiers": list(missing_mods),
                "applicable_properties": len(applicable_props),
                "current_properties": len(current_props),
                "missing_properties": list(missing_props),
                "enrichment_potential": {
                    "modifiers": len(missing_mods) / len(applicable_mods) if applicable_mods else 0,
                    "properties": len(missing_props) / len(applicable_props) if applicable_props else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get enrichment statistics for {relationship.relationship_id}: {e}")
            return {}


class BatchEnrichmentProcessor:
    """Handles batch enrichment operations across multiple data types"""
    
    def __init__(self, entity_enricher: EntityEnricher, relationship_enricher: RelationshipEnricher):
        """Initialize with individual enrichers"""
        self.entity_enricher = entity_enricher
        self.relationship_enricher = relationship_enricher
        self.logger = logging.getLogger("core.ontology_validation.batch_enricher")

    def enrich_graph_data(self, entities: List[Entity], relationships: List[Relationship],
                         enrichment_options: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """Enrich complete graph data (entities and relationships)"""
        
        # Default enrichment options
        if enrichment_options is None:
            enrichment_options = {
                "include_properties": True,
                "include_metadata": True,
                "auto_populate_defaults": True
            }
        
        try:
            # Enrich entities
            enriched_entities = self.entity_enricher.batch_enrich_entities(
                entities,
                include_properties=enrichment_options.get("include_properties", True),
                include_metadata=enrichment_options.get("include_metadata", True)
            )
            
            # Enrich relationships
            enriched_relationships = self.relationship_enricher.batch_enrich_relationships(
                relationships,
                include_properties=enrichment_options.get("include_properties", True),
                include_metadata=enrichment_options.get("include_metadata", True)
            )
            
            # Generate enrichment report
            enrichment_report = self._generate_enrichment_report(
                entities, enriched_entities, relationships, enriched_relationships
            )
            
            return {
                "entities": enriched_entities,
                "relationships": enriched_relationships,
                "enrichment_report": enrichment_report,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to enrich graph data: {e}")
            return {
                "entities": entities,  # Return originals on failure
                "relationships": relationships,
                "enrichment_report": {"error": str(e)},
                "status": "failed"
            }

    def _generate_enrichment_report(self, original_entities: List[Entity], enriched_entities: List[Entity],
                                  original_relationships: List[Relationship], enriched_relationships: List[Relationship]) -> Dict[str, Any]:
        """Generate report of enrichment changes"""
        
        entity_changes = 0
        relationship_changes = 0
        
        # Count entity changes
        for orig, enriched in zip(original_entities, enriched_entities):
            if (len(enriched.modifiers) > len(orig.modifiers) or 
                len(enriched.properties) > len(orig.properties) or
                (hasattr(enriched, 'metadata') and len(enriched.metadata) > len(getattr(orig, 'metadata', {})))):
                entity_changes += 1
        
        # Count relationship changes
        for orig, enriched in zip(original_relationships, enriched_relationships):
            if (len(enriched.modifiers) > len(orig.modifiers) or 
                len(enriched.properties) > len(orig.properties) or
                (hasattr(enriched, 'metadata') and len(enriched.metadata) > len(getattr(orig, 'metadata', {})))):
                relationship_changes += 1
        
        return {
            "total_entities": len(original_entities),
            "entities_enriched": entity_changes,
            "entity_enrichment_rate": entity_changes / len(original_entities) if original_entities else 0,
            "total_relationships": len(original_relationships),
            "relationships_enriched": relationship_changes,
            "relationship_enrichment_rate": relationship_changes / len(original_relationships) if original_relationships else 0,
            "overall_enrichment_rate": (entity_changes + relationship_changes) / (len(original_entities) + len(original_relationships)) if (original_entities or original_relationships) else 0
        }