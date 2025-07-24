"""Demo script to create persistent data in Neo4j to prove we're using real database."""

import asyncio
import uuid
from neo4j import AsyncGraphDatabase
import aiosqlite
import tempfile
from pathlib import Path

from src.core.distributed_transaction_manager import DistributedTransactionManager


async def create_persistent_data():
    """Create data that will persist in Neo4j for inspection."""
    print("Creating persistent data in Neo4j...")
    
    # Setup SQLite
    temp_dir = tempfile.mkdtemp()
    db_path = str(Path(temp_dir) / "demo.db")
    
    # Initialize database schema
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE entities (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    
    # Setup Neo4j
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    
    # Create manager
    manager = DistributedTransactionManager()
    
    # Override connection methods
    async def get_neo4j_session():
        return driver.session()
    
    async def get_sqlite_connection():
        return await aiosqlite.connect(db_path)
    
    manager._get_neo4j_session = get_neo4j_session
    manager._get_sqlite_connection = get_sqlite_connection
    
    # Create several entities with distributed transactions
    entities = [
        ("person_1", "Alice Smith", "Person"),
        ("person_2", "Bob Jones", "Person"), 
        ("org_1", "Acme Corp", "Organization"),
        ("doc_1", "Important Document", "Document"),
        ("doc_2", "Research Paper", "Document")
    ]
    
    for entity_id, name, entity_type in entities:
        tx_id = str(uuid.uuid4())
        
        neo4j_ops = [
            {"query": "CREATE (n:Entity {id: $id, name: $name, type: $type, demo: true})", 
             "params": {"id": entity_id, "name": name, "type": entity_type}}
        ]
        sqlite_ops = [
            {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
             "params": [entity_id, name]}
        ]
        
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        result = await manager.commit_all(tx_id)
        
        print(f"Created {entity_type}: {name} (ID: {entity_id})")
    
    # Create some relationships
    async with driver.session() as session:
        # Alice works at Acme Corp
        await session.run("""
            MATCH (p:Entity {id: 'person_1'}), (o:Entity {id: 'org_1'})
            CREATE (p)-[:WORKS_AT {since: 2020}]->(o)
        """)
        
        # Bob authored Document 1
        await session.run("""
            MATCH (p:Entity {id: 'person_2'}), (d:Entity {id: 'doc_1'})
            CREATE (p)-[:AUTHORED]->(d)
        """)
        
        # Document 2 references Document 1
        await session.run("""
            MATCH (d1:Entity {id: 'doc_2'}), (d2:Entity {id: 'doc_1'})
            CREATE (d1)-[:REFERENCES]->(d2)
        """)
        
        print("\nCreated relationships:")
        print("- Alice WORKS_AT Acme Corp")
        print("- Bob AUTHORED Important Document")
        print("- Research Paper REFERENCES Important Document")
    
    print("\n✅ Data created successfully!")
    print("\n📊 You can now:")
    print("1. Open Neo4j Browser at http://localhost:7474")
    print("2. Login with username: neo4j, password: testpassword")
    print("3. Run this query to see the data: MATCH (n) RETURN n")
    print("4. Or run: python check_neo4j_data.py")
    
    await driver.close()


if __name__ == "__main__":
    asyncio.run(create_persistent_data())