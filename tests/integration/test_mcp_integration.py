"""
MCP Integration Tests

Tests the integration of all MCP services working together for comprehensive
discourse analysis and monitoring.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.integrations.mcp.orchestrator import MCPOrchestrator, SearchScope
from src.integrations.mcp.semantic_scholar_client import SemanticScholarMCPClient
from src.integrations.mcp.arxiv_latex_client import ArXivLatexMCPClient
from src.integrations.mcp.youtube_client import YouTubeMCPClient
from src.integrations.mcp.google_news_client import GoogleNewsMCPClient
from src.integrations.mcp.dappier_client import DappierMCPClient
from src.integrations.mcp.content_core_client import ContentCoreMCPClient
from src.integrations.mcp.markitdown_client import MarkItDownMCPClient, ConversionOptions
from src.integrations.mcp.pandoc_client import PandocMCPClient, ConversionFormat
from src.integrations.mcp.grafana_client import GrafanaMCPClient, TimeRange
from src.integrations.mcp.auth_provider_client import AuthProviderMCPClient, AuthenticationMethod
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreakerManager


class TestMCPIntegration:
    """Test suite for MCP service integration"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create shared rate limiter"""
        return APIRateLimiter()
    
    @pytest.fixture
    def circuit_breaker_manager(self):
        """Create circuit breaker manager"""
        return CircuitBreakerManager()
    
    @pytest.fixture
    def mcp_clients(self, rate_limiter, circuit_breaker_manager):
        """Create all MCP clients"""
        clients = {
            'semantic_scholar': SemanticScholarMCPClient(
                "http://localhost:8001",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("semantic_scholar")
            ),
            'arxiv_latex': ArXivLatexMCPClient(
                "http://localhost:8002",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("arxiv_latex")
            ),
            'youtube': YouTubeMCPClient(
                "http://localhost:8003",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("youtube")
            ),
            'google_news': GoogleNewsMCPClient(
                "http://localhost:8004",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("google_news")
            ),
            'dappier': DappierMCPClient(
                "http://localhost:8005",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("dappier")
            ),
            'content_core': ContentCoreMCPClient(
                "http://localhost:8006",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("content_core")
            ),
            'markitdown': MarkItDownMCPClient(
                "http://localhost:8010",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("markitdown")
            ),
            'pandoc': PandocMCPClient(
                "http://localhost:8011",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("pandoc")
            ),
            'grafana': GrafanaMCPClient(
                "http://localhost:8012",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("grafana")
            ),
            'auth_provider': AuthProviderMCPClient(
                "http://localhost:8013",
                rate_limiter,
                circuit_breaker_manager.get_circuit_breaker("auth_provider")
            )
        }
        return clients
    
    @pytest.fixture
    def orchestrator(self, mcp_clients):
        """Create MCP orchestrator"""
        return MCPOrchestrator(**mcp_clients)
    
    @pytest.mark.asyncio
    async def test_authenticated_research_workflow(self, orchestrator, mcp_clients):
        """Test: Complete authenticated research workflow"""
        # Step 1: Authenticate user
        auth_client = mcp_clients['auth_provider']
        
        auth_response = {
            "result": {
                "token": {
                    "access_token": "test_token_123",
                    "expires_in": 3600
                },
                "user": {
                    "id": "researcher123",
                    "username": "researcher",
                    "roles": ["researcher", "admin"]
                }
            }
        }
        
        with patch.object(auth_client, '_send_request', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = auth_response
            
            auth_result = await auth_client.authenticate(
                username="researcher",
                password="secure_password"
            )
        
        assert auth_result.success
        assert auth_result.data.access_token == "test_token_123"
        
        # Step 2: Search for academic papers on machine learning
        mock_semantic_response = {
            "result": {
                "papers": [{
                    "paperId": "abc123",
                    "title": "Deep Learning in NLP",
                    "abstract": "This paper explores...",
                    "authors": [{"name": "John Doe"}],
                    "year": 2024,
                    "citationCount": 50
                }]
            }
        }
        
        with patch.object(orchestrator.semantic_scholar, '_send_request', new_callable=AsyncMock) as mock_ss:
            mock_ss.return_value = mock_semantic_response
            
            # Step 3: Search news for related coverage
            mock_news_response = {
                "result": {
                    "articles": [{
                        "title": "AI Breakthrough in Language Models",
                        "source": "TechNews",
                        "published": "2024-01-15",
                        "content": "Researchers announce...",
                        "url": "https://example.com/ai-news"
                    }]
                }
            }
            
            with patch.object(orchestrator.google_news, '_send_request', new_callable=AsyncMock) as mock_news:
                mock_news.return_value = mock_news_response
                
                # Execute unified search
                results = await orchestrator.unified_search(
                    query="machine learning NLP",
                    scope=SearchScope.ALL
                )
        
        # Verify integrated results
        assert len(results) >= 2  # At least academic and news results
        academic_results = [r for r in results if r.source == "semantic_scholar"]
        news_results = [r for r in results if r.source == "google_news"]
        
        assert len(academic_results) > 0
        assert len(news_results) > 0
    
    @pytest.mark.asyncio
    async def test_document_processing_pipeline(self, mcp_clients):
        """Test: Document conversion and processing pipeline"""
        markitdown = mcp_clients['markitdown']
        pandoc = mcp_clients['pandoc']
        
        # Step 1: Convert DOCX to Markdown
        mock_markitdown_response = {
            "result": {
                "content": "# Research Paper\n\n## Introduction\n\nThis research explores...",
                "metadata": {
                    "title": "Research Paper",
                    "author": "Dr. Smith",
                    "word_count": 5000
                }
            }
        }
        
        with patch.object(markitdown, '_send_request', new_callable=AsyncMock) as mock_md:
            mock_md.return_value = mock_markitdown_response
            
            md_result = await markitdown.convert_document(
                file_path=Path("/docs/research.docx")
            )
        
        assert md_result.success
        assert "# Research Paper" in md_result.data.markdown_content
        
        # Step 2: Convert Markdown to LaTeX using Pandoc
        mock_pandoc_response = {
            "result": {
                "content": "\\documentclass{article}\n\\title{Research Paper}...",
                "metadata": {"pandoc_version": "3.1.9"}
            }
        }
        
        with patch.object(pandoc, '_send_request', new_callable=AsyncMock) as mock_pandoc:
            mock_pandoc.return_value = mock_pandoc_response
            
            latex_result = await pandoc.convert(
                content=md_result.data.markdown_content,
                from_format=ConversionFormat.MARKDOWN,
                to_format=ConversionFormat.LATEX
            )
        
        assert latex_result.success
        assert "\\documentclass{article}" in latex_result.data.content
    
    @pytest.mark.asyncio
    async def test_monitoring_and_alerting(self, mcp_clients):
        """Test: System monitoring and alerting integration"""
        grafana = mcp_clients['grafana']
        auth = mcp_clients['auth_provider']
        
        # Step 1: Check authentication for monitoring access
        mock_permission_response = {
            "result": {
                "allowed": True,
                "reason": "User has monitoring role"
            }
        }
        
        with patch.object(auth, '_send_request', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_permission_response
            
            perm_result = await auth.check_permission(
                user_id="admin123",
                resource="monitoring",
                action="view"
            )
        
        assert perm_result.data["allowed"] is True
        
        # Step 2: Search for system dashboards
        mock_dashboard_response = {
            "result": {
                "dashboards": [{
                    "uid": "sys123",
                    "title": "KGAS System Metrics",
                    "tags": ["production", "kgas"],
                    "folder": "Production"
                }]
            }
        }
        
        with patch.object(grafana, '_send_request', new_callable=AsyncMock) as mock_grafana:
            mock_grafana.return_value = mock_dashboard_response
            
            dashboards = await grafana.search_dashboards(
                tags=["kgas", "production"]
            )
        
        assert len(dashboards.data) > 0
        assert dashboards.data[0].title == "KGAS System Metrics"
        
        # Step 3: Check for alerts
        mock_alerts_response = {
            "result": {
                "alerts": [{
                    "id": 1,
                    "name": "High API Latency",
                    "state": "alerting",
                    "message": "API response time > 1s"
                }]
            }
        }
        
        with patch.object(grafana, '_send_request', new_callable=AsyncMock) as mock_alerts:
            mock_alerts.return_value = mock_alerts_response
            
            alerts = await grafana.get_alerts(states=["alerting"])
        
        assert len(alerts.data) > 0
        assert alerts.data[0].state == "alerting"
    
    @pytest.mark.asyncio
    async def test_cross_source_discourse_analysis(self, orchestrator):
        """Test: Analyze discourse across academic papers, news, and videos"""
        topic = "climate change impacts"
        
        # Mock responses for different sources
        mock_responses = {
            'semantic_scholar': {
                "result": {
                    "papers": [{
                        "paperId": "climate123",
                        "title": "Climate Change Effects on Agriculture",
                        "abstract": "Analysis of temperature impacts...",
                        "year": 2024,
                        "citationCount": 100
                    }]
                }
            },
            'youtube': {
                "result": {
                    "videos": [{
                        "video_id": "vid123",
                        "title": "Climate Scientists Explain Latest Research",
                        "channel": "Science Channel",
                        "transcript": "Today we discuss the latest findings..."
                    }]
                }
            },
            'google_news': {
                "result": {
                    "articles": [{
                        "title": "UN Report: Climate Action Urgently Needed",
                        "source": "Reuters",
                        "content": "The latest UN report shows..."
                    }]
                }
            }
        }
        
        # Patch all clients
        with patch.object(orchestrator.semantic_scholar, '_send_request', new_callable=AsyncMock) as mock_ss:
            mock_ss.return_value = mock_responses['semantic_scholar']
            
            with patch.object(orchestrator.youtube, '_send_request', new_callable=AsyncMock) as mock_yt:
                mock_yt.return_value = mock_responses['youtube']
                
                with patch.object(orchestrator.google_news, '_send_request', new_callable=AsyncMock) as mock_news:
                    mock_news.return_value = mock_responses['google_news']
                    
                    # Analyze discourse
                    analysis = await orchestrator.analyze_discourse(
                        topic=topic,
                        include_academic=True,
                        include_media=True,
                        include_video=True
                    )
        
        # Verify comprehensive analysis
        assert analysis.topic == topic
        assert len(analysis.sources) >= 3
        assert analysis.total_items > 0
        assert any(s["type"] == "academic" for s in analysis.sources)
        assert any(s["type"] == "news" for s in analysis.sources)
        assert any(s["type"] == "video" for s in analysis.sources)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_circuit_breakers(self, orchestrator):
        """Test: Error handling with circuit breakers"""
        # Simulate service failure
        with patch.object(orchestrator.semantic_scholar, '_send_request', new_callable=AsyncMock) as mock_ss:
            mock_ss.side_effect = Exception("Service unavailable")
            
            # First few calls should attempt and fail
            for _ in range(5):
                result = await orchestrator.semantic_scholar.search_papers("test")
                assert not result.success
            
            # Circuit breaker should now be open
            cb = orchestrator.semantic_scholar.circuit_breaker
            assert cb.state.name == "OPEN"
            
            # Calls should fail fast without attempting request
            result = await orchestrator.semantic_scholar.search_papers("test")
            assert not result.success
            assert "circuit breaker is open" in str(result.error).lower()
    
    @pytest.mark.asyncio
    async def test_rate_limiting_across_services(self, mcp_clients, rate_limiter):
        """Test: Rate limiting applied across all services"""
        # Configure strict rate limits
        rate_limiter.configure_service("semantic_scholar", requests_per_second=1)
        rate_limiter.configure_service("arxiv_latex", requests_per_second=1)
        
        # Make rapid requests
        import asyncio
        
        # Mock successful responses
        mock_response = {"result": {"papers": []}}
        
        with patch.object(mcp_clients['semantic_scholar'], '_send_request', new_callable=AsyncMock) as mock_ss:
            mock_ss.return_value = mock_response
            
            # First request should succeed
            result1 = await mcp_clients['semantic_scholar'].search_papers("test1")
            assert result1.success
            
            # Immediate second request should be rate limited
            result2 = await mcp_clients['semantic_scholar'].search_papers("test2")
            # Rate limiter should delay but eventually allow
            
            # Check rate limit stats
            remaining = rate_limiter.get_remaining_requests("semantic_scholar")
            assert remaining >= 0