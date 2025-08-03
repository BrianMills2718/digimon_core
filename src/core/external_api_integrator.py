#!/usr/bin/env python3
"""
External API Integration System

Provides comprehensive integration capabilities with external data sources including
academic databases, research repositories, citation services, and knowledge bases.
Supports data enrichment, cross-referencing, and automated data validation.
"""

import logging
import asyncio
import aiohttp
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, urlparse, quote
import re
from collections import defaultdict, deque
import sqlite3
import threading
from contextlib import asynccontextmanager
import ssl

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """Supported external API providers"""
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    CROSSREF = "crossref"
    GOOGLE_SCHOLAR = "google_scholar"
    ORCID = "orcid"
    OPENALEX = "openalex"
    WIKIPEDIA = "wikipedia"
    WIKIDATA = "wikidata"
    DBLP = "dblp"
    ACM_DL = "acm_dl"
    IEEE_XPLORE = "ieee_xplore"


class DataType(Enum):
    """Types of data that can be retrieved"""
    PAPER_METADATA = "paper_metadata"
    AUTHOR_PROFILE = "author_profile"
    CITATION_DATA = "citation_data"
    ABSTRACT = "abstract"
    FULL_TEXT = "full_text"
    VENUE_INFO = "venue_info"
    REFERENCE_LIST = "reference_list"
    ENTITY_INFORMATION = "entity_information"
    DISAMBIGUATION = "disambiguation"


@dataclass
class APICredentials:
    """API credentials configuration"""
    provider: APIProvider
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    endpoint_url: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    timeout: int = 30  # seconds
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIRequest:
    """API request specification"""
    request_id: str
    provider: APIProvider
    data_type: DataType
    query_params: Dict[str, Any]
    priority: int = 1
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class APIResponse:
    """API response container"""
    request_id: str
    provider: APIProvider
    data_type: DataType
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    response_time: float = 0.0
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    retrieved_at: datetime = field(default_factory=datetime.now)


@dataclass
class EnrichmentResult:
    """Result of data enrichment operation"""
    original_entity: str
    enriched_data: Dict[str, Any]
    confidence_score: float
    sources: List[str]
    disambiguation_candidates: List[Dict[str, Any]] = field(default_factory=list)
    cross_references: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times = deque()
        self.lock = threading.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make API request"""
        with self.lock:
            now = datetime.now()
            
            # Remove requests older than 1 minute
            while (self.request_times and 
                   (now - self.request_times[0]).total_seconds() > 60):
                self.request_times.popleft()
            
            # Check if we can make a request
            if len(self.request_times) >= self.requests_per_minute:
                # Calculate wait time
                oldest_request = self.request_times[0]
                wait_time = 60 - (now - oldest_request).total_seconds()
                
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # Record this request
            self.request_times.append(now)


class APICache:
    """Caching system for API responses"""
    
    def __init__(self, cache_dir: str = "api_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    cache_key TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    cached_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON api_cache(expires_at)
            """)
            conn.commit()
        finally:
            conn.close()
    
    def _generate_cache_key(self, provider: APIProvider, data_type: DataType, 
                          query_params: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        key_data = f"{provider.value}:{data_type.value}:{json.dumps(query_params, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def get(self, provider: APIProvider, data_type: DataType, 
                 query_params: Dict[str, Any]) -> Optional[APIResponse]:
        """Get cached response if available and not expired"""
        cache_key = self._generate_cache_key(provider, data_type, query_params)
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT response_data, cached_at FROM api_cache 
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now()))
            
            row = cursor.fetchone()
            if row:
                response_data, cached_at = row
                data = json.loads(response_data)
                
                return APIResponse(
                    request_id="cached",
                    provider=provider,
                    data_type=data_type,
                    success=True,
                    data=data,
                    cached=True,
                    retrieved_at=datetime.fromisoformat(cached_at)
                )
        finally:
            conn.close()
        
        return None
    
    async def set(self, provider: APIProvider, data_type: DataType,
                 query_params: Dict[str, Any], response: APIResponse) -> None:
        """Cache successful response"""
        if not response.success:
            return
        
        cache_key = self._generate_cache_key(provider, data_type, query_params)
        cached_at = datetime.now()
        expires_at = cached_at + timedelta(hours=self.ttl_hours)
        
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR REPLACE INTO api_cache 
                (cache_key, provider, data_type, response_data, cached_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cache_key, 
                provider.value, 
                data_type.value,
                json.dumps(response.data, default=str),
                cached_at.isoformat(),
                expires_at.isoformat()
            ))
            conn.commit()
        finally:
            conn.close()
    
    async def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                DELETE FROM api_cache WHERE expires_at < ?
            """, (datetime.now(),))
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} expired cache entries")
            return deleted_count
        finally:
            conn.close()


class BaseAPIClient(ABC):
    """Abstract base class for API clients"""
    
    def __init__(self, credentials: APICredentials, cache: APICache):
        self.credentials = credentials
        self.cache = cache
        self.rate_limiter = RateLimiter(credentials.rate_limit)
        self.session = None
    
    @abstractmethod
    async def search_papers(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for papers"""
        pass
    
    @abstractmethod
    async def get_paper_details(self, paper_id: str, **kwargs) -> Dict[str, Any]:
        """Get detailed information about a specific paper"""
        pass
    
    @abstractmethod
    async def get_author_profile(self, author_id: str, **kwargs) -> Dict[str, Any]:
        """Get author profile information"""
        pass
    
    async def _make_request(self, url: str, params: Dict[str, Any] = None,
                          headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make HTTP request with rate limiting and error handling"""
        await self.rate_limiter.acquire()
        
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.credentials.timeout)
            connector = aiohttp.TCPConnector(ssl=ssl.create_default_context())
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        
        try:
            start_time = time.time()
            
            async with self.session.get(url, params=params, headers=headers) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"API request successful: {url} ({response_time:.2f}s)")
                    return data
                elif response.status == 429:  # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded for {url}")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return await self._make_request(url, params, headers)
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed: {url} (status: {response.status}) - {error_text}")
                    raise aiohttp.ClientError(f"HTTP {response.status}: {error_text}")
                    
        except asyncio.TimeoutError:
            logger.error(f"API request timeout: {url}")
            raise
        except Exception as e:
            logger.error(f"API request error: {url} - {e}")
            raise
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


class ArXivClient(BaseAPIClient):
    """arXiv API client"""
    
    def __init__(self, credentials: APICredentials, cache: APICache):
        super().__init__(credentials, cache)
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def search_papers(self, query: str, max_results: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """Search arXiv for papers"""
        
        # Check cache first
        cache_params = {"query": query, "max_results": max_results}
        cached_response = await self.cache.get(APIProvider.ARXIV, DataType.PAPER_METADATA, cache_params)
        if cached_response:
            return cached_response.data
        
        # Make API request
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        try:
            response_text = await self._make_arxiv_request(params)
            papers = self._parse_arxiv_response(response_text)
            
            # Cache the response
            response = APIResponse(
                request_id="search",
                provider=APIProvider.ARXIV,
                data_type=DataType.PAPER_METADATA,
                success=True,
                data=papers
            )
            await self.cache.set(APIProvider.ARXIV, DataType.PAPER_METADATA, cache_params, response)
            
            return papers
            
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []
    
    async def get_paper_details(self, arxiv_id: str, **kwargs) -> Dict[str, Any]:
        """Get details for specific arXiv paper"""
        
        # Check cache
        cache_params = {"arxiv_id": arxiv_id}
        cached_response = await self.cache.get(APIProvider.ARXIV, DataType.PAPER_METADATA, cache_params)
        if cached_response:
            return cached_response.data
        
        params = {
            "id_list": arxiv_id,
            "max_results": 1
        }
        
        try:
            response_text = await self._make_arxiv_request(params)
            papers = self._parse_arxiv_response(response_text)
            paper = papers[0] if papers else {}
            
            # Cache the response
            response = APIResponse(
                request_id="details",
                provider=APIProvider.ARXIV,
                data_type=DataType.PAPER_METADATA,
                success=True,
                data=paper
            )
            await self.cache.set(APIProvider.ARXIV, DataType.PAPER_METADATA, cache_params, response)
            
            return paper
            
        except Exception as e:
            logger.error(f"arXiv paper details failed: {e}")
            return {}
    
    async def get_author_profile(self, author_name: str, **kwargs) -> Dict[str, Any]:
        """Get author profile from arXiv (limited functionality)"""
        # arXiv doesn't have dedicated author profiles, so search for papers by author
        papers = await self.search_papers(f"au:{author_name}", max_results=50)
        
        return {
            "author_name": author_name,
            "paper_count": len(papers),
            "papers": papers,
            "source": "arxiv"
        }
    
    async def _make_arxiv_request(self, params: Dict[str, Any]) -> str:
        """Make request to arXiv API (returns XML)"""
        await self.rate_limiter.acquire()
        
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.credentials.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        try:
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    error_text = await response.text()
                    raise aiohttp.ClientError(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"arXiv API request failed: {e}")
            raise
    
    def _parse_arxiv_response(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        try:
            root = ET.fromstring(xml_text)
            papers = []
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                paper = {}
                
                # Basic information
                paper['id'] = entry.find('atom:id', namespaces).text.split('/')[-1]
                paper['title'] = entry.find('atom:title', namespaces).text.strip()
                paper['summary'] = entry.find('atom:summary', namespaces).text.strip()
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    name = author.find('atom:name', namespaces)
                    if name is not None:
                        authors.append(name.text)
                paper['authors'] = authors
                
                # Publication date
                published = entry.find('atom:published', namespaces)
                if published is not None:
                    paper['published'] = published.text
                
                # Categories
                categories = []
                for category in entry.findall('atom:category', namespaces):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                paper['categories'] = categories
                
                # DOI if available
                doi_elem = entry.find('arxiv:doi', namespaces)
                if doi_elem is not None:
                    paper['doi'] = doi_elem.text
                
                # PDF link
                for link in entry.findall('atom:link', namespaces):
                    if link.get('type') == 'application/pdf':
                        paper['pdf_url'] = link.get('href')
                        break
                
                papers.append(paper)
            
            return papers
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse arXiv XML: {e}")
            return []


class SemanticScholarClient(BaseAPIClient):
    """Semantic Scholar API client"""
    
    def __init__(self, credentials: APICredentials, cache: APICache):
        super().__init__(credentials, cache)
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        
        # Add API key to headers if available
        self.headers = {}
        if credentials.api_key:
            self.headers['x-api-key'] = credentials.api_key
    
    async def search_papers(self, query: str, limit: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """Search Semantic Scholar for papers"""
        
        # Check cache
        cache_params = {"query": query, "limit": limit}
        cached_response = await self.cache.get(APIProvider.SEMANTIC_SCHOLAR, DataType.PAPER_METADATA, cache_params)
        if cached_response:
            return cached_response.data
        
        url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "paperId,title,abstract,authors,year,journal,doi,citationCount,referenceCount,url"
        }
        
        try:
            data = await self._make_request(url, params, self.headers)
            papers = data.get('data', [])
            
            # Cache the response
            response = APIResponse(
                request_id="search",
                provider=APIProvider.SEMANTIC_SCHOLAR,
                data_type=DataType.PAPER_METADATA,
                success=True,
                data=papers
            )
            await self.cache.set(APIProvider.SEMANTIC_SCHOLAR, DataType.PAPER_METADATA, cache_params, response)
            
            return papers
            
        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
            return []
    
    async def get_paper_details(self, paper_id: str, **kwargs) -> Dict[str, Any]:
        """Get detailed paper information"""
        
        # Check cache
        cache_params = {"paper_id": paper_id}
        cached_response = await self.cache.get(APIProvider.SEMANTIC_SCHOLAR, DataType.PAPER_METADATA, cache_params)
        if cached_response:
            return cached_response.data
        
        url = f"{self.base_url}/paper/{paper_id}"
        params = {
            "fields": "paperId,title,abstract,authors,year,journal,doi,citationCount,referenceCount,url,references,citations"
        }
        
        try:
            paper = await self._make_request(url, params, self.headers)
            
            # Cache the response
            response = APIResponse(
                request_id="details",
                provider=APIProvider.SEMANTIC_SCHOLAR,
                data_type=DataType.PAPER_METADATA,
                success=True,
                data=paper
            )
            await self.cache.set(APIProvider.SEMANTIC_SCHOLAR, DataType.PAPER_METADATA, cache_params, response)
            
            return paper
            
        except Exception as e:
            logger.error(f"Semantic Scholar paper details failed: {e}")
            return {}
    
    async def get_author_profile(self, author_id: str, **kwargs) -> Dict[str, Any]:
        """Get author profile"""
        
        # Check cache
        cache_params = {"author_id": author_id}
        cached_response = await self.cache.get(APIProvider.SEMANTIC_SCHOLAR, DataType.AUTHOR_PROFILE, cache_params)
        if cached_response:
            return cached_response.data
        
        url = f"{self.base_url}/author/{author_id}"
        params = {
            "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex,papers"
        }
        
        try:
            author = await self._make_request(url, params, self.headers)
            
            # Cache the response
            response = APIResponse(
                request_id="profile",
                provider=APIProvider.SEMANTIC_SCHOLAR,
                data_type=DataType.AUTHOR_PROFILE,
                success=True,
                data=author
            )
            await self.cache.set(APIProvider.SEMANTIC_SCHOLAR, DataType.AUTHOR_PROFILE, cache_params, response)
            
            return author
            
        except Exception as e:
            logger.error(f"Semantic Scholar author profile failed: {e}")
            return {}
    
    async def get_citations(self, paper_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get citations for a paper"""
        url = f"{self.base_url}/paper/{paper_id}/citations"
        params = {
            "limit": limit,
            "fields": "paperId,title,authors,year,journal"
        }
        
        try:
            data = await self._make_request(url, params, self.headers)
            return data.get('data', [])
        except Exception as e:
            logger.error(f"Semantic Scholar citations failed: {e}")
            return []


class CrossRefClient(BaseAPIClient):
    """CrossRef API client"""
    
    def __init__(self, credentials: APICredentials, cache: APICache):
        super().__init__(credentials, cache)
        self.base_url = "https://api.crossref.org"
        
        # Add polite user agent
        self.headers = {
            'User-Agent': 'KGAS Research System (mailto:research@example.com)'
        }
    
    async def search_papers(self, query: str, rows: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """Search CrossRef for papers"""
        
        # Check cache
        cache_params = {"query": query, "rows": rows}
        cached_response = await self.cache.get(APIProvider.CROSSREF, DataType.PAPER_METADATA, cache_params)
        if cached_response:
            return cached_response.data
        
        url = f"{self.base_url}/works"
        params = {
            "query": query,
            "rows": rows,
            "sort": "relevance",
            "order": "desc"
        }
        
        try:
            data = await self._make_request(url, params, self.headers)
            papers = data.get('message', {}).get('items', [])
            
            # Cache the response
            response = APIResponse(
                request_id="search",
                provider=APIProvider.CROSSREF,
                data_type=DataType.PAPER_METADATA,
                success=True,
                data=papers
            )
            await self.cache.set(APIProvider.CROSSREF, DataType.PAPER_METADATA, cache_params, response)
            
            return papers
            
        except Exception as e:
            logger.error(f"CrossRef search failed: {e}")
            return []
    
    async def get_paper_details(self, doi: str, **kwargs) -> Dict[str, Any]:
        """Get paper details by DOI"""
        
        # Check cache
        cache_params = {"doi": doi}
        cached_response = await self.cache.get(APIProvider.CROSSREF, DataType.PAPER_METADATA, cache_params)
        if cached_response:
            return cached_response.data
        
        url = f"{self.base_url}/works/{quote(doi, safe='')}"
        
        try:
            data = await self._make_request(url, headers=self.headers)
            paper = data.get('message', {})
            
            # Cache the response
            response = APIResponse(
                request_id="details",
                provider=APIProvider.CROSSREF,
                data_type=DataType.PAPER_METADATA,
                success=True,
                data=paper
            )
            await self.cache.set(APIProvider.CROSSREF, DataType.PAPER_METADATA, cache_params, response)
            
            return paper
            
        except Exception as e:
            logger.error(f"CrossRef paper details failed: {e}")
            return {}
    
    async def get_author_profile(self, author_name: str, **kwargs) -> Dict[str, Any]:
        """Get author information (limited in CrossRef)"""
        # CrossRef doesn't have dedicated author profiles
        # Search for works by author
        papers = await self.search_papers(f"author:{author_name}", rows=50)
        
        return {
            "author_name": author_name,
            "paper_count": len(papers),
            "papers": papers,
            "source": "crossref"
        }


class WikipediaClient(BaseAPIClient):
    """Wikipedia API client"""
    
    def __init__(self, credentials: APICredentials, cache: APICache):
        super().__init__(credentials, cache)
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.search_url = "https://en.wikipedia.org/w/api.php"
        
        self.headers = {
            'User-Agent': 'KGAS Research System/1.0 (https://example.com/contact)'
        }
    
    async def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Wikipedia for entities"""
        
        # Check cache
        cache_params = {"query": query, "limit": limit}
        cached_response = await self.cache.get(APIProvider.WIKIPEDIA, DataType.ENTITY_INFORMATION, cache_params)
        if cached_response:
            return cached_response.data
        
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet|titlesnippet|size|wordcount"
        }
        
        try:
            data = await self._make_request(self.search_url, params, self.headers)
            search_results = data.get('query', {}).get('search', [])
            
            # Get additional details for each result
            entities = []
            for result in search_results:
                entity_data = await self.get_entity_details(result['title'])
                if entity_data:
                    entities.append(entity_data)
            
            # Cache the response
            response = APIResponse(
                request_id="search",
                provider=APIProvider.WIKIPEDIA,
                data_type=DataType.ENTITY_INFORMATION,
                success=True,
                data=entities
            )
            await self.cache.set(APIProvider.WIKIPEDIA, DataType.ENTITY_INFORMATION, cache_params, response)
            
            return entities
            
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []
    
    async def get_entity_details(self, title: str) -> Dict[str, Any]:
        """Get detailed information about Wikipedia entity"""
        
        # Check cache
        cache_params = {"title": title}
        cached_response = await self.cache.get(APIProvider.WIKIPEDIA, DataType.ENTITY_INFORMATION, cache_params)
        if cached_response:
            return cached_response.data
        
        # Get page summary
        url = f"{self.base_url}/page/summary/{quote(title, safe='')}"
        
        try:
            summary_data = await self._make_request(url, headers=self.headers)
            
            # Get additional structured data
            infobox_data = await self._get_infobox_data(title)
            
            entity = {
                "title": summary_data.get('title', ''),
                "extract": summary_data.get('extract', ''),
                "description": summary_data.get('description', ''),
                "url": summary_data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                "thumbnail": summary_data.get('thumbnail', {}).get('source', ''),
                "infobox": infobox_data,
                "coordinates": summary_data.get('coordinates', {}),
                "source": "wikipedia"
            }
            
            # Cache the response
            response = APIResponse(
                request_id="details",
                provider=APIProvider.WIKIPEDIA,
                data_type=DataType.ENTITY_INFORMATION,
                success=True,
                data=entity
            )
            await self.cache.set(APIProvider.WIKIPEDIA, DataType.ENTITY_INFORMATION, cache_params, response)
            
            return entity
            
        except Exception as e:
            logger.error(f"Wikipedia entity details failed: {e}")
            return {}
    
    async def _get_infobox_data(self, title: str) -> Dict[str, Any]:
        """Extract infobox data from Wikipedia page"""
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "exsectionformat": "plain"
        }
        
        try:
            data = await self._make_request(self.search_url, params, self.headers)
            pages = data.get('query', {}).get('pages', {})
            
            # Extract basic information (simplified infobox extraction)
            for page_id, page_data in pages.items():
                extract = page_data.get('extract', '')
                # Simple pattern matching for common infobox fields
                infobox = {}
                
                # Look for birth/death dates for people
                birth_match = re.search(r'born[:\s]+([^,\n]+)', extract, re.IGNORECASE)
                if birth_match:
                    infobox['birth'] = birth_match.group(1).strip()
                
                death_match = re.search(r'died[:\s]+([^,\n]+)', extract, re.IGNORECASE)
                if death_match:
                    infobox['death'] = death_match.group(1).strip()
                
                # Look for occupation
                occupation_match = re.search(r'(is|was) an? ([^,\n]+)', extract, re.IGNORECASE)
                if occupation_match:
                    infobox['occupation'] = occupation_match.group(2).strip()
                
                return infobox
            
            return {}
            
        except Exception as e:
            logger.error(f"Wikipedia infobox extraction failed: {e}")
            return {}
    
    async def search_papers(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Not applicable for Wikipedia"""
        return []
    
    async def get_paper_details(self, paper_id: str, **kwargs) -> Dict[str, Any]:
        """Not applicable for Wikipedia"""
        return {}
    
    async def get_author_profile(self, author_name: str, **kwargs) -> Dict[str, Any]:
        """Get author/person information from Wikipedia"""
        entities = await self.search_entities(author_name, limit=1)
        if entities:
            return entities[0]
        return {}


class ExternalAPIIntegrator:
    """Main external API integration system"""
    
    def __init__(self, cache_dir: str = "api_cache", cache_ttl_hours: int = 24):
        self.cache = APICache(cache_dir, cache_ttl_hours)
        self.clients = {}
        self.credentials = {}
        
        # Request queue and processing
        self.request_queue = asyncio.Queue()
        self.active_requests = {}
        self.request_handlers = {}
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_responses': 0,
            'provider_usage': defaultdict(int),
            'data_type_usage': defaultdict(int)
        }
    
    def register_credentials(self, provider: APIProvider, credentials: APICredentials):
        """Register API credentials for provider"""
        self.credentials[provider] = credentials
        logger.info(f"Registered credentials for {provider.value}")
    
    def _get_client(self, provider: APIProvider) -> Optional[BaseAPIClient]:
        """Get or create API client for provider"""
        if provider not in self.clients:
            if provider not in self.credentials:
                logger.error(f"No credentials registered for {provider.value}")
                return None
            
            credentials = self.credentials[provider]
            
            if provider == APIProvider.ARXIV:
                self.clients[provider] = ArXivClient(credentials, self.cache)
            elif provider == APIProvider.SEMANTIC_SCHOLAR:
                self.clients[provider] = SemanticScholarClient(credentials, self.cache)
            elif provider == APIProvider.CROSSREF:
                self.clients[provider] = CrossRefClient(credentials, self.cache)
            elif provider == APIProvider.WIKIPEDIA:
                self.clients[provider] = WikipediaClient(credentials, self.cache)
            else:
                logger.error(f"Unsupported provider: {provider.value}")
                return None
        
        return self.clients[provider]
    
    async def search_papers(self, query: str, providers: List[APIProvider] = None,
                          max_results: int = 100) -> Dict[APIProvider, List[Dict[str, Any]]]:
        """Search for papers across multiple providers"""
        if providers is None:
            providers = [APIProvider.ARXIV, APIProvider.SEMANTIC_SCHOLAR, APIProvider.CROSSREF]
        
        results = {}
        tasks = []
        
        for provider in providers:
            client = self._get_client(provider)
            if client:
                task = asyncio.create_task(
                    client.search_papers(query, max_results=max_results)
                )
                tasks.append((provider, task))
        
        # Wait for all searches to complete
        for provider, task in tasks:
            try:
                papers = await task
                results[provider] = papers
                self.stats['successful_requests'] += 1
                logger.info(f"Found {len(papers)} papers from {provider.value}")
            except Exception as e:
                logger.error(f"Search failed for {provider.value}: {e}")
                results[provider] = []
                self.stats['failed_requests'] += 1
        
        self.stats['total_requests'] += len(tasks)
        return results
    
    async def enrich_entity_data(self, entity_name: str, entity_type: str = None,
                               providers: List[APIProvider] = None) -> EnrichmentResult:
        """Enrich entity data using external sources"""
        if providers is None:
            providers = [APIProvider.WIKIPEDIA, APIProvider.SEMANTIC_SCHOLAR]
        
        enriched_data = {}
        sources = []
        disambiguation_candidates = []
        cross_references = {}
        
        for provider in providers:
            try:
                client = self._get_client(provider)
                if not client:
                    continue
                
                if provider == APIProvider.WIKIPEDIA:
                    entities = await client.search_entities(entity_name, limit=5)
                    if entities:
                        enriched_data['wikipedia'] = entities[0]
                        sources.append('wikipedia')
                        
                        # Add disambiguation candidates
                        if len(entities) > 1:
                            disambiguation_candidates.extend(entities[1:])
                
                elif provider == APIProvider.SEMANTIC_SCHOLAR:
                    # Try to find author profile
                    # Note: This would require author ID, simplified for example
                    papers = await client.search_papers(f"author:{entity_name}", limit=10)
                    if papers:
                        enriched_data['semantic_scholar'] = {
                            'papers': papers,
                            'paper_count': len(papers)
                        }
                        sources.append('semantic_scholar')
                
                self.stats['successful_requests'] += 1
                
            except Exception as e:
                logger.error(f"Entity enrichment failed for {provider.value}: {e}")
                self.stats['failed_requests'] += 1
        
        # Calculate confidence score based on data availability
        confidence_score = len(sources) / len(providers)
        
        return EnrichmentResult(
            original_entity=entity_name,
            enriched_data=enriched_data,
            confidence_score=confidence_score,
            sources=sources,
            disambiguation_candidates=disambiguation_candidates,
            cross_references=cross_references
        )
    
    async def validate_citations(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and enrich citation information"""
        validated_citations = []
        
        for citation in citations:
            validated_citation = citation.copy()
            
            # Try to find additional information using DOI
            if 'doi' in citation and citation['doi']:
                try:
                    client = self._get_client(APIProvider.CROSSREF)
                    if client:
                        paper_details = await client.get_paper_details(citation['doi'])
                        if paper_details:
                            # Enrich citation with CrossRef data
                            validated_citation['crossref_data'] = paper_details
                            validated_citation['validated'] = True
                            
                except Exception as e:
                    logger.error(f"Citation validation failed for DOI {citation['doi']}: {e}")
            
            # Try to find in Semantic Scholar
            if 'title' in citation and citation['title']:
                try:
                    client = self._get_client(APIProvider.SEMANTIC_SCHOLAR)
                    if client:
                        papers = await client.search_papers(citation['title'], limit=1)
                        if papers:
                            validated_citation['semantic_scholar_data'] = papers[0]
                            
                except Exception as e:
                    logger.error(f"Citation enrichment failed for title '{citation['title']}': {e}")
            
            validated_citations.append(validated_citation)
        
        return validated_citations
    
    async def get_comprehensive_paper_data(self, identifier: str, 
                                         identifier_type: str = "doi") -> Dict[str, Any]:
        """Get comprehensive paper data from multiple sources"""
        comprehensive_data = {
            'identifier': identifier,
            'identifier_type': identifier_type,
            'sources': {}
        }
        
        # Try different providers based on identifier type
        if identifier_type == "doi":
            # CrossRef for DOI
            try:
                client = self._get_client(APIProvider.CROSSREF)
                if client:
                    crossref_data = await client.get_paper_details(identifier)
                    if crossref_data:
                        comprehensive_data['sources']['crossref'] = crossref_data
            except Exception as e:
                logger.error(f"CrossRef lookup failed: {e}")
            
            # Semantic Scholar might also have DOI
            try:
                client = self._get_client(APIProvider.SEMANTIC_SCHOLAR)
                if client:
                    # Search by DOI in Semantic Scholar
                    papers = await client.search_papers(f"doi:{identifier}", limit=1)
                    if papers:
                        comprehensive_data['sources']['semantic_scholar'] = papers[0]
            except Exception as e:
                logger.error(f"Semantic Scholar lookup failed: {e}")
        
        elif identifier_type == "arxiv_id":
            # arXiv for arXiv IDs
            try:
                client = self._get_client(APIProvider.ARXIV)
                if client:
                    arxiv_data = await client.get_paper_details(identifier)
                    if arxiv_data:
                        comprehensive_data['sources']['arxiv'] = arxiv_data
            except Exception as e:
                logger.error(f"arXiv lookup failed: {e}")
        
        return comprehensive_data
    
    async def batch_enrich_entities(self, entities: List[str], 
                                  batch_size: int = 10) -> List[EnrichmentResult]:
        """Enrich multiple entities in batches"""
        results = []
        
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i+batch_size]
            
            # Process batch concurrently
            tasks = [self.enrich_entity_data(entity) for entity in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for entity, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Batch enrichment failed for {entity}: {result}")
                    # Create empty result
                    result = EnrichmentResult(
                        original_entity=entity,
                        enriched_data={},
                        confidence_score=0.0,
                        sources=[]
                    )
                
                results.append(result)
            
            # Small delay between batches to be respectful
            await asyncio.sleep(1)
        
        return results
    
    async def cleanup_cache(self) -> int:
        """Clean up expired cache entries"""
        return await self.cache.cleanup_expired()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (self.stats['successful_requests'] / 
                           max(1, self.stats['total_requests'])) * 100,
            'cached_responses': self.stats['cached_responses'],
            'provider_usage': dict(self.stats['provider_usage']),
            'data_type_usage': dict(self.stats['data_type_usage']),
            'registered_providers': list(self.credentials.keys())
        }
    
    async def close(self):
        """Close all API clients and cleanup resources"""
        for client in self.clients.values():
            await client.close()
        
        logger.info("External API integrator closed")


# Factory functions
def create_research_integrator(cache_dir: str = "research_cache") -> ExternalAPIIntegrator:
    """Create integrator configured for research use cases"""
    integrator = ExternalAPIIntegrator(cache_dir, cache_ttl_hours=48)  # Longer cache for research
    
    # Register default credentials (these would come from environment/config)
    integrator.register_credentials(
        APIProvider.ARXIV,
        APICredentials(provider=APIProvider.ARXIV, rate_limit=30)  # Be conservative
    )
    
    integrator.register_credentials(
        APIProvider.CROSSREF,
        APICredentials(provider=APIProvider.CROSSREF, rate_limit=50)
    )
    
    integrator.register_credentials(
        APIProvider.WIKIPEDIA,
        APICredentials(provider=APIProvider.WIKIPEDIA, rate_limit=100)
    )
    
    return integrator


# Example usage and testing
if __name__ == "__main__":
    async def test_api_integration():
        """Test API integration functionality"""
        
        # Create integrator
        integrator = create_research_integrator()
        
        # Add Semantic Scholar credentials if available
        # integrator.register_credentials(
        #     APIProvider.SEMANTIC_SCHOLAR,
        #     APICredentials(
        #         provider=APIProvider.SEMANTIC_SCHOLAR,
        #         api_key="your_api_key_here",
        #         rate_limit=100
        #     )
        # )
        
        try:
            # Test paper search
            print("Testing paper search...")
            search_results = await integrator.search_papers(
                "machine learning natural language processing",
                providers=[APIProvider.ARXIV, APIProvider.CROSSREF],
                max_results=5
            )
            
            for provider, papers in search_results.items():
                print(f"\n{provider.value}: Found {len(papers)} papers")
                for paper in papers[:2]:  # Show first 2
                    title = paper.get('title', 'No title')
                    print(f"  - {title}")
            
            # Test entity enrichment
            print("\nTesting entity enrichment...")
            enrichment = await integrator.enrich_entity_data(
                "Geoffrey Hinton",
                entity_type="PERSON",
                providers=[APIProvider.WIKIPEDIA]
            )
            
            print(f"Enrichment confidence: {enrichment.confidence_score:.2f}")
            print(f"Sources: {enrichment.sources}")
            if enrichment.enriched_data:
                print(f"Found data from {len(enrichment.enriched_data)} sources")
            
            # Test comprehensive paper data
            print("\nTesting comprehensive paper lookup...")
            # Example DOI - replace with a real one for testing
            # comprehensive = await integrator.get_comprehensive_paper_data(
            #     "10.1038/nature14539",
            #     identifier_type="doi"
            # )
            # print(f"Found data from {len(comprehensive['sources'])} sources")
            
            # Show statistics
            stats = integrator.get_statistics()
            print(f"\nIntegration Statistics:")
            print(f"  Total requests: {stats['total_requests']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")
            print(f"  Registered providers: {len(stats['registered_providers'])}")
            
        finally:
            await integrator.close()
    
    # Run the test
    asyncio.run(test_api_integration())