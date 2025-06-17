#!/usr/bin/env python
"""Test that timestamp fix works."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import DatabaseManager

print("=== TESTING TIMESTAMP FIX ===\n")

# Initialize
db = DatabaseManager()
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Test 1: Create entity without timestamps
print("Test 1: Entity without timestamps")
with db.neo4j.driver.session() as session:
    session.run("""
        CREATE (e:Entity {
            id: 'test_no_timestamps',
            name: 'Test Entity',
            entity_type: 'TEST'
        })
    """)

# Try to retrieve it
try:
    entity = db.neo4j.get_entity('test_no_timestamps')
    if entity:
        print(f"✓ Retrieved entity without timestamps")
        print(f"  created_at: {entity.created_at}")
        print(f"  updated_at: {entity.updated_at}")
    else:
        print("✗ Failed to retrieve entity")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: PageRank with entities without timestamps
print("\n\nTest 2: PageRank with entities without timestamps")
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create entities without timestamps
    session.run("""
        CREATE (a:Entity {id: 'a', name: 'A', entity_type: 'TEST'})
        CREATE (b:Entity {id: 'b', name: 'B', entity_type: 'TEST'})
        CREATE (c:Entity {id: 'c', name: 'C', entity_type: 'TEST'})
        CREATE (a)-[:LINKS_TO]->(b)
        CREATE (b)-[:LINKS_TO]->(c)
        CREATE (c)-[:LINKS_TO]->(a)
    """)

# Run PageRank
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
pagerank = PageRankAnalyzer(db)

try:
    result = pagerank.compute_pagerank()
    print(f"✓ PageRank completed successfully")
    print(f"  Processed {result['metadata']['entity_count']} entities")
except Exception as e:
    print(f"✗ PageRank failed: {e}")

# Test 3: Check if entities have PageRank scores
print("\n\nTest 3: Verify PageRank scores")
with db.neo4j.driver.session() as session:
    scores = session.run("""
        MATCH (e:Entity)
        RETURN e.id as id, e.pagerank_score as score
        ORDER BY e.id
    """).data()
    
    for s in scores:
        print(f"  {s['id']}: {s['score']}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Timestamp fix test complete!")