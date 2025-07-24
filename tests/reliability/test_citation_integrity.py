"""
Test citation integrity and provenance tracking.

Ensures that every citation has a verifiable source and prevents
fabrication of citations.
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any
import hashlib
import json

from src.core.provenance_manager import ProvenanceManager
from src.core.citation_validator import CitationValidator


class TestCitationIntegrity:
    """Test suite for citation integrity and provenance."""
    
    @pytest.mark.asyncio
    async def test_citation_source_tracking(self):
        """Test that every citation has a verifiable source."""
        provenance = ProvenanceManager()
        
        # Create a source document
        source_doc = {
            "id": "doc_123",
            "title": "Test Document",
            "content": "This is test content with important facts.",
            "url": "https://example.com/doc123",
            "hash": hashlib.sha256("Test content".encode()).hexdigest()
        }
        
        source_id = await provenance.register_source(source_doc)
        
        # Create citation from source
        # Find actual positions of the text
        content = source_doc["content"]
        text = "important facts"
        start_pos = content.find(text)
        end_pos = start_pos + len(text)
        
        citation = await provenance.create_citation(
            source_id=source_id,
            text=text,
            start_pos=start_pos,
            end_pos=end_pos,
            metadata={"page": 1, "section": "intro"}
        )
        
        # Verify citation has proper provenance
        assert citation["source_id"] == source_id
        assert citation["text"] == "important facts"
        assert citation["provenance_chain"] is not None
        assert len(citation["provenance_chain"]) > 0
        
        # Verify source can be retrieved
        source = await provenance.get_source(citation["source_id"])
        assert source["id"] == "doc_123"
        assert source["hash"] == source_doc["hash"]
    
    @pytest.mark.asyncio
    async def test_modification_audit_trail(self):
        """Test that modifications create an audit trail."""
        provenance = ProvenanceManager()
        
        # Create initial citation
        source_id = await provenance.register_source({
            "id": "doc_456",
            "content": "Original content"
        })
        
        citation = await provenance.create_citation(
            source_id=source_id,
            text="Original",
            start_pos=0,
            end_pos=8
        )
        
        citation_id = citation["id"]
        
        # Modify citation
        modified = await provenance.modify_citation(
            citation_id=citation_id,
            new_text="Modified Original",
            reason="Clarification",
            modifier="test_user"
        )
        
        # Check audit trail
        audit_trail = await provenance.get_audit_trail(citation_id)
        assert len(audit_trail) == 2  # Original + modification
        
        # Verify original is preserved
        assert audit_trail[0]["text"] == "Original"
        assert audit_trail[0]["operation"] == "create"
        
        # Verify modification is tracked
        assert audit_trail[1]["text"] == "Modified Original"
        assert audit_trail[1]["operation"] == "modify"
        assert audit_trail[1]["reason"] == "Clarification"
        assert audit_trail[1]["modifier"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_fabrication_detection(self):
        """Test detection of fabricated citations."""
        provenance = ProvenanceManager()
        validator = CitationValidator(provenance)
        
        # Register legitimate source
        source_id = await provenance.register_source({
            "id": "real_doc",
            "content": "This document contains real information about AI."
        })
        
        # Create legitimate citation
        legit_citation = await provenance.create_citation(
            source_id=source_id,
            text="real information about AI",
            start_pos=23,
            end_pos=48
        )
        
        # Validate legitimate citation
        is_valid = await validator.validate_citation(legit_citation["id"])
        assert is_valid is True
        
        # Try to create fabricated citation (text not in source)
        with pytest.raises(ValueError, match="Text not found in source"):
            await provenance.create_citation(
                source_id=source_id,
                text="fabricated information about quantum computing",
                start_pos=0,
                end_pos=45
            )
        
        # Try to use non-existent source
        with pytest.raises(ValueError, match="Source not found"):
            await provenance.create_citation(
                source_id="fake_source_id",
                text="any text",
                start_pos=0,
                end_pos=8
            )
    
    @pytest.mark.asyncio
    async def test_provenance_chain_validation(self):
        """Test validation of complete provenance chains."""
        provenance = ProvenanceManager()
        validator = CitationValidator(provenance)
        
        # Create chain: Source -> Extract -> Summary -> Citation
        source_id = await provenance.register_source({
            "id": "chain_doc",
            "content": "The capital of France is Paris. Paris has many museums."
        })
        
        # Extract operation
        extract = await provenance.create_derived_content(
            source_id=source_id,
            operation="extract",
            input_text="The capital of France is Paris. Paris has many museums.",
            output_text="Capital: Paris. Museums: many.",
            tool="text_extractor_v1"
        )
        
        # Summary operation
        summary = await provenance.create_derived_content(
            source_id=extract["id"],
            operation="summarize",
            input_text=extract["output_text"],
            output_text="Paris is France's capital with museums.",
            tool="summarizer_v1"
        )
        
        # Create citation from summary
        citation = await provenance.create_citation(
            source_id=summary["id"],
            text="Paris is France's capital",
            start_pos=0,
            end_pos=25
        )
        
        # Validate complete chain
        chain_valid = await validator.validate_provenance_chain(citation["id"])
        assert chain_valid is True
        
        # Get complete chain
        chain = await provenance.get_provenance_chain(citation["id"])
        assert len(chain) == 4  # Source -> Extract -> Summary -> Citation
        assert chain[0]["type"] == "source"
        assert chain[1]["operation"] == "extract"
        assert chain[2]["operation"] == "summarize"
        assert chain[3]["type"] == "citation"
    
    @pytest.mark.asyncio
    async def test_hash_verification(self):
        """Test content hash verification."""
        provenance = ProvenanceManager()
        
        content = "This is immutable content that should not change."
        source_id = await provenance.register_source({
            "id": "hash_doc",
            "content": content,
            "hash": hashlib.sha256(content.encode()).hexdigest()
        })
        
        # Verify hash matches
        is_valid = await provenance.verify_source_integrity(source_id)
        assert is_valid is True
        
        # Simulate tampering
        await provenance._tamper_source_content(source_id, "Tampered content")
        
        # Hash should no longer match
        is_valid = await provenance.verify_source_integrity(source_id)
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_citation_statistics(self):
        """Test citation usage statistics."""
        provenance = ProvenanceManager()
        
        # Create source and citations
        source_id = await provenance.register_source({
            "id": "stats_doc",
            "content": "Fact one. Fact two. Fact three."
        })
        
        # Create multiple citations
        citation1 = await provenance.create_citation(
            source_id=source_id,
            text="Fact one",
            start_pos=0,
            end_pos=8
        )
        
        citation2 = await provenance.create_citation(
            source_id=source_id,
            text="Fact two",
            start_pos=10,
            end_pos=18
        )
        
        # Track usage
        await provenance.track_citation_usage(citation1["id"], "report_1")
        await provenance.track_citation_usage(citation1["id"], "report_2")
        await provenance.track_citation_usage(citation2["id"], "report_1")
        
        # Get statistics
        stats = await provenance.get_citation_statistics()
        
        assert stats["total_citations"] == 2
        assert stats["total_sources"] == 1
        assert stats["citations_by_source"][source_id] == 2
        assert stats["usage_count"][citation1["id"]] == 2
        assert stats["usage_count"][citation2["id"]] == 1
    
    @pytest.mark.asyncio
    async def test_bulk_validation(self):
        """Test bulk validation of citations."""
        provenance = ProvenanceManager()
        validator = CitationValidator(provenance)
        
        # Create multiple sources and citations
        sources = []
        citations = []
        
        for i in range(5):
            source_id = await provenance.register_source({
                "id": f"bulk_doc_{i}",
                "content": f"This is document {i} with facts."
            })
            sources.append(source_id)
            
            citation = await provenance.create_citation(
                source_id=source_id,
                text=f"document {i}",
                start_pos=8,
                end_pos=8 + len(f"document {i}")
            )
            citations.append(citation["id"])
        
        # Validate all citations
        validation_results = await validator.validate_bulk(citations)
        
        assert validation_results["total"] == 5
        assert validation_results["valid"] == 5
        assert validation_results["invalid"] == 0
        
        # Corrupt one citation
        await provenance._corrupt_citation(citations[2])
        
        # Re-validate
        validation_results = await validator.validate_bulk(citations)
        assert validation_results["valid"] == 4
        assert validation_results["invalid"] == 1
        assert citations[2] in validation_results["invalid_citations"]