"""
Compatibility module for t49_multihop_query.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t49_multihop_query_unified import *

# Backward compatibility aliases
MultiHopQuery = T49MultiHopQueryUnified