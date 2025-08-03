#!/usr/bin/env python3
"""Remove ALL sys.path manipulations from Python files"""

import os
import re
from pathlib import Path

def fix_sys_path_in_file(file_path):
    """Remove sys.path manipulations from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove sys.path.insert and sys.path.append lines
        content = re.sub(r'^.*sys\.path\.insert\([^)]+\).*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'^.*sys\.path\.append\([^)]+\).*\n?', '', content, flags=re.MULTILINE)
        
        # Remove standalone 'import sys' if no other sys usage
        lines = content.split('\n')
        sys_import_line = None
        sys_used_elsewhere = False
        
        for i, line in enumerate(lines):
            if line.strip() == 'import sys' or line.strip() == 'import sys ':
                sys_import_line = i
            elif 'sys.' in line and 'sys.path' not in line:
                sys_used_elsewhere = True
        
        if sys_import_line is not None and not sys_used_elsewhere:
            lines.pop(sys_import_line)
            content = '\n'.join(lines)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all Python files with sys.path manipulations"""
    fixed_count = 0
    
    # Process all Python files
    for py_file in Path('.').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                if 'sys.path' in f.read():
                    if fix_sys_path_in_file(py_file):
                        fixed_count += 1
        except Exception as e:
            print(f"Error checking {py_file}: {e}")
    
    print(f"\nFixed {fixed_count} files")
    
    # Verify no sys.path remains
    remaining_files = []
    for py_file in Path('.').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'sys.path.insert' in content or 'sys.path.append' in content:
                    remaining_files.append(str(py_file))
        except:
            continue
    
    if remaining_files:
        print(f"\nWARNING: {len(remaining_files)} files still have sys.path:")
        for f in remaining_files[:10]:  # Show first 10
            print(f"  {f}")
    else:
        print("\n✅ ALL sys.path manipulations eliminated")

if __name__ == "__main__":
    main()