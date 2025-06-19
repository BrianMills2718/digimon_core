#!/usr/bin/env python
"""Test spaCy loading."""

print("Testing spaCy...")

# Test spaCy
print("1. Loading spaCy model...")
import spacy

nlp = spacy.load("en_core_web_sm")
print("✓ Model loaded")

# Test NER
print("2. Testing NER...")
doc = nlp("Apple Inc. is in Cupertino. Microsoft is in Redmond.")
print(f"✓ Found {len(doc.ents)} entities:")
for ent in doc.ents:
    print(f"  - {ent.text} ({ent.label_})")

print("\n✅ SpaCy test completed!")