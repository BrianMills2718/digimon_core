"""
GraphRAG Integration Testing Framework

This framework provides comprehensive integration testing for the GraphRAG system,
focusing on cross-component compatibility and preventing integration failures.
"""

import time
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback

from src.core.graphrag_phase_interface import (
    ProcessingRequest, PhaseResult, PhaseStatus, get_available_phases, execute_phase
)
from src.core.phase_adapters import initialize_phase_adapters
from src.ui.ui_phase_adapter import get_ui_phase_manager, process_document_with_phase


@dataclass
class IntegrationTestResult:
    """Result of an integration test"""
    test_name: str
    test_type: str
    status: str  # "pass", "fail", "skip"
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass 
class IntegrationTestSuite:
    """Collection of integration test results"""
    suite_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tests: List[IntegrationTestResult] = None
    
    def __post_init__(self):
        if self.tests is None:
            self.tests = []
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def summary(self) -> Dict[str, int]:
        passed = sum(1 for t in self.tests if t.status == "pass")
        failed = sum(1 for t in self.tests if t.status == "fail")
        skipped = sum(1 for t in self.tests if t.status == "skip")
        return {"total": len(self.tests), "passed": passed, "failed": failed, "skipped": skipped}


class IntegrationTester:
    """Main integration testing framework"""
    
    def __init__(self, test_data_dir: str = "examples/pdfs"):
        self.test_data_dir = Path(test_data_dir)
        self.temp_dir = None
        self.results = []
        
    def setup(self):
        """Setup test environment"""
        # Create temporary directory for test outputs
        self.temp_dir = Path(tempfile.mkdtemp(prefix="graphrag_integration_"))
        
        # Initialize phase system
        success = initialize_phase_adapters()
        if not success:
            raise RuntimeError("Failed to initialize phase adapters for testing")
        
        print(f"✅ Integration test environment setup complete")
        print(f"   Temp directory: {self.temp_dir}")
        print(f"   Available phases: {get_available_phases()}")
    
    def teardown(self):
        """Cleanup test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"✅ Cleanup complete: {self.temp_dir}")
    
    def run_full_integration_suite(self) -> IntegrationTestSuite:
        """Run the complete integration test suite"""
        suite = IntegrationTestSuite(
            suite_name="GraphRAG Full Integration Test",
            start_time=datetime.now()
        )
        
        print("🧪 Running GraphRAG Integration Test Suite")
        print("=" * 60)
        
        # Test categories
        test_categories = [
            ("Phase Interface Compatibility", self._test_phase_interface_compatibility),
            ("Cross-Phase Data Flow", self._test_cross_phase_data_flow),
            ("UI Integration", self._test_ui_integration),
            ("Error Handling", self._test_error_handling),
            ("Performance Baseline", self._test_performance_baseline),
            ("Service Dependencies", self._test_service_dependencies)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 40)
            
            try:
                category_results = test_func()
                suite.tests.extend(category_results)
                
                # Summary for this category
                passed = sum(1 for r in category_results if r.status == "pass")
                total = len(category_results)
                print(f"   Results: {passed}/{total} passed")
                
            except Exception as e:
                error_result = IntegrationTestResult(
                    test_name=f"{category_name} (Category Error)",
                    test_type="category",
                    status="fail",
                    execution_time=0.0,
                    details={},
                    error_message=str(e)
                )
                suite.tests.append(error_result)
                print(f"   ❌ Category failed: {e}")
        
        suite.end_time = datetime.now()
        return suite
    
    def _test_phase_interface_compatibility(self) -> List[IntegrationTestResult]:
        """Test that all phases implement the interface correctly"""
        results = []
        phases = get_available_phases()
        
        for phase_name in phases:
            start_time = time.time()
            
            try:
                # Test phase can be retrieved
                from src.core.graphrag_phase_interface import phase_registry
                phase = phase_registry.get_phase(phase_name)
                
                if not phase:
                    results.append(IntegrationTestResult(
                        test_name=f"Phase Retrieval: {phase_name}",
                        test_type="interface",
                        status="fail",
                        execution_time=time.time() - start_time,
                        details={},
                        error_message="Phase not found in registry"
                    ))
                    continue
                
                # Test required methods exist
                required_methods = ['execute', 'get_capabilities', 'validate_input', 'get_phase_info']
                missing_methods = []
                
                for method in required_methods:
                    if not hasattr(phase, method) or not callable(getattr(phase, method)):
                        missing_methods.append(method)
                
                if missing_methods:
                    results.append(IntegrationTestResult(
                        test_name=f"Interface Methods: {phase_name}",
                        test_type="interface", 
                        status="fail",
                        execution_time=time.time() - start_time,
                        details={"missing_methods": missing_methods},
                        error_message=f"Missing methods: {missing_methods}"
                    ))
                else:
                    # Test method calls work
                    capabilities = phase.get_capabilities()
                    phase_info = phase.get_phase_info()
                    
                    # Test validation with sample request
                    sample_request = ProcessingRequest(
                        documents=["test.pdf"],
                        queries=["Test query"],
                        workflow_id="test"
                    )
                    validation_errors = phase.validate_input(sample_request)
                    
                    results.append(IntegrationTestResult(
                        test_name=f"Interface Compliance: {phase_name}",
                        test_type="interface",
                        status="pass",
                        execution_time=time.time() - start_time,
                        details={
                            "capabilities_count": len(capabilities),
                            "phase_info": phase_info,
                            "validation_working": isinstance(validation_errors, list)
                        }
                    ))
                    
            except Exception as e:
                results.append(IntegrationTestResult(
                    test_name=f"Interface Error: {phase_name}",
                    test_type="interface",
                    status="fail", 
                    execution_time=time.time() - start_time,
                    details={},
                    error_message=str(e)
                ))
        
        return results
    
    def _test_cross_phase_data_flow(self) -> List[IntegrationTestResult]:
        """Test data compatibility between phases"""
        results = []
        
        # Test phase result format consistency
        start_time = time.time()
        
        try:
            phases = get_available_phases()
            
            # Test that all phases return PhaseResult with same structure
            for phase_name in phases:
                if "Phase 3" in phase_name:  # Skip unimplemented phases
                    continue
                    
                # Create test request
                test_request = ProcessingRequest(
                    documents=[],  # Empty for validation test
                    queries=["Test"],
                    workflow_id="data_flow_test"
                )
                
                # Test validation returns list
                phase = phase_registry.get_phase(phase_name)
                validation_result = phase.validate_input(test_request)
                
                if not isinstance(validation_result, list):
                    results.append(IntegrationTestResult(
                        test_name=f"Validation Format: {phase_name}",
                        test_type="data_flow",
                        status="fail",
                        execution_time=time.time() - start_time,
                        details={},
                        error_message="Validation should return list of errors"
                    ))
                else:
                    results.append(IntegrationTestResult(
                        test_name=f"Validation Format: {phase_name}",
                        test_type="data_flow", 
                        status="pass",
                        execution_time=time.time() - start_time,
                        details={"validation_errors": len(validation_result)}
                    ))
            
        except Exception as e:
            results.append(IntegrationTestResult(
                test_name="Cross-Phase Data Flow",
                test_type="data_flow",
                status="fail",
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return results
    
    def _test_ui_integration(self) -> List[IntegrationTestResult]:
        """Test UI integration with phase system"""
        results = []
        
        # Test UI adapter initialization
        start_time = time.time()
        
        try:
            manager = get_ui_phase_manager()
            
            if not manager.is_initialized():
                results.append(IntegrationTestResult(
                    test_name="UI Manager Initialization", 
                    test_type="ui_integration",
                    status="fail",
                    execution_time=time.time() - start_time,
                    details={},
                    error_message="UI manager failed to initialize"
                ))
            else:
                # Test UI can see all phases
                ui_phases = manager.get_available_phases()
                core_phases = get_available_phases()
                
                missing_phases = set(core_phases) - set(ui_phases)
                
                if missing_phases:
                    results.append(IntegrationTestResult(
                        test_name="UI Phase Visibility",
                        test_type="ui_integration", 
                        status="fail",
                        execution_time=time.time() - start_time,
                        details={"missing_phases": list(missing_phases)},
                        error_message=f"UI missing phases: {missing_phases}"
                    ))
                else:
                    results.append(IntegrationTestResult(
                        test_name="UI Phase Visibility",
                        test_type="ui_integration",
                        status="pass",
                        execution_time=time.time() - start_time,
                        details={"ui_phases": len(ui_phases), "core_phases": len(core_phases)}
                    ))
                
                # Test UI processing interface
                ui_result = process_document_with_phase(
                    phase_name="Phase 1: Basic",
                    file_path="nonexistent.pdf", 
                    filename="test.pdf",
                    queries=["Test query"]
                )
                
                # Should fail gracefully
                if ui_result.status == "error" and "not found" in (ui_result.error_message or "").lower():
                    results.append(IntegrationTestResult(
                        test_name="UI Error Handling",
                        test_type="ui_integration",
                        status="pass", 
                        execution_time=time.time() - start_time,
                        details={"error_handled": True}
                    ))
                else:
                    results.append(IntegrationTestResult(
                        test_name="UI Error Handling",
                        test_type="ui_integration",
                        status="fail",
                        execution_time=time.time() - start_time,
                        details={"unexpected_result": ui_result.status},
                        error_message="UI should handle missing file gracefully"
                    ))
                    
        except Exception as e:
            results.append(IntegrationTestResult(
                test_name="UI Integration Error",
                test_type="ui_integration",
                status="fail",
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return results
    
    def _test_error_handling(self) -> List[IntegrationTestResult]:
        """Test error handling across the system"""
        results = []
        
        # Test various error conditions
        error_tests = [
            ("Missing File", {"documents": ["missing.pdf"], "queries": ["Test"]}),
            ("Empty Documents", {"documents": [], "queries": ["Test"]}),
            ("Empty Queries", {"documents": ["test.pdf"], "queries": []}),
            ("Invalid Phase", {"phase": "Invalid Phase", "documents": ["test.pdf"], "queries": ["Test"]})
        ]
        
        for test_name, test_params in error_tests:
            start_time = time.time()
            
            try:
                if "phase" in test_params:
                    # Test invalid phase
                    try:
                        execute_phase(test_params["phase"], ProcessingRequest(
                            documents=test_params["documents"],
                            queries=test_params["queries"],
                            workflow_id="error_test"
                        ))
                        # Should have failed
                        results.append(IntegrationTestResult(
                            test_name=f"Error Test: {test_name}",
                            test_type="error_handling",
                            status="fail",
                            execution_time=time.time() - start_time,
                            details={},
                            error_message="Expected error was not raised"
                        ))
                    except ValueError:
                        # Expected error
                        results.append(IntegrationTestResult(
                            test_name=f"Error Test: {test_name}",
                            test_type="error_handling",
                            status="pass", 
                            execution_time=time.time() - start_time,
                            details={"error_type": "ValueError"}
                        ))
                else:
                    # Test validation errors
                    request = ProcessingRequest(
                        documents=test_params["documents"],
                        queries=test_params["queries"],
                        workflow_id="error_test"
                    )
                    
                    phase = phase_registry.get_phase("Phase 1: Basic")
                    errors = phase.validate_input(request)
                    
                    if errors:
                        results.append(IntegrationTestResult(
                            test_name=f"Error Test: {test_name}",
                            test_type="error_handling",
                            status="pass",
                            execution_time=time.time() - start_time,
                            details={"validation_errors": len(errors)}
                        ))
                    else:
                        results.append(IntegrationTestResult(
                            test_name=f"Error Test: {test_name}",
                            test_type="error_handling",
                            status="fail",
                            execution_time=time.time() - start_time,
                            details={},
                            error_message="Expected validation errors not found"
                        ))
                        
            except Exception as e:
                results.append(IntegrationTestResult(
                    test_name=f"Error Test: {test_name}",
                    test_type="error_handling",
                    status="fail",
                    execution_time=time.time() - start_time,
                    details={},
                    error_message=str(e)
                ))
        
        return results
    
    def _test_performance_baseline(self) -> List[IntegrationTestResult]:
        """Test basic performance metrics"""
        results = []
        
        # Test phase initialization time
        start_time = time.time()
        
        try:
            # Re-initialize and time it
            init_start = time.time()
            success = initialize_phase_adapters()
            init_time = time.time() - init_start
            
            if success and init_time < 5.0:  # Should initialize in under 5 seconds
                results.append(IntegrationTestResult(
                    test_name="Phase Initialization Performance",
                    test_type="performance",
                    status="pass",
                    execution_time=init_time,
                    details={"init_time_seconds": init_time}
                ))
            else:
                results.append(IntegrationTestResult(
                    test_name="Phase Initialization Performance",
                    test_type="performance",
                    status="fail",
                    execution_time=init_time,
                    details={"init_time_seconds": init_time},
                    error_message=f"Initialization too slow: {init_time:.2f}s or failed"
                ))
                
        except Exception as e:
            results.append(IntegrationTestResult(
                test_name="Performance Baseline Error",
                test_type="performance",
                status="fail",
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return results
    
    def _test_service_dependencies(self) -> List[IntegrationTestResult]:
        """Test service dependency handling"""
        results = []
        
        # Test that phases report their dependencies correctly
        start_time = time.time()
        
        try:
            phases = get_available_phases()
            
            for phase_name in phases:
                phase = phase_registry.get_phase(phase_name)
                capabilities = phase.get_capabilities()
                
                required_services = capabilities.get("required_services", [])
                
                # Validate service names
                valid_services = ["neo4j", "sqlite", "openai", "google", "qdrant"]
                invalid_services = [s for s in required_services if s not in valid_services]
                
                if invalid_services:
                    results.append(IntegrationTestResult(
                        test_name=f"Service Dependencies: {phase_name}",
                        test_type="dependencies",
                        status="fail",
                        execution_time=time.time() - start_time,
                        details={"invalid_services": invalid_services},
                        error_message=f"Unknown services: {invalid_services}"
                    ))
                else:
                    results.append(IntegrationTestResult(
                        test_name=f"Service Dependencies: {phase_name}",
                        test_type="dependencies", 
                        status="pass",
                        execution_time=time.time() - start_time,
                        details={"required_services": required_services}
                    ))
                    
        except Exception as e:
            results.append(IntegrationTestResult(
                test_name="Service Dependencies Error",
                test_type="dependencies",
                status="fail",
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return results
    
    def generate_report(self, suite: IntegrationTestSuite) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("GraphRAG Integration Test Report")
        report.append("=" * 50)
        report.append(f"Suite: {suite.suite_name}")
        report.append(f"Start: {suite.start_time}")
        report.append(f"End: {suite.end_time}")
        report.append(f"Duration: {suite.duration:.2f} seconds")
        report.append("")
        
        # Summary
        summary = suite.summary
        report.append("Summary:")
        report.append(f"  Total tests: {summary['total']}")
        report.append(f"  Passed: {summary['passed']}")
        report.append(f"  Failed: {summary['failed']}")
        report.append(f"  Skipped: {summary['skipped']}")
        report.append(f"  Success rate: {(summary['passed']/summary['total']*100):.1f}%")
        report.append("")
        
        # Group by test type
        by_type = {}
        for test in suite.tests:
            test_type = test.test_type
            if test_type not in by_type:
                by_type[test_type] = []
            by_type[test_type].append(test)
        
        for test_type, tests in by_type.items():
            report.append(f"{test_type.upper()} Tests:")
            report.append("-" * 30)
            
            for test in tests:
                status_icon = {"pass": "✅", "fail": "❌", "skip": "⏭️"}[test.status]
                report.append(f"  {status_icon} {test.test_name} ({test.execution_time:.3f}s)")
                
                if test.status == "fail" and test.error_message:
                    report.append(f"      Error: {test.error_message}")
                    
                if test.details:
                    key_details = {k: v for k, v in test.details.items() if k in ['validation_errors', 'missing_methods', 'init_time_seconds']}
                    if key_details:
                        report.append(f"      Details: {key_details}")
            
            report.append("")
        
        return "\n".join(report)


def run_integration_tests(test_data_dir: str = "examples/pdfs") -> IntegrationTestSuite:
    """Run the full integration test suite"""
    tester = IntegrationTester(test_data_dir)
    
    try:
        tester.setup()
        suite = tester.run_full_integration_suite()
        return suite
    finally:
        tester.teardown()


if __name__ == "__main__":
    # Run integration tests when called directly
    suite = run_integration_tests()
    
    tester = IntegrationTester()
    report = tester.generate_report(suite)
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # Exit with appropriate code
    summary = suite.summary
    if summary['failed'] == 0:
        print(f"\n🎉 All {summary['passed']} integration tests passed!")
        exit(0)
    else:
        print(f"\n❌ {summary['failed']} integration tests failed")
        exit(1)