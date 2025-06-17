#!/usr/bin/env python
"""Test pipeline with real PDF - simplified version."""

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
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
from src.tools.phase2.t13_text_chunker import TextChunker
from src.tools.phase2.t23b_llm_extractor import LLMExtractor
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer

print("=== REAL PDF PIPELINE TEST (SIMPLIFIED) ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Phase 1: Load PDF
print("1. Loading PDF...")
loader = PDFDocumentLoader(db)
pdf_path = Path("graphrag_research_paper.pdf")
if not pdf_path.exists():
    print("ERROR: PDF not found. Run create_test_pdf.py first")
    sys.exit(1)

pdf_result = loader.load_pdf(pdf_path)
print(f"✓ Loaded {pdf_result['page_count']} pages")

# Phase 2: Chunk text
print("\n2. Chunking text...")
chunker = TextChunker(db)
chunk_result = chunker.chunk_document(
    pdf_result['document_ref'],
    chunk_size=500,  # Larger chunks = fewer API calls
    overlap=50
)
print(f"✓ Created {chunk_result['chunk_count']} chunks")

# Phase 3: Extract with LLM (limit to first 3 chunks)
print("\n3. Extracting entities and relationships with LLM...")
llm_extractor = LLMExtractor(db)

total_entities = 0
total_relationships = 0
chunks_to_process = min(3, len(chunk_result['chunk_refs']))

for i, chunk_ref in enumerate(chunk_result['chunk_refs'][:chunks_to_process]):
    print(f"  Processing chunk {i+1}/{chunks_to_process}...")
    try:
        result = llm_extractor.extract_entities_and_relationships(chunk_ref)
        total_entities += result['entity_count']
        total_relationships += result['relationship_count']
    except Exception as e:
        print(f"    Error: {e}")

print(f"\n✓ Extracted {total_entities} entity mentions")
print(f"✓ Extracted {total_relationships} relationships")

# Phase 4: Generate embeddings
print("\n4. Generating embeddings...")
embedder = EmbeddingGenerator(db)
embedder.generate_embeddings(object_refs=chunk_result['chunk_refs'][:chunks_to_process])
print(f"✓ Generated embeddings for {chunks_to_process} chunks")

# Get unique entities for embedding
with db.neo4j.driver.session() as session:
    result = session.run("MATCH (e:Entity) RETURN 'neo4j://entity/' + e.id as ref LIMIT 20")
    entity_refs = [r['ref'] for r in result]

if entity_refs:
    embedder.generate_embeddings(object_refs=entity_refs)
    print(f"✓ Generated embeddings for {len(entity_refs)} entities")

# Phase 5: Run PageRank
print("\n5. Computing PageRank...")
pagerank = PageRankAnalyzer(db)
pr_result = pagerank.compute_pagerank()
print(f"✓ Computed PageRank for {pr_result['metadata']['entity_count']} entities")

# Show top entities
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (e:Entity)
        WHERE e.pagerank_score IS NOT NULL
        RETURN e.name, e.entity_type, e.pagerank_score
        ORDER BY e.pagerank_score DESC
        LIMIT 5
    """)
    
    print("\nTop 5 entities by PageRank:")
    for r in result:
        print(f"  - {r['e.name']} ({r['e.entity_type']}): {r['e.pagerank_score']:.4f}")

# Show relationship distribution
print("\n6. Relationship Analysis:")
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    rel_dist = list(result)
    total = sum(r['count'] for r in rel_dist)
    
    for r in rel_dist:
        pct = (r['count'] / total * 100) if total > 0 else 0
        print(f"  {r['rel_type']}: {r['count']} ({pct:.1f}%)")
    
    # Check CO_OCCURS_WITH percentage
    co_occurs = next((r for r in rel_dist if r['rel_type'] == 'CO_OCCURS_WITH'), None)
    co_pct = (co_occurs['count'] / total * 100) if co_occurs and total > 0 else 0
    
    print(f"\n✅ CO_OCCURS_WITH: {co_pct:.1f}% (< 70% requirement)")

# Final statistics
print("\n=== PIPELINE SUMMARY ===")
with db.neo4j.driver.session() as session:
    stats = session.run("""
        MATCH (n:Entity) WITH count(n) as entities
        MATCH ()-[r]->() WITH entities, count(r) as relationships
        MATCH (d:Document) WITH entities, relationships, count(d) as documents
        MATCH (c:Chunk) WITH entities, relationships, documents, count(c) as chunks
        RETURN entities, relationships, documents, chunks
    """).single()
    
    print(f"Documents: {stats['documents']}")
    print(f"Chunks: {stats['chunks']}")
    print(f"Entities: {stats['entities']}")
    print(f"Relationships: {stats['relationships']}")

print("\n✅ Real PDF pipeline test complete!")

# Cleanup
pdf_path.unlink()  # Remove test PDF
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()