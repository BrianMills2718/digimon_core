"""
Semantic Scholar MCP Client

Client for the semantic-scholar-fastmcp-mcp-server providing access to:
- Academic paper search and discovery
- Citation network analysis
- Author information and profiles
- Paper recommendations
- Batch operations

Based on: https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .http_client import HTTPMCPClient
from .base_client import MCPResponse
from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
import logging

logger = logging.getLogger(__name__)


@dataclass
class SemanticScholarPaper:
    """Semantic Scholar paper representation"""
    paper_id: str
    title: str
    abstract: str
    authors: List[Dict[str, Any]]
    year: Optional[int]
    citation_count: int
    reference_count: int
    venue: Optional[str]
    doi: Optional[str]
    arxiv_id: Optional[str]
    fields_of_study: List[str]
    influential_citation_count: int
    s2_url: str


@dataclass
class SemanticScholarAuthor:
    """Semantic Scholar author representation"""
    author_id: str
    name: str
    paper_count: int
    citation_count: int
    h_index: int
    affiliations: List[str]
    homepage: Optional[str]
    papers: Optional[List[SemanticScholarPaper]] = None


class SemanticScholarMCPClient(HTTPMCPClient):
    """
    MCP client for Semantic Scholar academic search and analysis.
    
    Provides comprehensive access to:
    - Paper search with advanced filtering
    - Citation and reference networks
    - Author profiles and publication history
    - Paper recommendations
    - Batch operations for efficiency
    """
    
    def __init__(self, 
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 api_key: Optional[str] = None,
                 server_url: str = "http://localhost:8000"):
        """
        Initialize Semantic Scholar MCP client.
        
        Args:
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            api_key: Optional Semantic Scholar API key for higher limits
            server_url: MCP server URL
        """
        config = {}
        if api_key:
            config['headers'] = {'X-API-Key': api_key}
        
        super().__init__(
            server_name="semantic_scholar",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            config=config
        )
    
    # Paper Search Methods
    
    async def search_papers(self, 
                          query: str,
                          limit: int = 10,
                          offset: int = 0,
                          year: Optional[str] = None,
                          min_citation_count: Optional[int] = None,
                          fields_of_study: Optional[List[str]] = None,
                          fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Search for papers using relevance ranking.
        
        Args:
            query: Search query string
            limit: Maximum results (1-100)
            offset: Pagination offset
            year: Year or year range (e.g., "2020", "2020-2023")
            min_citation_count: Minimum citation count filter
            fields_of_study: List of fields to filter by
            fields: Comma-separated list of fields to return
            
        Returns:
            MCPResponse containing list of papers
        """
        params = {
            "query": query,
            "limit": min(limit, 100),
            "offset": offset
        }
        
        if year:
            params["year"] = year
        if min_citation_count:
            params["minCitationCount"] = min_citation_count
        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_relevance_search", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("papers", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    async def search_papers_bulk(self,
                               query: str,
                               limit: int = 100,
                               sort: Optional[str] = None,
                               **kwargs) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Bulk paper search with sorting options.
        
        Args:
            query: Search query
            limit: Maximum results
            sort: Sort by "citationCount", "paperId", "publicationDate"
            **kwargs: Additional search parameters
            
        Returns:
            MCPResponse containing list of papers
        """
        params = {
            "query": query,
            "limit": limit,
            **kwargs
        }
        
        if sort:
            params["sort"] = sort
        
        response = await self.call_method("paper_bulk_search", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("papers", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    async def get_paper_details(self, 
                              paper_id: str,
                              fields: Optional[str] = None) -> MCPResponse[SemanticScholarPaper]:
        """
        Get comprehensive details about a specific paper.
        
        Args:
            paper_id: Paper ID (S2 ID, DOI, ArXiv ID, etc.)
            fields: Comma-separated list of fields to return
            
        Returns:
            MCPResponse containing paper details
        """
        params = {"paper_id": paper_id}
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_details", params)
        
        if response.success and response.data:
            paper = self._parse_paper(response.data)
            return MCPResponse(success=True, data=paper, metadata=response.metadata)
        
        return response
    
    async def get_papers_batch(self,
                             paper_ids: List[str],
                             fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Get details for multiple papers efficiently.
        
        Args:
            paper_ids: List of paper IDs (up to 1000)
            fields: Comma-separated list of fields to return
            
        Returns:
            MCPResponse containing list of papers
        """
        params = {"paper_ids": paper_ids[:1000]}  # API limit
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_batch_details", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("papers", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    # Citation Methods
    
    async def get_citations(self,
                          paper_id: str,
                          limit: int = 10,
                          offset: int = 0,
                          fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Get papers that cite a specific paper.
        
        Args:
            paper_id: Paper ID
            limit: Maximum results
            offset: Pagination offset
            fields: Fields to return for citing papers
            
        Returns:
            MCPResponse containing citing papers
        """
        params = {
            "paper_id": paper_id,
            "limit": limit,
            "offset": offset
        }
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_citations", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("citations", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    async def get_references(self,
                           paper_id: str,
                           limit: int = 10,
                           offset: int = 0,
                           fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Get papers referenced by a specific paper.
        
        Args:
            paper_id: Paper ID
            limit: Maximum results
            offset: Pagination offset
            fields: Fields to return for referenced papers
            
        Returns:
            MCPResponse containing referenced papers
        """
        params = {
            "paper_id": paper_id,
            "limit": limit,
            "offset": offset
        }
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_references", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("references", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    # Author Methods
    
    async def search_authors(self,
                           query: str,
                           limit: int = 10,
                           offset: int = 0,
                           fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarAuthor]]:
        """
        Search for authors by name.
        
        Args:
            query: Author name query
            limit: Maximum results
            offset: Pagination offset
            fields: Fields to return
            
        Returns:
            MCPResponse containing list of authors
        """
        params = {
            "query": query,
            "limit": limit,
            "offset": offset
        }
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("author_search", params)
        
        if response.success and response.data:
            authors = [self._parse_author(a) for a in response.data.get("authors", [])]
            return MCPResponse(success=True, data=authors, metadata=response.metadata)
        
        return response
    
    async def get_author_details(self,
                               author_id: str,
                               fields: Optional[str] = None) -> MCPResponse[SemanticScholarAuthor]:
        """
        Get detailed information about an author.
        
        Args:
            author_id: Author ID
            fields: Fields to return
            
        Returns:
            MCPResponse containing author details
        """
        params = {"author_id": author_id}
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("author_details", params)
        
        if response.success and response.data:
            author = self._parse_author(response.data)
            return MCPResponse(success=True, data=author, metadata=response.metadata)
        
        return response
    
    async def get_author_papers(self,
                              author_id: str,
                              limit: int = 10,
                              offset: int = 0,
                              fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Get papers written by an author.
        
        Args:
            author_id: Author ID
            limit: Maximum results
            offset: Pagination offset
            fields: Fields to return for papers
            
        Returns:
            MCPResponse containing author's papers
        """
        params = {
            "author_id": author_id,
            "limit": limit,
            "offset": offset
        }
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("author_papers", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("papers", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    # Recommendation Methods
    
    async def get_recommendations_single(self,
                                       paper_id: str,
                                       limit: int = 10,
                                       fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Get recommendations based on a single paper.
        
        Args:
            paper_id: Source paper ID
            limit: Maximum recommendations
            fields: Fields to return
            
        Returns:
            MCPResponse containing recommended papers
        """
        params = {
            "paper_id": paper_id,
            "limit": limit
        }
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_recommendations_single", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("recommendations", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    async def get_recommendations_multi(self,
                                      positive_paper_ids: List[str],
                                      negative_paper_ids: Optional[List[str]] = None,
                                      limit: int = 10,
                                      fields: Optional[str] = None) -> MCPResponse[List[SemanticScholarPaper]]:
        """
        Get recommendations based on multiple papers.
        
        Args:
            positive_paper_ids: Papers to find similar to
            negative_paper_ids: Papers to avoid similarity to
            limit: Maximum recommendations
            fields: Fields to return
            
        Returns:
            MCPResponse containing recommended papers
        """
        params = {
            "positive_paper_ids": positive_paper_ids,
            "limit": limit
        }
        if negative_paper_ids:
            params["negative_paper_ids"] = negative_paper_ids
        if fields:
            params["fields"] = fields
        
        response = await self.call_method("paper_recommendations_multi", params)
        
        if response.success and response.data:
            papers = [self._parse_paper(p) for p in response.data.get("recommendations", [])]
            return MCPResponse(success=True, data=papers, metadata=response.metadata)
        
        return response
    
    # Helper Methods
    
    def _parse_paper(self, data: Dict[str, Any]) -> SemanticScholarPaper:
        """Parse paper data from MCP response"""
        return SemanticScholarPaper(
            paper_id=data.get("paperId", ""),
            title=data.get("title", ""),
            abstract=data.get("abstract", ""),
            authors=data.get("authors", []),
            year=data.get("year"),
            citation_count=data.get("citationCount", 0),
            reference_count=data.get("referenceCount", 0),
            venue=data.get("venue"),
            doi=data.get("doi"),
            arxiv_id=data.get("arxivId"),
            fields_of_study=data.get("fieldsOfStudy", []),
            influential_citation_count=data.get("influentialCitationCount", 0),
            s2_url=data.get("url", "")
        )
    
    def _parse_author(self, data: Dict[str, Any]) -> SemanticScholarAuthor:
        """Parse author data from MCP response"""
        return SemanticScholarAuthor(
            author_id=data.get("authorId", ""),
            name=data.get("name", ""),
            paper_count=data.get("paperCount", 0),
            citation_count=data.get("citationCount", 0),
            h_index=data.get("hIndex", 0),
            affiliations=data.get("affiliations", []),
            homepage=data.get("homepage")
        )