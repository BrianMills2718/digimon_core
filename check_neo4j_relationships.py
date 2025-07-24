"""Check relationships in Neo4j."""

import asyncio
from neo4j import AsyncGraphDatabase


async def check_relationships():
    """Query Neo4j to see relationships."""
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    
    try:
        async with driver.session() as session:
            # Get all relationships
            result = await session.run("""
                MATCH (a)-[r]->(b)
                RETURN a.name as from_name, type(r) as rel_type, b.name as to_name, r as relationship
            """)
            
            print("Relationships in Neo4j:")
            async for record in result:
                rel_props = dict(record['relationship']) if record['relationship'] else {}
                props_str = f" {rel_props}" if rel_props else ""
                print(f"  {record['from_name']} --[{record['rel_type']}{props_str}]--> {record['to_name']}")
            
            # Show graph statistics
            result = await session.run("""
                MATCH (n)
                RETURN count(n) as node_count
            """)
            stats = await result.single()
            
            result = await session.run("""
                MATCH ()-[r]->()
                RETURN count(r) as rel_count
            """)
            rel_stats = await result.single()
            
            print(f"\nGraph statistics:")
            print(f"  Total nodes: {stats['node_count']}")
            print(f"  Total relationships: {rel_stats['rel_count']}")
                
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(check_relationships())