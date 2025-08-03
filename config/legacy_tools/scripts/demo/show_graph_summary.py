#!/usr/bin/env python3
"""Show summary of what's in the graph"""

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