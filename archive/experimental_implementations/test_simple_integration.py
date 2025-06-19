#!/usr/bin/env python
"""Simple integration test to verify databases work."""

import time
import sqlite3
from pathlib import Path
import numpy as np
from neo4j import GraphDatabase
import faiss


def test_databases():
    """Test all databases are working correctly."""
    print("🧪 Starting Simple Database Integration Test")
    print("=" * 50)
    
    # Wait for services
    print("⏳ Waiting for services...")
    time.sleep(3)
    
    # Test 1: Neo4j
    print("\n🌐 Testing Neo4j...")
    try:
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            # Create test entity
            result = session.run("""
                CREATE (e:Entity {
                    id: 'test_123',
                    name: 'Test Entity',
                    entity_type: 'TEST',
                    confidence: 0.95
                })
                RETURN e.id as id, e.name as name
            """)
            record = result.single()
            print(f"✓ Created entity: {record['name']} (id: {record['id']})")
            
            # Clean up
            session.run("MATCH (e:Entity {id: 'test_123'}) DELETE e")
        driver.close()
        print("✓ Neo4j is working correctly")
    except Exception as e:
        print(f"✗ Neo4j error: {e}")
        return False
    
    # Test 2: SQLite
    print("\n📊 Testing SQLite...")
    try:
        db_path = Path("./data/test_simple.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                confidence REAL NOT NULL
            )
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO test_entities (id, name, confidence)
            VALUES (?, ?, ?)
        """, ("test_456", "Test SQLite Entity", 0.85))
        
        # Query back
        cursor.execute("SELECT * FROM test_entities WHERE id = ?", ("test_456",))
        row = cursor.fetchone()
        print(f"✓ Created entity: {row[1]} (confidence: {row[2]})")
        
        conn.commit()
        conn.close()
        
        # Clean up
        if db_path.exists():
            db_path.unlink()
        
        print("✓ SQLite is working correctly")
    except Exception as e:
        print(f"✗ SQLite error: {e}")
        return False
    
    # Test 3: FAISS
    print("\n🔍 Testing FAISS...")
    try:
        # Create test index
        dimension = 384
        index = faiss.IndexFlatL2(dimension)
        
        # Add test vectors
        test_vectors = np.random.rand(5, dimension).astype('float32')
        index.add(test_vectors)
        
        print(f"✓ Added {index.ntotal} vectors to index")
        
        # Search
        query = np.random.rand(1, dimension).astype('float32')
        distances, indices = index.search(query, k=3)
        
        print(f"✓ Found {len(indices[0])} nearest neighbors")
        print(f"  Distances: {distances[0]}")
        
        print("✓ FAISS is working correctly")
    except Exception as e:
        print(f"✗ FAISS error: {e}")
        return False
    
    # Test 4: Redis (optional)
    print("\n💾 Testing Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6380, decode_responses=True)
        r.ping()
        
        # Set and get test value
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"✓ Redis set/get: {value}")
        
        # Clean up
        r.delete('test_key')
        
        print("✓ Redis is working correctly")
    except Exception as e:
        print(f"⚠️ Redis not available (optional): {e}")
    
    # Test 5: Cross-database references
    print("\n🔗 Testing Reference Format...")
    refs = [
        "neo4j://entity/ent_123",
        "sqlite://mention/ment_456",
        "faiss://vector/vec_789"
    ]
    
    for ref in refs:
        parts = ref.split("://")
        storage = parts[0]
        type_id = parts[1].split("/")
        obj_type = type_id[0]
        obj_id = type_id[1]
        print(f"✓ Parsed {ref} -> storage={storage}, type={obj_type}, id={obj_id}")
    
    print("\n✅ All database tests passed!")
    print("=" * 50)
    return True


def test_integration_workflow():
    """Test a simple integration workflow."""
    print("\n🔄 Testing Integration Workflow")
    print("=" * 50)
    
    try:
        # 1. Create document in SQLite
        print("\n1️⃣ Creating document in SQLite...")
        db_path = Path("./data/test_workflow.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO documents (id, title)
            VALUES (?, ?)
        """, ("doc_001", "Test Document"))
        
        conn.commit()
        print("✓ Document created: doc_001")
        
        # 2. Create entity in Neo4j
        print("\n2️⃣ Creating entity in Neo4j...")
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        
        with driver.session() as session:
            session.run("""
                CREATE (e:Entity {
                    id: 'ent_001',
                    name: 'Apple Inc.',
                    document_ref: 'sqlite://document/doc_001'
                })
            """)
        print("✓ Entity created: ent_001")
        
        # 3. Create vector in FAISS
        print("\n3️⃣ Creating vector in FAISS...")
        dimension = 384
        index = faiss.IndexFlatL2(dimension)
        
        vector = np.random.rand(1, dimension).astype('float32')
        index.add(vector)
        
        print(f"✓ Vector added (dimension: {dimension})")
        
        # 4. Query across databases
        print("\n4️⃣ Cross-database query...")
        
        # Get entity from Neo4j
        with driver.session() as session:
            result = session.run("""
                MATCH (e:Entity {id: 'ent_001'})
                RETURN e.document_ref as doc_ref
            """)
            doc_ref = result.single()['doc_ref']
            print(f"✓ Found document reference: {doc_ref}")
        
        # Parse reference and query SQLite
        if doc_ref.startswith("sqlite://document/"):
            doc_id = doc_ref.split("/")[-1]
            cursor.execute("SELECT title FROM documents WHERE id = ?", (doc_id,))
            title = cursor.fetchone()[0]
            print(f"✓ Retrieved document: {title}")
        
        # 5. Cleanup
        print("\n5️⃣ Cleaning up...")
        with driver.session() as session:
            session.run("MATCH (e:Entity {id: 'ent_001'}) DELETE e")
        driver.close()
        
        conn.close()
        if db_path.exists():
            db_path.unlink()
        
        print("\n✅ Integration workflow completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Workflow error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Run tests
    if test_databases():
        test_integration_workflow()