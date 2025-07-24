#!/usr/bin/env python3
"""Validate Claim 1 with minimal project structure to avoid rate limits"""

import subprocess
import os
import time

# Wait for rate limit reset
print("Waiting 60 seconds for rate limit to fully reset...")
time.sleep(60)

# Run gemini validation on minimal project
print("\nRunning Gemini validation on minimal project (only provenance_manager.py)...")
cmd = [
    "python", "gemini-review-tool/gemini_review.py", 
    "/tmp/validate_claim1",  # Minimal project with only provenance_manager.py
    "--no-cache",
    "--prompt", """Validate this specific claim about audit trail immutability in ProvenanceManager.

CLAIM: Audit trails use cryptographic chaining preventing tampering

SPECIFIC CHECKS:
1. Line 72: AuditEntry class must have @dataclass(frozen=True) decorator
2. Line 83-93: Hash calculation must include previous_hash for chaining  
3. Line 117-132: verify_integrity() method must check chain continuity
4. Line 163: _audit_trails must be typed as Dict[str, ImmutableAuditTrail]

VERDICT:
- ✅ FULLY RESOLVED if all 4 requirements are met
- ⚠️ PARTIALLY RESOLVED if some requirements are met
- ❌ NOT RESOLVED if implementation is missing"""
]

# Run the command
result = subprocess.run(cmd, capture_output=True, text=True)

print("\nSTDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nReturn code: {result.returncode}")

# Check if review was created
review_dirs = [d for d in os.listdir("gemini-review-tool/outputs") if d.startswith("2025")]
if review_dirs:
    latest_dir = max(review_dirs)
    review_file = f"gemini-review-tool/outputs/{latest_dir}/reviews/gemini-review.md"
    if os.path.exists(review_file):
        print(f"\n✅ Review created: {review_file}")
        print("\nReview content:")
        with open(review_file, 'r') as f:
            print(f.read())