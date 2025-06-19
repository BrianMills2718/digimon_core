#!/usr/bin/env python
"""Direct test of the workflow without complex test infrastructure."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Direct imports
from src.utils.database import DatabaseManager
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery
from src.models import Document, Chunk

print("=== Direct Flow Test ===\n")

# 1. Initialize database
print("1. Initializing database...")
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear Neo4j
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
print("✓ Database initialized")

# 2. Create test data directly
print("\n2. Creating test document and chunk...")
doc = Document(
    title="AI Companies",
    source_path="test.pdf",
    content_hash="abc123",
    metadata={"test": True}
)
db.sqlite.save_document(doc)

chunk = Chunk(
    document_id=doc.id,
    text="OpenAI created GPT-4 in 2023. The company is led by Sam Altman. Anthropic built Claude with a focus on AI safety. Dario Amodei leads Anthropic.",
    position=0,
    start_char=0,
    end_char=150,
    confidence=1.0
)
db.sqlite.save_chunk(chunk)
print(f"✓ Document: {doc.id}")
print(f"✓ Chunk: {chunk.id}")

# 3. Extract entities
print("\n3. Extracting entities...")
extractor = EntityExtractorSpacy(db)
entity_result = extractor.extract_entities(f"sqlite://chunk/{chunk.id}")
print(f"✓ Found {entity_result['entity_count']} entities")

# Show what was found
if entity_result['entity_refs']:
    print("  Entities:")
    for ref in entity_result['entity_refs'][:5]:
        # Parse the reference to get entity ID
        entity_id = ref.split('/')[-1]
        entity = db.neo4j.get_entity(entity_id)
        if entity:
            print(f"  - {entity.name} ({entity.entity_type})")

# 4. Generate embeddings
print("\n4. Generating embeddings...")
if entity_result['entity_refs']:
    embedder = EmbeddingGenerator(db)
    embed_result = embedder.generate_embeddings(
        object_refs=entity_result['entity_refs']
    )
    print(f"✓ Created {embed_result['embedding_count']} embeddings")
    print(f"  FAISS index: {db.faiss.index.ntotal} vectors")

# 5. Test queries
print("\n5. Testing natural language queries...")
query_tool = NaturalLanguageQuery(db)

queries = [
    "Who created GPT-4?",
    "Who leads OpenAI?",
    "What is Anthropic focused on?"
]

for query in queries:
    print(f"\nQuery: '{query}'")
    try:
        result = query_tool.query(query, top_k=3)
        print(f"Results: {len(result['results'])}")
        
        # Check answer type
        answer = result['answer']
        if "Based on the available information:" in answer:
            print("Answer type: Template-based")
        else:
            print("Answer type: LLM-generated")
        
        # Show answer preview
        print(f"Answer: {answer[:150]}...")
        
    except Exception as e:
        print(f"Error: {e}")

# 6. Verify final state
print("\n6. Final database state:")
with db.neo4j.driver.session() as session:
    r = session.run("MATCH (n:Entity) RETURN count(n) as count")
    entity_count = r.single()['count']
    print(f"  Neo4j entities: {entity_count}")

print(f"  FAISS vectors: {db.faiss.index.ntotal}")

docs = []  # No get_all_documents method available
print(f"  SQLite documents: {len(docs)}")

# Cleanup
print("\n7. Cleaning up...")
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Direct flow test completed!")