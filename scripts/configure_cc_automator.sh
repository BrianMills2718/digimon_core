#!/bin/bash
# Configure cc_automator for Super-Digimon enhancements

echo "🚀 Configuring cc_automator for Super-Digimon enhancements..."

# Create .claude directory if it doesn't exist
mkdir -p cc_automator/.claude

# Copy Super-Digimon specific CLAUDE.md
echo "📋 Setting up enhancement specifications..."
cp cc_automator/specs/SUPER_DIGIMON_CLAUDE.md cc_automator/.claude/CLAUDE.md

# Backup original files
echo "💾 Backing up original files..."
cp cc_automator/specs/master_plan.md cc_automator/specs/master_plan.original.md
cp cc_automator/specs/onboarding_plan.md cc_automator/specs/onboarding_plan.original.md

# Use Super-Digimon specific onboarding
echo "🔧 Configuring onboarding for enhancements..."
cp cc_automator/specs/SUPER_DIGIMON_ONBOARDING.md cc_automator/specs/onboarding_plan.md

# Create enhancement tracking directory
echo "📊 Setting up enhancement tracking..."
mkdir -p cc_automator/enhancement_tracking
echo "{\"baseline_established\": false, \"enhancements_completed\": []}" > cc_automator/enhancement_tracking/status.json

# Create a simple test to verify digimon_scratch_cc2 is working
echo "✅ Creating baseline verification script..."
cat > cc_automator/verify_baseline.py << 'EOF'
#!/usr/bin/env python3
"""Verify digimon_scratch_cc2 is working before enhancements."""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.abspath(".."))

def verify_baseline():
    """Run basic tests to ensure system is working."""
    print("🔍 Verifying digimon_scratch_cc2 baseline functionality...")
    
    # Change to digimon_scratch_cc2 directory
    os.chdir("../digimon_scratch_cc2")
    
    # Run a simple test
    result = subprocess.run([sys.executable, "test_core_functionality.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Baseline tests passed!")
        print("   The system is ready for enhancements.")
        return True
    else:
        print("❌ Baseline tests failed!")
        print("   Please fix the existing system before enhancing.")
        print("\nError output:")
        print(result.stderr)
        return False

if __name__ == "__main__":
    if verify_baseline():
        sys.exit(0)
    else:
        sys.exit(1)
EOF

chmod +x cc_automator/verify_baseline.py

echo ""
echo "✅ Configuration complete!"
echo ""
echo "Next steps:"
echo "1. cd cc_automator"
echo "2. python verify_baseline.py  # Verify existing system works"
echo "3. python scripts/orchestrator.py  # Start enhancements"
echo ""
echo "The system will enhance digimon_scratch_cc2 with:"
echo "  • Neo4j persistence"
echo "  • SQLite metadata storage" 
echo "  • Advanced MCP features"
echo "  • StructGPT integration"
echo "  • Production optimizations"