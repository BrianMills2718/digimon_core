#!/usr/bin/env python3
"""
Debug the UI status check function to see why Phase 2/3 show as unavailable
"""

from pathlib import Path

# Add project root to path (same as UI does)

# Mock streamlit to capture what's happening
class MockStreamlit:
    def __init__(self):
        self.messages = []
    
    def markdown(self, text, unsafe_allow_html=False):
        self.messages.append(text)
        print(f"UI would show: {text}")
    
    class sidebar:
        @staticmethod
        def header(text):
            print(f"HEADER: {text}")
        
        @staticmethod
        def subheader(text):
            print(f"SUBHEADER: {text}")

# Replace streamlit in the UI module
import ui.graphrag_ui as graphrag_ui
graphrag_ui.st = MockStreamlit()

print("🔍 Debugging UI Status Check")
print("=" * 50)

# Test the status check function directly
print("\n1. Testing render_system_status function...")

# We need to mock the sidebar context
class MockSidebar:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def header(self, text):
        print(f"SIDEBAR HEADER: {text}")
    def subheader(self, text):
        print(f"SIDEBAR SUBHEADER: {text}")
    def markdown(self, text, unsafe_allow_html=False):
        print(f"SIDEBAR: {text}")
    def selectbox(self, *args, **kwargs):
        return "Phase 1: Basic"
    def checkbox(self, *args, **kwargs):
        return True
    def slider(self, *args, **kwargs):
        return 100
    def warning(self, text):
        print(f"WARNING: {text}")

graphrag_ui.st.sidebar = MockSidebar()

# Capture the global variables before and after
print(f"Before - PHASE2_AVAILABLE: {graphrag_ui.PHASE2_AVAILABLE}")
print(f"Before - PHASE3_AVAILABLE: {graphrag_ui.PHASE3_AVAILABLE}")
print(f"Before - MCP_AVAILABLE: {graphrag_ui.MCP_AVAILABLE}")

# Run the function that checks availability
try:
    result = graphrag_ui.render_system_status()
    print("✅ render_system_status completed")
except Exception as e:
    print(f"❌ render_system_status failed: {e}")
    import traceback
    traceback.print_exc()

print(f"After - PHASE2_AVAILABLE: {graphrag_ui.PHASE2_AVAILABLE}")  
print(f"After - PHASE3_AVAILABLE: {graphrag_ui.PHASE3_AVAILABLE}")
print(f"After - MCP_AVAILABLE: {graphrag_ui.MCP_AVAILABLE}")