#!/usr/bin/env python3
"""Quick test with sample data"""

import sys
from pathlib import Path

src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow

def create_sample_pdf():
    """Create a sample text file to test with"""
    content = """
Tesla Inc. is an American electric vehicle and clean energy company founded by Elon Musk in 2003. 
The company is headquartered in Austin, Texas, and was previously based in Palo Alto, California.

Elon Musk serves as CEO and has been instrumental in Tesla's growth. The company produces electric 
vehicles including the Model S, Model 3, Model X, and Model Y. Tesla also manufactures energy 
storage systems and solar panels.

SpaceX, another company founded by Elon Musk, works closely with Tesla on various technologies. 
Both companies are based in the United States and focus on sustainable technology.

Tesla's main competitors include Ford Motor Company, General Motors, and Volkswagen. The electric 
vehicle market has grown significantly since Tesla's founding.
"""
    
    test_file = Path("sample_doc.txt")
    with open(test_file, 'w') as f:
        f.write(content)
    return str(test_file)

def quick_test():
    """Run a quick test with sample data"""
    print("🚀 Quick Test of Super-Digimon System")
    print("="*40)
    
    # Create sample document
    sample_file = create_sample_pdf()
    print(f"📄 Created sample document: {sample_file}")
    
    # Initialize workflow
    workflow = VerticalSliceWorkflow(workflow_storage_dir="./data/test_workflows")
    
    # Test queries
    test_queries = [
        "Who founded Tesla?",
        "Where is Tesla headquartered?",
        "What products does Tesla make?",
        "Who are Tesla's competitors?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("⏳ Processing...")
        
        try:
            result = workflow.execute_workflow(
                pdf_path=sample_file,
                query=query,
                workflow_name=f"Quick_Test_{len(query)}"
            )
            
            if result["status"] == "success":
                print(f"✅ Success! Confidence: {result.get('confidence', 'N/A')}")
                
                if "query_result" in result and result["query_result"].get("results"):
                    top_answer = result["query_result"]["results"][0]
                    print(f"💡 Top answer: {top_answer.get('answer_entity', 'N/A')}")
                else:
                    print("💡 Answer: Found relevant entities but no specific answer")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Error: {e}")
    
    # Cleanup
    Path(sample_file).unlink()
    print("\n🎉 Quick test complete!")

if __name__ == "__main__":
    quick_test()