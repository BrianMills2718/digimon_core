#!/usr/bin/env python3
"""
DIRECT MCP TOOLS TESTING VIA PROTOCOL
Test all 29 MCP tools by directly calling them through the MCP server protocol
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add src to path

# Import MCP client libraries
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("ERROR: MCP client library not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

async def test_all_29_mcp_tools():
    """Test all 29 MCP tools via direct protocol calls"""
    
    print("🔥 DIRECT MCP TOOLS TESTING VIA PROTOCOL")
    print("=" * 80)
    print(f"Start Time: {datetime.now()}")
    print("=" * 80)
    
    results = {
        "test_metadata": {
            "test_type": "Direct MCP Protocol Testing",
            "start_time": time.time(),
            "mcp_server": "src/mcp_server.py"
        },
        "summary": {
            "total_tools": 29,
            "tools_passed": 0,
            "tools_failed": 0,
            "tools_not_tested": 0
        },
        "tool_results": [],
        "raw_logs": []
    }
    
    # Define all 29 MCP tools with test parameters
    mcp_tools = [
        # Identity Service Tools (5)
        {
            "name": "create_mention",
            "category": "Identity Service",
            "params": {
                "surface_form": "Dr. John Smith",
                "start_pos": 0,
                "end_pos": 14,
                "source_ref": "test_document.pdf",
                "entity_type": "PERSON",
                "confidence": 0.95
            }
        },
        {
            "name": "get_entity_by_mention",
            "category": "Identity Service",
            "params": {"mention_id": "mention_test_12345"}
        },
        {
            "name": "get_mentions_for_entity",
            "category": "Identity Service",
            "params": {"entity_id": "entity_test_67890"}
        },
        {
            "name": "merge_entities",
            "category": "Identity Service",
            "params": {"entity_id1": "entity_001", "entity_id2": "entity_002"}
        },
        {
            "name": "get_identity_stats",
            "category": "Identity Service",
            "params": {}
        },
        
        # Provenance Service Tools (6)
        {
            "name": "start_operation",
            "category": "Provenance Service",
            "params": {
                "tool_id": "test_tool",
                "operation_type": "create",
                "inputs": ["input1.pdf", "input2.pdf"],
                "parameters": {"model": "gpt-4", "temperature": 0.7}
            }
        },
        {
            "name": "complete_operation",
            "category": "Provenance Service",
            "params": {
                "operation_id": "op_test_123",
                "outputs": ["result1", "result2"],
                "success": True,
                "metadata": {"duration": 5.2}
            }
        },
        {
            "name": "get_lineage",
            "category": "Provenance Service",
            "params": {"object_ref": "doc_12345", "max_depth": 5}
        },
        {
            "name": "get_operation_details",
            "category": "Provenance Service",
            "params": {"operation_id": "op_test_123"}
        },
        {
            "name": "get_operations_for_object",
            "category": "Provenance Service",
            "params": {"object_ref": "doc_12345"}
        },
        {
            "name": "get_tool_statistics",
            "category": "Provenance Service",
            "params": {}
        },
        
        # Quality Service Tools (6)
        {
            "name": "assess_confidence",
            "category": "Quality Service",
            "params": {
                "object_ref": "entity_12345",
                "base_confidence": 0.85,
                "factors": {"source_quality": 0.9, "extraction_method": 0.8},
                "metadata": {"assessed_by": "test_run"}
            }
        },
        {
            "name": "propagate_confidence",
            "category": "Quality Service",
            "params": {
                "input_refs": ["entity_001", "entity_002", "entity_003"],
                "operation_type": "merge",
                "boost_factor": 1.1
            }
        },
        {
            "name": "get_quality_assessment",
            "category": "Quality Service",
            "params": {"object_ref": "entity_12345"}
        },
        {
            "name": "get_confidence_trend",
            "category": "Quality Service",
            "params": {"object_ref": "entity_12345"}
        },
        {
            "name": "filter_by_quality",
            "category": "Quality Service",
            "params": {
                "object_refs": ["obj1", "obj2", "obj3", "obj4", "obj5"],
                "min_tier": "MEDIUM",
                "min_confidence": 0.7
            }
        },
        {
            "name": "get_quality_statistics",
            "category": "Quality Service",
            "params": {}
        },
        
        # Workflow Service Tools (7)
        {
            "name": "start_workflow",
            "category": "Workflow Service",
            "params": {
                "name": "Test_Workflow_Run",
                "total_steps": 10,
                "initial_state": {"stage": "initialization", "progress": 0}
            }
        },
        {
            "name": "create_checkpoint",
            "category": "Workflow Service",
            "params": {
                "workflow_id": "workflow_test_123",
                "step_name": "data_processing",
                "step_number": 3,
                "state_data": {"processed_items": 150, "errors": 0},
                "metadata": {"checkpoint_reason": "milestone"}
            }
        },
        {
            "name": "restore_from_checkpoint",
            "category": "Workflow Service",
            "params": {"checkpoint_id": "checkpoint_test_456"}
        },
        {
            "name": "update_workflow_progress",
            "category": "Workflow Service",
            "params": {
                "workflow_id": "workflow_test_123",
                "step_number": 5,
                "status": "running",
                "error_message": None
            }
        },
        {
            "name": "get_workflow_status",
            "category": "Workflow Service",
            "params": {"workflow_id": "workflow_test_123"}
        },
        {
            "name": "get_workflow_checkpoints",
            "category": "Workflow Service",
            "params": {"workflow_id": "workflow_test_123"}
        },
        {
            "name": "get_workflow_statistics",
            "category": "Workflow Service",
            "params": {}
        },
        
        # Vertical Slice Tools (2)
        {
            "name": "execute_pdf_to_answer_workflow",
            "category": "Vertical Slice",
            "params": {
                "pdf_path": "examples/pdfs/wiki1.pdf",
                "query": "What are the main topics discussed?",
                "workflow_name": "Direct_Test_Analysis"
            }
        },
        {
            "name": "get_vertical_slice_info",
            "category": "Vertical Slice",
            "params": {}
        },
        
        # System Tools (3)
        {
            "name": "test_connection",
            "category": "System",
            "params": {}
        },
        {
            "name": "echo",
            "category": "System",
            "params": {"message": "Testing MCP Server Direct Protocol"}
        },
        {
            "name": "get_system_status",
            "category": "System",
            "params": {}
        }
    ]
    
    # Start MCP server connection
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_server.py"],
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print(f"\n✅ Connected to MCP server")
                results["raw_logs"].append(f"Connected to MCP server at {datetime.now()}")
                
                # Initialize the session
                await session.initialize()
                print("✅ Session initialized")
                results["raw_logs"].append("Session initialized successfully")
                
                # Test each tool
                print(f"\n📋 Testing {len(mcp_tools)} MCP tools...")
                
                for tool in mcp_tools:
                    print(f"\n🧪 TESTING: {tool['name']} ({tool['category']})")
                    print(f"   Parameters: {json.dumps(tool['params'], indent=2)}")
                    print("-" * 70)
                    
                    tool_start = time.time()
                    tool_result = {
                        "tool_name": tool['name'],
                        "category": tool['category'],
                        "parameters": tool['params'],
                        "status": "NOT TESTED",
                        "execution_time": 0,
                        "request": None,
                        "response": None,
                        "error": None
                    }
                    
                    try:
                        # Make the actual MCP tool call
                        request = {
                            "tool": tool['name'],
                            "arguments": tool['params']
                        }
                        tool_result["request"] = request
                        
                        response = await session.call_tool(
                            tool['name'], 
                            tool['params']
                        )
                        
                        tool_result["response"] = response
                        tool_result["status"] = "PASS"
                        results["summary"]["tools_passed"] += 1
                        
                        print(f"✅ PASS: {json.dumps(response, indent=2)}")
                        results["raw_logs"].append(f"PASS: {tool['name']} - Response: {response}")
                        
                    except Exception as e:
                        tool_result["status"] = "FAIL"
                        tool_result["error"] = str(e)
                        results["summary"]["tools_failed"] += 1
                        
                        print(f"❌ FAIL: {str(e)}")
                        results["raw_logs"].append(f"FAIL: {tool['name']} - Error: {str(e)}")
                    
                    tool_result["execution_time"] = time.time() - tool_start
                    results["tool_results"].append(tool_result)
                
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: Failed to connect to MCP server: {str(e)}")
        results["raw_logs"].append(f"CRITICAL ERROR: {str(e)}")
        
        # Mark all tools as NOT TESTED if we can't connect
        for tool in mcp_tools:
            results["tool_results"].append({
                "tool_name": tool['name'],
                "category": tool['category'],
                "parameters": tool['params'],
                "status": "NOT TESTED",
                "error": "Could not connect to MCP server"
            })
            results["summary"]["tools_not_tested"] += 1
    
    # Calculate final statistics
    results["test_metadata"]["end_time"] = time.time()
    results["test_metadata"]["total_duration"] = results["test_metadata"]["end_time"] - results["test_metadata"]["start_time"]
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 DIRECT MCP PROTOCOL TEST RESULTS")
    print("=" * 80)
    print(f"Total Tools: {results['summary']['total_tools']}")
    print(f"✅ Tools Passed: {results['summary']['tools_passed']}")
    print(f"❌ Tools Failed: {results['summary']['tools_failed']}")
    print(f"⚠️  Tools Not Tested: {results['summary']['tools_not_tested']}")
    
    if results['summary']['total_tools'] > 0:
        pass_rate = (results['summary']['tools_passed'] / results['summary']['total_tools']) * 100
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
    
    print(f"⏱️  Total Time: {results['test_metadata']['total_duration']:.2f}s")
    
    # Save detailed results
    with open("mcp_direct_protocol_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: mcp_direct_protocol_test_results.json")
    
    return results

# Run the async test
if __name__ == "__main__":
    print("Starting Direct MCP Protocol Testing...")
    results = asyncio.run(test_all_29_mcp_tools())
    
    # Exit with appropriate code
    if results["summary"]["tools_failed"] > 0 or results["summary"]["tools_not_tested"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)