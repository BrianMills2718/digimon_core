"""Path Analysis Data Models

Data structures and enums for path analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PathAlgorithm(Enum):
    """Supported path algorithms"""
    DIJKSTRA = "dijkstra"
    BELLMAN_FORD = "bellman_ford"
    FLOYD_WARSHALL = "floyd_warshall"
    ASTAR = "astar"
    BFS = "bfs"
    DFS = "dfs"
    SHORTEST_PATH = "shortest_path"
    ALL_PAIRS = "all_pairs"


class FlowAlgorithm(Enum):
    """Supported flow algorithms"""
    MAX_FLOW = "max_flow"
    MIN_CUT = "min_cut"
    FLOW_NETWORK = "flow_network"


@dataclass
class PathResult:
    """Result of a path analysis"""
    source: str
    target: str
    path: List[str]
    length: float
    weight: Optional[float]
    algorithm: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class FlowResult:
    """Result of a flow analysis"""
    source: str
    sink: str
    max_flow_value: float
    min_cut_edges: List[tuple]
    flow_dict: Dict[str, Dict[str, float]]
    algorithm: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PathStats:
    """Statistical summary of path analysis"""
    total_paths: int
    avg_path_length: float
    median_path_length: float
    std_path_length: float
    min_path_length: float
    max_path_length: float
    reachable_pairs: int
    unreachable_pairs: int
    connectivity_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)