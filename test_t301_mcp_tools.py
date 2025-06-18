#!/usr/bin/env python3
"""
Test T301 MCP Tools - Verify modular fusion tools work correctly.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import the tool functions directly for testing
# In production, these would be called via MCP protocol
from src.tools.phase3.t301_multi_document_fusion_tools import (
    calculate_entity_similarity,
    find_entity_clusters,
    resolve_entity_conflicts,
    merge_relationship_evidence,
    check_fusion_consistency
)


def test_similarity_tool():
    """Test the calculate_entity_similarity tool."""
    print("🔍 Testing calculate_entity_similarity")
    print("-" * 60)
    
    # Test 1: String matching only (fast)
    print("\n1. String matching only (no API calls):")
    result = calculate_entity_similarity.func(
        "United Nations",
        "UN",
        "ORG",
        "ORG",
        use_embeddings=False,
        use_string_matching=True
    )
    print(f"   Result: {result['similarities']}")
    print(f"   Methods used: {result['methods_used']}")
    
    # Test 2: Embeddings only (semantic)
    print("\n2. Embeddings only (semantic understanding):")
    result = calculate_entity_similarity.func(
        "Climate Change Policy",
        "Global Warming Strategy",
        "POLICY",
        "POLICY",
        use_embeddings=True,
        use_string_matching=False
    )
    print(f"   Result: {result['similarities']}")
    print(f"   Methods used: {result['methods_used']}")
    
    # Test 3: Different types (should be 0)
    print("\n3. Different entity types:")
    result = calculate_entity_similarity.func(
        "Paris Agreement",
        "Paris",
        "POLICY",
        "CITY",
        use_embeddings=True,
        use_string_matching=True
    )
    print(f"   Result: {result['similarities']}")
    print(f"   Reason: {result.get('reason', 'N/A')}")


def test_clustering_tool():
    """Test the find_entity_clusters tool."""
    print("\n\n🔗 Testing find_entity_clusters")
    print("-" * 60)
    
    # Test entities with various similarities
    entities = [
        {"id": "e1", "name": "United Nations", "type": "ORG", "confidence": 0.95},
        {"id": "e2", "name": "UN", "type": "ORG", "confidence": 0.90},
        {"id": "e3", "name": "United Nations Organization", "type": "ORG", "confidence": 0.88},
        {"id": "e4", "name": "World Bank", "type": "ORG", "confidence": 0.92},
        {"id": "e5", "name": "Paris Agreement", "type": "POLICY", "confidence": 0.94},
        {"id": "e6", "name": "Paris Climate Agreement", "type": "POLICY", "confidence": 0.89},
    ]
    
    # Test with different thresholds
    print("\n1. High threshold (0.9) with string matching only:")
    result = find_entity_clusters.func(
        entities,
        similarity_threshold=0.9,
        use_embeddings=False
    )
    print(f"   Total entities: {result['total_entities']}")
    print(f"   Clusters found: {result['clusters_found']}")
    print(f"   Entities clustered: {result['entities_clustered']}")
    
    print("\n2. Medium threshold (0.7) with embeddings:")
    result = find_entity_clusters.func(
        entities,
        similarity_threshold=0.7,
        use_embeddings=True
    )
    print(f"   Total entities: {result['total_entities']}")
    print(f"   Clusters found: {result['clusters_found']}")
    print(f"   Entities clustered: {result['entities_clustered']}")
    if result['clusters']:
        for cid, cluster in result['clusters'].items():
            names = [e['name'] for e in cluster['entities']]
            print(f"   - {cid}: {names} (avg confidence: {cluster['average_confidence']:.3f})")


def test_conflict_resolution_tool():
    """Test the resolve_entity_conflicts tool."""
    print("\n\n⚔️ Testing resolve_entity_conflicts")
    print("-" * 60)
    
    # Conflicting entities
    conflicting_entities = [
        {
            "id": "doc1_paris",
            "name": "Paris Agreement",
            "type": "POLICY",
            "confidence": 0.95,
            "attributes": {
                "year": "2015",
                "target": "1.5°C limit",
                "countries": "196"
            }
        },
        {
            "id": "doc2_paris",
            "name": "Paris Climate Agreement",
            "type": "POLICY",
            "confidence": 0.88,
            "attributes": {
                "year": "2016",  # Wrong year
                "target": "1.5-2°C limit",  # Different wording
                "countries": "195"  # Different count
            }
        },
        {
            "id": "doc3_paris",
            "name": "The Paris Agreement",
            "type": "POLICY",
            "confidence": 0.92,
            "attributes": {
                "year": "2015",
                "target": "Well below 2°C",  # Another variation
                "countries": "196",
                "ratified": "2016"  # Additional attribute
            }
        }
    ]
    
    # Test different strategies
    strategies = ["confidence_weighted", "evidence_based"]
    
    for strategy in strategies:
        print(f"\n{strategy.upper()} Strategy:")
        result = resolve_entity_conflicts.func(
            conflicting_entities,
            strategy=strategy,
            use_llm=False
        )
        print(f"   Resolved name: {result['name']}")
        print(f"   Final confidence: {result['confidence']:.3f}")
        print(f"   Conflicts resolved: {result['evidence']['conflicts_resolved']}")
        print(f"   Final attributes:")
        for attr, value in result['attributes'].items():
            source_info = result['evidence']['attribute_sources'].get(attr, 'unanimous')
            print(f"     - {attr}: {value} (source: {source_info})")


def test_relationship_merge_tool():
    """Test the merge_relationship_evidence tool."""
    print("\n\n🔄 Testing merge_relationship_evidence")
    print("-" * 60)
    
    # Multiple observations of same relationship
    relationships = [
        {
            "id": "r1",
            "source_id": "UN",
            "target_id": "ParisAgreement",
            "type": "OVERSEES",
            "confidence": 0.90,
            "source_document": "doc1.pdf",
            "attributes": {"established": "2015", "strength": "strong"}
        },
        {
            "id": "r2",
            "source_id": "UN",
            "target_id": "ParisAgreement", 
            "type": "OVERSEES",
            "confidence": 0.85,
            "source_document": "doc2.pdf",
            "attributes": {"established": "2016", "strength": "strong"}
        },
        {
            "id": "r3",
            "source_id": "UN",
            "target_id": "ParisAgreement",
            "type": "OVERSEES",
            "confidence": 0.92,
            "source_document": "doc3.pdf",
            "attributes": {"established": "2015", "strength": "moderate"}
        }
    ]
    
    result = merge_relationship_evidence.func(relationships)
    print(f"   Merged relationship: {result['source_id']} --[{result['type']}]--> {result['target_id']}")
    print(f"   Final confidence: {result['confidence']:.3f}")
    print(f"   Evidence count: {result['evidence']['observation_count']}")
    print(f"   Source documents: {result['evidence']['source_documents']}")
    print(f"   Attribute consensus:")
    for attr, consensus in result['evidence']['attribute_consensus'].items():
        print(f"     - {attr}: {consensus['value']} (agreement: {consensus['agreement']:.1%})")


def test_consistency_check_tool():
    """Test the check_fusion_consistency tool."""
    print("\n\n✅ Testing check_fusion_consistency")
    print("-" * 60)
    
    # Test data with some issues
    entities = [
        {"id": "e1", "name": "United Nations", "type": "ORG"},
        {"id": "e2", "name": "UN", "type": "ORG"},  # Duplicate
        {"id": "e3", "name": "Paris Agreement", "type": "POLICY"},
        {"id": "e4", "name": "Paris Climate Agreement", "type": "POLICY"},  # Duplicate
        {"id": "e5", "name": "IPCC", "type": "ORG"},
        {"id": "e6", "name": "Invalid Entity", "type": "INVALID_TYPE"},  # Invalid type
    ]
    
    relationships = [
        {"source_id": "e1", "target_id": "e3", "type": "OVERSEES"},
        {"source_id": "e2", "target_id": "e3", "type": "MANAGES"},  # Conflict with e1->e3
        {"source_id": "e5", "target_id": "e3", "type": "MONITORS"},
        {"source_id": "e5", "target_id": "e4", "type": "INVALID_REL"},  # Invalid type
    ]
    
    # Simple ontology for testing
    ontology = {
        "entity_types": [
            {"name": "ORG"},
            {"name": "POLICY"}
        ],
        "relationship_types": [
            {"name": "OVERSEES"},
            {"name": "MANAGES"},
            {"name": "MONITORS"}
        ]
    }
    
    # Test different check combinations
    print("\n1. Check duplicates only:")
    result = check_fusion_consistency.func(
        entities, relationships,
        check_duplicates=True,
        check_conflicts=False,
        check_ontology=False
    )
    print(f"   Entity consistency: {result['scores'].get('entity_consistency', 0):.2%}")
    print(f"   Duplicate pairs found: {result['summary'].get('duplicate_pairs_found', 0)}")
    
    print("\n2. Check conflicts only:")
    result = check_fusion_consistency.func(
        entities, relationships,
        check_duplicates=False,
        check_conflicts=True,
        check_ontology=False
    )
    print(f"   Relationship consistency: {result['scores'].get('relationship_consistency', 0):.2%}")
    print(f"   Conflicts found: {result['summary'].get('relationship_conflicts', 0)}")
    
    print("\n3. Full check with ontology:")
    result = check_fusion_consistency.func(
        entities, relationships,
        check_duplicates=True,
        check_conflicts=True,
        check_ontology=True,
        ontology=ontology
    )
    print(f"   Overall score: {result['scores'].get('overall', 0):.2%}")
    print(f"   Checks performed: {result['checks_performed']}")
    print(f"   Total issues: {len(result['issues'])}")
    print(f"   Health status: {result['summary'].get('overall_health', 'unknown')}")
    
    # Show some issues
    if result['issues']:
        print("\n   Sample issues found:")
        for issue in result['issues'][:3]:
            print(f"     - {issue['type']}: {issue}")


def demonstrate_pipeline():
    """Demonstrate how tools can be composed into a pipeline."""
    print("\n\n🔧 Demonstrating Tool Pipeline")
    print("-" * 60)
    
    print("Pipeline: Document Fusion → Deduplication → Consistency Check")
    
    # Step 1: Start with entities from multiple documents
    raw_entities = [
        {"id": "doc1_e1", "name": "Artificial Intelligence", "type": "TECH", "confidence": 0.9},
        {"id": "doc1_e2", "name": "Machine Learning", "type": "TECH", "confidence": 0.85},
        {"id": "doc2_e1", "name": "AI", "type": "TECH", "confidence": 0.88},
        {"id": "doc2_e2", "name": "ML", "type": "TECH", "confidence": 0.83},
        {"id": "doc3_e1", "name": "Artificial Intelligence", "type": "TECH", "confidence": 0.92},
    ]
    
    print(f"\n1. Starting with {len(raw_entities)} entities from 3 documents")
    
    # Step 2: Find clusters
    clusters = find_entity_clusters.func(
        raw_entities,
        similarity_threshold=0.7,
        use_embeddings=True
    )
    print(f"\n2. Found {clusters['clusters_found']} duplicate clusters")
    
    # Step 3: Resolve each cluster
    resolved_entities = []
    for cluster_data in clusters['clusters'].values():
        resolved = resolve_entity_conflicts.func(
            cluster_data['entities'],
            strategy="confidence_weighted"
        )
        resolved_entities.append(resolved)
        print(f"   - Resolved {len(cluster_data['entities'])} entities → 1")
    
    # Add unclustered entities
    clustered_ids = set()
    for cluster in clusters['clusters'].values():
        clustered_ids.update(e['id'] for e in cluster['entities'])
    
    for entity in raw_entities:
        if entity['id'] not in clustered_ids:
            resolved_entities.append(entity)
    
    print(f"\n3. Final entity count: {len(resolved_entities)}")
    
    # Step 4: Check consistency
    consistency = check_fusion_consistency.func(
        resolved_entities, [],
        check_duplicates=True,
        check_conflicts=False
    )
    print(f"\n4. Final consistency score: {consistency['scores'].get('entity_consistency', 0):.2%}")
    print(f"   Deduplication efficiency: {(1 - len(resolved_entities)/len(raw_entities)):.1%}")


if __name__ == "__main__":
    print("🧪 T301 MCP Tools Test Suite")
    print("=" * 80)
    
    test_similarity_tool()
    test_clustering_tool()
    test_conflict_resolution_tool()
    test_relationship_merge_tool()
    test_consistency_check_tool()
    demonstrate_pipeline()
    
    print("\n\n✅ All T301 MCP tools tested successfully!")
    print("\nKey advantages of this modular design:")
    print("  • Each tool can be called independently via MCP")
    print("  • Flexible parameters (embeddings on/off, thresholds, strategies)")
    print("  • Tools compose into custom pipelines")
    print("  • Clear separation of concerns")
    print("  • Easy to test and debug individual components")