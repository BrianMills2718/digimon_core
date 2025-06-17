#!/usr/bin/env python3
"""Test the Super-Digimon system with your own PDF and queries"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow

def test_with_your_pdf():
    """Test with your own PDF file and queries"""
    
    # Initialize the workflow
    workflow = VerticalSliceWorkflow(workflow_storage_dir="./data/test_workflows")
    
    # Example with your PDF path - CHANGE THIS to your actual PDF
    pdf_path = input("Enter path to your PDF file: ").strip()
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"📄 Processing: {pdf_path}")
    
    while True:
        # Get your query
        query = input("\nEnter your question (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        if not query:
            continue
            
        print(f"🔍 Query: {query}")
        print("⏳ Processing... (this may take a few minutes)")
        
        try:
            # Execute the complete workflow
            result = workflow.execute_workflow(
                pdf_path=pdf_path,
                query=query,
                workflow_name=f"User_Query_{len(query)}"
            )
            
            print("\n" + "="*60)
            print("📊 RESULTS:")
            print("="*60)
            
            if result["status"] == "success":
                print(f"✅ Workflow completed successfully")
                print(f"📈 Processing confidence: {result.get('confidence', 'N/A')}")
                
                # Show workflow summary
                if "workflow_summary" in result:
                    summary = result["workflow_summary"]
                    print(f"\n📋 Workflow Summary:")
                    print(f"   • Document: {summary.get('document_processed', 'N/A')}")
                    print(f"   • Chunks: {summary.get('chunks_created', 0)}")
                    print(f"   • Entities: {summary.get('entities_extracted', 0)}")
                    print(f"   • Relationships: {summary.get('relationships_found', 0)}")
                    print(f"   • Graph entities: {summary.get('graph_entities', 0)}")
                    print(f"   • Graph edges: {summary.get('graph_edges', 0)}")
                
                # Show query results
                if "query_result" in result:
                    query_result = result["query_result"]
                    print(f"\n💡 Query Results:")
                    
                    if query_result.get("results"):
                        for i, answer in enumerate(query_result["results"][:3]):
                            print(f"   {i+1}. {answer.get('answer_entity', 'N/A')} "
                                  f"(confidence: {answer.get('confidence', 0):.2f})")
                            if "evidence" in answer:
                                print(f"      Evidence: {answer['evidence'][:100]}...")
                    else:
                        print("   No specific answers found")
                        
                    if query_result.get("top_entities"):
                        print(f"\n🏆 Most Relevant Entities:")
                        for entity in query_result["top_entities"][:5]:
                            print(f"   • {entity.get('name', 'N/A')} "
                                  f"(rank: {entity.get('pagerank_score', 0):.4f})")
            else:
                print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🤖 Super-Digimon PDF Query System")
    print("="*40)
    print("This will process your PDF and answer questions about it.")
    print("Make sure Neo4j is running: docker-compose up -d neo4j")
    print()
    
    test_with_your_pdf()