#!/usr/bin/env python3
"""
Test the exact import context that Streamlit UI uses
"""

from pathlib import Path

# Add project root to path (same as UI does)

print("🔍 Testing UI Import Context")
print(f"Python path: {sys.path[:3]}")
print(f"Current directory: {Path.cwd()}")

# Test Phase 2 import exactly as UI does
print("\n1. Testing Phase 2 import...")
try:
    from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
    print("✅ Phase 2: Available")
except ImportError as e:
    print(f"❌ Phase 2: Not Available - {e}")

# Test Phase 3 import exactly as UI does  
print("\n2. Testing Phase 3 import...")
try:
    from src.core.phase_adapters import Phase3Adapter
    print("✅ Phase 3: Available")
except ImportError as e:
    print(f"❌ Phase 3: Not Available - {e}")

# Test MCP import exactly as UI does
print("\n3. Testing MCP import...")
try:
    import mcp
    from src.mcp_server import mcp as super_digimon_mcp
    print("✅ MCP: Available")
except ImportError as e:
    print(f"❌ MCP: Not Available - {e}")

print("\n4. Testing if files exist...")
phase2_file = Path("src/tools/phase2/enhanced_vertical_slice_workflow.py")
phase3_file = Path("src/core/phase_adapters.py")
mcp_file = Path("src/mcp_server.py")

print(f"Phase 2 file exists: {phase2_file.exists()}")
print(f"Phase 3 file exists: {phase3_file.exists()}")
print(f"MCP file exists: {mcp_file.exists()}")