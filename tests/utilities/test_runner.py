"""Comprehensive Test Runner for KGAS

Provides unified test execution, coverage reporting, and test result analysis.
Ensures >95% test coverage across all critical components.
"""

import os
import sys
import subprocess
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logging_config import get_logger

logger = get_logger("tests.test_runner")


@dataclass
class TestResult:
    """Test execution result"""
    test_suite: str
    passed: int
    failed: int
    skipped: int
    total: int
    duration: float
    coverage: float
    errors: List[str]


@dataclass
class CoverageReport:
    """Coverage analysis report"""
    total_coverage: float
    module_coverage: Dict[str, float]
    uncovered_lines: Dict[str, List[int]]
    critical_modules_coverage: Dict[str, float]
    coverage_target_met: bool


class TestRunner:
    """Comprehensive test runner with coverage analysis"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.logger = get_logger("tests.test_runner")
        
        # Critical modules that must have >95% coverage
        self.critical_modules = [
            "src/core/config_manager.py",
            "src/core/service_manager.py",
            "src/core/enhanced_service_manager.py",
            "src/core/dependency_injection.py",
            "src/core/unified_service_interface.py",
            "src/core/security_validation.py",
            "src/core/anyio_api_client.py",
            "src/core/orchestration/pipeline_orchestrator.py"
        ]
        
        # Test suites to run
        self.test_suites = {
            "unit": "tests/unit/",
            "integration": "tests/integration/",
            "functional": "tests/functional/",
            "performance": "tests/performance/",
            "security": "tests/security/",
            "reliability": "tests/reliability/"
        }
        
    def run_all_tests(self, coverage_threshold: float = 95.0) -> Dict[str, Any]:
        """Run all test suites with coverage analysis
        
        Args:
            coverage_threshold: Minimum coverage percentage required
            
        Returns:
            Comprehensive test results
        """
        self.logger.info("Starting comprehensive test execution")
        start_time = time.time()
        
        # Install required testing packages
        self._ensure_test_dependencies()
        
        # Run individual test suites
        suite_results = {}
        for suite_name, suite_path in self.test_suites.items():
            self.logger.info(f"Running {suite_name} tests...")
            result = self._run_test_suite(suite_name, suite_path)
            suite_results[suite_name] = result
            
        # Generate comprehensive coverage report
        coverage_report = self._generate_coverage_report()
        
        total_time = time.time() - start_time
        
        # Compile overall results
        overall_results = {
            "execution_summary": {
                "total_time": total_time,
                "suites_run": len(suite_results),
                "timestamp": datetime.now().isoformat()
            },
            "suite_results": suite_results,
            "coverage_report": coverage_report,
            "compliance": self._check_compliance(suite_results, coverage_report, coverage_threshold),
            "recommendations": self._generate_recommendations(suite_results, coverage_report)
        }
        
        self.logger.info(f"Test execution complete in {total_time:.2f}s")
        return overall_results
        
    def _ensure_test_dependencies(self):
        """Ensure required testing packages are installed"""
        required_packages = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.0.0"  # For parallel test execution
        ]
        
        for package in required_packages:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "show", package.split(">=")[0]
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                self.logger.info(f"Installing {package}...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True)
                
    def _run_test_suite(self, suite_name: str, suite_path: str) -> TestResult:
        """Run a specific test suite
        
        Args:
            suite_name: Name of the test suite
            suite_path: Path to test suite directory
            
        Returns:
            Test execution results
        """
        full_path = self.project_root / suite_path
        
        if not full_path.exists():
            self.logger.warning(f"Test suite path not found: {full_path}")
            return TestResult(
                test_suite=suite_name,
                passed=0, failed=0, skipped=0, total=0,
                duration=0.0, coverage=0.0,
                errors=[f"Test suite path not found: {suite_path}"]
            )
            
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(full_path),
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--cov=src",  # Coverage for src directory (relative path)
            "--cov-report=term-missing",  # Show missing lines
            "--cov-report=json:coverage.json",  # JSON report for parsing
            "--cov-config=.coveragerc",  # Use coverage config file
            "--maxfail=3"  # Stop after 3 failures for faster feedback
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per suite
            )
            
            duration = time.time() - start_time
            
            # Parse test results
            test_stats = self._parse_pytest_output(result.stdout)
            coverage = self._extract_coverage_from_output(result.stdout)
            
            errors = []
            if result.returncode != 0:
                errors.append(f"Test suite failed with exit code {result.returncode}")
                if result.stderr:
                    errors.append(result.stderr)
                    
            return TestResult(
                test_suite=suite_name,
                passed=test_stats.get("passed", 0),
                failed=test_stats.get("failed", 0),
                skipped=test_stats.get("skipped", 0),
                total=test_stats.get("total", 0),
                duration=duration,
                coverage=coverage,
                errors=errors
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_suite=suite_name,
                passed=0, failed=0, skipped=0, total=0,
                duration=300.0, coverage=0.0,
                errors=[f"Test suite timed out after 5 minutes"]
            )
        except Exception as e:
            return TestResult(
                test_suite=suite_name,
                passed=0, failed=0, skipped=0, total=0,
                duration=time.time() - start_time, coverage=0.0,
                errors=[f"Test execution error: {str(e)}"]
            )
            
    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test statistics"""
        stats = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
        
        # Look for summary line like "5 passed, 1 failed, 2 skipped in 1.23s"
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line or 'failed' in line or 'skipped' in line:
                if ' in ' in line and 's' in line:  # Summary line
                    parts = line.split(',')
                    for part in parts:
                        part = part.strip()
                        if 'passed' in part:
                            stats["passed"] = int(part.split()[0])
                        elif 'failed' in part:
                            stats["failed"] = int(part.split()[0])
                        elif 'skipped' in part:
                            stats["skipped"] = int(part.split()[0])
                    break
                    
        stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]
        return stats
        
    def _extract_coverage_from_output(self, output: str) -> float:
        """Extract coverage percentage from pytest output"""
        lines = output.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                # Look for line like "TOTAL     1234    567    76%"
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        try:
                            return float(part.replace('%', ''))
                        except ValueError:
                            continue
        return 0.0
        
    def _generate_coverage_report(self) -> CoverageReport:
        """Generate comprehensive coverage report"""
        coverage_file = self.project_root / "coverage.json"
        
        if not coverage_file.exists():
            return CoverageReport(
                total_coverage=0.0,
                module_coverage={},
                uncovered_lines={},
                critical_modules_coverage={},
                coverage_target_met=False
            )
            
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
                
            total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
            
            # Extract module-specific coverage
            module_coverage = {}
            uncovered_lines = {}
            
            for file_path, file_data in coverage_data.get('files', {}).items():
                # Convert absolute path to relative
                rel_path = os.path.relpath(file_path, self.project_root)
                module_coverage[rel_path] = file_data.get('summary', {}).get('percent_covered', 0.0)
                
                # Get uncovered lines
                missing_lines = file_data.get('missing_lines', [])
                if missing_lines:
                    uncovered_lines[rel_path] = missing_lines
                    
            # Check critical modules coverage
            critical_modules_coverage = {}
            for module in self.critical_modules:
                if module in module_coverage:
                    critical_modules_coverage[module] = module_coverage[module]
                else:
                    critical_modules_coverage[module] = 0.0
                    
            # Check if coverage target is met
            coverage_target_met = (
                total_coverage >= 95.0 and
                all(cov >= 95.0 for cov in critical_modules_coverage.values())
            )
            
            return CoverageReport(
                total_coverage=total_coverage,
                module_coverage=module_coverage,
                uncovered_lines=uncovered_lines,
                critical_modules_coverage=critical_modules_coverage,
                coverage_target_met=coverage_target_met
            )
            
        except Exception as e:
            self.logger.error(f"Error generating coverage report: {e}")
            return CoverageReport(
                total_coverage=0.0,
                module_coverage={},
                uncovered_lines={},
                critical_modules_coverage={},
                coverage_target_met=False
            )
            
    def _check_compliance(self, suite_results: Dict[str, TestResult], 
                         coverage_report: CoverageReport, 
                         coverage_threshold: float) -> Dict[str, Any]:
        """Check compliance with testing requirements"""
        total_tests = sum(r.total for r in suite_results.values())
        total_passed = sum(r.passed for r in suite_results.values())
        total_failed = sum(r.failed for r in suite_results.values())
        
        # Calculate overall pass rate
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Check compliance criteria
        compliance_checks = {
            "all_tests_pass": total_failed == 0,
            "coverage_target_met": coverage_report.coverage_target_met,
            "critical_modules_covered": all(
                cov >= coverage_threshold 
                for cov in coverage_report.critical_modules_coverage.values()
            ),
            "minimum_test_count": total_tests >= 50,  # Minimum test requirement
            "no_test_suite_failures": all(
                len(r.errors) == 0 for r in suite_results.values()
            )
        }
        
        overall_compliance = all(compliance_checks.values())
        
        return {
            "overall_compliance": overall_compliance,
            "pass_rate": pass_rate,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "compliance_checks": compliance_checks,
            "coverage_score": coverage_report.total_coverage
        }
        
    def _generate_recommendations(self, suite_results: Dict[str, TestResult],
                                coverage_report: CoverageReport) -> List[str]:
        """Generate testing recommendations"""
        recommendations = []
        
        # Check for failed tests
        failed_suites = [name for name, result in suite_results.items() if result.failed > 0]
        if failed_suites:
            recommendations.append(f"Fix failing tests in: {', '.join(failed_suites)}")
            
        # Check coverage
        if coverage_report.total_coverage < 95.0:
            recommendations.append(f"Increase overall coverage from {coverage_report.total_coverage:.1f}% to 95%")
            
        # Check critical modules
        low_coverage_modules = [
            module for module, cov in coverage_report.critical_modules_coverage.items()
            if cov < 95.0
        ]
        if low_coverage_modules:
            recommendations.append(f"Improve coverage for critical modules: {', '.join(low_coverage_modules)}")
            
        # Check for missing test suites
        empty_suites = [name for name, result in suite_results.items() if result.total == 0]
        if empty_suites:
            recommendations.append(f"Add tests to empty suites: {', '.join(empty_suites)}")
            
        if not recommendations:
            recommendations.append("All testing requirements met! 🎉")
            
        return recommendations
        
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable test report"""
        report = []
        report.append("=" * 60)
        report.append("KGAS COMPREHENSIVE TEST REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {results['execution_summary']['timestamp']}")
        report.append(f"Total Execution Time: {results['execution_summary']['total_time']:.2f}s")
        report.append("")
        
        # Compliance status
        compliance = results['compliance']
        status = "✅ PASS" if compliance['overall_compliance'] else "❌ FAIL"
        report.append(f"Overall Status: {status}")
        report.append(f"Pass Rate: {compliance['pass_rate']:.1f}%")
        report.append(f"Coverage Score: {compliance['coverage_score']:.1f}%")
        report.append("")
        
        # Suite results
        report.append("TEST SUITE RESULTS:")
        report.append("-" * 30)
        for suite_name, result in results['suite_results'].items():
            status = "✅" if result.failed == 0 and len(result.errors) == 0 else "❌"
            report.append(f"{status} {suite_name}: {result.passed}P/{result.failed}F/{result.skipped}S "
                         f"({result.duration:.1f}s, {result.coverage:.1f}% cov)")
            
        report.append("")
        
        # Coverage details
        report.append("CRITICAL MODULE COVERAGE:")
        report.append("-" * 35)
        coverage_report = results['coverage_report']
        if hasattr(coverage_report, 'critical_modules_coverage'):
            for module, coverage in coverage_report.critical_modules_coverage.items():
                status = "✅" if coverage >= 95.0 else "❌"
                report.append(f"{status} {module}: {coverage:.1f}%")
        else:
            report.append("No coverage data available")
            
        report.append("")
        
        # Recommendations
        if results['recommendations']:
            report.append("RECOMMENDATIONS:")
            report.append("-" * 20)
            for i, rec in enumerate(results['recommendations'], 1):
                report.append(f"{i}. {rec}")
                
        return "\n".join(report)


def run_comprehensive_tests() -> Dict[str, Any]:
    """Run comprehensive test suite
    
    Returns:
        Complete test results
    """
    runner = TestRunner()
    return runner.run_all_tests()


if __name__ == "__main__":
    print("Running KGAS Comprehensive Test Suite...")
    results = run_comprehensive_tests()
    
    # Generate and display report
    runner = TestRunner()
    report = runner.generate_test_report(results)
    print(report)
    
    # Exit with appropriate code
    exit_code = 0 if results['compliance']['overall_compliance'] else 1
    sys.exit(exit_code)