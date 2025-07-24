"""
Simple unit tests for distributed transactions without external dependencies.

Tests core transaction logic with in-memory SQLite and mocked Neo4j.
"""

import pytest
import asyncio
import uuid
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock
import aiosqlite
from datetime import datetime

from src.core.distributed_transaction_manager import DistributedTransactionManager


class TestDistributedTransactionsSimple:
    """Simple unit tests without complex fixtures."""
    
    async def setup_sqlite_db(self):
        """Create and initialize a temporary SQLite database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / "test.db")
        
        # Initialize schema
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE entities (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        
        return self.db_path
    
    async def teardown_sqlite_db(self):
        """Clean up temporary database."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def create_mock_neo4j(self):
        """Create mock Neo4j driver and session."""
        driver = AsyncMock()
        session = AsyncMock()
        tx = AsyncMock()
        
        # Configure mock behavior
        driver.session.return_value = session
        session.begin_transaction = AsyncMock(return_value=tx)
        
        # Mock transaction methods
        tx.run = AsyncMock()
        tx.commit = AsyncMock()
        tx.rollback = AsyncMock()
        
        return driver, session, tx
    
    async def create_manager(self):
        """Create a distributed transaction manager with test dependencies."""
        # Setup SQLite
        db_path = await self.setup_sqlite_db()
        
        # Setup Neo4j mocks
        driver, session, tx = self.create_mock_neo4j()
        
        # Create manager
        manager = DistributedTransactionManager()
        
        # Override connection methods
        async def get_neo4j_session():
            return session
        
        async def get_sqlite_connection():
            return await aiosqlite.connect(db_path)
        
        manager._get_neo4j_session = get_neo4j_session
        manager._get_sqlite_connection = get_sqlite_connection
        
        return manager, tx
    
    @pytest.mark.asyncio
    async def test_successful_distributed_commit(self):
        """Test successful commit across both databases."""
        manager, neo4j_tx = await self.create_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Define operations
            neo4j_ops = [
                {"query": "CREATE (n:Entity {id: $id, name: $name})", 
                 "params": {"id": "test123", "name": "Test Entity"}}
            ]
            sqlite_ops = [
                {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
                 "params": ["test123", "Test Entity"]}
            ]
            
            # Execute transaction
            await manager.begin_transaction(tx_id)
            await manager.prepare_neo4j(tx_id, neo4j_ops)
            await manager.prepare_sqlite(tx_id, sqlite_ops)
            result = await manager.commit_all(tx_id)
            
            # Verify success
            assert result["status"] == "committed"
            assert result["neo4j_committed"] is True
            assert result["sqlite_committed"] is True
            
            # Verify Neo4j mock was called correctly
            neo4j_tx.run.assert_called_with(
                "CREATE (n:Entity {id: $id, name: $name})",
                {"id": "test123", "name": "Test Entity"}
            )
            neo4j_tx.commit.assert_called_once()
            
            # Verify SQLite data
            async with aiosqlite.connect(manager._sqlite_path) as db:
                cursor = await db.execute("SELECT name FROM entities WHERE id = ?", ["test123"])
                row = await cursor.fetchone()
                assert row[0] == "Test Entity"
                
        finally:
            await self.teardown_sqlite_db()
    
    @pytest.mark.asyncio
    async def test_rollback_on_failure(self):
        """Test rollback when Neo4j fails."""
        manager, neo4j_tx = await self.create_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Make Neo4j fail
            neo4j_tx.run.side_effect = Exception("Connection lost")
            
            # Define operations
            neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": "fail123"}}]
            sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["fail123"]}]
            
            await manager.begin_transaction(tx_id)
            
            # Should fail during prepare
            with pytest.raises(Exception, match="Connection lost"):
                await manager.prepare_neo4j(tx_id, neo4j_ops)
            
            # Rollback
            result = await manager.rollback_all(tx_id)
            assert result["status"] == "rolled_back"
            
            # Verify rollback was called
            neo4j_tx.rollback.assert_called()
            
            # Verify no data in SQLite
            async with aiosqlite.connect(manager._sqlite_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM entities WHERE id = ?", ["fail123"])
                count = await cursor.fetchone()
                assert count[0] == 0
                
        finally:
            await self.teardown_sqlite_db()
    
    @pytest.mark.asyncio
    async def test_transaction_state_management(self):
        """Test transaction state tracking."""
        manager, _ = await self.create_manager()
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Begin
            await manager.begin_transaction(tx_id)
            state = await manager.get_transaction_state(tx_id)
            assert state["status"] == "active"
            
            # Prepare Neo4j
            await manager.prepare_neo4j(tx_id, [{"query": "CREATE (n:Entity)"}])
            state = await manager.get_transaction_state(tx_id)
            assert state["neo4j_prepared"] is True
            assert state["sqlite_prepared"] is False
            
            # Prepare SQLite
            await manager.prepare_sqlite(tx_id, [{"query": "INSERT INTO entities (id) VALUES (?)"}])
            state = await manager.get_transaction_state(tx_id)
            assert state["neo4j_prepared"] is True
            assert state["sqlite_prepared"] is True
            assert state["status"] == "prepared"
            
        finally:
            await self.teardown_sqlite_db()
    
    @pytest.mark.asyncio
    async def test_concurrent_transaction_isolation(self):
        """Test multiple concurrent transactions."""
        manager, _ = await self.create_manager()
        
        try:
            async def run_transaction(tx_id, entity_id):
                await manager.begin_transaction(tx_id)
                await manager.prepare_neo4j(tx_id, [
                    {"query": "CREATE (n:Entity {id: $id})", "params": {"id": entity_id}}
                ])
                await manager.prepare_sqlite(tx_id, [
                    {"query": "INSERT INTO entities (id) VALUES (?)", "params": [entity_id]}
                ])
                return await manager.commit_all(tx_id)
            
            # Run 3 transactions concurrently
            tx_ids = [str(uuid.uuid4()) for _ in range(3)]
            tasks = [
                run_transaction(tx_id, f"entity{i}")
                for i, tx_id in enumerate(tx_ids)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 3
            for result in results:
                assert result["status"] == "committed"
            
            # Verify all entities in SQLite
            async with aiosqlite.connect(manager._sqlite_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM entities")
                count = await cursor.fetchone()
                assert count[0] == 3
                
        finally:
            await self.teardown_sqlite_db()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test transaction timeout."""
        manager, neo4j_tx = await self.create_manager()
        manager.timeout_seconds = 0.1  # 100ms timeout
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Make operation slow
            async def slow_op(*args, **kwargs):
                await asyncio.sleep(0.5)
            
            neo4j_tx.run = slow_op
            
            await manager.begin_transaction(tx_id)
            
            # Should timeout
            with pytest.raises(asyncio.TimeoutError):
                await manager.prepare_neo4j(tx_id, [{"query": "SLOW"}])
            
            # Check state
            state = await manager.get_transaction_state(tx_id)
            assert state["status"] == "failed"
            assert "timeout" in str(state["errors"])
            
        finally:
            await self.teardown_sqlite_db()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_transactions(self):
        """Test cleanup of old transactions."""
        manager, _ = await self.create_manager()
        manager.cleanup_after_seconds = 0.5
        
        try:
            tx_id = str(uuid.uuid4())
            
            # Create transaction
            await manager.begin_transaction(tx_id)
            assert await manager.get_transaction_state(tx_id) is not None
            
            # Wait for cleanup threshold
            await asyncio.sleep(0.6)
            
            # Clean up
            cleaned = await manager.cleanup_old_transactions()
            assert cleaned == 1
            
            # Should be gone
            assert await manager.get_transaction_state(tx_id) is None
            
        finally:
            await self.teardown_sqlite_db()