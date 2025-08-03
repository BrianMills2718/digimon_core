"""
Compatibility module for t23c_llm_entity_extractor.

This module provides backward compatibility by importing from phase2 implementation.
"""

# Import from phase2 ontology-aware extractor as compatibility
try:
    from ..phase2.t23c_ontology_aware_extractor_unified import *
    # Try to find the correct class name
    if 'T23COntologyAwareExtractorUnified' in globals():
        LLMEntityExtractor = T23COntologyAwareExtractorUnified
    else:
        # Create fallback class
        class LLMEntityExtractor:
            def __init__(self):
                self.tool_id = "T23C_LLM_ENTITY_EXTRACTOR"
except ImportError:
    try:
        from ..phase2.t23c_ontology_aware_extractor import *
        # Fallback alias if unified doesn't exist
        if 'T23COntologyAwareExtractor' in globals():
            LLMEntityExtractor = T23COntologyAwareExtractor
        else:
            raise ImportError
    except ImportError:
        # Create placeholder if nothing works
        class LLMEntityExtractor:
            def __init__(self):
                self.tool_id = "T23C_LLM_ENTITY_EXTRACTOR"