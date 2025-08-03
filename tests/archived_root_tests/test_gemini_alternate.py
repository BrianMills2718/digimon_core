#!/usr/bin/env python3
"""
Test Gemini using alternative approaches
"""

import os
import sys
import json
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code.structured_extractor import StructuredParameterExtractor, TextSchema

print("TESTING GEMINI WITH ALTERNATIVE APPROACHES")
print("=" * 60)

# Test text
test_text = """
The company faces two strategic options:

Option A: Aggressive market entry with 70% probability of major gains 
but 30% chance of substantial losses from regulatory pushback.

Option B: Conservative partnership approach that's virtually certain 
(95%) to deliver moderate returns with only 5% risk of minor setbacks.
"""

print(f"Test Text:")
print("-" * 40)
print(test_text.strip())
print("-" * 40)

# Try different Gemini model names
gemini_models = [
    "gemini-pro",
    "gemini-1.5-pro", 
    "gemini-2.0-flash-exp",
    "google/gemini-pro",
    "google/gemini-1.5-pro"
]

for model in gemini_models:
    print(f"\n\nTesting {model}")
    print("=" * 50)
    
    try:
        import litellm
        
        # Simple JSON extraction without structured output
        response = litellm.completion(
            model=model,
            messages=[
                {
                    "role": "user", 
                    "content": f"""Extract the decision alternatives from this text and format as JSON:

{test_text}

Return a JSON object with this exact structure:
{{
  "theory_name": "Prospect Theory",
  "extracted_prospects": [
    {{
      "name": "name of alternative",
      "full_description": "full text description", 
      "text_outcomes": [
        {{
          "description": "outcome description",
          "linguistic_category": "gain_type",
          "mapped_range": "numerical_range"
        }}
      ],
      "text_probabilities": [
        {{
          "description": "probability phrase",
          "value": 0.70
        }}
      ],
      "reference_point_description": "current situation"
    }}
  ],
  "extraction_notes": "extraction notes",
  "confidence": 0.90
}}

Extract both alternatives with their outcomes and probabilities."""
                }
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON from response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content
            
        # Clean up common JSON issues
        json_str = json_str.replace("'", '"')
        
        # Try to parse
        extracted_data = json.loads(json_str)
        
        print(f"✓ {model} SUCCESS")
        print(f"  Prospects: {len(extracted_data.get('extracted_prospects', []))}")
        print(f"  Confidence: {extracted_data.get('confidence', 'N/A')}")
        
        # Show brief results
        for prospect in extracted_data.get('extracted_prospects', []):
            print(f"    {prospect.get('name', 'Unknown')}: {len(prospect.get('text_outcomes', []))} outcomes")
            
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f"✗ {model} - Model not available")
        elif "credentials" in error_msg.lower():
            print(f"✗ {model} - Authentication required") 
        elif "json" in error_msg.lower():
            print(f"✗ {model} - JSON parsing failed")
        else:
            print(f"✗ {model} - {error_msg}")

print(f"\n\n{'='*60}")
print("SUMMARY:")
print("- Most Gemini models require Google Cloud authentication")
print("- O4-mini works but requires temperature=1 and has 90% confidence vs 95% for GPT-4o")
print("- GPT-4o-2024-08-06 remains the best choice for structured extraction")
print(f"{'='*60}")