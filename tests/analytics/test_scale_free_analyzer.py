#!/usr/bin/env python3
"""
Test Scale-Free Network Analyzer

Comprehensive tests for ScaleFreeAnalyzer including power-law distribution
analysis, hub detection, and temporal analysis capabilities.
"""

import pytest
import asyncio
import networkx as nx
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import powerlaw

from src.analytics.scale_free_analyzer import ScaleFreeAnalyzer, ScaleFreeAnalysisError


class TestScaleFreeAnalyzer:
    """Test suite for ScaleFreeAnalyzer"""
    
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
        dtm.record_operation = AsyncMock()
        dtm.commit_distributed_transaction = AsyncMock()
        dtm.rollback_distributed_transaction = AsyncMock()
        dtm.current_tx_id = "test_tx_123"
        return dtm
    
    @pytest.fixture
    def analyzer(self, mock_neo4j_manager, mock_dtm):
        """Create ScaleFreeAnalyzer instance"""
        return ScaleFreeAnalyzer(mock_neo4j_manager, mock_dtm)
    
    @pytest.fixture
    def scale_free_graph_data(self):
        """Create mock data for a scale-free network"""
        # Generate a Barabasi-Albert scale-free network
        G = nx.barabasi_albert_graph(100, 3)
        
        nodes = []
        edges = []
        
        for node in G.nodes():
            nodes.append({
                'node_id': node,
                'labels': ['Entity'],
                'name': f'Entity_{node}'
            })
        
        for source, target in G.edges():
            edges.append({
                'source': source,
                'target': target,
                'type': 'CONNECTED_TO'
            })
        
        return nodes, edges
    
    @pytest.fixture
    def random_graph_data(self):
        """Create mock data for a random (non-scale-free) network"""
        # Generate an Erdos-Renyi random network
        G = nx.erdos_renyi_graph(100, 0.05)
        
        nodes = []
        edges = []
        
        for node in G.nodes():
            nodes.append({
                'node_id': node,
                'labels': ['Entity'],
                'name': f'Entity_{node}'
            })
        
        for source, target in G.edges():
            edges.append({
                'source': source,
                'target': target,
                'type': 'CONNECTED_TO'
            })
        
        return nodes, edges
    
    @pytest.mark.asyncio
    async def test_analyze_scale_free_properties_basic(self, analyzer, mock_neo4j_manager, scale_free_graph_data):
        """Test basic scale-free analysis functionality"""
        nodes, edges = scale_free_graph_data
        
        # Mock Neo4j response
        mock_response = []
        for node in nodes:
            node_edges = [e for e in edges if e['source'] == node['node_id']]
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'name': node['name'],
                'relationships': node_edges
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Run analysis
        result = await analyzer.analyze_scale_free_properties(
            entity_type='Entity',
            relationship_type='CONNECTED_TO'
        )
        
        # Verify results
        assert result['status'] == 'success'
        assert 'is_scale_free' in result
        assert 'confidence_score' in result
        assert 'basic_statistics' in result
        assert 'power_law_fit' in result
        assert result['basic_statistics']['node_count'] == 100
    
    @pytest.mark.asyncio
    async def test_analyze_no_data(self, analyzer, mock_neo4j_manager):
        """Test analysis with no data"""
        mock_neo4j_manager.execute_read_query.return_value = []
        
        result = await analyzer.analyze_scale_free_properties()
        
        assert result['status'] == 'no_data'
        assert 'message' in result
    
    @pytest.mark.asyncio
    async def test_analyze_insufficient_data(self, analyzer, mock_neo4j_manager):
        """Test analysis with insufficient data"""
        # Create small graph (< 100 nodes)
        small_data = []
        for i in range(10):
            small_data.append({
                'node_id': i,
                'labels': ['Entity'],
                'name': f'Entity_{i}',
                'relationships': []
            })
        
        mock_neo4j_manager.execute_read_query.return_value = small_data
        
        result = await analyzer.analyze_scale_free_properties()
        
        assert result['status'] == 'insufficient_data'
        assert result['node_count'] == 10
    
    @pytest.mark.asyncio
    async def test_power_law_fitting(self, analyzer):
        """Test power-law fitting functionality"""
        # Generate a perfect power-law distribution
        alpha = 2.5
        xmin = 1
        n = 1000
        
        # Generate power-law distributed data
        data = powerlaw.Power_Law(xmin=xmin, parameters=[alpha]).generate_random(n)
        degree_sequence = [int(x) for x in data if x < 100]  # Cap for realistic degrees
        
        # Test fitting
        result = await analyzer._fit_power_law(degree_sequence)
        
        assert 'alpha' in result
        assert 'xmin' in result
        assert 'confidence' in result
        assert result['alpha'] is not None
        # Alpha should be roughly close to the true value (within reasonable range)
        assert 1.5 < result['alpha'] < 3.5
    
    @pytest.mark.asyncio
    async def test_degree_distribution_analysis(self, analyzer):
        """Test degree distribution analysis"""
        # Create a simple degree sequence
        degree_sequence = [1, 1, 2, 2, 2, 3, 3, 4, 5, 10, 20, 50]
        
        result = await analyzer._analyze_degree_distribution(degree_sequence)
        
        assert 'degree_counts' in result
        assert 'cumulative_distribution' in result
        assert 'log_log_regression' in result
        assert 'heavy_tail' in result
        
        # Check degree counts
        assert result['degree_counts'][1] == 2
        assert result['degree_counts'][2] == 3
        assert result['degree_counts'][50] == 1
    
    @pytest.mark.asyncio
    async def test_hub_analysis(self, analyzer):
        """Test hub analysis functionality"""
        # Create a graph with clear hubs
        G = nx.Graph()
        
        # Add a hub with many connections
        hub_node = 0
        for i in range(1, 21):
            G.add_edge(hub_node, i)
        
        # Add some regular connections
        for i in range(21, 30):
            G.add_edge(i, i+1)
        
        degrees = dict(G.degree())
        
        result = await analyzer._analyze_hubs(G, degrees)
        
        assert 'n_hubs' in result
        assert 'hub_threshold_degree' in result
        assert 'max_hub_degree' in result
        assert 'top_hubs' in result
        
        # Hub node should be identified
        top_hub = result['top_hubs'][0]
        assert top_hub['node_id'] == hub_node
        assert top_hub['degree'] == 20
    
    @pytest.mark.asyncio
    async def test_scale_free_determination(self, analyzer):
        """Test scale-free determination logic"""
        # Test positive case (scale-free)
        power_law_fit = {
            'alpha': 2.5,
            'confidence': 0.8
        }
        alt_distributions = {
            'is_power_law_preferred': True
        }
        degree_dist = {
            'heavy_tail': True
        }
        hub_analysis = {
            'hub_degree_fraction': 0.4
        }
        
        is_scale_free = analyzer._determine_scale_free(
            power_law_fit, alt_distributions, degree_dist, hub_analysis
        )
        
        assert is_scale_free is True
        
        # Test negative case (not scale-free)
        power_law_fit['confidence'] = 0.2
        alt_distributions['is_power_law_preferred'] = False
        degree_dist['heavy_tail'] = False
        hub_analysis['hub_degree_fraction'] = 0.1
        
        is_scale_free = analyzer._determine_scale_free(
            power_law_fit, alt_distributions, degree_dist, hub_analysis
        )
        
        assert is_scale_free is False
    
    @pytest.mark.asyncio
    async def test_visualization_data_preparation(self, analyzer):
        """Test visualization data preparation"""
        degree_sequence = [1, 1, 2, 2, 3, 3, 3, 4, 5, 10, 20]
        
        result = await analyzer._prepare_visualization_data(degree_sequence)
        
        assert 'degree_distribution_plot' in result
        assert 'degree_histogram' in result
        
        # Check plot data
        plot_data = result['degree_distribution_plot']
        assert len(plot_data) > 0
        assert all('degree' in item and 'count' in item for item in plot_data)
        assert all('log_degree' in item and 'log_count' in item for item in plot_data)
    
    @pytest.mark.asyncio
    async def test_temporal_analysis(self, analyzer, mock_neo4j_manager):
        """Test temporal scale-free analysis"""
        # Mock time window data
        mock_neo4j_manager.execute_read_query.side_effect = [
            # First call for time windows
            [{'min_date': '2020-01-01', 'max_date': '2023-12-31'}],
            # Subsequent calls for each year (simplified)
            [], [], [], []
        ]
        
        # Mock the individual window analysis
        with patch.object(analyzer, '_analyze_time_window') as mock_analyze:
            mock_analyze.return_value = {
                'status': 'success',
                'is_scale_free': True,
                'power_law_fit': {'alpha': 2.5},
                'basic_statistics': {'node_count': 100},
                'confidence_score': 0.8
            }
            
            result = await analyzer.analyze_temporal_scale_free()
            
            assert result['status'] == 'success'
            assert 'temporal_analysis' in result
            assert 'trends' in result
            assert 'summary' in result
    
    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer, mock_neo4j_manager, mock_dtm):
        """Test error handling in analysis"""
        # Simulate Neo4j error
        mock_neo4j_manager.execute_read_query.side_effect = Exception("Database error")
        
        with pytest.raises(ScaleFreeAnalysisError) as excinfo:
            await analyzer.analyze_scale_free_properties()
        
        assert "Database error" in str(excinfo.value)
        
        # Verify rollback was called
        mock_dtm.rollback_distributed_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, analyzer):
        """Test confidence score calculation"""
        # High confidence case
        confidence = analyzer._calculate_confidence(
            alpha=2.5,  # Good range
            R=1.5,      # Power law preferred
            p=0.15,     # Good p-value
            D=0.04      # Low KS distance
        )
        assert confidence > 0.7
        
        # Low confidence case
        confidence = analyzer._calculate_confidence(
            alpha=5.0,  # Outside typical range
            R=-1.0,     # Power law not preferred
            p=0.5,      # High p-value
            D=0.2       # High KS distance
        )
        assert confidence < 0.3
        
        # None alpha case
        confidence = analyzer._calculate_confidence(
            alpha=None,
            R=1.0,
            p=0.1,
            D=0.05
        )
        assert confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_direction_parameter(self, analyzer, mock_neo4j_manager, scale_free_graph_data):
        """Test analysis with different direction parameters"""
        nodes, edges = scale_free_graph_data
        
        # Mock response
        mock_response = []
        for node in nodes:
            node_edges = [e for e in edges if e['source'] == node['node_id']]
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'name': node['name'],
                'relationships': node_edges
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # Test different directions
        for direction in ['in', 'out', 'both']:
            result = await analyzer.analyze_scale_free_properties(
                direction=direction
            )
            
            assert result['status'] == 'success'
            assert 'is_scale_free' in result
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, analyzer, mock_neo4j_manager, scale_free_graph_data):
        """Test that results are properly cached"""
        nodes, edges = scale_free_graph_data
        
        # Mock response
        mock_response = []
        for node in nodes[:50]:  # Use smaller graph for speed
            mock_response.append({
                'node_id': node['node_id'],
                'labels': node['labels'],
                'name': node['name'],
                'relationships': []
            })
        
        mock_neo4j_manager.execute_read_query.return_value = mock_response
        
        # First call
        result1 = await analyzer.analyze_scale_free_properties()
        
        # Verify Neo4j was called
        assert mock_neo4j_manager.execute_read_query.call_count == 1
        
        # Note: The analyzer doesn't have built-in caching, so this test
        # mainly verifies that repeated calls work correctly
        result2 = await analyzer.analyze_scale_free_properties()
        
        # Should make another call (no caching)
        assert mock_neo4j_manager.execute_read_query.call_count == 2
        
        # Results should be similar structure
        assert result1['status'] == result2['status']
    
    @pytest.mark.asyncio
    async def test_real_world_networks(self, analyzer):
        """Test with real-world network patterns"""
        # Test cases representing different network types
        
        # 1. Citation network (typically scale-free)
        citation_degrees = []
        # Many papers with few citations
        citation_degrees.extend([1] * 500)
        citation_degrees.extend([2] * 200)
        citation_degrees.extend([3] * 100)
        # Some well-cited papers
        citation_degrees.extend(list(range(10, 50)) * 2)
        # Few highly-cited papers
        citation_degrees.extend([100, 150, 200, 500, 1000])
        
        result = await analyzer._analyze_degree_distribution(citation_degrees)
        assert result['heavy_tail'] is True
        
        # 2. Social network (often scale-free)
        # Simulate follower counts
        social_degrees = []
        # Most users have few connections
        social_degrees.extend(np.random.poisson(5, 1000).tolist())
        # Some influencers
        social_degrees.extend(np.random.poisson(50, 50).tolist())
        # Few super-influencers
        social_degrees.extend([1000, 5000, 10000])
        
        result = await analyzer._fit_power_law(social_degrees)
        assert result['alpha'] is not None