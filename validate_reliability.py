#!/usr/bin/env python3
"""Direct validation of Phase RELIABILITY implementations using Gemini."""

import os
from pathlib import Path

# Read the repomix output
repomix_file = Path("reliability-validation.xml")
with open(repomix_file, 'r') as f:
    codebase = f.read()

# Create validation prompt
prompt = """
Validate the Phase RELIABILITY implementation claims for KGAS. 

For each claimed fix, verify:
1. The implementation is present in the specified file
2. The implementation is complete (not a stub or placeholder)
3. The implementation addresses the specific issue mentioned

## Claims to Validate:

### Claim 1: Audit Trail Immutability
- **File**: src/core/provenance_manager.py
- **Expected**: ImmutableAuditTrail class with SHA256 cryptographic chaining
- **Verify**: 
  - AuditEntry dataclass is frozen (immutable)
  - Hash chaining implemented with previous_hash linking
  - verify_integrity() method can detect tampering
  - ProvenanceManager uses ImmutableAuditTrail instead of mutable dicts

### Claim 2: Performance Tracking
- **File**: src/monitoring/performance_tracker.py  
- **Expected**: PerformanceTracker with automatic baseline establishment
- **Verify**:
  - PerformanceTracker class fully implemented
  - Automatic baseline calculation after configurable samples
  - Degradation detection when performance exceeds thresholds
  - Persistent storage of baselines to JSON

### Claim 3: SLA Monitoring
- **File**: src/core/sla_monitor.py
- **Expected**: SLAMonitor with violation detection and alerting
- **Verify**:
  - SLAMonitor class with configurable thresholds
  - Real-time violation detection for duration and error rates
  - Alert handler registration and callback system
  - Integration with PerformanceTracker for metrics

## Verdict Format:
For each claim, provide:
- ✅ FULLY RESOLVED: Implementation complete and addresses the issue
- ⚠️ PARTIALLY RESOLVED: Implementation present but incomplete
- ❌ NOT RESOLVED: Implementation missing or doesn't address the issue

Include specific line numbers and code snippets as evidence.
"""

# Send to Gemini via the tool
import subprocess
import tempfile

# Save prompt to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(prompt)
    prompt_file = f.name

# Run gemini review with the repomix file
cmd = [
    'python', 'gemini-review-tool/gemini_review.py',
    '.', '--no-cache',
    '--prompt', prompt_file,
    '--keep-repomix'
]

# Copy repomix file to expected location
import shutil
shutil.copy('reliability-validation.xml', 'gemini-review-tool/repomix-output.xml')

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Clean up
os.unlink(prompt_file)