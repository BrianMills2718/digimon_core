#!/usr/bin/env python3
"""Initialize Neo4j schema to match application expectations"""

import os
from neo4j import GraphDatabase

def initialize_schema():
    """Create proper Neo4j schema with all required properties and labels"""
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    
    try:
        driver = GraphDatabase.driver(uri, auth=None)
        print(f"Connecting to Neo4j at {uri}")
        
        with driver.session() as session:
            # Clear existing data
            print("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create constraints
            print("Creating constraints...")
            session.run("""
            CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
            FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE
            """)
            
            # Create indexes
            print("Creating indexes...")
            session.run("""
            CREATE INDEX entity_canonical_name IF NOT EXISTS
            FOR (e:Entity) ON (e.canonical_name)
            """)
            
            session.run("""
            CREATE INDEX entity_type IF NOT EXISTS
            FOR (e:Entity) ON (e.entity_type)
            """)
            
            session.run("""
            CREATE INDEX entity_confidence IF NOT EXISTS
            FOR (e:Entity) ON (e.confidence)
            """)
            
            # Create relationship indexes
            session.run("""
            CREATE INDEX relationship_type IF NOT EXISTS
            FOR ()-[r:RELATED_TO]-() ON (r.relationship_type)
            """)
            
            session.run("""
            CREATE INDEX relationship_confidence IF NOT EXISTS
            FOR ()-[r:RELATED_TO]-() ON (r.confidence)
            """)
            
            print("✅ Neo4j schema initialized successfully")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing schema: {e}")
        return False

def verify_schema():
    """Verify schema was created correctly"""
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    
    try:
        driver = GraphDatabase.driver(uri, auth=None)
        
        with driver.session() as session:
            # Check constraints
            constraints = session.run("SHOW CONSTRAINTS").data()
            print(f"Constraints: {len(constraints)}")
            
            # Check indexes
            indexes = session.run("SHOW INDEXES").data()
            print(f"Indexes: {len(indexes)}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"Error verifying schema: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Neo4j Schema Initialization")
    
    if initialize_schema():
        verify_schema()
    else:
        print("❌ Schema initialization failed")