#!/usr/bin/env python3
"""Find organizations from climate report"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # Find organizations related to climate/energy
    print("\n🏢 Organizations from Climate Report:\n")
    
    result = session.run("""
        MATCH (e:Entity:ORG)
        WHERE toLower(e.canonical_name) CONTAINS 'solar'
           OR toLower(e.canonical_name) CONTAINS 'wind'
           OR toLower(e.canonical_name) CONTAINS 'green'
           OR toLower(e.canonical_name) CONTAINS 'climate'
           OR toLower(e.canonical_name) CONTAINS 'energy'
           OR toLower(e.canonical_name) CONTAINS 'panel'
           OR e.canonical_name IN ['the united nations', 'the european union', 'mit', 'stanford university']
        RETURN DISTINCT e.canonical_name as name, e.pagerank_score as score
        ORDER BY e.canonical_name
    """)
    
    orgs = list(result)
    if orgs:
        for record in orgs:
            print(f"• {record['name']}")
    else:
        print("No climate-related organizations found")
    
    print(f"\nTotal: {len(orgs)} organizations")

driver.close()