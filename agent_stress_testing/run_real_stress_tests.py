#!/usr/bin/env python3
"""
Real KGAS Agent Stress Testing Runner

Orchestrates comprehensive stress tests using real Claude Code, MCP, and KGAS integrations.
No mocks - authentic testing of dual-agent research architecture.
"""

import asyncio
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Import real test modules
from workflow_execution_tests.real_workflow_test import test_real_workflow_execution
from research_scenario_tests.literature_review_test import test_literature_review
from real_claude_integration import RealClaudeCodeClient, DualAgentCoordinator
from real_mcp_integration import RealMemoryIntegrator
from real_kgas_integration import RealWorkflowExecutor


@dataclass
class StressTestSuite:
    """Complete stress test suite configuration"""
    name: str
    categories: List[str]
    total_tests: int
    expected_duration_minutes: int
    success_criteria: Dict[str, float]


@dataclass
class StressTestResults:
    """Comprehensive stress test results"""
    suite_name: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    error_tests: int
    total_execution_time: float
    success_rate: float
    category_results: Dict[str, Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    integration_status: Dict[str, bool]
    recommendations: List[str]


class RealStressTestRunner:
    """Real stress test runner with no mocks"""
    
    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.results_dir = test_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Integration status tracking
        self.integration_status = {
            "claude_code_cli": False,
            "mcp_servers": False,
            "kgas_tools": False,
            "memory_persistence": False
        }
        
        # Performance tracking
        self.performance_metrics = {
            "total_agent_calls": 0,
            "total_tool_executions": 0,
            "total_memory_operations": 0,
            "avg_response_time": 0.0,
            "error_rate": 0.0
        }
    
    async def validate_integrations(self) -> Dict[str, bool]:
        """Validate that all real integrations are available"""
        print("🔍 Validating Real Integrations...")
        print("-" * 50)
        
        # Test Claude Code CLI
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.integration_status["claude_code_cli"] = True
                print("✅ Claude Code CLI: Available")
            else:
                print("❌ Claude Code CLI: Not configured")
        except Exception as e:
            print(f"❌ Claude Code CLI: Failed ({e})")
        
        # Test MCP server connectivity
        try:
            memory_integrator = RealMemoryIntegrator()
            mcp_connected = await memory_integrator.connect()
            if mcp_connected:
                self.integration_status["mcp_servers"] = True
                print("✅ MCP Servers: Connected")
                await memory_integrator.disconnect()
            else:
                print("❌ MCP Servers: Connection failed")
        except Exception as e:
            print(f"❌ MCP Servers: Failed ({e})")
        
        # Test KGAS tools
        try:
            workflow_executor = RealWorkflowExecutor()
            available_tools = workflow_executor.tool_executor.available_tools
            if available_tools:
                self.integration_status["kgas_tools"] = True
                print(f"✅ KGAS Tools: {len(available_tools)} tools available")
            else:
                print("❌ KGAS Tools: No tools available")
        except Exception as e:
            print(f"❌ KGAS Tools: Failed ({e})")
        
        # Test memory persistence
        try:
            # Test basic file system access for memory persistence
            test_file = self.results_dir / "memory_test.json"
            test_data = {"test": "memory_persistence", "timestamp": time.time()}
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            test_file.unlink()  # Clean up
            self.integration_status["memory_persistence"] = True
            print("✅ Memory Persistence: Available")
        except Exception as e:
            print(f"❌ Memory Persistence: Failed ({e})")
        
        integration_count = sum(self.integration_status.values())
        total_integrations = len(self.integration_status)
        
        print(f"\n📊 Integration Status: {integration_count}/{total_integrations} available")
        
        if integration_count == total_integrations:
            print("🚀 All integrations ready - running full stress tests")
        elif integration_count >= total_integrations * 0.5:
            print("⚠️  Partial integrations - running with reduced functionality")
        else:
            print("❌ Insufficient integrations - stress tests may fail")
        
        return self.integration_status
    
    async def run_dual_agent_coordination_tests(self) -> Dict[str, Any]:
        """Run real dual-agent coordination tests"""
        print("\n📂 Category: Dual-Agent Coordination")
        print("-" * 50)
        
        category_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "execution_time": 0.0,
            "agent_performance": {},
            "coordination_metrics": {}
        }
        
        if not self.integration_status["claude_code_cli"]:
            print("❌ Skipping - Claude Code CLI not available")
            return category_results
        
        start_time = time.time()
        
        try:
            # Test basic coordination
            print("🧪 Test: Basic Agent Coordination")
            
            research_config = {
                "system_prompt": """You are an expert research assistant specializing in social science research.""",
                "temperature": 0.7
            }
            
            execution_config = {
                "system_prompt": """You are a precise workflow execution agent for research analysis.""",
                "temperature": 0.3
            }
            
            coordinator = DualAgentCoordinator(research_config, execution_config)
            
            test_query = "How do communication patterns change during organizational restructuring?"
            result = await coordinator.execute_research_workflow(test_query)
            
            category_results["tests_run"] += 1
            
            if result["status"] == "success":
                category_results["tests_passed"] += 1
                print("✅ Basic coordination: PASSED")
                
                # Extract performance metrics
                perf_metrics = result.get("performance_metrics", {})
                category_results["agent_performance"] = {
                    "research_agent": perf_metrics.get("research_agent_stats", {}),
                    "execution_agent": perf_metrics.get("execution_agent_stats", {})
                }
                
                # Update global metrics
                self.performance_metrics["total_agent_calls"] += (
                    perf_metrics.get("research_agent_stats", {}).get("total_calls", 0) +
                    perf_metrics.get("execution_agent_stats", {}).get("total_calls", 0)
                )
            else:
                print(f"❌ Basic coordination: FAILED - {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"💥 Dual-agent coordination error: {e}")
        
        category_results["execution_time"] = time.time() - start_time
        return category_results
    
    async def run_memory_integration_tests(self) -> Dict[str, Any]:
        """Run real memory integration tests"""
        print("\n📂 Category: Memory Integration")
        print("-" * 50)
        
        category_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "execution_time": 0.0,
            "memory_operations": 0,
            "context_enhancement_score": 0.0
        }
        
        if not self.integration_status["mcp_servers"]:
            print("❌ Skipping - MCP servers not available")
            return category_results
        
        start_time = time.time()
        
        try:
            print("🧪 Test: Knowledge Graph Memory Integration")
            
            memory_integrator = RealMemoryIntegrator()
            connected = await memory_integrator.connect()
            
            category_results["tests_run"] += 1
            
            if connected:
                # Test storing and retrieving research session
                session_data = {
                    "session_id": f"test_{int(time.time())}",
                    "user_id": "stress_test_user",
                    "query": "Test query for memory integration",
                    "domain": "organizational_behavior",
                    "methodology": "mixed_methods",
                    "execution_time": 30.0,
                    "quality_score": 0.85,
                    "findings": ["Test finding 1", "Test finding 2"]
                }
                
                # Store session
                stored_ids = await memory_integrator.store_research_session(session_data)
                category_results["memory_operations"] += len(stored_ids)
                
                # Retrieve context
                context = await memory_integrator.retrieve_research_context(
                    "Test context retrieval query",
                    "stress_test_user"
                )
                
                if context and context.get("context_enhancement_score", 0) > 0:
                    category_results["tests_passed"] += 1
                    category_results["context_enhancement_score"] = context.get("context_enhancement_score", 0)
                    print("✅ Memory integration: PASSED")
                else:
                    print("❌ Memory integration: FAILED - No context enhancement")
                
                await memory_integrator.disconnect()
                
                # Update global metrics
                self.performance_metrics["total_memory_operations"] += category_results["memory_operations"]
            else:
                print("❌ Memory integration: FAILED - Connection failed")
            
        except Exception as e:
            print(f"💥 Memory integration error: {e}")
        
        category_results["execution_time"] = time.time() - start_time
        return category_results
    
    async def run_workflow_execution_tests(self) -> Dict[str, Any]:
        """Run real workflow execution tests"""
        print("\n📂 Category: Workflow Execution")
        print("-" * 50)
        
        if not self.integration_status["kgas_tools"]:
            print("❌ Skipping - KGAS tools not available")
            return {"tests_run": 0, "tests_passed": 0, "execution_time": 0.0}
        
        start_time = time.time()
        
        try:
            print("🧪 Running Real Workflow Execution Tests...")
            results = await test_real_workflow_execution()
            
            category_results = {
                "tests_run": len(results),
                "tests_passed": len([r for r in results if r.status == "success"]),
                "execution_time": time.time() - start_time,
                "workflow_success_rate": len([r for r in results if r.workflow_executed]) / len(results) if results else 0,
                "avg_quality_score": sum(r.research_quality_score for r in results) / len(results) if results else 0,
                "tool_coordination_success": len([r for r in results if r.tool_coordination_success]) / len(results) if results else 0
            }
            
            # Update global metrics
            for result in results:
                perf_metrics = result.performance_metrics
                if "tool_execution" in perf_metrics:
                    self.performance_metrics["total_tool_executions"] += perf_metrics["tool_execution"].get("total_executions", 0)
            
            if category_results["tests_passed"] > 0:
                print(f"✅ Workflow execution: {category_results['tests_passed']}/{category_results['tests_run']} PASSED")
            else:
                print("❌ Workflow execution: All tests FAILED")
            
            return category_results
            
        except Exception as e:
            print(f"💥 Workflow execution error: {e}")
            return {"tests_run": 0, "tests_passed": 0, "execution_time": time.time() - start_time}
    
    async def run_research_scenario_tests(self) -> Dict[str, Any]:
        """Run real research scenario tests"""
        print("\n📂 Category: Research Scenarios")
        print("-" * 50)
        
        start_time = time.time()
        category_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "execution_time": 0.0,
            "literature_review_quality": 0.0,
            "research_insights_generated": 0
        }
        
        try:
            print("🧪 Running Literature Review Test...")
            lit_result = await test_literature_review()
            
            category_results["tests_run"] += 1
            
            if lit_result and lit_result.status == "success":
                category_results["tests_passed"] += 1
                category_results["literature_review_quality"] = lit_result.synthesis_quality
                category_results["research_insights_generated"] = len(lit_result.research_gaps_identified)
                print("✅ Literature review: PASSED")
            else:
                print("❌ Literature review: FAILED")
            
        except Exception as e:
            print(f"💥 Research scenario error: {e}")
        
        category_results["execution_time"] = time.time() - start_time
        return category_results
    
    async def run_comprehensive_stress_tests(self, categories: List[str] = None) -> StressTestResults:
        """Run comprehensive stress tests with real integrations"""
        print("🚀 Starting Real KGAS Agent Stress Testing Suite")
        print("=" * 70)
        
        start_time = time.time()
        
        # Validate integrations first
        await self.validate_integrations()
        
        # Define test categories
        all_categories = {
            "dual_agent_coordination": self.run_dual_agent_coordination_tests,
            "memory_integration": self.run_memory_integration_tests,
            "workflow_execution": self.run_workflow_execution_tests,
            "research_scenarios": self.run_research_scenario_tests
        }
        
        # Filter categories if specified
        if categories:
            test_categories = {k: v for k, v in all_categories.items() if k in categories}
        else:
            test_categories = all_categories
        
        print(f"\n📋 Running {len(test_categories)} test categories")
        
        category_results = {}
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        error_tests = 0
        
        # Run each category
        for category_name, test_function in test_categories.items():
            print(f"\n🏃 Executing: {category_name.replace('_', ' ').title()}")
            
            try:
                result = await test_function()
                category_results[category_name] = result
                
                total_tests += result.get("tests_run", 0)
                successful_tests += result.get("tests_passed", 0)
                failed_tests += result.get("tests_run", 0) - result.get("tests_passed", 0)
                
                print(f"   📊 {result.get('tests_passed', 0)}/{result.get('tests_run', 0)} tests passed")
                
            except Exception as e:
                print(f"   💥 Category failed: {e}")
                error_tests += 1
                category_results[category_name] = {
                    "tests_run": 1,
                    "tests_passed": 0,
                    "execution_time": 0.0,
                    "error": str(e)
                }
        
        total_execution_time = time.time() - start_time
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        
        # Calculate final performance metrics
        self.performance_metrics["avg_response_time"] = total_execution_time / max(total_tests, 1)
        self.performance_metrics["error_rate"] = (failed_tests + error_tests) / max(total_tests, 1)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            success_rate, category_results, self.integration_status
        )
        
        return StressTestResults(
            suite_name="Real KGAS Agent Stress Tests",
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            error_tests=error_tests,
            total_execution_time=total_execution_time,
            success_rate=success_rate,
            category_results=category_results,
            performance_metrics=self.performance_metrics,
            integration_status=self.integration_status,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, success_rate: float, category_results: Dict, integration_status: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Overall performance recommendations
        if success_rate >= 0.9:
            recommendations.append("✅ Excellent performance - consider expanding test coverage")
        elif success_rate >= 0.7:
            recommendations.append("⚠️ Good performance - address failing test categories")
        else:
            recommendations.append("❌ Poor performance - comprehensive review needed")
        
        # Integration-specific recommendations
        if not integration_status.get("claude_code_cli"):
            recommendations.append("🔧 Install and configure Claude Code CLI for agent coordination")
        
        if not integration_status.get("mcp_servers"):
            recommendations.append("🔧 Set up MCP servers for memory integration")
        
        if not integration_status.get("kgas_tools"):
            recommendations.append("🔧 Implement missing KGAS analysis tools")
        
        # Category-specific recommendations
        for category, results in category_results.items():
            if results.get("tests_passed", 0) == 0 and results.get("tests_run", 0) > 0:
                recommendations.append(f"🔧 Fix {category.replace('_', ' ')} - all tests failing")
        
        # Performance recommendations
        if self.performance_metrics.get("error_rate", 0) > 0.2:
            recommendations.append("🔧 High error rate - improve error handling and recovery")
        
        if self.performance_metrics.get("avg_response_time", 0) > 60.0:
            recommendations.append("🔧 Slow response times - optimize agent and tool performance")
        
        return recommendations
    
    def print_comprehensive_summary(self, results: StressTestResults):
        """Print comprehensive test summary"""
        print(f"\n📊 COMPREHENSIVE STRESS TEST SUMMARY")
        print("=" * 70)
        
        print(f"Suite: {results.suite_name}")
        print(f"Total Tests: {results.total_tests}")
        print(f"✅ Successful: {results.successful_tests}")
        print(f"❌ Failed: {results.failed_tests}")
        print(f"💥 Errors: {results.error_tests}")
        print(f"📈 Success Rate: {results.success_rate:.1%}")
        print(f"⏱️ Total Time: {results.total_execution_time:.2f}s")
        
        print(f"\n🔗 Integration Status:")
        for integration, status in results.integration_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {integration.replace('_', ' ').title()}")
        
        print(f"\n📂 Category Results:")
        for category, result in results.category_results.items():
            success_rate = result.get("tests_passed", 0) / max(result.get("tests_run", 1), 1)
            print(f"   {category.replace('_', ' ').title()}: {result.get('tests_passed', 0)}/{result.get('tests_run', 0)} ({success_rate:.1%})")
        
        print(f"\n⚡ Performance Metrics:")
        perf = results.performance_metrics
        print(f"   Agent Calls: {perf.get('total_agent_calls', 0)}")
        print(f"   Tool Executions: {perf.get('total_tool_executions', 0)}")
        print(f"   Memory Operations: {perf.get('total_memory_operations', 0)}")
        print(f"   Avg Response Time: {perf.get('avg_response_time', 0):.2f}s")
        print(f"   Error Rate: {perf.get('error_rate', 0):.1%}")
        
        print(f"\n💡 Recommendations:")
        for recommendation in results.recommendations:
            print(f"   {recommendation}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT")
        print("=" * 70)
        
        if results.success_rate >= 0.9 and sum(results.integration_status.values()) >= 3:
            print("🚀 EXCELLENT: Real integrations working effectively")
        elif results.success_rate >= 0.7 and sum(results.integration_status.values()) >= 2:
            print("⚠️ GOOD: Most functionality working, some integration issues")
        else:
            print("❌ NEEDS IMPROVEMENT: Multiple integration failures")


async def main():
    """Main entry point for real stress testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Real KGAS Agent Stress Tests")
    parser.add_argument("--categories", nargs="+", 
                       choices=["dual_agent_coordination", "memory_integration", "workflow_execution", "research_scenarios"],
                       help="Specific test categories to run")
    parser.add_argument("--test-dir", default="/home/brian/projects/Digimons/agent_stress_testing",
                       help="Directory containing stress tests")
    
    args = parser.parse_args()
    
    test_dir = Path(args.test_dir)
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)
    
    runner = RealStressTestRunner(test_dir)
    
    try:
        # Run comprehensive stress tests
        results = await runner.run_comprehensive_stress_tests(args.categories)
        
        # Print detailed summary
        runner.print_comprehensive_summary(results)
        
        # Save detailed results
        timestamp = int(time.time())
        results_file = runner.results_dir / f"real_stress_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Exit with appropriate code
        if results.success_rate >= 0.8:
            print(f"\n🎉 STRESS TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n⚠️ STRESS TESTING COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stress testing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Stress testing failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())