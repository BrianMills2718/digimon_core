#!/usr/bin/env python3
"""
Graph Centrality Analyzer - Advanced centrality analysis for academic knowledge graphs

Implements PageRank, betweenness centrality, and closeness centrality algorithms
with comprehensive error handling and integration with the distributed transaction system.
"""

import asyncio
import time
import logging
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsError(Exception):
    """Base exception for analytics operations"""
    pass


class GraphCentralityAnalyzer:
    """Advanced centrality analysis for academic knowledge graphs"""
    
    def __init__(self, neo4j_manager, distributed_tx_manager):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        self.centrality_cache = {}
        
        # Performance thresholds
        self.max_nodes_for_exact = 10000
        self.max_nodes_for_betweenness = 5000
        self.sampling_ratio = 0.1
        
        logger.info("GraphCentralityAnalyzer initialized")
    
    async def calculate_pagerank_centrality(self, entity_type: str = None, 
                                          damping_factor: float = 0.85,
                                          max_iterations: int = 100,
                                          tolerance: float = 1e-6) -> Dict[str, Any]:
        """Calculate PageRank centrality for entities in knowledge graph"""
        
        tx_id = f"pagerank_{entity_type}_{int(time.time())}"
        logger.info(f"Starting PageRank calculation - tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Query graph structure with optional entity type filter
            if entity_type:
                query = """
                MATCH (source)-[r]->(target)
                WHERE labels(source) = [$entity_type]
                RETURN id(source) as source_id, id(target) as target_id, 
                       type(r) as relationship_type, properties(r) as props,
                       labels(source) as source_labels, labels(target) as target_labels
                """
                params = {'entity_type': entity_type}
            else:
                query = """
                MATCH (source)-[r]->(target)
                RETURN id(source) as source_id, id(target) as target_id, 
                       type(r) as relationship_type, properties(r) as props,
                       labels(source) as source_labels, labels(target) as target_labels
                LIMIT 50000
                """
                params = {}
            
            # Execute with transaction safety
            await self.dtm.add_operation(tx_id, 'read', 'neo4j', 'graph_structure', {
                'query': query,
                'params': params,
                'operation_type': 'pagerank_data_fetch'
            })
            
            graph_data = await self.neo4j_manager.execute_read_query(query, params)
            
            if not graph_data:
                logger.warning("No graph data found for PageRank calculation")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'algorithm': 'pagerank',
                    'entity_type': entity_type,
                    'scores': {},
                    'metadata': {
                        'total_nodes': 0,
                        'total_edges': 0,
                        'damping_factor': damping_factor,
                        'execution_time': 0,
                        'method': 'exact'
                    }
                }
            
            # Build NetworkX graph for PageRank calculation
            G = nx.DiGraph()
            node_metadata = {}
            
            for record in graph_data:
                source = record['source_id']
                target = record['target_id']
                weight = self._calculate_edge_weight(record['relationship_type'], record['props'])
                
                G.add_edge(source, target, weight=weight)
                
                # Store node metadata for enrichment
                if source not in node_metadata:
                    node_metadata[source] = {
                        'labels': record['source_labels'],
                        'id': source
                    }
                if target not in node_metadata:
                    node_metadata[target] = {
                        'labels': record['target_labels'],
                        'id': target
                    }
            
            logger.info(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Choose algorithm based on graph size
            start_time = time.time()
            if G.number_of_nodes() > self.max_nodes_for_exact:
                pagerank_scores = await self._calculate_approximate_pagerank(
                    G, damping_factor, max_iterations, tolerance
                )
                method = 'approximate'
            else:
                pagerank_scores = nx.pagerank(
                    G, alpha=damping_factor, max_iter=max_iterations, 
                    tol=tolerance, weight='weight'
                )
                method = 'exact'
            
            execution_time = time.time() - start_time
            
            # Enrich results with entity names and metadata
            enriched_scores = await self._enrich_pagerank_results(pagerank_scores, node_metadata)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'algorithm': 'pagerank',
                'entity_type': entity_type,
                'scores': enriched_scores,
                'metadata': {
                    'total_nodes': G.number_of_nodes(),
                    'total_edges': G.number_of_edges(),
                    'damping_factor': damping_factor,
                    'execution_time': execution_time,
                    'method': method,
                    'max_iterations': max_iterations,
                    'tolerance': tolerance
                }
            }
            
            logger.info(f"PageRank calculation completed in {execution_time:.2f}s using {method} method")
            return result
            
        except Exception as e:
            logger.error(f"PageRank calculation failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"PageRank calculation failed: {e}")
    
    async def calculate_betweenness_centrality(self, entity_type: str = None,
                                             normalized: bool = True,
                                             k: Optional[int] = None) -> Dict[str, Any]:
        """Calculate betweenness centrality to identify bridge entities"""
        
        tx_id = f"betweenness_{entity_type}_{int(time.time())}"
        logger.info(f"Starting betweenness centrality calculation - tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Fetch undirected graph structure for betweenness
            if entity_type:
                query = """
                MATCH (a)-[r]-(b)
                WHERE labels(a) = [$entity_type]
                RETURN DISTINCT id(a) as node_a, id(b) as node_b,
                       collect(type(r)) as relationship_types,
                       labels(a) as labels_a, labels(b) as labels_b
                """
                params = {'entity_type': entity_type}
            else:
                query = """
                MATCH (a)-[r]-(b)
                RETURN DISTINCT id(a) as node_a, id(b) as node_b,
                       collect(type(r)) as relationship_types,
                       labels(a) as labels_a, labels(b) as labels_b
                LIMIT 25000
                """
                params = {}
            
            await self.dtm.add_operation(tx_id, 'read', 'neo4j', 'graph_structure', {
                'query': query,
                'params': params,
                'operation_type': 'betweenness_data_fetch'
            })
            
            graph_data = await self.neo4j_manager.execute_read_query(query, params)
            
            if not graph_data:
                logger.warning("No graph data found for betweenness centrality calculation")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'algorithm': 'betweenness_centrality',
                    'entity_type': entity_type,
                    'scores': {},
                    'metadata': {
                        'total_nodes': 0,
                        'total_edges': 0,
                        'normalized': normalized,
                        'execution_time': 0,
                        'method': 'exact'
                    }
                }
            
            # Build undirected graph
            G = nx.Graph()
            node_metadata = {}
            
            for record in graph_data:
                node_a = record['node_a']
                node_b = record['node_b']
                
                G.add_edge(node_a, node_b)
                
                # Store node metadata
                if node_a not in node_metadata:
                    node_metadata[node_a] = {
                        'labels': record['labels_a'],
                        'id': node_a
                    }
                if node_b not in node_metadata:
                    node_metadata[node_b] = {
                        'labels': record['labels_b'],
                        'id': node_b
                    }
            
            logger.info(f"Built undirected graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Choose algorithm based on graph size
            start_time = time.time()
            if G.number_of_nodes() > self.max_nodes_for_betweenness:
                # Use approximation with sampling
                sample_k = k or max(100, int(G.number_of_nodes() * self.sampling_ratio))
                betweenness_scores = nx.betweenness_centrality(
                    G, k=sample_k, normalized=normalized
                )
                method = 'approximate'
                logger.info(f"Using approximate betweenness with k={sample_k} samples")
            else:
                betweenness_scores = nx.betweenness_centrality(
                    G, normalized=normalized
                )
                method = 'exact'
            
            execution_time = time.time() - start_time
            
            # Enrich with entity metadata
            enriched_scores = await self._enrich_centrality_results(betweenness_scores, node_metadata)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'algorithm': 'betweenness_centrality',
                'entity_type': entity_type,
                'scores': enriched_scores,
                'metadata': {
                    'total_nodes': G.number_of_nodes(),
                    'total_edges': G.number_of_edges(),
                    'normalized': normalized,
                    'execution_time': execution_time,
                    'method': method,
                    'k_samples': k if method == 'approximate' else None
                }
            }
            
            logger.info(f"Betweenness centrality calculation completed in {execution_time:.2f}s using {method} method")
            return result
            
        except Exception as e:
            logger.error(f"Betweenness centrality calculation failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"Betweenness centrality calculation failed: {e}")
    
    async def calculate_closeness_centrality(self, entity_type: str = None,
                                           distance: Optional[str] = None,
                                           wf_improved: bool = True) -> Dict[str, Any]:
        """Calculate closeness centrality to identify central entities"""
        
        tx_id = f"closeness_{entity_type}_{int(time.time())}"
        logger.info(f"Starting closeness centrality calculation - tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Use same query as betweenness for undirected graph
            if entity_type:
                query = """
                MATCH (a)-[r]-(b)
                WHERE labels(a) = [$entity_type]
                RETURN DISTINCT id(a) as node_a, id(b) as node_b,
                       collect(type(r)) as relationship_types,
                       labels(a) as labels_a, labels(b) as labels_b
                """
                params = {'entity_type': entity_type}
            else:
                query = """
                MATCH (a)-[r]-(b)
                RETURN DISTINCT id(a) as node_a, id(b) as node_b,
                       collect(type(r)) as relationship_types,
                       labels(a) as labels_a, labels(b) as labels_b
                LIMIT 25000
                """
                params = {}
            
            await self.dtm.add_operation(tx_id, 'read', 'neo4j', 'graph_structure', {
                'query': query,
                'params': params,
                'operation_type': 'closeness_data_fetch'
            })
            
            graph_data = await self.neo4j_manager.execute_read_query(query, params)
            
            if not graph_data:
                logger.warning("No graph data found for closeness centrality calculation")
                await self.dtm.commit_distributed_transaction(tx_id)
                return {
                    'algorithm': 'closeness_centrality',
                    'entity_type': entity_type,
                    'scores': {},
                    'metadata': {
                        'total_nodes': 0,
                        'total_edges': 0,
                        'execution_time': 0
                    }
                }
            
            # Build undirected graph
            G = nx.Graph()
            node_metadata = {}
            
            for record in graph_data:
                node_a = record['node_a']
                node_b = record['node_b']
                
                G.add_edge(node_a, node_b)
                
                # Store node metadata
                if node_a not in node_metadata:
                    node_metadata[node_a] = {
                        'labels': record['labels_a'],
                        'id': node_a
                    }
                if node_b not in node_metadata:
                    node_metadata[node_b] = {
                        'labels': record['labels_b'],
                        'id': node_b
                    }
            
            logger.info(f"Built undirected graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Calculate closeness centrality
            start_time = time.time()
            closeness_scores = nx.closeness_centrality(
                G, distance=distance, wf_improved=wf_improved
            )
            execution_time = time.time() - start_time
            
            # Enrich with entity metadata
            enriched_scores = await self._enrich_centrality_results(closeness_scores, node_metadata)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            result = {
                'algorithm': 'closeness_centrality',
                'entity_type': entity_type,
                'scores': enriched_scores,
                'metadata': {
                    'total_nodes': G.number_of_nodes(),
                    'total_edges': G.number_of_edges(),
                    'execution_time': execution_time,
                    'distance_metric': distance,
                    'wf_improved': wf_improved
                }
            }
            
            logger.info(f"Closeness centrality calculation completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Closeness centrality calculation failed: {e}", exc_info=True)
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise AnalyticsError(f"Closeness centrality calculation failed: {e}")
    
    async def _calculate_approximate_pagerank(self, G: nx.DiGraph, alpha: float, 
                                            max_iter: int, tol: float) -> Dict[int, float]:
        """Calculate approximate PageRank using power iteration with early stopping"""
        
        logger.info("Using approximate PageRank with power iteration")
        
        # Initialize with uniform distribution
        nodes = list(G.nodes())
        n = len(nodes)
        scores = {node: 1.0 / n for node in nodes}
        
        # Power iteration
        for iteration in range(max_iter):
            new_scores = {}
            
            for node in nodes:
                # Calculate PageRank contribution from incoming edges
                incoming_score = 0.0
                for predecessor in G.predecessors(node):
                    out_degree = G.out_degree(predecessor, weight='weight')
                    if out_degree > 0:
                        edge_weight = G[predecessor][node].get('weight', 1.0)
                        incoming_score += (scores[predecessor] * edge_weight) / out_degree
                
                # Apply damping factor
                new_scores[node] = (1 - alpha) / n + alpha * incoming_score
            
            # Check convergence
            diff = sum(abs(new_scores[node] - scores[node]) for node in nodes)
            scores = new_scores
            
            if diff < tol:
                logger.info(f"PageRank converged after {iteration + 1} iterations")
                break
        
        return scores
    
    def _calculate_edge_weight(self, relationship_type: str, properties: Dict[str, Any]) -> float:
        """Calculate edge weight based on relationship type and properties"""
        
        # Base weights by relationship type
        type_weights = {
            'CITES': 1.0,
            'AUTHORED_BY': 0.8,
            'MENTIONS': 0.6,
            'RELATES_TO': 0.4,
            'SIMILAR_TO': 0.3
        }
        
        base_weight = type_weights.get(relationship_type, 0.5)
        
        # Adjust based on properties
        if properties:
            # Confidence score adjustment
            confidence = properties.get('confidence', 0.5)
            base_weight *= confidence
            
            # Frequency adjustment
            frequency = properties.get('frequency', 1)
            base_weight *= min(frequency / 10.0, 2.0)  # Cap at 2x multiplier
            
            # Recency adjustment (if timestamp available)
            if 'timestamp' in properties:
                try:
                    timestamp = datetime.fromisoformat(properties['timestamp'])
                    days_old = (datetime.now() - timestamp).days
                    recency_factor = max(0.1, 1.0 - (days_old / 365.0))  # Decay over a year
                    base_weight *= recency_factor
                except:
                    pass  # Use base weight if timestamp parsing fails
        
        return max(0.01, base_weight)  # Minimum weight threshold
    
    async def _enrich_pagerank_results(self, pagerank_scores: Dict[int, float], 
                                     node_metadata: Dict[int, Dict]) -> List[Dict[str, Any]]:
        """Enrich PageRank results with entity names and metadata"""
        
        enriched_results = []
        
        # Sort by PageRank score
        sorted_scores = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        
        for node_id, score in sorted_scores[:1000]:  # Top 1000 results
            metadata = node_metadata.get(node_id, {})
            
            # Get entity name from Neo4j
            entity_name = await self._get_entity_name(node_id)
            
            enriched_results.append({
                'node_id': node_id,
                'entity_name': entity_name,
                'pagerank_score': score,
                'labels': metadata.get('labels', []),
                'rank': len(enriched_results) + 1
            })
        
        return enriched_results
    
    async def _enrich_centrality_results(self, centrality_scores: Dict[int, float], 
                                       node_metadata: Dict[int, Dict]) -> List[Dict[str, Any]]:
        """Enrich centrality results with entity names and metadata"""
        
        enriched_results = []
        
        # Sort by centrality score
        sorted_scores = sorted(centrality_scores.items(), key=lambda x: x[1], reverse=True)
        
        for node_id, score in sorted_scores[:1000]:  # Top 1000 results
            metadata = node_metadata.get(node_id, {})
            
            # Get entity name from Neo4j
            entity_name = await self._get_entity_name(node_id)
            
            enriched_results.append({
                'node_id': node_id,
                'entity_name': entity_name,
                'centrality_score': score,
                'labels': metadata.get('labels', []),
                'rank': len(enriched_results) + 1
            })
        
        return enriched_results
    
    async def _get_entity_name(self, node_id: int) -> str:
        """Get entity name from Neo4j node"""
        
        try:
            query = """
            MATCH (n)
            WHERE id(n) = $node_id
            RETURN coalesce(n.name, n.title, n.surface_form, toString(id(n))) as name
            """
            
            result = await self.neo4j_manager.execute_read_query(query, {'node_id': node_id})
            if result:
                return result[0]['name']
            else:
                return f"Entity_{node_id}"
                
        except Exception as e:
            logger.warning(f"Failed to get entity name for node {node_id}: {e}")
            return f"Entity_{node_id}"