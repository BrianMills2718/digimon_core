#!/usr/bin/env python3
"""
Test different models for structured parameter extraction
"""

import os
import sys
import json
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code.structured_extractor import StructuredParameterExtractor

print("MODEL COMPARISON FOR PARAMETER EXTRACTION")
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

# Models to test
models_to_test = [
    ("gpt-4o-2024-08-06", "Current model"),
    ("o4-mini", "New OpenAI o4-mini"),
    ("gemini-2.5-flash", "Google Gemini 2.5 Flash")
]

results = {}

print(f"\nTest Text:")
print("-" * 40)
print(test_text.strip())
print("-" * 40)

for model_name, description in models_to_test:
    print(f"\n\nTesting {model_name} ({description})")
    print("=" * 50)
    
    try:
        # Create extractor with specific model
        extractor = StructuredParameterExtractor(model=model_name)
        
        # Time the extraction
        start_time = time.time()
        
        # Extract text-schema
        text_schema = extractor.extract_text_schema(test_text, theory_schema)
        
        extraction_time = time.time() - start_time
        
        # Resolve parameters
        resolved_params = extractor.resolve_parameters(text_schema)
        
        # Store results
        results[model_name] = {
            "success": True,
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects_found": len(text_schema.extracted_prospects),
            "text_schema": text_schema.model_dump(),
            "resolved_parameters": [p.model_dump() for p in resolved_params],
            "error": None
        }
        
        # Display results
        print(f"✓ SUCCESS")
        print(f"  Extraction Time: {extraction_time:.2f}s")
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects Found: {len(text_schema.extracted_prospects)}")
        
        for i, prospect in enumerate(text_schema.extracted_prospects):
            print(f"\n  Prospect {i+1}: {prospect.name}")
            print(f"    Outcomes: {len(prospect.text_outcomes)}")
            for outcome in prospect.text_outcomes:
                print(f"      - {outcome.description}")
                print(f"        Category: {outcome.linguistic_category}")
                print(f"        Range: {outcome.mapped_range}")
            print(f"    Probabilities: {len(prospect.text_probabilities)}")
            for prob in prospect.text_probabilities:
                print(f"      - {prob.description}: {prob.value}")
        
        print(f"\n  Resolved Parameters:")
        for params in resolved_params:
            print(f"    {params.prospect_name}:")
            print(f"      Outcomes: {params.outcomes}")
            print(f"      Probabilities: {params.probabilities}")
        
    except Exception as e:
        # Store error
        results[model_name] = {
            "success": False,
            "extraction_time": None,
            "confidence": None,
            "prospects_found": 0,
            "text_schema": None,
            "resolved_parameters": None,
            "error": str(e)
        }
        
        print(f"✗ FAILED")
        print(f"  Error: {e}")
        
        # Check if it's a model support issue
        if "not found" in str(e).lower() or "invalid" in str(e).lower():
            print(f"  Note: Model may not be available or supported")

# Summary comparison
print(f"\n\nSUMMARY COMPARISON")
print("=" * 60)

print(f"{'Model':<20} {'Success':<8} {'Time':<8} {'Conf':<6} {'Prospects':<10}")
print("-" * 60)

for model_name, description in models_to_test:
    result = results[model_name]
    
    success = "✓" if result["success"] else "✗"
    time_str = f"{result['extraction_time']:.2f}s" if result["extraction_time"] else "N/A"
    conf_str = f"{result['confidence']:.0%}" if result["confidence"] else "N/A"
    prospects = result["prospects_found"]
    
    print(f"{model_name:<20} {success:<8} {time_str:<8} {conf_str:<6} {prospects:<10}")

# Save detailed results
output_file = f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nDetailed results saved to: {output_file}")

# Recommendations
print(f"\nRECOMMENDATIONS")
print("=" * 60)

successful_models = [(name, result) for name, result in results.items() if result["success"]]

if successful_models:
    # Find fastest model
    fastest = min(successful_models, key=lambda x: x[1]["extraction_time"])
    print(f"Fastest: {fastest[0]} ({fastest[1]['extraction_time']:.2f}s)")
    
    # Find most confident
    most_confident = max(successful_models, key=lambda x: x[1]["confidence"])
    print(f"Most Confident: {most_confident[0]} ({most_confident[1]['confidence']:.0%})")
    
    # Find most prospects
    most_prospects = max(successful_models, key=lambda x: x[1]["prospects_found"])
    print(f"Most Prospects Found: {most_prospects[0]} ({most_prospects[1]['prospects_found']} prospects)")
    
else:
    print("No models succeeded. Check API keys and model availability.")

print(f"\n{'='*60}")
print("TESTING COMPLETE")
print(f"{'='*60}")