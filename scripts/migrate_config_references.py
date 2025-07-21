"""
Migration script to consolidate configuration systems.

Migrates from src.core.unified_config and src.core.config to the new
consolidated src.core.config_manager system.
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json
from typing import List, Tuple


def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in the directory tree."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'archive', 'archived'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def analyze_file(file_path: Path) -> Tuple[bool, str, List[str]]:
    """Analyze a file for configuration imports and return updated content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return False, "", []
    
    original_content = content
    changes = []
    
    # Pattern 1: from src.core.unified_config import ...
    pattern1 = r'from\s+src\.core\.unified_config\s+import\s+([^\n]+)'
    def replace1(match):
        imports = match.group(1).strip()
        
        if 'UnifiedConfigManager as ConfigurationManager' in imports:
            changes.append("Updated UnifiedConfigManager import to ConfigurationManager")
            return 'from src.core.config_manager import ConfigurationManager'
        elif 'UnifiedConfigManager' in imports:
            changes.append("Updated UnifiedConfigManager import")
            return 'from src.core.config_manager import ConfigurationManager'
        elif 'get_config' in imports:
            changes.append("Updated get_config import")
            return 'from src.core.config_manager import get_config'
        else:
            changes.append(f"Updated unified_config import: {imports}")
            return f'from src.core.config_manager import {imports}'
    
    content = re.sub(pattern1, replace1, content)
    
    # Pattern 2: from src.core.config import ...
    pattern2 = r'from\s+src\.core\.config\s+import\s+([^\n]+)'
    def replace2(match):
        imports = match.group(1).strip()
        changes.append(f"Updated legacy config import: {imports}")
        return f'from src.core.config_manager import {imports}'
    
    content = re.sub(pattern2, replace2, content)
    
    # Pattern 3: from .config import ... (relative imports in core module)
    pattern3 = r'from\s+\.config\s+import\s+([^\n]+)'
    def replace3(match):
        imports = match.group(1).strip()
        changes.append(f"Updated relative config import: {imports}")
        return f'from .config_manager import {imports}'
    
    content = re.sub(pattern3, replace3, content)
    
    # Pattern 4: from core.config import ... (fallback imports)
    pattern4 = r'from\s+core\.config\s+import\s+([^\n]+)'
    def replace4(match):
        imports = match.group(1).strip()
        changes.append(f"Updated fallback config import: {imports}")
        return f'from src.core.config_manager import {imports}'
    
    content = re.sub(pattern4, replace4, content)
    
    # Pattern 5: Try/except import patterns
    try_except_pattern = r'try:\s*\n\s*from\s+src\.core\.config\s+import\s+([^\n]+)\s*\n\s*except\s+ImportError:\s*\n\s*from\s+core\.config\s+import\s+([^\n]+)'
    def replace_try_except(match):
        import1 = match.group(1).strip()
        changes.append(f"Simplified try/except import: {import1}")
        return f'from src.core.config_manager import {import1}'
    
    content = re.sub(try_except_pattern, replace_try_except, content, flags=re.MULTILINE)
    
    # Fix any remaining class name references
    content = re.sub(r'\bUnifiedConfigManager\b', 'ConfigurationManager', content)
    
    # Check if content changed
    has_changes = content != original_content
    
    return has_changes, content, changes


def migrate_config_references():
    """Migrate all configuration references to consolidated system."""
    print("Starting configuration consolidation migration...")
    
    # Find all Python files
    project_root = Path(__file__).parent.parent
    python_files = find_python_files(str(project_root))
    
    print(f"Found {len(python_files)} Python files to analyze")
    
    updated_files = []
    total_changes = 0
    
    for file_path in python_files:
        # Skip certain files
        if (file_path.name in ['migrate_config_references.py', 'unified_config.py', 'config.py'] or
            file_path.suffix not in ['.py']):
            continue
        
        has_changes, new_content, changes = analyze_file(file_path)
        
        if has_changes:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(str(file_path))
                total_changes += len(changes)
                
                print(f"Updated {file_path}")
                for change in changes:
                    print(f"  - {change}")
                
            except Exception as e:
                print(f"Error updating {file_path}: {e}")
    
    # Log migration results
    migration_result = {
        'migrated_files': updated_files,
        'migration_count': len(updated_files),
        'total_changes': total_changes,
        'migration_timestamp': datetime.now().isoformat()
    }
    
    print(f"\nMigration completed!")
    print(f"Updated {len(updated_files)} files with {total_changes} changes")
    
    return migration_result

if __name__ == '__main__':
    result = migrate_config_references()
    print(f"Migration completed. {result['migration_count']} files migrated.")
    print(f"Results logged to Evidence.md")