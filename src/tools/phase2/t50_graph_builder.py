"""
Compatibility module for t50_graph_builder.

This module provides backward compatibility by importing from community detection.
"""

# Import from community detection as the graph builder functionality
from .t50_community_detection import *

# Backward compatibility aliases
GraphBuilder = CommunityDetectionTool