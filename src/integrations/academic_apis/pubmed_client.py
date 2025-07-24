"""
Production PubMed API Client

Provides real-time access to PubMed papers with proper rate limiting,
circuit breaker protection, and comprehensive error handling.

Features:
- Real HTTP calls to PubMed E-utilities API
- XML response parsing for both search and fetch operations
- MeSH term filtering and advanced search capabilities
- Medical research metadata extraction
- Rate limiting and circuit breaker protection
- Comprehensive error handling
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import re

from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
from ...core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


@dataclass
class PubMedPaper:
    """PubMed paper metadata with full medical research information"""
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    pub_date: datetime
    doi: str = ""
    pmcid: str = ""
    keywords: List[str] = field(default_factory=list)
    mesh_terms: List[str] = field(default_factory=list)
    citation_count: int = 0
    references: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.mesh_terms is None:
            self.mesh_terms = []
        if self.references is None:
            self.references = []


@dataclass
class PubMedSearchResult:
    """Result of PubMed search containing papers and metadata"""
    papers: List[PubMedPaper]
    total_results: int
    start_index: int
    items_per_page: int
    query: str
    
    def __len__(self) -> int:
        return len(self.papers)


class PubMedClient:
    """
    Production PubMed API client with comprehensive error handling.
    
    Provides access to PubMed's E-utilities API with:
    - Rate limiting compliance (PubMed allows up to 10/sec with API key)
    - Circuit breaker protection
    - Real XML parsing for both search and fetch
    - MeSH term filtering
    - Medical research metadata extraction
    """
    
    def __init__(self, rate_limiter: APIRateLimiter, circuit_breaker: CircuitBreaker, 
                 api_key: Optional[str] = None):
        """
        Initialize PubMed client with dependencies.
        
        Args:
            rate_limiter: API rate limiter for respectful usage
            circuit_breaker: Circuit breaker for failure protection
            api_key: Optional NCBI API key for higher rate limits
        """
        self.search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.debug("PubMed client initialized")
    
    async def __aenter__(self) -> 'PubMedClient':
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_papers(self, query: str, max_results: int = 10,
                          mesh_terms: Optional[List[str]] = None,
                          min_date: Optional[str] = None,
                          max_date: Optional[str] = None,
                          sort_by: str = "relevance") -> PubMedSearchResult:
        """
        Search PubMed papers with real API calls and structured parsing.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            mesh_terms: List of MeSH terms to filter by
            min_date: Minimum publication date (YYYY/MM/DD format)
            max_date: Maximum publication date (YYYY/MM/DD format)
            sort_by: Sort criteria (relevance, pub_date, first_author)
            
        Returns:
            PubMedSearchResult containing papers and metadata
            
        Raises:
            ServiceUnavailableError: If PubMed API is unavailable
        """
        # Construct search query with MeSH terms if specified
        search_query = query
        if mesh_terms:
            mesh_filter = " OR ".join(f'"{term}"[MeSH Terms]' for term in mesh_terms)
            search_query = f"({query}) AND ({mesh_filter})"
        
        # Add date filters if specified
        if min_date or max_date:
            date_filter = self._build_date_filter(min_date, max_date)
            search_query = f"({search_query}) AND {date_filter}"
        
        search_params = {
            'db': 'pubmed',
            'term': search_query,
            'retmax': max_results,
            'retstart': 0,
            'sort': sort_by,
            'retmode': 'xml'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        
        # Acquire rate limit permission
        await self.rate_limiter.acquire('pubmed')
        
        # Execute search request through circuit breaker
        async def make_search_request():
            async with self.session.get(self.search_url, params=search_params) as response:
                if response.status != 200:
                    raise ServiceUnavailableError("pubmed", f"PubMed API error: {response.status}")
                
                xml_content = await response.text()
                return self._parse_search_response(xml_content)
        
        pmids = await self.circuit_breaker.call(make_search_request)
        
        if not pmids:
            return PubMedSearchResult(
                papers=[],
                total_results=0,
                start_index=0,
                items_per_page=0,
                query=query
            )
        
        # Fetch detailed paper information
        papers = await self._fetch_papers_by_pmids(pmids)
        
        return PubMedSearchResult(
            papers=papers,
            total_results=len(pmids),
            start_index=0,
            items_per_page=len(papers),
            query=query
        )
    
    async def get_paper_by_pmid(self, pmid: str) -> PubMedPaper:
        """
        Get detailed metadata for a specific PubMed paper.
        
        Args:
            pmid: PubMed ID of the paper
            
        Returns:
            PubMedPaper with complete metadata
            
        Raises:
            ServiceUnavailableError: If paper not found or API unavailable
        """
        papers = await self._fetch_papers_by_pmids([pmid])
        
        if not papers:
            raise ServiceUnavailableError("pubmed", f"Paper with PMID {pmid} not found")
        
        return papers[0]
    
    async def _fetch_papers_by_pmids(self, pmids: List[str]) -> List[PubMedPaper]:
        """
        Fetch detailed paper information by PMIDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of PubMedPaper objects
        """
        if not pmids:
            return []
        
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'rettype': 'medline'
        }
        
        if self.api_key:
            fetch_params['api_key'] = self.api_key
        
        await self.rate_limiter.acquire('pubmed')
        
        async def make_fetch_request():
            async with self.session.get(self.fetch_url, params=fetch_params) as response:
                if response.status != 200:
                    raise ServiceUnavailableError("pubmed", f"PubMed fetch error: {response.status}")
                
                xml_content = await response.text()
                return self._parse_fetch_response(xml_content)
        
        return await self.circuit_breaker.call(make_fetch_request)
    
    def _parse_search_response(self, xml_content: str) -> List[str]:
        """
        Parse PubMed search response XML to extract PMIDs.
        
        Args:
            xml_content: XML response from PubMed search API
            
        Returns:
            List of PMIDs
        """
        try:
            root = ET.fromstring(xml_content)
            
            pmids = []
            id_list = root.find('IdList')
            if id_list is not None:
                for id_elem in id_list.findall('Id'):
                    if id_elem.text:
                        pmids.append(id_elem.text.strip())
            
            logger.debug(f"Parsed {len(pmids)} PMIDs from search response")
            return pmids
            
        except ET.ParseError as e:
            raise ServiceUnavailableError("pubmed", f"Failed to parse PubMed search response: {e}")
    
    def _parse_fetch_response(self, xml_content: str) -> List[PubMedPaper]:
        """
        Parse PubMed fetch response XML into structured data.
        
        Args:
            xml_content: XML response from PubMed fetch API
            
        Returns:
            List of PubMedPaper objects
        """
        try:
            root = ET.fromstring(xml_content)
            
            papers = []
            
            for article in root.findall('PubmedArticle'):
                try:
                    paper = self._parse_article(article)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to parse PubMed article: {e}")
                    continue
            
            logger.debug(f"Parsed {len(papers)} papers from fetch response")
            return papers
            
        except ET.ParseError as e:
            raise ServiceUnavailableError("pubmed", f"Failed to parse PubMed fetch response: {e}")
    
    def _parse_article(self, article) -> PubMedPaper:
        """
        Parse individual PubMed article from XML.
        
        Args:
            article: XML article element
            
        Returns:
            PubMedPaper with parsed data
        """
        # Extract PMID
        pmid_elem = article.find('.//PMID')
        pmid = pmid_elem.text if pmid_elem is not None else ""
        
        # Extract title
        title_elem = article.find('.//ArticleTitle')
        title = title_elem.text if title_elem is not None else ""
        if title:
            title = title.strip()
        
        # Extract authors
        authors = []
        author_list = article.find('.//AuthorList')
        if author_list is not None:
            for author in author_list.findall('Author'):
                last_name_elem = author.find('LastName')
                first_name_elem = author.find('ForeName')
                
                if last_name_elem is not None:
                    last_name = last_name_elem.text or ""
                    first_name = first_name_elem.text if first_name_elem is not None else ""
                    
                    if first_name:
                        full_name = f"{last_name}, {first_name}"
                    else:
                        full_name = last_name
                    
                    authors.append(full_name.strip())
        
        # Extract abstract
        abstract = ""
        abstract_elem = article.find('.//Abstract/AbstractText')
        if abstract_elem is not None:
            abstract = abstract_elem.text or ""
        
        # Extract journal
        journal = ""
        journal_elem = article.find('.//Journal/Title')
        if journal_elem is not None:
            journal = journal_elem.text or ""
        
        # Extract publication date
        pub_date = self._extract_publication_date(article)
        
        # Extract DOI and PMC ID
        doi = ""
        pmcid = ""
        
        pubmed_data = article.find('PubmedData')
        if pubmed_data is not None:
            article_ids = pubmed_data.find('ArticleIdList')
            if article_ids is not None:
                for article_id in article_ids.findall('ArticleId'):
                    id_type = article_id.get('IdType')
                    if id_type == 'doi':
                        doi = article_id.text or ""
                    elif id_type == 'pmc':
                        pmcid = article_id.text or ""
        
        # Extract keywords
        keywords = []
        keyword_list = article.find('.//KeywordList')
        if keyword_list is not None:
            for keyword in keyword_list.findall('Keyword'):
                if keyword.text:
                    keywords.append(keyword.text.strip())
        
        # Extract MeSH terms
        mesh_terms = []
        mesh_list = article.find('.//MeshHeadingList')
        if mesh_list is not None:
            for mesh_heading in mesh_list.findall('MeshHeading'):
                descriptor = mesh_heading.find('DescriptorName')
                if descriptor is not None and descriptor.text:
                    mesh_terms.append(descriptor.text.strip())
        
        return PubMedPaper(
            pmid=pmid,
            title=title,
            authors=authors,
            abstract=abstract,
            journal=journal,
            pub_date=pub_date,
            doi=doi,
            pmcid=pmcid,
            keywords=keywords,
            mesh_terms=mesh_terms,
            citation_count=0,  # Would be enriched from external sources
            references=[]      # Would be extracted from PMC or other sources
        )
    
    def _extract_publication_date(self, article) -> datetime:
        """Extract publication date from article XML"""
        try:
            # Try PubmedData first
            pubmed_data = article.find('PubmedData')
            if pubmed_data is not None:
                history = pubmed_data.find('History')
                if history is not None:
                    for pub_date in history.findall('PubMedPubDate'):
                        if pub_date.get('PubStatus') == 'pubmed':
                            year_elem = pub_date.find('Year')
                            month_elem = pub_date.find('Month')
                            day_elem = pub_date.find('Day')
                            
                            if year_elem is not None:
                                year = int(year_elem.text)
                                month = int(month_elem.text) if month_elem is not None else 1
                                day = int(day_elem.text) if day_elem is not None else 1
                                return datetime(year, month, day)
            
            # Try Journal publication date
            journal = article.find('.//Journal')
            if journal is not None:
                journal_issue = journal.find('JournalIssue')
                if journal_issue is not None:
                    pub_date = journal_issue.find('PubDate')
                    if pub_date is not None:
                        year_elem = pub_date.find('Year')
                        if year_elem is not None:
                            year = int(year_elem.text)
                            month_elem = pub_date.find('Month')
                            day_elem = pub_date.find('Day')
                            
                            month = 1
                            day = 1
                            
                            if month_elem is not None:
                                try:
                                    month = int(month_elem.text)
                                except ValueError:
                                    # Handle month names
                                    month_names = {
                                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                                        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                                        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                                    }
                                    month = month_names.get(month_elem.text, 1)
                            
                            if day_elem is not None:
                                try:
                                    day = int(day_elem.text)
                                except ValueError:
                                    day = 1
                            
                            return datetime(year, month, day)
            
        except (ValueError, TypeError):
            pass
        
        return datetime.now()
    
    def _build_date_filter(self, min_date: Optional[str], max_date: Optional[str]) -> str:
        """Build date filter for PubMed search"""
        if min_date and max_date:
            return f'("{min_date}"[Date - Publication] : "{max_date}"[Date - Publication])'
        elif min_date:
            return f'"{min_date}"[Date - Publication] : "3000"[Date - Publication]'
        elif max_date:
            return f'"1900"[Date - Publication] : "{max_date}"[Date - Publication]'
        else:
            return ""
    
    async def get_citation_count(self, pmid: str) -> int:
        """
        Get citation count for paper (would integrate with external service).
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Citation count (placeholder implementation)
        """
        # Placeholder - would integrate with citation tracking service
        # For now, return 0 to satisfy interface
        return 0
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of PubMed client.
        
        Returns:
            Dictionary with health information
        """
        return {
            'service': 'pubmed',
            'status': 'healthy' if self.session and not self.session.closed else 'disconnected',
            'search_url': self.search_url,
            'fetch_url': self.fetch_url,
            'has_api_key': self.api_key is not None,
            'circuit_breaker_state': self.circuit_breaker.state.value,
            'rate_limiter_stats': self.rate_limiter.get_service_stats('pubmed')
        }