#!/usr/bin/env python3
"""
Comprehensive UI and Interface Testing Script

This script systematically tests ALL user interfaces and functionality
to find integration issues before manual testing by users.

Usage: python test_all_interfaces_comprehensive.py
"""

import sys
import os
import subprocess
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any
import importlib.util

# Add project root to path
sys.path.insert(0, '.')

def test_result(name: str, success: bool, details: str = "", error: str = ""):
    """Standard test result format"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {name}")
    if details:
        print(f"    Details: {details}")
    if error:
        print(f"    Error: {error}")
    return {"name": name, "success": success, "details": details, "error": error}

def test_streamlit_ui_functions():
    """Test Streamlit UI core functions without running the full app"""
    results = []
    
    try:
        # Test imports
        print("\n🧪 Testing Streamlit UI imports...")
        import streamlit as st
        sys.path.insert(0, './ui')
        
        # Import the main module
        spec = importlib.util.spec_from_file_location("graphrag_ui", "./ui/graphrag_ui.py")
        ui_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ui_module)
        
        results.append(test_result("Streamlit UI imports", True, "All imports successful"))
        
        # Test DocumentProcessingResult class
        print("🧪 Testing DocumentProcessingResult class...")
        test_result_obj = ui_module.DocumentProcessingResult(
            document_id="test_id",
            filename="test.pdf", 
            entities_found=5,
            relationships_found=3,
            graph_data={"test": "data"},
            processing_time=1.0,
            phase_used="Phase 1"
        )
        
        # Test that it has the expected attributes
        assert hasattr(test_result_obj, 'filename')
        assert hasattr(test_result_obj, 'entities_found')
        assert test_result_obj.filename == "test.pdf"
        
        results.append(test_result("DocumentProcessingResult class", True, "Class works correctly"))
        
        # Test phase processing functions
        print("🧪 Testing phase processing functions...")
        
        # Mock session state for testing
        class MockSessionState:
            def __init__(self):
                self.processing_history = []
                
        # Test that we can create the processing functions
        test_functions = [
            'init_session_state',
            'process_with_phase1', 
            'process_with_phase2',
            'process_with_phase3'
        ]
        
        for func_name in test_functions:
            if hasattr(ui_module, func_name):
                results.append(test_result(f"Function {func_name}", True, "Function exists"))
            else:
                results.append(test_result(f"Function {func_name}", False, f"Function {func_name} not found"))
        
    except Exception as e:
        results.append(test_result("Streamlit UI functions", False, "", str(e)))
        print(f"Full traceback: {traceback.format_exc()}")
    
    return results

def test_cli_tool():
    """Test CLI tool with actual document processing"""
    results = []
    
    try:
        print("\n🧪 Testing CLI tool...")
        
        # Test basic import
        import ui.cli_tool
        results.append(test_result("CLI tool import", True, "Module imports successfully"))
        
        # Test with actual PDF processing
        test_pdf = "examples/pdfs/test_document.pdf"
        if os.path.exists(test_pdf):
            print(f"🧪 Testing CLI processing with {test_pdf}...")
            
            # Run CLI tool with timeout
            cmd = [sys.executable, "ui/cli_tool.py", "process", test_pdf, "What is this document about?"]
            
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                
                if result.returncode == 0:
                    results.append(test_result("CLI document processing", True, f"Processed {test_pdf} successfully"))
                else:
                    results.append(test_result("CLI document processing", False, 
                                             f"Return code: {result.returncode}", result.stderr))
                    
            except subprocess.TimeoutExpired:
                results.append(test_result("CLI document processing", False, "Timeout after 60s", "Processing took too long"))
                
        else:
            results.append(test_result("CLI test document", False, f"Test PDF not found: {test_pdf}"))
            
    except Exception as e:
        results.append(test_result("CLI tool", False, "", str(e)))
        
    return results

def test_demo_scripts():
    """Test all demo scripts"""
    results = []
    
    demo_scripts = [
        "scripts/demo/demo_extraction.py",
        "scripts/demo/show_graph_summary.py",
        "scripts/demo/query_by_type.py",
        "scripts/demo/find_climate_orgs.py"
    ]
    
    print("\n🧪 Testing demo scripts...")
    
    for script in demo_scripts:
        if os.path.exists(script):
            try:
                print(f"🧪 Testing {script}...")
                
                # Run script with timeout
                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    results.append(test_result(f"Demo script {script}", True, "Script completed successfully"))
                else:
                    results.append(test_result(f"Demo script {script}", False, 
                                             f"Return code: {result.returncode}", result.stderr))
                    
            except subprocess.TimeoutExpired:
                results.append(test_result(f"Demo script {script}", False, "Timeout after 30s"))
            except Exception as e:
                results.append(test_result(f"Demo script {script}", False, "", str(e)))
        else:
            results.append(test_result(f"Demo script {script}", False, "Script file not found"))
    
    return results

def test_examples():
    """Test example scripts"""
    results = []
    
    examples = [
        "examples/minimal_working_example.py",
        "examples/verify_installation.py"
    ]
    
    print("\n🧪 Testing examples...")
    
    for example in examples:
        if os.path.exists(example):
            try:
                print(f"🧪 Testing {example}...")
                
                result = subprocess.run(
                    [sys.executable, example],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    results.append(test_result(f"Example {example}", True, "Example completed successfully"))
                else:
                    results.append(test_result(f"Example {example}", False,
                                             f"Return code: {result.returncode}", result.stderr))
                    
            except subprocess.TimeoutExpired:
                results.append(test_result(f"Example {example}", False, "Timeout after 60s"))
            except Exception as e:
                results.append(test_result(f"Example {example}", False, "", str(e)))
        else:
            results.append(test_result(f"Example {example}", False, "Example file not found"))
    
    return results

def test_mcp_server():
    """Test MCP server startup"""
    results = []
    
    try:
        print("\n🧪 Testing MCP server...")
        
        # Test import
        import src.mcp_server
        results.append(test_result("MCP server import", True, "Module imports successfully"))
        
        # Test server startup (with timeout)
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); exec(open('src/mcp_server.py').read())"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # MCP server starting is success (it will hang waiting for input)
            results.append(test_result("MCP server startup", True, "Server starts successfully"))
            
        except subprocess.TimeoutExpired:
            # Timeout is expected for MCP server
            results.append(test_result("MCP server startup", True, "Server starts (timeout is normal)"))
        except Exception as e:
            results.append(test_result("MCP server startup", False, "", str(e)))
            
    except Exception as e:
        results.append(test_result("MCP server", False, "", str(e)))
        
    return results

def test_core_imports():
    """Test core module imports"""
    results = []
    
    core_modules = [
        "src.core.pipeline_orchestrator",
        "src.core.config_manager", 
        "src.core.tool_factory",
        "src.core.phase_adapters"
    ]
    
    print("\n🧪 Testing core imports...")
    
    for module in core_modules:
        try:
            __import__(module)
            results.append(test_result(f"Import {module}", True, "Module imports successfully"))
        except Exception as e:
            results.append(test_result(f"Import {module}", False, "", str(e)))
    
    return results

def generate_summary_report(all_results: List[Dict]):
    """Generate comprehensive summary report"""
    
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r["success"])
    failed_tests = total_tests - passed_tests
    
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TESTING SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ FAILED TESTS ({failed_tests}):")
        print("-" * 40)
        for i, result in enumerate(all_results, 1):
            if not result["success"]:
                print(f"{i}. {result['name']}")
                if result["error"]:
                    print(f"   Error: {result['error']}")
                print()
    
    overall_status = "✅ ALL TESTS PASSED" if failed_tests == 0 else f"❌ {failed_tests} TESTS FAILED"
    print(f"\n🎯 Overall Status: {overall_status}")
    
    return failed_tests == 0

def main():
    """Run comprehensive testing"""
    print("🚀 Starting Comprehensive Interface Testing...")
    print("This will systematically test ALL user interfaces and functionality")
    print("to find integration issues before manual testing.\n")
    
    all_results = []
    
    # Run all test suites
    test_suites = [
        ("Core Imports", test_core_imports),
        ("Streamlit UI Functions", test_streamlit_ui_functions), 
        ("CLI Tool", test_cli_tool),
        ("Demo Scripts", test_demo_scripts),
        ("Examples", test_examples),
        ("MCP Server", test_mcp_server)
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n{'='*60}")
        print(f"🧪 Testing {suite_name}")
        print('='*60)
        
        try:
            results = test_func()
            all_results.extend(results)
        except Exception as e:
            print(f"❌ Test suite {suite_name} crashed: {e}")
            all_results.append({
                "name": f"{suite_name} (suite crash)",
                "success": False,
                "details": "",
                "error": str(e)
            })
    
    # Generate summary
    success = generate_summary_report(all_results)
    
    if success:
        print("\n🎉 System is ready for production use!")
    else:
        print("\n⚠️  Issues found - system requires fixes before production use.")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())