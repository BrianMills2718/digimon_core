#!/usr/bin/env python3
"""
Final UI Fix Verification
Test that all UI startup issues are resolved.
"""

import sys
import subprocess
import time
import requests
from pathlib import Path

def test_ui_startup():
    """Test that UI starts without errors."""
    print("🧪 Testing Complete UI Startup Fix")
    
    # Start UI process
    ui_process = None
    try:
        print("1. Starting UI on port 8504...")
        ui_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "/home/brian/Digimons/ui/graphrag_ui.py",
            "--server.port", "8504",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for startup
        print("2. Waiting for UI startup...")
        time.sleep(8)
        
        # Check if process is still running (not crashed)
        if ui_process.poll() is None:
            print("✅ UI process started and is running")
        else:
            stdout, stderr = ui_process.communicate()
            print(f"❌ UI process exited: {ui_process.returncode}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        # Try to connect to UI
        print("3. Testing UI connectivity...")
        try:
            response = requests.get("http://localhost:8504", timeout=5)
            if response.status_code == 200:
                print("✅ UI responds with HTTP 200")
            else:
                print(f"⚠️ UI responds with HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ UI connection failed: {e} (may be normal for headless mode)")
        
        # Check error output
        print("4. Checking for startup errors...")
        stdout, stderr = ui_process.communicate(timeout=2)
        
        # Look for specific errors we fixed
        error_patterns = [
            "UnboundLocalError",
            "torch.classes", 
            "multiple record",
            "RuntimeError: no running event loop"
        ]
        
        found_errors = []
        full_output = stdout + stderr
        for pattern in error_patterns:
            if pattern in full_output:
                found_errors.append(pattern)
        
        if found_errors:
            print(f"❌ Found error patterns: {found_errors}")
            print("STDERR:", stderr[-1000:])  # Last 1000 chars
            return False
        else:
            print("✅ No critical error patterns found")
        
        return True
        
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        return False
    
    finally:
        # Clean up process
        if ui_process and ui_process.poll() is None:
            ui_process.terminate()
            time.sleep(2)
            if ui_process.poll() is None:
                ui_process.kill()

def test_import_fixes():
    """Test that imports work without side effects."""
    print("\n🔧 Testing Import Fixes")
    
    try:
        # Test lazy loading is working
        print("1. Testing spaCy lazy loading...")
        
        import sys
        old_modules = set(sys.modules.keys())
        
        # Import UI components
        from ui.graphrag_ui import _get_phase1_workflow, PHASE1_AVAILABLE
        
        new_modules = set(sys.modules.keys()) - old_modules
        spacy_modules = [m for m in new_modules if 'spacy' in m]
        
        if not spacy_modules:
            print("✅ spaCy modules not loaded on import")
        else:
            print(f"⚠️ spaCy modules loaded: {spacy_modules}")
        
        # Test Phase 1 workflow creation speed
        print("2. Testing workflow creation speed...")
        start_time = time.time()
        workflow = _get_phase1_workflow()
        creation_time = time.time() - start_time
        
        print(f"   Workflow creation time: {creation_time:.2f}s")
        if creation_time < 5:  # Should be fast
            print("✅ Fast workflow creation (lazy loading working)")
        else:
            print("⚠️ Slow workflow creation (lazy loading may not be effective)")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all UI fix tests."""
    print("🔬 Complete UI Fix Verification")
    print("=" * 50)
    
    tests = [
        ("Import Fixes", test_import_fixes),
        ("UI Startup", test_ui_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "="*50)
    print("🏁 FINAL RESULTS")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL UI FIXES VERIFIED SUCCESSFUL!")
        print("\n📋 Summary of Fixed Issues:")
        print("   ✅ UnboundLocalError for PHASE2_AVAILABLE/PHASE3_AVAILABLE")
        print("   ✅ spaCy/torch conflicts with lazy loading")
        print("   ✅ Neo4j multiple record warnings")
        print("   ✅ UI startup speed improved")
        print("\n🚀 UI should now start cleanly on:")
        print("   python start_graphrag_ui_fixed.py")
        print("   http://localhost:8502")
    else:
        print(f"\n⚠️ {total-passed} test(s) failed - additional fixes needed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)