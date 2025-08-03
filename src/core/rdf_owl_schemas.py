"""
RDF/OWL Ontology Schema System for Political Analysis

This module implements RDF (Resource Description Framework) and OWL (Web Ontology Language)
modeling where:
- Everything is expressed as RDF triples (subject-predicate-object)
- OWL provides formal ontology with classes, properties, and reasoning rules
- URIs uniquely identify all resources
- Semantic web standards for interoperability
- Formal logic foundation for automated reasoning

RDF/OWL Principles:
1. Triple-based knowledge representation
2. URI-based global identification
3. Formal ontology with logical constraints
4. Automated reasoning and inference
5. Open-world assumption
6. Web-scale interoperability
"""

from typing import Dict, List, Set, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import re


class RDFDataType(Enum):
    """RDF/XSD data types"""
    STRING = "xsd:string"
    INTEGER = "xsd:integer"
    DECIMAL = "xsd:decimal"
    BOOLEAN = "xsd:boolean"
    DATE = "xsd:date"
    DATETIME = "xsd:dateTime"
    URI = "xsd:anyURI"


class OWLClassExpression(Enum):
    """OWL class expression types"""
    INTERSECTION = "owl:intersectionOf"
    UNION = "owl:unionOf"
    COMPLEMENT = "owl:complementOf"
    SOME_VALUES_FROM = "owl:someValuesFrom"
    ALL_VALUES_FROM = "owl:allValuesFrom"
    HAS_VALUE = "owl:hasValue"
    CARDINALITY = "owl:cardinality"
    MIN_CARDINALITY = "owl:minCardinality"
    MAX_CARDINALITY = "owl:maxCardinality"


@dataclass
class RDFTriple:
    """RDF triple (subject-predicate-object)"""
    subject: str  # URI or blank node
    predicate: str  # URI
    object: str  # URI, literal, or blank node
    
    def __str__(self) -> str:
        return f"<{self.subject}> <{self.predicate}> {self._format_object()} ."
    
    def _format_object(self) -> str:
        """Format object based on type"""
        if self.object.startswith("http://") or self.object.startswith("https://"):
            return f"<{self.object}>"
        elif '"' in self.object:
            return self.object  # Already formatted literal
        elif self.object.startswith("_:"):
            return self.object  # Blank node
        else:
            return f'"{self.object}"'


@dataclass
class RDFLiteral:
    """RDF literal with optional datatype and language"""
    value: str
    datatype: Optional[RDFDataType] = None
    language: Optional[str] = None
    
    def __str__(self) -> str:
        result = f'"{self.value}"'
        if self.language:
            result += f"@{self.language}"
        elif self.datatype:
            result += f"^^{self.datatype.value}"
        return result


@dataclass
class OWLClass:
    """OWL class definition"""
    uri: str
    label: Optional[str] = None
    comment: Optional[str] = None
    subclass_of: List[str] = field(default_factory=list)
    equivalent_class: List[str] = field(default_factory=list)
    disjoint_with: List[str] = field(default_factory=list)
    
    def to_triples(self) -> List[RDFTriple]:
        """Convert to RDF triples"""
        triples = [
            RDFTriple(self.uri, "rdf:type", "owl:Class")
        ]
        
        if self.label:
            triples.append(RDFTriple(self.uri, "rdfs:label", RDFLiteral(self.label, RDFDataType.STRING).__str__()))
        
        if self.comment:
            triples.append(RDFTriple(self.uri, "rdfs:comment", RDFLiteral(self.comment, RDFDataType.STRING).__str__()))
        
        for superclass in self.subclass_of:
            triples.append(RDFTriple(self.uri, "rdfs:subClassOf", superclass))
        
        for equiv_class in self.equivalent_class:
            triples.append(RDFTriple(self.uri, "owl:equivalentClass", equiv_class))
        
        for disjoint_class in self.disjoint_with:
            triples.append(RDFTriple(self.uri, "owl:disjointWith", disjoint_class))
        
        return triples


@dataclass
class OWLProperty:
    """OWL property (object or data property)"""
    uri: str
    property_type: str  # "owl:ObjectProperty" or "owl:DatatypeProperty"
    label: Optional[str] = None
    comment: Optional[str] = None
    domain: List[str] = field(default_factory=list)
    range: List[str] = field(default_factory=list)
    subproperty_of: List[str] = field(default_factory=list)
    inverse_of: Optional[str] = None
    is_functional: bool = False
    is_inverse_functional: bool = False
    is_transitive: bool = False
    is_symmetric: bool = False
    is_asymmetric: bool = False
    is_reflexive: bool = False
    is_irreflexive: bool = False
    
    def to_triples(self) -> List[RDFTriple]:
        """Convert to RDF triples"""
        triples = [
            RDFTriple(self.uri, "rdf:type", self.property_type)
        ]
        
        if self.label:
            triples.append(RDFTriple(self.uri, "rdfs:label", RDFLiteral(self.label, RDFDataType.STRING).__str__()))
        
        if self.comment:
            triples.append(RDFTriple(self.uri, "rdfs:comment", RDFLiteral(self.comment, RDFDataType.STRING).__str__()))
        
        for domain_class in self.domain:
            triples.append(RDFTriple(self.uri, "rdfs:domain", domain_class))
        
        for range_class in self.range:
            triples.append(RDFTriple(self.uri, "rdfs:range", range_class))
        
        for superprop in self.subproperty_of:
            triples.append(RDFTriple(self.uri, "rdfs:subPropertyOf", superprop))
        
        if self.inverse_of:
            triples.append(RDFTriple(self.uri, "owl:inverseOf", self.inverse_of))
        
        # Property characteristics
        if self.is_functional:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:FunctionalProperty"))
        if self.is_inverse_functional:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:InverseFunctionalProperty"))
        if self.is_transitive:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:TransitiveProperty"))
        if self.is_symmetric:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:SymmetricProperty"))
        if self.is_asymmetric:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:AsymmetricProperty"))
        if self.is_reflexive:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:ReflexiveProperty"))
        if self.is_irreflexive:
            triples.append(RDFTriple(self.uri, "rdf:type", "owl:IrreflexiveProperty"))
        
        return triples


@dataclass
class OWLIndividual:
    """OWL named individual (instance)"""
    uri: str
    class_types: List[str] = field(default_factory=list)
    properties: Dict[str, List[str]] = field(default_factory=dict)
    labels: List[RDFLiteral] = field(default_factory=list)
    
    def to_triples(self) -> List[RDFTriple]:
        """Convert to RDF triples"""
        triples = [
            RDFTriple(self.uri, "rdf:type", "owl:NamedIndividual")
        ]
        
        # Class memberships
        for class_type in self.class_types:
            triples.append(RDFTriple(self.uri, "rdf:type", class_type))
        
        # Property assertions
        for prop, values in self.properties.items():
            for value in values:
                triples.append(RDFTriple(self.uri, prop, value))
        
        # Labels
        for label in self.labels:
            triples.append(RDFTriple(self.uri, "rdfs:label", str(label)))
        
        return triples


@dataclass
class SWRLRule:
    """SWRL (Semantic Web Rule Language) rule"""
    rule_id: str
    antecedent: List[str]  # Body atoms
    consequent: List[str]  # Head atoms
    comment: Optional[str] = None
    
    def to_triples(self) -> List[RDFTriple]:
        """Convert to RDF triples"""
        rule_uri = f"rules:{self.rule_id}"
        
        triples = [
            RDFTriple(rule_uri, "rdf:type", "swrl:Imp"),
            RDFTriple(rule_uri, "swrl:body", f"_:body_{self.rule_id}"),
            RDFTriple(rule_uri, "swrl:head", f"_:head_{self.rule_id}")
        ]
        
        if self.comment:
            triples.append(RDFTriple(rule_uri, "rdfs:comment", RDFLiteral(self.comment, RDFDataType.STRING).__str__()))
        
        # Simplified rule representation (full SWRL would be more complex)
        body_list = " ∧ ".join(self.antecedent)
        head_list = " ∧ ".join(self.consequent)
        
        triples.extend([
            RDFTriple(f"_:body_{self.rule_id}", "rdf:type", "swrl:AtomList"),
            RDFTriple(f"_:body_{self.rule_id}", "rdfs:comment", f'"{body_list}"^^xsd:string'),
            RDFTriple(f"_:head_{self.rule_id}", "rdf:type", "swrl:AtomList"),
            RDFTriple(f"_:head_{self.rule_id}", "rdfs:comment", f'"{head_list}"^^xsd:string')
        ])
        
        return triples


class RDFOWLOntology:
    """Complete RDF/OWL ontology for political analysis"""
    
    def __init__(self, namespace: str, name: str):
        self.namespace = namespace
        self.name = name
        self.classes: Dict[str, OWLClass] = {}
        self.properties: Dict[str, OWLProperty] = {}
        self.individuals: Dict[str, OWLIndividual] = {}
        self.rules: Dict[str, SWRLRule] = {}
        self.prefixes = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "swrl": "http://www.w3.org/2003/11/swrl#",
            "rules": f"{namespace}/rules#",
            "pol": namespace
        }
    
    # Add compatibility properties for demo scripts
    @property
    def owl_classes(self) -> Dict[str, OWLClass]:
        """Compatibility property for demo scripts"""
        return self.classes
    
    @property
    def owl_properties(self) -> Dict[str, OWLProperty]:
        """Compatibility property for demo scripts"""
        return self.properties
    
    @property
    def swrl_rules(self) -> Dict[str, Any]:
        """Compatibility property for demo scripts"""
        return self.rules
    
    def add_class(self, owl_class: OWLClass) -> None:
        """Add OWL class to ontology"""
        self.classes[owl_class.uri] = owl_class
    
    def add_property(self, owl_property: OWLProperty) -> None:
        """Add OWL property to ontology"""
        self.properties[owl_property.uri] = owl_property
    
    def add_individual(self, individual: OWLIndividual) -> None:
        """Add OWL individual to ontology"""
        self.individuals[individual.uri] = individual
    
    def add_rule(self, rule: SWRLRule) -> None:
        """Add SWRL rule to ontology"""
        self.rules[rule.rule_id] = rule
    
    def get_all_triples(self) -> List[RDFTriple]:
        """Get all RDF triples in the ontology"""
        triples = []
        
        # Ontology metadata
        triples.extend([
            RDFTriple(self.namespace, "rdf:type", "owl:Ontology"),
            RDFTriple(self.namespace, "rdfs:label", RDFLiteral(self.name, RDFDataType.STRING).__str__())
        ])
        
        # Classes
        for owl_class in self.classes.values():
            triples.extend(owl_class.to_triples())
        
        # Properties
        for owl_property in self.properties.values():
            triples.extend(owl_property.to_triples())
        
        # Individuals
        for individual in self.individuals.values():
            triples.extend(individual.to_triples())
        
        # Rules
        for rule in self.rules.values():
            triples.extend(rule.to_triples())
        
        return triples
    
    def generate_turtle_syntax(self) -> str:
        """Generate Turtle (.ttl) serialization"""
        lines = []
        
        # Prefixes
        for prefix, uri in self.prefixes.items():
            lines.append(f"@prefix {prefix}: <{uri}> .")
        lines.append("")
        
        # Ontology declaration
        lines.append(f"<{self.namespace}> rdf:type owl:Ontology ;")
        lines.append(f'    rdfs:label "{self.name}"@en .')
        lines.append("")
        
        # Classes
        lines.append("# Classes")
        for owl_class in self.classes.values():
            class_triples = owl_class.to_triples()
            uri = owl_class.uri.replace(self.namespace + "#", "pol:")
            
            lines.append(f"{uri} rdf:type owl:Class")
            
            if owl_class.label:
                lines.append(f'    ; rdfs:label "{owl_class.label}"@en')
            if owl_class.comment:
                lines.append(f'    ; rdfs:comment "{owl_class.comment}"@en')
            for superclass in owl_class.subclass_of:
                superclass_short = superclass.replace(self.namespace + "#", "pol:")
                lines.append(f"    ; rdfs:subClassOf {superclass_short}")
            
            lines.append("    .")
            lines.append("")
        
        # Properties
        lines.append("# Properties")
        for owl_property in self.properties.values():
            prop_uri = owl_property.uri.replace(self.namespace + "#", "pol:")
            prop_type = "owl:ObjectProperty" if owl_property.property_type == "owl:ObjectProperty" else "owl:DatatypeProperty"
            
            lines.append(f"{prop_uri} rdf:type {prop_type}")
            
            if owl_property.label:
                lines.append(f'    ; rdfs:label "{owl_property.label}"@en')
            if owl_property.comment:
                lines.append(f'    ; rdfs:comment "{owl_property.comment}"@en')
            
            for domain in owl_property.domain:
                domain_short = domain.replace(self.namespace + "#", "pol:")
                lines.append(f"    ; rdfs:domain {domain_short}")
            
            for range_val in owl_property.range:
                range_short = range_val.replace(self.namespace + "#", "pol:")
                lines.append(f"    ; rdfs:range {range_short}")
            
            # Property characteristics
            if owl_property.is_functional:
                lines.append("    ; rdf:type owl:FunctionalProperty")
            if owl_property.is_transitive:
                lines.append("    ; rdf:type owl:TransitiveProperty")
            if owl_property.is_symmetric:
                lines.append("    ; rdf:type owl:SymmetricProperty")
            
            lines.append("    .")
            lines.append("")
        
        # Individuals
        if self.individuals:
            lines.append("# Individuals")
            for individual in self.individuals.values():
                ind_uri = individual.uri.replace(self.namespace + "#", "pol:")
                
                lines.append(f"{ind_uri} rdf:type owl:NamedIndividual")
                
                for class_type in individual.class_types:
                    class_short = class_type.replace(self.namespace + "#", "pol:")
                    lines.append(f"    ; rdf:type {class_short}")
                
                for prop, values in individual.properties.items():
                    prop_short = prop.replace(self.namespace + "#", "pol:")
                    for value in values:
                        value_short = value.replace(self.namespace + "#", "pol:") if value.startswith(self.namespace) else value
                        lines.append(f"    ; {prop_short} {value_short}")
                
                for label in individual.labels:
                    lines.append(f"    ; rdfs:label {label}")
                
                lines.append("    .")
                lines.append("")
        
        return "\n".join(lines)
    
    def to_turtle(self) -> str:
        """Compatibility method for demo scripts"""
        return self.generate_turtle_syntax()
    
    def generate_sparql_queries(self) -> List[str]:
        """Generate example SPARQL queries"""
        
        return [
            # Query all political actors
            """
PREFIX pol: <%s#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?actor ?label ?type WHERE {
    ?actor rdf:type ?type .
    ?type rdfs:subClassOf pol:PoliticalActor .
    ?actor rdfs:label ?label .
}
""" % self.namespace,
            
            # Query negotiations with participants
            """
PREFIX pol: <%s#>

SELECT ?negotiation ?initiator ?responder ?concept WHERE {
    ?negotiation rdf:type pol:Negotiation ;
                pol:hasInitiator ?initiator ;
                pol:hasResponder ?responder ;
                pol:concerns ?concept .
}
""" % self.namespace,
            
            # Query causal relationships
            """
PREFIX pol: <%s#>

SELECT ?cause ?effect ?confidence WHERE {
    ?cause pol:enables ?effect ;
          pol:hasConfidenceLevel ?confidence .
    FILTER(?confidence > 0.7)
}
""" % self.namespace,
            
            # Complex query with reasoning
            """
PREFIX pol: <%s#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?leader ?country ?policy ?concept WHERE {
    ?leader rdf:type pol:PoliticalLeader ;
           pol:leads ?country .
    ?country pol:implements ?policy .
    ?policy pol:aims_for ?concept .
    ?concept rdf:type pol:PoliticalConcept .
}
""" % self.namespace
        ]
    
    def validate_ontology(self) -> List[str]:
        """Validate the OWL ontology for consistency"""
        errors = []
        
        # Check domain/range consistency
        for prop in self.properties.values():
            for domain_class in prop.domain:
                if domain_class not in self.classes and not domain_class.startswith("xsd:"):
                    errors.append(f"Property {prop.uri} references undefined domain class: {domain_class}")
            
            for range_class in prop.range:
                if range_class not in self.classes and not range_class.startswith("xsd:"):
                    errors.append(f"Property {prop.uri} references undefined range class: {range_class}")
        
        # Check class hierarchy consistency
        for owl_class in self.classes.values():
            for superclass in owl_class.subclass_of:
                if superclass not in self.classes:
                    errors.append(f"Class {owl_class.uri} references undefined superclass: {superclass}")
        
        # Check individual type consistency
        for individual in self.individuals.values():
            for class_type in individual.class_types:
                if class_type not in self.classes:
                    errors.append(f"Individual {individual.uri} references undefined class: {class_type}")
        
        return errors
    
    def get_statistics(self) -> Dict[str, int]:
        """Get ontology statistics"""
        return {
            "classes": len(self.classes),
            "object_properties": len([p for p in self.properties.values() if p.property_type == "owl:ObjectProperty"]),
            "datatype_properties": len([p for p in self.properties.values() if p.property_type == "owl:DatatypeProperty"]),
            "individuals": len(self.individuals),
            "rules": len(self.rules),
            "total_triples": len(self.get_all_triples())
        }


def create_political_rdf_owl_ontology() -> RDFOWLOntology:
    """Create comprehensive RDF/OWL ontology for political analysis"""
    
    namespace = "http://example.org/political-ontology"
    ontology = RDFOWLOntology(namespace, "Political Analysis Ontology")
    
    # ========== CLASSES ==========
    
    # Top-level classes
    ontology.add_class(OWLClass(
        uri=f"{namespace}#PoliticalActor",
        label="Political Actor",
        comment="Any entity that participates in political processes"
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#PoliticalEvent",
        label="Political Event",
        comment="Temporal political occurrences"
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#PoliticalConcept",
        label="Political Concept",
        comment="Abstract political ideas and theories"
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Document",
        label="Document",
        comment="Textual political documents"
    ))
    
    # Political Actor subclasses
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Country",
        label="Country",
        comment="Sovereign nation-state",
        subclass_of=[f"{namespace}#PoliticalActor"]
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#PoliticalLeader",
        label="Political Leader",
        comment="Individual political leader",
        subclass_of=[f"{namespace}#PoliticalActor"]
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#InternationalOrganization",
        label="International Organization",
        comment="Multinational political organization",
        subclass_of=[f"{namespace}#PoliticalActor"]
    ))
    
    # Political Event subclasses
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Negotiation",
        label="Negotiation",
        comment="Diplomatic negotiation process",
        subclass_of=[f"{namespace}#PoliticalEvent"]
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Treaty",
        label="Treaty",
        comment="International agreement",
        subclass_of=[f"{namespace}#PoliticalEvent"]
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Policy",
        label="Policy",
        comment="Government policy decision",
        subclass_of=[f"{namespace}#PoliticalEvent"]
    ))
    
    # Political Concept subclasses
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Detente",
        label="Détente",
        comment="Policy of easing tensions",
        subclass_of=[f"{namespace}#PoliticalConcept"]
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#NuclearDeterrence",
        label="Nuclear Deterrence",
        comment="Prevention through nuclear threat",
        subclass_of=[f"{namespace}#PoliticalConcept"]
    ))
    
    ontology.add_class(OWLClass(
        uri=f"{namespace}#WorldPeace",
        label="World Peace",
        comment="Global peaceful coexistence",
        subclass_of=[f"{namespace}#PoliticalConcept"]
    ))
    
    # Document subclasses
    ontology.add_class(OWLClass(
        uri=f"{namespace}#Speech",
        label="Speech",
        comment="Political speech or address",
        subclass_of=[f"{namespace}#Document"]
    ))
    
    # ========== OBJECT PROPERTIES ==========
    
    # Actor relationships
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#leads",
        property_type="owl:ObjectProperty",
        label="leads",
        comment="Political leader leads country",
        domain=[f"{namespace}#PoliticalLeader"],
        range=[f"{namespace}#Country"],
        is_functional=True
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#participatesIn",
        property_type="owl:ObjectProperty",
        label="participates in",
        comment="Actor participates in political event",
        domain=[f"{namespace}#PoliticalActor"],
        range=[f"{namespace}#PoliticalEvent"]
    ))
    
    # Event relationships
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasInitiator",
        property_type="owl:ObjectProperty",
        label="has initiator",
        comment="Event has initiating actor",
        domain=[f"{namespace}#PoliticalEvent"],
        range=[f"{namespace}#PoliticalActor"],
        is_functional=True
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasResponder",
        property_type="owl:ObjectProperty",
        label="has responder",
        comment="Event has responding actor",
        domain=[f"{namespace}#PoliticalEvent"],
        range=[f"{namespace}#PoliticalActor"]
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#concerns",
        property_type="owl:ObjectProperty",
        label="concerns",
        comment="Event concerns political concept",
        domain=[f"{namespace}#PoliticalEvent"],
        range=[f"{namespace}#PoliticalConcept"]
    ))
    
    # Causal relationships
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#enables",
        property_type="owl:ObjectProperty",
        label="enables",
        comment="One concept enables another",
        domain=[f"{namespace}#PoliticalConcept"],
        range=[f"{namespace}#PoliticalConcept"],
        is_transitive=True
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#implements",
        property_type="owl:ObjectProperty",
        label="implements",
        comment="Actor implements policy",
        domain=[f"{namespace}#PoliticalActor"],
        range=[f"{namespace}#Policy"]
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#aims_for",
        property_type="owl:ObjectProperty",
        label="aims for",
        comment="Policy aims for concept",
        domain=[f"{namespace}#Policy"],
        range=[f"{namespace}#PoliticalConcept"]
    ))
    
    # Opposition relationships
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#opposes",
        property_type="owl:ObjectProperty",
        label="opposes",
        comment="Actor opposes another actor",
        domain=[f"{namespace}#PoliticalActor"],
        range=[f"{namespace}#PoliticalActor"],
        is_symmetric=True
    ))
    
    # Document relationships
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#deliveredBy",
        property_type="owl:ObjectProperty",
        label="delivered by",
        comment="Speech delivered by leader",
        domain=[f"{namespace}#Speech"],
        range=[f"{namespace}#PoliticalLeader"],
        is_functional=True
    ))
    
    # ========== DATATYPE PROPERTIES ==========
    
    # Names and identifiers
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasName",
        property_type="owl:DatatypeProperty",
        label="has name",
        comment="Entity has name",
        range=["xsd:string"],
        is_functional=True
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasCountryCode",
        property_type="owl:DatatypeProperty",
        label="has country code",
        comment="Country has ISO code",
        domain=[f"{namespace}#Country"],
        range=["xsd:string"],
        is_functional=True
    ))
    
    # Temporal properties
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasDate",
        property_type="owl:DatatypeProperty",
        label="has date",
        comment="Event has date",
        domain=[f"{namespace}#PoliticalEvent"],
        range=["xsd:date"]
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasBirthDate",
        property_type="owl:DatatypeProperty",
        label="has birth date",
        comment="Leader has birth date",
        domain=[f"{namespace}#PoliticalLeader"],
        range=["xsd:date"],
        is_functional=True
    ))
    
    # Confidence and measurements
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasConfidenceLevel",
        property_type="owl:DatatypeProperty",
        label="has confidence level",
        comment="Assertion has confidence level",
        range=["xsd:decimal"]
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasMilitarySpending",
        property_type="owl:DatatypeProperty",
        label="has military spending",
        comment="Country has military spending",
        domain=[f"{namespace}#Country"],
        range=["xsd:decimal"]
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasNuclearWarheads",
        property_type="owl:DatatypeProperty",
        label="has nuclear warheads",
        comment="Country has nuclear warheads",
        domain=[f"{namespace}#Country"],
        range=["xsd:integer"]
    ))
    
    # Document properties
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasContent",
        property_type="owl:DatatypeProperty",
        label="has content",
        comment="Document has textual content",
        domain=[f"{namespace}#Document"],
        range=["xsd:string"]
    ))
    
    ontology.add_property(OWLProperty(
        uri=f"{namespace}#hasVenue",
        property_type="owl:DatatypeProperty",
        label="has venue",
        comment="Speech has venue",
        domain=[f"{namespace}#Speech"],
        range=["xsd:string"]
    ))
    
    # ========== RULES ==========
    
    # Transitive alliance rule
    ontology.add_rule(SWRLRule(
        rule_id="transitive_alliance",
        antecedent=[
            "Country(?x)",
            "Country(?y)", 
            "Country(?z)",
            "alliedWith(?x, ?y)",
            "alliedWith(?y, ?z)"
        ],
        consequent=[
            "alliedWith(?x, ?z)"
        ],
        comment="If country X is allied with Y, and Y is allied with Z, then X is allied with Z"
    ))
    
    # Détente enables cooperation rule
    ontology.add_rule(SWRLRule(
        rule_id="detente_enables_cooperation",
        antecedent=[
            "Negotiation(?n)",
            "Country(?c1)",
            "Country(?c2)",
            "Detente(?d)",
            "hasInitiator(?n, ?c1)",
            "hasResponder(?n, ?c2)",
            "concerns(?n, ?d)"
        ],
        consequent=[
            "cooperatesWith(?c1, ?c2)"
        ],
        comment="Détente negotiations enable bilateral cooperation"
    ))
    
    # Nuclear deterrence policy rule
    ontology.add_rule(SWRLRule(
        rule_id="nuclear_deterrence_policy",
        antecedent=[
            "Country(?c)",
            "Policy(?p)",
            "NuclearDeterrence(?nd)",
            "implements(?c, ?p)",
            "aims_for(?p, ?nd)",
            "hasNuclearWarheads(?c, ?w)",
            "greaterThan(?w, 0)"
        ],
        consequent=[
            "hasNuclearCapability(?c, true)"
        ],
        comment="Countries implementing nuclear deterrence policies have nuclear capability"
    ))
    
    return ontology


def create_carter_rdf_owl_instance(ontology: RDFOWLOntology) -> None:
    """Create RDF/OWL individuals for Carter speech analysis"""
    
    namespace = ontology.namespace
    
    # Countries
    usa = OWLIndividual(
        uri=f"{namespace}#USA",
        class_types=[f"{namespace}#Country"],
        properties={
            f"{namespace}#hasName": ['"United States"^^xsd:string'],
            f"{namespace}#hasCountryCode": ['"USA"^^xsd:string'],
            f"{namespace}#hasMilitarySpending": ['"200000000"^^xsd:decimal'],
            f"{namespace}#hasNuclearWarheads": ['"10000"^^xsd:integer']
        },
        labels=[RDFLiteral("United States", language="en")]
    )
    ontology.add_individual(usa)
    
    ussr = OWLIndividual(
        uri=f"{namespace}#USSR",
        class_types=[f"{namespace}#Country"],
        properties={
            f"{namespace}#hasName": ['"Soviet Union"^^xsd:string'],
            f"{namespace}#hasCountryCode": ['"USSR"^^xsd:string'],
            f"{namespace}#hasMilitarySpending": ['"180000000"^^xsd:decimal'],
            f"{namespace}#hasNuclearWarheads": ['"12000"^^xsd:integer']
        },
        labels=[RDFLiteral("Soviet Union", language="en")]
    )
    ontology.add_individual(ussr)
    
    # Political Leaders
    carter = OWLIndividual(
        uri=f"{namespace}#JimmyCarter",
        class_types=[f"{namespace}#PoliticalLeader"],
        properties={
            f"{namespace}#hasName": ['"Jimmy Carter"^^xsd:string'],
            f"{namespace}#hasBirthDate": ['"1924-10-01"^^xsd:date'],
            f"{namespace}#leads": [f"{namespace}#USA"]
        },
        labels=[RDFLiteral("Jimmy Carter", language="en")]
    )
    ontology.add_individual(carter)
    
    brezhnev = OWLIndividual(
        uri=f"{namespace}#LeonidBrezhnev",
        class_types=[f"{namespace}#PoliticalLeader"],
        properties={
            f"{namespace}#hasName": ['"Leonid Brezhnev"^^xsd:string'],
            f"{namespace}#hasBirthDate": ['"1906-12-19"^^xsd:date'],
            f"{namespace}#leads": [f"{namespace}#USSR"]
        },
        labels=[RDFLiteral("Leonid Brezhnev", language="en")]
    )
    ontology.add_individual(brezhnev)
    
    # Political Concepts
    detente = OWLIndividual(
        uri=f"{namespace}#DetenteInstance",
        class_types=[f"{namespace}#Detente"],
        properties={
            f"{namespace}#hasName": ['"Détente"^^xsd:string']
        },
        labels=[RDFLiteral("Détente", language="en")]
    )
    ontology.add_individual(detente)
    
    world_peace = OWLIndividual(
        uri=f"{namespace}#WorldPeaceInstance",
        class_types=[f"{namespace}#WorldPeace"],
        properties={
            f"{namespace}#hasName": ['"World Peace"^^xsd:string']
        },
        labels=[RDFLiteral("World Peace", language="en")]
    )
    ontology.add_individual(world_peace)
    
    # Negotiation
    detente_negotiation = OWLIndividual(
        uri=f"{namespace}#DetenteNegotiation1977",
        class_types=[f"{namespace}#Negotiation"],
        properties={
            f"{namespace}#hasInitiator": [f"{namespace}#JimmyCarter"],
            f"{namespace}#hasResponder": [f"{namespace}#LeonidBrezhnev"],
            f"{namespace}#concerns": [f"{namespace}#DetenteInstance"],
            f"{namespace}#hasDate": ['"1977-06-01"^^xsd:date'],
            f"{namespace}#hasConfidenceLevel": ['"0.85"^^xsd:decimal']
        },
        labels=[RDFLiteral("Détente Negotiation 1977", language="en")]
    )
    ontology.add_individual(detente_negotiation)
    
    # Speech
    carter_speech = OWLIndividual(
        uri=f"{namespace}#CarterForeignPolicySpeech",
        class_types=[f"{namespace}#Speech"],
        properties={
            f"{namespace}#deliveredBy": [f"{namespace}#JimmyCarter"],
            f"{namespace}#hasVenue": ['"White House"^^xsd:string'],
            f"{namespace}#hasDate": ['"1977-06-01"^^xsd:date'],
            f"{namespace}#hasContent": ['"Text of Carter foreign policy speech..."^^xsd:string'],
            f"{namespace}#hasConfidenceLevel": ['"0.92"^^xsd:decimal']
        },
        labels=[RDFLiteral("Carter Foreign Policy Speech", language="en")]
    )
    ontology.add_individual(carter_speech)


def demonstrate_rdf_owl_modeling():
    """Demonstrate RDF/OWL ontology modeling capabilities"""
    
    print("RDF/OWL POLITICAL ANALYSIS ONTOLOGY")
    print("=" * 50)
    
    ontology = create_political_rdf_owl_ontology()
    create_carter_rdf_owl_instance(ontology)
    
    print("Ontology Statistics:")
    stats = ontology.get_statistics()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nKey RDF/OWL Features Demonstrated:")
    print(f"  ✓ Triple-based knowledge representation")
    print(f"  ✓ Formal OWL ontology with classes and properties")
    print(f"  ✓ Property characteristics (functional, transitive, symmetric)")
    print(f"  ✓ Class hierarchies with inheritance")
    print(f"  ✓ SWRL rules for automated reasoning")
    print(f"  ✓ Named individuals (instances)")
    print(f"  ✓ Semantic web standards compliance")
    
    # Validate ontology
    errors = ontology.validate_ontology()
    print(f"\nOntology Validation: {'✅ VALID' if not errors else '❌ ERRORS'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    return ontology


if __name__ == "__main__":
    demonstrate_rdf_owl_modeling()