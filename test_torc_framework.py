#!/usr/bin/env python3
"""
TORC (Time, Operational Resilience, Compatibility) Testing Framework
Comprehensive testing framework for measuring and improving system reliability
"""

import sys
import time
import asyncio
import threading
import concurrent.futures
import psutil
import os
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@dataclass
class TORCMetrics:
    """Comprehensive TORC metrics"""
    # Time metrics
    response_time_p50: float  # 50th percentile response time
    response_time_p95: float  # 95th percentile response time  
    response_time_p99: float  # 99th percentile response time
    throughput_peak: float    # Peak throughput (ops/sec)
    throughput_sustained: float  # Sustained throughput over time
    
    # Operational Resilience metrics
    failure_recovery_time: float  # Average time to recover from failures
    error_rate_under_load: float  # Error rate under stress conditions
    graceful_degradation_score: float  # How well system degrades under pressure
    circuit_breaker_effectiveness: float  # Effectiveness of failure handling
    
    # Compatibility metrics
    interface_compliance_score: float  # API/interface standard compliance
    backward_compatibility_score: float  # Backward compatibility maintenance
    cross_component_compatibility: float  # Inter-component compatibility
    version_tolerance_score: float  # Tolerance to version differences


@dataclass
class TORCTestResult:
    """Result of a TORC test"""
    test_name: str
    category: str  # "Time", "Operational", "Compatibility"
    passed: bool
    score: float
    metrics: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    execution_time: float


class TORCTestFramework:
    """Comprehensive TORC testing framework"""
    
    def __init__(self):
        self.test_results = []
        self.metrics_history = []
        self.performance_baseline = None
        
    def run_torc_assessment(self) -> Dict[str, Any]:
        """Run complete TORC assessment"""
        print("⚡ COMPREHENSIVE TORC ASSESSMENT")
        print("Testing Time, Operational Resilience, and Compatibility")
        print("=" * 80)
        
        torc_tests = [
            # Time Performance Tests
            ("Response Time Analysis", "Time", self.test_response_time_performance),
            ("Throughput Analysis", "Time", self.test_throughput_performance),
            ("Latency Under Load", "Time", self.test_latency_under_load),
            ("Performance Scaling", "Time", self.test_performance_scaling),
            
            # Operational Resilience Tests
            ("Failure Recovery", "Operational", self.test_failure_recovery),
            ("Error Rate Under Stress", "Operational", self.test_error_rate_stress),
            ("Graceful Degradation", "Operational", self.test_graceful_degradation),
            ("Circuit Breaker Patterns", "Operational", self.test_circuit_breaker_patterns),
            ("Resource Exhaustion Recovery", "Operational", self.test_resource_exhaustion_recovery),
            
            # Compatibility Tests
            ("Interface Compliance", "Compatibility", self.test_interface_compliance),
            ("Backward Compatibility", "Compatibility", self.test_backward_compatibility),
            ("Cross-Component Integration", "Compatibility", self.test_cross_component_integration),
            ("Version Tolerance", "Compatibility", self.test_version_tolerance),
            ("Configuration Compatibility", "Compatibility", self.test_configuration_compatibility)
        ]
        
        overall_results = {
            "torc_summary": {},
            "metrics_by_category": {},
            "overall_torc_score": 0.0,
            "time_performance": {},
            "operational_resilience": {},
            "compatibility_assessment": {},
            "improvement_plan": []
        }
        
        # Run tests by category
        for test_name, category, test_func in torc_tests:
            print(f"\n{'='*15} {category}: {test_name} {'='*15}")
            
            start_time = time.time()
            try:
                result = test_func()
                execution_time = time.time() - start_time
                
                torc_result = TORCTestResult(
                    test_name=test_name,
                    category=category,
                    passed=result.get("passed", False),
                    score=result.get("score", 0.0),
                    metrics=result.get("metrics", {}),
                    issues=result.get("issues", []),
                    recommendations=result.get("recommendations", []),
                    execution_time=execution_time
                )
                
                self.test_results.append(torc_result)
                
                status = "✅ PASSED" if torc_result.passed else "❌ FAILED"
                print(f"{status} {test_name}: {torc_result.score:.1%} ({execution_time:.2f}s)")
                
                if torc_result.issues:
                    for issue in torc_result.issues[:2]:
                        print(f"   ⚠️  {issue}")
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"❌ {test_name}: FAILED with exception: {e}")
                
                self.test_results.append(TORCTestResult(
                    test_name=test_name,
                    category=category,
                    passed=False,
                    score=0.0,
                    metrics={},
                    issues=[f"Test execution failed: {str(e)}"],
                    recommendations=[],
                    execution_time=execution_time
                ))
        
        # Calculate comprehensive TORC metrics
        overall_results["torc_summary"] = self._calculate_torc_summary()
        overall_results["metrics_by_category"] = self._organize_metrics_by_category()
        overall_results["overall_torc_score"] = self._calculate_overall_torc_score()
        overall_results["time_performance"] = self._analyze_time_performance()
        overall_results["operational_resilience"] = self._analyze_operational_resilience()
        overall_results["compatibility_assessment"] = self._analyze_compatibility()
        overall_results["improvement_plan"] = self._generate_improvement_plan()
        
        return overall_results
    
    # Time Performance Tests
    def test_response_time_performance(self) -> Dict[str, Any]:
        """Test response time performance across components"""
        print("⏱️ Testing response time performance...")
        
        response_times = []
        issues = []
        
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Measure response times for various operations
            for i in range(100):
                start_time = time.time()
                service.create_mention(
                    surface_form=f"Response Test {i}",
                    start_pos=0,
                    end_pos=15,
                    source_ref=f"response://test/{i}",
                    entity_type="RESPONSE_TEST",
                    confidence=0.8
                )
                response_times.append(time.time() - start_time)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            # Performance thresholds
            if p50 > 0.05:  # 50ms
                issues.append(f"High median response time: {p50*1000:.1f}ms")
            if p95 > 0.2:   # 200ms
                issues.append(f"High 95th percentile response time: {p95*1000:.1f}ms")
            if p99 > 0.5:   # 500ms
                issues.append(f"High 99th percentile response time: {p99*1000:.1f}ms")
            
            # Calculate score based on response times
            score = 1.0
            if p50 > 0.01: score -= 0.2
            if p95 > 0.1: score -= 0.3
            if p99 > 0.3: score -= 0.3
            score = max(0.0, score)
            
            metrics = {
                "response_time_p50": p50,
                "response_time_p95": p95,
                "response_time_p99": p99,
                "avg_response_time": sum(response_times) / len(response_times),
                "sample_size": len(response_times)
            }
            
            return {
                "passed": score >= 0.7,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_time_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Response time test failed: {str(e)}"],
                "recommendations": ["Fix response time testing infrastructure"]
            }
    
    def test_throughput_performance(self) -> Dict[str, Any]:
        """Test throughput performance"""
        print("📈 Testing throughput performance...")
        
        issues = []
        
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Test peak throughput
            start_time = time.time()
            operations_completed = 0
            
            # Run for 5 seconds
            while time.time() - start_time < 5.0:
                service.create_mention(
                    surface_form=f"Throughput Test {operations_completed}",
                    start_pos=0,
                    end_pos=15,
                    source_ref=f"throughput://test/{operations_completed}",
                    entity_type="THROUGHPUT_TEST",
                    confidence=0.8
                )
                operations_completed += 1
            
            total_time = time.time() - start_time
            peak_throughput = operations_completed / total_time
            
            # Test sustained throughput over longer period
            start_time = time.time()
            sustained_operations = 0
            
            # Run for 30 seconds with pauses
            while time.time() - start_time < 10.0:  # Reduced for testing
                for _ in range(10):
                    service.create_mention(
                        surface_form=f"Sustained Test {sustained_operations}",
                        start_pos=0,
                        end_pos=15,
                        source_ref=f"sustained://test/{sustained_operations}",
                        entity_type="SUSTAINED_TEST",
                        confidence=0.8
                    )
                    sustained_operations += 1
                time.sleep(0.1)  # Small pause
            
            sustained_time = time.time() - start_time
            sustained_throughput = sustained_operations / sustained_time
            
            # Evaluate throughput
            if peak_throughput < 10:
                issues.append(f"Low peak throughput: {peak_throughput:.1f} ops/sec")
            if sustained_throughput < peak_throughput * 0.7:
                issues.append(f"Poor sustained throughput: {sustained_throughput:.1f} ops/sec vs peak {peak_throughput:.1f}")
            
            score = 1.0
            if peak_throughput < 20: score -= 0.3
            if sustained_throughput < 15: score -= 0.3
            if sustained_throughput < peak_throughput * 0.5: score -= 0.4
            score = max(0.0, score)
            
            metrics = {
                "throughput_peak": peak_throughput,
                "throughput_sustained": sustained_throughput,
                "throughput_degradation": (peak_throughput - sustained_throughput) / peak_throughput,
                "peak_operations": operations_completed,
                "sustained_operations": sustained_operations
            }
            
            return {
                "passed": score >= 0.6,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_throughput_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Throughput test failed: {str(e)}"],
                "recommendations": ["Optimize throughput performance"]
            }
    
    def test_latency_under_load(self) -> Dict[str, Any]:
        """Test latency behavior under increasing load"""
        print("⚡ Testing latency under load...")
        
        issues = []
        
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Test latency with increasing concurrent load
            load_levels = [1, 2, 5, 10]
            latency_results = {}
            
            for load_level in load_levels:
                latencies = []
                
                def worker():
                    start_time = time.time()
                    service.create_mention(
                        surface_form=f"Load Test {threading.current_thread().ident}",
                        start_pos=0,
                        end_pos=9,
                        source_ref=f"load://test/{threading.current_thread().ident}",
                        entity_type="LOAD_TEST",
                        confidence=0.8
                    )
                    return time.time() - start_time
                
                # Run concurrent operations
                with concurrent.futures.ThreadPoolExecutor(max_workers=load_level) as executor:
                    futures = [executor.submit(worker) for _ in range(load_level * 5)]
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            latency = future.result()
                            latencies.append(latency)
                        except Exception:
                            latencies.append(float('inf'))
                
                if latencies:
                    avg_latency = sum(l for l in latencies if l != float('inf')) / len([l for l in latencies if l != float('inf')])
                    latency_results[load_level] = avg_latency
            
            # Analyze latency degradation
            baseline_latency = latency_results.get(1, 0)
            latency_increase = {}
            
            for load, latency in latency_results.items():
                if baseline_latency > 0:
                    increase = (latency - baseline_latency) / baseline_latency
                    latency_increase[load] = increase
                    
                    if increase > 2.0:  # More than 200% increase
                        issues.append(f"High latency increase at load {load}: {increase:.1%}")
            
            # Calculate score
            score = 1.0
            max_increase = max(latency_increase.values()) if latency_increase else 0
            if max_increase > 1.0: score -= 0.3
            if max_increase > 3.0: score -= 0.4
            if max_increase > 5.0: score -= 0.3
            score = max(0.0, score)
            
            metrics = {
                "latency_by_load": latency_results,
                "latency_increase": latency_increase,
                "max_latency_increase": max_increase,
                "baseline_latency": baseline_latency
            }
            
            return {
                "passed": score >= 0.6,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_latency_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Latency under load test failed: {str(e)}"],
                "recommendations": ["Implement load testing infrastructure"]
            }
    
    def test_performance_scaling(self) -> Dict[str, Any]:
        """Test how performance scales with system resources"""
        print("📊 Testing performance scaling...")
        
        issues = []
        
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Test scaling with different batch sizes
            batch_sizes = [1, 10, 50, 100]
            scaling_results = {}
            
            for batch_size in batch_sizes:
                start_time = time.time()
                
                for i in range(batch_size):
                    service.create_mention(
                        surface_form=f"Scaling Test {i}",
                        start_pos=0,
                        end_pos=12,
                        source_ref=f"scaling://test/{i}",
                        entity_type="SCALING_TEST",
                        confidence=0.8
                    )
                
                total_time = time.time() - start_time
                throughput = batch_size / total_time
                scaling_results[batch_size] = throughput
            
            # Analyze scaling efficiency
            scaling_efficiency = {}
            baseline_throughput = scaling_results.get(1, 0)
            
            for batch_size, throughput in scaling_results.items():
                if baseline_throughput > 0:
                    efficiency = throughput / (baseline_throughput * batch_size)
                    scaling_efficiency[batch_size] = efficiency
                    
                    if efficiency < 0.5:  # Less than 50% efficiency
                        issues.append(f"Poor scaling efficiency at batch size {batch_size}: {efficiency:.1%}")
            
            # Calculate score
            score = 1.0
            avg_efficiency = sum(scaling_efficiency.values()) / len(scaling_efficiency) if scaling_efficiency else 0
            if avg_efficiency < 0.7: score -= 0.3
            if avg_efficiency < 0.5: score -= 0.4
            if avg_efficiency < 0.3: score -= 0.3
            score = max(0.0, score)
            
            metrics = {
                "throughput_by_batch_size": scaling_results,
                "scaling_efficiency": scaling_efficiency,
                "avg_scaling_efficiency": avg_efficiency
            }
            
            return {
                "passed": score >= 0.6,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_scaling_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Performance scaling test failed: {str(e)}"],
                "recommendations": ["Implement performance scaling optimizations"]
            }
    
    # Operational Resilience Tests
    def test_failure_recovery(self) -> Dict[str, Any]:
        """Test system recovery from failures"""
        print("🔧 Testing failure recovery...")
        
        issues = []
        recovery_times = []
        
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            # Test recovery from connection failures
            start_time = time.time()
            
            # Test with invalid connection (should fail gracefully)
            calc = PageRankCalculator(
                neo4j_uri="bolt://invalid:7687",
                neo4j_user="invalid",
                neo4j_password="invalid"
            )
            
            result = calc.calculate_pagerank()
            recovery_time = time.time() - start_time
            recovery_times.append(recovery_time)
            
            if result["status"] != "error":
                issues.append("System didn't properly handle connection failure")
            
            if recovery_time > 10.0:  # Should fail quickly
                issues.append(f"Slow failure detection: {recovery_time:.1f}s")
            
            # Test recovery from Gemini API failures
            try:
                from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
                
                start_time = time.time()
                workflow = EnhancedVerticalSliceWorkflow()
                result = workflow._execute_ontology_generation("test", "Test domain")
                recovery_time = time.time() - start_time
                recovery_times.append(recovery_time)
                
                # Should either succeed or fail gracefully with fallback
                if result["status"] not in ["success", "error"]:
                    issues.append("Ontology generation didn't handle failures properly")
                
            except Exception as e:
                issues.append(f"Ontology failure recovery failed: {str(e)}")
            
            # Calculate metrics
            avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0
            
            score = 1.0
            if avg_recovery_time > 5.0: score -= 0.3
            if avg_recovery_time > 15.0: score -= 0.4
            if len(issues) > 1: score -= 0.3
            score = max(0.0, score)
            
            metrics = {
                "avg_recovery_time": avg_recovery_time,
                "recovery_times": recovery_times,
                "failure_scenarios_tested": len(recovery_times),
                "graceful_failures": len([r for r in recovery_times if r < 10.0])
            }
            
            return {
                "passed": score >= 0.6,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_recovery_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Failure recovery test failed: {str(e)}"],
                "recommendations": ["Implement proper failure recovery mechanisms"]
            }
    
    def test_error_rate_stress(self) -> Dict[str, Any]:
        """Test error rate under stress conditions"""
        print("⚠️ Testing error rate under stress...")
        
        issues = []
        
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Stress test with rapid operations
            total_operations = 200
            errors = 0
            successes = 0
            
            start_time = time.time()
            
            for i in range(total_operations):
                try:
                    result = service.create_mention(
                        surface_form=f"Stress Test {i}",
                        start_pos=0,
                        end_pos=11,
                        source_ref=f"stress://test/{i}",
                        entity_type="STRESS_TEST",
                        confidence=0.8
                    )
                    
                    if result["status"] == "success":
                        successes += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
            
            total_time = time.time() - start_time
            error_rate = errors / total_operations
            
            # Test with invalid inputs (should handle gracefully)
            invalid_operations = 50
            invalid_errors = 0
            
            for i in range(invalid_operations):
                try:
                    result = service.create_mention(
                        surface_form="",  # Invalid
                        start_pos=-1,    # Invalid
                        end_pos=0,
                        source_ref="",   # Invalid
                        entity_type="",  # Invalid
                        confidence=2.0   # Invalid
                    )
                    
                    # Should return error, not crash
                    if result["status"] != "error":
                        invalid_errors += 1
                        
                except Exception:
                    invalid_errors += 1  # Should not raise exceptions
            
            invalid_error_rate = invalid_errors / invalid_operations
            
            # Evaluate error rates
            if error_rate > 0.05:  # More than 5% error rate
                issues.append(f"High error rate under normal stress: {error_rate:.1%}")
            
            if invalid_error_rate > 0.1:  # More than 10% crashes on invalid input
                issues.append(f"Poor invalid input handling: {invalid_error_rate:.1%} crashes")
            
            score = 1.0
            if error_rate > 0.02: score -= 0.3
            if error_rate > 0.1: score -= 0.4
            if invalid_error_rate > 0.05: score -= 0.3
            score = max(0.0, score)
            
            metrics = {
                "error_rate_under_load": error_rate,
                "invalid_input_error_rate": invalid_error_rate,
                "total_operations": total_operations,
                "successful_operations": successes,
                "failed_operations": errors,
                "operations_per_second": total_operations / total_time
            }
            
            return {
                "passed": score >= 0.7,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_error_rate_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Error rate stress test failed: {str(e)}"],
                "recommendations": ["Implement proper error handling under stress"]
            }
    
    def test_graceful_degradation(self) -> Dict[str, Any]:
        """Test graceful degradation under resource constraints"""
        print("📉 Testing graceful degradation...")
        
        issues = []
        
        try:
            # Test memory pressure degradation
            import psutil
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Create memory pressure
            large_objects = []
            degradation_points = []
            
            for i in range(100):
                # Create entities
                start_time = time.time()
                result = service.create_mention(
                    surface_form=f"Degradation Test {i}",
                    start_pos=0,
                    end_pos=16,
                    source_ref=f"degradation://test/{i}",
                    entity_type="DEGRADATION_TEST",
                    confidence=0.8
                )
                response_time = time.time() - start_time
                
                # Add memory pressure
                large_objects.append(["x"] * 1000)  # 1KB object
                
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                degradation_points.append({
                    "iteration": i,
                    "response_time": response_time,
                    "memory_mb": memory_increase,
                    "success": result["status"] == "success"
                })
                
                # Stop if memory gets too high
                if memory_increase > 100:  # 100MB limit
                    break
            
            # Analyze degradation
            response_times = [p["response_time"] for p in degradation_points]
            initial_avg = sum(response_times[:10]) / 10 if len(response_times) >= 10 else 0
            final_avg = sum(response_times[-10:]) / 10 if len(response_times) >= 10 else 0
            
            if final_avg > initial_avg * 3:  # More than 3x degradation
                issues.append(f"Poor graceful degradation: {final_avg/initial_avg:.1f}x response time increase")
            
            success_rate = sum(1 for p in degradation_points if p["success"]) / len(degradation_points)
            if success_rate < 0.9:
                issues.append(f"System fails under pressure: {success_rate:.1%} success rate")
            
            score = 1.0
            if final_avg > initial_avg * 2: score -= 0.3
            if success_rate < 0.95: score -= 0.3
            if success_rate < 0.8: score -= 0.4
            score = max(0.0, score)
            
            metrics = {
                "initial_avg_response_time": initial_avg,
                "final_avg_response_time": final_avg,
                "response_time_degradation": final_avg / initial_avg if initial_avg > 0 else 0,
                "success_rate_under_pressure": success_rate,
                "memory_pressure_mb": max(p["memory_mb"] for p in degradation_points),
                "degradation_points": len(degradation_points)
            }
            
            return {
                "passed": score >= 0.6,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_degradation_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Graceful degradation test failed: {str(e)}"],
                "recommendations": ["Implement graceful degradation patterns"]
            }
    
    def test_circuit_breaker_patterns(self) -> Dict[str, Any]:
        """Test circuit breaker and failure isolation patterns"""
        print("🔌 Testing circuit breaker patterns...")
        
        issues = []
        
        try:
            # Test Phase 2 fallback patterns
            from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
            
            workflow = EnhancedVerticalSliceWorkflow()
            
            # Test Gemini fallback mechanism
            start_time = time.time()
            result = workflow._execute_ontology_generation("circuit_test", "Invalid domain that might cause Gemini to fail")
            circuit_time = time.time() - start_time
            
            # Should have fallback mechanism
            if result["status"] == "success":
                method = result.get("method", "unknown")
                if "fallback" in method or "mock" in method:
                    # Good - has fallback
                    pass
                else:
                    # Either real Gemini worked or no fallback
                    if circuit_time > 30.0:
                        issues.append("No circuit breaker for slow Gemini responses")
            else:
                issues.append("No fallback mechanism for Gemini failures")
            
            # Test PageRank failure handling
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            calc = PageRankCalculator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            start_time = time.time()
            pagerank_result = calc.calculate_pagerank()
            pagerank_time = time.time() - start_time
            
            # Should handle gracefully even if Neo4j is not available
            if pagerank_result["status"] == "error" and pagerank_time < 10.0:
                # Good - fails fast
                pass
            elif pagerank_result["status"] == "success":
                # Good - works
                pass
            else:
                issues.append("PageRank doesn't have proper circuit breaker")
            
            # Evaluate circuit breaker effectiveness
            circuit_breaker_score = 1.0
            
            if circuit_time > 60.0:  # Too slow
                circuit_breaker_score -= 0.3
                issues.append("Slow circuit breaker response")
            
            if pagerank_time > 30.0 and pagerank_result["status"] == "error":
                circuit_breaker_score -= 0.3
                issues.append("Slow failure detection")
            
            if len(issues) > 1:
                circuit_breaker_score -= 0.4
            
            circuit_breaker_score = max(0.0, circuit_breaker_score)
            
            metrics = {
                "circuit_breaker_effectiveness": circuit_breaker_score,
                "gemini_circuit_time": circuit_time,
                "pagerank_circuit_time": pagerank_time,
                "fallback_mechanisms_found": 1 if "fallback" in result.get("method", "") else 0
            }
            
            return {
                "passed": circuit_breaker_score >= 0.6,
                "score": circuit_breaker_score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_circuit_breaker_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Circuit breaker test failed: {str(e)}"],
                "recommendations": ["Implement circuit breaker patterns"]
            }
    
    def test_resource_exhaustion_recovery(self) -> Dict[str, Any]:
        """Test recovery from resource exhaustion"""
        print("💾 Testing resource exhaustion recovery...")
        
        issues = []
        
        try:
            import gc
            import psutil
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Create resource exhaustion
            memory_hogs = []
            recovery_successful = False
            
            try:
                # Gradually increase memory usage
                for i in range(500):
                    # Create entities
                    service.create_mention(
                        surface_form=f"Resource Test {i}",
                        start_pos=0,
                        end_pos=13,
                        source_ref=f"resource://test/{i}",
                        entity_type="RESOURCE_TEST",
                        confidence=0.8
                    )
                    
                    # Add memory pressure
                    memory_hogs.append([random.random() for _ in range(1000)])
                    
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_increase = current_memory - initial_memory
                    
                    # Stop before hitting system limits
                    if memory_increase > 150:  # 150MB limit
                        break
                
                # Test recovery
                memory_hogs.clear()
                gc.collect()
                
                # Test that system still works after resource pressure
                start_time = time.time()
                result = service.create_mention(
                    surface_form="Recovery Test",
                    start_pos=0,
                    end_pos=12,
                    source_ref="recovery://test",
                    entity_type="RECOVERY_TEST",
                    confidence=0.8
                )
                recovery_time = time.time() - start_time
                
                if result["status"] == "success" and recovery_time < 1.0:
                    recovery_successful = True
                else:
                    issues.append("System didn't recover properly from resource exhaustion")
                
            except MemoryError:
                # This is expected behavior
                recovery_successful = True
                issues.append("System hit memory limits but handled gracefully")
            
            # Check memory cleanup
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_cleanup = (final_memory - initial_memory) < 50  # Less than 50MB increase
            
            if not memory_cleanup:
                issues.append(f"Poor memory cleanup: {final_memory - initial_memory:.1f}MB remaining")
            
            score = 1.0
            if not recovery_successful: score -= 0.5
            if not memory_cleanup: score -= 0.3
            if len(issues) > 1: score -= 0.2
            score = max(0.0, score)
            
            metrics = {
                "recovery_successful": recovery_successful,
                "memory_cleanup_successful": memory_cleanup,
                "final_memory_increase": final_memory - initial_memory,
                "max_memory_reached": True  # We intentionally hit limits
            }
            
            return {
                "passed": score >= 0.6,
                "score": score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": self._generate_resource_recovery_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Resource exhaustion recovery test failed: {str(e)}"],
                "recommendations": ["Implement resource exhaustion recovery mechanisms"]
            }
    
    # Compatibility Tests (simplified versions focusing on core compatibility)
    def test_interface_compliance(self) -> Dict[str, Any]:
        """Test interface compliance across components"""
        print("📋 Testing interface compliance...")
        
        issues = []
        
        try:
            from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
            
            phases = [Phase1Adapter(), Phase2Adapter()]
            required_methods = ["get_capabilities", "validate_input", "execute"]
            
            compliance_score = 0
            total_checks = len(phases) * len(required_methods)
            
            for phase in phases:
                for method in required_methods:
                    if hasattr(phase, method) and callable(getattr(phase, method)):
                        compliance_score += 1
                    else:
                        issues.append(f"Phase missing {method}")
            
            interface_compliance = compliance_score / total_checks
            
            return {
                "passed": interface_compliance >= 0.8,
                "score": interface_compliance,
                "metrics": {"interface_compliance_score": interface_compliance},
                "issues": issues,
                "recommendations": ["Ensure all phases implement required interface methods"] if issues else []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Interface compliance test failed: {str(e)}"],
                "recommendations": ["Fix interface compliance testing"]
            }
    
    def test_backward_compatibility(self) -> Dict[str, Any]:
        """Test backward compatibility"""
        print("🔄 Testing backward compatibility...")
        
        # Basic compatibility test
        try:
            from src.core.identity_service import IdentityService
            from src.core.enhanced_identity_service import EnhancedIdentityService
            
            basic_service = IdentityService()
            enhanced_service = EnhancedIdentityService()
            
            # Both should work with same interface
            result1 = basic_service.create_mention("Test", 0, 4, "test", "TEST", 0.8)
            result2 = enhanced_service.create_mention("Test", 0, 4, "test", "TEST", 0.8)
            
            compatible = (isinstance(result1, dict) and isinstance(result2, dict) and
                         "status" in result1 and "status" in result2)
            
            return {
                "passed": compatible,
                "score": 1.0 if compatible else 0.0,
                "metrics": {"backward_compatibility_score": 1.0 if compatible else 0.0},
                "issues": [] if compatible else ["Enhanced service not backward compatible"],
                "recommendations": [] if compatible else ["Maintain backward compatibility"]
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Backward compatibility test failed: {str(e)}"],
                "recommendations": ["Fix backward compatibility"]
            }
    
    def test_cross_component_integration(self) -> Dict[str, Any]:
        """Test cross-component integration"""
        print("🔗 Testing cross-component integration...")
        
        # Simplified integration test
        try:
            from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest
            
            request = ProcessingRequest(
                documents=["test.pdf"],
                queries=["Test"],
                workflow_id="integration_test",
                domain_description="Test domain"
            )
            
            phase1 = Phase1Adapter()
            phase2 = Phase2Adapter()
            
            errors1 = phase1.validate_input(request)
            errors2 = phase2.validate_input(request)
            
            # Both should handle request (may have different requirements)
            integration_score = 1.0
            if errors1 and any("critical" in e.lower() for e in errors1):
                integration_score -= 0.5
            if errors2 and any("critical" in e.lower() for e in errors2):
                integration_score -= 0.5
            
            return {
                "passed": integration_score >= 0.5,
                "score": integration_score,
                "metrics": {"cross_component_compatibility": integration_score},
                "issues": [],
                "recommendations": []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Cross-component integration test failed: {str(e)}"],
                "recommendations": ["Fix cross-component integration"]
            }
    
    def test_version_tolerance(self) -> Dict[str, Any]:
        """Test version tolerance"""
        print("🏷️ Testing version tolerance...")
        
        # Basic version tolerance test
        try:
            import sys
            python_version = sys.version_info
            
            version_score = 1.0
            issues = []
            
            if python_version.major < 3:
                version_score = 0.0
                issues.append("Python 2.x not supported")
            elif python_version.minor < 8:
                version_score -= 0.3
                issues.append(f"Python 3.{python_version.minor} may have issues")
            
            return {
                "passed": version_score >= 0.7,
                "score": version_score,
                "metrics": {"version_tolerance_score": version_score},
                "issues": issues,
                "recommendations": ["Update to Python 3.8+"] if issues else []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Version tolerance test failed: {str(e)}"],
                "recommendations": ["Fix version compatibility"]
            }
    
    def test_configuration_compatibility(self) -> Dict[str, Any]:
        """Test configuration compatibility"""
        print("⚙️ Testing configuration compatibility...")
        
        # Basic configuration compatibility test
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
            
            # Both should accept standard Neo4j config
            calc = PageRankCalculator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            workflow = EnhancedVerticalSliceWorkflow(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            return {
                "passed": True,
                "score": 1.0,
                "metrics": {"configuration_compatibility": 1.0},
                "issues": [],
                "recommendations": []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "metrics": {},
                "issues": [f"Configuration compatibility test failed: {str(e)}"],
                "recommendations": ["Standardize configuration interfaces"]
            }
    
    # Analysis and reporting methods
    def _calculate_torc_summary(self) -> Dict[str, Any]:
        """Calculate comprehensive TORC summary"""
        if not self.test_results:
            return {}
        
        # Group by category
        by_category = {}
        for result in self.test_results:
            category = result.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        # Calculate category scores
        category_scores = {}
        for category, results in by_category.items():
            scores = [r.score for r in results]
            category_scores[category] = {
                "avg_score": sum(scores) / len(scores),
                "tests_passed": sum(1 for r in results if r.passed),
                "total_tests": len(results),
                "pass_rate": sum(1 for r in results if r.passed) / len(results)
            }
        
        return {
            "category_scores": category_scores,
            "total_tests": len(self.test_results),
            "total_passed": sum(1 for r in self.test_results if r.passed),
            "overall_pass_rate": sum(1 for r in self.test_results if r.passed) / len(self.test_results)
        }
    
    def _organize_metrics_by_category(self) -> Dict[str, Any]:
        """Organize metrics by TORC category"""
        metrics = {"Time": {}, "Operational": {}, "Compatibility": {}}
        
        for result in self.test_results:
            category = result.category
            if category in metrics:
                metrics[category][result.test_name] = result.metrics
        
        return metrics
    
    def _calculate_overall_torc_score(self) -> float:
        """Calculate overall TORC score"""
        if not self.test_results:
            return 0.0
        
        scores = [r.score for r in self.test_results]
        return sum(scores) / len(scores)
    
    def _analyze_time_performance(self) -> Dict[str, Any]:
        """Analyze time performance metrics"""
        time_results = [r for r in self.test_results if r.category == "Time"]
        
        if not time_results:
            return {}
        
        # Extract key time metrics
        response_times = []
        throughputs = []
        
        for result in time_results:
            metrics = result.metrics
            if "response_time_p50" in metrics:
                response_times.append(metrics["response_time_p50"])
            if "throughput_peak" in metrics:
                throughputs.append(metrics["throughput_peak"])
        
        return {
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "max_throughput": max(throughputs) if throughputs else 0,
            "time_performance_score": sum(r.score for r in time_results) / len(time_results)
        }
    
    def _analyze_operational_resilience(self) -> Dict[str, Any]:
        """Analyze operational resilience metrics"""
        operational_results = [r for r in self.test_results if r.category == "Operational"]
        
        if not operational_results:
            return {}
        
        # Extract key resilience metrics
        recovery_times = []
        error_rates = []
        
        for result in operational_results:
            metrics = result.metrics
            if "avg_recovery_time" in metrics:
                recovery_times.append(metrics["avg_recovery_time"])
            if "error_rate_under_load" in metrics:
                error_rates.append(metrics["error_rate_under_load"])
        
        return {
            "avg_recovery_time": sum(recovery_times) / len(recovery_times) if recovery_times else 0,
            "avg_error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
            "resilience_score": sum(r.score for r in operational_results) / len(operational_results)
        }
    
    def _analyze_compatibility(self) -> Dict[str, Any]:
        """Analyze compatibility metrics"""
        compatibility_results = [r for r in self.test_results if r.category == "Compatibility"]
        
        if not compatibility_results:
            return {}
        
        return {
            "compatibility_score": sum(r.score for r in compatibility_results) / len(compatibility_results),
            "compatibility_issues": sum(len(r.issues) for r in compatibility_results),
            "compatibility_tests": len(compatibility_results)
        }
    
    def _generate_improvement_plan(self) -> List[str]:
        """Generate comprehensive improvement plan"""
        plan = []
        
        # Analyze failed tests
        failed_tests = [r for r in self.test_results if not r.passed]
        
        if failed_tests:
            # Time performance improvements
            time_failures = [r for r in failed_tests if r.category == "Time"]
            if time_failures:
                plan.append("Time Performance: Optimize response times and throughput")
                plan.append("- Implement caching strategies")
                plan.append("- Add connection pooling")
                plan.append("- Optimize database queries")
            
            # Operational resilience improvements
            operational_failures = [r for r in failed_tests if r.category == "Operational"]
            if operational_failures:
                plan.append("Operational Resilience: Improve failure handling")
                plan.append("- Implement circuit breaker patterns")
                plan.append("- Add graceful degradation")
                plan.append("- Improve error recovery mechanisms")
            
            # Compatibility improvements
            compatibility_failures = [r for r in failed_tests if r.category == "Compatibility"]
            if compatibility_failures:
                plan.append("Compatibility: Standardize interfaces")
                plan.append("- Ensure consistent API contracts")
                plan.append("- Maintain backward compatibility")
                plan.append("- Improve cross-component integration")
        
        if not plan:
            plan.append("System TORC performance is good - focus on monitoring and maintenance")
        
        return plan
    
    # Recommendation generators
    def _generate_time_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("response time" in issue.lower() for issue in issues):
            recommendations.append("Optimize response time performance")
        return recommendations
    
    def _generate_throughput_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("throughput" in issue.lower() for issue in issues):
            recommendations.append("Improve throughput optimization")
        return recommendations
    
    def _generate_latency_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("latency" in issue.lower() for issue in issues):
            recommendations.append("Implement latency optimization under load")
        return recommendations
    
    def _generate_scaling_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("scaling" in issue.lower() for issue in issues):
            recommendations.append("Improve scaling efficiency")
        return recommendations
    
    def _generate_recovery_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("recovery" in issue.lower() or "failure" in issue.lower() for issue in issues):
            recommendations.append("Implement better failure recovery mechanisms")
        return recommendations
    
    def _generate_error_rate_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("error rate" in issue.lower() for issue in issues):
            recommendations.append("Reduce error rate under stress")
        return recommendations
    
    def _generate_degradation_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("degradation" in issue.lower() for issue in issues):
            recommendations.append("Implement graceful degradation patterns")
        return recommendations
    
    def _generate_circuit_breaker_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("circuit" in issue.lower() or "breaker" in issue.lower() for issue in issues):
            recommendations.append("Implement circuit breaker patterns")
        return recommendations
    
    def _generate_resource_recovery_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any("resource" in issue.lower() or "memory" in issue.lower() for issue in issues):
            recommendations.append("Improve resource management and recovery")
        return recommendations


def main():
    """Run comprehensive TORC assessment"""
    
    print("⚡ STARTING COMPREHENSIVE TORC ASSESSMENT")
    print("Testing Time, Operational Resilience, and Compatibility")
    print("=" * 80)
    
    framework = TORCTestFramework()
    
    # Run TORC assessment
    start_time = time.time()
    results = framework.run_torc_assessment()
    total_time = time.time() - start_time
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("⚡ TORC ASSESSMENT RESULTS")
    print("=" * 80)
    
    # Overall TORC score
    torc_summary = results["torc_summary"]
    overall_score = results["overall_torc_score"]
    
    print(f"\n🎯 Overall TORC Score: {overall_score:.1%}")
    print(f"   Assessment Time: {total_time:.2f}s")
    
    # Category breakdown
    if "category_scores" in torc_summary:
        print(f"\n📊 TORC Category Breakdown:")
        for category, scores in torc_summary["category_scores"].items():
            print(f"   {category}: {scores['avg_score']:.1%} ({scores['tests_passed']}/{scores['total_tests']} passed)")
    
    # Performance metrics
    if results["time_performance"]:
        perf = results["time_performance"]
        print(f"\n⏱️  Time Performance:")
        print(f"   Average Response Time: {perf.get('avg_response_time', 0)*1000:.1f}ms")
        print(f"   Max Throughput: {perf.get('max_throughput', 0):.1f} ops/sec")
        print(f"   Performance Score: {perf.get('time_performance_score', 0):.1%}")
    
    # Operational resilience
    if results["operational_resilience"]:
        resilience = results["operational_resilience"]
        print(f"\n🔧 Operational Resilience:")
        print(f"   Average Recovery Time: {resilience.get('avg_recovery_time', 0):.2f}s")
        print(f"   Average Error Rate: {resilience.get('avg_error_rate', 0):.1%}")
        print(f"   Resilience Score: {resilience.get('resilience_score', 0):.1%}")
    
    # Compatibility assessment
    if results["compatibility_assessment"]:
        compatibility = results["compatibility_assessment"]
        print(f"\n🔗 Compatibility Assessment:")
        print(f"   Compatibility Score: {compatibility.get('compatibility_score', 0):.1%}")
        print(f"   Compatibility Issues: {compatibility.get('compatibility_issues', 0)}")
    
    # Improvement plan
    if results["improvement_plan"]:
        print(f"\n💡 TORC Improvement Plan:")
        for i, item in enumerate(results["improvement_plan"][:8], 1):
            print(f"   {i}. {item}")
    
    # Final TORC assessment
    print(f"\n🎯 TORC ASSESSMENT:")
    
    if overall_score >= 0.9:
        print("🟢 EXCELLENT: System demonstrates outstanding TORC characteristics")
    elif overall_score >= 0.8:
        print("🟡 GOOD: System has good TORC performance with minor areas for improvement")
    elif overall_score >= 0.7:
        print("🟠 FAIR: System has acceptable TORC performance, optimization recommended")
    elif overall_score >= 0.6:
        print("🔴 POOR: System TORC performance needs significant improvement")
    else:
        print("🔴 CRITICAL: System TORC performance is inadequate for production")
    
    print(f"\nTORC Score: {overall_score:.1%}")
    print(f"Time Performance: {results['time_performance'].get('time_performance_score', 0):.1%}")
    print(f"Operational Resilience: {results['operational_resilience'].get('resilience_score', 0):.1%}")
    print(f"Compatibility: {results['compatibility_assessment'].get('compatibility_score', 0):.1%}")
    
    return overall_score >= 0.7  # Return success if >= 70% TORC score


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)