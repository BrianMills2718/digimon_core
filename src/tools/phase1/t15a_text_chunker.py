"""
Compatibility module for t15a_text_chunker.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t15a_text_chunker_unified import *

# Backward compatibility aliases
TextChunker = T15ATextChunkerUnified