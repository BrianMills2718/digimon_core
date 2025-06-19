#!/usr/bin/env python
"""Adversarial review - hunt for mocks, fakes, and incorrect implementations."""

import os
import sys
import time
import hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

print("=== ADVERSARIAL REVIEW: HUNTING FOR FAKES ===\n")

# Test 1: Check if databases actually persist data
print("TEST 1: Database Persistence Check")
print("-" * 50)

from src.utils.database import DatabaseManager
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear everything
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create test entity
test_id = "persistence_test_" + str(time.time())
with db.neo4j.driver.session() as session:
    session.run("""
        CREATE (e:Entity {
            id: $id,
            name: 'Persistence Test Entity',
            entity_type: 'TEST'
        })
    """, id=test_id)

# Close and reopen database
db.close()
db2 = DatabaseManager()
db2.initialize()

# Check if entity still exists
with db2.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (e:Entity {id: $id})
        RETURN e.name as name
    """, id=test_id).single()
    
    if result:
        print("✓ Neo4j persistence REAL - entity survived reconnection")
    else:
        print("❌ Neo4j persistence FAKE - entity lost after reconnection")

# Test 2: Verify LLM actually calls OpenAI
print("\n\nTEST 2: LLM Extractor Reality Check")
print("-" * 50)

if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  No API key - skipping LLM test")
else:
    # Intercept network calls
    import time
    from src.tools.phase2.t23b_llm_extractor import LLMExtractor
    from src.models import Document, Chunk
    
    # Create test chunk
    doc = Document(
        id='doc_adversarial',
        source_path='test.txt',
        title='Test',
        content_hash=hashlib.md5(b"test").hexdigest()
    )
    db2.sqlite.save_document(doc)
    
    chunk = Chunk(
        id='chunk_adversarial',
        document_id='doc_adversarial',
        text='Barack Obama was the 44th president of the United States.',
        position=0,
        start_char=0,
        end_char=57
    )
    db2.sqlite.save_chunk(chunk)
    
    # Time the extraction
    llm = LLMExtractor(db2)
    start = time.time()
    
    try:
        # Make two different calls with different text
        chunk1_text = 'Barack Obama was the 44th president of the United States.'
        chunk2_text = 'Martian robots invaded Earth yesterday according to sources.'
        
        # Update chunk text for second call
        chunk.text = chunk1_text
        db2.sqlite.save_chunk(chunk)
        
        result1 = llm.extract_entities_and_relationships(f"neo4j://chunk/{chunk.id}")
        
        # Update for second call
        chunk.text = chunk2_text
        db2.sqlite.save_chunk(chunk)
        
        result2 = llm.extract_entities_and_relationships(f"neo4j://chunk/{chunk.id}")
        
        elapsed = time.time() - start
        
        # Check for signs of real API calls
        if elapsed < 0.5:
            print(f"❌ SUSPICIOUS: Extraction took only {elapsed:.2f}s - likely FAKE")
        elif elapsed > 1.0:
            print(f"✓ Extraction took {elapsed:.2f}s - likely REAL API call")
        
        # Check if results differ
        if result1 == result2:
            print("❌ FAKE: Identical results for different text!")
        else:
            print("✓ Different results for different text - likely REAL")
            
    except Exception as e:
        print(f"⚠️  LLM test error: {e}")

# Test 3: Community detection randomness
print("\n\nTEST 3: Community Detection Reality Check")
print("-" * 50)

from src.tools.phase3.t31_entity_node_builder import EntityNodeBuilder

# Create random graph
import random
with db2.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create 20 random entities
    for i in range(20):
        session.run("""
            CREATE (e:Entity {
                id: $id,
                name: $name,
                entity_type: 'TEST'
            })
        """, id=f"rand_{i}", name=f"Random Entity {i}")
    
    # Create random edges
    for _ in range(30):
        a = random.randint(0, 19)
        b = random.randint(0, 19)
        if a != b:
            session.run("""
                MATCH (a:Entity {id: $a})
                MATCH (b:Entity {id: $b})
                MERGE (a)-[:RANDOM {weight: $w}]->(b)
            """, a=f"rand_{a}", b=f"rand_{b}", w=random.random() * 10)

# Run community detection multiple times
node_builder = EntityNodeBuilder(db2)
results = []
for i in range(3):
    result = node_builder.build_entity_nodes(algorithm="louvain")
    results.append(result['community_count'])
    
    # Shuffle edge weights
    with db2.neo4j.driver.session() as session:
        session.run("""
            MATCH ()-[r:RANDOM]->()
            SET r.weight = rand() * 10
        """)

if len(set(results)) == 1:
    print(f"❌ SUSPICIOUS: Same community count ({results[0]}) every time despite randomness")
else:
    print(f"✓ Community counts vary: {results} - algorithm seems REAL")

# Test 4: Check for hardcoded responses
print("\n\nTEST 4: Hardcoded Response Detection")
print("-" * 50)

# Create entities with specific names that might trigger hardcoded responses
test_entities = [
    ("Microsoft", "ORG"),
    ("Zzyzx Corp", "ORG"),  # Unusual name
    ("🤖 Robot Inc", "ORG"),  # Emoji name
    ("X Æ A-XII", "PERSON"),  # Special characters
]

with db2.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    for name, etype in test_entities:
        session.run("""
            CREATE (e:Entity {
                id: $id,
                name: $name,
                entity_type: $type
            })
        """, id=name.lower().replace(" ", "_"), name=name, type=etype)

# Test PageRank
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
pagerank = PageRankAnalyzer(db2)
pr_result = pagerank.compute_pagerank()

with db2.neo4j.driver.session() as session:
    scores = session.run("""
        MATCH (e:Entity)
        RETURN e.name as name, e.pagerank_score as score
        ORDER BY score DESC
    """).data()
    
    # Check if all scores are identical (suspicious)
    unique_scores = set(s['score'] for s in scores if s['score'] is not None)
    if len(unique_scores) == 1:
        print("❌ FAKE: All PageRank scores identical!")
    else:
        print(f"✓ PageRank scores vary: {len(unique_scores)} unique values")

# Test 5: Multi-hop query edge cases
print("\n\nTEST 5: Multi-hop Query Edge Cases")
print("-" * 50)

from src.tools.phase4.t49_hop_query import HopQuery

# Create disconnected graph
with db2.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Island 1
    session.run("""
        CREATE (a:Entity {id: 'island1_a', name: 'Island 1 A'})
        CREATE (b:Entity {id: 'island1_b', name: 'Island 1 B'})
        CREATE (a)-[:CONNECTED]->(b)
    """)
    
    # Island 2 (disconnected)
    session.run("""
        CREATE (x:Entity {id: 'island2_x', name: 'Island 2 X'})
        CREATE (y:Entity {id: 'island2_y', name: 'Island 2 Y'})
        CREATE (x)-[:CONNECTED]->(y)
    """)

hop_query = HopQuery(db2)

# Query from island 1 - should NOT find island 2
result = hop_query.hop_query(["Island 1 A"], k=10)
found_names = [e['name'] for dist in result['entities_by_distance'].values() for e in dist]

if 'Island 2 X' in found_names or 'Island 2 Y' in found_names:
    print("❌ FAKE: Found disconnected entities - graph traversal is broken!")
else:
    print("✓ Correctly limited to connected component")

# Test with non-existent entity
result = hop_query.hop_query(["This Entity Does Not Exist"], k=2)
if result['total_entities_found'] > 0:
    print("❌ FAKE: Found entities from non-existent source!")
else:
    print("✓ Correctly returned empty for non-existent source")

# Test 6: Vector search reality check
print("\n\nTEST 6: FAISS Vector Search Reality")
print("-" * 50)

import numpy as np
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator

# Generate embeddings for test entities
with db2.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create test entities
    for i in range(5):
        session.run("""
            CREATE (e:Entity {
                id: $id,
                name: $name,
                entity_type: 'TEST'
            })
        """, id=f"embed_test_{i}", name=f"Embedding Test {i}")

# Add to FAISS with known vectors
for i in range(5):
    # Create distinct vectors
    vector = np.zeros(384, dtype=np.float32)
    vector[i*50:(i+1)*50] = 1.0  # Different pattern for each
    db2.faiss.add_embedding(f"test_{i}", vector)

# Search with a specific pattern
query_vector = np.zeros(384, dtype=np.float32)
query_vector[100:150] = 1.0  # Should match test_2

results = db2.faiss.search(query_vector, k=3)
if results:
    top_result = results[0]
    if top_result['id'] == 'test_2':
        print("✓ FAISS search works correctly - found expected match")
    else:
        print(f"❌ FAISS search broken - expected test_2, got {top_result['id']}")
else:
    print("❌ FAISS search returned no results")

# Final Summary
print("\n\n=== ADVERSARIAL REVIEW SUMMARY ===")
print("=" * 50)
print("Checked for:")
print("- Database persistence (Neo4j)")
print("- Real API calls (OpenAI)")
print("- Algorithm randomness (Community detection)")
print("- Hardcoded responses (PageRank)")
print("- Graph traversal correctness")
print("- Vector search functionality")

# Cleanup
with db2.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db2.close()

print("\n✅ Adversarial review complete!")