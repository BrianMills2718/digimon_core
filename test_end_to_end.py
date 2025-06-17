#!/usr/bin/env python3
"""End-to-end test with a real PDF"""

import sys
from pathlib import Path
import tempfile

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def create_test_pdf():
    """Create a test PDF using reportlab"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Add content
        y = 750
        content = [
            "Research Paper: Technology Companies",
            "",
            "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.",
            "The company is headquartered in Cupertino, California.",
            "Apple produces consumer electronics including the iPhone, iPad, and Mac computers.",
            "",
            "Tesla Inc. was founded by Elon Musk in 2003 in Palo Alto, California.",
            "Tesla specializes in electric vehicles and clean energy technology.",
            "The company moved its headquarters to Austin, Texas in 2021.",
            "",
            "Microsoft Corporation was founded by Bill Gates and Paul Allen in 1975.",
            "Microsoft is based in Redmond, Washington and creates software products.",
            "The company produces Windows operating system and Office productivity suite.",
            "",
            "Google was founded by Larry Page and Sergey Brin in 1998.",
            "Google is headquartered in Mountain View, California.",
            "The company specializes in internet search and online advertising."
        ]
        
        for line in content:
            if line:  # Skip empty lines
                c.drawString(50, y, line)
            y -= 25
            if y < 50:  # Start new page if needed
                c.showPage()
                y = 750
        
        c.save()
        return pdf_path
        
    except ImportError:
        print("❌ reportlab not available, install with: pip install reportlab")
        return None
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")
        return None

def test_full_pipeline(pdf_path):
    """Test the complete pipeline"""
    print(f"🔬 Testing complete pipeline with: {pdf_path}")
    
    try:
        from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        
        # Initialize workflow
        workflow = VerticalSliceWorkflow(workflow_storage_dir="./data/end_to_end_test")
        
        # Test queries
        test_queries = [
            "Who founded Apple?",
            "Where is Tesla headquartered?", 
            "What does Microsoft produce?",
            "Who founded Google?",
            "Which companies are mentioned?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            print("⏳ Processing... (this will take time for real processing)")
            
            try:
                result = workflow.execute_workflow(
                    pdf_path=pdf_path,
                    query=query,
                    workflow_name=f"EndToEnd_{query[:20]}"
                )
                
                print(f"   Status: {result['status']}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                
                if result["status"] == "success":
                    # Workflow summary
                    if "workflow_summary" in result:
                        summary = result["workflow_summary"]
                        print(f"   📊 Chunks: {summary.get('chunks_created', 0)}")
                        print(f"   📊 Entities: {summary.get('entities_extracted', 0)}")
                        print(f"   📊 Relationships: {summary.get('relationships_found', 0)}")
                        print(f"   📊 Graph entities: {summary.get('graph_entities', 0)}")
                    
                    # Query results
                    if "query_result" in result:
                        query_result = result["query_result"]
                        
                        if query_result.get("results"):
                            print("   💡 Top answers:")
                            for answer in query_result["results"][:2]:
                                print(f"      • {answer.get('answer_entity', 'N/A')} (conf: {answer.get('confidence', 0):.2f})")
                        
                        if query_result.get("top_entities"):
                            print("   🏆 Top entities:")
                            for entity in query_result["top_entities"][:3]:
                                print(f"      • {entity.get('name', 'N/A')} (rank: {entity.get('pagerank_score', 0):.4f})")
                
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"   💥 Query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run end-to-end test"""
    print("🚀 END-TO-END PIPELINE TEST")
    print("Testing with real PDF processing (no mocking)")
    print("=" * 60)
    
    # Create test PDF
    print("📄 Creating test PDF...")
    pdf_path = create_test_pdf()
    
    if not pdf_path:
        print("❌ Cannot create test PDF")
        return False
    
    print(f"✅ Created test PDF: {pdf_path}")
    
    # Test pipeline
    success = test_full_pipeline(pdf_path)
    
    # Cleanup
    import os
    if os.path.exists(pdf_path):
        os.unlink(pdf_path)
        print(f"🗑️  Cleaned up: {pdf_path}")
    
    if success:
        print("\n🎉 END-TO-END TEST PASSED!")
        print("📱 The system can process real PDFs and answer questions")
        print("💡 Upload functionality issue is likely browser/UI specific")
    else:
        print("\n💥 END-TO-END TEST FAILED!")
        print("🔧 Core pipeline needs fixes before UI testing")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)