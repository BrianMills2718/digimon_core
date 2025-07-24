#!/usr/bin/env python3
"""Validate Claim 1: Audit Trail Immutability"""

import subprocess
import sys

# First generate the repomix with the correct file
print("Generating repomix for provenance_manager.py...")
cmd = [
    "npx", "repomix@latest",
    "--include", "src/core/provenance_manager.py",
    "--style", "xml",
    "--output", "claim1-repomix.xml",
    "."
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
    sys.exit(1)

# Check file size
import os
size = os.path.getsize("claim1-repomix.xml")
print(f"Repomix file size: {size/1024:.1f}KB")

# Now run gemini validation
print("\nRunning Gemini validation...")
cmd = [
    "python", "gemini-review-tool/gemini_review.py",
    ".", "--no-cache",
    "--prompt", """Validate ONLY this specific claim about ProvenanceManager:

CLAIM: Audit trails use cryptographic chaining preventing tampering

SPECIFIC CHECKS:
1. AuditEntry dataclass has @dataclass(frozen=True) decorator
2. SHA256 hash calculation includes previous_hash for chaining
3. verify_integrity() method checks chain continuity
4. ProvenanceManager._audit_trails is Dict[str, ImmutableAuditTrail]

Look for these specific patterns in src/core/provenance_manager.py:
- Line ~20: @dataclass(frozen=True) on AuditEntry
- Line ~30-40: Hash calculation with previous_hash
- Line ~55-66: verify_integrity() implementation
- Line ~93: _audit_trails type annotation

VERDICT:
✅ FULLY RESOLVED if all 4 checks pass
⚠️ PARTIALLY RESOLVED if some checks pass
❌ NOT RESOLVED if implementation missing"""
]

subprocess.run(cmd)