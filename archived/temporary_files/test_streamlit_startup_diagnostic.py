#!/usr/bin/env python3
"""
Streamlit Startup Diagnostic Tool
Identifies and fixes specific UI startup issues
"""

import sys
import os
import traceback
from pathlib import Path
import importlib.util

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class StreamlitDiagnostic:
    """Diagnostic tool for Streamlit UI issues"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
    
    def check_dependencies(self):
        """Check all required dependencies"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            "streamlit",
            "plotly",
            "pandas", 
            "networkx",
            "dataclasses"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - MISSING")
                missing_packages.append(package)
        
        if missing_packages:
            self.issues_found.append(f"Missing packages: {missing_packages}")
        
        return len(missing_packages) == 0
    
    def check_project_imports(self):
        """Check project-specific imports"""
        print("\n🔍 Checking project imports...")
        
        project_modules = [
            "src.ontology.gemini_ontology_generator",
            "src.core.ontology_storage_service", 
            "src.core.config",
            "src.ontology_generator"
        ]
        
        import_issues = []
        for module in project_modules:
            try:
                spec = importlib.util.find_spec(module)
                if spec is None:
                    print(f"  ❌ {module} - NOT FOUND")
                    import_issues.append(f"Module {module} not found")
                else:
                    # Try actual import
                    imported = importlib.import_module(module)
                    print(f"  ✅ {module}")
            except Exception as e:
                print(f"  ⚠️  {module} - ERROR: {str(e)}")
                import_issues.append(f"Module {module}: {str(e)}")
        
        if import_issues:
            self.issues_found.extend(import_issues)
        
        return len(import_issues) == 0
    
    def check_streamlit_app_structure(self):
        """Check streamlit_app.py structure and functions"""
        print("\n🔍 Checking streamlit_app.py structure...")
        
        try:
            import streamlit_app
            
            required_functions = [
                "init_session_state",
                "get_ontology_generator",
                "get_storage_service",
                "generate_ontology_with_gemini",
                "validate_ontology_with_text",
                "render_header",
                "render_sidebar",
                "render_chat_interface",
                "render_ontology_preview",
                "main"
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if hasattr(streamlit_app, func_name):
                    print(f"  ✅ {func_name}")
                else:
                    print(f"  ❌ {func_name} - MISSING")
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.issues_found.append(f"Missing functions: {missing_functions}")
            
            return len(missing_functions) == 0
            
        except Exception as e:
            error_msg = f"Cannot import streamlit_app.py: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.issues_found.append(error_msg)
            return False
    
    def check_configuration(self):
        """Check configuration and environment setup"""
        print("\n🔍 Checking configuration...")
        
        try:
            from src.core.config import ConfigurationManager
            config_manager = ConfigurationManager()
            config = config_manager.get_config()
            print("  ✅ Configuration manager works")
            
            # Check API keys
            api_key_status = {}
            if hasattr(config, 'api'):
                if hasattr(config.api, 'google_api_key'):
                    api_key_status['google'] = bool(config.api.google_api_key)
                if hasattr(config.api, 'openai_api_key'):
                    api_key_status['openai'] = bool(config.api.openai_api_key)
            
            print(f"  🔑 API Keys: {api_key_status}")
            
            return True
            
        except Exception as e:
            error_msg = f"Configuration error: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.issues_found.append(error_msg)
            return False
    
    def check_ui_initialization(self):
        """Test UI initialization without starting server"""
        print("\n🔍 Testing UI initialization...")
        
        try:
            import streamlit_app
            
            # Test session state initialization
            streamlit_app.init_session_state()
            print("  ✅ Session state initialization")
            
            # Test generator initialization (should not fail even if API keys missing)
            generator = streamlit_app.get_ontology_generator()
            print(f"  ✅ Generator initialization (available: {generator is not None})")
            
            # Test storage service initialization
            storage = streamlit_app.get_storage_service()
            print(f"  ✅ Storage service initialization (available: {storage is not None})")
            
            return True
            
        except Exception as e:
            error_msg = f"UI initialization error: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.issues_found.append(error_msg)
            print(f"  📋 Traceback: {traceback.format_exc()}")
            return False
    
    def attempt_fixes(self):
        """Attempt to fix common issues"""
        print("\n🔧 Attempting to fix common issues...")
        
        # Check if any fixes are needed based on issues found
        fixes_needed = False
        
        for issue in self.issues_found:
            if "Missing packages" in issue:
                print("  📦 Install missing packages with: pip install streamlit plotly pandas networkx")
                fixes_needed = True
            
            elif "Module" in issue and "not found" in issue:
                print("  📁 Ensure project is properly installed: pip install -e .")
                fixes_needed = True
            
            elif "Configuration error" in issue:
                print("  ⚙️  Check config files and environment variables")
                fixes_needed = True
        
        if not fixes_needed:
            print("  ✅ No automatic fixes needed")
        
        return not fixes_needed
    
    def generate_fix_script(self):
        """Generate a script to fix identified issues"""
        if not self.issues_found:
            return None
        
        fix_script = """#!/bin/bash
# Auto-generated fix script for Streamlit UI issues

echo "🔧 Fixing Streamlit UI issues..."

# Install missing packages
pip install streamlit plotly pandas networkx dataclasses

# Reinstall project in editable mode
pip install -e .

# Check configuration
echo "✅ Please verify your .env file has the required API keys"
echo "✅ Run: python test_streamlit_startup_diagnostic.py"

echo "🚀 Fixes applied. Try running streamlit again."
"""
        
        with open("fix_streamlit_issues.sh", "w") as f:
            f.write(fix_script)
        
        os.chmod("fix_streamlit_issues.sh", 0o755)
        return "fix_streamlit_issues.sh"
    
    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print("🏥 STREAMLIT UI DIAGNOSTIC REPORT")
        print("=" * 50)
        
        checks = [
            ("Dependencies", self.check_dependencies),
            ("Project Imports", self.check_project_imports),
            ("App Structure", self.check_streamlit_app_structure),
            ("Configuration", self.check_configuration),
            ("UI Initialization", self.check_ui_initialization)
        ]
        
        results = {}
        all_passed = True
        
        for check_name, check_func in checks:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        
        print("\n" + "=" * 50)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 50)
        
        for check_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {check_name}")
        
        if self.issues_found:
            print("\n🚨 ISSUES FOUND:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        
        print(f"\n🎯 OVERALL STATUS: {'✅ READY' if all_passed else '❌ NEEDS FIXES'}")
        
        if not all_passed:
            self.attempt_fixes()
            fix_script = self.generate_fix_script()
            if fix_script:
                print(f"\n🔧 Generated fix script: {fix_script}")
                print("Run: chmod +x fix_streamlit_issues.sh && ./fix_streamlit_issues.sh")
        
        return all_passed


def main():
    """Run diagnostic"""
    diagnostic = StreamlitDiagnostic()
    success = diagnostic.run_full_diagnostic()
    
    if success:
        print("\n🚀 Streamlit UI is ready! Try: streamlit run streamlit_app.py")
    else:
        print("\n🔧 Please fix the issues above and run diagnostic again")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)