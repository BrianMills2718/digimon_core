"""
Agent implementations for KGAS orchestration.

Includes both memory-aware agents and simple agents for different use cases.
Memory-aware agents learn from experience and adapt their behavior over time.
"""

# Memory-aware agents (Phase 1: Advanced Agent Features)
from .document_agent import DocumentAgent
from .analysis_agent import AnalysisAgent

# Simple agents (original implementations)
from .graph_agent import SimpleGraphAgent
from .insight_agent import SimpleInsightAgent

__all__ = [
    # Memory-aware agents
    "DocumentAgent",
    "AnalysisAgent",
    # Simple agents
    "SimpleGraphAgent", 
    "SimpleInsightAgent"
]