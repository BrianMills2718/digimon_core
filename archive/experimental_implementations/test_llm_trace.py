#!/usr/bin/env python
"""Trace LLM extraction to find timeout issue."""

import os
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

print("=== TRACING LLM EXTRACTION ===\n")

# Initialize
print("1. Initializing database...")
from src.utils.database import DatabaseManager
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create test data
print("\n2. Creating test document and chunk...")
from src.models import Document, Chunk
import hashlib

# Document
doc = Document(
    id='doc_trace',
    source_path='test.txt',
    title='Test',
    content_hash=hashlib.md5(b"test").hexdigest()
)
db.sqlite.save_document(doc)

# Chunk  
chunk = Chunk(
    id='chunk_trace',
    document_id='doc_trace',
    text='Microsoft invested $10 billion in OpenAI.',
    position=0,
    start_char=0,
    end_char=41
)
db.sqlite.save_chunk(chunk)

# Neo4j chunk
with db.neo4j.driver.session() as session:
    session.run("""
        CREATE (c:Chunk {
            id: $id,
            text: $text,
            confidence: 1.0
        })
    """, id=chunk.id, text=chunk.text)

print("✓ Created test data")

# Import and create extractor
print("\n3. Creating LLM extractor...")
from src.tools.phase2.t23b_llm_extractor import LLMExtractor
llm = LLMExtractor(db)
print("✓ LLM extractor created")

# Manually trace the extraction
print("\n4. Starting extraction trace...")
chunk_ref = f"neo4j://chunk/{chunk.id}"

# Step 1: Load chunk
print("   - Loading chunk...")
start = time.time()
chunk_id = chunk_ref.split("/")[-1]
loaded_chunk = db.sqlite.get_chunk(chunk_id)
print(f"     ✓ Chunk loaded ({time.time() - start:.2f}s)")

# Step 2: Create prompt
print("   - Creating prompt...")
prompt = f'Extract entities and relationships from: "{loaded_chunk.text}"'
print(f"     ✓ Prompt created")

# Step 3: Call OpenAI
print("   - Calling OpenAI API...")
start = time.time()
try:
    # Call the actual method
    result = llm.extract_entities_and_relationships(chunk_ref)
    elapsed = time.time() - start
    print(f"     ✓ Extraction complete ({elapsed:.2f}s)")
    print(f"     - Entities: {result['entity_count']}")
    print(f"     - Relationships: {result['relationship_count']}")
except Exception as e:
    elapsed = time.time() - start
    print(f"     ✗ Extraction failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Trace complete!")