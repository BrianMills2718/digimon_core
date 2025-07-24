"""
Unit tests for distributed transactions without requiring real databases.

Tests the transaction manager logic with mocked database connections.
"""

import pytest
import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Import the fixture from our no-docker conftest
from .conftest_no_docker import test_distributed_tx_manager_mock, sqlite_db, mock_neo4j_driver


class TestDistributedTransactionsUnit:
    """Unit tests with mocked databases."""
    
    @pytest.mark.asyncio
    async def test_both_databases_commit_on_success(self, test_distributed_tx_manager_mock):
        """Both databases should commit when all operations succeed."""
        manager, neo4j_tx_mock = test_distributed_tx_manager_mock
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
        
        # Execute distributed transaction
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        result = await manager.commit_all(tx_id)
        
        # Verify both committed
        assert result["status"] == "committed"
        assert result["neo4j_committed"] is True
        assert result["sqlite_committed"] is True
        
        # Verify Neo4j methods were called
        neo4j_tx_mock.run.assert_called()
        neo4j_tx_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rollback_on_neo4j_failure(self, test_distributed_tx_manager_mock):
        """Both databases should rollback when Neo4j fails."""
        manager, neo4j_tx_mock = test_distributed_tx_manager_mock
        tx_id = str(uuid.uuid4())
        
        # Configure Neo4j to fail
        neo4j_tx_mock.run.side_effect = Exception("Neo4j connection error")
        
        # Define operations
        neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": "test456"}}]
        sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["test456"]}]
        
        await manager.begin_transaction(tx_id)
        
        # Neo4j prepare should fail
        with pytest.raises(Exception, match="Neo4j connection error"):
            await manager.prepare_neo4j(tx_id, neo4j_ops)
        
        # Rollback should be called
        result = await manager.rollback_all(tx_id)
        assert result["status"] == "rolled_back"
        
        # Verify Neo4j rollback was called
        neo4j_tx_mock.rollback.assert_called()
    
    @pytest.mark.asyncio
    async def test_transaction_state_tracking(self, test_distributed_tx_manager_mock):
        """Transaction state should be accurately tracked."""
        manager, _ = test_distributed_tx_manager_mock
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
        
        # Prepare SQLite
        sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": ["state123"]}]
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        state = await manager.get_transaction_state(tx_id)
        assert state["sqlite_prepared"] is True
        assert state["status"] == "prepared"
    
    @pytest.mark.asyncio
    async def test_concurrent_transactions(self, test_distributed_tx_manager_mock):
        """Multiple transactions should be handled independently."""
        manager, _ = test_distributed_tx_manager_mock
        
        # Create multiple transactions
        tx_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        async def execute_transaction(tx_id, entity_id):
            neo4j_ops = [{"query": "CREATE (n:Entity {id: $id})", "params": {"id": entity_id}}]
            sqlite_ops = [{"query": "INSERT INTO entities (id) VALUES (?)", "params": [entity_id]}]
            
            await manager.begin_transaction(tx_id)
            await manager.prepare_neo4j(tx_id, neo4j_ops)
            await manager.prepare_sqlite(tx_id, sqlite_ops)
            return await manager.commit_all(tx_id)
        
        # Execute transactions concurrently
        tasks = [
            execute_transaction(tx_id, f"entity{i}")
            for i, tx_id in enumerate(tx_ids)
        ]
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        assert len(results) == 3
        for result in results:
            assert result["status"] == "committed"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, test_distributed_tx_manager_mock):
        """Transactions should timeout appropriately."""
        manager, neo4j_tx_mock = test_distributed_tx_manager_mock
        manager.timeout_seconds = 0.1  # Very short timeout
        
        tx_id = str(uuid.uuid4())
        
        # Make Neo4j operation slow
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(0.5)
        
        neo4j_tx_mock.run = slow_operation
        
        await manager.begin_transaction(tx_id)
        
        # Should timeout
        with pytest.raises(asyncio.TimeoutError):
            await manager.prepare_neo4j(tx_id, [{"query": "SLOW QUERY"}])
        
        # State should reflect failure
        state = await manager.get_transaction_state(tx_id)
        assert state["status"] == "failed"
    
    @pytest.mark.asyncio
    async def test_partial_commit_handling(self, test_distributed_tx_manager_mock):
        """System should handle partial commits gracefully."""
        manager, neo4j_tx_mock = test_distributed_tx_manager_mock
        tx_id = str(uuid.uuid4())
        
        # Prepare both successfully
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, [{"query": "CREATE (n:Entity)"}])
        await manager.prepare_sqlite(tx_id, [{"query": "INSERT INTO entities (id) VALUES (?)"}])
        
        # Make SQLite commit fail
        state = manager._transactions[tx_id]
        original_conn = state.sqlite_conn
        original_conn.commit = AsyncMock(side_effect=Exception("Disk full"))
        
        # Attempt commit
        result = await manager.commit_all(tx_id)
        
        # Should indicate partial failure
        assert result["status"] == "partial_failure"
        assert result["recovery_needed"] is True
        assert "SQLite commit failed" in str(result["errors"])
    
    @pytest.mark.asyncio
    async def test_cleanup_mechanism(self, test_distributed_tx_manager_mock):
        """Old transactions should be cleaned up."""
        manager, _ = test_distributed_tx_manager_mock
        manager.cleanup_after_seconds = 0.5
        
        # Create transaction
        tx_id = str(uuid.uuid4())
        await manager.begin_transaction(tx_id)
        
        # Should exist
        assert await manager.get_transaction_state(tx_id) is not None
        
        # Wait for cleanup threshold
        await asyncio.sleep(0.6)
        
        # Run cleanup
        cleaned = await manager.cleanup_old_transactions()
        assert cleaned == 1
        
        # Should be gone
        assert await manager.get_transaction_state(tx_id) is None