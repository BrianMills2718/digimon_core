#!/usr/bin/env python3

"""
Integration test for phase switching with theory schema validation.
Tests that phases can switch cleanly with theory schema support.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.phase_adapters import PhaseAdapter


def test_phase_switch_with_schema():
    """Test that phases can switch with theory schema validation"""
    from src.phase_adapters import PhaseAdapter
    
    for phase in ["phase1", "phase2"]:
        pa = PhaseAdapter(phase, theory_schema_path="_schemas/theory_meta_schema_v9.json")
        assert pa.health_check()["success"]


def test_phase_schema_validation():
    """Test that theory schemas are properly validated"""
    # Test with valid schema
    pa = PhaseAdapter("phase1", theory_schema_path="_schemas/theory_meta_schema_v9.json")
    result = pa.validate_schema()
    assert result["valid"] is True
    
    # Test with invalid schema path
    pa_invalid = PhaseAdapter("phase1", theory_schema_path="nonexistent_schema.json")
    result = pa_invalid.validate_schema()
    assert result["valid"] is False


def test_phase_compatibility():
    """Test that phases are compatible with each other"""
    phase1 = PhaseAdapter("phase1", theory_schema_path="_schemas/theory_meta_schema_v9.json")
    phase2 = PhaseAdapter("phase2", theory_schema_path="_schemas/theory_meta_schema_v9.json")
    
    # Test that both phases can process the same document
    test_doc = "examples/test_document.txt"
    
    result1 = phase1.process_document(test_doc)
    result2 = phase2.process_document(test_doc)
    
    # Both should succeed
    assert result1["success"] is True
    assert result2["success"] is True
    
    # Results should have compatible structure
    assert "entities" in result1["data"]
    assert "entities" in result2["data"]
    assert "relationships" in result1["data"]
    assert "relationships" in result2["data"]


def test_theory_integration():
    """Test that theory schemas are properly integrated"""
    pa = PhaseAdapter("phase1", theory_schema_path="_schemas/theory_meta_schema_v9.json")
    
    # Test theory schema loading
    schema = pa.load_theory_schema()
    assert schema is not None
    assert "version" in schema
    assert schema["version"] == "9"
    
    # Test theory-aware processing
    test_doc = "examples/test_document.txt"
    result = pa.process_document_with_theory(test_doc)
    
    assert result["success"] is True
    assert "theoretical_insights" in result["data"]


if __name__ == "__main__":
    pytest.main([__file__]) 