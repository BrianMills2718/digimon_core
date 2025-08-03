#!/usr/bin/env python3
"""
Test Gemini models with Google API key
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

print("TESTING GEMINI WITH GOOGLE API KEY")
print("=" * 60)

# Check if API key is loaded
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    print(f"✓ Google API Key found: {google_api_key[:10]}...")
else:
    print("✗ No Google API Key found in environment")
    sys.exit(1)

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

# Test different Gemini model names and approaches
gemini_tests = [
    ("gemini/gemini-1.5-pro", "Google AI Studio Gemini 1.5 Pro"),
    ("gemini/gemini-1.5-flash", "Google AI Studio Gemini 1.5 Flash"),
    ("gemini/gemini-2.0-flash-exp", "Google AI Studio Gemini 2.0 Flash"),
    ("gemini-1.5-pro", "Direct Gemini 1.5 Pro"),
    ("gemini-2.0-flash-exp", "Direct Gemini 2.0 Flash")
]

results = {}

for model_name, description in gemini_tests:
    print(f"\n\nTesting {model_name} ({description})")
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
        
        # Store results
        results[model_name] = {
            "success": True,
            "method": method_used,
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects_found": len(text_schema.extracted_prospects),
            "resolved_parameters": len(resolved_params),
            "error": None
        }
        
        print(f"✓ SUCCESS ({method_used})")
        print(f"  Extraction Time: {extraction_time:.2f}s")
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects Found: {len(text_schema.extracted_prospects)}")
        
        for i, prospect in enumerate(text_schema.extracted_prospects):
            print(f"    {i+1}. {prospect.name}")
            print(f"       Outcomes: {len(prospect.text_outcomes)}")
            print(f"       Probabilities: {len(prospect.text_probabilities)}")
        
        print(f"  Resolved Parameters:")
        for params in resolved_params:
            print(f"    {params.prospect_name}: {params.outcomes} @ {params.probabilities}")
        
    except Exception as e:
        results[model_name] = {
            "success": False,
            "method": None,
            "extraction_time": None,
            "confidence": None,
            "prospects_found": 0,
            "resolved_parameters": 0,
            "error": str(e)
        }
        
        print(f"✗ FAILED: {e}")

# Compare with baselines
print(f"\n\nCOMPARISON WITH BASELINES")
print("=" * 60)

baselines = [
    ("gpt-4o-2024-08-06", "GPT-4o Baseline"),
    ("o4-mini", "O4-mini")
]

for model, desc in baselines:
    try:
        start_time = time.time()
        
        if model == "o4-mini":
            # Use temperature=1 for o4-mini
            from src.theory_to_code.o4_mini_extractor import O4MiniExtractor
            extractor = O4MiniExtractor()
        else:
            extractor = StructuredParameterExtractor(model=model)
        
        text_schema = extractor.extract_text_schema(test_text, theory_schema)
        extraction_time = time.time() - start_time
        
        results[model] = {
            "success": True,
            "method": "Structured Output",
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects_found": len(text_schema.extracted_prospects),
            "resolved_parameters": len(extractor.resolve_parameters(text_schema)),
            "error": None
        }
        
        print(f"✓ {desc}: {text_schema.confidence:.0%} confidence in {extraction_time:.2f}s")
        
    except Exception as e:
        print(f"✗ {desc}: {e}")

# Summary table
print(f"\n\nSUMMARY COMPARISON")
print("=" * 80)
print(f"{'Model':<25} {'Success':<8} {'Method':<15} {'Time':<8} {'Conf':<6} {'Prospects':<10}")
print("-" * 80)

for model, result in results.items():
    success = "✓" if result["success"] else "✗"
    method = result["method"] or "N/A"
    time_str = f"{result['extraction_time']:.2f}s" if result["extraction_time"] else "N/A"
    conf_str = f"{result['confidence']:.0%}" if result["confidence"] else "N/A"
    prospects = result["prospects_found"]
    
    print(f"{model:<25} {success:<8} {method:<15} {time_str:<8} {conf_str:<6} {prospects:<10}")

# Save results
output_file = f"gemini_comparison_{int(time.time())}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nDetailed results saved to: {output_file}")

# Recommendations
successful_gemini = [(name, result) for name, result in results.items() 
                    if result["success"] and "gemini" in name.lower()]

if successful_gemini:
    print(f"\n\nRECOMMENDATIONS")
    print("=" * 60)
    
    # Find best Gemini model
    best_gemini = min(successful_gemini, key=lambda x: x[1]["extraction_time"])
    print(f"Fastest Gemini: {best_gemini[0]} ({best_gemini[1]['extraction_time']:.2f}s)")
    
    most_confident_gemini = max(successful_gemini, key=lambda x: x[1]["confidence"])
    print(f"Most Confident Gemini: {most_confident_gemini[0]} ({most_confident_gemini[1]['confidence']:.0%})")
    
else:
    print("\n❌ No Gemini models succeeded")

print(f"\n{'='*80}")
print("TESTING COMPLETE")
print(f"{'='*80}")