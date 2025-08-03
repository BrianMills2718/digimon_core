"""
Phase 3: Multi-Document GraphRAG Tools
Now decomposed into focused, maintainable modules under 500 lines each.
"""

# Import decomposed components
from .data_models import FusionResult, ConsistencyMetrics, EntityCluster
from .fusion_coordinator import MultiDocumentFusionCoordinator  
from .document_ingestion import BasicMultiDocumentWorkflow
from .t301_multi_document_fusion import MultiDocumentFusion, T301MultiDocumentFusionTool

# Import algorithm components
from .fusion_algorithms import (
    EntitySimilarityCalculator,
    EntityClusterFinder,
    ConflictResolver,
    RelationshipMerger,
    ConsistencyChecker
)

__all__ = [
    # Main API classes
    'MultiDocumentFusion',
    'T301MultiDocumentFusionTool',
    'MultiDocumentFusionCoordinator',
    'BasicMultiDocumentWorkflow',
    
    # Data models
    'FusionResult',
    'ConsistencyMetrics', 
    'EntityCluster',
    
    # Algorithm components
    'EntitySimilarityCalculator',
    'EntityClusterFinder',
    'ConflictResolver',
    'RelationshipMerger',
    'ConsistencyChecker'
]