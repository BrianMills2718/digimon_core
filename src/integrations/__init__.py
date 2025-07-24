"""
Integrations Package

Provides unified access to external APIs and MCP servers.
"""

from .mcp import (
    MCPOrchestrator,
    SemanticScholarMCPClient,
    ArXivLatexMCPClient,
    YouTubeMCPClient,
    GoogleNewsMCPClient,
    DappierMCPClient,
    ContentCoreMCPClient
)

# Legacy direct API clients (being phased out in favor of MCP)
from .academic_apis.arxiv_client import ArXivClient
from .academic_apis.pubmed_client import PubMedClient

__all__ = [
    # MCP Clients
    'MCPOrchestrator',
    'SemanticScholarMCPClient',
    'ArXivLatexMCPClient',
    'YouTubeMCPClient',
    'GoogleNewsMCPClient',
    'DappierMCPClient',
    'ContentCoreMCPClient',
    
    # Legacy clients
    'ArXivClient',
    'PubMedClient'
]