#!/usr/bin/env python3
"""Demo script to show entity and relationship extraction in action"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.phase1.t23a_spacy_ner import SpacyNER
from tools.phase1.t27_relationship_extractor import RelationshipExtractor
from core.identity_service import IdentityService
from core.provenance_service import ProvenanceService
from core.quality_service import QualityService

# Sample text
sample_text = """
Elon Musk is the CEO of Tesla Inc., an electric vehicle company based in Austin, Texas. 
He also founded SpaceX in 2002, which develops spacecraft and rockets. 
Both Tesla and SpaceX are innovative technology companies pushing the boundaries of their industries.
Apple Inc., founded by Steve Jobs in 1976, is headquartered in Cupertino, California.
Tim Cook currently serves as Apple's CEO.
"""

print("=== Entity and Relationship Extraction Demo ===\n")
print("Sample Text:")
print("-" * 80)
print(sample_text.strip())
print("-" * 80)
print()

# Initialize services
identity = IdentityService()
provenance = ProvenanceService()
quality = QualityService()

# Initialize extractors
ner = SpacyNER(identity, provenance, quality)
rel_extractor = RelationshipExtractor(identity, provenance, quality)

# Extract entities
print("STEP 1: Entity Extraction")
print("=" * 40)

entity_result = ner.extract_entities(
    chunk_ref="demo_chunk_001",
    text=sample_text,
    chunk_confidence=0.9
)

if entity_result["status"] == "success":
    print(f"Found {len(entity_result['entities'])} entities:\n")
    
    for entity in entity_result["entities"]:
        print(f"• {entity['surface_form']:<20} ({entity['entity_type']:<10}) confidence: {entity['confidence']:.2f}")
        print(f"  Position: chars {entity['start_char']}-{entity['end_char']}")
        print()
else:
    print(f"Error: {entity_result.get('error')}")

# Extract relationships
print("\nSTEP 2: Relationship Extraction")
print("=" * 40)

rel_result = rel_extractor.extract_relationships(
    chunk_ref="demo_chunk_001",
    text=sample_text,
    entities=entity_result["entities"],
    chunk_confidence=0.9
)

if rel_result["status"] == "success":
    print(f"Found {len(rel_result['relationships'])} relationships:\n")
    
    for rel in rel_result["relationships"]:
        print(f"• {rel['subject_text']:<15} --[{rel['relationship_type']}]--> {rel['object_text']:<15}")
        print(f"  Confidence: {rel['confidence']:.2f}")
        print(f"  Method: {rel['extraction_method']}")
        if 'evidence_text' in rel:
            print(f"  Evidence: '{rel['evidence_text']}'")
        print()
else:
    print(f"Error: {rel_result.get('error')}")

# Show extraction patterns
print("\nExtraction Methods Explained:")
print("=" * 40)
print("""
1. Pattern-Based: Uses linguistic patterns like "X is CEO of Y" or "X founded Y"
   - Most reliable method (confidence 0.7-0.9)
   - Captures specific relationship types

2. Dependency Parsing: Analyzes grammatical structure (subject-verb-object)
   - Good for simple sentences (confidence 0.6-0.8)
   - Requires clear sentence structure

3. Proximity-Based: Finds entities near each other
   - Fallback method (confidence ~0.5)
   - Creates generic RELATED_TO relationships
""")

# Show confidence calculation
print("\nConfidence Calculation:")
print("=" * 40)
print("""
Entity confidence factors:
- Base spaCy confidence: 0.85
- Type adjustments: MONEY/DATE (0.95), WORK_OF_ART (0.75)
- Length bonus: Longer entities get higher confidence
- Context quality: From source document

Relationship confidence factors:
- Pattern confidence: 40% weight
- Context confidence: 30% weight  
- Entity confidence: 30% weight
- Distance penalty for proximity-based
""")