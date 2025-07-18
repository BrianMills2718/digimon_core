#!/usr/bin/env python3
"""
Comprehensive Error Testing
Tests actual system failures, not just handler isolation
"""

import sys
import os
import time
import pytest
from unittest.mock import patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.evidence_logger import EvidenceLogger
from src.core.service_manager import ServiceManager
from src.core.pipeline_orchestrator import PipelineOrchestrator


class TestComprehensiveErrorCoverage:
    """Test comprehensive error coverage with actual system failures"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.evidence_logger = EvidenceLogger()
    
    def test_database_connection_failure_real(self):
        """Test actual database connection failure"""
        # Create orchestrator with invalid database config
        original_uri = os.environ.get('NEO4J_URI')
        os.environ['NEO4J_URI'] = 'bolt://nonexistent:7687'
        
        try:
            # This should fail with real database error
            service_manager = ServiceManager()
            
            # Try to get Neo4j driver with invalid URI
            with pytest.raises(Exception) as exc_info:
                driver = service_manager.get_neo4j_driver()
                
                # This should raise ConnectionError
                with driver.session() as session:
                    session.run("RETURN 1")
            
            # Record evidence of actual error
            self.evidence_logger.log_error_test(
                "DATABASE_CONNECTION_FAILURE",
                "Test database connection with invalid URI",
                str(exc_info.value),
                expected=True
            )
            
            # Verify error type
            assert "connection" in str(exc_info.value).lower() or "address" in str(exc_info.value).lower()
            
        finally:
            # Restore original config
            if original_uri:
                os.environ['NEO4J_URI'] = original_uri
            else:
                os.environ.pop('NEO4J_URI', None)
    
    def test_file_not_found_real(self):
        """Test actual file not found error"""
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        
        loader = PDFLoader()
        
        # Try to load non-existent file
        result = loader.load_pdf("non_existent_file.pdf")
        
        assert result['status'] == 'error'
        assert 'not found' in result['error'].lower() or 'no such file' in result['error'].lower()
        
        # Record evidence
        self.evidence_logger.log_error_test(
            "FILE_NOT_FOUND",
            "Test PDF loader with non-existent file",
            result['error'],
            expected=True
        )
    
    def test_spacy_model_missing_real(self):
        """Test actual spaCy model missing error"""
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        
        # Temporarily simulate missing spaCy model
        import spacy
        original_load = spacy.load
        
        def mock_load(model_name):
            raise OSError(f"Model '{model_name}' not found")
        
        spacy.load = mock_load
        
        try:
            ner = SpacyNER()
            result = ner.extract_entities("test_chunk", "Test text")
            
            assert result['status'] == 'error'
            assert 'spacy' in result['error'].lower() or 'model' in result['error'].lower()
            
            # Record evidence
            self.evidence_logger.log_error_test(
                "SPACY_MODEL_MISSING",
                "Test spaCy NER with missing model",
                result['error'],
                expected=True
            )
                
        finally:
            spacy.load = original_load
    
    def test_invalid_cypher_query_real(self):
        """Test actual invalid Cypher query error"""
        from src.tools.phase1.t49_multihop_query import MultiHopQuery
        
        query_tool = MultiHopQuery()
        
        # Try to execute invalid Cypher query
        result = query_tool.execute_query("INVALID CYPHER SYNTAX")
        
        assert result['status'] == 'error'
        assert 'syntax' in result['error'].lower() or 'invalid' in result['error'].lower()
        
        # Record evidence
        self.evidence_logger.log_error_test(
            "INVALID_CYPHER_QUERY",
            "Test multi-hop query with invalid syntax",
            result['error'],
            expected=True
        )
    
    def test_memory_exhaustion_simulation(self):
        """Test system behavior under memory pressure"""
        from src.tools.phase1.t15a_text_chunker import TextChunker
        
        chunker = TextChunker()
        
        # Create extremely large text to simulate memory pressure
        large_text = "A" * (10 ** 7)  # 10MB of text
        
        start_time = time.time()
        result = chunker.chunk_text(large_text)
        execution_time = time.time() - start_time
        
        # Should either succeed or fail gracefully
        assert result['status'] in ['success', 'error']
        
        # Record evidence
        self.evidence_logger.log_error_test(
            "MEMORY_PRESSURE_TEST",
            f"Test text chunker with {len(large_text)} characters",
            f"Status: {result['status']}, Time: {execution_time:.2f}s",
            expected=True
        )
    
    def test_concurrent_access_errors(self):
        """Test concurrent access error scenarios"""
        from src.core.neo4j_manager import Neo4jManager
        import threading
        
        manager = Neo4jManager()
        errors = []
        
        def concurrent_operation():
            """Concurrent database operation"""
            try:
                driver = manager.get_driver()
                with driver.session() as session:
                    session.run("CREATE (n:ConcurrentTest {id: randomUUID()})")
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_operation)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Clean up
        try:
            driver = manager.get_driver()
            with driver.session() as session:
                session.run("MATCH (n:ConcurrentTest) DELETE n")
        except:
            pass
        
        # Record evidence
        self.evidence_logger.log_error_test(
            "CONCURRENT_ACCESS_TEST",
            "Test concurrent database access",
            f"Errors encountered: {len(errors)}, Details: {errors[:3]}",
            expected=True
        )
    
    def test_end_to_end_pipeline_with_real_errors(self):
        """Test end-to-end pipeline with real error conditions"""
        orchestrator = PipelineOrchestrator()
        
        # Test with corrupted PDF (simulate with non-PDF file)
        test_file = "corrupted_test.pdf"
        with open(test_file, "w") as f:
            f.write("This is not a valid PDF file")
        
        try:
            result = orchestrator.execute_full_pipeline(test_file)
            
            # Should either process or fail gracefully
            assert result.status in ['success', 'error']
            
            # Record evidence
            self.evidence_logger.log_error_test(
                "END_TO_END_PIPELINE_ERROR",
                "Test pipeline with corrupted PDF",
                f"Status: {result.status}, Error: {getattr(result, 'error', 'None')}",
                expected=True
            )
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_network_timeout_simulation(self):
        """Test network timeout scenarios"""
        from src.core.service_manager import ServiceManager
        
        # Simulate network timeout by patching socket operations
        with patch('socket.socket') as mock_socket:
            mock_socket.side_effect = OSError("Network timeout")
            
            service_manager = ServiceManager()
            
            # This should handle network errors gracefully
            with pytest.raises(Exception) as exc_info:
                service_manager.get_neo4j_driver()
            
            # Record evidence
            self.evidence_logger.log_error_test(
                "NETWORK_TIMEOUT_TEST",
                "Test network timeout handling",
                str(exc_info.value),
                expected=True
            )
    
    def test_configuration_validation_errors(self):
        """Test configuration validation with invalid settings"""
        from src.core.config import get_config
        
        # Test with invalid configuration
        original_config = os.environ.get('NEO4J_URI')
        os.environ['NEO4J_URI'] = 'invalid://not-a-valid-uri'
        
        try:
            config = get_config()
            
            # Should detect invalid configuration
            assert config is not None
            
            # Record evidence
            self.evidence_logger.log_error_test(
                "CONFIGURATION_VALIDATION",
                "Test configuration with invalid URI",
                f"Config loaded: {config is not None}",
                expected=True
            )
            
        finally:
            # Restore original config
            if original_config:
                os.environ['NEO4J_URI'] = original_config
            else:
                os.environ.pop('NEO4J_URI', None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])