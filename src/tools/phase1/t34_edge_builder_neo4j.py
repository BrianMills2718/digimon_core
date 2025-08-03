"""
T34: Edge Builder - Neo4j Version
Build graph edges and store in Neo4j
REAL IMPLEMENTATION - NO MOCKS
"""

from typing import Dict, Any, List
import logging
from datetime import datetime

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract

logger = logging.getLogger(__name__)


class T34EdgeBuilderNeo4j(BaseTool):
    """T34: Edge Builder - Uses real Neo4j for relationship storage"""
    
    def __init__(self, service_manager=None):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T34_EDGE_BUILDER"
        # Get Neo4j driver from service manager
        self.neo4j_driver = self.service_manager.get_neo4j_driver()
        if not self.neo4j_driver:
            raise RuntimeError("Neo4j driver required for T34 Edge Builder")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Edge Builder",
            description="Build graph edges from relationships and store in Neo4j",
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
                                "source_id": {"type": "string"},
                                "target_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence": {"type": "string"}
                            },
                            "required": ["source_id", "target_id", "relationship_type"]
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
                    "edges_created": {"type": "integer"},
                    "edges_updated": {"type": "integer"},
                    "total_processed": {"type": "integer"},
                    "failed_edges": {"type": "integer"}
                }
            },
            dependencies=["neo4j", "identity_service", "provenance_service"],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_RELATIONSHIPS",
                "NEO4J_ERROR",
                "ENTITY_NOT_FOUND"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute edge building with Neo4j storage"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result("INVALID_INPUT", "Input validation failed")
            
            relationships = request.input_data.get("relationships", [])
            if not relationships:
                return self._create_error_result("NO_RELATIONSHIPS", "No relationships provided")
            
            source_refs = request.input_data.get("source_refs", [])
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="build_edges",
                inputs=source_refs,
                parameters={
                    "relationship_count": len(relationships)
                }
            )
            
            # Build edges in Neo4j
            edges_created = 0
            edges_updated = 0
            failed_edges = 0
            
            with self.neo4j_driver.session() as session:
                for rel in relationships:
                    try:
                        # Handle both formats: source_id/target_id and source_entity/target_entity
                        source_id = rel.get("source_id")
                        target_id = rel.get("target_id")
                        source_entity = rel.get("source_entity")
                        target_entity = rel.get("target_entity")
                        
                        # If using entity names instead of IDs, find by canonical_name (case-insensitive)
                        if source_entity and target_entity:
                            # Try exact match first
                            check_result = session.run("""
                                MATCH (source:Entity {canonical_name: $source_entity})
                                MATCH (target:Entity {canonical_name: $target_entity})
                                RETURN source.entity_id as source, target.entity_id as target
                            """,
                            source_entity=source_entity,
                            target_entity=target_entity)
                            
                            # If no exact match, try case-insensitive match
                            if not check_result.peek():
                                check_result = session.run("""
                                    MATCH (source:Entity)
                                    WHERE toLower(source.canonical_name) = toLower($source_entity)
                                    MATCH (target:Entity)
                                    WHERE toLower(target.canonical_name) = toLower($target_entity)
                                    RETURN source.entity_id as source, target.entity_id as target
                                    LIMIT 1
                                """,
                                source_entity=source_entity,
                                target_entity=target_entity)
                        else:
                            # Use entity IDs
                            check_result = session.run("""
                                MATCH (source:Entity {entity_id: $source_id})
                                MATCH (target:Entity {entity_id: $target_id})
                                RETURN source.entity_id as source, target.entity_id as target
                            """,
                            source_id=source_id,
                            target_id=target_id)
                        
                        record = check_result.single()
                        if not record:
                            source_name = source_entity or source_id
                            target_name = target_entity or target_id
                            logger.warning(f"Entities not found for relationship: {source_name} -> {target_name}")
                            failed_edges += 1
                            continue
                        
                        # Get the actual entity IDs
                        actual_source_id = record["source"]
                        actual_target_id = record["target"]
                        
                        # Create or update relationship in Neo4j
                        result = session.run("""
                            MATCH (source:Entity {entity_id: $source_id})
                            MATCH (target:Entity {entity_id: $target_id})
                            MERGE (source)-[r:RELATES_TO {
                                source_id: $source_id,
                                target_id: $target_id
                            }]->(target)
                            ON CREATE SET 
                                r.relationship_type = $rel_type,
                                r.confidence = $confidence,
                                r.evidence = $evidence,
                                r.created_at = datetime(),
                                r.updated_at = datetime()
                            ON MATCH SET
                                r.confidence = CASE 
                                    WHEN r.confidence < $confidence 
                                    THEN $confidence 
                                    ELSE r.confidence 
                                END,
                                r.evidence = CASE
                                    WHEN r.confidence < $confidence
                                    THEN $evidence
                                    ELSE r.evidence
                                END,
                                r.updated_at = datetime()
                            RETURN r, 
                                   CASE WHEN r.created_at = r.updated_at THEN 'created' ELSE 'updated' END as action
                        """, 
                        source_id=actual_source_id,
                        target_id=actual_target_id,
                        rel_type=rel.get("relationship_type", "RELATES_TO"),
                        confidence=rel.get("confidence", 0.5),
                        evidence=rel.get("evidence", "") or rel.get("context", ""))
                        
                        record = result.single()
                        if record:
                            if record["action"] == "created":
                                edges_created += 1
                            else:
                                edges_updated += 1
                                
                            # Track quality for the edge
                            self.quality_service.assess_confidence(
                                object_ref=f"edge_{actual_source_id}_{actual_target_id}",
                                base_confidence=rel.get("confidence", 0.5),
                                factors={
                                    "extraction_method": 0.7,
                                    "evidence_strength": 0.8 if rel.get("evidence") else 0.5
                                },
                                metadata={
                                    "relationship_type": rel.get("relationship_type", "RELATES_TO"),
                                    "source": actual_source_id,
                                    "target": actual_target_id
                                }
                            )
                    
                    except Exception as e:
                        logger.error(f"Failed to create edge: {e}")
                        failed_edges += 1
            
            # Complete provenance tracking
            edge_outputs = []
            for r in relationships:
                source = r.get("source_id") or r.get("source_entity")
                target = r.get("target_id") or r.get("target_entity")
                edge_outputs.append(f"edge_{source}_{target}")
            
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=edge_outputs,
                success=True,
                metadata={
                    "edges_created": edges_created,
                    "edges_updated": edges_updated,
                    "failed_edges": failed_edges
                }
            )
            
            # Return success result
            return self._create_success_result(
                data={
                    "edges_created": edges_created,
                    "edges_updated": edges_updated,
                    "total_processed": len(relationships),
                    "failed_edges": failed_edges
                },
                metadata={
                    "operation_id": operation_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Edge building failed: {e}")
            return self._create_error_result("NEO4J_ERROR", str(e))
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        if not isinstance(input_data, dict):
            return False
        
        if "relationships" not in input_data:
            return False
        
        relationships = input_data["relationships"]
        if not isinstance(relationships, list):
            return False
        
        for rel in relationships:
            if not isinstance(rel, dict):
                return False
            # Accept either source_id/target_id or source_entity/target_entity
            has_ids = "source_id" in rel and "target_id" in rel
            has_entities = "source_entity" in rel and "target_entity" in rel
            if not (has_ids or has_entities):
                return False
        
        return True


# Test function
def test_edge_builder():
    """Test the edge builder with sample data"""
    from src.core.service_manager import get_service_manager
    
    service_manager = get_service_manager()
    builder = T34EdgeBuilderNeo4j(service_manager)
    
    # Sample relationships
    test_relationships = [
        {
            "source_id": "entity_123",
            "target_id": "entity_456",
            "relationship_type": "WORKS_WITH",
            "confidence": 0.85,
            "evidence": "They collaborated on multiple projects"
        },
        {
            "source_id": "entity_456",
            "target_id": "entity_789",
            "relationship_type": "LOCATED_IN",
            "confidence": 0.90,
            "evidence": "Office location records"
        }
    ]
    
    request = ToolRequest(
        tool_id="T34",
        operation="build_edges",
        input_data={
            "relationships": test_relationships,
            "source_refs": ["doc_123"]
        },
        parameters={}
    )
    
    result = builder.execute(request)
    
    if result.status == "success":
        print(f"✅ Created {result.data['edges_created']} edges")
        print(f"   Updated: {result.data['edges_updated']}")
        print(f"   Failed: {result.data['failed_edges']}")
    else:
        print(f"❌ Error: {result.error_message}")
    
    return result


if __name__ == "__main__":
    test_edge_builder()