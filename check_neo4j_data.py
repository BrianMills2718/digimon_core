"""Check what data is actually in Neo4j from our tests."""

import asyncio
from neo4j import AsyncGraphDatabase


async def check_neo4j_data():
    """Query Neo4j to see what's actually in there."""
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    
    try:
        async with driver.session() as session:
            # Count all nodes
            result = await session.run("MATCH (n) RETURN count(n) as count")
            record = await result.single()
            print(f"Total nodes in Neo4j: {record['count']}")
            
            # Get all Entity nodes
            result = await session.run("""
                MATCH (n:Entity) 
                RETURN n.id as id, n.name as name, n.type as type, labels(n) as labels
                LIMIT 20
            """)
            
            print("\nEntity nodes found:")
            async for record in result:
                print(f"  ID: {record['id']}, Name: {record['name']}, Type: {record['type']}, Labels: {record['labels']}")
            
            # Get all TestNode nodes (from our connection test)
            result = await session.run("MATCH (n:TestNode) RETURN n.name as name")
            print("\nTestNode nodes found:")
            async for record in result:
                print(f"  Name: {record['name']}")
            
            # Show all node labels in the database
            result = await session.run("CALL db.labels() YIELD label RETURN label")
            print("\nAll node labels in database:")
            async for record in result:
                print(f"  - {record['label']}")
                
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(check_neo4j_data())