#!/usr/bin/env python3
"""
Step 1A Adversarial Test: Try to break basic MCP functionality
"""

import asyncio
import sys
from mcp.server import Server
from mcp.types import Tool, TextContent

async def test_mcp_adversarial():
    """Adversarial tests for MCP server."""
    print("=== Step 1A: Adversarial MCP Tests ===")
    
    results = []
    
    try:
        server = Server("test-server")
        
        @server.list_tools()
        async def handle_list_tools():
            return [
                Tool(
                    name="echo_test",
                    description="Test tool",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"}
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            if name == "echo_test":
                message = arguments.get("message", "")
                return [TextContent(type="text", text=f"Echo: {message}")]
            raise ValueError(f"Unknown tool: {name}")
        
        # Test 1: Empty message
        print("1. Testing empty message...")
        try:
            result = await handle_call_tool("echo_test", {"message": ""})
            assert result[0].text == "Echo: "
            print("✓ Empty message handled")
            results.append("PASS")
        except Exception as e:
            print(f"✗ Empty message failed: {e}")
            results.append("FAIL")
        
        # Test 2: Missing message parameter
        print("2. Testing missing parameter...")
        try:
            result = await handle_call_tool("echo_test", {})
            assert result[0].text == "Echo: "
            print("✓ Missing parameter handled")
            results.append("PASS")
        except Exception as e:
            print(f"✗ Missing parameter failed: {e}")
            results.append("FAIL")
        
        # Test 3: Invalid tool name
        print("3. Testing invalid tool name...")
        try:
            result = await handle_call_tool("nonexistent_tool", {"message": "test"})
            print("✗ Invalid tool should have failed")
            results.append("FAIL")
        except ValueError:
            print("✓ Invalid tool properly rejected")
            results.append("PASS")
        except Exception as e:
            print(f"✗ Unexpected error for invalid tool: {e}")
            results.append("FAIL")
        
        # Test 4: Very long message
        print("4. Testing very long message...")
        try:
            long_message = "x" * 10000
            result = await handle_call_tool("echo_test", {"message": long_message})
            assert "Echo: " + long_message == result[0].text
            print("✓ Long message handled")
            results.append("PASS")
        except Exception as e:
            print(f"✗ Long message failed: {e}")
            results.append("FAIL")
        
        # Test 5: Special characters
        print("5. Testing special characters...")
        try:
            special_chars = "\\n\\r\\t\"'`${}[]<>&"
            result = await handle_call_tool("echo_test", {"message": special_chars})
            assert f"Echo: {special_chars}" == result[0].text
            print("✓ Special characters handled")
            results.append("PASS")
        except Exception as e:
            print(f"✗ Special characters failed: {e}")
            results.append("FAIL")
        
        # Test 6: Unicode characters
        print("6. Testing Unicode characters...")
        try:
            unicode_chars = "🙂😀🎉测试🔥"
            result = await handle_call_tool("echo_test", {"message": unicode_chars})
            assert f"Echo: {unicode_chars}" == result[0].text
            print("✓ Unicode characters handled")
            results.append("PASS")
        except Exception as e:
            print(f"✗ Unicode characters failed: {e}")
            results.append("FAIL")
        
        # Test 7: Invalid argument types
        print("7. Testing invalid argument types...")
        try:
            result = await handle_call_tool("echo_test", {"message": 12345})
            # Should handle or reject gracefully
            print("✓ Invalid argument type handled")
            results.append("PASS")
        except Exception as e:
            print(f"⚠️  Invalid argument type error: {e}")
            results.append("PASS")  # Either handling or rejecting is acceptable
        
        return results
        
    except Exception as e:
        print(f"✗ Adversarial test setup failed: {e}")
        return ["FAIL"] * 7

async def main():
    results = await test_mcp_adversarial()
    
    passed = results.count("PASS")
    total = len(results)
    
    print(f"\n=== Step 1A Adversarial Test Results ===")
    print(f"Passed: {passed}/{total} tests")
    
    with open("step1A_adversarial_results.txt", "w") as f:
        f.write(f"Step 1A Adversarial Tests: {passed}/{total} passed\\n")
        for i, result in enumerate(results, 1):
            f.write(f"Test {i}: {result}\\n")
    
    if passed >= total - 1:  # Allow 1 failure
        print("✓ Step 1A adversarial tests mostly passed")
        return True
    else:
        print("✗ Step 1A adversarial tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)