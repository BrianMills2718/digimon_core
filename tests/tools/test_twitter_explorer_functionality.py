"""
TwitterExplorer Tool Functionality Tests

TDD Phase 3: Core functionality tests
These tests validate the tool's business logic and Twitter-specific functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from datetime import datetime

from src.tools.base_tool import ToolRequest, ToolResult


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


@pytest.fixture
def mock_service_manager():
    """Create comprehensive mock service manager"""
    service_manager = Mock()
    
    # Mock identity service
    identity_service = Mock()
    identity_service.create_entity.return_value = Mock(
        success=True, 
        data={"entity_id": "test_entity_id", "mention_id": "test_mention_id"}
    )
    identity_service.create_mention.return_value = Mock(
        success=True,
        data={"mention_id": "test_mention_id", "entity_id": "test_entity_id"}
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
    
    return service_manager


@pytest.fixture
def mock_twitter_api_responses():
    """Mock Twitter API responses for testing"""
    return {
        "screenname_response": {
            "profile": "github",
            "name": "GitHub",
            "description": "How people build software.",
            "followers": 2500000,
            "friends": 350,
            "verified": True,
            "rest_id": "13334762"
        },
        "timeline_response": {
            "timeline": [
                {
                    "tweet_id": "1234567890",
                    "text": "Great new feature release!",
                    "author": {"screen_name": "github", "rest_id": "13334762"},
                    "created_at": "2025-01-15T12:00:00Z",
                    "retweets_count": 150,
                    "likes_count": 500
                }
            ]
        },
        "followers_response": {
            "followers": [
                {
                    "screen_name": "developer1",
                    "name": "Developer One", 
                    "rest_id": "11111111",
                    "description": "Software developer"
                },
                {
                    "screen_name": "developer2",
                    "name": "Developer Two",
                    "rest_id": "22222222", 
                    "description": "Open source contributor"
                }
            ]
        }
    }


class TestTwitterQueryProcessing:
    """Test Twitter query processing logic"""
    
    def test_simple_user_profile_query(self, mock_service_manager, mock_twitter_api_responses):
        """Test processing simple user profile query"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Tell me about the user @github")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            # Mock query planning
            mock_plan.return_value = {
                "response_type": "PLAN",
                "api_plan": [
                    {
                        "step": 1,
                        "endpoint": "screenname.php",
                        "params": {"screenname": "github"},
                        "reason": "Get user profile information"
                    }
                ]
            }
            
            # Mock API execution
            mock_execute.return_value = [mock_twitter_api_responses["screenname_response"]]
            
            # Mock graph building
            mock_graph.return_value = {
                "nodes": [{"id": "github", "type": "TwitterUser", "properties": {"name": "GitHub"}}],
                "edges": [],
                "metadata": {"node_count": 1, "edge_count": 0, "connected_components": 1}
            }
            
            result = tool.execute(request)
            
            assert result.status == "success"
            assert "entities" in result.data
            assert len(result.data["entities"]) > 0
            
            # Should extract user entity
            user_entities = [e for e in result.data["entities"] if e["entity_type"] == "TwitterUser"]
            assert len(user_entities) == 1
            assert user_entities[0]["canonical_name"] == "github"
            assert user_entities[0]["confidence"] > 0.8
    
    def test_complex_multi_step_query(self, mock_service_manager, mock_twitter_api_responses):
        """Test multi-step query requiring API orchestration"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request(
            "Find recent followers of @github and tell me their bios",
            max_results=10
        )
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            # Mock complex query planning
            mock_plan.return_value = {
                "response_type": "PLAN",
                "api_plan": [
                    {
                        "step": 1,
                        "endpoint": "screenname.php",
                        "params": {"screenname": "github"},
                        "reason": "Get GitHub user information"
                    },
                    {
                        "step": 2,
                        "endpoint": "followers.php",
                        "params": {"screenname": "github", "max_pages": 1},
                        "reason": "Get recent followers"
                    }
                ]
            }
            
            # Mock multi-step API execution
            mock_execute.return_value = [
                mock_twitter_api_responses["screenname_response"],
                mock_twitter_api_responses["followers_response"] 
            ]
            
            # Mock graph with relationships
            mock_graph.return_value = {
                "nodes": [
                    {"id": "github", "type": "TwitterUser"},
                    {"id": "developer1", "type": "TwitterUser"},
                    {"id": "developer2", "type": "TwitterUser"}
                ],
                "edges": [
                    {"source": "developer1", "target": "github", "type": "FOLLOWS"},
                    {"source": "developer2", "target": "github", "type": "FOLLOWS"}
                ],
                "metadata": {"node_count": 3, "edge_count": 2, "connected_components": 1}
            }
            
            result = tool.execute(request)
            
            assert result.status == "success"
            
            # Should have multiple entities (github + followers)
            assert len(result.data["entities"]) >= 3
            
            # Should have relationships (follows relationships)
            assert len(result.data["relationships"]) >= 2
            follow_rels = [r for r in result.data["relationships"] if r["relationship_type"] == "FOLLOWS"]
            assert len(follow_rels) >= 2
            
            # Should have generated summary
            assert len(result.data["summary"]) > 0
            assert "followers" in result.data["summary"].lower()
    
    @pytest.mark.parametrize("query,expected_entities,expected_relationships", [
        ("What are @nasa's recent tweets?", ["TwitterUser", "Tweet"], ["POSTED"]),
        ("Who follows @elonmusk?", ["TwitterUser"], ["FOLLOWS"]),
        ("Show me replies to tweet 123456", ["Tweet", "TwitterUser"], ["REPLIES_TO"]),
        ("Find users who retweeted this tweet", ["TwitterUser", "Tweet"], ["RETWEETS"]),
    ])
    def test_query_types_extract_correct_entities(self, query, expected_entities, expected_relationships, 
                                                 mock_service_manager):
        """Test different query types extract expected entity and relationship types"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request(query)
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            # Mock appropriate plan for each query type
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = []
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            # Mock entity extraction based on query type
            mock_entities = []
            mock_relationships = []
            
            for entity_type in expected_entities:
                mock_entities.append({
                    "entity_id": f"test_{entity_type.lower()}",
                    "entity_type": entity_type,
                    "surface_form": f"Test {entity_type}",
                    "canonical_name": f"test_{entity_type.lower()}",
                    "confidence": 0.9,
                    "metadata": {}
                })
            
            for rel_type in expected_relationships:
                mock_relationships.append({
                    "relationship_id": f"test_{rel_type.lower()}",
                    "source_entity_id": "test_source",
                    "target_entity_id": "test_target", 
                    "relationship_type": rel_type,
                    "confidence": 0.9,
                    "metadata": {}
                })
            
            with patch.object(tool, '_extract_entities_from_results') as mock_extract_entities, \
                 patch.object(tool, '_extract_relationships_from_results') as mock_extract_rels:
                
                mock_extract_entities.return_value = mock_entities
                mock_extract_rels.return_value = mock_relationships
                
                result = tool.execute(request)
                
                assert result.status == "success"
                
                extracted_entity_types = {e["entity_type"] for e in result.data["entities"]}
                for expected_type in expected_entities:
                    assert expected_type in extracted_entity_types
                
                extracted_rel_types = {r["relationship_type"] for r in result.data["relationships"]}
                for expected_type in expected_relationships:
                    assert expected_type in extracted_rel_types
    
    def test_query_complexity_assessment(self, mock_service_manager):
        """Test query complexity is properly assessed"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        simple_queries = [
            "Tell me about @github",
            "What is @nasa's bio?",
        ]
        
        complex_queries = [
            "Find all followers of @github who also follow @microsoft and analyze their tweet patterns",
            "Show me the conversation threads for all replies to @elonmusk's last 10 tweets",
        ]
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            mock_execute.return_value = []
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            # Test simple queries
            for query in simple_queries:
                mock_plan.return_value = {
                    "response_type": "PLAN", 
                    "api_plan": [{"step": 1, "endpoint": "screenname.php"}]
                }
                
                request = create_test_request(query)
                result = tool.execute(request)
                
                complexity = result.data["processing_stats"]["query_complexity_score"]
                assert 0.0 <= complexity <= 0.5, f"Simple query should have low complexity: {complexity}"
            
            # Test complex queries
            for query in complex_queries:
                mock_plan.return_value = {
                    "response_type": "PLAN",
                    "api_plan": [
                        {"step": 1, "endpoint": "followers.php"},
                        {"step": 2, "endpoint": "following.php"},
                        {"step": 3, "endpoint": "timeline.php"},
                        {"step": 4, "endpoint": "replies.php"}
                    ]
                }
                
                request = create_test_request(query)
                result = tool.execute(request)
                
                complexity = result.data["processing_stats"]["query_complexity_score"]
                assert 0.7 <= complexity <= 1.0, f"Complex query should have high complexity: {complexity}"


class TestTwitterServiceIntegration:
    """Test integration with KGAS core services"""
    
    def test_identity_service_entity_creation(self, mock_service_manager):
        """Test Twitter entities registered with Identity Service"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Tell me about @github")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = [{"profile": "github", "name": "GitHub"}]
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            result = tool.execute(request)
            
            # Should have called Identity Service to create entities
            assert mock_service_manager.identity_service.create_entity.called
            calls = mock_service_manager.identity_service.create_entity.call_args_list
            
            # Should create TwitterUser entity
            user_call = None
            for call in calls:
                if call[1]["entity_type"] == "TwitterUser":
                    user_call = call
                    break
            
            assert user_call is not None, "Should create TwitterUser entity"
            assert user_call[1]["surface_form"] == "github"
    
    def test_provenance_service_tracking(self, mock_service_manager):
        """Test all operations tracked via Provenance Service"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Test query")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = []
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            result = tool.execute(request)
            
            # Should log execution steps
            assert mock_service_manager.provenance_service.log_execution.call_count >= 1
            
            # Check that main execution was logged
            calls = mock_service_manager.provenance_service.log_execution.call_args_list
            main_call = calls[0]
            
            assert main_call[1]["operation"] == "twitter_query_execution"
            assert "inputs" in main_call[1]
            assert "outputs" in main_call[1]
    
    def test_quality_service_confidence_assessment(self, mock_service_manager):
        """Test quality service used for confidence assessment"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Test query")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = [{"profile": "test_user"}]
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            result = tool.execute(request)
            
            # Should assess confidence for extracted entities
            if result.data["entities"]:
                assert mock_service_manager.quality_service.assess_confidence.called
    
    def test_graph_data_neo4j_format(self, mock_service_manager):
        """Test output produces data suitable for Neo4j storage"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Find followers of @github")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute:
            
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = []
            
            result = tool.execute(request)
            
            assert result.status == "success"
            graph_data = result.data["graph_data"]
            
            # Should have nodes and edges in Neo4j format
            assert "nodes" in graph_data
            assert "edges" in graph_data
            assert "metadata" in graph_data
            
            # Nodes should have Neo4j-compatible structure
            for node in graph_data["nodes"]:
                assert "id" in node
                # Neo4j nodes should have type/label information
                assert any(key in node for key in ["type", "labels", "label"])
            
            # Edges should have source/target structure
            for edge in graph_data["edges"]:
                assert "source" in edge
                assert "target" in edge
                assert "type" in edge


class TestTwitterErrorHandling:
    """Test comprehensive error handling"""
    
    def test_invalid_api_keys_handling(self, mock_service_manager):
        """Test handling of invalid API credentials"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = ToolRequest(
            tool_id="T85_TWITTER_EXPLORER",
            operation="query",
            input_data={
                "query": "Test query",
                "api_keys": {"gemini_key": "invalid", "rapidapi_key": "invalid"}
            },
            parameters={}
        )
        
        with patch.object(tool, '_plan_query_execution') as mock_plan:
            # Mock API authentication failure
            mock_plan.side_effect = Exception("Invalid API credentials")
            
            result = tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["INVALID_API_CREDENTIALS", "API_AUTHENTICATION_FAILED"]
            assert "api" in result.error_message.lower() or "credential" in result.error_message.lower()
    
    def test_rate_limit_handling(self, mock_service_manager):
        """Test API rate limit error handling"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Test query")
        
        with patch.object(tool, '_execute_api_plan') as mock_execute:
            # Mock rate limit error
            mock_execute.side_effect = Exception("Rate limit exceeded")
            
            result = tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "RATE_LIMIT_EXCEEDED"
            assert "rate limit" in result.error_message.lower()
    
    def test_malformed_query_handling(self, mock_service_manager):
        """Test handling of malformed or unclear queries"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        
        unclear_queries = [
            "",  # Empty query
            "asdfkjasdf",  # Nonsense
            "Show me the thing about the stuff",  # Too vague
            "a" * 1000,  # Too long
        ]
        
        for query in unclear_queries:
            request = create_test_request(query)
            result = tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["INVALID_QUERY", "QUERY_TOO_VAGUE", "QUERY_TOO_COMPLEX"]
            assert result.error_message is not None
    
    def test_api_timeout_handling(self, mock_service_manager):
        """Test API timeout error handling"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Test query", timeout_seconds=1)
        
        with patch.object(tool, '_execute_api_plan') as mock_execute:
            # Mock timeout error
            import socket
            mock_execute.side_effect = socket.timeout("API request timed out")
            
            result = tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "API_TIMEOUT"
            assert "timeout" in result.error_message.lower()
    
    def test_graceful_degradation_on_partial_failure(self, mock_service_manager):
        """Test graceful degradation when some API calls fail"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        request = create_test_request("Complex multi-step query")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute:
            
            # Mock complex plan
            mock_plan.return_value = {
                "response_type": "PLAN",
                "api_plan": [
                    {"step": 1, "endpoint": "screenname.php"},
                    {"step": 2, "endpoint": "followers.php"},
                    {"step": 3, "endpoint": "timeline.php"}
                ]
            }
            
            # Mock partial success (first call succeeds, others fail)
            mock_execute.return_value = [
                {"profile": "test_user", "name": "Test User"},  # Success
                {"error": "Rate limit exceeded"},  # Failure
                {"error": "API timeout"}  # Failure
            ]
            
            result = tool.execute(request)
            
            # Should return partial results, not complete failure
            assert result.status == "success"  # Partial success is still success
            assert len(result.data["entities"]) > 0  # Should have some entities
            assert "partial" in result.data["summary"].lower()  # Should indicate partial results


class TestTwitterPerformanceRequirements:
    """Test performance requirements from contract"""
    
    def test_execution_time_within_limits(self, mock_service_manager):
        """Test tool meets max execution time requirements"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        contract = tool.get_contract()
        max_time = contract.performance_requirements["max_execution_time"]
        
        request = create_test_request("Quick test query")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = []
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            start_time = time.time()
            result = tool.execute(request)
            execution_time = time.time() - start_time
            
            assert execution_time <= max_time
            assert result.execution_time <= max_time
    
    def test_memory_usage_within_limits(self, mock_service_manager):
        """Test memory usage stays within contract limits"""  
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        contract = tool.get_contract()
        max_memory = contract.performance_requirements["max_memory_mb"] * 1024 * 1024
        
        request = create_test_request("Memory test query")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute, \
             patch.object(tool, '_build_graph_data') as mock_graph:
            
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": []}
            mock_execute.return_value = []
            mock_graph.return_value = {"nodes": [], "edges": [], "metadata": {}}
            
            import psutil
            process = psutil.Process()
            start_memory = process.memory_info().rss
            
            result = tool.execute(request)
            
            end_memory = process.memory_info().rss
            memory_used = end_memory - start_memory
            
            # Memory usage should be reasonable (allowing for test overhead)
            assert memory_used <= max_memory * 2  # Allow 2x for test overhead
            assert result.memory_used >= 0
    
    def test_api_call_limits_respected(self, mock_service_manager):
        """Test tool respects API call limits"""
        from src.tools.phase1.t85_twitter_explorer import TwitterExplorerTool
        
        tool = TwitterExplorerTool(mock_service_manager)
        contract = tool.get_contract()
        max_api_calls = contract.performance_requirements["max_api_calls_per_query"]
        
        request = create_test_request("Complex query that might require many API calls")
        
        with patch.object(tool, '_plan_query_execution') as mock_plan, \
             patch.object(tool, '_execute_api_plan') as mock_execute:
            
            # Mock plan with many API calls
            api_plan = [{"step": i, "endpoint": f"endpoint_{i}.php"} for i in range(max_api_calls + 5)]
            mock_plan.return_value = {"response_type": "PLAN", "api_plan": api_plan}
            mock_execute.return_value = []
            
            result = tool.execute(request)
            
            # Should limit API calls or return appropriate error
            if result.status == "success":
                actual_calls = result.data["processing_stats"]["total_api_calls"]
                assert actual_calls <= max_api_calls
            else:
                assert result.error_code == "QUERY_TOO_COMPLEX"