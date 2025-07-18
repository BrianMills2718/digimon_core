import pytest
import sys
import os
import hashlib
import json
import re
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.evidence_logger import EvidenceLogger

class TestEvidenceVerification:
    def test_evidence_authenticity(self):
        """Test that evidence entries are authentic and verifiable"""
        evidence_logger = EvidenceLogger()
        
        # Create a test operation
        test_operation = "AUTHENTICITY_TEST"
        test_details = {
            "test_data": "This is a test entry",
            "timestamp": datetime.now().isoformat(),
            "test_number": 42
        }
        
        # Log the operation
        verification_hash = evidence_logger.log_with_verification(test_operation, test_details)
        
        # Verify the hash was created
        assert verification_hash is not None, "No verification hash returned"
        assert len(verification_hash) == 64, "Invalid hash length"
        
        # Verify the evidence was logged
        assert os.path.exists(evidence_logger.evidence_file), "Evidence file not created"
        
        # Read the evidence file and verify the entry exists
        with open(evidence_logger.evidence_file, 'r') as f:
            content = f.read()
            
        assert test_operation in content, "Test operation not found in evidence file"
        assert verification_hash in content, "Verification hash not found in evidence file"
        
    def test_timestamp_consistency(self):
        """Test that timestamps are consistent and realistic"""
        evidence_logger = EvidenceLogger()
        
        # Log multiple operations quickly
        start_time = datetime.now()
        hashes = []
        
        for i in range(3):
            operation = f"TIMESTAMP_TEST_{i}"
            details = {"test_index": i, "timestamp": datetime.now().isoformat()}
            hash_val = evidence_logger.log_with_verification(operation, details)
            hashes.append(hash_val)
        
        end_time = datetime.now()
        
        # Verify all hashes are unique
        assert len(set(hashes)) == len(hashes), "Duplicate verification hashes found"
        
        # Verify timestamps are within reasonable range
        duration = (end_time - start_time).total_seconds()
        assert duration < 10, f"Test took too long: {duration} seconds"
        
    def test_evidence_integrity_verification(self):
        """Test evidence integrity verification system"""
        evidence_logger = EvidenceLogger()
        
        # Log a test operation
        test_operation = "INTEGRITY_TEST"
        test_details = {"integrity_check": True, "test_value": "authentic"}
        
        verification_hash = evidence_logger.log_with_verification(test_operation, test_details)
        
        # Verify evidence integrity
        integrity_result = evidence_logger.verify_evidence_integrity()
        
        assert integrity_result is True, "Evidence integrity verification failed"
        
    def test_evidence_file_format(self):
        """Test that evidence file follows proper format"""
        evidence_logger = EvidenceLogger()
        
        # Log a test operation
        test_operation = "FORMAT_TEST"
        test_details = {"format_check": True}
        
        evidence_logger.log_with_verification(test_operation, test_details)
        
        # Check file format
        with open(evidence_logger.evidence_file, 'r') as f:
            content = f.read()
        
        # Verify required sections exist
        assert "**TIMESTAMP**:" in content, "Timestamp section missing"
        assert "**VERIFICATION_HASH**:" in content, "Verification hash section missing"
        assert "**DETAILS**:" in content, "Details section missing"
        assert "```json" in content, "JSON formatting missing"
        
    def test_cryptographic_verification(self):
        """Test cryptographic verification of evidence entries"""
        evidence_logger = EvidenceLogger()
        
        # Create test data
        test_operation = "CRYPTO_TEST"
        test_details = {"crypto_test": True, "value": 123}
        
        # Log operation
        verification_hash = evidence_logger.log_with_verification(test_operation, test_details)
        
        # Verify hash format
        assert len(verification_hash) == 64, "Hash should be 64 characters (SHA256)"
        assert all(c in '0123456789abcdef' for c in verification_hash), "Hash should be hexadecimal"
        
    def test_evidence_accumulation(self):
        """Test that evidence accumulates properly over time"""
        evidence_logger = EvidenceLogger()
        
        # Get initial evidence file size
        initial_size = 0
        if os.path.exists(evidence_logger.evidence_file):
            with open(evidence_logger.evidence_file, 'r') as f:
                initial_size = len(f.read())
        
        # Log multiple operations
        for i in range(5):
            operation = f"ACCUMULATION_TEST_{i}"
            details = {"iteration": i, "data": f"test_data_{i}"}
            evidence_logger.log_with_verification(operation, details)
        
        # Verify evidence file grew
        with open(evidence_logger.evidence_file, 'r') as f:
            final_size = len(f.read())
        
        assert final_size > initial_size, "Evidence file did not grow after logging operations"
        
        # Verify all operations are recorded
        with open(evidence_logger.evidence_file, 'r') as f:
            content = f.read()
        
        for i in range(5):
            assert f"ACCUMULATION_TEST_{i}" in content, f"Operation {i} not found in evidence"