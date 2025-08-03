"""Plotly Renderer for Graph Visualization

Creates interactive Plotly visualizations from graph data.
"""

import os
import tempfile
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    # Create dummy objects when plotly not available
    class DummyGO:
        Figure = object
        Scatter = object
        
    go = DummyGO()
    px = None
    make_subplots = None
    pyo = None
    PLOTLY_AVAILABLE = False

import networkx as nx
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PlotlyRenderer:
    """Render graph visualizations using Plotly"""
    
    def __init__(self):
        self.plotly_available = PLOTLY_AVAILABLE
        if not self.plotly_available:
            logger.warning("Plotly not available. Visualization features will be limited.")
    
    def create_visualization(self, graph: nx.Graph, layout_data: Dict[str, Any], 
                           node_attributes: Dict[str, Any], edge_attributes: List[Dict[str, Any]],
                           color_mapping: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive Plotly visualization"""
        try:
            if not self.plotly_available:
                return self._create_fallback_visualization(graph, layout_data, config)
            
            positions = layout_data.get("positions", {})
            if not positions:
                logger.error("No layout positions available")
                return {"success": False, "error": "No layout positions"}
            
            # Create figure
            fig = go.Figure()
            
            # Add edges first (so they appear behind nodes)
            self._add_edges_to_figure(fig, edge_attributes, positions)
            
            # Add nodes
            self._add_nodes_to_figure(fig, node_attributes, color_mapping, positions)
            
            # Update layout
            self._update_figure_layout(fig, config, layout_data)
            
            # Generate visualization data
            viz_data = {
                "figure": fig,
                "html": fig.to_html(include_plotlyjs='cdn'),
                "json": fig.to_json(),
                "success": True,
                "interactive": config.get("interactive", True),
                "node_count": len(node_attributes.get("attributes", {})),
                "edge_count": len(edge_attributes)
            }
            
            return viz_data
            
        except Exception as e:
            logger.error(f"Error creating Plotly visualization: {e}")
            return {"success": False, "error": str(e)}
    
    def save_visualization(self, viz_data: Dict[str, Any], output_format: str, 
                          output_dir: Optional[str] = None) -> List[str]:
        """Save visualization to various formats"""
        try:
            if not viz_data.get("success"):
                logger.error("Cannot save failed visualization")
                return []
            
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"graph_visualization_{timestamp}"
            
            saved_files = []
            fig = viz_data.get("figure")
            
            if not fig:
                logger.error("No figure available for saving")
                return []
            
            if output_format == "html" or output_format == "all":
                html_path = os.path.join(output_dir, f"{base_filename}.html")
                fig.write_html(html_path, include_plotlyjs='cdn')
                saved_files.append(html_path)
            
            if output_format == "png" or output_format == "all":
                try:
                    png_path = os.path.join(output_dir, f"{base_filename}.png")
                    fig.write_image(png_path, width=1200, height=800)
                    saved_files.append(png_path)
                except Exception as e:
                    logger.warning(f"Could not save PNG (requires kaleido): {e}")
            
            if output_format == "pdf" or output_format == "all":
                try:
                    pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")
                    fig.write_image(pdf_path, width=1200, height=800)
                    saved_files.append(pdf_path)
                except Exception as e:
                    logger.warning(f"Could not save PDF (requires kaleido): {e}")
            
            if output_format == "json" or output_format == "all":
                json_path = os.path.join(output_dir, f"{base_filename}.json")
                with open(json_path, 'w') as f:
                    json.dump(viz_data.get("json", {}), f, indent=2)
                saved_files.append(json_path)
            
            if output_format == "svg" or output_format == "all":
                try:
                    svg_path = os.path.join(output_dir, f"{base_filename}.svg")
                    fig.write_image(svg_path, width=1200, height=800)
                    saved_files.append(svg_path)
                except Exception as e:
                    logger.warning(f"Could not save SVG (requires kaleido): {e}")
            
            logger.info(f"Saved visualization to {len(saved_files)} files: {saved_files}")
            return saved_files
            
        except Exception as e:
            logger.error(f"Error saving visualization: {e}")
            return []
    
    def _add_edges_to_figure(self, fig: go.Figure, edge_attributes: List[Dict[str, Any]], 
                           positions: Dict[str, Dict[str, float]]):
        """Add edges to Plotly figure"""
        try:
            edge_x = []
            edge_y = []
            edge_info = []
            
            for edge in edge_attributes:
                source = edge["source"]
                target = edge["target"]
                
                if source in positions and target in positions:
                    x0, y0 = positions[source]["x"], positions[source]["y"]
                    x1, y1 = positions[target]["x"], positions[target]["y"]
                    
                    # Add edge line
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    
                    # Store edge info for hover
                    edge_info.append({
                        "source": source,
                        "target": target,
                        "type": edge.get("relationship_type", "RELATED"),
                        "confidence": edge.get("confidence", 0.5),
                        "weight": edge.get("weight", 1.0)
                    })
            
            # Add edge trace
            if edge_x:
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='#888'),
                    hoverinfo='none',
                    mode='lines',
                    name='Edges',
                    showlegend=False
                ))
            
        except Exception as e:
            logger.error(f"Error adding edges to figure: {e}")
    
    def _add_nodes_to_figure(self, fig: go.Figure, node_attributes: Dict[str, Any], 
                           color_mapping: Dict[str, Any], positions: Dict[str, Dict[str, float]]):
        """Add nodes to Plotly figure"""
        try:
            attributes = node_attributes.get("attributes", {})
            colors = color_mapping.get("colors", {})
            
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            node_sizes = []
            node_hover = []
            
            for node_id, attr in attributes.items():
                if node_id in positions:
                    pos = positions[node_id]
                    node_x.append(pos["x"])
                    node_y.append(pos["y"])
                    
                    # Node text (labels)
                    label = attr.get("label", node_id)
                    node_text.append(label)
                    
                    # Node color
                    color = colors.get(node_id, "#gray")
                    node_colors.append(color)
                    
                    # Node size
                    size = attr.get("size", 10)
                    node_sizes.append(size)
                    
                    # Hover information
                    hover_text = f"""
                    <b>{label}</b><br>
                    ID: {node_id}<br>
                    Type: {attr.get('entity_type', 'UNKNOWN')}<br>
                    Confidence: {attr.get('confidence', 0.5):.3f}<br>
                    Degree: {attr.get('degree', 0)}<br>
                    Size: {size:.1f}
                    """.strip()
                    node_hover.append(hover_text)
            
            # Add node trace
            if node_x:
                fig.add_trace(go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    marker=dict(
                        size=node_sizes,
                        color=node_colors,
                        line=dict(width=1, color='white'),
                        opacity=0.8
                    ),
                    text=node_text,
                    textposition="middle center",
                    textfont=dict(size=8, color="white"),
                    hovertext=node_hover,
                    hoverinfo='text',
                    name='Nodes',
                    showlegend=False
                ))
            
        except Exception as e:
            logger.error(f"Error adding nodes to figure: {e}")
    
    def _update_figure_layout(self, fig: go.Figure, config: Dict[str, Any], 
                            layout_data: Dict[str, Any]):
        """Update figure layout and styling"""
        try:
            layout_type = layout_data.get("layout_type", "spring")
            interactive = config.get("interactive", True)
            show_labels = config.get("show_labels", True)
            
            fig.update_layout(
                title={
                    'text': f"Graph Visualization ({layout_type} layout)",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16}
                },
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text=f"Layout: {layout_type} | Nodes: {len(layout_data.get('positions', {}))}",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="gray", size=10)
                    )
                ],
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False
                ),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # Configure interactivity
            if interactive:
                fig.update_layout(
                    dragmode='pan',
                    newshape=dict(line_color="cyan"),
                    hovermode='closest'
                )
            else:
                fig.update_layout(
                    dragmode=False,
                    hovermode='x'
                )
            
        except Exception as e:
            logger.error(f"Error updating figure layout: {e}")
    
    def _create_fallback_visualization(self, graph: nx.Graph, layout_data: Dict[str, Any], 
                                     config: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback visualization when Plotly is not available"""
        try:
            positions = layout_data.get("positions", {})
            
            # Create simple text-based visualization data
            viz_data = {
                "success": True,
                "fallback": True,
                "message": "Plotly not available - using fallback visualization",
                "graph_info": {
                    "nodes": len(graph.nodes),
                    "edges": len(graph.edges),
                    "layout": layout_data.get("layout_type", "unknown")
                },
                "node_positions": positions,
                "html": self._generate_fallback_html(graph, positions),
                "interactive": False
            }
            
            return viz_data
            
        except Exception as e:
            logger.error(f"Error creating fallback visualization: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_fallback_html(self, graph: nx.Graph, positions: Dict[str, Dict[str, float]]) -> str:
        """Generate simple HTML fallback visualization"""
        try:
            html = f"""
            <html>
            <head>
                <title>Graph Visualization (Fallback)</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .graph-info {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                    .node-list {{ columns: 3; margin-top: 20px; }}
                    .node {{ margin: 5px 0; }}
                </style>
            </head>
            <body>
                <h1>Graph Visualization (Fallback Mode)</h1>
                <div class="graph-info">
                    <p><strong>Nodes:</strong> {len(graph.nodes)}</p>
                    <p><strong>Edges:</strong> {len(graph.edges)}</p>
                    <p><strong>Note:</strong> Plotly not available. Install plotly for interactive visualization.</p>
                </div>
                <h2>Nodes</h2>
                <div class="node-list">
            """
            
            for node, data in graph.nodes(data=True):
                entity_type = data.get("entity_type", "UNKNOWN")
                confidence = data.get("confidence", 0.5)
                degree = graph.degree(node)
                
                html += f"""
                    <div class="node">
                        <strong>{node}</strong><br>
                        Type: {entity_type}<br>
                        Confidence: {confidence:.3f}<br>
                        Degree: {degree}
                    </div>
                """
            
            html += """
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error generating fallback HTML: {e}")
            return f"<html><body><h1>Error generating visualization: {e}</h1></body></html>"
    
    def calculate_visualization_statistics(self, graph: nx.Graph, layout_data: Dict[str, Any],
                                         node_attributes: Dict[str, Any], 
                                         edge_attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive visualization statistics"""
        try:
            positions = layout_data.get("positions", {})
            attributes = node_attributes.get("attributes", {})
            
            # Basic graph statistics
            stats = {
                "graph_stats": {
                    "nodes": len(graph.nodes),
                    "edges": len(graph.edges),
                    "density": nx.density(graph),
                    "is_connected": nx.is_connected(graph),
                    "number_of_components": nx.number_connected_components(graph)
                },
                "layout_stats": {
                    "algorithm": layout_data.get("layout_type", "unknown"),
                    "positioned_nodes": len(positions),
                    "layout_bounds": layout_data.get("statistics", {}).get("bounds", {}),
                    "layout_center": layout_data.get("statistics", {}).get("center", {})
                },
                "visualization_stats": {
                    "total_visual_elements": len(attributes) + len(edge_attributes),
                    "rendered_nodes": len([n for n in attributes.keys() if n in positions]),
                    "rendered_edges": len(edge_attributes),
                    "interactive_elements": len(attributes) if self.plotly_available else 0
                }
            }
            
            # Node attribute statistics
            if attributes:
                sizes = [attr.get("size", 10) for attr in attributes.values()]
                confidences = [attr.get("confidence", 0.5) for attr in attributes.values()]
                
                stats["node_stats"] = {
                    "size_range": [min(sizes), max(sizes)],
                    "confidence_range": [min(confidences), max(confidences)],
                    "entity_types": len(set(attr.get("entity_type", "UNKNOWN") 
                                           for attr in attributes.values()))
                }
            
            # Edge attribute statistics
            if edge_attributes:
                widths = [edge.get("width", 1.0) for edge in edge_attributes]
                edge_confidences = [edge.get("confidence", 0.5) for edge in edge_attributes]
                
                stats["edge_stats"] = {
                    "width_range": [min(widths), max(widths)],
                    "confidence_range": [min(edge_confidences), max(edge_confidences)],
                    "relationship_types": len(set(edge.get("relationship_type", "RELATED") 
                                                for edge in edge_attributes))
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating visualization statistics: {e}")
            return {"error": str(e)}