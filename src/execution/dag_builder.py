"""
Dynamic DAG Builder

Builds directed acyclic graphs for tool execution based on question analysis.
Creates optimal execution DAGs that respect dependencies and enable parallelization.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import networkx as nx

from ..analysis.contract_analyzer import ToolContractAnalyzer, DependencyGraph
from ..analysis.resource_conflict_analyzer import ResourceConflictAnalyzer
from .parallel_opportunity_finder import ParallelOpportunityFinder
from ..nlp.advanced_intent_classifier import QuestionIntent

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in execution DAG"""
    TOOL = "tool"
    PARALLEL_GROUP = "parallel_group"
    CONDITIONAL = "conditional"
    CHECKPOINT = "checkpoint"
    DATA_TRANSFORM = "data_transform"


@dataclass
class DAGNode:
    """Node in execution DAG"""
    node_id: str
    node_type: NodeType
    tool_id: Optional[str] = None
    parallel_tools: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_time: float = 0.0
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_parallel_group(self) -> bool:
        """Check if this node represents a parallel group"""
        return self.node_type == NodeType.PARALLEL_GROUP
    
    @property
    def execution_weight(self) -> float:
        """Get execution weight for scheduling"""
        return max(self.estimated_time, 1.0)


@dataclass
class DAGEdge:
    """Edge in execution DAG"""
    source: str
    target: str
    edge_type: str = "dependency"  # dependency, data_flow, conditional
    data_requirements: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    weight: float = 1.0


@dataclass
class ExecutionDAG:
    """Complete execution DAG with nodes and edges"""
    nodes: Dict[str, DAGNode]
    edges: List[DAGEdge]
    entry_points: List[str]  # Nodes with no dependencies
    exit_points: List[str]   # Nodes with no dependents
    critical_path: List[str] = field(default_factory=list)
    estimated_makespan: float = 0.0
    parallelization_factor: float = 1.0
    
    def get_node(self, node_id: str) -> Optional[DAGNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get dependencies for a node"""
        return [edge.source for edge in self.edges if edge.target == node_id]
    
    def get_dependents(self, node_id: str) -> List[str]:
        """Get dependents of a node"""
        return [edge.target for edge in self.edges if edge.source == node_id]
    
    def to_networkx(self) -> nx.DiGraph:
        """Convert to NetworkX graph for analysis"""
        G = nx.DiGraph()
        
        # Add nodes
        for node_id, node in self.nodes.items():
            G.add_node(node_id, 
                      node_type=node.node_type.value,
                      weight=node.execution_weight,
                      estimated_time=node.estimated_time)
        
        # Add edges
        for edge in self.edges:
            G.add_edge(edge.source, edge.target, 
                      edge_type=edge.edge_type,
                      weight=edge.weight)
        
        return G


class DynamicDAGBuilder:
    """Builds execution DAGs dynamically based on question analysis"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with analysis components"""
        self.contract_analyzer = ToolContractAnalyzer(contracts_dir)
        self.conflict_analyzer = ResourceConflictAnalyzer(contracts_dir)
        self.parallel_finder = ParallelOpportunityFinder(contracts_dir)
        self.logger = logger
        
        # Tool execution time estimates
        self.execution_times = {
            'T01_PDF_LOADER': 5.0,
            'T15A_TEXT_CHUNKER': 2.0,
            'T23A_SPACY_NER': 8.0,
            'T27_RELATIONSHIP_EXTRACTOR': 10.0,
            'T31_ENTITY_BUILDER': 6.0,
            'T34_EDGE_BUILDER': 4.0,
            'T68_PAGE_RANK': 15.0,
            'T49_MULTI_HOP_QUERY': 3.0,
            'T85_TWITTER_EXPLORER': 20.0
        }
    
    def build_execution_dag(self, required_tools: List[str], 
                           question_intent: Optional[QuestionIntent] = None,
                           question_context: Optional[Dict[str, Any]] = None) -> ExecutionDAG:
        """Build execution DAG for required tools"""
        
        self.logger.info(f"Building execution DAG for {len(required_tools)} tools")
        
        # Build dependency graph from contracts
        dependency_graph = self.contract_analyzer.build_dependency_graph()
        
        # Filter to required tools and their dependencies
        filtered_tools = self._collect_required_dependencies(required_tools, dependency_graph)
        
        # Create DAG nodes
        nodes = self._create_dag_nodes(filtered_tools, dependency_graph, question_context)
        
        # Optimize for parallel execution
        optimized_nodes = self._optimize_for_parallelization(nodes, dependency_graph)
        
        # Create DAG edges
        edges = self._create_dag_edges(optimized_nodes, dependency_graph)
        
        # Identify entry and exit points
        entry_points, exit_points = self._identify_entry_exit_points(optimized_nodes, edges)
        
        # Build final DAG
        dag = ExecutionDAG(
            nodes=optimized_nodes,
            edges=edges,
            entry_points=entry_points,
            exit_points=exit_points
        )
        
        # Calculate critical path and performance metrics
        dag = self._calculate_critical_path(dag)
        dag = self._calculate_performance_metrics(dag)
        
        self.logger.info(f"Built DAG: {len(dag.nodes)} nodes, {len(dag.edges)} edges, "
                        f"{dag.estimated_makespan:.1f}s makespan")
        
        return dag
    
    def _collect_required_dependencies(self, required_tools: List[str], 
                                      dependency_graph: DependencyGraph) -> Set[str]:
        """Collect all required tools and their transitive dependencies"""
        collected = set()
        to_process = set(required_tools)
        
        while to_process:
            tool_id = to_process.pop()
            if tool_id in collected:
                continue
                
            collected.add(tool_id)
            
            # Add dependencies
            if tool_id in dependency_graph.edges:
                dependencies = dependency_graph.edges[tool_id]
                to_process.update(dependencies - collected)
        
        self.logger.debug(f"Collected {len(collected)} tools including dependencies")
        return collected
    
    def _create_dag_nodes(self, tools: Set[str], dependency_graph: DependencyGraph,
                         question_context: Optional[Dict[str, Any]] = None) -> Dict[str, DAGNode]:
        """Create DAG nodes for tools"""
        nodes = {}
        
        for tool_id in tools:
            # Estimate execution time
            estimated_time = self.execution_times.get(tool_id, 5.0)
            
            # Apply context-based adjustments
            if question_context:
                estimated_time = self._adjust_time_for_context(tool_id, estimated_time, question_context)
            
            # Create node
            node = DAGNode(
                node_id=tool_id,
                node_type=NodeType.TOOL,
                tool_id=tool_id,
                estimated_time=estimated_time,
                resource_requirements=self._get_resource_requirements(tool_id),
                metadata={
                    'dependency_level': dependency_graph.levels.get(tool_id, 0),
                    'original_tool': True
                }
            )
            
            nodes[tool_id] = node
        
        return nodes
    
    def _optimize_for_parallelization(self, nodes: Dict[str, DAGNode], 
                                     dependency_graph: DependencyGraph) -> Dict[str, DAGNode]:
        """Optimize DAG structure for parallel execution"""
        optimized_nodes = nodes.copy()
        
        # Group tools by dependency level
        level_groups = {}
        for node_id, node in nodes.items():
            level = node.metadata.get('dependency_level', 0)
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node_id)
        
        # Create parallel groups for levels with multiple tools
        for level, tools_at_level in level_groups.items():
            if len(tools_at_level) > 1:
                # Find parallel opportunities
                parallel_groups = self.parallel_finder.find_maximal_parallel_groups(tools_at_level)
                
                # Create parallel group nodes where beneficial
                for i, group in enumerate(parallel_groups):
                    if len(group) > 1:
                        group_id = f"parallel_group_L{level}_{i}"
                        
                        # Calculate group execution time (max of parallel tools)
                        group_time = max(nodes[tool_id].estimated_time for tool_id in group)
                        
                        # Create parallel group node
                        parallel_node = DAGNode(
                            node_id=group_id,
                            node_type=NodeType.PARALLEL_GROUP,
                            parallel_tools=group,
                            estimated_time=group_time,
                            metadata={
                                'dependency_level': level,
                                'parallel_group': True,
                                'original_tools': group
                            }
                        )
                        
                        optimized_nodes[group_id] = parallel_node
                        
                        # Remove original tool nodes from top level (they're now in the group)
                        for tool_id in group:
                            if tool_id in optimized_nodes:
                                # Keep the tool node but mark it as part of group
                                optimized_nodes[tool_id].metadata['parent_group'] = group_id
                        
                        self.logger.debug(f"Created parallel group {group_id}: {group}")
        
        return optimized_nodes
    
    def _create_dag_edges(self, nodes: Dict[str, DAGNode], 
                         dependency_graph: DependencyGraph) -> List[DAGEdge]:
        """Create edges between DAG nodes"""
        edges = []
        
        # Track which tools are in parallel groups
        tool_to_group = {}
        for node_id, node in nodes.items():
            if node.node_type == NodeType.PARALLEL_GROUP:
                for tool_id in node.parallel_tools:
                    tool_to_group[tool_id] = node_id
        
        # Create dependency edges
        for tool_id, dependencies in dependency_graph.edges.items():
            if tool_id not in nodes:
                continue
            
            # Determine the target node (tool itself or its parallel group)
            target_node = tool_to_group.get(tool_id, tool_id)
            
            for dep_id in dependencies:
                if dep_id not in nodes:
                    continue
                
                # Determine the source node (dependency itself or its parallel group)
                source_node = tool_to_group.get(dep_id, dep_id)
                
                # Don't create self-edges or duplicate edges
                if source_node == target_node:
                    continue
                
                # Check if edge already exists
                existing_edge = any(e.source == source_node and e.target == target_node 
                                  for e in edges)
                if existing_edge:
                    continue
                
                edge = DAGEdge(
                    source=source_node,
                    target=target_node,
                    edge_type="dependency",
                    data_requirements=[f"output_of_{dep_id}"],
                    weight=1.0
                )
                
                edges.append(edge)
        
        return edges
    
    def _identify_entry_exit_points(self, nodes: Dict[str, DAGNode], 
                                   edges: List[DAGEdge]) -> Tuple[List[str], List[str]]:
        """Identify entry and exit points in the DAG"""
        
        # Nodes that are targets of edges (have dependencies)
        has_dependencies = {edge.target for edge in edges}
        
        # Nodes that are sources of edges (have dependents)
        has_dependents = {edge.source for edge in edges}
        
        # Entry points: nodes with no dependencies
        entry_points = [node_id for node_id in nodes.keys() 
                       if node_id not in has_dependencies]
        
        # Exit points: nodes with no dependents
        exit_points = [node_id for node_id in nodes.keys() 
                      if node_id not in has_dependents]
        
        return entry_points, exit_points
    
    def _calculate_critical_path(self, dag: ExecutionDAG) -> ExecutionDAG:
        """Calculate critical path through the DAG"""
        
        # Convert to NetworkX for critical path calculation
        G = dag.to_networkx()
        
        if not G.nodes():
            dag.critical_path = []
            return dag
        
        try:
            # Find longest path (critical path)
            # NetworkX longest_path works on DAGs
            if nx.is_directed_acyclic_graph(G):
                critical_path = nx.dag_longest_path(G, weight='estimated_time')
                dag.critical_path = critical_path
            else:
                self.logger.warning("DAG contains cycles - using topological order")
                dag.critical_path = list(nx.topological_sort(G))
                
        except Exception as e:
            self.logger.warning(f"Could not calculate critical path: {e}")
            dag.critical_path = list(dag.entry_points)
        
        return dag
    
    def _calculate_performance_metrics(self, dag: ExecutionDAG) -> ExecutionDAG:
        """Calculate performance metrics for the DAG"""
        
        # Calculate makespan (length of critical path)
        if dag.critical_path:
            makespan = sum(dag.nodes[node_id].estimated_time 
                          for node_id in dag.critical_path 
                          if node_id in dag.nodes)
            dag.estimated_makespan = makespan
        
        # Calculate parallelization factor
        total_work = sum(node.estimated_time for node in dag.nodes.values())
        if dag.estimated_makespan > 0:
            dag.parallelization_factor = total_work / dag.estimated_makespan
        
        return dag
    
    def _adjust_time_for_context(self, tool_id: str, base_time: float, 
                                context: Dict[str, Any]) -> float:
        """Adjust execution time based on question context"""
        
        # Context-based adjustments
        multiplier = 1.0
        
        # Document size adjustments
        if 'document_size' in context:
            size = context['document_size']
            if size == 'large':
                multiplier *= 1.5
            elif size == 'small':
                multiplier *= 0.8
        
        # Complexity adjustments
        if 'complexity' in context:
            complexity = context['complexity']
            if complexity == 'high':
                multiplier *= 1.3
            elif complexity == 'low':
                multiplier *= 0.9
        
        # Tool-specific adjustments
        if tool_id == 'T68_PAGE_RANK' and context.get('graph_size') == 'small':
            multiplier *= 0.7
        
        return base_time * multiplier
    
    def _get_resource_requirements(self, tool_id: str) -> Dict[str, float]:
        """Get resource requirements for a tool"""
        
        # Basic resource requirements by tool
        requirements = {
            'T01_PDF_LOADER': {'cpu': 1.0, 'memory': 200, 'io': 2.0},
            'T15A_TEXT_CHUNKER': {'cpu': 1.0, 'memory': 100, 'io': 1.0},
            'T23A_SPACY_NER': {'cpu': 2.0, 'memory': 500, 'io': 0.5},
            'T27_RELATIONSHIP_EXTRACTOR': {'cpu': 2.0, 'memory': 300, 'io': 0.5},
            'T31_ENTITY_BUILDER': {'cpu': 1.0, 'memory': 500, 'io': 1.5},
            'T34_EDGE_BUILDER': {'cpu': 1.0, 'memory': 400, 'io': 1.5},
            'T68_PAGE_RANK': {'cpu': 4.0, 'memory': 1000, 'io': 0.5},
            'T49_MULTI_HOP_QUERY': {'cpu': 1.0, 'memory': 300, 'io': 1.0},
            'T85_TWITTER_EXPLORER': {'cpu': 2.0, 'memory': 500, 'io': 0.5}
        }
        
        return requirements.get(tool_id, {'cpu': 1.0, 'memory': 200, 'io': 1.0})
    
    def visualize_dag(self, dag: ExecutionDAG) -> str:
        """Generate text visualization of the DAG"""
        
        lines = []
        lines.append("EXECUTION DAG VISUALIZATION")
        lines.append("=" * 50)
        
        # Group nodes by dependency level
        level_groups = {}
        for node_id, node in dag.nodes.items():
            level = node.metadata.get('dependency_level', 0)
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)
        
        # Display by level
        for level in sorted(level_groups.keys()):
            lines.append(f"\nLevel {level}:")
            
            for node in level_groups[level]:
                if node.node_type == NodeType.PARALLEL_GROUP:
                    lines.append(f"  ⚡ PARALLEL: {node.parallel_tools} ({node.estimated_time:.1f}s)")
                else:
                    lines.append(f"  📋 {node.tool_id} ({node.estimated_time:.1f}s)")
        
        # Critical path
        lines.append(f"\nCritical Path: {' → '.join(dag.critical_path)}")
        lines.append(f"Estimated Makespan: {dag.estimated_makespan:.1f}s")
        lines.append(f"Parallelization Factor: {dag.parallelization_factor:.2f}x")
        
        return "\n".join(lines)
    
    def export_dag_metadata(self, dag: ExecutionDAG) -> Dict[str, Any]:
        """Export DAG metadata for analysis"""
        
        return {
            "nodes": len(dag.nodes),
            "edges": len(dag.edges),
            "entry_points": dag.entry_points,
            "exit_points": dag.exit_points,
            "critical_path": dag.critical_path,
            "estimated_makespan": dag.estimated_makespan,
            "parallelization_factor": dag.parallelization_factor,
            "parallel_groups": [
                {
                    "group_id": node_id,
                    "tools": node.parallel_tools,
                    "estimated_time": node.estimated_time
                }
                for node_id, node in dag.nodes.items()
                if node.node_type == NodeType.PARALLEL_GROUP
            ]
        }