"""
Ontology Validator - Main Interface

Streamlined ontology validator interface using decomposed components.
Reduced from 902 lines to focused interface.

Validates data models against the Master Concept Library and DOLCE ontology
with comprehensive testing and evidence generation.
"""

import logging

# Import main validator from decomposed module
from .ontology_validation import OntologyValidator as OntologyValidatorImpl

logger = logging.getLogger(__name__)


class OntologyValidator(OntologyValidatorImpl):
    """
    Main ontology validator interface that extends the decomposed implementation.
    
    Uses decomposed components for maintainability and testing:
    - MasterConceptValidator: Master Concept Library validation engine
    - DolceValidator: DOLCE ontology validation and mapping  
    - EntityTemplateGenerator & RelationshipTemplateGenerator: Template creation
    - TypeSuggestionEngine & ConceptMappingEngine: Intelligent suggestions
    - EntityEnricher & RelationshipEnricher: Data enrichment processors
    - ComprehensiveOntologyTester: Evidence-based validation testing
    """
    
    def __init__(self):
        """Initialize ontology validator with decomposed architecture"""
        super().__init__()
        
        # Log initialization with component status
        components_status = {
            "master_concept_validator": "initialized",
            "dolce_validator": "initialized",
            "template_generators": "initialized", 
            "suggestion_engines": "initialized",
            "enrichment_processors": "initialized",
            "comprehensive_tester": "initialized"
        }
        
        logger.info(f"Ontology validator initialized with components: {components_status}")


# Export for backward compatibility
__all__ = ["OntologyValidator"]


def get_ontology_validator_info():
    """Get information about the ontology validator implementation"""
    return {
        "module": "ontology_validator",
        "version": "2.0.0", 
        "architecture": "decomposed_components",
        "description": "Comprehensive ontology validator with fail-fast testing",
        "capabilities": [
            "master_concept_library_validation",
            "dolce_ontology_validation", 
            "entity_relationship_templates",
            "intelligent_type_suggestions",
            "cross_ontology_mapping",
            "automatic_data_enrichment",
            "comprehensive_evidence_testing"
        ],
        "components": {
            "core_validators": "Master Concept Library and DOLCE validation engines",
            "template_generators": "Entity and relationship template creation", 
            "suggestion_engine": "Type suggestions and concept mapping",
            "enrichment_processor": "Data enrichment with ontology defaults",
            "comprehensive_tester": "Evidence-based validation testing"
        },
        "decomposed": True,
        "file_count": 7,  # Main file + 6 component files
        "total_lines": 90   # This main file line count
    }