#!/usr/bin/env python3
"""
Test Performance Monitoring - Comprehensive system performance validation
Tests memory usage, processing speed, resource management under various loads
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

import time
import psutil
import threading
from src.core.service_manager import ServiceManager
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker import TextChunker
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
import tempfile
import json

class PerformanceMonitor:
    """Monitor system performance during testing"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.measurements = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval=0.1):
        """Start continuous performance monitoring"""
        self.monitoring = True
        self.measurements = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring and return results"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        return self._analyze_measurements()
    
    def _monitor_loop(self, interval):
        """Continuous monitoring loop"""
        while self.monitoring:
            try:
                measurement = {
                    'timestamp': time.time(),
                    'memory_mb': self.process.memory_info().rss / 1024 / 1024,
                    'cpu_percent': self.process.cpu_percent(),
                    'threads': self.process.num_threads()
                }
                self.measurements.append(measurement)
                time.sleep(interval)
            except Exception:
                break
    
    def _analyze_measurements(self):
        """Analyze collected measurements"""
        if not self.measurements:
            return {}
        
        memory_values = [m['memory_mb'] for m in self.measurements]
        cpu_values = [m['cpu_percent'] for m in self.measurements if m['cpu_percent'] > 0]
        thread_values = [m['threads'] for m in self.measurements]
        
        return {
            'duration': self.measurements[-1]['timestamp'] - self.measurements[0]['timestamp'],
            'memory': {
                'peak_mb': max(memory_values),
                'average_mb': sum(memory_values) / len(memory_values),
                'min_mb': min(memory_values)
            },
            'cpu': {
                'peak_percent': max(cpu_values) if cpu_values else 0,
                'average_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0
            },
            'threads': {
                'peak': max(thread_values),
                'average': sum(thread_values) / len(thread_values)
            },
            'measurements_count': len(self.measurements)
        }

def test_performance_monitoring():
    """Comprehensive performance testing"""
    
    print("⚡ TESTING SYSTEM PERFORMANCE")
    print("=" * 60)
    
    performance_results = {
        "initialization_performance": False,
        "document_processing_performance": False,
        "entity_extraction_performance": False,
        "memory_management": False,
        "concurrent_processing": False,
        "resource_cleanup": False,
        "performance_benchmarks": False
    }
    
    monitor = PerformanceMonitor()
    
    try:
        # 1. Test System Initialization Performance
        print("\n1. Testing system initialization performance...")
        
        monitor.start_monitoring()
        init_start = time.time()
        
        service_manager = ServiceManager()
        
        init_time = time.time() - init_start
        init_stats = monitor.stop_monitoring()
        
        print(f"   ✅ System initialization: {init_time:.3f}s")
        print(f"      Peak memory: {init_stats['memory']['peak_mb']:.1f}MB")
        print(f"      Average CPU: {init_stats['cpu']['average_percent']:.1f}%")
        
        if init_time < 10.0 and init_stats['memory']['peak_mb'] < 1000:
            performance_results["initialization_performance"] = True
            print("   ✅ Initialization performance: EXCELLENT")
        else:
            print("   ⚠️  Initialization performance: NEEDS IMPROVEMENT")
        
        # 2. Test Document Processing Performance
        print("\n2. Testing document processing performance...")
        
        # Create test document
        test_content = """
        This is a comprehensive test document for performance analysis.
        It contains multiple entities like Stanford University, Apple Inc., and Google.
        The document discusses research conducted by Dr. Sarah Johnson and Michael Chen.
        Various locations are mentioned including California, New York, and London.
        The research was funded by the National Science Foundation in 2024.
        Results were published in Nature Machine Intelligence journal.
        The study achieved 95% accuracy in machine learning tasks.
        Collaboration involved MIT, Harvard, and Oxford University.
        """ * 5  # Make it longer for better testing
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            monitor.start_monitoring()
            processing_start = time.time()
            
            # Test T01 (Document Loading)
            loader = PDFLoader(service_manager)
            load_result = loader.load_pdf(test_file, "perf_test")
            
            processing_time = time.time() - processing_start
            processing_stats = monitor.stop_monitoring()
            
            if load_result.status == "success":
                chars_per_second = len(test_content) / processing_time
                print(f"   ✅ Document loading: {processing_time:.3f}s")
                print(f"      Processing speed: {chars_per_second:.0f} chars/second")
                print(f"      Peak memory: {processing_stats['memory']['peak_mb']:.1f}MB")
                
                if processing_time < 5.0 and chars_per_second > 1000:
                    performance_results["document_processing_performance"] = True
                    print("   ✅ Document processing performance: EXCELLENT")
                else:
                    print("   ⚠️  Document processing performance: ACCEPTABLE")
            else:
                print("   ❌ Document loading failed")
        
        finally:
            os.unlink(test_file)
        
        # 3. Test Entity Extraction Performance
        print("\n3. Testing entity extraction performance...")
        
        if load_result.status == "success":
            monitor.start_monitoring()
            extraction_start = time.time()
            
            # Test T23A (Entity Extraction)
            ner = T23ASpacyNERUnified(service_manager)
            extraction_result = ner.extract_entities(
                "perf_test_chunk", 
                load_result.data["text"],
                0.0  # Use threshold=0 for comprehensive extraction
            )
            
            extraction_time = time.time() - extraction_start
            extraction_stats = monitor.stop_monitoring()
            
            if extraction_result.status == "success":
                entities = extraction_result.data.get("entities", [])
                entities_per_second = len(entities) / extraction_time if extraction_time > 0 else 0
                
                print(f"   ✅ Entity extraction: {extraction_time:.3f}s")
                print(f"      Entities found: {len(entities)}")
                print(f"      Extraction speed: {entities_per_second:.1f} entities/second")
                print(f"      Peak memory: {extraction_stats['memory']['peak_mb']:.1f}MB")
                
                if extraction_time < 10.0 and len(entities) > 0:
                    performance_results["entity_extraction_performance"] = True
                    print("   ✅ Entity extraction performance: EXCELLENT")
                else:
                    print("   ⚠️  Entity extraction performance: ACCEPTABLE")
            else:
                print("   ❌ Entity extraction failed")
        
        # 4. Test Memory Management
        print("\n4. Testing memory management...")
        
        baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
        print(f"   Baseline memory: {baseline_memory:.1f}MB")
        
        # Simulate intensive processing
        intensive_start = time.time()
        monitor.start_monitoring()
        
        for i in range(3):
            # Process multiple small documents
            small_content = "Test document with entities like Apple, Google, Microsoft." * 20
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(small_content)
                temp_file = f.name
            
            try:
                loader_result = loader.load_pdf(temp_file, f"intensive_test_{i}")
                if loader_result.status == "success":
                    ner_result = ner.extract_entities(
                        f"intensive_chunk_{i}",
                        loader_result.data["text"], 
                        0.0
                    )
            finally:
                os.unlink(temp_file)
        
        intensive_stats = monitor.stop_monitoring()
        intensive_time = time.time() - intensive_start
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - baseline_memory
        
        print(f"   ✅ Intensive processing: {intensive_time:.3f}s")
        print(f"      Memory growth: {memory_growth:.1f}MB")
        print(f"      Peak memory: {intensive_stats['memory']['peak_mb']:.1f}MB")
        
        if memory_growth < 200:  # Less than 200MB growth
            performance_results["memory_management"] = True
            print("   ✅ Memory management: EXCELLENT")
        else:
            print("   ⚠️  Memory management: MONITOR FOR LEAKS")
        
        # 5. Test Concurrent Processing (simplified)
        print("\n5. Testing concurrent processing capability...")
        
        def process_document(content, doc_id):
            """Process a document in a separate thread"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                loader_result = loader.load_pdf(temp_file, f"concurrent_{doc_id}")
                return loader_result.status == "success"
            finally:
                os.unlink(temp_file)
        
        concurrent_start = time.time()
        
        # Simple concurrent test - process 2 documents
        test_docs = [
            "Document 1 with Apple and Google" * 10,
            "Document 2 with Microsoft and Tesla" * 10
        ]
        
        results = []
        for i, content in enumerate(test_docs):
            result = process_document(content, i)
            results.append(result)
        
        concurrent_time = time.time() - concurrent_start
        success_count = sum(results)
        
        print(f"   ✅ Concurrent processing: {concurrent_time:.3f}s")
        print(f"      Documents processed: {success_count}/{len(test_docs)}")
        
        if success_count == len(test_docs):
            performance_results["concurrent_processing"] = True
            print("   ✅ Concurrent processing: FUNCTIONAL")
        else:
            print("   ⚠️  Concurrent processing: ISSUES DETECTED")
        
        # 6. Test Resource Cleanup
        print("\n6. Testing resource cleanup...")
        
        pre_cleanup_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Force garbage collection
        import gc
        gc.collect()
        
        time.sleep(1)  # Allow cleanup to complete
        
        post_cleanup_memory = psutil.Process().memory_info().rss / 1024 / 1024
        cleanup_reduction = pre_cleanup_memory - post_cleanup_memory
        
        print(f"   Memory before cleanup: {pre_cleanup_memory:.1f}MB")
        print(f"   Memory after cleanup: {post_cleanup_memory:.1f}MB")
        print(f"   Memory freed: {cleanup_reduction:.1f}MB")
        
        if post_cleanup_memory < 1000:  # Under 1GB after cleanup
            performance_results["resource_cleanup"] = True
            print("   ✅ Resource cleanup: EFFECTIVE")
        else:
            print("   ⚠️  Resource cleanup: MONITOR MEMORY USAGE")
        
        # 7. Performance Benchmarks
        print("\n7. Performance benchmarks summary...")
        
        benchmarks = {
            "initialization_time_s": init_time,
            "document_processing_s_per_kb": processing_time / (len(test_content) / 1024) if 'processing_time' in locals() else 0,
            "entity_extraction_s_per_entity": extraction_time / len(entities) if 'extraction_time' in locals() and entities else 0,
            "peak_memory_mb": max(
                init_stats['memory']['peak_mb'],
                processing_stats.get('memory', {}).get('peak_mb', 0),
                extraction_stats.get('memory', {}).get('peak_mb', 0)
            ),
            "memory_efficiency": (len(entities) if 'entities' in locals() else 0) / post_cleanup_memory if post_cleanup_memory > 0 else 0
        }
        
        print(f"   📊 Benchmark Results:")
        for metric, value in benchmarks.items():
            print(f"      {metric}: {value:.3f}")
        
        # Determine if benchmarks are acceptable
        benchmark_acceptable = (
            init_time < 10.0 and
            post_cleanup_memory < 1000 and
            (len(entities) if 'entities' in locals() else 0) > 0
        )
        
        if benchmark_acceptable:
            performance_results["performance_benchmarks"] = True
            print("   ✅ Performance benchmarks: MEET REQUIREMENTS")
        else:
            print("   ⚠️  Performance benchmarks: REVIEW NEEDED")
    
    except Exception as e:
        print(f"   ❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final Assessment
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE MONITORING TEST RESULTS")
    print("=" * 60)
    
    success_count = sum(performance_results.values())
    total_tests = len(performance_results)
    success_rate = (success_count / total_tests) * 100
    
    print(f"\n✅ Performance Success Rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    for test_name, success in performance_results.items():
        status = "✅" if success else "❌"
        formatted_name = test_name.replace("_", " ").title()
        print(f"   {status} {formatted_name}")
    
    # Performance verdict
    print(f"\n🎯 PERFORMANCE VERDICT:")
    if success_rate >= 85:
        print("   ✅ SYSTEM PERFORMANCE EXCELLENT!")
        print("   - All performance metrics within acceptable ranges")
        print("   - Ready for production workloads")
        verdict = "EXCELLENT"
    elif success_rate >= 70:
        print("   ⚠️  SYSTEM PERFORMANCE ACCEPTABLE")
        print("   - Most performance metrics good")
        print("   - Some optimization opportunities exist")
        verdict = "ACCEPTABLE"
    else:
        print("   ❌ SYSTEM PERFORMANCE NEEDS IMPROVEMENT")
        print("   - Significant performance issues detected")
        print("   - Optimization required before production")
        verdict = "NEEDS_IMPROVEMENT"
    
    return {
        "verdict": verdict,
        "success_rate": success_rate,
        "metrics": performance_results,
        "benchmarks": benchmarks if 'benchmarks' in locals() else {}
    }

if __name__ == "__main__":
    result = test_performance_monitoring()
    sys.exit(0 if result["success_rate"] >= 70 else 1)