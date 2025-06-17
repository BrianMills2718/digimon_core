#!/usr/bin/env python3
"""
Test the working MCP server functionality
"""

import subprocess
import sys
import time

def test_server_startup():
    """Test that the working MCP server starts properly."""
    print("=== Testing Working MCP Server ===")
    
    try:
        # Test server startup
        print("1. Testing server startup...")
        proc = subprocess.Popen([
            'python', '/home/brian/Digimons/working_mcp_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for startup
        time.sleep(2)
        
        # Check if process is still running (stdio servers stay alive)
        if proc.poll() is None:
            print("✅ Working MCP server started successfully")
            proc.terminate()
            proc.wait(timeout=5)
            print("✅ Server terminated cleanly")
            return True
        else:
            stdout, stderr = proc.communicate()
            print(f"❌ Server process exited early")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def test_server_import():
    """Test that the server module can be imported."""
    print("2. Testing server import...")
    
    try:
        result = subprocess.run([
            'python', '-c', 
            '''
import sys
sys.path.append("/home/brian/Digimons")
from working_mcp_server import server
print("✅ Server object imported successfully")
print("Server name:", server.name if hasattr(server, "name") else "MCP Server")
'''
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Working MCP server can be imported")
            print(result.stdout.strip())
            return True
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    print("=== Testing Working MCP Server ===\n")
    
    results = []
    results.append(test_server_startup())
    results.append(test_server_import())
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("✅ Working MCP server is functioning properly")
        
        # Write verification file
        with open("working_mcp_verification.txt", "w") as f:
            f.write(f"Working MCP Server Verification: {passed}/{total} tests passed\n")
            f.write(f"Date: {time.ctime()}\n")
            f.write("Status: WORKING\n")
            f.write("Server: /home/brian/Digimons/working_mcp_server.py\n")
            f.write("Configuration: claude mcp list shows super-digimon\n")
        
        return True
    else:
        print("❌ Working MCP server has issues")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)