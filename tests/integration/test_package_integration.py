#!/usr/bin/env python3
"""
Package Integration Tests
Tests that verify package installation and imports work correctly
"""

import sys
import unittest
import importlib.util

class TestPackageIntegration(unittest.TestCase):
    """Test package integration without sys.path hacks"""
    
    def test_core_imports(self):
        """Test that core modules can be imported"""
        try:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
            from src.core.service_manager import get_service_manager
            self.assertTrue(True, "Core imports successful")
        except ImportError as e:
            self.fail(f"Core imports failed: {e}")
    
    def test_no_sys_path_in_examples(self):
        """Test that examples don't use sys.path manipulation"""
        from pathlib import Path
        
        examples_dir = Path(__file__).parent.parent.parent / "examples"
        python_files = list(examples_dir.glob("*.py"))
        
        sys_path_violations = []
        for file_path in python_files:
            # Skip verification script which legitimately checks for sys.path usage
            if file_path.name == "verify_package_installation.py":
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
                if 'sys.path.insert' in content or 'sys.path.append' in content:
                    sys_path_violations.append(file_path.name)
        
        self.assertEqual(len(sys_path_violations), 0, 
                        f"Found sys.path violations in: {sys_path_violations}")
    
    def test_package_installation(self):
        """Test that package is properly installed"""
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-c", "import src; print('OK')"], 
                                  capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, 
                           f"Package import failed: {result.stderr}")
        except Exception as e:
            self.fail(f"Package installation test failed: {e}")
    
    def test_basic_functionality(self):
        """Test basic system functionality"""
        try:
            from src.core.pipeline_orchestrator import PipelineOrchestrator
            from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
            
            config = create_unified_workflow_config(
                phase=Phase.PHASE1,
                optimization_level=OptimizationLevel.STANDARD
            )
            orchestrator = PipelineOrchestrator(config)
            self.assertIsNotNone(orchestrator, "PipelineOrchestrator creation failed")
        except Exception as e:
            self.fail(f"Basic functionality test failed: {e}")

if __name__ == '__main__':
    unittest.main()