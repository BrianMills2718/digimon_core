"""
MCP Server Implementation for KGAS Tools
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .tool_wrapper import MCPCompatibilityLayer

logger = logging.getLogger(__name__)

@dataclass
class MCPRequest:
    """MCP protocol request"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

@dataclass
class MCPResponse:
    """MCP protocol response"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPServer:
    """MCP Server for KGAS tools"""
    
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.mcp_layer = MCPCompatibilityLayer(service_manager)
        self.running = False
        
    async def start(self, host: str = "localhost", port: int = 8765):
        """Start the MCP server"""
        try:
            # For now, we'll implement a simple async interface
            # In a full implementation, this would be a WebSocket or HTTP server
            logger.info(f"MCP Server starting on {host}:{port}")
            self.running = True
            logger.info("MCP Server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def stop(self):
        """Stop the MCP server"""
        self.running = False
        logger.info("MCP Server stopped")
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP protocol request"""
        try:
            # Parse request
            request = MCPRequest(
                jsonrpc=request_data.get("jsonrpc", "2.0"),
                id=request_data.get("id"),
                method=request_data.get("method"),
                params=request_data.get("params", {})
            )
            
            # Route request to appropriate handler
            if request.method == "initialize":
                result = await self._handle_initialize(request.params)
            elif request.method == "tools/list":
                result = await self._handle_list_tools(request.params)
            elif request.method == "tools/call":
                result = await self._handle_call_tool(request.params)
            elif request.method == "tools/batch_call":
                result = await self._handle_batch_call_tools(request.params)
            elif request.method == "server/info":
                result = await self._handle_server_info(request.params)
            elif request.method == "ping":
                result = await self._handle_ping(request.params)
            else:
                raise ValueError(f"Unknown method: {request.method}")
            
            # Create success response
            response = MCPResponse(
                id=request.id,
                result=result
            )
            
            return asdict(response)
            
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            
            # Create error response
            response = MCPResponse(
                id=request_data.get("id"),
                error={
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            )
            
            return asdict(response)
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        client_info = params.get("clientInfo", {})
        logger.info(f"MCP client connecting: {client_info}")
        
        return {
            "protocolVersion": "1.0.0",
            "serverInfo": self.mcp_layer.get_server_info(),
            "capabilities": self.mcp_layer.get_capabilities()
        }
    
    async def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return await self.mcp_layer.list_tools()
    
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not name:
            raise ValueError("Tool name is required")
        
        return await self.mcp_layer.call_tool(name, arguments)
    
    async def _handle_batch_call_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/batch_call request"""
        calls = params.get("calls", [])
        
        if not calls:
            raise ValueError("Calls list is required")
        
        results = await self.mcp_layer.batch_call_tools(calls)
        return {"results": results}
    
    async def _handle_server_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle server/info request"""
        return self.mcp_layer.get_server_info()
    
    async def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request"""
        timestamp = params.get("timestamp")
        return {
            "pong": True,
            "timestamp": timestamp,
            "server_time": asyncio.get_event_loop().time()
        }

class MCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self._request_id = 0
    
    def _next_id(self) -> str:
        """Generate next request ID"""
        self._request_id += 1
        return str(self._request_id)
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection with server"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "KGAS Test Client",
                    "version": "1.0.0"
                }
            }
        }
        
        return await self.server.handle_request(request)
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        request = {
            "jsonrpc": "2.0", 
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        
        return await self.server.handle_request(request)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(), 
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        return await self.server.handle_request(request)
    
    async def ping(self) -> Dict[str, Any]:
        """Ping the server"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "ping",
            "params": {
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        
        return await self.server.handle_request(request)

# Convenience functions for testing
async def create_test_mcp_setup():
    """Create MCP server and client for testing"""
    # Import here to avoid circular imports
    from ..core.service_manager import ServiceManager
    
    service_manager = ServiceManager()
    server = MCPServer(service_manager)
    client = MCPClient(server)
    
    await server.start()
    return server, client

async def test_mcp_integration():
    """Test MCP integration with KGAS tools"""
    print("🔧 Testing MCP Integration")
    print("=" * 50)
    
    try:
        server, client = await create_test_mcp_setup()
        
        # Test initialize
        print("\n1. Testing initialize...")
        init_response = await client.initialize()
        print(f"   Status: {'✅' if init_response.get('result') else '❌'}")
        
        # Test list tools
        print("\n2. Testing list tools...")
        tools_response = await client.list_tools()
        if tools_response.get('result'):
            tools = tools_response['result'].get('tools', [])
            print(f"   Found {len(tools)} tools: {[t['name'] for t in tools]}")
        
        # Test ping
        print("\n3. Testing ping...")
        ping_response = await client.ping()
        print(f"   Ping successful: {'✅' if ping_response.get('result', {}).get('pong') else '❌'}")
        
        await server.stop()
        
        print("\n✅ MCP integration test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ MCP integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())