#!/usr/bin/env python3
"""
Automated UI Testing Script

This script runs comprehensive UI tests without manual intervention.
Run this before deploying any UI changes.
"""

import subprocess
import sys
import time
import requests
import signal
import os
from pathlib import Path
import pytest

class UITestRunner:
    """Automated UI test runner"""
    
    def __init__(self):
        self.streamlit_process = None
        self.test_port = 8504
        self.base_url = f"http://localhost:{self.test_port}"
    
    def start_streamlit_server(self):
        """Start Streamlit server for testing"""
        print("🚀 Starting Streamlit server for testing...")
        
        # Start server in headless mode
        self.streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            f"--server.port={self.test_port}",
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        self.wait_for_server()
    
    def wait_for_server(self, timeout=30):
        """Wait for Streamlit server to be ready"""
        print(f"⏳ Waiting for server at {self.base_url}...")
        
        for i in range(timeout):
            try:
                response = requests.get(self.base_url, timeout=5)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            if i % 5 == 0:  # Progress indicator
                print(f"   Still waiting... ({i}/{timeout}s)")
        
        raise Exception(f"❌ Server failed to start within {timeout} seconds")
    
    def stop_streamlit_server(self):
        """Stop Streamlit server"""
        if self.streamlit_process:
            print("🛑 Stopping Streamlit server...")
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
    
    def run_unit_tests(self):
        """Run unit tests for UI components"""
        print("\n🧪 Running UI unit tests...")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/ui/test_ui_components.py",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Unit tests passed!")
        else:
            print("❌ Unit tests failed!")
            print(result.stdout)
            print(result.stderr)
            return False
        
        return True
    
    def run_streamlit_tests(self):
        """Run Streamlit-specific tests"""
        print("\n🎭 Running Streamlit component tests...")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/ui/test_streamlit_ui.py",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Streamlit tests passed!")
        else:
            print("❌ Streamlit tests failed!")
            print(result.stdout)
            print(result.stderr)
            return False
        
        return True
    
    def run_browser_tests(self):
        """Run automated browser tests"""
        print("\n🌐 Running browser automation tests...")
        
        # Check if selenium is available
        try:
            import selenium
        except ImportError:
            print("⚠️  Selenium not installed, skipping browser tests")
            print("   Install with: pip install selenium")
            return True
        
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/ui/test_ui_automation.py::TestStreamlitBrowserAutomation",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Browser tests passed!")
        else:
            print("❌ Browser tests failed!")
            print(result.stdout)
            print(result.stderr)
            return False
        
        return True
    
    def run_performance_tests(self):
        """Run UI performance tests"""
        print("\n⚡ Running performance tests...")
        
        # Simple performance test - check page load time
        start_time = time.time()
        try:
            response = requests.get(self.base_url, timeout=10)
            load_time = time.time() - start_time
            
            if response.status_code == 200 and load_time < 5:
                print(f"✅ Page loads in {load_time:.2f}s (acceptable)")
                return True
            else:
                print(f"❌ Page load too slow: {load_time:.2f}s")
                return False
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def check_ui_accessibility(self):
        """Basic accessibility checks"""
        print("\n♿ Running accessibility checks...")
        
        try:
            # Check that page has proper structure
            response = requests.get(self.base_url)
            content = response.text
            
            # Basic checks
            has_title = "<title>" in content
            has_headings = any(f"<h{i}" in content for i in range(1, 7))
            
            if has_title and has_headings:
                print("✅ Basic accessibility structure present")
                return True
            else:
                print("❌ Missing basic accessibility elements")
                return False
                
        except Exception as e:
            print(f"❌ Accessibility check failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run complete UI test suite"""
        print("🎯 Starting comprehensive UI test suite...")
        print("=" * 50)
        
        test_results = {}
        
        try:
            # 1. Unit tests (can run without server)
            test_results['unit_tests'] = self.run_unit_tests()
            
            # 2. Start server for integration tests
            self.start_streamlit_server()
            
            # 3. Streamlit component tests
            test_results['streamlit_tests'] = self.run_streamlit_tests()
            
            # 4. Performance tests
            test_results['performance_tests'] = self.run_performance_tests()
            
            # 5. Accessibility tests
            test_results['accessibility_tests'] = self.check_ui_accessibility()
            
            # 6. Browser automation tests
            test_results['browser_tests'] = self.run_browser_tests()
            
        finally:
            # Always stop the server
            self.stop_streamlit_server()
        
        # Report results
        self.report_results(test_results)
        
        # Return overall success
        return all(test_results.values())
    
    def report_results(self, results):
        """Report test results"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:25} {status}")
        
        print("-" * 50)
        print(f"Overall: {passed_tests}/{total_tests} test suites passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! UI is ready for deployment.")
        else:
            print("⚠️  Some tests failed. Fix issues before deploying.")
    
    def run_quick_smoke_test(self):
        """Run a quick smoke test to check basic functionality"""
        print("💨 Running quick smoke test...")
        
        try:
            self.start_streamlit_server()
            
            # Just check that the server responds
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✅ Smoke test passed - UI starts without errors")
                return True
            else:
                print(f"❌ Smoke test failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Smoke test failed: {e}")
            return False
        finally:
            self.stop_streamlit_server()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run UI tests")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick smoke test only")
    parser.add_argument("--unit-only", action="store_true",
                       help="Run unit tests only")
    
    args = parser.parse_args()
    
    runner = UITestRunner()
    
    try:
        if args.quick:
            success = runner.run_quick_smoke_test()
        elif args.unit_only:
            success = runner.run_unit_tests()
        else:
            success = runner.run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        runner.stop_streamlit_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        runner.stop_streamlit_server()
        sys.exit(1)

if __name__ == "__main__":
    main()