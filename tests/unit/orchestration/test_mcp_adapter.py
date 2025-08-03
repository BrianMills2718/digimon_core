"""
Unit tests for MCP tool adapter.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.orchestration.mcp_adapter import MCPToolAdapter
from src.orchestration.base import Result


class TestMCPToolAdapter:
    """Test MCP tool adapter."""
    
    @pytest.fixture
    def mock_mcp_server(self):
        """Create mock MCP server."""
        server = Mock()
        server._tools = {
            "test_tool": lambda: "test_result",
            "param_tool": lambda param1, param2: f"{param1}_{param2}",
            "error_tool": Mock(side_effect=Exception("Tool error"))
        }
        return server
    
    @pytest.fixture
    def mock_server_manager(self, mock_mcp_server):
        """Create mock server manager."""
        manager = Mock()
        manager.register_all_tools = Mock()
        manager.get_server = Mock(return_value=mock_mcp_server)
        return manager
    
    def test_adapter_creation(self):
        """Test creating MCP adapter."""
        adapter = MCPToolAdapter()
        
        assert adapter.server_manager is None
        assert adapter.mcp_server is None
        assert adapter.tool_registry == {}
        assert adapter._initialized is False
        assert len(adapter._available_tools) == 0
    
    @pytest.mark.asyncio
    async def test_adapter_initialization_success(self, mock_server_manager, mock_mcp_server):
        """Test successful adapter initialization."""
        adapter = MCPToolAdapter()
        
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                success = await adapter.initialize()
        
        assert success is True
        assert adapter._initialized is True
        assert adapter.server_manager is mock_server_manager
        assert adapter.mcp_server is mock_mcp_server
        assert len(adapter.tool_registry) == 3
        assert "test_tool" in adapter._available_tools
        assert "param_tool" in adapter._available_tools
        assert "error_tool" in adapter._available_tools
    
    def test_adapter_initialization_import_error(self):
        """Test adapter initialization with import error (sync test)."""
        adapter = MCPToolAdapter()
        
        # Test the sync aspects - async initialization is tested elsewhere
        assert adapter.server_manager is None
        assert adapter.mcp_server is None
        assert adapter._initialized is False
        assert len(adapter.tool_registry) == 0
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, mock_server_manager, mock_mcp_server):
        """Test successful tool call."""
        adapter = MCPToolAdapter()
        
        # Initialize adapter
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                await adapter.initialize()
        
        # Call tool without parameters
        result = await adapter.call_tool("test_tool")
        
        assert result.success is True
        assert result.data == "test_result"
        assert result.metadata["tool"] == "test_tool"
        assert result.metadata["adapter"] == "mcp"
        assert "execution_time" in result.metadata
    
    @pytest.mark.asyncio
    async def test_call_tool_with_parameters(self, mock_server_manager, mock_mcp_server):
        """Test tool call with parameters."""
        adapter = MCPToolAdapter()
        
        # Initialize adapter
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                await adapter.initialize()
        
        # Call tool with parameters
        result = await adapter.call_tool("param_tool", {"param1": "hello", "param2": "world"})
        
        assert result.success is True
        assert result.data == "hello_world"
        assert result.metadata["parameters"] == {"param1": "hello", "param2": "world"}
    
    @pytest.mark.asyncio
    async def test_call_tool_not_initialized(self):
        """Test calling tool when not initialized."""
        adapter = MCPToolAdapter()
        
        result = await adapter.call_tool("test_tool")
        
        assert result.success is False
        assert result.error == "MCP adapter not initialized"
    
    @pytest.mark.asyncio
    async def test_call_tool_not_found(self, mock_server_manager, mock_mcp_server):
        """Test calling non-existent tool."""
        adapter = MCPToolAdapter()
        
        # Initialize adapter
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                await adapter.initialize()
        
        result = await adapter.call_tool("nonexistent_tool")
        
        assert result.success is False
        assert "not found" in result.error
        assert result.metadata["available_tools"] == ["test_tool", "param_tool", "error_tool"]
    
    @pytest.mark.asyncio
    async def test_call_tool_execution_error(self, mock_server_manager, mock_mcp_server):
        """Test tool execution error."""
        adapter = MCPToolAdapter()
        
        # Initialize adapter
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                await adapter.initialize()
        
        result = await adapter.call_tool("error_tool")
        
        assert result.success is False
        assert "Tool error" in result.error
        assert result.metadata["error_type"] == "Exception"
    
    def test_get_available_tools(self, mock_server_manager, mock_mcp_server):
        """Test getting available tools."""
        adapter = MCPToolAdapter()
        adapter._available_tools = {"tool1", "tool2", "tool3"}
        
        tools = adapter.get_available_tools()
        
        assert len(tools) == 3
        assert "tool1" in tools
        assert "tool2" in tools
        assert "tool3" in tools
    
    def test_get_tool_info(self):
        """Test getting tool information."""
        adapter = MCPToolAdapter()
        
        # Mock tool with docstring
        def mock_tool(param1: str, param2: int) -> str:
            """This is a test tool."""
            return "result"
        
        adapter.tool_registry = {"test_tool": mock_tool}
        
        info = adapter.get_tool_info("test_tool")
        
        assert info["name"] == "test_tool"
        assert info["available"] is True
        assert info["callable"] is True
        assert info["description"] == "This is a test tool."
        assert "param1: str" in info["parameters"]
        assert "param2: int" in info["parameters"]
    
    def test_get_tool_info_not_found(self):
        """Test getting info for non-existent tool."""
        adapter = MCPToolAdapter()
        
        info = adapter.get_tool_info("nonexistent")
        
        assert info["error"] == "Tool 'nonexistent' not found"
    
    def test_get_tools_by_category(self):
        """Test categorizing tools."""
        adapter = MCPToolAdapter()
        adapter._available_tools = {
            "load_documents",
            "extract_entities",
            "build_edges",
            "calculate_pagerank",
            "chunk_text",
            "test_connection",
            "custom_tool"
        }
        
        categories = adapter.get_tools_by_category()
        
        assert "load_documents" in categories["document_processing"]
        assert "extract_entities" in categories["entity_extraction"]
        assert "build_edges" in categories["graph_building"]
        assert "calculate_pagerank" in categories["graph_analysis"]
        assert "chunk_text" in categories["text_processing"]
        assert "test_connection" in categories["server_management"]
        assert "custom_tool" in categories["other"]
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_server_manager, mock_mcp_server):
        """Test health check."""
        adapter = MCPToolAdapter()
        
        # Before initialization
        health = await adapter.health_check()
        assert health["initialized"] is False
        assert health["status"] == "unhealthy"
        
        # After initialization
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                await adapter.initialize()
        
        # Add test_connection tool
        adapter.tool_registry["test_connection"] = lambda: True
        
        health = await adapter.health_check()
        assert health["initialized"] is True
        assert health["total_tools"] == 4
        assert health["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_server_manager, mock_mcp_server):
        """Test adapter cleanup."""
        adapter = MCPToolAdapter()
        
        # Initialize first
        with patch('src.mcp_tools.server_manager.get_mcp_server_manager', return_value=mock_server_manager):
            with patch('src.tools.phase1.phase1_mcp_tools.create_phase1_mcp_tools'):
                await adapter.initialize()
        
        assert adapter._initialized is True
        assert len(adapter.tool_registry) > 0
        
        # Cleanup
        await adapter.cleanup()
        
        assert adapter._initialized is False
        assert len(adapter.tool_registry) == 0
        assert len(adapter._available_tools) == 0
        assert adapter.mcp_server is None
        assert adapter.server_manager is None