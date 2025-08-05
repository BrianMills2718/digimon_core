"""
Field Adapter System

Adapts field names between tool outputs and inputs to ensure compatibility.
"""

from typing import Dict, Any, Callable, List, Optional
import logging
import copy

logger = logging.getLogger(__name__)


class FieldAdapter:
    """Adapts field names between tool outputs and inputs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adapters = self._build_adapters()
    
    def _build_adapters(self) -> Dict[str, Callable]:
        """Build adapters for known tool pairs."""
        return {
            ("T23C", "T31"): self._adapt_t23c_to_t31,
            ("T23C", "T34"): self._adapt_t23c_to_t34,
            ("T31", "T68"): self._adapt_t31_to_t68,
            ("T15A", "T23C"): self._adapt_t15a_to_t23c,
            ("T27", "T34"): self._adapt_t27_to_t34,
            # OntologyAwareExtractor class name mappings
            ("OntologyAwareExtractor", "T31"): self._adapt_ontology_extractor_to_t31,
            ("OntologyAwareExtractor", "T31EntityBuilderUnified"): self._adapt_ontology_extractor_to_t31,
            ("T31EntityBuilderUnified", "T34EdgeBuilderUnified"): self._adapt_t31_to_t34,
            # Add more as discovered
        }
    
    def adapt(self, source_tool: str, target_tool: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt data from source tool format to target tool format."""
        adapter_key = (source_tool, target_tool)
        
        if adapter_key in self.adapters:
            # Make a deep copy to avoid modifying original data
            adapted_data = copy.deepcopy(data)
            return self.adapters[adapter_key](adapted_data)
        
        # No adapter needed - return as is
        return data
    
    def _adapt_t23c_to_t31(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T23C output to T31 input."""
        # T31 expects "mentions" with "text" field
        mentions = data.get("mentions", [])
        adapted_mentions = []
        
        for mention in mentions:
            adapted_mention = {
                "mention_id": mention.get("mention_id"),
                "text": mention.get("surface_form"),  # Map surface_form -> text
                "entity_type": mention.get("entity_type"),
                "entity_id": mention.get("entity_id"),
                "confidence": mention.get("confidence"),
                "source_ref": mention.get("source_ref")
            }
            # Remove None values
            adapted_mention = {k: v for k, v in adapted_mention.items() if v is not None}
            adapted_mentions.append(adapted_mention)
        
        return {
            "mentions": adapted_mentions,
            "source_refs": data.get("source_refs", ["unknown"])
        }
    
    def _adapt_t23c_to_t34(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T23C output to T34 input."""
        # T34 expects different relationship format
        relationships = data.get("relationships", [])
        adapted_rels = []
        
        for rel in relationships:
            adapted_rel = {
                "subject": {
                    "entity_id": rel.get("source_id"),
                    "canonical_name": rel.get("head_entity"),
                    "text": rel.get("head_entity"),
                    "entity_type": rel.get("source_type", "UNKNOWN")
                },
                "object": {
                    "entity_id": rel.get("target_id"),
                    "canonical_name": rel.get("tail_entity"),
                    "text": rel.get("tail_entity"),
                    "entity_type": rel.get("target_type", "UNKNOWN")
                },
                "relationship_type": rel.get("relationship_type"),
                "confidence": rel.get("confidence", 0.8),
                "properties": rel.get("attributes", {})
            }
            adapted_rels.append(adapted_rel)
        
        return {
            "relationships": adapted_rels,
            "source_refs": data.get("source_refs", ["unknown"])
        }
    
    def _adapt_ontology_extractor_to_t31(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt OntologyAwareExtractor output to T31 input."""
        # OntologyAwareExtractor outputs "entities" but T31 expects "mentions"
        entities = data.get("entities", [])
        mentions = data.get("mentions", [])
        
        # If we have mentions, use them directly
        if mentions:
            return {
                "mentions": mentions,
                "source_refs": data.get("source_refs", [data.get("source_ref", "unknown")])
            }
        
        # Otherwise, convert entities to mentions format
        adapted_mentions = []
        for entity in entities:
            # Create mention from entity
            mention = {
                "mention_id": entity.get("mention_id") or entity.get("id"),
                "text": entity.get("surface_form") or entity.get("text"),
                "entity_type": entity.get("entity_type"),
                "entity_id": entity.get("entity_id") or entity.get("id"),
                "confidence": entity.get("confidence", 0.8),
                "source_ref": data.get("source_ref", "unknown")
            }
            adapted_mentions.append(mention)
        
        return {
            "mentions": adapted_mentions,
            "source_refs": data.get("source_refs", [data.get("source_ref", "unknown")])
        }
    
    def _adapt_t31_to_t34(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T31 output to T34 input."""
        # T31 doesn't output relationships, but T34 needs them
        # We need to get relationships from somewhere else or skip this step
        relationships = data.get("relationships", [])
        
        # If no relationships, return empty but valid structure
        if not relationships:
            logger.warning("No relationships found in T31 output for T34")
            return {
                "relationships": [],
                "source_refs": data.get("source_refs", ["unknown"])
            }
        
        return {
            "relationships": relationships,
            "source_refs": data.get("source_refs", ["unknown"])
        }
    
    def _adapt_t31_to_t68(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T31 output to T68 input."""
        # T68 (PageRank) typically needs graph_ref or can work with entities
        # This depends on the specific PageRank implementation
        return {
            "graph_ref": "neo4j://graph/main",  # Default graph reference
            "entities": data.get("entities", []),
            "entity_count": data.get("entity_count", 0)
        }
    
    def _adapt_t15a_to_t23c(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T15A (chunker) output to T23C input."""
        chunks = data.get("chunks", [])
        
        # T23C expects text and chunk_ref
        # Process chunks one at a time or aggregate
        if chunks:
            # For now, take first chunk as example
            # In practice, you'd process each chunk separately
            first_chunk = chunks[0]
            return {
                "text": first_chunk.get("text", ""),
                "chunk_ref": first_chunk.get("chunk_id", "unknown"),
                "source_ref": data.get("document_ref", "unknown")
            }
        
        return {"text": "", "chunk_ref": "unknown"}
    
    def _adapt_t27_to_t34(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T27 (relationship extractor) output to T34 input."""
        # T27 outputs relationships in a similar format to T34 expects
        # but might need minor adjustments
        relationships = data.get("relationships", [])
        
        # Ensure relationships have the expected structure
        adapted_rels = []
        for rel in relationships:
            # Check if already in correct format
            if "subject" in rel and "object" in rel:
                adapted_rels.append(rel)
            else:
                # Convert from older format if needed
                adapted_rel = {
                    "subject": {
                        "entity_id": rel.get("source_entity_id"),
                        "canonical_name": rel.get("source_text"),
                        "text": rel.get("source_text"),
                        "entity_type": rel.get("source_type", "UNKNOWN")
                    },
                    "object": {
                        "entity_id": rel.get("target_entity_id"),
                        "canonical_name": rel.get("target_text"),
                        "text": rel.get("target_text"),
                        "entity_type": rel.get("target_type", "UNKNOWN")
                    },
                    "relationship_type": rel.get("relationship_type", "RELATED_TO"),
                    "confidence": rel.get("confidence", 0.8)
                }
                adapted_rels.append(adapted_rel)
        
        return {
            "relationships": adapted_rels,
            "source_refs": data.get("source_refs", ["unknown"])
        }
    
    def get_required_adapters(self, pipeline: List[str]) -> List[tuple]:
        """Get list of required adapters for a pipeline."""
        required = []
        
        for i in range(len(pipeline) - 1):
            source = pipeline[i]
            target = pipeline[i + 1]
            
            if (source, target) in self.adapters:
                required.append((source, target))
        
        return required
    
    def create_adapter_chain(self, pipeline: List[str]) -> Callable:
        """Create a chain of adapters for a complete pipeline."""
        def adapter_chain(initial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Apply adapters through the pipeline, returning all intermediate results."""
            results = [initial_data]
            current_data = initial_data
            
            for i in range(len(pipeline) - 1):
                source = pipeline[i]
                target = pipeline[i + 1]
                
                # Apply adapter if exists
                adapted_data = self.adapt(source, target, current_data)
                results.append(adapted_data)
                current_data = adapted_data
            
            return results
        
        return adapter_chain


class AdapterValidator:
    """Validates that adapters work correctly."""
    
    def __init__(self, schema_registry):
        self.schema_registry = schema_registry
        self.adapter = FieldAdapter()
    
    def validate_adapter(self, source_tool: str, target_tool: str, 
                        sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that an adapter correctly transforms data."""
        # Get schemas
        source_schema = self.schema_registry.get_schema(source_tool)
        target_schema = self.schema_registry.get_schema(target_tool)
        
        # Apply adapter
        adapted_data = self.adapter.adapt(source_tool, target_tool, sample_data)
        
        # Validate adapted data against target schema
        validation_results = self._validate_against_schema(
            adapted_data, 
            target_schema["input"]
        )
        
        return {
            "valid": validation_results["valid"],
            "errors": validation_results.get("errors", []),
            "adapted_data": adapted_data
        }
    
    def _validate_against_schema(self, data: Dict[str, Any], 
                                schema: Dict[str, Any]) -> Dict[str, Any]:
        """Basic schema validation."""
        errors = []
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types (basic)
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if not self._check_type(value, expected_type):
                    errors.append(
                        f"Field '{field}' has wrong type. "
                        f"Expected {expected_type}, got {type(value).__name__}"
                    )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON schema type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type not in type_map:
            return True  # Unknown type, assume valid
        
        expected_python_type = type_map[expected_type]
        return isinstance(value, expected_python_type)