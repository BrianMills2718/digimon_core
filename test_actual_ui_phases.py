#!/usr/bin/env python3
"""
Test the actual UI to see if phases show as available now
"""

import requests
import re
import time

def test_ui_phases():
    """Test if phases show as available in actual UI"""
    print("🔍 Testing Actual UI Phase Status")
    
    # Wait for UI to be ready
    for i in range(10):
        try:
            response = requests.get("http://localhost:8502", timeout=5)
            if response.status_code == 200:
                break
        except:
            time.sleep(1)
    else:
        print("❌ UI not responding")
        return False
    
    print("✅ UI is responding")
    
    # Get the page content
    content = response.text
    
    # Check for phase availability indicators
    phase2_available = "Phase 2: Ontology System" in content
    phase3_available = "Phase 3: Multi-Document Fusion" in content
    mcp_available = "MCP Server Connected" in content
    
    # Check for unavailable indicators
    phase2_unavailable = "Phase 2: Not Available" in content  
    phase3_unavailable = "Phase 3: Not Available" in content
    mcp_unavailable = "MCP Server Disconnected" in content
    
    print(f"\n📊 Phase Availability Status:")
    print(f"Phase 2 Available: {phase2_available}")
    print(f"Phase 2 Not Available: {phase2_unavailable}")
    print(f"Phase 3 Available: {phase3_available}")  
    print(f"Phase 3 Not Available: {phase3_unavailable}")
    print(f"MCP Available: {mcp_available}")
    print(f"MCP Not Available: {mcp_unavailable}")
    
    # Look for specific phase selection options
    phase_options = []
    if "Phase 1: Basic" in content:
        phase_options.append("Phase 1")
    if "Phase 2: Enhanced" in content:
        phase_options.append("Phase 2")
    if "Phase 3: Multi-Doc" in content:
        phase_options.append("Phase 3")
    
    print(f"\n📋 Available Phase Options: {phase_options}")
    
    success = (phase2_available and phase3_available and mcp_available)
    
    if success:
        print("\n🎉 All phases should now be available in UI!")
    else:
        print("\n⚠️ Some phases still showing as unavailable")
        
        # Show some content for debugging
        if "Not Available" in content:
            print("\n🔍 Debug - Content around 'Not Available':")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "Not Available" in line:
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        print(f"{marker}{lines[j]}")
                    print()
    
    return success

if __name__ == "__main__":
    test_ui_phases()