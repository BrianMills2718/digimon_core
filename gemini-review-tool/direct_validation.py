#\!/usr/bin/env python3
"""Direct validation using Gemini API with pre-generated repomix."""

import os
import yaml
from pathlib import Path
import google.generativeai as genai

def validate_claim(repomix_file, config_file):
    """Validate a specific claim using Gemini."""
    
    # Read config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Read repomix content
    with open(repomix_file, 'r') as f:
        codebase = f.read()
    
    # Configure Gemini
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Create full prompt
    full_prompt = f"""
{config['custom_prompt']}

CODEBASE:
{codebase}
"""
    
    # Get response
    response = model.generate_content(full_prompt)
    
    return response.text

if __name__ == "__main__":
    print("Validating Audit Trail Immutability...")
    print("="*80)
    
    result = validate_claim("audit-trail-repomix.xml", "validation-audit-trail.yaml")
    print(result)
ENDOFFILE < /dev/null
