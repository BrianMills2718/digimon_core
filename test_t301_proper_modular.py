#!/usr/bin/env python3
"""
Test T301 proper modular design - separate tools for flexibility.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.phase3.t301_fusion_tools import (
    entity_similarity,
    cluster_finder,
    conflict_resolver,
    relationship_merger,
    consistency_checker
)


def test_proper_modular_design():
    """Show how T301 should be designed as separate, flexible tools."""
    print("🔧 T301 Proper Modular Design Test")
    print("="*60)
    
    # Test 1: Control similarity methods independently
    print("\n1. Flexible Similarity Calculation:")
    print("-"*50)
    
    # Case 1: Fast string-only matching for initial screening
    print("\nCase 1: Fast string matching (no API calls):")
    result = entity_similarity.calculate(
        "United Nations Framework Convention on Climate Change",
        "UNFCCC",
        "ORG", "ORG",
        use_embeddings=False,  # Skip expensive API call
        use_string_matching=True
    )
    print(f"  Result: {result['similarities']}")
    
    # Case 2: Precise embedding similarity for final decisions
    print("\nCase 2: Precise embedding similarity:")
    result = entity_similarity.calculate(
        "Climate Policy",
        "Environmental Policy",
        "POLICY", "POLICY",
        use_embeddings=True,  # Use embeddings for semantic similarity
        use_string_matching=False
    )
    print(f"  Result: {result['similarities']}")
    
    # Case 3: Combined for best of both worlds
    print("\nCase 3: Combined approach:")
    result = entity_similarity.calculate(
        "Paris Agreement",
        "Paris Climate Accord",
        "POLICY", "POLICY",
        use_embeddings=True,
        use_string_matching=True
    )
    print(f"  Result: {result['similarities']}")
    
    # Test 2: Clustering with different thresholds for different use cases
    print("\n\n2. Flexible Clustering:")
    print("-"*50)
    
    entities = [
        {"id": "1", "name": "Artificial Intelligence", "type": "TECH", "confidence": 0.9},
        {"id": "2", "name": "AI", "type": "TECH", "confidence": 0.85},
        {"id": "3", "name": "Machine Learning", "type": "TECH", "confidence": 0.88},
        {"id": "4", "name": "ML", "type": "TECH", "confidence": 0.82},
        {"id": "5", "name": "Deep Learning", "type": "TECH", "confidence": 0.87},
        {"id": "6", "name": "Neural Networks", "type": "TECH", "confidence": 0.86},
    ]
    
    # Conservative clustering - only obvious duplicates
    print("\nConservative (threshold=0.9, no embeddings):")
    result = cluster_finder.find_clusters(
        entities, 
        similarity_threshold=0.9,
        use_embeddings=False  # Fast, string-based only
    )
    print(f"  Found {result['clusters_found']} clusters")
    for cid, cluster in result['clusters'].items():
        names = [e['name'] for e in cluster['entities']]
        print(f"  - {cid}: {names}")
    
    # Aggressive clustering - find related concepts
    print("\nAggressive (threshold=0.6, with embeddings):")
    result = cluster_finder.find_clusters(
        entities,
        similarity_threshold=0.6,
        use_embeddings=True  # Use semantic understanding
    )
    print(f"  Found {result['clusters_found']} clusters")
    for cid, cluster in result['clusters'].items():
        names = [e['name'] for e in cluster['entities']]
        print(f"  - {cid}: {names}")
    
    # Test 3: Different conflict resolution strategies
    print("\n\n3. Flexible Conflict Resolution:")
    print("-"*50)
    
    conflicting_data = [
        {
            "id": "source1",
            "name": "CO2 Emissions Target",
            "type": "TARGET",
            "confidence": 0.95,
            "attributes": {
                "value": "50% reduction by 2030",
                "baseline": "1990 levels",
                "source": "Government Report 2023"
            }
        },
        {
            "id": "source2", 
            "name": "Carbon Emissions Target",
            "type": "TARGET",
            "confidence": 0.88,
            "attributes": {
                "value": "45% reduction by 2030",
                "baseline": "2005 levels",
                "source": "Industry Analysis 2023"
            }
        },
        {
            "id": "source3",
            "name": "CO2 Reduction Goal",
            "type": "TARGET",
            "confidence": 0.92,
            "attributes": {
                "value": "50% reduction by 2030",
                "baseline": "1990 levels", 
                "source": "UN Report 2023"
            }
        }
    ]
    
    # Different strategies for different needs
    strategies = ["confidence_weighted", "evidence_based", "temporal_priority"]
    
    for strategy in strategies:
        print(f"\nStrategy: {strategy}")
        result = conflict_resolver.resolve(conflicting_data, strategy=strategy)
        print(f"  Final value: {result['attributes'].get('value', 'N/A')}")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"  Conflicts: {result['evidence']['conflicts_resolved']}")
    
    # Test 4: Selective consistency checking
    print("\n\n4. Selective Consistency Checking:")
    print("-"*50)
    
    test_entities = [
        {"id": "e1", "name": "United Nations", "type": "ORG"},
        {"id": "e2", "name": "UN", "type": "ORG"},  # Potential duplicate
        {"id": "e3", "name": "World Bank", "type": "ORG"},
        {"id": "e4", "name": "Paris Agreement", "type": "POLICY"},
    ]
    
    test_relationships = [
        {"source_id": "e1", "target_id": "e4", "type": "OVERSEES"},
        {"source_id": "e2", "target_id": "e4", "type": "MANAGES"},  # Conflict with e1->e4
        {"source_id": "e3", "target_id": "e4", "type": "FUNDS"},
    ]
    
    # Quick check - duplicates only
    print("\nQuick duplicate check (no embeddings):")
    result = consistency_checker.check(
        test_entities, test_relationships,
        check_duplicates=True,
        check_conflicts=False  # Skip this for speed
    )
    print(f"  Entity consistency: {result['scores'].get('entity_consistency', 0):.2%}")
    print(f"  Time saved by skipping conflict check")
    
    # Full check when needed
    print("\nFull consistency check:")
    result = consistency_checker.check(
        test_entities, test_relationships,
        check_duplicates=True,
        check_conflicts=True
    )
    print(f"  Overall score: {result['scores'].get('overall', 0):.2%}")
    print(f"  Issues found: {len(result['issues'])}")
    for issue in result['issues']:
        print(f"    - {issue['type']}: {issue}")
    
    # Test 5: Custom pipeline example
    print("\n\n5. Custom Pipeline Example:")
    print("-"*50)
    print("Example: Fast deduplication pipeline without expensive embeddings")
    
    # Step 1: Quick clustering
    clusters = cluster_finder.find_clusters(
        test_entities,
        similarity_threshold=0.8,
        use_embeddings=False  # Fast mode
    )
    print(f"1. Found {clusters['clusters_found']} potential duplicate clusters")
    
    # Step 2: Resolve each cluster
    resolved_entities = []
    for cluster_data in clusters['clusters'].values():
        if len(cluster_data['entities']) > 1:
            resolved = conflict_resolver.resolve(
                cluster_data['entities'],
                strategy="confidence_weighted"  # Simple strategy
            )
            resolved_entities.append(resolved)
            print(f"2. Resolved cluster: {len(cluster_data['entities'])} → 1 entity")
    
    # Step 3: Quick consistency check
    final_check = consistency_checker.check(
        resolved_entities, [],
        check_duplicates=True,
        check_conflicts=False  # No relationships to check
    )
    print(f"3. Final consistency: {final_check['scores'].get('entity_consistency', 0):.2%}")
    
    print("\n\n✅ Benefits of This Modular Design:")
    print("  1. Use embeddings only when needed (save API costs)")
    print("  2. Choose string matching for speed vs embeddings for accuracy")
    print("  3. Pick conflict resolution strategy based on use case")
    print("  4. Run only the consistency checks you need")
    print("  5. Build custom pipelines for specific scenarios")
    print("  6. Each tool can be exposed as a separate MCP endpoint")


if __name__ == "__main__":
    test_proper_modular_design()