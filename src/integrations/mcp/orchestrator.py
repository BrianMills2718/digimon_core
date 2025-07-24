"""
MCP Orchestrator

Coordinates between multiple MCP servers to provide unified discourse analysis capabilities.
Handles cross-server operations, data aggregation, and intelligent routing.

Features:
- Unified search across all data sources
- Cross-reference academic papers with news and media
- Multi-modal content analysis (text, video, LaTeX)
- Intelligent source selection based on query type
- Result aggregation and ranking
"""

import asyncio
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

from .semantic_scholar_client import SemanticScholarMCPClient, SemanticScholarPaper
from .arxiv_latex_client import ArXivLatexMCPClient, ArXivLatexContent
from .youtube_client import YouTubeMCPClient, YouTubeVideo
from .google_news_client import GoogleNewsMCPClient, NewsArticle, NewsCategory
from .dappier_client import DappierMCPClient, DappierContent, ContentDomain
from .content_core_client import ContentCoreMCPClient, ExtractedContent, ContentType

from ...core.circuit_breaker import CircuitBreaker, CircuitBreakerManager
from ...core.api_rate_limiter import APIRateLimiter, RateLimitConfig
from ...core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class SearchScope(Enum):
    """Search scope for discourse analysis"""
    ACADEMIC = "academic"
    NEWS = "news"
    MEDIA = "media"
    SOCIAL = "social"
    ALL = "all"


@dataclass
class UnifiedSearchResult:
    """Unified search result across all sources"""
    result_id: str
    source: str  # MCP server name
    result_type: str  # paper, article, video, etc.
    title: str
    summary: str
    url: str
    published_date: Optional[datetime]
    relevance_score: float
    raw_data: Any  # Original data object
    metadata: Dict[str, Any]


@dataclass
class DiscourseAnalysisResult:
    """Result of cross-source discourse analysis"""
    topic: str
    time_range: Dict[str, datetime]
    academic_papers: List[SemanticScholarPaper]
    news_articles: List[Union[NewsArticle, DappierContent]]
    media_content: List[Union[YouTubeVideo, ExtractedContent]]
    sentiment_analysis: Dict[str, float]
    key_entities: List[Dict[str, Any]]
    trending_score: float
    cross_references: List[Dict[str, Any]]


class MCPOrchestrator:
    """
    Orchestrates multiple MCP servers for comprehensive discourse analysis.
    
    Provides:
    - Unified search interface
    - Cross-source correlation
    - Multi-modal content analysis
    - Intelligent routing and aggregation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MCP Orchestrator with configuration.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config
        
        # Initialize rate limiter with appropriate limits for each service
        self.rate_limiter = APIRateLimiter({
            'semantic_scholar': RateLimitConfig(
                requests_per_second=1.0 if config.get('semantic_scholar_api_key') else 0.3,
                burst_capacity=10
            ),
            'arxiv_latex': RateLimitConfig(
                requests_per_second=3.0,
                burst_capacity=10
            ),
            'youtube': RateLimitConfig(
                requests_per_second=1.0,
                burst_capacity=5
            ),
            'google_news': RateLimitConfig(
                requests_per_second=1.0,
                burst_capacity=5
            ),
            'dappier': RateLimitConfig(
                requests_per_second=2.0,
                burst_capacity=10
            ),
            'content_core': RateLimitConfig(
                requests_per_second=5.0,
                burst_capacity=20
            )
        })
        
        # Initialize circuit breaker manager
        self.circuit_breaker_manager = CircuitBreakerManager()
        
        # Initialize MCP clients
        self._init_clients()
        
        logger.info("MCP Orchestrator initialized with %d clients", len(self.clients))
    
    def _init_clients(self):
        """Initialize all MCP clients"""
        self.clients = {}
        
        # Semantic Scholar
        if self.config.get('enable_semantic_scholar', True):
            self.clients['semantic_scholar'] = SemanticScholarMCPClient(
                rate_limiter=self.rate_limiter,
                circuit_breaker=self.circuit_breaker_manager.get_breaker('semantic_scholar'),
                api_key=self.config.get('semantic_scholar_api_key'),
                server_url=self.config.get('semantic_scholar_url', 'http://localhost:8000')
            )
        
        # ArXiv LaTeX
        if self.config.get('enable_arxiv_latex', True):
            self.clients['arxiv_latex'] = ArXivLatexMCPClient(
                rate_limiter=self.rate_limiter,
                circuit_breaker=self.circuit_breaker_manager.get_breaker('arxiv_latex'),
                server_url=self.config.get('arxiv_latex_url', 'http://localhost:8001')
            )
        
        # YouTube
        if self.config.get('enable_youtube', True):
            self.clients['youtube'] = YouTubeMCPClient(
                rate_limiter=self.rate_limiter,
                circuit_breaker=self.circuit_breaker_manager.get_breaker('youtube'),
                openai_api_key=self.config.get('openai_api_key'),
                server_url=self.config.get('youtube_url', 'http://localhost:8002')
            )
        
        # Google News
        if self.config.get('enable_google_news', True):
            self.clients['google_news'] = GoogleNewsMCPClient(
                rate_limiter=self.rate_limiter,
                circuit_breaker=self.circuit_breaker_manager.get_breaker('google_news'),
                serp_api_key=self.config.get('serp_api_key', ''),
                server_url=self.config.get('google_news_url', 'http://localhost:8003')
            )
        
        # DappierAI
        if self.config.get('enable_dappier', True):
            self.clients['dappier'] = DappierMCPClient(
                rate_limiter=self.rate_limiter,
                circuit_breaker=self.circuit_breaker_manager.get_breaker('dappier'),
                api_key=self.config.get('dappier_api_key', ''),
                server_url=self.config.get('dappier_url', 'http://localhost:8004')
            )
        
        # Content Core
        if self.config.get('enable_content_core', True):
            self.clients['content_core'] = ContentCoreMCPClient(
                rate_limiter=self.rate_limiter,
                circuit_breaker=self.circuit_breaker_manager.get_breaker('content_core'),
                api_key=self.config.get('content_core_api_key'),
                server_url=self.config.get('content_core_url', 'http://localhost:8005')
            )
    
    async def unified_search(self,
                           query: str,
                           scope: SearchScope = SearchScope.ALL,
                           limit_per_source: int = 10,
                           date_from: Optional[datetime] = None,
                           date_to: Optional[datetime] = None) -> List[UnifiedSearchResult]:
        """
        Perform unified search across all configured sources.
        
        Args:
            query: Search query
            scope: Scope of search
            limit_per_source: Max results per source
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            List of unified search results
        """
        results = []
        search_tasks = []
        
        # Determine which sources to search based on scope
        if scope in [SearchScope.ACADEMIC, SearchScope.ALL]:
            if 'semantic_scholar' in self.clients:
                search_tasks.append(self._search_semantic_scholar(query, limit_per_source))
        
        if scope in [SearchScope.NEWS, SearchScope.ALL]:
            if 'google_news' in self.clients:
                search_tasks.append(self._search_google_news(query, limit_per_source, date_from, date_to))
            if 'dappier' in self.clients:
                search_tasks.append(self._search_dappier(query, limit_per_source, date_from, date_to))
        
        if scope in [SearchScope.MEDIA, SearchScope.ALL]:
            if 'youtube' in self.clients:
                search_tasks.append(self._search_youtube(query, limit_per_source))
        
        # Execute searches in parallel
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Process results
        for result_set in search_results:
            if isinstance(result_set, Exception):
                logger.warning(f"Search error: {result_set}")
                continue
            results.extend(result_set)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results
    
    async def analyze_discourse(self,
                              topic: str,
                              time_range_days: int = 30,
                              include_sentiment: bool = True) -> DiscourseAnalysisResult:
        """
        Perform comprehensive discourse analysis on a topic.
        
        Args:
            topic: Topic to analyze
            time_range_days: Days to look back
            include_sentiment: Include sentiment analysis
            
        Returns:
            Comprehensive discourse analysis result
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(days=time_range_days)
        
        # Gather data from all sources
        tasks = []
        
        # Academic sources
        if 'semantic_scholar' in self.clients:
            tasks.append(self._get_academic_discourse(topic, start_date, end_date))
        
        # News sources
        news_tasks = []
        if 'google_news' in self.clients:
            news_tasks.append(self._get_google_news_discourse(topic, time_range_days))
        if 'dappier' in self.clients:
            news_tasks.append(self._get_dappier_discourse(topic, start_date, end_date))
        
        if news_tasks:
            tasks.append(self._aggregate_news_discourse(news_tasks))
        
        # Media sources
        if 'youtube' in self.clients:
            tasks.append(self._get_youtube_discourse(topic))
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        academic_papers = []
        news_articles = []
        media_content = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Discourse analysis error: {result}")
                continue
            
            if isinstance(result, list):
                if result and isinstance(result[0], SemanticScholarPaper):
                    academic_papers = result
                elif result and isinstance(result[0], (NewsArticle, DappierContent)):
                    news_articles = result
                elif result and isinstance(result[0], (YouTubeVideo, ExtractedContent)):
                    media_content = result
        
        # Analyze sentiment if requested
        sentiment_analysis = {}
        if include_sentiment and 'dappier' in self.clients:
            sentiment_result = await self._analyze_sentiment(topic, time_range_days)
            if sentiment_result:
                sentiment_analysis = sentiment_result
        
        # Extract key entities
        key_entities = self._extract_key_entities(academic_papers, news_articles, media_content)
        
        # Calculate trending score
        trending_score = self._calculate_trending_score(
            len(academic_papers), len(news_articles), len(media_content), time_range_days
        )
        
        # Find cross-references
        cross_references = self._find_cross_references(academic_papers, news_articles, media_content)
        
        return DiscourseAnalysisResult(
            topic=topic,
            time_range={'start': start_date, 'end': end_date},
            academic_papers=academic_papers,
            news_articles=news_articles,
            media_content=media_content,
            sentiment_analysis=sentiment_analysis,
            key_entities=key_entities,
            trending_score=trending_score,
            cross_references=cross_references
        )
    
    async def extract_mathematical_content(self,
                                         arxiv_id: str) -> Dict[str, Any]:
        """
        Extract mathematical content from an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            Dictionary with LaTeX content and equations
        """
        if 'arxiv_latex' not in self.clients:
            raise ServiceUnavailableError('arxiv_latex', 'ArXiv LaTeX client not configured')
        
        async with self.clients['arxiv_latex'].connect() as client:
            # Get LaTeX source
            latex_response = await client.get_latex_source(arxiv_id)
            
            if not latex_response.success:
                return {'error': 'Failed to get LaTeX source'}
            
            # Extract equations
            equations_response = await client.extract_equations(arxiv_id, include_context=True)
            
            # Extract theorems and proofs
            theorems_response = await client.extract_theorems_proofs(arxiv_id)
            
            return {
                'latex_content': latex_response.data,
                'equations': equations_response.data if equations_response.success else [],
                'theorems': theorems_response.data if theorems_response.success else []
            }
    
    async def transcribe_and_analyze_video(self,
                                         video_url: str,
                                         extract_topics: bool = True) -> Dict[str, Any]:
        """
        Transcribe video and analyze content.
        
        Args:
            video_url: YouTube video URL
            extract_topics: Extract topic timestamps
            
        Returns:
            Dictionary with transcript and analysis
        """
        if 'youtube' not in self.clients:
            raise ServiceUnavailableError('youtube', 'YouTube client not configured')
        
        async with self.clients['youtube'].connect() as client:
            # Transcribe video
            transcript_response = await client.transcribe_video(video_url)
            
            if not transcript_response.success:
                return {'error': 'Failed to transcribe video'}
            
            video = transcript_response.data
            
            # Get summary
            summary_response = await client.get_transcript_summary(video_url)
            
            result = {
                'video': video,
                'summary': summary_response.data if summary_response.success else None
            }
            
            # Extract topic timestamps if requested
            if extract_topics:
                # Simple topic extraction based on common terms
                topics = self._extract_topics_from_transcript(video.transcript_chunks)
                if topics:
                    timestamps_response = await client.extract_timestamps(video_url, topics[:5])
                    if timestamps_response.success:
                        result['topic_timestamps'] = timestamps_response.data
            
            return result
    
    async def get_comprehensive_news_coverage(self,
                                            topic: str,
                                            include_financial: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive news coverage from multiple sources.
        
        Args:
            topic: Topic to search
            include_financial: Include financial data if available
            
        Returns:
            Dictionary with news from multiple sources
        """
        results = {}
        
        # Google News
        if 'google_news' in self.clients:
            async with self.clients['google_news'].connect() as client:
                # Get headlines
                headlines = await client.get_headlines(limit=5)
                
                # Search specific topic
                topic_news = await client.search_news(topic, limit=10)
                
                # Get trending topics
                trending = await client.get_trending_topics()
                
                results['google_news'] = {
                    'headlines': headlines.data if headlines.success else [],
                    'topic_news': topic_news.data if topic_news.success else [],
                    'trending': trending.data if trending.success else []
                }
        
        # DappierAI multi-domain
        if 'dappier' in self.clients:
            async with self.clients['dappier'].connect() as client:
                # Search across domains
                content = await client.search_content(topic, limit=10)
                
                # Get trending topics
                trending = await client.get_trending_topics()
                
                results['dappier'] = {
                    'content': content.data if content.success else [],
                    'trending': trending.data if trending.success else []
                }
                
                # Include financial data if requested
                if include_financial:
                    # Extract stock symbols from topic
                    symbols = self._extract_stock_symbols(topic)
                    if symbols:
                        financial = await client.get_financial_data(symbols)
                        if financial.success:
                            results['dappier']['financial'] = financial.data
        
        return results
    
    # Helper methods for search
    
    async def _search_semantic_scholar(self, query: str, limit: int) -> List[UnifiedSearchResult]:
        """Search Semantic Scholar"""
        results = []
        
        try:
            async with self.clients['semantic_scholar'].connect() as client:
                response = await client.search_papers(query, limit=limit)
                
                if response.success and response.data:
                    for paper in response.data:
                        results.append(UnifiedSearchResult(
                            result_id=f"ss_{paper.paper_id}",
                            source="semantic_scholar",
                            result_type="paper",
                            title=paper.title,
                            summary=paper.abstract[:500] + "..." if len(paper.abstract) > 500 else paper.abstract,
                            url=paper.s2_url,
                            published_date=datetime(paper.year, 1, 1) if paper.year else None,
                            relevance_score=self._calculate_paper_relevance(paper, query),
                            raw_data=paper,
                            metadata={
                                'citation_count': paper.citation_count,
                                'authors': [a['name'] for a in paper.authors[:3]]
                            }
                        ))
        except Exception as e:
            logger.error(f"Semantic Scholar search error: {e}")
        
        return results
    
    async def _search_google_news(self, query: str, limit: int, 
                                date_from: Optional[datetime], 
                                date_to: Optional[datetime]) -> List[UnifiedSearchResult]:
        """Search Google News"""
        results = []
        
        try:
            async with self.clients['google_news'].connect() as client:
                time_range = None
                if date_from and date_to:
                    days_diff = (date_to - date_from).days
                    if days_diff <= 1:
                        time_range = "day"
                    elif days_diff <= 7:
                        time_range = "week"
                    elif days_diff <= 30:
                        time_range = "month"
                    else:
                        time_range = "year"
                
                response = await client.search_news(query, limit=limit, time_range=time_range)
                
                if response.success and response.data:
                    for article in response.data:
                        results.append(UnifiedSearchResult(
                            result_id=f"gn_{hash(article.link)}",
                            source="google_news",
                            result_type="news_article",
                            title=article.title,
                            summary=article.description,
                            url=article.link,
                            published_date=article.published_date,
                            relevance_score=0.8,  # Google News is generally relevant
                            raw_data=article,
                            metadata={
                                'source': article.source,
                                'category': article.category
                            }
                        ))
        except Exception as e:
            logger.error(f"Google News search error: {e}")
        
        return results
    
    async def _search_dappier(self, query: str, limit: int,
                            date_from: Optional[datetime],
                            date_to: Optional[datetime]) -> List[UnifiedSearchResult]:
        """Search DappierAI"""
        results = []
        
        try:
            async with self.clients['dappier'].connect() as client:
                response = await client.search_content(
                    query, 
                    limit=limit,
                    date_from=date_from,
                    date_to=date_to
                )
                
                if response.success and response.data:
                    for content in response.data:
                        results.append(UnifiedSearchResult(
                            result_id=f"da_{content.content_id}",
                            source="dappier",
                            result_type=f"{content.domain.value}_content",
                            title=content.title,
                            summary=content.summary,
                            url=content.url,
                            published_date=content.published_date,
                            relevance_score=content.source_reputation,  # Use source reputation as relevance
                            raw_data=content,
                            metadata={
                                'source': content.source,
                                'domain': content.domain.value,
                                'tags': content.tags[:5]
                            }
                        ))
        except Exception as e:
            logger.error(f"Dappier search error: {e}")
        
        return results
    
    async def _search_youtube(self, query: str, limit: int) -> List[UnifiedSearchResult]:
        """Search YouTube (via transcripts)"""
        results = []
        
        # Note: YouTube MCP doesn't have direct search, this is a placeholder
        # In practice, you might need to use YouTube Data API separately
        # or search through already transcribed videos
        
        return results
    
    # Helper methods for discourse analysis
    
    def _calculate_paper_relevance(self, paper: SemanticScholarPaper, query: str) -> float:
        """Calculate relevance score for a paper"""
        score = 0.5  # Base score
        
        # Title match
        if query.lower() in paper.title.lower():
            score += 0.3
        
        # Citation count factor
        if paper.citation_count > 100:
            score += 0.1
        elif paper.citation_count > 50:
            score += 0.05
        
        # Recent paper bonus
        if paper.year and paper.year >= datetime.now().year - 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_key_entities(self, 
                            academic_papers: List[SemanticScholarPaper],
                            news_articles: List[Union[NewsArticle, DappierContent]],
                            media_content: List[Union[YouTubeVideo, ExtractedContent]]) -> List[Dict[str, Any]]:
        """Extract key entities from all content"""
        entities = {}
        
        # Extract from academic papers
        for paper in academic_papers:
            for author in paper.authors:
                name = author.get('name', '') if isinstance(author, dict) else str(author)
                if name:
                    entities.setdefault(name, {'type': 'person', 'count': 0})
                    entities[name]['count'] += 1
        
        # Extract from news articles
        for article in news_articles:
            if isinstance(article, DappierContent) and article.entities:
                for entity in article.entities:
                    name = entity.get('name', '')
                    entity_type = entity.get('type', 'unknown')
                    if name:
                        entities.setdefault(name, {'type': entity_type, 'count': 0})
                        entities[name]['count'] += 1
        
        # Sort by frequency
        sorted_entities = sorted(
            [{'name': k, **v} for k, v in entities.items()],
            key=lambda x: x['count'],
            reverse=True
        )
        
        return sorted_entities[:20]  # Top 20 entities
    
    def _calculate_trending_score(self, 
                                academic_count: int,
                                news_count: int,
                                media_count: int,
                                time_range_days: int) -> float:
        """Calculate trending score based on content volume"""
        # Normalize by time range
        daily_rate = (academic_count + news_count + media_count) / max(time_range_days, 1)
        
        # Weight different content types
        weighted_score = (
            academic_count * 2.0 +  # Academic papers weighted higher
            news_count * 1.0 +
            media_count * 1.5
        ) / time_range_days
        
        # Normalize to 0-1 range
        return min(weighted_score / 10.0, 1.0)
    
    def _find_cross_references(self,
                             academic_papers: List[SemanticScholarPaper],
                             news_articles: List[Union[NewsArticle, DappierContent]],
                             media_content: List[Union[YouTubeVideo, ExtractedContent]]) -> List[Dict[str, Any]]:
        """Find cross-references between different content types"""
        cross_refs = []
        
        # Create lookup dictionaries
        paper_titles = {p.title.lower(): p for p in academic_papers}
        paper_authors = {}
        for paper in academic_papers:
            for author in paper.authors:
                name = author.get('name', '').lower() if isinstance(author, dict) else str(author).lower()
                if name:
                    paper_authors.setdefault(name, []).append(paper)
        
        # Check news articles for academic references
        for article in news_articles:
            content = article.title + " " + article.description
            content_lower = content.lower()
            
            # Check for paper title mentions
            for title, paper in paper_titles.items():
                if title in content_lower:
                    cross_refs.append({
                        'type': 'news_cites_paper',
                        'source': article,
                        'target': paper,
                        'confidence': 0.8
                    })
            
            # Check for author mentions
            for author, papers in paper_authors.items():
                if author in content_lower:
                    for paper in papers:
                        cross_refs.append({
                            'type': 'news_mentions_author',
                            'source': article,
                            'target': paper,
                            'author': author,
                            'confidence': 0.6
                        })
        
        return cross_refs[:50]  # Limit to top 50 cross-references
    
    def _extract_topics_from_transcript(self, chunks) -> List[str]:
        """Extract potential topics from video transcript chunks"""
        # Simple implementation - in practice, use NLP
        word_freq = {}
        for chunk in chunks:
            words = chunk.text.lower().split()
            for word in words:
                if len(word) > 5:  # Simple filter
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top frequent words as topics
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq > 3]
    
    def _extract_stock_symbols(self, text: str) -> List[str]:
        """Extract potential stock symbols from text"""
        import re
        # Simple pattern for stock symbols (1-5 uppercase letters)
        pattern = r'\b[A-Z]{1,5}\b'
        potential_symbols = re.findall(pattern, text)
        
        # Filter common words
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'WITH', 'FROM', 'THIS', 'THAT'}
        symbols = [s for s in potential_symbols if s not in common_words]
        
        return symbols[:5]  # Limit to 5 symbols
    
    # Additional helper methods for specific analyses...
    
    async def _get_academic_discourse(self, topic: str, start_date: datetime, end_date: datetime):
        """Get academic papers for discourse analysis"""
        async with self.clients['semantic_scholar'].connect() as client:
            response = await client.search_papers(
                topic,
                limit=50,
                year=f"{start_date.year}-{end_date.year}"
            )
            return response.data if response.success else []
    
    async def _get_google_news_discourse(self, topic: str, days: int):
        """Get Google News articles for discourse analysis"""
        async with self.clients['google_news'].connect() as client:
            time_range = "week" if days <= 7 else "month" if days <= 30 else "year"
            response = await client.search_news(topic, limit=50, time_range=time_range)
            return response.data if response.success else []
    
    async def _get_dappier_discourse(self, topic: str, start_date: datetime, end_date: datetime):
        """Get Dappier content for discourse analysis"""
        async with self.clients['dappier'].connect() as client:
            response = await client.search_content(
                topic,
                limit=50,
                date_from=start_date,
                date_to=end_date
            )
            return response.data if response.success else []
    
    async def _aggregate_news_discourse(self, news_tasks):
        """Aggregate news from multiple sources"""
        results = await asyncio.gather(*news_tasks, return_exceptions=True)
        aggregated = []
        for result in results:
            if not isinstance(result, Exception) and result:
                aggregated.extend(result)
        return aggregated
    
    async def _get_youtube_discourse(self, topic: str):
        """Get YouTube videos for discourse analysis"""
        # This would need integration with YouTube search API
        # For now, return empty list
        return []
    
    async def _analyze_sentiment(self, topic: str, days: int):
        """Analyze sentiment using Dappier"""
        async with self.clients['dappier'].connect() as client:
            time_range = "week" if days <= 7 else "month" if days <= 30 else "year"
            response = await client.analyze_sentiment(topic, time_range=time_range)
            return response.data if response.success else {}