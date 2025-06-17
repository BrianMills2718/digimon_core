#!/usr/bin/env python
"""Debug entity matching in relationship extraction."""

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

# Create test data
doc = Document(title="Test", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

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

# Show entities
print(f"\nExtracted {entity_result['entity_count']} entities:")
entities = {}
with db.neo4j.driver.session() as session:
    for ref in entity_result['entity_refs']:
        entity_id = ref.split("/")[-1]
        result = session.run("MATCH (e:Entity {id: $id}) RETURN e", id=entity_id)
        record = result.single()
        if record:
            entity = record['e']
            entities[entity_id] = {
                'name': entity['name'],
                'type': entity.get('entity_type', 'UNKNOWN')
            }
            print(f"  - '{entity['name']}' ({entity.get('entity_type', 'UNKNOWN')})")

# Test the relationship extractor's internal methods
print("\n2. Testing relationship extraction internals...")
rel_extractor = RelationshipExtractor(db)

# Convert entities to the format expected by the extractor
entity_objects = {}
for entity_id, entity_data in entities.items():
    from src.models import Entity
    entity_obj = Entity(
        id=entity_id,
        name=entity_data['name'],
        canonical_name=entity_data['name'].lower(),
        entity_type=entity_data['type'],
        attributes={}
    )
    entity_objects[entity_id] = entity_obj

# Test pattern matching
import re
pattern = r"([\w\s]+?)\s+founded\s+([\w\s]+?)(?:\s+in|\s*$|\.|,)"
match = re.search(pattern, chunk.text, re.IGNORECASE)
if match:
    print(f"\nPattern matched: '{match.group(0)}'")
    print(f"  Source text: '{match.group(1)}'")
    print(f"  Target text: '{match.group(2)}'")
    
    # Test entity matching
    source_entity = rel_extractor._find_matching_entity(match.group(1), entity_objects)
    target_entity = rel_extractor._find_matching_entity(match.group(2), entity_objects)
    
    print(f"\nEntity matching:")
    print(f"  Source '{match.group(1)}' -> {source_entity.name if source_entity else 'NOT FOUND'}")
    print(f"  Target '{match.group(2)}' -> {target_entity.name if target_entity else 'NOT FOUND'}")

# Now run full extraction
print("\n3. Running full relationship extraction...")
rel_result = rel_extractor.extract_relationships(chunk_ref, entity_result['entity_refs'])
print(f"Found {rel_result['relationship_count']} relationships")

# Show relationships in Neo4j
with db.neo4j.driver.session() as session:
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name as source, type(r) as rel_type, b.name as target
        ORDER BY type(r)
    """)
    
    rels = list(result)
    if rels:
        print("\nRelationships in graph:")
        for r in rels:
            print(f"  - {r['source']} --[{r['rel_type']}]--> {r['target']}")

# Debug: Show what's in the saved relationships
if 'relationships' in rel_result:
    print("\nDetailed relationships returned:")
    for rel in rel_result['relationships']:
        print(f"  - {rel}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()