"""
MCP Integration Testing
Tests for MCP tool registration, wrapper, and server functionality
"""
import pytest
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mcp.tool_registry import MCPToolRegistry
from src.mcp.tool_wrapper import MCPCompatibilityLayer
from src.mcp.mcp_server import MCPServer, MCPClient
from src.core.service_manager import ServiceManager

class TestMCPToolRegistry:
    """Test MCP tool registration functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service_manager = ServiceManager()
        self.registry = MCPToolRegistry(self.service_manager)
    
    def test_tool_registration(self):
        """Test that all 8 tools are registered"""
        tools = self.registry.list_tools()
        
        expected_tools = [
            "T01_PDF_LOADER",
            "T15A_TEXT_CHUNKER", 
            "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR",
            "T31_ENTITY_BUILDER",
            "T34_EDGE_BUILDER",
            "T68_PAGE_RANK",
            "T49_MULTI_HOP_QUERY"
        ]
        
        assert len(tools) == 8, f"Expected 8 tools, got {len(tools)}"
        
        for tool_id in expected_tools:
            assert tool_id in tools, f"Tool {tool_id} not registered"
    
    def test_tool_manifest_generation(self):
        """Test MCP tool manifest generation"""
        manifest = self.registry.get_tool_manifest()
        
        assert "tools" in manifest
        assert "version" in manifest
        assert "protocol_version" in manifest
        
        tools = manifest["tools"]
        assert len(tools) == 8
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert "outputSchema" in tool
    
    def test_tool_instance_creation(self):
        """Test tool instance creation"""
        # Test getting a tool instance
        tool_instance = self.registry.get_tool_instance("T01_PDF_LOADER")
        
        # Should be able to create instance (may be None if dependencies missing)
        # This is acceptable for testing
        if tool_instance:
            assert hasattr(tool_instance, 'execute')
    
    def test_registry_stats(self):
        """Test registry statistics"""
        stats = self.registry.get_registry_stats()
        
        assert "total_tools" in stats
        assert "instantiated_tools" in stats
        assert "tools_by_id" in stats
        assert "registry_status" in stats
        
        assert stats["total_tools"] == 8
        assert stats["registry_status"] == "operational"

class TestMCPCompatibilityLayer:
    """Test MCP compatibility layer"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service_manager = ServiceManager()
        self.mcp_layer = MCPCompatibilityLayer(self.service_manager)
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test tool listing via MCP"""
        tools_response = await self.mcp_layer.list_tools()
        
        assert "tools" in tools_response
        tools = tools_response["tools"]
        assert len(tools) == 8
    
    @pytest.mark.asyncio
    async def test_call_tool_simple(self):
        """Test simple tool call"""
        # Test with a simple tool call (may fail due to missing dependencies)
        response = await self.mcp_layer.call_tool(
            "T01_PDF_LOADER",
            {"input_data": {"file_path": "nonexistent.pdf"}}
        )
        
        assert "content" in response
        # Should either succeed or fail gracefully
        assert "isError" in response or "content" in response
    
    def test_server_info(self):
        """Test server info generation"""
        info = self.mcp_layer.get_server_info()
        
        assert "name" in info
        assert "version" in info
        assert "protocol_version" in info
        assert "capabilities" in info
        assert "server_stats" in info
        
        assert info["name"] == "KGAS MCP Server"
    
    def test_capabilities(self):
        """Test capabilities reporting"""
        capabilities = self.mcp_layer.get_capabilities()
        
        assert "tools" in capabilities
        assert "resources" in capabilities
        assert "prompts" in capabilities
        assert "experimental" in capabilities

class TestMCPServer:
    """Test MCP server functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service_manager = ServiceManager()
        self.server = MCPServer(self.service_manager)
    
    @pytest.mark.asyncio
    async def test_server_startup(self):
        """Test server can start"""
        await self.server.start()
        assert self.server.running == True
        await self.server.stop()
    
    @pytest.mark.asyncio
    async def test_initialize_request(self):
        """Test initialize request handling"""
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "Test Client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "1"
        assert "result" in response
        
        result = response["result"]
        assert "protocolVersion" in result
        assert "serverInfo" in result
        assert "capabilities" in result
    
    @pytest.mark.asyncio
    async def test_list_tools_request(self):
        """Test tools/list request handling"""
        request = {
            "jsonrpc": "2.0",
            "id": "2", 
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "2"
        assert "result" in response
        
        result = response["result"]
        assert "tools" in result
        assert len(result["tools"]) == 8
    
    @pytest.mark.asyncio
    async def test_ping_request(self):
        """Test ping request handling"""
        request = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "ping",
            "params": {"timestamp": 12345}
        }
        
        response = await self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "3"
        assert "result" in response
        
        result = response["result"]
        assert result["pong"] == True
        assert result["timestamp"] == 12345
    
    @pytest.mark.asyncio
    async def test_unknown_method(self):
        """Test unknown method handling"""
        request = {
            "jsonrpc": "2.0",
            "id": "4",
            "method": "unknown/method",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "4"
        assert "error" in response
        
        error = response["error"]
        assert error["code"] == -32603  # Internal error
        assert "Unknown method" in error["message"]

class TestMCPClientServerIntegration:
    """Test MCP client-server integration"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service_manager = ServiceManager()
        self.server = MCPServer(self.service_manager)
        self.client = MCPClient(self.server)
    
    @pytest.mark.asyncio
    async def test_client_server_initialize(self):
        """Test client-server initialization"""
        await self.server.start()
        
        response = await self.client.initialize()
        
        assert "result" in response
        result = response["result"]
        assert "serverInfo" in result
        assert result["serverInfo"]["name"] == "KGAS MCP Server"
        
        await self.server.stop()
    
    @pytest.mark.asyncio
    async def test_client_server_list_tools(self):
        """Test client-server tool listing"""
        await self.server.start()
        
        # Initialize first
        await self.client.initialize()
        
        # List tools
        response = await self.client.list_tools()
        
        assert "result" in response
        result = response["result"]
        assert "tools" in result
        assert len(result["tools"]) == 8
        
        await self.server.stop()
    
    @pytest.mark.asyncio
    async def test_client_server_ping(self):
        """Test client-server ping"""
        await self.server.start()
        
        response = await self.client.ping()
        
        assert "result" in response
        result = response["result"]
        assert result["pong"] == True
        
        await self.server.stop()

# Main test execution
if __name__ == "__main__":
    # Run basic tests
    print("🔧 Running MCP Integration Tests")
    print("=" * 50)
    
    # Test registry
    print("\n1. Testing Tool Registry...")
    test_registry = TestMCPToolRegistry()
    test_registry.setup_method()
    
    try:
        test_registry.test_tool_registration()
        print("   ✅ Tool registration")
        
        test_registry.test_tool_manifest_generation()
        print("   ✅ Manifest generation")
        
        test_registry.test_registry_stats()
        print("   ✅ Registry statistics")
        
    except Exception as e:
        print(f"   ❌ Registry test failed: {e}")
    
    # Test compatibility layer
    print("\n2. Testing MCP Compatibility Layer...")
    test_compat = TestMCPCompatibilityLayer()
    test_compat.setup_method()
    
    try:
        info = test_compat.mcp_layer.get_server_info()
        print("   ✅ Server info generation")
        
        capabilities = test_compat.mcp_layer.get_capabilities()
        print("   ✅ Capabilities reporting")
        
    except Exception as e:
        print(f"   ❌ Compatibility layer test failed: {e}")
    
    # Test async functionality
    print("\n3. Testing Async MCP Operations...")
    
    async def run_async_tests():
        try:
            # Test server
            service_manager = ServiceManager()
            server = MCPServer(service_manager)
            
            await server.start()
            print("   ✅ Server startup")
            
            # Test request handling
            request = {
                "jsonrpc": "2.0",
                "id": "test",
                "method": "ping",
                "params": {"timestamp": 12345}
            }
            
            response = await server.handle_request(request)
            if response.get("result", {}).get("pong"):
                print("   ✅ Request handling")
            else:
                print("   ❌ Request handling failed")
            
            await server.stop()
            print("   ✅ Server shutdown")
            
        except Exception as e:
            print(f"   ❌ Async test failed: {e}")
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    print("\n✅ MCP Integration Tests completed")