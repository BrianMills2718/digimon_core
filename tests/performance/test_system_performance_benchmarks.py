"""
Performance Tests - System Performance Benchmarks

Tests system performance with realistic workloads and establishes
performance baselines for production deployment.
"""

import pytest
import time
import threading
import multiprocessing
import psutil
import os
from pathlib import Path
from typing import List, Dict, Any
import json
import statistics

# Import components for performance testing
from src.tools.phase1.t23a_spacy_ner_unified import SpacyNER
from src.tools.phase1.t27_relationship_extractor_unified import RelationshipExtractor
from src.core.dependency_injection import DependencyContainer
from src.core.unified_service_interface import ServiceRequest, ServiceResponse
from src.core.security_validation import SecurityValidator
from src.core.anyio_api_client import AnyIOAPIClient


@pytest.fixture
def performance_test_data():
    """Generate realistic performance test data"""
    # Large academic paper content for performance testing
    base_content = """
Dr. Sarah Johnson from Stanford University published groundbreaking research on 
machine learning algorithms in Nature journal. The study, conducted with 
Professor Michael Chen from MIT, demonstrates novel applications in healthcare 
diagnostics. The research was funded by the National Science Foundation 
grant NSF-2023-ML-001 and involved collaboration with Google Research.

The paper introduces the Johnson-Chen Algorithm, which improves accuracy 
by 23% over existing methods. Clinical trials at Massachusetts General Hospital 
showed promising results for early cancer detection. The algorithm processes 
medical imaging data using deep neural networks trained on over 100,000 
patient records from Mayo Clinic and Johns Hopkins Hospital.

Key findings include:
1. 95% accuracy in early-stage cancer detection
2. 40% reduction in false positives compared to existing methods
3. Processing time reduced from 4 hours to 15 minutes
4. Successful validation across 5 major medical centers

The research team included Dr. Elena Rodriguez from UCSF, Dr. James Wilson 
from Harvard Medical School, and Dr. Priya Patel from Cleveland Clinic.
Additional collaborators were Professor Liu Wei from Tsinghua University,
Dr. Mohammed Hassan from King Abdul Aziz University, and Dr. Anna Kowalski
from the University of Warsaw.

The study analyzed data from 50,000 patients across multiple demographics
including participants from Johns Hopkins University, Massachusetts Institute
of Technology, California Institute of Technology, University of California
San Francisco, Harvard University, Stanford University School of Medicine,
Mayo Clinic Rochester, Cleveland Clinic Foundation, and Memorial Sloan
Kettering Cancer Center.

Funding sources included the National Institutes of Health grant R01-CA123456,
Department of Defense grant W81XWH-20-1-0123, and private funding from
the Bill and Melinda Gates Foundation, Wellcome Trust, and Howard Hughes
Medical Institute. Industry partnerships included IBM Watson Health,
Google DeepMind, Microsoft Research, NVIDIA Corporation, and Intel Labs.

The computational infrastructure utilized Amazon Web Services EC2 instances,
Google Cloud Platform compute engines, Microsoft Azure virtual machines,
and on-premise clusters at Oak Ridge National Laboratory and Argonne
National Laboratory. Data storage was provided by MongoDB Atlas,
PostgreSQL databases, and Hadoop distributed file systems.
"""
    
    return {
        "small_document": base_content,
        "medium_document": base_content * 3,  # ~3x larger
        "large_document": base_content * 10,  # ~10x larger
        "xlarge_document": base_content * 25,  # ~25x larger for stress testing
        "document_batch": [base_content * i for i in range(1, 6)]  # Varying sizes
    }


class TestCoreComponentPerformance:
    """Test performance of core components"""
    
    @pytest.mark.performance
    def test_ner_processing_performance(self, performance_test_data):
        """Test NER processing performance with various document sizes"""
        ner_tool = SpacyNER()
        
        performance_results = {}
        
        for size_name, content in performance_test_data.items():
            if isinstance(content, str):  # Skip batch data
                # Measure processing time
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                entities = ner_tool.extract_entities_working(content)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                processing_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                performance_results[size_name] = {
                    "processing_time": processing_time,
                    "memory_used": memory_used,
                    "content_length": len(content),
                    "entities_found": len(entities),
                    "entities_per_second": len(entities) / processing_time if processing_time > 0 else 0,
                    "chars_per_second": len(content) / processing_time if processing_time > 0 else 0
                }
        
        # Performance assertions
        small_perf = performance_results["small_document"]
        medium_perf = performance_results["medium_document"]
        large_perf = performance_results["large_document"]
        
        # Processing time should scale reasonably
        assert small_perf["processing_time"] < 2.0, f"Small doc processing too slow: {small_perf['processing_time']:.2f}s"
        assert medium_perf["processing_time"] < 5.0, f"Medium doc processing too slow: {medium_perf['processing_time']:.2f}s"
        assert large_perf["processing_time"] < 15.0, f"Large doc processing too slow: {large_perf['processing_time']:.2f}s"
        
        # Entity extraction should be consistent
        assert small_perf["entities_found"] >= 10, "Should find substantial entities in small doc"
        assert medium_perf["entities_found"] >= 25, "Should find substantial entities in medium doc"
        assert large_perf["entities_found"] >= 80, "Should find substantial entities in large doc"
        
        # Performance should be reasonable
        assert small_perf["entities_per_second"] >= 10, "Should process >=10 entities/sec for small doc"
        assert small_perf["chars_per_second"] >= 2000, "Should process >=2000 chars/sec for small doc"
        
        # Memory usage should be reasonable (less than 100MB increase per document)
        assert small_perf["memory_used"] < 100 * 1024 * 1024, "Memory usage too high for small doc"
    
    @pytest.mark.performance
    def test_dependency_injection_performance_scale(self):
        """Test dependency injection performance at scale"""
        container = DependencyContainer()
        
        # Register multiple services
        service_classes = {
            f"ner_service_{i}": SpacyNER for i in range(10)
        }
        
        for name, service_class in service_classes.items():
            container.register_singleton(name, service_class)
        
        # Test resolution performance
        resolution_times = []
        
        for _ in range(100):  # 100 resolution cycles
            start_time = time.time()
            
            # Resolve all services in one cycle
            resolved_services = []
            for service_name in service_classes.keys():
                service = container.resolve(service_name)
                resolved_services.append(service)
            
            end_time = time.time()
            resolution_times.append(end_time - start_time)
        
        # Performance assertions
        avg_resolution_time = statistics.mean(resolution_times)
        max_resolution_time = max(resolution_times)
        
        assert avg_resolution_time < 0.01, f"Average resolution too slow: {avg_resolution_time:.4f}s"
        assert max_resolution_time < 0.05, f"Max resolution too slow: {max_resolution_time:.4f}s"
        
        # Verify singleton behavior (same instances should be fast)
        first_batch = [container.resolve(name) for name in service_classes.keys()]
        second_batch = [container.resolve(name) for name in service_classes.keys()]
        
        for first, second in zip(first_batch, second_batch):
            assert first is second, "Singletons should return same instance"
    
    @pytest.mark.performance
    def test_security_validation_performance(self, performance_test_data):
        """Test security validation performance"""
        validator = SecurityValidator()
        
        # Create test files with different sizes
        test_files = []
        for size_name, content in performance_test_data.items():
            if isinstance(content, str):
                test_file = Path(f"/tmp/perf_test_{size_name}.py")
                test_file.write_text(f'content = """{content}"""')
                test_files.append((size_name, test_file))
        
        performance_results = {}
        
        try:
            for size_name, test_file in test_files:
                start_time = time.time()
                issues = validator.scan_file(str(test_file))
                end_time = time.time()
                
                performance_results[size_name] = {
                    "scan_time": end_time - start_time,
                    "file_size": test_file.stat().st_size,
                    "issues_found": len(issues),
                    "bytes_per_second": test_file.stat().st_size / (end_time - start_time) if (end_time - start_time) > 0 else 0
                }
        
        finally:
            # Cleanup test files
            for _, test_file in test_files:
                test_file.unlink(missing_ok=True)
        
        # Performance assertions
        for size_name, results in performance_results.items():
            assert results["scan_time"] < 1.0, f"Security scan too slow for {size_name}: {results['scan_time']:.2f}s"
            assert results["bytes_per_second"] >= 100000, f"Scan throughput too low for {size_name}: {results['bytes_per_second']:.0f} bytes/s"


class TestConcurrentPerformance:
    """Test performance under concurrent load"""
    
    @pytest.mark.performance
    def test_concurrent_ner_processing(self, performance_test_data):
        """Test NER processing performance under concurrent load"""
        import threading
        import queue
        
        # Setup
        ner_tool = SpacyNER()
        results_queue = queue.Queue()
        num_threads = 4
        documents_per_thread = 3
        
        def process_documents_thread(thread_id):
            """Process documents in a single thread"""
            thread_results = []
            
            for i in range(documents_per_thread):
                start_time = time.time()
                
                # Use medium document for testing
                content = performance_test_data["medium_document"]
                entities = ner_tool.extract_entities_working(content)
                
                end_time = time.time()
                
                thread_results.append({
                    "thread_id": thread_id,
                    "document_index": i,
                    "processing_time": end_time - start_time,
                    "entities_found": len(entities),
                    "content_length": len(content)
                })
            
            results_queue.put(thread_results)
        
        # Execute concurrent processing
        threads = []
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=process_documents_thread, args=(thread_id,))
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
        
        # Performance analysis
        total_documents = num_threads * documents_per_thread
        total_entities = sum(r["entities_found"] for r in all_results)
        total_content_length = sum(r["content_length"] for r in all_results)
        
        avg_processing_time = statistics.mean(r["processing_time"] for r in all_results)
        max_processing_time = max(r["processing_time"] for r in all_results)
        
        # Performance assertions
        assert len(all_results) == total_documents, f"Should process all {total_documents} documents"
        assert total_time < 20.0, f"Concurrent processing too slow: {total_time:.2f}s"
        assert avg_processing_time < 8.0, f"Average processing time too high: {avg_processing_time:.2f}s"
        assert max_processing_time < 15.0, f"Max processing time too high: {max_processing_time:.2f}s"
        
        # Throughput assertions
        documents_per_second = total_documents / total_time
        entities_per_second = total_entities / total_time
        
        assert documents_per_second >= 0.8, f"Document throughput too low: {documents_per_second:.2f} docs/s"
        assert entities_per_second >= 15, f"Entity throughput too low: {entities_per_second:.2f} entities/s"
        
        # Verify concurrent processing benefit (should be faster than sequential)
        sequential_estimate = avg_processing_time * total_documents
        concurrency_benefit = sequential_estimate / total_time
        
        assert concurrency_benefit >= 1.5, f"Concurrency benefit too low: {concurrency_benefit:.2f}x"
    
    @pytest.mark.performance
    def test_service_container_concurrent_access(self):
        """Test service container performance under concurrent access"""
        import threading
        import queue
        
        container = DependencyContainer()
        
        # Register services
        services = {
            "ner_service": SpacyNER,
            "security_validator": SecurityValidator
        }
        
        for name, service_class in services.items():
            container.register_singleton(name, service_class)
        
        results_queue = queue.Queue()
        num_threads = 8
        resolutions_per_thread = 50
        
        def concurrent_resolution_thread(thread_id):
            """Perform service resolutions in thread"""
            thread_results = []
            
            for i in range(resolutions_per_thread):
                start_time = time.time()
                
                # Resolve both services
                ner_service = container.resolve("ner_service")
                security_validator = container.resolve("security_validator")
                
                end_time = time.time()
                
                # Verify services are correct type
                assert isinstance(ner_service, SpacyNER)
                assert isinstance(security_validator, SecurityValidator)
                
                thread_results.append({
                    "thread_id": thread_id,
                    "resolution_index": i,
                    "resolution_time": end_time - start_time
                })
            
            results_queue.put(thread_results)
        
        # Execute concurrent access
        threads = []
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=concurrent_resolution_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        all_results = []
        while not results_queue.empty():
            thread_results = results_queue.get()
            all_results.extend(thread_results)
        
        # Performance analysis
        total_resolutions = num_threads * resolutions_per_thread * 2  # 2 services per resolution
        avg_resolution_time = statistics.mean(r["resolution_time"] for r in all_results)
        max_resolution_time = max(r["resolution_time"] for r in all_results)
        
        # Performance assertions
        assert len(all_results) == num_threads * resolutions_per_thread
        assert total_time < 5.0, f"Concurrent access too slow: {total_time:.2f}s"
        assert avg_resolution_time < 0.01, f"Average resolution too slow: {avg_resolution_time:.4f}s"
        assert max_resolution_time < 0.1, f"Max resolution too slow: {max_resolution_time:.4f}s"
        
        # Throughput assertions
        resolutions_per_second = total_resolutions / total_time
        assert resolutions_per_second >= 100, f"Resolution throughput too low: {resolutions_per_second:.0f} resolutions/s"


class TestMemoryPerformance:
    """Test memory usage and performance characteristics"""
    
    @pytest.mark.performance
    def test_memory_usage_scaling(self, performance_test_data):
        """Test memory usage scaling with document size"""
        ner_tool = SpacyNER()
        
        memory_measurements = {}
        
        for size_name, content in performance_test_data.items():
            if isinstance(content, str):
                # Measure memory before processing
                process = psutil.Process()
                memory_before = process.memory_info().rss
                
                # Process document
                entities = ner_tool.extract_entities_working(content)
                
                # Measure memory after processing
                memory_after = process.memory_info().rss
                memory_used = memory_after - memory_before
                
                memory_measurements[size_name] = {
                    "content_length": len(content),
                    "entities_found": len(entities),
                    "memory_used": memory_used,
                    "memory_per_char": memory_used / len(content) if len(content) > 0 else 0,
                    "memory_per_entity": memory_used / len(entities) if len(entities) > 0 else 0
                }
        
        # Memory usage assertions
        small_memory = memory_measurements["small_document"]
        large_memory = memory_measurements["large_document"]
        
        # Memory usage should be reasonable
        assert small_memory["memory_used"] < 50 * 1024 * 1024, "Small doc memory usage too high"  # <50MB
        assert large_memory["memory_used"] < 200 * 1024 * 1024, "Large doc memory usage too high"  # <200MB
        
        # Memory scaling should be reasonable (not exponential)
        size_ratio = large_memory["content_length"] / small_memory["content_length"]
        memory_ratio = large_memory["memory_used"] / max(small_memory["memory_used"], 1)
        
        # Memory usage should scale roughly linearly (within 3x of size ratio)
        assert memory_ratio <= size_ratio * 3, f"Memory scaling too high: {memory_ratio:.2f}x vs {size_ratio:.2f}x size"
    
    @pytest.mark.performance
    def test_memory_leak_detection(self, performance_test_data):
        """Test for memory leaks during repeated processing"""
        ner_tool = SpacyNER()
        content = performance_test_data["medium_document"]
        
        memory_measurements = []
        num_iterations = 10
        
        for i in range(num_iterations):
            # Measure memory before processing
            memory_before = psutil.Process().memory_info().rss
            
            # Process document
            entities = ner_tool.extract_entities_working(content)
            
            # Measure memory after processing
            memory_after = psutil.Process().memory_info().rss
            
            memory_measurements.append({
                "iteration": i,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_used": memory_after - memory_before,
                "entities_found": len(entities)
            })
            
            # Verify consistent entity extraction
            assert len(entities) >= 25, f"Iteration {i} should find consistent entities"
        
        # Memory leak analysis
        memory_trend = [m["memory_after"] for m in memory_measurements]
        
        # Check for significant memory growth over iterations
        first_half_avg = statistics.mean(memory_trend[:num_iterations//2])
        second_half_avg = statistics.mean(memory_trend[num_iterations//2:])
        
        memory_growth = (second_half_avg - first_half_avg) / first_half_avg
        
        # Memory growth should be minimal (<20% over iterations)
        assert memory_growth < 0.2, f"Potential memory leak detected: {memory_growth:.2%} growth"
        
        # Memory usage should be consistent across iterations
        memory_used_values = [m["memory_used"] for m in memory_measurements]
        memory_std = statistics.stdev(memory_used_values) if len(memory_used_values) > 1 else 0
        memory_mean = statistics.mean(memory_used_values)
        
        coefficient_of_variation = memory_std / memory_mean if memory_mean > 0 else 0
        assert coefficient_of_variation < 0.5, f"Memory usage too inconsistent: {coefficient_of_variation:.2f} CV"


class TestRealWorldPerformanceBenchmarks:
    """Test performance with real-world scenarios"""
    
    @pytest.mark.performance
    def test_batch_document_processing_performance(self, performance_test_data):
        """Test batch document processing performance"""
        ner_tool = SpacyNER()
        
        # Process batch of documents
        document_batch = performance_test_data["document_batch"]
        
        start_time = time.time()
        
        batch_results = []
        for i, content in enumerate(document_batch):
            doc_start_time = time.time()
            entities = ner_tool.extract_entities_working(content)
            doc_end_time = time.time()
            
            batch_results.append({
                "document_index": i,
                "content_length": len(content),
                "entities_found": len(entities),
                "processing_time": doc_end_time - doc_start_time
            })
        
        total_time = time.time() - start_time
        
        # Performance analysis
        total_documents = len(document_batch)
        total_entities = sum(r["entities_found"] for r in batch_results)
        total_content_length = sum(r["content_length"] for r in batch_results)
        
        avg_processing_time = statistics.mean(r["processing_time"] for r in batch_results)
        
        # Performance assertions
        assert total_time < 30.0, f"Batch processing too slow: {total_time:.2f}s"
        assert avg_processing_time < 8.0, f"Average document processing too slow: {avg_processing_time:.2f}s"
        
        # Throughput assertions
        documents_per_second = total_documents / total_time
        entities_per_second = total_entities / total_time
        chars_per_second = total_content_length / total_time
        
        assert documents_per_second >= 0.3, f"Document throughput too low: {documents_per_second:.2f} docs/s"
        assert entities_per_second >= 5, f"Entity throughput too low: {entities_per_second:.2f} entities/s"
        assert chars_per_second >= 1000, f"Character throughput too low: {chars_per_second:.0f} chars/s"
        
        # Verify batch processing quality
        for result in batch_results:
            assert result["entities_found"] >= 10, f"Document {result['document_index']} should find >=10 entities"
    
    @pytest.mark.performance  
    def test_end_to_end_pipeline_performance(self, performance_test_data):
        """Test end-to-end pipeline performance"""
        # Initialize components
        container = DependencyContainer()
        container.register_singleton("ner_service", SpacyNER)
        container.register_singleton("security_validator", SecurityValidator)
        
        ner_service = container.resolve("ner_service")
        security_validator = container.resolve("security_validator")
        
        content = performance_test_data["large_document"]
        
        # Measure end-to-end pipeline
        start_time = time.time()
        
        # Step 1: Entity extraction
        entities = ner_service.extract_entities_working(content)
        
        # Step 2: Entity validation and filtering
        validated_entities = [
            e for e in entities 
            if e.get("confidence", 0) >= 0.7 and len(e.get("name", "")) >= 3
        ]
        
        # Step 3: Relationship extraction (simplified)
        relationships = []
        person_entities = [e for e in validated_entities if e.get("type") == "PERSON"]
        org_entities = [e for e in validated_entities if e.get("type") == "ORG"]
        
        for person in person_entities[:10]:  # Limit for performance
            for org in org_entities[:10]:
                relationships.append({
                    "source": person["name"],
                    "target": org["name"],
                    "type": "AFFILIATED_WITH",
                    "confidence": min(person.get("confidence", 0.8), org.get("confidence", 0.8))
                })
        
        # Step 4: Result compilation
        pipeline_result = {
            "entities": validated_entities,
            "relationships": relationships,
            "statistics": {
                "total_entities": len(entities),
                "validated_entities": len(validated_entities),
                "relationships": len(relationships),
                "content_length": len(content)
            }
        }
        
        end_time = time.time()
        total_pipeline_time = end_time - start_time
        
        # Performance assertions
        assert total_pipeline_time < 20.0, f"End-to-end pipeline too slow: {total_pipeline_time:.2f}s"
        assert len(entities) >= 80, f"Should find substantial entities: {len(entities)}"
        assert len(validated_entities) >= 50, f"Should have substantial validated entities: {len(validated_entities)}"
        assert len(relationships) >= 20, f"Should create substantial relationships: {len(relationships)}"
        
        # Calculate pipeline throughput
        entities_per_second = len(entities) / total_pipeline_time
        chars_per_second = len(content) / total_pipeline_time
        
        assert entities_per_second >= 8, f"Pipeline entity throughput too low: {entities_per_second:.1f} entities/s"
        assert chars_per_second >= 2000, f"Pipeline char throughput too low: {chars_per_second:.0f} chars/s"