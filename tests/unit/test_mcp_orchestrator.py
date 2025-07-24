"""
Tests for MCP Orchestrator

Tests the coordination between multiple MCP servers for discourse analysis.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.integrations.mcp.orchestrator import (
    MCPOrchestrator, SearchScope, UnifiedSearchResult, DiscourseAnalysisResult
)
from src.integrations.mcp.base_client import MCPResponse
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreakerManager


class TestMCPOrchestrator:
    """Test suite for MCP Orchestrator"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            'enable_semantic_scholar': True,
            'enable_arxiv_latex': True,
            'enable_youtube': True,
            'enable_google_news': True,
            'enable_dappier': True,
            'enable_content_core': True,
            'semantic_scholar_api_key': 'test_key',
            'serp_api_key': 'test_serp_key',
            'dappier_api_key': 'test_dappier_key',
            'openai_api_key': 'test_openai_key'
        }
    
    @pytest.fixture
    def orchestrator(self, config):
        """Create orchestrator with mocked clients"""
        with patch('src.integrations.mcp.orchestrator.SemanticScholarMCPClient'):
            with patch('src.integrations.mcp.orchestrator.ArXivLatexMCPClient'):
                with patch('src.integrations.mcp.orchestrator.YouTubeMCPClient'):
                    with patch('src.integrations.mcp.orchestrator.GoogleNewsMCPClient'):
                        with patch('src.integrations.mcp.orchestrator.DappierMCPClient'):
                            with patch('src.integrations.mcp.orchestrator.ContentCoreMCPClient'):
                                return MCPOrchestrator(config)
    
    @pytest.mark.asyncio
    async def test_unified_search_all_sources(self, orchestrator):
        """Test: Unified search queries all configured sources"""
        # Mock search results from each source
        mock_ss_results = [
            {
                'paperId': '123',
                'title': 'Machine Learning Paper',
                'abstract': 'Abstract about ML',
                'authors': [{'name': 'John Doe'}],
                'year': 2023,
                'citationCount': 100,
                'url': 'https://example.com/paper'
            }
        ]
        
        mock_news_results = [
            {
                'title': 'AI News Article',
                'description': 'News about AI',
                'link': 'https://news.com/ai',
                'source': 'Tech News',
                'published_date': datetime.now().isoformat()
            }
        ]
        
        # Mock client responses
        orchestrator.clients['semantic_scholar'].connect = AsyncMock()
        orchestrator.clients['semantic_scholar'].search_papers = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_ss_results)
        )
        
        orchestrator.clients['google_news'].connect = AsyncMock()
        orchestrator.clients['google_news'].search_news = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_news_results)
        )
        
        # Perform unified search
        results = await orchestrator.unified_search("machine learning", SearchScope.ALL)
        
        # Verify results
        assert len(results) >= 2  # At least one from each source
        assert any(r.source == "semantic_scholar" for r in results)
        assert any(r.source == "google_news" for r in results)
    
    @pytest.mark.asyncio
    async def test_discourse_analysis_comprehensive(self, orchestrator):
        """Test: Discourse analysis aggregates from multiple sources"""
        # Mock responses from different sources
        mock_papers = [MagicMock(
            paper_id='123',
            title='AI Research',
            authors=[{'name': 'Researcher'}],
            year=2023,
            citation_count=50
        )]
        
        mock_news = [MagicMock(
            title='AI News',
            source='News Source',
            published_date=datetime.now()
        )]
        
        # Mock methods
        orchestrator._get_academic_discourse = AsyncMock(return_value=mock_papers)
        orchestrator._aggregate_news_discourse = AsyncMock(return_value=mock_news)
        orchestrator._get_youtube_discourse = AsyncMock(return_value=[])
        orchestrator._analyze_sentiment = AsyncMock(return_value={'positive': 0.7})
        
        # Perform discourse analysis
        result = await orchestrator.analyze_discourse("artificial intelligence", time_range_days=30)
        
        # Verify comprehensive analysis
        assert isinstance(result, DiscourseAnalysisResult)
        assert result.topic == "artificial intelligence"
        assert len(result.academic_papers) > 0
        assert len(result.news_articles) > 0
        assert 'positive' in result.sentiment_analysis
        assert result.trending_score >= 0
    
    @pytest.mark.asyncio
    async def test_extract_mathematical_content(self, orchestrator):
        """Test: Mathematical content extraction from ArXiv"""
        mock_latex_content = MagicMock(
            arxiv_id='2301.00001',
            title='Math Paper',
            main_tex='\\begin{equation}E=mc^2\\end{equation}'
        )
        
        mock_equations = [
            MagicMock(latex_code='E=mc^2', context='Famous equation')
        ]
        
        # Mock ArXiv LaTeX client
        orchestrator.clients['arxiv_latex'].connect = AsyncMock()
        orchestrator.clients['arxiv_latex'].get_latex_source = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_latex_content)
        )
        orchestrator.clients['arxiv_latex'].extract_equations = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_equations)
        )
        orchestrator.clients['arxiv_latex'].extract_theorems_proofs = AsyncMock(
            return_value=MCPResponse(success=True, data=[])
        )
        
        # Extract content
        result = await orchestrator.extract_mathematical_content('2301.00001')
        
        # Verify extraction
        assert 'latex_content' in result
        assert 'equations' in result
        assert len(result['equations']) > 0
    
    @pytest.mark.asyncio
    async def test_transcribe_and_analyze_video(self, orchestrator):
        """Test: Video transcription and analysis"""
        mock_video = MagicMock(
            video_id='abc123',
            title='AI Tutorial',
            transcript_chunks=[
                MagicMock(text='Introduction to machine learning concepts')
            ],
            total_words=1000
        )
        
        mock_summary = {
            'summary': 'Video about machine learning basics',
            'key_points': ['ML concepts', 'Neural networks']
        }
        
        # Mock YouTube client
        orchestrator.clients['youtube'].connect = AsyncMock()
        orchestrator.clients['youtube'].transcribe_video = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_video)
        )
        orchestrator.clients['youtube'].get_transcript_summary = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_summary)
        )
        orchestrator.clients['youtube'].extract_timestamps = AsyncMock(
            return_value=MCPResponse(success=True, data=[])
        )
        
        # Transcribe and analyze
        result = await orchestrator.transcribe_and_analyze_video('https://youtube.com/watch?v=abc123')
        
        # Verify results
        assert 'video' in result
        assert 'summary' in result
        assert result['video'].title == 'AI Tutorial'
        assert result['summary']['summary'] == 'Video about machine learning basics'
    
    @pytest.mark.asyncio
    async def test_comprehensive_news_coverage(self, orchestrator):
        """Test: Comprehensive news coverage from multiple sources"""
        mock_google_headlines = [MagicMock(title='Top Story')]
        mock_google_search = [MagicMock(title='AI Development')]
        mock_dappier_content = [MagicMock(title='Tech Update', domain='technology')]
        
        # Mock news clients
        orchestrator.clients['google_news'].connect = AsyncMock()
        orchestrator.clients['google_news'].get_headlines = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_google_headlines)
        )
        orchestrator.clients['google_news'].search_news = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_google_search)
        )
        orchestrator.clients['google_news'].get_trending_topics = AsyncMock(
            return_value=MCPResponse(success=True, data=[])
        )
        
        orchestrator.clients['dappier'].connect = AsyncMock()
        orchestrator.clients['dappier'].search_content = AsyncMock(
            return_value=MCPResponse(success=True, data=mock_dappier_content)
        )
        orchestrator.clients['dappier'].get_trending_topics = AsyncMock(
            return_value=MCPResponse(success=True, data=[])
        )
        
        # Get comprehensive coverage
        result = await orchestrator.get_comprehensive_news_coverage('artificial intelligence')
        
        # Verify coverage from multiple sources
        assert 'google_news' in result
        assert 'dappier' in result
        assert len(result['google_news']['headlines']) > 0
        assert len(result['google_news']['topic_news']) > 0
        assert len(result['dappier']['content']) > 0
    
    @pytest.mark.asyncio
    async def test_search_scope_filtering(self, orchestrator):
        """Test: Search scope correctly filters sources"""
        # Mock only academic source
        orchestrator.clients['semantic_scholar'].connect = AsyncMock()
        orchestrator.clients['semantic_scholar'].search_papers = AsyncMock(
            return_value=MCPResponse(success=True, data=[])
        )
        
        # Mock news sources should not be called
        orchestrator.clients['google_news'].search_news = AsyncMock()
        orchestrator.clients['dappier'].search_content = AsyncMock()
        
        # Search only academic scope
        await orchestrator.unified_search("test query", SearchScope.ACADEMIC)
        
        # Verify only academic sources were searched
        orchestrator.clients['semantic_scholar'].search_papers.assert_called_once()
        orchestrator.clients['google_news'].search_news.assert_not_called()
        orchestrator.clients['dappier'].search_content.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_unified_search(self, orchestrator):
        """Test: Unified search handles errors gracefully"""
        # Make one source fail
        orchestrator.clients['semantic_scholar'].connect = AsyncMock()
        orchestrator.clients['semantic_scholar'].search_papers = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Other source succeeds
        orchestrator.clients['google_news'].connect = AsyncMock()
        orchestrator.clients['google_news'].search_news = AsyncMock(
            return_value=MCPResponse(success=True, data=[{'title': 'News'}])
        )
        
        # Should still get results from working source
        results = await orchestrator.unified_search("test", SearchScope.ALL)
        
        assert len(results) > 0  # Should have results from Google News
        assert all(r.source != "semantic_scholar" for r in results)  # No results from failed source
    
    @pytest.mark.asyncio
    async def test_cross_reference_detection(self, orchestrator):
        """Test: Cross-reference detection between sources"""
        mock_paper = MagicMock(
            title="Deep Learning Research",
            authors=[{'name': 'Dr. Smith'}]
        )
        
        mock_article = MagicMock(
            title="News: Deep Learning Research Breakthrough",
            description="Dr. Smith's team published new findings"
        )
        
        # Test cross-reference finding
        cross_refs = orchestrator._find_cross_references(
            [mock_paper], [mock_article], []
        )
        
        # Should find references
        assert len(cross_refs) > 0
        assert any(ref['type'] == 'news_cites_paper' for ref in cross_refs)
        assert any(ref['type'] == 'news_mentions_author' for ref in cross_refs)
    
    def test_relevance_score_calculation(self, orchestrator):
        """Test: Relevance score calculation for papers"""
        # High relevance paper
        high_rel_paper = MagicMock(
            title="Machine Learning for Natural Language Processing",
            citation_count=200,
            year=2023
        )
        
        # Low relevance paper
        low_rel_paper = MagicMock(
            title="Unrelated Topic",
            citation_count=5,
            year=2010
        )
        
        # Calculate scores
        high_score = orchestrator._calculate_paper_relevance(high_rel_paper, "machine learning")
        low_score = orchestrator._calculate_paper_relevance(low_rel_paper, "machine learning")
        
        # Verify scoring
        assert high_score > low_score
        assert 0 <= high_score <= 1.0
        assert 0 <= low_score <= 1.0


class TestMCPIntegration:
    """Integration tests for MCP system"""
    
    @pytest.mark.asyncio
    async def test_full_discourse_analysis_workflow(self):
        """Test: Complete discourse analysis workflow"""
        config = {
            'enable_semantic_scholar': True,
            'enable_google_news': True,
            'enable_dappier': False,  # Disable some for simplicity
            'enable_arxiv_latex': False,
            'enable_youtube': False,
            'enable_content_core': False
        }
        
        with patch('src.integrations.mcp.orchestrator.SemanticScholarMCPClient') as MockSS:
            with patch('src.integrations.mcp.orchestrator.GoogleNewsMCPClient') as MockGN:
                # Create orchestrator
                orchestrator = MCPOrchestrator(config)
                
                # Mock client methods
                mock_ss_instance = MockSS.return_value
                mock_ss_instance.connect = AsyncMock()
                mock_ss_instance.search_papers = AsyncMock(
                    return_value=MCPResponse(success=True, data=[])
                )
                
                mock_gn_instance = MockGN.return_value
                mock_gn_instance.connect = AsyncMock()
                mock_gn_instance.search_news = AsyncMock(
                    return_value=MCPResponse(success=True, data=[])
                )
                
                orchestrator.clients['semantic_scholar'] = mock_ss_instance
                orchestrator.clients['google_news'] = mock_gn_instance
                
                # Run discourse analysis
                result = await orchestrator.analyze_discourse(
                    "artificial intelligence ethics",
                    time_range_days=7
                )
                
                # Verify workflow completion
                assert isinstance(result, DiscourseAnalysisResult)
                assert result.topic == "artificial intelligence ethics"
                assert isinstance(result.time_range, dict)
                assert 'start' in result.time_range
                assert 'end' in result.time_range