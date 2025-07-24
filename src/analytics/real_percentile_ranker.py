"""Real percentile ranking using statistical analysis and reference distributions"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any
import asyncio
from scipy import stats
import networkx as nx

logger = logging.getLogger(__name__)


class RealPercentileRanker:
    """Calculate real percentile ranks using reference distributions and statistical methods"""
    
    def __init__(self, neo4j_manager):
        """Initialize with Neo4j manager for database access.
        
        Args:
            neo4j_manager: Neo4j manager instance for querying reference data
        """
        self.neo4j_manager = neo4j_manager
        self.reference_distributions = {}
        self.distribution_cache_valid = False
        
    async def load_reference_distributions(self):
        """Load reference distributions from database"""
        logger.info("Loading reference distributions from database")
        
        metrics = ['h_index', 'citation_velocity', 'cross_disciplinary_impact', 
                  'citation_count', 'impact_factor', 'collaboration_count']
        
        for metric in metrics:
            try:
                # Query database for metric distribution
                query = f"""
                MATCH (e:Entity)
                WHERE e.{metric} IS NOT NULL
                RETURN e.{metric} as value
                ORDER BY value
                """
                
                result = await self.neo4j_manager.execute_read_query(query)
                values = [r['value'] for r in result if r['value'] is not None]
                
                if values and len(values) >= 10:  # Need minimum sample size
                    self.reference_distributions[metric] = np.array(values)
                    logger.info(f"Loaded {len(values)} reference values for {metric}")
                else:
                    # If insufficient real data, create synthetic distribution
                    logger.warning(f"Insufficient data for {metric}, using synthetic distribution")
                    self.reference_distributions[metric] = self._create_synthetic_distribution(metric)
                    
            except Exception as e:
                logger.error(f"Failed to load distribution for {metric}: {e}")
                self.reference_distributions[metric] = self._create_synthetic_distribution(metric)
        
        self.distribution_cache_valid = True
        logger.info(f"Loaded reference distributions for {len(self.reference_distributions)} metrics")
    
    def _create_synthetic_distribution(self, metric: str, size: int = 10000) -> np.ndarray:
        """Create synthetic distribution based on typical patterns.
        
        Args:
            metric: Metric name
            size: Number of samples to generate
            
        Returns:
            Synthetic distribution array
        """
        np.random.seed(42)  # Reproducible distributions
        
        if metric == 'h_index':
            # H-index typically follows power law / exponential decay
            # Most researchers have low h-index, few have very high
            values = np.random.exponential(scale=8, size=size)
            values = np.clip(values, 0, 100)  # Cap at realistic maximum
            
        elif metric == 'citation_velocity':
            # Citation velocity often log-normal
            # Most papers get few citations per year, some get many
            values = np.random.lognormal(mean=2.0, sigma=1.5, size=size)
            values = np.clip(values, 0, 500)
            
        elif metric == 'cross_disciplinary_impact':
            # Usually beta distribution (bounded 0-1)
            # Most work is within discipline, some is highly cross-disciplinary
            values = np.random.beta(a=2, b=5, size=size)
            
        elif metric == 'citation_count':
            # Heavy-tailed distribution (power law)
            # Most papers have few citations, very few have many
            values = np.random.pareto(a=1.5, size=size) * 10
            values = np.clip(values, 0, 10000)
            
        elif metric == 'impact_factor':
            # Log-normal distribution
            # Most journals have moderate IF, few have very high
            values = np.random.lognormal(mean=1.0, sigma=0.8, size=size)
            values = np.clip(values, 0.1, 50)
            
        elif metric == 'collaboration_count':
            # Poisson or negative binomial
            # Most researchers have moderate collaborations
            values = np.random.negative_binomial(n=10, p=0.3, size=size)
            
        else:
            # Generic beta distribution for unknown metrics
            values = np.random.beta(a=2, b=5, size=size)
        
        return np.sort(values)
    
    async def calculate_percentile_rank(self, score: float, metric: str) -> float:
        """Calculate real percentile rank for a score.
        
        Args:
            score: The score to rank
            metric: The metric name
            
        Returns:
            Percentile rank (0-100)
        """
        # Load distributions if not cached
        if not self.distribution_cache_valid:
            await self.load_reference_distributions()
        
        if metric not in self.reference_distributions:
            logger.warning(f"No reference distribution for {metric}, using conservative estimate")
            return 50.0  # Conservative middle ranking
        
        distribution = self.reference_distributions[metric]
        
        # Calculate percentile using empirical CDF
        percentile = stats.percentileofscore(distribution, score, kind='rank')
        
        # Apply smoothing for extreme values
        if percentile > 99:
            # Log scale for top 1% to differentiate extreme outliers
            excess = score / np.percentile(distribution, 99)
            percentile = min(99 + np.log10(excess), 100)
        elif percentile < 1:
            # Similar treatment for bottom 1%
            ratio = score / (np.percentile(distribution, 1) + 1e-6)
            percentile = max(ratio, 0)
        
        return float(percentile)
    
    async def calculate_percentile_ranks_batch(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate percentile ranks for multiple metrics.
        
        Args:
            scores: Dictionary mapping metric names to scores
            
        Returns:
            Dictionary mapping metric names to percentile ranks
        """
        percentiles = {}
        
        for metric, score in scores.items():
            if score is not None:
                percentiles[metric] = await self.calculate_percentile_rank(score, metric)
            else:
                percentiles[metric] = 0.0
        
        return percentiles
    
    async def calculate_collaboration_network_centrality(self, entity_id: str) -> float:
        """Calculate real network centrality in collaboration network.
        
        Args:
            entity_id: Entity ID to analyze
            
        Returns:
            Centrality score (0-1)
        """
        try:
            # Query collaboration network
            query = """
            // Get direct collaborators
            MATCH (e:Entity {id: $entity_id})-[:COLLABORATES_WITH]-(collaborator:Entity)
            WITH e, collect(DISTINCT collaborator) as direct_collaborators
            
            // Get extended network (2 hops)
            MATCH (e)-[:COLLABORATES_WITH*1..2]-(extended:Entity)
            WITH e, direct_collaborators, collect(DISTINCT extended) as extended_network
            
            // Get all collaboration edges in the subgraph
            UNWIND extended_network as n1
            MATCH (n1)-[r:COLLABORATES_WITH]-(n2:Entity)
            WHERE n2 IN extended_network
            RETURN 
                e.id as center_id,
                [c IN direct_collaborators | c.id] as direct_ids,
                [n IN extended_network | n.id] as network_ids,
                collect(DISTINCT {source: n1.id, target: n2.id}) as edges
            """
            
            result = await self.neo4j_manager.execute_read_query(
                query, {'entity_id': entity_id}
            )
            
            if not result:
                return 0.0
            
            data = result[0]
            network_ids = data.get('network_ids', [])
            edges = data.get('edges', [])
            
            if len(network_ids) < 2:
                return 0.0
            
            # Build NetworkX graph
            G = nx.Graph()
            
            # Add nodes
            for node_id in network_ids:
                G.add_node(node_id)
            
            # Add edges
            for edge in edges:
                if edge['source'] in network_ids and edge['target'] in network_ids:
                    G.add_edge(edge['source'], edge['target'])
            
            # Ensure entity is in graph
            if entity_id not in G:
                G.add_node(entity_id)
            
            # Calculate various centrality measures
            centrality_scores = []
            
            # Degree centrality
            degree_cent = nx.degree_centrality(G)
            centrality_scores.append(degree_cent.get(entity_id, 0))
            
            # Betweenness centrality
            if G.number_of_nodes() > 2:
                between_cent = nx.betweenness_centrality(G)
                centrality_scores.append(between_cent.get(entity_id, 0))
            
            # Closeness centrality
            if nx.is_connected(G):
                close_cent = nx.closeness_centrality(G)
                centrality_scores.append(close_cent.get(entity_id, 0))
            else:
                # Use subgraph containing the entity
                for component in nx.connected_components(G):
                    if entity_id in component:
                        subgraph = G.subgraph(component)
                        close_cent = nx.closeness_centrality(subgraph)
                        centrality_scores.append(close_cent.get(entity_id, 0))
                        break
            
            # Eigenvector centrality (if possible)
            try:
                if G.number_of_nodes() > 2 and G.number_of_edges() > 0:
                    eigen_cent = nx.eigenvector_centrality_numpy(G, max_iter=100)
                    centrality_scores.append(eigen_cent.get(entity_id, 0))
            except:
                pass  # Skip if computation fails
            
            # Return average of available centrality measures
            if centrality_scores:
                return float(np.mean(centrality_scores))
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate collaboration centrality: {e}")
            return 0.0
    
    async def get_field_statistics(self, field: str) -> Dict[str, float]:
        """Get statistical summary for a field.
        
        Args:
            field: Academic field/discipline
            
        Returns:
            Dictionary with statistical measures
        """
        try:
            query = """
            MATCH (e:Entity)
            WHERE e.field = $field AND e.h_index IS NOT NULL
            WITH e.h_index as h_index, e.citation_count as citations
            RETURN 
                avg(h_index) as mean_h_index,
                percentileCont(h_index, 0.5) as median_h_index,
                percentileCont(h_index, 0.25) as q1_h_index,
                percentileCont(h_index, 0.75) as q3_h_index,
                avg(citations) as mean_citations,
                percentileCont(citations, 0.5) as median_citations
            """
            
            result = await self.neo4j_manager.execute_read_query(
                query, {'field': field}
            )
            
            if result:
                return result[0]
            else:
                return {
                    'mean_h_index': 10.0,
                    'median_h_index': 8.0,
                    'q1_h_index': 4.0,
                    'q3_h_index': 15.0,
                    'mean_citations': 100.0,
                    'median_citations': 50.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get field statistics: {e}")
            return {}
    
    def calculate_relative_impact(self, score: float, field_stats: Dict[str, float], 
                                metric: str = 'h_index') -> float:
        """Calculate impact relative to field norms.
        
        Args:
            score: Individual's score
            field_stats: Field statistics
            metric: Metric to compare
            
        Returns:
            Relative impact score
        """
        field_median = field_stats.get(f'median_{metric}', 10.0)
        field_mean = field_stats.get(f'mean_{metric}', 10.0)
        
        if field_median > 0:
            # Calculate z-score relative to field
            relative_score = score / field_median
            
            # Apply log scaling for extreme values
            if relative_score > 3:
                relative_score = 3 + np.log(relative_score - 2)
            
            return relative_score
        else:
            return 1.0