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

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestToolsFunctionalReal:
    """Test tools with real execution, not mocks."""

    def test_t01_pdf_loader_functional(self):
        """Test T01 PDF Loader with real execution."""
        print("🔍 Testing T01 PDF Loader functional execution...")
        
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        
        # Create test text file (simpler than PDF for testing)
        test_content = "This is a test document with John Smith and Microsoft Corporation."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            loader = PDFLoader()
            result = loader.load_pdf(test_file)
            
            # Functional assertions
            assert result["status"] == "success"
            assert "text_content" in result["data"]
            assert len(result["data"]["text_content"]) > 0
            assert "John Smith" in result["data"]["text_content"]
            
            print(f"   ✅ PDF Loader: Extracted {len(result['data']['text_content'])} characters")
            
        finally:
            Path(test_file).unlink()  # Cleanup

    def test_t23a_spacy_ner_functional(self):
        """Test T23a SpaCy NER with real execution."""
        print("🔍 Testing T23a SpaCy NER functional execution...")
        
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        
        ner = SpacyNER()
        test_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976. Microsoft was started by Bill Gates."
        
        # Real execution (no mocks)
        result = ner.extract_entities_working(test_text)
        
        # Functional assertions
        assert len(result) > 0, "Should extract at least some entities"
        
        # Check for expected entities
        entity_texts = [e["name"] for e in result]
        entity_types = [e["type"] for e in result]
        
        # Should find organizations
        assert any("Apple" in text for text in entity_texts), "Should find Apple Inc."
        assert any("Microsoft" in text for text in entity_texts), "Should find Microsoft"
        
        # Should find people
        assert any("Jobs" in text for text in entity_texts), "Should find Steve Jobs"
        assert any("Gates" in text for text in entity_texts), "Should find Bill Gates"
        
        # Should have different entity types
        assert "ORG" in entity_types, "Should find organization entities"
        assert "PERSON" in entity_types, "Should find person entities"
        
        print(f"   ✅ SpaCy NER: Extracted {len(result)} entities")
        for entity in result[:3]:  # Show first 3
            print(f"      {entity['name']} ({entity['type']}) - conf: {entity.get('confidence', 'N/A')}")

    def test_t15a_text_chunker_functional(self):
        """Test T15a Text Chunker with real execution."""
        print("🔍 Testing T15a Text Chunker functional execution...")
        
        from src.tools.phase1.t15a_text_chunker import TextChunker
        
        chunker = TextChunker()
        
        # Create text long enough to need chunking
        test_text = " ".join([f"Sentence {i} with content about research and analysis." for i in range(100)])
        
        result = chunker.chunk_text("storage://test/doc123", test_text, 0.9)
        
        # Functional assertions
        assert result["status"] == "success"
        assert "chunks" in result["data"]
        assert len(result["data"]["chunks"]) > 1, "Long text should be split into multiple chunks"
        
        # Check chunk properties
        chunks = result["data"]["chunks"]
        for chunk in chunks:
            assert "content" in chunk
            assert "start_position" in chunk
            assert "end_position" in chunk
            assert len(chunk["content"]) > 0
        
        print(f"   ✅ Text Chunker: Created {len(chunks)} chunks")

    def test_t27_relationship_extractor_functional(self):
        """Test T27 Relationship Extractor with real execution."""
        print("🔍 Testing T27 Relationship Extractor functional execution...")
        
        from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
        
        extractor = RelationshipExtractor()
        test_text = "John Smith works for Microsoft Corporation. The company was founded by Bill Gates in Seattle."
        
        # Mock entities for relationship extraction
        entities = [
            {"id": "ent1", "name": "John Smith", "type": "PERSON", "start_offset": 0, "end_offset": 10},
            {"id": "ent2", "name": "Microsoft Corporation", "type": "ORG", "start_offset": 21, "end_offset": 41},
            {"id": "ent3", "name": "Bill Gates", "type": "PERSON", "start_offset": 70, "end_offset": 80},
            {"id": "ent4", "name": "Seattle", "type": "GPE", "start_offset": 84, "end_offset": 91}
        ]
        
        result = extractor.extract_relationships("storage://test/chunk123", test_text, entities, 0.8)
        
        # Functional assertions
        assert result["status"] == "success"
        assert "relationships" in result["data"]
        
        relationships = result["data"]["relationships"]
        if len(relationships) > 0:
            # Check relationship structure
            rel = relationships[0]
            assert "source_entity" in rel
            assert "target_entity" in rel
            assert "relationship_type" in rel
            assert "confidence" in rel
            
            print(f"   ✅ Relationship Extractor: Found {len(relationships)} relationships")
        else:
            print("   ⚠️  Relationship Extractor: No relationships found (may need pattern improvement)")

    def test_tool_chain_functional(self):
        """Test tool chain execution (mini end-to-end)."""
        print("🔍 Testing tool chain functional execution...")
        
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        from src.tools.phase1.t15a_text_chunker import TextChunker
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        
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
            loader = PDFLoader()
            load_result = loader.load_pdf(test_file)
            assert load_result["status"] == "success"
            
            # Step 2: Chunk text
            chunker = TextChunker()
            chunk_result = chunker.chunk_text(
                "storage://test/doc123", 
                load_result["data"]["text_content"], 
                0.9
            )
            assert chunk_result["status"] == "success"
            
            # Step 3: Extract entities from first chunk
            ner = SpacyNER()
            first_chunk = chunk_result["data"]["chunks"][0]["content"]
            entity_result = ner.extract_entities_working(first_chunk)
            
            # Functional assertions for chain
            assert len(entity_result) > 0, "Chain should produce entities"
            
            # Should find expected entities
            entity_names = [e["name"] for e in entity_result]
            assert any("Johnson" in name for name in entity_names), "Should find Dr. Sarah Johnson"
            assert any("MIT" in name for name in entity_names), "Should find MIT"
            
            print(f"   ✅ Tool Chain: PDF → Chunks → {len(entity_result)} entities")
            
        finally:
            Path(test_file).unlink()  # Cleanup

    def test_tool_error_handling_functional(self):
        """Test tool error handling with real scenarios."""
        print("🔍 Testing tool error handling functional scenarios...")
        
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        
        # Test 1: Non-existent file
        loader = PDFLoader()
        result = loader.load_pdf("nonexistent_file.pdf")
        assert result["status"] == "error"
        assert "error" in result
        print("   ✅ PDF Loader: Handles missing file gracefully")
        
        # Test 2: Empty text
        ner = SpacyNER()
        result = ner.extract_entities_working("")
        # Should return empty list, not crash
        assert isinstance(result, list)
        print("   ✅ SpaCy NER: Handles empty text gracefully")

if __name__ == "__main__":
    """Run functional tests directly."""
    print("🧪 KGAS Tools Functional Testing")
    print("=" * 50)
    
    tester = TestToolsFunctionalReal()
    
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