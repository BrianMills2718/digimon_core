#!/usr/bin/env python3
"""Demonstration of full validation pipeline with all tools."""

import json
import time
from pathlib import Path

# Add src to path for imports

from src.adapters.t23a_spacy_ner_adapter import SpacyNERAdapter
from src.adapters.t27_relationship_extractor_adapter import RelationshipExtractorAdapter
from src.core.contract_validator import ContractValidator
from src.ontology_library.ontology_service import OntologyService


def create_sample_chunks():
    """Create sample text chunks for processing."""
    return [
        {
            "chunk_id": "chunk_001",
            "text": "Dr. Jane Smith from Harvard University collaborates with the MIT Research Institute on climate change studies. The National Science Foundation provides funding for their research.",
            "start_position": 0,
            "end_position": 185,
            "chunk_index": 0
        },
        {
            "chunk_id": "chunk_002",
            "text": "The Environmental Protection Agency regulates industrial emissions and monitors compliance. Major corporations like EcoTech Inc. must follow these regulations and report their carbon footprint.",
            "start_position": 186,
            "end_position": 380,
            "chunk_index": 1
        },
        {
            "chunk_id": "chunk_003",
            "text": "Local community groups in Boston organize climate action events. These groups communicate with city officials and influence local environmental policies through grassroots activism.",
            "start_position": 381,
            "end_position": 560,
            "chunk_index": 2
        }
    ]


def run_full_pipeline():
    """Run the complete validation pipeline."""
    print("\n" + "="*80)
    print("FULL VALIDATION PIPELINE DEMONSTRATION")
    print("="*80)
    
    # Initialize services
    print("\n1. Initializing services...")
    ontology_service = OntologyService()
    contract_validator = ContractValidator()
    
    # Show loaded concepts
    print(f"   - Loaded {len(ontology_service.registry.entities)} entity concepts")
    print(f"   - Loaded {len(ontology_service.registry.connections)} relationship concepts")
    print(f"   - Loaded {len(ontology_service.registry.properties)} property concepts")
    print(f"   - Loaded {len(ontology_service.registry.modifiers)} modifier concepts")
    
    # Create sample data
    chunks = create_sample_chunks()
    print(f"\n2. Created {len(chunks)} sample text chunks")
    
    # Step 1: Entity Extraction with T23A_SpacyNER
    print("\n3. Running T23A_SpacyNER (Entity Extraction)...")
    ner_adapter = SpacyNERAdapter()
    
    ner_input = {
        "chunks": chunks,
        "min_confidence": 0.7,
        "entity_types": []  # Extract all types
    }
    
    ner_result = ner_adapter.execute(ner_input)
    
    if ner_result.get("status") == "error":
        print(f"   ERROR: {ner_result['error']}")
        print(f"   Details: {json.dumps(ner_result['error_details'], indent=2)}")
        return
    
    print(f"   - Extracted {len(ner_result['entities'])} entities")
    print(f"   - Execution time: {ner_result['execution_metadata']['execution_time']:.2f}s")
    
    # Show entity validation results
    validation_summary = ner_result['summary'].get('ontology_validation', {})
    print(f"   - Validated: {validation_summary.get('total_validated', 0)} entities")
    print(f"   - Type corrections: {validation_summary.get('type_corrections', 0)}")
    print(f"   - Enriched: {validation_summary.get('enriched_count', 0)}")
    
    # Display extracted entities
    print("\n   Extracted Entities:")
    for entity in ner_result['entities'][:10]:  # Show first 10
        validated = "✓" if entity.get('ontology_validated') else "✗"
        corrected = " (corrected)" if entity.get('type_corrected') else ""
        print(f"   {validated} {entity['text']} [{entity['type']}{corrected}] - confidence: {entity['confidence']:.2f}")
    
    # Step 2: Relationship Extraction with T27_RelationshipExtractor
    print("\n4. Running T27_RelationshipExtractor...")
    rel_adapter = RelationshipExtractorAdapter()
    
    rel_input = {
        "entities": ner_result['entities'],
        "chunks": chunks,
        "extraction_method": "dependency_parsing",
        "min_confidence": 0.6
    }
    
    rel_result = rel_adapter.execute(rel_input)
    
    if rel_result.get("status") == "error":
        print(f"   ERROR: {rel_result['error']}")
        print(f"   Details: {json.dumps(rel_result['error_details'], indent=2)}")
        return
    
    print(f"   - Extracted {len(rel_result['relationships'])} relationships")
    print(f"   - Execution time: {rel_result['execution_metadata']['execution_time']:.2f}s")
    
    # Show relationship validation results
    rel_validation = rel_result['summary'].get('ontology_validation', {})
    print(f"   - Validated: {rel_validation.get('total_validated', 0)} relationships")
    print(f"   - Domain/range violations: {rel_validation.get('domain_range_violations', 0)}")
    print(f"   - Type corrections: {rel_validation.get('type_corrections', 0)}")
    
    # Display extracted relationships
    print("\n   Extracted Relationships:")
    for rel in rel_result['relationships'][:10]:  # Show first 10
        validated = "✓" if rel.get('ontology_validated') else "✗"
        corrected = " (corrected)" if rel.get('type_corrected') else ""
        print(f"   {validated} {rel['source_entity_text']} --[{rel['relationship_type']}{corrected}]--> {rel['target_entity_text']}")
        if rel.get('evidence'):
            print(f"      Evidence: \"{rel['evidence']}\"")
    
    # Step 3: Show complete validation statistics
    print("\n5. Validation Pipeline Summary:")
    print("   " + "-"*60)
    
    total_items = len(ner_result['entities']) + len(rel_result['relationships'])
    total_validated = validation_summary.get('total_validated', 0) + rel_validation.get('total_validated', 0)
    total_corrections = validation_summary.get('type_corrections', 0) + rel_validation.get('type_corrections', 0)
    
    print(f"   Total items processed: {total_items}")
    print(f"   Total validated: {total_validated} ({total_validated/total_items*100:.1f}%)")
    print(f"   Total type corrections: {total_corrections}")
    print(f"   Total execution time: {ner_result['execution_metadata']['execution_time'] + rel_result['execution_metadata']['execution_time']:.2f}s")
    
    # Step 4: Demonstrate contract validation
    print("\n6. Contract Validation Checks:")
    
    # Validate a sample output against contract
    sample_output = {
        "entities": [{"entity_id": "entity_0001", "text": "Test", "type": "IndividualActor", "confidence": 0.9}],
        "summary": {"total_entities": 1, "entity_types": {"IndividualActor": 1}, "chunks_processed": 1, "extraction_method": "spacy_ner"},
        "execution_metadata": {"tool_name": "T23A_SpacyNER", "execution_time": 0.1}
    }
    
    is_valid, errors = contract_validator.validate_output("T23A_SpacyNER", sample_output)
    print(f"   - Sample output validation: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"     Errors: {errors}")
    
    # Step 5: Show available tools with contracts
    print("\n7. Available Tool Contracts:")
    contracts_dir = Path("contracts/tools")
    if contracts_dir.exists():
        for contract_file in sorted(contracts_dir.glob("*.yaml")):
            print(f"   - {contract_file.stem}")
    
    print("\n" + "="*80)
    print("PIPELINE DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


def show_ontology_concepts():
    """Display all available ontology concepts."""
    print("\n" + "="*80)
    print("MASTER CONCEPT LIBRARY")
    print("="*80)
    
    ontology_service = OntologyService()
    
    print("\nENTITY CONCEPTS:")
    for name, concept in ontology_service.registry.entities.items():
        print(f"  - {name}: {concept.description}")
    
    print("\nRELATIONSHIP CONCEPTS (showing first 10):")
    for i, (name, concept) in enumerate(ontology_service.registry.connections.items()):
        if i >= 10:
            print(f"  ... and {len(ontology_service.registry.connections) - 10} more")
            break
        print(f"  - {name}: {concept.description}")
        print(f"    Domain: {', '.join(concept.domain)}")
        print(f"    Range: {', '.join(concept.range)}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Full validation pipeline demonstration")
    parser.add_argument("--show-concepts", action="store_true", help="Show all ontology concepts")
    args = parser.parse_args()
    
    if args.show_concepts:
        show_ontology_concepts()
    else:
        run_full_pipeline()


if __name__ == "__main__":
    main()