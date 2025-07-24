"""
Test suite for enhanced IdentityService coordination.

This module follows TDD approach - tests are written BEFORE implementation.
Tests MUST fail initially to ensure we're testing the right behavior.
"""

import pytest
import asyncio
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Configure pytest to handle async tests
pytestmark = pytest.mark.asyncio

# Import components to be tested
from src.core.enhanced_identity_service import EnhancedIdentityService as IdentityService
from src.core.workflow_models import DocumentResult
from src.core.exceptions import ServiceException


class TestIdentityServiceCoordination:
    """Test suite for enhanced IdentityService with cross-modal entity resolution."""
    
    @pytest.fixture
    def identity_service(self):
        """Create an IdentityService instance for testing."""
        # For testing, create service directly
        service = IdentityService(
            use_embeddings=False,  # Disable for testing
            persistence_path=None,  # In-memory only
            similarity_threshold=0.85
        )
        return service
    
    @pytest.fixture
    def test_entities(self):
        """Sample entities for testing."""
        return [
            {
                'surface_form': 'quantum computing',
                'entity_type': 'TECHNOLOGY',
                'start_pos': 10,
                'end_pos': 27,
                'confidence': 0.95,
                'source': 'doc1',
                'modality': 'graph'
            },
            {
                'surface_form': 'Quantum Computing',  # Different case
                'entity_type': 'TECHNOLOGY',
                'start_pos': 50,
                'end_pos': 67,
                'confidence': 0.90,
                'source': 'doc1',
                'modality': 'table'
            },
            {
                'surface_form': 'QC',  # Abbreviation
                'entity_type': 'TECHNOLOGY',
                'start_pos': 100,
                'end_pos': 102,
                'confidence': 0.80,
                'source': 'doc1',
                'modality': 'vector'
            }
        ]
    
    async def test_cross_modal_entity_resolution(
        self, identity_service, test_entities
    ):
        """Test entity resolution across graph, table, vector modes."""
        # Create mentions from different modalities
        mention_ids = []
        for entity in test_entities:
            result = await identity_service.create_mention(
                surface_form=entity['surface_form'],
                start_pos=entity['start_pos'],
                end_pos=entity['end_pos'],
                source_ref=entity['source'],
                entity_type=entity['entity_type'],
                confidence=entity['confidence'],
                modality=entity['modality']
            )
            assert result.success
            mention_ids.append(result.data['mention_id'])
        
        # Resolve entities across modalities
        resolution_result = await identity_service.resolve_cross_modal_entities(
            mention_ids=mention_ids
        )
        
        assert resolution_result.success
        assert 'unified_entity' in resolution_result.data
        
        unified_entity = resolution_result.data['unified_entity']
        assert unified_entity['canonical_form'] == 'Quantum Computing'
        assert unified_entity['entity_type'] == 'TECHNOLOGY'
        assert len(unified_entity['mentions']) == 3
        assert set(unified_entity['modalities']) == {'graph', 'table', 'vector'}
        assert unified_entity['confidence'] >= 0.85
        
        # Verify all mentions are linked
        for mention_id in mention_ids:
            mention_entity = await identity_service.get_entity_by_mention(mention_id)
            assert mention_entity.success
            assert mention_entity.data['entity_id'] == unified_entity['entity_id']
    
    async def test_entity_conflict_resolution(
        self, identity_service
    ):
        """Test handling of entity identity conflicts."""
        # Create conflicting entities
        mention1 = await identity_service.create_mention(
            surface_form='Apple Inc.',
            start_pos=0,
            end_pos=10,
            source_ref='doc1',
            entity_type='ORGANIZATION',
            confidence=0.95,
            modality='graph'
        )
        
        mention2 = await identity_service.create_mention(
            surface_form='Apple',
            start_pos=50,
            end_pos=55,
            source_ref='doc2',
            entity_type='FRUIT',  # Different type - conflict!
            confidence=0.90,
            modality='table'
        )
        
        mention3 = await identity_service.create_mention(
            surface_form='AAPL',
            start_pos=100,
            end_pos=104,
            source_ref='doc3',
            entity_type='ORGANIZATION',
            confidence=0.85,
            modality='vector'
        )
        
        # Attempt to resolve with conflicts
        resolution_result = await identity_service.resolve_entities_with_conflicts(
            mention_ids=[
                mention1.data['mention_id'],
                mention2.data['mention_id'],
                mention3.data['mention_id']
            ]
        )
        
        assert resolution_result.success
        assert 'resolved_entities' in resolution_result.data
        assert 'conflicts' in resolution_result.data
        
        # Should create two separate entities due to type conflict
        resolved = resolution_result.data['resolved_entities']
        assert len(resolved) == 2
        
        # Verify conflict was detected and logged
        conflicts = resolution_result.data['conflicts']
        assert len(conflicts) > 0
        assert conflicts[0]['reason'] == 'entity_type_mismatch'
        assert conflicts[0]['resolution_strategy'] == 'split_entities'
    
    async def test_identity_persistence_across_sessions(
        self, identity_service
    ):
        """Test entity identity persistence and recovery."""
        # Create entity in first session
        mention_result = await identity_service.create_mention(
            surface_form='Machine Learning',
            start_pos=0,
            end_pos=16,
            source_ref='doc1',
            entity_type='TECHNOLOGY',
            confidence=0.92
        )
        
        assert mention_result.success
        entity_id = mention_result.data['entity_id']
        mention_id = mention_result.data['mention_id']
        
        # Persist current state
        persist_result = await identity_service.persist_state()
        assert persist_result.success
        assert persist_result.data['entities_persisted'] > 0
        assert persist_result.data['mentions_persisted'] > 0
        
        # Simulate new session by creating new service instance
        new_service = IdentityService()
        new_service.initialize({
            'entity_resolution_threshold': 0.85,
            'persistence_enabled': True
        })
        
        # Restore state
        restore_result = await new_service.restore_state()
        assert restore_result.success
        assert restore_result.data['entities_restored'] > 0
        assert restore_result.data['mentions_restored'] > 0
        
        # Verify entity can be retrieved
        entity_result = await new_service.get_entity_by_id(entity_id)
        assert entity_result.success
        assert entity_result.data['canonical_form'] == 'Machine Learning'
        assert entity_result.data['entity_type'] == 'TECHNOLOGY'
        
        # Verify mention linkage is preserved
        mention_entity = await new_service.get_entity_by_mention(mention_id)
        assert mention_entity.success
        assert mention_entity.data['entity_id'] == entity_id
    
    async def test_batch_entity_resolution(
        self, identity_service
    ):
        """Test batch processing of entity resolution."""
        # Create many mentions
        mentions = []
        for i in range(100):
            entity_type = 'PERSON' if i % 2 == 0 else 'ORGANIZATION'
            mention = {
                'surface_form': f'Entity_{i // 10}',  # 10 mentions per entity
                'start_pos': i * 10,
                'end_pos': i * 10 + 8,
                'source_ref': f'doc_{i % 5}',
                'entity_type': entity_type,
                'confidence': 0.8 + (i % 20) * 0.01
            }
            mentions.append(mention)
        
        # Batch create mentions
        batch_result = await identity_service.batch_create_mentions(mentions)
        assert batch_result.success
        assert batch_result.data['created_count'] == 100
        assert len(batch_result.data['mention_ids']) == 100
        
        # Batch resolve entities
        resolve_result = await identity_service.batch_resolve_entities()
        assert resolve_result.success
        
        # Should have ~10 unified entities (Entity_0 through Entity_9)
        stats = resolve_result.data['resolution_stats']
        assert stats['total_mentions'] == 100
        assert 8 <= stats['unified_entities'] <= 12  # Allow for some variation
        assert stats['cross_modal_links'] > 0
        assert stats['conflicts_resolved'] >= 0
    
    async def test_entity_similarity_calculation(
        self, identity_service
    ):
        """Test entity similarity calculation for resolution."""
        # Create base entity
        base_mention = await identity_service.create_mention(
            surface_form='International Business Machines',
            start_pos=0,
            end_pos=31,
            source_ref='doc1',
            entity_type='ORGANIZATION',
            confidence=0.95
        )
        
        # Test various similarity cases
        test_cases = [
            {
                'surface_form': 'IBM',  # Abbreviation
                'expected_similarity': 0.90,
                'should_match': True
            },
            {
                'surface_form': 'International Business Machines Corporation',  # Extended
                'expected_similarity': 0.95,
                'should_match': True
            },
            {
                'surface_form': 'I.B.M.',  # Punctuated abbreviation
                'expected_similarity': 0.85,
                'should_match': True
            },
            {
                'surface_form': 'Microsoft',  # Different entity
                'expected_similarity': 0.2,
                'should_match': False
            }
        ]
        
        base_entity_id = base_mention.data['entity_id']
        
        for test_case in test_cases:
            similarity_result = await identity_service.calculate_entity_similarity(
                surface_form=test_case['surface_form'],
                entity_type='ORGANIZATION',
                target_entity_id=base_entity_id
            )
            
            assert similarity_result.success
            similarity_score = similarity_result.data['similarity_score']
            
            # Check similarity is in expected range
            assert abs(similarity_score - test_case['expected_similarity']) < 0.15
            
            # Check match decision
            matches = similarity_score >= 0.85  # Threshold
            assert matches == test_case['should_match']
    
    async def test_entity_merge_operation(
        self, identity_service
    ):
        """Test merging of duplicate entities."""
        # Create duplicate entities
        entity1 = await identity_service.create_mention(
            surface_form='Google',
            start_pos=0,
            end_pos=6,
            source_ref='doc1',
            entity_type='ORGANIZATION',
            confidence=0.90
        )
        
        entity2 = await identity_service.create_mention(
            surface_form='Google Inc',
            start_pos=50,
            end_pos=60,
            source_ref='doc2',
            entity_type='ORGANIZATION',
            confidence=0.85
        )
        
        entity3 = await identity_service.create_mention(
            surface_form='Alphabet/Google',
            start_pos=100,
            end_pos=115,
            source_ref='doc3',
            entity_type='ORGANIZATION',
            confidence=0.80
        )
        
        entity_ids = [
            entity1.data['entity_id'],
            entity2.data['entity_id'],
            entity3.data['entity_id']
        ]
        
        # Merge entities
        merge_result = await identity_service.merge_entities(
            entity_ids=entity_ids,
            canonical_form='Google',
            merge_strategy='confidence_weighted'
        )
        
        assert merge_result.success
        merged_entity = merge_result.data['merged_entity']
        
        # Verify merge results
        assert merged_entity['canonical_form'] == 'Google'
        assert len(merged_entity['mentions']) == 3
        assert merged_entity['confidence'] >= 0.85  # Weighted average
        assert len(merged_entity['aliases']) >= 2  # Inc, Alphabet/Google
        
        # Verify all mentions now point to merged entity
        for mention in [entity1, entity2, entity3]:
            mention_id = mention.data['mention_id']
            updated = await identity_service.get_entity_by_mention(mention_id)
            assert updated.data['entity_id'] == merged_entity['entity_id']
    
    async def test_cross_modal_entity_tracking(
        self, identity_service
    ):
        """Test tracking entity appearances across modalities."""
        # Create entity mentions across different modalities
        entity_mentions = [
            ('graph', 5, 0.95),
            ('table', 3, 0.90),
            ('vector', 8, 0.85),
            ('graph', 2, 0.92),  # More graph mentions
        ]
        
        for modality, count, confidence in entity_mentions:
            for i in range(count):
                await identity_service.create_mention(
                    surface_form='Neural Network',
                    start_pos=i * 20,
                    end_pos=i * 20 + 14,
                    source_ref=f'doc_{modality}_{i}',
                    entity_type='TECHNOLOGY',
                    confidence=confidence,
                    modality=modality
                )
        
        # Get cross-modal statistics
        stats_result = await identity_service.get_entity_cross_modal_stats(
            entity_surface_form='Neural Network'
        )
        
        assert stats_result.success
        stats = stats_result.data
        
        # Verify statistics
        assert stats['total_mentions'] == 18  # 5+3+8+2
        assert stats['modality_distribution']['graph'] == 7  # 5+2
        assert stats['modality_distribution']['table'] == 3
        assert stats['modality_distribution']['vector'] == 8
        assert stats['dominant_modality'] == 'vector'
        assert stats['cross_modal_confidence'] >= 0.85
        
        # Verify temporal tracking
        assert 'first_seen' in stats
        assert 'last_seen' in stats
        assert stats['active_documents'] >= 4
    
    async def test_entity_health_check(
        self, identity_service
    ):
        """Test IdentityService health check functionality."""
        health_result = await identity_service.health_check()
        
        assert health_result.success
        health_data = health_result.data
        
        # Verify health metrics
        assert 'service' in health_data
        assert health_data['service'] == 'IdentityService'
        assert 'state' in health_data
        assert health_data['state'] in ['ready', 'busy']
        assert 'entity_count' in health_data
        assert 'mention_count' in health_data
        assert 'cache_hit_rate' in health_data
        assert 'resolution_accuracy' in health_data
        assert health_data['resolution_accuracy'] >= 0.85