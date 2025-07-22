"""
Schema Registry - Centralized Management and Versioning
Manages theory schemas, versions, compatibility, and migrations
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import hashlib
import semver

class SchemaVersion:
    """Semantic versioning for schemas"""
    
    def __init__(self, version_string: str):
        self.version = semver.VersionInfo.parse(version_string)
    
    def __str__(self):
        return str(self.version)
    
    def is_compatible_with(self, other: 'SchemaVersion') -> bool:
        """Check if this version is backward compatible with another"""
        # Major version must match for compatibility
        return self.version.major == other.version.major
    
    def is_newer_than(self, other: 'SchemaVersion') -> bool:
        """Check if this version is newer"""
        return self.version > other.version

@dataclass
class SchemaMetadata:
    """Metadata about a theory schema"""
    schema_id: str
    version: SchemaVersion
    theory_name: str
    author: str
    description: str
    created_at: datetime
    file_path: str
    checksum: str
    dependencies: List[str]
    compatible_versions: List[str]

class CompatibilityLevel(Enum):
    FULL = "full"
    PARTIAL = "partial"
    INCOMPATIBLE = "incompatible"

@dataclass
class CompatibilityResult:
    """Result of compatibility check between schemas"""
    level: CompatibilityLevel
    issues: List[str]
    migration_required: bool
    migration_path: Optional[str] = None

class SchemaRegistry:
    """
    Centralized registry for theory schemas with versioning and compatibility management
    """
    
    def __init__(self, registry_dir: str = "theory"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        
        # Registry metadata
        self.metadata_file = self.registry_dir / "registry.json"
        self.schemas: Dict[str, Dict[str, SchemaMetadata]] = {}  # schema_id -> version -> metadata
        self.compatibility_matrix: Dict[Tuple[str, str], CompatibilityResult] = {}
        
        # Load existing registry
        self._load_registry()
    
    def _load_registry(self):
        """Load registry metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct metadata objects
                for schema_id, versions in data.get('schemas', {}).items():
                    self.schemas[schema_id] = {}
                    for version_str, metadata in versions.items():
                        self.schemas[schema_id][version_str] = SchemaMetadata(
                            schema_id=metadata['schema_id'],
                            version=SchemaVersion(metadata['version']),
                            theory_name=metadata['theory_name'],
                            author=metadata['author'],
                            description=metadata['description'],
                            created_at=datetime.fromisoformat(metadata['created_at']),
                            file_path=metadata['file_path'],
                            checksum=metadata['checksum'],
                            dependencies=metadata['dependencies'],
                            compatible_versions=metadata['compatible_versions']
                        )
                
                # Load compatibility matrix
                for key_str, result_data in data.get('compatibility_matrix', {}).items():
                    schema1, schema2 = key_str.split('|')
                    self.compatibility_matrix[(schema1, schema2)] = CompatibilityResult(
                        level=CompatibilityLevel(result_data['level']),
                        issues=result_data['issues'],
                        migration_required=result_data['migration_required'],
                        migration_path=result_data.get('migration_path')
                    )
                    
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
    
    def _save_registry(self):
        """Save registry metadata to file"""
        data = {
            'schemas': {},
            'compatibility_matrix': {},
            'last_updated': datetime.now().isoformat()
        }
        
        # Serialize schemas
        for schema_id, versions in self.schemas.items():
            data['schemas'][schema_id] = {}
            for version_str, metadata in versions.items():
                data['schemas'][schema_id][version_str] = {
                    'schema_id': metadata.schema_id,
                    'version': str(metadata.version),
                    'theory_name': metadata.theory_name,
                    'author': metadata.author,
                    'description': metadata.description,
                    'created_at': metadata.created_at.isoformat(),
                    'file_path': metadata.file_path,
                    'checksum': metadata.checksum,
                    'dependencies': metadata.dependencies,
                    'compatible_versions': metadata.compatible_versions
                }
        
        # Serialize compatibility matrix
        for (schema1, schema2), result in self.compatibility_matrix.items():
            key_str = f"{schema1}|{schema2}"
            data['compatibility_matrix'][key_str] = {
                'level': result.level.value,
                'issues': result.issues,
                'migration_required': result.migration_required,
                'migration_path': result.migration_path
            }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of schema file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def register_schema(self, schema_file: str, schema_id: Optional[str] = None) -> bool:
        """
        Register a new schema or version
        
        Args:
            schema_file: Path to schema file
            schema_id: Optional explicit schema ID
            
        Returns:
            True if registration successful
        """
        schema_path = Path(schema_file)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        # Load schema content
        with open(schema_path, 'r') as f:
            if schema_path.suffix == '.json':
                schema_data = json.load(f)
            elif schema_path.suffix in ['.yaml', '.yml']:
                schema_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported schema format: {schema_path.suffix}")
        
        # Extract metadata
        theory_name = schema_data.get('theory_name', 'Unknown')
        version_str = schema_data.get('theory_version', '1.0.0')
        author = schema_data.get('theory_author', 'Unknown')
        description = schema_data.get('description', '')
        dependencies = schema_data.get('dependencies', [])
        
        # Generate schema ID if not provided
        if not schema_id:
            schema_id = theory_name.lower().replace(' ', '_').replace('-', '_')
        
        # Create metadata
        metadata = SchemaMetadata(
            schema_id=schema_id,
            version=SchemaVersion(version_str),
            theory_name=theory_name,
            author=author,
            description=description,
            created_at=datetime.now(),
            file_path=str(schema_path),
            checksum=self._calculate_checksum(str(schema_path)),
            dependencies=dependencies,
            compatible_versions=[]
        )
        
        # Register schema
        if schema_id not in self.schemas:
            self.schemas[schema_id] = {}
        
        self.schemas[schema_id][version_str] = metadata
        
        # Update compatibility matrix
        self._update_compatibility_matrix(schema_id, version_str)
        
        # Save registry
        self._save_registry()
        
        print(f"✓ Registered schema: {schema_id} v{version_str}")
        return True
    
    def _update_compatibility_matrix(self, schema_id: str, version: str):
        """Update compatibility matrix for new schema version"""
        # Check compatibility with other versions of same schema
        if schema_id in self.schemas:
            for other_version in self.schemas[schema_id]:
                if other_version != version:
                    result = self._check_version_compatibility(schema_id, version, other_version)
                    self.compatibility_matrix[(f"{schema_id}:{version}", f"{schema_id}:{other_version}")] = result
        
        # Check compatibility with other schemas
        for other_schema_id in self.schemas:
            if other_schema_id != schema_id:
                for other_version in self.schemas[other_schema_id]:
                    result = self._check_schema_compatibility(schema_id, version, other_schema_id, other_version)
                    self.compatibility_matrix[(f"{schema_id}:{version}", f"{other_schema_id}:{other_version}")] = result
    
    def _check_version_compatibility(self, schema_id: str, version1: str, version2: str) -> CompatibilityResult:
        """Check compatibility between versions of same schema"""
        v1 = SchemaVersion(version1)
        v2 = SchemaVersion(version2)
        
        if v1.is_compatible_with(v2):
            return CompatibilityResult(
                level=CompatibilityLevel.FULL,
                issues=[],
                migration_required=False
            )
        else:
            return CompatibilityResult(
                level=CompatibilityLevel.INCOMPATIBLE,
                issues=[f"Major version mismatch: {v1} vs {v2}"],
                migration_required=True,
                migration_path=f"migration_{schema_id}_{version2}_to_{version1}.py"
            )
    
    def _check_schema_compatibility(self, schema1_id: str, version1: str, schema2_id: str, version2: str) -> CompatibilityResult:
        """Check compatibility between different schemas"""
        # Load both schemas
        try:
            schema1_metadata = self.schemas[schema1_id][version1]
            schema2_metadata = self.schemas[schema2_id][version2]
            
            # Load schema content
            with open(schema1_metadata.file_path, 'r') as f:
                if Path(schema1_metadata.file_path).suffix == '.json':
                    schema1_data = json.load(f)
                else:
                    schema1_data = yaml.safe_load(f)
            
            with open(schema2_metadata.file_path, 'r') as f:
                if Path(schema2_metadata.file_path).suffix == '.json':
                    schema2_data = json.load(f)
                else:
                    schema2_data = yaml.safe_load(f)
            
            # Check for integration points
            compatibility = schema1_data.get('theory_compatibility', {})
            compatible_theories = compatibility.get('compatible_with', [])
            
            if schema2_metadata.theory_name.lower() in [t.lower() for t in compatible_theories]:
                return CompatibilityResult(
                    level=CompatibilityLevel.FULL,
                    issues=[],
                    migration_required=False
                )
            elif schema2_metadata.theory_name.lower() in compatibility.get('conflicts_with', []):
                return CompatibilityResult(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    issues=[f"Explicit conflict declared between {schema1_metadata.theory_name} and {schema2_metadata.theory_name}"],
                    migration_required=False
                )
            else:
                # Check for shared data types
                schema1_types = set(schema1_data.get('data_type_mappings', {}).keys())
                schema2_types = set(schema2_data.get('data_type_mappings', {}).keys())
                shared_types = schema1_types.intersection(schema2_types)
                
                if shared_types:
                    return CompatibilityResult(
                        level=CompatibilityLevel.PARTIAL,
                        issues=[f"Shared data types may conflict: {shared_types}"],
                        migration_required=False
                    )
                else:
                    return CompatibilityResult(
                        level=CompatibilityLevel.INCOMPATIBLE,
                        issues=["No integration points found"],
                        migration_required=False
                    )
                    
        except Exception as e:
            return CompatibilityResult(
                level=CompatibilityLevel.INCOMPATIBLE,
                issues=[f"Error checking compatibility: {e}"],
                migration_required=False
            )
    
    def get_schema(self, schema_id: str, version: Optional[str] = None) -> Optional[SchemaMetadata]:
        """
        Get schema metadata
        
        Args:
            schema_id: Schema identifier
            version: Specific version (defaults to latest)
            
        Returns:
            Schema metadata if found
        """
        if schema_id not in self.schemas:
            return None
        
        if version:
            return self.schemas[schema_id].get(version)
        else:
            # Return latest version
            versions = list(self.schemas[schema_id].keys())
            if not versions:
                return None
            
            latest_version = max(versions, key=lambda v: SchemaVersion(v).version)
            return self.schemas[schema_id][latest_version]
    
    def get_compatible_schemas(self, schema_id: str, version: str) -> List[Tuple[str, str, CompatibilityLevel]]:
        """
        Get list of schemas compatible with given schema
        
        Args:
            schema_id: Target schema ID
            version: Target schema version
            
        Returns:
            List of (schema_id, version, compatibility_level) tuples
        """
        compatible = []
        target_key = f"{schema_id}:{version}"
        
        for (key1, key2), result in self.compatibility_matrix.items():
            if key1 == target_key and result.level != CompatibilityLevel.INCOMPATIBLE:
                other_schema, other_version = key2.split(':')
                compatible.append((other_schema, other_version, result.level))
            elif key2 == target_key and result.level != CompatibilityLevel.INCOMPATIBLE:
                other_schema, other_version = key1.split(':')
                compatible.append((other_schema, other_version, result.level))
        
        return compatible
    
    def validate_schema_ecosystem(self) -> Dict[str, Any]:
        """
        Validate the entire schema ecosystem for consistency
        
        Returns:
            Validation report
        """
        report = {
            "total_schemas": len(self.schemas),
            "total_versions": sum(len(versions) for versions in self.schemas.values()),
            "compatibility_checks": len(self.compatibility_matrix),
            "issues": [],
            "recommendations": []
        }
        
        # Check for missing dependencies
        for schema_id, versions in self.schemas.items():
            for version, metadata in versions.items():
                for dep in metadata.dependencies:
                    if dep not in self.schemas:
                        report["issues"].append(f"Missing dependency: {schema_id}:{version} depends on {dep}")
        
        # Check for conflicting schemas in ecosystem
        incompatible_pairs = []
        for (key1, key2), result in self.compatibility_matrix.items():
            if result.level == CompatibilityLevel.INCOMPATIBLE:
                incompatible_pairs.append((key1, key2))
        
        if incompatible_pairs:
            report["issues"].extend([f"Incompatible schemas: {pair[0]} <-> {pair[1]}" for pair in incompatible_pairs])
        
        # Generate recommendations
        if not report["issues"]:
            report["recommendations"].append("Schema ecosystem is consistent and well-integrated")
        else:
            report["recommendations"].append("Address compatibility issues before deploying multi-theory workflows")
        
        return report
    
    def list_schemas(self) -> Dict[str, List[str]]:
        """List all registered schemas and their versions"""
        return {schema_id: list(versions.keys()) for schema_id, versions in self.schemas.items()}
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_versions = sum(len(versions) for versions in self.schemas.values())
        compatible_pairs = sum(1 for result in self.compatibility_matrix.values() 
                             if result.level != CompatibilityLevel.INCOMPATIBLE)
        
        return {
            "total_schemas": len(self.schemas),
            "total_versions": total_versions,
            "compatibility_checks": len(self.compatibility_matrix),
            "compatible_pairs": compatible_pairs,
            "last_updated": datetime.now().isoformat()
        }