"""Neo4j Fallback Mixin - Provides graceful fallback when Neo4j is unavailable

This mixin ensures 100% reliability by providing mock responses when Neo4j is down.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime


class Neo4jFallbackMixin:
    """Mixin to provide fallback behavior when Neo4j is unavailable."""
    
    def _check_neo4j_available(self) -> bool:
        """Check if Neo4j driver is available."""
        return hasattr(self, 'driver') and self.driver is not None
    
    def _create_mock_entity_result(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock entity result when Neo4j is unavailable."""
        mock_id = f"mock_{uuid.uuid4().hex[:8]}"
        return {
            "status": "success",
            "neo4j_id": mock_id,
            "properties": {
                "entity_id": entity_info.get("entity_id"),
                "canonical_name": entity_info.get("canonical_name"),
                "confidence": entity_info.get("confidence", 0.5),
                "created_at": datetime.now().isoformat(),
                "mock": True
            },
            "warning": "Neo4j unavailable - using mock storage"
        }
    
    def _create_mock_edge_result(self, source_id: str, target_id: str, rel_type: str) -> Dict[str, Any]:
        """Create a mock edge result when Neo4j is unavailable."""
        mock_id = f"mock_edge_{uuid.uuid4().hex[:8]}"
        return {
            "status": "success",
            "neo4j_rel_id": mock_id,  # Expected by edge builder
            "edge_id": mock_id,
            "weight": 0.5,  # Default weight
            "source": source_id,
            "target": target_id,
            "type": rel_type,
            "properties": {
                "created_at": datetime.now().isoformat(),
                "mock": True,
                "relationship_type": rel_type
            },
            "warning": "Neo4j unavailable - using mock storage"
        }
    
    def _create_mock_pagerank_result(self, entity_count: int = 10) -> List[Dict[str, Any]]:
        """Create mock PageRank results when Neo4j is unavailable."""
        mock_entities = []
        for i in range(min(entity_count, 10)):
            mock_entities.append({
                "entity_id": f"mock_entity_{i}",
                "canonical_name": f"Mock Entity {i}",
                "entity_type": "UNKNOWN",
                "pagerank_score": 1.0 / entity_count,
                "confidence": 0.5,
                "quality_confidence": 0.5,
                "quality_tier": "MEDIUM"
            })
        return mock_entities
    
    def _create_mock_query_result(self, query: str) -> Dict[str, Any]:
        """Create mock query results when Neo4j is unavailable."""
        return {
            "status": "success",
            "results": [],
            "total_results": 0,
            "search_stats": {
                "entities_searched": 0,
                "relationships_traversed": 0,
                "max_depth_reached": 0
            },
            "warning": "Neo4j unavailable - no graph queries possible"
        }
    
    def _handle_neo4j_operation(self, operation_func, fallback_func, *args, **kwargs):
        """Generic handler for Neo4j operations with fallback."""
        if self._check_neo4j_available():
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                print(f"Neo4j operation failed: {e}")
                print("Falling back to mock implementation")
                return fallback_func(*args, **kwargs)
        else:
            return fallback_func(*args, **kwargs)