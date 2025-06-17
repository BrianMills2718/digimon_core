#!/usr/bin/env python
"""Test LLM extraction directly without full infrastructure."""

import os
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

from openai import OpenAI

print("=== DIRECT LLM EXTRACTION TEST ===\n")

# Test text
text = "Microsoft invested $10 billion in OpenAI in 2023. Sam Altman is the CEO of OpenAI."

# Create prompt
prompt = f"""Extract all entities and relationships from the following text. 

Text: "{text}"

Return a JSON object with:
1. "entities": List of entities with name, type (PERSON, ORG, GPE, DATE, MONEY, PRODUCT)
2. "relationships": List of relationships between entities

Example format:
{{
  "entities": [
    {{"name": "Elon Musk", "type": "PERSON"}},
    {{"name": "Tesla", "type": "ORG"}}
  ],
  "relationships": [
    {{"source": "Elon Musk", "target": "Tesla", "type": "FOUNDED", "confidence": 0.9}}
  ]
}}

Relationship types: FOUNDED, WORKS_AT, ACQUIRED, INVESTED_IN, PARTNERS_WITH, COMPETES_WITH, LOCATED_IN, MANUFACTURES, OWNS

Only extract relationships that are explicitly stated or strongly implied.
DO NOT create CO_OCCURS_WITH relationships.
"""

# Call OpenAI
print("Calling OpenAI API...")
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an expert at extracting entities and relationships from text. Return only valid JSON."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    response_format={"type": "json_object"}
)

# Parse result
result = json.loads(response.choices[0].message.content)
print("\n✓ Extraction complete!")
print(f"\nEntities ({len(result.get('entities', []))}):")
for e in result.get('entities', []):
    print(f"  - {e['name']} ({e['type']})")

print(f"\nRelationships ({len(result.get('relationships', []))}):")
for r in result.get('relationships', []):
    print(f"  - {r['source']} --[{r['type']}]--> {r['target']} (conf: {r.get('confidence', 'N/A')})")

# Check for CO_OCCURS_WITH
co_occurs_count = sum(1 for r in result.get('relationships', []) if r['type'] == 'CO_OCCURS_WITH')
print(f"\nCO_OCCURS_WITH relationships: {co_occurs_count}")

print("\n✅ Direct LLM test complete!")