#!/usr/bin/env python3
"""
Test T301 as modular MCP tools with flexibility.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.phase3.t301_mcp_tools import (
    calculate_entity_similarity,
    find_entity_clusters,
    resolve_entity_conflicts,
    merge_relationship_evidence,
    calculate_fusion_consistency
)


def test_modular_approach():
    """Demonstrate the flexibility of modular MCP tools."""
    print("🧩 T301 Modular MCP Tools Test")
    print("="*60)
    
    # Test 1: Similarity with different methods
    print("\n1. Entity Similarity - Choose Your Method:")
    print("-"*50)
    
    test_pairs = [
        ("Paris Agreement", "Paris Climate Agreement"),
        ("United Nations", "UN"),
        ("Climate Policy", "Energy Policy"),
    ]
    
    for name1, name2 in test_pairs:
        print(f"\nComparing: '{name1}' vs '{name2}'")
        
        # String matching only
        result1 = calculate_entity_similarity(
            name1, name2, "POLICY", "POLICY",
            use_embeddings=False,
            use_string_matching=True
        )
        print(f"  String only: {result1['similarities']}")
        
        # Embeddings only
        result2 = calculate_entity_similarity(
            name1, name2, "POLICY", "POLICY",
            use_embeddings=True,
            use_string_matching=False
        )
        print(f"  Embeddings only: {result2['similarities']}")
        
        # Both methods
        result3 = calculate_entity_similarity(
            name1, name2, "POLICY", "POLICY",
            use_embeddings=True,
            use_string_matching=True
        )
        print(f"  Combined: {result3['similarities']}")
    
    # Test 2: Clustering with control
    print("\n\n2. Entity Clustering - Control the Threshold:")
    print("-"*50)
    
    entities = [
        {"id": "e1", "name": "Climate Change Policy", "type": "POLICY", "confidence": 0.9},
        {"id": "e2", "name": "Climate Policy", "type": "POLICY", "confidence": 0.85},
        {"id": "e3", "name": "Environmental Policy", "type": "POLICY", "confidence": 0.8},
        {"id": "e4", "name": "UN Climate Agreement", "type": "POLICY", "confidence": 0.95},
        {"id": "e5", "name": "United Nations", "type": "ORG", "confidence": 0.9},
        {"id": "e6", "name": "UN", "type": "ORG", "confidence": 0.88},
    ]
    
    # High threshold - only very similar
    clusters_high = find_entity_clusters(entities, similarity_threshold=0.9, use_embeddings=False)
    print(f"\nHigh threshold (0.9): {clusters_high['clusters_found']} clusters")
    
    # Medium threshold
    clusters_med = find_entity_clusters(entities, similarity_threshold=0.7, use_embeddings=False)
    print(f"Medium threshold (0.7): {clusters_med['clusters_found']} clusters")
    
    # Low threshold - more aggressive clustering
    clusters_low = find_entity_clusters(entities, similarity_threshold=0.5, use_embeddings=False)
    print(f"Low threshold (0.5): {clusters_low['clusters_found']} clusters")
    
    # Test 3: Conflict resolution strategies
    print("\n\n3. Conflict Resolution - Choose Your Strategy:")
    print("-"*50)
    
    conflicting_entities = [
        {
            "id": "doc1_paris",
            "name": "Paris Agreement",
            "type": "POLICY",
            "confidence": 0.95,
            "attributes": {"year": "2015", "target": "1.5°C", "scope": "Global"}
        },
        {
            "id": "doc2_paris",
            "name": "Paris Climate Agreement",
            "type": "POLICY", 
            "confidence": 0.88,
            "attributes": {"year": "2016", "target": "1.5-2°C", "scope": "International"}
        },
        {
            "id": "doc3_paris",
            "name": "The Paris Agreement",
            "type": "POLICY",
            "confidence": 0.92,
            "attributes": {"year": "2015", "target": "Well below 2°C", "scope": "Global"}
        }
    ]
    
    # Try different strategies
    strategies = ["confidence_weighted", "temporal_priority", "evidence_based"]
    
    for strategy in strategies:
        result = resolve_entity_conflicts(conflicting_entities, strategy=strategy)
        print(f"\nStrategy: {strategy}")
        print(f"  Resolved name: {result['name']}")
        print(f"  Final confidence: {result['confidence']:.3f}")
        print(f"  Attributes: {result['attributes']}")
        print(f"  Conflicts resolved: {result['evidence']['conflicts_resolved']}")
    
    # Test 4: Consistency checking options
    print("\n\n4. Consistency Checking - Pick Your Checks:")
    print("-"*50)
    
    # Some test data with issues
    test_entities = [
        {"id": "e1", "name": "Paris Agreement", "type": "POLICY"},
        {"id": "e2", "name": "Paris Climate Agreement", "type": "POLICY"},  # Duplicate
        {"id": "e3", "name": "IPCC", "type": "ORG"},
    ]
    
    test_relationships = [
        {"source_id": "e3", "target_id": "e1", "type": "IMPLEMENTS"},
        {"source_id": "e3", "target_id": "e1", "type": "MONITORS"},  # Conflict
    ]
    
    # Check only duplicates
    result1 = calculate_fusion_consistency(
        test_entities, test_relationships,
        check_duplicates=True,
        check_conflicts=False
    )
    print("\nChecking duplicates only:")
    print(f"  Issues found: {len(result1['issues'])}")
    print(f"  Entity consistency: {result1['scores'].get('entity_consistency', 'N/A')}")
    
    # Check only conflicts
    result2 = calculate_fusion_consistency(
        test_entities, test_relationships,
        check_duplicates=False,
        check_conflicts=True
    )
    print("\nChecking conflicts only:")
    print(f"  Issues found: {len(result2['issues'])}")
    print(f"  Relationship consistency: {result2['scores'].get('relationship_consistency', 'N/A')}")
    
    # Check everything
    result3 = calculate_fusion_consistency(
        test_entities, test_relationships,
        check_duplicates=True,
        check_conflicts=True
    )
    print("\nChecking everything:")
    print(f"  Issues found: {len(result3['issues'])}")
    print(f"  Overall score: {result3['scores'].get('overall', 'N/A'):.3f}")
    
    print("\n\n✅ Benefits of Modular MCP Tools:")
    print("  1. Use only what you need (e.g., skip expensive embeddings)")
    print("  2. Configure each tool independently") 
    print("  3. Chain tools in custom pipelines")
    print("  4. Test individual components easily")
    print("  5. Different strategies for different use cases")


if __name__ == "__main__":
    test_modular_approach()