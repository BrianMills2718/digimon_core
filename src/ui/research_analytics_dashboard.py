#!/usr/bin/env python3
"""
Research Analytics Dashboard - Phase D.4 Implementation

Research-focused analytics and visualization dashboard for academic insights.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Handle NetworkX import with version compatibility
try:
    import networkx as nx
except AttributeError:
    # Handle networkx version issues
    import sys
    import importlib
    if 'networkx' in sys.modules:
        del sys.modules['networkx']
    import networkx as nx

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import logging
from collections import Counter, defaultdict
from scipy import stats

logger = logging.getLogger(__name__)


class ResearchAnalyticsDashboard:
    """
    Research-focused analytics and visualization dashboard.
    
    Features:
    - Citation network analysis
    - Cross-document entity analysis
    - Temporal concept evolution
    - Research domain insights
    - Statistical analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize session state
        if 'research_analytics_state' not in st.session_state:
            st.session_state.research_analytics_state = {
                'selected_domain': None,
                'time_window': 'all',
                'min_citations': 5,
                'entity_type_filter': 'all',
                'analysis_depth': 'standard'
            }
    
    def render_research_analytics(self):
        """Render the research analytics dashboard"""
        st.header("📚 Research Analytics Dashboard")
        
        # Control panel
        self._render_control_panel()
        
        # Research overview metrics
        self._render_research_overview()
        
        # Main analysis sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Citation Network",
            "Entity Analysis", 
            "Temporal Evolution",
            "Domain Insights",
            "Statistical Analysis"
        ])
        
        with tab1:
            self._render_citation_network()
        
        with tab2:
            self._render_entity_clustering()
        
        with tab3:
            self._render_temporal_analysis()
        
        with tab4:
            self._render_domain_insights()
        
        with tab5:
            self._render_statistical_analysis()
    
    def _render_control_panel(self):
        """Render analytics control panel"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Domain filter
            domains = self._get_available_domains()
            st.session_state.research_analytics_state['selected_domain'] = st.selectbox(
                "Research Domain",
                ["All Domains"] + domains
            )
        
        with col2:
            # Time window
            st.session_state.research_analytics_state['time_window'] = st.selectbox(
                "Time Window",
                ["All Time", "Last Year", "Last 6 Months", "Last Month"]
            )
        
        with col3:
            # Citation threshold
            st.session_state.research_analytics_state['min_citations'] = st.number_input(
                "Min Citations",
                min_value=0,
                max_value=100,
                value=5,
                step=1
            )
        
        with col4:
            # Analysis depth
            st.session_state.research_analytics_state['analysis_depth'] = st.selectbox(
                "Analysis Depth",
                ["Quick", "Standard", "Deep"]
            )
    
    def _render_research_overview(self):
        """Render research overview metrics"""
        metrics = self._get_research_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Documents",
                f"{metrics['total_documents']:,}",
                delta=f"+{metrics['new_documents']} this week"
            )
        
        with col2:
            st.metric(
                "Unique Authors",
                f"{metrics['unique_authors']:,}",
                delta=f"+{metrics['new_authors']} this week"
            )
        
        with col3:
            st.metric(
                "Research Domains",
                metrics['domain_count'],
                delta=None
            )
        
        with col4:
            st.metric(
                "Avg Citations",
                f"{metrics['avg_citations']:.1f}",
                delta=f"{metrics['citation_trend']:+.1%} trend"
            )
        
        # Key insights
        if metrics['key_insights']:
            st.info("🔍 " + metrics['key_insights'][0])
    
    def _render_citation_network(self):
        """Render citation network analysis"""
        st.subheader("Citation Network Analysis")
        
        # Get citation data
        citation_data = self._get_citation_network_data()
        
        # Network visualization options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            viz_type = st.radio(
                "Visualization Type",
                ["2D Network", "3D Network", "Hierarchical", "Circular"],
                horizontal=True
            )
        
        with col2:
            color_by = st.selectbox(
                "Color By",
                ["Year", "Domain", "Citations", "Centrality"]
            )
        
        with col3:
            size_by = st.selectbox(
                "Size By",
                ["Citations", "PageRank", "Degree", "Impact"]
            )
        
        # Create and display network
        if viz_type == "2D Network":
            fig = self._create_2d_citation_network(citation_data, color_by, size_by)
        elif viz_type == "3D Network":
            fig = self._create_3d_citation_network(citation_data, color_by, size_by)
        elif viz_type == "Hierarchical":
            fig = self._create_hierarchical_network(citation_data)
        else:
            fig = self._create_circular_network(citation_data)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Citation statistics
        st.markdown("### Citation Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Most cited papers
            st.write("**Most Cited Papers:**")
            cited_df = pd.DataFrame(citation_data['most_cited'])
            st.dataframe(cited_df.head(10), use_container_width=True)
        
        with col2:
            # Citation distribution
            fig = px.histogram(
                citation_data['citation_counts'],
                x='citations',
                nbins=30,
                title="Citation Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_entity_clustering(self):
        """Render cross-document entity analysis"""
        st.subheader("Cross-Document Entity Analysis")
        
        # Entity type filter
        entity_types = ["All Types", "PERSON", "ORG", "GPE", "CONCEPT", "TECHNOLOGY"]
        selected_type = st.selectbox("Entity Type", entity_types)
        
        # Get entity cluster data
        clusters = self._get_entity_clusters(selected_type)
        
        # Cluster visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Entity co-occurrence network
            fig = self._create_entity_network(clusters)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cluster statistics
            st.markdown("### Cluster Statistics")
            
            stats_df = pd.DataFrame({
                'Metric': ['Total Entities', 'Unique Clusters', 'Avg Cluster Size', 'Max Cluster Size'],
                'Value': [
                    clusters['total_entities'],
                    clusters['cluster_count'],
                    f"{clusters['avg_cluster_size']:.1f}",
                    clusters['max_cluster_size']
                ]
            })
            st.dataframe(stats_df, use_container_width=True)
        
        # Detailed cluster view
        st.markdown("### Entity Clusters")
        
        # Cluster selection
        cluster_names = [c['name'] for c in clusters['clusters'][:20]]
        selected_cluster = st.selectbox("Select Cluster", cluster_names)
        
        if selected_cluster:
            cluster_data = next(c for c in clusters['clusters'] if c['name'] == selected_cluster)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Entities in Cluster:**")
                entity_df = pd.DataFrame(cluster_data['entities'])
                st.dataframe(entity_df, use_container_width=True)
            
            with col2:
                st.write("**Document Distribution:**")
                doc_dist = pd.DataFrame(cluster_data['document_distribution'])
                fig = px.pie(doc_dist, values='count', names='document', title="")
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_temporal_analysis(self):
        """Render temporal concept evolution"""
        st.subheader("Temporal Concept Evolution")
        
        # Concept selection
        concepts = self._get_top_concepts()
        selected_concepts = st.multiselect(
            "Select Concepts",
            concepts,
            default=concepts[:3]
        )
        
        if selected_concepts:
            # Get temporal data
            temporal_data = self._get_temporal_evolution(selected_concepts)
            
            # Evolution chart
            fig = go.Figure()
            
            for concept in selected_concepts:
                data = temporal_data[concept]
                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data['frequency'],
                    mode='lines+markers',
                    name=concept,
                    line=dict(width=3)
                ))
            
            fig.update_layout(
                title="Concept Frequency Over Time",
                xaxis_title="Date",
                yaxis_title="Frequency",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Concept relationships over time
            st.markdown("### Concept Relationships Evolution")
            
            time_point = st.slider(
                "Select Time Point",
                min_value=0,
                max_value=len(temporal_data['time_points'])-1,
                value=len(temporal_data['time_points'])-1,
                format_func=lambda x: temporal_data['time_points'][x]
            )
            
            # Show concept network at selected time
            network_data = self._get_concept_network_at_time(
                selected_concepts,
                temporal_data['time_points'][time_point]
            )
            
            fig = self._create_concept_network(network_data)
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_domain_insights(self):
        """Render research domain insights"""
        st.subheader("Research Domain Insights")
        
        # Get domain data
        domain_data = self._get_domain_insights()
        
        # Domain overview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Domain distribution
            fig = px.treemap(
                domain_data['distribution'],
                path=['category', 'domain'],
                values='count',
                title="Research Domain Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Domain growth
            fig = px.line(
                domain_data['growth'],
                x='year',
                y='publications',
                color='domain',
                title="Domain Growth Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Cross-domain connections
        st.markdown("### Cross-Domain Connections")
        
        # Sankey diagram for domain relationships
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=domain_data['sankey']['labels'],
                color=domain_data['sankey']['colors']
            ),
            link=dict(
                source=domain_data['sankey']['source'],
                target=domain_data['sankey']['target'],
                value=domain_data['sankey']['value']
            )
        )])
        
        fig.update_layout(title="Cross-Domain Research Flow", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Emerging topics
        st.markdown("### Emerging Topics")
        
        emerging_df = pd.DataFrame(domain_data['emerging_topics'])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Topic growth chart
            fig = px.bar(
                emerging_df.head(10),
                x='topic',
                y='growth_rate',
                color='domain',
                title="Fastest Growing Topics"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Topic details
            st.dataframe(
                emerging_df[['topic', 'domain', 'growth_rate', 'papers']].head(10),
                use_container_width=True
            )
    
    def _render_statistical_analysis(self):
        """Render statistical analysis section"""
        st.subheader("Statistical Analysis")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Correlation Analysis", "Trend Analysis", "Impact Factors", "Clustering Analysis"]
        )
        
        if analysis_type == "Correlation Analysis":
            self._render_correlation_analysis()
        elif analysis_type == "Trend Analysis":
            self._render_trend_analysis()
        elif analysis_type == "Impact Factors":
            self._render_impact_analysis()
        else:
            self._render_clustering_analysis()
    
    def _render_correlation_analysis(self):
        """Render correlation analysis"""
        # Get correlation data
        corr_data = self._get_correlation_data()
        
        # Correlation matrix
        fig = px.imshow(
            corr_data['matrix'],
            labels=dict(x="Variable", y="Variable", color="Correlation"),
            x=corr_data['variables'],
            y=corr_data['variables'],
            color_continuous_scale='RdBu',
            aspect="auto"
        )
        fig.update_layout(title="Research Metrics Correlation Matrix")
        st.plotly_chart(fig, use_container_width=True)
        
        # Significant correlations
        st.markdown("### Significant Correlations")
        
        sig_corr = pd.DataFrame(corr_data['significant_correlations'])
        st.dataframe(sig_corr, use_container_width=True)
    
    def _render_trend_analysis(self):
        """Render trend analysis"""
        # Trend options
        trend_metric = st.selectbox(
            "Metric",
            ["Publications", "Citations", "Collaborations", "Cross-Domain"]
        )
        
        # Get trend data
        trend_data = self._get_trend_data(trend_metric)
        
        # Trend visualization
        fig = go.Figure()
        
        # Actual data
        fig.add_trace(go.Scatter(
            x=trend_data['dates'],
            y=trend_data['values'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='blue', width=2)
        ))
        
        # Trend line
        fig.add_trace(go.Scatter(
            x=trend_data['dates'],
            y=trend_data['trend'],
            mode='lines',
            name='Trend',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=trend_data['dates'] + trend_data['dates'][::-1],
            y=trend_data['upper_bound'] + trend_data['lower_bound'][::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        ))
        
        fig.update_layout(
            title=f"{trend_metric} Trend Analysis",
            xaxis_title="Date",
            yaxis_title=trend_metric,
            hovermode='x'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Trend Direction", trend_data['direction'])
        with col2:
            st.metric("Growth Rate", f"{trend_data['growth_rate']:.1%}")
        with col3:
            st.metric("R-squared", f"{trend_data['r_squared']:.3f}")
    
    def _render_impact_analysis(self):
        """Render impact factor analysis"""
        # Get impact data
        impact_data = self._get_impact_factors()
        
        # Impact distribution
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bubble chart
            fig = px.scatter(
                impact_data['papers'],
                x='citations',
                y='h_index',
                size='impact_score',
                color='domain',
                hover_data=['title', 'authors'],
                title="Research Impact Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top impact papers
            st.markdown("### High Impact Research")
            impact_df = pd.DataFrame(impact_data['top_impact'])
            st.dataframe(impact_df.head(10), use_container_width=True)
    
    def _render_clustering_analysis(self):
        """Render clustering analysis"""
        # Clustering options
        cluster_by = st.selectbox(
            "Cluster By",
            ["Topic Similarity", "Citation Patterns", "Author Networks", "Methodology"]
        )
        
        # Get clustering data
        cluster_data = self._get_clustering_data(cluster_by)
        
        # Cluster visualization
        fig = px.scatter(
            cluster_data['points'],
            x='x',
            y='y',
            color='cluster',
            size='size',
            hover_data=['label', 'cluster_name'],
            title=f"Research Clustering by {cluster_by}"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cluster characteristics
        st.markdown("### Cluster Characteristics")
        
        char_df = pd.DataFrame(cluster_data['characteristics'])
        st.dataframe(char_df, use_container_width=True)
    
    # Helper methods for creating visualizations
    
    def _create_2d_citation_network(self, data: Dict, color_by: str, size_by: str) -> go.Figure:
        """Create 2D citation network visualization"""
        G = nx.from_pandas_edgelist(
            pd.DataFrame(data['edges']),
            source='source',
            target='target',
            edge_attr='weight'
        )
        
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
        
        # Edge traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=0.5, color='#888'),
                    hoverinfo='none'
                )
            )
        
        # Node trace
        node_x = []
        node_y = []
        node_color = []
        node_size = []
        node_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node attributes
            node_data = data['nodes'].get(node, {})
            
            # Color
            if color_by == "Year":
                node_color.append(node_data.get('year', 2020))
            elif color_by == "Domain":
                node_color.append(hash(node_data.get('domain', 'Unknown')) % 10)
            elif color_by == "Citations":
                node_color.append(node_data.get('citations', 0))
            else:  # Centrality
                node_color.append(nx.degree_centrality(G)[node])
            
            # Size
            if size_by == "Citations":
                node_size.append(10 + node_data.get('citations', 0) * 0.5)
            elif size_by == "PageRank":
                pr = nx.pagerank(G)
                node_size.append(10 + pr[node] * 1000)
            elif size_by == "Degree":
                node_size.append(10 + G.degree(node) * 2)
            else:  # Impact
                node_size.append(10 + node_data.get('impact', 1) * 5)
            
            # Text
            node_text.append(f"{node_data.get('title', node)[:50]}...")
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers',
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                color=node_color,
                size=node_size,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=color_by)
            )
        )
        
        fig = go.Figure(data=edge_trace + [node_trace])
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def _create_3d_citation_network(self, data: Dict, color_by: str, size_by: str) -> go.Figure:
        """Create 3D citation network visualization"""
        # Similar to 2D but with 3D layout
        # Implementation would follow similar pattern with 3D coordinates
        return self._create_2d_citation_network(data, color_by, size_by)  # Placeholder
    
    def _create_entity_network(self, clusters: Dict) -> go.Figure:
        """Create entity co-occurrence network"""
        # Create co-occurrence matrix
        entities = clusters['entities']
        co_occur = clusters['co_occurrence']
        
        # Create network graph
        fig = go.Figure()
        
        # Add nodes
        for entity in entities:
            fig.add_trace(go.Scatter(
                x=[entity['x']],
                y=[entity['y']],
                mode='markers+text',
                text=[entity['name']],
                textposition='top center',
                marker=dict(
                    size=entity['frequency'] * 2,
                    color=entity['cluster_id']
                ),
                showlegend=False
            ))
        
        # Add edges for co-occurrences
        for edge in co_occur:
            if edge['weight'] > 0.1:  # Threshold for visibility
                fig.add_trace(go.Scatter(
                    x=[edge['x0'], edge['x1']],
                    y=[edge['y0'], edge['y1']],
                    mode='lines',
                    line=dict(
                        width=edge['weight'] * 5,
                        color='rgba(125,125,125,0.5)'
                    ),
                    showlegend=False
                ))
        
        fig.update_layout(
            title="Entity Co-occurrence Network",
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    # Data retrieval methods - real implementation needed
    
    def _get_available_domains(self) -> List[str]:
        """Get list of available research domains"""
        return [
            "Computer Science",
            "Biology",
            "Physics",
            "Medicine",
            "Psychology",
            "Economics",
            "Environmental Science"
        ]
    
    def _get_research_metrics(self) -> Dict[str, Any]:
        """Get research overview metrics"""
        return {
            'total_documents': 15234,
            'new_documents': 342,
            'unique_authors': 4567,
            'new_authors': 89,
            'domain_count': 7,
            'avg_citations': 23.4,
            'citation_trend': 0.12,
            'key_insights': [
                "Citation rates increasing 12% month-over-month",
                "Cross-domain collaborations up 25% this quarter",
                "Emerging trend in AI-biology intersections"
            ]
        }
    
    def _get_citation_network_data(self) -> Dict[str, Any]:
        """Get citation network data"""
        # Generate sample network data
        nodes = {}
        edges = []
        
        # Create sample papers
        for i in range(50):
            nodes[f"paper_{i}"] = {
                'title': f"Research Paper {i}",
                'year': 2020 + (i % 5),
                'domain': np.random.choice(['CS', 'Bio', 'Physics']),
                'citations': np.random.randint(0, 100),
                'impact': np.random.uniform(0, 10)
            }
        
        # Create citation edges
        for i in range(100):
            source = f"paper_{np.random.randint(0, 50)}"
            target = f"paper_{np.random.randint(0, 50)}"
            if source != target:
                edges.append({
                    'source': source,
                    'target': target,
                    'weight': np.random.uniform(0.1, 1.0)
                })
        
        # Most cited papers
        most_cited = sorted(
            [(k, v['citations']) for k, v in nodes.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        most_cited_df = pd.DataFrame(
            [(nodes[k]['title'], c) for k, c in most_cited],
            columns=['Title', 'Citations']
        )
        
        return {
            'nodes': nodes,
            'edges': pd.DataFrame(edges),
            'most_cited': most_cited_df,
            'citation_counts': pd.DataFrame({'citations': [v['citations'] for v in nodes.values()]})
        }
    
    def _get_entity_clusters(self, entity_type: str) -> Dict[str, Any]:
        """Get entity cluster data"""
        # Generate sample clusters
        clusters = []
        entities = []
        
        for i in range(20):
            cluster = {
                'name': f"Cluster_{i}",
                'size': np.random.randint(5, 50),
                'entities': [],
                'document_distribution': []
            }
            
            # Add entities to cluster
            for j in range(cluster['size']):
                entity = {
                    'name': f"Entity_{i}_{j}",
                    'type': entity_type if entity_type != "All Types" else np.random.choice(['PERSON', 'ORG', 'GPE']),
                    'frequency': np.random.randint(1, 20),
                    'documents': np.random.randint(1, 10)
                }
                cluster['entities'].append(entity)
                entities.append({
                    'name': entity['name'],
                    'cluster_id': i,
                    'frequency': entity['frequency'],
                    'x': np.random.uniform(-1, 1),
                    'y': np.random.uniform(-1, 1)
                })
            
            # Document distribution
            for k in range(5):
                cluster['document_distribution'].append({
                    'document': f"Doc_{k}",
                    'count': np.random.randint(1, 10)
                })
            
            clusters.append(cluster)
        
        # Generate co-occurrence data
        co_occurrence = []
        for i in range(50):
            idx1, idx2 = np.random.choice(len(entities), 2, replace=False)
            e1, e2 = entities[idx1], entities[idx2]
            co_occurrence.append({
                'x0': e1['x'],
                'y0': e1['y'],
                'x1': e2['x'],
                'y1': e2['y'],
                'weight': np.random.uniform(0, 1)
            })
        
        return {
            'clusters': clusters,
            'entities': entities,
            'co_occurrence': co_occurrence,
            'total_entities': len(entities),
            'cluster_count': len(clusters),
            'avg_cluster_size': np.mean([c['size'] for c in clusters]),
            'max_cluster_size': max(c['size'] for c in clusters)
        }
    
    def _get_top_concepts(self) -> List[str]:
        """Get top research concepts"""
        return [
            "Machine Learning",
            "Neural Networks",
            "Quantum Computing",
            "Gene Editing",
            "Climate Change",
            "Renewable Energy",
            "Protein Folding",
            "Natural Language Processing",
            "Computer Vision",
            "Blockchain"
        ]
    
    def _get_temporal_evolution(self, concepts: List[str]) -> Dict[str, Any]:
        """Get temporal evolution data for concepts"""
        # Generate time series data
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='M')
        
        temporal_data = {}
        for concept in concepts:
            # Generate frequency data with trend
            base = np.random.uniform(10, 50)
            trend = np.random.uniform(-0.5, 1.5)
            noise = np.random.normal(0, 5, len(dates))
            
            frequency = base + trend * np.arange(len(dates)) + noise
            frequency = np.maximum(frequency, 0)  # Ensure non-negative
            
            temporal_data[concept] = {
                'dates': dates,
                'frequency': frequency
            }
        
        temporal_data['time_points'] = [d.strftime('%Y-%m') for d in dates]
        
        return temporal_data
    
    def _get_domain_insights(self) -> Dict[str, Any]:
        """Get domain insight data"""
        # Domain distribution
        domains = ['CS', 'Bio', 'Physics', 'Chem', 'Math', 'Medicine', 'Psychology']
        categories = ['STEM', 'STEM', 'STEM', 'STEM', 'STEM', 'Life Sciences', 'Social Sciences']
        
        distribution = []
        for domain, category in zip(domains, categories):
            distribution.append({
                'domain': domain,
                'category': category,
                'count': np.random.randint(100, 1000)
            })
        
        # Domain growth over time
        years = list(range(2018, 2024))
        growth_data = []
        for domain in domains[:4]:  # Top 4 domains
            for year in years:
                growth_data.append({
                    'domain': domain,
                    'year': year,
                    'publications': np.random.randint(50, 500)
                })
        
        # Sankey diagram data
        sankey_data = {
            'labels': domains + ['Interdisciplinary'],
            'colors': ['blue', 'green', 'red', 'yellow', 'purple', 'orange', 'pink', 'gray'],
            'source': [0, 0, 1, 1, 2, 2, 3, 3, 4, 4],
            'target': [7, 1, 7, 2, 7, 3, 7, 4, 7, 5],
            'value': [10, 15, 20, 25, 30, 10, 15, 20, 25, 30]
        }
        
        # Emerging topics
        emerging_topics = []
        for i in range(15):
            emerging_topics.append({
                'topic': f"Emerging Topic {i+1}",
                'domain': np.random.choice(domains),
                'growth_rate': np.random.uniform(0.2, 2.0),
                'papers': np.random.randint(10, 100)
            })
        
        return {
            'distribution': pd.DataFrame(distribution),
            'growth': pd.DataFrame(growth_data),
            'sankey': sankey_data,
            'emerging_topics': pd.DataFrame(emerging_topics).sort_values('growth_rate', ascending=False)
        }
    
    def _get_correlation_data(self) -> Dict[str, Any]:
        """Get correlation analysis data"""
        variables = ['Citations', 'Authors', 'Pages', 'References', 'Impact', 'Novelty']
        n_vars = len(variables)
        
        # Generate correlation matrix
        corr_matrix = np.random.rand(n_vars, n_vars)
        corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Make symmetric
        np.fill_diagonal(corr_matrix, 1.0)  # Diagonal = 1
        
        # Significant correlations
        sig_corr = []
        for i in range(n_vars):
            for j in range(i+1, n_vars):
                if abs(corr_matrix[i, j]) > 0.7:
                    sig_corr.append({
                        'Variable 1': variables[i],
                        'Variable 2': variables[j],
                        'Correlation': corr_matrix[i, j],
                        'p-value': np.random.uniform(0.001, 0.05)
                    })
        
        return {
            'matrix': corr_matrix,
            'variables': variables,
            'significant_correlations': sig_corr
        }
    
    def _get_trend_data(self, metric: str) -> Dict[str, Any]:
        """Get trend analysis data"""
        # Generate time series with trend
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='M')
        n_points = len(dates)
        
        # Generate data with trend
        trend_slope = np.random.uniform(0.5, 2.0)
        base_value = 100
        noise = np.random.normal(0, 10, n_points)
        
        values = base_value + trend_slope * np.arange(n_points) + noise
        
        # Fit trend line
        x = np.arange(n_points)
        z = np.polyfit(x, values, 1)
        p = np.poly1d(z)
        trend_line = p(x)
        
        # Calculate R-squared
        ss_res = np.sum((values - trend_line) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Confidence intervals
        std_error = np.sqrt(ss_res / (n_points - 2))
        confidence = 1.96 * std_error
        
        return {
            'dates': dates,
            'values': values,
            'trend': trend_line,
            'upper_bound': trend_line + confidence,
            'lower_bound': trend_line - confidence,
            'direction': "Increasing" if z[0] > 0 else "Decreasing",
            'growth_rate': z[0] / base_value,
            'r_squared': r_squared
        }
    
    def _get_impact_factors(self) -> Dict[str, Any]:
        """Get impact factor data"""
        # Generate sample papers with impact metrics
        papers = []
        for i in range(100):
            papers.append({
                'title': f"Paper {i}",
                'authors': f"Author {i} et al.",
                'citations': np.random.randint(0, 200),
                'h_index': np.random.randint(0, 50),
                'impact_score': np.random.uniform(0, 100),
                'domain': np.random.choice(['CS', 'Bio', 'Physics', 'Medicine'])
            })
        
        papers_df = pd.DataFrame(papers)
        
        # Top impact papers
        top_impact = papers_df.nlargest(10, 'impact_score')[['title', 'impact_score', 'citations']]
        
        return {
            'papers': papers_df,
            'top_impact': top_impact
        }
    
    def _get_clustering_data(self, cluster_by: str) -> Dict[str, Any]:
        """Get clustering analysis data"""
        # Generate clustered points
        n_clusters = 5
        n_points = 200
        
        points = []
        characteristics = []
        
        for cluster_id in range(n_clusters):
            # Cluster center
            cx, cy = np.random.uniform(-5, 5, 2)
            
            # Generate points around center
            for _ in range(n_points // n_clusters):
                x = cx + np.random.normal(0, 1)
                y = cy + np.random.normal(0, 1)
                
                points.append({
                    'x': x,
                    'y': y,
                    'cluster': cluster_id,
                    'cluster_name': f"Cluster {cluster_id}",
                    'label': f"Item {len(points)}",
                    'size': np.random.uniform(5, 20)
                })
            
            # Cluster characteristics
            characteristics.append({
                'Cluster': f"Cluster {cluster_id}",
                'Size': n_points // n_clusters,
                'Density': np.random.uniform(0.5, 1.0),
                'Cohesion': np.random.uniform(0.6, 0.95),
                'Separation': np.random.uniform(0.7, 0.9)
            })
        
        return {
            'points': pd.DataFrame(points),
            'characteristics': characteristics
        }
    
    def _get_concept_network_at_time(self, concepts: List[str], time_point: str) -> Dict[str, Any]:
        """Get concept network data at specific time point"""
        # Generate network data
        nodes = []
        edges = []
        
        # Add concept nodes
        for i, concept in enumerate(concepts):
            nodes.append({
                'id': i,
                'label': concept,
                'size': np.random.uniform(10, 30)
            })
        
        # Add related concepts
        for i in range(5):
            nodes.append({
                'id': len(concepts) + i,
                'label': f"Related_{i}",
                'size': np.random.uniform(5, 15)
            })
        
        # Create edges
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if np.random.random() > 0.6:  # 40% chance of connection
                    edges.append({
                        'source': i,
                        'target': j,
                        'weight': np.random.uniform(0.1, 1.0)
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'time_point': time_point
        }
    
    def _create_concept_network(self, network_data: Dict) -> go.Figure:
        """Create concept network visualization"""
        # Simple force-directed layout visualization
        G = nx.Graph()
        
        # Add nodes
        for node in network_data['nodes']:
            G.add_node(node['id'], **node)
        
        # Add edges
        for edge in network_data['edges']:
            G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
        # Calculate layout
        pos = nx.spring_layout(G)
        
        # Create traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=G.edges[edge]['weight'] * 2, color='#888'),
                    hoverinfo='none'
                )
            )
        
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            text=[G.nodes[node]['label'] for node in G.nodes()],
            textposition='top center',
            marker=dict(
                size=[G.nodes[node]['size'] for node in G.nodes()],
                color='lightblue',
                line=dict(width=2, color='darkblue')
            )
        )
        
        fig = go.Figure(data=edge_trace + [node_trace])
        fig.update_layout(
            title=f"Concept Network at {network_data['time_point']}",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def _create_hierarchical_network(self, data: Dict) -> go.Figure:
        """Create hierarchical network layout"""
        # Placeholder - would implement hierarchical layout
        return self._create_2d_citation_network(data, "Year", "Citations")
    
    def _create_circular_network(self, data: Dict) -> go.Figure:
        """Create circular network layout"""
        # Placeholder - would implement circular layout
        return self._create_2d_citation_network(data, "Domain", "PageRank")


if __name__ == "__main__":
    # Test the research analytics dashboard
    dashboard = ResearchAnalyticsDashboard()
    dashboard.render_research_analytics()