"""
Compatibility module for t34_edge_builder.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t34_edge_builder_unified import *

# Backward compatibility aliases
EdgeBuilder = T34EdgeBuilderUnified