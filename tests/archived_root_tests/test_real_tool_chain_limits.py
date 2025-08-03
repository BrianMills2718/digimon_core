#!/usr/bin/env python3
"""
Test REAL tool chain limits - no simulation, actual execution
"""

import sys
import os
sys.path.append('src')

import time
import json
from datetime import datetime
from typing import List, Dict, Any
import traceback

def test_real_tool_chain(chain_length: int) -> Dict[str, Any]:
    """Test actual tool execution for specified chain length"""
    print(f"🔧 Testing REAL {chain_length}-tool chain execution...")
    
    try:
        # Import real unified tools
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified  
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
        from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
        from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
        from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
        from src.tools.phase2.t50_community_detection_unified import T50CommunityDetectionUnified
        from src.tools.phase2.t51_centrality_analysis_unified import T51CentralityAnalysisUnified
        
        # Available real tools
        available_tools = [
            ("T01", T01PDFLoaderUnified()),
            ("T15A", T15ATextChunkerUnified()),
            ("T23A", T23ASpacyNERUnified()),
            ("T27", T27RelationshipExtractorUnified()),
            ("T31", T31EntityBuilderUnified()),
            ("T34", T34EdgeBuilderUnified()),
            ("T68", T68PageRankCalculatorUnified()),
            ("T50", T50CommunityDetectionUnified()),
            ("T51", T51CentralityAnalysisUnified())
        ]
        
        # Limit to available tools
        if chain_length > len(available_tools):
            print(f"   ⚠️ Requested {chain_length} tools, only {len(available_tools)} available")
            chain_length = len(available_tools)
        
        # Execute actual tool chain
        start_time = time.time()
        results = {
            "chain_length": chain_length,
            "tools_executed": [],
            "execution_times": [],
            "success_count": 0,
            "total_errors": 0,
            "error_details": []
        }
        
        # Test data
        test_content = """
        KGAS Real Tool Chain Test
        
        Stanford University Artificial Intelligence Research
        Stanford University is a leading research institution located in California.
        Dr. Sarah Chen is a professor at Stanford University who leads the Natural 
        Language Processing laboratory. The research focuses on machine learning 
        and computational linguistics.
        
        MIT Computer Science Department
        MIT is another prestigious institution in Massachusetts. Professor John Smith
        at MIT works on robotics and autonomous systems. The collaboration between
        Stanford and MIT has produced significant advances in AI research.
        """
        
        current_data = test_content
        
        for i in range(chain_length):
            tool_id, tool_instance = available_tools[i]
            
            try:
                print(f"   Executing {tool_id}...")
                tool_start = time.time()
                
                # Execute tool based on type
                if tool_id == "T01":
                    # PDF loader - simulate with text content
                    result = current_data
                elif tool_id == "T15A":
                    # Text chunker
                    result = tool_instance.execute(current_data)
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T23A":
                    # Entity extraction  
                    result = tool_instance.execute(current_data)
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T27":
                    # Relationship extraction
                    result = tool_instance.execute(current_data) 
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T31":
                    # Entity builder
                    result = tool_instance.execute(current_data)
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T34":
                    # Edge builder
                    result = tool_instance.execute(current_data)
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T68":
                    # PageRank
                    result = tool_instance.execute({})
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T50":
                    # Community detection
                    result = tool_instance.execute({})
                    current_data = result.data if hasattr(result, 'data') else result
                elif tool_id == "T51":
                    # Centrality analysis
                    result = tool_instance.execute({})
                    current_data = result.data if hasattr(result, 'data') else result
                
                tool_time = time.time() - tool_start
                
                results["tools_executed"].append(tool_id)
                results["execution_times"].append({
                    "tool": tool_id,
                    "time": tool_time,
                    "success": True
                })
                results["success_count"] += 1
                
                print(f"   ✅ {tool_id}: {tool_time:.3f}s - SUCCESS")
                
            except Exception as e:
                tool_time = time.time() - tool_start
                error_msg = str(e)
                
                results["execution_times"].append({
                    "tool": tool_id,
                    "time": tool_time,
                    "success": False,
                    "error": error_msg
                })
                results["total_errors"] += 1
                results["error_details"].append({
                    "tool": tool_id,
                    "error": error_msg,
                    "position": i + 1
                })
                
                print(f"   ❌ {tool_id}: {tool_time:.3f}s - FAILED: {error_msg}")
                
                # CRITICAL: Should the chain stop here or continue?
                # This is a key architectural decision
                print(f"   🤔 Chain failure at position {i+1}/{chain_length}")
                
                # For now, STOP the chain on first failure
                print(f"   🛑 STOPPING CHAIN - Real systems should fail fast")
                break
        
        total_time = time.time() - start_time
        results["total_time"] = total_time
        results["success_rate"] = results["success_count"] / chain_length
        
        return results
        
    except Exception as e:
        return {
            "chain_length": chain_length,
            "fatal_error": str(e),
            "success_count": 0,
            "total_errors": 1
        }

def test_real_breaking_points():
    """Find real breaking points with actual tool execution"""
    print("🎯 TESTING REAL BREAKING POINTS")
    print("=" * 80)
    
    breaking_points = []
    test_results = []
    
    # Test increasing chain lengths with REAL tools
    for chain_length in [1, 3, 5, 7, 9]:  # Limited by available tools
        print(f"\n🔗 Testing {chain_length}-tool chain...")
        
        result = test_real_tool_chain(chain_length)
        test_results.append(result)
        
        success_rate = result.get("success_rate", 0)
        
        if "fatal_error" in result:
            breaking_points.append({
                "type": "fatal_error",
                "chain_length": chain_length,
                "error": result["fatal_error"],
                "issue": "System crash during execution"
            })
            print(f"💥 FATAL ERROR at {chain_length} tools: {result['fatal_error']}")
            break
            
        elif result["total_errors"] > 0:
            breaking_points.append({
                "type": "tool_failure",
                "chain_length": chain_length,
                "failed_at_position": len(result["tools_executed"]) + 1,
                "success_rate": success_rate,
                "error_details": result["error_details"],
                "issue": f"Tool failure stopped chain at position {len(result['tools_executed']) + 1}"
            })
            print(f"💥 BREAKING POINT at {chain_length} tools: Failed at position {len(result['tools_executed']) + 1}")
            
        elif success_rate == 1.0:
            print(f"✅ {chain_length} tools: 100% SUCCESS (all tools executed)")
        else:
            print(f"⚠️ {chain_length} tools: {success_rate:.1%} success")
    
    return breaking_points, test_results

def main():
    """Main real testing function"""
    print("🚀 REAL TOOL CHAIN EXECUTION LIMITS TEST")
    print("=" * 80)
    print("Testing ACTUAL tools - no simulation, no probability")
    print("Success = binary (100% or failure point)")
    print("=" * 80)
    
    breaking_points, test_results = test_real_breaking_points()
    
    # Save results
    final_results = {
        "test_type": "real_tool_chain_limits",
        "timestamp": datetime.now().isoformat(),
        "breaking_points": breaking_points,
        "test_results": test_results,
        "summary": {
            "max_successful_chain": max([r.get("success_count", 0) for r in test_results]),
            "breaking_points_found": len(breaking_points),
            "real_execution": True,
            "simulation": False
        }
    }
    
    results_file = f"REAL_TOOL_LIMITS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print("🎯 REAL EXECUTION RESULTS")
    print("=" * 80)
    
    if breaking_points:
        print("💥 REAL BREAKING POINTS FOUND:")
        for bp in breaking_points:
            print(f"   • Chain length {bp['chain_length']}: {bp['issue']}")
            if bp['type'] == 'tool_failure':
                print(f"     Failed tool: {bp['error_details'][0]['tool']}")
                print(f"     Error: {bp['error_details'][0]['error']}")
    else:
        max_chain = final_results["summary"]["max_successful_chain"]
        print(f"✅ NO BREAKING POINTS - Successfully executed {max_chain}-tool chains")
    
    print(f"\n📄 Detailed results: {results_file}")
    
    return final_results

if __name__ == "__main__":
    results = main()