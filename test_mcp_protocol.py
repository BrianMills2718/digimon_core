#!/usr/bin/env python3
"""
Test MCP server with actual protocol communication
"""

import asyncio
import json
import subprocess
import sys
import time

async def test_mcp_protocol():
    """Test MCP server using actual protocol."""
    print("=== Testing MCP Protocol Communication ===")
    
    # Start the MCP server
    proc = subprocess.Popen([
        'python', '/home/brian/Digimons/working_mcp_server.py'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        # Test 1: Initialize
        print("1. Testing initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        proc.stdin.write(json.dumps(init_request) + '\n')
        proc.stdin.flush()
        
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print(f"✓ Initialize response: {response.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
        else:
            print("✗ No initialize response")
            return False
        
        # Test 2: List tools
        print("2. Testing tools/list...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        proc.stdin.write(json.dumps(list_request) + '\n')
        proc.stdin.flush()
        
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            tools = response.get('result', {}).get('tools', [])
            tool_names = [tool['name'] for tool in tools]
            print(f"✓ Tools available: {tool_names}")
            
            if 'echo' in tool_names and 'test_connection' in tool_names:
                print("✓ Expected tools found")
            else:
                print("✗ Expected tools missing")
                return False
        else:
            print("✗ No tools/list response")
            return False
        
        # Test 3: Call tool
        print("3. Testing tools/call...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "test_connection",
                "arguments": {}
            }
        }
        
        proc.stdin.write(json.dumps(call_request) + '\n')
        proc.stdin.flush()
        
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            content = response.get('result', {}).get('content', [])
            if content and 'working' in content[0].get('text', ''):
                print("✓ Tool execution works")
                return True
            else:
                print(f"✗ Unexpected tool response: {content}")
                return False
        else:
            print("✗ No tools/call response")
            return False
            
    except Exception as e:
        print(f"✗ Protocol test failed: {e}")
        return False
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

def main():
    try:
        result = asyncio.run(test_mcp_protocol())
        
        print(f"\n=== MCP Protocol Test Result ===")
        if result:
            print("✓ MCP server protocol communication works")
            with open("mcp_protocol_test.txt", "w") as f:
                f.write("PASS: MCP protocol communication working\n")
                f.write(f"Date: {time.time()}\n")
            return True
        else:
            print("✗ MCP server protocol communication failed")
            with open("mcp_protocol_test.txt", "w") as f:
                f.write("FAIL: MCP protocol communication failed\n")
            return False
    except Exception as e:
        print(f"✗ Test setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)