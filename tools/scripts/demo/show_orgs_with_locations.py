#!/usr/bin/env python3
"""Show organizations with their locations from the graph"""

from neo4j import GraphDatabase

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import ConfigManager

config_manager = ConfigManager()
neo4j_config = config_manager.get_neo4j_config()
auth = None if neo4j_config['user'] is None else (neo4j_config['user'], neo4j_config['password'])
driver = GraphDatabase.driver(neo4j_config['uri'], auth=auth)

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