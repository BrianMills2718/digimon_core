#!/usr/bin/env python3
"""
Stress Testing for All GraphRAG Phases
Tests system behavior under high load, concurrent access, and resource constraints
"""

import sys
import time
import threading
import concurrent.futures
import psutil
import os
import random
import gc
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent

@dataclass
class StressTestResult:
    """Result of a stress test"""
    test_name: str
    passed: bool
    throughput: float  # Operations per second
    avg_response_time: float  # Average response time in seconds
    max_response_time: float  # Maximum response time in seconds
    memory_usage_mb: float  # Peak memory usage in MB
    error_rate: float  # Percentage of failed operations
    details: str


class PhaseStressTester:
    """Comprehensive stress testing for all GraphRAG phases"""
    
    def __init__(self):
        self.test_results = []
        self.process = psutil.Process(os.getpid())
        
    def run_all_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests on all phases and components"""
        print("⚡ COMPREHENSIVE PHASE STRESS TESTING")
        print("=" * 80)
        
        stress_tests = [
            ("Phase 1 Entity Extraction Stress", self.stress_test_phase1_extraction),
            ("Phase 1 PageRank Stress", self.stress_test_phase1_pagerank),
            ("Phase 2 Ontology Generation Stress", self.stress_test_phase2_ontology),
            ("Phase 2 Graph Building Stress", self.stress_test_phase2_graph_building),
            ("MCP Tools Concurrent Access", self.stress_test_mcp_concurrent),
            ("Identity Service Load", self.stress_test_identity_service),
            ("Neo4j Connection Pool", self.stress_test_neo4j_connections),
            ("Memory Pressure Test", self.stress_test_memory_pressure),
            ("File System I/O Stress", self.stress_test_file_io),
            ("Cross-Phase Workflow Stress", self.stress_test_cross_phase_workflow)
        ]
        
        overall_results = {
            "stress_test_summary": {},
            "performance_metrics": {},
            "system_health": {},
            "bottlenecks_identified": [],
            "recommendations": []
        }
        
        for test_name, test_func in stress_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            try:
                result = test_func()
                self.test_results.append(result)
                
                overall_results["stress_test_summary"][test_name] = {
                    "passed": result.passed,
                    "throughput": result.throughput,
                    "avg_response_time": result.avg_response_time,
                    "max_response_time": result.max_response_time,
                    "memory_usage_mb": result.memory_usage_mb,
                    "error_rate": result.error_rate
                }
                
                status = "✅ PASSED" if result.passed else "❌ FAILED"
                print(f"{status} {test_name}")
                print(f"   Throughput: {result.throughput:.1f} ops/sec")
                print(f"   Avg Response: {result.avg_response_time*1000:.1f}ms")
                print(f"   Memory: {result.memory_usage_mb:.1f}MB")
                print(f"   Error Rate: {result.error_rate:.1%}")
                
            except Exception as e:
                print(f"❌ {test_name}: FAILED with exception: {e}")
                self.test_results.append(StressTestResult(
                    test_name=test_name,
                    passed=False,
                    throughput=0.0,
                    avg_response_time=0.0,
                    max_response_time=0.0,
                    memory_usage_mb=0.0,
                    error_rate=1.0,
                    details=f"Exception: {str(e)}"
                ))
        
        # Analyze results and generate insights
        overall_results["performance_metrics"] = self._analyze_performance_metrics()
        overall_results["system_health"] = self._assess_system_health()
        overall_results["bottlenecks_identified"] = self._identify_bottlenecks()
        overall_results["recommendations"] = self._generate_stress_recommendations()
        
        return overall_results
    
    def stress_test_phase1_extraction(self) -> StressTestResult:
        """Stress test Phase 1 entity extraction with high load"""
        print("🔍 Testing Phase 1 entity extraction under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.tools.phase1.t23a_spacy_ner import SpacyNER
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Initialize extractor
            extractor = SpacyNER(
                IdentityService(),
                ProvenanceService(),
                QualityService()
            )
            
            # Prepare test data
            test_texts = [
                "Apple Inc. is a technology company founded by Steve Jobs in Cupertino, California.",
                "Microsoft Corporation was established by Bill Gates and Paul Allen in Seattle, Washington.",
                "Google LLC, now part of Alphabet Inc., was founded by Larry Page and Sergey Brin at Stanford University.",
                "Amazon.com Inc. started as an online bookstore by Jeff Bezos in Bellevue, Washington.",
                "Meta Platforms Inc., formerly Facebook, was founded by Mark Zuckerberg at Harvard University."
            ] * 20  # 100 test texts total
            
            # Stress test with concurrent processing
            start_time = time.time()
            response_times = []
            errors = 0
            successful_extractions = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                for i, text in enumerate(test_texts):
                    future = executor.submit(self._extract_entities_timed, extractor, text, f"stress_doc_{i}")
                    futures.append(future)
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        response_time, success = future.result()
                        response_times.append(response_time)
                        if success:
                            successful_extractions += 1
                        else:
                            errors += 1
                    except Exception:
                        errors += 1
                        response_times.append(0.0)
            
            total_time = time.time() - start_time
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Calculate metrics
            throughput = len(test_texts) / total_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            error_rate = errors / len(test_texts)
            
            # Success criteria: >80% success rate, >5 docs/sec, <5s max response time
            passed = (error_rate < 0.2 and throughput > 5 and max_response_time < 5.0)
            
            return StressTestResult(
                test_name="Phase 1 Entity Extraction Stress",
                passed=passed,
                throughput=throughput,
                avg_response_time=avg_response_time,
                max_response_time=max_response_time,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Processed {len(test_texts)} texts, {successful_extractions} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Phase 1 Entity Extraction Stress",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to initialize: {str(e)}"
            )
    
    def stress_test_phase1_pagerank(self) -> StressTestResult:
        """Stress test Phase 1 PageRank with large graphs"""
        print("📊 Testing Phase 1 PageRank under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            # Test PageRank calculation multiple times
            calc = PageRankCalculator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            start_time = time.time()
            response_times = []
            errors = 0
            successful_calculations = 0
            
            # Run PageRank calculations with different parameters
            test_iterations = 20
            
            for i in range(test_iterations):
                iteration_start = time.time()
                try:
                    result = calc.calculate_pagerank()
                    iteration_time = time.time() - iteration_start
                    response_times.append(iteration_time)
                    
                    if result["status"] == "success":
                        successful_calculations += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
                    response_times.append(0.0)
            
            total_time = time.time() - start_time
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Calculate metrics
            throughput = test_iterations / total_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            error_rate = errors / test_iterations
            
            # Success criteria: >70% success rate, <30s max response time
            passed = (error_rate < 0.3 and max_response_time < 30.0)
            
            return StressTestResult(
                test_name="Phase 1 PageRank Stress",
                passed=passed,
                throughput=throughput,
                avg_response_time=avg_response_time,
                max_response_time=max_response_time,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Ran {test_iterations} PageRank calculations, {successful_calculations} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Phase 1 PageRank Stress",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to initialize: {str(e)}"
            )
    
    def stress_test_phase2_ontology(self) -> StressTestResult:
        """Stress test Phase 2 ontology generation"""
        print("🧠 Testing Phase 2 ontology generation under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
            
            workflow = EnhancedVerticalSliceWorkflow()
            
            # Test multiple ontology generations
            test_domains = [
                "Climate change and environmental policy",
                "Healthcare and medical research",
                "Financial technology and blockchain",
                "Artificial intelligence and machine learning",
                "Space exploration and astronomy",
                "Renewable energy and sustainability",
                "Cybersecurity and data protection",
                "Biotechnology and genetic engineering",
                "Transportation and autonomous vehicles",
                "Education technology and e-learning"
            ]
            
            start_time = time.time()
            response_times = []
            errors = 0
            successful_generations = 0
            
            for domain in test_domains:
                iteration_start = time.time()
                try:
                    result = workflow._execute_ontology_generation("stress_test", domain)
                    iteration_time = time.time() - iteration_start
                    response_times.append(iteration_time)
                    
                    if result["status"] == "success":
                        successful_generations += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
                    response_times.append(0.0)
            
            total_time = time.time() - start_time
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Calculate metrics
            throughput = len(test_domains) / total_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            error_rate = errors / len(test_domains)
            
            # Success criteria: >70% success rate (accounting for Gemini fallbacks), <60s max response time
            passed = (error_rate < 0.3 and max_response_time < 60.0)
            
            return StressTestResult(
                test_name="Phase 2 Ontology Generation Stress",
                passed=passed,
                throughput=throughput,
                avg_response_time=avg_response_time,
                max_response_time=max_response_time,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Generated ontologies for {len(test_domains)} domains, {successful_generations} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Phase 2 Ontology Generation Stress",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to initialize: {str(e)}"
            )
    
    def stress_test_phase2_graph_building(self) -> StressTestResult:
        """Stress test Phase 2 graph building with large datasets"""
        print("🔨 Testing Phase 2 graph building under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
            from src.tools.phase2.t23c_ontology_aware_extractor import ExtractionResult
            from src.core.identity_service import Entity, Relationship
            
            # Initialize graph builder
            builder = OntologyAwareGraphBuilder()
            
            # Create mock extraction results with many entities
            entities = []
            relationships = []
            
            # Generate test entities
            for i in range(1000):
                entity = Entity(
                    id=f"entity_{i}",
                    canonical_name=f"Test Entity {i}",
                    entity_type="TEST_TYPE",
                    confidence=0.8,
                    attributes={"source": "stress_test"}
                )
                entities.append(entity)
            
            # Generate test relationships
            for i in range(0, 1000, 2):
                if i + 1 < len(entities):
                    relationship = Relationship(
                        id=f"rel_{i}",
                        source_id=entities[i].id,
                        target_id=entities[i+1].id,
                        relationship_type="RELATED_TO",
                        confidence=0.7,
                        attributes={"source": "stress_test"}
                    )
                    relationships.append(relationship)
            
            extraction_result = ExtractionResult(
                entities=entities,
                relationships=relationships,
                mentions=[],
                extraction_metadata={"source": "stress_test"}
            )
            
            start_time = time.time()
            
            try:
                # This is resource-intensive, so we test it once with large data
                build_result = builder.build_graph_from_extraction(
                    extraction_result=extraction_result,
                    source_document="stress_test_document"
                )
                
                total_time = time.time() - start_time
                peak_memory = self.process.memory_info().rss / 1024 / 1024
                
                # Check if build was successful
                success = (build_result.entities_created > 0 and 
                          build_result.relationships_created > 0 and
                          len(build_result.errors) == 0)
                
                throughput = (len(entities) + len(relationships)) / total_time
                
                return StressTestResult(
                    test_name="Phase 2 Graph Building Stress",
                    passed=success,
                    throughput=throughput,
                    avg_response_time=total_time,
                    max_response_time=total_time,
                    memory_usage_mb=peak_memory - initial_memory,
                    error_rate=0.0 if success else 1.0,
                    details=f"Built graph with {build_result.entities_created} entities, {build_result.relationships_created} relationships"
                )
                
            except Exception as e:
                total_time = time.time() - start_time
                return StressTestResult(
                    test_name="Phase 2 Graph Building Stress",
                    passed=False,
                    throughput=0.0,
                    avg_response_time=total_time,
                    max_response_time=total_time,
                    memory_usage_mb=0.0,
                    error_rate=1.0,
                    details=f"Graph building failed: {str(e)}"
                )
                
        except Exception as e:
            return StressTestResult(
                test_name="Phase 2 Graph Building Stress",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to initialize: {str(e)}"
            )
    
    def stress_test_mcp_concurrent(self) -> StressTestResult:
        """Stress test MCP tools with concurrent access"""
        print("🔧 Testing MCP tools under concurrent access...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.core.identity_service import IdentityService
            
            # Test concurrent access to identity service
            service = IdentityService()
            
            start_time = time.time()
            response_times = []
            errors = 0
            successful_operations = 0
            
            # Concurrent operations
            def create_entities_batch(thread_id, batch_size=50):
                thread_response_times = []
                thread_errors = 0
                thread_successes = 0
                
                for i in range(batch_size):
                    op_start = time.time()
                    try:
                        result = service.create_mention(
                            surface_form=f"Concurrent Entity {thread_id}_{i}",
                            start_pos=0,
                            end_pos=10,
                            source_ref=f"concurrent://thread/{thread_id}/entity/{i}",
                            entity_type="CONCURRENT",
                            confidence=0.8
                        )
                        op_time = time.time() - op_start
                        thread_response_times.append(op_time)
                        
                        if result["status"] == "success":
                            thread_successes += 1
                        else:
                            thread_errors += 1
                            
                    except Exception:
                        thread_errors += 1
                        thread_response_times.append(0.0)
                
                return thread_response_times, thread_errors, thread_successes
            
            # Run concurrent threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for thread_id in range(8):
                    future = executor.submit(create_entities_batch, thread_id, 25)
                    futures.append(future)
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        thread_times, thread_errors, thread_successes = future.result()
                        response_times.extend(thread_times)
                        errors += thread_errors
                        successful_operations += thread_successes
                    except Exception:
                        errors += 25  # Assume all operations in thread failed
            
            total_time = time.time() - start_time
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            total_operations = 8 * 25  # 8 threads × 25 operations each
            throughput = total_operations / total_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            error_rate = errors / total_operations
            
            # Success criteria: >80% success rate, >20 ops/sec
            passed = (error_rate < 0.2 and throughput > 20)
            
            return StressTestResult(
                test_name="MCP Tools Concurrent Access",
                passed=passed,
                throughput=throughput,
                avg_response_time=avg_response_time,
                max_response_time=max_response_time,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Concurrent access: {total_operations} operations, {successful_operations} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="MCP Tools Concurrent Access",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to initialize: {str(e)}"
            )
    
    def stress_test_identity_service(self) -> StressTestResult:
        """Stress test identity service with high load"""
        print("🆔 Testing Identity Service under high load...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # High-volume entity creation
            start_time = time.time()
            response_times = []
            errors = 0
            successful_operations = 0
            
            # Create 1000 entities rapidly
            for i in range(1000):
                op_start = time.time()
                try:
                    result = service.create_mention(
                        surface_form=f"Load Test Entity {i}",
                        start_pos=0,
                        end_pos=15,
                        source_ref=f"load://test/{i}",
                        entity_type="LOAD_TEST",
                        confidence=0.8
                    )
                    op_time = time.time() - op_start
                    response_times.append(op_time)
                    
                    if result["status"] == "success":
                        successful_operations += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
                    response_times.append(0.0)
            
            total_time = time.time() - start_time
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            throughput = 1000 / total_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            error_rate = errors / 1000
            
            # Success criteria: >90% success rate, >50 ops/sec
            passed = (error_rate < 0.1 and throughput > 50)
            
            return StressTestResult(
                test_name="Identity Service Load",
                passed=passed,
                throughput=throughput,
                avg_response_time=avg_response_time,
                max_response_time=max_response_time,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Created 1000 entities, {successful_operations} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Identity Service Load",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to initialize: {str(e)}"
            )
    
    def stress_test_neo4j_connections(self) -> StressTestResult:
        """Stress test Neo4j connection handling"""
        print("🗄️ Testing Neo4j connection pool under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            # Create multiple PageRank calculators (connection pool stress)
            calculators = []
            start_time = time.time()
            errors = 0
            successful_connections = 0
            
            for i in range(20):
                try:
                    calc = PageRankCalculator(
                        neo4j_uri="bolt://localhost:7687",
                        neo4j_user="neo4j",
                        neo4j_password="password"
                    )
                    calculators.append(calc)
                    
                    # Test that connection works
                    tool_info = calc.get_tool_info()
                    if tool_info.get("neo4j_connected", False):
                        successful_connections += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
            
            total_time = time.time() - start_time
            
            # Clean up connections
            for calc in calculators:
                try:
                    calc.close()
                except:
                    pass
            
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            throughput = 20 / total_time
            error_rate = errors / 20
            
            # Success criteria: >80% successful connections
            passed = (error_rate < 0.2)
            
            return StressTestResult(
                test_name="Neo4j Connection Pool",
                passed=passed,
                throughput=throughput,
                avg_response_time=total_time / 20,
                max_response_time=total_time / 20,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Created 20 connections, {successful_connections} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Neo4j Connection Pool",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed to test connections: {str(e)}"
            )
    
    def stress_test_memory_pressure(self) -> StressTestResult:
        """Test system behavior under memory pressure"""
        print("💾 Testing system under memory pressure...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.core.identity_service import IdentityService
            
            # Create memory pressure by holding many objects
            service = IdentityService()
            large_objects = []
            
            start_time = time.time()
            operations_completed = 0
            
            # Gradually increase memory usage
            for i in range(500):
                try:
                    # Create entities and keep references
                    result = service.create_mention(
                        surface_form=f"Memory Pressure Entity {i}",
                        start_pos=0,
                        end_pos=20,
                        source_ref=f"memory://pressure/{i}",
                        entity_type="MEMORY_PRESSURE",
                        confidence=0.8
                    )
                    
                    # Create additional memory pressure
                    large_data = {
                        "entity_id": result.get("entity_id"),
                        "large_text": "A" * 1000,  # 1KB per entity
                        "metadata": {"index": i, "data": list(range(100))}
                    }
                    large_objects.append(large_data)
                    
                    operations_completed += 1
                    
                    # Check memory usage periodically
                    if i % 100 == 0:
                        current_memory = self.process.memory_info().rss / 1024 / 1024
                        memory_increase = current_memory - initial_memory
                        
                        # If memory usage gets too high, break
                        if memory_increase > 200:  # 200MB limit
                            break
                            
                except Exception:
                    break
            
            total_time = time.time() - start_time
            
            # Force garbage collection
            gc.collect()
            
            final_memory = self.process.memory_info().rss / 1024 / 1024
            memory_usage = final_memory - initial_memory
            
            throughput = operations_completed / total_time if total_time > 0 else 0
            
            # Success criteria: Complete at least 300 operations without crashing
            passed = (operations_completed >= 300)
            
            return StressTestResult(
                test_name="Memory Pressure Test",
                passed=passed,
                throughput=throughput,
                avg_response_time=total_time / operations_completed if operations_completed > 0 else 0,
                max_response_time=total_time / operations_completed if operations_completed > 0 else 0,
                memory_usage_mb=memory_usage,
                error_rate=0.0 if operations_completed > 0 else 1.0,
                details=f"Completed {operations_completed} operations under memory pressure"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Memory Pressure Test",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Failed under memory pressure: {str(e)}"
            )
    
    def stress_test_file_io(self) -> StressTestResult:
        """Test file I/O operations under stress"""
        print("📁 Testing file I/O under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            import tempfile
            import os
            
            # Create temporary directory for stress testing
            with tempfile.TemporaryDirectory() as temp_dir:
                start_time = time.time()
                files_created = 0
                errors = 0
                
                # Create many temporary files rapidly
                for i in range(100):
                    try:
                        file_path = os.path.join(temp_dir, f"stress_test_{i}.txt")
                        with open(file_path, 'w') as f:
                            f.write(f"Stress test content {i}\n" * 100)  # ~2KB per file
                        files_created += 1
                    except Exception:
                        errors += 1
                
                # Read files back
                files_read = 0
                for i in range(files_created):
                    try:
                        file_path = os.path.join(temp_dir, f"stress_test_{i}.txt")
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if content:
                                files_read += 1
                    except Exception:
                        errors += 1
                
                total_time = time.time() - start_time
                peak_memory = self.process.memory_info().rss / 1024 / 1024
                
                total_operations = files_created + files_read
                throughput = total_operations / total_time if total_time > 0 else 0
                error_rate = errors / (200) if total_operations > 0 else 1.0  # 100 writes + 100 reads expected
                
                # Success criteria: >90% successful file operations
                passed = (error_rate < 0.1 and files_created >= 90)
                
                return StressTestResult(
                    test_name="File System I/O Stress",
                    passed=passed,
                    throughput=throughput,
                    avg_response_time=total_time / total_operations if total_operations > 0 else 0,
                    max_response_time=total_time / total_operations if total_operations > 0 else 0,
                    memory_usage_mb=peak_memory - initial_memory,
                    error_rate=error_rate,
                    details=f"Created {files_created} files, read {files_read} files"
                )
            
        except Exception as e:
            return StressTestResult(
                test_name="File System I/O Stress",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"File I/O stress test failed: {str(e)}"
            )
    
    def stress_test_cross_phase_workflow(self) -> StressTestResult:
        """Test complete workflow under stress"""
        print("🔄 Testing cross-phase workflow under stress...")
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            from src.core.phase_adapters import Phase1Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest
            
            adapter = Phase1Adapter()
            
            start_time = time.time()
            successful_workflows = 0
            errors = 0
            
            # Run multiple workflow iterations
            for i in range(5):  # Reduced to 5 for stress testing
                try:
                    request = ProcessingRequest(
                        documents=["examples/pdfs/wiki1.pdf"],
                        queries=[f"What are the main entities in iteration {i}?"],
                        workflow_id=f"stress_workflow_{i}"
                    )
                    
                    # Validate input
                    validation_errors = adapter.validate_input(request)
                    if validation_errors:
                        errors += 1
                        continue
                    
                    # Execute workflow (this is resource-intensive)
                    result = adapter.execute(request)
                    
                    if result.status.value == "success":
                        successful_workflows += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
            
            total_time = time.time() - start_time
            peak_memory = self.process.memory_info().rss / 1024 / 1024
            
            total_workflows = 5
            throughput = total_workflows / total_time if total_time > 0 else 0
            error_rate = errors / total_workflows
            
            # Success criteria: >60% successful workflows (workflows are resource-intensive)
            passed = (error_rate < 0.4 and successful_workflows > 0)
            
            return StressTestResult(
                test_name="Cross-Phase Workflow Stress",
                passed=passed,
                throughput=throughput,
                avg_response_time=total_time / total_workflows,
                max_response_time=total_time / total_workflows,
                memory_usage_mb=peak_memory - initial_memory,
                error_rate=error_rate,
                details=f"Ran {total_workflows} workflows, {successful_workflows} successful"
            )
            
        except Exception as e:
            return StressTestResult(
                test_name="Cross-Phase Workflow Stress",
                passed=False,
                throughput=0.0,
                avg_response_time=0.0,
                max_response_time=0.0,
                memory_usage_mb=0.0,
                error_rate=1.0,
                details=f"Workflow stress test failed: {str(e)}"
            )
    
    def _extract_entities_timed(self, extractor, text: str, doc_ref: str) -> tuple:
        """Helper method to extract entities with timing"""
        start_time = time.time()
        try:
            result = extractor.extract_entities(
                chunk_ref=doc_ref,
                text=text,
                chunk_confidence=0.8
            )
            response_time = time.time() - start_time
            success = result["status"] == "success"
            return response_time, success
        except Exception:
            response_time = time.time() - start_time
            return response_time, False
    
    def _analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze performance metrics across all stress tests"""
        if not self.test_results:
            return {}
        
        throughputs = [r.throughput for r in self.test_results if r.throughput > 0]
        response_times = [r.avg_response_time for r in self.test_results if r.avg_response_time > 0]
        memory_usages = [r.memory_usage_mb for r in self.test_results if r.memory_usage_mb > 0]
        error_rates = [r.error_rate for r in self.test_results]
        
        return {
            "avg_throughput": sum(throughputs) / len(throughputs) if throughputs else 0,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "avg_memory_usage": sum(memory_usages) / len(memory_usages) if memory_usages else 0,
            "avg_error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
            "max_throughput": max(throughputs) if throughputs else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "max_memory_usage": max(memory_usages) if memory_usages else 0
        }
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health based on stress test results"""
        passed_tests = sum(1 for r in self.test_results if r.passed)
        total_tests = len(self.test_results)
        
        health_score = passed_tests / total_tests if total_tests > 0 else 0
        
        if health_score >= 0.8:
            health_status = "Excellent"
        elif health_score >= 0.6:
            health_status = "Good"
        elif health_score >= 0.4:
            health_status = "Fair"
        else:
            health_status = "Poor"
        
        return {
            "overall_health_score": health_score,
            "health_status": health_status,
            "tests_passed": passed_tests,
            "total_tests": total_tests,
            "critical_failures": [r.test_name for r in self.test_results if not r.passed and r.error_rate > 0.5]
        }
    
    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks from stress test results"""
        bottlenecks = []
        
        for result in self.test_results:
            if result.avg_response_time > 5.0:  # Slow response time
                bottlenecks.append(f"{result.test_name}: Slow response time ({result.avg_response_time:.2f}s)")
            
            if result.throughput < 1.0 and result.throughput > 0:  # Low throughput
                bottlenecks.append(f"{result.test_name}: Low throughput ({result.throughput:.2f} ops/sec)")
            
            if result.memory_usage_mb > 100:  # High memory usage
                bottlenecks.append(f"{result.test_name}: High memory usage ({result.memory_usage_mb:.1f}MB)")
            
            if result.error_rate > 0.2:  # High error rate
                bottlenecks.append(f"{result.test_name}: High error rate ({result.error_rate:.1%})")
        
        return bottlenecks
    
    def _generate_stress_recommendations(self) -> List[str]:
        """Generate recommendations based on stress test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if not r.passed]
        
        if any("Memory" in r.test_name for r in failed_tests):
            recommendations.append("Implement memory optimization: connection pooling, object reuse, garbage collection tuning")
        
        if any("Concurrent" in r.test_name for r in failed_tests):
            recommendations.append("Improve concurrency handling: thread safety, lock optimization, async processing")
        
        if any("PageRank" in r.test_name for r in failed_tests):
            recommendations.append("Optimize PageRank algorithm: graph caching, incremental updates, parallel processing")
        
        if any("Neo4j" in r.test_name for r in failed_tests):
            recommendations.append("Enhance Neo4j performance: connection pooling, query optimization, indexing")
        
        if any("File" in r.test_name for r in failed_tests):
            recommendations.append("Optimize file I/O: buffering, streaming, async file operations")
        
        # Performance-specific recommendations
        slow_tests = [r for r in self.test_results if r.avg_response_time > 3.0]
        if slow_tests:
            recommendations.append("Address slow response times: caching, indexing, algorithm optimization")
        
        high_memory_tests = [r for r in self.test_results if r.memory_usage_mb > 50]
        if high_memory_tests:
            recommendations.append("Reduce memory usage: object pooling, streaming processing, memory profiling")
        
        if not recommendations:
            recommendations.append("System performance is good under stress - consider increasing test intensity")
        
        return recommendations


def main():
    """Run comprehensive stress testing"""
    
    print("⚡ STARTING COMPREHENSIVE STRESS TESTING")
    print("Testing all GraphRAG phases under high load and stress conditions")
    print("=" * 80)
    
    tester = PhaseStressTester()
    
    # Run all stress tests
    start_time = time.time()
    results = tester.run_all_stress_tests()
    total_time = time.time() - start_time
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("⚡ STRESS TESTING RESULTS SUMMARY")
    print("=" * 80)
    
    # Overall statistics
    stress_summary = results["stress_test_summary"]
    passed_tests = sum(1 for test in stress_summary.values() if test["passed"])
    total_tests = len(stress_summary)
    
    print(f"\n📊 Stress Test Results:")
    print(f"   Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests:.1%})")
    print(f"   Total Test Time: {total_time:.2f}s")
    
    # Performance metrics
    if results["performance_metrics"]:
        perf = results["performance_metrics"]
        print(f"\n📈 Performance Metrics:")
        print(f"   Average Throughput: {perf.get('avg_throughput', 0):.1f} ops/sec")
        print(f"   Average Response Time: {perf.get('avg_response_time', 0)*1000:.1f}ms")
        print(f"   Average Memory Usage: {perf.get('avg_memory_usage', 0):.1f}MB")
        print(f"   Average Error Rate: {perf.get('avg_error_rate', 0):.1%}")
    
    # System health
    if results["system_health"]:
        health = results["system_health"]
        print(f"\n🏥 System Health Assessment:")
        print(f"   Overall Health: {health['health_status']} ({health['overall_health_score']:.1%})")
        if health["critical_failures"]:
            print(f"   Critical Failures: {', '.join(health['critical_failures'])}")
    
    # Bottlenecks
    if results["bottlenecks_identified"]:
        print(f"\n🚧 Performance Bottlenecks Identified:")
        for i, bottleneck in enumerate(results["bottlenecks_identified"][:5], 1):
            print(f"   {i}. {bottleneck}")
    
    # Test details
    print(f"\n🔍 Individual Test Results:")
    for test_name, test_result in stress_summary.items():
        status_icon = "✅" if test_result["passed"] else "❌"
        print(f"   {status_icon} {test_name}")
        print(f"      Throughput: {test_result['throughput']:.1f} ops/sec")
        print(f"      Response Time: {test_result['avg_response_time']*1000:.1f}ms")
        print(f"      Memory: {test_result['memory_usage_mb']:.1f}MB")
        print(f"      Error Rate: {test_result['error_rate']:.1%}")
    
    # Recommendations
    if results["recommendations"]:
        print(f"\n💡 Stress Testing Recommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    # Final assessment
    overall_health = passed_tests / total_tests
    print(f"\n🎯 STRESS TESTING ASSESSMENT:")
    
    if overall_health >= 0.8:
        print("🟢 EXCELLENT: System handles stress very well")
    elif overall_health >= 0.6:
        print("🟡 GOOD: System handles most stress conditions adequately")
    elif overall_health >= 0.4:
        print("🟠 FAIR: System shows stress under high load, optimization needed")
    else:
        print("🔴 POOR: System fails under stress, requires immediate optimization")
    
    print(f"\nStress Resistance Score: {overall_health:.1%}")
    
    return overall_health >= 0.6  # Return success if >= 60% pass rate for stress tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)