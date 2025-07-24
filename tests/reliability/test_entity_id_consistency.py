"""
Test entity ID mapping consistency across Neo4j and SQLite.

Ensures that entity IDs remain consistent and properly mapped
between the two databases.
"""

import pytest
import asyncio
import uuid
from typing import List, Dict, Any
import aiosqlite
from unittest.mock import AsyncMock
import tempfile
import shutil
from pathlib import Path

from src.core.entity_id_manager import EntityIDManager


class TestEntityIDConsistency:
    """Test suite for entity ID consistency."""
    
    async def setup_databases(self):
        """Set up test databases."""
        # SQLite setup
        self.temp_dir = tempfile.mkdtemp()
        self.sqlite_path = str(Path(self.temp_dir) / "test.db")
        
        async with aiosqlite.connect(self.sqlite_path) as db:
            # Create entity mapping table
            await db.execute("""
                CREATE TABLE entity_mappings (
                    internal_id TEXT PRIMARY KEY,
                    neo4j_id TEXT UNIQUE NOT NULL,
                    entity_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(neo4j_id)
                )
            """)
            await db.execute("""
                CREATE INDEX idx_neo4j_id ON entity_mappings(neo4j_id)
            """)
            await db.commit()
        
        # Mock Neo4j
        self.neo4j_session = AsyncMock()
        self.neo4j_tx = AsyncMock()
        self.neo4j_session.begin_transaction = AsyncMock(return_value=self.neo4j_tx)
        
        return self.sqlite_path, self.neo4j_session
    
    async def teardown_databases(self):
        """Clean up test databases."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_entity_id_generation_uniqueness(self):
        """Test that generated entity IDs are unique."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            # Generate multiple IDs
            ids = []
            for _ in range(100):
                entity_id = await manager.generate_entity_id("Person")
                ids.append(entity_id)
            
            # All IDs should be unique
            assert len(ids) == len(set(ids))
            
            # IDs should follow expected format
            for entity_id in ids:
                assert entity_id.startswith("PERSON_")
                assert len(entity_id) > 10  # Has UUID suffix
                
        finally:
            await self.teardown_databases()
    
    @pytest.mark.asyncio
    async def test_entity_id_mapping_persistence(self):
        """Test that ID mappings are persisted correctly."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            # Create entity with mapping
            internal_id = await manager.generate_entity_id("Document")
            neo4j_id = f"neo4j_{uuid.uuid4()}"
            
            await manager.create_id_mapping(internal_id, neo4j_id, "Document")
            
            # Verify mapping exists
            retrieved_neo4j_id = await manager.get_neo4j_id(internal_id)
            assert retrieved_neo4j_id == neo4j_id
            
            retrieved_internal_id = await manager.get_internal_id(neo4j_id)
            assert retrieved_internal_id == internal_id
            
        finally:
            await self.teardown_databases()
    
    @pytest.mark.asyncio
    async def test_concurrent_id_creation(self):
        """Test ID creation under concurrent access."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            async def create_entity(entity_type: str, index: int):
                entity_id = await manager.generate_entity_id(entity_type)
                neo4j_id = f"neo4j_{entity_type}_{index}"
                await manager.create_id_mapping(entity_id, neo4j_id, entity_type)
                return entity_id, neo4j_id
            
            # Create multiple entities concurrently
            tasks = []
            for i in range(20):
                entity_type = "Person" if i % 2 == 0 else "Document"
                tasks.append(create_entity(entity_type, i))
            
            results = await asyncio.gather(*tasks)
            
            # Verify all IDs are unique
            internal_ids = [r[0] for r in results]
            neo4j_ids = [r[1] for r in results]
            
            assert len(internal_ids) == len(set(internal_ids))
            assert len(neo4j_ids) == len(set(neo4j_ids))
            
            # Verify all mappings are correct
            for internal_id, neo4j_id in results:
                assert await manager.get_neo4j_id(internal_id) == neo4j_id
                assert await manager.get_internal_id(neo4j_id) == internal_id
                
        finally:
            await self.teardown_databases()
    
    @pytest.mark.asyncio
    async def test_id_collision_handling(self):
        """Test handling of ID collisions."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            # Create first mapping
            internal_id = await manager.generate_entity_id("Person")
            neo4j_id = "neo4j_123"
            await manager.create_id_mapping(internal_id, neo4j_id, "Person")
            
            # Try to create duplicate Neo4j ID mapping
            internal_id2 = await manager.generate_entity_id("Person")
            with pytest.raises(Exception, match="already exists"):
                await manager.create_id_mapping(internal_id2, neo4j_id, "Person")
            
            # Original mapping should still be intact
            assert await manager.get_internal_id(neo4j_id) == internal_id
            
        finally:
            await self.teardown_databases()
    
    @pytest.mark.asyncio
    async def test_cross_database_consistency(self):
        """Test consistency between Neo4j and SQLite operations."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            # Simulate creating entity in both databases
            internal_id = await manager.generate_entity_id("Organization")
            
            # Mock Neo4j node creation
            neo4j_result = AsyncMock()
            neo4j_result.single = AsyncMock(return_value={"id": "neo4j_org_123"})
            self.neo4j_tx.run = AsyncMock(return_value=neo4j_result)
            
            # Create entity with transaction
            async with manager.create_entity_transaction() as tx:
                neo4j_id = await tx.create_neo4j_node("Organization", {"name": "Test Org"})
                await tx.create_sqlite_record(internal_id, {"name": "Test Org"})
                await tx.create_id_mapping(internal_id, neo4j_id)
                await tx.commit()
            
            # Verify consistency
            assert await manager.get_neo4j_id(internal_id) == "neo4j_org_123"
            assert await manager.validate_id_consistency(internal_id, "neo4j_org_123")
            
        finally:
            await self.teardown_databases()
    
    @pytest.mark.asyncio
    async def test_orphaned_id_detection(self):
        """Test detection of orphaned IDs (exists in one DB but not the other)."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            # Create mapping without corresponding Neo4j node
            internal_id = await manager.generate_entity_id("Person")
            neo4j_id = "neo4j_orphan_123"
            await manager.create_id_mapping(internal_id, neo4j_id, "Person")
            
            # Mock Neo4j query to return no results
            self.neo4j_tx.run = AsyncMock(return_value=AsyncMock(single=AsyncMock(return_value=None)))
            
            # Check for orphaned IDs
            orphaned_ids = await manager.find_orphaned_ids()
            assert len(orphaned_ids) == 1
            assert orphaned_ids[0]["internal_id"] == internal_id
            assert orphaned_ids[0]["neo4j_id"] == neo4j_id
            assert orphaned_ids[0]["status"] == "missing_in_neo4j"
            
        finally:
            await self.teardown_databases()
    
    @pytest.mark.asyncio
    async def test_bulk_id_validation(self):
        """Test bulk validation of ID mappings."""
        sqlite_path, neo4j_session = await self.setup_databases()
        
        try:
            manager = EntityIDManager(sqlite_path, neo4j_session)
            
            # Create multiple mappings
            mappings = []
            for i in range(10):
                internal_id = await manager.generate_entity_id("Document")
                neo4j_id = f"neo4j_doc_{i}"
                await manager.create_id_mapping(internal_id, neo4j_id, "Document")
                mappings.append((internal_id, neo4j_id))
            
            # Validate all mappings
            validation_results = await manager.validate_all_mappings()
            
            assert validation_results["total"] == 10
            assert validation_results["valid"] == 10
            assert validation_results["invalid"] == 0
            
            # Corrupt one mapping
            async with aiosqlite.connect(sqlite_path) as db:
                await db.execute(
                    "UPDATE entity_mappings SET neo4j_id = ? WHERE internal_id = ?",
                    ["corrupted_id", mappings[0][0]]
                )
                await db.commit()
            
            # Re-validate
            validation_results = await manager.validate_all_mappings()
            assert validation_results["invalid"] == 1
            
        finally:
            await self.teardown_databases()