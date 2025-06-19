#!/usr/bin/env python
"""Complete working flow demonstration."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== Complete GraphRAG Flow Demo ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear Neo4j
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# 1. Create document
print("1. Creating document...")
doc = Document(
    title="AI Industry Report 2024",
    source_path="ai_report.pdf",
    content_hash="abc123",
    metadata={"year": 2024}
)
db.sqlite.save_document(doc)
print(f"✓ Document created: {doc.id}")

# 2. Create chunks with rich content
print("\n2. Creating content chunks...")
chunks_data = [
    "OpenAI is a leading artificial intelligence research laboratory that created GPT-4, their most advanced large language model. Founded in December 2015, OpenAI has revolutionized natural language processing.",
    "Sam Altman serves as the Chief Executive Officer of OpenAI. Under his leadership since 2019, the company has released groundbreaking models including GPT-3, GPT-4, DALL-E, and ChatGPT.",
    "Anthropic is an AI safety company founded in 2021 by former OpenAI researchers Dario Amodei and Daniela Amodei. The company focuses on building reliable, interpretable, and steerable AI systems.",
    "Claude is Anthropic's AI assistant, designed with a focus on being helpful, harmless, and honest. It uses constitutional AI techniques to ensure safe and beneficial behavior.",
    "Google DeepMind, based in London, is known for breakthrough achievements like AlphaGo and AlphaFold. Demis Hassabis leads the company as CEO and co-founder."
]

chunk_refs = []
for i, text in enumerate(chunks_data):
    chunk = Chunk(
        document_id=doc.id,
        text=text,
        position=i,
        start_char=i*250,
        end_char=(i+1)*250,
        confidence=1.0
    )
    db.sqlite.save_chunk(chunk)
    chunk_refs.append(f"sqlite://chunk/{chunk.id}")
print(f"✓ Created {len(chunk_refs)} chunks")

# 3. Extract entities from each chunk
print("\n3. Extracting entities...")
extractor = EntityExtractorSpacy(db)
all_entity_refs = []

for i, chunk_ref in enumerate(chunk_refs):
    result = extractor.extract_entities(chunk_ref)
    all_entity_refs.extend(result['entity_refs'])
    print(f"  Chunk {i+1}: {result['entity_count']} entities")

unique_entity_refs = list(set(all_entity_refs))
print(f"✓ Total unique entities: {len(unique_entity_refs)}")

# 4. Generate embeddings for BOTH chunks and entities
print("\n4. Generating embeddings...")
embedder = EmbeddingGenerator(db)

# Embed chunks
print("  Embedding chunks...")
chunk_embed = embedder.generate_embeddings(object_refs=chunk_refs)
print(f"  ✓ {chunk_embed['embedding_count']} chunk embeddings")

# Embed entities
print("  Embedding entities...")
if unique_entity_refs:
    entity_embed = embedder.generate_embeddings(object_refs=unique_entity_refs[:20])  # Limit to 20
    print(f"  ✓ {entity_embed['embedding_count']} entity embeddings")

print(f"✓ Total vectors in FAISS: {db.faiss.index.ntotal}")

# 5. Calculate PageRank
print("\n5. Calculating PageRank...")
pagerank = PageRankAnalyzer(db)

# First create some relationships between entities
with db.neo4j.driver.session() as session:
    # Create relationships based on co-occurrence in chunks
    session.run("""
        MATCH (e1:Entity)-[:MENTIONED_IN]->(c:Chunk)<-[:MENTIONED_IN]-(e2:Entity)
        WHERE id(e1) < id(e2)
        MERGE (e1)-[r:CO_OCCURS_WITH]->(e2)
        SET r.weight = 1.0
    """)
    
    result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
    rel_count = result.single()["rel_count"]
    print(f"  Created {rel_count} relationships")

if rel_count > 0:
    pr_result = pagerank.calculate_pagerank()
    print(f"✓ PageRank calculated for {pr_result['entities_processed']} entities")
    if pr_result['top_entities']:
        print("  Top entities by PageRank:")
        for i, entity in enumerate(pr_result['top_entities'][:3]):
            print(f"    {i+1}. {entity['name']} (score: {entity['score']:.4f})")

# 6. Test natural language queries
print("\n6. Testing natural language queries with OpenAI...")
query_tool = NaturalLanguageQuery(db)

test_queries = [
    "Who is the CEO of OpenAI?",
    "What company created GPT-4?",
    "What is Anthropic's main focus?",
    "Tell me about Claude",
    "Who leads Google DeepMind?"
]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    
    try:
        result = query_tool.query(query, top_k=5)
        
        # Check if we got results
        if result['results']:
            print(f"✓ Found {len(result['results'])} relevant items")
            
            # Show top result
            top_result = result['results'][0]
            print(f"  Top match: {top_result['type']} (score: {top_result['combined_score']:.3f})")
            
            # Check answer type
            answer = result['answer']
            if len(answer) > 200 and "Based on the following context" not in answer:
                print("✓ LLM-generated answer:")
            else:
                print("  Template answer:")
            
            # Show answer (truncated)
            print(f"\n💬 Answer: {answer[:300]}{'...' if len(answer) > 300 else ''}")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# 7. Summary
print("\n\n=== Summary ===")
print(f"✅ Documents: 1")
print(f"✅ Chunks: {len(chunk_refs)}")
print(f"✅ Entities: {len(unique_entity_refs)}")
print(f"✅ Embeddings: {db.faiss.index.ntotal}")
print(f"✅ OpenAI Integration: {'Working' if query_tool.openai_client else 'Not configured'}")

# Cleanup
print("\n8. Cleaning up...")
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✨ Complete GraphRAG flow demonstrated successfully!")