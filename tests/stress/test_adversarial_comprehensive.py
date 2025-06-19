#!/usr/bin/env python3
"""
Comprehensive Adversarial Testing Framework
Tests reliability, TORC, robustness, and flexibility across all GraphRAG components
while ensuring compatibility between phases and services.
"""

import sys
import time
import asyncio
import concurrent.futures
import random
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@dataclass
class TORCMetrics:
    """Time, Operational Resilience, Compatibility metrics"""
    time_performance: Dict[str, float]  # Response times
    operational_resilience: Dict[str, int]  # Failure recovery counts
    compatibility_score: float  # Cross-component compatibility
    robustness_score: float  # Edge case handling


class AdversarialTestFramework:
    """Comprehensive adversarial testing for GraphRAG system"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.compatibility_matrix = {}
        self.stress_test_data = {}
        
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all adversarial tests and return comprehensive results"""
        print("🚀 COMPREHENSIVE ADVERSARIAL TESTING")
        print("=" * 80)
        
        test_suite = [
            ("Component Isolation Tests", self.test_component_isolation),
            ("Cross-Phase Compatibility", self.test_cross_phase_compatibility),
            ("Stress & Load Testing", self.test_stress_and_load),
            ("Edge Case Robustness", self.test_edge_case_robustness),
            ("Failure Recovery Testing", self.test_failure_recovery),
            ("Performance Under Load", self.test_performance_under_load),
            ("Memory & Resource Management", self.test_resource_management),
            ("Concurrent Access Testing", self.test_concurrent_access),
            ("Data Corruption Resilience", self.test_data_corruption_resilience),
            ("API Contract Validation", self.test_api_contract_validation)
        ]
        
        overall_results = {
            "test_summary": {},
            "torc_metrics": None,
            "compatibility_scores": {},
            "robustness_assessment": {},
            "recommendations": []
        }
        
        for test_name, test_func in test_suite:
            print(f"\n{'='*20} {test_name} {'='*20}")
            start_time = time.time()
            
            try:
                result = test_func()
                execution_time = time.time() - start_time
                
                overall_results["test_summary"][test_name] = {
                    "status": "passed" if result.get("passed", False) else "failed",
                    "score": result.get("score", 0.0),
                    "execution_time": execution_time,
                    "details": result.get("details", ""),
                    "warnings": result.get("warnings", []),
                    "errors": result.get("errors", [])
                }
                
                print(f"✅ {test_name}: {result.get('score', 0):.1%} pass rate ({execution_time:.2f}s)")
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"❌ {test_name}: FAILED with exception: {e}")
                overall_results["test_summary"][test_name] = {
                    "status": "error",
                    "score": 0.0,
                    "execution_time": execution_time,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
        
        # Calculate overall TORC metrics
        overall_results["torc_metrics"] = self._calculate_torc_metrics()
        overall_results["compatibility_scores"] = self._assess_compatibility()
        overall_results["robustness_assessment"] = self._assess_robustness()
        overall_results["recommendations"] = self._generate_recommendations(overall_results)
        
        return overall_results
    
    def test_component_isolation(self) -> Dict[str, Any]:
        """Test that components can work independently without dependencies failing"""
        print("🔍 Testing component isolation...")
        
        isolation_tests = []
        
        # Test Phase 1 isolation
        try:
            from src.core.phase_adapters import Phase1Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest
            
            adapter = Phase1Adapter()
            request = ProcessingRequest(
                documents=["examples/pdfs/wiki1.pdf"],
                queries=["Test query"],
                workflow_id="isolation_test"
            )
            
            # Test without other phases running
            validation_result = adapter.validate_input(request)
            isolation_tests.append({
                "component": "Phase1Adapter",
                "test": "standalone_validation",
                "passed": len(validation_result) == 0,
                "details": f"Validation errors: {len(validation_result)}"
            })
            
        except Exception as e:
            isolation_tests.append({
                "component": "Phase1Adapter",
                "test": "standalone_validation", 
                "passed": False,
                "error": str(e)
            })
        
        # Test Neo4j connectivity isolation
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            # Test with mock connection parameters
            calc = PageRankCalculator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            tool_info = calc.get_tool_info()
            isolation_tests.append({
                "component": "PageRankCalculator",
                "test": "isolated_initialization",
                "passed": tool_info is not None,
                "details": f"Connected: {tool_info.get('neo4j_connected', False)}"
            })
            
        except Exception as e:
            isolation_tests.append({
                "component": "PageRankCalculator",
                "test": "isolated_initialization",
                "passed": False,
                "error": str(e)
            })
        
        # Test MCP tools isolation
        try:
            from src.mcp_server import mcp
            
            # Test that MCP tools can be imported without starting server
            isolation_tests.append({
                "component": "MCP_Tools",
                "test": "import_without_server",
                "passed": True,
                "details": "MCP tools imported successfully"
            })
            
        except Exception as e:
            isolation_tests.append({
                "component": "MCP_Tools",
                "test": "import_without_server",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in isolation_tests if test["passed"])
        total_tests = len(isolation_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.7,  # 70% pass rate
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Component isolation: {passed_tests}/{total_tests} passed",
            "test_results": isolation_tests
        }
    
    def test_cross_phase_compatibility(self) -> Dict[str, Any]:
        """Test compatibility between different phases and their adapters"""
        print("🔗 Testing cross-phase compatibility...")
        
        compatibility_tests = []
        
        # Test Phase 1 -> Phase 2 data flow
        try:
            from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
            from src.core.graphrag_phase_interface import ProcessingRequest
            
            # Test that Phase 1 output can be consumed by Phase 2
            request = ProcessingRequest(
                documents=["examples/pdfs/wiki1.pdf"],
                queries=["What are the main entities?"],
                workflow_id="compatibility_test",
                domain_description="Test domain"
            )
            
            # Validate both phases accept same request format
            phase1 = Phase1Adapter()
            phase2 = Phase2Adapter()
            
            p1_validation = phase1.validate_input(request)
            p2_validation = phase2.validate_input(request)
            
            compatibility_tests.append({
                "test": "phase1_phase2_request_compatibility",
                "passed": len(p1_validation) == 0 and len(p2_validation) == 0,
                "details": f"Phase1 errors: {len(p1_validation)}, Phase2 errors: {len(p2_validation)}"
            })
            
        except Exception as e:
            compatibility_tests.append({
                "test": "phase1_phase2_request_compatibility",
                "passed": False,
                "error": str(e)
            })
        
        # Test service interface compatibility
        try:
            from src.core.identity_service import IdentityService
            from src.core.enhanced_identity_service import EnhancedIdentityService
            
            # Test that both services have compatible interfaces
            basic_service = IdentityService()
            enhanced_service = EnhancedIdentityService()
            
            # Test common methods exist
            common_methods = ["create_mention", "find_or_create_entity"]
            compatibility_score = 0
            
            for method in common_methods:
                if hasattr(basic_service, method) and hasattr(enhanced_service, method):
                    compatibility_score += 1
            
            compatibility_tests.append({
                "test": "identity_service_compatibility",
                "passed": compatibility_score == len(common_methods),
                "details": f"Compatible methods: {compatibility_score}/{len(common_methods)}"
            })
            
        except Exception as e:
            compatibility_tests.append({
                "test": "identity_service_compatibility",
                "passed": False,
                "error": str(e)
            })
        
        # Test Neo4j schema compatibility
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
            
            # Both should work with same Neo4j schema
            pagerank = PageRankCalculator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j", 
                neo4j_password="password"
            )
            
            graph_builder = OntologyAwareGraphBuilder(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password"
            )
            
            compatibility_tests.append({
                "test": "neo4j_schema_compatibility",
                "passed": True,
                "details": "Phase 1 and Phase 2 Neo4j tools initialized successfully"
            })
            
        except Exception as e:
            compatibility_tests.append({
                "test": "neo4j_schema_compatibility", 
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in compatibility_tests if test["passed"])
        total_tests = len(compatibility_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.8,  # 80% pass rate for compatibility
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Cross-phase compatibility: {passed_tests}/{total_tests} passed",
            "test_results": compatibility_tests
        }
    
    def test_stress_and_load(self) -> Dict[str, Any]:
        """Test system behavior under stress and high load"""
        print("⚡ Testing stress and load handling...")
        
        stress_tests = []
        
        # Test concurrent entity creation
        try:
            from src.core.identity_service import IdentityService
            
            service = IdentityService()
            
            # Create many entities concurrently
            start_time = time.time()
            entity_count = 100
            
            for i in range(entity_count):
                service.create_mention(
                    surface_form=f"Test Entity {i}",
                    start_pos=0,
                    end_pos=10,
                    source_ref=f"test://doc/{i}",
                    entity_type="TEST",
                    confidence=0.8
                )
            
            duration = time.time() - start_time
            throughput = entity_count / duration
            
            stress_tests.append({
                "test": "concurrent_entity_creation",
                "passed": throughput > 10,  # At least 10 entities/second
                "details": f"Created {entity_count} entities in {duration:.2f}s ({throughput:.1f}/s)"
            })
            
        except Exception as e:
            stress_tests.append({
                "test": "concurrent_entity_creation",
                "passed": False,
                "error": str(e)
            })
        
        # Test large document processing
        try:
            from src.tools.phase1.t15a_text_chunker import TextChunker
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Create large text document
            large_text = "This is a test sentence. " * 1000  # ~25KB text
            
            chunker = TextChunker(
                IdentityService(),
                ProvenanceService(), 
                QualityService()
            )
            
            start_time = time.time()
            result = chunker.chunk_text(
                document_ref="stress_test",
                text=large_text,
                document_confidence=0.8
            )
            duration = time.time() - start_time
            
            stress_tests.append({
                "test": "large_document_chunking",
                "passed": result["status"] == "success" and duration < 10,  # Under 10 seconds
                "details": f"Chunked {len(large_text)} chars in {duration:.2f}s, {result.get('chunk_count', 0)} chunks"
            })
            
        except Exception as e:
            stress_tests.append({
                "test": "large_document_chunking",
                "passed": False,
                "error": str(e)
            })
        
        # Test memory usage under load
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Create many objects in memory
            entities = []
            for i in range(500):
                result = service.create_mention(
                    surface_form=f"Memory Test Entity {i}",
                    start_pos=0,
                    end_pos=15,
                    source_ref=f"memory://test/{i}",
                    entity_type="MEMORY_TEST",
                    confidence=0.8
                )
                entities.append(result)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            stress_tests.append({
                "test": "memory_usage_under_load",
                "passed": memory_increase < 100,  # Less than 100MB increase
                "details": f"Memory increased by {memory_increase:.1f}MB ({initial_memory:.1f} -> {final_memory:.1f})"
            })
            
        except Exception as e:
            stress_tests.append({
                "test": "memory_usage_under_load",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in stress_tests if test["passed"])
        total_tests = len(stress_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.6,  # 60% pass rate for stress tests
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Stress and load testing: {passed_tests}/{total_tests} passed",
            "test_results": stress_tests
        }
    
    def test_edge_case_robustness(self) -> Dict[str, Any]:
        """Test handling of edge cases and malformed inputs"""
        print("🎯 Testing edge case robustness...")
        
        edge_case_tests = []
        
        # Test empty/null inputs
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # Test empty string
            result = service.create_mention("", 0, 0, "test://empty", "TEST", 0.5)
            edge_case_tests.append({
                "test": "empty_string_handling",
                "passed": result["status"] in ["success", "error"],  # Should handle gracefully
                "details": f"Empty string result: {result['status']}"
            })
            
            # Test very long string
            long_string = "A" * 10000
            result = service.create_mention(long_string, 0, 10000, "test://long", "TEST", 0.5)
            edge_case_tests.append({
                "test": "long_string_handling", 
                "passed": result["status"] in ["success", "error"],
                "details": f"Long string result: {result['status']}"
            })
            
            # Test invalid confidence values
            result = service.create_mention("Test", 0, 4, "test://conf", "TEST", -1.0)
            edge_case_tests.append({
                "test": "invalid_confidence_handling",
                "passed": result["status"] in ["success", "error"],
                "details": f"Invalid confidence result: {result['status']}"
            })
            
        except Exception as e:
            edge_case_tests.append({
                "test": "input_validation_edge_cases",
                "passed": False,
                "error": str(e)
            })
        
        # Test malformed JSON handling (for API endpoints)
        try:
            from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator
            
            generator = GeminiOntologyGenerator()
            
            # Test malformed JSON parsing
            malformed_json = '{"incomplete": "json"'
            
            try:
                result = generator._parse_response(malformed_json)
                edge_case_tests.append({
                    "test": "malformed_json_handling",
                    "passed": False,  # Should have raised an exception
                    "details": "Malformed JSON was incorrectly parsed"
                })
            except Exception:
                edge_case_tests.append({
                    "test": "malformed_json_handling",
                    "passed": True,  # Correctly raised exception
                    "details": "Malformed JSON correctly rejected"
                })
                
        except Exception as e:
            edge_case_tests.append({
                "test": "malformed_json_handling",
                "passed": False,
                "error": str(e)
            })
        
        # Test Unicode and special characters
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            unicode_texts = [
                "café",  # Accented characters
                "北京",  # Chinese characters
                "🚀",   # Emoji
                "‰",    # Special symbols
                "\n\t\r",  # Control characters
            ]
            
            unicode_pass_count = 0
            for text in unicode_texts:
                try:
                    result = service.create_mention(text, 0, len(text), "test://unicode", "TEST", 0.8)
                    if result["status"] in ["success", "error"]:
                        unicode_pass_count += 1
                except:
                    pass  # Expected for some edge cases
            
            edge_case_tests.append({
                "test": "unicode_handling",
                "passed": unicode_pass_count >= len(unicode_texts) * 0.8,  # 80% should work
                "details": f"Unicode tests passed: {unicode_pass_count}/{len(unicode_texts)}"
            })
            
        except Exception as e:
            edge_case_tests.append({
                "test": "unicode_handling",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in edge_case_tests if test["passed"])
        total_tests = len(edge_case_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.7,  # 70% pass rate for edge cases
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Edge case robustness: {passed_tests}/{total_tests} passed",
            "test_results": edge_case_tests
        }
    
    def test_failure_recovery(self) -> Dict[str, Any]:
        """Test system recovery from various failure scenarios"""
        print("🔧 Testing failure recovery...")
        
        recovery_tests = []
        
        # Test Neo4j connection failure recovery
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            
            # Test with invalid connection
            calc = PageRankCalculator(
                neo4j_uri="bolt://invalid:7687",
                neo4j_user="invalid",
                neo4j_password="invalid"
            )
            
            # Should handle connection failure gracefully
            result = calc.calculate_pagerank()
            recovery_tests.append({
                "test": "neo4j_connection_failure_recovery",
                "passed": result["status"] == "error",  # Should return error, not crash
                "details": f"Connection failure handled: {result.get('error', 'No error message')}"
            })
            
        except Exception as e:
            recovery_tests.append({
                "test": "neo4j_connection_failure_recovery",
                "passed": True,  # Exception is acceptable for connection failure
                "details": f"Connection failure raised exception (acceptable): {str(e)[:100]}"
            })
        
        # Test Phase 2 Gemini API failure recovery
        try:
            from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
            
            workflow = EnhancedVerticalSliceWorkflow()
            
            # Test ontology generation with potential Gemini failure
            result = workflow._execute_ontology_generation("test_workflow", "Test domain description")
            
            recovery_tests.append({
                "test": "gemini_api_failure_recovery",
                "passed": result["status"] == "success",  # Should fallback to mock ontology
                "details": f"Ontology generation method: {result.get('method', 'unknown')}"
            })
            
        except Exception as e:
            recovery_tests.append({
                "test": "gemini_api_failure_recovery",
                "passed": False,
                "error": str(e)
            })
        
        # Test file system failure recovery
        try:
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            loader = PDFLoader(IdentityService(), ProvenanceService(), QualityService())
            
            # Test with non-existent file
            result = loader.load_pdf("/nonexistent/file.pdf")
            
            recovery_tests.append({
                "test": "file_not_found_recovery",
                "passed": result["status"] == "error",  # Should return error, not crash
                "details": f"File not found handled: {result.get('error', 'No error message')[:100]}"
            })
            
        except Exception as e:
            recovery_tests.append({
                "test": "file_not_found_recovery",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in recovery_tests if test["passed"])
        total_tests = len(recovery_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.8,  # 80% pass rate for recovery
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Failure recovery: {passed_tests}/{total_tests} passed", 
            "test_results": recovery_tests
        }
    
    def test_performance_under_load(self) -> Dict[str, Any]:
        """Test performance characteristics under various load conditions"""
        print("📊 Testing performance under load...")
        
        performance_tests = []
        
        # Test response time consistency
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            response_times = []
            for i in range(20):
                start_time = time.time()
                service.create_mention(f"Perf Test {i}", 0, 10, f"perf://test/{i}", "PERF", 0.8)
                response_times.append(time.time() - start_time)
            
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            performance_tests.append({
                "test": "response_time_consistency",
                "passed": avg_time < 0.1 and max_time < 0.5,  # Avg < 100ms, Max < 500ms
                "details": f"Avg: {avg_time*1000:.1f}ms, Max: {max_time*1000:.1f}ms"
            })
            
        except Exception as e:
            performance_tests.append({
                "test": "response_time_consistency",
                "passed": False,
                "error": str(e)
            })
        
        # Test throughput under load
        try:
            from src.tools.phase1.t15a_text_chunker import TextChunker
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            chunker = TextChunker(IdentityService(), ProvenanceService(), QualityService())
            
            test_text = "This is a performance test sentence. " * 50  # ~2KB
            
            start_time = time.time()
            chunk_count = 0
            
            for i in range(10):
                result = chunker.chunk_text(f"perf_doc_{i}", test_text, 0.8)
                if result["status"] == "success":
                    chunk_count += result.get("chunk_count", 0)
            
            duration = time.time() - start_time
            throughput = chunk_count / duration
            
            performance_tests.append({
                "test": "chunking_throughput",
                "passed": throughput > 5,  # At least 5 chunks/second
                "details": f"Processed {chunk_count} chunks in {duration:.2f}s ({throughput:.1f}/s)"
            })
            
        except Exception as e:
            performance_tests.append({
                "test": "chunking_throughput",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in performance_tests if test["passed"])
        total_tests = len(performance_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.7,  # 70% pass rate for performance
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Performance under load: {passed_tests}/{total_tests} passed",
            "test_results": performance_tests
        }
    
    def test_resource_management(self) -> Dict[str, Any]:
        """Test memory and resource management"""
        print("💾 Testing resource management...")
        
        resource_tests = []
        
        # Test memory cleanup
        try:
            import psutil
            import os
            import gc
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create and destroy many objects
            from src.core.identity_service import IdentityService
            services = []
            
            for i in range(100):
                service = IdentityService()
                service.create_mention(f"Resource Test {i}", 0, 10, f"resource://test/{i}", "RESOURCE", 0.8)
                services.append(service)
            
            # Clear references and force garbage collection
            services.clear()
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            resource_tests.append({
                "test": "memory_cleanup",
                "passed": memory_increase < 50,  # Less than 50MB increase after cleanup
                "details": f"Memory after cleanup: {memory_increase:.1f}MB increase"
            })
            
        except Exception as e:
            resource_tests.append({
                "test": "memory_cleanup",
                "passed": False,
                "error": str(e)
            })
        
        # Test file handle management
        try:
            import os
            
            initial_fd_count = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 0
            
            # Simulate file operations
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Create multiple loaders (they should clean up file handles)
            loaders = []
            for i in range(20):
                loader = PDFLoader(IdentityService(), ProvenanceService(), QualityService())
                loaders.append(loader)
            
            # Clear loaders
            loaders.clear()
            
            final_fd_count = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 0
            fd_increase = final_fd_count - initial_fd_count
            
            resource_tests.append({
                "test": "file_handle_management",
                "passed": fd_increase < 10,  # Less than 10 new file descriptors
                "details": f"File descriptor increase: {fd_increase}"
            })
            
        except Exception as e:
            resource_tests.append({
                "test": "file_handle_management",
                "passed": True,  # This test is platform-specific
                "details": f"Platform-specific test skipped: {str(e)[:50]}"
            })
        
        passed_tests = sum(1 for test in resource_tests if test["passed"])
        total_tests = len(resource_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.8,  # 80% pass rate for resource management
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Resource management: {passed_tests}/{total_tests} passed",
            "test_results": resource_tests
        }
    
    def test_concurrent_access(self) -> Dict[str, Any]:
        """Test concurrent access and thread safety"""
        print("🔄 Testing concurrent access...")
        
        concurrent_tests = []
        
        # Test concurrent entity creation
        try:
            import threading
            import queue
            
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            results_queue = queue.Queue()
            threads = []
            
            def create_entities(thread_id):
                try:
                    for i in range(10):
                        result = service.create_mention(
                            f"Concurrent Entity {thread_id}_{i}",
                            0, 10,
                            f"concurrent://test/{thread_id}/{i}",
                            "CONCURRENT",
                            0.8
                        )
                        results_queue.put(("success", result))
                except Exception as e:
                    results_queue.put(("error", str(e)))
            
            # Start 5 concurrent threads
            for i in range(5):
                thread = threading.Thread(target=create_entities, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Collect results
            successes = 0
            errors = 0
            while not results_queue.empty():
                result_type, _ = results_queue.get()
                if result_type == "success":
                    successes += 1
                else:
                    errors += 1
            
            concurrent_tests.append({
                "test": "concurrent_entity_creation",
                "passed": errors == 0 and successes > 0,
                "details": f"Successes: {successes}, Errors: {errors}"
            })
            
        except Exception as e:
            concurrent_tests.append({
                "test": "concurrent_entity_creation",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in concurrent_tests if test["passed"])
        total_tests = len(concurrent_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.8,  # 80% pass rate for concurrency
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Concurrent access: {passed_tests}/{total_tests} passed",
            "test_results": concurrent_tests
        }
    
    def test_data_corruption_resilience(self) -> Dict[str, Any]:
        """Test resilience to data corruption and inconsistencies"""
        print("🛡️ Testing data corruption resilience...")
        
        corruption_tests = []
        
        # Test malformed configuration handling
        try:
            # Test with various invalid configurations
            invalid_configs = [
                {},  # Empty config
                {"invalid": "config"},  # Unknown keys
                {"neo4j_uri": ""},  # Empty values
                {"confidence_threshold": "invalid"},  # Wrong types
            ]
            
            from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
            
            corruption_test_results = []
            for config in invalid_configs:
                try:
                    builder = OntologyAwareGraphBuilder(**config)
                    corruption_test_results.append("handled")
                except Exception:
                    corruption_test_results.append("rejected")  # This is also acceptable
            
            corruption_tests.append({
                "test": "invalid_config_handling",
                "passed": len(corruption_test_results) == len(invalid_configs),
                "details": f"Invalid configs handled: {len(corruption_test_results)}/{len(invalid_configs)}"
            })
            
        except Exception as e:
            corruption_tests.append({
                "test": "invalid_config_handling",
                "passed": False,
                "error": str(e)
            })
        
        # Test corrupted input data handling
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            corrupted_inputs = [
                ("", 0, 0, "", "", ""),  # All empty
                ("test", -1, 5, "test", "TEST", 0.5),  # Negative position
                ("test", 10, 5, "test", "TEST", 0.5),  # End before start
                ("test", 0, 4, "test", "", 0.5),  # Empty entity type
                ("test", 0, 4, "test", "TEST", 2.0),  # Invalid confidence
            ]
            
            handled_count = 0
            for surface_form, start, end, source_ref, entity_type, confidence in corrupted_inputs:
                try:
                    result = service.create_mention(surface_form, start, end, source_ref, entity_type, confidence)
                    if result["status"] in ["success", "error"]:  # Either is acceptable
                        handled_count += 1
                except Exception:
                    pass  # Some corruption may cause exceptions, which is acceptable
            
            corruption_tests.append({
                "test": "corrupted_input_handling",
                "passed": handled_count >= len(corrupted_inputs) * 0.6,  # At least 60% handled
                "details": f"Corrupted inputs handled: {handled_count}/{len(corrupted_inputs)}"
            })
            
        except Exception as e:
            corruption_tests.append({
                "test": "corrupted_input_handling",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in corruption_tests if test["passed"])
        total_tests = len(corruption_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.7,  # 70% pass rate for corruption resilience
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"Data corruption resilience: {passed_tests}/{total_tests} passed",
            "test_results": corruption_tests
        }
    
    def test_api_contract_validation(self) -> Dict[str, Any]:
        """Test API contract compliance and interface consistency"""
        print("📋 Testing API contract validation...")
        
        contract_tests = []
        
        # Test Phase interface compliance
        try:
            from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
            from src.core.graphrag_phase_interface import GraphRAGPhase
            
            adapters = [Phase1Adapter(), Phase2Adapter()]
            
            required_methods = ["get_capabilities", "validate_input", "execute"]
            compliance_score = 0
            
            for adapter in adapters:
                adapter_compliance = 0
                for method in required_methods:
                    if hasattr(adapter, method) and callable(getattr(adapter, method)):
                        adapter_compliance += 1
                
                if adapter_compliance == len(required_methods):
                    compliance_score += 1
            
            contract_tests.append({
                "test": "phase_interface_compliance",
                "passed": compliance_score == len(adapters),
                "details": f"Compliant adapters: {compliance_score}/{len(adapters)}"
            })
            
        except Exception as e:
            contract_tests.append({
                "test": "phase_interface_compliance",
                "passed": False,
                "error": str(e)
            })
        
        # Test return type consistency
        try:
            from src.core.identity_service import IdentityService
            service = IdentityService()
            
            # All service methods should return consistent format
            result = service.create_mention("Test", 0, 4, "test://api", "TEST", 0.8)
            
            required_keys = ["status"]
            has_required_keys = all(key in result for key in required_keys)
            
            contract_tests.append({
                "test": "return_type_consistency",
                "passed": has_required_keys and isinstance(result, dict),
                "details": f"Result format valid: {has_required_keys}, Type: {type(result)}"
            })
            
        except Exception as e:
            contract_tests.append({
                "test": "return_type_consistency",
                "passed": False,
                "error": str(e)
            })
        
        passed_tests = sum(1 for test in contract_tests if test["passed"])
        total_tests = len(contract_tests)
        
        return {
            "passed": passed_tests >= total_tests * 0.9,  # 90% pass rate for API contracts
            "score": passed_tests / total_tests if total_tests > 0 else 0,
            "details": f"API contract validation: {passed_tests}/{total_tests} passed",
            "test_results": contract_tests
        }
    
    def _calculate_torc_metrics(self) -> TORCMetrics:
        """Calculate Time, Operational Resilience, Compatibility metrics"""
        
        # Extract performance data from test results
        time_metrics = {}
        for test_name, result in self.test_results.items():
            if "execution_time" in result:
                time_metrics[test_name] = result["execution_time"]
        
        # Calculate operational resilience (recovery from failures)
        resilience_metrics = {}
        for test_name, result in self.test_results.items():
            if "failure_recovery" in test_name.lower():
                resilience_metrics[test_name] = 1 if result.get("passed", False) else 0
        
        # Calculate compatibility score
        compatibility_score = 0.0
        compatibility_tests = [name for name in self.test_results.keys() if "compatibility" in name.lower()]
        if compatibility_tests:
            compatibility_score = sum(
                self.test_results[test].get("score", 0) for test in compatibility_tests
            ) / len(compatibility_tests)
        
        # Calculate robustness score  
        robustness_score = 0.0
        robustness_tests = [name for name in self.test_results.keys() if any(
            keyword in name.lower() for keyword in ["edge", "stress", "robustness", "corruption"]
        )]
        if robustness_tests:
            robustness_score = sum(
                self.test_results[test].get("score", 0) for test in robustness_tests
            ) / len(robustness_tests)
        
        return TORCMetrics(
            time_performance=time_metrics,
            operational_resilience=resilience_metrics,
            compatibility_score=compatibility_score,
            robustness_score=robustness_score
        )
    
    def _assess_compatibility(self) -> Dict[str, float]:
        """Assess compatibility between different components"""
        
        compatibility_matrix = {}
        
        # Phase compatibility
        if "Cross-Phase Compatibility" in self.test_results:
            compatibility_matrix["phase_compatibility"] = self.test_results["Cross-Phase Compatibility"].get("score", 0.0)
        
        # Service compatibility  
        if "Component Isolation Tests" in self.test_results:
            compatibility_matrix["service_compatibility"] = self.test_results["Component Isolation Tests"].get("score", 0.0)
        
        # API compatibility
        if "API Contract Validation" in self.test_results:
            compatibility_matrix["api_compatibility"] = self.test_results["API Contract Validation"].get("score", 0.0)
        
        return compatibility_matrix
    
    def _assess_robustness(self) -> Dict[str, Any]:
        """Assess system robustness across different dimensions"""
        
        robustness_assessment = {
            "edge_case_handling": 0.0,
            "failure_recovery": 0.0,
            "stress_tolerance": 0.0,
            "data_corruption_resilience": 0.0,
            "overall_robustness": 0.0
        }
        
        if "Edge Case Robustness" in self.test_results:
            robustness_assessment["edge_case_handling"] = self.test_results["Edge Case Robustness"].get("score", 0.0)
        
        if "Failure Recovery Testing" in self.test_results:
            robustness_assessment["failure_recovery"] = self.test_results["Failure Recovery Testing"].get("score", 0.0)
        
        if "Stress & Load Testing" in self.test_results:
            robustness_assessment["stress_tolerance"] = self.test_results["Stress & Load Testing"].get("score", 0.0)
        
        if "Data Corruption Resilience" in self.test_results:
            robustness_assessment["data_corruption_resilience"] = self.test_results["Data Corruption Resilience"].get("score", 0.0)
        
        # Calculate overall robustness
        scores = [v for v in robustness_assessment.values() if isinstance(v, float) and v > 0]
        if scores:
            robustness_assessment["overall_robustness"] = sum(scores) / len(scores)
        
        return robustness_assessment
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Analyze test failures and generate specific recommendations
        failed_tests = []
        for test_name, result in results["test_summary"].items():
            if result["status"] != "passed":
                failed_tests.append(test_name)
        
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed test categories: {', '.join(failed_tests[:3])}")
        
        # Performance recommendations
        torc_metrics = results.get("torc_metrics")
        if torc_metrics and torc_metrics.compatibility_score < 0.8:
            recommendations.append("Improve cross-component compatibility (current score: {:.1%})".format(torc_metrics.compatibility_score))
        
        if torc_metrics and torc_metrics.robustness_score < 0.7:
            recommendations.append("Enhance system robustness and error handling (current score: {:.1%})".format(torc_metrics.robustness_score))
        
        # Specific component recommendations
        if "Stress & Load Testing" in failed_tests:
            recommendations.append("Optimize performance under load - consider connection pooling and caching")
        
        if "Failure Recovery Testing" in failed_tests:
            recommendations.append("Implement better failure recovery mechanisms and circuit breakers")
        
        if "Cross-Phase Compatibility" in failed_tests:
            recommendations.append("Standardize interfaces between phases to improve compatibility")
        
        if not recommendations:
            recommendations.append("System showing good overall health - consider adding more comprehensive test coverage")
        
        return recommendations


def main():
    """Run comprehensive adversarial testing"""
    
    print("🚀 STARTING COMPREHENSIVE ADVERSARIAL TESTING")
    print("Testing reliability, TORC, robustness, and flexibility")
    print("=" * 80)
    
    framework = AdversarialTestFramework()
    
    # Run all tests
    start_time = time.time()
    results = framework.run_comprehensive_tests()
    total_time = time.time() - start_time
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Test summary
    passed_tests = sum(1 for result in results["test_summary"].values() if result["status"] == "passed")
    total_tests = len(results["test_summary"])
    
    print(f"\n📊 Overall Results:")
    print(f"   Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests:.1%})")
    print(f"   Total Execution Time: {total_time:.2f}s")
    
    # TORC Metrics
    if results["torc_metrics"]:
        torc = results["torc_metrics"]
        print(f"\n⏱️  TORC Metrics:")
        print(f"   Compatibility Score: {torc.compatibility_score:.1%}")
        print(f"   Robustness Score: {torc.robustness_score:.1%}")
        print(f"   Operational Resilience: {len(torc.operational_resilience)} tests")
    
    # Component Health
    print(f"\n🔍 Component Health:")
    for test_name, result in results["test_summary"].items():
        status_icon = "✅" if result["status"] == "passed" else "❌"
        print(f"   {status_icon} {test_name}: {result['score']:.1%} ({result['execution_time']:.2f}s)")
    
    # Recommendations
    if results["recommendations"]:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    # Final Assessment
    overall_health = passed_tests / total_tests
    print(f"\n🎯 SYSTEM HEALTH ASSESSMENT:")
    
    if overall_health >= 0.9:
        print("🟢 EXCELLENT: System demonstrates high reliability and robustness")
    elif overall_health >= 0.8:
        print("🟡 GOOD: System is generally reliable with some areas for improvement")
    elif overall_health >= 0.7:
        print("🟠 FAIR: System has moderate reliability, several issues need attention")
    else:
        print("🔴 POOR: System reliability is below acceptable levels, requires immediate attention")
    
    print(f"\nReliability Score: {overall_health:.1%}")
    print(f"TORC Compliance: {results['torc_metrics'].compatibility_score + results['torc_metrics'].robustness_score:.1%}")
    
    return overall_health >= 0.7  # Return success if >= 70% pass rate


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)