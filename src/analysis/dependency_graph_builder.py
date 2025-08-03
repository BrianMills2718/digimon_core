"""
Dependency Graph Builder

Builds and manages dependency graphs for tool execution planning.
Works with ToolContractAnalyzer to create executable dependency graphs.
"""

import logging
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from .contract_analyzer import ToolContractAnalyzer, DependencyGraph

logger = logging.getLogger(__name__)


@dataclass
class ExecutionLevel:
    """Represents a level in the execution hierarchy"""
    level: int
    tools: List[str]
    max_parallelism: int = 1
    estimated_time: float = 0.0


@dataclass
class ExecutionPlan:
    """Complete execution plan with levels and parallelization"""
    levels: List[ExecutionLevel]
    total_tools: int
    estimated_total_time: float
    parallelization_opportunities: int
    dependency_graph: DependencyGraph
    
    def get_tools_at_level(self, level: int) -> List[str]:
        """Get all tools at a specific dependency level"""
        if level < len(self.levels):
            return self.levels[level].tools
        return []
    
    def get_max_level(self) -> int:
        """Get maximum dependency level"""
        return len(self.levels) - 1 if self.levels else 0


class DependencyGraphBuilder:
    """Builds executable dependency graphs from tool contracts"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with tool contract analyzer"""
        self.contract_analyzer = ToolContractAnalyzer(contracts_dir)
        self.logger = logger
        self._cached_graph = None
        self._cached_execution_plan = None
    
    def build_execution_graph(self, required_tools: List[str]) -> DependencyGraph:
        """Build dependency graph for specific set of tools"""
        # Get all contracts
        all_contracts = self.contract_analyzer.get_all_contracts()
        
        # Filter to only required tools and their dependencies
        needed_contracts = {}
        self._collect_dependencies(required_tools, all_contracts, needed_contracts)
        
        # Build dependency graph
        dependency_graph = self.contract_analyzer.build_dependency_graph(needed_contracts)
        
        self.logger.info(f"Built execution graph for {len(required_tools)} tools, "
                        f"total nodes: {len(dependency_graph.nodes)}")
        
        return dependency_graph
    
    def create_execution_plan(self, required_tools: List[str]) -> ExecutionPlan:
        """Create complete execution plan with parallelization analysis"""
        # Build dependency graph
        dependency_graph = self.build_execution_graph(required_tools)
        
        # Group tools by dependency level
        levels_dict = {}
        for tool_id, level in dependency_graph.levels.items():
            if level not in levels_dict:
                levels_dict[level] = []
            levels_dict[level].append(tool_id)
        
        # Create execution levels
        execution_levels = []
        total_parallelization = 0
        
        for level_num in sorted(levels_dict.keys()):
            tools_at_level = levels_dict[level_num]
            max_parallelism = len(tools_at_level)  # Theoretical maximum
            
            if max_parallelism > 1:
                total_parallelization += max_parallelism - 1
            
            execution_level = ExecutionLevel(
                level=level_num,
                tools=tools_at_level,
                max_parallelism=max_parallelism,
                estimated_time=self._estimate_level_time(tools_at_level)
            )
            execution_levels.append(execution_level)
        
        # Calculate total estimated time
        total_time = sum(level.estimated_time for level in execution_levels)
        
        execution_plan = ExecutionPlan(
            levels=execution_levels,
            total_tools=len([tool for level in execution_levels for tool in level.tools]),
            estimated_total_time=total_time,
            parallelization_opportunities=total_parallelization,
            dependency_graph=dependency_graph
        )
        
        self.logger.info(f"Created execution plan: {len(execution_levels)} levels, "
                        f"{total_parallelization} parallelization opportunities")
        
        return execution_plan
    
    def _collect_dependencies(self, tools: List[str], all_contracts: Dict[str, Path], 
                            needed_contracts: Dict[str, Path]) -> None:
        """Recursively collect all dependencies for required tools"""
        for tool_id in tools:
            if tool_id in needed_contracts:
                continue  # Already processed
            
            if tool_id not in all_contracts:
                self.logger.warning(f"Contract not found for tool: {tool_id}")
                continue
            
            # Add this tool's contract
            needed_contracts[tool_id] = all_contracts[tool_id]
            
            # Get dependencies and recurse
            dependencies = self.contract_analyzer.extract_dependencies(str(all_contracts[tool_id]))
            if dependencies:
                self._collect_dependencies(dependencies, all_contracts, needed_contracts)
    
    def _estimate_level_time(self, tools_at_level: List[str]) -> float:
        """Estimate execution time for a level (assumes parallel execution)"""
        # This is a simplified estimation - in practice would use contract performance data
        base_time_per_tool = {
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
        
        # If tools can run in parallel, time is max of individual times
        # Otherwise, sum of times
        tool_times = [base_time_per_tool.get(tool, 5.0) for tool in tools_at_level]
        
        if len(tools_at_level) == 1:
            return tool_times[0]
        
        # Assume parallel execution - return max time
        return max(tool_times)
    
    def get_independent_tools_at_level(self, level: int, dependency_graph: DependencyGraph) -> List[List[str]]:
        """Get groups of tools that can run independently at given level"""
        tools_at_level = [tool for tool, tool_level in dependency_graph.levels.items() 
                         if tool_level == level]
        
        if len(tools_at_level) <= 1:
            return [[tool] for tool in tools_at_level]
        
        # For now, assume all tools at same level can run in parallel
        # This will be enhanced in PDA-2 with resource conflict analysis
        return [tools_at_level]
    
    def validate_execution_plan(self, execution_plan: ExecutionPlan) -> bool:
        """Validate that execution plan respects all dependencies"""
        dependency_graph = execution_plan.dependency_graph
        
        # Check that all dependencies are satisfied
        for tool_id, dependencies in dependency_graph.edges.items():
            tool_level = dependency_graph.levels[tool_id]
            
            for dep in dependencies:
                if dep not in dependency_graph.levels:
                    self.logger.error(f"Dependency {dep} not found in graph for {tool_id}")
                    return False
                
                dep_level = dependency_graph.levels[dep]
                if dep_level >= tool_level:
                    self.logger.error(f"Dependency violation: {tool_id} (level {tool_level}) "
                                    f"depends on {dep} (level {dep_level})")
                    return False
        
        self.logger.info("Execution plan validation passed")
        return True
    
    def get_cached_graph(self) -> Optional[DependencyGraph]:
        """Get cached dependency graph if available"""
        return self._cached_graph
    
    def cache_graph(self, dependency_graph: DependencyGraph) -> None:
        """Cache dependency graph for reuse"""
        self._cached_graph = dependency_graph
        self.logger.debug("Cached dependency graph")
    
    def print_execution_plan(self, execution_plan: ExecutionPlan) -> None:
        """Print human-readable execution plan"""
        print("\n" + "="*60)
        print("EXECUTION PLAN")
        print("="*60)
        print(f"Total Tools: {execution_plan.total_tools}")
        print(f"Total Levels: {len(execution_plan.levels)}")
        print(f"Estimated Time: {execution_plan.estimated_total_time:.1f}s")
        print(f"Parallelization Opportunities: {execution_plan.parallelization_opportunities}")
        print()
        
        for level in execution_plan.levels:
            print(f"Level {level.level}: {level.tools}")
            print(f"  Max Parallelism: {level.max_parallelism}")
            print(f"  Estimated Time: {level.estimated_time:.1f}s")
            print()
    
    def get_execution_order(self, execution_plan: ExecutionPlan) -> List[str]:
        """Get linear execution order respecting dependencies"""
        return execution_plan.dependency_graph.topological_order