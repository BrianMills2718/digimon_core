# Phase D.4: Visualization Dashboard - Web UI for Viewing Results and Graphs

## Overview

**Phase**: D.4 - Production Optimization  
**Focus**: Interactive Visualization Dashboard  
**Timeline**: 4-6 days  
**Priority**: Medium  
**Prerequisites**: D.3 (Multi-document batch processing)

## Mission Statement

Build an interactive web-based visualization dashboard that provides comprehensive views of graph analysis results, batch processing status, research insights, and cross-modal analysis outputs for research group access.

## Current State Assessment

### Existing UI Infrastructure ✅
- **GraphRAGUI** (`src/ui/graphrag_ui.py`) - Main UI interface with session management
- **UIPhaseManager** (`src/ui/ui_phase_adapter.py`) - Phase management and execution  
- **Streamlit Integration** - UI framework with file upload and progress tracking
- **Phase Integration** - Integration with all processing phases
- **Result Structures** - UIProcessingResult with visualization data support

### Existing Visualization Components ✅
- **Graph Visualization** (`src/tools/phase2/t54_graph_visualization_unified.py`) - Plotly-based graph rendering
- **Interactive Visualizer** (`src/tools/phase2/interactive_graph_visualizer.py`) - Interactive graph exploration
- **Monitoring Dashboards** (`src/monitoring/dashboards/`) - Grafana dashboard configurations

## Enhancement Objectives

### 1. **Real-Time Graph Explorer**
- **Interactive Graph Viewer**: Navigate large knowledge graphs with zoom, pan, filter capabilities
- **Multi-Level Views**: Entity-level, relationship-level, and community-level visualizations
- **Dynamic Filtering**: Filter by entity types, confidence scores, temporal ranges

### 2. **Batch Processing Monitor**
- **Live Processing Status**: Real-time view of batch processing progress
- **Resource Utilization**: Memory, CPU, and processing queue visualizations  
- **Error Tracking**: Interactive error logs with remediation suggestions

### 3. **Research Analytics Dashboard**
- **Citation Network Visualization**: Interactive citation networks with impact metrics
- **Cross-Document Entity Clusters**: Visualize entity resolution results across documents
- **Temporal Analysis Views**: Timeline visualizations of concept evolution

### 4. **Cross-Modal Analysis Explorer**
- **Graph-Table-Vector Views**: Side-by-side views of data in different formats
- **Conversion Tracking**: Visualize data transformation pipelines
- **Quality Metrics**: Visual quality assessment of cross-modal conversions

## Implementation Plan

### Task D.4.1: Enhanced Web Dashboard Framework

**Deliverable**: Robust web framework with real-time capabilities

**Implementation Details**:
```python
# src/ui/enhanced_dashboard.py
import streamlit as st
import asyncio
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import pandas as pd
from datetime import datetime, timedelta

@dataclass
class DashboardConfig:
    """Configuration for dashboard components"""
    enable_real_time: bool = True
    refresh_interval: int = 5  # seconds
    max_graph_nodes: int = 1000
    default_time_range: timedelta = timedelta(hours=24)
    theme: str = "dark"  # "dark" or "light"

class EnhancedDashboard:
    """Enhanced visualization dashboard with real-time capabilities"""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        self.graphrag_ui = GraphRAGUI()
        self.batch_monitor = BatchProcessingMonitor()
        self.graph_explorer = InteractiveGraphExplorer()
        self.research_analytics = ResearchAnalyticsDashboard()
        
        # Session state management
        if 'dashboard_state' not in st.session_state:
            st.session_state.dashboard_state = {
                'current_view': 'overview',
                'selected_batch': None,
                'graph_filters': {},
                'time_range': self.config.default_time_range
            }
    
    def render_main_dashboard(self):
        """Render the main dashboard interface"""
        st.set_page_config(
            page_title="KGAS Research Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main header
        self._render_header()
        
        # Sidebar navigation
        view = self._render_sidebar()
        
        # Main content area
        if view == "overview":
            self._render_overview_page()
        elif view == "graph_explorer":
            self._render_graph_explorer_page()
        elif view == "batch_monitor":
            self._render_batch_monitor_page()
        elif view == "research_analytics":
            self._render_research_analytics_page()
        elif view == "cross_modal":
            self._render_cross_modal_page()
        elif view == "system_status":
            self._render_system_status_page()
    
    def _render_header(self):
        """Render dashboard header with system status"""
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.title("🧠 KGAS Research Dashboard")
            st.caption("Knowledge Graph Analysis System - Real-time Visualization")
        
        with col2:
            # System health indicator
            health_status = self.graphrag_ui.get_system_status()
            if health_status.get("healthy", False):
                st.success("🟢 System Healthy")
            else:
                st.error("🔴 System Issues")
        
        with col3:
            # Real-time toggle
            if st.checkbox("Real-time Updates", value=self.config.enable_real_time):
                self.config.enable_real_time = True
                st.empty()  # Placeholder for auto-refresh
    
    def _render_sidebar(self) -> str:
        """Render sidebar navigation"""
        with st.sidebar:
            st.header("📊 Navigation")
            
            view = st.radio(
                "Select View",
                ["overview", "graph_explorer", "batch_monitor", 
                 "research_analytics", "cross_modal", "system_status"],
                format_func=lambda x: {
                    "overview": "🏠 Overview",
                    "graph_explorer": "🕸️ Graph Explorer", 
                    "batch_monitor": "⚡ Batch Monitor",
                    "research_analytics": "📚 Research Analytics",
                    "cross_modal": "🔄 Cross-Modal Analysis",
                    "system_status": "💻 System Status"
                }.get(x, x)
            )
            
            st.session_state.dashboard_state['current_view'] = view
            
            # Time range selector
            st.subheader("⏰ Time Range")
            time_options = {
                "Last Hour": timedelta(hours=1),
                "Last 6 Hours": timedelta(hours=6),
                "Last 24 Hours": timedelta(hours=24),
                "Last Week": timedelta(days=7),
                "Last Month": timedelta(days=30)
            }
            
            selected_time = st.selectbox(
                "Select Range",
                list(time_options.keys()),
                index=2  # Default to 24 hours
            )
            st.session_state.dashboard_state['time_range'] = time_options[selected_time]
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            if st.button("📥 Upload Document"):
                self._show_upload_dialog()
            
            if st.button("📊 Generate Report"):
                self._generate_dashboard_report()
        
        return view
    
    def _render_overview_page(self):
        """Render overview dashboard page"""
        st.header("📊 System Overview")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Total documents processed
            total_docs = self._get_total_documents_processed()
            st.metric("📄 Documents Processed", total_docs, delta=None)
        
        with col2:
            # Total entities extracted
            total_entities = self._get_total_entities()
            st.metric("🏷️ Entities Extracted", total_entities, delta=None)
        
        with col3:
            # Active batch jobs
            active_batches = self._get_active_batch_count()
            st.metric("⚡ Active Batches", active_batches, delta=None)
        
        with col4:
            # System uptime
            uptime = self._get_system_uptime()
            st.metric("⏱️ System Uptime", uptime, delta=None)
        
        # Recent activity timeline
        st.subheader("📈 Recent Activity")
        recent_activity = self._get_recent_activity()
        self._render_activity_timeline(recent_activity)
        
        # System performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💾 Memory Usage")
            memory_data = self._get_memory_usage_data()
            self._render_memory_usage_chart(memory_data)
        
        with col2:
            st.subheader("⚡ Processing Performance")
            performance_data = self._get_performance_data()
            self._render_performance_chart(performance_data)
```

### Task D.4.2: Interactive Graph Explorer

**Deliverable**: Advanced graph visualization with exploration capabilities

**Implementation Details**:
```python
# src/ui/interactive_graph_explorer.py
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, Any, List, Tuple, Optional

class InteractiveGraphExplorer:
    """Interactive graph exploration interface"""
    
    def __init__(self):
        self.current_graph = None
        self.layout_cache = {}
        self.filter_state = {
            'entity_types': [],
            'confidence_threshold': 0.0,
            'relationship_types': [],
            'communities': []
        }
    
    def render_graph_explorer(self):
        """Render the main graph explorer interface"""
        st.header("🕸️ Interactive Graph Explorer")
        
        # Graph selection and loading
        col1, col2 = st.columns([2, 1])
        
        with col1:
            graph_source = st.selectbox(
                "Select Graph Source",
                ["Recent Processing", "Saved Graphs", "Upload Graph"]
            )
            
            if graph_source == "Recent Processing":
                self._load_recent_graph()
            elif graph_source == "Saved Graphs":
                self._load_saved_graph()
            else:
                self._upload_graph()
        
        with col2:
            # Graph statistics
            if self.current_graph:
                self._render_graph_statistics()
        
        if self.current_graph:
            # Filter controls
            self._render_filter_controls()
            
            # Main graph visualization
            self._render_interactive_graph()
            
            # Node/edge details panel
            self._render_details_panel()
    
    def _render_filter_controls(self):
        """Render graph filtering controls"""
        st.subheader("🔍 Graph Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Entity type filter
            entity_types = self._get_entity_types()
            selected_types = st.multiselect(
                "Entity Types",
                entity_types,
                default=entity_types[:5] if len(entity_types) > 5 else entity_types
            )
            self.filter_state['entity_types'] = selected_types
        
        with col2:
            # Confidence threshold
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
            self.filter_state['confidence_threshold'] = confidence_threshold
        
        with col3:
            # Relationship types
            relationship_types = self._get_relationship_types()
            selected_rels = st.multiselect(
                "Relationship Types",
                relationship_types,
                default=relationship_types[:3] if len(relationship_types) > 3 else relationship_types
            )
            self.filter_state['relationship_types'] = selected_rels
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Community filter
                communities = self._get_communities()
                selected_communities = st.multiselect(
                    "Communities",
                    communities,
                    default=[]
                )
                self.filter_state['communities'] = selected_communities
            
            with col2:
                # Node degree filter
                min_degree = st.number_input("Minimum Node Degree", min_value=0, value=0)
                max_degree = st.number_input("Maximum Node Degree", min_value=1, value=100)
                self.filter_state['degree_range'] = (min_degree, max_degree)
    
    def _render_interactive_graph(self):
        """Render the main interactive graph visualization"""
        st.subheader("🌐 Graph Visualization")
        
        # Layout options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            layout_type = st.selectbox(
                "Layout Algorithm",
                ["force_directed", "circular", "hierarchical", "community_based"]
            )
        
        with col2:
            node_size_metric = st.selectbox(
                "Node Size by",
                ["degree", "betweenness", "closeness", "pagerank"]
            )
        
        with col3:
            edge_width_metric = st.selectbox(
                "Edge Width by",
                ["weight", "confidence", "uniform"]
            )
        
        # Apply filters and generate visualization
        filtered_graph = self._apply_filters(self.current_graph)
        fig = self._create_graph_visualization(
            filtered_graph, layout_type, node_size_metric, edge_width_metric
        )
        
        # Display graph with interaction callbacks
        selected_node = st.plotly_chart(
            fig, 
            use_container_width=True,
            on_select="rerun",
            selection_mode="points"
        )
        
        # Handle node selection
        if selected_node:
            self._handle_node_selection(selected_node)
    
    def _create_graph_visualization(self, graph: nx.Graph, 
                                   layout_type: str,
                                   node_size_metric: str,
                                   edge_width_metric: str) -> go.Figure:
        """Create interactive graph visualization"""
        
        # Calculate layout
        pos = self._calculate_layout(graph, layout_type)
        
        # Calculate node sizes
        node_sizes = self._calculate_node_sizes(graph, node_size_metric)
        
        # Calculate edge widths
        edge_widths = self._calculate_edge_widths(graph, edge_width_metric)
        
        # Create edge traces
        edge_traces = []
        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    width=edge_widths.get(edge, 1),
                    color='rgba(125, 125, 125, 0.5)'
                ),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = [pos[node][0] for node in graph.nodes()]
        node_y = [pos[node][1] for node in graph.nodes()]
        node_colors = [self._get_node_color(graph, node) for node in graph.nodes()]
        node_text = [self._get_node_hover_text(graph, node) for node in graph.nodes()]
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=[node_sizes.get(node, 10) for node in graph.nodes()],
                color=node_colors,
                line=dict(width=2, color='white'),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Node Metric")
            ),
            text=[self._get_node_label(graph, node) for node in graph.nodes()],
            textposition="middle center",
            hovertext=node_text,
            hoverinfo='text',
            name="Entities"
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title="Knowledge Graph Visualization",
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="Interactive Graph Explorer - Click nodes for details",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(size=12, color="gray")
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
```

### Task D.4.3: Real-Time Batch Processing Monitor

**Deliverable**: Live monitoring dashboard for batch processing operations

**Implementation Details**:
```python
# src/ui/batch_processing_monitor.py
import streamlit as st
import time
import asyncio
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

class BatchProcessingMonitor:
    """Real-time batch processing monitoring dashboard"""
    
    def __init__(self):
        self.batch_scheduler = None  # Will be injected
        self.refresh_interval = 5  # seconds
        
    def render_batch_monitor(self):
        """Render the batch processing monitor dashboard"""
        st.header("⚡ Batch Processing Monitor")
        
        # Auto-refresh mechanism
        placeholder = st.empty()
        
        with placeholder.container():
            # Current batch status overview
            self._render_batch_overview()
            
            # Active batches table
            self._render_active_batches()
            
            # Resource utilization
            col1, col2 = st.columns(2)
            with col1:
                self._render_resource_utilization()
            with col2:
                self._render_processing_queue()
            
            # Error tracking
            self._render_error_tracking()
            
            # Historical performance
            self._render_historical_performance()
        
        # Auto-refresh
        if st.session_state.get('batch_monitor_auto_refresh', False):
            time.sleep(self.refresh_interval)
            st.rerun()
    
    def _render_batch_overview(self):
        """Render batch processing overview metrics"""
        st.subheader("📊 Batch Status Overview")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Get current batch statistics
        stats = self._get_batch_statistics()
        
        with col1:
            st.metric(
                "🔄 Active Batches",
                stats.get('active_batches', 0),
                delta=stats.get('active_delta', 0)
            )
        
        with col2:
            st.metric(
                "⏳ Queued Jobs",
                stats.get('queued_jobs', 0),
                delta=stats.get('queued_delta', 0)
            )
        
        with col3:
            st.metric(
                "✅ Completed Today",
                stats.get('completed_today', 0),
                delta=stats.get('completed_delta', 0)
            )
        
        with col4:
            st.metric(
                "❌ Failed Jobs",
                stats.get('failed_jobs', 0),
                delta=stats.get('failed_delta', 0)
            )
        
        with col5:
            avg_time = stats.get('avg_processing_time', 0)
            st.metric(
                "⏱️ Avg Time (min)",
                f"{avg_time:.1f}",
                delta=f"{stats.get('time_delta', 0):.1f}"
            )
    
    def _render_active_batches(self):
        """Render table of currently active batches"""
        st.subheader("🚀 Active Batches")
        
        active_batches = self._get_active_batches()
        
        if not active_batches:
            st.info("No active batches currently running")
            return
        
        # Create DataFrame for display
        df = pd.DataFrame(active_batches)
        
        # Add progress bars
        for idx, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
            
            with col1:
                st.write(f"**{row['batch_id']}**")
                st.write(f"📄 {row['total_documents']} documents")
            
            with col2:
                st.write(f"⏱️ {row['elapsed_time']}")
                st.write(f"🔧 {row['priority']}")
            
            with col3:
                progress = row['completed'] / row['total_documents']
                st.progress(progress)
                st.write(f"{row['completed']}/{row['total_documents']} complete")
            
            with col4:
                status_color = {
                    'running': '🟢',
                    'paused': '🟡', 
                    'error': '🔴'
                }.get(row['status'], '⚪')
                st.write(f"{status_color} {row['status']}")
                
                if st.button(f"View Details", key=f"details_{idx}"):
                    self._show_batch_details(row['batch_id'])
    
    def _render_resource_utilization(self):
        """Render resource utilization charts"""
        st.subheader("💻 Resource Utilization")
        
        # Get resource data
        resource_data = self._get_resource_utilization()
        
        # CPU utilization gauge
        cpu_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = resource_data['cpu_percent'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CPU Usage (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        cpu_fig.update_layout(height=300)
        st.plotly_chart(cpu_fig, use_container_width=True)
        
        # Memory utilization
        memory_data = resource_data['memory']
        memory_fig = go.Figure()
        memory_fig.add_trace(go.Bar(
            x=['Used', 'Available'],
            y=[memory_data['used_gb'], memory_data['available_gb']],
            marker_color=['red', 'green']
        ))
        memory_fig.update_layout(
            title="Memory Usage (GB)",
            height=300,
            yaxis_title="GB"
        )
        st.plotly_chart(memory_fig, use_container_width=True)
    
    def _render_processing_queue(self):
        """Render processing queue visualization"""
        st.subheader("📋 Processing Queue")
        
        queue_data = self._get_queue_status()
        
        # Queue status pie chart
        queue_fig = go.Figure(data=[go.Pie(
            labels=['Pending', 'Processing', 'Completed', 'Failed'],
            values=[
                queue_data['pending'],
                queue_data['processing'], 
                queue_data['completed'],
                queue_data['failed']
            ],
            hole=0.4
        )])
        queue_fig.update_layout(
            title="Queue Status Distribution",
            height=300
        )
        st.plotly_chart(queue_fig, use_container_width=True)
        
        # Processing rate over time
        rate_data = self._get_processing_rate_data()
        rate_fig = go.Figure()
        rate_fig.add_trace(go.Scatter(
            x=rate_data['timestamps'],
            y=rate_data['documents_per_minute'],
            mode='lines+markers',
            name='Processing Rate'
        ))
        rate_fig.update_layout(
            title="Processing Rate (docs/min)",
            height=200,
            xaxis_title="Time",
            yaxis_title="Documents/min"
        )
        st.plotly_chart(rate_fig, use_container_width=True)
```

### Task D.4.4: Research Analytics Dashboard

**Deliverable**: Comprehensive research workflow visualization

**Implementation Details**:
```python
# src/ui/research_analytics_dashboard.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from typing import Dict, Any, List

class ResearchAnalyticsDashboard:
    """Research-focused analytics and visualization dashboard"""
    
    def render_research_analytics(self):
        """Render the research analytics dashboard"""
        st.header("📚 Research Analytics Dashboard")
        
        # Research overview metrics
        self._render_research_overview()
        
        # Citation network analysis
        self._render_citation_network()
        
        # Cross-document entity analysis
        self._render_entity_clustering()
        
        # Temporal concept evolution
        self._render_temporal_analysis()
        
        # Research domain insights
        self._render_domain_insights()
    
    def _render_research_overview(self):
        """Render research overview metrics"""
        st.subheader("📊 Research Collection Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        research_stats = self._get_research_statistics()
        
        with col1:
            st.metric(
                "📄 Total Papers", 
                research_stats.get('total_papers', 0)
            )
        
        with col2:
            st.metric(
                "👥 Unique Authors",
                research_stats.get('unique_authors', 0)
            )
        
        with col3:
            st.metric(
                "🔗 Citation Links",
                research_stats.get('citation_links', 0)
            )
        
        with col4:
            st.metric(
                "🏷️ Research Domains",
                research_stats.get('research_domains', 0)
            )
    
    def _render_citation_network(self):
        """Render interactive citation network"""
        st.subheader("🔗 Citation Network Analysis")
        
        # Citation network controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_citations = st.slider("Minimum Citations", 0, 20, 1)
        
        with col2:
            max_nodes = st.slider("Maximum Nodes", 50, 500, 100)
        
        with col3:
            layout_algorithm = st.selectbox(
                "Layout", 
                ["spring", "circular", "shell", "kamada_kawai"]
            )
        
        # Generate citation network
        citation_graph = self._build_citation_network(min_citations, max_nodes)
        citation_fig = self._create_citation_network_viz(citation_graph, layout_algorithm)
        
        st.plotly_chart(citation_fig, use_container_width=True)
        
        # Citation metrics table
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Most Cited Papers")
            most_cited = self._get_most_cited_papers()
            st.dataframe(most_cited, use_container_width=True)
        
        with col2:
            st.subheader("🌟 Influential Authors")
            influential_authors = self._get_influential_authors()
            st.dataframe(influential_authors, use_container_width=True)
    
    def _render_entity_clustering(self):
        """Render cross-document entity clustering results"""
        st.subheader("🏷️ Cross-Document Entity Clusters")
        
        # Entity clustering controls
        col1, col2 = st.columns(2)
        
        with col1:
            entity_type = st.selectbox(
                "Entity Type",
                ["PERSON", "ORG", "GPE", "TECHNOLOGY", "CONCEPT"]
            )
        
        with col2:
            confidence_threshold = st.slider(
                "Confidence Threshold", 
                0.0, 1.0, 0.7, 0.1
            )
        
        # Get entity clusters
        entity_clusters = self._get_entity_clusters(entity_type, confidence_threshold)
        
        # Render cluster visualization
        if entity_clusters:
            cluster_fig = self._create_entity_cluster_viz(entity_clusters)
            st.plotly_chart(cluster_fig, use_container_width=True)
            
            # Entity cluster details
            selected_cluster = st.selectbox(
                "Select Cluster for Details",
                [cluster['cluster_id'] for cluster in entity_clusters]
            )
            
            if selected_cluster:
                self._show_cluster_details(selected_cluster, entity_clusters)
        else:
            st.info("No entity clusters found for the selected criteria")
    
    def _render_temporal_analysis(self):
        """Render temporal concept evolution analysis"""
        st.subheader("⏰ Temporal Concept Evolution")
        
        # Temporal analysis controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            concept = st.text_input("Concept to Track", "artificial intelligence")
        
        with col2:
            time_granularity = st.selectbox(
                "Time Granularity",
                ["yearly", "monthly", "quarterly"]
            )
        
        with col3:
            show_trends = st.checkbox("Show Trend Lines", True)
        
        if concept:
            # Get temporal data
            temporal_data = self._get_temporal_concept_data(concept, time_granularity)
            
            if temporal_data:
                # Create temporal evolution chart
                temporal_fig = self._create_temporal_evolution_chart(
                    temporal_data, concept, show_trends
                )
                st.plotly_chart(temporal_fig, use_container_width=True)
                
                # Concept milestones
                st.subheader(f"🎯 Key Milestones for '{concept}'")
                milestones = self._get_concept_milestones(concept)
                
                for milestone in milestones:
                    with st.expander(f"📅 {milestone['date']} - {milestone['title']}"):
                        st.write(milestone['description'])
                        st.write(f"**Impact Score**: {milestone['impact_score']:.2f}")
                        st.write(f"**Source**: {milestone['source_document']}")
            else:
                st.info(f"No temporal data found for concept: {concept}")
    
    def _render_domain_insights(self):
        """Render research domain insights"""
        st.subheader("🔬 Research Domain Insights")
        
        # Domain distribution
        col1, col2 = st.columns(2)
        
        with col1:
            domain_distribution = self._get_domain_distribution()
            domain_fig = go.Figure(data=[go.Pie(
                labels=list(domain_distribution.keys()),
                values=list(domain_distribution.values()),
                hole=0.4
            )])
            domain_fig.update_layout(title="Research Domain Distribution")
            st.plotly_chart(domain_fig, use_container_width=True)
        
        with col2:
            # Domain evolution over time
            domain_evolution = self._get_domain_evolution()
            evolution_fig = px.line(
                domain_evolution, 
                x='year', 
                y='paper_count', 
                color='domain',
                title="Domain Evolution Over Time"
            )
            st.plotly_chart(evolution_fig, use_container_width=True)
        
        # Interdisciplinary connections
        st.subheader("🔗 Interdisciplinary Connections")
        interdisciplinary_data = self._get_interdisciplinary_connections()
        
        if interdisciplinary_data:
            interdisciplinary_fig = self._create_interdisciplinary_network(interdisciplinary_data)
            st.plotly_chart(interdisciplinary_fig, use_container_width=True)
        
        # Emerging research themes
        st.subheader("🌱 Emerging Research Themes")
        emerging_themes = self._get_emerging_themes()
        
        for theme in emerging_themes:
            with st.expander(f"📈 {theme['theme_name']} (Growth: +{theme['growth_rate']:.1%})"):
                st.write(f"**Description**: {theme['description']}")
                st.write(f"**Key Papers**: {theme['paper_count']}")
                st.write(f"**Key Researchers**: {', '.join(theme['key_researchers'][:3])}")
                
                # Theme evolution mini-chart
                theme_data = theme['evolution_data']
                theme_fig = px.line(
                    x=theme_data['years'],
                    y=theme_data['mentions'],
                    title=f"{theme['theme_name']} Mentions Over Time"
                )
                st.plotly_chart(theme_fig, use_container_width=True)
```

## Success Criteria

Phase D.4 is complete when:

1. **✅ Real-Time Dashboard**: Interactive web dashboard with live updates and system monitoring
2. **✅ Graph Explorer**: Advanced graph visualization with filtering, zooming, and exploration capabilities  
3. **✅ Batch Monitor**: Live batch processing status with resource utilization and error tracking
4. **✅ Research Analytics**: Citation networks, entity clustering, and temporal analysis visualizations
5. **✅ Cross-Modal Views**: Side-by-side visualization of data in different formats
6. **✅ Performance Validation**: Dashboard performance and usability testing with evidence

## Evidence Requirements

Create `Evidence_Phase_D4_Visualization_Dashboard.md` with:

### 1. Dashboard Functionality
- Interactive feature demonstrations (screenshots/videos)
- Real-time update validation
- Multi-user access testing
- Performance metrics under load

### 2. Graph Visualization Capabilities  
- Large graph rendering performance (>1000 nodes)
- Interactive exploration workflows
- Filter and search functionality validation
- Layout algorithm comparisons

### 3. Batch Monitoring Accuracy
- Real-time status accuracy validation
- Resource utilization monitoring
- Error tracking and notification testing
- Historical data accuracy

### 4. Research Analytics Value
- Citation network analysis results
- Cross-document entity resolution visualization
- Temporal analysis insights
- Research domain clustering validation

## Integration Points

### Dependencies
- **Phase D.3**: Multi-document batch processing provides data for monitoring
- **Existing UI Infrastructure**: Builds on GraphRAGUI and UIPhaseManager
- **Graph Visualization Tools**: Leverages existing Plotly-based visualization components

### Provides Foundation For
- **Phase D.5**: Research workflow improvements benefit from visualization insights
- **Phase D.6**: Web deployment strategy includes dashboard deployment
- **Future Phases**: Advanced analytics and reporting capabilities

## Implementation Timeline

**Day 1**: Enhanced web dashboard framework with real-time capabilities  
**Day 2**: Interactive graph explorer with advanced filtering  
**Day 3**: Real-time batch processing monitor  
**Day 4**: Research analytics dashboard with citation networks  
**Day 5**: Cross-modal analysis explorer  
**Day 6**: Integration testing, performance optimization, and evidence collection

---

**Status**: Ready for Implementation  
**Next Phase**: D.5 - Research Workflow Improvements  
**Owner**: Development Team  
**Review Date**: Upon completion of implementation