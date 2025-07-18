#!/usr/bin/env python3
"""Streamlit Web UI for Super-Digimon GraphRAG System"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
import json
from datetime import datetime
import platform
import traceback
import networkx as nx
import plotly.graph_objects as go

# Add src to path
src_dir = Path(__file__).parent / "src"

try:
    from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
    SYSTEM_AVAILABLE = True
except ImportError as e:
    SYSTEM_AVAILABLE = False
    IMPORT_ERROR = str(e)

def init_session_state():
    """Initialize session state variables"""
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

def initialize_workflow():
    """Initialize the workflow system"""
    if st.session_state.workflow is None:
        try:
            st.session_state.workflow = VerticalSliceWorkflow(
                workflow_storage_dir="./data/ui_workflows"
            )
            return True
        except Exception as e:
            st.error(f"Failed to initialize workflow: {e}")
            return False
    return True

def process_uploaded_file(uploaded_file):
    """Process uploaded PDF file"""
    if uploaded_file is None:
        return None
    
    try:
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            st.error("Please upload a PDF file only")
            return None
        
        # Check file size (limit to 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            st.error("File too large. Please upload a PDF under 50MB")
            return None
        
        # Create temporary file with proper PDF extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="uploaded_") as tmp_file:
            # Read file content
            file_content = uploaded_file.read()
            
            # Basic PDF validation - check for PDF header
            if not file_content.startswith(b'%PDF'):
                st.error("Invalid PDF file. Please upload a valid PDF document.")
                return None
            
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        # Debug info for WSL
        st.info(f"📁 Saved to: {tmp_path}")
        if st.checkbox("Show file debug info"):
            st.write(f"🔍 Debug: File exists: {os.path.exists(tmp_path)}")
            st.write(f"🔍 Debug: File size: {os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 'N/A'} bytes")
            st.write(f"🔍 Debug: File permissions: {oct(os.stat(tmp_path).st_mode) if os.path.exists(tmp_path) else 'N/A'}")
            st.write(f"🔍 Debug: Is file: {os.path.isfile(tmp_path) if os.path.exists(tmp_path) else 'N/A'}")
            st.write(f"🔍 Debug: Can read: {os.access(tmp_path, os.R_OK) if os.path.exists(tmp_path) else 'N/A'}")
        
        return tmp_path
        
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
        return None

def run_query(file_path, query, file_name):
    """Run a query against the processed document"""
    if not initialize_workflow():
        return None
    
    try:
        # Extra debug for WSL file issues
        if st.checkbox("Enable verbose debug"):
            st.write(f"🔍 Debug: About to process file: {file_path}")
            st.write(f"🔍 Debug: File exists before processing: {os.path.exists(file_path)}")
            st.write(f"🔍 Debug: File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")
        
        with st.spinner(f"Processing query: '{query}'..."):
            result = st.session_state.workflow.execute_workflow(
                pdf_path=file_path,
                query=query,
                workflow_name=f"UI_{file_name}_{len(query)}"
            )
        
        # Add to query history
        st.session_state.query_history.append({
            'timestamp': datetime.now(),
            'file_name': file_name,
            'query': query,
            'result': result
        })
        
        return result
        
    except Exception as e:
        error_trace = traceback.format_exc()
        st.error(f"Error processing query: {e}")
        st.error(f"🔍 Debug: Exception type: {type(e).__name__}")
        with st.expander("Full error traceback"):
            st.code(error_trace, language="python")
        
        # Return error result with traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": error_trace,
            "exception_type": type(e).__name__
        }

def display_results(result):
    """Display query results in a nice format"""
    if not result:
        return
    
    if result["status"] == "success":
        st.success("✅ Query processed successfully!")
        
        # Overall confidence
        confidence = result.get('confidence', 0)
        st.metric("Overall Confidence", f"{confidence:.2f}")
        
        # Workflow summary
        if "workflow_summary" in result:
            summary = result["workflow_summary"]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Chunks Created", summary.get('chunks_created', 0))
            with col2:
                st.metric("Entities Found", summary.get('entities_extracted', 0))
            with col3:
                st.metric("Relationships", summary.get('relationships_found', 0))
            with col4:
                st.metric("Graph Entities", summary.get('graph_entities', 0))
        
        # Query results
        if "query_result" in result:
            query_result = result["query_result"]
            
            st.subheader("🔍 Query Results")
            
            if query_result.get("results"):
                st.write("**Direct Answers:**")
                for i, answer in enumerate(query_result["results"][:5]):
                    with st.expander(f"Answer {i+1}: {answer.get('answer_entity', 'N/A')}", expanded=i==0):
                        st.write(f"**Entity:** {answer.get('answer_entity', 'N/A')}")
                        st.write(f"**Confidence:** {answer.get('confidence', 0):.2f}")
                        if "evidence" in answer:
                            st.write(f"**Evidence:** {answer['evidence']}")
                        if "full_path" in answer:
                            st.write(f"**Path:** {answer['full_path']}")
            else:
                st.info("No direct answers found, but here are relevant entities:")
            
            # Top entities
            if query_result.get("top_entities"):
                st.write("**Most Relevant Entities:**")
                entities_df = []
                for entity in query_result["top_entities"][:10]:
                    entities_df.append({
                        "Entity": entity.get('name', 'N/A'),
                        "PageRank Score": f"{entity.get('pagerank_score', 0):.6f}",
                        "Type": entity.get('type', 'Unknown')
                    })
                
                if entities_df:
                    st.dataframe(entities_df, use_container_width=True)
        
        # Store the result for graph visualization
        if "workflow_summary" in result:
            st.session_state.last_result = result
        
    else:
        st.error(f"❌ Query failed: {result.get('error', 'Unknown error')}")
        
        # Show detailed error info
        if "exception_type" in result:
            st.error(f"Exception type: {result['exception_type']}")
        
        if "traceback" in result:
            with st.expander("🔍 Debug: Full Error Traceback"):
                st.code(result["traceback"], language="python")
        
        if "partial_results" in result:
            st.info("Some partial results were obtained:")
            st.json(result["partial_results"])

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Super-Digimon GraphRAG",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Super-Digimon GraphRAG System")
    st.markdown("Upload a PDF and ask questions about its content!")
    
    init_session_state()
    
    # Check if system is available
    if not SYSTEM_AVAILABLE:
        st.error(f"❌ System not available: {IMPORT_ERROR}")
        st.info("Make sure you're in the correct directory and dependencies are installed.")
        return
    
    # Sidebar for system status
    with st.sidebar:
        st.header("System Status")
        
        # Environment info for WSL debugging
        with st.expander("🔍 Environment Info"):
            st.write(f"Platform: {platform.system()}")
            st.write(f"Release: {platform.release()}")
            st.write(f"WSL: {'Microsoft' in platform.release() or 'WSL' in platform.release()}")
            st.write(f"Python: {sys.version.split()[0]}")
            st.write(f"Working Dir: {os.getcwd()}")
            st.write(f"Temp Dir: {tempfile.gettempdir()}")
        
        # Check Neo4j connection
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            st.success("✅ Neo4j Connected")
        except Exception as e:
            st.error("❌ Neo4j Disconnected")
            st.info("Run: `docker-compose up -d neo4j`")
        
        # System info
        if initialize_workflow():
            st.success("✅ Workflow Ready")
        else:
            st.error("❌ Workflow Failed")
        
        st.header("Query History")
        if st.session_state.query_history:
            for i, item in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history)-i}"):
                    st.write(f"**File:** {item['file_name']}")
                    st.write(f"**Query:** {item['query']}")
                    st.write(f"**Status:** {item['result'].get('status', 'unknown')}")
                    st.write(f"**Time:** {item['timestamp'].strftime('%H:%M:%S')}")
        else:
            st.info("No queries yet")
    
    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload & Query", "🧪 Quick Test", "📊 System Info", "🔍 Graph Explorer"])
    
    with tab1:
        st.header("Upload PDF and Ask Questions")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a PDF document to analyze",
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            st.success(f"📄 Uploaded: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Show file details
            with st.expander("File Details"):
                st.write(f"**Name:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size:,} bytes ({uploaded_file.size/(1024*1024):.2f} MB)")
                st.write(f"**Type:** {uploaded_file.type}")
            
            # Process file
            file_path = process_uploaded_file(uploaded_file)
            
            if file_path:
                # Query input
                st.subheader("Ask a Question")
                
                # Predefined example queries
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    query = st.text_input(
                        "Enter your question:",
                        placeholder="e.g., Who are the main people mentioned in this document?"
                    )
                
                with col2:
                    example_queries = [
                        "Who are the key people?",
                        "What organizations are mentioned?",
                        "What are the main topics?",
                        "Where are the locations?",
                        "When did events occur?"
                    ]
                    
                    selected_example = st.selectbox(
                        "Or choose an example:",
                        [""] + example_queries
                    )
                    
                    if selected_example:
                        query = selected_example
                
                # Execute query
                if st.button("🔍 Run Query", type="primary") and query:
                    result = run_query(file_path, query, uploaded_file.name)
                    
                    if result:
                        display_results(result)
                
                # Cleanup temp file (with better error handling for WSL)
                if file_path and os.path.exists(file_path):
                    try:
                        os.unlink(file_path)
                    except Exception as e:
                        st.warning(f"Could not delete temp file: {e}")
    
    with tab2:
        st.header("Quick Test with Sample Data")
        st.markdown("Test the system with built-in sample content")
        
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
        
        st.text_area("Sample Content:", sample_content, height=150, disabled=True)
        
        sample_queries = [
            "Who founded Tesla?",
            "Where is Tesla headquartered?",
            "What companies did Elon Musk found?",
            "Who founded Apple?",
            "What products does Apple make?"
        ]
        
        selected_query = st.selectbox("Choose a test query:", sample_queries)
        
        if st.button("🧪 Run Test Query", type="primary"):
            # Test without PDF - use direct workflow components
            try:
                if not initialize_workflow():
                    st.error("Failed to initialize workflow")
                    return
                
                with st.spinner("Processing sample query..."):
                    # Use the chunker and NER directly instead of full PDF workflow
                    from tools.phase1.t15a_text_chunker import TextChunker
                    from tools.phase1.t23a_spacy_ner import SpacyNER
                    from src.core.service_manager import get_service_manager
                    
                    # Get shared services from manager
                    service_manager = get_service_manager()
                    identity = service_manager.identity_service
                    provenance = service_manager.provenance_service
                    quality = service_manager.quality_service
                    
                    # Process text directly
                    chunker = TextChunker(identity, provenance, quality)
                    document_ref = "storage://document/sample_test"
                    
                    chunk_result = chunker.chunk_text(
                        document_ref=document_ref,
                        text=sample_content,
                        document_confidence=0.9
                    )
                    
                    if chunk_result["status"] == "success":
                        # Extract entities
                        ner = SpacyNER(identity, provenance, quality)
                        all_entities = []
                        
                        for chunk in chunk_result["chunks"]:
                            entity_result = ner.extract_entities(
                                chunk_ref=chunk["chunk_ref"],
                                text=chunk["text"],
                                chunk_confidence=chunk["confidence"]
                            )
                            if entity_result["status"] == "success":
                                all_entities.extend(entity_result["entities"])
                        
                        # Mock result for display
                        mock_result = {
                            "status": "success",
                            "confidence": 0.85,
                            "workflow_summary": {
                                "chunks_created": len(chunk_result["chunks"]),
                                "entities_extracted": len(all_entities),
                                "relationships_found": 0,
                                "graph_entities": 0,
                                "graph_edges": 0
                            },
                            "query_result": {
                                "results": [],
                                "top_entities": [
                                    {"name": entity["surface_form"], 
                                     "pagerank_score": 0.1, 
                                     "type": entity["entity_type"]} 
                                    for entity in all_entities[:10]
                                ]
                            }
                        }
                        
                        # Find relevant entities for the query
                        query_lower = selected_query.lower()
                        relevant_entities = []
                        
                        for entity in all_entities:
                            entity_name = entity["surface_form"].lower()
                            if any(word in entity_name for word in query_lower.split()):
                                relevant_entities.append({
                                    "answer_entity": entity["surface_form"],
                                    "confidence": entity["confidence"],
                                    "evidence": f"Found in sample text: {entity['surface_form']}",
                                    "full_path": f"{entity['surface_form']} -> direct_mention"
                                })
                        
                        if relevant_entities:
                            mock_result["query_result"]["results"] = relevant_entities[:3]
                        
                        display_results(mock_result)
                        
                        st.info("ℹ️ This is a simplified test using text processing only. For full functionality including graph analysis, upload a PDF file.")
                    
                    else:
                        st.error(f"Text processing failed: {chunk_result.get('error', 'Unknown error')}")
                        
            except Exception as e:
                st.error(f"Test query error: {e}")
                st.code(traceback.format_exc())
    
    with tab3:
        st.header("System Information")
        
        # System capabilities
        st.subheader("🔧 System Capabilities")
        capabilities = [
            "✅ PDF text extraction",
            "✅ Named Entity Recognition (spaCy)",
            "✅ Relationship extraction",
            "✅ Graph database storage (Neo4j)",
            "✅ PageRank entity ranking",
            "✅ Multi-hop graph queries",
            "✅ Confidence tracking",
            "✅ Workflow state management"
        ]
        
        for cap in capabilities:
            st.markdown(cap)
        
        # Architecture info
        st.subheader("🏗️ Architecture")
        st.markdown("""
        - **Document Processing**: PDF → Text Chunks → Entities → Relationships
        - **Graph Storage**: Neo4j for entities and relationships
        - **Entity Ranking**: PageRank algorithm for importance scoring
        - **Query Processing**: Multi-hop graph traversal for answers
        - **Quality Tracking**: Confidence propagation through pipeline
        """)
        
        # Performance info
        st.subheader("⚡ Performance")
        st.markdown("""
        - **Small PDFs** (1-10 pages): ~30 seconds
        - **Medium PDFs** (10-50 pages): ~2-5 minutes  
        - **Large PDFs** (50+ pages): ~5-15 minutes
        - **Memory Usage**: ~500MB-2GB depending on document size
        """)
        
        # Debug info
        if st.button("🔧 Show Debug Info"):
            st.subheader("Debug Information")
            
            debug_info = {
                "Python Path": sys.path[:3],
                "Working Directory": str(Path.cwd()),
                "System Available": SYSTEM_AVAILABLE,
                "Query History Count": len(st.session_state.query_history),
                "Workflow Initialized": st.session_state.workflow is not None
            }
            
            st.json(debug_info)

    with tab4:
        st.header("Graph Explorer")
        st.markdown("Visualize the knowledge graph extracted from your documents")
        
        # Check Neo4j connection
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            
            # Query options
            col1, col2 = st.columns([2, 1])
            with col1:
                entity_filter = st.text_input(
                    "Filter entities (optional):",
                    placeholder="e.g., Elon Musk, Tesla",
                    help="Leave empty to show all entities"
                )
            
            with col2:
                limit = st.slider("Max nodes to display:", 10, 100, 30)
            
            if st.button("🔍 Load Graph", type="primary"):
                with st.spinner("Loading graph data..."):
                    # Build the query
                    if entity_filter:
                        # Query for specific entity and its neighbors
                        query = """
                        MATCH (e:Entity)
                        WHERE e.canonical_name CONTAINS $filter
                        WITH e
                        LIMIT 1
                        MATCH path = (e)-[r]-(connected)
                        RETURN e, r, connected, path
                        LIMIT $limit
                        """
                        params = {"filter": entity_filter, "limit": limit}
                    else:
                        # Query for top entities by PageRank
                        query = """
                        MATCH (e:Entity)
                        WITH e
                        ORDER BY coalesce(e.pagerank_score, 0) DESC
                        LIMIT $limit
                        OPTIONAL MATCH (e)-[r]-(connected)
                        RETURN e, r, connected
                        LIMIT $limit
                        """
                        params = {"limit": limit}
                    
                    with driver.session() as session:
                        result = session.run(query, params)
                        
                        # Build graph data
                        G = nx.Graph()
                        nodes = {}
                        edges = []
                        
                        for record in result:
                            # Add main entity
                            if 'e' in record and record['e']:
                                entity = record['e']
                                node_id = entity['entity_id']
                                nodes[node_id] = {
                                    'name': entity['canonical_name'],
                                    'type': entity.get('entity_type', 'UNKNOWN'),
                                    'pagerank': entity.get('pagerank_score', 0),
                                    'confidence': entity.get('confidence', 0.5)
                                }
                                G.add_node(node_id)
                            
                            # Add connected entity
                            if 'connected' in record and record['connected']:
                                connected = record['connected']
                                conn_id = connected['entity_id']
                                nodes[conn_id] = {
                                    'name': connected['canonical_name'],
                                    'type': connected.get('entity_type', 'UNKNOWN'),
                                    'pagerank': connected.get('pagerank_score', 0),
                                    'confidence': connected.get('confidence', 0.5)
                                }
                                G.add_node(conn_id)
                            
                            # Add edge
                            if 'r' in record and record['r'] and 'e' in record and 'connected' in record:
                                edge = {
                                    'source': record['e']['entity_id'],
                                    'target': record['connected']['entity_id'],
                                    'type': record['r'].type,
                                    'confidence': record['r'].get('confidence', 0.5)
                                }
                                edges.append(edge)
                                G.add_edge(edge['source'], edge['target'])
                    
                    driver.close()
                    
                    if len(nodes) == 0:
                        st.warning("No entities found in the graph")
                    else:
                        # Create Plotly visualization
                        st.subheader(f"Knowledge Graph ({len(nodes)} nodes, {len(edges)} edges)")
                        
                        # Use spring layout
                        pos = nx.spring_layout(G, k=2, iterations=50)
                        
                        # Create edge traces
                        edge_traces = []
                        for edge in edges:
                            if edge['source'] in pos and edge['target'] in pos:
                                x0, y0 = pos[edge['source']]
                                x1, y1 = pos[edge['target']]
                                
                                edge_trace = go.Scatter(
                                    x=[x0, x1, None],
                                    y=[y0, y1, None],
                                    mode='lines',
                                    line=dict(width=2, color='#888'),
                                    hoverinfo='text',
                                    text=f"{edge['type']} (confidence: {edge['confidence']:.2f})",
                                    showlegend=False
                                )
                                edge_traces.append(edge_trace)
                        
                        # Create node trace
                        node_x = []
                        node_y = []
                        node_text = []
                        node_size = []
                        node_color = []
                        
                        # Color map for entity types
                        type_colors = {
                            'PERSON': 'red',
                            'ORG': 'blue',
                            'GPE': 'green',
                            'PRODUCT': 'orange',
                            'EVENT': 'purple',
                            'WORK_OF_ART': 'pink',
                            'LAW': 'brown',
                            'LANGUAGE': 'cyan',
                            'FACILITY': 'yellow',
                            'MONEY': 'gold',
                            'DATE': 'lightgray',
                            'TIME': 'darkgray',
                            'UNKNOWN': 'black'
                        }
                        
                        for node_id, node_data in nodes.items():
                            if node_id in pos:
                                x, y = pos[node_id]
                                node_x.append(x)
                                node_y.append(y)
                                
                                # Create hover text
                                hover_text = f"""<b>{node_data['name']}</b><br>
                                Type: {node_data['type']}<br>
                                PageRank: {node_data['pagerank']:.4f}<br>
                                Confidence: {node_data['confidence']:.2f}"""
                                node_text.append(hover_text)
                                
                                # Size based on PageRank
                                size = 20 + (node_data['pagerank'] * 500)
                                node_size.append(size)
                                
                                # Color based on type
                                color = type_colors.get(node_data['type'], 'gray')
                                node_color.append(color)
                        
                        node_trace = go.Scatter(
                            x=node_x,
                            y=node_y,
                            mode='markers+text',
                            hoverinfo='text',
                            text=[nodes[nid]['name'] for nid in nodes if nid in pos],
                            textposition="top center",
                            hovertext=node_text,
                            marker=dict(
                                size=node_size,
                                color=node_color,
                                line=dict(width=2, color='white')
                            )
                        )
                        
                        # Create the figure
                        fig = go.Figure(data=edge_traces + [node_trace])
                        
                        fig.update_layout(
                            title="Knowledge Graph Visualization",
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=600,
                            plot_bgcolor='white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show entity type legend
                        st.subheader("Entity Types")
                        legend_cols = st.columns(4)
                        for i, (entity_type, color) in enumerate(type_colors.items()):
                            col_idx = i % 4
                            with legend_cols[col_idx]:
                                st.markdown(f"<span style='color:{color}'>●</span> {entity_type}", unsafe_allow_html=True)
                        
                        # Show statistics
                        st.subheader("Graph Statistics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Nodes", len(nodes))
                        
                        with col2:
                            st.metric("Total Edges", len(edges))
                        
                        with col3:
                            if nodes:
                                avg_pagerank = sum(n['pagerank'] for n in nodes.values()) / len(nodes)
                                st.metric("Avg PageRank", f"{avg_pagerank:.4f}")
                        
                        # Show top entities table
                        if nodes:
                            st.subheader("Top Entities by PageRank")
                            sorted_nodes = sorted(nodes.items(), key=lambda x: x[1]['pagerank'], reverse=True)[:10]
                            
                            top_entities = []
                            for node_id, node_data in sorted_nodes:
                                top_entities.append({
                                    "Entity": node_data['name'],
                                    "Type": node_data['type'],
                                    "PageRank": f"{node_data['pagerank']:.4f}",
                                    "Confidence": f"{node_data['confidence']:.2f}"
                                })
                            
                            st.dataframe(top_entities, use_container_width=True)
            
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")
            st.info("Make sure Neo4j is running with: `docker-compose up -d neo4j`")

if __name__ == "__main__":
    main()