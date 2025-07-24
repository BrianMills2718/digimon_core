#!/usr/bin/env python3
"""
Direct Gemini validation for Connection Pool
"""

import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Read the bundle
with open('connection_pool.xml', 'r') as f:
    bundle_content = f.read()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

prompt = """Validate Connection Pool Manager:

REQUIREMENTS:
1. Dynamic pool sizing between min and max limits
2. Automatic health checks removing unhealthy connections
3. Graceful exhaustion handling with request queuing
4. Timeout support for connection acquisition
5. Proper connection lifecycle (acquire/release)

FOCUS: Pool management logic, health checking, and exhaustion handling

EVIDENCE: Show pool sizing, health check, and queue mechanisms

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
    output_file = f"connection_pool_validation_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Connection Pool Validation\n")
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
