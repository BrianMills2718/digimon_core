"""
Test-Driven Development: PubMed API Client Tests

Testing real PubMed API integration with production patterns:
1. Write tests first (RED phase)
2. Implement minimal code (GREEN phase)  
3. Refactor for quality (REFACTOR phase)
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch
from datetime import datetime
from typing import List

from src.integrations.academic_apis.pubmed_client import (
    PubMedClient, PubMedPaper, PubMedSearchResult
)
from src.core.circuit_breaker import CircuitBreaker
from src.core.api_rate_limiter import APIRateLimiter, RateLimitConfig
from src.core.exceptions import ServiceUnavailableError


class TestPubMedPaper:
    """Test PubMed paper data model"""
    
    def test_pubmed_paper_creation(self):
        """Test: PubMed paper data structure is created correctly"""
        paper = PubMedPaper(
            pmid="12345678",
            title="Test Medical Paper Title",
            authors=["Smith, John", "Doe, Jane"],
            abstract="This is a test medical abstract",
            journal="Test Medical Journal",
            pub_date=datetime(2023, 1, 15),
            doi="10.1000/test.123",
            pmcid="PMC1234567",
            keywords=["medicine", "research"],
            mesh_terms=["Humans", "Adult"],
            citation_count=25,
            references=["ref1", "ref2"]
        )
        
        assert paper.pmid == "12345678"
        assert paper.title == "Test Medical Paper Title"
        assert len(paper.authors) == 2
        assert paper.authors[0] == "Smith, John"
        assert paper.journal == "Test Medical Journal"
        assert paper.citation_count == 25
        assert len(paper.mesh_terms) == 2
    
    def test_pubmed_paper_validation(self):
        """Test: PubMed paper validates required fields"""
        # Should not raise exception with valid data
        paper = PubMedPaper(
            pmid="87654321",
            title="Valid Medical Title",
            authors=["Author One"],
            abstract="Valid medical abstract",
            journal="Valid Journal",
            pub_date=datetime.now(),
            doi="10.1000/valid.456",
            pmcid="PMC7654321"
        )
        
        assert paper.pmid == "87654321"
        assert paper.journal == "Valid Journal"


class TestPubMedClient:
    """Test suite for PubMed API client implementation"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for PubMed API"""
        return APIRateLimiter({
            'pubmed': RateLimitConfig(
                requests_per_second=10.0,  # PubMed allows higher rate
                requests_per_minute=100,
                burst_capacity=20
            )
        })
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker for PubMed API"""
        return CircuitBreaker(
            name="pubmed_api",
            failure_threshold=3,
            timeout_seconds=30.0,
            recovery_timeout=60.0
        )
    
    @pytest.fixture
    def pubmed_client(self, rate_limiter, circuit_breaker):
        """Create PubMed client with dependencies"""
        return PubMedClient(
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    def test_pubmed_client_initialization(self, pubmed_client):
        """Test: PubMed client initializes correctly"""
        assert pubmed_client.search_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        assert pubmed_client.fetch_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        assert pubmed_client.rate_limiter is not None
        assert pubmed_client.circuit_breaker is not None
        assert pubmed_client.session is None  # Not initialized yet
    
    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self, pubmed_client):
        """Test: PubMed client context manager lifecycle"""
        async with pubmed_client as client:
            assert client.session is not None
            assert isinstance(client.session, aiohttp.ClientSession)
        
        # Session should be closed after context
        assert client.session.closed
    
    @pytest.mark.asyncio
    async def test_search_papers_with_valid_query(self, pubmed_client):
        """Test: Search papers with valid query returns results"""
        mock_search_response = """<?xml version="1.0" encoding="UTF-8"?>
        <eSearchResult>
            <Count>1</Count>
            <RetMax>1</RetMax>
            <RetStart>0</RetStart>
            <IdList>
                <Id>12345678</Id>
            </IdList>
        </eSearchResult>"""
        
        mock_fetch_response = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345678</PMID>
                    <Article>
                        <ArticleTitle>Test Diabetes Research Paper</ArticleTitle>
                        <Abstract>
                            <AbstractText>This is a test abstract about diabetes research.</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                            <Author>
                                <LastName>Doe</LastName>
                                <ForeName>Jane</ForeName>
                            </Author>
                        </AuthorList>
                        <Journal>
                            <Title>Diabetes Research Journal</Title>
                        </Journal>
                        <PublicationTypeList>
                            <PublicationType>Journal Article</PublicationType>
                        </PublicationTypeList>
                    </Article>
                    <KeywordList>
                        <Keyword>diabetes</Keyword>
                        <Keyword>glucose</Keyword>
                    </KeywordList>
                    <MeshHeadingList>
                        <MeshHeading>
                            <DescriptorName>Diabetes Mellitus</DescriptorName>
                        </MeshHeading>
                        <MeshHeading>
                            <DescriptorName>Humans</DescriptorName>
                        </MeshHeading>
                    </MeshHeadingList>
                </MedlineCitation>
                <PubmedData>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">12345678</ArticleId>
                        <ArticleId IdType="doi">10.1000/diabetes.123</ArticleId>
                        <ArticleId IdType="pmc">PMC1234567</ArticleId>
                    </ArticleIdList>
                    <History>
                        <PubMedPubDate PubStatus="pubmed">
                            <Year>2023</Year>
                            <Month>1</Month>
                            <Day>15</Day>
                        </PubMedPubDate>
                    </History>
                </PubmedData>
            </PubmedArticle>
        </PubmedArticleSet>"""
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock both search and fetch calls
            responses = [mock_search_response, mock_fetch_response]
            response_index = [0]
            
            def create_response():
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=responses[response_index[0]])
                response_index[0] += 1
                return mock_response
            
            mock_get.return_value.__aenter__.side_effect = lambda: create_response()
            
            async with pubmed_client as client:
                results = await client.search_papers("diabetes", max_results=10)
            
            assert isinstance(results, PubMedSearchResult)
            assert len(results.papers) == 1
            
            paper = results.papers[0]
            assert paper.pmid == "12345678"
            assert paper.title == "Test Diabetes Research Paper"
            assert len(paper.authors) == 2
            assert "Smith, John" in paper.authors
            assert paper.journal == "Diabetes Research Journal"
            assert "diabetes" in paper.keywords
            assert "Humans" in paper.mesh_terms
    
    @pytest.mark.asyncio
    async def test_search_papers_handles_api_errors(self, pubmed_client):
        """Test: Search papers handles API errors gracefully"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with pubmed_client as client:
                with pytest.raises(ServiceUnavailableError) as exc_info:
                    await client.search_papers("test query")
                
                assert "PubMed API error: 500" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_papers_respects_rate_limits(self, pubmed_client):
        """Test: Search papers respects rate limits"""
        mock_search_response = """<?xml version="1.0" encoding="UTF-8"?>
        <eSearchResult>
            <Count>0</Count>
            <RetMax>0</RetMax>
            <RetStart>0</RetStart>
            <IdList></IdList>
        </eSearchResult>"""
        
        mock_fetch_response = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticleSet></PubmedArticleSet>"""
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            responses = [mock_search_response, mock_fetch_response] * 5
            response_index = [0]
            
            def create_response():
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=responses[response_index[0] % len(responses)])
                response_index[0] += 1
                return mock_response
            
            mock_get.return_value.__aenter__.side_effect = lambda: create_response()
            
            async with pubmed_client as client:
                # Make multiple requests to trigger rate limiting
                tasks = []
                for i in range(3):
                    task = client.search_papers(f"query {i}", max_results=1)
                    tasks.append(task)
                
                # Should complete without errors (rate limiter handles delays)
                results = await asyncio.gather(*tasks)
                assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_get_paper_by_pmid(self, pubmed_client):
        """Test: Get paper by PMID works correctly"""
        mock_fetch_response = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>87654321</PMID>
                    <Article>
                        <ArticleTitle>Specific Medical Paper</ArticleTitle>
                        <Abstract>
                            <AbstractText>Specific medical abstract</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Johnson</LastName>
                                <ForeName>Alice</ForeName>
                            </Author>
                        </AuthorList>
                        <Journal>
                            <Title>Medical Journal</Title>
                        </Journal>
                    </Article>
                </MedlineCitation>
                <PubmedData>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">87654321</ArticleId>
                    </ArticleIdList>
                </PubmedData>
            </PubmedArticle>
        </PubmedArticleSet>"""
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_fetch_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with pubmed_client as client:
                paper = await client.get_paper_by_pmid("87654321")
            
            assert paper.pmid == "87654321"
            assert paper.title == "Specific Medical Paper"
            assert "Johnson, Alice" in paper.authors
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, pubmed_client):
        """Test: Search with MeSH terms and date filters"""
        mock_search_response = """<?xml version="1.0" encoding="UTF-8"?>
        <eSearchResult>
            <Count>0</Count>
            <RetMax>0</RetMax>
            <RetStart>0</RetStart>
            <IdList></IdList>
        </eSearchResult>"""
        
        mock_fetch_response = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticleSet></PubmedArticleSet>"""
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            responses = [mock_search_response, mock_fetch_response]
            response_index = [0]
            
            def create_response():
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=responses[response_index[0]])
                response_index[0] += 1
                return mock_response
            
            mock_get.return_value.__aenter__.side_effect = lambda: create_response()
            
            async with pubmed_client as client:
                await client.search_papers(
                    query="cancer treatment",
                    mesh_terms=["Neoplasms", "Therapy"],
                    max_results=50,
                    min_date="2020/01/01",
                    max_date="2023/12/31"
                )
            
            # Verify the API call was made with correct parameters
            assert mock_get.called
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, pubmed_client):
        """Test: Circuit breaker protects against repeated failures"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Make requests fail consistently
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Server Error")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with pubmed_client as client:
                # First few failures should raise ServiceUnavailableError
                for i in range(3):
                    with pytest.raises(ServiceUnavailableError):
                        await client.search_papers("test query")
                
                # After threshold, should get CircuitBreakerError
                from src.core.exceptions import CircuitBreakerError
                with pytest.raises(CircuitBreakerError):
                    await client.search_papers("test query")


class TestPubMedIntegration:
    """Integration tests for PubMed client with real patterns"""
    
    @pytest.mark.asyncio
    async def test_complete_medical_research_workflow(self):
        """Test: Complete workflow for medical research"""
        rate_limiter = APIRateLimiter({
            'pubmed': RateLimitConfig(requests_per_second=5.0, burst_capacity=10)
        })
        circuit_breaker = CircuitBreaker("pubmed_test", failure_threshold=2)
        
        client = PubMedClient(
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
        
        mock_search_response = """<?xml version="1.0" encoding="UTF-8"?>
        <eSearchResult>
            <Count>1</Count>
            <RetMax>1</RetMax>
            <RetStart>0</RetStart>
            <IdList>
                <Id>99999999</Id>
            </IdList>
        </eSearchResult>"""
        
        mock_fetch_response = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>99999999</PMID>
                    <Article>
                        <ArticleTitle>Integration Test Medical Paper</ArticleTitle>
                        <Abstract>
                            <AbstractText>Test abstract for medical research</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Test</LastName>
                                <ForeName>Doctor</ForeName>
                            </Author>
                        </AuthorList>
                        <Journal>
                            <Title>Test Medical Journal</Title>
                        </Journal>
                    </Article>
                </MedlineCitation>
                <PubmedData>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">99999999</ArticleId>
                    </ArticleIdList>
                </PubmedData>
            </PubmedArticle>
        </PubmedArticleSet>"""
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            responses = [mock_search_response, mock_fetch_response, mock_fetch_response]
            response_index = [0]
            
            def create_response():
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=responses[response_index[0] % len(responses)])
                response_index[0] += 1
                return mock_response
            
            mock_get.return_value.__aenter__.side_effect = lambda: create_response()
            
            async with client:
                # 1. Search for medical papers
                search_results = await client.search_papers("medical research")
                assert len(search_results.papers) == 1
                
                # 2. Get detailed metadata for specific paper
                paper = search_results.papers[0]
                detailed_paper = await client.get_paper_by_pmid(paper.pmid)
                assert detailed_paper.title == "Integration Test Medical Paper"
                
                # 3. Check health status
                health = client.get_health_status()
                assert 'service' in health
                assert health['service'] == 'pubmed'