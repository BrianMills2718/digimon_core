#!/usr/bin/env python3
"""Simple test of enhanced services without full pipeline"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path

# Load environment variables
load_dotenv()

# Test enhanced identity service
print("Testing Enhanced Identity Service...\n")

from src.core.enhanced_identity_service import EnhancedIdentityService

service = EnhancedIdentityService()

# Test basic entity resolution
test_entities = [
    ("MIT", "ORG"),
    ("Massachusetts Institute of Technology", "ORG"),
    ("M.I.T.", "ORG")
]

print("Creating entities:")
results = []
for name, entity_type in test_entities:
    result = service.find_or_create_entity(name, entity_type)
    results.append(result)
    print(f"  {name} → {result['entity_id']} (matched: {result['matched']})")

# Check if they resolved to same entity
unique_ids = set(r['entity_id'] for r in results)
print(f"\nUnique entities created: {len(unique_ids)}")

# Test LLM extractor
print("\n\nTesting LLM Entity Extractor...\n")

from src.tools.phase1.t23c_llm_entity_extractor import LLMEntityExtractor
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService

provenance = ProvenanceService()
quality = QualityService()

extractor = LLMEntityExtractor(
    identity_service=service,
    provenance_service=provenance,
    quality_service=quality,
    use_enhanced_identity=True
)

test_text = """
Dr. Sarah Johnson from MIT announced a breakthrough. 
The Massachusetts Institute of Technology is leading quantum research.
"""

print(f"Extracting from text: {test_text[:50]}...")

result = extractor.extract_entities_and_relationships(test_text)

if result["status"] == "success":
    print(f"\n✅ Extraction successful!")
    print(f"Entities: {result['entity_count']}")
    print(f"Relationships: {result['relationship_count']}")
    
    for entity in result["entities"][:5]:
        print(f"\n  • {entity['text']} ({entity['entity_type']})")
        print(f"    Canonical: {entity['canonical_name']}")
        if entity.get('identity_matched'):
            print(f"    Matched existing entity!")
else:
    print(f"\n❌ Extraction failed: {result.get('error')}")

# Show final statistics
stats = service.get_statistics()
print(f"\n\nFinal Statistics:")
print(f"Total unique entities: {stats['total_entities']}")
print(f"Total surface forms: {stats['total_surface_forms']}")
print(f"Entities with aliases: {stats['entities_with_aliases']}")