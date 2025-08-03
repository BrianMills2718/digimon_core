#!/usr/bin/env python3
"""Find organizations from climate report"""

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