"""
Reified N-ary Graph Schema System

This module implements reified n-ary relationships for complex political analysis.
Instead of simple binary relations, we can represent:

1. Multi-participant relationships (US, USSR, China negotiate)
2. Conditional relationships (Détente DEPENDS_ON mutual restraint)  
3. Temporal relationships (Arms race LEADS_TO détente GIVEN cooperation)
4. Contextual relationships (Treaty negotiation OCCURS_IN Cold War context)

Reification turns relationships into first-class entities that can have properties,
participants, and be related to other entities/relationships.
"""

from typing import Dict, List, Any, Optional, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

from .extraction_schemas import ExtractionSchema, SchemaMode, EntityTypeSchema, RelationTypeSchema


class NAryRelationType(Enum):
    """Types of n-ary relationships in political analysis"""
    NEGOTIATION = "negotiation"  # Multi-party negotiation
    ALLIANCE = "alliance"  # Multi-party alliance
    CONFLICT = "conflict"  # Multi-party conflict
    TREATY = "treaty"  # Multi-party agreement
    POLICY_IMPLEMENTATION = "policy_implementation"  # Complex policy with multiple actors
    CAUSAL_CHAIN = "causal_chain"  # Multi-step causation
    CONDITIONAL_RELATIONSHIP = "conditional_relationship"  # If-then relationships
    TEMPORAL_SEQUENCE = "temporal_sequence"  # Time-ordered events
    STRATEGIC_INTERACTION = "strategic_interaction"  # Game-theoretic interactions


class ParticipantRole(Enum):
    """Roles that entities can play in n-ary relationships"""
    INITIATOR = "initiator"
    RESPONDER = "responder"
    MEDIATOR = "mediator"
    BENEFICIARY = "beneficiary"
    VICTIM = "victim"
    OBSERVER = "observer"
    GUARANTOR = "guarantor"
    IMPLEMENTER = "implementer"
    CONDITION = "condition"
    OUTCOME = "outcome"
    CONTEXT = "context"
    INSTRUMENT = "instrument"
    TARGET = "target"
    AGENT = "agent"


@dataclass
class NAryParticipant:
    """A participant in an n-ary relationship"""
    entity_id: str
    role: ParticipantRole
    contribution: Optional[str] = None  # What they contribute to the relationship
    weight: float = 1.0  # Importance/strength of participation
    temporal_order: Optional[int] = None  # Order in temporal sequences
    conditions: List[str] = field(default_factory=list)  # Conditions for participation


@dataclass
class ReifiedRelationship:
    """A reified n-ary relationship that becomes a first-class entity"""
    relation_id: str
    relation_type: NAryRelationType
    participants: List[NAryParticipant]
    
    # Relationship properties
    confidence: float = 0.8
    temporal_bounds: Optional[Tuple[datetime, datetime]] = None
    spatial_context: Optional[str] = None
    political_context: Optional[str] = None
    
    # Metadata
    source_text: Optional[str] = None
    extraction_method: str = "unknown"
    evidence_strength: float = 0.8
    
    # Relationships to other reified relationships
    dependent_on: List[str] = field(default_factory=list)  # Other relation IDs this depends on
    enables: List[str] = field(default_factory=list)  # Other relations this enables
    conflicts_with: List[str] = field(default_factory=list)  # Conflicting relations


@dataclass
class NAryRelationSchema:
    """Schema defining structure for n-ary relationships"""
    relation_type: NAryRelationType
    required_roles: Set[ParticipantRole]
    optional_roles: Set[ParticipantRole] = field(default_factory=set)
    min_participants: int = 2
    max_participants: Optional[int] = None
    allowed_entity_types: Dict[ParticipantRole, Set[str]] = field(default_factory=dict)
    temporal_constraints: Optional[Dict[str, Any]] = None
    causal_constraints: Optional[Dict[str, Any]] = None


class NAryGraphSchema(ExtractionSchema):
    """Extended schema supporting reified n-ary relationships"""
    
    def __init__(self, 
                 schema_id: str,
                 mode: SchemaMode = SchemaMode.HYBRID,
                 description: str = "",
                 entity_types: Dict[str, EntityTypeSchema] = None,
                 relation_types: Dict[str, RelationTypeSchema] = None,
                 nary_relation_schemas: Dict[NAryRelationType, NAryRelationSchema] = None):
        
        super().__init__(
            mode=mode,
            schema_id=schema_id,
            description=description,
            entity_types=entity_types or {},
            relation_types=relation_types or {}
        )
        
        self.nary_relation_schemas = nary_relation_schemas or {}
        self.reified_relationships: Dict[str, ReifiedRelationship] = {}
    
    def add_nary_relation_schema(self, schema: NAryRelationSchema) -> None:
        """Add an n-ary relation schema"""
        self.nary_relation_schemas[schema.relation_type] = schema
    
    def validate_reified_relationship(self, relationship: ReifiedRelationship) -> Dict[str, Any]:
        """Validate a reified relationship against schema"""
        errors = []
        warnings = []
        
        # Check if relation type is defined
        if relationship.relation_type not in self.nary_relation_schemas:
            errors.append(f"Relation type {relationship.relation_type} not defined in schema")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        schema = self.nary_relation_schemas[relationship.relation_type]
        
        # Check participant count
        if len(relationship.participants) < schema.min_participants:
            errors.append(f"Too few participants: {len(relationship.participants)} < {schema.min_participants}")
        
        if schema.max_participants and len(relationship.participants) > schema.max_participants:
            errors.append(f"Too many participants: {len(relationship.participants)} > {schema.max_participants}")
        
        # Check required roles
        participant_roles = {p.role for p in relationship.participants}
        missing_roles = schema.required_roles - participant_roles
        if missing_roles:
            errors.append(f"Missing required roles: {missing_roles}")
        
        # Check entity types for roles
        for participant in relationship.participants:
            if participant.role in schema.allowed_entity_types:
                # In a real implementation, we'd check the actual entity type
                # For now, we assume this validation happens elsewhere
                pass
        
        # Check temporal constraints
        if schema.temporal_constraints and relationship.temporal_bounds:
            # Validate temporal constraints
            pass
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def add_reified_relationship(self, relationship: ReifiedRelationship) -> bool:
        """Add a reified relationship to the schema"""
        validation = self.validate_reified_relationship(relationship)
        if validation["valid"]:
            self.reified_relationships[relationship.relation_id] = relationship
            return True
        return False
    
    def get_relationships_by_type(self, relation_type: NAryRelationType) -> List[ReifiedRelationship]:
        """Get all relationships of a specific type"""
        return [r for r in self.reified_relationships.values() if r.relation_type == relation_type]
    
    def get_relationships_with_entity(self, entity_id: str) -> List[ReifiedRelationship]:
        """Get all relationships involving a specific entity"""
        return [r for r in self.reified_relationships.values() 
                if any(p.entity_id == entity_id for p in r.participants)]
    
    def get_causal_chain(self, start_relation_id: str) -> List[str]:
        """Get causal chain starting from a relationship"""
        chain = [start_relation_id]
        current = self.reified_relationships.get(start_relation_id)
        
        while current and current.enables:
            # For simplicity, follow the first enabled relationship
            next_id = current.enables[0]
            if next_id not in chain:  # Avoid cycles
                chain.append(next_id)
                current = self.reified_relationships.get(next_id)
            else:
                break
        
        return chain


def create_political_nary_schema() -> NAryGraphSchema:
    """Create sophisticated n-ary schema for political analysis"""
    
    # Define entity types for political analysis
    entity_types = {
        # Political Actors
        "NATION_STATE": EntityTypeSchema(type_name="NATION_STATE"),
        "POLITICAL_LEADER": EntityTypeSchema(type_name="POLITICAL_LEADER"),
        "GOVERNMENT_INSTITUTION": EntityTypeSchema(type_name="GOVERNMENT_INSTITUTION"),
        "INTERNATIONAL_ORGANIZATION": EntityTypeSchema(type_name="INTERNATIONAL_ORGANIZATION"),
        "MILITARY_ALLIANCE": EntityTypeSchema(type_name="MILITARY_ALLIANCE"),
        
        # Abstract Concepts
        "DETENTE_CONCEPT": EntityTypeSchema(type_name="DETENTE_CONCEPT"),
        "BALANCE_OF_POWER": EntityTypeSchema(type_name="BALANCE_OF_POWER"),
        "NUCLEAR_DETERRENCE": EntityTypeSchema(type_name="NUCLEAR_DETERRENCE"),
        "ARMS_CONTROL_REGIME": EntityTypeSchema(type_name="ARMS_CONTROL_REGIME"),
        
        # Policy Instruments
        "NUCLEAR_WEAPONS": EntityTypeSchema(type_name="NUCLEAR_WEAPONS"),
        "MILITARY_SPENDING": EntityTypeSchema(type_name="MILITARY_SPENDING"),
        "BILATERAL_TREATY": EntityTypeSchema(type_name="BILATERAL_TREATY"),
        "ECONOMIC_SANCTIONS": EntityTypeSchema(type_name="ECONOMIC_SANCTIONS"),
        
        # Strategic Objectives
        "WORLD_PEACE": EntityTypeSchema(type_name="WORLD_PEACE"),
        "NUCLEAR_DISARMAMENT": EntityTypeSchema(type_name="NUCLEAR_DISARMAMENT"),
        "REGIONAL_STABILITY": EntityTypeSchema(type_name="REGIONAL_STABILITY")
    }
    
    # Create base schema
    schema = NAryGraphSchema(
        schema_id="political_nary_analysis",
        mode=SchemaMode.HYBRID,
        description="N-ary graph schema for sophisticated political analysis",
        entity_types=entity_types
    )
    
    # Define n-ary relationship schemas
    
    # 1. Multi-party Negotiation
    negotiation_schema = NAryRelationSchema(
        relation_type=NAryRelationType.NEGOTIATION,
        required_roles={ParticipantRole.INITIATOR, ParticipantRole.RESPONDER},
        optional_roles={ParticipantRole.MEDIATOR, ParticipantRole.OBSERVER},
        min_participants=2,
        max_participants=10,
        allowed_entity_types={
            ParticipantRole.INITIATOR: {"NATION_STATE", "POLITICAL_LEADER"},
            ParticipantRole.RESPONDER: {"NATION_STATE", "POLITICAL_LEADER"},
            ParticipantRole.MEDIATOR: {"INTERNATIONAL_ORGANIZATION", "NATION_STATE"}
        }
    )
    
    # 2. Treaty Formation
    treaty_schema = NAryRelationSchema(
        relation_type=NAryRelationType.TREATY,
        required_roles={ParticipantRole.AGENT, ParticipantRole.INSTRUMENT, ParticipantRole.TARGET},
        optional_roles={ParticipantRole.GUARANTOR, ParticipantRole.BENEFICIARY},
        min_participants=3,
        allowed_entity_types={
            ParticipantRole.AGENT: {"NATION_STATE", "POLITICAL_LEADER"},
            ParticipantRole.INSTRUMENT: {"BILATERAL_TREATY", "ARMS_CONTROL_REGIME"},
            ParticipantRole.TARGET: {"NUCLEAR_DISARMAMENT", "REGIONAL_STABILITY"}
        }
    )
    
    # 3. Policy Implementation
    policy_schema = NAryRelationSchema(
        relation_type=NAryRelationType.POLICY_IMPLEMENTATION,
        required_roles={ParticipantRole.IMPLEMENTER, ParticipantRole.INSTRUMENT, ParticipantRole.TARGET},
        optional_roles={ParticipantRole.CONDITION, ParticipantRole.OUTCOME},
        min_participants=3,
        allowed_entity_types={
            ParticipantRole.IMPLEMENTER: {"NATION_STATE", "GOVERNMENT_INSTITUTION"},
            ParticipantRole.INSTRUMENT: {"NUCLEAR_WEAPONS", "MILITARY_SPENDING", "ECONOMIC_SANCTIONS"},
            ParticipantRole.TARGET: {"BALANCE_OF_POWER", "NUCLEAR_DETERRENCE"}
        }
    )
    
    # 4. Causal Chain
    causal_chain_schema = NAryRelationSchema(
        relation_type=NAryRelationType.CAUSAL_CHAIN,
        required_roles={ParticipantRole.CONDITION, ParticipantRole.OUTCOME},
        optional_roles={ParticipantRole.AGENT, ParticipantRole.CONTEXT},
        min_participants=2,
        max_participants=5
    )
    
    # 5. Strategic Interaction
    strategic_schema = NAryRelationSchema(
        relation_type=NAryRelationType.STRATEGIC_INTERACTION,
        required_roles={ParticipantRole.AGENT, ParticipantRole.TARGET},
        optional_roles={ParticipantRole.CONTEXT, ParticipantRole.INSTRUMENT},
        min_participants=2,
        allowed_entity_types={
            ParticipantRole.AGENT: {"NATION_STATE", "MILITARY_ALLIANCE"},
            ParticipantRole.TARGET: {"NATION_STATE", "BALANCE_OF_POWER"},
            ParticipantRole.CONTEXT: {"DETENTE_CONCEPT", "NUCLEAR_DETERRENCE"}
        }
    )
    
    # Add schemas to the main schema
    schema.add_nary_relation_schema(negotiation_schema)
    schema.add_nary_relation_schema(treaty_schema)
    schema.add_nary_relation_schema(policy_schema)
    schema.add_nary_relation_schema(causal_chain_schema)
    schema.add_nary_relation_schema(strategic_schema)
    
    return schema


def create_carter_detente_nary_analysis() -> Tuple[NAryGraphSchema, List[ReifiedRelationship]]:
    """Create n-ary analysis of Carter's détente speech"""
    
    schema = create_political_nary_schema()
    
    # Define the complex relationships from Carter's speech
    relationships = []
    
    # 1. Détente Negotiation (Multi-party process)
    detente_negotiation = ReifiedRelationship(
        relation_id="detente_negotiation_1977",
        relation_type=NAryRelationType.NEGOTIATION,
        participants=[
            NAryParticipant("usa", ParticipantRole.INITIATOR, "Proposes détente framework"),
            NAryParticipant("ussr", ParticipantRole.RESPONDER, "Must show reciprocity"),
            NAryParticipant("world_peace", ParticipantRole.TARGET, "Ultimate objective"),
            NAryParticipant("mutual_restraint", ParticipantRole.CONDITION, "Required for stability")
        ],
        confidence=0.92,
        political_context="Cold War détente period",
        source_text="Detente between our two countries is central to world peace... must be truly reciprocal",
        evidence_strength=0.89
    )
    
    # 2. Nuclear Balance Policy Implementation
    nuclear_balance_policy = ReifiedRelationship(
        relation_id="nuclear_balance_implementation",
        relation_type=NAryRelationType.POLICY_IMPLEMENTATION,
        participants=[
            NAryParticipant("usa", ParticipantRole.IMPLEMENTER, "Maintains nuclear strength"),
            NAryParticipant("nuclear_weapons", ParticipantRole.INSTRUMENT, "Equivalent nuclear strength"),
            NAryParticipant("nuclear_deterrence", ParticipantRole.TARGET, "Deterrence through equivalency"),
            NAryParticipant("nuclear_disarmament_absence", ParticipantRole.CONDITION, "Until worldwide disarmament"),
            NAryParticipant("world_stability", ParticipantRole.OUTCOME, "Least threatening situation")
        ],
        confidence=0.95,
        source_text="We will continue to maintain equivalent nuclear strength... least threatening and most stable",
        evidence_strength=0.93
    )
    
    # 3. Soviet Military Buildup Strategic Interaction
    soviet_buildup_interaction = ReifiedRelationship(
        relation_id="soviet_buildup_interaction",
        relation_type=NAryRelationType.STRATEGIC_INTERACTION,
        participants=[
            NAryParticipant("ussr", ParticipantRole.AGENT, "Builds military power"),
            NAryParticipant("military_spending", ParticipantRole.INSTRUMENT, "Military assistance"),
            NAryParticipant("global_influence", ParticipantRole.TARGET, "Expanding influence abroad"),
            NAryParticipant("other_nations", ParticipantRole.OBSERVER, "See buildup as excessive"),
            NAryParticipant("defensive_justification", ParticipantRole.CONTEXT, "Beyond legitimate defense")
        ],
        confidence=0.88,
        source_text="Soviet Union apparently sees military power... far beyond legitimate requirement",
        evidence_strength=0.85
    )
    
    # 4. Cooperation Causal Chain
    cooperation_chain = ReifiedRelationship(
        relation_id="cooperation_causal_chain",
        relation_type=NAryRelationType.CAUSAL_CHAIN,
        participants=[
            NAryParticipant("soviet_people_peace_desire", ParticipantRole.CONDITION, "People want peace", temporal_order=1),
            NAryParticipant("cooperation_advantages", ParticipantRole.INSTRUMENT, "Benefits of cooperation", temporal_order=2),
            NAryParticipant("disruptive_behavior_costs", ParticipantRole.INSTRUMENT, "Costs of disruption", temporal_order=2),
            NAryParticipant("soviet_behavior_change", ParticipantRole.OUTCOME, "Convincing USSR", temporal_order=3),
            NAryParticipant("long_term_objective", ParticipantRole.CONTEXT, "Long-term US goal", temporal_order=0)
        ],
        confidence=0.86,
        source_text="I'm convinced that people of Soviet Union want peace... convince Soviet Union of advantages of cooperation",
        evidence_strength=0.83
    )
    
    # 5. NATO Strengthening Treaty
    nato_strengthening = ReifiedRelationship(
        relation_id="nato_strengthening_treaty",
        relation_type=NAryRelationType.TREATY,
        participants=[
            NAryParticipant("usa", ParticipantRole.AGENT, "Commits to stronger NATO"),
            NAryParticipant("nato_alliance", ParticipantRole.INSTRUMENT, "Alliance structure"),
            NAryParticipant("military_spending", ParticipantRole.INSTRUMENT, "Sustained military spending"),
            NAryParticipant("alliance_strength", ParticipantRole.TARGET, "Stronger alliance"),
            NAryParticipant("nato_members", ParticipantRole.BENEFICIARY, "Allied nations")
        ],
        confidence=0.91,
        source_text="We will maintain prudent and sustained level of military spending, keyed to stronger NATO",
        evidence_strength=0.88
    )
    
    # Set up causal dependencies
    detente_negotiation.enables = ["nuclear_balance_implementation", "cooperation_causal_chain"]
    nuclear_balance_policy.dependent_on = ["detente_negotiation_1977"]
    cooperation_chain.dependent_on = ["detente_negotiation_1977"]
    soviet_buildup_interaction.conflicts_with = ["detente_negotiation_1977", "cooperation_causal_chain"]
    
    relationships = [
        detente_negotiation,
        nuclear_balance_policy, 
        soviet_buildup_interaction,
        cooperation_chain,
        nato_strengthening
    ]
    
    # Add relationships to schema
    for rel in relationships:
        schema.add_reified_relationship(rel)
    
    return schema, relationships


def analyze_nary_relationships(schema: NAryGraphSchema, relationships: List[ReifiedRelationship]) -> Dict[str, Any]:
    """Analyze the complexity and sophistication of n-ary relationships"""
    
    analysis = {
        "total_relationships": len(relationships),
        "relationship_types": {},
        "participant_roles": {},
        "complexity_metrics": {},
        "causal_chains": [],
        "conflicts": [],
        "sophistication_score": 0
    }
    
    # Analyze relationship types
    for rel in relationships:
        rel_type = rel.relation_type.value
        if rel_type not in analysis["relationship_types"]:
            analysis["relationship_types"][rel_type] = 0
        analysis["relationship_types"][rel_type] += 1
    
    # Analyze participant roles
    total_participants = 0
    for rel in relationships:
        total_participants += len(rel.participants)
        for participant in rel.participants:
            role = participant.role.value
            if role not in analysis["participant_roles"]:
                analysis["participant_roles"][role] = 0
            analysis["participant_roles"][role] += 1
    
    # Complexity metrics
    analysis["complexity_metrics"] = {
        "avg_participants_per_relation": total_participants / len(relationships) if relationships else 0,
        "unique_participant_roles": len(analysis["participant_roles"]),
        "unique_relation_types": len(analysis["relationship_types"]),
        "max_participants": max(len(r.participants) for r in relationships) if relationships else 0,
        "min_participants": min(len(r.participants) for r in relationships) if relationships else 0
    }
    
    # Causal analysis
    for rel in relationships:
        if rel.enables:
            chain = schema.get_causal_chain(rel.relation_id)
            if len(chain) > 1:
                analysis["causal_chains"].append(chain)
    
    # Conflict analysis
    for rel in relationships:
        if rel.conflicts_with:
            analysis["conflicts"].append({
                "relation": rel.relation_id,
                "conflicts_with": rel.conflicts_with
            })
    
    # Sophistication score (based on complexity and theoretical depth)
    base_score = min(100, len(relationships) * 10)  # Base score from number of relationships
    complexity_bonus = analysis["complexity_metrics"]["avg_participants_per_relation"] * 5
    role_diversity_bonus = len(analysis["participant_roles"]) * 2
    causal_bonus = len(analysis["causal_chains"]) * 8
    
    analysis["sophistication_score"] = base_score + complexity_bonus + role_diversity_bonus + causal_bonus
    
    return analysis