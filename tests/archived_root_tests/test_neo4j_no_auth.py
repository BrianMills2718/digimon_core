#!/usr/bin/env python3
"""
Test Neo4j Connection Without Authentication
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from neo4j import GraphDatabase

def test_neo4j_no_auth():
    """Test Neo4j connection without authentication"""
    
    print("🔍 TESTING NEO4J CONNECTION (NO AUTH)")
    print("=" * 60)
    
    # Test connection without auth
    print("\n1. Testing connection without authentication...")
    try:
        # No auth parameter needed when NEO4J_AUTH=none
        driver = GraphDatabase.driver("neo4j://localhost:7687")
        
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j (No Auth)!' as message")
            record = result.single()
            print(f"   ✅ Connection successful: {record['message']}")
            
            # Test database info
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in result:
                print(f"   📊 {record['name']}: {record['versions'][0]} ({record['edition']})")
            
            # Check if any data exists
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            record = result.single()
            print(f"   📊 Nodes in database: {record['node_count']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_neo4j_no_auth()
    if success:
        print("\n✅ Neo4j is now accessible without authentication!")
        print("\n🌐 Browser Access:")
        print("   URL: http://localhost:7474")
        print("   Connection: neo4j://localhost:7687")
        print("   Username: (leave blank or use 'neo4j')")
        print("   Password: (leave blank)")
        print("\n💡 You can now connect directly without any credentials!")
    sys.exit(0 if success else 1)