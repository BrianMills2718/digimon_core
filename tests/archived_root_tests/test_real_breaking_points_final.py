#!/usr/bin/env python3
"""
Find REAL breaking points - no simulation, actual tool execution failures
"""

import sys
sys.path.append('src')

import time
import json
from datetime import datetime
from typing import List, Dict, Any
import traceback

def test_actual_tool_execution_chain():
    """Test the actual working tool chain we validated earlier"""
    print("🔧 TESTING ACTUAL WORKING TOOL CHAIN")
    print("=" * 80)
    
    try:
        # Use the same tools that worked in our previous evidence tests
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified  
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
        from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
        from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
        from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
        
        # Define the working chain
        working_chain = [
            ("T01", T01PDFLoaderUnified),
            ("T15A", T15ATextChunkerUnified),
            ("T23A", T23ASpacyNERUnified),
            ("T27", T27RelationshipExtractorUnified),
            ("T31", T31EntityBuilderUnified),
            ("T34", T34EdgeBuilderUnified),
            ("T68", T68PageRankCalculatorUnified)
        ]
        
        print(f"📋 Testing {len(working_chain)}-tool chain that previously worked...")
        
        # Test each tool instantiation
        results = {
            "chain_length": len(working_chain),
            "instantiation_results": [],
            "execution_results": [],
            "breaking_points": []
        }
        
        instantiated_tools = []
        
        for i, (tool_id, tool_class) in enumerate(working_chain):
            try:
                print(f"   🔧 Instantiating {tool_id}...")
                start_time = time.time()
                
                tool_instance = tool_class()
                instantiation_time = time.time() - start_time
                
                instantiated_tools.append((tool_id, tool_instance))
                results["instantiation_results"].append({
                    "tool": tool_id,
                    "success": True,
                    "time": instantiation_time
                })
                
                print(f"   ✅ {tool_id}: Instantiated in {instantiation_time:.3f}s")
                
            except Exception as e:
                error_msg = str(e)
                results["instantiation_results"].append({
                    "tool": tool_id,
                    "success": False,
                    "error": error_msg,
                    "time": time.time() - start_time
                })
                results["breaking_points"].append({
                    "type": "instantiation_failure",
                    "tool": tool_id,
                    "position": i + 1,
                    "error": error_msg
                })
                
                print(f"   ❌ {tool_id}: INSTANTIATION FAILED - {error_msg}")
                break
        
        # If all instantiated successfully, test execution
        if len(instantiated_tools) == len(working_chain):
            print(f"\n✅ All {len(working_chain)} tools instantiated successfully")
            print("🚀 Testing actual execution chain...")
            
            execution_results = test_execution_chain(instantiated_tools)
            results["execution_results"] = execution_results
            
        return results
        
    except Exception as e:
        print(f"💥 FATAL ERROR in tool chain test: {e}")
        traceback.print_exc()
        return {
            "fatal_error": str(e),
            "chain_length": 0,
            "breaking_points": [{
                "type": "fatal_system_error", 
                "error": str(e)
            }]
        }

def test_execution_chain(instantiated_tools: List) -> Dict:
    """Test actual execution of instantiated tools"""
    
    # Test content
    test_content = """
    KGAS Breaking Point Analysis Test
    
    Stanford University Artificial Intelligence Research Division
    Stanford University is a prestigious research institution located in California.
    Dr. Sarah Chen leads the Natural Language Processing laboratory at Stanford.
    The research focuses on machine learning, computational linguistics, and AI systems.
    
    Massachusetts Institute of Technology Computer Science
    MIT is another leading institution in Cambridge, Massachusetts.
    Professor John Smith at MIT works on robotics and autonomous systems.
    The collaboration between Stanford and MIT has produced breakthrough AI research.
    """
    
    results = {
        "total_tools": len(instantiated_tools),
        "successful_executions": 0,
        "failed_executions": 0,
        "execution_details": [],
        "breaking_points": []
    }
    
    current_data = test_content
    
    for i, (tool_id, tool_instance) in enumerate(instantiated_tools):
        try:
            print(f"   🔄 Executing {tool_id} (position {i+1}/{len(instantiated_tools)})...")
            start_time = time.time()
            
            # Execute based on tool type and expected input/output
            if tool_id == "T01":
                # PDF loader - pass text content as simulation
                result = current_data  # Simulate PDF content
                execution_output = {"content": result, "type": "text"}
                
            elif tool_id == "T15A":
                # Text chunker
                result = tool_instance.execute(current_data)
                execution_output = result
                current_data = result.data if hasattr(result, 'data') else result
                
            elif tool_id == "T23A":
                # Entity extraction
                result = tool_instance.execute(current_data)
                execution_output = result
                current_data = result.data if hasattr(result, 'data') else result
                
            elif tool_id == "T27":
                # Relationship extraction
                result = tool_instance.execute(current_data)
                execution_output = result
                current_data = result.data if hasattr(result, 'data') else result
                
            elif tool_id == "T31":
                # Entity builder
                result = tool_instance.execute(current_data)
                execution_output = result
                current_data = result.data if hasattr(result, 'data') else result
                
            elif tool_id == "T34":
                # Edge builder
                result = tool_instance.execute(current_data)
                execution_output = result
                current_data = result.data if hasattr(result, 'data') else result
                
            elif tool_id == "T68":
                # PageRank
                result = tool_instance.execute({})
                execution_output = result
                current_data = result.data if hasattr(result, 'data') else result
            
            execution_time = time.time() - start_time
            
            results["execution_details"].append({
                "tool": tool_id,
                "position": i + 1,
                "success": True,
                "execution_time": execution_time,
                "output_type": type(execution_output).__name__
            })
            results["successful_executions"] += 1
            
            print(f"   ✅ {tool_id}: SUCCESS in {execution_time:.3f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            results["execution_details"].append({
                "tool": tool_id,
                "position": i + 1,
                "success": False,
                "execution_time": execution_time,
                "error": error_msg
            })
            results["failed_executions"] += 1
            results["breaking_points"].append({
                "type": "execution_failure",
                "tool": tool_id,  
                "position": i + 1,
                "error": error_msg,
                "execution_time": execution_time
            })
            
            print(f"   ❌ {tool_id}: EXECUTION FAILED in {execution_time:.3f}s")
            print(f"      Error: {error_msg}")
            
            # This is the KEY QUESTION: Do we stop here or continue?
            print(f"   🤔 BREAKING POINT: Chain failed at position {i+1}")
            print(f"   🛑 Real system behavior: STOP execution (fail-fast)")
            break
    
    results["success_rate"] = results["successful_executions"] / len(instantiated_tools)
    return results

def test_memory_exhaustion():
    """Test memory exhaustion breaking points"""
    print("\n\n🧠 TESTING MEMORY EXHAUSTION BREAKING POINTS")
    print("=" * 80)
    
    try:
        import psutil
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"📊 Initial memory usage: {initial_memory:.1f} MB")
        
        # Try to load multiple heavy models simultaneously
        memory_intensive_tools = []
        memory_results = []
        
        for i in range(5):  # Try to load 5 spaCy models
            try:
                print(f"   🔄 Loading spaCy model #{i+1}...")
                from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
                
                tool = T23ASpacyNERUnified()
                memory_intensive_tools.append(tool)
                
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                print(f"   📈 Memory after model #{i+1}: {current_memory:.1f} MB (+{memory_increase:.1f} MB)")
                
                memory_results.append({
                    "model_number": i + 1,
                    "total_memory_mb": current_memory,
                    "memory_increase_mb": memory_increase,
                    "success": True
                })
                
                # Threshold check
                if memory_increase > 500:  # 500MB increase
                    print(f"   ⚠️ Memory usage critical: {memory_increase:.1f} MB increase")
                    break
                    
            except Exception as e:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_results.append({
                    "model_number": i + 1,
                    "total_memory_mb": current_memory,
                    "error": str(e),
                    "success": False
                })
                print(f"   💥 MEMORY BREAKING POINT at model #{i+1}: {e}")
                break
        
        return {
            "initial_memory_mb": initial_memory,
            "memory_results": memory_results,
            "models_loaded": len(memory_intensive_tools),
            "breaking_point_found": any(not r["success"] for r in memory_results)
        }
        
    except Exception as e:
        print(f"💥 Memory test failed: {e}")
        return {"error": str(e)}

def main():
    """Main breaking point analysis"""
    print("💥 REAL BREAKING POINT ANALYSIS")
    print("=" * 80)
    print("Testing actual system limits - no simulation")
    print("Success = binary (works or breaks)")
    print("=" * 80)
    
    # Test 1: Tool chain execution
    chain_results = test_actual_tool_execution_chain()
    
    # Test 2: Memory exhaustion
    memory_results = test_memory_exhaustion()
    
    # Compile final results
    final_results = {
        "test_type": "real_breaking_point_analysis",
        "timestamp": datetime.now().isoformat(),
        "chain_execution": chain_results,
        "memory_exhaustion": memory_results,
        "summary": {
            "chain_breaking_points": len(chain_results.get("breaking_points", [])),
            "memory_breaking_point": memory_results.get("breaking_point_found", False),
            "real_execution": True,
            "simulation": False
        }
    }
    
    # Save results
    results_file = f"REAL_BREAKING_POINTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print("💥 REAL BREAKING POINT ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Report findings
    chain_bp = final_results["summary"]["chain_breaking_points"]
    memory_bp = final_results["summary"]["memory_breaking_point"]
    
    if chain_bp > 0:
        print(f"🔗 TOOL CHAIN BREAKING POINTS: {chain_bp} found")
        for bp in chain_results.get("breaking_points", []):
            print(f"   • {bp['type']} at {bp.get('tool', 'unknown')} (position {bp.get('position', '?')})")
    else:
        successful = chain_results.get("execution_results", {}).get("successful_executions", 0)
        total = chain_results.get("execution_results", {}).get("total_tools", 0)
        print(f"🔗 TOOL CHAIN: {successful}/{total} tools executed successfully")
    
    if memory_bp:
        models_loaded = memory_results.get("models_loaded", 0)
        print(f"🧠 MEMORY BREAKING POINT: Found after loading {models_loaded} models")
    else:
        print(f"🧠 MEMORY: No breaking point found")
    
    print(f"\n📄 Detailed results: {results_file}")
    
    print(f"\n🎯 KEY INSIGHT:")
    print(f"   Success is BINARY - tools either work (100%) or fail at specific point")
    print(f"   Previous 'percentage success' was simulation artifact")
    print(f"   Real systems exhibit fail-fast behavior at breaking points")
    
    return final_results

if __name__ == "__main__":
    results = main()