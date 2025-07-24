#!/usr/bin/env python3
"""
Test Analytics Integration with Neo4j and Distributed Transaction System

Comprehensive integration tests to verify analytics modules work correctly
with the existing infrastructure.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.core.neo4j_manager import Neo4jDockerManager
from src.core.distributed_transaction_manager import DistributedTransactionManager, TransactionStatus
from src.analytics import (
    GraphCentralityAnalyzer,
    CommunityDetector,
    CrossModalEntityLinker,
    ConceptualKnowledgeSynthesizer,
    CitationImpactAnalyzer,
    AnalyticsError
)


@pytest.mark.integration
class TestAnalyticsIntegration:
    """Integration tests for analytics modules"""
    
    @pytest.fixture
    async def neo4j_manager(self):
        """Create real Neo4j manager for integration testing"""
        manager = Neo4jDockerManager()
        await manager.ensure_started()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def dtm(self, neo4j_manager):
        """Create real distributed transaction manager"""
        dtm = DistributedTransactionManager(neo4j_manager)
        yield dtm
    
    @pytest.fixture
    async def setup_test_data(self, neo4j_manager):
        """Setup test data in Neo4j"""
        # Clear existing test data
        await neo4j_manager.execute_write_query(
            "MATCH (n:IntegrationTest) DETACH DELETE n"
        )
        
        # Create test nodes
        create_nodes_query = """
        CREATE (p1:IntegrationTest:Paper {
            id: 'paper_1',
            name: 'Machine Learning Foundations',
            title: 'Machine Learning Foundations',
            year: 2020,
            field: 'Computer Science'
        })
        CREATE (p2:IntegrationTest:Paper {
            id: 'paper_2', 
            name: 'Neural Networks',
            title: 'Neural Networks',
            year: 2021,
            field: 'Computer Science'
        })
        CREATE (p3:IntegrationTest:Paper {
            id: 'paper_3',
            name: 'Quantum Computing',
            title: 'Quantum Computing',
            year: 2021,
            field: 'Physics'
        })
        CREATE (a1:IntegrationTest:Author {
            id: 'author_1',
            name: 'John Doe'
        })
        CREATE (a2:IntegrationTest:Author {
            id: 'author_2',
            name: 'Jane Smith'
        })
        
        CREATE (p1)-[:CITES {confidence: 0.9, weight: 1.0}]->(p2)
        CREATE (p2)-[:CITES {confidence: 0.8, weight: 1.0}]->(p3)
        CREATE (a1)-[:AUTHORED {year: 2020}]->(p1)
        CREATE (a1)-[:AUTHORED {year: 2021}]->(p2)
        CREATE (a2)-[:AUTHORED {year: 2021}]->(p3)
        CREATE (a1)-[:COLLABORATES_WITH {strength: 0.8}]->(a2)
        """
        
        await neo4j_manager.execute_write_query(create_nodes_query)
        
        yield
        
        # Cleanup
        await neo4j_manager.execute_write_query(
            "MATCH (n:IntegrationTest) DETACH DELETE n"
        )
    
    @pytest.mark.asyncio
    async def test_graph_centrality_integration(self, neo4j_manager, dtm, setup_test_data):
        """Test GraphCentralityAnalyzer with real Neo4j and DTM"""
        analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
        
        # Test PageRank calculation
        result = await analyzer.calculate_pagerank_centrality(entity_type='Paper')
        
        # Verify results
        assert result['algorithm'] == 'pagerank'
        assert 'scores' in result
        assert result['metadata']['total_nodes'] >= 3
        assert result['metadata']['method'] in ['exact', 'approximate']
        
        # Verify transaction was committed
        assert len(dtm.active_transactions) == 0
        
        # Test with filtering
        result = await analyzer.calculate_betweenness_centrality(entity_type='Author')
        assert result['algorithm'] == 'betweenness_centrality'
        assert 'scores' in result
    
    @pytest.mark.asyncio
    async def test_community_detection_integration(self, neo4j_manager, dtm, setup_test_data):
        """Test CommunityDetector with real infrastructure"""
        detector = CommunityDetector(neo4j_manager, dtm)
        
        # Test community detection
        result = await detector.detect_research_communities(
            algorithm='louvain',
            min_community_size=1
        )
        
        # Verify results
        assert result['algorithm'] == 'louvain'
        assert 'communities' in result
        assert len(result['communities']) > 0
        
        # Check community structure
        for community in result['communities']:
            assert 'members' in community
            assert 'size' in community
            assert 'dominant_labels' in community
        
        # Verify analysis was performed
        assert 'analysis' in result
        assert 'modularity' in result['analysis']
    
    @pytest.mark.asyncio
    async def test_distributed_transaction_rollback(self, neo4j_manager, dtm):
        """Test transaction rollback on analytics failure"""
        analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
        
        # Mock a failure during processing
        original_method = neo4j_manager.execute_read_query
        
        async def failing_query(*args, **kwargs):
            # First call succeeds, second fails
            if hasattr(failing_query, 'call_count'):
                failing_query.call_count += 1
                if failing_query.call_count > 1:
                    raise Exception("Simulated database error")
            else:
                failing_query.call_count = 1
            return await original_method(*args, **kwargs)
        
        neo4j_manager.execute_read_query = failing_query
        
        # Attempt analysis that should fail
        with pytest.raises(AnalyticsError):
            await analyzer.calculate_pagerank_centrality()
        
        # Verify transaction was rolled back
        assert len(dtm.active_transactions) == 0
        
        # Restore original method
        neo4j_manager.execute_read_query = original_method
    
    @pytest.mark.asyncio
    async def test_cross_modal_linking_integration(self, neo4j_manager, dtm, setup_test_data):
        """Test CrossModalEntityLinker with real data"""
        linker = CrossModalEntityLinker(neo4j_manager, dtm)
        
        # Create entity candidates
        entity_candidates = {
            'text': [
                {'text_content': 'Machine Learning', 'entity_id': 'paper_1'},
                {'text_content': 'Neural Networks', 'entity_id': 'paper_2'}
            ],
            'structured': [
                {'structured_data': {'field': 'Computer Science'}, 'name': 'CS Field'}
            ]
        }
        
        # Execute linking
        result = await linker.link_cross_modal_entities(entity_candidates)
        
        # Verify results
        assert 'linked_entities' in result
        assert 'cross_modal_graph' in result
        assert 'linking_metrics' in result
        
        # Check metrics
        metrics = result['linking_metrics']
        assert metrics['total_entities'] == 3
        assert 'linking_rate' in metrics
    
    @pytest.mark.asyncio
    async def test_knowledge_synthesis_integration(self, neo4j_manager, dtm, setup_test_data):
        """Test ConceptualKnowledgeSynthesizer with real data"""
        synthesizer = ConceptualKnowledgeSynthesizer(neo4j_manager, dtm)
        
        # Synthesize insights for Computer Science domain
        result = await synthesizer.synthesize_research_insights(
            domain='Computer Science',
            synthesis_strategy='inductive',
            max_hypotheses=2
        )
        
        # Verify results
        assert result['domain'] == 'Computer Science'
        assert result['synthesis_strategy'] == 'inductive'
        assert 'evidence_base' in result
        assert 'synthesis_results' in result
        assert 'generated_hypotheses' in result
        
        # Check evidence was gathered
        evidence = result['evidence_base']
        assert len(evidence['entities']) > 0
        assert 'modality_distribution' in evidence
    
    @pytest.mark.asyncio
    async def test_citation_impact_integration(self, neo4j_manager, dtm, setup_test_data):
        """Test CitationImpactAnalyzer with real data"""
        analyzer = CitationImpactAnalyzer(neo4j_manager, dtm)
        
        # Analyze impact for an author
        result = await analyzer.analyze_research_impact(
            entity_id='author_1',
            entity_type='Author',
            time_window_years=5
        )
        
        # Verify results
        assert result['entity_id'] == 'author_1'
        assert result['entity_type'] == 'Author'
        assert 'impact_scores' in result
        assert 'temporal_analysis' in result
        assert 'influence_analysis' in result
        
        # Check impact metrics
        scores = result['impact_scores']
        assert 'h_index' in scores
        assert 'citation_velocity' in scores
        assert 'collaboration_network_centrality' in scores
    
    @pytest.mark.asyncio
    async def test_concurrent_analytics_operations(self, neo4j_manager, dtm, setup_test_data):
        """Test concurrent analytics operations with shared DTM"""
        centrality_analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
        community_detector = CommunityDetector(neo4j_manager, dtm)
        
        # Run multiple analytics operations concurrently
        tasks = [
            centrality_analyzer.calculate_pagerank_centrality(),
            community_detector.detect_research_communities(algorithm='louvain'),
            centrality_analyzer.calculate_betweenness_centrality()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all operations completed successfully
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed: {result}"
            assert isinstance(result, dict)
        
        # Verify no active transactions remain
        assert len(dtm.active_transactions) == 0
    
    @pytest.mark.asyncio
    async def test_analytics_with_empty_graph(self, neo4j_manager, dtm):
        """Test analytics behavior with empty graph"""
        # Clear all data
        await neo4j_manager.execute_write_query("MATCH (n) DETACH DELETE n")
        
        analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
        
        # Test with empty graph
        result = await analyzer.calculate_pagerank_centrality()
        
        # Should handle gracefully
        assert result['scores'] == {}
        assert result['metadata']['total_nodes'] == 0
        assert result['metadata']['total_edges'] == 0
    
    @pytest.mark.asyncio
    async def test_analytics_error_propagation(self, neo4j_manager, dtm):
        """Test proper error propagation through analytics stack"""
        # Create analyzer with invalid query
        analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
        
        # Override method to inject invalid query
        original_build = analyzer._build_networkx_graph
        
        async def bad_query(*args, **kwargs):
            # This will cause a Neo4j error
            await neo4j_manager.execute_read_query("INVALID CYPHER QUERY")
        
        analyzer._build_networkx_graph = bad_query
        
        # Should raise AnalyticsError with proper context
        with pytest.raises(AnalyticsError) as exc_info:
            await analyzer.calculate_pagerank_centrality()
        
        assert "PageRank calculation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_transaction_isolation(self, neo4j_manager, dtm, setup_test_data):
        """Test transaction isolation between analytics operations"""
        analyzer1 = GraphCentralityAnalyzer(neo4j_manager, dtm)
        analyzer2 = CitationImpactAnalyzer(neo4j_manager, dtm)
        
        # Start first transaction
        tx_id1 = "test_tx_1"
        await dtm.begin_distributed_transaction(tx_id1)
        
        # Start second transaction
        tx_id2 = "test_tx_2"
        await dtm.begin_distributed_transaction(tx_id2)
        
        # Verify transactions are isolated
        assert tx_id1 in dtm.active_transactions
        assert tx_id2 in dtm.active_transactions
        assert dtm.active_transactions[tx_id1] != dtm.active_transactions[tx_id2]
        
        # Commit both
        await dtm.commit_distributed_transaction(tx_id1)
        await dtm.commit_distributed_transaction(tx_id2)
        
        # Verify cleanup
        assert len(dtm.active_transactions) == 0


@pytest.mark.integration
class TestAnalyticsPerformanceIntegration:
    """Performance integration tests with real infrastructure"""
    
    @pytest.mark.asyncio
    async def test_large_graph_performance(self, neo4j_manager, dtm):
        """Test performance with larger graph"""
        # Create larger test dataset
        batch_create_query = """
        UNWIND range(1, $count) as i
        CREATE (n:PerfTest:Paper {
            id: 'perf_' + toString(i),
            name: 'Paper ' + toString(i),
            year: 2020 + (i % 5)
        })
        """
        
        await neo4j_manager.execute_write_query(
            batch_create_query, {'count': 100}
        )
        
        # Create random relationships
        rel_query = """
        MATCH (a:PerfTest), (b:PerfTest)
        WHERE a.id < b.id AND rand() < 0.05
        CREATE (a)-[:CITES {weight: rand()}]->(b)
        """
        
        await neo4j_manager.execute_write_query(rel_query)
        
        # Test PageRank performance
        analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
        
        import time
        start = time.time()
        result = await analyzer.calculate_pagerank_centrality(entity_type='Paper')
        elapsed = time.time() - start
        
        # Should complete within reasonable time
        assert elapsed < 5.0, f"PageRank took {elapsed:.2f}s (should be <5s)"
        assert result['metadata']['total_nodes'] >= 100
        
        # Cleanup
        await neo4j_manager.execute_write_query(
            "MATCH (n:PerfTest) DETACH DELETE n"
        )