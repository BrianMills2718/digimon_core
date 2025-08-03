#!/usr/bin/env python3
"""
Comprehensive Test Suite for All Critical Fixes
Verifies that all Gemini validation issues have been resolved
"""

import unittest
import sys
import subprocess
from pathlib import Path

class TestAllFixes(unittest.TestCase):
    """Test all critical fixes from Gemini validation"""
    
    def test_fix_1_package_installation(self):
        """Test Fix 1: Package installation works without sys.path hacks"""
        # Test package can be imported
        try:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.tool_factory import create_unified_workflow_config
        except ImportError as e:
            self.fail(f"Package installation failed: {e}")
    
    def test_fix_2_no_sys_path_hacks(self):
        """Test Fix 2: No sys.path manipulation in examples"""
        examples_dir = Path(__file__).parent.parent / "examples"
        python_files = list(examples_dir.glob("*.py"))
        
        for file_path in python_files:
            # Skip verification script which legitimately checks for sys.path usage
            if file_path.name == "verify_package_installation.py":
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertNotIn('sys.path.insert', content, 
                               f"Found sys.path.insert in {file_path}")
                self.assertNotIn('sys.path.append', content, 
                               f"Found sys.path.append in {file_path}")
    
    def test_fix_3_documentation_consistency(self):
        """Test Fix 3: Documentation is consistently experimental"""
        readme_path = Path(__file__).parent.parent / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
                self.assertIn('EXPERIMENTAL', content, 
                            "README.md should contain experimental warning")
                self.assertNotIn('production-ready', content.lower(), 
                               "README.md should not contain production-ready claims")
    
    def test_fix_4_examples_work(self):
        """Test Fix 4: Examples work without import errors"""
        try:
            # Test that minimal example can be imported and basic functions work
            from pathlib import Path
            
            from examples.minimal_working_example import minimal_working_example
            # Just test import, not full execution (which needs Neo4j)
            self.assertTrue(callable(minimal_working_example))
        except ImportError as e:
            self.fail(f"Example import failed: {e}")
        finally:
            # Clean up sys.path modification
            if str(Path(__file__).parent.parent) in sys.path:
                sys.path.remove(str(Path(__file__).parent.parent))
    
    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and is valid"""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml should exist")
        
        # Basic validation
        with open(pyproject_path, 'r') as f:
            content = f.read()
            self.assertIn('[project]', content, "pyproject.toml should have [project] section")
            self.assertIn('name = "super-digimon-graphrag"', content, 
                         "pyproject.toml should have correct project name")

if __name__ == '__main__':
    unittest.main()