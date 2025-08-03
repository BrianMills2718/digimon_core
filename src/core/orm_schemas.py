"""
Object-Role Modeling (ORM) Schema System for Political Analysis

This module implements a fact-based modeling approach where:
- Information is expressed as elementary facts (irreducible propositions)
- All properties are relationships, not attributes (attribute-free modeling)
- Rich semantic constraints ensure data integrity
- Natural language verbalization for domain expert validation
- Conceptual focus independent of implementation details

Core ORM Principles:
1. Fact-Based Modeling: "Person has Name" vs "Person.name" 
2. Attribute-Free: All properties as relationships
3. Conceptual Focus: Business-understandable models
4. Semantic Richness: Precise constraint capture
"""

from typing import Dict, List, Set, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import re


class ObjectTypeCategory(Enum):
    """ORM object type categories"""
    ENTITY = "entity"      # Independent existence and identity
    VALUE = "value"        # Lexical concepts for identification


class ConstraintType(Enum):
    """ORM constraint types"""
    UNIQUENESS = "uniqueness"          # Combination uniquely identifies
    MANDATORY = "mandatory"            # Must participate in role
    FREQUENCY = "frequency"            # Min/max participation count
    SUBSET = "subset"                  # One fact type subset of another
    EXCLUSION = "exclusion"            # Cannot participate in multiple roles
    RING = "ring"                      # Self-referential constraints
    VALUE = "value"                    # Allowed value restrictions


class RingType(Enum):
    """ORM ring constraint types for self-referential facts"""
    ACYCLIC = "acyclic"               # No cycles allowed
    SYMMETRIC = "symmetric"           # If A relates to B, then B relates to A
    ANTISYMMETRIC = "antisymmetric"   # If A relates to B, then B cannot relate to A
    ASYMMETRIC = "asymmetric"         # Neither symmetric nor allows self-relation
    IRREFLEXIVE = "irreflexive"       # Object cannot relate to itself
    INTRANSITIVE = "intransitive"     # If A-B and B-C, then not A-C


@dataclass
class ObjectType:
    """ORM object type (entity or value type)"""
    name: str
    category: ObjectTypeCategory
    description: str = ""
    reference_scheme: Optional[str] = None  # How instances are identified
    
    def __str__(self) -> str:
        border = "solid" if self.category == ObjectTypeCategory.ENTITY else "dashed"
        return f"{self.name} ({border} ellipse)"
    
    def verbalize(self) -> str:
        """Generate natural language description"""
        if self.category == ObjectTypeCategory.ENTITY:
            return f"Each {self.name} is an entity that exists independently."
        else:
            return f"Each {self.name} is a value used for identification or description."


@dataclass
class Role:
    """ORM role within a fact type"""
    name: str
    object_type: str  # Name of the object type playing this role
    role_description: str = ""
    
    def __str__(self) -> str:
        return f"[{self.name}]"


@dataclass
class FactType:
    """ORM fact type representing elementary facts"""
    predicate_text: str  # Natural language predicate with placeholders
    roles: List[Role]
    fact_type_id: str
    examples: List[str] = field(default_factory=list)  # Example instances
    
    def __post_init__(self):
        if not self.fact_type_id:
            # Generate ID from predicate
            self.fact_type_id = re.sub(r'[^a-zA-Z0-9_]', '_', self.predicate_text.lower())
    
    def get_arity(self) -> int:
        """Get the number of roles (arity) of this fact type"""
        return len(self.roles)
    
    def verbalize(self, include_examples: bool = False) -> str:
        """Generate natural language verbalization"""
        # Replace placeholders in predicate with role names
        verbalization = self.predicate_text
        for i, role in enumerate(self.roles):
            placeholder = f"<{i+1}>"
            if placeholder in verbalization:
                verbalization = verbalization.replace(placeholder, f"{{{role.object_type}}}")
        
        result = f"FACT: {verbalization}"
        
        if include_examples and self.examples:
            result += f"\nExamples: {', '.join(self.examples[:3])}"
        
        return result
    
    def get_participating_object_types(self) -> Set[str]:
        """Get all object types participating in this fact"""
        return {role.object_type for role in self.roles}


@dataclass
class UniquenessConstraint:
    """ORM uniqueness constraint"""
    constraint_id: str
    fact_type_id: str
    role_sequence: List[int]  # Indices of roles that form unique combination
    is_preferred_identifier: bool = False
    
    def verbalize(self, fact_type: FactType) -> str:
        """Generate natural language constraint description"""
        if len(self.role_sequence) == 1:
            role_idx = self.role_sequence[0]
            role = fact_type.roles[role_idx]
            return f"Each {role.object_type} {fact_type.predicate_text.split()[1]} at most one thing."
        else:
            role_names = [fact_type.roles[i].object_type for i in self.role_sequence]
            return f"Each combination of {', '.join(role_names)} occurs at most once."


@dataclass
class MandatoryConstraint:
    """ORM mandatory role constraint"""
    constraint_id: str
    fact_type_id: str
    role_index: int  # Index of the mandatory role
    
    def verbalize(self, fact_type: FactType) -> str:
        """Generate natural language constraint description"""
        role = fact_type.roles[self.role_index]
        return f"Each {role.object_type} must participate in this fact type."


@dataclass
class FrequencyConstraint:
    """ORM frequency constraint"""
    constraint_id: str
    fact_type_id: str
    role_index: int
    min_frequency: int = 0
    max_frequency: Optional[int] = None
    
    def verbalize(self, fact_type: FactType) -> str:
        """Generate natural language constraint description"""
        role = fact_type.roles[self.role_index]
        obj_type = role.object_type
        
        if self.max_frequency is None:
            return f"Each {obj_type} must participate at least {self.min_frequency} times."
        elif self.min_frequency == self.max_frequency:
            return f"Each {obj_type} must participate exactly {self.min_frequency} times."
        else:
            return f"Each {obj_type} must participate between {self.min_frequency} and {self.max_frequency} times."


@dataclass
class ValueConstraint:
    """ORM value constraint restricting allowed values"""
    constraint_id: str
    object_type: str
    allowed_values: List[Any]
    
    def verbalize(self) -> str:
        """Generate natural language constraint description"""
        if len(self.allowed_values) <= 5:
            values_str = "', '".join(map(str, self.allowed_values))
            return f"{self.object_type} must be one of: '{values_str}'"
        else:
            return f"{self.object_type} must be one of {len(self.allowed_values)} predefined values"


@dataclass
class RingConstraint:
    """ORM ring constraint for self-referential fact types"""
    constraint_id: str
    fact_type_id: str
    ring_type: RingType
    
    def verbalize(self, fact_type: FactType) -> str:
        """Generate natural language constraint description"""
        if self.ring_type == RingType.ACYCLIC:
            return f"No cycles are allowed in this relationship."
        elif self.ring_type == RingType.SYMMETRIC:
            return f"If A relates to B, then B must relate to A."
        elif self.ring_type == RingType.ANTISYMMETRIC:
            return f"If A relates to B, then B cannot relate to A."
        elif self.ring_type == RingType.IRREFLEXIVE:
            return f"No object can relate to itself."
        else:
            return f"Ring constraint: {self.ring_type.value}"


class ORMSchema:
    """Complete ORM schema for political analysis"""
    
    def __init__(self, schema_name: str):
        self.schema_name = schema_name
        self.object_types: Dict[str, ObjectType] = {}
        self.fact_types: Dict[str, FactType] = {}
        self.uniqueness_constraints: Dict[str, UniquenessConstraint] = {}
        self.mandatory_constraints: Dict[str, MandatoryConstraint] = {}
        self.frequency_constraints: Dict[str, FrequencyConstraint] = {}
        self.value_constraints: Dict[str, ValueConstraint] = {}
        self.ring_constraints: Dict[str, RingConstraint] = {}
    
    @property
    def constraints(self) -> Dict[str, Any]:
        """Compatibility property for demo scripts - returns all constraints"""
        all_constraints = {}
        all_constraints.update(self.uniqueness_constraints)
        all_constraints.update(self.mandatory_constraints)
        all_constraints.update(self.frequency_constraints)
        all_constraints.update(self.value_constraints)
        all_constraints.update(self.ring_constraints)
        return all_constraints
    
    def add_object_type(self, obj_type: ObjectType) -> None:
        """Add an object type to the schema"""
        self.object_types[obj_type.name] = obj_type
    
    def add_fact_type(self, fact_type: FactType) -> None:
        """Add a fact type to the schema"""
        self.fact_types[fact_type.fact_type_id] = fact_type
        
        # Validate that all referenced object types exist
        for role in fact_type.roles:
            if role.object_type not in self.object_types:
                raise ValueError(f"Object type '{role.object_type}' not defined for role in fact type '{fact_type.fact_type_id}'")
    
    def add_constraint(self, constraint: Union[UniquenessConstraint, MandatoryConstraint, 
                                            FrequencyConstraint, ValueConstraint, RingConstraint]) -> None:
        """Add a constraint to the schema"""
        if isinstance(constraint, UniquenessConstraint):
            self.uniqueness_constraints[constraint.constraint_id] = constraint
        elif isinstance(constraint, MandatoryConstraint):
            self.mandatory_constraints[constraint.constraint_id] = constraint
        elif isinstance(constraint, FrequencyConstraint):
            self.frequency_constraints[constraint.constraint_id] = constraint
        elif isinstance(constraint, ValueConstraint):
            self.value_constraints[constraint.constraint_id] = constraint
        elif isinstance(constraint, RingConstraint):
            self.ring_constraints[constraint.constraint_id] = constraint
    
    def validate_schema(self) -> List[str]:
        """Validate the complete schema for consistency"""
        errors = []
        
        # Check that all fact type roles reference existing object types
        for fact_type in self.fact_types.values():
            for role in fact_type.roles:
                if role.object_type not in self.object_types:
                    errors.append(f"Fact type '{fact_type.fact_type_id}' references undefined object type '{role.object_type}'")
        
        # Check that constraints reference existing fact types
        all_constraints = (list(self.uniqueness_constraints.values()) + 
                          list(self.mandatory_constraints.values()) + 
                          list(self.frequency_constraints.values()) + 
                          list(self.ring_constraints.values()))
        
        for constraint in all_constraints:
            if hasattr(constraint, 'fact_type_id') and constraint.fact_type_id not in self.fact_types:
                errors.append(f"Constraint '{constraint.constraint_id}' references undefined fact type '{constraint.fact_type_id}'")
        
        return errors
    
    def verbalize_schema(self, include_examples: bool = False) -> str:
        """Generate complete natural language description of the schema"""
        lines = [f"OBJECT-ROLE MODEL: {self.schema_name}", "=" * 50, ""]
        
        # Object Types
        lines.append("OBJECT TYPES:")
        lines.append("-" * 20)
        for obj_type in self.object_types.values():
            lines.append(f"• {obj_type.verbalize()}")
        lines.append("")
        
        # Fact Types  
        lines.append("FACT TYPES:")
        lines.append("-" * 20)
        for fact_type in self.fact_types.values():
            lines.append(f"• {fact_type.verbalize(include_examples)}")
        lines.append("")
        
        # Constraints
        if self.uniqueness_constraints or self.mandatory_constraints or self.frequency_constraints:
            lines.append("CONSTRAINTS:")
            lines.append("-" * 20)
            
            for constraint in self.uniqueness_constraints.values():
                fact_type = self.fact_types[constraint.fact_type_id]
                lines.append(f"• UNIQUENESS: {constraint.verbalize(fact_type)}")
            
            for constraint in self.mandatory_constraints.values():
                fact_type = self.fact_types[constraint.fact_type_id]
                lines.append(f"• MANDATORY: {constraint.verbalize(fact_type)}")
                
            for constraint in self.frequency_constraints.values():
                fact_type = self.fact_types[constraint.fact_type_id]
                lines.append(f"• FREQUENCY: {constraint.verbalize(fact_type)}")
            
            for constraint in self.value_constraints.values():
                lines.append(f"• VALUE: {constraint.verbalize()}")
                
            for constraint in self.ring_constraints.values():
                fact_type = self.fact_types[constraint.fact_type_id]
                lines.append(f"• RING: {constraint.verbalize(fact_type)}")
        
        return "\n".join(lines)
    
    def verbalize(self) -> str:
        """Compatibility method for demo scripts"""
        return self.verbalize_schema()
    
    def get_schema_statistics(self) -> Dict[str, int]:
        """Get schema complexity statistics"""
        entity_count = sum(1 for obj in self.object_types.values() if obj.category == ObjectTypeCategory.ENTITY)
        value_count = sum(1 for obj in self.object_types.values() if obj.category == ObjectTypeCategory.VALUE)
        
        binary_facts = sum(1 for ft in self.fact_types.values() if ft.get_arity() == 2)
        ternary_facts = sum(1 for ft in self.fact_types.values() if ft.get_arity() == 3)
        nary_facts = sum(1 for ft in self.fact_types.values() if ft.get_arity() > 3)
        
        return {
            "entities": entity_count,
            "values": value_count,
            "total_object_types": len(self.object_types),
            "total_fact_types": len(self.fact_types),
            "binary_facts": binary_facts,
            "ternary_facts": ternary_facts,
            "nary_facts": nary_facts,
            "uniqueness_constraints": len(self.uniqueness_constraints),
            "mandatory_constraints": len(self.mandatory_constraints),
            "frequency_constraints": len(self.frequency_constraints),
            "value_constraints": len(self.value_constraints),
            "ring_constraints": len(self.ring_constraints),
            "total_constraints": (len(self.uniqueness_constraints) + len(self.mandatory_constraints) + 
                                len(self.frequency_constraints) + len(self.value_constraints) + 
                                len(self.ring_constraints))
        }


def create_political_orm_schema() -> ORMSchema:
    """Create comprehensive ORM schema for political analysis"""
    
    schema = ORMSchema("Political Analysis ORM")
    
    # ========== OBJECT TYPES ==========
    
    # Entity Types (Independent existence)
    schema.add_object_type(ObjectType("Person", ObjectTypeCategory.ENTITY, 
                                    "Political actors with independent identity"))
    schema.add_object_type(ObjectType("Country", ObjectTypeCategory.ENTITY,
                                    "Sovereign nation-states"))
    schema.add_object_type(ObjectType("Organization", ObjectTypeCategory.ENTITY,
                                    "Institutional political actors"))
    schema.add_object_type(ObjectType("Treaty", ObjectTypeCategory.ENTITY,
                                    "Formal international agreements"))
    schema.add_object_type(ObjectType("Policy", ObjectTypeCategory.ENTITY,
                                    "Government policy initiatives"))
    schema.add_object_type(ObjectType("Alliance", ObjectTypeCategory.ENTITY,
                                    "Military or political alliances"))
    schema.add_object_type(ObjectType("Concept", ObjectTypeCategory.ENTITY,
                                    "Abstract political concepts"))
    schema.add_object_type(ObjectType("Negotiation", ObjectTypeCategory.ENTITY,
                                    "Diplomatic negotiation processes"))
    
    # Value Types (Lexical identification)
    schema.add_object_type(ObjectType("PersonName", ObjectTypeCategory.VALUE,
                                    "Names identifying persons"))
    schema.add_object_type(ObjectType("CountryName", ObjectTypeCategory.VALUE,
                                    "Names identifying countries"))
    schema.add_object_type(ObjectType("CountryCode", ObjectTypeCategory.VALUE,
                                    "ISO country codes"))
    schema.add_object_type(ObjectType("OrganizationName", ObjectTypeCategory.VALUE,
                                    "Names identifying organizations"))
    schema.add_object_type(ObjectType("TreatyName", ObjectTypeCategory.VALUE,
                                    "Names identifying treaties"))
    schema.add_object_type(ObjectType("PolicyName", ObjectTypeCategory.VALUE,
                                    "Names identifying policies"))
    schema.add_object_type(ObjectType("ConceptName", ObjectTypeCategory.VALUE,
                                    "Names identifying concepts"))
    schema.add_object_type(ObjectType("Date", ObjectTypeCategory.VALUE,
                                    "Temporal identifiers"))
    schema.add_object_type(ObjectType("Amount", ObjectTypeCategory.VALUE,
                                    "Numeric quantities"))
    schema.add_object_type(ObjectType("Percentage", ObjectTypeCategory.VALUE,
                                    "Percentage values"))
    schema.add_object_type(ObjectType("ConfidenceLevel", ObjectTypeCategory.VALUE,
                                    "Analysis confidence ratings"))
    schema.add_object_type(ObjectType("RoleName", ObjectTypeCategory.VALUE,
                                    "Names of roles in relationships"))
    
    # ========== FACT TYPES ==========
    
    # Basic identification facts
    schema.add_fact_type(FactType(
        "Person <1> has PersonName <2>",
        [Role("person", "Person"), Role("name", "PersonName")],
        "person_has_name",
        ["Jimmy Carter has PersonName 'Jimmy Carter'", "Leonid Brezhnev has PersonName 'Leonid Brezhnev'"]
    ))
    
    schema.add_fact_type(FactType(
        "Country <1> has CountryName <2>",
        [Role("country", "Country"), Role("name", "CountryName")],
        "country_has_name",
        ["USA has CountryName 'United States'", "USSR has CountryName 'Soviet Union'"]
    ))
    
    schema.add_fact_type(FactType(
        "Country <1> has CountryCode <2>",
        [Role("country", "Country"), Role("code", "CountryCode")],
        "country_has_code",
        ["USA has CountryCode 'US'", "USSR has CountryCode 'SU'"]
    ))
    
    # Leadership facts
    schema.add_fact_type(FactType(
        "Person <1> leads Country <2> on Date <3>",
        [Role("leader", "Person"), Role("country", "Country"), Role("date", "Date")],
        "person_leads_country",
        ["Jimmy Carter leads USA on Date '1977-06-01'"]
    ))
    
    # Negotiation facts (complex multi-role)
    schema.add_fact_type(FactType(
        "Person <1> initiates Negotiation <2> with Person <3> regarding Concept <4> on Date <5>",
        [Role("initiator", "Person"), Role("negotiation", "Negotiation"), 
         Role("responder", "Person"), Role("topic", "Concept"), Role("date", "Date")],
        "negotiation_initiation",
        ["Jimmy Carter initiates Negotiation détente_talks with Leonid Brezhnev regarding Concept détente on Date '1977-06-01'"]
    ))
    
    # Policy implementation facts
    schema.add_fact_type(FactType(
        "Country <1> implements Policy <2> to achieve Concept <3> with ConfidenceLevel <4>",
        [Role("implementer", "Country"), Role("policy", "Policy"), 
         Role("objective", "Concept"), Role("confidence", "ConfidenceLevel")],
        "policy_implementation",
        ["USA implements Policy nuclear_deterrence to achieve Concept strategic_balance with ConfidenceLevel 0.85"]
    ))
    
    # Alliance membership facts
    schema.add_fact_type(FactType(
        "Country <1> participates in Alliance <2> with RoleName <3> from Date <4>",
        [Role("member", "Country"), Role("alliance", "Alliance"), 
         Role("role", "RoleName"), Role("start_date", "Date")],
        "alliance_participation",
        ["USA participates in Alliance NATO with RoleName 'founding_member' from Date '1949-04-04'"]
    ))
    
    # Treaty signing facts
    schema.add_fact_type(FactType(
        "Country <1> signs Treaty <2> with Country <3> on Date <4>",
        [Role("signatory1", "Country"), Role("treaty", "Treaty"), 
         Role("signatory2", "Country"), Role("date", "Date")],
        "treaty_signing",
        ["USA signs Treaty SALT_I with USSR on Date '1972-05-26'"]
    ))
    
    # Causal relationship facts
    schema.add_fact_type(FactType(
        "Concept <1> enables Concept <2> with ConfidenceLevel <3>",
        [Role("cause", "Concept"), Role("effect", "Concept"), Role("confidence", "ConfidenceLevel")],
        "causal_relationship",
        ["Concept détente enables Concept bilateral_cooperation with ConfidenceLevel 0.78"]
    ))
    
    # Military spending facts
    schema.add_fact_type(FactType(
        "Country <1> spends Amount <2> on military in Date <3>",
        [Role("spender", "Country"), Role("amount", "Amount"), Role("year", "Date")],
        "military_spending",
        ["USA spends Amount 200000000 on military in Date '1977'"]
    ))
    
    # Conflict facts (self-referential)
    schema.add_fact_type(FactType(
        "Country <1> opposes Country <2> regarding Concept <3>",
        [Role("opponent1", "Country"), Role("opponent2", "Country"), Role("issue", "Concept")],
        "country_opposition",
        ["USA opposes USSR regarding Concept nuclear_proliferation"]
    ))
    
    # ========== CONSTRAINTS ==========
    
    # Uniqueness constraints (preferred identifiers)
    schema.add_constraint(UniquenessConstraint(
        "person_name_unique", "person_has_name", [1], is_preferred_identifier=True
    ))
    
    schema.add_constraint(UniquenessConstraint(
        "country_code_unique", "country_has_code", [1], is_preferred_identifier=True
    ))
    
    schema.add_constraint(UniquenessConstraint(
        "negotiation_unique", "negotiation_initiation", [0, 2, 3], is_preferred_identifier=True
    ))
    
    # Mandatory constraints
    schema.add_constraint(MandatoryConstraint(
        "person_must_have_name", "person_has_name", 0
    ))
    
    schema.add_constraint(MandatoryConstraint(
        "country_must_have_name", "country_has_name", 0
    ))
    
    schema.add_constraint(MandatoryConstraint(
        "country_must_have_code", "country_has_code", 0
    ))
    
    # Frequency constraints
    schema.add_constraint(FrequencyConstraint(
        "person_one_name", "person_has_name", 0, min_frequency=1, max_frequency=1
    ))
    
    schema.add_constraint(FrequencyConstraint(
        "country_leadership_max", "person_leads_country", 1, min_frequency=0, max_frequency=1
    ))
    
    # Value constraints
    schema.add_constraint(ValueConstraint(
        "confidence_range", "ConfidenceLevel", [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    ))
    
    schema.add_constraint(ValueConstraint(
        "role_types", "RoleName", 
        ["founding_member", "full_member", "observer", "partner", "ally", "neutral"]
    ))
    
    # Ring constraints for self-referential facts
    schema.add_constraint(RingConstraint(
        "opposition_symmetric", "country_opposition", RingType.SYMMETRIC
    ))
    
    return schema


def create_carter_orm_instance(schema: ORMSchema) -> Dict[str, List[Tuple]]:
    """Create ORM instance data for Carter speech analysis"""
    
    instances = {
        # Basic identification facts
        "person_has_name": [
            ("jimmy_carter", "Jimmy Carter"),
            ("leonid_brezhnev", "Leonid Brezhnev")
        ],
        
        "country_has_name": [
            ("usa", "United States"),
            ("ussr", "Soviet Union")
        ],
        
        "country_has_code": [
            ("usa", "US"),
            ("ussr", "SU")
        ],
        
        # Leadership facts
        "person_leads_country": [
            ("jimmy_carter", "usa", "1977-06-01")
        ],
        
        # Negotiation facts
        "negotiation_initiation": [
            ("jimmy_carter", "detente_negotiation", "leonid_brezhnev", "detente_concept", "1977-06-01")
        ],
        
        # Policy implementation facts
        "policy_implementation": [
            ("usa", "nuclear_deterrence_policy", "strategic_balance", 0.85),
            ("usa", "nato_strengthening", "alliance_solidarity", 0.78)
        ],
        
        # Alliance participation facts
        "alliance_participation": [
            ("usa", "nato", "founding_member", "1949-04-04")
        ],
        
        # Causal relationship facts
        "causal_relationship": [
            ("detente_concept", "bilateral_cooperation", 0.82),
            ("nuclear_deterrence", "strategic_stability", 0.88),
            ("mutual_restraint", "tension_reduction", 0.75)
        ],
        
        # Military spending facts
        "military_spending": [
            ("usa", 200000000, "1977"),
            ("ussr", 180000000, "1977")
        ],
        
        # Opposition facts
        "country_opposition": [
            ("usa", "ussr", "nuclear_proliferation"),
            ("ussr", "usa", "western_influence")
        ]
    }
    
    return instances