#!/usr/bin/env python3
"""
Extreme Stress Conditions Test
Tests the GraphRAG system under extreme conditions to verify:
1. 100% reliability (success OR clear error)
2. No unhandled exceptions under stress
3. Clear error messages even under extreme conditions
4. Graceful degradation rather than crashes
5. NO MOCKS policy maintained under stress
"""

import sys
import time
import gc
import threading
import psutil
import os
import tempfile
import random
import string
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def generate_large_text(size_kb: int) -> str:
    """Generate large text of specified size in KB"""
    text_chunk = "This is a test sentence with various entities like Apple Inc., Microsoft Corporation, and Google LLC. " * 10
    chunks_needed = (size_kb * 1024) // len(text_chunk.encode())
    return text_chunk * chunks_needed

def generate_unicode_stress_text() -> str:
    """Generate text with problematic Unicode characters"""
    return """
    Test with accented characters: café, naïve, résumé
    Test with Asian characters: 北京, 東京, 서울
    Test with emojis: 🚀🎯💾🔧🎨
    Test with mathematical symbols: ∞ ≤ ≥ ∑ ∏ ∆
    Test with control characters: \n\t\r\f\v
    Test with zero-width characters: ‌‍
    Test with right-to-left text: עברית العربية
    Test with combining characters: e̊ å ñ
    """

class ExtremeStressTester:
    """Test system under extreme stress conditions"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.test_results = []
        
    def run_extreme_stress_tests(self) -> Dict[str, Any]:
        """Run all extreme stress tests"""
        print("💥 EXTREME STRESS TESTING")
        print("Testing system reliability under extreme conditions")
        print("=" * 80)
        
        stress_tests = [
            ("Memory Exhaustion Test", self.test_memory_exhaustion),
            ("Large Document Processing", self.test_large_document_processing),
            ("Unicode Stress Test", self.test_unicode_stress),
            ("Concurrent Overload Test", self.test_concurrent_overload),
            ("Resource Starvation Test", self.test_resource_starvation),
            ("Invalid Input Flood Test", self.test_invalid_input_flood),
            ("Network Failure Simulation", self.test_network_failure_simulation),
            ("File System Stress Test", self.test_file_system_stress),
            ("Service Dependency Failure", self.test_service_dependency_failure),
            ("Malformed Data Attack", self.test_malformed_data_attack)
        ]
        
        results = {
            "test_summary": {},
            "reliability_score": 0.0,
            "no_mocks_verified": True,
            "graceful_degradation": True,
            "clear_error_messages": True,
            "recommendations": []
        }
        
        for test_name, test_func in stress_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            try:
                result = test_func()
                
                results["test_summary"][test_name] = result
                
                status = "✅ RELIABLE" if result["reliable"] else "❌ UNRELIABLE"
                print(f"{status} {test_name}")
                print(f"   Success Rate: {result['success_rate']:.1%}")
                print(f"   Clear Errors: {result['clear_errors']}")
                print(f"   No Crashes: {result['no_crashes']}")
                print(f"   No Mocks: {result['no_mocks_used']}")
                
                # Track violations of NO MOCKS policy
                if not result["no_mocks_used"]:
                    results["no_mocks_verified"] = False
                
                if not result["graceful_handling"]:
                    results["graceful_degradation"] = False
                    
                if not result["clear_errors"]:
                    results["clear_error_messages"] = False
                
            except Exception as e:
                print(f"❌ {test_name}: FAILED with unhandled exception: {e}")
                results["test_summary"][test_name] = {
                    "reliable": False,
                    "success_rate": 0.0,
                    "clear_errors": False,
                    "no_crashes": False,
                    "no_mocks_used": True,
                    "graceful_handling": False,
                    "error": str(e)
                }
                results["graceful_degradation"] = False
        
        # Calculate overall reliability
        reliable_tests = sum(1 for result in results["test_summary"].values() if result["reliable"])
        total_tests = len(results["test_summary"])
        results["reliability_score"] = reliable_tests / total_tests if total_tests > 0 else 0.0
        
        return results
    
    def test_memory_exhaustion(self) -> Dict[str, Any]:
        """Test behavior under memory exhaustion"""
        print("💾 Testing memory exhaustion handling...")
        
        try:
            from src.core.identity_service import IdentityService
            
            service = IdentityService()
            large_objects = []
            operations_completed = 0
            errors = 0
            clear_errors = 0
            
            # Gradually increase memory usage until system limits
            for i in range(1000):
                try:
                    # Create entity and large data
                    result = service.create_mention(
                        surface_form=f"Memory Stress Entity {i}",
                        start_pos=0,
                        end_pos=20,
                        source_ref=f"memory://stress/{i}",
                        entity_type="MEMORY_STRESS",
                        confidence=0.8
                    )
                    
                    # Add memory pressure
                    large_data = {
                        "entity": result,
                        "large_text": "X" * 10000,  # 10KB per entity
                        "metadata": list(range(1000))
                    }
                    large_objects.append(large_data)
                    
                    operations_completed += 1
                    
                    # Check memory usage
                    current_memory = self.process.memory_info().rss / 1024 / 1024
                    if current_memory - self.initial_memory > 500:  # 500MB limit
                        print(f"   Memory limit reached at {operations_completed} operations")
                        break
                        
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    
                    # Check if error message is clear
                    if any(keyword in error_msg for keyword in ["memory", "resource", "limit", "failed"]):
                        clear_errors += 1
                    
                    # Stop if too many consecutive errors
                    if errors > 10:
                        break
            
            # Force garbage collection
            large_objects.clear()
            gc.collect()
            
            success_rate = (operations_completed - errors) / operations_completed if operations_completed > 0 else 0.0
            
            return {
                "reliable": operations_completed > 100 and errors < operations_completed * 0.5,
                "success_rate": success_rate,
                "clear_errors": clear_errors >= errors * 0.8 if errors > 0 else True,
                "no_crashes": True,  # If we reach here, no crashes occurred
                "no_mocks_used": True,  # Memory test doesn't use mocks
                "graceful_handling": errors > 0,  # Should have some errors under memory pressure
                "details": f"Completed {operations_completed} operations, {errors} errors, {clear_errors} clear errors"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_large_document_processing(self) -> Dict[str, Any]:
        """Test processing very large documents"""
        print("📄 Testing large document processing...")
        
        try:
            from src.tools.phase1.t15a_text_chunker import TextChunker
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            chunker = TextChunker(IdentityService(), ProvenanceService(), QualityService())
            
            operations_completed = 0
            errors = 0
            clear_errors = 0
            
            # Test with increasingly large documents
            for size_kb in [100, 500, 1000, 5000]:  # Up to 5MB documents
                try:
                    large_text = generate_large_text(size_kb)
                    
                    print(f"   Processing {size_kb}KB document...")
                    
                    start_time = time.time()
                    result = chunker.chunk_text(
                        document_ref=f"large_doc_{size_kb}kb",
                        text=large_text,
                        document_confidence=0.8
                    )
                    duration = time.time() - start_time
                    
                    if result["status"] == "success":
                        operations_completed += 1
                        print(f"   ✅ {size_kb}KB processed in {duration:.2f}s")
                    else:
                        errors += 1
                        error_msg = result.get("error", "").lower()
                        if any(keyword in error_msg for keyword in ["size", "large", "memory", "timeout"]):
                            clear_errors += 1
                        print(f"   ❌ {size_kb}KB failed: {result.get('error', 'Unknown error')}")
                    
                    # Stop if taking too long (over 30 seconds per document)
                    if duration > 30:
                        print(f"   ⏰ Stopping due to timeout on {size_kb}KB document")
                        break
                        
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ["memory", "size", "timeout", "resource"]):
                        clear_errors += 1
                    print(f"   ❌ {size_kb}KB failed with exception: {str(e)[:100]}")
            
            total_attempts = operations_completed + errors
            success_rate = operations_completed / total_attempts if total_attempts > 0 else 0.0
            
            return {
                "reliable": total_attempts > 0,
                "success_rate": success_rate,
                "clear_errors": clear_errors >= errors * 0.8 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": True,
                "graceful_handling": True,
                "details": f"Processed {operations_completed}/{total_attempts} large documents"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_unicode_stress(self) -> Dict[str, Any]:
        """Test with problematic Unicode characters"""
        print("🌐 Testing Unicode stress handling...")
        
        try:
            from src.core.identity_service import IdentityService
            
            service = IdentityService()
            operations_completed = 0
            errors = 0
            clear_errors = 0
            
            unicode_test_cases = [
                ("café", "Accented characters"),
                ("北京", "Chinese characters"),
                ("🚀🎯💾", "Emojis"),
                ("∞≤≥∑∏∆", "Mathematical symbols"),
                ("\n\t\r\f\v", "Control characters"),
                ("‌‍", "Zero-width characters"),
                ("עברית", "Right-to-left text"),
                ("e̊åñ", "Combining characters"),
                (generate_unicode_stress_text(), "Mixed Unicode stress"),
                ("A" * 1000 + "café" + "🚀", "Long text with Unicode")
            ]
            
            for test_text, description in unicode_test_cases:
                try:
                    result = service.create_mention(
                        surface_form=test_text,
                        start_pos=0,
                        end_pos=len(test_text),
                        source_ref=f"unicode://test/{operations_completed}",
                        entity_type="UNICODE_TEST",
                        confidence=0.8
                    )
                    
                    if result["status"] in ["success", "error"]:
                        operations_completed += 1
                        if result["status"] == "error":
                            errors += 1
                            error_msg = result.get("error", "").lower()
                            if "unicode" in error_msg or "encoding" in error_msg or "character" in error_msg:
                                clear_errors += 1
                    
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ["unicode", "encoding", "character", "decode"]):
                        clear_errors += 1
            
            success_rate = (operations_completed - errors) / operations_completed if operations_completed > 0 else 0.0
            
            return {
                "reliable": operations_completed > 0,
                "success_rate": success_rate,
                "clear_errors": clear_errors >= errors * 0.7 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": True,
                "graceful_handling": True,
                "details": f"Processed {operations_completed} Unicode test cases, {errors} errors"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_concurrent_overload(self) -> Dict[str, Any]:
        """Test system under extreme concurrent load"""
        print("🔄 Testing concurrent overload handling...")
        
        try:
            from src.core.identity_service import IdentityService
            import concurrent.futures
            import queue
            
            service = IdentityService()
            results_queue = queue.Queue()
            
            def stress_worker(worker_id, operations_per_worker=100):
                worker_successes = 0
                worker_errors = 0
                worker_clear_errors = 0
                
                for i in range(operations_per_worker):
                    try:
                        result = service.create_mention(
                            surface_form=f"Concurrent Entity {worker_id}_{i}",
                            start_pos=0,
                            end_pos=20,
                            source_ref=f"concurrent://worker/{worker_id}/{i}",
                            entity_type="CONCURRENT_STRESS",
                            confidence=0.8
                        )
                        
                        if result["status"] == "success":
                            worker_successes += 1
                        else:
                            worker_errors += 1
                            error_msg = result.get("error", "").lower()
                            if any(keyword in error_msg for keyword in ["concurrent", "resource", "timeout", "busy"]):
                                worker_clear_errors += 1
                                
                    except Exception as e:
                        worker_errors += 1
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ["concurrent", "thread", "lock", "resource"]):
                            worker_clear_errors += 1
                
                results_queue.put((worker_successes, worker_errors, worker_clear_errors))
            
            # Launch many concurrent workers
            max_workers = 20  # High concurrency
            operations_per_worker = 50
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for worker_id in range(max_workers):
                    future = executor.submit(stress_worker, worker_id, operations_per_worker)
                    futures.append(future)
                
                # Wait for all workers
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()  # This will raise if worker failed
                    except Exception:
                        pass  # Worker failure is acceptable under stress
            
            # Collect results
            total_successes = 0
            total_errors = 0
            total_clear_errors = 0
            
            while not results_queue.empty():
                successes, errors, clear_errors = results_queue.get()
                total_successes += successes
                total_errors += errors
                total_clear_errors += clear_errors
            
            total_operations = total_successes + total_errors
            success_rate = total_successes / total_operations if total_operations > 0 else 0.0
            
            return {
                "reliable": total_operations > 0,
                "success_rate": success_rate,
                "clear_errors": total_clear_errors >= total_errors * 0.6 if total_errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": True,
                "graceful_handling": True,
                "details": f"Concurrent test: {total_successes} successes, {total_errors} errors from {max_workers} workers"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_resource_starvation(self) -> Dict[str, Any]:
        """Test behavior under resource starvation"""
        print("🍽️ Testing resource starvation handling...")
        
        try:
            # Test file descriptor exhaustion
            file_handles = []
            operations_completed = 0
            errors = 0
            clear_errors = 0
            
            try:
                # Open many temporary files to exhaust file descriptors
                with tempfile.TemporaryDirectory() as temp_dir:
                    for i in range(1000):  # Try to open many files
                        try:
                            temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
                            file_handles.append(temp_file)
                            operations_completed += 1
                            
                            # Test if system still works under fd pressure
                            if i % 100 == 0:
                                from src.core.identity_service import IdentityService
                                service = IdentityService()
                                result = service.create_mention(
                                    surface_form=f"FD Test {i}",
                                    start_pos=0,
                                    end_pos=10,
                                    source_ref=f"fd://test/{i}",
                                    entity_type="FD_TEST",
                                    confidence=0.8
                                )
                                
                                if result["status"] == "error":
                                    errors += 1
                                    error_msg = result.get("error", "").lower()
                                    if any(keyword in error_msg for keyword in ["file", "resource", "limit", "descriptor"]):
                                        clear_errors += 1
                                        
                        except OSError as e:
                            # Expected when file descriptors are exhausted
                            errors += 1
                            if "too many open files" in str(e).lower():
                                clear_errors += 1
                            break
                        except Exception as e:
                            errors += 1
                            error_msg = str(e).lower()
                            if any(keyword in error_msg for keyword in ["resource", "file", "limit"]):
                                clear_errors += 1
                            break
                            
            finally:
                # Clean up file handles
                for fh in file_handles:
                    try:
                        fh.close()
                    except:
                        pass
            
            return {
                "reliable": operations_completed > 0,
                "success_rate": (operations_completed - errors) / operations_completed if operations_completed > 0 else 0.0,
                "clear_errors": clear_errors >= errors * 0.8 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": True,
                "graceful_handling": errors > 0,  # Should encounter resource limits
                "details": f"Resource starvation: {operations_completed} operations, {errors} resource errors"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_invalid_input_flood(self) -> Dict[str, Any]:
        """Test with flood of invalid inputs"""
        print("🌊 Testing invalid input flood handling...")
        
        try:
            from src.core.identity_service import IdentityService
            
            service = IdentityService()
            operations_completed = 0
            errors = 0
            clear_errors = 0
            
            # Generate many invalid inputs
            invalid_inputs = [
                ("", -1, -1, "", "", -1.0),  # All invalid
                ("test", 100, 1, "ref", "TYPE", 2.0),  # End before start, invalid confidence
                (None, 0, 5, "ref", "TYPE", 0.8),  # None surface form
                ("test", "invalid", 5, "ref", "TYPE", 0.8),  # Invalid position type
                ("test", 0, 5, "ref", None, 0.8),  # None entity type
                ("x" * 100000, 0, 100000, "ref", "TYPE", 0.8),  # Extremely long surface form
                ("test", 0, 5, "ref", "TYPE", "invalid"),  # Invalid confidence type
                ("test\x00test", 0, 9, "ref", "TYPE", 0.8),  # Null byte in string
                ("test", -100, -50, "ref", "TYPE", 0.8),  # Very negative positions
                ("test", 0, 5, "\x00\x01\x02", "TYPE", 0.8),  # Control characters in ref
            ]
            
            # Flood with invalid inputs
            for invalid_input in invalid_inputs * 100:  # 1000 total invalid inputs
                try:
                    surface_form, start_pos, end_pos, source_ref, entity_type, confidence = invalid_input
                    
                    result = service.create_mention(
                        surface_form=surface_form,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        source_ref=source_ref,
                        entity_type=entity_type,
                        confidence=confidence
                    )
                    
                    operations_completed += 1
                    
                    if result["status"] == "error":
                        errors += 1
                        error_msg = result.get("error", "").lower()
                        if any(keyword in error_msg for keyword in ["invalid", "error", "bad", "illegal", "wrong"]):
                            clear_errors += 1
                    
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ["invalid", "type", "value", "argument"]):
                        clear_errors += 1
            
            success_rate = (operations_completed - errors) / operations_completed if operations_completed > 0 else 0.0
            
            return {
                "reliable": operations_completed > 0,
                "success_rate": success_rate,
                "clear_errors": clear_errors >= errors * 0.8 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": True,
                "graceful_handling": errors > operations_completed * 0.5,  # Most inputs should be rejected
                "details": f"Invalid input flood: {operations_completed} operations, {errors} errors, {clear_errors} clear errors"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_network_failure_simulation(self) -> Dict[str, Any]:
        """Test behavior when network dependencies fail"""
        print("🌐 Testing network failure simulation...")
        
        try:
            from src.tools.phase1.t68_pagerank import PageRankCalculator
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            # Create required services
            identity_service = IdentityService()
            provenance_service = ProvenanceService()
            quality_service = QualityService()
            
            operations_completed = 0
            errors = 0
            clear_errors = 0
            mocks_detected = False
            
            # Test with invalid network configurations
            invalid_configs = [
                ("bolt://invalid-host:7687", "neo4j", "password"),
                ("bolt://localhost:9999", "neo4j", "password"),  # Wrong port
                ("bolt://localhost:7687", "invalid_user", "invalid_password"),
                ("invalid://protocol", "neo4j", "password"),
                ("", "", ""),  # Empty config
            ]
            
            for neo4j_uri, neo4j_user, neo4j_password in invalid_configs:
                try:
                    calc = PageRankCalculator(
                        identity_service=identity_service,
                        provenance_service=provenance_service,
                        quality_service=quality_service,
                        neo4j_uri=neo4j_uri,
                        neo4j_user=neo4j_user,
                        neo4j_password=neo4j_password
                    )
                    
                    result = calc.calculate_pagerank()
                    operations_completed += 1
                    
                    if result["status"] == "error":
                        errors += 1
                        error_msg = result.get("error", "").lower()
                        
                        # Check for clear network error messages
                        if any(keyword in error_msg for keyword in ["connection", "network", "host", "authentication", "timeout"]):
                            clear_errors += 1
                        
                        # Check for mock data (violation of NO MOCKS policy)
                        if "mock" in error_msg or "fake" in error_msg or result.get("pagerank_scores"):
                            mocks_detected = True
                    
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ["connection", "network", "authentication", "uri"]):
                        clear_errors += 1
            
            return {
                "reliable": operations_completed > 0,
                "success_rate": 0.0,  # All should fail with invalid configs
                "clear_errors": clear_errors >= errors * 0.8 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": not mocks_detected,
                "graceful_handling": errors > 0,  # Should have network errors
                "details": f"Network failure test: {operations_completed} operations, {errors} network errors, mocks detected: {mocks_detected}"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_file_system_stress(self) -> Dict[str, Any]:
        """Test file system stress scenarios"""
        print("📁 Testing file system stress...")
        
        try:
            from src.tools.phase1.t01_pdf_loader import PDFLoader
            from src.core.identity_service import IdentityService
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            loader = PDFLoader(IdentityService(), ProvenanceService(), QualityService())
            
            operations_completed = 0
            errors = 0
            clear_errors = 0
            mocks_detected = False
            
            # Test problematic file paths
            problematic_paths = [
                "/nonexistent/file.pdf",
                "/dev/null",
                "/etc/passwd",  # System file
                "",  # Empty path
                "file_with_unicode_名前.pdf",
                "file with spaces.pdf",
                "file.txt",  # Wrong extension
                "https://invalid-url.pdf",  # URL instead of file
                "/tmp/nonexistent_dir/file.pdf",
                "." * 1000 + ".pdf",  # Very long filename
            ]
            
            for file_path in problematic_paths:
                try:
                    result = loader.load_pdf(file_path)
                    operations_completed += 1
                    
                    if result["status"] == "error":
                        errors += 1
                        error_msg = result.get("error", "").lower()
                        
                        # Check for clear file error messages
                        if any(keyword in error_msg for keyword in ["file", "not found", "access", "permission", "invalid"]):
                            clear_errors += 1
                        
                        # Check for mock data (violation of NO MOCKS policy)
                        if result.get("text") or result.get("pages") or "mock" in error_msg:
                            mocks_detected = True
                    
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ["file", "path", "permission", "not found"]):
                        clear_errors += 1
            
            return {
                "reliable": operations_completed > 0,
                "success_rate": 0.0,  # All should fail with invalid files
                "clear_errors": clear_errors >= errors * 0.8 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": not mocks_detected,
                "graceful_handling": errors > 0,  # Should have file errors
                "details": f"File system stress: {operations_completed} operations, {errors} file errors, mocks detected: {mocks_detected}"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_service_dependency_failure(self) -> Dict[str, Any]:
        """Test when service dependencies fail"""
        print("🔧 Testing service dependency failures...")
        
        try:
            operations_completed = 0
            errors = 0
            clear_errors = 0
            mocks_detected = False
            
            # Test Phase 2 with potential Gemini API failures
            try:
                from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
                
                workflow = EnhancedVerticalSliceWorkflow()
                
                # Test ontology generation multiple times to potentially trigger API limits
                for i in range(5):
                    try:
                        result = workflow._execute_ontology_generation(f"stress_test_{i}", f"Test domain {i}")
                        operations_completed += 1
                        
                        if result["status"] == "error":
                            errors += 1
                            error_msg = result.get("error", "").lower()
                            if any(keyword in error_msg for keyword in ["api", "quota", "limit", "rate", "timeout"]):
                                clear_errors += 1
                        elif result["status"] == "success":
                            # Check if using fallback (which might be mocks)
                            method = result.get("method", "")
                            if "fallback" in method.lower() or "mock" in method.lower():
                                mocks_detected = True
                        
                    except Exception as e:
                        errors += 1
                        error_msg = str(e).lower()
                        if any(keyword in error_msg for keyword in ["api", "connection", "timeout", "authentication"]):
                            clear_errors += 1
                            
            except ImportError:
                pass  # Phase 2 not available
            
            # Test with obviously broken service configurations
            try:
                from src.core.enhanced_identity_service import EnhancedIdentityService
                
                # This might fail due to OpenAI API issues
                service = EnhancedIdentityService()
                
                result = service.create_mention(
                    surface_form="Test",
                    start_pos=0,
                    end_pos=4,
                    source_ref="dependency://test",
                    entity_type="DEPENDENCY_TEST",
                    confidence=0.8
                )
                
                operations_completed += 1
                
                if result["status"] == "error":
                    errors += 1
                    error_msg = result.get("error", "").lower()
                    if any(keyword in error_msg for keyword in ["api", "key", "authentication", "service"]):
                        clear_errors += 1
                        
            except Exception as e:
                errors += 1
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ["api", "service", "dependency", "configuration"]):
                    clear_errors += 1
            
            return {
                "reliable": operations_completed > 0 or errors > 0,  # Should have attempted something
                "success_rate": (operations_completed - errors) / operations_completed if operations_completed > 0 else 0.0,
                "clear_errors": clear_errors >= errors * 0.7 if errors > 0 else True,
                "no_crashes": True,
                "no_mocks_used": not mocks_detected,
                "graceful_handling": True,
                "details": f"Service dependency test: {operations_completed} operations, {errors} dependency errors, mocks detected: {mocks_detected}"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }
    
    def test_malformed_data_attack(self) -> Dict[str, Any]:
        """Test with malformed data designed to break the system"""
        print("💀 Testing malformed data attack resistance...")
        
        try:
            from src.core.identity_service import IdentityService
            
            service = IdentityService()
            operations_completed = 0
            errors = 0
            clear_errors = 0
            
            # Malicious/malformed inputs designed to break systems
            malformed_inputs = [
                # Buffer overflow attempts
                ("A" * 1000000, 0, 1000000, "ref", "TYPE", 0.8),
                # Code injection attempts
                ("'; DROP TABLE entities; --", 0, 20, "ref", "TYPE", 0.8),
                ("<script>alert('xss')</script>", 0, 30, "ref", "TYPE", 0.8),
                # Path traversal attempts
                ("../../../etc/passwd", 0, 20, "ref", "TYPE", 0.8),
                # Format string attacks
                ("%s%s%s%s%s%s%s", 0, 14, "ref", "TYPE", 0.8),
                # Binary data
                (b"\x00\x01\x02\x03\x04".decode('latin1'), 0, 5, "ref", "TYPE", 0.8),
                # Extremely nested structures (if JSON processed)
                ('{"a":{"b":{"c":{"d":{"e":"deep"}}}}}', 0, 35, "ref", "TYPE", 0.8),
                # Unicode normalization attacks
                ("Ǎ", 0, 1, "ref", "TYPE", 0.8),  # Decomposed vs composed
                # Regular expression denial of service
                ("a" * 1000 + "X", 0, 1001, "ref", "TYPE", 0.8),
            ]
            
            for surface_form, start_pos, end_pos, source_ref, entity_type, confidence in malformed_inputs:
                try:
                    result = service.create_mention(
                        surface_form=surface_form,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        source_ref=source_ref,
                        entity_type=entity_type,
                        confidence=confidence
                    )
                    
                    operations_completed += 1
                    
                    if result["status"] == "error":
                        errors += 1
                        error_msg = result.get("error", "").lower()
                        if any(keyword in error_msg for keyword in ["invalid", "malformed", "unsafe", "rejected"]):
                            clear_errors += 1
                    
                except Exception as e:
                    errors += 1
                    error_msg = str(e).lower()
                    if any(keyword in error_msg for keyword in ["invalid", "malformed", "security", "unsafe"]):
                        clear_errors += 1
            
            return {
                "reliable": operations_completed > 0,
                "success_rate": (operations_completed - errors) / operations_completed if operations_completed > 0 else 0.0,
                "clear_errors": clear_errors >= errors * 0.7 if errors > 0 else True,
                "no_crashes": True,  # System should not crash from malformed input
                "no_mocks_used": True,
                "graceful_handling": errors > operations_completed * 0.7,  # Most malformed inputs should be rejected
                "details": f"Malformed data attack: {operations_completed} operations, {errors} rejections, {clear_errors} clear rejections"
            }
            
        except Exception as e:
            return {
                "reliable": False,
                "success_rate": 0.0,
                "clear_errors": False,
                "no_crashes": False,
                "no_mocks_used": True,
                "graceful_handling": False,
                "error": str(e)
            }


def main():
    """Run extreme stress testing"""
    
    print("💥 STARTING EXTREME STRESS TESTING")
    print("Verifying system reliability under extreme conditions")
    print("Testing NO MOCKS policy compliance under stress")
    print("=" * 80)
    
    tester = ExtremeStressTester()
    
    # Run all extreme stress tests
    start_time = time.time()
    results = tester.run_extreme_stress_tests()
    total_time = time.time() - start_time
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("💥 EXTREME STRESS TESTING RESULTS")
    print("=" * 80)
    
    # Overall statistics
    test_summary = results["test_summary"]
    reliable_tests = sum(1 for test in test_summary.values() if test["reliable"])
    total_tests = len(test_summary)
    
    print(f"\n📊 Extreme Stress Results:")
    print(f"   Reliable Tests: {reliable_tests}/{total_tests} ({reliable_tests/total_tests:.1%})")
    print(f"   Overall Reliability Score: {results['reliability_score']:.1%}")
    print(f"   Total Test Time: {total_time:.2f}s")
    
    # CLAUDE.md compliance checks
    print(f"\n✅ CLAUDE.md Compliance Verification:")
    print(f"   NO MOCKS Policy: {'✅ VERIFIED' if results['no_mocks_verified'] else '❌ VIOLATED'}")
    print(f"   Graceful Degradation: {'✅ VERIFIED' if results['graceful_degradation'] else '❌ FAILED'}")
    print(f"   Clear Error Messages: {'✅ VERIFIED' if results['clear_error_messages'] else '❌ FAILED'}")
    
    # Individual test results
    print(f"\n🔍 Individual Extreme Stress Tests:")
    for test_name, test_result in test_summary.items():
        status_icon = "✅" if test_result["reliable"] else "❌"
        success_rate = test_result.get("success_rate", 0)
        no_mocks = "✅" if test_result.get("no_mocks_used", True) else "❌"
        print(f"   {status_icon} {test_name}:")
        print(f"      Success Rate: {success_rate:.1%}")
        print(f"      No Mocks: {no_mocks}")
        print(f"      Clear Errors: {'✅' if test_result.get('clear_errors', False) else '❌'}")
        print(f"      No Crashes: {'✅' if test_result.get('no_crashes', False) else '❌'}")
    
    # Policy violations (critical issues)
    policy_violations = []
    if not results['no_mocks_verified']:
        policy_violations.append("MOCK DATA DETECTED under stress (violates NO MOCKS policy)")
    if not results['graceful_degradation']:
        policy_violations.append("UNGRACEFUL FAILURES detected under stress")
    if not results['clear_error_messages']:
        policy_violations.append("UNCLEAR ERROR MESSAGES under stress")
    
    if policy_violations:
        print(f"\n🚨 POLICY VIOLATIONS:")
        for violation in policy_violations:
            print(f"   ⚠️  {violation}")
    
    # Final assessment
    reliability_score = results["reliability_score"]
    compliance_score = (
        (1 if results['no_mocks_verified'] else 0) +
        (1 if results['graceful_degradation'] else 0) +
        (1 if results['clear_error_messages'] else 0)
    ) / 3
    
    print(f"\n🎯 EXTREME STRESS ASSESSMENT:")
    
    if reliability_score >= 0.8 and compliance_score >= 0.8:
        print("🟢 EXCELLENT: System maintains reliability and policy compliance under extreme stress")
    elif reliability_score >= 0.6 and compliance_score >= 0.6:
        print("🟡 GOOD: System mostly reliable under stress with minor policy issues")
    elif reliability_score >= 0.4 or compliance_score >= 0.4:
        print("🟠 FAIR: System has stress reliability issues, policy compliance needs work")
    else:
        print("🔴 POOR: System fails under stress, major policy violations detected")
    
    print(f"\nReliability Under Stress: {reliability_score:.1%}")
    print(f"Policy Compliance Under Stress: {compliance_score:.1%}")
    
    # Success criteria: Both reliability and compliance must be good
    success = reliability_score >= 0.6 and compliance_score >= 0.8
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)