#!/usr/bin/env python3
"""
Level 4 (RULES) Implementation for Theory-to-Code System

Generates OWL2 DL ontologies and SWRL rules from theory descriptions.
Handles logical reasoning and inference for social science theories.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from owlready2 import *

# Configure owlready2
onto_path.append(os.path.join(os.path.dirname(__file__), "ontologies"))

logger = logging.getLogger(__name__)


@dataclass
class GeneratedRule:
    """Represents a generated SWRL rule"""
    name: str
    swrl_rule: str
    owl_classes: List[str]
    owl_properties: List[str]
    source_theory: str
    confidence: float
    

class RuleGenerator:
    """Generates OWL2 DL ontologies and SWRL rules from theory descriptions"""
    
    def __init__(self, base_iri: str = "http://kgas.ai/theories/"):
        self.base_iri = base_iri
        self.namespaces = {
            "owl": "http://www.w3.org/2002/07/owl#",
            "swrl": "http://www.w3.org/2003/11/swrl#",
            "swrlb": "http://www.w3.org/2003/11/swrlb#"
        }
        
    def generate_ontology(self, theory_schema: Dict[str, Any]) -> Ontology:
        """Generate OWL2 DL ontology from theory schema"""
        
        theory_id = theory_schema.get('theory_id', 'unknown_theory')
        onto_iri = f"{self.base_iri}{theory_id}#"
        
        # Create new ontology
        onto = get_ontology(onto_iri)
        
        with onto:
            # Generate classes from entities
            self._generate_owl_classes(onto, theory_schema)
            
            # Generate properties from relationships
            self._generate_owl_properties(onto, theory_schema)
            
            # Generate SWRL rules from logical algorithms
            self._generate_swrl_rules(onto, theory_schema)
            
        return onto
    
    def _generate_owl_classes(self, onto: Ontology, theory_schema: Dict[str, Any]):
        """Generate OWL classes from theory entities"""
        
        entities = theory_schema.get('theoretical_structure', {}).get('entities', {})
        
        for entity_name, entity_def in entities.items():
            # Create OWL class
            owl_class = types.new_class(entity_name, (Thing,))
            
            # Add annotations
            if 'definition' in entity_def:
                owl_class.comment = [entity_def['definition']]
            
            # Handle entity types/subtypes
            if 'types' in entity_def:
                for subtype in entity_def['types']:
                    subclass = types.new_class(f"{entity_name}_{subtype}", (owl_class,))
                    
    def _generate_owl_properties(self, onto: Ontology, theory_schema: Dict[str, Any]):
        """Generate OWL properties from theory relationships"""
        
        relationships = theory_schema.get('theoretical_structure', {}).get('relationships', {})
        
        for rel_name, rel_def in relationships.items():
            # Determine property type
            if rel_def.get('type') == 'causal':
                # Object property for causal relationships
                prop = types.new_class(rel_name, (ObjectProperty,))
                
                # Set domain and range if specified
                if 'from_entity' in rel_def:
                    prop.domain = [getattr(onto, rel_def['from_entity'])]
                if 'to_entity' in rel_def:
                    prop.range = [getattr(onto, rel_def['to_entity'])]
                    
                # Add characteristics
                properties = rel_def.get('properties', [])
                if 'transitive' in properties:
                    prop.is_a.append(TransitiveProperty)
                if 'symmetric' in properties:
                    prop.is_a.append(SymmetricProperty)
                    
    def _generate_swrl_rules(self, onto: Ontology, theory_schema: Dict[str, Any]):
        """Generate SWRL rules from logical algorithms"""
        
        logical_algos = theory_schema.get('algorithms', {}).get('logical', [])
        
        for algo in logical_algos:
            rule_name = algo.get('name', 'unnamed_rule')
            rules = algo.get('rules', [])
            
            for rule_spec in rules:
                swrl_rule = self._create_swrl_rule(
                    onto,
                    rule_spec['condition'],
                    rule_spec['consequence'],
                    rule_spec.get('confidence', 1.0)
                )
                
                # Store rule in ontology if created
                if swrl_rule:
                    swrl_rule.comment = [f"Generated from {rule_name}"]
                
    def _create_swrl_rule(self, onto: Ontology, condition: str, consequence: str, confidence: float) -> Optional[Imp]:
        """Create SWRL rule from condition and consequence strings"""
        
        try:
            # Import the parser
            from .swrl_parser import SWRLParser
            
            # Parse the rule
            parser = SWRLParser()
            parsed_rule = parser.parse_rule(condition, consequence, confidence)
            
            # Generate SWRL string
            swrl_string = parser.rule_to_swrl_string(parsed_rule)
            
            # For now, just log the parsed rule
            # Actual SWRL atom creation would be done here
            logger.info(f"Parsed rule: {swrl_string}")
            
            # Return None since we can't create proper SWRL rules here
            # This should be done through level4_integration.py
            return None
            
        except Exception as e:
            logger.error(f"Failed to create SWRL rule: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Test with a simple theory
    test_theory = {
        "theory_id": "social_identity_theory",
        "theoretical_structure": {
            "entities": {
                "Person": {"definition": "An individual actor"},
                "Group": {"definition": "A social group"}
            },
            "relationships": {
                "belongsTo": {
                    "type": "membership",
                    "from_entity": "Person",
                    "to_entity": "Group"
                }
            }
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
    
    generator = RuleGenerator()
    ontology = generator.generate_ontology(test_theory)
    
    # Save ontology
    ontology.save(file="test_social_identity.owl", format="rdfxml")
    print(f"Generated ontology with {len(list(ontology.classes()))} classes")