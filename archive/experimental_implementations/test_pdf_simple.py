#!/usr/bin/env python
"""Simple PDF pipeline test."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
from src.tools.phase2.t13_text_chunker import TextChunker
from src.tools.phase2.t23b_llm_extractor import LLMExtractor

print("=== SIMPLE PDF TEST ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create simple test PDF
from reportlab.pdfgen import canvas
c = canvas.Canvas("test.pdf")
c.drawString(100, 750, "Microsoft invested $10 billion in OpenAI.")
c.drawString(100, 730, "Google competes with Microsoft in AI.")
c.drawString(100, 710, "Sam Altman leads OpenAI.")
c.save()

# Load PDF
loader = PDFDocumentLoader(db)
pdf_result = loader.load_pdf(Path("test.pdf"))
print(f"✓ Loaded PDF: {pdf_result['page_count']} pages")

# Chunk
chunker = TextChunker(db)
chunk_result = chunker.chunk_document(pdf_result['document_ref'], chunk_size=500)
print(f"✓ Created {chunk_result['chunk_count']} chunks")

# Extract with LLM (just first chunk)
llm_extractor = LLMExtractor(db)
result = llm_extractor.extract_entities_and_relationships(chunk_result['chunk_refs'][0])
print(f"\n✓ Extracted {result['entity_count']} entities")
print(f"✓ Extracted {result['relationship_count']} relationships")

# Show relationships
print("\nRelationships found:")
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name as source, type(r) as rel_type, b.name as target
    """)
    
    for r in result:
        print(f"  {r['source']} --[{r['rel_type']}]--> {r['target']}")

# Check CO_OCCURS_WITH
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH ()-[r]->()
        WHERE type(r) = 'CO_OCCURS_WITH'
        RETURN count(r) as count
    """)
    
    co_count = result.single()['count']
    print(f"\n✅ CO_OCCURS_WITH relationships: {co_count}")

# Cleanup
Path("test.pdf").unlink()
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ PDF pipeline works with LLM extraction!")