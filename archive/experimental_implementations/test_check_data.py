#!/usr/bin/env python
"""Check what data is actually stored and searchable."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Create more meaningful test data
print("1. Creating test data with better context...")

# Clear everything first
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create document
doc = Document(
    title="AI Companies Overview",
    source_path="test.pdf", 
    content_hash="test123",
    metadata={"type": "research"}
)
db.sqlite.save_document(doc)

# Create chunks with clear information
chunks_data = [
    "OpenAI is an artificial intelligence research company that created GPT-4, their most advanced language model. The company was founded in 2015 and is headquartered in San Francisco.",
    "Sam Altman serves as the CEO of OpenAI. Under his leadership, OpenAI has developed groundbreaking AI systems including GPT-3, GPT-4, and DALL-E.",
    "Anthropic is an AI safety company founded by former OpenAI researchers. The company focuses on building reliable, interpretable, and steerable AI systems.",
    "Dario Amodei and Daniela Amodei are the co-founders of Anthropic. They left OpenAI to start Anthropic with a focus on AI safety and developing Claude, their AI assistant."
]

chunk_refs = []
for i, text in enumerate(chunks_data):
    chunk = Chunk(
        document_id=doc.id,
        text=text,
        position=i,
        start_char=i*200,
        end_char=(i+1)*200,
        confidence=1.0
    )
    db.sqlite.save_chunk(chunk)
    chunk_refs.append(f"sqlite://chunk/{chunk.id}")
    print(f"✓ Created chunk {i+1}: {text[:50]}...")

# Now generate embeddings for the chunks themselves
print("\n2. Generating embeddings for chunks...")
embedder = EmbeddingGenerator(db)
embed_result = embedder.generate_embeddings(object_refs=chunk_refs)
print(f"✓ Created {embed_result['embedding_count']} chunk embeddings")

# Test searching
print("\n3. Testing FAISS search...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

test_queries = [
    "Who is the CEO of OpenAI?",
    "What company created GPT-4?",
    "What is Anthropic focused on?"
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    
    # Generate query embedding
    query_embedding = model.encode([query], show_progress_bar=False)[0]
    
    # Search FAISS
    results = db.faiss.search(query_embedding, k=3)
    print(f"Found {len(results)} results:")
    
    for ref, score in results[:2]:
        # Get the actual content
        parts = ref.split("://")[1].split("/")
        obj_type, obj_id = parts
        
        if obj_type == "chunk":
            chunk = db.sqlite.get_chunk(obj_id)
            if chunk:
                print(f"  - Chunk (score {score:.3f}): {chunk.text[:80]}...")
        elif obj_type == "entity":
            entity = db.neo4j.get_entity(obj_id)
            if entity:
                print(f"  - Entity (score {score:.3f}): {entity.name} ({entity.entity_type})")

# Cleanup
print("\n4. Cleaning up...")
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Data check completed!")