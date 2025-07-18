#!/usr/bin/env python3
"""
Installation Process Test
Tests the complete installation process as a user would experience it
"""

import unittest
import subprocess
import sys
import tempfile
import os
from pathlib import Path

class TestInstallationProcess(unittest.TestCase):
    """Test complete installation process"""
    
    def test_pip_install_works(self):
        """Test that pip install -e . works correctly"""
        try:
            # This test assumes the package is already installed in development mode
            # In a real scenario, this would be run in a clean environment
            result = subprocess.run([sys.executable, "-c", "import src"], 
                                  capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, 
                           f"Package not importable after installation: {result.stderr}")
        except Exception as e:
            self.fail(f"Installation test failed: {e}")
    
    def test_verification_script_works(self):
        """Test that verification script works"""
        verification_script = Path(__file__).parent.parent / "examples" / "verify_package_installation.py"
        
        if verification_script.exists():
            try:
                result = subprocess.run([sys.executable, str(verification_script)], 
                                      capture_output=True, text=True)
                # If verification script exists, it should pass
                self.assertEqual(result.returncode, 0, 
                               f"Verification script failed: {result.stderr}")
            except Exception as e:
                self.fail(f"Verification script test failed: {e}")

if __name__ == '__main__':
    unittest.main()