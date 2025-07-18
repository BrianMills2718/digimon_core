#!/usr/bin/env python3
"""
Comprehensive Streamlit UI Testing Framework
Tests all UI components, integrations, and workflows for production readiness
"""

import sys
import os
import subprocess
import time
import json
import requests
from pathlib import Path
from typing import Dict, Any, List
import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.evidence_logger import evidence_logger

class StreamlitTester:
    """Comprehensive Streamlit UI testing framework"""
    
    def __init__(self):
        self.base_url = "http://localhost:8501"
        self.streamlit_process = None
        self.test_results = {}
        
    def setup_test_environment(self):
        """Set up test environment and start Streamlit"""
        try:
            # Kill any existing Streamlit processes
            subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
            time.sleep(2)
            
            # Start Streamlit in background
            self.streamlit_process = subprocess.Popen([
                "streamlit", "run", "streamlit_app.py",
                "--server.headless", "true",
                "--server.port", "8501",
                "--browser.gatherUsageStats", "false"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for startup
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.base_url}/healthz", timeout=1)
                    if response.status_code == 200:
                        return True
                except:
                    time.sleep(1)
            
            return False
            
        except Exception as e:
            print(f"Failed to setup test environment: {e}")
            return False
    
    def teardown_test_environment(self):
        """Clean up test environment"""
        if self.streamlit_process:
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
    
    def test_ui_startup(self) -> Dict[str, Any]:
        """Test UI startup and basic functionality"""
        try:
            # Test main page loads
            response = requests.get(self.base_url, timeout=10)
            startup_success = response.status_code == 200
            
            # Test if UI components are accessible
            ui_accessible = "Ontology Generator" in response.text
            
            # Test if required imports work
            import_test = self._test_imports()
            
            return {
                "startup_success": startup_success,
                "ui_accessible": ui_accessible,
                "import_test": import_test,
                "status_code": response.status_code,
                "response_size": len(response.text)
            }
            
        except Exception as e:
            return {
                "startup_success": False,
                "ui_accessible": False,
                "import_test": False,
                "error": str(e)
            }
    
    def _test_imports(self) -> Dict[str, bool]:
        """Test all required imports for UI"""
        imports_to_test = [
            "streamlit",
            "plotly.graph_objects",
            "pandas",
            "networkx",
            "src.ontology_generator",
            "src.core.config"
        ]
        
        results = {}
        for module in imports_to_test:
            try:
                __import__(module)
                results[module] = True
            except ImportError:
                results[module] = False
        
        return results
    
    def test_ui_components(self) -> Dict[str, Any]:
        """Test individual UI components"""
        try:
            # Test streamlit app import
            import streamlit_app
            
            # Test session state initialization
            streamlit_app.init_session_state()
            
            # Test ontology generator initialization
            generator = streamlit_app.get_ontology_generator()
            generator_available = generator is not None
            
            # Test storage service initialization
            storage = streamlit_app.get_storage_service()
            storage_available = storage is not None
            
            # Test UI component functions
            component_tests = {}
            ui_functions = [
                "render_header", 
                "render_sidebar",
                "render_chat_interface",
                "render_ontology_preview"
            ]
            
            for func_name in ui_functions:
                try:
                    func = getattr(streamlit_app, func_name)
                    component_tests[func_name] = callable(func)
                except AttributeError:
                    component_tests[func_name] = False
            
            return {
                "session_init": True,
                "generator_available": generator_available,
                "storage_available": storage_available,
                "component_tests": component_tests,
                "all_components_working": all(component_tests.values())
            }
            
        except Exception as e:
            return {
                "session_init": False,
                "generator_available": False,
                "storage_available": False,
                "component_tests": {},
                "all_components_working": False,
                "error": str(e)
            }
    
    def test_ui_workflow_integration(self) -> Dict[str, Any]:
        """Test UI integration with GraphRAG workflows"""
        try:
            import streamlit_app
            
            # Test ontology generation workflow
            test_domain = "Test domain for UI integration"
            config = {
                "temperature": 0.7,
                "max_entities": 10,
                "max_relations": 5
            }
            
            ontology = streamlit_app.generate_ontology_with_gemini(test_domain, config)
            ontology_generated = ontology is not None
            
            # Test ontology validation
            if ontology:
                sample_text = "This is a test document for validation."
                validation_result = streamlit_app.validate_ontology_with_text(ontology, sample_text)
                validation_working = "entities_found" in validation_result
            else:
                validation_working = False
            
            # Test ontology refinement
            if ontology:
                refinement_request = "Add more entity types"
                refined_ontology = streamlit_app.refine_ontology_with_gemini(ontology, refinement_request)
                refinement_working = refined_ontology is not None
            else:
                refinement_working = False
            
            # Test data conversion functions
            if ontology:
                try:
                    from src.ontology_generator import DomainOntology
                    # Test conversion function exists
                    conversion_working = hasattr(streamlit_app, 'domain_to_ui_ontology')
                except ImportError:
                    conversion_working = False
            else:
                conversion_working = False
            
            return {
                "ontology_generated": ontology_generated,
                "validation_working": validation_working,
                "refinement_working": refinement_working,
                "conversion_working": conversion_working,
                "workflow_integration": all([
                    ontology_generated,
                    validation_working,
                    refinement_working,
                    conversion_working
                ])
            }
            
        except Exception as e:
            return {
                "ontology_generated": False,
                "validation_working": False,
                "refinement_working": False,
                "conversion_working": False,
                "workflow_integration": False,
                "error": str(e)
            }
    
    def test_ui_error_handling(self) -> Dict[str, Any]:
        """Test UI error handling and recovery"""
        try:
            import streamlit_app
            
            # Test error handling in ontology generation
            try:
                # Test with invalid config
                invalid_config = {"temperature": "invalid"}
                ontology = streamlit_app.generate_ontology_with_gemini("test", invalid_config)
                generation_error_handling = True
            except:
                generation_error_handling = False
            
            # Test error handling in validation
            try:
                # Test with None ontology
                validation_result = streamlit_app.validate_ontology_with_text(None, "test")
                validation_error_handling = True
            except:
                validation_error_handling = False
            
            # Test error handling in refinement
            try:
                # Test with None ontology
                refined = streamlit_app.refine_ontology_with_gemini(None, "test")
                refinement_error_handling = True
            except:
                refinement_error_handling = False
            
            return {
                "generation_error_handling": generation_error_handling,
                "validation_error_handling": validation_error_handling,
                "refinement_error_handling": refinement_error_handling,
                "error_handling_working": all([
                    generation_error_handling,
                    validation_error_handling,
                    refinement_error_handling
                ])
            }
            
        except Exception as e:
            return {
                "generation_error_handling": False,
                "validation_error_handling": False,
                "refinement_error_handling": False,
                "error_handling_working": False,
                "error": str(e)
            }
    
    def test_ui_performance(self) -> Dict[str, Any]:
        """Test UI performance and responsiveness"""
        try:
            import streamlit_app
            
            start_time = time.time()
            
            # Test startup time
            streamlit_app.init_session_state()
            init_time = time.time() - start_time
            
            # Test ontology generation time
            gen_start = time.time()
            ontology = streamlit_app.generate_ontology_with_gemini("test domain", {})
            gen_time = time.time() - gen_start
            
            # Test UI rendering functions
            render_start = time.time()
            generator = streamlit_app.get_ontology_generator()
            storage = streamlit_app.get_storage_service()
            render_time = time.time() - render_start
            
            # Performance thresholds (in seconds)
            init_acceptable = init_time < 5.0
            gen_acceptable = gen_time < 30.0
            render_acceptable = render_time < 10.0
            
            return {
                "init_time": init_time,
                "generation_time": gen_time,
                "render_time": render_time,
                "init_acceptable": init_acceptable,
                "gen_acceptable": gen_acceptable,
                "render_acceptable": render_acceptable,
                "performance_acceptable": all([
                    init_acceptable,
                    gen_acceptable,
                    render_acceptable
                ])
            }
            
        except Exception as e:
            return {
                "init_time": -1,
                "generation_time": -1,
                "render_time": -1,
                "init_acceptable": False,
                "gen_acceptable": False,
                "render_acceptable": False,
                "performance_acceptable": False,
                "error": str(e)
            }
    
    def run_comprehensive_ui_tests(self) -> Dict[str, Any]:
        """Run all UI tests and return comprehensive results"""
        evidence_logger.clear_evidence_file()
        evidence_logger.log_task_start(
            "COMPREHENSIVE_UI_TESTING",
            "Complete Streamlit UI testing and verification"
        )
        
        # Setup test environment
        setup_success = self.setup_test_environment()
        if not setup_success:
            return {
                "setup_success": False,
                "error": "Failed to start Streamlit server"
            }
        
        try:
            # Run all test categories
            test_categories = {
                "startup": self.test_ui_startup,
                "components": self.test_ui_components,
                "workflow_integration": self.test_ui_workflow_integration,
                "error_handling": self.test_ui_error_handling,
                "performance": self.test_ui_performance
            }
            
            results = {"setup_success": True}
            
            for category, test_func in test_categories.items():
                evidence_logger.log_task_start(f"UI_TEST_{category.upper()}", f"Testing UI {category}")
                
                category_result = test_func()
                results[category] = category_result
                
                # Determine success for this category
                category_success = self._determine_category_success(category, category_result)
                
                evidence_logger.log_task_completion(
                    f"UI_TEST_{category.upper()}",
                    category_result,
                    category_success
                )
            
            # Overall assessment
            overall_success = self._assess_overall_ui_health(results)
            
            evidence_logger.log_verification_result(
                "COMPREHENSIVE_UI_TESTING",
                {
                    "overall_success": overall_success,
                    "detailed_results": results,
                    "ui_production_ready": overall_success
                }
            )
            
            return results
            
        finally:
            self.teardown_test_environment()
    
    def _determine_category_success(self, category: str, result: Dict[str, Any]) -> bool:
        """Determine if a test category was successful"""
        if "error" in result:
            return False
            
        if category == "startup":
            return result.get("startup_success", False) and result.get("ui_accessible", False)
        elif category == "components":
            return result.get("all_components_working", False)
        elif category == "workflow_integration":
            return result.get("workflow_integration", False)
        elif category == "error_handling":
            return result.get("error_handling_working", False)
        elif category == "performance":
            return result.get("performance_acceptable", False)
        
        return False
    
    def _assess_overall_ui_health(self, results: Dict[str, Any]) -> bool:
        """Assess overall UI health and production readiness"""
        critical_categories = ["startup", "components"]
        important_categories = ["workflow_integration", "error_handling"]
        
        # All critical categories must pass
        for category in critical_categories:
            if not self._determine_category_success(category, results.get(category, {})):
                return False
        
        # At least 75% of important categories must pass
        important_passed = sum(
            1 for category in important_categories
            if self._determine_category_success(category, results.get(category, {}))
        )
        
        return important_passed >= len(important_categories) * 0.75


def main():
    """Run comprehensive UI testing"""
    print("🚀 Starting Comprehensive Streamlit UI Testing...")
    
    tester = StreamlitTester()
    results = tester.run_comprehensive_ui_tests()
    
    if results.get("overall_success", False):
        print("✅ ALL UI TESTS PASSED - Streamlit UI is production ready!")
    else:
        print("❌ SOME UI TESTS FAILED - Check detailed results in Evidence.md")
    
    # Print summary
    print("\n📊 UI Test Summary:")
    for category, result in results.items():
        if category == "setup_success":
            continue
        success = tester._determine_category_success(category, result)
        status = "✅" if success else "❌"
        print(f"  {status} {category.replace('_', ' ').title()}: {'PASS' if success else 'FAIL'}")
    
    print("\n📁 Detailed results saved to Evidence.md")
    return results.get("overall_success", False)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)