#!/usr/bin/env python3
"""
Direct validation of reliability components using pre-generated bundles.
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
        return False
    
    # Read bundle
    print(f"📖 Reading bundle: {bundle_file}")
    with open(bundle_file, 'r') as f:
        codebase_content = f.read()
    
    # Check size
    size_kb = len(codebase_content) / 1024
    print(f"📊 Bundle size: {size_kb:.1f}KB")
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
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
    print("🤖 Sending to Gemini for validation...")
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
        
        print(f"✅ Validation complete!")
        print(f"📄 Results saved to: {output_file}")
        
        # Print summary
        if "✅ FULLY RESOLVED" in result:
            print("\n🎉 Component FULLY RESOLVED!")
        elif "⚠️ PARTIALLY RESOLVED" in result:
            print("\n⚠️  Component PARTIALLY RESOLVED - review needed")
        elif "❌ NOT RESOLVED" in result:
            print("\n❌ Component NOT RESOLVED - fixes required")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def main():
    """Run all reliability validations."""
    
    validations = [
        {
            "name": "Distributed Transactions",
            "bundle": "reliability-distributed-tx.xml",
            "prompt": """Validate ONLY this specific claim:

**CLAIM**: Distributed transaction manager implements two-phase commit across Neo4j and SQLite

SPECIFIC CHECKS:
1. TransactionState enum with states: PREPARING, PREPARED, COMMITTING, COMMITTED, ABORTING, ABORTED
2. DistributedTransactionManager class with required methods
3. Two-phase commit protocol in commit_all() method
4. Proper rollback handling in rollback_all() method

EVIDENCE REQUIRED:
- TransactionState enum definition
- Method signatures: begin_transaction, prepare_neo4j, prepare_sqlite, commit_all, rollback_all
- Actual 2PC logic in commit_all
- Error handling that triggers rollback"""
        }
    ]
    
    print("🔧 Phase RELIABILITY Component Validations")
    print("=" * 60)
    
    for val in validations:
        if not validate_component(val["name"], val["bundle"], val["prompt"]):
            print(f"❌ Failed to validate {val['name']}")
            continue
        
        # Brief pause
        time.sleep(2)
    
    print("\n✨ All validations complete!")


if __name__ == "__main__":
    main()