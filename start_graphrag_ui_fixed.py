#!/usr/bin/env python3
"""
Start GraphRAG Testing UI with fixes applied
Use a different port to avoid conflicts
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the GraphRAG UI on port 8502 to avoid conflicts"""
    
    print("🚀 Starting FIXED GraphRAG Testing UI...")
    print(f"📁 Project root: {Path.cwd()}")
    print("🌐 UI will be available at: http://localhost:8503")
    print("📝 Use Ctrl+C to stop the server")
    print("--" * 25)
    
    # Stay in project root directory so imports work
    project_root = Path(__file__).parent
    ui_file = project_root / "ui" / "graphrag_ui.py"
    
    # Start streamlit with explicit port from project root
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(ui_file),
            "--server.port", "8503",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], cwd=project_root, check=True)
    except KeyboardInterrupt:
        print("\n👋 GraphRAG UI stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()