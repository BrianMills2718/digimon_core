#!/usr/bin/env python3
"""
Launcher for GraphRAG Testing UI
Starts the Streamlit interface for testing Super-Digimon capabilities
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the GraphRAG testing UI"""
    
    # Ensure we're in the correct directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # UI file path
    ui_file = project_root / "ui" / "graphrag_ui.py"
    
    if not ui_file.exists():
        print(f"❌ UI file not found: {ui_file}")
        return 1
    
    print("🚀 Starting GraphRAG Testing UI...")
    print(f"📁 Project root: {project_root}")
    print(f"🌐 UI will be available at: http://localhost:8501")
    print("📝 Use Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(ui_file),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ]
        
        subprocess.run(cmd, env=env, cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n✅ UI server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting UI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())