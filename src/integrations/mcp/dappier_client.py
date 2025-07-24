"""
DappierAI MCP Client

Client for the dappier-mcp server providing access to:
- Real-time web search across trusted media brands
- News, financial markets, sports, entertainment, weather data
- Premium content from verified sources
- Multi-domain discourse analysis

Based on: DappierAI/dappier-mcp
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .http_client import HTTPMCPClient
from .base_client import MCPResponse
from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
import logging

logger = logging.getLogger(__name__)


class ContentDomain(Enum):
    """Dappier content domains"""
    NEWS = "news"
    FINANCE = "finance"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    WEATHER = "weather"
    TECHNOLOGY = "technology"
    POLITICS = "politics"
    HEALTH = "health"
    SCIENCE = "science"


@dataclass
class DappierContent:
    """Base content from Dappier sources"""
    content_id: str
    title: str
    source: str
    source_reputation: float  # 0-1 trust score
    published_date: datetime
    url: str
    domain: ContentDomain
    summary: str
    full_text: Optional[str]
    author: Optional[str]
    tags: List[str]
    sentiment: Optional[Dict[str, float]]  # positive, negative, neutral scores
    entities: List[Dict[str, Any]]  # Named entities extracted
    metadata: Dict[str, Any]


@dataclass
class FinancialData:
    """Financial market data"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    news_sentiment: Dict[str, float]
    related_articles: List[DappierContent]


@dataclass
class SportsEvent:
    """Sports event data"""
    event_id: str
    sport: str
    league: str
    teams: List[str]
    score: Optional[Dict[str, int]]
    status: str  # scheduled, live, completed
    start_time: datetime
    venue: str
    related_articles: List[DappierContent]
    statistics: Dict[str, Any]


@dataclass
class WeatherData:
    """Weather information"""
    location: str
    current_temp: float
    conditions: str
    forecast: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    related_articles: List[DappierContent]


class DappierMCPClient(HTTPMCPClient):
    """
    MCP client for DappierAI multi-domain content access.
    
    Provides access to:
    - Trusted media sources across multiple domains
    - Real-time data feeds
    - Premium content with source verification
    - Cross-domain discourse analysis
    """
    
    def __init__(self,
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 api_key: str,
                 server_url: str = "http://localhost:8004"):
        """
        Initialize Dappier MCP client.
        
        Args:
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            api_key: DappierAI API key
            server_url: MCP server URL
        """
        config = {
            'headers': {'X-Dappier-API-Key': api_key}
        }
        
        super().__init__(
            server_name="dappier",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            config=config
        )
    
    async def search_content(self,
                           query: str,
                           domains: Optional[List[ContentDomain]] = None,
                           sources: Optional[List[str]] = None,
                           date_from: Optional[datetime] = None,
                           date_to: Optional[datetime] = None,
                           min_reputation: float = 0.7,
                           limit: int = 20) -> MCPResponse[List[DappierContent]]:
        """
        Search across all Dappier content sources.
        
        Args:
            query: Search query
            domains: List of content domains to search
            sources: Specific sources to include
            date_from: Start date filter
            date_to: End date filter
            min_reputation: Minimum source reputation score (0-1)
            limit: Maximum results
            
        Returns:
            MCPResponse containing search results
        """
        params = {
            "query": query,
            "min_reputation": min_reputation,
            "limit": limit
        }
        
        if domains:
            params["domains"] = [d.value for d in domains]
        if sources:
            params["sources"] = sources
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        response = await self.call_method("search_content", params)
        
        if response.success and response.data:
            content = [self._parse_content(c) for c in response.data.get("results", [])]
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def get_trending_topics(self,
                                domains: Optional[List[ContentDomain]] = None,
                                time_range: str = "day",
                                limit: int = 10) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Get trending topics across domains.
        
        Args:
            domains: Domains to get trends from
            time_range: Time range ('hour', 'day', 'week')
            limit: Maximum topics
            
        Returns:
            MCPResponse containing trending topics
        """
        params = {
            "time_range": time_range,
            "limit": limit
        }
        
        if domains:
            params["domains"] = [d.value for d in domains]
        
        response = await self.call_method("get_trending_topics", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("topics", []),
                metadata=response.metadata
            )
        
        return response
    
    async def get_financial_data(self,
                               symbols: List[str],
                               include_news: bool = True) -> MCPResponse[List[FinancialData]]:
        """
        Get financial market data and related news.
        
        Args:
            symbols: List of stock/crypto symbols
            include_news: Include related news articles
            
        Returns:
            MCPResponse containing financial data
        """
        params = {
            "symbols": symbols,
            "include_news": include_news
        }
        
        response = await self.call_method("get_financial_data", params)
        
        if response.success and response.data:
            data = [self._parse_financial_data(f) for f in response.data.get("financial", [])]
            return MCPResponse(success=True, data=data, metadata=response.metadata)
        
        return response
    
    async def get_sports_events(self,
                              sport: Optional[str] = None,
                              league: Optional[str] = None,
                              date: Optional[datetime] = None,
                              include_news: bool = True) -> MCPResponse[List[SportsEvent]]:
        """
        Get sports events and related content.
        
        Args:
            sport: Sport filter
            league: League filter
            date: Date filter
            include_news: Include related articles
            
        Returns:
            MCPResponse containing sports events
        """
        params = {
            "include_news": include_news
        }
        
        if sport:
            params["sport"] = sport
        if league:
            params["league"] = league
        if date:
            params["date"] = date.isoformat()
        
        response = await self.call_method("get_sports_events", params)
        
        if response.success and response.data:
            events = [self._parse_sports_event(e) for e in response.data.get("events", [])]
            return MCPResponse(success=True, data=events, metadata=response.metadata)
        
        return response
    
    async def get_weather_info(self,
                             locations: List[str],
                             include_news: bool = True) -> MCPResponse[List[WeatherData]]:
        """
        Get weather data and related content.
        
        Args:
            locations: List of locations
            include_news: Include weather-related news
            
        Returns:
            MCPResponse containing weather data
        """
        params = {
            "locations": locations,
            "include_news": include_news
        }
        
        response = await self.call_method("get_weather_info", params)
        
        if response.success and response.data:
            weather = [self._parse_weather_data(w) for w in response.data.get("weather", [])]
            return MCPResponse(success=True, data=weather, metadata=response.metadata)
        
        return response
    
    async def analyze_sentiment(self,
                              topic: str,
                              domains: Optional[List[ContentDomain]] = None,
                              time_range: str = "week") -> MCPResponse[Dict[str, Any]]:
        """
        Analyze sentiment across sources for a topic.
        
        Args:
            topic: Topic to analyze
            domains: Domains to include
            time_range: Time range for analysis
            
        Returns:
            MCPResponse containing sentiment analysis
        """
        params = {
            "topic": topic,
            "time_range": time_range
        }
        
        if domains:
            params["domains"] = [d.value for d in domains]
        
        response = await self.call_method("analyze_sentiment", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("sentiment", {}),
                metadata=response.metadata
            )
        
        return response
    
    async def get_entity_mentions(self,
                                entity_name: str,
                                entity_type: str,
                                domains: Optional[List[ContentDomain]] = None,
                                limit: int = 20) -> MCPResponse[List[DappierContent]]:
        """
        Find mentions of specific entities across sources.
        
        Args:
            entity_name: Entity name to search
            entity_type: Entity type (person, organization, location, etc.)
            domains: Domains to search
            limit: Maximum results
            
        Returns:
            MCPResponse containing entity mentions
        """
        params = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "limit": limit
        }
        
        if domains:
            params["domains"] = [d.value for d in domains]
        
        response = await self.call_method("get_entity_mentions", params)
        
        if response.success and response.data:
            content = [self._parse_content(c) for c in response.data.get("mentions", [])]
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def get_source_info(self, source_name: str) -> MCPResponse[Dict[str, Any]]:
        """
        Get information about a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            MCPResponse containing source information
        """
        params = {"source_name": source_name}
        
        response = await self.call_method("get_source_info", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("source", {}),
                metadata=response.metadata
            )
        
        return response
    
    # Helper Methods
    
    def _parse_content(self, data: Dict[str, Any]) -> DappierContent:
        """Parse content from MCP response"""
        # Parse published date
        published_date = datetime.now()
        if data.get("published_date"):
            try:
                published_date = datetime.fromisoformat(data["published_date"])
            except:
                pass
        
        # Parse domain
        domain = ContentDomain.NEWS
        if data.get("domain"):
            try:
                domain = ContentDomain(data["domain"])
            except:
                pass
        
        return DappierContent(
            content_id=data.get("content_id", ""),
            title=data.get("title", ""),
            source=data.get("source", ""),
            source_reputation=data.get("source_reputation", 0.0),
            published_date=published_date,
            url=data.get("url", ""),
            domain=domain,
            summary=data.get("summary", ""),
            full_text=data.get("full_text"),
            author=data.get("author"),
            tags=data.get("tags", []),
            sentiment=data.get("sentiment"),
            entities=data.get("entities", []),
            metadata=data.get("metadata", {})
        )
    
    def _parse_financial_data(self, data: Dict[str, Any]) -> FinancialData:
        """Parse financial data from MCP response"""
        related = []
        if data.get("related_articles"):
            related = [self._parse_content(a) for a in data["related_articles"]]
        
        return FinancialData(
            symbol=data.get("symbol", ""),
            name=data.get("name", ""),
            price=data.get("price", 0.0),
            change=data.get("change", 0.0),
            change_percent=data.get("change_percent", 0.0),
            volume=data.get("volume", 0),
            market_cap=data.get("market_cap"),
            pe_ratio=data.get("pe_ratio"),
            news_sentiment=data.get("news_sentiment", {}),
            related_articles=related
        )
    
    def _parse_sports_event(self, data: Dict[str, Any]) -> SportsEvent:
        """Parse sports event from MCP response"""
        # Parse start time
        start_time = datetime.now()
        if data.get("start_time"):
            try:
                start_time = datetime.fromisoformat(data["start_time"])
            except:
                pass
        
        related = []
        if data.get("related_articles"):
            related = [self._parse_content(a) for a in data["related_articles"]]
        
        return SportsEvent(
            event_id=data.get("event_id", ""),
            sport=data.get("sport", ""),
            league=data.get("league", ""),
            teams=data.get("teams", []),
            score=data.get("score"),
            status=data.get("status", ""),
            start_time=start_time,
            venue=data.get("venue", ""),
            related_articles=related,
            statistics=data.get("statistics", {})
        )
    
    def _parse_weather_data(self, data: Dict[str, Any]) -> WeatherData:
        """Parse weather data from MCP response"""
        related = []
        if data.get("related_articles"):
            related = [self._parse_content(a) for a in data["related_articles"]]
        
        return WeatherData(
            location=data.get("location", ""),
            current_temp=data.get("current_temp", 0.0),
            conditions=data.get("conditions", ""),
            forecast=data.get("forecast", []),
            alerts=data.get("alerts", []),
            related_articles=related
        )