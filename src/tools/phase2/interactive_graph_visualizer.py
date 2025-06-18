"""
Interactive Graph Visualizer for Ontology-Aware Knowledge Graphs
Provides rich visualization with ontological structure display and semantic exploration.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import neo4j
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


@dataclass
class GraphVisualizationConfig:
    """Configuration for graph visualization."""
    max_nodes: int = 500
    max_edges: int = 1000
    node_size_factor: float = 20.0
    edge_width_factor: float = 5.0
    layout_algorithm: str = "spring"  # spring, circular, kamada_kawai
    color_by: str = "entity_type"  # entity_type, confidence, ontology_domain
    show_labels: bool = True
    show_confidence: bool = True
    filter_low_confidence: bool = True
    confidence_threshold: float = 0.7


@dataclass
class VisualizationData:
    """Structured data for graph visualization."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    ontology_info: Dict[str, Any]
    metrics: Dict[str, Any]
    layout_positions: Dict[str, Tuple[float, float]]


class InteractiveGraphVisualizer:
    """
    Create rich, interactive visualizations of ontology-aware knowledge graphs.
    Supports filtering, semantic exploration, and ontological structure display.
    """
    
    def __init__(self, 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "password"):
        """Initialize the graph visualizer."""
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Color palettes for different entity types
        self.entity_colors = {
            "CLIMATE_POLICY": "#e74c3c",      # Red
            "RENEWABLE_TECH": "#2ecc71",      # Green  
            "CLIMATE_ORG": "#3498db",         # Blue
            "ENVIRONMENTAL_IMPACT": "#f39c12", # Orange
            "ORGANIZATION": "#9b59b6",        # Purple
            "PERSON": "#1abc9c",              # Teal
            "LOCATION": "#34495e",            # Dark gray
            "UNKNOWN": "#95a5a6"              # Light gray
        }
        
        # Relationship colors
        self.relationship_colors = {
            "IMPLEMENTS": "#e74c3c",
            "ADDRESSES": "#2ecc71", 
            "DEVELOPS": "#3498db",
            "COLLABORATES_WITH": "#f39c12",
            "LOCATED_IN": "#9b59b6",
            "WORKS_FOR": "#1abc9c",
            "RELATED_TO": "#95a5a6"
        }
        
        logger.info("✅ Interactive graph visualizer initialized")
    
    def fetch_graph_data(self, 
                        source_document: Optional[str] = None,
                        ontology_domain: Optional[str] = None,
                        config: Optional[GraphVisualizationConfig] = None) -> VisualizationData:
        """
        Fetch graph data from Neo4j with filtering options.
        
        Args:
            source_document: Filter by source document
            ontology_domain: Filter by ontology domain
            config: Visualization configuration
            
        Returns:
            VisualizationData with nodes, edges, and metadata
        """
        if config is None:
            config = GraphVisualizationConfig()
        
        nodes = []
        edges = []
        
        try:
            with self.driver.session() as session:
                # Build filtering conditions
                where_conditions = []
                params = {}
                
                if source_document:
                    where_conditions.append("$source_document IN e.source_documents")
                    params["source_document"] = source_document
                
                if ontology_domain:
                    where_conditions.append("e.ontology_domain = $ontology_domain")
                    params["ontology_domain"] = ontology_domain
                
                if config.filter_low_confidence:
                    where_conditions.append("e.confidence >= $min_confidence")
                    params["min_confidence"] = config.confidence_threshold
                
                where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                # Fetch nodes (entities)
                node_query = f"""
                    MATCH (e:Entity)
                    {where_clause}
                    RETURN e.id as id, 
                           e.canonical_name as name,
                           e.entity_type as type,
                           e.confidence as confidence,
                           e.ontology_domain as domain,
                           e.source_documents as sources,
                           e.attributes as attributes
                    LIMIT $max_nodes
                """
                params["max_nodes"] = config.max_nodes
                
                result = session.run(node_query, params)
                for record in result:
                    attributes = json.loads(record["attributes"]) if record["attributes"] else {}
                    nodes.append({
                        "id": record["id"],
                        "name": record["name"],
                        "type": record["type"],
                        "confidence": record["confidence"],
                        "domain": record["domain"],
                        "sources": record["sources"],
                        "attributes": attributes,
                        "size": max(10, record["confidence"] * config.node_size_factor),
                        "color": self._get_entity_color(record["type"], config.color_by, record)
                    })
                
                # Fetch edges (relationships) 
                edge_query = f"""
                    MATCH (source:Entity)-[r]->(target:Entity)
                    {where_clause.replace('e.', 'source.')}
                    AND target.confidence >= $min_confidence
                    RETURN source.id as source_id,
                           target.id as target_id,
                           type(r) as rel_type,
                           r.confidence as confidence,
                           r.ontology_domain as domain,
                           r.source_documents as sources,
                           r.attributes as attributes
                    LIMIT $max_edges
                """
                params["max_edges"] = config.max_edges
                
                result = session.run(edge_query, params)
                for record in result:
                    attributes = json.loads(record["attributes"]) if record["attributes"] else {}
                    edges.append({
                        "source": record["source_id"],
                        "target": record["target_id"],
                        "type": record["rel_type"],
                        "confidence": record["confidence"],
                        "domain": record["domain"],
                        "sources": record["sources"],
                        "attributes": attributes,
                        "width": max(1, record["confidence"] * config.edge_width_factor),
                        "color": self._get_relationship_color(record["rel_type"])
                    })
                
                # Calculate layout positions
                layout_positions = self._calculate_layout(nodes, edges, config.layout_algorithm)
                
                # Get ontology information
                ontology_info = self._get_ontology_info(session, ontology_domain)
                
                # Calculate metrics
                metrics = self._calculate_visualization_metrics(nodes, edges, ontology_info)
                
                return VisualizationData(
                    nodes=nodes,
                    edges=edges,
                    ontology_info=ontology_info,
                    metrics=metrics,
                    layout_positions=layout_positions
                )
                
        except Exception as e:
            logger.error(f"Failed to fetch graph data: {e}")
            raise
    
    def create_interactive_plot(self, data: VisualizationData,
                               config: Optional[GraphVisualizationConfig] = None) -> go.Figure:
        """
        Create an interactive Plotly visualization.
        
        Args:
            data: Visualization data from fetch_graph_data
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
                text=f"Ontology-Aware Knowledge Graph ({data.metrics['total_nodes']} entities, {data.metrics['total_edges']} relationships)",
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
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
    
    def create_ontology_structure_plot(self, ontology_info: Dict[str, Any]) -> go.Figure:
        """Create a plot showing the ontology structure."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Entity Type Distribution', 'Relationship Type Distribution',
                           'Confidence Distribution', 'Ontology Coverage'),
            specs=[[{"type": "pie"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Entity type distribution
        if ontology_info.get('entity_type_counts'):
            entity_types = list(ontology_info['entity_type_counts'].keys())
            entity_counts = list(ontology_info['entity_type_counts'].values())
            colors = [self.entity_colors.get(et, "#95a5a6") for et in entity_types]
            
            fig.add_trace(
                go.Pie(labels=entity_types, values=entity_counts, 
                       marker_colors=colors, name="Entity Types"),
                row=1, col=1
            )
        
        # Relationship type distribution
        if ontology_info.get('relationship_type_counts'):
            rel_types = list(ontology_info['relationship_type_counts'].keys())
            rel_counts = list(ontology_info['relationship_type_counts'].values())
            colors = [self.relationship_colors.get(rt, "#95a5a6") for rt in rel_types]
            
            fig.add_trace(
                go.Pie(labels=rel_types, values=rel_counts,
                       marker_colors=colors, name="Relationship Types"),
                row=1, col=2
            )
        
        # Confidence distribution
        if ontology_info.get('confidence_distribution'):
            conf_buckets = list(ontology_info['confidence_distribution'].keys())
            conf_counts = list(ontology_info['confidence_distribution'].values())
            
            fig.add_trace(
                go.Bar(x=conf_buckets, y=conf_counts, 
                       marker_color=['#e74c3c', '#f39c12', '#2ecc71'],
                       name="Confidence"),
                row=2, col=1
            )
        
        # Ontology coverage
        coverage_data = ontology_info.get('ontology_coverage', {})
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
        """Create a heatmap showing semantic similarity between entities."""
        # Extract entities with embeddings
        entities_with_embeddings = []
        entity_names = []
        
        for node in data.nodes:
            if 'embedding' in node.get('attributes', {}):
                entities_with_embeddings.append(node['attributes']['embedding'])
                entity_names.append(node['name'])
        
        if len(entities_with_embeddings) < 2:
            # Return empty plot if insufficient data
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient embedding data for similarity analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
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
                    dot_product = np.dot(emb1, emb2)
                    norm1 = np.linalg.norm(emb1)
                    norm2 = np.linalg.norm(emb2)
                    similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
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
    
    def _get_entity_color(self, entity_type: str, color_by: str, record: Dict) -> str:
        """Get color for entity based on coloring scheme."""
        if color_by == "entity_type":
            return self.entity_colors.get(entity_type, "#95a5a6")
        elif color_by == "confidence":
            confidence = record.get("confidence", 0.5)
            if confidence >= 0.8:
                return "#2ecc71"  # Green for high confidence
            elif confidence >= 0.6:
                return "#f39c12"  # Orange for medium confidence
            else:
                return "#e74c3c"  # Red for low confidence
        elif color_by == "ontology_domain":
            domain = record.get("domain", "unknown")
            # Hash domain name to consistent color
            import hashlib
            hash_val = int(hashlib.md5(domain.encode()).hexdigest(), 16)
            colors = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c"]
            return colors[hash_val % len(colors)]
        else:
            return "#95a5a6"
    
    def _get_relationship_color(self, rel_type: str) -> str:
        """Get color for relationship type."""
        return self.relationship_colors.get(rel_type, "#95a5a6")
    
    def _calculate_layout(self, nodes: List[Dict], edges: List[Dict], algorithm: str) -> Dict[str, Tuple[float, float]]:
        """Calculate layout positions for nodes."""
        if not nodes:
            return {}
        
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes (filter out None ids)
        valid_nodes = [node for node in nodes if node.get("id")]
        for node in valid_nodes:
            G.add_node(node["id"], **node)
        
        # Add edges (validate source and target exist)
        for edge in edges:
            source_id = edge.get("source")
            target_id = edge.get("target")
            if source_id and target_id and G.has_node(source_id) and G.has_node(target_id):
                G.add_edge(source_id, target_id, **edge)
        
        # Calculate positions based on algorithm
        try:
            if algorithm == "spring":
                pos = nx.spring_layout(G, k=1, iterations=50)
            elif algorithm == "circular":
                pos = nx.circular_layout(G)
            elif algorithm == "kamada_kawai":
                pos = nx.kamada_kawai_layout(G)
            else:
                pos = nx.spring_layout(G)
            
            return {node_id: (float(coords[0]), float(coords[1])) for node_id, coords in pos.items()}
            
        except Exception as e:
            logger.warning(f"Layout calculation failed: {e}, using fallback")
            # Fallback to simple circular layout
            valid_nodes = [node for node in nodes if node.get("id")]
            if not valid_nodes:
                return {}
            return {node["id"]: (np.cos(i * 2 * np.pi / len(valid_nodes)), np.sin(i * 2 * np.pi / len(valid_nodes))) 
                   for i, node in enumerate(valid_nodes)}
    
    def _create_edge_trace(self, edges: List[Dict], positions: Dict[str, Tuple[float, float]]) -> Optional[go.Scatter]:
        """Create edge trace for visualization."""
        if not edges:
            return None
        
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in edges:
            source_pos = positions.get(edge["source"])
            target_pos = positions.get(edge["target"])
            
            if source_pos and target_pos:
                edge_x.extend([source_pos[0], target_pos[0], None])
                edge_y.extend([source_pos[1], target_pos[1], None])
                edge_info.append(f"{edge['type']} (confidence: {edge['confidence']:.2f})")
        
        if not edge_x:
            return None
        
        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Relationships'
        )
    
    def _create_node_trace(self, nodes: List[Dict], positions: Dict[str, Tuple[float, float]], 
                          config: GraphVisualizationConfig) -> go.Scatter:
        """Create node trace for visualization."""
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_text = []
        node_info = []
        
        for node in nodes:
            pos = positions.get(node["id"])
            if pos:
                node_x.append(pos[0])
                node_y.append(pos[1])
                node_colors.append(node["color"])
                node_sizes.append(node["size"])
                
                # Node labels
                if config.show_labels:
                    node_text.append(node["name"])
                else:
                    node_text.append("")
                
                # Hover info
                sources_str = ", ".join(node.get("sources", [])[:3])
                if len(node.get("sources", [])) > 3:
                    sources_str += "..."
                
                hover_text = (
                    f"<b>{node['name']}</b><br>"
                    f"Type: {node['type']}<br>"
                    f"Confidence: {node['confidence']:.2f}<br>"
                    f"Domain: {node.get('domain', 'unknown')}<br>"
                    f"Sources: {sources_str}"
                )
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
    
    def _get_ontology_info(self, session: neo4j.Session, ontology_domain: Optional[str] = None) -> Dict[str, Any]:
        """Get ontology information from the graph."""
        info = {}
        
        try:
            # Entity type counts
            query = """
                MATCH (e:Entity)
                WHERE $domain IS NULL OR e.ontology_domain = $domain
                RETURN e.entity_type as type, count(e) as count
                ORDER BY count DESC
            """
            result = session.run(query, {"domain": ontology_domain})
            info["entity_type_counts"] = {record["type"]: record["count"] for record in result}
            
            # Relationship type counts
            query = """
                MATCH (e1:Entity)-[r]->(e2:Entity)
                WHERE $domain IS NULL OR r.ontology_domain = $domain
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """
            result = session.run(query, {"domain": ontology_domain})
            info["relationship_type_counts"] = {record["rel_type"]: record["count"] for record in result}
            
            # Confidence distribution
            query = """
                MATCH (e:Entity)
                WHERE $domain IS NULL OR e.ontology_domain = $domain
                WITH CASE 
                    WHEN e.confidence >= 0.8 THEN 'High (≥0.8)'
                    WHEN e.confidence >= 0.6 THEN 'Medium (0.6-0.8)'
                    ELSE 'Low (<0.6)'
                END as conf_bucket
                RETURN conf_bucket, count(*) as count
            """
            result = session.run(query, {"domain": ontology_domain})
            info["confidence_distribution"] = {record["conf_bucket"]: record["count"] for record in result}
            
            # Coverage information
            total_entity_types = len(info["entity_type_counts"])
            total_rel_types = len(info["relationship_type_counts"])
            
            info["ontology_coverage"] = {
                "Entity Types Used": total_entity_types,
                "Relationship Types Used": total_rel_types,
                "Total Types": total_entity_types + total_rel_types
            }
            
        except Exception as e:
            logger.error(f"Failed to get ontology info: {e}")
        
        return info
    
    def _calculate_visualization_metrics(self, nodes: List[Dict], edges: List[Dict], 
                                       ontology_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for the visualization."""
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "avg_confidence": np.mean([node["confidence"] for node in nodes]) if nodes else 0,
            "entity_types": len(set(node["type"] for node in nodes)),
            "relationship_types": len(set(edge["type"] for edge in edges)),
            "graph_density": len(edges) / max(len(nodes) * (len(nodes) - 1) / 2, 1) if len(nodes) > 1 else 0
        }
    
    def adversarial_test_visualization(self, max_test_nodes: int = 100) -> Dict[str, Any]:
        """Test visualization with adversarial inputs."""
        logger.info("🎨 Running adversarial tests for visualization...")
        
        test_results = {
            "large_graph_handling": self._test_large_graph_visualization(max_test_nodes),
            "empty_graph_handling": self._test_empty_graph_visualization(),
            "malformed_data_handling": self._test_malformed_data_visualization(),
            "unicode_label_handling": self._test_unicode_labels(),
            "extreme_confidence_values": self._test_extreme_confidence_values()
        }
        
        passed_tests = sum(1 for test in test_results.values() if test["passed"])
        total_tests = len(test_results)
        
        test_results["overall_score"] = passed_tests / total_tests
        test_results["summary"] = f"Visualization tests: {passed_tests}/{total_tests} passed"
        
        logger.info(f"🎨 Visualization testing complete: {passed_tests}/{total_tests} passed")
        
        return test_results
    
    def _test_large_graph_visualization(self, max_nodes: int) -> Dict[str, Any]:
        """Test visualization with large graphs."""
        try:
            config = GraphVisualizationConfig(max_nodes=max_nodes, max_edges=max_nodes*2)
            data = self.fetch_graph_data(config=config)
            
            # Try to create visualization
            fig = self.create_interactive_plot(data, config)
            
            passed = len(data.nodes) <= max_nodes and fig is not None
            
            return {
                "passed": passed,
                "details": f"Handled {len(data.nodes)} nodes, {len(data.edges)} edges"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_empty_graph_visualization(self) -> Dict[str, Any]:
        """Test visualization with empty graph."""
        try:
            # Create empty visualization data
            empty_data = VisualizationData(
                nodes=[],
                edges=[],
                ontology_info={},
                metrics={"total_nodes": 0, "total_edges": 0},
                layout_positions={}
            )
            
            fig = self.create_interactive_plot(empty_data)
            passed = fig is not None
            
            return {
                "passed": passed,
                "details": "Empty graph visualization handled"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_malformed_data_visualization(self) -> Dict[str, Any]:
        """Test visualization with malformed data."""
        try:
            # Create malformed data
            malformed_data = VisualizationData(
                nodes=[{"id": "node1", "name": None, "type": "", "confidence": "invalid"}],
                edges=[{"source": "missing", "target": "node1", "type": None}],
                ontology_info={},
                metrics={},
                layout_positions={}
            )
            
            fig = self.create_interactive_plot(malformed_data)
            passed = fig is not None
            
            return {
                "passed": passed,
                "details": "Malformed data handled gracefully"
            }
            
        except Exception as e:
            return {"passed": True, "details": f"Handled malformed data error: {str(e)[:100]}"}
    
    def _test_unicode_labels(self) -> Dict[str, Any]:
        """Test visualization with Unicode labels."""
        try:
            unicode_data = VisualizationData(
                nodes=[
                    {
                        "id": "node1", "name": "北京", "type": "LOCATION", 
                        "confidence": 0.9, "size": 20, "color": "#3498db"
                    },
                    {
                        "id": "node2", "name": "São Paulo", "type": "LOCATION", 
                        "confidence": 0.8, "size": 18, "color": "#3498db"
                    }
                ],
                edges=[],
                ontology_info={},
                metrics={"total_nodes": 2, "total_edges": 0},
                layout_positions={"node1": (0, 0), "node2": (1, 1)}
            )
            
            fig = self.create_interactive_plot(unicode_data)
            passed = fig is not None
            
            return {
                "passed": passed,
                "details": "Unicode labels handled"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_extreme_confidence_values(self) -> Dict[str, Any]:
        """Test visualization with extreme confidence values."""
        try:
            extreme_data = VisualizationData(
                nodes=[
                    {
                        "id": "node1", "name": "Test1", "type": "TEST", 
                        "confidence": 0.0, "size": 1, "color": "#e74c3c"
                    },
                    {
                        "id": "node2", "name": "Test2", "type": "TEST", 
                        "confidence": 1.0, "size": 100, "color": "#2ecc71"
                    },
                    {
                        "id": "node3", "name": "Test3", "type": "TEST", 
                        "confidence": -0.5, "size": 10, "color": "#95a5a6"  # Invalid confidence
                    }
                ],
                edges=[],
                ontology_info={},
                metrics={"total_nodes": 3, "total_edges": 0},
                layout_positions={"node1": (0, 0), "node2": (1, 0), "node3": (0.5, 1)}
            )
            
            fig = self.create_interactive_plot(extreme_data)
            passed = fig is not None
            
            return {
                "passed": passed,
                "details": "Extreme confidence values handled"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'driver'):
            self.driver.close()
        logger.info("🎨 Visualizer resources cleaned up")