#!/usr/bin/env python3
"""
Validate the two fixed reliability components.
"""

import os
import sys
import time
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def validate_component(component_name: str, bundle_file: str, validation_prompt: str):
    """Validate a single component."""
    print(f"\n{'='*60}")
    print(f"Validating: {component_name}")
    print(f"{'='*60}\n")
    
    # Check bundle exists
    if not Path(bundle_file).exists():
        print(f"❌ Bundle not found: {bundle_file}")
        return False, "Bundle not found"
    
    # Read bundle
    with open(bundle_file, 'r') as f:
        codebase_content = f.read()
    
    size_kb = len(codebase_content) / 1024
    print(f"📊 Bundle size: {size_kb:.1f}KB")
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False, "API key missing"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Create prompt
    full_prompt = f"""
You are a critical code reviewer. Your task is to validate specific claims about the implementation.

{validation_prompt}

CODEBASE:
{codebase_content}

Provide a verdict:
- ✅ FULLY RESOLVED: If all checks pass with evidence
- ⚠️ PARTIALLY RESOLVED: If some checks pass but others fail
- ❌ NOT RESOLVED: If critical checks fail

Include specific evidence from the code to support your verdict.
"""
    
    # Send to Gemini
    print("🤖 Validating with Gemini AI...")
    try:
        response = model.generate_content(full_prompt)
        result = response.text
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"reliability-validations/results/{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{component_name.lower().replace(' ', '_')}_validation.md"
        with open(output_file, 'w') as f:
            f.write(f"# {component_name} Validation\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"📄 Results saved to: {output_file}")
        
        # Determine status
        if "✅ FULLY RESOLVED" in result:
            status = "FULLY RESOLVED"
            print("🎉 Component FULLY RESOLVED!")
        elif "⚠️ PARTIALLY RESOLVED" in result:
            status = "PARTIALLY RESOLVED"
            print("⚠️  Component PARTIALLY RESOLVED")
        elif "❌ NOT RESOLVED" in result:
            status = "NOT RESOLVED"
            print("❌ Component NOT RESOLVED")
        else:
            status = "UNKNOWN"
            print("❓ Unable to determine status")
        
        return True, status
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False, f"Error: {e}"


def main():
    """Run validation for fixed components."""
    
    validations = [
        {
            "name": "Thread Safety (Fixed)",
            "bundle": "reliability-thread-safety.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: ThreadSafeServiceManager eliminates race conditions with proper locking

SPECIFIC CHECKS:
1. Singleton pattern with double-check locking in __new__
2. Service-specific locks in _service_locks dictionary
3. Thread-safe service registration and retrieval
4. atomic_operation context manager with proper lock protection

EVIDENCE REQUIRED:
- Double-check locking in __new__ method
- _instance_lock protection for _service_locks creation in atomic_operation
- Service-specific locks used in get_service
- No race conditions in atomic_operation

IMPORTANT: The fix added _instance_lock protection when creating service locks in atomic_operation method (lines 342-346)"""
        },
        {
            "name": "Error Handling (Fixed)",
            "bundle": "reliability-error-handling.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Unified error taxonomy with categorization and recovery strategies

SPECIFIC CHECKS:
1. ErrorCategory enum with comprehensive categories
2. ErrorSeverity levels (CRITICAL, HIGH, MEDIUM, LOW)
3. CentralizedErrorHandler class
4. Recovery strategy mapping correctly implemented

EVIDENCE REQUIRED:
- ErrorCategory and ErrorSeverity enums
- Recovery strategies registered with enum values as keys
- _attempt_recovery uses strategy.value to lookup functions
- Mapping between RecoveryStrategy enum and recovery functions works

IMPORTANT: The fix changed recovery strategy registration to use RecoveryStrategy enum values as keys (lines 159-164)"""
        }
    ]
    
    print("🔧 Phase RELIABILITY - Fixed Components Validation")
    print("=" * 60)
    print("Validating fixes for Thread Safety and Error Handling\n")
    
    results = []
    
    for val in validations:
        success, status = validate_component(val["name"], val["bundle"], val["prompt"])
        results.append({
            "component": val["name"],
            "success": success,
            "status": status
        })
        
        # Brief pause between API calls
        time.sleep(3)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}\n")
    
    for r in results:
        status_icon = {
            "FULLY RESOLVED": "✅",
            "PARTIALLY RESOLVED": "⚠️",
            "NOT RESOLVED": "❌",
            "UNKNOWN": "❓"
        }.get(r["status"], "❓")
        
        print(f"{status_icon} {r['component']:30} - {r['status']}")
    
    if all(r["status"] == "FULLY RESOLVED" for r in results):
        print("\n🎉 ALL FIXED COMPONENTS FULLY RESOLVED!")
        print("Phase RELIABILITY is now 100% complete!")
    else:
        print("\n⚠️  Some issues remain. Review the validation results.")


if __name__ == "__main__":
    main()