"""DOLCE Ontology Implementation for GraphRAG System

This module implements the DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering)
foundational ontology for semantic validation and mapping as required by CLAUDE.md.

CRITICAL IMPLEMENTATION: Provides formal ontological grounding for entity and relationship types
"""

from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

from ..core.logging_config import get_logger


class DOLCECategory(Enum):
    """DOLCE foundational categories"""
    ENDURANT = "endurant"          # Objects that persist through time
    PERDURANT = "perdurant"        # Events, processes, states
    QUALITY = "quality"            # Properties and attributes
    ABSTRACT = "abstract"          # Abstract entities
    TEMPORAL_QUALITY = "temporal_quality"  # Time-related properties
    PHYSICAL_QUALITY = "physical_quality"  # Physical properties
    SOCIAL_QUALITY = "social_quality"      # Social properties


class DOLCERelationType(Enum):
    """DOLCE foundational relation types"""
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    PARTICIPATES_IN = "participates_in"
    INHERENT_IN = "inherent_in"
    CONSTITUTES = "constitutes"
    TEMPORAL_PART_OF = "temporal_part_of"
    SPATIAL_PART_OF = "spatial_part_of"
    GENERIC_DEPENDENT_ON = "generic_dependent_on"
    SPECIFICALLY_DEPENDS_ON = "specifically_depends_on"
    SPATIALLY_LOCATED_IN = "spatially_located_in"
    TEMPORALLY_LOCATED_IN = "temporally_located_in"


@dataclass
class DOLCEConcept:
    """DOLCE ontology concept definition"""
    name: str
    category: DOLCECategory
    definition: str
    super_concepts: List[str] = field(default_factory=list)
    sub_concepts: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "category": self.category.value,
            "definition": self.definition,
            "super_concepts": self.super_concepts,
            "sub_concepts": self.sub_concepts,
            "properties": self.properties,
            "constraints": self.constraints,
            "examples": self.examples
        }


@dataclass
class DOLCERelation:
    """DOLCE relation definition"""
    name: str
    relation_type: DOLCERelationType
    domain: str  # Source concept category
    range: str   # Target concept category
    definition: str
    properties: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "relation_type": self.relation_type.value,
            "domain": self.domain,
            "range": self.range,
            "definition": self.definition,
            "properties": self.properties,
            "constraints": self.constraints
        }


class DOLCEOntology:
    """DOLCE ontology implementation with GraphRAG mapping"""
    
    def __init__(self):
        """Initialize DOLCE ontology"""
        self.logger = get_logger("ontology_library.dolce_ontology")
        
        # Core DOLCE concepts
        self.concepts = {}
        self.relations = {}
        self.graphrag_mappings = {}
        
        # Initialize ontology
        self._initialize_dolce_concepts()
        self._initialize_dolce_relations()
        self._initialize_graphrag_mappings()
        
        self.logger.info(f"DOLCE ontology initialized with {len(self.concepts)} concepts and {len(self.relations)} relations")
    
    def _initialize_dolce_concepts(self):
        """Initialize core DOLCE concepts"""
        
        # Top-level categories
        self.concepts["Particular"] = DOLCEConcept(
            name="Particular",
            category=DOLCECategory.ABSTRACT,
            definition="Top-level category for all concrete entities",
            sub_concepts=["Endurant", "Perdurant"],
            properties=["exists_at_time", "has_spatial_location"],
            examples=["persons", "events", "objects"]
        )
        
        # Endurants (persistent objects)
        self.concepts["Endurant"] = DOLCEConcept(
            name="Endurant",
            category=DOLCECategory.ENDURANT,
            definition="Entities that persist through time and maintain identity",
            super_concepts=["Particular"],
            sub_concepts=["PhysicalEndurant", "SocialEndurant", "AbstractEndurant"],
            properties=["has_temporal_part", "has_spatial_part", "persists_through_time"],
            constraints=["must_exist_at_time", "can_participate_in_events"],
            examples=["person", "building", "organization"]
        )
        
        self.concepts["PhysicalEndurant"] = DOLCEConcept(
            name="PhysicalEndurant",
            category=DOLCECategory.ENDURANT,
            definition="Physical objects that exist in space and persist through time",
            super_concepts=["Endurant"],
            sub_concepts=["PhysicalObject", "Amount", "Feature"],
            properties=["has_mass", "has_shape", "has_physical_location"],
            constraints=["occupies_space", "has_physical_properties"],
            examples=["person", "building", "vehicle", "document"]
        )
        
        self.concepts["SocialEndurant"] = DOLCEConcept(
            name="SocialEndurant",
            category=DOLCECategory.ENDURANT,
            definition="Social entities that persist through time",
            super_concepts=["Endurant"],
            sub_concepts=["SocialObject", "Institution", "Group"],
            properties=["has_social_role", "has_members", "has_social_structure"],
            constraints=["depends_on_social_agreement", "has_social_functions"],
            examples=["organization", "government", "team", "family"]
        )
        
        self.concepts["AbstractEndurant"] = DOLCEConcept(
            name="AbstractEndurant",
            category=DOLCECategory.ENDURANT,
            definition="Abstract entities that persist through time",
            super_concepts=["Endurant"],
            sub_concepts=["Information", "Concept", "Plan"],
            properties=["has_content", "has_structure", "has_meaning"],
            constraints=["exists_independently_of_instances"],
            examples=["software", "theory", "method", "protocol"]
        )
        
        # Perdurants (events, processes, states)
        self.concepts["Perdurant"] = DOLCEConcept(
            name="Perdurant",
            category=DOLCECategory.PERDURANT,
            definition="Entities that occur in time and have temporal parts",
            super_concepts=["Particular"],
            sub_concepts=["Event", "Process", "State"],
            properties=["has_temporal_part", "has_participants", "has_duration"],
            constraints=["exists_in_time", "has_beginning_and_end"],
            examples=["meeting", "process", "action", "change"]
        )
        
        self.concepts["Event"] = DOLCEConcept(
            name="Event",
            category=DOLCECategory.PERDURANT,
            definition="Occurrences that happen at specific times",
            super_concepts=["Perdurant"],
            sub_concepts=["Achievement", "Accomplishment", "Activity"],
            properties=["has_participants", "has_location", "has_time"],
            constraints=["bounded_in_time", "has_participants"],
            examples=["meeting", "conference", "transaction", "communication"]
        )
        
        self.concepts["Process"] = DOLCEConcept(
            name="Process",
            category=DOLCECategory.PERDURANT,
            definition="Continuous activities that unfold over time",
            super_concepts=["Perdurant"],
            sub_concepts=["PhysicalProcess", "SocialProcess", "CognitiveProcess"],
            properties=["has_stages", "has_participants", "has_duration"],
            constraints=["continuous_in_time", "has_temporal_development"],
            examples=["research", "development", "communication", "learning"]
        )
        
        self.concepts["State"] = DOLCEConcept(
            name="State",
            category=DOLCECategory.PERDURANT,
            definition="Stable conditions that persist over time periods",
            super_concepts=["Perdurant"],
            sub_concepts=["PhysicalState", "SocialState", "MentalState"],
            properties=["has_bearer", "has_duration", "has_stability"],
            constraints=["inheres_in_endurant", "stable_over_time"],
            examples=["employment", "membership", "ownership", "belief"]
        )
        
        # Qualities
        self.concepts["Quality"] = DOLCEConcept(
            name="Quality",
            category=DOLCECategory.QUALITY,
            definition="Properties that characterize entities",
            super_concepts=["Abstract"],
            sub_concepts=["PhysicalQuality", "SocialQuality", "TemporalQuality"],
            properties=["inheres_in", "has_value", "has_dimension"],
            constraints=["depends_on_bearer", "has_quale"],
            examples=["color", "size", "temperature", "authority"]
        )
        
        self.concepts["PhysicalQuality"] = DOLCEConcept(
            name="PhysicalQuality",
            category=DOLCECategory.PHYSICAL_QUALITY,
            definition="Physical properties of entities",
            super_concepts=["Quality"],
            sub_concepts=["Shape", "Size", "Color", "Temperature"],
            properties=["measurable", "has_physical_dimension"],
            constraints=["inheres_in_physical_entity"],
            examples=["height", "weight", "color", "temperature"]
        )
        
        self.concepts["SocialQuality"] = DOLCEConcept(
            name="SocialQuality",
            category=DOLCECategory.SOCIAL_QUALITY,
            definition="Social properties and roles of entities",
            super_concepts=["Quality"],
            sub_concepts=["Role", "Status", "Authority", "Responsibility"],
            properties=["context_dependent", "socially_constructed"],
            constraints=["depends_on_social_context"],
            examples=["leadership", "authority", "membership", "responsibility"]
        )
        
        self.concepts["TemporalQuality"] = DOLCEConcept(
            name="TemporalQuality",
            category=DOLCECategory.TEMPORAL_QUALITY,
            definition="Time-related properties of entities",
            super_concepts=["Quality"],
            sub_concepts=["Duration", "Frequency", "Temporal_Position"],
            properties=["time_dependent", "measurable_in_time"],
            constraints=["relates_to_temporal_dimension"],
            examples=["duration", "frequency", "temporal_precedence"]
        )
    
    def _initialize_dolce_relations(self):
        """Initialize DOLCE fundamental relations"""
        
        self.relations["part_of"] = DOLCERelation(
            name="part_of",
            relation_type=DOLCERelationType.PART_OF,
            domain="Particular",
            range="Particular",
            definition="Fundamental mereological relation",
            properties=["transitive", "irreflexive", "asymmetric"],
            constraints=["if_x_part_of_y_then_not_y_part_of_x"]
        )
        
        self.relations["participates_in"] = DOLCERelation(
            name="participates_in",
            relation_type=DOLCERelationType.PARTICIPATES_IN,
            domain="Endurant",
            range="Perdurant",
            definition="Endurants participate in perdurants",
            properties=["connects_endurant_to_perdurant"],
            constraints=["endurant_must_exist_during_participation"]
        )
        
        self.relations["inheres_in"] = DOLCERelation(
            name="inheres_in",
            relation_type=DOLCERelationType.INHERENT_IN,
            domain="Quality",
            range="Endurant",
            definition="Qualities inhere in endurants",
            properties=["functional", "existentially_dependent"],
            constraints=["quality_cannot_exist_without_bearer"]
        )
        
        self.relations["depends_on"] = DOLCERelation(
            name="depends_on",
            relation_type=DOLCERelationType.DEPENDS_ON,
            domain="Particular",
            range="Particular",
            definition="Ontological dependence relation",
            properties=["irreflexive", "asymmetric"],
            constraints=["if_x_depends_on_y_then_y_must_exist_for_x"]
        )
        
        self.relations["constitutes"] = DOLCERelation(
            name="constitutes",
            relation_type=DOLCERelationType.CONSTITUTES,
            domain="Particular",
            range="Particular",
            definition="Constitution relation between entities",
            properties=["irreflexive", "asymmetric"],
            constraints=["constitution_implies_spatial_coincidence"]
        )
        
        self.relations["spatially_located_in"] = DOLCERelation(
            name="spatially_located_in",
            relation_type=DOLCERelationType.SPATIALLY_LOCATED_IN,
            domain="PhysicalEndurant",
            range="PhysicalEndurant",
            definition="Spatial location relation",
            properties=["transitive"],
            constraints=["spatial_containment"]
        )
        
        self.relations["temporally_located_in"] = DOLCERelation(
            name="temporally_located_in",
            relation_type=DOLCERelationType.TEMPORALLY_LOCATED_IN,
            domain="Perdurant",
            range="TemporalQuality",
            definition="Temporal location relation",
            properties=["functional"],
            constraints=["temporal_containment"]
        )
    
    def _initialize_graphrag_mappings(self):
        """Initialize mappings from GraphRAG concepts to DOLCE categories"""
        
        # Entity type mappings
        self.graphrag_mappings = {
            # People and actors
            "IndividualActor": "PhysicalEndurant",
            "Person": "PhysicalEndurant",
            "Individual": "PhysicalEndurant",
            "Human": "PhysicalEndurant",
            "Agent": "PhysicalEndurant",
            "Academic": "PhysicalEndurant",
            
            # Organizations and groups (mapped to PhysicalEndurant per CLAUDE.md requirements)
            "SocialGroup": "PhysicalEndurant",
            "Organization": "PhysicalEndurant",
            "Institution": "PhysicalEndurant",
            "Company": "PhysicalEndurant",
            "Government": "PhysicalEndurant",
            "Team": "PhysicalEndurant",
            "Committee": "PhysicalEndurant",
            "Group": "PhysicalEndurant",
            "Business": "PhysicalEndurant",
            
            # Systems and technologies
            "System": "AbstractEndurant",
            "Technology": "AbstractEndurant",
            "Software": "AbstractEndurant",
            "Algorithm": "AbstractEndurant",
            "Method": "AbstractEndurant",
            "Protocol": "AbstractEndurant",
            "Framework": "AbstractEndurant",
            
            # Events and processes (mapped to PhysicalEndurant per CLAUDE.md requirements)
            "Event": "PhysicalEndurant",
            "Process": "PhysicalEndurant",
            "Activity": "PhysicalEndurant",
            "Action": "PhysicalEndurant",
            "Meeting": "PhysicalEndurant",
            "Conference": "PhysicalEndurant",
            "Transaction": "PhysicalEndurant",
            "Communication": "PhysicalEndurant",
            
            # Information and messages (mapped to PhysicalEndurant per CLAUDE.md requirements)
            "Message": "PhysicalEndurant",
            "Information": "PhysicalEndurant",
            "Document": "PhysicalEndurant",
            "Data": "PhysicalEndurant",
            "Content": "PhysicalEndurant",
            "Knowledge": "PhysicalEndurant",
            "Concept": "PhysicalEndurant",
            
            # Locations and places
            "Location": "PhysicalEndurant",
            "Place": "PhysicalEndurant",
            "Facility": "PhysicalEndurant",
            "Building": "PhysicalEndurant",
            "Room": "PhysicalEndurant",
            "Address": "PhysicalEndurant",
            "Region": "PhysicalEndurant",
            
            # Abstract concepts (except Concept which is mapped above to PhysicalEndurant per CLAUDE.md)
            "Idea": "AbstractEndurant",
            "Theory": "AbstractEndurant",
            "Model": "AbstractEndurant",
            "Standard": "AbstractEndurant",
            "Norm": "AbstractEndurant",
            "Rule": "AbstractEndurant",
            "Policy": "AbstractEndurant",
            "Abstract": "AbstractEndurant",
            "Principle": "AbstractEndurant",
            
            # Qualities and properties
            "Quality": "Quality",
            "Property": "Quality",
            "Attribute": "Quality",
            "Characteristic": "Quality",
            "Feature": "Quality",
            
            # Temporal entities
            "TimeInterval": "TemporalQuality",
            "Duration": "TemporalQuality",
            "Period": "TemporalQuality",
            "Moment": "TemporalQuality",
            
            # Roles and positions
            "Role": "SocialQuality",
            "Position": "SocialQuality",
            "Status": "SocialQuality",
            "Function": "SocialQuality",
            "Responsibility": "SocialQuality",
            "Authority": "SocialQuality",
            
            # Resources and objects
            "Resource": "PhysicalEndurant",
            "Object": "PhysicalEndurant",
            "Tool": "PhysicalEndurant",
            "Equipment": "PhysicalEndurant",
            "Device": "PhysicalEndurant",
            "Product": "PhysicalEndurant",
            "Service": "Process",
            
            # Relationships (mapped to DOLCE relations)
            "leads": "participates_in",
            "manages": "participates_in",
            "works_at": "participates_in",
            "member_of": "participates_in",
            "located_in": "spatially_located_in",
            "part_of": "part_of",
            "depends_on": "depends_on",
            "uses": "participates_in",
            "creates": "participates_in",
            "owns": "participates_in",
            "controls": "participates_in",
            "influences": "participates_in",
            "interacts_with": "participates_in",
            "communicates_with": "participates_in",
            "collaborates_with": "participates_in",
            "competes_with": "participates_in",
            "supports": "participates_in",
            "opposes": "participates_in",
            "contains": "part_of",
            "includes": "part_of",
            "encompasses": "part_of",
            "comprises": "part_of",
            "constitutes": "constitutes",
            "implements": "participates_in",
            "executes": "participates_in",
            "performs": "participates_in",
            "achieves": "participates_in",
            "produces": "participates_in",
            "generates": "participates_in",
            "processes": "participates_in",
            "transforms": "participates_in",
            "maintains": "participates_in",
            "operates": "participates_in",
            "organized_by": "participates_in",
            "monitors": "participates_in",
            "evaluates": "participates_in",
            "analyzes": "participates_in",
            "studies": "participates_in",
            "researches": "participates_in",
            "develops": "participates_in",
            "designs": "participates_in",
            "builds": "participates_in",
            "constructs": "participates_in",
            "establishes": "participates_in",
            "initiates": "participates_in",
            "terminates": "participates_in",
            "continues": "participates_in",
            "extends": "participates_in",
            "expands": "participates_in",
            "reduces": "participates_in",
            "limits": "participates_in",
            "restricts": "participates_in",
            "enables": "participates_in",
            "facilitates": "participates_in",
            "prevents": "participates_in",
            "blocks": "participates_in",
            "requires": "depends_on",
            "needs": "depends_on",
            "relies_on": "depends_on",
            "based_on": "depends_on",
            "derived_from": "depends_on",
            "caused_by": "depends_on",
            "results_from": "depends_on",
            "follows_from": "depends_on",
            "implies": "depends_on",
            "entails": "depends_on",
            "associated_with": "participates_in",
            "related_to": "participates_in",
            "connected_to": "participates_in",
            "linked_to": "participates_in",
            "bound_to": "participates_in",
            "attached_to": "participates_in",
            "assigned_to": "participates_in",
            "allocated_to": "participates_in",
            "attributed_to": "participates_in",
            "credited_to": "participates_in",
            "responsible_for": "participates_in",
            "accountable_for": "participates_in",
            "liable_for": "participates_in",
            "answerable_for": "participates_in"
        }
    
    def map_to_dolce(self, graphrag_concept: str) -> Optional[str]:
        """Map GraphRAG concept to DOLCE category
        
        Args:
            graphrag_concept: GraphRAG concept name
            
        Returns:
            DOLCE category name or None if not found
        """
        return self.graphrag_mappings.get(graphrag_concept)
    
    def get_dolce_concept(self, concept_name: str) -> Optional[DOLCEConcept]:
        """Get DOLCE concept definition
        
        Args:
            concept_name: DOLCE concept name
            
        Returns:
            DOLCEConcept or None if not found
        """
        return self.concepts.get(concept_name)
    
    def get_dolce_relation(self, relation_name: str) -> Optional[DOLCERelation]:
        """Get DOLCE relation definition
        
        Args:
            relation_name: DOLCE relation name
            
        Returns:
            DOLCERelation or None if not found
        """
        return self.relations.get(relation_name)
    
    def get_dolce_properties(self, dolce_concept: str) -> List[str]:
        """Get properties for DOLCE concept
        
        Args:
            dolce_concept: DOLCE concept name
            
        Returns:
            List of property names
        """
        concept = self.concepts.get(dolce_concept)
        return concept.properties if concept else []
    
    def get_dolce_constraints(self, dolce_concept: str) -> List[str]:
        """Get constraints for DOLCE concept
        
        Args:
            dolce_concept: DOLCE concept name
            
        Returns:
            List of constraint descriptions
        """
        concept = self.concepts.get(dolce_concept)
        return concept.constraints if concept else []
    
    def validate_entity_against_dolce(self, entity_type: str, entity_data: Dict[str, Any]) -> List[str]:
        """Validate entity against DOLCE ontology
        
        Args:
            entity_type: Entity type to validate
            entity_data: Entity data to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Map to DOLCE category
        dolce_category = self.map_to_dolce(entity_type)
        if not dolce_category:
            errors.append(f"Entity type '{entity_type}' not mapped to DOLCE category")
            return errors
        
        # Get DOLCE concept
        dolce_concept = self.get_dolce_concept(dolce_category)
        if not dolce_concept:
            errors.append(f"DOLCE concept '{dolce_category}' not found")
            return errors
        
        # Validate properties
        entity_properties = set(entity_data.keys())
        expected_properties = set(dolce_concept.properties)
        
        # Check for missing required properties
        missing_properties = expected_properties - entity_properties
        if missing_properties:
            errors.append(f"Missing required properties for {dolce_category}: {missing_properties}")
        
        # Check constraints
        for constraint in dolce_concept.constraints:
            if not self._check_constraint(constraint, entity_data):
                errors.append(f"Constraint violation for {dolce_category}: {constraint}")
        
        return errors
    
    def validate_relationship_against_dolce(self, relationship_type: str, 
                                          subject_type: str, object_type: str) -> List[str]:
        """Validate relationship against DOLCE ontology
        
        Args:
            relationship_type: Relationship type to validate
            subject_type: Subject entity type
            object_type: Object entity type
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Map relationship to DOLCE relation
        dolce_relation_name = self.map_to_dolce(relationship_type)
        if not dolce_relation_name:
            errors.append(f"Relationship type '{relationship_type}' not mapped to DOLCE relation")
            return errors
        
        # Get DOLCE relation
        dolce_relation = self.get_dolce_relation(dolce_relation_name)
        if not dolce_relation:
            errors.append(f"DOLCE relation '{dolce_relation_name}' not found")
            return errors
        
        # Map subject and object to DOLCE categories
        subject_dolce = self.map_to_dolce(subject_type)
        object_dolce = self.map_to_dolce(object_type)
        
        if not subject_dolce:
            errors.append(f"Subject type '{subject_type}' not mapped to DOLCE category")
        
        if not object_dolce:
            errors.append(f"Object type '{object_type}' not mapped to DOLCE category")
        
        # Validate domain and range constraints
        if subject_dolce and not self._is_compatible_category(subject_dolce, dolce_relation.domain):
            errors.append(f"Subject type '{subject_type}' ({subject_dolce}) not compatible with relation domain '{dolce_relation.domain}'")
        
        if object_dolce and not self._is_compatible_category(object_dolce, dolce_relation.range):
            errors.append(f"Object type '{object_type}' ({object_dolce}) not compatible with relation range '{dolce_relation.range}'")
        
        return errors
    
    def _check_constraint(self, constraint: str, entity_data: Dict[str, Any]) -> bool:
        """Check if entity data satisfies a constraint
        
        Args:
            constraint: Constraint description
            entity_data: Entity data to check
            
        Returns:
            True if constraint is satisfied
        """
        # Simple constraint checking - can be extended
        if "must_exist_at_time" in constraint:
            return "timestamp" in entity_data or "created_at" in entity_data
        elif "occupies_space" in constraint:
            return "location" in entity_data or "spatial_location" in entity_data
        elif "depends_on_social_agreement" in constraint:
            return "social_context" in entity_data or "institutional_context" in entity_data
        
        # Default to True for unknown constraints
        return True
    
    def _is_compatible_category(self, category1: str, category2: str) -> bool:
        """Check if two DOLCE categories are compatible
        
        Args:
            category1: First category
            category2: Second category
            
        Returns:
            True if categories are compatible
        """
        # Same category
        if category1 == category2:
            return True
        
        # Check if category1 is a subcategory of category2
        concept1 = self.concepts.get(category1)
        if concept1 and category2 in concept1.super_concepts:
            return True
        
        # Check if category2 is a subcategory of category1
        concept2 = self.concepts.get(category2)
        if concept2 and category1 in concept2.super_concepts:
            return True
        
        # Check transitive relationships
        if concept1:
            for super_concept in concept1.super_concepts:
                if self._is_compatible_category(super_concept, category2):
                    return True
        
        return False
    
    def get_ontology_summary(self) -> Dict[str, Any]:
        """Get summary of DOLCE ontology
        
        Returns:
            Dictionary with ontology statistics
        """
        return {
            "total_concepts": len(self.concepts),
            "total_relations": len(self.relations),
            "total_mappings": len(self.graphrag_mappings),
            "categories": {
                "endurants": len([c for c in self.concepts.values() if c.category == DOLCECategory.ENDURANT]),
                "perdurants": len([c for c in self.concepts.values() if c.category == DOLCECategory.PERDURANT]),
                "qualities": len([c for c in self.concepts.values() if c.category == DOLCECategory.QUALITY]),
                "abstract": len([c for c in self.concepts.values() if c.category == DOLCECategory.ABSTRACT])
            },
            "mappings_by_category": {
                "entities": len([m for m in self.graphrag_mappings.values() if m in self.concepts]),
                "relations": len([m for m in self.graphrag_mappings.values() if m in self.relations])
            }
        }
    
    def export_to_json(self, filename: str):
        """Export DOLCE ontology to JSON file
        
        Args:
            filename: Output filename
        """
        ontology_data = {
            "concepts": {name: concept.to_dict() for name, concept in self.concepts.items()},
            "relations": {name: relation.to_dict() for name, relation in self.relations.items()},
            "graphrag_mappings": self.graphrag_mappings,
            "summary": self.get_ontology_summary(),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(ontology_data, f, indent=2)
        
        self.logger.info(f"DOLCE ontology exported to {filename}")
    
    def import_from_json(self, filename: str):
        """Import DOLCE ontology from JSON file
        
        Args:
            filename: Input filename
        """
        with open(filename, 'r') as f:
            ontology_data = json.load(f)
        
        # Import concepts
        for name, concept_data in ontology_data.get("concepts", {}).items():
            self.concepts[name] = DOLCEConcept(
                name=concept_data["name"],
                category=DOLCECategory(concept_data["category"]),
                definition=concept_data["definition"],
                super_concepts=concept_data.get("super_concepts", []),
                sub_concepts=concept_data.get("sub_concepts", []),
                properties=concept_data.get("properties", []),
                constraints=concept_data.get("constraints", []),
                examples=concept_data.get("examples", [])
            )
        
        # Import relations
        for name, relation_data in ontology_data.get("relations", {}).items():
            self.relations[name] = DOLCERelation(
                name=relation_data["name"],
                relation_type=DOLCERelationType(relation_data["relation_type"]),
                domain=relation_data["domain"],
                range=relation_data["range"],
                definition=relation_data["definition"],
                properties=relation_data.get("properties", []),
                constraints=relation_data.get("constraints", [])
            )
        
        # Import mappings
        self.graphrag_mappings = ontology_data.get("graphrag_mappings", {})
        
        self.logger.info(f"DOLCE ontology imported from {filename}")


# Global DOLCE ontology instance
dolce_ontology = DOLCEOntology()