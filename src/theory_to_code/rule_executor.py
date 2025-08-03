#!/usr/bin/env python3
"""
Level 4 (RULES) Executor for Theory-to-Code System

Executes OWL2 DL ontologies and SWRL rules using reasoners.
Performs inference and logical reasoning for social science theories.
"""

import os
import logging
import time
import subprocess
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from owlready2 import *

logger = logging.getLogger(__name__)


class ReasonerType(Enum):
    """Available reasoner types"""
    HERMIT = "hermit"
    PELLET = "pellet"
    FACT = "fact++"
    

@dataclass
class InferenceResult:
    """Result of rule-based inference"""
    success: bool
    inferences: List[Dict[str, Any]]
    facts_before: int
    facts_after: int
    rules_fired: List[str]
    execution_time: float
    error: Optional[str] = None
    reasoning_log: Optional[List[str]] = None
    

@dataclass
class QueryResult:
    """Result of querying the knowledge base"""
    success: bool
    results: List[Dict[str, Any]]
    query_time: float
    error: Optional[str] = None


class RuleExecutor:
    """Executes OWL2/SWRL rules and performs reasoning"""
    
    def __init__(self, reasoner_type: ReasonerType = ReasonerType.HERMIT):
        self.reasoner_type = reasoner_type
        self.ontologies = {}
        self.reasoner = None
        self._java_available = None  # Cache Java availability check
        
    def load_ontology(self, ontology_path: str, name: str) -> bool:
        """Load an OWL ontology"""
        
        try:
            onto = get_ontology(ontology_path).load()
            self.ontologies[name] = onto
            logger.info(f"Loaded ontology {name} from {ontology_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            return False
    
    def add_facts(self, ontology_name: str, facts: List[Dict[str, Any]]) -> bool:
        """Add facts (individuals and assertions) to ontology"""
        
        if ontology_name not in self.ontologies:
            logger.error(f"Ontology {ontology_name} not loaded")
            return False
            
        onto = self.ontologies[ontology_name]
        
        try:
            with onto:
                for fact in facts:
                    self._add_fact(onto, fact)
            return True
        except Exception as e:
            logger.error(f"Failed to add facts: {e}")
            return False
    
    def _add_fact(self, onto: Ontology, fact: Dict[str, Any]):
        """Add a single fact to the ontology"""
        
        fact_type = fact.get('type', 'individual')
        
        if fact_type == 'individual':
            # Create individual of a class
            class_name = fact['class']
            individual_name = fact['name']
            
            # Get the class
            owl_class = getattr(onto, class_name, None)
            if not owl_class:
                logger.warning(f"Class {class_name} not found in ontology")
                return
                
            # Create individual
            individual = owl_class(individual_name)
            
        elif fact_type == 'property':
            # Add property assertion
            subject = fact['subject']
            property_name = fact['property']
            object_value = fact['object']
            
            # Get individuals
            subj_ind = getattr(onto, subject, None)
            if not subj_ind:
                logger.warning(f"Individual {subject} not found")
                return
                
            # Get property
            prop = getattr(onto, property_name, None)
            if not prop:
                logger.warning(f"Property {property_name} not found")
                return
                
            # Add assertion
            if isinstance(object_value, str) and hasattr(onto, object_value):
                # Object property
                obj_ind = getattr(onto, object_value)
                prop[subj_ind].append(obj_ind)
            else:
                # Data property
                prop[subj_ind].append(object_value)
    
    def _check_java_availability(self) -> Dict[str, Any]:
        """Check if Java is available on the system"""
        
        if self._java_available is not None:
            return self._java_available
            
        try:
            # Try to run java -version
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            
            if result.returncode == 0:
                # Parse version from stderr (Java outputs version info to stderr)
                version_info = result.stderr
                self._java_available = {
                    'available': True,
                    'version': version_info.split('\n')[0],
                    'error': None
                }
            else:
                self._java_available = {
                    'available': False,
                    'version': None,
                    'error': 'Java command failed'
                }
                
        except FileNotFoundError:
            self._java_available = {
                'available': False,
                'version': None,
                'error': 'Java not found in PATH'
            }
        except subprocess.TimeoutExpired:
            self._java_available = {
                'available': False,
                'version': None,
                'error': 'Java check timed out'
            }
        except Exception as e:
            self._java_available = {
                'available': False,
                'version': None,
                'error': str(e)
            }
            
        return self._java_available
    
    def execute_reasoning(self, ontology_name: str, 
                         infer_property_values: bool = True,
                         infer_data_property_values: bool = True) -> InferenceResult:
        """Execute reasoning on the ontology"""
        
        if ontology_name not in self.ontologies:
            return InferenceResult(
                success=False,
                inferences=[],
                facts_before=0,
                facts_after=0,
                rules_fired=[],
                execution_time=0.0,
                error=f"Ontology {ontology_name} not loaded"
            )
        
        # Check Java availability before attempting reasoning
        java_check = self._check_java_availability()
        if not java_check['available']:
            return InferenceResult(
                success=False,
                inferences=[],
                facts_before=0,
                facts_after=0,
                rules_fired=[],
                execution_time=0.0,
                error=f"Java not available: {java_check['error']}. "
                      f"Please install Java 8 or higher to use reasoning."
            )
        
        onto = self.ontologies[ontology_name]
        start_time = time.time()
        
        try:
            # Count facts before reasoning
            facts_before = self._count_facts(onto)
            
            # Run reasoner
            with onto:
                if self.reasoner_type == ReasonerType.HERMIT:
                    sync_reasoner_hermit(onto)
                elif self.reasoner_type == ReasonerType.PELLET:
                    sync_reasoner_pellet(onto)
                else:
                    # Default to HermiT
                    sync_reasoner_hermit(onto)
            
            # Count facts after reasoning
            facts_after = self._count_facts(onto)
            
            # Extract inferences
            inferences = self._extract_inferences(onto, facts_before)
            
            execution_time = time.time() - start_time
            
            return InferenceResult(
                success=True,
                inferences=inferences,
                facts_before=facts_before,
                facts_after=facts_after,
                rules_fired=self._get_fired_rules(onto),
                execution_time=execution_time
            )
            
        except FileNotFoundError as e:
            if "java" in str(e).lower():
                return InferenceResult(
                    success=False,
                    inferences=[],
                    facts_before=facts_before if 'facts_before' in locals() else 0,
                    facts_after=0,
                    rules_fired=[],
                    execution_time=time.time() - start_time,
                    error="Java not found. Please install Java 8 or higher to use reasoning."
                )
            else:
                return InferenceResult(
                    success=False,
                    inferences=[],
                    facts_before=facts_before if 'facts_before' in locals() else 0,
                    facts_after=0,
                    rules_fired=[],
                    execution_time=time.time() - start_time,
                    error=f"File not found: {e}"
                )
                
        except subprocess.CalledProcessError as e:
            return InferenceResult(
                success=False,
                inferences=[],
                facts_before=facts_before if 'facts_before' in locals() else 0,
                facts_after=0,
                rules_fired=[],
                execution_time=time.time() - start_time,
                error=f"Reasoner process failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"
            )
            
        except Exception as e:
            return InferenceResult(
                success=False,
                inferences=[],
                facts_before=facts_before if 'facts_before' in locals() else 0,
                facts_after=0,
                rules_fired=[],
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    def _count_facts(self, onto: Ontology) -> int:
        """Count total facts in ontology"""
        
        count = 0
        
        # Count individuals
        for individual in onto.individuals():
            count += 1
            # Count property assertions
            for prop in individual.get_properties():
                for value in prop[individual]:
                    count += 1
        
        return count
    
    def _extract_inferences(self, onto: Ontology, facts_before: int) -> List[Dict[str, Any]]:
        """Extract new inferences made by reasoner"""
        
        inferences = []
        fact_count = 0
        
        for individual in onto.individuals():
            fact_count += 1
            
            # Check for inferred class memberships
            for cls in individual.is_a:
                if cls != Thing:
                    inferences.append({
                        'type': 'class_membership',
                        'individual': individual.name,
                        'class': cls.name,
                        'inferred': fact_count > facts_before
                    })
            
            # Check for inferred property values
            for prop in individual.get_properties():
                for value in prop[individual]:
                    fact_count += 1
                    inferences.append({
                        'type': 'property_assertion',
                        'subject': individual.name,
                        'property': prop.name,
                        'object': value.name if hasattr(value, 'name') else str(value),
                        'inferred': fact_count > facts_before
                    })
        
        # Return only new inferences
        return [inf for inf in inferences if inf.get('inferred', False)]
    
    def _get_fired_rules(self, onto: Ontology) -> List[str]:
        """Get list of rules that fired during reasoning"""
        
        # This is a simplified version - real implementation would
        # track which SWRL rules actually fired
        rules = []
        
        for rule in onto.rules():
            rules.append(str(rule))
            
        return rules
    
    def query(self, ontology_name: str, query_type: str, 
              parameters: Dict[str, Any]) -> QueryResult:
        """Query the knowledge base"""
        
        if ontology_name not in self.ontologies:
            return QueryResult(
                success=False,
                results=[],
                query_time=0.0,
                error=f"Ontology {ontology_name} not loaded"
            )
        
        onto = self.ontologies[ontology_name]
        start_time = time.time()
        
        try:
            if query_type == "instances_of_class":
                # Find all instances of a class
                class_name = parameters['class']
                owl_class = getattr(onto, class_name)
                results = [{'name': ind.name, 'class': class_name} 
                          for ind in owl_class.instances()]
                
            elif query_type == "property_values":
                # Find property values for an individual
                individual_name = parameters['individual']
                property_name = parameters.get('property')
                
                individual = getattr(onto, individual_name)
                results = []
                
                if property_name:
                    prop = getattr(onto, property_name)
                    values = prop[individual]
                    results = [{'property': property_name, 'value': str(v)} 
                              for v in values]
                else:
                    # All properties
                    for prop in individual.get_properties():
                        for value in prop[individual]:
                            results.append({
                                'property': prop.name,
                                'value': str(value)
                            })
                            
            elif query_type == "sparql":
                # SPARQL query
                query = parameters['query']
                results = list(default_world.sparql(query))
                
            else:
                results = []
                
            query_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                results=results,
                query_time=query_time
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                results=[],
                query_time=time.time() - start_time,
                error=str(e)
            )


# Example usage
if __name__ == "__main__":
    executor = RuleExecutor(ReasonerType.HERMIT)
    
    # Test with the generated ontology
    if os.path.exists("test_social_identity.owl"):
        executor.load_ontology("test_social_identity.owl", "social_identity")
        
        # Add some test facts
        facts = [
            {'type': 'individual', 'class': 'Person', 'name': 'alice'},
            {'type': 'individual', 'class': 'Person', 'name': 'bob'},
            {'type': 'individual', 'class': 'Group', 'name': 'group1'},
            {'type': 'property', 'subject': 'alice', 'property': 'belongsTo', 'object': 'group1'},
            {'type': 'property', 'subject': 'bob', 'property': 'belongsTo', 'object': 'group1'}
        ]
        
        executor.add_facts("social_identity", facts)
        
        # Run reasoning
        result = executor.execute_reasoning("social_identity")
        
        print(f"Reasoning completed: {result.success}")
        print(f"Facts before: {result.facts_before}")
        print(f"Facts after: {result.facts_after}")
        print(f"New inferences: {len(result.inferences)}")
        
        for inference in result.inferences:
            print(f"  - {inference}")
    else:
        print("Test ontology not found. Run rule_generator.py first.")