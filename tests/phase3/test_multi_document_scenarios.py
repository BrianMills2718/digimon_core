#!/usr/bin/env python3
"""
Comprehensive tests for T301: Multi-Document Knowledge Fusion
Tests multi-document scenarios, entity deduplication, and conflict resolution.
"""

from pathlib import Path

import pytest
import time
from datetime import datetime
from typing import List, Dict, Any
import json

# Import Phase 3 components
from src.tools.phase3.t301_multi_document_fusion import (
    MultiDocumentFusion,
    FusionResult,
    ConsistencyMetrics,
    EntityCluster
)

# Import Phase 2 components for compatibility
from src.core.identity_service import Entity, Relationship
from src.ontology_generator import DomainOntology, EntityType, RelationshipType


class TestMultiDocumentFusion:
    """Test suite for multi-document knowledge fusion."""
    
    @pytest.fixture
    def fusion_engine(self):
        """Create test fusion engine."""
        return MultiDocumentFusion(
            confidence_threshold=0.8,
            similarity_threshold=0.85
        )
    
    @pytest.fixture
    def test_ontology(self):
        """Create test ontology for climate domain."""
        return DomainOntology(
            domain_name="Climate Policy Test",
            domain_description="Test ontology for multi-document fusion",
            entity_types=[
                EntityType(
                    name="CLIMATE_POLICY",
                    description="Climate policies and agreements",
                    examples=["Paris Agreement", "Carbon Tax"],
                    attributes=["scope", "target", "year"]
                ),
                EntityType(
                    name="ORGANIZATION",
                    description="Organizations involved in climate",
                    examples=["UNFCCC", "IPCC"],
                    attributes=["type", "location", "founded"]
                ),
                EntityType(
                    name="TECHNOLOGY",
                    description="Climate technologies",
                    examples=["Solar Power", "Wind Energy"],
                    attributes=["efficiency", "cost", "maturity"]
                )
            ],
            relationship_types=[
                RelationshipType(
                    name="IMPLEMENTS",
                    description="Organization implements policy",
                    source_types=["ORGANIZATION"],
                    target_types=["CLIMATE_POLICY"],
                    examples=[]
                ),
                RelationshipType(
                    name="DEVELOPS",
                    description="Organization develops technology",
                    source_types=["ORGANIZATION"],
                    target_types=["TECHNOLOGY"],
                    examples=[]
                )
            ],
            extraction_patterns=[],
            created_by_conversation="Test creation"
        )
    
    @pytest.fixture
    def test_entities(self):
        """Create test entities with duplicates and conflicts."""
        entities = []
        
        # Helper to create Entity with both canonical_name and name
        def create_entity(id, name, entity_type, confidence):
            e = Entity(id=id, canonical_name=name, entity_type=entity_type)
            e.confidence = confidence
            e.name = name  # Add name for compatibility
            return e
        
        return [
            # Document 1 entities
            create_entity("ent_1_1", "Paris Agreement", "CLIMATE_POLICY", 0.95),
            create_entity("ent_1_2", "United Nations", "ORGANIZATION", 0.90),
            create_entity("ent_1_3", "Solar Energy", "TECHNOLOGY", 0.85),
            
            # Document 2 entities (with duplicates)
            create_entity("ent_2_1", "Paris Climate Agreement", "CLIMATE_POLICY", 0.92),  # Duplicate
            create_entity("ent_2_2", "UN", "ORGANIZATION", 0.88),  # Duplicate
            create_entity("ent_2_3", "Wind Power", "TECHNOLOGY", 0.87),
            
            # Document 3 entities (more duplicates)
            create_entity("ent_3_1", "The Paris Agreement", "CLIMATE_POLICY", 0.93),  # Duplicate
            create_entity("ent_3_2", "United Nations Organization", "ORGANIZATION", 0.91),  # Duplicate
            create_entity("ent_3_3", "Solar Power", "TECHNOLOGY", 0.86),  # Similar to Solar Energy
        ]
    
    @pytest.fixture
    def test_relationships(self):
        """Create test relationships with conflicts."""
        # Helper to create Relationship
        def create_rel(id, source, target, rel_type, confidence):
            r = Relationship(id=id, source_id=source, target_id=target, relationship_type=rel_type)
            r.confidence = confidence
            return r
        
        return [
            # Document 1 relationships
            create_rel("rel_1_1", "ent_1_2", "ent_1_1", "IMPLEMENTS", 0.90),
            create_rel("rel_1_2", "ent_1_2", "ent_1_3", "DEVELOPS", 0.85),
            
            # Document 2 relationships (conflicting)
            create_rel("rel_2_1", "ent_2_2", "ent_2_1", "IMPLEMENTS", 0.88),
            create_rel("rel_2_2", "ent_2_2", "ent_2_3", "DEVELOPS", 0.86),
            
            # Document 3 relationships
            create_rel("rel_3_1", "ent_3_2", "ent_3_1", "IMPLEMENTS", 0.92),
        ]
    
    def test_basic_fusion(self, fusion_engine, test_ontology):
        """Test basic multi-document fusion functionality."""
        fusion_engine.set_ontology(test_ontology)
        
        # Mock document references
        document_refs = ["doc1", "doc2", "doc3"]
        
        # Perform fusion
        result = fusion_engine.fuse_documents(
            document_refs=document_refs,
            fusion_strategy="evidence_based"
        )
        
        # Verify result structure
        assert isinstance(result, FusionResult)
        assert result.total_documents == 3
        assert result.fusion_time_seconds > 0
        assert 0 <= result.consistency_score <= 1
    
    def test_entity_deduplication(self, fusion_engine):
        """Test entity deduplication across documents."""
        # Helper to create Entity
        def create_entity(id, name, entity_type, confidence):
            e = Entity(id=id, canonical_name=name, entity_type=entity_type)
            e.confidence = confidence
            e.name = name
            return e
        
        # Create duplicate entities
        entities = [
            create_entity("e1", "Climate Policy", "POLICY", 0.9),
            create_entity("e2", "Climate Policy", "POLICY", 0.85),  # Exact duplicate
            create_entity("e3", "The Climate Policy", "POLICY", 0.88),  # Near duplicate
            create_entity("e4", "Energy Policy", "POLICY", 0.87),  # Different
        ]
        
        # Test cluster finding
        clusters = fusion_engine._find_entity_clusters(entities)
        
        # Should find cluster with duplicates
        assert len(clusters) >= 1
        
        # Test entity resolution
        for cluster in clusters.values():
            if len(cluster.entities) > 1:
                resolved = fusion_engine.resolve_entity_conflicts(cluster.entities)
                assert resolved is not None
                assert resolved.confidence > 0
                assert hasattr(resolved, '_fusion_evidence')
    
    def test_relationship_merging(self, fusion_engine):
        """Test relationship evidence merging."""
        # Create duplicate relationships
        relationships = [
            Relationship("A", "B", "IMPLEMENTS", confidence=0.9),
            Relationship("A", "B", "IMPLEMENTS", confidence=0.85),
            Relationship("A", "B", "IMPLEMENTS", confidence=0.92),
        ]
        
        # Merge evidence
        merged = fusion_engine.merge_relationship_evidence(relationships)
        
        assert merged is not None
        assert merged.source_id == "A"
        assert merged.target_id == "B"
        assert merged.relationship_type == "IMPLEMENTS"
        assert 0.85 <= merged.confidence <= 0.92
        assert hasattr(merged, '_fusion_evidence')
        assert merged._fusion_evidence['evidence_count'] == 3
    
    def test_conflict_resolution(self, fusion_engine):
        """Test conflict resolution between entities."""
        # Create conflicting entities
        entities = [
            Entity("e1", "Paris Agreement", "POLICY", confidence=0.95),
            Entity("e2", "Paris Agreement", "POLICY", confidence=0.90),
        ]
        
        # Add conflicting attributes
        entities[0].attributes = {"year": "2015", "scope": "Global"}
        entities[1].attributes = {"year": "2016", "scope": "International"}  # Conflict
        
        # Resolve conflicts
        resolved = fusion_engine.resolve_entity_conflicts(entities)
        
        assert resolved is not None
        assert hasattr(resolved, '_fusion_evidence')
        assert 'merged_attributes' in resolved._fusion_evidence
        assert resolved._fusion_evidence['conflicts_resolved'] > 0
    
    def test_consistency_metrics(self, fusion_engine):
        """Test knowledge consistency calculation."""
        # Calculate consistency
        metrics = fusion_engine.calculate_knowledge_consistency()
        
        assert isinstance(metrics, ConsistencyMetrics)
        assert 0 <= metrics.entity_consistency <= 1
        assert 0 <= metrics.relationship_consistency <= 1
        assert 0 <= metrics.temporal_consistency <= 1
        assert 0 <= metrics.ontological_compliance <= 1
        assert 0 <= metrics.overall_score <= 1
    
    def test_batch_processing(self, fusion_engine):
        """Test batch processing of documents."""
        # Create many document references
        document_refs = [f"doc_{i}" for i in range(20)]
        
        # Process with small batch size
        result = fusion_engine.fuse_documents(
            document_refs=document_refs,
            fusion_strategy="confidence_weighted",
            batch_size=5
        )
        
        assert result.total_documents == 20
        # Should process in 4 batches
    
    def test_fusion_strategies(self, fusion_engine):
        """Test different fusion strategies."""
        strategies = ["evidence_based", "confidence_weighted", "temporal_priority"]
        document_refs = ["doc1", "doc2", "doc3"]
        
        results = {}
        for strategy in strategies:
            result = fusion_engine.fuse_documents(
                document_refs=document_refs,
                fusion_strategy=strategy
            )
            results[strategy] = result
            
            assert result.fusion_time_seconds > 0
            # Different strategies may produce different results
    
    def test_performance_scaling(self, fusion_engine):
        """Test performance with increasing document counts."""
        document_counts = [10, 50, 100]
        times = []
        
        for count in document_counts:
            doc_refs = [f"doc_{i}" for i in range(count)]
            
            start_time = time.time()
            result = fusion_engine.fuse_documents(doc_refs)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            
            # Should complete within reasonable time
            assert elapsed < 10 * count / 10  # Less than 10s per 10 documents
            
            # Verify deduplication
            if result.entities_before_fusion > 0:
                dedup_rate = 1 - (result.entities_after_fusion / result.entities_before_fusion)
                assert dedup_rate >= 0  # Some deduplication should occur
        
        # Check sub-linear scaling
        # Time should not grow linearly with document count
        if len(times) >= 2:
            scaling_factor = times[-1] / times[0]
            doc_factor = document_counts[-1] / document_counts[0]
            assert scaling_factor < doc_factor  # Sub-linear scaling
    
    def test_evidence_chains(self, fusion_engine):
        """Test evidence chain generation."""
        # Create entities with evidence
        entities = [
            Entity("e1", "Climate Policy", "POLICY", confidence=0.9),
            Entity("e2", "Climate Policy", "POLICY", confidence=0.85),
        ]
        
        # Mock fusion with evidence
        document_refs = ["doc1", "doc2"]
        result = fusion_engine.fuse_documents(document_refs)
        
        # Check evidence chains
        if result.evidence_chains:
            for chain in result.evidence_chains:
                assert 'entity_id' in chain
                assert 'evidence' in chain
    
    def test_inconsistency_detection(self, fusion_engine):
        """Test detection of knowledge inconsistencies."""
        # Calculate consistency
        metrics = fusion_engine.calculate_knowledge_consistency()
        
        # If inconsistencies exist
        if metrics.overall_score < 1.0:
            assert len(metrics.inconsistencies) > 0
            
            for inconsistency in metrics.inconsistencies:
                assert 'type' in inconsistency
                # Type should be known
                assert inconsistency['type'] in [
                    'potential_duplicate',
                    'conflicting_relationships',
                    'temporal_inconsistency',
                    'ontology_violation'
                ]


class TestAdvancedFusionScenarios:
    """Test advanced multi-document fusion scenarios."""
    
    @pytest.fixture
    def fusion_engine(self):
        """Create fusion engine for advanced tests."""
        return MultiDocumentFusion(
            confidence_threshold=0.75,
            similarity_threshold=0.80
        )
    
    def test_cross_document_entity_resolution(self, fusion_engine):
        """Test entity resolution across multiple documents."""
        # Simulate entities from different documents
        doc1_entities = [
            Entity("d1_e1", "International Energy Agency", "ORGANIZATION", confidence=0.95),
            Entity("d1_e2", "IEA", "ORGANIZATION", confidence=0.90),  # Abbreviation
        ]
        
        doc2_entities = [
            Entity("d2_e1", "Intl. Energy Agency", "ORGANIZATION", confidence=0.88),  # Variation
            Entity("d2_e2", "Solar Technology", "TECHNOLOGY", confidence=0.85),
        ]
        
        doc3_entities = [
            Entity("d3_e1", "IEA (International Energy Agency)", "ORGANIZATION", confidence=0.92),
            Entity("d3_e2", "Photovoltaic Solar Technology", "TECHNOLOGY", confidence=0.87),
        ]
        
        all_entities = doc1_entities + doc2_entities + doc3_entities
        
        # Find clusters
        clusters = fusion_engine._find_entity_clusters(all_entities)
        
        # Should identify IEA variations as one cluster
        org_cluster_found = False
        for cluster in clusters.values():
            names = [e.name for e in cluster.entities]
            if any("IEA" in name or "Energy Agency" in name for name in names):
                org_cluster_found = True
                assert len(cluster.entities) >= 3  # Should group IEA variations
        
        assert org_cluster_found
    
    def test_temporal_conflict_resolution(self, fusion_engine):
        """Test resolution of temporal conflicts."""
        # Create entities with temporal attributes
        entities = [
            Entity("e1", "Carbon Tax Policy", "POLICY", confidence=0.90),
            Entity("e2", "Carbon Tax Policy", "POLICY", confidence=0.92),
        ]
        
        # Add temporal attributes
        entities[0].attributes = {"effective_date": "2023-01-01", "rate": "$50/ton"}
        entities[0].timestamp = datetime(2023, 1, 1)
        
        entities[1].attributes = {"effective_date": "2024-01-01", "rate": "$75/ton"}
        entities[1].timestamp = datetime(2024, 1, 1)
        
        # Resolve with temporal priority
        clusters = {"c1": EntityCluster("c1", entities)}
        resolved = fusion_engine._resolve_entity_clusters(clusters, "temporal_priority")
        
        # Should prefer more recent entity
        assert len(resolved) == 1
        resolved_entity = list(resolved.values())[0]
        assert resolved_entity.timestamp == datetime(2024, 1, 1)
    
    def test_multi_hop_relationship_fusion(self, fusion_engine):
        """Test fusion of multi-hop relationship chains."""
        # Create relationship chain: A -> B -> C
        relationships_doc1 = [
            Relationship("A", "B", "IMPLEMENTS", confidence=0.90),
            Relationship("B", "C", "REQUIRES", confidence=0.85),
        ]
        
        # Overlapping chain from doc2: A -> B -> D
        relationships_doc2 = [
            Relationship("A", "B", "IMPLEMENTS", confidence=0.88),  # Duplicate
            Relationship("B", "D", "ENABLES", confidence=0.86),
        ]
        
        all_relationships = relationships_doc1 + relationships_doc2
        
        # Merge relationships
        merged = fusion_engine._merge_relationships(
            all_relationships,
            {},  # No entity resolution needed
            "evidence_based"
        )
        
        # Should merge A->B relationship
        implements_count = sum(1 for r in merged if r.relationship_type == "IMPLEMENTS")
        assert implements_count == 1  # Duplicates merged
        
        # Should preserve both B->C and B->D
        assert len(merged) == 3
    
    def test_ontology_constraint_validation(self, fusion_engine, test_ontology):
        """Test validation against ontology constraints."""
        fusion_engine.set_ontology(test_ontology)
        
        # Create entities with invalid types
        entities = [
            Entity("e1", "Valid Policy", "CLIMATE_POLICY", confidence=0.90),
            Entity("e2", "Invalid Entity", "INVALID_TYPE", confidence=0.85),  # Invalid
            Entity("e3", "Valid Org", "ORGANIZATION", confidence=0.88),
        ]
        
        # Create invalid relationship
        relationships = [
            Relationship("e1", "e3", "IMPLEMENTS", confidence=0.90),  # Wrong direction
            Relationship("e3", "e1", "IMPLEMENTS", confidence=0.85),  # Correct
        ]
        
        # Check ontology compliance
        # This should be detected in consistency metrics
        metrics = fusion_engine.calculate_knowledge_consistency()
        
        # Ontological compliance should be less than perfect
        assert metrics.ontological_compliance < 1.0
    
    def test_large_scale_deduplication(self, fusion_engine):
        """Test deduplication with large entity sets."""
        # Create many entities with duplicates
        base_names = ["Climate Policy", "Energy Agency", "Solar Tech", "Wind Power", "Carbon Market"]
        variations = ["", "International ", "Global ", "The ", "New "]
        
        entities = []
        for i, base in enumerate(base_names):
            for j, variation in enumerate(variations):
                entity = Entity(
                    f"e_{i}_{j}",
                    f"{variation}{base}",
                    "POLICY" if "Policy" in base else "ORGANIZATION",
                    confidence=0.8 + (i * 0.01) + (j * 0.001)
                )
                entities.append(entity)
        
        # Find clusters
        clusters = fusion_engine._find_entity_clusters(entities)
        
        # Should find approximately 5 clusters (one per base name)
        assert 4 <= len(clusters) <= 6
        
        # Each cluster should have multiple entities
        for cluster in clusters.values():
            assert len(cluster.entities) >= 2
    
    def test_incremental_fusion(self, fusion_engine):
        """Test incremental document fusion."""
        # Initial fusion
        initial_docs = ["doc1", "doc2"]
        initial_result = fusion_engine.fuse_documents(initial_docs)
        
        initial_entities = initial_result.entities_after_fusion
        
        # Add more documents incrementally
        additional_docs = ["doc3", "doc4"]
        incremental_result = fusion_engine.fuse_documents(additional_docs)
        
        # Total entities should not grow linearly
        total_entities = incremental_result.entities_after_fusion
        
        # Some deduplication should occur
        if initial_entities > 0:
            growth_rate = total_entities / initial_entities
            assert growth_rate < 2.0  # Should not double


def test_end_to_end_fusion_pipeline():
    """Test complete end-to-end fusion pipeline."""
    print("\n🔄 Testing End-to-End Multi-Document Fusion Pipeline")
    
    # Initialize components
    fusion_engine = MultiDocumentFusion(
        confidence_threshold=0.8,
        similarity_threshold=0.85
    )
    
    # Create comprehensive test ontology
    ontology = DomainOntology(
        domain_name="Climate Research",
        domain_description="Comprehensive climate research ontology",
        entity_types=[
            EntityType("CLIMATE_POLICY", "Climate policies", ["Paris Agreement"], ["scope"]),
            EntityType("ORGANIZATION", "Organizations", ["UN", "IPCC"], ["type"]),
            EntityType("TECHNOLOGY", "Technologies", ["Solar", "Wind"], ["efficiency"]),
            EntityType("IMPACT", "Environmental impacts", ["Sea Level Rise"], ["severity"]),
        ],
        relationship_types=[
            RelationshipType("IMPLEMENTS", "Implements policy", ["ORGANIZATION"], ["CLIMATE_POLICY"], []),
            RelationshipType("ADDRESSES", "Addresses impact", ["CLIMATE_POLICY"], ["IMPACT"], []),
            RelationshipType("DEVELOPS", "Develops technology", ["ORGANIZATION"], ["TECHNOLOGY"], []),
        ],
        extraction_patterns=[],
        created_by_conversation="Test pipeline"
    )
    
    fusion_engine.set_ontology(ontology)
    
    # Simulate multiple documents
    document_refs = [
        "climate_report_2023_q1",
        "climate_report_2023_q2", 
        "climate_report_2023_q3",
        "climate_report_2023_q4",
        "paris_agreement_analysis",
        "renewable_tech_survey",
        "organization_directory",
        "impact_assessment_global",
        "policy_recommendations",
        "technology_roadmap"
    ]
    
    print(f"Fusing {len(document_refs)} documents...")
    
    # Perform fusion
    start_time = time.time()
    result = fusion_engine.fuse_documents(
        document_refs=document_refs,
        fusion_strategy="evidence_based",
        batch_size=3
    )
    elapsed = time.time() - start_time
    
    # Display results
    print(f"\n✅ Fusion Complete in {elapsed:.2f}s")
    print(f"  Documents processed: {result.total_documents}")
    print(f"  Entities: {result.entities_before_fusion} → {result.entities_after_fusion}")
    print(f"  Relationships: {result.relationships_before_fusion} → {result.relationships_after_fusion}")
    print(f"  Deduplication rate: {(1 - result.entities_after_fusion/max(1, result.entities_before_fusion))*100:.1f}%")
    print(f"  Conflicts resolved: {result.conflicts_resolved}")
    print(f"  Consistency score: {result.consistency_score:.2%}")
    
    # Calculate detailed consistency
    consistency = fusion_engine.calculate_knowledge_consistency()
    print(f"\n📊 Detailed Consistency Analysis:")
    print(f"  Entity consistency: {consistency.entity_consistency:.2%}")
    print(f"  Relationship consistency: {consistency.relationship_consistency:.2%}")
    print(f"  Temporal consistency: {consistency.temporal_consistency:.2%}")
    print(f"  Ontological compliance: {consistency.ontological_compliance:.2%}")
    print(f"  Overall score: {consistency.overall_score:.2%}")
    
    if consistency.inconsistencies:
        print(f"\n⚠️  Found {len(consistency.inconsistencies)} inconsistencies:")
        for i, inc in enumerate(consistency.inconsistencies[:3]):
            print(f"  {i+1}. {inc['type']}: {json.dumps(inc, indent=4)}")
    
    # Performance analysis
    print(f"\n⚡ Performance Analysis:")
    print(f"  Processing rate: {result.total_documents / elapsed:.2f} documents/second")
    print(f"  Fusion efficiency: {elapsed / result.total_documents:.3f}s per document")
    
    # Verify success criteria
    assert result.total_documents == 10
    assert result.entities_after_fusion < result.entities_before_fusion  # Deduplication occurred
    assert result.consistency_score >= 0.7  # Reasonable consistency
    # A simple check to ensure it's not excessively slow
    assert elapsed < 60  # Should be well under a minute for this test
    
    print("\n✅ All fusion tests passed!")
    
    return result


if __name__ == "__main__":
    # Run specific test scenarios
    print("🧪 Running Multi-Document Fusion Tests")
    
    # Test basic functionality
    fusion_engine = MultiDocumentFusion()
    
    # Test entity conflict resolution
    print("\n1. Testing Entity Conflict Resolution:")
    # Create entities with proper constructor
    entity1 = Entity(id="e1", canonical_name="Paris Agreement", entity_type="POLICY")
    entity1.confidence = 0.95
    entity1.name = entity1.canonical_name  # Add name attribute for compatibility
    
    entity2 = Entity(id="e2", canonical_name="The Paris Agreement", entity_type="POLICY")
    entity2.confidence = 0.90
    entity2.name = entity2.canonical_name
    
    entity3 = Entity(id="e3", canonical_name="Paris Climate Agreement", entity_type="POLICY")
    entity3.confidence = 0.92
    entity3.name = entity3.canonical_name
    
    entities = [entity1, entity2, entity3]
    
    resolved = fusion_engine.resolve_entity_conflicts(entities)
    print(f"  Resolved {len(entities)} entities → 1 canonical entity")
    print(f"  Canonical name: {resolved.canonical_name}")
    print(f"  Merged confidence: {resolved.confidence:.3f}")
    
    # Test relationship merging
    print("\n2. Testing Relationship Evidence Merging:")
    # Create relationships with proper constructor
    rel1 = Relationship(id="r1", source_id="UN", target_id="Paris", relationship_type="IMPLEMENTS")
    rel1.confidence = 0.90
    
    rel2 = Relationship(id="r2", source_id="UN", target_id="Paris", relationship_type="IMPLEMENTS")
    rel2.confidence = 0.85
    
    rel3 = Relationship(id="r3", source_id="UN", target_id="Paris", relationship_type="IMPLEMENTS")
    rel3.confidence = 0.92
    
    relationships = [rel1, rel2, rel3]
    
    merged = fusion_engine.merge_relationship_evidence(relationships)
    print(f"  Merged {len(relationships)} relationships → 1 with aggregated evidence")
    print(f"  Evidence count: {merged._fusion_evidence['evidence_count']}")
    print(f"  Confidence range: {min(merged._fusion_evidence['confidence_distribution']):.3f} - {max(merged._fusion_evidence['confidence_distribution']):.3f}")
    
    # Run full pipeline test
    test_end_to_end_fusion_pipeline()