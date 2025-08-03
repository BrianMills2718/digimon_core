"""
Compatibility module for t01_pdf_processor.

This module provides backward compatibility by importing from the unified implementation.
"""

# Import everything from the unified implementation
from .t01_pdf_loader_unified import *

# Backward compatibility aliases - both names map to same implementation
PDFProcessor = T01PDFLoaderUnified
PDFLoader = T01PDFLoaderUnified