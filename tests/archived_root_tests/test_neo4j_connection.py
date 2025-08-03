#!/usr/bin/env python3
"""
Test Neo4j Connection
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from neo4j import GraphDatabase
from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
from src.core.service_manager import ServiceManager

def test_neo4j_connection():
    """Test Neo4j connection"""
    
    print("🔍 TESTING NEO4J CONNECTION")
    print("=" * 60)
    
    # Test direct connection
    print("\n1. Testing direct Neo4j connection...")
    try:
        driver = GraphDatabase.driver(
            "neo4j://localhost:7687",
            auth=("neo4j", "kgas_test_2024")
        )
        
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"   ✅ Direct connection successful: {record['message']}")
        
        driver.close()
        
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        return False
    
    # Test BaseNeo4jTool connection
    print("\n2. Testing BaseNeo4jTool connection...")
    try:
        service_manager = ServiceManager()
        tool = BaseNeo4jTool(
            service_manager.identity_service,
            service_manager.provenance_service,
            service_manager.quality_service,
            neo4j_uri="neo4j://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="kgas_test_2024"
        )
        
        if tool.driver:
            print("   ✅ BaseNeo4jTool connection successful")
            
            # Test a simple query
            with tool.driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                record = result.single()
                print(f"   📊 Current nodes in database: {record['node_count']}")
            
        else:
            print("   ❌ BaseNeo4jTool connection failed")
            return False
        
    except Exception as e:
        print(f"   ❌ BaseNeo4jTool connection error: {e}")
        return False
    
    # Test with default config
    print("\n3. Testing with default configuration...")
    try:
        from src.tools.phase1.t31_entity_builder import T31EntityBuilderUnified
        
        entity_builder = T31EntityBuilderUnified(service_manager)
        if hasattr(entity_builder, 'driver') and entity_builder.driver:
            print("   ✅ T31EntityBuilder connected successfully")
        else:
            print("   ❌ T31EntityBuilder connection failed")
    
    except Exception as e:
        print(f"   ❌ T31EntityBuilder error: {e}")
    
    print("\n✅ Neo4j connection test complete!")
    return True

if __name__ == "__main__":
    success = test_neo4j_connection()
    sys.exit(0 if success else 1)