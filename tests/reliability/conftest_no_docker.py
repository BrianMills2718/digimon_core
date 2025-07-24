"""
Alternative pytest fixtures for reliability tests without Docker.

Provides mock or skip options when Docker/Neo4j is not available.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import aiosqlite
from unittest.mock import AsyncMock, MagicMock
import logging

logger = logging.getLogger(__name__)


def is_neo4j_available():
    """Check if Neo4j is available for testing."""
    try:
        from neo4j import AsyncGraphDatabase
        # Try to connect to a local Neo4j instance
        driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        asyncio.run(driver.close())
        return True
    except Exception:
        return False


@pytest.fixture
async def sqlite_db():
    """Create a temporary SQLite database for testing."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    
    # Initialize database schema
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE entities (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE transactions (
                tx_id TEXT PRIMARY KEY,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                neo4j_prepared BOOLEAN DEFAULT 0,
                sqlite_prepared BOOLEAN DEFAULT 0,
                neo4j_committed BOOLEAN DEFAULT 0,
                sqlite_committed BOOLEAN DEFAULT 0
            )
        """)
        await db.commit()
    
    yield str(db_path)
    
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver for testing without Neo4j."""
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
    
    # Make session context manager work
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock()
    
    return driver, session, tx


@pytest.fixture
async def test_distributed_tx_manager_mock(mock_neo4j_driver, sqlite_db):
    """Create a distributed transaction manager with mocked Neo4j."""
    from src.core.distributed_transaction_manager import DistributedTransactionManager
    
    driver, session, tx = mock_neo4j_driver
    manager = DistributedTransactionManager()
    
    # Ensure SQLite database is initialized
    db_path = await sqlite_db
    
    # Override the connection methods
    async def get_neo4j_session():
        return session
    
    async def get_sqlite_connection():
        return await aiosqlite.connect(db_path)
    
    # Patch session to return our mock transaction
    async def mock_begin_transaction():
        return tx
    
    session.begin_transaction = mock_begin_transaction
    
    manager._get_neo4j_session = get_neo4j_session
    manager._get_sqlite_connection = get_sqlite_connection
    manager._neo4j_driver = driver
    manager._sqlite_path = db_path
    
    return manager, tx