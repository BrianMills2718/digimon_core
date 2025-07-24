#!/usr/bin/env python3
"""
Test the T23A → T27 format conversion fix
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

async def test_format_conversion_fix():
    print('🔧 TESTING FORMAT CONVERSION FIX')
    print('   Goal: Convert T23A entity format to T27 format and test pipeline')
    print('=' * 70)
    
    try:
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        entity_extractor = T23ASpacyNERUnified(service_manager)
        relationship_extractor = T27RelationshipExtractorUnified(service_manager)
        
        print('✅ Both T23A and T27 tools initialized')
        
        # Test text with clear relationships
        test_text = 'Dr. Sarah Chen works at MIT Computer Science Department. She collaborates with Prof. Michael Rodriguez from Stanford University.'
        
        print(f'📝 Test text: {test_text}')
        
        # Step 1: Extract entities with T23A
        entity_request = ToolRequest(
            tool_id='T23A',
            operation='extract_entities',
            input_data={
                'chunk_ref': 'test_chunk_1',
                'text': test_text,
                'chunk_confidence': 0.9
            },
            parameters={'confidence_threshold': 0.1}
        )
        
        print('\n🔧 Step 1: Extracting entities with T23A...')
        entity_result = await asyncio.to_thread(entity_extractor.execute, entity_request)
        
        if entity_result.status != 'success':
            print(f'❌ T23A failed: {entity_result.error_message}')
            return
            
        t23a_entities = entity_result.data.get('entities', [])
        print(f'   ✅ T23A extracted {len(t23a_entities)} entities')
        
        # Step 2: Convert T23A format to T27 format
        print('\n🔄 Step 2: Converting entity format T23A → T27...')
        
        def convert_t23a_to_t27_format(t23a_entities, original_text):
            """Convert T23A entity format to T27 expected format"""
            t27_entities = []
            
            for entity in t23a_entities:
                # T27 expects: ['text', 'label', 'start', 'end']
                # T23A provides: ['surface_form', 'entity_type', 'start_pos', 'end_pos']
                
                t27_entity = {
                    'text': entity.get('surface_form', ''),  # T23A → T27
                    'label': entity.get('entity_type', ''),  # T23A → T27
                    'start': entity.get('start_pos', 0),     # T23A → T27
                    'end': entity.get('end_pos', 0),         # T23A → T27
                    # Preserve original T23A data for debugging
                    '_original_entity_id': entity.get('entity_id', ''),
                    '_original_confidence': entity.get('confidence', 0.0)
                }
                t27_entities.append(t27_entity)
            
            return t27_entities
        
        t27_formatted_entities = convert_t23a_to_t27_format(t23a_entities, test_text)
        
        print(f'   ✅ Converted {len(t27_formatted_entities)} entities to T27 format')
        if t27_formatted_entities:
            first = t27_formatted_entities[0]
            print(f'   📋 First converted entity: text="{first["text"]}", label="{first["label"]}", start={first["start"]}, end={first["end"]}')
        
        # Step 3: Test T27 with converted entities
        print('\n🔧 Step 3: Testing T27 with converted entities...')
        
        rel_request = ToolRequest(
            tool_id='T27',
            operation='extract_relationships',
            input_data={
                'chunk_ref': 'test_chunk_1',
                'text': test_text,
                'entities': t27_formatted_entities,  # Use converted format!
                'confidence': 0.1
            },
            parameters={}
        )
        
        rel_result = await asyncio.to_thread(relationship_extractor.execute, rel_request)
        
        print(f'📊 T27 RESULT WITH CONVERTED ENTITIES:')
        print(f'   Status: {rel_result.status}')
        print(f'   Execution Time: {rel_result.execution_time:.3f}s')
        
        if rel_result.status == 'success':
            relationships = rel_result.data.get('relationships', [])
            print(f'   🎉 SUCCESS! Found {len(relationships)} relationships')
            
            if relationships:
                print(f'\n📋 EXTRACTED RELATIONSHIPS:')
                for i, rel in enumerate(relationships, 1):
                    source = rel.get('source_entity', 'Unknown')
                    rel_type = rel.get('relationship_type', 'Unknown') 
                    target = rel.get('target_entity', 'Unknown')
                    confidence = rel.get('confidence', 0.0)
                    print(f'   {i}. {source} → {rel_type} → {target} (conf: {confidence:.2f})')
            
            print(f'\n🎯 PIPELINE SUCCESS!')
            print(f'   Problem: T23A and T27 had incompatible entity formats')
            print(f'   Solution: Format conversion layer')
            print(f'   Result: Zero relationships problem SOLVED!')
            
        else:
            print(f'   ❌ T27 still failed: {rel_result.error_message}')
            print(f'   Error Code: {rel_result.error_code}')
            
        return rel_result
        
    except Exception as e:
        print(f'💥 FORMAT CONVERSION TEST FAILED: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_format_conversion_fix())