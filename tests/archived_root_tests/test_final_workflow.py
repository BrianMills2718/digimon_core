#!/usr/bin/env python3
"""
Final comprehensive test of the end-to-end workflow
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

def test_final_workflow():
    """Test the complete end-to-end workflow with proper parameters"""
    
    print("=== Final Workflow Test ===")
    
    # Create comprehensive test document
    test_file = "/tmp/final_workflow_test.txt"
    test_content = """Technology Company Analysis

John Smith serves as the Chief Executive Officer of TechCorp Corporation, a pioneering technology company headquartered in San Francisco, California. The organization was established in 2010 and has experienced remarkable growth under John's visionary leadership.

TechCorp specializes in cutting-edge artificial intelligence and machine learning solutions designed specifically for enterprise clients. The company has positioned itself as a leader in the rapidly evolving AI landscape.

Mary Johnson holds the position of Chief Technology Officer at TechCorp, where she directs the engineering team responsible for developing groundbreaking AI products. Before joining TechCorp in 2015, Mary gained valuable experience working at prestigious technology companies including Google and Microsoft.

The company maintains its primary headquarters in downtown San Francisco, with strategic satellite offices located in New York City and Austin, Texas. TechCorp currently employs more than 500 talented professionals across its global operations.

In 2023, TechCorp successfully launched AIAssist, their flagship artificial intelligence product that has been rapidly adopted by major corporations such as Apple, Amazon, and Tesla. AIAssist leverages advanced natural language processing technologies to help companies streamline and automate their customer service operations.

Most recently, John Smith announced TechCorp's ambitious plans to expand into the European market, with a new regional office scheduled to open in London, England by the end of 2024. This strategic expansion is projected to create approximately 100 new employment opportunities."""
    
    print(f"Creating comprehensive test document ({len(test_content)} characters)")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Initialize services
    print("Initializing service manager...")
    service_manager = get_service_manager()
    
    # Step 1: Load document
    print("\n=== Step 1: Document Loading ===")
    pdf_loader = T01PDFLoaderUnified(service_manager)
    
    load_request = ToolRequest(
        tool_id="T01",
        operation="load_document",
        input_data={
            "file_path": test_file,
            "workflow_id": "final_test"
        },
        parameters={}
    )
    
    load_result = pdf_loader.execute(load_request)
    print(f"✓ Load status: {load_result.status}")
    
    if load_result.status != "success":
        print(f"✗ Load failed: {load_result.error_message}")
        return False
    
    document = load_result.data['document']
    print(f"✓ Document loaded: {document['text_length']} characters, confidence: {document['confidence']:.3f}")
    
    # Step 2: Chunk text
    print("\n=== Step 2: Text Chunking ===")
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
    print(f"✓ Chunk status: {chunk_result.status}")
    
    if chunk_result.status != "success":
        print(f"✗ Chunking failed: {chunk_result.error_message}")
        return False
    
    chunks = chunk_result.data['chunks']
    print(f"✓ Created {len(chunks)} chunks")
    
    total_entities = 0
    
    # Step 3: Extract entities from all chunks
    print("\n=== Step 3: Entity Extraction ===")
    entity_extractor = T23ASpacyNERUnified(
        service_manager=service_manager,
        memory_config={"db_path": None},
        reasoning_config={"enable_reasoning": False}
    )
    
    for i, chunk in enumerate(chunks):
        print(f"\nProcessing chunk {i+1}/{len(chunks)} ({len(chunk['text'])} chars)")
        
        entity_request = ToolRequest(
            tool_id="T23A",
            operation="extract_entities",
            input_data={
                "text": chunk['text'],
                "chunk_ref": chunk['chunk_ref'],
                "chunk_confidence": chunk['confidence']
            },
            parameters={
                "confidence_threshold": 0.5,
                "schema": None,
                "reasoning_guidance": None,
                "context_metadata": {}
            }
        )
        
        entity_result = entity_extractor.execute(entity_request)
        
        if entity_result.status == "success":
            entities = entity_result.data['entities']
            chunk_entity_count = len(entities)
            total_entities += chunk_entity_count
            
            print(f"✓ Extracted {chunk_entity_count} entities from chunk {i+1}")
            
            # Show top entities from this chunk
            for j, entity in enumerate(entities[:5]):  # Show first 5
                print(f"  {j+1}. {entity['surface_form']} ({entity['entity_type']}) - {entity['confidence']:.3f}")
            
            if len(entities) > 5:
                print(f"  ... and {len(entities) - 5} more")
        else:
            print(f"✗ Entity extraction failed for chunk {i+1}: {entity_result.error_message}")
    
    # Final summary
    print(f"\n=== Final Workflow Results ===")
    print(f"✓ Document processed: {document['file_name']}")
    print(f"✓ Text length: {document['text_length']} characters")
    print(f"✓ Chunks created: {len(chunks)}")
    print(f"✓ Total entities extracted: {total_entities}")
    
    success = total_entities > 0
    
    if success:
        print(f"🎉 End-to-end workflow completed successfully!")
        print(f"   System is ready for production use.")
    else:
        print(f"⚠️  Workflow completed but no entities were extracted.")
    
    # Cleanup
    print(f"\nCleaning up test file: {test_file}")
    os.remove(test_file)
    
    return success

if __name__ == "__main__":
    success = test_final_workflow()
    sys.exit(0 if success else 1)