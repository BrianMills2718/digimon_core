"""Performance Validation Test - F3 from CLAUDE.md

Tests the performance improvements from service singleton and connection pooling.
Target: Validate sub-10s processing time (down from 85.4s).
"""

import time
import os
import sys
from pathlib import Path
import statistics

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
from src.core.service_manager import get_service_manager


def measure_workflow_performance(pdf_path: str, query: str, runs: int = 3):
    """Measure workflow performance over multiple runs."""
    
    print(f"\n{'='*60}")
    print("PERFORMANCE VALIDATION TEST")
    print(f"{'='*60}\n")
    
    print(f"Test Configuration:")
    print(f"- PDF: {pdf_path}")
    print(f"- Query: {query}")
    print(f"- Runs: {runs}")
    print(f"- Target: < 10 seconds (down from 85.4s)")
    print()
    
    # Get service manager stats before
    service_manager = get_service_manager()
    print("Service Manager Status (Before):")
    stats = service_manager.get_service_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    print()
    
    # Warm-up run
    print("Performing warm-up run...")
    workflow = VerticalSliceWorkflow()
    result = workflow.execute_workflow(pdf_path, query, "warmup_run")
    workflow.close()
    
    if result["status"] != "success":
        print(f"ERROR: Warm-up run failed: {result.get('error')}")
        return
    
    # Performance runs
    times = []
    print(f"\nPerforming {runs} timed runs...")
    
    for i in range(runs):
        print(f"\nRun {i+1}/{runs}:")
        
        # Time the workflow execution
        start_time = time.time()
        
        workflow = VerticalSliceWorkflow()
        result = workflow.execute_workflow(
            pdf_path, 
            query, 
            f"performance_run_{i+1}"
        )
        workflow.close()
        
        end_time = time.time()
        execution_time = end_time - start_time
        times.append(execution_time)
        
        print(f"  - Status: {result['status']}")
        print(f"  - Execution time: {execution_time:.2f}s")
        
        if result["status"] == "success":
            summary = result.get("workflow_summary", {})
            print(f"  - Entities extracted: {summary.get('entities_extracted', 0)}")
            print(f"  - Relationships found: {summary.get('relationships_found', 0)}")
            print(f"  - Graph entities: {summary.get('graph_entities', 0)}")
            print(f"  - Graph edges: {summary.get('graph_edges', 0)}")
    
    # Calculate statistics
    print(f"\n{'='*60}")
    print("PERFORMANCE RESULTS")
    print(f"{'='*60}\n")
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Execution Times:")
    for i, t in enumerate(times):
        print(f"  - Run {i+1}: {t:.2f}s")
    
    print(f"\nStatistics:")
    print(f"  - Average: {avg_time:.2f}s")
    print(f"  - Min: {min_time:.2f}s")
    print(f"  - Max: {max_time:.2f}s")
    
    # Performance comparison
    original_time = 85.4  # From CLAUDE.md
    speedup = original_time / avg_time
    
    print(f"\nPerformance Improvement:")
    print(f"  - Original time: {original_time}s")
    print(f"  - Current average: {avg_time:.2f}s")
    print(f"  - Speedup: {speedup:.1f}x")
    print(f"  - Target met: {'YES' if avg_time < 10 else 'NO'} (target < 10s)")
    
    # Service manager stats after
    print(f"\nService Manager Status (After):")
    stats = service_manager.get_service_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # Detailed performance breakdown
    print(f"\n{'='*60}")
    print("PERFORMANCE BREAKDOWN")
    print(f"{'='*60}\n")
    
    print("Expected improvements:")
    print("  - F1 Service Singleton: ~10x speedup (sharing services)")
    print("  - F2 Connection Pooling: ~3x speedup (shared Neo4j driver)")
    print(f"  - Combined theoretical: ~30x speedup")
    print(f"  - Actual speedup: {speedup:.1f}x")
    
    # Write performance report
    report_path = "performance_report.md"
    with open(report_path, "w") as f:
        f.write("# Performance Validation Report\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Original Time**: {original_time}s\n")
        f.write(f"- **Current Average**: {avg_time:.2f}s\n")
        f.write(f"- **Speedup**: {speedup:.1f}x\n")
        f.write(f"- **Target Met**: {'YES' if avg_time < 10 else 'NO'} (target < 10s)\n\n")
        f.write("## Detailed Results\n\n")
        f.write("| Run | Time (s) |\n")
        f.write("|-----|----------|\n")
        for i, t in enumerate(times):
            f.write(f"| {i+1} | {t:.2f} |\n")
        f.write(f"| **Avg** | **{avg_time:.2f}** |\n\n")
        f.write("## Optimizations Applied\n\n")
        f.write("1. **F1: Service Singleton Pattern**\n")
        f.write("   - Shared IdentityService, ProvenanceService, QualityService\n")
        f.write("   - Eliminated redundant service creation\n\n")
        f.write("2. **F2: Connection Pool Management**\n")
        f.write("   - Shared Neo4j driver with connection pooling\n")
        f.write("   - Single connection instead of 4 separate connections\n\n")
    
    print(f"\nPerformance report written to: {report_path}")


def main():
    """Run performance validation test."""
    # Test with sample PDF
    pdf_path = "./examples/pdfs/wiki1.pdf"
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"ERROR: Test file not found: {pdf_path}")
        return
    
    # Test query
    query = "Who conducted cancer research?"
    
    # Run performance test
    measure_workflow_performance(pdf_path, query, runs=3)
    
    # Cleanup
    service_manager = get_service_manager()
    service_manager.close_all()


if __name__ == "__main__":
    main()