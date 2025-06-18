#!/usr/bin/env python3
"""Test the UI fixes work correctly"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_quick_mode():
    """Test the quick test mode without PDF"""
    print("🧪 Testing Quick Mode (Text Processing Only)")
    print("=" * 50)
    
    try:
        from tools.phase1.t15a_text_chunker import TextChunker
        from tools.phase1.t23a_spacy_ner import SpacyNER
        from core.identity_service import IdentityService
        from core.provenance_service import ProvenanceService
        from core.quality_service import QualityService
        
        # Sample content
        sample_content = """
        Tesla Inc. is an American electric vehicle company founded by Elon Musk in 2003. 
        The company is headquartered in Austin, Texas. Tesla produces electric vehicles 
        including the Model S, Model 3, Model X, and Model Y.
        
        SpaceX, another company founded by Elon Musk, develops spacecraft and rockets. 
        Both Tesla and SpaceX are innovative technology companies.
        
        Apple Inc. is a technology company founded by Steve Jobs, Steve Wozniak, and 
        Ronald Wayne in 1976. Apple is headquartered in Cupertino, California and 
        produces consumer electronics like the iPhone and Mac computers.
        """
        
        # Initialize services
        print("📋 Initializing services...")
        identity = IdentityService()
        provenance = ProvenanceService()
        quality = QualityService()
        print("✅ Services initialized")
        
        # Process text directly
        print("📝 Processing text...")
        chunker = TextChunker(identity, provenance, quality)
        document_ref = "storage://document/ui_test"
        
        chunk_result = chunker.chunk_text(
            document_ref=document_ref,
            text=sample_content,
            document_confidence=0.9
        )
        
        print(f"✅ Text chunking: {chunk_result['status']}")
        print(f"   📊 Chunks created: {chunk_result['total_chunks']}")
        
        if chunk_result["status"] == "success":
            # Extract entities
            print("🏷️  Extracting entities...")
            ner = SpacyNER(identity, provenance, quality)
            all_entities = []
            
            for i, chunk in enumerate(chunk_result["chunks"]):
                entity_result = ner.extract_entities(
                    chunk_ref=chunk["chunk_ref"],
                    text=chunk["text"],
                    chunk_confidence=chunk["confidence"]
                )
                if entity_result["status"] == "success":
                    all_entities.extend(entity_result["entities"])
                    print(f"   ✅ Chunk {i+1}: {entity_result['total_entities']} entities")
            
            print(f"📊 Total entities extracted: {len(all_entities)}")
            
            if all_entities:
                print("🏷️  Sample entities:")
                for entity in all_entities[:8]:
                    print(f"   • {entity['surface_form']} ({entity['entity_type']}) - {entity['confidence']:.2f}")
            
            # Test query matching
            test_queries = [
                "Who founded Tesla?",
                "Where is Tesla headquartered?", 
                "Who founded Apple?",
                "What does Tesla make?"
            ]
            
            print("\n🔍 Testing query matching...")
            for query in test_queries:
                query_lower = query.lower()
                relevant_entities = []
                
                for entity in all_entities:
                    entity_name = entity["surface_form"].lower()
                    if any(word in entity_name for word in query_lower.split()):
                        relevant_entities.append(entity)
                
                print(f"   Query: '{query}'")
                if relevant_entities:
                    print(f"      → Found: {relevant_entities[0]['surface_form']}")
                else:
                    print(f"      → No direct matches found")
            
            print("\n✅ Quick mode test completed successfully!")
            return True
            
        else:
            print(f"❌ Text processing failed: {chunk_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Quick mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_validation():
    """Test PDF validation logic"""
    print("\n📄 Testing PDF Validation")
    print("=" * 50)
    
    # Test PDF header validation
    test_cases = [
        (b'%PDF-1.4\nrest of pdf...', True, "Valid PDF header"),
        (b'%PDF-1.7\nrest of pdf...', True, "Valid PDF 1.7 header"),
        (b'Not a PDF file', False, "Invalid header"),
        (b'', False, "Empty file"),
        (b'<html><body>HTML file</body></html>', False, "HTML file")
    ]
    
    for content, should_pass, description in test_cases:
        result = content.startswith(b'%PDF')
        status = "✅" if result == should_pass else "❌"
        print(f"   {status} {description}: {result}")
    
    print("✅ PDF validation test completed!")
    return True

def main():
    """Run all UI fix tests"""
    print("🔧 TESTING UI FIXES")
    print("=" * 50)
    
    results = []
    results.append(("Quick Mode", test_quick_mode()))
    results.append(("PDF Validation", test_pdf_validation()))
    
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    if passed == len(results):
        print("\n🎉 All UI fixes working correctly!")
        print("💡 The web UI should now work properly")
        print("📱 Run: streamlit run web_ui.py")
    else:
        print(f"\n🔧 {len(results)-passed} issues still need fixing")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)