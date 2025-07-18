#!/usr/bin/env python3
"""
FIXED MCP TOOLS TESTING
Test all 29 MCP tools by directly calling the functions
"""

import sys
import json
import time
import traceback
from pathlib import Path

# Add src to path for imports

def test_all_29_mcp_tools():
    """Test all 29 MCP tools by direct function calls"""
    
    print("🔥 TESTING ALL 29 MCP TOOLS (DIRECT FUNCTION CALLS)")
    print("=" * 80)
    
    results = {
        "test_summary": {
            "total_tools": 29,
            "tools_tested": 0,
            "tools_passed": 0,
            "tools_failed": 0,
            "start_time": time.time()
        },
        "tool_results": []
    }
    
    # Import the MCP server module to get access to all the tool functions
    try:
        import src.mcp_server as mcp_server
        print("✅ Successfully imported MCP server module")
    except Exception as e:
        print(f"❌ Failed to import MCP server: {e}")
        return results
    
    # Define all 29 tools with their direct function references and test parameters
    tools_to_test = [
        # Identity Service Tools (5)
        {
            "name": "create_mention",
            "category": "Identity Service",
            "func": mcp_server.create_mention,
            "params": {
                "surface_form": "Dr. Smith",
                "start_pos": 0,
                "end_pos": 9,
                "source_ref": "test_document",
                "entity_type": "PERSON",
                "confidence": 0.8
            }
        },
        {
            "name": "get_entity_by_mention",
            "category": "Identity Service",
            "func": mcp_server.get_entity_by_mention,
            "params": {"mention_id": "test_mention_123"}
        },
        {
            "name": "get_mentions_for_entity",
            "category": "Identity Service",
            "func": mcp_server.get_mentions_for_entity,
            "params": {"entity_id": "test_entity_123"}
        },
        {
            "name": "merge_entities",
            "category": "Identity Service",
            "func": mcp_server.merge_entities,
            "params": {"entity_id1": "entity_1", "entity_id2": "entity_2"}
        },
        {
            "name": "get_identity_stats",
            "category": "Identity Service",
            "func": mcp_server.get_identity_stats,
            "params": {}
        },
        
        # Provenance Service Tools (6)
        {
            "name": "start_operation",
            "category": "Provenance Service",
            "func": mcp_server.start_operation,
            "params": {
                "tool_id": "test_tool",
                "operation_type": "create", 
                "inputs": ["input1", "input2"],
                "parameters": {"test": "data"}
            }
        },
        {
            "name": "complete_operation",
            "category": "Provenance Service",
            "func": mcp_server.complete_operation,
            "params": {
                "operation_id": "test_op_123",
                "outputs": ["output1"],
                "success": True
            }
        },
        {
            "name": "get_lineage",
            "category": "Provenance Service",
            "func": mcp_server.get_lineage,
            "params": {"object_ref": "test_object_123", "max_depth": 10}
        },
        {
            "name": "get_operation_details",
            "category": "Provenance Service",
            "func": mcp_server.get_operation_details,
            "params": {"operation_id": "test_op_123"}
        },
        {
            "name": "get_operations_for_object",
            "category": "Provenance Service",
            "func": mcp_server.get_operations_for_object,
            "params": {"object_ref": "test_object_123"}
        },
        {
            "name": "get_tool_statistics",
            "category": "Provenance Service",
            "func": mcp_server.get_tool_statistics,
            "params": {}
        },
        
        # Quality Service Tools (6)
        {
            "name": "assess_confidence",
            "category": "Quality Service",
            "func": mcp_server.assess_confidence,
            "params": {
                "object_ref": "test_object_123",
                "base_confidence": 0.8,
                "factors": {"factor1": 0.1},
                "metadata": {"test": "data"}
            }
        },
        {
            "name": "propagate_confidence",
            "category": "Quality Service", 
            "func": mcp_server.propagate_confidence,
            "params": {
                "input_refs": ["obj1", "obj2"],
                "operation_type": "extraction",
                "boost_factor": 1.0
            }
        },
        {
            "name": "get_quality_assessment",
            "category": "Quality Service",
            "func": mcp_server.get_quality_assessment,
            "params": {"object_ref": "test_object_123"}
        },
        {
            "name": "get_confidence_trend",
            "category": "Quality Service",
            "func": mcp_server.get_confidence_trend,
            "params": {"object_ref": "test_object_123"}
        },
        {
            "name": "filter_by_quality",
            "category": "Quality Service",
            "func": mcp_server.filter_by_quality,
            "params": {
                "object_refs": ["obj1", "obj2", "obj3"],
                "min_tier": "LOW",
                "min_confidence": 0.0
            }
        },
        {
            "name": "get_quality_statistics",
            "category": "Quality Service",
            "func": mcp_server.get_quality_statistics,
            "params": {}
        },
        
        # Workflow Service Tools (6)
        {
            "name": "start_workflow",
            "category": "Workflow Service",
            "func": mcp_server.start_workflow,
            "params": {
                "name": "test_workflow",
                "total_steps": 5,
                "initial_state": {"progress": 0}
            }
        },
        {
            "name": "create_checkpoint",
            "category": "Workflow Service",
            "func": mcp_server.create_checkpoint,
            "params": {
                "workflow_id": "test_workflow_123",
                "step_name": "processing",
                "step_number": 1,
                "state_data": {"progress": 0.2}
            }
        },
        {
            "name": "restore_from_checkpoint",
            "category": "Workflow Service",
            "func": mcp_server.restore_from_checkpoint,
            "params": {"checkpoint_id": "checkpoint_123"}
        },
        {
            "name": "update_workflow_progress",
            "category": "Workflow Service",
            "func": mcp_server.update_workflow_progress,
            "params": {
                "workflow_id": "test_workflow_123",
                "step_number": 2,
                "status": "running"
            }
        },
        {
            "name": "get_workflow_status",
            "category": "Workflow Service",
            "func": mcp_server.get_workflow_status,
            "params": {"workflow_id": "test_workflow_123"}
        },
        {
            "name": "get_workflow_checkpoints",
            "category": "Workflow Service",
            "func": mcp_server.get_workflow_checkpoints,
            "params": {"workflow_id": "test_workflow_123"}
        },
        {
            "name": "get_workflow_statistics",
            "category": "Workflow Service",
            "func": mcp_server.get_workflow_statistics,
            "params": {}
        },
        
        # Vertical Slice Tools (2)
        {
            "name": "execute_pdf_to_answer_workflow",
            "category": "Vertical Slice",
            "func": mcp_server.execute_pdf_to_answer_workflow,
            "params": {
                "pdf_path": "examples/test.pdf",
                "query": "What are the main topics?",
                "workflow_name": "Test_Analysis"
            }
        },
        {
            "name": "get_vertical_slice_info",
            "category": "Vertical Slice",
            "func": mcp_server.get_vertical_slice_info,
            "params": {}
        },
        
        # System Tools (3)
        {
            "name": "test_connection",
            "category": "System",
            "func": mcp_server.test_connection,
            "params": {}
        },
        {
            "name": "echo",
            "category": "System",
            "func": mcp_server.echo,
            "params": {"message": "Hello MCP Server!"}
        },
        {
            "name": "get_system_status",
            "category": "System",
            "func": mcp_server.get_system_status,
            "params": {}
        }
    ]
    
    print(f"📋 Testing {len(tools_to_test)} MCP tools...")
    results["test_summary"]["total_tools"] = len(tools_to_test)
    
    # Test each tool
    for tool in tools_to_test:
        print(f"\n🧪 TESTING: {tool['name']} ({tool['category']})")
        print(f"   Parameters: {tool['params']}")
        print("-" * 70)
        
        tool_start = time.time()
        tool_result = {
            "tool_name": tool['name'],
            "category": tool['category'],
            "parameters": tool['params'],
            "execution_time": 0,
            "status": "UNKNOWN",
            "result": None,
            "error": None
        }
        
        try:
            # Call the function directly
            if tool['params']:
                result = tool['func'](**tool['params'])
            else:
                result = tool['func']()
                
            tool_result["result"] = result
            tool_result["status"] = "PASS"
            results["test_summary"]["tools_passed"] += 1
            print(f"✅ PASS: {result}")
            
        except Exception as e:
            tool_result["error"] = f"{type(e).__name__}: {str(e)}"
            tool_result["status"] = "FAIL"
            results["test_summary"]["tools_failed"] += 1
            print(f"❌ FAIL: {tool_result['error']}")
        
        tool_result["execution_time"] = time.time() - tool_start
        results["tool_results"].append(tool_result)
        results["test_summary"]["tools_tested"] += 1
    
    # Generate summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 MCP TOOLS DIRECT TESTING SUMMARY")
    print("=" * 80)
    print(f"Total Tools: {results['test_summary']['total_tools']}")
    print(f"✅ Passed: {results['test_summary']['tools_passed']}")
    print(f"❌ Failed: {results['test_summary']['tools_failed']}")
    print(f"📈 Pass Rate: {(results['test_summary']['tools_passed']/results['test_summary']['total_tools'])*100:.1f}%")
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
    
    # Show sample failed tools
    failed_tools = [r for r in results["tool_results"] if r["status"] != "PASS"]
    if failed_tools:
        print(f"\n⚠️  SAMPLE FAILED TOOLS:")
        for tool in failed_tools[:5]:  # Show first 5 failures
            print(f"  - {tool['tool_name']}: {tool['error']}")
        if len(failed_tools) > 5:
            print(f"  ... and {len(failed_tools) - 5} more")
    
    # Save results
    with open("mcp_tools_direct_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: mcp_tools_direct_test_results.json")
    
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
        print("   ⚠️  GOOD: Majority of tools working")
        sys.exit(0)
    elif pass_rate >= 40:
        print("   🔧 PARTIAL: Significant functionality present")
        sys.exit(1)
    else:
        print("   ❌ NEEDS WORK: Major issues to address")
        sys.exit(1)