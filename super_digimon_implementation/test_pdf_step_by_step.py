#!/usr/bin/env python
"""Test PDF pipeline step by step with timing."""

import os
import sys
import time
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

print("=== STEP BY STEP PDF TEST ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create test PDF
print("1. Creating test PDF...")
import create_test_pdf
create_test_pdf.create_research_paper()

# Load PDF
print("\n2. Loading PDF...")
start = time.time()
loader = PDFDocumentLoader(db)
pdf_result = loader.load_pdf(Path("graphrag_research_paper.pdf"))
print(f"   ✓ Loaded in {time.time() - start:.2f}s - {pdf_result['page_count']} pages")

# Chunk text
print("\n3. Chunking text...")
start = time.time()
chunker = TextChunker(db)
chunk_result = chunker.chunk_document(
    pdf_result['document_ref'],
    chunk_size=500,
    overlap=50
)
print(f"   ✓ Chunked in {time.time() - start:.2f}s - {chunk_result['chunk_count']} chunks")

# Process first chunk with LLM
print("\n4. Processing first chunk with LLM...")
llm_extractor = LLMExtractor(db)

# Get chunk text to show
chunk_ref = chunk_result['chunk_refs'][0]
chunk_id = chunk_ref.split("/")[-1]
chunk = db.sqlite.get_chunk(chunk_id)
print(f"\nChunk text preview:")
print(f'"{chunk.text[:100]}..."')

start = time.time()
try:
    result = llm_extractor.extract_entities_and_relationships(chunk_ref)
    elapsed = time.time() - start
    print(f"\n   ✓ Extracted in {elapsed:.2f}s")
    print(f"   - Entities: {result['entity_count']}")
    print(f"   - Relationships: {result['relationship_count']}")
    
    # Show what was extracted
    with db.neo4j.driver.session() as session:
        entities = session.run("""
            MATCH (e:Entity)
            RETURN e.name, e.entity_type
            ORDER BY e.name
            LIMIT 10
        """)
        print("\nEntities found:")
        for e in entities:
            print(f"   - {e['e.name']} ({e['e.entity_type']})")
            
        rels = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            RETURN a.name as source, type(r) as rel_type, b.name as target
            LIMIT 10
        """)
        print("\nRelationships found:")
        for r in rels:
            print(f"   - {r['source']} --[{r['rel_type']}]--> {r['target']}")
        
except Exception as e:
    elapsed = time.time() - start
    print(f"\n   ✗ Failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
Path("graphrag_research_paper.pdf").unlink()
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Test complete!")