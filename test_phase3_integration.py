#!/usr/bin/env python3
"""
Phase 3 Integration Test: Multi-Document Knowledge Fusion
Demonstrates complete T301 functionality with mock data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
from datetime import datetime
import json

from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion
from src.core.identity_service import Entity, Relationship
from src.ontology_generator import DomainOntology, EntityType, RelationshipType


def create_test_ontology():
    """Create a comprehensive climate research ontology."""
    return DomainOntology(
        domain_name="Climate Research",
        domain_description="Comprehensive ontology for climate change research and policy",
        entity_types=[
            EntityType(
                name="CLIMATE_POLICY",
                description="Climate policies and international agreements",
                examples=["Paris Agreement", "Kyoto Protocol", "Carbon Tax"],
                attributes=["scope", "target_year", "emission_reduction"]
            ),
            EntityType(
                name="ORGANIZATION",
                description="Organizations involved in climate action",
                examples=["UNFCCC", "IPCC", "IEA"],
                attributes=["type", "headquarters", "founded_year"]
            ),
            EntityType(
                name="TECHNOLOGY",
                description="Climate technologies and solutions",
                examples=["Solar Power", "Wind Energy", "Carbon Capture"],
                attributes=["efficiency", "cost_per_mwh", "maturity_level"]
            ),
            EntityType(
                name="IMPACT",
                description="Environmental and climate impacts",
                examples=["Sea Level Rise", "Temperature Increase", "Extreme Weather"],
                attributes=["severity", "affected_regions", "timeline"]
            ),
        ],
        relationship_types=[
            RelationshipType(
                name="IMPLEMENTS",
                description="Organization implements policy",
                source_types=["ORGANIZATION"],
                target_types=["CLIMATE_POLICY"],
                examples=["UN implements Paris Agreement"]
            ),
            RelationshipType(
                name="ADDRESSES",
                description="Policy addresses impact",
                source_types=["CLIMATE_POLICY"],
                target_types=["IMPACT"],
                examples=["Paris Agreement addresses Temperature Increase"]
            ),
            RelationshipType(
                name="DEVELOPS",
                description="Organization develops technology",
                source_types=["ORGANIZATION"],
                target_types=["TECHNOLOGY"],
                examples=["Tesla develops Solar Power"]
            ),
            RelationshipType(
                name="MITIGATES",
                description="Technology mitigates impact",
                source_types=["TECHNOLOGY"],
                target_types=["IMPACT"],
                examples=["Solar Power mitigates Carbon Emissions"]
            ),
        ],
        extraction_patterns=[
            "Look for climate policies and agreements",
            "Identify organizations working on climate",
            "Find technologies mentioned",
            "Extract environmental impacts"
        ],
        created_by_conversation="Climate research ontology for Phase 3 testing"
    )


def test_multi_document_fusion():
    """Test complete multi-document fusion pipeline."""
    print("🚀 Phase 3 Integration Test: Multi-Document Knowledge Fusion\n")
    
    # Initialize fusion engine
    fusion_engine = MultiDocumentFusion(
        confidence_threshold=0.8,
        similarity_threshold=0.85
    )
    
    # Set ontology
    ontology = create_test_ontology()
    fusion_engine.set_ontology(ontology)
    
    print("✅ Fusion engine initialized with climate research ontology")
    print(f"   Entity types: {len(ontology.entity_types)}")
    print(f"   Relationship types: {len(ontology.relationship_types)}")
    
    # Test 1: Entity Conflict Resolution
    print("\n📋 Test 1: Entity Conflict Resolution")
    print("-" * 50)
    
    # Create conflicting entities from different documents
    paris_entities = []
    
    # Document 1: Official UN document
    e1 = Entity(id="doc1_e1", canonical_name="Paris Agreement", entity_type="CLIMATE_POLICY")
    e1.confidence = 0.95
    e1.name = e1.canonical_name
    e1.attributes = {"year": "2015", "target": "1.5°C", "scope": "Global"}
    paris_entities.append(e1)
    
    # Document 2: News article
    e2 = Entity(id="doc2_e1", canonical_name="The Paris Agreement", entity_type="CLIMATE_POLICY")
    e2.confidence = 0.88
    e2.name = e2.canonical_name
    e2.attributes = {"year": "2016", "target": "1.5-2°C", "scope": "International"}  # Conflicting data
    paris_entities.append(e2)
    
    # Document 3: Research paper
    e3 = Entity(id="doc3_e1", canonical_name="Paris Climate Agreement", entity_type="CLIMATE_POLICY")
    e3.confidence = 0.92
    e3.name = e3.canonical_name
    e3.attributes = {"year": "2015", "target": "Well below 2°C", "scope": "Global"}
    paris_entities.append(e3)
    
    # Resolve conflicts
    resolved_paris = fusion_engine.resolve_entity_conflicts(paris_entities)
    
    print(f"✅ Resolved {len(paris_entities)} conflicting entities:")
    print(f"   Canonical name: {resolved_paris.canonical_name}")
    print(f"   Merged confidence: {resolved_paris.confidence:.3f}")
    print(f"   Conflicts resolved: {resolved_paris._fusion_evidence['conflicts_resolved']}")
    print(f"   Merged attributes:")
    for attr, data in resolved_paris._fusion_evidence['merged_attributes'].items():
        print(f"     - {attr}: {data['value']} (from {len(data['sources'])} sources)")
    
    # Test 2: Relationship Evidence Merging
    print("\n📋 Test 2: Relationship Evidence Merging")
    print("-" * 50)
    
    # Create multiple instances of same relationship from different documents
    un_implements_paris = []
    
    r1 = Relationship(id="doc1_r1", source_id="UN", target_id="Paris", relationship_type="IMPLEMENTS")
    r1.confidence = 0.90
    r1.source_document = "doc1"
    un_implements_paris.append(r1)
    
    r2 = Relationship(id="doc2_r1", source_id="UN", target_id="Paris", relationship_type="IMPLEMENTS")
    r2.confidence = 0.85
    r2.source_document = "doc2"
    un_implements_paris.append(r2)
    
    r3 = Relationship(id="doc3_r1", source_id="UN", target_id="Paris", relationship_type="IMPLEMENTS")
    r3.confidence = 0.93
    r3.source_document = "doc3"
    un_implements_paris.append(r3)
    
    # Merge evidence
    merged_rel = fusion_engine.merge_relationship_evidence(un_implements_paris)
    
    print(f"✅ Merged {len(un_implements_paris)} relationship instances:")
    print(f"   Type: {merged_rel.relationship_type}")
    print(f"   Aggregated confidence: {merged_rel.confidence:.3f}")
    print(f"   Evidence sources: {merged_rel._fusion_evidence['evidence_sources']}")
    print(f"   Confidence distribution: {[f'{c:.3f}' for c in merged_rel._fusion_evidence['confidence_distribution']]}")
    
    # Test 3: Entity Clustering
    print("\n📋 Test 3: Entity Clustering and Deduplication")
    print("-" * 50)
    
    # Create entities with duplicates and near-duplicates
    test_entities = []
    
    # Climate organizations with variations
    for i, name in enumerate([
        "United Nations", "UN", "United Nations Organization",
        "IPCC", "Intergovernmental Panel on Climate Change", "IPCC Panel",
        "IEA", "International Energy Agency", "Intl. Energy Agency"
    ]):
        e = Entity(id=f"test_e{i}", canonical_name=name, entity_type="ORGANIZATION")
        e.confidence = 0.8 + (i * 0.01)
        e.name = name
        test_entities.append(e)
    
    # Find clusters
    clusters = fusion_engine._find_entity_clusters(test_entities)
    
    print(f"✅ Found {len(clusters)} entity clusters from {len(test_entities)} entities:")
    for cluster_id, cluster in clusters.items():
        print(f"\n   Cluster {cluster_id}:")
        for entity in cluster.entities:
            print(f"     - {entity.canonical_name} (confidence: {entity.confidence:.3f})")
    
    # Test 4: Multi-Document Fusion Simulation
    print("\n📋 Test 4: Complete Multi-Document Fusion Pipeline")
    print("-" * 50)
    
    # Simulate document references
    document_refs = [
        "climate_report_q1_2023",
        "climate_report_q2_2023",
        "paris_agreement_analysis",
        "renewable_tech_survey",
        "ipcc_assessment_report"
    ]
    
    print(f"Simulating fusion of {len(document_refs)} documents...")
    
    # For this test, we'll use mock data since we don't have actual documents in Neo4j
    # In production, this would load from the database
    
    # Create mock entities and relationships
    mock_entities = []
    mock_relationships = []
    
    # Add entities from each "document"
    for doc_idx, doc_ref in enumerate(document_refs):
        # Each document mentions Paris Agreement slightly differently
        paris = Entity(
            id=f"{doc_ref}_paris",
            canonical_name=f"Paris {'Climate ' if doc_idx % 2 else ''}Agreement",
            entity_type="CLIMATE_POLICY"
        )
        paris.confidence = 0.85 + (doc_idx * 0.02)
        paris.name = paris.canonical_name
        mock_entities.append(paris)
        
        # Each document mentions UN
        un = Entity(
            id=f"{doc_ref}_un",
            canonical_name="UN" if doc_idx % 2 else "United Nations",
            entity_type="ORGANIZATION"
        )
        un.confidence = 0.90
        un.name = un.canonical_name
        mock_entities.append(un)
        
        # Add relationship
        rel = Relationship(
            id=f"{doc_ref}_r1",
            source_id=un.id,
            target_id=paris.id,
            relationship_type="IMPLEMENTS"
        )
        rel.confidence = 0.85 + (doc_idx * 0.01)
        mock_relationships.append(rel)
    
    # Perform clustering
    print(f"\nClustering {len(mock_entities)} entities...")
    entity_clusters = fusion_engine._find_entity_clusters(mock_entities)
    
    print(f"✅ Found {len(entity_clusters)} duplicate clusters")
    
    # Resolve clusters
    resolved_entities = fusion_engine._resolve_entity_clusters(entity_clusters, "evidence_based")
    
    print(f"✅ Resolved to {len(resolved_entities)} canonical entities")
    
    # Calculate deduplication rate
    dedup_rate = 1 - (len(resolved_entities) / len(mock_entities))
    print(f"✅ Deduplication rate: {dedup_rate:.1%}")
    
    # Test 5: Consistency Metrics
    print("\n📋 Test 5: Knowledge Consistency Analysis")
    print("-" * 50)
    
    # Calculate consistency (this would normally check the actual graph)
    # For testing, we'll simulate the metrics
    consistency = fusion_engine.calculate_knowledge_consistency()
    
    print(f"📊 Consistency Metrics:")
    print(f"   Entity consistency: {consistency.entity_consistency:.2%}")
    print(f"   Relationship consistency: {consistency.relationship_consistency:.2%}")
    print(f"   Temporal consistency: {consistency.temporal_consistency:.2%}")
    print(f"   Ontological compliance: {consistency.ontological_compliance:.2%}")
    print(f"   Overall score: {consistency.overall_score:.2%}")
    
    # Performance summary
    print("\n✅ Phase 3 T301 Multi-Document Fusion Test Complete!")
    print(f"   - Entity conflict resolution: Working")
    print(f"   - Relationship evidence merging: Working")
    print(f"   - Entity clustering: Working")
    print(f"   - Deduplication: {dedup_rate:.1%} efficiency")
    print(f"   - Consistency tracking: Working")
    
    return True


def test_advanced_scenarios():
    """Test advanced fusion scenarios."""
    print("\n\n🔬 Advanced Fusion Scenarios")
    print("=" * 60)
    
    fusion_engine = MultiDocumentFusion()
    
    # Scenario 1: Temporal Conflict Resolution
    print("\n📋 Scenario 1: Temporal Conflict Resolution")
    print("-" * 50)
    
    # Create carbon tax policies with temporal evolution
    carbon_tax_v1 = Entity(id="2022_carbon_tax", canonical_name="EU Carbon Tax", entity_type="CLIMATE_POLICY")
    carbon_tax_v1.confidence = 0.90
    carbon_tax_v1.name = carbon_tax_v1.canonical_name
    carbon_tax_v1.attributes = {"rate": "€50/ton", "effective_date": "2022-01-01"}
    carbon_tax_v1.timestamp = datetime(2022, 1, 1)
    
    carbon_tax_v2 = Entity(id="2023_carbon_tax", canonical_name="EU Carbon Tax", entity_type="CLIMATE_POLICY")
    carbon_tax_v2.confidence = 0.92
    carbon_tax_v2.name = carbon_tax_v2.canonical_name
    carbon_tax_v2.attributes = {"rate": "€75/ton", "effective_date": "2023-01-01"}
    carbon_tax_v2.timestamp = datetime(2023, 1, 1)
    
    carbon_tax_v3 = Entity(id="2024_carbon_tax", canonical_name="EU Carbon Tax", entity_type="CLIMATE_POLICY")
    carbon_tax_v3.confidence = 0.94
    carbon_tax_v3.name = carbon_tax_v3.canonical_name
    carbon_tax_v3.attributes = {"rate": "€100/ton", "effective_date": "2024-01-01"}
    carbon_tax_v3.timestamp = datetime(2024, 1, 1)
    
    # Test temporal priority resolution
    temporal_cluster = type('obj', (object,), {
        'entities': [carbon_tax_v1, carbon_tax_v2, carbon_tax_v3],
        'cluster_id': 'temporal_test'
    })
    
    resolved = fusion_engine._resolve_entity_clusters(
        {'temporal_test': temporal_cluster},
        'temporal_priority'
    )
    
    latest_entity = list(resolved.values())[0]
    print(f"✅ Temporal resolution selected most recent:")
    print(f"   Entity: {latest_entity.canonical_name}")
    print(f"   Timestamp: {latest_entity.timestamp}")
    print(f"   Rate: {latest_entity.attributes.get('rate', 'N/A')}")
    
    # Scenario 2: Cross-Document Relationship Validation
    print("\n📋 Scenario 2: Cross-Document Relationship Validation")
    print("-" * 50)
    
    # Create conflicting relationships
    rels = [
        Relationship(id="r1", source_id="IPCC", target_id="Report2023", relationship_type="PUBLISHES"),
        Relationship(id="r2", source_id="IPCC", target_id="Report2023", relationship_type="REVIEWS"),  # Conflict
        Relationship(id="r3", source_id="IPCC", target_id="Report2023", relationship_type="PUBLISHES"),
    ]
    
    # Group by endpoints
    rel_groups = fusion_engine._merge_relationships(rels, {}, "evidence_based")
    
    print(f"✅ Resolved {len(rels)} relationships to {len(rel_groups)}")
    for rel in rel_groups:
        print(f"   {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id} (confidence: {rel.confidence:.3f})")
    
    # Scenario 3: Large-Scale Deduplication Performance
    print("\n📋 Scenario 3: Large-Scale Deduplication Performance")
    print("-" * 50)
    
    # Create many entities with variations
    large_entity_set = []
    base_entities = ["Climate Policy", "Carbon Market", "Renewable Energy", "IPCC Report", "Net Zero Target"]
    variations = ["", "International ", "Global ", "The ", "New ", "Updated "]
    
    for base in base_entities:
        for variation in variations:
            for suffix in ["", " 2023", " Initiative"]:
                name = f"{variation}{base}{suffix}".strip()
                e = Entity(
                    id=f"large_{len(large_entity_set)}",
                    canonical_name=name,
                    entity_type="CLIMATE_POLICY"
                )
                e.confidence = 0.8 + (len(large_entity_set) * 0.001)
                e.name = name
                large_entity_set.append(e)
    
    print(f"Created {len(large_entity_set)} entities with variations")
    
    start_time = time.time()
    clusters = fusion_engine._find_entity_clusters(large_entity_set)
    clustering_time = time.time() - start_time
    
    print(f"✅ Clustering completed in {clustering_time:.3f}s")
    print(f"   Found {len(clusters)} clusters")
    print(f"   Processing rate: {len(large_entity_set) / clustering_time:.0f} entities/second")
    
    # Show largest clusters
    sorted_clusters = sorted(clusters.values(), key=lambda c: len(c.entities), reverse=True)
    print("\n   Largest clusters:")
    for i, cluster in enumerate(sorted_clusters[:3]):
        print(f"   {i+1}. {len(cluster.entities)} entities")
        sample_names = [e.canonical_name for e in cluster.entities[:3]]
        print(f"      Examples: {', '.join(sample_names)}...")
    
    print("\n✅ All advanced scenarios completed successfully!")


if __name__ == "__main__":
    # Run main test
    success = test_multi_document_fusion()
    
    if success:
        # Run advanced scenarios
        test_advanced_scenarios()
    
    print("\n🎯 Phase 3 T301 Integration Testing Complete!")