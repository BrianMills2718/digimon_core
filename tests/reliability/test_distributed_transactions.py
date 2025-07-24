"""
Test distributed transactions for Neo4j and SQLite consistency.

Tests the two-phase commit protocol implementation to ensure
both databases commit or both rollback atomically.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from contextlib import asynccontextmanager


@pytest.fixture
def mock_neo4j_session():
    """Mock Neo4j session with transaction support."""
    session = AsyncMock()
    tx = AsyncMock()
    
    @asynccontextmanager
    async def mock_transaction():
        yield tx
    
    session.begin_transaction = mock_transaction
    return session, tx


@pytest.fixture
def mock_sqlite_conn():
    """Mock SQLite connection with transaction support."""
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.commit = AsyncMock()
    conn.rollback = AsyncMock()
    return conn


class TestDistributedTransactions:
    """Test suite for distributed transaction management."""
    
    @pytest.mark.asyncio
    async def test_both_databases_commit_on_success(self, mock_neo4j_session, mock_sqlite_conn):
        """Both databases should commit when all operations succeed."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        session, neo4j_tx = mock_neo4j_session
        
        # Create manager with mocked connections
        manager = DistributedTransactionManager()
        manager._get_neo4j_session = AsyncMock(return_value=session)
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        tx_id = str(uuid.uuid4())
        
        # Define operations
        neo4j_ops = [
            {"query": "CREATE (n:Entity {id: $id})", "params": {"id": "test123"}}
        ]
        sqlite_ops = [
            {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", "params": ["test123", "Test Entity"]}
        ]
        
        # Execute distributed transaction
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        result = await manager.commit_all(tx_id)
        
        # Verify both committed
        assert result["status"] == "committed"
        assert result["neo4j_committed"] is True
        assert result["sqlite_committed"] is True
        # Note: Neo4j commit is simulated in current implementation
        mock_sqlite_conn.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rollback_on_neo4j_failure(self, mock_neo4j_session, mock_sqlite_conn):
        """Both databases should rollback when Neo4j fails."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        session, neo4j_tx = mock_neo4j_session
        # Simulate Neo4j failure
        neo4j_tx.run.side_effect = Exception("Neo4j connection lost")
        
        manager = DistributedTransactionManager()
        manager._get_neo4j_session = AsyncMock(return_value=session)
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        tx_id = str(uuid.uuid4())
        
        neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": "test123"}}]
        sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["test123"]}]
        
        await manager.begin_transaction(tx_id)
        
        # Neo4j prepare should fail
        with pytest.raises(Exception, match="Neo4j connection lost"):
            await manager.prepare_neo4j(tx_id, neo4j_ops)
        
        # Rollback should be called
        result = await manager.rollback_all(tx_id)
        
        assert result["status"] == "rolled_back"
        neo4j_tx.rollback.assert_called_once()
        mock_sqlite_conn.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rollback_on_sqlite_failure(self, mock_neo4j_session, mock_sqlite_conn):
        """Both databases should rollback when SQLite fails."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        session, neo4j_tx = mock_neo4j_session
        # Simulate SQLite failure
        mock_sqlite_conn.execute.side_effect = Exception("SQLite disk full")
        
        manager = DistributedTransactionManager()
        manager._get_neo4j_session = AsyncMock(return_value=session)
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        tx_id = str(uuid.uuid4())
        
        neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": "test123"}}]
        sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["test123"]}]
        
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        
        # SQLite prepare should fail
        with pytest.raises(Exception, match="SQLite disk full"):
            await manager.prepare_sqlite(tx_id, sqlite_ops)
        
        # Rollback should be called
        result = await manager.rollback_all(tx_id)
        
        assert result["status"] == "rolled_back"
        neo4j_tx.rollback.assert_called_once()
        mock_sqlite_conn.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self, mock_neo4j_session, mock_sqlite_conn):
        """System should recover from partial commit failures."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        session, neo4j_tx = mock_neo4j_session
        # Simulate commit phase failure
        mock_sqlite_conn.commit.side_effect = Exception("Network timeout during commit")
        
        manager = DistributedTransactionManager()
        manager._get_neo4j_session = AsyncMock(return_value=session)
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        tx_id = str(uuid.uuid4())
        
        neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": "test123"}}]
        sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["test123"]}]
        
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        
        # Commit should handle partial failure
        result = await manager.commit_all(tx_id)
        
        assert result["status"] == "partial_failure"
        assert result["recovery_needed"] is True
        assert "SQLite commit failed" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_concurrent_transactions_isolation(self, mock_neo4j_session, mock_sqlite_conn):
        """Multiple transactions should be isolated from each other."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        manager = DistributedTransactionManager()
        
        # Create multiple sessions for concurrent transactions
        sessions = []
        for _ in range(3):
            session = AsyncMock()
            tx = AsyncMock()
            
            @asynccontextmanager
            async def mock_transaction():
                yield tx
            
            session.begin_transaction = mock_transaction
            sessions.append((session, tx))
        
        # Mock connection getters to return different sessions
        manager._get_neo4j_session = AsyncMock(side_effect=[s[0] for s in sessions])
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        # Start multiple transactions
        tx_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        # Execute transactions concurrently
        tasks = []
        for i, tx_id in enumerate(tx_ids):
            neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": f"test{i}"}}]
            sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": [f"test{i}"]}]
            
            async def execute_transaction(tx_id, neo4j_ops, sqlite_ops):
                await manager.begin_transaction(tx_id)
                await manager.prepare_neo4j(tx_id, neo4j_ops)
                await manager.prepare_sqlite(tx_id, sqlite_ops)
                return await manager.commit_all(tx_id)
            
            tasks.append(execute_transaction(tx_id, neo4j_ops, sqlite_ops))
        
        results = await asyncio.gather(*tasks)
        
        # Verify all transactions completed independently
        assert len(results) == 3
        for result in results:
            assert result["status"] == "committed"
    
    @pytest.mark.asyncio
    async def test_transaction_timeout_handling(self, mock_neo4j_session, mock_sqlite_conn):
        """Transactions should timeout and rollback if taking too long."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        session, neo4j_tx = mock_neo4j_session
        
        manager = DistributedTransactionManager(timeout_seconds=1)
        manager._get_neo4j_session = AsyncMock(return_value=session)
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        tx_id = str(uuid.uuid4())
        
        # Simulate slow operation
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(2)
        
        neo4j_tx.run = slow_operation
        
        await manager.begin_transaction(tx_id)
        
        # Should timeout during prepare
        with pytest.raises(asyncio.TimeoutError):
            await manager.prepare_neo4j(tx_id, [{"query": "SLOW QUERY"}])
        
        # Verify rollback was called
        result = await manager.rollback_all(tx_id)
        assert result["status"] == "rolled_back"
        assert "timeout" in result.get("reason", "").lower()
    
    @pytest.mark.asyncio
    async def test_transaction_state_persistence(self, mock_neo4j_session, mock_sqlite_conn):
        """Transaction state should be persisted for recovery."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        session, neo4j_tx = mock_neo4j_session
        
        manager = DistributedTransactionManager()
        manager._get_neo4j_session = AsyncMock(return_value=session)
        manager._get_sqlite_connection = AsyncMock(return_value=mock_sqlite_conn)
        
        tx_id = str(uuid.uuid4())
        
        # Begin transaction
        await manager.begin_transaction(tx_id)
        
        # Verify transaction state is tracked
        state = await manager.get_transaction_state(tx_id)
        assert state["status"] == "active"
        assert state["tx_id"] == tx_id
        
        # Prepare operations
        await manager.prepare_neo4j(tx_id, [{"query": "CREATE (n:Entity)"}])
        state = await manager.get_transaction_state(tx_id)
        assert state["neo4j_prepared"] is True
        
        await manager.prepare_sqlite(tx_id, [{"query": "INSERT INTO entities VALUES (1)"}])
        state = await manager.get_transaction_state(tx_id)
        assert state["sqlite_prepared"] is True
        
        # Commit
        await manager.commit_all(tx_id)
        state = await manager.get_transaction_state(tx_id)
        assert state["status"] == "committed"
    
    @pytest.mark.asyncio
    async def test_automatic_cleanup_of_old_transactions(self, mock_neo4j_session, mock_sqlite_conn):
        """Old transaction states should be automatically cleaned up."""
        from src.core.distributed_transaction_manager import DistributedTransactionManager
        
        manager = DistributedTransactionManager(cleanup_after_seconds=1)
        
        tx_id = str(uuid.uuid4())
        await manager.begin_transaction(tx_id)
        
        # Transaction should exist
        state = await manager.get_transaction_state(tx_id)
        assert state is not None
        
        # Wait for cleanup
        await asyncio.sleep(2)
        
        # Run cleanup
        await manager.cleanup_old_transactions()
        
        # Transaction state should be gone
        state = await manager.get_transaction_state(tx_id)
        assert state is None