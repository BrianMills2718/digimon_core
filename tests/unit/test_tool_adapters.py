"""Unit tests for tool adapters.

Tests individual tool adapters in isolation with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from src.core.tool_adapters import (
    PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter,
    RelationshipExtractorAdapter, EntityBuilderAdapter, EdgeBuilderAdapter,
    PageRankAdapter, MultiHopQueryAdapter
)


class TestPDFLoaderAdapter:
    """Unit tests for PDFLoaderAdapter"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.identity_service = Mock()
        self.provenance_service = Mock()
        self.quality_service = Mock()
        
        self.adapter = PDFLoaderAdapter(
            self.identity_service,
            self.provenance_service,
            self.quality_service
        )
    
    def test_pdf_loader_adapter_init(self):
        """Test PDFLoaderAdapter initialization"""
        assert self.adapter is not None
        assert hasattr(self.adapter, 'execute')
        assert hasattr(self.adapter, '_tool')
    
    def test_pdf_loader_adapter_execute_valid_input(self):
        """Test PDFLoaderAdapter execute with valid input"""
        # Mock the underlying tool
        self.adapter._tool.load_pdf = Mock(return_value={
            "documents": [{"id": "doc1", "content": "test content"}]
        })
        
        input_data = {"document_paths": ["test1.pdf", "test2.pdf"]}
        result = self.adapter.execute(input_data)
        
        assert "documents" in result
        assert "document_paths" in result
        assert self.adapter._tool.load_pdf.call_count == 2
    
    def test_pdf_loader_adapter_execute_invalid_input(self):
        """Test PDFLoaderAdapter execute with invalid input"""
        with pytest.raises(ValueError, match="PDFLoaderAdapter requires input_data with 'document_paths' key"):
            self.adapter.execute({"invalid": "data"})


class TestTextChunkerAdapter:
    """Unit tests for TextChunkerAdapter"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.identity_service = Mock()
        self.provenance_service = Mock()
        self.quality_service = Mock()
        
        self.adapter = TextChunkerAdapter(
            self.identity_service,
            self.provenance_service,
            self.quality_service
        )
    
    def test_text_chunker_adapter_execute_valid_input(self):
        """Test TextChunkerAdapter execute with valid input"""
        # Mock the underlying tool
        self.adapter._tool.chunk_text = Mock(return_value={
            "chunks": [{"id": "chunk1", "content": "chunk content"}]
        })
        
        input_data = {"documents": [{"id": "doc1", "content": "test"}]}
        result = self.adapter.execute(input_data)
        
        assert "chunks" in result
        assert "documents" in result
        assert self.adapter._tool.chunk_text.call_count == 1
    
    def test_text_chunker_adapter_execute_invalid_input(self):
        """Test TextChunkerAdapter execute with invalid input"""
        with pytest.raises(ValueError, match="TextChunkerAdapter requires input_data with 'documents' key"):
            self.adapter.execute({"invalid": "data"})


class TestSpacyNERAdapter:
    """Unit tests for SpacyNERAdapter"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.identity_service = Mock()
        self.provenance_service = Mock()
        self.quality_service = Mock()
        
        self.adapter = SpacyNERAdapter(
            self.identity_service,
            self.provenance_service,
            self.quality_service
        )
    
    def test_spacy_ner_adapter_execute_valid_input(self):
        """Test SpacyNERAdapter execute with valid input"""
        # Mock the underlying tool
        self.adapter._tool.extract_entities = Mock(return_value={
            "entities": [{"id": "ent1", "type": "PERSON", "text": "John"}]
        })
        
        input_data = {"chunks": [{"id": "chunk1", "content": "John works here"}]}
        result = self.adapter.execute(input_data)
        
        assert "entities" in result
        assert "chunks" in result
        assert self.adapter._tool.extract_entities.call_count == 1


class TestRelationshipExtractorAdapter:
    """Unit tests for RelationshipExtractorAdapter"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.identity_service = Mock()
        self.provenance_service = Mock()
        self.quality_service = Mock()
        
        self.adapter = RelationshipExtractorAdapter(
            self.identity_service,
            self.provenance_service,
            self.quality_service
        )
    
    def test_relationship_extractor_execute_valid_input(self):
        """Test RelationshipExtractorAdapter execute with valid input"""
        # Mock the underlying tool
        self.adapter._tool.extract_relationships = Mock(return_value={
            "relationships": [{"source": "ent1", "target": "ent2", "type": "WORKS_FOR"}]
        })
        
        input_data = {"entities": [{"id": "ent1"}, {"id": "ent2"}]}
        result = self.adapter.execute(input_data)
        
        assert "relationships" in result
        assert "entities" in result
        assert self.adapter._tool.extract_relationships.call_count == 1


class TestToolAdapterProtocolCompliance:
    """Test that all adapters implement the Tool protocol correctly"""
    
    def test_all_adapters_have_execute_method(self):
        """Test that all adapter classes have execute method"""
        adapter_classes = [
            PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter,
            RelationshipExtractorAdapter, EntityBuilderAdapter, EdgeBuilderAdapter,
            PageRankAdapter, MultiHopQueryAdapter
        ]
        
        for adapter_class in adapter_classes:
            # Check class has execute method
            assert hasattr(adapter_class, 'execute'), f"{adapter_class.__name__} missing execute method"
            
            # Check execute is callable (method, not property)
            if hasattr(adapter_class, '__dict__') and 'execute' in adapter_class.__dict__:
                assert callable(adapter_class.__dict__['execute']), f"{adapter_class.__name__}.execute not callable"
    
    def test_adapter_classes_are_instantiable(self):
        """Test that adapter classes can be instantiated with proper arguments"""
        identity_service = Mock()
        provenance_service = Mock()
        quality_service = Mock()
        
        # Test basic adapters (no Neo4j)
        basic_adapters = [PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter, RelationshipExtractorAdapter]
        
        for adapter_class in basic_adapters:
            adapter = adapter_class(identity_service, provenance_service, quality_service)
            assert adapter is not None
            assert hasattr(adapter, 'execute')
        
        # Test Neo4j adapters (need additional parameters)
        neo4j_adapters = [EntityBuilderAdapter, EdgeBuilderAdapter, PageRankAdapter, MultiHopQueryAdapter]
        
        for adapter_class in neo4j_adapters:
            adapter = adapter_class(
                identity_service, provenance_service, quality_service,
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j", 
                neo4j_password="password"
            )
            assert adapter is not None
            assert hasattr(adapter, 'execute')