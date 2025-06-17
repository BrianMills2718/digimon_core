"""Adversarial testing for T69: Centrality Measures."""

import time
from datetime import datetime

from src.utils.database import DatabaseManager
from src.tools.phase5.t69_centrality_measures import CentralityAnalyzer
from tests.utils.builders import TestEntityBuilder, TestGraphBuilder, TestDataCleaner


def test_empty_graph():
    """Test centrality on empty graph."""
    print("\n=== TEST 1: Empty Graph ===")
    
    db = DatabaseManager()
    db.initialize()
    
    # Clean database
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
    
    analyzer = CentralityAnalyzer(db)
    
    # Test all measures on empty graph
    measures = ["degree", "betweenness", "closeness", "eigenvector"]
    
    for measure in measures:
        print(f"\nTesting {measure} centrality on empty graph:")
        result = analyzer.compute_centrality(measure=measure)
        
        print(f"  Status: {result['status']}")
        print(f"  Scores: {len(result['scores'])} entities")
        print(f"  Warnings: {result['warnings']}")
        print(f"  Confidence: {result['confidence']}")
        
        # Verify it handles empty graph gracefully
        assert result["status"] == "success"
        assert len(result["scores"]) == 0
        assert result["confidence"] == 0.0
        assert "No entities found" in str(result["warnings"])
    
    db.close()
    print("✅ Empty graph test passed")


def test_single_node():
    """Test centrality on single isolated node."""
    print("\n=== TEST 2: Single Node ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create single entity
        entity_id = TestEntityBuilder.create_entity(
            session,
            name="Lonely Node",
            entity_type="ISOLATED"
        )
    
    analyzer = CentralityAnalyzer(db)
    
    # Test all measures
    results = {}
    for measure in ["degree", "betweenness", "closeness", "eigenvector"]:
        result = analyzer.compute_centrality(measure=measure)
        results[measure] = result
        
        print(f"\n{measure.capitalize()} centrality:")
        print(f"  Score: {result['scores'].get(f'neo4j://entity/{entity_id}', 'N/A')}")
        print(f"  Stats: {result['statistics']}")
    
    # Verify expected values for single node
    assert results["degree"]["scores"][f"neo4j://entity/{entity_id}"] == 0.0  # No connections
    assert results["betweenness"]["scores"][f"neo4j://entity/{entity_id}"] == 0.0  # No paths through it
    assert results["closeness"]["scores"][f"neo4j://entity/{entity_id}"] == 0.0  # Unreachable to others
    
    db.close()
    print("✅ Single node test passed")


def test_simple_patterns():
    """Test on known graph patterns."""
    print("\n=== TEST 3: Known Patterns ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create star pattern (hub and spoke)
        print("\n1. Star Pattern (1 hub, 5 spokes):")
        id_map = TestGraphBuilder.create_hub_spoke(
            session,
            hub_name="Hub",
            spoke_count=5
        )
        
    analyzer = CentralityAnalyzer(db)
    
    # Test degree centrality
    degree_result = analyzer.compute_centrality(measure="degree", normalized=True)
    
    hub_ref = f"neo4j://entity/{id_map['Hub']}"
    hub_degree = degree_result["scores"][hub_ref]
    
    print(f"  Hub degree centrality: {hub_degree}")
    print(f"  Top entity: {degree_result['top_entities'][0]['name']}")
    
    # Hub should have highest degree (normalized to 1.0)
    assert hub_degree == 1.0
    assert degree_result['top_entities'][0]['name'] == "Hub"
    
    # All spokes should have same low degree
    spoke_degrees = []
    for i in range(5):
        spoke_ref = f"neo4j://entity/{id_map[f'Spoke_{i}']}"
        spoke_degrees.append(degree_result["scores"][spoke_ref])
    
    print(f"  Spoke degrees: {spoke_degrees}")
    assert all(d == spoke_degrees[0] for d in spoke_degrees)  # All equal
    assert spoke_degrees[0] < 0.3  # Much lower than hub
    
    # Clean and create chain
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        print("\n2. Chain Pattern (5 nodes in line):")
        chain_ids = TestGraphBuilder.create_simple_chain(
            session,
            length=5,
            entity_prefix="Node"
        )
    
    # Test betweenness on chain
    between_result = analyzer.compute_centrality(measure="betweenness", normalized=True)
    
    # Middle nodes should have highest betweenness
    middle_ref = f"neo4j://entity/{chain_ids[2]}"  # Node_2 (middle)
    middle_between = between_result["scores"].get(middle_ref, 0)
    
    end_ref = f"neo4j://entity/{chain_ids[0]}"  # Node_0 (end)
    end_between = between_result["scores"].get(end_ref, 0)
    
    print(f"  Middle node betweenness: {middle_between}")
    print(f"  End node betweenness: {end_between}")
    
    # Middle should have higher betweenness than ends
    assert middle_between > end_between
    
    db.close()
    print("✅ Pattern tests passed")


def test_directed_vs_undirected():
    """Test direction parameter effect."""
    print("\n=== TEST 4: Direction Testing ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create directed pattern: A -> B -> C, A -> C
        entities = [
            {"name": "A", "entity_type": "NODE"},
            {"name": "B", "entity_type": "NODE"},
            {"name": "C", "entity_type": "NODE"}
        ]
        
        relationships = [
            {"source_name": "A", "target_name": "B", "relationship_type": "POINTS_TO"},
            {"source_name": "B", "target_name": "C", "relationship_type": "POINTS_TO"},
            {"source_name": "A", "target_name": "C", "relationship_type": "POINTS_TO"}
        ]
        
        id_map = TestEntityBuilder.create_entities_with_relationships(
            session, entities, relationships
        )
    
    analyzer = CentralityAnalyzer(db)
    
    # Test degree with different directions
    directions = ["in", "out", "both"]
    results = {}
    
    for direction in directions:
        result = analyzer.compute_centrality(measure="degree", direction=direction)
        results[direction] = result
        
        print(f"\nDegree centrality (direction={direction}):")
        for name in ["A", "B", "C"]:
            ref = f"neo4j://entity/{id_map[name]}"
            score = result["scores"].get(ref, 0)
            print(f"  {name}: {score}")
    
    # Verify direction effects
    # In-degree: A=0, B=1, C=2
    # Out-degree: A=2, B=1, C=0
    # Both: A=2, B=2, C=2
    
    a_ref = f"neo4j://entity/{id_map['A']}"
    b_ref = f"neo4j://entity/{id_map['B']}"
    c_ref = f"neo4j://entity/{id_map['C']}"
    
    assert results["in"]["scores"][a_ref] == 0  # A has no incoming
    assert results["in"]["scores"][c_ref] == 2  # C has 2 incoming
    
    assert results["out"]["scores"][a_ref] == 2  # A has 2 outgoing
    assert results["out"]["scores"][c_ref] == 0  # C has no outgoing
    
    assert results["both"]["scores"][a_ref] == 2  # A has 2 total
    assert results["both"]["scores"][b_ref] == 2  # B has 2 total
    
    db.close()
    print("✅ Direction test passed")


def test_weighted_centrality():
    """Test weighted vs unweighted calculations."""
    print("\n=== TEST 5: Weighted Centrality ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create entities with weighted relationships
        entities = [
            {"name": "Strong", "entity_type": "NODE"},
            {"name": "Weak", "entity_type": "NODE"},
            {"name": "Target", "entity_type": "NODE"}
        ]
        
        # Create with different confidence weights
        id_map = TestEntityBuilder.create_entities_with_relationships(
            session, entities, []
        )
        
        # Add weighted relationships manually
        session.run("""
            MATCH (s:Entity {name: 'Strong'}), (t:Entity {name: 'Target'})
            CREATE (s)-[r:RELATES {
                id: 'strong_rel',
                relationship_type: 'STRONG_LINK',
                confidence: 0.9,
                created_at: datetime()
            }]->(t)
        """)
        
        session.run("""
            MATCH (w:Entity {name: 'Weak'}), (t:Entity {name: 'Target'})
            CREATE (w)-[r:RELATES {
                id: 'weak_rel',
                relationship_type: 'WEAK_LINK',
                confidence: 0.1,
                created_at: datetime()
            }]->(t)
        """)
    
    analyzer = CentralityAnalyzer(db)
    
    # Compare weighted vs unweighted
    unweighted = analyzer.compute_centrality(
        measure="degree",
        direction="in",
        weighted=False
    )
    
    weighted = analyzer.compute_centrality(
        measure="degree",
        direction="in",
        weighted=True,
        weight_property="confidence"
    )
    
    target_ref = f"neo4j://entity/{id_map['Target']}"
    
    print(f"\nTarget node centrality:")
    print(f"  Unweighted in-degree: {unweighted['scores'][target_ref]}")
    print(f"  Weighted in-degree: {weighted['scores'][target_ref]}")
    
    # Unweighted should count both equally (2)
    assert unweighted['scores'][target_ref] == 2.0
    
    # Weighted should sum confidences (0.9 + 0.1 = 1.0)
    assert abs(weighted['scores'][target_ref] - 1.0) < 0.01
    
    db.close()
    print("✅ Weighted centrality test passed")


def test_large_graph_performance():
    """Test performance on larger graphs."""
    print("\n=== TEST 6: Performance Testing ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create a larger random graph
        print("Creating test graph with 100 nodes...")
        
        # Create 100 entities
        entity_ids = []
        for i in range(100):
            eid = TestEntityBuilder.create_entity(
                session,
                name=f"Entity_{i}",
                entity_type="PERF_TEST"
            )
            entity_ids.append(eid)
        
        # Create ~300 random relationships
        import random
        for _ in range(300):
            src = random.choice(entity_ids)
            tgt = random.choice(entity_ids)
            if src != tgt:
                session.run("""
                    MATCH (s:Entity {id: $src}), (t:Entity {id: $tgt})
                    MERGE (s)-[r:RELATES {
                        id: $rid,
                        relationship_type: 'TEST_REL',
                        confidence: $conf,
                        created_at: datetime()
                    }]->(t)
                """, src=src, tgt=tgt, rid=f"rel_{_}", conf=random.random())
    
    analyzer = CentralityAnalyzer(db)
    
    # Time each measure
    measures = ["degree", "betweenness", "closeness", "eigenvector"]
    timings = {}
    
    for measure in measures:
        start = time.time()
        result = analyzer.compute_centrality(measure=measure)
        elapsed = time.time() - start
        timings[measure] = elapsed
        
        print(f"\n{measure.capitalize()} centrality:")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Entities: {len(result['scores'])}")
        print(f"  Top entity: {result['top_entities'][0]['name'] if result['top_entities'] else 'None'}")
        print(f"  Max score: {result['statistics']['max']:.4f}")
    
    # Verify reasonable performance
    assert timings["degree"] < 1.0  # Degree should be fast
    assert timings["eigenvector"] < 5.0  # Iterative, but reasonable
    
    # Betweenness is expensive, just check it completes
    assert result["status"] == "success"
    
    db.close()
    print("✅ Performance test passed")


def test_edge_cases():
    """Test various edge cases."""
    print("\n=== TEST 7: Edge Cases ===")
    
    db = DatabaseManager()
    db.initialize()
    
    analyzer = CentralityAnalyzer(db)
    
    # Test 1: Invalid measure
    print("\n1. Invalid measure name:")
    result = analyzer.compute_centrality(measure="invalid_measure")
    print(f"   Status: {result['status']}")
    print(f"   Error: {result.get('error', 'None')}")
    assert result["status"] == "error"
    assert "Invalid measure" in result["error"]
    
    # Test 2: Invalid direction
    print("\n2. Invalid direction:")
    result = analyzer.compute_centrality(measure="degree", direction="sideways")
    print(f"   Status: {result['status']}")
    print(f"   Error: {result.get('error', 'None')}")
    assert result["status"] == "error"
    assert "Invalid direction" in result["error"]
    
    # Test 3: Self-loops
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        print("\n3. Self-loop handling:")
        eid = TestEntityBuilder.create_entity(session, name="SelfLoop")
        
        # Create self-loop
        session.run("""
            MATCH (e:Entity {id: $id})
            CREATE (e)-[:RELATES {id: 'self', created_at: datetime()}]->(e)
        """, id=eid)
    
    result = analyzer.compute_centrality(measure="degree")
    ref = f"neo4j://entity/{eid}"
    print(f"   Self-loop degree: {result['scores'].get(ref, 'N/A')}")
    # Should handle gracefully, exact behavior may vary
    assert result["status"] == "success"
    
    # Test 4: Disconnected components
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        print("\n4. Disconnected components:")
        components = TestGraphBuilder.create_disconnected_components(
            session,
            component_count=3,
            size_per_component=3
        )
    
    result = analyzer.compute_centrality(measure="closeness")
    print(f"   Total entities: {len(result['scores'])}")
    print(f"   Avg closeness: {result['statistics']['mean']:.4f}")
    
    # Closeness should be low/zero for disconnected graph
    assert result['statistics']['mean'] < 0.5
    
    db.close()
    print("✅ Edge cases handled correctly")


def test_confidence_filtering():
    """Test minimum confidence filtering."""
    print("\n=== TEST 8: Confidence Filtering ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create entities with different confidence levels
        high_conf = TestEntityBuilder.create_entity(
            session,
            name="HighConfidence",
            confidence=0.9
        )
        
        low_conf = TestEntityBuilder.create_entity(
            session,
            name="LowConfidence",
            confidence=0.3
        )
        
        # Connect them
        session.run("""
            MATCH (h:Entity {id: $high}), (l:Entity {id: $low})
            CREATE (h)-[:RELATES {id: 'rel1', created_at: datetime()}]->(l)
        """, high=high_conf, low=low_conf)
    
    analyzer = CentralityAnalyzer(db)
    
    # Test without filtering
    result_all = analyzer.compute_centrality(
        measure="degree",
        min_confidence=0.0
    )
    
    # Test with filtering
    result_filtered = analyzer.compute_centrality(
        measure="degree",
        min_confidence=0.5
    )
    
    print(f"\nWithout filtering: {len(result_all['scores'])} entities")
    print(f"With filtering (>0.5): {len(result_filtered['scores'])} entities")
    print(f"Warnings: {result_filtered['warnings']}")
    
    # Should filter out low confidence entity
    assert len(result_all['scores']) == 2
    assert len(result_filtered['scores']) == 1
    assert f"neo4j://entity/{high_conf}" in result_filtered['scores']
    assert f"neo4j://entity/{low_conf}" not in result_filtered['scores']
    
    db.close()
    print("✅ Confidence filtering works correctly")


def main():
    """Run all adversarial tests."""
    print("=" * 80)
    print("ADVERSARIAL TESTING: T69 Centrality Measures")
    print("=" * 80)
    
    tests = [
        test_empty_graph,
        test_single_node,
        test_simple_patterns,
        test_directed_vs_undirected,
        test_weighted_centrality,
        test_large_graph_performance,
        test_edge_cases,
        test_confidence_filtering
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {len(tests) - failed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - T69 is working correctly!")
    else:
        print(f"❌ {failed} tests failed - needs fixes")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)