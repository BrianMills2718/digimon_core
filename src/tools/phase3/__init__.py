"""
Phase 3: Advanced GraphRAG Tools
Multi-document fusion and advanced reasoning capabilities.
"""

from .t301_multi_document_fusion import (
    MultiDocumentFusion,
    FusionResult,
    ConsistencyMetrics,
    EntityCluster
)

__all__ = [
    'MultiDocumentFusion',
    'FusionResult', 
    'ConsistencyMetrics',
    'EntityCluster'
]