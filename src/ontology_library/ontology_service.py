"""Ontology Service - Loads and manages the Master Concept Library

This service provides a singleton interface for accessing the master concept
definitions throughout the KGAS system.
"""

import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path

from .master_concepts import (
    MasterConceptRegistry,
    EntityConcept,
    ConnectionConcept,
    PropertyConcept,
    ModifierConcept,
    ConceptDefinition,
    TheoryReference
)


class OntologyService:
    """Singleton service for managing the Master Concept Library."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.registry = MasterConceptRegistry()
            self.concepts_dir = Path(__file__).parent / "concepts"
            self._load_all_concepts()
            self._initialized = True
    
    def _load_all_concepts(self):
        """Load all concept definitions from YAML files."""
        # Load entities
        entities_file = self.concepts_dir / "entities.yaml"
        if entities_file.exists():
            self._load_entities(entities_file)
        
        # Load connections
        connections_file = self.concepts_dir / "connections.yaml"
        if connections_file.exists():
            self._load_connections(connections_file)
        
        # Load properties
        properties_file = self.concepts_dir / "properties.yaml"
        if properties_file.exists():
            self._load_properties(properties_file)
        
        # Load modifiers
        modifiers_file = self.concepts_dir / "modifiers.yaml"
        if modifiers_file.exists():
            self._load_modifiers(modifiers_file)
        
        print(f"Loaded {len(self.registry.entities)} entities, "
              f"{len(self.registry.connections)} connections, "
              f"{len(self.registry.properties)} properties, "
              f"{len(self.registry.modifiers)} modifiers")
    
    def _load_entities(self, file_path: Path):
        """Load entity concepts from YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return
        
        for name, concept_data in data.items():
            if isinstance(concept_data, dict):
                try:
                    concept = EntityConcept(name=name, **concept_data)
                    self.registry.entities[name] = concept
                except Exception as e:
                    print(f"Error loading entity {name}: {e}")
    
    def _load_connections(self, file_path: Path):
        """Load connection concepts from YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return
        
        for name, concept_data in data.items():
            if isinstance(concept_data, dict):
                try:
                    concept = ConnectionConcept(name=name, **concept_data)
                    self.registry.connections[name] = concept
                except Exception as e:
                    print(f"Error loading connection {name}: {e}")
    
    def _load_properties(self, file_path: Path):
        """Load property concepts from YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return
        
        for name, concept_data in data.items():
            if isinstance(concept_data, dict):
                try:
                    concept = PropertyConcept(name=name, **concept_data)
                    self.registry.properties[name] = concept
                except Exception as e:
                    print(f"Error loading property {name}: {e}")
    
    def _load_modifiers(self, file_path: Path):
        """Load modifier concepts from YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return
            
        for name, concept_data in data.items():
            if isinstance(concept_data, dict):
                try:
                    concept = ModifierConcept(name=name, **concept_data)
                    self.registry.modifiers[name] = concept
                except Exception as e:
                    print(f"Error loading modifier {name}: {e}")
    
    # Public API Methods
    
    def get_concept(self, concept_name: str) -> Optional[ConceptDefinition]:
        """Get a concept by name from any category."""
        return self.registry.get_concept(concept_name)
    
    def validate_entity_type(self, entity_type: str) -> bool:
        """Check if an entity type exists in the master library."""
        try:
            return entity_type in self.registry.entities
        except Exception as e:
            print(f"Error validating entity type '{entity_type}': {e}")
            return False
    
    def validate_connection_type(self, connection_type: str) -> bool:
        """Check if a connection type exists in the master library."""
        try:
            return connection_type in self.registry.connections
        except Exception as e:
            print(f"Error validating connection type '{connection_type}': {e}")
            return False
    
    def validate_property_name(self, property_name: str) -> bool:
        """Check if a property name exists in the master library."""
        try:
            return property_name in self.registry.properties
        except Exception as e:
            print(f"Error validating property name '{property_name}': {e}")
            return False
    
    def validate_modifier_name(self, modifier_name: str) -> bool:
        """Check if a modifier name exists in the master library."""
        try:
            return modifier_name in self.registry.modifiers
        except Exception as e:
            print(f"Error validating modifier name '{modifier_name}': {e}")
            return False
    
    def validate_connection_domain_range(self, connection_type: str, 
                                       source_type: str, target_type: str) -> bool:
        """Validate if a connection's domain and range constraints are satisfied."""
        try:
            return self.registry.validate_domain_range(connection_type, source_type, target_type)
        except Exception as e:
            print(f"Error validating domain/range for '{connection_type}': {e}")
            return False
    
    def get_entity_attributes(self, entity_type: str) -> List[str]:
        """Get typical attributes for an entity type."""
        if entity_type in self.registry.entities:
            entity = self.registry.entities[entity_type]
            return entity.typical_attributes or []
        return []
    
    def get_property_value_type(self, property_name: str) -> Optional[str]:
        """Get the value type for a property."""
        if property_name in self.registry.properties:
            prop = self.registry.properties[property_name]
            return prop.value_type
        return None
    
    def get_property_valid_values(self, property_name: str) -> List[Any]:
        """Get valid values for a categorical property."""
        if property_name in self.registry.properties:
            prop = self.registry.properties[property_name]
            return prop.valid_values or []
        return []
    
    def get_modifier_values(self, modifier_name: str) -> List[str]:
        """Get possible values for a modifier."""
        if modifier_name in self.registry.modifiers:
            modifier = self.registry.modifiers[modifier_name]
            return modifier.values or []
        return []
    
    def get_modifier_default(self, modifier_name: str) -> Optional[str]:
        """Get the default value for a modifier."""
        if modifier_name in self.registry.modifiers:
            modifier = self.registry.modifiers[modifier_name]
            return modifier.default_value
        return None
    
    def search_by_indigenous_term(self, term: str) -> List[ConceptDefinition]:
        """Search for concepts that include a specific indigenous term."""
        results = []
        
        for registry in [self.registry.entities, self.registry.connections, 
                        self.registry.properties, self.registry.modifiers]:
            for concept in registry.values():
                if term.lower() in [t.lower() for t in concept.indigenous_term]:
                    results.append(concept)
        
        return results
    
    def get_concepts_for_theory(self, theory_name: str) -> List[str]:
        """Get all concepts used by a specific theory."""
        concepts = []
        for concept_name, theory_refs in self.registry.theories_using_concepts.items():
            for ref in theory_refs:
                if ref.theory_name == theory_name:
                    concepts.append(concept_name)
        return concepts
    
    def add_theory_usage(self, concept_name: str, theory_name: str, 
                        theory_file: str, usage: str):
        """Record that a theory uses a specific concept."""
        theory_ref = TheoryReference(
            theory_name=theory_name,
            theory_file=theory_file,
            usage=usage
        )
        self.registry.add_theory_reference(concept_name, theory_ref)
    
    def get_subtypes(self, concept_name: str) -> List[str]:
        """Get all concepts that are subtypes of the given concept."""
        return self.registry.get_subtypes(concept_name)
    
    def get_concept_hierarchy(self, root_concept: str = None) -> Dict[str, List[str]]:
        """Get the concept hierarchy as a tree structure."""
        return self.registry.get_concept_hierarchy(root_concept)
    
    def validate_property_value(self, property_name: str, value: Any) -> bool:
        """Validate if a value is appropriate for a property."""
        if property_name not in self.registry.properties:
            return False
        
        prop = self.registry.properties[property_name]
        
        if prop.value_type == "numeric":
            if not isinstance(value, (int, float)):
                return False
            if prop.value_range:
                min_val = prop.value_range.get("min", float("-inf"))
                max_val = prop.value_range.get("max", float("inf"))
                return min_val <= value <= max_val
        
        elif prop.value_type == "categorical":
            if prop.valid_values:
                return value in prop.valid_values
        
        elif prop.value_type == "boolean":
            return isinstance(value, bool)
        
        elif prop.value_type == "string":
            return isinstance(value, str)
        
        return True
    
    def get_applicable_properties(self, concept_type: str, 
                                concept_category: str = None) -> List[str]:
        """Get properties that can be applied to a concept."""
        applicable = []
        
        for prop_name, prop in self.registry.properties.items():
            if prop.applies_to:
                # Check if concept type is in applies_to
                if concept_type in prop.applies_to:
                    applicable.append(prop_name)
                # Check if concept category is in applies_to
                elif concept_category and concept_category in prop.applies_to:
                    applicable.append(prop_name)
        
        return applicable
    
    def get_applicable_modifiers(self, concept_type: str,
                               concept_category: str = None) -> List[str]:
        """Get modifiers that can be applied to a concept."""
        applicable = []
        
        for mod_name, modifier in self.registry.modifiers.items():
            if modifier.applies_to:
                # Check if concept type is in applies_to
                if concept_type in modifier.applies_to:
                    applicable.append(mod_name)
                # Check if concept category is in applies_to
                elif concept_category and concept_category in modifier.applies_to:
                    applicable.append(mod_name)
        
        return applicable
    
    def export_registry(self, output_path: str):
        """Export the entire registry to a JSON file."""
        import json
        
        data = self.registry.export_to_dict()
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_concept(self, concept_name: str) -> Optional[ConceptDefinition]:
        """Get a concept by name, searching all registries.
        
        Returns None if concept not found instead of raising an error.
        """
        try:
            # Check entities
            if concept_name in self.registry.entities:
                return self.registry.entities[concept_name]
            
            # Check connections
            if concept_name in self.registry.connections:
                return self.registry.connections[concept_name]
            
            # Check properties
            if concept_name in self.registry.properties:
                return self.registry.properties[concept_name]
            
            # Check modifiers
            if concept_name in self.registry.modifiers:
                return self.registry.modifiers[concept_name]
            
            return None
        except Exception as e:
            print(f"Error retrieving concept '{concept_name}': {e}")
            return None
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the loaded concepts."""
        stats = {
            "total_concepts": len(self.registry.get_all_names()),
            "entities": len(self.registry.entities),
            "connections": len(self.registry.connections),
            "properties": len(self.registry.properties),
            "modifiers": len(self.registry.modifiers),
            "concept_relations": len(self.registry.relations),
            "theories_tracked": len(set(
                ref.theory_name 
                for refs in self.registry.theories_using_concepts.values()
                for ref in refs
            ))
        }
        return stats
    
    def validate_extraction(self, extraction: Dict[str, Any]) -> List[str]:
        """Validate an extraction against the master concept library."""
        errors = []
        
        # Validate entity type if present
        if "entity_type" in extraction:
            if not self.validate_entity_type(extraction["entity_type"]):
                errors.append(f"Unknown entity type: {extraction['entity_type']}")
        
        # Validate connection type if present
        if "connection_type" in extraction:
            if not self.validate_connection_type(extraction["connection_type"]):
                errors.append(f"Unknown connection type: {extraction['connection_type']}")
            
            # Validate domain/range if connection
            if "source_type" in extraction and "target_type" in extraction:
                if not self.validate_connection_domain_range(
                    extraction["connection_type"],
                    extraction["source_type"],
                    extraction["target_type"]
                ):
                    errors.append(
                        f"Invalid domain/range for {extraction['connection_type']}: "
                        f"{extraction['source_type']} -> {extraction['target_type']}"
                    )
        
        # Validate properties
        if "properties" in extraction and isinstance(extraction["properties"], dict):
            for prop_name, prop_value in extraction["properties"].items():
                if not self.validate_property_name(prop_name):
                    errors.append(f"Unknown property: {prop_name}")
                elif not self.validate_property_value(prop_name, prop_value):
                    errors.append(f"Invalid value for property {prop_name}: {prop_value}")
        
        # Validate modifiers
        if "modifiers" in extraction and isinstance(extraction["modifiers"], dict):
            for mod_name, mod_value in extraction["modifiers"].items():
                if not self.validate_modifier_name(mod_name):
                    errors.append(f"Unknown modifier: {mod_name}")
                elif mod_value not in self.get_modifier_values(mod_name):
                    errors.append(f"Invalid value for modifier {mod_name}: {mod_value}")
        
        return errors