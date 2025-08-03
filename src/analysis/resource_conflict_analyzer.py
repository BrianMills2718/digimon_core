"""
Resource Conflict Analysis

Detects resource conflicts between tools to determine safe parallel execution.
Analyzes database access, file system usage, and shared state modifications.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .contract_analyzer import ToolContractAnalyzer, ResourceUsage

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of resource conflicts"""
    NO_CONFLICT = "no_conflict"
    DATABASE_WRITE_CONFLICT = "database_write_conflict"
    DATABASE_READ_WRITE_CONFLICT = "database_read_write_conflict"
    FILE_WRITE_CONFLICT = "file_write_conflict"
    SHARED_STATE_CONFLICT = "shared_state_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"


@dataclass
class ConflictResult:
    """Result of conflict analysis between two tools"""
    tool1: str
    tool2: str
    conflict_type: ConflictType
    has_conflict: bool
    details: str = ""
    severity: str = "medium"  # low, medium, high
    
    def __str__(self) -> str:
        conflict_status = "CONFLICT" if self.has_conflict else "SAFE"
        return f"{self.tool1} <-> {self.tool2}: {conflict_status} ({self.conflict_type.value})"


class ResourceConflictAnalyzer:
    """Analyzes resource conflicts between tools for parallel execution safety"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with contract analyzer"""
        self.contract_analyzer = ToolContractAnalyzer(contracts_dir)
        self.logger = logger
        self._resource_cache = {}  # Cache resource analysis results
        
        # Load all tool resources
        self._load_all_resources()
    
    def _load_all_resources(self) -> None:
        """Pre-load resource usage for all tools"""
        contracts = self.contract_analyzer.get_all_contracts()
        
        for tool_id, contract_path in contracts.items():
            resources = self.contract_analyzer.extract_resources(str(contract_path))
            self._resource_cache[tool_id] = resources
            
        self.logger.info(f"Loaded resource information for {len(self._resource_cache)} tools")
    
    def analyze_database_conflicts(self, tool1: str, tool2: str) -> ConflictResult:
        """Check if tools conflict on database operations"""
        resources1 = self._resource_cache.get(tool1, ResourceUsage())
        resources2 = self._resource_cache.get(tool2, ResourceUsage())
        
        db_access1 = set(resources1.database_access)
        db_access2 = set(resources2.database_access)
        
        # Check for write-write conflicts
        write_ops1 = {op for op in db_access1 if 'write' in op}
        write_ops2 = {op for op in db_access2 if 'write' in op}
        
        if write_ops1 & write_ops2:
            # Both write to same database
            common_writes = write_ops1 & write_ops2
            return ConflictResult(
                tool1=tool1,
                tool2=tool2,
                conflict_type=ConflictType.DATABASE_WRITE_CONFLICT,
                has_conflict=True,
                details=f"Both tools write to: {common_writes}",
                severity="high"
            )
        
        # Check for read-write conflicts
        read_ops1 = {op for op in db_access1 if 'read' in op}
        read_ops2 = {op for op in db_access2 if 'read' in op}
        
        # Extract database names
        write_dbs1 = {op.replace('write_', '') for op in write_ops1}
        write_dbs2 = {op.replace('write_', '') for op in write_ops2}
        read_dbs1 = {op.replace('read_', '') for op in read_ops1}
        read_dbs2 = {op.replace('read_', '') for op in read_ops2}
        
        # Check if one writes while other reads same database
        if (write_dbs1 & read_dbs2) or (write_dbs2 & read_dbs1):
            conflict_dbs = (write_dbs1 & read_dbs2) | (write_dbs2 & read_dbs1)
            return ConflictResult(
                tool1=tool1,
                tool2=tool2,
                conflict_type=ConflictType.DATABASE_READ_WRITE_CONFLICT,
                has_conflict=True,
                details=f"Read-write conflict on: {conflict_dbs}",
                severity="medium"
            )
        
        # No database conflicts
        return ConflictResult(
            tool1=tool1,
            tool2=tool2,
            conflict_type=ConflictType.NO_CONFLICT,
            has_conflict=False,
            details="No database conflicts detected"
        )
    
    def analyze_file_conflicts(self, tool1: str, tool2: str) -> ConflictResult:
        """Check if tools access same files"""
        resources1 = self._resource_cache.get(tool1, ResourceUsage())
        resources2 = self._resource_cache.get(tool2, ResourceUsage())
        
        file_access1 = set(resources1.file_access)
        file_access2 = set(resources2.file_access)
        
        # Check for write-write conflicts on same files
        write_ops1 = {op for op in file_access1 if 'write' in op}
        write_ops2 = {op for op in file_access2 if 'write' in op}
        
        if write_ops1 & write_ops2:
            common_writes = write_ops1 & write_ops2
            return ConflictResult(
                tool1=tool1,
                tool2=tool2,
                conflict_type=ConflictType.FILE_WRITE_CONFLICT,
                has_conflict=True,
                details=f"Both tools write to: {common_writes}",
                severity="high"
            )
        
        # Most file operations are safe if not writing to same files
        return ConflictResult(
            tool1=tool1,
            tool2=tool2,
            conflict_type=ConflictType.NO_CONFLICT,
            has_conflict=False,
            details="No file conflicts detected"
        )
    
    def analyze_shared_state_conflicts(self, tool1: str, tool2: str) -> ConflictResult:
        """Check if tools modify shared application state"""
        resources1 = self._resource_cache.get(tool1, ResourceUsage())
        resources2 = self._resource_cache.get(tool2, ResourceUsage())
        
        shared_state1 = set(resources1.shared_state)
        shared_state2 = set(resources2.shared_state)
        
        # Check for conflicts in shared services
        common_services = shared_state1 & shared_state2
        
        if common_services:
            # Services are generally safe for concurrent access (they handle concurrency)
            # But some combinations might be problematic
            problematic_combinations = {
                'service_identity_service',  # Identity resolution might conflict
            }
            
            if any(service in problematic_combinations for service in common_services):
                return ConflictResult(
                    tool1=tool1,
                    tool2=tool2,
                    conflict_type=ConflictType.SHARED_STATE_CONFLICT,
                    has_conflict=True,
                    details=f"Shared state conflicts: {common_services}",
                    severity="medium"
                )
        
        return ConflictResult(
            tool1=tool1,
            tool2=tool2,
            conflict_type=ConflictType.NO_CONFLICT,
            has_conflict=False,
            details="No shared state conflicts detected"
        )
    
    def can_run_in_parallel(self, tool1: str, tool2: str) -> bool:
        """Determine if tools can safely run together"""
        # Check all conflict types
        db_conflict = self.analyze_database_conflicts(tool1, tool2)
        file_conflict = self.analyze_file_conflicts(tool1, tool2)
        state_conflict = self.analyze_shared_state_conflicts(tool1, tool2)
        
        # Any conflict prevents parallel execution
        if db_conflict.has_conflict or file_conflict.has_conflict or state_conflict.has_conflict:
            self.logger.debug(f"Parallel execution blocked for {tool1} and {tool2}")
            if db_conflict.has_conflict:
                self.logger.debug(f"  Database conflict: {db_conflict.details}")
            if file_conflict.has_conflict:
                self.logger.debug(f"  File conflict: {file_conflict.details}")
            if state_conflict.has_conflict:
                self.logger.debug(f"  State conflict: {state_conflict.details}")
            return False
        
        # Additional business logic checks
        if not self._check_business_logic_compatibility(tool1, tool2):
            return False
        
        self.logger.debug(f"✅ {tool1} and {tool2} can run in parallel")
        return True
    
    def _check_business_logic_compatibility(self, tool1: str, tool2: str) -> bool:
        """Check business logic compatibility beyond resource conflicts"""
        
        # Known incompatible pairs based on business logic
        incompatible_pairs = {
            # Entity builder and edge builder both modify graph structure
            # but in a coordinated way, so they're actually safe
            # ("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"): False,  # Actually safe per current system
        }
        
        pair = tuple(sorted([tool1, tool2]))
        if pair in incompatible_pairs:
            if not incompatible_pairs[pair]:
                self.logger.debug(f"Business logic incompatibility: {pair}")
                return False
        
        # Check for specific tool patterns that shouldn't run together
        if self._are_graph_modification_tools(tool1, tool2):
            # Both tools modify graph structure - need to check if safe
            return self._check_graph_modification_safety(tool1, tool2)
        
        return True
    
    def _are_graph_modification_tools(self, tool1: str, tool2: str) -> bool:
        """Check if both tools modify graph structure"""
        graph_modifiers = {"T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"}
        return tool1 in graph_modifiers and tool2 in graph_modifiers
    
    def _check_graph_modification_safety(self, tool1: str, tool2: str) -> bool:
        """Check if graph modification tools can run safely together"""
        # T31 (Entity Builder) and T34 (Edge Builder) work on different aspects
        # T31 creates nodes, T34 creates relationships
        # They're designed to be compatible
        safe_graph_pairs = {
            ("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER")
        }
        
        pair = tuple(sorted([tool1, tool2]))
        return pair in safe_graph_pairs
    
    def analyze_all_conflicts(self) -> Dict[Tuple[str, str], List[ConflictResult]]:
        """Analyze conflicts between all tool pairs"""
        all_tools = list(self._resource_cache.keys())
        conflicts = {}
        
        for i, tool1 in enumerate(all_tools):
            for tool2 in all_tools[i+1:]:
                pair = (tool1, tool2)
                
                # Analyze all conflict types
                results = [
                    self.analyze_database_conflicts(tool1, tool2),
                    self.analyze_file_conflicts(tool1, tool2),
                    self.analyze_shared_state_conflicts(tool1, tool2)
                ]
                
                conflicts[pair] = results
        
        return conflicts
    
    def get_safe_parallel_pairs(self) -> Set[Tuple[str, str]]:
        """Get all pairs of tools that can run safely in parallel"""
        all_tools = list(self._resource_cache.keys())
        safe_pairs = set()
        
        for i, tool1 in enumerate(all_tools):
            for tool2 in all_tools[i+1:]:
                if self.can_run_in_parallel(tool1, tool2):
                    safe_pairs.add(tuple(sorted([tool1, tool2])))
        
        self.logger.info(f"Found {len(safe_pairs)} safe parallel pairs out of "
                        f"{len(all_tools) * (len(all_tools) - 1) // 2} total pairs")
        
        return safe_pairs
    
    def get_conflict_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Get conflict matrix for all tools"""
        all_tools = list(self._resource_cache.keys())
        matrix = {}
        
        for tool1 in all_tools:
            matrix[tool1] = {}
            for tool2 in all_tools:
                if tool1 == tool2:
                    matrix[tool1][tool2] = False  # Tool doesn't conflict with itself
                else:
                    matrix[tool1][tool2] = not self.can_run_in_parallel(tool1, tool2)
        
        return matrix
    
    def print_conflict_analysis(self) -> None:
        """Print human-readable conflict analysis"""
        safe_pairs = self.get_safe_parallel_pairs()
        all_tools = list(self._resource_cache.keys())
        total_pairs = len(all_tools) * (len(all_tools) - 1) // 2
        
        print("\n" + "="*70)
        print("RESOURCE CONFLICT ANALYSIS")
        print("="*70)
        print(f"Total Tools: {len(all_tools)}")
        print(f"Total Possible Pairs: {total_pairs}")
        print(f"Safe Parallel Pairs: {len(safe_pairs)}")
        print(f"Conflict Rate: {((total_pairs - len(safe_pairs)) / total_pairs * 100):.1f}%")
        print()
        
        print("SAFE PARALLEL PAIRS:")
        for pair in sorted(safe_pairs):
            print(f"  ✅ {pair[0]} <-> {pair[1]}")
        
        print()
        print("CONFLICTING PAIRS:")
        for i, tool1 in enumerate(all_tools):
            for tool2 in all_tools[i+1:]:
                pair = tuple(sorted([tool1, tool2]))
                if pair not in safe_pairs:
                    print(f"  ❌ {tool1} <-> {tool2}")
                    # Show why they conflict
                    db_conflict = self.analyze_database_conflicts(tool1, tool2)
                    if db_conflict.has_conflict:
                        print(f"     Database: {db_conflict.details}")
                    file_conflict = self.analyze_file_conflicts(tool1, tool2)
                    if file_conflict.has_conflict:
                        print(f"     File: {file_conflict.details}")
                    state_conflict = self.analyze_shared_state_conflicts(tool1, tool2)
                    if state_conflict.has_conflict:
                        print(f"     State: {state_conflict.details}")