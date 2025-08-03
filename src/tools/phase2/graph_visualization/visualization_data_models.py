"""
Graph Visualization Data Models

Data structures and configurations for graph visualization components.
"""

import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class VisualizationColorScheme(Enum):
    """Color scheme options for visualization"""
    ENTITY_TYPE = "entity_type"
    CONFIDENCE = "confidence"
    ONTOLOGY_DOMAIN = "ontology_domain"


class LayoutAlgorithm(Enum):
    """Layout algorithm options"""
    SPRING = "spring"
    CIRCULAR = "circular"
    KAMADA_KAWAI = "kamada_kawai"


@dataclass
class GraphVisualizationConfig:
    """Configuration for graph visualization."""
    max_nodes: int = 500
    max_edges: int = 1000
    node_size_factor: float = 20.0
    edge_width_factor: float = 5.0
    layout_algorithm: LayoutAlgorithm = LayoutAlgorithm.SPRING
    color_by: VisualizationColorScheme = VisualizationColorScheme.ENTITY_TYPE
    show_labels: bool = True
    show_confidence: bool = True
    filter_low_confidence: bool = True
    confidence_threshold: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "max_nodes": self.max_nodes,
            "max_edges": self.max_edges,
            "node_size_factor": self.node_size_factor,
            "edge_width_factor": self.edge_width_factor,
            "layout_algorithm": self.layout_algorithm.value,
            "color_by": self.color_by.value,
            "show_labels": self.show_labels,
            "show_confidence": self.show_confidence,
            "filter_low_confidence": self.filter_low_confidence,
            "confidence_threshold": self.confidence_threshold
        }


@dataclass
class NodeData:
    """Structured data for a graph node"""
    id: str
    name: str
    type: str
    confidence: float
    domain: Optional[str] = None
    sources: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    size: Optional[float] = None
    color: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "confidence": self.confidence,
            "domain": self.domain,
            "sources": self.sources or [],
            "attributes": self.attributes or {},
            "size": self.size,
            "color": self.color
        }


@dataclass
class EdgeData:
    """Structured data for a graph edge"""
    source: str
    target: str
    type: str
    confidence: float
    domain: Optional[str] = None
    sources: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    width: Optional[float] = None
    color: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "confidence": self.confidence,
            "domain": self.domain,
            "sources": self.sources or [],
            "attributes": self.attributes or {},
            "width": self.width,
            "color": self.color
        }


@dataclass
class VisualizationMetrics:
    """Metrics for graph visualization"""
    total_nodes: int
    total_edges: int
    avg_confidence: float
    entity_types: int
    relationship_types: int
    graph_density: float
    layout_quality: Optional[float] = None
    rendering_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "avg_confidence": self.avg_confidence,
            "entity_types": self.entity_types,
            "relationship_types": self.relationship_types,
            "graph_density": self.graph_density,
            "layout_quality": self.layout_quality,
            "rendering_time": self.rendering_time
        }


@dataclass
class OntologyInfo:
    """Information about ontology structure in visualization"""
    entity_type_counts: Dict[str, int]
    relationship_type_counts: Dict[str, int]
    confidence_distribution: Dict[str, int]
    ontology_coverage: Dict[str, int]
    domains: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "entity_type_counts": self.entity_type_counts,
            "relationship_type_counts": self.relationship_type_counts,
            "confidence_distribution": self.confidence_distribution,
            "ontology_coverage": self.ontology_coverage,
            "domains": self.domains
        }


@dataclass
class VisualizationData:
    """Complete structured data for graph visualization."""
    nodes: List[NodeData]
    edges: List[EdgeData]
    ontology_info: OntologyInfo
    metrics: VisualizationMetrics
    layout_positions: Dict[str, Tuple[float, float]]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "ontology_info": self.ontology_info.to_dict(),
            "metrics": self.metrics.to_dict(),
            "layout_positions": self.layout_positions,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualizationData":
        """Create instance from dictionary"""
        nodes = [NodeData(**node_data) for node_data in data.get("nodes", [])]
        edges = [EdgeData(**edge_data) for edge_data in data.get("edges", [])]
        
        ontology_data = data.get("ontology_info", {})
        ontology_info = OntologyInfo(
            entity_type_counts=ontology_data.get("entity_type_counts", {}),
            relationship_type_counts=ontology_data.get("relationship_type_counts", {}),
            confidence_distribution=ontology_data.get("confidence_distribution", {}),
            ontology_coverage=ontology_data.get("ontology_coverage", {}),
            domains=ontology_data.get("domains", [])
        )
        
        metrics_data = data.get("metrics", {})
        metrics = VisualizationMetrics(
            total_nodes=metrics_data.get("total_nodes", 0),
            total_edges=metrics_data.get("total_edges", 0),
            avg_confidence=metrics_data.get("avg_confidence", 0.0),
            entity_types=metrics_data.get("entity_types", 0),
            relationship_types=metrics_data.get("relationship_types", 0),
            graph_density=metrics_data.get("graph_density", 0.0),
            layout_quality=metrics_data.get("layout_quality"),
            rendering_time=metrics_data.get("rendering_time")
        )
        
        return cls(
            nodes=nodes,
            edges=edges,
            ontology_info=ontology_info,
            metrics=metrics,
            layout_positions=data.get("layout_positions", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class ColorPalette:
    """Color palette for visualization elements"""
    entity_colors: Dict[str, str]
    relationship_colors: Dict[str, str]
    confidence_colors: Dict[str, str]
    default_color: str = "#95a5a6"
    
    def get_entity_color(self, entity_type: str) -> str:
        """Get color for entity type"""
        return self.entity_colors.get(entity_type, self.default_color)
    
    def get_relationship_color(self, relationship_type: str) -> str:
        """Get color for relationship type"""
        return self.relationship_colors.get(relationship_type, self.default_color)
    
    def get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence level"""
        if confidence >= 0.8:
            return self.confidence_colors.get("high", "#2ecc71")
        elif confidence >= 0.6:
            return self.confidence_colors.get("medium", "#f39c12")
        else:
            return self.confidence_colors.get("low", "#e74c3c")


class DefaultColorPalette:
    """Default color palette for graph visualization"""
    
    @staticmethod
    def get_default_palette() -> ColorPalette:
        """Get default color palette"""
        entity_colors = {
            "CLIMATE_POLICY": "#e74c3c",      # Red
            "RENEWABLE_TECH": "#2ecc71",      # Green  
            "CLIMATE_ORG": "#3498db",         # Blue
            "ENVIRONMENTAL_IMPACT": "#f39c12", # Orange
            "ORGANIZATION": "#9b59b6",        # Purple
            "PERSON": "#1abc9c",              # Teal
            "LOCATION": "#34495e",            # Dark gray
            "UNKNOWN": "#95a5a6"              # Light gray
        }
        
        relationship_colors = {
            "IMPLEMENTS": "#e74c3c",
            "ADDRESSES": "#2ecc71", 
            "DEVELOPS": "#3498db",
            "COLLABORATES_WITH": "#f39c12",
            "LOCATED_IN": "#9b59b6",
            "WORKS_FOR": "#1abc9c",
            "RELATED_TO": "#95a5a6"
        }
        
        confidence_colors = {
            "high": "#2ecc71",    # Green
            "medium": "#f39c12",  # Orange
            "low": "#e74c3c"      # Red
        }
        
        return ColorPalette(
            entity_colors=entity_colors,
            relationship_colors=relationship_colors,
            confidence_colors=confidence_colors,
            default_color="#95a5a6"
        )


@dataclass
class VisualizationQuery:
    """Query parameters for visualization data"""
    source_document: Optional[str] = None
    ontology_domain: Optional[str] = None
    entity_types: Optional[List[str]] = None
    relationship_types: Optional[List[str]] = None
    min_confidence: Optional[float] = None
    max_nodes: Optional[int] = None
    max_edges: Optional[int] = None
    
    def to_cypher_where_clause(self) -> Tuple[str, Dict[str, Any]]:
        """Convert to Cypher WHERE clause and parameters"""
        where_conditions = []
        params = {}
        
        if self.source_document:
            where_conditions.append("$source_document IN e.source_documents")
            params["source_document"] = self.source_document
        
        if self.ontology_domain:
            where_conditions.append("e.ontology_domain = $ontology_domain")
            params["ontology_domain"] = self.ontology_domain
        
        if self.entity_types:
            where_conditions.append("e.entity_type IN $entity_types")
            params["entity_types"] = self.entity_types
        
        if self.min_confidence:
            where_conditions.append("e.confidence >= $min_confidence")
            params["min_confidence"] = self.min_confidence
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        return where_clause, params


@dataclass
class LayoutQualityMetrics:
    """Metrics for assessing layout quality"""
    edge_crossing_count: int
    node_overlap_count: int
    edge_length_variance: float
    angular_resolution: float
    aspect_ratio: float
    node_distribution_uniformity: float
    
    def calculate_overall_quality(self) -> float:
        """Calculate overall layout quality score (0-1)"""
        # Normalize metrics and weight them
        crossing_score = max(0, 1 - (self.edge_crossing_count / 100))  # Penalty for crossings
        overlap_score = max(0, 1 - (self.node_overlap_count / 50))    # Penalty for overlaps
        variance_score = max(0, 1 - self.edge_length_variance)        # Penalty for high variance
        resolution_score = self.angular_resolution                    # 0-1 already
        ratio_score = min(1, max(0, 1 - abs(self.aspect_ratio - 1)))  # Penalty for extreme ratios
        uniformity_score = self.node_distribution_uniformity          # 0-1 already
        
        # Weighted average
        weights = [0.2, 0.2, 0.15, 0.15, 0.1, 0.2]
        scores = [crossing_score, overlap_score, variance_score, 
                 resolution_score, ratio_score, uniformity_score]
        
        return sum(w * s for w, s in zip(weights, scores))