#!/usr/bin/env python3
"""
COMPLETE MCP TOOLS TESTING
Test all 29 MCP tools from the full super-digimon server

This test systematically validates all tools by:
1. Testing import capability
2. Testing method signatures 
3. Testing realistic function calls
4. Documenting expected behavior vs actual results
"""

import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports

def test_all_29_mcp_tools():
    """Test all 29 MCP tools systematically"""
    
    print("🔥 TESTING ALL 29 MCP TOOLS FROM FULL SERVER")
    print("=" * 80)
    
    results = {
        "test_summary": {
            "total_tools": 29,
            "tools_tested": 0,
            "tools_passed": 0,
            "tools_failed": 0,
            "import_successful": 0,
            "function_callable": 0,
            "start_time": time.time()
        },
        "tool_results": []
    }
    
    # Import the full MCP server and get the tools
    try:
        from src.mcp_server import mcp
        print("✅ Successfully imported full MCP server")
        results["test_summary"]["import_successful"] = 1
    except Exception as e:
        print(f"❌ Failed to import MCP server: {e}")
        return results
    
    # Get all registered tools from the MCP server
    try:
        # Access the tools registry from FastMCP
        tools_registry = mcp._tools
        print(f"📊 Found {len(tools_registry)} registered tools in MCP server")
        
        if len(tools_registry) != 29:
            print(f"⚠️  Expected 29 tools, found {len(tools_registry)}")
            
    except Exception as e:
        print(f"❌ Could not access tools registry: {e}")
        return results
    
    # Define expected tools with categories and test parameters
    expected_tools = {
        # Identity Service Tools (5)
        "create_mention": {
            "category": "Identity Service",
            "params": {
                "surface_form": "Dr. Smith",
                "start_pos": 0,
                "end_pos": 9,
                "source_ref": "test_document",
                "entity_type": "PERSON",
                "confidence": 0.8
            },
            "expected": "creates mention and returns mention data"
        },
        "get_entity_by_mention": {
            "category": "Identity Service", 
            "params": {"mention_id": "test_mention_123"},
            "expected": "returns entity data or None"
        },
        "get_mentions_for_entity": {
            "category": "Identity Service",
            "params": {"entity_id": "test_entity_123"}, 
            "expected": "returns list of mentions"
        },
        "merge_entities": {
            "category": "Identity Service",
            "params": {"entity_id1": "entity_1", "entity_id2": "entity_2"},
            "expected": "merges entities and returns result"
        },
        "get_identity_stats": {
            "category": "Identity Service",
            "params": {},
            "expected": "returns identity service statistics"
        },
        
        # Provenance Service Tools (6)
        "start_operation": {
            "category": "Provenance Service",
            "params": {
                "tool_id": "test_tool",
                "operation_type": "create",
                "inputs": ["input1", "input2"],
                "parameters": {"test": "data"}
            },
            "expected": "returns operation ID"
        },
        "complete_operation": {
            "category": "Provenance Service",
            "params": {
                "operation_id": "test_op_123",
                "outputs": ["output1"],
                "success": True
            },
            "expected": "completes operation and returns result"
        },
        "get_lineage": {
            "category": "Provenance Service",
            "params": {"object_ref": "test_object_123", "max_depth": 10},
            "expected": "returns lineage chain"
        },
        "get_operation_details": {
            "category": "Provenance Service",
            "params": {"operation_id": "test_op_123"},
            "expected": "returns operation details or None"
        },
        "get_operations_for_object": {
            "category": "Provenance Service",
            "params": {"object_ref": "test_object_123"},
            "expected": "returns list of operations"
        },
        "get_tool_statistics": {
            "category": "Provenance Service",
            "params": {},
            "expected": "returns tool usage statistics"
        },
        
        # Quality Service Tools (6)
        "assess_confidence": {
            "category": "Quality Service",
            "params": {
                "object_ref": "test_object_123",
                "base_confidence": 0.8,
                "factors": {"factor1": 0.1},
                "metadata": {"test": "data"}
            },
            "expected": "assesses and returns confidence data"
        },
        "propagate_confidence": {
            "category": "Quality Service",
            "params": {
                "input_refs": ["obj1", "obj2"],
                "operation_type": "extraction",
                "boost_factor": 1.0
            },
            "expected": "returns propagated confidence score"
        },
        "get_quality_assessment": {
            "category": "Quality Service",
            "params": {"object_ref": "test_object_123"},
            "expected": "returns quality assessment or None"
        },
        "get_confidence_trend": {
            "category": "Quality Service",
            "params": {"object_ref": "test_object_123"},
            "expected": "returns confidence trend data"
        },
        "filter_by_quality": {
            "category": "Quality Service",
            "params": {
                "object_refs": ["obj1", "obj2", "obj3"],
                "min_tier": "LOW",
                "min_confidence": 0.0
            },
            "expected": "returns filtered object list"
        },
        "get_quality_statistics": {
            "category": "Quality Service",
            "params": {},
            "expected": "returns quality service statistics"
        },
        
        # Workflow Service Tools (6)
        "start_workflow": {
            "category": "Workflow Service",
            "params": {
                "name": "test_workflow",
                "total_steps": 5,
                "initial_state": {"progress": 0}
            },
            "expected": "returns workflow ID"
        },
        "create_checkpoint": {
            "category": "Workflow Service",
            "params": {
                "workflow_id": "test_workflow_123",
                "step_name": "processing",
                "step_number": 1,
                "state_data": {"progress": 0.2}
            },
            "expected": "creates checkpoint and returns checkpoint ID"
        },
        "restore_from_checkpoint": {
            "category": "Workflow Service",
            "params": {"checkpoint_id": "checkpoint_123"},
            "expected": "restores and returns workflow state"
        },
        "update_workflow_progress": {
            "category": "Workflow Service",
            "params": {
                "workflow_id": "test_workflow_123",
                "step_number": 2,
                "status": "running"
            },
            "expected": "updates and returns workflow status"
        },
        "get_workflow_status": {
            "category": "Workflow Service",
            "params": {"workflow_id": "test_workflow_123"},
            "expected": "returns workflow status or None"
        },
        "get_workflow_checkpoints": {
            "category": "Workflow Service",
            "params": {"workflow_id": "test_workflow_123"},
            "expected": "returns list of checkpoints"
        },
        "get_workflow_statistics": {
            "category": "Workflow Service",
            "params": {},
            "expected": "returns workflow service statistics"
        },
        
        # Vertical Slice Tools (2)
        "execute_pdf_to_answer_workflow": {
            "category": "Vertical Slice",
            "params": {
                "pdf_path": "examples/test.pdf",
                "query": "What are the main topics?",
                "workflow_name": "Test_Analysis"
            },
            "expected": "executes PDF workflow and returns results"
        },
        "get_vertical_slice_info": {
            "category": "Vertical Slice",
            "params": {},
            "expected": "returns vertical slice workflow info"
        },
        
        # System Tools (3)
        "test_connection": {
            "category": "System",
            "params": {},
            "expected": "returns connection success message"
        },
        "echo": {
            "category": "System", 
            "params": {"message": "Hello MCP Server!"},
            "expected": "echoes back the message"
        },
        "get_system_status": {
            "category": "System",
            "params": {},
            "expected": "returns system status information"
        }
    }
    
    print(f"📋 Testing {len(expected_tools)} expected tools...")
    results["test_summary"]["total_tools"] = len(expected_tools)
    
    # Test each tool
    for tool_name, tool_info in expected_tools.items():
        print(f"\n🧪 TESTING: {tool_name} ({tool_info['category']})")
        print(f"   Parameters: {tool_info['params']}")
        print(f"   Expected: {tool_info['expected']}")
        print("-" * 70)
        
        tool_start = time.time()
        tool_result = {
            "tool_name": tool_name,
            "category": tool_info['category'],
            "parameters": tool_info['params'],
            "expected": tool_info['expected'],
            "execution_time": 0,
            "status": "UNKNOWN",
            "result": None,
            "error": None,
            "found_in_registry": False,
            "callable": False
        }
        
        try:
            # Check if tool exists in registry
            if tool_name in tools_registry:
                tool_result["found_in_registry"] = True
                tool_func = tools_registry[tool_name].func
                tool_result["callable"] = callable(tool_func)
                
                if tool_result["callable"]:
                    results["test_summary"]["function_callable"] += 1
                    
                    # Try to call the function with test parameters
                    try:
                        if tool_info['params']:
                            result = tool_func(**tool_info['params'])
                        else:
                            result = tool_func()
                            
                        tool_result["result"] = result
                        tool_result["status"] = "PASS"
                        results["test_summary"]["tools_passed"] += 1
                        print(f"✅ PASS: {result}")
                        
                    except Exception as call_error:
                        tool_result["error"] = str(call_error)
                        tool_result["status"] = "CALL_FAILED"
                        results["test_summary"]["tools_failed"] += 1
                        print(f"⚠️  CALL_FAILED: {call_error}")
                else:
                    tool_result["error"] = "Function not callable"
                    tool_result["status"] = "NOT_CALLABLE"
                    results["test_summary"]["tools_failed"] += 1
                    print(f"❌ NOT_CALLABLE: Function exists but not callable")
            else:
                tool_result["error"] = "Tool not found in registry"
                tool_result["status"] = "NOT_FOUND"
                results["test_summary"]["tools_failed"] += 1
                print(f"❌ NOT_FOUND: Tool not in registry")
                
        except Exception as e:
            tool_result["error"] = f"Test error: {str(e)}\n{traceback.format_exc()}"
            tool_result["status"] = "TEST_ERROR"
            results["test_summary"]["tools_failed"] += 1
            print(f"💥 TEST_ERROR: {e}")
        
        tool_result["execution_time"] = time.time() - tool_start
        results["tool_results"].append(tool_result)
        results["test_summary"]["tools_tested"] += 1
    
    # Generate summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 COMPLETE MCP TOOLS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Expected Tools: {results['test_summary']['total_tools']}")
    print(f"✅ Passed: {results['test_summary']['tools_passed']}")
    print(f"❌ Failed: {results['test_summary']['tools_failed']}")
    print(f"📈 Pass Rate: {(results['test_summary']['tools_passed']/results['test_summary']['total_tools'])*100:.1f}%")
    print(f"🔧 Found in Registry: {sum(1 for r in results['tool_results'] if r['found_in_registry'])}")
    print(f"📞 Callable Functions: {results['test_summary']['function_callable']}")
    print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
    
    # Detailed breakdown by category
    categories = {}
    for result in results["tool_results"]:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "failed": 0}
        categories[cat]["total"] += 1
        if result["status"] == "PASS":
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    print(f"\n📋 BREAKDOWN BY CATEGORY:")
    for cat, stats in categories.items():
        pass_rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
    
    # Show failed tools
    failed_tools = [r for r in results["tool_results"] if r["status"] != "PASS"]
    if failed_tools:
        print(f"\n⚠️  FAILED TOOLS ({len(failed_tools)}):")
        for tool in failed_tools:
            print(f"  - {tool['tool_name']}: {tool['status']} - {tool['error']}")
    
    # Save results
    with open("complete_mcp_tools_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: complete_mcp_tools_test_results.json")
    
    return results

if __name__ == "__main__":
    results = test_all_29_mcp_tools()
    
    # Determine success
    total_tools = results["test_summary"]["total_tools"]
    tools_passed = results["test_summary"]["tools_passed"]
    pass_rate = (tools_passed / total_tools) * 100 if total_tools > 0 else 0
    
    print(f"\n🎯 FINAL CONCLUSION:")
    print(f"   {tools_passed}/{total_tools} MCP tools working ({pass_rate:.1f}% pass rate)")
    
    if pass_rate >= 80:
        print("   🎉 EXCELLENT: Most tools are functional")
        sys.exit(0)
    elif pass_rate >= 60:
        print("   ⚠️  GOOD: Majority of tools working, some issues to address")
        sys.exit(0)
    elif pass_rate >= 40:
        print("   🔧 PARTIAL: Significant functionality present, integration work needed")
        sys.exit(1)
    else:
        print("   ❌ CRITICAL: Major issues preventing tool functionality")
        sys.exit(1)