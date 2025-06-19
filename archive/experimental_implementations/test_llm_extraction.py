#!/usr/bin/env python
"""Test LLM-based entity and relationship extraction."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in environment")
    sys.exit(1)

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23b_llm_extractor import LLMExtractor

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create test document
doc = Document(title="Tech Industry", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

# Test with the same problematic texts from before
test_chunks = [
    # From adversarial test
    "Elon Musk founded Tesla in 2003. Tesla is headquartered in Austin, Texas.",
    "Musk also founded SpaceX. He sold PayPal to eBay. Peter Thiel was Musk's partner at PayPal.",
    "Tesla acquired SolarCity in 2016. SolarCity was founded by Musk's cousins. This was controversial.",
    
    # Business relationships
    "Microsoft invested $10 billion in OpenAI. Microsoft partners with OpenAI to integrate GPT into Bing.",
    "Google competes with Microsoft in AI. Google and DeepMind collaborate on research.",
    
    # More complex
    "Satya Nadella leads Microsoft. Sam Altman heads OpenAI. They announced a partnership in 2023."
]

# Process with LLM
llm_extractor = LLMExtractor(db)

print("Processing chunks with LLM extractor...\n")

all_relationships = []
for i, text in enumerate(test_chunks):
    print(f"Chunk {i+1}: {text[:50]}...")
    
    chunk = Chunk(
        document_id=doc.id,
        text=text,
        position=i,
        start_char=i*200,
        end_char=(i+1)*200,
        confidence=1.0
    )
    db.sqlite.save_chunk(chunk)
    chunk_ref = f"sqlite://chunk/{chunk.id}"
    
    try:
        result = llm_extractor.extract_entities_and_relationships(chunk_ref)
        print(f"  Entities: {result['entity_count']}")
        print(f"  Relationships: {result['relationship_count']}")
        all_relationships.extend(result['relationships'])
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print()

# Analyze results
print("\n" + "="*60)
print("RELATIONSHIP ANALYSIS")
print("="*60)

with db.neo4j.driver.session() as session:
    # Get relationship distribution
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    rel_dist = list(result)
    total_rels = sum(r['count'] for r in rel_dist)
    
    print("\nRelationship distribution:")
    co_occurs_count = 0
    semantic_count = 0
    
    for r in rel_dist:
        pct = (r['count'] / total_rels) * 100 if total_rels > 0 else 0
        print(f"  {r['rel_type']}: {r['count']} ({pct:.1f}%)")
        
        if r['rel_type'] == 'CO_OCCURS_WITH':
            co_occurs_count = r['count']
        else:
            semantic_count += r['count']
    
    co_occurs_pct = (co_occurs_count / total_rels) * 100 if total_rels > 0 else 0
    semantic_pct = (semantic_count / total_rels) * 100 if total_rels > 0 else 0
    
    print(f"\nSummary:")
    print(f"  Semantic relationships: {semantic_count} ({semantic_pct:.1f}%)")
    print(f"  Co-occurrence relationships: {co_occurs_count} ({co_occurs_pct:.1f}%)")
    
    if co_occurs_pct < 70:
        print(f"\n✅ SUCCESS: CO_OCCURS_WITH is {co_occurs_pct:.1f}% (< 70% requirement)")
    else:
        print(f"\n❌ FAILURE: CO_OCCURS_WITH is {co_occurs_pct:.1f}% (> 70% requirement)")

# Show extracted relationships
print("\n\nExtracted relationships:")
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name as source, type(r) as rel_type, b.name as target, r.confidence as conf
        ORDER BY type(r), a.name
    """)
    
    for record in result:
        print(f"  {record['source']} --[{record['rel_type']}]--> {record['target']} (conf: {record['conf']})")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()