#!/usr/bin/env python3
"""
REAL test of T301 - what does it actually do?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion
from src.core.identity_service import Entity, Relationship

def test_what_t301_actually_does():
    """Test the actual functionality, not made-up metrics."""
    print("🔍 REAL T301 Test - What Actually Happens")
    print("="*60)
    
    fusion_engine = MultiDocumentFusion()
    
    # Create realistic entities from "different documents"
    print("\n1. Creating entities from 3 'documents' about climate change:")
    
    # Document 1 entities
    doc1_entities = [
        Entity(id="d1_e1", canonical_name="Paris Agreement", entity_type="POLICY"),
        Entity(id="d1_e2", canonical_name="United Nations", entity_type="ORG"),
        Entity(id="d1_e3", canonical_name="1.5 degrees", entity_type="TARGET"),
    ]
    
    # Document 2 entities (some overlap)
    doc2_entities = [
        Entity(id="d2_e1", canonical_name="Paris Climate Agreement", entity_type="POLICY"),  # Same as d1_e1
        Entity(id="d2_e2", canonical_name="UN", entity_type="ORG"),  # Same as d1_e2
        Entity(id="d2_e3", canonical_name="Net Zero 2050", entity_type="TARGET"),  # New
    ]
    
    # Document 3 entities (more overlap)
    doc3_entities = [
        Entity(id="d3_e1", canonical_name="The Paris Agreement", entity_type="POLICY"),  # Same as d1_e1
        Entity(id="d3_e2", canonical_name="IPCC", entity_type="ORG"),  # New
        Entity(id="d3_e3", canonical_name="1.5°C target", entity_type="TARGET"),  # Same as d1_e3
    ]
    
    # Set confidence and name attributes
    all_entities = doc1_entities + doc2_entities + doc3_entities
    for i, e in enumerate(all_entities):
        e.confidence = 0.8 + (i * 0.02)  # Varying confidence
        e.name = e.canonical_name
    
    print(f"   Total entities: {len(all_entities)}")
    for e in all_entities:
        print(f"   - {e.id}: '{e.canonical_name}' (type: {e.entity_type})")
    
    # Test clustering
    print("\n2. Finding entity clusters (duplicates):")
    clusters = fusion_engine._find_entity_clusters(all_entities)
    
    print(f"   Found {len(clusters)} clusters")
    for cluster_id, cluster in clusters.items():
        print(f"\n   Cluster: {cluster_id}")
        for e in cluster.entities:
            print(f"     - {e.id}: '{e.canonical_name}'")
    
    # Test conflict resolution
    print("\n3. Testing conflict resolution:")
    if clusters:
        first_cluster = list(clusters.values())[0]
        if len(first_cluster.entities) > 1:
            # Add conflicting attributes to test resolution
            first_cluster.entities[0].attributes = {"year": "2015", "target": "1.5°C"}
            first_cluster.entities[1].attributes = {"year": "2016", "target": "1.5-2°C"}  # Conflict!
            
            resolved = fusion_engine.resolve_entity_conflicts(first_cluster.entities)
            print(f"   Resolved {len(first_cluster.entities)} entities to: '{resolved.canonical_name}'")
            print(f"   Confidence: {resolved.confidence:.3f}")
            if hasattr(resolved, '_fusion_evidence'):
                print(f"   Evidence: {resolved._fusion_evidence}")
    
    # Test actual fusion method
    print("\n4. Testing fuse_documents (mock):")
    try:
        # This will fail because we don't have actual documents in Neo4j
        result = fusion_engine.fuse_documents(["doc1", "doc2", "doc3"])
    except Exception as e:
        print(f"   Expected failure (no Neo4j data): {type(e).__name__}")
    
    # What does similarity calculation actually do?
    print("\n5. Testing similarity calculation:")
    test_pairs = [
        ("Paris Agreement", "Paris Climate Agreement"),
        ("United Nations", "UN"),
        ("1.5 degrees", "1.5°C target"),
        ("Climate Policy", "Energy Policy"),
        ("IPCC", "United Nations"),
    ]
    
    for name1, name2 in test_pairs:
        e1 = Entity(id="test1", canonical_name=name1, entity_type="TEST")
        e2 = Entity(id="test2", canonical_name=name2, entity_type="TEST")
        e1.name = name1
        e2.name = name2
        
        similarity = fusion_engine._calculate_entity_similarity(e1, e2)
        print(f"   '{name1}' vs '{name2}': {similarity:.3f}")
    
    print("\n6. What T301 ACTUALLY does:")
    print("   ✓ Groups entities by exact/substring name matching")
    print("   ✓ Averages confidence scores")
    print("   ✓ Keeps track of source entities")
    print("   ✓ Basic attribute merging (highest confidence wins)")
    print("   ✗ NO actual LLM calls for conflict resolution")
    print("   ✗ NO semantic understanding (just string matching)")
    print("   ✗ NO real document loading from storage")
    print("   ✗ NO temporal analysis")
    print("   ✗ NO advanced reasoning")


if __name__ == "__main__":
    test_what_t301_actually_does()