"""
YouTube MCP Client

Client for the youtube_mcp server providing access to:
- YouTube video transcriptions using OpenAI Whisper
- Video metadata extraction
- Transcript chunking for long videos
- Multi-language support

Based on: format37/youtube_mcp
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from .http_client import HTTPMCPClient
from .base_client import MCPResponse
from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
import logging

logger = logging.getLogger(__name__)


@dataclass
class YouTubeTranscriptChunk:
    """A chunk of YouTube transcript"""
    chunk_id: int
    start_time: float
    end_time: float
    text: str
    word_count: int


@dataclass
class YouTubeVideo:
    """YouTube video metadata and transcript"""
    video_id: str
    title: str
    author: str
    duration: int  # seconds
    upload_date: Optional[datetime]
    description: str
    view_count: int
    like_count: int
    transcript_chunks: List[YouTubeTranscriptChunk]
    language: str
    total_words: int


@dataclass
class YouTubeChannel:
    """YouTube channel information"""
    channel_id: str
    channel_name: str
    subscriber_count: int
    video_count: int
    description: str


class YouTubeMCPClient(HTTPMCPClient):
    """
    MCP client for YouTube video transcription and analysis.
    
    Provides access to:
    - High-quality transcriptions using OpenAI Whisper
    - Video metadata and statistics
    - Channel information
    - Transcript search and analysis
    """
    
    def __init__(self,
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 openai_api_key: Optional[str] = None,
                 server_url: str = "http://localhost:8002"):
        """
        Initialize YouTube MCP client.
        
        Args:
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            openai_api_key: Optional OpenAI API key for Whisper
            server_url: MCP server URL
        """
        config = {}
        if openai_api_key:
            config['headers'] = {'X-OpenAI-API-Key': openai_api_key}
        
        super().__init__(
            server_name="youtube",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            config=config
        )
    
    async def transcribe_video(self, 
                             video_url: str,
                             language: Optional[str] = None,
                             chunk_size: int = 1000) -> MCPResponse[YouTubeVideo]:
        """
        Transcribe a YouTube video using Whisper.
        
        Args:
            video_url: YouTube video URL
            language: Language code (e.g., 'en', 'es') - auto-detected if not specified
            chunk_size: Words per chunk for long videos
            
        Returns:
            MCPResponse containing video metadata and transcript
        """
        params = {
            "video_url": video_url,
            "chunk_size": chunk_size
        }
        
        if language:
            params["language"] = language
        
        response = await self.call_method("transcribe_video", params)
        
        if response.success and response.data:
            video = self._parse_video(response.data)
            return MCPResponse(success=True, data=video, metadata=response.metadata)
        
        return response
    
    async def get_video_metadata(self, video_url: str) -> MCPResponse[Dict[str, Any]]:
        """
        Get video metadata without transcribing.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            MCPResponse containing video metadata
        """
        params = {"video_url": video_url}
        
        response = await self.call_method("get_video_metadata", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("metadata", {}),
                metadata=response.metadata
            )
        
        return response
    
    async def search_video_transcript(self,
                                    video_url: str,
                                    search_terms: List[str],
                                    context_words: int = 50) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Search for terms within a video transcript.
        
        Args:
            video_url: YouTube video URL
            search_terms: List of terms to search for
            context_words: Number of words of context around matches
            
        Returns:
            MCPResponse containing search results with timestamps
        """
        params = {
            "video_url": video_url,
            "search_terms": search_terms,
            "context_words": context_words
        }
        
        response = await self.call_method("search_transcript", params)
        
        if response.success and response.data:
            return MCPResponse(
                success=True,
                data=response.data.get("matches", []),
                metadata=response.metadata
            )
        
        return response
    
    async def get_channel_videos(self,
                               channel_url: str,
                               limit: int = 10,
                               sort_by: str = "newest") -> MCPResponse[List[Dict[str, Any]]]:
        """
        Get list of videos from a YouTube channel.
        
        Args:
            channel_url: YouTube channel URL
            limit: Maximum number of videos to return
            sort_by: Sort order - "newest", "oldest", "popular"
            
        Returns:
            MCPResponse containing list of video metadata
        """
        params = {
            "channel_url": channel_url,
            "limit": limit,
            "sort_by": sort_by
        }
        
        response = await self.call_method("get_channel_videos", params)
        
        if response.success and response.data:
            return MCPResponse(
                success=True,
                data=response.data.get("videos", []),
                metadata=response.metadata
            )
        
        return response
    
    async def transcribe_playlist(self,
                                playlist_url: str,
                                max_videos: int = 10) -> MCPResponse[List[YouTubeVideo]]:
        """
        Transcribe multiple videos from a playlist.
        
        Args:
            playlist_url: YouTube playlist URL
            max_videos: Maximum number of videos to transcribe
            
        Returns:
            MCPResponse containing list of transcribed videos
        """
        params = {
            "playlist_url": playlist_url,
            "max_videos": max_videos
        }
        
        response = await self.call_method("transcribe_playlist", params)
        
        if response.success and response.data:
            videos = [self._parse_video(v) for v in response.data.get("videos", [])]
            return MCPResponse(success=True, data=videos, metadata=response.metadata)
        
        return response
    
    async def get_transcript_summary(self,
                                   video_url: str,
                                   summary_length: int = 500) -> MCPResponse[Dict[str, Any]]:
        """
        Get a summary of a video transcript.
        
        Args:
            video_url: YouTube video URL
            summary_length: Target summary length in words
            
        Returns:
            MCPResponse containing transcript summary
        """
        params = {
            "video_url": video_url,
            "summary_length": summary_length
        }
        
        response = await self.call_method("get_transcript_summary", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("summary", {}),
                metadata=response.metadata
            )
        
        return response
    
    async def extract_timestamps(self,
                                video_url: str,
                                topics: List[str]) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Extract timestamps for specific topics in a video.
        
        Args:
            video_url: YouTube video URL
            topics: List of topics to find timestamps for
            
        Returns:
            MCPResponse containing topic timestamps
        """
        params = {
            "video_url": video_url,
            "topics": topics
        }
        
        response = await self.call_method("extract_timestamps", params)
        
        if response.success and response.data:
            return MCPResponse(
                success=True,
                data=response.data.get("timestamps", []),
                metadata=response.metadata
            )
        
        return response
    
    # Helper Methods
    
    def _parse_video(self, data: Dict[str, Any]) -> YouTubeVideo:
        """Parse video data from MCP response"""
        # Parse upload date
        upload_date = None
        if data.get("upload_date"):
            try:
                upload_date = datetime.fromisoformat(data["upload_date"])
            except:
                pass
        
        # Parse transcript chunks
        chunks = []
        for chunk_data in data.get("transcript_chunks", []):
            chunk = YouTubeTranscriptChunk(
                chunk_id=chunk_data.get("chunk_id", 0),
                start_time=chunk_data.get("start_time", 0.0),
                end_time=chunk_data.get("end_time", 0.0),
                text=chunk_data.get("text", ""),
                word_count=chunk_data.get("word_count", 0)
            )
            chunks.append(chunk)
        
        return YouTubeVideo(
            video_id=data.get("video_id", ""),
            title=data.get("title", ""),
            author=data.get("author", ""),
            duration=data.get("duration", 0),
            upload_date=upload_date,
            description=data.get("description", ""),
            view_count=data.get("view_count", 0),
            like_count=data.get("like_count", 0),
            transcript_chunks=chunks,
            language=data.get("language", "en"),
            total_words=data.get("total_words", 0)
        )
    
    def format_timestamp(self, seconds: float) -> str:
        """Format seconds into YouTube timestamp format (HH:MM:SS)"""
        td = timedelta(seconds=int(seconds))
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        seconds = td.seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"