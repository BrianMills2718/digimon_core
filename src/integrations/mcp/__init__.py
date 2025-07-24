"""
MCP Integration Package

Provides unified access to all MCP servers for discourse analysis.
"""

from .base_client import BaseMCPClient, MCPRequest, MCPResponse, MCPError
from .http_client import HTTPMCPClient
from .semantic_scholar_client import SemanticScholarMCPClient
from .arxiv_latex_client import ArXivLatexMCPClient
from .youtube_client import YouTubeMCPClient
from .google_news_client import GoogleNewsMCPClient
from .dappier_client import DappierMCPClient
from .content_core_client import ContentCoreMCPClient
from .orchestrator import MCPOrchestrator

__all__ = [
    'BaseMCPClient',
    'MCPRequest',
    'MCPResponse',
    'MCPError',
    'HTTPMCPClient',
    'SemanticScholarMCPClient',
    'ArXivLatexMCPClient',
    'YouTubeMCPClient',
    'GoogleNewsMCPClient',
    'DappierMCPClient',
    'ContentCoreMCPClient',
    'MCPOrchestrator'
]