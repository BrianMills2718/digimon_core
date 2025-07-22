"""
Tool Integration Framework
Standardized way for tools to declare compatibility and auto-generate pipelines
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import importlib
import inspect

class DataFlowDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"

class CompatibilityType(Enum):
    DIRECT = "direct"           # Tool A output directly feeds Tool B input
    TRANSFORMABLE = "transformable"  # Requires data transformation
    INCOMPATIBLE = "incompatible"   # Cannot be connected

@dataclass
class DataTypeSpec:
    """Specification for a data type"""
    type_name: str
    schema_class: str
    required_attributes: List[str]
    optional_attributes: List[str]
    direction: DataFlowDirection

@dataclass  
class ToolCapability:
    """What a tool can do"""
    tool_id: str
    tool_name: str
    description: str
    input_types: List[DataTypeSpec]
    output_types: List[DataTypeSpec]
    theory_compatibility: List[str]
    performance_characteristics: Dict[str, Any]
    resource_requirements: Dict[str, Any]

@dataclass
class CompatibilityRule:
    """Rule for tool compatibility"""
    source_tool: str
    target_tool: str
    compatibility: CompatibilityType
    transformation_required: Optional[str] = None
    confidence: float = 1.0
    notes: str = ""

@dataclass
class PipelineNode:
    """Node in a generated pipeline"""
    tool_id: str
    tool_capability: ToolCapability
    inputs: List[str]
    outputs: List[str]
    position: int

@dataclass
class GeneratedPipeline:
    """Auto-generated analysis pipeline"""
    pipeline_id: str
    theory_context: str
    nodes: List[PipelineNode]
    data_flow: List[Tuple[str, str]]  # (source_node, target_node) pairs
    estimated_performance: Dict[str, Any]
    confidence_score: float

class ToolIntegrationFramework:
    """
    Framework for tool integration and pipeline generation
    """
    
    def __init__(self, capabilities_dir: str = "tool_capabilities"):
        self.capabilities_dir = Path(capabilities_dir)
        self.capabilities_dir.mkdir(exist_ok=True)
        
        # Tool registry
        self.tool_capabilities: Dict[str, ToolCapability] = {}
        self.compatibility_rules: List[CompatibilityRule] = {}
        self.data_type_registry: Dict[str, str] = {}  # type_name -> schema_class
        
        # Pipeline cache
        self.pipeline_cache: Dict[str, GeneratedPipeline] = {}
        
        # Load existing capabilities
        self._load_capabilities()
    
    def _load_capabilities(self):
        """Load tool capabilities from files"""
        if not self.capabilities_dir.exists():
            return
        
        for capability_file in self.capabilities_dir.glob("*.yaml"):
            try:
                with open(capability_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Parse capability
                capability = self._parse_capability(data)
                self.tool_capabilities[capability.tool_id] = capability
                
                # Update data type registry
                for input_type in capability.input_types:
                    self.data_type_registry[input_type.type_name] = input_type.schema_class
                for output_type in capability.output_types:
                    self.data_type_registry[output_type.type_name] = output_type.schema_class
                    
            except Exception as e:
                print(f"Warning: Could not load capability {capability_file}: {e}")
    
    def _parse_capability(self, data: Dict[str, Any]) -> ToolCapability:
        """Parse capability from YAML data"""
        
        # Parse input types
        input_types = []
        for input_spec in data.get('input_types', []):
            input_types.append(DataTypeSpec(
                type_name=input_spec['type_name'],
                schema_class=input_spec['schema_class'],
                required_attributes=input_spec.get('required_attributes', []),
                optional_attributes=input_spec.get('optional_attributes', []),
                direction=DataFlowDirection.INPUT
            ))
        
        # Parse output types
        output_types = []
        for output_spec in data.get('output_types', []):
            output_types.append(DataTypeSpec(
                type_name=output_spec['type_name'],
                schema_class=output_spec['schema_class'],
                required_attributes=output_spec.get('required_attributes', []),
                optional_attributes=output_spec.get('optional_attributes', []),
                direction=DataFlowDirection.OUTPUT
            ))
        
        return ToolCapability(
            tool_id=data['tool_id'],
            tool_name=data['tool_name'],
            description=data['description'],
            input_types=input_types,
            output_types=output_types,
            theory_compatibility=data.get('theory_compatibility', []),
            performance_characteristics=data.get('performance_characteristics', {}),
            resource_requirements=data.get('resource_requirements', {})
        )
    
    def register_tool_capability(self, capability: ToolCapability) -> bool:
        """
        Register a tool capability
        
        Args:
            capability: Tool capability specification
            
        Returns:
            True if registration successful
        """
        try:
            # Validate capability
            if not capability.tool_id:
                raise ValueError("Tool ID is required")
            
            if not capability.input_types and not capability.output_types:
                raise ValueError("Tool must have at least one input or output type")
            
            # Register capability
            self.tool_capabilities[capability.tool_id] = capability
            
            # Update data type registry
            for input_type in capability.input_types:
                self.data_type_registry[input_type.type_name] = input_type.schema_class
            for output_type in capability.output_types:
                self.data_type_registry[output_type.type_name] = output_type.schema_class
            
            # Save to file
            self._save_capability(capability)
            
            print(f"✓ Registered tool capability: {capability.tool_id}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to register capability {capability.tool_id}: {e}")
            return False
    
    def _save_capability(self, capability: ToolCapability):
        """Save capability to YAML file"""
        capability_file = self.capabilities_dir / f"{capability.tool_id}.yaml"
        
        data = {
            'tool_id': capability.tool_id,
            'tool_name': capability.tool_name,
            'description': capability.description,
            'input_types': [
                {
                    'type_name': t.type_name,
                    'schema_class': t.schema_class,
                    'required_attributes': t.required_attributes,
                    'optional_attributes': t.optional_attributes
                } for t in capability.input_types
            ],
            'output_types': [
                {
                    'type_name': t.type_name,
                    'schema_class': t.schema_class,
                    'required_attributes': t.required_attributes,
                    'optional_attributes': t.optional_attributes
                } for t in capability.output_types
            ],
            'theory_compatibility': capability.theory_compatibility,
            'performance_characteristics': capability.performance_characteristics,
            'resource_requirements': capability.resource_requirements
        }
        
        with open(capability_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def compute_compatibility_matrix(self) -> Dict[Tuple[str, str], CompatibilityRule]:
        """
        Compute compatibility matrix between all registered tools
        
        Returns:
            Compatibility matrix as (source_tool, target_tool) -> CompatibilityRule
        """
        compatibility_matrix = {}
        
        tools = list(self.tool_capabilities.keys())
        
        for source_tool in tools:
            for target_tool in tools:
                if source_tool == target_tool:
                    continue
                
                rule = self._compute_tool_compatibility(source_tool, target_tool)
                compatibility_matrix[(source_tool, target_tool)] = rule
        
        self.compatibility_rules = list(compatibility_matrix.values())
        return compatibility_matrix
    
    def _compute_tool_compatibility(self, source_tool: str, target_tool: str) -> CompatibilityRule:
        """Compute compatibility between two specific tools"""
        source_cap = self.tool_capabilities[source_tool]
        target_cap = self.tool_capabilities[target_tool]
        
        # Check for direct data type compatibility
        source_output_types = {t.type_name for t in source_cap.output_types}
        target_input_types = {t.type_name for t in target_cap.input_types}
        
        direct_matches = source_output_types.intersection(target_input_types)
        
        if direct_matches:
            return CompatibilityRule(
                source_tool=source_tool,
                target_tool=target_tool,
                compatibility=CompatibilityType.DIRECT,
                confidence=1.0,
                notes=f"Direct type matches: {direct_matches}"
            )
        
        # Check for transformable compatibility
        transformable_pairs = self._find_transformable_types(source_output_types, target_input_types)
        
        if transformable_pairs:
            return CompatibilityRule(
                source_tool=source_tool,
                target_tool=target_tool,
                compatibility=CompatibilityType.TRANSFORMABLE,
                transformation_required=f"transform_{transformable_pairs[0][0]}_to_{transformable_pairs[0][1]}",
                confidence=0.8,
                notes=f"Transformable pairs: {transformable_pairs}"
            )
        
        # No compatibility found
        return CompatibilityRule(
            source_tool=source_tool,
            target_tool=target_tool,
            compatibility=CompatibilityType.INCOMPATIBLE,
            confidence=0.0,
            notes="No compatible data types found"
        )
    
    def _find_transformable_types(self, source_types: Set[str], target_types: Set[str]) -> List[Tuple[str, str]]:
        """Find pairs of types that can be transformed between"""
        transformable = []
        
        # Define known transformations
        known_transformations = {
            ('StakeholderEntity', 'OrganizationEntity'): True,
            ('OrganizationEntity', 'StakeholderEntity'): True,
            ('Entity', 'StakeholderEntity'): True,
            ('Entity', 'OrganizationEntity'): True,
            ('Relationship', 'DependencyRelationship'): True,
            ('Graph', 'Table'): True,
            ('Table', 'Graph'): True
        }
        
        for source_type in source_types:
            for target_type in target_types:
                if (source_type, target_type) in known_transformations:
                    transformable.append((source_type, target_type))
        
        return transformable
    
    def generate_pipeline(self, theory_context: str, available_data: List[str], 
                         desired_output: str) -> Optional[GeneratedPipeline]:
        """
        Auto-generate analysis pipeline based on theory context and requirements
        
        Args:
            theory_context: Theory being analyzed (e.g., "stakeholder_theory")
            available_data: List of available data types
            desired_output: Desired output type
            
        Returns:
            Generated pipeline if possible
        """
        
        # Check cache first
        cache_key = f"{theory_context}:{','.join(sorted(available_data))}:{desired_output}"
        if cache_key in self.pipeline_cache:
            return self.pipeline_cache[cache_key]
        
        # Find tools compatible with theory
        compatible_tools = []
        for tool_id, capability in self.tool_capabilities.items():
            if theory_context in capability.theory_compatibility or not capability.theory_compatibility:
                compatible_tools.append(tool_id)
        
        if not compatible_tools:
            print(f"No tools compatible with theory: {theory_context}")
            return None
        
        # Build pipeline using graph search
        pipeline = self._build_pipeline_graph(compatible_tools, available_data, desired_output)
        
        if pipeline:
            # Cache successful pipeline
            self.pipeline_cache[cache_key] = pipeline
        
        return pipeline
    
    def _build_pipeline_graph(self, compatible_tools: List[str], available_data: List[str], 
                            desired_output: str) -> Optional[GeneratedPipeline]:
        """Build pipeline using graph search algorithm"""
        
        # Find tools that can produce desired output
        output_producers = []
        for tool_id in compatible_tools:
            capability = self.tool_capabilities[tool_id]
            for output_type in capability.output_types:
                if output_type.type_name == desired_output:
                    output_producers.append(tool_id)
        
        if not output_producers:
            print(f"No tools can produce output type: {desired_output}")
            return None
        
        # For each output producer, find path from available data
        for producer_tool in output_producers:
            path = self._find_data_path(available_data, producer_tool, compatible_tools)
            if path:
                return self._create_pipeline_from_path(path, desired_output)
        
        print(f"No valid pipeline found from {available_data} to {desired_output}")
        return None
    
    def _find_data_path(self, available_data: List[str], target_tool: str, 
                       compatible_tools: List[str]) -> Optional[List[str]]:
        """Find path from available data to target tool using BFS"""
        from collections import deque
        
        # Build adjacency list of tool connections
        tool_graph = {}
        for tool_id in compatible_tools:
            tool_graph[tool_id] = []
            
            # Find tools this one can connect to
            for other_tool in compatible_tools:
                if tool_id != other_tool:
                    rule = self._compute_tool_compatibility(tool_id, other_tool)
                    if rule.compatibility != CompatibilityType.INCOMPATIBLE:
                        tool_graph[tool_id].append(other_tool)
        
        # Find tools that can process available data
        start_tools = []
        for tool_id in compatible_tools:
            capability = self.tool_capabilities[tool_id]
            tool_input_types = {t.type_name for t in capability.input_types}
            if any(data_type in tool_input_types for data_type in available_data):
                start_tools.append(tool_id)
        
        # BFS to find path to target tool
        queue = deque([(tool, [tool]) for tool in start_tools])
        visited = set()
        
        while queue:
            current_tool, path = queue.popleft()
            
            if current_tool == target_tool:
                return path
            
            if current_tool in visited:
                continue
            
            visited.add(current_tool)
            
            for neighbor in tool_graph.get(current_tool, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def _create_pipeline_from_path(self, tool_path: List[str], desired_output: str) -> GeneratedPipeline:
        """Create pipeline object from tool path"""
        nodes = []
        data_flow = []
        
        for i, tool_id in enumerate(tool_path):
            capability = self.tool_capabilities[tool_id]
            
            # Determine inputs and outputs for this node
            if i == 0:
                # First node uses available input data
                inputs = [t.type_name for t in capability.input_types]
            else:
                # Subsequent nodes use outputs from previous node
                prev_capability = self.tool_capabilities[tool_path[i-1]]
                inputs = [t.type_name for t in prev_capability.output_types]
            
            outputs = [t.type_name for t in capability.output_types]
            
            node = PipelineNode(
                tool_id=tool_id,
                tool_capability=capability,
                inputs=inputs,
                outputs=outputs,
                position=i
            )
            nodes.append(node)
            
            # Add data flow edge
            if i > 0:
                data_flow.append((tool_path[i-1], tool_id))
        
        # Calculate estimated performance
        estimated_performance = {
            "total_steps": len(tool_path),
            "estimated_time": sum(cap.performance_characteristics.get('average_time', 1.0) 
                                for cap in [self.tool_capabilities[tool_id] for tool_id in tool_path]),
            "memory_required": max(cap.resource_requirements.get('memory_mb', 100)
                                 for cap in [self.tool_capabilities[tool_id] for tool_id in tool_path])
        }
        
        # Calculate confidence score
        confidence_score = min(0.9 ** (len(tool_path) - 1), 0.5)  # Decreases with pipeline length
        
        pipeline_id = f"auto_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return GeneratedPipeline(
            pipeline_id=pipeline_id,
            theory_context="multi_theory",
            nodes=nodes,
            data_flow=data_flow,
            estimated_performance=estimated_performance,
            confidence_score=confidence_score
        )
    
    def validate_pipeline(self, pipeline: GeneratedPipeline) -> Dict[str, Any]:
        """
        Validate a generated pipeline for correctness
        
        Args:
            pipeline: Pipeline to validate
            
        Returns:
            Validation report
        """
        issues = []
        
        # Check data flow consistency
        for source_tool, target_tool in pipeline.data_flow:
            source_node = next((n for n in pipeline.nodes if n.tool_id == source_tool), None)
            target_node = next((n for n in pipeline.nodes if n.tool_id == target_tool), None)
            
            if not source_node or not target_node:
                issues.append(f"Invalid data flow: {source_tool} -> {target_tool}")
                continue
            
            # Check type compatibility
            source_outputs = {t.type_name for t in source_node.tool_capability.output_types}
            target_inputs = {t.type_name for t in target_node.tool_capability.input_types}
            
            if not source_outputs.intersection(target_inputs):
                issues.append(f"Type mismatch: {source_tool} outputs {source_outputs}, {target_tool} needs {target_inputs}")
        
        # Check resource requirements
        total_memory = sum(node.tool_capability.resource_requirements.get('memory_mb', 100) for node in pipeline.nodes)
        if total_memory > 8000:  # 8GB limit
            issues.append(f"Pipeline requires too much memory: {total_memory}MB")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "confidence": pipeline.confidence_score,
            "estimated_performance": pipeline.estimated_performance
        }
    
    def get_framework_stats(self) -> Dict[str, Any]:
        """Get framework statistics"""
        total_rules = len(self.compatibility_rules)
        compatible_rules = sum(1 for rule in self.compatibility_rules 
                             if rule.compatibility != CompatibilityType.INCOMPATIBLE)
        
        return {
            "registered_tools": len(self.tool_capabilities),
            "data_types": len(self.data_type_registry),
            "compatibility_rules": total_rules,
            "compatible_connections": compatible_rules,
            "cached_pipelines": len(self.pipeline_cache),
            "compatibility_rate": compatible_rules / total_rules if total_rules > 0 else 0.0
        }