#!/usr/bin/env python3
"""Test script for the new schema system

Tests all three schema modes (open, closed, hybrid) with validation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import json
from typing import Dict, Any
from src.core.extraction_schemas import (
    create_open_schema, create_closed_schema, create_hybrid_schema,
    get_academic_paper_schema, get_business_document_schema, get_general_open_schema
)
from src.core.schema_manager import SchemaManager
from src.tools.base_tool import ToolRequest


def test_schema_creation():
    """Test basic schema creation"""
    print("=== Testing Schema Creation ===")
    
    # Test open schema
    open_schema = create_open_schema("test_open", "Test open schema")
    print(f"✓ Created open schema: {open_schema.schema_id}")
    
    # Test closed schema
    closed_schema = create_closed_schema(
        "test_closed", 
        ["Person", "Organization", "Location"],
        ["works_for", "located_in"]
    )
    print(f"✓ Created closed schema: {closed_schema.schema_id}")
    
    # Test hybrid schema
    hybrid_schema = create_hybrid_schema(
        "test_hybrid",
        ["Person", "Organization"],
        ["works_for"]
    )
    print(f"✓ Created hybrid schema: {hybrid_schema.schema_id}")
    
    return True


def test_builtin_schemas():
    """Test built-in schema templates"""
    print("\n=== Testing Built-in Schemas ===")
    
    academic = get_academic_paper_schema()
    print(f"✓ Academic paper schema: {len(academic.entity_types)} entity types, {len(academic.relation_types)} relation types")
    
    business = get_business_document_schema()
    print(f"✓ Business document schema: {len(business.entity_types)} entity types, {len(business.relation_types)} relation types")
    
    general = get_general_open_schema()
    print(f"✓ General open schema: {general.mode.value} mode")
    
    return True


def test_schema_manager():
    """Test schema manager functionality"""
    print("\n=== Testing Schema Manager ===")
    
    manager = SchemaManager()
    
    # List schemas
    schemas = manager.list_schemas()
    print(f"✓ Found {len(schemas)} schemas: {', '.join(schemas)}")
    
    # Get default schema
    default = manager.get_default_schema()
    print(f"✓ Default schema: {default.schema_id} ({default.mode.value})")
    
    # Test schema statistics
    stats = manager.get_schema_statistics()
    print(f"✓ Schema statistics: {stats['total_schemas']} total, {stats['schemas_by_mode']}")
    
    return True


def test_spacy_ner_with_schema():
    """Test T23A SpaCy NER with schema support"""
    print("\n=== Testing T23A SpaCy NER with Schema ===")
    
    try:
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.core.service_manager import ServiceManager
        
        # Initialize service manager and tool
        service_manager = ServiceManager()
        ner_tool = T23ASpacyNERUnified(service_manager)
        
        # Test with closed schema
        closed_schema = create_closed_schema(
            "person_org_test",
            ["PERSON", "ORG"],  # Use spaCy entity types
            []
        )
        
        test_text = "John Smith works for Microsoft Corporation in Seattle."
        
        request = ToolRequest(
            tool_id="T23A_SPACY_NER",
            operation="extract",
            input_data={
                "text": test_text,
                "chunk_ref": "test_chunk_001",
                "schema": closed_schema
            },
            parameters={}
        )
        
        result = ner_tool.execute(request)
        
        if result.status == "success":
            entities = result.data["entities"]
            print(f"✓ T23A extracted {len(entities)} entities with closed schema")
            for entity in entities:
                print(f"  - {entity['surface_form']} ({entity['entity_type']}) confidence: {entity['confidence']:.3f}")
        else:
            print(f"✗ T23A failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"✗ T23A test failed: {e}")
        return False
    
    return True


def test_llm_extractor_with_schema():
    """Test T23C LLM extractor with schema support"""
    print("\n=== Testing T23C LLM Extractor with Schema ===")
    
    try:
        from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor
        
        extractor = OntologyAwareExtractor()
        
        # Test with hybrid schema
        hybrid_schema = create_hybrid_schema(
            "academic_hybrid",
            ["Author", "Institution", "Method"],
            ["affiliated_with", "uses"]
        )
        
        test_text = "Dr. Jane Doe from Stanford University developed a new machine learning algorithm."
        
        result = extractor.execute({
            "text": test_text,
            "source_ref": "test_doc_001",
            "schema": hybrid_schema,
            "use_mock_apis": True  # Use mock for testing
        })
        
        if "error" not in result:
            entities = result["results"]["entities"]
            print(f"✓ T23C extracted {len(entities)} entities with hybrid schema")
            for entity in entities:
                print(f"  - {entity['surface_form']} ({entity['entity_type']}) confidence: {entity['confidence']:.3f}")
        else:
            print(f"✗ T23C failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"✗ T23C test failed: {e}")
        return False
    
    return True


def test_schema_validation():
    """Test schema validation functionality"""
    print("\n=== Testing Schema Validation ===")
    
    # Create test extraction result
    test_extraction = {
        "entities": [
            {
                "id": "entity_001",
                "type": "Person",
                "surface_form": "John Smith",
                "confidence": 0.9
            },
            {
                "id": "entity_002", 
                "type": "Organization",
                "surface_form": "Microsoft",
                "confidence": 0.85
            },
            {
                "id": "entity_003",
                "type": "UnknownType",  # This should fail validation in closed mode
                "surface_form": "Something",
                "confidence": 0.7
            }
        ],
        "relations": [
            {
                "id": "rel_001",
                "type": "works_for",
                "source_entity_type": "Person",
                "target_entity_type": "Organization",
                "confidence": 0.8
            }
        ]
    }
    
    # Test with closed schema
    closed_schema = create_closed_schema(
        "validation_test",
        ["Person", "Organization"],
        ["works_for"]
    )
    
    validation_result = closed_schema.validate_extraction_result(test_extraction)
    
    print(f"✓ Validation result: valid={validation_result['valid']}")
    print(f"  Errors: {len(validation_result['errors'])}")
    print(f"  Warnings: {len(validation_result['warnings'])}")
    
    if validation_result['errors']:
        print("  Error details:")
        for error in validation_result['errors']:
            print(f"    - {error}")
    
    return True


def test_all_schema_modes():
    """Test all three schema modes with sample data"""
    print("\n=== Testing All Schema Modes ===")
    
    # Sample text
    test_text = "Dr. Alice Johnson, a researcher at MIT, published a paper on quantum computing using Python programming language."
    
    schemas = {
        "open": get_general_open_schema(),
        "closed": create_closed_schema("test_closed", ["PERSON", "ORG", "LANGUAGE"], []),
        "hybrid": create_hybrid_schema("test_hybrid", ["PERSON", "ORG"], [])
    }
    
    results = {}
    
    try:
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.core.service_manager import ServiceManager
        
        service_manager = ServiceManager()
        ner_tool = T23ASpacyNERUnified(service_manager)
        
        for mode, schema in schemas.items():
            print(f"\n--- Testing {mode.upper()} mode ---")
            
            request = ToolRequest(
                tool_id="T23A_SPACY_NER",
                operation="extract",
                input_data={
                    "text": test_text,
                    "chunk_ref": f"test_chunk_{mode}",
                    "schema": schema
                },
                parameters={}
            )
            
            result = ner_tool.execute(request)
            
            if result.status == "success":
                entities = result.data["entities"]
                results[mode] = len(entities)
                print(f"✓ {mode.capitalize()} mode: {len(entities)} entities extracted")
                
                # Show entity types found
                entity_types = set(e["entity_type"] for e in entities)
                print(f"  Entity types: {', '.join(sorted(entity_types))}")
            else:
                print(f"✗ {mode.capitalize()} mode failed: {result.error_message}")
                results[mode] = 0
        
        print(f"\n--- Results Summary ---")
        for mode, count in results.items():
            print(f"{mode.capitalize()} mode: {count} entities")
            
    except Exception as e:
        print(f"✗ Schema mode testing failed: {e}")
        return False
    
    return True


def main():
    """Run all schema system tests"""
    print("Schema System Testing Suite")
    print("=" * 50)
    
    tests = [
        test_schema_creation,
        test_builtin_schemas,
        test_schema_manager,
        test_spacy_ner_with_schema,
        test_llm_extractor_with_schema,
        test_schema_validation,
        test_all_schema_modes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All schema system tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())