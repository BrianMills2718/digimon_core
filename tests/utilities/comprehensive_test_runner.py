"""
Comprehensive Test Runner for Production-Ready Testing

Runs all test categories with detailed reporting and analysis.
Supports functional, integration, performance, and error scenario testing.
"""

import os
import sys
import subprocess
import time
import json
import psutil
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logging_config import get_logger

logger = get_logger("tests.comprehensive_test_runner")


@dataclass
class TestSuiteResult:
    """Comprehensive test suite result"""
    suite_name: str
    category: str
    passed: int
    failed: int
    skipped: int
    errors: int
    total: int
    duration: float
    coverage: float
    memory_peak: int
    cpu_avg: float
    test_details: List[Dict[str, Any]]
    error_messages: List[str]


@dataclass
class ComprehensiveTestReport:
    """Complete test execution report"""
    execution_time: float
    total_tests: int
    total_passed: int
    total_failed: int
    total_errors: int
    overall_coverage: float
    suite_results: List[TestSuiteResult]
    performance_metrics: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    production_readiness: Dict[str, bool]


class ComprehensiveTestRunner:
    """Comprehensive test runner with full analysis"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.logger = get_logger("tests.comprehensive_test_runner")
        
        # Test suite definitions
        self.test_suites = {
            # Core unit tests
            "unit_core": {
                "path": "tests/unit/core/",
                "category": "unit",
                "markers": ["unit"],
                "timeout": 120,
                "critical": True
            },
            
            # Functional tests with real execution
            "functional_real": {
                "path": "tests/functional/",
                "category": "functional", 
                "markers": ["functional"],
                "timeout": 300,
                "critical": True
            },
            
            # Integration tests across components
            "integration_complete": {
                "path": "tests/integration/",
                "category": "integration",
                "markers": ["integration"],
                "timeout": 600,
                "critical": True
            },
            
            # Performance benchmarks
            "performance_benchmarks": {
                "path": "tests/performance/",
                "category": "performance",
                "markers": ["performance"],
                "timeout": 900,
                "critical": False
            },
            
            # Error scenario testing
            "error_scenarios": {
                "path": "tests/error_scenarios/",
                "category": "error_handling",
                "markers": ["error_scenarios"],
                "timeout": 300,
                "critical": True
            }
        }
        
        # Production readiness criteria
        self.production_criteria = {
            "minimum_test_count": 150,
            "minimum_coverage": 75.0,
            "maximum_failure_rate": 0.05,
            "required_test_categories": ["unit", "functional", "integration"],
            "performance_requirements": {
                "max_avg_test_time": 5.0,
                "max_memory_usage_gb": 2.0,
                "max_cpu_usage_percent": 80.0
            }
        }
    
    def run_comprehensive_tests(self, include_performance: bool = True, 
                               include_error_scenarios: bool = True) -> ComprehensiveTestReport:
        """Run comprehensive test suite with detailed analysis"""
        self.logger.info("Starting comprehensive test execution")
        start_time = time.time()
        
        # System resource monitoring setup
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Install test dependencies
        self._ensure_test_dependencies()
        
        # Run test suites
        suite_results = []
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for suite_name, suite_config in self.test_suites.items():
            # Skip performance tests if not requested
            if not include_performance and suite_config["category"] == "performance":
                continue
                
            # Skip error scenario tests if not requested
            if not include_error_scenarios and suite_config["category"] == "error_handling":
                continue
            
            self.logger.info(f"Running test suite: {suite_name}")
            
            result = self._run_test_suite_comprehensive(suite_name, suite_config)
            suite_results.append(result)
            
            total_tests += result.total
            total_passed += result.passed
            total_failed += result.failed
            total_errors += result.errors
        
        # Generate comprehensive coverage report
        overall_coverage = self._generate_comprehensive_coverage_report()
        
        # Calculate performance metrics
        peak_memory = process.memory_info().rss
        memory_used_gb = (peak_memory - initial_memory) / (1024 ** 3)
        
        performance_metrics = {
            "total_execution_time": time.time() - start_time,
            "memory_used_gb": memory_used_gb,
            "peak_memory_mb": peak_memory / (1024 ** 2),
            "avg_test_duration": self._calculate_avg_test_duration(suite_results),
            "throughput_tests_per_second": total_tests / (time.time() - start_time)
        }
        
        # Quality assessment
        quality_assessment = self._assess_test_quality(suite_results)
        
        # Production readiness check
        production_readiness = self._check_production_readiness(
            suite_results, overall_coverage, performance_metrics
        )
        
        # Compile comprehensive report
        report = ComprehensiveTestReport(
            execution_time=time.time() - start_time,
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            total_errors=total_errors,
            overall_coverage=overall_coverage,
            suite_results=suite_results,
            performance_metrics=performance_metrics,
            quality_assessment=quality_assessment,
            production_readiness=production_readiness
        )
        
        self.logger.info(f"Comprehensive test execution complete in {report.execution_time:.2f}s")
        return report
    
    def _run_test_suite_comprehensive(self, suite_name: str, 
                                    suite_config: Dict[str, Any]) -> TestSuiteResult:
        """Run a test suite with comprehensive monitoring"""
        suite_path = self.project_root / suite_config["path"]
        
        if not suite_path.exists():
            self.logger.warning(f"Test suite path not found: {suite_path}")
            return TestSuiteResult(
                suite_name=suite_name,
                category=suite_config["category"],
                passed=0, failed=0, skipped=0, errors=0, total=0,
                duration=0.0, coverage=0.0,
                memory_peak=0, cpu_avg=0.0,
                test_details=[], 
                error_messages=[f"Test suite path not found: {suite_path}"]
            )
        
        # Resource monitoring setup
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss
        cpu_measurements = []
        
        # Build comprehensive pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(suite_path),
            "-v",  # Verbose output
            "--tb=short",  # Short traceback
            f"--cov={self.project_root}/src",  # Coverage
            "--cov-report=json:coverage_temp.json",  # JSON coverage report
            "--cov-report=term-missing",  # Terminal coverage report
            "--json-report",  # JSON test report
            "--json-report-file=test_report_temp.json",
            f"--timeout={suite_config['timeout']}",  # Test timeout
        ]
        
        # Add markers if specified
        if suite_config.get("markers"):
            markers = " or ".join(suite_config["markers"])
            cmd.extend(["-m", markers])
        
        try:
            # Execute tests with monitoring
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=suite_config["timeout"] + 60  # Extra timeout buffer
            )
            
            # Monitor CPU during execution
            cpu_measurements.append(process.cpu_percent())
            
            duration = time.time() - start_time
            peak_memory = process.memory_info().rss
            memory_used = peak_memory - start_memory
            avg_cpu = sum(cpu_measurements) / len(cpu_measurements) if cpu_measurements else 0.0
            
            # Parse test results
            test_stats = self._parse_pytest_json_report()
            coverage = self._extract_coverage_from_json()
            test_details = self._extract_test_details()
            
            error_messages = []
            if result.returncode != 0:
                error_messages.append(f"Test suite failed with exit code {result.returncode}")
                if result.stderr:
                    error_messages.append(result.stderr)
            
            return TestSuiteResult(
                suite_name=suite_name,
                category=suite_config["category"],
                passed=test_stats.get("passed", 0),
                failed=test_stats.get("failed", 0),
                skipped=test_stats.get("skipped", 0),
                errors=test_stats.get("errors", 0),
                total=test_stats.get("total", 0),
                duration=duration,
                coverage=coverage,
                memory_peak=memory_used,
                cpu_avg=avg_cpu,
                test_details=test_details,
                error_messages=error_messages
            )
            
        except subprocess.TimeoutExpired:
            return TestSuiteResult(
                suite_name=suite_name,
                category=suite_config["category"],
                passed=0, failed=0, skipped=0, errors=1, total=0,
                duration=suite_config["timeout"], coverage=0.0,
                memory_peak=0, cpu_avg=0.0,
                test_details=[],
                error_messages=[f"Test suite timed out after {suite_config['timeout']}s"]
            )
        except Exception as e:
            return TestSuiteResult(
                suite_name=suite_name,
                category=suite_config["category"],
                passed=0, failed=0, skipped=0, errors=1, total=0,
                duration=time.time() - start_time, coverage=0.0,
                memory_peak=0, cpu_avg=0.0,
                test_details=[],
                error_messages=[f"Test execution error: {str(e)}"]
            )
    
    def _parse_pytest_json_report(self) -> Dict[str, int]:
        """Parse pytest JSON report for detailed statistics"""
        report_file = self.project_root / "test_report_temp.json"
        
        if not report_file.exists():
            return {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
        
        try:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            summary = report_data.get("summary", {})
            stats = {
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0), 
                "skipped": summary.get("skipped", 0),
                "errors": summary.get("error", 0),
                "total": summary.get("total", 0)
            }
            
            # Cleanup temp file
            report_file.unlink()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON report: {e}")
            return {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
    
    def _extract_coverage_from_json(self) -> float:
        """Extract coverage percentage from JSON coverage report"""
        coverage_file = self.project_root / "coverage_temp.json"
        
        if not coverage_file.exists():
            return 0.0
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
            
            # Cleanup temp file
            coverage_file.unlink()
            return total_coverage
            
        except Exception as e:
            self.logger.error(f"Error parsing coverage report: {e}")
            return 0.0
    
    def _extract_test_details(self) -> List[Dict[str, Any]]:
        """Extract detailed test information"""
        report_file = self.project_root / "test_report_temp.json"
        
        if not report_file.exists():
            return []
        
        try:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            test_details = []
            for test in report_data.get("tests", []):
                test_details.append({
                    "name": test.get("nodeid", "unknown"),
                    "outcome": test.get("outcome", "unknown"),
                    "duration": test.get("duration", 0.0),
                    "file": test.get("file", "unknown"),
                    "line": test.get("line", 0)
                })
            
            return test_details
            
        except Exception as e:
            self.logger.error(f"Error extracting test details: {e}")
            return []
    
    def _generate_comprehensive_coverage_report(self) -> float:
        """Generate comprehensive coverage report across all test suites"""
        try:
            # Run coverage measurement across all source files
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/unit/core/",
                "tests/functional/",
                "tests/integration/",
                f"--cov={self.project_root}/src",
                "--cov-report=json:comprehensive_coverage.json",
                "--cov-report=html:comprehensive_htmlcov",
                "--quiet"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Extract overall coverage
            coverage_file = self.project_root / "comprehensive_coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                overall_coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
                return overall_coverage
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive coverage: {e}")
        
        return 0.0
    
    def _calculate_avg_test_duration(self, suite_results: List[TestSuiteResult]) -> float:
        """Calculate average test duration across all suites"""
        total_duration = sum(r.duration for r in suite_results)
        total_tests = sum(r.total for r in suite_results)
        
        return total_duration / total_tests if total_tests > 0 else 0.0
    
    def _assess_test_quality(self, suite_results: List[TestSuiteResult]) -> Dict[str, Any]:
        """Assess overall test quality"""
        total_tests = sum(r.total for r in suite_results)
        total_passed = sum(r.passed for r in suite_results)
        total_failed = sum(r.failed for r in suite_results)
        
        pass_rate = total_passed / total_tests if total_tests > 0 else 0.0
        failure_rate = total_failed / total_tests if total_tests > 0 else 0.0
        
        # Assess test distribution across categories
        categories_covered = set(r.category for r in suite_results)
        
        # Calculate coverage variance across suites
        coverages = [r.coverage for r in suite_results if r.coverage > 0]
        avg_coverage = sum(coverages) / len(coverages) if coverages else 0.0
        
        return {
            "pass_rate": pass_rate,
            "failure_rate": failure_rate,
            "categories_covered": list(categories_covered),
            "category_count": len(categories_covered),
            "avg_coverage": avg_coverage,
            "test_distribution": {r.category: r.total for r in suite_results},
            "quality_score": self._calculate_quality_score(pass_rate, len(categories_covered), avg_coverage)
        }
    
    def _calculate_quality_score(self, pass_rate: float, category_count: int, avg_coverage: float) -> float:
        """Calculate overall test quality score (0-100)"""
        # Weighted quality score
        pass_weight = 0.4
        category_weight = 0.3  
        coverage_weight = 0.3
        
        pass_score = pass_rate * 100
        category_score = min(category_count / 5, 1.0) * 100  # Max score for 5+ categories
        coverage_score = avg_coverage
        
        quality_score = (
            pass_score * pass_weight +
            category_score * category_weight + 
            coverage_score * coverage_weight
        )
        
        return min(quality_score, 100.0)
    
    def _check_production_readiness(self, suite_results: List[TestSuiteResult], 
                                  overall_coverage: float,
                                  performance_metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Check production readiness criteria"""
        total_tests = sum(r.total for r in suite_results)
        total_failed = sum(r.failed for r in suite_results)
        failure_rate = total_failed / total_tests if total_tests > 0 else 1.0
        
        categories_covered = set(r.category for r in suite_results)
        required_categories = set(self.production_criteria["required_test_categories"])
        
        criteria = {
            "sufficient_test_count": total_tests >= self.production_criteria["minimum_test_count"],
            "adequate_coverage": overall_coverage >= self.production_criteria["minimum_coverage"],
            "low_failure_rate": failure_rate <= self.production_criteria["maximum_failure_rate"],
            "required_categories_covered": required_categories.issubset(categories_covered),
            "acceptable_performance": (
                performance_metrics["avg_test_duration"] <= self.production_criteria["performance_requirements"]["max_avg_test_time"] and
                performance_metrics["memory_used_gb"] <= self.production_criteria["performance_requirements"]["max_memory_usage_gb"]
            ),
            "critical_suites_passing": all(
                r.failed == 0 for r in suite_results 
                if self.test_suites.get(r.suite_name, {}).get("critical", False)
            )
        }
        
        criteria["overall_production_ready"] = all(criteria.values())
        
        return criteria
    
    def _ensure_test_dependencies(self):
        """Ensure all required testing packages are installed"""
        required_packages = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-json-report>=1.5.0",
            "pytest-timeout>=2.1.0",
            "pytest-xdist>=3.0.0",
            "psutil>=5.9.0"
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
    
    def generate_comprehensive_report(self, report: ComprehensiveTestReport) -> str:
        """Generate human-readable comprehensive test report"""
        lines = []
        lines.append("=" * 80)
        lines.append("COMPREHENSIVE TEST EXECUTION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Total Execution Time: {report.execution_time:.2f}s")
        lines.append("")
        
        # Overall Status
        overall_status = "✅ PRODUCTION READY" if report.production_readiness["overall_production_ready"] else "❌ NOT PRODUCTION READY"
        lines.append(f"Overall Status: {overall_status}")
        lines.append(f"Total Tests: {report.total_tests}")
        lines.append(f"Passed: {report.total_passed} | Failed: {report.total_failed} | Errors: {report.total_errors}")
        lines.append(f"Pass Rate: {(report.total_passed / report.total_tests * 100):.1f}%")
        lines.append(f"Overall Coverage: {report.overall_coverage:.1f}%")
        lines.append("")
        
        # Test Suite Results
        lines.append("TEST SUITE RESULTS:")
        lines.append("-" * 50)
        for result in report.suite_results:
            status = "✅" if result.failed == 0 and len(result.error_messages) == 0 else "❌"
            lines.append(
                f"{status} {result.suite_name} ({result.category}): "
                f"{result.passed}P/{result.failed}F/{result.skipped}S "
                f"({result.duration:.1f}s, {result.coverage:.1f}% cov, {result.memory_peak/1024/1024:.0f}MB)"
            )
        lines.append("")
        
        # Performance Metrics
        lines.append("PERFORMANCE METRICS:")
        lines.append("-" * 30)
        lines.append(f"Memory Used: {report.performance_metrics['memory_used_gb']:.2f} GB")
        lines.append(f"Peak Memory: {report.performance_metrics['peak_memory_mb']:.0f} MB")
        lines.append(f"Average Test Duration: {report.performance_metrics['avg_test_duration']:.2f}s")
        lines.append(f"Throughput: {report.performance_metrics['throughput_tests_per_second']:.1f} tests/s")
        lines.append("")
        
        # Quality Assessment
        lines.append("QUALITY ASSESSMENT:")
        lines.append("-" * 30)
        lines.append(f"Quality Score: {report.quality_assessment['quality_score']:.1f}/100")
        lines.append(f"Categories Covered: {', '.join(report.quality_assessment['categories_covered'])}")
        lines.append(f"Average Coverage: {report.quality_assessment['avg_coverage']:.1f}%")
        lines.append("")
        
        # Production Readiness
        lines.append("PRODUCTION READINESS:")
        lines.append("-" * 30)
        for criterion, status in report.production_readiness.items():
            status_icon = "✅" if status else "❌"
            lines.append(f"{status_icon} {criterion.replace('_', ' ').title()}")
        lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS:")
        lines.append("-" * 20)
        recommendations = self._generate_recommendations(report)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, report: ComprehensiveTestReport) -> List[str]:
        """Generate actionable recommendations based on test results"""
        recommendations = []
        
        # Coverage recommendations
        if report.overall_coverage < 75.0:
            recommendations.append(f"Increase test coverage from {report.overall_coverage:.1f}% to at least 75%")
        
        # Failure rate recommendations
        failure_rate = report.total_failed / report.total_tests if report.total_tests > 0 else 0
        if failure_rate > 0.05:
            recommendations.append(f"Fix failing tests - current failure rate {failure_rate:.1%} exceeds 5% threshold")
        
        # Performance recommendations
        if report.performance_metrics["avg_test_duration"] > 5.0:
            recommendations.append("Optimize test performance - average test duration exceeds 5 seconds")
        
        # Test count recommendations  
        if report.total_tests < 150:
            recommendations.append(f"Add more tests - current count {report.total_tests} below minimum 150")
        
        # Category coverage recommendations
        missing_categories = set(["unit", "functional", "integration"]) - set(report.quality_assessment["categories_covered"])
        if missing_categories:
            recommendations.append(f"Add missing test categories: {', '.join(missing_categories)}")
        
        if not recommendations:
            recommendations.append("All quality criteria met! System is production-ready 🎉")
        
        return recommendations


def main():
    """Main entry point for comprehensive test runner"""
    runner = ComprehensiveTestRunner()
    
    print("Starting comprehensive test execution...")
    print("This will run all test categories including functional, integration, performance, and error scenarios.")
    print()
    
    # Run comprehensive tests
    report = runner.run_comprehensive_tests(
        include_performance=True,
        include_error_scenarios=True
    )
    
    # Generate and display report
    comprehensive_report = runner.generate_comprehensive_report(report)
    print(comprehensive_report)
    
    # Save report to file
    report_file = Path("comprehensive_test_report.txt")
    with open(report_file, 'w') as f:
        f.write(comprehensive_report)
    
    print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    exit_code = 0 if report.production_readiness["overall_production_ready"] else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()