#!/usr/bin/env python3
"""
Test the new Gemini 2.5 Flash that came out today
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.theory_to_code.structured_extractor import StructuredParameterExtractor, TextSchema
import litellm

print("TESTING GEMINI 2.5 FLASH (NEW MODEL)")
print("=" * 60)

# Check API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("✗ No Google API Key found")
    sys.exit(1)

print(f"✓ Google API Key found: {google_api_key[:10]}...")

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

print(f"\nTest Text:")
print("-" * 40)
print(test_text.strip())
print("-" * 40)

# Test different ways to call Gemini 2.5 Flash
gemini_2_5_variants = [
    "gemini-2.5-flash",
    "gemini/gemini-2.5-flash", 
    "google/gemini-2.5-flash",
    "gemini-2.5-flash-exp",
    "gemini/gemini-2.5-flash-exp"
]

results = {}

for model_name in gemini_2_5_variants:
    print(f"\n\nTesting {model_name}")
    print("=" * 50)
    
    try:
        start_time = time.time()
        
        # Method 1: Try structured output first
        try:
            schema = TextSchema.model_json_schema()
            
            response = litellm.completion(
                model=model_name,
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
4. Note how the reference point is described"""}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "text_schema_extraction",
                        "strict": True,
                        "schema": schema
                    }
                },
                api_key=google_api_key,
                temperature=0.2
            )
            
            # Parse structured response
            extracted_json = json.loads(response.choices[0].message.content)
            text_schema = TextSchema(**extracted_json)
            method_used = "Structured Output"
            
        except Exception as struct_error:
            print(f"  Structured output failed: {struct_error}")
            print("  Trying JSON mode...")
            
            # Method 2: Fallback to JSON mode
            response = litellm.completion(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Extract decision alternatives from this text and return as valid JSON:

{test_text}

Return JSON with this exact structure:
{{
  "theory_name": "Prospect Theory",
  "extracted_prospects": [
    {{
      "name": "prospect name",
      "full_description": "complete description",
      "text_outcomes": [
        {{
          "description": "outcome description",
          "linguistic_category": "major_gain",
          "mapped_range": "60 to 89"
        }}
      ],
      "text_probabilities": [
        {{
          "description": "probability description", 
          "value": 0.7
        }}
      ],
      "reference_point_description": "current situation"
    }}
  ],
  "extraction_notes": "extraction notes",
  "confidence": 0.90
}}

Map outcomes using these categories:
- major gains → major_gain → "60 to 89"
- substantial losses → major_loss → "-60 to -89"
- moderate returns → moderate_gain → "20 to 59"
- minor setbacks → minor_loss → "-1 to -19"
"""
                    }
                ],
                api_key=google_api_key,
                temperature=0.2
            )
            
            # Parse JSON response
            content = response.choices[0].message.content.strip()
            
            # Clean up markdown formatting
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            extracted_json = json.loads(content)
            text_schema = TextSchema(**extracted_json)
            method_used = "JSON Mode"
        
        extraction_time = time.time() - start_time
        
        # Test parameter resolution
        extractor = StructuredParameterExtractor()
        resolved_params = extractor.resolve_parameters(text_schema)
        
        results[model_name] = {
            "success": True,
            "method": method_used,
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects": len(text_schema.extracted_prospects),
            "resolved_parameters": len(resolved_params)
        }
        
        print(f"✅ SUCCESS ({method_used})")
        print(f"  Time: {extraction_time:.2f}s")
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects: {len(text_schema.extracted_prospects)}")
        
        for i, prospect in enumerate(text_schema.extracted_prospects, 1):
            outcomes = len(prospect.text_outcomes)
            probs = len(prospect.text_probabilities)
            print(f"    {i}. {prospect.name}: {outcomes} outcomes, {probs} probs")
        
        print(f"  Resolved Parameters:")
        for params in resolved_params:
            print(f"    {params.prospect_name}: {params.outcomes} @ {params.probabilities}")
        
        # This is the one that worked, break here
        print(f"\n🎉 FOUND WORKING GEMINI 2.5 FLASH: {model_name}")
        break
        
    except Exception as e:
        results[model_name] = {
            "success": False,
            "error": str(e)
        }
        
        if "not found" in str(e).lower() or "invalid" in str(e).lower():
            print(f"✗ Model not available: {model_name}")
        else:
            print(f"✗ FAILED: {e}")

# Compare with current champion
print(f"\n\nCOMPARISON WITH CURRENT CHAMPION")
print("=" * 60)

try:
    start_time = time.time()
    baseline_extractor = StructuredParameterExtractor(model="gpt-4o-2024-08-06")
    baseline_schema = baseline_extractor.extract_text_schema(test_text, theory_schema)
    baseline_time = time.time() - start_time
    
    print(f"GPT-4o-2024-08-06: {baseline_schema.confidence:.0%} confidence in {baseline_time:.2f}s")
    
    # Find successful Gemini 2.5
    successful_2_5 = [(name, result) for name, result in results.items() if result.get("success")]
    
    if successful_2_5:
        best_2_5 = successful_2_5[0]  # First successful one
        model_name, result = best_2_5
        
        print(f"\nCOMPARISON:")
        print(f"  GPT-4o:       {baseline_time:.2f}s, {baseline_schema.confidence:.0%} confidence")
        print(f"  Gemini 2.5:   {result['extraction_time']:.2f}s, {result['confidence']:.0%} confidence")
        
        time_diff = result['extraction_time'] - baseline_time
        if time_diff > 0:
            print(f"  → Gemini 2.5 is {time_diff:.2f}s slower")
        else:
            print(f"  → Gemini 2.5 is {abs(time_diff):.2f}s faster!")
        
        conf_diff = result['confidence'] - baseline_schema.confidence
        if conf_diff > 0:
            print(f"  → Gemini 2.5 is {conf_diff:.0%} more confident")
        elif conf_diff < 0:
            print(f"  → GPT-4o is {abs(conf_diff):.0%} more confident")
        else:
            print(f"  → Same confidence level")
            
    else:
        print("❌ No Gemini 2.5 Flash variants worked")
        
except Exception as e:
    print(f"Baseline test failed: {e}")

print(f"\n{'='*60}")
if any(result.get("success") for result in results.values()):
    print("✅ GEMINI 2.5 FLASH WORKS FOR PARAMETER EXTRACTION!")
else:
    print("❌ GEMINI 2.5 FLASH NOT AVAILABLE YET")
print(f"{'='*60}")