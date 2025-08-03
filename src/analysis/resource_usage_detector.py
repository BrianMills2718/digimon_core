"""
Resource Usage Detector

Analyzes and detects resource usage patterns from tool contracts and runtime behavior.
Provides detailed insights into how tools access databases, files, and shared state.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

from .contract_analyzer import ToolContractAnalyzer, ResourceUsage

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that tools can access"""
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MEMORY = "memory"
    NETWORK = "network"
    SHARED_SERVICE = "shared_service"


class AccessPattern(Enum):
    """Patterns of resource access"""
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    READ_WRITE = "read_write"
    CREATE = "create"
    DELETE = "delete"
    TRANSACTIONAL = "transactional"


@dataclass
class ResourceAccess:
    """Detailed resource access information"""
    resource_type: ResourceType
    resource_name: str
    access_pattern: AccessPattern
    frequency: str = "unknown"  # low, medium, high
    criticality: str = "medium"  # low, medium, high
    concurrent_safe: bool = True
    details: List[str] = field(default_factory=list)


@dataclass
class ToolResourceProfile:
    """Complete resource profile for a tool"""
    tool_id: str
    resource_accesses: List[ResourceAccess]
    resource_footprint: Dict[ResourceType, int]  # Count by type
    concurrency_safety: str = "safe"  # safe, caution, unsafe
    estimated_resource_load: float = 1.0  # Relative load factor
    
    def get_database_accesses(self) -> List[ResourceAccess]:
        """Get all database access patterns"""
        return [access for access in self.resource_accesses 
                if access.resource_type == ResourceType.DATABASE]
    
    def get_file_accesses(self) -> List[ResourceAccess]:
        """Get all file system access patterns"""
        return [access for access in self.resource_accesses 
                if access.resource_type == ResourceType.FILE_SYSTEM]
    
    def has_write_access(self, resource_type: ResourceType) -> bool:
        """Check if tool has write access to resource type"""
        for access in self.resource_accesses:
            if (access.resource_type == resource_type and 
                access.access_pattern in [AccessPattern.WRITE_ONLY, AccessPattern.READ_WRITE, 
                                        AccessPattern.CREATE, AccessPattern.DELETE]):
                return True
        return False


class ResourceUsageDetector:
    """Detects and analyzes resource usage patterns from tool contracts"""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize with contract analyzer"""
        self.contract_analyzer = ToolContractAnalyzer(contracts_dir)
        self.logger = logger
        self._tool_profiles = {}
        
        # Database access patterns
        self.database_patterns = {
            'neo4j': {
                'read_neo4j': AccessPattern.READ_ONLY,
                'write_neo4j': AccessPattern.READ_WRITE,
                'create_neo4j': AccessPattern.CREATE
            },
            'sqlite': {
                'read_sqlite': AccessPattern.READ_ONLY,
                'write_sqlite': AccessPattern.READ_WRITE,
                'create_sqlite': AccessPattern.CREATE
            }
        }
        
        # File access patterns
        self.file_patterns = {
            'read_input': AccessPattern.READ_ONLY,
            'write_output': AccessPattern.WRITE_ONLY,
            'read_file': AccessPattern.READ_ONLY,
            'write_file': AccessPattern.WRITE_ONLY,
            'temp_files': AccessPattern.READ_WRITE
        }
        
        # Build profiles for all tools
        self._build_all_profiles()
    
    def _build_all_profiles(self) -> None:
        """Build resource profiles for all tools"""
        contracts = self.contract_analyzer.get_all_contracts()
        
        for tool_id, contract_path in contracts.items():
            profile = self._analyze_tool_resources(tool_id, str(contract_path))
            self._tool_profiles[tool_id] = profile
        
        self.logger.info(f"Built resource profiles for {len(self._tool_profiles)} tools")
    
    def _analyze_tool_resources(self, tool_id: str, contract_path: str) -> ToolResourceProfile:
        """Analyze resource usage for a single tool"""
        # Get basic resource usage
        resources = self.contract_analyzer.extract_resources(contract_path)
        
        # Build detailed resource accesses
        resource_accesses = []
        
        # Analyze database accesses
        for db_access in resources.database_access:
            resource_access = self._parse_database_access(db_access, tool_id)
            if resource_access:
                resource_accesses.append(resource_access)
        
        # Analyze file accesses
        for file_access in resources.file_access:
            resource_access = self._parse_file_access(file_access, tool_id)
            if resource_access:
                resource_accesses.append(resource_access)
        
        # Analyze shared state
        for shared_state in resources.shared_state:
            resource_access = self._parse_shared_state(shared_state, tool_id)
            if resource_access:
                resource_accesses.append(resource_access)
        
        # Calculate resource footprint
        footprint = {}
        for resource_type in ResourceType:
            count = len([access for access in resource_accesses 
                        if access.resource_type == resource_type])
            footprint[resource_type] = count
        
        # Assess concurrency safety
        concurrency_safety = self._assess_concurrency_safety(tool_id, resource_accesses)
        
        # Estimate resource load
        resource_load = self._estimate_resource_load(tool_id, resource_accesses)
        
        profile = ToolResourceProfile(
            tool_id=tool_id,
            resource_accesses=resource_accesses,
            resource_footprint=footprint,
            concurrency_safety=concurrency_safety,
            estimated_resource_load=resource_load
        )
        
        self.logger.debug(f"Built resource profile for {tool_id}: "
                         f"{len(resource_accesses)} accesses, "
                         f"safety: {concurrency_safety}")
        
        return profile
    
    def _parse_database_access(self, db_access: str, tool_id: str) -> Optional[ResourceAccess]:
        """Parse database access pattern"""
        for db_name, patterns in self.database_patterns.items():
            if db_access in patterns:
                access_pattern = patterns[db_access]
                
                # Determine concurrent safety
                concurrent_safe = access_pattern == AccessPattern.READ_ONLY
                
                # Set criticality based on access type
                criticality = "high" if "write" in db_access else "medium"
                
                return ResourceAccess(
                    resource_type=ResourceType.DATABASE,
                    resource_name=db_name,
                    access_pattern=access_pattern,
                    criticality=criticality,
                    concurrent_safe=concurrent_safe,
                    details=[f"Tool {tool_id} performs {db_access}"]
                )
        
        # Unknown database access pattern
        return ResourceAccess(
            resource_type=ResourceType.DATABASE,
            resource_name="unknown",
            access_pattern=AccessPattern.READ_WRITE,
            concurrent_safe=False,
            details=[f"Unknown database access: {db_access}"]
        )
    
    def _parse_file_access(self, file_access: str, tool_id: str) -> Optional[ResourceAccess]:
        """Parse file access pattern"""
        if file_access in self.file_patterns:
            access_pattern = self.file_patterns[file_access]
            
            # File operations are generally safe if not writing to same files
            concurrent_safe = access_pattern == AccessPattern.READ_ONLY
            
            # Set frequency based on tool type
            frequency = self._estimate_file_frequency(tool_id, file_access)
            
            return ResourceAccess(
                resource_type=ResourceType.FILE_SYSTEM,
                resource_name=file_access,
                access_pattern=access_pattern,
                frequency=frequency,
                concurrent_safe=concurrent_safe,
                details=[f"Tool {tool_id} performs {file_access}"]
            )
        
        return None
    
    def _parse_shared_state(self, shared_state: str, tool_id: str) -> Optional[ResourceAccess]:
        """Parse shared state access"""
        if shared_state.startswith('service_'):
            service_name = shared_state.replace('service_', '')
            
            # Services are generally designed for concurrent access
            concurrent_safe = True
            criticality = "medium"
            
            # Some services might be more critical
            if service_name == 'identity_service':
                criticality = "high"
                concurrent_safe = False  # Identity resolution might have conflicts
            
            return ResourceAccess(
                resource_type=ResourceType.SHARED_SERVICE,
                resource_name=service_name,
                access_pattern=AccessPattern.READ_WRITE,
                criticality=criticality,
                concurrent_safe=concurrent_safe,
                details=[f"Tool {tool_id} uses {service_name}"]
            )
        
        return None
    
    def _assess_concurrency_safety(self, tool_id: str, accesses: List[ResourceAccess]) -> str:
        """Assess overall concurrency safety for tool"""
        unsafe_count = len([access for access in accesses if not access.concurrent_safe])
        
        # Count database write operations (more critical)
        db_write_count = len([access for access in accesses 
                             if (access.resource_type == ResourceType.DATABASE and
                                 access.access_pattern in [AccessPattern.WRITE_ONLY, 
                                                          AccessPattern.READ_WRITE,
                                                          AccessPattern.CREATE,
                                                          AccessPattern.DELETE])])
        
        # Count high-criticality unsafe accesses
        high_criticality_unsafe = len([access for access in accesses 
                                      if not access.concurrent_safe and access.criticality == "high"])
        
        if high_criticality_unsafe > 0 or db_write_count > 1:
            return "unsafe"
        elif unsafe_count > 0 or db_write_count > 0:
            return "caution"
        else:
            return "safe"
    
    def _estimate_resource_load(self, tool_id: str, accesses: List[ResourceAccess]) -> float:
        """Estimate relative resource load"""
        base_load = 1.0
        
        # Heavy tools based on known patterns
        heavy_tools = {
            'T68_PAGE_RANK': 3.0,  # Graph algorithms are resource intensive
            'T85_TWITTER_EXPLORER': 2.5,  # Network requests and LLM calls
            'T01_PDF_LOADER': 2.0,  # File I/O intensive
            'T27_RELATIONSHIP_EXTRACTOR': 2.0,  # NLP processing
        }
        
        if tool_id in heavy_tools:
            base_load = heavy_tools[tool_id]
        
        # Adjust based on resource accesses
        database_writes = len([access for access in accesses 
                              if (access.resource_type == ResourceType.DATABASE and
                                  access.access_pattern in [AccessPattern.WRITE_ONLY, 
                                                           AccessPattern.READ_WRITE])])
        
        base_load += database_writes * 0.5
        
        return base_load
    
    def _estimate_file_frequency(self, tool_id: str, file_access: str) -> str:
        """Estimate file access frequency"""
        # PDF loaders and processors are high frequency
        if 'LOADER' in tool_id or 'CHUNKER' in tool_id:
            return "high"
        elif 'BUILDER' in tool_id:
            return "medium"
        else:
            return "low"
    
    def get_tool_profile(self, tool_id: str) -> Optional[ToolResourceProfile]:
        """Get resource profile for specific tool"""
        return self._tool_profiles.get(tool_id)
    
    def get_all_profiles(self) -> Dict[str, ToolResourceProfile]:
        """Get all tool resource profiles"""
        return self._tool_profiles.copy()
    
    def find_resource_conflicts(self, tool1: str, tool2: str) -> List[str]:
        """Find specific resource conflicts between two tools"""
        profile1 = self._tool_profiles.get(tool1)
        profile2 = self._tool_profiles.get(tool2)
        
        if not profile1 or not profile2:
            return []
        
        conflicts = []
        
        # Check database conflicts
        db_accesses1 = profile1.get_database_accesses()
        db_accesses2 = profile2.get_database_accesses()
        
        for access1 in db_accesses1:
            for access2 in db_accesses2:
                if (access1.resource_name == access2.resource_name and
                    (access1.access_pattern != AccessPattern.READ_ONLY or
                     access2.access_pattern != AccessPattern.READ_ONLY)):
                    conflicts.append(f"Database conflict on {access1.resource_name}: "
                                   f"{access1.access_pattern.value} vs {access2.access_pattern.value}")
        
        return conflicts
    
    def get_resource_usage_summary(self) -> Dict[str, any]:
        """Get summary of resource usage across all tools"""
        total_tools = len(self._tool_profiles)
        
        # Count by safety level
        safety_counts = {"safe": 0, "caution": 0, "unsafe": 0}
        for profile in self._tool_profiles.values():
            safety_counts[profile.concurrency_safety] += 1
        
        # Count by resource type
        resource_counts = {}
        for resource_type in ResourceType:
            count = sum([profile.resource_footprint.get(resource_type, 0) 
                        for profile in self._tool_profiles.values()])
            resource_counts[resource_type.value] = count
        
        # Average resource load
        avg_load = sum([profile.estimated_resource_load 
                       for profile in self._tool_profiles.values()]) / total_tools
        
        return {
            "total_tools": total_tools,
            "safety_distribution": safety_counts,
            "resource_usage": resource_counts,
            "average_resource_load": avg_load
        }
    
    def print_resource_analysis(self) -> None:
        """Print detailed resource analysis"""
        summary = self.get_resource_usage_summary()
        
        print("\n" + "="*70)
        print("RESOURCE USAGE ANALYSIS")
        print("="*70)
        print(f"Total Tools Analyzed: {summary['total_tools']}")
        print(f"Average Resource Load: {summary['average_resource_load']:.2f}")
        print()
        
        print("CONCURRENCY SAFETY DISTRIBUTION:")
        for safety, count in summary['safety_distribution'].items():
            percentage = (count / summary['total_tools']) * 100
            print(f"  {safety.upper()}: {count} tools ({percentage:.1f}%)")
        print()
        
        print("RESOURCE USAGE BY TYPE:")
        for resource_type, count in summary['resource_usage'].items():
            print(f"  {resource_type.upper()}: {count} accesses")
        print()
        
        print("TOOL RESOURCE PROFILES:")
        for tool_id, profile in sorted(self._tool_profiles.items()):
            print(f"\n  {tool_id}:")
            print(f"    Safety: {profile.concurrency_safety}")
            print(f"    Load Factor: {profile.estimated_resource_load:.1f}")
            print(f"    Resource Accesses: {len(profile.resource_accesses)}")
            
            for access in profile.resource_accesses:
                safety_indicator = "✅" if access.concurrent_safe else "⚠️"
                print(f"      {safety_indicator} {access.resource_type.value}: "
                      f"{access.resource_name} ({access.access_pattern.value})")
    
    def export_resource_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """Export resource usage matrix for external analysis"""
        matrix = {}
        
        for tool_id, profile in self._tool_profiles.items():
            matrix[tool_id] = {}
            
            for resource_type in ResourceType:
                accesses = [access for access in profile.resource_accesses 
                           if access.resource_type == resource_type]
                matrix[tool_id][resource_type.value] = [
                    f"{access.resource_name}:{access.access_pattern.value}" 
                    for access in accesses
                ]
        
        return matrix