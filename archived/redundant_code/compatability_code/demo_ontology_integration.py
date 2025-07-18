#!/usr/bin/env python3
"""
Demonstration of Master Concept Library Integration

This script demonstrates how the ontology service integrates with the
contract validation system to ensure tools produce semantically valid outputs.
"""

from pathlib import Path

# Add src to path for imports

from src.ontology_library.ontology_service import OntologyService
from src.core.ontology_validator import OntologyValidator
from src.core.data_models import Entity, Relationship
from src.core.contract_validator import ContractValidator
import json


def demonstrate_ontology_service():
    """Demonstrate basic ontology service functionality"""
    print("=" * 80)
    print("MASTER CONCEPT LIBRARY DEMONSTRATION")
    print("=" * 80)
    
    # Initialize the ontology service
    ontology = OntologyService()
    
    # Get statistics
    stats = ontology.get_statistics()
    print("\n📊 Ontology Statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # Search for concepts by indigenous terms
    print("\n🔍 Searching for concepts containing 'influence':")
    influence_concepts = ontology.search_by_indigenous_term("influence")
    for concept in influence_concepts[:3]:  # Show first 3
        print(f"  - {concept.name}: {concept.description}")
    
    # Validate entity types
    print("\n✅ Validating entity types:")
    valid_types = ["IndividualActor", "Institution", "SocialGroup"]
    invalid_types = ["RandomType", "MadeUpEntity"]
    
    for entity_type in valid_types:
        is_valid = ontology.validate_entity_type(entity_type)
        print(f"  - {entity_type}: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    for entity_type in invalid_types:
        is_valid = ontology.validate_entity_type(entity_type)
        print(f"  - {entity_type}: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Get entity template
    print("\n📋 Entity template for 'IndividualActor':")
    template = OntologyValidator().get_entity_template("IndividualActor")
    print(f"  - Typical attributes: {template['typical_attributes']}")
    print(f"  - Applicable properties: {list(template['applicable_properties'].keys())[:5]}...")
    print(f"  - Applicable modifiers: {list(template['applicable_modifiers'].keys())[:5]}...")


def demonstrate_entity_validation():
    """Demonstrate entity validation against ontology"""
    print("\n" + "=" * 80)
    print("ENTITY VALIDATION DEMONSTRATION")
    print("=" * 80)
    
    validator = OntologyValidator()
    
    # Create a valid entity
    valid_entity = Entity(
        canonical_name="John Smith",
        entity_type="IndividualActor",
        confidence=0.9,
        quality_tier="high",
        created_by="demo_script",
        workflow_id="demo_workflow",
        properties={
            "age": 35,
            "source_credibility": 0.8,
            "confidence_level": 0.9
        },
        modifiers={
            "certainty_level": "certain",
            "temporal_phase": "present"
        }
    )
    
    print("\n✅ Validating VALID entity:")
    errors = validator.validate_entity(valid_entity)
    if errors:
        print("  ✗ Validation errors:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✓ Entity is valid!")
    
    # Create an invalid entity
    invalid_entity = Entity(
        canonical_name="Mystery Organization",
        entity_type="UnknownEntityType",  # Invalid type
        confidence=0.7,
        quality_tier="medium",
        created_by="demo_script",
        workflow_id="demo_workflow",
        properties={
            "invalid_property": "value",  # Invalid property
            "age": "not a number"  # Invalid value type
        },
        modifiers={
            "certainty_level": "absolutely_sure"  # Invalid modifier value
        }
    )
    
    print("\n❌ Validating INVALID entity:")
    errors = validator.validate_entity(invalid_entity)
    if errors:
        print("  ✗ Validation errors:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✓ Entity is valid!")


def demonstrate_relationship_validation():
    """Demonstrate relationship validation with domain/range checking"""
    print("\n" + "=" * 80)
    print("RELATIONSHIP VALIDATION DEMONSTRATION")
    print("=" * 80)
    
    validator = OntologyValidator()
    
    # Create source and target entities
    person = Entity(
        canonical_name="Jane Doe",
        entity_type="IndividualActor",
        confidence=0.9,
        quality_tier="high",
        created_by="demo_script",
        workflow_id="demo_workflow"
    )
    
    organization = Entity(
        canonical_name="Acme Corporation",
        entity_type="Institution",
        confidence=0.85,
        quality_tier="high",
        created_by="demo_script",
        workflow_id="demo_workflow"
    )
    
    # Create a valid relationship
    valid_relationship = Relationship(
        source_id=person.id,
        target_id=organization.id,
        relationship_type="BelongsTo",  # Valid: IndividualActor -> Institution
        weight=0.9,
        confidence=0.85,
        quality_tier="high",
        created_by="demo_script",
        workflow_id="demo_workflow",
        properties={
            "tie_strength": "strong",
            "duration": 365  # days
        },
        modifiers={
            "certainty_level": "certain",
            "temporal_phase": "present"
        }
    )
    
    print("\n✅ Validating VALID relationship (IndividualActor -[BelongsTo]-> Institution):")
    errors = validator.validate_relationship(valid_relationship, person, organization)
    if errors:
        print("  ✗ Validation errors:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✓ Relationship is valid!")
    
    # Create an invalid relationship (wrong direction)
    invalid_relationship = Relationship(
        source_id=organization.id,
        target_id=person.id,
        relationship_type="BelongsTo",  # Invalid: Institution -> IndividualActor
        weight=0.9,
        confidence=0.85,
        quality_tier="high",
        created_by="demo_script",
        workflow_id="demo_workflow"
    )
    
    print("\n❌ Validating INVALID relationship (Institution -[BelongsTo]-> IndividualActor):")
    errors = validator.validate_relationship(invalid_relationship, organization, person)
    if errors:
        print("  ✗ Validation errors:")
        for error in errors:
            print(f"    - {error}")
    else:
        print("  ✓ Relationship is valid!")


def demonstrate_contract_integration():
    """Demonstrate how contracts integrate with ontology validation"""
    print("\n" + "=" * 80)
    print("CONTRACT + ONTOLOGY INTEGRATION DEMONSTRATION")
    print("=" * 80)
    
    # Initialize contract validator
    validator = ContractValidator("contracts")
    
    # Load contracts with ontology integration
    print("\n📄 Loading contracts with ontology integration:")
    
    contracts_to_check = [
        ("T23A_SpacyNER", "tool"),
        ("T27_RelationshipExtractor", "tool")
    ]
    
    for contract_id, contract_type in contracts_to_check:
        try:
            contract = validator.load_contract(contract_id, contract_type)
            print(f"\n✓ Loaded {contract_id}:")
            
            # Check for ontology integration
            if "ontology_integration" in contract:
                ontology_config = contract["ontology_integration"]
                print("  Ontology Integration:")
                
                if "entity_type_mapping" in ontology_config:
                    print("    - Entity type mappings:")
                    for spacy_type, onto_type in list(ontology_config["entity_type_mapping"].items())[:3]:
                        print(f"      {spacy_type} → {onto_type}")
                
                if "default_properties" in ontology_config:
                    print("    - Default properties configured")
                
                if "default_modifiers" in ontology_config:
                    print("    - Default modifiers configured")
            
            # Check output validation rules
            output_contract = contract.get("output_contract", {})
            for data_type in output_contract.get("produced_data_types", []):
                if "validation" in data_type:
                    print(f"  Validation rules for {data_type['type']}:")
                    for field, rules in data_type["validation"].items():
                        print(f"    - {field}: {rules.get('constraint', 'unknown')}")
                        
        except Exception as e:
            print(f"\n✗ Error loading {contract_id}: {str(e)}")


def demonstrate_enrichment():
    """Demonstrate entity enrichment with default modifiers"""
    print("\n" + "=" * 80)
    print("ENTITY ENRICHMENT DEMONSTRATION")
    print("=" * 80)
    
    validator = OntologyValidator()
    
    # Create a minimal entity
    minimal_entity = Entity(
        canonical_name="Simple Entity",
        entity_type="IndividualActor",
        confidence=0.8,
        quality_tier="medium",
        created_by="demo_script",
        workflow_id="demo_workflow"
    )
    
    print("\n📝 Original entity modifiers:")
    print(f"  {minimal_entity.modifiers}")
    
    # Enrich with default modifiers
    enriched_entity = validator.enrich_entity(minimal_entity)
    
    print("\n✨ Enriched entity modifiers:")
    for mod_name, mod_value in enriched_entity.modifiers.items():
        print(f"  - {mod_name}: {mod_value}")


def main():
    """Run all demonstrations"""
    try:
        demonstrate_ontology_service()
        demonstrate_entity_validation()
        demonstrate_relationship_validation()
        demonstrate_contract_integration()
        demonstrate_enrichment()
        
        print("\n" + "=" * 80)
        print("✅ MASTER CONCEPT LIBRARY INTEGRATION SUCCESSFUL!")
        print("=" * 80)
        print("\nKey Benefits Demonstrated:")
        print("  1. Standardized entity and relationship types")
        print("  2. Automatic validation against master concepts")
        print("  3. Domain/range constraints for relationships")
        print("  4. Property and modifier validation")
        print("  5. Contract integration for tool validation")
        print("  6. Entity enrichment with defaults")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()