"""
Ontology Validation Module

Decomposed ontology validation components for validating entities and relationships
against Master Concept Library and DOLCE ontology standards.
"""

from .core_validators import MasterConceptValidator, DolceValidator
from .template_generators import EntityTemplateGenerator, RelationshipTemplateGenerator
from .suggestion_engine import TypeSuggestionEngine, ConceptMappingEngine
from .enrichment_processor import EntityEnricher, RelationshipEnricher
from .comprehensive_tester import ComprehensiveOntologyTester
from .ontology_validator import OntologyValidator

__all__ = [
    # Core validation engines
    "MasterConceptValidator", "DolceValidator",
    
    # Template generation
    "EntityTemplateGenerator", "RelationshipTemplateGenerator",
    
    # Suggestion and mapping
    "TypeSuggestionEngine", "ConceptMappingEngine",
    
    # Data enrichment
    "EntityEnricher", "RelationshipEnricher",
    
    # Comprehensive testing
    "ComprehensiveOntologyTester",
    
    # Main validator
    "OntologyValidator"
]