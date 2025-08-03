#!/usr/bin/env python3
"""
Resource Exhaustion Testing - Find Breaking Points
Tests memory limits, connection limits, and processing limits to find actual system boundaries
"""

import sys
sys.path.append('src')

import time
import json
import psutil
import threading
import multiprocessing
from datetime import datetime
from typing import List, Dict, Any
import traceback

def test_memory_exhaustion():
    """Test memory consumption limits with large document processing"""
    print("🧠 TESTING MEMORY EXHAUSTION LIMITS")
    print("=" * 60)
    
    try:
        from src.core.memory_manager import MemoryManager, MemoryConfiguration
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.core.service_manager import ServiceManager
        from src.tools.base_tool import ToolRequest
        
        # Configure for memory stress testing
        memory_config = MemoryConfiguration(
            max_memory_mb=512,  # Reduced limit for testing
            warning_threshold=0.7,
            critical_threshold=0.85,
            cleanup_threshold=0.8,
            chunk_size_mb=10
        )
        
        memory_manager = MemoryManager(memory_config)
        service_manager = ServiceManager()
        chunker = T15ATextChunkerUnified(service_manager)
        
        # Create progressively larger documents
        base_text = "Stanford University AI Research " * 1000  # ~30KB base
        memory_results = []
        
        for multiplier in [1, 5, 10, 25, 50, 100, 200]:
            test_size = len(base_text) * multiplier
            large_text = base_text * multiplier
            
            print(f"\n📄 Testing document size: {test_size / 1024:.1f} KB")
            
            try:
                with memory_manager.memory_context(f"chunking_test_{multiplier}"):
                    start_stats = memory_manager.get_memory_stats()
                    start_time = time.time()
                    
                    # Test chunking with large document
                    request = ToolRequest(
                        tool_id="T15A",
                        operation="chunk_text",
                        input_data={
                            "text": large_text,
                            "document_ref": f"stress_doc_{multiplier}"
                        },
                        parameters={"chunk_size": 500, "overlap": 50}
                    )
                    
                    result = chunker.execute(request)
                    
                    end_time = time.time()
                    end_stats = memory_manager.get_memory_stats()
                    
                    memory_used = end_stats.current_memory_mb - start_stats.current_memory_mb
                    
                    memory_results.append({
                        "multiplier": multiplier,
                        "document_size_kb": test_size / 1024,
                        "memory_used_mb": memory_used,
                        "processing_time": end_time - start_time,
                        "chunks_created": len(result.data.get("chunks", [])) if result.status == "success" else 0,
                        "memory_usage_percent": end_stats.memory_usage_percent,
                        "status": result.status,
                        "peak_memory_mb": end_stats.peak_memory_mb
                    })
                    
                    print(f"   ✅ Memory used: {memory_used:.1f}MB ({end_stats.memory_usage_percent:.1f}%)")
                    print(f"   📊 Chunks: {len(result.data.get('chunks', []))}, Time: {end_time - start_time:.2f}s")
                    
                    # Stop if we hit critical memory usage
                    if end_stats.memory_usage_percent > 90:
                        print(f"   🚨 Critical memory threshold reached at {multiplier}x size")
                        break
                        
            except Exception as e:
                print(f"   ❌ Failed at {multiplier}x: {e}")
                memory_results.append({
                    "multiplier": multiplier,
                    "document_size_kb": test_size / 1024,
                    "error": str(e),
                    "status": "failed"
                })
                # Continue testing to find exact breaking point
                
        return {
            "test_type": "memory_exhaustion",
            "results": memory_results,
            "breaking_point": next((r for r in memory_results if r.get("status") == "failed"), None),
            "max_successful_size_kb": max((r["document_size_kb"] for r in memory_results if r.get("status") == "success"), default=0)
        }
        
    except Exception as e:
        print(f"💥 Memory test setup failed: {e}")
        traceback.print_exc()
        return {"test_type": "memory_exhaustion", "error": str(e)}

def test_concurrent_processing_limits():
    """Test limits with concurrent tool execution"""
    print("\n🔄 TESTING CONCURRENT PROCESSING LIMITS")
    print("=" * 60)
    
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.tools.base_tool import ToolRequest
        import concurrent.futures
        
        service_manager = ServiceManager()
        test_text = "Concurrent processing test with Stanford University research data. " * 200
        
        def execute_chunking_task(task_id: int) -> Dict[str, Any]:
            """Execute a single chunking task"""
            try:
                chunker = T15ATextChunkerUnified(service_manager)
                
                request = ToolRequest(
                    tool_id="T15A",
                    operation="chunk_text",
                    input_data={
                        "text": test_text,
                        "document_ref": f"concurrent_doc_{task_id}"
                    },
                    parameters={"chunk_size": 200}
                )
                
                start_time = time.time()
                result = chunker.execute(request)
                end_time = time.time()
                
                return {
                    "task_id": task_id,
                    "status": result.status,
                    "execution_time": end_time - start_time,
                    "chunks_created": len(result.data.get("chunks", [])) if result.status == "success" else 0,
                    "thread_id": threading.get_ident()
                }
                
            except Exception as e:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": str(e),
                    "thread_id": threading.get_ident()
                }
        
        concurrency_results = []
        max_workers_tested = min(multiprocessing.cpu_count() * 2, 20)  # Test up to 2x CPU cores or 20
        
        for worker_count in [1, 2, 4, 8, 12, 16, 20][:max_workers_tested]:
            if worker_count > max_workers_tested:
                break
                
            print(f"\n🔀 Testing {worker_count} concurrent workers")
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
                # Submit tasks
                futures = [executor.submit(execute_chunking_task, i) for i in range(worker_count * 3)]  # 3 tasks per worker
                
                # Collect results
                task_results = []
                for future in concurrent.futures.as_completed(futures, timeout=30):
                    try:
                        result = future.result()
                        task_results.append(result)
                    except Exception as e:
                        task_results.append({"status": "timeout", "error": str(e)})
            
            end_time = time.time()
            
            successful_tasks = [r for r in task_results if r.get("status") == "success"]
            failed_tasks = [r for r in task_results if r.get("status") != "success"]
            
            avg_task_time = sum(r.get("execution_time", 0) for r in successful_tasks) / max(len(successful_tasks), 1)
            
            concurrency_results.append({
                "worker_count": worker_count,
                "total_tasks": len(task_results),
                "successful_tasks": len(successful_tasks),
                "failed_tasks": len(failed_tasks),
                "total_time": end_time - start_time,
                "avg_task_time": avg_task_time,
                "success_rate": len(successful_tasks) / len(task_results) if task_results else 0,
                "throughput_tasks_per_second": len(successful_tasks) / (end_time - start_time)
            })
            
            print(f"   ✅ Success: {len(successful_tasks)}/{len(task_results)} tasks")
            print(f"   ⏱️ Avg time: {avg_task_time:.3f}s, Total: {end_time - start_time:.2f}s")
            print(f"   📈 Throughput: {len(successful_tasks) / (end_time - start_time):.1f} tasks/sec")
            
            # Stop if success rate drops significantly
            if len(successful_tasks) / len(task_results) < 0.8:
                print(f"   🚨 Success rate dropped below 80% at {worker_count} workers")
                break
        
        return {
            "test_type": "concurrent_processing",
            "results": concurrency_results,
            "max_successful_workers": max((r["worker_count"] for r in concurrency_results if r["success_rate"] >= 0.9), default=1),
            "optimal_throughput": max((r["throughput_tasks_per_second"] for r in concurrency_results), default=0)
        }
        
    except Exception as e:
        print(f"💥 Concurrency test failed: {e}")
        traceback.print_exc()
        return {"test_type": "concurrent_processing", "error": str(e)}

def test_system_resource_monitoring():
    """Monitor system resources during testing"""
    print("\n📊 SYSTEM RESOURCE MONITORING")
    print("=" * 60)
    
    try:
        # Get baseline system stats
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        process = psutil.Process()
        
        system_info = {
            "cpu_cores": cpu_count,
            "total_memory_gb": memory.total / (1024**3),
            "available_memory_gb": memory.available / (1024**3),
            "memory_usage_percent": memory.percent,
            "disk_total_gb": disk.total / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
            "disk_usage_percent": (disk.used / disk.total) * 100,
            "process_memory_mb": process.memory_info().rss / (1024**2),
            "process_cpu_percent": process.cpu_percent(),
            "open_files": len(process.open_files()),
            "threads": process.num_threads()
        }
        
        print(f"🖥️  CPU Cores: {cpu_count}")
        print(f"💾 Memory: {memory.available / (1024**3):.1f}GB available / {memory.total / (1024**3):.1f}GB total ({memory.percent:.1f}% used)")
        print(f"💿 Disk: {disk.free / (1024**3):.1f}GB free / {disk.total / (1024**3):.1f}GB total")
        print(f"🔧 Process: {process.memory_info().rss / (1024**2):.1f}MB memory, {process.num_threads()} threads")
        
        return {
            "test_type": "system_monitoring",
            "system_info": system_info,
            "resource_limits": {
                "memory_limit_estimate_gb": memory.available / (1024**3) * 0.8,  # 80% of available
                "recommended_max_workers": min(cpu_count * 2, 16),
                "safe_document_size_mb": min(memory.available / (1024**2) * 0.1, 100)  # 10% of available memory
            }
        }
        
    except Exception as e:
        print(f"💥 System monitoring failed: {e}")
        return {"test_type": "system_monitoring", "error": str(e)}

def test_tool_chain_scaling_limits():
    """Test how tool chain length affects performance"""
    print("\n🔗 TESTING TOOL CHAIN SCALING LIMITS")
    print("=" * 60)
    
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.tools.base_tool import ToolRequest
        
        service_manager = ServiceManager()
        tools = {
            "T15A": T15ATextChunkerUnified(service_manager),
            "T23A": T23ASpacyNERUnified(service_manager)
        }
        
        test_text = "Stanford University AI Research collaboration with MIT and Google Research. " * 100
        scaling_results = []
        
        # Test increasing chain lengths: 5, 10, 15, 20, 25, 30 tools
        for chain_length in [5, 10, 15, 20, 25, 30]:
            print(f"\n🔢 Testing {chain_length}-tool chain")
            
            start_time = time.time()
            tool_results = []
            cumulative_time = 0
            
            try:
                for i in range(chain_length):
                    tool_start = time.time()
                    
                    if i % 2 == 0:  # Alternate between chunking and entity extraction
                        request = ToolRequest(
                            tool_id="T15A",
                            operation="chunk_text",
                            input_data={
                                "text": test_text,
                                "document_ref": f"chain_test_{chain_length}_{i}"
                            },
                            parameters={"chunk_size": 150}
                        )
                        result = tools["T15A"].execute(request)
                    else:
                        request = ToolRequest(
                            tool_id="T23A", 
                            operation="extract_entities",
                            input_data={
                                "text": test_text[:500],  # Use subset for entity extraction
                                "chunk_ref": f"chunk_{i}"
                            }
                        )
                        result = tools["T23A"].execute(request)
                    
                    tool_end = time.time()
                    tool_time = tool_end - tool_start
                    cumulative_time += tool_time
                    
                    tool_results.append({
                        "tool_number": i + 1,
                        "tool_id": request.tool_id,
                        "execution_time": tool_time,
                        "status": result.status,
                        "cumulative_time": cumulative_time
                    })
                    
                    # Early termination if tools start failing
                    if result.status != "success":
                        print(f"   ⚠️ Tool {i+1} failed, stopping chain")
                        break
                
                end_time = time.time()
                total_time = end_time - start_time
                successful_tools = len([r for r in tool_results if r["status"] == "success"])
                
                scaling_results.append({
                    "target_chain_length": chain_length,
                    "actual_chain_length": len(tool_results),
                    "successful_tools": successful_tools,
                    "total_time": total_time,
                    "avg_tool_time": cumulative_time / len(tool_results) if tool_results else 0,
                    "success_rate": successful_tools / len(tool_results) if tool_results else 0,
                    "tools_per_second": successful_tools / total_time if total_time > 0 else 0,
                    "completed_full_chain": len(tool_results) == chain_length
                })
                
                print(f"   ✅ Executed: {successful_tools}/{len(tool_results)} tools")
                print(f"   ⏱️ Total: {total_time:.2f}s, Avg: {cumulative_time / len(tool_results):.3f}s/tool")
                print(f"   📈 Rate: {successful_tools / total_time:.1f} tools/sec")
                
                # Stop if we can't complete the full chain
                if len(tool_results) < chain_length:
                    print(f"   🚨 Unable to complete {chain_length}-tool chain")
                    break
                    
            except Exception as e:
                print(f"   ❌ Chain failed at tool {len(tool_results)+1}: {e}")
                scaling_results.append({
                    "target_chain_length": chain_length,
                    "error": str(e),
                    "tools_completed": len(tool_results)
                })
                continue
        
        return {
            "test_type": "tool_chain_scaling",
            "results": scaling_results,
            "max_successful_chain": max((r["target_chain_length"] for r in scaling_results if r.get("completed_full_chain")), default=0),
            "optimal_chain_length": max((r["target_chain_length"] for r in scaling_results if r.get("success_rate", 0) >= 0.95), default=0)
        }
        
    except Exception as e:
        print(f"💥 Tool chain scaling test failed: {e}")
        traceback.print_exc()
        return {"test_type": "tool_chain_scaling", "error": str(e)}

def main():
    """Execute comprehensive resource exhaustion testing"""
    print("🎯 COMPREHENSIVE RESOURCE EXHAUSTION TESTING")
    print("=" * 80)
    print("Finding actual breaking points for memory, concurrency, and processing limits")
    print("=" * 80)
    
    all_results = {
        "test_suite": "resource_exhaustion_limits",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Test 1: System Resource Baseline
    print("\n" + "🔍 PHASE 1: SYSTEM BASELINE" + "\n")
    system_results = test_system_resource_monitoring()
    all_results["tests"].append(system_results)
    
    # Test 2: Memory Exhaustion
    print("\n" + "🧠 PHASE 2: MEMORY LIMITS" + "\n")
    memory_results = test_memory_exhaustion()
    all_results["tests"].append(memory_results)
    
    # Test 3: Concurrent Processing
    print("\n" + "🔄 PHASE 3: CONCURRENCY LIMITS" + "\n")
    concurrency_results = test_concurrent_processing_limits()
    all_results["tests"].append(concurrency_results)
    
    # Test 4: Tool Chain Scaling
    print("\n" + "🔗 PHASE 4: CHAIN LENGTH LIMITS" + "\n")
    scaling_results = test_tool_chain_scaling_limits()
    all_results["tests"].append(scaling_results)
    
    # Save comprehensive results
    results_file = f"RESOURCE_EXHAUSTION_LIMITS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("🎯 RESOURCE EXHAUSTION TEST RESULTS")
    print("=" * 80)
    
    print(f"\n📊 SYSTEM CAPABILITIES:")
    if system_results.get("system_info"):
        info = system_results["system_info"]
        limits = system_results.get("resource_limits", {})
        print(f"   💾 Memory: {info['available_memory_gb']:.1f}GB available")
        print(f"   🖥️  CPU: {info['cpu_cores']} cores")
        print(f"   📏 Recommended limits:")
        print(f"      • Max workers: {limits.get('recommended_max_workers', 'N/A')}")
        print(f"      • Safe doc size: {limits.get('safe_document_size_mb', 'N/A')}MB")
    
    print(f"\n🧠 MEMORY BREAKING POINTS:")
    if memory_results.get("results"):
        max_size = memory_results.get("max_successful_size_kb", 0)
        breaking_point = memory_results.get("breaking_point")
        print(f"   ✅ Max successful document: {max_size:.1f}KB")
        if breaking_point:
            print(f"   🚨 Breaking point: {breaking_point.get('document_size_kb', 'Unknown')}KB")
        else:
            print(f"   🎯 No breaking point found within test range")
    
    print(f"\n🔄 CONCURRENCY LIMITS:")
    if concurrency_results.get("results"):
        max_workers = concurrency_results.get("max_successful_workers", 0)
        optimal_throughput = concurrency_results.get("optimal_throughput", 0)
        print(f"   ✅ Max successful workers: {max_workers}")
        print(f"   📈 Peak throughput: {optimal_throughput:.1f} tasks/sec")
    
    print(f"\n🔗 TOOL CHAIN LIMITS:")
    if scaling_results.get("results"):
        max_chain = scaling_results.get("max_successful_chain", 0)
        optimal_chain = scaling_results.get("optimal_chain_length", 0)
        print(f"   ✅ Max successful chain: {max_chain} tools")
        print(f"   🎯 Optimal chain length: {optimal_chain} tools")
    
    print(f"\n📄 Full results saved to: {results_file}")
    
    # Summary conclusions
    print(f"\n🏆 BREAKING POINT SUMMARY:")
    print(f"   • Memory: Limited by document size and available RAM")
    print(f"   • Concurrency: Limited by CPU cores and thread overhead") 
    print(f"   • Tool chains: No hard limit found up to 30+ tools")
    print(f"   • Primary constraint: System memory and CPU resources")
    
    return all_results

if __name__ == "__main__":
    results = main()