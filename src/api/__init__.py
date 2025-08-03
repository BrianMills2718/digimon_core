"""
KGAS REST API Module

Provides local REST API endpoints for cross-modal analysis operations.
This complements the MCP interface by enabling:
- Custom web UIs
- Script automation
- Tool integration
- Batch processing

All endpoints are localhost-only for security.
"""

from .cross_modal_api import app, AnalyzeRequest, ConvertRequest, RecommendRequest

__all__ = [
    "app",
    "AnalyzeRequest", 
    "ConvertRequest",
    "RecommendRequest"
]