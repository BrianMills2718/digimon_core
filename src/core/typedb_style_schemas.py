"""
TypeDB-Style Schema System for Political Analysis

Inspired by TypeDB's Enhanced Entity-Relation-Attribute model, this module
provides a TypeDB-style schema system where:
- Entities, relations, and attributes are first-class citizens
- Strong type inheritance with abstract and concrete types
- Polymorphic queries and type inference
- Symbolic reasoning through rules
- Native support for n-ary relationships without reification
"""

from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class TypeDBEntityType(Enum):
    """TypeDB-style entity type categories"""
    ENTITY = "entity"
    RELATION = "relation" 
    ATTRIBUTE = "attribute"


class TypeDBValueType(Enum):
    """TypeDB attribute value types"""
    STRING = "string"
    LONG = "long"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    DATETIME = "datetime"


@dataclass
class TypeDBAttribute:
    """TypeDB-style attribute definition"""
    name: str
    value_type: TypeDBValueType
    abstract: bool = False
    parent: Optional[str] = None
    unique: bool = False
    key: bool = False
    
    def __str__(self) -> str:
        parts = [f"{self.name} sub attribute"]
        if self.abstract:
            parts.append("abstract")
        if self.parent and self.parent != "attribute":
            parts = [f"{self.name} sub {self.parent}"]
        parts.append(f"value {self.value_type.value}")
        if self.unique:
            parts.append("@unique")
        if self.key:
            parts.append("@key")
        return ", ".join(parts) + ";"


@dataclass
class TypeDBRole:
    """TypeDB-style relation role"""
    name: str
    cardinality: Optional[str] = None  # "one", "many", etc.
    
    def __str__(self) -> str:
        return f"relates {self.name}"


@dataclass
class TypeDBEntity:
    """TypeDB-style entity definition"""
    name: str
    abstract: bool = False
    parent: Optional[str] = None
    owns_attributes: List[str] = field(default_factory=list)
    plays_roles: List[str] = field(default_factory=list)  # Format: "relation:role"
    
    def __str__(self) -> str:
        parts = [f"{self.name} sub entity"]
        if self.abstract:
            parts.append("abstract")
        if self.parent and self.parent != "entity":
            parts = [f"{self.name} sub {self.parent}"]
        
        result = ", ".join(parts)
        
        if self.owns_attributes:
            owns_clauses = [f"owns {attr}" for attr in self.owns_attributes]
            result += ",\n    " + ",\n    ".join(owns_clauses)
        
        if self.plays_roles:
            plays_clauses = [f"plays {role}" for role in self.plays_roles]
            result += ",\n    " + ",\n    ".join(plays_clauses)
        
        return result + ";"


@dataclass 
class TypeDBRelation:
    """TypeDB-style relation definition"""
    name: str
    abstract: bool = False
    parent: Optional[str] = None
    roles: List[TypeDBRole] = field(default_factory=list)
    owns_attributes: List[str] = field(default_factory=list)
    plays_roles: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        parts = [f"{self.name} sub relation"]
        if self.abstract:
            parts.append("abstract")
        if self.parent and self.parent != "relation":
            parts = [f"{self.name} sub {self.parent}"]
        
        result = ", ".join(parts)
        
        if self.roles:
            role_clauses = [str(role) for role in self.roles]
            result += ",\n    " + ",\n    ".join(role_clauses)
        
        if self.owns_attributes:
            owns_clauses = [f"owns {attr}" for attr in self.owns_attributes]
            result += ",\n    " + ",\n    ".join(owns_clauses)
        
        if self.plays_roles:
            plays_clauses = [f"plays {role}" for role in self.plays_roles]
            result += ",\n    " + ",\n    ".join(plays_clauses)
        
        return result + ";"


@dataclass
class TypeDBRule:
    """TypeDB-style deductive rule"""
    name: str
    when_conditions: List[str]
    then_conclusions: List[str]
    
    def __str__(self) -> str:
        when_clause = ";\n      ".join(self.when_conditions)
        then_clause = ";\n      ".join(self.then_conclusions)
        
        return f"""rule {self.name}:
    when {{
      {when_clause};
    }} then {{
      {then_clause};
    }};"""


class TypeDBPoliticalSchema:
    """TypeDB-style schema for sophisticated political analysis"""
    
    def __init__(self):
        self.attributes: Dict[str, TypeDBAttribute] = {}
        self.entities: Dict[str, TypeDBEntity] = {}
        self.relations: Dict[str, TypeDBRelation] = {}
        self.rules: Dict[str, TypeDBRule] = {}
        
        self._define_political_schema()
    
    # Add compatibility properties for demo scripts
    @property
    def entity_types(self) -> Dict[str, TypeDBEntity]:
        """Compatibility property for demo scripts"""
        return self.entities
    
    @property
    def relation_types(self) -> Dict[str, TypeDBRelation]:
        """Compatibility property for demo scripts"""
        return self.relations
    
    def _define_political_schema(self):
        """Define comprehensive political analysis schema in TypeDB style"""
        
        # ========== ATTRIBUTES ==========
        
        # Base attributes
        self.attributes["id"] = TypeDBAttribute("id", TypeDBValueType.STRING, abstract=True)
        self.attributes["name"] = TypeDBAttribute("name", TypeDBValueType.STRING)
        self.attributes["description"] = TypeDBAttribute("description", TypeDBValueType.STRING)
        self.attributes["confidence"] = TypeDBAttribute("confidence", TypeDBValueType.DOUBLE)
        self.attributes["timestamp"] = TypeDBAttribute("timestamp", TypeDBValueType.DATETIME)
        
        # Political-specific attributes
        self.attributes["country-code"] = TypeDBAttribute("country-code", TypeDBValueType.STRING, parent="id", unique=True)
        self.attributes["leader-name"] = TypeDBAttribute("leader-name", TypeDBValueType.STRING, parent="name")
        self.attributes["treaty-name"] = TypeDBAttribute("treaty-name", TypeDBValueType.STRING, parent="name")
        self.attributes["policy-name"] = TypeDBAttribute("policy-name", TypeDBValueType.STRING, parent="name")
        self.attributes["concept-name"] = TypeDBAttribute("concept-name", TypeDBValueType.STRING, parent="name")
        
        # Measurement attributes
        self.attributes["military-spending"] = TypeDBAttribute("military-spending", TypeDBValueType.LONG)
        self.attributes["nuclear-warheads"] = TypeDBAttribute("nuclear-warheads", TypeDBValueType.LONG)
        self.attributes["alliance-strength"] = TypeDBAttribute("alliance-strength", TypeDBValueType.DOUBLE)
        
        # ========== ENTITIES ==========
        
        # Abstract political actor
        self.entities["political-actor"] = TypeDBEntity(
            name="political-actor",
            abstract=True,
            owns_attributes=["name", "confidence"],
            plays_roles=["negotiation:initiator", "negotiation:responder", "alliance:member", 
                        "conflict:aggressor", "conflict:defender", "treaty-signing:signatory"]
        )
        
        # Concrete political actors
        self.entities["nation-state"] = TypeDBEntity(
            name="nation-state",
            parent="political-actor",
            owns_attributes=["country-code", "military-spending", "nuclear-warheads"],
            plays_roles=["bilateral-relations:state-a", "bilateral-relations:state-b",
                        "containment:container", "containment:contained"]
        )
        
        self.entities["political-leader"] = TypeDBEntity(
            name="political-leader", 
            parent="political-actor",
            owns_attributes=["leader-name"],
            plays_roles=["leadership:leader", "negotiation:chief-negotiator"]
        )
        
        self.entities["government-institution"] = TypeDBEntity(
            name="government-institution",
            parent="political-actor",
            owns_attributes=["description"],
            plays_roles=["policy-implementation:implementer"]
        )
        
        self.entities["international-organization"] = TypeDBEntity(
            name="international-organization",
            parent="political-actor",
            plays_roles=["mediation:mediator", "alliance:coordinator"]
        )
        
        # Abstract concepts as entities (TypeDB style)
        self.entities["political-concept"] = TypeDBEntity(
            name="political-concept",
            abstract=True,
            owns_attributes=["concept-name", "description"],
            plays_roles=["policy-implementation:guiding-principle", "strategic-thinking:framework"]
        )
        
        self.entities["detente-concept"] = TypeDBEntity(
            name="detente-concept",
            parent="political-concept",
            plays_roles=["negotiation:underlying-principle", "tension-reduction:mechanism"]
        )
        
        self.entities["balance-of-power"] = TypeDBEntity(
            name="balance-of-power",
            parent="political-concept", 
            plays_roles=["strategic-balance:principle", "alliance:rationale"]
        )
        
        self.entities["nuclear-deterrence"] = TypeDBEntity(
            name="nuclear-deterrence",
            parent="political-concept",
            plays_roles=["nuclear-policy:doctrine", "strategic-balance:mechanism"]
        )
        
        # Policy instruments
        self.entities["policy-instrument"] = TypeDBEntity(
            name="policy-instrument",
            abstract=True,
            owns_attributes=["policy-name", "description"],
            plays_roles=["policy-implementation:instrument"]
        )
        
        self.entities["nuclear-weapons"] = TypeDBEntity(
            name="nuclear-weapons",
            parent="policy-instrument",
            owns_attributes=["nuclear-warheads"],
            plays_roles=["nuclear-policy:instrument", "deterrence:weapon"]
        )
        
        self.entities["military-alliance"] = TypeDBEntity(
            name="military-alliance",
            parent="policy-instrument",
            owns_attributes=["alliance-strength"],
            plays_roles=["alliance:structure", "collective-defense:mechanism"]
        )
        
        # Strategic objectives
        self.entities["strategic-objective"] = TypeDBEntity(
            name="strategic-objective",
            abstract=True,
            owns_attributes=["name", "description"],
            plays_roles=["policy-implementation:objective", "negotiation:goal"]
        )
        
        self.entities["world-peace"] = TypeDBEntity(
            name="world-peace",
            parent="strategic-objective",
            plays_roles=["negotiation:ultimate-goal", "detente:objective"]
        )
        
        self.entities["nuclear-disarmament"] = TypeDBEntity(
            name="nuclear-disarmament",
            parent="strategic-objective",
            plays_roles=["arms-control:objective", "treaty-signing:goal"]
        )
        
        # ========== RELATIONS ==========
        
        # Core political relations
        self.relations["negotiation"] = TypeDBRelation(
            name="negotiation",
            roles=[
                TypeDBRole("initiator"),
                TypeDBRole("responder"), 
                TypeDBRole("mediator"),
                TypeDBRole("underlying-principle"),
                TypeDBRole("goal"),
                TypeDBRole("ultimate-goal")
            ],
            owns_attributes=["confidence", "timestamp"],
            plays_roles=["causal-sequence:cause", "causal-sequence:effect"]
        )
        
        self.relations["alliance"] = TypeDBRelation(
            name="alliance",
            roles=[
                TypeDBRole("member"),
                TypeDBRole("coordinator"),
                TypeDBRole("structure"),
                TypeDBRole("rationale")
            ],
            owns_attributes=["alliance-strength", "timestamp"]
        )
        
        self.relations["policy-implementation"] = TypeDBRelation(
            name="policy-implementation",
            roles=[
                TypeDBRole("implementer"),
                TypeDBRole("instrument"),
                TypeDBRole("objective"),
                TypeDBRole("guiding-principle")
            ],
            owns_attributes=["confidence", "timestamp"],
            plays_roles=["causal-sequence:cause", "causal-sequence:effect"]
        )
        
        self.relations["nuclear-policy"] = TypeDBRelation(
            name="nuclear-policy",
            parent="policy-implementation",
            roles=[
                TypeDBRole("doctrine"),
                TypeDBRole("instrument")
            ]
        )
        
        self.relations["bilateral-relations"] = TypeDBRelation(
            name="bilateral-relations",
            roles=[
                TypeDBRole("state-a"),
                TypeDBRole("state-b")
            ],
            owns_attributes=["description", "confidence"]
        )
        
        self.relations["containment"] = TypeDBRelation(
            name="containment",
            parent="bilateral-relations",
            roles=[
                TypeDBRole("container"),
                TypeDBRole("contained")
            ]
        )
        
        self.relations["treaty-signing"] = TypeDBRelation(
            name="treaty-signing",
            roles=[
                TypeDBRole("signatory"),
                TypeDBRole("goal")
            ],
            owns_attributes=["treaty-name", "timestamp"]
        )
        
        # Meta-relation for causality
        self.relations["causal-sequence"] = TypeDBRelation(
            name="causal-sequence",
            roles=[
                TypeDBRole("cause"),
                TypeDBRole("effect")
            ],
            owns_attributes=["confidence", "timestamp"]
        )
        
        # Strategic analysis relations
        self.relations["strategic-balance"] = TypeDBRelation(
            name="strategic-balance",
            roles=[
                TypeDBRole("principle"),
                TypeDBRole("mechanism")
            ],
            owns_attributes=["confidence"]
        )
        
        self.relations["tension-reduction"] = TypeDBRelation(
            name="tension-reduction",
            roles=[
                TypeDBRole("mechanism")
            ],
            owns_attributes=["confidence"]
        )
        
        # ========== RULES ==========
        
        # Rule: Transitive alliance membership
        self.rules["transitive-alliance"] = TypeDBRule(
            name="transitive-alliance",
            when_conditions=[
                "(member: $state-a, member: $state-b) isa alliance",
                "(member: $state-b, member: $state-c) isa alliance"
            ],
            then_conclusions=[
                "(member: $state-a, member: $state-c) isa alliance"
            ]
        )
        
        # Rule: Détente enables cooperation
        self.rules["detente-enables-cooperation"] = TypeDBRule(
            name="detente-enables-cooperation",
            when_conditions=[
                "(initiator: $state-a, responder: $state-b, underlying-principle: $detente) isa negotiation",
                "$detente isa detente-concept"
            ],
            then_conclusions=[
                "(state-a: $state-a, state-b: $state-b) isa bilateral-relations"
            ]
        )
        
        # Rule: Nuclear weapons enable deterrence
        self.rules["nuclear-deterrence-policy"] = TypeDBRule(
            name="nuclear-deterrence-policy",
            when_conditions=[
                "(implementer: $state, instrument: $weapons, objective: $deterrence) isa policy-implementation",
                "$weapons isa nuclear-weapons",
                "$deterrence isa nuclear-deterrence"
            ],
            then_conclusions=[
                "(doctrine: $deterrence, instrument: $weapons) isa nuclear-policy"
            ]
        )
        
        # Rule: Balance of power through alliances
        self.rules["balance-through-alliance"] = TypeDBRule(
            name="balance-through-alliance",
            when_conditions=[
                "(member: $state, structure: $alliance-entity, rationale: $balance) isa alliance",
                "$balance isa balance-of-power",
                "$alliance-entity isa military-alliance"
            ],
            then_conclusions=[
                "(principle: $balance, mechanism: $alliance-entity) isa strategic-balance"
            ]
        )
    
    def to_typeql(self) -> str:
        """Compatibility method for demo scripts"""
        return self.generate_schema_definition()
    
    def generate_schema_definition(self) -> str:
        """Generate complete TypeDB schema definition"""
        
        lines = ["define\n"]
        
        # Attributes
        lines.append("  # ========== ATTRIBUTES ==========")
        for attr in self.attributes.values():
            lines.append(f"  {attr}")
        
        lines.append("\n  # ========== ENTITIES ==========")
        for entity in self.entities.values():
            entity_def = str(entity).replace('\n', '\n  ')
            lines.append(f"  {entity_def}")
        
        lines.append("\n  # ========== RELATIONS ==========") 
        for relation in self.relations.values():
            relation_def = str(relation).replace('\n', '\n  ')
            lines.append(f"  {relation_def}")
        
        lines.append("\n  # ========== RULES ==========")
        for rule in self.rules.values():
            rule_def = str(rule).replace('\n', '\n  ')
            lines.append(f"  {rule_def}")
        
        return "\n".join(lines)
    
    def generate_carter_data_insertion(self) -> str:
        """Generate TypeDB data insertion for Carter speech analysis"""
        
        return """
insert

  # ========== ENTITIES ==========
  
  # Nation states
  $usa isa nation-state,
    has country-code "USA",
    has name "United States",
    has military-spending 200000000;
  
  $ussr isa nation-state,
    has country-code "USSR", 
    has name "Soviet Union",
    has military-spending 180000000;
  
  # Political concepts
  $detente isa detente-concept,
    has concept-name "détente",
    has description "Easing of tension between nations";
  
  $balance isa balance-of-power,
    has concept-name "balance of power",
    has description "Strategic equilibrium";
  
  $deterrence isa nuclear-deterrence,
    has concept-name "nuclear deterrence",
    has description "Prevention through nuclear threat";
  
  # Strategic objectives  
  $world-peace isa world-peace,
    has name "world peace",
    has description "Global peaceful coexistence";
  
  $disarmament isa nuclear-disarmament,
    has name "nuclear disarmament",
    has description "Elimination of nuclear weapons";
  
  # Policy instruments
  $nuclear-weapons isa nuclear-weapons,
    has policy-name "nuclear arsenal",
    has nuclear-warheads 10000;
  
  $nato isa military-alliance,
    has policy-name "NATO alliance",
    has alliance-strength 0.85;
  
  # ========== RELATIONS ==========
  
  # Détente negotiation
  (initiator: $usa, responder: $ussr, underlying-principle: $detente, ultimate-goal: $world-peace) isa negotiation,
    has confidence 0.92,
    has timestamp 2024-01-01T00:00:00;
  
  # Nuclear policy implementation
  (implementer: $usa, instrument: $nuclear-weapons, objective: $deterrence, guiding-principle: $balance) isa policy-implementation,
    has confidence 0.95,
    has timestamp 2024-01-01T00:00:00;
  
  # US-USSR bilateral relations
  (state-a: $usa, state-b: $ussr) isa bilateral-relations,
    has description "Cold War superpower relations",
    has confidence 0.88;
  
  # NATO alliance
  (member: $usa, structure: $nato, rationale: $balance) isa alliance,
    has alliance-strength 0.85,
    has timestamp 2024-01-01T00:00:00;
"""
    
    def generate_example_queries(self) -> List[str]:
        """Generate example TypeDB queries for political analysis"""
        
        return [
            # Polymorphic query for all political actors
            """
match
  $actor isa $actor-type;
  $actor-type sub political-actor;
  $actor has name $name;
fetch 
  $name;
  $actor-type;
""",
            
            # Complex negotiation analysis
            """
match
  (initiator: $init, responder: $resp, underlying-principle: $principle, ultimate-goal: $goal) isa negotiation;
  $init isa nation-state, has name $init-name;
  $resp isa nation-state, has name $resp-name;
  $principle isa $principle-type;
  $goal isa $goal-type;
fetch
  $init-name;
  $resp-name;
  $principle-type;
  $goal-type;
""",
            
            # Policy implementation with instruments
            """
match
  (implementer: $impl, instrument: $instr, objective: $obj) isa policy-implementation;
  $impl has name $impl-name;
  $instr isa $instr-type;
  $obj isa $obj-type;
fetch
  $impl-name;
  $instr-type;
  $obj-type;
""",
            
            # Causal reasoning through rules
            """
match
  (cause: $cause, effect: $effect) isa causal-sequence;
  $cause isa $cause-type;
  $effect isa $effect-type;
fetch
  $cause-type;
  $effect-type;
""",
            
            # Strategic balance analysis  
            """
match
  (principle: $principle, mechanism: $mechanism) isa strategic-balance;
  $principle isa balance-of-power;
  $mechanism isa $mech-type;
  $mechanism has policy-name $mech-name;
fetch
  $mech-type;
  $mech-name;
"""
        ]


def create_typedb_political_schema() -> TypeDBPoliticalSchema:
    """Create and return a TypeDB-style political analysis schema"""
    return TypeDBPoliticalSchema()


def demonstrate_typedb_style_modeling():
    """Demonstrate TypeDB-style modeling capabilities"""
    
    print("TYPEDB-STYLE POLITICAL ANALYSIS SCHEMA")
    print("=" * 60)
    
    schema = create_typedb_political_schema()
    
    print("Schema Components:")
    print(f"  Attributes: {len(schema.attributes)}")
    print(f"  Entities: {len(schema.entities)}")
    print(f"  Relations: {len(schema.relations)}")
    print(f"  Rules: {len(schema.rules)}")
    
    print(f"\nKey TypeDB Features Demonstrated:")
    print(f"  ✓ Enhanced Entity-Relation-Attribute model")
    print(f"  ✓ Type inheritance with abstract and concrete types")
    print(f"  ✓ Native n-ary relationships (no reification needed)")
    print(f"  ✓ Polymorphic queries with type variables")
    print(f"  ✓ Symbolic reasoning through deductive rules")
    print(f"  ✓ Strong type system with validation")
    
    return schema


if __name__ == "__main__":
    demonstrate_typedb_style_modeling()