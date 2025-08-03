"""
Contract-Based Dependency Discovery

Analyzes tool YAML contracts to extract dependencies, resources, and build dependency graphs.
Replaces hardcoded dependency logic with programmatic analysis.
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ResourceUsage:
    """Resource usage patterns extracted from tool contract"""
    database_access: List[str] = None  # ['read_neo4j', 'write_sqlite', etc]
    file_access: List[str] = None      # ['read_input', 'write_output', etc]
    shared_state: List[str] = None     # ['memory_cache', 'temp_files', etc]
    
    def __post_init__(self):
        if self.database_access is None:
            self.database_access = []
        if self.file_access is None:
            self.file_access = []
        if self.shared_state is None:
            self.shared_state = []


@dataclass
class DependencyGraph:
    """Complete dependency graph for all tools"""
    nodes: Set[str]  # All tool IDs
    edges: Dict[str, Set[str]]  # tool_id -> set of dependencies
    levels: Dict[str, int]  # tool_id -> dependency level
    topological_order: List[str]  # Ordered list of tools
    

class ToolContractAnalyzer:
    """Analyzes tool contracts to extract dependencies and resources programmatically"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with contracts directory"""
        if contracts_dir is None:
            # Default to contracts/tools directory
            contracts_dir = Path(__file__).parent.parent.parent / "contracts" / "tools"
        
        self.contracts_dir = Path(contracts_dir)
        self.logger = logger
        
        if not self.contracts_dir.exists():
            raise FileNotFoundError(f"Contracts directory not found: {self.contracts_dir}")
    
    def extract_dependencies(self, contract_path: str) -> List[str]:
        """Parse YAML contract, return list of tool dependencies"""
        try:
            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)
            
            # Extract depends_on field
            depends_on = contract.get('depends_on', [])
            
            # Validate dependencies exist
            for dep in depends_on:
                dep_path = self.contracts_dir / f"{dep}.yaml"
                if not dep_path.exists():
                    self.logger.warning(f"Dependency {dep} not found for {contract_path}")
            
            self.logger.debug(f"Extracted dependencies for {contract_path}: {depends_on}")
            return depends_on
            
        except Exception as e:
            self.logger.error(f"Failed to extract dependencies from {contract_path}: {e}")
            return []
    
    def extract_resources(self, contract_path: str) -> ResourceUsage:
        """Extract database/file resources accessed by tool"""
        try:
            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)
            
            # Analyze dependencies for resource patterns
            dependencies = contract.get('dependencies', [])
            
            database_access = []
            file_access = ['read_input']  # All tools read input
            shared_state = []
            
            # Infer resource access from dependencies
            for dep in dependencies:
                if dep == 'neo4j':
                    database_access.extend(['read_neo4j', 'write_neo4j'])
                elif dep == 'sqlite' or 'sqlite' in dep:
                    database_access.extend(['read_sqlite', 'write_sqlite'])
                elif dep in ['identity_service', 'provenance_service', 'quality_service']:
                    shared_state.append(f'service_{dep}')
            
            # Analyze tool category for additional patterns
            category = contract.get('category', '')
            tool_id = contract.get('tool_id', '')
            
            if 'builder' in tool_id.lower() or category == 'graph_building':
                file_access.append('write_output')
                database_access.append('write_neo4j')
            elif 'loader' in tool_id.lower() or category == 'loader':
                file_access.extend(['read_file', 'write_output'])
            elif 'chunker' in tool_id.lower():
                file_access.append('write_output')
            
            resource_usage = ResourceUsage(
                database_access=database_access,
                file_access=file_access,
                shared_state=shared_state
            )
            
            self.logger.debug(f"Extracted resources for {contract_path}: {resource_usage}")
            return resource_usage
            
        except Exception as e:
            self.logger.error(f"Failed to extract resources from {contract_path}: {e}")
            return ResourceUsage()
    
    def build_dependency_graph(self, all_contracts: Optional[Dict[str, Path]] = None) -> DependencyGraph:
        """Build complete directed dependency graph"""
        if all_contracts is None:
            # Auto-discover all contracts
            all_contracts = {}
            for contract_file in self.contracts_dir.glob("*.yaml"):
                tool_id = contract_file.stem
                all_contracts[tool_id] = contract_file
        
        # Build adjacency list
        edges = {}
        nodes = set()
        
        for tool_id, contract_path in all_contracts.items():
            nodes.add(tool_id)
            dependencies = self.extract_dependencies(str(contract_path))
            edges[tool_id] = set(dependencies)
            
            # Add dependency nodes
            for dep in dependencies:
                nodes.add(dep)
        
        # Validate no circular dependencies and calculate levels
        levels, topological_order = self._calculate_dependency_levels(edges)
        
        if not levels:
            self.logger.error("Circular dependency detected in tool contracts")
            raise ValueError("Circular dependency detected")
        
        dependency_graph = DependencyGraph(
            nodes=nodes,
            edges=edges,
            levels=levels,
            topological_order=topological_order
        )
        
        self.logger.info(f"Built dependency graph with {len(nodes)} nodes, {sum(len(deps) for deps in edges.values())} edges")
        self.logger.debug(f"Dependency levels: {levels}")
        
        return dependency_graph
    
    def _calculate_dependency_levels(self, edges: Dict[str, Set[str]]) -> tuple[Dict[str, int], List[str]]:
        """Calculate topological ordering (dependency levels) using Kahn's algorithm"""
        levels = {}
        topological_order = []
        
        # Calculate in-degree for each node
        in_degree = defaultdict(int)
        all_nodes = set(edges.keys())
        
        # Add all dependency nodes
        for deps in edges.values():
            all_nodes.update(deps)
        
        # Initialize in-degrees
        for node in all_nodes:
            in_degree[node] = 0
        
        # Calculate actual in-degrees
        for node, deps in edges.items():
            for dep in deps:
                in_degree[node] += 1
        
        # Kahn's algorithm for topological sort
        current_level = 0
        queue = [node for node in all_nodes if in_degree[node] == 0]
        
        while queue:
            next_queue = []
            
            # Process all nodes at current level
            for node in queue:
                levels[node] = current_level
                topological_order.append(node)
                
                # Reduce in-degree of dependent nodes
                for dependent, deps in edges.items():
                    if node in deps:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            next_queue.append(dependent)
            
            queue = next_queue
            current_level += 1
        
        # Check for circular dependencies
        if len(levels) != len(all_nodes):
            self.logger.error(f"Circular dependency detected. Processed {len(levels)}/{len(all_nodes)} nodes")
            return {}, []
        
        return levels, topological_order
    
    def get_all_contracts(self) -> Dict[str, Path]:
        """Get all available tool contracts"""
        contracts = {}
        for contract_file in self.contracts_dir.glob("*.yaml"):
            tool_id = contract_file.stem
            contracts[tool_id] = contract_file
        return contracts
    
    def validate_contract(self, contract_path: str) -> bool:
        """Validate that a contract has required fields for dependency analysis"""
        try:
            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)
            
            required_fields = ['tool_id', 'depends_on']
            for field in required_fields:
                if field not in contract:
                    self.logger.error(f"Contract {contract_path} missing required field: {field}")
                    return False
            
            # Validate depends_on is a list
            if not isinstance(contract['depends_on'], list):
                self.logger.error(f"Contract {contract_path} depends_on must be a list")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate contract {contract_path}: {e}")
            return False