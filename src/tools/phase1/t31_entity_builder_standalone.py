"""
T31: Entity Builder - Standalone Version
Build graph entities from extracted mentions
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
from collections import defaultdict

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T31EntityBuilderStandalone(BaseTool):
    """T31: Entity Builder - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T31_ENTITY_BUILDER"
        # In-memory storage for standalone mode
        self.entity_store = {}
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Entity Builder",
            description="Build graph entities from extracted mentions",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "description": "List of entity mentions to build from",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "source_refs": {
                        "type": "array",
                        "description": "Source references for provenance"
                    },
                    "merge_strategy": {
                        "type": "string",
                        "description": "Strategy for merging duplicate entities",
                        "enum": ["exact", "fuzzy", "type_aware"],
                        "default": "type_aware"
                    }
                },
                "required": ["entities"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "mention_count": {"type": "integer"},
                                "confidence": {"type": "number"},
                                "properties": {"type": "object"}
                            }
                        }
                    },
                    "total_entities": {"type": "integer"},
                    "merged_count": {"type": "integer"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 20.0,
                "max_memory_mb": 1000
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_ENTITIES",
                "BUILD_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity building"""
        self._start_execution()
        
        try:
            # Extract parameters
            entity_mentions = request.input_data.get("entities", [])
            source_refs = request.input_data.get("source_refs", [])
            merge_strategy = request.input_data.get("merge_strategy", "type_aware")
            
            # Validate input
            if not entity_mentions:
                return self._create_error_result(
                    "NO_ENTITIES",
                    "No entity mentions provided"
                )
            
            # Group mentions by canonical form
            entity_groups = self._group_mentions(entity_mentions, merge_strategy)
            
            # Build entities from groups
            built_entities = []
            merged_count = 0
            
            for canonical_form, mentions in entity_groups.items():
                # Determine entity type (most common among mentions)
                type_counts = defaultdict(int)
                for mention in mentions:
                    type_counts[mention["entity_type"]] += 1
                entity_type = max(type_counts, key=type_counts.get)
                
                # Calculate aggregate confidence
                total_confidence = sum(m.get("confidence", 0.8) for m in mentions)
                avg_confidence = total_confidence / len(mentions)
                
                # Boost confidence based on mention count
                if len(mentions) > 1:
                    avg_confidence = min(1.0, avg_confidence * 1.1)
                    merged_count += len(mentions) - 1
                
                # Create entity
                entity_id = f"entity_{uuid.uuid4().hex[:12]}"
                entity = {
                    "entity_id": entity_id,
                    "canonical_name": canonical_form,
                    "entity_type": entity_type,
                    "mention_count": len(mentions),
                    "confidence": avg_confidence,
                    "properties": {
                        "surface_forms": list(set(m["surface_form"] for m in mentions)),
                        "source_refs": source_refs,
                        "created_at": datetime.now().isoformat()
                    }
                }
                
                # Store in memory (simulating database)
                self.entity_store[entity_id] = entity
                built_entities.append(entity)
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="build_entities",
                inputs=source_refs,
                parameters={
                    "mention_count": len(entity_mentions),
                    "merge_strategy": merge_strategy
                }
            )
            
            entity_ids = [e["entity_id"] for e in built_entities]
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=entity_ids,
                success=True,
                metadata={
                    "entity_count": len(built_entities),
                    "merged_count": merged_count
                }
            )
            
            return self._create_success_result(
                data={
                    "entities": built_entities,
                    "total_entities": len(built_entities),
                    "merged_count": merged_count
                },
                metadata={
                    "operation_id": operation_id,
                    "merge_strategy": merge_strategy,
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in entity building: {e}", exc_info=True)
            return self._create_error_result(
                "BUILD_FAILED",
                f"Entity building failed: {str(e)}"
            )
    
    def _group_mentions(self, mentions: List[Dict], strategy: str) -> Dict[str, List[Dict]]:
        """Group mentions by canonical form based on strategy"""
        groups = defaultdict(list)
        
        for mention in mentions:
            if strategy == "exact":
                # Exact matching
                canonical = mention["surface_form"]
            elif strategy == "fuzzy":
                # Simple fuzzy matching (lowercase, strip)
                canonical = mention["surface_form"].lower().strip()
            elif strategy == "type_aware":
                # Type-aware matching
                canonical = f"{mention['entity_type']}:{mention['surface_form'].lower().strip()}"
            else:
                canonical = mention["surface_form"]
            
            groups[canonical].append(mention)
        
        # For type_aware, clean up the canonical names
        if strategy == "type_aware":
            cleaned_groups = {}
            for key, mentions in groups.items():
                # Remove the type prefix from canonical name
                if ":" in key:
                    _, name = key.split(":", 1)
                    # Use the most common surface form as canonical
                    surface_forms = [m["surface_form"] for m in mentions]
                    canonical = max(set(surface_forms), key=surface_forms.count)
                else:
                    canonical = key
                cleaned_groups[canonical] = mentions
            return cleaned_groups
        
        return dict(groups)
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity by ID (for testing)"""
        return self.entity_store.get(entity_id)
    
    def get_all_entities(self) -> List[Dict]:
        """Get all entities (for testing)"""
        return list(self.entity_store.values())


# Test function
def test_standalone_entity_builder():
    """Test the standalone entity builder"""
    builder = T31EntityBuilderStandalone()
    print(f"✅ Entity Builder initialized: {builder.tool_id}")
    
    # Test entities with duplicates
    test_entities = [
        {
            "entity_id": "mention1",
            "surface_form": "Joe Biden",
            "entity_type": "PERSON",
            "confidence": 0.9
        },
        {
            "entity_id": "mention2", 
            "surface_form": "President Biden",
            "entity_type": "PERSON",
            "confidence": 0.85
        },
        {
            "entity_id": "mention3",
            "surface_form": "Biden",
            "entity_type": "PERSON", 
            "confidence": 0.8
        },
        {
            "entity_id": "mention4",
            "surface_form": "United States",
            "entity_type": "GPE",
            "confidence": 0.95
        },
        {
            "entity_id": "mention5",
            "surface_form": "US",
            "entity_type": "GPE",
            "confidence": 0.9
        },
        {
            "entity_id": "mention6",
            "surface_form": "Microsoft",
            "entity_type": "ORG",
            "confidence": 0.92
        }
    ]
    
    request = ToolRequest(
        tool_id="T31",
        operation="build",
        input_data={
            "entities": test_entities,
            "source_refs": ["doc1", "doc2"],
            "merge_strategy": "type_aware"
        }
    )
    
    result = builder.execute(request)
    print(f"Status: {result.status}")
    
    if result.status == "success":
        data = result.data
        print(f"Built {data['total_entities']} entities from {len(test_entities)} mentions")
        print(f"Merged {data['merged_count']} duplicate mentions")
        
        for entity in data['entities']:
            print(f"\n  {entity['canonical_name']} ({entity['entity_type']})")
            print(f"    ID: {entity['entity_id']}")
            print(f"    Mentions: {entity['mention_count']}")
            print(f"    Confidence: {entity['confidence']:.2f}")
            print(f"    Surface forms: {entity['properties']['surface_forms']}")
    else:
        print(f"Error: {result.error_message}")
    
    return builder


if __name__ == "__main__":
    test_standalone_entity_builder()