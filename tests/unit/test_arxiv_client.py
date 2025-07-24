"""
Test-Driven Development: ArXiv API Client Tests

Testing real ArXiv API integration with production patterns:
1. Write tests first (RED phase)
2. Implement minimal code (GREEN phase)
3. Refactor for quality (REFACTOR phase)
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from typing import List

from src.integrations.academic_apis.arxiv_client import (
    ArXivClient, ArXivPaper, ArXivSearchResult
)
from src.core.circuit_breaker import CircuitBreaker
from src.core.api_rate_limiter import APIRateLimiter, RateLimitConfig
from src.core.exceptions import ServiceUnavailableError


class TestArXivPaper:
    """Test ArXiv paper data model"""
    
    def test_arxiv_paper_creation(self):
        """Test: ArXiv paper data structure is created correctly"""
        paper = ArXivPaper(
            arxiv_id="2023.12345",
            title="Test Paper Title",
            authors=["John Doe", "Jane Smith"],
            abstract="This is a test abstract",
            categories=["cs.AI", "cs.LG"],
            published=datetime(2023, 1, 15),
            pdf_url="https://arxiv.org/pdf/2023.12345.pdf",
            citation_count=42,
            references=["ref1", "ref2"]
        )
        
        assert paper.arxiv_id == "2023.12345"
        assert paper.title == "Test Paper Title"
        assert len(paper.authors) == 2
        assert paper.authors[0] == "John Doe"
        assert paper.citation_count == 42
        assert len(paper.references) == 2
    
    def test_arxiv_paper_validation(self):
        """Test: ArXiv paper validates required fields"""
        # Should not raise exception with valid data
        paper = ArXivPaper(
            arxiv_id="2023.12345",
            title="Valid Title",
            authors=["Author One"],
            abstract="Valid abstract",
            categories=["cs.AI"],
            published=datetime.now(),
            pdf_url="https://arxiv.org/pdf/2023.12345.pdf",
            citation_count=0,
            references=[]
        )
        
        assert paper.arxiv_id == "2023.12345"


class TestArXivClient:
    """Test suite for ArXiv API client implementation"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for ArXiv API"""
        return APIRateLimiter({
            'arxiv': RateLimitConfig(
                requests_per_second=3.0,
                requests_per_minute=10,
                burst_capacity=5
            )
        })
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker for ArXiv API"""
        return CircuitBreaker(
            name="arxiv_api",
            failure_threshold=3,
            timeout_seconds=30.0,
            recovery_timeout=60.0
        )
    
    @pytest.fixture
    def arxiv_client(self, rate_limiter, circuit_breaker):
        """Create ArXiv client with dependencies"""
        return ArXivClient(
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    def test_arxiv_client_initialization(self, arxiv_client):
        """Test: ArXiv client initializes correctly"""
        assert arxiv_client.base_url == "http://export.arxiv.org/api/query"
        assert arxiv_client.rate_limiter is not None
        assert arxiv_client.circuit_breaker is not None
        assert arxiv_client.session is None  # Not initialized yet
    
    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self, arxiv_client):
        """Test: ArXiv client context manager lifecycle"""
        async with arxiv_client as client:
            assert client.session is not None
            assert isinstance(client.session, aiohttp.ClientSession)
        
        # Session should be closed after context
        assert client.session.closed
    
    @pytest.mark.asyncio
    async def test_search_papers_with_valid_query(self, arxiv_client):
        """Test: Search papers with valid query returns results"""
        mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2023.12345v1</id>
                <title>Test Machine Learning Paper</title>
                <author><name>John Doe</name></author>
                <author><name>Jane Smith</name></author>
                <summary>This is a test abstract about machine learning.</summary>
                <category term="cs.LG" />
                <category term="cs.AI" />
                <published>2023-01-15T00:00:00Z</published>
                <link href="http://arxiv.org/pdf/2023.12345v1.pdf" type="application/pdf" />
            </entry>
        </feed>'''
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_xml_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                results = await client.search_papers("machine learning", max_results=10)
            
            assert isinstance(results, ArXivSearchResult)
            assert len(results.papers) == 1
            
            paper = results.papers[0]
            assert paper.arxiv_id == "2023.12345"
            assert paper.title == "Test Machine Learning Paper"
            assert len(paper.authors) == 2
            assert "John Doe" in paper.authors
            assert "cs.LG" in paper.categories
    
    @pytest.mark.asyncio
    async def test_search_papers_handles_api_errors(self, arxiv_client):
        """Test: Search papers handles API errors gracefully"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                with pytest.raises(ServiceUnavailableError) as exc_info:
                    await client.search_papers("test query")
                
                assert "ArXiv API error: 500" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_papers_respects_rate_limits(self, arxiv_client):
        """Test: Search papers respects rate limits"""
        mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
        </feed>'''
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_xml_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                # Make multiple requests to trigger rate limiting
                tasks = []
                for i in range(3):
                    task = client.search_papers(f"query {i}", max_results=1)
                    tasks.append(task)
                
                # Should complete without errors (rate limiter handles delays)
                results = await asyncio.gather(*tasks)
                assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_download_pdf_success(self, arxiv_client):
        """Test: PDF download works correctly"""
        mock_pdf_content = b"Mock PDF content here"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.read = AsyncMock(return_value=mock_pdf_content)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                pdf_content = await client.download_pdf("2023.12345")
            
            assert pdf_content == mock_pdf_content
            mock_get.assert_called_once_with("https://arxiv.org/pdf/2023.12345.pdf")
    
    @pytest.mark.asyncio
    async def test_download_pdf_handles_errors(self, arxiv_client):
        """Test: PDF download handles errors"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                with pytest.raises(ServiceUnavailableError) as exc_info:
                    await client.download_pdf("nonexistent.12345")
                
                assert "PDF download failed: 404" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, arxiv_client):
        """Test: Search with category and date filters"""
        mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
        </feed>'''
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_xml_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                await client.search_papers(
                    query="machine learning",
                    categories=["cs.LG", "cs.AI"],
                    max_results=50,
                    sort_by="submittedDate",
                    sort_order="descending"
                )
            
            # Verify the API call was made with correct parameters
            call_args = mock_get.call_args
            assert "search_query" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_get_paper_metadata(self, arxiv_client):
        """Test: Get metadata for specific paper"""
        mock_xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2023.12345v1</id>
                <title>Specific Paper Title</title>
                <author><name>Author Name</name></author>
                <summary>Paper abstract</summary>
                <category term="cs.AI" />
                <published>2023-01-15T00:00:00Z</published>
            </entry>
        </feed>'''
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_xml_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                paper = await client.get_paper_metadata("2023.12345")
            
            assert paper.arxiv_id == "2023.12345"
            assert paper.title == "Specific Paper Title"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, arxiv_client):
        """Test: Circuit breaker protects against repeated failures"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Make requests fail consistently
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Server Error")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with arxiv_client as client:
                # First few failures should raise ServiceUnavailableError
                for i in range(3):
                    with pytest.raises(ServiceUnavailableError):
                        await client.search_papers("test query")
                
                # After threshold, should get CircuitBreakerError
                from src.core.exceptions import CircuitBreakerError
                with pytest.raises(CircuitBreakerError):
                    await client.search_papers("test query")


class TestArXivIntegration:
    """Integration tests for ArXiv client with real patterns"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test: Complete workflow from search to PDF download"""
        # This would be a real integration test in production
        # For now, we'll mock the responses to test the workflow
        
        rate_limiter = APIRateLimiter({
            'arxiv': RateLimitConfig(requests_per_second=1.0, burst_capacity=3)
        })
        circuit_breaker = CircuitBreaker("arxiv_test", failure_threshold=2)
        
        client = ArXivClient(
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
        
        mock_search_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2023.test</id>
                <title>Integration Test Paper</title>
                <author><name>Test Author</name></author>
                <summary>Test abstract</summary>
                <category term="cs.AI" />
                <published>2023-01-01T00:00:00Z</published>
            </entry>
        </feed>'''
        
        mock_pdf_content = b"Mock PDF for integration test"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Create a single mock response that works for both calls
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_search_response)
            mock_response.read = AsyncMock(return_value=mock_pdf_content)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with client:
                # 1. Search for papers
                search_results = await client.search_papers("test query")
                assert len(search_results.papers) == 1
                
                # 2. Download PDF for first result
                paper = search_results.papers[0]
                pdf_content = await client.download_pdf(paper.arxiv_id)
                assert pdf_content == mock_pdf_content
                
                # 3. Get additional metadata
                metadata = await client.get_paper_metadata(paper.arxiv_id)
                assert metadata.title == "Integration Test Paper"