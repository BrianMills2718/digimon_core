#!/usr/bin/env python3
"""
Test Entity Extraction with Threshold Set to 0
This tests the entity extraction with a threshold of 0 to extract all entities
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.base_tool import ToolRequest

def test_entity_extraction_threshold_zero():
    """Test entity extraction with threshold set to 0"""
    
    print("🔍 TESTING ENTITY EXTRACTION WITH THRESHOLD = 0")
    print("=" * 60)
    
    # Initialize service manager
    service_manager = ServiceManager()
    
    # Initialize entity extractor with custom confidence threshold
    print("\n1. Initializing T23A spaCy NER with custom reasoning config...")
    reasoning_config = {
        "enable_reasoning": True,
        "confidence_threshold": 0.0  # Set to 0 for initial development
    }
    
    ner_tool = T23ASpacyNERUnified(
        service_manager=service_manager,
        reasoning_config=reasoning_config
    )
    
    # Also update the adaptive threshold
    ner_tool.adaptive_confidence_threshold = 0.0
    
    print(f"   Tool ID: {ner_tool.tool_id}")
    print(f"   Adaptive threshold: {ner_tool.adaptive_confidence_threshold}")
    print(f"   Reasoning config: {reasoning_config}")
    
    # Test text with various entity types
    test_text = """
    Apple Inc. was founded by Steve Jobs in Cupertino, California. 
    The company is worth over $3 trillion as of 2024. 
    Microsoft and Google are major competitors.
    The iPhone was released on June 29, 2007.
    Tim Cook became CEO in August 2011.
    They have offices in London, Tokyo, and Sydney.
    The company employs over 150,000 people worldwide.
    Products include MacBook, iPad, and Apple Watch.
    """
    
    print("\n2. Creating extraction request with threshold = 0...")
    request = ToolRequest(
        tool_id=ner_tool.tool_id,
        operation="extract_entities",
        input_data={
            "text": test_text,
            "chunk_ref": "test_chunk_001"
        },
        parameters={
            "confidence_threshold": 0.0,  # Override to 0
            "chunk_confidence": 1.0
        }
    )
    
    print("\n3. Executing entity extraction...")
    result = ner_tool.execute(request)
    
    print(f"\n4. Extraction Result:")
    print(f"   Status: {result.status}")
    if result.status == "success":
        entities = result.data.get("entities", [])
        print(f"   Total entities found: {len(entities)}")
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity.get("entity_type", "UNKNOWN")
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        print("\n5. Entities by Type:")
        for entity_type, type_entities in sorted(entities_by_type.items()):
            print(f"\n   {entity_type} ({len(type_entities)}):")
            for entity in type_entities[:5]:  # Show first 5 of each type
                print(f"     - '{entity['surface_form']}' (confidence: {entity['confidence']:.3f})")
            if len(type_entities) > 5:
                print(f"     ... and {len(type_entities) - 5} more")
        
        # Show lowest confidence entities
        sorted_entities = sorted(entities, key=lambda x: x['confidence'])
        print("\n6. Lowest Confidence Entities (these would normally be filtered):")
        for entity in sorted_entities[:10]:
            print(f"   - '{entity['surface_form']}' ({entity['entity_type']}) - confidence: {entity['confidence']:.3f}")
        
        # Show processing stats
        stats = result.data.get("processing_stats", {})
        print(f"\n7. Processing Statistics:")
        print(f"   Text length: {stats.get('text_length', 0)}")
        print(f"   Entities found by spaCy: {stats.get('entities_found', 0)}")
        print(f"   Entities extracted (threshold=0): {stats.get('entities_extracted', 0)}")
        print(f"   Applied threshold: {stats.get('confidence_threshold', 'N/A')}")
        
        # Test with normal threshold for comparison
        print("\n8. Testing with normal threshold (0.8) for comparison...")
        request_normal = ToolRequest(
            tool_id=ner_tool.tool_id,
            operation="extract_entities",
            input_data={
                "text": test_text,
                "chunk_ref": "test_chunk_002"
            },
            parameters={
                "confidence_threshold": 0.8,  # Normal threshold
                "chunk_confidence": 1.0
            }
        )
        
        result_normal = ner_tool.execute(request_normal)
        if result_normal.status == "success":
            entities_normal = result_normal.data.get("entities", [])
            print(f"   Entities with threshold=0.8: {len(entities_normal)}")
            print(f"   Entities with threshold=0.0: {len(entities)}")
            print(f"   Additional entities with threshold=0: {len(entities) - len(entities_normal)}")
    else:
        print(f"   Error: {result.error_message}")
        print(f"   Error code: {result.error_code}")
    
    print("\n✅ Entity extraction threshold test complete!")
    return result.status == "success"

if __name__ == "__main__":
    success = test_entity_extraction_threshold_zero()
    sys.exit(0 if success else 1)