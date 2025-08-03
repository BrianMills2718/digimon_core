"""
T34: Edge Builder - Standalone Version
Build graph edges from extracted relationships
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T34EdgeBuilderStandalone(BaseTool):
    """T34: Edge Builder - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T34_EDGE_BUILDER"
        # In-memory storage for standalone mode
        self.edge_store = {}
        self.entity_store = {}  # Reference to entities
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Edge Builder",
            description="Build graph edges from extracted relationships",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "description": "List of relationships to build edges from",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_entity_id": {"type": "string"},
                                "target_entity_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence_text": {"type": "string"}
                            }
                        }
                    },
                    "entities": {
                        "type": "array",
                        "description": "List of entities (for validation)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"}
                            }
                        }
                    },
                    "source_refs": {
                        "type": "array",
                        "description": "Source references for provenance"
                    }
                },
                "required": ["relationships"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "edge_id": {"type": "string"},
                                "source_id": {"type": "string"},
                                "target_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "weight": {"type": "number"},
                                "properties": {"type": "object"}
                            }
                        }
                    },
                    "total_edges": {"type": "integer"},
                    "edge_types": {"type": "object"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 15.0,
                "max_memory_mb": 500
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_RELATIONSHIPS",
                "BUILD_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute edge building"""
        self._start_execution()
        
        try:
            # Extract parameters
            relationships = request.input_data.get("relationships", [])
            entities = request.input_data.get("entities", [])
            source_refs = request.input_data.get("source_refs", [])
            
            # Validate input
            if not relationships:
                return self._create_error_result(
                    "NO_RELATIONSHIPS",
                    "No relationships provided"
                )
            
            # Store entities for reference
            for entity in entities:
                self.entity_store[entity["entity_id"]] = entity
            
            # Build edges
            built_edges = []
            edge_types = {}
            
            for rel in relationships:
                # Calculate edge weight from confidence
                weight = self._calculate_edge_weight(rel.get("confidence", 0.7))
                
                # Create edge
                edge_id = f"edge_{uuid.uuid4().hex[:12]}"
                edge = {
                    "edge_id": edge_id,
                    "source_id": rel["source_entity_id"],
                    "target_id": rel["target_entity_id"],
                    "relationship_type": rel["relationship_type"],
                    "weight": weight,
                    "properties": {
                        "confidence": rel.get("confidence", 0.7),
                        "evidence_text": rel.get("evidence_text", ""),
                        "extraction_method": rel.get("extraction_method", "unknown"),
                        "source_refs": source_refs,
                        "created_at": datetime.now().isoformat()
                    }
                }
                
                # Store edge
                self.edge_store[edge_id] = edge
                built_edges.append(edge)
                
                # Count edge types
                edge_type = rel["relationship_type"]
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="build_edges",
                inputs=source_refs,
                parameters={
                    "relationship_count": len(relationships)
                }
            )
            
            edge_ids = [e["edge_id"] for e in built_edges]
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=edge_ids,
                success=True,
                metadata={
                    "edge_count": len(built_edges),
                    "edge_types": edge_types
                }
            )
            
            return self._create_success_result(
                data={
                    "edges": built_edges,
                    "total_edges": len(built_edges),
                    "edge_types": edge_types
                },
                metadata={
                    "operation_id": operation_id,
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in edge building: {e}", exc_info=True)
            return self._create_error_result(
                "BUILD_FAILED",
                f"Edge building failed: {str(e)}"
            )
    
    def _calculate_edge_weight(self, confidence: float) -> float:
        """Calculate edge weight from confidence"""
        # Map confidence [0, 1] to weight [0.1, 1.0]
        # We don't want zero weights
        return max(0.1, min(1.0, confidence))
    
    def get_edge(self, edge_id: str) -> Optional[Dict]:
        """Get edge by ID (for testing)"""
        return self.edge_store.get(edge_id)
    
    def get_all_edges(self) -> List[Dict]:
        """Get all edges (for testing)"""
        return list(self.edge_store.values())
    
    def get_edges_for_entity(self, entity_id: str) -> List[Dict]:
        """Get all edges connected to an entity"""
        edges = []
        for edge in self.edge_store.values():
            if edge["source_id"] == entity_id or edge["target_id"] == entity_id:
                edges.append(edge)
        return edges


# Test function
def test_standalone_edge_builder():
    """Test the standalone edge builder"""
    builder = T34EdgeBuilderStandalone()
    print(f"✅ Edge Builder initialized: {builder.tool_id}")
    
    # Test relationships
    test_relationships = [
        {
            "source_entity_id": "entity_001",
            "target_entity_id": "entity_002",
            "relationship_type": "WORKS_FOR",
            "confidence": 0.85,
            "evidence_text": "Joe Biden works for the United States",
            "extraction_method": "pattern"
        },
        {
            "source_entity_id": "entity_001",
            "target_entity_id": "entity_003",
            "relationship_type": "LOCATED_IN",
            "confidence": 0.9,
            "evidence_text": "Joe Biden in Washington D.C.",
            "extraction_method": "pattern"
        },
        {
            "source_entity_id": "entity_004",
            "target_entity_id": "entity_005",
            "relationship_type": "CREATED",
            "confidence": 0.75,
            "evidence_text": "Bill Gates founded Microsoft",
            "extraction_method": "pattern"
        }
    ]
    
    # Test entities (for reference)
    test_entities = [
        {"entity_id": "entity_001", "canonical_name": "Joe Biden"},
        {"entity_id": "entity_002", "canonical_name": "United States"},
        {"entity_id": "entity_003", "canonical_name": "Washington D.C."},
        {"entity_id": "entity_004", "canonical_name": "Bill Gates"},
        {"entity_id": "entity_005", "canonical_name": "Microsoft"}
    ]
    
    request = ToolRequest(
        tool_id="T34",
        operation="build",
        input_data={
            "relationships": test_relationships,
            "entities": test_entities,
            "source_refs": ["doc1", "doc2"]
        }
    )
    
    result = builder.execute(request)
    print(f"Status: {result.status}")
    
    if result.status == "success":
        data = result.data
        print(f"Built {data['total_edges']} edges")
        print(f"Edge types: {data['edge_types']}")
        
        for edge in data['edges']:
            # Get entity names
            source = builder.entity_store.get(edge["source_id"], {}).get("canonical_name", edge["source_id"])
            target = builder.entity_store.get(edge["target_id"], {}).get("canonical_name", edge["target_id"])
            
            print(f"\n  {source} --[{edge['relationship_type']}]--> {target}")
            print(f"    Weight: {edge['weight']:.2f}")
            print(f"    Confidence: {edge['properties']['confidence']:.2f}")
            print(f"    Evidence: {edge['properties']['evidence_text'][:50]}...")
    else:
        print(f"Error: {result.error_message}")
    
    return builder


if __name__ == "__main__":
    test_standalone_edge_builder()