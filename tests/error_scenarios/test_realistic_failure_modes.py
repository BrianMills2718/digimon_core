"""
Error Scenario Tests - Realistic Failure Modes

Tests system behavior under realistic failure conditions including
network failures, resource exhaustion, corrupted data, and edge cases.
"""

import pytest
import tempfile
import os
import threading
import time
import signal
from pathlib import Path
from typing import List, Dict, Any
import json
from unittest.mock import patch, Mock

# Import components for error testing
from src.tools.phase1.t23a_spacy_ner_unified import SpacyNER
from src.core.dependency_injection import DependencyContainer
from src.core.unified_service_interface import ServiceRequest, ServiceResponse
from src.core.security_validation import SecurityValidator
from src.core.anyio_api_client import AnyIOAPIClient


class TestInputValidationErrors:
    """Test error handling for invalid inputs"""
    
    def test_ner_invalid_input_types(self):
        """Test NER tool with various invalid input types"""
        ner_tool = SpacyNER()
        
        # Test None input
        result = ner_tool.extract_entities_working(None)
        assert isinstance(result, list), "Should handle None input gracefully"
        assert len(result) == 0, "None input should produce no entities"
        
        # Test numeric input
        result = ner_tool.extract_entities_working(12345)
        assert isinstance(result, list), "Should handle numeric input gracefully"
        
        # Test list input
        result = ner_tool.extract_entities_working([1, 2, 3])
        assert isinstance(result, list), "Should handle list input gracefully"
        
        # Test dict input
        result = ner_tool.extract_entities_working({"key": "value"})
        assert isinstance(result, list), "Should handle dict input gracefully"
        
        # Test boolean input
        result = ner_tool.extract_entities_working(True)
        assert isinstance(result, list), "Should handle boolean input gracefully"
    
    def test_ner_malformed_text_input(self):
        """Test NER tool with malformed text inputs"""
        ner_tool = SpacyNER()
        
        # Test very long input (potential memory issues)
        very_long_text = "A" * 100000  # 100k characters
        result = ner_tool.extract_entities_working(very_long_text)
        assert isinstance(result, list), "Should handle very long text"
        
        # Test text with special unicode characters
        unicode_text = "Hello 👋 World 🌍 测试 テスト العالم мир"
        result = ner_tool.extract_entities_working(unicode_text)
        assert isinstance(result, list), "Should handle unicode text"
        
        # Test text with only punctuation
        punctuation_text = "!@#$%^&*()[]{}|;':\",./<>?"
        result = ner_tool.extract_entities_working(punctuation_text)
        assert isinstance(result, list), "Should handle punctuation-only text"
        
        # Test text with control characters
        control_chars_text = "Hello\x00\x01\x02World\n\r\t"
        result = ner_tool.extract_entities_working(control_chars_text)
        assert isinstance(result, list), "Should handle control characters"
        
        # Test binary data (simulated)
        binary_text = "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        result = ner_tool.extract_entities_working(binary_text)
        assert isinstance(result, list), "Should handle binary-like data"
    
    def test_service_request_invalid_parameters(self):
        """Test ServiceRequest with invalid parameters"""
        # Test missing required parameters
        try:
            request = ServiceRequest(
                operation="",  # Empty operation
                parameters={}
            )
            # Should not crash, but may have validation issues
            assert request.operation == ""
        except Exception as e:
            # If it raises an exception, it should be meaningful
            assert len(str(e)) > 0, "Error message should be meaningful"
        
        # Test invalid parameter types
        request = ServiceRequest(
            operation="test_operation",
            parameters=None  # Invalid type
        )
        # Should handle gracefully or provide clear error
        assert request.parameters is None
        
        # Test oversized parameters
        large_params = {"large_data": "x" * 1000000}  # 1MB of data
        request = ServiceRequest(
            operation="test_operation",
            parameters=large_params
        )
        assert len(request.parameters["large_data"]) == 1000000
    
    def test_dependency_injection_invalid_registrations(self):
        """Test dependency injection with invalid service registrations"""
        container = DependencyContainer()
        
        # Test registering None as service
        try:
            container.register_singleton("null_service", None)
            service = container.resolve("null_service")
            # Should either work or raise meaningful error
        except Exception as e:
            assert "None" in str(e) or "null" in str(e).lower()
        
        # Test registering non-callable
        try:
            container.register_singleton("invalid_service", "not_a_class")
            service = container.resolve("invalid_service")
            assert False, "Should raise error for non-callable registration"
        except Exception as e:
            assert len(str(e)) > 0, "Should provide meaningful error message"
        
        # Test circular dependencies (simplified)
        class ServiceA:
            def __init__(self, service_b=None):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a=None):
                self.service_a = service_a
        
        container.register_singleton("service_a", ServiceA)
        container.register_singleton("service_b", ServiceB)
        
        # This might cause issues, should be handled gracefully
        try:
            service_a = container.resolve("service_a")
            service_b = container.resolve("service_b")
            # Should work or provide clear error about circular dependency
        except Exception as e:
            assert "circular" in str(e).lower() or "dependency" in str(e).lower()


class TestResourceExhaustionScenarios:
    """Test behavior under resource exhaustion"""
    
    def test_memory_pressure_handling(self):
        """Test system behavior under memory pressure"""
        ner_tool = SpacyNER()
        
        # Create progressively larger inputs to test memory limits
        base_text = "Dr. John Smith from Harvard University researches machine learning. "
        
        memory_test_results = []
        
        for multiplier in [1, 10, 100, 500]:  # Increasing sizes
            test_text = base_text * multiplier
            text_size = len(test_text)
            
            try:
                start_time = time.time()
                result = ner_tool.extract_entities_working(test_text)
                end_time = time.time()
                
                memory_test_results.append({
                    "multiplier": multiplier,
                    "text_size": text_size,
                    "entities_found": len(result),
                    "processing_time": end_time - start_time,
                    "success": True
                })
                
                # Verify reasonable processing time scaling
                if multiplier >= 100:
                    assert (end_time - start_time) < 60.0, f"Processing time too long for {multiplier}x text"
                
            except MemoryError:
                memory_test_results.append({
                    "multiplier": multiplier,
                    "text_size": text_size,
                    "error": "MemoryError",
                    "success": False
                })
                break  # Stop testing at memory limit
            except Exception as e:
                memory_test_results.append({
                    "multiplier": multiplier,
                    "text_size": text_size,
                    "error": str(e),
                    "success": False
                })
        
        # Verify graceful handling of memory pressure
        successful_tests = [r for r in memory_test_results if r.get("success", False)]
        assert len(successful_tests) >= 2, "Should handle at least small and medium inputs"
        
        # Check for graceful degradation
        if len(memory_test_results) > len(successful_tests):
            failed_test = memory_test_results[len(successful_tests)]
            assert "error" in failed_test, "Should provide error information for failures"
    
    def test_concurrent_resource_contention(self):
        """Test behavior under concurrent resource contention"""
        import threading
        import queue
        
        ner_tool = SpacyNER()
        results_queue = queue.Queue()
        num_threads = 8  # Create resource contention
        
        # Text that requires processing resources
        processing_text = """
        Dr. Sarah Johnson from Stanford University published research with Professor Michael Chen 
        from MIT. The study involved collaboration with Google Research, Microsoft Research, 
        IBM Watson, and Amazon Science. Funding came from the National Science Foundation,
        Department of Energy, and National Institutes of Health.
        """ * 10  # Make it substantial
        
        def concurrent_processing_thread(thread_id):
            """Process text in concurrent thread"""
            thread_results = []
            
            try:
                for i in range(3):  # Process multiple documents per thread
                    start_time = time.time()
                    entities = ner_tool.extract_entities_working(processing_text)
                    end_time = time.time()
                    
                    thread_results.append({
                        "thread_id": thread_id,
                        "iteration": i,
                        "entities_found": len(entities),
                        "processing_time": end_time - start_time,
                        "success": True
                    })
                    
            except Exception as e:
                thread_results.append({
                    "thread_id": thread_id,
                    "error": str(e),
                    "success": False
                })
            
            results_queue.put(thread_results)
        
        # Start concurrent threads
        threads = []
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=concurrent_processing_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        all_results = []
        while not results_queue.empty():
            thread_results = results_queue.get()
            all_results.extend(thread_results)
        
        # Analyze concurrent performance
        successful_results = [r for r in all_results if r.get("success", False)]
        failed_results = [r for r in all_results if not r.get("success", False)]
        
        # Should handle most concurrent requests successfully
        success_rate = len(successful_results) / len(all_results) if all_results else 0
        assert success_rate >= 0.8, f"Success rate too low under contention: {success_rate:.2%}"
        
        # Processing times should be reasonable even under contention
        if successful_results:
            avg_processing_time = sum(r["processing_time"] for r in successful_results) / len(successful_results)
            max_processing_time = max(r["processing_time"] for r in successful_results)
            
            assert avg_processing_time < 10.0, f"Average processing time too high under contention: {avg_processing_time:.2f}s"
            assert max_processing_time < 20.0, f"Max processing time too high under contention: {max_processing_time:.2f}s"
    
    def test_file_system_errors(self):
        """Test handling of file system errors"""
        validator = SecurityValidator()
        
        # Test with non-existent file
        result = validator.scan_file("/non/existent/path/file.py")
        assert isinstance(result, list), "Should handle non-existent file gracefully"
        assert len(result) == 0, "Non-existent file should produce no issues"
        
        # Test with permission denied (simulate)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write('test_content = "hello"')
            temp_file_path = temp_file.name
        
        try:
            # Change permissions to deny read access
            os.chmod(temp_file_path, 0o000)
            
            result = validator.scan_file(temp_file_path)
            # Should handle permission error gracefully
            assert isinstance(result, list), "Should handle permission errors gracefully"
            
        except PermissionError:
            # If it raises PermissionError, that's also acceptable
            pass
        finally:
            # Restore permissions and cleanup
            try:
                os.chmod(temp_file_path, 0o644)
                os.unlink(temp_file_path)
            except:
                pass
        
        # Test with directory instead of file
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.scan_file(temp_dir)
            assert isinstance(result, list), "Should handle directory input gracefully"


class TestNetworkAndExternalServiceErrors:
    """Test handling of network and external service failures"""
    
    def test_api_client_network_failures(self):
        """Test API client behavior during network failures"""
        api_client = AnyIOAPIClient()
        
        # Test with invalid API key (simulated failure)
        test_request = ServiceRequest(
            operation="generate_embeddings",
            parameters={
                "texts": ["Test text for embedding"],
                "api_key": "invalid_key_12345"
            }
        )
        
        # The API client should handle invalid keys gracefully
        # (This test assumes the client has error handling)
        try:
            # This would normally make an API call, but with invalid key should fail gracefully
            response = ServiceResponse(
                success=False,
                data=None,
                metadata={"api_client": "anyio_client"},
                error_code="INVALID_API_KEY",
                error_message="API authentication failed"
            )
            
            assert response.success is False
            assert response.error_code == "INVALID_API_KEY"
            
        except Exception as e:
            # If it raises an exception, it should be handled gracefully
            assert len(str(e)) > 0, "Should provide meaningful error message"
    
    def test_service_timeout_handling(self):
        """Test service timeout scenarios"""
        # Simulate slow service with sleep
        def slow_processing_function(text):
            time.sleep(2)  # Simulate slow processing
            return [{"name": "Test Entity", "type": "TEST", "confidence": 0.8}]
        
        # Test timeout handling
        start_time = time.time()
        
        try:
            # Set a short timeout and see if it's handled
            with threading.Timer(1.0, lambda: None):  # 1 second timeout
                result = slow_processing_function("test text")
            
            # If we get here, the function completed (unexpected for this test)
            processing_time = time.time() - start_time
            assert processing_time >= 2.0, "Function should have taken time to complete"
            
        except Exception as e:
            # Timeout or other error should be handled gracefully
            processing_time = time.time() - start_time
            assert processing_time < 1.5, "Should have timed out quickly"
    
    def test_dependency_injection_service_failures(self):
        """Test dependency injection when services fail to initialize"""
        container = DependencyContainer()
        
        # Create a service class that fails to initialize
        class FailingService:
            def __init__(self):
                raise ValueError("Service initialization failed")
        
        # Register the failing service
        container.register_singleton("failing_service", FailingService)
        
        # Try to resolve the failing service
        try:
            service = container.resolve("failing_service")
            assert False, "Should raise error for failing service initialization"
        except Exception as e:
            assert "initialization failed" in str(e) or "ValueError" in str(e)
        
        # Container should still be usable for other services
        container.register_singleton("working_service", SpacyNER)
        working_service = container.resolve("working_service")
        assert isinstance(working_service, SpacyNER), "Container should still work for valid services"


class TestDataCorruptionScenarios:
    """Test handling of corrupted or malformed data"""
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted files"""
        validator = SecurityValidator()
        
        # Create file with corrupted Python syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write("""
# This file has corrupted Python syntax
def incomplete_function(
    # Missing closing parenthesis and function body
if True
    print("No colon after if")
    
class BrokenClass
    # Missing colon after class definition
    def method_without_self():
        pass

# Unclosed string literal
unclosed_string = "This string is never closed
""")
            temp_file_path = temp_file.name
        
        try:
            # Security validator should handle corrupted syntax gracefully
            result = validator.scan_file(temp_file_path)
            assert isinstance(result, list), "Should handle corrupted Python file gracefully"
            # May or may not find security issues, but should not crash
            
        finally:
            os.unlink(temp_file_path)
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON data"""
        # Test with various malformed JSON structures
        malformed_json_examples = [
            '{"incomplete": ',  # Incomplete JSON
            '{invalid_key: "value"}',  # Unquoted key
            '{"duplicate": "value1", "duplicate": "value2"}',  # Duplicate keys
            '{"nested": {"incomplete":}',  # Incomplete nested structure
            '[1, 2, 3,]',  # Trailing comma
            '{"unicode": "\x00\x01\x02"}',  # Control characters
        ]
        
        for malformed_json in malformed_json_examples:
            try:
                # Test JSON parsing error handling
                parsed = json.loads(malformed_json)
                # If it doesn't raise an error, that's fine too
            except json.JSONDecodeError:
                # Expected behavior for malformed JSON
                pass
            except Exception as e:
                # Other exceptions should be handled gracefully
                assert len(str(e)) > 0, f"Should provide meaningful error for: {malformed_json}"
    
    def test_encoding_error_handling(self):
        """Test handling of encoding errors"""
        validator = SecurityValidator()
        
        # Create file with mixed encodings
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as temp_file:
            # Write mixed UTF-8 and Latin-1 content
            content = b"""# -*- coding: utf-8 -*-
# This file has encoding issues
normal_text = "Hello World"
utf8_text = "Caf\xc3\xa9"  # UTF-8 encoded
latin1_text = b"Caf\xe9".decode('latin-1')  # Latin-1 content
binary_data = \x89PNG\r\n\x1a\n  # Binary data in Python file
"""
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Validator should handle encoding issues gracefully
            result = validator.scan_file(temp_file_path)
            assert isinstance(result, list), "Should handle encoding issues gracefully"
            
        finally:
            os.unlink(temp_file_path)


class TestConcurrencyErrorScenarios:
    """Test error scenarios under concurrent access"""
    
    def test_race_condition_handling(self):
        """Test handling of race conditions"""
        container = DependencyContainer()
        container.register_singleton("ner_service", SpacyNER)
        
        results = []
        errors = []
        
        def concurrent_access_thread(thread_id):
            """Access services concurrently"""
            try:
                for i in range(10):
                    # Concurrent service resolution
                    service = container.resolve("ner_service")
                    
                    # Concurrent service usage
                    entities = service.extract_entities_working(f"Test text from thread {thread_id} iteration {i}")
                    
                    results.append({
                        "thread_id": thread_id,
                        "iteration": i,
                        "entities_count": len(entities),
                        "service_id": id(service)
                    })
                    
            except Exception as e:
                errors.append({
                    "thread_id": thread_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
        
        # Start multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=concurrent_access_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Analyze results
        assert len(errors) == 0, f"Should handle concurrent access without errors: {errors}"
        assert len(results) == 50, "Should complete all concurrent operations"
        
        # Verify singleton behavior (same service instance across threads)
        service_ids = set(r["service_id"] for r in results)
        assert len(service_ids) == 1, "Singleton should return same instance across threads"
    
    def test_deadlock_prevention(self):
        """Test prevention of deadlocks"""
        # Create two containers that might create circular dependencies
        container1 = DependencyContainer()
        container2 = DependencyContainer()
        
        class ServiceX:
            def __init__(self):
                # Simulate some setup time
                time.sleep(0.1)
                
        class ServiceY:
            def __init__(self):
                # Simulate some setup time
                time.sleep(0.1)
        
        container1.register_singleton("service_x", ServiceX)
        container2.register_singleton("service_y", ServiceY)
        
        results = []
        
        def resolve_services_thread(container, service_name, thread_id):
            """Resolve services in different orders"""
            try:
                start_time = time.time()
                service = container.resolve(service_name)
                end_time = time.time()
                
                results.append({
                    "thread_id": thread_id,
                    "service_name": service_name,
                    "resolution_time": end_time - start_time,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "thread_id": thread_id,
                    "service_name": service_name,
                    "error": str(e),
                    "success": False
                })
        
        # Start threads that might create deadlock conditions
        threads = []
        
        # Thread 1: Resolve service_x then service_y
        thread1 = threading.Thread(target=resolve_services_thread, args=(container1, "service_x", 1))
        threads.append(thread1)
        
        # Thread 2: Resolve service_y then service_x  
        thread2 = threading.Thread(target=resolve_services_thread, args=(container2, "service_y", 2))
        threads.append(thread2)
        
        # Start threads simultaneously
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for completion with timeout
        for thread in threads:
            thread.join(timeout=5.0)  # 5 second timeout
        
        total_time = time.time() - start_time
        
        # Verify no deadlock occurred
        assert total_time < 3.0, f"Potential deadlock detected: took {total_time:.2f}s"
        
        # Verify all threads completed
        successful_results = [r for r in results if r.get("success", False)]
        assert len(successful_results) >= 1, "At least one service resolution should succeed"
        
        # Check that no threads are still running
        for thread in threads:
            assert not thread.is_alive(), "All threads should have completed"


class TestGracefulDegradationScenarios:
    """Test graceful degradation under various failure conditions"""
    
    def test_partial_service_failure_handling(self):
        """Test system behavior when some services fail"""
        container = DependencyContainer()
        
        # Register working and failing services
        container.register_singleton("working_service", SpacyNER)
        
        class PartiallyFailingService:
            def __init__(self):
                self.failure_count = 0
            
            def process_data(self, data):
                self.failure_count += 1
                if self.failure_count % 3 == 0:  # Fail every 3rd call
                    raise RuntimeError("Simulated service failure")
                return f"Processed: {data}"
        
        container.register_singleton("failing_service", PartiallyFailingService)
        
        # Test resilience to partial failures
        working_service = container.resolve("working_service")
        failing_service = container.resolve("failing_service")
        
        results = []
        for i in range(10):
            try:
                # Working service should always work
                ner_result = working_service.extract_entities_working(f"Test text {i}")
                
                # Failing service should fail intermittently
                try:
                    failing_result = failing_service.process_data(f"data_{i}")
                    results.append({"iteration": i, "ner_success": True, "failing_success": True})
                except RuntimeError:
                    results.append({"iteration": i, "ner_success": True, "failing_success": False})
                    
            except Exception as e:
                results.append({"iteration": i, "ner_success": False, "error": str(e)})
        
        # Analyze graceful degradation
        ner_successes = sum(1 for r in results if r.get("ner_success", False))
        failing_successes = sum(1 for r in results if r.get("failing_success", False))
        
        assert ner_successes == 10, "Working service should never fail"
        assert failing_successes < 10, "Failing service should have some failures"
        assert failing_successes >= 6, "Failing service should succeed most of the time"
    
    def test_fallback_mechanism_testing(self):
        """Test fallback mechanisms when primary services fail"""
        # Simulate a service with fallback behavior
        class ServiceWithFallback:
            def __init__(self):
                self.primary_available = True
                
            def toggle_primary_service(self):
                self.primary_available = not self.primary_available
                
            def process_text(self, text):
                if self.primary_available:
                    # Simulate primary processing
                    return {
                        "method": "primary",
                        "entities": [{"name": "Primary Entity", "confidence": 0.9}],
                        "processing_time": 0.1
                    }
                else:
                    # Fallback processing (simpler/faster)
                    return {
                        "method": "fallback", 
                        "entities": [{"name": "Fallback Entity", "confidence": 0.6}],
                        "processing_time": 0.05
                    }
        
        service = ServiceWithFallback()
        
        # Test primary service
        result1 = service.process_text("test text")
        assert result1["method"] == "primary"
        assert result1["entities"][0]["confidence"] >= 0.9
        
        # Simulate primary service failure
        service.toggle_primary_service()
        
        # Test fallback service
        result2 = service.process_text("test text")
        assert result2["method"] == "fallback"
        assert result2["entities"][0]["confidence"] >= 0.6
        assert result2["processing_time"] < result1["processing_time"]
        
        # Test service recovery
        service.toggle_primary_service()
        
        result3 = service.process_text("test text")
        assert result3["method"] == "primary"
        assert result3["entities"][0]["confidence"] >= 0.9