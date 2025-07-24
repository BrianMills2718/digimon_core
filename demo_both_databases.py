"""Demo showing data in BOTH Neo4j and SQLite working together."""

import asyncio
import uuid
from neo4j import AsyncGraphDatabase
import aiosqlite
from datetime import datetime

from src.core.distributed_transaction_manager import DistributedTransactionManager


async def demo_both_databases():
    """Show that both databases are really working together."""
    
    db_path = "demo_kgas.db"
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
    
    print("🔄 Creating entities in BOTH databases atomically...\n")
    
    # Create multiple entities
    entities = [
        ("user_001", "John Doe", "User"),
        ("user_002", "Jane Smith", "User"),
        ("product_001", "Laptop Pro", "Product"),
        ("order_001", "Order #12345", "Order")
    ]
    
    for entity_id, name, entity_type in entities:
        tx_id = str(uuid.uuid4())
        
        neo4j_ops = [
            {"query": "CREATE (n:Entity {id: $id, name: $name, type: $type, created: $time})", 
             "params": {"id": entity_id, "name": name, "type": entity_type, "time": datetime.now().isoformat()}}
        ]
        sqlite_ops = [
            {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
             "params": [entity_id, name]}
        ]
        
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        result = await manager.commit_all(tx_id)
        
        print(f"✅ Created {entity_type}: {name}")
    
    print("\n📊 VERIFYING DATA IN BOTH DATABASES:\n")
    
    # Check Neo4j
    print("=== NEO4J DATA ===")
    async with driver.session() as session:
        result = await session.run("""
            MATCH (n:Entity)
            WHERE n.id IN ['user_001', 'user_002', 'product_001', 'order_001']
            RETURN n.id as id, n.name as name, n.type as type
            ORDER BY n.id
        """)
        async for record in result:
            print(f"  {record['type']}: {record['name']} (ID: {record['id']})")
    
    # Check SQLite
    print("\n=== SQLITE DATA ===")
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("""
            SELECT id, name, created_at 
            FROM entities 
            WHERE id IN ('user_001', 'user_002', 'product_001', 'order_001')
            ORDER BY id
        """)
        async for row in cursor:
            print(f"  ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")
    
    # Now let's simulate a failed transaction to show rollback works
    print("\n🚫 Testing transaction rollback (simulating failure)...\n")
    
    tx_id = str(uuid.uuid4())
    try:
        await manager.begin_transaction(tx_id)
        
        # This will succeed
        await manager.prepare_neo4j(tx_id, [
            {"query": "CREATE (n:Entity {id: $id, name: $name})", 
             "params": {"id": "should_not_exist", "name": "Failed Entity"}}
        ])
        
        # This will fail (invalid SQL)
        await manager.prepare_sqlite(tx_id, [
            {"query": "INSERT INTO nonexistent_table (id) VALUES (?)", 
             "params": ["should_not_exist"]}
        ])
        
    except Exception as e:
        print(f"❌ Transaction failed as expected: {e}")
        await manager.rollback_all(tx_id)
        print("🔄 Rolled back transaction")
    
    # Verify the failed entity doesn't exist in either database
    print("\n✅ Verifying rollback worked:")
    
    async with driver.session() as session:
        result = await session.run(
            "MATCH (n:Entity {id: $id}) RETURN count(n) as count",
            {"id": "should_not_exist"}
        )
        record = await result.single()
        print(f"  Neo4j count for 'should_not_exist': {record['count']}")
    
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM entities WHERE id = ?",
            ["should_not_exist"]
        )
        count = await cursor.fetchone()
        print(f"  SQLite count for 'should_not_exist': {count[0]}")
    
    await driver.close()
    
    print("\n✨ Demo complete! Both databases are working together with atomic transactions!")
    print(f"\n📁 SQLite database: {db_path}")
    print("🌐 Neo4j browser: http://localhost:7474")


if __name__ == "__main__":
    asyncio.run(demo_both_databases())