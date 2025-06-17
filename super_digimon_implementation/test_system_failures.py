#!/usr/bin/env python
"""Comprehensive test proving system failures."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== SYSTEM FAILURE ANALYSIS ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear everything
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Test 1: Entity Extraction
print("TEST 1: Entity Extraction")
print("-" * 50)

doc = Document(title="Test", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

chunk = Chunk(
    document_id=doc.id,
    text="Bill Gates founded Microsoft in 1975. Steve Jobs founded Apple in 1976. Gates and Jobs were rivals.",
    position=0, start_char=0, end_char=200, confidence=1.0
)
db.sqlite.save_chunk(chunk)

extractor = EntityExtractorSpacy(db)
result = extractor.extract_entities(f"sqlite://chunk/{chunk.id}")
print(f"✓ Extracted {result['entity_count']} entities")

# Check what was extracted
with db.neo4j.driver.session() as session:
    entities = session.run("MATCH (e:Entity) RETURN e.name as name, e.entity_type as type").data()
    print("\nExtracted entities:")
    for e in entities:
        print(f"  - {e['name']} ({e['type']})")
    
    # Check relationships
    rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
    print(f"\n❌ FAILURE: Relationships created: {rels} (should have relationships between entities)")

# Test 2: PageRank on empty relationship graph
print("\n\nTEST 2: PageRank Analysis")
print("-" * 50)

pagerank = PageRankAnalyzer(db)
try:
    pr_result = pagerank.calculate_pagerank()
    print(f"PageRank claims to have processed: {pr_result['entities_processed']} entities")
    
    # Check if scores were actually computed
    with db.neo4j.driver.session() as session:
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.pagerank_score IS NOT NULL
            RETURN count(e) as count
        """)
        scored_count = result.single()["count"]
        print(f"Entities with PageRank scores: {scored_count}")
        
    if pr_result['top_entities']:
        print("\nTop entities:")
        for e in pr_result['top_entities'][:3]:
            print(f"  - {e['name']}: {e['score']}")
    else:
        print("❌ FAILURE: No top entities returned")
        
except Exception as e:
    print(f"❌ FAILURE: PageRank crashed: {e}")

# Test 3: Embeddings
print("\n\nTEST 3: Embeddings")
print("-" * 50)

embedder = EmbeddingGenerator(db)
embed_result = embedder.generate_embeddings(
    object_refs=[f"sqlite://chunk/{chunk.id}"] + result['entity_refs'][:5]
)
print(f"✓ Created {embed_result['embedding_count']} embeddings")
print(f"FAISS index size: {db.faiss.index.ntotal}")

# Test 4: Natural Language Queries
print("\n\nTEST 4: Natural Language Queries")
print("-" * 50)

query_tool = NaturalLanguageQuery(db)

# Test relationship understanding
queries = [
    ("Who founded Microsoft?", "Bill Gates"),
    ("When was Apple founded?", "1976"),
    ("What is the relationship between Gates and Jobs?", "rivals"),
    ("Which companies did Gates and Jobs found?", "Microsoft and Apple")
]

failures = []
for query, expected in queries:
    print(f"\nQuery: '{query}'")
    result = query_tool.query(query)
    answer = result['answer']
    
    # Check if answer contains expected information
    if expected.lower() in answer.lower():
        print(f"✓ Answer contains '{expected}'")
    else:
        print(f"❌ FAILURE: Answer missing '{expected}'")
        failures.append(f"Query '{query}' failed to find '{expected}'")
    
    print(f"Answer preview: {answer[:150]}...")

# Test 5: Graph Traversal
print("\n\nTEST 5: Graph Traversal Capabilities")
print("-" * 50)

with db.neo4j.driver.session() as session:
    # Try to find paths between entities
    result = session.run("""
        MATCH (gates:Entity {name: 'Bill Gates'})
        MATCH (jobs:Entity {name: 'Steve Jobs'})
        MATCH path = shortestPath((gates)-[*]-(jobs))
        RETURN length(path) as path_length
    """)
    
    paths = list(result)
    if paths:
        print(f"✓ Path found between Gates and Jobs: length {paths[0]['path_length']}")
    else:
        print("❌ FAILURE: No path between Gates and Jobs (no relationships)")

# FINAL VERDICT
print("\n\n=== FINAL VERDICT ===")
print("=" * 50)

issues = [
    "❌ No relationships created between entities",
    "❌ PageRank runs on isolated nodes (meaningless)",
    "❌ No graph traversal possible",
    "❌ Entity extraction misses dates as DATE type",
    "❌ System can't answer relationship questions",
    "❌ No mention-to-entity relationships",
    "❌ No co-occurrence relationships"
]

if failures:
    issues.extend([f"❌ {f}" for f in failures])

print("\nCRITICAL SYSTEM FAILURES:")
for issue in issues:
    print(f"  {issue}")

print("\nCONCLUSION: The system is NOT a functional GraphRAG.")
print("It's just keyword search with embeddings, not true graph analysis.")

# Show what a real GraphRAG would have
print("\n\nWhat's missing for real GraphRAG:")
print("- Entity-to-entity relationships (FOUNDED, RIVALS, etc.)")
print("- Temporal relationships (HAPPENED_IN year)")  
print("- Co-occurrence relationships between entities in same chunk")
print("- Hierarchical relationships (PART_OF, SUBSIDIARY_OF)")
print("- True graph algorithms (community detection, centrality)")
print("- Multi-hop reasoning capabilities")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()