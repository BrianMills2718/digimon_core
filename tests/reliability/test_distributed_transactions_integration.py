"""
Integration tests for distributed transactions with real databases.

Tests the two-phase commit protocol implementation with actual
Neo4j and SQLite instances.
"""

import pytest
import asyncio
import uuid
from datetime import datetime


class TestDistributedTransactionsIntegration:
    """Integration tests with real databases."""
    
    @pytest.mark.asyncio
    async def test_both_databases_commit_on_success(self, real_distributed_tx_manager):
        """Both databases should commit when all operations succeed."""
        manager = real_distributed_tx_manager
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
        
        # Verify data exists in both databases
        # Check Neo4j
        neo4j_session = await manager._get_neo4j_session()
        neo4j_result = await neo4j_session.run(
            "MATCH (n:Entity {id: $id}) RETURN n.name as name",
            {"id": "test123"}
        )
        records = await neo4j_result.single()
        assert records["name"] == "Test Entity"
        await neo4j_session.close()
        
        # Check SQLite
        sqlite_conn = await manager._get_sqlite_connection()
        cursor = await sqlite_conn.execute(
            "SELECT name FROM entities WHERE id = ?",
            ["test123"]
        )
        row = await cursor.fetchone()
        assert row[0] == "Test Entity"
        await sqlite_conn.close()
    
    @pytest.mark.asyncio
    async def test_rollback_on_neo4j_failure(self, real_distributed_tx_manager):
        """Both databases should rollback when Neo4j fails."""
        manager = real_distributed_tx_manager
        tx_id = str(uuid.uuid4())
        
        # Define operations - Neo4j query will fail due to syntax error
        neo4j_ops = [
            {"query": "INVALID CYPHER SYNTAX", "params": {}}
        ]
        sqlite_ops = [
            {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
             "params": ["test456", "Should Not Exist"]}
        ]
        
        await manager.begin_transaction(tx_id)
        
        # Neo4j prepare should fail
        with pytest.raises(Exception):
            await manager.prepare_neo4j(tx_id, neo4j_ops)
        
        # Rollback should be called
        result = await manager.rollback_all(tx_id)
        assert result["status"] == "rolled_back"
        
        # Verify no data was committed to SQLite
        sqlite_conn = await manager._get_sqlite_connection()
        cursor = await sqlite_conn.execute(
            "SELECT COUNT(*) FROM entities WHERE id = ?",
            ["test456"]
        )
        count = await cursor.fetchone()
        assert count[0] == 0
        await sqlite_conn.close()
    
    @pytest.mark.asyncio
    async def test_rollback_on_sqlite_failure(self, real_distributed_tx_manager):
        """Both databases should rollback when SQLite fails."""
        manager = real_distributed_tx_manager
        tx_id = str(uuid.uuid4())
        
        # Define operations - SQLite will fail due to invalid column
        neo4j_ops = [
            {"query": "CREATE (n:Entity {id: $id})", "params": {"id": "test789"}}
        ]
        sqlite_ops = [
            {"query": "INSERT INTO entities (id, invalid_column) VALUES (?, ?)", 
             "params": ["test789", "value"]}
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
        neo4j_session = await manager._get_neo4j_session()
        neo4j_result = await neo4j_session.run(
            "MATCH (n:Entity {id: $id}) RETURN count(n) as count",
            {"id": "test789"}
        )
        records = await neo4j_result.single()
        assert records["count"] == 0
        await neo4j_session.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_transactions_isolation(self, real_distributed_tx_manager):
        """Multiple transactions should be isolated from each other."""
        manager = real_distributed_tx_manager
        
        # Create multiple transactions
        tx_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        async def execute_transaction(tx_id, entity_id):
            neo4j_ops = [
                {"query": "CREATE (n:Entity {id: $id, tx: $tx})", 
                 "params": {"id": entity_id, "tx": tx_id}}
            ]
            sqlite_ops = [
                {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
                 "params": [entity_id, f"Entity-{tx_id[:8]}"]}
            ]
            
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
        
        # Verify all entities exist
        sqlite_conn = await manager._get_sqlite_connection()
        cursor = await sqlite_conn.execute("SELECT COUNT(*) FROM entities")
        count = await cursor.fetchone()
        assert count[0] == 3
        await sqlite_conn.close()
    
    @pytest.mark.asyncio
    async def test_transaction_timeout_handling(self, real_distributed_tx_manager):
        """Transactions should timeout and rollback if taking too long."""
        # Create manager with very short timeout
        manager = real_distributed_tx_manager
        manager.timeout_seconds = 0.1  # 100ms timeout
        
        tx_id = str(uuid.uuid4())
        
        # Define slow operation (simulated with large data)
        # Create many nodes which should take longer than timeout
        neo4j_ops = [
            {"query": "UNWIND range(1, 10000) as i CREATE (n:Entity {id: $id + toString(i)})", 
             "params": {"id": "slow"}}
        ]
        
        await manager.begin_transaction(tx_id)
        
        # Should timeout during prepare
        with pytest.raises(asyncio.TimeoutError):
            await manager.prepare_neo4j(tx_id, neo4j_ops)
        
        # Transaction should be marked as failed
        state = await manager.get_transaction_state(tx_id)
        assert state["status"] == "failed"
        assert "timeout" in str(state["errors"])
    
    @pytest.mark.asyncio
    async def test_partial_commit_recovery(self, real_distributed_tx_manager):
        """System should handle partial commit scenarios."""
        manager = real_distributed_tx_manager
        tx_id = str(uuid.uuid4())
        
        # Prepare both databases successfully
        neo4j_ops = [
            {"query": "CREATE (n:Entity {id: $id})", "params": {"id": "partial123"}}
        ]
        sqlite_ops = [
            {"query": "INSERT INTO entities (id, name) VALUES (?, ?)", 
             "params": ["partial123", "Partial Test"]}
        ]
        
        await manager.begin_transaction(tx_id)
        await manager.prepare_neo4j(tx_id, neo4j_ops)
        await manager.prepare_sqlite(tx_id, sqlite_ops)
        
        # Simulate Neo4j commit but SQLite failure by closing connection
        state = manager._transactions[tx_id]
        original_conn = state.sqlite_conn
        
        # Close the connection to simulate failure
        await original_conn.close()
        
        # Attempt commit
        result = await manager.commit_all(tx_id)
        
        # Should indicate partial failure
        assert result["status"] == "partial_failure"
        assert result["recovery_needed"] is True
        assert len(result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_transaction_state_persistence(self, real_distributed_tx_manager):
        """Transaction state should be accurately tracked."""
        manager = real_distributed_tx_manager
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
        assert state["neo4j_committed"] is True
        assert state["sqlite_committed"] is True
    
    @pytest.mark.asyncio
    async def test_cleanup_old_transactions(self, real_distributed_tx_manager):
        """Old transactions should be cleaned up."""
        manager = real_distributed_tx_manager
        manager.cleanup_after_seconds = 1  # Clean up after 1 second
        
        # Create a transaction
        tx_id = str(uuid.uuid4())
        await manager.begin_transaction(tx_id)
        
        # Transaction should exist
        state = await manager.get_transaction_state(tx_id)
        assert state is not None
        
        # Wait for cleanup threshold
        await asyncio.sleep(1.5)
        
        # Run cleanup
        cleaned = await manager.cleanup_old_transactions()
        assert cleaned == 1
        
        # Transaction should be gone
        state = await manager.get_transaction_state(tx_id)
        assert state is None