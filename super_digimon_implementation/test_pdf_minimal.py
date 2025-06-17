#!/usr/bin/env python
"""Minimal PDF test - just load, chunk, and extract from one chunk."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

# Create simple PDF with minimal content
from reportlab.pdfgen import canvas
c = canvas.Canvas("minimal_test.pdf")
c.drawString(100, 750, "Microsoft invested $10 billion in OpenAI in 2023.")
c.save()
print("Created minimal test PDF")

# Initialize
from src.utils.database import DatabaseManager
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Load PDF
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
loader = PDFDocumentLoader(db)
pdf_result = loader.load_pdf(Path("minimal_test.pdf"))
print(f"✓ Loaded PDF: {pdf_result['page_count']} pages")

# Chunk
from src.tools.phase2.t13_text_chunker import TextChunker
chunker = TextChunker(db)
chunk_result = chunker.chunk_document(pdf_result['document_ref'], chunk_size=500)
print(f"✓ Created {chunk_result['chunk_count']} chunks")

# Extract from first chunk
from src.tools.phase2.t23b_llm_extractor import LLMExtractor
llm = LLMExtractor(db)
result = llm.extract_entities_and_relationships(chunk_result['chunk_refs'][0])
print(f"✓ Extracted {result['entity_count']} entities, {result['relationship_count']} relationships")

# Check what we got
with db.neo4j.driver.session() as session:
    # Count relationship types
    rel_counts = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    print("\nRelationships:")
    total = 0
    co_occurs = 0
    for r in rel_counts:
        print(f"  {r['rel_type']}: {r['count']}")
        total += r['count']
        if r['rel_type'] == 'CO_OCCURS_WITH':
            co_occurs = r['count']
    
    co_pct = (co_occurs / total * 100) if total > 0 else 0
    print(f"\nCO_OCCURS_WITH: {co_pct:.1f}%")

# Cleanup
Path("minimal_test.pdf").unlink()
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Minimal PDF test complete!")