"""
Dynamic Dependency Analyzer for Parallel Execution
Analyzes tool dependencies to determine which can run in parallel
"""
import logging
from typing import List, Set, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DependencyAnalysis:
    """Results of dependency analysis"""
    can_parallelize: bool
    parallel_groups: List[List[str]]
    dependency_levels: Dict[str, int]
    independent_pairs: Set[Tuple[str, str]]


class DependencyAnalyzer:
    """Analyzes tool dependencies to find parallelization opportunities"""
    
    def __init__(self):
        self.logger = logger
        
    def analyze_dependencies(self, steps: List['ToolStep']) -> DependencyAnalysis:
        """Analyze dependencies to find parallel execution opportunities"""
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(steps)
        
        # Calculate dependency levels
        levels = self._calculate_dependency_levels(steps)
        
        # Find independent tool pairs
        independent_pairs = self._find_independent_pairs(steps)
        
        # Build parallel groups
        parallel_groups = self._build_parallel_groups(steps, levels, independent_pairs)
        
        # Check if any parallelization is possible
        can_parallelize = any(len(group) > 1 for group in parallel_groups)
        
        return DependencyAnalysis(
            can_parallelize=can_parallelize,
            parallel_groups=parallel_groups,
            dependency_levels=levels,
            independent_pairs=independent_pairs
        )
    
    def _build_dependency_graph(self, steps: List['ToolStep']) -> Dict[str, Set[str]]:
        """Build a graph of tool dependencies"""
        graph = {}
        
        for step in steps:
            graph[step.tool_id] = set(step.depends_on)
        
        return graph
    
    def _calculate_dependency_levels(self, steps: List['ToolStep']) -> Dict[str, int]:
        """Calculate dependency levels (topological sort levels)"""
        levels = {}
        
        # Start with tools that have no dependencies
        current_level = 0
        remaining = {step.tool_id: set(step.depends_on) for step in steps}
        
        while remaining:
            # Find tools with no remaining dependencies
            ready = [tool_id for tool_id, deps in remaining.items() if not deps]
            
            if not ready:
                # Circular dependency detected
                logger.error(f"Circular dependency detected in: {list(remaining.keys())}")
                break
            
            # Assign level to ready tools
            for tool_id in ready:
                levels[tool_id] = current_level
                del remaining[tool_id]
            
            # Remove ready tools from dependencies
            for deps in remaining.values():
                deps.difference_update(ready)
            
            current_level += 1
        
        return levels
    
    def _find_independent_pairs(self, steps: List['ToolStep']) -> Set[Tuple[str, str]]:
        """Find all pairs of tools that can run in parallel"""
        independent_pairs = set()
        
        for i, step1 in enumerate(steps):
            for j, step2 in enumerate(steps[i+1:], i+1):
                if self._are_independent(step1, step2, steps):
                    pair = tuple(sorted([step1.tool_id, step2.tool_id]))
                    independent_pairs.add(pair)
                    logger.info(f"✅ Found independent pair: {pair}")
                else:
                    pair = tuple(sorted([step1.tool_id, step2.tool_id]))
                    logger.debug(f"❌ Not independent: {pair}")
        
        return independent_pairs
    
    def _are_independent(self, step1: 'ToolStep', step2: 'ToolStep', 
                        all_steps: List['ToolStep']) -> bool:
        """Check if two tools are independent (can run in parallel)"""
        
        # Direct dependency check
        if step1.tool_id in step2.depends_on or step2.tool_id in step1.depends_on:
            logger.debug(f"{step1.tool_id} and {step2.tool_id}: Direct dependency")
            return False
        
        # Check if they're at different dependency levels (can't run together)
        levels = self._calculate_dependency_levels(all_steps)
        if levels.get(step1.tool_id, 0) != levels.get(step2.tool_id, 0):
            logger.debug(f"{step1.tool_id} and {step2.tool_id}: Different dependency levels")
            return False
        
        # Check for shared resources or state modifications
        if self._share_mutable_state(step1, step2):
            logger.debug(f"{step1.tool_id} and {step2.tool_id}: Share mutable state")
            return False
        
        # Check transitive dependencies
        if self._have_transitive_dependency(step1, step2, all_steps):
            logger.debug(f"{step1.tool_id} and {step2.tool_id}: Transitive dependency")
            return False
        
        return True
    
    def _share_mutable_state(self, step1: 'ToolStep', step2: 'ToolStep') -> bool:
        """Check if tools share mutable state (conservative for now)"""
        
        # Tools that modify the graph shouldn't run in parallel
        graph_modifiers = {"T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"}
        if step1.tool_id in graph_modifiers and step2.tool_id in graph_modifiers:
            # Unless we know they work on different parts
            safe_pairs = {
                ("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"),  # Different graph components
            }
            pair = tuple(sorted([step1.tool_id, step2.tool_id]))
            return pair not in safe_pairs
        
        return False
    
    def _have_transitive_dependency(self, step1: 'ToolStep', step2: 'ToolStep',
                                   all_steps: List['ToolStep']) -> bool:
        """Check for transitive dependencies between tools"""
        
        # Build full dependency closure
        def get_all_dependencies(tool_id: str, steps_dict: Dict[str, 'ToolStep']) -> Set[str]:
            """Get all transitive dependencies of a tool"""
            if tool_id not in steps_dict:
                return set()
            
            visited = set()
            to_visit = set(steps_dict[tool_id].depends_on)
            
            while to_visit:
                dep = to_visit.pop()
                if dep not in visited:
                    visited.add(dep)
                    if dep in steps_dict:
                        to_visit.update(steps_dict[dep].depends_on)
            
            return visited
        
        steps_dict = {step.tool_id: step for step in all_steps}
        
        step1_all_deps = get_all_dependencies(step1.tool_id, steps_dict)
        step2_all_deps = get_all_dependencies(step2.tool_id, steps_dict)
        
        # Check if either depends on the other transitively
        return (step1.tool_id in step2_all_deps or 
                step2.tool_id in step1_all_deps)
    
    def _build_parallel_groups(self, steps: List['ToolStep'], 
                             levels: Dict[str, int],
                             independent_pairs: Set[Tuple[str, str]]) -> List[List[str]]:
        """Build groups of tools that can execute in parallel"""
        
        # Group by level first - tools must be at same level to run in parallel
        level_groups = {}
        for step in steps:
            level = levels.get(step.tool_id, 0)
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(step.tool_id)
        
        logger.debug(f"Tools grouped by dependency level: {level_groups}")
        
        # Within each level, find maximal parallel groups
        parallel_groups = []
        
        for level in sorted(level_groups.keys()):
            tools_at_level = level_groups[level]
            
            if len(tools_at_level) == 1:
                # Single tool at this level
                parallel_groups.append(tools_at_level)
            else:
                # Multiple tools at same level - check if they can parallelize
                logger.debug(f"Level {level} has {len(tools_at_level)} tools: {tools_at_level}")
                
                # Only consider pairs that are actually independent
                level_independent_pairs = set()
                for tool1, tool2 in independent_pairs:
                    if tool1 in tools_at_level and tool2 in tools_at_level:
                        level_independent_pairs.add((tool1, tool2))
                
                logger.debug(f"Independent pairs at level {level}: {level_independent_pairs}")
                
                if level_independent_pairs:
                    # Find maximal cliques of independent tools
                    groups = self._find_maximal_parallel_groups(tools_at_level, level_independent_pairs)
                    parallel_groups.extend(groups)
                else:
                    # No independent pairs, execute sequentially
                    for tool in tools_at_level:
                        parallel_groups.append([tool])
        
        return parallel_groups
    
    def _find_maximal_parallel_groups(self, tools: List[str], 
                                     independent_pairs: Set[Tuple[str, str]]) -> List[List[str]]:
        """Find maximal groups of tools that can all run in parallel"""
        
        # Build adjacency for independent tools
        adjacency = {tool: set() for tool in tools}
        
        for tool1, tool2 in independent_pairs:
            if tool1 in tools and tool2 in tools:
                adjacency[tool1].add(tool2)
                adjacency[tool2].add(tool1)
        
        # Greedy algorithm to find parallel groups
        groups = []
        unassigned = set(tools)
        
        while unassigned:
            # Start a new group
            group = []
            
            # Pick a tool with most connections
            best_tool = max(unassigned, key=lambda t: len(adjacency[t] & unassigned))
            group.append(best_tool)
            unassigned.remove(best_tool)
            
            # Add compatible tools
            candidates = adjacency[best_tool] & unassigned
            while candidates:
                # Find tool that's compatible with all in group
                for candidate in list(candidates):
                    if all(candidate in adjacency[member] for member in group):
                        group.append(candidate)
                        unassigned.remove(candidate)
                        candidates = candidates & adjacency[candidate]
                        break
                else:
                    break
            
            groups.append(group)
        
        return groups