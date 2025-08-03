#!/usr/bin/env python3
"""
Package Installation Verification Script
Verifies that the package can be imported properly without sys.path hacks
"""

import sys
import importlib.util
import subprocess
from pathlib import Path

def verify_package_installation():
    """Verify package installation is working correctly."""
    print("🔍 Package Installation Verification")
    print("=" * 50)
    
    # Check 1: Verify package can be imported
    print("\n1. Testing package imports...")
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.service_manager import get_service_manager
        print("✅ Core imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Solution: Run 'pip install -e .' from project root")
        return False
    
    # Check 2: Verify no sys.path in examples
    print("\n2. Checking examples for sys.path hacks...")
    examples_dir = Path(__file__).parent
    python_files = list(examples_dir.glob("*.py"))
    
    sys_path_issues = []
    for file_path in python_files:
        # Skip verification script which legitimately checks for sys.path usage
        if file_path.name == "verify_package_installation.py":
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            if 'sys.path.insert' in content or 'sys.path.append' in content:
                sys_path_issues.append(file_path.name)
    
    if sys_path_issues:
        print(f"❌ Found sys.path hacks in: {', '.join(sys_path_issues)}")
        print("💡 Solution: Remove sys.path manipulation, use proper package imports")
        return False
    else:
        print("✅ No sys.path hacks found")
    
    # Check 3: Verify package is properly installed
    print("\n3. Verifying package installation...")
    try:
        result = subprocess.run([sys.executable, "-c", "import src; print('Package installed correctly')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Package installed correctly")
        else:
            print(f"❌ Package installation issue: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Package verification failed: {e}")
        return False
    
    # Check 4: Test basic functionality
    print("\n4. Testing basic functionality...")
    try:
        config = create_unified_workflow_config(
            phase=Phase.PHASE1,
            optimization_level=OptimizationLevel.STANDARD
        )
        orchestrator = PipelineOrchestrator(config)
        print("✅ PipelineOrchestrator creates successfully")
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False
    
    print("\n🎉 All verification checks passed!")
    print("✅ Package installation is working correctly")
    return True

if __name__ == "__main__":
    success = verify_package_installation()
    exit(0 if success else 1)