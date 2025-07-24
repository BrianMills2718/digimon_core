#!/usr/bin/env python3
"""Run focused validation with pre-generated repomix output."""

import sys
import subprocess
import shutil
from pathlib import Path

def run_validation(repomix_file, config_file):
    """Run validation with specific repomix file."""
    
    # Copy repomix file to expected location
    shutil.copy(repomix_file, "repomix-output.xml")
    
    # Read the config to get the prompt
    import yaml
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Read the repomix content
    with open("repomix-output.xml", 'r') as f:
        codebase = f.read()
    
    # Use the gemini API directly
    import os
    import google.generativeai as genai
    
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Combine prompt with codebase
    full_prompt = f"""
{config['custom_prompt']}

CODEBASE:
{codebase}
"""
    
    # Get response
    response = model.generate_content(full_prompt)
    
    # Save result
    output_dir = Path("outputs/manual_validation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "result.md", 'w') as f:
        f.write(response.text)
    
    return response.text
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Get the latest output
    outputs = sorted(Path("outputs").glob("*/reviews/gemini-review.md"))
    if outputs:
        with open(outputs[-1], 'r') as f:
            content = f.read()
            print("\n" + "="*80)
            print("VALIDATION RESULT:")
            print("="*80)
            print(content)

if __name__ == "__main__":
    # Run audit trail validation
    print("Running Audit Trail Immutability Validation...")
    run_validation("audit-trail-repomix.xml", "validation-audit-trail.yaml")