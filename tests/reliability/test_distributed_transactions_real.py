"""
Real integration tests for distributed transactions with Neo4j and SQLite.

These tests use actual database instances to verify the two-phase commit protocol.
"""

import pytest
import asyncio
import uuid
import tempfile
import shutil
from pathlib import Path
import aiosqlite
from neo4j import AsyncGraphDatabase
from datetime import datetime

from src.core.distributed_transaction_manager import DistributedTransactionManager


class TestDistributedTransactionsReal:
    """Integration tests with real Neo4j and SQLite databases."""
    
    async def setup_manager(self):
        """Set up a distributed transaction manager with real databases."""
        # Setup SQLite
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / "test.db")
        
        # Initialize database schema
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE entities (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        
        # Setup Neo4j
        self.driver = AsyncGraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        
        # Clear Neo4j
        async with self.driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")
        
        # Create manager
        manager = DistributedTransactionManager()
        
        # Override connection methods
        async def get_neo4j_session():
            return self.driver.session()
        
        async def get_sqlite_connection():
            return await aiosqlite.connect(self.db_path)
        
        manager._get_neo4j_session = get_neo4j_session
        manager._get_sqlite_connection = get_sqlite_connection
        
        return manager
    
    async def cleanup(self):
        """Clean up test resources."""
        if hasattr(self, 'driver'):
            await self.driver.close()
        if hasattr(self, 'temp_dir'):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
    
    @pytest.mark.asyncio
    async def test_successful_distributed_commit(self):
        """Test successful commit across both databases."""
        manager = await self.setup_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Define operations
            neo4j_ops = [
                {"query": "CREATE (n:Entity {id: $id, name: $name, type: $type})", 
                 "params": {"id": "test123", "name": "Test Entity", "type": "TestType"}}
            ]
            sqlite_ops = [
                {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
                 "params": ["test123", "Test Entity"]}
            ]
            
            # Execute distributed transaction
            await manager.begin_transaction(tx_id)
            await manager.prepare_neo4j(tx_id, neo4j_ops)
            await manager.prepare_sqlite(tx_id, sqlite_ops)
            result = await manager.commit_all(tx_id)
            
            # Verify success
            assert result["status"] == "committed"
            assert result["neo4j_committed"] is True
            assert result["sqlite_committed"] is True
            
            # Verify data in Neo4j
            async with self.driver.session() as session:
                neo4j_result = await session.run(
                    "MATCH (n:Entity {id: $id}) RETURN n.name as name, n.type as type",
                    {"id": "test123"}
                )
                record = await neo4j_result.single()
                assert record is not None
                assert record["name"] == "Test Entity"
                assert record["type"] == "TestType"
            
            # Verify data in SQLite
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT name FROM entities WHERE id = ?", ["test123"])
                row = await cursor.fetchone()
                assert row is not None
                assert row[0] == "Test Entity"
                
        finally:
            await self.cleanup()
    
    @pytest.mark.asyncio
    async def test_rollback_on_neo4j_failure(self):
        """Test rollback when Neo4j operation fails."""
        manager = await self.setup_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Invalid Neo4j query
            neo4j_ops = [
                {"query": "INVALID CYPHER QUERY", "params": {}}
            ]
            sqlite_ops = [
                {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
                 "params": ["rollback123", "Should Not Exist"]}
            ]
            
            await manager.begin_transaction(tx_id)
            
            # Neo4j prepare should fail
            with pytest.raises(Exception):
                await manager.prepare_neo4j(tx_id, neo4j_ops)
            
            # Rollback
            result = await manager.rollback_all(tx_id)
            assert result["status"] == "rolled_back"
            
            # Verify no data in SQLite
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM entities WHERE id = ?", ["rollback123"])
                count = await cursor.fetchone()
                assert count[0] == 0
                
        finally:
            await self.cleanup()
    
    @pytest.mark.asyncio
    async def test_rollback_on_sqlite_failure(self):
        """Test rollback when SQLite operation fails."""
        manager = await self.setup_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Valid Neo4j query
            neo4j_ops = [
                {"query": "CREATE (n:Entity {id: $id})", "params": {"id": "rollback456"}}
            ]
            # Invalid SQLite query (missing column)
            sqlite_ops = [
                {"query": "INSERT INTO entities (id, invalid_column) VALUES (?, ?)", 
                 "params": ["rollback456", "value"]}
            ]
            
            await manager.begin_transaction(tx_id)
            await manager.prepare_neo4j(tx_id, neo4j_ops)
            
            # SQLite prepare should fail
            with pytest.raises(Exception):
                await manager.prepare_sqlite(tx_id, sqlite_ops)
            
            # Rollback
            result = await manager.rollback_all(tx_id)
            assert result["status"] == "rolled_back"
            
            # Verify no data in Neo4j
            async with self.driver.session() as session:
                neo4j_result = await session.run(
                    "MATCH (n:Entity {id: $id}) RETURN count(n) as count",
                    {"id": "rollback456"}
                )
                record = await neo4j_result.single()
                assert record["count"] == 0
                
        finally:
            await self.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_transactions(self):
        """Test multiple concurrent transactions."""
        manager = await self.setup_manager()
        
        try:
            async def execute_transaction(tx_index):
                tx_id = str(uuid.uuid4())
                entity_id = f"concurrent_{tx_index}"
                
                neo4j_ops = [
                    {"query": "CREATE (n:Entity {id: $id, index: $index})", 
                     "params": {"id": entity_id, "index": tx_index}}
                ]
                sqlite_ops = [
                    {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
                     "params": [entity_id, f"Concurrent {tx_index}"]}
                ]
                
                await manager.begin_transaction(tx_id)
                await manager.prepare_neo4j(tx_id, neo4j_ops)
                await manager.prepare_sqlite(tx_id, sqlite_ops)
                return await manager.commit_all(tx_id)
            
            # Execute 5 transactions concurrently
            tasks = [execute_transaction(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            for result in results:
                assert result["status"] == "committed"
            
            # Verify all data in Neo4j
            async with self.driver.session() as session:
                neo4j_result = await session.run("MATCH (n:Entity) RETURN count(n) as count")
                record = await neo4j_result.single()
                assert record["count"] == 5
            
            # Verify all data in SQLite
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM entities")
                count = await cursor.fetchone()
                assert count[0] == 5
                
        finally:
            await self.cleanup()
    
    @pytest.mark.asyncio
    async def test_transaction_state_tracking(self):
        """Test transaction state is properly tracked."""
        manager = await self.setup_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Begin transaction
            await manager.begin_transaction(tx_id)
            state = await manager.get_transaction_state(tx_id)
            assert state["status"] == "active"
            assert state["neo4j_prepared"] is False
            assert state["sqlite_prepared"] is False
            
            # Prepare Neo4j
            neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": "state123"}}]
            await manager.prepare_neo4j(tx_id, neo4j_ops)
            state = await manager.get_transaction_state(tx_id)
            assert state["neo4j_prepared"] is True
            assert state["sqlite_prepared"] is False
            
            # Prepare SQLite
            sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["state123"]}]
            await manager.prepare_sqlite(tx_id, sqlite_ops)
            state = await manager.get_transaction_state(tx_id)
            assert state["neo4j_prepared"] is True
            assert state["sqlite_prepared"] is True
            assert state["status"] == "prepared"
            
            # Commit
            await manager.commit_all(tx_id)
            state = await manager.get_transaction_state(tx_id)
            assert state["status"] == "committed"
            
        finally:
            await self.cleanup()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test transaction timeout behavior."""
        manager = await self.setup_manager()
        manager.timeout_seconds = 0.5  # 500ms timeout
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Create a very large operation that will timeout
            neo4j_ops = []
            for i in range(1000):
                neo4j_ops.append({
                    "query": "CREATE (n:Entity {id: $id, data: $data})",
                    "params": {"id": f"timeout_{i}", "data": "x" * 10000}
                })
            
            await manager.begin_transaction(tx_id)
            
            # Should timeout
            with pytest.raises(asyncio.TimeoutError):
                await manager.prepare_neo4j(tx_id, neo4j_ops)
            
            # Transaction should be failed
            state = await manager.get_transaction_state(tx_id)
            assert state["status"] == "failed"
            
        finally:
            await self.cleanup()