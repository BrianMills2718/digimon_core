"""
Compatibility module for t23a_spacy_ner.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t23a_spacy_ner_unified import *

# Backward compatibility aliases  
SpacyNER = T23ASpacyNERUnified