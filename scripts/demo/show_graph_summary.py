#!/usr/bin/env python3
"""Show summary of what's in the graph"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # Count by entity type
    print("\n📊 Entity Types in Graph:")
    print("=" * 40)
    
    result = session.run("""
        MATCH (e:Entity)
        RETURN e.entity_type as type, COUNT(e) as count
        ORDER BY count DESC
    """)
    
    for record in result:
        print(f"• {record['type']}: {record['count']}")
    
    # Show some entities
    print("\n\n🔝 Sample Entities (first 20):")
    print("=" * 40)
    
    result = session.run("""
        MATCH (e:Entity)
        RETURN e.canonical_name as name, e.entity_type as type
        ORDER BY e.canonical_name
        LIMIT 20
    """)
    
    for record in result:
        print(f"• {record['name']} ({record['type']})")
    
    # Show relationship types
    print("\n\n🔗 Relationship Types:")
    print("=" * 40)
    
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as type, COUNT(r) as count
        ORDER BY count DESC
    """)
    
    for record in result:
        print(f"• {record['type']}: {record['count']}")
    
    # Show some relationships
    print("\n\n🔗 Sample Relationships (first 10):")
    print("=" * 40)
    
    result = session.run("""
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.canonical_name as from, type(r) as rel, b.canonical_name as to
        LIMIT 10
    """)
    
    for record in result:
        print(f"• {record['from']} --[{record['rel']}]--> {record['to']}")

driver.close()