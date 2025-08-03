"""
Graph Data Loader for Visualization

Loads graph data from Neo4j database for visualization with filtering and query support.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import neo4j
from neo4j import GraphDatabase

from .visualization_data_models import (
    VisualizationData, NodeData, EdgeData, OntologyInfo, 
    VisualizationMetrics, GraphVisualizationConfig, VisualizationQuery,
    DefaultColorPalette, VisualizationColorScheme
)

logger = logging.getLogger(__name__)


class GraphDataLoader:
    """Load graph data from Neo4j for visualization"""
    
    def __init__(self, driver: Optional[neo4j.Driver] = None):
        """Initialize with optional Neo4j driver"""
        self.driver = driver
        self.color_palette = DefaultColorPalette.get_default_palette()
        self.is_connected = self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test Neo4j connection"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.warning(f"Neo4j connection test failed: {e}")
            return False
    
    def fetch_graph_data(self, 
                        query: Optional[VisualizationQuery] = None,
                        config: Optional[GraphVisualizationConfig] = None) -> VisualizationData:
        """
        Fetch graph data from Neo4j with filtering options.
        
        Args:
            query: Query parameters for filtering
            config: Visualization configuration
            
        Returns:
            VisualizationData with nodes, edges, and metadata
        """
        if query is None:
            query = VisualizationQuery()
        if config is None:
            config = GraphVisualizationConfig()
        
        # Handle offline mode
        if not self.is_connected or not self.driver:
            logger.warning("No database connection - returning empty visualization data")
            return self._create_empty_visualization_data()
        
        try:
            with self.driver.session() as session:
                # Fetch nodes
                nodes = self._fetch_nodes(session, query, config)
                
                # Fetch edges
                edges = self._fetch_edges(session, query, config, nodes)
                
                # Get ontology information
                ontology_info = self._fetch_ontology_info(session, query)
                
                # Calculate metrics
                metrics = self._calculate_metrics(nodes, edges, ontology_info)
                
                return VisualizationData(
                    nodes=nodes,
                    edges=edges,
                    ontology_info=ontology_info,
                    metrics=metrics,
                    layout_positions={},  # Will be calculated by layout engine
                    metadata={
                        "query_timestamp": datetime.now().isoformat(),
                        "query_params": query.__dict__,
                        "config_params": config.to_dict()
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to fetch graph data: {e}")
            return self._create_empty_visualization_data()
    
    def _fetch_nodes(self, session: neo4j.Session, 
                    query: VisualizationQuery,
                    config: GraphVisualizationConfig) -> List[NodeData]:
        """Fetch nodes from Neo4j"""
        where_clause, params = query.to_cypher_where_clause()
        
        # Add confidence filtering if enabled
        if config.filter_low_confidence:
            if where_clause:
                where_clause += f" AND e.confidence >= {config.confidence_threshold}"
            else:
                where_clause = f"WHERE e.confidence >= {config.confidence_threshold}"
        
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
            ORDER BY e.confidence DESC
            LIMIT {config.max_nodes}
        """
        
        nodes = []
        result = session.run(node_query, params)
        
        for record in result:
            try:
                attributes = json.loads(record["attributes"]) if record["attributes"] else {}
                
                node = NodeData(
                    id=record["id"],
                    name=record["name"] or record["id"],
                    type=record["type"] or "UNKNOWN",
                    confidence=float(record["confidence"] or 0.0),
                    domain=record["domain"],
                    sources=record["sources"] or [],
                    attributes=attributes,
                    size=self._calculate_node_size(record["confidence"], config),
                    color=self._get_node_color(record, config)
                )
                nodes.append(node)
                
            except Exception as e:
                logger.warning(f"Failed to process node record: {e}")
                continue
        
        logger.info(f"Fetched {len(nodes)} nodes from database")
        return nodes
    
    def _fetch_edges(self, session: neo4j.Session,
                    query: VisualizationQuery,
                    config: GraphVisualizationConfig,
                    nodes: List[NodeData]) -> List[EdgeData]:
        """Fetch edges from Neo4j"""
        # Create set of valid node IDs for filtering
        valid_node_ids = {node.id for node in nodes}
        
        where_clause, params = query.to_cypher_where_clause()
        
        # Modify where clause for relationship queries
        where_clause = where_clause.replace('e.', 'source.')
        
        if config.filter_low_confidence:
            confidence_condition = f"source.confidence >= {config.confidence_threshold} AND target.confidence >= {config.confidence_threshold}"
            if where_clause:
                where_clause += f" AND {confidence_condition}"
            else:
                where_clause = f"WHERE {confidence_condition}"
        
        edge_query = f"""
            MATCH (source:Entity)-[r]->(target:Entity)
            {where_clause}
            RETURN source.id as source_id,
                   target.id as target_id,
                   type(r) as rel_type,
                   r.confidence as confidence,
                   r.ontology_domain as domain,
                   r.source_documents as sources,
                   r.attributes as attributes
            LIMIT {config.max_edges}
        """
        
        edges = []
        result = session.run(edge_query, params)
        
        for record in result:
            try:
                source_id = record["source_id"]
                target_id = record["target_id"]
                
                # Only include edges between nodes we have
                if source_id not in valid_node_ids or target_id not in valid_node_ids:
                    continue
                
                attributes = json.loads(record["attributes"]) if record["attributes"] else {}
                confidence = float(record["confidence"] or 0.0)
                
                edge = EdgeData(
                    source=source_id,
                    target=target_id,
                    type=record["rel_type"] or "RELATED_TO",
                    confidence=confidence,
                    domain=record["domain"],
                    sources=record["sources"] or [],
                    attributes=attributes,
                    width=self._calculate_edge_width(confidence, config),
                    color=self._get_edge_color(record["rel_type"])
                )
                edges.append(edge)
                
            except Exception as e:
                logger.warning(f"Failed to process edge record: {e}")
                continue
        
        logger.info(f"Fetched {len(edges)} edges from database")
        return edges
    
    def _fetch_ontology_info(self, session: neo4j.Session,
                           query: VisualizationQuery) -> OntologyInfo:
        """Fetch ontology information from the graph"""
        where_clause, params = query.to_cypher_where_clause()
        
        try:
            # Entity type counts
            entity_query = f"""
                MATCH (e:Entity)
                {where_clause}
                RETURN e.entity_type as type, count(e) as count
                ORDER BY count DESC
            """
            result = session.run(entity_query, params)
            entity_type_counts = {record["type"]: record["count"] for record in result}
            
            # Relationship type counts
            rel_query = f"""
                MATCH (e1:Entity)-[r]->(e2:Entity)
                {where_clause.replace('e.', 'e1.')}
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """
            result = session.run(rel_query, params)
            relationship_type_counts = {record["rel_type"]: record["count"] for record in result}
            
            # Confidence distribution
            conf_query = f"""
                MATCH (e:Entity)
                {where_clause}
                WITH CASE 
                    WHEN e.confidence >= 0.8 THEN 'High (≥0.8)'
                    WHEN e.confidence >= 0.6 THEN 'Medium (0.6-0.8)'
                    ELSE 'Low (<0.6)'
                END as conf_bucket
                RETURN conf_bucket, count(*) as count
            """
            result = session.run(conf_query, params)
            confidence_distribution = {record["conf_bucket"]: record["count"] for record in result}
            
            # Domains
            domain_query = f"""
                MATCH (e:Entity)
                {where_clause}
                WHERE e.ontology_domain IS NOT NULL
                RETURN DISTINCT e.ontology_domain as domain
            """
            result = session.run(domain_query, params)
            domains = [record["domain"] for record in result if record["domain"]]
            
            # Coverage information
            total_entity_types = len(entity_type_counts)
            total_rel_types = len(relationship_type_counts)
            
            ontology_coverage = {
                "Entity Types Used": total_entity_types,
                "Relationship Types Used": total_rel_types,
                "Total Types": total_entity_types + total_rel_types,
                "Domains": len(domains)
            }
            
            return OntologyInfo(
                entity_type_counts=entity_type_counts,
                relationship_type_counts=relationship_type_counts,
                confidence_distribution=confidence_distribution,
                ontology_coverage=ontology_coverage,
                domains=domains
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch ontology info: {e}")
            return OntologyInfo(
                entity_type_counts={},
                relationship_type_counts={},
                confidence_distribution={},
                ontology_coverage={},
                domains=[]
            )
    
    def _calculate_metrics(self, nodes: List[NodeData], edges: List[EdgeData],
                          ontology_info: OntologyInfo) -> VisualizationMetrics:
        """Calculate visualization metrics"""
        try:
            total_nodes = len(nodes)
            total_edges = len(edges)
            
            # Average confidence
            avg_confidence = np.mean([node.confidence for node in nodes]) if nodes else 0.0
            
            # Entity and relationship type counts
            entity_types = len(set(node.type for node in nodes))
            relationship_types = len(set(edge.type for edge in edges))
            
            # Graph density
            max_possible_edges = total_nodes * (total_nodes - 1) / 2 if total_nodes > 1 else 1
            graph_density = total_edges / max_possible_edges if max_possible_edges > 0 else 0
            
            return VisualizationMetrics(
                total_nodes=total_nodes,
                total_edges=total_edges,
                avg_confidence=float(avg_confidence),
                entity_types=entity_types,
                relationship_types=relationship_types,
                graph_density=float(graph_density)
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            return VisualizationMetrics(
                total_nodes=0,
                total_edges=0,
                avg_confidence=0.0,
                entity_types=0,
                relationship_types=0,
                graph_density=0.0
            )
    
    def _calculate_node_size(self, confidence: float, config: GraphVisualizationConfig) -> float:
        """Calculate node size based on confidence"""
        return max(10, confidence * config.node_size_factor)
    
    def _calculate_edge_width(self, confidence: float, config: GraphVisualizationConfig) -> float:
        """Calculate edge width based on confidence"""
        return max(1, confidence * config.edge_width_factor)
    
    def _get_node_color(self, record: Dict[str, Any], config: GraphVisualizationConfig) -> str:
        """Get color for node based on coloring scheme"""
        if config.color_by == VisualizationColorScheme.ENTITY_TYPE:
            return self.color_palette.get_entity_color(record.get("type", "UNKNOWN"))
        elif config.color_by == VisualizationColorScheme.CONFIDENCE:
            return self.color_palette.get_confidence_color(record.get("confidence", 0.0))
        elif config.color_by == VisualizationColorScheme.ONTOLOGY_DOMAIN:
            domain = record.get("domain", "unknown")
            # Hash domain name to consistent color
            import hashlib
            hash_val = int(hashlib.md5(domain.encode()).hexdigest(), 16)
            colors = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c"]
            return colors[hash_val % len(colors)]
        else:
            return self.color_palette.default_color
    
    def _get_edge_color(self, relationship_type: str) -> str:
        """Get color for edge based on relationship type"""
        return self.color_palette.get_relationship_color(relationship_type or "RELATED_TO")
    
    def _create_empty_visualization_data(self) -> VisualizationData:
        """Create empty visualization data for offline mode"""
        return VisualizationData(
            nodes=[],
            edges=[],
            ontology_info=OntologyInfo(
                entity_type_counts={},
                relationship_type_counts={},
                confidence_distribution={},
                ontology_coverage={},
                domains=[]
            ),
            metrics=VisualizationMetrics(
                total_nodes=0,
                total_edges=0,
                avg_confidence=0.0,
                entity_types=0,
                relationship_types=0,
                graph_density=0.0
            ),
            layout_positions={},
            metadata={"status": "offline_mode"}
        )
    
    def validate_data_quality(self, data: VisualizationData) -> Dict[str, Any]:
        """Validate quality of loaded graph data"""
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "quality_score": 1.0
        }
        
        try:
            # Check for empty data
            if not data.nodes:
                validation_results["warnings"].append("No nodes found in graph data")
                validation_results["quality_score"] *= 0.5
            
            if not data.edges:
                validation_results["warnings"].append("No edges found in graph data")
                validation_results["quality_score"] *= 0.7
            
            # Check for orphaned nodes
            node_ids = {node.id for node in data.nodes}
            connected_nodes = set()
            for edge in data.edges:
                connected_nodes.add(edge.source)
                connected_nodes.add(edge.target)
            
            orphaned_nodes = node_ids - connected_nodes
            if orphaned_nodes:
                validation_results["warnings"].append(
                    f"Found {len(orphaned_nodes)} orphaned nodes"
                )
                validation_results["quality_score"] *= 0.9
            
            # Check confidence levels
            low_confidence_nodes = [n for n in data.nodes if n.confidence < 0.5]
            if low_confidence_nodes:
                validation_results["warnings"].append(
                    f"Found {len(low_confidence_nodes)} nodes with low confidence (<0.5)"
                )
                validation_results["quality_score"] *= 0.95
            
            # Check for missing attributes
            nodes_missing_type = [n for n in data.nodes if not n.type or n.type == "UNKNOWN"]
            if nodes_missing_type:
                validation_results["warnings"].append(
                    f"Found {len(nodes_missing_type)} nodes with missing or unknown type"
                )
                validation_results["quality_score"] *= 0.9
            
            # Overall quality assessment
            if validation_results["quality_score"] < 0.7:
                validation_results["valid"] = False
                validation_results["errors"].append("Data quality below acceptable threshold")
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation failed: {str(e)}")
            validation_results["quality_score"] = 0.0
        
        return validation_results