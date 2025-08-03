"""
TwitterExplorer Tool Interface Compliance Tests

TDD Phase 2: Interface compliance tests
These tests validate the tool implements the UnifiedTool interface correctly.
"""

import pytest
from unittest.mock import Mock, patch
import time
import psutil
from datetime import datetime

# Import KGAS base classes
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

# Mock service manager for testing
@pytest.fixture
def mock_service_manager():
    """Create mock service manager for testing"""
    service_manager = Mock()
    
    # Mock identity service
    identity_service = Mock()
    identity_service.create_entity.return_value = Mock(
        success=True, 
        data={"entity_id": "test_entity_id", "mention_id": "test_mention_id"}
    )
    service_manager.identity_service = identity_service
    
    # Mock provenance service
    provenance_service = Mock()
    provenance_service.log_execution.return_value = True
    service_manager.provenance_service = provenance_service
    
    # Mock quality service
    quality_service = Mock()
    quality_service.assess_confidence.return_value = 0.9
    service_manager.quality_service = quality_service
    
    # Mock health check
    service_manager.health_check.return_value = {
        "identity_service": True,
        "provenance_service": True, 
        "quality_service": True
    }
    
    return service_manager


def create_test_request(query: str, **kwargs) -> ToolRequest:
    """Helper to create test requests"""
    return ToolRequest(
        tool_id="T85_TWITTER_EXPLORER",
        operation="query",
        input_data={
            "query": query,
            "api_keys": {
                "gemini_key": "test_gemini_key",
                "rapidapi_key": "test_rapidapi_key"
            },
            **kwargs
        },
        parameters={}
    )


class TestTwitterExplorerInterface:
    """Test tool interface compliance before implementation"""
    
    def test_tool_class_exists(self):
        """Test TwitterExplorerTool class can be imported"""
        try:
            from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        except ImportError as e:
            pytest.fail(f"TwitterExplorerTool class not found: {e}")
    
    def test_implements_base_tool_interface(self, mock_service_manager):
        """Test tool implements BaseTool ABC"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        # Should be subclass of BaseTool
        assert issubclass(TwitterExplorerTool, BaseTool)
        
        # Should be instantiable
        tool = TwitterExplorerTool(mock_service_manager)
        assert isinstance(tool, BaseTool)
    
    def test_has_required_methods(self, mock_service_manager):
        """Test tool has all required BaseTool methods"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        # Check all required methods exist
        assert hasattr(tool, 'get_contract'), "Missing get_contract method"
        assert hasattr(tool, 'execute'), "Missing execute method"
        assert hasattr(tool, 'validate_input'), "Missing validate_input method"
        assert hasattr(tool, 'health_check'), "Missing health_check method"
        assert hasattr(tool, 'get_status'), "Missing get_status method"
        assert hasattr(tool, 'cleanup'), "Missing cleanup method"
        
        # Check methods are callable
        assert callable(tool.get_contract)
        assert callable(tool.execute)
        assert callable(tool.validate_input)
        assert callable(tool.health_check)
        assert callable(tool.get_status)
        assert callable(tool.cleanup)
    
    def test_get_contract_returns_valid_contract(self, mock_service_manager):
        """Test get_contract() returns valid ToolContract"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        contract = tool.get_contract()
        
        # Should return ToolContract instance
        assert isinstance(contract, ToolContract)
        
        # Should have correct tool ID
        assert contract.tool_id == "T85_TWITTER_EXPLORER"
        
        # Should have correct category
        assert contract.category == "social_media_analysis"
        
        # Should have dependencies
        assert len(contract.dependencies) > 0
        assert "google-generativeai" in contract.dependencies
        assert "requests" in contract.dependencies
        
        # Should have performance requirements
        assert contract.performance_requirements is not None
        assert "max_execution_time" in contract.performance_requirements
        assert "max_memory_mb" in contract.performance_requirements
        
        # Should have error conditions
        assert len(contract.error_conditions) > 0
        assert "INVALID_QUERY" in contract.error_conditions
        assert "MISSING_API_KEYS" in contract.error_conditions
    
    def test_get_status_returns_tool_status(self, mock_service_manager):
        """Test get_status() returns valid ToolStatus"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        status = tool.get_status()
        
        # Should return ToolStatus enum value
        assert isinstance(status, ToolStatus)
        
        # Should be ready initially
        assert status == ToolStatus.READY
    
    def test_validate_input_handles_valid_input(self, mock_service_manager):
        """Test validate_input() accepts valid input"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        valid_input = {
            "query": "Tell me about @github",
            "api_keys": {
                "gemini_key": "test_key",
                "rapidapi_key": "test_key"
            }
        }
        
        result = tool.validate_input(valid_input)
        assert result is True
    
    def test_validate_input_rejects_invalid_input(self, mock_service_manager):
        """Test validate_input() rejects invalid input"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        invalid_inputs = [
            {},  # Empty input
            {"query": ""},  # Empty query
            {"query": "test"},  # Missing api_keys
            {"api_keys": {"gemini_key": "test"}},  # Missing rapidapi_key
            {"query": "test", "api_keys": {"gemini_key": "", "rapidapi_key": "test"}},  # Empty gemini_key
        ]
        
        for invalid_input in invalid_inputs:
            result = tool.validate_input(invalid_input)
            assert result is False, f"Should reject invalid input: {invalid_input}"
    
    def test_execute_returns_tool_result(self, mock_service_manager):
        """Test execute() returns valid ToolResult"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Tell me about @github")
        
        with patch.object(tool, '_execute_twitter_query') as mock_execute:
            # Mock successful execution
            mock_execute.return_value = {
                "summary": "Test summary",
                "entities": [],
                "relationships": [],
                "graph_data": {"nodes": [], "edges": [], "metadata": {}},
                "api_execution_log": [],
                "processing_stats": {
                    "total_api_calls": 1,
                    "total_execution_time": 1.0,
                    "entities_extracted": 0,
                    "relationships_extracted": 0,
                    "query_complexity_score": 0.5
                }
            }
            
            result = tool.execute(request)
            
            # Should return ToolResult instance
            assert isinstance(result, ToolResult)
            
            # Should have correct tool ID
            assert result.tool_id == "T85_TWITTER_EXPLORER"
            
            # Should have success status
            assert result.status == "success"
            
            # Should have execution metrics
            assert result.execution_time >= 0
            assert result.memory_used >= 0
            
            # Should have required data fields
            assert "summary" in result.data
            assert "entities" in result.data
            assert "relationships" in result.data
            assert "processing_stats" in result.data
    
    def test_execute_handles_invalid_input(self, mock_service_manager):
        """Test execute() handles invalid input gracefully"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        # Create request with invalid input
        invalid_request = ToolRequest(
            tool_id="T85_TWITTER_EXPLORER",
            operation="query",
            input_data={},  # Invalid - missing required fields
            parameters={}
        )
        
        result = tool.execute(invalid_request)
        
        # Should return error result
        assert isinstance(result, ToolResult)
        assert result.status == "error"
        assert result.error_code is not None
        assert result.error_message is not None
    
    def test_health_check_returns_tool_result(self, mock_service_manager):
        """Test health_check() returns valid ToolResult"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        result = tool.health_check()
        
        # Should return ToolResult instance
        assert isinstance(result, ToolResult)
        assert result.tool_id == "T85_TWITTER_EXPLORER"
        
        # Should have health status
        assert "healthy" in result.data
        assert isinstance(result.data["healthy"], bool)
        
        # Should check dependencies
        if result.data["healthy"]:
            assert "dependencies_healthy" in result.data
            assert result.data["dependencies_healthy"] is True
    
    def test_cleanup_returns_boolean(self, mock_service_manager):
        """Test cleanup() returns boolean"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        result = tool.cleanup()
        
        # Should return boolean
        assert isinstance(result, bool)
    
    def test_tool_is_stateless_between_executions(self, mock_service_manager):
        """Test tool doesn't maintain state between executions"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        with patch.object(tool, '_execute_twitter_query') as mock_execute:
            mock_execute.return_value = {
                "summary": "Test summary",
                "entities": [],
                "relationships": [],
                "graph_data": {"nodes": [], "edges": [], "metadata": {}},
                "api_execution_log": [],
                "processing_stats": {
                    "total_api_calls": 1,
                    "total_execution_time": 1.0,
                    "entities_extracted": 0,
                    "relationships_extracted": 0,
                    "query_complexity_score": 0.5
                }
            }
            
            # Execute first query
            request1 = create_test_request("Query 1")
            result1 = tool.execute(request1)
            
            # Execute second query
            request2 = create_test_request("Query 2")
            result2 = tool.execute(request2)
            
            # Results should be independent
            assert result1.data != result2.data or mock_execute.call_count == 2
            
            # Tool should not have cached state
            assert not hasattr(tool, '_cached_results')
            assert not hasattr(tool, '_last_query')
            assert not hasattr(tool, '_session_data')


class TestTwitterExplorerInterfaceEdgeCases:
    """Test interface edge cases and error conditions"""
    
    def test_execute_with_none_request(self, mock_service_manager):
        """Test execute() handles None request"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        try:
            result = tool.execute(None)
            # Should return error result, not crash
            assert isinstance(result, ToolResult)
            assert result.status == "error"
        except Exception as e:
            pytest.fail(f"Tool should handle None request gracefully, not crash: {e}")
    
    def test_validate_input_with_none_input(self, mock_service_manager):
        """Test validate_input() handles None input"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        try:
            result = tool.validate_input(None)
            assert result is False
        except Exception as e:
            pytest.fail(f"Tool should handle None input gracefully: {e}")
    
    def test_tool_handles_service_manager_none(self):
        """Test tool handles None service manager"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        try:
            tool = TwitterExplorerTool(None)
            # Should either work with None or raise clear error
            assert tool is not None
        except Exception as e:
            # Should be clear error message, not cryptic failure
            assert "service_manager" in str(e).lower() or "required" in str(e).lower()
    
    def test_concurrent_execution_safety(self, mock_service_manager):
        """Test tool can handle concurrent execution safely"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        import threading
        
        tool = TwitterExplorerTool(mock_service_manager)
        results = []
        errors = []
        
        def execute_query(query_id):
            try:
                request = create_test_request(f"Query {query_id}")
                with patch.object(tool, '_execute_twitter_query') as mock_execute:
                    mock_execute.return_value = {
                        "summary": f"Summary {query_id}",
                        "entities": [],
                        "relationships": [],
                        "graph_data": {"nodes": [], "edges": [], "metadata": {}},
                        "api_execution_log": [],
                        "processing_stats": {
                            "total_api_calls": 1,
                            "total_execution_time": 1.0,
                            "entities_extracted": 0,
                            "relationships_extracted": 0,
                            "query_complexity_score": 0.5
                        }
                    }
                    result = tool.execute(request)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Execute concurrent queries
        threads = []
        for i in range(3):
            thread = threading.Thread(target=execute_query, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should handle concurrent execution without errors
        assert len(errors) == 0, f"Concurrent execution errors: {errors}"
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # All results should be valid
        for result in results:
            assert isinstance(result, ToolResult)
            assert result.status in ["success", "error"]  # Either is acceptable