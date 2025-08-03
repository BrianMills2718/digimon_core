"""
Plotly Graph Renderer

Creates interactive Plotly visualizations from graph data with multiple plot types.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from .visualization_data_models import (
    VisualizationData, NodeData, EdgeData, GraphVisualizationConfig,
    OntologyInfo, DefaultColorPalette
)

logger = logging.getLogger(__name__)


class PlotlyGraphRenderer:
    """Create interactive Plotly visualizations from graph data"""
    
    def __init__(self):
        """Initialize renderer with color palette"""
        self.color_palette = DefaultColorPalette.get_default_palette()
    
    def create_interactive_plot(self, data: VisualizationData,
                               config: Optional[GraphVisualizationConfig] = None) -> go.Figure:
        """
        Create an interactive Plotly graph visualization.
        
        Args:
            data: Visualization data with nodes, edges, and layout
            config: Visualization configuration
            
        Returns:
            Plotly Figure with interactive graph
        """
        if config is None:
            config = GraphVisualizationConfig()
        
        fig = go.Figure()
        
        # Add edges first (so they appear behind nodes)
        edge_trace = self._create_edge_trace(data.edges, data.layout_positions)
        if edge_trace:
            fig.add_trace(edge_trace)
        
        # Add nodes
        node_trace = self._create_node_trace(data.nodes, data.layout_positions, config)
        fig.add_trace(node_trace)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Ontology-Aware Knowledge Graph ({data.metrics.total_nodes} entities, {data.metrics.total_edges} relationships)",
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[dict(
                text="Hover over nodes for details. Drag to pan, scroll to zoom.",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig
    
    def create_ontology_structure_plot(self, ontology_info: OntologyInfo) -> go.Figure:
        """Create a plot showing the ontology structure analysis"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Entity Type Distribution', 'Relationship Type Distribution',
                           'Confidence Distribution', 'Ontology Coverage'),
            specs=[[{"type": "pie"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Entity type distribution (top-left)
        if ontology_info.entity_type_counts:
            entity_types = list(ontology_info.entity_type_counts.keys())
            entity_counts = list(ontology_info.entity_type_counts.values())
            colors = [self.color_palette.get_entity_color(et) for et in entity_types]
            
            fig.add_trace(
                go.Pie(labels=entity_types, values=entity_counts, 
                       marker_colors=colors, name="Entity Types"),
                row=1, col=1
            )
        
        # Relationship type distribution (top-right)
        if ontology_info.relationship_type_counts:
            rel_types = list(ontology_info.relationship_type_counts.keys())
            rel_counts = list(ontology_info.relationship_type_counts.values())
            colors = [self.color_palette.get_relationship_color(rt) for rt in rel_types]
            
            fig.add_trace(
                go.Pie(labels=rel_types, values=rel_counts,
                       marker_colors=colors, name="Relationship Types"),
                row=1, col=2
            )
        
        # Confidence distribution (bottom-left)
        if ontology_info.confidence_distribution:
            conf_buckets = list(ontology_info.confidence_distribution.keys())
            conf_counts = list(ontology_info.confidence_distribution.values())
            
            fig.add_trace(
                go.Bar(x=conf_buckets, y=conf_counts, 
                       marker_color=['#e74c3c', '#f39c12', '#2ecc71'],
                       name="Confidence"),
                row=2, col=1
            )
        
        # Ontology coverage (bottom-right)
        coverage_data = ontology_info.ontology_coverage
        if coverage_data:
            categories = list(coverage_data.keys())
            percentages = list(coverage_data.values())
            
            fig.add_trace(
                go.Bar(x=categories, y=percentages,
                       marker_color='#3498db',
                       name="Coverage"),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Ontology Structure Analysis",
            showlegend=False,
            height=600
        )
        
        return fig
    
    def create_semantic_similarity_heatmap(self, data: VisualizationData) -> go.Figure:
        """Create a heatmap showing semantic similarity between entities"""
        # Extract entities with embeddings
        entities_with_embeddings = []
        entity_names = []
        
        for node in data.nodes:
            if 'embedding' in node.attributes:
                entities_with_embeddings.append(node.attributes['embedding'])
                entity_names.append(node.name)
        
        if len(entities_with_embeddings) < 2:
            # Return empty plot if insufficient data
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient embedding data for similarity analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title="Entity Semantic Similarity Heatmap")
            return fig
        
        # Calculate similarity matrix
        similarity_matrix = []
        for i, emb1 in enumerate(entities_with_embeddings):
            row = []
            for j, emb2 in enumerate(entities_with_embeddings):
                if i == j:
                    similarity = 1.0
                else:
                    # Cosine similarity
                    try:
                        dot_product = np.dot(emb1, emb2)
                        norm1 = np.linalg.norm(emb1)
                        norm2 = np.linalg.norm(emb2)
                        similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
                    except Exception as e:
                        logger.warning(f"Failed to calculate similarity: {e}")
                        similarity = 0.0
                row.append(similarity)
            similarity_matrix.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=entity_names,
            y=entity_names,
            colorscale='Viridis',
            text=[[f"{val:.3f}" for val in row] for row in similarity_matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Entity Semantic Similarity Heatmap",
            xaxis_title="Entities",
            yaxis_title="Entities",
            height=min(800, max(400, len(entity_names) * 30))
        )
        
        return fig
    
    def create_confidence_distribution_plot(self, data: VisualizationData) -> go.Figure:
        """Create plot showing confidence distribution across entities"""
        if not data.nodes:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for confidence distribution",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Extract confidence values
        confidence_values = [node.confidence for node in data.nodes]
        
        # Create histogram
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=confidence_values,
            nbinsx=20,
            marker_color='rgba(52, 152, 219, 0.7)',
            name="Entity Confidence Distribution"
        ))
        
        # Add mean line
        mean_confidence = np.mean(confidence_values)
        fig.add_vline(
            x=mean_confidence,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_confidence:.3f}"
        )
        
        fig.update_layout(
            title="Entity Confidence Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Number of Entities",
            showlegend=False
        )
        
        return fig
    
    def create_network_metrics_plot(self, data: VisualizationData) -> go.Figure:
        """Create plot showing network metrics and statistics"""
        metrics = data.metrics
        
        # Create metrics visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Graph Statistics', 'Entity Types', 'Relationship Types', 'Quality Metrics'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Graph statistics (top-left)
        stats_labels = ['Nodes', 'Edges', 'Entity Types', 'Relationship Types']
        stats_values = [metrics.total_nodes, metrics.total_edges, 
                       metrics.entity_types, metrics.relationship_types]
        
        fig.add_trace(
            go.Bar(x=stats_labels, y=stats_values,
                   marker_color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
                   name="Graph Statistics"),
            row=1, col=1
        )
        
        # Entity type distribution (top-right)
        if data.ontology_info.entity_type_counts:
            entity_types = list(data.ontology_info.entity_type_counts.keys())
            entity_counts = list(data.ontology_info.entity_type_counts.values())
            colors = [self.color_palette.get_entity_color(et) for et in entity_types]
            
            fig.add_trace(
                go.Pie(labels=entity_types, values=entity_counts,
                       marker_colors=colors, name="Entity Types"),
                row=1, col=2
            )
        
        # Relationship type distribution (bottom-left)
        if data.ontology_info.relationship_type_counts:
            rel_types = list(data.ontology_info.relationship_type_counts.keys())
            rel_counts = list(data.ontology_info.relationship_type_counts.values())
            colors = [self.color_palette.get_relationship_color(rt) for rt in rel_types]
            
            fig.add_trace(
                go.Pie(labels=rel_types, values=rel_counts,
                       marker_colors=colors, name="Relationship Types"),
                row=2, col=1
            )
        
        # Quality metrics (bottom-right)
        quality_labels = ['Avg Confidence', 'Graph Density']
        quality_values = [metrics.avg_confidence, metrics.graph_density]
        
        fig.add_trace(
            go.Bar(x=quality_labels, y=quality_values,
                   marker_color=['#9b59b6', '#1abc9c'],
                   name="Quality Metrics"),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Network Analysis Dashboard",
            showlegend=False,
            height=700
        )
        
        return fig
    
    def _create_edge_trace(self, edges: List[EdgeData], 
                          positions: Dict[str, tuple]) -> Optional[go.Scatter]:
        """Create edge trace for visualization"""
        if not edges or not positions:
            return None
        
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in edges:
            source_pos = positions.get(edge.source)
            target_pos = positions.get(edge.target)
            
            if source_pos and target_pos:
                edge_x.extend([source_pos[0], target_pos[0], None])
                edge_y.extend([source_pos[1], target_pos[1], None])
                edge_info.append(f"{edge.type} (confidence: {edge.confidence:.2f})")
        
        if not edge_x:
            return None
        
        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Relationships'
        )
    
    def _create_node_trace(self, nodes: List[NodeData], 
                          positions: Dict[str, tuple],
                          config: GraphVisualizationConfig) -> go.Scatter:
        """Create node trace for visualization"""
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_text = []
        node_info = []
        
        for node in nodes:
            pos = positions.get(node.id)
            if pos:
                node_x.append(pos[0])
                node_y.append(pos[1])
                node_colors.append(node.color or self.color_palette.default_color)
                node_sizes.append(node.size or 10)
                
                # Node labels
                if config.show_labels:
                    node_text.append(node.name)
                else:
                    node_text.append("")
                
                # Hover info
                sources_str = ", ".join((node.sources or [])[:3])
                if len(node.sources or []) > 3:
                    sources_str += "..."
                
                hover_text = (
                    f"<b>{node.name}</b><br>"
                    f"Type: {node.type}<br>"
                    f"Confidence: {node.confidence:.2f}<br>"
                    f"Domain: {node.domain or 'unknown'}<br>"
                    f"Sources: {sources_str}"
                )
                
                # Add custom attributes to hover text
                if node.attributes:
                    for key, value in list(node.attributes.items())[:5]:  # Limit to 5 attributes
                        if key != 'embedding':  # Skip large embedding vectors
                            hover_text += f"<br>{key}: {str(value)[:50]}"
                
                node_info.append(hover_text)
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text' if config.show_labels else 'markers',
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color="white"),
                sizemode='diameter'
            ),
            name='Entities'
        )
    
    def create_multi_view_dashboard(self, data: VisualizationData,
                                   config: Optional[GraphVisualizationConfig] = None) -> go.Figure:
        """Create a multi-view dashboard with multiple visualizations"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Main Graph View', 'Confidence Distribution',
                'Entity Types', 'Relationship Types',
                'Network Metrics', 'Quality Assessment'
            ),
            specs=[
                [{"colspan": 2}, None],  # Graph takes full width
                [{"type": "pie"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # Main graph view (top row, full width)
        main_plot = self.create_interactive_plot(data, config)
        for trace in main_plot.data:
            fig.add_trace(trace, row=1, col=1)
        
        # Entity types pie chart (middle-left)
        if data.ontology_info.entity_type_counts:
            entity_types = list(data.ontology_info.entity_type_counts.keys())
            entity_counts = list(data.ontology_info.entity_type_counts.values())
            colors = [self.color_palette.get_entity_color(et) for et in entity_types]
            
            fig.add_trace(
                go.Pie(labels=entity_types, values=entity_counts,
                       marker_colors=colors, name="Entity Types"),
                row=2, col=1
            )
        
        # Relationship types pie chart (middle-right)
        if data.ontology_info.relationship_type_counts:
            rel_types = list(data.ontology_info.relationship_type_counts.keys())
            rel_counts = list(data.ontology_info.relationship_type_counts.values())
            colors = [self.color_palette.get_relationship_color(rt) for rt in rel_types]
            
            fig.add_trace(
                go.Pie(labels=rel_types, values=rel_counts,
                       marker_colors=colors, name="Relationship Types"),
                row=2, col=2
            )
        
        # Network metrics (bottom-left)
        metrics_labels = ['Nodes', 'Edges', 'Avg Confidence', 'Density']
        metrics_values = [
            data.metrics.total_nodes,
            data.metrics.total_edges,
            data.metrics.avg_confidence * 100,  # Scale for visibility
            data.metrics.graph_density * 100   # Scale for visibility
        ]
        
        fig.add_trace(
            go.Bar(x=metrics_labels, y=metrics_values,
                   marker_color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
                   name="Network Metrics"),
            row=3, col=1
        )
        
        # Quality assessment (bottom-right)
        quality_labels = ['Entity Types', 'Relationship Types', 'Coverage']
        quality_values = [
            data.metrics.entity_types,
            data.metrics.relationship_types,
            len(data.ontology_info.domains) if data.ontology_info.domains else 0
        ]
        
        fig.add_trace(
            go.Bar(x=quality_labels, y=quality_values,
                   marker_color=['#9b59b6', '#1abc9c', '#e67e22'],
                   name="Quality Assessment"),
            row=3, col=2
        )
        
        fig.update_layout(
            title_text="Knowledge Graph Analysis Dashboard",
            showlegend=False,
            height=1000
        )
        
        return fig
    
    def export_plot_data(self, fig: go.Figure, format_type: str = "json") -> Union[str, bytes]:
        """Export plot data in various formats"""
        try:
            if format_type.lower() == "json":
                return fig.to_json()
            elif format_type.lower() == "html":
                return fig.to_html()
            elif format_type.lower() == "png":
                return fig.to_image(format="png")
            elif format_type.lower() == "svg":
                return fig.to_image(format="svg")
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
        except Exception as e:
            logger.error(f"Failed to export plot in {format_type} format: {e}")
            raise