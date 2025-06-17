#!/usr/bin/env python
"""Test if Neo4j actually has entities and relationships."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import DatabaseManager

# Initialize
db = DatabaseManager()
db.initialize()

print("=== NEO4J RELATIONSHIP TEST ===\n")

# Check what's in Neo4j
with db.neo4j.driver.session() as session:
    # 1. Count entities
    result = session.run("MATCH (n:Entity) RETURN count(n) as count")
    entity_count = result.single()["count"]
    print(f"1. Total entities in Neo4j: {entity_count}")
    
    # 2. Count relationships
    result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
    rel_count = result.single()["count"]
    print(f"2. Total relationships in Neo4j: {rel_count}")
    
    # 3. Show sample entities
    print("\n3. Sample entities:")
    result = session.run("""
        MATCH (n:Entity) 
        RETURN n.name as name, n.entity_type as type, n.id as id
        LIMIT 10
    """)
    for i, record in enumerate(result):
        print(f"   {i+1}. {record['name']} ({record['type']}) - ID: {record['id'][:8]}...")
    
    # 4. Show relationship types
    print("\n4. Relationship types:")
    result = session.run("""
        MATCH ()-[r]->() 
        RETURN DISTINCT type(r) as rel_type, count(r) as count
    """)
    for record in result:
        print(f"   - {record['rel_type']}: {record['count']}")
    
    # 5. Show sample relationships
    print("\n5. Sample relationships:")
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name as from, type(r) as rel, b.name as to
        LIMIT 10
    """)
    rels = list(result)
    if rels:
        for record in rels:
            print(f"   - {record['from']} --[{record['rel']}]--> {record['to']}")
    else:
        print("   ❌ NO RELATIONSHIPS FOUND!")
    
    # 6. Check for specific relationship types that should exist
    print("\n6. Expected relationships:")
    
    # Check MENTIONED_IN relationships (entity to chunk)
    result = session.run("""
        MATCH (e:Entity)-[r:MENTIONED_IN]->(c:Chunk)
        RETURN count(r) as count
    """)
    mentioned_count = result.single()["count"]
    print(f"   - MENTIONED_IN relationships: {mentioned_count}")
    
    # Check CO_OCCURS_WITH relationships
    result = session.run("""
        MATCH (e1:Entity)-[r:CO_OCCURS_WITH]->(e2:Entity)
        RETURN count(r) as count
    """)
    cooccur_count = result.single()["count"]
    print(f"   - CO_OCCURS_WITH relationships: {cooccur_count}")
    
    # 7. Check if entities have PageRank scores
    print("\n7. Entities with PageRank scores:")
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.pagerank_score IS NOT NULL
        RETURN n.name as name, n.pagerank_score as score
        ORDER BY n.pagerank_score DESC
        LIMIT 5
    """)
    pr_entities = list(result)
    if pr_entities:
        for record in pr_entities:
            print(f"   - {record['name']}: {record['score']}")
    else:
        print("   ❌ NO PAGERANK SCORES FOUND!")

print("\n=== VERDICT ===")
if entity_count == 0:
    print("❌ NO ENTITIES IN NEO4J - Entity extraction is broken!")
elif rel_count == 0:
    print("❌ NO RELATIONSHIPS IN NEO4J - Graph construction is broken!")
elif mentioned_count == 0:
    print("❌ NO MENTIONED_IN RELATIONSHIPS - Entity-chunk linking is broken!")
else:
    print(f"⚠️  System has {entity_count} entities and {rel_count} relationships")
    print("   But relationship creation may still be incomplete")

db.close()