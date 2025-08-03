#!/usr/bin/env python3
"""
Installation Checker for Super-Digimon GraphRAG System
Comprehensive check that guides users through installation process
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check Python version requirements"""
    print("1. Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("💡 Please upgrade to Python 3.8 or higher")
        return False

def check_package_installation():
    """Check if package is properly installed"""
    print("\n2. Checking package installation...")
    try:
        import src
        print("✅ Package 'src' can be imported")
        return True
    except ImportError:
        print("❌ Package 'src' cannot be imported")
        print("💡 Run: pip install -e .")
        return False

def check_core_modules():
    """Check if core modules can be imported"""
    print("\n3. Checking core modules...")
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        print("✅ Core modules can be imported")
        return True
    except ImportError as e:
        print(f"❌ Core modules cannot be imported: {e}")
        print("💡 Check that all dependencies are installed")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n4. Checking dependencies...")
    required_packages = [
        'neo4j', 'spacy', 'pandas', 'numpy', 'PyPDF2', 
        'streamlit', 'plotly', 'networkx', 'yaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing dependencies: {', '.join(missing_packages)}")
        print("💡 Run: pip install -e .")
        return False
    else:
        print("✅ All required dependencies are installed")
        return True

def check_examples():
    """Check if examples work without sys.path hacks"""
    print("\n5. Checking examples...")
    examples_dir = Path(__file__).parent / "examples"
    
    if not examples_dir.exists():
        print("❌ Examples directory not found")
        return False
    
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
        print(f"❌ Examples use sys.path hacks: {', '.join(sys_path_issues)}")
        print("💡 Examples need to be updated to use proper imports")
        return False
    else:
        print("✅ Examples use proper imports")
        return True

def check_neo4j_optional():
    """Check Neo4j availability (optional)"""
    print("\n6. Checking Neo4j (optional)...")
    try:
        result = subprocess.run(['docker', 'exec', 'neo4j', 'echo', 'test'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Neo4j container is running")
            return True
        else:
            print("⚠️  Neo4j container not running (optional)")
            print("💡 Run: docker run -p 7687:7687 -p 7474:7474 --name neo4j -d -e NEO4J_AUTH=none neo4j:latest")
            return True  # Optional, so don't fail
    except FileNotFoundError:
        print("⚠️  Docker not found (optional)")
        print("💡 Install Docker to use Neo4j features")
        return True  # Optional, so don't fail

def main():
    """Run all installation checks"""
    print("🚀 Super-Digimon GraphRAG Installation Checker")
    print("=" * 60)
    
    checks = [
        check_python_version,
        check_package_installation,
        check_core_modules,
        check_dependencies,
        check_examples,
        check_neo4j_optional
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Installation is working correctly.")
        print("\nNext steps:")
        print("1. Run: python examples/minimal_working_example.py")
        print("2. Run: python ui/launch_ui.py")
        print("3. Check INSTALLATION_GUIDE.md for detailed instructions")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Run: pip install -e .")
        print("2. Check that you're in the correct directory")
        print("3. Verify Python version is 3.8+")
        print("4. See INSTALLATION_GUIDE.md for detailed help")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)