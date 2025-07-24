#!/usr/bin/env python3
"""
Direct Gemini validation for Entity ID Mapping
"""

import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Read the bundle
with open('entity_id_mapping.xml', 'r') as f:
    bundle_content = f.read()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

prompt = """Validate Entity ID Manager implementation:
  
REQUIREMENTS:
1. Bidirectional ID mapping between Neo4j and SQLite
2. Collision detection before ID assignment
3. Thread-safe concurrent ID generation
4. Proper error handling for ID conflicts

FOCUS: ID generation, mapping storage, and consistency checks

EVIDENCE: Show specific code for mapping methods and thread safety

CODEBASE:
""" + bundle_content + """

For each requirement, provide verdict:
- ✅ FULLY RESOLVED: Implementation complete and meets all requirements
- ⚠️ PARTIALLY RESOLVED: Implementation present but incomplete  
- ❌ NOT RESOLVED: Implementation missing or doesn't meet requirements

IMPORTANT: The codebase is included above. Please analyze it thoroughly."""

print("🤖 Sending to Gemini for validation...")
print(f"📊 Bundle size: {len(bundle_content) / 1024:.1f}KB")

try:
    response = model.generate_content(prompt)
    result = response.text
    
    # Save result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"entity_id_mapping_validation_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Entity ID Mapping Validation\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Tool: Direct Gemini Validation\n\n")
        f.write("---\n\n")
        f.write(result)
    
    print(f"\n✅ Validation complete!")
    print(f"📄 Results saved to: {output_file}")
    
    # Print result
    print("\n" + "="*60)
    print("VALIDATION RESULT")
    print("="*60)
    print(result)
    
except Exception as e:
    print(f"❌ Validation failed: {e}")
