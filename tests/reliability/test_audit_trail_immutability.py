"""
Test audit trail immutability in ProvenanceManager.

Verifies cryptographic chaining and tamper detection.
"""

import pytest
import asyncio
from datetime import datetime
import json

from src.core.provenance_manager import ProvenanceManager, AuditEntry, ImmutableAuditTrail


class TestAuditEntry:
    """Test the AuditEntry dataclass."""
    
    def test_audit_entry_hash_calculation(self):
        """Test that audit entry calculates hash correctly."""
        entry = AuditEntry(
            timestamp="2025-01-23T10:00:00",
            operation="create",
            actor="test_user",
            data={"text": "test citation"},
            previous_hash="0" * 64
        )
        
        # Hash should be deterministic
        assert entry.entry_hash is not None
        assert len(entry.entry_hash) == 64  # SHA256 produces 64 hex chars
        
        # Same data should produce same hash
        entry2 = AuditEntry(
            timestamp="2025-01-23T10:00:00",
            operation="create",
            actor="test_user",
            data={"text": "test citation"},
            previous_hash="0" * 64
        )
        assert entry.entry_hash == entry2.entry_hash
        
        # Different data should produce different hash
        entry3 = AuditEntry(
            timestamp="2025-01-23T10:00:00",
            operation="create",
            actor="different_user",
            data={"text": "test citation"},
            previous_hash="0" * 64
        )
        assert entry.entry_hash != entry3.entry_hash
    
    def test_audit_entry_immutability(self):
        """Test that audit entries are immutable."""
        entry = AuditEntry(
            timestamp="2025-01-23T10:00:00",
            operation="create",
            actor="test_user",
            data={"text": "test citation"},
            previous_hash="0" * 64
        )
        
        # Should not be able to modify fields
        with pytest.raises(AttributeError):
            entry.timestamp = "modified"
        
        with pytest.raises(AttributeError):
            entry.operation = "modified"
        
        with pytest.raises(AttributeError):
            entry.entry_hash = "modified"


class TestImmutableAuditTrail:
    """Test the ImmutableAuditTrail class."""
    
    def test_append_creates_chain(self):
        """Test that appending creates a hash chain."""
        trail = ImmutableAuditTrail()
        
        # First entry
        hash1 = trail.append("create", "user1", {"text": "first"})
        assert hash1 is not None
        assert len(trail._chain) == 1
        assert trail._chain[0].previous_hash == trail._genesis_hash
        
        # Second entry should chain to first
        hash2 = trail.append("modify", "user2", {"text": "second"})
        assert hash2 != hash1
        assert len(trail._chain) == 2
        assert trail._chain[1].previous_hash == hash1
        
        # Third entry should chain to second
        hash3 = trail.append("delete", "user3", {"text": "third"})
        assert hash3 != hash2
        assert len(trail._chain) == 3
        assert trail._chain[2].previous_hash == hash2
    
    def test_verify_integrity_valid_chain(self):
        """Test integrity verification on valid chain."""
        trail = ImmutableAuditTrail()
        
        # Empty chain is valid
        assert trail.verify_integrity() is True
        
        # Add entries
        trail.append("create", "user1", {"text": "first"})
        trail.append("modify", "user2", {"text": "second"})
        trail.append("review", "user3", {"text": "third"})
        
        # Chain should be valid
        assert trail.verify_integrity() is True
    
    def test_verify_integrity_detects_tampering(self):
        """Test that tampering is detected."""
        trail = ImmutableAuditTrail()
        
        # Create valid chain
        trail.append("create", "user1", {"text": "first"})
        trail.append("modify", "user2", {"text": "second"})
        
        # Verify it's valid
        assert trail.verify_integrity() is True
        
        # Tamper with first entry's data (simulate attack)
        # Note: In real implementation, entries are immutable, but we're testing detection
        original_entry = trail._chain[0]
        tampered_entry = AuditEntry(
            timestamp=original_entry.timestamp,
            operation="tampered",  # Changed operation
            actor=original_entry.actor,
            data=original_entry.data,
            previous_hash=original_entry.previous_hash
        )
        trail._chain[0] = tampered_entry
        
        # Should detect tampering
        assert trail.verify_integrity() is False
    
    def test_verify_integrity_detects_broken_chain(self):
        """Test detection of broken chain links."""
        trail = ImmutableAuditTrail()
        
        # Create entries
        trail.append("create", "user1", {"text": "first"})
        trail.append("modify", "user2", {"text": "second"})
        trail.append("review", "user3", {"text": "third"})
        
        # Break the chain by swapping entries
        trail._chain[1], trail._chain[2] = trail._chain[2], trail._chain[1]
        
        # Should detect broken chain
        assert trail.verify_integrity() is False
    
    def test_get_entries_returns_readonly(self):
        """Test that get_entries returns read-only data."""
        trail = ImmutableAuditTrail()
        
        trail.append("create", "user1", {"text": "first"})
        trail.append("modify", "user2", {"text": "second"})
        
        entries = trail.get_entries()
        assert len(entries) == 2
        
        # Verify structure
        assert all(isinstance(e, dict) for e in entries)
        assert all("timestamp" in e for e in entries)
        assert all("operation" in e for e in entries)
        assert all("actor" in e for e in entries)
        assert all("data" in e for e in entries)
        assert all("hash" in e for e in entries)
        
        # Modifying returned data shouldn't affect trail
        entries[0]["operation"] = "tampered"
        
        # Original should be unchanged
        fresh_entries = trail.get_entries()
        assert fresh_entries[0]["operation"] == "create"


class TestProvenanceManagerAuditImmutability:
    """Test ProvenanceManager with immutable audit trails."""
    
    @pytest.mark.asyncio
    async def test_citation_creates_immutable_audit_trail(self):
        """Test that creating citation creates immutable audit trail."""
        manager = ProvenanceManager()
        
        # Register source
        source_id = await manager.register_source({
            "id": "test_source",
            "content": "This is a test document with some content."
        })
        
        # Create citation
        citation = await manager.create_citation(
            source_id=source_id,
            text="test document",
            start_pos=10,
            end_pos=23
        )
        
        # Get audit trail
        audit_trail = await manager.get_audit_trail(citation["id"])
        assert len(audit_trail) == 1
        assert audit_trail[0]["operation"] == "create"
        assert audit_trail[0]["actor"] == "system"
        assert audit_trail[0]["hash"] is not None
    
    @pytest.mark.asyncio
    async def test_citation_modification_extends_chain(self):
        """Test that modifying citation extends the audit chain."""
        manager = ProvenanceManager()
        
        # Register source
        source_id = await manager.register_source({
            "id": "test_source",
            "content": "This is a test document with some content."
        })
        
        # Create citation
        citation = await manager.create_citation(
            source_id=source_id,
            text="test document",
            start_pos=10,
            end_pos=23
        )
        
        # Modify citation
        modified = await manager.modify_citation(
            citation_id=citation["id"],
            new_text="test doc",
            reason="Shortened for clarity",
            modifier="editor1"
        )
        
        # Get audit trail
        audit_trail = await manager.get_audit_trail(citation["id"])
        assert len(audit_trail) == 2
        
        # Verify chain
        assert audit_trail[0]["operation"] == "create"
        assert audit_trail[1]["operation"] == "modify"
        assert audit_trail[1]["actor"] == "editor1"
        
        # Each entry should have unique hash
        assert audit_trail[0]["hash"] != audit_trail[1]["hash"]
    
    @pytest.mark.asyncio
    async def test_audit_integrity_verification(self):
        """Test audit trail integrity verification."""
        manager = ProvenanceManager()
        
        # Register source
        source_id = await manager.register_source({
            "id": "test_source",
            "content": "This is a test document with some content."
        })
        
        # Create citation
        citation = await manager.create_citation(
            source_id=source_id,
            text="test document",
            start_pos=10,
            end_pos=23
        )
        
        # Verify integrity
        is_valid = await manager.verify_audit_integrity(citation["id"])
        assert is_valid is True
        
        # Make modifications
        await manager.modify_citation(
            citation_id=citation["id"],
            new_text="test doc",
            reason="Edit 1",
            modifier="editor1"
        )
        
        await manager.modify_citation(
            citation_id=citation["id"],
            new_text="test document",
            reason="Revert",
            modifier="editor2"
        )
        
        # Should still be valid
        is_valid = await manager.verify_audit_integrity(citation["id"])
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_audit_trail_persistence_through_operations(self):
        """Test that audit trail persists through various operations."""
        manager = ProvenanceManager()
        
        # Register source
        source_id = await manager.register_source({
            "id": "test_source",
            "content": "This is a test document with some content for testing."
        })
        
        # Create multiple citations
        citations = []
        for i in range(3):
            citation = await manager.create_citation(
                source_id=source_id,
                text="test",
                start_pos=10,
                end_pos=14,
                metadata={"index": i}
            )
            citations.append(citation)
        
        # Modify each citation
        for i, citation in enumerate(citations):
            await manager.modify_citation(
                citation_id=citation["id"],
                new_text=f"test{i}",
                reason=f"Adding index {i}",
                modifier=f"user{i}"
            )
        
        # Verify all audit trails are intact
        for citation in citations:
            trail = await manager.get_audit_trail(citation["id"])
            assert len(trail) == 2  # create + modify
            assert await manager.verify_audit_integrity(citation["id"])
    
    @pytest.mark.asyncio
    async def test_concurrent_modifications_maintain_integrity(self):
        """Test that concurrent modifications maintain audit integrity."""
        manager = ProvenanceManager()
        
        # Register source
        source_id = await manager.register_source({
            "id": "test_source",
            "content": "This is a test document with some content."
        })
        
        # Create citation
        citation = await manager.create_citation(
            source_id=source_id,
            text="test document",
            start_pos=10,
            end_pos=23
        )
        
        # Concurrent modifications
        async def modify_citation(index):
            await manager.modify_citation(
                citation_id=citation["id"],
                new_text=f"test doc {index}",
                reason=f"Concurrent edit {index}",
                modifier=f"user{index}"
            )
        
        # Run concurrent modifications
        tasks = [modify_citation(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # Verify integrity
        is_valid = await manager.verify_audit_integrity(citation["id"])
        assert is_valid is True
        
        # Check audit trail
        trail = await manager.get_audit_trail(citation["id"])
        assert len(trail) == 6  # 1 create + 5 modifications
        
        # All hashes should be unique
        hashes = [entry["hash"] for entry in trail]
        assert len(set(hashes)) == len(hashes)


@pytest.mark.asyncio
async def test_audit_trail_immutability_stress_test():
    """Stress test audit trail immutability with many operations."""
    manager = ProvenanceManager()
    
    # Register source
    source_id = await manager.register_source({
        "id": "stress_test_source",
        "content": "A" * 10000  # Large content
    })
    
    # Create many citations
    citation_ids = []
    for i in range(50):
        citation = await manager.create_citation(
            source_id=source_id,
            text="A" * 100,
            start_pos=i * 100,
            end_pos=(i + 1) * 100,
            metadata={"batch": i // 10}
        )
        citation_ids.append(citation["id"])
    
    # Modify each citation multiple times
    for citation_id in citation_ids[:10]:  # Modify first 10
        for j in range(5):
            await manager.modify_citation(
                citation_id=citation_id,
                new_text="B" * 100,
                reason=f"Batch modification {j}",
                modifier=f"batch_user_{j}"
            )
    
    # Verify all audit trails
    for citation_id in citation_ids[:10]:
        is_valid = await manager.verify_audit_integrity(citation_id)
        assert is_valid is True
        
        trail = await manager.get_audit_trail(citation_id)
        assert len(trail) == 6  # 1 create + 5 modifications