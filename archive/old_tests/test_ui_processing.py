#!/usr/bin/env python3
"""
Test the UI processing function directly to see if it now works correctly
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ui_processing():
    """Test the UI processing function with the updated logic"""
    try:
        # Import the UI processing function
        from ui.graphrag_ui import process_with_phase1
        
        # Use a sample document
        test_file = "examples/pdfs/wiki1.pdf"
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        print(f"🧪 Testing UI processing function with {test_file}")
        
        # Test the UI processing function
        result = process_with_phase1(test_file, "wiki1.pdf")
        
        print(f"📊 UI Processing Result:")
        print(f"   Filename: {result.filename}")
        print(f"   Phase: {result.phase_used}")
        print(f"   Entities found: {result.entities_found}")
        print(f"   Relationships found: {result.relationships_found}")
        print(f"   Processing time: {result.processing_time}")
        
        # Check graph data structure
        graph_data = result.graph_data
        print(f"   Graph data keys: {list(graph_data.keys())}")
        
        if "entities" in graph_data:
            entities = graph_data["entities"]
            print(f"   Actual entities retrieved: {len(entities)}")
            if entities:
                print(f"   Sample entity: {entities[0]}")
        
        if "relationships" in graph_data:
            relationships = graph_data["relationships"]
            print(f"   Actual relationships retrieved: {len(relationships)}")
            if relationships:
                print(f"   Sample relationship: {relationships[0]}")
        
        if "extraction_stats" in graph_data:
            stats = graph_data["extraction_stats"]
            print(f"   Extraction stats: {stats}")
        
        # Success if we found entities or relationships
        if result.entities_found > 0 or result.relationships_found > 0:
            print(f"\n✅ SUCCESS: UI processing found {result.entities_found} entities and {result.relationships_found} relationships")
            return True
        else:
            print(f"\n❌ PROBLEM: UI processing still returned 0 entities and 0 relationships")
            return False
            
    except Exception as e:
        print(f"❌ UI processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_processing()
    if success:
        print("\n🎉 UI processing is now working correctly!")
        print("🚀 Try the UI again - it should show the extracted entities and relationships")
    else:
        print("\n🚨 UI processing still has issues")
    sys.exit(0 if success else 1)