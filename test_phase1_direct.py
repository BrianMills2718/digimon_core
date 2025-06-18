#!/usr/bin/env python3
"""
Test Phase 1 processing directly to debug the UI issue
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_phase1_processing():
    """Test Phase 1 workflow with a real document"""
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        
        workflow = VerticalSliceWorkflow()
        
        # Use a sample document
        test_file = "examples/pdfs/wiki1.pdf"
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        print(f"🧪 Testing Phase 1 processing with {test_file}")
        
        # Run the workflow
        query = "What are the main entities and relationships in this document?"
        result = workflow.execute_workflow(test_file, query, "Direct_Test")
        
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, list):
                    print(f"📊 {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"📊 {key}: dict with {len(value)} keys")
                    if key == "steps":
                        print(f"   Steps keys: {list(value.keys())}")
                        for step_key, step_value in value.items():
                            if isinstance(step_value, dict):
                                print(f"     {step_key}: {list(step_value.keys())}")
                                if "results" in step_value:
                                    results = step_value["results"]
                                    if isinstance(results, list):
                                        print(f"       {step_key} results: {len(results)} items")
                                    elif isinstance(results, dict):
                                        print(f"       {step_key} results keys: {list(results.keys())}")
                else:
                    print(f"📊 {key}: {type(value)}")
                    if key == "error" and value:
                        print(f"   ERROR: {value}")
                    if key == "status":
                        print(f"   STATUS: {value}")
        
        # Extract data from workflow steps (the real extraction results)
        steps = result.get("steps", {})
        
        # Get entity extraction results
        entity_extraction = steps.get("entity_extraction", {})
        total_entities = entity_extraction.get("total_entities", 0)
        entity_types = entity_extraction.get("entity_types", {})
        
        # Get relationship extraction results  
        relationship_extraction = steps.get("relationship_extraction", {})
        total_relationships = relationship_extraction.get("total_relationships", 0)
        relationship_types = relationship_extraction.get("relationship_types", {})
        
        print(f"\n📈 EXTRACTION RESULTS:")
        print(f"   Entities extracted: {total_entities}")
        if entity_types:
            print(f"   Entity types: {entity_types}")
        print(f"   Relationships extracted: {total_relationships}")
        if relationship_types:
            print(f"   Relationship types: {relationship_types}")
        
        entities = total_entities
        relationships = total_relationships
        
        print(f"\n🔍 Found {entities} entities")        
        print(f"\n🔗 Found {relationships} relationships")
        
        if entities == 0 and relationships == 0:
            print("\n❌ PROBLEM: Pipeline extracted 0 entities and 0 relationships")
            print("This could indicate:")
            print("1. Document is empty or unreadable")
            print("2. Entity/relationship extraction is not working")
            print("3. Document content doesn't match extraction patterns")
            return False
        else:
            print(f"\n✅ SUCCESS: Extracted {entities} entities and {relationships} relationships")
            print("Note: PageRank failed but extraction worked!")
            return True
            
    except Exception as e:
        print(f"❌ Phase 1 processing failed: {e}")
        return False

if __name__ == "__main__":
    success = test_phase1_processing()
    if not success:
        print("\n🚨 Phase 1 processing is broken - this explains the UI issue")
        sys.exit(1)
    else:
        print("\n✅ Phase 1 processing works - UI issue is in data extraction logic")
        sys.exit(0)