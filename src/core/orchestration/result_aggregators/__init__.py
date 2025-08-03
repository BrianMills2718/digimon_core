"""Result Aggregators - Data aggregation and consolidation

Provides aggregation components for consolidating pipeline results:
- SimpleAggregator: Basic aggregation for sequential results  
- GraphAggregator: Graph-based aggregation for complex relationships
"""

from .simple_aggregator import SimpleAggregator
from .graph_aggregator import GraphAggregator

__all__ = ['SimpleAggregator', 'GraphAggregator']