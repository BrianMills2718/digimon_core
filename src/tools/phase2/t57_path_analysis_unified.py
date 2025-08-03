"""
Compatibility module for t57_path_analysis_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t57_path_analysis import *

# Add missing dataclass for compatibility
from dataclasses import dataclass
from typing import List, Any

@dataclass
class PathInstance:
    """Represents a path instance in the graph."""
    nodes: List[str]
    edges: List[str] 
    path_length: int
    total_weight: float
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}