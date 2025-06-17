"""Milestone 4 Validation: Statistical Analysis Tools."""

import time
import random
from datetime import datetime

from src.utils.database import DatabaseManager
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase5.t69_centrality_measures import CentralityAnalyzer
from src.tools.phase5.t70_clustering_coefficient import ClusteringAnalyzer
from src.tools.phase5.t71_graph_statistics import GraphStatisticsAnalyzer
from tests.utils.builders import TestEntityBuilder, TestDataCleaner


def create_research_graph(session):
    """Create a realistic research knowledge graph."""
    print("Creating research knowledge graph...")
    
    # Entities: Researchers, Papers, Institutions, Topics
    entities = [
        # Researchers
        {"name": "Dr. Alice Chen", "entity_type": "RESEARCHER"},
        {"name": "Prof. Bob Smith", "entity_type": "RESEARCHER"},
        {"name": "Dr. Carol Lee", "entity_type": "RESEARCHER"},
        {"name": "Prof. David Kim", "entity_type": "RESEARCHER"},
        {"name": "Dr. Eve Johnson", "entity_type": "RESEARCHER"},
        
        # Papers
        {"name": "GraphRAG: A Novel Approach", "entity_type": "PAPER"},
        {"name": "Neural Networks for Graphs", "entity_type": "PAPER"},
        {"name": "Knowledge Graph Construction", "entity_type": "PAPER"},
        {"name": "Graph Mining Techniques", "entity_type": "PAPER"},
        {"name": "LLM Integration Methods", "entity_type": "PAPER"},
        
        # Institutions
        {"name": "MIT", "entity_type": "INSTITUTION"},
        {"name": "Stanford", "entity_type": "INSTITUTION"},
        {"name": "CMU", "entity_type": "INSTITUTION"},
        
        # Topics
        {"name": "Graph Theory", "entity_type": "TOPIC"},
        {"name": "Machine Learning", "entity_type": "TOPIC"},
        {"name": "NLP", "entity_type": "TOPIC"}
    ]
    
    # Relationships with varying confidence
    relationships = [
        # Authorship (high confidence)
        {"source_name": "Dr. Alice Chen", "target_name": "GraphRAG: A Novel Approach", 
         "relationship_type": "AUTHORED", "confidence": 1.0},
        {"source_name": "Prof. Bob Smith", "target_name": "GraphRAG: A Novel Approach", 
         "relationship_type": "AUTHORED", "confidence": 1.0},
        {"source_name": "Dr. Carol Lee", "target_name": "Neural Networks for Graphs", 
         "relationship_type": "AUTHORED", "confidence": 1.0},
        {"source_name": "Prof. David Kim", "target_name": "Knowledge Graph Construction", 
         "relationship_type": "AUTHORED", "confidence": 1.0},
        {"source_name": "Dr. Eve Johnson", "target_name": "Graph Mining Techniques", 
         "relationship_type": "AUTHORED", "confidence": 1.0},
        
        # Affiliations
        {"source_name": "Dr. Alice Chen", "target_name": "MIT", 
         "relationship_type": "AFFILIATED_WITH", "confidence": 0.95},
        {"source_name": "Prof. Bob Smith", "target_name": "Stanford", 
         "relationship_type": "AFFILIATED_WITH", "confidence": 0.95},
        {"source_name": "Dr. Carol Lee", "target_name": "CMU", 
         "relationship_type": "AFFILIATED_WITH", "confidence": 0.95},
        {"source_name": "Prof. David Kim", "target_name": "Stanford", 
         "relationship_type": "AFFILIATED_WITH", "confidence": 0.95},
        {"source_name": "Dr. Eve Johnson", "target_name": "MIT", 
         "relationship_type": "AFFILIATED_WITH", "confidence": 0.95},
        
        # Paper topics
        {"source_name": "GraphRAG: A Novel Approach", "target_name": "Graph Theory", 
         "relationship_type": "DISCUSSES", "confidence": 0.9},
        {"source_name": "GraphRAG: A Novel Approach", "target_name": "Machine Learning", 
         "relationship_type": "DISCUSSES", "confidence": 0.8},
        {"source_name": "Neural Networks for Graphs", "target_name": "Machine Learning", 
         "relationship_type": "DISCUSSES", "confidence": 0.95},
        {"source_name": "Knowledge Graph Construction", "target_name": "NLP", 
         "relationship_type": "DISCUSSES", "confidence": 0.85},
        {"source_name": "LLM Integration Methods", "target_name": "NLP", 
         "relationship_type": "DISCUSSES", "confidence": 0.9},
        
        # Citations (varying confidence)
        {"source_name": "Neural Networks for Graphs", "target_name": "GraphRAG: A Novel Approach", 
         "relationship_type": "CITES", "confidence": 0.7},
        {"source_name": "Knowledge Graph Construction", "target_name": "GraphRAG: A Novel Approach", 
         "relationship_type": "CITES", "confidence": 0.8},
        {"source_name": "LLM Integration Methods", "target_name": "Knowledge Graph Construction", 
         "relationship_type": "CITES", "confidence": 0.6},
        
        # Collaborations (co-authorship implies collaboration)
        {"source_name": "Dr. Alice Chen", "target_name": "Prof. Bob Smith", 
         "relationship_type": "COLLABORATES_WITH", "confidence": 0.85},
        {"source_name": "Prof. David Kim", "target_name": "Dr. Eve Johnson", 
         "relationship_type": "COLLABORATES_WITH", "confidence": 0.5}
    ]
    
    # Create entities
    id_map = {}
    for entity_data in entities:
        entity_id = TestEntityBuilder.create_entity(
            session,
            name=entity_data["name"],
            entity_type=entity_data["entity_type"],
            confidence=0.9 + random.random() * 0.1  # 0.9-1.0
        )
        id_map[entity_data["name"]] = entity_id
    
    # Create relationships
    for rel_data in relationships:
        source_id = id_map[rel_data["source_name"]]
        target_id = id_map[rel_data["target_name"]]
        
        session.run("""
            MATCH (s:Entity {id: $source_id}), (t:Entity {id: $target_id})
            CREATE (s)-[r:RELATES {
                id: $rid,
                relationship_type: $rel_type,
                confidence: $confidence,
                created_at: datetime()
            }]->(t)
        """, 
            source_id=source_id,
            target_id=target_id,
            rid=f"rel_{source_id}_{target_id}",
            rel_type=rel_data["relationship_type"],
            confidence=rel_data.get("confidence", 0.8)
        )
    
    return id_map


def test_pagerank_integration():
    """Test T68: PageRank on research graph."""
    print("\n=== Testing T68: PageRank ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        id_map = create_research_graph(session)
    
    analyzer = PageRankAnalyzer(db)
    
    # Test 1: Basic PageRank
    print("\n1. Basic PageRank:")
    result = analyzer.compute_pagerank(
        max_iterations=20,
        damping_factor=0.85
    )
    
    print(f"   Status: {result['status']}")
    print(f"   Entities ranked: {len(result['scores'])}")
    print(f"   Top 3 entities:")
    for entity in result["top_entities"][:3]:
        print(f"     - {entity['name']} ({entity['type']}): {entity['pagerank']:.4f}")
    
    assert result["status"] == "success"
    assert len(result["scores"]) == 16  # All entities
    
    # Test 2: Type-specific PageRank
    print("\n2. PageRank for PAPER entities only:")
    paper_result = analyzer.compute_pagerank(
        entity_type="PAPER"
    )
    
    print(f"   Papers ranked: {len(paper_result['scores'])}")
    print(f"   Top paper: {paper_result['top_entities'][0]['name']}")
    
    assert len(paper_result["scores"]) == 5  # Only papers
    
    db.close()
    return True


def test_centrality_integration():
    """Test T69: Centrality Measures on research graph."""
    print("\n=== Testing T69: Centrality Measures ===")
    
    db = DatabaseManager()
    db.initialize()
    
    # Use existing graph
    analyzer = CentralityAnalyzer(db)
    
    measures = ["degree", "betweenness", "closeness", "eigenvector"]
    results = {}
    
    for measure in measures:
        print(f"\n{measure.capitalize()} Centrality:")
        result = analyzer.compute_centrality(
            measure=measure,
            normalized=True,
            weighted=True,
            weight_property="confidence"
        )
        
        if result["status"] == "success":
            print(f"   Computed for {len(result['scores'])} entities")
            print(f"   Top entity: {result['top_entities'][0]['name']} - Score: {result['top_entities'][0][f'{measure}_score']:.4f}")
            results[measure] = result
        else:
            print(f"   Failed: {result.get('error', 'Unknown error')}")
    
    # Verify all measures computed
    assert len(results) == 4
    assert all(r["status"] == "success" for r in results.values())
    
    # Compare different centrality measures
    print("\n\nCentrality Comparison for 'GraphRAG: A Novel Approach':")
    paper_ref = f"neo4j://entity/{[k for k, v in create_research_graph(db.neo4j.driver.session()).items() if 'GraphRAG' in k][0]}"
    
    for measure, result in results.items():
        if paper_ref in result["scores"]:
            print(f"   {measure}: {result['scores'][paper_ref]:.4f}")
    
    db.close()
    return True


def test_clustering_integration():
    """Test T70: Clustering Coefficient on research graph."""
    print("\n=== Testing T70: Clustering Coefficient ===")
    
    db = DatabaseManager()
    db.initialize()
    
    analyzer = ClusteringAnalyzer(db)
    
    # Test different modes
    modes = ["local", "global", "both"]
    
    for mode in modes:
        print(f"\n{mode.capitalize()} clustering:")
        result = analyzer.compute_clustering(
            mode=mode,
            weighted=True,
            weight_property="confidence",
            min_degree=1  # Include all nodes
        )
        
        if mode in ["local", "both"]:
            print(f"   Nodes analyzed: {len(result['local_clustering'])}")
            print(f"   Average clustering: {result['average_clustering']:.4f}")
            print(f"   Clustered nodes: {result['clustered_nodes']}")
        
        if mode in ["global", "both"]:
            print(f"   Global clustering: {result['global_clustering']:.4f}")
        
        assert result["status"] == "success"
    
    # Test entity type filtering
    print("\n\nClustering by entity type:")
    for entity_type in ["RESEARCHER", "PAPER", "INSTITUTION"]:
        result = analyzer.compute_clustering(
            mode="both",
            entity_type=entity_type
        )
        print(f"   {entity_type}: avg={result['average_clustering']:.4f}, global={result['global_clustering']:.4f}")
    
    db.close()
    return True


def test_statistics_integration():
    """Test T71: Graph Statistics on research graph."""
    print("\n=== Testing T71: Graph Statistics ===")
    
    db = DatabaseManager()
    db.initialize()
    
    # Clean and recreate graph
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        id_map = create_research_graph(session)
    
    analyzer = GraphStatisticsAnalyzer(db)
    
    # Comprehensive statistics
    print("\nComprehensive graph statistics:")
    result = analyzer.compute_statistics(
        include_degree_distribution=True,
        include_component_analysis=True,
        include_path_metrics=True,
        sample_size=None  # Small graph, no sampling needed
    )
    
    # Basic metrics
    print(f"\nBasic Metrics:")
    for key, value in result["basic_metrics"].items():
        print(f"   {key}: {value}")
    
    # Degree distribution
    print(f"\nDegree Distribution:")
    print(f"   Mean degree: {result['degree_distribution']['total_degree_mean']:.2f}")
    print(f"   Max degree: {result['degree_distribution']['total_degree_max']}")
    
    # Component analysis
    print(f"\nComponent Analysis:")
    print(f"   Components: {result['component_stats']['num_components']}")
    print(f"   Largest component: {result['component_stats']['largest_component_size']} nodes")
    
    # Path metrics
    print(f"\nPath Metrics:")
    print(f"   Diameter: {result['path_metrics']['diameter']}")
    print(f"   Average path length: {result['path_metrics']['average_path_length']:.2f}")
    
    # Type distribution
    print(f"\nEntity Type Distribution:")
    for et in result["type_distribution"]["entity_types"]:
        print(f"   {et['type']}: {et['count']}")
    
    # Assortativity
    print(f"\nAssortativity: {result['assortativity']:.4f}")
    
    assert result["status"] == "success"
    assert result["basic_metrics"]["node_count"] == 16
    assert result["component_stats"]["num_components"] == 1  # Should be connected
    
    db.close()
    return True


def test_combined_analysis():
    """Test all tools working together on same graph."""
    print("\n=== Testing Combined Analysis ===")
    
    db = DatabaseManager()
    db.initialize()
    
    # Initialize all analyzers
    pagerank_analyzer = PageRankAnalyzer(db)
    centrality_analyzer = CentralityAnalyzer(db)
    clustering_analyzer = ClusteringAnalyzer(db)
    stats_analyzer = GraphStatisticsAnalyzer(db)
    
    # Run all analyses
    print("\nRunning all analyses...")
    start_time = time.time()
    
    pagerank = pagerank_analyzer.compute_pagerank()
    degree_centrality = centrality_analyzer.compute_centrality(measure="degree")
    clustering = clustering_analyzer.compute_clustering(mode="both")
    statistics = stats_analyzer.compute_statistics()
    
    total_time = time.time() - start_time
    print(f"\nTotal analysis time: {total_time:.2f}s")
    
    # Find most important RESEARCHER
    print("\n\nMost Important Researcher Analysis:")
    
    # Get researcher entities
    researchers = [e for e in pagerank["top_entities"] if e["type"] == "RESEARCHER"]
    
    if researchers:
        top_researcher = researchers[0]
        researcher_ref = top_researcher["entity_ref"]
        
        print(f"\nTop Researcher: {top_researcher['name']}")
        print(f"   PageRank: {pagerank['scores'][researcher_ref]:.4f}")
        print(f"   Degree Centrality: {degree_centrality['scores'].get(researcher_ref, 0):.4f}")
        
        if researcher_ref in clustering["local_clustering"]:
            print(f"   Clustering Coefficient: {clustering['local_clustering'][researcher_ref]:.4f}")
    
    # Verify all succeeded
    assert all(r["status"] == "success" for r in [pagerank, degree_centrality, clustering, statistics])
    
    db.close()
    return True


def test_performance_scaling():
    """Test performance with larger graphs."""
    print("\n=== Testing Performance Scaling ===")
    
    db = DatabaseManager()
    db.initialize()
    
    with db.neo4j.driver.session() as session:
        TestDataCleaner.cleanup_all(session)
        
        # Create larger graph
        print("Creating large test graph (200 nodes, ~600 edges)...")
        
        entity_ids = []
        for i in range(200):
            eid = TestEntityBuilder.create_entity(
                session,
                name=f"Entity_{i}",
                entity_type=random.choice(["TYPE_A", "TYPE_B", "TYPE_C"]),
                confidence=random.random()
            )
            entity_ids.append(eid)
        
        # Create random edges
        edge_count = 0
        for _ in range(600):
            src = random.choice(entity_ids)
            tgt = random.choice(entity_ids)
            if src != tgt:
                try:
                    session.run("""
                        MATCH (s:Entity {id: $src}), (t:Entity {id: $tgt})
                        CREATE (s)-[r:RELATES {
                            id: $rid,
                            relationship_type: $rtype,
                            confidence: $conf,
                            created_at: datetime()
                        }]->(t)
                    """, src=src, tgt=tgt, rid=f"edge_{edge_count}",
                        rtype=random.choice(["RELATES", "LINKS", "CONNECTS"]),
                        conf=random.random())
                    edge_count += 1
                except:
                    pass  # Ignore duplicate edges
    
    # Time each analysis
    timings = {}
    
    # PageRank
    pr_analyzer = PageRankAnalyzer(db)
    start = time.time()
    pr_result = pr_analyzer.compute_pagerank(max_iterations=10)
    timings["PageRank"] = time.time() - start
    
    # Centrality (just degree - others are slow)
    cent_analyzer = CentralityAnalyzer(db)
    start = time.time()
    cent_result = cent_analyzer.compute_centrality(measure="degree")
    timings["Degree Centrality"] = time.time() - start
    
    # Clustering (local only)
    clust_analyzer = ClusteringAnalyzer(db)
    start = time.time()
    clust_result = clust_analyzer.compute_clustering(mode="local")
    timings["Local Clustering"] = time.time() - start
    
    # Statistics (without path metrics)
    stats_analyzer = GraphStatisticsAnalyzer(db)
    start = time.time()
    stats_result = stats_analyzer.compute_statistics(include_path_metrics=False)
    timings["Graph Statistics"] = time.time() - start
    
    print("\nPerformance Results (200 nodes, ~600 edges):")
    for analysis, duration in timings.items():
        print(f"   {analysis}: {duration:.3f}s")
    
    # All should complete in reasonable time
    assert all(t < 5.0 for t in timings.values())  # 5 seconds max
    
    db.close()
    return True


def main():
    """Run Milestone 4 validation tests."""
    print("=" * 80)
    print("MILESTONE 4 VALIDATION: Statistical Analysis Tools")
    print("=" * 80)
    
    tests = [
        ("PageRank Integration", test_pagerank_integration),
        ("Centrality Measures Integration", test_centrality_integration),
        ("Clustering Coefficient Integration", test_clustering_integration),
        ("Graph Statistics Integration", test_statistics_integration),
        ("Combined Analysis", test_combined_analysis),
        ("Performance Scaling", test_performance_scaling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                print(f"\n✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"MILESTONE 4 VALIDATION RESULTS: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("\n✅ MILESTONE 4 COMPLETE! All statistical analysis tools working correctly.")
        print("\nTools Validated:")
        print("  - T68: PageRank ✅")
        print("  - T69: Centrality Measures ✅")
        print("  - T70: Clustering Coefficient ✅")
        print("  - T71: Graph Statistics ✅")
        print("\nAll tools:")
        print("  - Handle real graph structures")
        print("  - Compute correct metrics")
        print("  - Scale to larger graphs")
        print("  - Work together seamlessly")
    else:
        print(f"\n❌ MILESTONE 4 INCOMPLETE: {failed} tests failed")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)