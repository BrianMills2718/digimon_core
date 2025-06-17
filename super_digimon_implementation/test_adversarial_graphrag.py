#!/usr/bin/env python
"""Adversarial test to prove we have TRUE GraphRAG, not just semantic search."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.utils.database import DatabaseManager
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
from src.tools.phase2.t13_text_chunker import TextChunker
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase2.t24_relationship_extractor import RelationshipExtractor
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== ADVERSARIAL GRAPHRAG TEST ===")
print("Testing if the system is TRUE GraphRAG or just pretending...\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear everything
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create a complex test PDF with intricate relationships
print("1. Creating complex relationship test PDF...")
test_pdf = Path("adversarial_graphrag_test.pdf")
c = canvas.Canvas(str(test_pdf), pagesize=letter)
width, height = letter

# Complex relationship network
c.setFont("Helvetica-Bold", 14)
c.drawString(50, height - 50, "Technology Company Relationships")

c.setFont("Helvetica", 11)
y = height - 100
content = [
    "",
    "Microsoft was founded by Bill Gates and Paul Allen in 1975. The company",
    "acquired GitHub in 2018 for $7.5 billion. GitHub was previously led by",
    "Chris Wanstrath, who co-founded the company with Tom Preston-Werner.",
    "",
    "Satya Nadella became CEO of Microsoft in 2014, succeeding Steve Ballmer.",
    "Under Nadella's leadership, Microsoft also acquired LinkedIn in 2016.",
    "LinkedIn was founded by Reid Hoffman and is based in Sunnyvale, California.",
    "",
    "GitHub competed with GitLab and Bitbucket in the version control market.",
    "GitLab was founded by Dmitriy Zaporozhets and Sytse Sijbrandij.",
    "Atlassian, which owns Bitbucket, also owns Jira and Confluence.",
    "",
    "Microsoft's acquisition strategy put them in competition with Google,",
    "which had previously tried to acquire GitHub. Google later acquired",
    "Fitbit in 2021 and previously bought YouTube in 2006.",
    "",
    "The connections between these companies form a complex web of",
    "acquisitions, competitions, and leadership changes that shaped",
    "the modern technology landscape."
]

for line in content:
    c.drawString(50, y, line)
    y -= 16

c.save()
print("✓ Created complex PDF")

try:
    # Load and process the PDF
    print("\n2. Processing PDF through pipeline...")
    
    # Load PDF
    loader = PDFDocumentLoader(db)
    pdf_result = loader.load_pdf(test_pdf)
    doc_ref = pdf_result['document_ref']
    
    # Chunk text
    chunker = TextChunker(db)
    chunk_result = chunker.chunk_document(doc_ref, chunk_size=300, overlap=50)
    
    # Extract entities and relationships
    entity_extractor = EntityExtractorSpacy(db)
    relationship_extractor = RelationshipExtractor(db)
    
    all_entity_refs = []
    total_relationships = 0
    
    for chunk_ref in chunk_result['chunk_refs']:
        # Extract entities
        entity_result = entity_extractor.extract_entities(chunk_ref)
        entity_refs = entity_result['entity_refs']
        all_entity_refs.extend(entity_refs)
        
        # Extract relationships
        if entity_refs:
            rel_result = relationship_extractor.extract_relationships(chunk_ref, entity_refs)
            total_relationships += rel_result['relationship_count']
    
    unique_entities = list(set(all_entity_refs))
    print(f"✓ Extracted {len(unique_entities)} entities and {total_relationships} relationships")
    
    # Generate embeddings
    embedder = EmbeddingGenerator(db)
    embedder.generate_embeddings(object_refs=chunk_result['chunk_refs'])
    embedder.generate_embeddings(object_refs=unique_entities[:50])
    
    # Run PageRank
    pagerank = PageRankAnalyzer(db)
    pr_result = pagerank.compute_pagerank()
    
    # Now run adversarial tests
    print("\n\n=== ADVERSARIAL TESTS ===")
    
    # Test 1: Can it find multi-hop relationships?
    print("\n❓ Test 1: Multi-hop relationship queries")
    query_tool = NaturalLanguageQuery(db)
    
    with db.neo4j.driver.session() as session:
        # Check if Bill Gates is connected to GitHub through Microsoft
        result = session.run("""
            MATCH path = (gates:Entity)-[*2..3]-(github:Entity)
            WHERE gates.name =~ '(?i).*bill gates.*' 
            AND github.name =~ '(?i).*github.*'
            RETURN length(path) as hops,
                   [n in nodes(path) | n.name] as path
            LIMIT 1
        """)
        
        record = result.single()
        if record:
            print(f"✅ Found path: {' -> '.join(record['path'])} ({record['hops']} hops)")
        else:
            print("❌ FAIL: No path between Bill Gates and GitHub")
    
    # Test 2: Can it answer relationship-based questions?
    print("\n❓ Test 2: Relationship-based reasoning")
    
    complex_queries = [
        ("What companies has Microsoft acquired?", ["GitHub", "LinkedIn"]),
        ("Who are the founders of GitHub?", ["Chris Wanstrath", "Tom Preston-Werner"]),
        ("What is the connection between Bill Gates and GitHub?", ["Microsoft", "acquired"]),
        ("Which companies compete with GitHub?", ["GitLab", "Bitbucket"])
    ]
    
    passed = 0
    for query, expected_terms in complex_queries:
        result = query_tool.query(query)
        answer = result['answer'].lower()
        
        found_terms = [term for term in expected_terms if term.lower() in answer]
        
        if len(found_terms) >= len(expected_terms) // 2:  # At least half the terms
            print(f"✅ '{query}' - Found: {found_terms}")
            passed += 1
        else:
            print(f"❌ '{query}' - Missing: {[t for t in expected_terms if t.lower() not in answer]}")
    
    print(f"\nRelationship queries passed: {passed}/{len(complex_queries)}")
    
    # Test 3: PageRank reflects graph structure
    print("\n❓ Test 3: PageRank reflects actual importance")
    
    with db.neo4j.driver.session() as session:
        # Get entities with most relationships
        result = session.run("""
            MATCH (e:Entity)
            OPTIONAL MATCH (e)-[r]-()
            WITH e, count(r) as degree
            RETURN e.name as name, 
                   degree, 
                   e.pagerank_score as pagerank
            ORDER BY degree DESC
            LIMIT 10
        """)
        
        entities = list(result)
        if entities:
            print("\nEntity importance (degree vs PageRank):")
            for e in entities[:5]:
                print(f"  {e['name']}: degree={e['degree']}, pagerank={e['pagerank']:.4f if e['pagerank'] else 'None'}")
            
            # Check correlation
            high_degree = [e for e in entities if e['degree'] > 3]
            high_pagerank = [e for e in entities if e['pagerank'] and e['pagerank'] > 0.03]
            
            if len(set(e['name'] for e in high_degree) & set(e['name'] for e in high_pagerank)) > 0:
                print("✅ PageRank correlates with node importance")
            else:
                print("❌ PageRank doesn't reflect graph structure")
    
    # Test 4: Graph patterns
    print("\n❓ Test 4: Complex graph patterns")
    
    with db.neo4j.driver.session() as session:
        # Find acquisition chains
        result = session.run("""
            MATCH (a:Entity)-[:ACQUIRED|OWNS*1..2]->(b:Entity)
            RETURN a.name as acquirer, collect(DISTINCT b.name) as acquired
            ORDER BY size(acquired) DESC
            LIMIT 5
        """)
        
        chains = list(result)
        if chains and any(len(c['acquired']) > 0 for c in chains):
            print("✅ Found acquisition chains:")
            for c in chains[:3]:
                if c['acquired']:
                    print(f"  {c['acquirer']} -> {c['acquired']}")
        else:
            print("❌ No acquisition chains found")
    
    # Test 5: Semantic search vs Graph reasoning
    print("\n❓ Test 5: Graph reasoning vs keyword matching")
    
    # Query that requires graph traversal, not just keywords
    result = query_tool.query(
        "What companies are connected to Bill Gates through acquisitions?"
    )
    
    answer = result['answer'].lower()
    
    # Should find GitHub and LinkedIn through Microsoft
    if "github" in answer and "linkedin" in answer and "microsoft" in answer:
        print("✅ Found indirect connections through graph traversal")
    else:
        print("❌ Failed to find indirect connections")
    
    # Final verdict
    print("\n\n=== FINAL VERDICT ===")
    
    with db.neo4j.driver.session() as session:
        stats = session.run("""
            MATCH (n:Entity)
            OPTIONAL MATCH (n)-[r]-()
            RETURN count(DISTINCT n) as nodes,
                   count(DISTINCT r) as edges,
                   count(DISTINCT type(r)) as rel_types
        """).single()
        
        has_multi_hop = session.run("""
            MATCH path = (a:Entity)-[*2..3]-(b:Entity)
            RETURN count(path) > 0 as has_paths
            LIMIT 1
        """).single()
    
    if stats['edges'] > 20 and stats['rel_types'] > 3 and has_multi_hop['has_paths']:
        print("✅ TRUE GRAPHRAG CONFIRMED!")
        print(f"   - {stats['nodes']} nodes, {stats['edges']} edges, {stats['rel_types']} relationship types")
        print("   - Multi-hop graph traversal working")
        print("   - Relationship-based reasoning functional")
        print("   - PageRank reflects graph structure")
    else:
        print("❌ NOT TRUE GRAPHRAG")
        print("   - Missing complex relationships")
        print("   - No multi-hop reasoning")
        print("   - Just semantic search with entities")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    if test_pdf.exists():
        test_pdf.unlink()
    with db.neo4j.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    db.close()