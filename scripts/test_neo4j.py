#!/usr/bin/env python3
"""Simple test to verify Neo4j integration is working."""

import os
import sys
from neo4j import GraphDatabase

# Set environment for Neo4j testing
os.environ['NEO4J_ENABLED'] = 'true'
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'password'

def test_neo4j_working():
    """Simple test to verify Neo4j is working and has data."""
    print("🔍 Testing Neo4j Integration")
    print("=" * 40)
    
    try:
        # Test basic connectivity
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        driver.verify_connectivity()
        print("✅ Neo4j connection successful")
        
        with driver.session() as session:
            # Check Neo4j version
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            components = list(result)
            if components:
                version = components[0]["versions"][0]
                edition = components[0]["edition"]
                print(f"✅ Neo4j version: {version} ({edition})")
            
            # Check for existing data
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            print(f"✅ Nodes in database: {node_count}")
            
            # Check for GraphRAG schema
            result = session.run("MATCH (n:M1_Entity) RETURN count(n) as entity_count")
            entity_count = result.single()["entity_count"]
            print(f"✅ M1 entities: {entity_count}")
            
            # List some sample data
            if entity_count > 0:
                result = session.run("MATCH (n:M1_Entity) RETURN n.name LIMIT 3")
                entities = [record["n.name"] for record in result]
                print(f"✅ Sample entities: {entities}")
            
            # Check relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            print(f"✅ Relationships: {rel_count}")
            
        driver.close()
        print("\n🎉 Neo4j integration is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_neo4j_working()