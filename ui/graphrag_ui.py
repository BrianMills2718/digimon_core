#!/usr/bin/env python3
"""
GraphRAG Testing UI for Super-Digimon
Web interface for testing and visualizing GraphRAG capabilities with custom datasets
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from dataclasses import dataclass, asdict
import tempfile
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import components based on availability - CRASH LOUDLY IF MISSING
try:
    from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
    PHASE1_AVAILABLE = True
except ImportError as e:
    st.error("❌ CRITICAL: Phase 1 pipeline not available")
    st.error(f"Import error: {e}")
    st.error("Phase 1 is required for basic functionality")
    st.stop()

try:
    from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
    from src.tools.phase2.interactive_graph_visualizer import InteractiveGraphVisualizer
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False

try:
    from src.tools.phase3.t301_multi_document_fusion_tools import *
    PHASE3_AVAILABLE = True
except ImportError:
    PHASE3_AVAILABLE = False

# MCP connection
try:
    import mcp
    from src.mcp_server import mcp as super_digimon_mcp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="GraphRAG Testing Interface - Super-Digimon",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .phase-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .status-available { color: #10b981; font-weight: bold; }
    .status-missing { color: #ef4444; font-weight: bold; }
    .test-result {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .test-success {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
    }
    .test-error {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
    }
    .file-upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class TestResult:
    success: bool
    phase: str
    operation: str
    duration: float
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None

@dataclass
class DocumentProcessingResult:
    document_id: str
    filename: str
    entities_found: int
    relationships_found: int
    graph_data: Dict
    processing_time: float
    phase_used: str

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []
    if "test_results" not in st.session_state:
        st.session_state.test_results = []
    if "current_graph" not in st.session_state:
        st.session_state.current_graph = None
    if "processing_history" not in st.session_state:
        st.session_state.processing_history = []
    if "query_results" not in st.session_state:
        st.session_state.query_results = []

def render_header():
    """Render main header"""
    st.markdown('<h1 class="main-header">🔬 GraphRAG Testing Interface</h1>', unsafe_allow_html=True)
    st.markdown("**Test and visualize Super-Digimon GraphRAG capabilities with your own datasets**")

def render_system_status():
    """Render system status sidebar"""
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Phase availability
        st.subheader("Available Phases")
        
        # Phase 1 (always available)
        st.markdown('✅ <span class="status-available">Phase 1: Basic Pipeline</span>', unsafe_allow_html=True)
        
        # Phase 2
        if PHASE2_AVAILABLE:
            st.markdown('✅ <span class="status-available">Phase 2: Ontology System</span>', unsafe_allow_html=True)
        else:
            st.markdown('❌ <span class="status-missing">Phase 2: Not Available</span>', unsafe_allow_html=True)
        
        # Phase 3
        if PHASE3_AVAILABLE:
            st.markdown('✅ <span class="status-available">Phase 3: Multi-Document Fusion</span>', unsafe_allow_html=True)
        else:
            st.markdown('❌ <span class="status-missing">Phase 3: Not Available</span>', unsafe_allow_html=True)
        
        # MCP Server
        if MCP_AVAILABLE:
            st.markdown('✅ <span class="status-available">MCP Server Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('❌ <span class="status-missing">MCP Server Disconnected</span>', unsafe_allow_html=True)
        
        # Test controls
        st.subheader("⚙️ Test Configuration")
        
        # Build available phases list based on what's actually available
        available_phases = ["Phase 1: Basic"]
        if PHASE2_AVAILABLE:
            available_phases.append("Phase 2: Enhanced")
        if PHASE3_AVAILABLE:
            available_phases.append("Phase 3: Multi-Doc")
        
        test_phase = st.selectbox(
            "Select Testing Phase",
            available_phases,
            help="Choose which phase to use for document processing"
        )
        
        # Store in session state for access by processing function
        st.session_state.selected_phase = test_phase
        
        enable_visualization = st.checkbox("Enable Graph Visualization", value=True)
        max_entities = st.slider("Max Entities to Display", 10, 500, 100)
        
        # Show warnings for unavailable phases
        if not PHASE2_AVAILABLE:
            st.warning("⚠️ Phase 2 not available - install Phase 2 components")
        if not PHASE3_AVAILABLE:
            st.warning("⚠️ Phase 3 not available - install Phase 3 components")
        
        return test_phase, enable_visualization, max_entities

def render_document_upload():
    """Render document upload interface"""
    st.header("📄 Document Upload & Processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose documents to analyze",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            help="Upload PDF, TXT, or DOCX files for GraphRAG analysis"
        )
        
        if uploaded_files:
            st.write(f"**{len(uploaded_files)} file(s) uploaded:**")
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size:,} bytes)")
    
    with col2:
        if st.button("🚀 Process Documents", type="primary", use_container_width=True):
            if uploaded_files:
                # Get test phase from sidebar
                test_phase = st.session_state.get('selected_phase', 'Phase 1: Basic')
                process_documents(uploaded_files, test_phase)
            else:
                st.error("Please upload at least one document")
        
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_all_data()

def process_documents(uploaded_files, test_phase="Phase 1: Basic"):
    """Process uploaded documents through the GraphRAG pipeline"""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            start_time = datetime.now()
            
            if "Phase 2" in test_phase:
                if not PHASE2_AVAILABLE:
                    raise Exception("❌ Phase 2 selected but not available. Install Phase 2 components.")
                result = process_with_phase2(tmp_path, uploaded_file.name)
            elif "Phase 3" in test_phase:
                if not PHASE3_AVAILABLE:
                    raise Exception("❌ Phase 3 selected but not available. Install Phase 3 components.")
                result = process_with_phase3(tmp_path, uploaded_file.name)
            else:
                result = process_with_phase1(tmp_path, uploaded_file.name)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            results.append(result)
            
        except Exception as e:
            st.error(f"❌ PROCESSING FAILED: {uploaded_file.name}")
            st.error(f"Error: {str(e)}")
            # Don't continue processing if one fails - crash loudly
            st.stop()
        
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Update session state
    st.session_state.processing_history.extend(results)
    if results and results[-1].graph_data:
        st.session_state.current_graph = results[-1].graph_data
    
    status_text.text("✅ Processing complete!")
    
    # Display results
    display_processing_results(results)

def process_with_phase1(file_path: str, filename: str) -> DocumentProcessingResult:
    """Process document with Phase 1 basic pipeline"""
    try:
        workflow = VerticalSliceWorkflow()
        
        # Extract basic query for testing
        query = "What are the main entities and relationships in this document?"
        
        # Run the workflow
        result = workflow.execute_workflow(file_path, query, f"UI_Test_{filename}")
        
        # Extract data from workflow steps, even if final status is "failed"
        entities = []
        relationships = []
        
        # The workflow steps contain the actual extracted data
        steps = result.get("steps", {})
        
        # Get entity extraction results
        entity_extraction = steps.get("entity_extraction", {})
        total_entities = entity_extraction.get("total_entities", 0)
        
        # Get relationship extraction results  
        relationship_extraction = steps.get("relationship_extraction", {})
        total_relationships = relationship_extraction.get("total_relationships", 0)
        
        print(f"DEBUG: Entity extraction step found {total_entities} entities")
        print(f"DEBUG: Relationship extraction step found {total_relationships} relationships")
        print(f"DEBUG: Workflow status: {result.get('status', 'unknown')}")
        if result.get("error"):
            print(f"DEBUG: Workflow error: {result.get('error')}")
        
        # Use the counts from the extraction steps, not final aggregated results
        entities_found = total_entities
        relationships_found = total_relationships
        
        # If still 0, check if extraction steps actually failed
        if entities_found == 0 and relationships_found == 0:
            entity_status = entity_extraction.get("status", "unknown")
            rel_status = relationship_extraction.get("status", "unknown")
            if entity_status == "failed" or rel_status == "failed":
                raise Exception(f"Entity extraction ({entity_status}) or relationship extraction ({rel_status}) failed")
            else:
                print("WARNING: Document may be empty or extraction found nothing (not necessarily an error)")
        
        # Query Neo4j for the actual extracted entities and relationships
        # The workflow stores data in Neo4j even if PageRank fails
        try:
            from py2neo import Graph
            graph = Graph(uri="bolt://localhost:7687", auth=None)
            
            # Query for entities (limit to recent ones from this document)
            entity_query = """
            MATCH (e:Entity) 
            RETURN e.id as id, e.canonical_name as name, e.entity_type as type
            ORDER BY e.created_at DESC 
            LIMIT $limit
            """
            entity_results = graph.run(entity_query, limit=entities_found*2).data()
            entities = entity_results[:entities_found] if entity_results else []
            
            # Query for relationships
            rel_query = """
            MATCH (a:Entity)-[r:RELATIONSHIP]->(b:Entity)
            RETURN a.id as source, b.id as target, r.relation_type as type
            ORDER BY r.created_at DESC
            LIMIT $limit
            """
            rel_results = graph.run(rel_query, limit=relationships_found*2).data()
            relationships = rel_results[:relationships_found] if rel_results else []
            
            print(f"DEBUG: Retrieved {len(entities)} entities and {len(relationships)} relationships from Neo4j")
            
        except Exception as e:
            print(f"DEBUG: Could not query Neo4j for actual data: {e}")
            # If we can't query Neo4j, we'll show the counts but no visualization
            entities = []
            relationships = []
        
        # Create enhanced graph data with actual entities and relationships
        enhanced_graph_data = {
            "original_result": result,
            "entities": entities,
            "relationships": relationships,
            "extraction_stats": {
                "entities_found": entities_found,
                "relationships_found": relationships_found,
                "workflow_status": result.get("status", "unknown"),
                "workflow_error": result.get("error", None)
            }
        }
        
        return DocumentProcessingResult(
            document_id=str(uuid.uuid4()),
            filename=filename,
            entities_found=entities_found,
            relationships_found=relationships_found,
            graph_data=enhanced_graph_data,
            processing_time=0,  # Will be set by caller
            phase_used="Phase 1"
        )
    
    except Exception as e:
        raise Exception(f"Phase 1 processing failed: {str(e)}")

def process_with_phase2(file_path: str, filename: str) -> DocumentProcessingResult:
    """Process document with Phase 2 enhanced pipeline"""
    if not PHASE2_AVAILABLE:
        raise Exception("❌ Phase 2 not available. Install Phase 2 components first.")
    
    try:
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        
        workflow = EnhancedVerticalSliceWorkflow()
        
        # Use ontology-aware processing
        query = "What are the main entities and relationships in this document?"
        
        result = workflow.execute_enhanced_workflow(file_path, query, f"UI_Enhanced_{filename}")
        
        entities_found = len(result.get("entities", []))
        relationships_found = len(result.get("relationships", []))
        
        return DocumentProcessingResult(
            document_id=str(uuid.uuid4()),
            filename=filename,
            entities_found=entities_found,
            relationships_found=relationships_found,
            graph_data=result,
            processing_time=0,
            phase_used="Phase 2"
        )
    
    except Exception as e:
        raise Exception(f"Phase 2 processing failed: {str(e)}")

def process_with_phase3(file_path: str, filename: str) -> DocumentProcessingResult:
    """Process document with Phase 3 multi-document fusion"""
    if not PHASE3_AVAILABLE:
        raise Exception("❌ Phase 3 not available. T301 fusion tools not installed.")
    
    if not PHASE2_AVAILABLE:
        raise Exception("❌ Phase 3 requires Phase 2. Install Phase 2 components first.")
    
    try:
        # Use Phase 2 as base, then add T301 fusion
        result = process_with_phase2(file_path, filename)
        
        # TODO: Add actual T301 multi-document fusion here
        # This would involve calling the T301 MCP tools for entity clustering, etc.
        # For now, this is the same as Phase 2 until T301 integration is complete
        
        result.phase_used = "Phase 3"
        return result
    
    except Exception as e:
        raise Exception(f"Phase 3 processing failed: {str(e)}")

def display_processing_results(results: List[DocumentProcessingResult]):
    """Display processing results in a nice format"""
    st.subheader("📊 Processing Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_entities = sum(r.entities_found for r in results)
    total_relationships = sum(r.relationships_found for r in results)
    avg_processing_time = sum(r.processing_time for r in results) / len(results) if results else 0
    success_rate = len([r for r in results if not hasattr(r, 'error')]) / len(results) * 100 if results else 0
    
    with col1:
        st.metric("Documents Processed", len(results))
    with col2:
        st.metric("Total Entities", total_entities)
    with col3:
        st.metric("Total Relationships", total_relationships)
    with col4:
        st.metric("Avg Processing Time", f"{avg_processing_time:.2f}s")
    
    # Detailed results table
    if results:
        df_data = []
        for r in results:
            df_data.append({
                "Filename": r.filename,
                "Phase": r.phase_used,
                "Entities": r.entities_found,
                "Relationships": r.relationships_found,
                "Processing Time": f"{r.processing_time:.2f}s",
                "Status": "✅ Success" if not hasattr(r, 'error') else "❌ Error"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

def render_query_interface():
    """Render query testing interface"""
    st.header("🔍 Query Testing")
    
    st.error("❌ QUERY INTERFACE NOT IMPLEMENTED")
    st.error("Real graph database querying requires:")
    st.error("• Integration with Neo4j graph database")
    st.error("• SQLite backend connection") 
    st.error("• Actual query processing pipeline")
    st.error("This tab is disabled until real implementation is complete")

def execute_query(query: str):
    """Execute a query against the processed documents"""
    st.error("❌ QUERY FUNCTIONALITY NOT IMPLEMENTED")
    st.error("Real graph database querying requires integration with Neo4j/SQLite backends")
    st.error("This feature is disabled until actual query implementation is complete")
    st.stop()

def render_graph_visualization():
    """Render graph visualization"""
    st.header("🕸️ Knowledge Graph Visualization")
    
    if not st.session_state.current_graph:
        st.info("💡 Process documents to see graph visualization")
        return
    
    # Visualization controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        layout_type = st.selectbox("Layout", ["spring", "circular", "hierarchical"])
    with col2:
        node_size = st.slider("Node Size", 10, 100, 30)
    with col3:
        show_labels = st.checkbox("Show Labels", value=True)
    
    # Create visualization
    try:
        fig = create_graph_visualization(
            st.session_state.current_graph,
            layout_type,
            node_size,
            show_labels
        )
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Visualization error: {str(e)}")

def create_graph_visualization(graph_data: Dict, layout_type: str, node_size: int, show_labels: bool):
    """Create interactive graph visualization using Plotly"""
    # Create NetworkX graph from data
    G = nx.Graph()
    
    # Add nodes and edges from graph_data
    entities = graph_data.get("entities", [])
    relationships = graph_data.get("relationships", [])
    
    # Add entity nodes
    for entity in entities:
        G.add_node(
            entity.get("id", entity.get("name", "Unknown")),
            type=entity.get("type", "UNKNOWN"),
            label=entity.get("name", entity.get("id", "Unknown"))
        )
    
    # Add relationship edges
    for rel in relationships:
        source = rel.get("source", rel.get("source_id", ""))
        target = rel.get("target", rel.get("target_id", ""))
        rel_type = rel.get("type", rel.get("relation_type", "RELATED"))
        
        if source and target:
            G.add_edge(source, target, relation=rel_type)
    
    # Choose layout
    if layout_type == "spring":
        pos = nx.spring_layout(G, k=3, iterations=50)
    elif layout_type == "circular":
        pos = nx.circular_layout(G)
    else:  # hierarchical
        pos = nx.spring_layout(G, k=3)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_info.append(edge[2].get('relation', 'RELATED'))
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    node_colors = []
    
    color_map = {
        'PERSON': '#ff6b6b',
        'ORGANIZATION': '#4ecdc4',
        'LOCATION': '#45b7d1',
        'POLICY': '#96ceb4',
        'EVENT': '#ffeaa7',
        'CONCEPT': '#dda0dd',
        'UNKNOWN': '#95a5a6'
    }
    
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        
        node_type = node[1].get('type', 'UNKNOWN')
        node_label = node[1].get('label', node[0])
        
        node_text.append(node_label if show_labels else '')
        node_info.append(f"{node_label}<br>Type: {node_type}")
        node_colors.append(color_map.get(node_type, color_map['UNKNOWN']))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text' if show_labels else 'markers',
        hoverinfo='text',
        text=node_text,
        hovertext=node_info,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_colors,
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=dict(text="Knowledge Graph Visualization", font=dict(size=16)),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[
            dict(
                text="Hover over nodes for details",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='#888', size=12)
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600
    )
    
    return fig

def render_phase_comparison():
    """Render phase comparison interface"""
    st.header("⚡ Phase Comparison")
    
    if len(st.session_state.processing_history) < 2:
        st.info("💡 Process the same document with different phases to compare performance")
        return
    
    # Group results by filename and phase
    results_by_file = {}
    for result in st.session_state.processing_history:
        if result.filename not in results_by_file:
            results_by_file[result.filename] = []
        results_by_file[result.filename].append(result)
    
    # Show comparison for files processed with multiple phases
    for filename, results in results_by_file.items():
        if len(results) > 1:
            st.subheader(f"📄 {filename}")
            
            # Create comparison chart
            phases = [r.phase_used for r in results]
            entities = [r.entities_found for r in results]
            relationships = [r.relationships_found for r in results]
            times = [r.processing_time for r in results]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Entities/Relationships comparison
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(name='Entities', x=phases, y=entities))
                fig1.add_trace(go.Bar(name='Relationships', x=phases, y=relationships))
                fig1.update_layout(
                    title="Entities & Relationships Found",
                    barmode='group',
                    height=300
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Processing time comparison
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(name='Processing Time (s)', x=phases, y=times))
                fig2.update_layout(
                    title="Processing Time",
                    height=300
                )
                st.plotly_chart(fig2, use_container_width=True)

def clear_all_data():
    """Clear all session data"""
    st.session_state.uploaded_documents = []
    st.session_state.test_results = []
    st.session_state.current_graph = None
    st.session_state.processing_history = []
    st.session_state.query_results = []
    st.success("All data cleared!")
    st.rerun()

def render_export_tools():
    """Render data export tools"""
    st.header("📤 Export & Integration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_data = {
            "processing_history": [asdict(r) for r in st.session_state.processing_history],
            "export_timestamp": datetime.now().isoformat()
        }
        
        st.download_button(
            label="📄 Download Results JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"graphrag_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        if st.session_state.current_graph:
            st.download_button(
                label="🐍 Download Graph JSON",
                data=json.dumps(st.session_state.current_graph, indent=2),
                file_name=f"graph_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("No graph data to export")
    
    with col3:
        analytics_data = generate_analytics_report()
        st.download_button(
            label="📊 Download Analytics CSV",
            data=analytics_data,
            file_name=f"graphrag_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def generate_analytics_report() -> str:
    """Generate analytics report as CSV"""
    data = []
    for result in st.session_state.processing_history:
        data.append({
            "filename": result.filename,
            "phase": result.phase_used,
            "entities_found": result.entities_found,
            "relationships_found": result.relationships_found,
            "processing_time": result.processing_time,
            "timestamp": getattr(result, 'timestamp', datetime.now().isoformat())
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

# Main application
def main():
    """Main application entry point"""
    init_session_state()
    
    # Header
    render_header()
    
    # System status sidebar
    test_phase, enable_visualization, max_entities = render_system_status()
    
    # Main content tabs - disable non-functional ones
    if st.session_state.processing_history:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Document Processing",
            "🕸️ Graph Visualization",
            "⚡ Phase Comparison", 
            "📤 Export & Tools"
        ])
        
        with tab1:
            render_document_upload()
        
        with tab2:
            if enable_visualization:
                render_graph_visualization()
            else:
                st.info("Graph visualization disabled in settings")
        
        with tab3:
            render_phase_comparison()
        
        with tab4:
            render_export_tools()
    else:
        # Only show document processing until something is processed
        st.subheader("👆 Upload and process documents to unlock all features")
        render_document_upload()
    
    # Footer
    st.markdown("---")
    st.markdown("🔬 **Super-Digimon GraphRAG Testing Interface** | Test all phases with your own data")

if __name__ == "__main__":
    main()