"""
UML Class Diagram Schema System for Political Analysis

This module implements UML-style class-based modeling where:
- Classes contain attributes and methods
- Associations connect classes with cardinalities
- Inheritance creates is-a hierarchies
- Attributes are properties "owned" by classes
- Implementation-focused design (object-oriented bias)

UML Principles:
1. Classes as primary modeling units
2. Attributes encapsulated within classes
3. Associations as relationships between classes
4. Methods define behavior
5. Inheritance for specialization
"""

from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class UMLVisibility(Enum):
    """UML visibility modifiers"""
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    PACKAGE = "~"


class UMLCardinality(Enum):
    """UML association cardinalities"""
    ONE_TO_ONE = "1..1"
    ONE_TO_MANY = "1..*"
    ZERO_TO_ONE = "0..1"
    ZERO_TO_MANY = "0..*"
    MANY_TO_MANY = "*"


class UMLDataType(Enum):
    """UML primitive data types"""
    STRING = "String"
    INTEGER = "Integer"
    BOOLEAN = "Boolean"
    DATE = "Date"
    FLOAT = "Float"
    OBJECT = "Object"


@dataclass
class UMLAttribute:
    """UML class attribute definition"""
    name: str
    data_type: UMLDataType
    visibility: UMLVisibility = UMLVisibility.PUBLIC
    default_value: Optional[Any] = None
    is_derived: bool = False
    multiplicity: str = "1"
    
    def __str__(self) -> str:
        result = f"{self.visibility.value} {self.name}: {self.data_type.value}"
        if self.default_value is not None:
            result += f" = {self.default_value}"
        if self.multiplicity != "1":
            result += f" [{self.multiplicity}]"
        if self.is_derived:
            result = "/" + result
        return result


@dataclass
class UMLMethod:
    """UML class method definition"""
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[UMLDataType] = None
    visibility: UMLVisibility = UMLVisibility.PUBLIC
    is_abstract: bool = False
    
    def __str__(self) -> str:
        params = ", ".join(self.parameters)
        result = f"{self.visibility.value} {self.name}({params})"
        if self.return_type:
            result += f": {self.return_type.value}"
        if self.is_abstract:
            result = "{abstract} " + result
        return result


@dataclass
class UMLAssociation:
    """UML association between classes"""
    name: str
    from_class: str
    to_class: str
    from_cardinality: UMLCardinality
    to_cardinality: UMLCardinality
    from_role: Optional[str] = None
    to_role: Optional[str] = None
    is_aggregation: bool = False
    is_composition: bool = False
    
    def __str__(self) -> str:
        relationship = "◇──" if self.is_aggregation else "◆──" if self.is_composition else "───"
        return f"{self.from_class} ({self.from_cardinality.value}) {relationship} ({self.to_cardinality.value}) {self.to_class}"


@dataclass
class UMLGeneralization:
    """UML inheritance relationship"""
    child_class: str
    parent_class: str
    
    def __str__(self) -> str:
        return f"{self.child_class} ───▷ {self.parent_class}"


@dataclass
class UMLClass:
    """UML class definition"""
    name: str
    attributes: List[UMLAttribute] = field(default_factory=list)
    methods: List[UMLMethod] = field(default_factory=list)
    is_abstract: bool = False
    stereotype: Optional[str] = None
    
    def add_attribute(self, attribute: UMLAttribute) -> None:
        """Add attribute to class"""
        self.attributes.append(attribute)
    
    def add_method(self, method: UMLMethod) -> None:
        """Add method to class"""
        self.methods.append(method)
    
    def get_attribute_by_name(self, name: str) -> Optional[UMLAttribute]:
        """Get attribute by name"""
        return next((attr for attr in self.attributes if attr.name == name), None)
    
    def __str__(self) -> str:
        lines = []
        
        # Class header
        header = self.name
        if self.is_abstract:
            header = f"<<abstract>> {header}"
        if self.stereotype:
            header = f"<<{self.stereotype}>> {header}"
        
        lines.append(f"┌─{header}─┐")
        lines.append("├─" + "─" * len(header) + "─┤")
        
        # Attributes section
        if self.attributes:
            for attr in self.attributes:
                lines.append(f"│ {attr} │")
        else:
            lines.append("│ (no attributes) │")
        
        lines.append("├─" + "─" * len(header) + "─┤")
        
        # Methods section
        if self.methods:
            for method in self.methods:
                lines.append(f"│ {method} │")
        else:
            lines.append("│ (no methods) │")
        
        lines.append("└─" + "─" * len(header) + "─┘")
        
        return "\n".join(lines)


class UMLClassDiagram:
    """Complete UML class diagram for political analysis"""
    
    def __init__(self, name: str):
        self.name = name
        self.classes: Dict[str, UMLClass] = {}
        self.associations: List[UMLAssociation] = []
        self.generalizations: List[UMLGeneralization] = []
    
    def add_class(self, uml_class: UMLClass) -> None:
        """Add class to diagram"""
        self.classes[uml_class.name] = uml_class
    
    def add_association(self, association: UMLAssociation) -> None:
        """Add association to diagram"""
        self.associations.append(association)
    
    def add_generalization(self, generalization: UMLGeneralization) -> None:
        """Add inheritance relationship"""
        self.generalizations.append(generalization)
    
    def generate_class_diagram_text(self) -> str:
        """Generate textual representation of class diagram"""
        lines = [f"UML CLASS DIAGRAM: {self.name}", "=" * 50, ""]
        
        # Classes
        lines.append("CLASSES:")
        lines.append("-" * 20)
        for class_name, uml_class in self.classes.items():
            lines.append(str(uml_class))
            lines.append("")
        
        # Associations
        if self.associations:
            lines.append("ASSOCIATIONS:")
            lines.append("-" * 20)
            for assoc in self.associations:
                lines.append(str(assoc))
            lines.append("")
        
        # Inheritance
        if self.generalizations:
            lines.append("INHERITANCE:")
            lines.append("-" * 20)
            for gen in self.generalizations:
                lines.append(str(gen))
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_plantuml(self) -> str:
        """Generate PlantUML code for the diagram"""
        return self.generate_plantuml_code()
    
    def generate_plantuml_code(self) -> str:
        """Generate PlantUML code for the diagram"""
        lines = ["@startuml", f"title {self.name}", ""]
        
        # Classes
        for class_name, uml_class in self.classes.items():
            if uml_class.is_abstract:
                lines.append(f"abstract class {class_name} {{")
            else:
                lines.append(f"class {class_name} {{")
            
            # Attributes
            for attr in uml_class.attributes:
                lines.append(f"  {attr}")
            
            if uml_class.attributes and uml_class.methods:
                lines.append("  --")
            
            # Methods
            for method in uml_class.methods:
                lines.append(f"  {method}")
            
            lines.append("}")
            lines.append("")
        
        # Associations
        for assoc in self.associations:
            if assoc.is_composition:
                lines.append(f"{assoc.from_class} *-- {assoc.to_class}")
            elif assoc.is_aggregation:
                lines.append(f"{assoc.from_class} o-- {assoc.to_class}")
            else:
                lines.append(f"{assoc.from_class} -- {assoc.to_class}")
        
        # Inheritance
        for gen in self.generalizations:
            lines.append(f"{gen.child_class} --|> {gen.parent_class}")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def validate_diagram(self) -> List[str]:
        """Validate the UML diagram for consistency"""
        errors = []
        
        # Check that association endpoints exist
        for assoc in self.associations:
            if assoc.from_class not in self.classes:
                errors.append(f"Association references undefined class: {assoc.from_class}")
            if assoc.to_class not in self.classes:
                errors.append(f"Association references undefined class: {assoc.to_class}")
        
        # Check that inheritance endpoints exist
        for gen in self.generalizations:
            if gen.child_class not in self.classes:
                errors.append(f"Inheritance references undefined child class: {gen.child_class}")
            if gen.parent_class not in self.classes:
                errors.append(f"Inheritance references undefined parent class: {gen.parent_class}")
        
        # Check for circular inheritance
        inheritance_graph = {}
        for gen in self.generalizations:
            if gen.child_class not in inheritance_graph:
                inheritance_graph[gen.child_class] = []
            inheritance_graph[gen.child_class].append(gen.parent_class)
        
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in inheritance_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in inheritance_graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    errors.append("Circular inheritance detected")
                    break
        
        return errors
    
    def get_statistics(self) -> Dict[str, int]:
        """Get diagram statistics"""
        abstract_classes = sum(1 for cls in self.classes.values() if cls.is_abstract)
        concrete_classes = len(self.classes) - abstract_classes
        total_attributes = sum(len(cls.attributes) for cls in self.classes.values())
        total_methods = sum(len(cls.methods) for cls in self.classes.values())
        
        return {
            "total_classes": len(self.classes),
            "abstract_classes": abstract_classes,
            "concrete_classes": concrete_classes,
            "total_attributes": total_attributes,
            "total_methods": total_methods,
            "associations": len(self.associations),
            "inheritance_relationships": len(self.generalizations)
        }


def create_political_uml_diagram() -> UMLClassDiagram:
    """Create comprehensive UML class diagram for political analysis"""
    
    diagram = UMLClassDiagram("Political Analysis UML Model")
    
    # ========== ABSTRACT BASE CLASSES ==========
    
    # Abstract PoliticalActor
    political_actor = UMLClass("PoliticalActor", is_abstract=True)
    political_actor.add_attribute(UMLAttribute("name", UMLDataType.STRING))
    political_actor.add_attribute(UMLAttribute("establishedDate", UMLDataType.DATE))
    political_actor.add_attribute(UMLAttribute("description", UMLDataType.STRING))
    political_actor.add_method(UMLMethod("getName", [], UMLDataType.STRING))
    political_actor.add_method(UMLMethod("getDescription", [], UMLDataType.STRING))
    political_actor.add_method(UMLMethod("negotiate", ["other: PoliticalActor"], UMLDataType.BOOLEAN, is_abstract=True))
    diagram.add_class(political_actor)
    
    # Abstract Document
    document = UMLClass("Document", is_abstract=True)
    document.add_attribute(UMLAttribute("title", UMLDataType.STRING))
    document.add_attribute(UMLAttribute("createdDate", UMLDataType.DATE))
    document.add_attribute(UMLAttribute("content", UMLDataType.STRING))
    document.add_attribute(UMLAttribute("confidenceScore", UMLDataType.FLOAT))
    document.add_method(UMLMethod("getTitle", [], UMLDataType.STRING))
    document.add_method(UMLMethod("getContent", [], UMLDataType.STRING))
    document.add_method(UMLMethod("analyze", [], UMLDataType.OBJECT, is_abstract=True))
    diagram.add_class(document)
    
    # ========== CONCRETE POLITICAL ACTORS ==========
    
    # Country
    country = UMLClass("Country")
    country.add_attribute(UMLAttribute("countryCode", UMLDataType.STRING))
    country.add_attribute(UMLAttribute("population", UMLDataType.INTEGER))
    country.add_attribute(UMLAttribute("gdp", UMLDataType.FLOAT))
    country.add_attribute(UMLAttribute("militarySpending", UMLDataType.FLOAT))
    country.add_attribute(UMLAttribute("nuclearWarheads", UMLDataType.INTEGER))
    country.add_method(UMLMethod("negotiate", ["other: PoliticalActor"], UMLDataType.BOOLEAN))
    country.add_method(UMLMethod("signTreaty", ["treaty: Treaty"], UMLDataType.BOOLEAN))
    country.add_method(UMLMethod("implementPolicy", ["policy: Policy"], UMLDataType.BOOLEAN))
    diagram.add_class(country)
    diagram.add_generalization(UMLGeneralization("Country", "PoliticalActor"))
    
    # PoliticalLeader
    leader = UMLClass("PoliticalLeader")
    leader.add_attribute(UMLAttribute("firstName", UMLDataType.STRING))
    leader.add_attribute(UMLAttribute("lastName", UMLDataType.STRING))
    leader.add_attribute(UMLAttribute("birthDate", UMLDataType.DATE))
    leader.add_attribute(UMLAttribute("politicalParty", UMLDataType.STRING))
    leader.add_attribute(UMLAttribute("termStart", UMLDataType.DATE))
    leader.add_attribute(UMLAttribute("termEnd", UMLDataType.DATE))
    leader.add_method(UMLMethod("negotiate", ["other: PoliticalActor"], UMLDataType.BOOLEAN))
    leader.add_method(UMLMethod("giveSpeedh", ["topic: String"], UMLDataType.OBJECT))
    leader.add_method(UMLMethod("leadCountry", ["country: Country"], UMLDataType.BOOLEAN))
    diagram.add_class(leader)
    diagram.add_generalization(UMLGeneralization("PoliticalLeader", "PoliticalActor"))
    
    # InternationalOrganization
    intl_org = UMLClass("InternationalOrganization")
    intl_org.add_attribute(UMLAttribute("headquarters", UMLDataType.STRING))
    intl_org.add_attribute(UMLAttribute("memberCount", UMLDataType.INTEGER))
    intl_org.add_attribute(UMLAttribute("budget", UMLDataType.FLOAT))
    intl_org.add_attribute(UMLAttribute("mandate", UMLDataType.STRING))
    intl_org.add_method(UMLMethod("negotiate", ["other: PoliticalActor"], UMLDataType.BOOLEAN))
    intl_org.add_method(UMLMethod("mediate", ["party1: PoliticalActor", "party2: PoliticalActor"], UMLDataType.BOOLEAN))
    intl_org.add_method(UMLMethod("addMember", ["member: Country"], UMLDataType.BOOLEAN))
    diagram.add_class(intl_org)
    diagram.add_generalization(UMLGeneralization("InternationalOrganization", "PoliticalActor"))
    
    # ========== POLICY AND CONCEPT CLASSES ==========
    
    # Policy
    policy = UMLClass("Policy")
    policy.add_attribute(UMLAttribute("policyName", UMLDataType.STRING))
    policy.add_attribute(UMLAttribute("description", UMLDataType.STRING))
    policy.add_attribute(UMLAttribute("implementationDate", UMLDataType.DATE))
    policy.add_attribute(UMLAttribute("objective", UMLDataType.STRING))
    policy.add_attribute(UMLAttribute("budgetAllocation", UMLDataType.FLOAT))
    policy.add_attribute(UMLAttribute("successMetrics", UMLDataType.STRING, multiplicity="*"))
    policy.add_method(UMLMethod("implement", [], UMLDataType.BOOLEAN))
    policy.add_method(UMLMethod("evaluate", [], UMLDataType.FLOAT))
    policy.add_method(UMLMethod("getObjective", [], UMLDataType.STRING))
    diagram.add_class(policy)
    
    # Treaty
    treaty = UMLClass("Treaty")
    treaty.add_attribute(UMLAttribute("treatyName", UMLDataType.STRING))
    treaty.add_attribute(UMLAttribute("signingDate", UMLDataType.DATE))
    treaty.add_attribute(UMLAttribute("effectiveDate", UMLDataType.DATE))
    treaty.add_attribute(UMLAttribute("expirationDate", UMLDataType.DATE))
    treaty.add_attribute(UMLAttribute("provisions", UMLDataType.STRING, multiplicity="*"))
    treaty.add_attribute(UMLAttribute("ratificationStatus", UMLDataType.STRING))
    treaty.add_method(UMLMethod("sign", ["signatory: Country"], UMLDataType.BOOLEAN))
    treaty.add_method(UMLMethod("ratify", ["country: Country"], UMLDataType.BOOLEAN))
    treaty.add_method(UMLMethod("getProvisions", [], UMLDataType.OBJECT))
    diagram.add_class(treaty)
    
    # PoliticalConcept
    concept = UMLClass("PoliticalConcept")
    concept.add_attribute(UMLAttribute("conceptName", UMLDataType.STRING))
    concept.add_attribute(UMLAttribute("definition", UMLDataType.STRING))
    concept.add_attribute(UMLAttribute("theoreticalFramework", UMLDataType.STRING))
    concept.add_attribute(UMLAttribute("historicalContext", UMLDataType.STRING))
    concept.add_attribute(UMLAttribute("academicReferences", UMLDataType.STRING, multiplicity="*"))
    concept.add_method(UMLMethod("define", [], UMLDataType.STRING))
    concept.add_method(UMLMethod("applyTo", ["situation: String"], UMLDataType.OBJECT))
    concept.add_method(UMLMethod("getReferences", [], UMLDataType.OBJECT))
    diagram.add_class(concept)
    
    # ========== RELATIONSHIP/EVENT CLASSES ==========
    
    # Negotiation
    negotiation = UMLClass("Negotiation")
    negotiation.add_attribute(UMLAttribute("negotiationId", UMLDataType.STRING))
    negotiation.add_attribute(UMLAttribute("startDate", UMLDataType.DATE))
    negotiation.add_attribute(UMLAttribute("endDate", UMLDataType.DATE))
    negotiation.add_attribute(UMLAttribute("location", UMLDataType.STRING))
    negotiation.add_attribute(UMLAttribute("topic", UMLDataType.STRING))
    negotiation.add_attribute(UMLAttribute("outcome", UMLDataType.STRING))
    negotiation.add_attribute(UMLAttribute("confidenceLevel", UMLDataType.FLOAT))
    negotiation.add_method(UMLMethod("conduct", [], UMLDataType.BOOLEAN))
    negotiation.add_method(UMLMethod("addParticipant", ["participant: PoliticalActor"], UMLDataType.BOOLEAN))
    negotiation.add_method(UMLMethod("getOutcome", [], UMLDataType.STRING))
    diagram.add_class(negotiation)
    
    # ========== DOCUMENT SUBCLASSES ==========
    
    # Speech
    speech = UMLClass("Speech")
    speech.add_attribute(UMLAttribute("speaker", UMLDataType.STRING))
    speech.add_attribute(UMLAttribute("venue", UMLDataType.STRING))
    speech.add_attribute(UMLAttribute("audience", UMLDataType.STRING))
    speech.add_attribute(UMLAttribute("transcript", UMLDataType.STRING))
    speech.add_attribute(UMLAttribute("keyThemes", UMLDataType.STRING, multiplicity="*"))
    speech.add_method(UMLMethod("analyze", [], UMLDataType.OBJECT))
    speech.add_method(UMLMethod("extractThemes", [], UMLDataType.OBJECT))
    speech.add_method(UMLMethod("getTranscript", [], UMLDataType.STRING))
    diagram.add_class(speech)
    diagram.add_generalization(UMLGeneralization("Speech", "Document"))
    
    # ========== ASSOCIATIONS ==========
    
    # Country-Leader relationship
    diagram.add_association(UMLAssociation(
        "Leadership", "PoliticalLeader", "Country",
        UMLCardinality.ONE_TO_ONE, UMLCardinality.ZERO_TO_ONE,
        "leader", "leads"
    ))
    
    # Country-Treaty relationship (many-to-many)
    diagram.add_association(UMLAssociation(
        "TreatySignatory", "Country", "Treaty",
        UMLCardinality.ZERO_TO_MANY, UMLCardinality.ZERO_TO_MANY,
        "signatory", "signedTreaty"
    ))
    
    # Country-Policy relationship (composition)
    diagram.add_association(UMLAssociation(
        "PolicyImplementation", "Country", "Policy",
        UMLCardinality.ONE_TO_ONE, UMLCardinality.ZERO_TO_MANY,
        "implementer", "nationalPolicy",
        is_composition=True
    ))
    
    # Negotiation-PoliticalActor relationship
    diagram.add_association(UMLAssociation(
        "NegotiationParticipation", "Negotiation", "PoliticalActor",
        UMLCardinality.ZERO_TO_MANY, UMLCardinality.ONE_TO_MANY,
        "participatesIn", "participant"
    ))
    
    # Speech-PoliticalLeader relationship
    diagram.add_association(UMLAssociation(
        "SpeechDelivery", "PoliticalLeader", "Speech",
        UMLCardinality.ONE_TO_ONE, UMLCardinality.ZERO_TO_MANY,
        "speaker", "delivers"
    ))
    
    # Policy-PoliticalConcept relationship  
    diagram.add_association(UMLAssociation(
        "ConceptualBasis", "Policy", "PoliticalConcept",
        UMLCardinality.ZERO_TO_MANY, UMLCardinality.ONE_TO_MANY,
        "basedOn", "informs"
    ))
    
    # Treaty-PoliticalConcept relationship
    diagram.add_association(UMLAssociation(
        "TreatyPrinciple", "Treaty", "PoliticalConcept",
        UMLCardinality.ZERO_TO_MANY, UMLCardinality.ONE_TO_MANY,
        "embodiesPrinciple", "underlies"
    ))
    
    return diagram


def create_carter_uml_instance() -> Dict[str, Any]:
    """Create UML object instances for Carter speech analysis"""
    
    return {
        # Countries
        "usa": {
            "class": "Country",
            "attributes": {
                "name": "United States",
                "countryCode": "USA",
                "population": 220000000,
                "gdp": 2.36e12,
                "militarySpending": 200000000,
                "nuclearWarheads": 10000,
                "establishedDate": "1776-07-04",
                "description": "Democratic republic in North America"
            }
        },
        
        "ussr": {
            "class": "Country", 
            "attributes": {
                "name": "Soviet Union",
                "countryCode": "USSR",
                "population": 260000000,
                "gdp": 1.8e12,
                "militarySpending": 180000000,
                "nuclearWarheads": 12000,
                "establishedDate": "1922-12-30",
                "description": "Communist federation in Eurasia"
            }
        },
        
        # Political Leaders
        "jimmy_carter": {
            "class": "PoliticalLeader",
            "attributes": {
                "name": "Jimmy Carter",
                "firstName": "James",
                "lastName": "Carter",
                "birthDate": "1924-10-01",
                "politicalParty": "Democratic",
                "termStart": "1977-01-20",
                "termEnd": "1981-01-20",
                "establishedDate": "1977-01-20",
                "description": "39th President of the United States"
            }
        },
        
        "leonid_brezhnev": {
            "class": "PoliticalLeader",
            "attributes": {
                "name": "Leonid Brezhnev", 
                "firstName": "Leonid",
                "lastName": "Brezhnev",
                "birthDate": "1906-12-19",
                "politicalParty": "Communist Party",
                "termStart": "1964-10-14",
                "termEnd": "1982-11-10",
                "establishedDate": "1964-10-14",
                "description": "General Secretary of Communist Party USSR"
            }
        },
        
        # Political Concepts
        "detente": {
            "class": "PoliticalConcept",
            "attributes": {
                "conceptName": "Détente",
                "definition": "Easing of strained relations between countries",
                "theoreticalFramework": "Realist international relations theory",
                "historicalContext": "Cold War tension reduction strategy",
                "academicReferences": ["Kissinger (1979)", "Gaddis (2005)"]
            }
        },
        
        "nuclear_deterrence": {
            "class": "PoliticalConcept",
            "attributes": {
                "conceptName": "Nuclear Deterrence",
                "definition": "Prevention of aggression through nuclear threat",
                "theoreticalFramework": "Deterrence theory",
                "historicalContext": "Cold War military strategy",
                "academicReferences": ["Schelling (1960)", "Jervis (1984)"]
            }
        },
        
        "world_peace": {
            "class": "PoliticalConcept", 
            "attributes": {
                "conceptName": "World Peace",
                "definition": "Absence of war and conflict globally",
                "theoreticalFramework": "Liberal internationalism",
                "historicalContext": "Post-WWII international order",
                "academicReferences": ["Kant (1795)", "Doyle (1986)"]
            }
        },
        
        # Policies
        "nuclear_policy": {
            "class": "Policy",
            "attributes": {
                "policyName": "Nuclear Deterrence Policy",
                "description": "Maintain nuclear arsenal for deterrence",
                "implementationDate": "1977-01-20",
                "objective": "Prevent nuclear war through deterrence",
                "budgetAllocation": 50000000,
                "successMetrics": ["No nuclear conflict", "Strategic stability"]
            }
        },
        
        # Treaties
        "salt_treaty": {
            "class": "Treaty",
            "attributes": {
                "treatyName": "SALT I",
                "signingDate": "1972-05-26",
                "effectiveDate": "1972-10-03",
                "expirationDate": "1977-10-03",
                "provisions": ["ABM Treaty", "Interim Agreement on ICBMs"],
                "ratificationStatus": "Ratified"
            }
        },
        
        # Negotiations
        "detente_negotiation": {
            "class": "Negotiation",
            "attributes": {
                "negotiationId": "detente_1977",
                "startDate": "1977-06-01",
                "endDate": "1977-06-15",
                "location": "Vienna",
                "topic": "Strategic Arms Limitation",
                "outcome": "Renewed commitment to détente",
                "confidenceLevel": 0.85
            }
        },
        
        # Speeches
        "carter_speech": {
            "class": "Speech",
            "attributes": {
                "title": "Carter Foreign Policy Speech",
                "createdDate": "1977-06-01",
                "content": "Text of Carter's speech on détente and world peace",
                "confidenceScore": 0.92,
                "speaker": "Jimmy Carter",
                "venue": "White House",
                "audience": "American public",
                "transcript": "Full transcript of foreign policy address",
                "keyThemes": ["détente", "nuclear deterrence", "world peace", "bilateral cooperation"]
            }
        }
    }


def demonstrate_uml_modeling():
    """Demonstrate UML class diagram modeling capabilities"""
    
    print("UML CLASS DIAGRAM POLITICAL ANALYSIS")
    print("=" * 50)
    
    diagram = create_political_uml_diagram()
    
    print("Diagram Statistics:")
    stats = diagram.get_statistics()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nKey UML Features Demonstrated:")
    print(f"  ✓ Class-based modeling with attributes and methods")
    print(f"  ✓ Inheritance hierarchies (PoliticalActor specializations)")
    print(f"  ✓ Associations with cardinalities")
    print(f"  ✓ Composition and aggregation relationships")
    print(f"  ✓ Abstract classes and methods")
    print(f"  ✓ Encapsulation through visibility modifiers")
    
    # Validate diagram
    errors = diagram.validate_diagram()
    print(f"\nDiagram Validation: {'✅ VALID' if not errors else '❌ ERRORS'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    return diagram


if __name__ == "__main__":
    demonstrate_uml_modeling()