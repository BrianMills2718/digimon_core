#!/usr/bin/env python
"""Demonstration of the working GraphRAG system."""

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

print("=== SUPER-DIGIMON GRAPHRAG DEMONSTRATION ===")
print("Showing the complete working system\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create demo PDF
print("1. Creating demonstration PDF...")
demo_pdf = Path("graphrag_demo.pdf")
c = canvas.Canvas(str(demo_pdf), pagesize=letter)
width, height = letter

c.setFont("Helvetica-Bold", 16)
c.drawString(50, height - 50, "The AI Revolution: Key Players and Relationships")

c.setFont("Helvetica", 12)
y = height - 100
content = [
    "",
    "OpenAI, founded by Elon Musk and Sam Altman in 2015, revolutionized AI with GPT.",
    "The company is based in San Francisco and created ChatGPT in 2022.",
    "",
    "Anthropic was founded in 2021 by former OpenAI researchers Dario and Daniela Amodei.",
    "They created Claude to compete with ChatGPT, focusing on AI safety.",
    "",
    "Google acquired DeepMind in 2014 for $500 million. DeepMind, based in London,",
    "was founded by Demis Hassabis and created AlphaGo, which beat the world Go champion.",
    "",
    "Microsoft invested $10 billion in OpenAI in 2023 and integrated GPT into Bing.",
    "This partnership put Microsoft in direct competition with Google in AI search.",
    "",
    "The AI race intensified in 2023 as these companies competed for dominance."
]

for line in content:
    c.drawString(50, y, line)
    y -= 20

c.save()
print("✓ Created demo PDF\n")

# Process through pipeline
print("2. Processing PDF through GraphRAG pipeline...")

# Load PDF
loader = PDFDocumentLoader(db)
pdf_result = loader.load_pdf(demo_pdf)
print(f"✓ PDF loaded: {pdf_result['page_count']} pages")

# Chunk text
chunker = TextChunker(db)
chunk_result = chunker.chunk_document(pdf_result['document_ref'], chunk_size=300, overlap=50)
print(f"✓ Created {chunk_result['chunk_count']} chunks")

# Extract entities and relationships
entity_extractor = EntityExtractorSpacy(db)
relationship_extractor = RelationshipExtractor(db)

all_entities = []
total_relationships = 0

for chunk_ref in chunk_result['chunk_refs']:
    # Extract entities
    entity_result = entity_extractor.extract_entities(chunk_ref)
    entities = entity_result['entity_refs']
    all_entities.extend(entities)
    
    # Extract relationships
    if entities:
        rel_result = relationship_extractor.extract_relationships(chunk_ref, entities)
        total_relationships += rel_result['relationship_count']

unique_entities = list(set(all_entities))
print(f"✓ Extracted {len(unique_entities)} entities")
print(f"✓ Extracted {total_relationships} relationships")

# Generate embeddings
embedder = EmbeddingGenerator(db)
embedder.generate_embeddings(object_refs=chunk_result['chunk_refs'])
embedder.generate_embeddings(object_refs=unique_entities[:50])
print(f"✓ Generated {db.faiss.index.ntotal} embeddings")

# Run PageRank
pagerank = PageRankAnalyzer(db)
pr_result = pagerank.compute_pagerank()
print(f"✓ Computed PageRank for {pr_result['metadata']['entity_count']} entities\n")

# Show graph structure
print("3. Graph Structure Analysis:")
with db.neo4j.driver.session() as session:
    # Top entities by PageRank
    result = session.run("""
        MATCH (e:Entity)
        WHERE e.pagerank_score IS NOT NULL
        RETURN e.name as name, e.entity_type as type, e.pagerank_score as score
        ORDER BY e.pagerank_score DESC
        LIMIT 5
    """)
    
    print("\nTop entities by PageRank:")
    for record in result:
        print(f"  - {record['name']} ({record['type']}): {record['score']:.4f}")
    
    # Relationship summary
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    print("\nRelationship types:")
    for record in result:
        print(f"  - {record['rel_type']}: {record['count']}")

# Demonstrate GraphRAG capabilities
print("\n4. GraphRAG Query Demonstrations:")
query_tool = NaturalLanguageQuery(db)

demo_queries = [
    "Who founded OpenAI?",
    "What is the relationship between Microsoft and OpenAI?",
    "Which companies are competing in the AI space?",
    "What did Google acquire and when?",
    "How are Anthropic and OpenAI connected?",
    "Tell me about the AI race in 2023"
]

for query in demo_queries:
    print(f"\n❓ {query}")
    result = query_tool.query(query, top_k=5)
    answer = result['answer']
    
    # Show first 200 chars of answer
    if len(answer) > 200:
        print(f"💡 {answer[:200]}...")
    else:
        print(f"💡 {answer}")

# Show multi-hop reasoning
print("\n5. Multi-hop Graph Reasoning:")
with db.neo4j.driver.session() as session:
    # Find connections between companies
    result = session.run("""
        MATCH (a:Entity)-[r1*1..2]-(b:Entity)
        WHERE a.name =~ '(?i).*microsoft.*' AND b.name =~ '(?i).*google.*'
        AND ALL(rel IN r1 WHERE type(rel) <> 'CO_OCCURS_WITH')
        RETURN [n in nodes([a] + nodes(r1) + [b]) | n.name] as path
        LIMIT 3
    """)
    
    paths = list(result)
    if paths:
        print("\nConnections between Microsoft and Google:")
        for i, p in enumerate(paths, 1):
            print(f"  Path {i}: {' -> '.join(p['path'])}")
    
    # Find all founded relationships
    result = session.run("""
        MATCH (founder:Entity)-[:FOUNDED]->(company:Entity)
        RETURN founder.name as founder, company.name as company
        ORDER BY company.name
    """)
    
    founded = list(result)
    if founded:
        print("\nFounder relationships:")
        for f in founded:
            print(f"  - {f['founder']} founded {f['company']}")

# Summary
print("\n6. System Summary:")
with db.neo4j.driver.session() as session:
    stats = session.run("""
        MATCH (n:Entity) WITH count(n) as nodes
        MATCH ()-[r]->() WITH nodes, count(r) as edges
        MATCH (e:Entity) WHERE e.pagerank_score IS NOT NULL WITH nodes, edges, count(e) as ranked
        RETURN nodes, edges, ranked
    """).single()
    
    print(f"✅ Graph Statistics:")
    print(f"   - Entities: {stats['nodes']}")
    print(f"   - Relationships: {stats['edges']}")
    print(f"   - PageRank computed: {stats['ranked']}")
    print(f"   - Embeddings: {db.faiss.index.ntotal}")
    
print("\n✨ GraphRAG system fully operational!")

# Cleanup
if demo_pdf.exists():
    demo_pdf.unlink()
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()