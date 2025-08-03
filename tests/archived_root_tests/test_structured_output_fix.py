#!/usr/bin/env python3
"""
Test fix for OpenAI structured output
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code.structured_extractor import TextSchema
import litellm

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Generate the proper JSON schema
schema = TextSchema.model_json_schema()

# The issue might be that we need to pass the schema directly, not wrapped
# Let's test different approaches

print("Testing OpenAI Structured Output Fix")
print("=" * 60)

# Test text
test_text = """
Company must choose between:
Option A: 70% chance of major gains, 30% chance of substantial losses.
Option B: 95% chance of moderate returns, 5% chance of minor losses.
"""

# Approach 1: Direct schema
print("\n1. Testing with direct schema:")
try:
    response = litellm.completion(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Extract structured information about decision alternatives."
            },
            {"role": "user", "content": test_text}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "text_schema_extraction",
                "strict": True,
                "schema": schema  # Direct schema
            }
        },
        temperature=0
    )
    print("✓ Success with direct schema!")
    print(json.dumps(json.loads(response.choices[0].message.content), indent=2))
    
except Exception as e:
    print(f"✗ Failed with direct schema: {e}")
    
    # Approach 2: Try with wrapped schema structure
    print("\n2. Testing with different structure:")
    try:
        # Ensure all required fields are at top level
        wrapped_schema = {
            "type": "object",
            "properties": schema["properties"],
            "required": schema["required"],
            "additionalProperties": False
        }
        
        # Include definitions if needed
        if "$defs" in schema:
            wrapped_schema["$defs"] = schema["$defs"]
            
        response = litellm.completion(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system", 
                    "content": "Extract structured information about decision alternatives."
                },
                {"role": "user", "content": test_text}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "text_extraction",
                    "strict": True,
                    "schema": wrapped_schema
                }
            },
            temperature=0
        )
        print("✓ Success with wrapped schema!")
        
    except Exception as e2:
        print(f"✗ Failed with wrapped schema: {e2}")
        
        # Approach 3: Minimal test
        print("\n3. Testing with minimal schema:")
        minimal_schema = {
            "type": "object",
            "properties": {
                "test": {"type": "string"}
            },
            "required": ["test"],
            "additionalProperties": False
        }
        
        try:
            response = litellm.completion(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "user", "content": "Say hello"}
                ],
                response_format={
                    "type": "json_schema", 
                    "json_schema": {
                        "name": "test_schema",
                        "strict": True,
                        "schema": minimal_schema
                    }
                }
            )
            print("✓ Minimal schema works!")
            print("Issue is with our complex schema structure")
            
        except Exception as e3:
            print(f"✗ Even minimal schema failed: {e3}")
            print("This might be an API or litellm issue")