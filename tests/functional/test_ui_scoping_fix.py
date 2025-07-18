#!/usr/bin/env python3
"""
Test the UI scoping fix for PHASE2_AVAILABLE variable
"""

import sys
from pathlib import Path

# Add project paths

def test_ui_variable_scoping():
    """Test that the UI variables are properly scoped."""
    print("🧪 Testing UI Variable Scoping Fix")
    
    try:
        # Test importing the module
        print("1. Testing module import...")
        import graphrag_ui
        
        # Check initial values
        print(f"   PHASE1_AVAILABLE: {graphrag_ui.PHASE1_AVAILABLE}")
        print(f"   PHASE2_AVAILABLE: {graphrag_ui.PHASE2_AVAILABLE}")
        print(f"   PHASE3_AVAILABLE: {graphrag_ui.PHASE3_AVAILABLE}")
        print("✅ Module imports without UnboundLocalError")
        
        # Test render_system_status function
        print("\n2. Testing render_system_status function...")
        
        # Mock streamlit for testing
        class MockST:
            def markdown(self, text, unsafe_allow_html=False):
                pass
            def selectbox(self, label, options, help=None):
                return options[0] if options else None
            def checkbox(self, label, value=True):
                return value
            def slider(self, label, min_val, max_val, default):
                return default
            def warning(self, text):
                pass
            def subheader(self, text):
                pass
            def header(self, text):
                pass
            
            class sidebar:
                @staticmethod
                def header(text):
                    pass
                @staticmethod
                def subheader(text):
                    pass
                @staticmethod
                def markdown(text, unsafe_allow_html=False):
                    pass
                @staticmethod
                def selectbox(label, options, help=None):
                    return options[0] if options else None
                @staticmethod
                def checkbox(label, value=True):
                    return value
                @staticmethod
                def slider(label, min_val, max_val, default):
                    return default
                @staticmethod
                def warning(text):
                    pass
        
        # Temporarily replace streamlit
        original_st = getattr(graphrag_ui, 'st', None)
        graphrag_ui.st = MockST()
        
        try:
            # Call the function that was failing
            result = graphrag_ui.render_system_status()
            print("✅ render_system_status() executes without error")
            print(f"   Returns: {result}")
            
        finally:
            # Restore original streamlit
            if original_st:
                graphrag_ui.st = original_st
        
        print("\n🎉 UI scoping fix verified!")
        return True
        
    except Exception as e:
        print(f"❌ UI scoping test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    success = test_ui_variable_scoping()
    if success:
        print("\n✅ UI should now start without UnboundLocalError")
    else:
        print("\n❌ UI still has scoping issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)