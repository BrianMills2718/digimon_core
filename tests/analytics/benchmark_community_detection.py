#!/usr/bin/env python3
"""
Benchmark Community Detection Performance

Performance benchmarks for community detection algorithms to ensure
they meet the <2 second response time requirement.
"""

import pytest
import asyncio
import time
import networkx as nx
import numpy as np
from unittest.mock import Mock, AsyncMock
import random

from src.analytics.community_detector import CommunityDetector, AnalyticsError


class BenchmarkCommunityDetection:
    """Benchmark suite for community detection performance"""
    
    @pytest.fixture
    def mock_neo4j_manager(self):
        """Create mock Neo4j manager with realistic data"""
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
        dtm.current_tx_id = "benchmark_tx_123"
        return dtm
    
    @pytest.fixture
    def detector(self, mock_neo4j_manager, mock_dtm):
        """Create CommunityDetector instance"""
        return CommunityDetector(mock_neo4j_manager, mock_dtm)
    
    def generate_network_data(self, num_nodes: int, num_edges: int, 
                            num_communities: int = 5) -> list:
        """Generate realistic network data with community structure"""
        # Use stochastic block model for community structure
        sizes = [num_nodes // num_communities] * num_communities
        sizes[-1] += num_nodes % num_communities  # Handle remainder
        
        # Higher probability within communities
        p_matrix = np.full((num_communities, num_communities), 0.01)
        np.fill_diagonal(p_matrix, 0.3)
        
        G = nx.stochastic_block_model(sizes, p_matrix, directed=False)
        
        # Convert to query result format
        network_data = []
        node_labels = ['Author', 'Paper', 'Institution', 'Topic', 'Project']
        
        for u, v in G.edges():
            network_data.append({
                'node_a': u,
                'node_b': v,
                'labels_a': [random.choice(node_labels)],
                'labels_b': [random.choice(node_labels)],
                'name_a': f'Entity_{u}',
                'name_b': f'Entity_{v}',
                'relationship_type': random.choice(['CITES', 'COLLABORATES', 'AFFILIATED']),
                'edge_weight': random.randint(1, 5),
                'confidences': [random.uniform(0.5, 1.0) for _ in range(random.randint(1, 3))]
            })
        
        return network_data
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_louvain_performance_small_network(self, detector, mock_neo4j_manager):
        """Benchmark Louvain on small network (100 nodes)"""
        # Generate small network
        network_data = self.generate_network_data(100, 500)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # Measure execution time
        start_time = time.time()
        result = await detector.detect_research_communities(
            algorithm='louvain',
            min_community_size=3
        )
        execution_time = time.time() - start_time
        
        # Verify performance
        assert execution_time < 2.0, f"Small network took {execution_time:.2f}s (must be <2s)"
        assert len(result['communities']) > 0
        assert result['metadata']['execution_time'] < 2.0
        
        print(f"\nLouvain small network (100 nodes): {execution_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_louvain_performance_medium_network(self, detector, mock_neo4j_manager):
        """Benchmark Louvain on medium network (1000 nodes)"""
        # Generate medium network
        network_data = self.generate_network_data(1000, 5000, num_communities=10)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # Measure execution time
        start_time = time.time()
        result = await detector.detect_research_communities(
            algorithm='louvain',
            min_community_size=5
        )
        execution_time = time.time() - start_time
        
        # Verify performance
        assert execution_time < 2.0, f"Medium network took {execution_time:.2f}s (must be <2s)"
        assert len(result['communities']) > 0
        
        print(f"Louvain medium network (1000 nodes): {execution_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_louvain_performance_large_network(self, detector, mock_neo4j_manager):
        """Benchmark Louvain on large network (5000 nodes)"""
        # Generate large network
        network_data = self.generate_network_data(5000, 25000, num_communities=20)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # Measure execution time
        start_time = time.time()
        result = await detector.detect_research_communities(
            algorithm='louvain',
            min_community_size=10,
            max_communities=20  # Limit output size
        )
        execution_time = time.time() - start_time
        
        # Verify performance (allow slightly more time for large networks)
        assert execution_time < 3.0, f"Large network took {execution_time:.2f}s (must be <3s)"
        
        print(f"Louvain large network (5000 nodes): {execution_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_label_propagation_performance(self, detector, mock_neo4j_manager):
        """Benchmark label propagation algorithm"""
        # Generate network
        network_data = self.generate_network_data(500, 2500)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # Measure execution time
        start_time = time.time()
        result = await detector.detect_research_communities(
            algorithm='label_propagation',
            min_community_size=5
        )
        execution_time = time.time() - start_time
        
        # Verify performance
        assert execution_time < 2.0, f"Label propagation took {execution_time:.2f}s (must be <2s)"
        
        print(f"Label propagation (500 nodes): {execution_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_greedy_modularity_performance(self, detector, mock_neo4j_manager):
        """Benchmark greedy modularity algorithm"""
        # Generate network
        network_data = self.generate_network_data(500, 2500)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # Measure execution time
        start_time = time.time()
        result = await detector.detect_research_communities(
            algorithm='greedy_modularity',
            min_community_size=5
        )
        execution_time = time.time() - start_time
        
        # Verify performance
        assert execution_time < 2.0, f"Greedy modularity took {execution_time:.2f}s (must be <2s)"
        
        print(f"Greedy modularity (500 nodes): {execution_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_community_analysis_performance(self, detector, mock_neo4j_manager):
        """Benchmark community analysis overhead"""
        # Generate network with known communities
        network_data = self.generate_network_data(1000, 5000, num_communities=10)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # First, detect communities
        result = await detector.detect_research_communities(
            algorithm='louvain',
            min_community_size=5
        )
        
        # Measure just the analysis time
        communities = result['communities']
        network_data_dict = await detector._build_research_network()
        
        start_time = time.time()
        analysis = await detector._analyze_communities(communities, network_data_dict)
        analysis_time = time.time() - start_time
        
        # Verify analysis performance
        assert analysis_time < 0.5, f"Analysis took {analysis_time:.2f}s (must be <0.5s)"
        
        print(f"Community analysis overhead: {analysis_time:.3f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark 
    async def test_resolution_parameter_impact(self, detector, mock_neo4j_manager):
        """Test impact of resolution parameter on performance"""
        # Generate network
        network_data = self.generate_network_data(1000, 5000)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        resolutions = [0.5, 1.0, 1.5, 2.0]
        times = []
        
        for resolution in resolutions:
            start_time = time.time()
            result = await detector.detect_research_communities(
                algorithm='louvain',
                resolution=resolution,
                min_community_size=5
            )
            execution_time = time.time() - start_time
            times.append(execution_time)
            
            print(f"Resolution {resolution}: {execution_time:.3f}s, {len(result['communities'])} communities")
        
        # All should complete within time limit
        assert all(t < 2.0 for t in times), "Some resolutions exceeded time limit"
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_parallel_algorithm_comparison(self, detector, mock_neo4j_manager):
        """Compare performance of different algorithms on same network"""
        # Generate test network
        network_data = self.generate_network_data(500, 2500)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        algorithms = ['louvain', 'label_propagation', 'greedy_modularity']
        results = {}
        
        for algorithm in algorithms:
            start_time = time.time()
            result = await detector.detect_research_communities(
                algorithm=algorithm,
                min_community_size=5
            )
            execution_time = time.time() - start_time
            
            results[algorithm] = {
                'time': execution_time,
                'communities': len(result['communities']),
                'modularity': result['analysis'].get('modularity', 0)
            }
            
            print(f"\n{algorithm}:")
            print(f"  Time: {execution_time:.3f}s")
            print(f"  Communities: {results[algorithm]['communities']}")
            print(f"  Modularity: {results[algorithm]['modularity']:.3f}")
        
        # All should complete within time limit
        assert all(r['time'] < 2.0 for r in results.values())
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_memory_efficiency(self, detector, mock_neo4j_manager):
        """Test memory efficiency of community detection"""
        import psutil
        import gc
        
        # Generate large network
        network_data = self.generate_network_data(5000, 25000)
        mock_neo4j_manager.execute_read_query.return_value = network_data
        
        # Force garbage collection
        gc.collect()
        
        # Measure initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run community detection
        result = await detector.detect_research_communities(
            algorithm='louvain',
            min_community_size=10
        )
        
        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        print(f"\nMemory usage:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Peak: {peak_memory:.1f} MB") 
        print(f"  Increase: {memory_increase:.1f} MB")
        
        # Should not use excessive memory
        assert memory_increase < 500, f"Used {memory_increase:.1f} MB (limit 500 MB)"


class TestAlgorithmScaling:
    """Test algorithm scaling characteristics"""
    
    @pytest.mark.asyncio
    async def test_scaling_behavior(self):
        """Test how algorithms scale with network size"""
        sizes = [100, 500, 1000, 2000]
        
        # Mock components
        mock_neo4j = Mock()
        mock_neo4j.execute_read_query = AsyncMock()
        
        mock_dtm = Mock()
        mock_dtm.begin_distributed_transaction = AsyncMock()
        mock_dtm.add_operation = AsyncMock()
        mock_dtm.commit_distributed_transaction = AsyncMock()
        mock_dtm.current_tx_id = "test"
        
        detector = CommunityDetector(mock_neo4j, mock_dtm)
        
        louvain_times = []
        
        for size in sizes:
            # Generate network
            network_data = BenchmarkCommunityDetection().generate_network_data(
                size, size * 5
            )
            mock_neo4j.execute_read_query.return_value = network_data
            
            # Measure time
            start = time.time()
            await detector.detect_research_communities(algorithm='louvain')
            elapsed = time.time() - start
            
            louvain_times.append(elapsed)
            print(f"Size {size}: {elapsed:.3f}s")
        
        # Check scaling is reasonable (not exponential)
        # Time should grow slower than O(n^2)
        time_ratio = louvain_times[-1] / louvain_times[0]
        size_ratio = sizes[-1] / sizes[0]
        
        assert time_ratio < size_ratio ** 2, "Algorithm scaling is worse than O(n^2)"
        print(f"\nScaling factor: {time_ratio:.2f}x for {size_ratio}x size increase")