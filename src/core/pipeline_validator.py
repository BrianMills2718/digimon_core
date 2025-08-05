"""Pipeline Contract Validation

Validates tool compatibility in pipeline before execution to prevent runtime failures.
"""

from typing import List, Dict, Any, Tuple, Optional, Union
import logging
from src.tools.base_tool import BaseTool
from src.core.tool_contract import KGASTool, get_tool_registry

logger = logging.getLogger(__name__)


class PipelineValidator:
    """Validates tool compatibility in pipeline before execution."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tool_registry = get_tool_registry()
    
    def validate_pipeline(self, tools: List[Any]) -> Tuple[bool, List[str]]:
        """Validate that tools can be connected in sequence.
        
        Args:
            tools: List of tools in pipeline order (can be tool IDs, instances, or specs)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # If all tools are strings, we can validate using known patterns
        if all(isinstance(tool, str) for tool in tools):
            # Validate tool sequence using known patterns
            for i in range(len(tools) - 1):
                source_tool = tools[i]
                target_tool = tools[i + 1]
                
                # Check output -> input compatibility
                compatibility_errors = self._check_compatibility(
                    source_tool,
                    target_tool
                )
                
                errors.extend(compatibility_errors)
            
            return len(errors) == 0, errors
        
        # Otherwise, try to resolve tools to instances
        tool_instances = []
        for tool in tools:
            instance = self._resolve_tool(tool)
            if instance is None:
                # If it's a string, use it directly for pattern matching
                if isinstance(tool, str):
                    tool_instances.append(tool)
                else:
                    errors.append(f"Could not resolve tool: {tool}")
                    continue
            else:
                tool_instances.append(instance)
        
        # If we couldn't resolve any tools, fail
        if errors and not tool_instances:
            return False, errors
        
        # Validate tool sequence
        for i in range(len(tool_instances) - 1):
            source_tool = tool_instances[i]
            target_tool = tool_instances[i + 1]
            
            # Check output -> input compatibility
            compatibility_errors = self._check_compatibility(
                source_tool,
                target_tool
            )
            
            errors.extend(compatibility_errors)
        
        return len(errors) == 0, errors
    
    def _resolve_tool(self, tool_spec: Any) -> Optional[Any]:
        """Resolve tool specification to tool instance."""
        # If already a tool instance
        if hasattr(tool_spec, 'tool_id'):
            return tool_spec
        
        # If it's a string tool ID
        if isinstance(tool_spec, str):
            # Try registry first
            tool = self.tool_registry.get_tool(tool_spec)
            if tool:
                return tool
            
            # Try to match by tool_id attribute
            for registered_tool in self.tool_registry._tools.values():
                if hasattr(registered_tool, 'tool_id') and registered_tool.tool_id == tool_spec:
                    return registered_tool
        
        # If it's a dict with tool_id
        if isinstance(tool_spec, dict) and 'tool_id' in tool_spec:
            return self._resolve_tool(tool_spec['tool_id'])
        
        return None
    
    def _check_compatibility(self, source_tool: Any, target_tool: Any) -> List[str]:
        """Check if output schema is compatible with input schema."""
        errors = []
        
        # Get tool info
        source_id = getattr(source_tool, 'tool_id', str(source_tool))
        target_id = getattr(target_tool, 'tool_id', str(target_tool))
        
        # For KGASTool interface
        if isinstance(source_tool, KGASTool) and isinstance(target_tool, KGASTool):
            try:
                output_schema = source_tool.get_output_schema()
                input_schema = target_tool.get_input_schema()
                
                return self._check_schema_compatibility(
                    source_id, output_schema,
                    target_id, input_schema
                )
            except Exception as e:
                errors.append(f"Failed to get schemas for {source_id} -> {target_id}: {e}")
        
        # For string tool IDs or legacy tools - check known patterns
        compatibility = self._check_known_tool_compatibility(source_id, target_id)
        if not compatibility['compatible']:
            errors.append(compatibility['error'])
        
        return errors
    
    def _check_schema_compatibility(self, source_id: str, output_schema: Dict, 
                                   target_id: str, input_schema: Dict) -> List[str]:
        """Check if output schema is compatible with input schema."""
        errors = []
        
        # Check required fields
        input_required = input_schema.get("required", [])
        output_properties = output_schema.get("properties", {})
        
        for field in input_required:
            if field not in output_properties:
                # Check common aliases
                if not self._check_field_aliases(field, output_properties):
                    errors.append(
                        f"{source_id} output missing required field '{field}' "
                        f"needed by {target_id}"
                    )
        
        return errors
    
    def _check_field_aliases(self, field: str, properties: Dict) -> bool:
        """Check if field exists under common aliases."""
        aliases = {
            "mentions": ["entities", "extracted_entities", "entity_mentions"],
            "entities": ["mentions", "nodes", "extracted_entities"],
            "relationships": ["edges", "relations", "extracted_relationships"],
            "text": ["content", "data", "input_text", "text_content"],
            "source_ref": ["source", "reference", "chunk_ref", "document_ref"],
            "chunks": ["text_chunks", "documents", "segments"],
            "embeddings": ["vectors", "vector_embeddings"],
        }
        
        field_aliases = aliases.get(field, [])
        return any(alias in properties for alias in field_aliases)
    
    def _check_known_tool_compatibility(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Check compatibility based on known tool patterns."""
        # Define known compatible tool sequences
        compatible_sequences = {
            # PDF processing pipeline
            ("T01_PDF_LOADER", "T15A_TEXT_CHUNKER"): True,
            ("T15A_TEXT_CHUNKER", "T23C_ONTOLOGY_AWARE_EXTRACTOR"): True,
            ("T15A_TEXT_CHUNKER", "T23A_SPACY_NER"): True,
            ("T23C_ONTOLOGY_AWARE_EXTRACTOR", "T31_ENTITY_BUILDER"): True,
            ("T23C_ONTOLOGY_AWARE_EXTRACTOR", "T34_EDGE_BUILDER"): True,
            ("T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"): True,
            ("T23A_SPACY_NER", "T31_ENTITY_BUILDER"): True,
            ("T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"): True,
            
            # Graph analysis pipeline
            ("T31_ENTITY_BUILDER", "T68_PAGERANK"): True,
            ("T34_EDGE_BUILDER", "T68_PAGERANK"): True,
            ("T68_PAGERANK", "T49_MULTIHOP_QUERY"): True,
            
            # Cross-modal conversions
            ("T68_PAGERANK", "T91_GRAPH_TABLE_EXPORTER"): True,
            ("T49_MULTIHOP_QUERY", "T91_GRAPH_TABLE_EXPORTER"): True,
            ("T91_GRAPH_TABLE_EXPORTER", "T15B_VECTOR_EMBEDDER"): True,
            
            # Phase 2 tools
            ("T31_ENTITY_BUILDER", "T50_COMMUNITY_DETECTION"): True,
            ("T34_EDGE_BUILDER", "T50_COMMUNITY_DETECTION"): True,
            ("T31_ENTITY_BUILDER", "T51_CENTRALITY_ANALYSIS"): True,
            ("T34_EDGE_BUILDER", "T51_CENTRALITY_ANALYSIS"): True,
            ("T50_COMMUNITY_DETECTION", "T54_GRAPH_VISUALIZATION"): True,
            ("T51_CENTRALITY_ANALYSIS", "T54_GRAPH_VISUALIZATION"): True,
        }
        
        # Check direct compatibility
        if (source_id, target_id) in compatible_sequences:
            return {"compatible": True}
        
        # Check incompatible patterns
        incompatible_patterns = [
            # Can't go from graph analysis back to extraction
            (r"T(49|50|51|52|53|54|55|56|57|68)", r"T(01|15A|23|27)"),
            # Can't go from table/vector back to graph without explicit conversion
            (r"T(91|15B)", r"T(31|34|49|50|51|52|53|54|55|56|57|68)"),
        ]
        
        import re
        for source_pattern, target_pattern in incompatible_patterns:
            if re.match(source_pattern, source_id) and re.match(target_pattern, target_id):
                return {
                    "compatible": False,
                    "error": f"Incompatible tool sequence: {source_id} -> {target_id}. "
                             f"Cannot go from analysis/export tools back to extraction tools."
                }
        
        # Default: assume compatible but warn
        self.logger.warning(f"Unknown tool compatibility: {source_id} -> {target_id}")
        return {"compatible": True}
    
    def validate_workflow_yaml(self, workflow_yaml: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a workflow YAML specification."""
        errors = []
        
        if 'steps' not in workflow_yaml:
            errors.append("Workflow YAML missing 'steps' section")
            return False, errors
        
        steps = workflow_yaml['steps']
        
        # Build dependency graph
        step_order = self._build_execution_order(steps)
        if isinstance(step_order, str):
            errors.append(step_order)
            return False, errors
        
        # Validate each dependency
        for i in range(len(step_order) - 1):
            current_step = next(s for s in steps if s['step_id'] == step_order[i])
            next_step = next(s for s in steps if s['step_id'] == step_order[i + 1])
            
            # Check if next_step depends on current_step
            if 'depends_on' in next_step:
                deps = next_step['depends_on']
                if isinstance(deps, str):
                    deps = [deps]
                
                if current_step['step_id'] in deps:
                    # Validate tool compatibility
                    current_tool = current_step.get('tool_id')
                    next_tool = next_step.get('tool_id')
                    
                    if current_tool and next_tool:
                        tool_errors = self._check_known_tool_compatibility(
                            current_tool, next_tool
                        )
                        if not tool_errors['compatible']:
                            errors.append(tool_errors['error'])
        
        return len(errors) == 0, errors
    
    def _build_execution_order(self, steps: List[Dict]) -> Union[List[str], str]:
        """Build execution order from dependencies."""
        try:
            # Simple topological sort
            order = []
            remaining = {s['step_id']: s for s in steps}
            
            while remaining:
                # Find steps with no remaining dependencies
                ready = []
                for step_id, step in remaining.items():
                    deps = step.get('depends_on', [])
                    if isinstance(deps, str):
                        deps = [deps]
                    
                    # Check if all dependencies are already in order
                    if all(d in order for d in deps):
                        ready.append(step_id)
                
                if not ready:
                    return "Circular dependency detected in workflow"
                
                # Add ready steps to order
                order.extend(sorted(ready))
                for step_id in ready:
                    del remaining[step_id]
            
            return order
            
        except Exception as e:
            return f"Failed to build execution order: {e}"
    
    def suggest_fixes(self, errors: List[str]) -> List[str]:
        """Suggest fixes for validation errors."""
        suggestions = []
        
        for error in errors:
            if "missing required field" in error:
                # Extract field and tools
                import re
                match = re.search(r"(\S+) output missing required field '(\w+)' needed by (\S+)", error)
                if match:
                    source_tool, field, target_tool = match.groups()
                    
                    # Suggest common fixes
                    if field == "mentions" and "T23C" in source_tool:
                        suggestions.append(
                            f"T23c now outputs both 'entities' and 'mentions'. "
                            f"Ensure T23c is configured to output mentions format."
                        )
                    elif field == "relationships" and "T23A" in source_tool:
                        suggestions.append(
                            f"T23a only extracts entities. Use T23c instead for "
                            f"combined entity + relationship extraction."
                        )
            
            elif "Incompatible tool sequence" in error:
                suggestions.append(
                    "Consider adding intermediate conversion tools. For example:\n"
                    "- Use T91_GRAPH_TABLE_EXPORTER to convert graph data to tables\n"
                    "- Use T15B_VECTOR_EMBEDDER to create embeddings from text/tables"
                )
        
        return suggestions


def validate_pipeline(tools: List[Any]) -> Tuple[bool, List[str], List[str]]:
    """Convenience function to validate a pipeline.
    
    Returns:
        Tuple of (is_valid, errors, suggestions)
    """
    validator = PipelineValidator()
    is_valid, errors = validator.validate_pipeline(tools)
    suggestions = validator.suggest_fixes(errors) if errors else []
    
    return is_valid, errors, suggestions