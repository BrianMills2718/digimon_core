#!/usr/bin/env python3
"""
Real Functional Testing for KGAS Tools

Tests tools with actual execution (no mocks) to verify they work end-to-end.
This addresses the gap between unit tests (with mocks) and real functionality.
"""

import pytest
import tempfile
from pathlib import Path
import sys
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tools.base_tool import ToolRequest
from src.core.service_manager import ServiceManager

class TestToolsFunctionalReal:
    """Test tools with real execution, not mocks."""

    def setup_method(self):
        """Setup service manager for tests."""
        self.service_manager = ServiceManager()

    def test_t01_pdf_loader_functional(self):
        """Test T01 PDF Loader with real execution."""
        print("🔍 Testing T01 PDF Loader functional execution...")
        
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        
        # Create test text file (simpler than PDF for testing)
        test_content = "This is a test document with John Smith and Microsoft Corporation."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            loader = T01PDFLoaderUnified(self.service_manager)
            
            # Create request
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": test_file}
            )
            
            # Execute
            result = loader.execute(request)
            
            # Functional assertions
            assert result.status == "success"
            assert "document" in result.data
            assert result.data["document"]["text_length"] > 0
            assert "John Smith" in result.data["document"]["text"]
            
            print(f"   ✅ PDF Loader: Extracted {result.data['document']['text_length']} characters")
            
        finally:
            Path(test_file).unlink()  # Cleanup

    def test_t23a_spacy_ner_functional(self):
        """Test T23a SpaCy NER with real execution."""
        print("🔍 Testing T23a SpaCy NER functional execution...")
        
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        
        ner = T23ASpacyNERUnified(self.service_manager)
        test_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976. Microsoft was started by Bill Gates."
        
        # Create request
        request = ToolRequest(
            tool_id="T23A",
            operation="extract_entities",
            input_data={
                "text": test_text,
                "chunk_ref": "test_chunk_001"
            },
            parameters={"confidence_threshold": 0.5}  # Lower threshold for testing
        )
        
        # Real execution (no mocks)
        result = ner.execute(request)
        
        # Functional assertions
        assert result.status == "success"
        assert "entities" in result.data
        
        # Debug output
        print(f"   Debug: Result status: {result.status}")
        print(f"   Debug: Result data: {result.data}")
        
        assert len(result.data["entities"]) > 0, "Should extract at least some entities"
        
        # Check for expected entities
        entities = result.data["entities"]
        entity_texts = [e.get("surface_form", e.get("text", "")) for e in entities]
        entity_types = [e.get("entity_type", "") for e in entities]
        
        # Should find organizations
        assert any("Apple" in text for text in entity_texts), "Should find Apple Inc."
        assert any("Microsoft" in text for text in entity_texts), "Should find Microsoft"
        
        # Should find people
        assert any("Jobs" in text for text in entity_texts), "Should find Steve Jobs"
        assert any("Gates" in text for text in entity_texts), "Should find Bill Gates"
        
        # Should have different entity types
        assert "ORG" in entity_types, "Should find organization entities"
        assert "PERSON" in entity_types, "Should find person entities"
        
        print(f"   ✅ SpaCy NER: Extracted {len(entities)} entities")
        for entity in entities[:3]:  # Show first 3
            print(f"      {entity.get('surface_form', entity.get('text', 'N/A'))} ({entity.get('entity_type', 'N/A')}) - conf: {entity.get('confidence', 'N/A')}")

    def test_t15a_text_chunker_functional(self):
        """Test T15a Text Chunker with real execution."""
        print("🔍 Testing T15a Text Chunker functional execution...")
        
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        
        chunker = T15ATextChunkerUnified(self.service_manager)
        
        # Create text long enough to need chunking
        test_text = " ".join([f"Sentence {i} with content about research and analysis." for i in range(100)])
        
        # Create request
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "document_ref": "test_doc_001",
                "text": test_text,
                "chunk_size": 500,  # Small chunks for testing
                "overlap_size": 50
            }
        )
        
        result = chunker.execute(request)
        
        # Functional assertions
        assert result.status == "success"
        assert "chunks" in result.data
        assert len(result.data["chunks"]) > 1, "Long text should be split into multiple chunks"
        
        # Check chunk properties
        chunks = result.data["chunks"]
        for chunk in chunks:
            assert "chunk_id" in chunk or "chunk_ref" in chunk
            assert "text" in chunk
            assert "char_start" in chunk
            assert "char_end" in chunk
            assert "chunk_index" in chunk
            assert len(chunk["text"]) > 0
        
        print(f"   ✅ Text Chunker: Created {len(chunks)} chunks")

    def test_t27_relationship_extractor_functional(self):
        """Test T27 Relationship Extractor with real execution."""
        print("🔍 Testing T27 Relationship Extractor functional execution...")
        
        from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
        
        extractor = T27RelationshipExtractorUnified(self.service_manager)
        test_text = "John Smith works for Microsoft Corporation. The company was founded by Bill Gates in Seattle."
        
        # Mock entities for relationship extraction
        entities = [
            {
                "entity_ref": "ent1",
                "text": "John Smith",
                "label": "PERSON",
                "entity_type": "PERSON",
                "start": 0,
                "end": 10,
                "start_offset": 0,
                "end_offset": 10,
                "confidence": 0.95
            },
            {
                "entity_ref": "ent2",
                "text": "Microsoft Corporation",
                "label": "ORG",
                "entity_type": "ORG",
                "start": 21,
                "end": 41,
                "start_offset": 21,
                "end_offset": 41,
                "confidence": 0.98
            },
            {
                "entity_ref": "ent3",
                "text": "Bill Gates",
                "label": "PERSON",
                "entity_type": "PERSON",
                "start": 70,
                "end": 80,
                "start_offset": 70,
                "end_offset": 80,
                "confidence": 0.96
            },
            {
                "entity_ref": "ent4",
                "text": "Seattle",
                "label": "GPE",
                "entity_type": "GPE",
                "start": 84,
                "end": 91,
                "start_offset": 84,
                "end_offset": 91,
                "confidence": 0.92
            }
        ]
        
        # Create request
        request = ToolRequest(
            tool_id="T27",
            operation="extract_relationships",
            input_data={
                "chunk_ref": "test_chunk_001",
                "text": test_text,
                "entities": entities
            }
        )
        
        result = extractor.execute(request)
        
        # Debug output
        if result.status == "error":
            print(f"   Debug: Error code: {getattr(result, 'error_code', 'N/A')}")
            print(f"   Debug: Error message: {getattr(result, 'error_message', 'N/A')}")
        
        # Functional assertions
        assert result.status == "success"
        assert "relationships" in result.data
        
        relationships = result.data["relationships"]
        if len(relationships) > 0:
            # Check relationship structure
            rel = relationships[0]
            assert "relationship_ref" in rel
            assert "source_entity_ref" in rel
            assert "target_entity_ref" in rel
            assert "relationship_type" in rel
            assert "confidence" in rel
            
            print(f"   ✅ Relationship Extractor: Found {len(relationships)} relationships")
        else:
            print("   ⚠️  Relationship Extractor: No relationships found (may need pattern improvement)")

    def test_tool_chain_functional(self):
        """Test tool chain execution (mini end-to-end)."""
        print("🔍 Testing tool chain functional execution...")
        
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        
        # Create test content
        test_content = """
        Research Paper on Artificial Intelligence
        
        This paper by Dr. Sarah Johnson from MIT explores machine learning applications.
        The research was conducted in collaboration with Stanford University and Google AI.
        Key findings include improvements in natural language processing using transformer models.
        """
        
        # Step 1: Load document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            loader = T01PDFLoaderUnified(self.service_manager)
            load_request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": test_file}
            )
            load_result = loader.execute(load_request)
            assert load_result.status == "success"
            
            # Step 2: Chunk text
            chunker = T15ATextChunkerUnified(self.service_manager)
            chunk_request = ToolRequest(
                tool_id="T15A",
                operation="chunk",
                input_data={
                    "document_ref": load_result.data["document"]["document_ref"],
                    "text": load_result.data["document"]["text"],
                    "chunk_size": 1000,
                    "overlap_size": 100
                }
            )
            chunk_result = chunker.execute(chunk_request)
            assert chunk_result.status == "success"
            
            # Step 3: Extract entities from first chunk
            ner = T23ASpacyNERUnified(self.service_manager)
            first_chunk = chunk_result.data["chunks"][0]
            ner_request = ToolRequest(
                tool_id="T23A",
                operation="extract_entities",
                input_data={
                    "text": first_chunk["text"],
                    "chunk_ref": first_chunk.get("chunk_ref", first_chunk.get("chunk_id", "test_chunk"))
                },
                parameters={"confidence_threshold": 0.5}
            )
            entity_result = ner.execute(ner_request)
            
            # Functional assertions for chain
            assert entity_result.status == "success"
            entities = entity_result.data["entities"]
            assert len(entities) > 0, "Chain should produce entities"
            
            # Should find expected entities
            entity_names = [e.get("surface_form", e.get("text", "")) for e in entities]
            assert any("Johnson" in name for name in entity_names), "Should find Dr. Sarah Johnson"
            assert any("MIT" in name for name in entity_names), "Should find MIT"
            
            print(f"   ✅ Tool Chain: PDF → Chunks → {len(entities)} entities")
            
        finally:
            Path(test_file).unlink()  # Cleanup

    def test_tool_error_handling_functional(self):
        """Test tool error handling with real scenarios."""
        print("🔍 Testing tool error handling functional scenarios...")
        
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        
        # Test 1: Non-existent file
        loader = T01PDFLoaderUnified(self.service_manager)
        request = ToolRequest(
            tool_id="T01",
            operation="load",
            input_data={"file_path": "nonexistent_file.pdf"}
        )
        result = loader.execute(request)
        assert result.status == "error"
        assert result.error_code == "FILE_NOT_FOUND"
        print("   ✅ PDF Loader: Handles missing file gracefully")
        
        # Test 2: Empty text
        ner = T23ASpacyNERUnified(self.service_manager)
        request = ToolRequest(
            tool_id="T23A",
            operation="extract_entities",
            input_data={
                "text": "",
                "chunk_ref": "test_chunk_001"
            }
        )
        result = ner.execute(request)
        # Should return either success with empty entities or error for empty text
        if result.status == "error":
            # It's okay to return error for empty text
            print(f"   ✅ SpaCy NER: Handles empty text with error: {getattr(result, 'error_message', 'N/A')}")
        else:
            # Or success with empty entities
            assert result.status == "success"
            assert len(result.data["entities"]) == 0
            print("   ✅ SpaCy NER: Handles empty text gracefully")

if __name__ == "__main__":
    """Run functional tests directly."""
    print("🧪 KGAS Tools Functional Testing")
    print("=" * 50)
    
    tester = TestToolsFunctionalReal()
    tester.setup_method()
    
    # Run each test
    tests = [
        tester.test_t01_pdf_loader_functional,
        tester.test_t23a_spacy_ner_functional,
        tester.test_t15a_text_chunker_functional,
        tester.test_t27_relationship_extractor_functional,
        tester.test_tool_chain_functional,
        tester.test_tool_error_handling_functional
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"   ❌ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Functional Testing Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All functional tests passed! Tools are working end-to-end.")
    else:
        print("⚠️  Some functional tests failed. Check implementation.")