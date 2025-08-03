#!/usr/bin/env python3
"""
Test the enhanced T27 relationship extractor with comprehensive patterns and debugging
"""
import sys
import logging
sys.path.append('/home/brian/projects/Digimons')

from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from src.tools.base_tool import ToolRequest
from src.core.service_manager import ServiceManager

# Set up logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_enhanced_relationship_extraction():
    """Test relationship extraction with sample text containing clear relationships"""
    
    print("🧪 TESTING ENHANCED T27 RELATIONSHIP EXTRACTOR")
    print("=" * 60)
    
    # Sample text with clear relationships
    test_text = """
    John Smith is the CEO of TechCorp and works at the company headquarters. 
    TechCorp was founded by Sarah Johnson in 2010. The company is located in San Francisco.
    Microsoft acquired TechCorp last year for $2 billion. 
    John Smith studied at Stanford University and graduated in 2005.
    Sarah Johnson partnered with Google on several projects.
    """
    
    # Mock entities that should be found by spaCy
    test_entities = [
        {"text": "John Smith", "entity_type": "PERSON", "start": 5, "end": 15, "confidence": 0.9},
        {"text": "TechCorp", "entity_type": "ORG", "start": 30, "end": 38, "confidence": 0.95},
        {"text": "Sarah Johnson", "entity_type": "PERSON", "start": 80, "end": 93, "confidence": 0.9},
        {"text": "San Francisco", "entity_type": "GPE", "start": 150, "end": 163, "confidence": 0.85},
        {"text": "Microsoft", "entity_type": "ORG", "start": 180, "end": 189, "confidence": 0.95},
        {"text": "Stanford University", "entity_type": "ORG", "start": 250, "end": 269, "confidence": 0.9},
        {"text": "Google", "entity_type": "ORG", "start": 320, "end": 326, "confidence": 0.95}
    ]
    
    try:
        # Initialize T27 with service manager
        service_manager = ServiceManager()
        extractor = T27RelationshipExtractorUnified(service_manager)
        
        print(f"\n📝 Test Text ({len(test_text)} characters):")
        print(f"'{test_text.strip()}'")
        
        print(f"\n🏷️  Available Entities ({len(test_entities)}):")
        for entity in test_entities:
            print(f"  - '{entity['text']}' ({entity['entity_type']}) [confidence: {entity['confidence']}]")
        
        # Create tool request
        request = ToolRequest(
            tool_id="T27_ENHANCED",
            operation="extract_relationships",
            input_data={
                "text": test_text,
                "entities": test_entities,
                "chunk_ref": "test_chunk_001"
            },
            parameters={
                "confidence_threshold": 0.3  # Lower threshold to see more results
            }
        )
        
        print(f"\n🔄 Executing T27 relationship extraction...")
        print(f"   Confidence threshold: {request.parameters['confidence_threshold']}")
        
        # Execute extraction
        result = extractor.execute(request)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"   Status: {result.status}")
        print(f"   Execution time: {result.execution_time:.3f}s")
        print(f"   Memory used: {result.memory_used} bytes")
        
        if result.status == "success":
            relationships = result.data.get("relationships", [])
            print(f"   Relationships found: {len(relationships)}")
            
            if relationships:
                print(f"\n✅ FOUND RELATIONSHIPS:")
                for i, rel in enumerate(relationships, 1):
                    print(f"   {i}. {rel['relationship_type']}")
                    print(f"      Subject: '{rel['subject']['text']}' ({rel['subject']['entity_type']})")
                    print(f"      Object: '{rel['object']['text']}' ({rel['object']['entity_type']})")
                    print(f"      Confidence: {rel['confidence']:.3f}")
                    print(f"      Pattern: {rel['pattern_name']}")
                    print(f"      Evidence: '{rel['evidence_text']}'")
                    print()
            else:
                print(f"\n❌ NO RELATIONSHIPS FOUND")
                
            # Show extraction stats
            extraction_stats = result.data.get("extraction_stats", {})
            print(f"📈 EXTRACTION STATISTICS:")
            for stat_name, stat_value in extraction_stats.items():
                print(f"   {stat_name}: {stat_value}")
                
        else:
            print(f"❌ EXTRACTION FAILED:")
            print(f"   Error: {result.error_message}")
            print(f"   Error code: {result.error_code}")
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        
    print(f"\n{'='*60}")
    print("🧪 Test complete!")


def test_pattern_matching_debug():
    """Test individual pattern matching to debug issues"""
    
    print("\n🔍 PATTERN MATCHING DEBUG TEST")
    print("=" * 40)
    
    # Test simple cases
    test_cases = [
        {
            "text": "John Smith is the CEO of TechCorp",
            "entities": [
                {"text": "John Smith", "entity_type": "PERSON", "start": 0, "end": 10},
                {"text": "TechCorp", "entity_type": "ORG", "start": 26, "end": 34}
            ],
            "expected_relationships": ["WORKS_FOR"]
        },
        {
            "text": "Microsoft acquired TechCorp",
            "entities": [
                {"text": "Microsoft", "entity_type": "ORG", "start": 0, "end": 9},
                {"text": "TechCorp", "entity_type": "ORG", "start": 19, "end": 27}
            ],
            "expected_relationships": ["ACQUIRED"]
        },
        {
            "text": "TechCorp is located in San Francisco",
            "entities": [
                {"text": "TechCorp", "entity_type": "ORG", "start": 0, "end": 8},
                {"text": "San Francisco", "entity_type": "GPE", "start": 23, "end": 36}
            ],
            "expected_relationships": ["LOCATED_IN"]
        }
    ]
    
    service_manager = ServiceManager()
    extractor = T27RelationshipExtractorUnified(service_manager)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: '{test_case['text']}'")
        
        request = ToolRequest(
            tool_id="T27_ENHANCED",
            operation="extract_relationships", 
            input_data={
                "text": test_case["text"],
                "entities": test_case["entities"],
                "chunk_ref": f"debug_test_{i}"
            },
            parameters={"confidence_threshold": 0.1}
        )
        
        result = extractor.execute(request)
        relationships_found = result.data.get("relationships", []) if result.status == "success" else []
        
        print(f"   Expected: {test_case['expected_relationships']}")
        print(f"   Found: {[r['relationship_type'] for r in relationships_found]}")
        print(f"   Status: {'✅ PASS' if relationships_found else '❌ FAIL'}")


if __name__ == "__main__":
    test_enhanced_relationship_extraction()
    test_pattern_matching_debug()