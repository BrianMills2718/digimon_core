#!/usr/bin/env python
"""Test LLM extraction timeout issue."""

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

print("=== TESTING LLM EXTRACTION TIMEOUT ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create a simple chunk
with db.neo4j.driver.session() as session:
    result = session.run("""
        CREATE (c:Chunk {
            id: 'chunk_test',
            text: 'Microsoft invested $10 billion in OpenAI.',
            confidence: 1.0
        })
        RETURN c.id as chunk_id
    """)
    chunk_id = result.single()['chunk_id']
    print(f"Created chunk: {chunk_id}")

# Test extraction with timing
llm_extractor = LLMExtractor(db)

print("Starting LLM extraction...")
start_time = time.time()

try:
    result = llm_extractor.extract_entities_and_relationships(f"neo4j://chunk/{chunk_id}")
    elapsed = time.time() - start_time
    
    print(f"\n✓ Extraction completed in {elapsed:.2f} seconds")
    print(f"  Entities: {result['entity_count']}")
    print(f"  Relationships: {result['relationship_count']}")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n✗ Extraction failed after {elapsed:.2f} seconds")
    print(f"  Error: {e}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()