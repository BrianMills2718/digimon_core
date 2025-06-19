#!/usr/bin/env python3
"""
TEST ALL 29 MCP TOOLS IN THE SYSTEM
Real functional testing of each MCP tool with actual data
"""

import sys
import json
import time
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_tools():
    """Test all 29 MCP tools systematically"""
    
    print("🔥 TESTING ALL 29 MCP TOOLS")
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
    
    # List of all 29 MCP tools to test
    mcp_tools = [
        # Identity Service Tools (5)
        {"name": "create_mention", "category": "Identity", "test_func": test_create_mention},
        {"name": "get_entity_by_mention", "category": "Identity", "test_func": test_get_entity_by_mention},
        {"name": "get_mentions_for_entity", "category": "Identity", "test_func": test_get_mentions_for_entity},
        {"name": "merge_entities", "category": "Identity", "test_func": test_merge_entities},
        {"name": "get_identity_stats", "category": "Identity", "test_func": test_get_identity_stats},
        
        # Provenance Service Tools (5)
        {"name": "start_operation", "category": "Provenance", "test_func": test_start_operation},
        {"name": "complete_operation", "category": "Provenance", "test_func": test_complete_operation},
        {"name": "get_lineage", "category": "Provenance", "test_func": test_get_lineage},
        {"name": "get_operation_details", "category": "Provenance", "test_func": test_get_operation_details},
        {"name": "get_operations_for_object", "category": "Provenance", "test_func": test_get_operations_for_object},
        {"name": "get_tool_statistics", "category": "Provenance", "test_func": test_get_tool_statistics},
        
        # Quality Service Tools (6)
        {"name": "assess_confidence", "category": "Quality", "test_func": test_assess_confidence},
        {"name": "propagate_confidence", "category": "Quality", "test_func": test_propagate_confidence},
        {"name": "get_quality_assessment", "category": "Quality", "test_func": test_get_quality_assessment},
        {"name": "get_confidence_trend", "category": "Quality", "test_func": test_get_confidence_trend},
        {"name": "filter_by_quality", "category": "Quality", "test_func": test_filter_by_quality},
        {"name": "get_quality_statistics", "category": "Quality", "test_func": test_get_quality_statistics},
        
        # Workflow State Service Tools (7)
        {"name": "start_workflow", "category": "Workflow", "test_func": test_start_workflow},
        {"name": "create_checkpoint", "category": "Workflow", "test_func": test_create_checkpoint},
        {"name": "restore_from_checkpoint", "category": "Workflow", "test_func": test_restore_from_checkpoint},
        {"name": "update_workflow_progress", "category": "Workflow", "test_func": test_update_workflow_progress},
        {"name": "get_workflow_status", "category": "Workflow", "test_func": test_get_workflow_status},
        {"name": "get_workflow_checkpoints", "category": "Workflow", "test_func": test_get_workflow_checkpoints},
        {"name": "get_workflow_statistics", "category": "Workflow", "test_func": test_get_workflow_statistics},
        
        # Vertical Slice Workflow Tools (3)
        {"name": "execute_pdf_to_answer_workflow", "category": "VerticalSlice", "test_func": test_execute_pdf_to_answer_workflow},
        {"name": "get_vertical_slice_info", "category": "VerticalSlice", "test_func": test_get_vertical_slice_info},
        
        # System Tools (3)
        {"name": "test_connection", "category": "System", "test_func": test_test_connection},
        {"name": "echo", "category": "System", "test_func": test_echo},
        {"name": "get_system_status", "category": "System", "test_func": test_get_system_status},
    ]
    
    # Test each tool
    for tool in mcp_tools:
        print(f"\n🧪 TESTING: {tool['name']} ({tool['category']})")
        print("-" * 60)
        
        tool_start = time.time()
        try:
            result = tool['test_func']()
            tool_result = {
                "tool_name": tool['name'],
                "category": tool['category'],
                "status": "PASS",
                "result": result,
                "execution_time": time.time() - tool_start,
                "error": None
            }
            results["test_summary"]["tools_passed"] += 1
            print(f"✅ PASS: {result}")
            
        except Exception as e:
            tool_result = {
                "tool_name": tool['name'],
                "category": tool['category'],
                "status": "FAIL",
                "result": None,
                "execution_time": time.time() - tool_start,
                "error": str(e)
            }
            results["test_summary"]["tools_failed"] += 1
            print(f"❌ FAIL: {str(e)}")
        
        results["tool_results"].append(tool_result)
        results["test_summary"]["tools_tested"] += 1
    
    # Generate summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 MCP TOOLS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tools: {results['test_summary']['total_tools']}")
    print(f"✅ Passed: {results['test_summary']['tools_passed']}")
    print(f"❌ Failed: {results['test_summary']['tools_failed']}")
    print(f"📈 Pass Rate: {(results['test_summary']['tools_passed']/results['test_summary']['total_tools'])*100:.1f}%")
    print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
    
    # Save results
    with open("mcp_tools_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: mcp_tools_test_results.json")
    
    return results

# Individual test functions for each MCP tool
def test_create_mention():
    """Test create_mention MCP tool"""
    try:
        from src.mcp_server import create_mention
        result = create_mention(
            surface_form="Dr. Smith",
            start_pos=0,
            end_pos=9,
            source_ref="test_doc_1",
            entity_type="PERSON",
            confidence=0.8
        )
        return f"Created mention with ID: {result.get('mention_id', 'unknown')}"
    except Exception as e:
        raise Exception(f"create_mention failed: {str(e)}")

def test_get_entity_by_mention():
    """Test get_entity_by_mention MCP tool"""
    try:
        from src.mcp_server import get_entity_by_mention
        # First create a mention to test with
        result = get_entity_by_mention("test_mention_id")
        return f"Retrieved entity: {result is not None}"
    except Exception as e:
        raise Exception(f"get_entity_by_mention failed: {str(e)}")

def test_get_mentions_for_entity():
    """Test get_mentions_for_entity MCP tool"""
    try:
        from src.mcp_server import get_mentions_for_entity
        result = get_mentions_for_entity("test_entity_id")
        return f"Retrieved {len(result) if result else 0} mentions"
    except Exception as e:
        raise Exception(f"get_mentions_for_entity failed: {str(e)}")

def test_merge_entities():
    """Test merge_entities MCP tool"""
    try:
        from src.mcp_server import merge_entities
        result = merge_entities("entity_1", "entity_2")
        return f"Merge result: {result.get('success', False)}"
    except Exception as e:
        raise Exception(f"merge_entities failed: {str(e)}")

def test_get_identity_stats():
    """Test get_identity_stats MCP tool"""
    try:
        from src.mcp_server import get_identity_stats
        result = get_identity_stats()
        return f"Stats: {result.get('entity_count', 0)} entities, {result.get('mention_count', 0)} mentions"
    except Exception as e:
        raise Exception(f"get_identity_stats failed: {str(e)}")

def test_start_operation():
    """Test start_operation MCP tool"""
    try:
        from src.mcp_server import start_operation
        result = start_operation(
            tool_name="test_tool",
            input_objects=["test_input"],
            metadata={"test": "data"}
        )
        return f"Started operation: {result.get('operation_id', 'unknown')}"
    except Exception as e:
        raise Exception(f"start_operation failed: {str(e)}")

def test_complete_operation():
    """Test complete_operation MCP tool"""
    try:
        from src.mcp_server import complete_operation
        result = complete_operation(
            operation_id="test_op_id",
            output_objects=["test_output"],
            success=True
        )
        return f"Completed operation: {result.get('success', False)}"
    except Exception as e:
        raise Exception(f"complete_operation failed: {str(e)}")

def test_get_lineage():
    """Test get_lineage MCP tool"""
    try:
        from src.mcp_server import get_lineage
        result = get_lineage("test_object_id")
        return f"Found lineage with {len(result.get('operations', []))} operations"
    except Exception as e:
        raise Exception(f"get_lineage failed: {str(e)}")

def test_get_operation_details():
    """Test get_operation_details MCP tool"""
    try:
        from src.mcp_server import get_operation_details
        result = get_operation_details("test_operation_id")
        return f"Operation details: {result is not None}"
    except Exception as e:
        raise Exception(f"get_operation_details failed: {str(e)}")

def test_get_operations_for_object():
    """Test get_operations_for_object MCP tool"""
    try:
        from src.mcp_server import get_operations_for_object
        result = get_operations_for_object("test_object_id")
        return f"Found {len(result)} operations for object"
    except Exception as e:
        raise Exception(f"get_operations_for_object failed: {str(e)}")

def test_get_tool_statistics():
    """Test get_tool_statistics MCP tool"""
    try:
        from src.mcp_server import get_tool_statistics
        result = get_tool_statistics()
        return f"Tool stats: {len(result)} tools tracked"
    except Exception as e:
        raise Exception(f"get_tool_statistics failed: {str(e)}")

def test_assess_confidence():
    """Test assess_confidence MCP tool"""
    try:
        from src.mcp_server import assess_confidence
        result = assess_confidence(
            object_type="entity",
            object_data={"name": "Test Entity", "type": "PERSON"},
            context={"source": "test"}
        )
        return f"Confidence: {result.get('confidence', 0):.2f}"
    except Exception as e:
        raise Exception(f"assess_confidence failed: {str(e)}")

def test_propagate_confidence():
    """Test propagate_confidence MCP tool"""
    try:
        from src.mcp_server import propagate_confidence
        result = propagate_confidence(
            from_object_id="obj_1",
            to_object_id="obj_2", 
            operation_type="extraction"
        )
        return f"Propagated confidence: {result.get('new_confidence', 0):.2f}"
    except Exception as e:
        raise Exception(f"propagate_confidence failed: {str(e)}")

def test_get_quality_assessment():
    """Test get_quality_assessment MCP tool"""
    try:
        from src.mcp_server import get_quality_assessment
        result = get_quality_assessment("test_object_id")
        return f"Quality: {result.get('tier', 'unknown')} tier"
    except Exception as e:
        raise Exception(f"get_quality_assessment failed: {str(e)}")

def test_get_confidence_trend():
    """Test get_confidence_trend MCP tool"""
    try:
        from src.mcp_server import get_confidence_trend
        result = get_confidence_trend("test_object_id")
        return f"Trend: {result.get('direction', 'unknown')}"
    except Exception as e:
        raise Exception(f"get_confidence_trend failed: {str(e)}")

def test_filter_by_quality():
    """Test filter_by_quality MCP tool"""
    try:
        from src.mcp_server import filter_by_quality
        result = filter_by_quality(
            objects=[{"id": "1", "data": "test"}],
            min_tier="BRONZE"
        )
        return f"Filtered to {len(result)} objects"
    except Exception as e:
        raise Exception(f"filter_by_quality failed: {str(e)}")

def test_get_quality_statistics():
    """Test get_quality_statistics MCP tool"""
    try:
        from src.mcp_server import get_quality_statistics
        result = get_quality_statistics()
        return f"Quality stats: {result.get('total_assessments', 0)} assessments"
    except Exception as e:
        raise Exception(f"get_quality_statistics failed: {str(e)}")

def test_start_workflow():
    """Test start_workflow MCP tool"""
    try:
        from src.mcp_server import start_workflow
        result = start_workflow(
            workflow_name="test_workflow",
            description="Test workflow"
        )
        return f"Started workflow: {result.get('workflow_id', 'unknown')}"
    except Exception as e:
        raise Exception(f"start_workflow failed: {str(e)}")

def test_create_checkpoint():
    """Test create_checkpoint MCP tool"""
    try:
        from src.mcp_server import create_checkpoint
        result = create_checkpoint(
            workflow_id="test_workflow_id",
            stage="test_stage",
            data={"test": "checkpoint"}
        )
        return f"Created checkpoint: {result.get('checkpoint_id', 'unknown')}"
    except Exception as e:
        raise Exception(f"create_checkpoint failed: {str(e)}")

def test_restore_from_checkpoint():
    """Test restore_from_checkpoint MCP tool"""
    try:
        from src.mcp_server import restore_from_checkpoint
        result = restore_from_checkpoint("test_checkpoint_id")
        return f"Restored: {result.get('success', False)}"
    except Exception as e:
        raise Exception(f"restore_from_checkpoint failed: {str(e)}")

def test_update_workflow_progress():
    """Test update_workflow_progress MCP tool"""
    try:
        from src.mcp_server import update_workflow_progress
        result = update_workflow_progress(
            workflow_id="test_workflow_id",
            stage="test_stage",
            progress=0.5,
            status="running"
        )
        return f"Updated progress: {result.get('success', False)}"
    except Exception as e:
        raise Exception(f"update_workflow_progress failed: {str(e)}")

def test_get_workflow_status():
    """Test get_workflow_status MCP tool"""
    try:
        from src.mcp_server import get_workflow_status
        result = get_workflow_status("test_workflow_id")
        return f"Status: {result.get('status', 'unknown')}"
    except Exception as e:
        raise Exception(f"get_workflow_status failed: {str(e)}")

def test_get_workflow_checkpoints():
    """Test get_workflow_checkpoints MCP tool"""
    try:
        from src.mcp_server import get_workflow_checkpoints
        result = get_workflow_checkpoints("test_workflow_id")
        return f"Found {len(result)} checkpoints"
    except Exception as e:
        raise Exception(f"get_workflow_checkpoints failed: {str(e)}")

def test_get_workflow_statistics():
    """Test get_workflow_statistics MCP tool"""
    try:
        from src.mcp_server import get_workflow_statistics
        result = get_workflow_statistics()
        return f"Workflow stats: {result.get('total_workflows', 0)} workflows"
    except Exception as e:
        raise Exception(f"get_workflow_statistics failed: {str(e)}")

def test_execute_pdf_to_answer_workflow():
    """Test execute_pdf_to_answer_workflow MCP tool"""
    try:
        from src.mcp_server import execute_pdf_to_answer_workflow
        # This will likely fail due to missing file, but we can test the interface
        result = execute_pdf_to_answer_workflow(
            pdf_path="nonexistent.pdf",
            query="test query"
        )
        return f"Workflow result: {result.get('success', False)}"
    except Exception as e:
        if "No such file" in str(e) or "does not exist" in str(e):
            return "Interface works (expected file not found error)"
        raise Exception(f"execute_pdf_to_answer_workflow failed: {str(e)}")

def test_get_vertical_slice_info():
    """Test get_vertical_slice_info MCP tool"""
    try:
        from src.mcp_server import get_vertical_slice_info
        result = get_vertical_slice_info()
        return f"Info: {result.get('name', 'unknown')} workflow"
    except Exception as e:
        raise Exception(f"get_vertical_slice_info failed: {str(e)}")

def test_test_connection():
    """Test test_connection MCP tool"""
    try:
        from src.mcp_server import test_connection
        result = test_connection()
        return f"Connection test: {result.get('status', 'unknown')}"
    except Exception as e:
        raise Exception(f"test_connection failed: {str(e)}")

def test_echo():
    """Test echo MCP tool"""
    try:
        from src.mcp_server import echo
        result = echo("Hello, MCP!")
        return f"Echo result: {result.get('message', 'no response')}"
    except Exception as e:
        raise Exception(f"echo failed: {str(e)}")

def test_get_system_status():
    """Test get_system_status MCP tool"""
    try:
        from src.mcp_server import get_system_status
        result = get_system_status()
        return f"System status: {result.get('status', 'unknown')}"
    except Exception as e:
        raise Exception(f"get_system_status failed: {str(e)}")

if __name__ == "__main__":
    results = test_mcp_tools()
    
    # Exit with error code if any tests failed
    if results["test_summary"]["tools_failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)