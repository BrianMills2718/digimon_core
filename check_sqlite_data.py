"""Check SQLite data from our tests."""

import asyncio
import aiosqlite
import os
import glob
import tempfile
from pathlib import Path


async def check_sqlite_databases():
    """Find and examine SQLite databases created by our tests."""
    print("Looking for SQLite databases...\n")
    
    # First, let's create a persistent SQLite database with our transaction manager
    from src.core.distributed_transaction_manager import DistributedTransactionManager
    
    # Create a SQLite database in the current directory (not temp)
    db_path = "demo_kgas.db"
    
    # Initialize database schema
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS entity_mappings (
                internal_id TEXT PRIMARY KEY,
                neo4j_id TEXT UNIQUE NOT NULL,
                entity_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        print(f"Created/opened SQLite database: {db_path}")
    
    # Let's also check what's in this database from previous runs
    async with aiosqlite.connect(db_path) as db:
        # Check entities table
        cursor = await db.execute("SELECT COUNT(*) FROM entities")
        count = await cursor.fetchone()
        print(f"\nCurrent entities in database: {count[0]}")
        
        if count[0] > 0:
            print("\nExisting entities:")
            cursor = await db.execute("SELECT id, name, created_at FROM entities ORDER BY created_at DESC LIMIT 10")
            async for row in cursor:
                print(f"  ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")
    
    # Now let's add some data using our distributed transaction manager
    from neo4j import AsyncGraphDatabase
    
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    
    manager = DistributedTransactionManager()
    
    async def get_neo4j_session():
        return driver.session()
    
    async def get_sqlite_connection():
        return await aiosqlite.connect(db_path)
    
    manager._get_neo4j_session = get_neo4j_session
    manager._get_sqlite_connection = get_sqlite_connection
    
    # Add some new data
    import uuid
    tx_id = str(uuid.uuid4())
    
    neo4j_ops = [
        {"query": "CREATE (n:Entity {id: $id, name: $name, type: $type})", 
         "params": {"id": "sqlite_test_1", "name": "SQLite Test Entity", "type": "Test"}}
    ]
    sqlite_ops = [
        {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
         "params": ["sqlite_test_1", "SQLite Test Entity"]}
    ]
    
    print("\n🔄 Creating new entity through distributed transaction...")
    await manager.begin_transaction(tx_id)
    await manager.prepare_neo4j(tx_id, neo4j_ops)
    await manager.prepare_sqlite(tx_id, sqlite_ops)
    result = await manager.commit_all(tx_id)
    print(f"Transaction result: {result['status']}")
    
    # Now check the SQLite database again
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT id, name FROM entities WHERE id = ?", ["sqlite_test_1"])
        row = await cursor.fetchone()
        if row:
            print(f"\n✅ Found in SQLite: ID={row[0]}, Name={row[1]}")
        
        # Show all entities
        print("\nAll entities in SQLite:")
        cursor = await db.execute("SELECT id, name, created_at FROM entities ORDER BY created_at DESC")
        async for row in cursor:
            print(f"  ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")
        
        # Check if we have any entity mappings
        cursor = await db.execute("SELECT COUNT(*) FROM entity_mappings")
        count = await cursor.fetchone()
        print(f"\nEntity mappings in database: {count[0]}")
    
    await driver.close()
    
    # Also show temporary database locations
    print(f"\n📁 Temporary databases are created in: {tempfile.gettempdir()}")
    print("(These are cleaned up after each test)")
    
    print(f"\n💾 Persistent SQLite database location: {os.path.abspath(db_path)}")
    print("You can open this with any SQLite browser/tool!")


if __name__ == "__main__":
    asyncio.run(check_sqlite_databases())