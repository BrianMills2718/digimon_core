#!/usr/bin/env python3
"""
Test Gemini 2.5 Flash via Google AI Studio
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.theory_to_code.structured_extractor import TextSchema
import litellm

print("TESTING GEMINI 2.5 FLASH VIA GOOGLE AI STUDIO")
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

# Try different ways to access Gemini 2.5 Flash via Google AI Studio
gemini_2_5_variants = [
    "gemini/gemini-2.5-flash",
    "gemini-2.5-flash", 
]

results = {}
successful_model = None

for model_name in gemini_2_5_variants:
    print(f"\n\nTesting {model_name}")
    print("=" * 50)
    
    try:
        start_time = time.time()
        
        # Try structured output (if supported)
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
        
        extraction_time = time.time() - start_time
        
        # Parse structured response
        extracted_json = json.loads(response.choices[0].message.content)
        text_schema = TextSchema(**extracted_json)
        
        print(f"✅ SUCCESS with Structured Output!")
        print(f"  Time: {extraction_time:.2f}s")
        print(f"  Confidence: {text_schema.confidence:.0%}")
        print(f"  Prospects: {len(text_schema.extracted_prospects)}")
        
        for i, prospect in enumerate(text_schema.extracted_prospects, 1):
            outcomes = len(prospect.text_outcomes)
            probs = len(prospect.text_probabilities)
            print(f"    {i}. {prospect.name}: {outcomes} outcomes, {probs} probs")
        
        # Test parameter resolution
        from src.theory_to_code.structured_extractor import StructuredParameterExtractor
        extractor = StructuredParameterExtractor()
        resolved_params = extractor.resolve_parameters(text_schema)
        
        print(f"  Resolved Parameters:")
        for params in resolved_params:
            print(f"    {params.prospect_name}: {params.outcomes} @ {params.probabilities}")
        
        results[model_name] = {
            "success": True,
            "method": "Structured Output",
            "extraction_time": extraction_time,
            "confidence": text_schema.confidence,
            "prospects": len(text_schema.extracted_prospects)
        }
        
        successful_model = model_name
        break  # Found working model
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a specific error type
        if "model not found" in error_msg.lower() or "not available" in error_msg.lower():
            print(f"✗ Model not available: {model_name}")
        elif "structured output" in error_msg.lower() or "response_format" in error_msg.lower():
            print(f"⚠️ Structured output not supported, trying JSON mode...")
            
            # Fallback to JSON mode
            try:
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
                
                extraction_time = time.time() - start_time
                
                # Parse JSON response
                content = response.choices[0].message.content.strip()
                
                # Clean up markdown formatting
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                extracted_json = json.loads(content)
                text_schema = TextSchema(**extracted_json)
                
                print(f"✅ SUCCESS with JSON Mode!")
                print(f"  Time: {extraction_time:.2f}s")
                print(f"  Confidence: {text_schema.confidence:.0%}")
                print(f"  Prospects: {len(text_schema.extracted_prospects)}")
                
                results[model_name] = {
                    "success": True,
                    "method": "JSON Mode",
                    "extraction_time": extraction_time,
                    "confidence": text_schema.confidence,
                    "prospects": len(text_schema.extracted_prospects)
                }
                
                successful_model = model_name
                break
                
            except Exception as json_error:
                print(f"✗ JSON mode also failed: {json_error}")
        else:
            print(f"✗ FAILED: {e}")

# Compare with current champion if we found a working model
if successful_model:
    print(f"\n\n🎉 GEMINI 2.5 FLASH WORKS!")
    print("=" * 60)
    
    # Compare with GPT-4o
    try:
        print("Comparing with GPT-4o-2024-08-06...")
        
        start_time = time.time()
        from src.theory_to_code.structured_extractor import StructuredParameterExtractor
        baseline_extractor = StructuredParameterExtractor(model="gpt-4o-2024-08-06")
        baseline_schema = baseline_extractor.extract_text_schema(test_text, theory_schema)
        baseline_time = time.time() - start_time
        
        result = results[successful_model]
        
        print(f"\nPERFORMANCE COMPARISON:")
        print(f"  GPT-4o:           {baseline_time:.2f}s, {baseline_schema.confidence:.0%} confidence")
        print(f"  Gemini 2.5 Flash: {result['extraction_time']:.2f}s, {result['confidence']:.0%} confidence")
        print(f"  Method:           {result['method']}")
        
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
        
        print(f"\n✅ RECOMMENDATION:")
        if time_diff < 1 and conf_diff >= 0:
            print(f"   Gemini 2.5 Flash is a great alternative to GPT-4o!")
        elif time_diff > 3:
            print(f"   Gemini 2.5 Flash works but is significantly slower")
        else:
            print(f"   Gemini 2.5 Flash is viable with minor trade-offs")
            
    except Exception as e:
        print(f"Baseline comparison failed: {e}")
        
else:
    print(f"\n❌ GEMINI 2.5 FLASH NOT AVAILABLE")
    print("The model may not be released yet or may require different access.")

print(f"\n{'='*60}")
print("TESTING COMPLETE")
print(f"{'='*60}")