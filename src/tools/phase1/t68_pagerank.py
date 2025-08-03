"""
Compatibility module for t68_pagerank.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t68_pagerank_unified import *

# Backward compatibility aliases
PageRankCalculator = T68PageRankCalculatorUnified