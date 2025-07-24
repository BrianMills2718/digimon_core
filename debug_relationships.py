#!/usr/bin/env python3
"""
Debug why relationships still not extracted in multi-document pipeline
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

async def debug_multidoc_relationships():
    print('🔬 DEBUGGING MULTI-DOCUMENT RELATIONSHIP EXTRACTION')
    print('   Goal: Find why relationships still not extracted in pipeline')
    print('=' * 70)
    
    try:
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        text_chunker = T15ATextChunkerUnified(service_manager)
        entity_extractor = T23ASpacyNERUnified(service_manager)
        relationship_extractor = T27RelationshipExtractorUnified(service_manager)
        
        print('✅ All tools initialized')
        
        # Use the same text as the academic paper generator
        test_paper_content = '''
        This research conducted by Dr. Sarah Chen-Wang, Prof. Michael Rodriguez at TechCorp Industries LLC presents novel approaches to machine learning.
        
        The work builds on previous research from Meta Platforms Inc. where Chen-Wang and colleagues demonstrated applications of natural language processing to computer vision.
        
        Our methodology combines machine learning with reinforcement learning to address limitations in existing approaches.
        Prof. Michael Rodriguez developed the core algorithm while researchers at MIT Computer Science Department contributed the evaluation framework.
        '''
        
        print(f'📝 Test document content (length: {len(test_paper_content)} chars)')
        
        # Step 1: Chunking
        print('\n🔧 Step 1: Text chunking...')
        chunk_request = ToolRequest(
            tool_id='T15A',
            operation='chunk_text',
            input_data={
                'document_ref': 'storage://debug/paper001.txt',
                'text': test_paper_content,
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
        
        # Step 2: Entity extraction
        print('\n🔧 Step 2: Entity extraction...')
        all_entities = []
        
        for i, chunk in enumerate(chunks[:2]):  # Test first 2 chunks
            print(f'   Processing chunk {i+1}: "{chunk["text"][:50]}..."')
            
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
                print(f'     Found {len(entities)} entities')
                
                # Show entity details
                for j, entity in enumerate(entities[:3]):  # Show first 3
                    print(f'       {j+1}. "{entity.get("surface_form", "?")}" ({entity.get("entity_type", "?")})')
            else:
                print(f'     ❌ Entity extraction failed: {entity_result.error_message}')
        
        print(f'   ✅ Total entities extracted: {len(all_entities)}')
        
        if len(all_entities) == 0:
            print('❌ No entities found - cannot test relationships')
            return
        
        # Step 3: Test relationship extraction chunk by chunk
        print('\n🔧 Step 3: Relationship extraction debugging...')
        
        total_relationship_tasks = 0
        total_relationships_found = 0
        
        for i, chunk in enumerate(chunks[:2]):  # Test first 2 chunks
            chunk_entities = [e for e in all_entities if e.get('chunk_ref') == chunk['chunk_ref']]
            print(f'\n   Chunk {i+1} analysis:')
            print(f'     Text: "{chunk["text"][:100]}..."')
            print(f'     Entities in chunk: {len(chunk_entities)}')
            
            if len(chunk_entities) < 2:
                print(f'     ⚠️  Skipping - need at least 2 entities for relationships')
                continue
                
            total_relationship_tasks += 1
            
            # Show entities in this chunk
            print(f'     Entities:')
            for j, entity in enumerate(chunk_entities):
                print(f'       {j+1}. "{entity.get("surface_form", "?")}" ({entity.get("entity_type", "?")})')
            
            # Convert format
            def convert_t23a_to_t27_format(t23a_entities):
                t27_entities = []
                for entity in t23a_entities:
                    t27_entity = {
                        'text': entity.get('surface_form', ''),
                        'label': entity.get('entity_type', ''),
                        'start': entity.get('start_pos', 0),
                        'end': entity.get('end_pos', 0)
                    }
                    t27_entities.append(t27_entity)
                return t27_entities
            
            t27_entities = convert_t23a_to_t27_format(chunk_entities)
            print(f'     Converted to T27 format: {len(t27_entities)} entities')
            
            # Test relationship extraction
            rel_request = ToolRequest(
                tool_id='T27',
                operation='extract_relationships',
                input_data={
                    'chunk_ref': chunk['chunk_ref'],
                    'text': chunk['text'],
                    'entities': t27_entities,
                    'confidence': 0.1
                },
                parameters={}
            )
            
            print(f'     Executing T27...')
            rel_result = await asyncio.to_thread(relationship_extractor.execute, rel_request)
            
            print(f'     T27 Status: {rel_result.status}')
            if rel_result.status == 'success':
                relationships = rel_result.data.get('relationships', [])
                print(f'     Relationships found: {len(relationships)}')
                total_relationships_found += len(relationships)
                
                if relationships:
                    print(f'     Relationships:')
                    for k, rel in enumerate(relationships):
                        source = rel.get('source_entity', 'Unknown')
                        rel_type = rel.get('relationship_type', 'Unknown')
                        target = rel.get('target_entity', 'Unknown')
                        conf = rel.get('confidence', 0.0)
                        print(f'       {k+1}. {source} → {rel_type} → {target} (conf: {conf:.2f})')
            else:
                print(f'     ❌ T27 failed: {rel_result.error_message}')
        
        print(f'\n📊 DEBUGGING SUMMARY:')
        print(f'   Total chunks: {len(chunks)}')
        print(f'   Total entities: {len(all_entities)}')
        print(f'   Chunks with 2+ entities: {total_relationship_tasks}')
        print(f'   Total relationships found: {total_relationships_found}')
        
        if total_relationships_found > 0:
            print(f'\n🎉 RELATIONSHIPS ARE BEING EXTRACTED!')
            print(f'   The issue may be in the pipeline aggregation logic')
        else:
            print(f'\n🚨 NO RELATIONSHIPS EXTRACTED')
            print(f'   Issue is in T27 relationship extraction itself')
            
    except Exception as e:
        print(f'💥 DEBUG TEST FAILED: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_multidoc_relationships())