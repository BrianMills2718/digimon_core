"""
Intelligent Document Clustering Module

This module provides intelligent clustering capabilities for documents
based on content, temporal patterns, authorship, and citation networks.
"""

from .intelligent_clusterer import IntelligentClusterer
from .similarity_calculator import SimilarityCalculator
from .cluster_optimizer import ClusterOptimizer
from .cluster_evaluator import ClusterEvaluator

__all__ = [
    "IntelligentClusterer",
    "SimilarityCalculator", 
    "ClusterOptimizer",
    "ClusterEvaluator"
]