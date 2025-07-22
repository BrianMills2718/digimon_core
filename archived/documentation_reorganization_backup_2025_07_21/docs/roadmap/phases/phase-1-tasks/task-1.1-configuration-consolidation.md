# Task 1.1: Configuration Consolidation

**Duration**: Days 1-2 (Week 2)  
**Owner**: Backend Lead  
**Priority**: CRITICAL - Blocks all other optimization work

## Objective

Consolidate three separate configuration management systems into a single, unified ConfigManager that maintains backward compatibility while simplifying configuration access throughout the codebase.

## Current State Analysis

### Existing Configuration Systems

1. **src/core/config.py** - `ConfigurationManager`
   - Uses environment variables
   - Basic validation
   - ~23 files depend on this

2. **src/core/unified_config.py** - `ConfigManager`  
   - Attempted unification
   - YAML file support
   - ~15 files depend on this

3. **src/core/config_manager.py** - Newer attempt
   - Partial implementation
   - Better validation
   - ~9 files depend on this

### Configuration Usage Analysis

```bash
# Script to analyze configuration usage
#!/bin/bash

echo "=== Configuration Usage Analysis ==="
echo "Files using ConfigurationManager:"
grep -r "from src.core.config import ConfigurationManager" --include="*.py" | wc -l

echo "Files using unified ConfigManager:"
grep -r "from src.core.unified_config import ConfigManager" --include="*.py" | wc -l

echo "Files using new config_manager:"
grep -r "from src.core.config_manager import" --include="*.py" | wc -l

echo -e "\nDetailed usage patterns:"
grep -r "config\." --include="*.py" | grep -v "__pycache__" | sort | uniq -c | sort -nr | head -20
```

## Implementation Plan

### Day 1 Morning: Design Unified Interface

#### Step 1: Configuration Requirements Analysis
```python
# Consolidated configuration requirements

class ConfigurationRequirements:
    """Document all configuration needs across the system"""
    
    # Service Configurations
    SERVICES = {
        'neo4j': {
            'uri': str,           # Required
            'user': str,          # Required
            'password': str,      # Required
            'database': str,      # Optional, default: 'neo4j'
            'max_retry': int,     # Optional, default: 3
            'timeout': int        # Optional, default: 30
        },
        'qdrant': {
            'host': str,          # Required
            'port': int,          # Required
            'api_key': str,       # Optional
            'collection': str,    # Optional, default: 'kgas_vectors'
            'timeout': int        # Optional, default: 30
        },
        'openai': {
            'api_key': str,       # Required
            'organization': str,  # Optional
            'model': str,         # Optional, default: 'gpt-4'
            'max_tokens': int,    # Optional, default: 2000
            'temperature': float  # Optional, default: 0.7
        }
    }
    
    # Application Settings
    APP_SETTINGS = {
        'debug': bool,            # Optional, default: False
        'log_level': str,         # Optional, default: 'INFO'
        'data_dir': str,          # Required
        'cache_dir': str,         # Optional
        'max_file_size': int,     # Optional, default: 100MB
        'batch_size': int         # Optional, default: 32
    }
    
    # Feature Flags
    FEATURES = {
        'enable_caching': bool,
        'enable_monitoring': bool,
        'enable_async': bool,
        'enable_provenance': bool
    }
```

#### Step 2: Design Unified ConfigManager
```python
# File: src/core/unified_config_manager.py

import os
import json
import yaml
from typing import Any, Dict, Optional, Union, TypeVar, Type
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
import logging

T = TypeVar('T')

@dataclass
class ConfigValue:
    """Wrapper for configuration values with metadata"""
    value: Any
    source: str  # 'env', 'file', 'default'
    validated: bool = False

class UnifiedConfigManager:
    """
    Unified configuration manager supporting multiple sources:
    - Environment variables (highest priority)
    - Configuration files (YAML/JSON)
    - Default values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self._config_cache: Dict[str, ConfigValue] = {}
        self._config_file = config_file or os.getenv('KGAS_CONFIG_FILE')
        self._load_configuration()
        
    def _load_configuration(self):
        """Load configuration from all sources"""
        # 1. Load defaults
        self._load_defaults()
        
        # 2. Load from file if exists
        if self._config_file and Path(self._config_file).exists():
            self._load_from_file(self._config_file)
            
        # 3. Override with environment variables
        self._load_from_environment()
        
        # 4. Validate all loaded configuration
        self._validate_configuration()
    
    def get(self, key: str, default: Any = None, type_hint: Type[T] = None) -> T:
        """
        Get configuration value with type conversion and validation.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            type_hint: Expected type for validation
            
        Returns:
            Configuration value of specified type
        """
        # Check cache first
        if key in self._config_cache:
            value = self._config_cache[key].value
            if type_hint:
                return self._convert_type(value, type_hint)
            return value
            
        # Handle nested keys
        if '.' in key:
            return self._get_nested(key, default, type_hint)
            
        # Return default
        if default is not None:
            self._config_cache[key] = ConfigValue(default, 'default')
            return default
            
        raise KeyError(f"Configuration key '{key}' not found")
    
    def _convert_type(self, value: Any, target_type: Type[T]) -> T:
        """Convert value to target type"""
        if isinstance(value, target_type):
            return value
            
        # Special handling for common conversions
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
            
        if target_type == int:
            return int(value)
            
        if target_type == float:
            return float(value)
            
        if target_type == str:
            return str(value)
            
        # For complex types, attempt direct conversion
        return target_type(value)
    
    def set(self, key: str, value: Any, persist: bool = False):
        """Set configuration value"""
        self._config_cache[key] = ConfigValue(value, 'runtime')
        
        if persist and self._config_file:
            self._persist_to_file(key, value)
    
    def _get_nested(self, key: str, default: Any, type_hint: Type[T]) -> T:
        """Handle nested configuration keys"""
        parts = key.split('.')
        current = self._config_cache
        
        for part in parts[:-1]:
            if part not in current:
                return default
            current = current[part].value
            if not isinstance(current, dict):
                return default
                
        final_key = parts[-1]
        if final_key in current:
            value = current[final_key]
            if type_hint:
                return self._convert_type(value, type_hint)
            return value
            
        return default
    
    # Backward compatibility methods
    @property
    def neo4j_uri(self) -> str:
        """Backward compatibility for neo4j_uri"""
        return self.get('neo4j.uri', 'bolt://localhost:7687')
    
    @property
    def openai_api_key(self) -> str:
        """Backward compatibility for openai_api_key"""
        return self.get('openai.api_key', '')
    
    def get_service_config(self, service: str) -> Dict[str, Any]:
        """Get all configuration for a service"""
        return self.get(service, {})
```

### Day 1 Afternoon: Implementation

#### Step 3: Create Migration Utilities
```python
# File: src/core/config_migration.py

class ConfigMigration:
    """Utilities for migrating from old config systems"""
    
    @staticmethod
    def migrate_from_configuration_manager(old_config):
        """Migrate from ConfigurationManager to UnifiedConfigManager"""
        mapping = {
            # Old attribute -> New key
            'neo4j_uri': 'neo4j.uri',
            'neo4j_user': 'neo4j.user',
            'neo4j_password': 'neo4j.password',
            'openai_api_key': 'openai.api_key',
            'openai_model': 'openai.model',
            'qdrant_host': 'qdrant.host',
            'qdrant_port': 'qdrant.port',
            'log_level': 'app.log_level',
            'data_directory': 'app.data_dir'
        }
        
        new_config = UnifiedConfigManager()
        
        for old_attr, new_key in mapping.items():
            if hasattr(old_config, old_attr):
                value = getattr(old_config, old_attr)
                new_config.set(new_key, value)
                
        return new_config
    
    @staticmethod
    def create_compatibility_wrapper(unified_config):
        """Create wrapper that mimics old ConfigurationManager interface"""
        
        class CompatibilityWrapper:
            def __init__(self, config: UnifiedConfigManager):
                self._config = config
            
            def __getattr__(self, name):
                # Map old attribute access to new config
                mapping = ConfigMigration.get_attribute_mapping()
                if name in mapping:
                    return self._config.get(mapping[name])
                raise AttributeError(f"'{name}' not found in configuration")
        
        return CompatibilityWrapper(unified_config)
```

#### Step 4: Update Service Initialization
```python
# File: src/core/service_initialization_update.py

# Before (multiple places in codebase):
from src.core.config import ConfigurationManager
config = ConfigurationManager()
neo4j_uri = config.neo4j_uri

# After (unified approach):
from src.core.unified_config_manager import UnifiedConfigManager
config = UnifiedConfigManager()
neo4j_uri = config.get('neo4j.uri', type_hint=str)

# Or using service config:
neo4j_config = config.get_service_config('neo4j')
```

### Day 2 Morning: Migration Implementation

#### Step 5: Systematic File Updates
```python
# Migration script: scripts/migrate_config_usage.py

import os
import re
from pathlib import Path

class ConfigUsageMigrator:
    """Automatically migrate configuration usage patterns"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.changes_made = []
        
    def migrate_imports(self):
        """Update all import statements"""
        patterns = [
            (
                r'from src\.core\.config import ConfigurationManager',
                'from src.core.unified_config_manager import UnifiedConfigManager'
            ),
            (
                r'from src\.core\.unified_config import ConfigManager',
                'from src.core.unified_config_manager import UnifiedConfigManager'
            ),
            (
                r'ConfigurationManager\(\)',
                'UnifiedConfigManager()'
            )
        ]
        
        for py_file in self.project_root.glob('**/*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            self._update_file(py_file, patterns)
    
    def migrate_attribute_access(self):
        """Update attribute access patterns"""
        # Map of old attribute access to new method calls
        attribute_map = {
            'config.neo4j_uri': "config.get('neo4j.uri')",
            'config.neo4j_user': "config.get('neo4j.user')",
            'config.neo4j_password': "config.get('neo4j.password')",
            'config.openai_api_key': "config.get('openai.api_key')",
            'config.qdrant_host': "config.get('qdrant.host')",
            'config.qdrant_port': "config.get('qdrant.port', type_hint=int)"
        }
        
        patterns = [(re.escape(old), new) for old, new in attribute_map.items()]
        
        for py_file in self.project_root.glob('**/*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            self._update_file(py_file, patterns)
    
    def _update_file(self, file_path: Path, patterns: list):
        """Update a single file with pattern replacements"""
        try:
            content = file_path.read_text()
            original_content = content
            
            for old_pattern, new_pattern in patterns:
                content = re.sub(old_pattern, new_pattern, content)
            
            if content != original_content:
                file_path.write_text(content)
                self.changes_made.append(str(file_path))
                print(f"Updated: {file_path}")
                
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
    
    def generate_report(self):
        """Generate migration report"""
        print(f"\nMigration Complete!")
        print(f"Files updated: {len(self.changes_made)}")
        
        with open('config_migration_report.txt', 'w') as f:
            f.write("Configuration Migration Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total files updated: {len(self.changes_made)}\n\n")
            f.write("Files changed:\n")
            for file in sorted(self.changes_made):
                f.write(f"  - {file}\n")

# Run migration
if __name__ == "__main__":
    migrator = ConfigUsageMigrator("/home/brian/Digimons")
    migrator.migrate_imports()
    migrator.migrate_attribute_access()
    migrator.generate_report()
```

### Day 2 Afternoon: Testing and Validation

#### Step 6: Comprehensive Testing
```python
# File: tests/core/test_unified_config_manager.py

import pytest
import tempfile
import os
from src.core.unified_config_manager import UnifiedConfigManager

class TestUnifiedConfigManager:
    
    def test_environment_override(self):
        """Test environment variables override file config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            f.write("""
            neo4j:
              uri: bolt://file-config:7687
              user: file_user
            """)
            f.flush()
            
            # Set environment variable
            os.environ['NEO4J_URI'] = 'bolt://env-config:7687'
            
            config = UnifiedConfigManager(f.name)
            
            # Environment should override file
            assert config.get('neo4j.uri') == 'bolt://env-config:7687'
            # File value should be used for non-overridden
            assert config.get('neo4j.user') == 'file_user'
    
    def test_type_conversion(self):
        """Test automatic type conversion"""
        config = UnifiedConfigManager()
        
        # Set string values
        config.set('test.port', '8080')
        config.set('test.enabled', 'true')
        config.set('test.ratio', '0.95')
        
        # Get with type hints
        assert config.get('test.port', type_hint=int) == 8080
        assert config.get('test.enabled', type_hint=bool) is True
        assert config.get('test.ratio', type_hint=float) == 0.95
    
    def test_backward_compatibility(self):
        """Test backward compatibility with old config systems"""
        config = UnifiedConfigManager()
        config.set('neo4j.uri', 'bolt://test:7687')
        
        # Test property access (backward compatibility)
        assert config.neo4j_uri == 'bolt://test:7687'
    
    def test_service_config(self):
        """Test service configuration retrieval"""
        config = UnifiedConfigManager()
        config.set('openai.api_key', 'test-key')
        config.set('openai.model', 'gpt-4')
        config.set('openai.temperature', 0.7)
        
        service_config = config.get_service_config('openai')
        assert service_config['api_key'] == 'test-key'
        assert service_config['model'] == 'gpt-4'
        assert service_config['temperature'] == 0.7
```

#### Step 7: Validation Script
```python
# File: scripts/validate_config_migration.py

class ConfigMigrationValidator:
    """Validate that configuration migration was successful"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_all_services_start(self):
        """Ensure all services can start with new config"""
        services = [
            'src.core.neo4j_manager',
            'src.core.qdrant_manager',
            'src.core.service_manager',
            'src.api.app'
        ]
        
        for service_module in services:
            try:
                module = __import__(service_module, fromlist=[''])
                print(f"✓ {service_module} imports successfully")
            except Exception as e:
                self.errors.append(f"Failed to import {service_module}: {e}")
    
    def validate_config_access_patterns(self):
        """Check for any remaining old config patterns"""
        old_patterns = [
            'ConfigurationManager',
            'from src.core.config import',
            'from src.core.unified_config import',
            'config.neo4j_uri',  # Should use get() method
        ]
        
        import subprocess
        for pattern in old_patterns:
            result = subprocess.run(
                ['grep', '-r', pattern, 'src/', '--include=*.py'],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                self.warnings.append(f"Found old pattern '{pattern}' in files:\n{result.stdout}")
    
    def generate_validation_report(self):
        """Generate validation report"""
        print("\n" + "="*50)
        print("CONFIGURATION MIGRATION VALIDATION REPORT")
        print("="*50 + "\n")
        
        if not self.errors and not self.warnings:
            print("✅ All validation checks passed!")
        else:
            if self.errors:
                print(f"❌ Found {len(self.errors)} errors:")
                for error in self.errors:
                    print(f"  - {error}")
            
            if self.warnings:
                print(f"⚠️  Found {len(self.warnings)} warnings:")
                for warning in self.warnings:
                    print(f"  - {warning}")
        
        return len(self.errors) == 0

# Run validation
if __name__ == "__main__":
    validator = ConfigMigrationValidator()
    validator.validate_all_services_start()
    validator.validate_config_access_patterns()
    success = validator.generate_validation_report()
    
    exit(0 if success else 1)
```

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**
   ```bash
   git checkout main -- src/core/
   git checkout main -- src/
   ```

2. **Partial Rollback**
   - Keep UnifiedConfigManager but add compatibility layer
   - Gradually migrate services one by one

3. **Emergency Wrapper**
   ```python
   # Temporary wrapper to prevent breakage
   from src.core.unified_config_manager import UnifiedConfigManager
   
   class ConfigurationManager:
       def __init__(self):
           self._unified = UnifiedConfigManager()
           
       def __getattr__(self, name):
           # Delegate to unified config
           return getattr(self._unified, name)
   ```

## Success Criteria

- [ ] All 47 config access points migrated
- [ ] Zero runtime errors after migration
- [ ] All tests pass with new config system
- [ ] Performance not degraded
- [ ] Backward compatibility maintained
- [ ] Developer documentation updated

## Deliverables

1. **UnifiedConfigManager** implementation
2. **Migration script** and report
3. **Updated service files** (~47 files)
4. **Test suite** for new config system
5. **Rollback procedures** documented