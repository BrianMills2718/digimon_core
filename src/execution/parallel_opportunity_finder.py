"""
Parallel Opportunity Finder

Finds maximal parallel execution groups using algorithmic approaches.
Handles 2-way, 3-way, N-way parallelization for optimal resource utilization.
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

from ..analysis.contract_analyzer import DependencyGraph
from ..analysis.resource_conflict_analyzer import ResourceConflictAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ParallelGroup:
    """Group of tools that can execute in parallel"""
    tools: List[str]
    level: int
    estimated_speedup: float = 1.0
    resource_conflicts: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    
    @property
    def size(self) -> int:
        """Number of tools in the group"""
        return len(self.tools)
    
    @property
    def is_parallel(self) -> bool:
        """Whether this group enables parallelization"""
        return self.size > 1


@dataclass
class ExecutionPlan:
    """Optimized execution plan with parallel groups"""
    parallel_groups: List[ParallelGroup]
    total_tools: int
    total_levels: int
    estimated_total_time: float
    estimated_speedup: float
    parallelization_ratio: float  # Fraction of tools that can run in parallel
    
    def get_groups_at_level(self, level: int) -> List[ParallelGroup]:
        """Get all parallel groups at a specific level"""
        return [group for group in self.parallel_groups if group.level == level]
    
    def get_total_parallel_opportunities(self) -> int:
        """Count total tools that benefit from parallelization"""
        return sum(group.size for group in self.parallel_groups if group.is_parallel)


class ParallelOpportunityFinder:
    """Finds optimal parallel execution opportunities using algorithmic approaches"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with resource conflict analyzer"""
        self.conflict_analyzer = ResourceConflictAnalyzer(contracts_dir)
        self.logger = logger
        
        # Tool execution time estimates (in seconds)
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
    
    def find_maximal_parallel_groups(self, tools_at_level: List[str]) -> List[List[str]]:
        """Find largest groups that can run together using maximal clique algorithm"""
        if len(tools_at_level) <= 1:
            return [[tool] for tool in tools_at_level]
        
        # Build compatibility graph (adjacency list)
        compatibility_graph = self._build_compatibility_graph(tools_at_level)
        
        # Find maximal cliques (groups where all tools are pairwise compatible)
        maximal_cliques = self._find_maximal_cliques(compatibility_graph)
        
        # Convert back to optimal parallel groups
        parallel_groups = self._optimize_clique_selection(maximal_cliques, tools_at_level)
        
        self.logger.debug(f"Found {len(parallel_groups)} parallel groups for {len(tools_at_level)} tools")
        
        return parallel_groups
    
    def _build_compatibility_graph(self, tools: List[str]) -> Dict[str, Set[str]]:
        """Build graph where edges connect compatible (non-conflicting) tools"""
        graph = {tool: set() for tool in tools}
        
        # Check all pairs for compatibility
        for i, tool1 in enumerate(tools):
            for tool2 in tools[i+1:]:
                if self.conflict_analyzer.can_run_in_parallel(tool1, tool2):
                    graph[tool1].add(tool2)
                    graph[tool2].add(tool1)
                    self.logger.debug(f"Compatible: {tool1} <-> {tool2}")
                else:
                    self.logger.debug(f"Incompatible: {tool1} <-> {tool2}")
        
        return graph
    
    def _find_maximal_cliques(self, graph: Dict[str, Set[str]]) -> List[Set[str]]:
        """Find all maximal cliques using Bron-Kerbosch algorithm"""
        cliques = []
        
        def bron_kerbosch(current_clique: Set[str], candidates: Set[str], excluded: Set[str]):
            """Recursive Bron-Kerbosch algorithm for maximal clique finding"""
            if not candidates and not excluded:
                # Found a maximal clique
                if current_clique:
                    cliques.append(current_clique.copy())
                return
            
            # Try adding each candidate to the clique
            for vertex in list(candidates):
                neighbors = graph[vertex]
                
                # Recursive call with vertex added to clique
                bron_kerbosch(
                    current_clique | {vertex},
                    candidates & neighbors,
                    excluded & neighbors
                )
                
                # Move vertex from candidates to excluded
                candidates.remove(vertex)
                excluded.add(vertex)
        
        # Start algorithm
        all_vertices = set(graph.keys())
        bron_kerbosch(set(), all_vertices, set())
        
        self.logger.debug(f"Found {len(cliques)} maximal cliques")
        return cliques
    
    def _optimize_clique_selection(self, cliques: List[Set[str]], all_tools: List[str]) -> List[List[str]]:
        """Select optimal set of non-overlapping cliques to maximize parallelization"""
        if not cliques:
            return [[tool] for tool in all_tools]
        
        # Sort cliques by size (prefer larger groups)
        cliques_sorted = sorted(cliques, key=len, reverse=True)
        
        # Greedy selection of non-overlapping cliques
        selected_groups = []
        covered_tools = set()
        
        for clique in cliques_sorted:
            # Check if this clique overlaps with already selected tools
            if not (clique & covered_tools):
                selected_groups.append(list(clique))
                covered_tools.update(clique)
        
        # Add remaining tools as singleton groups
        remaining_tools = set(all_tools) - covered_tools
        for tool in remaining_tools:
            selected_groups.append([tool])
        
        self.logger.debug(f"Selected {len(selected_groups)} optimal parallel groups")
        return selected_groups
    
    def optimize_execution_plan(self, dependency_graph: DependencyGraph) -> ExecutionPlan:
        """Generate optimal parallel execution plan minimizing total time"""
        # Group tools by dependency level
        levels_dict = {}
        for tool_id, level in dependency_graph.levels.items():
            if level not in levels_dict:
                levels_dict[level] = []
            levels_dict[level].append(tool_id)
        
        # Find parallel groups for each level
        parallel_groups = []
        total_sequential_time = 0.0
        total_parallel_time = 0.0
        
        for level_num in sorted(levels_dict.keys()):
            tools_at_level = levels_dict[level_num]
            
            if len(tools_at_level) == 1:
                # Single tool - no parallelization possible
                tool = tools_at_level[0]
                execution_time = self.execution_times.get(tool, 5.0)
                
                group = ParallelGroup(
                    tools=[tool],
                    level=level_num,
                    estimated_speedup=1.0,
                    execution_time=execution_time
                )
                parallel_groups.append(group)
                
                total_sequential_time += execution_time
                total_parallel_time += execution_time
                
            else:
                # Multiple tools - find optimal parallel groups
                optimal_groups = self.find_maximal_parallel_groups(tools_at_level)
                
                level_sequential_time = sum(self.execution_times.get(tool, 5.0) for tool in tools_at_level)
                level_parallel_time = 0.0
                
                for group_tools in optimal_groups:
                    group_times = [self.execution_times.get(tool, 5.0) for tool in group_tools]
                    group_execution_time = max(group_times) if len(group_tools) > 1 else group_times[0]
                    group_speedup = sum(group_times) / group_execution_time if group_execution_time > 0 else 1.0
                    
                    group = ParallelGroup(
                        tools=group_tools,
                        level=level_num,
                        estimated_speedup=group_speedup,
                        execution_time=group_execution_time
                    )
                    parallel_groups.append(group)
                    
                    level_parallel_time += group_execution_time
                
                total_sequential_time += level_sequential_time
                total_parallel_time += level_parallel_time
        
        # Calculate overall metrics
        overall_speedup = total_sequential_time / total_parallel_time if total_parallel_time > 0 else 1.0
        
        parallel_tool_count = sum(group.size for group in parallel_groups if group.is_parallel)
        total_tool_count = sum(group.size for group in parallel_groups)
        parallelization_ratio = parallel_tool_count / total_tool_count if total_tool_count > 0 else 0.0
        
        execution_plan = ExecutionPlan(
            parallel_groups=parallel_groups,
            total_tools=total_tool_count,
            total_levels=len(levels_dict),
            estimated_total_time=total_parallel_time,
            estimated_speedup=overall_speedup,
            parallelization_ratio=parallelization_ratio
        )
        
        self.logger.info(f"Generated execution plan: {overall_speedup:.2f}x speedup, "
                        f"{parallelization_ratio:.1%} parallelization")
        
        return execution_plan
    
    def estimate_performance_gain(self, execution_plan: ExecutionPlan) -> Dict[str, float]:
        """Predict detailed performance gains from parallel execution"""
        # Calculate time savings
        sequential_time = sum(
            sum(self.execution_times.get(tool, 5.0) for tool in group.tools)
            for group in execution_plan.parallel_groups
        )
        
        parallel_time = execution_plan.estimated_total_time
        time_saved = sequential_time - parallel_time
        
        # Calculate resource utilization
        parallel_groups_count = len([g for g in execution_plan.parallel_groups if g.is_parallel])
        total_groups = len(execution_plan.parallel_groups)
        resource_utilization = parallel_groups_count / total_groups if total_groups > 0 else 0.0
        
        # Calculate parallelization efficiency
        max_possible_speedup = execution_plan.total_tools  # If all tools could run in parallel
        actual_speedup = execution_plan.estimated_speedup
        efficiency = actual_speedup / max_possible_speedup if max_possible_speedup > 0 else 0.0
        
        return {
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "time_saved": time_saved,
            "speedup_factor": execution_plan.estimated_speedup,
            "parallelization_ratio": execution_plan.parallelization_ratio,
            "resource_utilization": resource_utilization,
            "parallelization_efficiency": efficiency,
            "parallel_opportunities": execution_plan.get_total_parallel_opportunities()
        }
    
    def find_all_parallel_combinations(self, tools: List[str]) -> Dict[int, List[List[str]]]:
        """Find all possible parallel combinations of different sizes"""
        if not tools:
            return {}
        
        combinations_by_size = {}
        
        # Find combinations of increasing size
        for size in range(2, len(tools) + 1):
            valid_combinations = []
            
            for combination in combinations(tools, size):
                # Check if all tools in combination can run together
                if self._can_all_run_together(list(combination)):
                    valid_combinations.append(list(combination))
            
            if valid_combinations:
                combinations_by_size[size] = valid_combinations
        
        self.logger.debug(f"Found parallel combinations: "
                         f"{sum(len(combos) for combos in combinations_by_size.values())} total")
        
        return combinations_by_size
    
    def _can_all_run_together(self, tools: List[str]) -> bool:
        """Check if all tools in a group can run together (all pairwise compatible)"""
        for i, tool1 in enumerate(tools):
            for tool2 in tools[i+1:]:
                if not self.conflict_analyzer.can_run_in_parallel(tool1, tool2):
                    return False
        return True
    
    def analyze_parallelization_potential(self, dependency_graph: DependencyGraph) -> Dict[str, any]:
        """Analyze the parallelization potential of a dependency graph"""
        # Count tools at each level
        level_counts = {}
        for tool_id, level in dependency_graph.levels.items():
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Find levels with parallelization potential
        parallel_potential_levels = [level for level, count in level_counts.items() if count > 1]
        
        # Calculate maximum theoretical speedup
        max_theoretical_speedup = len(dependency_graph.nodes) / len(level_counts)
        
        # Analyze each level's potential
        level_analysis = {}
        for level, tools_count in level_counts.items():
            tools_at_level = [tool for tool, tool_level in dependency_graph.levels.items() 
                             if tool_level == level]
            
            if tools_count > 1:
                # Find actual parallel opportunities
                parallel_groups = self.find_maximal_parallel_groups(tools_at_level)
                max_group_size = max(len(group) for group in parallel_groups) if parallel_groups else 1
                
                level_analysis[level] = {
                    "total_tools": tools_count,
                    "parallel_groups": len(parallel_groups),
                    "max_group_size": max_group_size,
                    "parallelization_possible": max_group_size > 1
                }
            else:
                level_analysis[level] = {
                    "total_tools": tools_count,
                    "parallel_groups": 1,
                    "max_group_size": 1,
                    "parallelization_possible": False
                }
        
        return {
            "total_tools": len(dependency_graph.nodes),
            "total_levels": len(level_counts),
            "parallel_potential_levels": parallel_potential_levels,
            "max_theoretical_speedup": max_theoretical_speedup,
            "level_analysis": level_analysis
        }
    
    def print_execution_plan(self, execution_plan: ExecutionPlan) -> None:
        """Print human-readable execution plan"""
        print("\n" + "="*70)
        print("OPTIMIZED EXECUTION PLAN")
        print("="*70)
        print(f"Total Tools: {execution_plan.total_tools}")
        print(f"Total Levels: {execution_plan.total_levels}")
        print(f"Estimated Time: {execution_plan.estimated_total_time:.1f}s")
        print(f"Estimated Speedup: {execution_plan.estimated_speedup:.2f}x")
        print(f"Parallelization Ratio: {execution_plan.parallelization_ratio:.1%}")
        print()
        
        # Group by level
        levels_dict = {}
        for group in execution_plan.parallel_groups:
            if group.level not in levels_dict:
                levels_dict[group.level] = []
            levels_dict[group.level].append(group)
        
        for level in sorted(levels_dict.keys()):
            groups_at_level = levels_dict[level]
            print(f"Level {level}:")
            
            for i, group in enumerate(groups_at_level):
                if group.is_parallel:
                    print(f"  ⚡ Parallel Group {i+1}: {group.tools}")
                    print(f"     Speedup: {group.estimated_speedup:.2f}x, Time: {group.execution_time:.1f}s")
                else:
                    print(f"  📋 Sequential: {group.tools[0]}")
                    print(f"     Time: {group.execution_time:.1f}s")
            print()
        
        # Performance analysis
        performance = self.estimate_performance_gain(execution_plan)
        print("PERFORMANCE ANALYSIS:")
        print(f"  Sequential Time: {performance['sequential_time']:.1f}s")
        print(f"  Parallel Time: {performance['parallel_time']:.1f}s")
        print(f"  Time Saved: {performance['time_saved']:.1f}s")
        print(f"  Parallel Opportunities: {performance['parallel_opportunities']} tools")
        print(f"  Resource Utilization: {performance['resource_utilization']:.1%}")
        print(f"  Parallelization Efficiency: {performance['parallelization_efficiency']:.1%}")