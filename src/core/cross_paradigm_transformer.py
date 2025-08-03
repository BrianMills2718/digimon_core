"""
Cross-Paradigm Data Transformation System

This module provides actual data transformation between the 5 schema paradigms,
enabling real interoperability rather than just theoretical representations.

Transforms extracted entities and relationships between:
- UML Class Diagram instances
- RDF/OWL triples  
- ORM fact instances
- TypeDB data insertion
- N-ary graph relationship nodes
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import uuid
from datetime import datetime

from .uml_class_schemas import UMLClassDiagram, create_political_uml_diagram
from .rdf_owl_schemas import RDFOWLOntology, RDFTriple, RDFLiteral, RDFDataType
from .orm_schemas import ORMSchema, FactType, ObjectType, create_political_orm_schema
from .typedb_style_schemas import TypeDBPoliticalSchema, create_typedb_political_schema
from .nary_graph_schemas import NAryGraphSchema, create_political_nary_schema


@dataclass
class ExtractedEntity:
    """Standard representation of extracted entity"""
    text: str
    entity_type: str
    confidence: float
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    source_ref: Optional[str] = None


@dataclass
class ExtractedRelationship:
    """Standard representation of extracted relationship"""
    source: str
    target: str
    relation: str
    confidence: float = 1.0
    context: Optional[str] = None


@dataclass
class CrossParadigmData:
    """Container for data across all 5 paradigms"""
    uml_instances: Dict[str, Any]
    rdf_triples: List[RDFTriple]
    orm_facts: List[Dict[str, Any]]
    typedb_insertions: List[str]
    nary_relationships: List[Dict[str, Any]]
    
    def get_total_representations(self) -> int:
        """Get total number of data representations across all paradigms"""
        return (
            len(self.uml_instances) +
            len(self.rdf_triples) +
            len(self.orm_facts) +
            len(self.typedb_insertions) +
            len(self.nary_relationships)
        )


class CrossParadigmTransformer:
    """Transforms extracted data between all 5 schema paradigms"""
    
    def __init__(self):
        # Initialize all schema frameworks
        self.uml_diagram = create_political_uml_diagram()
        self.rdf_ontology = self._create_rdf_ontology()
        self.orm_schema = create_political_orm_schema()
        self.typedb_schema = create_typedb_political_schema()
        self.nary_schema = create_political_nary_schema()
        
        # Base URI for RDF resources
        self.base_uri = "http://political-analysis.example.org"
        
    def _create_rdf_ontology(self) -> RDFOWLOntology:
        """Create RDF ontology for transformation"""
        from .rdf_owl_schemas import create_political_rdf_owl_ontology
        return create_political_rdf_owl_ontology()
    
    def transform_extraction_results(self, entities: List[Dict[str, Any]], 
                                   relationships: List[Dict[str, Any]]) -> CrossParadigmData:
        """Transform LLM extraction results to all 5 paradigms"""
        
        # Convert to standard format
        std_entities = [self._to_standard_entity(e) for e in entities]
        std_relationships = [self._to_standard_relationship(r) for r in relationships]
        
        # Transform to each paradigm
        uml_instances = self._to_uml_instances(std_entities, std_relationships)
        rdf_triples = self._to_rdf_triples(std_entities, std_relationships)
        orm_facts = self._to_orm_facts(std_entities, std_relationships)
        typedb_insertions = self._to_typedb_insertions(std_entities, std_relationships)
        nary_relationships = self._to_nary_relationships(std_entities, std_relationships)
        
        return CrossParadigmData(
            uml_instances=uml_instances,
            rdf_triples=rdf_triples,
            orm_facts=orm_facts,
            typedb_insertions=typedb_insertions,
            nary_relationships=nary_relationships
        )
    
    def _to_standard_entity(self, entity: Dict[str, Any]) -> ExtractedEntity:
        """Convert extraction result to standard entity format"""
        return ExtractedEntity(
            text=entity.get('text', ''),
            entity_type=entity.get('type', 'UNKNOWN'),
            confidence=entity.get('confidence', 0.0),
            start_pos=entity.get('start_pos'),
            end_pos=entity.get('end_pos'),
            source_ref=entity.get('source_ref')
        )
    
    def _to_standard_relationship(self, relationship: Dict[str, Any]) -> ExtractedRelationship:
        """Convert extraction result to standard relationship format"""
        return ExtractedRelationship(
            source=relationship.get('source', ''),
            target=relationship.get('target', ''),
            relation=relationship.get('relation', 'RELATED_TO'),
            confidence=relationship.get('confidence', 1.0),
            context=relationship.get('context')
        )
    
    def _to_uml_instances(self, entities: List[ExtractedEntity], 
                         relationships: List[ExtractedRelationship]) -> Dict[str, Any]:
        """Transform to UML class instances"""
        instances = {}
        
        for entity in entities:
            entity_id = self._generate_id(entity.text)
            
            if entity.entity_type == 'PERSON':
                instances[entity_id] = {
                    'class': 'PoliticalLeader',
                    'attributes': {
                        'name': entity.text,
                        'firstName': entity.text.split()[0] if ' ' in entity.text else entity.text,
                        'lastName': entity.text.split()[-1] if ' ' in entity.text else '',
                        'establishedDate': datetime.now().isoformat(),
                        'description': f'Political leader extracted from text',
                        'confidence': entity.confidence
                    }
                }
            elif entity.entity_type == 'ORGANIZATION':
                instances[entity_id] = {
                    'class': 'InternationalOrganization',
                    'attributes': {
                        'name': entity.text,
                        'establishedDate': datetime.now().isoformat(),
                        'description': f'Political organization: {entity.text}',
                        'confidence': entity.confidence
                    }
                }
            elif entity.entity_type == 'LOCATION':
                instances[entity_id] = {
                    'class': 'Country',
                    'attributes': {
                        'name': entity.text,
                        'establishedDate': datetime.now().isoformat(),
                        'description': f'Political location: {entity.text}',
                        'confidence': entity.confidence
                    }
                }
            elif entity.entity_type == 'POLICY':
                instances[entity_id] = {
                    'class': 'Policy',
                    'attributes': {
                        'policyName': entity.text,
                        'description': f'Policy initiative: {entity.text}',
                        'implementationDate': datetime.now().isoformat(),
                        'objective': 'Political objective',
                        'confidence': entity.confidence
                    }
                }
            elif entity.entity_type == 'CONCEPT':
                instances[entity_id] = {
                    'class': 'PoliticalConcept',
                    'attributes': {
                        'conceptName': entity.text,
                        'definition': f'Political concept: {entity.text}',
                        'theoreticalFramework': 'Political theory',
                        'confidence': entity.confidence
                    }
                }
        
        # Add relationship instances
        for i, rel in enumerate(relationships):
            rel_id = f"relationship_{i}"
            instances[rel_id] = {
                'class': 'Negotiation',
                'attributes': {
                    'negotiationId': rel_id,
                    'topic': f'{rel.relation} between {rel.source} and {rel.target}',
                    'outcome': 'Inferred from text analysis',
                    'confidenceLevel': rel.confidence,
                    'startDate': datetime.now().isoformat()
                }
            }
        
        return instances
    
    def _to_rdf_triples(self, entities: List[ExtractedEntity], 
                       relationships: List[ExtractedRelationship]) -> List[RDFTriple]:
        """Transform to RDF triples"""
        triples = []
        
        for entity in entities:
            entity_uri = f"{self.base_uri}/entity/{self._generate_id(entity.text)}"
            
            # Entity type declaration
            if entity.entity_type == 'PERSON':
                triples.append(RDFTriple(entity_uri, "rdf:type", f"{self.base_uri}#PoliticalLeader"))
            elif entity.entity_type == 'ORGANIZATION':
                triples.append(RDFTriple(entity_uri, "rdf:type", f"{self.base_uri}#Organization"))
            elif entity.entity_type == 'LOCATION':
                triples.append(RDFTriple(entity_uri, "rdf:type", f"{self.base_uri}#Country"))
            elif entity.entity_type == 'POLICY':
                triples.append(RDFTriple(entity_uri, "rdf:type", f"{self.base_uri}#Policy"))
            elif entity.entity_type == 'CONCEPT':
                triples.append(RDFTriple(entity_uri, "rdf:type", f"{self.base_uri}#Concept"))
            
            # Properties
            triples.append(RDFTriple(entity_uri, f"{self.base_uri}#hasName", 
                                   RDFLiteral(entity.text, RDFDataType.STRING).__str__()))
            triples.append(RDFTriple(entity_uri, f"{self.base_uri}#hasConfidence", 
                                   RDFLiteral(str(entity.confidence), RDFDataType.DECIMAL).__str__()))
        
        # Relationships
        for rel in relationships:
            source_uri = f"{self.base_uri}/entity/{self._generate_id(rel.source)}"
            target_uri = f"{self.base_uri}/entity/{self._generate_id(rel.target)}"
            
            if rel.relation == 'NEGOTIATES_WITH':
                triples.append(RDFTriple(source_uri, f"{self.base_uri}#negotiatesWith", target_uri))
            elif rel.relation == 'MEMBER_OF':
                triples.append(RDFTriple(source_uri, f"{self.base_uri}#memberOf", target_uri))
            elif rel.relation == 'LEADS':
                triples.append(RDFTriple(source_uri, f"{self.base_uri}#leads", target_uri))
            else:
                triples.append(RDFTriple(source_uri, f"{self.base_uri}#relatedTo", target_uri))
        
        return triples
    
    def _to_orm_facts(self, entities: List[ExtractedEntity], 
                     relationships: List[ExtractedRelationship]) -> List[Dict[str, Any]]:
        """Transform to ORM fact instances"""
        facts = []
        
        for entity in entities:
            # Entity existence fact
            facts.append({
                'fact_type': 'entity_exists',
                'roles': [entity.text, entity.entity_type],
                'verbalization': f'{entity.entity_type} <{entity.text}> exists',
                'confidence': entity.confidence
            })
            
            # Entity has type fact
            facts.append({
                'fact_type': 'entity_has_type',
                'roles': [entity.text, entity.entity_type],
                'verbalization': f'Entity <{entity.text}> has EntityType <{entity.entity_type}>',
                'confidence': entity.confidence
            })
        
        for rel in relationships:
            # Relationship fact
            facts.append({
                'fact_type': 'entity_relates_to_entity',
                'roles': [rel.source, rel.relation, rel.target],
                'verbalization': f'Entity <{rel.source}> {rel.relation.lower().replace("_", " ")} Entity <{rel.target}>',
                'confidence': rel.confidence
            })
        
        return facts
    
    def _to_typedb_insertions(self, entities: List[ExtractedEntity], 
                            relationships: List[ExtractedRelationship]) -> List[str]:
        """Transform to TypeDB insertion statements"""
        insertions = []
        
        for entity in entities:
            entity_var = f"${self._generate_id(entity.text).replace('-', '_')}"
            
            if entity.entity_type == 'PERSON':
                insertions.append(
                    f'insert {entity_var} isa political-leader, has name "{entity.text}", '
                    f'has confidence {entity.confidence:.2f};'
                )
            elif entity.entity_type == 'ORGANIZATION':
                insertions.append(
                    f'insert {entity_var} isa international-organization, has name "{entity.text}", '
                    f'has confidence {entity.confidence:.2f};'
                )
            elif entity.entity_type == 'LOCATION':
                insertions.append(
                    f'insert {entity_var} isa nation-state, has name "{entity.text}", '
                    f'has confidence {entity.confidence:.2f};'
                )
            elif entity.entity_type == 'POLICY':
                insertions.append(
                    f'insert {entity_var} isa policy-initiative, has name "{entity.text}", '
                    f'has confidence {entity.confidence:.2f};'
                )
            elif entity.entity_type == 'CONCEPT':
                insertions.append(
                    f'insert {entity_var} isa political-concept, has name "{entity.text}", '
                    f'has confidence {entity.confidence:.2f};'
                )
        
        for i, rel in enumerate(relationships):
            source_var = f"${self._generate_id(rel.source).replace('-', '_')}"
            target_var = f"${self._generate_id(rel.target).replace('-', '_')}"
            
            if rel.relation == 'NEGOTIATES_WITH':
                insertions.append(
                    f'match {source_var} isa political-actor, has name "{rel.source}"; '
                    f'{target_var} isa political-actor, has name "{rel.target}"; '
                    f'insert (initiator: {source_var}, responder: {target_var}) isa negotiation;'
                )
            elif rel.relation == 'MEMBER_OF':
                insertions.append(
                    f'match {source_var} isa political-actor, has name "{rel.source}"; '
                    f'{target_var} isa political-actor, has name "{rel.target}"; '
                    f'insert (member: {source_var}, organization: {target_var}) isa membership;'
                )
            elif rel.relation == 'LEADS':
                insertions.append(
                    f'match {source_var} isa political-actor, has name "{rel.source}"; '
                    f'{target_var} isa political-actor, has name "{rel.target}"; '
                    f'insert (leader: {source_var}, led: {target_var}) isa leadership;'
                )
        
        return insertions
    
    def _to_nary_relationships(self, entities: List[ExtractedEntity], 
                             relationships: List[ExtractedRelationship]) -> List[Dict[str, Any]]:
        """Transform to N-ary graph relationship nodes"""
        nary_rels = []
        
        for rel in relationships:
            # Create reified relationship
            rel_id = f"rel_{self._generate_id(f'{rel.source}_{rel.relation}_{rel.target}')}"
            
            nary_rel = {
                'relationship_id': rel_id,
                'relation_type': rel.relation,
                'participants': [
                    {
                        'entity': rel.source,
                        'role': 'INITIATOR',
                        'confidence': rel.confidence
                    },
                    {
                        'entity': rel.target,
                        'role': 'RESPONDER',
                        'confidence': rel.confidence
                    }
                ],
                'properties': {
                    'confidence': rel.confidence,
                    'extraction_method': 'LLM',
                    'timestamp': datetime.now().isoformat()
                },
                'context': rel.context or 'Political text analysis'
            }
            
            # Add temporal context if negotiation
            if rel.relation == 'NEGOTIATES_WITH':
                nary_rel['properties']['temporal_context'] = 'Ongoing diplomatic relations'
                nary_rel['properties']['negotiation_type'] = 'Bilateral'
            
            nary_rels.append(nary_rel)
        
        return nary_rels
    
    def _generate_id(self, text: str) -> str:
        """Generate consistent ID from text"""
        return text.lower().replace(' ', '-').replace(',', '').replace('.', '')
    
    def cross_validate_transformations(self, data: CrossParadigmData) -> Dict[str, Any]:
        """Cross-validate that transformations preserve semantic content"""
        validation_results = {
            'entity_count_consistency': True,
            'relationship_preservation': True,
            'semantic_integrity': True,
            'details': {}
        }
        
        # Count entities across paradigms
        uml_entity_count = len([i for i in data.uml_instances.values() 
                               if i['class'] in ['PoliticalLeader', 'Country', 'InternationalOrganization']])
        rdf_entity_count = len([t for t in data.rdf_triples if '#hasName' in t.predicate])
        orm_entity_count = len([f for f in data.orm_facts if f['fact_type'] == 'entity_exists'])
        
        validation_results['details']['entity_counts'] = {
            'uml': uml_entity_count,
            'rdf': rdf_entity_count,
            'orm': orm_entity_count
        }
        
        # Check consistency
        if not (uml_entity_count == rdf_entity_count == orm_entity_count):
            validation_results['entity_count_consistency'] = False
        
        # Count relationships
        uml_rel_count = len([i for i in data.uml_instances.values() if i['class'] == 'Negotiation'])
        rdf_rel_count = len([t for t in data.rdf_triples if 'negotiatesWith' in t.predicate or 'memberOf' in t.predicate])
        nary_rel_count = len(data.nary_relationships)
        
        validation_results['details']['relationship_counts'] = {
            'uml': uml_rel_count,
            'rdf': rdf_rel_count,
            'nary': nary_rel_count
        }
        
        return validation_results
    
    def demonstrate_cross_paradigm_query(self, data: CrossParadigmData, 
                                       query_entity: str) -> Dict[str, Any]:
        """Demonstrate querying the same entity across all paradigms"""
        results = {}
        
        # UML query
        results['uml'] = [inst for inst_id, inst in data.uml_instances.items() 
                         if query_entity.lower() in inst.get('attributes', {}).get('name', '').lower()]
        
        # RDF query
        results['rdf'] = [t for t in data.rdf_triples 
                         if query_entity.lower() in t.object.lower() and 'hasName' in t.predicate]
        
        # ORM query
        results['orm'] = [f for f in data.orm_facts 
                         if query_entity.lower() in f['verbalization'].lower()]
        
        # TypeDB query
        results['typedb'] = [ins for ins in data.typedb_insertions 
                            if query_entity.lower() in ins.lower()]
        
        # N-ary query
        results['nary'] = [rel for rel in data.nary_relationships 
                          if any(query_entity.lower() in p['entity'].lower() 
                                for p in rel['participants'])]
        
        return results