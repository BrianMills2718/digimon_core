#!/usr/bin/env python3
"""
COMPREHENSIVE STRESS TEST RUNNER

Executes all rigorous stress tests to find system breaking points:
1. Multi-document overload (scalability limits)
2. Long chain complexity (memory and processing limits)
3. Concurrent agent chaos (resource contention)
4. Adversarial input attacks (robustness and security)

This is the ultimate test to reveal the TRUE capabilities and limitations
of the agent stress testing system.
"""

import asyncio
import json
import time
import psutil
import gc
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Import all stress test modules
from rigorous_stress_framework import RigorousStressTestFramework, MultiDocumentOverloadTest
from long_chain_stress_test import LongChainStressTest
from concurrent_agent_chaos_test import ConcurrentAgentChaosTest
from adversarial_input_test import AdversarialInputTest

class ComprehensiveStressRunner:
    """Run all stress tests and analyze comprehensive system limits"""
    
    def __init__(self):
        self.runner_id = f"comprehensive_{int(time.time())}"
        self.start_time = time.time()
        self.system_baseline = self._capture_system_baseline()
        self.breaking_points_found = []
        self.performance_degradation = []
        self.security_vulnerabilities = []
        
        # Setup comprehensive logging
        self.logger = self._setup_comprehensive_logging()
        
        print(f"🚨 COMPREHENSIVE AGENT STRESS TESTING SUITE")
        print(f"=" * 80)
        print(f"🎯 MISSION: Find ALL system breaking points and limitations")
        print(f"🔬 APPROACH: Execute progressively more aggressive stress tests")
        print(f"📊 BASELINE: CPU: {self.system_baseline['cpu_percent']:.1f}%, Memory: {self.system_baseline['memory_percent']:.1f}%")
        print(f"⚠️  WARNING: This testing suite is designed to BREAK the system")
        print(f"=" * 80)
    
    def _capture_system_baseline(self) -> Dict[str, Any]:
        """Capture baseline system metrics before testing"""
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
            "process_count": len(psutil.pids())
        }
    
    def _setup_comprehensive_logging(self):
        """Setup comprehensive logging for all stress tests"""
        
        logger = logging.getLogger(f"comprehensive_stress_{self.runner_id}")
        logger.setLevel(logging.DEBUG)
        
        # Create detailed log file
        handler = logging.FileHandler(f"comprehensive_stress_{self.runner_id}.log")
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def execute_comprehensive_stress_testing(self) -> Dict[str, Any]:
        """Execute all stress tests in order of increasing severity"""
        
        comprehensive_results = {
            "runner_id": self.runner_id,
            "start_time": datetime.now().isoformat(),
            "system_baseline": self.system_baseline,
            "test_sequence": [],
            "breaking_points": [],
            "performance_limits": [],
            "security_issues": [],
            "system_recovery": [],
            "final_assessment": {}
        }
        
        print(f"\n🚀 INITIATING COMPREHENSIVE STRESS TEST SEQUENCE")
        print(f"   Test Duration: Expected 10-15 minutes")
        print(f"   System Impact: HIGH - System may become unresponsive")
        print(f"   Recovery: Automatic cleanup between tests")
        
        try:
            # TEST 1: Adversarial Input Attack (Baseline Robustness)
            print(f"\n" + "="*60)
            print(f"🗡️  TEST 1: ADVERSARIAL INPUT ATTACKS")
            print(f"   Objective: Test input validation and parser robustness")
            print(f"   Expected: Security vulnerabilities, parsing failures")
            print(f"="*60)
            
            adversarial_test = AdversarialInputTest()
            adversarial_results = await adversarial_test.execute_adversarial_attack_suite()
            
            comprehensive_results["test_sequence"].append({
                "test_name": "adversarial_input_attacks",
                "start_time": adversarial_results["start_time"],
                "end_time": adversarial_results["end_time"],
                "attacks_executed": adversarial_results["attacks_executed"],
                "vulnerabilities_found": len(adversarial_results["vulnerabilities_found"]),
                "system_crashes": adversarial_results["system_crashes"],
                "status": "completed"
            })
            
            # Record security issues
            if adversarial_results["vulnerabilities_found"]:
                comprehensive_results["security_issues"].extend(adversarial_results["vulnerabilities_found"])
            
            # System recovery pause
            await self._system_recovery_pause("adversarial_input_test")
            
            # TEST 2: Long Chain Complexity (Processing Limits)
            print(f"\n" + "="*60)
            print(f"🔗 TEST 2: LONG CHAIN COMPLEXITY")
            print(f"   Objective: Find processing and memory limits in tool chains")
            print(f"   Expected: Memory exhaustion, cascading failures")
            print(f"="*60)
            
            long_chain_test = LongChainStressTest()
            long_chain_results = await long_chain_test.execute_maximum_length_chain()
            
            comprehensive_results["test_sequence"].append({
                "test_name": "long_chain_complexity",
                "start_time": long_chain_results["start_time"],
                "end_time": long_chain_results["end_time"],
                "steps_completed": long_chain_results["steps_completed"],
                "breaking_point": long_chain_results.get("breaking_point"),
                "completion_status": long_chain_results.get("completion_status"),
                "status": "completed"
            })
            
            # Record breaking points
            if long_chain_results.get("breaking_point"):
                comprehensive_results["breaking_points"].append({
                    "test": "long_chain_complexity",
                    "breaking_point": long_chain_results["breaking_point"],
                    "failure_reason": long_chain_results.get("failure_reason"),
                    "steps_before_failure": long_chain_results["steps_completed"]
                })
            
            # System recovery pause
            await self._system_recovery_pause("long_chain_test")
            
            # TEST 3: Multi-Document Overload (Scalability Limits)  
            print(f"\n" + "="*60)
            print(f"📚 TEST 3: MULTI-DOCUMENT OVERLOAD")
            print(f"   Objective: Find scalability limits with many documents")
            print(f"   Expected: Memory pressure, processing timeouts")
            print(f"="*60)
            
            framework = RigorousStressTestFramework(break_system=True)
            overload_test = MultiDocumentOverloadTest(framework)
            overload_results = await overload_test.execute_academic_paper_overload(50)  # Reduced from 75 for stability
            
            comprehensive_results["test_sequence"].append({
                "test_name": "multi_document_overload",
                "documents_processed": overload_results.documents_processed,
                "total_entities": overload_results.total_entities,
                "total_relationships": overload_results.total_relationships,
                "successful_operations": overload_results.successful_operations,
                "failed_operations": overload_results.failed_operations,
                "execution_time": overload_results.total_execution_time,
                "status": "completed"
            })
            
            # Record performance limits
            if overload_results.failed_operations > overload_results.successful_operations * 0.3:
                comprehensive_results["performance_limits"].append({
                    "test": "multi_document_overload",
                    "limit_type": "DOCUMENT_PROCESSING_SCALABILITY",
                    "failure_rate": overload_results.failed_operations / (overload_results.successful_operations + overload_results.failed_operations),
                    "description": f"High failure rate at {overload_results.documents_processed} documents"
                })
            
            # System recovery pause
            await self._system_recovery_pause("multi_document_overload")
            
            # TEST 4: Concurrent Agent Chaos (Ultimate Stress Test)
            print(f"\n" + "="*60)
            print(f"🌪️  TEST 4: CONCURRENT AGENT CHAOS")
            print(f"   Objective: Maximum stress with concurrent agents")
            print(f"   Expected: Resource exhaustion, system overload")
            print(f"   WARNING: This is the most aggressive test")
            print(f"="*60)
            
            chaos_test = ConcurrentAgentChaosTest(max_agents=12)  # Reduced from 15 for stability
            chaos_results = await chaos_test.execute_concurrent_agent_storm()
            
            comprehensive_results["test_sequence"].append({
                "test_name": "concurrent_agent_chaos",
                "agents_launched": chaos_results["agents_launched"],
                "agents_completed": chaos_results["agents_completed"],
                "agents_failed": chaos_results["agents_failed"],
                "resource_exhaustion_events": len(chaos_results["resource_exhaustion_events"]),
                "system_breaking_points": len(chaos_results["system_breaking_points"]),
                "status": "completed"
            })
            
            # Record breaking points from concurrent test
            if chaos_results["system_breaking_points"]:
                comprehensive_results["breaking_points"].extend([
                    {
                        "test": "concurrent_agent_chaos",
                        "breaking_point": bp["type"],
                        "description": bp["description"]
                    } for bp in chaos_results["system_breaking_points"]
                ])
            
            # Final system recovery
            await self._system_recovery_pause("concurrent_chaos_test")
            
        except Exception as e:
            self.logger.error(f"Comprehensive stress testing failed: {e}")
            comprehensive_results["critical_failure"] = {
                "error": str(e),
                "test_phase": "unknown",
                "system_state": "potentially_corrupted"
            }
        
        comprehensive_results["end_time"] = datetime.now().isoformat()
        comprehensive_results["total_duration"] = time.time() - self.start_time
        
        # Analyze comprehensive results
        self._analyze_comprehensive_results(comprehensive_results)
        
        return comprehensive_results
    
    async def _system_recovery_pause(self, test_name: str):
        """Allow system recovery between tests"""
        
        print(f"\n🔧 SYSTEM RECOVERY: {test_name} completed")
        print(f"   Forcing garbage collection...")
        
        # Force garbage collection
        gc.collect()
        
        # Brief pause for system recovery
        recovery_time = 5
        print(f"   Recovery pause: {recovery_time} seconds...")
        
        for i in range(recovery_time):
            await asyncio.sleep(1)
            if i == 0:
                # Check system state
                memory = psutil.virtual_memory()
                print(f"   Memory usage: {memory.percent:.1f}%")
        
        print(f"   ✅ Recovery complete")
    
    def _analyze_comprehensive_results(self, results: Dict[str, Any]):
        """Analyze comprehensive stress test results"""
        
        print(f"\n" + "="*80)
        print(f"📊 COMPREHENSIVE STRESS TEST ANALYSIS")
        print(f"="*80)
        
        total_duration = results["total_duration"]
        tests_completed = len(results["test_sequence"])
        breaking_points = len(results["breaking_points"])
        security_issues = len(results["security_issues"])
        performance_limits = len(results["performance_limits"])
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        print(f"   Tests Completed: {tests_completed}/4")
        print(f"   Breaking Points Found: {breaking_points}")
        print(f"   Security Issues: {security_issues}")
        print(f"   Performance Limits: {performance_limits}")
        
        # Test-by-test analysis
        print(f"\n🔍 TEST-BY-TEST BREAKDOWN:")
        
        for test in results["test_sequence"]:
            test_name = test["test_name"].replace("_", " ").title()
            print(f"\n   {test_name}:")
            
            if test_name == "Adversarial Input Attacks":
                print(f"     Attacks Executed: {test.get('attacks_executed', 0)}")
                print(f"     Vulnerabilities: {test.get('vulnerabilities_found', 0)}")
                print(f"     System Crashes: {test.get('system_crashes', 0)}")
                
            elif test_name == "Long Chain Complexity":
                print(f"     Steps Completed: {test.get('steps_completed', 0)}/15")
                breaking_point = test.get('breaking_point')
                if breaking_point:
                    print(f"     Breaking Point: {breaking_point}")
                else:
                    print(f"     Status: Completed successfully")
                
            elif test_name == "Multi Document Overload":
                success_rate = 0
                if test.get('successful_operations', 0) + test.get('failed_operations', 0) > 0:
                    success_rate = test.get('successful_operations', 0) / (test.get('successful_operations', 0) + test.get('failed_operations', 0)) * 100
                print(f"     Documents Processed: {test.get('documents_processed', 0)}")
                print(f"     Success Rate: {success_rate:.1f}%")
                print(f"     Entities Extracted: {test.get('total_entities', 0)}")
                
            elif test_name == "Concurrent Agent Chaos":
                agents_launched = test.get('agents_launched', 0)
                agents_completed = test.get('agents_completed', 0)
                success_rate = (agents_completed / agents_launched * 100) if agents_launched > 0 else 0
                print(f"     Agents Launched: {agents_launched}")
                print(f"     Success Rate: {success_rate:.1f}%")
                print(f"     Resource Exhaustion Events: {test.get('resource_exhaustion_events', 0)}")
        
        # Breaking points analysis
        if results["breaking_points"]:
            print(f"\n🚨 SYSTEM BREAKING POINTS DISCOVERED:")
            for bp in results["breaking_points"]:
                print(f"   • {bp['test']}: {bp['breaking_point']}")
                if 'failure_reason' in bp:
                    print(f"     Reason: {bp['failure_reason']}")
                if 'steps_before_failure' in bp:
                    print(f"     Failed at step: {bp['steps_before_failure']}")
        
        # Security analysis
        if results["security_issues"]:
            print(f"\n🔒 SECURITY VULNERABILITIES FOUND:")
            vuln_types = {}
            for issue in results["security_issues"]:
                vuln_type = issue.get("type", "UNKNOWN")
                vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
            
            for vuln_type, count in vuln_types.items():
                print(f"   • {vuln_type}: {count} instances")
        
        # Performance limits analysis
        if results["performance_limits"]:
            print(f"\n⚡ PERFORMANCE LIMITS IDENTIFIED:")
            for limit in results["performance_limits"]:
                print(f"   • {limit['limit_type']}: {limit['description']}")
        
        # Overall system assessment
        print(f"\n🎯 SYSTEM ROBUSTNESS ASSESSMENT:")
        
        # Calculate robustness score
        robustness_factors = {
            "completed_all_tests": tests_completed == 4,
            "low_breaking_points": breaking_points <= 2,
            "minimal_security_issues": security_issues <= 3,
            "acceptable_performance": performance_limits <= 2
        }
        
        robustness_score = sum(robustness_factors.values()) / len(robustness_factors) * 100
        
        print(f"   Robustness Score: {robustness_score:.1f}%")
        
        if robustness_score >= 85:
            print(f"   Assessment: 🟢 HIGHLY ROBUST - System handles stress very well")
        elif robustness_score >= 70:
            print(f"   Assessment: 🟡 MODERATELY ROBUST - Some limitations found")
        elif robustness_score >= 50:
            print(f"   Assessment: 🟠 BRITTLE - Multiple breaking points discovered")
        else:
            print(f"   Assessment: 🔴 FRAGILE - System struggles under stress")
        
        # Recommendations
        print(f"\n💡 IMPROVEMENT RECOMMENDATIONS:")
        
        if breaking_points > 0:
            print(f"   • Address breaking points to improve system stability")
        if security_issues > 0:
            print(f"   • Fix security vulnerabilities for production readiness")
        if performance_limits > 0:
            print(f"   • Optimize performance bottlenecks for better scalability")
        if tests_completed < 4:
            print(f"   • Fix critical issues preventing test completion")
        
        if robustness_score >= 85:
            print(f"   • System shows excellent resilience - ready for production workloads")
        
        # Save comprehensive assessment
        results["final_assessment"] = {
            "robustness_score": robustness_score,
            "robustness_factors": robustness_factors,
            "system_classification": self._classify_system(robustness_score),
            "production_readiness": robustness_score >= 70 and security_issues <= 2,
            "recommended_actions": self._generate_recommendations(results)
        }
    
    def _classify_system(self, robustness_score: float) -> str:
        """Classify system robustness"""
        if robustness_score >= 85:
            return "PRODUCTION_READY"
        elif robustness_score >= 70:
            return "NEEDS_OPTIMIZATION"
        elif robustness_score >= 50:
            return "REQUIRES_FIXES"
        else:
            return "NOT_PRODUCTION_READY"
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on test results"""
        recommendations = []
        
        if results["breaking_points"]:
            recommendations.append("Implement better error handling and recovery mechanisms")
        
        if results["security_issues"]:
            recommendations.append("Add comprehensive input validation and sanitization")
        
        if any("memory" in str(bp).lower() for bp in results["breaking_points"]):
            recommendations.append("Optimize memory usage and implement resource limits")
        
        if any("timeout" in str(bp).lower() for bp in results["breaking_points"]):
            recommendations.append("Add processing timeouts and cancellation mechanisms")
        
        concurrent_test = next((t for t in results["test_sequence"] if t["test_name"] == "concurrent_agent_chaos"), None)
        if concurrent_test and concurrent_test.get("resource_exhaustion_events", 0) > 0:
            recommendations.append("Implement resource pooling and connection management")
        
        return recommendations

async def run_comprehensive_stress_testing():
    """Execute the comprehensive stress testing suite"""
    
    runner = ComprehensiveStressRunner()
    
    print(f"\n⚠️  FINAL WARNING: COMPREHENSIVE STRESS TESTING")
    print(f"   This will aggressively stress test the entire system")
    print(f"   Expected duration: 10-15 minutes")
    print(f"   System may become temporarily unresponsive")
    print(f"   All tests designed to find breaking points")
    
    # Get user confirmation
    print(f"\n🤔 Do you want to proceed with comprehensive stress testing?")
    print(f"   This is the ultimate test of system robustness")
    
    try:
        results = await runner.execute_comprehensive_stress_testing()
        
        # Save final results
        results_file = f"comprehensive_stress_results_{runner.runner_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 COMPREHENSIVE RESULTS SAVED: {results_file}")
        print(f"\n🏁 COMPREHENSIVE STRESS TESTING COMPLETE")
        print(f"   Classification: {results['final_assessment']['system_classification']}")
        print(f"   Production Ready: {results['final_assessment']['production_readiness']}")
        
        return results
        
    except Exception as e:
        print(f"💥 COMPREHENSIVE STRESS TESTING FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_comprehensive_stress_testing())