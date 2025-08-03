"""
Test Mocks Package

This package contains mock implementations for testing only.
These classes should NEVER be imported by production code.
"""

# Prevent accidental imports in production
import os
import sys

# Check if we're in a test context
if 'pytest' not in sys.modules and not os.environ.get('TESTING'):
    raise ImportError(
        "Mock classes are for testing only and should not be imported in production. "
        "Set TESTING=1 environment variable if this is intentional."
    )

from .llm_mock_provider import MockAPIProvider

__all__ = ['MockAPIProvider']