#!/usr/bin/env python3
"""
Test Cross-Modal Entity Linking Accuracy

Comprehensive tests for CrossModalEntityLinker including entity resolution,
similarity calculations, and cross-modal graph construction.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.analytics.cross_modal_linker import (
    CrossModalEntityLinker, EntityResolver, MockEmbeddingService, AnalyticsError
)


class TestCrossModalEntityLinker:
    """Test suite for CrossModalEntityLinker"""
    
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
    def mock_embedding_service(self):
        """Create mock embedding service"""
        service = Mock()
        service.generate_text_embeddings = AsyncMock()
        service.generate_image_embeddings = AsyncMock()
        service.generate_structured_embeddings = AsyncMock()
        return service
    
    @pytest.fixture
    def linker(self, mock_neo4j_manager, mock_dtm, mock_embedding_service):
        """Create CrossModalEntityLinker instance"""
        return CrossModalEntityLinker(mock_neo4j_manager, mock_dtm, mock_embedding_service)
    
    @pytest.mark.asyncio
    async def test_entity_linking_basic(self, linker, mock_embedding_service):
        """Test basic cross-modal entity linking"""
        # Prepare test data
        entity_candidates = {
            'text': [
                {'text_content': 'Machine learning algorithms', 'entity_id': 1},
                {'text_content': 'Neural networks', 'entity_id': 2}
            ],
            'image': [
                {'image_path': '/path/to/ml_diagram.png', 'entity_id': 3},
                {'image_path': '/path/to/nn_architecture.png', 'entity_id': 4}
            ]
        }
        
        # Mock embeddings with high similarity between related entities
        text_embeddings = np.array([
            [0.9, 0.1, 0.2],  # ML algorithms
            [0.1, 0.9, 0.2]   # Neural networks
        ])
        
        image_embeddings = np.array([
            [0.85, 0.15, 0.2],  # ML diagram (similar to ML text)
            [0.15, 0.85, 0.2]   # NN architecture (similar to NN text)
        ])
        
        mock_embedding_service.generate_text_embeddings.return_value = text_embeddings
        mock_embedding_service.generate_image_embeddings.return_value = image_embeddings
        
        # Execute linking
        result = await linker.link_cross_modal_entities(entity_candidates)
        
        # Verify results
        assert 'linked_entities' in result
        assert 'cross_modal_graph' in result
        assert 'linking_metrics' in result
        
        # Check that entities were linked
        assert len(result['linked_entities']) > 0
        
        # Verify cross-modal clusters
        for cluster in result['linked_entities']:
            assert 'entities' in cluster
            assert len(cluster['modalities']) > 1  # Cross-modal
    
    @pytest.mark.asyncio
    async def test_entity_filtering(self, linker):
        """Test entity candidate filtering and validation"""
        # Test with invalid entities
        entity_candidates = {
            'text': [
                {'text_content': ''},  # Empty content
                {'text_content': '   '},  # Whitespace only
                {'text_content': 'Valid text'}  # Valid
            ],
            'image': [
                {},  # Missing required fields
                {'image_path': '/valid/path.jpg'}  # Valid
            ],
            'unknown_modality': [  # Unknown modality
                {'data': 'something'}
            ]
        }
        
        # Filter candidates
        filtered = await linker._filter_entity_candidates(entity_candidates)
        
        # Verify filtering
        assert len(filtered['text']) == 1  # Only valid text
        assert len(filtered['image']) == 1  # Only valid image
        assert 'unknown_modality' not in filtered
    
    @pytest.mark.asyncio
    async def test_similarity_calculation(self, linker):
        """Test cross-modal similarity matrix calculation"""
        # Create test embeddings
        modal_embeddings = {
            'text': np.array([[1, 0, 0], [0, 1, 0]]),
            'image': np.array([[0.9, 0.1, 0], [0.1, 0.9, 0]])
        }
        
        # Calculate similarities
        similarity_matrices = await linker._calculate_cross_modal_similarities(modal_embeddings)
        
        # Verify similarity matrix exists
        assert 'text_image' in similarity_matrices
        
        # Check similarity values
        sim_matrix = similarity_matrices['text_image']
        assert sim_matrix.shape == (2, 2)
        
        # High similarity between (text[0], image[0]) and (text[1], image[1])
        assert sim_matrix[0, 0] > 0.8  # Similar vectors
        assert sim_matrix[1, 1] > 0.8  # Similar vectors
        assert sim_matrix[0, 1] < 0.5  # Dissimilar vectors
        assert sim_matrix[1, 0] < 0.5  # Dissimilar vectors
    
    @pytest.mark.asyncio
    async def test_graph_context_retrieval(self, linker, mock_neo4j_manager):
        """Test graph context retrieval for entities"""
        # Mock entity with ID
        entity = {'entity_id': 123, 'name': 'Test Entity'}
        
        # Mock graph context query result
        mock_neo4j_manager.execute_read_query.return_value = [{
            'connected_entities': [456, 789],
            'relationship_types': ['CITES', 'RELATED_TO']
        }]
        
        # Get context
        context = await linker._query_entity_context(entity, 'text')
        
        # Verify context
        assert context['connected_entities'] == [456, 789]
        assert context['relationship_types'] == ['CITES', 'RELATED_TO']
    
    @pytest.mark.asyncio
    async def test_entity_resolution(self):
        """Test entity resolution algorithm"""
        # Create test similarity matrices
        similarity_matrices = {
            'text': np.array([[1, 0], [0, 1]]),
            'image': np.array([[1, 0], [0, 1]]),
            'text_image': np.array([[0.9, 0.1], [0.1, 0.9]])
        }
        
        # Create graph contexts
        graph_contexts = {
            'text_0': {'connected_entities': [1, 2, 3]},
            'text_1': {'connected_entities': [4, 5, 6]},
            'image_0': {'connected_entities': [1, 2, 7]},  # Overlaps with text_0
            'image_1': {'connected_entities': [4, 5, 8]}   # Overlaps with text_1
        }
        
        # Create resolver
        resolver = EntityResolver(
            similarity_matrices=similarity_matrices,
            graph_contexts=graph_contexts,
            similarity_threshold=0.85
        )
        
        # Resolve entities
        clusters = await resolver.resolve_entities()
        
        # Verify clustering
        assert len(clusters) > 0
        
        # Check that similar entities are clustered together
        for cluster in clusters:
            assert cluster['size'] >= 2  # At least 2 entities per cluster
            assert cluster['cross_modal_count'] >= 2  # Cross-modal clusters
    
    @pytest.mark.asyncio
    async def test_cross_modal_graph_construction(self, linker):
        """Test cross-modal graph construction"""
        # Create test linked entities
        linked_entities = [
            {
                'cluster_id': 0,
                'entities': {
                    'text': [{'text_content': 'Entity 1'}],
                    'image': [{'image_path': '/path/1.jpg'}]
                },
                'size': 2,
                'modalities': ['text', 'image'],
                'cross_modal_count': 2
            },
            {
                'cluster_id': 1,
                'entities': {
                    'text': [{'text_content': 'Entity 2'}, {'text_content': 'Entity 3'}],
                    'structured': [{'structured_data': {'key': 'value'}}]
                },
                'size': 3,
                'modalities': ['text', 'structured'],
                'cross_modal_count': 2
            }
        ]
        
        # Build graph
        graph = await linker._build_cross_modal_graph(linked_entities)
        
        # Verify graph structure
        assert 'nodes' in graph
        assert 'edges' in graph
        assert graph['total_clusters'] == 2
        
        # Check nodes
        cluster_nodes = [n for n in graph['nodes'] if n['type'] == 'entity_cluster']
        entity_nodes = [n for n in graph['nodes'] if n['type'] == 'entity']
        
        assert len(cluster_nodes) == 2
        assert len(entity_nodes) == 5  # Total entities across clusters
        
        # Check edges
        belongs_to_edges = [e for e in graph['edges'] if e['type'] == 'belongs_to']
        linked_edges = [e for e in graph['edges'] if e['type'] == 'linked_entity']
        
        assert len(belongs_to_edges) == 5  # Each entity belongs to a cluster
        assert len(linked_edges) > 0  # Entities within clusters are linked
    
    @pytest.mark.asyncio
    async def test_linking_metrics_calculation(self, linker):
        """Test linking metrics calculation"""
        # Create test data
        entity_candidates = {
            'text': [{'text_content': f'Text {i}'} for i in range(10)],
            'image': [{'image_path': f'/img_{i}.jpg'} for i in range(8)],
            'structured': [{'structured_data': {'id': i}} for i in range(5)]
        }
        
        linked_entities = [
            {
                'cluster_id': 0,
                'entities': {
                    'text': entity_candidates['text'][:3],
                    'image': entity_candidates['image'][:2]
                },
                'size': 5,
                'modalities': ['text', 'image'],
                'cross_modal_count': 2
            },
            {
                'cluster_id': 1,
                'entities': {
                    'text': entity_candidates['text'][3:5],
                    'structured': entity_candidates['structured'][:2]
                },
                'size': 4,
                'modalities': ['text', 'structured'],
                'cross_modal_count': 2
            }
        ]
        
        # Calculate metrics
        metrics = await linker._calculate_linking_metrics(entity_candidates, linked_entities)
        
        # Verify metrics
        assert metrics['total_entities'] == 23  # 10 + 8 + 5
        assert metrics['linked_entities'] == 9   # 5 + 4
        assert metrics['linking_rate'] == 9/23
        assert metrics['total_clusters'] == 2
        assert metrics['cross_modal_clusters'] == 2
        
        # Check modality coverage
        assert 'text' in metrics['modality_coverage']
        assert metrics['modality_coverage']['text'] == 5/10  # 5 out of 10 text entities linked
    
    @pytest.mark.asyncio
    async def test_empty_input_handling(self, linker):
        """Test handling of empty input"""
        # Empty entity candidates
        result = await linker.link_cross_modal_entities({})
        
        # Verify empty result
        assert result['linked_entities'] == []
        assert result['linking_metrics']['total_entities'] == 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, linker, mock_dtm):
        """Test error handling and transaction rollback"""
        # Cause error in embedding generation
        linker.embedding_service.generate_text_embeddings.side_effect = Exception("Embedding error")
        
        entity_candidates = {
            'text': [{'text_content': 'Test'}]
        }
        
        # Execute and expect error
        with pytest.raises(AnalyticsError) as exc_info:
            await linker.link_cross_modal_entities(entity_candidates)
        
        # Verify error message
        assert "Cross-modal entity linking failed" in str(exc_info.value)
        
        # Verify transaction was rolled back
        mock_dtm.rollback_distributed_transaction.assert_called_once()


class TestEntityResolver:
    """Test suite for EntityResolver"""
    
    @pytest.mark.asyncio
    async def test_context_similarity_calculation(self):
        """Test graph context similarity calculation"""
        resolver = EntityResolver({}, {})
        
        # Test with overlapping contexts
        context1 = {'connected_entities': [1, 2, 3, 4]}
        context2 = {'connected_entities': [2, 3, 5, 6]}
        
        similarity = await resolver._calculate_context_similarity(context1, context2)
        
        # Jaccard similarity: |{2,3}| / |{1,2,3,4,5,6}| = 2/6 = 0.333
        assert abs(similarity - 0.333) < 0.01
        
        # Test with identical contexts
        similarity = await resolver._calculate_context_similarity(context1, context1)
        assert similarity == 1.0
        
        # Test with no overlap
        context3 = {'connected_entities': [7, 8, 9]}
        similarity = await resolver._calculate_context_similarity(context1, context3)
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    async def test_high_confidence_match_extraction(self):
        """Test extraction of high-confidence matches"""
        resolver = EntityResolver({}, {}, similarity_threshold=0.8)
        
        # Create similarity matrix
        sim_matrix = np.array([
            [1.0, 0.9, 0.3],
            [0.9, 1.0, 0.4],
            [0.3, 0.4, 1.0]
        ])
        
        # Extract matches
        matches = await resolver._extract_high_confidence_matches(sim_matrix, 'text', 'image')
        
        # Verify high-confidence matches
        assert len(matches) > 0
        
        # Check that only high-confidence matches are included
        for match in matches:
            assert match['similarity_score'] >= 0.8
            assert match['modality_1'] == 'text'
            assert match['modality_2'] == 'image'


class TestMockEmbeddingService:
    """Test mock embedding service"""
    
    @pytest.mark.asyncio
    async def test_mock_embeddings(self):
        """Test mock embedding generation"""
        service = MockEmbeddingService()
        
        # Test text embeddings
        text_emb = await service.generate_text_embeddings(['text1', 'text2'])
        assert text_emb.shape == (2, 384)
        
        # Test image embeddings
        image_emb = await service.generate_image_embeddings(['img1.jpg', 'img2.jpg'])
        assert image_emb.shape == (2, 512)
        
        # Test structured embeddings
        struct_emb = await service.generate_structured_embeddings([{'a': 1}, {'b': 2}])
        assert struct_emb.shape == (2, 256)