#!/usr/bin/env python3
"""
KGAS Agent Stress Testing Runner

Orchestrates and runs the complete suite of agent stress tests
for dual-agent research architecture validation.
"""

import asyncio
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class TestResult:
    """Result from a stress test execution"""
    test_name: str
    test_category: str
    status: str  # "success", "failure", "error"
    execution_time: float
    metrics: Dict[str, Any]
    errors: List[str]
    output_file: str

class StressTestRunner:
    """Orchestrates execution of all agent stress tests"""
    
    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.results_dir = test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.test_results: List[TestResult] = []
    
    async def run_all_tests(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run all stress tests or specific categories"""
        
        print("🚀 Starting KGAS Agent Stress Testing Suite")
        print("=" * 70)
        
        # Define test categories and their tests
        test_categories = {
            "dual_agent": [
                {
                    "name": "Basic Coordination Test",
                    "script": "dual_agent_tests/basic_coordination_test.py",
                    "description": "Test basic dual-agent coordination patterns"
                }
            ],
            "memory_integration": [
                {
                    "name": "Knowledge Graph Test", 
                    "script": "memory_integration_tests/knowledge_graph_test.py",
                    "description": "Test knowledge graph memory integration"
                }
            ],
            "claude_code_integration": [
                {
                    "name": "SDK Coordination Test",
                    "script": "claude_code_integration/sdk_coordination_test.py", 
                    "description": "Test Claude Code SDK coordination patterns"
                }
            ]
        }
        
        # Filter categories if specified
        if categories:
            test_categories = {k: v for k, v in test_categories.items() if k in categories}
        
        total_tests = sum(len(tests) for tests in test_categories.values())
        current_test = 0
        
        print(f"📋 Running {total_tests} tests across {len(test_categories)} categories")
        print()
        
        # Run tests by category
        for category, tests in test_categories.items():
            print(f"📂 Category: {category.replace('_', ' ').title()}")
            print("-" * 50)
            
            for test in tests:
                current_test += 1
                print(f"\n🧪 Test {current_test}/{total_tests}: {test['name']}")
                print(f"📝 {test['description']}")
                
                result = await self._run_single_test(test, category)
                self.test_results.append(result)
                
                # Print immediate result
                if result.status == "success":
                    print(f"✅ PASSED ({result.execution_time:.2f}s)")
                elif result.status == "failure": 
                    print(f"❌ FAILED ({result.execution_time:.2f}s)")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"   ❌ {error}")
                else:
                    print(f"💥 ERROR ({result.execution_time:.2f}s)")
                    for error in result.errors[:3]:
                        print(f"   💥 {error}")
                
                print("-" * 30)
        
        # Generate comprehensive results
        summary = self._generate_test_summary()
        
        # Save comprehensive results
        timestamp = int(time.time())
        summary_file = self.results_dir / f"stress_test_summary_{timestamp}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📊 STRESS TEST SUMMARY")
        print("=" * 70)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"💥 Errors: {summary['error_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1%}")
        print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")
        
        # Category breakdown
        print(f"\n📋 Results by Category:")
        for category, stats in summary['category_stats'].items():
            print(f"  {category}: {stats['passed']}/{stats['total']} passed ({stats['success_rate']:.1%})")
        
        # Performance insights
        print(f"\n💡 Performance Insights:")
        if summary['success_rate'] >= 0.9:
            print("✅ EXCELLENT: High success rate across all test categories")
        elif summary['success_rate'] >= 0.7:
            print("⚠️  GOOD: Most tests passing, some areas need attention")
        else:
            print("❌ NEEDS IMPROVEMENT: Multiple test failures require investigation")
        
        avg_time = summary['total_execution_time'] / summary['total_tests']
        if avg_time <= 10.0:
            print("✅ EXCELLENT: Fast test execution times")
        elif avg_time <= 30.0:
            print("⚠️  ACCEPTABLE: Reasonable test execution times")
        else:
            print("❌ SLOW: Test execution times need optimization")
        
        print(f"\n💾 Detailed results saved to: {summary_file}")
        
        return summary
    
    async def _run_single_test(self, test: Dict[str, str], category: str) -> TestResult:
        """Run a single stress test"""
        
        test_script = self.test_dir / test["script"]
        
        if not test_script.exists():
            return TestResult(
                test_name=test["name"],
                test_category=category,
                status="error",
                execution_time=0.0,
                metrics={},
                errors=[f"Test script not found: {test_script}"],
                output_file=""
            )
        
        start_time = time.time()
        
        try:
            # Run the test script
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(test_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.test_dir)
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            # Determine test result
            if process.returncode == 0:
                status = "success"
                errors = []
            else:
                status = "failure"
                errors = [stderr.decode('utf-8')] if stderr else ["Unknown failure"]
            
            # Try to extract metrics from stdout
            metrics = self._extract_metrics_from_output(stdout.decode('utf-8'))
            
            # Generate output filename
            test_name_safe = test["name"].lower().replace(" ", "_").replace(".", "")
            output_file = f"{category}_{test_name_safe}_results.json"
            
            return TestResult(
                test_name=test["name"],
                test_category=category,
                status=status,
                execution_time=execution_time,
                metrics=metrics,
                errors=errors,
                output_file=output_file
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test["name"],
                test_category=category,
                status="error",
                execution_time=execution_time,
                metrics={},
                errors=[str(e)],
                output_file=""
            )
    
    def _extract_metrics_from_output(self, output: str) -> Dict[str, Any]:
        """Extract performance metrics from test output"""
        metrics = {}
        
        lines = output.split('\n')
        for line in lines:
            # Look for common metric patterns
            if "Success Rate:" in line:
                try:
                    value = line.split(':')[1].strip().rstrip('%')
                    metrics['success_rate'] = float(value) / 100
                except:
                    pass
            elif "Average" in line and "Score:" in line:
                try:
                    value = line.split(':')[1].strip()
                    metrics['average_score'] = float(value)
                except:
                    pass
            elif "Total Time:" in line:
                try:
                    value = line.split(':')[1].strip().rstrip('s')
                    metrics['total_time'] = float(value)
                except:
                    pass
            elif "Agent Calls:" in line:
                try:
                    value = line.split(':')[1].strip()
                    if "Research" in line:
                        metrics['research_agent_calls'] = int(value)
                    elif "Execution" in line:
                        metrics['execution_agent_calls'] = int(value)
                except:
                    pass
        
        return metrics
    
    def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "success"])
        failed_tests = len([r for r in self.test_results if r.status == "failure"])
        error_tests = len([r for r in self.test_results if r.status == "error"])
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        total_time = sum(r.execution_time for r in self.test_results)
        
        # Category statistics
        category_stats = {}
        for result in self.test_results:
            category = result.test_category
            if category not in category_stats:
                category_stats[category] = {"total": 0, "passed": 0, "failed": 0, "errors": 0}
            
            category_stats[category]["total"] += 1
            if result.status == "success":
                category_stats[category]["passed"] += 1
            elif result.status == "failure":
                category_stats[category]["failed"] += 1
            else:
                category_stats[category]["errors"] += 1
        
        # Add success rates to category stats
        for category, stats in category_stats.items():
            stats["success_rate"] = stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0
        
        # Performance metrics aggregation
        performance_metrics = {}
        all_metrics = [r.metrics for r in self.test_results if r.metrics]
        
        if all_metrics:
            # Calculate averages for common metrics
            for metric in ["success_rate", "average_score", "total_time"]:
                values = [m[metric] for m in all_metrics if metric in m]
                if values:
                    performance_metrics[f"avg_{metric}"] = sum(values) / len(values)
        
        return {
            "timestamp": time.time(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": success_rate,
            "total_execution_time": total_time,
            "average_execution_time": total_time / total_tests if total_tests > 0 else 0.0,
            "category_stats": category_stats,
            "performance_metrics": performance_metrics,
            "test_results": [asdict(r) for r in self.test_results],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze success rates
        success_rate = len([r for r in self.test_results if r.status == "success"]) / len(self.test_results)
        
        if success_rate < 0.7:
            recommendations.append("Overall success rate is low - review agent coordination patterns")
        
        if success_rate >= 0.9:
            recommendations.append("Excellent success rate - consider expanding test coverage")
        
        # Analyze execution times
        avg_time = sum(r.execution_time for r in self.test_results) / len(self.test_results)
        
        if avg_time > 60.0:
            recommendations.append("Test execution times are high - optimize agent response patterns")
        
        # Analyze by category
        categories = set(r.test_category for r in self.test_results)
        for category in categories:
            category_results = [r for r in self.test_results if r.test_category == category]
            category_success = len([r for r in category_results if r.status == "success"]) / len(category_results)
            
            if category_success < 0.8:
                recommendations.append(f"Category '{category}' needs attention - review implementation")
        
        # Performance-specific recommendations
        performance_issues = [r for r in self.test_results if r.execution_time > 30.0]
        if len(performance_issues) > len(self.test_results) * 0.3:
            recommendations.append("Performance optimization needed - review agent efficiency")
        
        if not recommendations:
            recommendations.append("All tests performing well - continue current approach")
        
        return recommendations

def main():
    """Main entry point for stress test runner"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Run KGAS Agent Stress Tests")
    parser.add_argument("--categories", nargs="+", choices=["dual_agent", "memory_integration", "claude_code_integration"],
                       help="Specific test categories to run")
    parser.add_argument("--test-dir", default="/home/brian/projects/Digimons/agent_stress_testing",
                       help="Directory containing stress tests")
    
    args = parser.parse_args()
    
    test_dir = Path(args.test_dir)
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)
    
    runner = StressTestRunner(test_dir)
    
    # Run the tests
    try:
        summary = asyncio.run(runner.run_all_tests(args.categories))
        
        # Exit with appropriate code
        if summary["success_rate"] >= 0.8:
            print(f"\n🎉 STRESS TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n⚠️  STRESS TESTING COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stress testing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Stress testing failed with error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()