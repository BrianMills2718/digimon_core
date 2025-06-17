#!/usr/bin/env python3
"""Simple debug UI to test PDF upload functionality"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
import traceback

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

st.set_page_config(page_title="Simple PDF Test", page_icon="📄")

st.title("📄 Simple PDF Upload Test")
st.markdown("Debug version to test upload functionality")

# Basic system check
st.header("System Status")

try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        session.run("RETURN 1")
    driver.close()
    st.success("✅ Neo4j Connected")
    neo4j_ok = True
except Exception as e:
    st.error(f"❌ Neo4j: {e}")
    neo4j_ok = False

try:
    from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
    st.success("✅ Workflow Available")
    workflow_ok = True
except Exception as e:
    st.error(f"❌ Workflow: {e}")
    workflow_ok = False

# File upload test
st.header("File Upload Test")

uploaded_file = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"],
    help="Test PDF file upload functionality"
)

if uploaded_file is not None:
    st.success("🎉 File upload working!")
    
    # Show file details
    st.write("**File Details:**")
    st.write(f"- Name: {uploaded_file.name}")
    st.write(f"- Size: {uploaded_file.size:,} bytes ({uploaded_file.size/(1024*1024):.2f} MB)")
    st.write(f"- Type: {uploaded_file.type}")
    
    # Validate PDF
    file_content = uploaded_file.read()
    is_pdf = file_content.startswith(b'%PDF')
    
    if is_pdf:
        st.success("✅ Valid PDF file detected")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        st.write(f"📁 Saved to: {tmp_path}")
        
        # Test processing if systems are OK
        if neo4j_ok and workflow_ok:
            
            query = st.text_input("Enter a question about the PDF:", value="What are the main topics?")
            
            if st.button("🔍 Process PDF") and query:
                try:
                    st.info("⏳ Processing... this may take 1-3 minutes for real processing")
                    
                    # Initialize workflow
                    workflow = VerticalSliceWorkflow(workflow_storage_dir="./data/ui_test")
                    
                    # Execute workflow
                    with st.spinner("Processing PDF and building graph..."):
                        result = workflow.execute_workflow(
                            pdf_path=tmp_path,
                            query=query,
                            workflow_name="Simple_UI_Test"
                        )
                    
                    # Show results
                    st.header("📊 Results")
                    
                    if result["status"] == "success":
                        st.success("✅ Processing completed!")
                        
                        # Workflow summary
                        if "workflow_summary" in result:
                            summary = result["workflow_summary"]
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Chunks", summary.get('chunks_created', 0))
                            with col2:
                                st.metric("Entities", summary.get('entities_extracted', 0))
                            with col3:
                                st.metric("Relationships", summary.get('relationships_found', 0))
                        
                        # Query results
                        if "query_result" in result and result["query_result"].get("results"):
                            st.subheader("🎯 Query Answers")
                            for i, answer in enumerate(result["query_result"]["results"][:3]):
                                st.write(f"**{i+1}.** {answer.get('answer_entity', 'N/A')} (confidence: {answer.get('confidence', 0):.2f})")
                                if "evidence" in answer:
                                    st.write(f"   Evidence: {answer['evidence'][:200]}...")
                        
                        # Top entities
                        if "query_result" in result and result["query_result"].get("top_entities"):
                            st.subheader("🏆 Important Entities")
                            entities = result["query_result"]["top_entities"][:10]
                            for entity in entities:
                                st.write(f"- {entity.get('name', 'N/A')} (rank: {entity.get('pagerank_score', 0):.4f})")
                    
                    else:
                        st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                        
                        if "partial_results" in result:
                            st.info("Partial results obtained:")
                            st.json(result["partial_results"])
                
                except Exception as e:
                    st.error(f"💥 Processing error: {e}")
                    st.code(traceback.format_exc())
                
                finally:
                    # Cleanup temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        
        else:
            st.warning("⚠️ Cannot process PDF - system components not ready")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    else:
        st.error("❌ Not a valid PDF file")

else:
    st.info("👆 Upload a PDF file to test the system")

# Instructions
st.header("📋 Instructions")
st.markdown("""
1. **Upload a PDF**: Use the file uploader above
2. **Enter a question**: Ask about the content (e.g., "Who are the main people mentioned?")
3. **Process**: Click the process button to run the full GraphRAG pipeline
4. **View results**: See extracted entities, relationships, and answers

**Expected processing time:**
- Small PDFs (1-5 pages): 30-60 seconds  
- Medium PDFs (5-20 pages): 1-3 minutes
- Large PDFs (20+ pages): 3-10 minutes
""")

# Debug info
if st.checkbox("Show debug info"):
    st.header("🔧 Debug Information")
    
    debug_info = {
        "Python Path": sys.path[:3],
        "Working Directory": str(Path.cwd()),
        "Neo4j Status": "OK" if neo4j_ok else "Failed",
        "Workflow Status": "OK" if workflow_ok else "Failed",
        "Streamlit Version": st.__version__
    }
    
    st.json(debug_info)