# Task 1.3: Tool Adapter Simplification

**Duration**: Days 4-5 (Week 2)  
**Owner**: Backend Lead  
**Priority**: HIGH - Reduces maintenance overhead

## Objective

Simplify the tool architecture by reducing adapter layers from 13 to 9 or fewer, making tools implement the KGASTool interface directly and removing unnecessary abstraction layers.

## Current State Analysis

### Adapter Inventory

```bash
# Script to analyze current adapter usage
#!/bin/bash

echo "=== Tool Adapter Analysis ==="
echo "Current adapter files:"
find src/core -name "*adapter*" -type f | grep -v __pycache__ | sort

echo -e "\nAdapter usage patterns:"
grep -r "ToolAdapter\|BaseAdapter\|adapter" src/tools/ --include="*.py" | \
    grep -v __pycache__ | \
    cut -d: -f1 | sort | uniq -c | sort -nr

echo -e "\nDirect KGASTool implementations:"
grep -r "class.*KGASTool" src/tools/ --include="*.py" | \
    grep -v __pycache__ | wc -l

echo -e "\nAdapter-wrapped tools:"
grep -r "adapter\." src/tools/ --include="*.py" | \
    grep -v __pycache__ | wc -l
```

### Identified Redundancies

1. **Phase Adapters** (3 files)
   - `phase1_adapter.py`
   - `phase2_adapter.py`
   - `phase3_adapter.py`
   - Can be consolidated into single adapter

2. **Type-Specific Adapters** (5 files)
   - `text_tool_adapter.py`
   - `graph_tool_adapter.py`
   - `vector_tool_adapter.py`
   - `llm_tool_adapter.py`
   - `export_tool_adapter.py`
   - Most provide minimal value

3. **Legacy Adapters** (3 files)
   - `mcp_tool_adapter.py`
   - `async_tool_adapter.py`
   - `validation_adapter.py`
   - Can be merged or removed

4. **Core Adapters to Keep** (2 files)
   - `tool_adapter.py` - Base functionality
   - `unified_tool_adapter.py` - Common patterns

## Implementation Plan

### Day 4 Morning: Design Simplified Architecture

#### Step 1: Define Direct KGASTool Interface
```python
# File: src/core/kgas_tool_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ToolMetadata:
    """Tool metadata for registry and discovery"""
    tool_id: str
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class KGASTool(ABC):
    """
    Simplified base interface for all KGAS tools.
    Tools should implement this directly without adapters.
    """
    
    def __init__(self):
        """Initialize tool with metadata"""
        self.metadata = self.get_metadata()
        self._initialized = False
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata for registration"""
        pass
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize tool with configuration.
        Called once before first execute.
        """
        pass
    
    @abstractmethod
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute tool with input data and context.
        
        Returns:
            Dict with keys:
            - status: 'success' or 'error'
            - results: Tool-specific results
            - metadata: Execution metadata
        """
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Optional: Validate input before execution.
        Override for custom validation.
        """
        return input_data is not None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Optional: Return tool capabilities for discovery.
        Override to advertise specific features.
        """
        return {
            'async': False,
            'batch': False,
            'streaming': False,
            'requires_auth': False
        }
    
    def ensure_initialized(self, config: Optional[Dict[str, Any]] = None):
        """Ensure tool is initialized before use"""
        if not self._initialized:
            self.initialize(config)
            self._initialized = True
    
    def create_result(self, 
                     status: str = 'success',
                     results: Any = None,
                     error: Optional[str] = None,
                     execution_time: Optional[float] = None) -> Dict[str, Any]:
        """Helper to create standardized results"""
        return {
            'tool_id': self.metadata.tool_id,
            'status': status,
            'results': results,
            'error': error,
            'metadata': {
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'version': self.metadata.version
            }
        }
```

#### Step 2: Create Migration Helper
```python
# File: src/core/tool_migration_helper.py

from typing import Type, Dict, Any
import inspect
from src.core.kgas_tool_interface import KGASTool, ToolMetadata

class ToolMigrationHelper:
    """Helper to migrate adapter-based tools to direct implementation"""
    
    @staticmethod
    def analyze_tool(tool_class: Type) -> Dict[str, Any]:
        """Analyze a tool class for migration requirements"""
        analysis = {
            'class_name': tool_class.__name__,
            'uses_adapter': False,
            'has_execute': False,
            'has_metadata': False,
            'parent_classes': [],
            'migration_complexity': 'low'
        }
        
        # Check parent classes
        for parent in inspect.getmro(tool_class)[1:]:
            if 'Adapter' in parent.__name__:
                analysis['uses_adapter'] = True
                analysis['migration_complexity'] = 'medium'
            analysis['parent_classes'].append(parent.__name__)
        
        # Check methods
        methods = inspect.getmembers(tool_class, predicate=inspect.ismethod)
        for name, _ in methods:
            if name == 'execute':
                analysis['has_execute'] = True
            if name == 'get_metadata':
                analysis['has_metadata'] = True
        
        # Determine complexity
        if analysis['uses_adapter'] and not analysis['has_execute']:
            analysis['migration_complexity'] = 'high'
        
        return analysis
    
    @staticmethod
    def generate_migration_code(tool_class: Type, analysis: Dict[str, Any]) -> str:
        """Generate migration code for a tool"""
        
        template = '''
# Migration for {class_name}
from src.core.kgas_tool_interface import KGASTool, ToolMetadata
from typing import Dict, Any, Optional

class {class_name}(KGASTool):
    """Migrated {class_name} - now implements KGASTool directly"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            tool_id="{tool_id}",
            name="{tool_name}",
            description="{description}",
            category="{category}",
            tags={tags}
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize tool with configuration"""
        self.config = config or {{}}
        # TODO: Add initialization logic from original tool
        
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute tool logic"""
        try:
            # Validate input
            if not self.validate_input(input_data):
                return self.create_result(
                    status='error',
                    error='Invalid input data'
                )
            
            # TODO: Migrate execute logic from original tool
            results = {{}}
            
            return self.create_result(
                status='success',
                results=results
            )
            
        except Exception as e:
            return self.create_result(
                status='error',
                error=str(e)
            )
'''
        
        # Fill in template
        return template.format(
            class_name=tool_class.__name__,
            tool_id=tool_class.__name__.lower().replace('tool', ''),
            tool_name=tool_class.__name__.replace('Tool', ' Tool'),
            description=f"Migrated {tool_class.__name__}",
            category='general',
            tags=['migrated']
        )
```

### Day 4 Afternoon: Migrate Core Tools

#### Step 3: Migrate Phase 1 Tools
```python
# Example migration for T01 PDF Loader

# BEFORE (with adapter):
from src.core.phase1_adapter import Phase1Adapter

class T01PDFLoader:
    def __init__(self):
        self.adapter = Phase1Adapter(self)
        
    def process_pdf(self, file_path):
        # Logic here
        pass

# AFTER (direct implementation):
from src.core.kgas_tool_interface import KGASTool, ToolMetadata
import PyPDF2
from typing import Dict, Any, Optional

class T01PDFLoader(KGASTool):
    """PDF document loader implementing KGASTool directly"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            tool_id="T01",
            name="PDF Loader",
            description="Load and extract text from PDF documents",
            category="document_processing",
            tags=["pdf", "loader", "phase1"]
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize PDF loader"""
        self.config = config or {}
        self.max_pages = self.config.get('max_pages', 1000)
        self.extract_images = self.config.get('extract_images', False)
    
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load PDF and extract text"""
        try:
            # Ensure initialized
            self.ensure_initialized()
            
            # Validate input
            if not isinstance(input_data, dict) or 'file_path' not in input_data:
                return self.create_result(
                    status='error',
                    error='Input must contain file_path'
                )
            
            file_path = input_data['file_path']
            
            # Extract text
            text = self._extract_text(file_path)
            metadata = self._extract_metadata(file_path)
            
            return self.create_result(
                status='success',
                results={
                    'text': text,
                    'metadata': metadata,
                    'page_count': len(text.split('\n\n'))
                }
            )
            
        except Exception as e:
            return self.create_result(
                status='error',
                error=f'PDF processing failed: {str(e)}'
            )
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        text_parts = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(min(len(pdf_reader.pages), self.max_pages)):
                page = pdf_reader.pages[page_num]
                text_parts.append(page.extract_text())
        
        return '\n\n'.join(text_parts)
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                }
            
            return metadata
```

#### Step 4: Update Tool Factory
```python
# File: src/core/simplified_tool_factory.py

from typing import Dict, Type, Optional, List
from src.core.kgas_tool_interface import KGASTool
import importlib
import inspect
from pathlib import Path

class SimplifiedToolFactory:
    """Simplified tool factory without adapters"""
    
    def __init__(self):
        self._tool_registry: Dict[str, Type[KGASTool]] = {}
        self._tool_instances: Dict[str, KGASTool] = {}
        self._scan_for_tools()
    
    def _scan_for_tools(self):
        """Scan tool directories for KGASTool implementations"""
        tool_dirs = [
            'src/tools/phase1',
            'src/tools/phase2',
            'src/tools/phase3',
            'src/tools/cross_modal'
        ]
        
        for tool_dir in tool_dirs:
            tool_path = Path(tool_dir)
            if not tool_path.exists():
                continue
                
            for py_file in tool_path.glob('*.py'):
                if py_file.name.startswith('_'):
                    continue
                    
                module_name = f"{tool_dir.replace('/', '.')}.{py_file.stem}"
                
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find KGASTool subclasses
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, KGASTool) and 
                            obj != KGASTool):
                            
                            # Register tool
                            tool_instance = obj()
                            tool_id = tool_instance.metadata.tool_id
                            self._tool_registry[tool_id] = obj
                            
                except Exception as e:
                    print(f"Failed to load module {module_name}: {e}")
    
    def get_tool(self, tool_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[KGASTool]:
        """Get tool instance by ID"""
        
        # Return cached instance if available
        if tool_id in self._tool_instances:
            return self._tool_instances[tool_id]
        
        # Create new instance
        if tool_id in self._tool_registry:
            tool_class = self._tool_registry[tool_id]
            tool_instance = tool_class()
            tool_instance.initialize(config)
            
            # Cache instance
            self._tool_instances[tool_id] = tool_instance
            
            return tool_instance
        
        return None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        tools = []
        
        for tool_id, tool_class in self._tool_registry.items():
            tool_instance = tool_class()
            metadata = tool_instance.metadata
            
            tools.append({
                'tool_id': metadata.tool_id,
                'name': metadata.name,
                'description': metadata.description,
                'category': metadata.category,
                'tags': metadata.tags,
                'capabilities': tool_instance.get_capabilities()
            })
        
        return tools
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tool IDs by category"""
        tool_ids = []
        
        for tool_id, tool_class in self._tool_registry.items():
            tool_instance = tool_class()
            if tool_instance.metadata.category == category:
                tool_ids.append(tool_id)
        
        return tool_ids
    
    def validate_all_tools(self) -> Dict[str, bool]:
        """Validate all registered tools"""
        results = {}
        
        for tool_id in self._tool_registry:
            try:
                tool = self.get_tool(tool_id)
                # Test with minimal input
                result = tool.execute(
                    input_data={'test': True},
                    context={'validation_mode': True}
                )
                results[tool_id] = result.get('status') == 'success'
            except Exception as e:
                results[tool_id] = False
                print(f"Validation failed for {tool_id}: {e}")
        
        return results
```

### Day 5 Morning: Complete Migration

#### Step 5: Batch Migration Script
```python
# File: scripts/migrate_tools_to_direct.py

#!/usr/bin/env python3
"""
Migrate all tools from adapter-based to direct KGASTool implementation
"""

import os
import ast
import shutil
from pathlib import Path
from typing import List, Dict, Any

class ToolMigrator:
    """Automated tool migration"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.migration_report = []
        
    def migrate_all_tools(self):
        """Migrate all tools to direct implementation"""
        
        tool_files = self.find_tool_files()
        
        for tool_file in tool_files:
            print(f"\nProcessing: {tool_file}")
            
            # Analyze file
            analysis = self.analyze_tool_file(tool_file)
            
            if analysis['needs_migration']:
                if self.dry_run:
                    print(f"  Would migrate: {analysis['reason']}")
                else:
                    self.migrate_tool_file(tool_file, analysis)
            else:
                print(f"  No migration needed")
            
            self.migration_report.append(analysis)
        
        self.generate_report()
    
    def analyze_tool_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a tool file for migration needs"""
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        analysis = {
            'file': str(file_path),
            'needs_migration': False,
            'reason': '',
            'has_adapter_import': False,
            'has_kgas_import': False,
            'classes': []
        }
        
        # Parse AST
        try:
            tree = ast.parse(content)
            
            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if 'adapter' in str(node.module).lower():
                        analysis['has_adapter_import'] = True
                        analysis['needs_migration'] = True
                        analysis['reason'] = 'Uses adapter imports'
                    
                    if 'kgas_tool_interface' in str(node.module):
                        analysis['has_kgas_import'] = True
                
                # Check class definitions
                if isinstance(node, ast.ClassDef):
                    base_names = [base.id for base in node.bases if hasattr(base, 'id')]
                    
                    if 'KGASTool' in base_names:
                        analysis['has_kgas_import'] = True
                    
                    analysis['classes'].append({
                        'name': node.name,
                        'bases': base_names
                    })
        
        except SyntaxError as e:
            analysis['error'] = str(e)
        
        # Determine migration need
        if analysis['has_adapter_import'] and not analysis['has_kgas_import']:
            analysis['needs_migration'] = True
        
        return analysis
    
    def migrate_tool_file(self, file_path: Path, analysis: Dict[str, Any]):
        """Migrate a tool file"""
        
        # Backup original
        backup_path = file_path.with_suffix('.py.backup')
        shutil.copy(file_path, backup_path)
        
        # Read content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Apply migrations
        migrated_content = self.apply_migrations(content, analysis)
        
        # Write migrated content
        with open(file_path, 'w') as f:
            f.write(migrated_content)
        
        print(f"  Migrated successfully (backup: {backup_path})")
    
    def apply_migrations(self, content: str, analysis: Dict[str, Any]) -> str:
        """Apply migration transformations"""
        
        # Replace adapter imports
        replacements = [
            # Remove adapter imports
            (r'from src\.core\.\w*adapter import \w+Adapter\n', ''),
            (r'from src\.core\.phase\d_adapter import \w+\n', ''),
            
            # Add KGASTool import
            ('from typing import', 
             'from src.core.kgas_tool_interface import KGASTool, ToolMetadata\nfrom typing import'),
            
            # Update class definitions
            (r'class (\w+)(?:\(\))?:', r'class \1(KGASTool):'),
            
            # Remove adapter initialization
            (r'self\.adapter = \w+Adapter\(.*\)\n', ''),
        ]
        
        import re
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Add required methods if missing
        if 'def get_metadata' not in content:
            content = self.add_metadata_method(content, analysis)
        
        if 'def initialize' not in content:
            content = self.add_initialize_method(content, analysis)
        
        return content
    
    def generate_report(self):
        """Generate migration report"""
        
        report_path = Path('migration_report.md')
        
        with open(report_path, 'w') as f:
            f.write("# Tool Migration Report\n\n")
            f.write(f"Total files analyzed: {len(self.migration_report)}\n")
            
            migrated = [r for r in self.migration_report if r.get('needs_migration')]
            f.write(f"Files needing migration: {len(migrated)}\n\n")
            
            f.write("## Migration Details\n\n")
            
            for report in self.migration_report:
                f.write(f"### {report['file']}\n")
                f.write(f"- Needs migration: {report['needs_migration']}\n")
                if report['needs_migration']:
                    f.write(f"- Reason: {report['reason']}\n")
                f.write(f"- Classes: {[c['name'] for c in report['classes']]}\n\n")
        
        print(f"\nMigration report saved to: {report_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate tools to direct KGASTool implementation')
    parser.add_argument('--dry-run', action='store_true', help='Analyze without making changes')
    parser.add_argument('--backup', action='store_true', help='Create backups before migration')
    
    args = parser.parse_args()
    
    migrator = ToolMigrator(dry_run=args.dry_run)
    migrator.migrate_all_tools()
```

### Day 5 Afternoon: Testing and Cleanup

#### Step 6: Validate Migrated Tools
```python
# File: tests/core/test_simplified_tools.py

import pytest
from src.core.simplified_tool_factory import SimplifiedToolFactory
from src.core.kgas_tool_interface import KGASTool

class TestSimplifiedTools:
    """Test migrated tools work correctly"""
    
    @pytest.fixture
    def factory(self):
        return SimplifiedToolFactory()
    
    def test_all_tools_implement_kgas_interface(self, factory):
        """Verify all tools implement KGASTool"""
        tools = factory.list_tools()
        
        for tool_info in tools:
            tool = factory.get_tool(tool_info['tool_id'])
            assert isinstance(tool, KGASTool)
            assert hasattr(tool, 'execute')
            assert hasattr(tool, 'get_metadata')
            assert hasattr(tool, 'initialize')
    
    def test_no_adapter_dependencies(self, factory):
        """Verify no tools depend on adapters"""
        import inspect
        
        tools = factory.list_tools()
        
        for tool_info in tools:
            tool = factory.get_tool(tool_info['tool_id'])
            
            # Check tool source for adapter imports
            source = inspect.getsource(tool.__class__)
            assert 'adapter' not in source.lower()
            assert 'Adapter' not in source
    
    def test_tool_execution_consistency(self, factory):
        """Verify tools execute consistently"""
        
        test_cases = [
            {
                'tool_id': 'T01',
                'input_data': {'file_path': 'test.pdf'},
                'expected_keys': ['text', 'metadata']
            },
            {
                'tool_id': 'T15a',
                'input_data': {'text': 'Test text'},
                'expected_keys': ['chunks']
            }
        ]
        
        for test_case in test_cases:
            tool = factory.get_tool(test_case['tool_id'])
            if not tool:
                continue
                
            result = tool.execute(
                test_case['input_data'],
                {'validation_mode': True}
            )
            
            assert result['status'] in ['success', 'error']
            assert 'metadata' in result
            assert 'tool_id' in result
    
    def test_performance_improvement(self, factory, benchmark):
        """Verify performance improved without adapters"""
        
        # Get a compute-intensive tool
        tool = factory.get_tool('T15b')  # Vector embedder
        
        test_data = {
            'chunks': [{'text': f'Test chunk {i}'} for i in range(100)]
        }
        
        # Benchmark execution
        result = benchmark(tool.execute, test_data, {})
        
        # Performance should be better than adapter version
        # (This would compare against baseline if available)
        assert result['status'] == 'success'
```

#### Step 7: Remove Obsolete Adapters
```python
# File: scripts/cleanup_adapters.py

#!/usr/bin/env python3
"""Remove obsolete adapter files after migration"""

import os
import shutil
from pathlib import Path

def cleanup_adapters(dry_run=True):
    """Remove obsolete adapter files"""
    
    adapters_to_remove = [
        'src/core/phase1_adapter.py',
        'src/core/phase2_adapter.py', 
        'src/core/phase3_adapter.py',
        'src/core/text_tool_adapter.py',
        'src/core/graph_tool_adapter.py',
        'src/core/vector_tool_adapter.py',
        'src/core/llm_tool_adapter.py',
        'src/core/export_tool_adapter.py',
        'src/core/mcp_tool_adapter.py',
        'src/core/async_tool_adapter.py',
        'src/core/validation_adapter.py'
    ]
    
    # Archive directory for removed files
    archive_dir = Path('archived_adapters')
    if not dry_run:
        archive_dir.mkdir(exist_ok=True)
    
    removed_count = 0
    
    for adapter_file in adapters_to_remove:
        file_path = Path(adapter_file)
        
        if file_path.exists():
            if dry_run:
                print(f"Would remove: {adapter_file}")
            else:
                # Archive before removing
                archive_path = archive_dir / file_path.name
                shutil.copy(file_path, archive_path)
                
                # Remove file
                file_path.unlink()
                print(f"Removed: {adapter_file} (archived to {archive_path})")
            
            removed_count += 1
    
    print(f"\nTotal adapters {'would be' if dry_run else ''} removed: {removed_count}")
    
    # Update imports in remaining files
    if not dry_run:
        update_remaining_imports()

def update_remaining_imports():
    """Update any remaining adapter imports"""
    
    # Files that might still reference adapters
    files_to_check = [
        'src/core/tool_factory.py',
        'src/core/service_manager.py',
        'src/api/endpoints.py'
    ]
    
    for file_path in files_to_check:
        if not Path(file_path).exists():
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remove adapter imports
        updated_content = content
        updated_content = updated_content.replace(
            'from src.core.tool_adapter import', 
            'from src.core.kgas_tool_interface import'
        )
        
        if updated_content != content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            print(f"Updated imports in: {file_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', 
                       help='Execute cleanup (default is dry run)')
    
    args = parser.parse_args()
    cleanup_adapters(dry_run=not args.execute)
```

## Validation Plan

### Functionality Tests
- [ ] All tools discoverable by factory
- [ ] All tools execute successfully
- [ ] No adapter imports remain
- [ ] Performance improved

### Integration Tests
- [ ] Tool factory works with new structure
- [ ] Service manager integrates properly
- [ ] API endpoints function correctly
- [ ] UI can access all tools

## Success Criteria

- [ ] Adapter count reduced from 13 to ≤9
- [ ] All MVRT tools migrated successfully
- [ ] Zero regression in functionality
- [ ] 10-20% performance improvement
- [ ] Cleaner, more maintainable code

## Deliverables

1. **Simplified KGASTool interface**
2. **Migrated tool implementations** (47 files)
3. **Updated tool factory**
4. **Migration scripts and reports**
5. **Archived adapter files**
6. **Updated documentation**