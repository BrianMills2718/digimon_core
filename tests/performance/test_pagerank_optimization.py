"""Test PageRank Optimization

Compares original vs optimized PageRank performance.
"""

import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

from src.tools.phase1.t68_pagerank import PageRankCalculator
from src.tools.phase1.t68_pagerank_optimized import PageRankCalculatorOptimized
from src.core.service_manager import get_service_manager


def test_pagerank_optimization():
    """Compare PageRank implementations."""
    print("="*60)
    print("PAGERANK OPTIMIZATION TEST")
    print("="*60)
    print()
    
    # Get shared services
    service_manager = get_service_manager()
    identity_service = service_manager.identity_service
    provenance_service = service_manager.provenance_service
    quality_service = service_manager.quality_service
    neo4j_driver = service_manager.get_neo4j_driver()
    
    # Test original implementation
    print("Testing ORIGINAL PageRank implementation...")
    original_calc = PageRankCalculator(
        identity_service, provenance_service, quality_service,
        shared_driver=neo4j_driver
    )
    
    start_time = time.time()
    original_result = original_calc.calculate_pagerank()
    original_time = time.time() - start_time
    
    print(f"Original PageRank:")
    print(f"  - Status: {original_result['status']}")
    print(f"  - Entities ranked: {original_result.get('total_entities', 0)}")
    print(f"  - Execution time: {original_time:.2f}s")
    
    # Test optimized implementation
    print("\nTesting OPTIMIZED PageRank implementation...")
    optimized_calc = PageRankCalculatorOptimized(
        identity_service, provenance_service, quality_service,
        shared_driver=neo4j_driver
    )
    
    start_time = time.time()
    optimized_result = optimized_calc.calculate_pagerank()
    optimized_time = time.time() - start_time
    
    print(f"Optimized PageRank:")
    print(f"  - Status: {optimized_result['status']}")
    print(f"  - Entities ranked: {optimized_result.get('total_entities', 0)}")
    print(f"  - Execution time: {optimized_time:.2f}s")
    
    # Compare results
    print(f"\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*60}")
    print(f"Original time: {original_time:.2f}s")
    print(f"Optimized time: {optimized_time:.2f}s")
    print(f"Speedup: {original_time/optimized_time:.1f}x")
    print(f"Time saved: {original_time - optimized_time:.2f}s")
    
    # Verify results are similar
    if original_result['status'] == 'success' and optimized_result['status'] == 'success':
        orig_entities = original_result.get('total_entities', 0)
        opt_entities = optimized_result.get('total_entities', 0)
        
        print(f"\nResult Validation:")
        print(f"  - Original entities: {orig_entities}")
        print(f"  - Optimized entities: {opt_entities}")
        print(f"  - Match: {'YES' if orig_entities == opt_entities else 'NO'}")
        
        # Compare top 5 results
        if original_result.get('ranked_entities') and optimized_result.get('ranked_entities'):
            print(f"\nTop 5 entities comparison:")
            print(f"{'Original':<30} | {'Optimized':<30}")
            print("-"*63)
            
            for i in range(min(5, len(original_result['ranked_entities']), len(optimized_result['ranked_entities']))):
                orig = original_result['ranked_entities'][i]
                opt = optimized_result['ranked_entities'][i]
                print(f"{orig['canonical_name'][:29]:<30} | {opt['canonical_name'][:29]:<30}")
    
    # Cleanup
    service_manager.close_all()


if __name__ == "__main__":
    test_pagerank_optimization()