"""
Fusion Algorithms Package

This package contains the core algorithms for multi-document fusion:
- EntitySimilarityCalculator: Calculate entity similarity scores
- EntityClusterFinder: Find clusters of similar entities  
- ConflictResolver: Resolve conflicts between entities
- RelationshipMerger: Merge relationships from multiple sources
- ConsistencyChecker: Check temporal and logical consistency
"""

from .entity_similarity import EntitySimilarityCalculator
from .entity_clustering import EntityClusterFinder
from .conflict_resolution import ConflictResolver
from .relationship_merger import RelationshipMerger
from .consistency_checker import ConsistencyChecker

__all__ = [
    'EntitySimilarityCalculator',
    'EntityClusterFinder', 
    'ConflictResolver',
    'RelationshipMerger',
    'ConsistencyChecker'
]