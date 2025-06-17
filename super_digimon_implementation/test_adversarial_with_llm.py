#!/usr/bin/env python
"""Adversarial test using LLM extraction."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found")
    sys.exit(1)

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23b_llm_extractor import LLMExtractor
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== ADVERSARIAL TESTING WITH LLM EXTRACTOR ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear everything
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Test 1: Relationship Extraction Accuracy
print("TEST 1: Relationship Extraction Accuracy")
print("-" * 50)

doc = Document(title="Test", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

# Test cases from adversarial test
test_chunks = [
    "Elon Musk founded Tesla in 2003. Tesla is headquartered in Austin, Texas.",
    "Musk also founded SpaceX. He sold PayPal to eBay. Peter Thiel was Musk's partner at PayPal.",
    "Tesla acquired SolarCity in 2016. SolarCity was founded by Musk's cousins. This was controversial.",
    "Before Tesla, Musk founded X.com in 1999. X.com merged with Confinity to become PayPal.",
    "Tesla competes with Ford and GM. Ford was founded by Henry Ford in 1903, the same year as Tesla's founding."
]

llm_extractor = LLMExtractor(db)
chunk_refs = []

for i, text in enumerate(test_chunks):
    chunk = Chunk(
        document_id=doc.id,
        text=text,
        position=i,
        start_char=i*200,
        end_char=(i+1)*200,
        confidence=1.0
    )
    db.sqlite.save_chunk(chunk)
    chunk_ref = f"sqlite://chunk/{chunk.id}"
    chunk_refs.append(chunk_ref)
    
    # Extract with LLM
    result = llm_extractor.extract_entities_and_relationships(chunk_ref)

# Check expected relationships
expected = [
    ("Elon Musk", "Tesla", "FOUNDED"),
    ("Tesla", "Austin", "LOCATED_IN"),
    ("Musk", "SpaceX", "FOUNDED"),
    ("Tesla", "SolarCity", "ACQUIRED"),
    ("Musk", "X.com", "FOUNDED")
]

found = 0
with db.neo4j.driver.session() as session:
    for source, target, rel_type in expected:
        result = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE toLower(a.name) CONTAINS toLower($source) 
               AND toLower(b.name) CONTAINS toLower($target)
            RETURN type(r) as rel_type, r.confidence as conf
        """, source=source, target=target)
        
        records = list(result)
        rel_types = [r['rel_type'] for r in records]
        
        if rel_type in rel_types:
            print(f"✓ Found: {source} --[{rel_type}]--> {target}")
            found += 1
        else:
            actual = rel_types[0] if rel_types else "NO RELATIONSHIP"
            print(f"✗ Missing: Expected {source} --[{rel_type}]--> {target}, got {actual}")

accuracy = found / len(expected)
print(f"\nRelationship accuracy: {found}/{len(expected)} = {accuracy:.1%}")

# Test 2: Relationship Type Distribution
print("\n\nTEST 2: Relationship Type Distribution")
print("-" * 50)

with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    rel_dist = list(result)
    total_rels = sum(r['count'] for r in rel_dist)
    
    print("Relationship distribution:")
    co_occurs_pct = 0
    for r in rel_dist:
        pct = (r['count'] / total_rels) * 100
        print(f"  {r['rel_type']}: {r['count']} ({pct:.1f}%)")
        if r['rel_type'] == 'CO_OCCURS_WITH':
            co_occurs_pct = pct
    
    if co_occurs_pct < 70:
        print(f"\n✅ PASS: CO_OCCURS_WITH is {co_occurs_pct:.1f}% (< 70%)")
    else:
        print(f"\n❌ FAIL: CO_OCCURS_WITH is {co_occurs_pct:.1f}% (>= 70%)")

# Test 3: Complex Queries
print("\n\nTEST 3: Complex Query Tests")
print("-" * 50)

# Generate embeddings
embedder = EmbeddingGenerator(db)
embedder.generate_embeddings(object_refs=chunk_refs)

# Run PageRank
pagerank = PageRankAnalyzer(db)
pagerank.compute_pagerank()

# Test queries
query_tool = NaturalLanguageQuery(db)

test_queries = [
    ("What companies are connected to Elon Musk through acquisitions?", ["Tesla", "SolarCity"]),
    ("Find companies founded by Musk", ["Tesla", "SpaceX", "X.com"]),
    ("What year did Tesla acquire SolarCity?", ["2016"])
]

success_count = 0
for query, expected_terms in test_queries:
    print(f"\nQuery: '{query}'")
    result = query_tool.query(query)
    answer = result['answer'].lower()
    
    found_terms = [term for term in expected_terms if term.lower() in answer]
    if len(found_terms) >= len(expected_terms) / 2:  # At least half the terms
        print(f"✓ Found relevant answer")
        success_count += 1
    else:
        print(f"✗ Answer not sufficient")
        print(f"  Expected terms: {expected_terms}")
        print(f"  Found: {found_terms}")

query_success_rate = success_count / len(test_queries)
print(f"\nQuery success rate: {success_count}/{len(test_queries)} = {query_success_rate:.1%}")

if query_success_rate >= 0.6:
    print("✅ PASS: Query success >= 60%")
else:
    print("❌ FAIL: Query success < 60%")

# Final Summary
print("\n\n=== FINAL RESULTS ===")
print("=" * 50)

issues = []
if accuracy < 0.6:
    issues.append(f"Relationship accuracy {accuracy:.1%} < 60%")
if co_occurs_pct >= 70:
    issues.append(f"CO_OCCURS_WITH {co_occurs_pct:.1%} >= 70%")
if query_success_rate < 0.6:
    issues.append(f"Query success {query_success_rate:.1%} < 60%")

if not issues:
    print("✅ ALL TESTS PASSED!")
    print("Milestone 2 requirements met with LLM extraction")
else:
    print("❌ FAILURES:")
    for issue in issues:
        print(f"  - {issue}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()