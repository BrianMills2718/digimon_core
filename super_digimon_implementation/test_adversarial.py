#!/usr/bin/env python
"""Adversarial test to prove the system doesn't actually work."""

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
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== ADVERSARIAL TEST: Trying to Break the System ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear everything
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create a complex test PDF with interconnected information
print("1. Creating complex test PDF...")
test_pdf = Path("adversarial_test.pdf")
c = canvas.Canvas(str(test_pdf), pagesize=letter)
width, height = letter

# Page 1: Complex relationships
c.setFont("Helvetica-Bold", 14)
c.drawString(50, height - 50, "The Celestial Council: A Complex Network")

c.setFont("Helvetica", 11)
y = height - 100
content = [
    "",
    "The Celestial Council was founded in 1823 by Aurora Starweaver and Orion Nightfall.",
    "Aurora's daughter, Luna Starweaver, later married Orion's son, Sol Nightfall, in 1855.",
    "Their child, Nova Starweaver-Nightfall, became the third Grand Celestial in 1878.",
    "",
    "The Council's main rivals were the Void Syndicate, led by Umbra Darkvoid.",
    "Umbra's lieutenant, Shadow Whisper, infiltrated the Council in 1856 by befriending Luna.",
    "This led to the Great Betrayal of 1857, where Shadow stole the Cosmic Codex.",
    "",
    "The Codex was recovered in 1860 by Comet Swiftblade, Nova's mentor.",
    "Comet discovered that Shadow was actually Aurora's estranged brother, Eclipse Starweaver.",
    "Eclipse had changed his name after a dispute over the Council's founding principles.",
    "",
    "In 1882, Nova negotiated peace with Eclipse's daughter, Twilight Whisper.",
    "Twilight revealed that the Void Syndicate was created to protect a dangerous artifact.",
    "This artifact, the Null Crystal, could unmake reality if misused.",
    ""
]

for line in content:
    c.drawString(50, y, line)
    y -= 18

c.showPage()

# Page 2: More complex information
c.setFont("Helvetica-Bold", 14)
c.drawString(50, height - 50, "The Null Crystal Conspiracy")

c.setFont("Helvetica", 11)
y = height - 100
content2 = [
    "",
    "The Null Crystal was originally discovered by Cosmos Voidwalker in 1799.",
    "Cosmos was Aurora Starweaver's grandfather and Umbra Darkvoid's mentor.",
    "He split the crystal into seven fragments and hid them across the realm.",
    "",
    "Fragment locations were known only to the Seven Guardians:",
    "1. Aurora Starweaver (deceased 1855) - passed knowledge to Luna",
    "2. Orion Nightfall (deceased 1862) - passed knowledge to Sol", 
    "3. Umbra Darkvoid (deceased 1881) - passed knowledge to Shadow/Eclipse",
    "4. Cosmos Voidwalker (deceased 1820) - knowledge lost",
    "5. Stellar Brightsun (deceased 1870) - passed knowledge to her son Photon",
    "6. Nebula Mistborn (alive in 1882) - location unknown",
    "7. Galaxy Eternus (immortal) - refuses to share knowledge",
    "",
    "By 1882, only 4 fragment locations were known. Nova and Twilight formed",
    "an alliance to prevent the crystal's reassembly by extremist factions.",
]

for line in content2:
    c.drawString(50, y, line)
    y -= 18

c.save()
print("✓ Created complex PDF with interconnected entities and relationships")

try:
    # Load the PDF
    print("\n2. Loading PDF...")
    loader = PDFDocumentLoader(db)
    pdf_result = loader.load_pdf(test_pdf)
    print(f"✓ Loaded: {pdf_result['document_ref']}")
    
    # Chunk it
    print("\n3. Chunking...")
    chunker = TextChunker(db)
    chunk_result = chunker.chunk_document(pdf_result['document_ref'], chunk_size=300, overlap=50)
    print(f"✓ Created {chunk_result['chunk_count']} chunks")
    
    # Extract entities
    print("\n4. Extracting entities...")
    extractor = EntityExtractorSpacy(db)
    all_entities = []
    
    for i, chunk_ref in enumerate(chunk_result['chunk_refs']):
        result = extractor.extract_entities(chunk_ref)
        all_entities.extend(result['entity_refs'])
        print(f"  Chunk {i+1}: {result['entity_count']} entities")
    
    unique_entities = list(set(all_entities))
    print(f"✓ Total unique entities: {len(unique_entities)}")
    
    # Generate embeddings
    print("\n5. Generating embeddings...")
    embedder = EmbeddingGenerator(db)
    
    # Embed everything
    chunk_embed = embedder.generate_embeddings(object_refs=chunk_result['chunk_refs'])
    entity_embed = embedder.generate_embeddings(object_refs=unique_entities[:50])
    
    print(f"✓ Total embeddings: {db.faiss.index.ntotal}")
    
    # Run PageRank
    print("\n6. Running PageRank...")
    pagerank = PageRankAnalyzer(db)
    pr_result = pagerank.calculate_pagerank()
    print(f"✓ PageRank processed: {pr_result['entities_processed']} entities")
    
    # ADVERSARIAL TESTS
    print("\n\n=== ADVERSARIAL TESTS ===")
    
    # Test 1: Check if entities are actually stored with relationships
    print("\n❓ Test 1: Are entities actually stored in Neo4j?")
    with db.neo4j.driver.session() as session:
        # Count entities
        result = session.run("MATCH (n:Entity) RETURN count(n) as count")
        entity_count = result.single()["count"]
        print(f"  Entities in Neo4j: {entity_count}")
        
        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()["count"]
        print(f"  Relationships in Neo4j: {rel_count}")
        
        # Get sample entities
        result = session.run("MATCH (n:Entity) RETURN n.name as name, n.entity_type as type LIMIT 5")
        print("  Sample entities:")
        for record in result:
            print(f"    - {record['name']} ({record['type']})")
    
    # Test 2: Check if PageRank actually computed scores
    print("\n❓ Test 2: Did PageRank actually compute meaningful scores?")
    if pr_result['top_entities']:
        print("  Top entities by PageRank:")
        for i, ent in enumerate(pr_result['top_entities'][:5]):
            print(f"    {i+1}. {ent['name']}: {ent['score']}")
    else:
        print("  ❌ No PageRank scores computed!")
    
    # Test 3: Complex relationship queries
    print("\n❓ Test 3: Testing complex relationship queries...")
    query_tool = NaturalLanguageQuery(db)
    
    complex_queries = [
        "Who founded the Celestial Council?",
        "What is the relationship between Aurora Starweaver and Eclipse Starweaver?",
        "Who knows the location of the Null Crystal fragments?",
        "What happened in the Great Betrayal of 1857?",
        "Who is Shadow Whisper really?",
        "How many fragments was the Null Crystal split into?",
        "What is the connection between Cosmos Voidwalker and Umbra Darkvoid?"
    ]
    
    for query in complex_queries:
        print(f"\n  Query: '{query}'")
        result = query_tool.query(query, top_k=5)
        
        # Analyze the answer
        answer = result['answer']
        
        # Check if it's just keyword matching
        if len(result['results']) == 0:
            print("    ❌ No results found at all!")
        elif "No relevant information found" in answer:
            print("    ❌ System couldn't find information")
        elif "Based on the available information:" in answer:
            print("    ⚠️  Template answer (not LLM)")
        else:
            # Check if answer is actually correct
            print(f"    Answer: {answer[:150]}...")
            
            # Verify correctness
            if "founded" in query.lower() and "aurora" in answer.lower() and "orion" in answer.lower():
                print("    ✓ Correct answer")
            elif "shadow whisper" in query.lower() and "eclipse" in answer.lower():
                print("    ✓ Correct answer") 
            elif "fragments" in query.lower() and "seven" in answer.lower():
                print("    ✓ Correct answer")
            else:
                print("    ❓ Answer may be incorrect or incomplete")
    
    # Test 4: Check entity extraction quality
    print("\n❓ Test 4: Entity extraction quality check...")
    with db.neo4j.driver.session() as session:
        # Check if complex names were extracted
        result = session.run("""
            MATCH (n:Entity) 
            WHERE n.name CONTAINS 'Starweaver' OR n.name CONTAINS 'Nightfall'
            RETURN n.name as name, n.entity_type as type
            ORDER BY n.name
        """)
        
        family_members = list(result)
        print(f"  Found {len(family_members)} Starweaver/Nightfall family members:")
        for record in family_members:
            print(f"    - {record['name']} ({record['type']})")
        
        # Check years
        result = session.run("""
            MATCH (n:Entity)
            WHERE n.name =~ '\\d{4}'
            RETURN n.name as name, n.entity_type as type
            LIMIT 10
        """)
        
        years = list(result)
        print(f"\n  Found {len(years)} year entities:")
        for record in years:
            print(f"    - {record['name']} ({record['type']})")
    
    # Test 5: Cross-reference check
    print("\n❓ Test 5: Can the system find cross-references?")
    
    # This should find Eclipse = Shadow connection
    result = query_tool.query(
        "Find all information about Eclipse Starweaver and Shadow Whisper",
        top_k=10
    )
    
    print(f"  Results: {len(result['results'])}")
    print(f"  Answer preview: {result['answer'][:200]}...")
    
    # Final verdict
    print("\n\n=== ADVERSARIAL TEST VERDICT ===")
    
    issues = []
    
    if entity_count < 20:
        issues.append("Very few entities extracted from rich text")
    
    if rel_count == 0:
        issues.append("NO relationships created between entities")
    
    if not pr_result['top_entities']:
        issues.append("PageRank didn't compute any scores")
    
    # Check if complex relationships were found
    with db.neo4j.driver.session() as session:
        result = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE a.name CONTAINS 'Aurora' AND b.name CONTAINS 'Luna'
            RETURN count(r) as count
        """)
        family_rels = result.single()["count"]
        
        if family_rels == 0:
            issues.append("Failed to extract family relationships")
    
    if issues:
        print("❌ SYSTEM FAILURES DETECTED:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✓ System appears to be working (but may have limitations)")
    
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    if test_pdf.exists():
        test_pdf.unlink()
    with db.neo4j.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    db.close()