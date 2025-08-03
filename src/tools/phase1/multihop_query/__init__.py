"""
Multi-hop Query Unified Tool - Decomposed Components

Modular architecture for multi-hop graph querying with Neo4j integration.
Decomposed from 792-line monolithic file into focused components.
"""

# Export main tool class
from .multihop_query_tool import T49MultiHopQueryUnified

# Export supporting classes for testing and extension
from .query_entity_extractor import QueryEntityExtractor
from .path_finder import PathFinder
from .result_ranker import ResultRanker
from .query_analyzer import QueryAnalyzer
from .connection_manager import Neo4jConnectionManager

__all__ = [
    "T49MultiHopQueryUnified",
    "QueryEntityExtractor",
    "PathFinder",
    "ResultRanker", 
    "QueryAnalyzer",
    "Neo4jConnectionManager"
]

def get_multihop_query_info():
    """Get information about the multi-hop query tool implementation"""
    return {
        "module": "multihop_query",
        "version": "2.0.0",
        "architecture": "decomposed_components", 
        "description": "Multi-hop graph query tool with modular architecture",
        "capabilities": [
            "natural_language_entity_extraction",
            "multi_hop_path_finding",
            "pagerank_weighted_ranking",
            "path_explanation_generation",
            "neo4j_graph_querying",
            "confidence_scoring",
            "query_complexity_analysis"
        ],
        "components": {
            "multihop_query_tool": "Main tool interface implementing BaseTool protocol",
            "query_entity_extractor": "Natural language entity extraction from queries",
            "path_finder": "Multi-hop path discovery between entities",
            "result_ranker": "PageRank-weighted result ranking and scoring",
            "query_analyzer": "Query complexity analysis and statistics",
            "connection_manager": "Neo4j connection and session management"
        },
        "decomposed": True,
        "file_count": 6,
        "total_lines": 90  # This main file line count
    }