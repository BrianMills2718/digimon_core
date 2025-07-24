"""
Pytest fixtures for reliability tests.

Provides real database instances for integration testing.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import docker
import time
import aiosqlite
from neo4j import AsyncGraphDatabase
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def docker_client():
    """Get Docker client for managing containers."""
    try:
        client = docker.from_env()
        # Test Docker is available
        client.ping()
        return client
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")


@pytest.fixture(scope="session")
async def neo4j_container(docker_client):
    """Start a Neo4j container for testing."""
    container_name = "kgas-test-neo4j"
    
    # Check if container already exists
    try:
        existing = docker_client.containers.get(container_name)
        existing.stop()
        existing.remove()
    except docker.errors.NotFound:
        pass
    
    # Start Neo4j container
    container = docker_client.containers.run(
        "neo4j:5-community",
        name=container_name,
        detach=True,
        ports={"7687/tcp": 7687, "7474/tcp": 7474},
        environment={
            "NEO4J_AUTH": "neo4j/testpassword",
            "NEO4J_ACCEPT_LICENSE_AGREEMENT": "yes"
        },
        remove=True
    )
    
    # Wait for Neo4j to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            driver = AsyncGraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "testpassword")
            )
            async with driver.session() as session:
                await session.run("RETURN 1")
            await driver.close()
            break
        except Exception:
            if i == max_retries - 1:
                container.stop()
                raise
            time.sleep(1)
    
    yield {
        "uri": "bolt://localhost:7687",
        "auth": ("neo4j", "testpassword"),
        "container": container
    }
    
    # Cleanup
    container.stop()


@pytest.fixture
async def neo4j_driver(neo4j_container):
    """Get Neo4j driver connected to test instance."""
    driver = AsyncGraphDatabase.driver(
        neo4j_container["uri"],
        auth=neo4j_container["auth"]
    )
    
    # Clear database before test
    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    
    yield driver
    
    await driver.close()


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
    shutil.rmtree(temp_dir)


@pytest.fixture
async def real_distributed_tx_manager():
    """Create a real distributed transaction manager with real Neo4j and SQLite."""
    from src.core.distributed_transaction_manager import DistributedTransactionManager
    import tempfile
    from pathlib import Path
    
    # Create SQLite database
    temp_dir = tempfile.mkdtemp()
    db_path = str(Path(temp_dir) / "test.db")
    
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
    
    # Create Neo4j driver
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "testpassword")
    )
    
    # Clear Neo4j database
    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    
    manager = DistributedTransactionManager()
    
    # Override the connection methods to use our test instances
    async def get_neo4j_session():
        return driver.session()
    
    async def get_sqlite_connection():
        return await aiosqlite.connect(db_path)
    
    manager._get_neo4j_session = get_neo4j_session
    manager._get_sqlite_connection = get_sqlite_connection
    manager._neo4j_driver = driver
    manager._sqlite_path = db_path
    
    yield manager
    
    # Cleanup
    await driver.close()
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass