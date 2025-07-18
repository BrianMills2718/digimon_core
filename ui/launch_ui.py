#!/usr/bin/env python3
"""Launch script for GraphRAG UI with proper error handling."""

import subprocess
import sys
import os
from pathlib import Path

def launch_ui():
    """Launch Streamlit UI with proper setup."""
    print("🚀 Launching GraphRAG UI...")
    
    # Verify installation
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        print("✅ Installation verified")
    except ImportError as e:
        print(f"❌ Installation error: {e}")
        print("Please run: pip install -e .")
        return False
    
    # Launch Streamlit
    ui_path = Path(__file__).parent / "graphrag_ui.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(ui_path)]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
        return True
    except KeyboardInterrupt:
        print("\n👋 UI stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to launch UI: {e}")
        return False

if __name__ == "__main__":
    launch_ui()