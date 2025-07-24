#!/usr/bin/env python3
"""
Direct Gemini validation without using gemini_review.py
"""

import google.generativeai as genai
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Read the bundle
with open('critical-components.xml', 'r') as f:
    bundle_content = f.read()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

prompt = """
You are a critical code reviewer. Validate that the 3 most critical Phase RELIABILITY components are fully implemented.

VALIDATION OBJECTIVE: Verify these critical components have no stubs and meet all requirements.

SPECIFIC VALIDATION CRITERIA:

1. **Distributed Transaction Manager** (distributed_transaction_manager.py):
   - CHECK: Two-phase commit protocol fully implemented
   - CHECK: TransactionState enum with states: PREPARING, PREPARED, COMMITTING, COMMITTED, ROLLING_BACK, ROLLED_BACK
   - CHECK: All methods present: begin_transaction, prepare_neo4j, prepare_sqlite, commit_all, rollback_all
   - CHECK: Proper rollback on any failure in prepare or commit phases
   - EVIDENCE: Look for actual transaction logic, not stubs

2. **Thread Safe Service Manager** (thread_safe_service_manager.py):
   - CHECK: Double-check locking pattern in __new__ method for singleton
   - CHECK: atomic_operation method has _instance_lock protection when creating service locks (around lines 342-346)
   - CHECK: _service_locks dictionary for service-specific locks
   - CHECK: No race conditions in service creation or atomic operations
   - EVIDENCE: Look for proper lock usage throughout

3. **Error Taxonomy** (error_taxonomy.py):
   - CHECK: ErrorCategory enum with at least 8 categories including DATA_CORRUPTION, NETWORK_FAILURE, etc.
   - CHECK: ErrorSeverity enum with LOW, MEDIUM, HIGH, CRITICAL levels
   - CHECK: CentralizedErrorHandler class fully implemented
   - CHECK: Recovery strategies registered using RecoveryStrategy enum values as keys (around lines 159-164)
   - CHECK: _attempt_recovery method uses strategy.value to lookup recovery functions
   - EVIDENCE: Verify the recovery strategy mapping works correctly

CODEBASE:
""" + bundle_content + """

For each component, provide verdict:
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
    output_file = f"phase_reliability_validation_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Phase RELIABILITY Critical Components Validation\n")
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