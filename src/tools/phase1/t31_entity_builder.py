"""
Compatibility module for t31_entity_builder.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t31_entity_builder_unified import *

# Backward compatibility aliases
EntityBuilder = T31EntityBuilderUnified