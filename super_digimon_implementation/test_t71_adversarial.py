"""Adversarial testing for T71: Graph Statistics."""

import time
from datetime import datetime

from src.utils.database import DatabaseManager
from src.tools.phase5.t71_graph_statistics import GraphStatisticsAnalyzer
from tests.utils.builders import TestEntityBuilder, TestGraphBuilder, TestDataCleaner


def test_empty_graph():
    """Test statistics on empty graph."""
    print("\n=== TEST 1: Empty Graph ===")
    
    db = DatabaseManager()
    db.initialize()
    
    # Clean database
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
    
    analyzer = GraphStatisticsAnalyzer(db)
    
    # Compute statistics on empty graph
    result = analyzer.compute_statistics()
    
    print(f"\nEmpty graph statistics:")
    print(f"  Status: {result['status']}")
    print(f"  Node count: {result['basic_metrics'].get('node_count', 0)}")
    print(f"  Edge count: {result['basic_metrics'].get('edge_count', 0)}")
    print(f"  Density: {result['basic_metrics'].get('density', 0)}")
    print(f"  Warnings: {result['warnings']}")
    
    assert result["status"] == "success"
    assert result["basic_metrics"]["node_count"] == 0
    assert result["basic_metrics"]["edge_count"] == 0
    assert result["confidence"] == 0.0  # Empty graph
    
    db.close()
    print("✅ Empty graph test passed")


def test_single_node():
    """Test statistics on single node."""
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
    
    analyzer = GraphStatisticsAnalyzer(db)
    result = analyzer.compute_statistics()
    
    print(f"\nSingle node statistics:")
    print(f"  Node count: {result['basic_metrics']['node_count']}")
    print(f"  Edge count: {result['basic_metrics']['edge_count']}")
    print(f"  Average degree: {result['basic_metrics']['average_degree']}")
    print(f"  Components: {result['component_stats'].get('num_components', 0)}")
    print(f"  Diameter: {result['path_metrics'].get('diameter', 0)}")
    
    assert result["basic_metrics"]["node_count"] == 1
    assert result["basic_metrics"]["edge_count"] == 0
    assert result["basic_metrics"]["density"] == 0.0
    assert result["component_stats"]["num_components"] == 1
    
    db.close()
    print("✅ Single node test passed")


def test_complete_graph():
    """Test on complete graph (K5)."""
    print("\n=== TEST 3: Complete Graph K5 ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create complete graph with 5 nodes
        n = 5
        entities = []
        relationships = []
        
        # Create nodes
        for i in range(n):
            entities.append({
                "name": f"Node_{i}",
                "entity_type": "COMPLETE"
            })
        
        # Create all edges
        for i in range(n):
            for j in range(n):
                if i != j:
                    relationships.append({
                        "source_name": f"Node_{i}",
                        "target_name": f"Node_{j}",
                        "relationship_type": "CONNECTS"
                    })
        
        id_map = TestEntityBuilder.create_entities_with_relationships(
            session, entities, relationships
        )
    
    analyzer = GraphStatisticsAnalyzer(db)
    result = analyzer.compute_statistics()
    
    print(f"\nComplete graph K5 statistics:")
    print(f"  Node count: {result['basic_metrics']['node_count']}")
    print(f"  Edge count: {result['basic_metrics']['edge_count']}")
    print(f"  Density: {result['basic_metrics']['density']:.3f}")
    print(f"  Average degree: {result['basic_metrics']['average_degree']}")
    print(f"  Diameter: {result['path_metrics']['diameter']}")
    print(f"  Is connected: {result['path_metrics']['is_connected']}")
    
    # In complete directed graph K5: 5 nodes, 20 edges
    assert result["basic_metrics"]["node_count"] == n
    assert result["basic_metrics"]["edge_count"] == n * (n - 1)  # 20 edges
    assert result["basic_metrics"]["density"] == 1.0  # Complete graph
    assert result["path_metrics"]["diameter"] == 1  # All connected directly
    assert result["path_metrics"]["is_connected"] == True
    
    db.close()
    print("✅ Complete graph test passed")


def test_star_pattern():
    """Test on star pattern."""
    print("\n=== TEST 4: Star Pattern ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create star with 10 spokes
        id_map = TestGraphBuilder.create_hub_spoke(
            session,
            hub_name="Hub",
            spoke_count=10
        )
    
    analyzer = GraphStatisticsAnalyzer(db)
    result = analyzer.compute_statistics()
    
    print(f"\nStar pattern statistics:")
    print(f"  Node count: {result['basic_metrics']['node_count']}")
    print(f"  Edge count: {result['basic_metrics']['edge_count']}")
    print(f"  Average degree: {result['basic_metrics']['average_degree']:.2f}")
    
    # Degree distribution
    deg_dist = result["degree_distribution"]
    print(f"\nDegree distribution:")
    print(f"  Max degree: {deg_dist['total_degree_max']}")
    print(f"  Min degree: {deg_dist['total_degree_min']}")
    print(f"  Mean degree: {deg_dist['total_degree_mean']:.2f}")
    
    # Type distribution
    print(f"\nEntity types:")
    for et in result["type_distribution"]["entity_types"]:
        print(f"  {et['type']}: {et['count']}")
    
    assert result["basic_metrics"]["node_count"] == 11  # 1 hub + 10 spokes
    assert result["basic_metrics"]["edge_count"] == 10  # Hub to each spoke
    assert deg_dist["out_degree_max"] == 10  # Hub has 10 outgoing
    assert result["component_stats"]["num_components"] == 1
    
    db.close()
    print("✅ Star pattern test passed")


def test_disconnected_components():
    """Test on graph with multiple components."""
    print("\n=== TEST 5: Disconnected Components ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create 3 disconnected components
        components = TestGraphBuilder.create_disconnected_components(
            session,
            component_count=3,
            size_per_component=4
        )
    
    analyzer = GraphStatisticsAnalyzer(db)
    result = analyzer.compute_statistics()
    
    print(f"\nDisconnected graph statistics:")
    print(f"  Node count: {result['basic_metrics']['node_count']}")
    print(f"  Edge count: {result['basic_metrics']['edge_count']}")
    print(f"  Number of components: {result['component_stats']['num_components']}")
    print(f"  Component sizes: {[c['size'] for c in result['component_stats']['component_sizes']]}")
    print(f"  Is connected: {result['path_metrics'].get('is_connected', False)}")
    
    assert result["basic_metrics"]["node_count"] == 12  # 3 * 4
    assert result["basic_metrics"]["edge_count"] == 9   # 3 * 3 edges per chain
    assert result["component_stats"]["num_components"] == 3
    assert result["path_metrics"]["is_connected"] == False
    
    db.close()
    print("✅ Disconnected components test passed")


def test_type_filtering():
    """Test statistics with entity type filtering."""
    print("\n=== TEST 6: Type Filtering ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create mixed type graph
        entities = [
            {"name": "Person1", "entity_type": "PERSON"},
            {"name": "Person2", "entity_type": "PERSON"},
            {"name": "Org1", "entity_type": "ORGANIZATION"},
            {"name": "Org2", "entity_type": "ORGANIZATION"},
            {"name": "Org3", "entity_type": "ORGANIZATION"}
        ]
        
        relationships = [
            {"source_name": "Person1", "target_name": "Org1", "relationship_type": "WORKS_FOR"},
            {"source_name": "Person2", "target_name": "Org1", "relationship_type": "WORKS_FOR"},
            {"source_name": "Org1", "target_name": "Org2", "relationship_type": "PARTNERS_WITH"},
            {"source_name": "Org2", "target_name": "Org3", "relationship_type": "ACQUIRED"}
        ]
        
        TestEntityBuilder.create_entities_with_relationships(
            session, entities, relationships
        )
    
    analyzer = GraphStatisticsAnalyzer(db)
    
    # Test 1: All entities
    all_stats = analyzer.compute_statistics()
    print(f"\nAll entities: {all_stats['basic_metrics']['node_count']} nodes")
    
    # Test 2: Only PERSON entities
    person_stats = analyzer.compute_statistics(entity_type="PERSON")
    print(f"PERSON entities: {person_stats['basic_metrics']['node_count']} nodes")
    
    # Test 3: Only ORGANIZATION entities
    org_stats = analyzer.compute_statistics(entity_type="ORGANIZATION")
    print(f"ORGANIZATION entities: {org_stats['basic_metrics']['node_count']} nodes")
    
    # Test 4: Specific relationship type
    works_stats = analyzer.compute_statistics(relationship_type="WORKS_FOR")
    print(f"WORKS_FOR edges: {works_stats['basic_metrics']['edge_count']} edges")
    
    assert all_stats["basic_metrics"]["node_count"] == 5
    assert person_stats["basic_metrics"]["node_count"] == 2
    assert org_stats["basic_metrics"]["node_count"] == 3
    assert works_stats["basic_metrics"]["edge_count"] == 2
    
    db.close()
    print("✅ Type filtering test passed")


def test_assortativity():
    """Test degree assortativity calculation."""
    print("\n=== TEST 7: Assortativity ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create assortative graph (high degree nodes connect to high degree)
        # Core: 3 highly connected nodes
        # Periphery: 6 low degree nodes
        
        entities = []
        relationships = []
        
        # Core nodes
        for i in range(3):
            entities.append({"name": f"Core_{i}", "entity_type": "ASSORTATIVE"})
        
        # Periphery nodes
        for i in range(6):
            entities.append({"name": f"Periph_{i}", "entity_type": "ASSORTATIVE"})
        
        # Core fully connected
        for i in range(3):
            for j in range(3):
                if i != j:
                    relationships.append({
                        "source_name": f"Core_{i}",
                        "target_name": f"Core_{j}",
                        "relationship_type": "CORE_LINK"
                    })
        
        # Each periphery connects to one core
        for i in range(6):
            relationships.append({
                "source_name": f"Periph_{i}",
                "target_name": f"Core_{i % 3}",
                "relationship_type": "PERIPH_LINK"
            })
        
        TestEntityBuilder.create_entities_with_relationships(
            session, entities, relationships
        )
    
    analyzer = GraphStatisticsAnalyzer(db)
    result = analyzer.compute_statistics()
    
    print(f"\nAssortativity test:")
    print(f"  Assortativity coefficient: {result['assortativity']:.3f}")
    print(f"  Node count: {result['basic_metrics']['node_count']}")
    print(f"  Edge count: {result['basic_metrics']['edge_count']}")
    
    # Should have positive assortativity (high degree connects to high degree)
    assert result["assortativity"] is not None
    # Note: exact value depends on graph structure
    
    db.close()
    print("✅ Assortativity test passed")


def test_performance():
    """Test performance on larger graph."""
    print("\n=== TEST 8: Performance Testing ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        print("Creating test graph with 100 nodes...")
        
        # Create random graph
        import random
        
        # Create nodes
        entity_ids = []
        for i in range(100):
            eid = TestEntityBuilder.create_entity(
                session,
                name=f"Node_{i}",
                entity_type="PERF_TEST",
                confidence=random.random()
            )
            entity_ids.append(eid)
        
        # Create ~300 random edges
        edge_count = 0
        for _ in range(300):
            src = random.choice(entity_ids)
            tgt = random.choice(entity_ids)
            if src != tgt:
                session.run("""
                    MATCH (s:Entity {id: $src}), (t:Entity {id: $tgt})
                    CREATE (s)-[r:RELATES {
                        id: $rid,
                        relationship_type: $rtype,
                        confidence: $conf,
                        created_at: datetime()
                    }]->(t)
                """, src=src, tgt=tgt, rid=f"edge_{edge_count}",
                    rtype=random.choice(["TYPE_A", "TYPE_B", "TYPE_C"]),
                    conf=random.random())
                edge_count += 1
    
    analyzer = GraphStatisticsAnalyzer(db)
    
    # Test different configurations
    configs = [
        ("Basic only", {"include_degree_distribution": False, 
                       "include_component_analysis": False, 
                       "include_path_metrics": False}),
        ("With degree dist", {"include_degree_distribution": True, 
                             "include_component_analysis": False, 
                             "include_path_metrics": False}),
        ("With components", {"include_degree_distribution": False, 
                            "include_component_analysis": True, 
                            "include_path_metrics": False}),
        ("Full stats", {"include_degree_distribution": True, 
                       "include_component_analysis": True, 
                       "include_path_metrics": True}),
    ]
    
    for name, config in configs:
        start = time.time()
        result = analyzer.compute_statistics(**config)
        elapsed = time.time() - start
        
        print(f"\n{name}:")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Node count: {result['basic_metrics']['node_count']}")
        print(f"  Edge count: {result['basic_metrics']['edge_count']}")
        
        # Performance check
        if "include_path_metrics" not in config or not config["include_path_metrics"]:
            assert elapsed < 1.0  # Should be fast without path metrics
        else:
            assert elapsed < 10.0  # Path metrics can be slower
    
    db.close()
    print("✅ Performance test passed")


def test_edge_cases():
    """Test various edge cases."""
    print("\n=== TEST 9: Edge Cases ===")
    
    db = DatabaseManager()
    db.initialize()
    
    analyzer = GraphStatisticsAnalyzer(db)
    
    # Test 1: Self-loops
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        print("\n1. Self-loops:")
        # Create node with self-loop
        eid = TestEntityBuilder.create_entity(
            session,
            name="SelfLoop",
            entity_type="LOOP"
        )
        
        # Add self-loop
        session.run("""
            MATCH (e:Entity {id: $id})
            CREATE (e)-[:RELATES {id: 'self_loop', created_at: datetime()}]->(e)
        """, id=eid)
    
    result = analyzer.compute_statistics()
    print(f"   Self-loops count: {result['basic_metrics']['self_loops']}")
    assert result["basic_metrics"]["self_loops"] == 1
    
    # Test 2: Invalid type filter
    print("\n2. Invalid type filter:")
    result = analyzer.compute_statistics(entity_type="NONEXISTENT")
    print(f"   Node count: {result['basic_metrics']['node_count']}")
    assert result["basic_metrics"]["node_count"] == 0
    
    # Test 3: High confidence filter
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        print("\n3. Confidence filtering:")
        # Create edges with different confidences
        entities = []
        for i in range(3):
            entities.append({"name": f"Node_{i}", "entity_type": "CONF_TEST"})
        
        id_map = TestEntityBuilder.create_entities_with_relationships(
            session, entities, []
        )
        
        # Add edges with specific confidences
        session.run("""
            MATCH (s:Entity {name: 'Node_0'}), (t:Entity {name: 'Node_1'})
            CREATE (s)-[:RELATES {id: 'e1', confidence: 0.9, created_at: datetime()}]->(t)
        """)
        session.run("""
            MATCH (s:Entity {name: 'Node_1'}), (t:Entity {name: 'Node_2'})
            CREATE (s)-[:RELATES {id: 'e2', confidence: 0.3, created_at: datetime()}]->(t)
        """)
    
    # Without filter
    result_all = analyzer.compute_statistics(min_confidence=0.0)
    print(f"   All edges: {result_all['basic_metrics']['edge_count']}")
    
    # With high confidence filter
    result_high = analyzer.compute_statistics(min_confidence=0.5)
    print(f"   High confidence edges: {result_high['basic_metrics']['edge_count']}")
    
    assert result_all["basic_metrics"]["edge_count"] == 2
    assert result_high["basic_metrics"]["edge_count"] == 1
    
    # Test 4: Sample size for path metrics
    print("\n4. Sample size test:")
    result_sample = analyzer.compute_statistics(
        include_path_metrics=True,
        sample_size=2
    )
    print(f"   Sample-based path metrics: {result_sample['path_metrics']['sample_based']}")
    assert result_sample["path_metrics"]["sample_based"] == True
    
    db.close()
    print("✅ Edge cases handled correctly")


def main():
    """Run all adversarial tests."""
    print("=" * 80)
    print("ADVERSARIAL TESTING: T71 Graph Statistics")
    print("=" * 80)
    
    tests = [
        test_empty_graph,
        test_single_node,
        test_complete_graph,
        test_star_pattern,
        test_disconnected_components,
        test_type_filtering,
        test_assortativity,
        test_performance,
        test_edge_cases
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
        print("✅ ALL TESTS PASSED - T71 is working correctly!")
    else:
        print(f"❌ {failed} tests failed - needs fixes")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)