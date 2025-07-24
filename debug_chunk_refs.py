#!/usr/bin/env python3
"""
Debug the chunk_ref association between T15A chunks and T23A entities
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

async def debug_chunk_ref_association():
    print('🔬 DEBUGGING CHUNK_REF ASSOCIATION ISSUE')
    print('   Goal: Find why entities are not associated with correct chunk_ref')
    print('=' * 70)
    
    try:
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        text_chunker = T15ATextChunkerUnified(service_manager)
        entity_extractor = T23ASpacyNERUnified(service_manager)
        
        print('✅ Tools initialized')
        
        test_text = 'Dr. Sarah Chen works at MIT Computer Science Department. She collaborates with Prof. Michael Rodriguez from Stanford University.'
        
        print(f'📝 Test text: {test_text}')
        
        # Step 1: Create chunks and inspect their structure
        print('\n🔧 Step 1: Creating chunks...')
        chunk_request = ToolRequest(
            tool_id='T15A',
            operation='chunk_text',
            input_data={
                'document_ref': 'storage://debug/test.txt',
                'text': test_text,
                'confidence': 0.9
            },
            parameters={}
        )
        
        chunk_result = await asyncio.to_thread(text_chunker.execute, chunk_request)
        if chunk_result.status != 'success':
            print(f'❌ Chunking failed: {chunk_result.error_message}')
            return
            
        chunks = chunk_result.data.get('chunks', [])
        print(f'   ✅ Created {len(chunks)} chunks')
        
        # Inspect chunk structure
        for i, chunk in enumerate(chunks):
            print(f'   Chunk {i+1}:')
            print(f'     chunk_ref: "{chunk.get("chunk_ref", "MISSING")}"')
            print(f'     text: "{chunk.get("text", "MISSING")[:50]}..."')
            print(f'     keys: {list(chunk.keys())}')
        
        # Step 2: Extract entities and inspect their chunk_ref association
        print('\n🔧 Step 2: Extracting entities...')
        
        for i, chunk in enumerate(chunks):
            print(f'\n   Processing chunk {i+1}:')
            print(f'     Input chunk_ref: "{chunk.get("chunk_ref", "MISSING")}"')
            
            entity_request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'chunk_ref': chunk['chunk_ref'],
                    'text': chunk['text'],
                    'chunk_confidence': 0.9
                },
                parameters={'confidence_threshold': 0.1}
            )
            
            entity_result = await asyncio.to_thread(entity_extractor.execute, entity_request)
            if entity_result.status == 'success':
                entities = entity_result.data.get('entities', [])
                print(f'     ✅ Extracted {len(entities)} entities')
                
                for j, entity in enumerate(entities):
                    entity_chunk_ref = entity.get('chunk_ref', 'MISSING')
                    surface_form = entity.get('surface_form', 'MISSING')
                    print(f'       Entity {j+1}: "{surface_form}"')
                    print(f'         chunk_ref: "{entity_chunk_ref}"')
                    print(f'         matches input: {entity_chunk_ref == chunk["chunk_ref"]}')
                    
                    # Check if there are issues with the chunk_ref
                    if entity_chunk_ref != chunk['chunk_ref']:
                        print(f'         🚨 CHUNK_REF MISMATCH!')
                        print(f'         Expected: "{chunk["chunk_ref"]}"')
                        print(f'         Got:      "{entity_chunk_ref}"')
            else:
                print(f'     ❌ Entity extraction failed: {entity_result.error_message}')
        
        # Step 3: Test the chunk_ref filtering logic used in relationship extraction
        print('\n🔧 Step 3: Testing chunk_ref filtering logic...')
        
        # Simulate the all_entities collection
        all_entities = []
        for chunk in chunks:
            entity_request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'chunk_ref': chunk['chunk_ref'],
                    'text': chunk['text'],
                    'chunk_confidence': 0.9
                },
                parameters={'confidence_threshold': 0.1}
            )
            
            entity_result = await asyncio.to_thread(entity_extractor.execute, entity_request)
            if entity_result.status == 'success':
                entities = entity_result.data.get('entities', [])
                all_entities.extend(entities)
        
        print(f'   Total entities collected: {len(all_entities)}')
        
        # Test the filtering logic used in the pipeline
        for i, chunk in enumerate(chunks):
            print(f'\\n   Chunk {i+1} filtering test:')
            print(f'     chunk_ref: "{chunk["chunk_ref"]}"')
            
            # This is the exact logic from the pipeline
            chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
            print(f'     Entities matching this chunk_ref: {len(chunk_entities)}')
            
            if len(chunk_entities) == 0:
                print(f'     🚨 NO ENTITIES MATCH THIS CHUNK_REF!')
                print(f'     Available chunk_refs in entities:')
                unique_refs = set(e.get('chunk_ref', 'MISSING') for e in all_entities)
                for ref in unique_refs:
                    count = sum(1 for e in all_entities if e.get('chunk_ref') == ref)
                    print(f'       "{ref}": {count} entities')
            else:
                print(f'     ✅ {len(chunk_entities)} entities found for this chunk')
                
        print(f'\n🎯 CHUNK_REF ASSOCIATION ANALYSIS COMPLETE')
        
    except Exception as e:
        print(f'💥 CHUNK_REF DEBUG FAILED: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chunk_ref_association())