#!/usr/bin/env python
"""Test LLM extraction with proper chunk setup."""

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
from src.tools.phase2.t23b_llm_extractor import LLMExtractor
from src.models import Chunk

print("=== TESTING LLM EXTRACTION ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create a document first
from src.models import Document
import hashlib

content = 'Microsoft invested $10 billion in OpenAI. Sam Altman is the CEO of OpenAI.'
doc = Document(
    id='doc_001',
    source_path='test.txt',
    title='Test Document',
    content_hash=hashlib.md5(content.encode()).hexdigest(),
    confidence=1.0
)
db.sqlite.save_document(doc)
print(f"Created document: {doc.id}")

# Create a chunk in SQLite
chunk = Chunk(
    id='test_chunk_001',
    document_id='doc_001',
    text='Microsoft invested $10 billion in OpenAI. Sam Altman is the CEO of OpenAI.',
    position=0,
    start_char=0,
    end_char=77,
    confidence=1.0
)
db.sqlite.save_chunk(chunk)
print(f"Created chunk in SQLite: {chunk.id}")

# Create corresponding Neo4j node
with db.neo4j.driver.session() as session:
    session.run("""
        CREATE (c:Chunk {
            id: $chunk_id,
            text: $text,
            confidence: $confidence
        })
    """, chunk_id=chunk.id, text=chunk.text, confidence=chunk.confidence)
print("Created chunk in Neo4j")

# Test extraction
llm_extractor = LLMExtractor(db)

print("\nStarting LLM extraction...")
start_time = time.time()

try:
    result = llm_extractor.extract_entities_and_relationships(f"neo4j://chunk/{chunk.id}")
    elapsed = time.time() - start_time
    
    print(f"\n✓ Extraction completed in {elapsed:.2f} seconds")
    print(f"  Entities: {result['entity_count']}")
    print(f"  Relationships: {result['relationship_count']}")
    
    # Show what was extracted
    print("\nEntities extracted:")
    with db.neo4j.driver.session() as session:
        entities = session.run("""
            MATCH (e:Entity)
            RETURN e.name as name, e.entity_type as type
            ORDER BY e.name
        """)
        for e in entities:
            print(f"  - {e['name']} ({e['type']})")
    
    print("\nRelationships extracted:")
    with db.neo4j.driver.session() as session:
        rels = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            RETURN a.name as source, type(r) as rel_type, b.name as target
        """)
        for r in rels:
            print(f"  - {r['source']} --[{r['rel_type']}]--> {r['target']}")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n✗ Extraction failed after {elapsed:.2f} seconds")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()