#!/usr/bin/env python
"""Test if entities are actually being saved to Neo4j."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear Neo4j
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
print("=== ENTITY SAVING TEST ===\n")

# Create test data
doc = Document(
    title="Test",
    source_path="test.pdf",
    content_hash="test123",
    metadata={}
)
db.sqlite.save_document(doc)

chunk = Chunk(
    document_id=doc.id,
    text="Bill Gates founded Microsoft. Steve Jobs founded Apple.",
    position=0,
    start_char=0,
    end_char=100,
    confidence=1.0
)
db.sqlite.save_chunk(chunk)
print(f"1. Created chunk: {chunk.id}")

# Extract entities
print("\n2. Extracting entities...")
extractor = EntityExtractorSpacy(db)
result = extractor.extract_entities(f"sqlite://chunk/{chunk.id}")
print(f"   Entity refs returned: {result['entity_refs']}")
print(f"   Entity count: {result['entity_count']}")

# Check Neo4j directly
print("\n3. Checking Neo4j...")
with db.neo4j.driver.session() as session:
    # Count all nodes
    result = session.run("MATCH (n) RETURN count(n) as count")
    node_count = result.single()["count"]
    print(f"   Total nodes: {node_count}")
    
    # Count Entity nodes
    result = session.run("MATCH (n:Entity) RETURN count(n) as count")
    entity_count = result.single()["count"]
    print(f"   Entity nodes: {entity_count}")
    
    # Show all nodes
    result = session.run("MATCH (n) RETURN labels(n) as labels, n LIMIT 10")
    nodes = list(result)
    if nodes:
        print("\n   All nodes in database:")
        for record in nodes:
            print(f"   - Labels: {record['labels']}")
            print(f"     Properties: {dict(record['n'])}")
    else:
        print("   ❌ NO NODES IN NEO4J AT ALL!")

# Check if create_or_link_entity actually saves
print("\n4. Testing create_or_link_entity directly...")
identity = db.get_identity_service()
result = identity.create_or_link_entity(
    surface_form="Test Entity",
    entity_type="PERSON",
    attributes={"test": True}
)
print(f"   Created entity: {result['entity'].id}")
print(f"   Is new: {result['is_new']}")

# Check Neo4j again
with db.neo4j.driver.session() as session:
    result = session.run("MATCH (n:Entity) RETURN count(n) as count")
    new_count = result.single()["count"]
    print(f"   Entity count after direct creation: {new_count}")

# Let's check the Neo4j save_entity method
print("\n5. Checking Neo4j save_entity method...")
from src.models import Entity
test_entity = Entity(
    name="Direct Test Entity",
    entity_type="TEST",
    canonical_name="Direct Test Entity",
    attributes={"direct": True}
)

try:
    db.neo4j.save_entity(test_entity)
    print(f"   ✓ Saved entity: {test_entity.id}")
except Exception as e:
    print(f"   ❌ Error saving entity: {e}")

# Final check
with db.neo4j.driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as count")
    final_count = result.single()["count"]
    print(f"\n6. FINAL Neo4j node count: {final_count}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()