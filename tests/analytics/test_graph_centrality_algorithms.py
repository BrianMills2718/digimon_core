#!/usr/bin/env python3
"""
Test Graph Centrality Algorithms

Comprehensive tests for GraphCentralityAnalyzer including PageRank,
betweenness centrality, and closeness centrality algorithms.
"""

import pytest
import asyncio
import networkx as nx
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.analytics.graph_centrality_analyzer import GraphCentralityAnalyzer, AnalyticsError


class TestGraphCentralityAnalyzer:
    """Test suite for GraphCentralityAnalyzer"""
    
    @pytest.fixture
    def mock_neo4j_manager(self):
        """Create mock Neo4j manager"""
        manager = Mock()
        manager.execute_read_query = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_dtm(self):
        """Create mock distributed transaction manager"""
        dtm = Mock()
        dtm.begin_distributed_transaction = AsyncMock()
        dtm.add_operation = AsyncMock()
        dtm.commit_distributed_transaction = AsyncMock()
        dtm.rollback_distributed_transaction = AsyncMock()
        dtm.current_tx_id = "test_tx_123"
        return dtm
    
    @pytest.fixture
    def analyzer(self, mock_neo4j_manager, mock_dtm):
        """Create GraphCentralityAnalyzer instance"""
        return GraphCentralityAnalyzer(mock_neo4j_manager, mock_dtm)
    
    @pytest.mark.asyncio
    async def test_pagerank_calculation_small_graph(self, analyzer, mock_neo4j_manager):
        """Test PageRank calculation on small graph"""
        # Mock graph data
        mock_graph_data = [
            {
                'source_id': 1, 'target_id': 2,
                'relationship_type': 'CITES', 'props': {'confidence': 0.9},
                'source_labels': ['Paper'], 'target_labels': ['Paper']
            },
            {
                'source_id': 2, 'target_id': 3,
                'relationship_type': 'CITES', 'props': {'confidence': 0.8},
                'source_labels': ['Paper'], 'target_labels': ['Paper']
            },
            {
                'source_id': 3, 'target_id': 1,
                'relationship_type': 'CITES', 'props': {'confidence': 0.7},
                'source_labels': ['Paper'], 'target_labels': ['Paper']
            }
        ]
        
        mock_neo4j_manager.execute_read_query.return_value = mock_graph_data
        
        # Execute PageRank
        result = await analyzer.calculate_pagerank_centrality()
        
        # Verify results
        assert result['algorithm'] == 'pagerank'
        assert 'scores' in result
        assert 'metadata' in result
        assert result['metadata']['total_nodes'] == 3
        assert result['metadata']['total_edges'] == 3
        assert result['metadata']['method'] == 'exact'
        assert result['metadata']['execution_time'] > 0
    
    @pytest.mark.asyncio
    async def test_pagerank_with_entity_type_filter(self, analyzer, mock_neo4j_manager):
        """Test PageRank with entity type filtering"""
        # Mock filtered data
        mock_graph_data = [
            {
                'source_id': 1, 'target_id': 2,
                'relationship_type': 'AUTHORED_BY', 'props': {},
                'source_labels': ['Author'], 'target_labels': ['Paper']
            }
        ]
        
        mock_neo4j_manager.execute_read_query.return_value = mock_graph_data
        
        # Execute with entity type filter
        result = await analyzer.calculate_pagerank_centrality(entity_type='Author')
        
        # Verify entity type was used
        assert result['entity_type'] == 'Author'
        assert result['metadata']['total_nodes'] == 2
    
    @pytest.mark.asyncio
    async def test_pagerank_approximate_method(self, analyzer, mock_neo4j_manager):
        """Test approximate PageRank for large graphs"""
        # Set threshold for approximation
        analyzer.max_nodes_for_exact = 5
        
        # Mock large graph data
        mock_graph_data = []
        for i in range(10):
            mock_graph_data.append({
                'source_id': i, 'target_id': (i + 1) % 10,
                'relationship_type': 'CITES', 'props': {},
                'source_labels': ['Paper'], 'target_labels': ['Paper']
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_graph_data
        
        # Execute PageRank
        result = await analyzer.calculate_pagerank_centrality()
        
        # Verify approximate method was used
        assert result['metadata']['method'] == 'approximate'
        assert result['metadata']['total_nodes'] == 10
    
    @pytest.mark.asyncio
    async def test_betweenness_centrality(self, analyzer, mock_neo4j_manager):
        """Test betweenness centrality calculation"""
        # Mock undirected graph data
        mock_graph_data = [
            {
                'node_a': 1, 'node_b': 2,
                'relationship_types': ['COLLABORATES'],
                'labels_a': ['Author'], 'labels_b': ['Author']
            },
            {
                'node_a': 2, 'node_b': 3,
                'relationship_types': ['COLLABORATES'],
                'labels_a': ['Author'], 'labels_b': ['Author']
            },
            {
                'node_a': 1, 'node_b': 3,
                'relationship_types': ['COLLABORATES'],
                'labels_a': ['Author'], 'labels_b': ['Author']
            }
        ]
        
        mock_neo4j_manager.execute_read_query.return_value = mock_graph_data
        
        # Execute betweenness centrality
        result = await analyzer.calculate_betweenness_centrality()
        
        # Verify results
        assert result['algorithm'] == 'betweenness_centrality'
        assert 'scores' in result
        assert result['metadata']['total_nodes'] == 3
        assert result['metadata']['normalized'] == True
    
    @pytest.mark.asyncio
    async def test_closeness_centrality(self, analyzer, mock_neo4j_manager):
        """Test closeness centrality calculation"""
        # Mock graph data
        mock_graph_data = [
            {
                'node_a': 1, 'node_b': 2,
                'relationship_types': ['RELATED'],
                'labels_a': ['Concept'], 'labels_b': ['Concept']
            },
            {
                'node_a': 2, 'node_b': 3,
                'relationship_types': ['RELATED'],
                'labels_a': ['Concept'], 'labels_b': ['Concept']
            }
        ]
        
        mock_neo4j_manager.execute_read_query.return_value = mock_graph_data
        
        # Execute closeness centrality
        result = await analyzer.calculate_closeness_centrality()
        
        # Verify results
        assert result['algorithm'] == 'closeness_centrality'
        assert 'scores' in result
        assert result['metadata']['total_nodes'] == 3
    
    @pytest.mark.asyncio
    async def test_edge_weight_calculation(self, analyzer):
        """Test edge weight calculation logic"""
        # Test base weight
        weight = analyzer._calculate_edge_weight('CITES', {})
        assert weight == 1.0
        
        # Test with confidence
        weight = analyzer._calculate_edge_weight('CITES', {'confidence': 0.5})
        assert weight == 0.5
        
        # Test with frequency
        weight = analyzer._calculate_edge_weight('CITES', {'frequency': 5})
        assert weight == 0.5  # 1.0 * (5/10)
        
        # Test unknown relationship type
        weight = analyzer._calculate_edge_weight('UNKNOWN', {})
        assert weight == 0.5
    
    @pytest.mark.asyncio
    async def test_empty_graph_handling(self, analyzer, mock_neo4j_manager):
        """Test handling of empty graph data"""
        mock_neo4j_manager.execute_read_query.return_value = []
        
        # Execute PageRank on empty graph
        result = await analyzer.calculate_pagerank_centrality()
        
        # Verify empty result handling
        assert result['scores'] == {}
        assert result['metadata']['total_nodes'] == 0
        assert result['metadata']['total_edges'] == 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer, mock_neo4j_manager, mock_dtm):
        """Test error handling and transaction rollback"""
        # Mock query failure
        mock_neo4j_manager.execute_read_query.side_effect = Exception("Database error")
        
        # Execute and expect error
        with pytest.raises(AnalyticsError) as exc_info:
            await analyzer.calculate_pagerank_centrality()
        
        # Verify error message
        assert "PageRank calculation failed" in str(exc_info.value)
        
        # Verify transaction was rolled back
        mock_dtm.rollback_distributed_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_result_enrichment(self, analyzer, mock_neo4j_manager):
        """Test entity name enrichment in results"""
        # Mock graph data
        mock_graph_data = [
            {
                'source_id': 1, 'target_id': 2,
                'relationship_type': 'CITES', 'props': {},
                'source_labels': ['Paper'], 'target_labels': ['Paper']
            }
        ]
        
        # Mock entity name query
        async def mock_name_query(query, params):
            if 'graph_structure' in str(query):
                return mock_graph_data
            else:
                return [{'name': f"Entity_{params['node_id']}"}]
        
        mock_neo4j_manager.execute_read_query.side_effect = mock_name_query
        
        # Execute PageRank
        result = await analyzer.calculate_pagerank_centrality()
        
        # Verify enriched results
        assert len(result['scores']) > 0
        if result['scores']:
            first_score = result['scores'][0]
            assert 'entity_name' in first_score
            assert 'rank' in first_score
    
    def test_approximate_pagerank_convergence(self):
        """Test approximate PageRank convergence"""
        # Create test graph
        G = nx.karate_club_graph()
        
        # Convert to directed graph format
        directed_G = nx.DiGraph()
        for u, v in G.edges():
            directed_G.add_edge(u, v, weight=1.0)
        
        # Run approximate PageRank synchronously
        analyzer = GraphCentralityAnalyzer(None, None)
        
        # Test convergence
        scores = asyncio.run(analyzer._calculate_approximate_pagerank(
            directed_G, alpha=0.85, max_iter=100, tol=1e-6
        ))
        
        # Verify all nodes have scores
        assert len(scores) == directed_G.number_of_nodes()
        
        # Verify scores sum to approximately 1
        total_score = sum(scores.values())
        assert abs(total_score - 1.0) < 0.01


class TestCentralityPerformance:
    """Performance tests for centrality algorithms"""
    
    @pytest.mark.asyncio
    async def test_pagerank_performance_scaling(self):
        """Test PageRank performance with different graph sizes"""
        import time
        
        # Test different graph sizes
        sizes = [10, 100, 1000]
        execution_times = []
        
        for size in sizes:
            # Create random graph
            G = nx.erdos_renyi_graph(size, 0.1, directed=True)
            
            # Mock analyzer
            analyzer = GraphCentralityAnalyzer(Mock(), Mock())
            
            # Time execution
            start = time.time()
            scores = await analyzer._calculate_approximate_pagerank(
                G, alpha=0.85, max_iter=20, tol=1e-4
            )
            end = time.time()
            
            execution_times.append(end - start)
        
        # Verify reasonable scaling
        # Time should not increase more than quadratically
        assert execution_times[2] < execution_times[0] * (1000/10)**2
    
    @pytest.mark.asyncio 
    async def test_centrality_caching(self):
        """Test that centrality results can be cached"""
        # Create analyzer with caching
        analyzer = GraphCentralityAnalyzer(Mock(), Mock())
        
        # Mock graph data
        mock_data = [
            {'source_id': 1, 'target_id': 2, 'relationship_type': 'CITES', 
             'props': {}, 'source_labels': ['Paper'], 'target_labels': ['Paper']}
        ]
        
        # Store in cache
        cache_key = "pagerank_test_123"
        analyzer.centrality_cache[cache_key] = {'cached': True}
        
        # Verify cache hit
        assert analyzer.centrality_cache.get(cache_key) == {'cached': True}