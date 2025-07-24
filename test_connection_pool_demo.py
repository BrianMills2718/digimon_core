"""Demo of connection pool manager with real Neo4j."""

import asyncio
import time
from src.core.connection_pool_manager import ConnectionPoolManager


async def demo_connection_pool():
    """Demonstrate connection pooling with Neo4j."""
    print("🏊 Connection Pool Demo\n")
    
    # Create pool with Neo4j connections
    pool = ConnectionPoolManager(
        min_size=2,
        max_size=5,
        connection_type="neo4j",
        connection_params={
            'uri': 'bolt://localhost:7687',
            'auth': ('neo4j', 'testpassword')
        }
    )
    
    # Give pool time to initialize
    await asyncio.sleep(1)
    
    print("📊 Initial pool stats:")
    print(pool.get_stats())
    print()
    
    # Simulate concurrent workers
    async def worker(worker_id: int):
        print(f"Worker {worker_id}: Requesting connection...")
        start = time.time()
        
        # Acquire connection
        conn = await pool.acquire_connection()
        wait_time = time.time() - start
        print(f"Worker {worker_id}: Got connection after {wait_time:.2f}s")
        
        # Do some work
        result = await conn.run("CREATE (n:Worker {id: $id}) RETURN n.id as id", id=worker_id)
        record = await result.single()
        print(f"Worker {worker_id}: Created node with ID {record['id']}")
        
        # Simulate work
        await asyncio.sleep(0.5)
        
        # Release connection
        await pool.release_connection(conn)
        print(f"Worker {worker_id}: Released connection")
        
        return worker_id
    
    # Launch 10 workers (more than pool max)
    print("\n🚀 Launching 10 workers (pool max is 5)...\n")
    workers = [worker(i) for i in range(10)]
    results = await asyncio.gather(*workers)
    
    print(f"\n✅ All workers completed: {results}")
    
    # Show final statistics
    print("\n📊 Final pool statistics:")
    stats = pool.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    print("\n🧹 Shutting down pool...")
    await pool.shutdown()
    
    # Clean up test data
    from neo4j import AsyncGraphDatabase
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    async with driver.session() as session:
        await session.run("MATCH (n:Worker) DELETE n")
    await driver.close()
    
    print("✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo_connection_pool())