#!/usr/bin/env python3
"""Direct Gemini validation for Claim 2: Performance Tracker"""

import os
import sys
import time
from pathlib import Path

# Check for required dependencies
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai", "python-dotenv"])
    import google.generativeai as genai
    from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment")
    sys.exit(1)

genai.configure(api_key=api_key)

# Wait for rate limit
print("Waiting 30 seconds for rate limit...")
time.sleep(30)

# Read our focused repomix file
repomix_file = Path("claim2-repomix.xml")
if not repomix_file.exists():
    print(f"ERROR: {repomix_file} not found")
    sys.exit(1)

print(f"Reading {repomix_file} ({repomix_file.stat().st_size / 1024:.1f}KB)...")
with open(repomix_file, 'r') as f:
    repomix_content = f.read()

# Create the prompt
prompt = f"""
Validate this specific claim about performance tracking implementation.

CODEBASE:
{repomix_content}

CLAIM: Performance tracking captures all operation timings with baseline establishment

SPECIFIC CHECKS:
1. PerformanceTracker class is fully implemented (not a stub/placeholder)
2. Automatic baseline calculation after configurable samples (default 100)
3. Degradation detection when performance exceeds thresholds
4. Persistent storage of baselines to JSON file
5. Time operation decorator for easy integration
6. Rolling window metrics with configurable size (default 1000)

Please examine the provided code and check each requirement.

VERDICT:
- ✅ FULLY RESOLVED if all requirements are met with evidence
- ⚠️ PARTIALLY RESOLVED if some requirements are met (list which are missing)
- ❌ NOT RESOLVED if implementation is missing

Provide specific line numbers and code snippets as evidence for your verdict.
"""

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    print("\nSending to Gemini for validation...")
    response = model.generate_content(prompt)
    
    print("\n" + "="*80)
    print("GEMINI VALIDATION RESPONSE:")
    print("="*80)
    print(response.text)
    
    # Save the response
    output_file = Path("gemini_validation_claim2.md")
    with open(output_file, 'w') as f:
        f.write(f"# Gemini Validation - Claim 2: Performance Tracker\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Response:\n\n")
        f.write(response.text)
    
    print(f"\n✅ Response saved to: {output_file}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)