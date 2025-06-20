#!/usr/bin/env python3
"""
REALISTIC MCP TOOLS TESTING
Start the actual MCP server and make real tool calls
"""

import sys
import json
import time
import subprocess
import requests
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

class MCPServerTester:
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8052"
        
    def start_mcp_server(self):
        """Start the MCP server"""
        print("🚀 Starting MCP server...")
        
        try:
            # Start the MCP server as a subprocess
            self.server_process = subprocess.Popen(
                [sys.executable, "-c", """
import sys
sys.path.insert(0, '.')
from src.mcp_server import mcp
mcp.run(host='localhost', port=8052)
"""],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Path(__file__).parent)
            )
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Test if server is responding
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ MCP server started successfully")
                return True
            else:
                print(f"❌ MCP server health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def stop_mcp_server(self):
        """Stop the MCP server"""
        if self.server_process:
            print("🛑 Stopping MCP server...")
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            print("✅ MCP server stopped")
    
    def call_mcp_tool(self, tool_name, parameters=None):
        """Make a real call to an MCP tool"""
        if parameters is None:
            parameters = {}
            
        try:
            response = requests.post(
                f"{self.server_url}/tools/{tool_name}",
                json=parameters,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "result": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_all_mcp_tools(self):
        """Test all 29 MCP tools with realistic calls"""
        
        print("🔥 TESTING ALL 29 MCP TOOLS (REALISTIC)")
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
        
        # Define all 29 MCP tools with realistic test parameters
        mcp_tools = [
            # Identity Service Tools
            {
                "name": "create_mention",
                "category": "Identity",
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
                "category": "Identity",
                "params": {"mention_id": "test_mention_123"}
            },
            {
                "name": "get_mentions_for_entity",
                "category": "Identity", 
                "params": {"entity_id": "test_entity_123"}
            },
            {
                "name": "merge_entities",
                "category": "Identity",
                "params": {"entity_id1": "entity_1", "entity_id2": "entity_2"}
            },
            {
                "name": "get_identity_stats",
                "category": "Identity",
                "params": {}
            },
            
            # Provenance Service Tools
            {
                "name": "start_operation",
                "category": "Provenance",
                "params": {
                    "tool_name": "test_tool",
                    "input_objects": ["input1", "input2"],
                    "metadata": {"test": "data"}
                }
            },
            {
                "name": "complete_operation",
                "category": "Provenance",
                "params": {
                    "operation_id": "test_op_123",
                    "output_objects": ["output1"],
                    "success": True
                }
            },
            {
                "name": "get_lineage",
                "category": "Provenance",
                "params": {"object_id": "test_object_123"}
            },
            {
                "name": "get_operation_details",
                "category": "Provenance",
                "params": {"operation_id": "test_op_123"}
            },
            {
                "name": "get_operations_for_object",
                "category": "Provenance",
                "params": {"object_id": "test_object_123"}
            },
            {
                "name": "get_tool_statistics",
                "category": "Provenance",
                "params": {}
            },
            
            # Quality Service Tools
            {
                "name": "assess_confidence",
                "category": "Quality",
                "params": {
                    "object_type": "entity",
                    "object_data": {"name": "Test Entity", "type": "PERSON"},
                    "context": {"source": "test"}
                }
            },
            {
                "name": "propagate_confidence",
                "category": "Quality",
                "params": {
                    "from_object_id": "obj1",
                    "to_object_id": "obj2",
                    "operation_type": "extraction"
                }
            },
            {
                "name": "get_quality_assessment",
                "category": "Quality",
                "params": {"object_id": "test_object_123"}
            },
            {
                "name": "get_confidence_trend",
                "category": "Quality", 
                "params": {"object_id": "test_object_123"}
            },
            {
                "name": "filter_by_quality",
                "category": "Quality",
                "params": {
                    "objects": [{"id": "1", "data": "test"}],
                    "min_tier": "BRONZE"
                }
            },
            {
                "name": "get_quality_statistics",
                "category": "Quality",
                "params": {}
            },
            
            # Workflow Service Tools
            {
                "name": "start_workflow",
                "category": "Workflow",
                "params": {
                    "workflow_name": "test_workflow",
                    "description": "Test workflow description"
                }
            },
            {
                "name": "create_checkpoint",
                "category": "Workflow",
                "params": {
                    "workflow_id": "test_workflow_123",
                    "stage": "processing",
                    "data": {"progress": 0.5}
                }
            },
            {
                "name": "restore_from_checkpoint",
                "category": "Workflow",
                "params": {"checkpoint_id": "checkpoint_123"}
            },
            {
                "name": "update_workflow_progress",
                "category": "Workflow",
                "params": {
                    "workflow_id": "test_workflow_123",
                    "stage": "processing",
                    "progress": 0.7,
                    "status": "running"
                }
            },
            {
                "name": "get_workflow_status",
                "category": "Workflow",
                "params": {"workflow_id": "test_workflow_123"}
            },
            {
                "name": "get_workflow_checkpoints",
                "category": "Workflow",
                "params": {"workflow_id": "test_workflow_123"}
            },
            {
                "name": "get_workflow_statistics",
                "category": "Workflow",
                "params": {}
            },
            
            # Vertical Slice Tools
            {
                "name": "execute_pdf_to_answer_workflow",
                "category": "VerticalSlice",
                "params": {
                    "pdf_path": "examples/test.pdf",
                    "query": "What are the main topics?"
                }
            },
            {
                "name": "get_vertical_slice_info",
                "category": "VerticalSlice",
                "params": {}
            },
            
            # System Tools
            {
                "name": "test_connection",
                "category": "System",
                "params": {}
            },
            {
                "name": "echo",
                "category": "System",
                "params": {"text": "Hello MCP!"}
            },
            {
                "name": "get_system_status",
                "category": "System",
                "params": {}
            }
        ]
        
        # Test each tool
        for tool in mcp_tools:
            print(f"\n🧪 TESTING: {tool['name']} ({tool['category']})")
            print(f"   Parameters: {tool['params']}")
            print("-" * 60)
            
            tool_start = time.time()
            result = self.call_mcp_tool(tool['name'], tool['params'])
            
            tool_result = {
                "tool_name": tool['name'],
                "category": tool['category'],
                "parameters": tool['params'],
                "execution_time": time.time() - tool_start,
                "success": result['success']
            }
            
            if result['success']:
                tool_result["result"] = result['result']
                tool_result["error"] = None
                results["test_summary"]["tools_passed"] += 1
                print(f"✅ PASS: {result['result']}")
            else:
                tool_result["result"] = None
                tool_result["error"] = result['error']
                results["test_summary"]["tools_failed"] += 1
                print(f"❌ FAIL: {result['error']}")
            
            results["tool_results"].append(tool_result)
            results["test_summary"]["tools_tested"] += 1
        
        # Generate summary
        results["test_summary"]["end_time"] = time.time()
        results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
        
        print("\n" + "=" * 80)
        print("📊 REALISTIC MCP TOOLS TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tools: {results['test_summary']['total_tools']}")
        print(f"✅ Passed: {results['test_summary']['tools_passed']}")
        print(f"❌ Failed: {results['test_summary']['tools_failed']}")
        print(f"📈 Pass Rate: {(results['test_summary']['tools_passed']/results['test_summary']['total_tools'])*100:.1f}%")
        print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
        
        # Save results
        with open("mcp_tools_realistic_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: mcp_tools_realistic_test_results.json")
        
        return results

def main():
    """Main test function"""
    tester = MCPServerTester()
    
    try:
        # Start MCP server
        if not tester.start_mcp_server():
            print("❌ Could not start MCP server, cannot test tools")
            return 1
        
        # Test all tools
        results = tester.test_all_mcp_tools()
        
        # Return exit code based on results
        return 0 if results["test_summary"]["tools_failed"] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
        
    finally:
        # Always stop the server
        tester.stop_mcp_server()

if __name__ == "__main__":
    sys.exit(main())