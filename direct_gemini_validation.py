#\!/usr/bin/env python3
"""Direct Gemini validation of Phase RELIABILITY implementations."""

import os
import google.generativeai as genai
from pathlib import Path

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Read the repomix output
with open('reliability-validation.xml', 'r') as f:
    codebase = f.read()

# Create validation prompt
prompt = f"""
Analyze the following codebase and validate the Phase RELIABILITY implementation claims.

{codebase}

## Validation Instructions:

For each claimed fix below, verify:
1. The implementation is present in the specified file
2. The implementation is complete (not a stub or placeholder)
3. The implementation addresses the specific issue mentioned

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

# Get response
response = model.generate_content(prompt)
print(response.text)
