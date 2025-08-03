#!/usr/bin/env python3
"""
Test o4-mini with fixed parameters and gemini via Google AI Studio
"""

import os
import sys
import json
import time
import litellm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code.structured_extractor import StructuredParameterExtractor, TextSchema

print("TESTING O4-MINI AND GEMINI WITH FIXES")
print("=" * 60)

# Test text
test_text = """
The company faces two strategic options:

Option A: Aggressive market entry with 70% probability of major gains 
but 30% chance of substantial losses from regulatory pushback.

Option B: Conservative partnership approach that's virtually certain 
(95%) to deliver moderate returns with only 5% risk of minor setbacks.
"""

# Load theory schema
with open("config/schemas/prospect_theory_schema.json", "r") as f:
    theory_schema = json.load(f)

print(f"Test Text:")
print("-" * 40)
print(test_text.strip())
print("-" * 40)

# Test 1: O4-mini with temperature=1 (required for O-series)
print(f"\n\n1. TESTING O4-MINI (with temperature=1)")
print("=" * 50)

try:
    # Manual call with correct parameters for o4-mini
    schema = TextSchema.model_json_schema()
    
    response = litellm.completion(
        model="o4-mini",
        messages=[
            {
                "role": "system",
                "content": "You extract structured information about decision alternatives from text."
            },
            {"role": "user", "content": f"""Extract decision alternatives and their attributes from this text:

{test_text}

Use these linguistic mappings from the theory:
Outcome Mappings: {json.dumps(theory_schema.get('ontology', {}).get('mathematical_algorithms', {}).get('text_to_numbers_conversion', {}).get('outcome_scaling', {}).get('linguistic_mappings', {}), indent=2)}

For each alternative:
1. Identify the name and full description
2. List all outcomes with their linguistic categories
3. Extract exact probabilities
4. Note how the reference point is described (use "current situation" if not explicitly mentioned)"""}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "text_schema_extraction",
                "strict": True,
                "schema": schema
            }
        },
        temperature=1  # Required for O-series models
    )
    
    print("✓ O4-MINI SUCCESS")
    
    # Parse response
    extracted_json = json.loads(response.choices[0].message.content)
    text_schema = TextSchema(**extracted_json)
    
    print(f"  Confidence: {text_schema.confidence:.0%}")
    print(f"  Prospects Found: {len(text_schema.extracted_prospects)}")
    
    for prospect in text_schema.extracted_prospects:
        print(f"    {prospect.name}: {len(prospect.text_outcomes)} outcomes, {len(prospect.text_probabilities)} probabilities")

except Exception as e:
    print(f"✗ O4-MINI FAILED: {e}")

# Test 2: Gemini via Google AI Studio (not Vertex AI)
print(f"\n\n2. TESTING GEMINI-2.0-FLASH-EXP (via Google AI Studio)")
print("=" * 50)

try:
    # Check for Google AI API key
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not google_api_key:
        print("✗ GEMINI FAILED: No GOOGLE_API_KEY or GEMINI_API_KEY found")
    else:
        # Try with regular JSON mode since structured output may not be supported
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured information about decision alternatives from text. Return valid JSON matching the required schema."
                },
                {"role": "user", "content": f"""Extract decision alternatives from this text and return as JSON:

{test_text}

Return JSON with this structure:
{{
  "theory_name": "Prospect Theory",
  "extracted_prospects": [
    {{
      "name": "prospect name",
      "full_description": "complete description",
      "text_outcomes": [
        {{
          "description": "outcome description",
          "linguistic_category": "category from mappings",
          "mapped_range": "range value"
        }}
      ],
      "text_probabilities": [
        {{
          "description": "probability description", 
          "value": 0.7
        }}
      ],
      "reference_point_description": "reference point"
    }}
  ],
  "extraction_notes": "notes",
  "confidence": 0.95
}}

Use these category mappings:
- major gains → major_gain → "60 to 89"
- substantial losses → major_loss → "-60 to -89"  
- moderate returns → moderate_gain → "20 to 59"
- minor setbacks → minor_loss → "-1 to -19"
"""}
            ],
            api_key=google_api_key,
            temperature=0.2
        )
        
        print("✓ GEMINI SUCCESS")
        
        # Parse response
        content = response.choices[0].message.content
        
        # Clean up markdown formatting if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        extracted_json = json.loads(content)
        text_schema = TextSchema(**extracted_json)
        
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects Found: {len(text_schema.extracted_prospects)}")
        
        for prospect in text_schema.extracted_prospects:
            print(f"    {prospect.name}: {len(prospect.text_outcomes)} outcomes, {len(prospect.text_probabilities)} probabilities")

except Exception as e:
    print(f"✗ GEMINI FAILED: {e}")

# Test 3: Compare with baseline
print(f"\n\n3. BASELINE: GPT-4O-2024-08-06")
print("=" * 50)

try:
    extractor = StructuredParameterExtractor(model="gpt-4o-2024-08-06")
    text_schema = extractor.extract_text_schema(test_text, theory_schema)
    
    print("✓ BASELINE SUCCESS")
    print(f"  Confidence: {text_schema.confidence:.0%}")
    print(f"  Prospects Found: {len(text_schema.extracted_prospects)}")

except Exception as e:
    print(f"✗ BASELINE FAILED: {e}")

print(f"\n{'='*60}")
print("CONCLUSION:")
print("- O4-mini requires temperature=1 and may not support structured outputs")
print("- Gemini via Google AI Studio needs GOOGLE_API_KEY environment variable")
print("- GPT-4o-2024-08-06 remains most reliable for structured extraction")
print(f"{'='*60}")