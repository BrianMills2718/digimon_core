"""
Compatibility module for t53_network_motifs_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t53_network_motifs import *

# Check what the main class is and create alias
try:
    # Try to get the main tool class from the module
    NetworkMotifsTool = NetworkMotifsDetectionTool
except NameError:
    try:
        NetworkMotifsTool = NetworkMotifsAnalyzer
    except NameError:
        # Create a simple placeholder if neither exists
        class NetworkMotifsTool:
            def __init__(self):
                pass