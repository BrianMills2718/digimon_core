#!/usr/bin/env python3
"""Show organizations with their locations from the graph"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # Find organizations with locations
    result = session.run("""
        MATCH (org:Entity:ORG)
        OPTIONAL MATCH (org)-[:LOCATED_IN]->(loc:Entity:GPE)
        RETURN org.canonical_name as Organization, 
               loc.canonical_name as Location
        ORDER BY org.canonical_name
    """)
    
    print("\n🏢 Organizations and Their Locations:")
    print("=" * 50)
    
    for record in result:
        org = record["Organization"]
        loc = record["Location"] or "Location not found"
        print(f"• {org} → {loc}")
    
    print("\n\n🌍 All Organizations:")
    print("=" * 50)
    
    # Show all organizations
    result = session.run("""
        MATCH (org:Entity:ORG)
        RETURN org.canonical_name as name
        ORDER BY name
    """)
    
    for record in result:
        print(f"• {record['name']}")
    
    print("\n\n📍 All Locations:")
    print("=" * 50)
    
    # Show all locations
    result = session.run("""
        MATCH (loc:Entity:GPE)
        RETURN loc.canonical_name as name
        ORDER BY name
    """)
    
    for record in result:
        print(f"• {record['name']}")

driver.close()