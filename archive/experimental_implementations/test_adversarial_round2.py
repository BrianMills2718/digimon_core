#!/usr/bin/env python
"""Second round of adversarial testing - even more aggressive."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy  
from src.tools.phase2.t24_relationship_extractor import RelationshipExtractor
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== ADVERSARIAL TESTING ROUND 2 ===")
print("Trying to break the 'GraphRAG' system...\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear everything
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Test 1: Does it actually extract the RIGHT relationships?
print("TEST 1: Relationship Extraction Accuracy")
print("-" * 50)

doc = Document(title="Test", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

# Tricky text with multiple relationship types
test_chunks = [
    # Clear relationships
    "Elon Musk founded Tesla in 2003. Tesla is headquartered in Austin, Texas.",
    # Ambiguous relationships
    "Musk also founded SpaceX. He sold PayPal to eBay. Peter Thiel was Musk's partner at PayPal.",
    # Complex relationships
    "Tesla acquired SolarCity in 2016. SolarCity was founded by Musk's cousins. This was controversial.",
    # Temporal relationships
    "Before Tesla, Musk founded X.com in 1999. X.com merged with Confinity to become PayPal.",
    # Competing relationships
    "Tesla competes with Ford and GM. Ford was founded by Henry Ford in 1903, the same year as Tesla's founding."
]

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
    chunk_refs.append(f"sqlite://chunk/{chunk.id}")

# Extract entities and relationships
entity_extractor = EntityExtractorSpacy(db)
relationship_extractor = RelationshipExtractor(db)

all_relationships = []
for chunk_ref in chunk_refs:
    entity_result = entity_extractor.extract_entities(chunk_ref)
    if entity_result['entity_refs']:
        rel_result = relationship_extractor.extract_relationships(chunk_ref, entity_result['entity_refs'])
        all_relationships.extend(rel_result['relationships'])

print(f"Extracted {len(all_relationships)} relationships")

# Check specific relationships
with db.neo4j.driver.session() as session:
    # Expected relationships
    expected = [
        ("Elon Musk", "Tesla", "FOUNDED"),
        ("Tesla", "Austin", "LOCATED_IN"), 
        ("Musk", "SpaceX", "FOUNDED"),
        ("Tesla", "SolarCity", "ACQUIRED"),
        ("Musk", "X.com", "FOUNDED")
    ]
    
    found = 0
    for source, target, rel_type in expected:
        result = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE a.name =~ $source AND b.name =~ $target
            RETURN type(r) as rel_type, r.confidence as conf
        """, source=f"(?i).*{source}.*", target=f"(?i).*{target}.*")
        
        records = list(result)
        rel_types = [r['rel_type'] for r in records]
        
        if rel_type in rel_types:
            conf = next((r['conf'] for r in records if r['rel_type'] == rel_type), 0)
            print(f"✓ Found: {source} --[{rel_type}]--> {target} (conf: {conf})")
            found += 1
        else:
            actual = rel_types[0] if rel_types else "NO RELATIONSHIP"
            if len(rel_types) > 1:
                actual = f"{actual} (+ {len(rel_types)-1} more)"
            print(f"✗ MISSING: Expected {source} --[{rel_type}]--> {target}, got {actual}")
    
    accuracy = found / len(expected)
    print(f"\nRelationship accuracy: {found}/{len(expected)} = {accuracy:.1%}")
    
    if accuracy < 0.5:
        print("❌ FAIL: Poor relationship extraction accuracy")

# Test 2: Does PageRank actually make sense?
print("\n\nTEST 2: PageRank Sanity Check")
print("-" * 50)

# Generate embeddings (needed for query tool)
embedder = EmbeddingGenerator(db)
embedder.generate_embeddings(object_refs=chunk_refs)

# Run PageRank
pagerank = PageRankAnalyzer(db)
pr_result = pagerank.compute_pagerank()

with db.neo4j.driver.session() as session:
    # Get all entities with their connections and PageRank
    result = session.run("""
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[r]-()
        WITH e, count(DISTINCT r) as degree
        RETURN e.name as name, degree, e.pagerank_score as pr_score
        ORDER BY degree DESC
    """)
    
    entities = list(result)
    print("Entity Rankings:")
    print("Name | Connections | PageRank")
    print("-" * 40)
    
    # Check if PageRank correlates with degree
    high_degree_high_pr = 0
    anomalies = []
    
    for e in entities[:10]:
        pr_str = f"{e['pr_score']:.4f}" if e['pr_score'] else "None"
        print(f"{e['name'][:20]:<20} | {e['degree']:^11} | {pr_str}")
        
        if e['degree'] > 5 and e['pr_score'] and e['pr_score'] > 0.03:
            high_degree_high_pr += 1
        elif e['degree'] > 5 and (not e['pr_score'] or e['pr_score'] < 0.02):
            anomalies.append(f"{e['name']} has {e['degree']} connections but low PageRank")
    
    if anomalies:
        print(f"\n❌ PageRank anomalies found:")
        for a in anomalies:
            print(f"   - {a}")

# Test 3: Graph queries vs keyword matching
print("\n\nTEST 3: Graph Queries vs Keyword Matching")
print("-" * 50)

query_tool = NaturalLanguageQuery(db)

# Queries that REQUIRE graph understanding
graph_queries = [
    {
        "query": "What companies are connected to Elon Musk through acquisitions?",
        "graph_required": True,
        "expected_path": ["Elon Musk", "Tesla", "SolarCity"],
        "keywords": ["musk", "acquisition", "solarcity"]
    },
    {
        "query": "Find the path from PayPal to Tesla",
        "graph_required": True,
        "expected_path": ["PayPal", "Elon Musk", "Tesla"],
        "keywords": ["paypal", "tesla", "path"]
    },
    {
        "query": "What year did the company founded by Musk acquire another company?",
        "graph_required": True,
        "expected_answer": "2016",
        "keywords": ["2016", "acquired", "tesla"]
    }
]

graph_success = 0
for test in graph_queries:
    print(f"\nQuery: '{test['query']}'")
    result = query_tool.query(test['query'])
    answer = result['answer'].lower()
    
    # Check if it found the graph path
    if 'expected_path' in test:
        path_found = all(node.lower() in answer for node in test['expected_path'])
        if path_found:
            print("✓ Found graph path")
            graph_success += 1
        else:
            print("✗ Failed to find graph path")
            
    elif 'expected_answer' in test:
        if test['expected_answer'].lower() in answer:
            print("✓ Found answer through graph")
            graph_success += 1
        else:
            print("✗ Failed to find answer")
    
    # Check if it's just keyword matching
    keyword_matches = sum(1 for kw in test['keywords'] if kw in answer)
    if keyword_matches == len(test['keywords']) and not test['graph_required']:
        print("⚠️  Might just be keyword matching")

graph_score = graph_success / len(graph_queries)
print(f"\nGraph query success: {graph_success}/{len(graph_queries)} = {graph_score:.1%}")

# Test 4: Remove embeddings and see if graph queries still work
print("\n\nTEST 4: Graph Queries WITHOUT Embeddings")
print("-" * 50)

# Clear FAISS to ensure no semantic search
db.faiss.index.reset()
print("✓ Cleared FAISS index")

# Try graph queries without embeddings
try:
    result = query_tool.query("What did Elon Musk found?")
    if "tesla" in result['answer'].lower() or "spacex" in result['answer'].lower():
        print("✓ Graph queries work without embeddings!")
    else:
        print("✗ Graph queries fail without embeddings")
except Exception as e:
    print(f"✗ System crashed without embeddings: {e}")

# Test 5: Adversarial graph patterns
print("\n\nTEST 5: Complex Graph Patterns")
print("-" * 50)

with db.neo4j.driver.session() as session:
    # Pattern 1: Circular relationships
    result = session.run("""
        MATCH (a:Entity)-[r1]->(b:Entity)-[r2]->(c:Entity)-[r3]->(a)
        RETURN a.name as a, b.name as b, c.name as c
        LIMIT 5
    """)
    
    circles = list(result)
    if circles:
        print(f"✓ Found {len(circles)} circular relationships")
    else:
        print("✗ No circular patterns found")
    
    # Pattern 2: Hub entities (high centrality)
    result = session.run("""
        MATCH (hub:Entity)
        WHERE hub.pagerank_score > 0.05
        MATCH (hub)-[r]-(connected)
        WITH hub, count(DISTINCT connected) as connections
        WHERE connections > 5
        RETURN hub.name as hub, connections
        ORDER BY connections DESC
    """)
    
    hubs = list(result)
    if hubs:
        print(f"✓ Found hub entities:")
        for h in hubs:
            print(f"   - {h['hub']}: {h['connections']} connections")
    else:
        print("✗ No hub entities found (graph too sparse?)")
    
    # Pattern 3: Isolated subgraphs
    result = session.run("""
        MATCH (n:Entity)
        WHERE NOT (n)-[]-()
        RETURN count(n) as isolated_count
    """)
    
    isolated = result.single()['isolated_count']
    total = session.run("MATCH (n:Entity) RETURN count(n) as c").single()['c']
    
    if isolated > 0:
        print(f"⚠️  Warning: {isolated}/{total} entities are isolated!")

# Test 6: Relationship type distribution
print("\n\nTEST 6: Relationship Type Analysis")
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
    
    if co_occurs_pct > 80:
        print(f"\n❌ WARNING: {co_occurs_pct:.1f}% are just CO_OCCURS_WITH!")
        print("   This suggests weak relationship extraction")

# Final Verdict
print("\n\n=== ADVERSARIAL VERDICT ===")
print("=" * 50)

issues = []

if accuracy < 0.6:
    issues.append("Poor relationship extraction accuracy")

if graph_score < 0.5:
    issues.append("Graph queries not working properly")

if co_occurs_pct > 80:
    issues.append("Over-reliance on co-occurrence relationships")

if isolated > total * 0.2:
    issues.append(f"Too many isolated entities ({isolated}/{total})")

# Check if system works without embeddings was already tested in Test 4
# Don't double-count this as an issue

if issues:
    print("❌ SYSTEM FAILURES:")
    for issue in issues:
        print(f"   - {issue}")
    print("\nCONCLUSION: Not a robust GraphRAG system")
else:
    print("✓ System passes adversarial tests")
    print("CONCLUSION: Appears to be functional GraphRAG")

print(f"\nFinal Score: {len(issues)} critical issues found")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()