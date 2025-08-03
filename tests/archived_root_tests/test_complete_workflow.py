#!/usr/bin/env python3
"""
Test the complete end-to-end workflow
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import get_service_manager
from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.base_tool import ToolRequest

def test_complete_workflow():
    """Test the complete PDF → Chunking → Entity extraction workflow"""
    
    print("=== Testing Complete Workflow ===")
    
    # Create substantial test document
    test_file = "/tmp/workflow_test.txt"
    test_content = """John Smith is the CEO of TechCorp Corporation, a leading technology company based in San Francisco, California. 

The company was founded in 2010 and has grown rapidly under John's leadership. TechCorp specializes in artificial intelligence and machine learning solutions for enterprise clients.

Mary Johnson, the CTO of TechCorp, leads the engineering team responsible for developing innovative AI products. She previously worked at Google and Microsoft before joining TechCorp in 2015.

The company's headquarters are located in downtown San Francisco, with additional offices in New York City and Austin, Texas. TechCorp employs over 500 people worldwide.

In 2023, TechCorp launched their flagship product, AIAssist, which has been adopted by major corporations including Apple, Amazon, and Tesla. The product uses advanced natural language processing to help companies automate customer service operations.

Recently, John Smith announced that TechCorp is planning to expand into the European market, with a new office opening in London, England by the end of 2024. The expansion is expected to create 100 new jobs."""
    
    print(f"Creating test document with {len(test_content)} characters")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Initialize services
    print("\nInitializing service manager...")
    service_manager = get_service_manager()
    
    # Step 1: Load document
    print("\n=== Step 1: Loading Document ===")
    pdf_loader = T01PDFLoaderUnified(service_manager)
    
    load_request = ToolRequest(
        tool_id="T01",
        operation="load_document",
        input_data={
            "file_path": test_file,
            "workflow_id": "workflow_test"
        },
        parameters={}
    )
    
    load_result = pdf_loader.execute(load_request)
    print(f"Load status: {load_result.status}")
    
    if load_result.status != "success":
        print(f"Load failed: {load_result.error_message}")
        return
    
    document = load_result.data['document']
    print(f"Document loaded: {document['text_length']} characters, confidence: {document['confidence']}")
    
    # Step 2: Chunk text
    print("\n=== Step 2: Chunking Text ===")
    text_chunker = T15ATextChunkerUnified(service_manager)
    
    chunk_request = ToolRequest(
        tool_id="T15A",
        operation="chunk_text",
        input_data={
            "text": document['text'],
            "document_ref": document['document_ref']
        },
        parameters={}
    )
    
    chunk_result = text_chunker.execute(chunk_request)
    print(f"Chunk status: {chunk_result.status}")
    
    if chunk_result.status != "success":
        print(f"Chunking failed: {chunk_result.error_message}")
        return
    
    chunks = chunk_result.data['chunks']
    print(f"Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk['text'])} chars, confidence: {chunk['confidence']:.3f}")
    
    # Step 3: Extract entities from first chunk
    print("\n=== Step 3: Extracting Entities ===")
    entity_extractor = T23ASpacyNERUnified(service_manager)
    
    # Test with the first chunk
    first_chunk = chunks[0]
    entity_request = ToolRequest(
        tool_id="T23A",
        operation="extract_entities",
        input_data={
            "text": first_chunk['text'],
            "chunk_ref": first_chunk['chunk_ref']
        },
        parameters={}
    )
    
    entity_result = entity_extractor.execute(entity_request)
    print(f"Entity extraction status: {entity_result.status}")
    
    if entity_result.status != "success":
        print(f"Entity extraction failed: {entity_result.error_message}")
        return
    
    entities = entity_result.data['entities']
    print(f"Extracted {len(entities)} entities from first chunk:")
    for entity in entities:
        print(f"  - {entity['surface_form']} ({entity['entity_type']}) confidence: {entity['confidence']:.3f}")
    
    # Summary
    print(f"\n=== Workflow Summary ===")
    print(f"✓ Document loaded: {document['text_length']} characters")
    print(f"✓ Text chunked: {len(chunks)} chunks created")
    print(f"✓ Entities extracted: {len(entities)} entities from first chunk")
    print(f"✓ End-to-end workflow completed successfully!")
    
    # Cleanup
    print(f"\nCleaning up test file: {test_file}")
    os.remove(test_file)
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_complete_workflow()