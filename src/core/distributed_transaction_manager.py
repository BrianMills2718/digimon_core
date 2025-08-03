"""
Distributed Transaction Manager for Neo4j and SQLite consistency.

Implements a two-phase commit protocol to ensure both databases
maintain consistency during operations.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
import logging
from dataclasses import dataclass, field
from enum import Enum

from neo4j import AsyncSession
import aiosqlite

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """Base class for transaction-related errors."""
    pass


class TransactionStatus(Enum):
    """Transaction status enum."""
    ACTIVE = "active"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    PARTIAL_FAILURE = "partial_failure"


@dataclass 
class TransactionOperation:
    """Represents a single operation within a transaction."""
    operation_type: str  # "query", "create", "update", "delete"
    target_database: str  # "neo4j" or "sqlite"
    query: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    rollback_query: Optional[str] = None
    rollback_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionState:
    """Tracks the state of a distributed transaction."""
    tx_id: str
    status: TransactionStatus = TransactionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    neo4j_prepared: bool = False
    sqlite_prepared: bool = False
    neo4j_committed: bool = False
    sqlite_committed: bool = False
    neo4j_session: Optional[AsyncSession] = None
    neo4j_tx: Optional[Any] = None  # Neo4j transaction object
    sqlite_conn: Optional[aiosqlite.Connection] = None
    neo4j_operations: List[Dict[str, Any]] = field(default_factory=list)
    sqlite_operations: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for external use."""
        return {
            "tx_id": self.tx_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "neo4j_prepared": self.neo4j_prepared,
            "sqlite_prepared": self.sqlite_prepared,
            "neo4j_committed": self.neo4j_committed,
            "sqlite_committed": self.sqlite_committed,
            "errors": self.errors
        }


class DistributedTransactionManager:
    """
    Manages distributed transactions across Neo4j and SQLite.
    
    Implements two-phase commit protocol:
    1. Prepare phase: Both databases prepare the transaction
    2. Commit phase: If both prepared successfully, commit both
    3. Rollback: If any failure, rollback both
    """
    
    def __init__(self, timeout_seconds: int = 30, cleanup_after_seconds: int = 3600):
        """
        Initialize the transaction manager.
        
        Args:
            timeout_seconds: Maximum time for a transaction
            cleanup_after_seconds: Time before cleaning up old transaction states
        """
        self.timeout_seconds = timeout_seconds
        self.cleanup_after_seconds = cleanup_after_seconds
        self._transactions: Dict[str, TransactionState] = {}
        self._lock = asyncio.Lock()
        
        # These should be injected or configured in production
        self._neo4j_driver = None
        self._sqlite_path = None
    
    async def _get_neo4j_session(self) -> AsyncSession:
        """Get a Neo4j session. Override in production."""
        if not self._neo4j_driver:
            raise RuntimeError("Neo4j driver not configured")
        return self._neo4j_driver.session()
    
    async def _get_sqlite_connection(self) -> aiosqlite.Connection:
        """Get a SQLite connection. Override in production."""
        if not self._sqlite_path:
            raise RuntimeError("SQLite path not configured")
        return await aiosqlite.connect(self._sqlite_path)
    
    async def begin_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Begin a new distributed transaction.
        
        Args:
            tx_id: Unique transaction identifier
            
        Returns:
            Transaction state dictionary
        """
        async with self._lock:
            if tx_id in self._transactions:
                raise ValueError(f"Transaction {tx_id} already exists")
            
            state = TransactionState(tx_id=tx_id)
            self._transactions[tx_id] = state
            
            logger.info(f"Started distributed transaction: {tx_id}")
            return state.to_dict()
    
    async def prepare_neo4j(self, tx_id: str, operations: List[Dict[str, Any]]) -> None:
        """
        Prepare Neo4j operations as part of the transaction.
        
        Args:
            tx_id: Transaction identifier
            operations: List of Neo4j operations with 'query' and 'params'
        """
        async with self._lock:
            state = self._transactions.get(tx_id)
            if not state:
                raise ValueError(f"Transaction {tx_id} not found")
            
            if state.status != TransactionStatus.ACTIVE:
                raise ValueError(f"Transaction {tx_id} is not active")
        
        try:
            # Execute with timeout
            await asyncio.wait_for(
                self._execute_neo4j_prepare(state, operations),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            state.status = TransactionStatus.FAILED
            state.errors.append("Neo4j prepare timeout")
            raise
        except Exception as e:
            state.status = TransactionStatus.FAILED
            state.errors.append(f"Neo4j prepare error: {str(e)}")
            raise
    
    async def _execute_neo4j_prepare(self, state: TransactionState, operations: List[Dict[str, Any]]) -> None:
        """Execute Neo4j prepare phase."""
        state.status = TransactionStatus.PREPARING
        
        # Get session if not already exists
        if not state.neo4j_session:
            state.neo4j_session = await self._get_neo4j_session()
        
        # Start transaction and keep it open
        state.neo4j_tx = await state.neo4j_session.begin_transaction()
        
        try:
            # Execute all operations in the transaction
            for op in operations:
                await state.neo4j_tx.run(op["query"], op.get("params", {}))
            
            # Store operations for potential retry
            state.neo4j_operations = operations
            
            # Don't commit yet - this is just prepare phase
            state.neo4j_prepared = True
            logger.info(f"Neo4j prepared for transaction: {state.tx_id}")
            
        except Exception as e:
            # Rollback on any error
            if state.neo4j_tx:
                await state.neo4j_tx.rollback()
                state.neo4j_tx = None
            raise
    
    async def prepare_sqlite(self, tx_id: str, operations: List[Dict[str, Any]]) -> None:
        """
        Prepare SQLite operations as part of the transaction.
        
        Args:
            tx_id: Transaction identifier
            operations: List of SQLite operations with 'query' and 'params'
        """
        async with self._lock:
            state = self._transactions.get(tx_id)
            if not state:
                raise ValueError(f"Transaction {tx_id} not found")
            
            if state.status not in [TransactionStatus.ACTIVE, TransactionStatus.PREPARING]:
                raise ValueError(f"Transaction {tx_id} is not in valid state for prepare")
        
        try:
            await asyncio.wait_for(
                self._execute_sqlite_prepare(state, operations),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            state.status = TransactionStatus.FAILED
            state.errors.append("SQLite prepare timeout")
            raise
        except Exception as e:
            state.status = TransactionStatus.FAILED
            state.errors.append(f"SQLite prepare error: {str(e)}")
            raise
    
    async def _execute_sqlite_prepare(self, state: TransactionState, operations: List[Dict[str, Any]]) -> None:
        """Execute SQLite prepare phase."""
        # Get connection if not already exists
        if not state.sqlite_conn:
            state.sqlite_conn = await self._get_sqlite_connection()
        
        # Execute all operations within transaction
        await state.sqlite_conn.execute("BEGIN TRANSACTION")
        
        try:
            for op in operations:
                await state.sqlite_conn.execute(op["query"], op.get("params", []))
            
            # Store operations for potential retry
            state.sqlite_operations = operations
            
            # Don't commit yet - this is just prepare phase
            state.sqlite_prepared = True
            state.status = TransactionStatus.PREPARED
            logger.info(f"SQLite prepared for transaction: {state.tx_id}")
        except Exception:
            await state.sqlite_conn.execute("ROLLBACK")
            raise
    
    async def commit_all(self, tx_id: str) -> Dict[str, Any]:
        """
        Commit the distributed transaction on both databases.
        
        Args:
            tx_id: Transaction identifier
            
        Returns:
            Result dictionary with commit status
        """
        async with self._lock:
            state = self._transactions.get(tx_id)
            if not state:
                raise ValueError(f"Transaction {tx_id} not found")
            
            if not (state.neo4j_prepared and state.sqlite_prepared):
                raise ValueError(f"Transaction {tx_id} not fully prepared")
        
        state.status = TransactionStatus.COMMITTING
        result = {
            "tx_id": tx_id,
            "status": "unknown",
            "neo4j_committed": False,
            "sqlite_committed": False,
            "errors": []
        }
        
        try:
            # Commit Neo4j transaction
            if state.neo4j_tx:
                await state.neo4j_tx.commit()
                state.neo4j_committed = True
                result["neo4j_committed"] = True
                logger.info(f"Neo4j committed for transaction: {tx_id}")
            
            # Commit SQLite
            if state.sqlite_conn:
                await state.sqlite_conn.commit()
                state.sqlite_committed = True
                result["sqlite_committed"] = True
                logger.info(f"SQLite committed for transaction: {tx_id}")
            
            # If both committed successfully
            if state.neo4j_committed and state.sqlite_committed:
                state.status = TransactionStatus.COMMITTED
                result["status"] = "committed"
            else:
                state.status = TransactionStatus.PARTIAL_FAILURE
                result["status"] = "partial_failure"
                result["recovery_needed"] = True
                
        except Exception as e:
            state.status = TransactionStatus.PARTIAL_FAILURE
            state.errors.append(f"Commit error: {str(e)}")
            result["status"] = "partial_failure"
            result["recovery_needed"] = True
            result["errors"] = [f"SQLite commit failed: {str(e)}"]
            logger.error(f"Partial failure in transaction {tx_id}: {e}")
        
        finally:
            # Clean up connections
            await self._cleanup_transaction_resources(state)
        
        return result
    
    async def rollback_all(self, tx_id: str) -> Dict[str, Any]:
        """
        Rollback the distributed transaction on both databases.
        
        Args:
            tx_id: Transaction identifier
            
        Returns:
            Result dictionary with rollback status
        """
        async with self._lock:
            state = self._transactions.get(tx_id)
            if not state:
                raise ValueError(f"Transaction {tx_id} not found")
        
        state.status = TransactionStatus.ROLLING_BACK
        result = {
            "tx_id": tx_id,
            "status": "unknown",
            "reason": "timeout" if "timeout" in str(state.errors) else "error"
        }
        
        try:
            # Rollback Neo4j transaction
            if state.neo4j_tx:
                await state.neo4j_tx.rollback()
                logger.info(f"Neo4j rolled back for transaction: {tx_id}")
            
            # Rollback SQLite
            if state.sqlite_conn:
                await state.sqlite_conn.rollback()
                logger.info(f"SQLite rolled back for transaction: {tx_id}")
            
            state.status = TransactionStatus.ROLLED_BACK
            result["status"] = "rolled_back"
            
        except Exception as e:
            state.status = TransactionStatus.FAILED
            state.errors.append(f"Rollback error: {str(e)}")
            result["status"] = "rollback_failed"
            logger.error(f"Rollback failed for transaction {tx_id}: {e}")
        
        finally:
            # Clean up connections
            await self._cleanup_transaction_resources(state)
        
        return result
    
    async def get_transaction_state(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a transaction.
        
        Args:
            tx_id: Transaction identifier
            
        Returns:
            Transaction state dictionary or None if not found
        """
        async with self._lock:
            state = self._transactions.get(tx_id)
            return state.to_dict() if state else None
    
    async def cleanup_old_transactions(self) -> int:
        """
        Clean up old transaction states.
        
        Returns:
            Number of transactions cleaned up
        """
        async with self._lock:
            cutoff_time = datetime.now() - timedelta(seconds=self.cleanup_after_seconds)
            old_tx_ids = [
                tx_id for tx_id, state in self._transactions.items()
                if state.created_at < cutoff_time
            ]
            
            for tx_id in old_tx_ids:
                state = self._transactions[tx_id]
                await self._cleanup_transaction_resources(state)
                del self._transactions[tx_id]
            
            logger.info(f"Cleaned up {len(old_tx_ids)} old transactions")
            return len(old_tx_ids)
    
    async def _cleanup_transaction_resources(self, state: TransactionState) -> None:
        """Clean up resources associated with a transaction."""
        try:
            # Close Neo4j transaction if still open
            if state.neo4j_tx:
                try:
                    # Rollback if not already committed
                    if state.status not in [TransactionStatus.COMMITTED, TransactionStatus.ROLLED_BACK]:
                        await state.neo4j_tx.rollback()
                except Exception:
                    pass  # Transaction might already be closed
                state.neo4j_tx = None
        except Exception as e:
            logger.error(f"Error closing Neo4j transaction: {e}")
        
        try:
            if state.neo4j_session:
                await state.neo4j_session.close()
                state.neo4j_session = None
        except Exception as e:
            logger.error(f"Error closing Neo4j session: {e}")
        
        try:
            if state.sqlite_conn:
                await state.sqlite_conn.close()
                state.sqlite_conn = None
        except Exception as e:
            logger.error(f"Error closing SQLite connection: {e}")