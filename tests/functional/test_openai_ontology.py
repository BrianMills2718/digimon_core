#!/usr/bin/env python3
"""
Test OpenAI o3-mini Ontology Generator in isolation.
This verifies the new core component works correctly.
"""

import os
import json
from pathlib import Path

# Add src to path

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator

def test_openai_ontology():
    """Test OpenAI ontology generation with a simple example."""
    print("="*80)
    print("Testing OpenAI o3-mini Ontology Generator")
    print("="*80)
    
    # Initialize the generator
    try:
        generator = GeminiOntologyGenerator()
        print("✅ Successfully initialized OpenAI ontology generator")
        print(f"   Model: {generator.model}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Create a simple test conversation
    messages = [
        {
            "role": "user",
            "content": "I'm working on a research project about scientific publications and their citations. I need to analyze relationships between papers, authors, and institutions."
        },
        {
            "role": "assistant", 
            "content": "I can help you analyze scientific publications. What specific aspects are you interested in - citation networks, collaboration patterns, or impact analysis?"
        },
        {
            "role": "user",
            "content": "I want to track how papers cite each other, which authors collaborate, and which institutions they're affiliated with."
        }
    ]
    
    # Generate ontology
    print("\n📋 Generating ontology from conversation...")
    try:
        ontology = generator.generate_from_conversation(
            messages=messages,
            constraints={
                "max_entities": 5,
                "max_relations": 6,
                "complexity": "medium"
            }
        )
        
        print("\n✅ Successfully generated ontology!")
        print(f"\n🏷️  Domain: {ontology.domain_name}")
        print(f"📝 Description: {ontology.domain_description}")
        
        print(f"\n📊 Entity Types ({len(ontology.entity_types)}):")
        for et in ontology.entity_types:
            print(f"   - {et.name}: {et.description}")
            print(f"     Examples: {', '.join(et.examples[:3])}")
        
        print(f"\n🔗 Relationship Types ({len(ontology.relationship_types)}):")
        for rt in ontology.relationship_types:
            print(f"   - {rt.name}: {rt.description}")
            print(f"     {rt.source_types[0]} → {rt.target_types[0]}")
        
        # Convert to JSON for inspection
        ontology_dict = {
            "domain_name": ontology.domain_name,
            "domain_description": ontology.domain_description,
            "entity_types": [
                {
                    "name": et.name,
                    "description": et.description,
                    "examples": et.examples,
                    "attributes": et.attributes
                }
                for et in ontology.entity_types
            ],
            "relationship_types": [
                {
                    "name": rt.name,
                    "description": rt.description,
                    "source_types": rt.source_types,
                    "target_types": rt.target_types,
                    "examples": rt.examples
                }
                for rt in ontology.relationship_types
            ],
            "extraction_patterns": ontology.extraction_patterns
        }
        
        print("\n📄 Full Ontology JSON:")
        print("="*80)
        print(json.dumps(ontology_dict, indent=2))
        
    except Exception as e:
        print(f"\n❌ Failed to generate ontology: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_ontology()