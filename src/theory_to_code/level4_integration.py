#!/usr/bin/env python3
"""
Level 4 (RULES) Integration for Theory-to-Code System

Integrates OWL2/SWRL rule generation and execution with the existing system.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from owlready2 import *

from .rule_generator import RuleGenerator, GeneratedRule
from .swrl_parser import SWRLParser, ParsedRule, AtomType
from .rule_executor import RuleExecutor, InferenceResult, ReasonerType

logger = logging.getLogger(__name__)


@dataclass
class Level4Component:
    """Represents a Level 4 rule component"""
    name: str
    rules: List[ParsedRule]
    ontology: Ontology
    swrl_rules: List[str]
    

class Level4RuleSystem:
    """Complete Level 4 rule-based reasoning system"""
    
    def __init__(self):
        self.rule_generator = RuleGenerator()
        self.swrl_parser = SWRLParser()
        self.rule_executor = RuleExecutor(ReasonerType.HERMIT)
        self.generated_ontologies = {}
        
    def generate_rules_from_theory(self, theory_schema: Dict[str, Any]) -> Level4Component:
        """Generate complete rule system from theory schema"""
        
        theory_id = theory_schema.get('theory_id', 'unknown')
        logger.info(f"Generating Level 4 rules for {theory_id}")
        
        # Create ontology with classes and properties
        onto = self._create_base_ontology(theory_schema)
        
        # Extract and parse logical rules FIRST to know what properties we need
        swrl_rules = []
        parsed_rules = []
        
        logical_algos = theory_schema.get('algorithms', {}).get('logical', [])
        
        for algo in logical_algos:
            algo_name = algo.get('name', 'unnamed')
            rules = algo.get('rules', [])
            
            for rule_spec in rules:
                # Parse natural language rule to SWRL
                parsed_rule = self.swrl_parser.parse_rule(
                    rule_spec.get('condition', ''),
                    rule_spec.get('consequence', '') or rule_spec.get('conclusion', ''),
                    rule_spec.get('confidence', 1.0)
                )
                parsed_rules.append(parsed_rule)
                
                # Generate SWRL rule string
                swrl_string = self.swrl_parser.rule_to_swrl_string(parsed_rule)
                swrl_rules.append(swrl_string)
        
        # Ensure ALL properties and classes needed by rules exist
        # and add SWRL rules in the same with block
        with onto:
            # First create all needed properties and classes
            for parsed_rule in parsed_rules:
                self._ensure_properties_exist(onto, parsed_rule)
            
            # Log what we have after creating properties
            logger.info(f"Properties after ensure: {[p.name for p in onto.object_properties()]}")
            logger.info(f"Classes after ensure: {[c.name for c in onto.classes()]}")
            
            # Then add the SWRL rules
            for parsed_rule in parsed_rules:
                self._add_swrl_rule_to_ontology(onto, parsed_rule)
        
        # Save ontology
        onto_path = f"{theory_id}_rules.owl"
        onto.save(file=onto_path, format="rdfxml")
        
        component = Level4Component(
            name=theory_id,
            rules=parsed_rules,
            ontology=onto,
            swrl_rules=swrl_rules
        )
        
        self.generated_ontologies[theory_id] = component
        
        return component
    
    def _create_base_ontology(self, theory_schema: Dict[str, Any]) -> Ontology:
        """Create base ontology with classes and properties"""
        
        theory_id = theory_schema.get('theory_id', 'unknown')
        onto = get_ontology(f"http://kgas.ai/theories/{theory_id}#")
        
        with onto:
            # Create classes from entities
            entities = theory_schema.get('theoretical_structure', {}).get('entities', {})
            
            # V12 schema has entities as array
            if isinstance(entities, list):
                for entity in entities:
                    class_name = entity.get('indigenous_name', '').replace(' ', '_')
                    if class_name:
                        types.new_class(class_name, (Thing,))
            else:
                # V11 schema compatibility
                for entity_name in entities:
                    class_name = entity_name.replace(' ', '_')
                    types.new_class(class_name, (Thing,))
            
            # Create properties from relationships
            relations = theory_schema.get('theoretical_structure', {}).get('relations', [])
            
            if isinstance(relations, list):
                for relation in relations:
                    prop_name = relation.get('indigenous_name', '').replace(' ', '_')
                    if prop_name:
                        types.new_class(prop_name, (ObjectProperty,))
            else:
                # Fallback for other formats
                relationships = theory_schema.get('theoretical_structure', {}).get('relationships', {})
                for rel_name in relationships:
                    prop_name = rel_name.replace(' ', '_')
                    types.new_class(prop_name, (ObjectProperty,))
        
        return onto
    
    def _add_swrl_rule_to_ontology(self, onto: Ontology, parsed_rule: ParsedRule):
        """Add parsed SWRL rule to ontology"""
        
        try:
            # Convert parsed rule to SWRL string
            swrl_string = self.swrl_parser.rule_to_swrl_string(parsed_rule)
            
            # Create Imp (implication) for the rule
            imp = Imp()
            
            # Use the string notation which is simpler and more reliable
            # Convert our SWRL syntax to owlready2 format (use comma instead of ^)
            owlready_swrl = swrl_string.replace(" ^ ", ", ")
            
            # Special handling for "Different" which should be "differentFrom"
            owlready_swrl = owlready_swrl.replace("Different(", "differentFrom(")
            
            # Set the rule
            imp.set_as_rule(owlready_swrl)
                
        except Exception as e:
            logger.warning(f"Could not add SWRL rule to ontology: {e}")
    
    def _ensure_properties_exist(self, onto: Ontology, parsed_rule: ParsedRule):
        """Ensure all properties used in the rule exist in the ontology"""
        
        # Check all atoms in both antecedent and consequent
        all_atoms = parsed_rule.antecedent + parsed_rule.consequent
        
        for atom in all_atoms:
            if atom.atom_type == AtomType.OBJECT_PROPERTY:
                prop_name = atom.predicate
                
                # Check what hasattr returns
                has_it = hasattr(onto, prop_name)
                get_it = getattr(onto, prop_name, None)
                logger.info(f"Property {prop_name}: hasattr={has_it}, getattr={get_it}")
                
                # Create property if it doesn't exist
                if get_it is None:
                    new_prop = types.new_class(prop_name, (ObjectProperty,))
                    logger.info(f"Created property: {prop_name} -> {new_prop}")
                    
            elif atom.atom_type == AtomType.CLASS:
                class_name = atom.predicate
                
                # Create class if it doesn't exist
                if not hasattr(onto, class_name):
                    types.new_class(class_name, (Thing,))
                    
            # Builtins don't need to be created
    
    def execute_rules(self, theory_id: str, facts: List[Dict[str, Any]]) -> InferenceResult:
        """Execute rules with given facts"""
        
        if theory_id not in self.generated_ontologies:
            logger.error(f"No rules generated for theory {theory_id}")
            return InferenceResult(
                success=False,
                inferences=[],
                facts_before=0,
                facts_after=0,
                rules_fired=[],
                execution_time=0.0,
                error="Theory not found"
            )
        
        component = self.generated_ontologies[theory_id]
        onto_path = f"{theory_id}_rules.owl"
        
        # Load ontology into executor
        self.rule_executor.load_ontology(onto_path, theory_id)
        
        # Add facts
        self.rule_executor.add_facts(theory_id, facts)
        
        # Execute reasoning
        result = self.rule_executor.execute_reasoning(theory_id)
        
        return result
    
    def extract_facts_from_text(self, text: str, theory_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract facts from text based on theory schema"""
        
        facts = []
        seen_individuals = set()  # Track already created individuals
        
        # Get entities and relations from theory schema
        entities = theory_schema.get('theoretical_structure', {}).get('entities', [])
        relations = theory_schema.get('theoretical_structure', {}).get('relations', [])
        
        # Build entity type mapping
        entity_types = {}
        if isinstance(entities, list):
            for entity in entities:
                entity_name = entity.get('indigenous_name', '')
                entity_types[entity_name.lower()] = entity_name
        
        # Build relation mapping
        relation_types = {}
        if isinstance(relations, list):
            for relation in relations:
                rel_name = relation.get('indigenous_name', '')
                relation_types[rel_name.lower()] = rel_name
        
        import re
        
        # Multiple patterns for membership/belonging
        membership_patterns = [
            (r"(\w+)\s+belongs?\s+to\s+([\w\s]+?)(?:\.|,|;|$|\s+and\s+|\s+who\s+|\s+that\s+)", "belongsTo"),
            (r"(\w+)\s+is\s+a?\s*members?\s+of\s+([\w\s]+?)(?:\.|,|;|$|\s+and\s+|\s+who\s+|\s+that\s+)", "belongsTo"),
            (r"(\w+)\s+joined\s+([\w\s]+?)(?:\.|,|;|$|\s+and\s+|\s+who\s+|\s+that\s+|\s+recently)", "belongsTo"),
            (r"(\w+)\s+is\s+in\s+([\w\s]+?)(?:\.|,|;|$|\s+and\s+|\s+who\s+|\s+that\s+)", "belongsTo"),
            (r"(\w+)\s+is\s+part\s+of\s+([\w\s]+?)(?:\.|,|;|$|\s+and\s+|\s+who\s+|\s+that\s+)", "belongsTo"),
            (r"(\w+)\s+is\s+affiliated\s+with\s+([\w\s]+?)(?:\.|,|;|$|\s+and\s+|\s+who\s+|\s+that\s+)", "belongsTo"),
        ]
        
        # Apply membership patterns
        for pattern, relation in membership_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                subject, object_val = match
                
                # Create individuals if not seen
                subject_key = f"{subject.lower()}_Person"
                if subject_key not in seen_individuals:
                    facts.append({
                        'type': 'individual',
                        'class': 'Person',
                        'name': subject.lower()
                    })
                    seen_individuals.add(subject_key)
                
                object_key = f"{object_val.lower()}_Group"
                if object_key not in seen_individuals:
                    facts.append({
                        'type': 'individual',
                        'class': 'Group',
                        'name': object_val.lower()
                    })
                    seen_individuals.add(object_key)
                
                # Add relation
                facts.append({
                    'type': 'property',
                    'subject': subject.lower(),
                    'property': relation,
                    'object': object_val.lower()
                })
        
        # Pattern for influences/affects
        influence_patterns = [
            (r"(\w+)\s+influences?\s+(\w+)", "influences"),
            (r"(\w+)\s+affects?\s+(\w+)", "affects"),
            (r"(\w+)\s+impacts?\s+(\w+)", "impacts"),
        ]
        
        for pattern, relation in influence_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                subject, object_val = match
                
                # Ensure individuals exist
                for name in [subject, object_val]:
                    key = f"{name.lower()}_Person"
                    if key not in seen_individuals:
                        facts.append({
                            'type': 'individual',
                            'class': 'Person',
                            'name': name.lower()
                        })
                        seen_individuals.add(key)
                
                # Add relation
                facts.append({
                    'type': 'property',
                    'subject': subject.lower(),
                    'property': relation,
                    'object': object_val.lower()
                })
        
        # Pattern for "X is a Y" (class membership)
        class_patterns = [
            (r"(\w+)\s+is\s+a?\s*(\w+)", "class"),
            (r"(\w+),?\s+a\s+(\w+)", "class"),
        ]
        
        for pattern, _ in class_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                individual, class_name = match
                
                # Check if class_name is a known entity type
                if class_name.lower() in entity_types:
                    key = f"{individual.lower()}_{entity_types[class_name.lower()]}"
                    if key not in seen_individuals:
                        facts.append({
                            'type': 'individual',
                            'class': entity_types[class_name.lower()],
                            'name': individual.lower()
                        })
                        seen_individuals.add(key)
        
        return facts


# Example usage and testing
def test_level4_integration():
    """Test Level 4 integration"""
    
    print("=" * 60)
    print("LEVEL 4 (RULES) INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize system
    system = Level4RuleSystem()
    
    # Test theory with rules
    test_theory = {
        "theory_id": "social_identity_theory",
        "theoretical_structure": {
            "entities": [
                {"indigenous_name": "Person", "description": "Individual actor"},
                {"indigenous_name": "Group", "description": "Social group"}
            ],
            "relations": [
                {"indigenous_name": "belongsTo", "from_entity": "Person", "to_entity": "Group"}
            ]
        },
        "algorithms": {
            "logical": [{
                "name": "in_group_bias",
                "rules": [{
                    "condition": "Person ?x belongs to Group ?g AND Person ?y belongs to Group ?g",
                    "consequence": "Person ?x shows bias toward Person ?y",
                    "confidence": 0.8
                }]
            }]
        }
    }
    
    # Generate rules
    print("\n1. Generating rules from theory...")
    component = system.generate_rules_from_theory(test_theory)
    print(f"   Generated {len(component.rules)} rules")
    print(f"   SWRL rules:")
    for rule in component.swrl_rules:
        print(f"     {rule}")
    
    # Test text
    test_text = "Alice belongs to TeamA. Bob belongs to TeamA. Charlie belongs to TeamB."
    
    # Extract facts
    print(f"\n2. Extracting facts from text: '{test_text}'")
    facts = system.extract_facts_from_text(test_text, test_theory)
    print(f"   Extracted {len(facts)} facts:")
    for fact in facts[:5]:  # Show first 5
        print(f"     {fact}")
    
    # Execute reasoning
    print("\n3. Executing rule-based reasoning...")
    result = system.execute_rules("social_identity_theory", facts)
    
    print(f"   Success: {result.success}")
    print(f"   Facts before reasoning: {result.facts_before}")
    print(f"   Facts after reasoning: {result.facts_after}")
    print(f"   New inferences: {len(result.inferences)}")
    
    if result.inferences:
        print("   Inferences made:")
        for inf in result.inferences[:3]:  # Show first 3
            print(f"     {inf}")
    
    if result.error:
        print(f"   Error: {result.error}")
    
    print("\n" + "=" * 60)
    

if __name__ == "__main__":
    test_level4_integration()