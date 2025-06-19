#!/usr/bin/env python
"""Test improved relationship extraction."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase2.t24_relationship_extractor import RelationshipExtractor

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create test document with rich relationships
doc = Document(title="Tech Industry", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

# Test texts with many semantic relationships
test_chunks = [
    # Business relationships
    "Microsoft invested $10 billion in OpenAI. Microsoft partners with OpenAI to integrate GPT into Bing.",
    
    # Competition and partnerships
    "Google competes with Microsoft in AI. Google and DeepMind collaborate on research. Amazon challenges both companies.",
    
    # Employment and leadership
    "Satya Nadella leads Microsoft. Sam Altman heads OpenAI. Sundar Pichai runs Google.",
    
    # Manufacturing and supply
    "Apple manufactures iPhones. TSMC supplies chips to Apple. Foxconn produces devices for Apple.",
    
    # Acquisitions and ownership
    "Facebook acquired Instagram and WhatsApp. Meta owns Facebook. Zuckerberg controls Meta.",
    
    # Geographic relationships
    "Microsoft operates in Redmond. Google has offices in Mountain View. Apple is headquartered in Cupertino.",
    
    # More complex relationships
    "Tesla manufactures electric vehicles. Elon Musk founded Tesla and SpaceX. SpaceX develops rockets.",
    
    # Investment relationships
    "Sequoia Capital invested in Google. Andreessen Horowitz backed Facebook. Y Combinator funded Airbnb."
]

# Process chunks
entity_extractor = EntityExtractorSpacy(db)
relationship_extractor = RelationshipExtractor(db)

all_relationships = []
for i, text in enumerate(test_chunks):
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
    
    # Extract entities
    entity_result = entity_extractor.extract_entities(chunk_ref)
    
    # Extract relationships
    if entity_result['entity_refs']:
        rel_result = relationship_extractor.extract_relationships(chunk_ref, entity_result['entity_refs'])
        all_relationships.extend(rel_result['relationships'])

print(f"Total relationships extracted: {len(all_relationships)}")

# Analyze relationship types
with db.neo4j.driver.session() as session:
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
        pct = (r['count'] / total_rels) * 100
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

# Show some example semantic relationships
print("\nExample semantic relationships found:")
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        WHERE type(r) <> 'CO_OCCURS_WITH'
        RETURN a.name as source, type(r) as rel_type, b.name as target
        LIMIT 20
    """)
    
    for record in result:
        print(f"  {record['source']} --[{record['rel_type']}]--> {record['target']}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()