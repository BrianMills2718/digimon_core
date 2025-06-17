#!/usr/bin/env python
"""Debug relationship extraction issues."""

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

# Test simple case
doc = Document(title="Test", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

# Use simpler text to debug
chunk = Chunk(
    document_id=doc.id,
    text="Elon Musk founded Tesla in 2003.",
    position=0, start_char=0, end_char=100, confidence=1.0
)
db.sqlite.save_chunk(chunk)
chunk_ref = f"sqlite://chunk/{chunk.id}"

# Extract entities
print("1. Extracting entities...")
entity_extractor = EntityExtractorSpacy(db)
entity_result = entity_extractor.extract_entities(chunk_ref)
print(f"Found {entity_result['entity_count']} entities:")

# Show entity details
with db.neo4j.driver.session() as session:
    result = session.run("MATCH (e:Entity) RETURN e.name, e.id")
    entities = list(result)
    for e in entities:
        print(f"  - \"{e['e.name']}\" (id: {e['e.id']})")

# Extract relationships
print("\n2. Testing relationship extraction...")
rel_extractor = RelationshipExtractor(db)

# Debug pattern matching
import re
text = chunk.text
print(f"\nText: '{text}'")

# Test FOUNDED pattern
pattern = r"(\w+)\s+founded\s+(\w+)"
matches = list(re.finditer(pattern, text, re.IGNORECASE))
print(f"\nPattern '{pattern}' matches: {len(matches)}")
for m in matches:
    print(f"  - Match: '{m.group(0)}' -> source='{m.group(1)}', target='{m.group(2)}'")

# Try better pattern
pattern2 = r"([\w\s]+?)\s+founded\s+([\w\s]+?)(?:\s+in|\s*$)"
matches2 = list(re.finditer(pattern2, text, re.IGNORECASE))
print(f"\nBetter pattern '{pattern2}' matches: {len(matches2)}")
for m in matches2:
    print(f"  - Match: '{m.group(0)}' -> source='{m.group(1).strip()}', target='{m.group(2).strip()}'")

# Now extract relationships
rel_result = rel_extractor.extract_relationships(chunk_ref, entity_result['entity_refs'])
print(f"\n3. Found {rel_result['relationship_count']} relationships")

# Show relationships
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name as source, type(r) as rel_type, b.name as target
    """)
    
    rels = list(result)
    if rels:
        print("\nRelationships in graph:")
        for r in rels:
            print(f"  - {r['source']} --[{r['rel_type']}]--> {r['target']}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()