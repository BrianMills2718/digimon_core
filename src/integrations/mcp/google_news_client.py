"""
Google News MCP Client

Client for the google-news-mcp-server providing access to:
- Google News search with automatic categorization
- Multi-language support
- Headlines, stories, and related topics
- News clustering and trending analysis

Based on: chanmeng/google-news-mcp-server
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .http_client import HTTPMCPClient
from .base_client import MCPResponse
from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
import logging

logger = logging.getLogger(__name__)


class NewsCategory(Enum):
    """Google News categories"""
    WORLD = "World"
    NATION = "Nation"
    BUSINESS = "Business"
    TECHNOLOGY = "Technology"
    ENTERTAINMENT = "Entertainment"
    SCIENCE = "Science"
    SPORTS = "Sports"
    HEALTH = "Health"


@dataclass
class NewsArticle:
    """News article representation"""
    title: str
    link: str
    source: str
    published_date: datetime
    description: str
    category: str
    related_topics: List[str]
    image_url: Optional[str]
    author: Optional[str]
    language: str


@dataclass
class NewsCluster:
    """Cluster of related news articles"""
    cluster_id: str
    main_story: NewsArticle
    related_stories: List[NewsArticle]
    trending_score: float
    keywords: List[str]


@dataclass
class NewsTopic:
    """Trending news topic"""
    topic_name: str
    topic_type: str  # event, person, organization, location
    articles_count: int
    trending_score: float
    related_keywords: List[str]
    time_range: Dict[str, datetime]


class GoogleNewsMCPClient(HTTPMCPClient):
    """
    MCP client for Google News integration via SerpAPI.
    
    Provides access to:
    - Real-time news search across multiple sources
    - Category-based news browsing
    - Multi-language news content
    - Trending topics and stories
    - News clustering for related stories
    """
    
    def __init__(self,
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 serp_api_key: str,
                 server_url: str = "http://localhost:8003"):
        """
        Initialize Google News MCP client.
        
        Args:
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            serp_api_key: SerpAPI key for Google News access
            server_url: MCP server URL
        """
        config = {
            'headers': {'X-SERP-API-Key': serp_api_key}
        }
        
        super().__init__(
            server_name="google_news",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            config=config
        )
    
    async def search_news(self,
                         query: str,
                         language: str = "en",
                         location: Optional[str] = None,
                         time_range: Optional[str] = None,
                         limit: int = 10) -> MCPResponse[List[NewsArticle]]:
        """
        Search Google News for articles.
        
        Args:
            query: Search query
            language: Language code (e.g., 'en', 'es', 'fr')
            location: Location for localized results (e.g., 'United States')
            time_range: Time range filter ('hour', 'day', 'week', 'month', 'year')
            limit: Maximum number of results
            
        Returns:
            MCPResponse containing list of news articles
        """
        params = {
            "query": query,
            "language": language,
            "limit": limit
        }
        
        if location:
            params["location"] = location
        if time_range:
            params["time_range"] = time_range
        
        response = await self.call_method("search_news", params)
        
        if response.success and response.data:
            articles = [self._parse_article(a) for a in response.data.get("articles", [])]
            return MCPResponse(success=True, data=articles, metadata=response.metadata)
        
        return response
    
    async def get_headlines(self,
                          category: Optional[NewsCategory] = None,
                          language: str = "en",
                          location: Optional[str] = None,
                          limit: int = 10) -> MCPResponse[List[NewsArticle]]:
        """
        Get top headlines from Google News.
        
        Args:
            category: News category filter
            language: Language code
            location: Location for localized headlines
            limit: Maximum number of headlines
            
        Returns:
            MCPResponse containing headline articles
        """
        params = {
            "language": language,
            "limit": limit
        }
        
        if category:
            params["category"] = category.value
        if location:
            params["location"] = location
        
        response = await self.call_method("get_headlines", params)
        
        if response.success and response.data:
            articles = [self._parse_article(a) for a in response.data.get("headlines", [])]
            return MCPResponse(success=True, data=articles, metadata=response.metadata)
        
        return response
    
    async def get_topic_stories(self,
                              topic: str,
                              language: str = "en",
                              limit: int = 10) -> MCPResponse[NewsCluster]:
        """
        Get clustered stories for a specific topic.
        
        Args:
            topic: Topic to get stories for
            language: Language code
            limit: Maximum number of story clusters
            
        Returns:
            MCPResponse containing news cluster
        """
        params = {
            "topic": topic,
            "language": language,
            "limit": limit
        }
        
        response = await self.call_method("get_topic_stories", params)
        
        if response.success and response.data:
            cluster = self._parse_cluster(response.data)
            return MCPResponse(success=True, data=cluster, metadata=response.metadata)
        
        return response
    
    async def get_trending_topics(self,
                                language: str = "en",
                                location: Optional[str] = None,
                                time_range: str = "day") -> MCPResponse[List[NewsTopic]]:
        """
        Get trending topics from Google News.
        
        Args:
            language: Language code
            location: Location for localized trends
            time_range: Time range for trends ('hour', 'day', 'week')
            
        Returns:
            MCPResponse containing trending topics
        """
        params = {
            "language": language,
            "time_range": time_range
        }
        
        if location:
            params["location"] = location
        
        response = await self.call_method("get_trending_topics", params)
        
        if response.success and response.data:
            topics = [self._parse_topic(t) for t in response.data.get("topics", [])]
            return MCPResponse(success=True, data=topics, metadata=response.metadata)
        
        return response
    
    async def get_related_articles(self,
                                 article_url: str,
                                 limit: int = 5) -> MCPResponse[List[NewsArticle]]:
        """
        Get articles related to a specific article.
        
        Args:
            article_url: URL of the source article
            limit: Maximum number of related articles
            
        Returns:
            MCPResponse containing related articles
        """
        params = {
            "article_url": article_url,
            "limit": limit
        }
        
        response = await self.call_method("get_related_articles", params)
        
        if response.success and response.data:
            articles = [self._parse_article(a) for a in response.data.get("related", [])]
            return MCPResponse(success=True, data=articles, metadata=response.metadata)
        
        return response
    
    async def get_news_by_location(self,
                                 location: str,
                                 category: Optional[NewsCategory] = None,
                                 language: str = "en",
                                 limit: int = 10) -> MCPResponse[List[NewsArticle]]:
        """
        Get news specific to a geographic location.
        
        Args:
            location: Geographic location (country, city, region)
            category: Optional category filter
            language: Language code
            limit: Maximum number of articles
            
        Returns:
            MCPResponse containing location-specific news
        """
        params = {
            "location": location,
            "language": language,
            "limit": limit
        }
        
        if category:
            params["category"] = category.value
        
        response = await self.call_method("get_news_by_location", params)
        
        if response.success and response.data:
            articles = [self._parse_article(a) for a in response.data.get("articles", [])]
            return MCPResponse(success=True, data=articles, metadata=response.metadata)
        
        return response
    
    async def track_topic(self,
                        topic: str,
                        time_range: str = "week",
                        language: str = "en") -> MCPResponse[Dict[str, Any]]:
        """
        Track a topic's coverage over time.
        
        Args:
            topic: Topic to track
            time_range: Time range to analyze
            language: Language code
            
        Returns:
            MCPResponse containing topic tracking data
        """
        params = {
            "topic": topic,
            "time_range": time_range,
            "language": language
        }
        
        response = await self.call_method("track_topic", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("tracking", {}),
                metadata=response.metadata
            )
        
        return response
    
    # Helper Methods
    
    def _parse_article(self, data: Dict[str, Any]) -> NewsArticle:
        """Parse article data from MCP response"""
        # Parse published date
        published_date = datetime.now()
        if data.get("published_date"):
            try:
                published_date = datetime.fromisoformat(data["published_date"])
            except:
                pass
        
        return NewsArticle(
            title=data.get("title", ""),
            link=data.get("link", ""),
            source=data.get("source", ""),
            published_date=published_date,
            description=data.get("description", ""),
            category=data.get("category", ""),
            related_topics=data.get("related_topics", []),
            image_url=data.get("image_url"),
            author=data.get("author"),
            language=data.get("language", "en")
        )
    
    def _parse_cluster(self, data: Dict[str, Any]) -> NewsCluster:
        """Parse news cluster from MCP response"""
        main_story = self._parse_article(data.get("main_story", {}))
        related = [self._parse_article(a) for a in data.get("related_stories", [])]
        
        return NewsCluster(
            cluster_id=data.get("cluster_id", ""),
            main_story=main_story,
            related_stories=related,
            trending_score=data.get("trending_score", 0.0),
            keywords=data.get("keywords", [])
        )
    
    def _parse_topic(self, data: Dict[str, Any]) -> NewsTopic:
        """Parse trending topic from MCP response"""
        # Parse time range
        time_range = {}
        if data.get("time_range"):
            tr = data["time_range"]
            if tr.get("start"):
                time_range["start"] = datetime.fromisoformat(tr["start"])
            if tr.get("end"):
                time_range["end"] = datetime.fromisoformat(tr["end"])
        
        return NewsTopic(
            topic_name=data.get("topic_name", ""),
            topic_type=data.get("topic_type", ""),
            articles_count=data.get("articles_count", 0),
            trending_score=data.get("trending_score", 0.0),
            related_keywords=data.get("related_keywords", []),
            time_range=time_range
        )