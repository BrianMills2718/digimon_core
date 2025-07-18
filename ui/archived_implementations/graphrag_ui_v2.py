#!/usr/bin/env python3
"""
GraphRAG UI v2.0 - Using Standardized Phase Interface

This version uses the new GraphRAG Phase Interface for consistent,
isolated interaction with all processing phases.
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import uuid

# Add project root to path

# Import UI phase adapter
try:
    from src.ui.ui_phase_adapter import (
        get_ui_phase_manager, get_available_ui_phases, 
        process_document_with_phase, validate_ui_phase_input
    )
    UI_ADAPTER_AVAILABLE = True
except ImportError as e:
    st.error("❌ CRITICAL: UI Phase Adapter not available")
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="GraphRAG UI v2.0",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    if 'current_graph' not in st.session_state:
        st.session_state.current_graph = None
    if 'selected_phase' not in st.session_state:
        st.session_state.selected_phase = None

def render_sidebar():
    """Render the sidebar with phase selection and options"""
    st.sidebar.title("🧠 GraphRAG v2.0")
    st.sidebar.markdown("**Standardized Phase Interface**")
    
    # Get available phases
    manager = get_ui_phase_manager()
    if not manager.is_initialized():
        st.sidebar.error("❌ Phase manager not initialized")
        return None
    
    available_phases = manager.get_available_phases()
    
    # Phase selection
    st.sidebar.subheader("📋 Phase Selection")
    selected_phase = st.sidebar.selectbox(
        "Choose processing phase:",
        available_phases,
        key="phase_selector"
    )
    
    st.session_state.selected_phase = selected_phase
    
    # Show phase information
    if selected_phase:
        st.sidebar.subheader("ℹ️ Phase Information")
        requirements = manager.get_phase_requirements(selected_phase)
        
        st.sidebar.write("**Supported files:**")
        for file_type in requirements.get('supported_files', []):
            st.sidebar.write(f"• {file_type.upper()}")
        
        st.sidebar.write("**Requirements:**")
        if requirements.get('requires_domain'):
            st.sidebar.write("• Domain description required")
        if requirements.get('supports_multiple_queries'):
            st.sidebar.write("• Supports multiple queries")
        else:
            st.sidebar.write("• Single query only")
        
        required_services = requirements.get('required_services', [])
        if required_services:
            st.sidebar.write("**Required services:**")
            for service in required_services:
                st.sidebar.write(f"• {service}")
    
    # Processing options
    st.sidebar.subheader("⚙️ Processing Options")
    
    # Domain description (for Phase 2+)
    domain_description = None
    if selected_phase and manager.get_phase_requirements(selected_phase).get('requires_domain'):
        domain_description = st.sidebar.text_area(
            "Domain Description:",
            placeholder="Describe the domain/topic of your documents...",
            help="Required for ontology-aware processing"
        )
    
    # Queries
    query_input = st.sidebar.text_area(
        "Analysis Queries:",
        value="What are the main entities and relationships in this document?",
        placeholder="Enter queries, one per line",
        help="Questions you want answered about the documents"
    )
    
    queries = [q.strip() for q in query_input.split('\n') if q.strip()]
    
    # Validate input
    validation_errors = []
    if selected_phase and queries:
        validation_errors = validate_ui_phase_input(
            selected_phase, [], queries, domain_description
        )
        # Filter out document-related errors for now
        validation_errors = [err for err in validation_errors if 'Document' not in err]
    
    if validation_errors:
        st.sidebar.error("⚠️ Input Issues:")
        for error in validation_errors:
            st.sidebar.write(f"• {error}")
    
    return {
        'phase': selected_phase,
        'domain_description': domain_description,
        'queries': queries,
        'validation_errors': validation_errors
    }

def render_main_interface(sidebar_config):
    """Render the main interface"""
    st.title("🧠 GraphRAG Testing Interface v2.0")
    st.markdown("**Standardized phase interface for consistent GraphRAG processing**")
    
    # Show selected phase
    if sidebar_config['phase']:
        st.info(f"**Selected Phase:** {sidebar_config['phase']}")
    
    # File upload
    st.subheader("📁 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload documents for analysis:",
        type=['pdf'],  # Start with PDF support
        accept_multiple_files=True,
        help="Upload PDF documents to analyze with GraphRAG"
    )
    
    # Processing controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if uploaded_files and sidebar_config['phase']:
            file_count = len(uploaded_files)
            phase_name = sidebar_config['phase']
            st.write(f"Ready to process {file_count} file(s) with {phase_name}")
    
    with col2:
        if st.button("🚀 Process Documents", type="primary", use_container_width=True):
            if uploaded_files and sidebar_config['phase']:
                if sidebar_config['validation_errors']:
                    st.error("Please fix validation errors in the sidebar before processing")
                else:
                    process_documents_v2(uploaded_files, sidebar_config)
            else:
                st.error("Please upload documents and select a phase")
        
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.processing_history = []
            st.session_state.current_graph = None
            st.rerun()

def process_documents_v2(uploaded_files, config):
    """Process documents using the standardized interface"""
    phase = config['phase']
    domain_description = config['domain_description']
    queries = config['queries']
    
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name} with {phase}...")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Process using standardized interface
            result = process_document_with_phase(
                phase_name=phase,
                file_path=tmp_path,
                filename=uploaded_file.name,
                queries=queries,
                domain_description=domain_description
            )
            
            results.append(result)
            
        except Exception as e:
            st.error(f"❌ Processing failed for {uploaded_file.name}: {str(e)}")
            
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Update session state
    st.session_state.processing_history.extend(results)
    
    status_text.text("✅ Processing complete!")
    
    # Display results
    display_results_v2(results)

def display_results_v2(results):
    """Display processing results"""
    if not results:
        return
    
    st.subheader("📊 Processing Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_entities = sum(r.entity_count for r in results)
    total_relationships = sum(r.relationship_count for r in results)
    avg_confidence = sum(r.confidence_score for r in results) / len(results) if results else 0
    avg_time = sum(r.processing_time for r in results) / len(results) if results else 0
    
    col1.metric("Total Entities", total_entities)
    col2.metric("Total Relationships", total_relationships)
    col3.metric("Avg Confidence", f"{avg_confidence:.2f}")
    col4.metric("Avg Time (s)", f"{avg_time:.2f}")
    
    # Results table
    st.subheader("📋 Detailed Results")
    
    df_data = []
    for result in results:
        df_data.append({
            "Filename": result.filename,
            "Phase": result.phase_name,
            "Status": result.status,
            "Entities": result.entity_count,
            "Relationships": result.relationship_count,
            "Confidence": f"{result.confidence_score:.2f}",
            "Time (s)": f"{result.processing_time:.2f}",
            "Error": result.error_message if result.error_message else "None"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)
    
    # Show errors if any
    error_results = [r for r in results if r.status == "error"]
    if error_results:
        st.subheader("❌ Processing Errors")
        for result in error_results:
            with st.expander(f"Error in {result.filename}"):
                st.error(result.error_message)
    
    # Success details
    success_results = [r for r in results if r.status == "success"]
    if success_results:
        st.subheader("✅ Successful Processing")
        
        for result in success_results:
            with st.expander(f"Details: {result.filename}"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Processing Info:**")
                    st.write(f"• Phase: {result.phase_name}")
                    st.write(f"• Processing time: {result.processing_time:.2f}s")
                    st.write(f"• Entities found: {result.entity_count}")
                    st.write(f"• Relationships found: {result.relationship_count}")
                    st.write(f"• Confidence score: {result.confidence_score:.2f}")
                
                with col2:
                    st.write("**Query Results:**")
                    if result.query_results:
                        for i, query_result in enumerate(result.query_results):
                            st.write(f"**Query {i+1}:** {query_result.get('query', 'N/A')}")
                            st.write(f"Answer: {query_result.get('answer', 'No answer')}")
                    else:
                        st.write("No query results available")
                
                # Phase-specific data
                if result.phase_specific_data:
                    st.write("**Phase-Specific Data:**")
                    st.json(result.phase_specific_data, expanded=False)

def render_processing_history():
    """Render processing history"""
    if not st.session_state.processing_history:
        st.info("No processing history yet. Upload and process some documents!")
        return
    
    st.subheader("📜 Processing History")
    
    # History summary
    history = st.session_state.processing_history
    total_processed = len(history)
    successful = len([r for r in history if r.status == "success"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Documents Processed", total_processed)
    col2.metric("Successful", successful)
    col3.metric("Success Rate", f"{(successful/total_processed*100):.1f}%" if total_processed > 0 else "0%")
    
    # History table
    df_data = []
    for i, result in enumerate(reversed(history)):  # Show newest first
        df_data.append({
            "#": len(history) - i,
            "Filename": result.filename,
            "Phase": result.phase_name,
            "Status": result.status,
            "Entities": result.entity_count,
            "Relationships": result.relationship_count,
            "Time": f"{result.processing_time:.2f}s"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

def main():
    """Main application"""
    initialize_session_state()
    
    # Sidebar
    sidebar_config = render_sidebar()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📊 Processing", "📜 History"])
    
    with tab1:
        render_main_interface(sidebar_config)
    
    with tab2:
        render_processing_history()

if __name__ == "__main__":
    main()