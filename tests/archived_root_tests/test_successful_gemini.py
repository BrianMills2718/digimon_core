#!/usr/bin/env python3
"""
Test only the successful Gemini models
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

print("GEMINI MODEL COMPARISON")
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

# Test working Gemini models via Google AI Studio
working_models = [
    ("gemini/gemini-1.5-pro", "Gemini 1.5 Pro"),
    ("gemini/gemini-1.5-flash", "Gemini 1.5 Flash"),  
    ("gemini/gemini-2.0-flash-exp", "Gemini 2.0 Flash")
]

results = {}

for model_name, description in working_models:
    print(f"\nTesting {description}")
    print("-" * 40)
    
    try:
        start_time = time.time()
        
        # Try structured output first
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
            temperature=0.2
        )
        
        extraction_time = time.time() - start_time
        
        # Parse response
        extracted_json = json.loads(response.choices[0].message.content)
        text_schema = TextSchema(**extracted_json)
        
        # Test parameter resolution
        extractor = StructuredParameterExtractor()
        resolved_params = extractor.resolve_parameters(text_schema)
        
        results[model_name] = {
            "success": True,
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects": len(text_schema.extracted_prospects),
            "description": description
        }
        
        print(f"✓ SUCCESS")
        print(f"  Time: {extraction_time:.2f}s")
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects: {len(text_schema.extracted_prospects)}")
        
        for i, prospect in enumerate(text_schema.extracted_prospects, 1):
            outcomes = len(prospect.text_outcomes)
            probs = len(prospect.text_probabilities)
            print(f"    {i}. {prospect.name}: {outcomes} outcomes, {probs} probs")
        
    except Exception as e:
        results[model_name] = {
            "success": False,
            "error": str(e),
            "description": description
        }
        print(f"✗ FAILED: {e}")

# Add baselines for comparison
print(f"\nTesting Baselines")
print("-" * 40)

baselines = [
    ("gpt-4o-2024-08-06", "GPT-4o"),
    ("o4-mini", "O4-mini")
]

for model, desc in baselines:
    try:
        start_time = time.time()
        
        if model == "o4-mini":
            from src.theory_to_code.o4_mini_extractor import O4MiniExtractor
            extractor = O4MiniExtractor()
        else:
            extractor = StructuredParameterExtractor(model=model)
        
        text_schema = extractor.extract_text_schema(test_text, theory_schema)
        extraction_time = time.time() - start_time
        
        results[model] = {
            "success": True,
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects": len(text_schema.extracted_prospects),
            "description": desc
        }
        
        print(f"✓ {desc}: {text_schema.confidence:.0%} confidence in {extraction_time:.2f}s")
        
    except Exception as e:
        print(f"✗ {desc}: {e}")

print(f"\n\nFINAL COMPARISON")
print("=" * 70)
print(f"{'Model':<25} {'Description':<20} {'Time':<8} {'Conf':<6} {'Prospects':<10}")
print("-" * 70)

for model, result in results.items():
    if result["success"]:
        desc = result["description"]
        time_str = f"{result['extraction_time']:.2f}s"
        conf_str = f"{result['confidence']:.0%}"
        prospects = result["prospects"]
        
        print(f"{model:<25} {desc:<20} {time_str:<8} {conf_str:<6} {prospects:<10}")

# Find winners
successful = [(name, result) for name, result in results.items() if result["success"]]

if successful:
    print(f"\nWINNERS:")
    print("-" * 20)
    
    # Fastest
    fastest = min(successful, key=lambda x: x[1]["extraction_time"])
    print(f"Fastest: {fastest[1]['description']} ({fastest[1]['extraction_time']:.2f}s)")
    
    # Most confident
    most_confident = max(successful, key=lambda x: x[1]["confidence"])
    print(f"Most Confident: {most_confident[1]['description']} ({most_confident[1]['confidence']:.0%})")
    
    # Best Gemini
    gemini_models = [(name, result) for name, result in successful if "gemini" in name]
    if gemini_models:
        best_gemini = min(gemini_models, key=lambda x: x[1]["extraction_time"])
        print(f"Best Gemini: {best_gemini[1]['description']} ({best_gemini[1]['extraction_time']:.2f}s)")

print(f"\n{'='*70}")
print("TESTING COMPLETE")
print(f"{'='*70}")