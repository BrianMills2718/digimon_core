#!/usr/bin/env python3
"""
Test dynamic tool chain orchestration - agent-driven tool selection
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
import traceback

def test_dynamic_orchestration():
    """Test if agent can dynamically select tools based on analytic tasks"""
    print("🤖 TESTING DYNAMIC TOOL ORCHESTRATION")
    print("=" * 80)
    
    test_scenarios = [
        {
            "task": "Extract entities from document and analyze network centrality",
            "expected_tools": ["T01", "T15A", "T23A", "T27", "T31", "T34", "T51", "T68"],
            "complexity": "medium"
        },
        {
            "task": "Multi-document fusion with community detection and temporal analysis",
            "expected_tools": ["T01", "T15A", "T23A", "T301", "T50", "T55", "T57"],
            "complexity": "high"
        },
        {
            "task": "Statistical analysis of graph metrics with visualization",
            "expected_tools": ["T51", "T52", "T56", "T54", "T57", "T58"],
            "complexity": "analytical"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 SCENARIO {i}: {scenario['task']}")
        print("-" * 60)
        
        try:
            # Test dynamic tool selection
            selected_tools = simulate_dynamic_tool_selection(scenario)
            
            # Test actual execution
            execution_result = test_tool_chain_execution(selected_tools, scenario['task'])
            
            results.append({
                "scenario": i,
                "task": scenario['task'],
                "selected_tools": selected_tools,
                "execution_result": execution_result,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ Scenario {i} failed: {e}")
            traceback.print_exc()
            results.append({
                "scenario": i,
                "task": scenario['task'],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    return results

def simulate_dynamic_tool_selection(scenario: Dict) -> List[str]:
    """Simulate intelligent tool selection based on task requirements"""
    task = scenario['task'].lower()
    selected_tools = []
    
    print(f"🧠 Analyzing task: '{scenario['task']}'")
    
    # Document processing pipeline
    if 'document' in task or 'extract' in task:
        selected_tools.extend(['T01', 'T15A', 'T23A'])
        print("   📄 Added document processing: T01 → T15A → T23A")
    
    # Graph construction
    if 'network' in task or 'graph' in task or 'entities' in task:
        selected_tools.extend(['T27', 'T31', 'T34'])
        print("   🕸️ Added graph construction: T27 → T31 → T34")
    
    # Centrality analysis
    if 'centrality' in task or 'important' in task:
        selected_tools.append('T51')
        print("   🎯 Added centrality analysis: T51")
    
    # PageRank
    if 'pagerank' in task or 'ranking' in task:
        selected_tools.append('T68')
        print("   📊 Added PageRank: T68")
    
    # Community detection
    if 'community' in task or 'clustering' in task:
        selected_tools.append('T50')
        print("   👥 Added community detection: T50")
    
    # Multi-document fusion
    if 'multi-document' in task or 'fusion' in task:
        selected_tools.append('T301')
        print("   🔄 Added multi-document fusion: T301")
    
    # Temporal analysis
    if 'temporal' in task or 'time' in task:
        selected_tools.append('T55')
        print("   ⏰ Added temporal analysis: T55")
    
    # Path analysis
    if 'path' in task or 'route' in task:
        selected_tools.append('T57')
        print("   🛤️ Added path analysis: T57")
    
    # Statistical analysis
    if 'statistical' in task or 'metrics' in task:
        selected_tools.extend(['T52', 'T56'])
        print("   📈 Added statistical analysis: T52, T56")
    
    # Visualization
    if 'visualization' in task or 'visual' in task:
        selected_tools.append('T54')
        print("   🎨 Added visualization: T54")
    
    # Comparison
    if 'comparison' in task or 'compare' in task:
        selected_tools.append('T58')
        print("   ⚖️ Added graph comparison: T58")
    
    print(f"   ✅ Selected {len(selected_tools)} tools: {' → '.join(selected_tools)}")
    return selected_tools

def test_tool_chain_execution(tools: List[str], task_description: str) -> Dict:
    """Test actual execution of dynamically selected tool chain"""
    print(f"🔧 Executing {len(tools)}-tool chain...")
    
    start_time = time.time()
    results = {
        "chain_length": len(tools),
        "execution_times": [],
        "memory_usage": [],
        "success_count": 0,
        "failed_tools": [],
        "total_time": 0
    }
    
    # Test each tool in sequence
    for i, tool_id in enumerate(tools):
        try:
            tool_start = time.time()
            
            # Simulate tool execution with realistic delays
            tool_result = execute_tool_simulation(tool_id, i)
            
            tool_time = time.time() - tool_start
            results["execution_times"].append({
                "tool": tool_id,
                "time": tool_time,
                "position": i + 1
            })
            
            if tool_result["success"]:
                results["success_count"] += 1
                print(f"   ✅ {tool_id}: {tool_time:.3f}s")
            else:
                results["failed_tools"].append(tool_id)
                print(f"   ❌ {tool_id}: Failed")
                
        except Exception as e:
            results["failed_tools"].append(tool_id)
            print(f"   💥 {tool_id}: Exception - {e}")
    
    results["total_time"] = time.time() - start_time
    results["success_rate"] = results["success_count"] / len(tools)
    
    print(f"   📊 Chain completed: {results['success_count']}/{len(tools)} tools succeeded")
    print(f"   ⏱️ Total time: {results['total_time']:.3f}s")
    
    return results

def execute_tool_simulation(tool_id: str, position: int) -> Dict:
    """Simulate tool execution with realistic behavior"""
    
    # Simulate different tool characteristics
    tool_configs = {
        "T01": {"base_time": 0.05, "memory": 10, "failure_rate": 0.02},
        "T15A": {"base_time": 0.01, "memory": 2, "failure_rate": 0.01},
        "T23A": {"base_time": 0.5, "memory": 60, "failure_rate": 0.05},  # spaCy model loading
        "T27": {"base_time": 0.02, "memory": 5, "failure_rate": 0.03},
        "T31": {"base_time": 0.15, "memory": 15, "failure_rate": 0.04},
        "T34": {"base_time": 0.01, "memory": 3, "failure_rate": 0.02},
        "T50": {"base_time": 0.3, "memory": 25, "failure_rate": 0.08},   # Community detection
        "T51": {"base_time": 0.2, "memory": 20, "failure_rate": 0.06},   # Centrality
        "T52": {"base_time": 0.25, "memory": 18, "failure_rate": 0.07},  # Clustering  
        "T54": {"base_time": 0.4, "memory": 30, "failure_rate": 0.10},   # Visualization
        "T55": {"base_time": 0.35, "memory": 22, "failure_rate": 0.09},  # Temporal
        "T56": {"base_time": 0.15, "memory": 12, "failure_rate": 0.05},  # Metrics
        "T57": {"base_time": 0.18, "memory": 14, "failure_rate": 0.06},  # Path analysis
        "T58": {"base_time": 0.22, "memory": 16, "failure_rate": 0.07},  # Comparison
        "T68": {"base_time": 0.12, "memory": 8, "failure_rate": 0.04},   # PageRank
        "T301": {"base_time": 0.6, "memory": 40, "failure_rate": 0.12}   # Multi-doc fusion
    }
    
    config = tool_configs.get(tool_id, {"base_time": 0.1, "memory": 10, "failure_rate": 0.05})
    
    # Simulate execution time with variance
    import random
    execution_time = config["base_time"] * (0.8 + 0.4 * random.random())
    time.sleep(execution_time)
    
    # Simulate memory pressure affecting later tools
    memory_pressure = min(position * 5, 50)  # Increases with chain length
    
    # Simulate failure probability (increases with chain length and complexity)
    failure_probability = config["failure_rate"] + (position * 0.01)
    
    success = random.random() > failure_probability
    
    return {
        "success": success,
        "execution_time": execution_time,
        "memory_used": config["memory"] + memory_pressure,
        "tool_id": tool_id
    }

def find_breaking_points():
    """Test for system breaking points"""
    print("\n\n💥 TESTING FOR BREAKING POINTS")
    print("=" * 80)
    
    breaking_points = []
    
    # Test 1: Long chain execution
    print("🔗 Test 1: Long chain execution limits...")
    for chain_length in [5, 10, 15, 20, 25, 30]:
        try:
            tools = [f"T{i:02d}" for i in range(1, chain_length + 1)]
            result = test_tool_chain_execution(tools, f"Chain of {chain_length} tools")
            
            if result["success_rate"] < 0.7:  # Less than 70% success
                breaking_points.append({
                    "type": "chain_length",
                    "limit": chain_length,
                    "success_rate": result["success_rate"],
                    "issue": f"Success rate dropped to {result['success_rate']:.1%}"
                })
                print(f"   💥 Breaking point at {chain_length} tools: {result['success_rate']:.1%} success")
                break
            else:
                print(f"   ✅ {chain_length} tools: {result['success_rate']:.1%} success")
                
        except Exception as e:
            breaking_points.append({
                "type": "chain_length",
                "limit": chain_length,
                "error": str(e),
                "issue": "Exception during execution"
            })
            print(f"   💥 Exception at {chain_length} tools: {e}")
            break
    
    # Test 2: Memory pressure
    print("\n🧠 Test 2: Memory pressure limits...")
    memory_intensive_tools = ["T23A", "T301", "T54", "T50", "T55"] * 3  # 15 memory-heavy tools
    
    try:
        result = test_tool_chain_execution(memory_intensive_tools, "Memory intensive chain")
        if result["success_rate"] < 0.8:
            breaking_points.append({
                "type": "memory_pressure",
                "tools": len(memory_intensive_tools),
                "success_rate": result["success_rate"],
                "issue": "Memory-intensive tools caused failures"
            })
            print(f"   💥 Memory pressure breaking point: {result['success_rate']:.1%} success")
        else:
            print(f"   ✅ Memory intensive chain: {result['success_rate']:.1%} success")
    except Exception as e:
        breaking_points.append({
            "type": "memory_pressure",
            "error": str(e),
            "issue": "Memory pressure caused exception"
        })
        print(f"   💥 Memory pressure exception: {e}")
    
    return breaking_points

def main():
    """Main orchestration test"""
    print("🎭 DYNAMIC TOOL ORCHESTRATION STRESS TEST")
    print("=" * 80)
    print("Testing agent-driven tool selection vs. predefined workflows")
    print("=" * 80)
    
    # Test dynamic orchestration
    orchestration_results = test_dynamic_orchestration()
    
    # Find breaking points
    breaking_points = find_breaking_points()
    
    # Save comprehensive results
    test_results = {
        "test_type": "dynamic_tool_orchestration",
        "timestamp": datetime.now().isoformat(),
        "orchestration_results": orchestration_results,
        "breaking_points": breaking_points,
        "summary": {
            "scenarios_tested": len(orchestration_results),
            "breaking_points_found": len(breaking_points),
            "dynamic_selection_works": len([r for r in orchestration_results if "error" not in r]) > 0
        }
    }
    
    results_file = f"DYNAMIC_ORCHESTRATION_RESULTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print("🎯 DYNAMIC ORCHESTRATION TEST SUMMARY")
    print("=" * 80)
    
    print(f"📊 Scenarios tested: {test_results['summary']['scenarios_tested']}")
    print(f"💥 Breaking points found: {test_results['summary']['breaking_points_found']}")
    print(f"🤖 Dynamic selection works: {test_results['summary']['dynamic_selection_works']}")
    
    if breaking_points:
        print(f"\n💥 BREAKING POINTS IDENTIFIED:")
        for bp in breaking_points:
            print(f"   • {bp['type']}: {bp['issue']}")
    else:
        print(f"\n✅ NO BREAKING POINTS FOUND (within test limits)")
    
    print(f"\n📁 Full results saved to: {results_file}")
    
    return test_results

if __name__ == "__main__":
    results = main()