#!/bin/bash

# Documentation Claims Verification Script
# Enforces "Truth Before Aspiration" rule for KGAS documentation

set -e

echo "🔍 Verifying documentation claims..."

# Check for aspirational claims without evidence
echo "Checking for unsubstantiated claims..."

# Look for performance claims without test evidence
if grep -r "performance\|speed\|latency\|throughput" docs/current/ | grep -v "TODO\|FIXME\|PENDING" | grep -E "(seconds?|ms|milliseconds?)" | grep -v "test_" | grep -v "benchmark"; then
    echo "❌ Found performance claims without test evidence"
    exit 1
fi

# Check for "implements" claims without code evidence
if grep -r "implements\|supports\|provides" docs/current/ | grep -v "TODO\|FIXME\|PENDING" | grep -v "test_" | grep -v "example"; then
    echo "❌ Found implementation claims without code evidence"
    exit 1
fi

# Verify schema version consistency
echo "Checking schema version consistency..."
if ! grep -r "meta_schema_v9" docs/current/ | grep -v "TODO\|FIXME"; then
    echo "❌ Meta-schema v9 not consistently referenced"
    exit 1
fi

# Check for proper cross-references
echo "Checking cross-references..."
if ! grep -r "ROADMAP_v2\.1\.md" docs/current/ | grep -v "TABLE_OF_CONTENTS"; then
    echo "❌ Missing roadmap cross-references"
    exit 1
fi

echo "✅ All documentation claims verified"
exit 0 