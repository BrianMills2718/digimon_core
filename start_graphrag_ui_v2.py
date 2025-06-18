#!/usr/bin/env python3
"""
Launch GraphRAG UI v2.0 with Standardized Phase Interface

This launcher starts the improved UI that uses the standardized
GraphRAG phase interface for consistent phase interaction.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import streamlit
        print("✅ Streamlit available")
    except ImportError:
        print("❌ Streamlit not installed. Run: pip install streamlit")
        return False
    
    try:
        from src.ui.ui_phase_adapter import get_ui_phase_manager
        manager = get_ui_phase_manager()
        if manager.is_initialized():
            print("✅ UI Phase Manager initialized")
            phases = manager.get_available_phases()
            print(f"✅ Available phases: {phases}")
        else:
            print("❌ UI Phase Manager failed to initialize")
            return False
    except ImportError as e:
        print(f"❌ UI Phase Adapter not available: {e}")
        return False
    
    return True

def main():
    """Launch the GraphRAG UI v2.0"""
    print("🚀 GraphRAG UI v2.0 Launcher")
    print("=" * 50)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Launch Streamlit
    print("\n🚀 Launching GraphRAG UI v2.0...")
    ui_path = Path(__file__).parent / "ui" / "graphrag_ui_v2.py"
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(ui_path),
            "--server.port", "8502",  # Different port from v1
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch UI: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 UI stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()