"""
Phase 3: Multi-Document GraphRAG Tools
Basic implementation with 100% reliability focus.
"""

# Import basic workflow (working)
from .basic_multi_document_workflow import BasicMultiDocumentWorkflow

# TODO: Import advanced t301 tools when relative import issues are resolved
# from .t301_multi_document_fusion import (
#     MultiDocumentFusion,
#     FusionResult,
#     ConsistencyMetrics,
#     EntityCluster
# )

__all__ = [
    'BasicMultiDocumentWorkflow',
    # 'MultiDocumentFusion',
    # 'FusionResult', 
    # 'ConsistencyMetrics',
    # 'EntityCluster'
]