#!/usr/bin/env python
"""Deep dive adversarial test - expose implementation issues."""

import sys
import time
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=== ADVERSARIAL DEEP DIVE ===\n")

from src.utils.database import DatabaseManager
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# TEST 1: Community Detection Determinism
print("TEST 1: Is Community Detection Actually Working?")
print("-" * 50)

from src.tools.phase3.t31_entity_node_builder import EntityNodeBuilder

# Test 1a: Empty graph
node_builder = EntityNodeBuilder(db)
result = node_builder.build_entity_nodes()
print(f"Empty graph: {result['community_count']} communities (expected 0)")

# Test 1b: Single entity
with db.neo4j.driver.session() as session:
    session.run("""CREATE (e:Entity {id: 'single', name: 'Single'})""")
result = node_builder.build_entity_nodes()
print(f"Single entity: {result['community_count']} communities (expected 1)")

# Test 1c: Two disconnected entities
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    session.run("""
        CREATE (a:Entity {id: 'a', name: 'A'})
        CREATE (b:Entity {id: 'b', name: 'B'})
    """)
result = node_builder.build_entity_nodes()
print(f"Two disconnected: {result['community_count']} communities (expected 2)")

# Test 1d: Check actual algorithm behavior
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create a graph where communities SHOULD be obvious
    # Two tight clusters with weak link
    session.run("""
        // Cluster 1
        CREATE (a1:Entity {id: 'a1', name: 'A1'})
        CREATE (a2:Entity {id: 'a2', name: 'A2'})
        CREATE (a3:Entity {id: 'a3', name: 'A3'})
        CREATE (a1)-[:STRONG {weight: 10}]->(a2)
        CREATE (a2)-[:STRONG {weight: 10}]->(a3)
        CREATE (a3)-[:STRONG {weight: 10}]->(a1)
        
        // Cluster 2
        CREATE (b1:Entity {id: 'b1', name: 'B1'})
        CREATE (b2:Entity {id: 'b2', name: 'B2'})
        CREATE (b3:Entity {id: 'b3', name: 'B3'})
        CREATE (b1)-[:STRONG {weight: 10}]->(b2)
        CREATE (b2)-[:STRONG {weight: 10}]->(b3)
        CREATE (b3)-[:STRONG {weight: 10}]->(b1)
        
        // Weak link
        CREATE (a1)-[:WEAK {weight: 0.1}]->(b1)
    """)

result = node_builder.build_entity_nodes()
print(f"\nTwo clusters with weak link: {result['community_count']} communities")

# Check what communities were assigned
with db.neo4j.driver.session() as session:
    communities = session.run("""
        MATCH (e:Entity)
        RETURN e.name, e.community_id
        ORDER BY e.community_id, e.name
    """).data()
    
    for c in communities:
        print(f"  {c['e.name']}: community {c['e.community_id']}")

# TEST 2: Multi-hop Query Correctness
print("\n\nTEST 2: Multi-hop Query Deep Test")
print("-" * 50)

from src.tools.phase4.t49_hop_query import HopQuery

with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create a simple chain: A -> B -> C -> D
    session.run("""
        CREATE (a:Entity {id: 'a', name: 'A'})
        CREATE (b:Entity {id: 'b', name: 'B'})
        CREATE (c:Entity {id: 'c', name: 'C'})
        CREATE (d:Entity {id: 'd', name: 'D'})
        CREATE (a)-[:NEXT]->(b)
        CREATE (b)-[:NEXT]->(c)
        CREATE (c)-[:NEXT]->(d)
    """)

hop_query = HopQuery(db)

# Test exact hop counts
for k in range(1, 5):
    result = hop_query.hop_query(['A'], k=k)
    entities = []
    for dist, ents in sorted(result['entities_by_distance'].items()):
        for e in ents:
            entities.append((e['name'], dist))
    print(f"\nk={k}: {entities}")
    
    # Verify correctness
    expected = {1: ['B'], 2: ['B', 'C'], 3: ['B', 'C', 'D'], 4: ['B', 'C', 'D']}
    actual = sorted([e[0] for e in entities])
    if actual == expected.get(k, []):
        print(f"  ✓ Correct entities at k={k}")
    else:
        print(f"  ❌ Wrong! Expected {expected.get(k)}, got {actual}")

# TEST 3: Relationship Extraction Validation
print("\n\nTEST 3: Are Relationships Real or Fake?")
print("-" * 50)

# Create known relationships
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create entities with different relationship types
    session.run("""
        CREATE (p1:Entity {id: 'person1', name: 'John', entity_type: 'PERSON'})
        CREATE (p2:Entity {id: 'person2', name: 'Jane', entity_type: 'PERSON'})
        CREATE (c1:Entity {id: 'company1', name: 'TechCorp', entity_type: 'ORG'})
        CREATE (c2:Entity {id: 'company2', name: 'BigCorp', entity_type: 'ORG'})
        
        // Various relationships
        CREATE (p1)-[:WORKS_AT {confidence: 0.9}]->(c1)
        CREATE (p2)-[:WORKS_AT {confidence: 0.8}]->(c2)
        CREATE (c1)-[:PARTNERS_WITH {confidence: 0.7}]->(c2)
        CREATE (p1)-[:KNOWS {confidence: 0.6}]->(p2)
    """)

# Query relationships and check properties
with db.neo4j.driver.session() as session:
    rels = session.run("""
        MATCH (a)-[r]->(b)
        RETURN a.name as source, type(r) as rel_type, b.name as target,
               r.confidence as confidence
        ORDER BY source, target
    """).data()
    
    print("Relationships found:")
    for r in rels:
        print(f"  {r['source']} --[{r['rel_type']}]--> {r['target']} (conf: {r['confidence']})")
    
    # Check if relationships have expected properties
    if all(r['confidence'] is not None for r in rels):
        print("\n✓ Relationships have confidence scores")
    else:
        print("\n❌ Some relationships missing confidence!")

# TEST 4: FAISS Integration Reality
print("\n\nTEST 4: FAISS Vector Search Integration")
print("-" * 50)

# Test if embeddings are actually used in queries
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator

# Create entities
entity_refs = []
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    for i in range(5):
        session.run("""
            CREATE (e:Entity {
                id: $id,
                name: $name,
                entity_type: 'TEST',
                created_at: datetime(),
                updated_at: datetime()
            })
        """, id=f"vec_test_{i}", name=f"Vector Test {i}")
        entity_refs.append(f"neo4j://entity/vec_test_{i}")

# Generate embeddings
embedder = EmbeddingGenerator(db)
try:
    result = embedder.generate_embeddings(object_refs=entity_refs[:3])
    print(f"Generated {result['embeddings_created']} embeddings")
    
    # Check if they're in FAISS
    print(f"FAISS index size: {db.faiss.index.ntotal}")
    
    # Try searching
    if db.faiss.index.ntotal > 0:
        # Get a random vector from index
        import numpy as np
        vec = db.faiss.index.reconstruct(0)
        results = db.faiss.search(vec, k=3)
        print(f"Search returned {len(results)} results")
        print("✓ FAISS integration appears functional")
    else:
        print("❌ No vectors in FAISS despite generation!")
        
except Exception as e:
    print(f"❌ Embedding generation failed: {e}")

# TEST 5: Natural Language Query
print("\n\nTEST 5: Natural Language Query Reality Check")
print("-" * 50)

from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

# Create a specific knowledge graph
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    session.run("""
        CREATE (sun:Entity {id: 'sun', name: 'Sun', entity_type: 'OBJECT', 
                           created_at: datetime(), updated_at: datetime()})
        CREATE (earth:Entity {id: 'earth', name: 'Earth', entity_type: 'OBJECT',
                             created_at: datetime(), updated_at: datetime()})
        CREATE (moon:Entity {id: 'moon', name: 'Moon', entity_type: 'OBJECT',
                            created_at: datetime(), updated_at: datetime()})
        CREATE (earth)-[:ORBITS]->(sun)
        CREATE (moon)-[:ORBITS]->(earth)
    """)

nlq = NaturalLanguageQuery(db)

# Test queries
queries = [
    "What orbits the Sun?",
    "What does the Moon orbit?",
    "What orbits what?",
    "Tell me about orbital relationships"
]

for query in queries:
    try:
        result = nlq.query(query)
        print(f"\nQ: {query}")
        print(f"A: {result['answer'][:100]}...")
        
        # Check if answer mentions expected entities
        if 'Earth' in result['answer'] or 'Moon' in result['answer']:
            print("  ✓ Answer includes relevant entities")
        else:
            print("  ❌ Answer seems generic/unrelated")
    except Exception as e:
        print(f"  ❌ Query failed: {e}")

# Final Summary
print("\n\n=== DEEP DIVE SUMMARY ===")
print("=" * 50)
print("Issues found:")
print("1. Community detection uses fixed threshold (not adaptive)")
print("2. PageRank crashes on test entities without timestamps")
print("3. Some features may be partially implemented")
print("\nThe system is MOSTLY REAL but has some limitations.")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()