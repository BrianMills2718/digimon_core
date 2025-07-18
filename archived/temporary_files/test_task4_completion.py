#!/usr/bin/env python3
"""Test Task 4 Completion - DOLCE Ontology Mapping Implementation

This script tests that Task 4 has been successfully completed by verifying:
1. DOLCE ontology models are properly implemented
2. GraphRAG to DOLCE mapping works correctly
3. DOLCE validation is functional
4. Integration with existing ontology validator works
5. All DOLCE components are operational
"""

import sys
sys.path.insert(0, '/home/brian/Digimons/src')

from src.ontology_library.dolce_ontology import dolce_ontology, DOLCECategory, DOLCERelationType
from src.core.ontology_validator import OntologyValidator
from src.core.data_models import Entity, Relationship
from src.core.evidence_logger import evidence_logger
import datetime

def test_dolce_ontology_implementation():
    """Test DOLCE ontology implementation"""
    print("Testing DOLCE Ontology Implementation...")
    
    # Test basic functionality
    concept_count = len(dolce_ontology.concepts)
    relation_count = len(dolce_ontology.relations)
    mapping_count = len(dolce_ontology.graphrag_mappings)
    
    print(f"  - DOLCE concepts: {concept_count}")
    print(f"  - DOLCE relations: {relation_count}")
    print(f"  - GraphRAG mappings: {mapping_count}")
    
    # Test concept retrieval
    endurant_concept = dolce_ontology.get_dolce_concept("Endurant")
    has_endurant = endurant_concept is not None
    print(f"  - Endurant concept found: {has_endurant}")
    
    # Test relation retrieval
    part_of_relation = dolce_ontology.get_dolce_relation("part_of")
    has_part_of = part_of_relation is not None
    print(f"  - Part_of relation found: {has_part_of}")
    
    # Test ontology summary
    summary = dolce_ontology.get_ontology_summary()
    has_summary = "total_concepts" in summary
    print(f"  - Ontology summary working: {has_summary}")
    
    return {
        'concepts_loaded': concept_count > 0,
        'relations_loaded': relation_count > 0,
        'mappings_loaded': mapping_count > 0,
        'concept_retrieval': has_endurant,
        'relation_retrieval': has_part_of,
        'summary_working': has_summary
    }

def test_graphrag_to_dolce_mapping():
    """Test GraphRAG to DOLCE mapping functionality"""
    print("Testing GraphRAG to DOLCE Mapping...")
    
    test_mappings = [
        ("IndividualActor", "PhysicalEndurant"),
        ("Organization", "SocialEndurant"),
        ("System", "AbstractEndurant"),
        ("Event", "Event"),
        ("Message", "AbstractEndurant"),
        ("Location", "PhysicalEndurant"),
        ("leads", "participates_in"),
        ("part_of", "part_of"),
        ("located_in", "spatially_located_in")
    ]
    
    mapping_results = []
    for graphrag_concept, expected_dolce in test_mappings:
        actual_dolce = dolce_ontology.map_to_dolce(graphrag_concept)
        matches = actual_dolce == expected_dolce
        mapping_results.append(matches)
        print(f"  - {graphrag_concept} -> {actual_dolce} (expected: {expected_dolce}): {matches}")
    
    # Test unknown concept
    unknown_mapping = dolce_ontology.map_to_dolce("UnknownConcept")
    unknown_handled = unknown_mapping is None
    print(f"  - Unknown concept handled: {unknown_handled}")
    
    return {
        'mappings_working': sum(mapping_results),
        'total_mappings_tested': len(mapping_results),
        'unknown_concepts_handled': unknown_handled,
        'mapping_accuracy': sum(mapping_results) / len(mapping_results) if mapping_results else 0
    }

def test_dolce_validation():
    """Test DOLCE validation functionality"""
    print("Testing DOLCE Validation...")
    
    # Test entity validation
    entity_data = {
        "entity_id": "test_entity",
        "entity_type": "IndividualActor",
        "canonical_name": "John Doe",
        "surface_form": "John",
        "confidence": 0.9,
        "properties": {"location": "New York"},
        "modifiers": {}
    }
    
    entity_errors = dolce_ontology.validate_entity_against_dolce("IndividualActor", entity_data)
    entity_validation_works = isinstance(entity_errors, list)
    print(f"  - Entity validation works: {entity_validation_works}")
    print(f"  - Entity validation errors: {len(entity_errors)}")
    
    # Test relationship validation
    relationship_errors = dolce_ontology.validate_relationship_against_dolce(
        "leads", "IndividualActor", "Organization"
    )
    relationship_validation_works = isinstance(relationship_errors, list)
    print(f"  - Relationship validation works: {relationship_validation_works}")
    print(f"  - Relationship validation errors: {len(relationship_errors)}")
    
    # Test invalid entity type
    invalid_entity_errors = dolce_ontology.validate_entity_against_dolce("InvalidType", entity_data)
    invalid_handled = len(invalid_entity_errors) > 0
    print(f"  - Invalid entity type handled: {invalid_handled}")
    
    return {
        'entity_validation_functional': entity_validation_works,
        'relationship_validation_functional': relationship_validation_works,
        'invalid_types_handled': invalid_handled,
        'validation_system_working': entity_validation_works and relationship_validation_works
    }

def test_ontology_validator_integration():
    """Test integration with existing ontology validator"""
    print("Testing Ontology Validator Integration...")
    
    try:
        # Create ontology validator
        validator = OntologyValidator()
        has_dolce = hasattr(validator, 'dolce')
        print(f"  - Validator has DOLCE: {has_dolce}")
        
        # Test DOLCE validation methods
        has_dolce_entity_validation = hasattr(validator, 'validate_entity_with_dolce')
        has_dolce_relationship_validation = hasattr(validator, 'validate_relationship_with_dolce')
        has_comprehensive_validation = hasattr(validator, 'validate_entity_comprehensive')
        
        print(f"  - DOLCE entity validation method: {has_dolce_entity_validation}")
        print(f"  - DOLCE relationship validation method: {has_dolce_relationship_validation}")
        print(f"  - Comprehensive validation method: {has_comprehensive_validation}")
        
        # Test DOLCE mapping methods
        has_dolce_mapping = hasattr(validator, 'get_dolce_mapping')
        has_dolce_concept_info = hasattr(validator, 'get_dolce_concept_info')
        has_ontology_summary = hasattr(validator, 'get_ontology_summary')
        
        print(f"  - DOLCE mapping method: {has_dolce_mapping}")
        print(f"  - DOLCE concept info method: {has_dolce_concept_info}")
        print(f"  - Ontology summary method: {has_ontology_summary}")
        
        # Test actual DOLCE mapping
        mapping = validator.get_dolce_mapping("IndividualActor")
        mapping_works = mapping == "PhysicalEndurant"
        print(f"  - Actual DOLCE mapping works: {mapping_works}")
        
        # Test ontology summary
        summary = validator.get_ontology_summary()
        summary_works = "dolce_ontology" in summary
        print(f"  - Ontology summary includes DOLCE: {summary_works}")
        
        return {
            'validator_has_dolce': has_dolce,
            'dolce_methods_available': has_dolce_entity_validation and has_dolce_relationship_validation,
            'comprehensive_validation_available': has_comprehensive_validation,
            'mapping_methods_available': has_dolce_mapping and has_dolce_concept_info,
            'integration_working': mapping_works and summary_works
        }
        
    except Exception as e:
        print(f"  - Integration test error: {e}")
        return {
            'validator_has_dolce': False,
            'dolce_methods_available': False,
            'comprehensive_validation_available': False,
            'mapping_methods_available': False,
            'integration_working': False
        }

def test_dolce_categories_and_relations():
    """Test DOLCE categories and relations"""
    print("Testing DOLCE Categories and Relations...")
    
    # Test category enumeration
    categories = [cat.value for cat in DOLCECategory]
    expected_categories = ["endurant", "perdurant", "quality", "abstract", "temporal_quality", "physical_quality", "social_quality"]
    categories_match = all(cat in categories for cat in expected_categories)
    print(f"  - All expected categories present: {categories_match}")
    
    # Test relation types
    relation_types = [rel.value for rel in DOLCERelationType]
    expected_relations = ["part_of", "depends_on", "participates_in", "inherent_in", "constitutes"]
    relations_match = all(rel in relation_types for rel in expected_relations)
    print(f"  - All expected relation types present: {relations_match}")
    
    # Test concept categories
    endurant_concept = dolce_ontology.get_dolce_concept("Endurant")
    endurant_category_correct = endurant_concept and endurant_concept.category == DOLCECategory.ENDURANT
    print(f"  - Endurant category correct: {endurant_category_correct}")
    
    # Test relation structure
    part_of_relation = dolce_ontology.get_dolce_relation("part_of")
    part_of_structure_correct = (part_of_relation and 
                               part_of_relation.relation_type == DOLCERelationType.PART_OF and
                               part_of_relation.domain == "Particular")
    print(f"  - Part_of relation structure correct: {part_of_structure_correct}")
    
    return {
        'categories_complete': categories_match,
        'relation_types_complete': relations_match,
        'concept_categories_correct': endurant_category_correct,
        'relation_structure_correct': part_of_structure_correct
    }

def main():
    """Run all tests and log evidence"""
    print("=== TASK 4 COMPLETION VERIFICATION ===")
    print("Testing DOLCE Ontology Mapping Implementation...")
    
    try:
        # Run all tests
        implementation_results = test_dolce_ontology_implementation()
        mapping_results = test_graphrag_to_dolce_mapping()
        validation_results = test_dolce_validation()
        integration_results = test_ontology_validator_integration()
        categories_results = test_dolce_categories_and_relations()
        
        # Check overall success
        all_passed = (
            implementation_results['concepts_loaded'] and
            implementation_results['relations_loaded'] and
            implementation_results['mappings_loaded'] and
            mapping_results['mapping_accuracy'] > 0.8 and
            validation_results['validation_system_working'] and
            integration_results['integration_working'] and
            categories_results['categories_complete'] and
            categories_results['relation_types_complete']
        )
        
        print(f"\n=== RESULTS ===")
        print(f"DOLCE concepts loaded: {implementation_results['concepts_loaded']}")
        print(f"DOLCE relations loaded: {implementation_results['relations_loaded']}")
        print(f"GraphRAG mappings loaded: {implementation_results['mappings_loaded']}")
        print(f"Mapping accuracy: {mapping_results['mapping_accuracy']:.2%}")
        print(f"Validation system working: {validation_results['validation_system_working']}")
        print(f"Integration working: {integration_results['integration_working']}")
        print(f"Categories complete: {categories_results['categories_complete']}")
        print(f"Relation types complete: {categories_results['relation_types_complete']}")
        
        if all_passed:
            print("✅ TASK 4 COMPLETED SUCCESSFULLY")
        else:
            print("❌ TASK 4 FAILED")
            
        # Log evidence
        evidence_logger.log_task_completion(
            "TASK4_DOLCE_ONTOLOGY_MAPPING",
            {
                "task_description": "Implement DOLCE Ontology Mapping",
                "files_created": [
                    "src/ontology_library/dolce_ontology.py",
                    "src/core/ontology_validator.py (updated with DOLCE integration)"
                ],
                "implementation_results": implementation_results,
                "mapping_results": mapping_results,
                "validation_results": validation_results,
                "integration_results": integration_results,
                "categories_results": categories_results
            },
            all_passed
        )
        
        return all_passed
        
    except Exception as e:
        print(f"❌ TASK 4 FAILED WITH ERROR: {e}")
        
        # Log evidence of failure
        evidence_logger.log_task_completion(
            "TASK4_DOLCE_ONTOLOGY_MAPPING",
            {
                "task_description": "Implement DOLCE Ontology Mapping",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            },
            False
        )
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)