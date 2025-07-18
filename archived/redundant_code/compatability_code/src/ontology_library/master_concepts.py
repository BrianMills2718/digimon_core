"""Master Concept Models - Pydantic models for generic concepts

These models represent the canonical concepts in the Master Concept Library.
They align with termDefinition, propertyDefinition, modifierDefinition from 
the Theory Meta-Schema.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class ConceptDefinition(BaseModel):
    """Base model for any concept in the Master Concept Library."""
    name: str = Field(description="Standardized, camelCase or snake_case name for the concept.")
    indigenous_term: List[str] = Field(
        description="Common real-world phrasing or key academic terms associated with this concept."
    )
    description: str = Field(description="A concise explanation of the concept's meaning.")
    subTypeOf: Optional[List[str]] = Field(
        default_factory=list, 
        description="List of parent concept names this concept is a subtype of."
    )
    references: Optional[List[str]] = Field(
        default_factory=list,
        description="Academic references where this concept is defined."
    )
    aliases: Optional[List[str]] = Field(
        default_factory=list,
        description="Alternative names or aliases for this concept."
    )


class EntityConcept(ConceptDefinition):
    """Concept definition for entities (actors, objects, etc.)"""
    object_type: Literal["Entity"] = "Entity"
    typical_attributes: Optional[List[str]] = Field(
        default_factory=list,
        description="Common attributes associated with this entity type."
    )
    examples: Optional[List[str]] = Field(
        default_factory=list,
        description="Examples of this entity type from literature."
    )


class ConnectionConcept(ConceptDefinition):
    """Concept definition for connections/relationships between entities"""
    object_type: Literal["Connection"] = "Connection"
    domain: Optional[List[str]] = Field(
        default_factory=list, 
        description="Valid source entity concept names for this connection."
    )
    range: Optional[List[str]] = Field(
        default_factory=list, 
        description="Valid target entity concept names for this connection."
    )
    is_directed: bool = Field(
        default=True,
        description="Whether this relationship type is directional."
    )
    is_symmetric: bool = Field(
        default=False,
        description="Whether this relationship is symmetric (A->B implies B->A)."
    )
    cardinality: Optional[str] = Field(
        default="many-to-many",
        description="Cardinality constraints (one-to-one, one-to-many, many-to-many)."
    )


class PropertyConcept(ConceptDefinition):
    """Concept definition for properties/attributes that can be attached to entities or connections"""
    object_type: Literal["Property"] = "Property"
    value_type: Literal["numeric", "categorical", "boolean", "string", "complex", "derived"] = Field(
        description="The data type of this property."
    )
    applies_to: Optional[List[str]] = Field(
        default_factory=list, 
        description="Concept names this property can be attached to (Entity, Connection)."
    )
    valid_values: Optional[List[Any]] = Field(
        default_factory=list,
        description="For categorical properties, the allowed values."
    )
    value_range: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="For numeric properties, min/max values."
    )
    computation: Optional[str] = Field(
        default=None,
        description="For derived properties, how to compute the value."
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measurement for numeric properties."
    )


class ModifierConcept(ConceptDefinition):
    """Concept definition for modifiers that qualify or contextualize other concepts"""
    object_type: Literal["Modifier"] = "Modifier"
    category: Literal["temporal", "modal", "truth_value", "certainty", "normative", "other"] = Field(
        description="The category of modifier."
    )
    applies_to: Optional[List[str]] = Field(
        default_factory=list, 
        description="Concept names this modifier can qualify (Entity, Connection, Property)."
    )
    values: Optional[List[str]] = Field(
        default_factory=list,
        description="Possible values this modifier can take."
    )
    default_value: Optional[str] = Field(
        default=None,
        description="Default value if not specified."
    )


class TheoryReference(BaseModel):
    """Reference to a theory that uses a concept"""
    theory_name: str = Field(description="Name of the theory")
    theory_file: str = Field(description="Path to the theory definition file")
    usage: str = Field(description="How this theory uses the concept")


class ConceptRelation(BaseModel):
    """Defines relationships between concepts in the library"""
    from_concept: str = Field(description="Source concept name")
    to_concept: str = Field(description="Target concept name")
    relation_type: Literal["subtype", "part_of", "related_to", "opposite_of", "implies"] = Field(
        description="Type of relationship between concepts"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the relationship"
    )


class MasterConceptRegistry(BaseModel):
    """Registry to hold all loaded concepts"""
    entities: Dict[str, EntityConcept] = Field(default_factory=dict)
    connections: Dict[str, ConnectionConcept] = Field(default_factory=dict)
    properties: Dict[str, PropertyConcept] = Field(default_factory=dict)
    modifiers: Dict[str, ModifierConcept] = Field(default_factory=dict)
    relations: List[ConceptRelation] = Field(default_factory=list)
    theories_using_concepts: Dict[str, List[TheoryReference]] = Field(
        default_factory=dict,
        description="Map of concept names to theories that use them"
    )

    def get_concept(self, concept_name: str) -> Optional[ConceptDefinition]:
        """Get a concept by name from any category"""
        for registry in [self.entities, self.connections, self.properties, self.modifiers]:
            if concept_name in registry:
                return registry[concept_name]
        return None

    def get_all_names(self) -> List[str]:
        """Get all concept names across all categories"""
        names = []
        for registry in [self.entities, self.connections, self.properties, self.modifiers]:
            names.extend(registry.keys())
        return names
    
    def get_concepts_by_type(self, concept_type: Literal["Entity", "Connection", "Property", "Modifier"]) -> Dict[str, ConceptDefinition]:
        """Get all concepts of a specific type"""
        if concept_type == "Entity":
            return self.entities
        elif concept_type == "Connection":
            return self.connections
        elif concept_type == "Property":
            return self.properties
        elif concept_type == "Modifier":
            return self.modifiers
        else:
            return {}
    
    def validate_domain_range(self, connection_name: str, source_type: str, target_type: str) -> bool:
        """Validate if a connection's domain and range constraints are satisfied"""
        if connection_name not in self.connections:
            return False
        
        connection = self.connections[connection_name]
        
        # Check domain (source)
        if connection.domain and source_type not in connection.domain:
            return False
        
        # Check range (target)
        if connection.range and target_type not in connection.range:
            return False
        
        return True
    
    def get_subtypes(self, concept_name: str) -> List[str]:
        """Get all concepts that are subtypes of the given concept"""
        subtypes = []
        for registry in [self.entities, self.connections, self.properties, self.modifiers]:
            for name, concept in registry.items():
                if concept_name in concept.subTypeOf:
                    subtypes.append(name)
        return subtypes
    
    def add_theory_reference(self, concept_name: str, theory_ref: TheoryReference):
        """Add a reference to a theory that uses a concept"""
        if concept_name not in self.theories_using_concepts:
            self.theories_using_concepts[concept_name] = []
        self.theories_using_concepts[concept_name].append(theory_ref)
    
    def get_concept_hierarchy(self, root_concept: str = None) -> Dict[str, List[str]]:
        """Get the concept hierarchy as a tree structure"""
        hierarchy = {}
        
        # Build parent-child relationships
        for registry in [self.entities, self.connections, self.properties, self.modifiers]:
            for name, concept in registry.items():
                for parent in concept.subTypeOf:
                    if parent not in hierarchy:
                        hierarchy[parent] = []
                    hierarchy[parent].append(name)
        
        if root_concept:
            # Return subtree starting from root_concept
            return self._get_subtree(hierarchy, root_concept)
        
        return hierarchy
    
    def _get_subtree(self, hierarchy: Dict[str, List[str]], root: str) -> Dict[str, List[str]]:
        """Get a subtree of the hierarchy starting from a root concept"""
        subtree = {}
        if root in hierarchy:
            subtree[root] = hierarchy[root]
            for child in hierarchy[root]:
                child_subtree = self._get_subtree(hierarchy, child)
                subtree.update(child_subtree)
        return subtree
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export the registry to a dictionary format"""
        return {
            "entities": {name: concept.model_dump() for name, concept in self.entities.items()},
            "connections": {name: concept.model_dump() for name, concept in self.connections.items()},
            "properties": {name: concept.model_dump() for name, concept in self.properties.items()},
            "modifiers": {name: concept.model_dump() for name, concept in self.modifiers.items()},
            "relations": [rel.model_dump() for rel in self.relations],
            "theories_using_concepts": {
                concept: [ref.model_dump() for ref in refs] 
                for concept, refs in self.theories_using_concepts.items()
            }
        }