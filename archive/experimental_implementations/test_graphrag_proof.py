#!/usr/bin/env python
"""Quick proof that we have TRUE GraphRAG."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.models import Document, Chunk
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase2.t24_relationship_extractor import RelationshipExtractor
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery

print("=== GRAPHRAG PROOF TEST ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Clear
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

# Create simple test data
doc = Document(title="Test", source_path="test.pdf", content_hash="test", metadata={})
db.sqlite.save_document(doc)

chunk = Chunk(
    document_id=doc.id,
    text="Microsoft acquired GitHub. Bill Gates founded Microsoft. GitHub competes with GitLab.",
    position=0, start_char=0, end_char=100, confidence=1.0
)
db.sqlite.save_chunk(chunk)
chunk_ref = f"sqlite://chunk/{chunk.id}"

# Extract entities
print("1. Extracting entities...")
extractor = EntityExtractorSpacy(db)
entity_result = extractor.extract_entities(chunk_ref)
print(f"   Found {entity_result['entity_count']} entities")

# Extract relationships
print("\n2. Extracting relationships...")
rel_extractor = RelationshipExtractor(db)
rel_result = rel_extractor.extract_relationships(chunk_ref, entity_result['entity_refs'])
print(f"   Found {rel_result['relationship_count']} relationships")

# Check graph
print("\n3. Checking graph structure...")
with db.neo4j.driver.session() as session:
    # Show all relationships
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name as source, type(r) as rel, b.name as target
        LIMIT 10
    """)
    
    rels = list(result)
    if rels:
        print("   Graph relationships:")
        for r in rels:
            print(f"   - {r['source']} --[{r['rel']}]--> {r['target']}")
    else:
        print("   ❌ No relationships in graph!")
    
    # Test multi-hop
    result = session.run("""
        MATCH path = (a:Entity)-[*1..2]-(b:Entity)
        WHERE a.name =~ '(?i).*gates.*' AND b.name =~ '(?i).*github.*'
        RETURN [n in nodes(path) | n.name] as path
        LIMIT 1
    """)
    
    path_record = result.single()
    if path_record:
        print(f"\n   ✅ Multi-hop path: {' -> '.join(path_record['path'])}")
    else:
        print("\n   ❌ No path between Gates and GitHub")

# Final check
print("\n4. Final verdict:")
with db.neo4j.driver.session() as session:
    stats = session.run("""
        MATCH (n:Entity) WITH count(n) as nodes
        MATCH ()-[r]->() WITH nodes, count(r) as edges
        RETURN nodes, edges
    """).single()
    
    if stats['edges'] > 0:
        print(f"   ✅ TRUE GRAPHRAG: {stats['nodes']} nodes, {stats['edges']} edges")
    else:
        print(f"   ❌ NOT GRAPHRAG: {stats['nodes']} nodes but NO edges!")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()