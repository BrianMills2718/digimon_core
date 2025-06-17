#!/usr/bin/env python
"""Adversarial testing for Milestone 3: Community Detection & Multi-hop."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

from src.utils.database import DatabaseManager

print("=== ADVERSARIAL TESTING: MILESTONE 3 ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create test graph with clear communities
print("Creating test graph with communities...")
with db.neo4j.driver.session() as session:
    # Community 1: Tech companies
    session.run("""
        CREATE (ms:Entity {id: 'microsoft', name: 'Microsoft', entity_type: 'ORG'})
        CREATE (openai:Entity {id: 'openai', name: 'OpenAI', entity_type: 'ORG'})
        CREATE (github:Entity {id: 'github', name: 'GitHub', entity_type: 'ORG'})
        CREATE (sam:Entity {id: 'sam', name: 'Sam Altman', entity_type: 'PERSON'})
        CREATE (satya:Entity {id: 'satya', name: 'Satya Nadella', entity_type: 'PERSON'})
        
        CREATE (ms)-[:INVESTED_IN {weight: 10.0}]->(openai)
        CREATE (ms)-[:ACQUIRED {weight: 8.0}]->(github)
        CREATE (sam)-[:WORKS_AT {weight: 5.0}]->(openai)
        CREATE (satya)-[:WORKS_AT {weight: 5.0}]->(ms)
        CREATE (github)-[:PARTNERS_WITH {weight: 3.0}]->(openai)
    """)
    
    # Community 2: Space companies  
    session.run("""
        CREATE (spacex:Entity {id: 'spacex', name: 'SpaceX', entity_type: 'ORG'})
        CREATE (blue:Entity {id: 'blue', name: 'Blue Origin', entity_type: 'ORG'})
        CREATE (nasa:Entity {id: 'nasa', name: 'NASA', entity_type: 'ORG'})
        CREATE (elon:Entity {id: 'elon', name: 'Elon Musk', entity_type: 'PERSON'})
        CREATE (jeff:Entity {id: 'jeff', name: 'Jeff Bezos', entity_type: 'PERSON'})
        
        CREATE (elon)-[:FOUNDED {weight: 10.0}]->(spacex)
        CREATE (jeff)-[:FOUNDED {weight: 10.0}]->(blue)
        CREATE (spacex)-[:PARTNERS_WITH {weight: 5.0}]->(nasa)
        CREATE (blue)-[:PARTNERS_WITH {weight: 5.0}]->(nasa)
        CREATE (spacex)-[:COMPETES_WITH {weight: 3.0}]->(blue)
    """)
    
    # Weak link between communities
    session.run("""
        MATCH (elon:Entity {id: 'elon'})
        MATCH (openai:Entity {id: 'openai'})
        CREATE (elon)-[:INVESTED_IN {weight: 1.0}]->(openai)
    """)

print("✓ Created test graph with 2 communities")

# TEST 1: Community Detection
print("\nTEST 1: Community Detection")
print("-" * 50)

# Check if T31 exists
try:
    from src.tools.phase3.t31_entity_node_builder import EntityNodeBuilder
    node_builder = EntityNodeBuilder(db)
    
    # Run community detection
    result = node_builder.build_entity_nodes()
    
    # Check communities
    with db.neo4j.driver.session() as session:
        communities = session.run("""
            MATCH (e:Entity)
            WHERE e.community_id IS NOT NULL
            RETURN DISTINCT e.community_id as community, 
                   collect(e.name) as members
            ORDER BY size(members) DESC
        """).data()
        
        print(f"Communities found: {len(communities)}")
        for comm in communities:
            print(f"  Community {comm['community']}: {', '.join(comm['members'])}")
        
        # Verify we have at least 2 communities
        if len(communities) >= 2:
            print("\n✅ PASS: Found multiple communities")
        else:
            print("\n❌ FAIL: Expected 2+ communities")
            
except ImportError:
    print("❌ FAIL: T31 EntityNodeBuilder not implemented")
except Exception as e:
    print(f"❌ FAIL: Community detection error: {e}")

# TEST 2: Multi-hop Query Paths
print("\n\nTEST 2: Multi-hop Query Paths")
print("-" * 50)

test_queries = [
    # 3-hop: Satya -> Microsoft -> OpenAI -> Sam
    {
        "start": "Satya Nadella",
        "end": "Sam Altman", 
        "hops": 3,
        "desc": "Path from Satya to Sam (3 hops)"
    },
    # 4-hop: Jeff -> Blue Origin -> NASA -> SpaceX -> Elon
    {
        "start": "Jeff Bezos",
        "end": "Elon Musk",
        "hops": 4,
        "desc": "Path from Jeff to Elon (4 hops)"
    },
    # Cross-community: Microsoft -> OpenAI <- Elon -> SpaceX
    {
        "start": "Microsoft",
        "end": "SpaceX",
        "hops": 3,
        "desc": "Cross-community path (3 hops)"
    }
]

paths_found = 0
for query in test_queries:
    with db.neo4j.driver.session() as session:
        # Find shortest path
        result = session.run("""
            MATCH (start:Entity {name: $start})
            MATCH (end:Entity {name: $end})
            MATCH path = shortestPath((start)-[*..5]-(end))
            RETURN length(path) as hops,
                   [n in nodes(path) | n.name] as nodes
        """, start=query["start"], end=query["end"]).data()
        
        if result:
            path = result[0]
            print(f"\n{query['desc']}:")
            print(f"  Expected: {query['hops']} hops")
            print(f"  Found: {path['hops']} hops")
            print(f"  Path: {' -> '.join(path['nodes'])}")
            
            if path['hops'] >= 3:
                print("  ✓ Valid multi-hop path")
                paths_found += 1
            else:
                print("  ✗ Path too short")
        else:
            print(f"\n{query['desc']}: ✗ No path found")

if paths_found >= 2:
    print(f"\n✅ PASS: {paths_found}/3 multi-hop paths found")
else:
    print(f"\n❌ FAIL: Only {paths_found}/3 multi-hop paths found")

# TEST 3: GraphRAG Operators
print("\n\nTEST 3: GraphRAG Operators")  
print("-" * 50)

# Check if key operators are implemented
operators_to_test = [
    ("T49", "hop_query", "Multi-hop traversal"),
    ("T50", "neighborhood_search", "k-hop neighborhood"),
    ("T52", "path_finding", "Path between entities"),
    ("T56", "community_summary", "Summarize communities")
]

implemented = 0
for tool_id, method_name, desc in operators_to_test:
    try:
        # Try to import the operator
        module_name = f"src.tools.phase4.{tool_id.lower()}_{method_name}"
        operator = __import__(module_name, fromlist=[method_name])
        print(f"✓ {tool_id}: {desc} - Implemented")
        implemented += 1
    except ImportError:
        print(f"✗ {tool_id}: {desc} - Not implemented")

if implemented >= 2:
    print(f"\n✅ PASS: {implemented}/4 key operators implemented")
else:
    print(f"\n❌ FAIL: Only {implemented}/4 operators implemented")

# TEST 4: Performance Test
print("\n\nTEST 4: Performance Benchmark")
print("-" * 50)

# Create larger graph
print("Creating larger test graph (100 entities)...")
import time
start_time = time.time()

with db.neo4j.driver.session() as session:
    # Create 100 entities in 5 communities
    for community in range(5):
        for i in range(20):
            entity_id = f"entity_{community}_{i}"
            session.run("""
                CREATE (e:Entity {
                    id: $id,
                    name: $name,
                    entity_type: 'ORG',
                    community_id: $community
                })
            """, id=entity_id, name=f"Entity-{community}-{i}", community=community)
        
        # Connect entities within community
        session.run("""
            MATCH (a:Entity {community_id: $community})
            MATCH (b:Entity {community_id: $community})
            WHERE a.id < b.id AND rand() < 0.3
            CREATE (a)-[:RELATED {weight: rand() * 10}]->(b)
        """, community=community)

creation_time = time.time() - start_time
print(f"✓ Created graph in {creation_time:.2f}s")

# Test query performance
print("\nTesting query performance...")
query_times = []

for i in range(5):
    start = time.time()
    with db.neo4j.driver.session() as session:
        session.run("""
            MATCH path = (a:Entity)-[*..3]-(b:Entity)
            WHERE a.community_id <> b.community_id
            RETURN path
            LIMIT 10
        """).consume()
    query_times.append(time.time() - start)

avg_query_time = sum(query_times) / len(query_times)
print(f"Average 3-hop query time: {avg_query_time:.3f}s")

if avg_query_time < 1.0:
    print("✅ PASS: Query performance acceptable")
else:
    print("❌ FAIL: Queries too slow (>1s)")

# Final Summary
print("\n\n=== MILESTONE 3 REQUIREMENTS ===")
print("=" * 50)
print("[ ] Community detection implemented")
print("[ ] Multi-hop paths (3+ hops) working") 
print("[ ] Key GraphRAG operators implemented")
print("[ ] Performance <5min for realistic graphs")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Adversarial testing complete!")