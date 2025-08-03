#!/usr/bin/env python3
"""
Interactive Graph Explorer - Phase D.4 Implementation

Interactive graph exploration interface with filtering, search, and analysis capabilities.
"""

import streamlit as st
try:
    import networkx as nx
except AttributeError:
    # Handle networkx version issues
    import sys
    import importlib
    if 'networkx' in sys.modules:
        del sys.modules['networkx']
    import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Tuple, Optional, Set
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class InteractiveGraphExplorer:
    """
    Interactive graph exploration interface.
    
    Features:
    - Real-time graph visualization
    - Node and edge filtering
    - Community detection
    - Path finding
    - Graph analytics
    """
    
    def __init__(self):
        self.current_graph = None
        self.layout_cache = {}
        self.filter_state = {
            'entity_types': [],
            'confidence_threshold': 0.0,
            'relationship_types': [],
            'communities': []
        }
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize session state
        if 'graph_explorer_state' not in st.session_state:
            st.session_state.graph_explorer_state = {
                'selected_node': None,
                'selected_edge': None,
                'graph_layout': 'spring',
                'show_labels': True,
                'node_size_metric': 'degree'
            }
    
    def render_graph_explorer(self):
        """Render the main graph explorer interface"""
        st.header("🕸️ Interactive Graph Explorer")
        
        # Graph selection and loading
        col1, col2 = st.columns([2, 1])
        
        with col1:
            graph_source = st.selectbox(
                "Select Graph Source",
                ["Recent Processing", "Saved Graphs", "Upload Graph", "Sample Data"]
            )
            
            if graph_source == "Recent Processing":
                self._load_recent_graph()
            elif graph_source == "Saved Graphs":
                self._load_saved_graph()
            elif graph_source == "Upload Graph":
                self._upload_graph()
            else:
                self._load_sample_graph()
        
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
            
            # Graph analysis tools
            self._render_analysis_tools()
    
    def _load_sample_graph(self):
        """Load a sample graph for demonstration"""
        # Create sample graph
        G = nx.karate_club_graph()
        
        # Add node attributes
        for node in G.nodes():
            G.nodes[node]['entity_type'] = np.random.choice(['PERSON', 'ORG', 'GPE'])
            G.nodes[node]['confidence'] = np.random.uniform(0.6, 1.0)
            G.nodes[node]['label'] = f"Entity_{node}"
        
        # Add edge attributes
        for edge in G.edges():
            G.edges[edge]['relationship_type'] = np.random.choice(['KNOWS', 'WORKS_WITH', 'LOCATED_IN'])
            G.edges[edge]['weight'] = np.random.uniform(0.5, 1.0)
        
        self.current_graph = G
        st.success(f"Loaded sample graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    def _load_recent_graph(self):
        """Load graph from recent processing"""
        # Placeholder - would load from actual processing results
        st.info("Loading graph from recent processing...")
        self._load_sample_graph()
    
    def _load_saved_graph(self):
        """Load a saved graph"""
        saved_graphs = ["Analysis_2024_01_15", "Research_Graph_v2", "Entity_Network_Final"]
        
        selected_graph = st.selectbox("Select saved graph", saved_graphs)
        
        if st.button("Load Graph"):
            st.info(f"Loading {selected_graph}...")
            # Placeholder - would load actual saved graph
            self._load_sample_graph()
    
    def _upload_graph(self):
        """Upload a graph file"""
        uploaded_file = st.file_uploader(
            "Choose a graph file",
            type=['json', 'gexf', 'graphml']
        )
        
        if uploaded_file is not None:
            try:
                # Parse uploaded file
                if uploaded_file.type == "application/json":
                    data = json.load(uploaded_file)
                    # Convert JSON to NetworkX graph
                    G = nx.node_link_graph(data)
                else:
                    st.error("Unsupported file format")
                    return
                
                self.current_graph = G
                st.success(f"Loaded graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
                
            except Exception as e:
                st.error(f"Error loading graph: {e}")
    
    def _render_graph_statistics(self):
        """Render graph statistics"""
        G = self.current_graph
        
        st.markdown("### Graph Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Nodes", len(G.nodes))
            st.metric("Edges", len(G.edges))
            
        with col2:
            st.metric("Density", f"{nx.density(G):.3f}")
            if nx.is_connected(G):
                st.metric("Diameter", nx.diameter(G))
            else:
                st.metric("Components", nx.number_connected_components(G))
    
    def _render_filter_controls(self):
        """Render graph filtering controls"""
        st.markdown("### Filters")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Entity type filter
            all_types = set()
            for node, data in self.current_graph.nodes(data=True):
                if 'entity_type' in data:
                    all_types.add(data['entity_type'])
            
            self.filter_state['entity_types'] = st.multiselect(
                "Entity Types",
                list(all_types),
                default=list(all_types)
            )
        
        with col2:
            # Confidence threshold
            self.filter_state['confidence_threshold'] = st.slider(
                "Min Confidence",
                0.0, 1.0, 0.0, 0.05
            )
        
        with col3:
            # Relationship type filter
            all_rel_types = set()
            for u, v, data in self.current_graph.edges(data=True):
                if 'relationship_type' in data:
                    all_rel_types.add(data['relationship_type'])
            
            self.filter_state['relationship_types'] = st.multiselect(
                "Relationship Types",
                list(all_rel_types),
                default=list(all_rel_types)
            )
        
        with col4:
            # Layout selection
            st.session_state.graph_explorer_state['graph_layout'] = st.selectbox(
                "Layout",
                ["spring", "circular", "kamada_kawai", "spectral"],
                index=0
            )
    
    def _render_interactive_graph(self):
        """Render the main interactive graph visualization"""
        G = self._apply_filters()
        
        if len(G.nodes) == 0:
            st.warning("No nodes match the current filters")
            return
        
        # Get layout
        layout_type = st.session_state.graph_explorer_state['graph_layout']
        pos = self._get_graph_layout(G, layout_type)
        
        # Create Plotly figure
        fig = self._create_plotly_graph(G, pos)
        
        # Render the graph
        st.plotly_chart(fig, use_container_width=True)
    
    def _apply_filters(self) -> nx.Graph:
        """Apply filters to the current graph"""
        G = self.current_graph.copy()
        
        # Filter nodes by entity type and confidence
        nodes_to_remove = []
        for node, data in G.nodes(data=True):
            # Entity type filter
            if (self.filter_state['entity_types'] and 
                data.get('entity_type') not in self.filter_state['entity_types']):
                nodes_to_remove.append(node)
                continue
            
            # Confidence filter
            if data.get('confidence', 1.0) < self.filter_state['confidence_threshold']:
                nodes_to_remove.append(node)
        
        G.remove_nodes_from(nodes_to_remove)
        
        # Filter edges by relationship type
        if self.filter_state['relationship_types']:
            edges_to_remove = []
            for u, v, data in G.edges(data=True):
                if data.get('relationship_type') not in self.filter_state['relationship_types']:
                    edges_to_remove.append((u, v))
            
            G.remove_edges_from(edges_to_remove)
        
        return G
    
    def _get_graph_layout(self, G: nx.Graph, layout_type: str) -> Dict:
        """Get graph layout positions"""
        # Cache layouts for performance
        cache_key = (id(G), layout_type)
        
        if cache_key in self.layout_cache:
            return self.layout_cache[cache_key]
        
        if layout_type == "spring":
            pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes)), iterations=50)
        elif layout_type == "circular":
            pos = nx.circular_layout(G)
        elif layout_type == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        elif layout_type == "spectral":
            pos = nx.spectral_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        self.layout_cache[cache_key] = pos
        return pos
    
    def _create_plotly_graph(self, G: nx.Graph, pos: Dict) -> go.Figure:
        """Create Plotly figure for graph visualization"""
        # Edge trace
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=1, color='#888'),
                    hoverinfo='none',
                    showlegend=False
                )
            )
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        # Calculate node sizes based on metric
        size_metric = st.session_state.graph_explorer_state['node_size_metric']
        if size_metric == 'degree':
            sizes = dict(G.degree())
        elif size_metric == 'pagerank':
            sizes = nx.pagerank(G)
        else:
            sizes = {node: 10 for node in G.nodes()}
        
        # Normalize sizes
        if sizes:
            min_size = min(sizes.values())
            max_size = max(sizes.values())
            size_range = max_size - min_size if max_size > min_size else 1
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Node info
            node_data = G.nodes[node]
            info = f"Node: {node}<br>"
            info += f"Type: {node_data.get('entity_type', 'Unknown')}<br>"
            info += f"Confidence: {node_data.get('confidence', 0):.2f}<br>"
            info += f"Degree: {G.degree(node)}"
            node_text.append(info)
            
            # Node color by type
            entity_type = node_data.get('entity_type', 'Unknown')
            color_map = {
                'PERSON': '#ff7f0e',
                'ORG': '#2ca02c',
                'GPE': '#d62728',
                'Unknown': '#7f7f7f'
            }
            node_color.append(color_map.get(entity_type, '#7f7f7f'))
            
            # Node size
            if sizes:
                normalized_size = 10 + 20 * (sizes[node] - min_size) / size_range
                node_size.append(normalized_size)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text' if st.session_state.graph_explorer_state['show_labels'] else 'markers',
            text=[G.nodes[node].get('label', str(node)) for node in G.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(width=2, color='white')
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def _render_details_panel(self):
        """Render node/edge details panel"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Node Details")
            
            # Node selection
            node_list = list(self.current_graph.nodes())
            selected_node = st.selectbox(
                "Select Node",
                ["None"] + node_list,
                index=0
            )
            
            if selected_node != "None":
                node_data = self.current_graph.nodes[selected_node]
                
                # Display node properties
                st.json(node_data)
                
                # Node neighbors
                neighbors = list(self.current_graph.neighbors(selected_node))
                st.write(f"**Neighbors ({len(neighbors)}):**")
                st.write(", ".join(map(str, neighbors[:10])))
                if len(neighbors) > 10:
                    st.write(f"... and {len(neighbors) - 10} more")
        
        with col2:
            st.markdown("### Edge Analysis")
            
            if selected_node != "None":
                # Show edges connected to selected node
                edges = list(self.current_graph.edges(selected_node, data=True))
                
                st.write(f"**Connected Edges ({len(edges)}):**")
                
                edge_df = []
                for u, v, data in edges[:10]:
                    edge_df.append({
                        "From": u,
                        "To": v,
                        "Type": data.get('relationship_type', 'Unknown'),
                        "Weight": data.get('weight', 1.0)
                    })
                
                if edge_df:
                    st.dataframe(pd.DataFrame(edge_df))
    
    def _render_analysis_tools(self):
        """Render graph analysis tools"""
        st.markdown("### Graph Analysis")
        
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Community Detection", "Path Finding", "Centrality", "Patterns"]
        )
        
        with tab1:
            self._render_community_detection()
        
        with tab2:
            self._render_path_finding()
        
        with tab3:
            self._render_centrality_analysis()
        
        with tab4:
            self._render_pattern_detection()
    
    def _render_community_detection(self):
        """Render community detection analysis"""
        if st.button("Detect Communities"):
            with st.spinner("Detecting communities..."):
                # Detect communities
                communities = nx.community.greedy_modularity_communities(
                    self.current_graph
                )
                
                st.success(f"Found {len(communities)} communities")
                
                # Display community information
                for i, community in enumerate(communities):
                    with st.expander(f"Community {i+1} ({len(community)} nodes)"):
                        st.write("Nodes:", list(community)[:20])
                        if len(community) > 20:
                            st.write(f"... and {len(community) - 20} more")
    
    def _render_path_finding(self):
        """Render path finding tools"""
        col1, col2 = st.columns(2)
        
        node_list = list(self.current_graph.nodes())
        
        with col1:
            source = st.selectbox("Source Node", node_list)
        
        with col2:
            target = st.selectbox("Target Node", node_list)
        
        if st.button("Find Path"):
            try:
                # Find shortest path
                path = nx.shortest_path(self.current_graph, source, target)
                length = nx.shortest_path_length(self.current_graph, source, target)
                
                st.success(f"Found path of length {length}")
                st.write("Path:", " → ".join(map(str, path)))
                
                # Show all paths if short enough
                if length <= 4:
                    all_paths = list(nx.all_simple_paths(
                        self.current_graph, source, target, cutoff=length+1
                    ))
                    
                    if len(all_paths) > 1:
                        st.write(f"Found {len(all_paths)} paths total")
                        
            except nx.NetworkXNoPath:
                st.error("No path exists between these nodes")
    
    def _render_centrality_analysis(self):
        """Render centrality analysis"""
        centrality_type = st.selectbox(
            "Centrality Measure",
            ["Degree", "Betweenness", "Closeness", "PageRank", "Eigenvector"]
        )
        
        if st.button("Calculate Centrality"):
            with st.spinner(f"Calculating {centrality_type} centrality..."):
                # Calculate centrality
                if centrality_type == "Degree":
                    centrality = nx.degree_centrality(self.current_graph)
                elif centrality_type == "Betweenness":
                    centrality = nx.betweenness_centrality(self.current_graph)
                elif centrality_type == "Closeness":
                    centrality = nx.closeness_centrality(self.current_graph)
                elif centrality_type == "PageRank":
                    centrality = nx.pagerank(self.current_graph)
                else:  # Eigenvector
                    try:
                        centrality = nx.eigenvector_centrality(self.current_graph)
                    except:
                        st.error("Could not compute eigenvector centrality")
                        return
                
                # Display top nodes
                sorted_nodes = sorted(
                    centrality.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                st.write(f"Top 10 nodes by {centrality_type} centrality:")
                
                df = pd.DataFrame(
                    sorted_nodes[:10],
                    columns=["Node", "Centrality"]
                )
                st.dataframe(df)
                
                # Update node sizes
                st.session_state.graph_explorer_state['node_size_metric'] = centrality_type.lower()
                st.experimental_rerun()
    
    def _render_pattern_detection(self):
        """Render pattern detection tools"""
        pattern_type = st.selectbox(
            "Pattern Type",
            ["Triangles", "Cliques", "Motifs", "Cycles"]
        )
        
        if st.button("Find Patterns"):
            with st.spinner(f"Finding {pattern_type}..."):
                if pattern_type == "Triangles":
                    triangles = sum(nx.triangles(self.current_graph).values()) // 3
                    st.write(f"Found {triangles} triangles")
                    
                elif pattern_type == "Cliques":
                    cliques = list(nx.find_cliques(self.current_graph))
                    max_clique = max(cliques, key=len) if cliques else []
                    
                    st.write(f"Found {len(cliques)} maximal cliques")
                    st.write(f"Largest clique size: {len(max_clique)}")
                    if max_clique:
                        st.write("Largest clique nodes:", max_clique)
                
                elif pattern_type == "Cycles":
                    try:
                        cycles = list(nx.simple_cycles(self.current_graph))
                        st.write(f"Found {len(cycles)} simple cycles")
                        
                        if cycles:
                            st.write("Sample cycles (first 5):")
                            for i, cycle in enumerate(cycles[:5]):
                                st.write(f"Cycle {i+1}:", " → ".join(map(str, cycle + [cycle[0]])))
                    except:
                        st.info("Cycle detection requires a directed graph")
                
                else:  # Motifs
                    st.info("Motif detection would be implemented here")


if __name__ == "__main__":
    # Test the graph explorer
    explorer = InteractiveGraphExplorer()
    explorer.render_graph_explorer()