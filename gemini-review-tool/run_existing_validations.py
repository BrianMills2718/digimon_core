#!/usr/bin/env python3
"""
Run focused validations for existing Phase RELIABILITY components.
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path

def run_validation(name, config_file, include_files):
    """Run a single focused validation."""
    print(f"\n{'='*60}")
    print(f"Running validation: {name}")
    print(f"Config: {config_file}")
    print(f"Files: {include_files}")
    print('='*60)
    
    # Create focused repomix bundle
    bundle_name = f"{name.lower().replace(' ', '_')}.xml"
    cmd = f'npx repomix --include "{include_files}" --output gemini-review-tool/{bundle_name} .'
    
    print(f"\nCreating bundle with: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/home/brian/projects/Digimons")
    
    if result.returncode != 0:
        print(f"❌ Failed to create bundle: {result.stderr}")
        return False
    
    # Check bundle size
    bundle_path = f"/home/brian/projects/Digimons/gemini-review-tool/{bundle_name}"
    if os.path.exists(bundle_path):
        size_kb = os.path.getsize(bundle_path) / 1024
        print(f"✅ Bundle created: {bundle_name} ({size_kb:.1f}KB)")
        
        if size_kb > 50:
            print(f"⚠️ Warning: Bundle size {size_kb:.1f}KB exceeds recommended 50KB")
    
    return True

def create_direct_validation(name, bundle_name, prompt):
    """Create a direct validation script for a component."""
    script_name = f"validate_{name.lower().replace(' ', '_')}.py"
    script_content = f'''#!/usr/bin/env python3
"""
Direct Gemini validation for {name}
"""

import google.generativeai as genai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Read the bundle
with open('{bundle_name}', 'r') as f:
    bundle_content = f.read()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

prompt = """{prompt}

CODEBASE:
""" + bundle_content + """

For each requirement, provide verdict:
- ✅ FULLY RESOLVED: Implementation complete and meets all requirements
- ⚠️ PARTIALLY RESOLVED: Implementation present but incomplete  
- ❌ NOT RESOLVED: Implementation missing or doesn't meet requirements

IMPORTANT: The codebase is included above. Please analyze it thoroughly."""

print("🤖 Sending to Gemini for validation...")
print(f"📊 Bundle size: {{len(bundle_content) / 1024:.1f}}KB")

try:
    response = model.generate_content(prompt)
    result = response.text
    
    # Save result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{name.lower().replace(' ', '_')}_validation_{{timestamp}}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# {name} Validation\\n")
        f.write(f"Generated: {{datetime.now().isoformat()}}\\n")
        f.write(f"Tool: Direct Gemini Validation\\n\\n")
        f.write("---\\n\\n")
        f.write(result)
    
    print(f"\\n✅ Validation complete!")
    print(f"📄 Results saved to: {{output_file}}")
    
    # Print result
    print("\\n" + "="*60)
    print("VALIDATION RESULT")
    print("="*60)
    print(result)
    
except Exception as e:
    print(f"❌ Validation failed: {{e}}")
'''
    
    script_path = f"/home/brian/projects/Digimons/gemini-review-tool/{script_name}"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    print(f"✅ Created validation script: {script_name}")

def main():
    """Run all existing component validations."""
    validations = [
        {
            "name": "Entity ID Mapping",
            "files": "src/core/entity_id_manager.py",
            "prompt": """Validate Entity ID Manager implementation:
  
REQUIREMENTS:
1. Bidirectional ID mapping between Neo4j and SQLite
2. Collision detection before ID assignment
3. Thread-safe concurrent ID generation
4. Proper error handling for ID conflicts

FOCUS: ID generation, mapping storage, and consistency checks

EVIDENCE: Show specific code for mapping methods and thread safety"""
        },
        {
            "name": "Citation Provenance",
            "files": "src/core/provenance_manager.py,src/core/citation_validator.py",
            "prompt": """Validate Citation/Provenance implementation:

REQUIREMENTS:
1. Every citation has verifiable source tracking
2. Full modification history with who/when/why
3. Fabrication detection through source validation
4. Immutable audit trail that cannot be tampered

FOCUS: Citation creation, validation, and audit methods

EVIDENCE: Show source verification and audit trail code"""
        },
        {
            "name": "Connection Pool",
            "files": "src/core/connection_pool_manager.py",
            "prompt": """Validate Connection Pool Manager:

REQUIREMENTS:
1. Dynamic pool sizing between min and max limits
2. Automatic health checks removing unhealthy connections
3. Graceful exhaustion handling with request queuing
4. Timeout support for connection acquisition
5. Proper connection lifecycle (acquire/release)

FOCUS: Pool management logic, health checking, and exhaustion handling

EVIDENCE: Show pool sizing, health check, and queue mechanisms"""
        }
    ]
    
    print(f"Phase RELIABILITY Existing Component Validations")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Total validations: {len(validations)}")
    
    results = []
    for validation in validations:
        # Create bundle
        success = run_validation(
            validation["name"],
            None,  # No config file needed
            validation["files"]
        )
        
        if success:
            # Create validation script
            bundle_name = f"{validation['name'].lower().replace(' ', '_')}.xml"
            create_direct_validation(
                validation["name"],
                bundle_name,
                validation["prompt"]
            )
        
        results.append((validation["name"], success))
    
    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print('='*60)
    
    for name, success in results:
        status = "✅ Ready" if success else "❌ Failed"
        print(f"{status} {name}")
    
    # Next steps
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print('='*60)
    print("1. Run the individual validation scripts:")
    print("   - python validate_entity_id_mapping.py")
    print("   - python validate_citation_provenance.py") 
    print("   - python validate_connection_pool.py")
    print("2. Review validation results")
    print("3. Fix any issues identified")
    print("4. Re-run validations after fixes")
    print("\nNOTE: Performance tracking and SLA monitoring components")
    print("      need to be implemented as they don't exist yet.")

if __name__ == "__main__":
    main()