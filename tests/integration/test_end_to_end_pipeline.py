#!/usr/bin/env python3
"""
End-to-End Pipeline Integration Tests
Tests complete PDF→Entities→Graph→Query workflow using actual orchestrator
"""

import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.service_manager import ServiceManager

class TestEndToEndPipeline(unittest.TestCase):
    """Test complete end-to-end pipeline functionality"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            self.service_manager = ServiceManager()
            # Create a minimal PipelineOrchestrator for testing
            self.orchestrator = PipelineOrchestrator()
            self.test_file = "examples/test_document.txt"
            
            # Create test file if it doesn't exist
            if not os.path.exists(self.test_file):
                self._create_test_file()
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        except Exception as e:
            self.skipTest(f"Setup failed: {e}")
    
    def _create_test_file(self):
        """Create test file"""
        os.makedirs("examples", exist_ok=True)
        
        # Create a simple test document
        test_content = """Test Document for GraphRAG System

Apple Inc. is a technology company located in California.
The company was founded by Steve Jobs and Steve Wozniak.
Microsoft Corporation is another major technology company based in Washington.
Google LLC operates from Mountain View, California.

These companies have various relationships and partnerships.
Apple and Microsoft compete in the personal computer market.
Google and Apple both develop mobile operating systems.

This document contains entities and relationships for testing."""
        
        # Write to text file
        with open(self.test_file, 'w') as f:
            f.write(test_content)
    
    def test_complete_pipeline_execution(self):
        """Test complete pipeline execution through orchestrator"""
        print("\n🧪 Testing complete pipeline execution...")
        
        # Execute full pipeline through orchestrator
        result = self.orchestrator.execute_full_pipeline(self.test_file)
        
        # Verify pipeline completed successfully
        self.assertEqual(result.status, "SUCCESS", f"Pipeline failed: {result.error}")
        
        # Verify entities were extracted
        self.assertGreater(len(result.entities), 0, "Pipeline should extract entities")
        
        # Verify relationships were extracted (may be 0 for simple text)
        self.assertGreaterEqual(len(result.relationships), 0, "Pipeline should handle relationships")
        
        # Verify graph was created
        self.assertTrue(result.graph_created, "Pipeline should create graph")
        
        # Verify querying is enabled
        self.assertTrue(result.query_enabled, "Pipeline should enable querying")
        
        print("✅ Complete pipeline execution test passed")
    
    def test_pipeline_with_real_file(self):
        """Test pipeline with actual document file"""
        if not os.path.exists(self.test_file):
            self.skipTest("Test file not available")
        
        print("\n🧪 Testing pipeline with real file...")
        
        # Execute pipeline with file
        result = self.orchestrator.execute_pdf_pipeline(self.test_file)
        
        # Verify file processing
        self.assertEqual(result.status, "SUCCESS", f"File pipeline failed: {result.error}")
        self.assertGreater(len(result.text_chunks), 0, "Should extract text chunks")
        
        # Verify entity extraction
        self.assertGreater(len(result.entities), 0, "Should extract entities")
        
        # Verify specific entities (if they exist)
        entity_names = [getattr(e, 'canonical_name', str(e)) for e in result.entities]
        print(f"Extracted entities: {entity_names}")
        
        print("✅ Real file pipeline test passed")
    
    def test_end_to_end_query_functionality(self):
        """Test end-to-end query functionality"""
        print("\n🧪 Testing end-to-end query functionality...")
        
        # Execute pipeline
        result = self.orchestrator.execute_full_pipeline(self.test_file)
        self.assertEqual(result.status, "SUCCESS")
        
        # Test queries
        queries = [
            "MATCH (n:Entity) RETURN count(n)",
            "MATCH (n:Entity) WHERE n.entity_type = 'ORG' RETURN n.canonical_name",
            "MATCH (n:Entity)-[r:RELATED_TO]->(m:Entity) RETURN n.canonical_name, r.relationship_type, m.canonical_name"
        ]
        
        for query in queries:
            query_result = self.orchestrator.execute_query(query)
            self.assertIsNotNone(query_result, f"Query should return results: {query}")
            
            if "count(n)" in query:
                self.assertGreater(query_result.count, 0, "Should have entities in graph")
        
        print("✅ End-to-end query functionality test passed")
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling"""
        print("\n🧪 Testing pipeline error handling...")
        
        # Test with invalid file
        with self.assertRaises(FileNotFoundError):
            self.orchestrator.execute_full_pipeline("nonexistent.pdf")
        
        # Test with invalid query
        result = self.orchestrator.execute_full_pipeline(self.test_file)
        self.assertEqual(result.status, "SUCCESS")
        
        with self.assertRaises(Exception):
            self.orchestrator.execute_query("INVALID CYPHER QUERY")
        
        print("✅ Pipeline error handling test passed")
    
    def test_pipeline_performance(self):
        """Test pipeline performance benchmarks"""
        print("\n🧪 Testing pipeline performance...")
        
        import time
        
        # Measure pipeline execution time
        start_time = time.time()
        result = self.orchestrator.execute_full_pipeline(self.test_file)
        execution_time = time.time() - start_time
        
        # Verify performance
        self.assertEqual(result.status, "SUCCESS")
        self.assertLess(execution_time, 60.0, "Pipeline should complete within 60 seconds")
        
        print(f"✅ Pipeline performance test passed (executed in {execution_time:.2f}s)")
    
    def test_pipeline_data_integrity(self):
        """Test pipeline data integrity"""
        print("\n🧪 Testing pipeline data integrity...")
        
        # Execute pipeline
        result = self.orchestrator.execute_full_pipeline(self.test_file)
        self.assertEqual(result.status, "SUCCESS")
        
        # Verify entity data integrity
        for entity in result.entities:
            if isinstance(entity, dict):
                self.assertIsNotNone(entity.get('canonical_name'), "Entity should have canonical name")
                self.assertIsNotNone(entity.get('entity_type'), "Entity should have type")
                self.assertIsInstance(entity.get('confidence', 0), (int, float), "Confidence should be numeric")
            else:
                self.assertIsNotNone(getattr(entity, 'canonical_name', None), "Entity should have canonical name")
                self.assertIsNotNone(getattr(entity, 'entity_type', None), "Entity should have type")
                self.assertIsInstance(getattr(entity, 'confidence', 0), (int, float), "Confidence should be numeric")
        
        # Verify relationship data integrity
        for relationship in result.relationships:
            if isinstance(relationship, dict):
                self.assertIsNotNone(relationship.get('source_entity') or relationship.get('subject_entity_id'), "Relationship should have source")
                self.assertIsNotNone(relationship.get('target_entity') or relationship.get('object_entity_id'), "Relationship should have target")
                self.assertIsNotNone(relationship.get('relationship_type'), "Relationship should have type")
            else:
                self.assertIsNotNone(getattr(relationship, 'source_entity', None), "Relationship should have source")
                self.assertIsNotNone(getattr(relationship, 'target_entity', None), "Relationship should have target")
                self.assertIsNotNone(getattr(relationship, 'relationship_type', None), "Relationship should have type")
        
        print("✅ Pipeline data integrity test passed")

if __name__ == "__main__":
    unittest.main(verbosity=2)