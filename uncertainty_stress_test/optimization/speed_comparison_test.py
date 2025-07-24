#!/usr/bin/env python3
"""
Compare sequential vs parallel LLM processing for uncertainty assessment
"""

import asyncio
import time
import os
import json
from pathlib import Path
import sys

# Add core services to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from llm_native_uncertainty_engine import LLMNativeUncertaintyEngine

async def test_sequential_vs_parallel():
    """Compare sequential vs optimized parallel processing"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key available")
        return
    
    engine = LLMNativeUncertaintyEngine(api_key)
    
    test_case = {
        "text": """
        A large randomized controlled trial (N=2,847) published in New England Journal of Medicine 
        found that treatment X reduces mortality by 35% (95% CI: 28-42%, p<0.001). The study was 
        conducted across 15 medical centers with rigorous inclusion criteria, double-blinding, and 
        independent data monitoring. Follow-up was complete for 98% of participants over 3 years.
        """,
        "claim": "Treatment X significantly reduces mortality compared to standard care",
        "domain": "medical_research"
    }
    
    print("⚡ Speed Optimization Test: Sequential vs Parallel LLM Calls")
    print("=" * 70)
    
    # Test 1: Current sequential approach
    print("\n📊 Testing Current Sequential Approach:")
    start_time = time.time()
    
    confidence_score = await engine.assess_contextual_confidence(
        test_case["text"], test_case["claim"], test_case["domain"]
    )
    
    sequential_time = time.time() - start_time
    print(f"✅ Sequential Time: {sequential_time:.1f}s")
    print(f"   Confidence: {confidence_score.value:.4f}")
    print(f"   API Calls: {engine.api_calls_made}")
    
    # Test 2: Parallel optimization simulation
    print("\n⚡ Simulating Parallel Optimization:")
    
    # Reset API call counter
    engine.api_calls_made = 0
    
    # Simulate parallel calls by timing individual components
    start_time = time.time()
    
    # These would normally be run in parallel with asyncio.gather()
    # For now, we'll measure the longest single call to estimate parallel time
    
    # Create test prompts (simplified)
    prior_prompt = f"Determine epistemic prior for claim: {test_case['claim']}"
    evidence_prompt = f"Assess evidence quality for: {test_case['text'][:500]}"
    
    # Time individual calls to estimate parallel performance
    call_times = []
    
    # Simulate prior assessment call
    call_start = time.time()
    await engine._make_llm_call(prior_prompt, max_tokens=400)
    call_times.append(time.time() - call_start)
    
    # Simulate evidence assessment call
    call_start = time.time()
    await engine._make_llm_call(evidence_prompt, max_tokens=400)
    call_times.append(time.time() - call_start)
    
    # Simulate synthesis call (would happen after the parallel calls)
    call_start = time.time()
    synthesis_prompt = "Synthesize final confidence based on prior and evidence assessment"
    await engine._make_llm_call(synthesis_prompt, max_tokens=400)
    synthesis_time = time.time() - call_start
    
    # Parallel time = max(parallel_calls) + synthesis_call
    parallel_time = max(call_times) + synthesis_time
    
    print(f"✅ Estimated Parallel Time: {parallel_time:.1f}s")
    print(f"   Individual call times: {[f'{t:.1f}s' for t in call_times]} + {synthesis_time:.1f}s")
    
    # Calculate improvement
    speed_improvement = ((sequential_time - parallel_time) / sequential_time) * 100
    speedup_factor = sequential_time / parallel_time
    
    print(f"\n🚀 Optimization Results:")
    print(f"Sequential Time: {sequential_time:.1f}s")
    print(f"Parallel Time:   {parallel_time:.1f}s")
    print(f"Speed Improvement: {speed_improvement:.1f}%")
    print(f"Speedup Factor: {speedup_factor:.1f}x")
    print(f"Time Saved: {sequential_time - parallel_time:.1f}s")
    
    # Caching simulation
    print(f"\n💾 Caching Potential:")
    cache_hit_rate = 0.2  # 20% cache hit rate
    cache_time = 0.1     # 100ms cache lookup
    avg_call_time = max(call_times)
    
    with_cache_time = (
        (cache_hit_rate * cache_time) + 
        ((1 - cache_hit_rate) * avg_call_time)
    ) + synthesis_time
    
    total_improvement = ((sequential_time - with_cache_time) / sequential_time) * 100
    
    print(f"With 20% cache hit rate: {with_cache_time:.1f}s")
    print(f"Total improvement: {total_improvement:.1f}%")
    print(f"Final optimization: {sequential_time:.1f}s → {with_cache_time:.1f}s")
    
    return {
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "with_cache_time": with_cache_time,
        "speed_improvement": speed_improvement,
        "total_improvement": total_improvement,
        "confidence": confidence_score.value
    }

if __name__ == "__main__":
    results = asyncio.run(test_sequential_vs_parallel())
    
    # Save results
    output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/optimization")
    with open(output_dir / "speed_optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to speed_optimization_results.json")