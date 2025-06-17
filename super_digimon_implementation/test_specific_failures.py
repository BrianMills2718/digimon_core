#!/usr/bin/env python
"""Test specific relationship extraction failures."""

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

# Test cases that failed
test_cases = [
    {
        "text": "Musk also founded SpaceX.",
        "expected": ("Musk", "SpaceX", "FOUNDED")
    },
    {
        "text": "Tesla acquired SolarCity in 2016.",
        "expected": ("Tesla", "SolarCity", "ACQUIRED") 
    },
    {
        "text": "Before Tesla, Musk founded X.com in 1999.",
        "expected": ("Musk", "X.com", "FOUNDED")
    }
]

for i, test in enumerate(test_cases):
    print(f"\n{'='*60}")
    print(f"Test {i+1}: {test['text']}")
    print('='*60)
    
    # Clear Neo4j
    with db.neo4j.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    
    # Create test data
    doc = Document(title=f"Test{i}", source_path="test.pdf", content_hash=f"test{i}", metadata={})
    db.sqlite.save_document(doc)
    
    chunk = Chunk(
        document_id=doc.id,
        text=test['text'],
        position=0, start_char=0, end_char=len(test['text']), confidence=1.0
    )
    db.sqlite.save_chunk(chunk)
    chunk_ref = f"sqlite://chunk/{chunk.id}"
    
    # Extract entities
    print("\n1. Entities extracted:")
    entity_extractor = EntityExtractorSpacy(db)
    entity_result = entity_extractor.extract_entities(chunk_ref)
    
    with db.neo4j.driver.session() as session:
        result = session.run("MATCH (e:Entity) RETURN e.name, e.entity_type ORDER BY e.name")
        for record in result:
            print(f"   - '{record['e.name']}' ({record['e.entity_type']})")
    
    # Extract relationships
    print("\n2. Relationships extracted:")
    rel_extractor = RelationshipExtractor(db)
    rel_result = rel_extractor.extract_relationships(chunk_ref, entity_result['entity_refs'])
    
    with db.neo4j.driver.session() as session:
        result = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE type(r) <> 'CO_OCCURS_WITH'
            RETURN a.name as source, type(r) as rel_type, b.name as target
        """)
        
        rels = list(result)
        if rels:
            for r in rels:
                print(f"   - {r['source']} --[{r['rel_type']}]--> {r['target']}")
        else:
            print("   - No semantic relationships found (only CO_OCCURS_WITH)")
    
    # Check expected
    print(f"\n3. Expected relationship:")
    exp_source, exp_target, exp_type = test['expected']
    print(f"   - {exp_source} --[{exp_type}]--> {exp_target}")
    
    # Debug: Check if entities match expected
    print("\n4. Debug entity matching:")
    with db.neo4j.driver.session() as session:
        # Check source
        result = session.run("""
            MATCH (e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($name)
               OR toLower($name) CONTAINS toLower(e.name)
            RETURN e.name
        """, name=exp_source)
        
        sources = [r['e.name'] for r in result]
        print(f"   - Entities matching '{exp_source}': {sources}")
        
        # Check target
        result = session.run("""
            MATCH (e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($name)
               OR toLower($name) CONTAINS toLower(e.name)
            RETURN e.name
        """, name=exp_target)
        
        targets = [r['e.name'] for r in result]
        print(f"   - Entities matching '{exp_target}': {targets}")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()