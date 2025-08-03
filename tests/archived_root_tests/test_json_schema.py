#!/usr/bin/env python3
"""
Test the JSON schema generation from Pydantic models
"""

import json
from src.theory_to_code.structured_extractor import TextSchema, TextProspect, TextOutcome, TextProbability

# Generate and print the JSON schema
schema = TextSchema.model_json_schema()
print("Generated JSON Schema:")
print(json.dumps(schema, indent=2))

# Check if additionalProperties is set correctly
def check_additional_properties(obj, path=""):
    """Recursively check if additionalProperties is set to false"""
    if isinstance(obj, dict):
        # Check current level
        if "properties" in obj and "additionalProperties" not in obj:
            print(f"WARNING: {path} has properties but no additionalProperties")
        
        # Check nested objects
        for key, value in obj.items():
            check_additional_properties(value, f"{path}.{key}" if path else key)

print("\nChecking additionalProperties:")
check_additional_properties(schema)